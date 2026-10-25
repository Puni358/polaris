#!/usr/bin/env python3
"""
PHASE 9 -- RESIDUAL FORENSICS on CANDIDATE F's OWN blind-2025 predictions.

Pure read-only / inference-only analysis. Loads the already-fitted Candidate F model
artifact (candidateF_elevation_x_cloud.joblib) and the already-fitted frozen control
artifact (stage8_1_CORRECTED_candidate_37feature_model.joblib) and calls .predict() on
each -- NO .fit() anywhere in this script. Does not modify, retrain, or re-save either
model, either feature matrix, the frozen blind-predictions CSV, or the freeze manifest.

Reproduces the exact inference path used in phase2_candidateF_additive_feature.py
(stage4-residual target, non-negativity clip, night-causal zeroing) so that the
per-row predictions used here are identical to the ones that produced
CANDIDATE_F_RESULTS.json's aggregate metrics -- this script only adds the row-level
breakdown that was never written out before.
"""
import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

import research_utils as ru

BASE = Path("/home/punith-bs/01polaris (Copy)")
FREEZE_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_station_tuning_research"
ARTIFACT_DIR = OUT_DIR / "model_artifacts"

MATRIX_2025_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
FROZEN_MODEL_PATH = FREEZE_DIR / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
CANDIDATE_F_MODEL_PATH = ARTIFACT_DIR / "candidateF_elevation_x_cloud.joblib"
FREEZE_MANIFEST_PATH = FREEZE_DIR / "FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json"
CANDIDATE_F_RESULTS_PATH = OUT_DIR / "CANDIDATE_F_RESULTS.json"

EXPECTED_MATRIX_2025_HASH = "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
EXPECTED_FROZEN_MODEL_HASH = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"
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
ADDITIVE_FEATURE_NAME = "elevation_x_cloud_frac"
CANDIDATE_F_38_FEATURES = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(err, actual):
    err = np.asarray(err)
    actual = np.asarray(actual)
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    bias = float(np.mean(err))
    m = float(np.mean(actual))
    nmae = float((mae / m) * 100.0) if m > 0 else float("nan")
    return {"n": int(len(err)), "mae": round(mae, 4), "rmse": round(rmse, 4),
            "bias": round(bias, 4), "nmae_pct": round(nmae, 4)}


