# N6 Multi-Origin Harness — Build Report (No Campaign Executed)

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`)
**Continues from:** `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` (Table row 2 — the N6-integrated multi-origin candidate harness did not exist anywhere in the repository), `POLARIS_MASTER_DECISION_REGISTER.md` v1.4.0.
**Nature of this document:** Build report for three bounded tasks: (1) a new, execution-gated multi-origin harness with unit tests against synthetic fixtures only; (2) a documentation-only trace of `epsilon_tol`'s dependency scope; (3) documentation-only description of the execution-authorization schema/precedent. **No replay, campaign, dispatch evaluation, or replay-equivalent simulation was run.** The sealed 2025 blind partition was not accessed. No model was trained, tuned, recalibrated, or promoted. `PROTECTED_FILES` were not edited. `winner: null` is unchanged. Nothing was staged, committed, or pushed.

---

## 1. Files changed and rationale

**New files:**

| Path | Purpose |
|---|---|
| `system/evaluation/n6_multi_origin_harness/__init__.py` | Package exports. |
| `system/evaluation/n6_multi_origin_harness/harness.py` | The harness itself: multi-origin `ScenarioSpec`/`ExperimentAConfig` construction, per-origin outcome recording, per-arm aggregation, and `MultiOriginCampaignHarness` (validate-only; execute always raises). |
| `system/tests/test_n6_multi_origin_harness.py` | 26 focused tests, synthetic fixtures only. |

**Placement rationale:** placed in `system/evaluation/`, alongside `replay_harness.py` and `forecast_lineage.py`, rather than in `research/`. `replay_harness.py`'s own module docstring frames itself as "the MINIMUM reusable structure needed for a future fair, paired evaluation" that is meant to be reused by later evaluation work — it is production-adjacent tooling, not a one-off research analysis. The new harness is exactly that: a second, larger-scale consumer of the same validation primitives (`ScenarioSpec`, `ExperimentAConfig`, `validate_matched_scenario_set`, `reject_if_oracle`), not a standalone research artifact like `research/pceeb_part_a_offline/` or `research/evid03_reserve_margin_analysis/` (which analyze existing historical data and publish a single numeric finding). Its tests live in `system/tests/`, next to `test_forecast_lineage_and_replay_harness.py`, for the same reason.

**Amended (not newly written) files**, both edits applied identically to keep the root and mirror in sync:

| Path | Change |
|---|---|
| `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` | Table row 2, Section 4.A item 2, and Section 8's bullet each gained an inline **"AMENDED 2026-10-17 (harness-build pass)"** note marking the harness-*existence* sub-gap closed, while explicitly stating the execution sub-gap (campaign authorization, and wiring `execute_origin_dispatch_cell`) remains open. Original text is left verbatim above each note, per this repository's existing amendment convention (see `POLARIS_MASTER_DECISION_REGISTER.md`'s own "amended..." header pattern). |
| `N6_REMEDIATION_REPORTS/DIESEL_COMPARISON_PREREQUISITE_PLAN.md` | Identical mirror of the above (byte-for-byte; verified with `diff`). |

**Not changed:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` — there is no dedicated register ID for "the multi-origin harness exists"; that gap lived only inside `DIESEL_COMPARISON_PREREQUISITE_PLAN.md`'s own Table row 2, which is what was amended instead. No owner-decision item (`SAF-03/04/05`, `DSL-01`, etc.) was touched or reclassified.

---

## 2. Focused tests and results

```
$ python3 -m pytest system/tests/test_n6_multi_origin_harness.py system/tests/test_forecast_lineage_and_replay_harness.py -q
.................................................
49 passed in 0.13s
```

The new suite's 26 tests, by category (directive's required categories in bold):

- **Interface wiring** (tests 01–03, 23): `build_origin_scenario_pair`/`build_multi_origin_campaign_config` construct `ScenarioSpec`/`ExperimentAConfig` instances correctly and `MultiOriginCampaignHarness.validate_campaign_config` delegates to `FactorIsolatedReplayHarness.validate_experiment_a_config` without error.
- **Multi-origin aggregation** (tests 18–22): status-count tallying, diesel total/mean that *excludes* (never zero-fills) missing values, safety-unknown vs. verified-pass/fail bucketing kept separate, per-arm filtering, and fail-closed on an empty arm.
- **Leakage prevention** (tests 02, 07): an oracle/leakage provider (`realized_sw_in`-family) as the *candidate* forecast is rejected by `OracleProviderRejectedError` both for a single origin and across a full multi-origin set — this is `forecast_lineage.reject_if_oracle`, already wired into `ScenarioSpec.__post_init__`, exercised at the new harness's own entry points, not reimplemented.
- **Failure handling** (tests 09–14, 16–17): exception → `FAILED_OPTIMIZATION_EXCEPTION`; non-`OPTIMAL` solver status → `FAILED_WORKER_EXIT`; fewer completed than expected steps → `INCOMPLETE_RUN`; missing safety evaluation → `UNKNOWN_NOT_VERIFIED` (never a pass); missing diesel/unmet-load metric → `None` (never `0.0`); malformed `OriginRunResult` construction fails closed.
- **Output integrity** (tests 15–17): `OriginRunResult.__post_init__` rejects an "unknown safety evidence paired with a non-null pass value" state, invalid step counts, and unrecognized `run_status` strings.
- **Execution gate** (tests 24, 26): `MultiOriginCampaignHarness.execute_campaign` raises `CampaignExecutionNotAuthorizedError` for both a 3-origin and a 1-origin config.
- **Documented gap, not a silent stub** (test 25): `execute_origin_dispatch_cell()` raises `NotImplementedError` unconditionally.

