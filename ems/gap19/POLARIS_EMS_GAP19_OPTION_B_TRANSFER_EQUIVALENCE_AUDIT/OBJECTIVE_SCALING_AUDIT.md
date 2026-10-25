# OBJECTIVE SCALING AUDIT

## Physical Unit Dimensional Scaling Audit

This document evaluates the physical unit dimensional scaling requirements across $J_1, J_2, J_3, J_4$.

---

## Dimensional Audit Matrix

| Stage | Governed Objective | Physical Unit | Magnitude Range (Synthetic Benchmark) | Scaling Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1 ($J_1$)** | Critical Unmet Load | Watt-hours ($\text{Wh}$) | $0.0\text{--}100,000\text{ Wh}$ | None (Strict priority isolation) |
| **Stage 2 ($J_2$)** | Reserve Deficit / EBR | Watt-hours ($\text{Wh}$) | $0.0\text{--}50,000\text{ Wh}$ | None (Strict priority isolation) |
| **Stage 3 ($J_3$)** | Diesel Fuel | Liters ($\text{L}$) | $0.0\text{--}500.0\text{ L}$ | None (Strict priority isolation) |
| **Stage 4 ($J_4$)** | Curtailment | Watt-hours ($\text{Wh}$) | $0.0\text{--}100,000\text{ Wh}$ | None (Strict priority isolation) |

---

## Technical Finding

Because HiGHS multi-objective lexicographic mode (`blend_multi_objectives = False`) solves objectives sequentially in separate priority passes, **physical unit scaling coefficients are NOT required**. $\text{Wh}$ and Liters are never added together in any objective vector.
