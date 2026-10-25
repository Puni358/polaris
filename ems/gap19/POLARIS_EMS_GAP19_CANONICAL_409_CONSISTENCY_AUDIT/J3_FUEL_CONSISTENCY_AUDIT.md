# J3 FUEL CONSISTENCY AUDIT

## CONSISTENCY VERIFICATION OF $J_3$ DIESEL FUEL OBJECTIVE

- **Mathematical Form**: $\min J_3 = \sum_{t=0}^{23} \left( F_{\text{marg}} P_{\text{diesel}}(t) + F_{\text{base}} u_{\text{diesel}}(t) + F_{\text{start}} v_{\text{start}}(t) \right) \cdot \Delta t$.
- **Variables**: `p_diesel` ($15t+7$), `u_diesel` ($15t+13$), `v_start` ($15t+14$).
- **Units Check**: $(\text{L/Wh} \cdot \text{W} \cdot \text{h}) + (\text{L/h} \cdot 1 \cdot \text{h}) + (\text{L/event} \cdot 1) = \text{Liters of Diesel}$.
- **Consistency Status**: Fully consistent and mathematically sound.

```text
J3 = CONSISTENT
```
