# MILP Infeasibility Interface Contract

## Governed Requirement (Decision D4)
`MILP_INFEASIBILITY = INPUT SIGNAL TO ECD ASSESSMENT PATHWAY`

## Current Solver Status Representation
In `GAP19HighsNativeOptimizer`, constraint status is returned inside `DispatchPlan.constraint_status`:
- `OPTIMAL`: Highs solver solved to optimality.
- `OPTIMIZATION_INFEASIBLE`: Solver returned infeasible.

## Adapter Interface & Flow Sequence

```mermaid
graph TD
    A[GAP19HighsNativeOptimizer.optimize] --> B{Check constraint_status}
    B -- OPTIMAL --> C[Return DispatchPlan NORMAL]
    B -- OPTIMIZATION_INFEASIBLE --> D[Trigger ECD Context Assessment]
    D --> E{ECD Assessment operating_mode}
    E -- EMERGENCY --> F[Execute Option D Critical-Load Fallback]
    E -- NORMAL --> G[Execute Degraded Normal Fallback - NO ZERO DISPATCH]
```

---

## Verdict
`MILP_INFEASIBILITY_INTERFACE = SPECIFIED`. Historical zero-dispatch response (`GOVERNED_ZERO_DISPATCH`) is explicitly rejected.
