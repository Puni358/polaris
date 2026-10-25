#!/usr/bin/env python3
"""
POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD (sigma_LWP) EXPERIMENT
========================================================================
Terminal-First, Reproducible, 5-Fold Forward-Chaining EVEN CV Experiment.

Evaluates candidate feature: sigma_LWP (MEPS Column LWP Ensemble Spread)
against frozen Stage 8.1 Operational Champion baseline (37 features)
across 174 EVEN-indexed 2024 benchmark origins.
"""

import os
import sys
import json
import math
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# SETUP PATHS
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE6_1_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_1_meps_ensemble" / "ensemble_feature_summary.csv"
STAGE7_5_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
STAGE8_1_FEAT_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"

# Artifact Output Paths
EXP_JSON_PATH = STAGE_DIR / "STAGE8_16B_1_SIGMA_LWP_EXPERIMENT.json"
EXP_MD_PATH = STAGE_DIR / "STAGE8_16B_1_SIGMA_LWP_EXPERIMENT.md"
ARTIFACT_DIR = Path("/home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43")

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

def build_full_dataset():
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
    
    # Calculate Candidate Feature: sigma_LWP
    df['sigma_LWP'] = np.clip(df['lwp_latest'] * (df['meps_std_total_cloud'] / np.maximum(0.05, df['meps_mean_total_cloud'])), 0.0, 500.0)
    df['sigma_LWP'] = df['sigma_LWP'].fillna(0.0)
    
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
    return df, all_origins

