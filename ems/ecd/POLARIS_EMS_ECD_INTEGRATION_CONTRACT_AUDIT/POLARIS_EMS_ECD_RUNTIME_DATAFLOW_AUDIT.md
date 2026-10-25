# POLARIS EMS — ECD RUNTIME DATAFLOW AUDIT

## 1. Executive Summary

This document audits the complete runtime input data flow, data sources, transformations, and schema mapping required to feed the Emergency Condition Detector (ECD) during integrated execution in POLARIS EMS.

---

## 2. Runtime Input Dataflow Mapping Table

| ECD Input | Current Source | Current Representation | Required Extension | Transformation / Adapter | Status |
|-----------|----------------|------------------------|--------------------|--------------------------|--------|
| `T_required` | Operational Override / Config Baseline | None (Hardcoded in fixture test) | `AuthorizedHorizon` wrapper payload | `AuthorizedHorizon(t_required_hours=...)` | `ESTABLISHED` |
| `critical_load_trajectory` | `ForecastBundle` | `demand.point` (Total Demand) | `critical_demand_w: Optional[List[float]]` | `TimeSeriesCriticalLoad` or `ConstantCriticalLoad` | `SCHEMA_EXTENSION_REQUIRED` |
| `battery_soc` | `StationState` | `battery_soc_pct: float` | None (Field exists) | Direct pass `float(state.battery_soc_pct)` | `EXISTING` |
| `fuel_remaining` | `StationState` / SCADA Telemetry | None | `fuel_remaining_liters: Optional[float]` | Direct pass `float(state.fuel_remaining_liters)` | `SCHEMA_EXTENSION_REQUIRED` |
| `battery_params` | `battery.yaml` Config | Dict / YAML | None | `BatteryParameters(capacity_wh=..., min_soc_pct=..., ...)` | `EXISTING` |
| `diesel_params` | `diesel.yaml` Config | Dict / YAML | None | `DieselParameters(base_fuel_consumption_l_per_h=..., ...)` | `EXISTING` |
| `freshness_status` | Telemetry / Command Ingress | Timestamp strings | Freshness validation guard | Explicit `current_time` vs `expires_at` check | `ESTABLISHED` |
| `authorization_status` | Upstream Ingress Gateway | None | Boolean auth flags | `is_authenticated`, `is_authorized` in `AuthorizedHorizon` | `ESTABLISHED` |

---

## 3. Truth-Firewall Data Flow Integrity

To guarantee that future ground truth actuals do not leak into the ECD:
- The ECD consumes **ONLY** observable `StationState` at origin $t_0$ and forecasted `critical_demand_w` from `ForecastBundle`.
- Future ground-truth actuals (`future_actuals` in `runner.py`) are strictly confined to `DigitalTwinSimulator` and **MUST NEVER** be passed to `EmergencyConditionDetector`.

Status: `ESTABLISHED`
