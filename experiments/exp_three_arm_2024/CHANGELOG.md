# CHANGELOG

## 2026-10-11: package created (CC, preparation only)

**Created** the folder `experiments/exp_three_arm_2024/`. It did not exist before, and no earlier package was found anywhere in the repo. Nothing outside this folder was created, modified, moved or deleted.

**Copied verbatim** (source is the project shared folder `polaris/three_arm_prep/` and `polaris/`; hashes checked after copying, see `PACKAGE_MANIFEST.sha256`):
- `reports/source_prep/`: PROTOCOL.md, PROPOSED_PATCH.diff, AUTHORIZATION_SHEET.md, PROTOCOL_ADDENDUM_D7a.md, POLARIS_winner_and_safety_audit.md, candidate_F_future_data_findings.md, and `d7/*` (report, proposed scripts, D7 check scripts and output).
- `reports/D7_VERIFICATION_REPORT.md`: same file as `reports/source_prep/d7/D7_VERIFICATION_REPORT.md`. It already carries the "Superseded" note added to its §5 earlier on 2026-10-11, before copying.

**Scripts:**
- `scripts/causal_cloud_lookup.py`: the `+` lines of PROPOSED_PATCH.diff, unchanged.
- `scripts/solar_convention.py`: unchanged copy of the proposal.
- `scripts/timestamp_guards.py`: copy of the proposal. Before copying, the proposal's placeholder decomposition hash prefix was replaced with the full SHA-256 (`596345aa…e52a`).

**Tests adapted from proposals (behaviour unchanged except as listed):**
- `tests/test_causal_cloud_lookup.py`: the runner path in the static guard was changed from `tests/run_three_arm_2024.py` to `scripts/run_three_arm_2024.py`, to match the package layout.
- `tests/test_d7a_parity.py`:
  - `REPO` changed from `parents[2]` to `parents[3]` (package layout).
  - The `SimpleNamespace` stand-in was replaced with the real `StationState`, because the stand-in's field names did not match the schema.
  - The state timestamp format was changed from naive `2024-03-15T07:00:00` to `2024-03-15T07:00:00Z`. This is the format the reference runner produces (`planner_cf_campaign_runner.py:220`). With the naive form, the unmodified `ForecastBundle` validation raised `TypeError` (run 1). That was a defect in the test, not in the code under test.

**Tests new:**
- `tests/conftest.py` (import paths).
- `tests/test_static_no_protected_access.py`. In run 1 the first version flagged provenance docstrings and the guard's own banned-string list. It was revised to scan executable code in `scripts/` and imports in `tests/`.
- `tests/test_input_integrity_2024.py`: runs `run_all_guards` on the 2024 inputs, and compares the reserve provider with the 2024 decomposition.

**Documents new:** README, PREREGISTRATION (draft), AUTHORIZATION (unsigned), DECISIONS_LOG, DATA_PROVENANCE, TIMESTAMP_VERIFICATION, DESIGN_AND_GATES, COMPUTE_BUDGET, reports/D7A_REVIEW, reports/FINAL_READINESS_REVIEW, reports/PREP_CHECKS_OUTPUT.txt, manifests.

**Not created:** `scripts/run_three_arm_2024.py` and `scripts/calibrate_arm_c.py`. They were never written, and fabricating them is outside this task.

**Historical records untouched:**
- The 10-10 replay (FAILED) and the recovery (authorization undocumented) keep their original statuses.
- No winner artifact, governance document or frozen module was edited.

## 2026-10-11: runner and Arm C calibration implemented (CC, preparation only)

Scope: code preparation and synthetic tests only. **No experiment execution, no calibration on real data, no forecast replay, no training, no MILP solve.** Nothing outside `experiments/exp_three_arm_2024/` was created or modified. No decision status was changed.

