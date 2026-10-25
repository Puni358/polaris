# MILP Infeasibility Temporal Control Flow Audit

## Temporal Control Flow Sequence

```text
State_k
   │
   ▼
Forecast_k
   │
   ▼
FIRST_ECD_EVALUATION (#1)
   │
   ├── operating_mode == EMERGENCY ──> Option D Fallback
   │
   └── operating_mode == NORMAL ──> Option B Native HiGHS Optimizer
                                           │
                                           ├── Status == OPTIMAL ──> Return DispatchPlan
                                           │
                                           └── Status == OPTIMIZATION_INFEASIBLE
                                                   │
                                                   ▼
                                           SECOND_ECD_EVALUATION (#2) [UNRESOLVED]
                                           (Evaluates infeasibility signal + state)
                                                   │
                                                   ├── operating_mode == EMERGENCY ──> Option D Fallback
                                                   │
                                                   └── operating_mode == NORMAL ──> NORMAL-AFTER-INFEASIBILITY ACTION
                                                                                   = NOT_ESTABLISHED
```

---

## Formal Classifications
- `FIRST_ECD_EVALUATION = SPECIFIED` (Pre-optimization state evaluation).
- `SECOND_ECD_EVALUATION = UNRESOLVED` (Re-assessment flow after solver infeasibility).
- `MILP_INFEASIBILITY_SIGNAL = SPECIFIED` (`constraint_status == "OPTIMIZATION_INFEASIBLE"`).
- `MILP_INFEASIBILITY_NORMAL_ACTION = NOT_ESTABLISHED` (Governed normal action after solver infeasibility remains un-governed).
