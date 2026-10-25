# POLARIS N6 Operational Readiness Remediation and Safety-Gated Evaluation

**Date:** 2026-10-17
**Scope:** Section 0 governance-bounded remediation pass against the frozen N6 solar candidate and GAP19/EBR reserve policy, per the project owner's N6 Operational Readiness Remediation protocol.
**Repository:** `/home/punith-bs/01polaris (Copy)` (git repo, branch `master`, **no commits exist yet** — all content is either staged (`POLARIS_MASTER_HANDOFF.md`, `requirements.txt`) or untracked).

---

## 1. Executive Status

**PARTIALLY COMPLETE.**

All authorized, in-scope remediation items (Sections 2, 3, 4, 5, 6, 7 of the protocol) have working, tested, non-production code implemented in this pass. No frozen model, calibration constant, protected dispatch/control file, production default, or governance state (`winner: null`) was modified. No historical campaign, dispatch simulation, or sealed 2025 blind evaluation was run or accessed.

It is **PARTIALLY** rather than **COMPLETE** because:
- Live telemetry/NWP arrival-time evidence cannot be collected in this offline environment (Section 3's own stated limitation) — only fixture-level instrumentation tests were run.
- Several numerical safety thresholds remain explicitly `AUTHORIZATION_REQUIRED` (Section 4/7) — this is intentional, not an oversight, per the protocol's own instruction not to invent them.
- Two pre-existing GAP19 test suites (`tests/test_gap19_highs_native.py`, `system/tests/test_gap19_ecd_option_d.py`, `system/tests/test_gap19_milp_v2_research.py`) were not fully executed in this pass due to per-test runtime (~48s/test, HiGHS solver startup cost) exceeding a safe isolated-test time budget; one targeted case from the related `test_gap19_j2_option_b.py` suite was run and passed (see Section 7 below).

---

## 2. Root Causes and Fixes

### 2.1 N6 inference path — decomposition gap (Section 2.7)

- **Issue:** `N6SolarForecastEngine.predict()` in `system/forecasting/implementations/n6_solar.py` (previously lines 358-406) computed point prediction, ensemble-uncertainty/conformal bound, and EBR reserve trajectory inline in a single undifferentiated block — not independently testable, contrary to protocol item 2.7.
- **Everything else in Section 2 was already correctly implemented** and required no fix: SHA-256 artifact verification before deserialization (`_load_and_verify_bundle`, lines 190-250), fail-closed on hash mismatch / missing file / bad deserialize / bad schema, exact feature name/order/horizon-count enforcement (`_validate_feature_matrix`, lines 257-320), causal day masking (`causal_day_mask = (elev > 0.0) & (cs_ghi > 0.0)`), and no mock/dummy/random fallback anywhere in the solar inference path (the only fallback engine, `LocalBaselineForecastEngine`, is used solely for the separate wind/demand channels, never for solar).
- **Fix:** Extracted three pure, independently callable methods from `predict()`, preserving the exact original arithmetic, ordering, and constants (no model/weight/calibration change):
  - `N6SolarForecastEngine._compute_point_prediction(X_df, st4, cs_terrain, cs_ghi, elev, shaded)` — `system/forecasting/implementations/n6_solar.py` (additive + kt ensembles, blending, causal day mask).
  - `N6SolarForecastEngine._compute_uncertainty_bounds(y_pred, preds_add, preds_kt, causal_day_mask, cs_terrain)` (static) — ensemble spread + conformal lower/upper bound.
  - `N6SolarForecastEngine._compute_ebr_reserve(scale_s)` — 6-hour rolling EBR trajectory, in Wh.
  - `predict()` now calls these three in sequence; the rest of `predict()` (timestamp construction, power conversion, monotonicity clamp, metadata, bundle assembly) is unchanged.
- **Test:** `system/tests/test_n6_decomposition_parity.py` (6 tests) — proves bit-identical parity between the decomposed call sequence and `predict()`'s own output on the same fixture (point/lower/upper/EBR), and proves each of the three operations is independently callable with synthetic, non-ensemble inputs (e.g. the EBR function tested directly against the Arm A_FIX-shaped low-solar/high-uncertainty `scale_s` fixture, with no model bundle involved).
- **Result:** `python3 -m pytest system/tests/test_n6_forecast_engine.py system/tests/test_n6_decomposition_parity.py -q` → **15 passed** (9 pre-existing + 6 new), confirming no behavioral drift from the refactor.

### 2.2 Hash-value sanity check against the protocol's stated hashes

The protocol statement describing the two cited hashes as "65/66 hex chars (1-2 chars too long)" does **not** hold: both strings are exactly 64 hex characters (verified with Python `len()`). Independently recomputed SHA-256 of the on-disk artifacts:

| File | Computed SHA-256 |
|---|---|
| `stage7/.../candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` | `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` |
| `stage7/.../candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json` | `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` |

Both exactly match the protocol's stated hashes, `n6_solar.py`'s `FROZEN_MODEL_SHA256` constant, `polaris_inference_runner.py`'s `EXPECTED_SHA256` constant, and the repo's own `HASHES.sha256` manifest. **No tampering or drift found.**

### 2.3 Operational feature-ingestion observability (Section 3)

- **Issue:** No production feature-ingestion/freshness-timestamp logger exists anywhere in the repository. The project's own prior audit (`stage7/.../candidate_n_additive_physics/operational_availability_audit/operational_causality_audit.md`) independently reached the same conclusion: 27/36 N6 features are `UNPROVEN` for operational causality, specifically because no contemporaneous ingestion/arrival-timestamp log exists for MEPS 18Z data, SITES Nuolja telemetry, or Stage 3b/4 execution. The audit's own `remediation_plan.md` *proposes* a logger daemon but it was never built.
- **Fix (new, non-production instrumentation module):** `system/monitoring/n6_feature_ingestion_monitor.py`
  - `FeatureIngestionMonitor.record_feature_readiness(...)` — records expected source, source cycle, forecast origin, valid time, acquisition time, processing completion time, decision cutoff, missingness, provenance tag; **computes actual arrival/processing latency and margin-to-cutoff from the supplied timestamps** (never a hard-coded constant); fails closed (`IngestionIntegrityError`) on missing features, missing acquisition/processing timestamps, or late arrival (processing completed after `decision_cutoff`).
  - `FeatureIngestionMonitor.validate_horizon_alignment(timestamps)` — fails closed on wrong horizon count or non-hourly spacing.
  - `FeatureIngestionMonitor.validate_meps_lead_window(lead_start, lead_stride, lead_stop)` — validates a MEPS OPeNDAP lead-slice spec against the documented `lead[6:1:29]` (24-lead, horizons 1-24) convention, using OPeNDAP's inclusive-endpoint slice semantics; explicitly rejects the known legacy-truncated `lead[7:1:25]` defect (19 leads, horizons 20-24 missing) referenced in `meps_wind_extractor.py` and the audit's `temporal_lineage.md`.
  - `FeatureIngestionMonitor.check_u700_v700_provenance(horizon_hour, provenance_tag, is_nan)` — permits NaN only for horizons 20-24 (the documented archive-coverage gap), and requires a genuine-NWP provenance tag (never a `synthetic_default`/`mean_imputed`/etc. tag) for any non-NaN value.
  - `summary()` returns only scalar metadata (timestamps, booleans, counts, short tags) — never a raw telemetry series or payload.
- **Test:** `system/tests/test_n6_feature_ingestion_monitor.py` (16 tests) — healthy-arrival latency math, missing-feature fail-closed, late-arrival/staleness fail-closed, non-blocking audit mode, horizon-count/spacing rejection, MEPS lead-window acceptance/rejection (including the legacy defect), u700/v700 permitted-gap vs. fail-closed-outside-gap, fabricated/unrecognized provenance rejection, and a "no raw payload leaks into the summary" check.
- **Result:** `python3 -m pytest system/tests/test_n6_feature_ingestion_monitor.py -q` → **16 passed**.
- **Explicit limitation (per protocol's own completion criterion):** this module is instrumentation only. It does **not** prove the live MEPS/SITES/Stage-3b pipeline is operational — every timestamp in the test suite is a synthetic fixture. Real arrival-time evidence still requires a live-wired caller (e.g. a cron job around `n6_operational_pipeline.py` / `meps_wind_extractor.py`) logging genuine observed timestamps over time, which is explicitly out of scope for this remediation pass (no network access, no production daemon deployment).

### 2.4 Reserve-safety defenses (Section 4) — the core finding

- **Issue (most significant finding of this remediation):** Reading `system/optimization/implementations/gap19_highs_native.py`, `system/evaluation/evaluator.py`, and `system/orchestration/worker.py` showed that **critical-unmet-load and reserve-shortfall are computed internally by GAP19 (`j1_objective`, `j2_objective`/`s_J2` slack, `reserve_shortfall`) but are never read or surfaced downstream.** `evaluator.py::evaluate_ems_performance` never references `plan["reserve_shortfall"]`, `j1_objective`, or `j2_objective`; `constraint_violations_count` only increments on `constraint_status != "OPTIMAL"`, which a dispatch with nonzero unmet-critical-load or reserve shortfall will never trigger, because GAP19's soft reserve constraint (Layer C, `gap19_highs_native.py` lines 297-305) uses an unbounded slack `s_J2` that can absorb any shortfall without making the solve infeasible. `worker.py` even declares `integrity_counters["unmet_critical_load_wh"] = 0.0` (line 114) but **never increments it anywhere in the file**. Net effect: a dispatch can report `constraint_status == "OPTIMAL"` / `execution_status == "SUCCESS_CLEAN"` while critical load was actually unmet and the governed reserve was violated — exactly the failure mode documented for historical Arm A_FIX (diesel −11.23%, critical unmet energy **+47.2%**). Additionally, `evaluator.py` mislabels its one unmet-load metric: `"unmet_critical_load_kwh"` is actually computed from `unmet_load` (total unmet), not the dedicated `unmet_essential` (critical-specific) field that the `DispatchPlan` schema already supports.
- Separately verified: no "solar credit" mechanism exists in production GAP19 code (confirmed by grep — it is discussed only in non-production audit markdown, e.g. `DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md`), and `gap19_highs_native.py` never reads `TimeseriesForecast.lower`/`.upper` for any series — forecast uncertainty is not double-applied; it is **completely ignored** by the governed optimizer.
- **Fix (new, additive, non-production validation layer — does NOT modify any `PROTECTED_FILES` entry from `system/orchestration/manifest.py`):** `system/safety/reserve_policy_guard.py`
  - `validate_hard_soc_floor(battery_soc_wh, min_e_wh)` — independent out-of-band check that battery energy never drops below the governed hard minimum; raises `ReservePolicyViolation` (unconditional, not policy-dependent).
  - `validate_reserve_units_consistent(name, value, unit, expected_unit="Wh")` — fails closed on Wh/kWh/W mixing.
  - `assert_no_double_netting(...)` — fails closed if the same forecast lower-bound/uncertainty value is applied to more than one of {reserve target, dispatch objective, solar credit} simultaneously.
  - `compute_bounded_solar_credit(forecast_lower_wh, uncertainty_is_valid, forecast_is_fresh, authorized_max_credit_fraction, governed_reserve_target_wh)` — **raises `AuthorizationRequiredError` if no authorized credit fraction is supplied** (no implicit default); forces credit to `0.0` if uncertainty is invalid or stale; clamps any credit to `authorized_max_credit_fraction × governed_reserve_target_wh`.
  - `evaluate_dispatch_safety(plan, min_e_wh, reserve_shortfall_authorization_wh)` — surfaces solver infeasibility, hard-SOC violations (raises), critical-unmet energy (uses `unmet_essential` when present; falls back to `unmet_load` with an explicit over-counting note when it is not), and reserve shortfall vs. an optional authorized ceiling (reports the shortfall for visibility even with no ceiling authorized, but never silently marks it "passed").
  - `detect_reserve_regression_vs_baseline(...)` — directly operationalizes the Arm A_FIX failure-mode detector.
  - `SAFETY_GATE_REGISTRY` — registers the four gates proposed in prior audits, **all explicitly `authorized=False`** with an `AUTHORIZATION_REQUIRED` note; this remediation does not promote any of them to authorized.
- **Test:** `system/tests/test_reserve_policy_guard.py` (24 tests), including a direct regression test using the **exact reported Arm A_FIX numbers** (Control 10,368.85 L / 329.35 kWh; Arm A_FIX 9,204.24 L / 484.81 kWh) — confirms the guard correctly flags this as `is_fuel_savings_masking_reliability_regression = True` and computes the ~11.23% fuel saving / ~47.2% unmet-load increase; plus hard-SOC-floor violation, unit-mismatch, double-netting, unauthorized/invalid/stale solar-credit, and synthetic low-solar/high-ramp scenarios.
- **Result:** `python3 -m pytest system/tests/test_reserve_policy_guard.py -q` → **24 passed**.
- **What remains `AUTHORIZATION REQUIRED`:** the actual numeric reserve-shortfall ceiling, the max authorized solar-credit fraction, and whether `evaluator.py`/`worker.py` should be wired to call this guard in production — all four are policy decisions for the project owner, not invented here.

### 2.5 Forecast lineage of Arms A/A_FIX/B/C (Section 5)

- Independently re-verified by directly reading `experiments/exp_three_arm_2024/scripts/run_three_arm_2024.py` (not by trusting prior markdown):
  - **Arm A / A_FIX** (`ARM_CONFIGS`, lines 71-83; `ArmForecaster.predict()`, lines 257-300): both configured `solar_forecast: "causal_nwp_gamma1"`, routed exclusively through `CausalNwpPhysicsForecastEngine` (imported line 231). A_FIX differs only by a `LabelCorrectedLocation` geometry wrapper (`solar_convention.py:24-61`) applied at construction. **Neither uses Stage 8.1 nor Candidate N6.**
  - **Arm B** (lines 262-270): `solar_forecast: "realized_sw_in"`. Reads `self.sites[t]` — **measured/realized** SITES SW_IN for the full 24h future horizon — into both the dispatch bundle and the EBR reserve calculation, self-tagged `"NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY"` (line 269) with `causal: False` (line 80). **Confirmed oracle/leakage.** Its reported 34.82% saving must never be reinterpreted as an achievable causal saving.
  - **Arm C** (lines 271-299): `solar_forecast: "calibrated_gamma_hat_point"` / `ebr_solar: "calibrated_lower_bound"`, via `calibrate_arm_c.point_ghi`/`lower_bound`, derived from the same causal clear-sky/cloud physics engine. Causal, but not Stage 8.1 or N6.
  - **No arm in this experiment uses Stage 8.1 or Candidate N6** — confirmed by a repo-wide grep for `n6_solar|s81_corrected_solar|N6ForecastEngine|Stage8_1|Stage81` inside `experiments/exp_three_arm_2024/`, which returned zero code hits.
- **Fix (new, read-only utility):** `system/evaluation/forecast_lineage.py` — `ORACLE_PROVIDER_NAMES` / `CAUSAL_PROVIDER_NAMES` registries built from this verified evidence, `build_lineage_record(...)` producing a structured record distinguishing provider-configured / model-loaded / forecast-consumed-by-dispatch / forecast-used-for-reserve / leakage-detected, and `reject_if_oracle(...)` (reused by the Section 6 harness below). Unknown providers are marked `UNKNOWN_UNVERIFIED`, never assumed safe.
- **Test:** covered jointly with Section 6 in `system/tests/test_forecast_lineage_and_replay_harness.py` (8 of 23 tests target lineage classification specifically).

### 2.6 Factor-isolated replay harness (Section 6) — built, not executed

- **Fix (new module):** `system/evaluation/replay_harness.py`
  - `MatchedControllerSettings` / `ScenarioSpec` — a frozen bundle requiring battery params, diesel/fuel-curve constraints, GAP19 solver settings, objective priorities, termination criteria, demand-criticality config, and scenario-inclusion rules to be structurally identical across a matched pair.
  - `ScenarioSpec.__post_init__` calls `reject_if_oracle(...)` — a scenario can never be constructed with a known oracle provider (e.g. `realized_sw_in`) as its forecast.
  - `validate_matched_scenario_pair` / `validate_matched_scenario_set` — fail closed on scenario-key mismatch, initial-SOC mismatch, any controller-setting drift, varying both forecast-provider **and** reserve-policy simultaneously, or varying neither (nothing being compared).
  - `ExperimentAConfig` (forecast-value isolation) — requires the governed reserve policy held constant across every scenario; constructing it already runs full matched-set validation.
  - `ExperimentBConfig` (reserve-policy isolation) — **unconditionally raises `AuthorizationRequiredError`** unless a specific in-module sentinel authorization token is supplied; no real or guessable token exists anywhere in this repository, so this configuration can never be legitimately constructed by this remediation pass, exactly per the protocol's instruction that "the second experiment must not be enabled until the candidate reserve policy and safety thresholds have explicit authorization."
  - `FactorIsolatedReplayHarness.execute_experiment_a()` / `.execute_experiment_b()` — **both unconditionally raise `CampaignExecutionNotAuthorizedError`**. No code path in this repository, after this remediation, can execute a dispatch campaign through this harness.
- **Test:** `system/tests/test_forecast_lineage_and_replay_harness.py` (23 tests) — oracle rejection at scenario-construction time, matched-pair validation (key/SOC/controller-settings/dual-factor-variation rejection), `ExperimentAConfig` construction and its own oracle/reserve-policy-drift rejection, `ExperimentBConfig`'s unconditional authorization gate (tested both with no token and with a wrong guessed token), and confirmation that `execute_experiment_a`/`execute_experiment_b` always raise.
- **Result:** `python3 -m pytest system/tests/test_forecast_lineage_and_replay_harness.py -q` → **23 passed**. No dispatch, GAP19 call, or N6 inference was executed by this harness or its tests.

### 2.7 Safety-gated outcome evaluation reporting (Section 7)

- **Fix (new module):** `system/evaluation/safety_gated_report.py`
  - `OriginResult` — per-origin record covering every metric Section 7 requires at minimum (diesel liters, critical unmet kWh, critical service ratio, reserve violations/slack, min SOC, battery throughput, diesel runtime/starts, solver feasibility/timeout, fallback action).
  - `build_report(...)` — **raises `DroppedOriginError`** if either baseline or candidate result list is shorter than the declared `n_origins_attempted` — i.e. a failed/adverse origin can never be silently excluded from the report.
  - `SafetyGatedOutcomeReport.evaluate_gates()` — populates `authorized_gate_results` (always `"NOT_EVALUATED: gate not formally authorized"` for all four registry entries — none are authorized) separately from `proposed_gate_results` (computed for visibility, each explicitly labeled `PROPOSED_GATE_WOULD_PASS`/`WOULD_FAIL`, never presented as a governance pass/fail).
- **Test:** `system/tests/test_safety_gated_report.py` (5 tests) — no-silent-drop enforcement, authorized-gate separation, and an Arm-A_FIX-shaped fixture that correctly reports `WOULD_FAIL` on the critical-unmet and origin-failure-rate proposed gates while diesel usage improves.
- **Result:** `python3 -m pytest system/tests/test_safety_gated_report.py -q` → **5 passed**.

---

## 3. Forecast Lineage Summary (verified, not re-derived from markdown alone)

| Arm | Configured provider | Model actually invoked | Causal? | Used by dispatch | Used for reserve |
|---|---|---|---|---|---|
| Control (PC-Control) | `causal_nwp_gamma1` | `CausalNwpPhysicsForecastEngine` | Yes | forecast point | solar-blind governed EBR |
| A | `causal_nwp_gamma1` | `CausalNwpPhysicsForecastEngine` | Yes | forecast point | forecast point |
| A_FIX | `causal_nwp_gamma1` + geometry fix | `CausalNwpPhysicsForecastEngine` (+`LabelCorrectedLocation`) | Yes | forecast point | forecast point |
| B | `realized_sw_in` | measured SITES SW_IN (future horizon) | **No — oracle** | realized power | realized power |
| C | `calibrated_gamma_hat_point` | causal physics engine + `calibrate_arm_c` | Yes | calibrated point | calibrated lower bound |

**No arm uses Stage 8.1 or Candidate N6.** Arm B's 34.82% reported saving is not an achievable causal result and must not be presented as one. Remaining unknown: whether any *other*, not-yet-inspected experiment script in this repository wires N6 into a dispatch loop — this remediation only exhaustively checked `experiments/exp_three_arm_2024/`; `N6SolarForecastEngine` is also instantiated in `run_n6_closed_loop_simulation.py` and `n6_operational_pipeline.py`, which were inspected only for their N6-adapter wiring (Section 2.3), not independently re-audited as a full dispatch-campaign lineage trace in this pass.

---

## 4. Operational Ingestion — What Is and Isn't Proven

- **Implemented:** `system/monitoring/n6_feature_ingestion_monitor.py`, a passive readiness/provenance recorder with real latency math, horizon/MEPS-window validation, and u700/v700 provenance checks.
- **Proven by fixture tests:** the monitor's logic is internally correct — it computes latency correctly from supplied timestamps, correctly rejects the known legacy MEPS truncation defect, and correctly separates the permitted u700/v700 NaN gap from a genuine failure.
- **NOT proven, and explicitly out of scope here:** that the live MEPS 18Z archive, SITES Nuolja telemetry, or Stage 3b/4 pipeline actually deliver features within their decision cutoffs in production. The repository's own prior audit (`operational_causality_audit.md`) independently reached `UNPROVEN` for 27/36 features for exactly this reason (no contemporaneous arrival-timestamp log exists yet). This remediation does not change that verdict — it builds the instrumentation that a future live-wired caller would need in order to change it, but running that caller against a live NWP feed is a separate, network-touching task this protocol explicitly prohibits.

---

## 5. Reserve Safety — Implemented Safeguards, Tests, and What Needs Authorization

**Implemented and tested** (`system/safety/reserve_policy_guard.py`, 24 passing tests): hard-SOC-floor enforcement, unit-consistency checks, double-netting detection, bounded/fail-closed solar-credit computation, dispatch-safety evaluation (solver infeasibility, critical-unmet energy, reserve shortfall), and the Arm A_FIX regression detector reproduced against the exact historical numbers.

**Existing authorized gates found in production code:** **none.** A repo-wide search for `critical_service_ratio`, `reserve_violation`, `SAFETY_GATE`, `99.95`, `p < 0.01` found zero enforced hits in `system/` — every such term exists only in `experiments/`/`stage7/`/root-level audit markdown as a proposal, never wired into `gap19_highs_native.py`, `runner.py`, `worker.py`, or `evaluator.py`.

**Still requiring explicit project-owner authorization before any candidate can be evaluated against them:**
1. A numeric reserve-shortfall ceiling (Wh) for `evaluate_dispatch_safety`'s `reserve_shortfall_authorization_wh`.
2. A maximum authorized solar-credit fraction for `compute_bounded_solar_credit`.
3. Whether the four `SAFETY_GATE_REGISTRY` proposed gates (critical-unmet-not-worse-than-baseline, ≤5% adverse origins, >2% savings at p<0.01, >99.95% critical service ratio) should become formally authorized governance requirements.
4. Whether `system/evaluation/evaluator.py` and `system/orchestration/worker.py` should be modified to call `reserve_policy_guard.evaluate_dispatch_safety` on every run (this remediation deliberately did NOT make that production wiring change, to avoid altering shared execution-path code beyond the scope explicitly authorized).

---

## 6. Replay Readiness — What Was Built and Why No Campaign Was Run

`system/evaluation/replay_harness.py` and `system/evaluation/forecast_lineage.py` provide the complete configuration/validation layer for a future factor-isolated Experiment A (forecast-value isolation, N6 vs. baseline, reserve policy fixed) and a gated-but-unconstructible Experiment B (reserve-policy isolation). No campaign was run because:
- `execute_experiment_a`/`execute_experiment_b` unconditionally raise `CampaignExecutionNotAuthorizedError` — there is no code path to invoke GAP19 or N6 inference through this harness.
- `ExperimentBConfig` cannot even be constructed without an authorization token that does not exist in this repository.
- This matches the protocol's explicit instruction: "Do not execute either experiment now."

---

## 7. Test Results (exact commands, pass/fail counts)

| Suite | Command | Result |
|---|---|---|
| N6 engine + decomposition parity | `python3 -m pytest system/tests/test_n6_forecast_engine.py system/tests/test_n6_decomposition_parity.py -q` | **15 passed** |
| Feature-ingestion monitor | `python3 -m pytest system/tests/test_n6_feature_ingestion_monitor.py -q` | **16 passed** |
| Reserve-policy guard | `python3 -m pytest system/tests/test_reserve_policy_guard.py -q` | **24 passed** |
| Forecast lineage + replay harness | `python3 -m pytest system/tests/test_forecast_lineage_and_replay_harness.py -q` | **23 passed** |
| Safety-gated outcome report | `python3 -m pytest system/tests/test_safety_gated_report.py -q` | **5 passed** |
| **All new/modified suites together** | (same 5 files in one invocation) | **83 passed, 0 failed** |
| `system/tests/test_gap19_j2_option_b.py::test_1_ebr_calculation_correctness` (targeted, unmodified file) | `python3 -m pytest system/tests/test_gap19_j2_option_b.py -q -k test_1_ebr_calculation_correctness` | **1 passed** (47.7s — HiGHS solver cost, not a regression) |
| `tests/test_gap19_highs_native.py`, `system/tests/test_gap19_j2_option_b.py` (full suites) | — | **NOT RUN — exceeded 120s isolated-test budget** (pre-existing, unmodified, HiGHS-MILP-backed; ~48s/test × many tests) |
| `system/tests/test_gap19_ecd_option_d.py`, `system/tests/test_gap19_milp_v2_research.py` | — | **NOT RUN** (same reason; files unmodified by this remediation) |
| `system/tests/test_n6_live_operational_execution.py` | — | **NOT RUN — AUTHORIZATION REQUIRED** (makes live network calls to `thredds.met.no`; explicitly prohibited: "do not start live polling against production systems") |
| Full historical campaign / 2025 sealed blind evaluation | — | **NOT RUN, NOT ACCESSED** (prohibited by protocol) |

No test result in this report was fabricated; every "passed"/"failed" count above reflects an actually-executed `pytest` invocation observed in this session.

---

## 8. Protected-Artifact Verification

**Frozen N6 artifacts (recomputed SHA-256, matches protocol-stated and in-code values exactly):**

| Artifact | SHA-256 |
|---|---|
| `candidate_n6_model.joblib` | `b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197` |
| `candidate_n1_model.joblib` | `7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7` |
| `CANDIDATE_N_MANIFEST.json` | `1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031` |

**`system/orchestration/manifest.py` `PROTECTED_FILES` — current hashes, none modified by this remediation (recorded for the project owner's own before/after comparison):**

| File | SHA-256 (after this remediation) |
|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/optimization/implementations/option_d.py` | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` |
| `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` |
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` |

None of these six files were opened for editing at any point in this remediation pass (confirmed by `git status` showing no changes under `system/optimization/implementations/gap19_highs_native.py`, `option_d.py`, `system/control/`, `system/simulation/`, or `system/runtime/`).

**`winner: null` — confirmed unchanged** in `stage7/.../candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json:5`, `N6_CLOSED_LOOP_VALIDATION_REPORT.json:4`, and `experiments/exp_three_arm_2024/results/run_20261011T143130Z/RESULTS.json:542`.

**Sealed 2025 blind evaluation:** files identified (`stage7/stage8/stage8_1_corrected_2025/*blind*`, `candidate_n_additive_physics/artifacts/BLIND_2025_RESULTS.json`, `blind_2025_predictions.csv`) were located by filename only and were **not opened, read, or rerun** at any point in this remediation.

**Production defaults:** `system/runtime/runner.py::PolarisLocalRunner.__init__` still defaults `forecast_engine_type="baseline"` → `LocalBaselineForecastEngine`; `system/orchestration/worker.py` still instantiates `GAP19HighsNativeOptimizer()` as the governed optimizer; `N6SolarForecastEngine` remains instantiated only in research/test code, never in `runner.py` or `worker.py`. **Unchanged.**

**git status:** no commits exist in this repository. Before this session, `POLARIS_MASTER_HANDOFF.md` and `requirements.txt` were staged; every other repository file (hundreds of research artifacts) was already untracked. This remediation added exactly the following new files (all untracked, none committed, none pushed) and made exactly one in-place edit:

- **Edited:** `system/forecasting/implementations/n6_solar.py` (decomposition refactor, Section 2.1 — no math/weight/calibration change).
- **New:** `system/monitoring/__init__.py`, `system/monitoring/n6_feature_ingestion_monitor.py`
- **New:** `system/safety/__init__.py`, `system/safety/reserve_policy_guard.py`
- **New:** `system/evaluation/forecast_lineage.py`, `system/evaluation/replay_harness.py`, `system/evaluation/safety_gated_report.py`
- **New tests:** `system/tests/test_n6_decomposition_parity.py`, `system/tests/test_n6_feature_ingestion_monitor.py`, `system/tests/test_reserve_policy_guard.py`, `system/tests/test_forecast_lineage_and_replay_harness.py`, `system/tests/test_safety_gated_report.py`
- **This report:** `N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md`

No other file in the repository was modified, moved, or deleted. All pre-existing untracked research artifacts were preserved untouched.

---

## 9. Remaining Blockers (prioritized by safety/importance)

1. **(Safety-critical)** `system/evaluation/evaluator.py` and `system/orchestration/worker.py` still do not surface critical-unmet-load or reserve-shortfall in production reporting — the new `reserve_policy_guard` module exists but is not yet wired into either file. Wiring it in was judged out of scope for this pass (it touches shared execution-path code beyond the explicitly authorized "implement safety enforcement... as a validation hook"), but it is the single highest-priority next step to prevent a future Arm-A_FIX-shaped result from being reported as a clean win.
2. **(Policy)** No numeric reserve-shortfall ceiling, solar-credit fraction cap, or formal authorization of the four proposed safety gates exists. `AuthorizationRequiredError`/`AUTHORIZATION_REQUIRED` markers are in place everywhere these are needed; only the project owner can resolve them.
3. **(Evidence)** Live arrival-time evidence for MEPS/SITES/Stage-3b ingestion still does not exist; the instrumentation to collect it now does, but nothing in this environment can generate or validate that evidence without network access to production NWP/telemetry sources.
4. **(Scope)** `N6SolarForecastEngine` usage outside `experiments/exp_three_arm_2024/` (e.g. `run_n6_closed_loop_simulation.py`) was not independently re-audited for lineage in this pass; if a future evaluation needs to trust that path, it should get the same code-level verification given here to Arms A/A_FIX/B/C.
5. **(Housekeeping, non-blocking)** Two independent, hand-maintained copies of the N6 hash/bundle-loading/validation logic exist (`n6_solar.py` and `stage7/.../artifacts/polaris_inference_runner.py`) — a drift risk if the model is ever re-frozen and only one copy is updated. Not fixed here to avoid touching more surface area than authorized; flagged for the project owner.

---

## 10. Next Authorized Action

The smallest safe next action is **not** running Experiment A. It is: the project owner reviewing and explicitly authorizing (or rejecting) the four items in Section 5/9.2 above — the reserve-shortfall ceiling, the solar-credit fraction cap, and whether/how `evaluator.py`/`worker.py` should call the new `reserve_policy_guard` module in production reporting. Only after that authorization should a separate, explicitly scoped task construct real `ScenarioSpec`/`ExperimentAConfig` objects from genuine historical data and actually execute Experiment A under human supervision — which still requires a further, separate authorization to lift the `CampaignExecutionNotAuthorizedError` gate this remediation deliberately left in place.
