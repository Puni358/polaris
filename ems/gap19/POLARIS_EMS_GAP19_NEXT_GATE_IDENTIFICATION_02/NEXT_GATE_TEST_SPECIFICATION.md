# Next-Gate Test Specification (`NEXT_GATE_TEST_SPECIFICATION.md`)

**GATE IDENTIFICATION CONTEXT**: POLARIS EMS GAP19 — Post-24H Baseline Next-Gate Identification  
**VERDICT**: `PASS`

---

## Controlled Multi-Scenario Stress Experiment Specification

> **NOTE**: This test specification defines the exact minimal experiment to be executed ONLY when explicit human authorization is granted for the next phase.

---

## 1. Experiment Overview

- **Test ID**: `POLARIS_EMS_GAP19_CONTROLLED_MULTI_SCENARIO_STRESS_TEST`
- **Execution Mode**: Offline Closed-Loop Receding-Horizon MPC Simulation Suite
- **Scenarios to Execute**:
  1. `normal_demo` (`demo_scenario.json` — 24 steps)
  2. `renewable_stress` (`renewable_stress_scenario.json` — 24 steps)
  3. `demand_stress` (`demand_stress_scenario.json` — 24 steps)
  4. `battery_stress` (`battery_stress_scenario.json` — 24 steps)
- **Total MPC Cycles**: 96 Steps (4 runs x 24 hours)
- **Harness Method**: [`PolarisLocalRunner.run_multi_scenario_suite(steps_to_run=24)`](file:///home/punith-bs/01polaris%20%28Copy%29/system/runtime/runner.py#L348-L380)

---

## 2. Configuration & Parameter Bindings

```json
{
  "optimizer_type": "highs_native",
  "forecast_engine_type": "baseline",
  "steps_to_run": 24,
  "scenarios": [
    "demo_scenario.json",
    "renewable_stress_scenario.json",
    "demand_stress_scenario.json",
    "battery_stress_scenario.json"
  ],
  "governed_parameters": {
    "t_required_hours": 6,
    "terminal_target_wh": 100000.0,
    "charge_efficiency": 0.92,
    "discharge_efficiency": 0.92
  }
}
```

---

## 3. Verification Protocol Across All 4 Scenarios

1. **Solver Feasibility**: `constraint_status == "OPTIMAL"` across all 96 MPC cycles. Zero fallbacks, zero retries.
2. **Reserve Maintenance**: $J2 = 0.0$ Wh (zero EBR or terminal reserve shortfall) across all 96 cycles.
3. **Unmet Load**: $J1 = 0.0$ Wh (zero unmet critical/total load) across all 96 cycles.
4. **Physical Boundaries**: Battery SOC remains within configured operational limits for each scenario.
5. **Source Integrity Verification**: Compute SHA-256 hashes of all protected source and schema files and verify 100% hash equality.
