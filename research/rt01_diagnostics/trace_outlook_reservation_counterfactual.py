#!/usr/bin/env python3
"""
POLARIS -- RT-01 Stage 2 Forecast-Outlook Reservation: Baseline-vs-Stage2 168h Counterfactual
================================================================================================

Owner-authorized ("POLARIS RT-01 -- STAGE 2 FORECAST-OUTLOOK RESERVATION").
This script runs the REAL, full 168-step `PolarisLocalRunner.run_pipeline()` on the
governed `synthetic_168h_endurance_scenario.json` scenario TWICE, using the exact
instance-method-wrapping instrumentation pattern already established by
`trace_step119_counterfactual.py` and `trace_stage1_reservation_counterfactual.py`
(no source file is edited by this script):

  1. "baseline" -- the real, unmodified pipeline, with BOTH the Stage 1 static
     reservation knobs AND the Stage 2 outlook_trigger forced IN-MEMORY to their
     fully-inert/disabled defaults. No source file is reverted.
  2. "outlook"  -- the real, unmodified pipeline, using the REAL on-disk
     `system/config/optimizer.yaml` values actually shipped by this pass
     (Stage 1 static knobs left inert; Stage 2 `reservation.outlook_trigger.enabled: true`).

Per step, this script records: the real ForecastBundle's `extended_outlook` metadata
(lookahead, projected min net-renewable margin, confidence), the reservation target
and outlook-triggered flag `LocalMILPEnergyOptimizer` actually computed (surfaced via
`DispatchPlan.reservation_target_wh`/`outlook_triggered_flag`), `reserve_shortfall`,
SOC before/after, fuel before/after, dispatch (solar/wind/battery/diesel), curtailment,
and unmet load -- exactly the fields the directive requires.

Both runs verify pre/post SHA-256 hashes of the 7 PROTECTED_FILES. `milp.py`,
`baseline.py`, `dispatch_plan.py`, and `optimizer.yaml` are NOT in that protected
set -- their hashes are expected to differ from any prior pass's recorded value
(this pass changed them), but must be IDENTICAL between the "baseline" and
"outlook" runs in this script (same on-disk files for both; only the in-memory
config dict differs for "baseline").
"""
from __future__ import annotations

import copy
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

PROTECTED_HASH_TARGETS = [
    "system/optimization/implementations/gap19_highs_native.py",
    "system/optimization/implementations/option_d.py",
    "system/control/ecd.py",
    "system/control/router.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "system/orchestration/manifest.py",
]
TRACKED_UNPROTECTED_TARGETS = [
    "system/optimization/implementations/milp.py",
    "system/forecasting/implementations/baseline.py",
    "system/schemas/dispatch_plan.py",
    "system/config/optimizer.yaml",
    "system/config/battery.yaml",
    "system/config/diesel.yaml",
    "system/config/loads.yaml",
    "system/config/solar_pv.yaml",
    "system/config/station.yaml",
    f"system/data/scenarios/{SCENARIO_FILENAME}",
]
HASH_TARGETS = PROTECTED_HASH_TARGETS + TRACKED_UNPROTECTED_TARGETS


