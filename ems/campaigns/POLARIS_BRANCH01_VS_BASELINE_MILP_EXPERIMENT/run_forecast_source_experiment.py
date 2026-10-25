"""
Branch 01 Candidate A HGB Forecast vs Current Baseline Forecast -> identical MILP.

EXPERIMENT ARMS (two independent closed-loop trajectories, same scenario/initial
state/configs/optimizer/simulator; the ONLY intended difference is the solar
forecast source fed to the optimizer each step):

  A. "baseline"  : LocalBaselineForecastEngine supplies solar_irradiance,
                   solar_generation, wind_generation, demand -- all four fields,
                   unmodified, exactly as the existing FINAL_168H protocol used it.
  B. "branch01"  : Branch01ForecastEngine (frozen Candidate A HGB artifact, via
                   LocalProviderBranch01Adapter) supplies solar_irradiance /
                   solar_generation. wind_generation and demand are inherited
                   from a LocalBaselineForecastEngine call on the SAME StationState
                   (control_bundle inheritance), because Branch01 is a solar-only
                   model that structurally requires non-solar forecasts from a
                   "Control" source (system/forecasting/.../branch01_forecast_engine.py
                   already enforces this fail-closed). Using the same baseline engine
                   as that Control source in both arms keeps wind/demand forecasts
                   identical in both arms for identical state, so the solar forecast
                   source remains the only varying input to the optimizer.

Both arms reuse, completely unmodified:
  - LocalDataProvider, the same scenario file
  - the same config YAMLs (station/battery/diesel/solar_pv/loads/optimizer)
  - the same build_initial_state()/load_configs()/sha256_file()/
    compute_fixed_weight_objective_cost()/FIXED_COST_WEIGHTS imported directly
    from forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION/run_candidate2_frozen_forecast_ablation.py
    (proven code, not duplicated)
  - LocalMILPEnergyOptimizer, DigitalTwinSimulator, EvaluationEngine
  - direct controller calls only: EMSControlRouter / OptionDFallbackSolver
    (ECD / OptionD) are never imported or invoked by this module.

Checkpoint/resume (per arm, modeled directly on
forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION/run_candidate2_checkpointed.py):
  checkpoints_<arm>/step_0000.json ... -- one atomic file per completed step
    (state before/after, forecast bundle + forecast provenance, dispatch plan,
    solver diagnostics, a running trajectory hash chain).
  PROGRESS_<arm>.json -- updated after every step.
  RUN_FAILED_<arm>.json -- written only on an unrecoverable fault; never
    silently discarded.
  Resume: longest contiguous prefix of step_*.json starting at 0 is treated as
  already done; the run continues from the next step using the last
  checkpoint's exact state_after (not re-derived).

Worker rule: timesteps within one arm are a single closed-loop trajectory and
are NEVER parallelized (step t depends on step t-1's committed dispatch via
the Digital Twin). The two ARMS are mutually independent (arm B's state never
depends on arm A's state) and MAY be run in parallel -- `run_both_arms_parallel()`
uses a process pool capped at min(2, 8, os.cpu_count()).

STOP: this module provides infrastructure only. Nothing in this file is
invoked at import time; running `main()` with `--run` is required to execute
ANY MILP step, and this task intentionally does not do so.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CANDIDATE2_DIR = PROJECT_ROOT / "forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CANDIDATE2_DIR))

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.evaluation.evaluator import EvaluationEngine
from system.governance.model_reproducibility import ModelGovernanceError

from forecasting.solar_branch_01.implementation.branch01_forecast_engine import (
    Branch01ForecastEngine, FROZEN_MODEL_SHA256, FROZEN_RUN_ID,
)
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder
from forecasting.solar_branch_01.implementation.local_provider_adapter import LocalProviderBranch01Adapter

# Reuse proven code from Candidate 2 rather than re-implementing it.
from run_candidate2_frozen_forecast_ablation import (
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
STEPS_TO_RUN = 168
ARMS = ("baseline", "branch01")
MAX_CPU_HEAVY_WORKERS = min(2, 8, max(1, os.cpu_count() or 1))

ADAPTER_PY = PROJECT_ROOT / "forecasting/solar_branch_01/implementation/local_provider_adapter.py"
FMB_PY = PROJECT_ROOT / "forecasting/solar_branch_01/implementation/feature_matrix_builder.py"
B01_ENGINE_PY = PROJECT_ROOT / "forecasting/solar_branch_01/implementation/branch01_forecast_engine.py"
BASELINE_PY = SYSTEM_DIR / "forecasting/implementations/baseline.py"
MILP_PY = SYSTEM_DIR / "optimization/implementations/milp.py"
MODEL_PATH = PROJECT_ROOT / "artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib"
CLEARSKY_CSV = PROJECT_ROOT / "forecasting/clear_sky/nuolja_clearsky_2024.csv"
SITES_CSV = PROJECT_ROOT / "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"


# ---------------------------------------------------------------------------
# Atomic I/O helpers (identical pattern to run_candidate2_checkpointed.py)
# ---------------------------------------------------------------------------

def atomic_write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def checkpoint_dir_for(arm: str) -> Path:
    return OUTPUT_DIR / f"checkpoints_{arm}"


def progress_path_for(arm: str) -> Path:
    return OUTPUT_DIR / f"PROGRESS_{arm}.json"


def run_failed_path_for(arm: str) -> Path:
    return OUTPUT_DIR / f"RUN_FAILED_{arm}.json"


def checkpoint_path(arm: str, step_idx: int) -> Path:
    return checkpoint_dir_for(arm) / f"step_{step_idx:04d}.json"


def list_completed_steps(arm: str) -> list:
    """Longest contiguous prefix of step_*.json starting at 0 for this arm."""
    d = checkpoint_dir_for(arm)
    if not d.exists():
        return []
    completed = []
    idx = 0
    while True:
        p = checkpoint_path(arm, idx)
        if not p.exists():
            break
        try:
            json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            break
        completed.append(idx)
        idx += 1
    return completed


def load_checkpoint(arm: str, step_idx: int) -> dict:
    return json.loads(checkpoint_path(arm, step_idx).read_text())


def write_progress(arm: str, step: int, total: int, status: str, detail: dict = None) -> None:
    atomic_write_json(progress_path_for(arm), {
        "arm": arm,
        "step": step,
        "total_steps": total,
        "status": status,
        "updated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "detail": detail or {},
    })


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def next_trajectory_hash(prev_hash: str, step_core: dict) -> str:
    """Hash-chains checkpoints so tampering with, or silently dropping, a
    completed step is detectable: each step's hash depends on every prior
    step's hash plus this step's own core (state/forecast/plan) content."""
    payload = prev_hash + canonical_json(step_core)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# No-ECD/OptionD guarantee: this module must never import the router or the
# OptionD fallback solver. Checked both at runtime (here) and in tests (by
# source inspection of this file).
# ---------------------------------------------------------------------------
assert "system.control.router" not in sys.modules, "EMSControlRouter must not be imported by this experiment module."
assert "system.optimization.implementations.option_d" not in sys.modules, "OptionDFallbackSolver must not be imported by this experiment module."


# ---------------------------------------------------------------------------
# Forecast construction: the ONLY point where the two arms differ.
# ---------------------------------------------------------------------------

def get_forecast_bundle_for_arm(
    arm: str,
    current_state: StationState,
    runtime_context: dict,
    data_provider: LocalDataProvider,
    step_idx: int,
    baseline_engine: LocalBaselineForecastEngine,
    branch01_engine: "Branch01ForecastEngine | None",
    branch01_adapter: "LocalProviderBranch01Adapter | None",
):
    """
    Returns (ForecastBundle, forecast_provenance_dict).

    arm == "baseline": the engine's own unmodified bundle (solar + wind + demand).
    arm == "branch01": Branch01's solar forecast, with wind/demand inherited from
      a baseline-engine call on the identical current_state (used as the shared
      "Control" source for non-solar fields in both arms -- see module docstring).
      Raises ModelGovernanceError (not silently substituted) if feature
      construction or inference fails closed; the caller must treat this as a
      fault, exactly like any other fault class -- NEVER fall back to a
      baseline solar forecast mid-arm, which would mix forecast sources
      within a single arm's trajectory.
    """
    if arm == "baseline":
        bundle = baseline_engine.predict(current_state, runtime_context)
        provenance = {
            "forecast_source": "baseline",
            "solar_model_sha256": None,
            "solar_model_run_id": None,
            "non_solar_source": "baseline",
        }
        return bundle, provenance

    if arm == "branch01":
        control_bundle = baseline_engine.predict(current_state, runtime_context)

        ctx = dict(runtime_context)
        ctx["control_bundle"] = control_bundle
        ctx.update(branch01_adapter.build_runtime_context_entry(data_provider, step_idx))

        bundle = branch01_engine.predict(current_state, ctx)
        provenance = {
            "forecast_source": "branch01_candidate_a_hgb",
            "solar_model_sha256": bundle.metadata["model_sha256"],
            "solar_model_run_id": bundle.metadata["run_id"],
            "non_solar_source": "baseline_control_bundle_inherited",
            "feature_vector": ctx["feature_vector"],
            "feature_names": FeatureMatrixBuilder.ORDERED_FEATURE_NAMES,
        }
        return bundle, provenance

    raise ValueError(f"Unknown arm '{arm}'")


# ---------------------------------------------------------------------------
# Main per-arm checkpointed runner
# ---------------------------------------------------------------------------

def run_arm_checkpointed(
    arm: str,
    configs: dict,
    scenario_path: Path,
    fresh: bool,
    max_steps_override: int = None,
    optimizer=None,
) -> dict:
    """
    Runs one arm's closed-loop trajectory, checkpointing atomically after
    every completed step. `optimizer` is injectable (defaults to the real
    LocalMILPEnergyOptimizer) so tests can substitute a fast fake optimizer
    without touching any of the checkpoint/resume/fairness logic under test.
    """
    if arm not in ARMS:
        raise ValueError(f"Unknown arm '{arm}', expected one of {ARMS}")

    ckpt_dir = checkpoint_dir_for(arm)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    if fresh and any(ckpt_dir.iterdir()):
        stale_dir = OUTPUT_DIR / f"checkpoints_{arm}_superseded_{int(time.time())}"
        shutil.move(str(ckpt_dir), str(stale_dir))
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        if run_failed_path_for(arm).exists():
            run_failed_path_for(arm).unlink()

    data_provider = LocalDataProvider(scenario_path)
    baseline_engine = LocalBaselineForecastEngine(CONFIG_DIR / "solar_pv.yaml")
    branch01_engine = Branch01ForecastEngine(PROJECT_ROOT) if arm == "branch01" else None
    branch01_adapter = LocalProviderBranch01Adapter(PROJECT_ROOT) if arm == "branch01" else None
    optimizer = optimizer if optimizer is not None else LocalMILPEnergyOptimizer()
    simulator = DigitalTwinSimulator(configs)

    diesel_cfg = configs.get("diesel", {})
    base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    requested_steps = max_steps_override if max_steps_override is not None else STEPS_TO_RUN
    max_steps = min(requested_steps, data_provider.total_timesteps)

    completed = list_completed_steps(arm)
    if completed:
        last = completed[-1]
        last_ckpt = load_checkpoint(arm, last)
        current_state = StationState.from_dict(last_ckpt["state_after"])
        trajectory_hash = last_ckpt["trajectory_hash"]
        start_step = last + 1
        print(f"[{arm}][resume] {len(completed)} valid checkpoints (0..{last}); resuming from step {start_step}.")
    else:
        current_state = build_initial_state(data_provider, configs)
        trajectory_hash = "GENESIS"
        start_step = 0
        print(f"[{arm}][fresh] No valid checkpoints found; starting from step 0.")

    if run_failed_path_for(arm).exists() and start_step > 0:
        run_failed_path_for(arm).unlink()

    write_progress(arm, start_step, max_steps, "running", {"resumed": start_step > 0})

    fault_record = None

    for step_idx in range(start_step, max_steps):
        runtime_context = data_provider.get_runtime_state(step_idx)
        state_before = current_state

        try:
            bundle, forecast_provenance = get_forecast_bundle_for_arm(
                arm, current_state, runtime_context, data_provider, step_idx,
                baseline_engine, branch01_engine, branch01_adapter,
            )
        except ModelGovernanceError as e:
            fault_record = {"step": step_idx, "fault_class": "FORECAST_FAIL_CLOSED", "message": str(e), "traceback": traceback.format_exc()}
            break
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

        per_step_summary = {
            "step": step_idx,
            "arm": arm,
            "controller": "milp",
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
            "forecast_source": forecast_provenance["forecast_source"],
            "solar_model_sha256": forecast_provenance["solar_model_sha256"],
        }

        step_core_for_hash = {
            "step": step_idx,
            "state_before": state_before.to_dict(),
            "state_after": new_state.to_dict(),
            "forecast_bundle": bundle.to_dict(),
            "dispatch_plan": plan.to_dict(),
            "forecast_provenance": forecast_provenance,
        }
        trajectory_hash = next_trajectory_hash(trajectory_hash, step_core_for_hash)

        checkpoint = {
            "step": step_idx,
            "arm": arm,
            "state_before": state_before.to_dict(),
            "state_after": new_state.to_dict(),
            "forecast_bundle": bundle.to_dict(),
            "forecast_provenance": forecast_provenance,
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
            "trajectory_hash": trajectory_hash,
            "per_step_summary": per_step_summary,
        }
        atomic_write_json(checkpoint_path(arm, step_idx), checkpoint)
        current_state = new_state

        write_progress(arm, step_idx + 1, max_steps, "running", {
            "solve_time_ms": solve_time_ms,
            "constraint_status": plan.constraint_status,
            "forecast_source": forecast_provenance["forecast_source"],
        })
        print(f"[{arm}][step {step_idx + 1}/{max_steps}] solve_time_ms={solve_time_ms:.1f} "
              f"status={plan.constraint_status} source={forecast_provenance['forecast_source']}", flush=True)

    completed = list_completed_steps(arm)
    completed_steps = len(completed)

    if fault_record is not None:
        write_progress(arm, completed_steps, max_steps, "failed", fault_record)
        atomic_write_json(run_failed_path_for(arm), {
            "arm": arm,
            "failed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_steps": completed_steps,
            "requested_steps": max_steps,
            "fault": fault_record,
        })
        print(f"[{arm}][FAILED] step {fault_record['step']}: {fault_record['fault_class']}: {fault_record['message']}")
    else:
        write_progress(arm, completed_steps, max_steps, "complete", {})

    return aggregate_from_checkpoints(arm, max_steps, fault_record, configs)


# ---------------------------------------------------------------------------
# Aggregation: reads checkpoints back off disk (never in-memory run state).
# ---------------------------------------------------------------------------

def compute_soc_and_diesel_stats(per_step: list) -> dict:
    socs = [s["soc_after_pct"] for s in per_step]
    diesel_starts = 0
    was_running = False
    for s in per_step:
        running = s["h1_diesel_power_w"] > 0
        if running and not was_running:
            diesel_starts += 1
        was_running = running
    return {
        "soc_min_pct": min(socs) if socs else None,
        "soc_max_pct": max(socs) if socs else None,
        "soc_mean_pct": sum(socs) / len(socs) if socs else None,
        "diesel_starts": diesel_starts,
        "mean_solve_time_ms": sum(s["solve_time_ms"] for s in per_step) / len(per_step) if per_step else None,
        "max_solve_time_ms": max((s["solve_time_ms"] for s in per_step), default=None),
    }


def aggregate_from_checkpoints(arm: str, requested_steps: int, fault_record: dict, configs: dict) -> dict:
    completed = list_completed_steps(arm)
    per_step, dispatch_plans, forecast_bundles, actual_scenarios = [], [], [], []
    fuel_overshoot_events = []
    forecast_sources_seen = set()

    for step_idx in completed:
        ckpt = load_checkpoint(arm, step_idx)
        per_step.append(ckpt["per_step_summary"])
        dispatch_plans.append(ckpt["dispatch_plan"])
        forecast_bundles.append(ckpt["forecast_bundle"])
        actual_scenarios.append(ckpt["actual_scenario"])
        forecast_sources_seen.add(ckpt["forecast_provenance"]["forecast_source"])
        if ckpt.get("fuel_overshoot"):
            fuel_overshoot_events.append({"step": step_idx, **ckpt["fuel_overshoot"]})

    faults = [fault_record] if fault_record else (
        [json.loads(run_failed_path_for(arm).read_text())["fault"]] if run_failed_path_for(arm).exists() else []
    )

    ems_eval = EvaluationEngine.evaluate_ems_performance(dispatch_plans, configs) if dispatch_plans else {}
    forecast_eval = EvaluationEngine.evaluate_forecasts(forecast_bundles, actual_scenarios) if forecast_bundles else {}
    extra_stats = compute_soc_and_diesel_stats(per_step)
    cost = compute_fixed_weight_objective_cost(per_step, FIXED_COST_WEIGHTS) if per_step else None

    return {
        "arm": arm,
        "controller": "milp",
        "requested_steps": requested_steps,
        "completed_steps": len(per_step),
        "faults": faults,
        "ecd_router_invocations": 0,
        "optiond_fallback_invocations": 0,
        "fuel_overshoot_events": fuel_overshoot_events,
        "forecast_sources_seen_in_arm": sorted(forecast_sources_seen),
        "forecast_source_mixed_within_arm": len(forecast_sources_seen) > 1,
        "ems_evaluation": ems_eval,
        "forecast_evaluation": forecast_eval,
        "extra_stats": extra_stats,
        "fixed_weight_objective_cost": cost,
        "final_trajectory_hash": load_checkpoint(arm, completed[-1])["trajectory_hash"] if completed else "GENESIS",
        "per_step": per_step,
    }


# ---------------------------------------------------------------------------
# Provenance manifest
# ---------------------------------------------------------------------------

def build_provenance_manifest(configs: dict, scenario_path: Path) -> dict:
    config_sha256 = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        config_sha256[cfg_name] = sha256_file(CONFIG_DIR / f"{cfg_name}.yaml")
    config_sha256["scenario"] = sha256_file(scenario_path)

    code_sha256 = {
        "milp.py": sha256_file(MILP_PY),
        "simulator.py": sha256_file(SYSTEM_DIR / "simulation/simulator.py"),
        "baseline_forecast_engine.py": sha256_file(BASELINE_PY),
        "branch01_forecast_engine.py": sha256_file(B01_ENGINE_PY),
        "local_provider_adapter.py": sha256_file(ADAPTER_PY),
        "feature_matrix_builder.py": sha256_file(FMB_PY),
        "forecast_bundle.py": sha256_file(SYSTEM_DIR / "schemas/forecast_bundle.py"),
        "dispatch_plan.py": sha256_file(SYSTEM_DIR / "schemas/dispatch_plan.py"),
        "evaluator.py": sha256_file(SYSTEM_DIR / "evaluation/evaluator.py"),
        "run_forecast_source_experiment.py": sha256_file(Path(__file__).resolve()),
    }

    data_provider = LocalDataProvider(scenario_path)
    initial_state = build_initial_state(data_provider, configs)

    return {
        "scenario_sha256": config_sha256["scenario"],
        "config_sha256": config_sha256,
        "code_sha256": code_sha256,
        "branch01_model_run_id": FROZEN_RUN_ID,
        "branch01_model_sha256": FROZEN_MODEL_SHA256,
        "branch01_model_sha256_matches_disk": sha256_file(MODEL_PATH) == FROZEN_MODEL_SHA256,
        "raw_sites_csv_sha256": sha256_file(SITES_CSV),
        "canonical_clearsky_csv_sha256": sha256_file(CLEARSKY_CSV),
        "feature_contract": FeatureMatrixBuilder.ORDERED_FEATURE_NAMES,
        "feature_contract_version": "POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1/18_feature_v1",
        "initial_state_fingerprint": initial_state.to_dict(),
        "initial_state_sha256": hashlib.sha256(canonical_json(initial_state.to_dict()).encode()).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Entrypoints
# ---------------------------------------------------------------------------

def run_single_arm(arm: str, fresh: bool, max_steps_override: int = None) -> dict:
    configs = load_configs()
    scenario_path = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME
    return run_arm_checkpointed(arm, configs, scenario_path, fresh=fresh, max_steps_override=max_steps_override)


def run_both_arms_parallel(fresh: bool) -> dict:
    """Runs arm 'baseline' and arm 'branch01' concurrently (they are mutually
    independent trajectories). Each arm's own timesteps remain strictly
    sequential inside run_arm_checkpointed; only the two arms run concurrently."""
    with ProcessPoolExecutor(max_workers=MAX_CPU_HEAVY_WORKERS) as pool:
        futures = {arm: pool.submit(run_single_arm, arm, fresh) for arm in ARMS}
        return {arm: f.result() for arm, f in futures.items()}


def write_final_outputs(results: dict) -> None:
    configs = load_configs()
    scenario_path = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME

    for arm, result in results.items():
        with open(OUTPUT_DIR / f"result_{arm}.json", "w") as f:
            json.dump(result, f, indent=2)

    comparison = {"cost_weights": FIXED_COST_WEIGHTS}
    for arm, result in results.items():
        comparison[arm] = result.get("fixed_weight_objective_cost")
    if "baseline" in results and "branch01" in results and results["baseline"]["fixed_weight_objective_cost"] and results["branch01"]["fixed_weight_objective_cost"]:
        comparison["delta_branch01_minus_baseline"] = {
            k: results["branch01"]["fixed_weight_objective_cost"]["breakdown"][k] - results["baseline"]["fixed_weight_objective_cost"]["breakdown"][k]
            for k in results["branch01"]["fixed_weight_objective_cost"]["breakdown"]
        }
    with open(OUTPUT_DIR / "objective_cost_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

    manifest = build_provenance_manifest(configs, scenario_path)
    manifest.update({
        "protocol": "POLARIS_BRANCH01_VS_BASELINE_MILP_EXPERIMENT",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scenario_file": SCENARIO_FILENAME,
        "steps": STEPS_TO_RUN,
        "arms": list(results.keys()),
        "per_arm_summary": {
            arm: {
                "requested_steps": r["requested_steps"],
                "completed_steps": r["completed_steps"],
                "faults": r["faults"],
                "forecast_sources_seen_in_arm": r["forecast_sources_seen_in_arm"],
                "forecast_source_mixed_within_arm": r["forecast_source_mixed_within_arm"],
                "final_trajectory_hash": r["final_trajectory_hash"],
                "ems_evaluation": r["ems_evaluation"],
            }
            for arm, r in results.items()
        },
    })
    with open(OUTPUT_DIR / "run_metadata.json", "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Branch01-vs-Baseline forecast source -> MILP experiment.")
    parser.add_argument("--run", action="store_true", help="Required to actually execute any MILP step. Without it, nothing is solved.")
    parser.add_argument("--arm", choices=list(ARMS) + ["both"], default="both")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--parallel-arms", action="store_true", help=f"Run both arms concurrently (up to {MAX_CPU_HEAVY_WORKERS} workers); never parallelizes timesteps within an arm.")
    parser.add_argument("--max-steps", type=int, default=None, help="Override STEPS_TO_RUN (for smoke tests only).")
    args = parser.parse_args()

    if not args.run and not args.aggregate_only:
        print("Refusing to solve: pass --run to execute MILP steps, or --aggregate-only to "
              "re-aggregate existing checkpoints. (This task intentionally stops here.)")
        return

    if args.aggregate_only:
        configs = load_configs()
        arms = ARMS if args.arm == "both" else (args.arm,)
        results = {}
        for arm in arms:
            max_steps = min(args.max_steps or STEPS_TO_RUN, LocalDataProvider(SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME).total_timesteps)
            fault_record = json.loads(run_failed_path_for(arm).read_text())["fault"] if run_failed_path_for(arm).exists() else None
            results[arm] = aggregate_from_checkpoints(arm, max_steps, fault_record, configs)
    elif args.arm == "both" and args.parallel_arms:
        results = run_both_arms_parallel(fresh=args.fresh)
    elif args.arm == "both":
        results = {arm: run_single_arm(arm, fresh=args.fresh, max_steps_override=args.max_steps) for arm in ARMS}
    else:
        results = {args.arm: run_single_arm(args.arm, fresh=args.fresh, max_steps_override=args.max_steps)}

    write_final_outputs(results)
    for arm, r in results.items():
        print(f"[{arm}] completed_steps={r['completed_steps']}/{r['requested_steps']} faults={len(r['faults'])}")


if __name__ == "__main__":
    main()
