# POLARIS — Narrow RT-01 Solar-Accounting Fix (Report)

**Date:** 2026-10-18
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `RT01_RT02_FAILURE_FORENSICS_REPORT.md` (2026-10-17, eighth pass) and `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.7.0.
**Authorization:** Project owner explicitly authorized, for this one task only, the single-line field-selection correction in the normally-protected file `system/optimization/implementations/option_d.py`, plus its focused regression test and verification. No other protected file was edited. No other production behavior change was authorized.

---

## 0. Important preliminary finding — the authorized fix was already present in the working tree

Before making any edit, this pass verified the current content of `system/optimization/implementations/option_d.py` at the line identified in the forensics report, per the directive's own instruction ("verify current file contents at the exact line" before editing). That verification found:

```
system/optimization/implementations/option_d.py:88
p_solar_avail = float(bundle.solar_generation.point[t]) if t < len(bundle.solar_generation.point) else 0.0
```

This is **already** the authorized, corrected form (`bundle.solar_generation.point[t]`, not `bundle.solar_irradiance.point[t]`). The file's own modification timestamp (`2026-10-17 20:23:42 +0530`) is **after** the forensics report's timestamp (`2026-10-17 20:10:50 +0530`) and after the register's v1.7.0 save (`20:08:03`), and the daily filesystem snapshot taken at `2026-10-17 23:00:01` already shows the fixed hash. The companion regression test file (`system/tests/test_rt01_rt02_failure_forensics_regressions.py`, modified `2026-10-17 20:24:29`) already asserts the **post-fix** behavior (`residual == pytest.approx(0.0, ...)`, `plan.solar_used[0] == pytest.approx(5969.55, ...)`), not the pre-fix characterization its own module docstring describes.

**Conclusion: the one-line fix and the test update this directive calls for were both already applied to the working tree, by a prior pass of this exact remediation, before this invocation began.** This task therefore did not need to — and did not — make any further edit to `option_d.py`. The remaining diff against the report's own unfixed hash is confirmed, below, to be exactly and only the authorized one-line change — nothing else.

**Diff confirmation**, against the pre-fix filesystem snapshot (`/timeshift/snapshots/2026-10-16_22-00-01/...`, hash `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12`, matching the forensics report's recorded baseline exactly):

```diff
88c88
<             p_solar_avail = float(bundle.solar_irradiance.point[t]) if t < len(bundle.solar_irradiance.point) else 0.0
---
>             p_solar_avail = float(bundle.solar_generation.point[t]) if t < len(bundle.solar_generation.point) else 0.0
```

Exit code 1 (one hunk), no other line in the file differs. This is exactly, and only, the authorized change. No edit was made in this pass; the file was read-verified to already match the single authorized target state, and left untouched.

---

## 1. Exact change (before / after)

**File:** `system/optimization/implementations/option_d.py`, line 88 (function `OptionDFallbackSolver.solve()`, "1. Total available renewable power").

| | Code |
|---|---|
| **Before** (pre-fix baseline, per forensics report + `2026-10-16` snapshot) | `p_solar_avail = float(bundle.solar_irradiance.point[t]) if t < len(bundle.solar_irradiance.point) else 0.0` |
| **After** (current working tree, already in place) | `p_solar_avail = float(bundle.solar_generation.point[t]) if t < len(bundle.solar_generation.point) else 0.0` |

**Behavioral effect:** `OptionDFallbackSolver` now treats "available solar power" as actual generation power in Watts (consistent with `milp.py` and `gap19_highs_native.py`, which already read `bundle.solar_generation.point[t]` for the identical purpose), instead of numerically substituting the irradiance reading (W/m²) as if it were Watts. Real solar generation above the previously tiny irradiance-shaped number is now correctly dispatched to load and/or recorded as curtailment, instead of silently vanishing from the energy balance.

**Regression test** (`system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestOptionDSolarIrradianceGenerationUnitBug::test_option_d_drops_solar_generation_above_irradiance_numeric_value`) was already updated (prior to this pass, per Section 0) to assert the corrected behavior: feeding the solver the exact RT-01 `(117.05 W/m², 5969.55 W)` pair now asserts `residual == pytest.approx(0.0, abs=1e-3)` and `plan.solar_used[0] == pytest.approx(5969.55, abs=0.01)`, i.e. "available solar generation is accounted for using generation in W, not irradiance in W/m²" — matching the directive's required assertion verbatim. No further edit to this test was needed or made.

---

## 2. Verification — exact commands and results

### 2.1 Isolated regression test (run first, per directive)

```
$ .venv/bin/python3 -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -v
TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting::test_demo_scenario_step0_routes_emergency_not_normal PASSED
TestOptionDSolarIrradianceGenerationUnitBug::test_option_d_drops_solar_generation_above_irradiance_numeric_value PASSED
TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel::test_corrupted_optimizer_weights_raises_on_direct_invocation PASSED
TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel::test_full_pipeline_never_reaches_milp_for_demo_scenario PASSED
4 passed in 0.78s
```

The specific bug-reproduction test (`TestOptionDSolarIrradianceGenerationUnitBug`) now passes with the **corrected** assertion (residual ≈ 0, not ≈ 5852.5). This confirms the fix is semantically correct in isolation. **Per the directive, this alone does not establish RT-01 closure** — see 2.2.

### 2.2 The five RT-01 tests — before vs. after

All five tests were re-run against the current (fixed) `option_d.py`. **All five still fail.** The fix changed the failure signatures (residual magnitudes moved, one failure roughly halved, one newly-passing signature elsewhere — see 2.3) but did not eliminate any of the five assertions.

```
$ .venv/bin/python3 -m pytest system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_cumulative_physical_conservation_168h system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_flexible_load_constraints system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_flexible_load_no_double_counting system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_long_duration_closed_loop_endurance_168h system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_per_timestep_conservation_audit -v
5 failed in 0.86s
```

| Test | Before (register / 8th pass, pre-fix) | After (this pass, post-fix) | Status |
|---|---|---|---|
| `test_per_timestep_conservation_audit` | `5852.500000000004` Wh residual at step 4 | `4658.729999999996` Wh residual at **step 22** (bus-bar imbalance) | FAIL (still, different step/value) |
| `test_cumulative_physical_conservation_168h` | `1029.98` kWh unmet vs. `0.0` expected | `529.78` kWh unmet vs. `0.0` expected | FAIL (still, ~49% smaller) |
| `test_flexible_load_constraints` | `0.0` vs `40000.0` (delta 40000.0) | `0.0` vs `40000.0` (delta 40000.0, within 1.0 tol) | FAIL (unchanged — see 2.4, unrelated) |
| `test_flexible_load_no_double_counting` | `40385.35` vs `35000.0` bus-bar (delta 5385.35) | `42556.509999999995` vs `37897.78` (delta `4658.729999999996`) | FAIL (still, value shifted) |
| `test_long_duration_closed_loop_endurance_168h` | `81.48%` vs `100.0%` reliability | `90.47%` vs `100.0%` reliability | FAIL (still, improved) |

**The fix has a real, measurable, directionally-correct effect** (smaller residuals/unmet-energy in 3 of 5 cases, consistent with more real solar now being counted/used instead of silently dropped), **but does not close RT-01.** Per the forensics report's own root-cause chain (A.2), the governing upstream defect is `router.py`'s critical-load substitution, which keeps routing these scenarios to `OptionDFallbackSolver` under `EMERGENCY` classification regardless of the solar-accounting fix; `option_d.py`'s other internal mechanics (proportional critical-load allocation, flexible-load handling, diesel/battery sequencing under `EMERGENCY` mode) still produce non-zero residuals independent of the one line fixed here. **RT-01 is NOT claimed closed.**

### 2.3 Overlap tests (Failure A / Failure B from the forensics report) — observed effect

Not explicitly required by the directive's steps 1–5, but run because the forensics report (A.2/A.3) established these two failures share `option_d.py`'s exact code path:

```
$ .venv/bin/python3 -m pytest system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution system/tests/test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved -v
test_10_24h_closed_loop_mpc_execution PASSED
test_gov_5_optimizer_deliberate_failure_preserved FAILED (SUCCESS_CLEAN, expected FAILED_TERMINATED)
1 failed, 1 passed
```

- **Failure A (`test_10_24h_closed_loop_mpc_execution`) now PASSES** — previously `46.35` kWh unmet vs `0.0` expected (register/8th-pass value). This is a genuine, direct benefit of the one-line fix: this scenario's 24-step `EMERGENCY`-routed dispatch now correctly accounts for solar generation, and the resulting unmet load falls to within the test's tolerance of `0.0`.
- **Failure B (`test_gov_5_optimizer_deliberate_failure_preserved`) still FAILS, unchanged** (`SUCCESS_CLEAN` observed, `FAILED_TERMINATED` expected). This is **unrelated to the one-line change**, exactly as the forensics report determined (A.3): `OptionDFallbackSolver` never reads `configs["optimizer"]["weights"]` at all, so this test's failure is governed entirely by `router.py`'s `EMERGENCY` misrouting (bypassing `LocalMILPEnergyOptimizer`, the only optimizer that reads the corrupted key), not by anything in `option_d.py`. Documented here, per the directive's instruction, without broadening the fix to touch it.

### 2.4 Focused Option-D/GAP19 regression suites (RT-02's named closure-test files)

```
$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py system/tests/test_gap19_milp_v2_research.py -q
3 failed, 29 passed in 764.75s (0:12:44)
FAILED tests/test_gap19_highs_native.py::test_canonical_409_model_structure
FAILED tests/test_gap19_highs_native.py::test_failsafe_unknown_invalid_mode
FAILED tests/test_gap19_ecd_option_d.py::TestGAP19ECDOptionD::test_R_option_b_protected_behavior_remains_unchanged
```

**Identical pass/fail outcome and identical failure reasons to the eighth pass's recorded result** (19/22 passed across the two root-level files + 10/10 for `test_gap19_milp_v2_research.py` = 29/32 combined; same 3 failures). The two `MISSING_GOVERNED_INPUT` failures are pre-existing test-fixture/interface-drift issues in `tests/test_gap19_highs_native.py` (its synthetic fixtures don't supply `demand_critical`), and the third is `tests/test_gap19_ecd_option_d.py::test_R`'s stale hardcoded `milp.py` hash — both explicitly unrelated to `option_d.py` and **not touched by this pass**, consistent with the directive's boundary against broadening the fix. **This confirms the one-line `option_d.py` change introduces zero regression anywhere in the focused GAP19/Option-D/ECD test surface.**

### 2.5 RT-01 closure verdict

**RT-01 is NOT closed.** All 5 of its named tests still fail. The fix is confirmed correct, isolated, non-regressive, and has a measurable positive effect (one previously-failing overlap test now passes; 3 of 5 RT-01 residuals shrink), but the dominant remaining cause is the separate, not-yet-authorized `router.py` critical-load-substitution defect (Section 4), which keeps these scenarios routed to the emergency fallback path where other, non-solar-related accounting limitations in `OptionDFallbackSolver` (flexible load, proportional allocation under `EMERGENCY`) still produce residuals. No failure encountered here is unrelated to the router/option_d mechanism already documented in the forensics report; none required broadening this pass's fix.

---

## 3. Protected-file and frozen-artifact integrity

### 3.1 Protected files (`manifest.py`'s 6-entry `PROTECTED_FILES` list + `manifest.py` itself)

| File | Baseline hash (eighth-pass report, pre-fix) | Current hash (this pass) | Status |
|---|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | **unchanged** |
| `system/optimization/implementations/option_d.py` | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` | `15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad` | **changed — expected, authorized, single-line diff confirmed (Section 0)** |
| `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | **unchanged** |
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` | **unchanged** |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | **unchanged** |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | **unchanged** |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | **unchanged** |

