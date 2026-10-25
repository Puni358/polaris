#!/usr/bin/env python3
"""
PHASE 2 -- STATION-SPECIFIC LEARNING candidates C, D, E.

Trains EVEN-only (2024), validates/tunes on ODD-only (2024, held out from training), and
performs a FINAL genuinely-blind check on 2025 (never touched by training or tuning for any
candidate here) -- exactly mirroring the frozen model's own methodology
(train_corrected_stage8_1_model.py / run_2025_blind_evaluation.py), reusing the identical
37-feature contract, target definition (residual-on-Stage4), and base hyperparameters except
where a candidate explicitly varies one axis.

Candidate B ("expanded same-station historical data") is NOT implemented here -- see
ERROR_FORENSICS_REPORT.md / CANDIDATE_COMPARISON_REPORT.md for why: the only data available
in this repository beyond 2024-EVEN is 2024-ODD (the held-out validation set) and 2025 (the
blind test set); using either for additional training would contaminate a set this
investigation is required to keep blind for every candidate, including this one. No
substitute/workaround was invented.

New files/models written to THIS directory only. The frozen artifact
(stage8_1_CORRECTED_candidate_37feature_model.joblib), its manifest, and all 2024/2025
feature matrices are read-only inputs here and are never modified.
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


def bootstrap_mae_diff_ci(origins_series, actual, pred_candidate, pred_control, n_boot=2000, seed=42):
    """Paired bootstrap over ORIGINS (not rows, to respect the 24-row-per-origin
    autocorrelation structure) of MAE(candidate) - MAE(control). Returns (mean_diff, lo95, hi95).
    New, read-only analysis code; does not affect any trained model."""
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
            "ci95_hi": round(float(np.percentile(diffs, 97.5)), 4),
            "n_boot": int(len(diffs))}


def per_horizon_metrics(df, actual_col, pred_col):
    out = []
    for h in sorted(df["horizon_hour"].unique()):
        sub = df[df["horizon_hour"] == h]
        if len(sub) == 0:
            continue
        out.append({"horizon_hour": int(h), **metrics(sub[actual_col].values, sub[pred_col].values)})
    return out


def load_split(path):
    df = pd.read_csv(path)
    df["forecast_start"] = pd.to_datetime(df["forecast_start"], utc=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    origins = sorted(df["forecast_start"].unique())
    even = [o for i, o in enumerate(origins) if i % 2 == 0]
    odd = [o for i, o in enumerate(origins) if i % 2 == 1]
    return df, df[df["forecast_start"].isin(even)].copy(), df[df["forecast_start"].isin(odd)].copy()


def main():
    print("=" * 80)
    print("PHASE 2 -- candidates C (horizon-specific), D (residual correction), E (HP search)")
    print("Train: 2024 EVEN. Validate/tune: 2024 ODD. Blind: 2025 (never touched).")
    print("=" * 80)

    hash_2024 = sha256_of(MATRIX_2024_PATH)
    hash_2025 = sha256_of(MATRIX_2025_PATH)
    print(f"2024 matrix hash: {hash_2024}")
    print(f"2025 matrix hash: {hash_2025}")

    df24, even24, odd24 = load_split(MATRIX_2024_PATH)
    df25 = pd.read_csv(MATRIX_2025_PATH)
    df25["forecast_start"] = pd.to_datetime(df25["forecast_start"], utc=True)
    print(f"2024: {len(sorted(df24['forecast_start'].unique()))} origins "
          f"({len(sorted(even24['forecast_start'].unique()))} EVEN / {len(sorted(odd24['forecast_start'].unique()))} ODD)")
    print(f"2025: {len(sorted(df25['forecast_start'].unique()))} origins (blind, untouched)\n")

    even_day = even24[even24["is_daytime"]].copy()
    odd_day = odd24[odd24["is_daytime"]].copy()
    day25 = df25[df25["is_daytime"]].copy()

    X_tr_full = even_day[CANDIDATE_37_FEATURES].values
    y_tr = even_day["actual_SW_IN"].values
    st4_tr = even_day["pred_stage4_fold"].values
    res_tr = y_tr - st4_tr

    X_odd_full = odd_day[CANDIDATE_37_FEATURES].values
    y_odd = odd_day["actual_SW_IN"].values
    st4_odd = odd_day["pred_stage4_fold"].values
    night_causal_odd = odd_day["is_night_causal"].values

    X_25_full = day25[CANDIDATE_37_FEATURES].values
    y_25 = day25["actual_SW_IN"].values
    st4_25 = day25["pred_stage4_fold"].values
    night_causal_25 = day25["is_night_causal"].values

    def apply_night_zero(pred, night_causal_mask):
        """Exact same overlay train_corrected_stage8_1_model.py / run_2025_blind_evaluation.py
        apply: within the is_daytime-filtered subset, force any row that is still causally
        night (twilight-glow edge case) to 0, to match the frozen model's own documented
        methodology exactly, for apples-to-apples comparison."""
        out = pred.copy()
        out[night_causal_mask] = 0.0
        return out

    results = {"input_hashes": {"matrix_2024": hash_2024, "matrix_2025": hash_2025},
               "hyperparameters_frozen": FROZEN_HP}

    # ---- Candidate A (frozen control) -- reproduce from already-fitted frozen artifact for
    # a byte-consistent reference point in THIS report (reusing the frozen artifact, not refitting). ----
    frozen_model_path = FREEZE_DIR / "model_artifact" / "stage8_1_CORRECTED_candidate_37feature_model.joblib"
    frozen_model = joblib.load(frozen_model_path)
    pred_res_odd_A = frozen_model.predict(X_odd_full)
    pred_odd_A = apply_night_zero(np.maximum(0.0, st4_odd + pred_res_odd_A), night_causal_odd)
    pred_res_25_A = frozen_model.predict(X_25_full)
    pred_25_A = apply_night_zero(np.maximum(0.0, st4_25 + pred_res_25_A), night_causal_25)
    results["A_frozen_control"] = {
        "odd_2024": metrics(y_odd, pred_odd_A),
        "blind_2025": metrics(y_25, pred_25_A),
        "blind_2025_by_horizon": per_horizon_metrics(
            day25.assign(_pred=pred_25_A), "actual_SW_IN", "_pred"),
    }
    print("A (frozen control)  ODD:", results["A_frozen_control"]["odd_2024"],
          " BLIND25:", results["A_frozen_control"]["blind_2025"])

    # ---- Candidate C: horizon-specific models (4 buckets) ----
    buckets = [(1, 6), (7, 12), (13, 18), (19, 24)]
    pred_odd_C = np.zeros(len(odd_day))
    pred_25_C = np.zeros(len(day25))
    c_bucket_info = []
    for lo, hi in buckets:
        tr_mask = (even_day["horizon_hour"] >= lo) & (even_day["horizon_hour"] <= hi)
        odd_mask = (odd_day["horizon_hour"] >= lo) & (odd_day["horizon_hour"] <= hi)
        d25_mask = (day25["horizon_hour"] >= lo) & (day25["horizon_hour"] <= hi)
        if tr_mask.sum() < 30:
            c_bucket_info.append({"bucket": f"H{lo}-{hi}", "n_train": int(tr_mask.sum()), "skipped": True})
            continue
        m = HistGradientBoostingRegressor(**FROZEN_HP)
        m.fit(X_tr_full[tr_mask.values], res_tr[tr_mask.values])
        pred_odd_C[odd_mask.values] = np.maximum(
            0.0, st4_odd[odd_mask.values] + m.predict(X_odd_full[odd_mask.values]))
        pred_25_C[d25_mask.values] = np.maximum(
            0.0, st4_25[d25_mask.values] + m.predict(X_25_full[d25_mask.values]))
        c_bucket_info.append({"bucket": f"H{lo}-{hi}", "n_train": int(tr_mask.sum()), "skipped": False})
        joblib.dump(m, ARTIFACT_DIR / f"candidateC_H{lo}_{hi}.joblib")
    pred_odd_C = apply_night_zero(pred_odd_C, night_causal_odd)
    pred_25_C = apply_night_zero(pred_25_C, night_causal_25)
    results["C_horizon_specific"] = {
        "bucket_info": c_bucket_info,
        "odd_2024": metrics(y_odd, pred_odd_C),
        "blind_2025": metrics(y_25, pred_25_C),
        "blind_2025_by_horizon": per_horizon_metrics(
            day25.assign(_pred=pred_25_C), "actual_SW_IN", "_pred"),
    }
    print("C (horizon-specific) ODD:", results["C_horizon_specific"]["odd_2024"],
          " BLIND25:", results["C_horizon_specific"]["blind_2025"])

    # ---- Candidate D: residual-correction second stage (out-of-fold base predictions on EVEN) ----
    rng = np.random.RandomState(42)
    even_origins_sorted = sorted(even_day["forecast_start"].unique())
    half = len(even_origins_sorted) // 2
    fold_a_origins = set(even_origins_sorted[:half])
    fold_a_mask = even_day["forecast_start"].isin(fold_a_origins).values
    fold_b_mask = ~fold_a_mask

    oof_base_pred_res = np.zeros(len(even_day))
    for fit_mask, pred_mask in [(fold_b_mask, fold_a_mask), (fold_a_mask, fold_b_mask)]:
        m_fold = HistGradientBoostingRegressor(**FROZEN_HP)
        m_fold.fit(X_tr_full[fit_mask], res_tr[fit_mask])
        oof_base_pred_res[pred_mask] = m_fold.predict(X_tr_full[pred_mask])
    oof_base_pred_sw = np.maximum(0.0, st4_tr + oof_base_pred_res)
    second_stage_target = y_tr - oof_base_pred_sw  # out-of-fold residual of the BASE model's own output

    base_model_full = HistGradientBoostingRegressor(**FROZEN_HP)
    base_model_full.fit(X_tr_full, res_tr)
    second_stage_model = HistGradientBoostingRegressor(**FROZEN_HP)
    second_stage_model.fit(X_tr_full, second_stage_target)

    base_pred_res_odd = base_model_full.predict(X_odd_full)
    base_pred_sw_odd = np.maximum(0.0, st4_odd + base_pred_res_odd)
    pred_odd_D = apply_night_zero(
        np.maximum(0.0, base_pred_sw_odd + second_stage_model.predict(X_odd_full)), night_causal_odd)

    base_pred_res_25 = base_model_full.predict(X_25_full)
    base_pred_sw_25 = np.maximum(0.0, st4_25 + base_pred_res_25)
    pred_25_D = apply_night_zero(
        np.maximum(0.0, base_pred_sw_25 + second_stage_model.predict(X_25_full)), night_causal_25)

    results["D_residual_correction"] = {
        "method": "2-fold out-of-fold base predictions on EVEN -> second HGB stage predicts "
                   "(actual - oof_base_pred); final = base_full_pred + second_stage_pred",
        "odd_2024": metrics(y_odd, pred_odd_D),
        "blind_2025": metrics(y_25, pred_25_D),
        "blind_2025_by_horizon": per_horizon_metrics(
            day25.assign(_pred=pred_25_D), "actual_SW_IN", "_pred"),
    }
    joblib.dump(base_model_full, ARTIFACT_DIR / "candidateD_base.joblib")
    joblib.dump(second_stage_model, ARTIFACT_DIR / "candidateD_secondstage.joblib")
    print("D (residual-correction) ODD:", results["D_residual_correction"]["odd_2024"],
          " BLIND25:", results["D_residual_correction"]["blind_2025"])

    # ---- Candidate E: hyperparameter search (select by 2024 ODD MAE, report 2025 blind) ----
    grid = []
    for max_depth in [3, 4, 5, 6]:
        for min_samples_leaf in [15, 30, 50, 100]:
            for l2 in [1.0, 10.0, 30.0]:
                for lr in [0.05, 0.1, 0.2]:
                    grid.append({"max_depth": max_depth, "min_samples_leaf": min_samples_leaf,
                                  "l2_regularization": l2, "learning_rate": lr})
    print(f"\nCandidate E: hyperparameter grid size = {len(grid)} (selecting by 2024 ODD MAE)")

    best = None
    e_grid_results = []
    for hp in grid:
        m = HistGradientBoostingRegressor(loss="absolute_error", random_state=42, **hp)
        m.fit(X_tr_full, res_tr)
        pred_res_odd = m.predict(X_odd_full)
        pred_odd = apply_night_zero(np.maximum(0.0, st4_odd + pred_res_odd), night_causal_odd)
        odd_metrics = metrics(y_odd, pred_odd)
        e_grid_results.append({"hp": hp, "odd_mae": odd_metrics["mae"]})
        if best is None or odd_metrics["mae"] < best["odd_mae"]:
            best = {"hp": hp, "odd_mae": odd_metrics["mae"], "model": m}

    best_model = best["model"]
    pred_res_odd_E = best_model.predict(X_odd_full)
    pred_odd_E = apply_night_zero(np.maximum(0.0, st4_odd + pred_res_odd_E), night_causal_odd)
    pred_res_25_E = best_model.predict(X_25_full)
    pred_25_E = apply_night_zero(np.maximum(0.0, st4_25 + pred_res_25_E), night_causal_25)

    results["E_hyperparameter_search"] = {
        "grid_size": len(grid),
        "best_hyperparameters": best["hp"],
        "selection_metric": "2024 ODD MAE (validation, not blind)",
        "odd_2024": metrics(y_odd, pred_odd_E),
        "blind_2025": metrics(y_25, pred_25_E),
        "blind_2025_by_horizon": per_horizon_metrics(
            day25.assign(_pred=pred_25_E), "actual_SW_IN", "_pred"),
        "grid_results_sorted_by_odd_mae": sorted(e_grid_results, key=lambda d: d["odd_mae"])[:10],
    }
    joblib.dump(best_model, ARTIFACT_DIR / "candidateE_best.joblib")
    print("E (best HP):", best["hp"])
    print("E ODD:", results["E_hyperparameter_search"]["odd_2024"],
          " BLIND25:", results["E_hyperparameter_search"]["blind_2025"])

    # ---- Bootstrap CIs (over origins) for each candidate's blind-2025 MAE delta vs. control A ----
    origins_25 = day25["forecast_start"]
    results["bootstrap_mae_diff_vs_control_blind2025"] = {
        "C_horizon_specific": bootstrap_mae_diff_ci(origins_25, y_25, pred_25_C, pred_25_A),
        "D_residual_correction": bootstrap_mae_diff_ci(origins_25, y_25, pred_25_D, pred_25_A),
        "E_hyperparameter_search": bootstrap_mae_diff_ci(origins_25, y_25, pred_25_E, pred_25_A),
    }
    print("\nBootstrap MAE diff vs control (blind 2025, 2000 resamples over origins):")
    for k, v in results["bootstrap_mae_diff_vs_control_blind2025"].items():
        print(f"  {k}: {v}")

    out_path = OUT_DIR / "CANDIDATE_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")
    print("PHASE 2 COMPLETE. Frozen artifact and matrices untouched (read-only inputs).")


if __name__ == "__main__":
    main()
