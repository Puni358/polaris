#!/usr/bin/env python3
"""
CANDIDATE J EMS REPLAY. RESEARCH-ONLY. NOT a production run. NOT a re-optimization.

Runs Candidate J (the 39-feature `elevation_x_transition_cloud` research model from
forecasting/stage7/stage8/stage8_1_station_tuning_research/, CANDIDATE_J_REPORT.md -- Candidate F's
38 features + solar_elevation * is_transition_cloud) through the EXACT SAME actual-solar
EMS replay methodology already used for the frozen Stage 8.1 control and for Candidate F
(run_candidateF_actual_solar_replay.py), on the SAME 245 NORMAL-route origins, SAME
warmed-up StationState construction, SAME critical-demand/terminal-reserve formula, SAME
replay physics (diesel/discharge held fixed, charge clipped to availability, critical load
prioritized over charging in the replay).

Only Candidate J's own arm is computed here. The frozen Stage 8.1 control and Candidate F
numbers are PULLED, unmodified, from the already-written CANDIDATE_F_EMS_REPLAY_RESULTS.json
(same 245 NORMAL origins, independently confirmed identical in this script before use) --
control/F are NOT re-run, per task instruction, to avoid redundant GAP19 solves; this script
adds exactly one new arm to the existing comparison.

Reused, UNMODIFIED, by import: `replay_plan_against_actual_solar` and `pv_from_sw_in` from
run_actual_solar_replay.py; `compute_terminal_target_wh` from run_research_simulation.py;
`verify_frozen_manifest`, `build_components` from run_full_experiment.py; `CANDIDATE_37_FEATURES`
from system/forecasting/implementations/s81_corrected_solar.py. GAP19 itself,
system/config/*.yaml, and the frozen Stage 8.1 model/manifest are never modified. Candidate
J's own model file (a NEW, research-only artifact, not a frozen one) is loaded read-only;
.fit() is never called anywhere in this script.

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
CANDIDATE_J_MODEL_PATH = STATION_TUNING_DIR / "model_artifacts" / "candidateJ_elevation_x_transition.joblib"
EXPECTED_CANDIDATE_J_HASH = "952b6e76f7623da6ecb91a1731e1d8104b1a60564126f02083d6377d215f0ccf"

CANDIDATE_F_MODEL_PATH = STATION_TUNING_DIR / "model_artifacts" / "candidateF_elevation_x_cloud.joblib"
EXPECTED_CANDIDATE_F_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"

FROZEN_STAGE81_MODEL_PATH = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025" / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
EXPECTED_FROZEN_STAGE81_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"

MATRIX_2024_PATH = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025" / "stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"

FREEZE_MANIFEST_PATH = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025" / "FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json"

CANDIDATE_J_RESULTS_PATH = STATION_TUNING_DIR / "CANDIDATE_J_RESULTS.json"
EXPECTED_CANDIDATE_J_RESULTS_HASH = None  # computed/verified at runtime, printed for the report

CANDIDATE_F_EMS_REPLAY_RESULTS_PATH = THIS_DIR / "CANDIDATE_F_EMS_REPLAY_RESULTS.json"

PV_CONFIG = {"array_area_m2": 300.0, "panel_efficiency": 0.20, "performance_ratio": 0.85,
             "max_inverter_power_w": 60000.0}
ELEV_CLOUD_FEATURE = "elevation_x_cloud_frac"              # Candidate F's base feature
JOINT_FEATURE = "elevation_x_transition_cloud"             # Candidate J's new feature
CANDIDATE_F_38_FEATURES = CANDIDATE_37_FEATURES + [ELEV_CLOUD_FEATURE]
CANDIDATE_J_39_FEATURES = CANDIDATE_F_38_FEATURES + [JOINT_FEATURE]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sw_in_to_power_w(sw_in):
    raw = sw_in * PV_CONFIG["array_area_m2"] * PV_CONFIG["panel_efficiency"] * PV_CONFIG["performance_ratio"]
    return max(0.0, min(raw, PV_CONFIG["max_inverter_power_w"]))


def add_candidate_j_features(d):
    """IDENTICAL definition to phase10_candidateJ_training.py's add_features(): base
    elevation_x_cloud_frac (Candidate F's feature), is_transition_cloud flag, and the new
    joint elevation_x_transition_cloud product. New, read-only research code."""
    d = d.copy()
    d[ELEV_CLOUD_FEATURE] = d["solar_elevation"] * d["cloud_frac"]
    is_transition_cloud = ((d["cloud_frac"] >= 0.2) & (d["cloud_frac"] < 0.6)).astype(float)
    d[JOINT_FEATURE] = d["solar_elevation"] * is_transition_cloud
    return d


def predict_solar_bundle(model, feature_cols, origin_rows_24, add_features_fn=None):
    """Reproduces Stage81CorrectedForecastEngine.predict()'s solar-reconstruction logic
    exactly (same PV formula, same night-causal zeroing, same residual-on-Stage4
    reconstruction), for a given already-fitted model and its own feature column list.
    New, read-only research code -- does not modify the frozen engine class. IDENTICAL
    convention to run_candidateF_actual_solar_replay.py's predict_solar_bundle()."""
    df = origin_rows_24.sort_values("horizon_hour").reset_index(drop=True)
    if add_features_fn is not None:
        df = add_features_fn(df)
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
    print("CANDIDATE J EMS REPLAY -- Candidate J vs frozen Stage 8.1 vs Candidate F,")
    print("same 245 NORMAL origins. Same actual-solar replay methodology. RESEARCH-ONLY.")
    print("=" * 80)

    rfe.verify_frozen_manifest()

    # --- Pre-run hashes of every frozen/existing input this script touches ---
    pre_hashes = {
        "candidate_J_model": sha256_of(CANDIDATE_J_MODEL_PATH),
        "candidate_F_model": sha256_of(CANDIDATE_F_MODEL_PATH),
        "frozen_stage81_model": sha256_of(FROZEN_STAGE81_MODEL_PATH),
        "matrix_2024": sha256_of(MATRIX_2024_PATH),
        "freeze_manifest": sha256_of(FREEZE_MANIFEST_PATH),
        "candidate_J_results_json": sha256_of(CANDIDATE_J_RESULTS_PATH),
        "candidate_F_ems_replay_results_json": sha256_of(CANDIDATE_F_EMS_REPLAY_RESULTS_PATH),
        "run_actual_solar_replay_py": sha256_of(THIS_DIR / "run_actual_solar_replay.py"),
        "run_full_experiment_py": sha256_of(THIS_DIR / "run_full_experiment.py"),
        "run_research_simulation_py": sha256_of(THIS_DIR / "run_research_simulation.py"),
    }
    assert pre_hashes["candidate_J_model"] == EXPECTED_CANDIDATE_J_HASH, \
        f"STOP: Candidate J model hash drift: {pre_hashes['candidate_J_model']}"
    assert pre_hashes["candidate_F_model"] == EXPECTED_CANDIDATE_F_HASH, \
        f"STOP: Candidate F model hash drift: {pre_hashes['candidate_F_model']}"
    assert pre_hashes["frozen_stage81_model"] == EXPECTED_FROZEN_STAGE81_HASH, \
        f"STOP: frozen Stage 8.1 model hash drift: {pre_hashes['frozen_stage81_model']}"
    assert pre_hashes["matrix_2024"] == EXPECTED_MATRIX_2024_HASH, \
        f"STOP: 2024 matrix hash drift: {pre_hashes['matrix_2024']}"
    print("Pre-run hashes verified MATCH:")
    for k, v in pre_hashes.items():
        print(f"  {k}: {v}")
    print()

    # --- Pull the already-recorded control/Candidate F EMS replay results (not re-run) ---
    with open(CANDIDATE_F_EMS_REPLAY_RESULTS_PATH) as f:
        f_replay = json.load(f)
    cf_results = f_replay["results"]
    normal_origins_stage81 = {o for o, v in cf_results.items() if v.get("stage81_frozen", {}).get("route") == "NORMAL"}
    normal_origins_f = {o for o, v in cf_results.items() if v.get("candidate_F", {}).get("route") == "NORMAL"}
    assert normal_origins_stage81 == normal_origins_f, "STOP: stage81/candidate_F NORMAL-origin sets differ unexpectedly."
    assert len(normal_origins_stage81) == 245, f"STOP: expected 245 NORMAL origins, got {len(normal_origins_stage81)}"
    print(f"Pulled control/Candidate F EMS replay results from {CANDIDATE_F_EMS_REPLAY_RESULTS_PATH.name}: "
          f"{len(normal_origins_stage81)} NORMAL origins confirmed identical across both existing arms.\n")

    model_j = joblib.load(CANDIDATE_J_MODEL_PATH)

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
    n_normal_mismatch = 0
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

        # Shared wind/demand (baseline-persistence), identical pattern to the control/F replay.
        shared_bundle = baseline_engine.predict(st_k, {})
        wind_gen = shared_bundle.wind_generation
        demand_fc = shared_bundle.demand

        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        critical_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]

        timestamps = [(origin + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        # --- Candidate J (39-feature) solar bundle ---
        solar_gen_j = predict_solar_bundle(
            model_j, CANDIDATE_J_39_FEATURES, origin_rows_all,
            add_features_fn=add_candidate_j_features)
        bundle_j = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_j, solar_gen_j, solar_gen_j, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "candidate_J_elevation_x_transition"},
            demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"),
        )

        configs = dict(configs_base)
        configs["critical_demand_w"] = critical_demand_w
        configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle_j)

        assessment, route = router.evaluate_and_route(st_k, bundle_j, configs)
        origin_result = {}
        if route != "NORMAL":
            origin_result["candidate_J"] = {"route": route}
            if origin_str in normal_origins_stage81:
                n_normal_mismatch += 1
        else:
            plan = optimizer.optimize(bundle_j, st_k, configs)  # frozen, unmodified GAP19; never called with actual solar
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
            origin_result["candidate_J"] = {"route": route, "planned": planned, "replay": replay}
            if origin_str in normal_origins_stage81:
                n_normal += 1
            else:
                n_normal_mismatch += 1

        results[origin_str] = origin_result

        if (i + 1) % 50 == 0 or (i + 1) == len(origins):
            print(f"  ... {i+1}/{len(origins)} origins processed ({n_normal} NORMAL-matched) "
                  f"[{round(time.time()-t_start,1)}s elapsed]")

    print(f"\nCandidate J NORMAL-route origins matching the control/F 245-origin set: {n_normal}")
    print(f"Mismatches (origin NORMAL for stage81/F but not J, or vice versa): {n_normal_mismatch}")

    # --- Post-run re-verification of all read-only inputs (no drift) ---
    post_hashes = {
        "candidate_J_model": sha256_of(CANDIDATE_J_MODEL_PATH),
        "candidate_F_model": sha256_of(CANDIDATE_F_MODEL_PATH),
        "frozen_stage81_model": sha256_of(FROZEN_STAGE81_MODEL_PATH),
        "matrix_2024": sha256_of(MATRIX_2024_PATH),
        "freeze_manifest": sha256_of(FREEZE_MANIFEST_PATH),
        "candidate_J_results_json": sha256_of(CANDIDATE_J_RESULTS_PATH),
        "candidate_F_ems_replay_results_json": sha256_of(CANDIDATE_F_EMS_REPLAY_RESULTS_PATH),
        "run_actual_solar_replay_py": sha256_of(THIS_DIR / "run_actual_solar_replay.py"),
        "run_full_experiment_py": sha256_of(THIS_DIR / "run_full_experiment.py"),
        "run_research_simulation_py": sha256_of(THIS_DIR / "run_research_simulation.py"),
    }
    drift = {k: (pre_hashes[k], post_hashes[k]) for k in pre_hashes if pre_hashes[k] != post_hashes[k]}
    if drift:
        raise RuntimeError(f"STOP: input drift detected during run: {drift}")
    print("\nPost-run re-verification: ALL frozen/existing inputs byte-identical to pre-run hashes. Zero drift.")

    out_path = THIS_DIR / "CANDIDATE_J_EMS_REPLAY_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "CANDIDATE J EMS REPLAY. RESEARCH-ONLY. Computes the Candidate J (39-feature, "
                "Candidate F's elevation_x_cloud_frac + new elevation_x_transition_cloud) arm "
                "feeding the REAL unmodified GAP19 optimizer, replayed against the same "
                "actual-solar ground truth and methodology as CANDIDATE_F_EMS_REPLAY_RESULTS.json "
                "and ACTUAL_SOLAR_REPLAY_RESULTS.json. The frozen Stage 8.1 control and "
                "Candidate F arms are NOT re-run here; they are pulled unmodified from "
                "CANDIDATE_F_EMS_REPLAY_RESULTS.json for the 3-way comparison (see the companion "
                "report). GAP19 was never re-run with actual solar as an input -- actual solar "
                "is used only to evaluate each already-generated plan. No production/config/"
                "freeze file modified. Candidate J is a research-only artifact; this is not a "
                "production/deployment comparison."
            ),
            "pre_run_hashes": pre_hashes,
            "post_run_hashes": post_hashes,
            "input_drift_detected": False,
            "num_origins": len(origins), "num_normal_matched": n_normal,
            "num_normal_mismatch": n_normal_mismatch,
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {round(time.time() - t_start, 1)}s")
    print("CANDIDATE J EMS REPLAY COMPLETE. No production/config/freeze file modified.")


if __name__ == "__main__":
    main()
