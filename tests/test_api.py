"""
Integration Tests for FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_analyze_normal_case():
    """Test /analyze endpoint for standard normal telemetry."""
    payload = {
        "machine_id": "M-101",
        "user_query": "Verify telemetry metrics.",
        "sensor_data": {
            "temperature": 52.0,
            "vibration": 0.85,
            "pressure": 5.4,
            "speed": 4500,
            "humidity": 45.0,
            "status": "RUNNING"
        },
        "provider": "fallback"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["machine_id"] == "M-101"
    assert data["risk_level"] == "NORMAL"
    assert data["retrieved_evidence_count"] > 0
    assert data["review_status"] == "approved"
    assert data["latency_seconds"] >= 0.0


def test_analyze_high_risk_escalation():
    """Test /analyze endpoint for critical high-risk breach."""
    payload = {
        "machine_id": "M-201",
        "user_query": "Critical vibration excursion and overheating during roughing.",
        "sensor_data": {
            "temperature": 91.5,
            "vibration": 5.8,
            "pressure": 2.8,
            "speed": 8200,
            "status": "ELEVATED_RISK"
        },
        "provider": "fallback"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "HIGH"
    assert data["review_status"] == "human_review"
    assert "HUMAN REVIEW REQUIRED" in data["final_response"]

    # Verify ticket appears in pending review queue
    req_id = data["request_id"]
    pending_res = client.get("/review/pending")
    assert pending_res.status_code == 200
    pending_data = pending_res.json()
    assert any(t["request_id"] == req_id for t in pending_data["tickets"])


def test_human_review_decision_submission():
    """Test submitting human sign-off via POST /review/{request_id}."""
    # 1. Trigger high risk analysis to create ticket
    trigger_payload = {
        "machine_id": "M-201",
        "user_query": "Escalation trigger test.",
        "sensor_data": {"temperature": 95.0, "vibration": 6.0, "pressure": 2.0},
        "provider": "fallback"
    }
    trigger_res = client.post("/analyze", json=trigger_payload)
    req_id = trigger_res.json()["request_id"]

    # 2. Submit human approval
    decision_payload = {
        "decision": "approve",
        "notes": "Verified bearing damage. Dispatched mechanical team.",
        "reviewer_id": "CHIEF_MAINT_ENG_01"
    }
    review_res = client.post(f"/review/{req_id}", json=decision_payload)
    assert review_res.status_code == 200
    rev_data = review_res.json()
    assert rev_data["success"] is True
    assert rev_data["decision"] == "approve"

    # 3. Verify ticket query
    get_ticket_res = client.get(f"/review/{req_id}")
    assert get_ticket_res.status_code == 200
    assert get_ticket_res.json()["decision"] == "approve"


def test_analyze_empty_inputs_error():
    """Test error handling for missing query and machine ID."""
    res1 = client.post("/analyze", json={"machine_id": "", "user_query": "test"})
    assert res1.status_code == 400

    res2 = client.post("/analyze", json={"machine_id": "M-101", "user_query": ""})
    assert res2.status_code == 400


def test_calculator_tool_endpoint():
    """Test /tools/calculate endpoint."""
    res = client.post("/tools/calculate", json={"expression": "15 * 4 + 2"})
    assert res.status_code == 200
    assert res.json()["result"] == 62


def test_list_machines_endpoint():
    """Test /machines endpoint returns simulated fleet."""
    res = client.get("/machines")
    assert res.status_code == 200
    data = res.json()
    assert "machines" in data
    assert "M-101" in data["machines"]
