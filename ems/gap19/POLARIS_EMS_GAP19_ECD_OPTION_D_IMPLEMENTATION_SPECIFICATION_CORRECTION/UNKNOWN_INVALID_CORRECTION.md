# UNKNOWN_INVALID Handling Correction

## Correction Details
The previous implementation specification incorrectly claimed that when `EmergencyConditionDetector` returns `operating_mode = UNKNOWN_INVALID`, the runtime runner MUST execute:
- `CRITICAL_TERMINATION`
- `FAILED_TERMINATED_FAIL_CLOSED`
- `halt MPC loop`
- `state_advanced=False`

These operational actions are **NOT ESTABLISHED** in governed policy or existing runner source code.

## Corrected Classification & Boundary

1. **Governed / Code Truth**:
   - `UNKNOWN_INVALID != NORMAL` (`GOVERNED_AND_ESTABLISHED`)
   - `UNKNOWN_INVALID != EMERGENCY` (`GOVERNED_AND_ESTABLISHED`)
   - ECD core (`system/control/ecd.py`) evaluates and returns `operating_mode = UNKNOWN_INVALID` upon invalid inputs (`IMPLEMENTED_AND_VERIFIED`).

2. **Runtime Action Boundary**:
   - `UNKNOWN_INVALID_RUNTIME_ACTION = NOT_ESTABLISHED`
   - The current runtime (`system/runtime/runner.py`) has **NO** consumer or handler for `UNKNOWN_INVALID`.

3. **Prohibited Un-Governed Actions**:
   Do **NOT** select or assume any of the following operational actions for `UNKNOWN_INVALID`:
   - `termination` / `shutdown`
   - `zero-dispatch`
   - `hold-last-plan`
   - `Option D`
   - `operator trip`
   - `generator start`
   - `load shedding`

The implementation specification defines **ONLY** the interface boundary (`ENGINEERING_INTERFACE_ONLY`), not the operational action.
