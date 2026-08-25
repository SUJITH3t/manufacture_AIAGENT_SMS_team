"""
Unit Tests for Human Review Workflow and Manager
"""

import pytest
from backend.app.agent.review import HumanReviewManager, evaluate_review_criteria


def test_human_review_ticket_lifecycle():
    """Test ticket registration, pending query, and sign-off decision lifecycle."""
    manager = HumanReviewManager()
    
    mock_state = {
        "request_id": "test_req_001",
        "machine_id": "M-201",
        "risk_level": "HIGH",
        "risk_reason": "Vibration > 3.8 mm/s and Temperature > 82°C",
        "sensor_data": {"temperature": 90.0, "vibration": 5.2},
        "user_query": "Severe bearing noise",
        "evidence": [{"source": "vibration_guidelines.md", "content": "Critical limits", "relevance": 0.9}],
        "draft_response": "Draft advisory for technician inspection."
    }

    # 1. Register ticket
    ticket = manager.register_ticket(mock_state)
    assert ticket.request_id == "test_req_001"
    assert ticket.risk_level == "HIGH"
    assert ticket.decision is None

    # 2. Check pending
    pending = manager.list_pending_tickets()
    assert any(t.request_id == "test_req_001" for t in pending)

    # 3. Submit human approval
    updated = manager.submit_decision("test_req_001", decision="approve", notes="Dispatched maintenance team.", reviewer_id="LEAD_TECH_01")
    assert updated.decision == "approve"
    assert updated.notes == "Dispatched maintenance team."
    assert updated.resolved_at is not None

    # 4. Confirm ticket is no longer pending
    pending_after = manager.list_pending_tickets()
    assert not any(t.request_id == "test_req_001" for t in pending_after)


def test_invalid_decision_rejection():
    """Test that invalid decision string raises ValueError."""
    manager = HumanReviewManager()
    manager.register_ticket({"request_id": "test_req_002", "machine_id": "M-201"})
    
    with pytest.raises(ValueError):
        manager.submit_decision("test_req_002", decision="invalid_action")


def test_review_safety_boundary_detection():
    """Test that drafts claiming autonomous physical actions trigger revision_required."""
    draft_with_violation = "Analysis complete. I have shut down the CNC machine and altered PLC registers."
    eval_res = evaluate_review_criteria(
        risk_level="NORMAL",
        sensor_data={"temperature": 50.0},
        evidence=[{"source": "doc", "content": "text"}],
        draft_response=draft_with_violation
    )
    assert eval_res["status"] == "revision_required"
    assert any("violates safety boundary" in r for r in eval_res["reasons"])
