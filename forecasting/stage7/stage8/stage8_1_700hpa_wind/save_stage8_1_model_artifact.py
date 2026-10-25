#!/usr/bin/env python3
"""
POLARIS STAGE 8.1 — MODEL ARTIFACT RECONSTRUCTION & SERIALIZATION
====================================================================
This file is a byte-identical copy of the original, unmodified
`run_official_odd_evaluation.py` (the authoritative Stage 8.1 ODD evaluation
script) through every data-loading, feature-construction, EVEN/ODD-split,
target-construction, and model-fitting step. NOTHING in that logic has been
changed: same files, same merges, same 37/35-feature contracts, same split,
same target (residual-on-Stage4), same HistGradientBoostingRegressor
hyperparameters, same random_state=42.

The ONLY addition (clearly marked "ARTIFACT SERIALIZATION ADDITION" below) is
code appended AFTER the original script's two model.fit() calls to persist
the fitted Stage 8.1 "candidate" (37-feature) estimator to disk via joblib,
record its SHA-256, write a feature/split/provenance manifest, and
independently re-verify that loading the saved artifact back and predicting
on the exact same held-out ODD feature matrix reproduces the exact same
predictions already written to stage8_1_official_odd_predictions.csv.

This exists ONLY because the original Stage 8.1 pipeline never itself called
joblib.dump/pickle on the fitted estimator (confirmed by repo-wide search —
no serialized Stage 8.1 model artifact existed anywhere). This script does
not create a "new" or "improved" Stage 8.1 model: it is the SAME fit, on the
SAME data, SAME features, SAME split, SAME hyperparameters as the original,
merely captured to disk afterward. It reproduced the authoritative ODD
metrics (MAE=36.188657, nMAE=28.0688%, RMSE=64.219495, bias=+1.439399) and
the exact byte-identical predictions CSV (SHA-256 213a71e1...) before any
serialization code ran.
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# PATHS
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE7_5_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
FEATURES_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"

# Output Artifacts (original, unmodified)
ODD_PREDS_PATH = STAGE_DIR / "stage8_1_official_odd_predictions.csv"
ODD_RESULTS_PATH = STAGE_DIR / "stage8_1_official_odd_results.json"
ODD_BOOTSTRAP_PATH = STAGE_DIR / "stage8_1_official_odd_bootstrap.json"
ODD_AUDIT_PATH = STAGE_DIR / "stage8_1_official_odd_audit.json"
ODD_REPORT_PATH = STAGE_DIR / "STAGE8_1_OFFICIAL_ODD_REPORT.md"
ODD_REPRO_PATH = STAGE_DIR / "STAGE8_1_OFFICIAL_ODD_REPRODUCIBILITY.md"

# New artifact-serialization outputs (this script only)
ARTIFACT_DIR = STAGE_DIR / "model_artifact"
MODEL_ARTIFACT_PATH = ARTIFACT_DIR / "stage8_1_candidate_37feature_model.joblib"
MANIFEST_PATH = ARTIFACT_DIR / "STAGE8_1_MODEL_RECONSTRUCTION_MANIFEST.json"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("odd_eval")

def atomic_write_json(obj, file_path: Path):
    tmp_path = file_path.with_suffix(".tmp.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp_path, file_path)

def run_odd_evaluation():
    logger.info("==================================================")
    logger.info("[STAGE 8.1] STARTING OFFICIAL ODD EVALUATION")
    logger.info("==================================================")

    # 1. Load Datasets
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"], utc=True)
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"], utc=True)

    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["timestamp"] = pd.to_datetime(df_nwp["timestamp"], utc=True)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)

    df_sites = pd.read_csv(SITES_PATH)
    df_sites["timestamp"] = pd.to_datetime(df_sites["TIMESTAMP"], utc=True)

    df_cs = pd.read_csv(CLEARSKY_PATH)
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)

    df_66 = pd.read_csv(STAGE6_6_FEAT_PATH)
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)

    df_75 = pd.read_csv(STAGE7_5_FEAT_PATH)
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)

    df_wind = pd.read_csv(FEATURES_PATH)
    df_wind["forecast_start"] = pd.to_datetime(df_wind["forecast_start"], utc=True)
    df_wind["valid_time"] = pd.to_datetime(df_wind["valid_time"], utc=True)

    df = s4_preds.copy()
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0

    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]
    df = df.merge(df_cs[cs_cols], on="timestamp", how="left")

    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]

    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    df = df.merge(df_75[terrain_cols], on="timestamp", how="left")

    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df = df.merge(df_wind[wind_cols], on=["forecast_start", "horizon_hour"], how="left")

    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["is_daytime"] = df["actual_SW_IN"] > 0
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)

    # Globally Frozen Stage 4 Features
    with open(STAGE4_PARAMS_PATH) as f:
        ensemble_params_full = json.load(f)

    phys_preds_full = []
    for idx, row in df.iterrows():
        h = str(int(row["horizon_hour"]))
        p = ensemble_params_full[h]
        k_h = p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        phys_preds_full.append(phys)

    df["phys_pred_fold"] = phys_preds_full
    df["pred_stage4_fold"] = df["pred_ensemble"]
    df["disagreement_fold"] = (df["pred_stage3b_cloud_nwp"] - df["phys_pred_fold"]).abs()

    base_28_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]

    all_origins = sorted(df["forecast_start"].unique())
    ctx_feature_rows = []
    for origin_ts in all_origins:
        context_start = origin_ts - pd.Timedelta(hours=24)
        ctx_sites = df_sites[(df_sites["timestamp"] >= context_start) & (df_sites["timestamp"] < origin_ts)].sort_values("timestamp")

        if len(ctx_sites) < 24:
            ctx_feature_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue

        sw_vals = ctx_sites["SW_IN"].values
        s3, s6, s12, s24 = sw_vals[-3:], sw_vals[-6:], sw_vals[-12:], sw_vals[-24:]

        std_3h = np.std(s3) if len(s3) > 1 else 0.0
        std_6h = np.std(s6) if len(s6) > 1 else 0.0
        std_12h = np.std(s12) if len(s12) > 1 else 0.0
        std_24h = np.std(s24) if len(s24) > 1 else 0.0

        abs_chg_1h = abs(sw_vals[-1] - sw_vals[-2]) if len(sw_vals) >= 2 else 0.0
        abs_chg_3h = abs(sw_vals[-1] - sw_vals[-4]) if len(sw_vals) >= 4 else 0.0
        abs_chg_6h = abs(sw_vals[-1] - sw_vals[-7]) if len(sw_vals) >= 7 else 0.0

        diffs_6h = np.abs(np.diff(s6)) if len(s6) > 1 else [0.0]
        max_diff_6h = np.max(diffs_6h)
        mean_diff_6h = np.mean(diffs_6h)
        slope_6h = np.polyfit(np.arange(len(s6)), s6, 1)[0] if len(s6) >= 3 else 0.0

        ctx_cs = df_cs[(df_cs["timestamp"] >= context_start) & (df_cs["timestamp"] < origin_ts)].sort_values("timestamp")
        if len(ctx_cs) == len(ctx_sites):
            cs_ghi_vals = ctx_cs["clearsky_ghi"].values
            valid_cs = cs_ghi_vals > 10.0
            kt_vals = np.zeros_like(sw_vals)
            kt_vals[valid_cs] = np.clip(sw_vals[valid_cs] / cs_ghi_vals[valid_cs], 0.0, 1.5)
            kt_std_6h = np.std(kt_vals[-6:]) if len(kt_vals) >= 6 else 0.0
        else:
            kt_std_6h = 0.0

        ctx_feature_rows.append({
            "forecast_start": origin_ts,
            "ctx_std_3h": std_3h, "ctx_std_6h": std_6h, "ctx_std_12h": std_12h, "ctx_std_24h": std_24h,
            "ctx_abs_change_1h": abs_chg_1h, "ctx_abs_change_3h": abs_chg_3h, "ctx_abs_change_6h": abs_chg_6h,
            "ctx_max_diff_6h": max_diff_6h, "ctx_mean_diff_6h": mean_diff_6h, "ctx_slope_6h": slope_6h,
            "ctx_kt_std_6h": kt_std_6h, "ctx_last_obs": sw_vals[-1],
            "ctx_mean_24h": np.mean(s24), "ctx_max_24h": np.max(s24)
        })

    ctx_df = pd.DataFrame(ctx_feature_rows)
    df = df.merge(ctx_df, on="forecast_start", how="left")

    stage66_31_features = base_28_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    stage75_35_features = stage66_31_features + ["terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    candidate_37_features = stage75_35_features + ["u700", "v700"]

    # 2. Split EVEN / ODD
    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    odd_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 1]

    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    df_odd = df[df["forecast_start"].isin(odd_origins)].copy()

    logger.info(f"Total Origins: {len(all_origins)} | EVEN (Train/Calib): {len(even_origins)} | ODD (Held-Out Test): {len(odd_origins)}")
    logger.info(f"ODD Hours Total: {len(df_odd)} | Daytime: {df_odd['is_daytime'].sum()} | Night: {(~df_odd['is_daytime']).sum()}")

    # Daylight subsets
    even_day = df_even[df_even["is_daytime"]].copy()
    odd_day = df_odd[df_odd["is_daytime"]].copy()

    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values

    # 3. Fit Stage 7.5 Champion (35 features)
    X_tr_st75 = even_day[stage75_35_features].values
    X_odd_st75 = odd_day[stage75_35_features].values

    model_st75 = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_st75.fit(X_tr_st75, res_tr)
    pred_res_st75 = model_st75.predict(X_odd_st75)
    pred_sw_st75_day = np.maximum(0.0, st4_odd + pred_res_st75)
    pred_sw_st75_day[odd_day["is_night_causal"].values] = 0.0

    # 4. Fit Stage 8.1 Candidate (37 features)
    X_tr_e1 = even_day[candidate_37_features].values
    X_odd_e1 = odd_day[candidate_37_features].values

    model_e1 = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_e1.fit(X_tr_e1, res_tr)
    pred_res_e1 = model_e1.predict(X_odd_e1)
    pred_sw_e1_day = np.maximum(0.0, st4_odd + pred_res_e1)
    pred_sw_e1_day[odd_day["is_night_causal"].values] = 0.0

    # ===================== ARTIFACT SERIALIZATION ADDITION =====================
    # Persist the fitted Stage 8.1 candidate (37-feature) estimator -- this is the
    # SAME object just fit above with the original, unmodified feature matrix,
    # target, split, and hyperparameters. No refitting, no new data, no changed
    # features. This exists solely because the original pipeline never itself
    # serialized the model (confirmed missing by prior repo-wide search).
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_e1, MODEL_ARTIFACT_PATH)

    def _sha256_file(p: Path) -> str:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            while chunk := fh.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def _sha256_bytes(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()

    model_artifact_sha256 = _sha256_file(MODEL_ARTIFACT_PATH)

    # Independent re-verification: load the just-saved artifact back from disk
    # (fresh object, not the in-memory model_e1) and re-predict on the exact same
    # held-out ODD feature matrix. This must reproduce pred_sw_e1_day exactly,
    # or the "artifact round-trips to identical predictions" claim is false.
    reloaded_model_e1 = joblib.load(MODEL_ARTIFACT_PATH)
    reloaded_pred_res_e1 = reloaded_model_e1.predict(X_odd_e1)
    reloaded_pred_sw_e1_day = np.maximum(0.0, st4_odd + reloaded_pred_res_e1)
    reloaded_pred_sw_e1_day[odd_day["is_night_causal"].values] = 0.0
    artifact_roundtrip_identical = bool(np.array_equal(pred_sw_e1_day, reloaded_pred_sw_e1_day))

    reloaded_mae = float(mean_absolute_error(y_odd, reloaded_pred_sw_e1_day))
    reloaded_rmse = float(np.sqrt(mean_squared_error(y_odd, reloaded_pred_sw_e1_day)))
    reloaded_bias = float(np.mean(reloaded_pred_sw_e1_day - y_odd))
    reloaded_nmae = float((reloaded_mae / np.mean(y_odd)) * 100.0)
    # ============================================================================

    # 5. Full ODD Prediction Dataframe
    df_odd_preds = df_odd[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "is_daytime", "is_night_causal"]].copy()
    df_odd_preds["pred_stage7_5_control"] = 0.0
    df_odd_preds.loc[df_odd_preds["is_daytime"], "pred_stage7_5_control"] = pred_sw_st75_day

    df_odd_preds["pred_stage8_1_candidate"] = 0.0
    df_odd_preds.loc[df_odd_preds["is_daytime"], "pred_stage8_1_candidate"] = pred_sw_e1_day

    df_odd_preds.to_csv(ODD_PREDS_PATH, index=False)

    # 6. Calculate Daytime ODD Metrics
    mean_y_odd = np.mean(y_odd)

    # Control (Stage 7.5)
    mae_st75 = float(mean_absolute_error(y_odd, pred_sw_st75_day))
    nmae_st75 = float((mae_st75 / mean_y_odd) * 100.0)
    rmse_st75 = float(np.sqrt(mean_squared_error(y_odd, pred_sw_st75_day)))
    bias_st75 = float(np.mean(pred_sw_st75_day - y_odd))

    # Candidate (Stage 8.1)
    mae_e1 = float(mean_absolute_error(y_odd, pred_sw_e1_day))
    nmae_e1 = float((mae_e1 / mean_y_odd) * 100.0)
    rmse_e1 = float(np.sqrt(mean_squared_error(y_odd, pred_sw_e1_day)))
    bias_e1 = float(np.mean(pred_sw_e1_day - y_odd))

    # Night MAE
    odd_night = df_odd[~df_odd["is_daytime"]]
    night_mae_st75 = float(mean_absolute_error(odd_night["actual_SW_IN"], df_odd_preds.loc[~df_odd_preds["is_daytime"], "pred_stage7_5_control"]))
    night_mae_e1 = float(mean_absolute_error(odd_night["actual_SW_IN"], df_odd_preds.loc[~df_odd_preds["is_daytime"], "pred_stage8_1_candidate"]))

    # Deltas
    delta_mae = mae_e1 - mae_st75
    delta_nmae = nmae_e1 - nmae_st75
    delta_rmse = rmse_e1 - rmse_st75
    delta_bias = bias_e1 - bias_st75

    repro_pass = bool(abs(mae_st75 - 36.613571) < 1e-3 and abs(nmae_st75 - 28.3983) < 1e-2)

    logger.info("\n==================================================")
    logger.info("STAGE 7.5 FROZEN CONTROL ODD METRICS:")
    logger.info(f"MAE:       {mae_st75:.6f} W/m² (Expected: 36.613571 W/m²)")
    logger.info(f"nMAE:      {nmae_st75:.4f}% (Expected: 28.3983%)")
    logger.info(f"RMSE:      {rmse_st75:.6f} W/m² (Expected: 65.347064 W/m²)")
    logger.info(f"Bias:      {bias_st75:+.6f} W/m² (Expected: +1.307778 W/m²)")
    logger.info(f"Night MAE: {night_mae_st75:.6f} W/m²")
    logger.info(f"Control Reproduction Pass: {repro_pass}")

    logger.info("\n==================================================")
    logger.info("STAGE 8.1 CANDIDATE ODD METRICS (U700 + V700):")
    logger.info(f"MAE:       {mae_e1:.6f} W/m²")
    logger.info(f"nMAE:      {nmae_e1:.4f}%")
    logger.info(f"RMSE:      {rmse_e1:.6f} W/m²")
    logger.info(f"Bias:      {bias_e1:+.6f} W/m²")
    logger.info(f"Night MAE: {night_mae_e1:.6f} W/m²")

    logger.info("\n==================================================")
    logger.info("DELTAS (Stage 8.1 Candidate - Stage 7.5 Control):")
    logger.info(f"ΔMAE:      {delta_mae:+.6f} W/m²")
    logger.info(f"ΔnMAE:     {delta_nmae:+.4f} pp")
    logger.info(f"ΔRMSE:     {delta_rmse:+.6f} W/m²")
    logger.info(f"ΔBias:     {delta_bias:+.6f} W/m²")

    # 7. Paired Origin-Level Bootstrap (10,000 resamples, seed=42)
    logger.info("\nRunning 10,000 paired origin-level bootstrap resamples (seed=42)...")
    np.random.seed(42)

    odd_day_df = df_odd[df_odd["is_daytime"]].copy()
    odd_day_df["pred_st75"] = pred_sw_st75_day
    odd_day_df["pred_e1"] = pred_sw_e1_day

    unique_odd_origs = np.array(odd_origins)
    n_odd_origs = len(unique_odd_origs)
    bootstrap_deltas = []

    # Map origins to dataframe indices for ultra-fast sampling
    orig_grouped = {orig: group.index.values for orig, group in odd_day_df.groupby("forecast_start")}

    for b in range(10000):
        sampled_origs = np.random.choice(unique_odd_origs, size=n_odd_origs, replace=True)
        sampled_indices = np.concatenate([orig_grouped[o] for o in sampled_origs if o in orig_grouped])

        b_sub = odd_day_df.loc[sampled_indices]
        b_y = b_sub["actual_SW_IN"].values
        b_p_st75 = b_sub["pred_st75"].values
        b_p_e1 = b_sub["pred_e1"].values

        b_mae_st75 = mean_absolute_error(b_y, b_p_st75)
        b_mae_e1 = mean_absolute_error(b_y, b_p_e1)
        bootstrap_deltas.append(b_mae_e1 - b_mae_st75)

    bootstrap_deltas = np.array(bootstrap_deltas)
    mean_bs_delta = float(np.mean(bootstrap_deltas))
    ci_lower = float(np.percentile(bootstrap_deltas, 2.5))
    ci_upper = float(np.percentile(bootstrap_deltas, 97.5))
    frac_lt_0 = float(np.mean(bootstrap_deltas < 0.0))

    logger.info(f"Bootstrap Mean ΔMAE: {mean_bs_delta:+.6f} W/m²")
    logger.info(f"95% CI: [{ci_lower:+.6f}, {ci_upper:+.6f}] W/m²")
    logger.info(f"Fraction ΔMAE < 0: {frac_lt_0:.4f}")

    is_improvement = bool(delta_mae < 0.0)
    final_status = "NEW OFFICIAL OPERATIONAL CHAMPION" if is_improvement else "STAGE 7.5 REMAINS OPERATIONAL CHAMPION"

    results_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "STAGE 8.1 700 hPa STEERING WIND EXPERIMENT",
        "evaluation": "OFFICIAL_HELD_OUT_ODD_EVALUATION",
        "status": final_status,
        "control_source": "stage4_results/ensemble_predictions.csv (pred_ensemble)",
        "stage4_refit_executed": False,
        "control_reproduction": {
            "expected_mae_w_m2": 36.613571,
            "actual_mae_w_m2": round(mae_st75, 6),
            "pass": repro_pass
        },
        "odd_counts": {
            "origins": len(odd_origins),
            "forecast_hours": len(df_odd),
            "daytime_rows": int(len(odd_day)),
            "night_rows": int(len(odd_night))
        },
        "stage7_5_control": {
            "daytime_mae_w_m2": round(mae_st75, 6),
            "daytime_nmae_pct": round(nmae_st75, 4),
            "daytime_rmse_w_m2": round(rmse_st75, 6),
            "daytime_bias_w_m2": round(bias_st75, 6),
            "night_mae_w_m2": round(night_mae_st75, 6)
        },
        "stage8_1_candidate": {
            "daytime_mae_w_m2": round(mae_e1, 6),
            "daytime_nmae_pct": round(nmae_e1, 4),
            "daytime_rmse_w_m2": round(rmse_e1, 6),
            "daytime_bias_w_m2": round(bias_e1, 6),
            "night_mae_w_m2": round(night_mae_e1, 6)
        },
        "deltas": {
            "delta_mae_w_m2": round(delta_mae, 6),
            "delta_nmae_pp": round(delta_nmae, 4),
            "delta_rmse_w_m2": round(delta_rmse, 6),
            "delta_bias_w_m2": round(delta_bias, 6)
        },
        "bootstrap": {
            "n_resamples": 10000,
            "seed": 42,
            "mean_delta_mae_w_m2": round(mean_bs_delta, 6),
            "ci_95_lower_w_m2": round(ci_lower, 6),
            "ci_95_upper_w_m2": round(ci_upper, 6),
            "fraction_delta_mae_lt_0": round(frac_lt_0, 4)
        },
        "governance_audit": {
            "odd_target_accessed": True,
            "odd_predictions_generated": True,
            "odd_metrics_evaluated": True,
            "odd_used_for_tuning": False,
            "odd_used_for_feature_selection": False,
            "odd_used_for_hyperparameter_tuning": False
        }
    }

    atomic_write_json(results_payload, ODD_RESULTS_PATH)

    bootstrap_payload = {
        "n_resamples": 10000,
        "seed": 42,
        "mean_delta_mae": round(mean_bs_delta, 6),
        "ci_95_lower": round(ci_lower, 6),
        "ci_95_upper": round(ci_upper, 6),
        "fraction_lt_0": round(frac_lt_0, 4),
        "sample_deltas_first_10": [round(x, 6) for x in bootstrap_deltas[:10]]
    }
    atomic_write_json(bootstrap_payload, ODD_BOOTSTRAP_PATH)

    audit_payload = {
        "control_source_verified": True,
        "stage4_refit_executed": False,
        "causality_verified": True,
        "row_alignment_verified": True,
        "feature_count_verified": True,
        "leakage_audit_pass": True,
        "odd_isolation_pass": True,
        "bootstrap_audit_pass": True,
        "overall_integrity": "PASS"
    }
    atomic_write_json(audit_payload, ODD_AUDIT_PATH)

    logger.info("==================================================")
    logger.info(f"FINAL DECISION: {final_status}")
    logger.info("==================================================")

    # ===================== ARTIFACT SERIALIZATION ADDITION =====================
    logger.info("\n==================================================")
    logger.info("MODEL ARTIFACT SERIALIZATION & ROUND-TRIP VERIFICATION")
    logger.info("==================================================")
    logger.info(f"Model artifact saved to: {MODEL_ARTIFACT_PATH}")
    logger.info(f"Model artifact SHA-256:  {model_artifact_sha256}")
    logger.info(f"Round-trip identical predictions (reloaded artifact vs in-memory fit): {artifact_roundtrip_identical}")
    logger.info(f"Reloaded-artifact MAE={reloaded_mae:.6f} RMSE={reloaded_rmse:.6f} bias={reloaded_bias:+.6f} nMAE={reloaded_nmae:.4f}%")
    logger.info(f"Matches authoritative candidate MAE exactly: {abs(reloaded_mae - mae_e1) < 1e-12}")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Reconstruction/serialization of the frozen Stage 8.1 candidate (37-feature) model artifact. "
                   "The original run_official_odd_evaluation.py never persisted a model artifact; this file "
                   "captures the SAME fit (identical data/features/split/target/hyperparameters) to disk.",
        "source_script_unmodified_through_fit": "run_official_odd_evaluation.py (byte-identical up to and including model_e1.fit())",
        "model_definition": {
            "estimator": "sklearn.ensemble.HistGradientBoostingRegressor",
            "loss": "absolute_error",
            "max_depth": 4,
            "min_samples_leaf": 30,
            "l2_regularization": 10.0,
            "random_state": 42,
        },
        "target_definition": {
            "description": "Residual regression: y = actual_SW_IN - pred_stage4_fold (Stage4 ensemble physical/cloud base prediction). "
                            "Final forecast = max(0, stage4_base + predicted_residual), clipped to 0 at night (is_night_causal).",
            "daytime_only": True,
        },
        "feature_contract": {
            "count": len(candidate_37_features),
            "ordered_names": candidate_37_features,
        },
        "split_manifest": {
            "method": "EVEN/ODD alternating daily forecast-origin split over all 347 real Nuolja/SITES 2024 origins",
            "total_origins": len(all_origins),
            "train_even_origins": len(even_origins),
            "test_odd_origins": len(odd_origins),
            "train_origins_first5": [str(o) for o in even_origins[:5]],
            "test_origins_first5": [str(o) for o in odd_origins[:5]],
            "train_daytime_rows": int(len(even_day)),
            "test_daytime_rows": int(len(odd_day)),
            "test_night_rows": int(len(odd_night)),
        },
        "dataset_sha256": {
            "sites_multivariate_csv": _sha256_file(SITES_PATH),
            "clearsky_decomposition_csv": _sha256_file(CLEARSKY_PATH),
            "nwp_future_weather_csv": _sha256_file(NWP_PATH),
            "stage4_ensemble_predictions_csv": _sha256_file(STAGE4_PREDS_PATH),
            "stage4_ensemble_parameters_json": _sha256_file(STAGE4_PARAMS_PATH),
            "stage6_6_lwp_iwp_features_csv": _sha256_file(STAGE6_6_FEAT_PATH),
            "stage7_5_terrain_features_csv": _sha256_file(STAGE7_5_FEAT_PATH),
            "stage8_1_extracted_wind_features_csv": _sha256_file(FEATURES_PATH),
        },
        "code_sha256": {
            "run_official_odd_evaluation.py": _sha256_file(STAGE_DIR / "run_official_odd_evaluation.py"),
            "save_stage8_1_model_artifact.py": _sha256_file(Path(__file__).resolve()),
        },
        "model_artifact": {
            "path": str(MODEL_ARTIFACT_PATH),
            "sha256": model_artifact_sha256,
        },
        "reproduction_verification": {
            "authoritative_daytime_mae_w_m2": 36.188657,
            "authoritative_daytime_nmae_pct": 28.0688,
            "authoritative_daytime_rmse_w_m2": 64.219495,
            "authoritative_daytime_bias_w_m2": 1.439399,
            "reproduced_daytime_mae_w_m2": round(mae_e1, 6),
            "reproduced_daytime_nmae_pct": round(nmae_e1, 4),
            "reproduced_daytime_rmse_w_m2": round(rmse_e1, 6),
            "reproduced_daytime_bias_w_m2": round(bias_e1, 6),
            "abs_diff_mae": round(abs(mae_e1 - 36.188657), 8),
            "abs_diff_nmae_pp": round(abs(nmae_e1 - 28.0688), 8),
            "abs_diff_rmse": round(abs(rmse_e1 - 64.219495), 8),
            "abs_diff_bias": round(abs(bias_e1 - 1.439399), 8),
            "predictions_csv_sha256": _sha256_file(ODD_PREDS_PATH),
            "authoritative_predictions_csv_sha256_backup": "213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707",
            "predictions_csv_byte_identical_to_authoritative_backup": _sha256_file(ODD_PREDS_PATH) == "213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707",
            "artifact_roundtrip_identical_predictions": artifact_roundtrip_identical,
            "prediction_count": int(len(y_odd)),
        },
    }
    atomic_write_json(manifest, MANIFEST_PATH)
    logger.info(f"\nReconstruction manifest written to: {MANIFEST_PATH}")
    # ============================================================================

if __name__ == "__main__":
    run_odd_evaluation()
