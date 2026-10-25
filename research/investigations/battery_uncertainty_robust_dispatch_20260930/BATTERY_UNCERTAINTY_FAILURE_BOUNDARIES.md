# POLARIS — Battery Uncertainty Failure Boundaries & Boundary Stress Analysis

> **RESEARCH SCENARIO / SYNTHETIC UNCERTAINTY ENVELOPE / NOT TARGET-HARDWARE EVIDENCE**

## 1. Boundary Audit Overview

This document defines the physical, operational, and mathematical failure boundaries identified during the battery-uncertainty campaign.

---

## 2. Identified Failure Boundaries

### Boundary 1: Minimum Usable Capacity for Survivability (< 45 kWh)
- **Condition**: `Capacity_usable < 45.0 kWh` (e.g., nominal capacity < 56 kWh at 80% DoD).
- **Observed Effect**: MILP solver returns `INFEASIBLE` when evaluating 6-hour critical-load survivability governance ($6.0 \text{ kW} \times 6 \text{ h} = 36.0 \text{ kWh}$ net requirement + 20% min SOC buffer = 45.0 kWh minimum required battery energy).
- **Safety Implication**: Severe. Below 45 kWh, battery alone cannot satisfy 6h emergency backup without generator operation.

### Boundary 2: Minimum Power Capability (< 12.0 kW)
- **Condition**: `Power_max < 12.0 kW` (for 200 kWh pack, C-rate < 0.06C).
- **Observed Effect**: Battery cannot ramp fast enough to catch net-load solar/wind variations. Annual curtailment spikes above 72,000 kWh, and diesel fuel rises to 95,890 L.
- **Safety Implication**: Operational performance degradation.

### Boundary 3: Round-Trip Efficiency Floor (< 75.0%)
- **Condition**: `eta_rt < 0.750` (25%+ round-trip loss).
- **Observed Effect**: Cycle losses outweigh diesel displacement benefit; charging battery increases total system energy loss.
- **Safety Implication**: Economic loss.

### Boundary 4: Telemetry Staleness / Invalidity (T1–T5)
- **Condition**: SOC, Power, or Temperature telemetry stale or missing.
- **Observed Effect**: Battery Safety Credit = 0 kW; battery locked out of dispatch.
- **Safety Implication**: System seamlessly falls back to non-battery diesel dispatch with 0 unmet load. Emergency Mode remains `FALSE` because diesel generator satisfies critical load.

---

## 3. Failure Boundary Summary Table

| Boundary Condition | Metric Threshold | Solver Result | System Safety | Diesel Fuel Impact | Action Required |
|---|---|---|---|---|---|
| **Usable Capacity Low** | < 45.0 kWh | **INFEASIBLE** | **FAIL (6h Survivability)** | N/A | Exclude battery from survivability credit |
| **Power Capability Low** | < 12.0 kW | OPTIMAL | PASS | High Fuel (+2,424 L) | Enforce min power rating 15 kW |
| **Efficiency Floor** | < 75.0% | OPTIMAL | PASS | Fuel Penalty | Lock battery from routine cycling |
| **Telemetry Invalid (T1-T5)** | Freshness = FALSE | OPTIMAL | PASS (Diesel Fallback) | Minor Fuel (+1,654 L) | Non-battery fallback dispatch |
