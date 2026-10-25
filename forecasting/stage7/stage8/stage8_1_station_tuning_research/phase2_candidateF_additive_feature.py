#!/usr/bin/env python3
"""
CANDIDATE F -- additive feature test: solar_elevation x cloud_frac.

The single Phase-1-motivated candidate recommended in CANDIDATE_COMPARISON_REPORT.md
("Recommendation for the single next candidate experiment"). Adds ONE new interaction
feature to the existing 37-feature contract (38 features total), both demonstrably available
at forecast time (solar_elevation: astronomical geometry, known in advance; cloud_frac:
already an existing frozen-contract input feature, itself forecast-time-available). No other
change to architecture, hyperparameters, split, or target.

Same frozen EVEN/ODD methodology reused from phase2_train_candidates.py / phase3_weight_experiment.py:
  - Train: 2024 EVEN daytime rows only.
  - Blind evaluation: 2025 (the genuinely blind set -- NOT 2024 ODD, which here plays the
    pure held-out-but-non-blind validation role, consistent with every other candidate in
    this investigation; the task's "2025 ODD" is read as "the 2025 blind set", since 2025
    carries no EVEN/ODD split of its own in this pipeline and was never split that way by
    the frozen model's own methodology either).

No production/config/freeze file modified. Frozen Stage 8.1 artifact never touched.
"""
import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE = Path("/home/punith-bs/01polaris (Copy)")
FREEZE_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_station_tuning_research"
ARTIFACT_DIR = OUT_DIR / "model_artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

MATRIX_2024_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
MATRIX_2025_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
FROZEN_MODEL_PATH = FREEZE_DIR / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"

EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
EXPECTED_MATRIX_2025_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
EXPECTED_MODEL_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"

CANDIDATE_37_FEATURES = [
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
    "u700", "v700",
]
ADDITIVE_FEATURE_NAME = "elevation_x_cloud_frac"
CANDIDATE_F_38_FEATURES = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]
FROZEN_HP = dict(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                  l2_regularization=10.0, random_state=42)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def metrics(actual, pred):
    e = pred - actual
    mae = float(mean_absolute_error(actual, pred))
    rmse = float(np.sqrt(mean_squared_error(actual, pred)))
    bias = float(np.mean(e))
    m = float(np.mean(actual))
    nmae = float((mae / m) * 100.0) if m > 0 else float("nan")
    return {"n": int(len(actual)), "mae": round(mae, 4), "rmse": round(rmse, 4),
            "bias": round(bias, 4), "nmae_pct": round(nmae, 4)}


def apply_night_zero(pred, night_causal_mask):
    out = pred.copy()
    out[night_causal_mask] = 0.0
    return out


def bootstrap_mae_diff_ci(origins_series, actual, pred_candidate, pred_control, n_boot=2000, seed=42):
    rng = np.random.RandomState(seed)
    origins = origins_series.values
    unique_origins = np.unique(origins)
    diffs = []
    for _ in range(n_boot):
        sample = rng.choice(unique_origins, size=len(unique_origins), replace=True)
        mask = np.isin(origins, sample)
        if mask.sum() == 0:
            continue
        mae_c = float(np.mean(np.abs(pred_candidate[mask] - actual[mask])))
        mae_k = float(np.mean(np.abs(pred_control[mask] - actual[mask])))
        diffs.append(mae_c - mae_k)
    diffs = np.array(diffs)
    return {"mean_diff": round(float(diffs.mean()), 4),
            "ci95_lo": round(float(np.percentile(diffs, 2.5)), 4),
            "ci95_hi": round(float(np.percentile(diffs, 97.5)), 4), "n_boot": int(len(diffs))}


