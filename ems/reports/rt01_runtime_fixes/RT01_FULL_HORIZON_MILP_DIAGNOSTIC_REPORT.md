# POLARIS — RT-01 Full-Horizon MILP Diagnostic Report (Evidence Only)

**Date:** 2026-10-18
**Nature of this document:** Bounded, ONE-TIME, owner-authorized evidence-gathering pass ("POLARIS — RT-01 Full-Horizon MILP Diagnostic (Evidence Only)"), continuing directly from `RT01_STEP0_MILP_DISPATCH_ROOT_CAUSE_REVIEW.md` (mirrored in `N6_REMEDIATION_REPORTS/`). This pass resolves the H1/H2/H3 uncertainty that review left open by capturing the full 24-hour MILP problem and solution for the existing step-0 scenario. **No source, test, config, register, or existing-report file was edited. No fix is implemented. RT-01 remains OPEN.**

---

## 1. Exact command / scope executed

```
python3 research/rt01_diagnostics/trace_step0_full_horizon.py
```

New file written: `research/rt01_diagnostics/trace_step0_full_horizon.py` (diagnostic harness). It:
1. Constructs `PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")` exactly as `trace_168h_endurance_scenario.py` and `test_offline_runtime.py` do, and applies the same pre-existing, already-authorized `_authorize_router_for_offline_runtime_test` fixture.
2. Reproduces **only** `run_pipeline()`'s `step_idx == 0` setup by hand (identical `StationState` construction to `runner.py` lines 97–109, `data_provider.get_runtime_state(0)`, `forecast_engine.predict(...)`), **without calling `run_pipeline()`** — so `runner.artifacts_dir` (`system/artifacts/*.json`) is never opened for writing. This is the key difference from the prior script and the reason production artifacts are untouched.
3. Calls `router.evaluate_and_route(...)` once, for confirmation only (route was not used to branch; the real, unmodified `LocalMILPEnergyOptimizer.optimize()` is called regardless, since the prior trace already established step 0 of this scenario routes NORMAL/MILP).
4. Calls the real, unmodified `runner.optimizer.optimize(bundle, initial_state, runner.configs)` **exactly once**.
5. To capture the full 24-hour decision vector (not just the rounded, binary-stripped `DispatchPlan` arrays), it monkey-patches the module-level name `system.optimization.implementations.milp.milp` — the `scipy.optimize.milp` reference that `LocalMILPEnergyOptimizer.optimize()` calls internally — with a thin wrapper that calls the **original, unmodified** scipy solver with the same arguments, records `c`, `integrality`, bounds, constraints, and the full `OptimizeResult` (`res.x`, `res.fun`, `res.status`, `res.message`), and returns the result unchanged. This is in-process attribute shadowing only; no file on disk is edited, and the real HiGHS solver computes the real answer — we only observe it. The patch is restored immediately after the single call.

**No 168-hour (or any multi-step) pipeline was run. Exactly one optimizer solve was executed.**

Outputs created (all under `research/rt01_diagnostics/`, isolated from production artifacts):
- `trace_step0_full_horizon.py` (the script)
- `rt01_step0_full_horizon_trace.json` (full capture: config, solver result, objective breakdown, 24-row horizon table, hash manifests)
- `rt01_step0_full_horizon_trace.csv` (24-row horizon table)

`system/artifacts/latest_dispatch_plan.json`, `latest_forecast_bundle.json`, and `run_report.json` were **not opened** by this script (confirmed by code inspection: the script contains no reference to `artifacts_dir`).

---

## 2. Input/config hashes

SHA-256 hashes of every file this diagnostic depends on, or whose immutability matters for governance, were recorded **before** and **after** execution (`pre_execution_hash_manifest` / `post_execution_hash_manifest` in the JSON output). Hashed files: `milp.py`, all six `PROTECTED_FILES` entries (`gap19_highs_native.py`, `option_d.py`, `ecd.py`, `router.py`, `simulator.py`, `runner.py`), `manifest.py`, `optimizer.yaml`, `battery.yaml`, `diesel.yaml`, `loads.yaml`, `solar_pv.yaml`, `station.yaml`, and the scenario file `synthetic_168h_endurance_scenario.json`.

**Result: `hash_diffs_detected: {}` — zero files changed.** All protected files, `milp.py`, every config file, and the scenario file are byte-for-byte identical before and after this run.

Live config values confirmed in use (identical to the prior review): `renewable_curtailment_penalty_per_wh = 0.05`, `deg_penalty_per_wh = 0.00005` (1000:1 ratio), `max_soc_pct = 95.0`, `min_soc_pct = 20.0`, `max_charge_power_w = 50000.0`, `max_discharge_power_w = 50000.0`, `charge_efficiency = discharge_efficiency = 0.92`.

