# J4 CURTAILMENT AUDIT

## CONSISTENCY VERIFICATION OF $J_4$ RENEWABLE CURTAILMENT OBJECTIVE

- **Mathematical Form**: $\min J_4 = \sum_{t=0}^{23} \left( P_{\text{pv,curt}}(t) + P_{\text{wind,curt}}(t) \right) \cdot \Delta t$.
- **Variables**: `p_curt_sol` ($15t+2$), `p_curt_wind` ($15t+3$).
- **Units Check**: $(\text{W} + \text{W}) \cdot \text{h} = \text{Wh}$.
- **Consistency Status**: Fully consistent and mathematically sound.

```text
J4 = CONSISTENT
```
