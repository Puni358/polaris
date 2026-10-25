# POLARIS — Bounded Correctness Fixes: Safety Unknowns and Failure-Status Propagation

**Date:** 2026-10-17
**Scope:** Exactly the four bounded correctness fixes authorized by the project owner's
scoped protocol, implementing findings documented in
`SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` Section 5 (items 1-3) and Section 1/4 (item 2a).
No safety halting/fallback behavior was implemented. No files were staged or committed.

---

## 1. Exact changed files

| File | Change |
|---|---|
| `system/safety/reserve_policy_guard.py` | `SafetyEvaluationResult.reserve_shortfall_total_wh` changed from `float` to `Optional[float]`; `evaluate_dispatch_safety()` now returns `None` (not `0.0`) when `plan.get("reserve_shortfall")` is absent. Present values are computed exactly as before. |
| `system/orchestration/worker.py` | (a) `_evaluate_step_dispatch_safety`'s "unavailable" branch (neither `unmet_essential` nor `unmet_load` present) now sets `critical_unmet_wh = None`, reported to callers as `"UNKNOWN_NOT_VERIFIED"` (mirroring the existing `reserve_shortfall_wh` pattern), instead of `0.0`. The `unmet_load` read feeding the guard's `safety_plan` dict was changed from a hard subscript to a `.get()`-based read so this branch is actually reachable rather than raising `KeyError` first. The `optimal_but_unsafe` boolean and the `unmet_critical_load_wh` integrity counter now guard against this value being `None`/non-numeric rather than assuming it is always a float. (b) The Cell B `router.evaluate_and_route` / `optimizer.optimize` / Gate-02 relaxation re-solve call sequence is now wrapped in `try/except Exception`, mirroring the equivalent pattern already present in `system/runtime/runner.py`. An exception is converted into `status = "FAILED_OPTIMIZATION_EXCEPTION"` plus a new `worker_failure_diagnostics` dict (`cycle_index`, `exception_type`, `exception_message`, `traceback`) that is persisted in both `trajectory_records.json` and the worker's returned result dict — never relabeled as `OPTIMIZATION_INFEASIBLE`. The existing post-loop aggregation/persistence code (unconditional after the loop, same as for `INTERRUPTED`/`BLOCKED_INFEASIBLE`) already guarantees reliable cleanup/persistence on this new failure path with no additional change needed. Added `import traceback`. |
| `system/orchestration/master.py` | Extracted the campaign-status decision into a new pure `CampaignMaster.compute_run_status(interrupted, workers_info)` staticmethod. It now returns `"INTERRUPTED"` if `self.interrupted`, else `"FAILED_WORKER_EXIT"` if any `workers_info[...]["status"]` starts with `"FAILED_EXIT_"`, else `"COMPLETED"` — replacing the old `"COMPLETED" if not self.interrupted else "INTERRUPTED"` logic that never inspected `workers_info`. `CAMPAIGN_STATUS.json` now also includes a `"failed_worker_cells"` list. |
| `system/tests/test_reserve_policy_guard.py` | Added `TestReserveShortfallTotalStaysUnknownWhenAbsent` (3 tests: missing → `None`, present values numerically unchanged including the present-all-zero case staying a verified `0.0`, missing does not raise or falsely report a violation). |
| `system/tests/test_worker_safety_wiring.py` | Added `TestWorkerCriticalUnmetUnavailableStaysUnknown` (1 test) and `TestWorkerOptimizerExceptionHandling` (3 tests: structured failure + persistence, worker never raises out of `execute()`, interruption/success stay uncontaminated by failure diagnostics). |
| `system/tests/test_master_run_status.py` | New file. 7 focused tests of `compute_run_status` covering: all-completed, crashed-worker (the exact audit-documented defect), interruption precedence, both-present, multiple failures, a still-`RUNNING` worker not being misread as failed, and the empty-list case. |

No other files were modified.

---

## 2. Focused test results

