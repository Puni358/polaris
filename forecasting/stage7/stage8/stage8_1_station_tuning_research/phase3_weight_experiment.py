#!/usr/bin/env python3
"""
PHASE 3 -- WEIGHT/OBJECTIVE QUESTION.

Tests ML SAMPLE WEIGHTING during training ONLY (one of the four distinct meanings of
"adjusting the weights" -- see CANDIDATE_COMPARISON_REPORT.md for the explicit distinction
from hyperparameter tuning, ensemble weighting, and optimizer objective weights). The EMS
optimizer's own J1-J4 objective weights (gap19_highs_native.py) are NOT touched anywhere in
this script.

Weighting rule, DEFINED BEFORE EVALUATION, from Phase 1 error forensics (ERROR_FORENSICS_RESULTS.json
"largest_error_contributors_by_elevation": the solar_elevation in [30,90) bucket alone
contributes 45.9% of total |error|, more than any other elevation bucket):

    sample_weight = 1.0 + (solar_elevation / 30.0),  clipped to solar_elevation in [0, 90]

This upweights higher solar-elevation (midday, high-magnitude) training rows more heavily.
`solar_elevation` is available at forecast time (astronomical geometry, known in advance) --
no ODD or 2025 information is used to define or compute the rule.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

BASE = Path("/home/punith-bs/01polaris (Copy)")
FREEZE_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_station_tuning_research"

MATRIX_2024_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
MATRIX_2025_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"

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
FROZEN_HP = dict(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                  l2_regularization=10.0, random_state=42)


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
    print("PHASE 3 -- sample-weighting experiment (elevation-weighted training)")
    print("=" * 80)

    import joblib
    df24 = pd.read_csv(MATRIX_2024_PATH)
    df24["forecast_start"] = pd.to_datetime(df24["forecast_start"], utc=True)
    origins = sorted(df24["forecast_start"].unique())
    even = [o for i, o in enumerate(origins) if i % 2 == 0]
    odd = [o for i, o in enumerate(origins) if i % 2 == 1]
    even_day = df24[df24["forecast_start"].isin(even) & df24["is_daytime"]].copy()
    odd_day = df24[df24["forecast_start"].isin(odd) & df24["is_daytime"]].copy()

    df25 = pd.read_csv(MATRIX_2025_PATH)
    day25 = df25[df25["is_daytime"]].copy()

    X_tr = even_day[CANDIDATE_37_FEATURES].values
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr
    weights = 1.0 + np.clip(even_day["solar_elevation"].values, 0, 90) / 30.0

    X_odd = odd_day[CANDIDATE_37_FEATURES].values
    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values
    night_odd = odd_day["is_night_causal"].values

    X_25 = day25[CANDIDATE_37_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_25 = day25["is_night_causal"].values

    # Control (unweighted), reproduced for apples-to-apples comparison in this script's own run
    control_model = HistGradientBoostingRegressor(**FROZEN_HP)
    control_model.fit(X_tr, res_tr)
    pred_odd_ctrl = apply_night_zero(np.maximum(0.0, st4_odd + control_model.predict(X_odd)), night_odd)
    pred_25_ctrl = apply_night_zero(np.maximum(0.0, st4_25 + control_model.predict(X_25)), night_25)

    # Weighted candidate
    weighted_model = HistGradientBoostingRegressor(**FROZEN_HP)
    weighted_model.fit(X_tr, res_tr, sample_weight=weights)
    pred_odd_w = apply_night_zero(np.maximum(0.0, st4_odd + weighted_model.predict(X_odd)), night_odd)
    pred_25_w = apply_night_zero(np.maximum(0.0, st4_25 + weighted_model.predict(X_25)), night_25)

    results = {
        "weighting_rule": "sample_weight = 1.0 + clip(solar_elevation,0,90)/30.0, defined pre-evaluation from Phase 1 findings",
        "control_unweighted": {"odd_2024": metrics(y_odd, pred_odd_ctrl), "blind_2025": metrics(y_25, pred_25_ctrl)},
        "weighted_candidate": {"odd_2024": metrics(y_odd, pred_odd_w), "blind_2025": metrics(y_25, pred_25_w)},
        "bootstrap_mae_diff_vs_control_blind2025": bootstrap_mae_diff_ci(
            day25["forecast_start"], y_25, pred_25_w, pred_25_ctrl),
    }

    # Regime check: does weighting help specifically at high elevation (where it targeted)?
    elev = day25["solar_elevation"].values
    high_elev_mask = elev >= 30
    results["high_elevation_subset_blind2025"] = {
        "control": metrics(y_25[high_elev_mask], pred_25_ctrl[high_elev_mask]),
        "weighted": metrics(y_25[high_elev_mask], pred_25_w[high_elev_mask]),
    }

    print(json.dumps(results, indent=2))
    out_path = OUT_DIR / "WEIGHT_EXPERIMENT_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print("PHASE 3 COMPLETE. EMS optimizer objective weights NOT touched. Frozen artifacts untouched.")


if __name__ == "__main__":
    main()
