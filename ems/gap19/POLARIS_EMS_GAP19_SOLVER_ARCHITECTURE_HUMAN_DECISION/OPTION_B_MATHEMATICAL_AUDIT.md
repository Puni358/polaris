# OPTION B MATHEMATICAL AUDIT

## Mathematical Formulation of Native Multi-Objective MILP Optimization

This document provides the formal mathematical formulation for **Option B**.

---

## Native Multi-Objective Formulation

Let $\mathcal{F}_0 = \{ x \in \mathbb{R}^n \mid A x \le b, \, x_j \in \mathbb{Z} \; \forall j \in \mathcal{I} \}$ be the initial system feasible region.

The native multi-objective problem is defined as the ordered tuple of objectives:

$$\min_{x \in \mathcal{F}_0} \mathbf{J}(x) = \left( J_1(x), J_2(x), J_3(x), J_4(x) \right)$$

with priority vector $p = (1, 2, 3, 4)$ and tolerance vector $\mathbf{\varepsilon} = (\varepsilon_1, \varepsilon_2, \varepsilon_3, \varepsilon_4)$.

---

## Solver Internal Execution Model

Internal C++ algorithm in HiGHS executes sequential sub-problems:

$$\text{Step } k: \quad \min_{x \in \mathcal{S}_{k-1}} c_k^T x$$
$$\text{where } \mathcal{S}_k = \left\{ x \in \mathcal{S}_{k-1} \mid c_k^T x \le z_k^* + \text{abs\_tol}_k + \text{rel\_tol}_k \cdot |z_k^*| \right\}$$
$$\mathcal{S}_0 = \mathcal{F}_0$$

---

## Equivalence Conditions

Option B is **mathematically equivalent** to Option A if and only if:
1. Native solver option `blend_multi_objectives` is set to `False`.
2. Priorities $p_1 < p_2 < p_3 < p_4$ are strictly distinct integers.
3. Native tolerances $(\text{abs\_tol}_k, \text{rel\_tol}_k)$ match POLARIS lock values $(\varepsilon_k)$.
4. Presolve and MIP solver settings are identical across both modes.
