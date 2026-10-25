#!/usr/bin/env python3
"""
POLARIS — Read-Only Diagnostic Script: Interrogate Frozen Stage 8.1 Model Artifact
Tracking ID: DIAG-S81-MODEL-INTERROGATION-2026-10-20
File: scratch/interrogate_stage81_model.py

Purpose:
  Safely loads and inspects the frozen Stage 8.1 candidate model artifact:
    forecasting/stage7/stage8/stage8_1_corrected_2025/model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib
  without mutating any files, without running predictions, and without calling optimizers.

Extracts:
  1. File existence and SHA-256 integrity digest.
  2. Scikit-learn estimator class and internal parameters.
  3. Feature dimensionality (`n_features_in_`) and feature names (`feature_names_in_`).
  4. Hyperparameter configuration (loss, max_depth, min_samples_leaf, l2_regularization).
  5. Internal bin thresholds (`_bin_mapper.bin_thresholds_`) for `horizon_hour` (feature 0)
     and `hour` (feature 2) to evaluate lead-time horizon bounds and extrapolation behavior.
"""

import sys
import hashlib
from pathlib import Path
import joblib
import numpy as np

EXPECTED_SHA256 = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"
MODEL_PATH = Path("forecasting/stage7/stage8/stage8_1_corrected_2025/model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib")

FROZEN_FEATURE_NAMES_37 = [
    "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
    "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700"
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("POLARIS — READ-ONLY MODEL ARTIFACT INTERROGATION DIAGNOSTIC")
    print("=" * 80)

    if not MODEL_PATH.exists():
        print(f"[FAIL] Model artifact not found at: {MODEL_PATH}")
        sys.exit(1)

    # 1. SHA-256 verification
    actual_hash = sha256_file(MODEL_PATH)
    print(f"Artifact Path:   {MODEL_PATH}")
    print(f"Calculated Hash: {actual_hash}")
    print(f"Expected Hash:   {EXPECTED_SHA256}")
    if actual_hash != EXPECTED_SHA256:
        print("[FAIL] SHA-256 mismatch! Artifact has been modified or corrupted.")
        sys.exit(2)
    else:
        print("[PASS] SHA-256 bit-for-bit match verified.")

    # 2. Load model object
    print("\n--- Model Architecture & Class Inspection ---")
    model = joblib.load(MODEL_PATH)
    print(f"Estimator Class: {type(model).__module__}.{type(model).__name__}")

    # 3. Dimensionality & Feature Names
    print("\n--- Feature Dimensionality & Names ---")
    n_features = getattr(model, "n_features_in_", None)
    print(f"Input Feature Dimensionality (n_features_in_): {n_features}")

    stored_features = getattr(model, "feature_names_in_", None)
    if stored_features is not None:
        print(f"Embedded feature_names_in_ ({len(stored_features)} features):")
        for idx, feat in enumerate(stored_features):
            print(f"  [{idx:02d}] {feat}")
    else:
        print("Model does not store `feature_names_in_` attribute directly.")
        print(f"Checking against canonical 37-feature list (length {len(FROZEN_FEATURE_NAMES_37)}):")
        for idx, feat in enumerate(FROZEN_FEATURE_NAMES_37):
            print(f"  [{idx:02d}] {feat}")

    # 4. Hyperparameters
    print("\n--- Hyperparameter Configuration ---")
    params = model.get_params()
    key_params = [
        "loss", "max_depth", "min_samples_leaf", "l2_regularization",
        "learning_rate", "max_iter", "random_state", "max_bins"
    ]
    for p in key_params:
        print(f"  {p:20s}: {params.get(p)}")

    # 5. Tree & Bin Mapper Analysis
    print("\n--- Internal Bin Mapper & Horizon Bounds Inspection ---")
    bin_mapper = getattr(model, "_bin_mapper", None)
    if bin_mapper is not None and hasattr(bin_mapper, "bin_thresholds_"):
        thresholds = bin_mapper.bin_thresholds_
        print(f"Bin mapper initialized: {len(thresholds)} feature threshold sets found.")

        # Feature 0: horizon_hour
        f0_thresh = thresholds[0]
        print(f"\nFeature [0] ('horizon_hour') Split Bin Thresholds ({len(f0_thresh)} bins):")
        print(f"  Values: {f0_thresh.tolist()}")
        print(f"  Min Bin Threshold: {f0_thresh[0] if len(f0_thresh) > 0 else 'N/A'}")
        print(f"  Max Bin Threshold: {f0_thresh[-1] if len(f0_thresh) > 0 else 'N/A'}")
        if len(f0_thresh) > 0:
            if f0_thresh[-1] < 24.0:
                print("  => CONCLUSION: Feature 0 thresholds terminate strictly BELOW 24 (bounded to <= 23).")
            elif f0_thresh[-1] <= 24.0:
                print("  => CONCLUSION: Feature 0 thresholds terminate at <= 24. Values > 24 fall into the final overflow bin.")
            else:
                print(f"  => CONCLUSION: Feature 0 thresholds include values up to {f0_thresh[-1]}.")

        # Feature 2: hour
        f2_thresh = thresholds[2]
        print(f"\nFeature [2] ('hour') Split Bin Thresholds ({len(f2_thresh)} bins):")
        print(f"  Values: {f2_thresh.tolist()}")
        print(f"  Min Bin Threshold: {f2_thresh[0] if len(f2_thresh) > 0 else 'N/A'}")
        print(f"  Max Bin Threshold: {f2_thresh[-1] if len(f2_thresh) > 0 else 'N/A'}")

    # 6. Ensemble structure
    predictors = getattr(model, "_predictors", None)
    if predictors is not None:
        print(f"\nTotal Boosting Iterations (Trees Built): {len(predictors)}")

    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE — NO MODIFICATIONS PERFORMED")
    print("=" * 80)


if __name__ == "__main__":
    main()
