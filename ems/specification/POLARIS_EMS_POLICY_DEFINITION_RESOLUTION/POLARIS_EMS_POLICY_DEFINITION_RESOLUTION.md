# POLARIS EMS POLICY DEFINITION RESOLUTION
## FORMAL GOVERNED POLICY-DEFINITION PHASE

**Package Label**: `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION`
**Document Version**: 1.1.0 (corrects v1.0.0 — see CORRECTION_MANIFEST)
**Governance Status**: `POLICY_DEFINITION_RESOLUTION = CONDITIONAL`
**Prepared**: 2026-09-22T00:10:00Z

---

## ABSOLUTE GOVERNANCE BOUNDARIES

```yaml
SYSTEM_STATUS:              FROZEN
EMS_MODIFICATION:           NOT_AUTHORIZED
OBJECTIVE_MODIFICATION:     NOT_AUTHORIZED
EMS_EXECUTION:              NOT_AUTHORIZED
MPC_EXECUTION:              NOT_AUTHORIZED
MODEL_TRAINING:             NOT_AUTHORIZED
MILP_EXECUTION:             NOT_AUTHORIZED
SIMULATION_EXECUTION:       NOT_AUTHORIZED
EXPERIMENT_EXECUTION:       NOT_AUTHORIZED
POLICY_RECOMMENDATION:      NONE
POLICY_RANKING:             NONE
NEXT_GOVERNED_STEP:         HUMAN_POLICY_PACKAGE_REVIEW
FOLLOWING_STEP:             GOVERNED_EMS_OBJECTIVE_SPECIFICATION
```

**Three-Layer Governance Separation (MANDATORY)**:
```
CURRENT_IMPLEMENTATION (FROZEN)
    ≠
HUMAN_SELECTED_STAKEHOLDER_POLICY (16 DECISIONS — FIXED)
    ≠
FUTURE_GOVERNED_EMS_OBJECTIVE_SPECIFICATION (NOT_YET_CREATED)
```

The 16 stakeholder decisions captured in `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET/` are
FIXED inputs to this document. They are NOT reopened, NOT reordered, NOT ranked,
and NOT modified here.

---

## STATUS MODEL USED IN THIS DOCUMENT

| Label | Meaning |
|-------|---------|
| `HUMAN_SELECTED_POLICY` | Directly traceable to the 16 fixed stakeholder decisions — immutable |
| `CONCEPTUALLY_RESOLVED` | Policy relationship or structure clarified from stakeholder decisions |
| `CONCEPTUAL_POLICY_FRAMEWORK` | Illustrative organizing concept; not formally authorized |
| `PROVISIONAL_ENGINEERING_VALUE` | From advisory stakeholder proposal; not authorized; requires validation |
| `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE` | Example not yet mapped to actual station; not authorized |
| `STATION_SPECIFIC_VALIDATION_REQUIRED` | Cannot be resolved without physical station data |
| `NUMERICAL_CALIBRATION_REQUIRED` | Numerical value pending empirical/engineering derivation |
| `NEXT_EMS_OBJECTIVE_SPECIFICATION` | Must be formally produced in the Specification phase |
| `FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED` | Requires formal governance sign-off |
| `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` | Not traceable to any authoritative source |
| `NOT_STAKEHOLDER_AUTHORIZED` | Not selected by stakeholder; must not enter Specification as policy |
| `CURRENT_IMPLEMENTATION_FACT` | What the frozen prototype software does — NOT policy |

---

## PURPOSE OF THIS DOCUMENT

This document reviews the **10 policy-definition areas** that must be settled before
the POLARIS Governed EMS Objective Specification can be written.

**Assessment**: Policy logic and relationships are conceptually resolved for all 10 areas.
Numerical parameters, station-specific mappings, and mathematical formulations remain
pending throughout. The overall status is therefore `CONDITIONAL`.

For each area this document provides:
1. The governing stakeholder decisions (fixed reference)
2. Evidence classified by type
3. The policy relationship resolved conceptually
4. What remains pending before this area can enter the Objective Specification

---

## EVIDENCE BASE: FROZEN IMPLEMENTATION FACTS

The following facts are established from frozen system artifacts.
They are `CURRENT_IMPLEMENTATION_FACT` only — NOT stakeholder policy.

| File | SHA-256 | Key Values |
|------|---------|------------|
| `system/optimization/implementations/milp.py` | `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` | composite scalar objective; c_unmet=$10,000/kWh; c_marg=$0.625/kWh; terminal SOC unconstrained |
| `system/config/battery.yaml` | `eb06f81d8b11364e254cbcd5c37a4769874f8703e9e86e3b067b60d8858da216` | 200 kWh capacity; SOC_min=20%; SOC_max=95%; charge/discharge=50 kW; deg=$0.00005/Wh |
| `system/config/diesel.yaml` | `421120967328e18366daf41b682fc9f1cbe91b0f9ebe2133b83290bb9e294ac3` | min=10 kW; max=100 kW; base=5.0 L/h; marginal=0.25 L/kWh; startup=$15; min_up=2h |
| `system/config/loads.yaml` | `ab6943d72f2054b001274de5a3fe229c9987eb31fb11be0422f33754fd5f3cad` | baseline_critical=30,000 W; deferrable water_pump=10 kW/4h; curtailable heat=5 kW |
| `system/config/optimizer.yaml` | `bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8` | RULE_BASED_HEURISTIC_D1; unmet penalty weight=1000.0 |
| `system/config/solar_pv.yaml` | `611521090b7d551614c23d91fc190320a42bccee667929618d40bab987262e5e` | array=300 m²; efficiency=20%; PR=0.85; max_inverter=60 kW |
| `system/config/station.yaml` | `e021368133587b5752b9471722d7997d1cd2aa2d674697a47b1b2f5b06052e42` | SITES Nuolja; Lat=68.36°N; Lon=18.74°E |

