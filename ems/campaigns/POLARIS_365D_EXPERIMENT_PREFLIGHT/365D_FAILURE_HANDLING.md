# 365D FAILURE & INFEASIBILITY CONTAINMENT (GATE-02 OPTION C COMPLIANT)

## Authoritative Gate-02 Option C Policy Enforcement

> [!IMPORTANT]
> The authoritative human Gate-02 decision is **`GATE02_HUMAN_DECISION = OPTION_C`**.
> - Critical load is compulsory and MUST NEVER be relaxed under any circumstance.
> - Governed constraint relaxation applies ONLY to authorized noncritical, flexible, or interruptible loads with mandatory operator notification.
> - Original MILP infeasibility MUST trigger the governed relaxation/re-solve pathway.
> - If the relaxed problem becomes feasible, execution proceeds with valid dispatch.
> - If the problem remains infeasible: NO further invented relaxation, NO zero-dispatch execution, NO Digital Twin advancement, and **NO AUTOMATIC OPTION D INVOCATION**. Return to governed unresolved state / stop condition.

```
                  MILP Solve Attempt
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
        FEASIBLE                   INFEASIBLE
            │                           │
            ▼                           ▼
     Commit k=0 Action     Governed Noncritical Relaxation
     Advance Digital Twin               │
                                ┌───────┴───────┐
                                ▼               ▼
                            FEASIBLE       REMAINS INFEASIBLE
                                │               │
                                ▼               ▼
                         Commit Action      STOP CONDITION
                         Advance Twin       No Twin Advancement
                                            No Auto Option D
```

## Failure Category Matrix

| Failure Trigger | Controller Action | Digital Twin Action | Campaign Status |
| :--- | :--- | :--- | :--- |
| **`UNKNOWN_INVALID` ECD** | Fail-Closed Stop | Zero Twin Advancement | `FAILED_TERMINATED` |
| **MILP Infeasibility** | Governed Relaxation / Re-solve | Zero Advancement if unresolved | `BLOCKED_INFEASIBLE` |
| **Invalid Forecast Bundle** | Reject Bundle | Zero Twin Advancement | `FAILED_TERMINATED` |
| **Battery SOC Breach** | Raise `FAILED_STATE_VIOLATION` | Zero Twin Advancement | `FAILED_TERMINATED` |
| **Solver Timeout / Exception** | Raise Runtime Exception | Zero Twin Advancement | `FAILED_TERMINATED` |

## Prohibited Behaviors
- **`MILP_INFEASIBLE != EMERGENCY`**: MILP infeasibility is NOT an ECD Emergency and must NOT automatically route to Option D fallback.
- **`MILP_INFEASIBLE != UNKNOWN_INVALID`**: MILP infeasibility is handled via governed relaxation, not silent fail-closed crash.
- **No Automatic Option D**: Option D fallback solver is invoked ONLY when ECD returns `EMERGENCY` mode.
