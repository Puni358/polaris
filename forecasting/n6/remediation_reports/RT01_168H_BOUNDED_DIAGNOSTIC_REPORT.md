# POLARIS — RT-01 Bounded Diagnostic: Routing, Fuel and Renewable Curtailment (168h Per-Step Trace)

**Date:** 2026-10-18
**Nature of this document:** Twenty-second pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `RT01_RENEWABLE_UTILIZATION_ROOT_CAUSE_REVIEW.md` (twenty-first pass). Mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Scope confirmation up front:** This is a **pure, bounded, read-only, one-time diagnostic pass**, per the owner's explicit "RT-01 Bounded Diagnostic" directive. The existing 168-hour synthetic endurance scenario was run **exactly once**, using the existing, unmodified `_authorize_router_for_offline_runtime_test` fixture and unmodified `synthetic_168h_endurance_scenario.json`. No production code, test, config, register, or `PROTECTED_FILES` entry was edited. No fuel capacity, refueling, ECD/router behavior, or renewable-to-battery charging logic was changed or implemented — this pass only **measures**. No campaign, diesel comparison, full suite, training/tuning, or sealed/blind data was run or accessed. Nothing staged, committed, or pushed. `RT-01` remains **OPEN**; no implementation is authorized by this pass.

---

## 1. Exact command used and artifacts created

**New, standalone diagnostic script** (not a production/test file): `research/rt01_diagnostics/trace_168h_endurance_scenario.py`

**Command run exactly once:**
```
python3 -I research/rt01_diagnostics/trace_168h_endurance_scenario.py
```
(`-I` isolates the interpreter from stray local/CWD modules; it has no effect on scenario/config behavior.)

**What the script does, precisely:** it imports the real, unmodified `PolarisLocalRunner` and the real, unmodified `_authorize_router_for_offline_runtime_test` fixture function directly from `system/tests/test_offline_runtime.py`, builds the runner with the identical call the existing tests use —
```python
runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
_authorize_router_for_offline_runtime_test(runner)
report = runner.run_pipeline(steps_to_run=168)
```
— and calls `run_pipeline(steps_to_run=168)` **exactly once**. To capture per-step telemetry, it monkey-patches four already-constructed **instance** methods (`runner.router.evaluate_and_route`, `runner.optimizer.optimize`, `runner.option_d_solver.solve`, `runner.simulator.step`) with thin wrappers that call the original, unmodified method, record its inputs/outputs, and return the original result completely unchanged. This is in-memory attribute shadowing in this script's own process; no `PROTECTED_FILES` entry is opened for writing, and none is edited (Section 6 confirms byte-identical hashes before/after). This is the same non-invasive external-harness pattern already used by `system/scripts/run_synthetic_critical_load_scenario.py`.

**Artifacts created (all new, in the new isolated diagnostic directory, alongside the script):**
- `research/rt01_diagnostics/rt01_168h_trace.json` — full per-step trace (168 records) + the run's `ems_evaluation` summary, for machine re-analysis.
- `research/rt01_diagnostics/rt01_168h_trace.csv` — same 168 records, flat CSV for spreadsheet inspection.
- `research/rt01_diagnostics/trace_168h_endurance_scenario.py` — the diagnostic script itself.

**Side effects from the one authorized `run_pipeline` call** (same disclosed class of side effect every prior RT-01 pass that ran this harness has reported): `system/artifacts/latest_dispatch_plan.json`, `system/artifacts/latest_forecast_bundle.json`, `system/artifacts/run_report.json` were regenerated (not tracked/protected source). No other file under `system/` was touched (confirmed by `find system -newermt ... | grep -v __pycache__` returning nothing outside `system/artifacts/`).

**Internal validation of the trace's correctness:** the script's own recomputed `renewable_utilization_pct` from its captured per-step records (`69.372%`) and the real `EvaluationEngine.evaluate_ems_performance` output in the same run (`69.37%`) agree to rounding, and `system_reliability_pct` (`90.04%`) and `total_diesel_fuel_liters` (`116.2`) both exactly match the byte-identical values recorded by every prior RT-01 pass back to the nineteenth pass. This confirms the diagnostic is observing the real, unmodified pipeline, not a divergent reimplementation.

