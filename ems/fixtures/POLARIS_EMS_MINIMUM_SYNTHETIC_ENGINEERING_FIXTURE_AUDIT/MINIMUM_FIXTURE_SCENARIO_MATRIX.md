# POLARIS EMS — MINIMUM FIXTURE SCENARIO MATRIX

## 1. Executive Summary

This document specifies the 5 core scenarios comprising the **Minimum Synthetic Engineering Fixture**.

---

## 2. Core 5-Scenario Test Matrix

| Scenario ID | Name | Primary Fixture Stress Condition | Expected ECD Output | Expected Controller / Option D Behavior | Fixture Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SCENARIO 1** | Normal Operation | High SOC (80%), High Fuel (100L), Renewables Available | `NORMAL` | Standard receding-horizon MILP dispatch. | `MINIMUM_REQUIRED` |
| **SCENARIO 2** | Battery-Limited | Low SOC (30%), Zero Renewables ($T_{\text{bat}} < 6\text{h}$) | `EMERGENCY` | Emergency dispatch prioritizing battery preservation. | `MINIMUM_REQUIRED` |
| **SCENARIO 3** | Diesel-Limited | Low Fuel (12.5L), Zero Renewables ($T_{\text{dsl}} < 6\text{h}$) | `EMERGENCY` | Emergency dispatch prioritizing diesel preservation. | `MINIMUM_REQUIRED` |
| **SCENARIO 4** | Both-Limited | Low SOC (30%) + Low Fuel (12.5L) | `EMERGENCY` | Emergency dispatch with tie-handling. | `MINIMUM_REQUIRED` |
| **SCENARIO 5** | UNKNOWN_INVALID Safe State | Missing / Expired $T_{\text{required}}$ input payload | `UNKNOWN_INVALID` | Option D Safe-State Fallback engaged (D1–D6). | `MINIMUM_REQUIRED` |

---

## 3. Extended Scenario Categorization

Advanced scenarios (e.g., dynamic proportional allocation rationing under severe shortfall, multi-day blizzard recovery) are categorized as `EXTENDED_ENGINEERING_TEST_FIXTURE` and omitted from the minimum architecture demonstration fixture to maintain minimum sufficiency.

```yaml
MINIMUM_SCENARIO_COUNT: 5
COVERAGE: 100% of ECD state classifications (NORMAL, EMERGENCY, UNKNOWN_INVALID) and Option D fallback transition paths.
```
