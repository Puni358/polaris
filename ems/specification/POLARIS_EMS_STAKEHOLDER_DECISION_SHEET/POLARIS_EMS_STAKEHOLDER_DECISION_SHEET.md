# POLARIS EMS
# STAKEHOLDER POLICY DECISION SHEET
## OFFICIAL GOVERNED POLICY CAPTURE RECORD

Purpose:
To record explicit human-selected stakeholder policy decisions for the POLARIS Energy Management System (EMS).

Current EMS Implementation:
FROZEN

Stakeholder Authorization Status:
HUMAN_SELECTED_POLICIES_CAPTURED — AWAITING_FORMAL_SPECIFICATION

Objective Modification:
NOT_AUTHORIZED

EMS Modification:
NOT_AUTHORIZED

---

## EXECUTIVE OVERVIEW & GOVERNANCE BOUNDARIES

This document serves as the official **Stakeholder Policy Decision Sheet** for the POLARIS EMS, populated with the **16 human-selected policy answers** provided by the authorized human stakeholder.

### Critical Three-Layer Governance Separation
```
CURRENT IMPLEMENTATION (FROZEN)
    ≠
STAKEHOLDER POLICY DECISIONS (HUMAN_SELECTED)
    ≠
FUTURE GOVERNED EMS OBJECTIVE SPECIFICATION (NOT_YET_CREATED)
```

- **Current Implementation**: Describes what the frozen prototype software does (e.g. `$10,000/kWh` soft penalty, `20%` technical min SOC). These are software facts, **NOT** stakeholder policy.
- **Stakeholder Policy Decisions**: Describes what the human stakeholder requires for future system behavior (e.g. 100% continuous critical service target, liters as primary fuel metric, lexicographic priority).
- **Future Governed EMS Objective Specification**: A subsequent governed phase that will translate these authorized policy decisions into explicit mathematical formulations, constraints, operating modes, KPIs, and change-control requirements.

---

## DECISION SUMMARY TABLE

| ID | Decision Question | Selected Option | Policy Intent Summary | Status |
|----|-------------------|-----------------|-----------------------|--------|
| DECISION_01 | Which station loads are classified as CRITICAL? | **A + C** | Tiered load classification (Critical / Essential / Interruptible) with mode-dependent operation | HUMAN_SELECTED |
| DECISION_02 | Which loads may be curtailed or shed during deficit? | **A + B** | Automated tier-based load shedding; Critical loads protected, Flexible/Interruptible shed | HUMAN_SELECTED |
| DECISION_03 | What minimum service level is required for critical loads? | **A** | 100% continuous energy service target for Critical Loads during normal governed operation | HUMAN_SELECTED |
| DECISION_04 | What maximum amount of unmet critical load is acceptable? | **A** | 0 kWh unmet Critical Load under normal governed operation; emergency policy for extraordinary events | HUMAN_SELECTED |
| DECISION_05 | What is the max continuous interruption duration? | **A** | 0 minutes intentional interruption for Critical Loads (policy requirement) | HUMAN_SELECTED |
| DECISION_06 | How should critical-load reliability be formulated? | **D + A** | Lexicographic / multi-stage optimization with a hard Stage-1 reliability boundary | HUMAN_SELECTED |
| DECISION_07 | What does POLARIS mean by "minimize diesel use"? | **A + B** | Primary metric: actual liters fuel consumed; Secondary metric: diesel electrical kWh generated | HUMAN_SELECTED |
| DECISION_08 | Is there a maximum fuel consumption or fuel budget cap? | **B + C** | Seasonal/resupply-cycle fuel budget combined with dynamic fuel management | HUMAN_SELECTED |
| DECISION_09 | Is there a quantitative renewable utilization target? | **B** | Minimize avoidable renewable curtailment; no arbitrary % target | HUMAN_SELECTED |
| DECISION_10 | How should renewable curtailment be treated? | **B** | Necessary renewable curtailment (spill) allowed without explicit objective penalty | HUMAN_SELECTED |
| DECISION_11 | What minimum battery reserve must remain for emergencies? | **B + A** | Dynamic emergency reserve adapting to forecast risk, plus dedicated baseline reserve floor | HUMAN_SELECTED |
| DECISION_12 | Should battery have a required terminal SOC per horizon? | **C + B** | Dynamic terminal SOC requirement adapting to risk, plus minimum terminal SOC floor | HUMAN_SELECTED |
| DECISION_13 | How should EMS dispatch account for forecast uncertainty? | **A + D** | Deterministic safety margins combined with real-time MPC rolling feedback correction | HUMAN_SELECTED |
| DECISION_14 | What trade-off between fuel and unmet load is authorized? | **A + C** | Reliability has absolute priority; fuel minimized subject to reliability SLA and budget | HUMAN_SELECTED |
| DECISION_15 | What explicit objective priority order should apply? | **A** | Strict Lexicographic Hierarchy: 1. Critical reliability -> 2. Resilience -> 3. Fuel -> 4. Renewables | HUMAN_SELECTED |
| DECISION_16 | Who has authority to approve EMS objective changes? | **C** | Multi-tier approval structure: 1. Technical -> 2. Mission/Ops -> 3. Final Approval | HUMAN_SELECTED |

