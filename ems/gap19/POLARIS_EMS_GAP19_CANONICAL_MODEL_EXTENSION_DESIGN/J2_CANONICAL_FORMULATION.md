# J2 CANONICAL FORMULATION

## EMERGENCY BATTERY RESERVE & TERMINAL RESERVE SHORTFALL OBJECTIVE ($J_2$)

- **Priority**: 2
- **Mathematical Form**:
  $$\min J_2(x) = \sum_{t=0}^{23} s_{\text{EBR}}(t) + s_{\text{term}}$$
- **Constraints**:
  $$E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR\_target}}(t), \quad s_{\text{EBR}}(t) \ge 0 \quad \forall t \in \{0, \dots, 23\}$$
  $$E_{\text{batt}}(23) + s_{\text{term}} \ge E_{\text{term\_target}}, \quad s_{\text{term}} \ge 0$$
- **Units**: Watt-hours ($\text{Wh}$).
- **Coefficient Vector ($c_2$)**: Nonzeros at $s_{\text{EBR}}(t)$ ($t=0..23$) and $s_{\text{term}}$ indices with value $1.0$.

`J2_CANONICAL_FORMULATION` = `ESTABLISHED`
