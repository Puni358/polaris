# EMS Control Router State Machine Specification

## Architecture: `EMSControlRouter` (`system/control/router.py`)

The `EMSControlRouter` operates as a pure policy routing layer wrapping ECD and optimizers:

```mermaid
stateDiagram-v2
    [*] --> EVALUATE_ECD

    state EVALUATE_ECD {
        [*] --> CheckValidity
        CheckValidity --> ValidPayload: ValidityStatus.VALID
        CheckValidity --> InvalidPayload: ValidityStatus != VALID
    }

    InvalidPayload --> UNKNOWN_INVALID_STATE: Fail-Closed
    UNKNOWN_INVALID_STATE --> [*]: Terminate Run

    ValidPayload --> CheckMode
    
    state CheckMode {
        [*] --> ModeBranch
        ModeBranch --> NORMAL_STATE: m_b >= 0 AND m_d >= 0
        ModeBranch --> EMERGENCY_STATE: m_b < 0 OR m_d < 0
    }

    NORMAL_STATE --> OptionB_MPC: Execute HiGHS MILP
    OptionB_MPC --> CheckSolverStatus
    CheckSolverStatus --> DispatchPlan_NORMAL: Status == OPTIMAL
    CheckSolverStatus --> InfeasibleFallback: Status == INFEASIBLE
    InfeasibleFallback --> EMERGENCY_STATE: ECD Confirms Emergency

    EMERGENCY_STATE --> OptionD_Fallback: Execute Option D Heuristic
    OptionD_Fallback --> DispatchPlan_EMERGENCY: Dispatch Plan Created
```

---

## Verdict
`ROUTER_ARCHITECTURE = SPECIFIED`. Pure policy state machine without internal optimizer modifications.
