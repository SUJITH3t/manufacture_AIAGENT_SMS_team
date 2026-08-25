"""
ManufacturingAgent Risk Evaluation Tool
Evaluates manufacturing telemetry against deterministic engineering standards and ISO 10816 tolerances.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RiskEvaluationInput(BaseModel):
    sensor_data: Dict[str, Any] = Field(description="Dictionary containing temperature, vibration, pressure, speed, humidity, and status")


class RiskEvaluationResult(BaseModel):
    risk_level: str = Field(description="'NORMAL', 'EDGE', or 'HIGH'")
    risk_score: float = Field(description="Numerical risk index from 0.0 (safest) to 1.0 (critical)")
    reasons: List[str] = Field(description="Specific engineering rationale for the risk score")
    requires_human_escalation: bool = Field(description="True if risk_level is HIGH or critical sensor failure")
    anomalies: List[str] = Field(description="Specific anomalous parameters identified")


# Standard Engineering Thresholds
THRESHOLDS = {
    "temperature": {
        "normal_max": 68.0,
        "edge_max": 82.0,
        "critical_min_valid": -20.0,
        "critical_max_valid": 300.0,
    },
    "vibration": {
        "normal_max": 1.8,
        "edge_max": 3.8,
        "critical_min_valid": 0.0,
        "critical_max_valid": 50.0,
    },
    "pressure": {
        "normal_min": 4.5,
        "normal_max": 6.5,
        "edge_low": 3.8,
        "edge_high": 7.8,
        "critical_min_valid": 0.0,
        "critical_max_valid": 25.0,
    },
    "speed": {
        "normal_max": 8500,
        "edge_max": 12000,
        "critical_min_valid": 0,
        "critical_max_valid": 25000,
    }
}


def evaluate_machine_risk(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate sensor data against industrial standards.
    Categorizes into NORMAL, EDGE, or HIGH risk with clear audit reasons.
    """
    if not sensor_data:
        return {
            "risk_level": "HIGH",
            "risk_score": 0.95,
            "reasons": ["Empty or missing sensor telemetry received. Cannot verify asset safety."],
            "requires_human_escalation": True,
            "anomalies": ["missing_sensor_payload"]
        }

    reasons: List[str] = []
    anomalies: List[str] = []
    max_severity = 0.1  # baseline normal

    # 1. Check for Sensor Fault / Out of physical range values
    temp = sensor_data.get("temperature")
    vib = sensor_data.get("vibration")
    pres = sensor_data.get("pressure")
    speed = sensor_data.get("speed")
    status = str(sensor_data.get("status", "")).upper()

    # Telemetry validity checks
    if temp is not None and (temp < THRESHOLDS["temperature"]["critical_min_valid"] or temp > THRESHOLDS["temperature"]["critical_max_valid"]):
        reasons.append(f"Temperature sensor reporting non-physical reading ({temp}°C). Potential transducer failure.")
        anomalies.append("temperature_sensor_fault")
        max_severity = max(max_severity, 0.9)

    if vib is not None and (vib < THRESHOLDS["vibration"]["critical_min_valid"] or vib > THRESHOLDS["vibration"]["critical_max_valid"]):
        reasons.append(f"Vibration accelerometer reporting non-physical value ({vib} mm/s).")
        anomalies.append("vibration_sensor_fault")
        max_severity = max(max_severity, 0.9)

    if pres is not None and (pres < THRESHOLDS["pressure"]["critical_min_valid"] or pres > THRESHOLDS["pressure"]["critical_max_valid"]):
        reasons.append(f"Hydraulic pressure sensor reporting non-physical reading ({pres} bar).")
        anomalies.append("pressure_sensor_fault")
        max_severity = max(max_severity, 0.9)

    # 2. Temperature Evaluation
    if temp is not None and temp > THRESHOLDS["temperature"]["critical_min_valid"]:
        if temp > THRESHOLDS["temperature"]["edge_max"]:
            reasons.append(f"Spindle temperature {temp}°C breaches critical limit (> {THRESHOLDS['temperature']['edge_max']}°C). High risk of bearing seizure.")
            anomalies.append("critical_temperature_excursion")
            max_severity = max(max_severity, 0.88)
        elif temp > THRESHOLDS["temperature"]["normal_max"]:
            reasons.append(f"Spindle temperature {temp}°C in advisory drift zone ({THRESHOLDS['temperature']['normal_max']}°C - {THRESHOLDS['temperature']['edge_max']}°C).")
            anomalies.append("elevated_temperature_edge")
            max_severity = max(max_severity, 0.55)

    # 3. Vibration Evaluation (ISO 10816)
    if vib is not None and vib >= 0.0:
        if vib > THRESHOLDS["vibration"]["edge_max"]:
            reasons.append(f"Vibration velocity {vib} mm/s RMS exceeds ISO 10816 critical threshold (> {THRESHOLDS['vibration']['edge_max']} mm/s). High risk of tool breakage or bearing spalling.")
            anomalies.append("critical_vibration_excursion")
            max_severity = max(max_severity, 0.92)
        elif vib > THRESHOLDS["vibration"]["normal_max"]:
            reasons.append(f"Vibration velocity {vib} mm/s RMS in Class B warning zone ({THRESHOLDS['vibration']['normal_max']} - {THRESHOLDS['vibration']['edge_max']} mm/s).")
            anomalies.append("elevated_vibration_edge")
            max_severity = max(max_severity, 0.52)

    # 4. Pressure Evaluation
    if pres is not None and pres >= 0.0:
        if pres < THRESHOLDS["pressure"]["edge_low"]:
            reasons.append(f"Hydraulic line pressure {pres} bar critically low (< {THRESHOLDS['pressure']['edge_low']} bar). Risk of tool unclamping in cut.")
            anomalies.append("critical_low_hydraulic_pressure")
            max_severity = max(max_severity, 0.85)
        elif pres > THRESHOLDS["pressure"]["edge_high"]:
            reasons.append(f"Hydraulic line pressure {pres} bar critically high (> {THRESHOLDS['pressure']['edge_high']} bar). Risk of seal blowout.")
            anomalies.append("critical_high_hydraulic_pressure")
            max_severity = max(max_severity, 0.85)
        elif pres < THRESHOLDS["pressure"]["normal_min"] or pres > THRESHOLDS["pressure"]["normal_max"]:
            reasons.append(f"Hydraulic line pressure {pres} bar in warning band (nominal {THRESHOLDS['pressure']['normal_min']}-{THRESHOLDS['pressure']['normal_max']} bar).")
            anomalies.append("pressure_warning_edge")
            max_severity = max(max_severity, 0.48)

    # 5. Speed Evaluation
    if speed is not None and speed > THRESHOLDS["speed"]["normal_max"]:
        if speed > THRESHOLDS["speed"]["edge_max"]:
            reasons.append(f"Spindle speed {speed} RPM exceeds rated maximum machine limit.")
            anomalies.append("critical_overspeed")
            max_severity = max(max_severity, 0.82)
        else:
            reasons.append(f"Spindle speed {speed} RPM is in high intermittent duty zone.")
            anomalies.append("intermittent_speed_edge")
            max_severity = max(max_severity, 0.45)

    # 6. Combined Multi-variable compound risk check
    has_critical = any("critical" in a or "fault" in a for a in anomalies)
    if len(anomalies) >= 2:
        if has_critical:
            max_severity = min(1.0, max_severity + 0.10)
            reasons.append("Multiple critical sensor deviations detected; compound operational failure risk.")
        else:
            max_severity = min(0.65, max_severity + 0.08)
            reasons.append("Multiple concurrent telemetry warnings detected; close monitoring advised.")

    # Status tag review
    if status in ["ELEVATED_RISK", "CRITICAL"]:
        max_severity = max(max_severity, 0.85)
    elif status == "SENSOR_FAULT":
        max_severity = max(max_severity, 0.90)

    # Final Risk Tier Assignment
    if max_severity >= 0.70:
        risk_level = "HIGH"
        requires_human = True
    elif max_severity >= 0.40:
        risk_level = "EDGE"
        requires_human = False  # May require depending on evidence or review node
    else:
        risk_level = "NORMAL"
        requires_human = False

    if not reasons:
        reasons.append("All measured telemetry parameters are strictly within nominal manufacturer tolerances.")

    return {
        "risk_level": risk_level,
        "risk_score": round(max_severity, 3),
        "reasons": reasons,
        "requires_human_escalation": requires_human,
        "anomalies": anomalies
    }
