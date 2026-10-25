# PRODUCTION MILP CURRENT STATE AUDIT

## SOURCE FILE: `system/optimization/implementations/milp.py`

Independent line-by-line inspection of the actual current production file `system/optimization/implementations/milp.py` establishes the exact physical model dimensions:

- **Horizon $H$**: 24 hours (Line 72: `H = 24`)
- **Decision Variables per Timestep $K$**: 15 (Line 73: `K = 15`)
- **Total Variables**: $N = H \times K = 24 \times 15 = 360$ (Line 80: `num_vars = H * K`)
- **Binary Variables**: 96 (4 per timestep $\times 24$ steps: `u_chg`, `u_dis`, `u_diesel`, `v_start` at Lines 139-142)
- **Continuous Variables**: 264 ($360 - 96 = 264$)
- **Base Linear Constraints**: 264 (11 constraint types $\times 24$ steps at Lines 149-265)
  1. Solar Decomposition ($p_{\text{sol\_used}} + p_{\text{curt\_sol}} = p_{\text{solar\_gen}}$)
  2. Wind Decomposition ($p_{\text{wind\_used}} + p_{\text{curt\_wind}} = p_{\text{wind\_gen}}$)
  3. Bus-Bar Balance ($p_{\text{sol\_used}} + p_{\text{wind\_used}} + p_{\text{dis}} + p_{\text{diesel}} - p_{\text{served}} - p_{\text{chg}} - p_{\text{flex}} = 0$)
  4. Demand Deficit Balance ($p_{\text{served}} + p_{\text{unmet}} = p_{\text{demand}}$)
  5. Charge Bound vs Binary ($p_{\text{chg}} - \text{max\_p\_chg} \cdot u_{\text{chg}} \le 0$)
  6. Discharge Bound vs Binary ($p_{\text{dis}} - \text{max\_p\_dis} \cdot u_{\text{dis}} \le 0$)
  7. Charge/Discharge Exclusivity ($u_{\text{chg}} + u_{\text{dis}} \le 1$)
  8. Battery Energy Discrete Transition ($E[t+1] - E[t] - \eta_{\text{chg}} p_{\text{chg}} \Delta t + \frac{1}{\eta_{\text{dis}}} p_{\text{dis}} \Delta t = 0$)
  9. Diesel Min Output when Running ($p_{\text{diesel}} - \text{min\_diesel\_w} \cdot u_{\text{diesel}} \ge 0$)
  10. Diesel Max Output when Running ($p_{\text{diesel}} - \text{max\_diesel\_w} \cdot u_{\text{diesel}} \le 0$)
  11. Diesel Startup Tracking ($v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$)
- **Objective Structure**: Historical single scalar cost function combining fuel cost, startup cost, degradation penalty, curtailment penalty, and unmet load penalty (Lines 97-114).
