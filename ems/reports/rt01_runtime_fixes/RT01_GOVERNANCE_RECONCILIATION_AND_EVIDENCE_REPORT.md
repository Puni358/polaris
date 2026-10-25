# POLARIS — RT-01 Governance Reconciliation & Synthetic E2E Evidence Preservation: Report

**Date:** 2026-10-18
**Nature of this document:** Seventeenth pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` (sixteenth pass). Mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Register impact:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json`, new Section 33, v1.9.6 → v1.9.7 — `RT-01`'s `closure_test` field and the matching entry in `critical_dependency_chain_to_production` corrected; `owner_decision_record` gains a dated note. **`RT-01.current_state` is UNCHANGED (`decided`, i.e. open/not-closed at the full-system level).** No other canonical item touched.
**Scope confirmation up front:** This is a narrow governance/documentation/evidence-preservation pass **only**. No production code was edited (`router.py`, `ecd.py`, `option_d.py`, `gap19_highs_native.py`, `simulator.py`, `runner.py`, `manifest.py`, `evaluator.py` were all read-only inspected). No campaign, replay, or dispatch-comparison experiment was run. No full test suite was run. Exactly one existing, already-authorized test fixture was re-invoked once, solely to close a specific evidence gap (artifact overwritten — see Item 2). Nothing was staged, committed, or pushed.

---

## 1. Exact files changed and why

| File | Change | Why |
|---|---|---|
| `POLARIS_MASTER_DECISION_REGISTER.json` | `version` 1.9.6→1.9.7; `date` updated; `RT-01.closure_test` corrected to name all 5 tests (was "The 3 tests pass..."); `critical_dependency_chain_to_production`'s RT-01 entry corrected 3→5; `RT-01.owner_decision_record` gains dated note `pass_2026_10_18_seventeenth_pass_governance_reconciliation`; new top-level `amendment_2026_10_18_seventeenth_pass_...` summary key added | Reconcile the directive's named inconsistency (closure wording said 3, scope/evidence notes already said 5) without inventing a new closure standard |
| `POLARIS_MASTER_DECISION_REGISTER.md` | Header date line appended ("amended a seventeenth time..."); companion-file version reference bumped; `RT-01` master-table row gains a note; new **Section 33** added | Mirror the JSON correction in the authoritative narrative document, per this register's own stated convention (MD is authoritative if the two differ) |
| `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` / `.json` | Copied verbatim from the root versions | Required mirror, per every prior pass's convention |
| `RT01_GOVERNANCE_RECONCILIATION_AND_EVIDENCE_REPORT.md` (this file) + `N6_REMEDIATION_REPORTS/` mirror | New | This pass's own deliverable |
| `system/artifacts/latest_dispatch_plan.json` | Regenerated (artifact, not a tracked/protected source file) | Side effect of the single authorized fixture re-invocation in Item 2 below |

**No test file, production file, config file, or `PROTECTED_FILES` entry was edited.** No file was staged, committed, or pushed.

---

## 2. RT-01 closure wording — before/after, and confirmation `current_state` is unchanged

**Before (JSON `items[RT-01].closure_test`):** *"The 3 tests pass, or a documented, owner-accepted explanation exists for why the residual is expected and the tests' assertions should be relaxed."*

**After:** corrected to explicitly name all 5 tests — `test_flexible_load_constraints`, `test_flexible_load_no_double_counting`, `test_per_timestep_conservation_audit`, `test_cumulative_physical_conservation_168h`, `test_long_duration_closed_loop_endurance_168h` — pass, or a documented/owner-accepted explanation exists, with an explicit note that the test *count/names* are corrected while the owner's closure *standard* (pass, or accepted relaxation) is preserved unchanged.

A second, related inconsistency was found and corrected in the same pass: `critical_dependency_chain_to_production` still read *"RT-01 (resolve or formally waive the 3 pre-existing conservation-residual failures)"* — corrected to 5, with a dated note.

**No conflict between the actual register schema/owner decision and this correction was found.** The owner's 2026-10-17 `owner_decision_record.rationale`/`scope` already established the 5-test family; only the literal `closure_test` field text and the dependency-chain entry had not been updated to match. This correction was therefore made in full, per the directive.

**`RT-01.current_state` confirmation:** field value is `"decided"` both before and after this pass — **unchanged**. In this register's own vocabulary, `decided` means the owner's 2026-10-17 decision ("retain diagnostic findings, defer the protected GAP19/Option-D fix") stands and the item is not closed at the full-system level — this is the register's substantive equivalent of "open," not a literal string `"OPEN"`; no pass has ever used that literal string for this field, and this pass does not introduce one. RT-01 is **not** declared partially or fully closed by this pass.

---

## 3. Synthetic E2E evidence table

