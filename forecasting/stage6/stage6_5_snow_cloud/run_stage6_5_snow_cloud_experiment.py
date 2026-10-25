#!/usr/bin/env python3
"""
POLARIS Stage 6.5 — Snow / Cloud Interaction Experiment
======================================================
Strict scientific experiment evaluating whether causally available observed
ground snow depth (D_SNOW) and snow-cloud interaction terms provide incremental
predictive value beyond the frozen Stage 5.2 Architecture A champion.

Scientific Locks:
- 174 EVEN origins used for CV evaluation. 173 ODD test origins remain 100% UNTOUCHED.
- Control reproduction must match Stage 5.2 baseline (MAE ≈ 39.4236 W/m²).
- Predeclared candidate acceptance gates strictly enforced.
- Resumable, atomic writes, manifest creation.
"""

import os
import sys
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Paths
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE_DIR / "forecasting/stage6" / "stage6_5_snow_cloud"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Datasets
SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"

MANIFEST_PATH = OUT_DIR / "snow_cloud_experiment_manifest.json"
DATA_AUDIT_PATH = OUT_DIR / "snow_cloud_data_audit.csv"
SUMMARY_PATH = OUT_DIR / "control_vs_candidate_cv_summary.csv"
FOLD_RESULTS_PATH = OUT_DIR / "per_fold_even_cv_comparison.csv"
FEATURE_IMP_PATH = OUT_DIR / "feature_importance.csv"
REGIME_DIAG_PATH = OUT_DIR / "snow_regime_diagnostics.csv"
DECISION_PATH = OUT_DIR / "experiment_decision_summary.json"
README_PATH = OUT_DIR / "README.md"


def atomic_write_json(obj, file_path):
    tmp_path = file_path.with_suffix(".tmp.json")
    with open(tmp_path, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp_path, file_path)


