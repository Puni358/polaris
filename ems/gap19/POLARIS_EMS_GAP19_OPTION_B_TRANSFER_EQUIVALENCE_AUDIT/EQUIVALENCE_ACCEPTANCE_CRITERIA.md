# EQUIVALENCE ACCEPTANCE CRITERIA

## Classification Categories for Equivalence Evaluation

This document defines the 4 distinct equivalence classification tiers for future test evaluation.

---

## Equivalence Classification Tiers

| Classification Tier | Definition & Numerical Criteria | Acceptance Status for Promotion |
| :--- | :--- | :--- |
| **`MATHEMATICAL_EXACT_EQUIVALENCE`** | Identical mathematical optimization problem with identical optimal objective values and optimal objective set. (Does not require identical decision vectors under primal degeneracy). | **Mathematically Exact** |
| **`NUMERICAL_DECISION_VECTOR_MATCH`** | Decision vectors match within provisional engineering test threshold ($\|x_A - x_B\|_\infty \le \varepsilon_x$, where $\varepsilon_x = 10^{-5}$ is a `PROVISIONAL_TEST_THRESHOLD`). | **Provisional Test Threshold Match** |
| **`OBJECTIVE_EQUIVALENCE`** | Decision vectors differ ($x_A \neq x_B$) due to primal degeneracy, but objective vectors match exactly ($J_{k,A} = J_{k,B} \; \forall k$) and both solutions are 100% feasible. | **Accepted for Promotion** |
| **`TOLERANCE_EQUIVALENCE`** | Objective vector differences fall within explicitly governed tolerances ($|J_{k,A} - J_{k,B}| \le \varepsilon_k$). | **Accepted subject to Engineering Sign-off** |
| **`NON_EQUIVALENT`** | Any higher-priority objective outcome differs beyond tolerance ($J_{1,A} \neq J_{1,B}$ or $J_{2,A} \neq J_{2,B}$), or priority lock is violated. | **REJECTED — Option B Promotion Blocked** |

---

## Technical Safeguard

The finite threshold $10^{-5}$ is explicitly classified as a **provisional engineering test configuration**, NOT mathematical exactness. Actual POLARIS A-vs-B equivalence remains `NOT_YET_TESTED`.
