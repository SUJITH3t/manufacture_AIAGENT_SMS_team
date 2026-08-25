"""
ManufacturingAgent LangGraph Conditional Routing Logic
Determines dynamic state machine transitions based on input validity, risk assessment, and review outcome.
"""

import logging
from backend.app.agent.state import AgentState

logger = logging.getLogger(__name__)


def route_after_validation(state: AgentState) -> str:
    """Route after input validation: proceed to risk assessment or short-circuit on error."""
    if state.get("error"):
        return "final_response"
    return "risk_assessment"


def route_after_risk_assessment(state: AgentState) -> str:
    """
    Route based on initial risk assessment:
    All standard queries proceed to retrieve_evidence to ensure grounded context.
    """
    risk_level = state.get("risk_level", "NORMAL")
    logger.info(f"[Graph Router] Risk Level determined: {risk_level}")
    return "retrieve_evidence"


def route_after_review(state: AgentState) -> str:
    """
    Conditional routing after review node:
    - 'approved' -> final_response
    - 'revision_required' -> re-attempt analysis/draft (up to 2 iterations), otherwise human_review
    - 'human_review' -> human_review_node
    """
    status = state.get("review_status", "approved")
    iterations = state.get("iteration_count", 0)

    if status == "human_review":
        logger.info("[Graph Router] Routing to HUMAN REVIEW queue.")
        return "human_review_node"

    elif status == "revision_required":
        if iterations < 2:
            logger.info(f"[Graph Router] Revision requested (Iteration {iterations + 1}). Re-routing to analysis.")
            return "analyze_sensor_data"
        else:
            logger.warning("[Graph Router] Max revisions exceeded. Escalating to human review.")
            return "human_review_node"

    else:
        logger.info("[Graph Router] Review approved. Routing to final response.")
        return "final_response"
