#!/usr/bin/env python3
"""
POLARIS -- RT-01 Bounded Diagnostic: Per-Step Trace of the 168h Endurance Scenario
====================================================================================

Owner-authorized, bounded, ONE-TIME, read-only diagnostic (directive dated
2026-10-18, continuing directly from RT01_RENEWABLE_UTILIZATION_ROOT_CAUSE_
REVIEW.md). Purpose: resolve the one open factual question that review could
not close without a re-run -- the actual per-step timing of the EMERGENCY
transition relative to literal diesel-fuel exhaustion -- and quantify the
renewable-curtailment / battery-charging-eligibility opportunity, WITHOUT
implementing any fix.

What this script is, precisely:
- A NEW, standalone, external harness (same pattern as
  system/scripts/run_synthetic_critical_load_scenario.py, which this repo's
  own prior passes already established as non-invasive). It IMPORTS the
  real, unmodified PROTECTED_FILES classes (EMSControlRouter,
  OptionDFallbackSolver, DigitalTwinSimulator via PolarisLocalRunner) and
  the real, unmodified, already-authorized test fixture function
  `_authorize_router_for_offline_runtime_test` from
  system/tests/test_offline_runtime.py.
- It runs the EXACT SAME call the existing 168h tests make:
      runner = PolarisLocalRunner(SYSTEM_DIR,
                                   scenario_filename="synthetic_168h_endurance_scenario.json",
                                   optimizer_type="milp")
      _authorize_router_for_offline_runtime_test(runner)
      report = runner.run_pipeline(steps_to_run=168)
  -- called exactly ONCE in this script, with no config/fixture/scenario
  changes of any kind.
- To capture per-step telemetry, this script monkey-patches four BOUND
  INSTANCE methods on the already-constructed runner's component objects
  (runner.router.evaluate_and_route, runner.optimizer.optimize,
  runner.option_d_solver.solve, runner.simulator.step) with thin wrappers
  that call the ORIGINAL, UNMODIFIED method, record its inputs/outputs into
  a local Python list, and return the original method's result completely
  unchanged. This is instance-level attribute shadowing in this script's own
  Python process; it does NOT edit, patch, or write to any file on disk --
  router.py, ecd.py, option_d.py, gap19_highs_native.py, simulator.py,
  runner.py, and manifest.py are never opened for writing by this script,
  and their on-disk SHA-256 hashes are verified unchanged before and after
  (see verify_protected_hashes.py in this same directory / the report).
- NOTE ON SOLVER IDENTITY: the 168h tests use optimizer_type="milp", which
  PolarisLocalRunner (system/runtime/runner.py lines ~78-86) maps to
  `LocalMILPEnergyOptimizer` (system/optimization/implementations/milp.py)
  for the NORMAL route -- NOT `GAP19HighsNativeOptimizer`
  (gap19_highs_native.py), which is only instantiated when
  optimizer_type is "highs_native"/"gap19_highs_native". LocalMILPEnergyOptimizer
  is a separate, unprotected, independent HiGHS-based MILP formulation with
  its own same-side bus-bar balance (p_sol_u + p_w_u + p_dis + p_dies -
  p_serv - p_chg - p_flx = 0; see milp.py lines ~384), structurally the same
  renewable-to-battery-charging capability GAP19 has (and OptionDFallbackSolver
  structurally lacks) -- but this script reports the ACTUAL class invoked by
  this exact test, not the one discussed by name in earlier passes, because
  that earlier discussion assumed an optimizer_type this test does not use.
  This is reported as a factual clarification, not a contradiction of the
  prior passes' structural finding about OptionDFallbackSolver.

Strict boundaries honored (see ems/reports/rt01_runtime_fixes/RT01_168H_BOUNDED_DIAGNOSTIC_REPORT.md):
- Exactly one run of run_pipeline(steps_to_run=168) on the unmodified
  synthetic_168h_endurance_scenario.json, with the unmodified
  _authorize_router_for_offline_runtime_test fixture.
- No production code, test, config, register, or protected file is edited.
- No fuel capacity change, no refueling, no ECD/router behavior change, no
  renewable-to-battery charging implementation. The "eligible for charging"
  figure below is a pure post-hoc arithmetic upper bound computed from the
  ALREADY-OBSERVED (unmodified) battery trajectory -- it does not simulate,
  assume, or claim what would happen if charging were actually implemented
  (seeSection on why eligible != recoverable in the output report).
- No campaign, no diesel comparison, no full suite, no training/tuning, no
  sealed/blind data.
- Nothing staged, committed, or pushed by this script.
"""
from __future__ import annotations

import csv
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


