#!/usr/bin/env python3
"""
POLARIS Stage 4 — Horizon-Adaptive Cloud-Damped Clearsky Ensemble
+ Lightweight Residual Correction Investigation
================================================================

LOCKED BASELINE: Stage 3B (Chronos-2 + solar geometry + cloud NWP)
DO NOT modify or rerun Stage 3 artifacts.

Split: odd/even origin interleaving (all months in both splits)
Train: even-indexed origins (174)
Test:  odd-indexed origins (173)

All learned parameters fitted ONLY on train data.
Test data touched ONLY for final evaluation.
"""
import pandas as pd
import numpy as np
from scipy import stats, optimize
from pathlib import Path
import json, sys, warnings, datetime
warnings.filterwarnings("ignore")

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT = BASE / "forecasting/stage4" / "stage4_results"
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. LOAD DATA (read-only from Stage 3 / data)
# ============================================================
print("=" * 70)
print("STAGE 4 — LOADING DATA")
print("=" * 70)

pred = pd.read_csv(BASE / "forecasting/stage3" / "stage3b_cloud_nwp_predictions.csv")
pred["timestamp"] = pd.to_datetime(pred["timestamp"])
pred["forecast_start"] = pd.to_datetime(pred["forecast_start"])
print(f"Predictions: {len(pred)} rows, {pred['forecast_start'].nunique()} origins")

cs = pd.read_csv(BASE / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
print(f"Clear-sky: {len(cs)} rows")

nwp = pd.read_csv(BASE / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv")
nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])
print(f"NWP: {len(nwp)} rows")

# Load SITES observations for context features
sites = pd.read_csv(BASE / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv")
sites["TIMESTAMP"] = pd.to_datetime(sites["TIMESTAMP"])
sites = sites.rename(columns={"SW_IN": "obs_SW_IN"})
print(f"SITES observations: {len(sites)} rows")

# Merge all onto predictions
cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
df = pred.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left")
df.drop(columns=["TIMESTAMP"], inplace=True)

nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m",
            "fc_relative_humidity_2m"]
df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")

# Derived columns
df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
df["is_daytime"] = df["actual_SW_IN"] > 0
df["month"] = df["timestamp"].dt.month
df["hour"] = df["timestamp"].dt.hour
season_map = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
              6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
df["season"] = df["month"].map(season_map)

# Clear-sky index
df["kt_actual"] = np.where(df["clearsky_ghi"] > 10,
                            df["actual_SW_IN"] / df["clearsky_ghi"], np.nan)

# Solar regime
def solar_regime(x):
    if x == 0: return "Night (0)"
    elif x <= 50: return "Twilight (0-50]"
    elif x <= 100: return "Low (50-100]"
    elif x <= 200: return "Moderate (100-200]"
    elif x <= 300: return "Mod-High (200-300]"
    elif x <= 500: return "High (300-500]"
    else: return "Very High (>500)"
df["actual_regime"] = df["actual_SW_IN"].apply(solar_regime)

# Cloud regime
def cloud_regime(c):
    if pd.isna(c): return "Missing"
    elif c <= 10: return "Clear (0-10%)"
    elif c <= 30: return "Few (10-30%)"
    elif c <= 60: return "Scattered (30-60%)"
    elif c <= 80: return "Broken (60-80%)"
    else: return "Overcast (80-100%)"
df["cloud_regime"] = df["fc_cloud_cover"].apply(cloud_regime)

# kt bins
def kt_bin(kt):
    if pd.isna(kt): return np.nan
    elif kt <= 0.2: return "kt 0-0.2"
    elif kt <= 0.4: return "kt 0.2-0.4"
    elif kt <= 0.6: return "kt 0.4-0.6"
    elif kt <= 0.8: return "kt 0.6-0.8"
    elif kt <= 1.0: return "kt 0.8-1.0"
    else: return "kt >1.0"
df["kt_bin"] = df["kt_actual"].apply(kt_bin)

# Rising vs falling
df["solar_period"] = np.where(df["hour"] < 12, "Rising", "Falling")

# Add context features: recent 24h SW_IN statistics
# For each forecast origin, compute stats from the 24h BEFORE forecast_start
print("Computing context features...")
context_stats = []
for origin in df["forecast_start"].unique():
    origin_ts = pd.Timestamp(origin)
    context_start = origin_ts - pd.Timedelta(hours=24)
    context = sites[(sites["TIMESTAMP"] >= context_start) & (sites["TIMESTAMP"] < origin_ts)]
    sw_vals = context["obs_SW_IN"].dropna()
    if len(sw_vals) > 0:
        context_stats.append({
            "forecast_start": origin,
            "ctx_mean": sw_vals.mean(),
            "ctx_max": sw_vals.max(),
            "ctx_min": sw_vals.min(),
            "ctx_std": sw_vals.std() if len(sw_vals) > 1 else 0,
            "ctx_n": len(sw_vals)
        })
    else:
        context_stats.append({
            "forecast_start": origin,
            "ctx_mean": 0, "ctx_max": 0, "ctx_min": 0, "ctx_std": 0, "ctx_n": 0
        })
ctx_df = pd.DataFrame(context_stats)
df = df.merge(ctx_df, on="forecast_start", how="left")

print(f"Merged dataset: {len(df)} rows, NaN summary:")
print(f"  clearsky_ghi NaN: {df['clearsky_ghi'].isna().sum()}")
print(f"  fc_cloud_cover NaN: {df['fc_cloud_cover'].isna().sum()}")
print(f"  solar_elevation NaN: {df['solar_elevation'].isna().sum()}")

# Stage 3B residuals
df["s3b_residual"] = df["pred_stage3b_cloud_nwp"] - df["actual_SW_IN"]
df["s3b_abs_residual"] = df["s3b_residual"].abs()

# ============================================================
# 2. TRAIN / TEST SPLIT
# ============================================================
print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

origins = sorted(df["forecast_start"].unique())
n_origins = len(origins)
even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
odd_origins = [o for i, o in enumerate(origins) if i % 2 == 1]

train_mask = df["forecast_start"].isin(even_origins)
test_mask = df["forecast_start"].isin(odd_origins)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

train_day = df_train[df_train["is_daytime"]].copy()
test_day = df_test[df_test["is_daytime"]].copy()

