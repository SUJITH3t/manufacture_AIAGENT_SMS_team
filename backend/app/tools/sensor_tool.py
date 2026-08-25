"""
ManufacturingAgent Sensor Tool
Retrieves current real-time telemetry from the machine fleet data source.
"""

import json
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SensorDataInput(BaseModel):
    machine_id: str = Field(description="Unique identifier of the target machine, e.g., 'M-101'")


class SensorToolResult(BaseModel):
    success: bool
    machine_id: str
    sensor_data: Dict[str, Any]
    error: Optional[str] = None


def get_sensor_data(machine_id: str, data_path: str = "./data/machines.json") -> Dict[str, Any]:
    """
    Retrieve current sensor telemetry for the given machine_id.
    Returns dictionary with temperature, vibration, pressure, speed, humidity, and status.
    """
    if not machine_id or not machine_id.strip():
        return {
            "success": False,
            "machine_id": machine_id,
            "sensor_data": {},
            "error": "Machine ID cannot be empty."
        }

    clean_id = machine_id.strip().upper()

    if not os.path.exists(data_path):
        return {
            "success": False,
            "machine_id": clean_id,
            "sensor_data": {},
            "error": f"Database file '{data_path}' not found."
        }

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        machines = db.get("machines", {})
        if clean_id not in machines:
            # If not in simulated db, provide a default dynamic profile
            return {
                "success": False,
                "machine_id": clean_id,
                "sensor_data": {},
                "error": f"Machine '{clean_id}' not found in active fleet registry."
            }

        machine_record = machines[clean_id]
        sensor_data = machine_record.get("current_sensors", {})
        return {
            "success": True,
            "machine_id": clean_id,
            "model": machine_record.get("model", "CNC-Mill-V4"),
            "location": machine_record.get("location", "Unknown Bay"),
            "sensor_data": sensor_data,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "machine_id": clean_id,
            "sensor_data": {},
            "error": f"Failed reading sensor telemetry: {str(e)}"
        }