---

## 3. Was the 24-hour plan and objective decomposition captured?

**Yes, fully.** `res.fun` (total objective) = **14,296.383046**. The independently reconstructed per-family, per-timestep breakdown (`c[idx] * sol[idx]` summed over all 24 timesteps and all cost-bearing variable families) sums to **14,296.383045507...** — matching `res.fun` to within 1e-3, confirming the decomposition is exact and complete:

| Family (24h total, $) | Value |
|---|---|
| Curtailment — solar | 4,353.05 |
| Curtailment — wind | 9,918.84 |
| Battery charge cycling | 15.51 |
| Battery discharge cycling | 8.99 |
| Diesel marginal fuel | 0.00 |
| Diesel base/startup | 0.00 |
| Unmet load | 0.00 |

Diesel and unmet load are zero throughout the 24-hour horizon — the entire objective is driven by curtailment (97.9%) and battery cycling (2.1%).

The full 24-hour forecast (`solar_generation.point`, `wind_generation.point`, `demand.point`) and full 24-hour solution (`solar_used`, `wind_used`, `battery_charge`, `battery_discharge`, `battery_soc`, `diesel_power`, `load_served`, `unmet_load`, `renewable_curtailment`, plus the raw pre-rounding solver values for every variable including the four binaries) are recorded in `rt01_step0_full_horizon_trace.json`/`.csv`, one row per hour 0–23.

---

## 4. The actual 24-hour trajectory

| t | Renewable fc (W) | Demand (W) | Surplus (W) | Charge | Discharge | SOC % | Curtailed (W) |
|---|---|---|---|---|---|---|---|
| 0 | 33,100 | 27,448 | +5,652 | 0 | 27,448 | 35.08 | **33,100** |
| 1 | 34,930 | 27,148 | +7,782 | 0 | 27,148 | 20.33 | **34,930** |
| 2 | 35,600 | 26,672 | +8,928 | 8,928 | 0 | 24.43 | 0 |
| 3 | 34,930 | 26,050 | +8,880 | 5,776 | 0 | 27.09 | 3,103 |
| 4 | 39,070 | 25,327 | +13,743 | 13,743 | 0 | 33.41 | 0 |
| 5 | 42,310 | 24,550 | +17,760 | 0 | 24,550 | 20.07 | **42,310** |
| 6 | 45,100 | 23,774 | +21,326 | 21,326 | 0 | 29.88 | 0 |
| 7 | 47,907 | 23,050 | +24,857 | 24,857 | 0 | 41.32 | 0 |
| 8 | 51,043 | 22,429 | +28,614 | 0 | 32,429 | 23.69 | **51,043** |
| 9 | 54,541 | 21,952 | +32,588 | 22,588 | 0 | 34.08 | 0 |
| 10 | 58,112 | 21,653 | +36,459 | 36,459 | 0 | 50.85 | 0 |
| 11 | 61,200 | 21,550 | +39,650 | 39,650 | 0 | 69.09 | 0 |
| 12 | 63,112 | 21,653 | +41,459 | 41,459 | 0 | 88.16 | 0 |
| 13 | 63,201 | 21,952 | +41,249 | 0 | 31,952 | 70.80 | **63,201** |
| 14 | 61,043 | 22,429 | +38,614 | 38,614 | 0 | 88.56 | 0 |
| 15 | 56,567 | 23,050 | +33,517 | 0 | 33,050 | 70.60 | **56,567** |
| 16 | 50,100 | 23,774 | +26,326 | 26,326 | 0 | 82.71 | 0 |
| 17 | 42,310 | 24,550 | +17,760 | 17,760 | 0 | 90.88 | 0 |
| 18 | 34,070 | 25,327 | +8,743 | 8,743 | 0 | 94.90 | 0 |
| 19 | 26,270 | 26,050 | +220 | 220 | 0 | 95.00 | 0 |
| 20 | 25,600 | 26,672 | −1,072 | 0 | 2,254 | 93.77 | 1,183 |
| 21 | 26,270 | 27,148 | −879 | 0 | 879 | 93.30 | 0 |
| 22 | 28,100 | 27,448 | +652 | 652 | 0 | 93.60 | 0 |
| 23 | 30,600 | 27,550 | +3,050 | 3,050 | 0 | 95.00 | 0 |

Total 24h curtailment: **285,437.8 Wh** (252,337.8 Wh after hour 0). Battery SOC: 50.0% → 35.08% (hour 0) → down to 20.07–20.33% twice more (hours 1, 5) → up to the 95% ceiling by hour 18–19, staying pinned there through most of hours 18–23. Final SOC: 95.0% (net +45 points vs. the 50% start).

