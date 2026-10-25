# Additive Schema Extensions Specification

## 1. Governance Schema Policy

GAP19 governance enforces:
1. **Additive Extensions Only**: No existing schema fields in version `1.0.0` may be deleted, renamed, or structurally altered.
2. **Explicit Data Semantics**: `demand.point` in `ForecastBundle` represents TOTAL station demand. It MUST NEVER be overwritten or repurposed to represent protected critical load.
3. **Backward Compatibility**: All new fields MUST provide non-breaking default fallback values so existing code continues to execute without modification.

---

## 2. Specified Additive Schema Extensions

### 2.1 `ForecastBundle` Extension (`system/schemas/forecast_bundle.py`)

Add optional field `demand_critical` to `ForecastBundle.__init__()`:

```python
demand_critical: Optional[TimeseriesForecast] = None
```

- **Validation Rule**:
  If `demand_critical` is provided:
  - Must be a `TimeseriesForecast` object with `unit == "W"` and length 24.
  - Must satisfy physical bound: $0.0 \le P_{\text{crit}}[t] \le P_{\text{demand}}[t]$ for all $t \in [0, 23]$.
- **Fallback Rule**:
  If `demand_critical` is `None`:
  - Default to governed scalar ratio: $P_{\text{crit}}[t] = \gamma_{\text{crit}} \cdot P_{\text{demand}}[t]$ (where $\gamma_{\text{crit}} = 1.0$ or governed parameter).

### 2.2 `StationState` Extension (`system/schemas/station_state.py`)

Add optional fields to `StationState.__init__()`:

```python
operating_mode: str = "NORMAL",
ebr_target_wh_override: Optional[float] = None,
terminal_target_wh_override: Optional[float] = None
```

- **Validation Rule**:
  - `operating_mode`: String enum matching `{"NORMAL", "EMERGENCY"}`.
  - `ebr_target_wh_override`: Non-negative float or `None`.
  - `terminal_target_wh_override`: Non-negative float or `None`.

### 2.3 `DispatchPlan` Extension (`system/schemas/dispatch_plan.py`)

Add optional fields to `DispatchPlan.__init__()` to report multi-objective stage results:

```python
j1_objective: Optional[float] = None,       # Critical load deficit (Wh)
j2_objective: Optional[float] = None,       # Reserve shortfall (Wh)
j3_objective: Optional[float] = None,       # Diesel fuel consumption (Liters)
j4_objective: Optional[float] = None,       # Renewable curtailment (Wh)
reserve_shortfall: Optional[List[float]] = None # 24h array of s_J2[t]
```

---

## 3. Summary Verdict

```text
SCHEMA_IMPACT = ADDITIVE_EXTENSION_REQUIRED
BREAKING_CHANGES = NONE
DEMAND_POINT_REUSE = STRICTLY_PROHIBITED
INTERFACE_COMPATIBILITY = PRESERVED
```