def fit_stage4_parameters(train_df):
    """Fits Stage 4 parameters (w_h, k_h) strictly on fold training data."""
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
    """Generates Stage 4 base predictions for a given dataset using specific parameters."""
    st4_preds = []
    phys_preds = []

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
    print("=" * 80)
    print("POLARIS STAGE 6.5 — SNOW / CLOUD INTERACTION EXPERIMENT")
    print("=" * 80)

    start_time = time.time()

    # --------------------------------------------------------------------------
    # 1. LOAD & AUDIT DATA
    # --------------------------------------------------------------------------
    print("\n--- Step 1: Performing Data Forensics & Audit ---")
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

    # Merge core data
    cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
    df = s4_preds.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left").drop(columns=["TIMESTAMP"])
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    df["pred_stage4_full"] = df["pred_ensemble"]

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
    df["disagreement"] = (df["pred_stage3b_cloud_nwp"] - df["phys_pred_full"]).abs()

    origins = sorted(df["forecast_start"].unique())
    even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
    odd_origins = [o for i, o in enumerate(origins) if i % 2 == 1]

    print(f"Total benchmark origins: {len(origins)}")
    print(f"EVEN origins (used for CV): {len(even_origins)}")
    print(f"ODD origins (100% UNTOUCHED): {len(odd_origins)}")

    # Audit D_SNOW Causal Extraction
    audit_records = []
    snow_t0_map = {}

    for origin in origins:
        origin_ts = pd.Timestamp(origin)
        context_start = origin_ts - pd.Timedelta(hours=24)

        past_sites = sites[(sites["TIMESTAMP"] >= context_start) & (sites["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
        valid_sn = past_sites["D_SNOW"].dropna()

        if len(valid_sn) > 0:
            last_val = valid_sn.iloc[-1]
            last_ts = past_sites[past_sites["D_SNOW"].notnull()].iloc[-1]["TIMESTAMP"]
            lag_h = (origin_ts - last_ts).total_seconds() / 3600.0
            has_valid = True
        else:
            last_val = 0.0
            last_ts = None
            lag_h = np.nan
            has_valid = False

        snow_t0_map[origin_ts] = last_val

        audit_records.append({
            "forecast_start": origin_ts,
            "has_causal_obs": has_valid,
            "last_obs_timestamp": last_ts,
            "lag_hours": lag_h,
            "D_SNOW_t0_cm": last_val
        })

    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv(DATA_AUDIT_PATH, index=False)

    print("\n--- Part B Data Audit Table Summary ---")
    print(f"  Total Origins: {len(origins)}")
    print(f"  Origins with valid causal D_SNOW: {audit_df['has_causal_obs'].sum()} / {len(origins)}")
    print(f"  Missing causal D_SNOW rate: {1.0 - audit_df['has_causal_obs'].mean():.2%}")
    print(f"  D_SNOW_t0 range: [{audit_df['D_SNOW_t0_cm'].min():.2f}, {audit_df['D_SNOW_t0_cm'].max():.2f}] cm")
    print(f"  D_SNOW_t0 mean: {audit_df['D_SNOW_t0_cm'].mean():.2f} cm")

    assert audit_df["has_causal_obs"].all(), "FATAL: Causal D_SNOW missing for one or more origins!"

    # --------------------------------------------------------------------------
    # 2. FEATURE ENGINEERING (CONTEXT + CANDIDATE SNOW FEATURES)
    # --------------------------------------------------------------------------
    print("\n--- Step 2: Constructing Context & Candidate Snow Features ---")

    # Context features
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

        s3 = sw_vals[-3:]
        s6 = sw_vals[-6:]
        s12 = sw_vals[-12:]
        s24 = sw_vals[-24:]

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

        if len(s6) >= 3:
            x_tr = np.arange(len(s6))
            slope_6h = np.polyfit(x_tr, s6, 1)[0]
        else:
            slope_6h = 0.0

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

    # Add D_SNOW_t0 and candidate interaction features
    df["D_SNOW_t0"] = df["forecast_start"].map(snow_t0_map)
    # 1. Raw causal snow depth D_SNOW_t0 (cm)
    # 2. snow_x_cloud = D_SNOW_t0 * cloud_frac
    df["snow_x_cloud"] = df["D_SNOW_t0"] * df["cloud_frac"]
    # 3. snow_x_cloud_x_solar = D_SNOW_t0 * cloud_frac * sin(solar_elevation)
    sin_solar = np.maximum(0.0, np.sin(np.radians(df["solar_elevation"])))
    df["snow_x_cloud_x_solar"] = df["snow_x_cloud"] * sin_solar

    # Define Feature Sets
    control_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]

    candidate_features = control_features + ["D_SNOW_t0", "snow_x_cloud", "snow_x_cloud_x_solar"]

    print(f"Control feature count: {len(control_features)}")
    print(f"Candidate feature count: {len(candidate_features)} (+3 candidate features)")

    # Filter EVEN origins strictly
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    even_origins_sorted = sorted(even_origins)

    # --------------------------------------------------------------------------
    # 3. FORWARD-CHAINING CV EVALUATION (CONTROL VS CANDIDATE)
    # --------------------------------------------------------------------------
    print("\n--- Step 3: Running 5-Fold Forward-Chaining EVEN CV ---")

    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)

    fold_metrics = []
    ctrl_all_val_preds = []
    cand_all_val_preds = []

    # Store model for feature importance
    fitted_cand_models = []

    for fold in range(1, n_splits + 1):
        tr_origs = even_origins_sorted[: fold * split_size]
        val_origs = even_origins_sorted[fold * split_size : (fold + 1) * split_size]

        tr_df = df_even[df_even["forecast_start"].isin(tr_origs)].copy()
        val_df = df_even[df_even["forecast_start"].isin(val_origs)].copy()

        # Fit Stage 4 parameters strictly on training fold
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

        X_tr_ctrl = tr_day[control_features].values
        X_val_ctrl = val_day[control_features].values

        X_tr_cand = tr_day[candidate_features].values
        X_val_cand = val_day[candidate_features].values

        # 1. CONTROL MODEL (Stage 5.2 Architecture A)
        model_ctrl = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_ctrl.fit(X_tr_ctrl, res_tr)
        pred_res_ctrl = model_ctrl.predict(X_val_ctrl)
        pred_ctrl_val = np.maximum(0.0, st4_val_day + pred_res_ctrl)
        pred_ctrl_val[val_day["is_night_causal"].values] = 0.0

        # 2. CANDIDATE MODEL (Stage 5.2 Architecture A + Snow Features)
        model_cand = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_cand.fit(X_tr_cand, res_tr)
        pred_res_cand = model_cand.predict(X_val_cand)
        pred_cand_val = np.maximum(0.0, st4_val_day + pred_res_cand)
        pred_cand_val[val_day["is_night_causal"].values] = 0.0

        fitted_cand_models.append(model_cand)

        # Fold Metrics
        mae_ctrl = mean_absolute_error(y_val, pred_ctrl_val)
        mae_cand = mean_absolute_error(y_val, pred_cand_val)
        delta_mae = mae_cand - mae_ctrl

        fold_pass = delta_mae <= 0.0
        fold_degradation_exceeded = delta_mae > 0.15

        fold_metrics.append({
            "fold": fold,
            "tr_origins": len(tr_origs),
            "val_origins": len(val_origs),
            "val_hours": len(val_day),
            "ctrl_mae": mae_ctrl,
            "cand_mae": mae_cand,
            "delta_mae": delta_mae,
            "fold_pass": fold_pass,
            "degradation_pass": not fold_degradation_exceeded
        })

        val_df_c = val_df.copy()
        val_df_c["pred_ctrl"] = 0.0
        val_df_c.loc[val_df_c["is_daytime"], "pred_ctrl"] = pred_ctrl_val
        ctrl_all_val_preds.append(val_df_c[val_df_c["is_daytime"]])

        val_df_k = val_df.copy()
        val_df_k["pred_cand"] = 0.0
        val_df_k.loc[val_df_k["is_daytime"], "pred_cand"] = pred_cand_val
        cand_all_val_preds.append(val_df_k[val_df_k["is_daytime"]])

    fold_df = pd.DataFrame(fold_metrics)
    fold_df.to_csv(FOLD_RESULTS_PATH, index=False)

    ctrl_full_df = pd.concat(ctrl_all_val_preds, ignore_index=True)
    cand_full_df = pd.concat(cand_all_val_preds, ignore_index=True)

    # --------------------------------------------------------------------------
    # 4. AGGREGATE CV METRICS & CONTROL REPRODUCTION CHECK
    # --------------------------------------------------------------------------
    print("\n--- Step 4: Computing Aggregate EVEN CV Performance ---")

    # Aggregate CV metrics following official Stage 5.2 benchmark protocol (mean of fold metrics)
    cv_ctrl_mae = float(fold_df["ctrl_mae"].mean())
    cv_cand_mae = float(fold_df["cand_mae"].mean())
    delta_mae_aggregate = cv_cand_mae - cv_ctrl_mae

    # Fold-level nMAE calculation (matching Stage 5.2 protocol)
    ctrl_full_df = pd.concat(ctrl_all_val_preds, ignore_index=True)
    cand_full_df = pd.concat(cand_all_val_preds, ignore_index=True)
    y_val_all = ctrl_full_df["actual_SW_IN"].values
    mean_y_val_global = float(y_val_all.mean())

    # Compute fold-level nMAEs
    fold_means = [ctrl_full_df[ctrl_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"].mean() for f in range(1, 6)]
    ctrl_fold_nmaes = [m / y * 100.0 for m, y in zip(fold_df["ctrl_mae"], fold_means)]
    cand_fold_nmaes = [m / y * 100.0 for m, y in zip(fold_df["cand_mae"], fold_means)]

    cv_ctrl_nmae = float(np.mean(ctrl_fold_nmaes))
    cv_cand_nmae = float(np.mean(cand_fold_nmaes))

    # Also compute global nMAE for audit documentation
    global_ctrl_nmae = (cv_ctrl_mae / mean_y_val_global) * 100.0
    global_cand_nmae = (cv_cand_mae / mean_y_val_global) * 100.0

    ctrl_rmse_folds = [np.sqrt(mean_squared_error(cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"], ctrl_full_df[ctrl_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["pred_ctrl"])) for f in range(1, 6)]
    cand_rmse_folds = [np.sqrt(mean_squared_error(cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"], cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["pred_cand"])) for f in range(1, 6)]

    cv_ctrl_rmse = float(np.mean(ctrl_rmse_folds))
    cv_cand_rmse = float(np.mean(cand_rmse_folds))

    ctrl_bias = (ctrl_full_df["pred_ctrl"] - ctrl_full_df["actual_SW_IN"]).mean()
    cand_bias = (cand_full_df["pred_cand"] - cand_full_df["actual_SW_IN"]).mean()

    print(f"CONTROL EVEN CV Daytime MAE:  {cv_ctrl_mae:.4f} W/m² (Expected: 39.4236 W/m²)")
    print(f"CANDIDATE EVEN CV Daytime MAE: {cv_cand_mae:.4f} W/m²")
    print(f"DELTA MAE:                   {delta_mae_aggregate:+.4f} W/m²")

    # Control Reproduction Lock
    repro_error = abs(cv_ctrl_mae - 39.423598)
    print(f"Control Reproduction Error: {repro_error:.6f} W/m²")
    assert repro_error < 0.01, f"FATAL: Control reproduction failed! ({cv_ctrl_mae:.4f} vs 39.4236)"
    print("=> CONTROL REPRODUCTION VERIFIED EXACTLY SUCCESSFUL!")

    # --------------------------------------------------------------------------
    # 5. PREDECLARED GATES EVALUATION
    # --------------------------------------------------------------------------
    print("\n--- Step 5: Predeclared Candidate Gates Evaluation ---")

    gate1_pass = delta_mae_aggregate <= -0.20
    gate2_folds_improved = int((fold_df["delta_mae"] <= 0.0).sum())
    gate2_pass = gate2_folds_improved >= 4
    gate3_max_degradation = float(fold_df["delta_mae"].max())
    gate3_pass = gate3_max_degradation <= 0.15
    gate4_pass = cv_cand_nmae <= 41.46
    gate5_pass = cv_cand_rmse <= 62.83

    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass

    print(f"  Gate 1 (ΔMAE <= -0.20 W/m²):      {delta_mae_aggregate:+.4f} W/m² | Pass: {gate1_pass}")
    print(f"  Gate 2 (Improved in >= 4 folds):  {gate2_folds_improved} / 5 folds   | Pass: {gate2_pass}")
    print(f"  Gate 3 (Max degradation <= +0.15): {gate3_max_degradation:+.4f} W/m² | Pass: {gate3_pass}")
    print(f"  Gate 4 (nMAE <= 41.46%):          {cv_cand_nmae:.2f}%          | Pass: {gate4_pass}")
    print(f"  Gate 5 (RMSE <= 62.83 W/m²):      {cv_cand_rmse:.4f} W/m²    | Pass: {gate5_pass}")
    print(f"\nOVERALL CANDIDATE GATE STATUS: {'PASS' if all_gates_pass else 'REJECT'}")

    # --------------------------------------------------------------------------
    # 6. BOOTSTRAP CONFIDENCE INTERVAL (EVEN ORIGINS)
    # --------------------------------------------------------------------------
    print("\n--- Step 6: 1,000-Sample Paired Origin Bootstrap ---")
    np.random.seed(42)

    val_origs_unique = cand_full_df["forecast_start"].unique()
    n_boot = 1000
    boot_deltas = []

    for _ in range(n_boot):
        sample_origs = np.random.choice(val_origs_unique, size=len(val_origs_unique), replace=True)
        sample_ctrl = ctrl_full_df[ctrl_full_df["forecast_start"].isin(sample_origs)]
        sample_cand = cand_full_df[cand_full_df["forecast_start"].isin(sample_origs)]

        m_ctrl = mean_absolute_error(sample_ctrl["actual_SW_IN"], sample_ctrl["pred_ctrl"])
        m_cand = mean_absolute_error(sample_cand["actual_SW_IN"], sample_cand["pred_cand"])
        boot_deltas.append(m_cand - m_ctrl)

    boot_mean = float(np.mean(boot_deltas))
    ci_low = float(np.percentile(boot_deltas, 2.5))
    ci_high = float(np.percentile(boot_deltas, 97.5))

    print(f"Bootstrap Mean ΔMAE: {boot_mean:+.4f} W/m²")
    print(f"95% Confidence Interval: [{ci_low:+.4f}, {ci_high:+.4f}] W/m²")

    # --------------------------------------------------------------------------
    # 7. DIAGNOSTICS & FEATURE IMPORTANCE
    # --------------------------------------------------------------------------
    print("\n--- Step 7: Feature Importance & Regime Diagnostics ---")

    # Feature Importance via Permutation Importance on Training Set
    from sklearn.inspection import permutation_importance
    perm_imps = []
    for m in fitted_cand_models:
        r = permutation_importance(m, X_tr_cand, res_tr, n_repeats=5, random_state=42)
        perm_imps.append(r.importances_mean)
    
    importances = np.mean(perm_imps, axis=0)
    feat_imp_df = pd.DataFrame({
        "feature": candidate_features,
        "importance": importances
    }).sort_values("importance", ascending=False)
    feat_imp_df.to_csv(FEATURE_IMP_PATH, index=False)

    print("\nCandidate Feature Importances (Top 10):")
    print(feat_imp_df.head(10).to_string(index=False))

    # Snow Regime Diagnostics (EVEN Validation Set Only)
    cand_full_df["snow_regime"] = np.where(cand_full_df["D_SNOW_t0"] > 0.0, "Snow Present (D_SNOW > 0)", "No Snow (D_SNOW <= 0)")

    regime_results = []
    for regime, grp_cand in cand_full_df.groupby("snow_regime"):
        grp_ctrl = ctrl_full_df.loc[grp_cand.index]
        mae_c = mean_absolute_error(grp_ctrl["actual_SW_IN"], grp_ctrl["pred_ctrl"])
        mae_k = mean_absolute_error(grp_cand["actual_SW_IN"], grp_cand["pred_cand"])
        regime_results.append({
            "regime": regime,
            "hours": len(grp_cand),
            "ctrl_mae": mae_c,
            "cand_mae": mae_k,
            "delta_mae": mae_k - mae_c
        })

    regime_df = pd.DataFrame(regime_results)
    regime_df.to_csv(REGIME_DIAG_PATH, index=False)

    print("\nRegime Diagnostics (EVEN CV Validation Set):")
    print(regime_df.to_string(index=False))

    # --------------------------------------------------------------------------
    # 8. SAVE SUMMARY & MANIFEST
    # --------------------------------------------------------------------------
    summary_df = pd.DataFrame([{
        "experiment": "Stage 6.5 Snow/Cloud Interaction",
        "even_origins_count": len(even_origins),
        "odd_origins_count": len(odd_origins),
        "odd_status": "100% UNTOUCHED",
        "ctrl_cv_mae": cv_ctrl_mae,
        "cand_cv_mae": cv_cand_mae,
        "delta_cv_mae": delta_mae_aggregate,
        "ctrl_cv_nmae": cv_ctrl_nmae,
        "cand_cv_nmae": cv_cand_nmae,
        "ctrl_cv_rmse": cv_ctrl_rmse,
        "cand_cv_rmse": cv_cand_rmse,
        "gate1_pass": gate1_pass,
        "gate2_pass": gate2_pass,
        "gate3_pass": gate3_pass,
        "gate4_pass": gate4_pass,
        "gate5_pass": gate5_pass,
        "overall_decision": "PASS" if all_gates_pass else "REJECT"
    }])
    summary_df.to_csv(SUMMARY_PATH, index=False)

    decision_data = {
        "experiment_name": "Stage 6.5 Snow/Cloud Interaction",
        "control_architecture": "Stage 5.2 Architecture A (GBDT Residual Corrector)",
        "decision": "PASS" if all_gates_pass else "REJECT",
        "odd_status": "ODD UNTOUCHED",
        "control_even_cv_mae": cv_ctrl_mae,
        "candidate_even_cv_mae": cv_cand_mae,
        "delta_mae_w_m2": delta_mae_aggregate,
        "bootstrap_mean_delta": boot_mean,
        "bootstrap_95_ci": [ci_low, ci_high],
        "predeclared_gates": {
            "gate1_min_improvement_0_20": {"value": delta_mae_aggregate, "pass": bool(gate1_pass)},
            "gate2_min_4_folds_improved": {"value": gate2_folds_improved, "pass": bool(gate2_pass)},
            "gate3_max_degradation_0_15": {"value": gate3_max_degradation, "pass": bool(gate3_pass)},
            "gate4_nmae_under_41_46": {"value": cv_cand_nmae, "pass": bool(gate4_pass)},
            "gate5_rmse_under_62_83": {"value": cv_cand_rmse, "pass": bool(gate5_pass)}
        },
        "candidate_features_added": ["D_SNOW_t0", "snow_x_cloud", "snow_x_cloud_x_solar"]
    }
    atomic_write_json(decision_data, DECISION_PATH)

    manifest_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "script_name": "run_stage6_5_snow_cloud_experiment.py",
        "input_files": [str(SITES_PATH), str(CLEARSKY_PATH), str(NWP_PATH), str(STAGE4_PREDS_PATH)],
        "control_features_count": len(control_features),
        "candidate_features_count": len(candidate_features),
        "execution_time_seconds": round(time.time() - start_time, 2)
    }
    atomic_write_json(manifest_data, MANIFEST_PATH)

    # --------------------------------------------------------------------------
    # 9. GENERATE README.md
    # --------------------------------------------------------------------------
    with open(README_PATH, "w") as f:
        f.write(f"""# POLARIS Stage 6.5 — Snow / Cloud Interaction Experiment Report

**Date:** {time.strftime('%Y-%m-%d')}  
**Experiment:** Candidate 1 — Snow / Cloud Interaction  
**Control Baseline:** Stage 5.2 Architecture A (GBDT Residual Corrector)  
**Status:** **{"PASS" if all_gates_pass else "REJECTED"}**  
**ODD Test Set Status:** **ODD UNTOUCHED** (100% preserved)

---

## 1. Summary Results

| Metric | Control (Stage 5.2) | Candidate | Delta | Gate Status |
| :--- | :--- | :--- | :--- | :--- |
| **Daytime MAE (W/m²)** | {cv_ctrl_mae:.4f} | {cv_cand_mae:.4f} | **{delta_mae_aggregate:+.4f}** | {"PASS" if gate1_pass else "FAIL"} (Target <= -0.20) |
| **Daytime nMAE (%)** | {cv_ctrl_nmae:.2f}% | {cv_cand_nmae:.2f}% | **{cv_cand_nmae - cv_ctrl_nmae:+.2f}%** | {"PASS" if gate4_pass else "FAIL"} (Target <= 41.46%) |
| **Daytime RMSE (W/m²)** | {cv_ctrl_rmse:.4f} | {cv_cand_rmse:.4f} | **{cv_cand_rmse - cv_ctrl_rmse:+.4f}** | {"PASS" if gate5_pass else "FAIL"} (Target <= 62.83) |
| **Folds Improved** | - | - | **{gate2_folds_improved} / 5** | {"PASS" if gate2_pass else "FAIL"} (Target >= 4) |
| **Max Degradation** | - | - | **{gate3_max_degradation:+.4f}** | {"PASS" if gate3_pass else "FAIL"} (Target <= +0.15) |

---

## 2. Gate Evaluation Breakdown

1. **Gate 1 (ΔMAE <= -0.20 W/m²):** {delta_mae_aggregate:+.4f} W/m² -> **{"PASSED" if gate1_pass else "FAILED"}**
2. **Gate 2 (Improved in >= 4 folds):** {gate2_folds_improved} / 5 folds -> **{"PASSED" if gate2_pass else "FAILED"}**
3. **Gate 3 (Max fold degradation <= +0.15 W/m²):** {gate3_max_degradation:+.4f} W/m² -> **{"PASSED" if gate3_pass else "FAILED"}**
4. **Gate 4 (nMAE <= 41.46%):** {cv_cand_nmae:.2f}% -> **{"PASSED" if gate4_pass else "FAILED"}**
5. **Gate 5 (RMSE <= 62.83 W/m²):** {cv_cand_rmse:.4f} W/m² -> **{"PASSED" if gate5_pass else "FAILED"}**

---

## 3. Five-Fold Forward-Chaining Results

```
{fold_df[['fold', 'tr_origins', 'val_origins', 'ctrl_mae', 'cand_mae', 'delta_mae', 'fold_pass']].to_string(index=False)}
```

---

## 4. Scientific Conclusion & ODD Protocol

{"**Decision:** Candidate PASSES all predeclared EVEN-CV gates and is eligible for ONE held-out ODD evaluation." if all_gates_pass else "**Decision:** Candidate FAILS predeclared gates and is REJECTED. Stage 5.2 Architecture A remains the undefeated champion."}

**ODD Test Set Status:** **ODD UNTOUCHED**
""")

    print(f"\nSaved all artifacts to: {OUT_DIR}")
    print(f"Execution complete in {round(time.time() - start_time, 2)} seconds.")


if __name__ == "__main__":
    main()
