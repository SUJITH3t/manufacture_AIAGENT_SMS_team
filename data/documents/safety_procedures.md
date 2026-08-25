# AI Decision Support Safety Procedures and Non-Actuation Protocol

## 1. Fundamental Safety Boundary
The ManufacturingAgent system functions strictly as a bounded decision-support and telemetry analytics assistant. Under no operational conditions may the software:
1. Directly issue PLC or CNC CNC-G-code commands.
2. Trigger autonomous emergency-stops (E-Stop) or safety interlock bypasses.
3. Automatically alter spindle RPM, axis feed rates, or coolant flow valves.
4. Execute physical modifications to physical shop-floor assets.

All recommendations and risk assessments produced by this system represent advisory telemetry evaluations designed to augment human operator and maintenance engineer situational awareness.

## 2. Risk Tier Escalation Matrix
- **NORMAL Risk**:
  - Telemetry parameters conform to baseline manufacturer tolerances.
  - Autonomous advisory response generated with retrieved technical citations.
  - Review status: `approved`.
- **EDGE Risk**:
  - Borderline telemetry (e.g. slight temperature rise 68-82°C, moderate vibration 1.9-3.8 mm/s, or contradictory trends).
  - System executes extended multi-document retrieval and flags recommendations with maintenance check reminders.
  - Review status: `approved` with advisory or `human_review` if confidence score is low.
- **HIGH Risk**:
  - Severe breaches (Temperature > 82°C, Vibration > 3.8 mm/s, Pressure < 3.8 bar or > 7.8 bar, or critical multi-variable anomalies).
  - Direct autonomous action is STRICTLY PROHIBITED.
  - System must set review status to `human_review` and prominently display: `HUMAN REVIEW REQUIRED`.
  - An audit record is created in the human review queue (`/review/{request_id}`).

## 3. Human Review Signoff and Audit Trail
Certified maintenance engineers or floor supervisors review escalated cases via the decision-support interface. Actions available:
- `approve`: Human supervisor confirms analysis and approves dispatch of maintenance team.
- `reject`: Human supervisor determines reading is false positive (e.g. known dry-run setup).
- `request_revision`: Human supervisor requests re-analysis with modified operational assumptions.