def main():
    print("=" * 80)
    print("CANDIDATE F -- additive feature: solar_elevation x cloud_frac")
    print("Train: 2024 EVEN. Blind eval: 2025 (genuinely blind, untouched by training).")
    print("=" * 80)

    hash24 = sha256_of(MATRIX_2024_PATH)
    hash25 = sha256_of(MATRIX_2025_PATH)
    hash_model = sha256_of(FROZEN_MODEL_PATH)
    assert hash24 == EXPECTED_MATRIX_2024_HASH, f"STOP: 2024 matrix hash drift: {hash24}"
    assert hash25 == EXPECTED_MATRIX_2025_HASH, f"STOP: 2025 matrix hash drift: {hash25}"
    assert hash_model == EXPECTED_MODEL_HASH, f"STOP: frozen model hash drift: {hash_model}"
    print(f"2024 matrix hash: {hash24}  (MATCH)")
    print(f"2025 matrix hash: {hash25}  (MATCH)")
    print(f"Frozen model hash: {hash_model}  (MATCH)\n")

    df24 = pd.read_csv(MATRIX_2024_PATH)
    df24["forecast_start"] = pd.to_datetime(df24["forecast_start"], utc=True)
    origins = sorted(df24["forecast_start"].unique())
    even = [o for i, o in enumerate(origins) if i % 2 == 0]
    odd = [o for i, o in enumerate(origins) if i % 2 == 1]
    even_day = df24[df24["forecast_start"].isin(even) & df24["is_daytime"]].copy()
    odd_day = df24[df24["forecast_start"].isin(odd) & df24["is_daytime"]].copy()
    print(f"2024: {len(origins)} origins ({len(even)} EVEN / {len(odd)} ODD) | "
          f"EVEN daytime rows: {len(even_day)} | ODD daytime rows: {len(odd_day)}")

    df25 = pd.read_csv(MATRIX_2025_PATH)
    day25 = df25[df25["is_daytime"]].copy()
    print(f"2025: {len(sorted(df25['forecast_start'].unique()))} origins (blind, untouched) | "
          f"daytime rows: {len(day25)}\n")

    for d in (even_day, odd_day, day25):
        d[ADDITIVE_FEATURE_NAME] = d["solar_elevation"] * d["cloud_frac"]

    X_tr = even_day[CANDIDATE_F_38_FEATURES].values
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    X_odd = odd_day[CANDIDATE_F_38_FEATURES].values
    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values
    night_odd = odd_day["is_night_causal"].values

    X_25 = day25[CANDIDATE_F_38_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_25 = day25["is_night_causal"].values

    # --- Control: frozen artifact's own predictions (37 features, untouched) ---
    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    X_odd_37 = odd_day[CANDIDATE_37_FEATURES].values
    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    pred_odd_ctrl = apply_night_zero(
        np.maximum(0.0, st4_odd + frozen_model.predict(X_odd_37)), night_odd)
    pred_25_ctrl = apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)

    # --- Candidate F: same architecture/hyperparameters, 38 features (37 + interaction) ---
    model_f = HistGradientBoostingRegressor(**FROZEN_HP)
    model_f.fit(X_tr, res_tr)
    pred_odd_f = apply_night_zero(np.maximum(0.0, st4_odd + model_f.predict(X_odd)), night_odd)
    pred_25_f = apply_night_zero(np.maximum(0.0, st4_25 + model_f.predict(X_25)), night_25)

    joblib.dump(model_f, ARTIFACT_DIR / "candidateF_elevation_x_cloud.joblib")
    model_f_hash = sha256_of(ARTIFACT_DIR / "candidateF_elevation_x_cloud.joblib")

    results = {
        "input_hashes": {"matrix_2024": hash24, "matrix_2025": hash25, "frozen_model": hash_model},
        "additive_feature": ADDITIVE_FEATURE_NAME,
        "feature_count": {"control": len(CANDIDATE_37_FEATURES), "candidate_f": len(CANDIDATE_F_38_FEATURES)},
        "hyperparameters": FROZEN_HP,
        "control_frozen_stage81": {
            "odd_2024_validation": metrics(y_odd, pred_odd_ctrl),
            "blind_2025": metrics(y_25, pred_25_ctrl),
        },
        "candidate_F": {
            "odd_2024_validation": metrics(y_odd, pred_odd_f),
            "blind_2025": metrics(y_25, pred_25_f),
        },
        "candidate_f_model_artifact_sha256": model_f_hash,
    }

    # Bootstrap CI, over origins, on blind 2025
    boot = bootstrap_mae_diff_ci(day25["forecast_start"], y_25, pred_25_f, pred_25_ctrl)
    results["bootstrap_mae_diff_vs_control_blind2025"] = boot

    # High-elevation subset check (the regime this feature specifically targets)
    elev = day25["solar_elevation"].values
    high_mask = elev >= 30
    results["high_elevation_subset_blind2025"] = {
        "n": int(high_mask.sum()),
        "control": metrics(y_25[high_mask], pred_25_ctrl[high_mask]),
        "candidate_F": metrics(y_25[high_mask], pred_25_f[high_mask]),
    }
    boot_high = bootstrap_mae_diff_ci(
        day25.loc[high_mask, "forecast_start"], y_25[high_mask], pred_25_f[high_mask], pred_25_ctrl[high_mask])
    results["bootstrap_mae_diff_high_elevation_blind2025"] = boot_high

    promote = boot["ci95_lo"] > 0.0 or boot["ci95_hi"] < 0.0
    # Explicit non-promotion rule from the task: if CI includes zero -> do not promote.
    ci_includes_zero = boot["ci95_lo"] <= 0.0 <= boot["ci95_hi"]
    results["decision"] = {
        "ci_includes_zero": bool(ci_includes_zero),
        "promoted": bool((not ci_includes_zero) and boot["mean_diff"] < 0),
        "rule": "Promote only if bootstrap 95% CI for (candidate-control) blind MAE excludes "
                 "zero AND the point estimate favors the candidate (negative = lower MAE). "
                 "If CI includes zero, do NOT promote, per instruction.",
    }

    print(json.dumps(results, indent=2))
    out_path = OUT_DIR / "CANDIDATE_F_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Candidate F model artifact SHA256: {model_f_hash}")
    print("DECISION:", results["decision"])
    print("CANDIDATE F TEST COMPLETE. Frozen Stage 8.1 artifact untouched.")


if __name__ == "__main__":
    main()