```
python3 -m pytest system/tests/test_reserve_policy_guard.py \
  system/tests/test_worker_safety_wiring.py \
  system/tests/test_master_run_status.py \
  system/tests/test_evaluator_safety_wiring.py -q

58 passed in 0.86s
```

Breakdown: `test_reserve_policy_guard.py` 27 tests (24 pre-existing + 3 new), `test_worker_safety_wiring.py` 10 tests (6 pre-existing + 4 new), `test_master_run_status.py` 7 new tests, `test_evaluator_safety_wiring.py` 12 pre-existing tests (unchanged — evaluator.py was not touched; its two call sites already independently guarded against the guard's prior `0.0` default, confirmed by direct re-reading before any edit was made, so this file needed no change and its tests remain a regression check that nothing was disturbed).

No campaign, no dispatch run, no HiGHS solve, and no network or sealed-data access occurred in this verification. Only the four target files' own existing/added unit tests were run, per the "run only focused unit tests" instruction.

## 3. Pre-existing failures

None observed. All 58 tests in the four relevant test files pass, both before this pass's new tests were added (54 pre-existing tests, re-run to confirm no latent failures) and after (58 total).

## 4. Protected files — confirmed unchanged

`system/orchestration/manifest.py::PROTECTED_FILES` (read, not edited) lists exactly:
`system/optimization/implementations/gap19_highs_native.py`, `system/optimization/implementations/option_d.py`,
`system/control/ecd.py`, `system/control/router.py`, `system/simulation/simulator.py`, `system/runtime/runner.py`.

SHA-256 of each, taken after all edits in this pass:

```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  runner.py
```

`runner.py` was opened only to **read** its existing try/except pattern (lines ~148-181) as the model to mirror in `worker.py`; it was never edited. None of the six protected files were written to. No GAP19 formulation, constraint, objective priority, or solver behavior was modified. No Stage 8.1/N6 artifact, manifest, calibration, production default, or `winner: null` governance state was touched. No model training/tuning/refitting, no campaign, no historical replay, no endurance test, no blind-data access, and no live service call occurred at any point in this pass.

## 5. Scope discipline confirmed

- `worker.py`'s core `execute()` loop still sets `status` from exactly the same category of events as before (`COMPLETED` default, `INTERRUPTED`, `FAILED_UNKNOWN_INVALID`, `BLOCKED_INFEASIBLE`) plus the one newly authorized addition, `FAILED_OPTIMIZATION_EXCEPTION`. No line sets `status` from `step_safety`, `hard_soc_violation`, or `optimal_but_unsafe` — that remains exactly as unauthorized and untouched as before this pass.
- No reserve-shortfall threshold, solar-credit cap, safety-gate authorization, fallback action, or physical safe-response behavior was introduced. `compute_bounded_solar_credit`, `SAFETY_GATE_REGISTRY` (all `authorized=False`), and `reserve_shortfall_authorization_wh=None` call sites are byte-for-byte unchanged.
- Total unmet load is still never reinterpreted as verified critical unmet load — the existing `"fallback_total_unmet_load"` / `"FALLBACK_TO_TOTAL_UNMET_LOAD: ... OVER-COUNTS ..."` labeling in `worker.py`/`evaluator.py` is unchanged.
- `master.py`'s new `FAILED_WORKER_EXIT` status is a status-reporting correction only — it does not stop, retry, or alter any worker process; it only changes what gets written to `CAMPAIGN_STATUS.json` after the existing polling loop has already finished (or been interrupted).
- Nothing was staged or committed: `git status` shows only the same two pre-existing staged entries (`A POLARIS_MASTER_HANDOFF.md`, `A requirements.txt`) that were staged before this session started; every file this pass touched or created (`system/safety/reserve_policy_guard.py`, `system/orchestration/worker.py`, `system/orchestration/master.py`, the three test files, and this report) appears only among the pre-existing large set of untracked files, consistent with the repository having no commits at all.

---

BOUNDED CORRECTNESS FIXES COMPLETE — SAFETY HALT POLICY STILL REQUIRES EXPLICIT AUTHORIZATION