These SHA-256 values are the authoritative frozen reference. No `system/` file was modified.

---

## 10 POLICY-DEFINITION AREAS REVIEW

**Summary status**: 10/10 areas conceptually reviewed with policy relationships identified.
0/10 areas have finalized numerical parameters.
Overall status = `CONDITIONAL`.

---

### AREA 1 — EMERGENCY MODE ENTRY CONDITIONS AND OPERATING MODES

**Governing Stakeholder Decisions**: D01, D02, D03, D04, D05, D06, D14, D15
**Area Status**: `CONCEPTUALLY_RESOLVED — FORMAL_SPECIFICATION_PENDING`

#### 1.1 Policy Logic (HUMAN_SELECTED_POLICY)

From the fixed stakeholder decisions:
- The EMS must distinguish between at least two operational states: one where the
  100% Critical service hard constraint applies (D03, D04), and one where emergency
  conditions relax that constraint and activate the lexicographic fallback (D06).
- Critical load shedding is authorized only as a declared-emergency last resort (D02).
- The lexicographic priority hierarchy applies during emergency conditions (D06, D15).
- The fuel budget is never a constraint that forces Critical load shedding (D08, D14).

These policy relationships are `CONCEPTUALLY_RESOLVED` from the stakeholder decisions.

#### 1.2 Conceptual Operating Mode Framework

> **CLASSIFICATION: `CONCEPTUAL_POLICY_FRAMEWORK`**
> **NOT `FORMALLY_AUTHORIZED_POLICY`**
> **REQUIRES: `STAKEHOLDER_AND_ENGINEERING_VALIDATION`**

The following is an **illustrative** organizing framework consistent with the
stakeholder decisions. It is NOT formally authorized. Mode names, entry conditions,
and transition thresholds must be defined in the Governed EMS Objective Specification
and validated by station engineering and stakeholders.

Illustrative mode concepts (NOT authorized):
- A **normal/degraded mode family** where: 100% Critical service hard constraint
  applies; only non-Critical tiers may be shed automatically.
- An **emergency mode family** where: lexicographic fallback activates; Critical
  load shedding permitted only as absolute last resort after all other options exhausted;
  mandatory logging and notification required.

Mode transition trigger conditions: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
Exact mode names and boundaries: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
Numerical SOC, fuel-level, or forecast thresholds: `STATION_SPECIFIC_VALIDATION_REQUIRED`
Operating mode transition logic: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

#### 1.3 Evidence Classification

| Evidence | Type |
|----------|------|
| 100% Critical service required in normal/degraded states | `HUMAN_SELECTED_POLICY` — D03 |
| Critical shedding authorized only in declared emergency last resort | `HUMAN_SELECTED_POLICY` — D02 |
| Lexicographic fallback applies under emergency | `HUMAN_SELECTED_POLICY` — D06, D15 |
| Fuel budget is never a Critical-shedding constraint | `HUMAN_SELECTED_POLICY` — D08, D14 |
| Illustrated four-mode naming structure | `CONCEPTUAL_POLICY_FRAMEWORK` — advisory only |
| Specific mode-transition numerical thresholds | `STATION_SPECIFIC_VALIDATION_REQUIRED` |
| Current MILP uses single operating mode — no mode switching | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen) |

---

### AREA 2 — LOAD SHEDDING DIRECTION AND TIER STRUCTURE

**Governing Stakeholder Decisions**: D01, D02, D03, D04, D05
**Area Status**: `CONCEPTUALLY_RESOLVED — STATION_MAPPING_AND_SPECIFICATION_PENDING`

#### 2.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D01 (A+C): Tiered load classification — at minimum three conceptual tiers:
- **Critical** — loads that must not be shed in normal/degraded operation
- **Essential / Flexible** — intermediate tier(s) with managed shedding rules
- **Interruptible / Noncritical** — lower-priority loads that may be shed first

From D02 (A+B): Automated tier-based shedding is authorized. Critical loads are
protected in normal/degraded operation. Lower-tier loads are shed first. Critical loads
may only be shed as an absolute last resort in declared emergencies.

These tier relationships and protection priorities are `HUMAN_SELECTED_POLICY`.

#### 2.2 Tier Structure Note

> **CLASSIFICATION: `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE`**
> **NOT `STAKEHOLDER_AUTHORIZED`**

A five-tier elaboration (CRITICAL / ESSENTIAL / DEFERRABLE / INTERRUPTIBLE / NONCRITICAL)
was introduced in v1.0.0 of this document. This elaboration is illustrative and draws
from an **advisory stakeholder role-based proposal** (POLAR_STATION_RESEARCH_MANAGER),
which is NOT formally authorized stakeholder policy.

The **minimum authorized conceptual structure** from D01 is three tiers:
- Tier 1: Critical (protected)
- Tier 2: Essential / Flexible (managed shedding)
- Tier 3: Interruptible / Noncritical (shed first)

Exact shedding sequence within and between tiers: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
Restoration sequence and logic: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
Circuit-level load mapping to tiers: `STATION_SPECIFIC_VALIDATION_REQUIRED`
Minimum restoration dwell time: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

**Note on 5-minute dwell value**: A figure of 5 minutes was introduced in v1.0.0.
Status: `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` — the figure originates from
the advisory proposal only and is not traceable to any authoritative POLARIS
document, configuration file, or stakeholder decision.

#### 2.3 Evidence Classification

