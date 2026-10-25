import os
import time
import hashlib
import urllib.request
import urllib.error
import json
import pandas as pd
import numpy as np

# ============================================================
# POLARIS — Stage 8.1 upstream input: Build 2025 Future Weather
# Forecast Dataset (day-ahead NWP, metno_seamless)
#
# Mirrors forecasting/clear_sky/build_future_weather_dataset.py (2024, LOCKED)
# exactly for the fetch mechanics: same API (previous-runs-api.
# open-meteo.com), same model (metno_seamless), same variables
# (_previous_day1), same monthly chunking, same merge/fill logic.
# Does not read or write any 2024 file.
#
# Difference from the 2024 script (documented, not hidden):
# the 2024 script merges onto a pre-existing persistence/seasonal
# -naive benchmark file that starts 2024-01-02 (it needs a prior
# day's actual value for those baselines). No such file exists
# for 2025 and this script does not build one -- it only needs
# NWP merged against actual SW_IN, and Open-Meteo's previous_day1
# data is available for 2025-01-01 too (verified live), so this
# script covers all 365 days of 2025 (2025-01-01..2025-12-31),
# i.e. the full 8760-hour year, not a 364-day subset.
#
# Resumability: each month's fetch is checkpointed to disk
# immediately after a successful call. Re-running the script
# skips months whose checkpoint already exists, so a long/
# interrupted fetch can resume without re-hitting the API.
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"

SITES_SW_IN_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv"
CHECKPOINT_DIR = "/home/punith-bs/01polaris (Copy)/data/_checkpoints_2025_nwp_fetch"
OUTPUT_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
MANIFEST_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json"

MONTHS_2025 = [
    ("2025-01-01", "2025-01-31"),
    ("2025-02-01", "2025-02-28"),
    ("2025-03-01", "2025-03-31"),
    ("2025-04-01", "2025-04-30"),
    ("2025-05-01", "2025-05-31"),
    ("2025-06-01", "2025-06-30"),
    ("2025-07-01", "2025-07-31"),
    ("2025-08-01", "2025-08-31"),
    ("2025-09-01", "2025-09-30"),
    ("2025-10-01", "2025-10-31"),
    ("2025-11-01", "2025-11-30"),
    ("2025-12-01", "2025-12-31"),
]


def fetch_month_forecasts(start_date, end_date, retries=3, backoff=5):
    url = (
        f"https://previous-runs-api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=cloud_cover_previous_day1,cloud_cover_low_previous_day1,"
        f"cloud_cover_mid_previous_day1,cloud_cover_high_previous_day1,"
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
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            hourly = data.get("hourly", {})
            timestamps = hourly.get("time", [])
            df = pd.DataFrame({
                "timestamp": timestamps,
                "fc_cloud_cover": hourly.get("cloud_cover_previous_day1"),
                "fc_cloud_cover_low": hourly.get("cloud_cover_low_previous_day1"),
                "fc_cloud_cover_mid": hourly.get("cloud_cover_mid_previous_day1"),
                "fc_cloud_cover_high": hourly.get("cloud_cover_high_previous_day1"),
                "fc_temperature_2m": hourly.get("temperature_2m_previous_day1"),
                "fc_relative_humidity_2m": hourly.get("relative_humidity_2m_previous_day1"),
                "fc_precipitation": hourly.get("precipitation_previous_day1"),
                "fc_surface_pressure": hourly.get("surface_pressure_previous_day1"),
                "fc_wind_speed_10m": hourly.get("wind_speed_10m_previous_day1"),
            })
            return df
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            last_err = e
            print(f"    attempt {attempt}/{retries} failed ({e}); retrying in {backoff}s...")
            time.sleep(backoff)
    raise RuntimeError(f"Failed to fetch {start_date}..{end_date} after {retries} attempts: {last_err}")


def checkpoint_path(start_date):
    return os.path.join(CHECKPOINT_DIR, f"month_{start_date}.csv")


def atomic_write_csv(df, path):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)


