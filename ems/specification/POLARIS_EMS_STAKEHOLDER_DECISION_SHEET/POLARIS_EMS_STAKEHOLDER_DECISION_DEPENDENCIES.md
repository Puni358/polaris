# POLARIS EMS STAKEHOLDER DECISION DEPENDENCY MAP

## PURPOSE & GOVERNANCE NOTICE

This document outlines the logical dependency relationships among the 16 POLARIS EMS stakeholder policy decisions.

> [!IMPORTANT]
> **GOVERNANCE NOTICE**: The dependency map presented here is a **LOGICAL DEPENDENCY SEQUENCE ONLY**. It is **NOT a policy ranking or priority hierarchy**. The sequence exists solely because downstream optimization parameters (e.g. penalty weights and constraint bounds) cannot be specified responsibly until upstream foundational definitions (e.g. load classifications, diesel metrics, and reliability SLAs) are established by human stakeholders.

---

## DEPENDENCY STRUCTURE

### Path 1: Critical Load & Service Level Dependency Chain
- **DECISION_01** (Critical Load Classification)
  └──> **DECISION_02** (Load Shedding Classification)
        └──> **DECISION_03** (Minimum Critical-Load Service Requirement)
              └──> **DECISION_04** (Maximum Acceptable Unmet Critical Load)
                    └──> **DECISION_05** (Maximum Continuous Interruption)
                          └──> **DECISION_06** (Reliability Mathematical Formulation)

### Path 2: Diesel Minimization & Budget Ceiling Dependency Chain
- **DECISION_07** (Definition of "Minimize Diesel Use")
  └──> **DECISION_08** (Fuel Ceiling / Budget)
        └──> **DECISION_14** (Fuel-vs-Reliability Trade-Off Ratio)

### Path 3: Renewable & Battery Storage Policy Dependency Chain
- **DECISION_09** (Renewable Utilization Target) & **DECISION_10** (Renewable Curtailment Policy)
- **DECISION_11** (Emergency Battery Reserve)
  └──> **DECISION_12** (Terminal SOC Requirement)
        └──> **DECISION_13** (Forecast Uncertainty Policy)

### Path 4: Multi-Objective & Governance Integration Chain
- **Decisions 01-14** (All Specific Policy Parameters)
  └──> **DECISION_15** (Governed Objective Priority Hierarchy)
        └──> **DECISION_16** (Governance Approval Authority Designation)

---

## LOGICAL RATIONALE TABLE

| Decision ID | Upstream Dependencies | Downstream Dependents | Logical Rationale | Is Policy Ranking? |
|-------------|-----------------------|-----------------------|-------------------|-------------------|
| DECISION_01 | None | DECISION_02, DECISION_03 | Cannot classify shed-able load or service levels without defining critical loads first | NO |
| DECISION_02 | DECISION_01 | DECISION_03 | Load shedding rules depend on which loads are sheddable | NO |
| DECISION_03 | DECISION_01, DECISION_02 | DECISION_04, DECISION_05 | Service level target defines baseline for maximum unmet load and interruption duration | NO |
| DECISION_04 | DECISION_03 | DECISION_06 | Unmet load tolerance bounds dictate hard vs soft reliability formulation | NO |
| DECISION_05 | DECISION_03 | DECISION_06 | Max outage duration informs time-step constraint formulation | NO |
| DECISION_06 | DECISION_04, DECISION_05 | DECISION_14, DECISION_15 | Reliability formulation type determines objective penalty weight structure | NO |
| DECISION_07 | None | DECISION_08, DECISION_14 | Diesel metric (L vs kWh vs $) must be defined before fuel budget or exchange rates | NO |
| DECISION_08 | DECISION_07 | DECISION_14 | Fuel budget caps bound allowed fuel/reliability exchange options | NO |
| DECISION_09 | None | DECISION_10, DECISION_15 | Renewable integration target informs curtailment policy and priority hierarchy | NO |
| DECISION_10 | DECISION_09 | DECISION_15 | Curtailment policy affects objective scalar terms | NO |
| DECISION_11 | None | DECISION_12, DECISION_13 | Emergency SOC floor bounds allowable terminal SOC and uncertainty reserves | NO |
| DECISION_12 | DECISION_11 | DECISION_13 | Terminal SOC policy constrains horizon dispatch | NO |
| DECISION_13 | DECISION_11, DECISION_12 | DECISION_15 | Uncertainty reserve strategy influences multi-objective trade-offs | NO |
| DECISION_14 | DECISION_06, DECISION_07, DECISION_08 | DECISION_15 | Fuel/reliability trade-off ratio requires both reliability and fuel definitions | NO |
| DECISION_15 | DECISION_01 to DECISION_14 | DECISION_16 | Composite priority hierarchy requires all individual policy choices to be defined | NO |
| DECISION_16 | DECISION_15 | Future EMS Spec | Governance approval authority formally signs off on complete specification | NO |
