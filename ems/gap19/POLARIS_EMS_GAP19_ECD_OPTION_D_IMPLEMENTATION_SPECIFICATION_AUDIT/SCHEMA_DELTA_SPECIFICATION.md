# Additive Schema Delta Specification

## Principle: ZERO REPURPOSING OF EXISTING FIELDS

All schema modifications are strictly additive and 100% backward-compatible.

## 1. `StationState` Additive Extension (`system/schemas/station_state.py`)

```python
# Additive optional field in __init__:
def __init__(
    self,
    ...,
    operating_mode: str = "NORMAL",
    ebr_target_wh_override: Optional[float] = None,
    terminal_target_wh_override: Optional[float] = None,
    emergency_assessment_json: Optional[str] = None  # ADDITIVE EXTENSION
):
    ...
    self.emergency_assessment_json = emergency_assessment_json
```

## 2. `DispatchPlan` Additive Extension (`system/schemas/dispatch_plan.py`)

```python
# Additive optional fields in __init__:
def __init__(
    self,
    ...,
    operating_mode: Optional[str] = None,       # ADDITIVE EXTENSION ("NORMAL" / "EMERGENCY")
    option_d_active: Optional[bool] = None,      # ADDITIVE EXTENSION (True / False)
    emergency_assessment_dict: Optional[Dict[str, Any]] = None # ADDITIVE EXTENSION
):
    ...
    self.operating_mode = operating_mode
    self.option_d_active = option_d_active
    self.emergency_assessment_dict = emergency_assessment_dict
```

---

## Verdict
`SCHEMA_DELTA = ADDITIVE_EXTENSION_REQUIRED`. Fully backward-compatible.
