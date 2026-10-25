"""
Step-82 MILP diagnostic (read-only forensic tool).

Does NOT modify system/optimization/implementations/milp.py, the objective,
constraints, configs, or the scenario file. This script independently
replicates milp.py's exact matrix construction (read, not imported, since we
need the RAW pre-rounding scipy.optimize.milp() result, which milp.py itself
discards) so we can instrument the solve without touching production code.

All production classes used (LocalDataProvider, StationState, DispatchPlan,
LocalBaselineForecastEngine, DigitalTwinSimulator) are imported and called
read-only / as pure functions; none are modified.

Writes each diagnostic's result to disk immediately (atomic tmp->rename) as
soon as it completes, per the infrastructure requirement: no diagnostic is
held only in memory until the end.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import milp as scipy_milp, LinearConstraint, Bounds

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

import yaml

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.simulation.simulator import DigitalTwinSimulator

OUT_DIR = Path(__file__).resolve().parent
SYSTEM_DIR = PROJECT_ROOT / "system"
CONFIG_DIR = SYSTEM_DIR / "config"
SCENARIO_PATH = SYSTEM_DIR / "data" / "scenarios" / "synthetic_168h_endurance_scenario.json"
CANDIDATE2_DIR = PROJECT_ROOT / "forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION"
STEP_OF_INTEREST = 82


def atomic_write_json(path: Path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def write_progress(stage: str, detail: dict = None):
    progress_path = OUT_DIR / "PROGRESS.json"
    payload = {
        "stage": stage,
        "updated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "detail": detail or {},
    }
    atomic_write_json(progress_path, payload)
    print(f"[progress] {stage}: {detail}", flush=True)


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


def freeze_forecast_bundle_dict(bundle_dict: dict) -> dict:
    """Identical freezing method used by run_candidate2_frozen_forecast_ablation.py:
    indices 1..23 of point/lower/upper repeat the index-0 value; index 0 preserved."""
    d = json.loads(json.dumps(bundle_dict))
    for field in ("solar_irradiance", "solar_generation", "wind_generation", "demand"):
        for arr_name in ("point", "lower", "upper"):
            arr = d[field][arr_name]
            d[field][arr_name] = [arr[0]] + [arr[0]] * 23
    return d


def reconstruct_exact_state_entering_step(target_step: int, configs: dict, data_provider: LocalDataProvider):
    """
    Replays DigitalTwinSimulator.step() (unmodified production code) forward
    from the recorded exact initial state, using the EXACT recorded h1
    dispatch values (battery_charge[0], battery_discharge[0], diesel_power[0])
    from forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION/milp_frozen_forecast_full_result.json
    for steps 0..target_step-1, and the EXACT scenario ground-truth actuals
    (same actuals the real run used) at each step.

    This recovers the StationState entering `target_step` EXACTLY (bit-for-bit
    via the same production arithmetic/rounding), NOT approximately -- the
    only reason this replay is needed instead of reading the state directly
    is that the per_step checkpoint JSON only stores battery_soc_pct (2dp)
    and fuel_after_l (4dp), not the raw battery_energy_wh the MILP itself
    requires; replaying the trivial (non-MILP) energy arithmetic from the
    exact recorded charge/discharge values avoids introducing that rounding
    gap.
    """
    frozen_result = json.loads((CANDIDATE2_DIR / "milp_frozen_forecast_full_result.json").read_text())
    per_step = frozen_result["per_step"]
    assert len(per_step) >= target_step, f"Only {len(per_step)} recorded steps available, need {target_step}"

    simulator = DigitalTwinSimulator(configs)

    first_step = data_provider.timesteps[0]
    state = StationState(
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

    for step_idx in range(target_step):
        s = per_step[step_idx]
        future_actuals = data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
        next_actual = future_actuals[0]

        # Minimal valid DispatchPlan carrying only the recorded, exact h1
        # (index-0) dispatch values; DigitalTwinSimulator.step() only reads
        # index 0 of each array, so indices 1..23 are inert placeholders.
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[next_actual["timestamp"]] * 24,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[s["h1_battery_charge_w"]] + [0.0] * 23,
            battery_discharge=[s["h1_battery_discharge_w"]] + [0.0] * 23,
            battery_soc=[0.0] * 24,
            diesel_power=[s["h1_diesel_power_w"]] + [0.0] * 23,
            load_served=[0.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )
        state = simulator.step(state, plan, next_actual)

        # Sanity check: replayed state must match the recorded checkpoint exactly.
        recorded_soc = s["soc_after_pct"] if step_idx < len(per_step) else None
        if step_idx + 1 < len(per_step):
            expected_next_soc = per_step[step_idx + 1]["soc_before_pct"]
            if abs(state.battery_soc_pct - expected_next_soc) > 1e-6:
                raise RuntimeError(
                    f"Replay divergence at step {step_idx}: replayed soc_after={state.battery_soc_pct}, "
                    f"recorded soc_before(next)={expected_next_soc}"
                )

    return state


def build_milp_matrices(forecast_bundle_dict: dict, station_state: StationState, config: dict, tie_break_epsilon: float = 0.0):
    """
    Faithful, independent replica of system/optimization/implementations/milp.py's
    matrix construction (lines ~17-295 of that file), for diagnostic
    instrumentation only. production milp.py is NOT imported or modified here.

    tie_break_epsilon=0.0 reproduces the exact production w_t = gamma**t (gamma=1.0
    by default in these configs) weighting used in the real run. Diagnostic 4
    passes tie_break_epsilon=1e-9 to additionally apply w_t *= (1 - tie_break_epsilon*t)
    as an infinitesimal, diagnostic-only tie-break -- this does NOT alter any
    economic coefficient's value at t=0 and changes hour-23's weight by at most 2.3e-8
    (relative), solely to test whether breaking the exact tie between repeated
    hours collapses the branch-and-bound tree. This is never written back to
    milp.py and is not a production change.
    """
    bat_cfg = config.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
    eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
    max_p_chg = float(bat_cfg.get("max_charge_power_w", 50000.0))
    max_p_dis = float(bat_cfg.get("max_discharge_power_w", 50000.0))
    deg_penalty = float(bat_cfg.get("deg_penalty_per_wh", 0.00005))

    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)
    initial_e_wh = max(min_e_wh, min(max_e_wh, station_state.battery_energy_wh))

    diesel_cfg = config.get("diesel", {})
    min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
    max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
    base_fuel_l_h = float(diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0))
    marg_fuel_l_wh = float(diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025))
    fuel_cost_per_l = float(diesel_cfg.get("fuel_cost_per_l", 2.50))
    startup_cost = float(diesel_cfg.get("startup_cost", 15.0))
    initial_diesel_running = 1 if station_state.diesel_running else 0

    current_fuel_l = station_state.diesel_fuel_remaining_liters
    if current_fuel_l is None:
        current_fuel_l = float(diesel_cfg.get("initial_fuel_l", 100.0))

    loads_cfg = config.get("loads", {})
    unmet_penalty_per_wh = float(loads_cfg.get("critical_load", {}).get("unmet_penalty_per_wh", 10.0))
    curt_penalty_per_wh = float(config.get("optimizer", {}).get("weights", {}).get("renewable_curtailment_penalty", 0.001))

    deferrable_list = loads_cfg.get("deferrable_loads", [])
    has_flexible_load = len(deferrable_list) > 0
    flex_power_w = 0.0
    flex_total_wh = 0.0
    flex_start_h = 0
    flex_finish_h = 24
    if has_flexible_load:
        def_item = deferrable_list[0]
        flex_power_w = float(def_item.get("power_w", 10000.0))
        flex_duration_h = float(def_item.get("duration_hours", 4))
        flex_total_wh = flex_power_w * flex_duration_h
        flex_start_h = int(def_item.get("earliest_start_h", 8))
        flex_finish_h = int(def_item.get("latest_finish_h", 18))

    timestamps = forecast_bundle_dict["timestamps"]
    solar_gen = forecast_bundle_dict["solar_generation"]["point"]
    wind_gen = forecast_bundle_dict["wind_generation"]["point"]
    demand = forecast_bundle_dict["demand"]["point"]

    H = 24
    K = 15

    num_vars = H * K
    c = np.zeros(num_vars)
    integrality = np.zeros(num_vars, dtype=int)
    lb = np.zeros(num_vars)
    ub = np.zeros(num_vars)

    opt_cfg = config.get("optimizer", {})
    for t in range(H):
        base = t * K
        p_sol_max = max(0.0, solar_gen[t])
        p_wind_max = max(0.0, wind_gen[t])
        p_dem = max(0.0, demand[t])

        dt = float(opt_cfg.get("timestep_hours", 1.0))

        if "custom_weight_vector" in opt_cfg and opt_cfg["custom_weight_vector"] is not None:
            w_t = float(opt_cfg["custom_weight_vector"][t])
        elif opt_cfg.get("v4g_single_horizon_mode", False):
            t_target = int(opt_cfg.get("v4g_target_index", 13))
            w_target = float(opt_cfg.get("v4g_weight", 0.5133))
            w_t = w_target if t == t_target else 1.0
        else:
            gamma = float(opt_cfg.get("horizon_discount_factor_gamma", 1.0))
            w_t = gamma ** t

        if tie_break_epsilon != 0.0:
            w_t = w_t * (1.0 - tie_break_epsilon * t)

        c[base + 2] = curt_penalty_per_wh * dt * w_t
        c[base + 3] = curt_penalty_per_wh * dt * w_t
        c[base + 4] = deg_penalty * dt * w_t
        c[base + 5] = deg_penalty * dt * w_t
        c[base + 7] = fuel_cost_per_l * marg_fuel_l_wh * dt * w_t
        c[base + 9] = unmet_penalty_per_wh * dt
        c[base + 13] = fuel_cost_per_l * base_fuel_l_h * dt * w_t
        c[base + 14] = startup_cost * w_t

        lb[base + 0], ub[base + 0] = 0.0, p_sol_max
        lb[base + 1], ub[base + 1] = 0.0, p_wind_max
        lb[base + 2], ub[base + 2] = 0.0, p_sol_max
        lb[base + 3], ub[base + 3] = 0.0, p_wind_max
        lb[base + 4], ub[base + 4] = 0.0, max_p_chg
        lb[base + 5], ub[base + 5] = 0.0, max_p_dis
        lb[base + 6], ub[base + 6] = min_e_wh, max_e_wh
        lb[base + 7], ub[base + 7] = 0.0, max_diesel_w
        lb[base + 8], ub[base + 8] = 0.0, p_dem
        lb[base + 9], ub[base + 9] = 0.0, p_dem

        if has_flexible_load and flex_start_h <= t < flex_finish_h:
            lb[base + 10], ub[base + 10] = 0.0, flex_power_w
        else:
            lb[base + 10], ub[base + 10] = 0.0, 0.0

        lb[base + 11], ub[base + 11] = 0.0, 1.0
        lb[base + 12], ub[base + 12] = 0.0, 1.0
        lb[base + 13], ub[base + 13] = 0.0, 1.0
        lb[base + 14], ub[base + 14] = 0.0, 1.0

        integrality[base + 11] = 1
        integrality[base + 12] = 1
        integrality[base + 13] = 1
        integrality[base + 14] = 1

    A_rows = []
    lhs = []
    rhs = []

    for t in range(H):
        base = t * K
        p_sol_max = max(0.0, solar_gen[t])
        p_wind_max = max(0.0, wind_gen[t])
        p_dem = max(0.0, demand[t])

        row = np.zeros(num_vars); row[base + 0] = 1.0; row[base + 2] = 1.0
        A_rows.append(row); lhs.append(p_sol_max); rhs.append(p_sol_max)

        row = np.zeros(num_vars); row[base + 1] = 1.0; row[base + 3] = 1.0
        A_rows.append(row); lhs.append(p_wind_max); rhs.append(p_wind_max)

        row = np.zeros(num_vars)
        row[base + 0] = 1.0; row[base + 1] = 1.0; row[base + 5] = 1.0; row[base + 7] = 1.0
        row[base + 8] = -1.0; row[base + 4] = -1.0; row[base + 10] = -1.0
        A_rows.append(row); lhs.append(0.0); rhs.append(0.0)

        row = np.zeros(num_vars); row[base + 8] = 1.0; row[base + 9] = 1.0
        A_rows.append(row); lhs.append(p_dem); rhs.append(p_dem)

        row = np.zeros(num_vars); row[base + 4] = 1.0; row[base + 11] = -max_p_chg
        A_rows.append(row); lhs.append(-np.inf); rhs.append(0.0)

        row = np.zeros(num_vars); row[base + 5] = 1.0; row[base + 12] = -max_p_dis
        A_rows.append(row); lhs.append(-np.inf); rhs.append(0.0)

        row = np.zeros(num_vars); row[base + 11] = 1.0; row[base + 12] = 1.0
        A_rows.append(row); lhs.append(-np.inf); rhs.append(1.0)

        dt = float(opt_cfg.get("timestep_hours", 1.0))
        row = np.zeros(num_vars)
        row[base + 6] = 1.0
        if t == 0:
            row[base + 4] = -eta_chg * dt
            row[base + 5] = dt / eta_dis
            A_rows.append(row); lhs.append(initial_e_wh); rhs.append(initial_e_wh)
        else:
            prev_base = (t - 1) * K
            row[prev_base + 6] = -1.0
            row[base + 4] = -eta_chg * dt
            row[base + 5] = dt / eta_dis
            A_rows.append(row); lhs.append(0.0); rhs.append(0.0)

        row = np.zeros(num_vars); row[base + 7] = 1.0; row[base + 13] = -min_diesel_w
        A_rows.append(row); lhs.append(0.0); rhs.append(np.inf)

        row = np.zeros(num_vars); row[base + 7] = 1.0; row[base + 13] = -max_diesel_w
        A_rows.append(row); lhs.append(-np.inf); rhs.append(0.0)

        row = np.zeros(num_vars); row[base + 14] = 1.0; row[base + 13] = -1.0
        if t == 0:
            A_rows.append(row); lhs.append(-initial_diesel_running); rhs.append(np.inf)
        else:
            prev_base = (t - 1) * K
            row[prev_base + 13] = 1.0
            A_rows.append(row); lhs.append(0.0); rhs.append(np.inf)

    row = np.zeros(num_vars)
    dt = float(opt_cfg.get("timestep_hours", 1.0))
    for t in range(H):
        base = t * K
        row[base + 7] = marg_fuel_l_wh * dt
        row[base + 13] = base_fuel_l_h * dt
    A_rows.append(row); lhs.append(-np.inf); rhs.append(current_fuel_l)

    if has_flexible_load and flex_total_wh > 0:
        row = np.zeros(num_vars)
        for t in range(flex_start_h, flex_finish_h):
            base = t * K
            row[base + 10] = 1.0
        A_rows.append(row); lhs.append(flex_total_wh); rhs.append(flex_total_wh)

    A = np.array(A_rows)
    constraints = LinearConstraint(A, lhs, rhs)
    bounds = Bounds(lb, ub)

    meta = dict(
        H=H, K=K, max_p_chg=max_p_chg, max_p_dis=max_p_dis, min_diesel_w=min_diesel_w,
        max_diesel_w=max_diesel_w, current_fuel_l=current_fuel_l, initial_e_wh=initial_e_wh,
        min_e_wh=min_e_wh, max_e_wh=max_e_wh, capacity_wh=capacity_wh, eta_chg=eta_chg, eta_dis=eta_dis,
    )
    return c, integrality, bounds, constraints, meta


def extract_raw_vars(sol, meta):
    K = meta["K"]
    out = {"p_chg": [], "p_dis": [], "u_chg": [], "u_dis": [], "e_next": [], "p_diesel": [], "u_diesel": []}
    for t in range(meta["H"]):
        base = t * K
        out["p_chg"].append(float(sol[base + 4]))
        out["p_dis"].append(float(sol[base + 5]))
        out["e_next"].append(float(sol[base + 6]))
        out["p_diesel"].append(float(sol[base + 7]))
        out["u_chg"].append(float(sol[base + 11]))
        out["u_dis"].append(float(sol[base + 12]))
        out["u_diesel"].append(float(sol[base + 13]))
    return out


def main():
    write_progress("start")
    configs = load_configs()
    data_provider = LocalDataProvider(SCENARIO_PATH)
    forecast_engine = LocalBaselineForecastEngine(CONFIG_DIR / "solar_pv.yaml")

    write_progress("replaying_exact_state_0_to_82")
    exact_state_82 = reconstruct_exact_state_entering_step(STEP_OF_INTEREST, configs, data_provider)
    atomic_write_json(OUT_DIR / "00_exact_state_step82.json", exact_state_82.to_dict())
    write_progress("exact_state_reconstructed", exact_state_82.to_dict())

    runtime_context = data_provider.get_runtime_state(STEP_OF_INTEREST)
    real_bundle = forecast_engine.predict(exact_state_82, runtime_context)
    real_bundle_dict = real_bundle.to_dict()
    frozen_bundle_dict = freeze_forecast_bundle_dict(real_bundle_dict)
    atomic_write_json(OUT_DIR / "01_real_bundle_step82.json", real_bundle_dict)
    atomic_write_json(OUT_DIR / "02_frozen_bundle_step82.json", frozen_bundle_dict)
    write_progress("bundles_built")

    # ---------------- DIAGNOSTIC 1: exact step-82 solve, no options (matches production exactly) ----------------
    write_progress("diagnostic_1_solving")
    c, integrality, bounds, constraints, meta = build_milp_matrices(frozen_bundle_dict, exact_state_82, configs)
    t0 = time.perf_counter()
    res1 = scipy_milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)
    t1 = time.perf_counter()
    solve_time_ms = (t1 - t0) * 1000.0

    raw1 = extract_raw_vars(res1.x, meta) if res1.x is not None else None
    rounded_chg = [round(v, 2) for v in raw1["p_chg"]] if raw1 else None
    rounded_dis = [round(v, 2) for v in raw1["p_dis"]] if raw1 else None

    dispatch_plan_error = None
    if raw1 is not None:
        try:
            _ = DispatchPlan(
                schema_version="1.0.0",
                timestamps=frozen_bundle_dict["timestamps"],
                solar_used=[0.0] * 24,
                wind_used=[0.0] * 24,
                battery_charge=rounded_chg,
                battery_discharge=rounded_dis,
                battery_soc=[0.0] * 24,
                diesel_power=[max(0.0, round(v, 2)) for v in raw1["p_diesel"]],
                load_served=[0.0] * 24,
                flexible_load_schedule=[0.0] * 24,
                renewable_curtailment=[0.0] * 24,
                unmet_load=[0.0] * 24,
                objective_value=round(float(res1.fun), 2) if res1.fun is not None else 0.0,
                constraint_status="OPTIMAL",
                energy_balance_errors=[0.0] * 24,
            )
        except ValueError as e:
            dispatch_plan_error = str(e)

    diag1 = {
        "step": STEP_OF_INTEREST,
        "solve_time_ms": solve_time_ms,
        "res_status": int(res1.status),
        "res_success": bool(res1.success),
        "res_message": str(res1.message),
        "res_fun": float(res1.fun) if res1.fun is not None else None,
        "res_mip_gap": float(res1.mip_gap) if getattr(res1, "mip_gap", None) is not None else None,
        "res_mip_node_count": int(res1.mip_node_count) if getattr(res1, "mip_node_count", None) is not None else None,
        "res_mip_dual_bound": float(res1.mip_dual_bound) if getattr(res1, "mip_dual_bound", None) is not None else None,
        "raw_hour0": {
            "p_chg": raw1["p_chg"][0] if raw1 else None,
            "p_dis": raw1["p_dis"][0] if raw1 else None,
            "u_chg": raw1["u_chg"][0] if raw1 else None,
            "u_dis": raw1["u_dis"][0] if raw1 else None,
        } if raw1 else None,
        "raw_all_24h": raw1,
        "rounded_2dp_hour0": {
            "p_chg": rounded_chg[0] if rounded_chg else None,
            "p_dis": rounded_dis[0] if rounded_dis else None,
        } if raw1 else None,
        "rounded_2dp_all_24h": {"p_chg": rounded_chg, "p_dis": rounded_dis} if raw1 else None,
        "dispatch_plan_construction_error": dispatch_plan_error,
    }
    atomic_write_json(OUT_DIR / "DIAGNOSTIC_1_exact_solve.json", diag1)
    write_progress("diagnostic_1_complete", {"solve_time_ms": solve_time_ms, "status": diag1["res_status"], "dispatch_plan_error": dispatch_plan_error})

    # ---------------- DIAGNOSTIC 2: constraint residuals for hour 0 (only if diag1 produced a solution) ----------------
    if raw1 is not None:
        p_chg0 = raw1["p_chg"][0]
        p_dis0 = raw1["p_dis"][0]
        u_chg0 = raw1["u_chg"][0]
        u_dis0 = raw1["u_dis"][0]
        max_p_chg = meta["max_p_chg"]
        max_p_dis = meta["max_p_dis"]

        c5_lhs = p_chg0 - max_p_chg * u_chg0
        c6_lhs = p_dis0 - max_p_dis * u_dis0
        c7_lhs = u_chg0 + u_dis0

        diag2 = {
            "constraint_5_charge_bound": {"expr": "p_chg - max_p_chg*u_chg <= 0", "lhs": c5_lhs, "rhs": 0.0, "slack_rhs_minus_lhs": 0.0 - c5_lhs},
            "constraint_6_discharge_bound": {"expr": "p_dis - max_p_dis*u_dis <= 0", "lhs": c6_lhs, "rhs": 0.0, "slack_rhs_minus_lhs": 0.0 - c6_lhs},
            "constraint_7_exclusivity": {"expr": "u_chg + u_dis <= 1", "lhs": c7_lhs, "rhs": 1.0, "slack_rhs_minus_lhs": 1.0 - c7_lhs},
            "u_chg_raw": u_chg0,
            "u_chg_integrality_residual_from_0": u_chg0 - 0.0,
            "u_chg_integrality_residual_from_1": u_chg0 - 1.0,
            "u_dis_raw": u_dis0,
            "u_dis_integrality_residual_from_0": u_dis0 - 0.0,
            "u_dis_integrality_residual_from_1": u_dis0 - 1.0,
            "u_chg_bound_check": {"lb": 0.0, "ub": 1.0, "within_bounds": 0.0 <= u_chg0 <= 1.0},
            "u_dis_bound_check": {"lb": 0.0, "ub": 1.0, "within_bounds": 0.0 <= u_dis0 <= 1.0},
            "p_chg_bound_check": {"lb": 0.0, "ub": max_p_chg, "within_bounds": 0.0 <= p_chg0 <= max_p_chg},
            "p_dis_bound_check": {"lb": 0.0, "ub": max_p_dis, "within_bounds": 0.0 <= p_dis0 <= max_p_dis},
            "max_p_chg_coefficient": max_p_chg,
            "max_p_dis_coefficient": max_p_dis,
            "hypothesis_check_p_chg_equals_max_p_chg_times_u_chg": {
                "max_p_chg * u_chg_raw": max_p_chg * u_chg0,
                "actual_p_chg_raw": p_chg0,
                "difference": p_chg0 - (max_p_chg * u_chg0),
            },
        }
        atomic_write_json(OUT_DIR / "DIAGNOSTIC_2_constraint_residuals.json", diag2)
        write_progress("diagnostic_2_complete", diag2["hypothesis_check_p_chg_equals_max_p_chg_times_u_chg"])
    else:
        atomic_write_json(OUT_DIR / "DIAGNOSTIC_2_constraint_residuals.json", {"skipped": "Diagnostic 1 produced no solution (res.x is None)"})
        write_progress("diagnostic_2_skipped")

    # ---------------- DIAGNOSTIC 3: node-limit probe ----------------
    diag3_results = []
    if diag1["res_success"]:
        for node_limit in [100, 1000, 10000]:
            write_progress(f"diagnostic_3_node_limit_{node_limit}_solving")
            t0 = time.perf_counter()
            res_n = scipy_milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints,
                                options={"node_limit": node_limit})
            t1 = time.perf_counter()
            raw_n = extract_raw_vars(res_n.x, meta) if res_n.x is not None else None
            entry = {
                "node_limit": node_limit,
                "status": int(res_n.status),
                "success": bool(res_n.success),
                "message": str(res_n.message),
                "objective": float(res_n.fun) if res_n.fun is not None else None,
                "mip_gap": float(res_n.mip_gap) if getattr(res_n, "mip_gap", None) is not None else None,
                "mip_node_count": int(res_n.mip_node_count) if getattr(res_n, "mip_node_count", None) is not None else None,
                "mip_dual_bound": float(res_n.mip_dual_bound) if getattr(res_n, "mip_dual_bound", None) is not None else None,
                "solve_time_ms": (t1 - t0) * 1000.0,
                "raw_hour0": {
                    "p_chg": raw_n["p_chg"][0], "p_dis": raw_n["p_dis"][0],
                    "u_chg": raw_n["u_chg"][0], "u_dis": raw_n["u_dis"][0],
                } if raw_n else None,
            }
            diag3_results.append(entry)
            atomic_write_json(OUT_DIR / "DIAGNOSTIC_3_node_limit_probe.json", {"note": "NODE-LIMITED SOLUTIONS ARE NOT FINAL/OPTIMAL -- diagnostic only.", "results": diag3_results})
            write_progress(f"diagnostic_3_node_limit_{node_limit}_complete", {"solve_time_ms": entry["solve_time_ms"], "mip_gap": entry["mip_gap"]})
    else:
        atomic_write_json(OUT_DIR / "DIAGNOSTIC_3_node_limit_probe.json", {"skipped": "Diagnostic 1 did not succeed"})
        write_progress("diagnostic_3_skipped")

    # ---------------- DIAGNOSTIC 4: symmetry-breaking probe (diagnostic-only copy of the objective) ----------------
    write_progress("diagnostic_4_solving")
    c_tb, integrality_tb, bounds_tb, constraints_tb, meta_tb = build_milp_matrices(
        frozen_bundle_dict, exact_state_82, configs, tie_break_epsilon=1e-9
    )
    t0 = time.perf_counter()
    res4 = scipy_milp(c=c_tb, integrality=integrality_tb, bounds=bounds_tb, constraints=constraints_tb)
    t1 = time.perf_counter()
    raw4 = extract_raw_vars(res4.x, meta_tb) if res4.x is not None else None
    diag4 = {
        "note": "DIAGNOSTIC-ONLY objective copy with w_t *= (1 - 1e-9*t); NOT written back to production milp.py.",
        "tie_break_epsilon": 1e-9,
        "solve_time_ms": (t1 - t0) * 1000.0,
        "status": int(res4.status),
        "success": bool(res4.success),
        "message": str(res4.message),
        "objective": float(res4.fun) if res4.fun is not None else None,
        "mip_gap": float(res4.mip_gap) if getattr(res4, "mip_gap", None) is not None else None,
        "mip_node_count": int(res4.mip_node_count) if getattr(res4, "mip_node_count", None) is not None else None,
        "mip_dual_bound": float(res4.mip_dual_bound) if getattr(res4, "mip_dual_bound", None) is not None else None,
        "raw_hour0": {
            "p_chg": raw4["p_chg"][0], "p_dis": raw4["p_dis"][0],
            "u_chg": raw4["u_chg"][0], "u_dis": raw4["u_dis"][0],
        } if raw4 else None,
        "comparison_vs_diagnostic_1": {
            "diag1_solve_time_ms": solve_time_ms,
            "diag4_solve_time_ms": (t1 - t0) * 1000.0,
            "diag1_mip_node_count": diag1["res_mip_node_count"],
            "diag4_mip_node_count": (int(res4.mip_node_count) if getattr(res4, "mip_node_count", None) is not None else None),
        },
    }
    atomic_write_json(OUT_DIR / "DIAGNOSTIC_4_symmetry_breaking.json", diag4)
    write_progress("diagnostic_4_complete", diag4["comparison_vs_diagnostic_1"])

    write_progress("all_diagnostics_complete")
    print("DONE")


if __name__ == "__main__":
    main()