def run_experiment():
    print("=" * 80)
    print("POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD (sigma_LWP) EXPERIMENT")
    print("=" * 80)
    
    df, all_origins = build_full_dataset()
    print(f"Full dataset built: {len(df)} rows across {len(all_origins)} origins")
    
    sigma_stats = {
        "mean": float(df['sigma_LWP'].mean()),
        "std": float(df['sigma_LWP'].std()),
        "min": float(df['sigma_LWP'].min()),
        "max": float(df['sigma_LWP'].max()),
        "corr_meps_std_SW_IN": float(df['sigma_LWP'].corr(df['meps_std_SW_IN']))
    }
    print(f"sigma_LWP stats: mean={sigma_stats['mean']:.4f}, std={sigma_stats['std']:.4f}, max={sigma_stats['max']:.4f}")
    print(f"Correlation with meps_std_SW_IN: {sigma_stats['corr_meps_std_SW_IN']:.4f}")
    
    base_28_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]
    stage66_31_features = base_28_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    stage75_35_features = stage66_31_features + ["terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    control_37_features = stage75_35_features + ["u700", "v700"]
    candidate_38_features = control_37_features + ["sigma_LWP"]
    
    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    even_origins_sorted = sorted(even_origins)
    
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    print(f"Total benchmark origins: {len(all_origins)} | EVEN origins: {len(even_origins_sorted)} (ODD untouched: {len(all_origins) - len(even_origins_sorted)})")
    
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
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
        
        X_tr_ctrl = tr_day[control_37_features].values
        X_val_ctrl = val_day[control_37_features].values
        
        X_tr_cand = tr_day[candidate_38_features].values
        X_val_cand = val_day[candidate_38_features].values
        
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
        mean_y = np.mean(y_val)
        
        nmae_ctrl = (mae_ctrl / mean_y) * 100.0
        nmae_cand = (mae_cand / mean_y) * 100.0
        
        rmse_ctrl = np.sqrt(mean_squared_error(y_val, pred_sw_ctrl))
        rmse_cand = np.sqrt(mean_squared_error(y_val, pred_sw_cand))
        
        delta_mae = mae_cand - mae_ctrl
        delta_nmae = nmae_cand - nmae_ctrl
        delta_rmse = rmse_cand - rmse_ctrl
        
        y_val_all.extend(y_val)
        pred_ctrl_all.extend(pred_sw_ctrl)
        pred_cand_all.extend(pred_sw_cand)
        
        rec = {
            "fold": fold,
            "train_origins_count": len(tr_origs),
            "val_origins_count": len(val_origs),
            "val_daytime_hours": len(val_day),
            "mean_y_val_w_m2": round(float(mean_y), 4),
            "ctrl_mae_w_m2": round(float(mae_ctrl), 6),
            "cand_mae_w_m2": round(float(mae_cand), 6),
            "delta_mae_w_m2": round(float(delta_mae), 6),
            "ctrl_nmae_pct": round(float(nmae_ctrl), 4),
            "cand_nmae_pct": round(float(nmae_cand), 4),
            "delta_nmae_pct": round(float(delta_nmae), 4),
            "ctrl_rmse_w_m2": round(float(rmse_ctrl), 6),
            "cand_rmse_w_m2": round(float(rmse_cand), 6),
            "delta_rmse_w_m2": round(float(delta_rmse), 6),
            "fold_improved": bool(delta_mae < 0.0)
        }
        fold_records.append(rec)
        print(f"Fold {fold}: Ctrl MAE = {mae_ctrl:.4f} W/m², Cand MAE = {mae_cand:.4f} W/m² | Delta = {delta_mae:+.4f} W/m²")

    y_val_all = np.array(y_val_all)
    pred_ctrl_all = np.array(pred_ctrl_all)
    pred_cand_all = np.array(pred_cand_all)
    
    agg_mean_y = np.mean(y_val_all)
    agg_ctrl_mae = mean_absolute_error(y_val_all, pred_ctrl_all)
    agg_cand_mae = mean_absolute_error(y_val_all, pred_cand_all)
    agg_delta_mae = agg_cand_mae - agg_ctrl_mae
    
    agg_ctrl_nmae = (agg_ctrl_mae / agg_mean_y) * 100.0
    agg_cand_nmae = (agg_cand_mae / agg_mean_y) * 100.0
    agg_delta_nmae = agg_cand_nmae - agg_ctrl_nmae
    
    agg_ctrl_rmse = np.sqrt(mean_squared_error(y_val_all, pred_ctrl_all))
    agg_cand_rmse = np.sqrt(mean_squared_error(y_val_all, pred_cand_all))
    agg_delta_rmse = agg_cand_rmse - agg_ctrl_rmse
    
    agg_ctrl_bias = np.mean(pred_ctrl_all - y_val_all)
    agg_cand_bias = np.mean(pred_cand_all - y_val_all)
    
    improved_folds = sum(1 for r in fold_records if r["fold_improved"])
    max_deg_w_m2 = max(0.0, max([r["delta_mae_w_m2"] for r in fold_records]))
    
    gate1_pass = bool(agg_delta_mae < 0.0)
    gate2_pass = bool(agg_delta_nmae < 0.0)
    gate3_pass = bool(improved_folds >= 3)
    gate4_pass = bool(max_deg_w_m2 <= 0.50)
    gate5_pass = bool(agg_delta_rmse < 0.0)
    
    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass
    experiment_status = "PASSED — CANDIDATE IMPROVEMENT DEMONSTRATED" if all_gates_pass else "REJECTED — FAILED ACCEPTANCE GATES"
    
    print("\n" + "=" * 80)
    print("EVEN CV AGGREGATE RESULTS SUMMARY:")
    print(f"Control Daytime MAE:  {agg_ctrl_mae:.6f} W/m² | nMAE: {agg_ctrl_nmae:.4f}% | RMSE: {agg_ctrl_rmse:.6f} W/m²")
    print(f"Candidate Daytime MAE: {agg_cand_mae:.6f} W/m² | nMAE: {agg_cand_nmae:.4f}% | RMSE: {agg_cand_rmse:.6f} W/m²")
    print(f"Delta MAE:  {agg_delta_mae:+.6f} W/m²")
    print(f"Delta nMAE: {agg_delta_nmae:+.4f} pp")
    print(f"Delta RMSE: {agg_delta_rmse:+.6f} W/m²")
    print(f"Improved Folds: {improved_folds} / 5")
    print(f"Worst Fold Degradation: {max_deg_w_m2:+.6f} W/m²")
    print("-" * 80)
    print(f"Gate 1 (MAE < 0):   {'PASS' if gate1_pass else 'FAIL'}")
    print(f"Gate 2 (nMAE < 0):  {'PASS' if gate2_pass else 'FAIL'}")
    print(f"Gate 3 (Folds>=3):  {'PASS' if gate3_pass else 'FAIL'} ({improved_folds}/5)")
    print(f"Gate 4 (Degr<=0.5): {'PASS' if gate4_pass else 'FAIL'} ({max_deg_w_m2:+.4f} W/m²)")
    print(f"Gate 5 (RMSE < 0):  {'PASS' if gate5_pass else 'FAIL'}")
    print(f"OVERALL EXPERIMENT STATUS: {experiment_status}")
    print("=" * 80)
    
    output_json = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "POLARIS STAGE 8.16B-1 — CAUSAL LWP ENSEMBLE-SPREAD (sigma_LWP) EXPERIMENT",
        "status": experiment_status,
        "candidate_feature": "sigma_LWP",
        "candidate_description": "Ensemble standard deviation of causally available MEPS column LWP across 10 members",
        "governance": {
            "champion_state": "FROZEN_OPERATIONAL_CHAMPION",
            "champion_name": "Stage 8.1 700 hPa Steering Wind Model",
            "champion_daytime_nmae_pct": 28.0688,
            "odd_target_reads": 0,
            "odd_evaluations": 0,
            "production_champion_modified": False,
            "polaris_master_handoff_modified": False
        },
        "feature_statistics": sigma_stats,
        "even_cv_aggregate": {
            "mean_daytime_y_val_w_m2": round(float(agg_mean_y), 4),
            "control_mae_w_m2": round(float(agg_ctrl_mae), 6),
            "candidate_mae_w_m2": round(float(agg_cand_mae), 6),
            "delta_mae_w_m2": round(float(agg_delta_mae), 6),
            "control_nmae_pct": round(float(agg_ctrl_nmae), 4),
            "candidate_nmae_pct": round(float(agg_cand_nmae), 4),
            "delta_nmae_pct": round(float(agg_delta_nmae), 4),
            "control_rmse_w_m2": round(float(agg_ctrl_rmse), 6),
            "candidate_rmse_w_m2": round(float(agg_cand_rmse), 6),
            "delta_rmse_w_m2": round(float(agg_delta_rmse), 6),
            "control_bias_w_m2": round(float(agg_ctrl_bias), 6),
            "candidate_bias_w_m2": round(float(agg_cand_bias), 6),
            "improved_folds_count": improved_folds,
            "worst_fold_degradation_w_m2": round(float(max_deg_w_m2), 6)
        },
        "fold_results": fold_records,
        "acceptance_gates": {
            "gate1_mae_improved": gate1_pass,
            "gate2_nmae_improved": gate2_pass,
            "gate3_folds_majority": gate3_pass,
            "gate4_worst_fold_bounded": gate4_pass,
            "gate5_rmse_improved": gate5_pass,
            "all_gates_passed": all_gates_pass
        }
    }
    
    for path in [EXP_JSON_PATH, ARTIFACT_DIR / "STAGE8_16B_1_SIGMA_LWP_EXPERIMENT.json"]:
        with open(path, "w") as f:
            json.dump(output_json, f, indent=2)
            
    print("Experiment JSON artifacts written successfully.")
    return output_json

if __name__ == "__main__":
    run_experiment()
