# GAP19 OBJECTIVE MAPPING

## Objective Hierarchy Mapping (Stages 1 to 4)

This document maps the four governed GAP19 EMS objective stages to solver representations under Option A and Option B.

---

## GAP19 Objective Hierarchy Mapping

| Stage # | Governed GAP19 Objective | Physical Unit | Option A Representation | Option B Representation |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | Critical Load Reliability ($D4$ Proportionality / Deficit Minimization) | Watt-hours ($\text{Wh}$) | **Pass 1 Objective**: Minimize $J_1(x)$. Lock $J_1(x) \le J_1^* + \varepsilon_1$. | **Priority 1 Objective**: `addLinearObjective(cost_j1, priority=1, abs_tol=eps1)` |
| **Stage 2** | Energy Buffer Ratio (EBR) / Terminal Reserve Target | Watt-hours ($\text{Wh}$) | **Pass 2 Objective**: Minimize $J_2(x)$ subject to Pass 1 lock. Lock $J_2(x) \le J_2^* + \varepsilon_2$. | **Priority 2 Objective**: `addLinearObjective(cost_j2, priority=2, abs_tol=eps2)` |
| **Stage 3** | Governed Fuel Optimization (Diesel Conservation & Starts) | Liters ($\text{L}$) | **Pass 3 Objective**: Minimize $J_3(x)$ subject to Pass 1 & 2 locks. Lock $J_3(x) \le J_3^* + \varepsilon_3$. | **Priority 3 Objective**: `addLinearObjective(cost_j3, priority=3, abs_tol=eps3)` |
| **Stage 4** | Renewable Capture / Avoidable Curtailment Minimization | Watt-hours ($\text{Wh}$) | **Pass 4 Objective**: Minimize $J_4(x)$ subject to Pass 1, 2 & 3 locks. | **Priority 4 Objective**: `addLinearObjective(cost_j4, priority=4, abs_tol=eps4)` |

---

## Governance Safeguards

1. Stage 2 numerical targets remain governed inputs and are **NOT** invented in this mapping.
2. Neither option modifies the relative hierarchy order ($1 \rightarrow 2 \rightarrow 3 \rightarrow 4$).
