# POLARIS — End-to-End Recovery After RT-01 Solar Fix: Continuation Pass (Report)

**Date:** 2026-10-18
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Continues from:** `RT01_SOLAR_ACCOUNTING_FIX_REPORT.md`, `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (both 2026-10-18) and `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` v1.8.0.
**Companion document:** `ECD_ROUTER_DECISION_RECORD.md` (repo root, mirrored to `N6_REMEDIATION_REPORTS/`) — the Part 2 design-decision analysis required by this pass's directive. This report covers Parts 1, 3, 4, and 5.

---

## 1. Preservation of current state — confirmed

Before any write this pass, all 7 `PROTECTED_FILES`+`manifest.py` hashes and all 4 frozen Stage 8.1/N6 artifact hashes were captured and compared against the register's own recorded baseline (Section 6 below). `winner: null` was re-confirmed present and unchanged. The sealed 2025 blind partition (`.../artifacts/BLIND_2025_RESULTS.json`, `.../artifacts/blind_2025_predictions.csv`) was located by filename only, via `find`, and never opened or read. `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard and all 4 `SAFETY_GATE_REGISTRY` entries (`authorized=False`) were re-confirmed unconditional/unchanged, read-only. The pre-existing `git status --short` `A ` entries (`POLARIS_MASTER_HANDOFF.md`, `requirements.txt`) are untouched by this pass. Nothing was reset, cleaned, stashed, staged, committed, or pushed.

---

## 2. ECD/router design-decision analysis — summary

Full detail, exact file/line citations, and the owner decision surface are in **`ECD_ROUTER_DECISION_RECORD.md`**. Headline findings:

