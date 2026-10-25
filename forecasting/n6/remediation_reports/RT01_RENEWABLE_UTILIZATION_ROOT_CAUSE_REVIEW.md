# POLARIS — RT-01 Renewable-Utilization Root-Cause Review (Read-Only)

**Date:** 2026-10-18
**Nature of this document:** Twenty-first pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `RT01_OWNER_DECISIONS_GOVERNANCE_REPORT.md` (twentieth pass). Mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Scope confirmation up front:** This is a **pure, read-only investigation pass**. No code, test, config, register, or report file (other than this new file and its mirror) was edited. No assertion or threshold was relaxed — `renewable_utilization_pct >= 75.0` is untouched and stays exactly as written. No fuel capacity or refueling change was made or proposed as an edit. No full test suite, campaign, diesel comparison, training/tuning, or sealed/blind data was run or accessed. One narrow, explained re-derivation was performed from an **existing, already-committed scenario input file** (`system/data/scenarios/synthetic_168h_endurance_scenario.json`) using pure arithmetic (no pytest, no pipeline execution, no new artifact generated) — see Section 2 for exactly why and what. `RT-01` is **not** closed, the 75% floor is **not** claimed satisfied, and no implementation is authorized by this pass.

---

## 1. Exact metric definition and relevant code locations

`renewable_utilization_pct` is computed in `system/evaluation/evaluator.py::evaluate_ems_performance` (lines 142–149, 231–234):

```python
total_solar_used_wh += s          # plan["solar_used"]
total_wind_used_wh  += w          # plan["wind_used"]
total_curtailment_wh += c         # plan["renewable_curtailment"]
...
total_renewables_used_wh = total_solar_used_wh + total_wind_used_wh
total_renewables_avail_wh = total_renewables_used_wh + total_curtailment_wh
renewable_utilization_pct = (total_renewables_used_wh / total_renewables_avail_wh * 100.0) if total_renewables_avail_wh > 0 else 0.0
```

The denominator is **not** total forecast/actual irradiance-derived generation potential and **not** total demand — it is reconstructed purely from each `DispatchPlan`'s own `solar_used` + `wind_used` + `renewable_curtailment` fields, summed across the 168 executed H1 (closed-loop MPC first-action) steps. This is an internally self-consistent "of the renewable energy a dispatch plan itself accounted for as either used or curtailed, what fraction was used" ratio — it is only as good as the two solvers' own curtailment bookkeeping (Section 2).

The two solvers that populate those fields for this scenario:
- **`GAP19HighsNativeOptimizer`** (`system/optimization/implementations/gap19_highs_native.py`, PROTECTED) — MILP, used when `router.py` classifies the step `NORMAL`.
- **`OptionDFallbackSolver`** (`system/optimization/implementations/option_d.py`, PROTECTED) — heuristic, used when `router.py` classifies the step `EMERGENCY`.

`test_cumulative_physical_conservation_168h` (`system/tests/test_offline_runtime.py:496-548`) asserts `renewable_utilization_pct >= 75.0` unchanged; it observes **69.37%**, confirmed verbatim from the nineteenth-pass byte-exact run and reused unchanged (per directive) by the twentieth pass and this pass — no re-run was performed this pass for this number.

---

## 2. Evidence-backed explanation of the 69.37% result — known vs. unproven

### 2a. The metric itself is not the defect (verified)

Direct read of `evaluator.py` lines 231–234 (above) shows the formula is an honest used/(used+curtailed) ratio built symmetrically from each plan's own fields, not a mislabeled total/critical confusion like the separate `unmet_critical_load_kwh` issue the nineteenth pass fixed. This is a **different metric** from `unmet_critical_load_kwh`/`critical_unmet_source`, and the twentieth pass's Decision 2 already correctly declined to treat the two as the same finding. This pass's own code trace confirms that caution was warranted: they are computed from different plan fields (`solar_used`/`wind_used`/`renewable_curtailment` vs. `unmet_load`/`unmet_essential`) and have different proximate drivers (Section 2c vs. the already-closed diesel-exhaustion/Task-2 mechanism).

