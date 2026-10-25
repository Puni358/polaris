# POLARIS EMS GAP19 — EMS Control Router Implementation Report

## Technical Design & Policy Boundary

`EMSControlRouter` (`system/control/router.py`) acts as a pure policy routing layer wrapping `EmergencyConditionDetector`.

### 1. Interface
```python
def evaluate_and_route(
    self,
    current_state: StationState,
    bundle: ForecastBundle,
    configs: Dict[str, Any]
) -> Tuple[EmergencyAssessment, str]
```

### 2. Policy Mapping
- `OperatingMode.NORMAL` → `"NORMAL"` (Routes execution to Option B `GAP19HighsNativeOptimizer`).
- `OperatingMode.EMERGENCY` → `"EMERGENCY"` (Routes execution to Option D `OptionDFallbackSolver`).
- `OperatingMode.UNKNOWN_INVALID` → `"UNKNOWN_INVALID"` (Prevents selection of Option B and Option D).

### 3. Immutable Governance Safeguards
- Pure functional wrapper: Zero state mutation.
- Does **NOT** calculate survivability (delegated 100% to `ecd.py`).
- Does **NOT** modify ECD results.
- Does **NOT** declare emergency independently.
- Does **NOT** override ECD decisions.
- Does **NOT** interpret J2 or MILP infeasibility as emergency.
- Does **NOT** implement emergency return.
- Does **NOT** invent UNKNOWN_INVALID runner operational actions (`UNKNOWN_INVALID_RUNNER_OPERATIONAL_ACTION = NOT_IMPLEMENTED`).
