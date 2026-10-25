# `w_stop` FORENSIC AUDIT

## MATHEMATICAL AUDIT OF THE 24 PROPOSED `w_stop` BINARY VARIABLES

1. **Objective Relevance**:
   - $J_1$ (Critical Reliability): Does NOT contain `w_stop`.
   - $J_2$ (Emergency Reserve): Does NOT contain `w_stop`.
   - $J_3$ (Diesel Fuel Liters): $\min J_3 = \sum (F_{\text{marg}} P_{\text{diesel}} + F_{\text{base}} u_{\text{diesel}} + F_{\text{start}} v_{\text{start}}) \Delta t$. Does NOT contain shutdown cost/fuel!
   - $J_4$ (Renewable Curtailment): Does NOT contain `w_stop`.
   - Option D Policy: Does NOT penalize or constrain shutdown events.
2. **Transition Dynamics**:
   - The base model inequality $v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$ correctly enforces $v_{\text{start}}[t] = 1$ on startup ($0 \to 1$) and $v_{\text{start}}[t] = 0$ on shutdown ($1 \to 0$) under cost minimization.
   - Shutdown transitions ($1 \to 0$) are fully permitted mathematically without `w_stop`.
3. **Conclusion**: `w_stop` is **NOT_REQUIRED** for optimization. Retaining 24 unnecessary binary variables inflates the MILP branch-and-bound search space from $2^{96}$ to $2^{120}$ with zero mathematical or policy benefit.

```text
W_STOP_STATUS = NOT_REQUIRED
W_STOP_MINIMUM_COUNT = 0
```
