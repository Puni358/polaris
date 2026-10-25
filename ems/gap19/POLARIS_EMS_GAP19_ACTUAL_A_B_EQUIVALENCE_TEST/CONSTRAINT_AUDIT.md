# CONSTRAINT AUDIT

## LINEAR CONSTRAINTS AUDIT (265 CONSTRAINTS)

1. **Power Balance (24 Equalities)**:
   $$P_{\text{diesel}}(t) + P_{\text{batt,dis}}(t) + P_{\text{pv,use}}(t) + P_{\text{wind,use}}(t) + P_{\text{unmet}}(t) - P_{\text{batt,ch}}(t) = P_{\text{load}}(t)$$
2. **Diesel Min Power Bound (24 Inequalities)**:
   $$P_{\text{diesel}}(t) - 1000 u_{\text{diesel}}(t) \ge 0$$
3. **Diesel Max Power Bound (24 Inequalities)**:
   $$P_{\text{diesel}}(t) - 5000 u_{\text{diesel}}(t) \le 0$$
4. **Diesel Commitment Transitions (24 Equalities)**:
   $$u_{\text{diesel}}(t) - u_{\text{diesel}}(t-1) - v_{\text{start}}(t) + w_{\text{stop}}(t) = 0$$
5. **Battery Charge Power Bound (24 Inequalities)**:
   $$P_{\text{batt,ch}}(t) - 2500 u_{\text{ch}}(t) \le 0$$
6. **Battery Discharge Power Bound (24 Inequalities)**:
   $$P_{\text{batt,dis}}(t) - 2500 u_{\text{dis}}(t) \le 0$$
7. **Battery Charge/Discharge Exclusivity (24 Inequalities)**:
   $$u_{\text{ch}}(t) + u_{\text{dis}}(t) \le 1$$
8. **Energy Storage Dynamics (24 Equalities)**:
   $$E_{\text{batt}}(t) - E_{\text{batt}}(t-1) - 0.95 P_{\text{batt,ch}}(t) \Delta t + \frac{1}{0.95} P_{\text{batt,dis}}(t) \Delta t = 0$$
9. **Solar Generation Balance (24 Equalities)**:
   $$P_{\text{pv,use}}(t) + P_{\text{pv,curt}}(t) = P_{\text{pv,avail}}(t)$$
10. **Wind Generation Balance (24 Equalities)**:
    $$P_{\text{wind,use}}(t) + P_{\text{wind,curt}}(t) = P_{\text{wind,avail}}(t)$$
11. **Emergency Battery Reserve Relation (24 Inequalities)**:
    $$E_{\text{batt}}(t) + s_{\text{EBR}}(t) \ge 3000$$
12. **Terminal Energy Relation (1 Inequality)**:
    $$E_{\text{batt}}(23) + s_{\text{term}} \ge 5000$$

`CONSTRAINT_IDENTITY_A_B` = `PASS`
