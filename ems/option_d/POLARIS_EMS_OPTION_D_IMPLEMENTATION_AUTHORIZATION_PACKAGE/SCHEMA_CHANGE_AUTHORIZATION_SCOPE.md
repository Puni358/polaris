# SCHEMA CHANGE AUTHORIZATION SCOPE

## Additive Non-Breaking Extension Specification

This document defines the authorized schema changes for `StationState`, `ForecastBundle`, and `DispatchPlan`. All proposed changes are strictly **ADDITIVE and OPTIONAL**, ensuring 100% backward compatibility with existing codebase callers.

---

## Schema Extension Details

### 1. `StationState` Extensions (`system/schemas/state.py`)
```python
# Additive optional fields in StationState dataclass
critical_demand: Optional[float] = None
# Sum of minimum viable requirements across protected critical categories (kW)

flexible_demand: Optional[float] = None
# Sheddable noncritical demand (kW)

minimum_viable_critical_vector: Optional[Dict[str, float]] = None
# Breakdown: {"heating": 15.0, "water": 10.0, "communications": 5.0} (kW)
```

### 2. `ForecastBundle` Extensions (`system/schemas/forecast.py`)
```python
# Additive optional fields in ForecastBundle dataclass
critical_demand_forecast: Optional[List[float]] = None
# Vector of forecasted critical demand over horizon H (kW)

flexible_demand_forecast: Optional[List[float]] = None
# Vector of forecasted flexible demand over horizon H (kW)
```

### 3. `DispatchPlan` Extensions (`system/schemas/dispatch.py`)
```python
# Additive optional fields in DispatchPlan dataclass
operating_mode: str = "NORMAL"
# Operating mode active during dispatch ("NORMAL", "OPTION_D", "UNKNOWN_INVALID")

critical_load_served: Optional[List[float]] = None
# Vector of served protected critical power over horizon H (kW)

flexible_load_served: Optional[List[float]] = None
# Vector of served flexible power over horizon H (kW)

alpha_critical: Optional[List[float]] = None
# Vector of D4 proportionality factor alpha(t) over horizon H (0.0 to 1.0)

curtailment: Optional[List[float]] = None
# Vector of curtailed excess power over horizon H (kW)
```

---

## Backward Compatibility Guarantee

1. Existing code accessing `state.demand.point` continues to function without error.
2. If `critical_demand` is `None`, the fixture adapter automatically populates `critical_demand` and `flexible_demand` based on the active mode or default fallback ratios.
3. Serializers and deserializers treat all new fields as optional JSON keys (`default=None`).