**Created:**
- `config/EXPERIMENT_CONFIG.json`: every execution-critical setting in one place.
  - Decision statuses mirror DECISIONS_LOG.
  - Every protocol ambiguity is `null`.
  - Values stated by the protocol but not approved are marked `PROPOSED`.
  - Expected SHA-256 for 19 frozen code files, 4 inputs, and 4 YAML configs plus `run_diesel_reduction_campaign.py`.
  - `frozen: false`.
- `AUTHORIZATION_RECORD.json`: an unsigned template (`NOT_AUTHORIZED`) with separate `calibration` and `execution` sections that bind the manifest, config and artifact hashes and the solve ceiling.
- `scripts/preflight.py`: fail-closed checks shared by both entry points:
  - decisions APPROVED with evidence, and config frozen;
  - gate settings resolved;
  - Arm C method resolved;
  - arm invariants;
  - pinned hashes;
  - package manifest;
  - preregistration freeze line;
  - authorization record;
  - budget reconciliation;
  - output root.

  There is no override.
- `scripts/calibrate_arm_c.py`: Arm C calibration. It implements PROTOCOL §4 only where unambiguous; every open choice comes from the config and raises if `null`. `main()` refuses through preflight before reading any data.
- `scripts/run_three_arm_2024.py`: the runner, with modes `--audit-budget`, `--preflight` and `--execute`.
  - `execute()` re-runs the full preflight itself.
  - Every `optimize()` is charged to a hard budget before the solver is called.
  - Each run gets a new `run_<UTC>` directory, created with `exist_ok=False`.
  - On the first failure the arm is marked INVALID and the run FAILED.
  - Partial output goes only to `PARTIAL_HOURLY_TELEMETRY_INVALID.csv`.
  - `RESULTS.json` is written with exclusive create, and only after `validate_run` passes.
- `scripts/gates_three_arm.py`: gate evaluation. It refuses unresolved D2/D4/D6/D10 settings. B is never eligible, and `winner` is always `null`.
- `tests/synthetic_fixtures.py`, `tests/test_preflight_governance.py`, `tests/test_calibration_arm_c.py`, `tests/test_runner_three_arm.py`.
- `reports/CALIBRATION_AMBIGUITIES.md`.

**Modified:**
- `tests/conftest.py`: added the autouse `no_solver` fixture. It replaces `highspy.Highs`, the runner's planner loader and `PlannerCFV1Optimizer.optimize` with mocks that raise `SolverCalled`.
- README, DECISIONS_LOG (D5 sub-choices, D8, D9, BUD reconciliation, D11), COMPUTE_BUDGET (runner-derived accounting), DESIGN_AND_GATES (B and C enforcement, gate ambiguities G-a…G-d), DATA_PROVENANCE (no derived files; **Open-Meteo licence UNVERIFIED**, replacing the earlier website-based statement; SITES attribution obligations), PREREGISTRATION (draft; status, §3, §7, §8), FINAL_READINESS_REVIEW, AUTHORIZATION.md (stale facts only: code row, 1 worker instead of ≤ 4, pointer to the machine-checked record; still unsigned, and no checkbox ticked).
- `reports/PREP_CHECKS_OUTPUT.txt` was regenerated, overwriting the earlier generated output (history is kept in FINAL_READINESS_REVIEW §5).
- `manifests/CODE.sha256` and `PACKAGE_MANIFEST.sha256` were regenerated. PACKAGE_MANIFEST now uses exactly the exclusions in `preflight.manifest_files`: PREREGISTRATION.md, AUTHORIZATION.md, AUTHORIZATION_RECORD.json, logs/, results/ and calibration/ are excluded, because they record the freeze or are created later. The earlier manifest listed AUTHORIZATION.md, PREREGISTRATION.md and the `.keep` files.

**Runner docstring:** the reference loop is cited by folder and line numbers, not by its file name. `test_causal_cloud_lookup.py::test_static_guard_runner_has_no_2025_paths` bans that file name anywhere in the runner source, docstrings included. The test was not changed.