Every fixture is a hand-built dict/dataclass instance (origins `"o1"`/`"o2"`/`"o3"` or ISO-timestamp strings, synthetic SOC/diesel/unmet-load numbers). No test reads `POLARIS_HYBRID_FIXTURE_H1_0`, any `candidate_k_*` matrix, or any file under a `blind`/`sealed` path.

---

## 3. Proof the campaign was not executed

- `MultiOriginCampaignHarness.execute_campaign()`'s entire body is one line: `self._replay_harness.execute_experiment_a(config.experiment_a_config)` — i.e. it does not call GAP19, N6, the router, or the simulator itself; it forwards to `replay_harness.py`'s **existing, unmodified** `execute_experiment_a`, which raises `CampaignExecutionNotAuthorizedError` **unconditionally** (no flag/config/env var bypasses it — verified again this pass, `replay_harness.py` lines 254–259, byte-identical to the version read by the prerequisite plan).
- `execute_origin_dispatch_cell` — the one place a real per-origin GAP19/N6/simulator call sequence would go — is a 12-line function whose entire body is `raise NotImplementedError(...)`. It imports nothing from `gap19_highs_native.py`, `n6_solar.py`, `simulator.py`, or `router.py`. It is not called by any other function in the module or by any test except the one that asserts it raises.
- `grep` confirms no production forecast/optimizer/simulator class is imported anywhere in the new module:
  ```
  $ grep -n "^from\|^import" system/evaluation/n6_multi_origin_harness/harness.py
  from dataclasses import dataclass, field
  from typing import Any, Dict, List, Optional, Tuple
  from system.evaluation.replay_harness import (ExperimentAConfig, FactorIsolatedReplayHarness, MatchedControllerSettings, ScenarioSpec)
  from system.safety.reserve_policy_guard import SafetyEvaluationResult
  ```
  (`SafetyEvaluationResult` is a plain dataclass used only for typing/packaging an already-computed result — its own module, `reserve_policy_guard.py`, is read-only imported, never executed against real dispatch here.)
- The 26 new tests run in 0.12–0.13 seconds total — consistent with pure dataclass/validation logic, not with any solver, forecast model, or simulator invocation.
- No new file under `experiments/`, `results/`, or any `*.csv`/`*.json` results path was created by this pass.

---

## 4. Protected-file hashes and `winner: null` integrity checks

```
$ sha256sum system/optimization/implementations/gap19_highs_native.py system/optimization/implementations/option_d.py \
            system/control/ecd.py system/control/router.py system/simulation/simulator.py system/runtime/runner.py
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  runner.py
```
**Exact match** to every prior pass's recorded values, re-verified both before and after this pass's file writes. No `PROTECTED_FILES` entry was opened for editing.

`winner: null` re-confirmed unchanged at `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json:5` (`"winner": null`), untouched by this pass.

`git status` confirms only the files listed in Section 1 are new/modified by this pass; nothing was staged (`git add` was never run) or committed.

---

## 5. `epsilon_tol` dependency findings (documentation only — no value selected)

**Direct search this pass:** `grep -rn "epsilon_tol" --include="*.md" --include="*.json" --include="*.py" .` — confirms, again, **no numeric value for `epsilon_tol` exists anywhere in the repository**, consistent with every prior pass's finding (`N6_ANNOTATION_AND_EVIDENCE_PLANNING_REPORT.md` §2, `POLARIS_MASTER_DECISION_REGISTER.json` DSL-01 blocks). This pass does not select or invent one.

