# J4 CANONICAL FORMULATION

## AVOIDABLE RENEWABLE CURTAILMENT OBJECTIVE ($J_4$)

- **Priority**: 4 (Lowest priority stage)
- **Mathematical Form**:
  $$\min J_4(x) = \sum_{t=0}^{23} \left( P_{\text{pv,curt}}(t) + P_{\text{wind,curt}}(t) \right) \cdot \Delta t$$
- **Units**: Watt-hours ($\text{Wh}$).
- **Coefficient Vector ($c_4$)**: Nonzeros at $P_{\text{pv,curt}}(t)$ and $P_{\text{wind,curt}}(t)$ indices with value $1.0 \cdot \Delta t$.

`J4_CANONICAL_FORMULATION` = `ESTABLISHED`