| Evidence | Type |
|----------|------|
| Three-tier conceptual load classification selected | `HUMAN_SELECTED_POLICY` — D01 |
| Automated tier-based shedding; Critical protected | `HUMAN_SELECTED_POLICY` — D02 |
| Lower tiers shed first; Critical shed only as last resort in emergency | `HUMAN_SELECTED_POLICY` — D02 |
| Five-tier elaboration (five named sub-tiers) | `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE — NOT_STAKEHOLDER_AUTHORIZED` |
| Exact shedding priority ordering | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |
| Restoration timing and dwell value | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |
| 5-minute dwell time figure | `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| Station circuit-level load inventory | `STATION_SPECIFIC_VALIDATION_REQUIRED` |
| Current implementation: single undifferentiated load at 30,000 W baseline | `CURRENT_IMPLEMENTATION_FACT` — loads.yaml |

---

### AREA 3 — CRITICAL LOAD SERVICE LEVEL AND EXCEPTION PROTOCOL

**Governing Stakeholder Decisions**: D03, D04, D05, D06
**Area Status**: `CONCEPTUALLY_RESOLVED — ENGINEERING_VALIDATION_AND_SPECIFICATION_PENDING`

#### 3.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D03 (A): 100% continuous energy service target for Critical Loads during
normal governed operation.

From D04 (A): 0 kWh unmet Critical Load under normal governed operation.
Emergency conditions for extraordinary events require separately defined emergency policy.

From D05 (A): 0 minutes intentional interruption for Critical Loads (policy requirement).
Physical hardware transfer gaps are governed separately from this policy statement.

From D06 (D+A): During infeasibility (declared emergency), the lexicographic fallback
applies — not a soft-penalty trade-off.

These are `HUMAN_SELECTED_POLICY` and are not modified here.

#### 3.2 Enforcement Note

The policy target (100% / 0 kWh) must be implemented as a **hard constraint** in the
EMS, not as a soft economic penalty. The current frozen implementation uses a
$10,000/kWh soft penalty — this is a `CURRENT_IMPLEMENTATION_FACT` and is explicitly
NOT the policy SLA.

Mathematical formulation of the hard constraint: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
Hardware validation of physical feasibility: `ENGINEERING_VALIDATION_REQUIRED`
ATS switching gap duration: `STATION_SPECIFIC_VALIDATION_REQUIRED` (SD-02)
UPS hold-up time per Critical circuit: `STATION_SPECIFIC_VALIDATION_REQUIRED` (SD-03)

#### 3.3 Exception Protocol and Review Triggers

The stakeholder decisions establish that emergency exceptions exist and that unmet
Critical load during emergencies must be logged and reported (D04). They do not
specify numerical review-trigger thresholds.

**15-minute event trigger**: `PROVISIONAL_EXAMPLE_ONLY — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`
(Originates from advisory proposal only; must not enter Objective Specification as policy.)

**2 kWh / 30-day cumulative trigger**: `PROVISIONAL_EXAMPLE_ONLY — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`
(Same source; same classification.)

The exception protocol structure (mandatory logging, root-cause review) is
`CONCEPTUALLY_RESOLVED`. Exact trigger thresholds are `NEXT_EMS_OBJECTIVE_SPECIFICATION`.

#### 3.4 Evidence Classification

| Evidence | Type |
|----------|------|
| 100% continuous Critical service target | `HUMAN_SELECTED_POLICY` — D03 |
| 0 kWh unmet Critical load in normal/degraded operation | `HUMAN_SELECTED_POLICY` — D04 |
| Emergency exception + mandatory logging requirement | `HUMAN_SELECTED_POLICY` — D04 (structural) |
| 0 minutes intentional interruption policy | `HUMAN_SELECTED_POLICY` — D05 |
| Lexicographic fallback during infeasibility | `HUMAN_SELECTED_POLICY` — D06 |
| 15-minute event review trigger | `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| 2 kWh/30-day cumulative trigger | `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| c_unmet = $10,000/kWh soft penalty in milp.py | `CURRENT_IMPLEMENTATION_FACT` — frozen; NOT SLA policy |
| Qualitative reliability requirement in documentation | `DOCUMENTED_REQUIREMENT` — POLARIS_MASTER_HANDOFF.md |

---

### AREA 4 — FUEL METRIC DEFINITION AND OBJECTIVE POSITION

**Governing Stakeholder Decisions**: D07, D08, D14, D15
**Area Status**: `CONCEPTUALLY_RESOLVED — MATHEMATICAL_FORMULATION_PENDING`

#### 4.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D07 (A+B): Primary metric = actual liters consumed. Secondary tracked metrics
(not primary optimization targets) = generator runtime and start count.

From D14 (A+C): Fuel minimization is a secondary objective, strictly subject to
reliability SLA and fuel budget. Critical load is never sacrificed for fuel.

From D15 (A): Fuel conservation is Stage 3 in the strict lexicographic hierarchy:
Reliability → Resilience → Fuel → Renewables.

These metric selections and priority positions are `HUMAN_SELECTED_POLICY`.

#### 4.2 Liters Formulation Note

The current frozen implementation uses a cost proxy ($0.625/kWh = 2.50 $/L × 0.25 L/kWh).
This is a `CURRENT_IMPLEMENTATION_FACT` and is rejected as the policy metric (per D07).

The liters-based formulation framework (using f_base and f_marg from diesel.yaml) is
`CONCEPTUALLY_RESOLVED`. The actual implementation with calibrated fuel curves is
`NEXT_EMS_OBJECTIVE_SPECIFICATION`.

**f_base = 5.0 L/h**: `CURRENT_IMPLEMENTATION_FACT — PROTOTYPE_ASSUMPTION`
**f_marg = 0.25 L/kWh**: `CURRENT_IMPLEMENTATION_FACT — PROTOTYPE_ASSUMPTION`
Generator bench-test fuel curves: `STATION_SPECIFIC_VALIDATION_REQUIRED` (SD-04)

#### 4.3 Evidence Classification

| Evidence | Type |
|----------|------|
| Primary fuel metric = liters consumed | `HUMAN_SELECTED_POLICY` — D07 |
| Secondary metrics: runtime, start count (tracked only) | `HUMAN_SELECTED_POLICY` — D07 |
| Fuel minimization is Stage 3 lexicographic objective | `HUMAN_SELECTED_POLICY` — D14, D15 |
| Reliability strictly dominates fuel in all normal operation | `HUMAN_SELECTED_POLICY` — D14 |
| Base fuel rate 5.0 L/h; marginal 0.25 L/kWh | `CURRENT_IMPLEMENTATION_FACT` — diesel.yaml (frozen) |
| Cost proxy $0.625/kWh | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen); NOT policy metric |
| Calibrated generator fuel curves | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-04 |
| Mathematical liters-objective formulation | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |

---

### AREA 5 — FUEL BUDGET STRUCTURE AND MANAGEMENT

**Governing Stakeholder Decisions**: D08, D14
**Area Status**: `CONCEPTUALLY_RESOLVED — ALL_NUMERICAL_PARAMETERS_PENDING`

#### 5.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D08 (B+C):
- A seasonal/resupply-cycle fuel budget exists.
- Dynamic fuel management is applied (accounting for inventory, time to resupply,
  and expected renewables).
- A protected emergency fuel reserve is held back from normal operations.
- Drawing on the emergency reserve requires authorized declaration and triggers a
  mandatory resupply-planning review.

From D14 (A+C): The fuel budget is NEVER a constraint that forces unmet Critical load.
Critical reliability retains absolute priority over any fuel budget consideration.

These structural relationships are `HUMAN_SELECTED_POLICY`.

#### 5.2 Numerical Parameters (ALL PENDING)

> **ALL OF THE FOLLOWING ARE `STATION_SPECIFIC_VALIDATION_REQUIRED`:**

- Fuel budget quantity (liters): `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-05
- Budget period (resupply cycle definition): `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-05
- Resupply interval (actual schedule): `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-05
- Emergency fuel reserve volume (liters): `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-05, SD-06

**Note on 30-day emergency reserve figure**: A figure of 30 days of Critical+Essential
coverage was introduced in v1.0.0 from the advisory stakeholder proposal.
Status: `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED`.
This figure must not enter the Objective Specification as an authorized parameter.
Actual sizing: `STATION_SPECIFIC_VALIDATION_REQUIRED`.

**Note on monthly framing**: A "monthly fuel ceiling" framing was introduced in v1.0.0.
Status: `NOT_STAKEHOLDER_AUTHORIZED`. D08 specifies "seasonal/resupply-cycle" — not
necessarily monthly. Budget period must match actual resupply schedule.

Dynamic fuel-management formulation: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

#### 5.3 Evidence Classification

| Evidence | Type |
|----------|------|
| Seasonal/resupply-cycle fuel budget structure | `HUMAN_SELECTED_POLICY` — D08 |
| Dynamic fuel management (inventory + time-to-resupply + renewables) | `HUMAN_SELECTED_POLICY` — D08 |
| Protected emergency fuel reserve (held back from normal operations) | `HUMAN_SELECTED_POLICY` — D08 |
| Fuel budget never forces Critical load shedding | `HUMAN_SELECTED_POLICY` — D08, D14 |
| Budget quantity, period, and reserve volume | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-05 |
| 30-day emergency reserve sizing figure | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Monthly fuel ceiling framing | `NOT_STAKEHOLDER_AUTHORIZED` |
| No fuel budget constraint currently in milp.py | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen) |
| Qualitative fuel reduction goal | `DOCUMENTED_REQUIREMENT` — POLARIS_MASTER_HANDOFF.md |

---

### AREA 6 — EMERGENCY BATTERY RESERVE AND TERMINAL SOC STRUCTURE

**Governing Stakeholder Decisions**: D11, D12, D13, D15
**Area Status**: `CONCEPTUALLY_RESOLVED — ALL_NUMERICAL_VALUES_PENDING`

#### 6.1 Emergency Battery Reserve Policy Logic (HUMAN_SELECTED_POLICY)

From D11 (B+A):
- A **dynamic emergency battery reserve** exists that adapts to forecast risk.
- A **dedicated baseline reserve floor** exists, above the technical minimum SOC.
- These two layers are distinct from the technical SOC minimum (equipment protection).

The structural three-layer relationship is `HUMAN_SELECTED_POLICY`:
- Layer 1: Technical minimum SOC — equipment protection (hardware constraint)
- Layer 2: Emergency Battery Reserve (EBR) — operational emergency headroom
- Layer 3: Dynamic risk-adaptive reserve margin on top of the EBR

#### 6.2 Terminal SOC Policy Logic (HUMAN_SELECTED_POLICY)

From D12 (C+B):
- A **dynamic terminal SOC requirement** adapts to upcoming risk at horizon end.
- A **minimum terminal SOC floor** constrains the horizon-end SOC.

The structural relationship is `HUMAN_SELECTED_POLICY`.

#### 6.3 Numerical Values (NONE SELECTED — ALL PENDING)

> **THE FOLLOWING FIGURES ARE `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED`:**

- 35% EBR baseline (from advisory proposal)
- 45% EBR precautionary (from advisory proposal)
- 35% minimum terminal SOC (from advisory proposal)
- 55–65% precautionary terminal SOC target (from advisory proposal)

None of these percentages are selected by the stakeholder decisions. All originate
from the POLAR_STATION_RESEARCH_MANAGER advisory proposal and require engineering
validation before they can become governed parameters.

**EMERGENCY_RESERVE_STRUCTURE**: `HUMAN_SELECTED_POLICY`
**BASELINE_RESERVE_PERCENTAGE**: `NUMERICAL_CALIBRATION_REQUIRED`
**DYNAMIC_RESERVE_FORMULATION**: `NEXT_EMS_OBJECTIVE_SPECIFICATION`
**NUMERICAL_RESERVE**: `ENGINEERING_VALIDATION_REQUIRED`
**TERMINAL_SOC_STRUCTURE**: `HUMAN_SELECTED_POLICY`
**TERMINAL_SOC_NUMERICAL_VALUES**: `NUMERICAL_CALIBRATION_REQUIRED`
**DYNAMIC_TERMINAL_SOC_FORMULATION**: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

#### 6.4 Current Implementation Fact (PRESERVED)

**Technical minimum SOC = 20%** (40 kWh from 200 kWh): `CURRENT_IMPLEMENTATION_FACT`
(battery.yaml, frozen, SHA verified). This is hardware equipment protection — NOT the
emergency battery reserve. The distinction is `HUMAN_SELECTED_POLICY` per D11.

#### 6.5 Evidence Classification

| Evidence | Type |
|----------|------|
| Dynamic emergency reserve + baseline reserve floor structure | `HUMAN_SELECTED_POLICY` — D11 |
| EBR is above (distinct from) technical minimum SOC | `HUMAN_SELECTED_POLICY` — D11 |
| Dynamic terminal SOC + minimum terminal floor structure | `HUMAN_SELECTED_POLICY` — D12 |
| Technical minimum SOC = 20% (equipment protection) | `CURRENT_IMPLEMENTATION_FACT` — battery.yaml (frozen) |
| Terminal SOC unconstrained at horizon boundary in current milp.py | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen) |
| 35% EBR baseline value | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 45% EBR precautionary value | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 35% minimum terminal SOC | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 55–65% precautionary terminal SOC | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Battery vendor true technical minimum SOC (confirm/revise 20%) | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-07 |
| Battery degradation curves | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-08 |
| EBR and terminal SOC mathematical formulation | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |

---

### AREA 7 — RENEWABLE CURTAILMENT POLICY

**Governing Stakeholder Decisions**: D09, D10, D15
**Area Status**: `CONCEPTUALLY_RESOLVED — FORMULATION_PENDING`

#### 7.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D09 (B): Minimize avoidable renewable curtailment. **No arbitrary percentage
target.** This decision explicitly rejects a fixed % target.

From D10 (B): Necessary renewable curtailment — required for battery protection,
generator stability, or reserve margins — is **allowed without explicit objective
penalty**.

From D15 (A): Renewable utilization is Stage 4 in the strict lexicographic hierarchy,
always subordinate to Stages 1–3 (reliability, resilience, fuel).

These are `HUMAN_SELECTED_POLICY`.

#### 7.2 Curtailment Classification Direction

The policy direction is `CONCEPTUALLY_RESOLVED`:
- Necessary/unavoidable curtailment: unpenalized.
- Avoidable curtailment: subject to soft minimization preference (Stage 4 only).
- Exact mathematical distinction between necessary and avoidable: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

#### 7.3 Renewable Percentage KPI

> **A figure of 50–70% renewable utilization was introduced in v1.0.0.**
> **Status: `NOT_STAKEHOLDER_AUTHORIZED — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`**

D09 explicitly selects "no arbitrary % target." Introducing any percentage figure
contradicts the selected policy. The 50–70% figure originates from the advisory
proposal only and must not be carried into the EMS Objective Specification as a
policy target.

Renewable utilization KPI (metric definition): `CONCEPTUALLY_RESOLVED` as
(renewable kWh served to load) / (total kWh served to load), measured per operating
period. Whether a target value is set, and what it would be, remains
`FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED` if a target is ever desired.

Avoidable vs. necessary curtailment KPI tracking: `NEXT_EMS_OBJECTIVE_SPECIFICATION`

#### 7.4 Evidence Classification

| Evidence | Type |
|----------|------|
| Minimize avoidable curtailment (no arbitrary % target) | `HUMAN_SELECTED_POLICY` — D09 |
| Necessary curtailment allowed without objective penalty | `HUMAN_SELECTED_POLICY` — D10 |
| Renewable utilization is Stage 4 (lowest priority) | `HUMAN_SELECTED_POLICY` — D15 |
| 50–70% renewable utilization target | `NOT_STAKEHOLDER_AUTHORIZED — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| Curtailment KPI metric definition (kWh served ratio) | `CONCEPTUALLY_RESOLVED` |
| Avoidable vs. necessary curtailment mathematical distinction | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |
| P_pv_curtail unpenalized in current milp.py | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen) |
| Qualitative goal to maximize renewable integration | `DOCUMENTED_REQUIREMENT` — POLARIS_MASTER_HANDOFF.md |

