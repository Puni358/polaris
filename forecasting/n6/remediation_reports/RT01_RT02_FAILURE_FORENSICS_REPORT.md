# POLARIS — Owner-Authorized Full-Suite Failure Forensics and RT-02 Closure (Report)

**Date:** 2026-10-17
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.6.0 (now v1.7.0) and `N6_OPERATIONAL_EVIDENCE_AND_GOVERNANCE_CAMPAIGN_REPORT.md` (seventh pass, which ran `system/tests/` to completion for the first time: 423 collected, 416 passed, 7 failed).
**Nature of this pass:** targeted forensic investigation, not another general audit. Investigates all 7 full-suite failures, prioritizes the 2 newly-found ones, obtains RT-02's missing closure evidence, and fixes only what is safely fixable without touching a protected file.

---

## A. Findings — all 7 failures

| # | Test | Reproduction | Root cause | Overlap | Fixed? |
|---|---|---|---|---|---|
| 1-5 | `test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::{test_cumulative_physical_conservation_168h, test_flexible_load_constraints, test_flexible_load_no_double_counting, test_long_duration_closed_loop_endurance_168h, test_per_timestep_conservation_audit}` (RT-01 family) | Reproduced identically (byte-exact 5852.500000000004 Wh residual at step 4) | **Corrected this pass** — NOT `gap19_highs_native.py:444` (the previously-recorded attribution). See A.1. | Shares root mechanism with Failure A (A.2) and causes Failure B's symptom (A.3) | No — protected files; change proposal in Section E |
| 6 | `test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution` (Failure A) | Reproduced identically (46.35 kWh unmet) | **Determined this pass.** See A.2. | Same root mechanism as RT-01 (router misrouting) + same `option_d.py:88` bug | No — protected files; change proposal in Section E |
| 7 | `test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved` (Failure B) | Reproduced identically (`SUCCESS_CLEAN` instead of `FAILED_TERMINATED`) | **Determined this pass.** See A.3. | Same root mechanism as A.2 | No — protected files; change proposal in Section E |

### A.1 RT-01 — corrected root cause

