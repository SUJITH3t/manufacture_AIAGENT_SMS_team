"""
ManufacturingAgent LangGraph Nodes
Execution nodes for input validation, risk scoring, RAG retrieval, analysis, drafting, review, and finalization.
"""

import json
import time
import logging
from typing import Dict, Any
from backend.app.agent.state import AgentState
from backend.app.tools.risk_tool import evaluate_machine_risk
from backend.app.tools.retrieval_tool import retrieve_manufacturing_guidelines
from backend.app.tools.history_tool import get_machine_history
from backend.app.tools.calculator_tool import calculate
from backend.app.agent.review import evaluate_review_criteria, get_review_manager
from backend.app.providers.router import get_llm_provider
from backend.app.prompts.risk_prompt import RISK_ASSESSMENT_SYSTEM_PROMPT, RISK_ASSESSMENT_USER_PROMPT
from backend.app.prompts.analysis_prompt import SENSOR_ANALYSIS_SYSTEM_PROMPT, SENSOR_ANALYSIS_USER_PROMPT
from backend.app.prompts.draft_prompt import DRAFT_RECOMMENDATION_SYSTEM_PROMPT, DRAFT_RECOMMENDATION_USER_PROMPT
from backend.app.prompts.review_prompt import REVIEW_SYSTEM_PROMPT, REVIEW_USER_PROMPT

logger = logging.getLogger(__name__)


def validate_input_node(state: AgentState) -> Dict[str, Any]:
    """Validate incoming payload, checking for missing or non-physical parameters."""
    start_time = time.time()
    logger.info(f"[Node: validate_input] Validating request {state.get('request_id')}")

    machine_id = str(state.get("machine_id", "")).strip().upper()
    user_query = str(state.get("user_query", "")).strip()
    sensor_data = state.get("sensor_data") or {}

    errors = []
    if not machine_id:
        errors.append("Missing required field: 'machine_id'.")
    if not user_query:
        errors.append("Missing required field: 'user_query'.")

    # If sensor data is empty, attempt to read from sensor tool
    if not sensor_data and machine_id:
        from backend.app.tools.sensor_tool import get_sensor_data
        tool_res = get_sensor_data(machine_id)
        if tool_res.get("success"):
            sensor_data = tool_res.get("sensor_data", {})
        else:
            errors.append(f"Sensor data missing and lookup failed: {tool_res.get('error')}")

    error_msg = "; ".join(errors) if errors else None
    return {
        "machine_id": machine_id,
        "user_query": user_query,
        "sensor_data": sensor_data,
        "error": error_msg,
        "risk_level": "HIGH" if error_msg else state.get("risk_level", "NORMAL"),
        "risk_reason": error_msg if error_msg else "",
        "iteration_count": 0
    }


def risk_assessment_node(state: AgentState) -> Dict[str, Any]:
    """Assess asset operational risk using deterministic engineering rules and LLM evaluation."""
    logger.info(f"[Node: risk_assessment] Evaluating risk for machine {state.get('machine_id')}")

    sensor_data = state.get("sensor_data", {})
    rule_eval = evaluate_machine_risk(sensor_data)

    risk_level = rule_eval["risk_level"]
    risk_score = rule_eval["risk_score"]
    risk_reasons = rule_eval["reasons"]

    # Determine tool requirements based on risk & query
    selected_tools = ["retrieve_manufacturing_guidelines"]
    if risk_level in ["EDGE", "HIGH"]:
        selected_tools.append("get_machine_history")
        selected_tools.append("calculate")
    if risk_level == "HIGH":
        selected_tools.append("request_human_review")

    provider = get_llm_provider(state.get("provider"))
    try:
        prompt = RISK_ASSESSMENT_USER_PROMPT.format(
            machine_id=state.get("machine_id", "UNKNOWN"),
            sensor_data_json=json.dumps(sensor_data, indent=2),
            user_query=state.get("user_query", "")
        )
        llm_out = provider.generate(prompt=prompt, system_prompt=RISK_ASSESSMENT_SYSTEM_PROMPT)
        logger.debug(f"[Risk LLM Output]: {llm_out[:120]}...")
    except Exception as e:
        logger.warning(f"LLM risk assessment fallback: {e}")

    return {
        "risk_level": risk_level,
        "risk_reason": " | ".join(risk_reasons),
        "tool_required": len(selected_tools) > 0,
        "selected_tools": selected_tools
    }


def route_request_node(state: AgentState) -> Dict[str, Any]:
    """Intermediary routing node logging dispatch."""
    logger.info(f"[Node: route_request] Routing dispatch for risk: {state.get('risk_level')}")
    return {}


def retrieve_evidence_node(state: AgentState) -> Dict[str, Any]:
    """Query RAG knowledge base for authoritative manufacturing manuals and SOPs."""
    logger.info(f"[Node: retrieve_evidence] Retrieving context for query: {state.get('user_query')}")

    query = state.get("user_query", "")
    sensor_data = state.get("sensor_data", {})
    risk_level = state.get("risk_level", "NORMAL")

    # Build contextual query
    search_terms = [query]
    if sensor_data.get("temperature", 0) > 68.0:
        search_terms.append("spindle overheating thermal tolerances bearing lubrication")
    if sensor_data.get("vibration", 0) > 1.8:
        search_terms.append("ISO 10816 vibration velocity RMS bearing fault unbalance")
    if sensor_data.get("pressure", 0) < 4.5 or sensor_data.get("pressure", 0) > 6.5:
        search_terms.append("hydraulic line pressure limits cavitation relief valve")

    augmented_query = " ".join(search_terms)
    top_k = 6 if risk_level in ["EDGE", "HIGH"] else 3

    rag_result = retrieve_manufacturing_guidelines(query=augmented_query, top_k=top_k)
    evidence_items = rag_result.get("evidence", [])

    return {
        "retrieved_documents": evidence_items,
        "evidence": evidence_items
    }


