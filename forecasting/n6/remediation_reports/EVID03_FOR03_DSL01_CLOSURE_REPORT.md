# EVID-03 Evidence Analysis, FOR-03 Hash Consolidation, DSL-01/FOR-01 Owner Notes & Register Closure — Implementation Report

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Nature of this pass:** Mixed implementation + offline-analysis + documentation pass, continuing from `PCEEB_DSL01_N6ANNOTATION_REGISTER_CLOSURE_REPORT.md` and `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (v1.2.0 → v1.3.0). Performs the project owner's explicitly commissioned EVID-03 analysis and authorized FOR-03 hash consolidation for real, adds owner-facing decision documentation for DSL-01 and FOR-01, and sweeps the register for independently closeable items. **No protected file was edited, no campaign/replay was run, no sealed data was accessed, no safety threshold was invented or adopted, and nothing was staged, committed, or pushed.**

---

## 1. EVID-03 — offline reserve-margin units/horizon/margin evidence analysis

**Authorization:** Project owner, this pass, directive item 1 — *"I commission the bounded, offline, research-only EVID-03 analysis described in the register."*

**Scope inspected before writing any code (per the directive's own instruction):**
- `POLARIS_MASTER_DECISION_REGISTER.json` item `EVID-03`: a shared evidence task feeding `SAF-03` (reserve-shortfall ceiling), `SAF-04` (solar-credit cap), and `SAF-05` (formal gate authorization). Its own `closure_test`: *"A report exists proposing specific units/horizon/margin values with supporting empirical analysis, ready for owner risk-tolerance sign-off."* Its own `proposed_options` Option 1 (the one exercised): *"Commission an empirical analysis analogous to FORECAST_UNCERTAINTY_AUDIT.md's methodology, deriving a candidate reserve-shortfall distribution from the existing historical forecast-error dataset."*
- `N6_REMEDIATION_REPORTS/SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` Section 4: the exact units/horizon/margin dimensions needing evidence — *"Wh vs. kWh; per-step vs. cumulative-over-horizon vs. cumulative-over-campaign; whether the ceiling scales with the EBR target (a percentage) or is a fixed absolute Wh figure; whether it differs for the 6-hour EBR window vs. the 24h terminal target."*
- Permitted datasets confirmed: identical to PCEEB Part (a)'s own two non-sealed historical CSVs (2020–2024 data only; the primary file's "BLIND_TEST_2023" split is a 2023 in-sample holdout, not the sealed 2025 blind partition).
- GAP19's own horizon/units facts, confirmed by a **read-only** inspection of `system/optimization/implementations/gap19_highs_native.py` (a `PROTECTED_FILES` entry — read, never edited, in this or any pass) and `system/safety/reserve_policy_guard.py` (not protected, read only): the EBR target is a genuine 6-hour rolling lookahead sum (`E_EBR_target[t]`, lines ~111–131); the terminal target applies only at the final step (`E_term_target`, lines ~133–151); the guard's own `reserve_shortfall_total_wh = sum(plan["reserve_shortfall"])` (lines 308–311) is already an ad-hoc "cumulative-over-one-24h-horizon" choice, never owner-validated as the correct basis.

**Location:** `research/evid03_reserve_margin_analysis/` (new, isolated directory, mirrors the `research/pceeb_part_a_offline/` pattern)
- `compute_evid03_reserve_margin_analysis.py` — stdlib-only implementation (no third-party dependency)
- `test_evid03_reserve_margin_analysis.py` — 14 focused unit tests
- `README.md` — spec, methodology, results summary, limitations, reproduction steps
- `outputs/evid03_reserve_margin_evidence.json`, `outputs/HASHES.txt`

**Inputs (identical to, and hash-matched against, PCEEB Part (a)'s own inputs):**

| Dataset | Path | Origins | SHA-256 |
|---|---|---|---|
| Primary | `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | 1,369 | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` |
| Secondary (corroboration) | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | 173 | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` |

