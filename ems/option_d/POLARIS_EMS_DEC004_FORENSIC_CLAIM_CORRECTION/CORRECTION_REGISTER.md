# POLARIS EMS — FORENSIC CLAIM CORRECTION REGISTER

## 1. Executive Summary

This register formally records every claim from the previous decision-support package (`POLARIS_EMS_DEC004_DECISION_SUPPORT_AND_OPTION_D_ARCHITECTURE_AUDIT/`) that was found to be overstated or conflated, providing the exact forensic classification, code evidence, required correction, and impact on DEC-004 decision support.

---

## 2. Itemized Correction Entries

### CORRECTION ENTRY 1: Option D State Recovery Status
- **CLAIM_ID**: `CLR-001` (Option D State Recovery)
- **PREVIOUS_CLASSIFICATION**: `ESTABLISHED` ("MPC loop resumes immediately, discarding degraded plans...").
- **FORENSIC_CLASSIFICATION**: `PROPOSED_ONLY` / `NOT_ESTABLISHED_IN_CODE`.
- **EVIDENCE**: `system/runtime/runner.py` contains zero imports of `ecd.py`, zero calls to `ecd.evaluate()`, zero plan cache logic, and zero recovery state transition code.
- **WHY_TOO_STRONG**: Conflated an architectural design proposal with an established executable code fact.
- **REQUIRED_CORRECTION**: Re-classify Option D state recovery as `PROPOSED_ARCHITECTURE` / `REQUIRES_IMPLEMENTATION_AUTHORIZATION`.
- **IMPACT_ON_DEC004_DECISION_SUPPORT**: Clarifies to the human decision-maker that choosing Option D will require future software implementation of the recovery state handler before runtime deployment.

---

### CORRECTION ENTRY 2: Option D Operator Escalation Status
- **CLAIM_ID**: `CLR-002` (Operator Escalation & FaultEvent Logging)
- **PREVIOUS_CLASSIFICATION**: `ESTABLISHED` ("Originates in Mode Manager; logs FaultEvent(fault_class='INVALID_SURVIVABILITY_ASSESSMENT')...").
- **FORENSIC_CLASSIFICATION**: `ESTABLISHED_BY_GOVERNANCE_ONLY` / `NOT_ESTABLISHED_IN_CODE`.
- **EVIDENCE**: The exact string `"INVALID_SURVIVABILITY_ASSESSMENT"` exists strictly in markdown files and is 100% absent from Python code (`system/`). `runner.py` logs `FaultEvent` for solver errors, but has zero code handling ECD `UNKNOWN_INVALID` escalation.
- **WHY_TOO_STRONG**: Conflated an authorized governance policy rule (D4/D5) with an implemented Python code handler.
- **REQUIRED_CORRECTION**: Re-classify operator escalation as `ESTABLISHED_BY_GOVERNANCE` (policy authorized) and `NOT_ESTABLISHED_IN_CODE` (runner handler un-implemented).
- **IMPACT_ON_DEC004_DECISION_SUPPORT**: Clarifies that while governance policy D4/D5 is authorized, runtime code integration remains a future implementation requirement.

---

### CORRECTION ENTRY 3: MILP Objective Guarantee vs. Prototype Penalty Weight
- **CLAIM_ID**: `CLR-003` (MILP Objective Compatibility & Stage 1 Guarantee)
- **PREVIOUS_CLASSIFICATION**: `NO_CONFLICT` ("Current $10/Wh scalar penalty guarantees critical reliability").
- **FORENSIC_CLASSIFICATION**: `IMPLEMENTATION_SCALAR_FACT_SEPARATED_FROM_GOVERNED_TARGET`.
- **EVIDENCE**: `milp.py` line 49 sets `unmet_penalty_per_wh = 10.0` as a single scalar penalty in a single-pass solver. `milp.py` contains zero multi-pass sequential or HiGHS lexicographic solver code.
- **WHY_TOO_STRONG**: Conflated a single prototype scalar penalty weight (`$10/Wh`) with an implemented 4-stage lexicographic objective guarantee.
- **REQUIRED_CORRECTION**: Explicitly decouple `CURRENT_IMPLEMENTATION_FACT` (scalar `$10/Wh` in `milp.py`) from `GOVERNED_TARGET_ARCHITECTURE` (4-stage lexicographic hierarchy).
- **IMPACT_ON_DEC004_DECISION_SUPPORT**: Clarifies that Option D mathematical formulation is linear-compatible, but production lexicographic solver locking remains a future engineering input.

---

## 3. Summary of Register Impact

```text
TOTAL_CLAIMS_AUDITED            = 3
CLAIMS_CORRECTED                = 3
DEC004_FINAL_SELECTION          = UNDECIDED (Unchanged)
OPTION_D_GOVERNANCE_STATUS      = SEALED_UNCHANGED (D1-D6 remain frozen)
IMPLEMENTATION_AUTHORIZATION    = NOT_GRANTED (Unchanged)
```

Status: `CORRECTION_REGISTER_SEALED`