---

### AREA 8 — FORECAST UNCERTAINTY METHOD AND MARGIN POLICY

**Governing Stakeholder Decisions**: D13, D11, D12
**Area Status**: `CONCEPTUALLY_RESOLVED — ALL_NUMERICAL_MARGINS_PENDING`

#### 8.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D13 (A+D): The **method** for handling forecast uncertainty is:
- Deterministic safety margins (conservative downward derate on generation,
  upward adjustment on demand)
- Combined with real-time rolling MPC feedback correction (receding-horizon re-optimization)

This method selection is `HUMAN_SELECTED_POLICY`. Full stochastic/scenario optimization
is NOT the selected approach.

#### 8.2 Numerical Margin Values (NONE SELECTED — ALL PENDING)

> **THE FOLLOWING FIGURES ARE `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED`:**
> (All originate from the advisory stakeholder proposal — NOT from stakeholder decisions.)

- Solar generation derate: −15–25%
- Wind generation derate: −20–30%
- Demand upward margin: +10%
- Re-optimization interval: 1–6 hours

These values require derivation from historical station forecast-error statistics
(SD-09, SD-10, SD-11) before they can become governed parameters. They are preserved
here as illustrative starting-point references only, clearly labeled.

**NOTE**: Solar credit during polar night = 0% is a physical fact (station latitude
68°N), not an arbitrary derate. Classification: `ENGINEERING_INFERENCE` from station.yaml.

