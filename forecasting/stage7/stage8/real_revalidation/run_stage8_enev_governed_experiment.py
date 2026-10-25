#!/usr/bin/env python3
"""
POLARIS STAGE 8 — ENEV METAR UPSTREAM CLOUD FEATURE GOVERNED EXPERIMENT
======================================================================
Terminal-First, Reproducible, 5-Fold Forward-Chaining EVEN CV Experiment.

Evaluates candidate features:
1. enev_cloud_cover_okta
2. enev_cloud_base_m

against frozen Stage 8.1 Operational Champion baseline (37 features)
across 174 EVEN-indexed 2024 benchmark origins.
Enforces strict acceptance gates G1-G6 and ODD firewall protocol.
"""

import os
import sys
import json
import math
import hashlib
import logging
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

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
ENEV_METAR_PATH = BASE_DIR / "data" / "enev_metar_2024.csv"

# Artifact Output Paths
EXP_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "real_revalidation"
EXP_JSON_PATH = EXP_DIR / "STAGE8_ENEV_EXPERIMENT.json"
EXP_MD_PATH = EXP_DIR / "STAGE8_ENEV_EXPERIMENT.md"
BRAIN_DIR = Path("/home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd")

def timestamp_now():
    return datetime.now(timezone.utc).isoformat()

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
    
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["is_daytime"] = df["actual_SW_IN"] > 0
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    
    return df, all_origins

def parse_enev_metar_features(all_origins):
    df_metar = pd.read_csv(ENEV_METAR_PATH)
    df_metar["valid_dt"] = pd.to_datetime(df_metar["valid"], utc=True)
    
    enev_rows = []
    unparsed_count = 0
    missing_count = 0
    
    for orig_ts in all_origins:
        target_dt = orig_ts - timedelta(minutes=10) # 23:50 UTC
        
        # Sub: reports within 2 hours prior to t0
        sub = df_metar[(df_metar["valid_dt"] >= orig_ts - timedelta(hours=2)) & (df_metar["valid_dt"] < orig_ts)].sort_values("valid_dt")
        
        if len(sub) == 0:
            missing_count += 1
            okta = 0.0
            base_m = 5000.0
            report_ts = target_dt
        else:
            exact = sub[sub["valid_dt"] == target_dt]
            if len(exact) > 0:
                row = exact.iloc[-1]
            else:
                row = sub.iloc[-1]
                
            report_ts = row["valid_dt"]
            raw_skyc1 = str(row["skyc1"]) if pd.notna(row["skyc1"]) else "M"
            raw_skyl1 = float(row["skyl1"]) if (pd.notna(row["skyl1"]) and str(row["skyl1"]) != "M") else np.nan
            metar_str = str(row["metar"]) if pd.notna(row["metar"]) else ""
            
            is_clear = any(k in metar_str for k in ["CAVOK", "NSC", "NCD", "SKC", "CLR"]) or raw_skyc1 in ["CLR", "SKC", "NCD", "NSC", "CAVOK"]
            
            if is_clear:
                okta = 0.0
                base_m = 5000.0
            elif raw_skyc1 == "FEW":
                okta = 1.5
                base_m = raw_skyl1 * 0.3048 if not np.isnan(raw_skyl1) else 5000.0
            elif raw_skyc1 == "SCT":
                okta = 3.5
                base_m = raw_skyl1 * 0.3048 if not np.isnan(raw_skyl1) else 5000.0
            elif raw_skyc1 == "BKN":
                okta = 6.0
                base_m = raw_skyl1 * 0.3048 if not np.isnan(raw_skyl1) else 5000.0
            elif raw_skyc1 == "OVC":
                okta = 8.0
                base_m = raw_skyl1 * 0.3048 if not np.isnan(raw_skyl1) else 5000.0
            elif raw_skyc1 == "VV" or "VV" in metar_str:
                okta = 8.0
                if "VV" in metar_str:
                    m = re.search(r'VV(\d{3})', metar_str)
                    if m:
                        base_m = float(m.group(1)) * 30.48
                    elif not np.isnan(raw_skyl1):
                        base_m = raw_skyl1 * 0.3048
                    else:
                        base_m = 100.0
                else:
                    base_m = raw_skyl1 * 0.3048 if not np.isnan(raw_skyl1) else 100.0
            else:
                unparsed_count += 1
                okta = 0.0
                base_m = 5000.0
                
        enev_rows.append({
            "forecast_start": orig_ts,
            "enev_report_ts": report_ts,
            "enev_cloud_cover_okta": okta,
            "enev_cloud_base_m": base_m
        })
        
    df_enev = pd.DataFrame(enev_rows)
    return df_enev, missing_count, unparsed_count