**What it is:** `epsilon_tol` is DSL-01's own preregistered **critical-reliability acceptance threshold** — the maximum tolerable degradation in critical-load service that diesel-reduction Candidate 2 (Net-Deficit EBR) may exhibit relative to baseline/Control before its *own* 123-origin research evaluation is considered to have passed (`POLARIS_MASTER_DECISION_REGISTER.json` §DSL-01 `owner_decision_note_2026_10_17`). It is **distinct from**:
- the diesel-savings **significance criterion** — `DIESEL_REDUCTION_CONTROL_DESIGN.md:205`'s preregistered p<0.05 Wilcoxon + BCa-CI research test vs. `reserve_policy_guard.py`'s separate, unauthorized p<0.01 SAF-05 production-promotion gate (traced to two independently-authored, non-conflicting criteria, register §19.2 — not reconciled or touched by this pass);
- SAF-03's reserve-shortfall ceiling and SAF-04's solar-credit cap (EBR/dispatch-level quantities, not a candidate-acceptance threshold).

**Classification, per the directive's three options:**
1. **Required to execute the comparison (mechanically)?** **No.** `epsilon_tol` is never read by `gap19_highs_native.py`, `router.py`, `simulator.py`, `reserve_policy_guard.py`'s `evaluate_dispatch_safety`, or the new multi-origin harness. Nothing in the dispatch/optimization/safety-evaluation code path consumes it as an input. A descriptive diesel-liters-and-unmet-load measurement (reporting numbers, not a pass/fail verdict) does not require it — this matches `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Table row 8 and Section 6's own "what must NOT be done" guidance (report descriptively; claim no gate verdict that was not authorized).
2. **Required only to classify research acceptance?** **Yes.** It is consumed exactly once, conceptually: as the pass/fail ceiling in DSL-01's own preregistered 123-origin acceptance test for Candidate 2. Without it, that specific test cannot be scored as PASS/FAIL — but a plain diesel/unmet-load report is still possible without invoking it at all.
3. **Required for both?** **No** — see (1). It gates *interpretation as an accepted research result under DSL-01's own protocol*, not the mechanical ability to run or measure dispatch.

