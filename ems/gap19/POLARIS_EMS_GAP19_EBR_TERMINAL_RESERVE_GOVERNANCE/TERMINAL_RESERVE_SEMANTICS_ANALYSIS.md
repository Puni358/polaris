# Terminal Reserve Semantics Analysis

This analysis examines potential operational interpretations of the Terminal Reserve (energy target at $t = 24\text{h}$) and its distinction from EBR.

## Candidate Operational Interpretations

### Interpretation 1: Horizon Continuation Reserve
- **Physical Meaning:** Energy required at the end of the 24-hour MPC horizon to prevent unserved load in the subsequent control horizon ($t > 24\text{h}$).
- **Relationship to EBR:** Distinct from intra-horizon EBR; addresses boundary conditions of finite-horizon optimization.
- **Operational Consequence:** Prevents the optimizer from depleting the battery to zero at $t = 24\text{h}$ merely to optimize the current 24-hour objective.

### Interpretation 2: Initial-State Neutrality Target ($E_{\text{terminal}} \ge E_{\text{initial}}$)
- **Physical Meaning:** Requires battery stored energy at $t = 24\text{h}$ to match or exceed initial stored energy at $t = 0\text{h}$.
- **Operational Consequence:** Enforces zero net daily depletion during normal cyclic operation.
- **Potential Drawbacks:** May force unnecessary diesel generation at night to recharge the battery before dawn.

### Interpretation 3: Redundant Duplicate of EBR
- **Physical Meaning:** Terminal reserve is not a separate concept, but simply the final timestep evaluation of EBR ($s_{\text{terminal}} \equiv s_{\text{EBR}}[23]$).
- **Operational Consequence:** Simplifies multi-objective formulation by removing $s_{\text{terminal}}$ as a distinct variable.

```text
TERMINAL_RESERVE_SEMANTICS = GOVERNANCE_DECISION_REQUIRED
EBR_TERMINAL_RELATIONSHIP = GOVERNANCE_DECISION_REQUIRED
```
