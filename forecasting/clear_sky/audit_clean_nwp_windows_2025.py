import os
import hashlib
import urllib.request
import urllib.error
import json
import time
import pandas as pd
import numpy as np

# ============================================================
# POLARIS — Audit Clean NWP Benchmark Windows (metno_seamless) — 2025
#
# Mirrors forecasting/clear_sky/audit_clean_nwp_windows.py (2024, LOCKED) exactly.
#
# IMPORTANT: this is the actual method Stage 3 consumes for 2024
# (confirmed by inspection: forecasting/stage3/run_stage3_experiments.py reads
# data/POLARIS_v0_1_future_weather_forecasts_2024.csv, and the file
# currently on disk at that path is the PASS-only, zero-synthetic-
# imputation output of audit_clean_nwp_windows.py -- 347 origins,
# 10 genuine columns -- not the earlier bfill/ffill-filled, 365-
# origin, 13-column file that build_future_weather_dataset.py
# produces at the same path before being overwritten).
#
# The forecasting/clear_sky/build_future_weather_dataset_2025.py script run
# earlier replicated the FILL version, which is NOT what Stage 3b
# actually needs. This script replicates the CLEAN/AUDIT version
# and overwrites data/POLARIS_v0_1_future_weather_forecasts_2025.csv
# with it, exactly mirroring the 2024 production pipeline's final
# state. Does not read or write any 2024 file.
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"

SITES_SW_IN_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv"
CHECKPOINT_DIR = "/home/punith-bs/01polaris (Copy)/data/_checkpoints_2025_nwp_fetch"
RAW_UNFILLED_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "raw_unfilled_year_2025.csv")
OUTPUT_CLEAN_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
OUTPUT_REPORT_CSV = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_coverage_pass_fail_2025.csv"
MANIFEST_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json"


def fetch_raw_unfilled_year(retries=3, backoff=5):
    url = (
        f"https://previous-runs-api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date=2025-01-01&end_date=2025-12-31"
        f"&hourly=cloud_cover_previous_day1,"
        f"temperature_2m_previous_day1,relative_humidity_2m_previous_day1,"
        f"precipitation_previous_day1,surface_pressure_previous_day1,"
        f"wind_speed_10m_previous_day1"
        f"&models=metno_seamless"
        f"&timezone={TIMEZONE}"
    )
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=120) as resp:
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
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            last_err = e
            print(f"  attempt {attempt}/{retries} failed ({e}); retrying in {backoff}s...")
            time.sleep(backoff)
    raise RuntimeError(f"Failed to fetch raw unfilled 2025 year after {retries} attempts: {last_err}")


def atomic_write_csv(df, path):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)


