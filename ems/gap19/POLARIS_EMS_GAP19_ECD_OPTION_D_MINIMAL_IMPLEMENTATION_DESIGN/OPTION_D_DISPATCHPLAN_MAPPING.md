# Option D to DispatchPlan Direct Mapping

## Minimality Verification: Zero Schema Delta for Option D Dispatch

Option D dispatch output maps **DIRECTLY** to the existing `DispatchPlan` schema (`system/schemas/dispatch_plan.py`):

| Dispatch Vector | Option D Source Value | Existing DispatchPlan Field | Status |
| :--- | :--- | :--- | :--- |
| Solar Power Used | Calculated solar dispatch $P_{\text{pv,used}}$ | `DispatchPlan.solar_used` | `DIRECTLY_REUSABLE` |
| Wind Power Used | Calculated wind dispatch $P_{\text{wind,used}}$ | `DispatchPlan.wind_used` | `DIRECTLY_REUSABLE` |
| Battery Charge Power | Calculated diesel excess charge $P_{\text{chg}}$ | `DispatchPlan.battery_charge` | `DIRECTLY_REUSABLE` |
| Battery Discharge Power | Calculated emergency discharge $P_{\text{dis}}$ | `DispatchPlan.battery_discharge` | `DIRECTLY_REUSABLE` |
| Battery State of Charge | Projected SOC profile | `DispatchPlan.battery_soc` | `DIRECTLY_REUSABLE` |
| Diesel Generator Power | Calculated diesel output $P_{\text{diesel}}$ | `DispatchPlan.diesel_power` | `DIRECTLY_REUSABLE` |
| Load Served | Served protected critical load | `DispatchPlan.load_served` | `DIRECTLY_REUSABLE` |
| Unmet Load | Unserved protected critical load | `DispatchPlan.unmet_load` | `DIRECTLY_REUSABLE` |
| Objective Value | `0.0` (Heuristic fallback) | `DispatchPlan.objective_value` | `DIRECTLY_REUSABLE` |
| Constraint Status | `"OPTION_D_FALLBACK"` | `DispatchPlan.constraint_status` | `DIRECTLY_REUSABLE` |

---

## Verdict
`DISPATCH_PLAN_EXTENSION = NONE`. Existing `DispatchPlan` schema carries Option D dispatch outputs cleanly.