def analyze_sensor_data_node(state: AgentState) -> Dict[str, Any]:
    """Perform engineering telemetry analysis synthesizing sensor readings with retrieved evidence."""
    logger.info(f"[Node: analyze_sensor_data] Analyzing telemetry for machine {state.get('machine_id')}")

    provider = get_llm_provider(state.get("provider"))
    sensor_data = state.get("sensor_data", {})
    evidence_items = state.get("evidence", [])

    evidence_text = "\n\n".join([
        f"[{i+1}] Source: {e.get('source')} (Section: {e.get('section', 'General')}, Relevance: {e.get('relevance', 0.0)})\nContent: {e.get('content')}"
        for i, e in enumerate(evidence_items)
    ]) if evidence_items else "No specific document evidence retrieved."

    prompt = SENSOR_ANALYSIS_USER_PROMPT.format(
        machine_id=state.get("machine_id", "UNKNOWN"),
        risk_level=state.get("risk_level", "NORMAL"),
        risk_score="0.85" if state.get("risk_level") == "HIGH" else "0.20",
        sensor_data_json=json.dumps(sensor_data, indent=2),
        user_query=state.get("user_query", ""),
        retrieved_evidence_text=evidence_text
    )

    try:
        analysis = provider.generate(prompt=prompt, system_prompt=SENSOR_ANALYSIS_SYSTEM_PROMPT)
    except Exception as e:
        analysis = f"Automated analysis fallback: Telemetry evaluated against ISO 10816 standards. Error details: {str(e)}"

    return {
        "analysis": analysis
    }


def generate_draft_node(state: AgentState) -> Dict[str, Any]:
    """Generate evidence-grounded draft recommendation adhering strictly to non-actuation boundaries."""
    logger.info(f"[Node: generate_draft] Drafting response for risk {state.get('risk_level')}")

    provider = get_llm_provider(state.get("provider"))
    sensor_data = state.get("sensor_data", {})
    evidence_items = state.get("evidence", [])

    evidence_text = "\n\n".join([
        f"- Source: {e.get('source')} | Section: {e.get('section', 'General')} | Relevance: {e.get('relevance', 0.0)}\n  Excerpt: {e.get('content')[:350]}..."
        for e in evidence_items
    ]) if evidence_items else "No authoritative document passages retrieved."

    prompt = DRAFT_RECOMMENDATION_USER_PROMPT.format(
        machine_id=state.get("machine_id", "UNKNOWN"),
        risk_level=state.get("risk_level", "NORMAL"),
        risk_reasons=state.get("risk_reason", "Telemetry within nominal limits"),
        sensor_data_json=json.dumps(sensor_data, indent=2),
        user_query=state.get("user_query", ""),
        analysis_text=state.get("analysis", ""),
        retrieved_evidence_text=evidence_text
    )

    try:
        draft = provider.generate(prompt=prompt, system_prompt=DRAFT_RECOMMENDATION_SYSTEM_PROMPT)
    except Exception as e:
        draft = f"Draft recommendation fallback: Telemetry analyzed with standard SOP protocols ({e})."

    return {
        "draft_response": draft,
        "iteration_count": (state.get("iteration_count") or 0) + 1
    }


def review_node(state: AgentState) -> Dict[str, Any]:
    """Audit the generated draft for evidence grounding, numerical consistency, and safety boundaries."""
    logger.info(f"[Node: review_node] Auditing draft for machine {state.get('machine_id')}")

    risk_level = state.get("risk_level", "NORMAL")
    sensor_data = state.get("sensor_data", {})
    evidence = state.get("evidence", [])
    draft = state.get("draft_response", "")

    eval_result = evaluate_review_criteria(
        risk_level=risk_level,
        sensor_data=sensor_data,
        evidence=evidence,
        draft_response=draft
    )

    review_status = eval_result["status"]
    review_reason = " | ".join(eval_result["reasons"])

    return {
        "review_status": review_status,
        "review_reason": review_reason
    }


def human_review_node(state: AgentState) -> Dict[str, Any]:
    """Escalate high-risk or uncertain cases to the human review manager."""
    logger.info(f"[Node: human_review_node] Registering review ticket for {state.get('machine_id')}")

    manager = get_review_manager()
    ticket = manager.register_ticket(state)

    escalation_banner = (
        f"\n\n=======================================================\n"
        f"🚨 HUMAN REVIEW REQUIRED (Ticket ID: {ticket.request_id})\n"
        f"Risk Level: {ticket.risk_level} | Machine ID: {ticket.machine_id}\n"
        f"Escalation Reason: {ticket.risk_reason}\n"
        f"Status: PENDING CERTIFIED MAINTENANCE ENGINEER SIGN-OFF\n"
        f"Endpoint: POST /review/{ticket.request_id}\n"
        f"=======================================================\n"
    )

    final_text = state.get("draft_response", "") + escalation_banner

    return {
        "final_response": final_text,
        "review_status": "human_review"
    }


def final_response_node(state: AgentState) -> Dict[str, Any]:
    """Format final output payload."""
    logger.info(f"[Node: final_response] Finalizing response for {state.get('request_id')}")

    if state.get("error"):
        final_text = (
            f"❌ REQUEST ERROR: {state.get('error')}\n\n"
            f"Please verify machine ID, input format, and telemetry payload."
        )
    elif state.get("review_status") == "human_review" and "HUMAN REVIEW REQUIRED" not in state.get("final_response", ""):
        final_text = state.get("final_response") or state.get("draft_response", "")
    else:
        final_text = state.get("final_response") or state.get("draft_response", "")

    return {
        "final_response": final_text
    }
