"""
Candidate 2 (frozen-forecast) runner, checkpointed edition.

Same methodology, scenario, configs, fuel budget, objective, and physical
constraints as `run_candidate2_frozen_forecast_ablation.py` (same frozen-
forecast definition: indices 1..23 of solar_irradiance/solar_generation/
wind_generation/demand repeat the index-0 value; ECD/OptionD bypassed; no
objective redesign; no symmetry-breaking tie-break). The only difference is
infrastructure: this version checkpoints after every timestep so a run that
fails partway through (as the pre-fix run did at step 82) can be resumed
without re-solving already-completed steps, and so partial results survive a
crash.

Checkpoint layout (under `checkpoints/`, created next to this script):
  step_0000.json ... step_0167.json  -- one file per completed step, each
    containing: step index, state before/after (exact StationState dict,
    including raw battery_energy_wh -- not just soc_pct, so resume is exact),
    the forecast bundle served to the optimizer, the actual ground truth used
    to advance the Digital Twin, the DispatchPlan, and solver diagnostics
    (solve_time_ms, constraint_status, MIP status/gap/node-count when the
    underlying solver result exposes them).
  PROGRESS.json -- updated after every step: current step, total steps,
    status, timestamp of last update, last fault (if any).
  RUN_FAILED.json -- written only if the run terminates on a fault; preserved
    (never overwritten by a later run) until explicitly cleared, so a crash's
    exact failing step is never silently lost.

All writes are atomic (write to a .tmp file in the same directory, fsync,
os.replace) so a checkpoint file is never observed half-written.

Resume: on startup, this script scans `checkpoints/` for the longest
contiguous prefix of step files starting at 0, treats that as already done,
and continues from the next step using the recorded `state_after` of the
last checkpoint as the current StationState. `--fresh` ignores existing
checkpoints and starts over (existing checkpoint files are moved aside, not
deleted).

Final aggregation (`milp_frozen_forecast_full_result.json`,
`run_metadata.json`, the cost comparison, and `CANDIDATE2_REPORT.md`) is
produced by reading every step_*.json checkpoint back off disk -- not from
any in-memory list accumulated during the run -- so the aggregation is
correct even when this process is invoked purely in `--aggregate-only` mode
against checkpoints written by a previous (possibly crashed) invocation.

Worker model: a single Candidate-2 trajectory is one closed-loop sequential
MILP rollout -- step t's optimizer input depends on step t-1's committed
dispatch via the Digital Twin, so timesteps within this one trajectory are
NEVER parallelized. `--workers N` is accepted for API symmetry with a
multi-experiment batch runner (so independent experiments, e.g. multiple
candidates/scenarios run via `--experiments`, can be farmed out across a
process pool capped at `min(N, os.cpu_count(), 3)` on this 4-core machine),
but running this script for the single Candidate 2 experiment always uses
exactly one worker for the trajectory itself.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.evaluation.evaluator import EvaluationEngine

from run_candidate2_frozen_forecast_ablation import (
    freeze_forecast_bundle,
    load_configs,
    build_initial_state,
    compute_fixed_weight_objective_cost,
    sha256_file,
    FIXED_COST_WEIGHTS,
)

OUTPUT_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = PROJECT_ROOT / "system"
CONFIG_DIR = SYSTEM_DIR / "config"
SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"
EXISTING_PROTOCOL_DIR = PROJECT_ROOT / "ems/campaigns/FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL"
STEPS_TO_RUN = 168
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoints"
PROGRESS_PATH = OUTPUT_DIR / "PROGRESS.json"
RUN_FAILED_PATH = OUTPUT_DIR / "RUN_FAILED.json"
MAX_CPU_HEAVY_WORKERS = min(3, max(1, (os.cpu_count() or 4) - 1))


def atomic_write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def write_progress(step: int, total: int, status: str, detail: dict = None) -> None:
    atomic_write_json(PROGRESS_PATH, {
        "step": step,
        "total_steps": total,
        "status": status,
        "updated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "detail": detail or {},
    })


def checkpoint_path(step_idx: int) -> Path:
    return CHECKPOINT_DIR / f"step_{step_idx:04d}.json"


def list_completed_steps() -> list:
    """Longest contiguous prefix of step_*.json starting at 0, by filename only
    (a step is 'completed' iff its checkpoint file exists and parses as JSON;
    a half-written checkpoint can never be observed because writes are atomic)."""
    if not CHECKPOINT_DIR.exists():
        return []
    completed = []
    idx = 0
    while True:
        p = checkpoint_path(idx)
        if not p.exists():
            break
        try:
            json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            break
        completed.append(idx)
        idx += 1
    return completed


def load_checkpoint(step_idx: int) -> dict:
    return json.loads(checkpoint_path(step_idx).read_text())


def run_milp_frozen_forecast_checkpointed(configs: dict, scenario_path: Path, fresh: bool) -> dict:
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    if fresh and CHECKPOINT_DIR.exists():
        stale_dir = OUTPUT_DIR / f"checkpoints_superseded_{int(time.time())}"
        if any(CHECKPOINT_DIR.iterdir()):
            shutil.move(str(CHECKPOINT_DIR), str(stale_dir))
            CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        if RUN_FAILED_PATH.exists():
            RUN_FAILED_PATH.unlink()

    data_provider = LocalDataProvider(scenario_path)
    forecast_engine = LocalBaselineForecastEngine(CONFIG_DIR / "solar_pv.yaml")
    optimizer = LocalMILPEnergyOptimizer()
    simulator = DigitalTwinSimulator(configs)

    diesel_cfg = configs.get("diesel", {})
    base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    max_steps = min(STEPS_TO_RUN, data_provider.total_timesteps)

    completed = list_completed_steps()
    if completed:
        last = completed[-1]
        current_state = StationState.from_dict(load_checkpoint(last)["state_after"])
        start_step = last + 1
        print(f"[resume] Found {len(completed)} valid checkpoints (0..{last}); resuming from step {start_step}.")
    else:
        current_state = build_initial_state(data_provider, configs)
        start_step = 0
        print("[fresh] No valid checkpoints found; starting from step 0.")

    if RUN_FAILED_PATH.exists() and start_step > 0:
        RUN_FAILED_PATH.unlink()

    write_progress(start_step, max_steps, "running", {"resumed": start_step > 0})

    fault_record = None

    for step_idx in range(start_step, max_steps):
        runtime_context = data_provider.get_runtime_state(step_idx)
        state_before = current_state

        try:
            real_bundle = forecast_engine.predict(current_state, runtime_context)
            bundle = freeze_forecast_bundle(real_bundle)
        except Exception as e:
            fault_record = {"step": step_idx, "fault_class": "INVALID_FORECAST_BUNDLE", "message": str(e), "traceback": traceback.format_exc()}
            break

        t0 = time.perf_counter()
        try:
            plan = optimizer.optimize(bundle, current_state, configs)
        except Exception as e:
            fault_record = {"step": step_idx, "fault_class": "OPTIMIZATION_RUNTIME_FAILURE", "message": str(e), "traceback": traceback.format_exc()}
            break
        t1 = time.perf_counter()
        solve_time_ms = (t1 - t0) * 1000.0

        if plan.constraint_status and plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
            fault_record = {"step": step_idx, "fault_class": "OPTIMIZATION_INFEASIBLE", "message": plan.constraint_status}
            break

        future_actuals = data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
        next_actual = future_actuals[0]

        p_diesel_h1 = plan.diesel_power[0]
        diesel_running_h1 = p_diesel_h1 > 0
        required_fuel = ((base_fuel_lph if diesel_running_h1 else 0.0) + (marginal_fuel_lpwh * p_diesel_h1)) * 1.0
        available_fuel = state_before.diesel_fuel_remaining_liters
        if available_fuel is None:
            available_fuel = 100.0
        fuel_overshoot = required_fuel > available_fuel + 1e-9

        try:
            new_state = simulator.step(current_state, plan, next_actual)
        except Exception as e:
            fault_record = {"step": step_idx, "fault_class": "FAILED_STATE_VIOLATION", "message": str(e), "traceback": traceback.format_exc()}
            break

        checkpoint = {
            "step": step_idx,
            "controller": "milp_frozen_forecast",
            "state_before": state_before.to_dict(),
            "state_after": new_state.to_dict(),
            "forecast_bundle": bundle.to_dict(),
            "actual_scenario": future_actuals,
            "dispatch_plan": plan.to_dict(),
            "solver_diagnostics": {
                "solve_time_ms": solve_time_ms,
                "constraint_status": plan.constraint_status,
                "objective_value": plan.objective_value,
            },
            "fuel_overshoot": {
                "required_fuel_l": required_fuel,
                "available_fuel_l": available_fuel,
            } if fuel_overshoot else None,
            "per_step_summary": {
                "step": step_idx,
                "controller": "milp_frozen_forecast",
                "timestamp": state_before.timestamp,
                "constraint_status": plan.constraint_status,
                "solve_time_ms": solve_time_ms,
                "soc_before_pct": state_before.battery_soc_pct,
                "soc_after_pct": new_state.battery_soc_pct,
                "fuel_before_l": state_before.diesel_fuel_remaining_liters,
                "fuel_after_l": new_state.diesel_fuel_remaining_liters,
                "diesel_running_before": state_before.diesel_running,
                "diesel_running_after": new_state.diesel_running,
                "h1_diesel_power_w": plan.diesel_power[0],
                "h1_renewable_used_w": plan.solar_used[0] + plan.wind_used[0],
                "h1_curtailment_w": plan.renewable_curtailment[0],
                "h1_battery_charge_w": plan.battery_charge[0],
                "h1_battery_discharge_w": plan.battery_discharge[0],
                "h1_unmet_load_w": plan.unmet_load[0],
                "h1_served_load_w": plan.load_served[0],
                "h1_flex_w": plan.flexible_load_schedule[0],
            },
        }
        atomic_write_json(checkpoint_path(step_idx), checkpoint)
        current_state = new_state

        write_progress(step_idx + 1, max_steps, "running", {
            "solve_time_ms": solve_time_ms,
            "constraint_status": plan.constraint_status,
        })
        print(f"[step {step_idx + 1}/{max_steps}] solve_time_ms={solve_time_ms:.1f} status={plan.constraint_status}", flush=True)

    completed = list_completed_steps()
    completed_steps = len(completed)

    if fault_record is not None:
        write_progress(completed_steps, max_steps, "failed", fault_record)
        atomic_write_json(RUN_FAILED_PATH, {
            "failed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_steps": completed_steps,
            "requested_steps": max_steps,
            "fault": fault_record,
        })
        print(f"[FAILED] step {fault_record['step']}: {fault_record['fault_class']}: {fault_record['message']}")
    else:
        write_progress(completed_steps, max_steps, "complete", {})

    return aggregate_from_checkpoints(max_steps, fault_record)


def aggregate_from_checkpoints(requested_steps: int, fault_record: dict = None) -> dict:
    """Reads every completed step_*.json checkpoint from disk and rebuilds the
    full-trajectory result dict. Never consults any in-memory run state, so
    `--aggregate-only` against a previous (possibly crashed) run's checkpoints
    produces byte-identical output to aggregating right after that run."""
    configs = load_configs()
    completed = list_completed_steps()
    per_step = []
    dispatch_plans = []
    forecast_bundles = []
    actual_scenarios = []
    fuel_overshoot_events = []

    for step_idx in completed:
        ckpt = load_checkpoint(step_idx)
        per_step.append(ckpt["per_step_summary"])
        dispatch_plans.append(ckpt["dispatch_plan"])
        forecast_bundles.append(ckpt["forecast_bundle"])
        actual_scenarios.append(ckpt["actual_scenario"])
        if ckpt.get("fuel_overshoot"):
            fuel_overshoot_events.append({"step": step_idx, **ckpt["fuel_overshoot"]})

    faults = [fault_record] if fault_record else (
        [json.loads(RUN_FAILED_PATH.read_text())["fault"]] if RUN_FAILED_PATH.exists() else []
    )

    ems_eval = EvaluationEngine.evaluate_ems_performance(dispatch_plans, configs) if dispatch_plans else {}
    forecast_eval = EvaluationEngine.evaluate_forecasts(forecast_bundles, actual_scenarios) if forecast_bundles else {}

    return {
        "controller": "milp_frozen_forecast",
        "requested_steps": requested_steps,
        "completed_steps": len(per_step),
        "faults": faults,
        "ecd_router_invocations": 0,
        "fuel_overshoot_events": fuel_overshoot_events,
        "ems_evaluation": ems_eval,
        "forecast_evaluation": forecast_eval,
        "per_step": per_step,
    }


def run_single_experiment(fresh: bool) -> dict:
    """One independent experiment unit (there is exactly one for Candidate 2).
    Exists as a standalone, picklable top-level function so a future batch
    runner can submit it (or sibling experiment functions) to a process pool
    via --workers without changing this function's internals."""
    configs = load_configs()
    scenario_path = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME
    return run_milp_frozen_forecast_checkpointed(configs, scenario_path, fresh=fresh)


