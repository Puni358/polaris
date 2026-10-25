# POLARIS — EMS IMPLEMENTATION SPECIFICATION
## GOVERNED IMPLEMENTATION-MECHANICS SPECIFICATION — PHASE 1 (SURGICALLY CORRECTED)

**STATUS**: `IMPLEMENTATION_SPECIFICATION_PACKAGE = CORRECTED_PENDING_REVIEW`  
**AUTHORIZATION**: `IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED`  
**NEXT GOVERNED STEP**: `NEXT_GOVERNED_STEP = FRESH_IMPLEMENTATION_SPECIFICATION_REVIEW`  

---

### 1. ABSOLUTE GOVERNANCE BOUNDARY

This document establishes the governed **Implementation Specification** (Layer C) for the POLARIS Energy Management System (EMS). It translates the approved stakeholder policy (Layer A) and governed mathematical specification (Layer B) into explicit, testable implementation mechanics and contracts.

**STRICT BOUNDARY DIRECTIVES**:
- **NO CODE MODIFICATION**: Prototype optimizer code (`system/optimization/implementations/milp.py`), `LocalMILPEnergyOptimizer`, `DispatchPlan`, `ForecastBundle`, `DigitalTwinSimulator`, Branch01, and Stage8.1 remain frozen.
- **NO CONFIGURATION MODIFICATION**: `battery.yaml`, `diesel.yaml`, `loads.yaml`, `optimizer.yaml`, `solar_pv.yaml`, and `station.yaml` remain frozen.
- **NO EXECUTION**: Zero execution of MILP, MPC, EMS, Digital Twin, or model training/inference is authorized by this specification.
- **NO UNAUTHORIZED SELECTION**: Provisional engineering numbers and unresolved governance decisions are explicitly marked as requiring station data, calibration, or policy approval.

---

### 2. GOVERNANCE LAYER SEPARATION & CLASSIFICATION TAXONOMY

To prevent silent promotion of engineering assumptions into policy, every system element is classified across 5 strict governance layers:

- **LAYER A**: Stakeholder Policy (Authoritative: D1–D16 decisions)
- **LAYER B**: Governed Mathematical Objective (Authoritative: Objective Specification v2.5.0)
- **LAYER C**: Implementation Mechanics (Authoritative: THIS DOCUMENT)
- **LAYER D**: Code & Configuration Implementation (FROZEN / NOT AUTHORIZED)
- **LAYER E**: Execution & Validation (FROZEN / NOT AUTHORIZED)

Every requirement is explicitly assigned one of the following governed status classifications:
1. `POLICY_RESOLVED`: Approved stakeholder policy decision.
2. `MATH_RESOLVED`: Formulated mathematical objective or constraint.
3. `IMPLEMENTATION_SPECIFIED`: Fully specified Layer C mechanism ready for coding (unambiguous contract with zero unresolved alternatives).
4. `IMPLEMENTATION_DEFERRED`: Explicitly deferred pending governance resolution / alternative selection.
5. `STATION_DATA_REQUIRED`: Requires empirical physical data from target station.
6. `NUMERICAL_CALIBRATION_REQUIRED`: Requires empirical tuning data.
7. `GOVERNANCE_CLARIFICATION_REQUIRED`: Requires formal stakeholder board decision.

---

### 3. AUTHORITATIVE INPUTS & TRACEABILITY

