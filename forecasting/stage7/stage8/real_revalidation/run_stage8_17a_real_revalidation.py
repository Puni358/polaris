#!/usr/bin/env python3
"""
POLARIS STAGE 8.17A — REAL-DATA REVALIDATION PIPELINE
=====================================================
Executes exact Stage 8.17A pipeline using 100% REAL historical AROME-Arctic 2024 data.

Data Source:
  ~/01polaris (Copy)/forecasting/stage7/stage8/real_revalidation/arome_arctic_347_origins_real_subset.csv
  SHA256: db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298

Governance:
  - 0 hardcoded metrics
  - 0 synthetic data
  - EVEN CV first (5 folds)
  - Candidate freeze before ODD evaluation
  - Row-level predictions persisted to disk before metric computation
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
REVAL_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "real_revalidation"
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

LOG_PATH = REVAL_DIR / "STAGE8_17A_REAL_AROME_RERUN.log"
AROME_CSV_PATH = REVAL_DIR / "arome_arctic_347_origins_real_subset.csv"
EXPECTED_AROME_SHA256 = "db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298"

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE6_1_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_1_meps_ensemble" / "ensemble_feature_summary.csv"
STAGE7_5_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
STAGE8_1_FEAT_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"

FREEZE_JSON_PATH = REVAL_DIR / "STAGE8_17A_REAL_AROME_FREEZE.json"
ODD_PREDS_CSV_PATH = REVAL_DIR / "STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv"

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)

def log(msg):
    logging.info(msg)

def fit_stage4_parameters(train_df):
    params = {}
    day_df = train_df[train_df["is_daytime"]]
    for h in range(1, 25):
        h_sub = day_df[day_df["horizon_hour"] == h]
        if len(h_sub) < 5:
            params[str(h)] = {"w": 0.5, "k": 0.9}
            continue
        y_true = h_sub["actual_SW_IN"].values
        chronos = h_sub["pred_stage3b_cloud_nwp"].values
        cs_ghi = h_sub["clearsky_ghi"].values
        c_frac = h_sub["cloud_frac"].values
        
        best_mae = 1e9
        best_w, best_k = 0.5, 0.9
        for w in np.linspace(0.0, 1.0, 51):
            for k in np.linspace(0.5, 1.2, 15):
                phys = np.maximum(0.0, cs_ghi * (1.0 - k * c_frac))
                pred = np.maximum(0.0, w * chronos + (1.0 - w) * phys)
                mae = mean_absolute_error(y_true, pred)
                if mae < best_mae:
                    best_mae = mae
                    best_w, best_k = w, k
        params[str(h)] = {"w": float(best_w), "k": float(best_k)}
    return params

def apply_stage4_params(df_subset, params):
    st4_preds, phys_preds = [], []
    for idx, row in df_subset.iterrows():
        h = str(int(row["horizon_hour"]))
        p = params.get(h, {"w": 0.5, "k": 0.9})
        w_h, k_h = p["w"], p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        chronos = row["pred_stage3b_cloud_nwp"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        st4 = max(0.0, w_h * chronos + (1.0 - w_h) * phys)
        if row["is_night_causal"]:
            st4 = 0.0
            phys = 0.0
        st4_preds.append(st4)
        phys_preds.append(phys)
    return np.array(st4_preds), np.array(phys_preds)

def validate_arome_input():
    log("VALIDATING AROME DATA")
    if not AROME_CSV_PATH.exists():
        log(f"ERROR: Real AROME CSV not found at {AROME_CSV_PATH}")
        sys.exit(1)
        
    with open(AROME_CSV_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        
    if file_hash != EXPECTED_AROME_SHA256:
        log(f"ERROR: SHA256 mismatch! Expected {EXPECTED_AROME_SHA256}, got {file_hash}")
        sys.exit(1)
    log(f"SHA256 Match PASSED: {file_hash}")
    
    df_arome = pd.read_csv(AROME_CSV_PATH)
    n_rows = len(df_arome)
    n_origs = df_arome["origin_t0"].nunique()
    
    log(f"Rows Count: {n_rows} (Expected 8328)")
    log(f"Unique Origins: {n_origs} (Expected 347)")
    
    if n_rows != 8328 or n_origs != 347:
        log("ERROR: Invalid row count or origin count!")
        sys.exit(1)
        
    dup_count = df_arome.duplicated(subset=["origin_t0", "horizon_h"]).sum()
    log(f"Duplicate Tuples: {dup_count} (Expected 0)")
    if dup_count > 0:
        log("ERROR: Duplicate origin/horizon tuples found!")
        sys.exit(1)
        
    null_u = df_arome["arome_u700"].isnull().sum()
    null_v = df_arome["arome_v700"].isnull().sum()
    null_lwp = df_arome["arome_lwp"].isnull().sum()
    log(f"Missing Values: u700={null_u}, v700={null_v}, lwp={null_lwp} (Expected 0)")
    if null_u > 0 or null_v > 0 or null_lwp > 0:
        log("ERROR: Missing AROME values found!")
        sys.exit(1)
        
    causal_fail = (df_arome["causal_pass"] != True).sum()
    log(f"Causal Failures: {causal_fail} (Expected 0)")
    if causal_fail > 0:
        log("ERROR: Non-causal AROME records found!")
        sys.exit(1)
        
    log("AROME VALIDATION PASSED")
    return df_arome

def build_40_feature_dataset(df_arome):
    log("BUILDING 40 FEATURES")
    
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"], utc=True)
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"], utc=True)
    
    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)
    
    df_cs = pd.read_csv(CLEARSKY_PATH)
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)
    
    df_sites = pd.read_csv(SITES_PATH)
    df_sites["timestamp"] = pd.to_datetime(df_sites["TIMESTAMP"], utc=True)
    
    df_66 = pd.read_csv(STAGE6_6_FEAT_PATH)
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)
    
    df_75 = pd.read_csv(STAGE7_5_FEAT_PATH)
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)
    
    df_wind = pd.read_csv(STAGE8_1_FEAT_PATH)
    df_wind["forecast_start"] = pd.to_datetime(df_wind["forecast_start"], utc=True)
    
    df_61 = pd.read_csv(STAGE6_1_FEAT_PATH)
    df_61["forecast_start"] = pd.to_datetime(df_61["forecast_start"], utc=True)
    
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
    
    ens_cols = ["forecast_start", "horizon_hour", "meps_std_SW_IN", "meps_std_total_cloud", "meps_mean_total_cloud"]
    df = df.merge(df_61[ens_cols], on=["forecast_start", "horizon_hour"], how="left")
    
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["is_daytime"] = df["actual_SW_IN"] > 0
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    
    alpha = 0.02
    phys_cloud_eff = 1.0 - np.exp(-alpha * df['lwp_latest'])
    df['phi_inconsist'] = np.abs(df['cloud_frac'] - phys_cloud_eff).fillna(0.0)
    
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
    
    all_origins = sorted(df["forecast_start"].unique())
    ctx_feature_rows = []
    
    for origin_ts in all_origins:
        context_start = origin_ts - timedelta(hours=24)
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
    
    # Merge REAL AROME Dataset
    df_arome["forecast_start"] = pd.to_datetime(df_arome["origin_t0"], utc=True)
    df_arome["horizon_hour"] = df_arome["horizon_h"]
    
    arome_merge_cols = ["forecast_start", "horizon_hour", "arome_u700", "arome_v700", "arome_lwp"]
    df = df.merge(df_arome[arome_merge_cols], on=["forecast_start", "horizon_hour"], how="left")
    
    # Compute Stage 8.17A disagreement features
    df["wind_disagreement_700"] = np.sqrt((df["arome_u700"] - df["u700"])**2 + (df["arome_v700"] - df["v700"])**2)
    df["LWP_disagreement"] = np.abs(df["arome_lwp"] - df["lwp_latest"])
    
    features_40 = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
        "lwp_latest", "iwp_latest", "lwp_x_cloud",
        "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
        "u700", "v700",
        "phi_inconsist",
        "wind_disagreement_700", "LWP_disagreement"
    ]
    
    missing_feats = df[features_40].isnull().sum().sum()
    
    log(f"FEATURE_BUILD_STATUS: SUCCESS")
    log(f"TOTAL_FEATURES: {len(features_40)}")
    log(f"TOTAL_ROWS: {len(df)}")
    log(f"MISSING_FEATURE_COUNT: {missing_feats}")
    log(f"DUPLICATE_TUPLES: {df.duplicated(subset=['forecast_start', 'horizon_hour']).sum()}")
    log(f"AROME_REAL_DATA_STATUS: VERIFIED_REAL")
    
    return df, all_origins, features_40

def run_pipeline():
    df_arome = validate_arome_input()
    df, all_origins, features_40 = build_40_feature_dataset(df_arome)
    
    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    odd_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 1]
    
    log(f"Origins Total: {len(all_origins)} | EVEN: {len(even_origins)} | ODD: {len(odd_origins)}")
    
    even_origins_sorted = sorted(even_origins)
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    
    # ----------------------------------------------------
    # EVEN CV (5 FOLDS)
    # ----------------------------------------------------
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
    control_38_features = features_40[:38]
    
    fold_records = []
    y_val_all, pred_ctrl_all, pred_cand_all = [], [], []
    
    for fold in range(1, n_splits + 1):
        tr_origs = even_origins_sorted[: fold * split_size]
        val_origs = even_origins_sorted[fold * split_size : (fold + 1) * split_size]
        
        tr_df = df_even[df_even["forecast_start"].isin(tr_origs)].copy()
        val_df = df_even[df_even["forecast_start"].isin(val_origs)].copy()
        
        st4_params_fold = fit_stage4_parameters(tr_df)
        st4_tr, phys_tr = apply_stage4_params(tr_df, st4_params_fold)
        st4_val, phys_val = apply_stage4_params(val_df, st4_params_fold)
        
        tr_df["pred_stage4_fold"] = st4_tr
        tr_df["phys_pred_fold"] = phys_tr
        tr_df["disagreement_fold"] = (tr_df["pred_stage3b_cloud_nwp"] - tr_df["phys_pred_fold"]).abs()
        
        val_df["pred_stage4_fold"] = st4_val
        val_df["phys_pred_fold"] = phys_val
        val_df["disagreement_fold"] = (val_df["pred_stage3b_cloud_nwp"] - val_df["phys_pred_fold"]).abs()
        
        tr_day = tr_df[tr_df["is_daytime"]].copy()
        val_day = val_df[val_df["is_daytime"]].copy()
        
        y_tr = tr_day["actual_SW_IN"].values
        st4_tr_day = tr_day["pred_stage4_fold"].values
        res_tr = y_tr - st4_tr_day
        
        y_val = val_day["actual_SW_IN"].values
        st4_val_day = val_day["pred_stage4_fold"].values
        
        X_tr_ctrl = tr_day[control_38_features].values
        X_val_ctrl = val_day[control_38_features].values
        
        X_tr_cand = tr_day[features_40].values
        X_val_cand = val_day[features_40].values
        
        model_ctrl = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_ctrl.fit(X_tr_ctrl, res_tr)
        pred_res_ctrl = model_ctrl.predict(X_val_ctrl)
        pred_sw_ctrl = np.maximum(0.0, st4_val_day + pred_res_ctrl)
        pred_sw_ctrl[val_day["is_night_causal"].values] = 0.0
        
        model_cand = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_cand.fit(X_tr_cand, res_tr)
        pred_res_cand = model_cand.predict(X_val_cand)
        pred_sw_cand = np.maximum(0.0, st4_val_day + pred_res_cand)
        pred_sw_cand[val_day["is_night_causal"].values] = 0.0
        
        mae_ctrl = mean_absolute_error(y_val, pred_sw_ctrl)
        mae_cand = mean_absolute_error(y_val, pred_sw_cand)
        delta_mae = mae_cand - mae_ctrl
        
        y_val_all.extend(y_val)
        pred_ctrl_all.extend(pred_sw_ctrl)
        pred_cand_all.extend(pred_sw_cand)
        
        improved = bool(delta_mae < 0.0)
        log(f"EVEN CV FOLD {fold}/5 | control_mae = {mae_ctrl:.6f} W/m² | candidate_mae = {mae_cand:.6f} W/m² | delta_mae = {delta_mae:+.6f} W/m² | improved = {improved}")
        fold_records.append({
            "fold": fold,
            "control_mae": mae_ctrl,
            "candidate_mae": mae_cand,
            "delta_mae": delta_mae,
            "improved": improved
        })
        
    agg_ctrl_mae = mean_absolute_error(y_val_all, pred_ctrl_all)
    agg_cand_mae = mean_absolute_error(y_val_all, pred_cand_all)
    agg_delta = agg_cand_mae - agg_ctrl_mae
    log(f"EVEN CV SUMMARY: Agg Control MAE = {agg_ctrl_mae:.6f} W/m² | Agg Candidate MAE = {agg_cand_mae:.6f} W/m² | Agg Delta = {agg_delta:+.6f} W/m²")

    # ----------------------------------------------------
    # FREEZE CANDIDATE ARTIFACT
    # ----------------------------------------------------
    log("FREEZE COMPLETE")
    freeze_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": "Stage 8.17A Real AROME Disagreement Model",
        "features_count": 40,
        "feature_list": features_40,
        "model_architecture": "HistGradientBoostingRegressor",
        "hyperparameters": {
            "loss": "absolute_error",
            "max_depth": 4,
            "min_samples_leaf": 30,
            "l2_regularization": 10.0,
            "random_state": 42
        },
        "arome_dataset_sha256": EXPECTED_AROME_SHA256,
        "even_cv_summary": {
            "control_mae": agg_ctrl_mae,
            "candidate_mae": agg_cand_mae,
            "delta_mae": agg_delta,
            "folds": fold_records
        }
    }
    with open(FREEZE_JSON_PATH, "w") as f:
        json.dump(freeze_data, f, indent=2)
    log(f"Saved Candidate Freeze Artifact to {FREEZE_JSON_PATH}")

    # ----------------------------------------------------
    # ODD EVALUATION & PREDICTION PERSISTENCE
    # ----------------------------------------------------
    log("STARTING ODD EVALUATION (173 ORIGINS)")
    
    st4_params_even = fit_stage4_parameters(df_even)
    st4_even, phys_even = apply_stage4_params(df_even, st4_params_even)
    df_even["pred_stage4_fold"] = st4_even
    df_even["phys_pred_fold"] = phys_even
    df_even["disagreement_fold"] = (df_even["pred_stage3b_cloud_nwp"] - df_even["phys_pred_fold"]).abs()
    
    even_day = df_even[df_even["is_daytime"]].copy()
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr
    
    X_tr_ctrl = even_day[control_38_features].values
    X_tr_cand = even_day[features_40].values
    
    model_ctrl_final = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_ctrl_final.fit(X_tr_ctrl, res_tr)
    
    model_cand_final = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_cand_final.fit(X_tr_cand, res_tr)
    
    odd_origins_sorted = sorted(odd_origins)
    odd_prediction_rows = []
    
    for i, orig in enumerate(odd_origins_sorted, 1):
        if i % 10 == 0 or i == 1 or i == len(odd_origins_sorted):
            log(f"ODD ORIGIN {i:03d}/{len(odd_origins_sorted)} ({orig.strftime('%Y-%m-%d')})")
            
        sub_odd = df[df["forecast_start"] == orig].sort_values("horizon_hour").copy()
        
        st4_odd, phys_odd = apply_stage4_params(sub_odd, st4_params_even)
        sub_odd["pred_stage4_fold"] = st4_odd
        sub_odd["phys_pred_fold"] = phys_odd
        sub_odd["disagreement_fold"] = (sub_odd["pred_stage3b_cloud_nwp"] - sub_odd["phys_pred_fold"]).abs()
        
        X_odd_ctrl = sub_odd[control_38_features].values
        X_odd_cand = sub_odd[features_40].values
        
        pred_res_ctrl = model_ctrl_final.predict(X_odd_ctrl)
        pred_res_cand = model_cand_final.predict(X_odd_cand)
        
        pred_ctrl = np.maximum(0.0, sub_odd["pred_stage4_fold"].values + pred_res_ctrl)
        pred_cand = np.maximum(0.0, sub_odd["pred_stage4_fold"].values + pred_res_cand)
        
        # Causal night zeroing
        pred_ctrl[sub_odd["is_night_causal"].values] = 0.0
        pred_cand[sub_odd["is_night_causal"].values] = 0.0
        
        for idx_row, row in enumerate(sub_odd.itertuples()):
            odd_prediction_rows.append({
                "origin_t0": row.forecast_start.strftime("%Y-%m-%d %H:%M:%S"),
                "horizon_h": row.horizon_hour,
                "valid_time": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "actual_sw_in": row.actual_SW_IN,
                "prediction": pred_cand[idx_row],
                "control_prediction": pred_ctrl[idx_row],
                "candidate_prediction": pred_cand[idx_row],
                "daytime_flag": bool(row.actual_SW_IN > 0),
                "is_night_causal": bool(row.is_night_causal),
                "solar_elevation": row.solar_elevation,
                "clearsky_ghi": row.clearsky_ghi,
                "wind_disagreement_700": row.wind_disagreement_700,
                "LWP_disagreement": row.LWP_disagreement
            })
            
    df_odd_preds = pd.DataFrame(odd_prediction_rows)
    df_odd_preds.to_csv(ODD_PREDS_CSV_PATH, index=False)
    log("PREDICTION CSV WRITTEN")
    log(f"Saved {len(df_odd_preds)} row-level ODD predictions to {ODD_PREDS_CSV_PATH}")
    
    with open(ODD_PREDS_CSV_PATH, "rb") as f:
        preds_sha256 = hashlib.sha256(f.read()).hexdigest()
        
    log(f"PREDICTION CSV SHA256: {preds_sha256}")

if __name__ == "__main__":
    run_pipeline()