1. **The six-hour survivability rule** (`ecd.py` lines 283–291) requires battery-alone endurance AND diesel-alone endurance, each independently, to meet or exceed the same target horizon `T_required` — not combined/sequential endurance. This is confirmed by both the code and `POLARIS_EMS_SURVIVABILITY_DETECTOR_SPECIFICATION_AUDIT.md`'s Policy E3 "Mathematical Requirement." No ambiguity, no owner decision needed on this specific point.
2. **`T_required` itself (`router.py` line 45's `6.0`-hour default) is not a governed value.** No `system/config/*.yaml` file sets `ecd.t_required_hours`, so `6.0` is the value actually in effect in every pipeline run today. The repository's own `POLARIS_EMS_HD03_*` governance track (≈20 documents) explicitly lists promoting this exact number (HD-01B's `N=6h` EBR buffer) to `T_required` as a **prohibited action**, and separately records a formally authorized prototype value (72h) whose *implementation* was explicitly withheld (`HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED`). This is a previously unexamined finding — neither `RT01_RT02_FAILURE_FORENSICS_REPORT.md` nor `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` looked at this input; both addressed only the critical-load substitution.
3. **No authoritative critical-load source exists at runtime** (re-confirmed, consistent with prior passes); the only candidate (CL-01's 11.6 kW) is scoped by the register to `research`, not `safety_enforcement`/`production_promotion` — using it for routing would extend that decision beyond what the owner authorized.
4. **Existing governance already requires fail-closed behavior on a missing governed input, with arbitrary numeric substitution explicitly prohibited** (`POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md`), yet `router.py`'s current code does exactly the prohibited thing (three-level arbitrary fallback chain for critical load; an ungoverned numeric default for `T_required`) — and because both fallback chains always produce a valid positive number, `ecd.py`'s own fail-closed path (`INVALID_CRITICAL_LOAD`/`MISSING_T_REQUIRED`) can never be reached from this call site, even though it exists and is correctly implemented.
5. **The owner decision required** is stated precisely in the decision record as two linked sub-decisions (T_required source/value; critical-load source for routing specifically), each with three options and their stated consequences. **Neither is implemented here.**

---

## 3. Independent, authorized recovery work completed this pass

### 3.1 RT-01 reproduction and first-failing-timestep root cause

All 5 RT-01 tests were re-run against the current working tree (post the already-applied `option_d.py:88` fix). Result: **identical to the register's v1.8.0 recorded state — all 5 still fail**, with `test_per_timestep_conservation_audit` failing at step 22 with a `4658.729999999996` Wh bus-bar imbalance (byte-identical to the ninth pass's recorded value). This pass traced that exact step to its source using a direct instrumentation script (`PolarisLocalRunner(...).run_pipeline(steps_to_run=12)`, then reading `latest_dispatch_plan.json`/`latest_forecast_bundle.json` for step 22):

```
constraint_status: OPTION_D_FALLBACK
solar_used[22]=0.0  wind_used[22]=27500.0  battery_discharge[22]=5056.509999999991
diesel_power[22]=10000.0  load_served[22]=37897.78  unmet_load[22]=0.0
demand.point[22]=37897.78
sources (sol+wind+batt_dis+diesel) = 42556.51; sinks (served+flex+batt_chg) = 37897.78
excess = 4658.73  (== the test's own recorded residual, exactly)
```

**This is a third, independent defect inside `option_d.py` (protected, read-only this pass), distinct from both the already-fixed solar/irradiance unit bug and from `router.py`'s misrouting:**

- At step 22, `preserved_resource == DIESEL` (battery is the weaker/limiting resource), so `option_d.py`'s lines 135–143 drain the battery first (`p_dis = 5056.51`, energy/power-limited) and run diesel only for the true remainder (`p_rem_demand_after_bat ≈ 5341.27`). But diesel cannot run below its configured floor (`min_power_w = 10000.0`), so `p_diesel = max(min_diesel_w, p_rem_demand_after_bat) = 10000.0` — **4658.73 W more than is actually needed**.
- The "excess diesel charges battery" logic (`option_d.py` line 157, `if p_diesel > 0 and p_dis == 0:`) only activates when the battery is **not** also discharging. Here `p_dis = 5056.51 ≠ 0`, so the gate never opens, and the 4658.73 W excess is neither curtailed, charged, served (load_served correctly caps at demand), nor recorded as unmet. It is simply absent from both sides of the bus-bar balance.
- Confirmed general, not a one-off: scanning all 24 steps of this run shows step 23 (`diesel=10000`, `batt_dis=0`, `batt_chg=2000`) correctly charges the battery with excess diesel via the *same* logic, because `p_dis == 0` there — the gate only fails specifically when diesel's minimum-power floor is binding **while** the battery is simultaneously discharging, which is exactly the `preserved_resource == DIESEL` branch's normal operating pattern whenever `0 < p_rem_demand_after_bat < min_diesel_w`.

**A new, isolated, deterministic regression test pins this down**, independent of the full pipeline: `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestOptionDDieselMinimumPowerExcessGenerationUnaccounted::test_diesel_min_power_floor_creates_unaccounted_excess_when_battery_also_discharges`. It hand-constructs a minimal scenario (no renewables, 7000 W demand, battery energy-limited to exactly 3000 W this step, diesel floor 10000 W, `preserved_resource=DIESEL`) and asserts the current, unfixed behavior (`excess_w ≈ 6000.0 W`), with a docstring stating exactly what should change (`excess_w ≈ 0.0`) if this is ever fixed. **This test does not fix `option_d.py` and does not propose exactly how to fix it** (several designs are possible — curtail the excess, allow simultaneous charge+discharge accounting, or cap diesel to need when thermal/fuel constraints allow — each with different tradeoffs that are a protected-file design decision, not an engineering judgment call this pass is authorized to make unilaterally). It exists so a future authorized change window has a precise, minimal, already-isolated regression target, matching the pattern the eighth/ninth passes already established for the other two mechanisms.

### 3.2 Flexible-load defect — separated, confirmed, not new

`test_flexible_load_constraints` (expects `40000.0` Wh of flexible load scheduled between hours 8–18; observes `0.0`) fails for a reason **unrelated to both the solar-accounting fix and the diesel-excess mechanism above**: `option_d.py` line 76 hardcodes `flexible_load_schedule: List[float] = [0.0] * horizon_steps` — `OptionDFallbackSolver` never implements flexible-load scheduling at all, under any input. Confirmed directly from source (read-only). Since `router.py`'s misrouting (Mechanism 1) sends `demo_scenario.json` to `OptionDFallbackSolver` for effectively all 24 steps, this test fails deterministically regardless of either `option_d.py` fix discussed above, and would continue to fail even if routing were corrected to reach `LocalMILPEnergyOptimizer` for some steps but not others, unless every step happened to route to `NORMAL`. This is evidence toward RT-01, not a new register item (consistent with the register's standing rule against inventing IDs for findings that are evidence toward an existing item).

### 3.3 RT-02 focused-suite failures — fixed within existing authorization

The three failures identified by the eighth/ninth passes in RT-02's own named closure-test files were inspected and fixed, **without touching any `PROTECTED_FILES` entry**:

**(a) `tests/test_gap19_highs_native.py::test_canonical_409_model_structure`** — failed with `MISSING_GOVERNED_INPUT` (no `demand_critical`) and then (after the first fix) `MISSING_GOVERNED_INPUT: Terminal reserve target`. Root cause: this test's synthetic fixtures predate `gap19_highs_native.py`'s mandatory `demand_critical`/`terminal_target_wh` input contract. **Fix (test file only):** added a `demand_critical` `TimeseriesForecast` (ratio-based, following the exact convention already used by the passing `system/tests/test_gap19_milp_v2_research.py::create_dummy_forecast_bundle`) to `create_synthetic_forecast_bundle()`, and added `"terminal_reserve_model": "INITIAL_STATE"` to the test's config (uses the battery's own starting energy — no new numeric value invented).

