# Critical-Demand Semantic & Fallback Correction

In `gap19_highs_native.py`, `critical_demand` is ingested as `config.get("critical_demand_w", None)`. If unprovided, it falls back to `forecast_bundle.demand.point`.

```text
TOTAL_STATION_DEMAND != PROTECTED_CRITICAL_DEMAND
REAL_STATION_CRITICAL_LOAD = NOT_ESTABLISHED

CRITICAL_DEMAND_EXPLICIT_INPUT = REQUIRED_FOR_GOVERNED_TEST
CRITICAL_DEMAND_FALLBACK = IMPLEMENTATION_ONLY
TOTAL_DEMAND_EQUALS_CRITICAL_DEMAND = NOT_ESTABLISHED
```

The runner integration must not rely silently on total demand as critical demand.
