#!/usr/bin/env python3
"""
POLARIS Stage 3B — Forensic Error Decomposition
=================================================
Reads LOCKED Stage 3B predictions + clear-sky + NWP data.
Produces comprehensive residual analysis by 14+ axes.
Does NOT modify any Stage 3 artifacts.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json, sys, warnings
warnings.filterwarnings("ignore")

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT = BASE / "forecasting/stage3" / "forensic_output"
OUT.mkdir(exist_ok=True)

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
print("=" * 60)
print("LOADING DATA")
print("=" * 60)

# Stage 3B predictions
pred = pd.read_csv(BASE / "forecasting/stage3" / "stage3b_cloud_nwp_predictions.csv")
pred["timestamp"] = pd.to_datetime(pred["timestamp"])
pred["forecast_start"] = pd.to_datetime(pred["forecast_start"])
print(f"Predictions: {len(pred)} rows, {pred['forecast_start'].nunique()} origins")

# Clear-sky decomposition
cs = pd.read_csv(BASE / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
print(f"Clear-sky: {len(cs)} rows, columns: {list(cs.columns)}")

# NWP forecasts
nwp = pd.read_csv(BASE / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv")
nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])
print(f"NWP: {len(nwp)} rows, columns: {list(nwp.columns)}")

# ============================================================
# 2. MERGE ALL DATA ONTO PREDICTIONS
# ============================================================
# Merge clear-sky by timestamp (drop duplicate actual_SW_IN from cs)
cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
df = pred.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left")
df.drop(columns=["TIMESTAMP"], inplace=True)

# Merge NWP by forecast_start + horizon_hour (only NWP-specific columns)
df = df.merge(
    nwp[["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m",
         "fc_relative_humidity_2m", "fc_precipitation", "fc_surface_pressure",
         "fc_wind_speed_10m"]],
    on=["forecast_start", "horizon_hour"],
    how="left"
)

print(f"\nMerged dataset: {len(df)} rows")
print(f"NaN counts:\n{df.isna().sum()}")

# ============================================================
# 3. COMPUTE RESIDUALS AND DERIVED COLUMNS
# ============================================================
df["residual"] = df["pred_stage3b_cloud_nwp"] - df["actual_SW_IN"]
df["abs_residual"] = df["residual"].abs()
df["sq_residual"] = df["residual"] ** 2

# Daytime flag
df["is_daytime"] = df["actual_SW_IN"] > 0

# Month / Season
df["month"] = df["timestamp"].dt.month
season_map = {12: "DJF", 1: "DJF", 2: "DJF",
              3: "MAM", 4: "MAM", 5: "MAM",
              6: "JJA", 7: "JJA", 8: "JJA",
              9: "SON", 10: "SON", 11: "SON"}
df["season"] = df["month"].map(season_map)

# Hour of day
df["hour"] = df["timestamp"].dt.hour

# Solar regime bins
def solar_regime(x):
    if x == 0:
        return "Night (0)"
    elif x <= 50:
        return "Twilight (0-50]"
    elif x <= 100:
        return "Low (50-100]"
    elif x <= 200:
        return "Moderate (100-200]"
    elif x <= 300:
        return "Mod-High (200-300]"
    elif x <= 500:
        return "High (300-500]"
    else:
        return "Very High (>500)"

df["actual_regime"] = df["actual_SW_IN"].apply(solar_regime)
df["pred_regime"] = df["pred_stage3b_cloud_nwp"].apply(solar_regime)

# Solar elevation bins
def elev_bin(e):
    if e <= 0:
        return "Below horizon"
    elif e <= 10:
        return "0-10°"
    elif e <= 20:
        return "10-20°"
    elif e <= 30:
        return "20-30°"
    elif e <= 40:
        return "30-40°"
    else:
        return ">40°"

df["elev_bin"] = df["solar_elevation"].apply(elev_bin)

# Cloud cover bins
def cloud_bin(c):
    if pd.isna(c):
        return "Missing"
    elif c <= 10:
        return "Clear (0-10%)"
    elif c <= 30:
        return "Few (10-30%)"
    elif c <= 60:
        return "Scattered (30-60%)"
    elif c <= 80:
        return "Broken (60-80%)"
    else:
        return "Overcast (80-100%)"

df["cloud_bin"] = df["fc_cloud_cover"].apply(cloud_bin)

# Clear-sky index (kt)
df["kt_actual"] = np.where(df["clearsky_ghi"] > 10, df["actual_SW_IN"] / df["clearsky_ghi"], np.nan)
df["kt_pred"] = np.where(df["clearsky_ghi"] > 10, df["pred_stage3b_cloud_nwp"] / df["clearsky_ghi"], np.nan)

# Rising vs falling solar
# Approximate: hours before/after solar noon (~12 UTC for this longitude)
# More precisely, mark the half of each day
df["is_rising"] = df["hour"] < 12  # before solar noon in UTC
df["solar_period"] = np.where(df["hour"] < 12, "Rising", "Falling")

# Sunrise/sunset proximity: daytime hours with solar elevation < 10°
df["is_near_transition"] = (df["solar_elevation"] > 0) & (df["solar_elevation"] < 10)

# Amplitude ratio
df["amplitude_ratio"] = np.where(
    df["actual_SW_IN"] > 10,
    df["pred_stage3b_cloud_nwp"] / df["actual_SW_IN"],
    np.nan
)

print("\nDerived columns computed.")
print(f"Daytime rows: {df['is_daytime'].sum()}")
print(f"Night rows: {(~df['is_daytime']).sum()}")

# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================
def compute_metrics(sub):
    """Compute MAE, RMSE, bias, n for a subset."""
    n = len(sub)
    if n == 0:
        return {"n": 0, "mae": np.nan, "rmse": np.nan, "bias": np.nan, "r": np.nan}
    mae = sub["abs_residual"].mean()
    rmse = np.sqrt(sub["sq_residual"].mean())
    bias = sub["residual"].mean()
    actual_std = sub["actual_SW_IN"].std()
    pred_std = sub["pred_stage3b_cloud_nwp"].std()
    if n >= 2 and actual_std > 0 and pred_std > 0:
        r = sub["actual_SW_IN"].corr(sub["pred_stage3b_cloud_nwp"])
    else:
        r = np.nan
    return {"n": n, "mae": mae, "rmse": rmse, "bias": bias, "r": r}

def metrics_by_group(group_col, daytime_only=False):
    """Compute metrics grouped by a column."""
    sub = df[df["is_daytime"]] if daytime_only else df
    results = []
    for name, grp in sub.groupby(group_col, sort=False):
        m = compute_metrics(grp)
        m[group_col] = name
        results.append(m)
    return pd.DataFrame(results)

# ============================================================
# 5. SECTION A — NORMALIZED METRICS
# ============================================================
print("\n" + "=" * 60)
print("SECTION A — NORMALIZED METRICS")
print("=" * 60)

day = df[df["is_daytime"]]
night = df[~df["is_daytime"]]
overall_mae = df["abs_residual"].mean()
overall_rmse = np.sqrt(df["sq_residual"].mean())
day_mae = day["abs_residual"].mean()
day_rmse = np.sqrt(day["sq_residual"].mean())
day_mean_actual = day["actual_SW_IN"].mean()
night_mae = night["abs_residual"].mean()
night_rmse = np.sqrt(night["sq_residual"].mean())

nmae_day = (day_mae / day_mean_actual) * 100
nrmse_day = (day_rmse / day_mean_actual) * 100

print(f"Overall MAE:    {overall_mae:.4f} W/m²")
print(f"Overall RMSE:   {overall_rmse:.4f} W/m²")
print(f"Daytime MAE:    {day_mae:.4f} W/m²")
print(f"Daytime RMSE:   {day_rmse:.4f} W/m²")
print(f"Night MAE:      {night_mae:.4f} W/m²")
print(f"Night RMSE:     {night_rmse:.4f} W/m²")
print(f"Mean daytime actual SW_IN: {day_mean_actual:.4f} W/m²")
print(f"nMAE_day:       {nmae_day:.2f}%")
print(f"nRMSE_day:      {nrmse_day:.2f}%")
print(f"Overall bias:   {df['residual'].mean():.4f} W/m²")
print(f"Daytime bias:   {day['residual'].mean():.4f} W/m²")

# ============================================================
# 6. SECTION B — ERROR DECOMPOSITION BY AXES
# ============================================================
print("\n" + "=" * 60)
print("SECTION B — ERROR DECOMPOSITION")
print("=" * 60)

# B1: By horizon
print("\n--- B1: By Horizon Hour ---")
h_metrics = metrics_by_group("horizon_hour")
h_metrics = h_metrics.sort_values("horizon_hour")
h_day = metrics_by_group("horizon_hour", daytime_only=True)
h_day = h_day.sort_values("horizon_hour")
h_day = h_day.rename(columns={"mae": "day_mae", "rmse": "day_rmse", "bias": "day_bias",
                                "n": "n_day", "r": "day_r"})
h_merged = h_metrics.merge(h_day[["horizon_hour", "n_day", "day_mae", "day_rmse", "day_bias", "day_r"]],
                           on="horizon_hour")
print(h_merged.to_string(index=False))
h_merged.to_csv(OUT / "B1_horizon_metrics.csv", index=False)

# B2: By Month
print("\n--- B2: By Month (daytime) ---")
m_day = metrics_by_group("month", daytime_only=True)
m_day = m_day.sort_values("month")
print(m_day.to_string(index=False))
m_day.to_csv(OUT / "B2_month_daytime_metrics.csv", index=False)

# B3: By Season
print("\n--- B3: By Season (daytime) ---")
s_day = metrics_by_group("season", daytime_only=True)
print(s_day.to_string(index=False))
s_day.to_csv(OUT / "B3_season_daytime_metrics.csv", index=False)

# B4: By Actual SW_IN Regime
print("\n--- B4: By Actual SW_IN Regime ---")
regime_order = ["Night (0)", "Twilight (0-50]", "Low (50-100]", "Moderate (100-200]",
                "Mod-High (200-300]", "High (300-500]", "Very High (>500)"]
r_met = metrics_by_group("actual_regime")
r_met["actual_regime"] = pd.Categorical(r_met["actual_regime"], categories=regime_order, ordered=True)
r_met = r_met.sort_values("actual_regime")
print(r_met.to_string(index=False))
r_met.to_csv(OUT / "B4_actual_regime_metrics.csv", index=False)

# B5: By Predicted SW_IN Regime
print("\n--- B5: By Predicted SW_IN Regime ---")
p_met = metrics_by_group("pred_regime")
p_met["pred_regime"] = pd.Categorical(p_met["pred_regime"], categories=regime_order, ordered=True)
p_met = p_met.sort_values("pred_regime")
print(p_met.to_string(index=False))
p_met.to_csv(OUT / "B5_pred_regime_metrics.csv", index=False)

# B6: By Solar Elevation
print("\n--- B6: By Solar Elevation (daytime) ---")
elev_order = ["0-10°", "10-20°", "20-30°", "30-40°", ">40°"]
e_met = metrics_by_group("elev_bin", daytime_only=True)
e_met["elev_bin"] = pd.Categorical(e_met["elev_bin"], categories=elev_order, ordered=True)
e_met = e_met.sort_values("elev_bin")
print(e_met.to_string(index=False))
e_met.to_csv(OUT / "B6_solar_elevation_metrics.csv", index=False)

# B7: By Clear-sky GHI bins (daytime)
print("\n--- B7: By Clear-sky GHI (daytime) ---")
day_cs = day.copy()
day_cs["cs_bin"] = pd.cut(day_cs["clearsky_ghi"],
                           bins=[0, 50, 100, 200, 400, 600, 1000],
                           labels=["0-50", "50-100", "100-200", "200-400", "400-600", ">600"])
cs_metrics = []
for name, grp in day_cs.groupby("cs_bin", observed=True):
    m = compute_metrics(grp)
    m["cs_bin"] = name
    cs_metrics.append(m)
cs_df = pd.DataFrame(cs_metrics)
print(cs_df.to_string(index=False))
cs_df.to_csv(OUT / "B7_clearsky_ghi_metrics.csv", index=False)

# B8: Amplitude analysis
print("\n--- B8: Actual vs Predicted Amplitude ---")
high_actual = day[day["actual_SW_IN"] > 300]
print(f"High-actual (>300 W/m²): n={len(high_actual)}")
print(f"  Mean actual:    {high_actual['actual_SW_IN'].mean():.2f}")
print(f"  Mean predicted: {high_actual['pred_stage3b_cloud_nwp'].mean():.2f}")
print(f"  Mean amplitude ratio: {high_actual['amplitude_ratio'].mean():.4f}")
print(f"  Median amplitude ratio: {high_actual['amplitude_ratio'].median():.4f}")
print(f"  MAE:            {high_actual['abs_residual'].mean():.2f}")
print(f"  Bias:           {high_actual['residual'].mean():.2f}")

vhigh_actual = day[day["actual_SW_IN"] > 500]
print(f"\nVery-high-actual (>500 W/m²): n={len(vhigh_actual)}")
print(f"  Mean actual:    {vhigh_actual['actual_SW_IN'].mean():.2f}")
print(f"  Mean predicted: {vhigh_actual['pred_stage3b_cloud_nwp'].mean():.2f}")
print(f"  Mean amplitude ratio: {vhigh_actual['amplitude_ratio'].mean():.4f}")
print(f"  Median amplitude ratio: {vhigh_actual['amplitude_ratio'].median():.4f}")
print(f"  MAE:            {vhigh_actual['abs_residual'].mean():.2f}")
print(f"  Bias:           {vhigh_actual['residual'].mean():.2f}")

# B9: By forecast cloud cover bin (daytime)
print("\n--- B9: By Forecast Cloud Cover (daytime) ---")
c_met = metrics_by_group("cloud_bin", daytime_only=True)
print(c_met.to_string(index=False))
c_met.to_csv(OUT / "B9_cloud_cover_metrics.csv", index=False)

# B10: Horizon x Solar Regime cross-table (daytime MAE)
print("\n--- B10: Horizon × Actual Regime (daytime MAE) ---")
day_copy = day.copy()
cross_table = day_copy.pivot_table(values="abs_residual", index="horizon_hour",
                                    columns="actual_regime", aggfunc="mean")
# Reorder columns
cross_cols = [c for c in regime_order if c in cross_table.columns]
cross_table = cross_table[cross_cols]
print(cross_table.to_string())
cross_table.to_csv(OUT / "B10_horizon_regime_cross.csv")

# B11: Rising vs Falling
print("\n--- B11: Rising vs Falling Solar (daytime) ---")
sp_met = metrics_by_group("solar_period", daytime_only=True)
print(sp_met.to_string(index=False))

# B12: Sunrise/Sunset Proximity
print("\n--- B12: Near Sunrise/Sunset (daytime) ---")
trans = day[day["is_near_transition"]]
non_trans = day[~day["is_near_transition"]]
print(f"Near transition (elev 0-10°):  n={len(trans)}, MAE={trans['abs_residual'].mean():.2f}, bias={trans['residual'].mean():.2f}")
print(f"Away from transition (elev>10°): n={len(non_trans)}, MAE={non_trans['abs_residual'].mean():.2f}, bias={non_trans['residual'].mean():.2f}")

# B13: Systematic Bias
print("\n--- B13: Systematic Bias Analysis ---")
# Bias by horizon
bias_h = df.groupby("horizon_hour")["residual"].agg(["mean", "std", "count"]).reset_index()
bias_h.columns = ["horizon_hour", "mean_bias", "std_bias", "n"]
print("\nBias by horizon (all hours):")
print(bias_h.to_string(index=False))
bias_h.to_csv(OUT / "B13_bias_by_horizon.csv", index=False)

# Bias by month (daytime)
bias_m = day.groupby("month")["residual"].agg(["mean", "std", "count"]).reset_index()
bias_m.columns = ["month", "mean_bias", "std_bias", "n"]
print("\nBias by month (daytime):")
print(bias_m.to_string(index=False))
bias_m.to_csv(OUT / "B13_bias_by_month_daytime.csv", index=False)

# B14: Regression statistics
print("\n--- B14: Regression Actual vs Predicted (daytime) ---")
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(day["actual_SW_IN"], day["pred_stage3b_cloud_nwp"])
print(f"slope     = {slope:.6f}")
print(f"intercept = {intercept:.4f}")
print(f"R²        = {r_value**2:.6f}")
print(f"R         = {r_value:.6f}")
print(f"p-value   = {p_value:.2e}")
print(f"std_err   = {std_err:.6f}")

# Residual vs actual
slope_ra, intercept_ra, r_ra, p_ra, se_ra = stats.linregress(day["actual_SW_IN"], day["residual"])
print(f"\nResidual vs Actual (daytime):")
print(f"slope     = {slope_ra:.6f}")
print(f"intercept = {intercept_ra:.4f}")
print(f"R         = {r_ra:.6f}")

# Residual vs predicted
slope_rp, intercept_rp, r_rp, p_rp, se_rp = stats.linregress(day["pred_stage3b_cloud_nwp"], day["residual"])
print(f"\nResidual vs Predicted (daytime):")
print(f"slope     = {slope_rp:.6f}")
print(f"intercept = {intercept_rp:.4f}")
print(f"R         = {r_rp:.6f}")

# Residual vs solar elevation (daytime)
valid_se = day.dropna(subset=["solar_elevation"])
slope_rse, intercept_rse, r_rse, p_rse, se_rse = stats.linregress(valid_se["solar_elevation"], valid_se["residual"])
print(f"\nResidual vs Solar Elevation (daytime):")
print(f"slope     = {slope_rse:.6f}")
print(f"intercept = {intercept_rse:.4f}")
print(f"R         = {r_rse:.6f}")

# ============================================================
# 7. AMPLITUDE COMPRESSION TEST
# ============================================================
print("\n" + "=" * 60)
print("SECTION C — AMPLITUDE COMPRESSION TEST")
print("=" * 60)

# Per-origin amplitude analysis
per_origin_amp = []
for origin, grp in pred.groupby("forecast_start"):
    day_grp = grp[grp["actual_SW_IN"] > 0]
    if len(day_grp) > 0:
        actual_peak = day_grp["actual_SW_IN"].max()
        pred_peak = day_grp["pred_stage3b_cloud_nwp"].max()
        actual_mean = day_grp["actual_SW_IN"].mean()
        pred_mean = day_grp["pred_stage3b_cloud_nwp"].mean()
        per_origin_amp.append({
            "origin": origin,
            "actual_peak": actual_peak,
            "pred_peak": pred_peak,
            "peak_ratio": pred_peak / actual_peak if actual_peak > 0 else np.nan,
            "actual_mean_day": actual_mean,
            "pred_mean_day": pred_mean,
            "mean_ratio": pred_mean / actual_mean if actual_mean > 0 else np.nan,
            "n_day": len(day_grp)
        })

amp_df = pd.DataFrame(per_origin_amp)
print(f"Total forecast origins with daytime: {len(amp_df)}")
print(f"\nPeak amplitude ratio (pred_peak / actual_peak):")
print(f"  Mean:   {amp_df['peak_ratio'].mean():.4f}")
print(f"  Median: {amp_df['peak_ratio'].median():.4f}")
print(f"  Std:    {amp_df['peak_ratio'].std():.4f}")
print(f"  Min:    {amp_df['peak_ratio'].min():.4f}")
print(f"  Max:    {amp_df['peak_ratio'].max():.4f}")

# How often does the model underpredict the peak?
under_peak = (amp_df["peak_ratio"] < 0.9).sum()
over_peak = (amp_df["peak_ratio"] > 1.1).sum()
within_peak = ((amp_df["peak_ratio"] >= 0.9) & (amp_df["peak_ratio"] <= 1.1)).sum()
print(f"\nPeak underprediction (<90%): {under_peak}/{len(amp_df)} ({100*under_peak/len(amp_df):.1f}%)")
print(f"Peak overprediction  (>110%): {over_peak}/{len(amp_df)} ({100*over_peak/len(amp_df):.1f}%)")
print(f"Peak within ±10%:             {within_peak}/{len(amp_df)} ({100*within_peak/len(amp_df):.1f}%)")

# For clear-sky days
amp_df_cs = amp_df.merge(
    df.groupby("forecast_start").agg(
        mean_cloud=("fc_cloud_cover", "mean"),
        max_clearsky=("clearsky_ghi", "max")
    ).reset_index(),
    left_on="origin", right_on="forecast_start", how="left"
)

clear_days = amp_df_cs[amp_df_cs["mean_cloud"] <= 20]
cloudy_days = amp_df_cs[amp_df_cs["mean_cloud"] > 60]
print(f"\nClear-sky days (mean cloud ≤20%): n={len(clear_days)}")
if len(clear_days) > 0:
    print(f"  Mean peak ratio: {clear_days['peak_ratio'].mean():.4f}")
    print(f"  Median peak ratio: {clear_days['peak_ratio'].median():.4f}")
print(f"Cloudy days (mean cloud >60%): n={len(cloudy_days)}")
if len(cloudy_days) > 0:
    print(f"  Mean peak ratio: {cloudy_days['peak_ratio'].mean():.4f}")
    print(f"  Median peak ratio: {cloudy_days['peak_ratio'].median():.4f}")

amp_df_cs.to_csv(OUT / "C_per_origin_amplitude.csv", index=False)

# ============================================================
# 8. SECTION D — HORIZON-DEPENDENT BIAS STRUCTURE
# ============================================================
print("\n" + "=" * 60)
print("SECTION D — HORIZON × BIAS STRUCTURE")
print("=" * 60)

# For each horizon, compute bias conditional on actual regime (daytime)
hb = day.pivot_table(values="residual", index="horizon_hour",
                     columns="actual_regime", aggfunc="mean")
hb_cols = [c for c in regime_order if c in hb.columns]
hb = hb[hb_cols]
print("Mean Bias by Horizon × Actual Regime (daytime):")
print(hb.to_string())
hb.to_csv(OUT / "D_horizon_regime_bias.csv")

# ============================================================
# 9. SECTION E — QUANTILE ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("SECTION E — QUANTILE ANALYSIS (daytime)")
print("=" * 60)

quantiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
q_actual = day["actual_SW_IN"].quantile(quantiles)
q_pred = day["pred_stage3b_cloud_nwp"].quantile(quantiles)

qdf = pd.DataFrame({"quantile": quantiles, "actual": q_actual.values, "predicted": q_pred.values})
qdf["ratio"] = qdf["predicted"] / qdf["actual"]
print(qdf.to_string(index=False))
qdf.to_csv(OUT / "E_quantile_analysis.csv", index=False)

# ============================================================
# 10. SECTION F — CALIBRATION OPPORTUNITY SIZING
# ============================================================
print("\n" + "=" * 60)
print("SECTION F — CALIBRATION OPPORTUNITY SIZING")
print("=" * 60)

# How much error could a perfect affine calibration remove?
# Fit y = a*x + b on daytime
perfect_fitted = slope * day["actual_SW_IN"] + intercept
# Reverse: if we knew actual = (pred - intercept) / slope
# calibrated = (pred - intercept) / slope
calibrated_pred = (day["pred_stage3b_cloud_nwp"].values - intercept) / slope
cal_residual = calibrated_pred - day["actual_SW_IN"].values
cal_mae = np.abs(cal_residual).mean()
cal_rmse = np.sqrt((cal_residual**2).mean())
cal_nmae = (cal_mae / day_mean_actual) * 100

print(f"Current daytime MAE:  {day_mae:.4f}")
print(f"Current daytime RMSE: {day_rmse:.4f}")
print(f"Current nMAE:         {nmae_day:.2f}%")
print(f"\nAffine-calibrated daytime MAE:  {cal_mae:.4f}")
print(f"Affine-calibrated daytime RMSE: {cal_rmse:.4f}")
print(f"Affine-calibrated nMAE:         {cal_nmae:.2f}%")
print(f"\nPotential MAE reduction from global affine: {day_mae - cal_mae:.4f} ({(1-cal_mae/day_mae)*100:.2f}%)")

# Horizon-specific affine calibration
print("\nHorizon-specific affine calibration:")
hs_results = []
for h in range(1, 25):
    h_day_sub = day[day["horizon_hour"] == h]
    if len(h_day_sub) < 10:
        continue
    h_slope, h_int, _, _, _ = stats.linregress(h_day_sub["actual_SW_IN"], h_day_sub["pred_stage3b_cloud_nwp"])
    h_cal = (h_day_sub["pred_stage3b_cloud_nwp"].values - h_int) / h_slope if abs(h_slope) > 1e-10 else h_day_sub["pred_stage3b_cloud_nwp"].values
    h_cal_mae = np.abs(h_cal - h_day_sub["actual_SW_IN"].values).mean()
    h_orig_mae = h_day_sub["abs_residual"].mean()
    hs_results.append({
        "horizon": h, "n_day": len(h_day_sub),
        "orig_mae": h_orig_mae, "cal_mae": h_cal_mae,
        "reduction_pct": (1 - h_cal_mae/h_orig_mae)*100 if h_orig_mae > 0 else 0,
        "slope": h_slope, "intercept": h_int
    })
hs_df = pd.DataFrame(hs_results)
print(hs_df.to_string(index=False))
hs_df.to_csv(OUT / "F_horizon_affine_calibration.csv", index=False)

# ============================================================
# 11. SECTION G — MONTH-SPECIFIC ERROR PATTERNS
# ============================================================
print("\n" + "=" * 60)
print("SECTION G — MONTHLY ERROR (daytime)")
print("=" * 60)

for m in sorted(day["month"].unique()):
    mdf = day[day["month"] == m]
    mean_act = mdf["actual_SW_IN"].mean()
    mae_m = mdf["abs_residual"].mean()
    rmse_m = np.sqrt(mdf["sq_residual"].mean())
    bias_m2 = mdf["residual"].mean()
    nmae_m = (mae_m / mean_act * 100) if mean_act > 0 else np.nan
    print(f"Month {m:2d}: n={len(mdf):5d}, mean_actual={mean_act:7.2f}, MAE={mae_m:7.2f}, "
          f"RMSE={rmse_m:7.2f}, bias={bias_m2:+7.2f}, nMAE={nmae_m:6.2f}%")

# ============================================================
# 12. SECTION H — FEATURE CORRELATION WITH ERROR
# ============================================================
print("\n" + "=" * 60)
print("SECTION H — FEATURE CORRELATION WITH ABS ERROR")
print("=" * 60)

features_to_test = ["actual_SW_IN", "pred_stage3b_cloud_nwp", "horizon_hour",
                    "solar_elevation", "clearsky_ghi", "fc_cloud_cover",
                    "fc_temperature_2m", "fc_relative_humidity_2m",
                    "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"]

print("\nCorrelation of |residual| with features (daytime):")
for feat in features_to_test:
    valid = day.dropna(subset=[feat, "abs_residual"])
    if len(valid) < 10:
        print(f"  {feat:30s}: insufficient data")
        continue
    r_val, p_val = stats.pearsonr(valid[feat], valid["abs_residual"])
    rho, p_rho = stats.spearmanr(valid[feat], valid["abs_residual"])
    print(f"  {feat:30s}: pearson={r_val:+.4f} (p={p_val:.2e}), spearman={rho:+.4f} (p={p_rho:.2e})")

# ============================================================
# 13. SECTION I — kt DECOMPOSITION
# ============================================================
print("\n" + "=" * 60)
print("SECTION I — CLEAR-SKY INDEX (kt) DECOMPOSITION")
print("=" * 60)

day_kt = day.dropna(subset=["kt_actual", "kt_pred"])
print(f"Valid kt pairs: {len(day_kt)}")

if len(day_kt) > 0:
    kt_residual = day_kt["kt_pred"] - day_kt["kt_actual"]
    print(f"kt residual: mean={kt_residual.mean():.4f}, std={kt_residual.std():.4f}")
    print(f"kt actual: mean={day_kt['kt_actual'].mean():.4f}, std={day_kt['kt_actual'].std():.4f}")
    print(f"kt pred:   mean={day_kt['kt_pred'].mean():.4f}, std={day_kt['kt_pred'].std():.4f}")
    
    kt_bins = pd.cut(day_kt["kt_actual"], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5],
                      labels=["0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0", ">1.0"])
    for name, grp in day_kt.groupby(kt_bins, observed=True):
        if len(grp) < 5:
            continue
        kt_r = grp["kt_pred"] - grp["kt_actual"]
        irr_r = grp["pred_stage3b_cloud_nwp"] - grp["actual_SW_IN"]
        print(f"  kt_bin={name}: n={len(grp)}, kt_bias={kt_r.mean():+.4f}, "
              f"irr_MAE={irr_r.abs().mean():.2f}, irr_bias={irr_r.mean():+.2f}")

# ============================================================
# 14. SAVE MASTER RESIDUAL CSV
# ============================================================
cols_to_save = ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
                "pred_stage3b_cloud_nwp", "residual", "abs_residual", "is_daytime",
                "month", "season", "hour", "actual_regime", "pred_regime",
                "solar_elevation", "clearsky_ghi", "kt_actual", "kt_pred",
                "fc_cloud_cover", "fc_temperature_2m", "cloud_bin", "elev_bin",
                "solar_period", "is_near_transition", "amplitude_ratio"]
df[cols_to_save].to_csv(OUT / "master_residual_dataset.csv", index=False)
print(f"\nMaster residual dataset saved: {OUT / 'master_residual_dataset.csv'}")

# ============================================================
# 15. TEMPORAL SPLIT DESIGN
# ============================================================
print("\n" + "=" * 60)
print("SECTION J — TEMPORAL SPLIT FOR CALIBRATION")
print("=" * 60)

origins = sorted(df["forecast_start"].unique())
n_origins = len(origins)
print(f"Total origins: {n_origins}")

# Strict temporal split: first 60% train, next 20% val, last 20% test
train_end = int(n_origins * 0.6)
val_end = int(n_origins * 0.8)

train_origins = origins[:train_end]
val_origins = origins[train_end:val_end]
test_origins = origins[val_end:]

print(f"Train: {len(train_origins)} origins, {pd.Timestamp(train_origins[0]).date()} to {pd.Timestamp(train_origins[-1]).date()}")
print(f"Val:   {len(val_origins)} origins, {pd.Timestamp(val_origins[0]).date()} to {pd.Timestamp(val_origins[-1]).date()}")
print(f"Test:  {len(test_origins)} origins, {pd.Timestamp(test_origins[0]).date()} to {pd.Timestamp(test_origins[-1]).date()}")

# Count daytime hours in each split
for split_name, split_origins in [("Train", train_origins), ("Val", val_origins), ("Test", test_origins)]:
    split_df = df[df["forecast_start"].isin(split_origins)]
    day_split = split_df[split_df["is_daytime"]]
    print(f"  {split_name}: total={len(split_df)}, daytime={len(day_split)}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
