# J3 Startup Audit

Startup tracking constraint formulation (lines 220-228):
$$v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$$
- For $t=0$: $v_{\text{start}}[0] - u_{\text{diesel}}[0] \ge -\text{initial\_diesel\_running}$.
- Removal of $w_{\text{stop}}$ did not affect startup tracking $v_{\text{start}}$, preserving valid physical commitment logic without unnecessary shutdown variables.

`J3_STARTUP = PASS`
