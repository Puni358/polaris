# POLARIS GATE-01 — UNKNOWN_INVALID Runtime Forensic Trace

This document details the exact read-only forensic trace of `OperatingMode.UNKNOWN_INVALID` through the POLARIS codebase.

## 1. Codebase Execution Flow

```
1. Input Payload & State Inspection
   ├── StationState (timestamp, soc_pct, fuel_remaining_liters, etc.)
   └── ForecastBundle & AuthorizedHorizon
        ↓
2. EmergencyConditionDetector.evaluate() [system/control/ecd.py]
   ├── Validates horizon_input (AuthorizedHorizon / float)
   ├── Validates critical_load (ConstantCriticalLoad / TimeSeriesCriticalLoad)
   ├── Validates telemetry (soc_pct, fuel_remaining_liters)
   └── Validates hardware parameters (BatteryParameters, DieselParameters)
        ↓ (If any validation fails)
   Calls _fail_closed(ValidityStatus, reason)
   Returns EmergencyAssessment(operating_mode=OperatingMode.UNKNOWN_INVALID, ...)
        ↓
3. EMSControlRouter.evaluate_and_route() [system/control/router.py]
   ├── Receives EmergencyAssessment with operating_mode == OperatingMode.UNKNOWN_INVALID
   ├── Checks assessment.operating_mode:
   │   ├── OperatingMode.NORMAL → route = "NORMAL"
   │   ├── OperatingMode.EMERGENCY → route = "EMERGENCY"
   │   └── Else → route = "UNKNOWN_INVALID"
   Returns (assessment, "UNKNOWN_INVALID")
        ↓
4. PolarisLocalRunner.run_pipeline() [system/runtime/runner.py]
   ├── Receives route == "UNKNOWN_INVALID"
   ├── Branch check:
   │   ├── if route == "NORMAL": optimizer.optimize(...)
   │   ├── elif route == "EMERGENCY": option_d_solver.solve(...)
   │   └── else:  # UNKNOWN_INVALID
   │       Appends FaultEvent(severity="CRITICAL_TERMINATION", response="FAILED_TERMINATED", state_advanced=False)
   │       Sets execution_status = "FAILED_TERMINATED"
   │       Breaks loop immediately (DigitalTwinSimulator.step() is NOT called)
```

## 2. Forensic Analysis of the Runtime Boundary

1. **Optimizer Isolation**: When `route == "UNKNOWN_INVALID"`, neither Option B (`GAP19HighsNativeOptimizer`) nor Option D (`OptionDFallbackSolver`) is invoked.
2. **Simulator Isolation**: `DigitalTwinSimulator.step()` is **NOT** executed. Digital Twin state advancement does **NOT** occur (`state_advanced = False`).
3. **DispatchPlan Non-Generation**: No new `DispatchPlan` is generated for `UNKNOWN_INVALID`.
4. **Engineering Interface Blocker Location**: The control flow hits the `ENGINEERING_INTERFACE_BLOCKER` in `runner.py` line 151 where `route == "UNKNOWN_INVALID"` branches to halt execution. The physical microgrid action (what physical switches/setpoints are commanded) remains `NOT_IMPLEMENTED`.
