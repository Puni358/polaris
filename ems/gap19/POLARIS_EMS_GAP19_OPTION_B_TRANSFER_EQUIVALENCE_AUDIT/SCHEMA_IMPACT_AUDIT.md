# SCHEMA IMPACT AUDIT

## Distinction Between Solver Choice Schema Impact vs Additive Architecture Extensions

This document provides the explicit separation between solver choice schema impact and GAP19 additive schema requirements.

---

## Schema Impact Separation

```text
SOLVER_ARCHITECTURE_SCHEMA_IMPACT = NONE_FOR_SOLVER_CHOICE
GAP19_OBJECTIVE_FORMULATION_SCHEMA_IMPACT = ADDITIVE_EXTENSION_REQUIRED
```

### 1. Solver Choice Schema Impact:
Selecting Option B vs Option A introduces **ZERO schema changes** to `StationState`, `ForecastBundle`, or `DispatchPlan`. Both solver options consume standard input states and return standard output dispatch setpoints.

### 2. Additive Architecture Extensions (Separately Tracked):
Implementing full GAP19 multi-objective architecture and Option D requires the previously defined non-breaking additive fields:
- `StationState`: `critical_demand`, `flexible_demand`, `minimum_viable_critical_vector`.
- `ForecastBundle`: `critical_demand_forecast`, `flexible_demand_forecast`.
- `DispatchPlan`: `operating_mode`, `critical_load_served`, `flexible_load_served`, `alpha_critical`, `curtailment`, `objective_stage_values`.
