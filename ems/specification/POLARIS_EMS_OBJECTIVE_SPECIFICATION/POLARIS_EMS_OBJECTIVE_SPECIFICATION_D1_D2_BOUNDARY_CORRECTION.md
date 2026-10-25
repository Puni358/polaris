# POLARIS EMS — D1/D2 POLICY-TO-MATHEMATICS BOUNDARY CORRECTION

**Document Version**: 1.0.0  
**Correction Date**: 2026-09-22  
**Correction Type**: Governance Policy-to-Math Boundary Correction  
**Governance Status**: `D1_D2_BOUNDARY_CORRECTION = COMPLETE`  
**Next Governed Gate**: `EMS_OBJECTIVE_SPECIFICATION_REVIEW`  

---

## 1. CORRECTION MISSION

This document records a narrow, read-only governance correction to `POLARIS_EMS_OBJECTIVE_SPECIFICATION/` targeting the **policy-to-mathematics boundary leakage** at the intersection of Decision D1 (five load-tier classification) and Decision D2 (automated tier-based load shedding).

**D1 is NOT reopened. D2 is NOT reopened.**  
The approved stakeholder policy decisions remain unchanged.

The correction resolves a single class of leakage: where the *existence* of five named policy tiers was being incorrectly interpreted as *authorizing an exact executable shedding order*.

---

## 2. GOVERNANCE PRINCIPLE

```
POLICY CLASSIFICATION        (D1: five load tiers)
    ≠
OPERATIONAL SHEDDING ORDER   (D2: automated shedding — order unresolved)
    ≠
LOAD SCHEDULING MATHEMATICS  (implementation-deferred)
    ≠
RESTORATION LOGIC            (implementation-deferred)
    ≠
HARDWARE CONTROL LOGIC       (implementation-deferred)
```

D1 establishes the **policy classification**.  
D2 establishes **automated tier-based load shedding as a policy concept**.  
The future EMS Implementation Specification must define the **executable mechanics**.

The D1 five-tier classification does **not**, by itself, fully determine:
- The executable shedding priority order
- The restoration order
- Scheduling constraints (earliest-start, latest-finish, duration, etc.)
- Interruption duration limits
- Task deadlines or restart behavior

---

## 3. LEAKAGE IDENTIFIED

### 3.1 Primary Leakage — D2 Exact Shedding Sequence

**Previous wording (UNAUTHORIZED)**:
> "Shedding Sequence: Noncritical loads (L_N) are shed first, followed by Interruptible (L_I), Deferrable (L_D), and Essential (L_E). Critical loads (L_C) are strictly protected."
> "Restoration Semantics & Timing: Restoration occurs in reverse priority order (L_E restored before L_D, L_I, L_N) once generation/storage margins recover."

**Problem**: This converts a D1 five-tier policy classification directly into a fully specified executable shedding order (N→I→D→E) and a fixed reverse restoration sequence. This inference is NOT authorized by D1 or D2 at the Objective Specification layer.

**Correction Applied**:
- Removed the exact shedding sequence N→I→D→E
- Removed the exact reverse restoration order E→D→I→N
- Added `EXACT_SHEDDING_ORDER = REQUIRES_IMPLEMENTATION_SPECIFICATION`
- Added `EXACT_RESTORATION_ORDER = REQUIRES_IMPLEMENTATION_SPECIFICATION`
- D2 now correctly states the policy *concept* (automated tier-based shedding with Critical protection) without authorizing the *executable sequence*

### 3.2 Secondary Leakage — D1 Variable Descriptions

**Previous wording (PROBLEMATIC)**:
- `P_demand_D(t): Deferrable load task demand with scheduling bounds` — implied scheduling bounds already defined
- `P_shed_D(t): Shed/Deferred load power` — implied deferral semantics already defined
- `P_served_E(t)/P_shed_E(t)` — marked `FULLY_SPECIFIED` when tier semantics unresolved