### 2b. `OptionDFallbackSolver` has no mechanism to route excess renewable energy to the battery (verified, structural)

Direct read of `option_d.py`:
- Lines 104–119: `p_ren_to_load = min(p_ren_avail, p_crit_demand)`; `p_curtail = max(0.0, p_ren_avail - p_ren_to_load)`. Any renewable generation above the step's demand figure is **unconditionally curtailed** — there is no code path anywhere in this function that routes surplus solar/wind into `p_chg` (battery charge).
- Lines 192–199 ("5. Excess Diesel Generation Battery Charging"): the **only** charging path in Option D is gated on `p_diesel > 0 and p_dis == 0` — i.e. charging is possible only from *excess diesel*, never from excess renewables.

By contrast, `gap19_highs_native.py`'s own MILP bus-bar constraint (lines 227–231) places `p_sol_used`/`p_wind_used` and `p_chg` on the **same side of one balance equation** (`p_sol_used + p_wind_used + p_dis + p_diesel - p_served - p_chg - p_flex = 0`), so GAP19's solver is mathematically free to direct surplus renewable power into `p_chg` instead of curtailment (`p_curt_sol`/`p_curt_wind`), subject to charge-power and SOC headroom limits. **This is a genuine, structural dispatch-capability asymmetry between the two solvers, confirmed by direct code read, not an inferred effect.**

### 2c. The scenario itself has substantial renewable-over-demand periods, not confined to the post-exhaustion tail (verified by direct computation on the existing scenario file)

**Why this computation was done, and why it did not require a pytest/pipeline run:** none of the existing reports record a per-step renewable-availability-vs-demand comparison for this scenario (only the unmet-load and reliability totals were previously reported). Answering "is the shortfall concentrated after hour 45, or scenario-wide?" needed that comparison. It was obtained by reading the committed scenario file (`system/data/scenarios/synthetic_168h_endurance_scenario.json`) and `system/config/solar_pv.yaml`'s own published conversion (`array_area_m2 * panel_efficiency * performance_ratio`, capped at `max_inverter_power_w`) with plain arithmetic — no code was executed, no test was run, no new artifact was produced.

Result: **renewable availability (solar + wind) exceeds `actual_demand` in 109 of 168 steps (64.9%)** — and this is **not confined to the post-exhaustion period**: 30 of the first 44 steps (the nominal pre-exhaustion window) already show renewable availability exceeding demand, alongside 79 of the remaining 124 steps. (Wind generation in this scenario is large and volatile — e.g. step 50 onward frequently shows 29–39 kW of wind alone against ~25–40 kW demand.)

### 2d. Re-examining *when* `EMERGENCY`/Option-D actually becomes active — this materially changes the causal picture (code-traced, with one unverified numeric step pending)

The prior passes' language ("167 of 168 steps route EMERGENCY ... after diesel exhausts at hour ~45") invites reading the renewable-utilization shortfall as a downstream consequence of literal fuel exhaustion. Direct trace of the **current** `router.py` → `ecd.py::evaluate()` (both PROTECTED, both read-only here, both hash-verified unchanged) shows this is likely not quite the right causal order:

- The 168h tests authorize routing with a **fixed, synthetic** `critical_load = 5000.0 W` and `t_required_hours = 6.0` (`test_offline_runtime.py:46-66`, `_authorize_router_for_offline_runtime_test`) — this is far below the scenario's real `actual_demand` (~20,000–40,000 W).
- `ecd.py::evaluate()` (lines 282–305) recomputes, **every step, from the current actual remaining fuel**, `t_diesel = available_fuel_l / (base_lph + marginal_lpwh * 5000)` = `available_fuel_l / 6.25` (using `diesel.yaml`'s `base_fuel_consumption_l_per_h=5.0`, `marginal_fuel_consumption_l_per_wh=0.00025`). `EMERGENCY` triggers as soon as `t_diesel < 6.0h`, i.e. as soon as **actual remaining fuel drops below ≈37.5 L** — not when it reaches 0 L.
- Because `diesel_power` under real `NORMAL`/GAP19 dispatch serves the *actual* ~20–40 kW demand (not the 5000 W fixture value used only for the survivability-margin arithmetic), the tank plausibly crosses the 37.5 L margin-trigger threshold within the first several hours of the run — **long before** the literal zero-fuel exhaustion previously pinned to step ~44.
- This would mean `OptionDFallbackSolver` (Section 2b's structurally curtailment-prone solver) is likely the active dispatcher for nearly the **entire** 168-hour run — consistent with the prior "167 of 168 steps" figure — and that the literal fuel-exhaustion event at step ~44 is a *later* milestone **inside** an already-EMERGENCY regime (Option D itself keeps drawing diesel in its `DIESEL`/`BOTH` preserved-resource branches until the tank is actually empty), not the trigger for entering it.

**What this does and does not establish:** the margin arithmetic above (≈37.5 L crossover, "within the first several hours") is derived directly from the governing code and config constants and is not guessed, but it has **not been confirmed against an actual per-step trace of `diesel_fuel_remaining_liters` or `operating_mode` for this exact scenario run** — doing so would require either re-running the pipeline (explicitly out of scope this pass) or reading a previously-saved full per-step trace, which no existing artifact in this repository currently contains (the saved `run_report.json`/`latest_dispatch_plan.json` artifacts on disk are from an unrelated 12-step demo run, not the 168h scenario, and only carry the final aggregate values, not a step-by-step `operating_mode` log). **This is flagged as the single most important open factual question this review could not close without a targeted re-run**, and no re-run was performed per the directive's instruction to explain before running anything — this report stops at explaining why, rather than running it.

### 2e. Synthesis — distinguishing the two RT-01 failures' root causes, not assuming they are one

Putting 2a–2d together:
- `test_long_duration_closed_loop_endurance_168h` (`90.04% != 100.0%` reliability) is tied to the literal, confirmed-at-step-44 fuel-exhaustion event and the 43 subsequent genuinely-unmet-load steps (eighteenth pass, independently re-verified unchanged here via hash check, not re-run).
- `test_cumulative_physical_conservation_168h`'s renewable-utilization shortfall (`69.37% < 75.0%`) is best explained by `OptionDFallbackSolver`'s **structural inability to charge the battery from surplus renewable generation** (Section 2b, verified by code), combined with the scenario's substantial renewable-over-demand periods occurring **throughout** the run, not only after hour 45 (Section 2c, verified by computation), and with Option D plausibly being the active solver for nearly the whole run **because of the survivability-margin formula**, not strictly because of literal fuel exhaustion (Section 2d, code-traced but not step-trace-confirmed).

These are evidenced as **related but mechanistically distinct** findings — exactly the distinction the twentieth pass's Decision 2 already preserved by refusing to treat the renewable-utilization and endurance-reliability failures as one problem. This review's own contribution is to show that the renewable-utilization shortfall's proximate cause (Option D's no-renewable-to-battery-charging architecture, active for most of the run) does not even require literal fuel exhaustion to occur — it would plausibly persist even if Task 2's fuel-capacity dependency were resolved (Option (a)/(b)), **unless** the EMERGENCY-routing margin trigger or Option D's charging logic were also addressed. This directly contradicts any assumption that fixing fuel capacity alone would be expected to restore `>= 75.0%` — the twentieth pass already declined to assume this, and this review's evidence reinforces that caution rather than resolving it.

---

## 3. Ranked minimal remedies (none implemented; effect stated as hypothesis unless already demonstrated)

| Rank | Remedy | Mechanism | Evidence status | Files touched | Protected? | Risk | Min. approval needed |
|---|---|---|---|---|---|---|---|
| 1 | **Give `OptionDFallbackSolver` a renewable-to-battery charging path** (mirror GAP19's bus-bar logic: allow surplus `p_ren_avail - p_ren_to_load` to charge the battery, bounded by `max_chg_w` and SOC headroom, before falling back to curtailment) | Directly closes the structural gap identified in Section 2b | **Hypothesis** — mechanism is verified (no such path exists today); the resulting utilization number after the fix is not. Section 2c's 64.9% renewable-over-demand-step figure suggests the addressable curtailment pool is large, but the actual Wh recovered depends on battery headroom/charge-power limits at each of those steps, which were not computed this pass | `system/optimization/implementations/option_d.py` only | **Yes** (PROTECTED_FILES) | Medium — new code path in the protected heuristic fallback solver; needs the same conservation/SOC-bounds/no-double-counting correctness review this register already requires for any Option-D change (cf. the fourteenth-pass diesel-floor repair's own review standard) | Full Section-6 protected-file governance review, specifically scoped to this one change |
| 2 | **Re-examine the EMERGENCY-routing margin trigger for this scenario class** (the 5000 W synthetic test-fixture critical-load value used for the *survivability margin* calculation vs. the real ~20–40 kW demand GAP19 actually serves under NORMAL mode causes an early EMERGENCY trip, per Section 2d) | If EMERGENCY triggers later (or not until fuel is genuinely critical), more of the run would use GAP19, which can avoid curtailment via battery charging | **Hypothesis, less certain than remedy 1** — the margin arithmetic is code-derived but the actual trigger timing is unconfirmed (Section 2d); also, this governs *safety-relevant* routing (ECD-01/HD-03), so any change here has much broader safety implications than a narrowly-scoped Option-D edit, and this review takes no position on whether the current fixture-based routing choice is itself correct for other reasons (e.g. deliberately conservative) | `system/tests/test_offline_runtime.py` (fixture values) and/or `system/control/router.py`/`ecd.py` config contract, depending on form | Possibly (if `router.py`/`ecd.py` logic itself changes; fixture-only change would not touch PROTECTED_FILES) | High if it touches `router.py`/`ecd.py` — this is the same fail-closed safety boundary ECD-01/HD-03 already governs; low if limited to the test fixture's own synthetic critical-load value, but that would itself need owner sign-off since it changes what the test is authorized to represent | Owner decision + (if code changes) full Section-6 review; this is **not** the same review window as remedy 1 and should not be bundled with it without separate scoping |
| 3 | **Accept 69.37% as a documented, owner-accepted scenario-design limitation and relax the assertion** | Satisfies RT-01's own closure-test branch (B) if the owner explicitly accepts and authorizes relaxing the assertion | Zero engineering risk; already available per the closure_test's own disjunctive wording | None (test-only, and only if owner explicitly authorizes relaxing this specific assertion) | No | None | Owner sign-off explicitly accepting the residual **and** explicitly authorizing the assertion to be relaxed — the twentieth pass's Decision 2 already explicitly declined exactly this for now |
| 4 | **Re-run the 168h pipeline once, read-only diagnostic, to log per-step `operating_mode`/`diesel_fuel_remaining_liters`/curtailment** | Would close the one open factual question in Section 2d and quantify remedy 1's expected recovered Wh precisely, before committing to any protected-file edit | N/A — this is a diagnostic proposal, not a remedy to the metric itself | None (diagnostic artifacts only) | No | Low (same class of read-only diagnostic run already authorized multiple times in this register's history, e.g. eighteenth pass) | Owner authorization to run one bounded, read-only 168h diagnostic (not a fix, not a campaign) — explicitly the kind of "specific unresolved question" the governing directive allows explaining-before-running for, but this pass did not do so, leaving it as the first concrete next step rather than performing it |

No remedy above has been implemented, and none is authorized by this review.

---

## 4. Metric or scenario-design issues needing separate owner adjudication

1. **Scenario-design question, not a code defect:** this scenario's wind resource is large and frequently exceeds demand (64.9% of all steps, not just post-exhaustion ones — Section 2c). Section 1's reference `run_report.json` artifact (a different, 12-step demo scenario, read only as corroborating context) independently shows `renewable_utilization_pct = 70.97%` with real curtailment even on a short run without any EMERGENCY/fuel-exhaustion involvement at all. This raises an open question this review cannot adjudicate: **is `>= 75.0%` achievable at all for this scenario's resource mix under correct (non-Option-D) dispatch**, or does the battery's 200 kWh capacity / 50 kW charge-power ceiling cap achievable utilization below 75% even under ideal GAP19-only dispatch? This is a scenario-capacity/floor-calibration question, separate from any dispatch bug, and is flagged for owner adjudication rather than assumed either way.
2. **Routing-governance question, not purely an RT-01 matter:** Section 2d's finding — that the EMERGENCY-routing margin trigger for this test's own synthetic fixture values plausibly activates `OptionDFallbackSolver` far earlier than literal fuel exhaustion — touches the already-governed ECD-01/HD-03 routing contract. This review does not recommend any change to that contract; it only reports that the contract's current test-fixture parameterization (5000 W / 6h) has this downstream effect on renewable utilization, which may be worth the owner's separate awareness independent of whatever is decided about remedy 1 or 2 above.

---

## 5. Exact next decision required from the owner

Choose one (or defer again, explicitly):
(a) Authorize a **Section-6 protected-file governance review scoped only to remedy 1** (a renewable-to-battery charging path inside `OptionDFallbackSolver`), understanding its effect on `renewable_utilization_pct` is a hypothesis, not a demonstrated fix; or
(b) Authorize the **narrow, bounded, read-only diagnostic re-run** described as remedy 4, to first quantify the actual per-step `operating_mode`/fuel/curtailment trace before committing to any protected-file change; or
(c) Reaffirm the twentieth pass's Decision 2 (69.37% remains open, unaccepted, unrelaxed) with no further action at this time; or
(d) Direct that the Section 4 scenario-design/floor-calibration question be adjudicated first, since its answer could make remedy 1 by itself insufficient regardless of implementation quality.

This review takes no position on which the owner should choose and implements none of them.

---

## 6. Confirmation — read-only, protected hashes unchanged

- No code, test, config, register, or report file was edited by this pass other than this new file and its `N6_REMEDIATION_REPORTS/` mirror.
- The only non-reading action taken was arithmetic performed directly on the already-committed `system/data/scenarios/synthetic_168h_endurance_scenario.json` and `system/config/solar_pv.yaml` values (Section 2c) — no pytest, no pipeline (`PolarisLocalRunner`/`run_pipeline`), no diagnostic script, and no campaign/replay harness was invoked.
- All 7 `PROTECTED_FILES` entries were re-hashed (read-only) this pass and found **byte-identical** to the v1.9.10-recorded values:

| File | SHA-256 | Match |
|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | match |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | match |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | match |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | match |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | match |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | match |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | match |

- `winner: null` (`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json`) — confirmed present/unchanged, read-only.
- The campaign-execution guard (`CampaignExecutionNotAuthorizedError` in `system/evaluation/replay_harness.py`) — confirmed present and unconditional, read-only, not invoked.
- `DSL-01`'s `epsilon_tol` — confirmed still deferred/unset in the register, read-only, not touched.
- `diesel.yaml` — confirmed unchanged, still carries no `initial_fuel_l` key.
- No sealed 2025 blind data, no frozen Stage 8.1/N6 asset, was accessed or changed.
- Nothing was staged, committed, or pushed.

**RT-01 remains OPEN.** This pass does not close it, does not claim `renewable_utilization_pct >= 75.0%` is satisfied, and authorizes no implementation. It adds one evidence-backed refinement to the existing record: the renewable-utilization shortfall's most likely proximate cause is `OptionDFallbackSolver`'s structural lack of a renewable-to-battery charging path, compounded by that solver plausibly being active for nearly the entire 168-hour run (not only after literal fuel exhaustion) — a distinction from, not an identity with, the separately-tracked fuel-exhaustion/endurance-reliability failure, consistent with the twentieth pass's own refusal to conflate the two.