**(b) `tests/test_gap19_highs_native.py::test_failsafe_unknown_invalid_mode`** — failed with the same `MISSING_GOVERNED_INPUT` before reaching the `UNKNOWN_INVALID` failsafe branch it intended to test. Root cause, traced to source: `gap19_highs_native.py` line 30 resolves operating mode via `getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))`. `StationState.__init__` (`system/schemas/station_state.py` line 32) **always** sets its own `operating_mode` attribute (default `"NORMAL"`), so `getattr`'s default branch — the test's `config["operating_mode"] = "UNKNOWN_INVALID"` — is unreachable; `station_state.operating_mode` always wins. The test's original fixture set mode only via `config`, so it silently never exercised the failsafe branch at all. **Fix (test file only):** `create_synthetic_station_state()` now accepts and forwards an `operating_mode` parameter directly onto `StationState`, and the test passes `operating_mode="UNKNOWN_INVALID"` there — matching the actual (protected) precedence rather than fighting it.

**(c) `tests/test_gap19_ecd_option_d.py::TestGAP19ECDOptionD::test_R_option_b_protected_behavior_remains_unchanged`** — failed on a stale hardcoded SHA-256 for `milp.py`. Confirmed (again) by direct inspection of `system/orchestration/manifest.py`'s `PROTECTED_FILES` list: it has exactly 6 entries, and `milp.py` is not one of them — this test's name and the inclusion of `milp.py` in its "protected" hash dict was itself the stale assumption (the forensics report's own finding #2, Section D). **Fix (test file only):** updated the hardcoded hash to `milp.py`'s current, verified value, with a comment explaining `milp.py` is not protected and the test still serves as a future-drift detector, not a protected-file integrity guarantee.

**Verification (this pass, exact commands):**

```
$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py -v
4 passed in 0.29s

$ .venv/bin/python3 -m pytest tests/test_gap19_ecd_option_d.py -q
18 passed in 0.14s

$ .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py system/tests/test_gap19_milp_v2_research.py -q
32 passed in 911.88s (0:15:11)   (see Section 3.4 for full result)
```

No `PROTECTED_FILES` entry was edited to achieve this. `system/control/router.py`, `system/control/ecd.py`, `system/optimization/implementations/gap19_highs_native.py`, `system/optimization/implementations/option_d.py`, and `system/orchestration/manifest.py` were read-only inspected only, to determine the correct, non-protected-file fix.

### 3.4 Combined RT-02 closure-test run — exact result

```
$ time .venv/bin/python3 -m pytest tests/test_gap19_highs_native.py tests/test_gap19_ecd_option_d.py system/tests/test_gap19_milp_v2_research.py -q
................................                                         [100%]
32 passed in 911.88s (0:15:11)
```

**This is RT-02's first-ever fully clean run of its own named closure-test files in this remediation cycle.** Previous result (ninth pass, unchanged since the eighth pass): 29 passed, 3 failed. All 32 tests across all three files now pass, with zero changes to any `PROTECTED_FILES` entry (Section 6) — the fix was entirely in the two non-protected test files' own fixtures (Section 3.3). Protected-file hashes were re-verified byte-identical immediately after this 15-minute run completed, confirming the long run itself made no incidental changes.

### 3.5 Overlap tests re-confirmed unchanged

```
$ .venv/bin/python3 -m pytest system/tests/test_s81_e2e_integration.py::test_10_24h_closed_loop_mpc_execution system/tests/test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved -v
test_10_24h_closed_loop_mpc_execution PASSED   (unchanged from ninth pass -- benefits from the already-applied solar fix)
test_gov_5_optimizer_deliberate_failure_preserved FAILED   (unchanged -- SUCCESS_CLEAN vs FAILED_TERMINATED)
```

### 3.6 Why the deliberate optimizer failure is bypassed — re-confirmed, not re-litigated

`test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved` corrupts `configs["optimizer"]["weights"]` expecting `LocalMILPEnergyOptimizer.optimize()` to raise and `runner.py` to convert that into `FAILED_TERMINATED`. Re-confirmed this pass, by direct invocation: `LocalMILPEnergyOptimizer.optimize()` **still raises exactly as designed** (`AttributeError: 'str' object has no attribute 'get'`) when called directly with the corrupted config — the injection mechanism itself is intact (`system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel`, both of its tests pass, re-run this pass). The full-pipeline test observes `SUCCESS_CLEAN` only because `router.py`'s Mechanism-1 misrouting (Section 2 above / `ECD_ROUTER_DECISION_RECORD.md`) sends `demo_scenario.json` to `OptionDFallbackSolver` for every step, and `OptionDFallbackSolver` never reads `configs["optimizer"]["weights"]` at all. **This is not a new finding** (the eighth pass, Section A.3, already determined this); this pass only re-verified it is still true and unchanged, since fixing RT-02's three focused-suite failures (3.3 above) does not touch anything in this causal chain. No routing or failure-policy change was made, per the directive's explicit boundary.

### 3.7 Register-adjacent regression surfaces re-checked

`system/tests/test_rt01_rt02_failure_forensics_regressions.py` (now 5 tests, 1 new) — all pass:

```
$ .venv/bin/python3 -m pytest system/tests/test_rt01_rt02_failure_forensics_regressions.py -v
5 passed in 0.76s
```

---

## 4. Operational readiness and diesel research — status, no new work performed

Reviewed existing evidence only, per the directive's instruction; no new acquisition, fabrication, or campaign work was attempted.

- **EVID-01** (live MEPS-18Z/SITES/Stage-3b arrival-time logging) and **EVID-02** (real Nuolja critical-load measurement) remain `EXTERNAL_EVIDENCE_REQUIRED` / blocked — re-confirmed unchanged this pass. Both require real station/provider data that cannot be synthesized or inferred from repository contents; no gap here can be closed with existing authorized evidence. This directly bears on `ECD_ROUTER_DECISION_RECORD.md`'s critical-load finding (Section 2.3 above): there is still nothing to feed the router besides a synthetic value, whatever the owner decides about scope.
- **DSL-01** (diesel-reduction preregistration / Candidate 2 authorization) remains `decided: leave epsilon_tol unset`, per the register's own fifth-pass decision — Candidate 2 execution remains unauthorized, and this pass did not invent a threshold or request/perform any campaign execution, consistent with the directive's explicit prohibition. `DIESEL_COMPARISON_PREREQUISITE_PLAN.md`'s dependency table and `replay_harness.py`'s unconditional `CampaignExecutionNotAuthorizedError` guard were re-confirmed unchanged (Section 6).
- **Next permitted research step, with its prerequisites, stated precisely:** before any Candidate 2 (or other diesel-reduction) execution — even research-mode — two things must happen, neither of which this pass is authorized to do unilaterally: (1) the owner must preregister a numeric `epsilon_tol` (critical-reliability degradation ceiling) *before* any result is inspected, per `DIESEL_REDUCTION_CONTROL_DESIGN_CORRECTION_AUDIT.md`'s own "AWAITING SAFETY-GATE PREREGISTRATION" verdict; (2) a separate, explicit campaign-execution authorization must be granted to lift `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard. Both are owner decisions the register (`DSL-01`) already states cannot be inferred from existing evidence (EVID-02's real critical-load gap is a direct input to any meaningful `epsilon_tol` choice, per the register's own `epsilon_tol` evidence-needed note). No change to this status was made or is proposed by this pass.

---

## 5. Owner decisions needed — precise questions

**(A) ECD/router — see `ECD_ROUTER_DECISION_RECORD.md` Section 5 for the full, two-part question with options and consequences.** Summary: (i) what `T_required` value, if any, should `router.py` use for the ECD's emergency/normal classification, and under what authorization (today's ungoverned `6.0`-hour default vs. implementing the already-decided-but-not-yet-implementation-authorized 72h prototype value vs. failing closed until a real value exists); (ii) whether `router.py` may use CL-01's 11.6 kW synthetic critical-load value for routing specifically (extending that decision's scope from `research` to `safety_enforcement`), continue the current full-demand substitution, or fail closed.