def main():
    print("=" * 85)
    print("POLARIS — Auditing Genuine NWP 24h Coverage (metno_seamless) — 2025")
    print("=" * 85)

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    # 1. Build 2025 target structure (365 origins x 24h) from actual SW_IN
    actual = pd.read_csv(SITES_SW_IN_FILE)
    actual["timestamp"] = pd.to_datetime(actual["TIMESTAMP"])
    assert len(actual) == 8760, f"Expected 8760 rows, got {len(actual)}"

    benchmark = pd.DataFrame({
        "forecast_start": actual["timestamp"].dt.floor("D"),
        "horizon_hour": actual["timestamp"].dt.hour + 1,
        "timestamp": actual["timestamp"],
        "actual_SW_IN": actual["SW_IN"],
    })
    unique_starts = benchmark["forecast_start"].drop_duplicates().sort_values()
    print(f"Total 2025 Forecast Origins (candidate): {len(unique_starts)}")
    assert len(unique_starts) == 365

    # 2. Fetch (or resume from checkpoint) raw unfilled forecast series
    if os.path.exists(RAW_UNFILLED_CHECKPOINT):
        print(f"\nCheckpoint found, loading raw unfilled 2025 series from: {RAW_UNFILLED_CHECKPOINT}")
        raw_df = pd.read_csv(RAW_UNFILLED_CHECKPOINT)
        raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp"])
    else:
        print("\nFetching raw unfilled 2025 metno_seamless forecast series...")
        raw_df = fetch_raw_unfilled_year()
        atomic_write_csv(raw_df, RAW_UNFILLED_CHECKPOINT)
        print(f"Checkpointed raw unfilled series ({len(raw_df)} hours) to: {RAW_UNFILLED_CHECKPOINT}")

    # 3. Audit each of the 365 candidate origins for PASS/FAIL 24h coverage
    pass_fail_list = []
    clean_windows = []
    cols_to_check = [
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
        "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
    ]

    for forecast_start in unique_starts:
        target_hours = benchmark[benchmark["forecast_start"] == forecast_start]
        merged_window = target_hours.merge(raw_df, on="timestamp", how="left")

        has_missing = merged_window[cols_to_check].isna().any().any()
        valid_count = len(merged_window) - merged_window[cols_to_check].isna().any(axis=1).sum()
        status = "FAIL" if has_missing else "PASS"

        pass_fail_list.append({
            "forecast_start": forecast_start.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "valid_hours": int(valid_count),
            "missing_hours": int(24 - valid_count)
        })

        if status == "PASS":
            clean_windows.append(merged_window)

    pf_df = pd.DataFrame(pass_fail_list)
    atomic_write_csv(pf_df, OUTPUT_REPORT_CSV)

    usable_origins = pf_df[pf_df["status"] == "PASS"]
    excluded_origins = pf_df[pf_df["status"] == "FAIL"]

    # 4. Save clean dataset with ONLY PASS windows
    clean_df = pd.concat(clean_windows, ignore_index=True)
    clean_df["forecast_start"] = clean_df["forecast_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    clean_df["timestamp"] = clean_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    clean_df = clean_df[[
        "forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
        "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
    ]]

    atomic_write_csv(clean_df, OUTPUT_CLEAN_CSV)

    # 5. Output Audit Statistics
    print("\n" + "=" * 65)
    print("AUDIT RESULTS & COVERAGE SUMMARY (2025)")
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
        print(f"\nExcluded Forecast Origins ({len(excluded_origins)}):")
        print(excluded_origins[['forecast_start', 'missing_hours']].to_string(index=False))

    print("\n" + "=" * 65)
    print("CLEAN DATASET VALIDATION (POLARIS_v0_1_future_weather_forecasts_2025.csv)")
    print("=" * 65)
    print(f"1. Dataset Shape:              {clean_df.shape} ({len(usable_origins)} origins x 24h, 10 genuine cols)")
    assert clean_df.isna().sum().sum() == 0
    print(f"2. Total Missing Values:        {clean_df.isna().sum().sum()} (Expected: 0)")
    dup = clean_df.duplicated(subset=['forecast_start', 'horizon_hour']).sum()
    assert dup == 0
    print(f"3. Duplicate Rows Count:       {dup} (Expected: 0)")
    assert clean_df['forecast_start'].nunique() == len(usable_origins)
    print(f"4. Unique Forecast Origins:    {clean_df['forecast_start'].nunique()} (Expected: {len(usable_origins)})")
    horiz_ok = (clean_df.groupby('forecast_start')['horizon_hour'].count() == 24).all()
    assert horiz_ok
    print(f"5. Exactly 24 Horizons/Origin: {horiz_ok}")
    print(f"6. PASS/FAIL Mapping File:    {OUTPUT_REPORT_CSV}")
    print(f"7. Synthetic Imputation Used:  NONE (0% bfill/ffill/interpolation/means)")

    sha256 = hashlib.sha256()
    with open(OUTPUT_CLEAN_CSV, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    digest = sha256.hexdigest()
    print(f"\n8. SHA256 of {OUTPUT_CLEAN_CSV}:\n   {digest}")

    manifest = {
        "output_file": OUTPUT_CLEAN_CSV,
        "sha256": digest,
        "row_count": int(clean_df.shape[0]),
        "usable_origins": int(len(usable_origins)),
        "excluded_origins": int(len(excluded_origins)),
        "columns": list(clean_df.columns),
        "source_api": "https://previous-runs-api.open-meteo.com/v1/forecast",
        "model": "metno_seamless",
        "synthetic_imputation": "none",
        "method": "exact replica of forecasting/clear_sky/audit_clean_nwp_windows.py (2024, LOCKED), year substituted",
        "supersedes": (
            "data/POLARIS_v0_1_future_weather_forecasts_2025.csv as produced by "
            "forecasting/clear_sky/build_future_weather_dataset_2025.py (bfill/ffill-filled, "
            "365 origins, 13 cols) -- that file matched the WRONG 2024 script "
            "(build_future_weather_dataset.py) rather than the one Stage 3 "
            "actually consumes in production (audit_clean_nwp_windows.py's "
            "output, which overwrites the same path on the 2024 side)."
        ),
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {MANIFEST_FILE}")
    print("Done!")


if __name__ == "__main__":
    main()