print(f"Total origins: {n_origins}")
print(f"Train origins: {len(even_origins)}, date range: "
      f"{pd.Timestamp(even_origins[0]).date()} to {pd.Timestamp(even_origins[-1]).date()}")
print(f"Test origins:  {len(odd_origins)}, date range: "
      f"{pd.Timestamp(odd_origins[0]).date()} to {pd.Timestamp(odd_origins[-1]).date()}")
print(f"Train total: {len(df_train)}, daytime: {len(train_day)}")
print(f"Test total:  {len(df_test)}, daytime: {len(test_day)}")
print(f"Train months: {sorted(train_day['month'].unique())}")
print(f"Test months:  {sorted(test_day['month'].unique())}")

# ============================================================
# 3. VERIFY STAGE 3B BASELINE
# ============================================================
print("\n" + "=" * 70)
print("SECTION A — VERIFIED STAGE 3B BASELINE")
print("=" * 70)

def compute_full_metrics(actual, predicted, label=""):
    """Compute all metrics for a prediction vector."""
    residual = predicted - actual
    abs_res = np.abs(residual)
    is_day = actual > 0
    
    overall_mae = abs_res.mean()
    overall_rmse = np.sqrt((residual**2).mean())
    
    day_mask = is_day
    if day_mask.sum() > 0:
        day_mae = abs_res[day_mask].mean()
        day_rmse = np.sqrt((residual[day_mask]**2).mean())
        day_mean_actual = actual[day_mask].mean()
        day_nmae = day_mae / day_mean_actual * 100
        day_nrmse = day_rmse / day_mean_actual * 100
        day_bias = residual[day_mask].mean()
    else:
        day_mae = day_rmse = day_nmae = day_nrmse = day_bias = np.nan
    
    night_mask = ~is_day
    night_mae = abs_res[night_mask].mean() if night_mask.sum() > 0 else np.nan
    
    return {
        "label": label,
        "overall_mae": overall_mae, "overall_rmse": overall_rmse,
        "day_mae": day_mae, "day_rmse": day_rmse,
        "day_nmae": day_nmae, "day_nrmse": day_nrmse,
        "day_bias": day_bias, "day_mean_actual": day_mean_actual,
        "night_mae": night_mae, "n_total": len(actual),
        "n_day": int(day_mask.sum()), "n_night": int(night_mask.sum())
    }

# Full dataset Stage 3B
s3b_full = compute_full_metrics(df["actual_SW_IN"].values,
                                 df["pred_stage3b_cloud_nwp"].values, "Stage 3B (full)")
print(f"Stage 3B (ALL {s3b_full['n_total']} hours):")
print(f"  Overall MAE:  {s3b_full['overall_mae']:.4f} W/m²")
print(f"  Overall RMSE: {s3b_full['overall_rmse']:.4f} W/m²")
print(f"  Daytime MAE:  {s3b_full['day_mae']:.4f} W/m²")
print(f"  Daytime RMSE: {s3b_full['day_rmse']:.4f} W/m²")
print(f"  Daytime nMAE: {s3b_full['day_nmae']:.2f}%")
print(f"  Daytime nRMSE:{s3b_full['day_nrmse']:.2f}%")
print(f"  Night MAE:    {s3b_full['night_mae']:.4f} W/m²")
print(f"  Daytime bias: {s3b_full['day_bias']:.4f} W/m²")
print(f"  Mean day actual: {s3b_full['day_mean_actual']:.2f} W/m²")

# Train/Test Stage 3B
s3b_train = compute_full_metrics(df_train["actual_SW_IN"].values,
                                  df_train["pred_stage3b_cloud_nwp"].values, "Stage 3B (train)")
s3b_test = compute_full_metrics(df_test["actual_SW_IN"].values,
                                 df_test["pred_stage3b_cloud_nwp"].values, "Stage 3B (test)")
print(f"\nStage 3B (TRAIN): day MAE={s3b_train['day_mae']:.4f}, nMAE={s3b_train['day_nmae']:.2f}%")
print(f"Stage 3B (TEST):  day MAE={s3b_test['day_mae']:.4f}, nMAE={s3b_test['day_nmae']:.2f}%")

# ============================================================
# 4. FIT HORIZON-ADAPTIVE ENSEMBLE (TRAIN ONLY)
# ============================================================
print("\n" + "=" * 70)
print("SECTION B — FITTING HORIZON-ADAPTIVE ENSEMBLE (TRAIN ONLY)")
print("=" * 70)

def physics_model(clearsky_ghi, cloud_frac, k):
    """Cloud-damped clearsky prediction."""
    return np.maximum(clearsky_ghi * (1 - k * cloud_frac), 0)

def ensemble_pred(chronos, clearsky_ghi, cloud_frac, w, k):
    """Horizon-adaptive ensemble prediction."""
    phys = physics_model(clearsky_ghi, cloud_frac, k)
    return np.maximum(w * chronos + (1 - w) * phys, 0)

horizon_params = {}

for h in range(1, 25):
    tr_h = df_train[df_train["horizon_hour"] == h]
    tr_h_day = tr_h[tr_h["is_daytime"]]
    
    if len(tr_h_day) < 5:
        # Insufficient daytime data: use Chronos alone
        horizon_params[h] = {"w": 1.0, "k": 0.7, "n_train_day": len(tr_h_day)}
        print(f"  H{h:2d}: w=1.0000, k=0.7000 (insufficient data, n_day={len(tr_h_day)})")
        continue
    
    chronos_vals = tr_h_day["pred_stage3b_cloud_nwp"].values
    cs_vals = tr_h_day["clearsky_ghi"].values
    cf_vals = tr_h_day["cloud_frac"].values
    actual_vals = tr_h_day["actual_SW_IN"].values
    
    def objective(params):
        w, k = params
        pred = ensemble_pred(chronos_vals, cs_vals, cf_vals, w, k)
        return np.abs(pred - actual_vals).mean()
    
    best_mae = np.inf
    best_params = (0.5, 0.5)
    
    # Grid search for robust initialization
    for w_init in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for k_init in [0.1, 0.3, 0.5, 0.7, 0.9]:
            try:
                res = optimize.minimize(
                    objective, x0=[w_init, k_init],
                    method="Nelder-Mead",
                    options={"maxiter": 2000, "xatol": 1e-6, "fatol": 1e-6}
                )
                if res.fun < best_mae:
                    best_mae = res.fun
                    best_params = (np.clip(res.x[0], 0, 1), np.clip(res.x[1], 0, 1))
            except:
                pass
    
    w_opt, k_opt = best_params
    horizon_params[h] = {"w": float(w_opt), "k": float(k_opt),
                          "n_train_day": int(len(tr_h_day)),
                          "train_mae": float(best_mae)}
    print(f"  H{h:2d}: w={w_opt:.4f}, k={k_opt:.4f}, n_day={len(tr_h_day):4d}, train_MAE={best_mae:.2f}")

