# POLARIS Deadline Master Resolution

**Date:** 2026-10-17 | **Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Pass:** Sixth pass (one prior Master Decision Register + four prior remediation/audit reports preceded this one).
**Nature:** Read-only audit, bounded diagnostic testing, and consolidated decision-sheet preparation. **No protected file, model, config default, or `winner: null` state was edited.** No commit, stage, or push occurred. No sealed 2025 blind data was accessed.
**Relationship to the Master Decision Register:** `POLARIS_MASTER_DECISION_REGISTER.md/.json` are **untouched** (not edited) — this document sits alongside them, reclassifies all 33 of their items into the directive's 7-value disposition taxonomy, corrects one scope error found by fresh verification (RT-01), and adds the work completed and the single consolidated decision sheet the directive asked for.

---

## 1. Executive Status — What Is Actually Ready for Tomorrow

**Ready to present as a defensible, evidence-backed project state:**
- The safety-finding **computation and reporting pipeline** (reserve-shortfall, critical-unmet-load, hard-SOC, worker/master crash status) is implemented, wired into `evaluator.py` and `worker.py`, and **tested**: 51/51 tests pass in this pass's own run of `test_reserve_policy_guard.py`, `test_evaluator_safety_wiring.py`, `test_master_run_status.py`, `test_safety_gated_report.py` (command and output in §7).
- All 6 `PROTECTED_FILES` (per `system/orchestration/manifest.py`) are **byte-for-byte unchanged** across all six passes to date — independently re-hashed by this pass and matched exactly against the hashes recorded in `BOUNDED_CORRECTNESS_FIXES_REPORT.md` and `SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md`.
- `winner: null` is independently re-confirmed unchanged in `N6_OPERATIONAL_READINESS_REPORT.json:5`.
- Arm B's 34.82% diesel-saving figure is backed by a real, tested oracle/leakage blocklist (`system/evaluation/forecast_lineage.py::reject_if_oracle`, `is_oracle_provider`) that fails closed on `"realized_sw_in"` — independently re-confirmed with a fresh test run (23/23 pass). The figure is not usable as a causal operational claim and multiple existing governance-correction documents in the repository already carry that label forward.
- The project's central honest finding stands and is **not contradicted by anything found in this pass**: every safety computation is reporting-only; nothing today halts execution or changes dispatch behavior on an unsafe finding.

**Still not proven, and must not be claimed tomorrow:**
- **Live operational readiness.** `FOR-01`'s contradiction (one document says PASS on live MEPS-18Z/SITES arrival-time evidence, a same-day document in the same folder says 27/36 features `UNPROVEN` for exactly that evidence) is real and unresolved. Do not claim live-readiness; say "fixture/provider-timestamp-validated, live-arrival-time unproven" instead.
- **Real critical-load demand.** Every critical-load number in the EMS/diesel-reduction stack is self-labeled `SYNTHETIC_ENGINEERING_SCENARIO`; no measured Nuolja station critical-load figure exists (`EVID-02`).
- **A clean `test_offline_runtime.py` conservation suite.** This pass found **5** pre-existing, reproducible failures in that file, not the 3 named in the register and prior reports (correction below, §3 and §7). All 5 share one root-cause family traced into the protected `gap19_highs_native.py`'s curtailment accounting — this is a genuine, previously under-scoped finding and should be stated as such, not minimized.
- **Any safety enforcement with operational teeth.** No halt mechanism exists; none was invented in this pass; none should be claimed.
- **The full HiGHS/GAP19 regression suites.** Still not run to completion in any of the six passes (runtime cost); SHA-256 match is the only continuity evidence for GAP19 itself.

---

## 2. Correction to Prior Scope: RT-01 Is 5 Failing Tests, Not 3

The Master Decision Register (`RT-01`, citing `SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md:152`) and all four prior reports state **3** pre-existing failures in `system/tests/test_offline_runtime.py`: `test_flexible_load_constraints`, `test_flexible_load_no_double_counting`, `test_per_timestep_conservation_audit`.

Running the full file fresh in this pass (`python3 -m pytest system/tests/test_offline_runtime.py -q`) produces **5 failed, 30 passed**. The two previously unlisted failures are:
- `test_cumulative_physical_conservation_168h` — `unmet_critical_load_kwh` = 1029.98, expected 0.0
- `test_long_duration_closed_loop_endurance_168h` — `system_reliability_pct` = 81.48, expected 100.0

