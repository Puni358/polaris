# ForecastBundle Input Audit

Option B consumes from `ForecastBundle` (v1.0.0):
- `forecast_bundle.timestamps` (24 timestamps)
- `forecast_bundle.solar_generation.point` (24 values, Watts)
- `forecast_bundle.wind_generation.point` (24 values, Watts)
- `forecast_bundle.demand.point` (24 values, Watts)

Critical Demand Audit:
Option B inspects `config.get("critical_demand_w", None)`. If `None`, it falls back to `forecast_bundle.demand.point`.

```text
FORECASTBUNDLE_INPUT_STATUS = ESTABLISHED
CRITICAL_DEMAND_FALLBACK = IMPLEMENTATION_FALLBACK
```
