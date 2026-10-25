# Schema Impact & Additive Requirements Audit

## Rule: NO REPURPOSING OF EXISTING SCHEMA FIELDS

Every schema modification must be strictly additive and backward-compatible.

## Audit of Target Schemas

### 1. `StationState` (`system/schemas/station_state.py`)
- **Current Fields**: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_solar_irradiance`, `last_observed_demand`, `last_observed_wind_generation`, `operating_mode="NORMAL"`, `ebr_target_wh_override`, `terminal_target_wh_override`.
- **Additive Extension Required**: Optional field `emergency_assessment_json: Optional[str] = None` to persist ECD output across timesteps.
- **Backward Compatibility**: Fully preserved (`operating_mode` already exists with default `"NORMAL"`).

### 2. `DispatchPlan` (`system/schemas/dispatch_plan.py`)
- **Current Fields**: 24h arrays for solar, wind, battery charge/discharge, SOC, diesel power, load served, flexible load, curtailment, unmet load; `objective_value`, `constraint_status`, `j1..j4_objective`, `reserve_shortfall`.
- **Additive Extension Required**: Optional fields `operating_mode: Optional[str] = None`, `option_d_active: Optional[bool] = None`.
- **Backward Compatibility**: Fully preserved via optional keyword arguments in `__init__` and `from_dict`.

### 3. `ForecastBundle` (`system/schemas/forecast_bundle.py`)
- **Current Fields**: 24h forecast vectors for solar, wind, demand, temperature.
- **Additive Extension Required**: None required for synthetic integration.

---

## Verdict
`SCHEMA_IMPACT = ADDITIVE_EXTENSION_REQUIRED`. All proposed extensions are strictly additive and 100% backward-compatible.
