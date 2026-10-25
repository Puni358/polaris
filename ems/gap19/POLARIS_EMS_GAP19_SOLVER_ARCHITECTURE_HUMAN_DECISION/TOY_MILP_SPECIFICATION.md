# TOY MILP SPECIFICATION

## Analytical Specification of Synthetic Benchmark Problem

This document provides the analytical specification for an isolated, synthetic toy MILP problem designed to distinguish strict lexicographic optimization from weighted-sum optimization.

---

## Toy MILP Problem Definition

### Decision Variables
- $x_1 \in \{0, 1, 2, 3, 4, 5\}$ (Integer variable)
- $x_2 \in [0.0, 10.0]$ (Continuous variable)

### Feasibility Constraints
1. $2 x_1 + x_2 \le 10.0$
2. $x_1 + 3 x_2 \le 15.0$
3. $x_1 \ge 0, \, x_2 \ge 0$

### Lexicographic Objectives
- **Primary Objective $J_1(x_1, x_2)$** (Priority 1):
  $$\text{Minimize } J_1 = -x_1$$
- **Secondary Objective $J_2(x_1, x_2)$** (Priority 2):
  $$\text{Minimize } J_2 = -x_2$$

---

## Analytical Lexicographic Solution

1. **Pass 1 (Maximize $x_1$)**:
   - Subject to $2 x_1 + x_2 \le 10.0$, integer $x_1 \in [0, 5]$.
   - Maximum integer value $x_1^* = 5$.
   - At $x_1^* = 5$, constraint 1 gives $2(5) + x_2 \le 10 \implies x_2 \le 0 \implies x_2 = 0$.
   - Optimal $J_1^* = -5.0$.

2. **Pass 2 (Lock $x_1 = 5$, Maximize $x_2$)**:
   - Feasible set locked to $x_1 = 5$.
   - Maximum feasible $x_2 = 0.0$.
   - Optimal $J_2^* = 0.0$.

### Analytical Lexicographic Result:
$$(x_1^*, x_2^*) = (5, 0.0), \quad J_1^* = -5.0, \quad J_2^* = 0.0$$

---

## Comparison with Weighted-Sum (Blended) Solution

If objectives were blended into a weighted sum $\min (-x_1 - 2 x_2)$:
- At $(5, 0)$, weighted objective is $-5$.
- At $(0, 5)$, $2(0) + 5 \le 10$ and $3(5) = 15 \le 15$. Weighted objective is $-10$.
- Blended mode selects $(0, 5)$, whereas strict lexicographic mode MUST select $(5, 0)$.