Both were re-run in isolation (not just inside the full-file run) and fail identically and deterministically — this is not test-order contamination or shared-fixture clobbering; both are independent, reproducible failures.

**Diagnostic root cause (read-only; no file was edited to investigate this):** all 5 failures trace to the same accounting surface. `gap19_highs_native.py:444` computes `renewable_curtailment` (`p_curt_tot`) inside the protected optimizer; the test assertions compare this field (and its downstream `unmet_load`/`system_reliability_pct` aggregates in `evaluator.py`) against the forecast bundle's reported solar/wind availability and find a reproducible imbalance (minimum observed: 5852.5 Wh at step 4 of a 12-step run; it compounds to 1029.98 kWh of "unmet critical load" and an 18.5-point reliability shortfall over a 168-hour endurance run). `evaluator.py` only sums fields GAP19 itself produces — it does not independently compute curtailment — so the discrepancy originates inside the **protected** `gap19_highs_native.py`, not in the unprotected evaluation/reporting layer.

**Classification impact:** this does not change RT-01's disposition (still `BLOCKED_BY_PREREQUISITE` — any real fix touches a protected file and needs the Batch-3 governance window), but it corrects the scope the owner is deciding about from "3 narrow test failures" to "5 failures in one root-cause family, worth the same protected-file review regardless." Treat this as the one substantive new finding from this pass.

---

## 3. Full Register — Disposition Table (all 33 items, reclassified into the directive's 7-value taxonomy)

Legend: **RWE**=RESOLVED_WITH_EVIDENCE · **SAFE**=SAFE_TO_EXECUTE_WITHIN_EXISTING_AUTHORITY · **OPR**=OWNER_PERMISSION_REQUIRED · **EXT**=EXTERNAL_DEPENDENCY · **BBP**=BLOCKED_BY_PREREQUISITE · **DWR**=DEFERRED_WITH_REASON · **N/A**=NOT_APPLICABLE_WITH_EVIDENCE

