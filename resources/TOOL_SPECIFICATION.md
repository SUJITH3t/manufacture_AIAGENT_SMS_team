# Structured Telemetry Tools Specification

**ManufacturingAgent: Tool API and Interface Definitions**

---

## 1. Tool Summary Matrix

| Tool Function | Purpose | Input Schema | Output Schema |
| :--- | :--- | :--- | :--- |
| `get_sensor_data` | Reads real-time telemetry from fleet DB | `machine_id: str` | `SensorToolResult` (`dict`) |
| `get_machine_history` | Fetches historical telemetry & maintenance logs | `machine_id: str`, `limit: int` | `MachineHistoryResult` (`dict`) |
| `calculate` | Safely evaluates engineering math expressions | `expression: str` | `CalculatorResult` (`dict`) |
| `evaluate_machine_risk` | Computes ISO 10816 and thermal risk tiers | `sensor_data: dict` | `RiskEvaluationResult` (`dict`) |
| `retrieve_manufacturing_guidelines` | RAG query tool returning manual excerpts | `query: str`, `top_k: int` | `RetrievalToolResult` (`dict`) |

---

## 2. Tool Details & Security Guardrails

### 2.1 `calculate(expression: str)`
- **Security Sandboxing**: Strictly prevents arbitrary code execution (`eval` injection).
- **Disallowed Tokens**: Blocks `__import__`, `eval`, `exec`, `globals`, `locals`, `open`, `os`, `sys`, `subprocess`, `class`, `lambda`.
- **Whitelisted Math Functions**: `abs`, `round`, `min`, `max`, `sum`, `sqrt`, `pow`, `log`, `exp`, `pi`, `e`.
- **Error Handling**: Gracefully handles division by zero and non-finite results (`NaN`, `Inf`).

### 2.2 `evaluate_machine_risk(sensor_data: dict)`
- **Engineering Tolerances**:
  - **Spindle Temperature**: Normal $\le 68.0^\circ\text{C}$, Edge $68.1 - 82.0^\circ\text{C}$, High $> 82.0^\circ\text{C}$.
  - **Vibration Velocity RMS**: Normal $\le 1.8\text{ mm/s}$ (ISO Class A), Edge $1.81 - 3.8\text{ mm/s}$ (Class B), High $> 3.8\text{ mm/s}$ (Class C/D).
  - **Hydraulic Pressure**: Normal $4.5 - 6.5\text{ bar}$, Edge $3.8 - 4.4\text{ bar}$ or $6.6 - 7.8\text{ bar}$, High $< 3.8\text{ bar}$ or $> 7.8\text{ bar}$.
  - **Sensor Faults**: Non-physical values (e.g. $-999^\circ\text{C}$, $-1\text{ bar}$) trigger automatic `HIGH` risk escalation.

### 2.3 `get_sensor_data(machine_id: str)` and `get_machine_history(machine_id: str)`
- Reads machine fleet profiles from `data/machines.json`.
- Handles unknown machine IDs gracefully with informative diagnostic error messages.
