import os
import pandas as pd
import numpy as np
import pvlib

# ============================================================
# POLARIS — Elevation Sensitivity Analysis for Clear-Sky GHI
#
# Elevations to test: 0m, 500m, 800m, 820m, 1000m
# Station: SITES Nuolja Middle Station (68.362074°N, 18.738752°E, UTC+1)
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"  # UTC+1 (CET)

DATA_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"
BENCHMARK_FILE = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"

ELEVATIONS = [0, 500, 800, 820, 1000]

def calculate_metrics(actual, prediction):
    error = prediction - actual
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))
    return mae, rmse

def main():
    print("=" * 75)
    print("POLARIS — Elevation Sensitivity Analysis")
    print("=" * 75)

    df = pd.read_csv(DATA_FILE)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    times_localized = pd.DatetimeIndex(df["TIMESTAMP"]).tz_localize(TIMEZONE)

    benchmark = pd.read_csv(BENCHMARK_FILE)
    benchmark["forecast_start"] = pd.to_datetime(benchmark["forecast_start"])
    unique_starts = benchmark["forecast_start"].drop_duplicates().sort_values()

    actual_sw_in = df["SW_IN"].values

    results = []

    for elev in ELEVATIONS:
        location = pvlib.location.Location(
            latitude=LATITUDE,
            longitude=LONGITUDE,
            altitude=elev,
            tz=TIMEZONE,
            name=f"Nuolja_{elev}m"
        )

        solpos = location.get_solarposition(times_localized)
        solar_elevation = solpos["elevation"].values
        solar_zenith = solpos["zenith"].values

        clearsky = location.get_clearsky(times_localized, model="ineichen")
        clearsky_ghi = clearsky["ghi"].values

        # kt calculation
        kt = np.zeros_like(actual_sw_in)
        daytime_mask = (solar_elevation > 0) & (clearsky_ghi >= 1.0)
        kt[daytime_mask] = actual_sw_in[daytime_mask] / clearsky_ghi[daytime_mask]
        kt[daytime_mask] = np.clip(kt[daytime_mask], 0.0, 1.5)

        # Temp df for indexing
        decomp_indexed = pd.DataFrame({
            "TIMESTAMP": df["TIMESTAMP"],
            "actual_SW_IN": actual_sw_in,
            "clearsky_ghi": clearsky_ghi,
            "kt": kt
        }).set_index("TIMESTAMP")

        # Run Smart Persistence
        predictions = []
        for forecast_start in unique_starts:
            context_start = forecast_start - pd.Timedelta(hours=24)
            context_end = forecast_start - pd.Timedelta(hours=1)
            context_kt = decomp_indexed.loc[context_start:context_end, "kt"].values

            target_end = forecast_start + pd.Timedelta(hours=23)
            target_decomp = decomp_indexed.loc[forecast_start:target_end]
            target_clearsky = target_decomp["clearsky_ghi"].values

            pred_sw_in = np.clip(context_kt * target_clearsky, 0.0, None)

            window_df = pd.DataFrame({
                "actual": target_decomp["actual_SW_IN"].values,
                "pred": pred_sw_in
            })
            predictions.append(window_df)

        pred_df = pd.concat(predictions, ignore_index=True)
        act = pred_df["actual"].values
        prs = pred_df["pred"].values
        day_m = act > 0

        mae_all, rmse_all = calculate_metrics(act, prs)
        mae_day, rmse_day = calculate_metrics(act[day_m], prs[day_m])

        daytime_cs_ghi = clearsky_ghi[solar_elevation > 0]

        results.append({
            "elevation_m": elev,
            "max_clearsky_ghi": clearsky_ghi.max(),
            "mean_daytime_clearsky_ghi": daytime_cs_ghi.mean(),
            "max_solar_elevation": solar_elevation.max(),
            "smart_p_MAE": mae_all,
            "smart_p_RMSE": rmse_all,
            "smart_p_day_MAE": mae_day,
            "smart_p_day_RMSE": rmse_day
        })

    res_df = pd.DataFrame(results)
    print("\nELEVATION SENSITIVITY RESULTS:")
    print(res_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

if __name__ == "__main__":
    main()
