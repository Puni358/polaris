# ECD Current Fuel Interface Specification

## Dynamic Fuel Input Flow to ECD

```text
StationState_k.diesel_fuel_remaining_liters
   │
   ▼
EmergencyConditionDetector.evaluate(
    horizon_input=AuthorizedHorizon(6.0),
    critical_load=ConstantCriticalLoad(demand_k),
    soc_pct=StationState_k.battery_soc_pct,
    fuel_remaining_liters=StationState_k.diesel_fuel_remaining_liters, # DYNAMIC CURRENT FUEL
    battery_params=battery_params,
    diesel_params=diesel_params
)
```

## Guarantees:
1. `configs["diesel"]["initial_fuel_l"]` is consumed **ONLY** as the initial condition at step $k=0$.
2. For all steps $k \ge 1$, ECD receives `State_k.diesel_fuel_remaining_liters`, ensuring real-time dynamic survivability evaluation.

---

## Verdict
`ECD_ROLLING_FUEL_INPUT = INTERFACE_REQUIRED`.
