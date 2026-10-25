# Operating Mode Dependence Analysis

This analysis contrasts required reserve behaviors between `NORMAL` and `EMERGENCY` operating modes.

## Mode-Specific Policy Governance

### NORMAL Mode
- **Governance Intent:** Critical service reliability is primary; battery lifetime preservation and efficient fuel usage are secondary.
- **Reserve Function:** EBR serves as a soft buffer or dynamic target. Extra diesel generation may be used to avoid unnecessary battery degradation, provided critical service is not compromised.
- **Constraint vs. Objective:** Reserve targets should act as lexicographic objectives ($J_2$) rather than hard constraints to prevent infeasibility.

### EMERGENCY Mode
- **Governance Intent:** Microgrid survivability is absolute. Battery lifetime preservation is secondary.
- **Resource Priority:** Dynamic resource preservation (preserve whichever asset has larger survivability margin). Battery discharge is permitted to serve protected critical load without artificial reserve locking.
- **Constraint vs. Objective:** Reserve restrictions that block necessary discharge to critical load are strictly forbidden.

```text
EBR_MODE_BEHAVIOR = GOVERNANCE_DECISION_REQUIRED
TERMINAL_MODE_BEHAVIOR = GOVERNANCE_DECISION_REQUIRED
```
