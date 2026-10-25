# J1 CANONICAL FORMULATION

## CRITICAL RELIABILITY OBJECTIVE ($J_1$)

- **Priority**: 1 (Highest priority stage)
- **Mathematical Form**:
  $$\min J_1(x) = \sum_{t=0}^{23} P_{\text{unmet,crit}}(t) \cdot \Delta t$$
- **Governed Normal-Operation Target**: $J_1^* = 0.0\text{ Wh}$ (Zero critical load deficit during normal operation whenever physically feasible).
- **Units**: Watt-hours ($\text{Wh}$).
- **Coefficient Vector ($c_1$)**: Nonzeros at $P_{\text{unmet,crit}}(t)$ indices with value $1.0 \cdot \Delta t$.

`J1_CANONICAL_FORMULATION` = `ESTABLISHED`
