#!/usr/bin/env python3
"""
Exports Candidate N (N1 & N6) models and validation artifacts strictly on 2024-ODD.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

SCRIPT_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Import definitions from run_candidate_n_experiment
sys.path.insert(0, str(SCRIPT_DIR))
from run_candidate_n_experiment import (
    CANDIDATE_K_35_FEATURES,
    CANDIDATE_N1_36_FEATURES,
    CANDIDATE_N2_40_FEATURES,
    engineer_candidate_n_features,
    fit_predict_bagged_gbdt,
    fit_predict_high_elev_kt_specialist,
    fit_predict_single_gbdt,
    load_2024_clean_matrix,
)

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_metrics(y_pred: np.ndarray, y_true: np.ndarray, mask: np.ndarray) -> Dict[str, float]:
    err = (y_pred - y_true)[mask]
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    bias = float(np.mean(err))
    mean_obs = float(np.mean(y_true[mask]))
    nmae = float((mae / mean_obs) * 100.0) if mean_obs > 0 else 0.0
    return {"mae": mae, "rmse": rmse, "bias": bias, "nmae_pct": nmae}

def run_bootstrap_diff(
    df_odd: pd.DataFrame,
    y_cand: np.ndarray,
    y_ref: np.ndarray,
    day_mask: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42,
) -> Dict[str, float]:
    n_orig = df_odd["origin_dt"].nunique()
    y_t = df_odd["actual_SW_IN"].values
    y_t_3d = y_t.reshape(n_orig, 24)
    y_c_3d = y_cand.reshape(n_orig, 24)
    y_r_3d = y_ref.reshape(n_orig, 24)
    d_3d = day_mask.reshape(n_orig, 24)

    cand_abs = np.sum(np.abs(y_c_3d - y_t_3d) * d_3d, axis=1)
    ref_abs = np.sum(np.abs(y_r_3d - y_t_3d) * d_3d, axis=1)
    day_counts = np.sum(d_3d, axis=1)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n_orig, size=n_orig)
        diffs[b] = (np.sum(cand_abs[idx]) - np.sum(ref_abs[idx])) / np.sum(day_counts[idx])

    delta = float(np.mean(np.abs((y_cand - y_t)[day_mask])) - np.mean(np.abs((y_ref - y_t)[day_mask])))
    return {
        "delta_mae": delta,
        "mean_diff": float(np.mean(diffs)),
        "ci95_lo": float(np.percentile(diffs, 2.5)),
        "ci95_hi": float(np.percentile(diffs, 97.5)),
        "n_boot": n_boot,
        "method": "origin_level_cluster_bootstrap",
        "passes_gate": bool(np.percentile(diffs, 97.5) < 0.0),
    }

def main():
    print("[EXPORT] Loading and preparing 2024 dataset...")
    df_raw, p = load_2024_clean_matrix()
    df = engineer_candidate_n_features(df_raw)
    df_even = df[df["is_even_origin"]].reset_index(drop=True)
    df_odd = df[~df["is_even_origin"]].reset_index(drop=True)

    tr_day = df_even[df_even["is_daytime"]].copy()
    y_res_tr = tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values

    # 1. Fit & Serialize Candidate N1 (Single Tree 36-feature)
    print("[EXPORT] Fitting Candidate N1 model...")
    t0_n1 = datetime.now(timezone.utc).isoformat()
    m_n1 = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_depth=4,
        min_samples_leaf=30,
        l2_regularization=10.0,
        max_features=1.0,
        random_state=42,
    )
    m_n1.fit(tr_day[CANDIDATE_N1_36_FEATURES], y_res_tr)
    t1_n1 = datetime.now(timezone.utc).isoformat()

    n1_model_path = ARTIFACTS_DIR / "candidate_n1_model.joblib"
    joblib.dump(m_n1, n1_model_path, compress=3)

    r_hat_n1 = m_n1.predict(df_odd[CANDIDATE_N1_36_FEATURES])
    pred_n1 = np.clip(df_odd["pred_stage4_clean"].values + r_hat_n1, 0.0, None)
    pred_n1 = np.where(df_odd["causal_day_mask"].values, pred_n1, 0.0)

    # 2. Fit & Serialize Candidate N6 (Bagged 25 additive + 15 kt specialist)
    print("[EXPORT] Fitting Candidate N6 ensemble (25 additive + 15 kt specialist)...")
    t0_n6 = datetime.now(timezone.utc).isoformat()
    n_seeds_add = 25
    additive_models = []
    preds_add = np.zeros((n_seeds_add, len(df_odd)), dtype=np.float64)

    for i in range(n_seeds_add):
        m_i = HistGradientBoostingRegressor(
            loss="absolute_error",
            max_depth=4,
            min_samples_leaf=25,
            l2_regularization=15.0,
            max_features=0.78,
            random_state=100 + i,
        )
        m_i.fit(tr_day[CANDIDATE_N1_36_FEATURES], y_res_tr)
        additive_models.append(m_i)
        r_i = m_i.predict(df_odd[CANDIDATE_N1_36_FEATURES])
        y_i = np.clip(df_odd["pred_stage4_clean"].values + r_i, 0.0, None)
        preds_add[i] = np.where(df_odd["causal_day_mask"].values, y_i, 0.0)

    pred_n6a = np.mean(preds_add, axis=0)

    # Fit 15 kt specialist models
    eps_kt = 15.0
    denom_tr = tr_day["clearsky_ghi_terrain_adjusted"].values + eps_kt
    y_rkt_tr = (tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values) / denom_tr
    n_seeds_kt = 15
    kt_models = []
    preds_kt = np.zeros((n_seeds_kt, len(df_odd)), dtype=np.float64)
    denom_odd = df_odd["clearsky_ghi_terrain_adjusted"].values + eps_kt

    for i in range(n_seeds_kt):
        m_kt = HistGradientBoostingRegressor(
            loss="absolute_error",
            max_depth=4,
            min_samples_leaf=30,
            l2_regularization=15.0,
            max_features=0.80,
            random_state=500 + i,
        )
        m_kt.fit(tr_day[CANDIDATE_N1_36_FEATURES], y_rkt_tr, sample_weight=denom_tr)
        kt_models.append(m_kt)
        rkt_hat = m_kt.predict(df_odd[CANDIDATE_N1_36_FEATURES])
        y_kt_i = df_odd["pred_stage4_clean"].values + rkt_hat * denom_odd
        ceiling = np.maximum(df_odd["clearsky_ghi"].values * 1.25, df_odd["pred_stage4_clean"].values)
        preds_kt[i] = np.clip(y_kt_i, 0.0, ceiling)

    t1_n6 = datetime.now(timezone.utc).isoformat()
    y_kt_bagged = np.mean(preds_kt, axis=0)

    elev = df_odd["solar_elevation"].values
    max_ramp_weight = 0.55
    alpha_he = max_ramp_weight * np.clip((elev - 22.0) / 10.0, 0.0, 1.0)
    unshaded = (df_odd["terrain_solar_obstruction_flag"].values == 0).astype(np.float64)
    w = alpha_he * unshaded
    pred_n6 = np.where(df_odd["causal_day_mask"].values, (1.0 - w) * pred_n6a + w * y_kt_bagged, 0.0)

    n6_bundle = {
        "model_name": "candidate_n6_bagged_additive_kt_ramp",
        "additive_models": additive_models,
        "kt_models": kt_models,
        "features": CANDIDATE_N1_36_FEATURES,
        "max_ramp_weight": max_ramp_weight,
        "ramp_start_deg": 22.0,
        "ramp_full_deg": 32.0,
        "eps_kt": eps_kt,
    }
    n6_model_path = ARTIFACTS_DIR / "candidate_n6_model.joblib"
    joblib.dump(n6_bundle, n6_model_path, compress=3)

    # 3. Fit Candidate K Control
    pred_k = fit_predict_single_gbdt(df_even, df_odd, CANDIDATE_K_35_FEATURES, seed=42)

    # 4. Generate validation_predictions.csv (4152 rows)
    print("[EXPORT] Writing validation_predictions.csv...")
    df_preds = pd.DataFrame({
        "forecast_start": df_odd["forecast_start"].dt.strftime("%Y-%m-%dT%H:%M:%S%z") if hasattr(df_odd["forecast_start"], "dt") else df_odd["forecast_start"],
        "horizon_hour": df_odd["horizon_hour"].astype(int),
        "timestamp": df_odd["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S%z") if hasattr(df_odd["timestamp"], "dt") else df_odd["timestamp"],
        "actual_SW_IN": df_odd["actual_SW_IN"].astype(float),
        "is_daytime": df_odd["is_daytime"].astype(bool),
        "is_night_causal": (~df_odd["causal_day_mask"]).astype(bool),
        "solar_elevation": df_odd["solar_elevation"].astype(float),
        "cloud_frac": df_odd["cloud_frac"].astype(float),
        "pred_stage4_clean": df_odd["pred_stage4_clean"].astype(float),
        "clean_attenuation": df_odd["clean_attenuation"].astype(float),
        "elevation_x_transition_cloud": df_odd["elevation_x_transition_cloud"].astype(float),
        "pred_candidate_k": pred_k,
        "pred_candidate_n1": pred_n1,
        "pred_candidate_n6": pred_n6,
    })
    preds_csv_path = ARTIFACTS_DIR / "validation_predictions.csv"
    df_preds.to_csv(preds_csv_path, index=False)

    # 5. Compute Full Evaluation Metrics & Bootstrap CIs
    print("[EXPORT] Computing comprehensive validation results...")
    day_mask = df_odd["is_daytime"].values
    he_mask = day_mask & (df_odd["solar_elevation"].values >= 30.0)
    le_mask = day_mask & (df_odd["solar_elevation"].values < 30.0)
    y_true = df_odd["actual_SW_IN"].values

    res = {
        "candidate_n6_pure_synthesis": {
            "overall_daytime": compute_metrics(pred_n6, y_true, day_mask),
            "high_elevation": compute_metrics(pred_n6, y_true, he_mask),
            "low_elevation": compute_metrics(pred_n6, y_true, le_mask),
        },
        "candidate_n1_single_tree": {
            "overall_daytime": compute_metrics(pred_n1, y_true, day_mask),
            "high_elevation": compute_metrics(pred_n1, y_true, he_mask),
            "low_elevation": compute_metrics(pred_n1, y_true, le_mask),
        },
        "candidate_k_control": {
            "overall_daytime": compute_metrics(pred_k, y_true, day_mask),
            "high_elevation": compute_metrics(pred_k, y_true, he_mask),
            "low_elevation": compute_metrics(pred_k, y_true, le_mask),
        },
        "clean_stage4_control": {
            "overall_daytime": compute_metrics(df_odd["pred_stage4_clean"].values, y_true, day_mask),
            "high_elevation": compute_metrics(df_odd["pred_stage4_clean"].values, y_true, he_mask),
            "low_elevation": compute_metrics(df_odd["pred_stage4_clean"].values, y_true, le_mask),
        },
        "bootstrap_comparisons": {
            "cand_n6_vs_cand_k": run_bootstrap_diff(df_odd, pred_n6, pred_k, day_mask),
            "cand_n1_vs_cand_k": run_bootstrap_diff(df_odd, pred_n1, pred_k, day_mask),
            "cand_n6_vs_clean_stage4": run_bootstrap_diff(df_odd, pred_n6, df_odd["pred_stage4_clean"].values, day_mask),
            "cand_n6_vs_cand_n1": run_bootstrap_diff(df_odd, pred_n6, pred_n1, day_mask),
        }
    }

    results_json_path = ARTIFACTS_DIR / "VALIDATION_RESULTS.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    # 6. Build CANDIDATE_N_MANIFEST.json
    print("[EXPORT] Building CANDIDATE_N_MANIFEST.json...")
    manifest = {
        "manifest_version": "1.0.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "POLARIS Candidate N (Additive Physics & High-Elevation k_t Specialist) Frozen Artifacts",
        "governance": {
            "winner_status": None,
            "operational_promotion": False,
            "blind_partition_inspected": False,
            "evaluated_on": "2024-ODD (173 origins, 4152 rows, 2883 daytime)",
            "trained_on": "2024-EVEN (174 origins, 4176 rows, 2885 daytime)",
        },
        "environment": {
            "python_version": sys.version,
            "scikit_learn_version": "1.9.0",
            "numpy_version": np.__version__,
            "pandas_version": pd.__version__,
            "joblib_version": joblib.__version__,
        },
        "models": {
            "candidate_n1": {
                "file": "candidate_n1_model.joblib",
                "sha256": sha256_file(n1_model_path),
                "features_count": 36,
                "features": CANDIDATE_N1_36_FEATURES,
                "hyperparameters": {
                    "loss": "absolute_error",
                    "max_depth": 4,
                    "min_samples_leaf": 30,
                    "l2_regularization": 10.0,
                    "max_features": 1.0,
                    "random_state": 42,
                },
                "training_window_utc": {"start": t0_n1, "end": t1_n1},
            },
            "candidate_n6": {
                "file": "candidate_n6_model.joblib",
                "sha256": sha256_file(n6_model_path),
                "features_count": 36,
                "features": CANDIDATE_N1_36_FEATURES,
                "components": {
                    "bagged_additive_trees": {"n_seeds": 25, "seed_start": 100, "max_features": 0.78, "min_samples_leaf": 25, "l2_reg": 15.0},
                    "bagged_kt_trees": {"n_seeds": 15, "seed_start": 500, "max_features": 0.80, "min_samples_leaf": 30, "l2_reg": 15.0},
                    "blending": {"ramp_start_deg": 22.0, "ramp_full_deg": 32.0, "max_ramp_weight": 0.55, "obstruction_flag_filter": True},
                },
                "training_window_utc": {"start": t0_n6, "end": t1_n6},
            }
        },
        "data_provenance": {
            "clean_matrix_file": str(p),
            "clean_matrix_sha256": sha256_file(p),
            "rows_total": 8328,
            "train_rows": 4176,
            "val_rows": 4152,
        }
    }
    manifest_path = ARTIFACTS_DIR / "CANDIDATE_N_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 7. Write HASHES.sha256
    print("[EXPORT] Writing HASHES.sha256...")
    artifact_files = [
        "candidate_n1_model.joblib",
        "candidate_n6_model.joblib",
        "validation_predictions.csv",
        "VALIDATION_RESULTS.json",
        "CANDIDATE_N_MANIFEST.json",
    ]
    hash_lines = []
    for fname in artifact_files:
        fpath = ARTIFACTS_DIR / fname
        hash_lines.append(f"{sha256_file(fpath)}  {fname}")
    hashes_path = ARTIFACTS_DIR / "HASHES.sha256"
    with open(hashes_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hash_lines) + "\n")

    print("[SUCCESS] All Candidate N artifacts successfully generated and hashed!")
    for l in hash_lines:
        print(" ", l)

if __name__ == "__main__":
    main()
