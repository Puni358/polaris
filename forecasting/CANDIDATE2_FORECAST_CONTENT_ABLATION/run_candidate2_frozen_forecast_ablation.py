"""
Candidate 2: Forecast-Content Ablation.

Runs the existing (unmodified) MILP optimizer on the existing (unmodified) 168h
endurance scenario, initial state, configs, and physical constraints, but replaces
the 24h ForecastBundle content at every timestep with a FROZEN bundle: indices
1..23 of solar_irradiance / solar_generation / wind_generation / demand (point,
lower, upper) are overwritten to repeat the index-0 (t+1h, i.e. the first
dispatched/forecasted hour) value. Index 0 is left untouched, so the immediate
(h=1) forecast seen by the optimizer is byte-identical to the real-forecast run;
only the forecast SHAPE beyond h=1 is flattened.

No production code (system/*) is modified. This script only imports and calls
existing, unmodified components: LocalDataProvider, LocalBaselineForecastEngine,
LocalMILPEnergyOptimizer, DigitalTwinSimulator, EvaluationEngine, and the
ForecastBundle/StationState schemas (used only to read/validate, not to change
their class definitions).

ECD bypass: matches the existing FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL
methodology — EMSControlRouter / OptionDFallbackSolver are not invoked; the
optimizer is called directly every step (ecd_router_invocations = 0), identical
to how the existing MILP-real-forecast and Reactive baseline runs were produced.

Outputs (this directory):
  - milp_frozen_forecast_full_result.json   (full 168-step trajectory + post-hoc metrics)
  - run_metadata.json                        (provenance: code/config hashes, initial state)
  - objective_cost_comparison_three_way.json (fixed-weight objective cost: reactive / milp-real / milp-frozen)
  - CANDIDATE2_REPORT.md                     (answers to the requested report questions only)
"""
import copy
import hashlib
import json
import sys
import time
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

OUTPUT_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = PROJECT_ROOT / "system"
CONFIG_DIR = SYSTEM_DIR / "config"
SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"
EXISTING_PROTOCOL_DIR = PROJECT_ROOT / "ems/campaigns/FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL"
STEPS_TO_RUN = 168

FIXED_COST_WEIGHTS = {
    "curtailment_per_wh": 0.05,
    "battery_deg_per_wh": 0.00005,
    "diesel_marginal_per_wh": 0.000625,
    "diesel_base_per_hour": 12.5,
    "startup": 15.0,
    "unmet_per_wh": 10.0,
}


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def freeze_forecast_bundle(bundle: ForecastBundle) -> ForecastBundle:
    """
    Returns a new ForecastBundle where, for solar_irradiance, solar_generation,
    wind_generation and demand, indices 1..23 of point/lower/upper are overwritten
    to repeat the index-0 value. Index 0, timestamps, origin, and metadata are
    otherwise preserved (metadata gets one additive provenance key).
    """
    d = bundle.to_dict()
    for field in ("solar_irradiance", "solar_generation", "wind_generation", "demand"):
        for arr_name in ("point", "lower", "upper"):
            arr = d[field][arr_name]
            frozen_value = arr[0]
            d[field][arr_name] = [arr[0]] + [frozen_value] * 23

    d["metadata"] = dict(d["metadata"])
    d["metadata"]["forecast_ablation"] = {
        "candidate": "candidate_2_frozen_forecast_content",
        "method": "indices_1_23_repeat_index_0_value",
        "fields_frozen": ["solar_irradiance", "solar_generation", "wind_generation", "demand"],
        "index_0_preserved": True,
    }
    return ForecastBundle.from_dict(d)


def load_configs() -> dict:
    configs = {}
    for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
        cfg_file = CONFIG_DIR / f"{cfg_name}.yaml"
        if cfg_file.exists():
            with open(cfg_file, "r") as f:
                configs[cfg_name] = yaml.safe_load(f)
        else:
            configs[cfg_name] = {}
    return configs


