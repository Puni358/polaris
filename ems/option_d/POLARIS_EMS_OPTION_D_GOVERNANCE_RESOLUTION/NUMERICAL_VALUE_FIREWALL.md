# POLARIS EMS — NUMERICAL VALUE FIREWALL TABLE

## 1. Executive Summary

This document establishes the formal **Numerical Value Firewall** for Option D. In compliance with governance instructions, every numerical value appearing in repository configs, test fixtures, synthetic examples, or governance discussions is strictly classified to prevent temporary prototype parameters or illustrative scenario values from becoming implied deployment policy.

---

## 2. Master Numerical Value Classification Table

| Numerical Parameter | Current Repository / Discussion Value | Scope / Context | Formal Governance Classification | Policy Status / Usage Rule |
|---------------------|----------------------------------------|-----------------|----------------------------------|----------------------------|
| **Required Endurance Horizon ($T_{\text{required}}$)** | $72.0\text{ hours}$ | Canonical ECD Fixture | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Synthetic engineering test parameter. Production value requires DEC-001 authorization (BLK-006). |
| **Validation Endurance Window ($T_{\text{test}}$)** | $2.0\text{ hours}$ | ECD Core Unit Tests | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Controlled offline validation value only. NOT deployment horizon. |
| **Total Station Prototype Demand** | $30,000.0\text{ W}$ ($30\text{ kW}$) | Fixtures / Scenarios | `ILLUSTRATIVE_ONLY` | Synthetic illustrative value. Real station demand is time-varying and telemetry-driven. |
| **High SOC Test Band** | $80.0\%$ | Canonical ECD Fixture | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype test band. Production SOC bounds are `ENGINEERING_DEFINITION_REQUIRED`. |
| **Low SOC Test Band** | $30.0\%$ | Canonical ECD Fixture | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype test band. Minimum SOC reserve limit ($SOC_{\text{min}}$) is `GOVERNANCE_DECISION_REQUIRED`. |
| **High Fuel Test Band** | $50.0\text{ L}$ | Canonical ECD Fixture | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype test band. Production fuel capacity requires station engineering input. |
| **Low Fuel Test Band** | $12.5\text{ L}$ | Canonical ECD Fixture | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype test band. Minimum fuel reserve ($F_{\text{reserve,min}}$) is `GOVERNANCE_DECISION_REQUIRED`. |
| **Equal-Margin Fuel Parameter** | $46.0\text{ L}$ | Fixture Analytical Tie Case | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Analytically derived tie-point for Case 5 validation. NOT deployment parameter. |
| **Generator Minimum Active Power** | $10,000.0\text{ W}$ ($10\text{ kW}$) | `system/config/diesel.yaml` | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype model parameter. Physical generator turndown ratio is `ENGINEERING_DEFINITION_REQUIRED`. |
| **Generator Base Fuel Burn** | $5.0\text{ L/h}$ | `system/config/diesel.yaml` | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype linear model parameter. Production fuel curve requires nameplate data. |
| **Generator Marginal Fuel Burn** | $0.25\text{ L/kWh}$ ($0.00025\text{ L/Wh}$) | `system/config/diesel.yaml` | `SYNTHETIC_PROTOTYPE_TEST_VALUE` | Prototype linear model parameter. Production fuel curve requires nameplate data. |
| **Illustrative Protected Critical Load** | $7\text{ kW}$ | Scenario Examples | `ILLUSTRATIVE_ONLY` | Synthetic example ($4\text{ kW}$ heating $+ 2\text{ kW}$ water $+ 1\text{ kW}$ comms). Real load is dynamic $P_{\text{critical}}(t)$. |
| **Illustrative Unconstrained Diesel Dispatch** | $4\text{ kW}$ | Scenario Power Balance | `ILLUSTRATIVE_ONLY` | Purely mathematical power balance ($7 - 3 = 4\text{ kW}$). NOT physical generator output limit. |
| **Illustrative Fuel Burn at 4 kW** | $6.0\text{ L/h}$ | Scenario Calculations | `ILLUSTRATIVE_ONLY` | Math example using prototype linear curve. NOT real station fuel rate. |
| **Illustrative Fuel Burn at 10 kW** | $7.5\text{ L/h}$ | Scenario Calculations | `ILLUSTRATIVE_ONLY` | Math example using prototype linear curve. NOT real station fuel rate. |
| **Degraded Watchdog Duration Limit** | `UNSPECIFIED` | Option D Policy D5 | `ENGINEERING_DEFINITION_REQUIRED` | No numerical threshold authorized. Must be defined by station governance. |
| **Minimum Battery Reserve Floor ($SOC_{\text{min}}$)** | `UNSPECIFIED` | Option D Policy D2 | `ENGINEERING_DEFINITION_REQUIRED` | No numerical threshold authorized. Must be defined by battery engineering. |
| **Maximum Battery Charge C-Rate** | `UNSPECIFIED` | Option D Policy D6 | `ENGINEERING_DEFINITION_REQUIRED` | No numerical limit authorized. Must be defined by battery vendor spec. |

---

## 3. Firewall Enforcement Rules

1. **Zero Promotion**: No synthetic prototype parameter or illustrative scenario number shall be converted into production policy without explicit governance authorization.
2. **Explicit Labeling**: All future documentation, analysis, and interface specs referencing these numbers MUST include explicit classification tags.

Status: `NUMERICAL_FIREWALL_SEALED`