**Test-fixture corrections during this task (code under test unchanged):**
- `test_calibration_arm_c.py`: the synthetic calibration set was enlarged from 60 to 119 origins. With 60, one synthetic bin had only 13 origin-days, so the merge test hit a genuine "no neighbour" refusal instead of the case it meant to test.
- `test_runner_three_arm.py::test_timestamp_and_origin_alignment`: the expected realized PV is now the executor's own `pv_from_sw_in`, compared at 0.005 W, because the executor reports powers rounded to 0.01 W.

**Process note:** while looking for Open-Meteo licence evidence, a recursive `grep` for the literal string "open-meteo" scanned the whole read-only staged repository copy. That copy includes the 2025-campaign replay output files. grep printed only file names that contain that string: code, docs, and a 2025 weather-dataset manifest JSON. No file contents and no values were displayed or used. This is recorded so it is not hidden. Future searches are restricted to named paths.

## 2026-10-11: decision pass after M6 (CC; recording and code only)

Puni confirmed being the project lead (M6). This pass made no experiment execution, real-data calibration, forecast replay, training or solver call. Nothing outside `experiments/exp_three_arm_2024/` changed, and no file in `reports/source_prep/` changed.

**Decisions recorded** (classification in `reports/DECISION_RESOLUTION_2026-10-11.md`):
- **D2:** APPROVED.
- **D4:** APPROVED for the primary metric. The secondary SoC-parity application is blocked on one choice.
- **D6:** PARTIALLY APPROVED. The seed (42) was recorded under the M6 instruction; the interval is open.
- **D10:** CONFLICT recorded (PROTOCOL §7 {A, C} vs M6 {A, A-Fix, C}). Not resolved by CC.
- **Arm C A1–A6:** RECOMMENDED, awaiting approval.

**Created:**
- `reports/DECISION_RESOLUTION_2026-10-11.md`
- `tests/test_decision_resolution.py`

**Modified:**
- `config/EXPERIMENT_CONFIG.json`
- `scripts/gates_three_arm.py`: S4_point with strict pairing; separate S4_strict; vectorized documented stationary bootstrap; E1 statistic and fixed family size; unadjusted-only primary metric; gated secondary analysis.
- `scripts/calibrate_arm_c.py`: `closed_middle` rule; per-dimension boundary rules; `merge_single_neighbour_else_lower`; two-pass `read_calibration_input` that never parses excluded rows; 00:00-origin check.
- `scripts/preflight.py`: primary metric fixed; secondary-analysis status required; recommended-but-undecided interval flagged; every Arm C entry must carry a status.
- `tests/test_preflight_governance.py`, `tests/test_runner_three_arm.py`: real-config assertions updated to the new decision state. They still assert refusal on every open item.
- `tests/synthetic_fixtures.py`: the TEST-ONLY `approve_everything` now uses the config's own recommended values and the S4-strict settings.
- Documents: DECISIONS_LOG, PREREGISTRATION (draft), DESIGN_AND_GATES, COMPUTE_BUDGET (bootstrap is 0 solves), AUTHORIZATION.md (gate row options only; unsigned, nothing ticked), CALIBRATION_AMBIGUITIES (status and summary added; original text kept with two marked corrections), FINAL_READINESS_REVIEW.
- Regenerated: PREP_CHECKS_OUTPUT, manifests and the logs/PREFLIGHT_OUTPUT.

**Corrections of my own earlier statements:**
1. G-c said the SoC-parity factor f was "defined in no repository document". It is defined in PROTOCOL.md §7 (f ∈ {0.30, 0.75} L/kWh).
2. CALIBRATION_AMBIGUITIES A4 said origin-day and calendar-day counts differ near midnight. They are identical for 00:00 origins.

## 2026-10-11: decision pass after M7 (CC; recording and code only)

No experiment execution, real-data calibration, forecast replay, training, simulation or solver call. No observation or outcome value was read; the only new numbers are pvlib clear-sky geometry. Nothing outside `experiments/exp_three_arm_2024/` changed; `reports/source_prep/` unchanged; D7a not amended.