Re-verified identical before and after this pass's full test run (including the 764.75s GAP19 suite). Exactly one of the seven hashes changed, and it is the one line authorized.

### 3.2 Frozen Stage 8.1/N6 artifacts and manifests

| Artifact | Hash | Status |
|---|---|---|
| `.../candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` | `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` | unchanged |
| `.../candidate_n_additive_physics/artifacts/candidate_n1_model.joblib` | `7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7` | unchanged |
| `.../candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json` | `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` | unchanged |
| `stage4/stage4_results/ensemble_parameters.json` | `26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0` | unchanged |

`winner: null` re-confirmed present, unchanged, at `.../N6_OPERATIONAL_READINESS_REPORT.json:5`. `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard re-confirmed unconditional in both `execute_experiment_a()`/`execute_experiment_b()` (read-only, unmodified). All 4 `SAFETY_GATE_REGISTRY` entries in `system/safety/reserve_policy_guard.py` re-confirmed `authorized=False` (read-only, unmodified). The sealed 2025 blind partition was not accessed. No model was retrained, refit, retuned, or promoted. The 11.6 kW synthetic critical-load value (`system/config/loads.yaml:5`, `baseline_power_w: 11600.0`) was read-only inspected, not changed, and is not treated as verified station demand anywhere in this pass.

### 3.3 Git state

```
$ git status --short | grep "^A "
A  POLARIS_MASTER_HANDOFF.md
A  requirements.txt
```

Unchanged, untouched by this pass. This pass staged, committed, or pushed nothing.

---

## 4. Files changed by this pass

| File | Change |
|---|---|
| `system/optimization/implementations/option_d.py` | **None made by this pass** — already contained the authorized fix at the start of this invocation (Section 0); read-verified only. |
| `system/tests/test_rt01_rt02_failure_forensics_regressions.py` | **None made by this pass** — already contained the post-fix assertion update at the start of this invocation; read-verified only. |
| `RT01_SOLAR_ACCOUNTING_FIX_REPORT.md` (new, this file) + `N6_REMEDIATION_REPORTS/RT01_SOLAR_ACCOUNTING_FIX_REPORT.md` (mirror) | New deliverable. |
| `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (new) + `N6_REMEDIATION_REPORTS/ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (mirror) | New deliverable — router-fix proposal (Section 5 below / standalone file). Router itself was **not** edited. |
| `POLARIS_MASTER_DECISION_REGISTER.md` / `.json` + mirrors | v1.7.0 → v1.8.0; new Section 25 (`.md`); `RT-01` gains a dated evidence note recording this pass's exact test results (decision/scope unchanged, remains `decided`/deferred); `RT-02` unchanged (not touched by this pass — its own closure evidence is unaffected by a change to `option_d.py` alone). |

No other file was created, edited, staged, committed, or pushed.

---

## 5. Router issue — remains a separate decision

See the standalone companion file **`ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md`** (root, mirrored to `N6_REMEDIATION_REPORTS/`) for the full evidence-based proposal. `system/control/router.py` was **not edited** in this pass (read-only inspected to confirm its hash and content are unchanged — Section 3.1). Summary of the proposal's key points:

- **Authoritative source for actual critical-load demand:** none currently exists at runtime. The only candidate, `system/config/loads.yaml`'s `critical_load.baseline_power_w = 11600.0` (register item `CL-01`), is an explicitly self-labeled `SYNTHETIC_ENGINEERING_SCENARIO` value, not a validated station measurement (per `RT01_RT02_FAILURE_FORENSICS_REPORT.md` and the register's own `EVID-02` item).
- **Availability/validation status:** not available and not validated for the real Nuolja station context; it is a prototype fixture value only.
- **Safe behavior when missing/stale/synthetic-only:** the proposal recommends the router fail toward its current conservative (`EMERGENCY`-biased) behavior when no validated critical-load source exists, rather than silently trusting an unvalidated config value — i.e., any fix must not become less safe merely because a number exists in a YAML file.
- **Proposed routing change:** read `configs["loads"]["critical_load"]["baseline_power_w"]` as the ECD survivability input in place of `current_state.last_observed_demand`, with explicit fallback to the current (full-demand) behavior if that config key is absent — exactly as the forensics report's E.1 proposed, with the added caveat (this pass) that doing so changes operational posture and is not a pure bugfix, unlike `option_d.py`'s one-line change.
- **Safety implications:** this would make `EMERGENCY` routing significantly less frequent for demo_scenario.json-like conditions. This is a reduction in conservatism, not a correctness-only change, and must go through a dedicated governance/safety review, not this pass's narrow authorization.
- **Required regression tests before any such change:** `TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting` (must then assert `route == "NORMAL"`), all 18 `tests/test_gap19_ecd_option_d.py` tests, and re-runs of `test_s81_e2e_integration.py` tests 10/11/14/15 plus all 5 RT-01 tests to confirm the fuel/unmet-load numbers move in the expected direction without introducing a new conservation residual.
- **Rollback:** single-file, single-expression change (two added lines, one changed line); trivial to revert; no schema or interface change.

**No change to `router.py` was made or is proposed to be made in this pass.** This remains a separate authorization decision, as the directive requires.

---

## 6. Register update

`POLARIS_MASTER_DECISION_REGISTER.md`/`.json` updated v1.7.0 → v1.8.0, new Section 25. Changes, evidence-justified only:

- `RT-01`: gains a dated note recording this pass's exact test results — the authorized `option_d.py:88` fix was found already applied; all 5 RT-01 tests still fail (with measurably reduced/shifted residuals in 3 of 5); one overlap test (`test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution`) now passes; `current_state` (`decided`) and `owner_decision_record.implementation_authorized` are updated to reflect that the solar-accounting half of the deferred fix is now implemented, while the item remains open pending the separate router decision. RT-01 is **not** closed.
- `RT-02`: **not changed** by this pass — the GAP19/Option-D/ECD focused-suite result (29 passed, 3 failed) is identical to the eighth pass's recorded result; no new evidence changes its disposition. Remains `ENGINEERING_WORK_REQUIRED`.
- No other of the 33 canonical register IDs changed.
- Both register files mirrored to `N6_REMEDIATION_REPORTS/`, verified byte-identical via `diff` after copying.