def build_instrumented_runner() -> "tuple[PolarisLocalRunner, List[Dict[str, Any]]]":
    """Builds the runner EXACTLY as the existing 168h tests do, then attaches
    non-invasive, instance-level telemetry wrappers. Returns (runner, trace)
    where `trace` is populated in place as run_pipeline executes."""

    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename="synthetic_168h_endurance_scenario.json",
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    trace: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {}

    # --- Battery / diesel config constants, read (not invented) from the
    # same runner.configs dict the real solvers/simulator themselves read,
    # used only to compute the post-hoc "eligible for charging" upper bound.
    bat_cfg = runner.configs.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    max_chg_w = float(bat_cfg.get("max_charge_power_w", 50000.0))
    eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)

    diesel_cfg = runner.configs.get("diesel", {})
    base_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    # --- 1. Router wrapper: capture pre-step state + assessment + route ---
    orig_evaluate_and_route = runner.router.evaluate_and_route

    def wrapped_evaluate_and_route(current_state, bundle, configs):
        assessment, route = orig_evaluate_and_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["operating_mode"] = assessment.operating_mode.value
        step_ctx["validity_status"] = assessment.validity_status.value
        step_ctx["battery_endurance_hours"] = assessment.battery_endurance_hours
        step_ctx["diesel_endurance_hours"] = assessment.diesel_endurance_hours
        step_ctx["battery_margin_hours"] = assessment.battery_margin_hours
        step_ctx["diesel_margin_hours"] = assessment.diesel_margin_hours
        step_ctx["preserved_resource"] = assessment.preserved_resource.value
        step_ctx["limiting_resource"] = assessment.limiting_resource.value
        step_ctx["fuel_before_l"] = current_state.diesel_fuel_remaining_liters
        step_ctx["soc_before_pct"] = current_state.battery_soc_pct
        step_ctx["battery_energy_wh_before"] = current_state.battery_energy_wh
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

    # --- 2. NORMAL-route optimizer wrapper ---
    orig_optimize = runner.optimizer.optimize
    optimizer_class_name = type(runner.optimizer).__name__

    def wrapped_optimize(bundle, current_state, configs):
        plan = orig_optimize(bundle, current_state, configs)
        step_ctx["solver"] = optimizer_class_name
        step_ctx["plan"] = plan
        return plan

    runner.optimizer.optimize = wrapped_optimize

    # --- 3. EMERGENCY-route Option D wrapper ---
    orig_solve = runner.option_d_solver.solve
    option_d_class_name = type(runner.option_d_solver).__name__

    def wrapped_solve(assessment, bundle, current_state, configs):
        plan = orig_solve(assessment, bundle, current_state, configs)
        step_ctx["solver"] = option_d_class_name
        step_ctx["plan"] = plan
        return plan

    runner.option_d_solver.solve = wrapped_solve

    # --- 4. Simulator wrapper: finalize the per-step record ---
    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)

        plan = step_ctx.get("plan")
        solar_h1 = float(plan.solar_used[0]) if plan is not None else None
        wind_h1 = float(plan.wind_used[0]) if plan is not None else None
        curtail_h1 = float(plan.renewable_curtailment[0]) if plan is not None else None
        chg_h1 = float(plan.battery_charge[0]) if plan is not None else None
        dis_h1 = float(plan.battery_discharge[0]) if plan is not None else None
        diesel_h1 = float(plan.diesel_power[0]) if plan is not None else None
        served_h1 = float(plan.load_served[0]) if plan is not None else None
        unmet_h1 = float(plan.unmet_load[0]) if plan is not None else None
        plan_soc_h1 = float(plan.battery_soc[0]) if plan is not None else None

        # Post-hoc eligibility upper bound, computed ONLY from the ALREADY-
        # OBSERVED (unmodified) pre-step battery energy and this step's
        # ALREADY-OBSERVED (unmodified) curtailment. Does not simulate a
        # counterfactual charging decision; see report Section on why this
        # is an upper bound, not a guaranteed recoverable figure.
        headroom_dc_wh = max(0.0, max_e_wh - step_ctx.get("battery_energy_wh_before", 0.0))
        max_chg_avail_w = min(max_chg_w, headroom_dc_wh / eta_chg if eta_chg > 0 else 0.0)
        eligible_charge_w = (
            min(curtail_h1, max_chg_avail_w) if curtail_h1 is not None else None
        )

        record = {
            "step": len(trace),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "operating_mode": step_ctx.get("operating_mode"),
            "solver": step_ctx.get("solver"),
            "validity_status": step_ctx.get("validity_status"),
            "preserved_resource": step_ctx.get("preserved_resource"),
            "limiting_resource": step_ctx.get("limiting_resource"),
            "battery_endurance_hours": step_ctx.get("battery_endurance_hours"),
            "diesel_endurance_hours": step_ctx.get("diesel_endurance_hours"),
            "battery_margin_hours": step_ctx.get("battery_margin_hours"),
            "diesel_margin_hours": step_ctx.get("diesel_margin_hours"),
            "fuel_before_l": step_ctx.get("fuel_before_l"),
            "fuel_after_l": state_after.diesel_fuel_remaining_liters,
            "soc_before_pct": step_ctx.get("soc_before_pct"),
            "soc_after_pct": state_after.battery_soc_pct,
            "battery_energy_wh_before": step_ctx.get("battery_energy_wh_before"),
            "battery_energy_wh_after": state_after.battery_energy_wh,
            "forecast_solar_h1_w": step_ctx.get("forecast_solar_h1_w"),
            "forecast_wind_h1_w": step_ctx.get("forecast_wind_h1_w"),
            "forecast_demand_h1_w": step_ctx.get("forecast_demand_h1_w"),
            "forecast_renewable_avail_h1_w": (
                (step_ctx.get("forecast_solar_h1_w") or 0.0) + (step_ctx.get("forecast_wind_h1_w") or 0.0)
            ),
            "plan_solar_used_h1_w": solar_h1,
            "plan_wind_used_h1_w": wind_h1,
            "plan_renewable_used_h1_w": (
                (solar_h1 or 0.0) + (wind_h1 or 0.0) if solar_h1 is not None else None
            ),
            "plan_renewable_curtailment_h1_w": curtail_h1,
            "plan_battery_charge_h1_w": chg_h1,
            "plan_battery_discharge_h1_w": dis_h1,
            "plan_diesel_power_h1_w": diesel_h1,
            "plan_load_served_h1_w": served_h1,
            "plan_unmet_load_h1_w": unmet_h1,
            "plan_battery_soc_h1_pct_SOLVER_INTERNAL": plan_soc_h1,
            "actual_demand_w": actuals_next_step.get("actual_demand"),
            "actual_SW_IN": actuals_next_step.get("actual_SW_IN"),
            "actual_wind_generation_w": actuals_next_step.get("actual_wind_generation"),
            "eligible_for_charging_upper_bound_w": eligible_charge_w,
            "charge_headroom_dc_wh_before_step": headroom_dc_wh,
            "max_chg_avail_w_before_step": max_chg_avail_w,
        }
        trace.append(record)
        step_ctx.clear()
        return state_after

    runner.simulator.step = wrapped_step

    return runner, trace


