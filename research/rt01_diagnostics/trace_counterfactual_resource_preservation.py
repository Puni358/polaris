#!/usr/bin/env python3
"""
POLARIS RT-01 Investigation: Resource Preservation Counterfactual Diagnostic
=============================================================================

Diagnostic Harness to rigorously test the hypothesis that unresolved 14,974.11 Wh
unmet load at steps 119-121 is caused by a structural interaction between
system/control/ecd.py and system/optimization/implementations/option_d.py.

Specifically:
- In EMERGENCY mode, when diesel endurance falls below battery endurance,
  ecd.py flags BATTERY as preserved_resource (and DIESEL as limiting_resource).
- In option_d.py, preserved_resource == BATTERY causes Option D to fire the diesel
  generator to meet critical demand before touching battery reserves.
- This burns the remaining diesel reserve prematurely, exhausting the 100 L tank
  long before step 119, leaving zero fuel when renewable generation drops at steps 119-121.

This diagnostic:
1. Strictly treats protected source files as READ-ONLY (no source code edits).
2. Computes pre- and post-run SHA-256 hashes of all protected files.
3. Establishes the exact 168-hour baseline run.
4. Executes the isolated counterfactual via non-invasive object interception
   (monkeypatching runner.option_d_solver.solve to override preserved_resource to DIESEL
   when battery SOC is safely above the 20.0% floor).
5. Compares baseline vs. counterfactual metrics and exports comprehensive traces.
"""

from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent
SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"

from system.runtime.runner import PolarisLocalRunner
from system.control.ecd import EmergencyAssessment, ResourceSelection
from system.tests.test_offline_runtime import (
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)

