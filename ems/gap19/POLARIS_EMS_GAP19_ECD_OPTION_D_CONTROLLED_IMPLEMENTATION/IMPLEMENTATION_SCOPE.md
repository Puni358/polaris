# POLARIS EMS GAP19 — Authorized Implementation Scope Report

## Scope Summary

The implementation was performed under strict authorization constraints.

### 1. Authorized Components Implemented
- **Rolling Diesel Fuel Physical State**:
  - Initialized once from `configs["diesel"]["initial_fuel_l"]`.
  - Propagated dynamically in `DigitalTwinSimulator.step()` for committed first action $k=0$ (`DispatchPlan.diesel_power[0]`) ONLY.
  - Calculated using physical model: `required_fuel = (base_fuel_lph if diesel_running else 0.0) + marginal_fuel_lpwh * p_diesel`.
  - Non-negative physical clipping `next_fuel = max(0.0, available_fuel - required_fuel)` with explicit observability.
  - Fuel state passed to `ECD.evaluate(...)`.

- **Minimal EMS Control Router**:
  - Pure policy routing in `EMSControlRouter`.
  - Maps `OperatingMode.NORMAL` → Option B (`GAP19HighsNativeOptimizer`).
  - Maps `OperatingMode.EMERGENCY` → Option D (`OptionDFallbackSolver`).
  - Classifies `OperatingMode.UNKNOWN_INVALID` and blocks Option B/Option D selection (`UNKNOWN_INVALID_RUNNER_OPERATIONAL_ACTION = NOT_IMPLEMENTED`).

- **Option D Fallback Solver (Sealed D1–D6 Governance)**:
  - `OptionDFallbackSolver` satisfies sealed DEC-004 emergency rules.
  - Protected critical load served first; non-critical load shed.
  - Direct renewable generation used first.
  - Diesel generator support when fuel available.
  - Battery discharge/charge respecting preserved/limiting resource without prohibiting battery use.
  - Proportional load allocation $\alpha = P_{\text{crit\_avail}} / \sum P_{i,\min}$ when power is insufficient.
  - Excess diesel charges battery ONLY when diesel is running for load. Diesel NEVER started solely to charge battery.
  - `OPTION_D_OBJECTIVE_VALUE = NOT_APPLICABLE / ENGINEERING_INTERFACE_REQUIRED`.

- **Unit & Isolated Component Test Suite**:
  - Authorized unit tests (`tests/test_gap19_ecd_option_d.py`) covering items A through R (18/18 passed).
  - Isolated synthetic component tests (`tests/test_isolated_components.py`) covering router, solver, and simulator interfaces (4/4 passed).

### 2. Unauthorized Items strictly Excluded
- Zero changes to `system/control/ecd.py`.
- Zero changes to `system/optimization/implementations/gap19_highs_native.py`.
- Zero changes to `system/optimization/implementations/milp.py`.
- Zero alterations to J1/J2/J3/J4 objective functions or priorities.
- Zero implementation of emergency return policy.
- Zero execution of full 24h EMS, multi-cycle MPC, or real-station data.