#### 8.3 Evidence Classification

| Evidence | Type |
|----------|------|
| Method: deterministic safety margins + rolling MPC correction | `HUMAN_SELECTED_POLICY` — D13 |
| Full stochastic optimization NOT the selected method | `HUMAN_SELECTED_POLICY` — D13 |
| Solar generation derate margin: −15–25% | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Wind generation derate margin: −20–30% | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Demand upward safety margin: +10% | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Re-optimization interval: 1–6 hours | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Solar credit during polar night = 0% | `ENGINEERING_INFERENCE` — station.yaml (68°N latitude) |
| Historical forecast vs. actual error statistics | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-09, SD-10, SD-11 |
| Current milp.py: no forecast margins implemented (deterministic point forecast) | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen) |
| Qualitative uncertainty mitigation goal | `DOCUMENTED_REQUIREMENT` — POLARIS_MASTER_HANDOFF.md §58 |

---

### AREA 9 — LEXICOGRAPHIC OBJECTIVE PRIORITY STRUCTURE

**Governing Stakeholder Decisions**: D06, D14, D15
**Area Status**: `CONCEPTUALLY_RESOLVED — MATHEMATICAL_FORMULATION_PENDING`

#### 9.1 Priority Order (HUMAN_SELECTED_POLICY)

From D15 (A): Strict Lexicographic Hierarchy — exactly this order:
1. Critical reliability
2. Emergency resilience / reserve maintenance
3. Fuel conservation
4. Renewable utilization