def build_initial_state(data_provider: LocalDataProvider, configs: dict) -> StationState:
    first_step = data_provider.timesteps[0]
    return StationState(
        timestamp=first_step["timestamp"],
        battery_soc_pct=configs.get("battery", {}).get("initial_soc_pct", 50.0),
        battery_energy_wh=configs.get("battery", {}).get("capacity_wh", 200000.0)
        * (configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=first_step["actual_SW_IN"],
        last_observed_demand=first_step["actual_demand"],
        last_observed_wind_generation=first_step["actual_wind_generation"],
        diesel_fuel_remaining_liters=configs.get("diesel", {}).get("initial_fuel_l", 100.0),
    )


def run_milp_frozen_forecast(configs: dict, scenario_path: Path) -> dict:
    data_provider = LocalDataProvider(scenario_path)
    forecast_engine = LocalBaselineForecastEngine(CONFIG_DIR / "solar_pv.yaml")
    optimizer = LocalMILPEnergyOptimizer()
    simulator = DigitalTwinSimulator(configs)

    diesel_cfg = configs.get("diesel", {})
    base_fuel_lph = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marginal_fuel_lpwh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))

    current_state = build_initial_state(data_provider, configs)

    per_step = []
    dispatch_plans = []
    forecast_bundles = []
    actual_scenarios = []
    faults = []
    fuel_overshoot_events = []

    max_steps = min(STEPS_TO_RUN, data_provider.total_timesteps)

    for step_idx in range(max_steps):
        runtime_context = data_provider.get_runtime_state(step_idx)

        try:
            real_bundle = forecast_engine.predict(current_state, runtime_context)
            bundle = freeze_forecast_bundle(real_bundle)
        except Exception as e:
            faults.append({"step": step_idx, "fault_class": "INVALID_FORECAST_BUNDLE", "message": str(e)})
            break

        t0 = time.perf_counter()
        try:
            # ECD bypass: direct optimizer invocation every step (ecd_router_invocations = 0),
            # matching the existing FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL methodology.
            plan = optimizer.optimize(bundle, current_state, configs)
        except Exception as e:
            faults.append({"step": step_idx, "fault_class": "OPTIMIZATION_RUNTIME_FAILURE", "message": str(e)})
            break
        t1 = time.perf_counter()
        solve_time_ms = (t1 - t0) * 1000.0

        if plan.constraint_status and plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
            faults.append({"step": step_idx, "fault_class": "OPTIMIZATION_INFEASIBLE", "message": plan.constraint_status})
            break

        future_actuals = data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
        next_actual = future_actuals[0]

        state_before = current_state

        # Independent fuel-overshoot detection (mirrors DigitalTwinSimulator's internal
        # fuel arithmetic without modifying it) for provenance/audit parity with the
        # existing protocol's run_metadata fuel_overshoot_events field.
        p_diesel_h1 = plan.diesel_power[0]
        diesel_running_h1 = p_diesel_h1 > 0
        required_fuel = ((base_fuel_lph if diesel_running_h1 else 0.0) + (marginal_fuel_lpwh * p_diesel_h1)) * 1.0
        available_fuel = state_before.diesel_fuel_remaining_liters
        if available_fuel is None:
            available_fuel = 100.0
        if required_fuel > available_fuel + 1e-9:
            fuel_overshoot_events.append({
                "step": step_idx,
                "required_fuel_l": required_fuel,
                "available_fuel_l": available_fuel,
            })

        try:
            current_state = simulator.step(current_state, plan, next_actual)
        except Exception as e:
            faults.append({"step": step_idx, "fault_class": "FAILED_STATE_VIOLATION", "message": str(e)})
            break

        plan_dict = plan.to_dict()
        dispatch_plans.append(plan_dict)
        forecast_bundles.append(bundle.to_dict())
        actual_scenarios.append(future_actuals)

        per_step.append({
            "step": step_idx,
            "controller": "milp_frozen_forecast",
            "timestamp": state_before.timestamp,
            "constraint_status": plan.constraint_status,
            "solve_time_ms": solve_time_ms,
            "soc_before_pct": state_before.battery_soc_pct,
            "soc_after_pct": current_state.battery_soc_pct,
            "fuel_before_l": state_before.diesel_fuel_remaining_liters,
            "fuel_after_l": current_state.diesel_fuel_remaining_liters,
            "diesel_running_before": state_before.diesel_running,
            "diesel_running_after": current_state.diesel_running,
            "h1_diesel_power_w": plan.diesel_power[0],
            "h1_renewable_used_w": plan.solar_used[0] + plan.wind_used[0],
            "h1_curtailment_w": plan.renewable_curtailment[0],
            "h1_battery_charge_w": plan.battery_charge[0],
            "h1_battery_discharge_w": plan.battery_discharge[0],
            "h1_unmet_load_w": plan.unmet_load[0],
            "h1_served_load_w": plan.load_served[0],
            "h1_flex_w": plan.flexible_load_schedule[0],
        })

    ems_eval = EvaluationEngine.evaluate_ems_performance(dispatch_plans, configs) if dispatch_plans else {}
    forecast_eval = EvaluationEngine.evaluate_forecasts(forecast_bundles, actual_scenarios) if forecast_bundles else {}

    return {
        "controller": "milp_frozen_forecast",
        "requested_steps": max_steps,
        "completed_steps": len(per_step),
        "faults": faults,
        "ecd_router_invocations": 0,
        "fuel_overshoot_events": fuel_overshoot_events,
        "ems_evaluation": ems_eval,
        "forecast_evaluation": forecast_eval,
        "per_step": per_step,
    }


