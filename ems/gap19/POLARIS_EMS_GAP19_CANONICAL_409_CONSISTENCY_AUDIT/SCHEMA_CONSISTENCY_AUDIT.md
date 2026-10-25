# SCHEMA CONSISTENCY AUDIT

## ADDITIVE SCHEMA INTERFACE BOUNDARY AUDIT

- `ForecastBundle.demand.point`: Preserves 100% legacy total station demand semantics.
- `ForecastBundle.demand.critical_point`: Additive field for protected critical load demand.
- `StationState.operating_mode`: Additive string field (`"NORMAL"`, `"EMERGENCY"`, `"UNKNOWN_INVALID"`).
- `DispatchPlan`: Additive fields for $J_1..J_4$ objective outputs and critical load served/unmet metrics.

```text
SCHEMA_BOUNDARY = PASS
```
