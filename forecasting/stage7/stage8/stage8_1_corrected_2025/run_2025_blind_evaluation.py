#!/usr/bin/env python3
"""
POLARIS — CORRECTED Stage 8.1, 2025 blind evaluation.

Loads the already-fitted, frozen CORRECTED 37-feature model (trained
and validated ONLY on 2024 EVEN/ODD in train_corrected_stage8_1_model.py
-- no retraining, no tuning here) and runs it forward over the full
2025 corrected feature matrix. actual_SW_IN for 2025 is used ONLY
after inference, to compute evaluation metrics -- it is never read
into the model's input matrix X.

This is a year-long forecasting evaluation (up to 8760 hourly rows),
not an EMS/MILP closed-loop simulation; no comparison to Branch01 is
performed here.

Day/night gating note (methodological choice, disclosed): the 2024
training procedure gated night-forcing with `is_daytime`
(actual_SW_IN > 0) -- i.e. it looked at the target to decide whether
to run the model or hardcode 0. For a genuinely blind 2025 forecast
that cannot be allowed to peek at the target even for row selection,
this script gates on the purely causal `is_night_causal`
(solar_elevation <= 0 OR clearsky_ghi == 0) instead, which is known
in advance from astronomy + the already-verified clear-sky model.
Both gates are evaluated and reported side by side for transparency;
they disagree on only 1,532/8,736 rows (17.5%), all in one direction
(causally-night hours with a small positive actual_SW_IN, median
0.40 W/m2, 75th pct 2.18 W/m2, max 43.6 W/m2 -- twilight glow, not a
materially different regime), so the choice has a small, quantified
effect, reported below rather than hidden.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
MATRIX_2025_PATH = OUT_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
MODEL_E1_PATH = OUT_DIR / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
TRAIN_RESULTS_PATH = OUT_DIR / "stage8_1_CORRECTED_official_odd_results_2024.json"

PRED_PATH = OUT_DIR / "stage8_1_CORRECTED_2025_blind_predictions.csv"
RESULTS_PATH = OUT_DIR / "stage8_1_CORRECTED_2025_blind_results.json"

# Expected hashes, recorded when these files were produced in prior steps
# of this investigation -- verified before any inference runs.
EXPECTED_MATRIX_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
EXPECTED_MODEL_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"

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

assert "actual_SW_IN" not in candidate_37_features, "Target leaked into feature list!"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_csv(df, path):
    tmp = str(path) + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def atomic_write_json(obj, path):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def compute_metrics(actual, pred):
    residual = pred - actual
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(np.mean(residual ** 2)))
    bias = float(np.mean(residual))
    mean_act = float(np.mean(actual)) if len(actual) else float("nan")
    nmae = float(mae / mean_act * 100.0) if mean_act not in (0, float("nan")) else float("nan")
    return {"n": int(len(actual)), "mae": mae, "rmse": rmse, "bias": bias, "nmae_pct": nmae, "mean_actual": mean_act}


def main():
    print("=" * 80)
    print("CORRECTED Stage 8.1 — 2025 BLIND EVALUATION (no retraining, no tuning)")
    print("=" * 80)

    # 1. Verify hashes BEFORE any inference
    matrix_hash = sha256_of(MATRIX_2025_PATH)
    model_hash = sha256_of(MODEL_E1_PATH)
    print(f"Feature matrix hash: {matrix_hash}")
    print(f"  expected:          {EXPECTED_MATRIX_HASH}  match={matrix_hash == EXPECTED_MATRIX_HASH}")
    print(f"Model artifact hash: {model_hash}")
    print(f"  expected:          {EXPECTED_MODEL_HASH}  match={model_hash == EXPECTED_MODEL_HASH}")
    assert matrix_hash == EXPECTED_MATRIX_HASH, "2025 feature matrix hash mismatch -- refusing to run blind eval on an unverified/changed input!"
    assert model_hash == EXPECTED_MODEL_HASH, "Model artifact hash mismatch -- refusing to run blind eval on an unverified/changed model!"
    print("Hash verification: PASS\n")

    model = joblib.load(MODEL_E1_PATH)
    df = pd.read_csv(MATRIX_2025_PATH)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # 2. Coverage confirmation
    n_rows = len(df)
    n_origins = df["forecast_start"].nunique()
    unique_hours = df["timestamp"].nunique()
    print(f"Rows: {n_rows} | Origins: {n_origins} | Unique valid-time hours: {unique_hours}")
    full_2025_hours = pd.date_range("2025-01-01", "2026-01-01", freq="1h", tz="UTC", inclusive="left")
    missing_hours = sorted(set(full_2025_hours) - set(df["timestamp"]))
    print(f"Hours of 2025 NOT covered by this matrix: {len(missing_hours)}")
    if missing_hours:
        print(f"  First missing: {missing_hours[0]}  Last missing: {missing_hours[-1]}")
        print("  Reason: Stage 3b (Chronos-2) origins start 2025-01-02 (2025-01-01 excluded -- "
              "it would need 2024-12-31 context, out of scope for this 2025-only rebuild). "
              "This is a known, previously-reported limitation, not introduced here.")
    horizons_ok = (df.groupby("forecast_start")["horizon_hour"].count() == 24).all()
    dup = df.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    print(f"24 horizons/origin: {horizons_ok} | Duplicates: {dup}")
    assert horizons_ok and dup == 0

    # 3. Blind-inference input audit
    print(f"\nModel input columns (37): {candidate_37_features}")
    print(f"'actual_SW_IN' present in model input columns: {'actual_SW_IN' in candidate_37_features} (must be False)")
    print(f"NaN cells in X (all from u700/v700, documented coverage gap): "
          f"{df[candidate_37_features].isna().sum().sum()}")

    X_all = df[candidate_37_features].values

    # 4. Day/night gating -- two variants, both reported (see module docstring)
    causally_day = ~df["is_night_causal"].values
    target_based_day = df["is_daytime"].values  # actual_SW_IN > 0 (reference only, not used for the primary blind run)
    gate_disagreement = int((causally_day != target_based_day).sum())
    print(f"\nDay/night gate disagreement (causal vs target-based): {gate_disagreement} / {n_rows} rows")

    # Single vectorized predict call over ALL rows (fast, in-memory, no batching
    # or threading needed for ~8.7k rows on an already-fitted sklearn model --
    # noted explicitly since the task allows up to 8 workers but does not
    # require forcing them where there is no I/O or long-running work to
    # parallelize).
    pred_res_all = model.predict(X_all)
    st4_all = df["pred_stage4_fold"].values
    pred_sw_all_if_day = np.maximum(0.0, st4_all + pred_res_all)

    pred_causal = np.where(causally_day, pred_sw_all_if_day, 0.0)
    pred_target_based = np.where(target_based_day, pred_sw_all_if_day, 0.0)

    df["pred_stage8_1_CORRECTED_blind2025"] = pred_causal
    df["pred_stage8_1_CORRECTED_blind2025_targetgated_refonly"] = pred_target_based

    pred_out = df[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "is_daytime",
                   "is_night_causal", "pred_stage3b_cloud_nwp", "pred_stage4_fold",
                   "pred_stage8_1_CORRECTED_blind2025",
                   "pred_stage8_1_CORRECTED_blind2025_targetgated_refonly"]].copy()
    atomic_write_csv(pred_out, PRED_PATH)
    pred_hash = sha256_of(PRED_PATH)
    print(f"\nPredictions saved atomically to: {PRED_PATH}")
    print(f"Predictions SHA256: {pred_hash}")

    # 5. Metrics
    actual = df["actual_SW_IN"].values
    overall_causal = compute_metrics(actual, pred_causal)
    overall_target = compute_metrics(actual, pred_target_based)

    day_mask_actual = df["is_daytime"].values  # standard convention: daytime = actual_SW_IN > 0, for reporting
    day_causal = compute_metrics(actual[day_mask_actual], pred_causal[day_mask_actual])
    day_target = compute_metrics(actual[day_mask_actual], pred_target_based[day_mask_actual])

    print("\n" + "=" * 70)
    print("OVERALL (all 8,736 rows) -- primary blind run (causal day/night gate)")
    print("=" * 70)
    print(f"MAE: {overall_causal['mae']:.6f} W/m²  RMSE: {overall_causal['rmse']:.6f} W/m²  "
          f"Bias: {overall_causal['bias']:+.6f} W/m²  nMAE: {overall_causal['nmae_pct']:.4f}%")

    print("\n" + "=" * 70)
    print("DAYTIME ONLY (actual_SW_IN > 0, n={}) -- primary blind run".format(day_causal["n"]))
    print("=" * 70)
    print(f"MAE: {day_causal['mae']:.6f} W/m²  RMSE: {day_causal['rmse']:.6f} W/m²  "
          f"Bias: {day_causal['bias']:+.6f} W/m²  nMAE: {day_causal['nmae_pct']:.4f}%")

    print("\n" + "=" * 70)
    print("Reference only: target-based gate (matches 2024 training-procedure convention)")
    print("=" * 70)
    print(f"Overall  MAE: {overall_target['mae']:.6f}  RMSE: {overall_target['rmse']:.6f}  "
          f"Bias: {overall_target['bias']:+.6f}  nMAE: {overall_target['nmae_pct']:.4f}%")
    print(f"Daytime  MAE: {day_target['mae']:.6f}  RMSE: {day_target['rmse']:.6f}  "
          f"Bias: {day_target['bias']:+.6f}  nMAE: {day_target['nmae_pct']:.4f}%")

    # 6. Per-horizon (H1-H24) metrics, daytime subset, primary (causal-gated) predictions
    print("\n" + "=" * 70)
    print("PER-HORIZON (H1-H24) METRICS, DAYTIME (actual_SW_IN > 0), primary blind run")
    print("=" * 70)
    horizon_rows = []
    for h in range(1, 25):
        hmask = (df["horizon_hour"].values == h) & day_mask_actual
        if hmask.sum() == 0:
            continue
        m = compute_metrics(actual[hmask], pred_causal[hmask])
        horizon_rows.append({"horizon_hour": h, **m})
        print(f"H{h:2d}: n={m['n']:4d}  MAE={m['mae']:7.3f}  RMSE={m['rmse']:7.3f}  "
              f"Bias={m['bias']:+7.3f}  nMAE={m['nmae_pct']:6.2f}%")

    horizon_df = pd.DataFrame(horizon_rows)
    atomic_write_csv(horizon_df, OUT_DIR / "stage8_1_CORRECTED_2025_blind_horizon_metrics.csv")

    results = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "2025 blind evaluation of the CORRECTED frozen Stage 8.1 37-feature model. "
                    "No retraining, no tuning, no feature/model modification. actual_SW_IN used "
                    "only for post-inference metrics, never as a model input.",
        "hash_verification": {
            "feature_matrix_path": str(MATRIX_2025_PATH), "feature_matrix_sha256": matrix_hash,
            "feature_matrix_hash_expected_match": matrix_hash == EXPECTED_MATRIX_HASH,
            "model_path": str(MODEL_E1_PATH), "model_sha256": model_hash,
            "model_hash_expected_match": model_hash == EXPECTED_MODEL_HASH,
        },
        "coverage": {
            "rows": n_rows, "origins": n_origins, "unique_valid_time_hours": unique_hours,
            "expected_full_year_hours": 8760,
            "missing_hours_count": len(missing_hours),
            "missing_hours_reason": "Stage 3b origin set starts 2025-01-02 (2025-01-01 excluded for lacking prior-day context); pre-existing, not introduced here." if missing_hours else None,
            "horizons_per_origin_ok": bool(horizons_ok),
            "duplicates": int(dup),
        },
        "blind_inference_audit": {
            "actual_SW_IN_in_model_input_columns": "actual_SW_IN" in candidate_37_features,
            "n_model_input_columns": len(candidate_37_features),
            "nan_cells_in_X": int(df[candidate_37_features].isna().sum().sum()),
            "day_night_gate_used_for_primary_run": "causal (solar_elevation<=0 OR clearsky_ghi==0); does not read actual_SW_IN",
            "day_night_gate_disagreement_with_target_based_gate": gate_disagreement,
            "single_vectorized_predict_call": True,
            "parallel_workers_used": 0,
            "parallelization_rationale": "single in-memory predict() over 8,736 rows on an already-fitted "
                                           "sklearn estimator completes in well under a second; no I/O-bound "
                                           "or long-running work exists to parallelize, so no worker threads "
                                           "were forced (up to 8 were permitted, 0 were needed).",
        },
        "metrics_primary_causal_gate": {
            "overall": overall_causal,
            "daytime_actual_gt_0": day_causal,
        },
        "metrics_reference_target_based_gate": {
            "overall": overall_target,
            "daytime_actual_gt_0": day_target,
        },
        "per_horizon_daytime_metrics_csv": str(OUT_DIR / "stage8_1_CORRECTED_2025_blind_horizon_metrics.csv"),
        "predictions_csv": {"path": str(PRED_PATH), "sha256": pred_hash},
        "branch01_comparison_performed": False,
        "retraining_or_tuning_performed": False,
        "model_or_features_modified": False,
    }
    atomic_write_json(results, RESULTS_PATH)
    print(f"\nResults written to: {RESULTS_PATH}")
    print("\nDone! 2025 blind evaluation complete. No Branch01 comparison performed.")


if __name__ == "__main__":
    main()
