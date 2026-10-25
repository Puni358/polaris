# MILP Infeasibility Interface Design

## Interface Design for Infeasibility Status Signal

1. **Solver Status Capture**:
   When `GAP19HighsNativeOptimizer.optimize(...)` returns a `DispatchPlan`, the router inspects `plan.constraint_status`.

2. **Infeasibility Status Signal Flow**:
   ```text
   plan.constraint_status == "OPTIMIZATION_INFEASIBLE"
     ↓
   Status passed as input signal to ECD assessment pathway
     ↓
   Is ECD assessment operating_mode == EMERGENCY?
     ├── YES: Route to Option D Protected Critical-Load Fallback.
     └── NO: Operational action for NORMAL mode after infeasibility is NOT_ESTABLISHED.
   ```

3. **Status Classification**:
   - `MILP_INFEASIBILITY_INTERFACE = SPECIFIED`
   - `MILP_INFEASIBILITY_NORMAL_ACTION = NOT_ESTABLISHED`

Historical zero-dispatch blackout (`GOVERNED_ZERO_DISPATCH`) remains rejected as governed policy.
