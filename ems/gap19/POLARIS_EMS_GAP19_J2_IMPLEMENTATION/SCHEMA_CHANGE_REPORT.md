# Additive Schema Changes Implementation Report

## 1. Governance Schema Principles Verification

- **Rule 1**: Zero existing schema fields in version `1.0.0` were deleted, renamed, or structurally altered.
- **Rule 2**: `demand.point` in `ForecastBundle` continues to represent TOTAL station demand. It was NOT repurposed or overwritten to mean protected critical demand.
- **Rule 3**: 100% backward compatibility is preserved. All existing pipelines calling `ForecastBundle`, `StationState`, or `DispatchPlan` continue to execute without error.

---

## 2. Documented Schema Modifications

### 2.1 `ForecastBundle` (`system/schemas/forecast_bundle.py`)
- **Old Fields**: `schema_version`, `origin_timestamp`, `horizon_hours`, `timestamps`, `solar_irradiance`, `solar_generation`, `wind_generation`, `demand`, `metadata`.
- **New Additive Field**: `demand_critical: Optional[TimeseriesForecast] = None`
- **Optional / Required Status**: `OPTIONAL` (defaults to `None`).
- **Validation Behavior**: If provided, checks `unit == "W"` and validates non-negativity and upper bound: $0 \le P_{\text{crit}}[t] \le P_{\text{demand}}[t]$. Raises `ValueError` if violated.
- **Compatibility Behavior**: Existing callers omitting `demand_critical` produce valid `ForecastBundle` objects without modification.

### 2.2 `StationState` (`system/schemas/station_state.py`)
- **Old Fields**: `timestamp`, `battery_soc_pct`, `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_solar_irradiance`, `last_observed_demand`, `last_observed_wind_generation`.
- **New Additive Fields**:
  - `operating_mode: str = "NORMAL"` (Optional, default `"NORMAL"`)
  - `ebr_target_wh_override: Optional[float] = None` (Optional, default `None`)
  - `terminal_target_wh_override: Optional[float] = None` (Optional, default `None`)
- **Compatibility Behavior**: Existing callers omitting new fields instantiate `StationState` with standard default `"NORMAL"` mode.

### 2.3 `DispatchPlan` (`system/schemas/dispatch_plan.py`)
- **Old Fields**: `schema_version`, `timestamps`, `solar_used`, `wind_used`, `battery_charge`, `battery_discharge`, `battery_soc`, `diesel_power`, `load_served`, `flexible_load_schedule`, `renewable_curtailment`, `unmet_load`, `objective_value`, `constraint_status`, `energy_balance_errors`.
- **New Additive Fields**:
  - `j1_objective: Optional[float] = None` (Critical load deficit Wh)
  - `j2_objective: Optional[float] = None` (Governed reserve shortfall Wh)
  - `j3_objective: Optional[float] = None` (Diesel fuel Liters)
  - `j4_objective: Optional[float] = None` (Renewable curtailment Wh)
  - `reserve_shortfall: Optional[List[float]] = None` (24h array of $s_{J2}[t]$)
- **Compatibility Behavior**: `to_dict()` and `from_dict()` handle new fields optionally, preserving 1.0.0 dict serialization round-trips.

---

## 3. Schema Change Audit Verdict

```text
SCHEMA_CHANGE_TYPE = ADDITIVE_ONLY
BACKWARD_COMPATIBILITY = 100% (PRESERVED)
DEMAND_POINT_REUSE = NO (STRICTLY PROHIBITED)
SCHEMA_CHANGE_REPORT_STATUS = PASS
```
