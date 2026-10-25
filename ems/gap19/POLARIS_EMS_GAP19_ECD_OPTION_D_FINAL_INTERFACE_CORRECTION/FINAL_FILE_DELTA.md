# Final Minimal File Delta Specification

## Precise Source File Delta Table

| File Path | Action | Purpose | Protected File? |
| :--- | :--- | :--- | :--- |
| `system/control/router.py` | **NEW FILE** | Implements `EMSControlRouter` policy router | No (New File) |
| `system/optimization/implementations/option_d.py` | **NEW FILE** | Implements `OptionDFallbackSolver` DEC-004 logic | No (New File) |
| `system/runtime/runner.py` | **MODIFY** | Integrates router call between forecasting & solver | YES (Target Mod) |
| `system/control/ecd.py` | **UNTOUCHED** | Core ECD evaluator functions remain untouched | **PROTECTED SOURCE** |
| `system/optimization/implementations/gap19_highs_native.py` | **UNTOUCHED** | Option B native HiGHS solver untouched | **PROTECTED SOURCE** |
| `system/optimization/implementations/milp.py` | **UNTOUCHED** | Base MILP optimizer untouched | **PROTECTED SOURCE** |
| `system/simulation/simulator.py` | **UNTOUCHED** | Digital Twin simulator untouched | **PROTECTED SOURCE** |
| `system/schemas/forecast_bundle.py` | **UNTOUCHED** | ForecastBundle schema untouched | **PROTECTED SOURCE** |
| `system/schemas/station_state.py` | **UNTOUCHED** | StationState schema untouched | **PROTECTED SOURCE** |
| `system/schemas/dispatch_plan.py` | **UNTOUCHED** | DispatchPlan schema untouched | **PROTECTED SOURCE** |

---

## Metric Totals
- `MINIMUM_NEW_SOURCE_FILES` = **2**
- `MINIMUM_MODIFIED_SOURCE_FILES` = **1**
- `SCHEMA_MODIFICATIONS` = **ZERO**
- `PROTECTED_SOLVER_MODIFICATIONS` = **ZERO**