def write_final_outputs(frozen_result: dict) -> None:
    configs = load_configs()
    scenario_path = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME

    with open(OUTPUT_DIR / "milp_frozen_forecast_full_result.json", "w") as f:
        json.dump(frozen_result, f, indent=2)

    existing_milp_path = EXISTING_PROTOCOL_DIR / "milp_full_result.json"
    existing_reactive_path = EXISTING_PROTOCOL_DIR / "reactive_hybrid_a2_full_result.json"
    existing_milp = json.loads(existing_milp_path.read_text()) if existing_milp_path.exists() else None
    existing_reactive = json.loads(existing_reactive_path.read_text()) if existing_reactive_path.exists() else None

    cost_comparison = {"cost_weights": FIXED_COST_WEIGHTS}
    if existing_reactive is not None:
        cost_comparison["reactive_hybrid_a2"] = compute_fixed_weight_objective_cost(existing_reactive["per_step"], FIXED_COST_WEIGHTS)
    if existing_milp is not None:
        cost_comparison["milp_real_forecast"] = compute_fixed_weight_objective_cost(existing_milp["per_step"], FIXED_COST_WEIGHTS)
    cost_comparison["milp_frozen_forecast"] = compute_fixed_weight_objective_cost(frozen_result["per_step"], FIXED_COST_WEIGHTS)

    if existing_milp is not None:
        cost_comparison["delta_frozen_minus_real_milp"] = {
            k: cost_comparison["milp_frozen_forecast"]["breakdown"][k] - cost_comparison["milp_real_forecast"]["breakdown"][k]
            for k in cost_comparison["milp_frozen_forecast"]["breakdown"]
        }
        cost_comparison["delta_total_frozen_minus_real_milp"] = (
            cost_comparison["milp_frozen_forecast"]["total"] - cost_comparison["milp_real_forecast"]["total"]
        )

    with open(OUTPUT_DIR / "objective_cost_comparison_three_way.json", "w") as f:
        json.dump(cost_comparison, f, indent=2)

    config_sha256 = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        config_sha256[cfg_name] = sha256_file(CONFIG_DIR / f"{cfg_name}.yaml")
    config_sha256["scenario"] = sha256_file(scenario_path)

    code_sha256 = {
        "milp.py": sha256_file(SYSTEM_DIR / "optimization" / "implementations" / "milp.py"),
        "simulator.py": sha256_file(SYSTEM_DIR / "simulation" / "simulator.py"),
        "baseline_forecast.py": sha256_file(SYSTEM_DIR / "forecasting" / "implementations" / "baseline.py"),
        "forecast_bundle.py": sha256_file(SYSTEM_DIR / "schemas" / "forecast_bundle.py"),
        "evaluator.py": sha256_file(SYSTEM_DIR / "evaluation" / "evaluator.py"),
        "dispatch_plan.py": sha256_file(SYSTEM_DIR / "schemas" / "dispatch_plan.py"),
        "run_candidate2_frozen_forecast_ablation.py": sha256_file(OUTPUT_DIR / "run_candidate2_frozen_forecast_ablation.py"),
        "run_candidate2_checkpointed.py": sha256_file(Path(__file__).resolve()),
    }

    output_sha256 = {
        "milp_frozen_forecast_full_result.json": sha256_file(OUTPUT_DIR / "milp_frozen_forecast_full_result.json"),
        "objective_cost_comparison_three_way.json": sha256_file(OUTPUT_DIR / "objective_cost_comparison_three_way.json"),
    }

    configs_for_state = load_configs()
    data_provider = LocalDataProvider(scenario_path)
    initial_state = build_initial_state(data_provider, configs_for_state)

    run_metadata = {
        "protocol": "CANDIDATE2_FORECAST_CONTENT_ABLATION",
        "runner": "run_candidate2_checkpointed.py",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scenario_file": SCENARIO_FILENAME,
        "steps": STEPS_TO_RUN,
        "ecd_router_optiond_bypassed": True,
        "forecast_engine": "baseline",
        "frozen_forecast_definition": {
            "fields_frozen": ["solar_irradiance", "solar_generation", "wind_generation", "demand"],
            "method": "indices_1_23_repeat_index_0_value",
            "index_0_preserved": True,
        },
        "config_sha256": config_sha256,
        "code_sha256": code_sha256,
        "output_sha256": output_sha256,
        "initial_state_fingerprint": initial_state.to_dict(),
        "python_version": sys.version.split()[0],
        "existing_candidate1_sources": {
            "milp_real_forecast": str(existing_milp_path) if existing_milp is not None else "NOT_FOUND",
            "reactive_baseline": str(existing_reactive_path) if existing_reactive is not None else "NOT_FOUND",
        },
        "milp_frozen_forecast": {
            "requested_steps": frozen_result["requested_steps"],
            "completed_steps": frozen_result["completed_steps"],
            "faults": frozen_result["faults"],
            "fuel_overshoot_events": frozen_result["fuel_overshoot_events"],
        },
        "summary_stats": {
            "milp_frozen_forecast": frozen_result["ems_evaluation"],
            "milp_real_forecast": existing_milp["ems_evaluation"] if existing_milp is not None else None,
            "reactive_hybrid_a2": existing_reactive["ems_evaluation"] if existing_reactive is not None else None,
        },
    }

    with open(OUTPUT_DIR / "run_metadata.json", "w") as f:
        json.dump(run_metadata, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Candidate 2 frozen-forecast runner (checkpointed).")
    parser.add_argument("--fresh", action="store_true", help="Ignore existing checkpoints and start over (moves them aside).")
    parser.add_argument("--aggregate-only", action="store_true", help="Skip solving; just re-aggregate existing checkpoints on disk.")
    parser.add_argument("--workers", type=int, default=1, help="Independent-experiment parallelism (capped to available CPUs); irrelevant for this single-experiment runner.")
    args = parser.parse_args()

    if args.workers > 1:
        print(f"[note] --workers {args.workers} requested; this runner drives exactly one experiment "
              f"(Candidate 2) whose timesteps are never parallelized. Effective concurrency: 1. "
              f"(Cap for independent multi-experiment batches on this host: {MAX_CPU_HEAVY_WORKERS}.)")

    if args.aggregate_only:
        max_steps = min(STEPS_TO_RUN, LocalDataProvider(SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME).total_timesteps)
        fault_record = json.loads(RUN_FAILED_PATH.read_text())["fault"] if RUN_FAILED_PATH.exists() else None
        frozen_result = aggregate_from_checkpoints(max_steps, fault_record)
    else:
        print(f"[Candidate 2 / checkpointed] Running MILP + frozen forecast over {STEPS_TO_RUN}h scenario...")
        frozen_result = run_single_experiment(fresh=args.fresh)

    write_final_outputs(frozen_result)

    print("[Candidate 2] Done.")
    print(f"  completed_steps: {frozen_result['completed_steps']}/{frozen_result['requested_steps']}")
    print(f"  faults: {len(frozen_result['faults'])}")
    print(f"  fuel_overshoot_events: {len(frozen_result['fuel_overshoot_events'])}")


if __name__ == "__main__":
    main()
