# Critical Demand Source Trace

Static trace of `system/optimization/implementations/gap19_highs_native.py` (lines 80-83):

```python
critical_demand = config.get("critical_demand_w", None)
if critical_demand is None or len(critical_demand) != 24:
    critical_demand = demand
```

## Trace Findings
- Primary source: `config.get("critical_demand_w", None)`.
- Fallback path: If `critical_demand_w` is `None` or length $
eq 24$, `critical_demand` is set to `demand` (`forecast_bundle.demand.point`, which is total station demand).
