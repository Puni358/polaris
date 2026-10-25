# DispatchPlan Schema Audit

Option B returns standard `DispatchPlan` (Version 1.0.0) with:
- `timestamps`, `solar_used`, `wind_used`, `battery_charge`, `battery_discharge`, `battery_soc`, `diesel_power`, `load_served`, `flexible_load_schedule`, `renewable_curtailment`, `unmet_load`, `objective_value`, `constraint_status`, `energy_balance_errors`.

All fields conform strictly to `system/schemas/dispatch_plan.py`.

```text
DISPATCHPLAN_COMPATIBILITY = ESTABLISHED
SCHEMA_EXTENSION_REQUIRED = NONE
```