def sha256_of(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_hash_manifest() -> Dict[str, Optional[str]]:
    return {rel: sha256_of(REPO_ROOT / rel) for rel in HASH_TARGETS}


def build_instrumented_runner(mode: str):
    """mode: 'baseline' (Stage 1 + Stage 2 forced fully inert/disabled,
    in-memory only) or 'outlook' (real on-disk optimizer.yaml values,
    unmodified -- Stage 1 static knobs inert, Stage 2 outlook_trigger
    enabled)."""
    assert mode in ("baseline", "outlook")

    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    if mode == "baseline":
        runner.configs = copy.deepcopy(runner.configs)
        opt_cfg = runner.configs.setdefault("optimizer", {})
        opt_cfg.setdefault("weights", {})["reserve_shortfall_penalty"] = 0.0
        min_soc_pct = float(runner.configs.get("battery", {}).get("min_soc_pct", 20.0))
        opt_cfg["reservation"] = {
            "terminal_target_soc_pct": min_soc_pct,
            "fuel_reserve_target_l": 0.0,
            "outlook_trigger": {"enabled": False},
        }

    trace: List[Dict[str, Any]] = []
    step_ctx: Dict[str, Any] = {}

    orig_predict = runner.forecast_engine.predict

    def wrapped_predict(station_state, runtime_context):
        bundle = orig_predict(station_state, runtime_context)
        step_ctx["extended_outlook"] = None
        try:
            md = getattr(bundle, "metadata", None)
            if isinstance(md, dict):
                step_ctx["extended_outlook"] = md.get("extended_outlook")
        except Exception:
            step_ctx["extended_outlook"] = None
        return bundle

    runner.forecast_engine.predict = wrapped_predict

    orig_evaluate_and_route = runner.router.evaluate_and_route

    def wrapped_evaluate_and_route(current_state, bundle, configs):
        assessment, route = orig_evaluate_and_route(current_state, bundle, configs)
        step_ctx["route"] = route
        step_ctx["fuel_before_l"] = current_state.diesel_fuel_remaining_liters
        step_ctx["soc_before_pct"] = current_state.battery_soc_pct
        return assessment, route

    runner.router.evaluate_and_route = wrapped_evaluate_and_route

    orig_optimize = runner.optimizer.optimize

    def wrapped_optimize(bundle, current_state, configs):
        plan = orig_optimize(bundle, current_state, configs)
        step_ctx["solver"] = "LocalMILPEnergyOptimizer"
        step_ctx["plan"] = plan
        return plan

    runner.optimizer.optimize = wrapped_optimize

    orig_solve = runner.option_d_solver.solve

    def wrapped_solve(assessment, bundle, current_state, configs):
        plan = orig_solve(assessment, bundle, current_state, configs)
        step_ctx["solver"] = "OptionDFallbackSolver"
        step_ctx["plan"] = plan
        return plan

    runner.option_d_solver.solve = wrapped_solve

    orig_step = runner.simulator.step

    def wrapped_step(current_state, dispatch_plan, actuals_next_step):
        state_after = orig_step(current_state, dispatch_plan, actuals_next_step)
        plan = step_ctx.get("plan")
        reserve_shortfall_terminal = None
        reservation_target_wh_terminal = None
        outlook_triggered = None
        if plan is not None:
            if getattr(plan, "reserve_shortfall", None) is not None:
                reserve_shortfall_terminal = float(plan.reserve_shortfall[23])
            if getattr(plan, "reservation_target_wh", None) is not None:
                reservation_target_wh_terminal = float(plan.reservation_target_wh[23])
            if getattr(plan, "outlook_triggered_flag", None) is not None:
                outlook_triggered = bool(plan.outlook_triggered_flag[23] >= 0.5)
        extended_outlook = step_ctx.get("extended_outlook")
        record = {
            "step": len(trace),
            "timestamp": current_state.timestamp,
            "route": step_ctx.get("route"),
            "solver": step_ctx.get("solver"),
            "fuel_before_l": step_ctx.get("fuel_before_l"),
            "fuel_after_l": state_after.diesel_fuel_remaining_liters,
            "soc_before_pct": step_ctx.get("soc_before_pct"),
            "soc_after_pct": state_after.battery_soc_pct,
            "forecast_outlook_lookahead_h": extended_outlook.get("lookahead_h") if extended_outlook else None,
            "forecast_outlook_projected_min_net_margin_wh": (
                extended_outlook.get("projected_min_net_renewable_margin_wh") if extended_outlook else None
            ),
            "forecast_outlook_confidence": extended_outlook.get("confidence") if extended_outlook else None,
            "reservation_target_wh": reservation_target_wh_terminal,
            "outlook_triggered": outlook_triggered,
            "plan_reserve_shortfall_terminal": reserve_shortfall_terminal,
            "plan_solar_used_h1_w": float(plan.solar_used[0]) if plan else None,
            "plan_wind_used_h1_w": float(plan.wind_used[0]) if plan else None,
            "plan_battery_charge_h1_w": float(plan.battery_charge[0]) if plan else None,
            "plan_battery_discharge_h1_w": float(plan.battery_discharge[0]) if plan else None,
            "plan_diesel_power_h1_w": float(plan.diesel_power[0]) if plan else None,
            "plan_renewable_curtailment_h1_w": float(plan.renewable_curtailment[0]) if plan else None,
            "plan_unmet_load_h1_w": float(plan.unmet_load[0]) if plan else None,
        }
        trace.append(record)
        step_ctx.clear()
        return state_after

    runner.simulator.step = wrapped_step

    return runner, trace


def summarize(trace: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_unmet_wh = sum((r["plan_unmet_load_h1_w"] or 0.0) for r in trace)
    steps_119_121_unmet_wh = sum(
        (r["plan_unmet_load_h1_w"] or 0.0) for r in trace if 119 <= r["step"] <= 121
    )
    unmet_steps = [r["step"] for r in trace if (r["plan_unmet_load_h1_w"] or 0.0) > 1e-6]
    fuel_zero_step = next((r["step"] for r in trace if (r["fuel_after_l"] or 0.0) <= 1e-6), None)
    last_normal_step = max((r["step"] for r in trace if r["route"] == "NORMAL"), default=None)
    outlook_triggered_steps = [r["step"] for r in trace if r.get("outlook_triggered") is True]
    outlook_triggered_normal_route_steps = [
        r["step"] for r in trace if r.get("outlook_triggered") is True and r["route"] == "NORMAL"
    ]
    nonzero_reserve_shortfall_steps = [
        r["step"] for r in trace
        if (r["plan_reserve_shortfall_terminal"] or 0.0) > 1e-6 and r["route"] == "NORMAL"
    ]
    total_reserve_shortfall = sum(
        (r["plan_reserve_shortfall_terminal"] or 0.0) for r in trace if r["route"] == "NORMAL"
    )
    return {
        "total_unmet_load_wh": round(total_unmet_wh, 2),
        "total_unmet_load_kwh": round(total_unmet_wh / 1000.0, 4),
        "steps_119_121_unmet_wh": round(steps_119_121_unmet_wh, 2),
        "steps_119_121_unmet_kwh": round(steps_119_121_unmet_wh / 1000.0, 4),
        "all_unmet_steps": unmet_steps,
        "first_literal_fuel_exhaustion_step": fuel_zero_step,
        "last_normal_milp_step": last_normal_step,
        "outlook_triggered_steps_any_route": outlook_triggered_steps,
        "outlook_triggered_steps_normal_route_only": outlook_triggered_normal_route_steps,
        "normal_route_steps_with_nonzero_reserve_shortfall": nonzero_reserve_shortfall_steps,
        "cumulative_reserve_shortfall_wh_normal_route_only": round(total_reserve_shortfall, 2),
    }


def main() -> None:
    pre_hashes = build_hash_manifest()

    import time

    t0 = time.monotonic()
    runner_b, trace_b = build_instrumented_runner(mode="baseline")
    report_b = runner_b.run_pipeline(steps_to_run=168)
    t1 = time.monotonic()
    summary_b = summarize(trace_b)

    runner_o, trace_o = build_instrumented_runner(mode="outlook")
    t2 = time.monotonic()
    report_o = runner_o.run_pipeline(steps_to_run=168)
    t3 = time.monotonic()
    summary_o = summarize(trace_o)

    post_hashes = build_hash_manifest()
    protected_hash_diffs = {
        k: (pre_hashes[k], post_hashes[k]) for k in PROTECTED_HASH_TARGETS if pre_hashes[k] != post_hashes[k]
    }

    ems_b = report_b["ems_evaluation"]
    ems_o = report_o["ems_evaluation"]

    comparison = {
        "baseline": summary_b,
        "outlook": summary_o,
        "steps_119_121_unmet_kwh_delta": round(
            summary_o["steps_119_121_unmet_kwh"] - summary_b["steps_119_121_unmet_kwh"], 4
        ),
        "total_unmet_load_kwh_delta": round(
            summary_o["total_unmet_load_kwh"] - summary_b["total_unmet_load_kwh"], 4
        ),
        "shortfall_119_121_eliminated": summary_o["steps_119_121_unmet_kwh"] <= 1e-6,
        "shortfall_119_121_reduced_but_not_eliminated": (
            0.0 < summary_o["steps_119_121_unmet_kwh"] < summary_b["steps_119_121_unmet_kwh"]
        ),
        "baseline_total_diesel_fuel_liters": ems_b.get("total_diesel_fuel_liters"),
        "outlook_total_diesel_fuel_liters": ems_o.get("total_diesel_fuel_liters"),
        "baseline_renewable_utilization_pct": ems_b.get("renewable_utilization_pct"),
        "outlook_renewable_utilization_pct": ems_o.get("renewable_utilization_pct"),
        "baseline_system_reliability_pct": ems_b.get("system_reliability_pct"),
        "outlook_system_reliability_pct": ems_o.get("system_reliability_pct"),
        "baseline_last_normal_milp_step": summary_b["last_normal_milp_step"],
        "outlook_last_normal_milp_step": summary_o["last_normal_milp_step"],
        "baseline_solve_wall_time_s": round(t1 - t0, 3),
        "outlook_solve_wall_time_s": round(t3 - t2, 3),
    }

    payload = {
        "scenario_filename": SCENARIO_FILENAME,
        "outlook_config_used": {
            "optimizer.reservation.outlook_trigger": True,
            "note": "Full on-disk system/config/optimizer.yaml reservation block (Stage 1 static knobs inert; Stage 2 outlook_trigger enabled) -- see payload hashes for exact file content.",
        },
        "comparison": comparison,
        "baseline_trace": trace_b,
        "outlook_trace": trace_o,
        "pre_execution_hash_manifest": pre_hashes,
        "post_execution_hash_manifest": post_hashes,
        "protected_hash_diffs_detected": protected_hash_diffs,
    }

    out_json = OUTPUT_DIR / "rt01_outlook_reservation_counterfactual_trace.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    print("=" * 80)
    print("POLARIS RT-01 STAGE 2 -- baseline-vs-outlook 168h forecast-outlook reservation counterfactual")
    print("=" * 80)
    print(json.dumps(comparison, indent=2))
    print(f"protected_hash_diffs_detected (should be empty): {protected_hash_diffs}")
    print(f"\nWrote: {out_json}")
    print("=" * 80)


if __name__ == "__main__":
    main()
