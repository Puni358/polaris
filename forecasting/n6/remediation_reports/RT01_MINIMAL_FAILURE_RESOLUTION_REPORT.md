# POLARIS — Minimal RT-01 Failure-Resolution Pass: Report

**Date:** 2026-10-18
**Nature of this document:** Eighteenth pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `RT01_GOVERNANCE_RECONCILIATION_AND_EVIDENCE_REPORT.md` (seventeenth pass). Mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Register impact:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json`, new Section 34, v1.9.7 → v1.9.8 — `RT-01.owner_decision_record` gains a dated note recording this pass's two findings. **`RT-01.current_state` is UNCHANGED (`decided`, i.e. open/not-closed at the full-system level).** No other canonical item touched.
**Scope confirmation up front:** Narrow, evidence-first pass only. No `PROTECTED_FILES` entry (`router.py`, `ecd.py`, `option_d.py`, `gap19_highs_native.py`, `simulator.py`, `runner.py`, `manifest.py`) was edited — all were read-only inspected. No test file was edited (Task 1's proposed change is recorded but not applied — see Section 2). No assertion was weakened, no threshold invented, no model trained/tuned. No full test suite was run — only the 5 RT-01 tests, by name, were re-invoked once. No campaign, replay, or diesel comparison was run. No sealed 2025 blind data was accessed. Nothing staged, committed, or pushed.

---

## 1. Exact files changed and why

| File | Change | Why |
|---|---|---|
| `POLARIS_MASTER_DECISION_REGISTER.json` | `version` 1.9.7→1.9.8; `date` updated; new top-level `amendment_2026_10_18_eighteenth_pass_minimal_rt01_resolution` key; `RT-01.owner_decision_record` gains dated note `pass_2026_10_18_eighteenth_pass_minimal_failure_resolution` | Record this pass's two findings (Task 1 stop-and-report; Task 2 root cause) without claiming closure or inventing a new standard |
| `POLARIS_MASTER_DECISION_REGISTER.md` | Header date line appended; new **Section 34** added | Mirror the JSON addition in the authoritative narrative document |
| `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` / `.json` | Copied verbatim from the root versions | Required mirror, per every prior pass's convention |
| `RT01_MINIMAL_FAILURE_RESOLUTION_REPORT.md` (this file) + `N6_REMEDIATION_REPORTS/` mirror | New | This pass's own deliverable |
| `system/artifacts/latest_dispatch_plan.json`, `latest_forecast_bundle.json`, `run_report.json` | Regenerated twice (artifacts, not tracked/protected source files) | Side effect of two read-only diagnostic re-invocations of the existing authorized fixture, run to investigate Task 2 (Section 3) |

**No test file, production file, config file, or `PROTECTED_FILES` entry was edited.** No file was staged, committed, or pushed.

---

## 2. Task 1 — `test_cumulative_physical_conservation_168h`: proposed test-only correction drafted, NOT applied

**Directive instruction (verbatim intent):** prefer a test-only change asserting the critical-specific result is `UNKNOWN_NOT_VERIFIED` when evidence is absent (never assert zero critical-unmet energy without evidence); before changing the acceptance meaning, record the proposed change and rationale; **if owner approval is required by the register's own rules, stop and report rather than silently changing it.**

**Determination: owner approval IS required by the register's own rules.** Two independent lines of evidence:

1. `RT-01.closure_test` (this register's own field) explicitly conditions any relaxation of a failing test's assertion on *"a documented, owner-accepted explanation ... for why the residual is expected and the tests' assertions should be relaxed."* Changing what `test_cumulative_physical_conservation_168h` asserts — from the legacy `unmet_critical_load_kwh == 0.0` to a new `dispatch_safety.critical_unmet_total_wh == "UNKNOWN_NOT_VERIFIED"` check — is precisely this kind of relaxation: it changes what counts as a passing test for RT-01 closure purposes.
2. This exact change was already considered and explicitly declined, twice, by name:
   - Sixteenth pass (`POST_TRIAGE_INTEGRATION_AND_DIESEL_COMPARISON_REPORT.md` §4, mirrored at register §32.3/32.5): confirmed `unmet_critical_load_kwh` is mislabeled total-unmet-load, confirmed `dispatch_safety.critical_unmet_total_wh`/`critical_unmet_source` are the correctly-scoped fields, but made **no code or test change**.
   - Seventeenth pass (`RT01_GOVERNANCE_RECONCILIATION_AND_EVIDENCE_REPORT.md` §4, register §33.3): stated explicitly, *"the smallest legitimate next action is an owner decision on whether the test should be updated to assert against `dispatch_safety.critical_unmet_total_wh`/`critical_unmet_source` instead of the legacy field (a test-only change, but one that changes what is being verified — itself worth explicit owner sign-off rather than silent correction) — not performed here."*

Given this register's own rule and this unbroken two-pass precedent, this pass **stops and reports** rather than applying the change. The proposed diff is recorded below for owner review.

### Proposed diff (NOT applied to `system/tests/test_offline_runtime.py`)

```python
# CURRENT (lines 496–504):
def test_cumulative_physical_conservation_168h(self):
    """D4-2. Audits bus-bar, demand, and renewable conservation residuals (< 0.1 W) across all 168 steps."""
    runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
    _authorize_router_for_offline_runtime_test(runner)
    report = runner.run_pipeline(steps_to_run=168)
    # Check overall EMS balance errors from evaluation engine
    ems_eval = report["ems_evaluation"]
    self.assertEqual(ems_eval["unmet_critical_load_kwh"], 0.0)
    self.assertGreaterEqual(ems_eval["renewable_utilization_pct"], 75.0)

