#!/usr/bin/env python3
"""
CANDIDATE G -- refinement of Candidate F: add a transition-cloud-regime indicator feature.

Forensic motivation (ERROR_FORENSICS_REPORT.md section 4): the "transition" cloud regime
(cloud_frac in [0.2, 0.6)) has the HIGHEST MAE (46.67) and HIGHEST bias (+12.74) of the three
cloud buckets examined (clear/transition/cloudy) -- worse than either clear or fully-cloudy
conditions. Candidate F's elevation_x_cloud_frac interaction gives the model a continuous
signal for "how much elevation-weighted cloud effect", but does not give it an explicit
discontinuous marker for this specific worst-performing regime boundary. This candidate adds
exactly one more additive feature, `is_transition_cloud = 1{0.2 <= cloud_frac < 0.6}`, on top
of Candidate F's 38-feature set (39 features total), to test whether an explicit regime flag
helps the model correct for this specific documented failure mode beyond what the continuous
interaction already captures.

Feature provenance / leakage check:
  - `is_transition_cloud` is a deterministic function of `cloud_frac`, which (per the
    Candidate F audit, item 2, and build_corrected_feature_matrix.py:120) is itself derived
    from `fc_cloud_cover`, an NWP FORECAST field -- forecast-time-available, not an observed/
    actual value. A thresholding of an already-cleared, already-forecast-time-available
    feature introduces no new information channel and no leakage. `actual_SW_IN` does not
    appear in this feature's construction.

Methodology: IDENTICAL EVEN/ODD/blind protocol to every prior candidate in this directory.
Train: 2024 EVEN daytime rows only. Tune/select: 2024 ODD (not used for any decision here,
reported for consistency). Blind comparison: 2025 (genuinely blind, untouched by training).
Same architecture/hyperparameters as the frozen control (HistGradientBoostingRegressor,
max_depth=4, min_samples_leaf=30, l2_regularization=10.0, loss="absolute_error",
random_state=42) -- only the feature set changes. Bootstrap CI uses the CORRECTED utility
(research_utils.bootstrap_mae_diff_ci_corrected), per the Candidate F audit's disclosed,
non-blocking recommendation to duplicate rows per bootstrap draw count rather than relying on
np.isin set membership.

No production/config/freeze file modified. Frozen Stage 8.1 artifact never touched (read-only
joblib.load + .predict() only).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor

from research_utils import (sha256_of, metrics, apply_night_zero,
                             bootstrap_mae_diff_ci_corrected, horizon_breakdown)

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
ELEV_CLOUD_FEATURE = "elevation_x_cloud_frac"
TRANSITION_FEATURE = "is_transition_cloud"
CANDIDATE_G_39_FEATURES = CANDIDATE_37_FEATURES + [ELEV_CLOUD_FEATURE, TRANSITION_FEATURE]
FROZEN_HP = dict(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                  l2_regularization=10.0, random_state=42)


def add_features(d):
    d[ELEV_CLOUD_FEATURE] = d["solar_elevation"] * d["cloud_frac"]
    d[TRANSITION_FEATURE] = ((d["cloud_frac"] >= 0.2) & (d["cloud_frac"] < 0.6)).astype(float)
    return d


def main():
    print("=" * 80)
    print("CANDIDATE G -- Candidate F + transition-cloud-regime indicator feature")
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
        add_features(d)

    print(f"is_transition_cloud prevalence: EVEN {even_day[TRANSITION_FEATURE].mean():.4f}, "
          f"ODD {odd_day[TRANSITION_FEATURE].mean():.4f}, 2025 {day25[TRANSITION_FEATURE].mean():.4f}")

    X_tr = even_day[CANDIDATE_G_39_FEATURES].values
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    X_odd = odd_day[CANDIDATE_G_39_FEATURES].values
    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values
    night_odd = odd_day["is_night_causal"].values

    X_25 = day25[CANDIDATE_G_39_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_25 = day25["is_night_causal"].values
    horizon_25 = day25["horizon_hour"].values

    # --- Control: frozen artifact's own predictions (37 features, untouched, read-only) ---
    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    X_odd_37 = odd_day[CANDIDATE_37_FEATURES].values
    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    pred_odd_ctrl = apply_night_zero(
        np.maximum(0.0, st4_odd + frozen_model.predict(X_odd_37)), night_odd)
    pred_25_ctrl = apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)

    # --- Candidate G: same architecture/hyperparameters, 39 features ---
    model_g = HistGradientBoostingRegressor(**FROZEN_HP)
    model_g.fit(X_tr, res_tr)
    pred_odd_g = apply_night_zero(np.maximum(0.0, st4_odd + model_g.predict(X_odd)), night_odd)
    pred_25_g = apply_night_zero(np.maximum(0.0, st4_25 + model_g.predict(X_25)), night_25)

    joblib.dump(model_g, ARTIFACT_DIR / "candidateG_transition_indicator.joblib")
    model_g_hash = sha256_of(ARTIFACT_DIR / "candidateG_transition_indicator.joblib")

    results = {
        "input_hashes": {"matrix_2024": hash24, "matrix_2025": hash25, "frozen_model": hash_model},
        "additive_features": [ELEV_CLOUD_FEATURE, TRANSITION_FEATURE],
        "feature_count": {"control": len(CANDIDATE_37_FEATURES), "candidate_g": len(CANDIDATE_G_39_FEATURES)},
        "hyperparameters": FROZEN_HP,
        "control_frozen_stage81": {
            "odd_2024_validation": metrics(y_odd, pred_odd_ctrl),
            "blind_2025": metrics(y_25, pred_25_ctrl),
        },
        "candidate_G": {
            "odd_2024_validation": metrics(y_odd, pred_odd_g),
            "blind_2025": metrics(y_25, pred_25_g),
        },
        "candidate_g_model_artifact_sha256": model_g_hash,
    }

    boot = bootstrap_mae_diff_ci_corrected(day25["forecast_start"], y_25, pred_25_g, pred_25_ctrl)
    results["bootstrap_mae_diff_vs_control_blind2025_CORRECTED"] = boot

    elev = day25["solar_elevation"].values
    high_mask = elev >= 30
    results["high_elevation_subset_blind2025"] = {
        "n": int(high_mask.sum()),
        "control": metrics(y_25[high_mask], pred_25_ctrl[high_mask]),
        "candidate_G": metrics(y_25[high_mask], pred_25_g[high_mask]),
    }
    boot_high = bootstrap_mae_diff_ci_corrected(
        day25.loc[high_mask, "forecast_start"], y_25[high_mask], pred_25_g[high_mask], pred_25_ctrl[high_mask])
    results["bootstrap_mae_diff_high_elevation_blind2025_CORRECTED"] = boot_high

    # Transition-regime subset check (the regime this specific feature targets)
    trans_mask = day25[TRANSITION_FEATURE].values.astype(bool)
    results["transition_cloud_subset_blind2025"] = {
        "n": int(trans_mask.sum()),
        "control": metrics(y_25[trans_mask], pred_25_ctrl[trans_mask]),
        "candidate_G": metrics(y_25[trans_mask], pred_25_g[trans_mask]),
    }
    boot_trans = bootstrap_mae_diff_ci_corrected(
        day25.loc[trans_mask, "forecast_start"], y_25[trans_mask], pred_25_g[trans_mask], pred_25_ctrl[trans_mask])
    results["bootstrap_mae_diff_transition_cloud_blind2025_CORRECTED"] = boot_trans

    results["horizon_breakdown_blind2025"] = horizon_breakdown(horizon_25, y_25, pred_25_ctrl, pred_25_g)

    ci_includes_zero = boot["ci95_lo"] <= 0.0 <= boot["ci95_hi"]
    results["decision"] = {
        "ci_includes_zero": bool(ci_includes_zero),
        "promoted": bool((not ci_includes_zero) and boot["mean_diff"] < 0),
        "rule": "Promote only if CORRECTED bootstrap 95% CI for (candidate-control) blind MAE "
                 "excludes zero AND the point estimate favors the candidate (negative = lower "
                 "MAE). If CI includes zero, do NOT promote, per instruction.",
    }

    print(json.dumps({k: v for k, v in results.items() if k != "horizon_breakdown_blind2025"}, indent=2))
    out_path = OUT_DIR / "CANDIDATE_G_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Candidate G model artifact SHA256: {model_g_hash}")
    print("DECISION:", results["decision"])
    print("CANDIDATE G TEST COMPLETE. Frozen Stage 8.1 artifact untouched.")


if __name__ == "__main__":
    main()
