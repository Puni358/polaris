# INTEGRALITY AUDIT

## INTEGRALITY CLASSIFICATION AUDIT

- **Total Binary Variables**: 120
  - Diesel Commitment $u_{\text{diesel}}(t)$ ($t=0..23$)
  - Diesel Startup $v_{\text{start}}(t)$ ($t=0..23$)
  - Diesel Shutdown $w_{\text{stop}}(t)$ ($t=0..23$)
  - Battery Charge Mode $u_{\text{ch}}(t)$ ($t=0..23$)
  - Battery Discharge Mode $u_{\text{dis}}(t)$ ($t=0..23$)
- **Total Continuous Variables**: 265

Both Option A (via SciPy `milp` `integrality` array) and Option B (via `highspy` `changeColIntegrality`) enforce the exact same integrality array.

`INTEGRALITY_IDENTITY_A_B` = `PASS`