# PROPOSED (not applied — owner sign-off pending):
def test_cumulative_physical_conservation_168h(self):
    """D4-2. Audits bus-bar, demand, and renewable conservation residuals (< 0.1 W) across all 168 steps.
    NOTE: 'unmet_critical_load_kwh' is a legacy, mislabeled TOTAL-unmet-load field (evaluator.py confirms
    it equals total_unmet_wh/1000, not critical-specific). This test instead asserts the dispatch_safety
    critical-specific signal is honestly reported as UNKNOWN_NOT_VERIFIED when no production optimizer
    sets 'unmet_essential' -- it does NOT assert zero critical-unmet energy without evidence for it."""
    runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
    _authorize_router_for_offline_runtime_test(runner)
    report = runner.run_pipeline(steps_to_run=168)
    ems_eval = report["ems_evaluation"]
    dispatch_safety = ems_eval["dispatch_safety"]
    # Critical-specific unmet energy is honestly UNKNOWN_NOT_VERIFIED for any run where no dispatch
    # plan carries 'unmet_essential' (true of both production optimizers) -- must not be silently
    # asserted as zero.
    self.assertEqual(dispatch_safety["critical_unmet_total_wh"], "UNKNOWN_NOT_VERIFIED")
    self.assertIn("FALLBACK_TO_TOTAL_UNMET_LOAD", dispatch_safety["critical_unmet_source"])
    # Separate, still-enforced physical-conservation assertion (unchanged standard):
    self.assertGreaterEqual(ems_eval["renewable_utilization_pct"], 75.0)
