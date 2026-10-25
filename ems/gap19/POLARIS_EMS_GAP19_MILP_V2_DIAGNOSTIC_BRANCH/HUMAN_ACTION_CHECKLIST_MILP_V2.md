# Human Action Checklist — Remaining MILP v2 Blockers

**Scope**: Synthesis of completed audits only. No code, config, or model changed; no
experiment run; no decision answered or value proposed below. GAP19 remains frozen as the
control. Every item below requires an authorized human or station source — none can be
closed by further document reconciliation alone.

---

### 1. Critical-service infeasibility fallback

- **Exact question/request**: What should the EMS do when Stage 1
  ($P_{\text{unmet,C}}(t) = 0$) is physically infeasible (e.g., fuel exhaustion, extreme
  weather, generator failure)? A human stakeholder must state the governed fallback
  behavior for this case.
- **Why required**: D04 covers *normal* operation (0 kWh unmet) and states emergency
  conditions need a *separate* policy — that separate policy has never been written.
- **What it unlocks**: resolution of `CRITICAL_RELIABILITY_INFEASIBILITY` in
  `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0, a prerequisite for that document's
  formal review (item 3) and for any MILP v2 infeasibility-handling logic.
- **Requires**: human/stakeholder decision.

### 2. Emergency Mode entry and policy mapping

- **Exact question/request**: What triggers transition into Emergency Mode, and how does
  that trigger map onto the EMS's operating-mode logic and lexicographic objective
  structure? A human stakeholder/technical authority must specify this.
- **Why required**: D06's lexicographic fallback is authorized only at the conceptual
  level; no trigger conditions or mode-transition mapping exist in any cited document.
- **What it unlocks**: resolution of `EMERGENCY_MODE_ENTRY` in v2.5.0, a prerequisite for
  that document's formal review (item 3) and for any MILP v2 mode-switching logic.
- **Requires**: human/stakeholder (and likely technical-validator) decision.

### 3. Formal v2.5.0 review/promotion

- **Exact question/request**: Once items 1–2 above are resolved, the named approval
  authorities (item 4) must formally review and either promote
  `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0 to an authorized specification or send it
  back for correction.
- **Why required**: v2.5.0's own status is `ESTABLISHED_AS_GOVERNED_DRAFT` with
  `Implementation Authorization: NOT_AUTHORIZED`; its own `NEXT_GOVERNED_STEP` field states
  a review has not yet occurred.
- **What it unlocks**: an authorized EMS objective specification that MILP v2 could
  actually be designed against (currently, no such authorized specification exists).
- **Requires**: human decision (by the D16 approval chain) — and is practically blocked
  until item 4 is also resolved.

### 4. Named D16 approval authorities

- **Exact question/request**: Who are the specific named individuals filling the Technical
  Validator, Cross-functional Reviewer, and Final Approver roles under the D16 three-tier
  approval structure?
- **Why required**: D16 authorizes the *structure* (no single role has unilateral
  authority), but no individual has been named to any of the three roles
  (`STATION_SPECIFIC_VALIDATION_REQUIRED` — SD-13).
- **What it unlocks**: a functioning approval pathway through which every other item in
  this checklist — and any future MILP v2 proposal itself — could actually be reviewed and
  ratified.
- **Requires**: station/organizational source (naming/appointing individuals).

### 5. Terminal-reserve physical unit (DEC-TR-03)

- **Exact question/request**: What physical quantity and unit defines Terminal Reserve
  (e.g., energy in Wh, percent SOC, or another quantity)? A human stakeholder must decide.
- **Why required**: `FINAL_GOVERNANCE_DECISION_STATUS.md` records
  `TERMINAL_PHYSICAL_UNIT = GOVERNANCE_DECISION_REQUIRED`; no document states an authorized
  unit.
- **What it unlocks**: closes DEC-TR-03, one of the two remaining open terminal-reserve
  decisions; a prerequisite for any governed (non-`SIMULATED_RESEARCH_ASSUMPTION`)
  terminal-reserve formulation in MILP v2.
- **Requires**: human/stakeholder decision (not gated on station data — a unit choice does
  not itself require battery specifications).

### 6. Station/BESS data for terminal-reserve numeric value (SD-07/SD-08)

- **Exact question/request**: Supply (a) the battery vendor's true technical minimum SOC
  (to confirm or revise the current 20% prototype value) — **SD-07**; and (b) battery
  degradation curves vs. depth of discharge — **SD-08**. Both must come from real station/
  vendor equipment data.
- **Why required**: tension **T-02** in `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`
  states SD-07/SD-08 validation is required *before any numerical values are governed* for
  the reserve envelope; `FINAL_EVIDENCE_RECOVERY_VERDICT.md` confirms
  `BATTERY_BESS = NOT_ESTABLISHED`, with a hard stop applied pending this data.
- **What it unlocks**: closes the data-dependency blocking DEC-RES-03 (the authorized
  numeric terminal-reserve value), without which MILP v2's reserve formulation would remain
  as unauthorized as R1/R2's research-only formula.
- **Requires**: station/technical source (vendor documentation or physical measurement) —
  not a policy decision.

---

## STOP

Checklist complete. No decision answered, no value proposed, no code/config/model changed.
GAP19 remains frozen as the control.
