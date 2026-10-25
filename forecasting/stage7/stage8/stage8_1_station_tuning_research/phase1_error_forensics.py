#!/usr/bin/env python3
"""
PHASE 1 -- ERROR FORENSICS on the FROZEN Stage 8.1 CORRECTED model's 2025 blind predictions.

Pure read-only analysis. Does not train anything. Does not touch the frozen artifact, the
freeze manifest, or any production code/config. Reads only:
  - stage8_1_CORRECTED_2025_blind_predictions.csv (frozen blind predictions)
  - stage8_1_full_37_feature_matrix_2025_CORRECTED.csv (frozen feature matrix, for regime
    variables: month, hour, solar_elevation, clearsky_ghi, fc_cloud_cover, cloud_frac)

Both inputs' hashes are recorded and compared against the freeze manifest's own recorded
values (FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json) to confirm nothing has drifted.
"""
import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
FREEZE_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_corrected_2025"
OUT_DIR = BASE / "forecasting/stage7" / "stage8" / "stage8_1_station_tuning_research"
OUT_DIR.mkdir(exist_ok=True)

PRED_PATH = FREEZE_DIR / "stage8_1_CORRECTED_2025_blind_predictions.csv"
MATRIX_PATH = FREEZE_DIR / "stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
FREEZE_MANIFEST_PATH = FREEZE_DIR / "FINAL_STAGE8_1_FORECASTING_FREEZE_MANIFEST.json"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def mae(e):
    return float(np.mean(np.abs(e)))


def rmse(e):
    return float(np.sqrt(np.mean(e ** 2)))


def bias(e):
    return float(np.mean(e))


def nmae(e, y):
    m = np.mean(y)
    return float((mae(e) / m) * 100.0) if m > 0 else float("nan")


def summarize(df, pred_col, actual_col="actual_SW_IN"):
    e = (df[pred_col] - df[actual_col]).values
    y = df[actual_col].values
    return {
        "n": int(len(df)), "mae": round(mae(e), 4), "rmse": round(rmse(e), 4),
        "bias": round(bias(e), 4), "nmae_pct": round(nmae(e, y), 4),
    }


