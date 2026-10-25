#!/usr/bin/env python3
"""
CANDIDATE F EMS REPLAY. RESEARCH-ONLY. NOT a production run. NOT a re-optimization.

Runs Candidate F (the 38-feature `solar_elevation x cloud_frac` additive-feature research
model from forecasting/stage7/stage8/stage8_1_station_tuning_research/, CANDIDATE_F_REPORT.md) through
the EXACT SAME actual-solar EMS replay methodology already used and disclosed in
run_actual_solar_replay.py, for direct comparison against the frozen Stage 8.1 (37-feature)
model, on the SAME 245 NORMAL-route origins, SAME warmed-up StationState construction, SAME
critical-demand/terminal-reserve formula, SAME replay physics (diesel/discharge held fixed,
charge clipped to availability, critical load prioritized over charging in the replay).

Reused, UNMODIFIED, by import: `replay_plan_against_actual_solar` and `pv_from_sw_in` from
run_actual_solar_replay.py; `compute_terminal_target_wh` from run_research_simulation.py;
`verify_frozen_manifest`, `build_components` from run_full_experiment.py. GAP19 itself,
system/config/*.yaml, and the frozen Stage 8.1 model/manifest are never modified. Candidate
F's own model file (a NEW, research-only artifact, not a frozen one) is loaded read-only.

No production/config/freeze file modified by this script.
"""
import sys
import json
import hashlib
import time
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

import run_full_experiment as rfe
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_actual_solar_replay import pv_from_sw_in, replay_plan_against_actual_solar

STATION_TUNING_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_station_tuning_research"
CANDIDATE_F_MODEL_PATH = STATION_TUNING_DIR / "model_artifacts" / "candidateF_elevation_x_cloud.joblib"
EXPECTED_CANDIDATE_F_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"

FROZEN_STAGE81_MODEL_PATH = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025" / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
EXPECTED_FROZEN_STAGE81_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"

MATRIX_2024_PATH = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025" / "stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"

PV_CONFIG = {"array_area_m2": 300.0, "panel_efficiency": 0.20, "performance_ratio": 0.85,
             "max_inverter_power_w": 60000.0}
ADDITIVE_FEATURE_NAME = "elevation_x_cloud_frac"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sw_in_to_power_w(sw_in):
    raw = sw_in * PV_CONFIG["array_area_m2"] * PV_CONFIG["panel_efficiency"] * PV_CONFIG["performance_ratio"]
    return max(0.0, min(raw, PV_CONFIG["max_inverter_power_w"]))


def predict_solar_bundle(model, feature_cols, origin_rows_24, extra_feature_fn=None):
    """Reproduces Stage81CorrectedForecastEngine.predict()'s solar-reconstruction logic
    exactly (same PV formula, same night-causal zeroing, same residual-on-Stage4
    reconstruction), for a given already-fitted model and its own feature column list.
    New, read-only research code -- does not modify the frozen engine class."""
    df = origin_rows_24.sort_values("horizon_hour").reset_index(drop=True)
    if extra_feature_fn is not None:
        df = df.copy()
        df[ADDITIVE_FEATURE_NAME] = extra_feature_fn(df)
    X = df[feature_cols].values.astype(np.float64)
    residual = model.predict(X)
    pred_stage4 = df["pred_stage4_fold"].values
    solar_elevation = df["solar_elevation"].values
    clearsky_ghi = df["clearsky_ghi"].values
    is_night_causal = (solar_elevation <= 0.0) | (clearsky_ghi == 0.0)
    pred_sw_in = np.maximum(0.0, pred_stage4 + residual)
    pred_sw_in = np.where(is_night_causal, 0.0, pred_sw_in)
    solar_gen_w = [round(sw_in_to_power_w(v), 2) for v in pred_sw_in]
    return solar_gen_w


def arrsum(a):
    return round(float(sum(a)), 4)


