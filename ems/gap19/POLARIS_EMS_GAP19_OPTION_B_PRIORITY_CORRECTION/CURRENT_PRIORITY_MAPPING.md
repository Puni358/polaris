# Current Priority Semantics & Mapping

## POLARIS Stage Mapping

The table below contrasts the intended POLARIS hierarchy against the actual HiGHS effective execution order produced by `gap19_highs_native.py`:

| POLARIS Stage | Physical Objective | Intended Hierarchy | Current Code Priority | HiGHS Effective Order | Enforced Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **J1** | Critical Deficit (Wh) | 1st (Highest) | `1` | **4th (Lowest)** | **FAILED** |
| **J2** | EBR Reserve Shortfall (Wh) | 2nd | `2` | **3rd** | **FAILED** |
| **J3** | Diesel Fuel (Liters) | 3rd | `3` | **2nd** | **FAILED** |
| **J4** | Renewable Curtailment (Wh) | 4th (Lowest) | `4` | **1st (Highest)** | **FAILED** |

## Lexicographic Priority Inversion Proof

- **Intended Hierarchy**: $J_1 > J_2 > J_3 > J_4$
- **HiGHS Execution Order (Current Code)**: Priority `4` ($J_4$) $\to$ Priority `3` ($J_3$) $\to$ Priority `2` ($J_2$) $\to$ Priority `1` ($J_1$)
- **Effective Hierarchy**: $J_4 > J_3 > J_2 > J_1$

**Conclusion**: The current code executes the objective hierarchy in **exact reverse order**. $J_1 > J_2 > J_3 > J_4$ is **NOT** enforced.
