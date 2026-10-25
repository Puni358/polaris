# POLARIS — Forecast vs Optimizer Failure Boundaries

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Boundary & Constraint Integrity Verification

Every diagnostic counterfactual run (Experiments A, B, C, D) strictly preserved all physical, operational, and safety constraints:

```yaml
CONSTRAINT_INTEGRITY:
  SOC_BOUNDS: [20.0%, 100.0%] # Preserved
  MAX_CHARGE_POWER: 50.0 kW   # Preserved
  MAX_DISCHARGE_POWER: 50.0 kW # Preserved
  ENERGY_CONSERVATION: 0.00 kWh ERROR # Preserved
  SURVIVABILITY_GOVERNANCE: 6 HOURS @ 6 KW # Preserved
  TELEMETRY_GOVERNANCE: G1.3-E # Preserved
```

---

## 2. Identified Diagnostic Failure Boundaries

### Boundary 1: Forced Cycling Without Physical Storage Capacity (< 45 kWh)
- **Condition**: Attempting to force 50 EFC on a battery system smaller than 45 kWh.
- **Result**: Solver infeasibility due to inability to satisfy 6h critical-load survivability.

### Boundary 2: Arbitrary Schedule Insertion vs MILP Optimization
- **Condition**: Hardcoding a rigid hourly discharge schedule rather than letting the MILP optimizer select timing.
- **Result**: Rigid schedule discharges battery during renewable surplus or low-load hours, increasing generator runtime and fuel burn by up to 4,200 L.
- **Governance Finding**: Diagnostic ~50 EFC must be implemented as a research objective/constraint within MILP, never as a hardcoded static schedule.

### Boundary 3: Over-Cycling Beyond Economic Value (> 120 EFC)
- **Condition**: Incentivizing battery cycling beyond net-load deficit opportunities (> 120 EFC/yr).
- **Result**: Battery charges from diesel generation to force cycling, causing net fuel penalty (+3,500 L).
