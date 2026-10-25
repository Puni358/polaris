# OPTION A MATHEMATICAL AUDIT

## Mathematical Formulation of Sequential Lexicographic Locking

This document provides the formal mathematical formulation for **Option A**.

---

## Sequential Optimization Problems

Let $\mathcal{F}_0 = \{ x \in \mathbb{R}^n \mid A x \le b, \, x_j \in \mathbb{Z} \; \forall j \in \mathcal{I} \}$ be the initial system feasible region.

### Pass 1: Stage 1 Optimization (Critical Reliability)
$$\min_{x \in \mathcal{F}_0} J_1(x)$$
Obtain optimal value $J_1^*$. Define feasible region $\mathcal{F}_1$:
$$\mathcal{F}_1 = \{ x \in \mathcal{F}_0 \mid J_1(x) \le J_1^* + \varepsilon_1 \}$$

### Pass 2: Stage 2 Optimization (Battery Reserve / EBR)
$$\min_{x \in \mathcal{F}_1} J_2(x)$$
Obtain optimal value $J_2^*$. Define feasible region $\mathcal{F}_2$:
$$\mathcal{F}_2 = \{ x \in \mathcal{F}_1 \mid J_2(x) \le J_2^* + \varepsilon_2 \}$$

### Pass 3: Stage 3 Optimization (Governed Fuel)
$$\min_{x \in \mathcal{F}_2} J_3(x)$$
Obtain optimal value $J_3^*$. Define feasible region $\mathcal{F}_3$:
$$\mathcal{F}_3 = \{ x \in \mathcal{F}_2 \mid J_3(x) \le J_3^* + \varepsilon_3 \}$$

### Pass 4: Stage 4 Optimization (Avoidable Curtailment)
$$\min_{x \in \mathcal{F}_3} J_4(x)$$
Obtain final solution vector $x^*$.

---

## Mathematical Guarantees

1. **Monotonic Feasibility**: $\mathcal{F}_0 \supseteq \mathcal{F}_1 \supseteq \mathcal{F}_2 \supseteq \mathcal{F}_3$.
2. **Lock Representation**: Each lock constraint $J_k(x) \le J_k^* + \varepsilon_k$ is a linear constraint $c_k^T x \le J_k^* + \varepsilon_k$, which preserves MILP linearity.
