# POLARIS — RT-01 Step-0 MILP Dispatch Root-Cause Review (Read-Only)

**Date:** 2026-10-18
**Nature of this document:** Continuation pass, following directly from `RT01_168H_BOUNDED_DIAGNOSTIC_REPORT.md` (mirrored in `N6_REMEDIATION_REPORTS/`) and the owner's verbatim "Step-0 MILP Dispatch Root-Cause Review (Read-Only)" directive. This is a **read-only code/evidence review**. No source, test, config, register, or report file was edited. No pipeline, campaign, test suite, training, or tuning was run. No threshold, routing/ECD behavior, fuel policy, or `PROTECTED_FILES` entry was touched. `winner: null`, the campaign guard, deferred `DSL-01` `epsilon_tol`, frozen assets, and blind-data restrictions are all unchanged. Nothing staged, committed, or pushed. RT-01 remains **OPEN**; no fix is implemented or authorized by this pass.

---

## 0. Confirmed file status

`LocalMILPEnergyOptimizer` lives in `system/optimization/implementations/milp.py`. `system/orchestration/manifest.py`'s `PROTECTED_FILES` constant (lines 10–17) lists exactly six entries:
```
system/optimization/implementations/gap19_highs_native.py
system/optimization/implementations/option_d.py
system/control/ecd.py
system/control/router.py
system/simulation/simulator.py
system/runtime/runner.py
```
`system/optimization/implementations/milp.py` is **not** in this list. The prior diagnostic report's claim that it is unprotected is **confirmed directly from the manifest source**, not just trusted. (Note: the prior report's Section 6 hash table lists 7 rows because it also hashes `manifest.py` itself; the actual `PROTECTED_FILES` array it enforces has 6 entries, consistent with the above.) A fix to `milp.py` therefore does **not** require the protected-file governance review that `option_d.py`/`ecd.py`/`router.py`/etc. would require — see Section 5 (Item 2) below for what it still needs.

---

## 1. Exact code locations and mathematical explanation

**File:** `system/optimization/implementations/milp.py`, class `LocalMILPEnergyOptimizer.optimize()` (lines 16–417).

**Observed step-0 facts (from `research/rt01_diagnostics/rt01_168h_trace.json`, record `step: 0`):** `forecast_wind_h1_w=33100.04`, `forecast_solar_h1_w=0.0`, `forecast_demand_h1_w=27448.19`; plan: `wind_used=0.0`, `renewable_curtailment=33100.04`, `battery_discharge=27448.19`, `diesel_power=0.0`, `load_served=27448.19`, SOC 50.0% → 35.08%. `constraint_status="OPTIMAL"` (i.e. HiGHS returned `res.success=True`, not an infeasibility fallback).

**Relevant objective terms (lines 111–118), with t the horizon index 0..23 and `w_t = gamma**t`, `gamma=1.0` by default (confirmed: `system/config/optimizer.yaml` sets no `horizon_discount_factor_gamma`, no `custom_weight_vector`, no `v4g_single_horizon_mode`, so `w_t ≡ 1.0` for all t):**
- `p_sol_used` (idx 0) and `p_wind_used` (idx 1): **objective coefficient 0** — using renewable energy to serve load is not directly rewarded.
- `p_curt_sol`/`p_curt_wind` (idx 2,3): coefficient `curt_penalty_per_wh * dt`. **Actual configured value: `curt_penalty_per_wh = 0.05` $/Wh**, read from `config["optimizer"]["weights"]["renewable_curtailment_penalty"]` (`system/config/optimizer.yaml` line 6: `renewable_curtailment_penalty: 0.05`) — not the code's own fallback default of `0.001` (line 54). The live config value is used.
- `p_chg`/`p_dis` (idx 4,5): coefficient `deg_penalty * dt`. **Actual configured value: `deg_penalty = 0.00005` $/Wh**, read from `battery.yaml`'s `deg_penalty_per_wh` (line 11), applied identically to charging and discharging.
- `p_diesel` (idx 7), `u_diesel` (idx 13), `v_start` (idx 14): diesel fuel/startup costs — not invoked at step 0 (`diesel_power=0`, `u_diesel=0`), irrelevant to this decision.
- `p_unmet` (idx 9): `unmet_penalty_per_wh=10.0` $/Wh default — not triggered (`unmet_load=0`).

**Key structural fact:** the ratio `curt_penalty_per_wh / deg_penalty = 0.05 / 0.00005 = 1000`. Curtailing a Wh of renewable energy costs the objective **1000× more** than cycling (charging or discharging) a Wh through the battery.

