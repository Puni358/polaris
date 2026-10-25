# J4 REPRESENTABILITY AUDIT

## RENEWABLE CURTAILMENT OBJECTIVE ($J_4$)

- **Governed Definition**: $J_4 = \sum_{t=0}^{23} \left( P_{\text{pv,curt}}(t) + P_{\text{wind,curt}}(t) \right) \Delta t$
- **Current Variables in `milp.py`**:
  - `p_curt_sol` ($15t+2$)
  - `p_curt_wind` ($15t+3$)

### FINDINGS
1. Decision variables for solar curtailment (`p_curt_sol`) and wind curtailment (`p_curt_wind`) already exist in the 360-variable model.
2. The linear objective vector $c_4$ can be mapped directly to these variables with coefficient $1.0 \cdot \Delta t$ without adding new decision variables or constraints.

```text
J4_REPRESENTABILITY = FULL
REASON = VARIABLES_AND_CONSTRAINTS_EXIST
```
