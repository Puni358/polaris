"""
POLARIS — Candidate K Baseline Conditioning Training & Validation Runner (Train/Validation Only).

Hypothesis 1: Conditioning on the Stage 4 baseline prediction and clean attenuation
(clearsky_ghi - pred_stage4_clean) alongside the 33 approved successor features to enable
the GBDT to learn non-linear residual interactions with baseline state.

Architecture & Hyperparameters (Frozen, identical to Successor v2):
  HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                                l2_regularization=10.0, random_state=42)

Target:
  residual_target = actual_SW_IN - pred_stage4_clean (fit on daytime rows only, n=2,885)

Features (Exact 35 features):
  33 Successor v2 features + pred_stage4_clean + clean_attenuation

Partitions:
  Train: 2024-EVEN (174 origins, 4,176 rows)
  Validation: 2024-ODD (173 origins, 4,152 rows)

Strict Prohibitions Enforced:
  - NO 2025 / blind data loaded, inspected, or evaluated.
  - NO blind baseline generated.
  - NO hyperparameters tuned against validation.
  - NO frozen Stage 8.1 controls or existing datasets overwritten.
  - Winner status strictly null.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor

# Add repository root for importing research_utils
BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
from forecasting.stage7.stage8.stage8_1_station_tuning_research.research_utils import (
    bootstrap_mae_diff_ci_corrected,
    metrics as compute_metrics,
    apply_night_zero,
    horizon_breakdown,
)

# Paths
SUCCESSOR_V2_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z"
DATASET_V2_DIR = SUCCESSOR_V2_DIR / "dataset_v2"
BASELINE_DIR = SUCCESSOR_V2_DIR / "stage4_clean_baseline"
SUCCESSOR_V2_ARTIFACTS = SUCCESSOR_V2_DIR / "artifacts_v2"

CAND_K_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning"
ARTIFACTS_DIR = CAND_K_DIR / "artifacts"

TRAIN_V2_PATH = DATASET_V2_DIR / "train.csv"
VAL_V2_PATH = DATASET_V2_DIR / "validation.csv"
TRAIN_BASE_PATH = BASELINE_DIR / "train_baseline.csv"
VAL_BASE_PATH = BASELINE_DIR / "validation_baseline.csv"
HISTORICAL_ODD_PREDS_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_official_odd_predictions_2024.csv"
SUCCESSOR_V2_VAL_PREDS_PATH = SUCCESSOR_V2_ARTIFACTS / "validation_predictions.csv"

# Pre-asserted SHA-256 hashes
EXPECTED_HASHES = {
    "train_v2": "7f2435fe5b2b239c9a2950366d56ab4297f29f1e8813d23a9ab64f62ca50483d",
    "val_v2": "24e6828ee7cb7d45fd755844653e4ad9396f07bfe1a551b4411867bb07c948a9",
    "train_base": "1b6ff36e50e0c415f3f1160a80aaa18fe2f6576245d28bbaaaed7cba1f9a1f57",
    "val_base": "087b5ca7d7ac70cf21918021854bfa01c59b6ee8e8eccb03253ad32b9c472664",
}

SUCCESSOR_33_FEATURES = [
    "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
    "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700",
    "lwp_18z_fc", "iwp_18z_fc", "lwp_x_cloud_18z", "elevation_x_cloud_frac"
]

CANDIDATE_K_35_FEATURES = SUCCESSOR_33_FEATURES + [
    "pred_stage4_clean",
    "clean_attenuation"
]

FROZEN_HP = dict(
    loss="absolute_error",
    max_depth=4,
    min_samples_leaf=30,
    l2_regularization=10.0,
    random_state=42
)


class TrainingError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_csv(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def atomic_write_json(obj: dict, path: Path) -> None:
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fp:
        json.dump(obj, fp, indent=2)
    tmp.replace(path)


def verify_inputs():
    log("Verifying pre-execution input hashes...")
    actual = {
        "train_v2": sha256_file(TRAIN_V2_PATH),
        "val_v2": sha256_file(VAL_V2_PATH),
        "train_base": sha256_file(TRAIN_BASE_PATH),
        "val_base": sha256_file(VAL_BASE_PATH),
    }
    for k, exp in EXPECTED_HASHES.items():
        if actual[k] != exp:
            raise TrainingError(f"Input hash mismatch for {k}: {actual[k]} != {exp}")
    log("All input hashes MATCH pre-asserted values.")


def run():
    print("=" * 80)
    print("POLARIS — CANDIDATE K BASELINE CONDITIONING (TRAIN / VALIDATION ONLY)")
    print("Hypothesis: Baseline Conditioning (35 features = 33 Successor v2 + pred_stage4_clean + clean_attenuation)")
    print("Architecture: HistGradientBoostingRegressor (Frozen hyperparameters)")
    print("Target: actual_SW_IN - pred_stage4_clean (Residual on Clean Stage 4)")
    print("=" * 80)

    # 1. Output directory isolation
    if ARTIFACTS_DIR.exists():
        files = list(ARTIFACTS_DIR.glob("*"))
        if files:
            raise TrainingError(f"Target directory {ARTIFACTS_DIR} exists and is non-empty; refusing to overwrite.")
    else:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Input verification
    verify_inputs()

    # 3. Load & Join Train Partition
    log("Loading and joining Train partition (2024-EVEN)...")
    df_tr_v2 = pd.read_csv(TRAIN_V2_PATH)
    df_tr_base = pd.read_csv(TRAIN_BASE_PATH)

    assert len(df_tr_v2) == 4176, f"Expected 4176 train_v2 rows, got {len(df_tr_v2)}"
    assert len(df_tr_base) == 4176, f"Expected 4176 train_base rows, got {len(df_tr_base)}"

    df_tr_v2["_fs_key"] = pd.to_datetime(df_tr_v2["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    df_tr_base["_fs_key"] = pd.to_datetime(df_tr_base["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    join_cols_base = ["_fs_key", "horizon_hour", "pred_stage3b_cloud_nwp", "phys_pred_clean", "pred_stage4_clean", "residual_target"]
    df_train = df_tr_v2.merge(df_tr_base[join_cols_base], on=["_fs_key", "horizon_hour"], how="inner")
    if len(df_train) != 4176:
        raise TrainingError(f"Train join produced {len(df_train)} rows instead of 4176.")
    if df_train.duplicated(subset=["_fs_key", "horizon_hour"]).sum() > 0:
        raise TrainingError("Train join contains duplicate keys.")
    df_train.drop(columns=["_fs_key"], inplace=True)

    # Construct clean_attenuation = clearsky_ghi - pred_stage4_clean
    df_train["clean_attenuation"] = df_train["clearsky_ghi"] - df_train["pred_stage4_clean"]

    # 4. Load & Join Validation Partition
    log("Loading and joining Validation partition (2024-ODD)...")
    df_val_v2 = pd.read_csv(VAL_V2_PATH)
    df_val_base = pd.read_csv(VAL_BASE_PATH)

    assert len(df_val_v2) == 4152, f"Expected 4152 val_v2 rows, got {len(df_val_v2)}"
    assert len(df_val_base) == 4152, f"Expected 4152 val_base rows, got {len(df_val_base)}"

    df_val_v2["_fs_key"] = pd.to_datetime(df_val_v2["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    df_val_base["_fs_key"] = pd.to_datetime(df_val_base["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    df_val = df_val_v2.merge(df_val_base[join_cols_base], on=["_fs_key", "horizon_hour"], how="inner")
    if len(df_val) != 4152:
        raise TrainingError(f"Val join produced {len(df_val)} rows instead of 4152.")
    if df_val.duplicated(subset=["_fs_key", "horizon_hour"]).sum() > 0:
        raise TrainingError("Validation join contains duplicate keys.")
    df_val.drop(columns=["_fs_key"], inplace=True)

    df_val["clean_attenuation"] = df_val["clearsky_ghi"] - df_val["pred_stage4_clean"]

    # Partition exclusivity assertion
    tr_origins = set(df_train["forecast_start"].unique())
    val_origins = set(df_val["forecast_start"].unique())
    assert len(tr_origins) == 174, f"Expected 174 train origins, got {len(tr_origins)}"
    assert len(val_origins) == 173, f"Expected 173 val origins, got {len(val_origins)}"
    if tr_origins & val_origins:
        raise TrainingError("Train and Validation origins overlap!")
    log(f"Partition counts: Train {len(tr_origins)} origins / {len(df_train)} rows | Validation {len(val_origins)} origins / {len(df_val)} rows (zero overlap).")

    # Feature assertion: exact 35 columns, exact order, labels strictly excluded
    for feat in CANDIDATE_K_35_FEATURES:
        if feat not in df_train.columns:
            raise TrainingError(f"Feature {feat} missing from train dataset.")
        if feat not in df_val.columns:
            raise TrainingError(f"Feature {feat} missing from validation dataset.")
    for forbidden in ["actual_SW_IN", "residual_target", "forecast_start", "timestamp", "split"]:
        if forbidden in CANDIDATE_K_35_FEATURES:
            raise TrainingError(f"Forbidden column {forbidden} leaked into feature list.")

    # 5. Training-only Daytime Filtering
    train_day = df_train[df_train["is_daytime"]].copy()
    val_day = df_val[df_val["is_daytime"]].copy()
    log(f"Daytime rows: Train {len(train_day)} / {len(df_train)} | Validation {len(val_day)} / {len(df_val)}")

    X_tr = train_day[CANDIDATE_K_35_FEATURES].values
    y_tr_actual = train_day["actual_SW_IN"].values
    st4_tr = train_day["pred_stage4_clean"].values
    res_tr = train_day["residual_target"].values

    # Assert target equality
    assert np.allclose(res_tr, y_tr_actual - st4_tr, atol=1e-12), "residual_target mismatch vs actual - st4"

    # NaN audit on X_tr: only u700 and v700 permitted to have NaNs (horizons 20-24)
    u_idx = CANDIDATE_K_35_FEATURES.index("u700")
    v_idx = CANDIDATE_K_35_FEATURES.index("v700")
    other_indices = [i for i in range(len(CANDIDATE_K_35_FEATURES)) if i not in (u_idx, v_idx)]
    assert not np.isnan(X_tr[:, other_indices]).any(), "Unexpected NaNs in non-wind features!"
    log(f"u700/v700 NaNs in train daytime: {np.isnan(X_tr[:, [u_idx, v_idx]]).sum()} cells (native handling, un-imputed).")
    log(f"All other 33 features in train daytime: ZERO NaNs.")

    # 6. Fit Model
    log("Fitting HistGradientBoostingRegressor on Train (2024-EVEN daytime rows only, 35 features)...")
    train_start_utc = datetime.now(timezone.utc).isoformat()
    model = HistGradientBoostingRegressor(**FROZEN_HP)
    model.fit(X_tr, res_tr)
    train_end_utc = datetime.now(timezone.utc).isoformat()
    log("Model training complete.")

    # 7. Model Serialization & Reload Integrity Check
    model_path = ARTIFACTS_DIR / "candidate_k_model.joblib"
    joblib.dump(model, model_path)
    model_sha256 = sha256_file(model_path)
    log(f"Model saved to {model_path.name} (SHA-256: {model_sha256}).")

    reloaded_model = joblib.load(model_path)
    X_val_all = df_val[CANDIDATE_K_35_FEATURES].values
    pred_res_mem = model.predict(X_val_all)
    pred_res_reloaded = reloaded_model.predict(X_val_all)
    if not np.array_equal(pred_res_mem, pred_res_reloaded):
        raise TrainingError("Reloaded model prediction mismatch against in-memory model!")
    log("Model reload integrity check: PASS (in-memory and reloaded predictions identical).")

    # 8. Inference & Reconstruction on Validation
    st4_val_all = df_val["pred_stage4_clean"].values
    night_val_all = df_val["is_night_causal"].values
    pred_raw_all = np.maximum(0.0, st4_val_all + pred_res_mem)
    pred_cand_k_all = apply_night_zero(pred_raw_all, night_val_all)

    # Attach predictions to validation dataframe
    df_val["pred_candidate_k"] = pred_cand_k_all
    df_val["pred_stage4_clean_control"] = apply_night_zero(np.maximum(0.0, st4_val_all), night_val_all)

    # Load Successor v2 predictions
    df_succ_v2 = pd.read_csv(SUCCESSOR_V2_VAL_PREDS_PATH)
    df_val["_fs_key"] = pd.to_datetime(df_val["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    df_succ_v2["_fs_key"] = pd.to_datetime(df_succ_v2["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    merged_succ = df_val.merge(
        df_succ_v2[["_fs_key", "horizon_hour", "pred_successor_v2"]],
        on=["_fs_key", "horizon_hour"],
        how="inner"
    )
    assert len(merged_succ) == 4152, f"Successor v2 merge count mismatch: {len(merged_succ)}"
    df_val["pred_successor_v2"] = merged_succ["pred_successor_v2"]

    # Load Historical Stage 8.1 control predictions
    df_hist_odd = pd.read_csv(HISTORICAL_ODD_PREDS_PATH)
    df_hist_odd["_fs_key"] = pd.to_datetime(df_hist_odd["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    merged_odd = df_val.merge(
        df_hist_odd[["_fs_key", "horizon_hour", "pred_stage8_1_candidate_CORRECTED"]],
        on=["_fs_key", "horizon_hour"],
        how="inner"
    )
    assert len(merged_odd) == 4152, f"Historical merge count mismatch: {len(merged_odd)}"
    df_val["pred_historical_stage8_1_control"] = merged_odd["pred_stage8_1_candidate_CORRECTED"]
    df_val.drop(columns=["_fs_key"], inplace=True)

    # 9. Metrics Computation on Daytime Validation Rows (n=2,883)
    val_day_mask = df_val["is_daytime"].values
    y_val_day = df_val.loc[val_day_mask, "actual_SW_IN"].values
    pred_cand_k_day = df_val.loc[val_day_mask, "pred_candidate_k"].values
    pred_succ_day = df_val.loc[val_day_mask, "pred_successor_v2"].values
    pred_st4_day = df_val.loc[val_day_mask, "pred_stage4_clean_control"].values
    pred_hist81_day = df_val.loc[val_day_mask, "pred_historical_stage8_1_control"].values
    origins_val_day = df_val.loc[val_day_mask, "forecast_start"]
    horizons_val_day = df_val.loc[val_day_mask, "horizon_hour"].values

    metrics_cand_k = compute_metrics(y_val_day, pred_cand_k_day)
    metrics_successor = compute_metrics(y_val_day, pred_succ_day)
    metrics_st4_control = compute_metrics(y_val_day, pred_st4_day)
    metrics_hist81_control = compute_metrics(y_val_day, pred_hist81_day)

    # Paired origin-level bootstrap CIs (2,000 resamples, seed 42)
    log("Computing paired origin-level bootstrap CIs (2,000 resamples, seed 42)...")
    boot_vs_st4 = bootstrap_mae_diff_ci_corrected(
        origins_val_day, y_val_day, pred_cand_k_day, pred_st4_day, n_boot=2000, seed=42
    )
    boot_vs_succ = bootstrap_mae_diff_ci_corrected(
        origins_val_day, y_val_day, pred_cand_k_day, pred_succ_day, n_boot=2000, seed=42
    )
    boot_vs_hist81 = bootstrap_mae_diff_ci_corrected(
        origins_val_day, y_val_day, pred_cand_k_day, pred_hist81_day, n_boot=2000, seed=42
    )

    # High-elevation subset performance (solar_elevation >= 30 deg on daytime rows, n=487)
    elev_val_day = df_val.loc[val_day_mask, "solar_elevation"].values
    high_elev_mask = elev_val_day >= 30.0
    n_high = int(high_elev_mask.sum())
    log(f"High-elevation subset: {n_high} rows (solar_elevation >= 30 deg).")

    high_metrics_cand_k = compute_metrics(y_val_day[high_elev_mask], pred_cand_k_day[high_elev_mask])
    high_metrics_succ = compute_metrics(y_val_day[high_elev_mask], pred_succ_day[high_elev_mask])
    high_metrics_st4 = compute_metrics(y_val_day[high_elev_mask], pred_st4_day[high_elev_mask])
    high_metrics_hist81 = compute_metrics(y_val_day[high_elev_mask], pred_hist81_day[high_elev_mask])

    boot_high_vs_succ = bootstrap_mae_diff_ci_corrected(
        origins_val_day.values[high_elev_mask],
        y_val_day[high_elev_mask],
        pred_cand_k_day[high_elev_mask],
        pred_succ_day[high_elev_mask],
        n_boot=2000,
        seed=42
    )
    boot_high_vs_hist81 = bootstrap_mae_diff_ci_corrected(
        origins_val_day.values[high_elev_mask],
        y_val_day[high_elev_mask],
        pred_cand_k_day[high_elev_mask],
        pred_hist81_day[high_elev_mask],
        n_boot=2000,
        seed=42
    )

    # Per-horizon breakdown
    h_breakdown_vs_st4 = horizon_breakdown(horizons_val_day, y_val_day, pred_st4_day, pred_cand_k_day)
    h_breakdown_vs_succ = horizon_breakdown(horizons_val_day, y_val_day, pred_succ_day, pred_cand_k_day)
    h_breakdown_vs_hist81 = horizon_breakdown(horizons_val_day, y_val_day, pred_hist81_day, pred_cand_k_day)

    # Gate assessment
    delta_mae_vs_st4 = metrics_cand_k["mae"] - metrics_st4_control["mae"]
    delta_mae_vs_succ = metrics_cand_k["mae"] - metrics_successor["mae"]
    delta_mae_vs_hist81 = metrics_cand_k["mae"] - metrics_hist81_control["mae"]

    gate1_passed = bool(delta_mae_vs_st4 <= -4.6553)
    gate2_passed = bool(metrics_cand_k["mae"] < 38.7742 and boot_vs_succ["ci95_hi"] < 0.0)
    gate3_passed = bool(metrics_cand_k["mae"] < 37.5000)
    superiority_over_stage81 = bool(metrics_cand_k["mae"] < 36.2040 and boot_vs_hist81["ci95_hi"] < 0.0)

    validation_summary = {
        "candidate_k_baseline_conditioning": metrics_cand_k,
        "candidate_successor_v2": metrics_successor,
        "clean_stage4_baseline_control": metrics_st4_control,
        "historical_stage8_1_control": metrics_hist81_control,
        "delta_vs_clean_stage4": {
            "delta_mae": round(delta_mae_vs_st4, 4),
            "delta_rmse": round(metrics_cand_k["rmse"] - metrics_st4_control["rmse"], 4),
            "delta_bias": round(metrics_cand_k["bias"] - metrics_st4_control["bias"], 4),
            "bootstrap_mae_diff": boot_vs_st4,
        },
        "delta_vs_successor_v2": {
            "delta_mae": round(delta_mae_vs_succ, 4),
            "delta_rmse": round(metrics_cand_k["rmse"] - metrics_successor["rmse"], 4),
            "delta_bias": round(metrics_cand_k["bias"] - metrics_successor["bias"], 4),
            "bootstrap_mae_diff": boot_vs_succ,
        },
        "delta_vs_historical_stage8_1": {
            "delta_mae": round(delta_mae_vs_hist81, 4),
            "delta_rmse": round(metrics_cand_k["rmse"] - metrics_hist81_control["rmse"], 4),
            "delta_bias": round(metrics_cand_k["bias"] - metrics_hist81_control["bias"], 4),
            "bootstrap_mae_diff": boot_vs_hist81,
        },
        "high_elevation_subset": {
            "n_rows": n_high,
            "candidate_k": high_metrics_cand_k,
            "candidate_successor_v2": high_metrics_succ,
            "clean_stage4_control": high_metrics_st4,
            "historical_stage8_1_control": high_metrics_hist81,
            "bootstrap_mae_diff_vs_succ": boot_high_vs_succ,
            "bootstrap_mae_diff_vs_hist81": boot_high_vs_hist81,
        },
        "gates": {
            "gate1_beat_clean_stage4": {
                "rule": "delta_mae_vs_clean_stage4 <= -4.6553 W/m² (reconciled exact saved improvement)",
                "actual_delta_mae": round(delta_mae_vs_st4, 4),
                "passed": gate1_passed,
            },
            "gate2_beat_successor_v2": {
                "rule": "daytime_mae < 38.7742 W/m² AND paired origin-level bootstrap ci95_hi vs successor_v2 < 0.0 W/m²",
                "actual_mae": metrics_cand_k["mae"],
                "bootstrap_ci95": [boot_vs_succ["ci95_lo"], boot_vs_succ["ci95_hi"]],
                "passed": gate2_passed,
            },
            "gate3_narrow_stage8_1_gap": {
                "rule": "daytime_mae < 37.5000 W/m²",
                "actual_mae": metrics_cand_k["mae"],
                "passed": gate3_passed,
            },
            "superiority_over_stage8_1_claimable": {
                "rule": "daytime_mae < 36.2040 W/m² AND bootstrap ci95_hi vs stage8_1 < 0.0 W/m²",
                "actual_mae": metrics_cand_k["mae"],
                "bootstrap_ci95": [boot_vs_hist81["ci95_lo"], boot_vs_hist81["ci95_hi"]],
                "claimable": superiority_over_stage81,
            }
        },
        "horizon_breakdown": {
            "vs_clean_stage4": h_breakdown_vs_st4,
            "vs_successor_v2": h_breakdown_vs_succ,
            "vs_historical_stage8_1": h_breakdown_vs_hist81,
        }
    }

    # 10. Save Validation Predictions and Results Atomically
    preds_out_path = ARTIFACTS_DIR / "validation_predictions.csv"
    val_out_cols = [
        "forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "is_daytime", "is_night_causal",
        "solar_elevation", "cloud_frac", "pred_stage4_clean", "clean_attenuation",
        "pred_candidate_k", "pred_successor_v2", "pred_stage4_clean_control", "pred_historical_stage8_1_control"
    ]
    atomic_write_csv(df_val[val_out_cols], preds_out_path)
    log(f"Saved validation predictions to {preds_out_path.name}.")

    results_out_path = ARTIFACTS_DIR / "VALIDATION_RESULTS.json"
    atomic_write_json(validation_summary, results_out_path)
    log(f"Saved validation results to {results_out_path.name}.")

    # 11. Model Manifest & HASHES.sha256
    manifest = {
        "artifact_name": "candidate_k_model.joblib",
        "model_sha256": model_sha256,
        "training_timestamp_utc": {
            "start": train_start_utc,
            "end": train_end_utc,
        },
        "environment": {
            "python_version": sys.version,
            "scikit_learn_version": sklearn.__version__,
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "joblib_version": joblib.__version__,
        },
        "hypothesis": "Hypothesis 1: Baseline Conditioning (pred_stage4_clean + clean_attenuation)",
        "hyperparameters": FROZEN_HP,
        "features": {
            "count": len(CANDIDATE_K_35_FEATURES),
            "order": CANDIDATE_K_35_FEATURES,
        },
        "input_hashes": EXPECTED_HASHES,
        "training_provenance": {
            "dataset": "dataset_v2/train.csv joined with stage4_clean_baseline/train_baseline.csv",
            "origins": len(tr_origins),
            "total_rows": len(df_train),
            "daytime_fitted_rows": len(train_day),
            "target": "actual_SW_IN - pred_stage4_clean (residual on clean Stage 4)",
        },
        "validation_provenance": {
            "dataset": "dataset_v2/validation.csv joined with stage4_clean_baseline/validation_baseline.csv",
            "origins": len(val_origins),
            "total_rows": len(df_val),
            "daytime_evaluated_rows": len(val_day),
        },
        "governance": {
            "blind_partition_used": False,
            "refit_on_validation": False,
            "winner_status": "null",
            "operational_promotion": False,
        }
    }
    manifest_out_path = ARTIFACTS_DIR / "CANDIDATE_K_MANIFEST.json"
    atomic_write_json(manifest, manifest_out_path)
    log("Saved CANDIDATE_K_MANIFEST.json.")

    out_hashes = {
        "candidate_k_model.joblib": model_sha256,
        "validation_predictions.csv": sha256_file(preds_out_path),
        "VALIDATION_RESULTS.json": sha256_file(results_out_path),
        "CANDIDATE_K_MANIFEST.json": sha256_file(manifest_out_path),
    }
    hashes_file = ARTIFACTS_DIR / "HASHES.sha256"
    hashes_file.write_text(
        "\n".join(f"{h}  {f}" for f, h in out_hashes.items()) + "\n", encoding="utf-8"
    )
    log("Saved HASHES.sha256.")

    print("\n" + "=" * 80)
    print("VALIDATION RESULTS SUMMARY (2024-ODD Daytime, n=2,883)")
    print("=" * 80)
    print(f"Candidate K (Conditioning): MAE = {metrics_cand_k['mae']:.4f} W/m² | RMSE = {metrics_cand_k['rmse']:.4f} W/m² | Bias = {metrics_cand_k['bias']:+.4f} W/m²")
    print(f"Candidate F Successor v2:   MAE = {metrics_successor['mae']:.4f} W/m² | RMSE = {metrics_successor['rmse']:.4f} W/m² | Bias = {metrics_successor['bias']:+.4f} W/m²")
    print(f"Clean Stage 4 Control:      MAE = {metrics_st4_control['mae']:.4f} W/m² | RMSE = {metrics_st4_control['rmse']:.4f} W/m² | Bias = {metrics_st4_control['bias']:+.4f} W/m²")
    print(f"Historical Stage 8.1 Ctrl:  MAE = {metrics_hist81_control['mae']:.4f} W/m² | RMSE = {metrics_hist81_control['rmse']:.4f} W/m² | Bias = {metrics_hist81_control['bias']:+.4f} W/m²")
    print("-" * 80)
    print(f"Delta vs Clean Stage 4:     {delta_mae_vs_st4:+.4f} W/m² (95% CI: [{boot_vs_st4['ci95_lo']}, {boot_vs_st4['ci95_hi']}])")
    print(f"Delta vs Successor v2:      {delta_mae_vs_succ:+.4f} W/m² (95% CI: [{boot_vs_succ['ci95_lo']}, {boot_vs_succ['ci95_hi']}])")
    print(f"Delta vs Historical St8.1:  {delta_mae_vs_hist81:+.4f} W/m² (95% CI: [{boot_vs_hist81['ci95_lo']}, {boot_vs_hist81['ci95_hi']}])")
    print("-" * 80)
    print("GATE EVALUATION:")
    print(f"  Gate 1 (Beat Clean Stage 4 baseline <= -4.6553): {'PASS' if gate1_passed else 'FAIL'} (delta = {delta_mae_vs_st4:+.4f} W/m²)")
    print(f"  Gate 2 (Beat Successor v2 < 38.7742 & CI hi < 0): {'PASS' if gate2_passed else 'FAIL'} (MAE = {metrics_cand_k['mae']:.4f}, CI = [{boot_vs_succ['ci95_lo']}, {boot_vs_succ['ci95_hi']}])")
    print(f"  Gate 3 (Narrow gap to St8.1 < 37.5000 W/m²):      {'PASS' if gate3_passed else 'FAIL'} (MAE = {metrics_cand_k['mae']:.4f})")
    print(f"  Superiority over Stage 8.1 claimable:             {'YES' if superiority_over_stage81 else 'NO'} (delta = {delta_mae_vs_hist81:+.4f}, CI = [{boot_vs_hist81['ci95_lo']}, {boot_vs_hist81['ci95_hi']}])")
    print("-" * 80)
    print("High-Elevation Regime (solar_elevation >= 30 deg, n=487):")
    print(f"  Candidate K:              MAE = {high_metrics_cand_k['mae']:.4f} W/m² | Bias = {high_metrics_cand_k['bias']:+.4f} W/m²")
    print(f"  Successor v2:             MAE = {high_metrics_succ['mae']:.4f} W/m² | Bias = {high_metrics_succ['bias']:+.4f} W/m²")
    print(f"  Clean Stage 4:            MAE = {high_metrics_st4['mae']:.4f} W/m² | Bias = {high_metrics_st4['bias']:+.4f} W/m²")
    print(f"  Historical Stage 8.1:     MAE = {high_metrics_hist81['mae']:.4f} W/m² | Bias = {high_metrics_hist81['bias']:+.4f} W/m²")
    print(f"  Delta vs Successor v2:    {high_metrics_cand_k['mae'] - high_metrics_succ['mae']:+.4f} W/m² (95% CI: [{boot_high_vs_succ['ci95_lo']}, {boot_high_vs_succ['ci95_hi']}])")
    print(f"  Delta vs Hist St8.1:      {high_metrics_cand_k['mae'] - high_metrics_hist81['mae']:+.4f} W/m² (95% CI: [{boot_high_vs_hist81['ci95_lo']}, {boot_high_vs_hist81['ci95_hi']}])")
    print("=" * 80)
    print("CANDIDATE K EXECUTION COMPLETE.")
    return validation_summary


if __name__ == "__main__":
    try:
        run()
    except TrainingError as e:
        print(f"TRAINING_FAILED: {e}")
        sys.exit(2)
