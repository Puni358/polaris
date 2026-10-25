# FORECASTBUNDLE INTEGRATION AUDIT

## 1. EXISTING FORECASTBUNDLE DEFINITION
Inspected: [ForecastBundle](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py#L54)

```python
class ForecastBundle:
    def __init__(
        self,
        schema_version: str,
        origin_timestamp: str,
        horizon_hours: int,
        timestamps: List[str],
        solar_irradiance: TimeseriesForecast, # W/m^2
        solar_generation: TimeseriesForecast, # W
        wind_generation: TimeseriesForecast,  # W
        demand: TimeseriesForecast,           # W
        metadata: Dict[str, Any]
    ):
```

---

## 2. FIXTURE FIELD PLACEMENT AUDIT

| Fixture Quantity | Fixture Name & Value | Unit | ForecastBundle Destination Field | Field Status | Notes / Repurposing Guard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Solar actual | `p_pv_actual_kW` | kW | None (Ground Truth only) | External | Not in ForecastBundle |
| Wind actual | `p_wind_actual_kW` | kW | None (Ground Truth only) | External | Not in ForecastBundle |
| Solar forecast | `p_pv_forecast_kW` | kW | `solar_generation.point` | **EXISTS** | Scale kW -> W (x 1000) |
| Wind forecast | `p_wind_forecast_kW` | kW | `wind_generation.point` | **EXISTS** | Scale kW -> W (x 1000) |
| Demand actual | `p_demand_total_actual_kW` | kW | None (Ground Truth only) | External | Not in ForecastBundle |
| Demand forecast | `p_demand_forecast_kW` (49.5 kW) | kW | `demand.point` | **EXISTS** | Represents TOTAL STATION DEMAND (49,500 W) |
| Critical demand forecast | `p_critical_forecast_kW` (33.0 kW) | kW | Proposed `critical_demand.point` | **ADDITIVE EXTENSION REQUIRED** | MUST NOT repurpose `demand.point` |
| Flexible demand forecast | `p_flexible_actual_kW` (15.0 kW) | kW | Proposed `flexible_demand.point` | **OPTIONAL EXTENSION** | Or calculated as total - critical |
| Weather state | N/A | - | `solar_irradiance.point` | **EXISTS** | Proxy derived from PV if needed |
| Forecast metadata | Scenario metadata | - | `metadata` | **EXISTS** | Carries `scenario_id`, `intended_ecd_state` |

---

## 3. PROHIBITED REPURPOSING GUARD
- `demand.point` currently holds total station demand (49.5 kW = 49,500 W in SC-01).
- Repurposing `demand.point` to hold `P_critical(t)` (33.0 kW = 33,000 W) would break existing total demand accounting in `LocalMILPEnergyOptimizer` and `DigitalTwinSimulator`.
- **Governed Rule**: Repurposing `demand.point` is **STRICTLY PROHIBITED**.

---

## 4. PROPOSED BACKWARD-COMPATIBLE ADDITIVE EXTENSION
To support Option D without breaking existing consumers:
```python
# Proposed Additive Field in ForecastBundle Version 1.1.0
critical_demand: Optional[TimeseriesForecast] = None
flexible_demand: Optional[TimeseriesForecast] = None
```
- If `critical_demand` is `None`, default downstream behavior uses total `demand` as single-tier load (backward compatible).
- If present, downstream components (ECD, Option D policy, tiered optimizer) consume `critical_demand`.
