# CURRENT CONSTRAINT MAP

## COMPLETE LINEAR CONSTRAINT MAP FOR PRODUCTION `milp.py` (264 CONSTRAINTS)

For each timestep $t \in \{0, \dots, 23\}$, $11$ constraints are added (Lines 149-265):

| ID | Constraint Name | Mathematical Equation | Type | Source Lines |
|---|---|---|---|---|
| C1 | Solar Decomposition | $p_{\text{sol\_used}} + p_{\text{curt\_sol}} = P_{\text{pv,avail}}(t)$ | Equality | Lines 155-161 |
| C2 | Wind Decomposition | $p_{\text{wind\_used}} + p_{\text{curt\_wind}} = P_{\text{wind,avail}}(t)$ | Equality | Lines 163-169 |
| C3 | Bus-Bar Balance | $p_{\text{sol\_used}} + p_{\text{wind\_used}} + p_{\text{dis}} + p_{\text{diesel}} - p_{\text{served}} - p_{\text{chg}} - p_{\text{flex}} = 0$ | Equality | Lines 171-182 |
| C4 | Demand Deficit Balance | $p_{\text{served}} + p_{\text{unmet}} = P_{\text{demand}}(t)$ | Equality | Lines 184-190 |
| C5 | Charge Power Bound | $p_{\text{chg}} - P_{\text{chg,max}} u_{\text{chg}} \le 0$ | Inequality | Lines 192-198 |
| C6 | Discharge Power Bound | $p_{\text{dis}} - P_{\text{dis,max}} u_{\text{dis}} \le 0$ | Inequality | Lines 200-206 |
| C7 | Exclusivity Bound | $u_{\text{chg}} + u_{\text{dis}} \le 1$ | Inequality | Lines 208-214 |
| C8 | Energy Transition | $E[t+1] - E[t] - \eta_{\text{chg}} p_{\text{chg}} \Delta t + \frac{1}{\eta_{\text{dis}}} p_{\text{dis}} \Delta t = 0$ | Equality | Lines 216-233 |
| C9 | Diesel Min Output | $p_{\text{diesel}} - P_{\text{diesel,min}} u_{\text{diesel}} \ge 0$ | Inequality | Lines 235-241 |
| C10 | Diesel Max Output | $p_{\text{diesel}} - P_{\text{diesel,max}} u_{\text{diesel}} \le 0$ | Inequality | Lines 243-249 |
| C11 | Diesel Startup Tracking| $v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$ | Inequality | Lines 251-264 |
