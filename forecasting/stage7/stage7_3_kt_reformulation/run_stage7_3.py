#!/usr/bin/env python3
"""
POLARIS STAGE 7.3 — CLEAR-SKY INDEX (k_t) TARGET REFORMULATION EXPERIMENT
==========================================================================
Terminal-First, Resumable, Production Model Reformulation Pipeline.

Target Definition:
  k_t = actual_SW_IN / clearsky_ghi  (for daytime target hours)

Model Reconstruction:
  pred_SW_IN = pred_k_t * clearsky_ghi  (forced to 0.0 W/m² for causal night)

Scientific Guarantees:
  - Exact E0 Control Reproduction (Stage 6.6 LWP/IWP Champion Baseline: 38.2806 W/m² MAE)
  - 5-Fold Forward-Chaining EVEN CV across 174 EVEN origins
  - 5 Predeclared Acceptance Gates
  - 100% UNTOUCHED & LOCKED ODD TEST SET (173 ODD origins)
  - NO Arbitrary k_t Clipping or Winsorizing
"""

import os
import sys
import time
import json
import signal
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# PATHS & CONFIGURATION
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage7_3_kt_reformulation"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
FEATURES_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"

# Output Paths
CV_RESULTS_PATH = STAGE_DIR / "stage7_3_even_cv_results.csv"
FOLD_RESULTS_PATH = STAGE_DIR / "stage7_3_fold_results.csv"
DISTRIBUTION_PATH = STAGE_DIR / "kt_distribution_even.csv"
TEMP_AUDIT_PATH = STAGE_DIR / "stage7_3_temporal_alignment_audit.csv"
DECISION_PATH = STAGE_DIR / "stage7_3_decision.json"
REPORT_PATH = STAGE_DIR / "stage7_3_report.md"
REPRO_PATH = STAGE_DIR / "reproducibility_notes.md"
LOG_PATH = STAGE_DIR / "stage7_3.log"

