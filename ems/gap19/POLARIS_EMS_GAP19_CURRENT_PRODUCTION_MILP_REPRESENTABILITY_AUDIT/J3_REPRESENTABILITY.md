# J3 REPRESENTABILITY AUDIT

## DIESEL FUEL CONSUMPTION OBJECTIVE ($J_3$)

- **Governed Definition**: $J_3 = \sum_{t=0}^{23} \left( a \cdot P_{\text{diesel}}(t) + b \cdot u_{\text{diesel}}(t) + c \cdot v_{\text{start}}(t) \right) \Delta t$
- **Current Variables in `milp.py`**:
  - `p_diesel` ($15t+7$)
  - `u_diesel` ($15t+13$)
  - `v_start` ($15t+14$)

### FINDINGS
1. All physical decision variables required for physical diesel fuel consumption ($P_{\text{diesel}}$, $u_{\text{diesel}}$, $v_{\text{start}}$) already exist in the 360-variable model.
2. The linear objective coefficients can be set directly to physical fuel rates (marginal fuel L/Wh, base fuel L/h, startup fuel L) without adding new decision variables or constraints.

```text
J3_REPRESENTABILITY = FULL
REASON = VARIABLES_AND_CONSTRAINTS_EXIST
```