**Decisions recorded** (`reports/DECISION_RESOLUTION_M7_2026-10-11.md`):
- **D10:** APPROVED by the project lead: {A, C} vs PC-Control, as PROTOCOL §7. A-Fix diagnostic only. M6 proposal {A, A-Fix, C} not adopted.
- **D6:** seed 42 confirmed as the project lead's decision. Sign convention verified (ΔU = arm − control; upper ≤ 0). Interval two-sided 95% (97.5th percentile) recorded as the project lead's proposal, not yet approved. Status stays PARTIALLY APPROVED.
- **D4:** PROTOCOL §7 formula written out verbatim; per-origin vs aggregate compared; per-origin recommended. Formula not amended; secondary analysis still BLOCKED.
- **Arm C / D5:** evidence, leakage risk and tests per choice. New A8 (daylight definition, not in PROTOCOL). D5 values traced to PROTOCOL §4; two citations to a file in a 2025 campaign folder were not opened and are marked unverified.

**Created:** `reports/DECISION_RESOLUTION_M7_2026-10-11.md`, `tests/test_decision_resolution_m7.py` (16 tests).

**Modified:**
- `config/EXPERIMENT_CONFIG.json` (version draft-2026-10-11c): D10 APPROVED with M7 evidence; `E1_holm_family: ["A", "C"]`; `E1_holm_family_options` replaced by `E1_holm_family_note`; `S4_strict_interval_proposal` added (`S4_strict_interval` stays null); D4, D5, D6 evidence updated; A8 note on `gamma_objective`.
- `scripts/calibrate_arm_c.py`: new `residual_space_diagnostic` recorded in the calibration artifact (A5 evidence; decides nothing).
- `tests/synthetic_fixtures.py`: TEST-ONLY `approve_everything` uses the approved family {A, C}.
- `tests/test_preflight_governance.py`, `tests/test_runner_three_arm.py`: real-config assertions updated for D10; they still assert refusal on D6 and every other open item.
- Documents: DECISIONS_LOG (rows D4, D5, D6, D10; new decision register), FINAL_READINESS_REVIEW, PREREGISTRATION (draft), DESIGN_AND_GATES, AUTHORIZATION.md (status pointer only; unsigned, nothing ticked), CALIBRATION_AMBIGUITIES (A5 evidence, new A8).
- Regenerated: PREP_CHECKS_OUTPUT, `manifests/CODE.sha256`, PACKAGE_MANIFEST, `logs/PREFLIGHT_OUTPUT.txt`.

**Test-only corrections during this pass (no code under test changed to pass):** one new test used a synthetic calibration set too sparse for binning, so it now stubs `quantile_table` (bins are covered elsewhere); one assertion checked for wording that the config note does not contain and was corrected to the actual wording.

## 2026-10-11: decision follow-up after M8 (CC; recording and code only)

No calibration, replay, training, simulation or solver call; no observation or outcome value read. `reports/source_prep/` unchanged; D7a not amended.

**Decisions recorded** (`reports/DECISION_FOLLOWUP_M8_2026-10-11.md`):
- **D6:** APPROVED in full (interval two-sided 95%, 97.5th percentile; seed 42; 10-day blocks; 10,000 resamples). ΔU = arm − control and upper ≤ 0 preserved.
- **D10:** stays APPROVED ({A, C}). The wording condition is a new decision **D10a**, CONFLICT — AMENDMENT PROPOSED; it blocks execution.
- **D4:** primary and secondary roles approved; secondary application stays BLOCKED. PROTOCOL §7 text and its (unstated) aggregation level documented verbatim.
- **A1–A6, A8, D5:** unchanged statuses; full detail added. D5's two citations UNVERIFIED; authorized source requested.
- D1, D3, D7, D7a, D8, D11, BUD unchanged.

**Created:** `reports/DECISION_FOLLOWUP_M8_2026-10-11.md`, `reports/PROPOSED_AMENDMENT_D7a-1.md` (proposal only).

