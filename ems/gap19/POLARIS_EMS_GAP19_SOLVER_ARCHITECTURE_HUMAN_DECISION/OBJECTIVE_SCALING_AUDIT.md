# OBJECTIVE SCALING AUDIT

## Unit Scaling & Dimensional Analysis

This document evaluates the physical unit dimensional scaling requirements across GAP19 objectives:

- **Stage 1 (Critical Reliability)**: Watt-hours ($\text{Wh}$)
- **Stage 2 (Battery Reserve / EBR)**: Watt-hours ($\text{Wh}$)
- **Stage 3 (Governed Fuel)**: Liters ($\text{L}$)
- **Stage 4 (Avoidable Curtailment)**: Watt-hours ($\text{Wh}$)

---

## Unit Scaling Analysis

1. **Lexicographic Isolation**: Because lexicographic optimization solves objectives in strict sequential order rather than adding them together, **physical unit normalization is NOT required to prevent cross-unit distortion**.
2. **Option A Scaling Impact**: In Option A, Stage 1 ($J_1$ in $\text{Wh}$) is solved first. Its lock $J_1(x) \le J_1^* + \varepsilon_1$ is expressed in $\text{Wh}$. Stage 3 ($J_3$ in Liters) is solved in Pass 3. Because $J_1$ and $J_3$ are never added into a single cost function, no artificial dollar conversion or unit weighting factor is needed.
3. **Option B Scaling Impact**: Native lexicographic optimization in HiGHS similarly keeps priorities separated during sequential solving. However, if `blend_multi_objectives` is accidentally enabled, different physical units ($\text{Wh}$ vs $\text{L}$) would be directly added together, causing severe dimensional corruption. Strict lexicographic enforcement is required.
