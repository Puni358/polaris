# POLARIS EMS STAKEHOLDER POLICY PROPOSAL
# EVIDENCE QUALIFICATION & GOVERNANCE REVIEW

**Document Version**: 1.0.0-REVIEW  
**Target Proposal**: Role-Based Stakeholder Policy Proposal (`POLAR_STATION_RESEARCH_MANAGER`)  
**Governance Status**: REVIEW_COMPLETE — ADVISORY_STAKEHOLDER_INPUT  
**Timestamp**: 2026-09-21T17:24:12.917593+00:00  

---

> [!IMPORTANT]
> **GOVERNANCE DIRECTIVE**: This review is a **READ-ONLY EVIDENCE QUALIFICATION EXERCISE**. It evaluates the role-based proposal submitted from the perspective of the `POLAR_STATION_RESEARCH_MANAGER`. This review does **NOT** authorize any policy decisions, does **NOT** modify the frozen EMS implementation (`milp.py`), does **NOT** alter configuration files, and does **NOT** execute any optimization, simulation, or model inference.

---

## 1. EXECUTIVE SUMMARY & GOVERNANCE BOUNDARIES

The attached proposal represents an extensive, role-based policy formulation from a **Polar Station Research Manager** perspective, addressing all 16 unresolved POLARIS EMS stakeholder policy decisions.

### Key Evidence Qualification Findings
1. **Nature of Input**: The proposal is a `ROLE_BASED_STAKEHOLDER_PROPOSAL`. It is **NOT** formally authorized POLARIS policy (`STAKEHOLDER_AUTHORIZATION = NOT_GRANTED`).
2. **Supported Implementation Facts**: The proposal accurately acknowledges current implementation baselines, including:
   - The `$10,000/kWh` unmet load penalty (`c_unmet` in `milp.py` / `optimizer.yaml`) is a software implementation artifact, not an authorized policy SLA.
   - The `16,000:1` coefficient ratio (`$10,000/kWh` / `$0.625/kWh`) is an objective cost ratio, not a physical fuel/reliability exchange rate.
   - The `~0.3716 L/kWh` V2 empirical ratio is a trajectory-dependent outcome (`MECHANISM_PARTIALLY_ESTABLISHED`), not a universal policy coefficient.
   - The `20%` technical minimum battery SOC limit (`battery.yaml`) is a hardware protection floor, not an operational emergency reserve.
3. **Provisional Numerical Assumptions**: The proposal introduces 20 specific numerical values (e.g. 35% EBR, 45% precautionary EBR, 55–65% terminal SOC, 15–25% solar derate, 30-day fuel reserve). All 20 numbers are classified as `PROVISIONAL_REQUIRES_STATION_SPECIFIC_VALIDATION`. None are established by current POLARIS evidence.

---

## 2. SUMMARY CLASSIFICATION TABLE (ALL 16 DECISIONS)