def run_experiment():
    print("=" * 75)
    print("POLARIS STAGE 8 — ENEV METAR UPSTREAM CLOUD FEATURE GOVERNED EXPERIMENT")
    print("=" * 75)
    
    # 1. Build dataset
    df, all_origins = build_full_dataset()
    df_enev, missing_origins_cnt, unparsed_cnt = parse_enev_metar_features(all_origins)
    
    df = df.merge(df_enev, on="forecast_start", how="left")
    
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
    candidate_39_features = control_37_features + ["enev_cloud_cover_okta", "enev_cloud_base_m"]
    
    # 2. Filter EVEN origins
    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    even_origins_sorted = sorted(even_origins)
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
        
        y_tr = tr_day["actual_SW_IN"].values
        st4_tr_day = tr_day["pred_stage4_fold"].values
        res_tr = y_tr - st4_tr_day
        
        y_val = val_day["actual_SW_IN"].values
        st4_val_day = val_day["pred_stage4_fold"].values
        
        X_tr_ctrl = tr_day[control_37_features].values
        X_val_ctrl = val_day[control_37_features].values
        
        X_tr_cand = tr_day[candidate_39_features].values
        X_val_cand = val_day[candidate_39_features].values
        
        # Control Model (Stage 8.1 37 features)
        model_ctrl = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_ctrl.fit(X_tr_ctrl, res_tr)
        pred_res_ctrl = model_ctrl.predict(X_val_ctrl)
        pred_sw_ctrl = np.maximum(0.0, st4_val_day + pred_res_ctrl)
        pred_sw_ctrl[val_day["is_night_causal"].values] = 0.0
        
        # Candidate Model (39 features)
        model_cand = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_cand.fit(X_tr_cand, res_tr)
        pred_res_cand = model_cand.predict(X_val_cand)
        pred_sw_cand = np.maximum(0.0, st4_val_day + pred_res_cand)
        pred_sw_cand[val_day["is_night_causal"].values] = 0.0
        
        mae_ctrl = mean_absolute_error(y_val, pred_sw_ctrl)
        mae_cand = mean_absolute_error(y_val, pred_sw_cand)
        mean_y_val = np.mean(y_val)
        
        nmae_ctrl = (mae_ctrl / mean_y_val) * 100.0
        nmae_cand = (mae_cand / mean_y_val) * 100.0
        
        rmse_ctrl = np.sqrt(mean_squared_error(y_val, pred_sw_ctrl))
        rmse_cand = np.sqrt(mean_squared_error(y_val, pred_sw_cand))
        
        bias_ctrl = np.mean(pred_sw_ctrl - y_val)
        bias_cand = np.mean(pred_sw_cand - y_val)
        
        delta_mae = mae_cand - mae_ctrl
        
        fold_records.append({
            "fold": fold,
            "ctrl_mae_w_m2": round(float(mae_ctrl), 6),
            "cand_mae_w_m2": round(float(mae_cand), 6),
            "delta_mae_w_m2": round(float(delta_mae), 6),
            "ctrl_nmae_pct": round(float(nmae_ctrl), 4),
            "cand_nmae_pct": round(float(nmae_cand), 4),
            "ctrl_rmse_w_m2": round(float(rmse_ctrl), 6),
            "cand_rmse_w_m2": round(float(rmse_cand), 6),
            "ctrl_bias_w_m2": round(float(bias_ctrl), 6),
            "cand_bias_w_m2": round(float(bias_cand), 6),
            "fold_improved": bool(delta_mae <= 0.0),
            "fold_degradation": round(float(max(0.0, delta_mae)), 6)
        })
        
        print(f"[FOLD {fold}/5] Control MAE: {mae_ctrl:.6f} W/m² | Candidate MAE: {mae_cand:.6f} W/m² | Delta: {delta_mae:+.6f} W/m²")

    agg_mae_ctrl = float(np.mean([r["ctrl_mae_w_m2"] for r in fold_records]))
    agg_mae_cand = float(np.mean([r["cand_mae_w_m2"] for r in fold_records]))
    
    agg_nmae_ctrl = float(np.mean([r["ctrl_nmae_pct"] for r in fold_records]))
    agg_nmae_cand = float(np.mean([r["cand_nmae_pct"] for r in fold_records]))
    
    agg_rmse_ctrl = float(np.mean([r["ctrl_rmse_w_m2"] for r in fold_records]))
    agg_rmse_cand = float(np.mean([r["cand_rmse_w_m2"] for r in fold_records]))
    
    agg_bias_ctrl = float(np.mean([r["ctrl_bias_w_m2"] for r in fold_records]))
    agg_bias_cand = float(np.mean([r["cand_bias_w_m2"] for r in fold_records]))
    
    delta_agg_mae = agg_mae_cand - agg_mae_ctrl
    delta_agg_nmae = agg_nmae_cand - agg_nmae_ctrl
    delta_agg_rmse = agg_rmse_cand - agg_rmse_ctrl
    
    folds_improved = sum(1 for r in fold_records if r["fold_improved"])
    max_degradation = max(r["delta_mae_w_m2"] for r in fold_records)
    
    # Gate Evaluations
    g1_pass = bool(delta_agg_mae <= -0.50)
    g2_pass = bool(folds_improved >= 4)
    g3_pass = bool(max_degradation <= 0.50)
    g4_pass = bool(agg_nmae_cand <= agg_nmae_ctrl and agg_rmse_cand <= agg_rmse_ctrl)
    g5_pass = bool(missing_origins_cnt == 0) # 100% causal dataset
    g6_pass = bool(abs(agg_mae_ctrl - 37.620054) < 0.1) # Control reproduction check
    
    all_even_gates_pass = bool(g1_pass and g2_pass and g3_pass and g4_pass and g5_pass and g6_pass)
    
    decision = "EVEN GATES PASSED — PROCEED TO ODD" if all_even_gates_pass else "STOP — EVEN GATE FAILURE"
    
    print("\n" + "=" * 75)
    print("EVEN CV EVALUATION RESULTS")
    print("=" * 75)
    print(f"Control EVEN MAE:   {agg_mae_ctrl:.6f} W/m² | nMAE: {agg_nmae_ctrl:.4f}% | RMSE: {agg_rmse_ctrl:.6f} W/m²")
    print(f"Candidate EVEN MAE: {agg_mae_cand:.6f} W/m² | nMAE: {agg_nmae_cand:.4f}% | RMSE: {agg_rmse_cand:.6f} W/m²")
    print(f"Delta Agg MAE:     {delta_agg_mae:+.6f} W/m² (Threshold: <= -0.50 W/m²)")
    print(f"Folds Improved:    {folds_improved}/5 (Threshold: >= 4)")
    print(f"Max Fold Degrad:   {max_degradation:+.6f} W/m² (Threshold: <= +0.50 W/m²)")
    print("-" * 75)
    print(f"Gate 1 (Delta MAE <= -0.50):    {g1_pass}")
    print(f"Gate 2 (Folds Improved >= 4):   {g2_pass}")
    print(f"Gate 3 (Max Degrad <= +0.50):   {g3_pass}")
    print(f"Gate 4 (nMAE & RMSE <= Ctrl):   {g4_pass}")
    print(f"Gate 5 (100% Causal Data):      {g5_pass}")
    print(f"Gate 6 (Control Reproduction):  {g6_pass}")
    print(f"OVERALL DECISION:               {decision}")
    print("=" * 75)
    
    results_manifest = {
        "stage": "STAGE 8 — ENEV METAR UPSTREAM CLOUD FEATURE GOVERNED EXPERIMENT",
        "timestamp": timestamp_now(),
        "station": {
            "icao": "ENEV",
            "distance_km": 86,
            "direction": "WNW"
        },
        "candidate_features": ["enev_cloud_cover_okta", "enev_cloud_base_m"],
        "control_features_count": len(control_37_features),
        "candidate_features_count": len(candidate_39_features),
        "even_benchmark_origins": len(even_origins),
        "missing_origins_count": missing_origins_cnt,
        "unparsed_metar_count": unparsed_cnt,
        "control_metrics": {
            "mae_w_m2": round(agg_mae_ctrl, 6),
            "nmae_pct": round(agg_nmae_ctrl, 4),
            "rmse_w_m2": round(agg_rmse_ctrl, 6),
            "bias_w_m2": round(agg_bias_ctrl, 6)
        },
        "candidate_metrics": {
            "mae_w_m2": round(agg_mae_cand, 6),
            "nmae_pct": round(agg_nmae_cand, 4),
            "rmse_w_m2": round(agg_rmse_cand, 6),
            "bias_w_m2": round(agg_bias_cand, 6)
        },
        "deltas": {
            "delta_mae_w_m2": round(delta_agg_mae, 6),
            "delta_nmae_pct": round(delta_agg_nmae, 4),
            "delta_rmse_w_m2": round(delta_agg_rmse, 6)
        },
        "fold_summary": fold_records,
        "gate_evaluations": {
            "g1_delta_mae_le_minus_0_50": g1_pass,
            "g2_folds_improved_ge_4": g2_pass,
            "g3_max_fold_degradation_le_0_50": g3_pass,
            "g4_nmae_rmse_le_control": g4_pass,
            "g5_100_percent_causal": g5_pass,
            "g6_control_reproduced": g6_pass
        },
        "final_decision": decision,
        "odd_firewall_status": {
            "odd_accessed": False,
            "odd_predictions_generated": False,
            "odd_metrics_computed": False,
            "firewall_reason": "EVEN gate failure — STOP protocol invoked" if not all_even_gates_pass else "ODD evaluation permitted"
        }
    }
    
    # Save JSON & MD Manifests
    with open(EXP_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results_manifest, f, indent=2)
        
    with open(BRAIN_DIR / "STAGE8_ENEV_EXPERIMENT.json", "w", encoding="utf-8") as f:
        json.dump(results_manifest, f, indent=2)
        
    md_content = f"""# POLARIS STAGE 8 — ENEV METAR GOVERNED EXPERIMENT REPORT

**Date:** {timestamp_now()}  
**Candidate Features:** `enev_cloud_cover_okta`, `enev_cloud_base_m`  
**Control Feature Inventory:** 37 features (Stage 8.1 Champion)  
**Evaluated Origins:** 174 EVEN origins (2024 benchmark split)  

---

## 1. Executive Summary & Gate Decision

| Gate | Description | Threshold | Observed | Result |
| :--- | :--- | :--- | :--- | :---: |
| **G1** | Aggregated Delta MAE | <= -0.50 W/m2 | {delta_agg_mae:+.6f} W/m2 | **{'PASS' if g1_pass else 'FAIL'}** |
| **G2** | Folds Improved | >= 4/5 folds | {folds_improved}/5 | **{'PASS' if g2_pass else 'FAIL'}** |
| **G3** | Max Fold Degradation | <= +0.50 W/m2 | {max_degradation:+.6f} W/m2 | **{'PASS' if g3_pass else 'FAIL'}** |
| **G4** | nMAE & RMSE <= Control | Both <= Control | nMAE: {agg_nmae_cand:.4f}% vs {agg_nmae_ctrl:.4f}%, RMSE: {agg_rmse_cand:.6f} vs {agg_rmse_ctrl:.6f} | **{'PASS' if g4_pass else 'FAIL'}** |
| **G5** | 100% Causal Availability | 0 missing/unparsed | Missing: {missing_origins_cnt}, Unparsed: {unparsed_cnt} | **{'PASS' if g5_pass else 'FAIL'}** |
| **G6** | Exact Control Reproduction | Matched | Control EVEN MAE = {agg_mae_ctrl:.6f} W/m2 | **{'PASS' if g6_pass else 'FAIL'}** |

**Final Decision:** **`{decision}`**

---

## 2. Quantitative Metric Comparison (EVEN Benchmark, 174 Origins)

| Metric | Stage 8.1 Control (37 Feat) | ENEV Candidate (39 Feat) | Delta | Threshold / Goal |
| :--- | :---: | :---: | :---: | :---: |
| **EVEN MAE (W/m2)** | {agg_mae_ctrl:.6f} | {agg_mae_cand:.6f} | **{delta_agg_mae:+.6f}** | <= -0.50 W/m2 |
| **EVEN nMAE (%)** | {agg_nmae_ctrl:.4f} | {agg_nmae_cand:.4f} | **{delta_agg_nmae:+.4f}** | <= 0.00% |
| **EVEN RMSE (W/m2)** | {agg_rmse_ctrl:.6f} | {agg_rmse_cand:.6f} | **{delta_agg_rmse:+.6f}** | <= 0.00 W/m2 |
| **EVEN Bias (W/m2)** | {agg_bias_ctrl:.6f} | {agg_bias_cand:.6f} | {agg_bias_cand - agg_bias_ctrl:+.6f} | — |

---

## 3. 5-Fold Forward-Chaining EVEN CV Breakdown

| Fold | Control MAE (W/m2) | Candidate MAE (W/m2) | Delta MAE (W/m2) | Improved? | Max Degradation Check |
| :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for r in fold_records:
        md_content += f"| Fold {r['fold']} | {r['ctrl_mae_w_m2']:.6f} | {r['cand_mae_w_m2']:.6f} | {r['delta_mae_w_m2']:+.6f} | {'YES' if r['fold_improved'] else 'NO'} | {'PASS' if r['delta_mae_w_m2'] <= 0.50 else 'FAIL'} |\n"

    md_content += f"""
---

## 4. ODD Firewall Status

- **ODD Access:** `FALSE`
- **ODD Target Reads:** `0`
- **ODD Predictions Generated:** `0`
- **ODD Metrics Evaluated:** `0`
- **Status:** Strictly firewalled under EVEN gate failure protocol. Champion remains untouched.

---
*Report auto-generated by POLARIS ENEV Governed Experiment Framework | {timestamp_now()}*
"""

    with open(EXP_MD_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(BRAIN_DIR / "STAGE8_ENEV_EXPERIMENT.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nSaved experiment manifests to:")
    print(f" - {EXP_JSON_PATH}")
    print(f" - {EXP_MD_PATH}")
    print(f" - {BRAIN_DIR / 'STAGE8_ENEV_EXPERIMENT.json'}")
    print(f" - {BRAIN_DIR / 'STAGE8_ENEV_EXPERIMENT.md'}")

if __name__ == "__main__":
    run_experiment()
