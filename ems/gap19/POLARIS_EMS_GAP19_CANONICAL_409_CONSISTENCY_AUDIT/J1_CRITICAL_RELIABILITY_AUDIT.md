# J1 CRITICAL RELIABILITY AUDIT

## CONSISTENCY VERIFICATION OF $J_1$ OBJECTIVE

- **Mathematical Form**: $\min J_1 = \sum_{t=0}^{23} P_{\text{unmet,crit}}(t) \cdot \Delta t$.
- **Variable**: $P_{\text{unmet,crit}}(t)$ (Indices $360 \dots 383$). Bound: $[0, P_{\text{demand,crit}}(t)]$.
- **Constraint Connection**: Connected to Critical Demand Balance row $264+t$: $P_{\text{served,crit}}(t) + P_{\text{unmet,crit}}(t) = P_{\text{demand,crit}}(t)$.
- **Units**: $\text{W} \cdot \text{h} = \text{Wh}$.
- **Consistency Status**: Fully consistent and mathematically sound.

```text
J1 = CONSISTENT
```
