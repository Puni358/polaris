# UNKNOWN_INVALID Fail-Closed Routing Audit

## Governance Principle (Fail-Closed Safety Boundary)
1. `UNKNOWN_INVALID != EMERGENCY`
2. `UNKNOWN_INVALID != NORMAL`

When telemetry, authorization, or configuration inputs fail validation, ECD returns `operating_mode = UNKNOWN_INVALID` with a specific `ValidityStatus`.

## Audit of `ValidityStatus` Triggers in `system/control/ecd.py`:
- `MISSING_T_REQUIRED`: Horizon input missing or non-finite.
- `EXPIRED_T_REQUIRED`: Authorization timestamp expired.
- `UNAUTHORIZED_T_REQUIRED`: Authorization payload unauthenticated or unauthorized.
- `INVALID_TELEMETRY`: NaN/Inf or out-of-bound SOC ($<0\%$ or $>100\%$) or negative fuel.
- `INVALID_CRITICAL_LOAD`: Invalid critical load trajectory.
- `INVALID_CONFIG`: Non-physical battery or diesel config parameters.

---

## Runtime Handling Audit (`system/runtime/runner.py`)
- **Current State**: `runner.py` does **NOT** currently check `operating_mode == UNKNOWN_INVALID`.
- **Target Integration Boundary**:
  ```text
  IF ECD returns UNKNOWN_INVALID:
      Emit FaultEvent(severity="CRITICAL_TERMINATION", response="FAIL_CLOSED")
      Halt MPC iteration without advancing simulator state with invalid commands.
  ```
- **Classification**: `UNKNOWN_INVALID_RUNTIME_HANDLING = NOT_ESTABLISHED` (Target implementation required).
