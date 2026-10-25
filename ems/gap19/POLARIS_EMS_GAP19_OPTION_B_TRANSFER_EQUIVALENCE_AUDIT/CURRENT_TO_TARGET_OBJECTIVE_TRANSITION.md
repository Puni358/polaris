# CURRENT TO TARGET OBJECTIVE TRANSITION

## Transition Map: Current Scalar Objective Terms to GAP19 Target Objectives

This document maps every existing scalar cost term in `milp.py` to its corresponding target representation under GAP19 Option B.

---

## Transition Mapping Table

| Current Scalar Term in `milp.py` | Current Cost Coefficient | Target GAP19 Destination | Target Objective Representation | Status |
| :--- | :--- | :--- | :--- | :--- |
| `c[base + 9]` (`p_unmet`) | `10.0 * dt` ($/\text{Wh}$) | **Stage 1 ($J_1$)** | $\min \sum P_{\text{unmet}} \Delta t$ (`priority=1`) | Extracted |
| Static $E_{\text{min}}$ bound | Bounds constraint | **Stage 2 ($J_2$)** | $\min \sum s_{\text{EBR}} + s_{\text{term}}$ (`priority=2`) | Formulated |
| `c[base + 7]` (`p_diesel`) | `2.50 * 0.00025 * dt` | **Stage 3 ($J_3$)** | $\min \sum F_{\text{marg}} P_{\text{diesel}} \Delta t$ (`priority=3`) | Extracted |
| `c[base + 13]` (`u_diesel`) | `2.50 * 5.0 * dt` | **Stage 3 ($J_3$)** | $\min \sum F_{\text{base}} u_{\text{diesel}} \Delta t$ (`priority=3`) | Extracted |
| `c[base + 14]` (`v_start`) | `15.0 * 1.0` | **Stage 3 ($J_3$)** | $\min \sum F_{\text{start}} v_{\text{start}}$ (`priority=3`) | Extracted |
| `c[base + 2, 3]` (`p_curt`) | `0.001 * dt` | **Stage 4 ($J_4$)** | $\min \sum (P_{\text{curt,sol}} + P_{\text{curt,wind}}) \Delta t$ (`priority=4`) | Extracted |
| `c[base + 4, 5]` (`p_chg,dis`) | `0.00005 * dt` | **Unresolved** | Battery degradation stage placement (`GOVERNANCE_REQUIRED`) | Pending Governance |