def compute_fixed_weight_objective_cost(per_step: list, weights: dict) -> dict:
    """
    Post-hoc, fixed-weight objective cost recomputed identically across controllers
    from each run's committed (h=1) trajectory, independent of each optimizer's own
    internal objective formulation. Mirrors the methodology already used in the
    existing objective_cost_comparison.json for the real-forecast MILP vs Reactive run.
    """
    curt_wh = 0.0
    deg_chg_wh = 0.0
    deg_dis_wh = 0.0
    diesel_marg_wh = 0.0
    diesel_base_hours = 0
    unmet_wh = 0.0
    diesel_starts = 0
    was_running = False

    for s in per_step:
        curt_wh += s["h1_curtailment_w"]
        deg_chg_wh += s["h1_battery_charge_w"]
        deg_dis_wh += s["h1_battery_discharge_w"]
        unmet_wh += s["h1_unmet_load_w"]
        running = s["h1_diesel_power_w"] > 0
        if running:
            diesel_marg_wh += s["h1_diesel_power_w"]
            diesel_base_hours += 1
            if not was_running:
                diesel_starts += 1
        was_running = running

    breakdown = {
        "curtailment": curt_wh * weights["curtailment_per_wh"],
        "battery_deg_charge": deg_chg_wh * weights["battery_deg_per_wh"],
        "battery_deg_discharge": deg_dis_wh * weights["battery_deg_per_wh"],
        "diesel_marginal": diesel_marg_wh * weights["diesel_marginal_per_wh"],
        "diesel_base": diesel_base_hours * weights["diesel_base_per_hour"],
        "diesel_startup": diesel_starts * weights["startup"],
        "unmet_load": unmet_wh * weights["unmet_per_wh"],
    }
    total = sum(breakdown.values())
    return {"breakdown": breakdown, "total": total, "diesel_starts": diesel_starts}


def main():
    configs = load_configs()
    scenario_path = SYSTEM_DIR / "data" / "scenarios" / SCENARIO_FILENAME

    print(f"[Candidate 2] Running MILP + frozen forecast over {STEPS_TO_RUN}h scenario...")
    frozen_result = run_milp_frozen_forecast(configs, scenario_path)

    with open(OUTPUT_DIR / "milp_frozen_forecast_full_result.json", "w") as f:
        json.dump(frozen_result, f, indent=2)

    # Load existing (unmodified) Candidate 1 results for comparison.
    existing_milp_path = EXISTING_PROTOCOL_DIR / "milp_full_result.json"
    existing_reactive_path = EXISTING_PROTOCOL_DIR / "reactive_hybrid_a2_full_result.json"
    existing_milp = json.loads(existing_milp_path.read_text()) if existing_milp_path.exists() else None
    existing_reactive = json.loads(existing_reactive_path.read_text()) if existing_reactive_path.exists() else None

    # Fixed-weight objective cost, recomputed identically for all three trajectories.
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

    # Provenance / hashes.
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
        "run_candidate2_frozen_forecast_ablation.py": sha256_file(Path(__file__).resolve()),
    }

    data_provider = LocalDataProvider(scenario_path)
    initial_state = build_initial_state(data_provider, configs)

    run_metadata = {
        "protocol": "CANDIDATE2_FORECAST_CONTENT_ABLATION",
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

    print("[Candidate 2] Done.")
    print(f"  completed_steps: {frozen_result['completed_steps']}/{frozen_result['requested_steps']}")
    print(f"  faults: {len(frozen_result['faults'])}")
    print(f"  fuel_overshoot_events: {len(frozen_result['fuel_overshoot_events'])}")


if __name__ == "__main__":
    main()
