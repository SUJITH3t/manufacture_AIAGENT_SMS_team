# Vibration Severity & Diagnostic Guidelines (ISO 10816-3 Industrial Standard)

## 1. Scope & Vibration Measurement Principles
Vibration telemetry is captured using triaxial piezoelectric accelerometers mounted directly to the spindle nose casting and main drive gearbox. Velocity RMS (Root Mean Square) in mm/s over a 10 Hz to 1,000 Hz frequency band provides early detection of unbalance, misalignment, looseness, and bearing raceway spalling.

## 2. Vibration Severity Classification (Rigid Foundation Machining Tools)
- **Class A / Green (0.0 to 1.8 mm/s RMS) - NORMAL**:
  - Vibration of newly commissioned or well-maintained machines.
  - Smooth cutting operation with pristine surface finish quality (Ra < 0.8 µm).
- **Class B / Yellow (1.81 to 3.8 mm/s RMS) - EDGE / WARNING**:
  - Machines within this zone are considered acceptable for unrestricted long-term operation, but warrant scheduled inspection.
  - Common causes: Minor toolholder imbalance, slight cutter wear, uneven coolant flutes, slight belt tension deflection.
  - Action: Log telemetry baseline; monitor trends over the current production batch.
- **Class C & D / Red (> 3.8 mm/s RMS) - HIGH RISK / CRITICAL**:
  - Vibration causes significant damage to machine spindle bearings, ball screws, and workpiece dimensional stability.
  - Risk of catastrophic tool fracture, spindle seizure, or operator safety hazards from thrown inserts.
  - Action: Prompt human review escalation (`HIGH` Risk classification). Immediate recommendation for operator tool and spindle check.

## 3. High-Frequency Peak Acceleration (Crest Factor)
- In addition to Velocity RMS, crest factors > 5.0 at high RPM indicate localized ball/roller impact faults on outer bearing rings.
- If vibration > 3.8 mm/s coincides with temperature > 80.0°C, bearing destruction is imminent within operational hours.
