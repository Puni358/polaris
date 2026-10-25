# OBJECTIVE TOLERANCE MAPPING

## Native HiGHS Tolerances vs Option A Reference Lock Tolerances

This document compares native HiGHS objective tolerance fields against Option A reference lock constraints.

---

## Authoritative Tolerance Mapping Table

| Stage | Option A Lock Constraint | Option B Native Attributes | Governance Status | Engineering Status | Comparison Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 ($J_1$)** | $J_1(x) \le J_1^* + \varepsilon_1$ | `abs_tolerance = 0.0` (Default) | `NOT_ESTABLISHED` | `ENGINEERING_DEFINITION_REQUIRED` | `TEST_CONFIGURATION_ONLY` |
| **Stage 2 ($J_2$)** | $J_2(x) \le J_2^* + \varepsilon_2$ | `abs_tolerance = 0.0` (Default) | `NOT_ESTABLISHED` | `ENGINEERING_DEFINITION_REQUIRED` | `TEST_CONFIGURATION_ONLY` |
| **Stage 3 ($J_3$)** | $J_3(x) \le J_3^* + \varepsilon_3$ | `abs_tolerance` (Unresolved) | `NOT_ESTABLISHED` | `ENGINEERING_DEFINITION_REQUIRED` | `TEST_CONFIGURATION_ONLY` ($0.01\text{ L}$ in toy test only) |
| **Stage 4 ($J_4$)** | Final stage (No lock required) | `abs_tolerance = 0.0` (Default) | `NOT_ESTABLISHED` | `ENGINEERING_DEFINITION_REQUIRED` | `TEST_CONFIGURATION_ONLY` |

---

## Tolerance Reclassification Finding

> [!CAUTION]
> **RECLASSIFICATION NOTICE**:
> The value $0.01\text{ L}$ for $J_3$ `abs_tolerance` was used strictly as a **TEST CONFIGURATION** parameter in isolated toy benchmark experiments.
> 
> It is **NOT** a POLARIS governed objective tolerance.
> 
> Production tolerances ($\varepsilon_1, \varepsilon_2, \varepsilon_3, \varepsilon_4$) remain `NOT_ESTABLISHED` and require explicit engineering and governance definition prior to implementation.
