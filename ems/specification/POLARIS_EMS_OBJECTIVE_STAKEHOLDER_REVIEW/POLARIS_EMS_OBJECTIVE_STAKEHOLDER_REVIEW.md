# POLARIS EMS OBJECTIVE — STAKEHOLDER GOVERNANCE REVIEW PACKAGE

**Document Version**: 1.0.0-FINAL  
**Governance Status**: STAKEHOLDER_REVIEW_PACKAGE_COMPLETE  
**Audit Timestamp**: 2026-09-21T21:56:54Z  
**Authoritative Directory**: `POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/`  
**Execution Mode**: STRICT_READ_ONLY  
**Frozen Implementation SHA-256**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` (`system/optimization/implementations/milp.py`)  

---

> [!IMPORTANT]
> **GOVERNANCE STATUS NOTICE**: This document and the associated artifacts in `POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/` constitute a **HUMAN-REVIEWABLE GOVERNANCE DECISION PACKAGE**. It is NOT an authorized modification to the POLARIS EMS. The current frozen EMS implementation (`LocalMILPEnergyOptimizer`) remains active and unchanged unless and until explicit stakeholder governance authorizes a change. Documenting options, gaps, formulations, or questions does NOT constitute approval.

---

## 1. Executive Summary

This governance review evaluates the requirements, current implementation assumptions, objective coefficients, and governance gaps of the POLARIS Energy Management System (EMS). 

### Core Governance Findings:
1. **Explicit Requirements vs. Implementation Assumptions**: POLARIS explicitly mandates 100% offline local execution, receding-horizon MPC architecture, and physical BESS operating limits ($20\%-95\%$ SOC). However, core operational targets—such as maximum acceptable unmet critical load, annual fuel consumption limits, and renewable energy targets—remain documented **qualitatively only**.
2. **Current Objective Semantics & Penalty Ratio**: The frozen `LocalMILPEnergyOptimizer` implements a weighted economic cost objective where unmet load is penalized at $\$10,000/\text{kWh}$ ($\$10/\text{Wh}$) compared to a marginal diesel fuel cost of $\$0.625/\text{kWh}$ ($0.00025\text{ L/Wh} \times \$2.50/\text{L}$). This establishes an implicit penalty ratio of **16,000 : 1**.
3. **Implementation Fact vs. Governed Policy**: The 16,000:1 value is an **OBJECTIVE COST COEFFICIENT RATIO** in code, NOT an authorized POLARIS project policy or a claim that the optimizer literally burns 4,000 L of diesel per avoided kWh of unmet load. Realized fuel consumption is trajectory-dependent.
4. **Governed V2 Evidence Context**: Locked V2 campaign evidence (173 trajectories, 4,152 H1 steps) demonstrates that the Branch01 solar forecast intervention changed the solar forecast supplied to the optimizer, and the resulting dispatch exhibited increased diesel commitment and reduced unmet load under the frozen MILP objective and constraints, reducing unmet load by $30,543.8\text{ kWh}$ while consuming $+11,350.2\text{ L}$ of additional fuel ($\approx 0.3716\text{ L/kWh}$ observed change ratio). Observed dispatch is consistent with the frozen MILP objective given treatment forecast inputs.
5. **Stakeholder Decisions Required**: A total of 16 explicit decision questions have been compiled into the Stakeholder Decision Register ([`POLARIS_EMS_STAKEHOLDER_DECISION_REGISTER.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_STAKEHOLDER_DECISION_REGISTER.md)). All numerical policy gaps are categorized as `AUTHORIZATION_REQUIRED = TRUE`.
6. **Change Boundary**: Objective modification remains `NOT_AUTHORIZED`.

---

## 2. Authoritative Requirements Discovered

A comprehensive read-only search of project documentation ([`POLARIS_MASTER_HANDOFF.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_MASTER_HANDOFF.md), [`POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md), `system/config/*.yaml`) established the following documented requirements:

- **Strict Local Offline Runtime**: 100% offline, zero external cloud APIs or network dependencies (`POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md` §1, §11). `EXPLICITLY_SPECIFIED`.
- **Separation of Forecasting & Optimization**: Optimizer operates strictly against stable `ForecastBundle` contract (`POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md` §1, §4). `EXPLICITLY_SPECIFIED`.
- **Receding-Horizon Model Predictive Control (MPC)**: Closed-loop MPC mode over 24h horizon (`POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md` §1, §7). `EXPLICITLY_SPECIFIED`.
- **Reliable Energy Supply**: Continuous power supply to research station facilities and scientific equipment (`POLARIS_MASTER_HANDOFF.md` §1). `QUALITATIVELY_SPECIFIED`.
- **Lower Fuel Dependence**: Minimize diesel generator fuel consumption and resupply logistics (`POLARIS_MASTER_HANDOFF.md` §1, §58). `QUALITATIVELY_SPECIFIED`.
- **Renewable Energy Integration**: Maximize integration and utilization of solar PV and wind generation (`POLARIS_MASTER_HANDOFF.md` §1, §58). `QUALITATIVELY_SPECIFIED`.
- **Battery SOC Bounds**: BESS operating limits bounded between 20% min SOC ($40\text{ kWh}$) and 95% max SOC ($190\text{ kWh}$) under 200 kWh capacity (`system/config/battery.yaml`). `EXPLICITLY_SPECIFIED`.
- **Generator Operating Bounds**: Diesel min power 10 kW, max power 100 kW when active (`system/config/diesel.yaml`). `EXPLICITLY_SPECIFIED`.

---

## 3. Current Frozen EMS Objective

