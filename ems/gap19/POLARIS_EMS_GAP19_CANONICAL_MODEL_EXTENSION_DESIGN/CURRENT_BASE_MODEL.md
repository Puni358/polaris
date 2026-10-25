# CURRENT BASE MODEL RECONSTRUCTION

## IMMUTABLE BASELINE: PRODUCTION `milp.py` (360 VARIABLES, 264 CONSTRAINTS)

- **Source File**: `system/optimization/implementations/milp.py`
- **Horizon $H$**: 24 hours ($t \in \{0, \dots, 23\}$)
- **Time step $\Delta t$**: 1.0 hour
- **Base Decision Variables ($N_{\text{base}}$)**: 360 ($24 \times 15$ variables per timestep)
  - Continuous variables: 264
  - Binary variables: 96 ($u_{\text{chg}}, u_{\text{dis}}, u_{\text{diesel}}, v_{\text{start}}$)
- **Base Linear Constraints ($M_{\text{base}}$)**: 264 linear constraints ($11 \times 24$)
  1. Solar Decomposition ($p_{\text{sol\_used}} + p_{\text{curt\_sol}} = P_{\text{solar}}$)
  2. Wind Decomposition ($p_{\text{wind\_used}} + p_{\text{curt\_wind}} = P_{\text{wind}}$)
  3. Bus-Bar Balance ($p_{\text{sol\_used}} + p_{\text{wind\_used}} + p_{\text{dis}} + p_{\text{diesel}} - p_{\text{served}} - p_{\text{chg}} - p_{\text{flex}} = 0$)
  4. Demand Deficit Balance ($p_{\text{served}} + p_{\text{unmet}} = P_{\text{demand}}$)
  5. Charge Bound vs Binary ($p_{\text{chg}} - P_{\text{chg,max}} u_{\text{chg}} \le 0$)
  6. Discharge Bound vs Binary ($p_{\text{dis}} - P_{\text{dis,max}} u_{\text{dis}} \le 0$)
  7. Exclusivity Bound ($u_{\text{chg}} + u_{\text{dis}} \le 1$)
  8. Energy Transition ($E[t+1] - E[t] - \eta_{\text{chg}} p_{\text{chg}} \Delta t + \frac{p_{\text{dis}}}{\eta_{\text{dis}}} \Delta t = 0$)
  9. Diesel Min Output ($p_{\text{diesel}} - P_{\text{diesel,min}} u_{\text{diesel}} \ge 0$)
  10. Diesel Max Output ($p_{\text{diesel}} - P_{\text{diesel,max}} u_{\text{diesel}} \le 0$)
  11. Diesel Startup Tracking ($v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$)