---

## 5. Does the solution charge the battery later from otherwise-curtailed renewables, and does that quantifiably justify the hour-0 choice?

**Partially yes on the mechanism, but no on the magnitude — this does not explain the decision.**

The battery is charged in 16 of the 23 remaining hours, and it does hit the 95% SOC ceiling at hours 18, 19, and 23 — so battery capacity genuinely does become binding later in the horizon, which is the structural precondition H1 requires. But the pattern is **not** a one-time "discharge now, recharge later from a surge" trade — it **repeats seven separate times** across the horizon (hours 0, 1, 5, 8, 13, 15, 20), each time curtailing the *entire* available renewable at that hour while simultaneously discharging the battery to cover demand that the same renewable could have covered directly, for zero cost, with no discharge at all:

| t | Actual cost (curtail+cycle, $) | Cost if renewable used directly, battery left alone ($) | Excess ($) |
|---|---|---|---|
| 0 | 1,656.37 | 282.59 | **1,373.78** |
| 1 | 1,747.87 | 389.08 | **1,358.78** |
| 5 | 2,116.74 | 887.99 | **1,228.75** |
| 8 | 2,553.77 | 1,430.69 | **1,123.08** |
| 13 | 3,161.65 | 2,062.43 | **1,099.21** |
| 15 | 2,830.02 | 1,675.85 | **1,154.17** |
| 20 | 59.25 | 0.05 | **59.19** |
| **Total** | | | **$7,396.97** |

An upper-bound estimate of the *maximum* plausible one-time benefit from the hour-0 discharge freeing battery headroom (computed only from the already-observed charge rate and ceiling-hit timing — no counterfactual re-solve was run): discharging 27,448.19 Wh at hour 0 shifts the ceiling-hit time by at most ≈0.6 hours of charging at the configured 50 kW / 0.92-efficiency rate, i.e. at most ≈46,000 Wh of additional curtailment could plausibly be avoided across the *entire* horizon as a result — worth at most **≈$1,492** in avoided curtailment penalty, one time.

That ≈$1,492 ceiling is already almost entirely consumed by hour 0's own $1,373.78 excess alone. It cannot explain the other six occurrences of the identical pattern, which together account for an additional **≈$6,023** of excess cost with no plausible multi-period justification — there is only one SOC-ceiling event to "buy headroom for," not seven.

**A direct, non-degenerate dominance violation was also found at hour 20**, independent of any horizon-shifting argument: at t=20 the solution uses only 24,417.38 W of the available 25,600.04 W of wind (curtailing 1,182.66 W) while simultaneously discharging 2,254.35 Wh of battery to cover the same hour's demand. Swapping 1,182.66 Wh from "curtailed" to "used" and reducing discharge by the identical 1,182.66 Wh is bus-bar-neutral (same demand served, same net energy balance), leaves the battery with *more* stored energy afterward (strictly better for every future hour, not worse), and reduces this single hour's cost by $59.19 under the model's own stated objective — with **no downside of any kind**. This proves the solution HiGHS returned, labeled `status=0`/`"OPTIMAL"`, is **not actually the cost-minimal point of its own stated LP/MILP** — at least one strictly-dominated choice survived into the "optimal" solution.

---

## 6. H1 / H2 / H3 classification

