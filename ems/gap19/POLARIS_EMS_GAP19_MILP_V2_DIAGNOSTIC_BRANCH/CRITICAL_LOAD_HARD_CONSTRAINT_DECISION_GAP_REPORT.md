# Critical-Load Hard Constraint: Decision/Gap Report

**Scope**: Audit only, of authoritative governance documents. No code, config, or model
changed; no experiment run. Current GAP19 remains unmodified and frozen as the control; it
is not referenced anywhere in the governed specification document discussed below and has
never been formally reviewed against it.

**Key source found in this pass** (not cited in earlier audits):
`POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0
("GOVERNED EMS OBJECTIVE SPECIFICATION V2") — this is the document the earlier audits'
`NEXT_EMS_OBJECTIVE_SPECIFICATION` placeholder pointed toward; it now exists in draft form.

---

## 1. Exact policy requirement already authorized

From the Stakeholder Decision Sheet (D03/D04/D05/D06), unchanged and still in force:
- 100% continuous Critical-load service in normal governed operation (D03).
- 0 kWh unmet Critical load in normal governed operation (D04); emergency conditions
  require a *separately defined* emergency policy (not yet specified — see §3).
- 0 minutes intentional interruption for Critical loads, as a policy requirement, distinct
  from physical hardware transfer gaps (D05).
- This must be formulated as a **hard constraint, not a soft economic penalty** — stated
  explicitly, with the $10,000/kWh soft-penalty implementation (`milp.py`) named as the
  example of what does **not** satisfy this policy (D06 + `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §3.2).

**This part is fully authorized and unambiguous.**

## 2. Mathematical/formulation status — partially advanced since the prior audit, still
not authorized for implementation

A governed draft specification now exists:
`POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0, dated 2026-09-22, states:

```yaml
EMS_OBJECTIVE_SPECIFICATION:   ESTABLISHED_AS_GOVERNED_DRAFT
STAKEHOLDER_POLICY_APPROVAL:   APPROVED
POLICY_TO_MATH_MAPPING:        COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS
Implementation Authorization:  NOT_AUTHORIZED
NEXT_GOVERNED_STEP:             EMS_OBJECTIVE_SPECIFICATION_REVIEW
```

It gives an explicit mathematical form for the critical-reliability stage: **Stage 1:
$P_{\text{unmet,C}}(t) = 0$**, within a strict lexicographic hierarchy (Stage 1 → 2 → 3 → 4,
consistent with D15), and explicitly flags the prior soft-penalty implementation as a
`MISMATCH` to be replaced.

**Still explicitly unresolved within this same draft** (its own status fields, not
inferred):
- `CRITICAL_RELIABILITY_INFEASIBILITY: REQUIRES_GOVERNANCE_CLARIFICATION` — what happens
  when Stage 1 ($P_{unmet,C}=0$) is physically infeasible (e.g., fuel exhaustion) is
  **not yet decided**, only flagged as needing governance input.
- `EMERGENCY_MODE_ENTRY: REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING` —
  the trigger/transition logic into the emergency policy D04 refers to is not specified.
- A cross-document inconsistency, confirmed and not resolved anywhere found: this draft's
  `LOAD_TIER_COUNT: 5` contradicts `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`'s explicit
  correction that only a **3**-tier structure is stakeholder-authorized (the 5-tier
  elaboration is `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE — NOT_STAKEHOLDER_AUTHORIZED`). This
  draft's internal tier count has not been reconciled with that correction.

## 3. Decisions requiring human/governance approval before this can move forward

- Formal **review and promotion** of the draft from `ESTABLISHED_AS_GOVERNED_DRAFT` to an
  authorized specification — the draft's own `NEXT_GOVERNED_STEP` is
  `EMS_OBJECTIVE_SPECIFICATION_REVIEW`, which has not occurred. Per D16, this requires the
  multi-tier approval chain (Technical Validator → Mission/Ops Reviewer → Final Approver) —
  none of whom are named individuals yet (confirmed unresolved in the earlier governance
  package, SD-13).
- Resolution of `CRITICAL_RELIABILITY_INFEASIBILITY` (what governs the system when 0 kWh
  unmet critical load is not physically achievable) — explicitly open.
- Resolution of `EMERGENCY_MODE_ENTRY` mapping (how/when the system transitions into the
  emergency policy referenced by D04) — explicitly open.
- Reconciliation of the 5-tier vs. 3-tier-authorized inconsistency noted above.

## 4. Is anything currently authorized for implementation?

**No.** The *policy* (D03/D04/D05/D06: hard constraint, 100%/0 kWh/0 min in normal
operation) is stakeholder-authorized. A *mathematical draft* of it now exists and is marked
stakeholder-policy-approved as an input — but the document's own top-level field states
**`Implementation Authorization: NOT_AUTHORIZED`**, alongside `EMS_EXECUTION`,
`EMS_IMPLEMENTATION_MODIFICATION`, and `MPC_EXECUTION`, all also `NOT_AUTHORIZED`. **GAP19's
existing code is not mentioned anywhere in this specification document and has never been
formally reviewed against it** — its current hard-cap treatment of critical load
(`p_served ≤ critical_demand`, top-priority `P_unmet_crit`) happens to resemble the Stage 1
formulation, but this resemblance has no governance standing; it was built independently and
has not been certified as satisfying this draft or any other governed document.

## STOP

Decision/gap report complete. No code, config, or model changed. GAP19 remains frozen as the
control.