**Bus-bar balance (constraint 3, lines 175–186):** `p_sol_u + p_w_u + p_dis + p_dies − p_serv − p_chg − p_flx = 0` — confirms the sign convention the prior report cited: renewables and battery discharge and diesel are sources (positive), load served, charging, and flexible load are sinks (negative). This is a correct, standard same-side formulation; no sign-convention defect was found here.

**Demand balance (constraint 4):** `p_serv + p_unmet = p_dem`.
**Renewable decomposition (constraints 1–2):** `p_sol_u + p_curt_sol = p_sol_max`, `p_wind_u + p_curt_wind = p_wind_max` — curtailment and usage are forced to exhaust the full forecast generation, so "not using" wind is always accounted as curtailment, never simply omitted.

**Arithmetic comparison of the chosen plan against the locally cheaper alternative, holding everything else in the single step fixed:**

| Dispatch choice at t=0 | Cost (this step alone, in the solver's own $ units) |
|---|---|
| **Actual MILP output:** curtail all 33,100.04 Wh of wind, discharge 27,448.19 Wh from battery, serve load from battery | `0.05×33,100.04 + 0.00005×27,448.19` ≈ **$1,656.37** |
| **Locally cheaper alternative:** use wind directly for the 27,448.19 Wh of demand, curtail only the 5,651.85 Wh surplus, leave battery untouched | `0.05×5,651.85` ≈ **$282.59** |

The actual chosen single-step cost is **≈5.9× higher** than the straightforward "use free wind first" alternative, for the same demand served and the same diesel state. A `scipy.optimize.milp` call with no explicit time limit or relaxed gap tolerance (none is passed at line 297: `milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)`) solves a problem this size (24×15=360 variables) to proven global optimality against its **full 24-hour objective**, not just hour 0 in isolation — so this gap is either (a) justified by something in hours 1–23 of the same horizon solve that this trace does not capture, or (b) a sign of a defect elsewhere in the formulation that was not found in the sections of the code inspected (bounds, constraints 1–11, and the fuel-budget constraint were all read in full and found self-consistent for t=0; see Section 2 for exactly what remains unverified).

---

## 2. Proven causes vs. hypotheses vs. missing evidence

**Proven (directly from code + trace, no inference required):**
- The objective gives **zero direct reward** for using solar/wind to serve load; renewables are only indirectly favored via the curtailment penalty on the *unused* portion.
- The configured curtailment penalty (0.05 $/Wh) is **1000× the configured battery cycling penalty** (0.00005 $/Wh) per the live `optimizer.yaml`/`battery.yaml` values actually passed into `milp.py` at runtime.
- The bus-bar balance and renewable-decomposition constraints are correctly signed and were not found defective for t=0.
- HiGHS returned `res.success=True` / `"OPTIMAL"`, not an infeasibility/fallback path, so the degenerate all-curtail-then-discharge plan was returned by the solver as the (claimed) optimal solution to whatever problem it was actually given.
- `LocalMILPEnergyOptimizer` is a full 24-hour receding-horizon MILP (`H=24`), but `research/rt01_diagnostics/trace_168h_endurance_scenario.py` (lines 141–242) **only records index `[0]` of the forecast bundle and the returned `DispatchPlan` arrays** — confirmed directly from the diagnostic script's own capture code. It does **not** record the hour-1-through-23 forecast inputs or planned dispatch that the MILP solved over at step 0.

**Hypotheses (plausible, consistent with the proven facts, but NOT distinguishable from each other using only this pass's evidence):**
- **H1 — Legitimate (if economically questionable) multi-period trade-off:** if the forecast fed to the step-0 solve shows continued high wind (or solar) later in the same 24-hour horizon that would otherwise be curtailed at the 1000×-higher penalty, the MILP could be using the cheap battery-discharge-now / recharge-later cycle to shift energy out of an hour where it would be curtailed anyway into a later hour, reducing total 24-hour objective cost even though it looks perverse at hour 0 alone. The 1000:1 penalty ratio makes this trade economically "worth it" to the solver for a very small amount of future curtailment avoidance (order of ~30,000 Wh of avoided future curtailment would already break even on this step's apparent $1,374 excess cost) — i.e., the mechanism is structurally capable of producing exactly this behavior even for modest future wind/solar forecasts, which somewhat strengthens H1 as plausible, but it is **not confirmed** because hours 1–23 of the step-0 horizon were never captured.
- **H2 — Formulation defect:** some other part of the 24-hour constraint set (not reviewed in exhaustive hour-by-hour detail for t=1..23, since the trace gives no visibility there) forces or strongly incentivizes this pattern regardless of the real forecast shape — e.g. an unintended interaction between the per-timestep charge/discharge exclusivity constraint (constraint 7), the battery transition chain (constraint 8), or the horizon weighting, that was not isolated in this pass.
- **H3 — Penalty miscalibration (a narrower case of "intentional but wrong"):** the 1000:1 curtailment-to-cycling ratio may simply be a configuration/tuning choice (`battery.yaml`'s `deg_penalty_per_wh=0.00005` vs. `optimizer.yaml`'s `renewable_curtailment_penalty=0.05`) that nobody validated against realistic degradation economics, making this kind of battery-laundering-of-curtailment the solver's *correct, intended* response to a poorly calibrated cost model rather than a code bug at all.

**Missing evidence needed to distinguish H1/H2/H3, not obtainable without rerunning the pipeline (out of scope for this pass):**
- The full 24-hour `forecast_bundle.wind_generation.point[1:24]` / `solar_generation.point[1:24]` / `demand.point[1:24]` arrays as seen by the step-0 `optimize()` call.
- The full 24-hour `DispatchPlan` (`wind_used[1:24]`, `renewable_curtailment[1:24]`, `battery_charge[1:24]`, `battery_soc[1:24]`) that the same step-0 solve produced, to see whether the plan actually charges the battery back up from otherwise-curtailed wind later in that same horizon (confirming H1) or continues to curtail heavily regardless (undermining H1, pointing toward H2/H3).
- `res.fun` (`objective_value`) decomposed by term, to see which cost components dominate the reported optimum.

None of this was obtained in this pass because doing so would require instrumenting and rerunning `run_pipeline` (even for a single step), which the directive's hard constraints prohibit ("Do not run another 168-hour pipeline... Do not run any script at all"). This is flagged as the single largest open evidence gap.

---

## 3. Smallest candidate remedies, expected effects, and regression risks

These are **candidates for future owner-authorized work**, not implemented or recommended as a specific choice here.

1. **Reward direct renewable usage explicitly** (e.g., a small negative coefficient on `p_sol_used`/`p_wind_used`, or equivalently restructure the curtailment penalty so that using-now is always weakly preferred to discharge-and-reuse-later at equal external conditions). *Expected effect:* removes the structural incentive described in Section 1 regardless of H1/H2/H3. *Regression risk:* could change dispatch in every scenario this optimizer is used in, including ones where the current behavior is in fact benign; needs re-validation against the existing MILP-path test suite and any scenario where `optimizer_type="milp"` is selected.
2. **Re-examine the `deg_penalty_per_wh` vs. `renewable_curtailment_penalty` ratio** (battery.yaml vs. optimizer.yaml) for physical realism, since a 1000:1 ratio may itself be the root cause (H3). *Expected effect:* could reduce or eliminate the incentive to discharge-to-avoid-curtailment-later without any code change, if recalibrated. *Regression risk:* low code risk (config-only), but changes dispatch economics project-wide; needs owner sign-off since these are declared `"PROTOTYPE_ASSUMPTION"` values that other analyses may already depend on.
3. **Add a per-step (not just whole-horizon) minimum-curtailment-first constraint or lexicographic preference** so hour-0's dispatch cannot curtail available renewables while using battery/diesel to cover otherwise-coverable demand, independent of future-horizon effects. *Expected effect:* directly prevents the observed step-0 pattern. *Regression risk:* could conflict with genuinely optimal multi-period shifting (if H1 is in fact correct for some scenarios), effectively overriding the solver's own optimality in a way that needs justification.
4. **Capture the full 24-hour horizon in the next diagnostic pass** (not a fix — an evidence-gathering prerequisite) before choosing among 1–3, so H1 vs H2 vs H3 can be distinguished with evidence rather than argued from cost arithmetic alone.

No remedy is implemented in this pass. Item 4 is the lowest-risk immediate next step and is explicitly **not executed here** because it would require a script run, which this pass's directive prohibits.

---

## 4. Can this be addressed within `LocalMILPEnergyOptimizer` alone, or does it need broader contract changes?

Based on the code read in this pass: **Remedies 1–3 above appear addressable entirely within `milp.py`** — they are objective-coefficient, constraint, or config changes local to this one optimizer implementation. They do not require touching `EnergyOptimizer`'s abstract interface (`system/optimization/interface/base.py`, `optimize(forecast_bundle, station_state, config) -> DispatchPlan`), `DispatchPlan`'s schema, `ForecastBundle`'s schema, or any `PROTECTED_FILES` entry (`router.py`, `ecd.py`, `option_d.py`, `gap19_highs_native.py`, `simulator.py`, `runner.py`) — none of those were found to define or constrain the objective/penalty structure that drives this behavior; they only consume the `DispatchPlan` this optimizer returns. This is consistent with the prior diagnostic report's framing (Section 2, last paragraph) that this is "a newly observed root-cause question into an unprotected, non-`PROTECTED_FILES` optimizer file."

One caveat: if Item 2's config recalibration were chosen, `battery.yaml`/`optimizer.yaml` are shared config files — changing them affects every optimizer/solver that reads them (confirmed `option_d.py` and `gap19_highs_native.py` likely read the same `battery.yaml` keys, though this pass did not re-verify those two files' config reads in detail, having focused scope on `milp.py` per the directive). A config-only remedy therefore has a wider blast radius than a `milp.py`-local code change even though it touches no `PROTECTED_FILES` source.

---

## 5. Precise owner approval required before implementation

Before any of Section 3's candidate remedies is implemented, the owner should explicitly approve:
1. **Confirmation of which hypothesis (H1/H2/H3) is the actual cause**, which requires authorizing a follow-up instrumented single/multi-step diagnostic run (capturing the full 24-hour horizon, per Section 2) — itself a small, bounded script run that would need its own explicit authorization, since this pass's directive prohibited any run.
2. **Which remedy** (objective reward term, penalty recalibration, explicit per-step preference constraint, or some combination) to implement, since they have different regression profiles and Section 3/4 shows this is a genuine design choice, not a single obvious bug fix.
3. **Scope of config changes**, if Item 2 (battery.yaml/optimizer.yaml recalibration) is chosen, given its cross-optimizer blast radius noted in Section 4.
4. **Explicit confirmation that `milp.py` is out of `PROTECTED_FILES` scope** (this pass confirmed this directly from `manifest.py`, Section 0) so that any future change to it is understood to not need the protected-file governance review process, but still needs ordinary code-review/testing sign-off and a re-run of the existing MILP-path tests plus the 168h endurance scenario to confirm no regression in `renewable_utilization_pct`, `system_reliability_pct`, and `total_diesel_fuel_liters` before being considered for merge.
5. Standard reconfirmation that **winner: null**, the campaign guard, deferred `DSL-01` `epsilon_tol`, frozen assets, and blind-data restrictions remain untouched by any such future work, per this register's standing governance.

---

## 6. Confirmation of read-only scope

This pass performed exactly the following read operations and no others:
- Read `RT01_168H_BOUNDED_DIAGNOSTIC_REPORT.md` in full.
- Read `research/rt01_diagnostics/rt01_168h_trace.json` (steps 0 and 1 records inspected in full; structure confirmed).
- Read `research/rt01_diagnostics/trace_168h_endurance_scenario.py` (capture logic, lines ~141–245) to confirm exactly which fields are and are not recorded.
- Read `system/orchestration/manifest.py` (`PROTECTED_FILES` constant, lines 10–17) to independently verify `milp.py`'s unprotected status.
- Read `system/optimization/implementations/milp.py` in full (417 lines).
- Read `system/config/battery.yaml` and `system/config/optimizer.yaml` in full to obtain the live (not just code-default) penalty values.
- Read `system/optimization/interface/base.py`'s `EnergyOptimizer` abstract interface.
- Listed `N6_REMEDIATION_REPORTS/` directory contents (no files opened for writing other than this report and its mirror).

**No pipeline, test, campaign, or any script was run or re-run in this pass.** No source, test, config, register, or existing report file was edited. No threshold, routing/ECD behavior, fuel policy, or `PROTECTED_FILES` entry was changed. `winner: null`, the campaign guard, deferred `DSL-01` `epsilon_tol`, frozen assets, and blind-data restrictions were not touched. Nothing was staged, committed, or pushed. **RT-01 remains OPEN**; this pass does not implement a fix, relax the 75% floor, or close RT-01. The only filesystem changes made by this pass are the creation of this report (`RT01_STEP0_MILP_DISPATCH_ROOT_CAUSE_REVIEW.md`) and its mirror in `N6_REMEDIATION_REPORTS/`.
