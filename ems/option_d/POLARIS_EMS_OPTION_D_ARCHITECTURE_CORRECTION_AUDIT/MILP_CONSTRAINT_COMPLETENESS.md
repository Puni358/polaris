# MILP CONSTRAINT COMPLETENESS

## 1. ENUMERATED 20 LINEAR CONSTRAINT SET FOR OPTION D

The audit enumerated the complete 20 linear constraint types required per timestep $t \in \{0 \dots 23\}$ under the 21-variable formulation:

1. **Solar Generation Decomposition**: $P_{\text{sol,crit}} + P_{\text{sol,flex}} + P_{\text{chg,sol}} + P_{\text{curt,sol}} = P_{\text{sol,gen}}$
2. **Wind Generation Decomposition**: $P_{\text{wind,crit}} + P_{\text{wind,flex}} + P_{\text{chg,wind}} + P_{\text{curt,wind}} = P_{\text{wind,gen}}$
3. **Total Diesel Output Decomposition**: $P_{\text{dies,crit}} + P_{\text{dies,flex}} = P_{\text{diesel}}$
4. **Critical Load Busbar Balance**: $P_{\text{serv,crit}} = P_{\text{sol,crit}} + P_{\text{wind,crit}} + P_{\text{dis}} + P_{\text{dies,crit}}$
5. **Flexible Load Busbar Balance**: $P_{\text{serv,flex}} = P_{\text{sol,flex}} + P_{\text{wind,flex}} + P_{\text{dies,flex}}$ *(zero $P_{\text{dis}}$ allowed)*
6. **Critical Load Deficit Balance**: $P_{\text{serv,crit}} + P_{\text{unm,crit}} = P_{\text{critical\_requested}}$
7. **Flexible Load Deficit Balance**: $P_{\text{serv,flex}} + P_{\text{unm,flex}} = P_{\text{flexible\_requested}}$
8. **Battery Charge Decomposition**: $P_{\text{chg}} = P_{\text{chg,ren}} + P_{\text{chg,ex}}$
9. **Battery Charge Power Bound**: $P_{\text{chg}} - P_{\text{chg,max}} u_{\text{chg}} \le 0$
10. **Battery Discharge Power Bound**: $P_{\text{dis}} - P_{\text{dis,max}} u_{\text{dis}} \le 0$
11. **Battery Exclusivity**: $u_{\text{chg}} + u_{\text{dis}} \le 1$
12. **Battery Discrete Energy Transition**: $E[t+1] - E[t] - \eta_{\text{chg}} P_{\text{chg}} \Delta t + \frac{P_{\text{dis}}}{\eta_{\text{dis}}} \Delta t = 0$
13. **Diesel Minimum Output when Running**: $P_{\text{diesel}} - P_{\text{dies,min}} u_{\text{diesel}} \ge 0$
14. **Diesel Maximum Output when Running**: $P_{\text{diesel}} - P_{\text{dies,max}} u_{\text{diesel}} \le 0$
15. **Diesel Startup Tracking**: $v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$
16. **D6 Diesel Requirement Firewall**: $u_{\text{diesel}}[t] \le \text{M} \cdot (P_{\text{critical}} - P_{\text{ren,gen}} - P_{\text{dis,max}})_+$
17. **D6 Diesel Excess Battery Charging Allocation**: $P_{\text{chg,ex}} \ge \min(P_{\text{excess}}, P_{\text{chg,max}})$ when $u_{\text{diesel}}=1$
18. **D4 Proportional Allocation Equality**: $P_{i,\text{serv,crit}} - \alpha P_{i,\text{min}} = 0 \quad \forall i$
19. **Option D Noncritical Shedding**: $P_{\text{serv,flex}} \le \text{M} \cdot \mathbf{1}_{\text{NORMAL}}$
20. **Fuel Inventory Depletion Tracking**: $V_{\text{fuel}}[t+1] - V_{\text{fuel}}[t] + \left(F_{\text{base}} u_{\text{diesel}} + F_{\text{marg}} P_{\text{diesel}}\right) \Delta t = 0$
