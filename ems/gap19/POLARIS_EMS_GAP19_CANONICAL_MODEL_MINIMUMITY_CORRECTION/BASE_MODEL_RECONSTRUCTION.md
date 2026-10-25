# BASE MODEL RECONSTRUCTION

## INDEPENDENT VERIFICATION OF BASELINE PRODUCTION `milp.py`

- **Source File**: `system/optimization/implementations/milp.py`
- **Base Variable Count ($N_{\text{base}}$)**: 360 ($24 \times 15$ variables per timestep)
  - Continuous variables: 264
  - Binary variables: 96 ($u_{\text{chg}}, u_{\text{dis}}, u_{\text{diesel}}, v_{\text{start}}$ for $t=0..23$)
- **Base Constraint Count ($M_{\text{base}}$)**: 264 linear constraints ($11 \times 24$)
- **Diesel Status Transition in Base**: Line 251-264 enforces $v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$ with $v_{\text{start}}[t] \in [0, 1]$.
