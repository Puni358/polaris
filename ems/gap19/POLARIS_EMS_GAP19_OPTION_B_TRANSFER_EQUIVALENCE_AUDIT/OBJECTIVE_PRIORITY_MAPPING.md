# OBJECTIVE PRIORITY MAPPING

## Priority Mapping to Native HiGHS Priority Values

This document defines the exact integer priority values assigned to $J_1, J_2, J_3, J_4$ in `highspy`.

---

## Governed Priority Mapping

The isolated native HiGHS validation empirically established that:

$$\text{LOWER_HIGHS_PRIORITY_NUMBER} = \text{HIGHER_POLARIS_PRIORITY_STAGE}$$

| POLARIS Stage | Governed Priority Description | Native HiGHS Objective Priority (`HighsLinearObjective.priority`) | Processing Order |
| :--- | :--- | :--- | :--- |
| **Stage 1 ($J_1$)** | Critical Load Reliability | `priority = 1` | Solved **FIRST** |
| **Stage 2 ($J_2$)** | Emergency Battery Reserve (EBR) | `priority = 2` | Solved **SECOND** |
| **Stage 3 ($J_3$)** | Governed Diesel Fuel Conservation | `priority = 3` | Solved **THIRD** |
| **Stage 4 ($J_4$)** | Avoidable Renewable Curtailment | `priority = 4` | Solved **FOURTH** |

---

## Enforcement Verification

Setting $1 < 2 < 3 < 4$ strictly guarantees that Stage 1 is fully optimized before Stage 2, Stage 2 before Stage 3, and Stage 3 before Stage 4.