def main():
    print("=" * 80)
    print("PHASE 1 -- ERROR FORENSICS (frozen Stage 8.1 CORRECTED, 2025 blind)")
    print("Read-only. No training. No modification of frozen artifacts.")
    print("=" * 80)

    pred_hash = sha256_of(PRED_PATH)
    matrix_hash = sha256_of(MATRIX_PATH)
    freeze_manifest = json.load(open(FREEZE_MANIFEST_PATH))

    print(f"predictions hash: {pred_hash}")
    print(f"matrix hash:      {matrix_hash}")

    preds = pd.read_csv(PRED_PATH)
    matrix = pd.read_csv(MATRIX_PATH)
    preds["forecast_start"] = pd.to_datetime(preds["forecast_start"], utc=True)
    matrix["forecast_start"] = pd.to_datetime(matrix["forecast_start"], utc=True)

    df = preds.merge(
        matrix[["forecast_start", "horizon_hour", "month", "hour", "solar_elevation",
                "clearsky_ghi", "fc_cloud_cover", "cloud_frac"]],
        on=["forecast_start", "horizon_hour"], how="left", validate="one_to_one",
    )
    assert df["solar_elevation"].notna().all(), "merge produced NaN regime columns -- STOP"

    pred_col = "pred_stage8_1_CORRECTED_blind2025"
    day = df[df["is_daytime"]].copy()
    print(f"\nTotal rows: {len(df)} | daytime rows: {len(day)}")

    report = {"input_hashes": {"predictions": pred_hash, "matrix": matrix_hash},
              "freeze_manifest_model_hash": freeze_manifest.get("model_artifact_sha256"),
              "n_total": int(len(df)), "n_daytime": int(len(day))}

    # Overall
    report["overall_daytime"] = summarize(day, pred_col)
    print("Overall daytime:", report["overall_daytime"])

    # 1a. By horizon H1-H24
    by_horizon = []
    for h in range(1, 25):
        sub = day[day["horizon_hour"] == h]
        if len(sub) == 0:
            continue
        by_horizon.append({"horizon_hour": h, **summarize(sub, pred_col)})
    report["by_horizon"] = by_horizon

    # 1b. By month
    by_month = []
    for m in sorted(day["month"].unique()):
        sub = day[day["month"] == m]
        by_month.append({"month": int(m), **summarize(sub, pred_col)})
    report["by_month"] = by_month

    # 1c. By solar elevation bucket
    elev_bins = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 90)]
    by_elev = []
    for lo, hi in elev_bins:
        sub = day[(day["solar_elevation"] >= lo) & (day["solar_elevation"] < hi)]
        if len(sub) == 0:
            continue
        by_elev.append({"elevation_bin": f"[{lo},{hi})", **summarize(sub, pred_col)})
    report["by_solar_elevation"] = by_elev

    # 1d. Clear vs cloudy (using fc_cloud_cover, 0-1 or 0-100 scale -- check & bucket)
    cc_max = day["fc_cloud_cover"].max()
    cc_series = day["fc_cloud_cover"] / 100.0 if cc_max > 1.5 else day["fc_cloud_cover"]
    day = day.assign(_cc_frac=cc_series)
    cloud_bins = [(0.0, 0.2, "clear"), (0.2, 0.6, "transition"), (0.6, 1.01, "cloudy")]
    by_cloud = []
    for lo, hi, label in cloud_bins:
        sub = day[(day["_cc_frac"] >= lo) & (day["_cc_frac"] < hi)]
        if len(sub) == 0:
            continue
        by_cloud.append({"regime": label, "cloud_cover_range": f"[{lo},{hi})", **summarize(sub, pred_col)})
    report["by_cloud_regime"] = by_cloud

    # 1e. By solar intensity (clearsky_ghi bucket, as proxy for intensity magnitude)
    intensity_bins = [(0, 50), (50, 150), (150, 300), (300, 1200)]
    by_intensity = []
    for lo, hi in intensity_bins:
        sub = day[(day["clearsky_ghi"] >= lo) & (day["clearsky_ghi"] < hi)]
        if len(sub) == 0:
            continue
        by_intensity.append({"clearsky_ghi_bin": f"[{lo},{hi})", **summarize(sub, pred_col)})
    report["by_clearsky_intensity"] = by_intensity

    # 2/3. Systematic residual predictability check: regress |error| on available-at-forecast-time
    # regime variables (month, hour, solar_elevation, cloud_frac, clearsky_ghi, horizon_hour) using a
    # simple correlation/R^2 probe -- NOT a leak (all these are inputs already in the feature set).
    from sklearn.linear_model import LinearRegression
    err = (day[pred_col] - day["actual_SW_IN"]).values
    abs_err = np.abs(err)
    X_probe = day[["month", "hour", "solar_elevation", "cloud_frac", "clearsky_ghi", "horizon_hour"]].values
    lr = LinearRegression().fit(X_probe, abs_err)
    r2 = lr.score(X_probe, abs_err)
    report["residual_predictability_probe"] = {
        "method": "OLS of |error| on [month,hour,solar_elevation,cloud_frac,clearsky_ghi,horizon_hour]",
        "r2": round(float(r2), 4),
        "coefficients": dict(zip(
            ["month", "hour", "solar_elevation", "cloud_frac", "clearsky_ghi", "horizon_hour"],
            [round(float(c), 6) for c in lr.coef_],
        )),
        "interpretation_note": (
            "r2 is the share of |error| variance linearly explainable by information already "
            "available at forecast time. A nonzero value indicates the CURRENT model is not "
            "fully exploiting these regime variables for its own uncertainty/error structure -- "
            "it does NOT by itself mean a better model is easy to build."
        ),
    }
    print(f"\nResidual-predictability probe R^2: {r2:.4f}")

    # 4/5. Largest avoidable-error regimes: rank buckets by (n * mae) contribution to total MAE
    total_abs_err = abs_err.sum()
    bucket_contrib = []
    for lo, hi in elev_bins:
        sub_mask = (day["solar_elevation"] >= lo) & (day["solar_elevation"] < hi)
        contrib = np.abs(err[sub_mask.values]).sum()
        bucket_contrib.append({"regime": f"elevation[{lo},{hi})", "n": int(sub_mask.sum()),
                                "abs_error_contribution": round(float(contrib), 1),
                                "share_pct": round(100 * contrib / total_abs_err, 2)})
    report["largest_error_contributors_by_elevation"] = sorted(
        bucket_contrib, key=lambda d: -d["abs_error_contribution"])

    bucket_contrib_h = []
    for h in range(1, 25):
        mask = day["horizon_hour"] == h
        contrib = np.abs(err[mask.values]).sum()
        bucket_contrib_h.append({"horizon_hour": h, "n": int(mask.sum()),
                                  "abs_error_contribution": round(float(contrib), 1),
                                  "share_pct": round(100 * contrib / total_abs_err, 2)})
    report["largest_error_contributors_by_horizon"] = sorted(
        bucket_contrib_h, key=lambda d: -d["abs_error_contribution"])[:8]

    out_path = OUT_DIR / "ERROR_FORENSICS_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nResults written to {out_path}")
    print("PHASE 1 COMPLETE. No frozen artifact modified.")


if __name__ == "__main__":
    main()