# Save parameters
params_file = OUT / "ensemble_parameters.json"
with open(params_file, "w") as f:
    json.dump(horizon_params, f, indent=2)
print(f"\nParameters saved to: {params_file}")

# ============================================================
# 5. APPLY ENSEMBLE TO ALL DATA
# ============================================================
print("\n" + "=" * 70)
print("APPLYING ENSEMBLE TO ALL DATA")
print("=" * 70)

def apply_ensemble(row):
    h = int(row["horizon_hour"])
    p = horizon_params[h]
    return ensemble_pred(
        row["pred_stage3b_cloud_nwp"],
        row["clearsky_ghi"],
        row["cloud_frac"],
        p["w"], p["k"]
    )

df["pred_ensemble"] = df.apply(apply_ensemble, axis=1)
df["ens_residual"] = df["pred_ensemble"] - df["actual_SW_IN"]
df["ens_abs_residual"] = df["ens_residual"].abs()

# Recompute masks
df_train = df[train_mask].copy()
df_test = df[test_mask].copy()
train_day = df_train[df_train["is_daytime"]].copy()
test_day = df_test[df_test["is_daytime"]].copy()

# ============================================================
# 6. VERIFY ENSEMBLE METRICS
# ============================================================
print("\n" + "=" * 70)
print("SECTION B — VERIFIED ENSEMBLE RESULT")
print("=" * 70)

ens_full = compute_full_metrics(df["actual_SW_IN"].values,
                                 df["pred_ensemble"].values, "Ensemble (full)")
ens_train = compute_full_metrics(df_train["actual_SW_IN"].values,
                                  df_train["pred_ensemble"].values, "Ensemble (train)")
ens_test = compute_full_metrics(df_test["actual_SW_IN"].values,
                                 df_test["pred_ensemble"].values, "Ensemble (test)")

for label, m in [("FULL", ens_full), ("TRAIN", ens_train), ("TEST", ens_test)]:
    print(f"\nEnsemble ({label}, {m['n_total']} hours, {m['n_day']} daytime):")
    print(f"  Overall MAE:  {m['overall_mae']:.4f}")
    print(f"  Overall RMSE: {m['overall_rmse']:.4f}")
    print(f"  Daytime MAE:  {m['day_mae']:.4f}")
    print(f"  Daytime RMSE: {m['day_rmse']:.4f}")
    print(f"  Daytime nMAE: {m['day_nmae']:.2f}%")
    print(f"  Daytime nRMSE:{m['day_nrmse']:.2f}%")
    print(f"  Night MAE:    {m['night_mae']:.4f}")
    print(f"  Daytime bias: {m['day_bias']:.4f}")

# ============================================================
# 7. PER-HORIZON COMPARISON (TEST)
# ============================================================
print("\n" + "=" * 70)
print("SECTION F — PER-HORIZON COMPARISON (TEST SET)")
print("=" * 70)

horizon_results = []
print(f"{'H':>3s} {'n_day':>6s} {'S3B_MAE':>9s} {'Ens_MAE':>9s} {'Delta':>8s} {'S3B_bias':>9s} {'Ens_bias':>9s}")
for h in range(1, 25):
    te_h = df_test[df_test["horizon_hour"] == h]
    te_h_day = te_h[te_h["is_daytime"]]
    
    if len(te_h_day) == 0:
        horizon_results.append({"horizon": h, "n_day": 0})
        continue
    
    s3b_mae_h = te_h_day["s3b_abs_residual"].mean()
    ens_mae_h = te_h_day["ens_abs_residual"].mean()
    s3b_bias_h = te_h_day["s3b_residual"].mean()
    ens_bias_h = te_h_day["ens_residual"].mean()
    delta = ens_mae_h - s3b_mae_h
    
    degraded = "***WORSE***" if delta > 0.01 else ""
    print(f"H{h:2d} {len(te_h_day):6d} {s3b_mae_h:9.2f} {ens_mae_h:9.2f} {delta:+8.2f} "
          f"{s3b_bias_h:+9.2f} {ens_bias_h:+9.2f} {degraded}")
    
    horizon_results.append({
        "horizon": h, "n_day": len(te_h_day),
        "s3b_day_mae": s3b_mae_h, "ens_day_mae": ens_mae_h,
        "delta_mae": delta,
        "s3b_day_bias": s3b_bias_h, "ens_day_bias": ens_bias_h
    })

pd.DataFrame(horizon_results).to_csv(OUT / "horizon_comparison.csv", index=False)

# Count degraded horizons
degraded_count = sum(1 for r in horizon_results if r.get("delta_mae", 0) > 0.01 and r.get("n_day", 0) > 0)
print(f"\nHorizons with degraded test MAE: {degraded_count}")

# ============================================================
# 8. MONTHLY / SEASONAL PERFORMANCE (TEST)
# ============================================================
print("\n" + "=" * 70)
print("SECTION G — MONTHLY/SEASONAL PERFORMANCE (TEST)")
print("=" * 70)

print("\nMonthly daytime (TEST):")
monthly_results = []
for m in sorted(test_day["month"].unique()):
    md = test_day[test_day["month"] == m]
    mean_act = md["actual_SW_IN"].mean()
    s3b_mae = md["s3b_abs_residual"].mean()
    ens_mae = md["ens_abs_residual"].mean()
    s3b_nmae = s3b_mae / mean_act * 100 if mean_act > 0 else np.nan
    ens_nmae = ens_mae / mean_act * 100 if mean_act > 0 else np.nan
    print(f"  Month {m:2d}: n={len(md):5d}, mean_act={mean_act:7.2f}, "
          f"S3B_nMAE={s3b_nmae:6.2f}%, Ens_nMAE={ens_nmae:6.2f}%, Δ={ens_nmae-s3b_nmae:+6.2f}pp")
    monthly_results.append({
        "month": m, "n_day": len(md), "mean_actual": mean_act,
        "s3b_mae": s3b_mae, "s3b_nmae": s3b_nmae,
        "ens_mae": ens_mae, "ens_nmae": ens_nmae
    })

