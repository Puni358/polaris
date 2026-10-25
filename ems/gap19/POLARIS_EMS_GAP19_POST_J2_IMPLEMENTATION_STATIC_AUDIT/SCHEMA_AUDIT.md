# Schema Additions & Backward Compatibility Static Audit

## 1. Schema Additions Audit

### 1. `ForecastBundle` (`system/schemas/forecast_bundle.py`)
- **Added Field**: `demand_critical: Optional[TimeseriesForecast] = None`.
- **Validation**: Enforces non-negativity and upper bound ($P_{\text{crit}}[t] \le P_{\text{demand}}[t]$ for all $t$).
- **Backward Compatibility**: `demand.point` retains its exact original semantics (total station demand). `demand_critical` is completely optional for legacy callers.

### 2. `StationState` (`system/schemas/station_state.py`)
- **Added Fields**: `operating_mode: str = "NORMAL"`, `ebr_target_wh_override: Optional[float] = None`, `terminal_target_wh_override: Optional[float] = None`.
- **Backward Compatibility**: Defaults `operating_mode` to `"NORMAL"`. Existing instantiation without new fields remains 100% valid.

### 3. `DispatchPlan` (`system/schemas/dispatch_plan.py`)
- **Added Fields**: `j1_objective: Optional[float] = None`, `j2_objective: Optional[float] = None`, `j3_objective: Optional[float] = None`, `j4_objective: Optional[float] = None`, `reserve_shortfall: Optional[List[float]] = None`.
- **Backward Compatibility**: Optional attributes with `None` default; does not break existing consumers of `DispatchPlan`.

---

## 2. Integrity Verification

- Operating mode is **NOT** silently inferred from ECD.
- ECD remains completely unintegrated.
- Critical demand is explicitly separated from total demand.

---

## 3. Verdict

```
FORECASTBUNDLE_CHANGES = ADDITIVE_COMPATIBLE
STATIONSTATE_CHANGES = ADDITIVE_COMPATIBLE
DISPATCHPLAN_CHANGES = ADDITIVE_COMPATIBLE
DEMAND_POINT_REPURPOSED = NO
SCHEMA_AUDIT_STATUS = PASS
```