| Field | Value |
|---|---|
| Entry point / harness | `system/tests/test_offline_runtime.py::_authorize_router_for_offline_runtime_test()` (existing, pre-dating this pass) |
| Minimal reproducible invocation | `PolarisLocalRunner(SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="milp")` → apply fixture → `runner.run_pipeline(steps_to_run=12)` |
| Synthetic authorization fixture / evidence ID | `evidence_id="EVID-TEST-OFFLINE-RUNTIME"`, `authorized_critical_load_w=5000.0`, `t_required_authorized=True` — confirmed by direct source read, unchanged from the sixteenth pass's citation |
| Route reached real optimizer/simulator? | Yes — `constraint_status: OPTIMAL` (route `NORMAL` → GAP19/MILP, not Option-D fallback, not blocked) |
| Execution status | `SUCCESS_CLEAN` |
| Requested / completed steps | 12 requested / 12 completed (`timesteps_executed: 12`) |
| Fault classes | `[]` (none) |
| System reliability | `100.0%` |
| Artifact path | `system/artifacts/latest_dispatch_plan.json` |
| Artifact mtime (this pass's re-run) | `Sun Oct 18 07:39:57 2026` |
| Artifact SHA-256 (this pass's re-run) | `da9269dfce78181a5a11c2ff12f1e228a42139717eb15f0e7123bf1eef542c8a` |
| Prior (sixteenth-pass) artifact SHA-256 | `a3d68d72995af368b36a02348c974440e27cafac6207b774a6c0f4f522705719` — **since overwritten on disk** (confirmed: current file's hash/mtime both differ from this value before this pass's re-run) |
| Limitations | Isolated SYNTHETIC test-fixture result only — **not** real station authorization, **not** proof of production readiness. The two artifact hashes necessarily differ between runs (run_id/timestamp fields vary per invocation); this is reported as fresh, independently-verified evidence of the *same result class*, not a bit-for-bit reproduction of the prior artifact. |

**Why this was rerun at all (evidence-gap justification):** the directive's own instructions required preferring existing artifacts/logs over rerunning, and rerunning only to close a specific gap via the existing authorized harness. The prior artifact was independently confirmed overwritten (different hash and mtime) before any rerun was performed, and no raw log of that specific ad hoc 12-step invocation (it is not a named pytest test method) existed elsewhere in the repository. The rerun used only the pre-existing fixture function, the identical scenario/optimizer/step-count the sixteenth pass used, no CLI, and no new authorization value — consistent with the "existing authorized synthetic test harness" requirement.

---

## 4. The two 168-hour failures — documented separately

**`test_long_duration_closed_loop_endurance_168h`** — exact assertions: `report["timesteps_executed"] == 168` and `report["ems_evaluation"]["system_reliability_pct"] == 100.0`. Only the second fails; observed value **90.04%**. Classification: a **genuine stress-scenario performance outcome** under the synthetic 168h endurance scenario — not a conservation/bus-bar defect, not a metric-label issue (reliability is a real, well-defined field here). Evidence: the sixteenth pass's own targeted re-run recorded this exact value; no bus-bar/double-counting/SOC-bound violation is asserted or found anywhere in this test. Smallest legitimate next action: an owner decision on whether 90.04% reliability under 168h synthetic stress conditions is an acceptable outcome, or whether further dispatch-performance engineering is warranted — any such engineering would likely touch `PROTECTED_FILES` (`option_d.py`/`router.py`/`gap19_highs_native.py`) and would require a separate governance authorization window, exactly as prior passes (§29–§31) already documented for related mechanisms. No prerequisite was created or removed by this pass.

**`test_cumulative_physical_conservation_168h`** — exact assertions: `ems_eval["unmet_critical_load_kwh"] == 0.0` and `ems_eval["renewable_utilization_pct"] >= 75.0`. Only the first fails; observed value **553.84 kWh**. Classification: a **metric-label/evidence limitation**, not a demonstrated bus-bar/physical-conservation defect. Direct, read-only inspection of `system/evaluation/evaluator.py` (lines ~268–304, unchanged) confirms:
- `unmet_critical_load_kwh` is computed as `total_unmet_wh / 1000.0` — numerically identical to `total_unmet_load_kwh` — and carries an explicit `unmet_critical_load_kwh_label_warning` stating it is not critical-specific.
- The actually critical-specific field, `dispatch_safety.critical_unmet_total_wh` / `critical_unmet_source`, is populated from `unmet_essential`, which (confirmed by `grep -rl "unmet_essential"`, zero occurrences outside the research-only `gap19_highs_native_milp_v2_research.py`) **neither `GAP19HighsNativeOptimizer` nor `OptionDFallbackSolver`** — the two optimizers the real production pipeline uses — ever sets.
- For this scenario, `critical_unmet_source` therefore reads `"FALLBACK_TO_TOTAL_UNMET_LOAD: ..."` and `critical_unmet_total_wh` reads `"UNKNOWN_NOT_VERIFIED"`.

**Per the directive's own instruction, the 553.84 kWh figure must not be represented as verified critical-load-only unmet energy, and it is not so represented here** — it is total unmet load under the test's own (mislabeled) field name. This is consistent with, and does not override, the sixteenth pass's own finding (§32.3/§32.5) that this gap was already corrected in the evaluator's richer `dispatch_safety` output by a prior pass; the test itself still asserts against the legacy, mislabeled field. Neither failure is claimed resolved, relaxed, or converted to a pass in this pass. Smallest legitimate next action: an owner decision on whether the test should be updated to assert against `dispatch_safety.critical_unmet_total_wh`/`critical_unmet_source` instead of the legacy field (a test-only change, but one that changes what is being verified — itself worth explicit owner sign-off rather than silent correction) — not performed here.

---

## 5. Protected-file hash comparison

All 7 `PROTECTED_FILES` entries were hashed **before** this pass's one fixture re-invocation and **after** it. Both sets are an **exact match** to the v1.9.6/sixteenth-pass recorded values:

| File | SHA-256 (before and after this pass — unchanged) | Matches v1.9.6? |
|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | Yes — exact match |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | Yes — exact match |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | Yes — exact match |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | Yes — exact match |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | Yes — exact match |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | Yes — exact match |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | Yes — exact match |

`system/evaluation/replay_harness.py` (not a `PROTECTED_FILES` entry, tracked for the campaign-guard boundary) also re-confirmed unchanged: `592a41c2700533dad8723fceb74e955cbf25b1d61cf950c95113e803e7cabf5b`. **Zero mismatches.** None of these 8 files was edited by this pass.

---

## 6. Campaign / frozen-asset / blind-data boundary confirmation

- `RT-01.current_state` remains `decided` (open at the full-system level) — confirmed unchanged (Item 2).
- `winner: null` re-confirmed unchanged at `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json` (line 5).
- The campaign-execution guard remains unconditional and unmodified: `replay_harness.py::FactorIsolatedReplayHarness.execute_experiment_a()`/`execute_experiment_b()` and `n6_multi_origin_harness/harness.py::execute_campaign()` both still unconditionally raise `CampaignExecutionNotAuthorizedError`; neither was invoked this pass.
- `DSL-01`'s `epsilon_tol` remains owner-deferred/unset: confirmed no numeric assignment exists anywhere in the repository (`grep -rln "epsilon_tol\s*=" system/` → zero matches); `DSL-01.current_state` remains `decided`/deferred.
- Critical-load-specific unmet energy remains unverified for production-optimizer output where the required `unmet_essential` signal is absent (Item 4).
- No sealed 2025 blind data was accessed.
- No frozen Stage 8.1/N6 asset was changed (none was opened for writing; `N6_OPERATIONAL_READINESS_REPORT.json` was read-only).
- No model training/tuning/promotion or broad experiment campaign occurred.
- Nothing staged, committed, or pushed (`git status --short` shows only pre-existing, unrelated staged files from before this session, and the register/report files as new untracked additions — no `git add`/`git commit` was run by this pass).

---

## 7. Remaining blockers and the smallest next authorized step

**Unchanged from the sixteenth pass, re-confirmed this pass, not newly resolved:**
1. The matched diesel comparison remains **BLOCKED** by the same 3 independent prerequisites: the campaign-execution guard (unconditional), `DSL-01`'s unset `epsilon_tol`, and the unverified critical-load-specific unmet-energy signal.
2. RT-01 remains open at the full-system level: 3 of 5 named tests pass under synthetic test-fixture authorization (sixteenth pass, re-confirmed in substance by this pass's fresh 12-step reproduction); 2 of 5 still fail for the reasons documented in Item 4 above (one performance outcome, one metric-label limitation) — neither newly resolved nor newly regressed.
3. `n6_operational_pipeline.py` still has no config-injection boundary (unchanged; not investigated further this pass — out of this pass's narrow scope).

**Smallest next authorized step (not taken by this pass, flagged for the owner):** a single owner decision on whether the now-internally-consistent 5-test, 3-pass/2-fail evidence picture (with the 2 failures' causes now individually and separately characterized, per Item 4) is sufficient for any partial RT-01 disposition change, or whether all 5 must pass first — exactly the open question the sixteenth pass's own Section 13 already flagged, now resting on a register that no longer disagrees with itself about how many tests that question refers to.

**This pass makes no success claim beyond what is directly, freshly verified above.** No test was relaxed or deleted. No threshold, authorization, or evidence value was invented. `RT-01.current_state` is unchanged.
