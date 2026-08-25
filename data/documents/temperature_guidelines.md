# Engineering Thermal Guidelines & Spindle Tolerance Specifications

## 1. Thermodynamic Context in Machining
Thermal expansion in machine tool spindles directly degrades part geometric tolerances and accelerates bearing degradation. Overheating in angular contact ceramic hybrid or steel ball bearings causes lubricant thermal breakdown, viscosity thinning, and ultimate bearing seizure.

## 2. Thermal Categorization Zones
- **Zone 1: Normal Thermal Steady-State (20.0°C to 68.0°C)**
  - Normal running temperature for heavy roughing and high-speed finishing operations.
  - Heat generation is balanced by active chiller dissipation.
  - No corrective action required.
- **Zone 2: Advisory Thermal Drift / Edge (68.1°C to 82.0°C)**
  - Indication of sub-optimal heat transfer, high ambient factory heat, excessive cutting feed, or initial bearing grease degradation.
  - Recommended actions: Operator advisory to check chiller coolant delta-T; verify spindle fan functionality; evaluate tool wear.
  - Human review: Recommended if trend continues for more than 15 consecutive minutes.
- **Zone 3: Critical Thermal Threshold / High Risk (> 82.0°C)**
  - Immediate risk of thermal runaway, permanent spindle runout, or bearing galling.
  - Advisory protocol: Flag system state as `HIGH` risk immediately.
  - Escalate directly to shop floor engineer for immediate inspection of spindle cooling jacket and toolholder clamping force.
  - Decision-support prototype constraint: Output must explicitly state that physical inspection by certified personnel is required.

## 3. Interaction of Temperature with Speed and Pressure
- Operating above 8,000 RPM at temperatures above 72.0°C accelerates lubricant breakdown by 400%.
- If temperature is high (> 75.0°C) while hydraulic pressure is low (< 4.2 bar), check central lubrication pump manifold.
