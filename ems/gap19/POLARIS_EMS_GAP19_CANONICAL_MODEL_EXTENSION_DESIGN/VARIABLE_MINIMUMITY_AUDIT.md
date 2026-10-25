# VARIABLE MINIMUMITY AUDIT

## JUSTIFICATION AND MINIMUMITY AUDIT FOR NEW VARIABLES

Every proposed new variable has been evaluated against the strict minimumity rule:

1. **$w_{\text{stop}}(t)$ (24 binaries)**: Required to enforce exact, non-ambiguous diesel shutdown transitions ($u_t - u_{t-1} - v_{\text{start,t}} + w_{\text{stop,t}} = 0$). Without $w_{\text{stop}}$, shutdown costs/events cannot be tracked cleanly.
2. **$P_{\text{unmet,crit}}(t)$ (24 continuous)**: Required for $J_1$ critical load deficit objective. Cannot reuse total $P_{\text{unmet}}$ because total demand includes flexible and non-critical loads.
3. **$s_{\text{EBR}}(t)$ (24 continuous)**: Required for $J_2$ Stage-2 shortfall linearization. In MILP, $\max(0, E_{\text{target}} - E)$ cannot be represented without non-negative auxiliary slacks.
4. **$s_{\text{term}}$ (1 continuous)**: Required for $J_2$ terminal reserve shortfall linearization.

`MINIMUMITY_AUDIT` = `PASS`
