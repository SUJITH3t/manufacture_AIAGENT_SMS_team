"""
ManufacturingAgent Review Management and Audit Evaluation
Manages draft quality evaluation and human-in-the-loop escalation tickets.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReviewDecisionRequest(BaseModel):
    decision: str = Field(description="'approve', 'reject', or 'request_revision'")
    notes: Optional[str] = Field(default="", description="Operator/engineer feedback notes")
    reviewer_id: Optional[str] = Field(default="HUMAN_ENG_01", description="ID of the human reviewer")


class HumanReviewTicket(BaseModel):
    request_id: str
    machine_id: str
    risk_level: str
    risk_reason: str
    sensor_data: Dict[str, Any]
    user_query: str
    evidence_count: int
    draft_response: str
    review_status: str
    created_at: float = Field(default_factory=time.time)
    decision: Optional[str] = None
    notes: Optional[str] = None
    reviewer_id: Optional[str] = None
    resolved_at: Optional[float] = None


class HumanReviewManager:
    """Thread-safe in-memory store for pending and resolved human review tickets."""

    def __init__(self):
        self._tickets: Dict[str, HumanReviewTicket] = {}

    def register_ticket(self, state: Dict[str, Any]) -> HumanReviewTicket:
        """Create or update a human review ticket from the agent state."""
        req_id = state.get("request_id", f"req_{int(time.time())}")
        ticket = HumanReviewTicket(
            request_id=req_id,
            machine_id=state.get("machine_id", "UNKNOWN"),
            risk_level=state.get("risk_level", "HIGH"),
            risk_reason=state.get("risk_reason", "High operational risk requiring human review."),
            sensor_data=state.get("sensor_data", {}),
            user_query=state.get("user_query", ""),
            evidence_count=len(state.get("evidence", [])),
            draft_response=state.get("draft_response", ""),
            review_status="human_review"
        )
        self._tickets[req_id] = ticket
        logger.info(f"Registered Human Review Ticket: {req_id} for Machine {ticket.machine_id}")
        return ticket

    def get_ticket(self, request_id: str) -> Optional[HumanReviewTicket]:
        return self._tickets.get(request_id)

    def list_pending_tickets(self) -> List[HumanReviewTicket]:
        return [t for t in self._tickets.values() if t.decision is None]

    def list_all_tickets(self) -> List[HumanReviewTicket]:
        return list(self._tickets.values())

    def submit_decision(self, request_id: str, decision: str, notes: str = "", reviewer_id: str = "HUMAN_ENG_01") -> Optional[HumanReviewTicket]:
        ticket = self._tickets.get(request_id)
        if not ticket:
            return None

        clean_dec = decision.lower().strip()
        if clean_dec not in ["approve", "reject", "request_revision"]:
            raise ValueError(f"Invalid decision '{decision}'. Must be 'approve', 'reject', or 'request_revision'.")

        ticket.decision = clean_dec
        ticket.notes = notes
        ticket.reviewer_id = reviewer_id
        ticket.resolved_at = time.time()
        logger.info(f"Resolved Human Review Ticket {request_id} with decision '{clean_dec}'")
        return ticket


_GLOBAL_REVIEW_MANAGER = HumanReviewManager()


def get_review_manager() -> HumanReviewManager:
    return _GLOBAL_REVIEW_MANAGER


def evaluate_review_criteria(
    risk_level: str,
    sensor_data: Dict[str, Any],
    evidence: List[Dict[str, Any]],
    draft_response: str
) -> Dict[str, Any]:
    """
    Evaluates evidence availability, consistency with sensor data, risk tier,
    unsupported claims, and whether human review is required.
    """
    reasons: List[str] = []
    
    # 1. Evidence availability check
    has_evidence = len(evidence) > 0
    if not has_evidence:
        reasons.append("No authoritative SOP or manual evidence chunks were retrieved.")

    # 2. Risk level check
    is_high_risk = risk_level == "HIGH"
    is_edge_risk = risk_level == "EDGE"

    # 3. Sensor anomaly check
    temp = sensor_data.get("temperature", 0.0)
    vib = sensor_data.get("vibration", 0.0)
    pres = sensor_data.get("pressure", 0.0)

    # 4. Check for safety boundaries / prohibited autonomous actuation claims
    prohibited_phrases = [
        "i have shut down", "machine has been stopped", "override plc",
        "changing production settings", "cutting power", "bypassed safety"
    ]
    lower_draft = draft_response.lower()
    for phrase in prohibited_phrases:
        if phrase in lower_draft:
            reasons.append(f"Draft violates safety boundary by claiming autonomous physical action: '{phrase}'")

    # Determine Review Status
    if is_high_risk:
        status = "human_review"
        reasons.append("Asset is operating in HIGH risk tier. Mandatory human escalation required.")
    elif "violates safety boundary" in "".join(reasons):
        status = "revision_required"
    elif not has_evidence and is_edge_risk:
        status = "human_review"
        reasons.append("Edge condition detected without conclusive grounded evidence.")
    else:
        status = "approved"
        reasons.append("Draft recommendation is evidence-grounded, consistent with telemetry, and adheres to non-actuation boundaries.")

    return {
        "status": status,
        "reasons": reasons,
        "requires_human": (status == "human_review")
    }
