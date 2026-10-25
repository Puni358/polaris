# Exception & Failure Contract Audit

If HiGHS reports `model_status != kOptimal`, Option B returns a valid `DispatchPlan` with `constraint_status="OPTIMIZATION_INFEASIBLE: <status>"`, `objective_value=1e9`, and `unmet_load=demand`.

```text
FAILURE_CONTRACT = ESTABLISHED
```
