# SOURCE CHANGE BOUNDARY

## File-Impact Matrix

This document defines the strict classification of all repository files for future pre-GAP19 implementation work. No file may be modified unless explicitly authorized in this matrix.

---

## Detailed File Classification Matrix

| File Path | Current Role | Proposed Change | Why Necessary | Dependencies | Tests Required | Governance / GAP19 Dependency | Proposed Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `system/schemas/state.py` | Defines `StationState` schema | Add optional fields: `critical_demand`, `flexible_demand`, `minimum_viable_critical_vector`. | Enable critical/flexible load representation without breaking existing code. | None | Schema validation tests | Pre-GAP19 | `MUST_MODIFY` |
| `system/schemas/forecast.py` | Defines `ForecastBundle` schema | Add optional fields: `critical_demand_forecast`, `flexible_demand_forecast`. | Propagate forecasted critical/flexible demand vectors. | `state.py` | Forecast schema tests | Pre-GAP19 | `MUST_MODIFY` |
| `system/schemas/dispatch.py` | Defines `DispatchPlan` schema | Add optional fields: `critical_load_served`, `flexible_load_served`, `alpha_critical`, `curtailment`. | Record Option D dispatch decisions and proportionality factor $\alpha(t)$. | `state.py` | Dispatch schema tests | Pre-GAP19 | `MUST_MODIFY` |
| `system/runtime/runner.py` | Controls execution pipeline loop | Import ECD, compute `OperatingMode`, invoke `OptionDPolicyLayer`, pass `ModeConstraintSet` to optimizer. | Connect isolated ECD logic to system runtime execution loop. | `ecd.py`, schemas | Runner integration tests | Pre-GAP19 | `MUST_MODIFY` |
| `system/optimization/implementations/milp.py` | SciPy HiGHS MILP formulation | Implement proposed pre-GAP19 Option-D 21-variable constraint formulation. | Enforce D4 proportional allocation and D6 excess charging mathematically in scalar solver. | `schemas` | MILP unit tests (Gates 4-5) | Proposed Pre-GAP19 Formulation | `MAY_MODIFY` |
| `system/simulation/simulator.py` | Digital Twin environment simulation | Add closed-loop fuel mass-balance tracking if multi-step synthetic fuel tracking is authorized. | Static source audit proves `simulator.py` currently lacks fuel level tracking (`SIMULATOR_FUEL_STATE_SUPPORT = NOT_ESTABLISHED`). | `runner.py` | Simulation tests | Engineeringly Required But Not Yet Authorized | `MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION` |
| `system/control/ecd.py` | Energy Crisis Detector core | **NONE**. Logic is frozen, verified, and reusable as-is. | Core ECD logic is fully verified and must not be altered. | None | ECD unit tests (Gate 2) | None | `MUST_NOT_MODIFY` |
| `system/forecasting/` | Model training & forecasting | **NONE**. Isolated by Forecasting Firewall. | Prevent future actual data leakage and preserve training integrity. | None | Static code audit | Independent | `MUST_NOT_MODIFY` |
| `system/data/` | Synthetic fixture JSON files | **NONE**. Isolated by Synthetic Production Firewall. | Fixture values are frozen benchmarks and must not be mutated. | None | Fixture hash audit | Independent | `MUST_NOT_MODIFY` |
| Production Config & Keys | Station configuration & crypto keys | **NONE**. Production security open. | Synthetic implementation uses mock fixture config; no production keys. | Security sign-off | None | Production Security | `MUST_NOT_MODIFY` |

---

## Summary Counts

- **`MUST_MODIFY`**: 4 files (`system/schemas/state.py`, `system/schemas/forecast.py`, `system/schemas/dispatch.py`, `system/runtime/runner.py`).
- **`MAY_MODIFY`**: 1 file (`system/optimization/implementations/milp.py` — Proposed pre-GAP19 Option-D formulation).
- **`MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION`**: 1 file (`system/simulation/simulator.py` — Reclassified from MUST_MODIFY following static source evidence audit).
- **`MUST_NOT_MODIFY`**: All other repository files (`system/control/ecd.py`, `system/forecasting/*`, `system/data/*`, production configurations).