Both re-verified this pass and confirmed **identical** to PCEEB Part (a)'s own recorded hashes (`pceeb_recorded_input_sha256_matches: true` for both datasets in the output JSON) — i.e., no drift in the underlying dataset between the two passes.

**Method, in one paragraph:** GAP19 defines two reserve-target horizon bases: a 6-hour rolling EBR window and a full-horizon/terminal target at the final step. This script re-expresses PCEEB Part (a)'s already-computed prefix-cumulative solar-forecast-error quantile envelope at exactly those two lookahead-step ranks (step 6; and the dataset's final step — 19 for primary, 24 for secondary), converts the irradiance-error quantiles (Wh/m²) into generation-energy-equivalent Wh via the existing `K_PV = 51.0 W/(W/m²)` constant (already hard-coded identically in `n6_solar.py` and `polaris_inference_runner.py`), and expresses the result both in absolute Wh and as a percentage of two existing reference constants: `EBR_BASE_WH = 15,000 Wh` and the default hard-SOC-floor `min_e_wh = 40,000 Wh`. It additionally computes a new descriptive statistic — the empirical rate and magnitude of "forecast-overestimate" events (cumulative realized irradiance below cumulative predicted) at the same two horizon bases — as the direct empirical analogue of the risk a solar-credit cap exists to bound.

**Methodological choices documented, not silently invented** (full detail in the script's module docstring, items E1–E5 and M1/M2/M4/M5): horizon-basis citation from GAP19 source; existing-guard-formula citation; linear K_PV units conversion (no inverter-clip nonlinearity applied); reference-scale choice (EBR_BASE_WH, hard-SOC-floor — both existing, not invented); overestimate-event definition; sign convention, horizon indexing (lookahead-step rank, not raw `horizon_hour`, per the register's own `GAP-INDX-03` gap), missing-data rule, and quantile estimator — all identical to PCEEB Part (a)'s own already-authorized choices.

**Focused test results:**
```
$ cd research/evid03_reserve_margin_analysis && python3 -m unittest test_evid03_reserve_margin_analysis -v
Ran 14 tests in 0.002s
OK
```

**Script run result:**
```
$ python3 compute_evid03_reserve_margin_analysis.py
Primary dataset:   6h-window step=6, terminal step=19
Secondary dataset: 6h-window step=6, terminal step=24
PCEEB input hash match (primary):   True
PCEEB input hash match (secondary): True
```

**Key empirical finding (primary dataset, 1,369 origins, generation-energy-equivalent, 5th-percentile adverse tail):**

| Horizon basis | q05 (Wh) | as % of EBR_BASE_WH (15,000 Wh) | as % of hard SOC floor (40,000 Wh) |
|---|---|---|---|
| 6h rolling EBR window | −21,961 Wh | −146.4% | −54.9% |
| Full horizon / terminal | −89,327 Wh | −595.5% | −223.3% |

**Overestimate-event rate (solar-credit risk proxy), primary dataset:** 39.0% of origins (6h basis), 54.9% of origins (full-horizon basis). Median overestimate magnitude: 6,810 Wh (45.4% of EBR_BASE_WH) at 6h; 29,376 Wh (195.8% of EBR_BASE_WH) at full horizon. Full figures, both datasets, both bases, all seven quantile levels: `research/evid03_reserve_margin_analysis/outputs/evid03_reserve_margin_evidence.json`.

**What this evidence shows, stated as empirical fact only:** at both horizon bases, the 5th-percentile adverse-tail solar-forecast-error magnitude already exceeds the existing `EBR_BASE_WH` reference constant, and at the full-horizon basis it exceeds even the default hard-SOC-floor. **This is not a recommendation for any specific ceiling or cap value.** No numeric reserve-shortfall ceiling, solar-credit cap fraction, or safety-gate threshold was selected, proposed, recommended, or adopted anywhere in this analysis — every number is reported as a labeled historical descriptive statistic for the owner's own risk-tolerance judgment.

