import os
import pandas as pd
import numpy as np
import scipy.stats as stats

# ============================================================
# POLARIS — Stage 2: NWP Forecast Skill Analysis (AUDITED & VALIDATED)
#
# Dataset: data/POLARIS_v0_1_future_weather_forecasts_2024.csv
# Coverage: 347 PASS forecast origins (8,328 total hours)
# Target: SITES Nuolja ground-truth actual_SW_IN & clear-sky index kt
# ============================================================

NWP_DATASET = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2024.csv"
DECOMP_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv"
OUTPUT_SUMMARY_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_skill_summary.csv"
OUTPUT_HORIZON_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_skill_horizon.csv"
OUTPUT_SEASONAL_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_skill_seasonal.csv"

def compute_stat_pair(x, y):
    """
    Computes Pearson r, Spearman rho, n, NaNs removed, and variances with strict safeguards.
    Explicitly handles zero-variance cases and asserts r, rho in [-1.0, +1.0].
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isinf(x) & ~np.isinf(y)
    n_removed = len(x) - np.sum(mask)
    x_valid = x[mask]
    y_valid = y[mask]
    n = len(x_valid)

    if n < 2:
        return np.nan, np.nan, n, n_removed, 0.0, 0.0

    var_x = np.var(x_valid, ddof=1)
    var_y = np.var(y_valid, ddof=1)

    if var_x == 0.0 or var_y == 0.0:
        return np.nan, np.nan, n, n_removed, var_x, var_y

    r, _ = stats.pearsonr(x_valid, y_valid)
    rho, _ = stats.spearmanr(x_valid, y_valid)

    # Hard Validation Safeguards
    assert np.isnan(r) or (-1.0 <= r <= 1.0), f"CRITICAL: Impossible Pearson r = {r}"
    assert np.isnan(rho) or (-1.0 <= rho <= 1.0), f"CRITICAL: Impossible Spearman rho = {rho}"

    return r, rho, n, n_removed, var_x, var_y

def main():
    print("=" * 85)
    print("POLARIS — Stage 2: NWP Forecast Skill Analysis (Audited & Validated)")
    print("=" * 85)

    # 1. Load NWP dataset
    df = pd.read_csv(NWP_DATASET)
    print(f"Loaded NWP Dataset Rows: {len(df)}")
    assert len(df) == 8328, f"Expected 8328 rows, got {len(df)}"

    # Audit NWP timestamps & origins
    assert df["timestamp"].nunique() == 8328, "Duplicate NWP timestamps found!"
    assert df["forecast_start"].nunique() == 347, "Unexpected forecast origins count!"
    assert df["horizon_hour"].value_counts().nunique() == 1, "Unequal distribution of horizons!"

    df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
    df["forecast_start"] = pd.to_datetime(df["forecast_start"])

    # 2. Merge clear-sky index kt from clear-sky decomposition file
    assert os.path.exists(DECOMP_FILE), f"Decomposition file missing: {DECOMP_FILE}"
    decomp = pd.read_csv(DECOMP_FILE)
    print(f"Loaded Clear-Sky Decomposition Rows: {len(decomp)}")
    assert decomp["TIMESTAMP"].nunique() == len(decomp), "Duplicate timestamps in decomposition file!"

    decomp["timestamp_dt"] = pd.to_datetime(decomp["TIMESTAMP"])
    
    # Perform strict 1-to-1 merge
    df = df.merge(decomp[["timestamp_dt", "kt", "clearsky_ghi", "solar_elevation"]], on="timestamp_dt", how="left")
    print(f"Post-Merge Row Count: {len(df)}")
    assert len(df) == 8328, f"Merge row multiplication error! Expected 8328, got {len(df)}"
    assert df["kt"].isna().sum() == 0, "Missing kt values after merge!"

    actual = df["actual_SW_IN"].values
    daytime_mask = actual > 0.0

    variables = [
        ("fc_cloud_cover", "Total Cloud Cover (%)"),
        ("fc_temperature_2m", "2m Temperature (°C)"),
        ("fc_relative_humidity_2m", "2m Relative Humidity (%)"),
        ("fc_precipitation", "Precipitation (mm)"),
        ("fc_surface_pressure", "Surface Pressure (hPa)"),
        ("fc_wind_speed_10m", "10m Wind Speed (m/s)"),
    ]

    # 3. Overall & Daytime Correlation Analysis
    summary_list = []

    for var_col, var_name in variables:
        r_all, rho_all, n_all, nan_all, _, _ = compute_stat_pair(df[var_col], df["actual_SW_IN"])
        
        day_df = df[daytime_mask]
        r_day, rho_day, n_day, nan_day, _, _ = compute_stat_pair(day_df[var_col], day_df["actual_SW_IN"])

        r_kt_all, rho_kt_all, _, _, _, _ = compute_stat_pair(df[var_col], df["kt"])
        r_kt_day, rho_kt_day, _, _, _, _ = compute_stat_pair(day_df[var_col], day_df["kt"])

        summary_list.append({
            "variable_code": var_col,
            "variable_name": var_name,
            "n_overall": n_all,
            "n_daytime": n_day,
            "pearson_overall": r_all,
            "spearman_overall": rho_all,
            "pearson_daytime": r_day,
            "spearman_daytime": rho_day,
            "pearson_kt_overall": r_kt_all,
            "pearson_kt_daytime": r_kt_day,
            "spearman_kt_daytime": rho_kt_day,
        })

    summary_df = pd.DataFrame(summary_list)
    summary_df.to_csv(OUTPUT_SUMMARY_CSV, index=False)

    print("\n" + "=" * 90)
    print("1. OVERALL & DAYTIME CORRELATION SUMMARY (TARGET: SITES SW_IN & kt)")
    print("=" * 90)
    print(f"{'Variable':<28} | {'Overall r':<10} | {'Overall ρ':<10} | {'Daytime r':<10} | {'Daytime ρ':<10} | {'kt Daytime r':<12}")
    print("-" * 92)
    for _, r in summary_df.iterrows():
        print(f"{r['variable_name']:<28} | {r['pearson_overall']:<10.3f} | {r['spearman_overall']:<10.3f} | {r['pearson_daytime']:<10.3f} | {r['spearman_daytime']:<10.3f} | {r['pearson_kt_daytime']:<12.3f}")

    # 4. Horizon-by-Horizon Correlation (h = 1..24)
    horizon_list = []

    for h in range(1, 25):
        h_df = df[df["horizon_hour"] == h]
        h_day_df = h_df[h_df["actual_SW_IN"] > 0]

        row = {"horizon_hour": h, "n_overall": len(h_df), "n_daytime": len(h_day_df)}
        for var_col, _ in variables:
            r_all, rho_all, _, _, _, _ = compute_stat_pair(h_df[var_col], h_df["actual_SW_IN"])
            r_day, rho_day, _, _, _, _ = compute_stat_pair(h_day_df[var_col], h_day_df["actual_SW_IN"])

            row[f"{var_col}_r_overall"] = r_all
            row[f"{var_col}_rho_overall"] = rho_all
            row[f"{var_col}_r_daytime"] = r_day
            row[f"{var_col}_rho_daytime"] = rho_day

            if var_col == "fc_cloud_cover":
                r_kt_day, rho_kt_day, _, _, _, _ = compute_stat_pair(h_day_df["fc_cloud_cover"], h_day_df["kt"])
                row["cloud_kt_r_daytime"] = r_kt_day
                row["cloud_kt_rho_daytime"] = rho_kt_day

        horizon_list.append(row)

    horizon_df = pd.DataFrame(horizon_list)
    horizon_df.to_csv(OUTPUT_HORIZON_CSV, index=False)

    print("\n" + "=" * 90)
    print("2. HORIZON-BY-HORIZON DAYTIME CORRELATION (h = 1..24)")
    print("=" * 90)
    print(f"{'Horizon':<8} | {'Cloud Cover r':<14} | {'Cloud vs kt r':<14} | {'Temp r':<10} | {'RH r':<10} | {'Precip r':<10}")
    print("-" * 80)
    for _, r in horizon_df.iterrows():
        h_int = int(r['horizon_hour'])
        print(f"H{h_int:<7} | {r['fc_cloud_cover_r_daytime']:<14.3f} | {r['cloud_kt_r_daytime']:<14.3f} | {r['fc_temperature_2m_r_daytime']:<10.3f} | {r['fc_relative_humidity_2m_r_daytime']:<10.3f} | {r['fc_precipitation_r_daytime']:<10.3f}")

    # 5. Seasonal Breakdown (Spring, Summer, Autumn, Winter)
    def get_season(month):
        if month in [12, 1, 2]: return "Winter"
        elif month in [3, 4, 5]: return "Spring"
        elif month in [6, 7, 8]: return "Summer"
        else: return "Autumn"

    df["season"] = df["timestamp_dt"].dt.month.map(get_season)

    seasonal_list = []
    seasons = ["Spring", "Summer", "Autumn", "Winter"]

    for s in seasons:
        s_df = df[df["season"] == s]
        s_day_df = s_df[s_df["actual_SW_IN"] > 0]

        row = {"season": s, "total_hours": len(s_df), "daytime_hours": len(s_day_df)}
        for var_col, _ in variables:
            r_day, rho_day, _, _, _, _ = compute_stat_pair(s_day_df[var_col], s_day_df["actual_SW_IN"])
            row[f"{var_col}_r_daytime"] = r_day
            row[f"{var_col}_rho_daytime"] = rho_day

            if var_col == "fc_cloud_cover":
                r_kt_day, rho_kt_day, _, _, _, _ = compute_stat_pair(s_day_df["fc_cloud_cover"], s_day_df["kt"])
                row["cloud_kt_r_daytime"] = r_kt_day
                row["cloud_kt_rho_daytime"] = rho_kt_day

        seasonal_list.append(row)

    seasonal_df = pd.DataFrame(seasonal_list)
    seasonal_df.to_csv(OUTPUT_SEASONAL_CSV, index=False)

    print("\n" + "=" * 90)
    print("3. SEASONAL DAYTIME CORRELATION BREAKDOWN")
    print("=" * 90)
    print(f"{'Season':<10} | {'Daytime Hrs':<12} | {'Cloud Cover r':<14} | {'Cloud vs kt r':<14} | {'Temp r':<10} | {'RH r':<10}")
    print("-" * 75)
    for _, r in seasonal_df.iterrows():
        print(f"{r['season']:<10} | {r['daytime_hours']:<12} | {r['fc_cloud_cover_r_daytime']:<14.3f} | {r['cloud_kt_r_daytime']:<14.3f} | {r['fc_temperature_2m_r_daytime']:<10.3f} | {r['fc_relative_humidity_2m_r_daytime']:<10.3f}")

    print("\nSkill analysis complete. All hard validation checks PASSED. Summary CSVs saved.")

if __name__ == "__main__":
    main()