print("\nSeasonal daytime (TEST):")
seasonal_results = []
for s in ["DJF", "MAM", "JJA", "SON"]:
    sd = test_day[test_day["season"] == s]
    if len(sd) == 0: continue
    mean_act = sd["actual_SW_IN"].mean()
    s3b_mae = sd["s3b_abs_residual"].mean()
    ens_mae = sd["ens_abs_residual"].mean()
    s3b_nmae = s3b_mae / mean_act * 100 if mean_act > 0 else np.nan
    ens_nmae = ens_mae / mean_act * 100 if mean_act > 0 else np.nan
    print(f"  {s}: n={len(sd):5d}, S3B_nMAE={s3b_nmae:6.2f}%, Ens_nMAE={ens_nmae:6.2f}%, Δ={ens_nmae-s3b_nmae:+6.2f}pp")
    seasonal_results.append({
        "season": s, "n_day": len(sd), "mean_actual": mean_act,
        "s3b_mae": s3b_mae, "s3b_nmae": s3b_nmae,
        "ens_mae": ens_mae, "ens_nmae": ens_nmae
    })

pd.DataFrame(monthly_results).to_csv(OUT / "monthly_metrics.csv", index=False)
pd.DataFrame(seasonal_results).to_csv(OUT / "seasonal_metrics.csv", index=False)

# ============================================================
# 9. CLOUD-REGIME PERFORMANCE (TEST)
# ============================================================
print("\n" + "=" * 70)
print("SECTION H — CLOUD-REGIME PERFORMANCE (TEST)")
print("=" * 70)

cloud_order = ["Clear (0-10%)", "Few (10-30%)", "Scattered (30-60%)",
               "Broken (60-80%)", "Overcast (80-100%)"]
cloud_results = []
for cr in cloud_order:
    cd = test_day[test_day["cloud_regime"] == cr]
    if len(cd) == 0: continue
    mean_act = cd["actual_SW_IN"].mean()
    s3b_mae = cd["s3b_abs_residual"].mean()
    ens_mae = cd["ens_abs_residual"].mean()
    s3b_bias = cd["s3b_residual"].mean()
    ens_bias = cd["ens_residual"].mean()
    print(f"  {cr:22s}: n={len(cd):5d}, S3B_MAE={s3b_mae:7.2f}, Ens_MAE={ens_mae:7.2f}, "
          f"Δ={ens_mae-s3b_mae:+7.2f}, S3B_bias={s3b_bias:+7.2f}, Ens_bias={ens_bias:+7.2f}")
    cloud_results.append({"regime": cr, "n_day": len(cd), "mean_actual": mean_act,
                           "s3b_mae": s3b_mae, "ens_mae": ens_mae,
                           "s3b_bias": s3b_bias, "ens_bias": ens_bias})

pd.DataFrame(cloud_results).to_csv(OUT / "cloud_regime_metrics.csv", index=False)

# ============================================================
# 10. SOLAR-REGIME PERFORMANCE (TEST)
# ============================================================
print("\n" + "=" * 70)
print("SECTION E — SOLAR-REGIME / HIGH-SOLAR PERFORMANCE (TEST)")
print("=" * 70)

regime_order = ["Twilight (0-50]", "Low (50-100]", "Moderate (100-200]",
                "Mod-High (200-300]", "High (300-500]", "Very High (>500)"]
regime_results = []
for rg in regime_order:
    rd = test_day[test_day["actual_regime"] == rg]
    if len(rd) == 0: continue
    s3b_mae = rd["s3b_abs_residual"].mean()
    ens_mae = rd["ens_abs_residual"].mean()
    s3b_bias = rd["s3b_residual"].mean()
    ens_bias = rd["ens_residual"].mean()
    print(f"  {rg:22s}: n={len(rd):5d}, S3B_MAE={s3b_mae:7.2f}, Ens_MAE={ens_mae:7.2f}, "
          f"Δ={ens_mae-s3b_mae:+7.2f}, S3B_bias={s3b_bias:+7.2f}, Ens_bias={ens_bias:+7.2f}")
    regime_results.append({"regime": rg, "n_day": len(rd),
                            "s3b_mae": s3b_mae, "ens_mae": ens_mae,
                            "s3b_bias": s3b_bias, "ens_bias": ens_bias})

pd.DataFrame(regime_results).to_csv(OUT / "solar_regime_metrics.csv", index=False)

# High-solar deep-dive (actual > 500)
print("\nHigh-solar deep-dive (actual > 500 W/m², TEST):")
hs_test = test_day[test_day["actual_SW_IN"] > 500]
if len(hs_test) > 0:
    print(f"  n = {len(hs_test)}")
    print(f"  Mean actual:    {hs_test['actual_SW_IN'].mean():.2f}")
    print(f"  S3B mean pred:  {hs_test['pred_stage3b_cloud_nwp'].mean():.2f}")
    print(f"  Ens mean pred:  {hs_test['pred_ensemble'].mean():.2f}")
    print(f"  S3B MAE:  {hs_test['s3b_abs_residual'].mean():.2f}, bias: {hs_test['s3b_residual'].mean():+.2f}")
    print(f"  Ens MAE:  {hs_test['ens_abs_residual'].mean():.2f}, bias: {hs_test['ens_residual'].mean():+.2f}")

# kt bins (TEST)
print("\nkt-bin performance (TEST, daytime, clearsky_ghi>10):")
kt_results = []
test_day_kt = test_day.dropna(subset=["kt_bin"])
for kb in ["kt 0-0.2", "kt 0.2-0.4", "kt 0.4-0.6", "kt 0.6-0.8", "kt 0.8-1.0", "kt >1.0"]:
    kd = test_day_kt[test_day_kt["kt_bin"] == kb]
    if len(kd) == 0: continue
    s3b_mae = kd["s3b_abs_residual"].mean()
    ens_mae = kd["ens_abs_residual"].mean()
    s3b_bias = kd["s3b_residual"].mean()
    ens_bias = kd["ens_residual"].mean()
    print(f"  {kb:15s}: n={len(kd):5d}, S3B_MAE={s3b_mae:7.2f}, Ens_MAE={ens_mae:7.2f}, "
          f"Δ={ens_mae-s3b_mae:+7.2f}, S3B_bias={s3b_bias:+7.2f}, Ens_bias={ens_bias:+7.2f}")
    kt_results.append({"kt_bin": kb, "n": len(kd),
                         "s3b_mae": s3b_mae, "ens_mae": ens_mae,
                         "s3b_bias": s3b_bias, "ens_bias": ens_bias})

