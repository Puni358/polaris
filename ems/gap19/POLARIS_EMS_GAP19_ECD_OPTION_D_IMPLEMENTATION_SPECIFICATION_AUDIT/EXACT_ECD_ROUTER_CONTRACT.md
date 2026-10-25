# Exact ECD Core → Router Interface Specification

## Function Signature
`EmergencyConditionDetector.evaluate(horizon_input, critical_load, soc_pct, fuel_remaining_liters, battery_params, diesel_params)`

## Input Parameter Specification & Mapping Table

| Parameter Name | Actual Source | Actual Type | Actual Unit | Current Runtime Availability | Req / Opt | Data Nature | Implemented / Contract | Future Adapter Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `horizon_input` | Upstream Config | `AuthorizedHorizon` | hours ($h$) | Available ($6.0	ext{h}$) | Required | Synthetic Fixture | Implemented | `AuthorizedHorizonAdapter` |
| `critical_load` | Scenario Demand | `CriticalLoadTrajectory` | Watts ($W$) | Available (`actual_demand`) | Required | Synthetic Fixture | Implemented | `CriticalLoadAdapter` |
| `soc_pct` | `StationState` | `float` | percent ($\%$) | `StationState.battery_soc_pct` | Required | Runtime State | Implemented | None (Direct attribute) |
| `fuel_remaining_liters` | Config / State | `float` | Liters ($L$) | `configs["diesel"]["initial_fuel_l"]` | Required | Synthetic Config | Implemented | `FuelStateAdapter` |
| `battery_params` | Config | `BatteryParameters` | Wh, %, W | `configs["battery"]` | Required | Hardware Spec | Implemented | `BatteryConfigAdapter` |
| `diesel_params` | Config | `DieselParameters` | L/h, L/Wh, W | `configs["diesel"]` | Required | Hardware Spec | Implemented | `DieselConfigAdapter` |

---

## Output Data Contract (`EmergencyAssessment`)
The router receives `EmergencyAssessment` containing:
- `operating_mode`: `OperatingMode` (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`) $	o$ **REQUIRED FOR ROUTING**
- `validity_status`: `ValidityStatus` (`VALID`, etc.) $	o$ **REQUIRED FOR ROUTING**
- `preserved_resource`: `ResourceSelection` (`BATTERY`, `DIESEL`, `BOTH`, `NONE`) $	o$ **REQUIRED FOR OPTION D**
- `limiting_resource`: `ResourceSelection` (`BATTERY`, `DIESEL`, `BOTH`, `NONE`) $	o$ **REQUIRED FOR OPTION D**
- `battery_margin_hours`: `float` $	o$ **LOGGING / METADATA**
- `diesel_margin_hours`: `float` $	o$ **LOGGING / METADATA**