**Limitations documented (not extrapolated past):** (1) solar-only proxy — does not model wind/demand/battery-SOC-trajectory/joint-MILP-objective interaction; a full measurement needs Part (b)-style replay, **not performed**; (2) linear K_PV scaling ignores the inverter-ceiling nonlinearity; (3) neither dataset carries ensemble/uncertainty spread, so N6's own conformal lower-bound coverage is **cited** from `FORECAST_UNCERTAINTY_AUDIT.md`, not recomputed; (4) not Nuolja-station-specific critical-load data (EVID-02 unchanged); (5) `EBR_BASE_WH`'s own provenance remains unverified (SAF-07's "unverified, no provenance found" disposition is unchanged and reiterated, not escalated).

**Register update:** `EVID-03.current_state`: `pending` → `resolved_with_evidence`; `disposition_2026_10_17.disposition`: `ENGINEERING_WORK_REQUIRED` → `RESOLVED_WITH_EVIDENCE` — **for the evidence-gathering task itself only.** `SAF-03`, `SAF-04`, `SAF-05` are explicitly **not** resolved by this; each still requires a separate owner/governance decision (see Section 5).

---

## 2. FOR-03 — bounded hash-constant consolidation

**Authorization:** Project owner, this pass, directive item 2 — narrowly scoped consolidation of the two hand-maintained SHA256 literals.

**Before editing — exact definitions and every consumer identified:**
- `system/forecasting/implementations/n6_solar.py:56` — `FROZEN_MODEL_SHA256 = "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197"`.
- `stage7/.../artifacts/polaris_inference_runner.py:28` — `EXPECTED_SHA256 = "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197"` (identical value).
- Consumers enumerated by repo-wide grep: `n6_solar.FROZEN_MODEL_SHA256` is imported by `system/tests/test_n6_forecast_engine.py`, `test_n6_decomposition_parity.py`, `test_n6_live_operational_execution.py` (not run — live network), and `stage7/.../n6_operational_pipeline.py`. `polaris_inference_runner.EXPECTED_SHA256` is imported by `test_inference_runner.py` and `test_n6_gap19_integration.py`. **Confirmed distinct** from several *other*, differently-named/differently-valued `FROZEN_MODEL_SHA256`/`EXPECTED_SHA256` constants elsewhere in the repository that govern unrelated models (Stage 8.1 corrected: `64ea4ab...`; Branch01: `65c04d6...`) or unrelated CSV-treatment-file checks (`run_polaris_stage8_1_ems_*.py`'s own `EXPECTED_SHA256 = "a4d288f9..."`, which is the *dataset* hash, not a model hash) — FOR-03's scope is specifically the two N6-model copies, not every generically-named constant sharing that name.

**Canonical source confirmed unambiguous:** `stage7/.../artifacts/CANDIDATE_N_MANIFEST.json`, field `models.candidate_n6.sha256 = b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197`. This manifest already existed (generated `2026-10-17T01:50:42Z`, alongside the frozen artifacts) and already equaled both hand-maintained literals **and** the on-disk artifact's own independently recomputed `sha256sum` before any edit was made this pass:
```
$ sha256sum stage7/.../artifacts/candidate_n6_model.joblib
b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197  candidate_n6_model.joblib
```

**Minimum change implemented:** both files now define a small `_load_frozen_model_sha256_from_manifest()` helper that reads `models.candidate_n6.sha256` from the manifest JSON, and assign the module-level constant from it **once, at import time** — replacing the hard-coded literal, preserving the exact same name, type (`str`), and value for every existing consumer. No other code, feature, formula, or control flow in either file was touched. No model artifact, feature order, hyperparameter, or inference behavior was changed.

**Focused parity/regression tests:**
```
Baseline (before edit):  24/24 pass
  test_inference_runner.py ............... 9/9
  test_n6_forecast_engine.py .............. 9/9
  test_n6_decomposition_parity.py ......... 6/6

After edit:               24/24 pass, identical results (same test names, same assertions)
```
Direct import check this pass (not a unit test, a verification script) confirmed:
```
EXPECTED_SHA256      = b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197
FROZEN_MODEL_SHA256  = b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197
OK: both constants equal pre-edit literal and each other
```

**Register update:** `FOR-03.current_state`: `pending` → `resolved_with_evidence`; `disposition_2026_10_17.disposition`: `ENGINEERING_WORK_REQUIRED` → `RESOLVED_WITH_EVIDENCE`.

---

## 3. DSL-01 — owner decision note (epsilon_tol); nothing selected

Per directive item 3, a concise owner decision note was added to the JSON register (`DSL-01.owner_decision_note_2026_10_17`), covering exactly the five things requested:

1. **What the threshold controls:** DSL-01's own preregistered critical-reliability *acceptance* threshold for Candidate 2's 123-origin research evaluation — distinct from the already-traced p<0.05 (DSL-01's own test) vs. p<0.01 (SAF-05's separate, unauthorized production gate) significance question, and distinct from SAF-03/SAF-04's EBR-level quantities.
2. **Existing reliability metrics/methodology:** `DIESEL_REDUCTION_CONTROL_DESIGN.md`'s preregistered protocol (paired Wilcoxon p<0.05, 95% BCa CI > 0, 123 origins, CL-01's 11,600 W value) — no `epsilon_tol` is defined anywhere in it or any other repository document.
3. **Evidence needed to compare candidate thresholds:** a replay-measured degradation distribution (gated behind a separate execution authorization, not performed), a real Nuolja critical-load baseline (EVID-02, not established), and the owner's own irreducible risk-tolerance judgment.
4. **Consequences of leaving it unset:** Candidate 2 stays unexecuted (per `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`'s own "AWAITING SAFETY-GATE PREREGISTRATION" verdict); this creates no safety risk by itself, only a research-progress block.
5. **No numeric candidate supported by current evidence:** confirmed, consistent with the prior pass's own finding.

**No value was selected, invented, or recommended.** `DSL-01`'s disposition remains `OWNER_DECISION_REQUIRED`, unchanged from the prior pass.

---

## 4. FOR-01 — exact closure-evidence checklist; not resolved

Per directive item 4, a five-step checklist was added to the JSON register (`FOR-01.disposition_2026_10_17.closure_evidence_checklist_2026_10_17`), explicitly linked to EVID-01's own named acceptance tests from `remediation_plan.md`:

1. EVID-01's evidence collected to spec (30 consecutive days MEPS 18Z ingestion logging; 14 consecutive days zero-dropped-hour SITES telemetry; 10 consecutive Stage 3b latency benchmarks).
2. A reconciliation pass re-deriving `N6_OPERATIONAL_READINESS_REPORT.md`'s Gate 2 margin figures from those genuine logs (not the report's current, unverified THREDDS-query claim).
3. The same reconciliation performed feature-by-feature against `operational_causality_audit.md`'s 27/36 UNPROVEN list.
4. A decision on retracting/amending/confirming the Gate 2–4 PASS claims, superseding the lighter annotation already applied in the prior pass (Section 19.3).
5. Formal governance sign-off closing FOR-01, naming the approving authority and date.

Step 1 explicitly **cannot** be performed in this or any offline/sandboxed session. **FOR-01 is not claimed closer to resolution** by this checklist's existence; its disposition remains `EXTERNAL_EVIDENCE_REQUIRED`.

---

## 5. Remaining-register closure sweep

**SAF-03 reclassified** `BLOCKED_BY_AUTHORIZATION` → `OWNER_DECISION_REQUIRED`: its named dependency (`EVID-03`) is now satisfied by Section 1's completed evidence task. This is a status upgrade reflecting that the prerequisite evidence now exists — **no numeric ceiling was selected or invented**; the item simply moved from "blocked on missing evidence" to "ready for the owner's own risk-tolerance input."

**SAF-05 text updated, disposition unchanged** (`BLOCKED_BY_AUTHORIZATION`): both named prerequisites (`SAF-02`, decided in the prior-prior pass; `EVID-03`, completed this pass) are now satisfied, but SAF-05 itself requires a **formal governance-authority review** (`decision_authority: "governance authority"`), not a single owner risk-tolerance call — so it stays in the authorization-blocked bucket, with its text corrected to state that no repository-internal blocker remains.

**Items inspected and left unchanged, with reasons:**
- `SAF-08` (HiGHS `time_limit` fix) — `ENGINEERING_WORK_REQUIRED`, unchanged; requires bundling into a future protected-file (`gap19_highs_native.py`) governance window, out of this pass's scope (no protected-file edit authorized).
- `RT-02` (full HiGHS/GAP19 suite) — `ENGINEERING_WORK_REQUIRED`, unchanged; requires a long-running test session this pass's bounded-testing instruction explicitly does not permit.
- `SAF-06` — `BLOCKED_BY_AUTHORIZATION`, unchanged; its prerequisite `SAF-01` was decided "defer," so no safe-response spec exists to authorize a halt against.
- `FOR-01`, `UNC-02`, `EVID-01`, `EVID-02` — `EXTERNAL_EVIDENCE_REQUIRED`, unchanged; no in-repository evidence is possible for any of these (live network/hardware/site access, all explicitly out of scope).
- All 10 `ALREADY_RESOLVED` items (`SAF-09`, `SAF-10`, `FOR-04`, `FOR-05`, `DSL-02`, `DSL-03`, `RT-03`, `GOV-01`, `GOV-02`, `GOV-03`) — not re-litigated, per every prior pass's own standing instruction not to reopen these without new evidence of regression. None was found.
- All 10 owner-decided items from Section 14 (`SAF-01`, `SAF-02`, `SAF-04`, `SAF-07`, `FOR-06`, `FOR-07`, `UNC-01`, `CL-01`, `PRB-01`, `RT-01`) — unchanged, except `UNC-01` which already carries its Part (a)/Part (b) split from the prior pass (unaffected by this one).

**A tally bug from the prior pass was also corrected this pass** (not a re-litigation of any item's own status): `POLARIS_MASTER_DECISION_REGISTER.json`'s `headline_counts.amendment_2026_10_17.disposition_tally` still showed `FOR-02` counted under `ENGINEERING_WORK_REQUIRED` (5) with `RESOLVED_WITH_EVIDENCE` at 0, even though `FOR-02`'s own item record had already been updated to `resolved_with_evidence`/`RESOLVED_WITH_EVIDENCE` in that same prior pass. The aggregate tally (not `FOR-02` itself, which was correct) is corrected this pass; see JSON field `disposition_tally_note_2026_10_17`.

---

## 6. Verification, register maintenance, and final status

**Register files updated:** `POLARIS_MASTER_DECISION_REGISTER.md` (version bumped via new Section 20; table rows and Section 15 detail rows updated for `FOR-03`, `EVID-03`, `SAF-03`, `SAF-05`, `DSL-01`, `FOR-01`) and `POLARIS_MASTER_DECISION_REGISTER.json` (`1.2.0` → `1.3.0`; `FOR-03`/`EVID-03.current_state` → `resolved_with_evidence`; `SAF-03.disposition_2026_10_17.disposition` → `OWNER_DECISION_REQUIRED`; `SAF-05` text updated; `DSL-01.owner_decision_note_2026_10_17` and `FOR-01...closure_evidence_checklist_2026_10_17` added; `FOR-03.hash_consolidation_2026_10_17` and `EVID-03.evid03_analysis_2026_10_17` evidence blocks added; `headline_counts.amendment_2026_10_17.disposition_tally` corrected). Validated as well-formed JSON with exactly 33 items, both before and after edits. Both files mirrored byte-for-byte into `N6_REMEDIATION_REPORTS/` (confirmed via `diff -q`, no differences).

**Protected-file integrity (re-verified this pass via `sha256sum`, exact match to every prior pass, all 8 passes to date):**
```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  runner.py
```
`winner: null` re-confirmed at `N6_OPERATIONAL_READINESS_REPORT.json:5` (untouched by this pass). `candidate_n6_model.joblib` re-confirmed unchanged (`sha256sum` matches the manifest and both consuming files' now-manifest-derived constant).

**Tests run this pass:**
- 14/14 focused unit tests, EVID-03 (`research/evid03_reserve_margin_analysis/test_evid03_reserve_margin_analysis.py`), 0.002s.
- 24/24 focused regression tests, FOR-03, run twice (baseline before edit, confirmation after edit): `test_inference_runner.py` (9), `test_n6_forecast_engine.py` (9), `test_n6_decomposition_parity.py` (6).
- No broad suite, no HiGHS/GAP19 regression suite (`test_n6_gap19_integration.py` was inspected but deliberately **not** run this pass — it exercises the full GAP19 optimizer + simulator step and was judged outside this pass's "focused tests for the specific changes you make" instruction, since FOR-03's change touches only the hash-constant definition, not GAP19 or simulation code), no replay, no campaign, and no live-network test was run.

**Files created/edited this pass (exact paths, repo-relative):**
- Created: `research/evid03_reserve_margin_analysis/compute_evid03_reserve_margin_analysis.py`, `test_evid03_reserve_margin_analysis.py`, `README.md`, `outputs/evid03_reserve_margin_evidence.json`, `outputs/HASHES.txt`
- Edited: `system/forecasting/implementations/n6_solar.py` (hash-literal consolidation, value unchanged), `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/polaris_inference_runner.py` (same), `POLARIS_MASTER_DECISION_REGISTER.md`, `POLARIS_MASTER_DECISION_REGISTER.json`, `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md`, `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.json`
- Created (this report): `EVID03_FOR03_DSL01_CLOSURE_REPORT.md` (root), mirrored to `N6_REMEDIATION_REPORTS/EVID03_FOR03_DSL01_CLOSURE_REPORT.md`

**Nothing was staged, committed, or pushed.** `git status` confirms all of the above remain untracked (`??`) in this no-commits repository.

### Remaining counts by register status (33 total, unchanged)

| Bucket | Count | IDs |
|---|---|---|
| Owner-decided, fully complete (Section 14) | 9 | SAF-01, SAF-02, SAF-04, SAF-07, FOR-06, FOR-07, CL-01, PRB-01, RT-01 |
| Owner-decided, partially complete | 1 | UNC-01 (Part (a) done; Part (b) separately gated) |
| ALREADY_RESOLVED | 10 | SAF-09, SAF-10, FOR-04, FOR-05, DSL-02, DSL-03, RT-03, GOV-01, GOV-02, GOV-03 |
| **RESOLVED_WITH_EVIDENCE** | **3** | FOR-02, FOR-03, EVID-03 |
| ENGINEERING_WORK_REQUIRED | 2 | SAF-08, RT-02 |
| EXTERNAL_EVIDENCE_REQUIRED (blocked, cannot advance in-repo) | 4 | FOR-01, UNC-02, EVID-01, EVID-02 |
| BLOCKED_BY_AUTHORIZATION (governance/protected-file review needed) | 2 | SAF-05, SAF-06 |
| **OWNER_DECISION_REQUIRED** | **2** | DSL-01, SAF-03 |

`9 + 1 + 10 + 3 + 2 + 4 + 2 + 2 = 33` ✓

### Decisions that genuinely still require the owner (or external authority)

1. **SAF-03 — numeric reserve-shortfall ceiling.** Newly ready: `research/evid03_reserve_margin_analysis/outputs/evid03_reserve_margin_evidence.json` supplies the units/horizon/margin evidence; the owner must still state a specific figure (or decline to). No candidate is recommended by this pass.
2. **DSL-01 — epsilon_tol**, and the narrow significance-criterion question (two distinct p-value criteria, or one unified value — see the prior pass's trace). No value selected.
3. **SAF-05 — formal governance authorization** of the four `SAFETY_GATE_REGISTRY` gates. Both prerequisites are now satisfied; needs a governance review to convene, informed by SAF-03's eventual resolution.
4. **SAF-04 — solar-credit cap value**, if the owner wishes to revisit the existing "defer" posture using the new EVID-03 evidence.
5. **FOR-01 — retract vs. annotate fully.** The lighter annotation stands; the owner may decide whether a fuller retraction is warranted ahead of EVID-01, independent of this pass.
6. **EVID-01 / EVID-02 / UNC-02 — resourcing/infrastructure decisions** (live telemetry daemons, station instrumentation, sensor/archive gaps) — outside any audit's ability to settle; a budget/access owner must decide.
7. **SAF-06** — stays blocked until the owner separately commissions a safe-response spec (SAF-01 was decided "defer"); no action possible until that choice is revisited.
8. **RT-02 / SAF-08** — scheduling/bundling decisions for a future protected-file-adjacent engineering window; not time-critical.

### Highest-value next actions, ordered

1. **Owner reviews the EVID-03 evidence and states SAF-03's ceiling** (and, if desired, revisits SAF-04's deferred posture) — this is now the single highest-leverage open action, since the evidence that was the sole blocker now exists.
2. **Owner states DSL-01's epsilon_tol** and confirms the significance-criterion interpretation — unblocks the diesel-reduction research track's preregistration (execution would still need separate authorization after).
3. **Convene SAF-05's formal governance review** — both prerequisites are now satisfied; this is a scheduling/convening action, not a repository-evidence gap.
4. **Decide the EVID-01/EVID-02/UNC-02 resourcing question** — a budget/infrastructure-investment call, not an audit finding.
5. **Schedule RT-02** (full HiGHS/GAP19 regression suite) for a dedicated longer session — not a deadline blocker since SHA-256 match remains the standing continuity evidence.
6. **SAF-06** remains last — gated on the owner choosing to revisit SAF-01's "defer" decision, which this pass does not second-guess.

---

## Boundary confirmation

- `winner: null` is unchanged (re-confirmed, Section 6).
- All 6 `PROTECTED_FILES` are byte-for-byte unchanged (re-hashed, Section 6).
- `system/evaluation/replay_harness.py` was not invoked, edited, bypassed, or reimplemented.
- No dispatch campaign, historical replay, closed-loop simulation, or replay-equivalent comparison was run.
- No sealed 2025 blind-evaluation data was accessed or used as a development/training dataset.
- No model was fit, trained, tuned, recalibrated, or promoted; `FROZEN_MODEL_SHA256`/`EXPECTED_SHA256`'s *value* is unchanged (only its *source* changed, from a literal to a manifest-derived read, confirmed by 24/24 identical focused-test results).
- No production formula, default, reserve policy, solar-credit behavior, or control flow was changed.
- No `epsilon_tol`, reserve-shortfall ceiling, solar-credit cap, or safety-gate authorization threshold was invented, selected, or adopted anywhere in this pass.
- Nothing was staged, committed, or pushed.

**PASS COMPLETE — EVID-03 EVIDENCE DELIVERED (NO THRESHOLD ADOPTED), FOR-03 CONSOLIDATED (VALUE UNCHANGED), DSL-01/FOR-01 OWNER NOTES ADDED, SAF-03/SAF-05 RECLASSIFIED, NO BOUNDARY CROSSED**
