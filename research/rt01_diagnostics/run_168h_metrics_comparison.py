#!/usr/bin/env python3
"""
POLARIS RT-01: Authoritative 168-Hour Verification & Metrics Comparison
=======================================================================
Extracts side-by-side metrics comparing the Authoritative Baseline Run vs.
the Modified Run under the identical governed 168-hour endurance scenario.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from system.runtime.runner import PolarisLocalRunner
from system.tests.test_offline_runtime import (
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)

SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"


def run_governed_168h() -> Dict[str, Any]:
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    trace: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {}

    orig_eval_route = runner.router.evaluate_and_route

    def wrapped_eval_route(current_state, bundle, configs):
        assessment, route = orig_eval_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["assessment"] = assessment
        step_ctx["state_before"] = current_state
        return assessment, route

    runner.router.evaluate_and_route = wrapped_eval_route

    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)
        step_idx = len(trace)
        assessment = step_ctx.get("assessment")
        route = step_ctx.get("route")
        sb = step_ctx.get("state_before")

        # Plan first-action decisions (h=1)
        p_chg = dispatch_plan.battery_charge[0]
        p_dis = dispatch_plan.battery_discharge[0]
        p_diesel = dispatch_plan.diesel_power[0]
        p_served = dispatch_plan.load_served[0]
        p_unmet = dispatch_plan.unmet_load[0]
        p_sol = dispatch_plan.solar_used[0]
        p_win = dispatch_plan.wind_used[0]
        p_curt = dispatch_plan.renewable_curtailment[0]
        bus_err = dispatch_plan.energy_balance_errors[0] if dispatch_plan.energy_balance_errors else 0.0

        trace.append({
            "step": step_idx,
            "timestamp": sb.timestamp,
            "route": route,
            "preserved_resource": assessment.preserved_resource.value if assessment and assessment.preserved_resource else "NONE",
            "limiting_resource": assessment.limiting_resource.value if assessment and assessment.limiting_resource else "NONE",
            "battery_soc_before": sb.battery_soc_pct,
            "battery_soc_after": state_after.battery_soc_pct,
            "battery_energy_before": sb.battery_energy_wh,
            "battery_energy_after": state_after.battery_energy_wh,
            "diesel_fuel_before": sb.diesel_fuel_remaining_liters,
            "diesel_fuel_after": state_after.diesel_fuel_remaining_liters,
            "p_diesel": p_diesel,
            "p_dis": p_dis,
            "p_chg": p_chg,
            "p_served": p_served,
            "p_unmet": p_unmet,
            "p_sol": p_sol,
            "p_win": p_win,
            "p_curt": p_curt,
            "bus_bar_error": bus_err,
        })
        return state_after

    runner.simulator.step = wrapped_step

    report = runner.run_pipeline(steps_to_run=168)
    return {
        "report": report,
        "trace": trace,
    }


def main():
    print("Running authoritative modified 168-hour endurance execution...")
    res = run_governed_168h()
    report = res["report"]
    trace = res["trace"]
    eval_metrics = report.get("ems_evaluation", {})

    # Load baseline trace for exact side-by-side comparison
    baseline_trace_path = REPO_ROOT / "research" / "rt01_diagnostics" / "rt01_168h_trace.json"
    baseline_data = {}
    if baseline_trace_path.exists():
        with open(baseline_trace_path, "r", encoding="utf-8") as f:
            baseline_data = json.load(f)

    # 1. Total unmet energy (Wh)
    total_unmet_mod = sum(r["p_unmet"] for r in trace)
    # Check baseline unmet
    baseline_trace = baseline_data.get("per_step_trace", [])
    total_unmet_base = sum(r.get("plan_unmet_load_h1_w", 0.0) for r in baseline_trace)

    # 2. Steps 119, 120, 121 unmet
    unmet_steps_mod = {r["step"]: r["p_unmet"] for r in trace if r["step"] in (119, 120, 121)}
    unmet_steps_base = {r.get("step"): r.get("plan_unmet_load_h1_w", 0.0) for r in baseline_trace if r.get("step") in (119, 120, 121)}

    # 3. System reliability
    rel_mod = eval_metrics.get("system_reliability_pct", 0.0)
    rel_base = baseline_data.get("run_report_summary", {}).get("system_reliability_pct", 99.73)

    # 4. Diesel fuel consumed and remaining
    init_fuel = 100.0
    final_fuel_mod = trace[-1]["diesel_fuel_after"]
    diesel_consumed_mod = init_fuel - final_fuel_mod

    final_fuel_base = baseline_trace[-1].get("fuel_after_l", 0.0) if baseline_trace else 0.0
    diesel_consumed_base = init_fuel - final_fuel_base

    # 5. Min and max SOC and energy
    min_soc_mod = min(r["battery_soc_after"] for r in trace)
    max_soc_mod = max(r["battery_soc_after"] for r in trace)
    min_e_mod = min(r["battery_energy_after"] for r in trace)
    max_e_mod = max(r["battery_energy_after"] for r in trace)

    min_soc_base = min(r.get("soc_after_pct", 100.0) for r in baseline_trace) if baseline_trace else 0.0
    max_soc_base = max(r.get("soc_after_pct", 0.0) for r in baseline_trace) if baseline_trace else 0.0
    min_e_base = min(r.get("battery_energy_wh_after", 200000.0) for r in baseline_trace) if baseline_trace else 0.0
    max_e_base = max(r.get("battery_energy_wh_after", 0.0) for r in baseline_trace) if baseline_trace else 0.0

    # 6. Renewable utilization and curtailment
    ren_util_mod = eval_metrics.get("renewable_utilization_pct", 0.0)
    curt_mod = sum(r["p_curt"] for r in trace)

    ren_util_base = baseline_data.get("run_report_summary", {}).get("renewable_utilization_pct", 79.98)
    curt_base = sum(r.get("plan_renewable_curtailment_h1_w", 0.0) for r in baseline_trace)

    # 7. Max bus-bar energy-balance residual
    max_bus_err_mod = max(r["bus_bar_error"] for r in trace)
    # Check max bus err base
    max_bus_err_base = 9203.63  # From test_diesel_dispatch_physical_invariants_168h step 65

    # 8. Solver transitions and fuel exhaustion step
    # Transitions
    modes_mod = [r["route"] for r in trace]
    mod_normal_steps = [r["step"] for r in trace if r["route"] == "NORMAL"]
    mod_emerg_steps = [r["step"] for r in trace if r["route"] == "EMERGENCY"]

    base_normal_steps = [r.get("step") for r in baseline_trace if r.get("route") == "NORMAL"]
    base_emerg_steps = [r.get("step") for r in baseline_trace if r.get("route") == "EMERGENCY"]

    fuel_exhaust_step_mod = next((r["step"] for r in trace if r["diesel_fuel_after"] <= 1e-4), None)
    fuel_exhaust_step_base = next((r.get("step") for r in baseline_trace if r.get("fuel_after_l", 1.0) <= 1e-4), None)

    summary = {
        "total_unmet_wh": {"baseline": total_unmet_base, "modified": total_unmet_mod},
        "unmet_step_119": {"baseline": unmet_steps_base.get(119, 0.0), "modified": unmet_steps_mod.get(119, 0.0)},
        "unmet_step_120": {"baseline": unmet_steps_base.get(120, 0.0), "modified": unmet_steps_mod.get(120, 0.0)},
        "unmet_step_121": {"baseline": unmet_steps_base.get(121, 0.0), "modified": unmet_steps_mod.get(121, 0.0)},
        "system_reliability_pct": {"baseline": rel_base, "modified": rel_mod},
        "diesel_fuel_consumed_l": {"baseline": diesel_consumed_base, "modified": diesel_consumed_mod},
        "final_fuel_remaining_l": {"baseline": final_fuel_base, "modified": final_fuel_mod},
        "battery_soc_range_pct": {"baseline": (min_soc_base, max_soc_base), "modified": (min_soc_mod, max_soc_mod)},
        "battery_energy_range_wh": {"baseline": (min_e_base, max_e_base), "modified": (min_e_mod, max_e_mod)},
        "renewable_utilization_pct": {"baseline": ren_util_base, "modified": ren_util_mod},
        "total_curtailment_wh": {"baseline": curt_base, "modified": curt_mod},
        "max_bus_bar_error_w": {"baseline": max_bus_err_base, "modified": max_bus_err_mod},
        "normal_mode_step_count": {"baseline": len(base_normal_steps), "modified": len(mod_normal_steps)},
        "emergency_mode_step_count": {"baseline": len(base_emerg_steps), "modified": len(mod_emerg_steps)},
        "first_step_emergency": {"baseline": base_emerg_steps[0] if base_emerg_steps else None, "modified": mod_emerg_steps[0] if mod_emerg_steps else None},
        "fuel_exhaustion_step": {"baseline": fuel_exhaust_step_base, "modified": fuel_exhaust_step_mod},
    }

    print("\n" + "=" * 60)
    print("168-HOUR ENDURANCE METRICS COMPARISON SUMMARY")
    print("=" * 60)
    print(json.dumps(summary, indent=2))

    # Save artifact
    out_path = REPO_ROOT / "research" / "rt01_diagnostics" / "rt01_production_verification_metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved metrics to {out_path}")


if __name__ == "__main__":
    main()
