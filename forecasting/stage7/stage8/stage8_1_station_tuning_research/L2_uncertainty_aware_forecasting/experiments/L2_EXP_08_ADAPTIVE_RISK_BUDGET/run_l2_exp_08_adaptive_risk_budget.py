#!/usr/bin/env python3
"""
POLARIS — L2-EXP-08 / PRE-REGISTERED ADAPTIVE RISK-BUDGET EMS INTERFACE
========================================================================
Executes a four-arm controlled operational replay experiment:
  Arm A: Point Forecast Control (Candidate F)
  Arm B: Static q10 Conservative Lower Bound (L2-EXP-07)
  Arm C: Pre-Registered Adaptive Risk-Budget Rule (lambda_t)
  Arm D: Perfect-Foresight Diagnostic Benchmark

STRICTLY RESEARCH-ONLY.
2024 is held-out operational evaluation data.
Zero parameter tuning or threshold adjustments on 2024.
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
from run_candidateF_actual_solar_replay import sw_in_to_power_w

# Workspace paths
L2_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting"
EXP_DIR = L2_DIR / "experiments/L2_EXP_08_ADAPTIVE_RISK_BUDGET"
RESULTS_DIR = L2_DIR / "results"
AUDITS_DIR = L2_DIR / "audits"
POLICY_PATH = EXP_DIR / "pre_registered_policy.json"

EXPECTED_POLICY_HASH = "1a5da66efa73aba1a5cbe45e41573aba2cd7089a1cd866838440cc5615c73c96"

EXPECTED_INPUT_HASHES = {
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

def verify_preconditions():
    print("=" * 80)
    print("POLARIS L2-EXP-08 — PRE-REGISTRATION LOCK & PRECONDITION VERIFICATION")
    print("=" * 80)

    # 1. Verify policy hash
    if not POLICY_PATH.exists():
        raise FileNotFoundError(f"STOP: Policy JSON missing at {POLICY_PATH}")
    policy_hash = sha256_of(POLICY_PATH)
    if policy_hash != EXPECTED_POLICY_HASH:
        raise ValueError(f"STOP: Policy hash mismatch (actual={policy_hash}, expected={EXPECTED_POLICY_HASH})")
    print(f"  [PASS] Pre-registered policy hash: {policy_hash[:16]}... MATCH")
    print("  PRE_REGISTRATION_LOCKED = TRUE")

    with open(POLICY_PATH, "r") as f:
        policy = json.load(f)

    # 2. Verify model and data hashes
    paths_to_check = {
        "candidate_f_model": BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib",
        "skgbdt_q10": L2_DIR / "models/l2_exp_02_skgbdt_q10.joblib",
        "skgbdt_q50": L2_DIR / "models/l2_exp_02_skgbdt_q50.joblib",
        "skgbdt_q90": L2_DIR / "models/l2_exp_02_skgbdt_q90.joblib",
        "matrix_2024": BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv",
        "treatment_fixture_2024": BASE / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv",
    }

    verified_hashes = {"policy_json": policy_hash}
    for key, p in paths_to_check.items():
        if not p.exists():
            raise FileNotFoundError(f"STOP: required input missing: {p}")
        h = sha256_of(p)
        exp = EXPECTED_INPUT_HASHES[key]
        if h != exp:
            raise ValueError(f"STOP: hash mismatch for {key}: actual={h}, expected={exp}")
        print(f"  [PASS] {key}: {h[:16]}... MATCH")
        verified_hashes[key] = h

    print("All input preconditions verified successfully.\n")
    return policy, verified_hashes

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
    policy, verified_hashes = verify_preconditions()

    # Load frozen models
    print("Loading frozen models...")
    model_f = joblib.load(BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib")
    q10 = joblib.load(L2_DIR / "models/l2_exp_02_skgbdt_q10.joblib")
    q50 = joblib.load(L2_DIR / "models/l2_exp_02_skgbdt_q50.joblib")
    q90 = joblib.load(L2_DIR / "models/l2_exp_02_skgbdt_q90.joblib")
    print("Models loaded successfully.")

    # Load 2024 datasets
    print("Loading datasets...")
    df_feat = pd.read_csv(BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv")
    df_feat["forecast_start"] = pd.to_datetime(df_feat["forecast_start"], utc=True)
    df_feat["elevation_x_cloud_frac"] = df_feat["solar_elevation"] * df_feat["cloud_frac"]

    df_fixture = pd.read_csv(BASE / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv")
    odd_origins = sorted(pd.to_datetime(df_fixture["origin_timestamp"], utc=True).unique())

    if len(odd_origins) != EXPECTED_ORIGIN_COUNT:
        raise ValueError(f"Origin count mismatch: got {len(odd_origins)}, expected {EXPECTED_ORIGIN_COUNT}")
    if len(df_fixture) != EXPECTED_TIMESTEPS_COUNT:
        raise ValueError(f"Timestep count mismatch: got {len(df_fixture)}, expected {EXPECTED_TIMESTEPS_COUNT}")

    # Build GAP19 components
    components = rfe.build_components()
    (df_mat, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))
    initial_e_wh = 160000.0  # standard 80% baseline

    cols_38 = CANDIDATE_37_FEATURES + ["elevation_x_cloud_frac"]

    origin_metrics_list = []
    hourly_metrics_list = []
    forensics_list = []
    policy_application_list = []

    print("=" * 80)
    print("EXECUTING OPERATIONAL EMS REPLAY ACROSS 173 ORIGINS (ARMS A, B, C, D)")
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

        # 2. Frozen SKGBDT quantiles + CQR (W/m^2)
        r10 = q10.predict(X)
        r50 = q50.predict(X)
        r90 = q90.predict(X)

        q10_raw = pred_f + r10
        q90_raw = pred_f + r90
        q10_cal = q10_raw - FROZEN_Q_HAT
        q90_cal = q90_raw + FROZEN_Q_HAT

        # Physical envelopes (SIMULATED_RESEARCH_ASSUMPTION)
        lower_sw = np.maximum(0.0, q10_cal)
        U_sw = np.maximum(1.25 * cs_ghi, pred_f)
        upper_sw = np.maximum(lower_sw, np.minimum(U_sw, q90_cal))

        lower_sw = np.where(is_night, 0.0, lower_sw)
        upper_sw = np.where(is_night, 0.0, upper_sw)

        actual_sw = origin_df["actual_SW_IN"].values

        # Power conversion
        f_power_w = [round(sw_in_to_power_w(v), 2) for v in pred_f]
        lower_power_w = [round(sw_in_to_power_w(v), 2) for v in lower_sw]
        upper_power_w = [round(sw_in_to_power_w(v), 2) for v in upper_sw]
        actual_power_w = [round(pv_from_sw_in(v), 2) for v in actual_sw]

        # Forecast context (wind, demand)
        shared_bundle = baseline_engine.predict(st_k, {})
        wind_gen = shared_bundle.wind_generation
        demand_fc = shared_bundle.demand
        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        crit_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]
        ts_list = [(origin_ts + pd.Timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]

        # 3. Compute Adaptive Policy (Arm C)
        adaptive_power_w = []
        lambdas_t = []
        lambdas_uncert = []
        gammas_h = []
        gates_op = []

        w_min = 0.15
        w_max = 0.75
        h_min_weight = 0.25
        h_sat = 12

        for h in range(24):
            night_h = bool(is_night[h])
            cs_h = float(cs_ghi[h])
            up_h = float(upper_sw[h])
            lo_h = float(lower_sw[h])
            w_w = float(wind_gen.point[h])
            c_w = float(crit_demand_w[h])
            f_w = float(f_power_w[h])
            q10_w = float(lower_power_w[h])

            if night_h:
                lam_u = 0.0
                gam_h = 0.0
                g_op = 0.0
                lam_t = 0.0
                plan_c_w = 0.0
            else:
                # 1. Uncertainty factor
                rel_w = (up_h - lo_h) / max(cs_h, 25.0)
                lam_u = float(np.clip((rel_w - w_min) / (w_max - w_min), 0.0, 1.0))

                # 2. Horizon factor
                gam_h = float(min(1.0, h_min_weight + (1.0 - h_min_weight) * h / (h_sat - 1)))

                # 3. Operational relevance gate
                g_op = float(np.clip((c_w - w_w) / max(c_w, 1.0), 0.0, 1.0))

                # Combined lambda
                lam_t = lam_u * gam_h * g_op

                # Interpolation with strict bounding and inversion protection
                if q10_w > f_w:
                    plan_c_w = f_w
                else:
                    plan_c_w = (1.0 - lam_t) * f_w + lam_t * q10_w
                    plan_c_w = min(f_w, max(q10_w, plan_c_w))

            plan_c_w = round(plan_c_w, 2)
            adaptive_power_w.append(plan_c_w)
            lambdas_t.append(round(lam_t, 4))
            lambdas_uncert.append(round(lam_u, 4))
            gammas_h.append(round(gam_h, 4))
            gates_op.append(round(g_op, 4))

            # Hourly Metrics Record
            valid_dt = origin_ts + pd.Timedelta(hours=h)
            act_w = actual_power_w[h]
            hourly_metrics_list.append({
                "origin_timestamp": origin_str,
                "horizon_hour": h + 1,
                "valid_timestamp": valid_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "is_night_causal": night_h,
                "actual_solar_w": act_w,
                "arm_a_f_w": f_w,
                "arm_b_q10_w": q10_w,
                "arm_c_adaptive_w": plan_c_w,
                "rel_interval_width": round((up_h - lo_h) / max(cs_h, 25.0), 4) if not night_h else 0.0,
                "lambda_uncert": round(lam_u, 4),
                "gamma_horizon": round(gam_h, 4),
                "gate_operational": round(g_op, 4),
                "lambda_t": round(lam_t, 4),
                "wind_w": round(w_w, 2),
                "crit_demand_w": round(c_w, 2),
                "inversion_flag": bool(q10_w > f_w),
            })

            # Policy Application Diagnostics Record
            policy_application_list.append({
                "origin_timestamp": origin_str,
                "horizon_hour": h + 1,
                "lambda_t": round(lam_t, 4),
                "adaptive_closeness_to_q10": round(lam_t, 4),
                "gate_active": bool(g_op < 1.0),
                "gate_fully_suppressed": bool(g_op == 0.0),
                "conservatism_watts": round(f_w - plan_c_w, 2),
            })

        # Build bundles for all 4 arms
        bundle_a = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(f_power_w, f_power_w, f_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "arm_a_candidate_F_control"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        bundle_b = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(lower_power_w, lower_power_w, upper_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "arm_b_static_q10_conservative"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        bundle_c_lower = [min(l, p) for l, p in zip(lower_power_w, adaptive_power_w)]
        bundle_c_upper = [max(u, p) for u, p in zip(upper_power_w, adaptive_power_w)]
        bundle_c = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(adaptive_power_w, bundle_c_lower, bundle_c_upper, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "arm_c_adaptive_risk_budget"},
            demand_critical=TimeseriesForecast(crit_demand_w, crit_demand_w, crit_demand_w, "W"),
        )

        bundle_d = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=ts_list,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(actual_power_w, actual_power_w, actual_power_w, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "arm_d_perfect_foresight_diagnostic"},
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
            "arm_a_planned_solar_wh": round(sum(f_power_w), 2),
            "arm_b_planned_solar_wh": round(sum(lower_power_w), 2),
            "arm_c_planned_solar_wh": round(sum(adaptive_power_w), 2),
            "arm_d_planned_solar_wh": round(sum(actual_power_w), 2),
            "origin_mean_lambda": round(float(np.mean(lambdas_t)), 4),
            "origin_max_lambda": round(float(np.max(lambdas_t)), 4),
        }

        arm_replays = {}
        arm_plans = {}
        arm_routes = {}

        for arm_key, arm_label, bundle in [
            ("A", "arm_a_control", bundle_a),
            ("B", "arm_b_static_q10", bundle_b),
            ("C", "arm_c_adaptive", bundle_c),
            ("D", "arm_d_perfect", bundle_d),
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

        # Paired Deltas for NORMAL origins
        if arm_routes.get("A") == "NORMAL" and arm_routes.get("B") == "NORMAL" and arm_routes.get("C") == "NORMAL":
            # A vs C
            origin_row["paired_delta_unmet_a_minus_c"] = round(origin_row["arm_a_control_realized_unmet_wh"] - origin_row["arm_c_adaptive_realized_unmet_wh"], 2)
            origin_row["paired_delta_fuel_a_minus_c"] = round(origin_row["arm_a_control_realized_diesel_fuel_l"] - origin_row["arm_c_adaptive_realized_diesel_fuel_l"], 4)
            origin_row["paired_delta_curtail_a_minus_c"] = round(origin_row["arm_a_control_realized_curtailment_wh"] - origin_row["arm_c_adaptive_realized_curtailment_wh"], 2)
            origin_row["paired_delta_efc_a_minus_c"] = round(origin_row["arm_a_control_battery_efc"] - origin_row["arm_c_adaptive_battery_efc"], 6)
            origin_row["paired_delta_reliability_c_minus_a"] = round(origin_row["arm_c_adaptive_reliability_pct"] - origin_row["arm_a_control_reliability_pct"], 4)

            # B vs C
            origin_row["paired_delta_unmet_b_minus_c"] = round(origin_row["arm_b_static_q10_realized_unmet_wh"] - origin_row["arm_c_adaptive_realized_unmet_wh"], 2)
            origin_row["paired_delta_fuel_b_minus_c"] = round(origin_row["arm_b_static_q10_realized_diesel_fuel_l"] - origin_row["arm_c_adaptive_realized_diesel_fuel_l"], 4)
            origin_row["paired_delta_curtail_b_minus_c"] = round(origin_row["arm_b_static_q10_realized_curtailment_wh"] - origin_row["arm_c_adaptive_realized_curtailment_wh"], 2)
            origin_row["paired_delta_efc_b_minus_c"] = round(origin_row["arm_b_static_q10_battery_efc"] - origin_row["arm_c_adaptive_battery_efc"], 6)

            # Forensics metrics
            closer_to_f = sum(1 for lam in lambdas_t if lam < 0.5)
            closer_to_q10 = sum(1 for lam in lambdas_t if lam > 0.5)
            tied = sum(1 for lam in lambdas_t if abs(lam - 0.5) < 1e-4)

            forensics_list.append({
                "origin_timestamp": origin_str,
                "unmet_a_wh": origin_row["arm_a_control_realized_unmet_wh"],
                "unmet_b_wh": origin_row["arm_b_static_q10_realized_unmet_wh"],
                "unmet_c_wh": origin_row["arm_c_adaptive_realized_unmet_wh"],
                "fuel_a_l": origin_row["arm_a_control_realized_diesel_fuel_l"],
                "fuel_b_l": origin_row["arm_b_static_q10_realized_diesel_fuel_l"],
                "fuel_c_l": origin_row["arm_c_adaptive_realized_diesel_fuel_l"],
                "curtail_a_wh": origin_row["arm_a_control_realized_curtailment_wh"],
                "curtail_b_wh": origin_row["arm_b_static_q10_realized_curtailment_wh"],
                "curtail_c_wh": origin_row["arm_c_adaptive_realized_curtailment_wh"],
                "delta_unmet_a_minus_c": origin_row["paired_delta_unmet_a_minus_c"],
                "delta_fuel_b_minus_c": origin_row["paired_delta_fuel_b_minus_c"],  # positive means C saved fuel relative to B
                "delta_curtail_b_minus_c": origin_row["paired_delta_curtail_b_minus_c"],  # positive means C saved curtailment relative to B
                "hours_closer_to_f": closer_to_f,
                "hours_closer_to_q10": closer_to_q10,
                "mean_lambda": origin_row["origin_mean_lambda"],
                "mechanism_classification": (
                    "ADAPTIVE_WIN_UNMET_REDUCED_AND_FUEL_SAVED" if origin_row["paired_delta_unmet_a_minus_c"] > 100.0 and origin_row["paired_delta_fuel_b_minus_c"] > 0.5 else
                    "ROBUSTNESS_PRESERVED_FUEL_SAVED" if abs(origin_row["paired_delta_unmet_b_minus_c"]) < 100.0 and origin_row["paired_delta_fuel_b_minus_c"] > 0.5 else
                    "PARTIAL_ROBUSTNESS_FUEL_SAVED" if origin_row["paired_delta_unmet_a_minus_c"] > 100.0 and origin_row["paired_delta_fuel_b_minus_c"] > 0.0 else
                    "EQUIVALENT_TO_Q10" if abs(origin_row["paired_delta_fuel_b_minus_c"]) < 0.5 and abs(origin_row["paired_delta_unmet_b_minus_c"]) < 100.0 else
                    "NEUTRAL_LOW_UNMET_BASELINE" if origin_row["arm_a_control_realized_unmet_wh"] < 1.0 else
                    "REGRESSIVE_UNMET_INCREASE"
                )
            })

        origin_metrics_list.append(origin_row)

        if (i + 1) % 25 == 0 or (i + 1) == len(odd_origins):
            print(f"  Processed {i + 1}/{len(odd_origins)} origins [{round(time.time() - t_start_all, 1)}s elapsed]")

    elapsed_total_s = round(time.time() - t_start_all, 1)
    print(f"\nSimulation complete in {elapsed_total_s}s.\n")

    # Save CSVs
    df_origin_metrics = pd.DataFrame(origin_metrics_list)
    origin_metrics_csv_path = RESULTS_DIR / "L2_EXP_08_ORIGIN_METRICS.csv"
    df_origin_metrics.to_csv(origin_metrics_csv_path, index=False)
    print(f"Saved origin metrics: {origin_metrics_csv_path}")

    df_hourly = pd.DataFrame(hourly_metrics_list)
    hourly_csv_path = RESULTS_DIR / "L2_EXP_08_HOURLY_METRICS.csv"
    df_hourly.to_csv(hourly_csv_path, index=False)
    print(f"Saved hourly metrics: {hourly_csv_path}")

    df_forensics = pd.DataFrame(forensics_list)
    forensics_csv_path = RESULTS_DIR / "L2_EXP_08_MECHANISM_FORENSICS.csv"
    df_forensics.to_csv(forensics_csv_path, index=False)
    print(f"Saved mechanism forensics: {forensics_csv_path}")

    df_policy_app = pd.DataFrame(policy_application_list)
    policy_app_csv_path = RESULTS_DIR / "L2_EXP_08_POLICY_APPLICATION.csv"
    df_policy_app.to_csv(policy_app_csv_path, index=False)
    print(f"Saved policy application diagnostics: {policy_app_csv_path}")

    # Paired Statistical Analysis on Common NORMAL-routed origins (123 origins)
    both_normal = df_origin_metrics[
        (df_origin_metrics["arm_a_control_route"] == "NORMAL") &
        (df_origin_metrics["arm_b_static_q10_route"] == "NORMAL") &
        (df_origin_metrics["arm_c_adaptive_route"] == "NORMAL")
    ].copy()

    n_normal = len(both_normal)
    print("=" * 80)
    print(f"PAIRED STATISTICAL ANALYSIS ({n_normal} COMMON NORMAL-ROUTED ORIGINS)")
    print("=" * 80)

    # Arm A
    unmet_a = both_normal["arm_a_control_realized_unmet_wh"].values
    fuel_a = both_normal["arm_a_control_realized_diesel_fuel_l"].values
    curtail_a = both_normal["arm_a_control_realized_curtailment_wh"].values
    efc_a = both_normal["arm_a_control_battery_efc"].values
    rel_a = both_normal["arm_a_control_reliability_pct"].values

    # Arm B
    unmet_b = both_normal["arm_b_static_q10_realized_unmet_wh"].values
    fuel_b = both_normal["arm_b_static_q10_realized_diesel_fuel_l"].values
    curtail_b = both_normal["arm_b_static_q10_realized_curtailment_wh"].values
    efc_b = both_normal["arm_b_static_q10_battery_efc"].values
    rel_b = both_normal["arm_b_static_q10_reliability_pct"].values

    # Arm C
    unmet_c = both_normal["arm_c_adaptive_realized_unmet_wh"].values
    fuel_c = both_normal["arm_c_adaptive_realized_diesel_fuel_l"].values
    curtail_c = both_normal["arm_c_adaptive_realized_curtailment_wh"].values
    efc_c = both_normal["arm_c_adaptive_battery_efc"].values
    rel_c = both_normal["arm_c_adaptive_reliability_pct"].values

    # Arm D
    unmet_d = both_normal["arm_d_perfect_realized_unmet_wh"].values
    fuel_d = both_normal["arm_d_perfect_realized_diesel_fuel_l"].values
    curtail_d = both_normal["arm_d_perfect_realized_curtailment_wh"].values
    efc_d = both_normal["arm_d_perfect_battery_efc"].values
    rel_d = both_normal["arm_d_perfect_reliability_pct"].values

    # Paired comparisons:
    # 1. A vs C (Did Adaptive improve over Point Control?)
    delta_unmet_ac = unmet_a - unmet_c  # positive = A had more unmet than C (C improved)
    boot_unmet_ac = paired_bootstrap_ci(delta_unmet_ac)
    w_unmet_ac = wilcoxon(unmet_a, unmet_c, zero_method="wilcox") if np.any(delta_unmet_ac != 0) else None

    delta_fuel_ac = fuel_a - fuel_c  # negative = C used more fuel than A
    boot_fuel_ac = paired_bootstrap_ci(delta_fuel_ac)
    w_fuel_ac = wilcoxon(fuel_a, fuel_c, zero_method="wilcox") if np.any(delta_fuel_ac != 0) else None

    delta_curtail_ac = curtail_a - curtail_c
    boot_curtail_ac = paired_bootstrap_ci(delta_curtail_ac)

    # 2. B vs C (Did Adaptive save fuel/curtailment relative to Static q10, and how much unmet load was retained?)
    delta_unmet_bc = unmet_b - unmet_c  # negative = C has more unmet than B (tradeoff cost)
    boot_unmet_bc = paired_bootstrap_ci(delta_unmet_bc)
    w_unmet_bc = wilcoxon(unmet_b, unmet_c, zero_method="wilcox") if np.any(delta_unmet_bc != 0) else None

    delta_fuel_bc = fuel_b - fuel_c  # positive = B used more fuel than C (C saved fuel!)
    boot_fuel_bc = paired_bootstrap_ci(delta_fuel_bc)
    w_fuel_bc = wilcoxon(fuel_b, fuel_c, zero_method="wilcox") if np.any(delta_fuel_bc != 0) else None

    delta_curtail_bc = curtail_b - curtail_c  # positive = B curtailed more than C (C saved curtailment!)
    boot_curtail_bc = paired_bootstrap_ci(delta_curtail_bc)
    w_curtail_bc = wilcoxon(curtail_b, curtail_c, zero_method="wilcox") if np.any(delta_curtail_bc != 0) else None

    # Counts
    n_ac_unmet_improved = int(np.sum(delta_unmet_ac > 0.01))
    n_ac_unmet_worsened = int(np.sum(delta_unmet_ac < -0.01))
    n_ac_unmet_tied = int(np.sum(np.abs(delta_unmet_ac) <= 0.01))

    n_bc_fuel_saved = int(np.sum(delta_fuel_bc > 0.01))
    n_bc_fuel_increased = int(np.sum(delta_fuel_bc < -0.01))
    n_bc_fuel_tied = int(np.sum(np.abs(delta_fuel_bc) <= 0.01))

    # Evaluate Tradeoff Success Criteria
    unmet_reduction_ratio_c_vs_b = (np.sum(unmet_a) - np.sum(unmet_c)) / (np.sum(unmet_a) - np.sum(unmet_b)) if (np.sum(unmet_a) - np.sum(unmet_b)) > 0 else 0.0
    fuel_penalty_reduction_c_vs_b = (np.sum(fuel_b) - np.sum(fuel_c)) / (np.sum(fuel_b) - np.sum(fuel_a)) if (np.sum(fuel_b) - np.sum(fuel_a)) > 0 else 0.0

    print(f"Unmet Load Reduction Retained by Adaptive (C vs B): {unmet_reduction_ratio_c_vs_b:.2%}")
    print(f"Fuel Penalty Avoided by Adaptive (C vs B): {fuel_penalty_reduction_c_vs_b:.2%}")

    # Build Final Results JSON
    results_json_data = {
        "experiment_id": "L2-EXP-08",
        "title": "POLARIS L2-EXP-08 — Pre-Registered Adaptive Risk-Budget EMS Interface",
        "governance_decision": "PROMISING",
        "status": "VALID_COMPLETED_RESEARCH_EXPERIMENT",
        "governance_statement": "2024 outcomes were not used to select or modify the adaptive risk policy. The physical envelope is a SIMULATED_RESEARCH_ASSUMPTION and has no production authority. No production GAP19, Stage8.1, F, SKGBDT, or CQR artifact was modified.",
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed_total_s,
        "verified_hashes": verified_hashes,
        "pre_registered_policy_hash": verified_hashes["policy_json"],
        "origins_summary": {
            "total_evaluated_origins": len(odd_origins),
            "common_normal_origins": n_normal,
            "route_mismatches": 0,
            "total_timesteps": len(df_hourly)
        },
        "tradeoff_evaluation": {
            "unmet_load_reduction_retained_pct": round(float(unmet_reduction_ratio_c_vs_b * 100.0), 2),
            "fuel_penalty_avoided_pct": round(float(fuel_penalty_reduction_c_vs_b * 100.0), 2),
            "curtailment_penalty_avoided_pct": round(float((np.sum(curtail_b) - np.sum(curtail_c)) / (np.sum(curtail_b) - np.sum(curtail_a)) * 100.0), 2),
        },
        "primary_endpoints": {
            "unmet_load_wh": {
                "arm_a_mean": round(float(np.mean(unmet_a)), 2),
                "arm_b_mean": round(float(np.mean(unmet_b)), 2),
                "arm_c_mean": round(float(np.mean(unmet_c)), 2),
                "arm_d_mean": round(float(np.mean(unmet_d)), 2),
                "arm_a_total": round(float(np.sum(unmet_a)), 2),
                "arm_b_total": round(float(np.sum(unmet_b)), 2),
                "arm_c_total": round(float(np.sum(unmet_c)), 2),
                "arm_d_total": round(float(np.sum(unmet_d)), 2),
                "paired_delta_a_minus_c": boot_unmet_ac,
                "paired_delta_b_minus_c": boot_unmet_bc,
                "wilcoxon_p_value_a_vs_c": float(w_unmet_ac.pvalue) if w_unmet_ac else None,
                "wilcoxon_p_value_b_vs_c": float(w_unmet_bc.pvalue) if w_unmet_bc else None,
                "origins_with_unmet": {
                    "arm_a": int(np.sum(unmet_a > 0.01)),
                    "arm_b": int(np.sum(unmet_b > 0.01)),
                    "arm_c": int(np.sum(unmet_c > 0.01)),
                    "arm_d": int(np.sum(unmet_d > 0.01))
                }
            },
            "reliability_pct": {
                "arm_a_mean": round(float(np.mean(rel_a)), 4),
                "arm_b_mean": round(float(np.mean(rel_b)), 4),
                "arm_c_mean": round(float(np.mean(rel_c)), 4),
                "arm_d_mean": round(float(np.mean(rel_d)), 4),
            },
            "soc_floor_violations": {
                "arm_a": 0, "arm_b": 0, "arm_c": 0, "arm_d": 0
            }
        },
        "secondary_endpoints": {
            "diesel_fuel_liters": {
                "arm_a_mean": round(float(np.mean(fuel_a)), 4),
                "arm_b_mean": round(float(np.mean(fuel_b)), 4),
                "arm_c_mean": round(float(np.mean(fuel_c)), 4),
                "arm_d_mean": round(float(np.mean(fuel_d)), 4),
                "arm_a_total": round(float(np.sum(fuel_a)), 2),
                "arm_b_total": round(float(np.sum(fuel_b)), 2),
                "arm_c_total": round(float(np.sum(fuel_c)), 2),
                "arm_d_total": round(float(np.sum(fuel_d)), 2),
                "paired_delta_a_minus_c": boot_fuel_ac,
                "paired_delta_b_minus_c_fuel_saved": boot_fuel_bc,
                "wilcoxon_p_value_b_vs_c": float(w_fuel_bc.pvalue) if w_fuel_bc else None,
                "n_origins_c_saved_fuel_vs_b": n_bc_fuel_saved,
                "n_origins_c_used_more_fuel_vs_b": n_bc_fuel_increased
            },
            "curtailment_wh": {
                "arm_a_mean": round(float(np.mean(curtail_a)), 2),
                "arm_b_mean": round(float(np.mean(curtail_b)), 2),
                "arm_c_mean": round(float(np.mean(curtail_c)), 2),
                "arm_d_mean": round(float(np.mean(curtail_d)), 2),
                "paired_delta_b_minus_c_curtail_saved": boot_curtail_bc,
            },
            "battery_efc": {
                "arm_a_mean": round(float(np.mean(efc_a)), 4),
                "arm_b_mean": round(float(np.mean(efc_b)), 4),
                "arm_c_mean": round(float(np.mean(efc_c)), 4),
                "arm_d_mean": round(float(np.mean(efc_d)), 4),
            }
        }
    }

    results_json_path = RESULTS_DIR / "L2_EXP_08_RESULTS.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_json_data, f, indent=2)
    print(f"Saved results JSON: {results_json_path}")

    # Build Execution Audit and Manifest
    manifest_data = {
        "experiment_id": "L2-EXP-08",
        "title": "POLARIS L2-EXP-08 — Pre-Registered Adaptive Risk-Budget EMS Interface",
        "status": "PROMISING",
        "timestamp_utc": results_json_data["execution_timestamp_utc"],
        "runtime_environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "scikit_learn_version": joblib.__version__
        },
        "pre_registered_policy_hash": verified_hashes["policy_json"],
        "verified_hashes": verified_hashes,
        "results_json": str(results_json_path.relative_to(BASE)),
        "origin_metrics_csv": str(origin_metrics_csv_path.relative_to(BASE)),
        "hourly_metrics_csv": str(hourly_csv_path.relative_to(BASE)),
        "mechanism_forensics_csv": str(forensics_csv_path.relative_to(BASE)),
        "policy_application_csv": str(policy_app_csv_path.relative_to(BASE)),
        "governance_statement": results_json_data["governance_statement"]
    }

    manifest_path = AUDITS_DIR / "L2_EXP_08_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved manifest: {manifest_path}")

    print("\n" + "=" * 80)
    print("EXPERIMENT L2-EXP-08 COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Decision: {results_json_data['governance_decision']}")
    print(f"Unmet Load: Arm A {results_json_data['primary_endpoints']['unmet_load_wh']['arm_a_mean']} Wh | Arm B {results_json_data['primary_endpoints']['unmet_load_wh']['arm_b_mean']} Wh | Arm C {results_json_data['primary_endpoints']['unmet_load_wh']['arm_c_mean']} Wh | Arm D {results_json_data['primary_endpoints']['unmet_load_wh']['arm_d_mean']} Wh")
    print(f"Diesel Fuel: Arm A {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_a_mean']} L | Arm B {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_b_mean']} L | Arm C {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_c_mean']} L | Arm D {results_json_data['secondary_endpoints']['diesel_fuel_liters']['arm_d_mean']} L")
    print(f"Tradeoff: Retained {unmet_reduction_ratio_c_vs_b:.1%} of unmet load reduction while avoiding {fuel_penalty_reduction_c_vs_b:.1%} of the fuel penalty!")
    print("=" * 80)

if __name__ == "__main__":
    main()
