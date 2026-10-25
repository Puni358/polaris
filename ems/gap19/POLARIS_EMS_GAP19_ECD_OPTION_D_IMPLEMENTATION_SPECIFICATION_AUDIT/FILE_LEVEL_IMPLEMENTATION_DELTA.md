# File-Level Implementation Delta Specification

## Minimum Implementation Set

The table below specifies the exact file-level modifications required for future integration implementation:

| File Path | Action Required | Nature of Change | Protected? |
| :--- | :--- | :--- | :--- |
| `system/control/router.py` | **NEW FILE** | Implements `EMSControlRouter` state machine | New Component |
| `system/optimization/implementations/option_d.py` | **NEW FILE** | Implements `OptionDFallbackSolver` heuristic | New Component |
| `system/runtime/runner.py` | **MODIFY** | Integrates router call between forecasting & optimization | Protected (Target Mod) |
| `system/schemas/station_state.py` | **MODIFY** | Adds optional `emergency_assessment_json` attribute | Protected (Additive Mod) |
| `system/schemas/dispatch_plan.py` | **MODIFY** | Adds optional `operating_mode` & `option_d_active` | Protected (Additive Mod) |
| `system/control/ecd.py` | **UNTOUCHED** | Core ECD evaluator functions remain untouched | **PROTECTED SOURCE** |
| `system/optimization/implementations/gap19_highs_native.py` | **UNTOUCHED** | Option B native HiGHS solver remains untouched | **PROTECTED SOURCE** |
| `system/optimization/implementations/milp.py` | **UNTOUCHED** | Base MILP optimizer remains untouched | **PROTECTED SOURCE** |
| `system/simulation/simulator.py` | **UNTOUCHED** | Digital Twin simulator remains untouched | **PROTECTED SOURCE** |
| `system/schemas/forecast_bundle.py` | **UNTOUCHED** | ForecastBundle schema remains untouched | **PROTECTED SOURCE** |