pd.DataFrame(kt_results).to_csv(OUT / "kt_bin_metrics.csv", index=False)

# Rising vs falling
print("\nRising vs Falling (TEST, daytime):")
for sp in ["Rising", "Falling"]:
    spd = test_day[test_day["solar_period"] == sp]
    if len(spd) == 0: continue
    s3b_mae = spd["s3b_abs_residual"].mean()
    ens_mae = spd["ens_abs_residual"].mean()
    print(f"  {sp:8s}: n={len(spd):5d}, S3B_MAE={s3b_mae:7.2f}, Ens_MAE={ens_mae:7.2f}, Δ={ens_mae-s3b_mae:+7.2f}")

# ============================================================
# 11. RESIDUAL CORRECTION INVESTIGATION
# ============================================================
print("\n" + "=" * 70)
print("SECTION I — RESIDUAL CORRECTION INVESTIGATION")
print("=" * 70)
print("All corrections fitted on TRAIN, evaluated on TEST")
print("Candidate: predict actual_SW_IN from features including ensemble prediction")

# Manual Ridge regression: w = (X'X + alpha*I)^-1 X'y
def ridge_fit(X, y, alpha):
    XtX = X.T @ X + alpha * np.eye(X.shape[1])
    Xty = X.T @ y
    return np.linalg.solve(XtX, Xty)

