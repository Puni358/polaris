# OBJECTIVE VECTOR SPECIFICATION

## SYMBOLIC COEFFICIENT VECTORS FOR HIGHS OPTIMIZATION

1. **$c_1$ ($J_1$ Critical Reliability)**:
   - Nonzeros: $c_1[idx(P_{\text{unmet,crit}}, t)] = 1.0 \cdot \Delta t$ ($\text{Wh}$)
2. **$c_2$ ($J_2$ Reserve Shortfall)**:
   - Nonzeros: $c_2[idx(s_{\text{EBR}}, t)] = 1.0$, $c_2[idx(s_{\text{term}})] = 1.0$ ($\text{Wh}$)
3. **$c_3$ ($J_3$ Diesel Fuel Liters)**:
   - Nonzeros: $c_3[idx(P_{\text{diesel}}, t)] = F_{\text{marg}} \Delta t$, $c_3[idx(u_{\text{diesel}}, t)] = F_{\text{base}} \Delta t$, $c_3[idx(v_{\text{start}}, t)] = F_{\text{start}}$ ($\text{L}$)
4. **$c_4$ ($J_4$ Avoidable Curtailment)**:
   - Nonzeros: $c_4[idx(P_{\text{pv,curt}}, t)] = 1.0 \cdot \Delta t$, $c_4[idx(P_{\text{wind,curt}}, t)] = 1.0 \cdot \Delta t$ ($\text{Wh}$)