---

## 2. Step-trace findings: EMERGENCY timing and solver split

**Required measurement 1 — first EMERGENCY timestep, fuel at transition, literal fuel exhaustion, solver split:**

| Finding | Value |
|---|---|
| First EMERGENCY step | **step 1** (the second executed hour) |
| Fuel remaining at the step-1 EMERGENCY transition | **100.0 L (full tank — unchanged from the 100 L default)** |
| Trigger at step 1 | `battery_margin_hours = -0.4506` (negative); `diesel_margin_hours = +10.0` (still comfortably positive) |
| Literal fuel-exhaustion step (`diesel_fuel_remaining_liters` first reaches exactly 0.0) | **step 44** (fuel_before=7.0384 L → fuel_after=0.0 L), matching every prior pass's "~step 44" figure |
| Route counts (168 steps) | `NORMAL: 1`, `EMERGENCY: 167` |
| Solver counts | `LocalMILPEnergyOptimizer: 1` (step 0 only), `OptionDFallbackSolver: 167` (steps 1–167) |

**The ≈37.5 L diesel-margin-trigger hypothesis from the twenty-first-pass root-cause review is REFUTED as the actual trigger, though its arithmetic is independently confirmed as correct for a different, later, non-binding event:**

- The hypothesis predicted EMERGENCY would begin once actual remaining fuel first drops below ≈37.5 L (`available_fuel_l / 6.25 < 6.0h`), "within the first several hours." The trace shows fuel never approaches that threshold before EMERGENCY begins — fuel is still **exactly 100.0 L (completely full)** at the moment EMERGENCY first triggers, at step 1.
- The diesel-margin crossover the hypothesis described **does occur**, but **41 steps later and with no causal effect**: `diesel_margin_hours` is `+0.021` at step 41 (fuel_before = 37.6299 L) and `-1.179` at step 42 (fuel_before = 30.1299 L) — i.e. the predicted ≈37.5 L crossover is numerically accurate to within ~0.1 L. But by step 42 the system has already been continuously in `EMERGENCY`/`OptionDFallbackSolver` for 41 consecutive hours, so this crossover changes nothing operationally; it is a secondary, non-binding confirmation of the formula, not the trigger.
- **The actual, binding trigger is the BATTERY survivability margin, not the diesel/fuel margin**, and it fires almost immediately:
  - At step 0 (the single `NORMAL` step), the router's own ECD assessment — evaluated against the *pre-dispatch* state (SOC 50.0%) — correctly shows `battery_margin_hours = +5.04` (`NORMAL`). `LocalMILPEnergyOptimizer` is invoked for this one step.
  - **That one MILP step's own chosen dispatch (not the ECD assessment) is what breaks the margin**: with `forecast_demand_h1_w = 27,448.19 W` and `forecast_wind_h1_w = 33,100.04 W` (wind alone exceeds demand by ~5.65 kW, solar forecast = 0.0), the MILP's step-0 plan sets `diesel_power=0`, `solar_used=0`, `wind_used=0`, **curtails the entire 33,100.04 W of forecast-available wind**, and serves 100% of load (`27,448.19 W`) from **battery discharge alone**. This single step drains battery SOC from 50.0% to 35.08% in one hour.
  - That SOC drop is exactly what the router's step-1 ECD evaluation then sees: `usable_ac_energy_wh` at SOC 35.08% gives `t_battery = 5.5494h`, `battery_margin_hours = 5.5494 - 6.0 = -0.4506h` → `EMERGENCY`.
  - **This is a directly observed, quantified fact of this run, not a guess**: the rapid EMERGENCY lock-in is proximately caused by the single `NORMAL`/MILP step itself fully curtailing available wind and discharging the battery instead, not by any diesel-fuel depletion. *Why* `LocalMILPEnergyOptimizer` chose 100% wind curtailment + battery-only service in that one step (its internal objective weighting) was not investigated — that would be a new root-cause question into an unprotected, non-`PROTECTED_FILES` optimizer file, outside this diagnostic's bounded measurement scope. It is flagged here as a newly observed, unresolved factual open item, not root-caused or implemented.
