# J2 REPRESENTABILITY AUDIT

## EMERGENCY BATTERY RESERVE & TERMINAL RESERVE OBJECTIVE ($J_2$)

- **Governed Definition**: $J_2 = \sum_{t=0}^{23} s_{\text{EBR}}(t) + s_{\text{term}}$
- **Required Slacks**:
  - $s_{\text{EBR}}(t) = \max(0, E_{\text{EBR\_target}}(t) - E_{\text{batt}}(t)) \ge 0$
  - $s_{\text{term}} = \max(0, E_{\text{term\_target}} - E_{\text{batt}}(23)) \ge 0$

### FINDINGS
1. The current 360-variable `milp.py` contains **ZERO** slack variables ($s_{\text{EBR}}(t)$ or $s_{\text{term}}$).
2. The current 360-variable `milp.py` contains **ZERO** constraints linking energy state $E_{\text{next}}(t)$ to an emergency reserve target or terminal reserve target.
3. In MILP optimization, representing the non-smooth shortfall $\max(0, E_{\text{target}} - E(t))$ requires explicit auxiliary non-negative slack variables ($s(t) \ge 0$) and linear inequality constraints ($E(t) + s(t) \ge E_{\text{target}}$).
4. Without adding 25 new variables ($24 \times s_{\text{EBR}}(t) + 1 \times s_{\text{term}}$) and 25 new linear constraints, the 360-variable model **CANNOT** represent $J_2$.

```text
J2_REPRESENTABILITY = BLOCKED
REASON = REQUIRES_ADDITIONAL_MODEL_VARIABLES_OR_CONSTRAINTS
```