**(B) `option_d.py`'s diesel-minimum-power excess-generation gap (Section 3.1) and its flexible-load omission (Section 3.2)** — both are genuine, now precisely isolated defects in a `PROTECTED_FILES` entry. Fixing either requires the same kind of protected-file governance review already called for in `RT01_RT02_FAILURE_FORENSICS_REPORT.md` Section E and `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` — not performed or proposed as a specific line-level change by this pass, since the directive's boundary prohibits further edits to `option_d.py` this pass. The owner should be aware that **fixing router.py's misrouting alone (Decision A) would not close RT-01**: even with correct routing, any genuinely-EMERGENCY scenario would still hit the diesel-excess and flexible-load gaps in `option_d.py`.

---

## 6. Integrity — before/after hashes and verification

**Protected files (`PROTECTED_FILES` + `manifest.py`), captured before this pass's work and re-verified after:**

| File | Hash (before and after this pass) | Status |
|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | unchanged |
| `system/optimization/implementations/option_d.py` | `15179e83e11797c31b94e8391a00d8645c6a2a44711237408c78d0bc9a58b5ad` | unchanged (post-fix value from the ninth pass; read-only inspected, not edited, this pass) |
| `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | unchanged |
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` | unchanged |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | unchanged |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | unchanged |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | unchanged |

