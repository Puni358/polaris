# POLARIS — Router/ECD Fail-Closed Implementation Report (ECD-01: A-iii / B-iii / M-A)

**Date:** 2026-10-18
**Nature of this document:** Implementation and test-evidence report for Phase 1 of the governing directive. This is the first pass that actually edits `system/control/router.py` and `system/control/ecd.py` to implement the project owner's already-recorded decisions (`POLARIS_MASTER_DECISION_REGISTER.md` item `ECD-01`, §28/§29). Phase 2 (a separate Option-D proposal, not implemented) is reported in the companion document `OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md`.

---

## 1. Exact files changed, and why

| File | Change | Why |
|---|---|---|
| `system/control/router.py` | Rewritten: removed the ungoverned `t_required_hours=6.0` default and the `current_state.last_observed_demand → bundle.demand.point[0] → 30000.0` critical-load substitution chain. Replaced with an explicit authorization contract read from `configs["ecd"]` and `configs["critical_load"]` (full schema in the file's own module docstring). | Implements Decision A = A-iii and Decision B = B-iii. This is the file the governance track (`HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md`, `N6_SYNTHETIC_END_TO_END_RUN_REPORT.md`) identified as the root cause: it never read any authorization signal and always synthesized a finite, positive value for both inputs. |
| `system/control/ecd.py` | One additive change: `critical_load=None` is now distinguished from a malformed-but-present value via a new `ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION` enum member and an early check in `evaluate()`. No existing validation branch, margin calculation, or classification rule was changed. Type hint widened from `Union[CriticalLoadTrajectory, float]` to `Optional[Union[...]]` to document the new legal input. | Implements Decision C = M-A's "explicit invalid-input status" requirement with a precise, honest label, rather than overloading the pre-existing generic `INVALID_CRITICAL_LOAD` status for two different conditions (missing authorization vs. a malformed value). |
| `system/tests/test_ecd01_fail_closed_implementation.py` | **New.** 16 focused tests covering all 9 directive-required scenarios. | Required test deliverable (Section 3 of the directive). |
| `tests/test_isolated_components.py` | Updated `setUp()`'s `self.config` to add explicit `t_required_authorized`/`critical_load` authorization keys. | Without this, all 3 of this file's router-dependent tests (which test genuine NORMAL/EMERGENCY/Option-D mechanics, not the fail-closed gate itself) would break. This is the directive's required test item 8 ("existing legitimate NORMAL and EMERGENCY paths still behave as specified when their required inputs are valid"), applied to this one small, directly-affected file. |
| `tests/test_gap19_ecd_option_d.py` | One hardcoded hash constant updated (`system/control/ecd.py`'s expected hash in `test_R_option_b_protected_behavior_remains_unchanged`), following the exact precedent already present in that same test for an earlier authorized `milp.py` hash bump. | `ecd.py`'s hash change is authorized and expected; the test's purpose (detect *future, unreviewed* drift) is preserved by updating the baseline to the new, reviewed value, not by deleting the check. |
| `POLARIS_MASTER_DECISION_REGISTER.md` / `.json` (+ mirrors) | `ECD-01.current_state`: `decided` → `implemented_fail_closed_pending_evidence_and_fixture_migration`; `owner_decision_record.implementation_authorized`/`.implementation_completed` → `true`; `.evidence_verified` stays `false`. New §29. Version `1.9.2` → `1.9.3`. | Genuinely evidence-justified: the code implementation described in this report is a fact, not a new decision — no numerical value, scope extension, or new authorization was invented. |

**Files explicitly NOT edited (verified, Section 6):** `system/optimization/implementations/gap19_highs_native.py`, `system/optimization/implementations/option_d.py`, `system/simulation/simulator.py`, `system/runtime/runner.py`, `system/orchestration/manifest.py`, `system/scripts/run_synthetic_critical_load_scenario.py`, all 4 frozen Candidate-N6 model/manifest assets, `winner: null`, the sealed 2025 blind partition, all `SAFETY_GATE_REGISTRY` entries, `replay_harness.py`'s campaign guard.

---

## 2. Exact behavior implemented for A-iii, B-iii, and M-A

**A-iii (`T_required`).** `router.py` no longer supplies a 6.0h (or any) default. It reads `configs["ecd"]["t_required_hours"]` and `configs["ecd"]["t_required_authorized"]`. If the authorization flag is not explicitly `True`, the `AuthorizedHorizon` payload built for `ecd.py` is marked `is_authenticated=False, is_authorized=False` — `ecd.py`'s own pre-existing validation (unchanged) then returns `UNKNOWN_INVALID` with `validity_status=UNAUTHORIZED_T_REQUIRED`. If the flag is `True` but the numeric value is missing/non-finite/non-positive, `ecd.py`'s own pre-existing numeric checks catch it (`MISSING_T_REQUIRED`). No numerical value — not 6h, not the 72h prototype, not any other — is invented or silently promoted anywhere in this path.

**B-iii (critical-load evidence).** `router.py` no longer reads `current_state.last_observed_demand`, `bundle.demand.point[0]`, or a hardcoded `30000.0` floor for this purpose. It reads `configs["critical_load"]["authorized"]`, `["evidence_id"]`, and `["authorized_critical_load_w"]`. All three must be present and the `evidence_id` must be a string prefixed `EVID-` (a real-station evidence record, per the register's own vocabulary) — a research-scoped id such as `CL-01` is explicitly rejected by this check. If any condition fails, `None` is passed to `ecd.py`, which fails closed via the new `MISSING_CRITICAL_LOAD_AUTHORIZATION` status. If authorized but the numeric value is malformed, `ecd.py`'s pre-existing numeric check catches it (`INVALID_CRITICAL_LOAD`). The synthetic CLI's `--critical-load-kw` input (surfaced only to `configs["critical_demand_w"]`, a separate, documented GAP19 optimizer input slot) is never read by this code path — confirmed by a dedicated regression test.

**M-A (invalid-input response).** Unchanged in structure, now actually reachable: `router.py`'s routing switch (`if NORMAL / elif EMERGENCY / else UNKNOWN_INVALID`) passes `OperatingMode.UNKNOWN_INVALID` straight through as `"UNKNOWN_INVALID"`, never remapping it to `"EMERGENCY"`. No stale/last-known-good value is substituted (no freshness policy exists or was added) and no fallback dispatch value is invented anywhere in this path.

---

## 3. How `UNKNOWN_INVALID` propagates through the tested execution path

`EMSControlRouter.evaluate_and_route()` returns `(assessment, "UNKNOWN_INVALID")` → `system/runtime/runner.py` (**read-only this pass, not edited**), lines ~149–167, has a pre-existing branch for exactly this route: it constructs a `FaultEvent` (`fault_class` = `assessment.validity_status.value`), sets `execution_status = "FAILED_TERMINATED"`, and `break`s the step loop — **before** any optimizer (`GAP19HighsNativeOptimizer` or `OptionDFallbackSolver`) is called and **before** `DigitalTwinSimulator.step()` is invoked. This was verified, not assumed: a new regression test (`test_runner_does_not_dispatch_or_advance_twin_on_unknown_invalid`) runs the real, unmodified `PolarisLocalRunner.run_pipeline()` with no authorization configured (its actual current default state) and asserts `completed_steps == 0`, `execution_status == "FAILED_TERMINATED"`, and that the simulator's `step()` was never called.

**No `runner.py` interface gap was found.** The directive asked me to stop and document a gap if safe propagation required editing `runner.py` — it does not. The existing, unmodified runner already fails safely.

---

## 4. Exact test commands and pass/fail results

```
$ .venv/bin/python3 -m pytest system/tests/test_ecd01_fail_closed_implementation.py -q
16 passed in 0.57s        # NEW focused suite — all 9 directive-required scenarios

$ .venv/bin/python3 -m pytest system/tests/test_ecd_core.py -q
7 passed in 0.11s          # direct ECD unit tests (bypass router) — unaffected, as expected

$ .venv/bin/python3 -m pytest tests/test_isolated_components.py -q
4 passed in 0.15s           # updated with explicit authorization fixtures

$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py -q
5 failed, 17 passed in 0.38s   # BEFORE: 22 passed, 0 failed (N6_SYNTHETIC_END_TO_END_RUN_REPORT.md §5)

$ .venv/bin/python3 -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -q
2 failed, 3 passed in 0.69s    # BEFORE: 5 passed, 0 failed (same source)

$ .venv/bin/python3 -m pytest system/tests/test_offline_runtime.py -q
11 failed, 24 passed in 9.24s  # BEFORE: 5 failed (pre-existing RT-01), 30 passed (same source)

$ .venv/bin/python3 -m pytest system/tests/test_n6_ia1_ia2_call_sequence_integration.py tests/test_gate10_milp_reference_fixture.py -q
13 passed in ...               # unaffected (both mock the router)
```

**Honest regression accounting — not bypassed.** Beyond the above, I ran every other pre-existing test file that calls `EMSControlRouter.evaluate_and_route()` with a real (non-mocked) `configs` dict, to give a complete picture:

| File | Total | Failed (after) | Failed (before, known) | New failures |
|---|---|---|---|---|
| `tests/test_research_route_mode_propagation.py` | 8 | 4 | 0 | 4 |
| `tests/test_gate08_ecd_routing_fixture.py` | 8 | 3 | 0 | 3 |
| `tests/test_ecd_option_d_integration.py` | 12 | 6 | 0 | 6 |
| `tests/test_gate05_synthetic_fixture.py` | 6 | 3 | 0 | 3 |
| `tests/test_gate06_rolling_twin_fixture.py` | 6 | 1 | 0 | 1 |
| `tests/test_gate07_fuel_propagation_fixture.py` | 15 | 1 | 0 | 1 |
| `tests/test_gate09_option_b_baseline_fixture.py` | 13 | 3 | 0 | 3 |
| `tests/test_gate11_option_d_fixture.py` | 7 | 3 | 0 | 3 |
| `tests/test_gap19_ecd_option_d.py` (+ `test_gap19_highs_native.py`) | 22 | 5 | 0 | 5 |
| `system/tests/test_rt01_rt02_failure_forensics_regressions.py` | 5 | 2 | 0 | 2 |
| `system/tests/test_offline_runtime.py` | 35 | 11 | 5 (RT-01) | 6 |
| **Total new regressions** | | | | **≈37** |

Also re-ran `tests/test_critical_load_11_6kw.py` (10 tests, 2 failed): these 2 failures (`test_4_ecd_receives_11_60_kw`, `test_6_no_future_truth_is_accessed`) are an `AttributeError` — they call `ConstantCriticalLoad.get_energy_required_wh()`, a method that does not exist on that class in **either** the before or after version of `ecd.py` (the real method is `get_cumulative_energy_wh`). **Pre-existing, unrelated to this change** — confirmed by reading the original `ecd.py` before editing it.

**Every one of the ≈37 new failures is a correct `UNKNOWN_INVALID`/`FAILED_TERMINATED` fail-closed outcome, not a crash, not a misclassification, and not a conservation/safety violation.** The root cause is uniform: none of these pre-existing fixtures supply the new `t_required_authorized` / `critical_load.authorized`+`evidence_id`+`authorized_critical_load_w` keys — they were written against, and implicitly validated, the exact substitution chain this decision removes. One illustrative example that demonstrates the mechanism precisely without a behavior change in substance: `tests/test_gate05_synthetic_fixture.py::test_03_unknown_invalid_pathway` already expected `UNKNOWN_INVALID`/`FAILED_TERMINATED`/no-simulator-step for a `t_required_hours=0.0` config — all three still hold exactly as before; the single assertion that now fails is `fault_class == "MISSING_T_REQUIRED"` vs. the new, more precise `"UNAUTHORIZED_T_REQUIRED"` (that config also lacks `t_required_authorized`, which is checked first). **I did not retrofit these ≈37 tests with authorization fixtures in this pass** — doing so for every file risked silently resolving the exact tension the directive warned against ("do not bypass or weaken the fail-closed behavior merely to keep ... a 'successful' green run") applied at test-suite scale, under time pressure, without being certain each fixture's demand/SOC/fuel values were re-validated for the resulting NORMAL/EMERGENCY boundary. This is listed as a concrete, actionable follow-up in Section 7.

---

## 5. Synthetic end-to-end outcome — honest, not bypassed

```
$ .venv/bin/python3 system/scripts/run_synthetic_critical_load_scenario.py --critical-load-kw 11.6
================================================================================
POLARIS -- SYNTHETIC CRITICAL-LOAD END-TO-END RUN
================================================================================
Critical load (synthetic, user-supplied): 11.6 kW
Steps requested: 24

Router decision:            UNKNOWN_INVALID
Optimizer executed:         None

OVERALL STATUS: BLOCKED_FAIL_CLOSED_UNKNOWN_INVALID
Full report written to: .../system/scripts/SYNTHETIC_CRITICAL_LOAD_RUN_REPORT.json
================================================================================
$ echo $?
1
```

**Before this pass** (per `N6_SYNTHETIC_END_TO_END_RUN_REPORT.md`, same command, same fixture): `route=NORMAL`, `optimizer_executed=GAP19HighsNativeOptimizer`, `constraint_status=OPTIMAL`, `status=SUCCESS_CLEAN`. **After this pass:** `route=UNKNOWN_INVALID`, `optimizer_executed=None`, `status=BLOCKED_FAIL_CLOSED_UNKNOWN_INVALID`, process exit code `1`. The JSON report's `failure_reason` is `"Target horizon payload is unauthenticated."` (`ecd.py`'s `UNAUTHORIZED_T_REQUIRED` path) — this CLI script never set `configs["ecd"]["t_required_authorized"]` or `configs["critical_load"]`, which is now correctly rejected rather than defaulted.

**This is the correct, intended, honestly-reportable outcome.** I did not weaken `router.py`/`ecd.py` to keep this CLI green, and I did not edit the CLI script to inject authorization keys it has no legitimate station evidence to back.

**One honest caveat on the CLI script itself (not edited — outside this pass's two-file authorization):** its own internal JSON narrative fields (e.g. `routing.router_internal_critical_load_source`, `routing.t_required_source`, which recompute and describe the *old*, pre-implementation substitution chain purely for explanatory text) are now stale — they still describe a mechanism that no longer governs the actual `route` value returned by the real `router.evaluate_and_route()` call directly above them in the same script. The `route`/`status` fields themselves are correct (computed by actually calling the real, now-fixed router); only the CLI's own explanatory prose about *why* is out of date. Flagged here, not fixed, per the explicit file-edit boundary.

---

## 6. Before/after integrity checks

```
                                                      BEFORE (hash)                                                      AFTER (hash)                           Changed?
system/control/router.py                             041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f    b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3   YES (authorized, expected)
system/control/ecd.py                                 d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23    091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db   YES (authorized, expected)
system/optimization/implementations/gap19_highs_native.py   fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737   (same)                                NO
system/optimization/implementations/option_d.py             15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad   (same)                                NO
system/simulation/simulator.py                               8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f   (same)                                NO
system/runtime/runner.py                                     6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10   (same)                                NO
system/orchestration/manifest.py                             7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35   (same)                                NO
```

All 4 frozen Candidate-N6 assets (`candidate_n6_model.joblib`, `candidate_n1_model.joblib`, `CANDIDATE_N_MANIFEST.json`, `ensemble_parameters.json`) re-verified against `run_n6_closed_loop_simulation.py`'s own `PROTECTED_ASSETS` manifest, both via that script's own internal check (runs on every CLI invocation, Section 5) and independently before/after this pass — all 4 unchanged. `POLARIS_MASTER_DECISION_REGISTER.md`'s `winner: null`, all 4 `SAFETY_GATE_REGISTRY` entries (`authorized: False`), the sealed 2025 blind partition, and `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard were not accessed, touched, or executed. `git status --short` at the end of this pass shows only the files listed in Section 1 as modified/created — nothing staged, committed, or pushed.

---

## 7. Remaining blockers

1. **Real-station `T_required` evidence** — still `NOT_ESTABLISHED`. No resupply/recovery/logistics evidence exists anywhere in the repository. This pass implements the *policy* (fail closed absent authorization); it does not and cannot manufacture the missing evidence.
2. **Real-station critical-load evidence (`EVID-02`)** — still unavailable/unverified. Same reasoning.
3. **Orchestration/dispatch-level specification for `UNKNOWN_INVALID`, beyond router.py/ecd.py's own classification** — M-A specifies only that the ECD/router must emit an explicit invalid-input status and refuse to classify; it does not specify (and this pass does not invent) what the broader EMS/dispatch system should do operationally with that status beyond what `runner.py` already, independently does (fail-terminate the local offline-runtime loop, Section 3). No real-station deployment context exists in this repository to specify further, and none was invented.
4. **No `runner.py` interface gap exists** — contrary to what might have been expected going in, the existing, unmodified `runner.py` already handles `UNKNOWN_INVALID` safely. Nothing to fix, nothing edited.
5. **≈37 pre-existing test fixtures (Section 4) now correctly fail closed** because they predate this authorization contract. Recommended, explicitly NOT done in this pass: a dedicated follow-up pass to add `configs["ecd"]["t_required_authorized"]`/`configs["critical_load"]` fixtures to each, re-deriving each fixture's intended NORMAL/EMERGENCY boundary values (most will need a specific `authorized_critical_load_w` chosen per-test, not a single constant) rather than mechanically stamping one value everywhere.
6. **The synthetic CLI's (`run_synthetic_critical_load_scenario.py`) own explanatory JSON/narrative fields are stale** (Section 5) — not fixed, outside this pass's two-file authorization.
7. **Campaign/replay authorization** remains locked (`CampaignExecutionNotAuthorizedError`, unconditional) — untouched, unrelated to this pass.
8. **`CL-01`'s 11.6 kW value** remains scoped `research` — not extended, not used as routing evidence anywhere in the implementation (confirmed by a dedicated regression test asserting it is explicitly rejected if someone tried to cite it as `evidence_id`).

---

## 8. Phase 2 — Option-D diesel-floor repair

Not implemented, not authorized by this pass. See the companion document `OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md` (root + `N6_REMEDIATION_REPORTS/` mirror) for the exact violated energy-balance equation, the minimal proposed code change, the tests needed to prove conservation, and the exact authorization that would be required before any edit to `system/optimization/implementations/option_d.py`.

---

**PASS COMPLETE.** `router.py`/`ecd.py` now implement A-iii/B-iii/M-A. The synthetic E2E CLI and ≈37 pre-existing tests now correctly fail closed; this is reported as the intended consequence, not bypassed. 16/16 new focused tests pass. All other protected files and frozen assets verified byte-identical before/after. Nothing staged, committed, or pushed. `ECD-01` is **not closed** — real evidence, the broader orchestration specification, and fixture migration remain open.