From D06 (D+A): Stage 1 (Critical reliability) is enforced as a **hard constraint**
during normal/degraded operation. Lexicographic fallback applies during declared
emergency when the hard constraint cannot be satisfied.

From D14 (A+C): Fuel minimization is always subject to the reliability SLA; Critical
load is never sacrificed for fuel savings.

This priority structure is `HUMAN_SELECTED_POLICY`.

#### 9.2 Equipment Protection Note

The stakeholder advisory proposal notes that equipment protection (battery/generator
technical limits) should be treated as a concurrent hard constraint alongside Stage 1,
because damaging equipment undermines all subsequent objectives. This interpretation is
`CONCEPTUALLY_RESOLVED` as a design principle consistent with the selected decisions.
Its exact formulation in the MILP is `NEXT_EMS_OBJECTIVE_SPECIFICATION`.

#### 9.3 Current Implementation Rejection

The current frozen milp.py uses a **single composite scalar weighted objective**.
The 16,000:1 cost ratio ($10,000/$0.625) is a `CURRENT_IMPLEMENTATION_FACT` — NOT the
authorized priority structure. It is explicitly rejected by D15 and D14.

#### 9.4 Evidence Classification

| Evidence | Type |
|----------|------|
| Strict 4-stage lexicographic priority order | `HUMAN_SELECTED_POLICY` — D15 |
| Stage 1 = Critical reliability as hard constraint | `HUMAN_SELECTED_POLICY` — D06 |
| Emergency lexicographic fallback when Stage 1 infeasible | `HUMAN_SELECTED_POLICY` — D06 |
| Reliability strictly dominates fuel at all times in normal operation | `HUMAN_SELECTED_POLICY` — D14 |
| Equipment protection as concurrent hard constraint | `CONCEPTUALLY_RESOLVED` — advisory note consistent with D11, D06 |
| Single composite scalar objective in current milp.py | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen); rejected |
| 16,000:1 cost ratio | `CURRENT_IMPLEMENTATION_FACT` — milp.py (frozen); explicitly NOT policy |
| Multi-stage lexicographic MILP mathematical formulation | `NEXT_EMS_OBJECTIVE_SPECIFICATION` |

---

### AREA 10 — GOVERNANCE CHANGE-CONTROL AND APPROVAL AUTHORITY

**Governing Stakeholder Decisions**: D16
**Area Status**: `CONCEPTUALLY_RESOLVED — ORGANIZATIONAL_ASSIGNMENTS_PENDING`

#### 10.1 Policy Logic (HUMAN_SELECTED_POLICY)

From D16 (C): Multi-tier governance approval structure with:
- Technical validation tier
- Mission / operations validation tier
- Final policy approval tier
- No single role may unilaterally change EMS policy

These structural requirements are `HUMAN_SELECTED_POLICY`.

#### 10.2 Functional Role Structure (CONCEPTUALLY_RESOLVED)

The following **functional roles** are `CONCEPTUALLY_RESOLVED` as consistent with D16:
- Proposer (initiates policy change)
- Cross-functional Reviewer (safety, mission, technical perspectives)
- Technical Validator (engineering feasibility)
- Final Approver (senior governance authority)
- Emergency Temporary Change Authority (on-duty senior operator)
- Records Function (archiving and audit trail)

