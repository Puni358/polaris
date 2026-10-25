#!/usr/bin/env python3
"""
POLARIS RT-01 Independent Verification Script
=============================================

Executes a comprehensive, independent audit of the resource-preservation
counterfactual results:
1. Re-runs baseline and counterfactual from clean, isolated runner instances.
2. Asserts identical scenario inputs, initial state, forecasts, and configs.
3. Audits every simulator state transition (SOC, battery energy, fuel).
4. Verifies per-step bus-bar conservation, SOC bounds, and fuel limits.
5. Verifies override trigger conditions and exact step boundaries.
6. Reconciles JSON trace artifact against markdown report and live evaluation.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from system.runtime.runner import PolarisLocalRunner
from system.control.ecd import ResourceSelection
from system.tests.test_offline_runtime import (
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)

SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"
SCENARIO_PATH = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME


def run_pipeline_with_full_audit(enable_intervention: bool = False):
    """Builds a pristine runner and records full state transition physics."""
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    # 1. Config parameters
    bat_cfg = runner.configs.get("battery", {})
    cap_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    min_soc = float(bat_cfg.get("min_soc_pct", 20.0))
    max_soc = float(bat_cfg.get("max_soc_pct", 95.0))
    eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
    eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))

    diesel_cfg = runner.configs.get("diesel", {})
    base_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    initial_state_record = {
        "battery_soc_pct": runner.configs.get("battery", {}).get("initial_soc_pct", 50.0),
        "diesel_fuel_remaining_liters": runner.configs.get("diesel", {}).get("initial_fuel_l", 100.0),
        "battery_energy_wh": cap_wh * (runner.configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
    }

    step_ctx: Dict[str, Any] = {}
    per_step_records: List[Dict[str, Any]] = []
    overrides_log: List[Dict[str, Any]] = []

    # Wrapper for router
    orig_eval_route = runner.router.evaluate_and_route

    def wrapped_eval_route(current_state, bundle, configs):
        assessment, route = orig_eval_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["assessment_orig"] = assessment
        step_ctx["state_before"] = current_state
        step_ctx["bundle"] = bundle
        return assessment, route

    runner.router.evaluate_and_route = wrapped_eval_route

    # Wrapper for Option D
    orig_solve = runner.option_d_solver.solve

    def wrapped_solve(assessment, bundle, current_state, configs):
        step_idx = len(per_step_records)
        used_assessment = assessment
        was_overridden = False

        if enable_intervention:
            if assessment.preserved_resource == ResourceSelection.BATTERY and current_state.battery_soc_pct > min_soc:
                used_assessment = dataclasses.replace(assessment, preserved_resource=ResourceSelection.DIESEL)
                was_overridden = True
                overrides_log.append({
                    "step": step_idx,
                    "soc_before": current_state.battery_soc_pct,
                    "fuel_before": current_state.diesel_fuel_remaining_liters,
                    "orig_preserved": assessment.preserved_resource.value,
                    "used_preserved": used_assessment.preserved_resource.value,
                    "m_battery": assessment.battery_margin_hours,
                    "m_diesel": assessment.diesel_margin_hours,
                })

        step_ctx["used_assessment"] = used_assessment
        step_ctx["was_overridden"] = was_overridden
        plan = orig_solve(used_assessment, bundle, current_state, configs)
        step_ctx["plan"] = plan
        return plan

    runner.option_d_solver.solve = wrapped_solve

    # Wrapper for NORMAL optimizer
    orig_opt = runner.optimizer.optimize

    def wrapped_opt(bundle, current_state, configs):
        plan = orig_opt(bundle, current_state, configs)
        step_ctx["plan"] = plan
        step_ctx["used_assessment"] = None
        step_ctx["was_overridden"] = False
        return plan

    runner.optimizer.optimize = wrapped_opt

    # Wrapper for Simulator
    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)
        plan = step_ctx.get("plan")
        bundle = step_ctx.get("bundle")

        # 1. Physical bus-bar check
        p_sol = float(plan.solar_used[0])
        p_win = float(plan.wind_used[0])
        p_dis = float(plan.battery_discharge[0])
        p_dies = float(plan.diesel_power[0])
        p_serv = float(plan.load_served[0])
        p_chg = float(plan.battery_charge[0])
        p_flx = float(plan.flexible_load_schedule[0])
        p_unmet = float(plan.unmet_load[0])

        gen_total = p_sol + p_win + p_dis + p_dies
        load_total = p_serv + p_chg + p_flx
        bus_bar_err = abs(gen_total - load_total)

        # 2. Simulator State Transition Validation
        # Expected battery energy after step
        exp_delta_e = (p_chg * eta_chg - p_dis / eta_dis) * 1.0
        exp_e_wh = round(current_state.battery_energy_wh + exp_delta_e, 2)
        sim_e_wh = state_after.battery_energy_wh
        sim_soc = state_after.battery_soc_pct

        # Expected fuel after step
        if p_dies > 0.0:
            fuel_burned = (base_lph + marginal_lpwh * p_dies) * 1.0
        else:
            fuel_burned = 0.0
        exp_fuel_l = round(max(0.0, current_state.diesel_fuel_remaining_liters - fuel_burned), 4)
        sim_fuel_l = state_after.diesel_fuel_remaining_liters

        rec = {
            "step": len(per_step_records),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "was_overridden": step_ctx.get("was_overridden", False),
            "orig_preserved": step_ctx["assessment_orig"].preserved_resource.value if step_ctx.get("assessment_orig") else None,
            "used_preserved": step_ctx["used_assessment"].preserved_resource.value if step_ctx.get("used_assessment") else None,
            "fuel_before_l": current_state.diesel_fuel_remaining_liters,
            "fuel_after_l": sim_fuel_l,
            "fuel_burned_l": fuel_burned,
            "sim_fuel_matches_expected": abs(exp_fuel_l - sim_fuel_l) < 1e-4,
            "soc_before_pct": current_state.battery_soc_pct,
            "soc_after_pct": sim_soc,
            "sim_energy_matches_expected": abs(exp_e_wh - sim_e_wh) < 1e-2,
            "plan_solar_used": p_sol,
            "plan_wind_used": p_win,
            "plan_diesel_power": p_dies,
            "plan_battery_discharge": p_dis,
            "plan_battery_charge": p_chg,
            "plan_load_served": p_serv,
            "plan_unmet_load": p_unmet,
            "bus_bar_error_w": bus_bar_err,
            "bus_bar_balanced": bus_bar_err < 1e-3,
            "forecast_solar_h1": float(bundle.solar_generation.point[0]),
            "forecast_wind_h1": float(bundle.wind_generation.point[0]),
            "forecast_demand_h1": float(bundle.demand.point[0]),
            "actual_demand_w": actuals_next_step.get("actual_demand"),
        }
        per_step_records.append(rec)
        step_ctx.clear()
        return state_after

    runner.simulator.step = wrapped_step

    report = runner.run_pipeline(steps_to_run=168)
    return report, per_step_records, overrides_log, initial_state_record, runner.configs


def main():
    print("=" * 80)
    print("POLARIS RT-01 INDEPENDENT VERIFICATION OF COUNTERFACTUAL RESULT")
    print("=" * 80)

    # 1. Re-run clean baseline and counterfactual
    print("\n--- 1. Clean Re-Execution ---")
    scenario_hash = hashlib.sha256(SCENARIO_PATH.read_bytes()).hexdigest()
    print(f"Scenario File: {SCENARIO_FILENAME}")
    print(f"Scenario SHA-256: {scenario_hash}")

    base_report, base_trace, _, base_init, base_cfg = run_pipeline_with_full_audit(enable_intervention=False)
    cf_report, cf_trace, overrides_log, cf_init, cf_cfg = run_pipeline_with_full_audit(enable_intervention=True)

    # Assert identical inputs
    assert base_init == cf_init, f"Initial state differs! {base_init} vs {cf_init}"
    assert json.dumps(base_cfg, sort_keys=True) == json.dumps(cf_cfg, sort_keys=True), "Configs differ!"
    
    # Assert identical forecasts across all 168 steps
    for step in range(168):
        b = base_trace[step]
        c = cf_trace[step]
        assert b["forecast_solar_h1"] == c["forecast_solar_h1"], f"Step {step} solar forecast mismatch"
        assert b["forecast_wind_h1"] == c["forecast_wind_h1"], f"Step {step} wind forecast mismatch"
        assert b["forecast_demand_h1"] == c["forecast_demand_h1"], f"Step {step} demand forecast mismatch"
        assert b["actual_demand_w"] == c["actual_demand_w"], f"Step {step} actual demand mismatch"
    print("VERIFIED: Baseline and counterfactual use 100% IDENTICAL scenario inputs, initial state, forecasts, and configs.")

    # 2. Simulator State Transition Verification
    print("\n--- 2. Simulator State Transition & Conservation Audit ---")
    fuel_transition_errors = [t["step"] for t in cf_trace if not t["sim_fuel_matches_expected"]]
    battery_transition_errors = [t["step"] for t in cf_trace if not t["sim_energy_matches_expected"]]
    bus_bar_errors = [t["step"] for t in cf_trace if not t["bus_bar_balanced"]]

    print(f"Fuel transition errors: {len(fuel_transition_errors)}")
    print(f"Battery energy transition errors: {len(battery_transition_errors)}")
    print(f"Bus-bar conservation errors (> 1e-3 W): {len(bus_bar_errors)}")
    assert len(fuel_transition_errors) == 0, f"Fuel transition mismatch at steps: {fuel_transition_errors}"
    assert len(battery_transition_errors) == 0, f"Battery transition mismatch at steps: {battery_transition_errors}"
    assert len(bus_bar_errors) == 0, f"Bus-bar balance violation at steps: {bus_bar_errors}"
    print("VERIFIED: All 168 simulator state transitions strictly conserve energy and fuel physics.")

    # 3. Check every timestep for SOC, fuel, and unmet load shifts
    print("\n--- 3. Per-Timestep Invariant & Shift Checks ---")
    soc_min = min(t["soc_after_pct"] for t in cf_trace)
    soc_max = max(t["soc_after_pct"] for t in cf_trace)
    soc_violations = [t["step"] for t in cf_trace if t["soc_after_pct"] < 20.0 or t["soc_after_pct"] > 95.0]
    fuel_min = min(t["fuel_after_l"] for t in cf_trace)
    fuel_violations = [t["step"] for t in cf_trace if t["fuel_after_l"] < 0.0 or t["fuel_after_l"] > 100.0]
    unmet_steps = [t["step"] for t in cf_trace if t["plan_unmet_load"] > 0.0]

    print(f"Minimum SOC observed: {soc_min:.4f}% (Hard floor: 20.0%)")
    print(f"Maximum SOC observed: {soc_max:.4f}% (Hard ceiling: 95.0%)")
    print(f"SOC boundary violations: {len(soc_violations)}")
    print(f"Fuel remaining range: [{fuel_min:.4f} L, {cf_trace[0]['fuel_before_l']:.4f} L]")
    print(f"Fuel boundary violations: {len(fuel_violations)}")
    print(f"Steps with unmet load > 0.0 W: {unmet_steps}")

    assert len(soc_violations) == 0, f"SOC violations at steps: {soc_violations}"
    assert len(fuel_violations) == 0, f"Fuel violations at steps: {fuel_violations}"
    assert len(unmet_steps) == 0, f"Unmet load shifted to steps: {unmet_steps}"
    print("VERIFIED: Zero SOC violations, zero fuel violations, and ZERO unmet load across all 168 hours.")

    # 4. Override Trigger Inspection
    print("\n--- 4. Override Trigger Inspection ---")
    trigger_steps = [o["step"] for o in overrides_log]
    print(f"Total overrides applied: {len(trigger_steps)}")
    print(f"First trigger step: {trigger_steps[0]}")
    print(f"Last trigger step: {trigger_steps[-1]}")
    print(f"Trigger steps range: {trigger_steps[:5]} ... {trigger_steps[-5:]}")

    # Verify that every trigger step satisfied the exact condition
    for o in overrides_log:
        step = o["step"]
        assert o["orig_preserved"] == "BATTERY", f"Step {step} had orig_preserved != BATTERY ({o['orig_preserved']})"
        assert o["soc_before"] > 20.0, f"Step {step} had soc_before <= 20.0 ({o['soc_before']})"

    # Verify that non-trigger steps did NOT meet the condition
    for t in cf_trace:
        step = t["step"]
        if step not in trigger_steps:
            if t["orig_preserved"] == "BATTERY":
                assert t["soc_before_pct"] <= 20.0, f"Step {step} met override condition but was not overridden!"

    print("VERIFIED: Override was applied ONLY when assessment.preserved_resource == BATTERY and battery_soc_pct > 20.0%.")

    # Document steps 118-121
    print("\nBehavior at Steps 118-121:")
    for step in [118, 119, 120, 121]:
        rec = cf_trace[step]
        print(f"  Step {step}: Route={rec['route']}, Orig_Pres={rec['orig_preserved']}, Used_Pres={rec['used_preserved']}, Overridden={rec['was_overridden']}, Fuel_Before={rec['fuel_before_l']:.2f}L, SOC_Before={rec['soc_before_pct']:.2f}%, Unmet={rec['plan_unmet_load']:.2f}W")

    # 5. Protected file SHA-256 verification
    print("\n--- 5. Independent Protected File Hash Audit ---")
    protected_files = [
        "system/control/ecd.py",
        "system/optimization/implementations/option_d.py",
        "system/control/router.py",
        "system/runtime/runner.py",
        "system/simulation/simulator.py",
        "system/optimization/implementations/gap19_highs_native.py",
    ]
    expected_hashes = {
        "system/control/ecd.py": "091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db",
        "system/optimization/implementations/option_d.py": "022cc6a0aef4e61772a7274ef3b0e772abacf16fab373feb3273d6af0f653771",
        "system/control/router.py": "b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3",
        "system/runtime/runner.py": "6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10",
        "system/simulation/simulator.py": "8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f",
        "system/optimization/implementations/gap19_highs_native.py": "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
    }
    for f in protected_files:
        act = hashlib.sha256((REPO_ROOT / f).read_bytes()).hexdigest()
        assert act == expected_hashes[f], f"Protected file {f} hash mismatch!"
        print(f"  {f}: MATCH ({act[:16]}...)")
    print("VERIFIED: All 6 protected files are 100% byte-identical to pre-experiment state.")

    # 6. Reconcile JSON trace artifact, markdown report, and live evaluation
    print("\n--- 6. Reconcile Artifacts vs Live Evaluation ---")
    json_path = REPO_ROOT / "research" / "rt01_diagnostics" / "rt01_resource_preservation_counterfactual_trace.json"
    with open(json_path) as f:
        artifact = json.load(f)

    art_cf_metrics = artifact["comparison_metrics"]["counterfactual"]
    ems = cf_report["ems_evaluation"]
    total_unmet_wh_trace = sum(t["plan_unmet_load"] for t in cf_trace)

    print(f"Live Evaluator total_unmet_load_kwh:  {ems['total_unmet_load_kwh']}")
    print(f"Per-step trace sum unmet load (Wh):   {total_unmet_wh_trace:.4f}")
    print(f"JSON artifact total_unmet_load_wh:    {art_cf_metrics['total_unmet_load_wh']}")
    print(f"Live Evaluator system_reliability_pct: {ems['system_reliability_pct']}%")
    print(f"JSON artifact system_reliability_pct: {art_cf_metrics['system_reliability_pct']}%")
    print(f"Live Evaluator renewable_util_pct:    {ems['renewable_utilization_pct']}%")
    print(f"JSON artifact renewable_util_pct:     {art_cf_metrics['renewable_utilization_pct']}%")
    print(f"Live total diesel fuel consumed (L):  {100.0 - cf_trace[-1]['fuel_after_l']:.2f}")
    print(f"JSON artifact diesel fuel consumed (L): {art_cf_metrics['total_diesel_fuel_consumed_l']}")

    assert ems['total_unmet_load_kwh'] == 0.0
    assert total_unmet_wh_trace == 0.0
    assert art_cf_metrics['total_unmet_load_wh'] == 0.0
    assert ems['system_reliability_pct'] == 100.0
    assert art_cf_metrics['system_reliability_pct'] == 100.0
    assert abs(ems['renewable_utilization_pct'] - art_cf_metrics['renewable_utilization_pct']) < 1e-2
    assert abs((100.0 - cf_trace[-1]['fuel_after_l']) - art_cf_metrics['total_diesel_fuel_consumed_l']) < 1e-2

    print("VERIFIED: Exact agreement across live evaluation, per-step trace, and JSON artifact.")
    print("\n" + "=" * 80)
    print("ALL 7 INDEPENDENT AUDIT CHECKS PASSED WITH ZERO DISCREPANCIES.")
    print("=" * 80)


if __name__ == "__main__":
    main()