**Procedural note (not a contradiction of the above):** `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`'s own verdict (`RESEARCH_DESIGN_COMPLETE — AWAITING SAFETY-GATE PREREGISTRATION`) states that DSL-01's *own* Candidate-2 123-origin evaluation specifically may not be *executed* — even in research mode — without `epsilon_tol` preregistered first, because preregistration-before-execution is the entire point of that protocol (mirroring PRB-01's own closed decision rule). This is a **self-imposed procedural gate on one specific future experiment (Candidate 2)**, not a computational dependency of dispatch/optimization code, and it is a separate, independent gate from `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` — both would need to clear, independently, before Candidate 2's own evaluation could run. It does **not** retroactively apply to a bare N6-vs-baseline descriptive diesel comparison that makes no DSL-01 research-acceptance claim.

**No value was selected, inferred, or implied by this pass.** DSL-01 remains `DEFERRED_BY_OWNER` (register §21.1 item 3), unchanged.

---

## 6. Execution-authorization requirements (documentation only — no record created)

**Mechanism inspected:** `system/evaluation/replay_harness.py`, class `FactorIsolatedReplayHarness`, methods `execute_experiment_a`/`execute_experiment_b`. Both raise `CampaignExecutionNotAuthorizedError` **unconditionally** — confirmed again this pass by direct read, byte-for-byte identical to the version cited in `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Section 2. `ExperimentBConfig` additionally cannot be *constructed* without `authorization_token` matching a module-level sentinel (`_EXPERIMENT_B_AUTHORIZATION_TOKEN = object()`) that no code path in this repository can satisfy.

**Precedent schema** (`experiments/exp_three_arm_2024/AUTHORIZATION_RECORD.json`, schema v2 — inspected directly this pass, not merely cited from the prior report):
- Three sections with **fixed, distinct scopes**: `calibration` (no `scope` field; informal), `execution_preflight` (`scope: "PREFLIGHT_ONLY"`), `execution` (`scope: "EXECUTE_EXPERIMENT"`). `preflight.py`'s `check_authorization()` enforces that `--preflight` accepts a valid `execution_preflight` **or** `execution` section, while `--execute` accepts **only** a valid `execution` section (`preflight.py:363-415`).
- **Required fields per signed section**: `decision` (`"APPROVE"`), `signer_name`, `signer_role` (must equal the literal string `"project lead"` — `preflight.py:298`, case-insensitive match enforced in code, not just convention), `signed_at_utc` (ISO-8601 UTC), `package_manifest_sha256`, `experiment_config_sha256`. The `execution` section additionally requires `calibration_artifact_sha256` (must match the actual calibration artifact's hash, checked in code — `preflight.py:383-384`) and `solve_ceiling` (must be an `int` exactly equal to the configured total solve-budget ceiling — `preflight.py:385`).
- **`execute_instruction_ref`** (execution section only): must be non-empty and must name the project lead's own separate, explicit "execute" instruction (by content hash and recording timestamp in this repository's observed instance — `AUTHORIZATION_RECORD.json`'s `execution.execute_instruction_ref`); code additionally checks it has not already been "consumed" by a prior run's `RUN_STATUS.json` (`preflight.py:308-403`), so the same execute instruction cannot silently authorize two separate runs.
- **Approving authority:** the signer's role must literally be `"project lead"` — no other role is accepted by `preflight.py`'s check. This is a repository-internal procedural control (the file's own `_comment` field states it is "not cryptographically signed"), not a cryptographic signature or external governance approval.
- **Verification conditions:** every hash field (`package_manifest_sha256`, `experiment_config_sha256`, `calibration_artifact_sha256`) must match the *current* artifact's actual computed hash at authorization-check time, not merely be present — a stale or mismatched hash fails the check even with an otherwise well-formed signed section.
- **`history`** is append-only and explicitly **never read for authorization** (`AUTHORIZATION_RECORD.json`'s own `_comment`) — it exists only as an audit trail of superseded entries.

**No equivalent signed record exists for `replay_harness.py`** — confirmed again this pass. It has no preflight/execute distinction, no signer/role/hash-matching fields, and no `history` ledger; it simply raises unconditionally regardless of any external file's contents. **This pass creates no such record, forges no signature, and modifies no guard.** Lifting `CampaignExecutionNotAuthorizedError` for a future N6-vs-baseline comparison would require either (a) extending `replay_harness.py` with an analogous checked-record mechanism (a code change, itself requiring its own authorization and governance review before being made), or (b) some other explicit, equally rigorous authorization path — this report does not recommend which, only documents that the `exp_three_arm_2024` precedent exists and what it requires structurally.

**Missing approval, stated exactly:** no signed section of any kind exists today authorizing execution of an N6-vs-baseline multi-origin campaign through this new harness or any other path. `MultiOriginCampaignHarness.execute_campaign()` will raise `CampaignExecutionNotAuthorizedError` for any config, today and until `replay_harness.py` itself is separately changed under its own governance review.

---

## 7. Remaining blockers and the shortest next step

**Remaining blockers (all independent, per `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Section 1 — none closed by this pass's harness-structure work):**
1. **Campaign-execution authorization** (Category C item 1) — `CampaignExecutionNotAuthorizedError` is still unconditional; this pass does not and cannot lift it.
2. **The harness's own execution body** — `execute_origin_dispatch_cell` still raises `NotImplementedError`; wiring it to real `N6SolarForecastEngine`/`GAP19HighsNativeOptimizer`/`DigitalTwinSimulator` calls is deliberately not done here, and should not be done before blocker 1 is resolved.
3. **DSL-01's `epsilon_tol`** — still unset by explicit, standing owner deferral; required only if a future comparison claims DSL-01's own research-acceptance verdict for Candidate 2 (see Section 5) — not required for a bare descriptive diesel/unmet-load report.
4. **EVID-02** (real, non-synthetic Nuolja critical-load measurement) — still `EXTERNAL_EVIDENCE_REQUIRED`; any future comparison's unmet-critical-load figures remain `SYNTHETIC_ENGINEERING_SCENARIO`-relative regardless of harness readiness.
5. **A combined cross-arm reproducibility manifest** covering both the N6 model hash and the baseline's existing config/code/input hashes together — still not assembled (Table row 12); the new harness's `OriginRunResult.provenance` field provides a place to put this once execution is authorized, but does not itself assemble it.

**Shortest next step:** the harness-structure sub-gap (Table row 2) is now closed and tested. The single next concrete action is for the project owner/governance authority to decide whether to seek a scoped, signed campaign-execution authorization analogous to `exp_three_arm_2024/AUTHORIZATION_RECORD.json` (Section 6 above) — naming the exact experiment, origin set, and arms — which this report does not and cannot grant. Only after that authorization exists should `execute_origin_dispatch_cell` be implemented for real.

---

## Final classification

**HARNESS_READY_FOR_REVIEW**

Rationale: the harness's structure, matching/leakage-prevention reuse, outcome-recording schema, aggregation logic, and execution gate are built, tested (26/26 passing against synthetic fixtures; 49/49 passing including the pre-existing `replay_harness` suite), and verified to touch no protected file and execute no dispatch. This is **not** a claim that the full N6-vs-baseline pipeline is ready to run: the per-origin dispatch-execution body remains an explicit, unimplemented `NotImplementedError` gap, campaign-execution authorization remains absent, and `epsilon_tol`/EVID-02/the combined manifest remain open exactly as `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` already stated. The harness is ready for a human reviewer to inspect and, separately, for the project owner/governance authority to decide whether and how to authorize the next, execution-bound phase of work.
