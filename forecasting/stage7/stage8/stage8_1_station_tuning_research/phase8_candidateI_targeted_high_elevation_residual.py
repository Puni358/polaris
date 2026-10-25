#!/usr/bin/env python3
"""
CANDIDATE I -- targeted residual-correction second stage, restricted to the high-solar-
elevation (>=30 deg) regime only, applied on top of Candidate F.

Forensic motivation:
  - ERROR_FORENSICS_REPORT.md section 3: the elevation >=30 deg bucket alone accounts for
    45.9% of total |error| and the largest, most systematic positive bias (+13.75 W/m^2) --
    the single largest avoidable-error regime identified.
  - ERROR_FORENSICS_REPORT.md section 6: R^2=0.4457 for a linear probe of |error| on
    forecast-time-available features -- i.e. there IS exploitable, forecast-time-knowable
    residual structure left in the model's errors, in aggregate.
  - CANDIDATE_COMPARISON_REPORT.md Candidate D already tried a residual-correction second
    stage, but UNTARGETED: trained the correction on out-of-fold (OOF) residuals from ALL
    EVEN rows and applied it to ALL rows. That failed to generalize to blind data (validation
    improved, blind CI centered on zero) -- a classic sign that an untargeted correction
    stage, with the same input features as the base model, mostly re-fits base-model-specific
    noise rather than a genuinely separable, regime-specific signal.
  - This candidate is DELIBERATELY NARROWER than D, per the task's explicit instruction that
    a retry of the residual-correction axis "must be meaningfully different ... targeted only
    at the high-elevation ... regime the forensics flagged, not a repeat of D's untargeted
    approach": the second-stage correction model is trained ONLY on high-elevation
    (solar_elevation >= 30) EVEN rows, using 2-fold OOF base predictions restricted to that
    subset, and is APPLIED ONLY to high-elevation rows at inference; low-elevation rows keep
    Candidate F's prediction completely unchanged. The hypothesis under test: a correction
    stage with a narrower, more homogeneous training target (only the specific regime
    forensics flagged) may generalize better than D's all-regime correction, which mixed a
    much more heterogeneous residual distribution into one second-stage fit.

Feature/method provenance and leakage check:
  - Same 38 input features as Candidate F (37-feature contract + elevation_x_cloud_frac),
    all forecast-time-available (see Candidate F audit item 2).
  - The 2-fold OOF split for computing the correction-stage TRAINING target is performed
    entirely WITHIN the 2024-EVEN set (never touching ODD or 2025), using a deterministic
    hash of forecast_start to assign each EVEN origin to fold 0 or fold 1 -- same principle
    as Candidate D's OOF scheme, applied here only to the elevation>=30 subset of EVEN.
  - `actual_SW_IN` is used only as the regression TARGET for the correction stage (residual
    = actual - OOF base prediction), exactly as in Candidate D and the base/control models
    themselves -- not as an input feature anywhere.

Methodology: identical EVEN/ODD/blind protocol otherwise. Architecture for both the F-style
base model and the correction-stage model: HistGradientBoostingRegressor, same frozen
hyperparameters as the control (max_depth=4, min_samples_leaf=30, l2_regularization=10.0,
loss="absolute_error", random_state=42). Bootstrap CI uses the CORRECTED utility.

No production/config/freeze file modified. Frozen Stage 8.1 artifact never touched (read-only
joblib.load + .predict() only).
"""
import json
import hashlib
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
FROZEN_HP = dict(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                  l2_regularization=10.0, random_state=42)
HIGH_ELEV_THRESHOLD = 30.0


def origin_fold(origin_ts):
    """Deterministic 2-fold assignment of an EVEN origin, by hashing its timestamp string.
    Independent of the EVEN/ODD split itself (which already used i%2 on sorted origins) --
    this is a second, orthogonal fold assignment used only to build OOF base predictions
    within EVEN, same principle as Candidate D's OOF scheme."""
    h = hashlib.md5(str(origin_ts).encode()).hexdigest()
    return int(h, 16) % 2


