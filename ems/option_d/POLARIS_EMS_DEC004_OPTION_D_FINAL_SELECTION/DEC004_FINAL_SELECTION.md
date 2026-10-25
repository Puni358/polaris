# POLARIS EMS — DEC-004 FINAL SELECTION RECORD

## 1. Authoritative Governance Selection

The human decision-maker has explicitly selected **Option D — Protected Critical-Load Fallback** as the authoritative policy response for **DEC-004: UNKNOWN_INVALID Operational Response**.

- **DECISION_ID**: `DEC-004`
- **DECISION_TITLE**: `UNKNOWN_INVALID Operational Response`
- **FINAL_SELECTION**: `OPTION_D_PROTECTED_CRITICAL_LOAD_FALLBACK`
- **DECISION_AUTHORITY**: `HUMAN GOVERNANCE DECISION`
- **DECISION_STATUS**: `FINAL_SELECTED`
- **SELECTION_DATE**: `2026-09-23`
- **DECISION_SCOPE**: Governed response when Emergency Condition Detector (ECD) returns `UNKNOWN_INVALID`.

---

## 2. Alternatives Evaluated & Status

| Option | Identifier | Governance Status | Role in Decision Record |
| :--- | :--- | :--- | :--- |
| **Option A** | `OPTION_A_FAIL_CLOSED` | `NOT_SELECTED` | Preserved documented alternative |
| **Option B** | `OPTION_B_HOLD_LAST_GOOD` | `NOT_SELECTED` | Preserved documented alternative |
| **Option C** | `OPTION_C_HEURISTIC_RULE_BASED` | `NOT_SELECTED` | Preserved documented alternative |
| **Option D** | `OPTION_D_PROTECTED_CRITICAL_LOAD_FALLBACK` | `SELECTED` | Authoritative governed policy |

> [!NOTE]
> Options A, B, and C remain preserved in the governance history as valid technical alternatives evaluated during DEC-004 decision-support analysis. "NOT_SELECTED" does not imply technical invalidity; it records that human governance selected Option D.

---

## 3. Governance Scope Boundary

### What DEC-004 Answers:
DEC-004 establishes the high-level policy answer to:
*"What governed operational response should POLARIS use when ECD returns UNKNOWN_INVALID?"*
**Answer**: Option D — Protected Critical-Load Fallback (D1 through D6 rules).

### What DEC-004 Does NOT Answer (Deferred Engineering & Governance Inputs):
DEC-004 does **NOT** resolve or authorize:
1. Exact production $T_{\text{required}}$ value or override TTL.
2. Exact degraded-operation watchdog duration ($T_{\text{max,degraded}}$).
3. Minimum fuel-reserve escalation threshold ($F_{\text{reserve,min}}$).
4. Telemetry maximum age / TTL definitions.
5. Production telemetry cryptographic authentication mechanism.
6. Station-specific protected critical equipment inventory & circuit mapping.
7. Station-specific dynamic critical-load formulation $P_{\text{critical}}(t)$.
8. Station-specific battery SOC reserve boundaries (charge/discharge floors & ceilings).
9. Generator physical operating parameters (minimum power, fuel curves).
10. Concrete software implementation architecture or runtime code changes.

---

## 4. Implementation Firewall & Authorization Notice

- **OPTION_D_GOVERNANCE_STATUS**: `SELECTED_AND_SEALED`
- **OPTION_D_RUNTIME_IMPLEMENTATION**: `NOT_IMPLEMENTED`
- **IMPLEMENTATION_AUTHORIZATION**: `NOT_GRANTED`
- **PRODUCTION_DEPLOYMENT**: `BLOCKED`

The selection of Option D seals the policy definition. It does NOT authorize code modifications, schema changes, optimizer re-formulation, or runtime execution. Implementation will be authorized under a separate future governance gate after engineering parameters are defined.