| ID | Title (short) | Disposition | Evidence / Blocker | Next action |
|---|---|---|---|---|
| SAF-01 | Safe-response action before halt | **OPR** | No handler exists anywhere in `system/safety`, `system/control`, `system/simulation` (grep-confirmed). | Owner decision sheet §5 Q1. |
| SAF-02 | Critical-unmet-load labeling (fallback vs. literal `UNKNOWN_NOT_VERIFIED`) | **OPR** | Current behavior (`FALLBACK_TO_TOTAL_UNMET_LOAD`) is implemented and disclosed; a defensible but non-literal reading. | Owner decision sheet §5 Q2. |
| SAF-03 | Numeric reserve-shortfall ceiling | **BBP** (needs EVID-03) | Both call sites pass `reserve_shortfall_authorization_wh=None`; no number exists anywhere. | Commission EVID-03 first. |
| SAF-04 | Max solar-credit fraction | **BBP** (needs EVID-03 for a number) / **OPR** (for posture now) | No production code computes a solar credit at all (`compute_bounded_solar_credit` unused outside the guard module). | Owner can decide "defer" today (§5 Q3); a number needs EVID-03. |
| SAF-05 | Formal authorization of 4 proposed safety gates | **BBP** (needs SAF-02 + EVID-03) | `SAFETY_GATE_REGISTRY` entries all `authorized=False`. | Resolve SAF-02 + EVID-03, then convene governance review. |
| SAF-06 | Halt/control-flow change in `runner.py`/`worker.py` | **BBP** (needs SAF-01) | No safe-response spec exists to authorize a halt against. | Resolve SAF-01, then governance review. |
| SAF-07 | "15 kWh EBR floor" provenance | **OPR** | Found only in `reserve_policy_guard.py`'s own docstring prose; not in any config or GAP19 file. Needs the owner's own records, not repo evidence. | Owner decision sheet §5 Q4. |
| SAF-08 | HiGHS timeout vs. infeasibility indistinguishable | **BBP** | Fix requires adding `time_limit` inside protected `gap19_highs_native.py:347-349`. | Bundle into the same protected-file window as SAF-06/RT-01 fix, if authorized. |
| SAF-09 | Guard zero-default bug | **RWE** | Independently re-confirmed this pass: `test_reserve_policy_guard.py` passes (part of the 51/51 run, §7). | Closed. Do not reopen without regression evidence. |
| SAF-10 | Worker/master crash-blind status | **RWE** | Independently re-confirmed this pass: `test_master_run_status.py` passes (7/7, part of the 51/51 run). | Closed. |
| FOR-01 | Contradictory N6 readiness verdicts (PASS vs. UNPROVEN) | **BBP** (needs EVID-01) | Two same-day documents in `candidate_n_additive_physics/` disagree; this and the prior pass side with the `UNPROVEN` (27/36) reading. | Commission EVID-01, or formally retract/relabel the PASS report as illustrative. |
| FOR-02 | Audit N6 usage outside `exp_three_arm_2024` | **DWR** | Attempted this pass; a quick grep for `n6_solar`/`stage8_1`/`candidate_n_additive_physics` returns false-positive-heavy noise (e.g. `stage8_1` substring-matches `stage8_10`–`stage8_19`) and cannot be trusted without a slower, string-exact pass. Not completed — reporting honestly rather than fabricating a result. | Needs ~30–60 min of careful, non-substring grep/AST work in a non-deadline session. |
| FOR-03 | Duplicate N6 hash-validation literals | **SAFE**, not executed | `n6_solar.py:56` and `polaris_inference_runner.py:28` are both outside `PROTECTED_FILES`; consolidation is low-risk, non-production-logic housekeeping. Deliberately **not executed** in this pass — editing forecasting-implementation files with zero slack before a deadline, for a non-blocking item both prior passes already declined to touch, is the wrong risk trade at T-minus-hours. | Safe to execute in the next calm session; no owner decision needed. |
| FOR-04 | Arm B oracle/leakage, 34.82% non-causal | **RWE** | Independently re-confirmed this pass: `forecast_lineage.py::is_oracle_provider`/`reject_if_oracle` blocklists `"realized_sw_in"`; `test_forecast_lineage_and_replay_harness.py` 23/23 pass. | Closed. |
| FOR-05 | No historical arm uses Stage 8.1/N6 | **RWE** | Carried forward from prior exhaustive grep (not independently re-run this pass; low-risk static claim). | Closed, pending no new evidence. |
| FOR-06 | Station-feedback research direction (Candidate F/L2/K) | **OPR** | Pure prioritization call. | Owner decision sheet §5 Q5. |
| FOR-07 | Sealed-2025-blind retention policy | **OPR** | No formal written policy exists yet; treated as sealed by convention only. | Owner decision sheet §5 Q6. |
| UNC-01 | Prefix Cumulative Energy Error Bound (PCEEB) | **SAFE** (spec/plan only — done this pass, §4) / **OPR** (implementation) | Spec prepared in §4 below, no code written, no experiment run. | Owner decides whether to authorize implementation (§5 Q7). |
| UNC-02 | Sensor/archive gaps block physical uncertainty envelope | **EXT** | No DNI/DHI decomposition sensor, truncated pre-2024 MEPS archive, uncalibrated diesel curve. | Acquisition plan, §6. |
| CL-01 | Critical-load design value (9.865 kW vs 11.6 kW) | **OPR** | Pure policy choice between a derived survival-core value and the already-used comfort-heating value. | Owner decision sheet §5 Q8. |
| DSL-01 | Diesel-reduction reliability threshold + Candidate 2 authorization | **BBP** (needs CL-01) | Threshold wording can be drafted now; formal preregistration needs CL-01 first. | Resolve CL-01, then governance preregistration. |
| DSL-02 | Diesel-savings attribution corrections | **RWE** | Carried forward from `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`'s disposition matrix; not independently re-derived this pass (statistical claim, out of this pass's re-verification list). | Closed. |
| DSL-03 | Candidate 1 (Solar Headroom) blocked | **RWE** | Same source. | Closed. |
| PRB-01 | Information Probe decision-rule closure/amendment | **OPR** | Register labels this "blocked," but the actual blocker is a missing *owner decision* (amend the hit-criterion, or close as inconclusive), not a missing artifact — reclassified accordingly. | Owner decision sheet §5 Q9. |
| RT-01 | 5 (not 3) pre-existing conservation-residual failures | Diagnostic: **RWE** (done this pass, §2/§7) · Fix: **BBP** | Root-caused to protected `gap19_highs_native.py` curtailment accounting. | Owner decides whether to authorize a protected-file fix (§5 Q10, scope-corrected). |
| RT-02 | Full HiGHS/GAP19 suites | **DWR** | `tests/test_gap19_highs_native.py`, `system/tests/test_gap19_ecd_option_d.py`, `system/tests/test_gap19_milp_v2_research.py` not run — ~48s/test × many tests exceeds this pass's bounded-test budget, consistent with all 5 prior passes. | Schedule a dedicated longer test session; not a deadline blocker (SHA-256 match is the standing continuity evidence). |
| RT-03 | Safety wiring advisory-only | **RWE** | Independently re-confirmed this pass via the 51/51 passing run and call-graph consistency with `SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` §2. | Closed (context item, not a to-do). |
| GOV-01 | `winner: null` unchanged | **RWE** | Independently re-grepped this pass: `"winner": null` confirmed at `N6_OPERATIONAL_READINESS_REPORT.json:5`. | Closed. |
| GOV-02 | Protected-file hash set unchanged | **RWE** | Independently re-hashed all 6 files this pass; exact match to `BOUNDED_CORRECTNESS_FIXES_REPORT.md` and `SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md` (§7). | Closed. |
| GOV-03 | N6/Candidate-N frozen artifact hashes verified | **RWE** | Carried forward (constants grep-confirmed to exist at the cited lines this pass; full artifact re-hash not repeated). | Closed. |
| EVID-01 | Live MEPS-18Z/SITES/Stage-3b arrival-time logging | **EXT** | Requires live telemetry daemons; explicitly out of scope (no network access performed). | Acquisition plan, §6. |
| EVID-02 | Real Nuolja critical-load measurement | **EXT** | Requires station instrumentation/circuit mapping. | Acquisition plan, §6. |
| EVID-03 | Numeric basis for reserve-shortfall ceiling/solar-credit cap | **DWR** | Commissionable now with existing historical data, no live access needed — but is itself a non-trivial empirical analysis task, not a quick lookup; no time to responsibly complete it before this deadline. | Pre-authorized to start immediately post-deadline; no further owner decision needed to *begin* it (per directive §2, bounded evidence-commissioning work is already authorized). |