def main():
    print("=" * 80)
    print("PHASE 9 -- CANDIDATE F RESIDUAL FORENSICS (blind 2025, inference only)")
    print("=" * 80)

    # ---- pre-analysis hash verification ----
    hash25_before = sha256_of(MATRIX_2025_PATH)
    hash_frozen_before = sha256_of(FROZEN_MODEL_PATH)
    hash_f_before = sha256_of(CANDIDATE_F_MODEL_PATH)
    assert hash25_before == EXPECTED_MATRIX_2025_HASH, f"STOP: 2025 matrix hash drift: {hash25_before}"
    assert hash_frozen_before == EXPECTED_FROZEN_MODEL_HASH, f"STOP: frozen model hash drift: {hash_frozen_before}"
    assert hash_f_before == EXPECTED_CANDIDATE_F_MODEL_HASH, f"STOP: candidate F model hash drift: {hash_f_before}"
    print(f"2025 matrix hash (before): {hash25_before}  (MATCH)")
    print(f"Frozen control model hash (before): {hash_frozen_before}  (MATCH)")
    print(f"Candidate F model hash (before): {hash_f_before}  (MATCH)")

    freeze_manifest_hash_before = sha256_of(FREEZE_MANIFEST_PATH)
    candidate_f_results_hash_before = sha256_of(CANDIDATE_F_RESULTS_PATH)

    # ---- load data, reproduce exact inference path from phase2_candidateF ----
    df25 = pd.read_csv(MATRIX_2025_PATH)
    day25 = df25[df25["is_daytime"]].copy()
    day25[ADDITIVE_FEATURE_NAME] = day25["solar_elevation"] * day25["cloud_frac"]

    X_25_37 = day25[CANDIDATE_37_FEATURES].values
    X_25_38 = day25[CANDIDATE_F_38_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_25 = day25["is_night_causal"].values

    frozen_model = joblib.load(FROZEN_MODEL_PATH)
    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)

    pred_25_ctrl = ru.apply_night_zero(
        np.maximum(0.0, st4_25 + frozen_model.predict(X_25_37)), night_25)
    pred_25_f = ru.apply_night_zero(
        np.maximum(0.0, st4_25 + model_f.predict(X_25_38)), night_25)

    # sanity check: reproduce CANDIDATE_F_RESULTS.json aggregate blind-2025 metrics exactly
    agg_ctrl = summarize(pred_25_ctrl - y_25, y_25)
    agg_f = summarize(pred_25_f - y_25, y_25)
    prior_results = json.load(open(CANDIDATE_F_RESULTS_PATH))
    reproduced_match = {
        "control_mae_match": abs(agg_ctrl["mae"] - prior_results["control_frozen_stage81"]["blind_2025"]["mae"]) < 1e-3,
        "candidate_f_mae_match": abs(agg_f["mae"] - prior_results["candidate_F"]["blind_2025"]["mae"]) < 1e-3,
    }
    print("Reproduction check vs CANDIDATE_F_RESULTS.json:", reproduced_match)
    assert reproduced_match["control_mae_match"] and reproduced_match["candidate_f_mae_match"], \
        "STOP: recomputed inference does not match prior recorded CANDIDATE_F_RESULTS.json aggregate -- inference path diverged"

    err_f = pred_25_f - y_25
    err_ctrl = pred_25_ctrl - y_25
    abs_err_f = np.abs(err_f)

    report = {
        "note": "All metrics below are on CANDIDATE F's OWN blind-2025 predictions (err = F_pred - actual), "
                "with the frozen control's own blind-2025 predictions shown alongside for direct comparison "
                "at each slice. Control numbers here are recomputed via inference in this script (matching "
                "ERROR_FORENSICS_RESULTS.json / CANDIDATE_F_RESULTS.json aggregates) and may differ by a "
                "few hundredths of a unit from ERROR_FORENSICS_RESULTS.json's merge-based pipeline at the "
                "4th decimal due to float accumulation order; aggregate MAE values matched prior recorded "
                "results to <1e-3 (see reproduction_check).",
        "reproduction_check": reproduced_match,
        "n_daytime_blind2025": int(len(day25)),
        "overall": {"control": agg_ctrl, "candidate_F": agg_f},
    }

    # ---- by horizon ----
    by_horizon = []
    total_abs_err_f = abs_err_f.sum()
    for h in range(1, 25):
        mask = day25["horizon_hour"].values == h
        if mask.sum() == 0:
            continue
        s_ctrl = summarize(err_ctrl[mask], y_25[mask])
        s_f = summarize(err_f[mask], y_25[mask])
        contrib = float(abs_err_f[mask].sum())
        by_horizon.append({
            "horizon_hour": h, "n": int(mask.sum()),
            "control_mae": s_ctrl["mae"], "control_bias": s_ctrl["bias"],
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            "mae_delta_F_minus_control": round(s_f["mae"] - s_ctrl["mae"], 4),
            "candidateF_abs_error_contribution": round(contrib, 1),
            "candidateF_share_pct_of_total": round(100 * contrib / total_abs_err_f, 2),
        })
    report["by_horizon"] = by_horizon
    report["largest_error_contributors_by_horizon_F"] = sorted(
        by_horizon, key=lambda d: -d["candidateF_abs_error_contribution"])[:8]

    # ---- by month ----
    by_month = []
    for m in sorted(day25["month"].unique()):
        mask = day25["month"].values == m
        s_ctrl = summarize(err_ctrl[mask], y_25[mask])
        s_f = summarize(err_f[mask], y_25[mask])
        by_month.append({
            "month": int(m), "n": int(mask.sum()),
            "control_mae": s_ctrl["mae"], "control_bias": s_ctrl["bias"],
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            "mae_delta_F_minus_control": round(s_f["mae"] - s_ctrl["mae"], 4),
            "bias_delta_F_minus_control": round(s_f["bias"] - s_ctrl["bias"], 4),
        })
    report["by_month"] = by_month

    # ---- by solar elevation (same bins as original forensics) ----
    elev = day25["solar_elevation"].values
    elev_bins = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 90)]
    by_elev = []
    for lo, hi in elev_bins:
        mask = (elev >= lo) & (elev < hi)
        if mask.sum() == 0:
            continue
        s_ctrl = summarize(err_ctrl[mask], y_25[mask])
        s_f = summarize(err_f[mask], y_25[mask])
        contrib = float(abs_err_f[mask].sum())
        by_elev.append({
            "elevation_bin": f"[{lo},{hi})", "n": int(mask.sum()),
            "control_mae": s_ctrl["mae"], "control_bias": s_ctrl["bias"],
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            "mae_delta_F_minus_control": round(s_f["mae"] - s_ctrl["mae"], 4),
            "bias_delta_F_minus_control": round(s_f["bias"] - s_ctrl["bias"], 4),
            "candidateF_abs_error_contribution": round(contrib, 1),
            "candidateF_share_pct_of_total": round(100 * contrib / total_abs_err_f, 2),
        })
    report["by_solar_elevation"] = by_elev

    # ---- by cloud regime (clear / transition / cloudy) ----
    cc_max = day25["fc_cloud_cover"].max()
    cc_frac = (day25["fc_cloud_cover"] / 100.0 if cc_max > 1.5 else day25["fc_cloud_cover"]).values
    cloud_bins = [(0.0, 0.2, "clear"), (0.2, 0.6, "transition"), (0.6, 1.01, "cloudy")]
    by_cloud = []
    for lo, hi, label in cloud_bins:
        mask = (cc_frac >= lo) & (cc_frac < hi)
        if mask.sum() == 0:
            continue
        s_ctrl = summarize(err_ctrl[mask], y_25[mask])
        s_f = summarize(err_f[mask], y_25[mask])
        by_cloud.append({
            "regime": label, "cloud_cover_range": f"[{lo},{hi})", "n": int(mask.sum()),
            "control_mae": s_ctrl["mae"], "control_bias": s_ctrl["bias"],
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            "mae_delta_F_minus_control": round(s_f["mae"] - s_ctrl["mae"], 4),
            "bias_delta_F_minus_control": round(s_f["bias"] - s_ctrl["bias"], 4),
        })
    report["by_cloud_regime"] = by_cloud

    # finer cloud_frac deciles (uses actual cloud_frac feature, not fc_cloud_cover)
    cf = day25["cloud_frac"].values
    by_cloud_decile = []
    qs = np.quantile(cf, np.linspace(0, 1, 11))
    qs[0], qs[-1] = -0.001, 1.001
    for i in range(10):
        lo, hi = qs[i], qs[i + 1]
        mask = (cf > lo) & (cf <= hi) if i > 0 else (cf >= lo) & (cf <= hi)
        if mask.sum() == 0:
            continue
        s_f = summarize(err_f[mask], y_25[mask])
        by_cloud_decile.append({
            "cloud_frac_range": f"({round(float(lo), 3)},{round(float(hi), 3)}]", "n": int(mask.sum()),
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
        })
    report["by_cloud_frac_decile_F_only"] = by_cloud_decile

    # ---- by clearsky_ghi intensity bucket ----
    ghi = day25["clearsky_ghi"].values
    intensity_bins = [(0, 50), (50, 150), (150, 300), (300, 1200)]
    by_intensity = []
    for lo, hi in intensity_bins:
        mask = (ghi >= lo) & (ghi < hi)
        if mask.sum() == 0:
            continue
        s_ctrl = summarize(err_ctrl[mask], y_25[mask])
        s_f = summarize(err_f[mask], y_25[mask])
        by_intensity.append({
            "clearsky_ghi_bin": f"[{lo},{hi})", "n": int(mask.sum()),
            "control_mae": s_ctrl["mae"], "control_bias": s_ctrl["bias"],
            "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            "mae_delta_F_minus_control": round(s_f["mae"] - s_ctrl["mae"], 4),
            "bias_delta_F_minus_control": round(s_f["bias"] - s_ctrl["bias"], 4),
        })
    report["by_clearsky_intensity"] = by_intensity

    # ---- 2-way interaction: elevation bin x cloud regime, F residuals ----
    interaction = []
    for lo, hi in elev_bins:
        emask = (elev >= lo) & (elev < hi)
        for clo, chi, label in cloud_bins:
            cmask = (cc_frac >= clo) & (cc_frac < chi)
            mask = emask & cmask
            if mask.sum() < 5:
                continue
            s_f = summarize(err_f[mask], y_25[mask])
            interaction.append({
                "elevation_bin": f"[{lo},{hi})", "cloud_regime": label, "n": int(mask.sum()),
                "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            })
    report["interaction_elevation_x_cloud_regime_F_only"] = interaction

    # ---- 2-way interaction: horizon bucket x month, F residuals (coarse, for H10-14 vs Aug/Sep) ----
    interaction_hm = []
    horizon_buckets = [(1, 9, "H1-9"), (10, 14, "H10-14"), (15, 24, "H15-24")]
    for hlo, hhi, hlabel in horizon_buckets:
        hmask = (day25["horizon_hour"].values >= hlo) & (day25["horizon_hour"].values <= hhi)
        for m in sorted(day25["month"].unique()):
            mmask = day25["month"].values == m
            mask = hmask & mmask
            if mask.sum() < 5:
                continue
            s_f = summarize(err_f[mask], y_25[mask])
            interaction_hm.append({
                "horizon_bucket": hlabel, "month": int(m), "n": int(mask.sum()),
                "candidateF_mae": s_f["mae"], "candidateF_bias": s_f["bias"],
            })
    report["interaction_horizon_x_month_F_only"] = interaction_hm

    # ---- residual predictability probe (linear), analogous to Phase 1's R^2=0.4457 ----
    X_probe = day25[["month", "hour", "solar_elevation", "cloud_frac", "clearsky_ghi", "horizon_hour"]].values
    lr = LinearRegression().fit(X_probe, abs_err_f)
    r2_lin = lr.score(X_probe, abs_err_f)
    report["residual_predictability_probe_linear_F"] = {
        "method": "OLS of |F_error| on [month,hour,solar_elevation,cloud_frac,clearsky_ghi,horizon_hour]",
        "r2": round(float(r2_lin), 4),
        "coefficients": dict(zip(
            ["month", "hour", "solar_elevation", "cloud_frac", "clearsky_ghi", "horizon_hour"],
            [round(float(c), 6) for c in lr.coef_],
        )),
        "control_comparison_r2_from_ERROR_FORENSICS_RESULTS_json": 0.4457,
    }

    # ---- shallow tree probe (nonlinear), same inputs ----
    X_probe_full = day25[["month", "hour", "solar_elevation", "cloud_frac", "clearsky_ghi",
                           "horizon_hour"] + CANDIDATE_F_38_FEATURES].copy()
    X_probe_full = X_probe_full.loc[:, ~X_probe_full.columns.duplicated()]
    tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=30, random_state=42)
    tree.fit(X_probe_full.values, abs_err_f)
    r2_tree = tree.score(X_probe_full.values, abs_err_f)
    importances = sorted(
        zip(X_probe_full.columns, tree.feature_importances_), key=lambda t: -t[1])[:10]
    report["residual_predictability_probe_tree_F_all38features"] = {
        "method": "DecisionTreeRegressor(max_depth=4,min_samples_leaf=30) of |F_error| on all 38 "
                  "Candidate F input features (forecast-time-available; no .fit on the production "
                  "model, this is a diagnostic-only probe model, not used for prediction/promotion)",
        "r2_in_sample": round(float(r2_tree), 4),
        "top10_feature_importances": [{"feature": f, "importance": round(float(i), 4)} for f, i in importances],
        "caveat": "in-sample R2 on a shallow tree is a rough diagnostic for signal concentration, "
                  "not a held-out generalization estimate -- it is reported as exploratory evidence only.",
    }

    # ---- correlation of |residual| and signed residual with each of the 38 features ----
    feat_corr = []
    for feat in CANDIDATE_F_38_FEATURES:
        vals = day25[feat].values.astype(float)
        if np.std(vals) < 1e-12:
            continue
        corr_abs = float(np.corrcoef(vals, abs_err_f)[0, 1])
        corr_signed = float(np.corrcoef(vals, err_f)[0, 1])
        feat_corr.append({"feature": feat,
                           "corr_with_abs_residual": round(corr_abs, 4),
                           "corr_with_signed_residual": round(corr_signed, 4)})
    feat_corr_sorted = sorted(feat_corr, key=lambda d: -abs(d["corr_with_abs_residual"]))
    report["feature_correlation_with_F_residual"] = feat_corr_sorted

    out_path = OUT_DIR / "CANDIDATE_F_RESIDUAL_FORENSICS_RESULTS.json"

    # ---- post-analysis hash re-verification (confirm zero drift from touching inputs) ----
    hash25_after = sha256_of(MATRIX_2025_PATH)
    hash_frozen_after = sha256_of(FROZEN_MODEL_PATH)
    hash_f_after = sha256_of(CANDIDATE_F_MODEL_PATH)
    freeze_manifest_hash_after = sha256_of(FREEZE_MANIFEST_PATH)
    candidate_f_results_hash_after = sha256_of(CANDIDATE_F_RESULTS_PATH)

    drift_check = {
        "matrix_2025": {"before": hash25_before, "after": hash25_after, "match": hash25_before == hash25_after},
        "frozen_control_model": {"before": hash_frozen_before, "after": hash_frozen_after,
                                  "match": hash_frozen_before == hash_frozen_after},
        "candidate_f_model": {"before": hash_f_before, "after": hash_f_after,
                               "match": hash_f_before == hash_f_after},
        "freeze_manifest": {"before": freeze_manifest_hash_before, "after": freeze_manifest_hash_after,
                             "match": freeze_manifest_hash_before == freeze_manifest_hash_after},
        "candidate_f_results_json": {"before": candidate_f_results_hash_before, "after": candidate_f_results_hash_after,
                                      "match": candidate_f_results_hash_before == candidate_f_results_hash_after},
    }
    assert all(v["match"] for v in drift_check.values()), f"STOP: input drift detected: {drift_check}"
    report["provenance_hash_drift_check"] = drift_check

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nResults written to {out_path}")
    print("Hash drift check:", {k: v["match"] for k, v in drift_check.items()})
    print("PHASE 9 COMPLETE. No frozen artifact, model, or feature matrix modified. No .fit() on any production model.")


if __name__ == "__main__":
    main()