**Correction Applied**:
- `P_demand_D` description: removed "with scheduling bounds"
- `P_shed_D` description: clarified as accounting variable; explicitly states it does NOT specify whether load is delayed/interrupted/rescheduled/deadline-constrained
- `P_served_E`, `P_unmet_E`, `P_shed_E`: governance status changed from `FULLY_SPECIFIED` to `POLICY_RESOLVED`
- `P_served_I`, `P_unmet_I`, `P_shed_I`, `P_served_N`, `P_unmet_N`, `P_shed_N`: governance status changed from `FULLY_SPECIFIED` to `POLICY_RESOLVED`

### 3.3 Tertiary Leakage — Implied Shedding Priority from Tier Names

**Previous wording**:
- `L_N: Noncritical loads (amenity heating/lighting, **shed first during deficit**)` — implied fixed shedding priority

**Correction Applied**:
- Removed "shed first during deficit" from L_N description
- Added explicit governance clarification note to D1 section: "The five-tier D1 classification establishes distinct policy classes but does NOT, by itself, fully determine the executable shedding priority, restoration order, scheduling constraints, interruption duration, task deadlines, or restart behavior of each class."

### 3.4 Load Balance Equation Semantics

**Previous wording (INCOMPLETE)**:
> "P_served,i(t) + P_unmet,i(t) + P_shed,i(t) = P_demand,i(t)"
> (no qualification)

**Correction Applied**:
Added explicit governance note immediately after the balance equation:
> "This balance equation defines accounting variables. It does NOT, by itself, define the operational semantics of shedding, deferral, interruption, restoration, or task scheduling for each tier. For example, P_shed,D(t) does not specify whether Deferrable load is delayed, interrupted, rescheduled, partially served, deadline-constrained, or task-constrained — those semantics are deferred to the EMS Implementation Specification."

---

## 4. WHAT IS PRESERVED (UNCHANGED)

### D1 — Fully Preserved
- Five-tier classification: L_C, L_E, L_D, L_I, L_N
- Disjoint union: L = L_C ∪ L_E ∪ L_D ∪ L_I ∪ L_N
- Deferrable ≠ Essential (explicitly maintained)
- Interruptible ≠ Noncritical (explicitly maintained)
- `D1_POLICY = RESOLVED`
- `LOAD_TIER_COUNT = 5`
- `LOAD_TIER_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`
- `STATION_LOAD_MAPPING = STATION_DATA_REQUIRED`

### D2 — Policy Concept Preserved, Unauthorized Sequence Removed
- Automated tier-based load shedding remains a **governed policy capability**
- Critical Load protection remains absolute during normal governed operation
- `D2_POLICY = RESOLVED`
- `D2_AUTOMATED_SHEDDING = POLICY_RESOLVED`

### Critical Load SLA (D3/D4/D5) — Unchanged
- `CRITICAL_LOAD_SERVICE_TARGET = 100%`
- `NORMAL_CRITICAL_UNMET = 0 kWh`
- `INTENTIONAL_CRITICAL_INTERRUPTION = 0 minutes`
- `CRITICAL_RELIABILITY = ABSOLUTE_PRIORITY`

### Regression Checks — All PASS
| Check | Status |
|-------|--------|
| D15_RECONCILIATION | PASS (unchanged) |
| STAGE2_OBJECTIVE_SEMANTICS = TARGET_SHORTFALL_MINIMIZATION | PASS (unchanged) |
| RESERVE_HEADROOM_MAXIMIZATION = DESCRIPTIVE_INTERPRETATION_ONLY | PASS (unchanged) |
| D8_PHYSICAL_FUEL_INVENTORY = PHYSICAL_CONSTRAINT | PASS (unchanged) |
| D8_SEASONAL_FUEL_ACCOUNTING = REQUIRES_IMPLEMENTATION_SPECIFICATION | PASS (unchanged) |
| D10_CURTAILMENT_DECOMPOSITION = CONCEPTUAL_DECOMPOSITION_ONLY | PASS (unchanged) |
| D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION | PASS (unchanged) |
| EMERGENCY_MODE_ENTRY = REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING | PASS (unchanged) |