---

## CONCEPTUAL GOVERNANCE BOUNDARIES

1. **DO NOT CONFUSE**: The `$10,000/kWh` unmet-load penalty coefficient in `milp.py` with stakeholder policy. It is an implementation fact, NOT a stakeholder SLA.
2. **DO NOT CONFUSE**: The `16,000:1` coefficient ratio (`$10,000/kWh` / `$0.625/kWh`) with a policy exchange rate. It is an objective cost ratio, NOT a stakeholder decision.
3. **DO NOT CONFUSE**: The `~0.3716 L/kWh` observed V2 empirical ratio with a universal policy coefficient. It is a trajectory-dependent empirical outcome.
4. **DO NOT CONFUSE**: The `20%` technical minimum battery SOC limit (`battery.yaml`) with a stakeholder emergency reserve. The 20% limit protects cell degradation, NOT emergency reserve energy.
5. **DO NOT CONFUSE**: Policy intent (e.g. 100% continuous critical service target) with a demonstrated physical hardware guarantee. Engineering validation is required.
6. **DO NOT CONFUSE**: Policy priority ordering (Decision 15) with a finished mathematical solver formulation. Mathematical formulation must be developed in the next phase.

---

## DETAILED 16 HUMAN-SELECTED STAKEHOLDER DECISIONS

### DECISION_01 — CRITICAL LOAD CLASSIFICATION

**HUMAN-SELECTED OPTION**: `A + C` — Tiered Load Classification with Mode-Dependent Operation

**POLICY INTENT**:
POLARIS should use authoritative load tiers: Critical, Essential / Flexible, Interruptible / Noncritical. Operational rules may vary by explicitly defined operating mode.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative commitment to power station loads reliably; no tiering documented.

**CURRENT IMPLEMENTATION FACT**:
loads.yaml defines single aggregate demand profile P_load without load tiering.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Actual station equipment and circuit-level mapping into Critical, Essential, and Interruptible tiers.

**REQUIRED VALIDATION**:
Station operator validation of physical electrical circuits and load equipment inventory.

**FUTURE SPECIFICATION REQUIRED**:
Define circuit-level relay switching groups and mode-dependent load tier schedules.

**STATUS**: `HUMAN_SELECTED` (`IMPLEMENTATION_DETAILS_PENDING`)

---

### DECISION_02 — LOAD SHEDDING CLASSIFICATION

**HUMAN-SELECTED OPTION**: `A + B` — Automated Tier-Based Load Shedding Queue

**POLICY INTENT**:
Critical loads are protected. Flexible/deferrable/interruptible loads may be curtailed or deferred following a predefined priority shedding structure.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative goal to avoid power outages; no shedding schedule specified.

**CURRENT IMPLEMENTATION FACT**:
milp.py & optimizer.yaml use c_unmet = $10,000/kWh penalty for all load equally.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact priority shedding sequence, restoration trigger thresholds, and dwell time parameters.

**REQUIRED VALIDATION**:
Relay switching hardware speed and automated load-shed controller response time.

**FUTURE SPECIFICATION REQUIRED**:
Specify automated shedding queue logic, restoration priority rules, and chattering-prevention dwell times.

**STATUS**: `HUMAN_SELECTED` (`IMPLEMENTATION_DETAILS_PENDING`)

---

### DECISION_03 — MINIMUM CRITICAL-LOAD SERVICE REQUIREMENT

**HUMAN-SELECTED OPTION**: `A` — 100% Continuous Service Target for Critical Loads

**POLICY INTENT**:
The governed policy target is 100% continuous service for Critical Loads during normal governed operation.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative requirement for high power reliability; no numerical percentage specified.

