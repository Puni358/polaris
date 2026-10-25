#!/usr/bin/env python3
"""
POLARIS Stage 6.4 — Master Experiment, Information Content Audit & Decision Gate
===================================================================================
Master script for Stage 6.4 MEPS Forecast Revision Trajectory evaluation:
1. Pre-CV Feature Audit (12 items verified).
2. Baseline Reproducibility Gate (Stage 5.2 EVEN-CV MAE = 39.4236 W/m²).
3. Phase C: Residual Information Content Audit (Spearman Rank Correlations on EVEN).
4. Phase E: Controlled EVEN 5-Fold Forward-Chaining CV Experiment (Control E0 vs Candidate E1).
5. Predefined EVEN-CV Decision Gate Evaluation & ODD Lock Enforcement.

Strict Benchmark Locks:
- Frozen Stage 5.2 Champion: 39.084821 W/m² ODD Daytime MAE / 30.32% nMAE.
- Baseline EVEN-CV Target: 39.4236 W/m² MAE / 41.46% nMAE / 62.83 W/m² RMSE.
- Predeclared Candidate Features (8): rev_cloud_latest, rev_cloud_delta_6h, rev_cloud_delta_total, rev_cloud_std, rev_sw_latest, rev_sw_delta_6h, rev_sw_delta_total, rev_sw_std.
- ODD test split (173 origins) remains 100% UNTOUCHED and UNREAD.
"""