- Once `EMERGENCY` begins at step 1, it **never returns to `NORMAL`** for the remaining 166 steps. `OptionDFallbackSolver` (Section 2b of the root-cause review: structurally unable to charge the battery from surplus renewables) is therefore the active dispatcher for **167 of 168 steps (99.4%)** — an even larger and earlier-starting share than the root-cause review's code-traced-but-unconfirmed "nearly the entire run" estimate, and it begins at **hour 1**, not "within the first several hours."
- **Correction to solver identity**: the 168h tests use `optimizer_type="milp"`, which `PolarisLocalRunner` maps to `LocalMILPEnergyOptimizer` (`system/optimization/implementations/milp.py`, **not** `PROTECTED_FILES`), not `GAP19HighsNativeOptimizer` (which is only instantiated for `optimizer_type in ("highs_native", "gap19_highs_native")`). The root-cause review's structural comparison was between `OptionDFallbackSolver` and `GAP19HighsNativeOptimizer`; this trace shows the actual `NORMAL`-route solver this exact test invokes is `LocalMILPEnergyOptimizer`, a separate, independent HiGHS-based MILP formulation with an analogous same-side bus-bar balance (`p_sol_u + p_w_u + p_dis + p_dies - p_serv - p_chg - p_flx = 0`) that is likewise structurally capable of charging from surplus renewables — so the prior passes' structural point about `OptionDFallbackSolver` vs. a renewable-charging-capable MILP-class solver still holds, but the specific class name used in this exact scenario is `LocalMILPEnergyOptimizer`, not `GAP19HighsNativeOptimizer`.

---

## 3. Quantified curtailed and charging-eligible renewable energy

All figures below are summed over the 168 physically-executed H1 (first-action) steps, using each step's own `DispatchPlan.solar_used[0]` / `wind_used[0]` / `renewable_curtailment[0]` — the identical fields and identical H1-only basis `EvaluationEngine.evaluate_ems_performance` itself sums (confirmed in Section 1: the script's independent recomputation of `renewable_utilization_pct` from these same fields reproduces `69.37%` exactly).

