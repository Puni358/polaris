# UNKNOWN_INVALID Runtime Boundary

- The `GAP19HighsNativeOptimizer` class does not instantiate ECD runtime, MPC controllers, or SCADA authentication.
- The return of `DEGRADED_FAILSAFE_UNKNOWN_INVALID` occurs entirely at the boundary of the optimizer call.

`ECD_UNKNOWN_INVALID_RUNTIME_INTEGRATION = NOT_ESTABLISHED`