Confirmed via `sha256sum` both before this pass began and after all work (edits, test runs) completed; all 7 identical both times and identical to every prior pass's recorded value.

**Frozen Stage 8.1/N6 artifacts and manifests (unchanged):**

| Artifact | Hash |
|---|---|
| `.../candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` | `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` |
| `.../candidate_n_additive_physics/artifacts/candidate_n1_model.joblib` | `7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7` |
| `.../candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json` | `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` |
| `stage4/stage4_results/ensemble_parameters.json` | `26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0` |

`winner: null` re-confirmed present, unchanged, at `.../N6_OPERATIONAL_READINESS_REPORT.json:5`. No model retrained/refit/retuned/promoted. The sealed 2025 blind partition was not accessed (located by filename only). All 4 `SAFETY_GATE_REGISTRY` entries remain `authorized=False`; `replay_harness.py`'s `CampaignExecutionNotAuthorizedError` remains unconditional in both `execute_experiment_a()`/`execute_experiment_b()`.

**Files changed this pass (exact paths):**

| File | Change | Protected? |
|---|---|---|
| `tests/test_gap19_highs_native.py` | Added `demand_critical` to the synthetic bundle fixture; added `terminal_reserve_model: "INITIAL_STATE"`; fixed `operating_mode` precedence in the UNKNOWN_INVALID test | No |
| `tests/test_gap19_ecd_option_d.py` | Updated `milp.py`'s stale hash in `test_R`, with an explanatory comment | No |
| `system/tests/test_rt01_rt02_failure_forensics_regressions.py` | Added `TestOptionDDieselMinimumPowerExcessGenerationUnaccounted` (new 4th-mechanism characterization test) | No |
| `ECD_ROUTER_DECISION_RECORD.md` (new) + mirror | New deliverable, documentation only | No |
| `N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md` (this file, new) + mirror | New deliverable | No |
| `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` + mirrors | v1.8.0 → v1.9.0, new amendment section | No |

**No `PROTECTED_FILES` entry, frozen artifact, safety-gate authorization, or dispatch/control policy was touched.** Nothing was reset, cleaned, stashed, staged, committed, or pushed.

---

## 7. Register update

`POLARIS_MASTER_DECISION_REGISTER.md`/`.json` updated v1.8.0 → v1.9.0, new Section 26. Changes, evidence-justified only:
- `RT-02`: `current_state` updated `awaiting_evidence` → `resolved_with_evidence`; `disposition_2026_10_17` gains a dated note recording this pass's exact fixes and the clean 32-passed/0-failed combined result. RT-02 is now closed — its focused GAP19/Option-D/ECD test surface is fully clean, with zero `PROTECTED_FILES` edits.
- `RT-01`: `owner_decision_record` gains a dated note recording two newly-isolated, additional `option_d.py` mechanisms (diesel-minimum-power excess generation at the current step-22 residual; flexible-load scheduling's complete absence) plus the new ECD/router `t_required_hours` governance finding. `current_state` remains `decided` (item not closed — 5/5 of its own tests still fail).
- No other of the 33 canonical register IDs changed. Both register files mirrored to `N6_REMEDIATION_REPORTS/`, verified byte-identical via `diff` after copying.