**Headline counts, this pass:** RWE 13 (was 10 in the register; +SAF-09, SAF-10, FOR-04 moved from "resolved" to "independently re-confirmed" — no net new closures, same 10 items plus RT-03 reclassified from "context" to RWE for clarity) · SAFE 2 (FOR-03, UNC-01-spec) · OPR 9 · BBP 7 · EXT 3 · DWR 3 (FOR-02, RT-02, EVID-03). 33 items, all accounted for, none silently dropped.

---

## 4. PCEEB Research Specification and Offline Analysis Plan (prepared, not executed)

Per directive §2 item 6 — specification and plan only; **no code was written, no experiment was run, no model was fit.**

- **Problem:** `FORECAST_UNCERTAINTY_AUDIT.md` shows static `q10` is statistically fine but operationally excessive (+38% diesel, +93% curtailment), while pointwise relaxation is unsafe (+71–106% unmet load) because errors are autocorrelated intra-day (r=0.63–0.78) and inter-day (r=0.464). A **dynamic, horizon-indexed, cumulative** bound is the audit's own recommended next step.
- **Proposed method:** for each forecast issue time, compute a running (prefix) sum of realized-minus-forecast solar energy error over the lookahead horizon, and derive an empirical quantile envelope of that prefix-sum trajectory (not a per-hour quantile) from the existing historical forecast-vs-realized record already used by `FORECAST_UNCERTAINTY_AUDIT.md`. The EBR target would be relaxed by the *prefix* bound at horizon h, rather than by a flat per-hour q10.
- **Data needed:** already-available historical forecast/realized SW_IN pairs (no new sensor, no live access) — the same dataset the existing uncertainty audit used.
- **Deliverable if authorized:** a standalone offline notebook/script computing the prefix-cumulative error distribution and comparing its closed-loop-replay impact (diesel, curtailment, unmet-load) against both current baselines (static q10, pointwise relaxation), using the existing replay/evaluation tooling in read-only mode.
- **Explicitly out of scope even if authorized:** touching `gap19_highs_native.py`'s EBR formula itself, changing the production reserve-policy default, or running any live/sealed-data evaluation. Authorization of this spec authorizes *research-only, offline* implementation and testing — nothing else.

---

## 5. Consolidated Owner Decision Sheet (single sheet — every outstanding decision, not batched)

Each question: Register ID · exact choice · recommended default · consequence/risk per option · needed before tomorrow? · what a "yes" authorizes / does not authorize.