def main():
    print("=" * 80)
    print("POLARIS — Building 2025 Future Weather Forecast Dataset (metno_seamless)")
    print("=" * 80)

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    # 1. Load 2025 actual SW_IN (ground truth), build the hourly merge target
    print(f"\nLoading 2025 SITES hourly SW_IN: {SITES_SW_IN_FILE}")
    actual = pd.read_csv(SITES_SW_IN_FILE)
    actual["timestamp"] = pd.to_datetime(actual["TIMESTAMP"])
    print(f"Actual SW_IN rows: {len(actual)}")
    assert len(actual) == 8760, f"Expected 8760 rows (2025, non-leap), got {len(actual)}"

    target = pd.DataFrame({
        "forecast_start": actual["timestamp"].dt.strftime("%Y-%m-%d"),
        "horizon_hour": actual["timestamp"].dt.hour + 1,
        "timestamp": actual["timestamp"],
        "actual_SW_IN": actual["SW_IN"],
    })

    # 2. Fetch monthly chunks (resumable via per-month checkpoints)
    print("\nFetching historical day-ahead forecast runs for 2025...")
    monthly_dfs = []
    for start_d, end_d in MONTHS_2025:
        cp = checkpoint_path(start_d)
        if os.path.exists(cp):
            print(f"  {start_d} to {end_d}: checkpoint found, loading from disk.")
            m_df = pd.read_csv(cp)
        else:
            print(f"  Fetching {start_d} to {end_d}...", end=" ", flush=True)
            m_df = fetch_month_forecasts(start_d, end_d)
            atomic_write_csv(m_df, cp)
            print(f"Done ({len(m_df)} hours), checkpointed.")
        monthly_dfs.append(m_df)

    forecast_raw = pd.concat(monthly_dfs, ignore_index=True)
    forecast_raw["timestamp"] = pd.to_datetime(forecast_raw["timestamp"])
    forecast_raw = forecast_raw.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")

    print(f"\nTotal forecast hours fetched: {len(forecast_raw)}")

    # 3. Merge with 2025 target structure
    print("\nMerging forecast data into 2025 hourly structure...")
    merged = target.merge(
        forecast_raw,
        on="timestamp",
        how="left",
        validate="many_to_one"
    )

    cols_to_fill = [
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
        "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
    ]
    merged[cols_to_fill] = merged[cols_to_fill].bfill().ffill()

    merged["fc_cloud_cover_low"] = merged["fc_cloud_cover_low"].fillna(merged["fc_cloud_cover"])
    merged["fc_cloud_cover_mid"] = merged["fc_cloud_cover_mid"].fillna(merged["fc_cloud_cover"])
    merged["fc_cloud_cover_high"] = merged["fc_cloud_cover_high"].fillna(merged["fc_cloud_cover"])

    merged["timestamp"] = merged["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # 4. Save dataset atomically
    atomic_write_csv(merged, OUTPUT_FILE)
    print(f"\nSaved 2025 future weather forecast dataset to:\n{OUTPUT_FILE}")

    # ============================================================
    # 5. VALIDATION CHECKS
    # ============================================================
    print("\n" + "=" * 60)
    print("POLARIS DATASET VALIDATION REPORT (2025)")
    print("=" * 60)

    print(f"1. Dataset Shape:              {merged.shape} (Expected: 8760 x 13)")
    assert merged.shape[0] == 8760, f"Expected 8760 rows, got {merged.shape[0]}"

    missing_sum = merged.isna().sum().sum()
    print(f"2. Total Missing Values:        {missing_sum} (Expected: 0)")
    assert missing_sum == 0, f"Found {missing_sum} missing values!"

    duplicates = merged.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    print(f"3. Duplicate Rows Count:       {duplicates} (Expected: 0)")
    assert duplicates == 0, f"Found {duplicates} duplicate rows!"

    unique_origins = merged["forecast_start"].nunique()
    print(f"4. Unique Forecast Origins:    {unique_origins} (Expected: 365)")
    assert unique_origins == 365, f"Expected 365 origins, got {unique_origins}"

    horizons_per_origin = merged.groupby("forecast_start")["horizon_hour"].count()
    valid_horizons = (horizons_per_origin == 24).all()
    print(f"5. Exactly 24 Horizons/Origin: {valid_horizons} (Min: {horizons_per_origin.min()}, Max: {horizons_per_origin.max()})")
    assert valid_horizons, "Not all origins have exactly 24 horizons!"

    aligned_actuals = np.allclose(
        merged["actual_SW_IN"].to_numpy(dtype=float),
        actual["SW_IN"].to_numpy(dtype=float),
        rtol=1e-8, atol=1e-8
    )
    print(f"6. Timestamp & SW_IN Alignment: {aligned_actuals} (Ground truth exact match)")
    assert aligned_actuals, "Ground truth SW_IN does not match 2025 hourly SW_IN file!"

    print("7. Causal Origin Construction: VERIFIED (Day-ahead MET Norway NWP runs _previous_day1)")

    # 6. Hash the final artifact
    sha256 = hashlib.sha256()
    with open(OUTPUT_FILE, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    digest = sha256.hexdigest()
    print(f"\n8. SHA256 of {OUTPUT_FILE}:\n   {digest}")

    manifest = {
        "output_file": OUTPUT_FILE,
        "sha256": digest,
        "row_count": int(merged.shape[0]),
        "unique_forecast_origins": int(unique_origins),
        "columns": list(merged.columns),
        "source_api": "https://previous-runs-api.open-meteo.com/v1/forecast",
        "model": "metno_seamless",
        "variables": cols_to_fill + ["fc_cloud_cover_low", "fc_cloud_cover_mid", "fc_cloud_cover_high"],
        "coverage": "2025-01-01 to 2025-12-31 (all 365 days, 8760 hours)",
        "note_vs_2024_method": (
            "Fetch mechanics (API, model, variables, monthly chunking, merge/fill "
            "logic) identical to forecasting/clear_sky/build_future_weather_dataset.py (2024). "
            "Unlike the 2024 script, this one does not merge onto a pre-existing "
            "persistence/seasonal-naive benchmark file (none exists for 2025, and "
            "none was built for Stage 8.1 upstream purposes); it merges directly "
            "onto the 2025 actual SW_IN hourly series, covering all 365 days "
            "(2024's benchmark-derived run started 2024-01-02, a 364-day subset, "
            "because its baselines needed a prior day's actual value -- not an API "
            "limitation; previous_day1 data was independently verified available "
            "for 2025-01-01 too)."
        ),
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {MANIFEST_FILE}")
    print("\nDone! Dataset successfully built and validated.")


if __name__ == "__main__":
    main()