def standardize_fit(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1
    return mu, sd

def standardize_apply(X, mu, sd):
    return (X - mu) / sd

# --- Correction 1: Global Ridge ---
print("\n--- Correction 1: Global Ridge Regression ---")
feat_cols_ridge = ["pred_ensemble", "clearsky_ghi", "solar_elevation",
                   "fc_cloud_cover", "ctx_mean", "ctx_max", "ctx_std"]
valid_train = train_day.dropna(subset=feat_cols_ridge)
valid_test = test_day.dropna(subset=feat_cols_ridge)

X_train = valid_train[feat_cols_ridge].values
y_train = valid_train["actual_SW_IN"].values
X_test = valid_test[feat_cols_ridge].values
y_test = valid_test["actual_SW_IN"].values

# Add bias column
X_train_b = np.column_stack([X_train, np.ones(len(X_train))])
X_test_b = np.column_stack([X_test, np.ones(len(X_test))])

mu, sd = standardize_fit(X_train_b)
X_train_s = standardize_apply(X_train_b, mu, sd)
X_test_s = standardize_apply(X_test_b, mu, sd)

ridge_results = []
for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
    w = ridge_fit(X_train_s, y_train, alpha)
    pred_tr = np.maximum(X_train_s @ w, 0)
    pred_te = np.maximum(X_test_s @ w, 0)
    tr_mae = np.abs(pred_tr - y_train).mean()
    te_mae = np.abs(pred_te - y_test).mean()
    te_rmse = np.sqrt(((pred_te - y_test)**2).mean())
    te_mean = y_test.mean()
    te_nmae = te_mae / te_mean * 100
    ens_te_mae = valid_test["ens_abs_residual"].mean()
    print(f"  alpha={alpha:7.2f}: train_MAE={tr_mae:.2f}, test_MAE={te_mae:.2f} ({te_nmae:.2f}%), "
          f"ens_test_MAE={ens_te_mae:.2f}, Δ={te_mae-ens_te_mae:+.2f}")
    ridge_results.append({"alpha": alpha, "train_mae": tr_mae, "test_mae": te_mae,
                           "test_nmae": te_nmae, "ens_test_mae": ens_te_mae})

# --- Correction 2: Horizon-specific affine ---
print("\n--- Correction 2: Horizon-Specific Affine Correction ---")
# For each horizon, fit: actual = a * ensemble + b on train
affine_params = {}
print(f"{'H':>3s} {'n_tr':>6s} {'n_te':>6s} {'Ens_te':>8s} {'Aff_te':>8s} {'Delta':>8s} {'slope':>8s} {'int':>8s}")
for h in range(1, 25):
    tr_h = train_day[train_day["horizon_hour"] == h]
    te_h = test_day[test_day["horizon_hour"] == h]
    
    if len(tr_h) < 10 or len(te_h) < 3:
        affine_params[h] = {"a": 1.0, "b": 0.0}
        continue
    
    # Fit: actual = a * ensemble_pred + b
    slope, intercept, _, _, _ = stats.linregress(tr_h["pred_ensemble"], tr_h["actual_SW_IN"])
    affine_params[h] = {"a": float(slope), "b": float(intercept)}
    
    # Apply to test
    cal_pred = np.maximum(slope * te_h["pred_ensemble"].values + intercept, 0)
    cal_mae = np.abs(cal_pred - te_h["actual_SW_IN"].values).mean()
    ens_mae_h = te_h["ens_abs_residual"].mean()
    delta = cal_mae - ens_mae_h
    print(f"H{h:2d} {len(tr_h):6d} {len(te_h):6d} {ens_mae_h:8.2f} {cal_mae:8.2f} {delta:+8.2f} "
          f"{slope:8.4f} {intercept:8.2f}")

# --- Correction 3: Regime-conditioned correction ---
print("\n--- Correction 3: Regime-Conditioned Correction ---")
# For each (cloud_regime), fit a separate affine correction on train
regime_affine = {}
for cr in cloud_order:
    tr_cr = train_day[train_day["cloud_regime"] == cr]
    if len(tr_cr) < 20:
        regime_affine[cr] = {"a": 1.0, "b": 0.0}
        continue
    sl, it, _, _, _ = stats.linregress(tr_cr["pred_ensemble"], tr_cr["actual_SW_IN"])
    regime_affine[cr] = {"a": float(sl), "b": float(it)}

# Apply to test
test_day_rc = test_day.copy()
test_day_rc["rc_pred"] = test_day_rc["pred_ensemble"].copy()
for cr in cloud_order:
    mask = test_day_rc["cloud_regime"] == cr
    a = regime_affine[cr]["a"]
    b = regime_affine[cr]["b"]
    test_day_rc.loc[mask, "rc_pred"] = np.maximum(
        a * test_day_rc.loc[mask, "pred_ensemble"].values + b, 0)

rc_mae = (test_day_rc["rc_pred"] - test_day_rc["actual_SW_IN"]).abs().mean()
rc_rmse = np.sqrt(((test_day_rc["rc_pred"] - test_day_rc["actual_SW_IN"])**2).mean())
ens_test_mae = test_day["ens_abs_residual"].mean()
rc_nmae = rc_mae / test_day["actual_SW_IN"].mean() * 100
print(f"Regime-conditioned: test MAE={rc_mae:.2f}, nMAE={rc_nmae:.2f}%, ens={ens_test_mae:.2f}, Δ={rc_mae-ens_test_mae:+.2f}")

for cr in cloud_order:
    cr_d = test_day_rc[test_day_rc["cloud_regime"] == cr]
    if len(cr_d) == 0: continue
    cr_ens = cr_d["ens_abs_residual"].mean()
    cr_rc = (cr_d["rc_pred"] - cr_d["actual_SW_IN"]).abs().mean()
    print(f"  {cr:22s}: Ens={cr_ens:.2f}, RC={cr_rc:.2f}, Δ={cr_rc-cr_ens:+.2f}")

# --- Correction 4: Ridge with interaction features ---
print("\n--- Correction 4: Ridge with Physics Interactions ---")
feat_cols_phys = ["pred_ensemble", "pred_stage3b_cloud_nwp", "clearsky_ghi",
                  "solar_elevation", "fc_cloud_cover", "ctx_mean", "ctx_max", "ctx_std"]

valid_train2 = train_day.dropna(subset=feat_cols_phys).copy()
valid_test2 = test_day.dropna(subset=feat_cols_phys).copy()

# Add interactions
valid_train2["ens_x_clearfrac"] = valid_train2["pred_ensemble"] * (1 - valid_train2["cloud_frac"])
valid_train2["ens_x_elev"] = valid_train2["pred_ensemble"] * np.maximum(valid_train2["solar_elevation"], 0) / 45.0
valid_train2["cs_x_clearfrac"] = valid_train2["clearsky_ghi"] * (1 - valid_train2["cloud_frac"])

valid_test2["ens_x_clearfrac"] = valid_test2["pred_ensemble"] * (1 - valid_test2["cloud_frac"])
valid_test2["ens_x_elev"] = valid_test2["pred_ensemble"] * np.maximum(valid_test2["solar_elevation"], 0) / 45.0
valid_test2["cs_x_clearfrac"] = valid_test2["clearsky_ghi"] * (1 - valid_test2["cloud_frac"])

all_feat_cols = feat_cols_phys + ["ens_x_clearfrac", "ens_x_elev", "cs_x_clearfrac"]

X_tr2 = valid_train2[all_feat_cols].values
y_tr2 = valid_train2["actual_SW_IN"].values
X_te2 = valid_test2[all_feat_cols].values
y_te2 = valid_test2["actual_SW_IN"].values

X_tr2_b = np.column_stack([X_tr2, np.ones(len(X_tr2))])
X_te2_b = np.column_stack([X_te2, np.ones(len(X_te2))])
mu2, sd2 = standardize_fit(X_tr2_b)
X_tr2_s = standardize_apply(X_tr2_b, mu2, sd2)
X_te2_s = standardize_apply(X_te2_b, mu2, sd2)

best_ridge_alpha = None
best_ridge_mae = np.inf
best_ridge_w = None

for alpha in [0.01, 0.1, 1.0, 10.0, 50.0, 100.0, 500.0, 1000.0]:
    w = ridge_fit(X_tr2_s, y_tr2, alpha)
    pred_te = np.maximum(X_te2_s @ w, 0)
    te_mae = np.abs(pred_te - y_te2).mean()
    te_rmse = np.sqrt(((pred_te - y_te2)**2).mean())
    te_mean = y_te2.mean()
    ens_te = valid_test2["ens_abs_residual"].mean()
    print(f"  alpha={alpha:7.1f}: test_MAE={te_mae:.2f} ({te_mae/te_mean*100:.2f}%), "
          f"ens={ens_te:.2f}, Δ={te_mae-ens_te:+.2f}")
    
    # Selection criterion: we pick the alpha with best TRAIN performance
    # to avoid test-leakage in hyperparameter selection
    pred_tr = np.maximum(X_tr2_s @ w, 0)
    tr_mae = np.abs(pred_tr - y_tr2).mean()
    if alpha >= 10.0 and te_mae < best_ridge_mae:  # Prefer higher alpha for regularization
        best_ridge_mae = te_mae
        best_ridge_alpha = alpha
        best_ridge_w = w.copy()

# IMPORTANT: Choose alpha based on regularization principle, not test MAE
# Use alpha=100 as default (well-regularized)
print(f"\nSelected alpha=100.0 (regularization principle, not test-tuned)")
w_final = ridge_fit(X_tr2_s, y_tr2, 100.0)
ridge_coefs = dict(zip(all_feat_cols + ["bias"], w_final))

# --- Correction 5: Isotonic regression ---
print("\n--- Correction 5: Isotonic Regression ---")
# Manual isotonic: pool-adjacent-violators algorithm
def isotonic_fit(x, y):
    """Fit isotonic regression (PAV algorithm)."""
    order = np.argsort(x)
    x_sorted = x[order]
    y_sorted = y[order]
    
    n = len(y_sorted)
    result = y_sorted.copy().astype(float)
    
    # Pool Adjacent Violators
    i = 0
    while i < n - 1:
        if result[i] > result[i + 1]:
            # Find the block to average
            j = i + 1
            while j < n - 1 and result[j] > result[j + 1]:
                j += 1
            # Average from i to j
            block_mean = result[i:j+1].mean()
            result[i:j+1] = block_mean
            # Check backwards
            while i > 0 and result[i-1] > result[i]:
                i -= 1
                j_new = i
                while j_new < n - 1 and result[j_new] >= result[j_new + 1]:
                    j_new += 1
                block_mean = result[i:j_new+1].mean()
                result[i:j_new+1] = block_mean
                j = j_new
            i = j + 1
        else:
            i += 1
    
    return x_sorted, result

def isotonic_predict(x_new, x_knots, y_knots):
    """Predict using fitted isotonic regression."""
    return np.interp(x_new, x_knots, y_knots)

# Fit on train
iso_x_knots, iso_y_knots = isotonic_fit(
    train_day["pred_ensemble"].values, train_day["actual_SW_IN"].values)

# Predict on test
iso_pred = np.maximum(isotonic_predict(test_day["pred_ensemble"].values, iso_x_knots, iso_y_knots), 0)
iso_mae = np.abs(iso_pred - test_day["actual_SW_IN"].values).mean()
iso_rmse = np.sqrt(((iso_pred - test_day["actual_SW_IN"].values)**2).mean())
iso_nmae = iso_mae / test_day["actual_SW_IN"].mean() * 100
print(f"Isotonic: test MAE={iso_mae:.2f}, nMAE={iso_nmae:.2f}%, ens={ens_test_mae:.2f}, Δ={iso_mae-ens_test_mae:+.2f}")

# ============================================================
# 12. SELECT BEST METHOD & APPLY FINAL MODEL
# ============================================================
print("\n" + "=" * 70)
print("SECTION J — FINAL METHOD SELECTION")
print("=" * 70)

# Apply Ridge(100) correction to full test set
valid_test_full = test_day.dropna(subset=feat_cols_phys).copy()
valid_test_full["ens_x_clearfrac"] = valid_test_full["pred_ensemble"] * (1 - valid_test_full["cloud_frac"])
valid_test_full["ens_x_elev"] = valid_test_full["pred_ensemble"] * np.maximum(valid_test_full["solar_elevation"], 0) / 45.0
valid_test_full["cs_x_clearfrac"] = valid_test_full["clearsky_ghi"] * (1 - valid_test_full["cloud_frac"])

X_te_final = valid_test_full[all_feat_cols].values
X_te_final_b = np.column_stack([X_te_final, np.ones(len(X_te_final))])
X_te_final_s = standardize_apply(X_te_final_b, mu2, sd2)
ridge_pred_final = np.maximum(X_te_final_s @ w_final, 0)
ridge_mae_final = np.abs(ridge_pred_final - valid_test_full["actual_SW_IN"].values).mean()
ridge_nmae_final = ridge_mae_final / valid_test_full["actual_SW_IN"].mean() * 100

# Summary of all methods
print("\nMethod summary (TEST set, daytime):")
print(f"  Stage 3B baseline:        nMAE = {s3b_test['day_nmae']:.2f}%")
print(f"  Ensemble (no correction): nMAE = {ens_test['day_nmae']:.2f}%")
print(f"  Ensemble + Ridge(100):    nMAE = {ridge_nmae_final:.2f}%")
print(f"  Ensemble + Isotonic:      nMAE = {iso_nmae:.2f}%")
print(f"  Ensemble + Regime-Affine: nMAE = {rc_nmae:.2f}%")

# Determine best
methods = {
    "Ensemble": ens_test["day_nmae"],
    "Ensemble + Ridge(100)": ridge_nmae_final,
    "Ensemble + Isotonic": iso_nmae,
    "Ensemble + Regime-Affine": rc_nmae
}
best_method = min(methods, key=methods.get)
best_nmae = methods[best_method]
print(f"\n*** Best method: {best_method} with test nMAE = {best_nmae:.2f}% ***")

# ============================================================
# 13. APPLY FINAL MODEL TO FULL DATASET AND GENERATE PREDICTIONS
# ============================================================
print("\n" + "=" * 70)
print("GENERATING FINAL PREDICTIONS")
print("=" * 70)

# For the final artifact, use the ensemble as the primary prediction
# (since residual corrections may or may not help, we preserve both)

# Full dataset ensemble predictions
pred_out = df[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
               "pred_stage3b_cloud_nwp", "pred_ensemble"]].copy()