| ID | Decision Name | Categories Applied | Evidence Status | Numerical Values Proposed | Station Data Req. | Eng. Val. Req. | Human Auth. Req. |
|----|---------------|-------------------|-----------------|---------------------------|-------------------|----------------|------------------|
| 01 | Critical Load Classification | B, D, E | NOT_ESTABLISHED | None (5-tier scheme) | YES | YES | YES |
| 02 | Load Shedding Classification | B, C, D, E | NOT_ESTABLISHED | 5 min dwell time | YES | YES | YES |
| 03 | Minimum Critical-Load Service | A, B, C, D, E | PARTIALLY_SUPPORTED | 100% service target | YES | YES | YES |
| 04 | Max Acceptable Unmet Critical Load | A, B, C, D, E, F | PARTIALLY_SUPPORTED | 0 kWh / 15m / 2 kWh / 30d | YES | YES | YES |
| 05 | Max Continuous Interruption | B, C, D, E | NOT_ESTABLISHED | 0s / 5s / 30m / 8h / 24h | YES | YES | YES |
| 06 | Reliability Formulation | A, B, D, E | PARTIALLY_SUPPORTED | None (Hybrid math formulation) | NO | YES | YES |
| 07 | Definition of "Minimize Diesel Use" | A, B, D, E | PARTIALLY_SUPPORTED | None (Liters primary metric) | YES | YES | YES |
| 08 | Fuel Ceiling / Budget | B, C, D, E | NOT_ESTABLISHED | 30 days reserve | YES | YES | YES |
| 09 | Renewable Utilization Target | A, B, C, D, E, F | PARTIALLY_SUPPORTED | 50–70% (polar-day) | YES | YES | YES |
| 10 | Renewable Curtailment Policy | A, B, D, E | PARTIALLY_SUPPORTED | None (Free spill allowed) | YES | YES | YES |
| 11 | Emergency Battery Reserve | A, B, C, D, E | PARTIALLY_SUPPORTED | 35% normal / 45% prec / 20% min | YES | YES | YES |
| 12 | Terminal SOC Requirement | A, B, C, D, E | PARTIALLY_SUPPORTED | 35% min / 55–65% target | YES | YES | YES |
| 13 | Forecast Uncertainty Policy | A, B, C, D, E | PARTIALLY_SUPPORTED | Solar 15-25% / Wind 20-30% / Dem +10% / 1-6h | YES | YES | YES |
| 14 | Fuel-vs-Reliability Trade-Off | A, B, D, E | PARTIALLY_SUPPORTED | Ref: 16,000:1 & ~0.3716 L/kWh | NO | YES | YES |
| 15 | Objective Priority Order | A, B, D, E | PARTIALLY_SUPPORTED | None (8-level hierarchy) | NO | YES | YES |
| 16 | Governance Approval Authority | A, B, C, D | PARTIALLY_SUPPORTED | 72 hours reporting window | NO | NO | YES |

*Category Key: A = Directly Supported Evidence Fact; B = Role-Based Stakeholder Proposal; C = Provisional Numerical Assumption; D = Human Authorization Required; E = Engineering Validation Required; F = Clarification / Internal Consistency Issue.*

---

## 3. DETAILED DECISION-BY-DECISION EVIDENCE QUALIFICATION

### DECISION_01 — CRITICAL LOAD CLASSIFICATION

**AI PROPOSED POSITION**:
Adopt 5-tier load classification (CRITICAL, ESSENTIAL, DEFERRABLE, INTERRUPTIBLE, NONCRITICAL) based on consequence of loss rather than academic discipline.

**PROPOSAL CLASSIFICATION**: `B, D, E`

**CURRENT POLARIS EVIDENCE**: loads.yaml defines single aggregate demand profile P_load without tiering. No 5-tier classification exists in documented project specs.

**EVIDENCE STATUS**: `NOT_ESTABLISHED`

