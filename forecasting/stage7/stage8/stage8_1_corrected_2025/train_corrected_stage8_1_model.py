#!/usr/bin/env python3
"""
POLARIS — CORRECTED Stage 8.1 model (2024 EVEN-train / ODD-eval only).

Exact replica of the fit/eval procedure in
forecasting/stage7/stage8/stage8_1_700hpa_wind/save_stage8_1_model_artifact.py
(2024, LOCKED) -- itself a byte-identical copy of
run_official_odd_evaluation.py through every merge/split/fit step:
  - same EVEN/ODD split (positional, i % 2 on sorted origins)
  - same target: residual-on-Stage4 (actual_SW_IN - pred_stage4_fold),
    fit on EVEN daytime rows only
  - same two models: Stage 7.5 control (35 features) and Stage 8.1
    candidate (37 features = 35 + u700 + v700)
  - same estimator: sklearn.ensemble.HistGradientBoostingRegressor
    (loss="absolute_error", max_depth=4, min_samples_leaf=30,
    l2_regularization=10.0, random_state=42)
  - same evaluation: predict residual on ODD, pred = max(0, st4_odd +
    residual), zero out is_night_causal rows, compare against
    actual_SW_IN on ODD daytime rows (MAE/RMSE/bias/nMAE)

ONLY the input feature matrix differs: this reads
stage8_1_full_37_feature_matrix_2024_CORRECTED.csv (terrain + u700/v700
rebuilt with corrected causal semantics, the other 31 features
byte-for-byte the same source data as the historical 2024 pipeline).
No tuning, no hyperparameter search, no retraining of anything else.

The historical frozen artifact
(forecasting/stage7/stage8/stage8_1_700hpa_wind/model_artifact/stage8_1_candidate_37feature_model.joblib)
is never read or written by this script.

2025 is NOT evaluated here (per instructions) -- this script stops
after reporting the corrected model's 2024 ODD metrics and saving the
artifact, leaving it ready for a later, separate 2025 blind-test run.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
MATRIX_2024_PATH = OUT_DIR / "stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
ARTIFACT_DIR = OUT_DIR / "model_artifact"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ST75_PATH = ARTIFACT_DIR / "stage8_1_CORRECTED_control_35feature_model.joblib"
MODEL_E1_PATH = ARTIFACT_DIR / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
ODD_PREDS_PATH = OUT_DIR / "stage8_1_CORRECTED_official_odd_predictions_2024.csv"
RESULTS_PATH = OUT_DIR / "stage8_1_CORRECTED_official_odd_results_2024.json"
MANIFEST_PATH = ARTIFACT_DIR / "STAGE8_1_CORRECTED_MODEL_MANIFEST.json"

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
stage75_35_features = stage66_31_features + ["terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
                                               "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
candidate_37_features = stage75_35_features + ["u700", "v700"]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_json(obj, path):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def atomic_write_csv(df, path):
    tmp = str(path) + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def main():
    print("=" * 80)
    print("CORRECTED Stage 8.1 model — training (2024 EVEN) + evaluation (2024 ODD)")
    print("=" * 80)

    matrix_hash = sha256_of(MATRIX_2024_PATH)
    print(f"Input feature matrix: {MATRIX_2024_PATH}")
    print(f"Input hash: {matrix_hash}")

    df = pd.read_csv(MATRIX_2024_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    all_origins = sorted(df["forecast_start"].unique())
    even_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 0]
    odd_origins = [orig for i, orig in enumerate(all_origins) if i % 2 == 1]

    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    df_odd = df[df["forecast_start"].isin(odd_origins)].copy()

    print(f"Total Origins: {len(all_origins)} | EVEN (Train): {len(even_origins)} | ODD (Held-Out Test): {len(odd_origins)}")
    print(f"ODD Hours Total: {len(df_odd)} | Daytime: {df_odd['is_daytime'].sum()} | Night: {(~df_odd['is_daytime']).sum()}")

    even_day = df_even[df_even["is_daytime"]].copy()
    odd_day = df_odd[df_odd["is_daytime"]].copy()

    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values

    print(f"\nTrain (EVEN daytime) rows: {len(even_day)} | NaN in u700/v700 (train): "
          f"{even_day[['u700', 'v700']].isna().sum().sum()}")
    print(f"Eval  (ODD daytime)  rows: {len(odd_day)} | NaN in u700/v700 (eval):  "
          f"{odd_day[['u700', 'v700']].isna().sum().sum()}")

    # 1. Stage 7.5 control (35 features, corrected terrain)
    X_tr_st75 = even_day[stage75_35_features].values
    X_odd_st75 = odd_day[stage75_35_features].values
    model_st75 = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_st75.fit(X_tr_st75, res_tr)
    pred_res_st75 = model_st75.predict(X_odd_st75)
    pred_sw_st75_day = np.maximum(0.0, st4_odd + pred_res_st75)
    pred_sw_st75_day[odd_day["is_night_causal"].values] = 0.0

    # 2. Stage 8.1 candidate (37 features, corrected terrain + corrected u700/v700)
    X_tr_e1 = even_day[candidate_37_features].values
    X_odd_e1 = odd_day[candidate_37_features].values
    model_e1 = HistGradientBoostingRegressor(
        loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
    )
    model_e1.fit(X_tr_e1, res_tr)
    pred_res_e1 = model_e1.predict(X_odd_e1)
    pred_sw_e1_day = np.maximum(0.0, st4_odd + pred_res_e1)
    pred_sw_e1_day[odd_day["is_night_causal"].values] = 0.0

    # Save artifacts
    joblib.dump(model_st75, MODEL_ST75_PATH)
    joblib.dump(model_e1, MODEL_E1_PATH)

    # Round-trip verification (same check as the historical artifact script)
    reloaded_model_e1 = joblib.load(MODEL_E1_PATH)
    reloaded_pred_res_e1 = reloaded_model_e1.predict(X_odd_e1)
    reloaded_pred_sw_e1_day = np.maximum(0.0, st4_odd + reloaded_pred_res_e1)
    reloaded_pred_sw_e1_day[odd_day["is_night_causal"].values] = 0.0
    artifact_roundtrip_identical = bool(np.array_equal(pred_sw_e1_day, reloaded_pred_sw_e1_day))

    # 3. Full ODD prediction dataframe
    df_odd_preds = df_odd[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "is_daytime", "is_night_causal"]].copy()
    df_odd_preds["pred_stage7_5_control_CORRECTED"] = 0.0
    df_odd_preds.loc[df_odd_preds["is_daytime"], "pred_stage7_5_control_CORRECTED"] = pred_sw_st75_day
    df_odd_preds["pred_stage8_1_candidate_CORRECTED"] = 0.0
    df_odd_preds.loc[df_odd_preds["is_daytime"], "pred_stage8_1_candidate_CORRECTED"] = pred_sw_e1_day
    atomic_write_csv(df_odd_preds, ODD_PREDS_PATH)

    # 4. Metrics
    mean_y_odd = np.mean(y_odd)

    mae_st75 = float(mean_absolute_error(y_odd, pred_sw_st75_day))
    nmae_st75 = float((mae_st75 / mean_y_odd) * 100.0)
    rmse_st75 = float(np.sqrt(mean_squared_error(y_odd, pred_sw_st75_day)))
    bias_st75 = float(np.mean(pred_sw_st75_day - y_odd))

    mae_e1 = float(mean_absolute_error(y_odd, pred_sw_e1_day))
    nmae_e1 = float((mae_e1 / mean_y_odd) * 100.0)
    rmse_e1 = float(np.sqrt(mean_squared_error(y_odd, pred_sw_e1_day)))
    bias_e1 = float(np.mean(pred_sw_e1_day - y_odd))

    odd_night = df_odd[~df_odd["is_daytime"]]
    night_mae_st75 = float(mean_absolute_error(odd_night["actual_SW_IN"], df_odd_preds.loc[~df_odd_preds["is_daytime"], "pred_stage7_5_control_CORRECTED"]))
    night_mae_e1 = float(mean_absolute_error(odd_night["actual_SW_IN"], df_odd_preds.loc[~df_odd_preds["is_daytime"], "pred_stage8_1_candidate_CORRECTED"]))

    delta_mae = mae_e1 - mae_st75
    delta_nmae = nmae_e1 - nmae_st75
    delta_rmse = rmse_e1 - rmse_st75
    delta_bias = bias_e1 - bias_st75

    print("\n" + "=" * 70)
    print("CORRECTED STAGE 7.5 CONTROL — 2024 ODD METRICS (35 features, corrected terrain)")
    print("=" * 70)
    print(f"MAE:       {mae_st75:.6f} W/m²  (historical buggy-terrain reference: 36.613571)")
    print(f"nMAE:      {nmae_st75:.4f}%     (historical buggy-terrain reference: 28.3983%)")
    print(f"RMSE:      {rmse_st75:.6f} W/m²  (historical buggy-terrain reference: 65.347064)")
    print(f"Bias:      {bias_st75:+.6f} W/m² (historical buggy-terrain reference: +1.307778)")
    print(f"Night MAE: {night_mae_st75:.6f} W/m²")

    print("\n" + "=" * 70)
    print("CORRECTED STAGE 8.1 CANDIDATE — 2024 ODD METRICS (37 features, corrected terrain + u700/v700)")
    print("=" * 70)
    print(f"MAE:       {mae_e1:.6f} W/m²")
    print(f"nMAE:      {nmae_e1:.4f}%")
    print(f"RMSE:      {rmse_e1:.6f} W/m²")
    print(f"Bias:      {bias_e1:+.6f} W/m²")
    print(f"Night MAE: {night_mae_e1:.6f} W/m²")

    print("\n" + "=" * 70)
    print("DELTAS (Corrected Candidate - Corrected Control)")
    print("=" * 70)
    print(f"ΔMAE:  {delta_mae:+.6f} W/m²  ΔnMAE: {delta_nmae:+.4f} pp  ΔRMSE: {delta_rmse:+.6f} W/m²  ΔBias: {delta_bias:+.6f} W/m²")

    model_st75_hash = sha256_of(MODEL_ST75_PATH)
    model_e1_hash = sha256_of(MODEL_E1_PATH)
    odd_preds_hash = sha256_of(ODD_PREDS_PATH)

    print(f"\nModel artifact (control, 35-feat)   SHA256: {model_st75_hash}")
    print(f"Model artifact (candidate, 37-feat) SHA256: {model_e1_hash}")
    print(f"ODD predictions CSV                 SHA256: {odd_preds_hash}")
    print(f"Round-trip identical (reloaded vs in-memory): {artifact_roundtrip_identical}")

    results_payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Separate CORRECTED Stage 8.1 model for the 2025 blind test. Trained and "
            "evaluated ONLY on 2024 data (EVEN-train / ODD-eval), exact original "
            "procedure, exact original target/split/hyperparameters/model type -- "
            "only the terrain (4) and u700/v700 (2) features were rebuilt with "
            "corrected causal semantics; the other 31 features are unchanged from "
            "the historical 2024 pipeline's source files."
        ),
        "historical_artifact_untouched": True,
        "retraining_scope": "2024 only; 2025 blind test NOT run by this script",
        "input_feature_matrix": {"path": str(MATRIX_2024_PATH), "sha256": matrix_hash},
        "split": {"total_origins": len(all_origins), "even_train_origins": len(even_origins),
                   "odd_eval_origins": len(odd_origins)},
        "odd_counts": {
            "origins": len(odd_origins), "forecast_hours": int(len(df_odd)),
            "daytime_rows": int(len(odd_day)), "night_rows": int(len(odd_night)),
        },
        "features": {
            "stage75_control_35": stage75_35_features,
            "stage8_1_candidate_37": candidate_37_features,
            "corrected_families": ["terrain (4)", "u700/v700 (2)"],
            "unchanged_count": 31,
            "nan_rows_in_u700_v700_train": int(even_day[["u700", "v700"]].isna().any(axis=1).sum()),
            "nan_rows_in_u700_v700_eval": int(odd_day[["u700", "v700"]].isna().any(axis=1).sum()),
            "nan_handling": "native HistGradientBoostingRegressor missing-value support; "
                             "model now trained WITH the same honest NaN pattern it will see at inference "
                             "(unlike the historical model, which never saw real NaN for u700/v700)",
        },
        "model_definition": {
            "estimator": "sklearn.ensemble.HistGradientBoostingRegressor",
            "loss": "absolute_error", "max_depth": 4, "min_samples_leaf": 30,
            "l2_regularization": 10.0, "random_state": 42, "tuned": False,
        },
        "corrected_stage7_5_control_2024_odd": {
            "daytime_mae_w_m2": round(mae_st75, 6), "daytime_nmae_pct": round(nmae_st75, 4),
            "daytime_rmse_w_m2": round(rmse_st75, 6), "daytime_bias_w_m2": round(bias_st75, 6),
            "night_mae_w_m2": round(night_mae_st75, 6),
        },
        "corrected_stage8_1_candidate_2024_odd": {
            "daytime_mae_w_m2": round(mae_e1, 6), "daytime_nmae_pct": round(nmae_e1, 4),
            "daytime_rmse_w_m2": round(rmse_e1, 6), "daytime_bias_w_m2": round(bias_e1, 6),
            "night_mae_w_m2": round(night_mae_e1, 6),
        },
        "deltas_candidate_minus_control": {
            "delta_mae_w_m2": round(delta_mae, 6), "delta_nmae_pp": round(delta_nmae, 4),
            "delta_rmse_w_m2": round(delta_rmse, 6), "delta_bias_w_m2": round(delta_bias, 6),
        },
        "historical_buggy_terrain_reference_for_context_only": {
            "note": "Historical stage7_5 control used UNCORRECTED terrain; these numbers "
                     "are NOT a valid apples-to-apples baseline, provided for context only.",
            "mae_w_m2": 36.613571, "nmae_pct": 28.3983, "rmse_w_m2": 65.347064, "bias_w_m2": 1.307778,
        },
        "artifacts": {
            "model_control_35feature": {"path": str(MODEL_ST75_PATH), "sha256": model_st75_hash},
            "model_candidate_37feature": {"path": str(MODEL_E1_PATH), "sha256": model_e1_hash},
            "odd_predictions_csv": {"path": str(ODD_PREDS_PATH), "sha256": odd_preds_hash},
        },
        "artifact_roundtrip_identical": artifact_roundtrip_identical,
    }
    atomic_write_json(results_payload, RESULTS_PATH)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_artifact_sha256": model_e1_hash,
        "model_artifact_path": str(MODEL_E1_PATH),
        "control_artifact_sha256": model_st75_hash,
        "control_artifact_path": str(MODEL_ST75_PATH),
        "feature_order_37": candidate_37_features,
        "feature_order_35": stage75_35_features,
        "trained_on": "2024 EVEN origins only (174 origins, daytime rows)",
        "evaluated_on": "2024 ODD origins only (173 origins, daytime rows for MAE/RMSE/bias/nMAE)",
        "ready_for_2025_blind_test": True,
        "2025_blind_test_executed": False,
        "corrected_2025_feature_matrix_path": str(OUT_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"),
        "historical_frozen_artifact_touched": False,
    }
    atomic_write_json(manifest, MANIFEST_PATH)
    print(f"\nResults written to: {RESULTS_PATH}")
    print(f"Manifest written to: {MANIFEST_PATH}")
    print("\nDone! Corrected Stage 8.1 model trained (2024 EVEN) and evaluated (2024 ODD) only.")
    print("2025 blind test NOT executed, per instructions.")


if __name__ == "__main__":
    main()