| Quantity | Value |
|---|---|
| Total renewable energy **used** (H1, all 168 steps) | 4,756,665.16 Wh |
| Total renewable energy **curtailed** (H1, all 168 steps) | **2,100,084.63 Wh** |
| Total renewable energy **available** (used + curtailed) | 6,856,749.79 Wh |
| Recomputed `renewable_utilization_pct` | 69.372% (matches evaluator's 69.37%) |
| Curtailment attributable to the single `NORMAL`/MILP step (step 0) | 33,100.04 Wh |
| Curtailment attributable to `EMERGENCY`/`OptionDFallbackSolver` steps (1–167) | 2,066,984.59 Wh (98.4% of all curtailment) |

**Charging-eligibility upper bound (Required measurement 2):** for every step, this diagnostic computed `eligible_for_charging_w = min(curtailment_w, max_charge_power_w, battery_headroom_dc_wh / charge_efficiency)`, using `battery.yaml`'s own already-configured `max_charge_power_w=50,000 W`, `max_soc_pct=95.0%`, `capacity_wh=200,000 Wh`, `charge_efficiency=0.92`, and the **actually-observed** (unmodified) `battery_energy_wh` at the start of each step — i.e. a static, step-wise snapshot test against the real, already-executed trajectory, not a re-simulation.

**Result: 0 of 168 steps had curtailment exceeding either the 50 kW charge-power cap or the available SOC headroom.** Maximum single-step curtailment observed was 33,829.83 W (well under the 50 kW cap); minimum available charge headroom at any step was the full 50,000 W (SOC never rose anywhere near the 95% ceiling in this run — the dominant dynamic is heavy battery *discharge*, not charge, under `OptionDFallbackSolver`). Consequently:

**Total eligible-for-charging upper bound = 2,100,084.63 Wh — numerically equal to 100% of the measured curtailment.**

---

## 4. Why eligible energy is not necessarily equal to recoverable energy or a guaranteed utilization improvement (Required measurement 3)

The 100%-eligible result above is a genuine, quantified finding for *this specific, already-executed, unmodified trajectory* — it is not an artifact of a trivial or vacuous calculation (curtailment per step was check against real, non-infinite 50 kW/headroom limits that were in fact binding candidates, they simply never bound in this run). But it is an **upper bound against a frozen counterfactual**, not a demonstrated recoverable amount or a guaranteed metric improvement, for four distinct, concrete reasons:

1. **Trajectory feedback is not modeled.** The eligibility test used the battery-energy trajectory *as it actually occurred* under the current (no-renewable-charging) dispatch. If `OptionDFallbackSolver` actually charged from this curtailment at each step, SOC would be higher at every subsequent step than what was observed — which changes `battery_margin_hours` at every later step (Section 2's own finding shows this margin is the single most consequential, binding quantity in this entire run, since it is what triggers and sustains `EMERGENCY` in the first place). A higher, earlier-rising SOC trajectory could plausibly *shorten* the `EMERGENCY` window (by restoring a positive battery margin sooner), which would itself change which solver runs and therefore change the entire downstream dispatch, curtailment, and eligibility pattern in ways this static, single-pass measurement cannot capture. The true recoverable amount under an actually-implemented fix could therefore be smaller, larger, or distributed completely differently across the 168 hours than this snapshot measurement.
2. **The 50 kW power cap and SOC headroom were never binding in this run**, which also means this specific measurement provides no information about whether they *would* bind under a different (post-fix) trajectory with a different, likely higher, SOC path — only that they did not bind on the as-observed path.
3. **This is forecast-based accounting, not literal physical generation.** Consistent with Section 1 of the twenty-first-pass root-cause review, `solar_used`/`wind_used`/`renewable_curtailment` are each solver's own accounting against its *forecast* input (`bundle.solar_generation.point[0]`, `bundle.wind_generation.point[0]`), not an independently verified, ground-truth-reconciled generation figure. Forecast error is a separate, unquantified source of divergence between "eligible on paper" and "physically recoverable," not addressed by this pass.
4. **Implementing the charging path is itself a `PROTECTED_FILES` change requiring its own correctness review** (conservation, no double-counting, SOC-bounds, interaction with the E3 preserved/limiting-resource branches) per this register's own existing governance standard for any `option_d.py` edit — this pass performs no such review and authorizes no such change.

---

## 5. Does the evidence say anything about the 75% floor's achievability? (Required measurement 4)

**No claim of achievability or impossibility is made.** The evidence narrows, but does not resolve, the question:

- Reaching `renewable_utilization_pct >= 75.0%` from the measured `69.37%` baseline requires recovering **385,897.18 Wh** of currently-curtailed energy into "used" status (since the metric's denominator — total available renewables — is fixed; reclassifying curtailed Wh as used directly raises the ratio). That is **18.38% of the 2,100,084.63 Wh measured curtailment pool** — i.e. the pool this run's curtailment comprises is, on paper, roughly 5.4× larger than the minimum recovery needed to cross the floor.
- Section 3/4's measurement shows that **none of that measured curtailment pool was blocked by the 50 kW charge-power cap or by SOC headroom in the trajectory as it actually occurred** — so, for this specific scenario and the trajectory it actually produced, the charge-power and SOC-headroom hardware limits are **not** an a-priori reason the needed recovery is unreachable.
- This is evidence that the 75% floor is **not mathematically foreclosed by the measured curtailment pool's size or by the hardware limits tested**, which is a real, bounded narrowing of the open question the twenty-first-pass review left (Section 4 of that review: "is ≥75% achievable at all for this scenario's resource mix?").
- It is **not** evidence that 75% is achievable: Section 4's four caveats (trajectory feedback not modeled, headroom/power-cap non-bindingness untested under a different trajectory, forecast-vs-actual accounting, no implementation/correctness review performed) all apply directly here. A genuine achievability determination requires implementing the charging path (or an equivalent fix) under full protected-file governance review and re-running the scenario — neither of which this bounded diagnostic pass performs or authorizes.
- Separately, Section 2's new finding (the step-0 MILP decision to curtail 100% of available wind in favor of battery-only service, which proximately triggers the near-immediate and essentially permanent `EMERGENCY` lock-in) is itself a candidate contributor to the shortfall that is **distinct from, and prior to, Option D's structural inability to charge** — and was not previously known. Any future engineering work toward the 75% floor should account for both mechanisms, not only the one already identified in the twenty-first pass.

---

## 6. Test/runtime outcome and protected-file hash integrity

**Runtime outcome of the one authorized `run_pipeline(steps_to_run=168)` call:** `timesteps_executed=168`, `execution_status="SUCCESS_CLEAN"` — no fault events, no solver failures, no early termination. `ems_evaluation.renewable_utilization_pct=69.37`, `ems_evaluation.system_reliability_pct=90.04`, `ems_evaluation.total_diesel_fuel_liters=116.2` — all byte-identical to the values every prior RT-01 pass (nineteenth through twenty-first) has recorded for this exact unmodified scenario/fixture combination. **No pytest was invoked by this pass** (the directive authorized exactly one diagnostic run of the scenario, not a test-suite re-run); the existing tests' own pass/fail status is unaffected and unchanged by this pass.

**All 7 `PROTECTED_FILES` entries, re-hashed read-only before and after this pass's one diagnostic run:**

| File | SHA-256 | Before | After |
|---|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | match | match |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | match | match |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | match | match |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | match | match |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | match | match |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | match | match |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | match | match |

All 7 values are byte-identical before and after, and exactly match the v1.9.10-recorded baseline. **Zero mismatches. None of these 7 files was opened for writing or edited by this pass.**

**Other preserved boundaries (read-only, re-confirmed):**
- `winner: null` (`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/N6_OPERATIONAL_READINESS_REPORT.json`) — confirmed present/unchanged.
- The campaign-execution guard (`CampaignExecutionNotAuthorizedError` in `system/evaluation/replay_harness.py`) — confirmed present, unconditional, not invoked.
- `DSL-01`'s `epsilon_tol` — confirmed still deferred/unset in the register.
- `system/config/diesel.yaml` — confirmed unchanged, still carries no `initial_fuel_l` key (100 L default from `simulator.py`/`option_d.py`/`router.py` code, unchanged).
- No sealed 2025 blind data, no frozen Stage 8.1/N6 asset, was accessed or changed.
- Nothing was staged, committed, or pushed.

---

## 7. RT-01 status

**RT-01 remains OPEN.** This pass does not close it, does not claim `renewable_utilization_pct >= 75.0%` is satisfied or foreclosed, and authorizes no implementation. It delivers the twenty-first pass's one explicitly flagged open factual question — resolved, but with the opposite answer to the twenty-first pass's own stated hypothesis: `EMERGENCY` begins at **step 1**, triggered by the **battery** survivability margin (itself driven by a single, newly-observed, unexplained MILP step-0 decision to fully curtail available wind in favor of battery-only service), not by the diesel-fuel margin crossing ≈37.5 L (which does occur, correctly, but 41 steps later and with no causal effect, since `EMERGENCY` was already locked in). It additionally quantifies, for the first time, that 100% of this run's 2.1 MWh of curtailed renewable energy is — on a static, step-wise, hardware-limit basis against the trajectory as it actually occurred — within the battery's charge-power and SOC-headroom limits, while explaining in Section 4 why that figure is an upper bound, not a demonstrated recoverable or guaranteed-improvement quantity. Neither the renewable-utilization floor's achievability nor the newly observed step-0 MILP curtailment decision is resolved or root-caused by this pass; both are left for separate, explicitly authorized owner decisions and engineering work.
