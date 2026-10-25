# First Single-Cycle Option-B Runtime Test Contract

## Test Parameters
- **Horizon:** 24 Hours (1 MPC timestep solve)
- **Operating Mode:** `NORMAL`
- **Optimizer:** `GAP19HighsNativeOptimizer` via `highs_native`
- **Explicit Critical Demand:** YES (`config["critical_demand_w"]`)
- **Future Truth Access to Optimizer:** NO
- **Expected Outcome:** Exactly one valid `DispatchPlan` with `constraint_status="OPTIMAL"`.
