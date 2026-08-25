# Human Review Audit Card Template

**Ticket ID**: `REQ-YYYYMMDD-XXXX`  
**Machine Asset ID**: `M-XXX` (Model: `CNC-Mill-V4` / `Lathe-Pro-X`)  
**Timestamp**: `YYYY-MM-DD HH:MM:SS UTC`  
**Triggered Risk Tier**: `[ ] NORMAL  [ ] EDGE  [X] HIGH`  

---

### 1. Telemetry Snapshot at Escalation
| Sensor Metric | Recorded Value | Engineering Nominal Band | Violation Severity |
| :--- | :--- | :--- | :--- |
| **Spindle Bearing Temperature** | `89.6 °C` | 35.0 - 68.0 °C | CRITICAL EXCURSION (>82°C) |
| **Vibration Velocity RMS** | `5.42 mm/s` | 0.2 - 1.8 mm/s | ISO 10816 CLASS C/D (>3.8 mm/s) |
| **Hydraulic Line Pressure** | `2.9 bar` | 4.5 - 6.5 bar | CRITICAL LOW (<3.8 bar) |
| **Spindle Speed** | `8200 RPM` | 1200 - 8500 RPM | High Intermittent |
| **Factory Ambient Humidity** | `48.0 %RH` | 30.0 - 65.0 %RH | Nominal |

---

### 2. Grounded RAG Citations
- **machine_manual.md (Section 2)**: Critical spindle thermal limit >82.0°C.
- **vibration_guidelines.md (ISO 10816-3)**: Velocity RMS >3.8 mm/s indicates severe bearing raceway spalling.
- **pressure_guidelines.md (Section 2)**: Pressure <3.8 bar introduces risk of un-clamped tool pullout in cut.

---

### 3. Model Diagnostic Root-Cause Hypothesis
The combination of rapid thermal rise, ISO Class D vibration velocity, and depleted hydraulic pressure indicates simultaneous bearing cage fatigue and proportional relief valve seal degradation.

---

### 4. Human Engineer Decision & Sign-off
**Reviewer Action**:
- [ ] **APPROVE**: Dispatch maintenance work order and schedule asset inspection.
- [ ] **REJECT**: False positive / known calibration test run.
- [ ] **REQUEST REVISION**: Request agent re-analysis with modified operational assumptions.

**Reviewer ID**: `TECH-ENG-XXXX`  
**Action Notes**:  
`____________________________________________________________________________________`  
`____________________________________________________________________________________`  
**Sign-off Timestamp**: `____________________`
