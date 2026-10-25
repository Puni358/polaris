# SCHEMA IMPACT MATRIX

## 1. MASTER SCHEMA IMPACT & COMPATIBILITY MATRIX

The audit evaluated all proposed schema modifications required for synthetic fixture integration against strict governance rules (NO field repurposing, NO breaking changes).

| Target Schema | Current Field | Required Fixture Field | Proposed Action | Compatibility Classification | Repurposing Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ForecastBundle` | `demand` (TimeseriesForecast) | `p_demand_forecast_kW` | Direct mapping (scale kW -> W) | `NO_CHANGE` | Preserves total station demand semantics |
| `ForecastBundle` | None | `p_critical_forecast_kW` | Add optional `critical_demand` field | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `ForecastBundle` | None | `p_flexible_actual_kW` | Add optional `flexible_demand` field | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `StationState` | `battery_soc_pct` | `soc_initial_pct` | Direct mapping | `NO_CHANGE` | Matches existing field |
| `StationState` | `battery_energy_wh` | `e_batt_initial_kWh` | Direct mapping (scale kWh -> Wh) | `NO_CHANGE` | Matches existing field |
| `StationState` | None | `v_fuel_initial_L` | Add optional `fuel_remaining_liters` field | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `StationState` | None | `intended_ecd_state` | Add optional `operating_mode` field | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `DispatchPlan` | `load_served` | `p_critical_total_actual_kW` | Keep total, add `critical_load_served` | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `DispatchPlan` | `unmet_load` | Unmet critical/flex | Keep total, add `critical_load_unmet` | `ADDITIVE_EXTENSION` | **PASSED** (New field, no repurposing) |
| `Station Config` | `diesel.yaml` | `max_power_w` | Align config max power ($60$ kW vs $100$ kW)| `NO_CHANGE` (Config update) | No code schema breaking change |

---

## 2. SUMMARY VERDICT
- **`SCHEMA_IMPACT_STATUS = ADDITIVE_NON_BREAKING`**
- All required schema extensions are purely additive and backward-compatible.
- Zero existing fields are repurposed.
