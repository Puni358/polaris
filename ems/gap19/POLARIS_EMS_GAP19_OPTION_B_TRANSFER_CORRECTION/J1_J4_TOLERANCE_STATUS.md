# J1-J4 TOLERANCE STATUS

## Authoritative Objective Tolerance Status Matrix

This document provides the authoritative tolerance status matrix across Stages $J_1, J_2, J_3, J_4$.

---

## Authoritative Tolerance Status Matrix

| Objective Stage | Physical Unit | Mathematical Tolerance ($\varepsilon_k$) | POLARIS Governance Status | Solver Tolerance Status | Numerical Comparison Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 ($J_1$)** | Watt-hours ($\text{Wh}$) | `unresolved` | `ENGINEERING_DEFINITION_REQUIRED` | `SOLVER_DEPENDENT` | `TEST_DEFINED` |
| **Stage 2 ($J_2$)** | Watt-hours ($\text{Wh}$) | `unresolved` | `ENGINEERING_DEFINITION_REQUIRED` | `SOLVER_DEPENDENT` | `TEST_DEFINED` |
| **Stage 3 ($J_3$)** | Liters ($\text{L}$) | `unresolved` | `ENGINEERING_DEFINITION_REQUIRED` | `SOLVER_DEPENDENT` | `TEST_DEFINED` ($0.01\text{ L}$ in toy test only) |
| **Stage 4 ($J_4$)** | Watt-hours ($\text{Wh}$) | `unresolved` | `ENGINEERING_DEFINITION_REQUIRED` | `SOLVER_DEPENDENT` | `TEST_DEFINED` |

---

## Audit Rule

No unresolved cell is populated with an invented number. The $0.01\text{ L}$ number is preserved purely as a historical test artifact and is explicitly labeled `TEST_CONFIGURATION_ONLY`.
