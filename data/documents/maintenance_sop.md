# Standard Operating Procedure: Preventive and Corrective Maintenance (SOP-MNT-2026)

## 1. Purpose and Scope
This Standard Operating Procedure (SOP) defines the protocol for monitoring, diagnosing, and inspecting industrial machining assets. It establishes clear guidelines for human maintenance engineers evaluating AI decision-support advisories.

## 2. Maintenance Tiers and Frequency
- **Daily Operator Check (Tier 1)**:
  - Visual inspection of hydraulic lines for weeping or pressure drops below 4.5 bar.
  - Spindle temperature log verification (must remain < 68.0°C).
  - Coolant reservoir level check and chip conveyor clearance.
- **Weekly Technical Inspection (Tier 2)**:
  - Vibration spectrum analysis on spindle housing and axis drive motors (ISO 10816 compliant).
  - Hydraulic filter differential pressure gauge inspection.
  - Waylube oil distribution manifold pressure verification.
- **Monthly Maintenance Overhaul (Tier 3)**:
  - Bearing grease repack or automatic lubrication cartridge replacement.
  - Thermal imaging of main electrical cabinet and drive amplifiers.
  - Laser interferometer axis backlash and pitch error calibration.

## 3. Telemetry Anomaly Resolution Protocols
### 3.1 Elevated Spindle Temperature (> 68.0°C)
1. Verify chiller fluid level and verify supply line thermocouple calibration.
2. Check tool load monitor percentage: if cutting force is > 115% of rated load, check for insert wear or chipping.
3. Review machine vibration: if vibration velocity exceeds 2.5 mm/s concurrently with thermal rise, bearing raceway degradation is probable.
4. Escalate to Senior Mechanical Maintenance Specialist for physical borehole endoscope inspection.

### 3.2 High Vibration Anomaly (> 3.8 mm/s)
1. Halt planned cycle upon current part completion (Operator intervention only).
2. Inspect toolholder taper (BT40/HSK63) for fretting corrosion or foreign debris.
3. Conduct bump test / coast-down test to determine if resonance coincides with operational RPM.
4. Check motor coupling elastomeric spider insert for mechanical fatigue or tears.

### 3.3 Hydraulic Pressure Loss (< 3.8 bar) or Spike (> 7.8 bar)
1. Inspect pressure relief valve proportional solenoid.
2. Check accumulator nitrogen pre-charge pressure.
3. If rapid fluctuating pulses occur, inspect pump inlet suction line for cavitation or air ingress.

## 4. Human-in-the-Loop Signoff Procedure
Every recommendation flagged by the decision-support agent as `HIGH` risk or `EDGE` requiring physical intervention must receive sign-off by a Level 2 Maintenance Technician before work order dispatch.
