# N6 Annotation & Evidence Planning Report

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Nature of this pass:** Bounded planning and evidence pass only, per the project owner's directive. Continues from `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (v1.1.0) and `REGISTER_UPDATE_AND_RECONCILIATION_REPORT.md`. **No protected file was edited, no campaign/replay was run, no sealed data was accessed, no threshold was invented, and nothing was committed, staged, or pushed.**

---

## 1. N6 readiness — proposed annotation (PROPOSAL ONLY — not applied to the N6 report)

**Target file (not edited):** `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.md`, Section 6 ("Verification Verdict & Governance Invariants"), lines 96–105 — the unqualified gate block:

```
Gate 2: MEPS 18Z Data Arrival Margins       --> PASS (+3.86h to +4.00h Margin)
Gate 3: Telemetry Freshness & Streaming      --> PASS (Causal Lookback [t0-24, t0))
Gate 4: Live Operational End-to-End Run     --> PASS (Bundle Valid, GAP19 OPTIMAL)
```

**Why this is the target:** This report's own file is the one `POLARIS_MASTER_DECISION_REGISTER.md` (FOR-01, §1 "Executive Summary" and §5) identifies as directly contradicting its sibling document in the same folder, `operational_availability_audit/operational_causality_audit.md`, which concludes (its own closing summary): *"5 criteria PASS, 3 criteria UNPROVEN, 0 FAIL. A single UNPROVEN criterion prevents operational sign-off"* and separately that 27/36 N6 features are `UNPROVEN` for live operational causality — specifically because no contemporaneous ingestion/arrival-timestamp log exists for MEPS 18Z, SITES telemetry, or Stage 3b/4 execution (`operational_causality_audit.md` §4.3, governing-mandate quote: *"If the necessary publication or ingestion timestamps cannot be established, mark the affected feature UNPROVEN."*). `N6_REMEDIATION_REPORTS/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` (lines 49, 127) independently sides with the `UNPROVEN` verdict and states explicitly that live arrival-timestamp evidence "does not change that verdict."

