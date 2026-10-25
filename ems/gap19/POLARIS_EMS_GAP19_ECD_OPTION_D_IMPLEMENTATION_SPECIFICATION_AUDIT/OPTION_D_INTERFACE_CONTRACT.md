# Option D Interface Specification Contract

## Input Parameters for Option D Dispatch Adapter
The future `OptionDFallbackSolver.solve(...)` requires:
1. `assessment`: `EmergencyAssessment` (from ECD core)
2. `bundle`: `ForecastBundle` (solar/wind forecasts)
3. `current_state`: `StationState` (battery SOC, diesel status)
4. `configs`: `Dict[str, Any]` (hardware parameters)

## Exact Dispatch Logic Hierarchy (DEC-004 Enforcement)
```text
1. Protect Critical Demand: P_critical(t) served at highest priority.
2. Direct Renewable Generation: Allocate P_pv(t) + P_wind(t) directly to critical load.
3. Diesel Generator Support: If renewables < P_critical(t), start/run diesel generator for remaining critical load.
4. Governed Emergency Battery Usage:
   - If preserved_resource == BATTERY: Preserve battery energy; rely primarily on diesel.
   - If preserved_resource == DIESEL: Discharge battery to save fuel; minimize diesel runtime.
5. Exclude Non-Critical Load: Non-critical demand is shed (P_noncritical = 0).
6. Proportional Allocation: If total available generation < P_critical(t), allocate available power proportionally across protected circuits.
7. Authority Escalation: Emit critical alert requesting operator intervention.
8. Excess Diesel Battery Charging:
   - IF diesel is required to run for critical load AND min_power > P_critical_remaining, excess power MAY charge battery.
   - DIESEL MUST NEVER BE STARTED SOLELY TO CHARGE BATTERY IN EMERGENCY MODE.
```
