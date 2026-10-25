#!/usr/bin/env python3
"""
POLARIS — Branch01 (Candidate A, frozen) 2025 blind evaluation.

Runs the frozen Branch01 model (POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1,
MultiOutputRegressor(HistGradientBoostingRegressor), run id
RUN_BRANCH01_CANDIDATE_A_HGB) over the SAME 364 2025 origins / 8,736
origin x horizon rows used by the corrected Stage 8.1 blind evaluation,
reusing the frozen production feature-building code
(forecasting/solar_branch_01/implementation/feature_matrix_builder.py)
unmodified. No retraining, no tuning, no feature/model changes.

Architecture note (not a bug, just a different design than Stage 8.1):
Branch01 takes ONE 18-feature vector per ORIGIN (built strictly from
data at-or-before the origin: causal SW_IN lookback/lag/stat features,
astronomical position, and a clear-sky reference AT the origin) and
its MultiOutputRegressor emits all 24 horizon predictions (t+1h..t+24h)
from that single vector in one call. It does not consume any
horizon-specific NWP/cloud-forecast input at all -- a much simpler,
persistence/astronomy-based model than Stage 8.1's horizon-conditioned
ensemble-residual model. This script reuses that frozen vector-builder
and model exactly as production does; it does not change the
architecture to look more like Stage 8.1's.

Causality note (disclosed, not a leak): Branch01's `sw_in_lag_0h`
feature is the actual SW_IN observed AT the forecast origin itself --
not future data, it's the "current reading" available at forecast
time. Under this repo's horizon_hour convention (horizon_hour=1 ==
valid_time = forecast_start + 0h), that happens to be numerically the
exact same timestamp as the h=1 target. This is an architectural
property of Branch01 (a nowcast-anchored persistence feature), not
something introduced by this script, and does not use any FUTURE
target value as input -- everything used is at-or-before the origin.
Flagged here for transparency since it means h=1 isn't a pure
"blind ahead" test of the same kind h=2..24 are.

Targets/timestamps/horizons/row set: taken directly from the already-
verified corrected Stage 8.1 2025 feature matrix (same 364 origins,
same (forecast_start, horizon_hour, timestamp, actual_SW_IN) grid),
so the two models' results are computed over an identical row set.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"

BRANCH01_MODEL_PATH = BASE / "artifacts" / "model_runs" / "RUN_BRANCH01_CANDIDATE_A_HGB" / "model.joblib"
FROZEN_MODEL_SHA256 = "65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781"
FROZEN_MODEL_ID = "POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1"
FROZEN_RUN_ID = "RUN_BRANCH01_CANDIDATE_A_HGB"

SITES_2025_SW_IN_PATH = BASE / "data" / "POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv"
CLEARSKY_2025_PATH = BASE / "data" / "POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
STAGE8_1_MATRIX_2025_PATH = OUT_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
EXPECTED_STAGE8_1_MATRIX_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"

PRED_PATH = OUT_DIR / "branch01_candidateA_2025_blind_predictions.csv"
RESULTS_PATH = OUT_DIR / "branch01_candidateA_2025_blind_results.json"


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
    print("Branch01 (Candidate A, frozen) — 2025 BLIND EVALUATION (no retraining, no tuning)")
    print("=" * 80)

    # 1. Hash verification BEFORE any inference
    model_hash = sha256_of(BRANCH01_MODEL_PATH)
    matrix_hash = sha256_of(STAGE8_1_MATRIX_2025_PATH)
    sites_hash = sha256_of(SITES_2025_SW_IN_PATH)
    clearsky_hash = sha256_of(CLEARSKY_2025_PATH)

    print(f"Branch01 model hash:        {model_hash}")
    print(f"  expected (frozen):       {FROZEN_MODEL_SHA256}  match={model_hash == FROZEN_MODEL_SHA256}")
    print(f"Stage 8.1 2025 matrix hash: {matrix_hash}")
    print(f"  expected (prior step):   {EXPECTED_STAGE8_1_MATRIX_HASH}  match={matrix_hash == EXPECTED_STAGE8_1_MATRIX_HASH}")
    print(f"SITES 2025 SW_IN hash:      {sites_hash}")
    print(f"Clearsky 2025 hash:         {clearsky_hash}")

    assert model_hash == FROZEN_MODEL_SHA256, "Branch01 model hash mismatch -- refusing to run on an unverified model!"
    assert matrix_hash == EXPECTED_STAGE8_1_MATRIX_HASH, "Stage 8.1 2025 matrix hash mismatch -- row set not verified!"
    print("Hash verification: PASS\n")

    model = joblib.load(BRANCH01_MODEL_PATH)

    # 2. Load the EXACT row set used by corrected Stage 8.1 (same targets/timestamps/horizons)
    s81 = pd.read_csv(STAGE8_1_MATRIX_2025_PATH)
    s81["forecast_start"] = pd.to_datetime(s81["forecast_start"], utc=True)
    s81["timestamp"] = pd.to_datetime(s81["timestamp"], utc=True)
    origins = sorted(s81["forecast_start"].unique())
    n_origins = len(origins)
    n_rows_expected = len(s81)
    print(f"Row set taken from corrected Stage 8.1 2025 matrix: {n_rows_expected} rows, {n_origins} origins")

    # 3. Build the causal SW_IN series (same full 2025 hourly series) and clearsky lookup table
    sw_in_df = pd.read_csv(SITES_2025_SW_IN_PATH)
    sw_in_df["timestamp"] = pd.to_datetime(sw_in_df["TIMESTAMP"], utc=True)
    sw_in_df = sw_in_df.sort_values("timestamp").reset_index(drop=True)
    assert len(sw_in_df) == 8760
    assert sw_in_df["SW_IN"].isna().sum() == 0

    ts_to_idx = {ts: i for i, ts in enumerate(sw_in_df["timestamp"])}

    clearsky_df = pd.read_csv(CLEARSKY_2025_PATH)
    clearsky_df["timestamp"] = pd.to_datetime(clearsky_df["TIMESTAMP"], utc=True)
    # ClearSkyFeatureBuilder looks for "clearsky_sw_in" first, falls back to "clearsky_ghi" (present here)

    # 4. Per-origin inference: ONE 18-feature vector -> 24 horizon predictions (frozen production code, unmodified)
    pred_rows = []
    failures = []
    for origin_t in origins:
        if origin_t not in ts_to_idx:
            failures.append(str(origin_t))
            continue
        origin_idx = ts_to_idx[origin_t]
        try:
            x_vec = FeatureMatrixBuilder.build_feature_vector(
                sw_in_df["SW_IN"], sw_in_df["timestamp"], origin_idx, clearsky_df
            )
        except Exception as e:
            failures.append(f"{origin_t}: {e}")
            continue

        assert x_vec.shape == (18,), f"Feature count mismatch at {origin_t}: {x_vec.shape}"
        assert not np.isnan(x_vec).any() and not np.isinf(x_vec).any(), f"NaN/Inf in feature vector at {origin_t}"

        sw_in_preds = model.predict(x_vec.reshape(1, -1))[0]
        assert len(sw_in_preds) == 24, f"Expected 24 horizon predictions, got {len(sw_in_preds)}"
        assert not np.isnan(sw_in_preds).any() and not np.isinf(sw_in_preds).any(), f"NaN/Inf in predictions at {origin_t}"

        sw_in_preds = np.maximum(0.0, sw_in_preds)  # same non-negative clip as production engine

        for h in range(1, 25):
            pred_rows.append({
                "forecast_start": origin_t,
                "horizon_hour": h,
                "pred_branch01_candidateA": float(sw_in_preds[h - 1]),
            })

    if failures:
        raise RuntimeError(f"{len(failures)} origins failed feature-building/inference: {failures[:5]}")

    pred_df = pd.DataFrame(pred_rows)
    print(f"\nGenerated {len(pred_df)} prediction rows across {pred_df['forecast_start'].nunique()} origins.")

    # 5. Merge onto the EXACT Stage 8.1 row set (same targets/timestamps, enforced by inner merge + count check)
    merged = s81[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "is_daytime"]].merge(
        pred_df, on=["forecast_start", "horizon_hour"], how="inner"
    )
    assert len(merged) == n_rows_expected, f"Row count mismatch after merge: {len(merged)} vs expected {n_rows_expected}"
    assert merged["pred_branch01_candidateA"].isna().sum() == 0

    atomic_write_csv(merged, PRED_PATH)
    pred_hash = sha256_of(PRED_PATH)
    print(f"Predictions saved atomically to: {PRED_PATH}")
    print(f"Predictions SHA256: {pred_hash}")

    # 6. Metrics -- same definitions as the corrected Stage 8.1 2025 blind evaluation
    actual = merged["actual_SW_IN"].values
    pred = merged["pred_branch01_candidateA"].values
    day_mask = merged["is_daytime"].values  # actual_SW_IN > 0, same convention used for Stage 8.1's reporting

    overall = compute_metrics(actual, pred)
    daytime = compute_metrics(actual[day_mask], pred[day_mask])

    print("\n" + "=" * 70)
    print(f"OVERALL (all {overall['n']} rows)")
    print("=" * 70)
    print(f"MAE: {overall['mae']:.6f} W/m²  RMSE: {overall['rmse']:.6f} W/m²  "
          f"Bias: {overall['bias']:+.6f} W/m²  nMAE: {overall['nmae_pct']:.4f}%")

    print("\n" + "=" * 70)
    print(f"DAYTIME ONLY (actual_SW_IN > 0, n={daytime['n']})")
    print("=" * 70)
    print(f"MAE: {daytime['mae']:.6f} W/m²  RMSE: {daytime['rmse']:.6f} W/m²  "
          f"Bias: {daytime['bias']:+.6f} W/m²  nMAE: {daytime['nmae_pct']:.4f}%")

    print("\n" + "=" * 70)
    print("PER-HORIZON (H1-H24) METRICS, DAYTIME (actual_SW_IN > 0)")
    print("=" * 70)
    horizon_rows = []
    for h in range(1, 25):
        hmask = (merged["horizon_hour"].values == h) & day_mask
        if hmask.sum() == 0:
            continue
        m = compute_metrics(actual[hmask], pred[hmask])
        horizon_rows.append({"horizon_hour": h, **m})
        print(f"H{h:2d}: n={m['n']:4d}  MAE={m['mae']:7.3f}  RMSE={m['rmse']:7.3f}  "
              f"Bias={m['bias']:+7.3f}  nMAE={m['nmae_pct']:6.2f}%")

    horizon_df = pd.DataFrame(horizon_rows)
    atomic_write_csv(horizon_df, OUT_DIR / "branch01_candidateA_2025_blind_horizon_metrics.csv")

    results = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "2025 blind evaluation of the frozen Branch01 Candidate A model, over the exact "
                    "same 8,736 origin x horizon rows used by the corrected Stage 8.1 2025 blind evaluation. "
                    "No retraining, no tuning, no feature/model modification. No comparison/winner declared.",
        "model_id": FROZEN_MODEL_ID,
        "run_id": FROZEN_RUN_ID,
        "hash_verification": {
            "model_path": str(BRANCH01_MODEL_PATH), "model_sha256": model_hash,
            "model_hash_matches_frozen_constant": model_hash == FROZEN_MODEL_SHA256,
            "stage8_1_2025_matrix_path": str(STAGE8_1_MATRIX_2025_PATH), "stage8_1_2025_matrix_sha256": matrix_hash,
            "stage8_1_2025_matrix_hash_matches_prior_step": matrix_hash == EXPECTED_STAGE8_1_MATRIX_HASH,
            "sites_2025_sw_in_sha256": sites_hash,
            "clearsky_2025_sha256": clearsky_hash,
        },
        "coverage": {
            "rows": int(len(merged)), "origins": int(merged["forecast_start"].nunique()),
            "matches_stage8_1_row_set_exactly": int(len(merged)) == n_rows_expected,
        },
        "architecture_note": (
            "Branch01 uses one 18-feature vector per ORIGIN (causal SW_IN lookback/lag/stats, "
            "astronomical position, clear-sky reference at origin) and its MultiOutputRegressor "
            "emits all 24 horizon predictions from that single vector -- no horizon-specific NWP "
            "input, unlike Stage 8.1's per-(origin,horizon) feature rows."
        ),
        "causality_note": (
            "sw_in_lag_0h is the actual SW_IN observed AT the origin (known at forecast time, not "
            "future data). Under this repo's horizon_hour=1 == forecast_start+0h convention, this "
            "coincides numerically with the h=1 target timestamp -- an architectural property of "
            "Branch01 as a nowcast-anchored persistence model, not a future-data leak. No actual "
            "SW_IN value from AFTER an origin was used as a feature for that origin's predictions."
        ),
        "feature_count": 18,
        "nmae_definition": "mae / mean(actual) * 100, identical to the corrected Stage 8.1 2025 evaluation",
        "metrics": {"overall": overall, "daytime_actual_gt_0": daytime},
        "per_horizon_daytime_metrics_csv": str(OUT_DIR / "branch01_candidateA_2025_blind_horizon_metrics.csv"),
        "predictions_csv": {"path": str(PRED_PATH), "sha256": pred_hash},
        "comparison_to_stage8_1_performed": False,
        "winner_declared": False,
        "retraining_or_tuning_performed": False,
        "corrected_stage8_1_results_modified": False,
    }
    atomic_write_json(results, RESULTS_PATH)
    print(f"\nResults written to: {RESULTS_PATH}")
    print("\nDone! Branch01 2025 blind evaluation complete. No comparison to Stage 8.1 performed.")


if __name__ == "__main__":
    main()