**Q1 — SAF-01: safe-response action before any safety-triggered halt.**
Choice: (a) forced minimum-diesel override, (b) operator-alarm-only (no automated action), (c) defer until a dedicated spec is written.
Recommended default: **(c) defer.** No halt mechanism can be built without this answer, and (a) requires inventing exactly the kind of forced-diesel-override behavior this task is barred from introducing on its own authority.
Risk: (a) changes control-flow behavior and needs its own full safety case; (b) is low-risk but leaves hard-SOC violations purely advisory; (c) costs nothing today but leaves SAF-06 permanently blocked.
Needed before tomorrow: No — nothing currently depends on this for the demonstration.
A "yes" to (a)/(b) authorizes: drafting a written safe-response spec only. It does NOT authorize editing `runner.py`/`worker.py` — that is SAF-06, a separate, later decision.

**Q2 — SAF-02: critical-unmet-load labeling.**
Choice: keep current `FALLBACK_TO_TOTAL_UNMET_LOAD` conservative over-count, or switch to the literal `UNKNOWN_NOT_VERIFIED` string.
Recommended default: **keep current.** Already implemented, tested, fully disclosed; switching is a reporting-string change with no functional benefit identified.
Risk: either choice is honest; switching costs engineering time to re-verify downstream consumers of the string.
Needed before tomorrow: No.
A "yes" authorizes: closing SAF-02 as-is. It does NOT authorize any change to `evaluator.py`/`worker.py` code — the current behavior already matches "keep current."

**Q3 — SAF-04: solar-credit cap posture.**
Choice: defer indefinitely, or authorize a provisional fraction now.
Recommended default: **defer.** Nothing in production computes a solar credit today; there is no live use for a cap.
Risk: deferring costs nothing; authorizing a number now without EVID-03 would be a numeric policy decision made without evidence.
Needed before tomorrow: No.
A "yes" to "defer" authorizes: nothing further right now. It does NOT authorize SAF-05 (gate authorization), which separately needs EVID-03.

**Q4 — SAF-07: "15 kWh EBR floor" provenance.**
Choice: confirm this is an owner-authorized figure from outside this repository, or confirm it is descriptive-only prose that the guard's docstring should be corrected to stop implying.
Recommended default: none possible from repository evidence — this needs the owner's own recollection/records.
Risk: if left ambiguous, future readers may treat the docstring prose as an authorized number when it is not.
Needed before tomorrow: No, but cheap to answer.
A "yes" (confirmed authorized) authorizes: citing it as a real figure elsewhere. A "no" (descriptive-only) authorizes: a documentation correction to the docstring (non-protected file, low risk, could be bundled with FOR-03).

**Q5 — FOR-06: station-feedback research direction (Candidate F/L2/K).**
Choice: pursue toward a future N6 successor, or park in favor of EVID-01.
Recommended default: **park.** EVID-01 blocks any candidate's production path regardless of this research's outcome.
Risk: parking delays a potentially useful signal; pursuing spends research time that EVID-01 could make moot.
Needed before tomorrow: No.
A "yes" (pursue) authorizes: continued offline research only — not training/promoting any model, which remains barred regardless.

**Q6 — FOR-07: sealed-2025-blind retention policy.**
Choice: formalize as permanently sealed, or define a specific future re-access trigger.
Recommended default: **formalize as permanently sealed** (current de facto convention across all 6 passes).
Risk: permanent sealing forecloses an easy future re-check; a trigger clause adds governance complexity now.
Needed before tomorrow: No.
A "yes" to either option authorizes: writing the policy document. It does NOT authorize opening or re-evaluating the sealed data itself under either option.

**Q7 — UNC-01: PCEEB implementation authorization.**
Choice: authorize the offline, research-only implementation and backtest of the PCEEB method specified in §4, or hold at spec-only.
Recommended default: **authorize** — the most concrete, evidence-backed next step in the uncertainty evidence base, and strictly offline/non-production per §4's explicit scope limits.
Risk: implementing costs research time; a flawed bound could mislead if later mistaken for production-ready (mitigated by its research-only labeling).
Needed before tomorrow: No.
A "yes" authorizes: exactly the offline notebook/script described in §4, using existing historical data. It does NOT authorize any change to `gap19_highs_native.py`'s EBR formula or any production default.