**CURRENT IMPLEMENTATION FACT**:
Economic trade-off against fuel via $10,000/kWh penalty; no minimum service level enforced.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Physical station hardware capability to guarantee 100% continuous service under worst-case weather stress.

**REQUIRED VALIDATION**:
Engineering validation of generator backup, battery capacity, and worst-case renewable dropouts.

**FUTURE SPECIFICATION REQUIRED**:
Define 100% continuous critical service SLA and emergency exception reporting criteria.

**STATUS**: `HUMAN_SELECTED` (`ENGINEERING_VALIDATION_PENDING`)

---

### DECISION_04 — MAXIMUM ACCEPTABLE UNMET CRITICAL LOAD

**HUMAN-SELECTED OPTION**: `A` — 0 kWh Unmet Critical Load under Normal Governed Operation

**POLICY INTENT**:
Normal governed operation permits zero unmet Critical Load. Extraordinary emergency conditions require separately defined emergency policy.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified.

**CURRENT IMPLEMENTATION FACT**:
c_unmet = $10,000/kWh penalty in MILP objective (implementation fact, NOT policy).

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Operational triggers and logging protocols for declared emergency modes when 0 kWh becomes physically unachievable.

**REQUIRED VALIDATION**:
Operational audit of backup power failover and emergency mode declaration protocols.

**FUTURE SPECIFICATION REQUIRED**:
Specify 0 kWh hard reliability boundary in normal MILP, plus explicit emergency fallback rules.

**STATUS**: `HUMAN_SELECTED` (`EMERGENCY_POLICY_DETAILS_PENDING`)

---

### DECISION_05 — MAXIMUM CONTINUOUS INTERRUPTION

**HUMAN-SELECTED OPTION**: `A` — 0 Minutes Intentional Interruption for Critical Loads

**POLICY INTENT**:
Zero intentional interruption permitted for Critical Loads as a policy requirement. Physical hardware transfer gaps are governed separately.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified.

**CURRENT IMPLEMENTATION FACT**:
1.0 hour timestep (dt = 1.0) in optimizer.yaml without sub-hour interruption limits.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Station physical transfer switching speed, UPS buffer duration, and equipment outage tolerance.

**REQUIRED VALIDATION**:
Measurement of automatic transfer switch (ATS) gap and local UPS hold-up times.

**FUTURE SPECIFICATION REQUIRED**:
Formulate zero-intentional-interruption constraint and specify hardware ATS performance bounds.

**STATUS**: `HUMAN_SELECTED` (`ENGINEERING_VALIDATION_PENDING`)

---

### DECISION_06 — RELIABILITY FORMULATION

**HUMAN-SELECTED OPTION**: `D + A` — Lexicographic / Multi-Stage Optimization with Hard Reliability Boundary

**POLICY INTENT**:
Critical reliability has absolute priority. Normal ops enforces Critical unmet load = 0. Remaining objectives optimized in priority order.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified.

**CURRENT IMPLEMENTATION FACT**:
Single scalar composite objective with c_unmet * P_unmet soft penalty in milp.py.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact multi-stage / lexicographic MILP mathematical formulation and stage-coupling constraints.

**REQUIRED VALIDATION**:
Solver execution speed and stability testing across multi-stage MILP formulations.

**FUTURE SPECIFICATION REQUIRED**:
Construct multi-stage lexicographic MILP mathematical formulation with hard Stage-1 reliability boundary.

**STATUS**: `HUMAN_SELECTED` (`FORMAL_OBJECTIVE_FORMULATION_PENDING`)

---

### DECISION_07 — DEFINITION OF "MINIMIZE DIESEL USE"

**HUMAN-SELECTED OPTION**: `A + B` — Primary Metric: Liters Fuel Consumed; Secondary Metric: Diesel kWh Generated

**POLICY INTENT**:
Primary fuel metric is actual liters consumed (physical resupply constraint). Secondary metric is diesel electrical kWh generated.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative objective to 'minimize diesel consumption'.

**CURRENT IMPLEMENTATION FACT**:
Linear fuel expenditure ($0.625/kWh) + quadratic fuel curve in diesel.yaml & milp.py.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact fuel curve quadratic coefficients (a*P^2 + b*P + c*u) for converting electric output to liters across temperatures.

**REQUIRED VALIDATION**:
Generator fuel consumption bench testing and empirical fuel flow meter calibration.

**FUTURE SPECIFICATION REQUIRED**:
Formulate diesel minimization objective in terms of liters consumed using calibrated fuel curves.