**Proposed annotation text** (to be inserted as a new, clearly-marked block immediately after line 105, i.e. after the closing ``` of the gate table — not altering any existing line):

> ---
> **ANNOTATION ADDED 2026-10-17 (governance note — does not alter the gates or findings above):**
> Gates 2–4 above report successful *historical replay* of the data-arrival-margin calculation and a single offline end-to-end execution; they do **not** constitute live operational monitoring. A sibling audit in this same folder, `operational_availability_audit/operational_causality_audit.md`, concludes 27 of 36 Candidate N6 features are `UNPROVEN` for live operational causality, because no contemporaneous ingestion/arrival-timestamp log exists for MEPS 18Z, SITES Nuolja telemetry, or Stage 3b/4 execution latency. `N6_REMEDIATION_REPORTS/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` (lines 49, 127) and `POLARIS_MASTER_DECISION_REGISTER.md` (item **FOR-01**) independently concur with the `UNPROVEN` verdict. **Live operational readiness for Candidate N6 remains unverified pending EVID-01 (sustained live arrival-time logging, see `POLARIS_MASTER_DECISION_REGISTER.json` id `EVID-01`) and a formal FOR-01 resolution.** No live evidence has been collected for this annotation; this note adds no new data, changes no gate result, and does not alter `winner: null`.
> ---

**Scope boundary on this proposal:** This wording is a *recommendation* for the project owner or a separately authorized editing pass to apply. Per the directive ("record the PROPOSAL... rather than editing the N6 report itself unless the exact edit is clearly already within current authorization — it likely is NOT"), **this pass does not edit `N6_OPERATIONAL_READINESS_REPORT.md`.** The file is untouched; its gate table, hashes, and all findings are preserved exactly as written. This annotation makes no live-evidence claim of its own — it only cross-references evidence already in the repository (the `UNPROVEN` audit and the two prior reports that concur with it).

---

## 2. DSL-01 — epsilon_tol: candidate values, sources, consequences, missing evidence

**Direct search performed this pass:** `grep -rn "epsilon_tol" --include="*.md" --include="*.json" --include="*.py" .` (excluding `N6_REMEDIATION_REPORTS/` mirrors) and a review of `DIESEL_REDUCTION_CONTROL_DESIGN.md`, `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`, `DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md`.

**Finding: no numeric candidate value for `epsilon_tol` exists anywhere in the repository.** Every occurrence is a reference to the *need* to preregister it, never a proposed number:

- `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md` line 37: *"Preregistration Requirement for Safety Gate: Critical reliability acceptance threshold **REQUIRES PREREGISTRATION/GOVERNANCE BEFORE EXECUTION**. No safety guarantees are asserted."*
- `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md` line 77 (Final Status, Required Next Actions): *"1. Preregister the precise numerical critical reliability acceptance threshold ($\epsilon_{\mathrm{tol}}$) and governance decision rule. 2. Obtain explicit user/governance authorization for implementation of Candidate 2..."*
- `DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md` lines 62, 136–137: explicitly rejects the earlier "100% critical reliability" guarantee as `UNSUPPORTED` ("no uncertainty model; point forecasts only") and rejects the "−25% fuel, −20% curtailment" headline figures as acceptance criteria with "no basis given."
- `POLARIS_MASTER_DECISION_REGISTER.json` (DSL-01, lines 855–888) and `POLARIS_MASTER_DECISION_REGISTER.md` line 88 confirm the same: CL-01's dependency (critical-load constant, 11.6 kW provisional) is now resolved, but `epsilon_tol` itself remains an open owner decision, and the register explicitly declines to invent one ("this pass does not invent an epsilon_tol either").

**Preregistered diesel-reduction criteria that *do* exist (methodology, not threshold):**
- Evaluation population: the full **123-origin closed-loop campaign** (`EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`), not the 6 diagnostic origins used during design (`DIESEL_REDUCTION_CONTROL_DESIGN.md` line 153; `DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md` line 177/184 — 6 origins explicitly rejected as "too small for significance").
- Statistical test: paired Wilcoxon signed-rank, two-sided, with the significance level stated in `DIESEL_REDUCTION_CONTROL_DESIGN.md` line 205: *"Paired Wilcoxon signed-rank, two-sided p < 0.05 **AND** BCa 95% CI for mean fuel saving (Frozen B minus candidate, litres) strictly > 0."* (Note: the register's own DSL-01 description cites "p<0.01" in one place and `DIESEL_REDUCTION_CONTROL_DESIGN.md` itself states p<0.05 — this discrepancy was not reconciled in this pass and should be flagged to the owner as a secondary open question when `epsilon_tol` is preregistered.)
- Confidence interval method: Bias-Corrected and Accelerated (BCa) bootstrap, 95%, fixed seed (`DIESEL_REDUCTION_CONTROL_DESIGN.md` line 191).
- Safety comparison basis: critical reliability under both reporting conventions, and minimum observed SOC (`DIESEL_REDUCTION_CONTROL_DESIGN.md` line 193).

**Critical-reliability evaluation methodology:** `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`'s disposition matrix additionally mandates: exact research critical-load metrics replacing the legacy `reliability_pct` campaign metric (banned), removal of all arbitrary 0–10 scoring, and labeling the 123-origin set as a "pre-specified paired historical evaluation set, not a pristine holdout."

**Consequences of leaving `epsilon_tol` unset:** No diesel-reduction controller experiment — including Candidate 2 (Net-Deficit EBR, Variant S/SW) — may be executed even in research mode (`DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md` §3 Final Verdict: `RESEARCH_DESIGN_COMPLETE — AWAITING SAFETY-GATE PREREGISTRATION`). This is a governance gate, not a code gate: `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` (raised unconditionally by `execute_experiment_a`/`execute_experiment_b`, lines 254–262) would independently block execution even if `epsilon_tol` were set, since a separate campaign-execution authorization is also required.

**Missing evidence:** No document in scope proposes, computes, or derives a candidate numeric value for `epsilon_tol` from any dataset — this is a pure governance/risk-tolerance input, not an empirical derivation task like EVID-03. **This pass does not select or invent one.** DSL-01 remains `OWNER_DECISION_REQUIRED` and open.

---

## 3. SAF-03/SAF-05 — evidence needed, units, EBR/SOC policy, and the 15 kWh authority question

**Existing EBR/SOC policy definitions found (all verified, none modified):**
- Hard SOC floor: `system/config/battery.yaml`: `min_soc_pct: 20.0` → `min_e_wh = capacity_wh × 0.20 = 40,000 Wh` at default `capacity_wh = 200,000 Wh`. This is already enforced by GAP19's own variable bounds (`SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` §4) and is **not** itself a reserve-shortfall tolerance.
- EBR reserve *target* (not a ceiling): `gap19_highs_native.py:111–146`, `ebr_req_wh = (1.0/eta_dis) × w_crit_sum_wh`, a rolling 6-hour lookahead sum (module docstring `:9`); terminal reserve target `E_term_target` via `terminal_target_wh` or `terminal_reserve_model`. The slack `s_J2[t]` ("reserve_shortfall") absorbs any shortfall against `E_next[t] + s_J2[t] >= E_stage2_target[t] + min_e_wh` (`gap19_highs_native.py:298`).
- No file in `system/config/`, `system/safety/`, or `system/optimization/implementations/` defines a numeric **ceiling** on how much shortfall against that target is tolerable (`SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` §4, independently re-confirmed this pass by the same grep scope).

**The "15 kWh EBR floor" — unresolved authority (re-confirmed this pass, not newly resolved):**
- The only repository occurrence is prose in `system/safety/reserve_policy_guard.py`'s module docstring, line 14: *"...does NOT claim the existing 15 kWh EBR floor alone guarantees safety..."* — a disclaimer, not a definition or authorization.
- It is **not** hard-coded as a numeric constant in any `system/config/` file or in `gap19_highs_native.py`.
- A bounded repo-wide grep this pass (and in the prior reconciliation pass) for "EBR floor"/"15 kWh" additionally surfaced `POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/HD01_EBR_DEFINITION_AUDIT.md`, `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_HIERARCHY.md`, `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md`, and `POLARIS_EMS_IMPLEMENTATION_SPECIFICATION/POLARIS_EMS_IMPLEMENTATION_SPECIFICATION.md` — none of these authorizes "15 kWh" specifically.
- `HD01_EBR_DEFINITION_AUDIT.md` row **HD-01E** (line 228): *"EBR vs Tech Min — **OPEN** — Tech min = 20% (40 kWh); EBR floor > 20% — Confirm EBR target is strictly above 20% cell floor — Prevents Stage 2 tautological objective bug."* This is the audit's own record that the EBR-floor-vs-technical-minimum relationship is explicitly unresolved.
- Separately, `DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md` line 57 references a different, unrelated "25 kWh floor" in a Candidate 2 EBR-synthesis design note, explicitly stating "its value is not computed anywhere in the design" — this is a distinct, also-unauthorized figure and should not be conflated with the "15 kWh" guard docstring reference.
- **No owner-authorization record for either figure was found anywhere in this pass.** This matches and reconfirms SAF-07's existing decided status ("unverified, no provenance found") without reopening it.

**Evidence needed for EVID-03 (feeds SAF-03/SAF-04/SAF-05):**
Per `SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` §4 and `POLARIS_MASTER_DECISION_REGISTER.json` (EVID-03, lines 1286–1320), a defensible numeric basis requires specifying, before any ceiling is authorized:
1. **Units:** Wh vs. kWh (the guard already enforces Wh consistency via `validate_reserve_units_consistent`).
2. **Horizon:** per-step vs. cumulative-over-the-6h-EBR-window vs. cumulative-over-the-24h-terminal-target vs. cumulative-over-campaign.
3. **Scaling:** a fixed absolute Wh figure, or a percentage of the dynamically-computed EBR target.
4. **Margin:** whether the ceiling differs between the 6-hour EBR window and the 24-hour terminal target.
5. For SAF-04/SAF-05's solar-credit-cap and gate-threshold components: the same units/horizon basis, plus a bounded fraction for `compute_bounded_solar_credit`'s `authorized_max_credit_fraction` (currently has no caller anywhere in production — confirmed by grep, unused outside the guard module itself).

**Relevant role and method (not executed — EVID-03 is a planning item, see §4 below):** `POLARIS_MASTER_DECISION_REGISTER.json`'s own `recommended_default` for EVID-03 proposes an empirical analysis analogous to `FORECAST_UNCERTAINTY_AUDIT.md`'s methodology, using the already-existing `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` and the 2024 odd-origin fixture — explicitly as a bounded, offline, non-campaign research task. **This pass does not perform that analysis or propose a numeric result**, consistent with the directive's prohibition on inventing SAF-03's ceiling, SAF-05's authorization, or any related number.

---

## 4. EVID-01 / EVID-02 / EVID-03 — compact collection plans (plans only; no collection performed)

| Field | EVID-01 | EVID-02 | EVID-03 |
|---|---|---|---|
| **Evidence artifact** | Timestamped ingestion log: MEPS 18Z pressure-level publication times (THREDDS-polling daemon, 30 days); SITES Nuolja telemetry streaming log (zero-dropped-hour, 14 days); Stage 3b/4 execution-latency benchmark (10 consecutive dispatches) | Real, station-specific Nuolja critical-load measurement and circuit-level mapping (kW, per circuit) | A derived numeric basis report: candidate units/horizon/margin values for a reserve-shortfall ceiling (Wh) and a solar-credit fraction cap, with supporting empirical analysis |
| **Responsible role** | Infrastructure/ops engineer with live network access to `thredds.met.no` and SCADA/telemetry bridge access to Nuolja Middle Station (external to this audit's sandboxed scope) | Facility operator / NCPOR or station-instrumentation team with physical site access | Internal engineering (statistical/empirical derivation) + project owner (final risk-tolerance sign-off) |
| **Collection method** | Deploy the three daemons specified in `operational_availability_audit/remediation_plan.md` §2 (Blockers 1–3): a THREDDS-polling arrival-time logger for MEPS 18Z; a real-time SITES telemetry streaming bridge with dropped-hour accounting; a Stage 3b/4 latency benchmark harness run over 10 consecutive live dispatches | Install/read station-level or circuit-level metering at Nuolja Middle Station (or, for the ultimate SIH26061 target, Maitri/Bharati); document circuit-to-load mapping | Offline, read-only empirical analysis of the existing historical forecast-error dataset (`CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` + 2024 odd-origin fixture), using a methodology analogous to `FORECAST_UNCERTAINTY_AUDIT.md`'s own approach — no live telemetry, no new sensor, no campaign execution |
| **Acceptance criterion** | `remediation_plan.md`'s own stated Phase 1 (Ingestion Logging, 30/14/10-sample thresholds) and Phase 2 (Live Replay Audit) acceptance tests are met and independently audited | A real, attributable measurement with its own provenance/calibration record replaces each synthetic figure now labeled `SYNTHETIC_ENGINEERING_SCENARIO` / `REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED` | A report exists proposing specific units/horizon/margin values with supporting empirical analysis, explicitly scoped as research/evidence-only (no production default change), ready for owner risk-tolerance sign-off |
| **Dependency** | None (foundational); gates FOR-01's resolution and any future N6-successor operational sign-off | None (foundational); gates CL-01's ultimate (non-provisional) validation | None (foundational to SAF-03, SAF-04, SAF-05) |
| **Required permission** | Live network/hardware access authorization outside this offline/sandboxed task's scope (explicitly prohibited here); separate infrastructure-investment decision | Site-access / instrumentation authorization from the facility operator, outside this task's scope | No separate permission needed to *commission* the offline analysis itself; a separate owner/governance authorization **is** required before any resulting number is adopted into `reserve_policy_guard.py` call sites or SAF-05's gate registry |

**No live collection was performed for any of the three.** This section is a plan only, consistent with the directive's explicit prohibition on claiming live operational evidence was collected.

---

## 5. PCEEB — scope finding

**Specification source:** `POLARIS_DEADLINE_MASTER_RESOLUTION.md` §4 ("PCEEB Research Specification and Offline Analysis Plan"), mirrored at `N6_REMEDIATION_REPORTS/POLARIS_DEADLINE_MASTER_RESOLUTION.md` lines 88–98.

**Two-part scope, reviewed (not executed):**
- **Part (a) — in scope for a standalone offline implementation:** compute a running (prefix) sum of realized-minus-forecast solar energy error over the lookahead horizon, and derive an empirical quantile envelope of that prefix-sum trajectory from the already-existing historical forecast-vs-realized SW_IN record used by `FORECAST_UNCERTAINTY_AUDIT.md`. This is a pure, offline statistical computation — no new sensor, no live access, no model fit, no simulation, and it does **not** invoke `replay_harness.py`.
- **Part (b) — ambiguous / likely requires the disabled harness:** comparing the resulting bound's "closed-loop-replay impact (diesel, curtailment, unmet-load) against both current baselines... using the existing replay/evaluation tooling." The only replay/evaluation tooling identified in this repository for closed-loop dispatch-impact comparison is `system/evaluation/replay_harness.py`, whose `execute_experiment_a`/`execute_experiment_b` (lines 254, 261) unconditionally raise `CampaignExecutionNotAuthorizedError` (defined line 64; the error class itself and the module docstring, line 12, confirm both methods raise it unconditionally). This is the exact guard this task's boundaries explicitly forbid running or bypassing.

**Finding:** A standalone offline implementation of **part (a) alone** can be built and analyzed without invoking `replay_harness.py` at all, and would satisfy the "derive an empirical quantile envelope" portion of the PCEEB spec. **Part (b) cannot be satisfied without either the disabled harness or a from-scratch reimplementation of closed-loop replay logic outside it** — and a from-scratch reimplementation would itself constitute building new dispatch-campaign/replay capability, which is at minimum a scope question for the owner (does recreating replay-equivalent logic outside `replay_harness.py` count as "campaign execution" for authorization purposes?).

**Action taken this pass, per the directive's explicit instruction to stop at ambiguity:** No PCEEB code was written, no historical dataset was opened or analyzed, no script was run, and no replay or campaign execution was attempted. This matches and does not reopen the prior pass's own identical finding (`REGISTER_UPDATE_AND_RECONCILIATION_REPORT.md` §4; register §16) — re-verified from source this pass (`replay_harness.py` lines 64, 254–262 read directly) rather than merely re-asserted.

**Proposed clarification for the owner:** Confirm whether UNC-01's "offline, research-only" authorization is intended to cover *only* part (a) (prefix-quantile derivation) for now, with part (b) deferred to a separately-authorized campaign-execution decision — or whether the owner wants a *from-scratch, non-replay-harness* closed-loop comparison script scoped and reviewed as its own, separately authorized research task. This pass does not resolve that ambiguity; it is recorded here as open.

---

## 6. Register updates made this pass

**None.** No field in `POLARIS_MASTER_DECISION_REGISTER.md` or `.json` was edited in this pass. Rationale: every item this directive touches (N6/FOR-01, DSL-01, SAF-03, SAF-05, SAF-07, EVID-01/02/03, UNC-01/PCEEB) was already correctly and fully reconciled as of the prior pass (`REGISTER_UPDATE_AND_RECONCILIATION_REPORT.md`, same date). This pass's findings — the bounded `epsilon_tol` search returning no candidate value, the re-confirmed "15 kWh"/"25 kWh" provenance gap, the three EVID collection plans, and the PCEEB part (a)/(b) split — all **corroborate** the existing register entries verified from source (`POLARIS_MASTER_DECISION_REGISTER.json` DSL-01 lines 855–888, SAF-03 lines 172–207, SAF-05 lines 252–261+, EVID-01/02/03 lines 1214–1320) without surfacing any new evidence that would change a `current_state`, `disposition_2026_10_17`, or `owner_decision_record` value. Per this pass's own boundary ("update statuses only where direct existing evidence supports the change"), making a cosmetic edit that only restates already-recorded findings was judged not evidence-supported as a *status change* and was skipped to avoid unnecessary churn on a file the owner is actively using. The one substantive new output — the proposed N6-report annotation wording (§1) and the PCEEB scope clarification question (§5) — are recorded in this standalone report instead, per the directive's explicit instruction.

**Open items unchanged and still open:** DSL-01 (`epsilon_tol`, `OWNER_DECISION_REQUIRED`), SAF-03/SAF-05/SAF-06 (`BLOCKED_BY_AUTHORIZATION`), EVID-01/EVID-02 (`EXTERNAL_EVIDENCE_REQUIRED`), EVID-03 (`ENGINEERING_WORK_REQUIRED`, not commissioned), FOR-01 (`EXTERNAL_EVIDENCE_REQUIRED`, plus the standing, separate "retract/annotate the PASS report now" option this pass's §1 proposal addresses).

---

## 7. Boundary confirmation

- No `PROTECTED_FILES` entry (`gap19_highs_native.py`, `option_d.py`, `ecd.py`, `router.py`, `simulator.py`, `runner.py`) was read for modification or edited; `manifest.py`'s list was only grepped for citation (lines 10–17).
- `system/evaluation/replay_harness.py` was read (lines 12, 51, 64, 68, 72, 254–262) for citation only; its `CampaignExecutionNotAuthorizedError` guard was not edited, bypassed, or run.
- No sealed 2025 blind data was accessed; no dispatch campaign, replay, or live-network call was executed.
- No production formula or default (GAP19 EBR/terminal formulation, reserve policy, solar-credit logic, control flow) was changed.
- No numeric threshold was selected or invented for `epsilon_tol` (DSL-01), the reserve-shortfall ceiling (SAF-03), the solar-credit cap (SAF-04), or any safety-gate authorization (SAF-05) — §2 and §3 above report only what candidate values and methodologies already exist in the repository (finding: none numeric exist for `epsilon_tol`; none authorized exist for the reserve-shortfall ceiling), not a new proposal.
- No claim is made that live operational evidence was collected for EVID-01/02/03 — §4 is a collection plan only.
- `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` were read but not edited (§6).
- Nothing was committed, staged, or pushed. `git status` was not re-run destructively; only read operations (`grep`, `sed`, file reads) and this new report file were produced.
- Files created this pass: this report (`N6_ANNOTATION_AND_EVIDENCE_PLANNING_REPORT.md`, root) and its mirror into `N6_REMEDIATION_REPORTS/`. No other file was created, edited, staged, or committed.

---

**BOUNDED PLANNING AND EVIDENCE PASS COMPLETE — NO BOUNDARY CROSSED**
