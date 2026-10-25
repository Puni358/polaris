# FIXTURE TO SCHEMA MAPPING AUDIT

## 1. COMPLETE FIELD INVENTORY & MAPPING TABLE

Every column in `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv` was audited against existing POLARIS schema definitions ([StationState](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py#L8), [ForecastBundle](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py#L54), [DispatchPlan](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/dispatch_plan.py#L10)).

| Fixture Field | Type | Unit | Semantics | Target Destination | Existing Schema Field | Direct Mapping | Adapter Required | Extension Required | Conflict / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `scenario_id` | str | - | Scenario Identifier (SC-01..05) | Provider / Test Metadata | None | NO | YES | NO | Fixture provider metadata |
| `scenario_name` | str | - | Scenario Descriptive Name | Provider / Test Metadata | None | NO | YES | NO | Fixture provider metadata |
| `intended_ecd_state`| str | - | Ground Truth ECD State | Test Assertion Engine | None | NO | NO | NO | UNUSED by runtime core |
| `timestep` | int | - | Timestep Index (0..23) | Runtime Context | `metadata["current_index"]`| YES | NO | NO | DIRECT_MAPPING |
| `timestamp_iso` | str | ISO-8601 | ISO Timestamp String | `StationState`, `ForecastBundle`| `timestamp` / `timestamps` | YES | NO | NO | DIRECT_MAPPING |
| `p_critical_heating_kW` | float | kW | Heating Critical Demand | Sub-critical demand | None | NO | YES | YES | Needs sum into `critical_demand` |
| `p_critical_water_kW` | float | kW | Water Critical Demand | Sub-critical demand | None | NO | YES | YES | Needs sum into `critical_demand` |
| `p_critical_comms_kW` | float | kW | Comms Critical Demand | Sub-critical demand | None | NO | YES | YES | Needs sum into `critical_demand` |
| `p_critical_total_actual_kW` | float | kW | Total Critical Demand Actual | `StationState` (Ground Truth) | None | NO | YES | YES | Unit kW -> W conversion needed |
| `p_flexible_actual_kW` | float | kW | Flexible Demand Actual | Ground Truth | None | NO | YES | YES | Unit kW -> W conversion needed |
| `p_demand_total_actual_kW` | float | kW | Total Station Demand Actual | `StationState.last_observed_demand` | `last_observed_demand` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_pv_actual_kW` | float | kW | Solar Generation Actual | Ground Truth | `actual_solar_PV_power` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_wind_actual_kW` | float | kW | Wind Generation Actual | `StationState.last_observed_wind_generation` | `last_observed_wind_generation` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_pv_forecast_kW` | float | kW | Solar Forecast Point | `ForecastBundle.solar_generation.point` | `solar_generation.point` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_wind_forecast_kW` | float | kW | Wind Forecast Point | `ForecastBundle.wind_generation.point` | `wind_generation.point` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_demand_forecast_kW` | float | kW | Total Demand Forecast Point | `ForecastBundle.demand.point` | `demand.point` | NO | YES | NO | Scale kW -> W (x 1000) |
| `p_critical_forecast_kW` | float | kW | Critical Demand Forecast | Proposed `ForecastBundle.critical_demand` | None | NO | YES | YES | SCHEMA_EXTENSION_REQUIRED |
| `soc_initial_pct` | float | % | Battery SOC Initial | `StationState.battery_soc_pct` | `battery_soc_pct` | YES | NO | NO | DIRECT_MAPPING (at t=0) |
| `e_batt_initial_kWh` | float | kWh | Battery Energy Initial | `StationState.battery_energy_wh` | `battery_energy_wh` | NO | YES | NO | Scale kWh -> Wh (x 1000) |
| `v_fuel_initial_L` | float | Liters | Fuel Remaining Initial | ECD Input / Proposed `StationState` | None | NO | YES | YES | STATIONSTATE_EXTENSION_REQUIRED |

---

## 2. CRITICAL AUDIT FINDINGS
1. **Unit Mismatch**: Fixture uses `kW` and `kWh` for power and energy fields, while `ForecastBundle` and `StationState` strictly enforce `W` and `Wh`. An adapter MUST multiply all fixture power/energy quantities by 1000.0.
2. **Field Repurposing Prohibition**: Existing `ForecastBundle.demand.point` represents total station demand (49.5 kW = 49,500 W). Repurposing `demand.point` to mean critical demand ($33.0$ kW) is **STRICTLY PROHIBITED**.
3. **Missing Schema Fields**:
   - `fuel_remaining_liters` is absent from `StationState`.
   - `critical_demand` is absent from `ForecastBundle`.
