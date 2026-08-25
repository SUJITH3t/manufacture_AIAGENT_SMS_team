"""
Unit Tests for LangGraph State Machine Routing and Execution
"""

import pytest
from backend.app.agent.graph import build_manufacturing_graph, ManufacturingAgentExecutor
from backend.app.agent.routing import route_after_validation, route_after_review


def test_graph_compilation():
    """Test that LangGraph compiles and initializes nodes and edges without error."""
    graph = build_manufacturing_graph()
    assert graph is not None


def test_normal_case_routing():
    """Test end-to-end execution of a NORMAL risk scenario."""
    executor = ManufacturingAgentExecutor()
    state = executor.run(
        machine_id="M-101",
        user_query="Check overall machine operational stability.",
        sensor_data={"temperature": 50.0, "vibration": 0.8, "pressure": 5.4, "speed": 4000, "status": "RUNNING"},
        provider="fallback"
    )

    assert state["risk_level"] == "NORMAL"
    assert state["review_status"] == "approved"
    assert len(state["evidence"]) > 0
    assert "draft_response" in state
    assert "final_response" in state
    assert "HUMAN REVIEW REQUIRED" not in state["final_response"]


def test_edge_case_routing():
    """Test end-to-end execution of an EDGE condition scenario."""
    executor = ManufacturingAgentExecutor()
    state = executor.run(
        machine_id="M-102",
        user_query="Spindle temperature is in warning zone. Recommend next steps.",
        sensor_data={"temperature": 75.0, "vibration": 1.2, "pressure": 5.0, "speed": 5000, "status": "WARN_TELEMETRY"},
        provider="fallback"
    )

    assert state["risk_level"] == "EDGE"
    assert len(state["evidence"]) > 0
    assert "calculate" in state["selected_tools"]


def test_high_risk_human_escalation_routing():
    """Test that HIGH risk triggers human escalation banner and review registration."""
    executor = ManufacturingAgentExecutor()
    state = executor.run(
        machine_id="M-201",
        user_query="Severe vibration excursion and overheating observed during heavy cut.",
        sensor_data={"temperature": 91.0, "vibration": 5.8, "pressure": 3.0, "speed": 8500, "status": "ELEVATED_RISK"},
        provider="fallback"
    )

    assert state["risk_level"] == "HIGH"
    assert state["review_status"] == "human_review"
    assert "HUMAN REVIEW REQUIRED" in state["final_response"]


def test_validation_failure_short_circuit():
    """Test that missing machine_id or query short-circuits to error output without crashing."""
    executor = ManufacturingAgentExecutor()
    state = executor.run(
        machine_id="",
        user_query="Check machine status.",
        provider="fallback"
    )
    assert state["error"] is not None
    assert "Missing required field" in state["error"]