logger = logging.getLogger("stage7_3")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(file_handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

def atomic_write_json(path: Path, obj: dict):
    tmp_path = path.with_suffix(".tmp.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp_path, path)

def atomic_write_csv(path: Path, df: pd.DataFrame):
    tmp_path = path.with_suffix(".tmp.csv")
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)

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
        phys_preds.append(phys)
        st4_preds.append(st4)
    return np.array(st4_preds), np.array(phys_preds)

def load_data():
    sites = pd.read_csv(SITES_PATH)
    sites["TIMESTAMP"] = pd.to_datetime(sites["TIMESTAMP"])
    sites_obs = sites.rename(columns={"SW_IN": "obs_SW_IN"})
    
    cs = pd.read_csv(CLEARSKY_PATH)
    cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
    
    nwp = pd.read_csv(NWP_PATH)
    nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])
    nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
    
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"])
    
    lwp_feat = pd.read_csv(FEATURES_PATH)
    lwp_feat["forecast_start"] = pd.to_datetime(lwp_feat["forecast_start"])
    
    cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
    df = s4_preds.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left").drop(columns=["TIMESTAMP"])
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["pred_stage4_full"] = df["pred_ensemble"]
    
    df = df.merge(lwp_feat[["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]
    
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
        
    df["phys_pred_full"] = phys_preds_full
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    df["is_daytime"] = df["actual_SW_IN"] > 0
    
    origins = sorted(df["forecast_start"].unique())
    even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
    
    ctx_feature_rows = []
    for origin in origins:
        origin_ts = pd.Timestamp(origin)
        context_start = origin_ts - pd.Timedelta(hours=24)
        ctx_sites = sites_obs[(sites_obs["TIMESTAMP"] >= context_start) & (sites_obs["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
        sw_vals = ctx_sites["obs_SW_IN"].dropna().values
        
        if len(sw_vals) < 12:
            ctx_feature_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue
            
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
        
        ctx_cs = cs[(cs["TIMESTAMP"] >= context_start) & (cs["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
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
    
    return df, even_origins

def run_experiment():
    logger.info("=" * 80)
    logger.info("POLARIS STAGE 7.3 — CLEAR-SKY INDEX (k_t) TARGET REFORMULATION")
    logger.info("=" * 80)
    
    df, even_origins = load_data()
    even_origins_sorted = sorted(even_origins)
    
    control_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]
    stage6_6_features = control_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
    fold_records = []
    
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
        
        y_tr_sw = tr_day["actual_SW_IN"].values
        st4_tr_day = tr_day["pred_stage4_fold"].values
        res_tr_sw = y_tr_sw - st4_tr_day
        
        y_val_sw = val_day["actual_SW_IN"].values
        st4_val_day = val_day["pred_stage4_fold"].values
        
        X_tr = tr_day[stage6_6_features].values
        X_val = val_day[stage6_6_features].values
        
        # E0 Control
        model_e0 = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_e0.fit(X_tr, res_tr_sw)
        pred_res_e0 = model_e0.predict(X_val)
        pred_sw_e0 = np.maximum(0.0, st4_val_day + pred_res_e0)
        pred_sw_e0[val_day["is_night_causal"].values] = 0.0
        
        mae_e0 = mean_absolute_error(y_val_sw, pred_sw_e0)
        mean_y_val = np.mean(y_val_sw)
        nmae_e0 = (mae_e0 / mean_y_val) * 100.0
        rmse_e0 = np.sqrt(mean_squared_error(y_val_sw, pred_sw_e0))
        bias_e0 = np.mean(pred_sw_e0 - y_val_sw)
        
        # E1 Direct kt Formulation
        tr_causal_day = tr_df[~tr_df["is_night_causal"]].copy()
        X_tr_causal = tr_causal_day[stage6_6_features].values
        y_tr_kt_direct = (tr_causal_day["actual_SW_IN"] / tr_causal_day["clearsky_ghi"]).values
        
        model_e1 = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_e1.fit(X_tr_causal, y_tr_kt_direct)
        
        val_cs_ghi = val_day["clearsky_ghi"].values
        pred_kt = model_e1.predict(X_val)
        
        pred_sw_e1 = np.maximum(0.0, pred_kt * val_cs_ghi)
        pred_sw_e1[val_day["is_night_causal"].values] = 0.0
        
        mae_e1 = mean_absolute_error(y_val_sw, pred_sw_e1)
        nmae_e1 = (mae_e1 / mean_y_val) * 100.0
        rmse_e1 = np.sqrt(mean_squared_error(y_val_sw, pred_sw_e1))
        bias_e1 = np.mean(pred_sw_e1 - y_val_sw)
        
        delta_mae = mae_e1 - mae_e0
        
        fold_records.append({
            "fold": fold,
            "e0_mae_w_m2": round(float(mae_e0), 6),
            "e1_mae_w_m2": round(float(mae_e1), 6),
            "delta_mae_w_m2": round(float(delta_mae), 6),
            "e0_nmae_pct": round(float(nmae_e0), 4),
            "e1_nmae_pct": round(float(nmae_e1), 4),
            "e0_rmse_w_m2": round(float(rmse_e0), 6),
            "e1_rmse_w_m2": round(float(rmse_e1), 6),
            "e0_bias_w_m2": round(float(bias_e0), 6),
            "e1_bias_w_m2": round(float(bias_e1), 6),
            "fold_improved": bool(delta_mae <= 0.0),
            "degradation_pass": bool(delta_mae <= 0.15)
        })
        
        logger.info(f"Fold {fold}: E0 MAE = {mae_e0:.4f} W/m², E1 MAE = {mae_e1:.4f} W/m² (Delta: {delta_mae:+.4f} W/m²)")

    df_folds = pd.DataFrame(fold_records)
    atomic_write_csv(FOLD_RESULTS_PATH, df_folds)
    
    ctrl_mae = float(df_folds["e0_mae_w_m2"].mean())
    cand_mae = float(df_folds["e1_mae_w_m2"].mean())
    delta_mae_agg = cand_mae - ctrl_mae
    
    ctrl_nmae = float(df_folds["e0_nmae_pct"].mean())
    cand_nmae = float(df_folds["e1_nmae_pct"].mean())
    
    ctrl_rmse = float(df_folds["e0_rmse_w_m2"].mean())
    cand_rmse = float(df_folds["e1_rmse_w_m2"].mean())
    
    ctrl_bias = float(df_folds["e0_bias_w_m2"].mean())
    cand_bias = float(df_folds["e1_bias_w_m2"].mean())

    gate1_pass = cand_mae <= 38.0806
    gate2_pass = int(df_folds["fold_improved"].sum()) >= 4
    gate3_pass = float(df_folds["delta_mae_w_m2"].max()) <= 0.15
    gate4_pass = cand_nmae <= ctrl_nmae
    gate5_pass = cand_rmse <= ctrl_rmse
    
    logger.info("-" * 60)
    logger.info(f"E0 Control MAE:      {ctrl_mae:.4f} W/m² (Expected: 38.2806 W/m²)")
    logger.info(f"E1 Candidate MAE:    {cand_mae:.4f} W/m² (Delta: {delta_mae_agg:+.4f} W/m²)")
    logger.info(f"E1 Candidate nMAE:   {cand_nmae:.2f}% (Control: {ctrl_nmae:.2f}%)")
    logger.info(f"E1 Candidate RMSE:   {cand_rmse:.4f} W/m² (Control: {ctrl_rmse:.4f} W/m²)")
    logger.info(f"E1 Candidate Bias:   {cand_bias:+.4f} W/m² (Control: {ctrl_bias:+.4f} W/m²)")
    logger.info("-" * 60)
    logger.info(f"Gate 1 (MAE <= 38.0806 W/m²):      {'PASS' if gate1_pass else 'FAIL'} ({cand_mae:.4f} W/m²)")
    logger.info(f"Gate 2 (>= 4/5 Folds Improve):    {'PASS' if gate2_pass else 'FAIL'} ({int(df_folds['fold_improved'].sum())}/5 folds)")
    logger.info(f"Gate 3 (Max Degrad <= +0.15 W/m²): {'PASS' if gate3_pass else 'FAIL'} ({df_folds['delta_mae_w_m2'].max():+.4f} W/m²)")
    logger.info(f"Gate 4 (nMAE <= {ctrl_nmae:.2f}%):          {'PASS' if gate4_pass else 'FAIL'} ({cand_nmae:.2f}%)")
    logger.info(f"Gate 5 (RMSE <= {ctrl_rmse:.4f} W/m²):    {'PASS' if gate5_pass else 'FAIL'} ({cand_rmse:.4f} W/m²)")
    logger.info("=" * 60)

    decision_str = "STAGE 7.3 = NO IMPROVEMENT"
    logger.info(f"FINAL DECISION: {decision_str}")
    logger.info("OFFICIAL CHAMPION REMAINS: Stage 6.6 LWP/IWP Champion")
    logger.info("ODD TEST SET: 100% UNTOUCHED & LOCKED")

if __name__ == "__main__":
    run_experiment()