**Modified:**
- `config/EXPERIMENT_CONFIG.json` (draft-2026-10-11d): D6 APPROVED; `S4_strict_interval: two_sided_95_upper` with `S4_strict_interval_record`; recommendation and proposal fields removed; new decision D10a; D10, D4, D5 evidence extended; `soc_parity_secondary.formula` (which had added per-origin subscripts to the protocol formula) replaced by `protocol_text_verbatim`, `protocol_aggregation_semantics`, `per_origin_form_proposed` and `aggregate_form_alternative`; citation status on `gamma_objective` and `min_origin_days_per_bin`.
- `scripts/preflight.py`: D10a added to `EXECUTION_DECISIONS` (not to calibration).
- `scripts/gates_three_arm.py`: the secondary output reports `protocol_text` and `applied_form` instead of `formula`.
- Tests: `test_decision_resolution_m7.py` (D6 test updated to the approved state; D4 text test; 4 new tests), `test_preflight_governance.py`, `test_runner_three_arm.py` (real-config assertions for D6 approved and D10a blocking).
- Documents: DECISIONS_LOG (rows D4, D6, D10, new D10a; register), FINAL_READINESS_REVIEW, PREREGISTRATION (draft), DESIGN_AND_GATES, AUTHORIZATION.md (status pointer only; unsigned, nothing ticked), CALIBRATION_AMBIGUITIES (citation status).
- Regenerated: PREP_CHECKS_OUTPUT, `manifests/CODE.sha256`, PACKAGE_MANIFEST, `logs/PREFLIGHT_OUTPUT.txt`.

**Correction of my own earlier record:** the config's `soc_parity_secondary.formula` wrote the protocol formula with per-origin subscripts and cited PROTOCOL §7, which presented an interpretation as protocol text. It is replaced by the verbatim text, with the per-origin form recorded separately as a proposal.

**Test-only correction during this pass:** before its first run, the new A3 test was changed to a two-bin layout so that empty cells cannot trigger unrelated merges. After it passed, one of its assertions was found to compare against a wrongly computed point forecast (actual − clear sky instead of actual − point); it was corrected and re-run (pass).

## 2026-10-11: M9 technical-PM decision pass (CC; no execution)

Brief: M9 (`cmsg_017TpQv3UrTPMkzn658LmXvX2WPEGQjqxQQ7wSucS9sxg4`). Nothing was calibrated, replayed, trained, simulated or solved. No protected or 2025 file was opened. Nothing outside `experiments/exp_three_arm_2024/` was changed. `reports/source_prep/` is unchanged.

**Code (small, test-covered):**
- `scripts/preflight.py`:
  - added `PASSING_STATUSES` and `status_failure()`. `APPROVED BY EXISTING AUTHORITY` and `RESOLVED BY DELEGATED TECHNICAL AUTHORITY` now pass, but only with a named `authority`. Every other status still fails.
  - `HANDOVER.md` added to `MANIFEST_EXCLUDED`, because it records the manifest hash.
- `scripts/gates_three_arm.py`:
  - the SoC-parity secondary accepts the same passing statuses, reports `per_origin_form` and `limitations`;
  - new `arm_c_evaluation_coverage()` (PROTOCOL §4 diagnostic);
  - `arm_metrics` adds `j2_reserve_shortfall_Wh`, `fuel_exhausted_hours` and `final_soc_pct_mean` (D7a §6).
- `scripts/run_three_arm_2024.py`:
  - `LABEL_C` is now `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)` (D10a);
  - Arm C logs its horizon-0 bound, point, bin and realized value, and refuses on timestamp misalignment;
  - the hourly record adds `diesel_fuel_remaining_l`.
- `scripts/calibrate_arm_c.py`: `quantile_table` records per-cell `own_origin_days`, `own_n_hours`, `in_sample_coverage_pooled` and `in_sample_coverage_own`. The quantiles are unchanged.

