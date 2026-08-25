"""
ManufacturingAgent Machine History Tool
Retrieves operational telemetry history and maintenance records for machine assets.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MachineHistoryInput(BaseModel):
    machine_id: str = Field(description="Unique identifier of the target machine, e.g., 'M-101'")
    limit: int = Field(default=5, description="Maximum number of historical records to retrieve")


class MachineHistoryResult(BaseModel):
    success: bool
    machine_id: str
    history: List[Dict[str, Any]]
    maintenance_logs: List[Dict[str, Any]]
    error: Optional[str] = None


def get_machine_history(machine_id: str, limit: int = 5, data_path: str = "./data/machines.json") -> Dict[str, Any]:
    """
    Retrieve historical telemetry and maintenance logs for a specific machine.
    """
    if not machine_id or not machine_id.strip():
        return {
            "success": False,
            "machine_id": machine_id,
            "history": [],
            "maintenance_logs": [],
            "error": "Machine ID cannot be empty."
        }

    clean_id = machine_id.strip().upper()

    if not os.path.exists(data_path):
        return {
            "success": False,
            "machine_id": clean_id,
            "history": [],
            "maintenance_logs": [],
            "error": f"Database file '{data_path}' not found."
        }

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        machines = db.get("machines", {})
        if clean_id not in machines:
            return {
                "success": False,
                "machine_id": clean_id,
                "history": [],
                "maintenance_logs": [],
                "error": f"Machine '{clean_id}' not found in fleet database."
            }

        machine_data = machines[clean_id]
        history = machine_data.get("history", [])[-limit:]
        maintenance_logs = machine_data.get("maintenance_logs", [])

        return {
            "success": True,
            "machine_id": clean_id,
            "model": machine_data.get("model", "CNC-Mill-V4"),
            "history": history,
            "maintenance_logs": maintenance_logs,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "machine_id": clean_id,
            "history": [],
            "maintenance_logs": [],
            "error": f"Error retrieving machine history: {str(e)}"
        }