Named organizational individuals: `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-13
Formal organizational governance charter: `FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED`

**Note on 72-hour emergency reporting window**: This figure originates from the
advisory proposal. Status: `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED`.
Actual reporting window: `FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED`.

#### 10.3 Change-Control Protocol

Formal change-control protocol document: `NEXT_EMS_OBJECTIVE_SPECIFICATION` (NS-11)

#### 10.4 Evidence Classification

| Evidence | Type |
|----------|------|
| Multi-tier governance approval structure | `HUMAN_SELECTED_POLICY` — D16 |
| No single role unilateral authority | `HUMAN_SELECTED_POLICY` — D16 |
| Three-tier structure (Technical / Mission-Ops / Final Approval) | `HUMAN_SELECTED_POLICY` — D16 |
| Functional role definitions (Proposer, Reviewer, etc.) | `CONCEPTUALLY_RESOLVED` |
| 72-hour emergency deviation reporting window | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Named organizational individuals | `STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-13 |
| Formal governance charter | `FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED` |
| Current EMS: ad-hoc engineering development choices, no formal change control | `CURRENT_IMPLEMENTATION_FACT` — milp.py, optimizer.yaml (frozen) |

---

## CROSS-AREA POLICY TENSION REGISTER (CORRECTED)

| ID | Tension | Areas | Status | Resolution |
|----|---------|-------|--------|-----------|
| T-01 | Emergency mode boundary between normal/degraded and emergency must be precisely defined to prevent premature or missed declarations | 1, 3 | `NEXT_EMS_OBJECTIVE_SPECIFICATION` | Explicit trigger conditions must be defined in Specification; not resolvable here |
| T-02 | EBR structure and terminal SOC structure must be physically achievable across consecutive low-renewable days — depends on battery capacity and load | 6, 8 | `STATION_DATA_REQUIRED` | SD-07, SD-08 validation required before any numerical values are governed |
| T-03 | D09 selects "no arbitrary % target" — any renewable % figure conflicts with this selection | 7 | `RESOLVED_BY_STAKEHOLDER_DECISION` | 50–70% figure is NOT stakeholder authorized (D09 is itself the rejection of a fixed target) |
| T-04 | Fuel budget must never force Critical load shedding — the stakeholder decisions resolve this unambiguously | 4, 5 | `RESOLVED_BY_DESIGN` — D08, D14 | D08 explicitly states soft-managed budget; D14 states reliability has absolute priority |
| T-05 | Forecast safety margins must be calibrated to avoid systematic over-conservatism | 8 | `STATION_DATA_REQUIRED` | SD-09 through SD-11 required before margins become governed parameters |
| T-06 | Equipment protection constraints must be explicitly formulated alongside Stage 1 in the lexicographic MILP | 9 | `NEXT_EMS_OBJECTIVE_SPECIFICATION` | NS-05 solver formulation must encode this explicitly |

---

## COMPLETE PENDING REQUIREMENTS REGISTER

### Category A — STATION_DATA_REQUIRED (SD)

| ID | Parameter |
|----|-----------|
| SD-01 | Station circuit-level load inventory (actual watts per circuit per tier) |
| SD-02 | ATS switching gap measurement (hardware measurement) |
| SD-03 | Local UPS hold-up time per Critical circuit |
| SD-04 | Generator fuel consumption bench-test curves (L/kWh vs. load and temperature) |
| SD-05 | Station fuel tank storage volume, resupply schedule, and resupply interval |
| SD-06 | Critical+Essential average demand (winter/polar-night, kWh/day) |
| SD-07 | Battery vendor true technical minimum SOC (confirm or revise 20% prototype value) |
| SD-08 | Battery degradation curves vs. depth of discharge |
| SD-09 | Historical solar forecast vs. actual error statistics |
| SD-10 | Historical wind forecast vs. actual error statistics |
| SD-11 | Historical demand forecast vs. actual error statistics |
| SD-12 | Emergency-mode transition numerical triggers (derived from SD-05 through SD-08) |
| SD-13 | Named organizational individuals for governance roles |

### Category B — NEXT_EMS_OBJECTIVE_SPECIFICATION (NS)

| ID | Item |
|----|------|
| NS-01 | Hard constraint MILP formulation for Stage 1 (zero unmet Critical load) |
| NS-02 | Stage 2 reserve/resilience MILP sub-objective formulation |
| NS-03 | Liters-based Stage 3 fuel objective formulation (replacing cost proxy) |
| NS-04 | Stage 4 avoidable curtailment preference formulation |
| NS-05 | Multi-stage lexicographic MILP solver implementation and dominance validation |
| NS-06 | Operating mode transition logic and EMS mode-switching protocol |
| NS-07 | Necessary vs. avoidable curtailment distinction implementation |
| NS-08 | Fuel budget KPI tracking and governance alert protocol |
| NS-09 | Emergency fuel reserve calculation, access authorization, and reporting workflow |
| NS-10 | Rolling re-optimization interval (computational feasibility assessment) |
| NS-11 | Formal change-control protocol document |

### Category C — NUMERICAL_CALIBRATION_REQUIRED (NC)

