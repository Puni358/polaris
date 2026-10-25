# OBJECTIVE DIRECTION AUDIT

## Objective Coefficient Sign & Sense Verification

This document verifies the coefficient signs and minimization sense for each objective in the HiGHS multi-objective formulation.

---

## Coefficient Direction Matrix

In HiGHS C++, linear objectives are solved in **minimization sense** ($\min c_k^T x$).

| Objective | Physical Quantity | Desired Operational Goal | Mathematical Form | Coefficient Sign in HiGHS Vector $c_k$ |
| :--- | :--- | :--- | :--- | :--- |
| **$J_1$ (Stage 1)** | Unmet critical load | Minimize unmet energy | $\min \sum P_{\text{unmet}} \Delta t$ | **Positive** ($+1.0 \cdot \Delta t$ at `p_unmet`) |
| **$J_2$ (Stage 2)** | Reserve shortfall | Minimize reserve deficit | $\min \sum s_{\text{EBR}} + s_{\text{term}}$ | **Positive** ($+1.0$ at `s_EBR` and `s_term` slacks) |
| **$J_3$ (Stage 3)** | Fuel consumption | Minimize fuel volume | $\min \sum F_{\text{diesel}} \Delta t$ | **Positive** ($+F_{\text{marg}} \Delta t$, $+F_{\text{base}} \Delta t$, $+F_{\text{start}}$) |
| **$J_4$ (Stage 4)** | Renewable curtailment | Minimize curtailed energy | $\min \sum P_{\text{curt}} \Delta t$ | **Positive** ($+1.0 \cdot \Delta t$ at `p_curt_sol` & `p_curt_wind`) |

---

## Technical Finding

All four GAP19 objectives naturally formulate as **positive cost vectors minimized by HiGHS**. Zero sign flips or artificial negative transformations are required.
