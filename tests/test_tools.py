"""
Unit Tests for ManufacturingAgent Operational Tools
"""

import pytest
from backend.app.tools.sensor_tool import get_sensor_data
from backend.app.tools.history_tool import get_machine_history
from backend.app.tools.calculator_tool import calculate
from backend.app.tools.retrieval_tool import retrieve_manufacturing_guidelines


def test_get_sensor_data_valid():
    """Test retrieving valid sensor telemetry for known machine."""
    res = get_sensor_data("M-101")
    assert res["success"] is True
    assert res["machine_id"] == "M-101"
    assert "temperature" in res["sensor_data"]
    assert "vibration" in res["sensor_data"]
    assert res["sensor_data"]["status"] == "RUNNING"


def test_get_sensor_data_unknown_machine():
    """Test retrieving sensor data for non-existent machine."""
    res = get_sensor_data("M-999")
    assert res["success"] is False
    assert "not found" in res["error"].lower()


def test_get_sensor_data_empty_id():
    """Test error handling for empty machine ID."""
    res = get_sensor_data("")
    assert res["success"] is False
    assert "cannot be empty" in res["error"].lower()


def test_get_machine_history_valid():
    """Test retrieving telemetry history and maintenance logs."""
    res = get_machine_history("M-101", limit=3)
    assert res["success"] is True
    assert len(res["history"]) > 0
    assert len(res["maintenance_logs"]) > 0


def test_calculator_valid_expressions():
    """Test safe engineering calculations."""
    res1 = calculate("(85.2 - 68.0) / 68.0 * 100")
    assert res1["success"] is True
    assert round(res1["result"], 2) == 25.29

    res2 = calculate("sqrt(16) + 10")
    assert res2["success"] is True
    assert res2["result"] == 14.0


def test_calculator_security_guardrails():
    """Test that arbitrary code execution and dangerous builtins are strictly blocked."""
    evil_expressions = [
        "__import__('os').system('ls')",
        "eval('2+2')",
        "open('/etc/passwd')",
        "exec('x=1')",
        "globals()"
    ]
    for expr in evil_expressions:
        res = calculate(expr)
        assert res["success"] is False
        assert res["result"] is None
        assert "disallowed" in res["error"].lower() or "unauthorized" in res["error"].lower()


def test_calculator_zero_division():
    """Test division by zero handling."""
    res = calculate("100 / 0")
    assert res["success"] is False
    assert "division by zero" in res["error"].lower()


def test_retrieve_manufacturing_guidelines():
    """Test RAG retrieval tool returns structured evidence with source citations."""
    res = retrieve_manufacturing_guidelines("spindle bearing overheating lubrication", top_k=3)
    assert res["success"] is True
    assert res["evidence_count"] > 0
    first_item = res["evidence"][0]
    assert "source" in first_item
    assert "content" in first_item
    assert "relevance" in first_item
    assert first_item["relevance"] >= 0.0
