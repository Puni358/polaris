# Next-Gate Test Specification (`NEXT_GATE_TEST_SPECIFICATION.md`)

**GATE IDENTIFICATION CONTEXT**: POLARIS EMS GAP19 — Next-Gate Identification  
**VERDICT**: `PASS`

---

## Controlled 24-Cycle MPC Integration Experiment Specification

> **NOTE**: This test specification defines the exact minimal experiment to be executed ONLY when explicit human authorization is granted for the next phase.

---

## 1. Experiment Overview

- **Test ID**: `POLARIS_EMS_GAP19_CONTROLLED_24_CYCLE_MPC_TEST`
- **Execution Mode**: Offline Closed-Loop Receding-Horizon MPC Simulation
- **Duration**: 24 Timesteps ($24 \text{ hours}$, 1 full diurnal cycle)
- **Origin Timestamp**: `2024-01-01T20:00:00Z`
- **End Timestamp**: `2024-01-02T20:00:00Z`
- **Scenario Fixture**: [`system/data/scenarios/demo_scenario.json`](file:///home/punith-bs/01polaris%20%28Copy%29/system/data/scenarios/demo_scenario.json)

---

## 2. Configuration & Parameter Bindings

```json
{
  "scenario_filename": "demo_scenario.json",
  "optimizer_type": "highs_native",
  "forecast_engine_type": "baseline",
  "steps_to_run": 24,
  "initial_state": {
    "timestamp": "2024-01-01T20:00:00Z",
    "battery_soc_pct": 80.0,
    "battery_capacity_wh": 200000.0,
    "diesel_running": false,
    "diesel_hours_running": 0.0
  },
  "governed_parameters": {
    "t_required_hours": 6,
    "terminal_target_wh": 100000.0,
    "min_soc_pct": 20.0,
    "max_soc_pct": 95.0,
    "charge_efficiency": 0.92,
    "discharge_efficiency": 0.92
  }
}
```

---

## 3. Execution Pipeline Step Sequence

For each step $k \in [0, 23]$:
1. `current_state` observed at origin timestamp $t_k$.
2. `bundle = forecast_engine.predict(current_state, runtime_context)` (24h lookahead).
3. `plan = optimizer.optimize(bundle, current_state, configs)` (HiGHS native lexicographic optimization).
4. `next_actual = data_provider.get_future_ground_truth(k, horizon_hours=24)[0]`.
5. `current_state = simulator.step(current_state, plan, next_actual)` (committed first action $k=0$ only applied).
6. Cycle result JSON written to artifact directory `CYCLE_{kk}_RESULT.json`.

---

## 4. Verification Protocol

1. **State Continuity Verification**: Check that `CYCLE_{kk+1}_RESULT.json` input origin state matches `CYCLE_{kk}_RESULT.json` output state exactly.
2. **Diurnal Solar Verification**: Verify smooth solar dispatch transition during daylight hours ($10:00 \dots 18:00$ UTC) without battery boundary violation or diesel over-generation.
3. **Objective Hierarchy Verification**: Verify $J1 = 0.0$ and $J2 = 0.0$ across all 24 cycles.
4. **Source Integrity Verification**: Compute SHA-256 hashes of all 7 protected source/schema files and verify 100% hash equality.
