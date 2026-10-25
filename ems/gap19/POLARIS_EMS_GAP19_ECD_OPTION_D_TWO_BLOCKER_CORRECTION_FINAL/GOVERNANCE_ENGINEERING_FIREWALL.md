# Governance vs Engineering Firewall

## Firewalled Decision Boundaries

1. **Resolved for Implementation Design (Blockers A & B)**:
   - Dynamic fuel state propagation architecture $\to$ **`RESOLVED_FOR_IMPLEMENTATION_DESIGN`**
   - Solver infeasibility routing to ECD context $\to$ **`RESOLVED_FOR_IMPLEMENTATION_DESIGN`**
   - `NEW_GOVERNANCE_DECISIONS_FOR_BLOCKER_A_B = NO`

2. **Unresolved Governance & Engineering Boundaries (Outside Blockers A & B)**:
   - `UNKNOWN_INVALID_RUNTIME_ACTION` = `NOT_ESTABLISHED` (`GOVERNANCE_REQUIRED`)
   - `EMERGENCY_RETURN_POLICY` = `NOT_ESTABLISHED` (`GOVERNANCE_REQUIRED`)
   - `MILP_INFEASIBLE_NORMAL_ACTION` = `NOT_ESTABLISHED` (`GOVERNANCE_REQUIRED` / `ENGINEERING_DESIGN`)
   - Real Station Critical Load Data = `ENGINEERING_INPUT_REQUIRED`