def main() -> None:
    runner, trace = build_instrumented_runner()

    run_report = runner.run_pipeline(steps_to_run=168)

    out_json = OUTPUT_DIR / "rt01_168h_trace.json"
    out_csv = OUTPUT_DIR / "rt01_168h_trace.csv"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "run_report_summary": {
                    "timesteps_executed": run_report["timesteps_executed"],
                    "execution_status": run_report["execution_status"],
                    "ems_evaluation": run_report["ems_evaluation"],
                },
                "per_step_trace": trace,
            },
            f,
            indent=2,
            default=str,
        )

    if trace:
        fieldnames = list(trace[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in trace:
                writer.writerow(row)

    # --- Console summary (also captured by the report) ---
    print("=" * 80)
    print("POLARIS RT-01 BOUNDED DIAGNOSTIC -- 168h endurance scenario per-step trace")
    print("=" * 80)
    print(f"timesteps_executed: {run_report['timesteps_executed']}")
    print(f"execution_status:   {run_report['execution_status']}")

    first_emergency = next((r for r in trace if r["route"] == "EMERGENCY"), None)
    if first_emergency:
        print(
            f"First EMERGENCY step: step={first_emergency['step']} "
            f"fuel_before_l={first_emergency['fuel_before_l']} "
            f"diesel_margin_hours={first_emergency['diesel_margin_hours']} "
            f"battery_margin_hours={first_emergency['battery_margin_hours']}"
        )
    else:
        print("No EMERGENCY step observed in this run.")

    fuel_exhaustion = next((r for r in trace if (r["fuel_after_l"] or 0.0) <= 0.0), None)
    if fuel_exhaustion:
        print(f"Literal fuel-exhaustion step (fuel_after_l hits 0): step={fuel_exhaustion['step']}")
    else:
        print("Fuel never literally reached 0 L in this run.")

    from collections import Counter

    solver_counts = Counter(r["solver"] for r in trace)
    route_counts = Counter(r["route"] for r in trace)
    print(f"Route counts:  {dict(route_counts)}")
    print(f"Solver counts: {dict(solver_counts)}")

    total_curtailed_wh = sum((r["plan_renewable_curtailment_h1_w"] or 0.0) for r in trace)
    total_eligible_wh = sum((r["eligible_for_charging_upper_bound_w"] or 0.0) for r in trace)
    print(f"Total H1 curtailed (Wh, == W over 1h step): {total_curtailed_wh:.2f}")
    print(f"Total eligible-for-charging upper bound (Wh): {total_eligible_wh:.2f}")

    print(f"\nWrote: {out_json}")
    print(f"Wrote: {out_csv}")
    print("=" * 80)


if __name__ == "__main__":
    main()
