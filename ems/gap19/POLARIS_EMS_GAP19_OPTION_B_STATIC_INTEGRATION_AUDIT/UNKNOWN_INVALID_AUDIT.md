# UNKNOWN_INVALID Fail-Safe Audit

Option B inspects `config["operating_mode"]`. If `"UNKNOWN_INVALID"`, Option B bypasses solver execution and returns a degraded fail-safe `DispatchPlan` (`constraint_status="DEGRADED_FAILSAFE_UNKNOWN_INVALID"`, zero generation, `objective_value=1e9`).

```text
UNKNOWN_INVALID = ESTABLISHED
BEHAVIOR = FAIL_SAFE_SOLVER_BYPASS
```