**STATUS**: `HUMAN_SELECTED` (`METRIC_FORMULATION_PENDING`)

---

### DECISION_08 — FUEL CEILING / BUDGET

**HUMAN-SELECTED OPTION**: `B + C` — Seasonal Fuel Budget with Dynamic Fuel Management

**POLICY INTENT**:
Establish seasonal/resupply-cycle fuel budget and dynamic fuel management accounting for inventory, time to resupply, and expected renewables.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative goal to reduce fuel reliance; no numerical ceiling specified.

**CURRENT IMPLEMENTATION FACT**:
No fuel budget ceiling or seasonal liter constraint in milp.py or configs.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Station fuel tank storage volume, resupply delivery interval, and seasonal liter allocation.

**REQUIRED VALIDATION**:
Station logistics audit of fuel storage capacity and resupply schedule reliability.

**FUTURE SPECIFICATION REQUIRED**:
Specify seasonal fuel budget constraint equations and dynamic fuel tracking KPIs.

**STATUS**: `HUMAN_SELECTED` (`STATION_FUEL_LIMIT_PENDING`)

---

### DECISION_09 — RENEWABLE UTILIZATION TARGET

**HUMAN-SELECTED OPTION**: `B` — Minimize Avoidable Renewable Curtailment (No Arbitrary % Target)

**POLICY INTENT**:
Maximize renewable utilization by avoiding unnecessary curtailment. Curtailment permitted only for reliability, storage, or generator safety.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative goal to 'maximize renewable integration'.

**CURRENT IMPLEMENTATION FACT**:
Zero marginal solar cost in MILP; no explicit renewable utilization KPI.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Tracking KPI formulation for avoidable vs unavoidable curtailment.

**REQUIRED VALIDATION**:
Site solar irradiance and wind availability telemetry integration.

**FUTURE SPECIFICATION REQUIRED**:
Formulate renewable utilization objective term penalizing avoidable curtailment.

**STATUS**: `HUMAN_SELECTED` (`IMPLEMENTATION_METRIC_PENDING`)

---

### DECISION_10 — RENEWABLE CURTAILMENT POLICY

**HUMAN-SELECTED OPTION**: `B` — Necessary Renewable Curtailment Allowed Without Explicit Penalty

**POLICY INTENT**:
Necessary renewable curtailment required for battery protection or generator stability is allowed without an objective penalty.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative goal to utilize renewables; no curtailment policy specified.

**CURRENT IMPLEMENTATION FACT**:
P_pv_curtail is unpenalized in milp.py (implementation fact, NOT policy).

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Mathematical distinction between necessary spill curtailment and avoidable economic curtailment.

**REQUIRED VALIDATION**:
Control controller validation of minimum generator loading and battery max charge rates.

**FUTURE SPECIFICATION REQUIRED**:
Specify curtailment balance equation leaving necessary spill unpenalized.

**STATUS**: `HUMAN_SELECTED` (`FORMAL_POLICY_TRANSLATION_PENDING`)

---

### DECISION_11 — EMERGENCY BATTERY RESERVE

**HUMAN-SELECTED OPTION**: `B + A` — Dynamic Emergency Reserve with Baseline Reserve Floor

**POLICY INTENT**:
Maintain dynamic emergency reserve adapting to forecast risk, plus a dedicated baseline reserve floor above technical minimum SOC.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified.

**CURRENT IMPLEMENTATION FACT**:
soc_min = 0.20 (20% SOC) technical cell protection floor in battery.yaml.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact numerical baseline reserve floor % SOC and dynamic risk-adjustment equations.

**REQUIRED VALIDATION**:
Battery vendor degradation testing to confirm usable SOC range above 20% floor.

**FUTURE SPECIFICATION REQUIRED**:
Formulate dynamic emergency BESS reserve constraints and baseline reserve floor equation.

**STATUS**: `HUMAN_SELECTED` (`NUMERICAL_RESERVE_PENDING`)

---

### DECISION_12 — TERMINAL SOC REQUIREMENT

**HUMAN-SELECTED OPTION**: `C + B` — Dynamic Terminal SOC Requirement with Minimum SOC Floor

**POLICY INTENT**:
End-of-horizon SOC governed by dynamic requirement adapting to upcoming risk, plus a minimum terminal SOC floor.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified.

**CURRENT IMPLEMENTATION FACT**:
SOC_terminal unconstrained at horizon boundary in milp.py.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact numerical minimum terminal SOC floor % and dynamic horizon-end SOC target formulation.