def main():
    print("=" * 80)
    print("CANDIDATE F EMS REPLAY -- frozen Stage 8.1 vs Candidate F, same 245 NORMAL origins")
    print("Same actual-solar replay methodology as run_actual_solar_replay.py. RESEARCH-ONLY.")
    print("=" * 80)

    rfe.verify_frozen_manifest()

    h_f = sha256_of(CANDIDATE_F_MODEL_PATH)
    h_stage81 = sha256_of(FROZEN_STAGE81_MODEL_PATH)
    h_matrix = sha256_of(MATRIX_2024_PATH)
    assert h_f == EXPECTED_CANDIDATE_F_HASH, f"STOP: Candidate F model hash drift: {h_f}"
    assert h_stage81 == EXPECTED_FROZEN_STAGE81_HASH, f"STOP: frozen Stage 8.1 model hash drift: {h_stage81}"
    assert h_matrix == EXPECTED_MATRIX_2024_HASH, f"STOP: 2024 matrix hash drift: {h_matrix}"
    print(f"Candidate F model hash:    {h_f}  (MATCH)")
    print(f"Frozen Stage 8.1 hash:     {h_stage81}  (MATCH)")
    print(f"2024 feature matrix hash:  {h_matrix}  (MATCH)\n")

    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)
    model_stage81 = joblib.load(FROZEN_STAGE81_MODEL_PATH)
    candidate_f_features = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]

    components = rfe.build_components()
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))

    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    origins = sorted(df["forecast_start"].unique())

    results = {}
    t_start = time.time()
    n_normal = 0
    for i, origin in enumerate(origins):
        origin_str = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)

        st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
        st_k = StationState(
            timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
            diesel_running=True, diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )
        initial_e_wh = 160000.0

        origin_rows_all = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        actual_solar_w = [pv_from_sw_in(v) for v in origin_rows_all["actual_SW_IN"].values]

        # Shared wind/demand (baseline-persistence), identical for both arms -- same pattern
        # used throughout R1/R2/the prior replay report.
        shared_bundle = baseline_engine.predict(st_k, {})
        wind_gen = shared_bundle.wind_generation
        demand_fc = shared_bundle.demand

        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        critical_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]

        timestamps = [(origin + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        # --- Frozen Stage 8.1 (37-feature) solar bundle ---
        solar_gen_stage81 = predict_solar_bundle(model_stage81, CANDIDATE_37_FEATURES, origin_rows_all)
        bundle_stage81 = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_stage81, solar_gen_stage81, solar_gen_stage81, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "frozen_stage8_1_corrected"},
            demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"),
        )

        # --- Candidate F (38-feature) solar bundle ---
        solar_gen_f = predict_solar_bundle(
            model_f, candidate_f_features, origin_rows_all,
            extra_feature_fn=lambda d: d["solar_elevation"] * d["cloud_frac"])
        bundle_f = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_f, solar_gen_f, solar_gen_f, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "candidate_F_elevation_x_cloud"},
            demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"),
        )

        origin_result = {}
        for label, bundle in [("stage81_frozen", bundle_stage81), ("candidate_F", bundle_f)]:
            configs = dict(configs_base)
            configs["critical_demand_w"] = critical_demand_w
            configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)

            assessment, route = router.evaluate_and_route(st_k, bundle, configs)
            if route != "NORMAL":
                origin_result[label] = {"route": route}
                continue

            plan = optimizer.optimize(bundle, st_k, configs)  # frozen, unmodified GAP19; never re-called with actual solar
            planned = {
                "constraint_status": plan.constraint_status,
                "planned_diesel_fuel_l": round(sum(
                    (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power), 4),
                "planned_curtailment_wh": arrsum(plan.renewable_curtailment),
                "planned_battery_charge_wh": arrsum(plan.battery_charge),
                "planned_battery_discharge_wh": arrsum(plan.battery_discharge),
            }
            replay = replay_plan_against_actual_solar(
                plan, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
                min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,
            )
            origin_result[label] = {"route": route, "planned": planned, "replay": replay}

        results[origin_str] = origin_result
        if origin_result.get("stage81_frozen", {}).get("route") == "NORMAL":
            n_normal += 1

        if (i + 1) % 50 == 0 or (i + 1) == len(origins):
            print(f"  ... {i+1}/{len(origins)} origins processed ({n_normal} NORMAL) "
                  f"[{round(time.time()-t_start,1)}s elapsed]")

    out_path = THIS_DIR / "CANDIDATE_F_EMS_REPLAY_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "CANDIDATE F EMS REPLAY. RESEARCH-ONLY. Compares the frozen Stage 8.1 "
                "(37-feature) forecast model against the research-only Candidate F "
                "(38-feature, solar_elevation x cloud_frac) model, both feeding the REAL "
                "unmodified GAP19 optimizer, replayed against the same actual-solar ground "
                "truth with the same methodology as ACTUAL_SOLAR_REPLAY_RESULTS.json. GAP19 "
                "was never re-run with actual solar as an input -- actual solar is used only "
                "to evaluate each already-generated plan. No production/config/freeze file "
                "modified. Candidate F is a research-only artifact; this is not a "
                "production/deployment comparison."
            ),
            "hashes": {"candidate_F_model": h_f, "frozen_stage81_model": h_stage81, "matrix_2024": h_matrix},
            "num_origins": len(origins), "num_normal": n_normal,
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {round(time.time() - t_start, 1)}s")
    print("CANDIDATE F EMS REPLAY COMPLETE. No production/config/freeze file modified.")


if __name__ == "__main__":
    main()
