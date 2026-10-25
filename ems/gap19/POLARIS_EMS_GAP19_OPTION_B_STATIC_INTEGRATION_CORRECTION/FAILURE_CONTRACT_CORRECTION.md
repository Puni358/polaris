# Failure Contract & Exception Classification

| Failure Scenario | Actual Code Behavior | Classification |
| :--- | :--- | :--- |
| Operating Mode `"UNKNOWN_INVALID"` | Returns degraded `DispatchPlan` (`constraint_status="DEGRADED_FAILSAFE_UNKNOWN_INVALID"`, `objective_value=1e9`) | `ACTUAL_CODE` |
| Missing `critical_demand_w` | Falls back to total demand `forecast_bundle.demand.point` | `ACTUAL_CODE` |
| Invalid `critical_demand` length | Falls back to total demand `forecast_bundle.demand.point` | `ACTUAL_CODE` |
| Solver Infeasibility (`model_status != kOptimal`) | Returns degraded `DispatchPlan` (`constraint_status="OPTIMIZATION_INFEASIBLE: <status>"`, `objective_value=1e9`) | `ACTUAL_CODE` |
| Governed Fault Event Emission | Not implemented inside optimizer module | `GOVERNANCE_ONLY` |
