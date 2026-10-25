#!/usr/bin/env python3
"""
POLARIS Stage 4.1 — Cloud-Regime-Conditioned Amplitude Correction
=================================================================

ONE controlled experiment. No test-set model selection.

Method: Per-cloud-regime isotonic regression
    ensemble_prediction → corrected_prediction
    fitted on TRAINING daytime data only.

Cloud regimes (from NWP fc_cloud_cover forecast):
    Clear:     0–10%
    Few:       10–30%
    Scattered: 30–60%
    Broken:    60–80%
    Overcast:  80–100%

Locked baseline: Stage 4 test daytime nMAE = 33.70%
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json, warnings
warnings.filterwarnings("ignore")

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT = BASE / "forecasting/stage4" / "stage4_1_cloud_regime_correction"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. LOAD DATA
# ============================================================
print("=" * 70)
print("STAGE 4.1 — LOADING DATA")
print("=" * 70)

pred = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
pred["timestamp"] = pd.to_datetime(pred["timestamp"])
pred["forecast_start"] = pd.to_datetime(pred["forecast_start"])
print(f"Predictions: {len(pred)} rows, {pred['forecast_start'].nunique()} origins")

cs = pd.read_csv(BASE / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])

nwp = pd.read_csv(BASE / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv")
nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])

# Merge clearsky
df = pred.merge(cs[["TIMESTAMP", "clearsky_ghi", "solar_elevation"]],
                left_on="timestamp", right_on="TIMESTAMP", how="left")
df.drop(columns=["TIMESTAMP"], inplace=True)

# Merge NWP cloud cover
df = df.merge(nwp[["forecast_start", "horizon_hour", "fc_cloud_cover"]],
              on=["forecast_start", "horizon_hour"], how="left")

# Derived
df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
df["is_daytime"] = df["actual_SW_IN"] > 0
df["month"] = df["timestamp"].dt.month
season_map = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
              6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
df["season"] = df["month"].map(season_map)

# Cloud regime classification (using NWP forecast, NOT actual observations)
def cloud_regime(c):
    if pd.isna(c): return "Missing"
    elif c <= 10: return "Clear (0-10%)"
    elif c <= 30: return "Few (10-30%)"
    elif c <= 60: return "Scattered (30-60%)"
    elif c <= 80: return "Broken (60-80%)"
    else: return "Overcast (80-100%)"
df["cloud_regime"] = df["fc_cloud_cover"].apply(cloud_regime)

# Stage 4 residuals
df["s4_residual"] = df["pred_ensemble"] - df["actual_SW_IN"]
df["s4_abs_residual"] = df["s4_residual"].abs()

print(f"Dataset: {len(df)} rows, cloud regime NaN: {df['cloud_regime'].isna().sum()}")
print(f"Cloud regimes: {df['cloud_regime'].value_counts().to_dict()}")

# ============================================================
# 2. TRAIN / TEST SPLIT (locked — same as Stage 4)
# ============================================================
print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT (locked interleaved holdout)")
print("=" * 70)

origins = sorted(df["forecast_start"].unique())
even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
odd_origins = [o for i, o in enumerate(origins) if i % 2 == 1]

train_mask = df["forecast_start"].isin(even_origins)
test_mask = df["forecast_start"].isin(odd_origins)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

train_day = df_train[df_train["is_daytime"]].copy()
test_day = df_test[df_test["is_daytime"]].copy()

print(f"Train: {len(df_train)} total, {len(train_day)} daytime")
print(f"Test:  {len(df_test)} total, {len(test_day)} daytime")

# ============================================================
# 3. VERIFY STAGE 4 BASELINE (test set)
# ============================================================
print("\n" + "=" * 70)
print("STAGE 4 BASELINE VERIFICATION (test set)")
print("=" * 70)

def compute_metrics(actual, predicted, label=""):
    residual = predicted - actual
    abs_res = np.abs(residual)
    is_day = actual > 0
    
    overall_mae = abs_res.mean()
    overall_rmse = np.sqrt((residual**2).mean())
    
    day_mask = is_day
    if day_mask.sum() > 0:
        day_mae = abs_res[day_mask].mean()
        day_rmse = np.sqrt((residual[day_mask]**2).mean())
        day_mean = actual[day_mask].mean()
        day_nmae = day_mae / day_mean * 100
        day_nrmse = day_rmse / day_mean * 100
        day_bias = residual[day_mask].mean()
    else:
        day_mae = day_rmse = day_nmae = day_nrmse = day_bias = np.nan
        day_mean = 0
    
    night_mask = ~is_day
    night_mae = abs_res[night_mask].mean() if night_mask.sum() > 0 else np.nan
    
    return {
        "label": label,
        "overall_mae": overall_mae, "overall_rmse": overall_rmse,
        "day_mae": day_mae, "day_rmse": day_rmse,
        "day_nmae": day_nmae, "day_nrmse": day_nrmse,
        "day_bias": day_bias, "day_mean_actual": day_mean,
        "night_mae": night_mae,
        "n_total": len(actual), "n_day": int(day_mask.sum()), "n_night": int(night_mask.sum())
    }

s4_test = compute_metrics(df_test["actual_SW_IN"].values,
                           df_test["pred_ensemble"].values, "Stage 4 (test)")
print(f"Stage 4 test: MAE={s4_test['overall_mae']:.4f}, "
      f"Day MAE={s4_test['day_mae']:.4f}, Day nMAE={s4_test['day_nmae']:.2f}%, "
      f"Day RMSE={s4_test['day_rmse']:.4f}")

# ============================================================
# 4. FIT ISOTONIC REGRESSION PER CLOUD REGIME (TRAIN ONLY)
# ============================================================
print("\n" + "=" * 70)
print("FITTING ISOTONIC REGRESSION PER CLOUD REGIME (TRAIN DAYTIME ONLY)")
print("=" * 70)
print("Method: Pool-Adjacent-Violators (PAV) isotonic regression")
print("Input: ensemble prediction → Output: corrected prediction")
print("Constraint: monotonically non-decreasing")

def isotonic_fit_pav(x, y):
    """Fit isotonic regression using Pool Adjacent Violators algorithm.
    Returns sorted x-knots and corresponding y-knots."""
    order = np.argsort(x)
    x_sorted = x[order].astype(float)
    y_sorted = y[order].astype(float)
    
    n = len(y_sorted)
    result = y_sorted.copy()
    weight = np.ones(n, dtype=float)
    
    # Pool Adjacent Violators
    i = 0
    while i < n - 1:
        if result[i] > result[i + 1]:
            # Find the block to pool
            j = i + 1
            while j < n - 1 and result[j] > result[j + 1]:
                j += 1
            # Pool from i to j: weighted average
            total_w = weight[i:j+1].sum()
            weighted_mean = (result[i:j+1] * weight[i:j+1]).sum() / total_w
            result[i:j+1] = weighted_mean
            weight[i:j+1] = total_w / (j - i + 1)
            # Check backwards
            while i > 0 and result[i-1] > result[i]:
                i -= 1
                j_check = i
                while j_check < n - 1 and result[j_check] >= result[j_check + 1]:
                    j_check += 1
                total_w = weight[i:j_check+1].sum()
                weighted_mean = (result[i:j_check+1] * weight[i:j_check+1]).sum() / total_w
                result[i:j_check+1] = weighted_mean
                weight[i:j_check+1] = total_w / (j_check - i + 1)
                j = j_check
            i = j + 1
        else:
            i += 1
    
    return x_sorted, result

def isotonic_predict(x_new, x_knots, y_knots):
    """Predict using fitted isotonic regression (linear interpolation)."""
    return np.interp(x_new, x_knots, y_knots)

regime_order = ["Clear (0-10%)", "Few (10-30%)", "Scattered (30-60%)",
                "Broken (60-80%)", "Overcast (80-100%)"]

calibration_params = {}

print(f"\n{'Regime':22s} {'N_train':>8s} {'Train MAE':>10s} {'Train MAE→':>10s} {'Slope':>8s} {'Intercept':>10s}")
print("-" * 75)

for regime in regime_order:
    tr_regime = train_day[train_day["cloud_regime"] == regime]
    
    if len(tr_regime) < 10:
        print(f"  {regime:22s}: INSUFFICIENT DATA (n={len(tr_regime)}), using identity")
        calibration_params[regime] = {"method": "identity", "n_train": len(tr_regime)}
        continue
    
    x_train = tr_regime["pred_ensemble"].values
    y_train = tr_regime["actual_SW_IN"].values
    
    # Fit isotonic regression
    x_knots, y_knots = isotonic_fit_pav(x_train, y_train)
    
    # Training performance
    train_pred_uncorr = tr_regime["pred_ensemble"].values
    train_pred_corr = isotonic_predict(train_pred_uncorr, x_knots, y_knots)
    train_pred_corr = np.maximum(train_pred_corr, 0)  # non-negativity
    
    train_mae_before = np.abs(train_pred_uncorr - y_train).mean()
    train_mae_after = np.abs(train_pred_corr - y_train).mean()
    
    # Also compute equivalent affine approximation for interpretability
    slope, intercept, r, p, se = stats.linregress(x_train, y_train)
    
    # Store knots (decimated for storage efficiency)
    # Keep unique knots only
    unique_mask = np.concatenate([[True], np.diff(y_knots) != 0])
    x_store = x_knots[unique_mask]
    y_store = y_knots[unique_mask]
    
    calibration_params[regime] = {
        "method": "isotonic",
        "n_train": len(tr_regime),
        "x_knots": x_store.tolist(),
        "y_knots": y_store.tolist(),
        "n_knots": len(x_store),
        "train_mae_before": float(train_mae_before),
        "train_mae_after": float(train_mae_after),
        "linear_slope": float(slope),
        "linear_intercept": float(intercept),
        "linear_r": float(r),
    }
    
    print(f"  {regime:22s} {len(tr_regime):8d} {train_mae_before:10.2f} {train_mae_after:10.2f} "
          f"{slope:8.4f} {intercept:10.2f}")

# ============================================================
# 5. INSPECT CALIBRATION BEHAVIOR (TRAINING DATA ONLY)
# ============================================================
print("\n" + "=" * 70)
print("CALIBRATION BEHAVIOR INSPECTION (TRAINING DATA)")
print("=" * 70)

for regime in regime_order:
    params = calibration_params[regime]
    if params["method"] == "identity":
        print(f"\n  {regime}: identity (no calibration)")
        continue
    
    x_knots = np.array(params["x_knots"])
    y_knots = np.array(params["y_knots"])
    
    # Check at representative prediction values
    test_points = [0, 50, 100, 200, 300, 400, 500, 600]
    print(f"\n  {regime} (n_knots={params['n_knots']}, slope≈{params['linear_slope']:.4f}, "
          f"intercept≈{params['linear_intercept']:.2f}):")
    print(f"    {'Input':>8s} → {'Output':>8s}  {'Ratio':>6s}")
    for tp in test_points:
        if tp > x_knots.max() + 50:
            continue
        out = max(float(np.interp(tp, x_knots, y_knots)), 0)
        ratio = out / tp if tp > 0 else 0
        flag = " *** AMPLIFICATION" if ratio > 2.0 and tp > 10 else ""
        print(f"    {tp:8.1f} → {out:8.2f}  {ratio:6.3f}{flag}")
    
    # Check for extreme amplification in training range
    pred_range = np.linspace(max(x_knots.min(), 0), x_knots.max(), 100)
    cal_range = np.maximum(np.interp(pred_range, x_knots, y_knots), 0)
    max_ratio = np.max(cal_range / np.maximum(pred_range, 1))
    print(f"    Max calibration ratio in training range: {max_ratio:.4f}")

# ============================================================
# 6. APPLY CALIBRATION TO ALL DATA
# ============================================================
print("\n" + "=" * 70)
print("APPLYING CALIBRATION")
print("=" * 70)

df["pred_corrected"] = df["pred_ensemble"].copy()

for regime in regime_order:
    params = calibration_params[regime]
    regime_mask = df["cloud_regime"] == regime
    
    if params["method"] == "identity":
        continue  # predictions unchanged
    
    x_knots = np.array(params["x_knots"])
    y_knots = np.array(params["y_knots"])
    
    ensemble_vals = df.loc[regime_mask, "pred_ensemble"].values
    corrected_vals = isotonic_predict(ensemble_vals, x_knots, y_knots)
    corrected_vals = np.maximum(corrected_vals, 0)  # non-negativity
    
    df.loc[regime_mask, "pred_corrected"] = corrected_vals
    
    n_regime = regime_mask.sum()
    n_changed = (np.abs(corrected_vals - ensemble_vals) > 0.01).sum()
    print(f"  {regime:22s}: {n_regime:5d} rows, {n_changed:5d} changed")

# Recompute test/train subsets
df_train = df[train_mask].copy()
df_test = df[test_mask].copy()
train_day = df_train[df_train["is_daytime"]].copy()
test_day = df_test[df_test["is_daytime"]].copy()

# Corrected residuals
df["corr_residual"] = df["pred_corrected"] - df["actual_SW_IN"]
df["corr_abs_residual"] = df["corr_residual"].abs()
df_test = df[test_mask].copy()
test_day = df_test[df_test["is_daytime"]].copy()

# ============================================================
# 7. CHECK FOR PATHOLOGICAL PREDICTIONS
# ============================================================
print("\n" + "=" * 70)
print("PATHOLOGICAL PREDICTION CHECK")
print("=" * 70)

# Negative predictions
n_neg = (df["pred_corrected"] < 0).sum()
print(f"Negative predictions: {n_neg}")

# Predictions exceeding 1.5x clearsky (flag, don't clip)
df["ratio_to_clearsky"] = np.where(df["clearsky_ghi"] > 10,
                                    df["pred_corrected"] / df["clearsky_ghi"], np.nan)
n_exceed_1_5 = (df["ratio_to_clearsky"] > 1.5).sum()
n_exceed_2_0 = (df["ratio_to_clearsky"] > 2.0).sum()
print(f"Predictions > 1.5x clearsky GHI: {n_exceed_1_5}")
print(f"Predictions > 2.0x clearsky GHI: {n_exceed_2_0}")

# Extreme predictions
max_pred = df["pred_corrected"].max()
max_actual = df["actual_SW_IN"].max()
print(f"Max corrected prediction: {max_pred:.2f} W/m²")
print(f"Max actual SW_IN: {max_actual:.2f} W/m²")

if n_exceed_2_0 > 0:
    exceed = df[df["ratio_to_clearsky"] > 2.0]
    print(f"\n  Predictions > 2x clearsky GHI:")
    for _, row in exceed.head(10).iterrows():
        print(f"    {row['timestamp']}: pred={row['pred_corrected']:.1f}, "
              f"clearsky={row['clearsky_ghi']:.1f}, actual={row['actual_SW_IN']:.1f}, "
              f"cloud={row['fc_cloud_cover']:.0f}%, regime={row['cloud_regime']}")

# Night predictions
night_corr = df[~df["is_daytime"]]["pred_corrected"]
print(f"\nNight predictions: mean={night_corr.mean():.4f}, max={night_corr.max():.4f}")

# ============================================================
# 8. MAIN EVALUATION — TEST SET
# ============================================================
print("\n" + "=" * 70)
print("STAGE 4.1 EVALUATION — TEST SET")
print("=" * 70)

s4_test_metrics = compute_metrics(df_test["actual_SW_IN"].values,
                                   df_test["pred_ensemble"].values, "Stage 4")
s41_test_metrics = compute_metrics(df_test["actual_SW_IN"].values,
                                    df_test["pred_corrected"].values, "Stage 4.1")

print(f"\n{'Metric':25s} {'Stage 4':>12s} {'Stage 4.1':>12s} {'Δ':>10s}")
print("-" * 65)
for key in ["overall_mae", "overall_rmse", "day_mae", "day_rmse",
            "day_nmae", "day_nrmse", "day_bias", "night_mae"]:
    v4 = s4_test_metrics[key]
    v41 = s41_test_metrics[key]
    delta = v41 - v4
    unit = "%" if "nmae" in key or "nrmse" in key else " W/m²"
    fmt = ".2f" if "nmae" in key or "nrmse" in key else ".4f"
    print(f"  {key:23s} {v4:{fmt}}{unit} {v41:{fmt}}{unit} {delta:+{fmt}}{unit}")

# Also compute FULL dataset metrics
s4_full = compute_metrics(df["actual_SW_IN"].values,
                           df["pred_ensemble"].values, "Stage 4 (full)")
s41_full = compute_metrics(df["actual_SW_IN"].values,
                            df["pred_corrected"].values, "Stage 4.1 (full)")

print(f"\n{'Metric':25s} {'Stage 4':>12s} {'Stage 4.1':>12s} {'Δ':>10s}")
print("(Full dataset)")
print("-" * 65)
for key in ["overall_mae", "overall_rmse", "day_mae", "day_rmse",
            "day_nmae", "day_nrmse", "day_bias", "night_mae"]:
    v4 = s4_full[key]
    v41 = s41_full[key]
    delta = v41 - v4
    unit = "%" if "nmae" in key or "nrmse" in key else " W/m²"
    fmt = ".2f" if "nmae" in key or "nrmse" in key else ".4f"
    print(f"  {key:23s} {v4:{fmt}}{unit} {v41:{fmt}}{unit} {delta:+{fmt}}{unit}")

# Also compute TRAIN metrics to check overfitting
s4_train = compute_metrics(df_train["actual_SW_IN"].values,
                            df_train["pred_ensemble"].values, "Stage 4 (train)")
s41_train = compute_metrics(df_train["actual_SW_IN"].values,
                             df_train["pred_corrected"].values, "Stage 4.1 (train)")

print(f"\n  Train/Test gap check:")
print(f"    Stage 4:  train nMAE={s4_train['day_nmae']:.2f}%, test nMAE={s4_test_metrics['day_nmae']:.2f}%, "
      f"gap={s4_test_metrics['day_nmae'] - s4_train['day_nmae']:+.2f}pp")
print(f"    Stage 4.1: train nMAE={s41_train['day_nmae']:.2f}%, test nMAE={s41_test_metrics['day_nmae']:.2f}%, "
      f"gap={s41_test_metrics['day_nmae'] - s41_train['day_nmae']:+.2f}pp")

# ============================================================
# 9. HIGH-SOLAR EVALUATION
# ============================================================
print("\n" + "=" * 70)
print("HIGH-SOLAR EVALUATION (test, actual > 500 W/m²)")
print("=" * 70)

hs_test = test_day[test_day["actual_SW_IN"] > 500]

if len(hs_test) > 0:
    hs_s4_mae = hs_test["s4_abs_residual"].mean()
    hs_s4_bias = hs_test["s4_residual"].mean()
    hs_corr_mae = (hs_test["pred_corrected"] - hs_test["actual_SW_IN"]).abs().mean()
    hs_corr_bias = (hs_test["pred_corrected"] - hs_test["actual_SW_IN"]).mean()
    
    print(f"  N test hours:            {len(hs_test)}")
    print(f"  Mean actual:             {hs_test['actual_SW_IN'].mean():.2f} W/m²")
    print(f"  Stage 4 mean prediction: {hs_test['pred_ensemble'].mean():.2f} W/m²")
    print(f"  Stage 4.1 mean predict:  {hs_test['pred_corrected'].mean():.2f} W/m²")
    print(f"  Stage 4 MAE:             {hs_s4_mae:.2f} W/m²")
    print(f"  Stage 4.1 MAE:           {hs_corr_mae:.2f} W/m²")
    print(f"  Δ MAE:                   {hs_corr_mae - hs_s4_mae:+.2f} W/m²")
    print(f"  Stage 4 bias:            {hs_s4_bias:+.2f} W/m²")
    print(f"  Stage 4.1 bias:          {hs_corr_bias:+.2f} W/m²")

# Also check >300 threshold
hs300 = test_day[test_day["actual_SW_IN"] > 300]
if len(hs300) > 0:
    hs300_s4 = hs300["s4_abs_residual"].mean()
    hs300_corr = (hs300["pred_corrected"] - hs300["actual_SW_IN"]).abs().mean()
    print(f"\n  actual > 300 W/m² (n={len(hs300)}):")
    print(f"    Stage 4 MAE:  {hs300_s4:.2f} W/m²")
    print(f"    Stage 4.1 MAE:{hs300_corr:.2f} W/m²")
    print(f"    Δ MAE:        {hs300_corr - hs300_s4:+.2f} W/m²")

# ============================================================
# 10. CLOUD-REGIME EVALUATION (test)
# ============================================================
print("\n" + "=" * 70)
print("CLOUD-REGIME EVALUATION (test, daytime)")
print("=" * 70)

regime_metrics = []
print(f"{'Regime':22s} {'N':>6s} {'S4 MAE':>8s} {'S4.1 MAE':>8s} {'Δ':>8s} "
      f"{'S4 bias':>8s} {'S4.1 bias':>9s}")
print("-" * 78)

for regime in regime_order:
    rd = test_day[test_day["cloud_regime"] == regime]
    if len(rd) == 0:
        continue
    s4_mae = rd["s4_abs_residual"].mean()
    s4_bias = rd["s4_residual"].mean()
    corr_mae = (rd["pred_corrected"] - rd["actual_SW_IN"]).abs().mean()
    corr_bias = (rd["pred_corrected"] - rd["actual_SW_IN"]).mean()
    delta = corr_mae - s4_mae
    degraded = " ***WORSE" if delta > 1.0 else ""
    
    print(f"  {regime:22s} {len(rd):6d} {s4_mae:8.2f} {corr_mae:8.2f} {delta:+8.2f} "
          f"{s4_bias:+8.2f} {corr_bias:+9.2f}{degraded}")
    
    regime_metrics.append({
        "regime": regime, "n_day": len(rd), "mean_actual": rd["actual_SW_IN"].mean(),
        "s4_mae": s4_mae, "s41_mae": corr_mae, "delta_mae": delta,
        "s4_bias": s4_bias, "s41_bias": corr_bias
    })

pd.DataFrame(regime_metrics).to_csv(OUT / "cloud_regime_metrics.csv", index=False)

# ============================================================
# 11. HORIZON EVALUATION (test)
# ============================================================
print("\n" + "=" * 70)
print("HORIZON EVALUATION (test, daytime)")
print("=" * 70)

horizon_metrics = []
degraded_horizons = 0
print(f"{'H':>3s} {'N':>6s} {'S4 MAE':>8s} {'S4.1 MAE':>8s} {'Δ':>8s} "
      f"{'S4 bias':>8s} {'S4.1 bias':>9s}")
print("-" * 58)

for h in range(1, 25):
    hd = test_day[test_day["horizon_hour"] == h]
    if len(hd) == 0:
        continue
    s4_mae = hd["s4_abs_residual"].mean()
    s4_bias = hd["s4_residual"].mean()
    corr_mae = (hd["pred_corrected"] - hd["actual_SW_IN"]).abs().mean()
    corr_bias = (hd["pred_corrected"] - hd["actual_SW_IN"]).mean()
    delta = corr_mae - s4_mae
    
    flag = ""
    if delta > 1.0:
        flag = " ***WORSE"
        degraded_horizons += 1
    
    print(f"H{h:2d} {len(hd):6d} {s4_mae:8.2f} {corr_mae:8.2f} {delta:+8.2f} "
          f"{s4_bias:+8.2f} {corr_bias:+9.2f}{flag}")
    
    horizon_metrics.append({
        "horizon": h, "n_day": len(hd),
        "s4_mae": s4_mae, "s41_mae": corr_mae, "delta_mae": delta,
        "s4_bias": s4_bias, "s41_bias": corr_bias
    })

print(f"\nHorizons degraded (Δ > 1.0 W/m²): {degraded_horizons}")
pd.DataFrame(horizon_metrics).to_csv(OUT / "horizon_metrics.csv", index=False)

# ============================================================
# 12. SEASON / MONTH EVALUATION (test)
# ============================================================
print("\n" + "=" * 70)
print("SEASONAL EVALUATION (test, daytime)")
print("=" * 70)

seasonal_metrics = []
print(f"{'Season':>6s} {'N':>6s} {'MeanAct':>8s} {'S4 MAE':>8s} {'S4.1 MAE':>8s} {'Δ':>8s} "
      f"{'S4 nMAE':>8s} {'S4.1 nMAE':>9s}")
print("-" * 75)

for s in ["DJF", "MAM", "JJA", "SON"]:
    sd = test_day[test_day["season"] == s]
    if len(sd) == 0:
        continue
    ma = sd["actual_SW_IN"].mean()
    s4_mae = sd["s4_abs_residual"].mean()
    corr_mae = (sd["pred_corrected"] - sd["actual_SW_IN"]).abs().mean()
    s4_nmae = s4_mae / ma * 100 if ma > 0 else np.nan
    corr_nmae = corr_mae / ma * 100 if ma > 0 else np.nan
    delta = corr_mae - s4_mae
    
    print(f"  {s:>4s} {len(sd):6d} {ma:8.2f} {s4_mae:8.2f} {corr_mae:8.2f} {delta:+8.2f} "
          f"{s4_nmae:8.2f}% {corr_nmae:9.2f}%")
    
    seasonal_metrics.append({
        "season": s, "n_day": len(sd), "mean_actual": ma,
        "s4_mae": s4_mae, "s41_mae": corr_mae, "delta_mae": delta,
        "s4_nmae": s4_nmae, "s41_nmae": corr_nmae
    })

pd.DataFrame(seasonal_metrics).to_csv(OUT / "seasonal_metrics.csv", index=False)

print("\n--- Monthly (test, daytime) ---")
monthly_metrics = []
print(f"{'Month':>5s} {'N':>6s} {'MeanAct':>8s} {'S4 MAE':>8s} {'S4.1 MAE':>8s} {'Δ':>8s} "
      f"{'S4 nMAE':>8s} {'S4.1 nMAE':>9s}")
print("-" * 75)

for m in range(1, 13):
    md = test_day[test_day["month"] == m]
    if len(md) == 0:
        continue
    ma = md["actual_SW_IN"].mean()
    s4_mae = md["s4_abs_residual"].mean()
    corr_mae = (md["pred_corrected"] - md["actual_SW_IN"]).abs().mean()
    s4_nmae = s4_mae / ma * 100 if ma > 0 else np.nan
    corr_nmae = corr_mae / ma * 100 if ma > 0 else np.nan
    delta = corr_mae - s4_mae
    
    print(f"  {m:3d} {len(md):6d} {ma:8.2f} {s4_mae:8.2f} {corr_mae:8.2f} {delta:+8.2f} "
          f"{s4_nmae:8.2f}% {corr_nmae:9.2f}%")
    
    monthly_metrics.append({
        "month": m, "n_day": len(md), "mean_actual": ma,
        "s4_mae": s4_mae, "s41_mae": corr_mae, "delta_mae": delta,
        "s4_nmae": s4_nmae, "s41_nmae": corr_nmae
    })

pd.DataFrame(monthly_metrics).to_csv(OUT / "monthly_metrics.csv", index=False)

# ============================================================
# 13. SAVE ARTIFACTS
# ============================================================
print("\n" + "=" * 70)
print("SAVING ARTIFACTS")
print("=" * 70)

# Save calibration parameters (without giant knot arrays for readability)
params_summary = {}
for regime in regime_order:
    p = calibration_params[regime].copy()
    if "x_knots" in p:
        p["x_knots_range"] = [float(min(p["x_knots"])), float(max(p["x_knots"]))]
        p["y_knots_range"] = [float(min(p["y_knots"])), float(max(p["y_knots"]))]
    params_summary[regime] = p

with open(OUT / "calibration_parameters.json", "w") as f:
    json.dump(params_summary, f, indent=2, default=str)
print(f"  Saved: {OUT / 'calibration_parameters.json'}")

# Save corrected predictions
pred_out = df[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
               "pred_stage3b_cloud_nwp", "pred_ensemble", "pred_corrected",
               "cloud_regime"]].copy()
pred_out.to_csv(OUT / "corrected_predictions.csv", index=False)
print(f"  Saved: {OUT / 'corrected_predictions.csv'}")

# Save final metrics
final_metrics = []
for label, pred_arr in [
    ("Stage 4", df["pred_ensemble"].values),
    ("Stage 4.1", df["pred_corrected"].values),
]:
    m = compute_metrics(df["actual_SW_IN"].values, pred_arr, label)
    final_metrics.append(m)
pd.DataFrame(final_metrics).to_csv(OUT / "final_metrics.csv", index=False)
print(f"  Saved: {OUT / 'final_metrics.csv'}")

# ============================================================
# 14. FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(f"""
POLARIS Stage 4.1 — Cloud-Regime-Conditioned Amplitude Correction

