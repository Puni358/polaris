#!/usr/bin/env python3
"""
POLARIS STAGE 7.2 — MEPS NATIVE SURFACE RADIATION EXPERIMENT PIPELINE
========================================================================
Executes 5-fold forward-chaining EVEN CV on 174 EVEN development origins.
Tests E0 Control vs E1, E2, E3, E4 candidate feature representations.

Protocol Locks:
- 173 ODD test origins 100% UNTOUCHED.
- Model & Hyperparameters frozen from Stage 6.6.
- 5 Predeclared Acceptance Gates against E0 Control.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage7_2_meps_native_radiation"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

# Datasets
SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEATURES_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
MEPS_RAD_FEATURES_PATH = STAGE_DIR / "meps_radiation_features.csv"

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

def main():
    print("================================================================================")
    print("POLARIS STAGE 7.2 — MEPS NATIVE SURFACE RADIATION FORECASTING EXPERIMENT")
    print("================================================================================")
    
    if not MEPS_RAD_FEATURES_PATH.exists():
        print(f"ERROR: Features file missing at {MEPS_RAD_FEATURES_PATH}!")
        return
        
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
    
    lwp_feat = pd.read_csv(STAGE6_6_FEATURES_PATH)
    lwp_feat["forecast_start"] = pd.to_datetime(lwp_feat["forecast_start"])
    
    rad_feat = pd.read_csv(MEPS_RAD_FEATURES_PATH)
    rad_feat["forecast_start"] = pd.to_datetime(rad_feat["forecast_start"])
    
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
    
    # Merge Stage 7.2 radiation features
    rad_cols = [
        "forecast_start", "horizon_hour", "meps_sw_instant", "meps_sw_hourly_derived",
        "meps_net_sw_hourly_derived", "meps_clearsky_net_sw_hourly_derived", "meps_dni_hourly_derived"
    ]
    df = df.merge(rad_feat[rad_cols], on=["forecast_start", "horizon_hour"], how="left")
    
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
    even_origins_sorted = sorted(even_origins)
    
    # Rolling Context Features
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
    
    # Define Feature Sets for E0, E1, E2, E3, E4
    e0_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
        "lwp_latest", "iwp_latest", "lwp_x_cloud"
    ]
    
    experiments = {
        "E0": e0_features,
        "E1": e0_features + ["meps_sw_instant"],
        "E2": e0_features + ["meps_sw_hourly_derived"],
        "E3": e0_features + ["meps_sw_instant", "meps_sw_hourly_derived", "meps_net_sw_hourly_derived", "meps_clearsky_net_sw_hourly_derived"],
        "E4": e0_features + ["meps_sw_hourly_derived", "meps_dni_hourly_derived"]
    }
    
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
    exp_results = {}
    
    for exp_name, feat_list in experiments.items():
        print(f"\n--- Running 5-Fold EVEN CV for Experiment {exp_name} ({len(feat_list)} features) ---")
        fold_metrics = []
        val_preds_list = []
        
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
            
            X_tr = tr_day[feat_list].values
            X_val = val_day[feat_list].values
            
            model = HistGradientBoostingRegressor(
                loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
            )
            model.fit(X_tr, res_tr)
            pred_res = model.predict(X_val)
            pred_val = np.maximum(0.0, st4_val_day + pred_res)
            pred_val[val_day["is_night_causal"].values] = 0.0
            
            mae_fold = mean_absolute_error(y_val, pred_val)
            rmse_fold = np.sqrt(mean_squared_error(y_val, pred_val))
            bias_fold = float(np.mean(pred_val - y_val))
            y_val_mean = float(np.mean(y_val))
            nmae_fold = (mae_fold / y_val_mean) * 100.0
            
            fold_metrics.append({
                "fold": fold,
                "mae": mae_fold,
                "nmae": nmae_fold,
                "rmse": rmse_fold,
                "bias": bias_fold
            })
            
            val_df_res = val_day[["forecast_start", "horizon_hour", "actual_SW_IN"]].copy()
            val_df_res["pred"] = pred_val
            val_preds_list.append(val_df_res)
            
        df_fold_res = pd.DataFrame(fold_metrics)
        df_val_preds = pd.concat(val_preds_list, ignore_index=True)
        
        agg_mae = float(df_fold_res["mae"].mean())
        agg_nmae = float(df_fold_res["nmae"].mean())
        agg_rmse = float(df_fold_res["rmse"].mean())
        agg_bias = float(df_fold_res["bias"].mean())
        
        exp_results[exp_name] = {
            "features": feat_list,
            "agg_mae": agg_mae,
            "agg_nmae": agg_nmae,
            "agg_rmse": agg_rmse,
            "agg_bias": agg_bias,
            "fold_df": df_fold_res,
            "val_preds": df_val_preds
        }
        
        print(f"  {exp_name} Aggregate Results -> MAE: {agg_mae:.4f} W/m², nMAE: {agg_nmae:.2f}%, RMSE: {agg_rmse:.4f} W/m², Bias: {agg_bias:+.4f} W/m²")

    # Verify E0 Control Reproduction
    e0_mae = exp_results["E0"]["agg_mae"]
    e0_repro_diff = abs(e0_mae - 38.2806)
    print(f"\n========================================================")
    print(f"E0 CONTROL REPRODUCTION CHECK:")
    print(f"  Expected E0 MAE: 38.2806 W/m²")
    print(f"  Observed E0 MAE: {e0_mae:.4f} W/m² (Diff: {e0_repro_diff:.6f} W/m²)")
    if e0_repro_diff < 0.05:
        print("  ✓ E0 CONTROL REPRODUCED SUCCESSFULLY")
    else:
        print("  FATAL: E0 CONTROL REPRODUCTION FAILED!")
        return

    # Compare E1, E2, E3, E4 against E0 Control
    e0_fold_maes = exp_results["E0"]["fold_df"]["mae"].values
    
    cv_summary_rows = []
    per_fold_comparison_rows = []
    decisions = {}
    
    for exp_name in ["E0", "E1", "E2", "E3", "E4"]:
        res = exp_results[exp_name]
        fold_maes = res["fold_df"]["mae"].values
        deltas = fold_maes - e0_fold_maes
        
        agg_mae = res["agg_mae"]
        agg_nmae = res["agg_nmae"]
        agg_rmse = res["agg_rmse"]
        agg_bias = res["agg_bias"]
        delta_agg_mae = agg_mae - e0_mae
        
        gate1_pass = agg_mae <= (e0_mae - 0.20)
        gate2_improved_folds = int((deltas <= 0.0).sum()) if exp_name != "E0" else 5
        gate2_pass = gate2_improved_folds >= 4
        gate3_max_degrad = float(np.max(deltas)) if exp_name != "E0" else 0.0
        gate3_pass = gate3_max_degrad <= 0.15
        gate4_pass = agg_nmae <= exp_results["E0"]["agg_nmae"]
        gate5_pass = agg_rmse <= exp_results["E0"]["agg_rmse"]
        
        all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass if exp_name != "E0" else True
        
        status = "CONTROL_REPRODUCED" if exp_name == "E0" else ("PASS" if all_gates_pass else "REJECTED")
        decisions[exp_name] = status
        
        cv_summary_rows.append({
            "experiment_id": exp_name,
            "feature_count": len(res["features"]),
            "agg_mae_w_m2": agg_mae,
            "delta_mae_w_m2": delta_agg_mae,
            "agg_nmae_pct": agg_nmae,
            "agg_rmse_w_m2": agg_rmse,
            "agg_bias_w_m2": agg_bias,
            "gate1_pass": gate1_pass,
            "gate2_folds_improved": gate2_improved_folds,
            "gate2_pass": gate2_pass,
            "gate3_max_degrad_w_m2": gate3_max_degrad,
            "gate3_pass": gate3_pass,
            "gate4_pass": gate4_pass,
            "gate5_pass": gate5_pass,
            "overall_status": status
        })
        
        for f_idx in range(5):
            per_fold_comparison_rows.append({
                "experiment_id": exp_name,
                "fold": f_idx + 1,
                "mae_w_m2": fold_maes[f_idx],
                "e0_mae_w_m2": e0_fold_maes[f_idx],
                "delta_mae_w_m2": deltas[f_idx],
                "fold_pass": deltas[f_idx] <= 0.0 if exp_name != "E0" else True
            })

    df_cv_summary = pd.DataFrame(cv_summary_rows)
    df_cv_summary.to_csv(STAGE_DIR / "stage7_2_even_cv_results.csv", index=False)
    
    df_fold_summary = pd.DataFrame(per_fold_comparison_rows)
    df_fold_summary.to_csv(STAGE_DIR / "stage7_2_fold_results.csv", index=False)

    # Generate decision JSON
    passed_exps = [k for k, v in decisions.items() if v == "PASS"]
    final_stage_decision = "PASS" if passed_exps else "STAGE 7.2 = NO IMPROVEMENT (STAGE 6.6 REMAINS CHAMPION)"
    
    decision_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "POLARIS Stage 7.2 MEPS Native Radiation Experiment",
        "frozen_champion": "Stage 6.6 LWP/IWP",
        "e0_control_mae_w_m2": e0_mae,
        "experiment_decisions": decisions,
        "passed_candidates": passed_exps,
        "final_stage_decision": final_stage_decision,
        "odd_test_set_locked": True,
        "odd_accessed": False
    }
    
    with open(STAGE_DIR / "stage7_2_decision.json", "w") as f:
        json.dump(decision_data, f, indent=2)
        
    print("\n========================================================")
    print("STAGE 7.2 EXPERIMENT SUMMARY & DECISIONS:")
    print("========================================================")
    print(df_cv_summary[["experiment_id", "feature_count", "agg_mae_w_m2", "delta_mae_w_m2", "gate1_pass", "gate2_folds_improved", "overall_status"]].to_string(index=False))
    print(f"\nFINAL DECISION: {final_stage_decision}")

if __name__ == "__main__":
    main()