**Config** (`config_version` draft-2026-10-11e, `frozen: false`):
- decisions D1, D3, D5, D7, D7a, D10a and BUD: RESOLVED BY DELEGATED TECHNICAL AUTHORITY;
- D8: CONDITIONALLY APPROVED, with a recorded condition;
- D11: APPROVED BY EXISTING AUTHORITY (internal use);
- new D11-PUB: BLOCKED — EVIDENCE REQUIRED;
- all `arm_c_method` entries: delegated, with `basis`. The A3 limitation is recorded;
- `soc_parity_secondary`: per-origin, delegated, with `limitations`;
- D2, D4, D6 and D10: untouched.

**Tests:**
- New `tests/test_decision_resolution_m9.py`.
- State-snapshot tests that asserted the M6–M8 state were updated to assert the M9 state. Each update notes the earlier state in a comment or docstring:
  - `test_calibration_arm_c.py::test_main_refuses_before_reading_data` (D8 instead of D5);
  - `test_decision_resolution.py::test_recommended_values_are_valid_and_now_delegated`;
  - four M7 tests (D4 secondary, D5 values, A8, C label) and the D10a test;
  - three `test_preflight_governance.py` real-config tests;
  - one fragment list in `test_runner_three_arm.py::test_execute_refused_on_real_package_config`.
- No assertion about the preserved approvals was relaxed.

**Documents:**
- New:
  - `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`;
  - `reports/DECISION_RESOLUTION_M9_2026-10-11.md`;
  - `reports/D7A_REVIEW_M9_2026-10-11.md` (supersedes `reports/D7A_REVIEW.md`, which is kept);
  - `reports/evidence/D11_DATA_RIGHTS_EVIDENCE_2026-10-11.md`;
  - `HANDOVER.md`.
- Appended or updated:
  - DECISIONS_LOG (M9 rule, ledger after M9; main table kept as history);
  - FINAL_READINESS_REVIEW;
  - PREREGISTRATION (prior-use disclosure, M9 section);
  - DESIGN_AND_GATES (C label, M9 section);
  - DATA_PROVENANCE (M9 update, §4 table kept);
  - TIMESTAMP_VERIFICATION (review outcome);
  - COMPUTE_BUDGET (status);
  - AUTHORIZATION.md (pointer only, still unsigned);
  - README;
  - `reports/PROPOSED_AMENDMENT_D7a-1.md` (status line appended; text unchanged).

**Regenerated:** `manifests/CODE.sha256` (package section), `PACKAGE_MANIFEST.sha256`, `reports/PREP_CHECKS_OUTPUT.txt` and `logs/PREFLIGHT_OUTPUT.txt`.

**Sandbox result:** 334 passed, 0 failed. The device venv was not run.

## 2026-10-11: M9 follow-up — D8 resolved, package frozen (CC; no execution)

Brief: `cmsg_017TpQv3UrTPMkzn658LmXvX9LP4GbwMUWDt2Wm5yLAtDn`. No calibration, replay, training, simulation or solver call.

