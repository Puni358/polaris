import os
import urllib.request
import json
import pandas as pd
import numpy as np

# ============================================================
# POLARIS — Audit Clean NWP Benchmark Windows (metno_seamless)
#
# Goal: Identify exact PASS/FAIL 24h NWP coverage for all 365
# locked POLARIS forecast origins without any synthetic filling.
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"

BENCHMARK_FILE = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"
SITES_DATA_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"
OUTPUT_CLEAN_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2024.csv"
OUTPUT_REPORT_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_coverage_pass_fail.csv"

def fetch_raw_unfilled_year():
    url = (
        f"https://previous-runs-api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date=2024-01-01&end_date=2024-12-31"
        f"&hourly=cloud_cover_previous_day1,"
        f"temperature_2m_previous_day1,relative_humidity_2m_previous_day1,"
        f"precipitation_previous_day1,surface_pressure_previous_day1,"
        f"wind_speed_10m_previous_day1"
        f"&models=metno_seamless"
        f"&timezone={TIMEZONE}"
    )

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    hourly = data.get("hourly", {})
    timestamps = hourly.get("time", [])

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "fc_cloud_cover": hourly.get("cloud_cover_previous_day1"),
        "fc_temperature_2m": hourly.get("temperature_2m_previous_day1"),
        "fc_relative_humidity_2m": hourly.get("relative_humidity_2m_previous_day1"),
        "fc_precipitation": hourly.get("precipitation_previous_day1"),
        "fc_surface_pressure": hourly.get("surface_pressure_previous_day1"),
        "fc_wind_speed_10m": hourly.get("wind_speed_10m_previous_day1"),
    })
    return df

def main():
    print("=" * 85)
    print("POLARIS — Auditing Genuine NWP 24h Coverage (metno_seamless)")
    print("=" * 85)

    # 1. Load benchmark
    benchmark = pd.read_csv(BENCHMARK_FILE)
    benchmark["forecast_start"] = pd.to_datetime(benchmark["forecast_start"])
    benchmark["timestamp"] = pd.to_datetime(benchmark["timestamp"])

    unique_starts = benchmark["forecast_start"].drop_duplicates().sort_values()
    print(f"Total Locked Benchmark Origins: {len(unique_starts)}")

    # 2. Fetch raw unfilled forecast series
    print("\nFetching raw unfilled 2024 metno_seamless forecast series...")
    raw_df = fetch_raw_unfilled_year()

    # 3. Audit each of the 365 origins for PASS/FAIL 24h coverage
    pass_fail_list = []
    clean_windows = []

    for forecast_start in unique_starts:
        # Benchmark window (24 hours)
        target_hours = benchmark[benchmark["forecast_start"] == forecast_start]
        merged_window = target_hours.merge(raw_df, on="timestamp", how="left")

        # Check if all 24 hours have non-null NWP values across all genuine variables
        cols_to_check = [
            "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
            "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
        ]
        has_missing = merged_window[cols_to_check].isna().any().any()
        valid_count = len(merged_window) - merged_window[cols_to_check].isna().any(axis=1).sum()

        status = "FAIL" if has_missing else "PASS"

        pass_fail_list.append({
            "forecast_start": forecast_start.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "valid_hours": valid_count,
            "missing_hours": 24 - valid_count
        })

        if status == "PASS":
            clean_windows.append(merged_window)

    pf_df = pd.DataFrame(pass_fail_list)
    pf_df.to_csv(OUTPUT_REPORT_CSV, index=False)

    usable_origins = pf_df[pf_df["status"] == "PASS"]
    excluded_origins = pf_df[pf_df["status"] == "FAIL"]

    # 4. Save clean dataset with ONLY PASS windows
    clean_df = pd.concat(clean_windows, ignore_index=True)
    clean_df["forecast_start"] = clean_df["forecast_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    clean_df["timestamp"] = clean_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Select strictly genuine columns (dropping low/mid/high duplicates)
    clean_df = clean_df[[
        "forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
        "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
    ]]

    os.makedirs(os.path.dirname(OUTPUT_CLEAN_CSV), exist_ok=True)
    clean_df.to_csv(OUTPUT_CLEAN_CSV, index=False)

    # 5. Output Audit Statistics
    print("\n" + "=" * 65)
    print("AUDIT RESULTS & COVERAGE SUMMARY")
    print("=" * 65)
    print(f"Total Forecast Origins Evaluated:  {len(pf_df)}")
    print(f"Usable Forecast Origins (PASS):    {len(usable_origins)}")
    print(f"Excluded Forecast Origins (FAIL):  {len(excluded_origins)}")
    print(f"Percentage Usable Origins:         {len(usable_origins)/len(pf_df)*100:.2f}%")
    print(f"Total Usable Forecast Hours:       {len(clean_df)} hours ({len(usable_origins)} x 24)")

    if len(usable_origins) > 0:
        print(f"\nFirst Usable Forecast Origin:      {usable_origins['forecast_start'].iloc[0]}")
        print(f"Last Usable Forecast Origin:       {usable_origins['forecast_start'].iloc[-1]}")

    if len(excluded_origins) > 0:
        print(f"\nExact Excluded Forecast Dates ({len(excluded_origins)} origins):")
        print(f"  Start: {excluded_origins['forecast_start'].iloc[0]}")
        print(f"  End:   {excluded_origins['forecast_start'].iloc[-1]}")

    print("\n" + "=" * 65)
    print("CLEAN DATASET VALIDATION (POLARIS_v0_1_future_weather_forecasts_2024.csv)")
    print("=" * 65)
    print(f"1. Dataset Shape:              {clean_df.shape} ({len(usable_origins)} origins x 24h, 10 genuine cols)")
    print(f"2. Total Missing Values:        {clean_df.isna().sum().sum()} (Expected: 0)")
    print(f"3. Duplicate Rows Count:       {clean_df.duplicated(subset=['forecast_start', 'horizon_hour']).sum()} (Expected: 0)")
    print(f"4. Unique Forecast Origins:    {clean_df['forecast_start'].nunique()} (Expected: {len(usable_origins)})")
    print(f"5. Exactly 24 Horizons/Origin: {(clean_df.groupby('forecast_start')['horizon_hour'].count() == 24).all()}")
    print(f"6. PASS/FAIL Mapping File:    {OUTPUT_REPORT_CSV}")
    print(f"7. Synthetic Imputation Used:  NONE (0% bfill/ffill/interpolation/means)")
    print("Done!")

if __name__ == "__main__":
    main()
