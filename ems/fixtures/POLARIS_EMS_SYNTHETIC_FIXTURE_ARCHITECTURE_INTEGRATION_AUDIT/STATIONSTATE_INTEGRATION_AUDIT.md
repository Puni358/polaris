# STATIONSTATE INTEGRATION AUDIT

## 1. EXISTING STATIONSTATE DEFINITION
Inspected: [StationState](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py#L8)

```python
class StationState:
    def __init__(
        self,
        timestamp: str,
        battery_soc_pct: float,
        battery_energy_wh: float,
        diesel_running: bool,
        diesel_hours_running: float,
        last_observed_solar_irradiance: float,
        last_observed_demand: float,
        last_observed_wind_generation: float
    ):
```

---

## 2. FIXTURE CAPABILITY MAPPING

| Capability / Quantity | Fixture Value / Representation | StationState Status | Action Required |
| :--- | :--- | :--- | :--- |
| **Battery SOC** | `soc_initial_pct` (e.g. 80.0%) | **EXISTS** (`battery_soc_pct`) | DIRECT_MAPPING |
| **Battery Energy** | `e_batt_initial_kWh` (e.g. 160.0 kWh) | **EXISTS** (`battery_energy_wh`) | Scale kWh -> Wh (160,000 Wh) |
| **Fuel Remaining** | `v_fuel_initial_L` (20.0L to 500.0L) | **NOT REPRESENTABLE** | **STATIONSTATE_EXTENSION_REQUIRED** |
| **Generator State** | `diesel_running` | **EXISTS** (`diesel_running`) | DIRECT_MAPPING |
| **Generator Hours** | `diesel_hours_running` | **EXISTS** (`diesel_hours_running`) | DIRECT_MAPPING |
| **Operating Mode** | `intended_ecd_state` / ECD state | **NOT REPRESENTABLE** | **ADDITIVE EXTENSION REQUIRED** |
| **Current Total Load** | `p_demand_total_actual_kW` (45.0 kW) | **EXISTS** (`last_observed_demand`) | Scale kW -> W (45,000 W) |
| **Critical Load** | `p_critical_total_actual_kW` (30.0 kW) | **NOT REPRESENTABLE** | **ADDITIVE EXTENSION REQUIRED** |
| **Renewable State** | `p_pv_actual_kW`, `p_wind_actual_kW` | **EXISTS** (`last_observed_*`) | DIRECT_MAPPING |

---

## 3. KEY GAPS: FUEL REMAINING & OPERATING MODE

### FUEL REMAINING (`fuel_remaining_liters`)
- `fuel_remaining_liters` is a mandatory input to `EmergencyConditionDetector.evaluate()` ([ecd.py:L213](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L213)).
- Currently, `StationState` does NOT track fuel volume.
- Classification: `STATIONSTATE_EXTENSION_REQUIRED`.

### OPERATING MODE (`operating_mode`)
- `operating_mode` (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`) is produced by ECD and needed by state updates.
- Currently, `StationState` does NOT store current operating mode.
- Classification: `ADDITIVE EXTENSION REQUIRED`.
