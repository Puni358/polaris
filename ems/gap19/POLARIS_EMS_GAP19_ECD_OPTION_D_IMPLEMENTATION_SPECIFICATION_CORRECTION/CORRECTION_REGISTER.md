# Correction Register & Classification Matrix

## Forensic Audit Purpose
This package provides a **correction-only forensic review** of the POLARIS EMS GAP19 ECD $\to$ Option D Implementation Specification. Unresolved governance and runtime boundaries previously overstated as established implementation requirements are hereby formally corrected and classified under the mandatory 7-category scheme.

## Mandatory 7-Category Classification Scheme
1. `GOVERNED_AND_ESTABLISHED`: Formally decided and sealed by human governance (Decisions D1–D4, DEC-004).
2. `IMPLEMENTED_AND_VERIFIED`: Coded, tested, and verified in source (`system/control/ecd.py`, `gap19_highs_native.py`).
3. `ENGINEERING_INTERFACE_ONLY`: Functional adapter boundary identified without runtime action commitment.
4. `PROPOSED_IMPLEMENTATION`: Candidate software design for future integration.
5. `NOT_ESTABLISHED`: Missing operational policy or un-governed runtime behavior.
6. `GOVERNANCE_REQUIRED`: Requires explicit human policy choice before code implementation.
7. `ENGINEERING_INPUT_REQUIRED`: Requires physical station measurements or hardware data.

---

## 10-Point Correction Summary Table

| Item # | Subject | Previous Claim (Incorrect / Overstated) | Corrected Classification | Status |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `UNKNOWN_INVALID` Action | Claimed `CRITICAL_TERMINATION` / fail-closed halt | `UNKNOWN_INVALID_RUNTIME_ACTION = NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| **2** | MILP Infeasibility Normal Path | Claimed "Degraded Normal Fallback" optimizer | `NORMAL_AFTER_INFEASIBILITY_ACTION = NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| **3** | Emergency Return | Claimed `EMERGENCY_RETURN_INTERFACE = SPECIFIED` | `EMERGENCY_RETURN_POLICY = NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| **4** | Option D Horizon | Claimed 24h / 24-step DispatchPlan schedule | `OPTION_D_HORIZON = NOT_ESTABLISHED` | `ENGINEERING_INPUT_REQUIRED` |
| **5** | Option D Numerical Rules | Over-specified numerical thresholds | `OPTION_D_POLICY = GOVERNED_AND_SEALED` (DEC-004 only) | `GOVERNED_AND_ESTABLISHED` |
| **6** | Preserved/Limiting Semantics | Verified ordering semantics | Larger margin = Preserved; Smaller = Limiting; Equal = Tie | `IMPLEMENTED_AND_VERIFIED` |
| **7** | Schema Extensions | Claimed override fields as policy knobs | `SCHEMA_DELTA = PARTIALLY_REQUIRED` (Remove overrides) | `PROPOSED_IMPLEMENTATION` |
| **8** | Authority Escalation | Claimed concrete `FaultEvent` subclasses | `AUTHORITY_ESCALATION_RUNTIME = NOT_IMPLEMENTED` | `ENGINEERING_INTERFACE_ONLY` |
| **9** | Specification Scope Claim | Claimed "100% Specified" | `SPECIFICATION_SCOPE = PARTIALLY_SPECIFIED` | `PROPOSED_IMPLEMENTATION` |
| **10** | Readiness Verdict | Claimed `READY_FOR_IMPLEMENTATION_AUTHORIZATION` | `IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED` | `GOVERNANCE_REQUIRED` |