def main():
    print("=" * 80)
    print("CANDIDATE I -- Candidate F + targeted high-elevation (>=30 deg) residual correction")
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

    even_day["fold2"] = even_day["forecast_start"].apply(origin_fold)
    print(f"EVEN 2-fold split for OOF: fold0={int((even_day['fold2']==0).sum())} rows, "
          f"fold1={int((even_day['fold2']==1).sum())} rows")

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

    # --- Control: frozen artifact (37 features, untouched, read-only) ---
    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    X_odd_37 = odd_day[CANDIDATE_37_FEATURES].values
    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    pred_odd_ctrl = apply_night_zero(
        np.maximum(0.0, st4_odd + frozen_model.predict(X_odd_37)), night_odd)
    pred_25_ctrl = apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)

    # --- Base = Candidate F, fit on full EVEN (same as phase2 script) ---
    model_f_full = HistGradientBoostingRegressor(**FROZEN_HP)
    model_f_full.fit(X_tr, res_tr)
    pred_odd_f = apply_night_zero(np.maximum(0.0, st4_odd + model_f_full.predict(X_odd)), night_odd)
    pred_25_f = apply_night_zero(np.maximum(0.0, st4_25 + model_f_full.predict(X_25)), night_25)

    # --- OOF Candidate-F predictions WITHIN EVEN (2-fold), for building the correction target ---
    oof_pred_f_even = np.zeros(len(even_day))
    for fold in (0, 1):
        train_mask = (even_day["fold2"] != fold).values
        apply_mask = (even_day["fold2"] == fold).values
        m = HistGradientBoostingRegressor(**FROZEN_HP)
        m.fit(X_tr[train_mask], res_tr[train_mask])
        pred_fold = np.maximum(0.0, st4_tr[apply_mask] + m.predict(X_tr[apply_mask]))
        oof_pred_f_even[apply_mask] = pred_fold
    # night-zero not needed here: training target construction restricted to daytime already,
    # and the high-elevation subset below is always daytime (elevation>=30 implies daytime).

    # --- Targeted correction stage: ONLY high-elevation EVEN rows, OOF residual as target ---
    elev_even = even_day["solar_elevation"].values
    high_even_mask = elev_even >= HIGH_ELEV_THRESHOLD
    print(f"High-elevation (>={HIGH_ELEV_THRESHOLD}) EVEN training rows for correction stage: "
          f"{int(high_even_mask.sum())} / {len(even_day)}")

    X_corr_tr = X_tr[high_even_mask]
    oof_resid_tr = y_tr[high_even_mask] - oof_pred_f_even[high_even_mask]
    model_corr = HistGradientBoostingRegressor(**FROZEN_HP)
    model_corr.fit(X_corr_tr, oof_resid_tr)

    joblib.dump(model_f_full, ARTIFACT_DIR / "candidateI_base_F.joblib")
    joblib.dump(model_corr, ARTIFACT_DIR / "candidateI_high_elevation_correction.joblib")
    base_hash = sha256_of(ARTIFACT_DIR / "candidateI_base_F.joblib")
    corr_hash = sha256_of(ARTIFACT_DIR / "candidateI_high_elevation_correction.joblib")

    # --- Apply: correction ONLY where elevation >= 30; elsewhere, F's prediction unchanged ---
    elev_odd = odd_day["solar_elevation"].values
    high_odd_mask = elev_odd >= HIGH_ELEV_THRESHOLD
    pred_odd_i = pred_odd_f.copy()
    if high_odd_mask.sum() > 0:
        corr_odd = model_corr.predict(X_odd[high_odd_mask])
        pred_odd_i[high_odd_mask] = np.maximum(0.0, pred_odd_f[high_odd_mask] + corr_odd)
    pred_odd_i = apply_night_zero(pred_odd_i, night_odd)

    elev_25 = day25["solar_elevation"].values
    high_25_mask = elev_25 >= HIGH_ELEV_THRESHOLD
    pred_25_i = pred_25_f.copy()
    if high_25_mask.sum() > 0:
        corr_25 = model_corr.predict(X_25[high_25_mask])
        pred_25_i[high_25_mask] = np.maximum(0.0, pred_25_f[high_25_mask] + corr_25)
    pred_25_i = apply_night_zero(pred_25_i, night_25)

    results = {
        "input_hashes": {"matrix_2024": hash24, "matrix_2025": hash25, "frozen_model": hash_model},
        "method": "Candidate F base + second-stage HGB correction, trained ONLY on "
                   "solar_elevation>=30 EVEN rows (2-fold OOF target), applied ONLY to "
                   "solar_elevation>=30 rows at inference; all other rows = Candidate F unchanged.",
        "high_elevation_threshold_deg": HIGH_ELEV_THRESHOLD,
        "additive_feature": ELEV_CLOUD_FEATURE,
        "feature_count": {"control": len(CANDIDATE_37_FEATURES), "candidate_i_base": len(CANDIDATE_F_38_FEATURES)},
        "hyperparameters": FROZEN_HP,
        "n_even_high_elevation_training_rows": int(high_even_mask.sum()),
        "control_frozen_stage81": {
            "odd_2024_validation": metrics(y_odd, pred_odd_ctrl),
            "blind_2025": metrics(y_25, pred_25_ctrl),
        },
        "candidate_F_base_reference": {
            "odd_2024_validation": metrics(y_odd, pred_odd_f),
            "blind_2025": metrics(y_25, pred_25_f),
        },
        "candidate_I": {
            "odd_2024_validation": metrics(y_odd, pred_odd_i),
            "blind_2025": metrics(y_25, pred_25_i),
        },
        "candidate_i_base_model_artifact_sha256": base_hash,
        "candidate_i_correction_model_artifact_sha256": corr_hash,
    }

    boot = bootstrap_mae_diff_ci_corrected(day25["forecast_start"], y_25, pred_25_i, pred_25_ctrl)
    results["bootstrap_mae_diff_vs_control_blind2025_CORRECTED"] = boot

    results["high_elevation_subset_blind2025"] = {
        "n": int(high_25_mask.sum()),
        "control": metrics(y_25[high_25_mask], pred_25_ctrl[high_25_mask]),
        "candidate_F_base": metrics(y_25[high_25_mask], pred_25_f[high_25_mask]),
        "candidate_I": metrics(y_25[high_25_mask], pred_25_i[high_25_mask]),
    }
    boot_high = bootstrap_mae_diff_ci_corrected(
        day25.loc[high_25_mask, "forecast_start"], y_25[high_25_mask],
        pred_25_i[high_25_mask], pred_25_ctrl[high_25_mask])
    results["bootstrap_mae_diff_high_elevation_blind2025_CORRECTED"] = boot_high

    results["horizon_breakdown_blind2025"] = horizon_breakdown(horizon_25, y_25, pred_25_ctrl, pred_25_i)

    ci_includes_zero = boot["ci95_lo"] <= 0.0 <= boot["ci95_hi"]
    results["decision"] = {
        "ci_includes_zero": bool(ci_includes_zero),
        "promoted": bool((not ci_includes_zero) and boot["mean_diff"] < 0),
        "rule": "Promote only if CORRECTED bootstrap 95% CI for (candidate-control) blind MAE "
                 "excludes zero AND the point estimate favors the candidate (negative = lower "
                 "MAE). If CI includes zero, do NOT promote, per instruction.",
    }

    print(json.dumps({k: v for k, v in results.items() if k != "horizon_breakdown_blind2025"}, indent=2))
    out_path = OUT_DIR / "CANDIDATE_I_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Candidate I base model SHA256: {base_hash}")
    print(f"Candidate I correction model SHA256: {corr_hash}")
    print("DECISION:", results["decision"])
    print("CANDIDATE I TEST COMPLETE. Frozen Stage 8.1 artifact untouched.")


if __name__ == "__main__":
    main()
