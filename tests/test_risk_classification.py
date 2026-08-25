"""
Unit Tests for Manufacturing Risk Classification & Threshold Rules
"""

import pytest
from backend.app.tools.risk_tool import evaluate_machine_risk, THRESHOLDS


def test_normal_telemetry_evaluation():
    """Test that safe nominal sensor values classify strictly as NORMAL."""
    normal_sensors = {
        "temperature": 52.0,
        "vibration": 0.85,
        "pressure": 5.4,
        "speed": 4500,
        "humidity": 45.0,
        "status": "RUNNING"
    }
    result = evaluate_machine_risk(normal_sensors)
    assert result["risk_level"] == "NORMAL"
    assert result["requires_human_escalation"] is False
    assert result["risk_score"] < 0.40
    assert len(result["anomalies"]) == 0


def test_edge_temperature_drift():
    """Test that temperatures in 68.1°C - 82.0°C trigger EDGE risk."""
    edge_temp_sensors = {
        "temperature": 75.2,
        "vibration": 1.20,
        "pressure": 5.2,
        "speed": 6000,
        "status": "WARN_TELEMETRY"
    }
    result = evaluate_machine_risk(edge_temp_sensors)
    assert result["risk_level"] == "EDGE"
    assert "elevated_temperature_edge" in result["anomalies"]


def test_edge_vibration_warning():
    """Test that ISO 10816 Class B vibration (1.81 - 3.8 mm/s) triggers EDGE risk."""
    edge_vib_sensors = {
        "temperature": 55.0,
        "vibration": 2.70,
        "pressure": 5.0,
        "speed": 5000,
        "status": "WARN_TELEMETRY"
    }
    result = evaluate_machine_risk(edge_vib_sensors)
    assert result["risk_level"] == "EDGE"
    assert "elevated_vibration_edge" in result["anomalies"]


def test_high_risk_temperature_excursion():
    """Test that spindle temperature > 82.0°C triggers HIGH risk and human escalation."""
    high_temp_sensors = {
        "temperature": 89.5,
        "vibration": 1.5,
        "pressure": 5.2,
        "speed": 7500,
        "status": "ELEVATED_RISK"
    }
    result = evaluate_machine_risk(high_temp_sensors)
    assert result["risk_level"] == "HIGH"
    assert result["requires_human_escalation"] is True
    assert "critical_temperature_excursion" in result["anomalies"]


def test_high_risk_vibration_breach():
    """Test that ISO 10816 Class C/D vibration (> 3.8 mm/s) triggers HIGH risk."""
    high_vib_sensors = {
        "temperature": 58.0,
        "vibration": 5.60,
        "pressure": 5.0,
        "speed": 8000,
        "status": "ELEVATED_RISK"
    }
    result = evaluate_machine_risk(high_vib_sensors)
    assert result["risk_level"] == "HIGH"
    assert result["requires_human_escalation"] is True
    assert "critical_vibration_excursion" in result["anomalies"]


def test_high_risk_low_hydraulic_pressure():
    """Test that hydraulic pressure below 3.8 bar triggers HIGH risk."""
    low_pres_sensors = {
        "temperature": 50.0,
        "vibration": 0.8,
        "pressure": 2.4,
        "speed": 4000,
        "status": "ELEVATED_RISK"
    }
    result = evaluate_machine_risk(low_pres_sensors)
    assert result["risk_level"] == "HIGH"
    assert result["requires_human_escalation"] is True
    assert "critical_low_hydraulic_pressure" in result["anomalies"]


def test_sensor_fault_negative_values():
    """Test that non-physical readings trigger sensor fault detection and escalation."""
    fault_sensors = {
        "temperature": -999.0,
        "vibration": 0.0,
        "pressure": -1.0,
        "speed": 0,
        "status": "SENSOR_FAULT"
    }
    result = evaluate_machine_risk(fault_sensors)
    assert result["risk_level"] == "HIGH"
    assert result["requires_human_escalation"] is True
    assert "temperature_sensor_fault" in result["anomalies"]


def test_empty_sensor_payload():
    """Test that empty payload safely defaults to HIGH risk escalation."""
    result = evaluate_machine_risk({})
    assert result["risk_level"] == "HIGH"
    assert result["requires_human_escalation"] is True
