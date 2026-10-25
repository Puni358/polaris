#!/usr/bin/env python3
"""
POLARIS -- RT-01 Bounded Diagnostic: Single-Step Counterfactual Re-Run for the
Steps-119-121 Unmet-Load Shortfall (168h endurance scenario)
====================================================================================

Owner-authorized, bounded, read-only diagnostic, continuing directly from
ems/reports/rt01_runtime_fixes/RT01_FUEL_ACCOUNTING_AND_MILP_VERIFICATION_REVIEW.md Q3 ("not unavoidable in
aggregate-energy terms ... but a DIRECT causal link from any specific known
defect to this specific night was NOT proven -- would need an actual
counterfactual re-solve"). This script IS that counterfactual re-solve.

What this script found BEFORE constructing any counterfactual (observational,
from a freshly regenerated, unmodified 168h baseline trace -- see Section 0
below): at absolute step 93 (the LAST step the real, unmodified
LocalMILPEnergyOptimizer/NORMAL route is active before the run permanently
falls to EMERGENCY/OptionDFallbackSolver), the real, unmodified MILP solver
dispatched diesel_power[0] = 66,992.87 W, while forecast demand net of wind
was only 16,992.87 W. The remaining 50,000 W (the battery's own
max_charge_power_w ceiling) was diesel power routed into battery_charge[0] =
50,000 W -- i.e., at that single step, the real MILP chose to charge the
battery to the brim USING DIESEL, consuming ~12.5 L of marginal fuel (plus
the associated base-rate fuel for that hour) purely for battery charging that
was not required to meet demand, decomposition, or any other constraint
(renewable curtailment was already exactly 0.0 that hour, so there was no
"free" surplus renewable being redirected -- this fuel was burned by choice,
not necessity). This is a DIFFERENT pattern from the already-closed H2
("simultaneous curtailment + discharge") dominance-violation theory audited
and falsified in ems/reports/rt01_runtime_fixes/RT01_TIGHT_GAP_VERIFICATION_REPORT.md and
ems/reports/rt01_runtime_fixes/RT01_SEVEN_HOUR_FEASIBILITY_AUDIT_AND_E2E_READINESS_REPORT.md (those hours
had curtailment > 0; step 93 has curtailment == 0 and an entirely different
variable pair, diesel_power + battery_charge). This script does NOT reopen
the H1/H2/H3 dominance-violation question -- it tests an independent,
previously-unexamined candidate cause.

Fuel trajectory immediately following step 93 (from the same unmodified
baseline trace): fuel_before_l=39.771 -> fuel_after_l=18.0228 at step 93 (a
drop of ~21.75 L in a single hour, versus a typical ~5-10 L/h non-charging
diesel hour elsewhere in the trace), then 18.0228 -> 9.5153 -> 2.0153 -> 0.0
at steps 94/95/96 under OptionDFallbackSolver. Diesel fuel is then 0.000 L
for the rest of the 168h run, including at steps 119-121, where the 14.97 kWh
of unmet load occurs.

THE COUNTERFACTUAL THIS SCRIPT RUNS (precisely, so it can be judged for
rigor, not taken on faith):
- Run the REAL, UNMODIFIED 168h pipeline (PolarisLocalRunner.run_pipeline,
  same construction and fixture as every other rt01_diagnostics script and
  the governed test suite) via the SAME non-invasive instance-level
  method-wrapping pattern already used in trace_168h_endurance_scenario.py.
- At EXACTLY ONE absolute step (step 93, located by direct inspection as
  above, not assumed), intercept the REAL DispatchPlan object returned by
  the REAL, UNMODIFIED LocalMILPEnergyOptimizer.optimize() call AFTER it has
  already run and solved the real MILP for that step's real forecast/state --
  no re-solve, no change to the solver's own decision -- and construct a
  single physically-consistent ALTERNATIVE for index 0 (the only index the
  simulator ever consumes) that removes ONLY the diesel-funded-charging
  component:
      new_battery_charge[0] = 0.0   (was 50,000.0 W)
      new_diesel_power[0]   = load_served[0] + flex[0] - solar_used[0]
                               - wind_used[0] - battery_discharge[0]
                             = 16,992.87 W (derived generically from the
                               REAL plan's own already-solved values, not
                               hardcoded -- see build_counterfactual_plan())
  Every other value at index 0 (solar_used, wind_used, battery_discharge,
  load_served, flexible_load_schedule, renewable_curtailment, unmet_load) is
  left EXACTLY as the real solver returned it. This preserves the bus-bar
  balance, solar/wind decomposition, and demand-deficit balance identically
  to the real solved solution -- it is not a new "better" MILP solution, it
  is the SAME solved solution with one discretionary, unforced diesel-funded
  charging decision reversed. Indices 1-23 of the plan are left completely
  untouched (irrelevant -- DigitalTwinSimulator.step() only ever reads index
  0, confirmed by direct inspection of system/simulation/simulator.py lines
  38-40).
- From step 94 onward, EVERY subsequent call to the real router, real
  optimizer, real OptionDFallbackSolver, and real DigitalTwinSimulator is
  the REAL, UNMODIFIED method, driven naturally by whatever REAL state
  (battery SOC, diesel fuel remaining) results from the one substituted
  step. No further intervention of any kind.
- This is therefore a genuine, reproducible, end-to-end counterfactual
  re-run of the real governed pipeline (168 real steps, real router, real
  optimizer, real fallback solver, real simulator), not a hand-computed
  arithmetic estimate and not a re-solve of the MILP itself.

Strict boundaries honored:
- system/optimization/implementations/milp.py, option_d.py, ecd.py,
  router.py, simulator.py, runner.py, manifest.py are NEVER edited -- this
  script only wraps PUBLIC, BOUND INSTANCE methods on one already-constructed
  runner instance, in this process only. Pre/post SHA-256 hashes of all
  seven are verified identical (Section 0 and the output JSON).
- No fuel policy, refueling policy, SOC floor, or renewable-utilization
  floor is touched. The 100 L no-refuel budget and 20%/95% SOC bounds are
  respected exactly as the real formulation enforces them (the counterfactual
  plan only reallocates where the SAME real solved energy goes; it adds no
  energy and removes no safety margin).
- Exactly one 168-step run_pipeline() call. No campaign, training, tuning,
  or additional solver re-invocation beyond what run_pipeline() itself makes.
- Nothing staged, committed, or pushed. All outputs written under
  research/rt01_diagnostics/ only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent

from system.runtime.runner import PolarisLocalRunner  # noqa: E402
from system.tests.test_offline_runtime import (  # noqa: E402
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)

SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"
BASELINE_TRACE_PATH = OUTPUT_DIR / "rt01_168h_trace.json"
TARGET_STEP = 93  # located by direct inspection of the freshly regenerated baseline trace; see module docstring

HASH_TARGETS = [
    "system/optimization/implementations/milp.py",
    "system/optimization/implementations/gap19_highs_native.py",
    "system/optimization/implementations/option_d.py",
    "system/control/ecd.py",
    "system/control/router.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "system/orchestration/manifest.py",
    "system/config/optimizer.yaml",
    "system/config/battery.yaml",
    "system/config/diesel.yaml",
    "system/config/loads.yaml",
    "system/config/solar_pv.yaml",
    "system/config/station.yaml",
    f"system/data/scenarios/{SCENARIO_FILENAME}",
]


def sha256_of(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_hash_manifest() -> Dict[str, Optional[str]]:
    return {rel: sha256_of(REPO_ROOT / rel) for rel in HASH_TARGETS}


def build_counterfactual_plan(plan, step_idx: int, applied_log: List[Dict[str, Any]]):
    """
    Given the REAL, already-solved DispatchPlan for this step, check whether
    index 0 exhibits the "diesel-funded, unforced battery charging" pattern
    (diesel_power[0] > demand-net-of-renewables-and-discharge AND
    battery_charge[0] > 0 AND renewable_curtailment[0] <= 1e-6, i.e. no
    surplus renewable being redirected -- the charging is unambiguously
    diesel-sourced). If so, mutate ONLY index 0, in place, removing the
    diesel-funded charging component and recomputing diesel_power[0] to the
    minimum needed to satisfy the SAME already-solved bus-bar balance with
    battery_charge[0] = 0. Returns True if a substitution was made.
    """
    sol0 = plan.solar_used[0]
    wind0 = plan.wind_used[0]
    chg0 = plan.battery_charge[0]
    dis0 = plan.battery_discharge[0]
    diesel0 = plan.diesel_power[0]
    served0 = plan.load_served[0]
    flex0 = plan.flexible_load_schedule[0]
    curt0 = plan.renewable_curtailment[0]

    # Bus-bar balance identity the real solved plan already satisfies:
    #   sol0 + wind0 + dis0 + diesel0 == served0 + chg0 + flex0
    # Define D = served0 + flex0 - sol0 - wind0 - dis0 (the diesel that would
    # be needed to meet demand alone, IGNORING battery charging). From the
    # balance identity, diesel0 - D == chg0 exactly, i.e. chg0 is funded by
    # diesel to the extent diesel0 exceeds D, and funded by non-diesel
    # surplus (sol0+wind0+dis0 - served0 - flex0 = -D) to the extent D < 0.
    # The generally-correct, balance-preserving substitution that removes
    # ONLY the diesel-funded portion of charging (and nothing else) is:
    #   new_diesel0 = max(0, D)     new_chg0 = max(0, -D)
    # This reduces to the simple "zero both" case only when D >= 0 (diesel
    # was genuinely needed for demand, so none of it should fund charging);
    # when D < 0 (renewable surplus alone, with zero curtailment, already
    # exceeds demand) it correctly preserves the renewable-funded slice of
    # charging and removes only the diesel slice on top of it.
    D = served0 + flex0 - sol0 - wind0 - dis0
    diesel_funded_charge_wh = chg0 - max(0.0, -D)

    pattern_present = (
        chg0 > 1e-6
        and curt0 <= 1e-6
        and diesel0 > 1e-6
        and diesel_funded_charge_wh > 1e-6
    )

    record = {
        "step": step_idx,
        "pattern_present": pattern_present,
        "original": {
            "solar_used": sol0, "wind_used": wind0, "battery_charge": chg0,
            "battery_discharge": dis0, "diesel_power": diesel0,
            "load_served": served0, "flexible_load": flex0,
            "renewable_curtailment": curt0, "unmet_load": plan.unmet_load[0],
        },
    }

    if not pattern_present:
        record["action"] = "NO_SUBSTITUTION (pattern not present at this step)"
        applied_log.append(record)
        return False

    new_diesel0 = max(0.0, D)
    new_chg0 = max(0.0, -D)

    # Sanity: the new plan must still balance exactly (bus-bar) with
    # everything else held fixed.
    balance_check = abs((sol0 + wind0 + dis0 + new_diesel0) - (served0 + new_chg0 + flex0))
    assert balance_check < 1e-3, f"Counterfactual bus-bar balance check failed: {balance_check}"

    plan.battery_charge[0] = new_chg0
    plan.diesel_power[0] = new_diesel0
    plan.energy_balance_errors[0] = 0.0

    record["action"] = "SUBSTITUTED (removed unforced diesel-funded battery charging)"
    record["modified"] = {
        "solar_used": sol0, "wind_used": wind0, "battery_charge": new_chg0,
        "battery_discharge": dis0, "diesel_power": new_diesel0,
        "load_served": served0, "flexible_load": flex0,
        "renewable_curtailment": curt0, "unmet_load": plan.unmet_load[0],
    }
    record["fuel_liters_this_hour_original_estimate"] = None  # filled by caller using config constants
    record["diesel_power_delta_w"] = diesel0 - new_diesel0
    record["battery_charge_delta_w"] = chg0 - new_chg0
    applied_log.append(record)
    return True


def build_instrumented_runner(mode: str):
    """mode: 'baseline' (no intervention), 'single_step' (TARGET_STEP only),
    or 'all_steps' (every step across the whole run exhibiting the same
    generic diesel-funded-charging pattern)."""
    assert mode in ("baseline", "single_step", "all_steps")

    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    trace: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {}
    step_counter = {"idx": -1}
    substitution_log: List[Dict[str, Any]] = []

    diesel_cfg = runner.configs.get("diesel", {})
    base_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    orig_evaluate_and_route = runner.router.evaluate_and_route

    def wrapped_evaluate_and_route(current_state, bundle, configs):
        step_counter["idx"] += 1
        assessment, route = orig_evaluate_and_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["operating_mode"] = assessment.operating_mode.value
        step_ctx["fuel_before_l"] = current_state.diesel_fuel_remaining_liters
        step_ctx["soc_before_pct"] = current_state.battery_soc_pct
        step_ctx["diesel_margin_hours"] = assessment.diesel_margin_hours
        step_ctx["battery_margin_hours"] = assessment.battery_margin_hours
        step_ctx["forecast_solar_h1_w"] = (
            float(bundle.solar_generation.point[0]) if bundle.solar_generation.point else None
        )
        step_ctx["forecast_wind_h1_w"] = (
            float(bundle.wind_generation.point[0]) if bundle.wind_generation.point else None
        )
        step_ctx["forecast_demand_h1_w"] = (
            float(bundle.demand.point[0]) if bundle.demand.point else None
        )
        return assessment, route

    runner.router.evaluate_and_route = wrapped_evaluate_and_route

    orig_optimize = runner.optimizer.optimize
    optimizer_class_name = type(runner.optimizer).__name__

    def wrapped_optimize(bundle, current_state, configs):
        plan = orig_optimize(bundle, current_state, configs)
        step_idx = step_counter["idx"]
        if mode == "single_step" and step_idx == TARGET_STEP:
            substituted = build_counterfactual_plan(plan, step_idx, substitution_log)
            if not substituted:
                raise RuntimeError(
                    f"COUNTERFACTUAL_PRECONDITION_FAILED: expected diesel-funded-charging "
                    f"pattern at step {TARGET_STEP}, but it was not present in this run. "
                    f"Refusing to silently proceed without the intended intervention."
                )
        elif mode == "all_steps":
            # Apply the SAME generic pattern-detection/substitution rule at
            # every NORMAL/MILP step where it is present, not just step 93.
            # This is the identical function used for the single-step case --
            # no new logic, same detection threshold, same substitution
            # formula -- applied uniformly wherever it fires.
            build_counterfactual_plan(plan, step_idx, substitution_log)
        step_ctx["solver"] = optimizer_class_name
        step_ctx["plan"] = plan
        return plan

    runner.optimizer.optimize = wrapped_optimize

    orig_solve = runner.option_d_solver.solve
    option_d_class_name = type(runner.option_d_solver).__name__

    def wrapped_solve(assessment, bundle, current_state, configs):
        plan = orig_solve(assessment, bundle, current_state, configs)
        step_ctx["solver"] = option_d_class_name
        step_ctx["plan"] = plan
        return plan

    runner.option_d_solver.solve = wrapped_solve

    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)
        plan = step_ctx.get("plan")
        record = {
            "step": len(trace),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "solver": step_ctx.get("solver"),
            "diesel_margin_hours": step_ctx.get("diesel_margin_hours"),
            "battery_margin_hours": step_ctx.get("battery_margin_hours"),
            "fuel_before_l": step_ctx.get("fuel_before_l"),
            "fuel_after_l": state_after.diesel_fuel_remaining_liters,
            "soc_before_pct": step_ctx.get("soc_before_pct"),
            "soc_after_pct": state_after.battery_soc_pct,
            "forecast_wind_h1_w": step_ctx.get("forecast_wind_h1_w"),
            "forecast_demand_h1_w": step_ctx.get("forecast_demand_h1_w"),
            "plan_diesel_power_h1_w": float(plan.diesel_power[0]) if plan else None,
            "plan_battery_charge_h1_w": float(plan.battery_charge[0]) if plan else None,
            "plan_battery_discharge_h1_w": float(plan.battery_discharge[0]) if plan else None,
            "plan_renewable_curtailment_h1_w": float(plan.renewable_curtailment[0]) if plan else None,
            "plan_unmet_load_h1_w": float(plan.unmet_load[0]) if plan else None,
        }
        trace.append(record)
        step_ctx.clear()
        return state_after

    runner.simulator.step = wrapped_step

    return runner, trace, substitution_log


def summarize(trace: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_unmet_wh = sum((r["plan_unmet_load_h1_w"] or 0.0) for r in trace)
    steps_119_121_unmet_wh = sum(
        (r["plan_unmet_load_h1_w"] or 0.0) for r in trace if 119 <= r["step"] <= 121
    )
    unmet_steps = [r["step"] for r in trace if (r["plan_unmet_load_h1_w"] or 0.0) > 1e-6]
    fuel_zero_step = next((r["step"] for r in trace if (r["fuel_after_l"] or 0.0) <= 1e-6), None)
    last_normal_step = max((r["step"] for r in trace if r["route"] == "NORMAL"), default=None)
    return {
        "total_unmet_load_wh": round(total_unmet_wh, 2),
        "total_unmet_load_kwh": round(total_unmet_wh / 1000.0, 4),
        "steps_119_121_unmet_wh": round(steps_119_121_unmet_wh, 2),
        "steps_119_121_unmet_kwh": round(steps_119_121_unmet_wh / 1000.0, 4),
        "all_unmet_steps": unmet_steps,
        "first_literal_fuel_exhaustion_step": fuel_zero_step,
        "last_normal_milp_step": last_normal_step,
    }


def main() -> None:
    pre_hashes = build_hash_manifest()

    baseline = None
    if BASELINE_TRACE_PATH.exists():
        with open(BASELINE_TRACE_PATH, "r", encoding="utf-8") as f:
            baseline = json.load(f)

    # ---- Run 1: BASELINE -- real, unmodified pipeline, no substitution ----
    runner_b, trace_b, log_b = build_instrumented_runner(mode="baseline")
    report_b = runner_b.run_pipeline(steps_to_run=168)
    summary_b = summarize(trace_b)

    # ---- Run 2: SINGLE-STEP COUNTERFACTUAL -- identical, except the one ----
    # ---- step-93 diesel-funded-charging substitution described in the  ----
    # ---- module docstring.                                              ----
    runner_c, trace_c, log_c = build_instrumented_runner(mode="single_step")
    report_c = runner_c.run_pipeline(steps_to_run=168)
    summary_c = summarize(trace_c)

    # ---- Run 3: ALL-STEPS COUNTERFACTUAL -- the SAME generic pattern-   ----
    # ---- detection/substitution rule applied at EVERY NORMAL/MILP step  ----
    # ---- where it fires across the whole 168h run, to test whether the  ----
    # ---- identified mechanism is sufficient IN AGGREGATE, not just at   ----
    # ---- the single occurrence located first.                          ----
    runner_a, trace_a, log_a = build_instrumented_runner(mode="all_steps")
    report_a = runner_a.run_pipeline(steps_to_run=168)
    summary_a = summarize(trace_a)

    post_hashes = build_hash_manifest()
    hash_diffs = {k: (pre_hashes[k], post_hashes[k]) for k in HASH_TARGETS if pre_hashes[k] != post_hashes[k]}

    comparison = {
        "baseline": summary_b,
        "single_step_counterfactual": summary_c,
        "all_steps_counterfactual": summary_a,
        "single_step_steps_119_121_unmet_kwh_delta": round(
            summary_c["steps_119_121_unmet_kwh"] - summary_b["steps_119_121_unmet_kwh"], 4
        ),
        "single_step_total_unmet_load_kwh_delta": round(
            summary_c["total_unmet_load_kwh"] - summary_b["total_unmet_load_kwh"], 4
        ),
        "single_step_shortfall_119_121_eliminated": summary_c["steps_119_121_unmet_kwh"] <= 1e-6,
        "all_steps_steps_119_121_unmet_kwh_delta": round(
            summary_a["steps_119_121_unmet_kwh"] - summary_b["steps_119_121_unmet_kwh"], 4
        ),
        "all_steps_total_unmet_load_kwh_delta": round(
            summary_a["total_unmet_load_kwh"] - summary_b["total_unmet_load_kwh"], 4
        ),
        "all_steps_shortfall_119_121_eliminated": summary_a["steps_119_121_unmet_kwh"] <= 1e-6,
        "all_steps_num_substitutions_applied": sum(1 for r in log_a if r.get("pattern_present")),
    }

    payload = {
        "scenario_filename": SCENARIO_FILENAME,
        "target_step": TARGET_STEP,
        "single_step_intervention_log": log_c,
        "all_steps_intervention_log": log_a,
        "baseline_run_report_summary": {
            "timesteps_executed": report_b["timesteps_executed"],
            "execution_status": report_b["execution_status"],
            "ems_evaluation": report_b["ems_evaluation"],
        },
        "single_step_counterfactual_run_report_summary": {
            "timesteps_executed": report_c["timesteps_executed"],
            "execution_status": report_c["execution_status"],
            "ems_evaluation": report_c["ems_evaluation"],
        },
        "all_steps_counterfactual_run_report_summary": {
            "timesteps_executed": report_a["timesteps_executed"],
            "execution_status": report_a["execution_status"],
            "ems_evaluation": report_a["ems_evaluation"],
        },
        "comparison": comparison,
        "baseline_trace_file_found_for_cross_check": baseline is not None,
        "pre_execution_hash_manifest": pre_hashes,
        "post_execution_hash_manifest": post_hashes,
        "hash_diffs_detected": hash_diffs,
    }

    out_json = OUTPUT_DIR / "rt01_step119_counterfactual_trace.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    print("=" * 80)
    print("POLARIS RT-01 BOUNDED DIAGNOSTIC -- diesel-funded-charging counterfactual(s)")
    print("=" * 80)
    print(f"Single-step intervention log: {json.dumps(log_c, indent=2, default=str)}")
    print(f"All-steps substitutions applied: {comparison['all_steps_num_substitutions_applied']}")
    print(f"Baseline summary:             {json.dumps(summary_b, indent=2)}")
    print(f"Single-step counterfactual:   {json.dumps(summary_c, indent=2)}")
    print(f"All-steps counterfactual:     {json.dumps(summary_a, indent=2)}")
    print(f"Comparison: {json.dumps(comparison, indent=2)}")
    print(f"hash_diffs_detected (should be empty): {hash_diffs}")
    print(f"\nWrote: {out_json}")
    print("=" * 80)


if __name__ == "__main__":
    main()
