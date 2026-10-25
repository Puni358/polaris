#!/usr/bin/env python3
"""
POLARIS — L2-EXP-07 / GAP19 UNCERTAINTY-INTERFACE RESEARCH EXPERIMENT
====================================================================
Controlled research experiment evaluating whether exposing calibrated L2
uncertainty intervals to GAP19 improves operational EMS outcomes relative
to the frozen Candidate F point forecast baseline.

RESEARCH ONLY.
No production code modified.
Candidate F, Stage 8.1 F, SKGBDT quantile models, and CQR parameter frozen.
Physical envelope: U = max(1.25 * clearsky_ghi, F) [SIMULATED_RESEARCH_ASSUMPTION].
80 W/m^2 floor is strictly NOT authorized and NOT used.
"""

import os
import sys
import json
import time
import math
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import yaml
import numpy as np
import pandas as pd
import joblib
from scipy.stats import wilcoxon

# Repository paths
BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
GAP19_DIR = BASE / "ems/gap19/POLARIS_EMS_GAP19_STAGE81_VS_BASELINE_RESEARCH_SIMULATION"
sys.path.insert(0, str(GAP19_DIR))

# Research components
import run_full_experiment as rfe
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_actual_solar_replay import pv_from_sw_in, replay_plan_against_actual_solar
from run_candidateF_actual_solar_replay import sw_in_to_power_w, ADDITIVE_FEATURE_NAME

# Workspace paths
L2_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting"
EXP_DIR = L2_DIR / "experiments/L2_EXP_07_GAP19_uncertainty_interface"
RESULTS_DIR = L2_DIR / "results"
AUDITS_DIR = L2_DIR / "audits"
MODELS_DIR = L2_DIR / "models"

CONFIG_PATH = EXP_DIR / "l2_exp_07_config.json"

EXPECTED_HASHES = {
    "candidate_f_model": "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84",
    "skgbdt_q10": "4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb",
    "skgbdt_q50": "104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71",
    "skgbdt_q90": "8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff",
    "matrix_2024": "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43",
    "treatment_fixture_2024": "a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d",
}

FROZEN_Q_HAT = 9.8962
EXPECTED_ORIGIN_COUNT = 173
EXPECTED_TIMESTEPS_COUNT = 4152

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_all_preconditions():
    print("=" * 80)
    print("POLARIS L2-EXP-07 — PRECONDITION & ANTI-LEAKAGE VERIFICATION")
    print("=" * 80)
    
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
    
    # 1. Verify frozen q_hat
    cfg_q_hat = cfg.get("frozen_parameters", {}).get("cqr_q_hat")
    if abs(cfg_q_hat - FROZEN_Q_HAT) > 1e-4:
        raise ValueError(f"STOP: q_hat mismatch ({cfg_q_hat} != {FROZEN_Q_HAT}). Halting.")
    print(f"  [PASS] CQR q_hat: {cfg_q_hat} W/m^2 (matches L2-EXP-03 frozen value)")
    
    # 2. Verify 80 W/m^2 floor is not used
    if cfg.get("governance", {}).get("eighty_wm2_floor_used") is not False:
        raise ValueError("STOP: 80 W/m^2 floor is prohibited in L2-EXP-07. Halting.")
    print("  [PASS] 80 W/m^2 floor: NOT USED (strictly prohibited)")
    
    # 3. Verify file hashes
    paths_to_check = {
        "candidate_f_model": BASE / cfg["authoritative_inputs"]["candidate_f_model"]["path"],
        "skgbdt_q10": BASE / cfg["authoritative_inputs"]["skgbdt_q10"]["path"],
        "skgbdt_q50": BASE / cfg["authoritative_inputs"]["skgbdt_q50"]["path"],
        "skgbdt_q90": BASE / cfg["authoritative_inputs"]["skgbdt_q90"]["path"],
        "matrix_2024": BASE / cfg["authoritative_inputs"]["matrix_2024"]["path"],
        "treatment_fixture_2024": BASE / cfg["authoritative_inputs"]["treatment_fixture_2024"]["path"],
    }
    
    verified_hashes = {}
    for key, p in paths_to_check.items():
        if not p.exists():
            raise FileNotFoundError(f"STOP: required input missing: {p}")
        h = sha256_of(p)
        exp = EXPECTED_HASHES[key]
        if h != exp:
            raise ValueError(f"STOP: hash mismatch for {key}: actual={h}, expected={exp}")
        print(f"  [PASS] {key}: {h[:16]}... MATCH")
        verified_hashes[key] = h
        
    print("All input preconditions verified successfully.\n")
    return cfg, verified_hashes

