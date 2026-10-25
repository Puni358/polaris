# PROPORTIONAL ALLOCATION ARCHITECTURE

## 1. D4 MINIMUM VIABLE & PROPORTIONAL ALLOCATION FORMULATION

Governance DEC-004 D4 requires:
> "Maintain every protected critical system at or above its engineering-defined minimum viable operating level whenever possible. If available power is insufficient: proportionally allocate available power across protected critical systems. Do NOT invent a fixed priority such as heating > water > communications."

---

## 2. MATHEMATICAL ALLOCATION FORMULATION

Let $i \in \{\text{heating}, \text{water}, \text{comms}\}$ be the protected critical load categories.

Each category $i$ has an engineering minimum viable power level $P_{i,\text{min}}(t)$ (e.g. Heating = 15 kW, Water = 10 kW, Comms = 5 kW; total = 30 kW).

If total available power for critical load $P_{\text{avail,crit}}[t] < \sum_i P_{i,\text{min}}(t)$, the available power ratio is defined as:

$$\alpha[t] = \frac{P_{\text{avail,crit}}[t]}{\sum_i P_{i,\text{min}}(t)} \in [0, 1)$$

The power allocated to each category $i$ is constrained by a linear equality:

$$P_{i,\text{served}}[t] = \alpha[t] \cdot P_{i,\text{min}}(t) \quad \forall i$$

---

## 3. MILP IMPLEMENTATION VIA LINEAR EQUALITY CONSTRAINTS

In the solver, linear equality constraints tie each category's served power ratio to a common scalar decision variable $\alpha[t] \in [0, 1]$:

$$\begin{aligned}
P_{\text{heating,served}}[t] - \alpha[t] \cdot P_{\text{heating,min}}[t] &= 0 \\
P_{\text{water,served}}[t] - \alpha[t] \cdot P_{\text{water,min}}[t] &= 0 \\
P_{\text{comms,served}}[t] - \alpha[t] \cdot P_{\text{comms,min}}[t] &= 0
\end{aligned}$$

This strictly enforces equal proportional degradation across all protected critical loads without imposing artificial fixed priorities (such as heating > water > comms).
