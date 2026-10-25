# Human Governance Decision Packet — Prerequisites for MILP v2

**Scope**: Synthesis of audits already completed. No code, config, or model changed; no
experiment run. No decision is chosen or recommended below. GAP19 remains unmodified and
frozen as the control throughout.

Each item lists: decision ID (if one exists) · exact question · current authorized position ·
unresolved conflict/gap · what becomes authorized once decided.

---

### 1. Load-tier structure: 3-tier vs. 5-tier

- **Decision ID**: D01 (already `HUMAN_SELECTED` at the 3-tier level); no ID exists for the
  5-tier figure.
- **Exact question**: Should the governed load-tier structure remain the 3-tier model
  (Critical / Essential-Flexible / Interruptible-Noncritical), or is a 5-tier structure
  (as used in `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0's `LOAD_TIER_COUNT: 5`)
  to be newly authorized?
- **Current authorized position**: 3-tier (D01). The 5-tier elaboration is explicitly
  `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE — NOT_STAKEHOLDER_AUTHORIZED`
  (`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`).
- **Unresolved conflict/gap**: v2.5.0 declares the 3-tier document as its own policy input
  (`POLICY_DEFINITION_RESOLUTION: APPROVED_AS_POLICY_INPUT`) yet internally uses
  `LOAD_TIER_COUNT: 5` — an unreconciled non-conformance, not a second authorization.
- **What becomes authorized after approval**: either (a) v2.5.0 is corrected to 3 tiers, or
  (b) a stakeholder explicitly authorizes a 5-tier structure, superseding D01. Until one
  occurs, no tier count beyond the existing 3 is usable as a basis for MILP v2.

### 2. Critical-service infeasibility behavior

- **Decision ID**: none assigned; flagged in v2.5.0 as `CRITICAL_RELIABILITY_INFEASIBILITY`.
- **Exact question**: What is the governed fallback behavior when Stage 1
  ($P_{\text{unmet,C}}(t) = 0$) is physically infeasible (e.g., fuel exhaustion, extreme
  weather, generator failure)?
- **Current authorized position**: D04 establishes 0 kWh unmet critical load in *normal*
  operation, and that *emergency* conditions require a *separately defined* emergency
  policy — but that separate policy does not yet exist.
- **Unresolved conflict/gap**: `CRITICAL_RELIABILITY_INFEASIBILITY: REQUIRES_GOVERNANCE_CLARIFICATION`
  (v2.5.0's own status field) — no governed answer exists for this case.
- **What becomes authorized after approval**: a defined infeasibility-handling rule (e.g.,
  what is shed, logged, and reported when Stage 1 cannot be met) that MILP v2 could
  implement as a governed fallback path.

### 3. Emergency Mode entry/mapping

- **Decision ID**: none assigned; flagged in v2.5.0 as `EMERGENCY_MODE_ENTRY`.
- **Exact question**: What triggers transition into Emergency Mode, and how does that
  transition map onto the EMS's operating-mode logic and the lexicographic objective
  structure?
- **Current authorized position**: D06's lexicographic fallback during infeasibility is
  `HUMAN_SELECTED_POLICY` at the conceptual level only; no trigger conditions or mapping
  logic are specified anywhere found.
- **Unresolved conflict/gap**: `EMERGENCY_MODE_ENTRY: REQUIRES_IMPLEMENTATION_SPECIFICATION_AND_GOVERNANCE_MAPPING`
  (v2.5.0's own status field).
- **What becomes authorized after approval**: an explicit, governed mode-transition
  specification MILP v2 (and the router/EMS logic around it) could be built against.

### 4. v2.5.0 formal review/promotion

- **Decision ID**: none; tracked via v2.5.0's own `NEXT_GOVERNED_STEP` field.
- **Exact question**: Should `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0 be formally
  reviewed and promoted from draft to an authorized specification (after items 1–3 above
  are resolved)?
- **Current authorized position**: v2.5.0 is `ESTABLISHED_AS_GOVERNED_DRAFT`, stakeholder
  policy-approved as an *input*, but `Implementation Authorization: NOT_AUTHORIZED`.
- **Unresolved conflict/gap**: `NEXT_GOVERNED_STEP: EMS_OBJECTIVE_SPECIFICATION_REVIEW` has
  not occurred; the document cannot currently serve as an implementation authority
  (confirmed in the prior governance-status audit).
- **What becomes authorized after approval**: v2.5.0 (or a corrected version of it) becomes
  an authorized EMS objective specification that MILP v2 could be designed against.

### 5. D16 approval chain / authority gap

- **Decision ID**: D16 (structure already `HUMAN_SELECTED`); the gap is in staffing, not
  the decision itself.
- **Exact question**: Who are the named individuals filling the Technical Validator,
  Cross-functional Reviewer, and Final Approver roles required to review/approve items 1–4?
- **Current authorized position**: D16 establishes the three-tier approval *structure*
  (Technical → Mission/Ops → Final Approval), with no single role having unilateral
  authority.
- **Unresolved conflict/gap**: named individuals are `STATION_SPECIFIC_VALIDATION_REQUIRED`
  (SD-13) — no one is currently named to any of these roles, so no formal review of items
  1–4 above can be executed even if content were otherwise ready.
- **What becomes authorized after approval**: a functioning approval pathway through which
  every other item in this packet, and any future MILP v2 proposal itself, could actually be
  ratified.

### 6. Remaining terminal-reserve decisions blocking MILP v2

- **Decision IDs**: DEC-TR-03, DEC-RES-03 (open); DEC-TR-01/02/04/05 already resolved per
  earlier audit.
- **Exact questions**:
  - DEC-TR-03 — What physical quantity/unit defines Terminal Reserve?
  - DEC-RES-03 — What specific numerical values/formula are authorized for the reserve
    target?
- **Current authorized position**: structural policy already decided (dynamic, risk-based,
  $J_2$-objective, not a hard constraint — recorded in the earlier research-governance
  package); no unit or numeric value is authorized.
- **Unresolved conflict/gap**: both remain `GOVERNANCE_DECISION_REQUIRED`, and are further
  gated on station-data validations **SD-07** (battery vendor true minimum SOC) and
  **SD-08** (battery degradation curves), both `NOT_ESTABLISHED` (confirmed:
  `BATTERY_BESS = NOT_ESTABLISHED`, hard stop applied, in the earlier evidence-recovery
  audit).
- **What becomes authorized after approval**: a governed numeric terminal-reserve target
  and unit that MILP v2 could implement in place of the current
  `SIMULATED_RESEARCH_ASSUMPTION` formula used in R1/R2.

---

## STOP

Decision packet complete. No decisions made or recommended. No code, config, or model
changed. GAP19 remains frozen as the control.