```

**Rationale for the proposed form:** it (a) stops presenting the mislabeled total-unmet-load figure as a critical-load pass/fail criterion, (b) does not assert zero critical-unmet energy without evidence (it asserts the honest absence of evidence instead), and (c) keeps a genuine, separate physical-conservation check (`renewable_utilization_pct >= 75.0`) in force, unweakened. It would make this specific test pass under the current, unmodified production pipeline (because `critical_unmet_source` already, correctly, reports `FALLBACK_TO_TOTAL_UNMET_LOAD`/`UNKNOWN_NOT_VERIFIED` for both production optimizers — confirmed by direct read of `system/evaluation/evaluator.py` lines 238–253, unchanged this pass). **This pass takes no position on whether that would be an acceptable basis for counting this test toward RT-01 closure — that is exactly the owner decision being deferred to.**

---

## 3. Task 2 — `test_long_duration_closed_loop_endurance_168h`: root cause identified to the mechanism level

### 3.1 Method

A local, read-only diagnostic script (`diag_168h_v2.py`, kept outside the repository in the session scratchpad, never committed) imported the unmodified `PolarisLocalRunner`, `OptionDFallbackSolver`, and `EvaluationEngine` and monkeypatched, **in-process only** (nothing written to any protected or config file), the evaluation-capture step to intercept the per-step H1 dispatch-plan list that `run_pipeline()` already builds internally but does not return or persist in full. It used the identical, already-authorized `_authorize_router_for_offline_runtime_test()` fixture and the identical `synthetic_168h_endurance_scenario.json` / `optimizer_type="milp"` / `steps_to_run=168` invocation the test itself uses. This is a targeted diagnostic reusing the existing authorized harness, per the directive's explicit allowance ("existing artifacts and targeted diagnostics"), not a new campaign or a tuning exercise.

### 3.2 Findings

- **Routing:** 167 of the 168 steps route to `EMERGENCY`/`OptionDFallbackSolver`; only step 0 reaches `NORMAL`/the real MILP optimizer. `assessment.preserved_resource` is `DIESEL` for the great majority of steps (battery is the `limiting_resource`), occasionally `BOTH`.
- **Diesel fuel exhaustion:** `current_state.diesel_fuel_remaining_liters`, seeded once at t=0 from `configs["diesel"]["initial_fuel_l"]`, reaches **exactly `0.0` at step 44 of 168 (timestamp `2024-06-02T21:00:00Z`, ≈ hour 45)** and never recovers. `system/config/diesel.yaml` does not define `initial_fuel_l` at all; every reader of this key — `system/simulation/simulator.py:25` (`self.initial_fuel_l = diesel_cfg.get("initial_fuel_l", 100.0)`), `system/optimization/implementations/option_d.py:61`, `system/runtime/runner.py:108`, and `system/control/router.py:153` — falls back to the same hardcoded **`100.0` L default**. No refueling mechanism of any kind exists anywhere in the codebase (confirmed by reading all fuel-related lines in `simulator.py`; fuel only ever decreases, via `next_fuel = max(0.0, available_fuel - required_fuel)`). This default is independently labeled `SYNTHETIC ASSUMPTION` / `PROTOTYPE_ASSUMPTION` elsewhere in the repository (e.g. `investigations/emergency_trigger_governance_2026/GAP1_GENERATOR_INPUT_INVENTORY.md`), i.e. this is a known, deliberate placeholder value, not a hidden bug — but its specific causal role in the 168h endurance outcome had not previously been traced to this level of detail in any prior RT-01 pass.
- **Unmet-load pattern:** all 43 of the 168 steps with `unmet_load[0] > 0` occur **strictly after** step 44 (the fuel-exhaustion point), in exactly 6 contiguous runs (steps 45–49, 65–70, 89–97, 112–121, 137–142, 161–167). At every one of these 43 steps, `diesel_power == 0.0` **and** `battery_discharge == 0.0` simultaneously — confirmed by direct inspection of the captured H1 dispatch-plan fields, not inferred. Battery SOC at these steps is independently confirmed pinned at its configured `20.0%` floor (`min_soc_pct`) — the battery is not being mis-dispatched; it has no usable energy left to give (`usable_dc_wh = max(0.0, curr_e_wh - min_e_wh) == 0`). The sum of `unmet_load[0]` across all 168 captured H1 plans is **`553,842.6` Wh = `553.84` kWh**, which matches the evaluator's reported `unmet_critical_load_kwh`/`total_unmet_load_kwh` exactly.
- **Not a conservation defect:** `system/optimization/implementations/option_d.py`'s own dispatch accounting (lines ~200–220, read-only, unchanged) defines, for every timestep, `p_total_served = p_ren_to_load + p_dis + min(p_diesel, p_rem_demand)` and `p_served_actual = min(p_crit_demand, p_total_served)`. When `p_dis == 0` and `p_diesel == 0` (as at every one of the 43 unmet steps), this reduces algebraically to `p_served_actual = p_ren_to_load = p_sol_used + p_win_used`, which is exactly what the solver's own `energy_balance_errors` bus-bar check (`abs((p_sol_used+p_win_used+p_dis+p_diesel) - (p_served_actual+flex+p_chg))`) computes against — producing an exact `0.0` residual by construction, not by approximation. There is no double-counting, no simultaneous charge/discharge, and no SOC-bound violation at any of these steps.

### 3.3 Classification

**This is a dispatch-performance/scenario-configuration limitation, not a conservation/bus-bar defect.** The system is doing exactly what its current configuration allows: once a fixed, never-replenished 100 L diesel reserve (sized, on this scenario's own fuel-burn rates, for roughly 13–20 hours of continuous minimum-power diesel operation) is exhausted less than a third of the way into a 168-hour (7-day) endurance scenario with no refueling logic, and the battery is simultaneously drawn down to its configured minimum-SOC floor during a subsequent low-wind window, there is genuinely no more dispatchable energy available — the 90.04% reliability figure is the scenario's own, physically consistent outcome under that configuration, not a bug in the optimizer, router, or evaluator.

### 3.4 Dependency reported, per directive — not implemented

Resolving this (e.g., raising `initial_fuel_l` for the 168h endurance scenario's config to a value representative of an actual multi-day fuel reserve, and/or adding a refueling/resupply mechanism to the digital-twin simulator) is a **new engineering/acceptance decision**, not a bug fix: it changes a physical assumption about the prototype station's fuel-storage capacity, with no existing owner-authorized value to apply, and any implementation would touch one or more `PROTECTED_FILES` (`system/simulation/simulator.py` seeds and consumes this value; `system/optimization/implementations/option_d.py` and `system/control/router.py` both independently read it for their own forecasting/assessment logic). Per the directive's explicit instruction ("If resolving it requires protected-code changes or a new acceptance decision, report the exact dependency and stop"), this pass reports the dependency and does not implement a fix, raise the default, or edit `diesel.yaml`.

---

## 4. Validation (Task 3)

**Command:**
```
python3 -m pytest system/tests/test_offline_runtime.py -k "test_flexible_load_constraints or test_flexible_load_no_double_counting or test_per_timestep_conservation_audit or test_cumulative_physical_conservation_168h or test_long_duration_closed_loop_endurance_168h" -q
```

**Outcome:** `3 passed, 2 failed` (30 deselected). The 2 failures are byte-for-byte the same assertions and values as every prior pass recorded:
- `test_cumulative_physical_conservation_168h`: `AssertionError: 553.84 != 0.0`
- `test_long_duration_closed_loop_endurance_168h`: `AssertionError: 90.04 != 100.0`

No new failure was introduced; no previously-passing test regressed. This exact reproduction (identical to the sixteenth/seventeenth passes' recorded figures) confirms this pass's read-only diagnostics did not alter production behavior in any way.

---

## 5. Protected-file hash comparison

All 7 `PROTECTED_FILES` entries were re-hashed after this pass's work. All match the v1.9.7/seventeenth-pass recorded values exactly (no file was edited, so no change was expected):

| File | SHA-256 (after this pass) | Matches v1.9.7? |
|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | Yes |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | Yes |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | Yes |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | Yes |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | Yes |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | Yes |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | Yes |

**Zero mismatches. None of these 7 files was edited by this pass.**

---

## 6. Campaign / frozen-asset / blind-data boundary confirmation

- `RT-01.current_state` remains `decided` (open at the full-system level) — unchanged by this pass. No fully owner-supportable reason to change it was found: both remaining failures still require an explicit owner decision (Task 1's proposed test-assertion change; Task 2's fuel-reserve/no-refueling engineering dependency).
- `winner: null` not re-examined this pass beyond the seventeenth pass's same-day re-confirmation; not touched.
- The campaign-execution guard (`replay_harness.py`, `n6_multi_origin_harness/harness.py`) was not invoked this pass.
- `DSL-01`'s `epsilon_tol` was not touched; remains owner-deferred/unset.
- No sealed 2025 blind data was accessed.
- No frozen Stage 8.1/N6 asset was changed.
- No model training/tuning/promotion or broad experiment campaign occurred.
- Nothing staged, committed, or pushed.

---

## 7. Remaining owner decisions and final answer

**Two explicit owner decisions remain open, neither resolved by this pass:**

1. **Task 1:** whether to accept the proposed test-only correction to `test_cumulative_physical_conservation_168h` (Section 2) — replacing the mislabeled `unmet_critical_load_kwh == 0.0` assertion with an honest `dispatch_safety.critical_unmet_total_wh == "UNKNOWN_NOT_VERIFIED"` assertion plus the retained `renewable_utilization_pct >= 75.0` check. If accepted, this test would pass under the current, unmodified production pipeline.
2. **Task 2:** whether to authorize an engineering/acceptance-criteria change to the diesel fuel-reserve assumption (`initial_fuel_l`) and/or a refueling mechanism for multi-day endurance scenarios — a change that would touch `PROTECTED_FILES` and requires separate Section-6-style governance review, exactly as the register's existing convention requires for any `PROTECTED_FILES` edit.

**Final answer: RT-01 remains open.** 3 of 5 named tests pass (unchanged, reconfirmed); the 2 remaining failures are now each individually root-caused to the mechanism level — one a metric-labeling/evidence limitation with a drafted-but-unapplied test-only fix pending owner sign-off, the other a dispatch-performance/configuration limitation (diesel fuel-reserve exhaustion with no refueling logic) whose fix requires a new owner-authorized engineering decision touching protected files. Neither failure is resolved, relaxed, or converted to a pass by this pass. `RT-01.current_state` is unchanged (`decided`, i.e. not closed at the full-system level). The campaign guard, `DSL-01`'s `epsilon_tol` deferral, and `winner: null` are all unchanged.