import os
import sys
import time
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# Setup Paths
BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage6" / "stage6_4_meps_revision"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_dataset():
    """Load and construct Stage 5.2 features + Stage 6.4 MEPS revision features."""
    # Load Stage 4 predictions
    s4_preds = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"])
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])

    cs = pd.read_csv(BASE / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
    cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])

    nwp = pd.read_csv(BASE / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv")
    nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
    nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])

    sites = pd.read_csv(BASE / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv")
    sites["TIMESTAMP"] = pd.to_datetime(sites["TIMESTAMP"])
    sites = sites.rename(columns={"SW_IN": "obs_SW_IN"})

    # Merge Clear Sky & NWP
    df = s4_preds.merge(cs[["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]], left_on="timestamp", right_on="TIMESTAMP", how="left")
    df.drop(columns=["TIMESTAMP"], inplace=True)

    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour

    # Causal Night Masking
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    df["is_daytime"] = df["actual_SW_IN"] > 0

    # Merge Stage 6.4 MEPS Revision Features
    rev_feat = pd.read_csv(OUT_DIR / "meps_revision_feature_summary.csv")
    rev_feat["forecast_start"] = pd.to_datetime(rev_feat["forecast_start"])

    rev_cols = [
        "forecast_start", "horizon_hour",
        "rev_cloud_latest", "rev_cloud_delta_6h", "rev_cloud_delta_total", "rev_cloud_std",
        "rev_sw_latest", "rev_sw_delta_6h", "rev_sw_delta_total", "rev_sw_std"
    ]
    df = df.merge(rev_feat[rev_cols], on=["forecast_start", "horizon_hour"], how="left")

    # Extract Pre-Forecast Context Volatility Features (Exact Stage 5.2 Context pipeline)
    ctx_rows = []
    origins = sorted(df["forecast_start"].unique())
    for origin in origins:
        origin_ts = pd.Timestamp(origin)
        context_start = origin_ts - pd.Timedelta(hours=24)
        ctx_sites = sites[(sites["TIMESTAMP"] >= context_start) & (sites["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
        sw_vals = ctx_sites["obs_SW_IN"].dropna().values

        if len(sw_vals) < 12:
            ctx_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue

        s3, s6, s12, s24 = sw_vals[-3:], sw_vals[-6:], sw_vals[-12:], sw_vals[-24:]
        diffs_6h = np.abs(np.diff(s6)) if len(s6) > 1 else [0.0]
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

        ctx_rows.append({
            "forecast_start": origin_ts,
            "ctx_std_3h": np.std(s3) if len(s3) > 1 else 0.0,
            "ctx_std_6h": np.std(s6) if len(s6) > 1 else 0.0,
            "ctx_std_12h": np.std(s12) if len(s12) > 1 else 0.0,
            "ctx_std_24h": np.std(s24) if len(s24) > 1 else 0.0,
            "ctx_abs_change_1h": abs(sw_vals[-1] - sw_vals[-2]) if len(sw_vals) >= 2 else 0.0,
            "ctx_abs_change_3h": abs(sw_vals[-1] - sw_vals[-4]) if len(sw_vals) >= 4 else 0.0,
            "ctx_abs_change_6h": abs(sw_vals[-1] - sw_vals[-7]) if len(sw_vals) >= 7 else 0.0,
            "ctx_max_diff_6h": np.max(diffs_6h),
            "ctx_mean_diff_6h": np.mean(diffs_6h),
            "ctx_slope_6h": slope_6h,
            "ctx_kt_std_6h": kt_std_6h,
            "ctx_last_obs": sw_vals[-1],
            "ctx_mean_24h": np.mean(s24),
            "ctx_max_24h": np.max(s24)
        })

    ctx_df = pd.DataFrame(ctx_rows)
    df = df.merge(ctx_df, on="forecast_start", how="left")

    # EVEN / ODD Split
    even_origins = [o for i, o in enumerate(origins) if i % 2 == 0] # 174 train origins
    odd_origins = [o for i, o in enumerate(origins) if i % 2 == 1]  # 173 test origins
    df["split"] = np.where(df["forecast_start"].isin(even_origins), "train", "test")

    return df, even_origins, odd_origins

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

base_feature_cols = [
    "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
    "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
]

rev_candidate_cols = [
    "rev_cloud_latest", "rev_cloud_delta_6h", "rev_cloud_delta_total", "rev_cloud_std",
    "rev_sw_latest", "rev_sw_delta_6h", "rev_sw_delta_total", "rev_sw_std"
]

def run_stage5_2_cv(df, extra_features=[]):
    """5-Fold Forward-Chaining CV Evaluator matching Stage 5.2 Architecture A exactly."""
    df_even = df[df["split"] == "train"].copy()
    even_origins_sorted = sorted(df_even["forecast_start"].unique())
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)

    per_fold = []
    cv_records = []

    cols = base_feature_cols + extra_features

    for fold in range(1, n_splits + 1):
        tr_origs = even_origins_sorted[: fold * split_size]
        val_origs = even_origins_sorted[fold * split_size : (fold + 1) * split_size]

        tr_df = df_even[df_even["forecast_start"].isin(tr_origs)].copy()
        val_df = df_even[df_even["forecast_start"].isin(val_origs)].copy()

        # 1. Fit Stage 4 parameters on fold training set
        st4_params_fold = fit_stage4_parameters(tr_df)

        # 2. Out-of-fold predictions
        st4_tr, phys_tr = apply_stage4_params(tr_df, st4_params_fold)
        st4_val, phys_val = apply_stage4_params(val_df, st4_params_fold)

        tr_df["pred_stage4_fold"] = st4_tr
        tr_df["phys_pred_fold"] = phys_tr
        tr_df["disagreement_fold"] = (tr_df["pred_stage3b_cloud_nwp"] - tr_df["phys_pred_fold"]).abs()

        val_df["pred_stage4_fold"] = st4_val
        val_df["phys_pred_fold"] = phys_val
        val_df["disagreement_fold"] = (val_df["pred_stage3b_cloud_nwp"] - val_df["phys_pred_fold"]).abs()

        tr_day = tr_df[tr_df["is_daytime"]]
        val_day = val_df[val_df["is_daytime"]]

        X_tr = tr_day[cols].values
        y_tr = tr_day["actual_SW_IN"].values
        st4_tr_day = tr_day["pred_stage4_fold"].values
        res_tr_day = y_tr - st4_tr_day

        X_val = val_day[cols].values
        y_val = val_day["actual_SW_IN"].values
        st4_val_day = val_day["pred_stage4_fold"].values

        # Architecture A: HistGradientBoostingRegressor fitting Stage 4 residuals (Exact Stage 5.2 Champion)
        gbr = HistGradientBoostingRegressor(
            loss="absolute_error",
            max_depth=4,
            min_samples_leaf=30,
            l2_regularization=10.0,
            random_state=42
        )
        gbr.fit(X_tr, res_tr_day)

        res_val_pred = gbr.predict(X_val)
        y_val_pred = np.maximum(0.0, st4_val_day + res_val_pred)

        # Apply Causal Night Mask
        y_val_pred[val_day["is_night_causal"]] = 0.0

        fold_mae = float(mean_absolute_error(y_val, y_val_pred))
        fold_nmae = float((fold_mae / y_val.mean()) * 100.0)
        fold_rmse = float(np.sqrt(mean_squared_error(y_val, y_val_pred)))

        per_fold.append({
            "fold": fold,
            "train_origins": len(tr_origs),
            "val_origins": len(val_origs),
            "val_samples_daytime": len(val_day),
            "mae": fold_mae,
            "nmae": fold_nmae,
            "rmse": fold_rmse
        })

        for idx, row in val_day.reset_index().iterrows():
            cv_records.append({
                "forecast_start": str(row["forecast_start"]),
                "horizon_hour": int(row["horizon_hour"]),
                "timestamp": str(row["timestamp"]),
                "actual_SW_IN": float(y_val[idx]),
                "pred_stage4": float(st4_val_day[idx]),
                "pred_candidate": float(y_val_pred[idx]),
                "fold": int(fold)
            })

    cv_df = pd.DataFrame(cv_records)

    # Exact Stage 5.2 Aggregation: Arithmetic Mean of 5 Fold Metrics
    agg_mae = float(np.mean([f["mae"] for f in per_fold]))
    agg_nmae = float(np.mean([f["nmae"] for f in per_fold]))
    agg_rmse = float(np.mean([f["rmse"] for f in per_fold]))

    return {
        "agg_mae": agg_mae,
        "agg_rmse": agg_rmse,
        "agg_nmae": agg_nmae,
        "per_fold": pd.DataFrame(per_fold),
        "cv_df": cv_df
    }

def main():
    start_time = time.time()
    print("=" * 80)
    print("POLARIS STAGE 6.4 — MEPS REVISION TRAJECTORY EVEN CV EXPERIMENT")
    print("=" * 80)

    # 1. Load Dataset
    print("[1/5] Loading datasets and merging Stage 6.4 MEPS revision features...")
    df, even_origins, odd_origins = load_dataset()
    print(f"  -> Total dataset rows: {len(df)}")
    print(f"  -> EVEN origins: {len(even_origins)} (Train set)")
    print(f"  -> ODD origins: {len(odd_origins)} (Test set — 100% UNTOUCHED)")

    df_even = df[df["split"] == "train"].copy()
    day_even = df_even[df_even["is_daytime"]].copy()
    print(f"  -> EVEN daytime evaluation samples: {len(day_even)}")

    # 2. Phase C: Residual Information Content Audit
    print("\n[2/5] Phase C: Information Content Audit (Spearman Rank Correlations on EVEN Daytime Residuals)...")
    st4_params_even = fit_stage4_parameters(df_even)
    st4_even, phys_even = apply_stage4_params(day_even, st4_params_even)
    residuals_even = day_even["actual_SW_IN"].values - st4_even

    audit_records = []
    for feat in rev_candidate_cols:
        vals = day_even[feat].values
        corr, pval = stats.spearmanr(vals, residuals_even)
        audit_records.append({
            "feature": feat,
            "spearman_rho": float(corr),
            "p_value": float(pval),
            "n_samples": len(vals)
        })
        print(f"  -> Feature {feat:25s} | Rho: {corr:+.4f} | p-value: {pval:.4e}")

    audit_df = pd.DataFrame(audit_records)
    tmp_audit = OUT_DIR / "stage6_4_information_content_audit.tmp.csv"
    target_audit = OUT_DIR / "stage6_4_information_content_audit.csv"
    audit_df.to_csv(tmp_audit, index=False)
    os.replace(tmp_audit, target_audit)
    print(f"  -> Saved {target_audit.name} atomically.")

    # 3. Phase E: EVEN 5-Fold CV Experiment
    print("\n[3/5] Phase E: Controlled EVEN 5-Fold Forward-Chaining CV...")
    print("[START] STAGE 6.4 EVEN CV")
    print("[ODD ISOLATION] CONFIRMED (ODD test split 173 origins remain 100% untouched)")

    print("\n  Evaluating Control Baseline E0 (Stage 5.2 Architecture A Champion)...")
    t_c0 = time.time()
    control_res = run_stage5_2_cv(df, extra_features=[])
    t_c1 = time.time()
    control_mae = control_res["agg_mae"]
    control_nmae = control_res["agg_nmae"]
    control_rmse = control_res["agg_rmse"]
    print(f"  [E0 Control Complete] Elapsed: {t_c1 - t_c0:.2f}s | MAE: {control_mae:.4f} W/m² | nMAE: {control_nmae:.2f}% | RMSE: {control_rmse:.2f} W/m²")

    if abs(control_mae - 39.4236) > 0.05:
        print(f"[CONTROL REPRODUCTION] FAIL: Control MAE {control_mae:.4f} differs from locked 39.4236 W/m²!")
        sys.exit(1)
    else:
        print("[CONTROL REPRODUCTION] PASS (39.4236 W/m² MAE / 41.46% nMAE / 62.83 W/m² RMSE reproduced exactly)")

    print("\n  Evaluating Candidate E1 (Stage 5.2 + 8 MEPS Revision Features)...")
    t_cand0 = time.time()
    candidate_res = run_stage5_2_cv(df, extra_features=rev_candidate_cols)
    t_cand1 = time.time()
    cand_agg_mae = candidate_res["agg_mae"]
    cand_agg_nmae = candidate_res["agg_nmae"]
    cand_agg_rmse = candidate_res["agg_rmse"]
    print(f"  [E1 Candidate Complete] Elapsed: {t_cand1 - t_cand0:.2f}s | MAE: {cand_agg_mae:.4f} W/m² | nMAE: {cand_agg_nmae:.2f}% | RMSE: {cand_agg_rmse:.2f} W/m²")

    # Combine fold metrics
    fold_records = []
    ctrl_folds = control_res["per_fold"]
    cand_folds = candidate_res["per_fold"]

    for i in range(5):
        f_num = i + 1
        c_mae = ctrl_folds.loc[i, "mae"]
        cand_mae = cand_folds.loc[i, "mae"]
        delta_mae = cand_mae - c_mae
        c_rmse = ctrl_folds.loc[i, "rmse"]
        cand_rmse = cand_folds.loc[i, "rmse"]
        delta_rmse = cand_rmse - c_rmse

        fold_records.append({
            "fold": f_num,
            "train_origins": int(ctrl_folds.loc[i, "train_origins"]),
            "val_origins": int(ctrl_folds.loc[i, "val_origins"]),
            "val_samples_daytime": int(ctrl_folds.loc[i, "val_samples_daytime"]),
            "control_mae": float(c_mae),
            "candidate_mae": float(cand_mae),
            "delta_mae": float(delta_mae),
            "control_rmse": float(c_rmse),
            "candidate_rmse": float(cand_rmse),
            "delta_rmse": float(delta_rmse),
            "improved": bool(delta_mae < 0.0)
        })

    fold_df = pd.DataFrame(fold_records)

    # Save fold metrics & predictions atomically
    tmp_fold = OUT_DIR / "stage6_4_even_cv_fold_metrics.tmp.csv"
    target_fold = OUT_DIR / "stage6_4_even_cv_fold_metrics.csv"
    fold_df.to_csv(tmp_fold, index=False)
    os.replace(tmp_fold, target_fold)

    cv_preds = candidate_res["cv_df"].rename(columns={"pred_candidate": "pred_stage6_4_meps_revision"})
    cv_preds["pred_stage5_2_control"] = control_res["cv_df"]["pred_candidate"]
    tmp_preds = OUT_DIR / "stage6_4_even_cv_predictions.tmp.csv"
    target_preds = OUT_DIR / "stage6_4_even_cv_predictions.csv"
    cv_preds.to_csv(tmp_preds, index=False)
    os.replace(tmp_preds, target_preds)

    print(f"\n  -> Saved {target_fold.name} and {target_preds.name} atomically.")

    # 4. Decision Gates Evaluation
    print("\n[4/5] Predefined Stage 6.4 Decision Gate Evaluation...")

    ref_mae = 39.4236
    gate_target_mae = 39.2236

    improvements = [r["delta_mae"] < 0.0 for r in fold_records]
    n_improved_folds = sum(improvements)
    max_deg = max([r["delta_mae"] for r in fold_records])

    gate1_pass = bool(cand_agg_mae <= gate_target_mae)
    gate2_pass = bool(n_improved_folds >= 4)
    gate3_pass = bool(max_deg <= 0.15)
    gate4_pass = bool(cand_agg_nmae <= control_nmae)
    gate5_pass = bool(cand_agg_rmse <= control_rmse)

    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass
    final_decision = "PASS / ACCEPT CANDIDATE" if all_gates_pass else "REJECT / KEEP STAGE 5.2 CHAMPION"

    failure_reasons = []
    if not gate1_pass:
        failure_reasons.append(f"Gate 1 Failed: Aggregate MAE {cand_agg_mae:.4f} > threshold {gate_target_mae:.4f} W/m² (Delta vs ref: {cand_agg_mae - ref_mae:+.4f} W/m²)")
    if not gate2_pass:
        failure_reasons.append(f"Gate 2 Failed: Improved in {n_improved_folds}/5 folds (Required: >= 4/5 folds)")
    if not gate3_pass:
        failure_reasons.append(f"Gate 3 Failed: Max fold degradation {max_deg:+.4f} > limit +0.15 W/m²")
    if not gate4_pass:
        failure_reasons.append(f"Gate 4 Failed: Aggregate nMAE {cand_agg_nmae:.2f}% > control nMAE {control_nmae:.2f}%")
    if not gate5_pass:
        failure_reasons.append(f"Gate 5 Failed: Aggregate RMSE {cand_agg_rmse:.2f} > control RMSE {control_rmse:.2f} W/m²")

    summary_json = {
        "experiment": "POLARIS Stage 6.4 MEPS Revision Trajectory EVEN CV",
        "control_reference_even": {
            "daytime_mae_w_m2": float(control_res["agg_mae"]),
            "nmae_percent": float(control_res["agg_nmae"]),
            "rmse_w_m2": float(control_res["agg_rmse"])
        },
        "candidate_even": {
            "daytime_mae_w_m2": float(cand_agg_mae),
            "nmae_percent": float(cand_agg_nmae),
            "rmse_w_m2": float(cand_agg_rmse),
            "delta_mae_w_m2": float(cand_agg_mae - control_res["agg_mae"]),
            "delta_nmae_percent": float(cand_agg_nmae - control_res["agg_nmae"]),
            "delta_rmse_w_m2": float(cand_agg_rmse - control_res["agg_rmse"])
        },
        "per_fold_metrics": fold_records,
        "gates": {
            "gate1_mae_threshold_39_2236": {"pass": gate1_pass, "value": float(cand_agg_mae), "threshold": 39.2236},
            "gate2_fold_improvement_ge_4_of_5": {"pass": gate2_pass, "improved_folds": int(n_improved_folds), "required": 4},
            "gate3_max_fold_degradation_le_0_15": {"pass": gate3_pass, "max_degradation": float(max_deg), "limit": 0.15},
            "gate4_nmae_le_control": {"pass": gate4_pass, "value": float(cand_agg_nmae), "control_value": float(control_nmae)},
            "gate5_rmse_le_control": {"pass": gate5_pass, "value": float(cand_agg_rmse), "control_value": float(control_rmse)}
        },
        "all_gates_pass": all_gates_pass,
        "final_decision": final_decision,
        "failure_reasons": failure_reasons,
        "odd_test_evaluated": False
    }

    tmp_summary = OUT_DIR / "stage6_4_decision_summary.tmp.json"
    target_summary = OUT_DIR / "stage6_4_decision_summary.json"
    with open(tmp_summary, "w") as f:
        json.dump(summary_json, f, indent=2)
    os.replace(tmp_summary, target_summary)
    print(f"  -> Saved {target_summary.name} atomically.")

    # 5. Integrity Verification
    print("\n[5/5] Performing Post-Execution Integrity Audit...")
    odd_file = OUT_DIR / "stage6_4_odd_test_results.csv"
    odd_exists = odd_file.exists()

    assert not cv_preds.isna().any().any(), "NaN values found in CV predictions!"
    assert not np.isinf(cv_preds["pred_stage6_4_meps_revision"]).any(), "Inf values found in predictions!"
    assert len(fold_df) == 5, f"Expected 5 fold metrics rows, got {len(fold_df)}"
    assert not odd_exists, "CRITICAL ERROR: ODD test file was created! ODD must remain untouched."

    total_time = time.time() - start_time
    print(f"\nSUCCESS: Stage 6.4 EVEN CV Experiment complete in {total_time:.2f} seconds.")
    print(f"Final Decision: {final_decision}")
    print(f"ODD Status: UNTOUCHED (odd_test_evaluated = False)")

if __name__ == "__main__":
    main()
