# System Limitations and Operational Boundaries

**ManufacturingAgent: Non-Actuation & Decision-Support Constraints**

---

## 1. Non-Actuation & Safety Boundaries

1. **Advisory Role Only**: ManufacturingAgent is strictly a decision-support prototype. It does not interface directly with industrial fieldbuses (e.g. Profinet, EtherCAT, Modbus TCP) and cannot issue control commands to PLCs, CNC controllers, or servo drives.
2. **No Emergency Stop (E-Stop) Authority**: Hardwired physical safety circuits, safety relays, and mechanical interlocks take unconditional precedence over any software advisory.
3. **No Replacement for Certified Engineers**: The system is designed to augment human situational awareness, not replace licensed mechanical, electrical, or safety engineers.

---

## 2. Technical and Algorithmic Limitations

1. **Simulated Telemetry Ingestion**: The prototype uses JSON-based machine profiles and HTTP REST payloads rather than high-frequency streaming OPC UA or MQTT industrial telemetry brokers.
2. **Context Window Limits**: In extremely dense multi-fault scenarios, retrieved RAG chunks are truncated to top-k relevance to maintain latency boundaries.
3. **Sensor Calibration Assumptions**: The risk scoring engine assumes that physical sensors are calibrated. Degraded thermocouples or drifting accelerometers require human engineer verification.
4. **Transient Dynamic Modeling**: Current evaluation focuses on steady-state and instantaneous threshold breaching; time-series frequency transforms (e.g. FFT waterfall plots or wavelet analysis) are delegated to external diagnostic toolchains.
