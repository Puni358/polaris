# OPTION A REFERENCE FORMULATION

## Pure Mathematical Specification of Reference Implementation

This document provides the mathematical specification for **Option A** as a reference implementation against which Option B will be evaluated.

---

## Reference Pass Sequence

Let $\mathcal{F}_0 = \{ x \in \mathbb{R}^n \mid A x \le b, \, x_j \in \mathbb{Z} \; \forall j \in \mathcal{I} \}$ be the system feasible region.

### Pass 1: Stage 1 (Critical Reliability)
$$\min_{x \in \mathcal{F}_0} J_1(x)$$
Obtain $J_1^*$. Define $\mathcal{F}_1 = \{ x \in \mathcal{F}_0 \mid J_1(x) \le J_1^* + \varepsilon_1 \}$ ($\varepsilon_1 = 0.0\text{ Wh}$).

### Pass 2: Stage 2 (Emergency Battery Reserve / EBR)
$$\min_{x \in \mathcal{F}_1} J_2(x)$$
Obtain $J_2^*$. Define $\mathcal{F}_2 = \{ x \in \mathcal{F}_1 \mid J_2(x) \le J_2^* + \varepsilon_2 \}$ ($\varepsilon_2 = 0.0\text{ Wh}$).

### Pass 3: Stage 3 (Governed Diesel Fuel Conservation)
$$\min_{x \in \mathcal{F}_2} J_3(x)$$
Obtain $J_3^*$. Define $\mathcal{F}_3 = \{ x \in \mathcal{F}_2 \mid J_3(x) \le J_3^* + \varepsilon_3 \}$ ($\varepsilon_3 = 0.01\text{ L}$).

### Pass 4: Stage 4 (Avoidable Renewable Curtailment)
$$\min_{x \in \mathcal{F}_3} J_4(x)$$
Obtain final decision vector $x_A^*$.

---

## Technical Audit Status

```text
OPTION_A_REFERENCE = DEFINED
```
Option A is fully defined as a pure mathematical reference formulation.
