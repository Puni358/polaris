# MILP Infeasibility Result Audit

## Forensic Inspection of Solver Output (`gap19_highs_native.py`)

`GAP19HighsNativeOptimizer.optimize(...)` returns `DispatchPlan`:
- `constraint_status == "OPTIMAL"`: Solver found optimal solution.
- `constraint_status == "OPTIMIZATION_INFEASIBLE"`: Solver returned infeasible.

## Key Properties:
1. `DispatchPlan` object is returned even on infeasibility (with `constraint_status="OPTIMIZATION_INFEASIBLE"`).
2. Returning an infeasible `DispatchPlan` does **NOT** automatically execute dispatch or advance physical simulator state.
3. `DigitalTwinSimulator.step()` is only invoked if `runner.py` explicitly passes `plan` to simulator.

---

## Verdict
`MILP_INFEASIBILITY_SIGNAL = ESTABLISHED`. Status is available via `plan.constraint_status`.