This specification is directly derived from and fully traceable to the following frozen inputs:
1. `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md` (SHA-256: `562834c2...`)
2. `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` (SHA-256: `4a34d11f...`)
3. `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0 (SHA-256: `36ec4676...`)
4. `POLARIS_EMS_OBJECTIVE_HIERARCHY.md` (SHA-256: `0d43429d...`)
5. `POLARIS_EMS_OBJECTIVE_SPECIFICATION_REVIEW.md` (SHA-256: `cf074914...`)
6. Frozen system configurations (`battery.yaml`, `diesel.yaml`, `loads.yaml`, etc.)
7. Frozen prototype code (`milp.py`)

---

### 4. IMPLEMENTATION GAP REGISTER SUMMARY (RECONCILED)

All 22 implementation gaps identified in the Objective Specification Review are registered in `POLARIS_EMS_IMPLEMENTATION_GAP_REGISTER.csv`:
- **Specified Implementation Mechanics**: 3 items (`GAP_05`, `GAP_11`, `GAP_20`)
- **Deferred Implementation Mechanics**: 8 items (`GAP_01`, `GAP_02`, `GAP_03`, `GAP_04`, `GAP_10`, `GAP_12`, `GAP_15`, `GAP_19`)
- **Station Data Required**: 5 items (`GAP_06`, `GAP_07`, `GAP_13`, `GAP_18`, `GAP_22`)
- **Numerical Calibration Required**: 2 items (`GAP_16`, `GAP_17`)
- **Governance Clarification Required**: 4 items (`GAP_08`, `GAP_09`, `GAP_14`, `GAP_21`)

---

### 5. D1 — FIVE LOAD TIERS IMPLEMENTATION CONTRACTS

The 5 stakeholder-approved load classes must remain structurally distinct across all Layer C data structures and solver variables:

1. **Critical Load ($L_C$)**: Continuous service target (100% SLA, 0 kWh unmet in normal operation). Contract requires feeder mapping, sub-hourly ATS transfer latency data, and UPS hold-up specs (`STATION_DATA_REQUIRED`).
2. **Essential Load ($L_E$)**: High-priority service target. Allowed load shedding only during severe deficits when Noncritical, Interruptible, and Deferrable loads have been fully shed.
3. **Deferrable Load ($L_D$)**: Shiftable task-based load. Contract specifies task duration $D_d$, earliest start $t_{\text{start}}$, latest finish $t_{\text{end}}$, energy requirement $E_d$, and deadline completion constraint $\sum_{t=t_{\text{start}}}^{t_{\text{end}}} P_{\text{served},D}(t) \ge E_d$. Task preemption & interruption semantics are explicitly deferred (`GAP_03 = IMPLEMENTATION_DEFERRED`).
4. **Interruptible Load ($L_I$)**: Immediately shed-able load with continuous downtime limits (`GAP_04 = IMPLEMENTATION_DEFERRED`). Contract specifies anti-chattering dwell time (`GAP_05 = IMPLEMENTATION_SPECIFIED`).
5. **Noncritical Load ($L_N$)**: Discretionary load shed first during energy deficits. Contract specifies automated shedding controls and manual operator override interface.

---

### 6. D2 — AUTOMATED LOAD SHEDDING & DEFERRABLE MECHANICS

- **Automated Shedding Policy**: `AUTOMATED_TIER_BASED_LOAD_SHEDDING = POLICY_RESOLVED`.
- **Executable Priority Sequence**: `D2_SHEDDING_PRIORITY_ORDER = IMPLEMENTATION_DEFERRED`. Exact shedding priority ($N \rightarrow I \rightarrow D \rightarrow E$) remains deferred pending stakeholder board authorization.
- **Restoration Mechanics**: `D2_RESTORATION_ORDER = IMPLEMENTATION_DEFERRED`. Restoration uses hysteresis timers per feeder to prevent busbar voltage collapse and inrush transients.
- **Deferrable Load Terminology Distinction**:
  - **SHEDDING**: Permanent unserved energy drop.
  - **INTERRUPTION**: Temporary pause during active task execution.
  - **DEFERRAL**: Delaying task start time prior to execution.
  - **RESCHEDULING**: Re-allocating task execution windows within allowed bounds.
  - **PREEMPTION**: Pausing active task to resume later.

---

### 7. STAGE 1 — CRITICAL LOAD RELIABILITY & INFEASIBILITY BOUNDARY

- **Normal Feasible Target**: Stage 1 enforces $Z_1^* = \min \sum P_{\text{unmet},C}(t) = 0$ kWh as an absolute priority hard constraint.
- **Infeasibility Boundary**: If physical generation and battery capacity are insufficient to meet Critical load ($Z_1^* > 0$), the implementation contract specifies:
  ```
  Z1* > 0  -->  Z1_INFEASIBLE  -->  GOVERNED_INFEASIBILITY_STATE
  ```
  The system MUST raise a governed infeasibility alarm and trigger emergency backup protocols. The solver MUST NOT silently sacrifice Critical load to conserve fuel.

---

### 8. EMERGENCY MODE IMPLEMENTATION CONTRACT & STATE MACHINE

- **State Representation**: Finite State Machine with 4 operating regimes (`CONCEPTUAL_IMPLEMENTATION_STRUCTURE`):
  - `NORMAL`: All load tiers served; energy balance nominal.
  - `WARNING`: BESS SOC below EBR floor or renewable deficit detected.
  - `EMERGENCY`: Critical energy deficit imminent; emergency load shedding active.
  - `RECOVERY`: Generation surplus verified; controlled load restoration active.
- **Governance Interface**: `EMERGENCY_MODE_TRIGGER_VALUES = GOVERNANCE_CLARIFICATION_REQUIRED`. Entry/exit trigger thresholds require formal policy sign-off.

---

### 9. STAGE 2 — EMERGENCY BATTERY RESILIENCE TARGET SHORTFALL MECHANICS

- **Objective Semantics**: Formulated strictly as **Target-Shortfall Minimization**:
  \[
  Z_2^* = \min \sum_{t=1}^{H} \max(0, \text{SOC}_{\text{EBR\_target}}(t) - \text{SOC}(t)) + \max(0, \text{terminal\_target} - \text{SOC}(H))
  \]
- **Target Generation Function**: `STAGE2_TARGET_GENERATION = IMPLEMENTATION_DEFERRED`. Dynamic target generation function $\text{SOC}_{\text{target}}(t)$ remains unresolved (`GAP_10`). Baseline 35% reserve floor is classified as `PROVISIONAL_ENGINEERING_VALUE`.
- **Target Bounding & Clipping**: If dynamic target $\text{SOC}_{\text{target}}(t) > \text{SOC}_{\text{max}}$, it is clipped to $\text{SOC}_{\text{max}}$. Non-negative slack variables $s_{\text{ebr}}(t) \ge 0$ absorb physical shortfall without causing MILP solver infeasibility (`GAP_11 = IMPLEMENTATION_SPECIFIED`).

---

### 10. TERMINAL SOC IMPLEMENTATION & ROLLING-HORIZON BOUNDARY

- **Policy Status**: `D12_POLICY = RESOLVED`.
- **Rolling-Horizon Boundary**: Terminal SOC target $\text{SOC}(H) \ge \text{SOC}_{\text{terminal}}$ is enforced at hour $H=24$ of each MPC solve window to prevent end-of-horizon battery depletion.
- **Stage Placement**: Placement between Stage 2 shortfall and Stage 3 fuel conservation remains unresolved (`GAP_12 = IMPLEMENTATION_DEFERRED`). Numerical values (55%, 65%) are classified as `PROVISIONAL_ENGINEERING_VALUE`.

---

### 11. D8 — FUEL PHYSICAL INVENTORY VS RESUPPLY BUDGET ACCOUNTING

- **Physical Fuel Inventory Balance**: Enforced as Stage 0 physical hard constraint:
  \[
  F_{\text{rem}}(t+1) = F_{\text{rem}}(t) - \text{Fuel}(t), \quad F_{\text{rem}}(t) \ge 0
  \]
- **Seasonal Resupply Budget**: `D8_SEASONAL_FUEL_ACCOUNTING = STATION_DATA_REQUIRED`. Candidate resupply budget inequality $\sum \text{Fuel}(t) \le F_{\text{budget}}$ is represented as a daily consumption target in Stage 3, and MUST NOT override Stage 1 Critical reliability (`GAP_13`).

---

### 12. D14/D15 — LEXICOGRAPHIC OPTIMIZATION SOLVER PIPELINE ARCHITECTURE

- **Sequential 4-Pass MILP Pipeline Concept**:
  - **Pass 1 (Stage 1)**: Solve $\min Z_1$ (Critical Unmet Load) $\rightarrow$ Record $Z_1^*$ $\rightarrow$ Add constraint $Z_1 \le Z_1^* + \epsilon_1$.
  - **Pass 2 (Stage 2)**: Solve $\min Z_2$ (EBR Shortfall) $\rightarrow$ Record $Z_2^*$ $\rightarrow$ Add constraint $Z_2 \le Z_2^* + \\epsilon_2$.
  - **Pass 3 (Stage 3)**: Solve $\min Z_3$ (Fuel Consumption) $\rightarrow$ Record $Z_3^*$ $\rightarrow$ Add constraint $Z_3 \le Z_3^* + \epsilon_3$.
  - **Pass 4 (Stage 4)**: Solve $\min Z_4$ (Renewable Curtailment) $\rightarrow$ Final Dispatch Plan.
- **Architecture Status**: `GAP_19 = IMPLEMENTATION_DEFERRED`. Solver architecture alternatives (sequential 4-pass vs solver-native lexicographic vs epsilon-constraint) remain unresolved. Scalar weighted-sum substitution is strictly PROHIBITED.

---

### 13. D9/D10 — RENEWABLE ABSORPTION & CURTAILMENT CLASSIFICATION DIAGNOSTIC

- **Renewable Absorption (D9)**: Maximize solar PV and wind absorption in Stage 4 objective $\min Z_4 = \sum P_{\text{curt}}(t)$.
- **Diagnostic Curtailment Classification (D10)**: `GAP_15 = IMPLEMENTATION_DEFERRED`. The diagnostic formula:
  \[
  P_{\text{curt,necessary}}(t) = \max\left(0, P_{\text{pv}}(t) - P_{\text{load,total}}(t) - P_{\text{bess,charge,max}}(t)\right)
  \]
  is classified as `PROVISIONAL_DIAGNOSTIC_ONLY`. Executable runtime classification algorithm remains deferred pending complete physical accounting boundary definition.

---

### 14. D13 — FORECAST UNCERTAINTY PIPELINE & DERATING APPLICATION

- **Data Pipeline Contract**: Derating margins apply to solar, wind, and demand forecasts in `ForecastBundle`:
  - $P_{\text{pv,safe}}(t) = (1 - \gamma_{\\text{pv}}) P_{\text{pv,fcst}}(t)$
  - $P_{\text{wind,safe}}(t) = (1 - \gamma_{\text{wind}}) P_{\text{wind,fcst}}(t)$
  - $P_{\text{demand,safe}}(t) = (1 + \gamma_{\text{demand}}) P_{\text{demand,fcst}}(t)$
- **Calibration Status**: `GAP_16 = NUMERICAL_CALIBRATION_REQUIRED`. Numerical derating factors ($\gamma_{\text{pv}}, \gamma_{\text{wind}}, \gamma_{\text{demand}}$) are classified as provisional engineering values requiring empirical station calibration.

---

### 15. BATTERY COMPONENT IMPLEMENTATION CONTRACT

- **State Variables**: $\text{SOC}(t)$, $P_{\text{charge}}(t)$, $P_{\text{discharge}}(t)$.
- **Physical Constraints**: $20\% \le \text{SOC}(t) \le 100\%$, $0 \le P_{\text{charge}}(t) \le P_{\text{ch,max}}$, $0 \le P_{\text{discharge}}(t) \le P_{\text{dis,max}}$.
- **Binary Interlocking**: $u_{\text{ch}}(t) + u_{\text{dis}}(t) \le 1$ prevents simultaneous charging and discharging. Technical floor 20% SOC is recognized as a hardware safety limit.

---

### 16. DIESEL GENERATOR IMPLEMENTATION CONTRACT

- **State Variables**: $u_{\text{gen}}(t) \in \{0,1\}$, $P_{\text{gen}}(t) \ge 0$.
- **Physical Constraints**: $P_{\text{gen,min}} \cdot u_{\text{gen}}(t) \le P_{\text{gen}}(t) \le P_{\text{gen,max}} \cdot u_{\text{gen}}(t)$.
- **Fuel Model**: $\text{Fuel}(t) = a_0 \cdot u_{\text{gen}}(t) + a_1 \cdot P_{\text{gen}}(t)$. Coefficients $a_0, a_1$ are marked as `STATION_DATA_REQUIRED` (`GAP_18`).

---

### 17. STATION LOAD IMPLEMENTATION CONTRACT (5 TIERS)

- **5 Tier Variables**: $P_{\text{served},i}(t), P_{\text{shed},i}(t), P_{\text{unmet},i}(t)$ for $i \in \{C, E, D, I, N\}$.
- **Feeder Assignment**: Configured via station load feeder mapping matrix (`GAP_07 = STATION_DATA_REQUIRED`).

---

### 18. RECEDING-HORIZON MPC LOOP & STATE CARRYOVER CONTRACT

- **Receding-Horizon MPC Workflow**:
  ```
  OBSERVE STATE (t_0) --> FETCH FORECAST (24h) --> DERATE MARGINS
    --> EXECUTE 4-PASS LEXICOGRAPHIC MILP --> EXTRACT CONTROL (t_0)
    --> DISPATCH TO HARDWARE --> ADVANCE TIME (t_0 + 1h)
  ```
- **Causality Constraint**: Optimization at step $t_0$ has zero access to actual weather or load realizations beyond $t_0$.

---

### 19. FAIL-CLOSED REQUIREMENTS & FALLBACK DISPATCH POLICY

- **Fail-Closed Input Validation**: Stale telemetry, missing forecast, or corrupt `ForecastBundle` triggers safe input rejection and exception logging (`IMPLEMENTATION_SPECIFIED`).
- **Fallback Dispatch Policy**: Operational fallback rules ("Generator started at min load, BESS held in reserve, Noncritical shed") are reclassified as `GAP_21 = GOVERNANCE_CLARIFICATION_REQUIRED` / `ENGINEERING_VALIDATION_REQUIRED`.

---

### 20. FORECASTBUNDLE & DISPATCHPLAN INTERFACE CONTRACTS

- **Interface Freeze**: Frozen Python data structures `ForecastBundle` and `DispatchPlan` remain unchanged.
- **Input Validation Contract**: Implementation pipeline validates timestamps, array lengths, non-negativity, and schema completeness before passing data to solver.

---

### 21. IMPLEMENTATION TEST PLAN (25 TEST CONTRACTS)

All 25 implementation test contracts registered in `POLARIS_EMS_IMPLEMENTATION_TEST_PLAN.csv`:
- `TEST_IMP_01` to `TEST_IMP_25` specified as pre-code-authorization test contracts. `IMPLEMENTATION_TEST_EXECUTION = NOT_AUTHORIZED`. Zero tests executed.

---

### 22. REQUIRED IMPLEMENTATION REGISTERS SUMMARY

- `POLARIS_EMS_IMPLEMENTATION_GAP_REGISTER.csv`: 22 items tracked (3 specified, 8 deferred, 5 station data, 2 numerical calibration, 4 governance clarification).
- `POLARIS_EMS_IMPLEMENTATION_INPUT_REGISTER.csv`: 15 missing engineering inputs tracked.
- `POLARIS_EMS_IMPLEMENTATION_DECISION_REGISTER.csv`: 7 key implementation questions tracked.
- `POLARIS_EMS_IMPLEMENTATION_NUMERICAL_REGISTER.csv`: 15 numerical values tracked.

---

### 23. HASH & PROVENANCE MANIFEST AUDIT

- All 16 authoritative input artifact byte digests verified and logged in `POLARIS_EMS_IMPLEMENTATION_PROVENANCE.csv`.
- Implementation Hash Manifest `POLARIS_EMS_IMPLEMENTATION_HASH_AUDIT.csv` updated with actual byte hashes for all 11 output files and 16 input files (27 total rows).
- External sidecar `POLARIS_EMS_IMPLEMENTATION_HASH_AUDIT.sha256` references the actual CSV byte hash (`cc88775a...`).

---

### 24. FINAL GOVERNANCE STATUS

```
IMPLEMENTATION_SPECIFICATION_PACKAGE = CORRECTED_PENDING_REVIEW
STAKEHOLDER_POLICY_APPROVAL = APPROVED
OBJECTIVE_SPECIFICATION_REVIEW = REVIEW_PASSED
IMPLEMENTATION_SPECIFICATION_REVIEW = PENDING_REVIEW
IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
NEXT_GOVERNED_STEP = FRESH_IMPLEMENTATION_SPECIFICATION_REVIEW
```

**STOP.**