METHOD:
  Per-cloud-regime isotonic regression (PAV algorithm)
  Fitted on training daytime data only (174 even-indexed origins)
  Applied frozen to test (173 odd-indexed origins)

STAGE 4 TEST BASELINE:
  Overall MAE:  {s4_test_metrics['overall_mae']:.4f} W/m²
  Daytime MAE:  {s4_test_metrics['day_mae']:.4f} W/m²
  Daytime nMAE: {s4_test_metrics['day_nmae']:.2f}%
  Daytime RMSE: {s4_test_metrics['day_rmse']:.4f} W/m²
  Daytime bias: {s4_test_metrics['day_bias']:+.4f} W/m²

STAGE 4.1 TEST RESULT:
  Overall MAE:  {s41_test_metrics['overall_mae']:.4f} W/m²
  Daytime MAE:  {s41_test_metrics['day_mae']:.4f} W/m²
  Daytime nMAE: {s41_test_metrics['day_nmae']:.2f}%
  Daytime RMSE: {s41_test_metrics['day_rmse']:.4f} W/m²
  Daytime bias: {s41_test_metrics['day_bias']:+.4f} W/m²

CHANGE:
  Daytime MAE:  {s41_test_metrics['day_mae'] - s4_test_metrics['day_mae']:+.4f} W/m²
  Daytime nMAE: {s41_test_metrics['day_nmae'] - s4_test_metrics['day_nmae']:+.2f} pp
  Daytime RMSE: {s41_test_metrics['day_rmse'] - s4_test_metrics['day_rmse']:+.4f} W/m²
""")

if len(hs_test) > 0:
    print(f"""HIGH-SOLAR (test, actual > 500 W/m², n={len(hs_test)}):
  Stage 4 MAE:  {hs_s4_mae:.2f} W/m²
  Stage 4.1 MAE:{hs_corr_mae:.2f} W/m²
  Δ MAE:        {hs_corr_mae - hs_s4_mae:+.2f} W/m²
  Stage 4 bias: {hs_s4_bias:+.2f} W/m²
  Stage 4.1 bias:{hs_corr_bias:+.2f} W/m²
""")

print(f"Degraded horizons (Δ > 1.0 W/m²): {degraded_horizons}")
print(f"Pathological predictions (negative): {n_neg}")
print(f"Predictions > 1.5x clearsky: {n_exceed_1_5}")
print(f"Predictions > 2.0x clearsky: {n_exceed_2_0}")

print("\nARTIFACTS:")
for f_path in sorted(OUT.iterdir()):
    print(f"  {f_path}")

print("\n" + "=" * 70)
print("STAGE 4.1 EXPERIMENT COMPLETE")
print("=" * 70)