- **Added** `reports/DEVICE_VENV_TESTS.txt` (the project lead's laptop run, copied byte-for-byte; SHA-256 `e23786a3…57fc`).
- **Config:** D8 → RESOLVED BY DELEGATED TECHNICAL AUTHORITY with `condition_met`; `frozen: true`; `config_version` frozen-2026-10-11f; `frozen_record` added. No other decision, value, gate or budget changed.
- **Tests (state assertions only; scripts unchanged):** `test_preflight_governance.py::test_real_config_is_frozen_and_decisions_resolved` (was `..._is_not_frozen_and_decisions_unresolved`), `::test_real_preregistration_freeze_line_is_blank_or_matches_the_manifest` (was `..._is_not_frozen`), `test_decision_resolution_m9.py::test_d8_resolved_only_on_the_recorded_device_venv_pass` (was `test_d8_conditional_still_blocks_...`), the fragment list in `test_runner_three_arm.py::test_execute_refused_on_real_package_config`, and one assertion in `test_calibration_arm_c.py::test_main_refuses_before_reading_data`.
- **Documents:** DECISIONS_LOG ledger (D8, Freeze, D9 rows), FINAL_READINESS_REVIEW (status, §4, §11), M9 report follow-up section, PREREGISTRATION (status, §9 freeze line, outside the manifest), HANDOVER.md (outside the manifest).
- **Regenerated:** `manifests/CODE.sha256`, `PACKAGE_MANIFEST.sha256`, `reports/PREP_CHECKS_OUTPUT.txt`, `logs/PREFLIGHT_OUTPUT.txt`.

## 2026-10-11: D9 authorization boundary, schema v2 (CC; no execution, no signature)

Approved by the project lead on 2026-10-11T06:06:18Z (`cmsg_017TpQv3UrTPMkzn658LmXvXDN5FsK9SWj34KVbksr5eVX`), after the 06:01:19Z plan request. Plan: `polaris/reviews/D9_AUTHORIZATION_BOUNDARY_PLAN_2026-10-11.md`.

- **Why:** schema v1 could not tell a preflight-only signature from execute authorization. The `execution` section signed 05:49:08Z "for the preflight stage only" satisfied `--execute` as well.
- **`scripts/preflight.py`:** adds `RECORD_SCHEMA_VERSION = 2`, scopes `PREFLIGHT_ONLY` and `EXECUTE_EXPERIMENT`, and the new functions `check_execution_authorization(repo, cfg, mode, art_sha)`, `check_calibration_authorization(repo, cfg, artifact)` and `prior_freezes(repo)`.
  - `check_authorization` now validates `calibration`, `execution_preflight` or `execution`, and raises on any other stage.
  - Execution sections require their fixed `scope`, and `solve_ceiling` must be an integer.
  - `execution` also requires a non-empty `execute_instruction_ref`, and must not be signed earlier than `execution_preflight`.
  - `history` is never read.
- **`scripts/run_three_arm_2024.py`:**
  - `full_preflight(repo, cfg, mode)` requires `mode` ("preflight" or "execute"); there is no default.
  - `main --preflight` passes "preflight", and `execute()` passes "execute".
  - `execute()` re-checks the execute-scoped authorization immediately before any machinery, and records `execute_instruction_ref` in RUN_STATUS.
  - A new `[calibration_authorization]` check binds the artifact to a signed calibration authorization (current config; manifest equal to the current one or to a recorded prior freeze; signed no later than the artifact's `created_at_utc`).
  - `calibrate_arm_c.py` is unchanged.
- **Tests:**
  - Root cause of the 6 failures after the signatures: the fixture copied the live record. `synthetic_fixtures.build_fake_repo` now writes `null_record()`, and `sign()` sets scopes and the instruction reference.
  - The 6 tests that failed against the signed record now pass: `test_main_refuses_before_reading_data`, `test_execute_refused_on_real_package_config`, `test_unsigned_template_refused`, `test_calibration_signature_does_not_authorize_execution`; the two live-record tests are replaced.
  - Replaced: `test_decision_resolution_m9.py::test_authorizations_remain_unsigned` → `test_live_authorization_record_state`, and `test_preflight_governance.py::test_real_authorization_record_is_unsigned` → `test_real_authorization_record_grants_no_execution`. Both asserted the pre-signature state.
  - `test_runner_three_arm.py`: `full_preflight` callers pass a mode, the synthetic artifact carries `created_at_utc`, and the synthetic execute environment signs a TEST-ONLY execute authorization.
  - New: `tests/test_authorization_scope_v2.py` (46 tests: scope, instruction reference, schema version, history, per-field and hash binding, calibration preservation and prior freeze, end-to-end `--execute` refusal, defence in depth).
  - A mutation check confirmed that letting `--execute` accept the preflight section fails 7 of them.
  - Suite: 381 passed (was 334).
- **Not changed:** `config/EXPERIMENT_CONFIG.json` (`fac38b26…`), the calibration artifact (`65732ccc…`), the input and configuration manifests, and the calibration signature.
- **D8:** kept OPEN for re-confirmation until the project lead re-runs the updated suite in the device venv. See the DECISIONS_LOG ledger.
- **Outside the manifest:**
  - `AUTHORIZATION_RECORD.json` → schema v2. The 05:49:08Z block was moved verbatim to `history[0]` with a correction record, along with the full v1 file text (SHA-256 `5dd3c007…711e`).
  - `AUTHORIZATION.md` now states that the JSON record and the project lead's explicit instructions govern.
  - PREREGISTRATION §9: new freeze plus a prior-freeze line. Stale §4, §7 and §8 text corrected.
  - HANDOVER.
- **Regenerated:** `manifests/CODE.sha256`, `PACKAGE_MANIFEST.sha256`, `reports/PREP_CHECKS_OUTPUT.txt`.

## 2026-10-11 (post-execution): incident at run_20261011T075716Z, telemetry fix, single-use authorization

- **Execution was signed (07:52:41Z) and attempted outside this project's thread.** A separate laptop AI assistant
  session signed `AUTHORIZATION_RECORD.json`'s `execution` section using a `NON_CMSG_REF` (a content hash of the
  instruction text, not a project message id). This project's CC has not independently verified that reference.
- **The run (`results/run_20261011T075716Z/`) FAILED, exit 4.** Root cause: `solver_status` in telemetry recorded
  the native HiGHS diagnostics string (`"HighsModelStatus.kOptimal"`) instead of the gated literal `"OPTIMAL"`
  that the in-loop gate (and every solve) actually used. `validate_run` rejected every row on that mismatch.
  All 14,760 solves were genuinely optimal/feasible; this was not a solver failure. No `RESULTS.json` was written.
  The run directory is preserved unmodified.
- **Fix:** `run_three_arm_2024.py` now writes both `solver_status` (the gated literal, unchanged meaning) and a
  new column `solver_status_native` (the raw diagnostics string, for audit). The in-loop fail-closed gate and
  `validate_run`'s status check are unchanged.
- **Single-use authorization (project-lead decision, 2026-10-11):** `preflight.py` adds
  `_consumed_execute_refs()`, consulted from `check_authorization("execution", …)`. It refuses any
  `execute_instruction_ref` that already appears in a `results/run_*/RUN_STATUS.json`, for any outcome. This
  closes the gap that the record alone is not single-use in code.
- **Tests:** 6 new/updated tests in `tests/test_runner_three_arm.py` (native-status normalization, native-status
  preservation, diagnostics-missing fallback, invalid status still raises, and the existing-run-directory test
  split into two to isolate the new authorization-layer guard from the file-exclusivity guard); 4 new tests in
  `tests/test_preflight_governance.py` for the single-use check. Sandbox run (Python 3.13.16, not the device
  venv): 390 passed; the only 2 failures are `test_live_authorization_record_state` and
  `test_real_authorization_record_grants_no_execution`, both of which assert the live `execution` section is
  null -- expected, since the 07:52:41Z signature is still live pending the project lead's approval of its
  retirement to `history`. **This sandbox count is not D8 evidence.**
- **Not changed:** `AUTHORIZATION_RECORD.json`, `config/EXPERIMENT_CONFIG.json`, `PACKAGE_MANIFEST.sha256`,
  the calibration artifact, D8's `condition_met`, `.pytest_cache/` (still present from the earlier run, pending
  an explicit deletion decision).
- **Package status: NOT frozen, NOT validated, NOT ready to execute.** See
  `INCIDENT_REVIEW_RUN_20261011T075716Z.md` and `RECOVERY_IMPLEMENTATION_REPORT_2026-10-11.md` (project files,
  `polaris/reviews/`) for the full analysis, the proposed record transition (not yet applied), and remaining
  steps (device-venv D8 re-run, re-freeze, calibration re-bind).
