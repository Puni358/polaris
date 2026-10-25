# DispatchPlan Dataflow Audit

Option B returns standard `DispatchPlan` (Version 1.0.0). The runner pipeline validates:
- `plan.constraint_status`
- `plan.solar_used`, `plan.wind_used`, `plan.battery_charge`, `plan.battery_discharge`, `plan.diesel_power` for simulator stepping.

```text
DISPATCHPLAN_DATAFLOW = PASS
```
