# Critical-Demand Semantic Firewall Audit

```text
TOTAL_STATION_DEMAND != PROTECTED_CRITICAL_DEMAND
REAL_STATION_CRITICAL_LOAD = NOT_ESTABLISHED
CRITICAL_DEMAND_INPUT_STATUS = FALLBACK_PRESENT
```

Option B supports explicit `critical_demand_w` via `config`. In the absence of governance-established critical load telemetry, Option B defaults to treating total demand as critical demand (`critical_demand = demand`). This is classified as `FALLBACK_PRESENT`.