PROTECTED_FILES = [
    "system/control/ecd.py",
    "system/optimization/implementations/option_d.py",
    "system/control/router.py",
    "system/runtime/runner.py",
    "system/simulation/simulator.py",
    "system/optimization/implementations/gap19_highs_native.py",
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def get_protected_hashes() -> Dict[str, str]:
    return {f: compute_sha256(REPO_ROOT / f) for f in PROTECTED_FILES}


def run_governed_scenario(
    enable_intervention: bool = False,
    soc_threshold_pct: float = 20.0,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes the 168h endurance scenario with instrumented telemetry.
    If enable_intervention is True, overrides preserved_resource to DIESEL
    in OptionDFallbackSolver when battery SOC > soc_threshold_pct.
    """
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    trace: List[Dict[str, Any]] = []
    intervention_log: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {}

    # 1. Router telemetry wrapper
    orig_evaluate_and_route = runner.router.evaluate_and_route

    def wrapped_evaluate_and_route(current_state, bundle, configs):
        assessment, route = orig_evaluate_and_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["assessment_orig"] = assessment
        step_ctx["fuel_before_l"] = current_state.diesel_fuel_remaining_liters
        step_ctx["soc_before_pct"] = current_state.battery_soc_pct
        step_ctx["battery_energy_wh_before"] = current_state.battery_energy_wh
        return assessment, route

    runner.router.evaluate_and_route = wrapped_evaluate_and_route

    # 2. NORMAL optimizer wrapper
    orig_optimize = runner.optimizer.optimize
    normal_optimizer_name = type(runner.optimizer).__name__

    def wrapped_optimize(bundle, current_state, configs):
        plan = orig_optimize(bundle, current_state, configs)
        step_ctx["solver"] = normal_optimizer_name
        step_ctx["plan"] = plan
        return plan

    runner.optimizer.optimize = wrapped_optimize

    # 3. EMERGENCY Option D solver wrapper
    orig_solve = runner.option_d_solver.solve
    option_d_name = type(runner.option_d_solver).__name__

    def wrapped_solve(assessment, bundle, current_state, configs):
        step_idx = len(trace)
        assessment_used = assessment
        was_overridden = False

        if enable_intervention:
            if assessment.preserved_resource == ResourceSelection.BATTERY and current_state.battery_soc_pct > soc_threshold_pct:
                assessment_used = dataclasses.replace(assessment, preserved_resource=ResourceSelection.DIESEL)
                was_overridden = True
                intervention_log.append({
                    "step": step_idx,
                    "timestamp": current_state.timestamp,
                    "soc_before_pct": current_state.battery_soc_pct,
                    "fuel_remaining_liters": current_state.diesel_fuel_remaining_liters,
                    "original_preserved_resource": assessment.preserved_resource.value,
                    "overridden_preserved_resource": assessment_used.preserved_resource.value,
                    "battery_margin_hours": assessment.battery_margin_hours,
                    "diesel_margin_hours": assessment.diesel_margin_hours,
                    "reason": f"SOC ({current_state.battery_soc_pct:.2f}%) > floor ({soc_threshold_pct:.2f}%); diesel preserved.",
                })

        step_ctx["solver"] = option_d_name
        step_ctx["was_overridden"] = was_overridden
        step_ctx["assessment_used"] = assessment_used
        plan = orig_solve(assessment_used, bundle, current_state, configs)
        step_ctx["plan"] = plan
        return plan

    runner.option_d_solver.solve = wrapped_solve

    # 4. Simulator step wrapper
    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)
        plan = step_ctx.get("plan")
        assessment_orig = step_ctx.get("assessment_orig")
        assessment_used = step_ctx.get("assessment_used")

        trace_entry = {
            "step": len(trace),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "solver": step_ctx.get("solver"),
            "was_overridden": step_ctx.get("was_overridden", False),
            "orig_preserved_resource": assessment_orig.preserved_resource.value if assessment_orig else None,
            "used_preserved_resource": assessment_used.preserved_resource.value if assessment_used else (
                assessment_orig.preserved_resource.value if assessment_orig else None
            ),
            "limiting_resource": assessment_orig.limiting_resource.value if assessment_orig else None,
            "battery_margin_hours": assessment_orig.battery_margin_hours if assessment_orig else None,
            "diesel_margin_hours": assessment_orig.diesel_margin_hours if assessment_orig else None,
            "battery_endurance_hours": assessment_orig.battery_endurance_hours if assessment_orig else None,
            "diesel_endurance_hours": assessment_orig.diesel_endurance_hours if assessment_orig else None,
            "fuel_before_l": step_ctx.get("fuel_before_l"),
            "fuel_after_l": state_after.diesel_fuel_remaining_liters,
            "soc_before_pct": step_ctx.get("soc_before_pct"),
            "soc_after_pct": state_after.battery_soc_pct,
            "battery_energy_wh_before": step_ctx.get("battery_energy_wh_before"),
            "battery_energy_wh_after": state_after.battery_energy_wh,
            "plan_solar_used_h1_w": float(plan.solar_used[0]) if plan else 0.0,
            "plan_wind_used_h1_w": float(plan.wind_used[0]) if plan else 0.0,
            "plan_renewable_used_h1_w": (float(plan.solar_used[0]) + float(plan.wind_used[0])) if plan else 0.0,
            "plan_renewable_curtailment_h1_w": float(plan.renewable_curtailment[0]) if plan else 0.0,
            "plan_battery_charge_h1_w": float(plan.battery_charge[0]) if plan else 0.0,
            "plan_battery_discharge_h1_w": float(plan.battery_discharge[0]) if plan else 0.0,
            "plan_diesel_power_h1_w": float(plan.diesel_power[0]) if plan else 0.0,
            "plan_load_served_h1_w": float(plan.load_served[0]) if plan else 0.0,
            "plan_unmet_load_h1_w": float(plan.unmet_load[0]) if plan else 0.0,
            "actual_demand_w": actuals_next_step.get("actual_demand"),
            "actual_wind_generation_w": actuals_next_step.get("actual_wind_generation"),
            "actual_SW_IN": actuals_next_step.get("actual_SW_IN"),
        }
        trace.append(trace_entry)
        step_ctx.clear()
        return state_after

    runner.simulator.step = wrapped_step

    report = runner.run_pipeline(steps_to_run=168)
    return report, trace, intervention_log


def extract_key_metrics(report: Dict[str, Any], trace: List[Dict[str, Any]]) -> Dict[str, Any]:
    ems = report.get("ems_evaluation", {})
    total_unmet_wh = sum(t["plan_unmet_load_h1_w"] for t in trace)
    unmet_119_121_wh = sum(t["plan_unmet_load_h1_w"] for t in trace if t["step"] in (119, 120, 121))
    unmet_119 = next((t["plan_unmet_load_h1_w"] for t in trace if t["step"] == 119), 0.0)
    unmet_120 = next((t["plan_unmet_load_h1_w"] for t in trace if t["step"] == 120), 0.0)
    unmet_121 = next((t["plan_unmet_load_h1_w"] for t in trace if t["step"] == 121), 0.0)

    # Literal fuel exhaustion step
    exhaustion_step = None
    for t in trace:
        if (t["fuel_after_l"] or 0.0) <= 0.0001:
            exhaustion_step = t["step"]
            break

    initial_fuel = trace[0]["fuel_before_l"] if trace else 100.0
    final_fuel = trace[-1]["fuel_after_l"] if trace else 0.0
    total_diesel_burned_l = initial_fuel - final_fuel

    min_soc = min(t["soc_after_pct"] for t in trace) if trace else 0.0
    max_soc = max(t["soc_after_pct"] for t in trace) if trace else 0.0

    return {
        "timesteps_executed": report.get("timesteps_executed", 168),
        "execution_status": report.get("execution_status"),
        "total_unmet_load_wh": round(total_unmet_wh, 2),
        "total_unmet_load_kwh": round(total_unmet_wh / 1000.0, 4),
        "steps_119_121_unmet_wh": round(unmet_119_121_wh, 2),
        "step_119_unmet_wh": round(unmet_119, 2),
        "step_120_unmet_wh": round(unmet_120, 2),
        "step_121_unmet_wh": round(unmet_121, 2),
        "total_diesel_fuel_consumed_l": round(total_diesel_burned_l, 2),
        "final_fuel_remaining_l": round(final_fuel, 2),
        "fuel_exhaustion_step": exhaustion_step,
        "renewable_utilization_pct": round(float(ems.get("renewable_utilization_pct", 0.0)), 2),
        "renewable_curtailment_pct": round(float(ems.get("renewable_curtailment_pct", 0.0)), 2),
        "system_reliability_pct": round(float(ems.get("system_reliability_pct", 0.0)), 2),
        "min_soc_pct": round(min_soc, 2),
        "max_soc_pct": round(max_soc, 2),
    }


def main():
    print("=" * 80)
    print("POLARIS RT-01 INVESTIGATION: RESOURCE PRESERVATION COUNTERFACTUAL")
    print("=" * 80)

    # 1. Pre-execution verification of protected files
    pre_hashes = get_protected_hashes()
    print("Pre-execution SHA-256 hashes of protected files verified.")

    # 2. Run Baseline
    print("\nExecuting governed 168h baseline run...")
    baseline_report, baseline_trace, _ = run_governed_scenario(enable_intervention=False)
    baseline_metrics = extract_key_metrics(baseline_report, baseline_trace)
    print(f"Baseline complete: Unmet 119-121 = {baseline_metrics['steps_119_121_unmet_wh']:.2f} Wh, Total = {baseline_metrics['total_unmet_load_wh']:.2f} Wh")

    # 3. Run Counterfactual
    print("\nExecuting counterfactual run (override preserved_resource -> DIESEL when SOC > 20.0%)...")
    cf_report, cf_trace, intervention_log = run_governed_scenario(enable_intervention=True, soc_threshold_pct=20.0)
    cf_metrics = extract_key_metrics(cf_report, cf_trace)
    print(f"Counterfactual complete: Unmet 119-121 = {cf_metrics['steps_119_121_unmet_wh']:.2f} Wh, Total = {cf_metrics['total_unmet_load_wh']:.2f} Wh")

    # 4. Post-execution verification of protected files
    post_hashes = get_protected_hashes()
    for f in PROTECTED_FILES:
        assert pre_hashes[f] == post_hashes[f], f"CRITICAL: Protected file {f} was modified on disk!"
    print("Post-execution SHA-256 hashes verified: 0 files modified on disk.")

    # 5. Extract critical window trace (steps 40 to 121)
    critical_window = []
    for step in range(40, 122):
        b = baseline_trace[step]
        c = cf_trace[step]
        critical_window.append({
            "step": step,
            "timestamp": b["timestamp"],
            "baseline": {
                "route": b["route"],
                "solver": b["solver"],
                "preserved_resource": b["used_preserved_resource"],
                "fuel_before_l": b["fuel_before_l"],
                "fuel_after_l": b["fuel_after_l"],
                "soc_before_pct": b["soc_before_pct"],
                "soc_after_pct": b["soc_after_pct"],
                "diesel_power_w": b["plan_diesel_power_h1_w"],
                "battery_discharge_w": b["plan_battery_discharge_h1_w"],
                "renewable_used_w": b["plan_renewable_used_h1_w"],
                "demand_w": b["actual_demand_w"],
                "unmet_load_w": b["plan_unmet_load_h1_w"],
            },
            "counterfactual": {
                "route": c["route"],
                "solver": c["solver"],
                "was_overridden": c["was_overridden"],
                "orig_preserved_resource": c["orig_preserved_resource"],
                "used_preserved_resource": c["used_preserved_resource"],
                "fuel_before_l": c["fuel_before_l"],
                "fuel_after_l": c["fuel_after_l"],
                "soc_before_pct": c["soc_before_pct"],
                "soc_after_pct": c["soc_after_pct"],
                "diesel_power_w": c["plan_diesel_power_h1_w"],
                "battery_discharge_w": c["plan_battery_discharge_h1_w"],
                "renewable_used_w": c["plan_renewable_used_h1_w"],
                "demand_w": c["actual_demand_w"],
                "unmet_load_w": c["plan_unmet_load_h1_w"],
            }
        })

    # 6. Save JSON trace artifact
    output_artifact = {
        "meta": {
            "title": "POLARIS RT-01 Resource Preservation Counterfactual Trace",
            "scenario": SCENARIO_FILENAME,
            "timesteps": 168,
            "intervention_description": "Override preserved_resource to DIESEL in OptionDFallbackSolver when SOC > 20.0%",
            "protected_file_hashes": pre_hashes,
        },
        "comparison_metrics": {
            "baseline": baseline_metrics,
            "counterfactual": cf_metrics,
            "reduction_step_119_121_wh": baseline_metrics["steps_119_121_unmet_wh"] - cf_metrics["steps_119_121_unmet_wh"],
            "shortfall_eliminated_exactly": (cf_metrics["steps_119_121_unmet_wh"] == 0.0),
            "physical_constraints_satisfied": {
                "fuel_budget_100l": (cf_metrics["total_diesel_fuel_consumed_l"] <= 100.0),
                "soc_floor_20pct": (cf_metrics["min_soc_pct"] >= 20.0),
                "soc_ceiling_95pct": (cf_metrics["max_soc_pct"] <= 95.0),
                "renewable_util_75pct": (cf_metrics["renewable_utilization_pct"] >= 75.0),
            }
        },
        "interventions_applied_count": len(intervention_log),
        "interventions_log": intervention_log,
        "critical_window_steps_40_121": critical_window,
        "baseline_trace": baseline_trace,
        "counterfactual_trace": cf_trace,
    }

    out_json = OUTPUT_DIR / "rt01_resource_preservation_counterfactual_trace.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output_artifact, f, indent=2)
    print(f"\nWrote full trace artifact to: {out_json}")

    # Print summary table
    print("\n" + "=" * 80)
    print("METRICS COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Metric':<38} | {'Baseline':<18} | {'Counterfactual':<18}")
    print("-" * 80)
    print(f"{'Total 168h Unmet Load (Wh)':<38} | {baseline_metrics['total_unmet_load_wh']:<18.2f} | {cf_metrics['total_unmet_load_wh']:<18.2f}")
    print(f"{'Steps 119-121 Unmet Load (Wh)':<38} | {baseline_metrics['steps_119_121_unmet_wh']:<18.2f} | {cf_metrics['steps_119_121_unmet_wh']:<18.2f}")
    print(f"{'  - Step 119 Unmet Load (Wh)':<38} | {baseline_metrics['step_119_unmet_wh']:<18.2f} | {cf_metrics['step_119_unmet_wh']:<18.2f}")
    print(f"{'  - Step 120 Unmet Load (Wh)':<38} | {baseline_metrics['step_120_unmet_wh']:<18.2f} | {cf_metrics['step_120_unmet_wh']:<18.2f}")
    print(f"{'  - Step 121 Unmet Load (Wh)':<38} | {baseline_metrics['step_121_unmet_wh']:<18.2f} | {cf_metrics['step_121_unmet_wh']:<18.2f}")
    print(f"{'Total Diesel Consumed (L)':<38} | {baseline_metrics['total_diesel_fuel_consumed_l']:<18.2f} | {cf_metrics['total_diesel_fuel_consumed_l']:<18.2f}")
    print(f"{'Final Diesel Fuel Remaining (L)':<38} | {baseline_metrics['final_fuel_remaining_l']:<18.2f} | {cf_metrics['final_fuel_remaining_l']:<18.2f}")
    ex_b = f"Step {baseline_metrics['fuel_exhaustion_step']}" if baseline_metrics['fuel_exhaustion_step'] is not None else "Never"
    ex_c = f"Step {cf_metrics['fuel_exhaustion_step']}" if cf_metrics['fuel_exhaustion_step'] is not None else "Never (>168h)"
    print(f"{'Fuel Exhaustion Step':<38} | {ex_b:<18} | {ex_c:<18}")
    print(f"{'Renewable Utilization (%)':<38} | {baseline_metrics['renewable_utilization_pct']:<18.2f} | {cf_metrics['renewable_utilization_pct']:<18.2f}")
    print(f"{'System Reliability (%)':<38} | {baseline_metrics['system_reliability_pct']:<18.2f} | {cf_metrics['system_reliability_pct']:<18.2f}")
    print(f"{'Battery Min SOC (%)':<38} | {baseline_metrics['min_soc_pct']:<18.2f} | {cf_metrics['min_soc_pct']:<18.2f}")
    print(f"{'Battery Max SOC (%)':<38} | {baseline_metrics['max_soc_pct']:<18.2f} | {cf_metrics['max_soc_pct']:<18.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
