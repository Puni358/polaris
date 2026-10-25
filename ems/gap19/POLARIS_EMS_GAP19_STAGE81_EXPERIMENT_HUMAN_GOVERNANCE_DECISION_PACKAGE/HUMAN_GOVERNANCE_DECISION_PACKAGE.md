# Human Governance Decision Package
## Stage 8.1 → MILP Closed-Loop Experiment (Baseline vs. Frozen Stage 8.1 Forecast)

**Package Label**: `POLARIS_EMS_GAP19_STAGE81_EXPERIMENT_HUMAN_GOVERNANCE_DECISION_PACKAGE`
**Purpose**: Surface the human decisions required before the Stage 8.1-vs-baseline closed-loop
experiment may run. This package does not select numerical values, formulas, or
authorize execution.
**Revision**: Updated to record newly-made human policy decisions on Terminal Reserve
structure (below). Numerical values, formulation details, and execution authorization
remain open.
**Resolution attempt (this revision)**: A search for authoritative evidence to close
SD-07, SD-08, DEC-TR-03, DEC-RES-03, SD-13, and execution authorization was performed
across all existing governance and station-evidence documents. **None of these blockers
could be legitimately resolved from existing evidence.** See §7 (RESOLUTION ATTEMPT —
RESULT: HARD STOP) below. No fallback or test value was substituted for any of them, and
no experiment was run.

---

## 1. CURRENT STATUS

| Item | Status |
|---|---|
| Stage 8.1 forecasting | `FROZEN` / `VALIDATED` |
| Stage 8.1 → POLARIS runtime integration | `VERIFIED` |
| `demand_critical` / `critical_demand_w` gap | `RESOLVED` |
| `terminal_target_wh` (GAP19 terminal reserve) | `POLICY_STRUCTURE_DECIDED — NUMERICS_AND_FORMULATION_PENDING` |
| `EXPERIMENT_EXECUTION` | `NOT_AUTHORIZED` |
| `SIMULATION_EXECUTION` | `NOT_AUTHORIZED` |
| `MILP_EXECUTION` | `NOT_AUTHORIZED` |

These `NOT_AUTHORIZED` execution flags are carried forward unmodified from
`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`
("ABSOLUTE GOVERNANCE BOUNDARIES") and
`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION/POLARIS_EMS_POLICY_DEFINITION_GOVERNANCE_STATUS.md`.
They apply to the proposed experiment exactly as they apply to production execution; no
research/experiment carve-out exists in either document. The policy decisions in §2a do
not change this — policy structure and execution authorization are separate decisions.

**Note on experiment hypothesis**: this package makes no claim, implied or otherwise, that
Stage 8.1 will outperform the baseline forecast. The experiment (§5) is designed to compare
the two; the outcome is not assumed.

---

## 2. REQUIRED HUMAN DECISIONS

### 2a. Decisions now made (HUMAN_SELECTED_POLICY)

The following Terminal Reserve policy decisions have been made by the human stakeholder and
are recorded here, in the terminology of
`POLARIS_EMS_GAP19_EBR_TERMINAL_RESERVE_GOVERNANCE/REQUIRED_HUMAN_DECISIONS.md`:

