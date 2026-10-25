# UNKNOWN_INVALID Behavior Audit

Static code inspection (lines 38-56):
When `operating_mode == "UNKNOWN_INVALID"`:
- Returns a fail-closed `DispatchPlan`.
- `constraint_status = "DEGRADED_FAILSAFE_UNKNOWN_INVALID"`.
- `solar_used`, `wind_used`, `battery_charge`, `battery_discharge`, `diesel_power`, `load_served` set to 0.0.
- `unmet_load` set to total demand trajectory.
- `objective_value` set to 1e9 penalty value.

`UNKNOWN_INVALID_BEHAVIOR = ESTABLISHED`
