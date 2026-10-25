# CURRENT OBJECTIVE AUDIT

## Deconstruction of Current Scalar Objective vs Governed Target

This document deconstructs the current scalar weighted objective function in [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) and contrasts it with the governed GAP19 4-stage hierarchy.

---

## Deconstruction Matrix

| Objective Component | Current Scalar Term in `milp.py` | Governed GAP19 Target Stage | Units | Transition Action |
| :--- | :--- | :--- | :--- | :--- |
| **Unmet Critical Load** | $c_9 = 10.0 \cdot \Delta t \cdot P_{\text{unmet}}$ | **Stage 1 (Critical Reliability)** | Watt-hours ($\text{Wh}$) | Extracted as $J_1$ primary objective vector. |
| **Battery Reserve Deficit / EBR** | Unrepresented (Uses static SOC bounds $E_{\text{min}}$) | **Stage 2 (Reserve Optimization / EBR)** | Watt-hours ($\text{Wh}$) | Formulated as Stage 2 linear objective using slack variables. |
| **Diesel Fuel Consumption** | $c_7 = 2.50 \cdot 0.00025 \cdot P_{\text{diesel}} + c_{13} = 2.50 \cdot 5.0 \cdot u_{\text{diesel}} + c_{14} = 15.0 \cdot v_{\text{start}}$ | **Stage 3 (Governed Fuel)** | Liters ($\text{L}$) | Combined into Stage 3 Liters fuel objective vector $J_3$. |
| **Renewable Curtailment** | $c_2, c_3 = 0.001 \cdot (P_{\text{curt,sol}} + P_{\text{curt,wind}})$ | **Stage 4 (Avoidable Curtailment)** | Watt-hours ($\text{Wh}$) | Formulated as Stage 4 curtailment minimization $J_4$. |
| **Battery Degradation Penalty** | $c_4, c_5 = 0.00005 \cdot (P_{\text{chg}} + P_{\text{dis}})$ | Unresolved (`GOVERNANCE_REQUIRED`) | Dollars / $\text{Wh}$ | Reclassified as open governance item; see degradation audit. |

---

## Architectural Finding

The current implementation combines all penalty terms into a single scalar dollar cost function via arbitrary numerical weights ($10.0, 2.50, 0.001, 0.00005$). GAP19 Option B replaces this scalar sum with 4 distinct `HighsLinearObjective` structures solved lexicographically by HiGHS.
