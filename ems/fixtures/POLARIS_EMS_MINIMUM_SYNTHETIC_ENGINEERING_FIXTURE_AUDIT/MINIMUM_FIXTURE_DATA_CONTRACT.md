# POLARIS EMS — MINIMUM FIXTURE DATA CONTRACT

## 1. Executive Summary

This document specifies the exact data schemas and field requirements for the **Minimum Synthetic Engineering Fixture**.

---

## 2. Interface Schema Contracts

### StationState Schema Contract
- `timestamp`: ISO-8601 string (e.g. `"2026-01-15T00:00:00Z"`).
- `battery_soc_pct`: `float` $\in [20.0, 95.0]$.
- `battery_energy_wh`: `float` $\in [40000.0, 190000.0]$.
- `diesel_running`: `bool`.
- `diesel_hours_running`: `float` $\ge 0.0$.
- `last_observed_solar_irradiance`: `float` $\ge 0.0$ ($\text{W/m}^2$).
- `last_observed_demand`: `float` $\ge 0.0$ ($\text{W}$).
- `last_observed_wind_generation`: `float` $\ge 0.0$ ($\text{W}$).

### ForecastBundle Schema Contract (Version 1.0.0)
- `schema_version`: `"1.0.0"`.
- `origin_timestamp`: ISO-8601 string.
- `horizon_hours`: `24`.
- `timestamps`: 24 hourly ISO-8601 strings.
- `solar_irradiance`: `TimeseriesForecast` ($\text{W/m}^2$).
- `solar_generation`: `TimeseriesForecast` ($\text{W}$).
- `wind_generation`: `TimeseriesForecast` ($\text{W}$).
- `demand`: `TimeseriesForecast` ($\text{W}$, Total Station Demand).
- `metadata`: `Dict[str, Any]` (Contains optional `metadata["critical_demand_forecast"]`).

---

## 3. Data Firewall Rules

1. **Schema Preservation**: `ForecastBundle` remains frozen at version `1.0.0`.
2. **Total vs Critical Demand**: `forecast_bundle.demand.point` represents total station demand. Synthetic critical load $P_{\text{critical}}(t)$ is injected via `metadata["critical_demand_forecast"]` or abstract provider interface.
3. **Truth Firewall**: Controller components (ECD, Policy, Optimizer) consume `ForecastBundle`. Simulator consumes ground-truth actuals $A_t$. Controller NEVER receives future actuals $A_t$.
