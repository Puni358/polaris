# ECD Input Interface & Data Source Audit

## Inspection of `system/control/ecd.py`

The core evaluator function signature is:
`EmergencyConditionDetector.evaluate(horizon_input, critical_load, soc_pct, fuel_remaining_liters, battery_params, diesel_params)`

### Input Data Dictionary & Mapping Table

| Input Parameter | Source Component | Current Schema Location | Runtime Availability | Data Type | Units | Req / Opt | Data Nature | Production Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `horizon_input` | Upstream Authority / Config | `AuthorizedHorizon` dataclass | Available in synthetic config (`T_required = 6.0h`) | `Union[AuthorizedHorizon, float]` | hours ($h$) | Required | Synthetic Fixture | `NOT_ESTABLISHED` |
| `critical_load` | Load Management / Forecast | `CriticalLoadTrajectory` (`ConstantCriticalLoad` / `TimeSeriesCriticalLoad`) | Available in scenario (`actual_demand` / `p_critical`) | `Union[CriticalLoadTrajectory, float]` | Watts ($W$) | Required | Synthetic Fixture | `NOT_ESTABLISHED` |
| `soc_pct` | Battery BMS Telemetry | `StationState.battery_soc_pct` | `ESTABLISHED_RUNTIME` (`StationState`) | `float` | percent ($\%$) | Required | Telemetry / State | `PARTIALLY_ESTABLISHED` |
| `fuel_remaining_liters` | Generator Fuel Gauge | Extracted from `StationState` or `configs["diesel"]` | Hardcoded in `configs["diesel"]` ($100.0	ext{L}$) | `float` | Liters ($L$) | Required | Synthetic Config | `NOT_ESTABLISHED` |
| `battery_params` | Hardware Spec / Config | `BatteryParameters` dataclass | Available in `configs["battery"].yaml` | `BatteryParameters` | Wh, %, W | Required | Synthetic Config | `PARTIALLY_ESTABLISHED` |
| `diesel_params` | Hardware Spec / Config | `DieselParameters` dataclass | Available in `configs["diesel"].yaml` | `DieselParameters` | L/h, L/Wh, W, L | Required | Synthetic Config | `PARTIALLY_ESTABLISHED` |

---

## Detailed Notes
1. `AuthorizedHorizon` must be authenticated and unexpired. For synthetic integration tests, `is_authenticated=True`, `is_authorized=True`, and `t_required_hours=6.0` provide a clean baseline fixture.
2. Fuel telemetry in real stations requires continuous physical volume measurement; currently defaulted via static config.