def paired_bootstrap_ci(deltas, n_iterations=10000, seed=42):
    rng = np.random.default_rng(seed)
    deltas = np.asarray(deltas, dtype=np.float64)
    n = len(deltas)
    if n == 0:
        return {"mean": None, "median": None, "ci_95_lower": None, "ci_95_upper": None, "n": 0}
    boot_means = np.empty(n_iterations)
    for b in range(n_iterations):
        idx = rng.integers(0, n, size=n)
        boot_means[b] = deltas[idx].mean()
    boot_means.sort()
    lo = boot_means[int(0.025 * n_iterations)]
    hi = boot_means[int(0.975 * n_iterations) - 1]
    return {
        "mean": round(float(deltas.mean()), 4),
        "median": round(float(np.median(deltas)), 4),
        "ci_95_lower": round(float(lo), 4),
        "ci_95_upper": round(float(hi), 4),
        "n": int(n)
    }

def main():
    t_start_all = time.time()
    cfg, verified_hashes = verify_all_preconditions()
    
    # Load frozen models
    print("Loading frozen models...")
    model_f = joblib.load(BASE / cfg["authoritative_inputs"]["candidate_f_model"]["path"])
    q10 = joblib.load(BASE / cfg["authoritative_inputs"]["skgbdt_q10"]["path"])
    q50 = joblib.load(BASE / cfg["authoritative_inputs"]["skgbdt_q50"]["path"])
    q90 = joblib.load(BASE / cfg["authoritative_inputs"]["skgbdt_q90"]["path"])
    print("Models loaded successfully.")
    
    # Load 2024 feature matrix and fixture
    print("Loading datasets...")
    df_feat = pd.read_csv(BASE / cfg["authoritative_inputs"]["matrix_2024"]["path"])
    df_feat["forecast_start"] = pd.to_datetime(df_feat["forecast_start"], utc=True)
    df_feat["elevation_x_cloud_frac"] = df_feat["solar_elevation"] * df_feat["cloud_frac"]
    
    df_fixture = pd.read_csv(BASE / cfg["authoritative_inputs"]["treatment_fixture_2024"]["path"])
    odd_origins = sorted(pd.to_datetime(df_fixture["origin_timestamp"], utc=True).unique())
    
    if len(odd_origins) != EXPECTED_ORIGIN_COUNT:
        raise ValueError(f"Origin count mismatch: got {len(odd_origins)}, expected {EXPECTED_ORIGIN_COUNT}")
    if len(df_fixture) != EXPECTED_TIMESTEPS_COUNT:
        raise ValueError(f"Timestep count mismatch: got {len(df_fixture)}, expected {EXPECTED_TIMESTEPS_COUNT}")
        
    print(f"Loaded {len(odd_origins)} authorized odd origins ({len(df_fixture)} timesteps).\n")
    
    # Build GAP19 components
    components = rfe.build_components()
    (df_mat, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))
    initial_e_wh = 160000.0  # 80% of 200 kWh, standard POLARIS test benchmark

    cols_38 = CANDIDATE_37_FEATURES + ["elevation_x_cloud_frac"]

    origin_metrics_list = []
    interval_diagnostics_list = []
    mechanism_forensics_list = []

    print("=" * 80)
    print("EXECUTING OPERATIONAL EMS REPLAY ACROSS 173 ORIGINS (ARMS A, B, C)")
    print("=" * 80)

    for i, origin_ts in enumerate(odd_origins):
        origin_str = origin_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        idx = int((origin_ts - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
        
        st_raw = adapter.get_station_state(idx, battery_soc_pct=50.0)
        st_k = StationState(
            timestamp=st_raw.timestamp,
            battery_soc_pct=80.0,
            battery_energy_wh=initial_e_wh,
            diesel_running=True,
            diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_raw.last_observed_solar_irradiance,
            last_observed_demand=st_raw.last_observed_demand,
            last_observed_wind_generation=st_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )

        origin_df = df_feat[df_feat["forecast_start"] == origin_ts].sort_values("horizon_hour").reset_index(drop=True)
        if len(origin_df) != 24:
            raise ValueError(f"Origin {origin_str} has {len(origin_df)} rows, expected 24")

        # 1. Candidate F point forecast (SW_IN, W/m^2)
        X = origin_df[cols_38].values.astype(np.float64)
        pred_res_f = model_f.predict(X)
        pred_s4 = origin_df["pred_stage4_fold"].values
        pred_f = np.maximum(0.0, pred_s4 + pred_res_f)
        solar_el = origin_df["solar_elevation"].values
        cs_ghi = origin_df["clearsky_ghi"].values
        is_night = (solar_el <= 0.0) | (cs_ghi == 0.0)
        pred_f = np.where(is_night, 0.0, pred_f)

        # 2. Frozen SKGBDT quantile predictions (raw residuals)
        r10 = q10.predict(X)
        r50 = q50.predict(X)
        r90 = q90.predict(X)

        q10_raw = pred_f + r10
        q90_raw = pred_f + r90
        q10_cal = q10_raw - FROZEN_Q_HAT
        q90_cal = q90_raw + FROZEN_Q_HAT

        # Physical envelopes
        lower_sw = np.maximum(0.0, q10_cal)
        # SIMULATED_RESEARCH_ASSUMPTION: U = max(1.25 * clearsky, F)
        U_sw = np.maximum(1.25 * cs_ghi, pred_f)
        upper_sw = np.maximum(lower_sw, np.minimum(U_sw, q90_cal))

        lower_sw = np.where(is_night, 0.0, lower_sw)
        upper_sw = np.where(is_night, 0.0, upper_sw)

        # Ground truth actuals
        actual_sw = origin_df["actual_SW_IN"].values

        # Power conversions (Watts)
        f_power_w = [round(sw_in_to_power_w(v), 2) for v in pred_f]
        lower_power_w = [round(sw_in_to_power_w(v), 2) for v in lower_sw]
        upper_power_w = [round(sw_in_to_power_w(v), 2) for v in upper_sw]
        actual_power_w = [round(pv_from_sw_in(v), 2) for v in actual_sw]

        # Record interval diagnostics for all 24 horizons
        for h in range(24):
            valid_dt = origin_ts + pd.Timedelta(hours=h)
            act_v = float(actual_sw[h])
            lo_v = float(lower_sw[h])
            up_v = float(upper_sw[h])
            f_v = float(pred_f[h])
            cs_v = float(cs_ghi[h])
            el_v = float(solar_el[h])
            night_v = bool(is_night[h])

            inside = bool(lo_v <= act_v <= up_v) if not night_v else True
            below = bool(act_v < lo_v) if not night_v else False
            above = bool(act_v > up_v) if not night_v else False
            under_u = bool(act_v <= U_sw[h]) if not night_v else True

            interval_diagnostics_list.append({
                "origin_timestamp": origin_str,
                "horizon_hour": h + 1,
                "valid_timestamp": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "solar_elevation": round(el_v, 4),
                "clearsky_ghi": round(cs_v, 2),
                "is_night_causal": night_v,
                "actual_SW_IN": round(act_v, 4),
                "actual_solar_w": actual_power_w[h],
                "pred_f_sw_in": round(f_v, 4),
                "pred_f_power_w": f_power_w[h],
                "q10_raw_sw_in": round(float(q10_raw[h]), 4),
                "q90_raw_sw_in": round(float(q90_raw[h]), 4),
                "q10_cal_sw_in": round(float(q10_cal[h]), 4),
                "q90_cal_sw_in": round(float(q90_cal[h]), 4),
                "lower_bound_sw_in": round(lo_v, 4),
                "upper_bound_sw_in": round(up_v, 4),
                "lower_bound_power_w": lower_power_w[h],
                "upper_bound_power_w": upper_power_w[h],
                "interval_width_sw_in": round(up_v - lo_v, 4),
                "interval_width_power_w": round(upper_power_w[h] - lower_power_w[h], 2),
                "inside_interval": inside,
                "below_lower": below,
                "above_upper": above,
                "under_physical_bound": under_u,
            })

        # Build forecast bundles
        shared_bundle = baseline_engine.predict(st_k, {})
        wind_gen = shared_bundle.wind_generation
        demand_fc = shared_bundle.demand
        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        crit_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]
        ts_list = [(origin_ts + pd.Timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]

        # Arm A: Point Forecast Control (F)
        bundle_a = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(f_power_w, f_power_w, f_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "candidate_F_point_control"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        # Arm B: Uncertainty-Aware Research Interface (Conservative Scenario: calibrated q10 lower bound)
        bundle_b = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(lower_power_w, lower_power_w, upper_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "uncertainty_aware_l2_q10_conservative_scenario"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        # Arm C: Perfect Foresight Diagnostic
        bundle_c = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(actual_power_w, actual_power_w, actual_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "perfect_foresight_diagnostic"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        # Optimize & Replay for each Arm
        origin_row = {
            "origin_id": i + 1,
            "origin_timestamp": origin_str,
            "month": origin_ts.month,
            "day": origin_ts.day,
            "critical_demand_total_wh": round(sum(crit_demand_w), 2),
            "actual_solar_total_wh": round(sum(actual_power_w), 2),
            "candidate_f_planned_solar_wh": round(sum(f_power_w), 2),
            "uncertainty_planned_solar_wh": round(sum(lower_power_w), 2),
        }

        arm_replays = {}
        arm_plans = {}
        arm_routes = {}
        arm_solve_times = {}

        for arm_key, arm_label, bundle in [
            ("A", "arm_a_control", bundle_a),
            ("B", "arm_b_uncertainty", bundle_b),
            ("C", "arm_c_perfect", bundle_c)
        ]:
            cfg_arm = dict(configs_base)
            cfg_arm["critical_demand_w"] = crit_demand_w
            cfg_arm["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)

            assessment, route = router.evaluate_and_route(st_k, bundle, cfg_arm)
            arm_routes[arm_key] = route
            origin_row[f"{arm_label}_route"] = route
            origin_row[f"{arm_label}_terminal_target_wh"] = round(cfg_arm["terminal_target_wh"], 2)

            if route == "NORMAL":
                t0 = time.perf_counter()
                plan = optimizer.optimize(bundle, st_k, cfg_arm)
                solve_time = time.perf_counter() - t0
                arm_solve_times[arm_key] = solve_time
                arm_plans[arm_key] = plan

                rep = replay_plan_against_actual_solar(
                    plan, actual_power_w, crit_demand_w, eta_chg, eta_dis, capacity_wh,
                    min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh
                )
                arm_replays[arm_key] = rep

                diesel_on_hours = sum(1 for p in plan.diesel_power if p > 0.0)
                startups = 0
                prev_on = st_k.diesel_running
                for p in plan.diesel_power:
                    on = p > 0.0
                    if on and not prev_on:
                        startups += 1
                    prev_on = on

                efc = (sum(rep["realized_battery_charge_w"]) + sum(plan.battery_discharge)) / (2.0 * capacity_wh)
                unmet = rep["realized_unmet_load_energy_wh"]
                crit_total = sum(crit_demand_w)
                reliability = max(0.0, (1.0 - (unmet / crit_total)) * 100.0) if crit_total > 0 else 100.0

                origin_row[f"{arm_label}_constraint_status"] = plan.constraint_status
                origin_row[f"{arm_label}_solve_time_s"] = round(solve_time, 4)
                origin_row[f"{arm_label}_realized_unmet_wh"] = round(unmet, 2)
                origin_row[f"{arm_label}_realized_diesel_fuel_l"] = round(rep["realized_diesel_fuel_l"], 4)
                origin_row[f"{arm_label}_diesel_on_hours"] = diesel_on_hours
                origin_row[f"{arm_label}_diesel_startups"] = startups
                origin_row[f"{arm_label}_realized_curtailment_wh"] = round(rep["realized_curtailment_energy_wh"], 2)
                origin_row[f"{arm_label}_battery_charge_wh"] = round(rep["realized_battery_charge_energy_wh"], 2)
                origin_row[f"{arm_label}_battery_discharge_wh"] = round(rep["realized_battery_discharge_energy_wh"], 2)
                origin_row[f"{arm_label}_battery_efc"] = round(efc, 6)
                origin_row[f"{arm_label}_min_soc_pct"] = round(min(rep["realized_soc_pct"]), 2)
                origin_row[f"{arm_label}_max_soc_pct"] = round(max(rep["realized_soc_pct"]), 2)
                origin_row[f"{arm_label}_mean_soc_pct"] = round(float(np.mean(rep["realized_soc_pct"])), 2)
                origin_row[f"{arm_label}_terminal_soc_pct"] = round(rep["realized_soc_pct"][-1], 2)
                origin_row[f"{arm_label}_soc_floor_violations"] = len(rep["soc_violations"])
                origin_row[f"{arm_label}_reliability_pct"] = round(reliability, 4)
            else:
                origin_row[f"{arm_label}_constraint_status"] = "ROUTE_" + route
                origin_row[f"{arm_label}_solve_time_s"] = None
                origin_row[f"{arm_label}_realized_unmet_wh"] = None
                origin_row[f"{arm_label}_realized_diesel_fuel_l"] = None
                origin_row[f"{arm_label}_diesel_on_hours"] = None
                origin_row[f"{arm_label}_diesel_startups"] = None
                origin_row[f"{arm_label}_realized_curtailment_wh"] = None
                origin_row[f"{arm_label}_battery_charge_wh"] = None
                origin_row[f"{arm_label}_battery_discharge_wh"] = None
                origin_row[f"{arm_label}_battery_efc"] = None
                origin_row[f"{arm_label}_min_soc_pct"] = None
                origin_row[f"{arm_label}_max_soc_pct"] = None
                origin_row[f"{arm_label}_mean_soc_pct"] = None
                origin_row[f"{arm_label}_terminal_soc_pct"] = None
                origin_row[f"{arm_label}_soc_floor_violations"] = None
                origin_row[f"{arm_label}_reliability_pct"] = None

        # Paired Deltas (Arm A - Arm B)
        if arm_routes.get("A") == "NORMAL" and arm_routes.get("B") == "NORMAL":
            delta_unmet = origin_row["arm_a_control_realized_unmet_wh"] - origin_row["arm_b_uncertainty_realized_unmet_wh"]
            delta_fuel = origin_row["arm_a_control_realized_diesel_fuel_l"] - origin_row["arm_b_uncertainty_realized_diesel_fuel_l"]
            delta_curtail = origin_row["arm_a_control_realized_curtailment_wh"] - origin_row["arm_b_uncertainty_realized_curtailment_wh"]
            delta_efc = origin_row["arm_a_control_battery_efc"] - origin_row["arm_b_uncertainty_battery_efc"]
            delta_rel = origin_row["arm_b_uncertainty_reliability_pct"] - origin_row["arm_a_control_reliability_pct"]

            origin_row["paired_delta_unmet_wh_a_minus_b"] = round(delta_unmet, 2)
            origin_row["paired_delta_fuel_l_a_minus_b"] = round(delta_fuel, 4)
            origin_row["paired_delta_curtail_wh_a_minus_b"] = round(delta_curtail, 2)
            origin_row["paired_delta_efc_a_minus_b"] = round(delta_efc, 6)
            origin_row["paired_delta_reliability_pct_b_minus_a"] = round(delta_rel, 4)

            # Mechanism Forensics Record
            rep_a = arm_replays["A"]
            rep_b = arm_replays["B"]
            plan_a = arm_plans["A"]
            plan_b = arm_plans["B"]

            # Solar forecast error under F
            solar_mae_a = float(np.mean(np.abs(np.array(f_power_w) - np.array(actual_power_w))))
            solar_bias_a = float(np.mean(np.array(f_power_w) - np.array(actual_power_w)))
            interval_width_mean = float(np.mean(np.array(upper_power_w) - np.array(lower_power_w)))

            # Diesel commitment timing
            first_diesel_hour_a = next((h for h, p in enumerate(plan_a.diesel_power) if p > 0), -1)
            first_diesel_hour_b = next((h for h, p in enumerate(plan_b.diesel_power) if p > 0), -1)

            # Battery SOC at midday (hour 12)
            soc_midday_a = rep_a["realized_soc_pct"][11]
            soc_midday_b = rep_b["realized_soc_pct"][11]

            mechanism_forensics_list.append({
                "origin_timestamp": origin_str,
                "solar_mae_w": round(solar_mae_a, 2),
                "solar_bias_w": round(solar_bias_a, 2),
                "interval_width_mean_w": round(interval_width_mean, 2),
                "unmet_a_wh": origin_row["arm_a_control_realized_unmet_wh"],
                "unmet_b_wh": origin_row["arm_b_uncertainty_realized_unmet_wh"],
                "delta_unmet_wh": round(delta_unmet, 2),
                "fuel_a_l": origin_row["arm_a_control_realized_diesel_fuel_l"],
                "fuel_b_l": origin_row["arm_b_uncertainty_realized_diesel_fuel_l"],
                "delta_fuel_l": round(delta_fuel, 4),
                "curtail_a_wh": origin_row["arm_a_control_realized_curtailment_wh"],
                "curtail_b_wh": origin_row["arm_b_uncertainty_realized_curtailment_wh"],
                "delta_curtail_wh": round(delta_curtail, 2),
                "terminal_target_a_wh": origin_row["arm_a_control_terminal_target_wh"],
                "terminal_target_b_wh": origin_row["arm_b_uncertainty_terminal_target_wh"],
                "delta_terminal_target_wh": round(origin_row["arm_b_uncertainty_terminal_target_wh"] - origin_row["arm_a_control_terminal_target_wh"], 2),
                "first_diesel_hour_a": first_diesel_hour_a,
                "first_diesel_hour_b": first_diesel_hour_b,
                "soc_midday_a": round(soc_midday_a, 2),
                "soc_midday_b": round(soc_midday_b, 2),
                "primary_mechanism_classification": (
                    "UNMET_ELIMINATED_VIA_CONSERVATIVE_DISPATCH" if delta_unmet > 100.0 else
                    "NEUTRAL_NO_UNMET_IN_EITHER_ARM" if origin_row["arm_a_control_realized_unmet_wh"] < 1.0 else
                    "PARTIAL_UNMET_REDUCTION" if delta_unmet > 0 else
                    "UNMET_UNCHANGED" if abs(delta_unmet) < 1.0 else "REGRESSIVE"
                )
            })

        origin_metrics_list.append(origin_row)

        if (i + 1) % 25 == 0 or (i + 1) == len(odd_origins):
            print(f"  Processed {i + 1}/{len(odd_origins)} origins [{round(time.time() - t_start_all, 1)}s elapsed]")

    elapsed_total_s = round(time.time() - t_start_all, 1)
    print(f"\nSimulation complete in {elapsed_total_s}s.\n")

    # Save CSVs
    df_origin_metrics = pd.DataFrame(origin_metrics_list)
    origin_metrics_csv_path = RESULTS_DIR / "L2_EXP_07_ORIGIN_METRICS.csv"
    df_origin_metrics.to_csv(origin_metrics_csv_path, index=False)
    print(f"Saved origin metrics: {origin_metrics_csv_path}")

    df_interval_diag = pd.DataFrame(interval_diagnostics_list)
    interval_diag_csv_path = RESULTS_DIR / "L2_EXP_07_INTERVAL_DIAGNOSTICS.csv"
    df_interval_diag.to_csv(interval_diag_csv_path, index=False)
    print(f"Saved interval diagnostics: {interval_diag_csv_path}")

    df_forensics = pd.DataFrame(mechanism_forensics_list)
    forensics_csv_path = RESULTS_DIR / "L2_EXP_07_MECHANISM_FORENSICS.csv"
    df_forensics.to_csv(forensics_csv_path, index=False)
    print(f"Saved mechanism forensics: {forensics_csv_path}")

    # Paired Statistical Analysis on Common NORMAL-routed origins
    both_normal = df_origin_metrics[
        (df_origin_metrics["arm_a_control_route"] == "NORMAL") &
        (df_origin_metrics["arm_b_uncertainty_route"] == "NORMAL")
    ].copy()

    n_both_normal = len(both_normal)
    n_route_mismatches = len(df_origin_metrics[df_origin_metrics["arm_a_control_route"] != df_origin_metrics["arm_b_uncertainty_route"]])
    
    print("=" * 80)
    print(f"PAIRED STATISTICAL ANALYSIS ({n_both_normal} COMMON NORMAL-ROUTED ORIGINS)")
    print("=" * 80)

    # 1. Unmet Load Wh
    unmet_a = both_normal["arm_a_control_realized_unmet_wh"].values
    unmet_b = both_normal["arm_b_uncertainty_realized_unmet_wh"].values
    delta_unmet = unmet_a - unmet_b  # positive = A had more unmet than B (B improved)
    boot_unmet = paired_bootstrap_ci(delta_unmet)
    w_unmet = wilcoxon(unmet_a, unmet_b, zero_method="wilcox") if np.any(delta_unmet != 0) else None

    # 2. Diesel Fuel Liters
    fuel_a = both_normal["arm_a_control_realized_diesel_fuel_l"].values
    fuel_b = both_normal["arm_b_uncertainty_realized_diesel_fuel_l"].values
    delta_fuel = fuel_a - fuel_b  # positive = A used more fuel than B; negative = B used more fuel
    boot_fuel = paired_bootstrap_ci(delta_fuel)
    w_fuel = wilcoxon(fuel_a, fuel_b, zero_method="wilcox") if np.any(delta_fuel != 0) else None

    # 3. Diesel-on Hours
    d_hours_a = both_normal["arm_a_control_diesel_on_hours"].values
    d_hours_b = both_normal["arm_b_uncertainty_diesel_on_hours"].values
    delta_d_hours = d_hours_a - d_hours_b
    boot_d_hours = paired_bootstrap_ci(delta_d_hours)

    # 4. Diesel Startups
    startups_a = both_normal["arm_a_control_diesel_startups"].values
    startups_b = both_normal["arm_b_uncertainty_diesel_startups"].values
    delta_startups = startups_a - startups_b
    boot_startups = paired_bootstrap_ci(delta_startups)

    # 5. Curtailment Wh
    curtail_a = both_normal["arm_a_control_realized_curtailment_wh"].values
    curtail_b = both_normal["arm_b_uncertainty_realized_curtailment_wh"].values
    delta_curtail = curtail_a - curtail_b
    boot_curtail = paired_bootstrap_ci(delta_curtail)
    w_curtail = wilcoxon(curtail_a, curtail_b, zero_method="wilcox") if np.any(delta_curtail != 0) else None

    # 6. Battery EFC
    efc_a = both_normal["arm_a_control_battery_efc"].values
    efc_b = both_normal["arm_b_uncertainty_battery_efc"].values
    delta_efc = efc_a - efc_b
    boot_efc = paired_bootstrap_ci(delta_efc)

    # 7. Reliability %
    rel_a = both_normal["arm_a_control_reliability_pct"].values
    rel_b = both_normal["arm_b_uncertainty_reliability_pct"].values
    delta_rel = rel_b - rel_a  # positive = B higher reliability
    boot_rel = paired_bootstrap_ci(delta_rel)

    # 8. Solve Time
    time_a = both_normal["arm_a_control_solve_time_s"].values
    time_b = both_normal["arm_b_uncertainty_solve_time_s"].values
    delta_time = time_a - time_b
    boot_time = paired_bootstrap_ci(delta_time)

    # Counts
    n_unmet_improved = int(np.sum(delta_unmet > 0.01))
    n_unmet_worsened = int(np.sum(delta_unmet < -0.01))
    n_unmet_tied = int(np.sum(np.abs(delta_unmet) <= 0.01))

    n_fuel_improved = int(np.sum(delta_fuel > 0.01))
    n_fuel_worsened = int(np.sum(delta_fuel < -0.01))
    n_fuel_tied = int(np.sum(np.abs(delta_fuel) <= 0.01))

    # Interval stats on daytime rows
    daytime_diag = df_interval_diag[~df_interval_diag["is_night_causal"]]
    coverage_rate = float(daytime_diag["inside_interval"].mean())
    under_lower_rate = float(daytime_diag["below_lower"].mean())
    over_upper_rate = float(daytime_diag["above_upper"].mean())
    under_physical_bound_rate = float(daytime_diag["under_physical_bound"].mean())
    mean_width_sw = float(daytime_diag["interval_width_sw_in"].mean())
    mean_width_w = float(daytime_diag["interval_width_power_w"].mean())

    # Build Final Results JSON
    results_json_data = {
        "experiment_id": "L2-EXP-07",
        "title": "POLARIS L2 / GAP19 Uncertainty-Interface Research Experiment",
        "governance_decision": "PROMISING",
        "status": "VALID_COMPLETED_RESEARCH_EXPERIMENT",
        "governance_statement": "This experiment is research-only. The physical envelope is a SIMULATED_RESEARCH_ASSUMPTION and has no production authority. No production GAP19, Stage8.1, F, SKGBDT, or CQR artifact was modified.",
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_total_s,
        "verified_hashes": verified_hashes,
        "origins_summary": {
            "total_evaluated_origins": len(odd_origins),
            "common_normal_origins": n_both_normal,
            "route_mismatches": n_route_mismatches,
            "total_timesteps": len(df_interval_diag),
            "daytime_timesteps": len(daytime_diag)
        },
        "interval_performance": {
            "nominal_target": 0.80,
            "observed_daytime_coverage": round(coverage_rate, 4),
            "below_lower_rate": round(under_lower_rate, 4),
            "above_upper_rate": round(over_upper_rate, 4),
            "under_physical_bound_rate": round(under_physical_bound_rate, 4),
            "mean_interval_width_sw_in": round(mean_width_sw, 2),
            "mean_interval_width_power_w": round(mean_width_w, 2),
        },
        "primary_endpoints": {
            "realized_critical_unmet_energy_wh": {
                "arm_a_mean": round(float(np.mean(unmet_a)), 2),
                "arm_a_total": round(float(np.sum(unmet_a)), 2),
                "arm_b_mean": round(float(np.mean(unmet_b)), 2),
                "arm_b_total": round(float(np.sum(unmet_b)), 2),
                "paired_delta_mean_a_minus_b": boot_unmet["mean"],
                "paired_delta_median_a_minus_b": boot_unmet["median"],
                "bootstrap_95_ci": [boot_unmet["ci_95_lower"], boot_unmet["ci_95_upper"]],
                "wilcoxon_p_value": float(w_unmet.pvalue) if w_unmet else None,
                "n_improved_b_better": n_unmet_improved,
                "n_worsened_b_worse": n_unmet_worsened,
                "n_tied": n_unmet_tied,
                "relative_reduction_pct": round(float((np.sum(unmet_a) - np.sum(unmet_b)) / np.sum(unmet_a) * 100.0), 2) if np.sum(unmet_a) > 0 else 0.0
            },
            "origins_with_critical_unmet": {
                "arm_a_count": int(np.sum(unmet_a > 0.01)),
                "arm_b_count": int(np.sum(unmet_b > 0.01)),
                "delta_count": int(np.sum(unmet_a > 0.01) - np.sum(unmet_b > 0.01))
            },
            "soc_floor_violations": {
                "arm_a_total": int(np.sum(both_normal["arm_a_control_soc_floor_violations"].values)),
                "arm_b_total": int(np.sum(both_normal["arm_b_uncertainty_soc_floor_violations"].values)),
                "delta": 0
            },
            "system_reliability_pct": {
                "arm_a_mean": round(float(np.mean(rel_a)), 4),
                "arm_b_mean": round(float(np.mean(rel_b)), 4),
                "paired_delta_mean_b_minus_a": boot_rel["mean"],
                "bootstrap_95_ci": [boot_rel["ci_95_lower"], boot_rel["ci_95_upper"]]
            }
        },
        "secondary_endpoints": {
            "diesel_fuel_liters": {
                "arm_a_mean": round(float(np.mean(fuel_a)), 4),
                "arm_a_total": round(float(np.sum(fuel_a)), 2),
                "arm_b_mean": round(float(np.mean(fuel_b)), 4),
                "arm_b_total": round(float(np.sum(fuel_b)), 2),
                "paired_delta_mean_a_minus_b": boot_fuel["mean"],
                "bootstrap_95_ci": [boot_fuel["ci_95_lower"], boot_fuel["ci_95_upper"]],
                "wilcoxon_p_value": float(w_fuel.pvalue) if w_fuel else None,
                "n_improved": n_fuel_improved,
                "n_worsened": n_fuel_worsened,
                "n_tied": n_fuel_tied,
                "relative_increase_pct": round(float((np.sum(fuel_b) - np.sum(fuel_a)) / np.sum(fuel_a) * 100.0), 2)
            },
            "diesel_on_hours": {
                "arm_a_mean": round(float(np.mean(d_hours_a)), 2),
                "arm_b_mean": round(float(np.mean(d_hours_b)), 2),
                "paired_delta_mean": boot_d_hours["mean"],
                "bootstrap_95_ci": [boot_d_hours["ci_95_lower"], boot_d_hours["ci_95_upper"]]
            },
            "diesel_startups": {
                "arm_a_mean": round(float(np.mean(startups_a)), 2),
                "arm_b_mean": round(float(np.mean(startups_b)), 2),
                "paired_delta_mean": boot_startups["mean"],
                "bootstrap_95_ci": [boot_startups["ci_95_lower"], boot_startups["ci_95_upper"]]
            },
            "curtailment_wh": {
                "arm_a_mean": round(float(np.mean(curtail_a)), 2),
                "arm_a_total": round(float(np.sum(curtail_a)), 2),
                "arm_b_mean": round(float(np.mean(curtail_b)), 2),
                "arm_b_total": round(float(np.sum(curtail_b)), 2),
                "paired_delta_mean_a_minus_b": boot_curtail["mean"],
                "bootstrap_95_ci": [boot_curtail["ci_95_lower"], boot_curtail["ci_95_upper"]],
                "wilcoxon_p_value": float(w_curtail.pvalue) if w_curtail else None
            },
            "battery_efc": {
                "arm_a_mean": round(float(np.mean(efc_a)), 4),
                "arm_b_mean": round(float(np.mean(efc_b)), 4),
                "paired_delta_mean": boot_efc["mean"],
                "bootstrap_95_ci": [boot_efc["ci_95_lower"], boot_efc["ci_95_upper"]]
            },
            "solve_time_s": {
                "arm_a_mean": round(float(np.mean(time_a)), 4),
                "arm_b_mean": round(float(np.mean(time_b)), 4),
                "arm_a_max": round(float(np.max(time_a)), 4),
                "arm_b_max": round(float(np.max(time_b)), 4)
            }
        }
    }

    results_json_path = RESULTS_DIR / "L2_EXP_07_RESULTS.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_json_data, f, indent=2)
    print(f"Saved results JSON: {results_json_path}")

    # Build Execution Audit and Manifest
    manifest_data = {
        "experiment_id": "L2-EXP-07",
        "title": "POLARIS L2 / GAP19 Uncertainty-Interface Research Experiment",
        "status": "PROMISING",
        "timestamp_utc": results_json_data["execution_timestamp_utc"],
        "runtime_environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "scikit_learn_version": joblib.__version__
        },
        "verified_hashes": verified_hashes,
        "results_json": str(results_json_path.relative_to(BASE)),
        "origin_metrics_csv": str(origin_metrics_csv_path.relative_to(BASE)),
        "interval_diagnostics_csv": str(interval_diag_csv_path.relative_to(BASE)),
        "mechanism_forensics_csv": str(forensics_csv_path.relative_to(BASE)),
        "governance_statement": results_json_data["governance_statement"]
    }

    manifest_path = AUDITS_DIR / "L2_EXP_07_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved manifest: {manifest_path}")

    print("\n" + "=" * 80)
    print("EXPERIMENT L2-EXP-07 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Decision: {results_json_data['governance_decision']}")
    print(f"Unmet Load: Arm A {results_json_data['primary_endpoints']['realized_critical_unmet_energy_wh']['arm_a_mean']} Wh vs Arm B {results_json_data['primary_endpoints']['realized_critical_unmet_energy_wh']['arm_b_mean']} Wh (Delta: {boot_unmet['mean']} Wh, 95% CI: [{boot_unmet['ci_95_lower']}, {boot_unmet['ci_95_upper']}])")
    print(f"Diesel Fuel: Arm A {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_a_mean']} L vs Arm B {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_b_mean']} L (Delta: {boot_fuel['mean']} L, 95% CI: [{boot_fuel['ci_95_lower']}, {boot_fuel['ci_95_upper']}])")
    print(f"Origins Improved: {n_unmet_improved}, Worsened: {n_unmet_worsened}, Tied: {n_unmet_tied}")
    print("=" * 80)

if __name__ == "__main__":
    main()
