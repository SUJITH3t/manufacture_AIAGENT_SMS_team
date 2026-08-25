# Hydraulic and Pneumatic Pressure Operating Guidelines

## 1. Subsystem Description
The machine tool utilizes an auxiliary hydraulic power unit (HPU) for tool clamping, pallet exchange, and spindle orient lock, alongside a 6-bar pneumatic air blast network for taper cleaning and linear scale positive air purges.

## 2. Pressure Operating Thresholds
- **Optimal Hydraulic Pressure**: 4.5 to 6.5 bar (Static holding pressure during cycle: 5.5 bar).
- **Edge Pressure Degradation (Low Warning)**: 3.8 to 4.4 bar.
  - Causes: Filter element clogging, slight internal bypass in proportional relief valve, cold hydraulic oil (viscosity > 150 cSt).
  - Protocol: Log event, verify HPU oil temperature (must reach 35°C before full roughing cuts).
- **Critical Low Pressure (< 3.8 bar)**:
  - Critical risk of un-clamped tool pullout during high-torque milling, risking severe mechanical collision.
  - Risk Level: `HIGH`. Mandatory human review escalation.
- **Edge Pressure Surge (High Warning)**: 6.6 to 7.8 bar.
  - Causes: Flow control orifice constriction, faulty pressure transducer, sticking accumulator unloader.
- **Critical Over-Pressure (> 7.8 bar)**:
  - Risk of hydraulic hose rupture, valve manifold seal blowout, and fluid contamination.
  - Risk Level: `HIGH`. Immediate escalation.

## 3. Sensor Fault Telemetry Indicators
- If pressure reports negative values (e.g. < 0.0 bar) or NaN values while speed is > 0 RPM, designate condition as `STATUS_SENSOR_FAULT` and initiate sensor diagnostics.
