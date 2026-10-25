# UNKNOWN_INVALID Source Trace

Static trace of `system/optimization/implementations/gap19_highs_native.py` (lines 38-56):

```python
if operating_mode == "UNKNOWN_INVALID":
    return DispatchPlan(
        schema_version="1.0.0",
        timestamps=timestamps,
        solar_used=[0.0]*24,
        wind_used=[0.0]*24,
        battery_charge=[0.0]*24,
        battery_discharge=[0.0]*24,
        battery_soc=[...]*24,
        diesel_power=[0.0]*24,
        load_served=[0.0]*24,
        flexible_load_schedule=[0.0]*24,
        renewable_curtailment=[(s + w) for s, w in zip(solar_gen, wind_gen)],
        unmet_load=demand,
        objective_value=1e9,
        constraint_status="DEGRADED_FAILSAFE_UNKNOWN_INVALID",
        energy_balance_errors=[0.0]*24
    )
```

## Trace Findings
- **Optimization Bypassed**: Optimization matrix construction and HiGHS solver invocation are completely bypassed.
- **Dispatch Outputs**: All controllable generation (`solar_used`, `wind_used`, `diesel_power`) and load served (`load_served`) are set to `0.0`.
- **Curtailment & Deficit**: `renewable_curtailment` equals total renewable generation (`solar_gen + wind_gen`); `unmet_load` equals total demand.
- **Exceptions / FaultEvents**: No Python exception is raised; no `FaultEvent` is emitted by this optimizer class.
- **Objective Sentinel**: `objective_value = 1e9` is returned directly in `DispatchPlan`.
