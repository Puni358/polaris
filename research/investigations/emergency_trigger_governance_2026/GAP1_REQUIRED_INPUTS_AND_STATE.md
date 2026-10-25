# POLARIS — GAP 1 REQUIRED INPUTS & STATE PARAMETER SCHEMA

## Executive Summary

This document specifies the complete telemetry, configuration, and state parameter schema required to execute **G1 through G6** in POLARIS.

Every field is cross-referenced against the current POLARIS codebase to identify existing parameters vs missing fields.

---

## 1. Complete Required Input Parameter Schema

| Parameter Name | Data Type | Physical Unit | Required By | Codebase Location | Codebase Feasibility |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `timestamp_epoch` | `float` | seconds | Telemetry Freshness | `station_state.timestamp` | `AVAILABLE` |
| `telemetry_age_seconds` | `float` | seconds | G6 (Freshness Check) | Derived: $t_{\text{wall}} - t_{\text{sample}}$ | `AVAILABLE` |
| `generator_running` | `bool` | boolean | G1 (Operating Status) | `station_state.diesel_running` | `AVAILABLE` |
| `generator_hours_running` | `float` | hours | G5 (Runtime Limits) | `station_state.diesel_hours_running` | `AVAILABLE` |
| `generator_rated_power_w` | `float` | Watts | G5 ($P_{\text{rated}}$) | `config["diesel"]["max_power_w"]` | `AVAILABLE BUT SYNTHETIC` |
| `generator_min_power_w` | `float` | Watts | G5 ($P_{\text{min}}$) | `config["diesel"]["min_power_w"]` | `AVAILABLE BUT SYNTHETIC` |
| `generator_health_status` | `enum` | OK/FAULT/UNKNOWN | G4 (Health Check) | N/A | **`MISSING`** |
| `generator_maintenance_lockout`| `bool` | boolean | G1 (Dispatchability) | N/A | **`MISSING`** |
| `generator_start_ready` | `bool` | boolean | G3 (Start Readiness) | N/A | **`MISSING`** |
| `generator_startup_delay_sec` | `float` | seconds | G3 (Startup Delay) | N/A (Assumed $0.0$ in MILP) | **`MISSING`** |
| `fuel_remaining_liters` | `float` | Liters | G2 (Fuel Sufficiency) | `station_state.diesel_fuel_remaining_liters` | `PARTIALLY AVAILABLE` (Optional) |
| `fuel_telemetry_valid` | `bool` | boolean | G2 (Fuel Check) | Derived from sensor check | `AVAILABLE` |
| `unpumpable_fuel_dead_volume_l`| `float` | Liters | G2 (Usable Fuel Math)| N/A | **`MISSING`** |
| `base_fuel_burn_lph` | `float` | L/h | G2 (Fuel Consumption)| `config["diesel"]["base_fuel_consumption_l_per_h"]` | `AVAILABLE BUT SYNTHETIC` |
| `marginal_fuel_burn_lpwh` | `float` | L/Wh | G2 (Fuel Consumption)| `config["diesel"]["marginal_fuel_consumption_l_per_wh"]` | `AVAILABLE BUT SYNTHETIC` |
| `thermal_derating_factor` | `float` | ratio [0, 1] | G5 (Polar Derating) | N/A (Assumed $1.0$) | **`MISSING`** |

---

## 2. Feasibility Summary & Implementation Roadmap

1. **Available Parameters ($5$ fields)**: `timestamp`, `diesel_running`, `diesel_hours_running`, `base_fuel_burn`, `marginal_fuel_burn`.
2. **Synthetic Parameters ($3$ fields)**: `max_power_w` ($100\text{ kW}$), `min_power_w` ($10\text{ kW}$), `startup_fuel_l` ($2.0\text{ L}$).
3. **Missing Telemetry Parameters ($6$ fields)**: `generator_health_status`, `maintenance_lockout`, `start_ready`, `startup_delay_sec`, `unpumpable_dead_volume`, `thermal_derating_factor`.

To support G1–G6 in synthetic simulations without modifying real station hardware, the missing fields can be assigned default synthetic values in `config["diesel"]`:

```python
# PROPOSED SYNTHETIC CONFIGURATION EXTENSIONS (SPECIFICATION ONLY - DO NOT IMPLEMENT YET)
SYNTHETIC_DIESEL_GOVERNANCE_CONFIG = {
    "max_power_w": 100000.0,
    "min_power_w": 10000.0,
    "base_fuel_consumption_l_per_h": 5.0,
    "marginal_fuel_consumption_l_per_wh": 0.00025,
    "startup_fuel_l": 2.0,
    # Proposed G1-G6 Synthetic Extensions:
    "synthetic_startup_delay_seconds": 300.0,  # 5 minutes warm-up
    "synthetic_unpumpable_fuel_liters": 10.0,   # 10 L dead volume
    "synthetic_thermal_derating_factor": 1.0,   # Nominal 1.0
    "telemetry_max_age_seconds": 30.0           # 30s freshness max
}
```
