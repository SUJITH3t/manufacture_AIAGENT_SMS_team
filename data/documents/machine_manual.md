# Industrial Machine Specification Manual (Model: CNC-Mill-V4 / Lathe-Pro-X)

## 1. Equipment Overview
The CNC-Mill-V4 and Lathe-Pro-X series are precision 5-axis computer numerical control (CNC) machining centers and turning centers designed for aerospace alloy and automotive parts fabrication.

## 2. Standard Operating Parameters
- **Nominal Spindle Speed**: 1,200 to 8,500 RPM (Continuous Duty)
- **Maximum Spindle Speed**: 12,000 RPM (Intermittent Duty, max 15 minutes)
- **Spindle Bearing Temperature (Normal)**: 35.0°C to 68.0°C
- **Spindle Bearing Temperature (Warning - Edge)**: 68.1°C to 82.0°C
- **Spindle Bearing Temperature (Critical - High Risk)**: > 82.0°C
- **Hydraulic Line Pressure (Normal)**: 4.5 bar to 6.5 bar
- **Hydraulic Line Pressure (Warning - Edge)**: 6.6 bar to 7.8 bar OR 3.8 bar to 4.4 bar
- **Hydraulic Line Pressure (Critical - High Risk)**: > 7.8 bar OR < 3.8 bar
- **Ambient Factory Humidity (Normal)**: 30.0% to 65.0% RH
- **Vibration Velocity RMS (Normal)**: 0.2 mm/s to 1.8 mm/s
- **Vibration Velocity RMS (Warning - Edge)**: 1.9 mm/s to 3.8 mm/s
- **Vibration Velocity RMS (Critical - High Risk)**: > 3.8 mm/s

## 3. Coolant and Lubrication Subsystems
- Flood coolant system requires minimal flow rate of 18 L/min at 2.5 bar delivery pressure.
- Micro-mist spindle lubrication cycle runs every 120 seconds during active toolpath execution.
- If spindle temperature rises above 75.0°C while coolant flow is confirmed, inspect bearing preload and chiller heat-exchanger core for fouling.

## 4. Machine Status Codes
- `STATUS_RUNNING`: Normal closed-loop execution.
- `STATUS_IDLE`: Ready state, spindle stationary, hydraulics pressurized.
- `STATUS_WARN_TELEMETRY`: Edge conditions detected; engineering inspection advised.
- `STATUS_ELEVATED_RISK`: Operational metrics breaching nominal bounds; requires human review.
- `STATUS_SENSOR_FAULT`: Missing or non-physical telemetry readings detected.

## 5. Non-Actuation Operational Boundaries
This manual is referenced exclusively by decision-support systems and operators. Automated systems must never issue direct servo cut-offs, spindle brake overrides, or power drops. Any advisory must be verified by a certified shop-floor technician.