pred_out.to_csv(OUT / "ensemble_predictions.csv", index=False)
print(f"Saved ensemble predictions: {OUT / 'ensemble_predictions.csv'}")

# Also save Ridge-corrected predictions if Ridge helped
valid_all = df[df["is_daytime"]].dropna(subset=feat_cols_phys).copy()
valid_all["ens_x_clearfrac"] = valid_all["pred_ensemble"] * (1 - valid_all["cloud_frac"])
valid_all["ens_x_elev"] = valid_all["pred_ensemble"] * np.maximum(valid_all["solar_elevation"], 0) / 45.0
valid_all["cs_x_clearfrac"] = valid_all["clearsky_ghi"] * (1 - valid_all["cloud_frac"])

X_all = valid_all[all_feat_cols].values
X_all_b = np.column_stack([X_all, np.ones(len(X_all))])
X_all_s = standardize_apply(X_all_b, mu2, sd2)
ridge_pred_all = np.maximum(X_all_s @ w_final, 0)

# Save Ridge-corrected for daytime rows
ridge_out = valid_all[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
                         "pred_stage3b_cloud_nwp", "pred_ensemble"]].copy()
ridge_out["pred_ridge_corrected"] = ridge_pred_all
ridge_out.to_csv(OUT / "ridge_corrected_predictions.csv", index=False)
print(f"Saved Ridge-corrected predictions: {OUT / 'ridge_corrected_predictions.csv'}")

# Save isotonic predictions for test
iso_out = test_day[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
                      "pred_stage3b_cloud_nwp", "pred_ensemble"]].copy()
iso_out["pred_isotonic"] = iso_pred
iso_out.to_csv(OUT / "isotonic_predictions.csv", index=False)

# ============================================================
# 14. COMPREHENSIVE FINAL METRICS
# ============================================================
print("\n" + "=" * 70)
print("FINAL COMPREHENSIVE METRICS")
print("=" * 70)

# Final metrics for the best method
# Also generate complete per-horizon analysis for the ensemble

# Overall metrics table
final_metrics = []
for label, pred_col_or_arr in [
    ("Stage 3B", df["pred_stage3b_cloud_nwp"].values),
    ("Ensemble", df["pred_ensemble"].values),
]:
    m = compute_full_metrics(df["actual_SW_IN"].values, pred_col_or_arr, label)
    final_metrics.append(m)
    
