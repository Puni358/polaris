#!/usr/bin/env python3
"""
CANDIDATE H -- Candidate F's features + an asymmetric (quantile) loss, biased toward
under-prediction, to directly target the EMS-relevant overprediction asymmetry.

Forensic motivation:
  - ERROR_FORENSICS_REPORT.md section 3/7: the dominant, systematic error mode of the frozen
    control is OVERPREDICTION (positive bias), monotonically increasing with solar elevation
    (+13.75 W/m^2 at elevation >=30 deg, 45.9% of total |error|).
  - CANDIDATE_COMPARISON_REPORT.md Phase 5 (cited, not re-run here): the EMS actual-solar-
    replay decomposition found 100% of realized-unmet hours coincide with the forecast
    OVERSTATING actual solar at that hour -- overprediction is the asymmetrically costly
    error direction for the downstream dispatch problem, not merely a symmetric nuisance.
  - Phase 3's prior attempt to address this (elevation-weighted sample weights, still trained
    under the symmetric absolute-error loss) FAILED: it nudged raw MAE down marginally but
    made the high-elevation bias WORSE (+13.75 -> +19.95) -- sample weighting under a
    symmetric loss does not by itself change which direction of error the model prefers; it
    only changes which *rows* get more attention, and (as observed) can make the preferred
    direction worse, not better.
  - This candidate is explicitly a DIFFERENT axis from Phase 3: instead of re-weighting rows
    under the same symmetric absolute-error loss, it changes the LOSS FUNCTION ITSELF to an
    asymmetric quantile (pinball) loss with quantile < 0.5, which by construction penalizes
    under-prediction less than over-prediction -- directly targeting the documented asymmetry
    (overprediction is the costly direction) rather than hoping a row-weighting scheme induces
    it as a side effect. Built on top of Candidate F's feature set (38 features: the 37-
    feature contract + elevation_x_cloud_frac), since F is the current best-performing,
    already-audited research baseline.

Quantile choice: quantile=0.35 (asymmetric, below-median). This is a single, pre-specified,
round value chosen BEFORE seeing blind-2025 results -- not grid-searched or selected post hoc
(no ODD-based "best of several quantiles" search is performed here, to avoid repeating
Candidate E's failure mode of selecting on ODD and overclaiming the benefit on blind data; a
single value directly motivated by "push below the symmetric median toward the cheaper
under-prediction side" is used, and this choice is disclosed as a single, un-tuned design
decision, not an optimized one).

Feature/method provenance and leakage check: identical to Candidate F (both features are
forecast-time-available; see CANDIDATE_F_PRE_TRAINING_AUDIT.md item 2). The loss function
change touches ONLY how the model is fit (sklearn `loss="quantile", quantile=0.35` in place of
`loss="absolute_error"`); it does not alter which columns are visible to the model and
introduces no new information channel.

Methodology: identical EVEN/ODD/blind protocol. Train: 2024 EVEN daytime rows only.
Architecture otherwise identical to the frozen control (HistGradientBoostingRegressor,
max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42) -- ONLY `loss` and
`quantile` differ, and the feature set (38 features, Candidate F's). Bootstrap CI uses the
CORRECTED utility (research_utils.bootstrap_mae_diff_ci_corrected).

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
CANDIDATE_F_38_FEATURES = CANDIDATE_37_FEATURES + [ELEV_CLOUD_FEATURE]
QUANTILE = 0.35
H_HP = dict(loss="quantile", quantile=QUANTILE, max_depth=4, min_samples_leaf=30,
            l2_regularization=10.0, random_state=42)


def main():
    print("=" * 80)
    print(f"CANDIDATE H -- Candidate F features + asymmetric quantile loss (q={QUANTILE})")
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
        d[ELEV_CLOUD_FEATURE] = d["solar_elevation"] * d["cloud_frac"]

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
    horizon_25 = day25["horizon_hour"].values

    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    X_odd_37 = odd_day[CANDIDATE_37_FEATURES].values
    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    pred_odd_ctrl = apply_night_zero(
        np.maximum(0.0, st4_odd + frozen_model.predict(X_odd_37)), night_odd)
    pred_25_ctrl = apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)

    model_h = HistGradientBoostingRegressor(**H_HP)
    model_h.fit(X_tr, res_tr)
    pred_odd_h = apply_night_zero(np.maximum(0.0, st4_odd + model_h.predict(X_odd)), night_odd)
    pred_25_h = apply_night_zero(np.maximum(0.0, st4_25 + model_h.predict(X_25)), night_25)

    joblib.dump(model_h, ARTIFACT_DIR / "candidateH_asymmetric_quantile.joblib")
    model_h_hash = sha256_of(ARTIFACT_DIR / "candidateH_asymmetric_quantile.joblib")

    results = {
        "input_hashes": {"matrix_2024": hash24, "matrix_2025": hash25, "frozen_model": hash_model},
        "additive_feature": ELEV_CLOUD_FEATURE,
        "quantile": QUANTILE,
        "feature_count": {"control": len(CANDIDATE_37_FEATURES), "candidate_h": len(CANDIDATE_F_38_FEATURES)},
        "hyperparameters": H_HP,
        "control_frozen_stage81": {
            "odd_2024_validation": metrics(y_odd, pred_odd_ctrl),
            "blind_2025": metrics(y_25, pred_25_ctrl),
        },
        "candidate_H": {
            "odd_2024_validation": metrics(y_odd, pred_odd_h),
            "blind_2025": metrics(y_25, pred_25_h),
        },
        "candidate_h_model_artifact_sha256": model_h_hash,
    }

    boot = bootstrap_mae_diff_ci_corrected(day25["forecast_start"], y_25, pred_25_h, pred_25_ctrl)
    results["bootstrap_mae_diff_vs_control_blind2025_CORRECTED"] = boot

    elev = day25["solar_elevation"].values
    high_mask = elev >= 30
    results["high_elevation_subset_blind2025"] = {
        "n": int(high_mask.sum()),
        "control": metrics(y_25[high_mask], pred_25_ctrl[high_mask]),
        "candidate_H": metrics(y_25[high_mask], pred_25_h[high_mask]),
    }
    boot_high = bootstrap_mae_diff_ci_corrected(
        day25.loc[high_mask, "forecast_start"], y_25[high_mask], pred_25_h[high_mask], pred_25_ctrl[high_mask])
    results["bootstrap_mae_diff_high_elevation_blind2025_CORRECTED"] = boot_high

    results["horizon_breakdown_blind2025"] = horizon_breakdown(horizon_25, y_25, pred_25_ctrl, pred_25_h)

    ci_includes_zero = boot["ci95_lo"] <= 0.0 <= boot["ci95_hi"]
    results["decision"] = {
        "ci_includes_zero": bool(ci_includes_zero),
        "promoted": bool((not ci_includes_zero) and boot["mean_diff"] < 0),
        "rule": "Promote only if CORRECTED bootstrap 95% CI for (candidate-control) blind MAE "
                 "excludes zero AND the point estimate favors the candidate (negative = lower "
                 "MAE). If CI includes zero, do NOT promote, per instruction.",
    }

    print(json.dumps({k: v for k, v in results.items() if k != "horizon_breakdown_blind2025"}, indent=2))
    out_path = OUT_DIR / "CANDIDATE_H_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Candidate H model artifact SHA256: {model_h_hash}")
    print("DECISION:", results["decision"])
    print("CANDIDATE H TEST COMPLETE. Frozen Stage 8.1 artifact untouched.")


if __name__ == "__main__":
    main()