**SOURCE EVIDENCE**: [system/config/loads.yaml:load_profiles](file:///system/config/loads.yaml)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 5-tier classification or specific load categorizations for research station equipment.

**NUMERICAL VALUES PROPOSED**: None (classification scheme) (`Not Applicable`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_02 — LOAD SHEDDING CLASSIFICATION

**AI PROPOSED POSITION**:
CRITICAL loads never auto-shed except in declared CRITICAL_INFRASTRUCTURE_EMERGENCY or BATTERY_EMERGENCY. ESSENTIAL shed after DEFERRABLE/INTERRUPTIBLE. NONCRITICAL shed first. 5-min restoration dwell.

**PROPOSAL CLASSIFICATION**: `B, C, D, E`

**CURRENT POLARIS EVIDENCE**: milp.py and optimizer.yaml implement uniform soft penalty c_unmet = $10,000/kWh for all load. No tiered shedding rules or restoration dwell times implemented.

**EVIDENCE STATUS**: `NOT_ESTABLISHED`

**SOURCE EVIDENCE**: [system/config/optimizer.yaml:penalties.c_unmet](file:///system/config/optimizer.yaml)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish tiered automated load shedding queues or 5-minute restoration dwell logic.

**NUMERICAL VALUES PROPOSED**: 5 minutes (restoration dwell time) (`Provisional Assumption`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_03 — MINIMUM CRITICAL-LOAD SERVICE REQUIREMENT

**AI PROPOSED POSITION**:
100% continuous energy service to CRITICAL loads during NORMAL_OPERATION and FORECAST_DEGRADED modes; best achievable service during declared emergencies.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E`

**CURRENT POLARIS EVIDENCE**: Project specs document qualitative goal for high reliability. No numerical 100% continuous service SLA or emergency best-effort policy documented.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md:Section 3.1](file:///POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish explicit 100% numerical SLA percentage or formal emergency best-effort carve-out.

**NUMERICAL VALUES PROPOSED**: 100% (service level in normal/degraded modes) (`Provisional Target`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_04 — MAXIMUM ACCEPTABLE UNMET CRITICAL LOAD

**AI PROPOSED POSITION**:
0 kWh unmet CRITICAL load in normal/degraded modes (hard constraint). Bounded operationally in emergencies. Review triggers: 15 min continuous outage or 2 kWh / 30 days. Rejects $10,000/kWh penalty as stakeholder policy.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E, F`

**CURRENT POLARIS EVIDENCE**: milp.py contains $10,000/kWh penalty coefficient (implementation evidence). Review confirms $10,000/kWh is software artifact, not stakeholder policy. 0 kWh constraint and review triggers are unestablished.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/optimization/implementations/milp.py:c_unmet](file:///system/optimization/implementations/milp.py)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 0 kWh hard constraint or 15-min / 2-kWh review triggers as policy.

**NUMERICAL VALUES PROPOSED**: 0 kWh (target), 15 minutes (event trigger), 2 kWh / 30 days (cumulative trigger) (`Provisional Assumptions`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `YES — Boundary triggers separating FORECAST_DEGRADED mode (0 kWh target) from EMERGENCY mode require precise operational definition.`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_05 — MAXIMUM CONTINUOUS INTERRUPTION

**AI PROPOSED POSITION**:
Tiered max continuous interruption: CRITICAL 0s target / 5s max gap; ESSENTIAL 30m; DEFERRABLE 8h (480m); INTERRUPTIBLE 24h (1440m); NONCRITICAL no max.

**PROPOSAL CLASSIFICATION**: `B, C, D, E`

**CURRENT POLARIS EVIDENCE**: optimizer.yaml defines dt = 1.0 hour timestep without inter-step interruption constraints or tier-differentiated outage limits.

**EVIDENCE STATUS**: `NOT_ESTABLISHED`

**SOURCE EVIDENCE**: [system/config/optimizer.yaml:time_step](file:///system/config/optimizer.yaml)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish sub-hour transfer gaps (5s) or tier outage limits (30m, 8h, 24h).

**NUMERICAL VALUES PROPOSED**: 0s / 5s (CRITICAL), 30 minutes (ESSENTIAL), 480 minutes (DEFERRABLE), 1440 minutes (INTERRUPTIBLE) (`Provisional Assumptions`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_06 — RELIABILITY FORMULATION

**AI PROPOSED POSITION**:
Hybrid hard-constraint (normal/degraded) + lexicographic fallback (emergency). Reject single soft penalty scalar objective.

**PROPOSAL CLASSIFICATION**: `A, B, D, E`

**CURRENT POLARIS EVIDENCE**: milp.py baseline uses single scalar objective with soft penalty c_unmet * P_unmet. Proposed hybrid hard + lexicographic formulation is unestablished in code.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/optimization/implementations/milp.py:objective_function](file:///system/optimization/implementations/milp.py)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish lexicographic multi-stage solver formulation or hard-constraint reliability in milp.py.

**NUMERICAL VALUES PROPOSED**: None (formulation architecture) (`Not Applicable`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `NO`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_07 — DEFINITION OF "MINIMIZE DIESEL USE"

**AI PROPOSED POSITION**:
Primary metric = liters of diesel consumed. Secondary metrics = runtime hours, start count, fuel expenditure ($). Rejects treating cost or kWh as equivalent to liters.

**PROPOSAL CLASSIFICATION**: `A, B, D, E`

**CURRENT POLARIS EVIDENCE**: diesel.yaml provides quadratic fuel curve (a*P^2 + b*P + c*u) and marginal fuel cost ($0.625/kWh). Specs state qualitative goal to minimize diesel reliance.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/config/diesel.yaml:fuel_curve](file:///system/config/diesel.yaml)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish liters as primary explicit metric over runtime or financial cost.

**NUMERICAL VALUES PROPOSED**: None (metric definition) (`Not Applicable`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_08 — FUEL CEILING / BUDGET

**AI PROPOSED POSITION**:
Monthly soft operating budget + protected 30-day emergency fuel reserve for CRITICAL+ESSENTIAL loads.

**PROPOSAL CLASSIFICATION**: `B, C, D, E`

**CURRENT POLARIS EVIDENCE**: No fuel budget ceiling or 30-day emergency reserve constraint exists in milp.py or system configs.

**EVIDENCE STATUS**: `NOT_ESTABLISHED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md:Section 4.2](file:///POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish monthly fuel ceilings or 30-day emergency fuel reserve.

**NUMERICAL VALUES PROPOSED**: 30 days (emergency fuel reserve coverage) (`Provisional Assumption`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_09 — RENEWABLE UTILIZATION TARGET

**AI PROPOSED POSITION**:
Renewable energy served to load as fraction of total load served. Target 50–70% for polar-day months; no target for polar-night months.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E, F`

**CURRENT POLARIS EVIDENCE**: Specs contain qualitative goal 'maximize renewable integration'. No numerical 50-70% seasonal target or load-served KPI documented.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md:Section 2.1](file:///POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 50-70% polar-day target or seasonal exemption rules.

**NUMERICAL VALUES PROPOSED**: 50–70% (polar-day renewable utilization target) (`Provisional Assumption`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `YES — Potential dispatch conflict between 50-70% renewable target and 55-65% terminal SOC target (Decision 12) if battery storage is undersized.`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_10 — RENEWABLE CURTAILMENT POLICY

**AI PROPOSED POSITION**:
Curtailment allowed freely without penalty to protect battery SOC or generator stability. Minimized when costless. Tracked, not penalized.

**PROPOSAL CLASSIFICATION**: `A, B, D, E`

**CURRENT POLARIS EVIDENCE**: milp.py leaves P_pv_curtail unpenalized in objective function. This establishes the CURRENT_IMPLEMENTATION_FACT, but does NOT establish authorized stakeholder policy.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/optimization/implementations/milp.py:solar_balance](file:///system/optimization/implementations/milp.py)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish explicit reporting protocols or soft-minimization rules.

**NUMERICAL VALUES PROPOSED**: None (policy choice) (`Not Applicable`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_11 — EMERGENCY BATTERY RESERVE

**AI PROPOSED POSITION**:
Dedicated Emergency Battery Reserve (EBR) of 35% SOC (normal) / 45% SOC (precautionary). Distinct from 20% technical minimum SOC floor.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E`

**CURRENT POLARIS EVIDENCE**: battery.yaml sets soc_min = 0.20 (technical minimum cell protection floor). 35% EBR and 45% precautionary SOC floors are unestablished.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/config/battery.yaml:soc_limits](file:///system/config/battery.yaml)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 35% normal EBR or 45% precautionary EBR as operational reserve policies.

**NUMERICAL VALUES PROPOSED**: 35% SOC (normal EBR), 45% SOC (precautionary EBR), ~20% (technical min SOC) (`Provisional Assumptions`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_12 — TERMINAL SOC REQUIREMENT

**AI PROPOSED POSITION**:
Terminal SOC floor = EBR (35% min under normal conditions); precautionary target = 55–65% ahead of storms / polar night. Relaxed in active emergencies.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E`

**CURRENT POLARIS EVIDENCE**: milp.py has no terminal SOC constraint. 35% floor and 55-65% precautionary target are unestablished in current codebase.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [system/optimization/implementations/milp.py:terminal_constraints](file:///system/optimization/implementations/milp.py)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 35% min terminal SOC or 55-65% storm target.

**NUMERICAL VALUES PROPOSED**: 35% SOC (minimum terminal SOC), 55–65% SOC (precautionary terminal SOC) (`Provisional Assumptions`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_13 — FORECAST UNCERTAINTY POLICY

**AI PROPOSED POSITION**:
Conservative deterministic derate + receding-horizon re-optimization (every 1–6 hours). Derates: Solar 15–25%; Wind 20–30%; Demand +10%.

**PROPOSAL CLASSIFICATION**: `A, B, C, D, E`

**CURRENT POLARIS EVIDENCE**: Project review notes qualitative goal to mitigate solar forecast uncertainty. milp.py uses deterministic point forecast. Derate margins (15-25%, 20-30%, +10%) are unestablished.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md:Forecast Uncertainty](file:///POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish specific numerical derate margins or 1-6h re-optimization frequency.

**NUMERICAL VALUES PROPOSED**: 15–25% (solar derate), 20–30% (wind derate), +10% (demand margin), 1–6 hours (re-optimization interval) (`Provisional Assumptions`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `YES`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_14 — FUEL-VS-RELIABILITY TRADE-OFF

**AI PROPOSED POSITION**:
Reliability hard priority over fuel in normal/degraded modes; mode-based lexicographic shift in emergency. Rejects 16,000:1 ratio and ~0.3716 L/kWh V2 empirical ratio as policy coefficients.

**PROPOSAL CLASSIFICATION**: `A, B, D, E`

**CURRENT POLARIS EVIDENCE**: Stakeholder review confirms 16,000:1 is objective cost coefficient ratio ($10,000/kWh / $0.625/kWh) and ~0.3716 L/kWh is trajectory-dependent empirical V2 outcome, neither being policy.

**EVIDENCE STATUS**: `SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md:Decision 14](file:///POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish formal lexicographic trade-off policy in code.

**NUMERICAL VALUES PROPOSED**: 16,000:1 (implementation ratio reference), ~0.3716 L/kWh (V2 empirical ratio reference) (`Reference / Established Evidence Facts`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `NO`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_15 — OBJECTIVE PRIORITY ORDER

**AI PROPOSED POSITION**:
8-level hierarchy: 1. Safety -> 2. Critical Reliability -> 3. Equipment Protection -> 4. Emergency Resilience -> 5. Diesel Conservation -> 6. Renewables -> 7. Cost/Wear -> 8. Comfort.

**PROPOSAL CLASSIFICATION**: `A, B, D, E`

**CURRENT POLARIS EVIDENCE**: milp.py baseline uses single scalar composite objective function. 8-level hierarchy is unestablished in codebase.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md:Section 5.1](file:///POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish explicit 8-level priority hierarchy in requirements or code.

**NUMERICAL VALUES PROPOSED**: None (priority ordering) (`Not Applicable`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `NO`
- ENGINEERING_VALIDATION_REQUIRED: `YES`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

### DECISION_16 — GOVERNANCE APPROVAL AUTHORITY

**AI PROPOSED POSITION**:
6 distinct governance roles: Propose, Review, Validate, Approve, Emergency-Authorize, Record. 72-hour emergency reporting window.

**PROPOSAL CLASSIFICATION**: `A, B, C, D`

**CURRENT POLARIS EVIDENCE**: Stakeholder review notes absence of formal governance approval structure in project specs.

**EVIDENCE STATUS**: `PARTIALLY_SUPPORTED`

**SOURCE EVIDENCE**: [POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md:Decision 16](file:///POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW/POLARIS_EMS_OBJECTIVE_STAKEHOLDER_REVIEW.md)

**WHAT THE EVIDENCE DOES NOT ESTABLISH**: Does not establish 6-role governance framework or 72-hour reporting window.

**NUMERICAL VALUES PROPOSED**: 72 hours (emergency reporting window) (`Provisional Assumption`)

**GOVERNANCE FLAGS**:
- STATION_SPECIFIC_DATA_REQUIRED: `NO`
- ENGINEERING_VALIDATION_REQUIRED: `NO`
- HUMAN_AUTHORIZATION_REQUIRED: `YES`
- CLARIFICATION_REQUIRED: `NO`

**GOVERNANCE STATUS**: `PROPOSAL_ONLY`

---

## 4. POLICY VS. ENGINEERING SEPARATION MATRIX

| Decision ID | Policy Question (Human Stakeholder Choice) | Engineering Question (Technical Validation Needed) |
|-------------|-------------------------------------------|----------------------------------------------------|
| DECISION_01 | Which station loads are classified as Critical vs Essential vs Sheddable? | How are individual circuits wired and metered to support 5-tier relay control? |
| DECISION_02 | Under what emergency conditions is automated shedding authorized? | What is the switching speed and restoration dwell time capability of station relays? |
| DECISION_03 | What minimum critical load service percentage is required? | Can worst-case generator/battery capacity physically guarantee 100% load under weather stress? |
| DECISION_04 | What maximum unmet critical load is acceptable before manual intervention? | What automated review triggers (minutes/kWh) can be logged reliably in control software? |
| DECISION_05 | What continuous outage duration can equipment and personnel tolerate? | What is the actual thermal drop rate of lab freezers, buildings, and communications UPS buffers? |
| DECISION_06 | Should reliability be a hard constraint or soft objective penalty? | How can a hard constraint + lexicographic fallback be formulated in MILP without solver stalling? |
| DECISION_07 | Is liters of diesel the primary fuel metric over runtime or financial cost? | How accurate are generator quadratic fuel curves (a*P^2 + b*P + c*u) across ambient temperature ranges? |
| DECISION_08 | Should the station maintain a monthly fuel budget and emergency fuel reserve? | What is total fuel tank storage capacity, delivery cadence, and worst-case isolation window? |
| DECISION_09 | What seasonal renewable utilization targets should apply? | What is the site solar irradiance, wind resource distribution, and seasonal PV profile? |
| DECISION_10 | Is renewable curtailment acceptable to protect batteries and generators? | What are minimum stable generator loading limits and battery maximum charge acceptance rates? |
| DECISION_11 | What operational Emergency Battery Reserve (EBR) floor should be maintained? | What is true battery cell degradation floor (SOC min) vs usable operational capacity? |
| DECISION_12 | What terminal SOC requirement should end each optimization horizon? | What horizon length (24h vs 48h) and overnight energy draw prevent systematic BESS depletion? |
| DECISION_13 | What forecast uncertainty margins and re-optimization intervals should be used? | What are historical solar, wind, and demand forecast-vs-actual error distributions at this site? |
| DECISION_14 | What explicit priority balance should exist between fuel and reliability? | How can multi-objective scalar weights be tuned to guarantee lexicographic priority dominance? |
| DECISION_15 | What 8-level priority hierarchy governs multi-objective trade-offs? | Can an 8-stage lexicographic MILP or multi-criteria optimization execute within real-time bounds? |
| DECISION_16 | What 6-role governance structure should oversee policy changes? | How will policy parameters, change logs, and emergency override alarms be archived in software? |

---

## 5. EXECUTION FIREWALL & IMMUTABILITY CONFIRMATION

- **MODEL_TRAINING**: `0`
- **MODEL_INFERENCE**: `0`
- **MILP_EXECUTION**: `0`
- **MPC_EXECUTION**: `0`
- **EMS_EXECUTION**: `0`
- **DIGITAL_TWIN_EXECUTION**: `0`
- **SIMULATION**: `0`
- **V2_RERUN**: `0`
- **SENSITIVITY_ANALYSIS**: `0`

---

## 6. FINAL REVIEW SUMMARY & GOVERNANCE STATUS

```yaml
AI_POLICY_PROPOSAL_REVIEW: COMPLETE
ROLE_BASED_PROPOSAL: RECEIVED
DECISIONS_TOTAL: 16
CATEGORY_COUNTS:
  A_DIRECTLY_SUPPORTED: 11
  B_ROLE_BASED_PROPOSAL: 16
  C_PROVISIONAL_NUMERICAL_ASSUMPTION: 9
  D_HUMAN_AUTHORIZATION_REQUIRED: 16
  E_ENGINEERING_VALIDATION_REQUIRED: 15
  F_CLARIFICATION_REQUIRED: 2
FORMAL_STAKEHOLDER_AUTHORIZATION: NOT_GRANTED
OFFICIAL_DECISION_SHEET_MODIFIED: NO
EMS_MODIFIED: NO
OBJECTIVE_MODIFIED: NO
MILP_EXECUTED: NO
MPC_EXECUTED: NO
DIGITAL_TWIN_EXECUTED: NO
V2_RERUN: NO
POLICY_RECOMMENDATION_BY_REVIEW: NONE
POLICY_RANKING_BY_REVIEW: NONE
NEXT_GOVERNED_STEP: HUMAN_REVIEW_OF_ROLE_BASED_POLICY_PROPOSAL
```
