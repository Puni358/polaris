# Minimal File Delta Specification

## Precise File Modification Table

| File Path | Action Type | Reason & Purpose | Mandatory? | Protected File? |
| :--- | :--- | :--- | :--- | :--- |
| `system/control/router.py` | **NEW FILE** | Implements `EMSControlRouter` state routing logic | YES | No (New File) |
| `system/optimization/implementations/option_d.py` | **NEW FILE** | Implements `OptionDFallbackSolver` DEC-004 logic | YES | No (New File) |
| `system/runtime/runner.py` | **MODIFY** | Calls router between ForecastEngine & optimization | YES | YES (Target Mod) |
| `system/control/ecd.py` | **UNTOUCHED** | Core ECD evaluator functions remain untouched | NO | **PROTECTED SOURCE** |
| `system/optimization/implementations/gap19_highs_native.py` | **UNTOUCHED** | Option B native HiGHS solver untouched | NO | **PROTECTED SOURCE** |
| `system/optimization/implementations/milp.py` | **UNTOUCHED** | Base MILP optimizer untouched | NO | **PROTECTED SOURCE** |
| `system/simulation/simulator.py` | **UNTOUCHED** | Digital Twin simulator untouched | NO | **PROTECTED SOURCE** |
| `system/schemas/forecast_bundle.py` | **UNTOUCHED** | ForecastBundle schema untouched | NO | **PROTECTED SOURCE** |
| `system/schemas/station_state.py` | **UNTOUCHED** | StationState schema untouched | NO | **PROTECTED SOURCE** |
| `system/schemas/dispatch_plan.py` | **UNTOUCHED** | DispatchPlan schema untouched | NO | **PROTECTED SOURCE** |

---

## Summary Totals
- `MINIMUM_NEW_FILES` = **2**
- `MINIMUM_MODIFIED_FILES` = **1**
- `PROTECTED_FILES_REQUIRING_MODIFICATION` = **0** (Only `runner.py` target integration)