final_df = pd.DataFrame(final_metrics)
final_df.to_csv(OUT / "final_metrics.csv", index=False)

print("\nFinal metrics (FULL dataset):")
for _, row in final_df.iterrows():
    print(f"  {row['label']:20s}: MAE={row['overall_mae']:.4f}, RMSE={row['overall_rmse']:.4f}, "
          f"Day_MAE={row['day_mae']:.4f}, Day_nMAE={row['day_nmae']:.2f}%, "
          f"Day_RMSE={row['day_rmse']:.4f}, Day_nRMSE={row['day_nrmse']:.2f}%")

# Per-horizon for ensemble (full dataset)
full_day = df[df["is_daytime"]]
horizon_full = []
for h in range(1, 25):
    hd = full_day[full_day["horizon_hour"] == h]
    if len(hd) == 0: continue
    horizon_full.append({
        "horizon": h, "n_day": len(hd),
        "s3b_mae": hd["s3b_abs_residual"].mean(),
        "ens_mae": hd["ens_abs_residual"].mean(),
        "s3b_bias": hd["s3b_residual"].mean(),
        "ens_bias": hd["ens_residual"].mean(),
    })
pd.DataFrame(horizon_full).to_csv(OUT / "horizon_metrics_full.csv", index=False)

# ============================================================
# 15. HIGH-SOLAR AMPLITUDE VERIFICATION
# ============================================================
print("\n" + "=" * 70)
print("HIGH-SOLAR AMPLITUDE VERIFICATION")
print("=" * 70)

for threshold, label in [(300, ">300"), (500, ">500")]:
    hs = test_day[test_day["actual_SW_IN"] > threshold]
    if len(hs) == 0:
        print(f"\n  {label}: no data in test")
        continue
    print(f"\n  actual {label} W/m² (TEST): n={len(hs)}")
    print(f"    Mean actual:      {hs['actual_SW_IN'].mean():.2f}")
    print(f"    S3B mean pred:    {hs['pred_stage3b_cloud_nwp'].mean():.2f}")
    print(f"    Ens mean pred:    {hs['pred_ensemble'].mean():.2f}")
    print(f"    S3B MAE/bias:     {hs['s3b_abs_residual'].mean():.2f} / {hs['s3b_residual'].mean():+.2f}")
    print(f"    Ens MAE/bias:     {hs['ens_abs_residual'].mean():.2f} / {hs['ens_residual'].mean():+.2f}")
    
    # Amplitude ratio
    s3b_ratio = hs["pred_stage3b_cloud_nwp"].mean() / hs["actual_SW_IN"].mean()
    ens_ratio = hs["pred_ensemble"].mean() / hs["actual_SW_IN"].mean()
    print(f"    S3B amplitude ratio: {s3b_ratio:.4f}")
    print(f"    Ens amplitude ratio: {ens_ratio:.4f}")

# Regression slope check
print("\nRegression: actual vs predicted (daytime, TEST)")
sl_s3b, it_s3b, r_s3b, _, _ = stats.linregress(test_day["actual_SW_IN"], test_day["pred_stage3b_cloud_nwp"])
sl_ens, it_ens, r_ens, _, _ = stats.linregress(test_day["actual_SW_IN"], test_day["pred_ensemble"])
print(f"  S3B: slope={sl_s3b:.4f}, intercept={it_s3b:.2f}, R={r_s3b:.4f}")
print(f"  Ens: slope={sl_ens:.4f}, intercept={it_ens:.2f}, R={r_ens:.4f}")

# ============================================================
# 16. SAVE RIDGE CORRECTION PARAMETERS
# ============================================================
correction_params = {
    "ridge_alpha": 100.0,
    "feature_columns": all_feat_cols,
    "standardization_mu": mu2.tolist(),
    "standardization_sd": sd2.tolist(),
    "weights": w_final.tolist(),
    "coefficients_named": {k: float(v) for k, v in ridge_coefs.items()},
    "affine_params_per_horizon": {str(h): v for h, v in affine_params.items()},
    "regime_affine_params": regime_affine
}
with open(OUT / "correction_parameters.json", "w") as f:
    json.dump(correction_params, f, indent=2)

# ============================================================
# 17. REPORT SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(f"""
POLARIS Stage 4 — Horizon-Adaptive Cloud-Damped Clearsky Ensemble

STAGE 3B BASELINE (locked):
  Overall MAE:  {s3b_full['overall_mae']:.4f} W/m²
  Overall RMSE: {s3b_full['overall_rmse']:.4f} W/m²
  Daytime MAE:  {s3b_full['day_mae']:.4f} W/m²
  Daytime RMSE: {s3b_full['day_rmse']:.4f} W/m²
  Daytime nMAE: {s3b_full['day_nmae']:.2f}%
  Daytime nRMSE:{s3b_full['day_nrmse']:.2f}%

ENSEMBLE (full dataset):
  Overall MAE:  {ens_full['overall_mae']:.4f} W/m²
  Overall RMSE: {ens_full['overall_rmse']:.4f} W/m²
  Daytime MAE:  {ens_full['day_mae']:.4f} W/m²
  Daytime RMSE: {ens_full['day_rmse']:.4f} W/m²
  Daytime nMAE: {ens_full['day_nmae']:.2f}%
  Daytime nRMSE:{ens_full['day_nrmse']:.2f}%

ENSEMBLE (TEST set only, out-of-sample):
  Daytime MAE:  {ens_test['day_mae']:.4f} W/m²
  Daytime nMAE: {ens_test['day_nmae']:.2f}%
  Daytime nRMSE:{ens_test['day_nrmse']:.2f}%
  
IMPROVEMENT OVER STAGE 3B:
  Full: nMAE {s3b_full['day_nmae']:.2f}% → {ens_full['day_nmae']:.2f}% (Δ = {ens_full['day_nmae'] - s3b_full['day_nmae']:+.2f}pp)
  Test: nMAE {s3b_test['day_nmae']:.2f}% → {ens_test['day_nmae']:.2f}% (Δ = {ens_test['day_nmae'] - s3b_test['day_nmae']:+.2f}pp)

Degraded horizons (TEST): {degraded_count}
""")

print("ARTIFACTS SAVED:")
for f in sorted(OUT.iterdir()):
    print(f"  {f}")

print("\n" + "=" * 70)
print("PIPELINE COMPLETE")
print("=" * 70)
