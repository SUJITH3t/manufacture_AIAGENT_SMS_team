"""
ManufacturingAgent LangGraph Graph Definition
Constructs and compiles the end-to-end StateGraph workflow.
"""

import time
import logging
from langgraph.graph import StateGraph, START, END
from backend.app.agent.state import AgentState
from backend.app.agent.nodes import (
    validate_input_node,
    risk_assessment_node,
    route_request_node,
    retrieve_evidence_node,
    analyze_sensor_data_node,
    generate_draft_node,
    review_node,
    human_review_node,
    final_response_node,
)
from backend.app.agent.routing import (
    route_after_validation,
    route_after_risk_assessment,
    route_after_review,
)

logger = logging.getLogger(__name__)


def build_manufacturing_graph() -> StateGraph:
    """Build and compile the complete ManufacturingAgent LangGraph workflow."""
    builder = StateGraph(AgentState)

    # 1. Add all nodes
    builder.add_node("validate_input", validate_input_node)
    builder.add_node("risk_assessment", risk_assessment_node)
    builder.add_node("route_request", route_request_node)
    builder.add_node("retrieve_evidence", retrieve_evidence_node)
    builder.add_node("analyze_sensor_data", analyze_sensor_data_node)
    builder.add_node("generate_draft", generate_draft_node)
    builder.add_node("review_node", review_node)
    builder.add_node("human_review_node", human_review_node)
    builder.add_node("final_response", final_response_node)

    # 2. Connect START -> validate_input
    builder.add_edge(START, "validate_input")

    # 3. Add conditional edge from validate_input
    builder.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "risk_assessment": "risk_assessment",
            "final_response": "final_response"
        }
    )

    # 4. Standard linear flow through risk & RAG pipeline
    builder.add_edge("risk_assessment", "route_request")
    builder.add_edge("route_request", "retrieve_evidence")
    builder.add_edge("retrieve_evidence", "analyze_sensor_data")
    builder.add_edge("analyze_sensor_data", "generate_draft")
    builder.add_edge("generate_draft", "review_node")

    # 5. Conditional routing after review
    builder.add_conditional_edges(
        "review_node",
        route_after_review,
        {
            "final_response": "final_response",
            "human_review_node": "human_review_node",
            "analyze_sensor_data": "analyze_sensor_data"
        }
    )

    # 6. Complete workflow
    builder.add_edge("human_review_node", "final_response")
    builder.add_edge("final_response", END)

    # Compile workflow
    graph = builder.compile()
    logger.info("Compiled ManufacturingAgent LangGraph workflow successfully.")
    return graph


class ManufacturingAgentExecutor:
    """Convenience executor wrapper around the compiled LangGraph."""

    def __init__(self):
        self.graph = build_manufacturing_graph()

    def run(
        self,
        machine_id: str,
        user_query: str,
        sensor_data: dict = None,
        request_id: str = None,
        provider: str = "fallback"
    ) -> AgentState:
        """Execute full decision-support pipeline."""
        start_time = time.time()
        req_id = request_id or f"req_{int(time.time() * 1000)}"

        initial_state: AgentState = {
            "request_id": req_id,
            "machine_id": machine_id,
            "sensor_data": sensor_data or {},
            "user_query": user_query,
            "risk_level": "NORMAL",
            "risk_reason": "",
            "tool_required": False,
            "selected_tools": [],
            "retrieved_documents": [],
            "evidence": [],
            "analysis": "",
            "draft_response": "",
            "review_status": "approved",
            "review_reason": "",
            "human_decision": None,
            "human_notes": None,
            "final_response": "",
            "provider": provider,
            "error": None,
            "latency": 0.0,
            "iteration_count": 0
        }

        final_state = self.graph.invoke(initial_state)
        final_state["latency"] = round(time.time() - start_time, 4)
        return final_state