---

## 5. FILES MODIFIED

| File | Change |
|------|--------|
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` | D1/D2 section rewritten; governance clarifications added; load variable descriptions corrected; load balance equation semantics note added; version 2.4.0 → 2.5.0 |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION.json` | D2 status keys added; version 2.4.0 → 2.5.0 |
| `POLARIS_EMS_VARIABLE_REGISTER.csv` | P_served_E/P_unmet_E/P_shed_E, P_served_I/etc., P_served_N/etc. governance status corrected; P_shed_D description corrected |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION_GOVERNANCE_STATUS.json` | D2 status keys added; CRITICAL_RELIABILITY_POLICY added |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION_GOVERNANCE_STATUS.md` | D2 status keys added; verification summary updated |

## 6. FILES CREATED

| File | Purpose |
|------|---------|
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION_D1_D2_BOUNDARY_CORRECTION.md` | This document |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION_D1_D2_BOUNDARY_CORRECTION.json` | JSON governance record |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION_D1_D2_BOUNDARY_TEST_MATRIX.csv` | 27-test verification matrix |

---

## 7. ZERO-EXECUTION VERIFICATION

```yaml
MODEL_TRAINED:                NO
MODEL_INFERRED:               NO
MILP_EXECUTED:                NO
MPC_EXECUTED:                 NO
EMS_EXECUTED:                 NO
DIGITAL_TWIN_EXECUTED:        NO
V2_RERUN:                     NO
NEW_EXPERIMENT:               NO
CODE_EXECUTION_FOR_EMS:       NO
EMS_CODE_MODIFIED:            NO
MILP_MODIFIED:                NO
OPTIMIZER_MODIFIED:           NO
CONFIG_MODIFIED:              NO
STAKEHOLDER_POLICY_REOPENED:  NO
D1_REOPENED:                  NO
D2_REOPENED:                  NO
```

---

## 8. FINAL GOVERNANCE STATUS

```yaml
D1_POLICY:                             RESOLVED
LOAD_TIER_COUNT:                       5
LOAD_TIER_FORMULATION:                 REQUIRES_IMPLEMENTATION_SPECIFICATION
STATION_LOAD_MAPPING:                  STATION_DATA_REQUIRED

D2_POLICY:                             RESOLVED
D2_AUTOMATED_SHEDDING:                 POLICY_RESOLVED
D2_SHEDDING_PRIORITY_ORDER:            REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_RESTORATION_ORDER:                  REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_TEMPORAL_SCHEDULING:                REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_INTERRUPTION_LIMITS:                REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_RESTART_BEHAVIOR:                   REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_ANTI_CHATTERING:                    REQUIRES_IMPLEMENTATION_SPECIFICATION
D2_EXECUTABLE_FORMULATION:             REQUIRES_IMPLEMENTATION_SPECIFICATION

CRITICAL_RELIABILITY_POLICY:           ABSOLUTE_PRIORITY
D15_RECONCILIATION:                    PASS
STAGE2_FORMULATION:                    REQUIRES_IMPLEMENTATION_SPECIFICATION
D8_SEASONAL_FUEL_ACCOUNTING:           REQUIRES_IMPLEMENTATION_SPECIFICATION
D10_EXECUTABLE_CLASSIFICATION:         REQUIRES_IMPLEMENTATION_SPECIFICATION
EMERGENCY_MODE_ENTRY:                  REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING

CURRENT_EMS_IMPLEMENTATION:            FROZEN
IMPLEMENTATION_AUTHORIZATION:          NOT_GRANTED
EMS_EXECUTION:                         NOT_AUTHORIZED
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW
```

---

**STOP.** This correction is complete. The next governed step is `EMS_OBJECTIVE_SPECIFICATION_REVIEW`. Do not begin the EMS Implementation Specification.