| ID | Parameter | Current Advisory Figure | Source |
|----|-----------|------------------------|--------|
| NC-01 | Emergency Battery Reserve % (baseline) | 35% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-02 | Emergency Battery Reserve % (precautionary) | 45% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-03 | Minimum terminal SOC % | 35% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-04 | Precautionary terminal SOC target % | 55–65% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-05 | Solar forecast derate % | 15–25% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-06 | Wind forecast derate % | 20–30% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-07 | Demand forecast upward margin % | +10% (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-08 | Re-optimization interval (hours) | 1–6h (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-09 | Emergency fuel reserve sizing | 30 days coverage (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-10 | Fuel budget period | Monthly (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-11 | Emergency governance reporting window | 72 hours (`NOT_STAKEHOLDER_AUTHORIZED`) | Advisory proposal |
| NC-12 | Load restoration dwell time | 5 minutes (`NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`) | Advisory proposal |
| NC-13 | Critical unmet load event review trigger | 15 minutes (`NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`) | Advisory proposal |
| NC-14 | Critical unmet load cumulative review trigger | 2 kWh/30 days (`NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`) | Advisory proposal |

---

## AREA-BY-AREA CORRECTED STATUS SUMMARY

| Area | Policy Logic | Numerical Values | Station Mapping | Specification |
|------|-------------|-----------------|-----------------|---------------|
| 1 — Emergency Modes | `CONCEPTUALLY_RESOLVED` | `STATION_DATA_REQUIRED` | N/A | `NEXT_SPEC_REQUIRED` |
| 2 — Load Shedding | `CONCEPTUALLY_RESOLVED` | `NEXT_SPEC_REQUIRED` | `STATION_DATA_REQUIRED` | `NEXT_SPEC_REQUIRED` |
| 3 — Critical Reliability | `HUMAN_SELECTED_POLICY` | `ENGINEERING_VALIDATION` | `STATION_DATA_REQUIRED` | `NEXT_SPEC_REQUIRED` |
| 4 — Fuel Metric | `HUMAN_SELECTED_POLICY` | `STATION_DATA_REQUIRED` | N/A | `NEXT_SPEC_REQUIRED` |
| 5 — Fuel Budget | `HUMAN_SELECTED_POLICY` | `STATION_DATA_REQUIRED` | N/A | `NEXT_SPEC_REQUIRED` |
| 6 — Battery Reserve | `HUMAN_SELECTED_POLICY` | `NUMERICAL_CALIBRATION_REQUIRED` | N/A | `NEXT_SPEC_REQUIRED` |
| 7 — Curtailment | `HUMAN_SELECTED_POLICY` | N/A (no % target authorized) | N/A | `NEXT_SPEC_REQUIRED` |
| 8 — Forecast Margins | `HUMAN_SELECTED_POLICY` (method) | `NUMERICAL_CALIBRATION_REQUIRED` | N/A | `NEXT_SPEC_REQUIRED` |
| 9 — Lexicographic Priority | `HUMAN_SELECTED_POLICY` | N/A (ordering, not numbers) | N/A | `NEXT_SPEC_REQUIRED` |
| 10 — Governance | `HUMAN_SELECTED_POLICY` | N/A | `STATION_DATA_REQUIRED` | `NEXT_SPEC_REQUIRED` |

**Overall: 10/10 areas have policy logic resolved. 0/10 areas have finalized numerical parameters.**

---

## FINAL GOVERNANCE STATUS

```yaml
PACKAGE_LABEL:                            POLARIS_EMS_POLICY_DEFINITION_RESOLUTION
PACKAGE_VERSION:                          1.1.0
POLICY_DEFINITION_RESOLUTION:             CONDITIONAL
AREAS_POLICY_LOGIC_REVIEWED:              10 of 10
AREAS_NUMERICALLY_COMPLETE:               0 of 10

D1_D16_CHANGED:                           NO
POLICY_CHOICES_REOPENED:                  NO
UNAUTHORIZED_NUMERICAL_POLICY_VALUES:     0
STATION_SPECIFIC_ASSUMPTIONS_INVENTED:    0

CURRENT_EMS_IMPLEMENTATION:               FROZEN
CURRENT_EMS_OBJECTIVE:                    FROZEN
milp.py_SHA256:                           ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35
battery.yaml_SHA256:                      eb06f81d8b11364e254cbcd5c37a4769874f8703e9e86e3b067b60d8858da216
diesel.yaml_SHA256:                       421120967328e18366daf41b682fc9f1cbe91b0f9ebe2133b83290bb9e294ac3
loads.yaml_SHA256:                        ab6943d72f2054b001274de5a3fe229c9987eb31fb11be0422f33754fd5f3cad
optimizer.yaml_SHA256:                    bdf5a61487fddf0695b8926a24499be17fef0181d3f755731d154c1fabbca1e8
solar_pv.yaml_SHA256:                     611521090b7d551614c23d91fc190320a42bccee667929618d40bab987262e5e
station.yaml_SHA256:                      e021368133587b5752b9471722d7997d1cd2aa2d674697a47b1b2f5b06052e42

EMS_MODIFICATION:                         NOT_AUTHORIZED
OBJECTIVE_MODIFICATION:                   NOT_AUTHORIZED
EMS_EXECUTION:                            NOT_AUTHORIZED
MPC_EXECUTION:                            NOT_AUTHORIZED
MODEL_TRAINING:                           NOT_AUTHORIZED
MILP_EXECUTION:                           NOT_AUTHORIZED
SIMULATION_EXECUTION:                     NOT_AUTHORIZED
NEW_EXPERIMENT:                           NOT_AUTHORIZED
POLICY_RECOMMENDATION:                    NONE
POLICY_RANKING:                           NONE
FORMAL_STAKEHOLDER_AUTHORIZATION:         PENDING

NEXT_GOVERNED_STEP:                       HUMAN_POLICY_PACKAGE_REVIEW
FOLLOWING_STEP:                           GOVERNED_EMS_OBJECTIVE_SPECIFICATION
```

---

*This document is a POLICY_DEFINITION governance document only.*
*No EMS code, model, optimizer, or configuration was modified.*
*All system SHA-256 hashes are verified unchanged.*
*Version 1.1.0 corrects classification errors in v1.0.0.*
*See `POLARIS_EMS_POLICY_DEFINITION_CORRECTION_MANIFEST.md` for full correction detail.*