| Decision | Resolution | Governance ID(s) addressed |
|---|---|---|
| Terminal Reserve is dynamic | Based on future demand + renewable availability | DEC-TR-04 |
| Includes an uncertainty/risk component | Yes | DEC-TR-02, DEC-TR-04 |
| Enforcement mechanism | Secondary lexicographic objective ($J_2$), **not** a hard constraint | DEC-TR-05 |
| Reserve shortfall reporting | Shortfall is explicitly reported | — (new, operational) |
| Minimum reserve floor | A station-defined minimum reserve floor exists | — (consistent with D12's "minimum terminal SOC floor") |
| Emergency Mode interaction | Terminal Reserve does **not** alter or trigger Emergency Mode | — (new, boundary clarification) |
| Cost treatment | Reserve preservation may incur operating cost through $J_2$ | — (new, objective clarification) |
| Information basis | Use only information available at optimization time; no hindsight / future actuals | — (new, causality constraint) |

These are structural/policy decisions, consistent with and extending the already-decided
**D12** structure (`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §6.2: "a dynamic terminal
SOC requirement" + "a minimum terminal SOC floor"). They decide *what kind* of mechanism
Terminal Reserve is; they do not decide its numbers or exact formula (§2b).

### 2b. Decisions still required (GOVERNANCE_DECISION_REQUIRED / TECHNICAL_VALIDATION_REQUIRED)

- **DEC-TR-03** — What physical quantity and unit defines Terminal Reserve? `GOVERNANCE_DECISION_REQUIRED`.
- **DEC-RES-03** — What specific numerical values are authorized? `GOVERNANCE_DECISION_REQUIRED` (gated on station data; see §4).
- **Formula / mathematical definition of the dynamic reserve** (how future demand, renewable availability, and uncertainty combine into a target) — `TECHNICAL_VALIDATION_REQUIRED`.
- **Look-ahead duration** used to assess future demand/renewable availability — `TECHNICAL_VALIDATION_REQUIRED`.
- **Recalculation frequency** of the dynamic target within the rolling MPC horizon — `TECHNICAL_VALIDATION_REQUIRED`.
- **Interaction between the minimum reserve floor and the dynamic target** (e.g. which binds, how they combine) — `TECHNICAL_VALIDATION_REQUIRED`.
- **Uncertainty source/model** (what uncertainty is modeled, and how) — `TECHNICAL_VALIDATION_REQUIRED`, per the human decision in §2a that an uncertainty component must exist, without specifying its model.
- **Explicit execution authorization** for this specific research simulation (§5) — separate from the above, still `NOT_AUTHORIZED` (see §1).

---

## 3. EXISTING OPTIONS

As defined in `POLARIS_EMS_GAP19_EBR_TERMINAL_RESERVE_GOVERNANCE/DECISION_OPTIONS_MATRIX.md`
("Candidate Terminal Reserve Formulations"), reproduced verbatim for reference. The §2a
decisions narrow the structural space (dynamic, risk-aware, $J_2$ objective) but **no
specific option, formula, or numerical value is selected, ranked, or recommended** by this
package:

- **TR-A**: Fixed Terminal SOC Target (e.g. $Z\%\ \text{SOC}$).
- **TR-B**: Fixed Terminal Energy Target ($E_{\text{terminal}} \ge E_{\text{initial}}$).
- **TR-C**: Dynamic Terminal Reserve derived from forecast horizon boundary condition.
- **TR-D**: Dynamic Terminal Reserve derived from future critical load survivability.
- **TR-E**: Zero separate terminal reserve (eliminate $s_{\text{terminal}}$, rely on
  $s_{\text{EBR}}[23]$).

**Provisional / unauthorized numerical values** (unchanged; still not authorized by §2a):

| Value | Status (as marked in source) |
|---|---|
| 35% minimum terminal SOC | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 55–65% precautionary terminal SOC | `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 160,000 Wh (test-script `terminal_target_wh`) | `NEW TEST-HARNESS VALUE` / `NOT ESTABLISHED` |
| `terminal_reserve_model: "INITIAL_STATE"` (code fallback) | test/smoke-test workaround only; not governance-authorized |

---

## 4. REQUIRED VALIDATION

Per tension **T-02** (`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`): *"EBR structure and
terminal SOC structure must be physically achievable across consecutive low-renewable
days ... SD-07, SD-08 validation required before any numerical values are governed."*

- **SD-07** — Battery vendor true technical minimum SOC (confirm/revise 20%).
- **SD-08** — Battery degradation curves.
- **Uncertainty source/model** (§2b) — a technical-validation decision, not resolved by
  this package's policy decisions.
- Formula, look-ahead duration, recalculation frequency, and floor-interaction (§2b) all
  require technical validation before numerical authorization can proceed.

---

## 5. EXPERIMENT SCOPE (PROPOSED — NOT AUTHORIZED)

Run the same physical station scenario and the same GAP19 MILP formulation twice under
otherwise identical configuration — once driven by the baseline forecast engine and once
driven by the frozen, validated Stage 8.1 forecast engine — and compare the two runs'
outcomes (e.g. dispatch decisions, fuel use, unmet load, curtailment, reported reserve
shortfall) on the closed-loop worker path in `system/orchestration/worker.py`. The only
intended difference between the two runs is the forecast engine; all other configuration,
including whichever Terminal Reserve formulation and numbers are eventually authorized,
would be held identical between arms. This description is neutral as to outcome: it does
not assume either forecast engine performs better.

**This experiment is NOT currently authorized to run.** It remains blocked by §1 and §2b,
independent of the policy decisions recorded in §2a.

---

## 6. DECISION RECORD

To be completed/confirmed by the human stakeholder(s) identified under the governance
structure in `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §10 (Technical Validator →
Cross-functional Reviewer → Final Approver; no single role has unilateral authority per
stakeholder decision D16).

### Terminal Reserve policy structure (DEC-TR-04, DEC-TR-05, DEC-TR-02) — DECIDED
- Decision: Dynamic Terminal Reserve, based on future demand and renewable availability,
  including an uncertainty/risk component; enforced via secondary lexicographic $J_2$
  objective, not a hard constraint; shortfall explicitly reported; does not alter/trigger
  Emergency Mode; may incur operating cost through $J_2$; uses only information available
  at optimization time (no hindsight/future actuals).
- Rationale: ________________________________________
- Authorized value/model: `NOT_APPLICABLE — STRUCTURE ONLY, NUMERICS PENDING`
- Execution authorization: `NOT_AUTHORIZED`
- Approver / sign-off: ________________________________________
- Date: ________________________________________

### DEC-TR-03 — Terminal Reserve physical quantity/unit
- Decision: ________________________________________
- Rationale: ________________________________________
- Authorized value/model: ________________________________________
- Execution authorization: ________________________________________
- Approver / sign-off: ________________________________________
- Date: ________________________________________

### DEC-RES-03 — Authorized numerical value/model (formula, look-ahead, recalculation
frequency, floor interaction, uncertainty model — all `TECHNICAL_VALIDATION_REQUIRED`)
- Decision: ________________________________________
- Rationale: ________________________________________
- Authorized value/model: ________________________________________
- Execution authorization: ________________________________________
- Approver / sign-off: ________________________________________
- Date: ________________________________________

### Execution authorization — this specific research simulation (§5)
- Decision: ________________________________________
- Rationale: ________________________________________
- Authorized value/model: ________________________________________
- Execution authorization: ________________________________________
- Approver / sign-off: ________________________________________
- Date: ________________________________________

---

## BLOCKERS REMAINING BEFORE EXECUTION CAN LEGALLY/PROCEDURALLY BEGIN

1. **DEC-TR-03** (terminal reserve unit) unresolved.
2. **DEC-RES-03** (numerical value/model) unresolved; gated on **SD-07**, **SD-08**, and
   the technical-validation items in §2b (formula, look-ahead duration, recalculation
   frequency, floor interaction, uncertainty model).
3. **No explicit execution authorization** exists for this research simulation —
   `EXPERIMENT_EXECUTION`, `SIMULATION_EXECUTION`, `MILP_EXECUTION` remain
   `NOT_AUTHORIZED`, unaffected by the §2a policy decisions.
4. **No individual or body currently holds confirmed authority to approve** — roles
   (Technical Validator / Cross-functional Reviewer / Final Approver) are only
   `CONCEPTUALLY_RESOLVED`; named individuals remain `STATION_SPECIFIC_VALIDATION_REQUIRED`
   (SD-13).

Until all four are closed, the Stage 8.1-vs-baseline closed-loop experiment cannot proceed.

---

## 7. RESOLUTION ATTEMPT — RESULT: HARD STOP

A targeted search of all existing governance and station-evidence documents in the
repository was performed to try to close the remaining blockers using only authoritative
evidence already on record. No invented values, formulas, or assumptions were introduced.
Result, blocker by blocker:

| Blocker | Evidence searched | Result |
|---|---|---|
| **SD-07** (battery vendor true minimum SOC) | `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY/FINAL_EVIDENCE_RECOVERY_VERDICT.md`, `BATTERY_BESS_RECOVERY.md`; `investigations/battery_physical_evidence_acquisition_20260930/*` | **NOT_ESTABLISHED.** The evidence-recovery verdict explicitly records `BATTERY_BESS = NOT_ESTABLISHED` with `STATION_MEASURED_DATA_RECEIVED = NO` and applies its own `HARD_STOP`. No vendor datasheet exists anywhere in the repository. |
| **SD-08** (battery degradation curves) | `investigations/battery_degradation_model_validation_20260930/*`, `investigations/battery_degradation_physical_sensitivity_1year_20260930/BATTERY_PHYSICAL_EVIDENCE_STATUS.md` | **NOT_ESTABLISHED.** Same evidence-recovery verdict covers this; only sensitivity/validation *research* on synthetic/candidate models exists, not an authorized empirical curve. |
| **DEC-TR-03** (Terminal Reserve unit) | `POLARIS_EMS_GAP19_EBR_TERMINAL_RESERVE_GOVERNANCE/FINAL_GOVERNANCE_DECISION_STATUS.md` | **Still `GOVERNANCE_DECISION_REQUIRED`.** No document records a stakeholder choice of unit; §2a's policy decisions settle *mechanism*, not unit. |
| **DEC-RES-03** (authorized numerical value/model) | Same, plus `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §6.3, `NUMERICAL_VALUE_STATUS_AUDIT.md` | **Still `GOVERNANCE_DECISION_REQUIRED`.** All candidate numbers remain explicitly marked `NOT_STAKEHOLDER_AUTHORIZED`; none were promoted. Gated on SD-07/SD-08, which are themselves unresolved. |
| **SD-13** (named sign-off authority) | `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §10.2, pending-requirements register | **Still `STATION_SPECIFIC_VALIDATION_REQUIRED`.** No document anywhere in the repository names an actual individual or body for any of the Technical Validator / Cross-functional Reviewer / Final Approver roles. |
| **Execution authorization** (this specific Stage 8.1-vs-baseline MILP simulation) | `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`, `...GOVERNANCE_STATUS.md` | **Still `NOT_AUTHORIZED`.** No document records an explicit authorization for this or any experiment; both documents' absolute governance boundaries remain in force. |

**Conclusion**: none of the six blockers can be legitimately resolved from evidence that
currently exists in this repository. This is not a gap in the search — it is the documented
state of the project (`FINAL_EVIDENCE_RECOVERY_VERDICT.md`'s own `HARD_STOP` and the
policy-resolution documents' `NOT_AUTHORIZED` boundaries agree on this independently).

**Per instruction, this is a STOP, not a workaround.** No fallback or test value
(`INITIAL_STATE`, the 100,000/160,000 Wh test-harness figures, the 35%/55–65% advisory
percentages) was substituted for any blocker. Named sign-off authority (SD-13) was not
confirmed because no such name exists in any document — it cannot be invented here.
Execution authorization for the Stage 8.1-vs-baseline MILP experiment was not obtained,
because obtaining it requires an actual human stakeholder decision that does not yet
exist in any record; no such authorization has been recorded, so the closed-loop MILP
experiment was **not run**, and neither model was touched.

**What would actually close this**: a human stakeholder (or delegated governance body)
would need to either (a) supply the missing station data (SD-07, SD-08) and empirically
derive DEC-TR-03/DEC-RES-03 from it, or (b) explicitly authorize a provisional
research-only value/model for DEC-RES-03 *as a stated exception*, together with naming
the SD-13 sign-off authority and explicitly authorizing `EXPERIMENT_EXECUTION` for this
specific simulation. None of that has happened in any document reviewed. This package
cannot manufacture that decision.
