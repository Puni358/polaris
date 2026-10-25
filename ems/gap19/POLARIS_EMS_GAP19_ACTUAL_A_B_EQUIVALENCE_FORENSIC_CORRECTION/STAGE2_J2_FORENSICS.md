# STAGE 2 J2 FORENSICS

## MATHEMATICAL VALIDITY OF SLACK LINEARIZATION FOR J2

The experiment implemented the $J_2$ emergency reserve shortfall objective via linear slack variables:

$$\min J_2(x) = \sum_{t=0}^{23} s_{\text{EBR}}(t) + s_{\text{term}}$$

subject to:
$$E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR\_target}}(t), \quad s_{\text{EBR}}(t) \ge 0$$
$$E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}, \quad s_{\text{term}} \ge 0$$

### MATHEMATICAL AUDIT VERDICT

- Because $s_{\text{EBR}}(t)$ and $s_{\text{term}}$ enter the objective with positive cost $+1.0$ and do not appear elsewhere in constraints, at optimality $s_{\text{EBR}}^*(t) = \max(0, E_{\text{EBR\_target}}(t) - E_{\text{batt}}^*(t))$.
- This exact linear reformulation is mathematically valid and equivalent to the non-smooth governed Stage-2 formulation.

```text
STAGE2_LINEARIZATION = MATHEMATICALLY_VALID_FOR_TEST_MODEL
EBR_TARGET_GOVERNANCE = NOT_YET_SEALED_IN_PRODUCTION
TERMINAL_TARGET_GOVERNANCE = NOT_YET_SEALED_IN_PRODUCTION
```