- **H1 (legitimate multi-period shifting): Not supported as a sufficient explanation.** The structural precondition (battery does hit its SOC ceiling later in the horizon) is present, but the magnitude test fails by roughly 5x: total unexplained excess across the seven discharge-and-full-curtail events is $7,397, while the most generous possible one-time multi-period benefit is bounded at ≈$1,492 — and that single bound cannot cover seven separate occurrences of the pattern. H1 is rejected as the primary or sufficient driver of the observed behavior, though it may contribute a small fraction of the hour-0 decision's apparent rationale.
- **H2 (formulation/solver defect): Supported by direct evidence.** The hour-20 swap is a strict, zero-downside, zero-counterfactual-solve dominance violation computed purely from the arithmetic of the actual returned solution and the model's own published cost coefficients. A solution containing a provably-improvable point cannot be the true global optimum of the stated problem, regardless of what HiGHS's `status`/`success` flags report. This is hard evidence that *something* in the formulation-plus-solver pipeline (most likely: degenerate/near-degenerate LP relaxation vertices created by the zero-reward-on-usage, positive-cost-on-curtailment structure, combined with scipy's default MIP gap/branch-and-bound tie-breaking) is allowing provably dominated choices to survive into the reported "optimal" solution. This pass did not isolate whether the defect sits in `milp.py`'s constraint/objective construction, in an unreviewed interaction with HiGHS's default solver tolerances, or both — that would require further, separately-authorized investigation (e.g. inspecting HiGHS's solve log / MIP gap, or testing whether a tighter gap tolerance changes the returned solution), which is out of this pass's scope since it would require changing solver options.
- **H3 (penalty miscalibration alone, solver correctly optimizing a bad-but-internally-consistent cost model): Not a sufficient standalone explanation.** The 1000:1 curtailment:cycling ratio is real and does make this kind of waste cheap in dollar terms (it is why the hour-20 violation is only $59 while hour-0-style violations are ~$1,100–1,400 each), but H3 as stated requires the solver to be *correctly* following its own incentive structure. The hour-20 case shows the solver failing to find even its own stated optimum under the existing (admittedly miscalibrated) cost model — that is a solver/formulation defect riding on top of the miscalibration, not the miscalibration acting alone. The two are entangled: the penalty ratio determines how *expensive* each dominated choice is, while H2's mechanism determines *whether* such dominated choices get left in the returned solution at all.
- **Inconclusive items:** The exact mechanism inside the solver/formulation producing the degeneracy (why these particular 7 of 24 hours, and not others, ended up with the full-curtail-and-discharge pattern) was not isolated in this pass and would need deeper solver-internals inspection to resolve — flagged as the next open question, not resolved here.

---

## 7. Smallest defensible next step

1. **Before any remedy is chosen:** re-run this same single step-0 solve (no config change) with `scipy.optimize.milp`'s `options={"mip_rel_gap": 0.0}` (or inspect HiGHS's solve log/B&B gap at termination) to determine whether tightening the gap removes the hour-20-style dominance violations. This is diagnostic-only (no parameter affecting dispatch economics changes — only solver *tolerance*), low-risk, and would directly distinguish "H2 is a solver-tolerance artifact" from "H2 is a genuine LP/MILP formulation degeneracy that persists even at a provably tight gap." **This itself needs separate owner authorization**, since it is an additional solver invocation beyond this pass's single authorized call.
2. Independently of (1), the magnitude evidence in Section 5 already stands on its own and does not require further runs: H1 cannot explain the bulk of the observed excess cost regardless of what (1) finds, so any remedy design can proceed without waiting on root-mechanism isolation of H2, if the owner prefers to prioritize Item 1/2 from the prior review's Section 3 (reward direct renewable usage explicitly, and/or recalibrate the penalty ratio) ahead of a deeper solver-internals investigation.
3. **Expected regression risk of any future remedy:** unchanged from the prior review's Section 3/4 — any objective-coefficient or constraint change to `milp.py` is local to that file and the three un-protected config YAMLs, but needs re-validation against the existing MILP-path test suite and the 168h endurance scenario (`renewable_utilization_pct`, `system_reliability_pct`, `total_diesel_fuel_liters`) before merge, per the prior review's Section 5 Item 4.
4. **Further evidence that would still help, if authorized:** (a) the gap-tolerance test in Item 1 above; (b) repeating this same full-horizon capture at a handful of *other* MILP-routed steps elsewhere in the 168h run (not just step 0) to see whether the full-curtail-and-discharge pattern recurs at a similar rate under different forecast/SOC starting conditions, which would further strengthen or weaken the "structural, not one-off" characterization of H2.

No remedy is implemented or recommended by name in this pass. RT-01 remains **OPEN**.

---

## 8. Confirmation of protected files and governance state

- All six `PROTECTED_FILES` entries (`router.py`, `ecd.py`, `option_d.py`, `gap19_highs_native.py`, `simulator.py`, `runner.py`), `manifest.py`, `milp.py`, every config YAML read by this diagnostic, and the `synthetic_168h_endurance_scenario.json` scenario file are **byte-identical before and after this run** (Section 2; `hash_diffs_detected: {}`).
- No parameter, threshold, routing/ECD behavior, fuel policy, `winner` status, the 75% renewable-utilization floor, or the campaign guard was touched, read-modified, or exercised beyond a single observational call to `router.evaluate_and_route` (consistent with the already-authorized prior trace script's pattern).
- No training, tuning, campaign, or sealed/blind-2025 data was accessed.
- Nothing was staged, committed, or pushed by this pass.
- The only filesystem changes made by this pass: `research/rt01_diagnostics/trace_step0_full_horizon.py`, `research/rt01_diagnostics/rt01_step0_full_horizon_trace.json`, `research/rt01_diagnostics/rt01_step0_full_horizon_trace.csv`, this report, and its mirror in `N6_REMEDIATION_REPORTS/`. `system/artifacts/*.json` production artifacts were never opened.
