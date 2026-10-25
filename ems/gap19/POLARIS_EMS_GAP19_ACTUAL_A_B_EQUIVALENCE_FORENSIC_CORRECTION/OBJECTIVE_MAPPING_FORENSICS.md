# OBJECTIVE MAPPING FORENSICS

## GOVERNED TARGET J1-J4 VS HISTORICAL PRODUCTION COST FUNCTION

- **Historical Production `milp.py` Objective**:
  $$\min \text{cost} = \sum \left( c_{\text{fuel}} P_{\text{diesel}} + c_{\text{startup}} v_{\text{start}} + c_{\text{deg}} (P_{\text{chg}} + P_{\text{dis}}) + c_{\text{curt}} P_{\text{curt}} + c_{\text{unmet}} P_{\text{unmet}} \right) \Delta t$$
- **GAP19 Governed Target Multi-Objective**:
  - $J_1 = \sum P_{\text{unmet}} \Delta t$ (Priority 1)
  - $J_2 = \sum s_{\text{EBR}} + s_{\text{term}}$ (Priority 2)
  - $J_3 = \sum (0.00025 P_{\text{diesel}} + 5.0 u_{\text{diesel}} + 6.0 v_{\text{start}}) \Delta t$ (Priority 3)
  - $J_4 = \sum (P_{\text{pv,curt}} + P_{\text{wind,curt}}) \Delta t$ (Priority 4)

The equivalence experiment evaluated the GAP19 Governed Target Multi-Objective $[J_1, J_2, J_3, J_4]$, not the scalar cost function.