The register (via `POLARIS_DEADLINE_MASTER_RESOLUTION.md`, itself filesystem-dated 2026-10-17 14:52, i.e. earlier in today's session) attributes the 5 RT-01 failures to `gap19_highs_native.py:444`'s `p_curt_tot` inside the **protected GAP19 optimizer**. This pass re-ran `test_per_timestep_conservation_audit` and inspected its own saved artifact:

```
$ .venv/bin/python3 -m pytest system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_per_timestep_conservation_audit -q
AssertionError: 5852.500000000004 not less than 0.1 : Renewable availability imbalance at step 4: 5852.500000000004
1 failed in 0.57s
```
```python
>>> plan['constraint_status']
'OPTION_D_FALLBACK'
>>> bundle['solar_generation']['point'][4], plan['solar_used'][4], plan['renewable_curtailment'][4]
(5969.55, 117.05, 0.0)
```

**`gap19_highs_native.py` never ran for this test.** `EMSControlRouter` (see A.2) routed this scenario's every step to `OptionDFallbackSolver`. The exact 5852.5 Wh residual (`5969.55 - 117.05 = 5852.5`) is fully and precisely explained by `system/optimization/implementations/option_d.py:88`:

```python
p_solar_avail = float(bundle.solar_irradiance.point[t]) if t < len(bundle.solar_irradiance.point) else 0.0
```

This reads `bundle.solar_irradiance.point[t]` — **irradiance, W/m²** (numerically `117.05` at this hour) — where every other optimizer in this codebase (`milp.py`, `gap19_highs_native.py`) reads `bundle.solar_generation.point[t]` — **actual generation power, W** (`5969.55` at the same hour) — as "available solar power." The real ~5.97 kW of available solar generation above the tiny irradiance-shaped number is never dispatched (`p_ren_avail` only ever "sees" 117.05 W of it) and never recorded as curtailed (curtailment is computed from the same undercounted `p_ren_avail`, so it comes out `0.0`), so it simply vanishes from the energy balance that `test_per_timestep_conservation_audit` checks.

This is confirmed by isolated, deterministic reproduction independent of the full pipeline: `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestOptionDSolarIrradianceGenerationUnitBug::test_option_d_drops_solar_generation_above_irradiance_numeric_value` feeds `OptionDFallbackSolver.solve()` a synthetic bundle with the identical `(117.05, 5969.55)` pair and reproduces a `5852.5 W` residual, with `plan.solar_used[0] == 117.05` — numerically the irradiance value, not a fraction of true generation.

**This does not reopen RT-01's owner decision** ("retain diagnostic findings, defer protected fix," Section 14/22 of the register). It corrects the evidence underlying it: a future protected-file governance window should target `option_d.py:88` (and the router misrouting in A.2), not `gap19_highs_native.py:444`. `gap19_highs_native.py`'s own `p_curt_tot` logic (lines ~430-444) was inspected directly and found to correctly decompose `p_sol_u + p_c_sol = p_sol_max` by construction via its own MILP decomposition constraint — it has no equivalent bug and is simply not in the call path for any of the 5 RT-01 tests (all 5 use `PolarisLocalRunner(optimizer_type="milp")`, confirmed by direct inspection of `test_offline_runtime.py`'s fixtures, and all 5 route through `EMSControlRouter` to `OptionDFallbackSolver`, confirmed by artifact inspection for the first-step case and for the 168h scenario's first step).

### A.2 Failure A — root cause determined

**Reproduction** (`.venv/bin/python3 -m pytest system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution -q`): `assert 46.35 == 0.0`, `1 failed in 0.64s`.

**Mechanism, traced end to end:**

1. `test_10` uses `PolarisLocalRunner(scenario_filename="demo_scenario.json", optimizer_type="milp", forecast_engine_type="stage81_solar")`. The configured optimizer is `LocalMILPEnergyOptimizer` (`system/optimization/implementations/milp.py`) — **not** `GAP19HighsNativeOptimizer`, and **not** a `PROTECTED_FILES` entry (`system/orchestration/manifest.py`'s `PROTECTED_FILES` list has exactly 6 entries: `gap19_highs_native.py`, `option_d.py`, `ecd.py`, `router.py`, `simulator.py`, `runner.py` — re-read directly from source this pass, confirming `milp.py` has never been protected).
2. Replicating `PolarisLocalRunner.run_pipeline()`'s loop exactly (including the router/Option-D branch it contains) step by step for 24 steps reproduces **46.35209999999999 kWh** — an exact match to the pytest failure.
3. Instrumenting the loop shows `EMSControlRouter.evaluate_and_route()` returns `route == "EMERGENCY"` for **all 24 of 24 steps** — `LocalMILPEnergyOptimizer.optimize()` is never called even once; `OptionDFallbackSolver.solve()` runs instead every time.
4. Root cause of the permanent EMERGENCY classification, in `system/control/router.py`:
   ```python
   # 2. Critical Load Trajectory (Use current demand scalar as synthetic fixture)
   critical_load_w = float(current_state.last_observed_demand)
   ```
   The router feeds the station's **full observed demand** (~35–48 kW for demo_scenario.json) into `EmergencyConditionDetector.evaluate()` as `critical_load`, instead of the station's actual, documented, much smaller critical-load design value (**11.6 kW**, `system/config/loads.yaml`'s `critical_load.baseline_power_w`, matching register item `CL-01`'s owner-decided value). In `system/control/ecd.py`, battery survivability is `t_battery = usable_ac_energy_wh / critical_load_w`; at 50% SOC, usable energy is ≈55,200 Wh AC, giving `t_battery ≈ 55200/37900 ≈ 1.46 h` against the full demand — far below the default `t_required_hours=6.0` — so `m_battery < 0` and `mode = EMERGENCY` at essentially every step, regardless of diesel's own endurance.
5. Once routed to `OptionDFallbackSolver`, the resulting dispatch is also subject to the `option_d.py:88` bug from A.1, and runs under the real `diesel_fuel_remaining_liters` default of 100 L and the demo scenario's diurnal wind/solar gaps (wind drops from ~17 kW to ~7–9 kW around hours 16–19 while solar is also low). The combination genuinely leaves 46.35 kWh unmet across the 24-step closed loop.

**Historical baseline, not invented:** `POLARIS_SYNTHETIC_E2E_INTEGRATION_IMPLEMENTATION.md` (filesystem-dated 2026-09-19, well before this session) documents, for this exact test under scenario "S1 Normal Operation," `14/14 PASSED` and **"Unmet Load: 0.0 kWh (Nominal S1)."** This is a genuine, reproducible divergence from a previously-documented passing state. Filesystem mtimes (no git history exists to bisect) show `demo_scenario.json`, `system/config/diesel.yaml`, `system/config/battery.yaml`, and `system/forecasting/implementations/baseline.py` (which supplies the wind/demand forecast Stage81 reuses) are all unchanged since 2026-09-16, i.e. before the passing report — ruling out scenario-data drift as the cause. `system/optimization/implementations/milp.py`'s only post-09-19 change (the 2026-10-02 binary-snapping fix, documented in `CANDIDATE2_FORECAST_CONTENT_ABLATION_FINAL_REPORT.md`) was directly verified this pass, by instrumenting `scipy.optimize.milp()`, to be a no-op for this exact 24-step scenario (zero fractional binaries occur at any of the 24 re-solves) — it is not the cause. `system/control/router.py` (mtime 2026-09-26) and `system/runtime/runner.py` (mtime 2026-10-01) both post-date the passing report; the router's critical-load substitution (step 4 above) is the best-evidenced, causally-traced explanation available without git history to pinpoint the exact change.

**Causal overlap with RT-01 — established, not assumed:** both failures are downstream of the *identical* `router.py` misrouting mechanism (A.2 step 4), and Failure A's dispatch plan is produced by the *exact same buggy code path* (`OptionDFallbackSolver`, including the `option_d.py:88` bug) that RT-01's residual traces to. This is a shared root cause, not merely a shared symptom ("both involve unmet load" — the directive's own caution against assuming overlap from symptom alone). Failure A is **not** mapped to RT-01's register ID: it is a different test, a different specific assertion (`0.0` total unmet vs. a `<0.1` conservation-residual tolerance), and not byte-identical to RT-01's historically-recorded value.

### A.3 Failure B — root cause determined

**Reproduction:** `assert report["execution_status"] == "FAILED_TERMINATED"` → observed `"SUCCESS_CLEAN"`, `1 failed in 0.55s`.

The seventh pass found zero occurrences of `"weights"` in `gap19_highs_native.py`/`option_d.py`/`runner.py` and concluded the corrupted `configs["optimizer"]["weights"]` key is "no longer read anywhere" in production. **This is true of those three files but incomplete.** `test_gov_5` constructs `PolarisLocalRunner(system_dir=system_dir, scenario_filename="demo_scenario.json")` with no `optimizer_type` argument — the default is `"milp"` → `LocalMILPEnergyOptimizer`, confirmed by direct inspection (`runner.optimizer_type == "milp"`, `type(runner.optimizer).__name__ == "LocalMILPEnergyOptimizer"`). `milp.py` **does** read the key:
```python
curt_penalty_per_wh = float(config.get("optimizer", {}).get("weights", {}).get("renewable_curtailment_penalty", 0.001))
```
Direct invocation this pass confirms it still raises exactly as the test intends:
```
>>> runner.optimizer.optimize(bundle, state, runner.configs)
RAISED: AttributeError 'str' object has no attribute 'get'
```
This `AttributeError` is exactly what `runner.py`'s own `try/except` around the optimizer call converts to `FAILED_TERMINATED` / `"OPTIMIZATION_RUNTIME_FAILURE: ..."` — **if that code path is ever reached.** It is not: the full-pipeline run of `test_gov_5`'s exact scenario shows `report["execution_status"] == "SUCCESS_CLEAN"` with the step-0 dispatch artifact's `constraint_status == "OPTION_D_FALLBACK"` — the *same* `router.py` misrouting mechanism from A.2 routes this scenario to `OptionDFallbackSolver` before `LocalMILPEnergyOptimizer.optimize()` is ever called, and `OptionDFallbackSolver` never reads `configs["optimizer"]["weights"]` at all (confirmed by direct inspection of `option_d.py`; it only reads `battery`/`diesel` config sections).

**Disposition:** this is category "failure injection no longer reaches the optimizer" — but the specific, evidenced reason is the `router.py` EMERGENCY-routing bypass (A.2), not an obsolete config key as the seventh pass concluded. The documented contract (`POLARIS_STAGE8_1_EMS_V2_TELEMETRY_NON_INTERVENTION_CORRECTION.md`, filesystem-dated 2026-09-19, predating this session, describing this exact test passing with "Invalid optimizer configuration produces `FAILED_TERMINATED`") is **not ambiguous and not stale** — it is blocked by the same upstream protected-file defect as A.1/A.2. **The original `test_gov_5` assertion is unmodified by this pass** (per the directive: preserved as evidence of the discovered divergence, and because it correctly encodes the intended contract). No status was hardcoded; no optimizer exception was suppressed; nothing was converted from failure to success. `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel` adds the required deterministic regression through the **supported interface** (direct `EnergyOptimizer.optimize()` invocation, the same interface `test_s81_e2e_integration.py::test_6` already uses): one test proves the injection mechanism itself is intact; a companion test proves the full pipeline's own saved artifact is `OPTION_D_FALLBACK`, pinning down exactly why `test_gov_5` cannot currently observe the mechanism it correctly tests for.

### A.4 RT-01 family — signatures confirmed unchanged, quickly

Per the directive's instruction not to re-litigate unchanged signatures: `test_cumulative_physical_conservation_168h` (1029.98 kWh unmet), `test_flexible_load_constraints` (0.0 vs 40000.0 total flexible load), `test_flexible_load_no_double_counting` (40385.35 vs 35000.0 bus-bar), `test_long_duration_closed_loop_endurance_168h` (81.48% vs 100.0% reliability), and `test_per_timestep_conservation_audit` (5852.500000000004 Wh at step 4) were confirmed byte-identical to the register's recorded values (the last one re-verified by direct re-run above; the other four were not independently re-run this pass since their assertion values are unchanged from the seventh pass's own just-completed, non-time-boxed run and re-running them would duplicate that evidence without new information). All 7 `PROTECTED_FILES`+`manifest.py` hashes (Section F) are confirmed byte-identical to every prior pass's recorded value, ruling out a protected-file edit as the cause of any RT-01 signature change (there is none).

---

## B. Changes

| File | Reason | Change | Before/after behavior |
|---|---|---|---|
| `system/tests/test_rt01_rt02_failure_forensics_regressions.py` (new) | Pin down the 3 causal mechanisms (A.1–A.3) deterministically, independent of the full pipeline, so a future protected-file fix has a precise regression target | 4 new tests: router-always-EMERGENCY characterization, isolated `option_d.py:88` unit-bug reproduction, direct-invocation deliberate-failure-still-intact confirmation, full-pipeline-uses-OPTION_D_FALLBACK confirmation | All 4 pass today (characterizing current, buggy behavior); each documents in its own docstring/assertion message what result would indicate the underlying defect was fixed |
| `POLARIS_MASTER_DECISION_REGISTER.md` / `.json` | Correct RT-01's recorded root cause; record RT-02's now-complete closure-test evidence | v1.6.0 → v1.7.0; new Section 24 (`.md`); `RT-01.owner_decision_record` gains a corrective note (decision/scope unchanged); `RT-02.disposition_2026_10_17` gains a dated note, `existing_evidence_sufficient` stays `false` | No disposition changed: RT-01 remains `decided`/deferred, RT-02 remains `ENGINEERING_WORK_REQUIRED` |
| `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` / `.json` | Mirror | Copied, byte-identical to root (verified via `diff`) | — |
| `RT01_RT02_FAILURE_FORENSICS_REPORT.md` (this file, new) + mirror | Deliverable | — | — |

**No `PROTECTED_FILES` entry was edited.** `system/control/router.py`, `system/control/ecd.py`, and `system/optimization/implementations/option_d.py` were read-only inspected. No frozen artifact was touched. No model was retrained/retuned/refit/promoted. The sealed 2025 blind partition was not accessed.

---

## C. Verification — exact commands and results

```
$ .venv/bin/python3 -m pytest system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution -q
1 failed in 0.64s   (assert 46.35 == 0.0 -- unchanged from seventh-pass report)

$ .venv/bin/python3 -m pytest system/tests/test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved -q
1 failed in 0.55s   (SUCCESS_CLEAN observed, not FAILED_TERMINATED -- unchanged from seventh-pass report)

$ .venv/bin/python3 -m pytest system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime::test_per_timestep_conservation_audit -q
1 failed in 0.57s   (5852.500000000004 Wh residual at step 4 -- byte-identical to register's recorded value)

$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py -q
22 collected, 3 failed, 19 passed in 0.26s
  FAILED tests/test_gap19_highs_native.py::test_canonical_409_model_structure
  FAILED tests/test_gap19_highs_native.py::test_failsafe_unknown_invalid_mode
  FAILED tests/test_gap19_ecd_option_d.py::TestGAP19ECDOptionD::test_R_option_b_protected_behavior_remains_unchanged

$ .venv/bin/python3 -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -q
4 passed in 0.50s   (new regression tests added by this pass)
```

**Not re-run this pass** (per the directive's instruction against repeatedly running the ~18-minute full suite without a warranting change): `python3 -m pytest system/tests/ -q`. The seventh pass's own just-completed, non-time-boxed run (423 collected, 416 passed, 7 failed, 1066.58s) is the current, unchanged, authoritative full-suite evidence; nothing in this pass's read-only investigation or additive new-test-file change warrants re-running it. The 4 untouched RT-01 tests (A.4) were likewise not re-run individually for the same reason.

**Pass/fail/skip/deselect accounting, non-overlapping, for the "RT-02 closure evidence base":**

| Source | Collected | Passed | Failed | Notes |
|---|---|---|---|---|
| `system/tests/` (seventh pass, unchanged) | 423 | 416 | 7 | Includes `system/tests/test_gap19_milp_v2_research.py` (10/10 passed) |
| `tests/test_gap19_highs_native.py` + `tests/test_gap19_ecd_option_d.py` (this pass, new) | 22 | 19 | 3 | Root-level `tests/` directory; not included in the 423 above (disjoint directories) |
| `system/tests/test_rt01_rt02_failure_forensics_regressions.py` (this pass, new) | 4 | 4 | 0 | Not part of RT-02's closure test; added evidence for A.1–A.3 |
| **Total non-overlapping evidence base this cycle** | **449** | **439** | **10** | 423 + 22 + 4 = 449; no file counted twice |

---

## D. RT-02 disposition — explicit

**RT-02's own `closure_test` field, verbatim:** *"`python3 -m pytest tests/test_gap19_highs_native.py system/tests/test_gap19_ecd_option_d.py system/tests/test_gap19_milp_v2_research.py -q` completes with a recorded pass/fail count."* (Note: the register's own text has a path error for the second file, which actually lives at root `tests/test_gap19_ecd_option_d.py`, not `system/tests/` — already identified by the seventh pass, re-confirmed by this pass's own `find`.)

**All three named files have now been run to completion in this remediation cycle for the first time, across two passes:**
- `tests/test_gap19_highs_native.py` — this pass — 4 collected, 2 passed, 2 failed.
- `tests/test_gap19_ecd_option_d.py` — this pass — 18 collected, 17 passed, 1 failed.
- `system/tests/test_gap19_milp_v2_research.py` — seventh pass, as part of the full-suite run — 10 collected, 10 passed.

**Literal closure_test wording ("completes with a recorded pass/fail count"): SATISFIED.** All three files ran to completion; pass/fail counts are recorded above.

**Implicit expectation of RT-02 as a clean regression baseline for the full GAP19 test surface: NOT SATISFIED.** 3 genuine failures are now recorded (Section A.4/C) that were not previously known because these files had never been run:
1. `test_canonical_409_model_structure` and `test_failsafe_unknown_invalid_mode` — both raise `ValueError: MISSING_GOVERNED_INPUT` because their synthetic fixtures predate `gap19_highs_native.py`'s current mandatory critical-load-trajectory input contract (`demand_critical` / `critical_demand_w` / `critical_demand_ratio` — none supplied). This is independent of RT-01/Failure-A/Failure-B; it is a test-fixture/interface-drift issue in an unprotected test file against a protected production interface that evolved after the test was written.
2. `test_R_option_b_protected_behavior_remains_unchanged` — fails on a stale hardcoded SHA-256 for `milp.py` that matches neither its current nor its documented pre-fix hash. `milp.py` is confirmed not a `PROTECTED_FILES` entry, so this is not a protected-file integrity violation — it is the test's own embedded assumption going stale across `milp.py`'s legitimate, separately-documented evolution.

**Verdict: RT-02 is NOT closed.** Unmet criteria: (a) a fully green run across all 3 named files (2 of 3 files have failures, for reasons unrelated to GAP19 regression risk but still unresolved); (b) the 3 new findings above have no owner disposition yet; (c) a protected-file fix for the A.1/A.2 `option_d.py`/`router.py` defects, which these same tests' execution now shows is also relevant to GAP19's broader test surface being trustworthy evidence of "no regression," has not been authorized or performed. **Register update:** `RT-02.disposition_2026_10_17.existing_evidence_sufficient` stays `false`; disposition stays `ENGINEERING_WORK_REQUIRED`; a dated note recording this pass's exact findings is added (Section 24.4 of the register).

---

## E. Remaining blockers — protected-file change proposals

Two protected files are implicated. Both proposals below are **not applied**; they are deferred to a dedicated Section-6/Batch-3-style governance review, per the directive's boundary rule.

### E.1 `system/control/router.py` — critical-load input

- **Evidence:** A.2 step 4. The router's own comment admits the substitution is a placeholder ("synthetic fixture").
- **Proposed line-level change:** replace
  ```python
  critical_load_w = float(current_state.last_observed_demand)
  if critical_load_w <= 0.0 and bundle.demand.point:
      critical_load_w = float(bundle.demand.point[0])
  ```
  with a read of the station's actual critical-load design value (`configs["loads"]["critical_load"]["baseline_power_w"]`, 11.6 kW per `CL-01`), falling back to the existing demand-based behavior only if that config key is absent, to preserve fail-safe conservatism when no critical-load config exists.
- **Safety implications:** this would make EMERGENCY routing *less* frequent for demo_scenario.json-like conditions (since 11.6 kW endures far longer against the battery/diesel than ~40 kW does). This is a reduction in conservatism and must be reviewed as a safety-relevant change, not merely a bugfix — the current over-conservative behavior is not unsafe by itself, only operationally misleading (it makes the "Emergency" classification nearly meaningless as a discriminator) and is the proximate cause of both newly-found failures plus 3-5 of RT-01's 5 failures.
- **Regression tests to require before any such change:** the new `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting` test must then assert `route == "NORMAL"` (its own docstring says to re-check this); all 18 tests in `tests/test_gap19_ecd_option_d.py` (which exercise E3 preserved/limiting-resource logic) must still pass; `test_s81_e2e_integration.py` tests 10, 11, 14, 15 and all 5 RT-01 tests should be re-run to confirm the fuel/unmet-load numbers change in the expected direction without introducing a new conservation residual.
- **Rollback:** single-file, single-expression change; trivial to revert; no schema or interface change.

### E.2 `system/optimization/implementations/option_d.py` — solar availability field

- **Evidence:** A.1.
- **Proposed line-level change:** line 88, replace
  ```python
  p_solar_avail = float(bundle.solar_irradiance.point[t]) if t < len(bundle.solar_irradiance.point) else 0.0
  ```
  with
  ```python
  p_solar_avail = float(bundle.solar_generation.point[t]) if t < len(bundle.solar_generation.point) else 0.0
  ```
  (matching the field both `milp.py` and `gap19_highs_native.py` already use for the identical purpose).
- **Safety implications:** this is a strict improvement in energy accounting (more real solar is correctly used/curtailed instead of silently vanishing); it would generally *reduce* diesel/battery reliance and unmet load in EMERGENCY mode, since real available solar is typically far larger in W than its own W/m² numeric value. No plausible safety regression identified; this is a pure bugfix with no interface change.
- **Regression tests to require:** `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestOptionDSolarIrradianceGenerationUnitBug` must then assert the residual is ≈0, not ≈5852.5 (its own docstring says to re-check this and then re-run the RT-01 suite); all 18 tests in `tests/test_gap19_ecd_option_d.py` must still pass (none of them currently assert the specific buggy value, so none should be affected negatively); RT-01's 5 tests should be re-run to confirm closure or a materially smaller residual.
- **Rollback:** single-token field-name change; trivial to revert.

**Recommended order:** fix E.2 first (pure bugfix, lower risk, directly closes most of RT-01), observe RT-01's residual-based tests, then evaluate E.1 (behavior-changing, needs an explicit owner/governance decision on the EMERGENCY-threshold conservatism trade-off) separately, since E.1 changes operational posture and E.2 does not.

**Other remaining blockers (not new, carried forward, not re-litigated here):** RT-02's 2 fixture-drift failures in `tests/test_gap19_highs_native.py` (Section D) — next action: update that test's synthetic `ForecastBundle`/`config` fixtures to supply `demand_critical` (or `critical_demand_w`/`critical_demand_ratio`), a low-risk, non-protected-file fix not performed this pass because it was outside this pass's prioritized scope (the 2 newly-found pipeline failures took priority, per the directive's own ordering); RT-02's stale-hash failure in `tests/test_gap19_ecd_option_d.py::test_R` — next action: update the test's hardcoded `milp.py` expected hash to the current, documented value, or remove `milp.py` from that test's protected-hash check since it is not actually in `manifest.py`'s `PROTECTED_FILES` list.

---

## F. Integrity

**Protected-file SHA-256, before and after this pass (identical to the seventh pass's recorded values and to every prior pass):**

```
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  system/optimization/implementations/gap19_highs_native.py
78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12  system/optimization/implementations/option_d.py
d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23  system/control/ecd.py
041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f  system/control/router.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  system/simulation/simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  system/runtime/runner.py
7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35  system/orchestration/manifest.py
```
All 7 re-verified byte-identical via `sha256sum` both before any investigation began and after all work completed in this pass.

**Frozen Stage 8.1/N6 artifact SHA-256, before and after (unchanged):**
```
b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197  .../artifacts/candidate_n6_model.joblib
7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7  .../artifacts/candidate_n1_model.joblib
1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031  .../artifacts/CANDIDATE_N_MANIFEST.json
26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0  stage4/stage4_results/ensemble_parameters.json
```
`winner: null` re-confirmed present, unchanged, at `.../N6_OPERATIONAL_READINESS_REPORT.json:5`.

**Campaign lock / safety gates:** `system/evaluation/replay_harness.py`'s `CampaignExecutionNotAuthorizedError` re-confirmed raised unconditionally by both `execute_experiment_a()`/`execute_experiment_b()` (read-only, unmodified). All 4 `SAFETY_GATE_REGISTRY` entries in `system/safety/reserve_policy_guard.py` re-confirmed `authorized=False` (read-only, unmodified). The sealed 2025 blind partition was not accessed. No model was retrained, refit, retuned, or promoted.

**Final git status:** nothing staged, committed, or pushed by this pass. The two pre-existing `A ` (already-staged, before this session) entries — `POLARIS_MASTER_HANDOFF.md`, `requirements.txt` — are untouched. This pass's new files (`system/tests/test_rt01_rt02_failure_forensics_regressions.py`, this report + its mirror, and the register amendment + its mirror) appear as untracked (`??`), consistent with this repository having no commit history at all.

---

## G. Register

`POLARIS_MASTER_DECISION_REGISTER.md`/`.json` updated v1.6.0 → v1.7.0, new Section 24. Changes, evidence-justified only:
- `RT-01`: `owner_decision_record` gains a corrective note (A.1); `current_state` (`decided`) and the decision text itself are **unchanged** — this is additive, corrective evidence about *where* the deferred protected-file fix should target, not a reopening of the decision to defer it.
- `RT-02`: `disposition_2026_10_17` gains a dated note (D) and `existing_evidence_sufficient` stays `false` (already `false` from the seventh pass; re-confirmed, not re-flipped).
- No other of the 33 canonical register IDs changed. The 2 Section-23 previously-unmapped failures (now root-caused in A.2/A.3) and the 3 new RT-02 findings (D) remain unmapped to any register ID, consistent with the register's standing rule against inventing IDs for findings that are evidence toward an existing item rather than new decisions.
- Both register files mirrored to `N6_REMEDIATION_REPORTS/`, verified byte-identical via `diff` after copying.
