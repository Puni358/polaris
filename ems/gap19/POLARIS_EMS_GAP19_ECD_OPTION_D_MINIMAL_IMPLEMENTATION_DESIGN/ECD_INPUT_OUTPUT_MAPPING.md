# ECD Input & Output Parameter Design Mapping

## 1. Input Parameter Mapping to Existing Runtime Sources

Signature: `EmergencyConditionDetector.evaluate(horizon_input, critical_load, soc_pct, fuel_remaining_liters, battery_params, diesel_params)`

| Parameter | Current Runtime Source | Data Availability | Data Type | Units | Directly Usable? | Adapter Required? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `horizon_input` | Governed baseline ($T_{\text{req}}=6.0	ext{h}$) | Configured default | `AuthorizedHorizon(6.0)` | hours | YES | NO (Instantiated directly) |
| `critical_load` | `runtime_context["actual_demand"]` | Scenario timesteps | `ConstantCriticalLoad` | Watts | YES | NO |
| `soc_pct` | `StationState.battery_soc_pct` | `StationState` | `float` | percent | YES | NO |
| `fuel_remaining_liters` | `configs["diesel"]["initial_fuel_l"]` | Config yaml | `float` | Liters | YES | NO |
| `battery_params` | `configs["battery"]` yaml | Config yaml | `BatteryParameters` | Wh, %, W | YES | NO (Constructed from dict) |
| `diesel_params` | `configs["diesel"]` yaml | Config yaml | `DieselParameters` | L/h, L/Wh, W | YES | NO (Constructed from dict) |

---

## 2. Output Parameter Classification for `EmergencyAssessment`

| Dataclass Field | Datatype | Router Necessity | Option D Necessity | Logging Necessity | Final Design Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `operating_mode` | `OperatingMode` | **REQUIRED** | **REQUIRED** | Required | `ROUTING_REQUIRED` |
| `validity_status` | `ValidityStatus` | **REQUIRED** | Not Required | Required | `ROUTING_REQUIRED` |
| `preserved_resource` | `ResourceSelection` | Not Required | **REQUIRED** | Required | `OPTION_D_REQUIRED` |
| `limiting_resource` | `ResourceSelection` | Not Required | **REQUIRED** | Required | `OPTION_D_REQUIRED` |
| `battery_margin_hours` | `float` | Not Required | Not Required | **Required** | `LOGGING_ONLY` |
| `diesel_margin_hours` | `float` | Not Required | Not Required | **Required** | `LOGGING_ONLY` |
| `tie_status` | `bool` | Not Required | Not Required | **Required** | `LOGGING_ONLY` |
| `failure_reason` | `Optional[str]` | Not Required | Not Required | **Required** | `LOGGING_ONLY` |
| `target_horizon_hours` | `Optional[float]` | Not Required | Not Required | **Required** | `LOGGING_ONLY` |
