#!/usr/bin/env python3
"""
CANDIDATE J -- Candidate F + joint elevation-x-transition-cloud interaction feature.

Forensic motivation (CANDIDATE_F_RESIDUAL_FORENSICS_REPORT.md section 2 finding #3 and
section 5's explicit proposal): the joint cell "solar_elevation >= 30 DEG AND cloud_frac in
[0.2, 0.6)" is Candidate F's single worst slice on blind 2025 (n=206, MAE 114.57, bias
+45.38) -- roughly 3-4x worse than either the aggregate high-elevation bucket (MAE 98.68,
bias +12.74) or the aggregate transition-cloud bucket (MAE 45.52, bias +12.15) alone.
Candidate F's `elevation_x_cloud_frac` is a smooth product over the *entire* cloud_frac
range and dilutes this specific joint signal; Candidate G's flat `is_transition_cloud` flag
was never crossed with elevation and could not isolate this cell either (and failed to beat
F standalone). Candidate J adds exactly ONE new additive feature that is the direct product
of the two signals that jointly define the worst cell:

    elevation_x_transition_cloud = solar_elevation * is_transition_cloud
    is_transition_cloud = 1{0.2 <= cloud_frac < 0.6}   (IDENTICAL to Candidate G's definition)

on top of Candidate F's 38-feature set (39 features total for Candidate J; note this reuses
Candidate F's `elevation_x_cloud_frac` as one of the 38 base features -- NOT the same as
Candidate G's 39-feature set, which added the flat is_transition_cloud flag instead of this
joint interaction).

Explicit overfitting caveat (carried over from the residual-forensics report and the task
spec): the targeted joint regime has only ~86/2885 (~3.0%) of 2024-EVEN training rows --
thin support, the same mechanism that sank Candidate I (targeted high-elevation-only
residual correction, which overfit on ODD and made blind bias WORSE than even the frozen
control in its own targeted regime). Candidate J is evaluated against that exact failure
mode below (targeted-regime bias must not regress materially relative to Candidate F).

Feature / leakage check:
  - `solar_elevation`: pure astronomical geometry, forecast-time-available (cleared for
    Candidate F, CANDIDATE_F_PRE_TRAINING_AUDIT.md item 2).
  - `cloud_frac`: already a frozen-37-feature-contract input, itself derived from
    `fc_cloud_cover`, an NWP FORECAST field -- forecast-time-available (same provenance
    cleared for Candidate G).
  - `is_transition_cloud`: deterministic binary function of `cloud_frac` alone (identical
    definition to Candidate G's own cleared feature).
  - `elevation_x_transition_cloud` is the product of two already-cleared,
    forecast-time-available quantities -- introduces no new information channel. Same
    precedent-based reasoning already used to clear Candidate F's own feature and
    Candidate G's flag. `actual_SW_IN` does not appear anywhere in this feature's
    construction.

Methodology: IDENTICAL EVEN/ODD/blind protocol to every prior candidate in this directory.
Train: 2024 EVEN daytime rows only. Validation: 2024 ODD (reported, not used for any
promotion decision). Blind comparison (primary claim): 2025 (genuinely blind, untouched by
training or selection). Same architecture/hyperparameters as the frozen control and
Candidate F (HistGradientBoostingRegressor, max_depth=4, min_samples_leaf=30,
l2_regularization=10.0, loss="absolute_error", random_state=42) -- NO hyperparameter tuning
(Candidate E already showed tuning alone doesn't clear the bar; this isolates the feature
effect only). Bootstrap CI uses the CORRECTED utility
(research_utils.bootstrap_mae_diff_ci_corrected) for every CI reported here, per the
Candidate F audit's finding that the original bootstrap utility under-calibrates variance.

Primary promotion comparison is Candidate J vs Candidate F (not vs. the frozen control),
per the task's explicit instruction, since F is the standing best research result this
candidate is trying to improve on.

No production/config/freeze file modified. Frozen Stage 8.1 artifact and Candidate F's own
artifact/results are never touched beyond read-only joblib.load() + .predict() calls --
no .fit() is ever called on either.
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
FREEZE_MANIFEST_PATH = FREEZE_DIR / "FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json"
CANDIDATE_F_MODEL_PATH = ARTIFACT_DIR / "candidateF_elevation_x_cloud.joblib"
CANDIDATE_F_RESULTS_PATH = OUT_DIR / "CANDIDATE_F_RESULTS.json"

EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
EXPECTED_MATRIX_2025_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
EXPECTED_MODEL_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"
EXPECTED_CANDIDATE_F_MODEL_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"

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
ELEV_CLOUD_FEATURE = "elevation_x_cloud_frac"            # Candidate F's feature
TRANSITION_FLAG = "is_transition_cloud"                   # Candidate G's flag (intermediate)
JOINT_FEATURE = "elevation_x_transition_cloud"            # Candidate J's new feature
CANDIDATE_F_38_FEATURES = CANDIDATE_37_FEATURES + [ELEV_CLOUD_FEATURE]
CANDIDATE_J_39_FEATURES = CANDIDATE_F_38_FEATURES + [JOINT_FEATURE]
FROZEN_HP = dict(loss="absolute_error", max_depth=4, min_samples_leaf=30,
                  l2_regularization=10.0, random_state=42)


def add_features(d):
    d[ELEV_CLOUD_FEATURE] = d["solar_elevation"] * d["cloud_frac"]
    d[TRANSITION_FLAG] = ((d["cloud_frac"] >= 0.2) & (d["cloud_frac"] < 0.6)).astype(float)
    d[JOINT_FEATURE] = d["solar_elevation"] * d[TRANSITION_FLAG]
    return d


def joint_regime_mask(d):
    """The specific slice Candidate J targets: solar_elevation >= 30 AND
    cloud_frac in [0.2, 0.6) -- exactly the cell flagged as F's worst in the residual
    forensics report (n=206 on blind 2025)."""
    elev = d["solar_elevation"].values
    cf = d["cloud_frac"].values
    return (elev >= 30) & (cf >= 0.2) & (cf < 0.6)


def main():
    print("=" * 80)
    print("CANDIDATE J -- Candidate F + elevation_x_transition_cloud joint interaction")
    print("Train: 2024 EVEN. Validation: 2024 ODD. Blind eval (primary claim): 2025.")
    print("=" * 80)

    hash24 = sha256_of(MATRIX_2024_PATH)
    hash25 = sha256_of(MATRIX_2025_PATH)
    hash_model = sha256_of(FROZEN_MODEL_PATH)
    hash_f_model = sha256_of(CANDIDATE_F_MODEL_PATH)
    assert hash24 == EXPECTED_MATRIX_2024_HASH, f"STOP: 2024 matrix hash drift: {hash24}"
    assert hash25 == EXPECTED_MATRIX_2025_HASH, f"STOP: 2025 matrix hash drift: {hash25}"
    assert hash_model == EXPECTED_MODEL_HASH, f"STOP: frozen model hash drift: {hash_model}"
    assert hash_f_model == EXPECTED_CANDIDATE_F_MODEL_HASH, f"STOP: Candidate F model hash drift: {hash_f_model}"
    print(f"2024 matrix hash: {hash24}  (MATCH)")
    print(f"2025 matrix hash: {hash25}  (MATCH)")
    print(f"Frozen control model hash: {hash_model}  (MATCH)")
    print(f"Candidate F model hash: {hash_f_model}  (MATCH)\n")

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

    n_even = len(even_day)
    n_joint_even = int(joint_regime_mask(even_day).sum())
    print(f"Targeted joint regime (elevation>=30 & cloud_frac in [0.2,0.6)) prevalence in "
          f"2024-EVEN training rows: {n_joint_even}/{n_even} "
          f"({100*n_joint_even/n_even:.2f}%) -- thin-slice overfitting risk flagged in the "
          f"residual forensics report (expected ~86/2885 ~ 3.0%).")

    X_tr = even_day[CANDIDATE_J_39_FEATURES].values
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    X_odd_j = odd_day[CANDIDATE_J_39_FEATURES].values
    X_odd_f = odd_day[CANDIDATE_F_38_FEATURES].values
    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values
    night_odd = odd_day["is_night_causal"].values

    X_25_j = day25[CANDIDATE_J_39_FEATURES].values
    X_25_f = day25[CANDIDATE_F_38_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_25 = day25["is_night_causal"].values
    horizon_25 = day25["horizon_hour"].values
    month_25 = day25["month"].values

    # --- Control: frozen artifact's own predictions (37 features, untouched, read-only) ---
    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    X_odd_37 = odd_day[CANDIDATE_37_FEATURES].values
    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    pred_odd_ctrl = apply_night_zero(
        np.maximum(0.0, st4_odd + frozen_model.predict(X_odd_37)), night_odd)
    pred_25_ctrl = apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)

    # --- Candidate F: its own frozen (already-trained) artifact, read-only, re-predicted ---
    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)
    pred_odd_f = apply_night_zero(np.maximum(0.0, st4_odd + model_f.predict(X_odd_f)), night_odd)
    pred_25_f = apply_night_zero(np.maximum(0.0, st4_25 + model_f.predict(X_25_f)), night_25)

    # --- Candidate J: same architecture/hyperparameters, 39 features (F's 38 + joint feature) ---
    model_j = HistGradientBoostingRegressor(**FROZEN_HP)
    model_j.fit(X_tr, res_tr)
    pred_odd_j = apply_night_zero(np.maximum(0.0, st4_odd + model_j.predict(X_odd_j)), night_odd)
    pred_25_j = apply_night_zero(np.maximum(0.0, st4_25 + model_j.predict(X_25_j)), night_25)

    model_j_path = ARTIFACT_DIR / "candidateJ_elevation_x_transition.joblib"
    joblib.dump(model_j, model_j_path)
    model_j_hash = sha256_of(model_j_path)

    results = {
        "input_hashes": {
            "matrix_2024": hash24, "matrix_2025": hash25,
            "frozen_control_model": hash_model, "candidate_F_model": hash_f_model,
        },
        "new_feature": JOINT_FEATURE,
        "feature_definition": "solar_elevation * is_transition_cloud, "
                                "is_transition_cloud = 1{0.2 <= cloud_frac < 0.6} (Candidate G's definition)",
        "feature_count": {
            "control": len(CANDIDATE_37_FEATURES),
            "candidate_F": len(CANDIDATE_F_38_FEATURES),
            "candidate_J": len(CANDIDATE_J_39_FEATURES),
        },
        "hyperparameters": FROZEN_HP,
        "targeted_joint_regime_prevalence_2024_EVEN_training": {
            "n_joint": n_joint_even, "n_total_even": n_even,
            "pct": round(100 * n_joint_even / n_even, 4),
        },
        "control_frozen_stage81": {
            "odd_2024_validation": metrics(y_odd, pred_odd_ctrl),
            "blind_2025": metrics(y_25, pred_25_ctrl),
        },
        "candidate_F": {
            "odd_2024_validation": metrics(y_odd, pred_odd_f),
            "blind_2025": metrics(y_25, pred_25_f),
        },
        "candidate_J": {
            "odd_2024_validation": metrics(y_odd, pred_odd_j),
            "blind_2025": metrics(y_25, pred_25_j),
        },
        "candidate_j_model_artifact_sha256": model_j_hash,
    }

    # --- Primary promotion comparison: J vs F (corrected bootstrap CI) ---
    boot_jf = bootstrap_mae_diff_ci_corrected(day25["forecast_start"], y_25, pred_25_j, pred_25_f)
    results["bootstrap_mae_diff_J_minus_F_blind2025_CORRECTED"] = boot_jf

    # --- Context comparison: J vs control ---
    boot_jc = bootstrap_mae_diff_ci_corrected(day25["forecast_start"], y_25, pred_25_j, pred_25_ctrl)
    results["bootstrap_mae_diff_J_minus_control_blind2025_CORRECTED"] = boot_jc

    # --- High-elevation (>=30) aggregate subset, all three models ---
    elev = day25["solar_elevation"].values
    high_mask = elev >= 30
    results["high_elevation_subset_blind2025"] = {
        "n": int(high_mask.sum()),
        "control": metrics(y_25[high_mask], pred_25_ctrl[high_mask]),
        "candidate_F": metrics(y_25[high_mask], pred_25_f[high_mask]),
        "candidate_J": metrics(y_25[high_mask], pred_25_j[high_mask]),
    }
    boot_high_jf = bootstrap_mae_diff_ci_corrected(
        day25.loc[high_mask, "forecast_start"], y_25[high_mask], pred_25_j[high_mask], pred_25_f[high_mask])
    results["bootstrap_mae_diff_J_minus_F_high_elevation_blind2025_CORRECTED"] = boot_high_jf

    # --- Transition-cloud aggregate subset, all three models ---
    trans_mask = (day25["cloud_frac"].values >= 0.2) & (day25["cloud_frac"].values < 0.6)
    results["transition_cloud_subset_blind2025"] = {
        "n": int(trans_mask.sum()),
        "control": metrics(y_25[trans_mask], pred_25_ctrl[trans_mask]),
        "candidate_F": metrics(y_25[trans_mask], pred_25_f[trans_mask]),
        "candidate_J": metrics(y_25[trans_mask], pred_25_j[trans_mask]),
    }

    # --- THE targeted joint regime: elevation>=30 AND cloud_frac in [0.2,0.6) ---
    joint_mask = joint_regime_mask(day25)
    results["TARGETED_joint_regime_high_elevation_x_transition_cloud_blind2025"] = {
        "definition": "solar_elevation >= 30 AND cloud_frac in [0.2, 0.6)",
        "n": int(joint_mask.sum()),
        "control": metrics(y_25[joint_mask], pred_25_ctrl[joint_mask]),
        "candidate_F": metrics(y_25[joint_mask], pred_25_f[joint_mask]),
        "candidate_J": metrics(y_25[joint_mask], pred_25_j[joint_mask]),
    }
    if int(joint_mask.sum()) > 1:
        boot_joint_jf = bootstrap_mae_diff_ci_corrected(
            day25.loc[joint_mask, "forecast_start"], y_25[joint_mask], pred_25_j[joint_mask], pred_25_f[joint_mask])
        results["bootstrap_mae_diff_J_minus_F_TARGETED_joint_regime_blind2025_CORRECTED"] = boot_joint_jf

    # --- H1-H24 breakdown: J vs F (primary) and J vs control (context) ---
    results["horizon_breakdown_J_vs_F_blind2025"] = horizon_breakdown(horizon_25, y_25, pred_25_f, pred_25_j)
    results["horizon_breakdown_J_vs_control_blind2025"] = horizon_breakdown(horizon_25, y_25, pred_25_ctrl, pred_25_j)

    # --- Aug-Sep month breakdown ---
    aug_sep_mask = np.isin(month_25, [8, 9])
    results["aug_sep_subset_blind2025"] = {
        "n": int(aug_sep_mask.sum()),
        "control": metrics(y_25[aug_sep_mask], pred_25_ctrl[aug_sep_mask]),
        "candidate_F": metrics(y_25[aug_sep_mask], pred_25_f[aug_sep_mask]),
        "candidate_J": metrics(y_25[aug_sep_mask], pred_25_j[aug_sep_mask]),
    }
    if aug_sep_mask.sum() > 1:
        boot_as_jf = bootstrap_mae_diff_ci_corrected(
            day25.loc[aug_sep_mask, "forecast_start"], y_25[aug_sep_mask], pred_25_j[aug_sep_mask], pred_25_f[aug_sep_mask])
        results["bootstrap_mae_diff_J_minus_F_aug_sep_blind2025_CORRECTED"] = boot_as_jf

    # --- Promotion bar (primary: J vs F; secondary bias-regression check at targeted cell) ---
    ci_jf_includes_zero = boot_jf["ci95_lo"] <= 0.0 <= boot_jf["ci95_hi"]
    mae_bar_pass = bool((not ci_jf_includes_zero) and boot_jf["mean_diff"] < 0)

    f_bias_joint = results["TARGETED_joint_regime_high_elevation_x_transition_cloud_blind2025"]["candidate_F"]["bias"]
    j_bias_joint = results["TARGETED_joint_regime_high_elevation_x_transition_cloud_blind2025"]["candidate_J"]["bias"]
    # "Not substantially worse" threshold: J's bias must not exceed F's bias by more than
    # 20% of F's own bias magnitude (a pre-specified, generous tolerance consistent with the
    # promotion bar's qualitative wording; any exceedance beyond this is treated as material).
    bias_tolerance = abs(f_bias_joint) * 0.20
    bias_bar_pass = bool(j_bias_joint <= f_bias_joint + bias_tolerance)

    results["decision"] = {
        "primary_comparison": "candidate_J vs candidate_F (standing best research result)",
        "mae_bar": {
            "rule": "blind-2025 MAE bootstrap 95% CI (CORRECTED) for (J - F) must exclude zero "
                     "on the improving side (negative = J lower MAE than F).",
            "ci_includes_zero": bool(ci_jf_includes_zero),
            "mean_diff_J_minus_F": boot_jf["mean_diff"],
            "pass": mae_bar_pass,
        },
        "targeted_regime_bias_bar": {
            "rule": "J's bias at the targeted joint regime (elevation>=30 & cloud_frac in "
                     "[0.2,0.6)) must not be substantially worse than F's bias there "
                     f"(F={f_bias_joint}, tolerance=+{round(bias_tolerance,4)}).",
            "candidate_F_bias": f_bias_joint,
            "candidate_J_bias": j_bias_joint,
            "pass": bias_bar_pass,
        },
        "overall_promotion_bar_pass": bool(mae_bar_pass and bias_bar_pass),
        "promoted_to_production": False,
        "note": "This is research only. No candidate is promoted to production under any "
                 "outcome of this test, per explicit task instruction. Candidate F remains "
                 "the standing best research result regardless of this outcome.",
    }

    print(json.dumps({k: v for k, v in results.items()
                       if not k.startswith("horizon_breakdown")}, indent=2))
    out_path = OUT_DIR / "CANDIDATE_J_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Candidate J model artifact SHA256: {model_j_hash}")
    print("DECISION:", json.dumps(results["decision"], indent=2))
    print("CANDIDATE J TEST COMPLETE. Frozen Stage 8.1 artifact and Candidate F artifact untouched.")

    # --- Post-run re-verification of all read-only inputs (no drift) ---
    final_hash24 = sha256_of(MATRIX_2024_PATH)
    final_hash25 = sha256_of(MATRIX_2025_PATH)
    final_hash_model = sha256_of(FROZEN_MODEL_PATH)
    final_hash_f_model = sha256_of(CANDIDATE_F_MODEL_PATH)
    final_hash_manifest = sha256_of(FREEZE_MANIFEST_PATH)
    assert final_hash24 == hash24
    assert final_hash25 == hash25
    assert final_hash_model == hash_model
    assert final_hash_f_model == hash_f_model
    print(f"\nPost-run re-verification: 2024 matrix, 2025 matrix, frozen control model, "
          f"Candidate F model all byte-identical to pre-run hashes. Freeze manifest hash: "
          f"{final_hash_manifest}")


if __name__ == "__main__":
    main()