**Q8 — CL-01: critical-load design value.**
Choice: adopt the derived survival-core 9.865 kW, or retain the already-used comfort-heating 11.6 kW.
Recommended default: **retain 11.6 kW**, documented explicitly as the conservative choice (matches the register's own recommendation).
Risk: 9.865 kW would reduce reserve/diesel margins project-wide on an undocumented re-derivation; 11.6 kW is already embedded throughout the diesel-reduction design and changing it now would require re-auditing DSL-01/DSL-02 downstream math.
Needed before tomorrow: **Yes, if CL-01-dependent numbers will be presented tomorrow** — otherwise can wait.
A "yes" to either authorizes: documenting the chosen constant as authoritative. It does NOT authorize re-running any diesel-reduction candidate evaluation with the new value — that is separately gated by DSL-01.

**Q9 — PRB-01: Information Probe closure.**
Choice: approve an amended hit-criterion (e.g., 2-of-3) before any T1–T3 computation, or formally close the probe as inconclusive.
Recommended default: none possible from repository evidence — pure research-prioritization call, per the register's own assessment.
Risk: amending the criterion after seeing T4 was unavailable risks the appearance of post-hoc rule changes unless the amendment is logged and justified before any T1–T3 result is inspected (the freeze record's own rule); closing as inconclusive loses the signal but avoids that risk entirely.
Needed before tomorrow: No.
A "yes" (amend) authorizes: logging the amended rule, then computing T1–T3 under it — strictly in that order. It does NOT authorize inspecting T1–T3 before the amendment is formally logged.

**Q10 — RT-01: protected-file fix authorization (scope-corrected to 5 failing tests).**
Choice: authorize a protected-file-touching fix to `gap19_highs_native.py`'s curtailment-accounting discrepancy (root-caused in §2), or hold at diagnostic-only.
Recommended default: **hold at diagnostic-only for tomorrow; authorize the fix as the first item in the next protected-file governance window (Batch 3).** This is a real, reproducible 5-test failure family, not a minor residual — but a GAP19 edit the night before a deadline is exactly the kind of change this task's boundaries exist to prevent from happening without deliberate review.
Risk: holding leaves 5 known test failures open (already true today, so no new exposure); authorizing a same-night fix to the governed optimizer risks an unreviewed change to the exact file every dispatch decision depends on, under time pressure.
Needed before tomorrow: **No — and should not be rushed even if offered.**
A "yes" authorizes: a scoped `gap19_highs_native.py` edit limited to the curtailment-accounting discrepancy identified in §2, with a full before/after SHA-256 + full-suite re-run as part of that same authorized session. It does NOT authorize any other change to GAP19's formulation, objective priorities, or reserve policy.

**Linked, not separately listed:** SAF-05, SAF-06, SAF-03, SAF-08, DSL-01 all remain `BLOCKED_BY_PREREQUISITE` on the answers above (or on EVID-03) and are intentionally not asked as independent questions — asking them now would be asking the owner to approve a consequence before its cause is decided.

---

## 6. External Evidence Checklist

| Item | What's needed | Who/what |
|---|---|---|
| EVID-01 | Live MEPS-18Z THREDDS arrival-time logging + SITES/Stage-3b telemetry ingestion logs, captured contemporaneously (not reconstructed after the fact) | Requires standing up a logging daemon against `thredds.met.no` and the SITES telemetry feed over a real operational window; cannot be produced retroactively. |
| EVID-02 | Real Nuolja station critical-load measurement and circuit-level mapping (which loads are actually "critical") | Requires site access / station instrumentation data from the facility operator; not obtainable from any file in this repository. |
| UNC-02 | DNI/DHI sensor decomposition, un-truncated pre-2024 MEPS archive, calibrated diesel fuel curve | Requires additional sensor deployment, an archive-provider data request, and a bench/field diesel-generator calibration test. |

None of these three can be advanced by any further offline audit, re-reading, or re-analysis inside this repository — this is stated plainly rather than re-litigated.

---

## 7. Test Results and Protected-Artifact Integrity (this pass)

**Protected-file SHA-256 (independently recomputed this pass):**
```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  runner.py
```
**Exact match** to the values recorded in `BOUNDED_CORRECTNESS_FIXES_REPORT.md` §4 and `SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md` §6. No drift across any of the six passes.

`winner: null` — reconfirmed present at `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json:5`.

**Tests run this pass (bounded, non-network, non-campaign):**

| Command | Result |
|---|---|
| `python3 -m pytest system/tests/test_offline_runtime.py -q` | **5 failed, 30 passed** (see §2 — corrected from the previously-reported "3 failed") |
| `python3 -m pytest system/tests/test_reserve_policy_guard.py system/tests/test_evaluator_safety_wiring.py system/tests/test_master_run_status.py system/tests/test_safety_gated_report.py -q` | **51 passed** |
| `python3 -m pytest system/tests/test_forecast_lineage_and_replay_harness.py -q` | **23 passed** |
| Isolated re-run of each of the 2 newly-found `test_offline_runtime.py` failures | Both fail identically in isolation — not order-dependent |

**Tests explicitly NOT run, with reason (consistent with all 5 prior passes):**

| Suite | Reason not run |
|---|---|
| `tests/test_gap19_highs_native.py` | HiGHS-MILP-backed; ~48s/test, many tests — exceeds this pass's bounded-test time budget |
| `system/tests/test_gap19_ecd_option_d.py` | Same |
| `system/tests/test_gap19_milp_v2_research.py` | Same |
| `system/tests/test_n6_live_operational_execution.py` | Makes live network calls to `thredds.met.no` — explicitly prohibited outside an authorized live-access task (EVID-01) |
| Any dispatch campaign / historical replay / sealed-2025-blind evaluation | Explicitly prohibited by this task's protocol; `replay_harness.py` itself also raises `CampaignExecutionNotAuthorizedError` unconditionally |

**Git state:** `git status --short` shows only the pre-existing baseline (`POLARIS_MASTER_HANDOFF.md`, `requirements.txt` staged from before this pass began; ~1,000 pre-existing untracked research files). This pass's only filesystem changes are the two copies of this document. **No file was staged, committed, or pushed.**

---

## 8. Deadline Plan — Demonstration Readiness vs. Operational/Production Readiness

**Can present tomorrow as demonstration-ready, with correct caveats stated out loud:**
- The safety-finding computation/reporting pipeline, its test coverage, and the two real bugs it already caught and fixed in itself (SAF-09, SAF-10).
- The governance continuity story: `winner: null`, protected-file integrity, and the oracle/leakage safeguard on Arm B — all independently re-verified today, not merely re-asserted.
- A clear, honest statement of what is reporting-only vs. operationally consequential (nothing is operationally consequential yet), and why.
- This consolidated decision sheet, as the single next step for the owner, replacing any further sequential batches.

**Cannot be claimed as production- or operational-ready, and should be stated as such:**
- No live telemetry/arrival-time evidence (EVID-01) — do not claim operational readiness from fixtures or provider timestamps.
- No real critical-load measurement (EVID-02) — every diesel/critical-protection number is synthetic and labeled so.
- No safety enforcement with actual control-flow consequences — by design, pending SAF-01/SAF-06.
- `test_offline_runtime.py`'s 5-test conservation-residual family is open, root-caused to the protected optimizer, and deliberately not fixed tonight.
- The full HiGHS/GAP19 regression suites have never completed in any pass; hash-matching is the only continuity evidence for the optimizer itself.

**Immediate next action after the owner answers §5:** triage the answers into the same four-batch structure the register already established (foundational decisions → bounded evidence-commissioning, e.g. EVID-03 → the one protected-file governance window covering SAF-06/SAF-08/RT-01's fix together → the externally-dependent acquisition plan in §6), and execute Batch-1/2-equivalent bounded work immediately; do not reopen items already marked RWE without new evidence of regression.

---

## 9. Final Change Inventory

**Files created this pass:**
- `/home/punith-bs/01polaris (Copy)/POLARIS_DEADLINE_MASTER_RESOLUTION.md` (this file)
- `/home/punith-bs/01polaris (Copy)/N6_REMEDIATION_REPORTS/POLARIS_DEADLINE_MASTER_RESOLUTION.md` (identical copy)

**Files edited this pass:** none.

**Confirmed unchanged this pass:**
- All 6 `PROTECTED_FILES` (hash-verified, §7).
- `POLARIS_MASTER_DECISION_REGISTER.md` and `.json` (not opened for writing; read-only).
- `winner: null` governance state.
- All model artifacts, frozen bundles, and production configuration defaults.
- Git state: no `git add`, `git commit`, or `git push` was executed; repository remains on branch `master` with zero commits, exactly as found at session start.

**No model was trained, tuned, refit, recalibrated, or promoted. No dispatch campaign, historical replay, or full EMS evaluation was run. No sealed 2025 blind data was accessed. No safe-response/halt mechanism or numeric safety threshold was invented.**