Direct inspection of `system/optimization/implementations/milp.py` (SHA-256: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`) verifies the exact mathematical objective function:

$$J = \sum_{t=0}^{23} \left[ c_{\text{curt}} \Delta t w_t (P_{\text{curt,sol},t} + P_{\text{curt,wind},t}) + c_{\text{deg}} \Delta t w_t (P_{\text{chg},t} + P_{\text{dis},t}) + c_{\text{marg}} \Delta t w_t P_{\text{diesel},t} + c_{\text{unmet}} \Delta t P_{\text{unmet},t} + c_{\text{base}} \Delta t w_t u_{\text{diesel},t} + c_{\text{start}} w_t v_{\text{start},t} \right]$$

### Directly Verified Coefficient Values:
- **Renewable Curtailment Penalty ($c_{\text{curt}}$)**: $\$0.001/\text{Wh} = \$1.00/\text{kWh}$ (`milp.py` L50, L107-108)
- **BESS Degradation Penalty ($c_{\text{deg}}$)**: $\$0.00005/\text{Wh} = \$0.05/\text{kWh}$ (`battery.yaml` L11, `milp.py` L109-110)
- **Marginal Diesel Fuel Cost ($c_{\text{marg}}$)**: $\$2.50/\text{L} \times 0.00025\text{ L/Wh} = \$0.000625/\text{Wh} = \$0.625/\text{kWh}$ (`diesel.yaml` L6-7, `milp.py` L111)
- **Unmet Load Penalty ($c_{\text{unmet}}$)**: $\$10.00/\text{Wh} = \$10,000.00/\text{kWh}$ (**Unweighted**, $\gamma^t = 1.0$) (`loads.yaml` L4, `milp.py` L112)
- **Base Running Fuel Cost ($c_{\text{base}}$)**: $\$2.50/\text{L} \times 5.0\text{ L/h} = \$12.50/\text{h}$ (`diesel.yaml` L5, L7, `milp.py` L113)
- **Generator Startup Penalty ($c_{\text{start}}$)**: $\$15.00/\text{start}$ (`diesel.yaml` L8, `milp.py` L114)

---

## 4. Current Implementation Assumptions

All configuration values in `system/config/*.yaml` are explicitly labeled `status_label: "PROTOTYPE_ASSUMPTION"`.
- **`battery.yaml`**: 200 kWh capacity, 20% min SOC, 95% max SOC, 92% efficiency, 50 kW max power, $\$0.05/\text{kWh}$ degradation.
- **`diesel.yaml`**: 10 kW min power, 100 kW max power, 5.0 L/h base fuel, 0.25 L/kWh marginal fuel, $\$2.50/\text{L}$ fuel price, $\$15.00$ startup.
- **`loads.yaml`**: 30 kW critical load baseline, $\$10,000/\text{kWh}$ unmet penalty.

---

## 5. Requirement vs. Implementation Gaps

| Operational Domain | Documented Requirement State | Current Implementation State | Governance Gap Category |
| :--- | :--- | :--- | :--- |
| **Max Unmet Critical Load** | Qualitative ("Reliable energy supply") | $\$10,000/\text{kWh}$ soft penalty | `NUMERICAL_TARGET_MISSING` |
| **Max Outage Duration** | Qualitative ("Protect critical loads") | Unconstrained in solver | `SLA_SPECIFICATION_MISSING` |
| **Fuel Minimization** | Qualitative ("Lower fuel dependence") | Minimized as linear cost term | `FUEL_CEILING_MISSING` |
| **Fuel-vs-Reliability Ratio** | Not specified | $16,000:1$ coefficient ratio | `POLICY_EXCHANGE_RATE_MISSING` |
| **Emergency BESS Reserve** | Qualitative ("Emergency storage") | $20\%$ technical min SOC floor | `DYNAMIC_RESERVE_FLOOR_MISSING` |
| **Terminal BESS SOC** | Not specified | Unconstrained ($E_{24} \ge E_{\min}$) | `HORIZON_BOUNDARY_MISSING` |
| **Renewable Utilization** | Qualitative ("Maximize renewables") | $\$1/\text{kWh}$ curtailment penalty | `RENEWABLE_TARGET_MISSING` |
| **Forecast Uncertainty** | Qualitative ("Uncertainty-aware") | Deterministic point forecasts | `STOCHASTIC_POLICY_MISSING` |

---

## 6. Reliability Requirements

- **Documented Status**: `QUALITATIVELY_SPECIFIED`. High priority, but zero numerical uptime SLA (e.g. 99.9%) or maximum continuous interruption allowance documented.
- **Implementation**: Formulated as a soft penalty in `milp.py` ($\$10,000/\text{kWh}$).
- **Required Decision**: Stakeholders must decide whether reliability is a strict hard constraint ($P_{\text{unmet}} = 0$) or a penalized objective term (`DECISION_04`, `DECISION_06`).

---

## 7. Fuel Requirements

- **Documented Status**: `QUALITATIVELY_SPECIFIED`. Source text states "minimize diesel use" and "lower fuel dependence".
- **Distinction**: Does NOT explicitly distinguish minimizing fuel volume (liters), operating hours (runtime), operating cost ($), generator starts, or emissions.
- **Numerical Target**: `FUEL_TARGET = NOT_SPECIFIED`. No annual fuel ceiling or percentage reduction target exists in project requirements.

---

## 8. Renewable Requirements

- **Documented Status**: `QUALITATIVELY_SPECIFIED`. Source text states "maximize renewable integration".
- **Definition**: `RENEWABLE_OBJECTIVE_DEFINITION = NOT_SPECIFIED`. Project docs do not specify whether this means maximizing kWh used, minimizing curtailment, maximizing renewable fraction %, or minimizing diesel generation.

---

## 9. Battery Requirements

- **Technical Bounds**: $20\% \le \text{SOC} \le 95\%$ ($40\text{ kWh} \le E \le 190\text{ kWh}$) hard bounds (`EXPLICITLY_SPECIFIED`).
- **Emergency Reserve**: `EMERGENCY_RESERVE = NOT_SPECIFIED`. The 20% SOC technical limit is an operational lower bound, NOT a dedicated emergency reserve floor.
- **Terminal SOC**: `TERMINAL_SOC_REQUIREMENT = NOT_SPECIFIED`. Solver horizon leaves end SOC unconstrained ($E_{24} \ge E_{\min}$).

---

## 10. Critical Load / Load Shedding Requirements

- **Documented Status**: `QUALITATIVELY_SPECIFIED`.
- **Hierarchy**: `CRITICAL_LOAD_HIERARCHY = NOT_SPECIFIED`. `loads.yaml` contains placeholder deferrable/curtailable load definitions (`PROTOTYPE_ASSUMPTION`).
- **Shedding Order**: `LOAD_SHEDDING_POLICY = NOT_SPECIFIED`. No formal multi-tier shedding hierarchy exists in project policy.

---

## 11. Forecast Uncertainty Requirements

- **Documented Status**: `QUALITATIVELY_SPECIFIED` / `ASPIRATIONAL_GOAL`.
- **Policy**: `FORECAST_UNCERTAINTY_POLICY = NOT_SPECIFIED`. Current implementation operates deterministically against point forecasts without dynamic spinning/BESS reserve buffers.

---

## 12. Fuel-vs-Reliability Governance Gap

$$\text{Objective Cost Coefficient Ratio} = \frac{\text{Unmet Load Penalty}}{\text{Marginal Diesel Cost}} = \frac{\$10,000.00 / \text{kWh}}{\$0.625 / \text{kWh}} = 16,000 : 1$$

- **Interpretation Boundary**: The unmet-load penalty is 16,000 times the marginal diesel-energy cost on a $\$/\text{kWh}$ basis. This is an **OBJECTIVE COST COEFFICIENT RATIO**, NOT a claim that the optimizer literally burns 4,000 Liters of diesel per avoided kWh of unmet load.
- **Governed Status**: `FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED`. No project document defines the authorized exchange rate between fuel consumption and load shedding.

---

## 13. Objective Priority Status

- **Governed Status**: `OBJECTIVE_PRIORITY = NOT_SPECIFIED`. Authoritative POLARIS documentation does not establish a formal priority ordering between reliability, fuel minimization, renewable utilization, BESS preservation, and operating cost.

---

## 14. Objective Formulation Options (Descriptive Only)

Without ranking, recommending, or selecting any formulation, four mathematical structures are available for stakeholder consideration:

1. **Lexicographic / Reliability-First Optimization**: Two-stage optimization. Stage 1 minimizes unmet load to absolute physical feasibility ($P_{\text{unmet}}^*$). Stage 2 minimizes fuel subject to $P_{\text{unmet}} \le P_{\text{unmet}}^*$.
2. **Reliability-Constrained Fuel Minimization**: Formulates load service as a hard constraint ($P_{\text{served}} = P_{\text{demand}}$) or SLA bound ($\sum P_{\text{unmet}} \le \text{Cap}$), directly minimizing fuel volume $\sum \text{Fuel}_t$.
3. **Weighted Economic Objective**: Single objective function combining fuel cost, degradation, and unserved energy penalty weights ($c_{\text{unmet}}$).
4. **Multi-Objective / Pareto Formulation**: Computes the Pareto frontier of non-dominated solutions trading off Fuel (L) vs Unmet Load (kWh), enabling operators to select operating modes dynamically.

---

## 15. Numerical Target Register Summary

| Parameter | Current Implementation Value | Authoritative Requirement | Source Document | Governed Status |
| :--- | :--- | :--- | :--- | :--- |
| **Unmet Load Penalty** | $\$10,000.00/\text{kWh}$ | `NOT_SPECIFIED` | `loads.yaml` L4 | `PROTOTYPE_ASSUMPTION` |
| **Marginal Diesel Cost** | $\$0.625/\text{kWh}$ | `NOT_SPECIFIED` | `diesel.yaml` L6-7 | `PROTOTYPE_ASSUMPTION` |
| **Base Fuel Consumption** | $5.0\text{ L/h}$ ($\$12.50/\text{h}$) | `NOT_SPECIFIED` | `diesel.yaml` L5 | `PROTOTYPE_ASSUMPTION` |
| **Generator Startup Cost** | $\$15.00/\text{start}$ | `NOT_SPECIFIED` | `diesel.yaml` L8 | `PROTOTYPE_ASSUMPTION` |
| **Fuel Target / Ceiling** | Uncapped | `NOT_SPECIFIED` | None | `AUTHORIZATION_REQUIRED` |
| **Max Unmet Load** | Uncapped | `NOT_SPECIFIED` | None | `AUTHORIZATION_REQUIRED` |
| **Max Outage Duration** | Unconstrained | `NOT_SPECIFIED` | None | `AUTHORIZATION_REQUIRED` |
| **Emergency BESS Reserve** | $20\%\text{ SOC}$ hard limit | `NOT_SPECIFIED` | `battery.yaml` L4 | `AUTHORIZATION_REQUIRED` |
| **Terminal BESS SOC** | Unconstrained | `NOT_SPECIFIED` | `milp.py` L123 | `AUTHORIZATION_REQUIRED` |
| **Renewable Target** | Unconstrained | `NOT_SPECIFIED` | None | `AUTHORIZATION_REQUIRED` |

---

## 16. Requirements Traceability Summary

All EMS behaviors trace to exactly one of four categories:
1. **Authoritative Requirement**: 100% local offline execution, MPC receding horizon, $20\%-95\%$ BESS SOC, $10-100\text{ kW}$ generator power bounds.
2. **Physical Constraint**: Bus-bar power balance, battery energy storage discrete state transition, demand service equality.
3. **Implementation Assumption**: $\$10,000/\text{kWh}$ unmet penalty, $\$0.625/\text{kWh}$ marginal diesel cost, $\$15$ startup penalty, $30\text{ kW}$ baseline demand.
4. **Unresolved Governance Decision**: Fuel-vs-reliability trade-off ratio, numerical fuel ceiling, emergency reserve floor, load-shedding hierarchy.

---

## 17. Stakeholder Decision Register

A total of 16 decision questions have been detailed in [`POLARIS_EMS_STAKEHOLDER_DECISION_REGISTER.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_STAKEHOLDER_DECISION_REGISTER.md):
- `DECISION_01`: Critical load classification?
- `DECISION_02`: Curtailable / shed-able load classification?
- `DECISION_03`: Minimum service level for critical loads?
- `DECISION_04`: Maximum acceptable unmet critical load (kWh)?
- `DECISION_05`: Maximum continuous critical-load interruption duration (hours)?
- `DECISION_06`: Hard constraint vs soft penalized objective for reliability?
- `DECISION_07`: Exact definition of "minimize diesel use" (liters, runtime, cost)?
- `DECISION_08`: Maximum acceptable fuel consumption / annual ceiling?
- `DECISION_09`: Renewable utilization target (%)?
- `DECISION_10`: Renewable curtailment objective definition?
- `DECISION_11`: Minimum emergency battery reserve floor (kWh)?
- `DECISION_12`: Horizon terminal SOC requirement (%)?
- `DECISION_13`: Battery behavior under forecast uncertainty?
- `DECISION_14`: Authorized fuel-vs-reliability penalty trade-off ratio?
- `DECISION_15`: Governed objective priority ordering?
- `DECISION_16`: Designated governance approval authority?

---

## 18. Draft Review-Only EMS Objective Specification

A complete draft review specification has been generated in [`POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md). All missing numerical thresholds are marked `VALUE = NOT_SPECIFIED`, `STATUS = TBD`, `AUTHORIZATION_REQUIRED = TRUE`.

---

## 19. Governance Change Boundary

| Component | Current Status | Change Allowed Now? | Required Authorization |
| :--- | :--- | :--- | :--- |
| **`milp.py` (LocalMILPEnergyOptimizer)** | FROZEN | `NO` | Explicit Stakeholder Approval of EMS Spec |
| **ForecastBundle Contract** | FROZEN | `NO` | Governance Architecture Board |
| **MILP Objective Weights / Coefficients** | FROZEN | `NO` | Stakeholder Decision on `DECISION_14` |
| **MILP Physical Constraints** | FROZEN | `NO` | Stakeholder Approval of Technical Specs |
| **DispatchPlan Schema** | FROZEN | `NO` | Governance Architecture Board |
| **DigitalTwinSimulator** | FROZEN | `NO` | Governance Architecture Board |
| **Battery Operating Limits** | FROZEN | `NO` | Equipment Specification Authorization |
| **Diesel Operating Limits** | FROZEN | `NO` | Equipment Specification Authorization |
| **V2 Campaign Evidence** | FROZEN_VALID | `NO` | Permanent Evidence Lock |

---

## 20. Provenance / Hash Status

- **`milp.py` Hash**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` (**VERIFIED_MATCH**).
- **Config & Document Hashes**: Computed directly from disk bytes using `hashlib.sha256()`.
- **Provenance Status**: `CORRECTION_PACKAGE_STATUS = VERIFIED_WITH_HISTORICAL_BASELINE_CORRECTION_REQUIRED`.

---

## 21. Final Governance Status

```
AUTHORITATIVE_REQUIREMENTS_AUDIT = INSUFFICIENT_EVIDENCE
CURRENT_OBJECTIVE_IMPLEMENTATION_AUDIT = PASS
OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED
RELIABILITY_REQUIREMENT = QUALITATIVELY_SPECIFIED
FUEL_REQUIREMENT = QUALITATIVELY_SPECIFIED
RENEWABLE_REQUIREMENT = QUALITATIVELY_SPECIFIED
BATTERY_REQUIREMENT = PARTIALLY_GOVERNED
CRITICAL_LOAD_POLICY = QUALITATIVELY_SPECIFIED
LOAD_SHEDDING_POLICY = QUALITATIVELY_SPECIFIED
FORECAST_UNCERTAINTY_POLICY = QUALITATIVELY_SPECIFIED
FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED
OBJECTIVE_PRIORITY = NOT_SPECIFIED
OBJECTIVE_FORMULATION_POLICY = NOT_SPECIFIED
NUMERICAL_POLICY_GAPS = 10
STAKEHOLDER_DECISIONS_REQUIRED = 16
DRAFT_REVIEW_SPECIFICATION = COMPLETE
STAKEHOLDER_AUTHORIZATION = NOT_GRANTED
OBJECTIVE_MODIFICATION = NOT_AUTHORIZED
EMS_MODIFICATION = NOT_AUTHORIZED
MODEL_MODIFICATION = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
V2_EVIDENCE_LOCK = PASS
ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET
NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED
```

---

## 22. Exact Next Governed Step

NEXT_GOVERNED_STEP =
STAKEHOLDER_REVIEW_AND_DECISION_ON_EXPLICIT_EMS_POLICY