**REQUIRED VALIDATION**:
Multi-day rolling MPC simulations to verify inter-day storage continuity.

**FUTURE SPECIFICATION REQUIRED**:
Specify dynamic terminal SOC constraints at horizon boundary end-step.

**STATUS**: `HUMAN_SELECTED` (`NUMERICAL_POLICY_PENDING`)

---

### DECISION_13 — FORECAST UNCERTAINTY POLICY

**HUMAN-SELECTED OPTION**: `A + D` — Deterministic Safety Margins with Real-Time MPC Feedback Correction

**POLICY INTENT**:
Account for forecast uncertainty using deterministic safety margins combined with real-time rolling MPC feedback correction.

**CURRENT DOCUMENTED REQUIREMENT**:
Qualitative goal to 'mitigate solar forecast uncertainty'.

**CURRENT IMPLEMENTATION FACT**:
Deterministic MILP optimization over point forecast in milp.py.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact numerical solar, wind, and demand uncertainty margin percentages.

**REQUIRED VALIDATION**:
Statistical analysis of historical station solar, wind, and load forecast errors.

**FUTURE SPECIFICATION REQUIRED**:
Formulate deterministic safety reserve margins and specify real-time MPC feedback execution frequency.

**STATUS**: `HUMAN_SELECTED` (`NUMERICAL_UNCERTAINTY_POLICY_PENDING`)

---

### DECISION_14 — FUEL VS RELIABILITY TRADE-OFF

**HUMAN-SELECTED OPTION**: `A + C` — Reliability Absolute Priority; Fuel Minimized Subject to Reliability & Budget

**POLICY INTENT**:
Critical reliability has absolute priority. Fuel minimized subject to reliability SLA and fuel budget limits. Critical load never sacrificed for fuel.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified qualitative balance.

**CURRENT IMPLEMENTATION FACT**:
16,000:1 objective cost ratio ($10,000/$0.625) & ~0.3716 L/kWh empirical V2 ratio.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact mathematical formulation of Stage-1 hard reliability vs Stage-2 fuel minimization.

**REQUIRED VALIDATION**:
Mathematical proof and MILP solver verification of lexicographic dominance.

**FUTURE SPECIFICATION REQUIRED**:
Construct multi-stage lexicographic objective function enforcing absolute reliability dominance over fuel.

**STATUS**: `HUMAN_SELECTED` (`FORMAL_OBJECTIVE_TRANSLATION_PENDING`)

---

### DECISION_15 — OBJECTIVE PRIORITY ORDER

**HUMAN-SELECTED OPTION**: `A` — Strict Lexicographic Priority Structure (Reliability -> Resilience -> Fuel -> Renewables)

**POLICY INTENT**:
1. Critical reliability -> 2. Emergency battery reserve / resilience -> 3. Fuel conservation -> 4. Renewable utilization.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified priority hierarchy.

**CURRENT IMPLEMENTATION FACT**:
Single composite scalar weighted objective function in milp.py.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Exact mathematical multi-stage solver formulation implementing 4-tier lexicographic priority.

**REQUIRED VALIDATION**:
Solver execution benchmark across 4-stage lexicographic optimization problems.

**FUTURE SPECIFICATION REQUIRED**:
Formulate 4-stage lexicographic MILP objective structure.

**STATUS**: `HUMAN_SELECTED` (`FORMAL_LEXICOGRAPHIC_IMPLEMENTATION_PENDING`)

---

### DECISION_16 — GOVERNANCE APPROVAL AUTHORITY

**HUMAN-SELECTED OPTION**: `C` — Multi-Tier Governance Approval Structure

**POLICY INTENT**:
Three distinct approval tiers: 1. Technical validation, 2. Mission / operations validation, 3. Final policy approval.

**CURRENT DOCUMENTED REQUIREMENT**:
Unspecified organizational governance structure.

**CURRENT IMPLEMENTATION FACT**:
Ad-hoc engineering development choices in prototype scripts.

**IS CURRENT IMPLEMENTATION A STAKEHOLDER POLICY?**:
NO — Current implementation parameters reflect prototype engineering defaults, NOT stakeholder policy.

**UNRESOLVED PARAMETER / DETAIL**:
`PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION`: Named organizational individuals and board positions assigned to each approval tier.

**REQUIRED VALIDATION**:
Formal organizational governance charter approval.

**FUTURE SPECIFICATION REQUIRED**:
Specify change control protocol, technical review board workflow, and sign-off archiving.

