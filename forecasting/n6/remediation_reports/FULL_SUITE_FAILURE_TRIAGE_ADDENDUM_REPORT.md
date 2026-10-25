# POLARIS — Full-Suite Failure Triage Addendum: Report

**Date:** 2026-10-18
**Nature of this document:** Triage-and-fix report, following the evidence-first methodology required by the governing directive ("POLARIS — Full-Suite Failure Triage Addendum"). This is the fifteenth pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md` (thirteenth pass) and `OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md` (fourteenth pass). It is mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Register impact:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json`, Section 31, v1.9.4 → v1.9.5 (narrative only — no canonical item's `current_state` changed).

---

## 1. Full failure inventory

**Baseline reported by the project owner:** `66 failed, 791 passed, 6 errors, 20 warnings in 1189.53s` (exit code 0 was a `tail`-pipe artifact, not a passing run).

**Evidence-first finding (required first action):** no complete raw traceback log from that exact run was found anywhere in the repository, bash history, or terminal scrollback. The only pre-existing evidence was (a) the pytest `.pytest_cache/v/cache/lastfailed` file (88 node IDs — a cumulative snapshot mixing stale entries from the original run with the thirteenth/fourteenth passes' own later, narrower re-runs, not a clean 66+6=72 list) and (b) the prior reports' own documented ≈37-test router/ECD regression list and 18/17-failure Option-D accounting. **This limitation is recorded explicitly, not papered over** — the exact 66+6 list as it existed at the moment the owner ran it could not be reconstructed byte-for-byte. Per the directive, the full suite was **not** re-run blind to manufacture a substitute list; instead, every file referenced by the cache and by the prior reports was re-run narrowly, with full tracebacks, to build an evidence-based current inventory, and a single full-suite confirmation run was reserved for the end (Section 10).

**Current, directly-reproduced inventory (post-fix), from the actual final run — `pytest tests/ system/tests/`, 863 tests collected (exactly matching the owner's original total of 66+791+6=863):**

```
7 failed, 856 passed, 20 warnings in 1868.45s (0:31:08)
```

1. `tests/test_critical_load_11_6kw.py::test_4_ecd_receives_11_60_kw`
2. `tests/test_critical_load_11_6kw.py::test_6_no_future_truth_is_accessed`
3. `system/tests/test_n6_live_operational_execution.py::TestN6LiveOperationalExecution::test_05_end_to_end_operational_execution_and_ebr`
4. `system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_cumulative_physical_conservation_168h`
5. `system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_long_duration_closed_loop_endurance_168h`
6. `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting::test_demo_scenario_step0_routes_emergency_not_normal`
7. `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel::test_full_pipeline_never_reaches_milp_for_demo_scenario`

(Note: `pytest`'s own exit code for this run is `1`, because 7 tests failed — this is the correct, expected non-zero code, not an error in the run itself; flagging this explicitly per the directive's own warning about misreading exit codes.)

**Separately, outside this command's scope** (not part of `tests/`/`system/tests/`, so not counted in the 7/856/863 above, but triaged and confirmed unchanged): `forecasting/solar_branch_01/tests/` — **14 failed, 50 passed** (64 tests), entirely unrelated to router/ECD/Option-D (Section 3).

---

## 2. Root-cause groups, with traceback evidence

### Group A — Router/ECD authorization-fixture drift (the overwhelming majority; now fixed)

**Mechanism:** every pre-existing test file that calls `EMSControlRouter.evaluate_and_route()` with a real `configs` dict, without supplying the thirteenth pass's new authorization keys (`configs["ecd"]["t_required_authorized"]`; `configs["critical_load"]["authorized"/"evidence_id"/"authorized_critical_load_w"]`), now correctly fails closed to `UNKNOWN_INVALID` instead of reaching the genuine `NORMAL`/`EMERGENCY` mechanics the test was written to exercise. This is the exact, intended, already-authorized consequence of `ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md` (thirteenth pass) — not a bug.

Representative traceback (`tests/test_planner_cf_closed_loop_synthetic.py`, all 6 errors, one shared cause):
```
tests/test_planner_cf_closed_loop_synthetic.py:55: in pc_control_origin
    hourly, executed = arm.run_origin(999, make_initial_state(FAKE_T0), weather, rs, rw, rd, rts)
experiments/stage4_planner_cf_consistency_2025/planner_cf_campaign_runner.py:136: in run_origin
    raise RuntimeError(f"{self.arm} optimizer failed at step {step}: {plan.constraint_status}")
RuntimeError: PC-Control optimizer failed at step 0: DEGRADED_FAILSAFE_UNKNOWN_INVALID
```
Representative traceback (`system/tests/test_v2_telemetry.py`, the two priority tests):
```
AssertionError: assert 'FAILED_TERMINATED' == 'SUCCESS_CLEAN'          # test_gov_1..4,7,8,9,10
AssertionError: assert 'OPTIMIZATION_RUNTIME_FAILURE' in 'FAIL_CLOSED_UNKNOWN_INVALID: ...'   # test_gov_5
AssertionError: assert 'FAILED_STATE_VIOLATION' in 'FAIL_CLOSED_UNKNOWN_INVALID: ...'          # test_gov_6
```
Files affected (confirmed by direct re-run, fixed — Section 5): `tests/test_planner_cf_closed_loop_synthetic.py` (6 errors), `system/tests/test_v2_telemetry.py` (8 of 16), `tests/test_gate05_synthetic_fixture.py` (3), `tests/test_gate06_rolling_twin_fixture.py` (1), `tests/test_gate07_fuel_propagation_fixture.py` (1), `tests/test_gate08_ecd_routing_fixture.py` (3), `tests/test_gate09_option_b_baseline_fixture.py` (3), `tests/test_ecd_option_d_integration.py` (3 of 6 — the other 3 are Group B), `tests/test_gap19_ecd_option_d.py` (3 of 4 — the 4th is Group B), `tests/test_research_route_mode_propagation.py` (4), `system/tests/test_offline_runtime.py` (7 of 9 — the other 2 became Group D), `system/tests/test_closed_loop_causal_nwp_runner.py` (9), `system/tests/test_research_critical_demand_adapter.py` (1), `system/tests/test_s81_e2e_integration.py` (3), `tests/test_forensic_planned_capture.py` (1), `tests/test_gate11_option_d_fixture.py::test_02` (1 of 2 — the other is Group B).

### Group B — Stale-but-already-authorized hash/label/numeric pins (now fixed)

- `tests/test_gate11_option_d_fixture.py::test_01_option_d_sha256_unmodified` and `tests/test_reactive_hybrid_a2_baseline.py::test_20_protected_component_hashes_unchanged` pinned `option_d.py`'s hash as `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` — a baseline that predates even the fourteenth pass's own recorded "before" value (`15179e83e1...`). The latter test's `PROTECTED_HASHES` dict also carried stale `ecd.py`/`router.py` hashes (from before the thirteenth pass) and a `runner.py` hash (`723635dad0b8...`) that never matched any pass's own recorded value for that file in any report.
  ```
  AssertionError: 'cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511' != '78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12'
  : Protected file modified: system/optimization/implementations/option_d.py
  ```
- `tests/test_gate05_synthetic_fixture.py::test_03_unknown_invalid_pathway` expected the stale `fault_class` label `"MISSING_T_REQUIRED"` for a condition (`t_required_hours=0.0`, no authorization) where `ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md` §4 already documented the new, correct label is `"UNAUTHORIZED_T_REQUIRED"` (the authorization check now runs before the numeric check).
- `tests/test_gap19_ecd_option_d.py::test_F_ecd_receives_current_fuel_not_initial` expected `diesel_endurance_hours == 0.4` — computed against **full observed demand** (30 kW), the pre-B-iii substitution semantics. B-iii's own intent is that this value is computed against the router's **authorized critical load**, not full demand; with this fixture's authorized value (5000 W), the correct figure is `0.8h`.
- `tests/test_ecd_option_d_integration.py::test_L/M/P` — `AttributeError: 'DummyBundle' object has no attribute 'solar_generation'`. These three local `DummyBundle` test helper classes predate the earlier, separately-authorized RT-01 mechanism-2 fix (`option_d.py:88`, `bundle.solar_irradiance` → `bundle.solar_generation`) and never gained the corresponding attribute.

### Group C — Genuinely unrelated, pre-existing, out-of-scope (left failing, not fixed)

- `tests/test_critical_load_11_6kw.py::test_4/test_6` — `AttributeError: 'ConstantCriticalLoad' object has no attribute 'get_energy_required_wh'`. The real method on this class (confirmed by reading `system/control/ecd.py`) is `get_cumulative_energy_wh` — this is a test-code method-name typo that never worked, unrelated to any pass's changes.
- `forecasting/solar_branch_01/tests/` — 14 failures: 1 frozen-component SHA mismatch (`test_model_identity_and_frozen_component_shas`) and 13 `ModelGovernanceError: Missing or invalid 'wind_generation' forecast in runtime_context. Non-solar forecasts must be inherited from Control.` — Branch-01's own internal forecast-governance contract, with no call to `EMSControlRouter`/`ecd.py` anywhere in the failing path. Outside this pass's router/ECD/Option-D scope; not touched.
- `system/tests/test_n6_live_operational_execution.py::test_05` —
  ```
  assert route == "NORMAL", f"Expected NORMAL route, got {route} ({assessment.failure_reason})"
  AssertionError: Expected NORMAL route, got UNKNOWN_INVALID (Target horizon payload is unauthenticated.)
  ```
  fails inside `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/n6_operational_pipeline.py` — a non-test, Stage-8.1-adjacent **research script** (not `router.py`/`ecd.py`) that builds its own `configs_gap19` dict internally from raw YAML with no authorization and no test-side injection point. Editing it is outside "fixture migration edits go to the relevant existing test files"; flagged for owner decision (Section 3/11).

### Group D — A previously-hidden finding, traced to an already-documented, separate gap (left failing, not fixed)

`system/tests/test_offline_runtime.py::test_cumulative_physical_conservation_168h` and `::test_long_duration_closed_loop_endurance_168h`. Once the router/ECD fixture migration let these 168h synthetic-endurance-scenario tests finally reach the real MILP optimizer for the first time, they still show `system_reliability_pct = 90.04%` (not 100%) and `unmet_critical_load_kwh = 553.84` (not 0.0) over the full 168-hour run. Direct inspection of the evaluation engine's own output:
```
"critical_unmet_total_wh falls back to TOTAL unmet_load because 'unmet_essential' was not present on
 this plan -- this OVER-COUNTS non-critical shortfalls and is a known evaluator gap (see
 N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md Section 4)."
```
`unmet_critical_load_kwh` is a **known-mislabeled total-unmet-load figure** (documented in a prior report, predating this pass) — not a critical-load safety violation and not a new router/ECD/Option-D defect. See Section 8 for the full conservation/reliability evidence and Section 11 for why this does not reopen RT-01.

### Group E — Stale / non-reproducing cache entries (confirmed, not real failures)

`tests/test_global_lower_bound.py::test_10_tiny_instance_matches_brute_force_enumeration` and `system/tests/test_n6_ia1_ia2_call_sequence_integration.py::test_21_unshimmed_forecast_adapter_fails_closed_at_step_zero` appear in the `lastfailed` cache but pass cleanly on direct, fresh re-run (confirmed individually and as part of their full files). Recorded as non-reproducing, not silently dropped from this report.

### Group F — Deliberately left failing, flagged for owner decision (not fixed)

`system/tests/test_rt01_rt02_failure_forensics_regressions.py::test_demo_scenario_step0_routes_emergency_not_normal` and `::test_full_pipeline_never_reaches_milp_for_demo_scenario`. See Section 3 for the full reasoning — these are forensic regression pins for the full-demand-as-critical-load substitution mechanism that the thirteenth pass's A-iii/B-iii implementation **removed from the code entirely**, not merely corrected the margin for. Calling the router with zero authorization now always returns `UNKNOWN_INVALID` before any critical-load/margin computation runs at all, so the pin's original `EMERGENCY` (and, in the companion test, `OPTION_D_FALLBACK`) expectation is now structurally unreachable — regardless of SOC, demand, or fuel.

---

## 3. Classification of all failures: pre-existing/expected/fixture-drift/genuine-regression/unclassified

| Classification | Items | Count |
|---|---|---|
| **Fixed this pass (Group A: authorization-fixture migration)** | 17 test files, restoring ~56 tests to genuine coverage | 56 |
| **Fixed this pass (Group B: stale hash/label/numeric pins)** | 2 hash pins, 1 label, 1 numeric value, 3 `DummyBundle` attributes (also counted toward Group A/B overlap in some files) | 7 |
| **Pre-existing, unrelated, out-of-scope — left failing, not fixed** | `test_critical_load_11_6kw.py` (2), `forecasting/solar_branch_01/` (14), `test_n6_live_operational_execution.py::test_05` (1) | 17 |
| **Previously-hidden finding, traced to an already-documented separate evaluator gap — left failing, not fixed** | `test_offline_runtime.py`'s two 168h tests | 2 |
| **Non-reproducing / stale cache entries** | `test_global_lower_bound.py::test_10`, `test_n6_ia1_ia2_call_sequence_integration.py::test_21` | 2 |
| **Deliberately left failing, forensic-pin owner-decision item** | `test_rt01_rt02_failure_forensics_regressions.py`'s two tests | 2 |
| **Unclassified / no evidence found** | none | 0 |

Every failure this pass touched or encountered has a recorded, evidence-backed classification. None is "unclassified pending evidence."

---

## 4. Exact files changed, and before/after hashes for protected files

**Files edited (17, all test files — zero production files):**
`system/tests/test_v2_telemetry.py`, `tests/test_planner_cf_closed_loop_synthetic.py`, `tests/test_gate11_option_d_fixture.py`, `tests/test_reactive_hybrid_a2_baseline.py`, `tests/test_gate05_synthetic_fixture.py`, `tests/test_gate06_rolling_twin_fixture.py`, `tests/test_gate07_fuel_propagation_fixture.py`, `tests/test_gate08_ecd_routing_fixture.py`, `tests/test_gate09_option_b_baseline_fixture.py`, `tests/test_ecd_option_d_integration.py`, `tests/test_gap19_ecd_option_d.py`, `tests/test_research_route_mode_propagation.py`, `system/tests/test_offline_runtime.py`, `system/tests/test_closed_loop_causal_nwp_runner.py`, `system/tests/test_research_critical_demand_adapter.py`, `system/tests/test_s81_e2e_integration.py`, `tests/test_forensic_planned_capture.py`.

Every added authorization fixture follows one convention, established by the thirteenth pass's own `tests/test_isolated_components.py` edit: `configs["ecd"] = {"t_required_hours": <N>, "t_required_authorized": True}` and `configs["critical_load"] = {"authorized": True, "evidence_id": "EVID-TEST-<FILE>", "authorized_critical_load_w": <value>}`, always commented as a **synthetic test-fixture value, not a real-station evidence record**. Every deliberately-unauthorized fail-closed test path within each edited file (e.g. `test_06_boundary_isolation_unknown_invalid_and_milp_infeasible` in `test_gate11_option_d_fixture.py`, `test_I_unknown_invalid_routing` in `test_ecd_option_d_integration.py`, `test_I_unknown_invalid_not_silently_routed` in `test_gap19_ecd_option_d.py`, `test_03_unknown_invalid_pathway`'s route/state-advancement assertions in `test_gate05_synthetic_fixture.py`) was individually identified and left untouched.

**Protected-file hashes (all 7), before this pass's first edit and after its last edit:**

| File | Hash (unchanged throughout this pass) |
|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` |

All 7 confirmed byte-identical before this pass's first edit and after its last edit (re-hashed independently at both ends). `winner: null`, the sealed 2025 blind partition, frozen Stage 8.1/N6 artifacts, and the campaign lock were not accessed or touched. Nothing staged, committed, or pushed.

`POLARIS_MASTER_DECISION_REGISTER.md`/`.json` updated: v1.9.4 → v1.9.5, new Section 31 (narrative only — no canonical item's `current_state` changed), mirrored to `N6_REMEDIATION_REPORTS/`.

---

## 5. Focused test results after each fix

| File | Before | After |
|---|---|---|
| `system/tests/test_v2_telemetry.py` | 8 failed, 8 passed | **16 passed** |
| `tests/test_planner_cf_closed_loop_synthetic.py` | 6 errors | **6 passed** |
| `tests/test_gate11_option_d_fixture.py` | 2 failed, 5 passed | **7 passed** |
| `tests/test_reactive_hybrid_a2_baseline.py` | 1 failed, 19 passed | **20 passed** |
| `tests/test_gate05_synthetic_fixture.py` | 3 failed, 3 passed | **6 passed** |
| `tests/test_gate06_rolling_twin_fixture.py` | 1 failed, 5 passed | **6 passed** |
| `tests/test_gate07_fuel_propagation_fixture.py` | 1 failed, 14 passed | **15 passed** |
| `tests/test_gate08_ecd_routing_fixture.py` | 3 failed, 5 passed | **8 passed** |
| `tests/test_gate09_option_b_baseline_fixture.py` | 3 failed, 10 passed | **13 passed** |
| `tests/test_ecd_option_d_integration.py` | 6 failed, 6 passed | **12 passed** |
| `tests/test_gap19_ecd_option_d.py` + `test_gap19_highs_native.py` | 4 failed, 18 passed | **22 passed** |
| `tests/test_research_route_mode_propagation.py` | 4 failed, 4 passed | **8 passed** |
| `system/tests/test_offline_runtime.py` | 9 failed, 26 passed | **33 passed, 2 failed** (Group D, unrelated to this fix) |
| `system/tests/test_closed_loop_causal_nwp_runner.py` | 9 failed, 6 passed | **15 passed** |
| `system/tests/test_research_critical_demand_adapter.py` | 1 failed, 3 passed | **4 passed** |
| `system/tests/test_s81_e2e_integration.py` | 3 failed, 11 passed | **14 passed** |
| `tests/test_forensic_planned_capture.py` | 1 failed, 19 passed | **20 passed** |

Every fix was verified immediately after being applied, before moving to the next file (narrowest-reproducing-test-first, per the directive).

---

## 6. Does synthetic planner execution reach the optimizer and complete the expected steps?

**Two distinct synthetic entry points, with two different current answers:**

1. **`tests/test_planner_cf_closed_loop_synthetic.py` (the Planner-CF v1 closed-loop test suite) — YES, now reaches the optimizer and completes fully.** After the fixture migration (Section 2, Group A), the fake-origin closed-loop run genuinely executes `PlannerCFV1Optimizer.optimize()` at every one of 24 steps, produces exactly 24 hourly rows and 24 executed-hour records, and passes every invariant the suite checks: `g6_busbar_soc_fuel` (bus-bar/SOC/fuel reconciliation), `g4_optimizer_status`/`g10_route_propagation` (all steps solve `OPTIMAL`/`FEASIBLE`, and the router's route is genuinely propagated into the optimizer's planning state), `g2_priority_inversion`/`g3_critical_infeasibility` (executed-record invariants), the `E_t` start-of-hour realized-energy identity, and `critical_served_first <= critical_demand` at every hour. This is a real, non-mocked execution — confirmed by re-running it standalone (`6 passed`) immediately after the fix, not assumed from the full-suite tally.

2. **`system/scripts/run_synthetic_critical_load_scenario.py` (the standalone synthetic CLI) — NO, still correctly blocked.** This is a CLI script, not a test file, so it is outside this pass's fixture-migration scope (the task's own boundary: "Fixture migration edits go to the relevant existing test files"). Re-run directly this pass, unmodified:
   ```
   Router decision:            UNKNOWN_INVALID
   Optimizer executed:         None
   OVERALL STATUS: BLOCKED_FAIL_CLOSED_UNKNOWN_INVALID
   ```
   This is the correct, intended, already-reported (thirteenth-pass) outcome — no real `T_required`/critical-load evidence exists for this script to supply, and it was not given a synthetic authorization override, by design.

---

## 7. Were fresh dispatch artifacts generated?

**Yes, for every scenario the fixture migration now reaches.** `system/tests/test_offline_runtime.py`'s and `system/tests/test_s81_e2e_integration.py`'s `run_pipeline()` calls (now authorized) regenerate `system/artifacts/latest_dispatch_plan.json` on every invocation that reaches `NORMAL`/`EMERGENCY` — confirmed by the fact that `test_cumulative_physical_conservation_168h` and `test_long_duration_closed_loop_endurance_168h` now report **genuinely computed, varying** `system_reliability_pct`/`unmet_critical_load_kwh` values (90.04%/553.84, Section 8) rather than the stale `4658.729999999996` Wh residual the fourteenth pass's report recorded when the pipeline could not reach the optimizer at all for these scenarios. The two `test_rt01_rt02_failure_forensics_regressions.py` tests that were deliberately left unfixed (Group F) still read a **stale, pre-fix artifact** for the unmodified `demo_scenario.json`/zero-authorization case, exactly as the fourteenth pass's report already documented — this is unchanged by this pass, since fixing those two specific tests' configs was explicitly judged out of this pass's authority (Section 11).

---

## 8. Independent conservation, SOC, critical-load, and fuel-accounting results

From the now-reachable 168h synthetic-endurance-scenario run (`system/tests/test_offline_runtime.py`, authorized test fixture, real MILP dispatch, 168 real timesteps):

- **Timesteps executed:** 168/168 (`test_long_duration_closed_loop_endurance_168h`, `test_solver_computational_stability_168h` — both pass).
- **Per-timestep bus-bar/conservation audit:** passes at the per-step level (`test_per_timestep_conservation_audit`'s own demo_scenario-based check and the 168h file's other conservation checks all pass except the two below).
- **System reliability:** `90.04%` (not 100%) over the full 168h run — **not** a conservation violation; this is the MILP's own real dispatch outcome under the scenario's own stress conditions.
- **Unmet "critical" load:** `553.84 kWh` over 168h, reported via the `unmet_critical_load_kwh` field — but this field is **independently confirmed, via the evaluator's own embedded warning string**, to be a mislabeled **total**-unmet-load figure (`"critical_unmet_total_wh falls back to TOTAL unmet_load because 'unmet_essential' was not present on this plan... this OVER-COUNTS non-critical shortfalls and is a known evaluator gap"`), not a measurement that critical load specifically went unserved. No genuine critical-load-specific unmet figure is available from this evaluator today (a separate, already-documented gap — `N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` §4).
- **SOC bounds:** respected throughout (confirmed by `test_i_soc_fuel_bounds`-equivalent checks across the fixed files; no SOC violation observed in any of the 33 now-passing `test_offline_runtime.py` tests).
- **Fuel accounting:** deterministic and consistent across repeated runs (`test_long_run_deterministic_replay_168h` passes — bit-for-bit identical `total_diesel_fuel_liters`/`system_reliability_pct` across two independent 168h runs).
- **Renewable utilization:** `69.37%` for the 168h scenario (observed; no assertion failure on this field).

None of this is attributable to router.py, ecd.py, or option_d.py — all three protected files are confirmed byte-identical throughout this pass (Section 4).

---

## 9. Confirmation that missing/invalid authorization still fails closed

Explicitly re-verified, for every file this pass edited, that the deliberately-unauthorized paths still correctly fail closed:

- `tests/test_gate11_option_d_fixture.py::test_06_boundary_isolation_unknown_invalid_and_milp_infeasible` — unauthorized `t_required_hours=0.0` config still produces `completed_steps == 0`, `option_d_called == False`. **Pass.**
- `tests/test_ecd_option_d_integration.py::test_I_unknown_invalid_routing` — invalid negative SOC still produces `route == "UNKNOWN_INVALID"`. **Pass.**
- `tests/test_gap19_ecd_option_d.py::test_I_unknown_invalid_not_silently_routed` — NaN SOC still produces `OperatingMode.UNKNOWN_INVALID`/`route == "UNKNOWN_INVALID"`. **Pass.**
- `tests/test_gate05_synthetic_fixture.py::test_03_unknown_invalid_pathway` — zero-authorization `bad_configs`/`runner.configs` still produces `route == "UNKNOWN_INVALID"`, `completed_steps == 0`, `execution_status == "FAILED_TERMINATED"`, `state_advanced == False` (only the `fault_class` label itself was corrected, Section 2 Group B — the fail-closed *behavior* is unchanged and still asserted). **Pass.**
- `system/scripts/run_synthetic_critical_load_scenario.py` — unmodified, still `BLOCKED_FAIL_CLOSED_UNKNOWN_INVALID` (Section 6). **Confirmed.**
- `system/tests/test_closed_loop_causal_nwp_runner.py::test_n_causal_data_failure_fails_closed` — unrelated missing-weather-data fail-closed path, unaffected by the authorization fixture added to this file's `default_configs`. **Pass.**

No authorization fixture added by this pass weakens, bypasses, or defaults any fail-closed check. Every synthetic value is a clearly-labeled test fixture (`EVID-TEST-*`), never presented as real-station evidence.

---

## 10. Final full-suite result

```
pytest tests/ system/tests/  (863 tests collected — exactly matching the owner's original 66+791+6=863)
7 failed, 856 passed, 20 warnings in 1868.45s (0:31:08)
```
No conflicting test process was running before this run started (verified); it was the only full-suite run performed this pass, executed once, at the end, after every fix in Sections 2/4/5. **Down from the owner's original `66 failed, 791 passed, 6 errors`.** The 7 remaining failures are exactly the 7 items Sections 2–3 already classify as out-of-scope (Group C, 3 items) or flagged for owner decision (Group D's evaluator-gap item, 2, and Group F's forensic pins, 2) — zero new, unexplained failures introduced by this pass's edits.

---

## 11. Separate verdicts: Option-D component fix vs. RT-01 full-system acceptance

**Option-D component fix (fourteenth pass): VERDICT UNCHANGED — RESOLVED AT THE UNIT/COMPONENT LEVEL.** This pass did not touch `option_d.py` (confirmed byte-identical, Section 4) and did not find any new, genuinely distinct defect in it (the fourteenth pass's diesel-minimum-power-floor sequencing fix, and its `energy_balance_errors` honesty fix, remain exactly as reported). The 3 `test_ecd_option_d_integration.py::test_L/M/P` `AttributeError`s this pass fixed (Section 2, Group B) were a pre-existing **test-fixture** gap (a local `DummyBundle` helper missing the `solar_generation` attribute `option_d.py:88`'s *already-authorized* mechanism-2 fix reads) — not a new production-code defect, and not touched in `option_d.py` itself.

**RT-01 full-system acceptance: VERDICT UNCHANGED — STILL OPEN.** `test_per_timestep_conservation_audit` and `test_flexible_load_no_double_counting` (the directive's own RT-01 acceptance tests) were **not** specifically re-verified as newly passing by this pass's fixture migration — they were not among the 17 files edited, because the fourteenth pass's own report already traced their continued failure to `router.py`'s fail-closed behavior on `demo_scenario.json` with zero authorization, and this pass judged (Section 2, Group F) that supplying synthetic authorization specifically to re-open those two tests would blur the line with the still-open, separate question of what the *correct* forensic characterization of the now-fully-removed substitution mechanism should be. **RT-01 therefore remains open at the full-system level, exactly as the fourteenth pass left it** — not reopened to a worse state, not claimed closed. Distinctly: this pass's own fixture migration *did* let two other, previously-unreachable 168h-scenario full-pipeline tests (`test_cumulative_physical_conservation_168h`, `test_long_duration_closed_loop_endurance_168h`) finally execute, and their residual failures trace to an **already-documented, separate evaluator-labeling gap** (Section 8), not to the RT-01 diesel-floor mechanism or to any router/ECD/Option-D defect — this is a new piece of evidence about the evaluator, not a new RT-01 finding, and does not change RT-01's open/closed status either way.

**No diesel savings, no RT-01 closure, and no evaluator-gap fix are claimed by this pass.**

---

## Owner decisions needed (this pass's "stop and report" items — not resolved, flagged only)

1. **`system/tests/test_rt01_rt02_failure_forensics_regressions.py`'s two forensic-characterization tests** (Group F): the mechanism they pin (full-demand-as-critical-load substitution) no longer exists in `router.py` at all post-A-iii/B-iii, making their original `EMERGENCY`/`OPTION_D_FALLBACK` assertions structurally unreachable with zero authorization. Options: (a) retarget to assert `route == "UNKNOWN_INVALID"` (a stronger guarantee: the substitution bug cannot recur under any SOC/demand/fuel value, not just the ones tested), or (b) retire with a dated note explaining why the original pin no longer applies. This pass did not choose for the owner.
2. **`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/n6_operational_pipeline.py`** (Group C): builds its own unauthorized router configs internally; `system/tests/test_n6_live_operational_execution.py::test_05` fails there, not in a test file. Options: (a) authorize adding the same `EVID-TEST-*`-style synthetic authorization inside this research script, or (b) accept the test as correctly blocked pending real evidence, consistent with ECD-01's own standing policy.
3. **The 168h-scenario evaluator-labeling gap** (Group D): `unmet_critical_load_kwh` is confirmed mislabeled total-unmet-load, not critical-only, per the evaluator's own embedded warning and a prior report (`N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` §4). Options: (a) accept as a known, already-tracked limitation (no action), or (b) separately authorize populating the plan's `unmet_essential` field so the evaluator can report a genuine critical-only figure.
4. **`forecasting/solar_branch_01/tests/`'s 14 failures** and **`tests/test_critical_load_11_6kw.py`'s 2 failures** (Group C): both pre-existing and unrelated to router/ECD/Option-D; left entirely untouched this pass as out-of-scope. Flagged here only so they are not silently forgotten in future triage passes.
