# `w_stop` REMOVAL CONSISTENCY AUDIT

## VERIFICATION OF MODEL INTEGRITY WITHOUT `w_stop`

1. **Transition Equation**: Retains baseline inequality $v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$.
2. **Transition Check**:
   - $0 \to 1$ (Startup): $v_{\text{start}} - 1 + 0 \ge 0 \implies v_{\text{start}} \ge 1 \implies v_{\text{start}} = 1$ (Startup cost incurred).
   - $1 \to 0$ (Shutdown): $v_{\text{start}} - 0 + 1 \ge 0 \implies v_{\text{start}} \ge -1 \implies v_{\text{start}} = 0$ (Zero startup cost incurred).
3. **Shutdown Event Reporting**: Post-solve derived reporting quantity $\text{shutdown}[t] = \max(0, u_{t-1} - u_t)$.
4. **Conclusion**: Model is 100% mathematically valid without `w_stop`. Zero dangling references or transition loopholes.

```text
W_STOP_REMOVAL = VALID
```