**STATUS**: `HUMAN_SELECTED` (`ORGANIZATIONAL_DETAILS_PENDING`)

---

## UNRESOLVED PARAMETERS & PENDING FIELDS REGISTER

The following numerical, technical, and organizational details remain unresolved and must be established during subsequent station engineering and governance phases:

1. **Circuit Load Mapping**: Actual station equipment and circuit-level mapping into Critical, Essential, and Interruptible tiers.
2. **Load Shedding Queue**: Exact priority shedding sequence, restoration trigger thresholds, and dwell time parameters.
3. **Hardware Service SLA Validation**: Physical station hardware capability to guarantee 100% continuous service under worst-case weather stress.
4. **Emergency Mode Boundary Triggers**: Operational triggers and logging protocols for declared emergency modes when 0 kWh becomes unachievable.
5. **Physical Interruption Capability**: Measurement of automatic transfer switch (ATS) gap and local UPS hold-up times.
6. **Mathematical Solver Formulation**: Multi-stage lexicographic MILP mathematical formulation with hard Stage-1 reliability boundary.
7. **Fuel Curve Calibration**: Exact fuel curve quadratic coefficients ($a P^2 + b P + c u$) for converting electric output to liters across temperatures.
8. **Fuel Budget & Logistics**: Station fuel tank storage volume, resupply delivery interval, and seasonal liter allocation.
9. **Renewable Curtailment KPI**: Tracking KPI formulation for avoidable vs unavoidable curtailment.
10. **Emergency Reserve %**: Exact numerical baseline reserve floor % SOC and dynamic risk-adjustment equations.
11. **Terminal SOC Floor %**: Exact numerical minimum terminal SOC floor % and dynamic horizon-end SOC target formulation.
12. **Forecast Uncertainty Margins**: Exact numerical solar, wind, and demand uncertainty margin percentages derived from empirical error data.
13. **Governance Role Assignment**: Named organizational individuals and board positions assigned to Technical, Mission/Ops, and Final Approval tiers.

---

## FUTURE TRANSLATION BOUNDARY & NEXT GOVERNED STEP

The human stakeholder decision sheet captured here defines **POLICY INTENT ONLY**. It does NOT alter code or mathematical formulations.

### Next Governed Sequence
```
STAKEHOLDER DECISIONS (HUMAN_SELECTED_CAPTURED)
        ↓
HUMAN POLICY PACKAGE REVIEW (NEXT_GOVERNED_STEP)
        ↓
GOVERNED EMS OBJECTIVE SPECIFICATION
        ↓
IMPLEMENTATION SPECIFICATION
        ↓
GOVERNANCE AUTHORIZATION
        ↓
CODE / CONFIGURATION CHANGE
        ↓
STATIC VALIDATION
        ↓
CONTROLLED EMS VALIDATION
        ↓
GOVERNED EXPERIMENT
```

---

## FINAL GOVERNANCE STATUS

```yaml
STAKEHOLDER_DECISION_SHEET_STATUS: POPULATED_WITH_HUMAN_SELECTED_POLICIES
DECISIONS_TOTAL: 16
DECISIONS_HUMAN_SELECTED: 16
DECISIONS_REMAINING_WITHOUT_SELECTED_POLICY: 0
NUMERICAL_PARAMETERS_PENDING: YES
STATION_SPECIFIC_VALIDATION_PENDING: YES
ORGANIZATIONAL_GOVERNANCE_DETAILS_PENDING: YES
CURRENT_EMS_IMPLEMENTATION: FROZEN
CURRENT_EMS_OBJECTIVE: FROZEN
OBJECTIVE_MODIFICATION: NOT_AUTHORIZED
EMS_MODIFICATION: NOT_AUTHORIZED
EMS_EXECUTION: NOT_AUTHORIZED
MPC_EXECUTION: NOT_AUTHORIZED
MODEL_TRAINING: NOT_AUTHORIZED
MODEL_MODIFICATION: NOT_AUTHORIZED
V2_RERUN: NOT_AUTHORIZED
NEW_EMS_EXPERIMENT: NOT_AUTHORIZED
POLICY_RECOMMENDATION: NONE
POLICY_RANKING: NONE
POLICY_IMPLEMENTATION: NOT_AUTHORIZED
NEXT_GOVERNED_STEP: HUMAN_POLICY_PACKAGE_REVIEW
FOLLOWING_STEP: GOVERNED_EMS_OBJECTIVE_SPECIFICATION
```
