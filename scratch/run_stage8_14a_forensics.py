import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

# File paths
ODD_PREDS_PATH = STAGE_DIR / "stage8_1_official_odd_predictions.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
STAGE66_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE75_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
STAGE81_FEAT_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"
SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"

def load_forensic_table():
    df_preds = pd.read_csv(ODD_PREDS_PATH)
    df_preds["forecast_start"] = pd.to_datetime(df_preds["forecast_start"], utc=True)
    df_preds["timestamp"] = pd.to_datetime(df_preds["timestamp"], utc=True)

    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)
    df_nwp["timestamp"] = pd.to_datetime(df_nwp["timestamp"], utc=True)

    df_cs = pd.read_csv(CLEARSKY_PATH)
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)

    df_66 = pd.read_csv(STAGE66_PATH)
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)

    df_75 = pd.read_csv(STAGE75_PATH)
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)

    df_81 = pd.read_csv(STAGE81_FEAT_PATH)
    df_81["forecast_start"] = pd.to_datetime(df_81["forecast_start"], utc=True)

    # Merge
    df = df_preds.copy()
    
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0

    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith", "solar_azimuth"]
    # Check if solar_azimuth exists in df_cs
    cs_cols_present = [c for c in cs_cols if c in df_cs.columns]
    df = df.merge(df_cs[cs_cols_present], on="timestamp", how="left")

    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")

    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    terrain_cols_present = [c for c in terrain_cols if c in df_75.columns]
    df = df.merge(df_75[terrain_cols_present], on="timestamp", how="left")

    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df = df.merge(df_81[wind_cols], on=["forecast_start", "horizon_hour"], how="left")

    # Also merge context features if needed
    # Derived quantities
    df["pred"] = df["pred_stage8_1_candidate"]
    df["actual"] = df["actual_SW_IN"]
    df["residual"] = df["pred"] - df["actual"]
    df["abs_error"] = df["residual"].abs()
    df["sq_error"] = df["residual"] ** 2

    # Wind speed and direction
    df["wind_speed_700"] = np.sqrt(df["u700"]**2 + df["v700"]**2)
    # Meteorological wind direction (direction wind is coming FROM)
    # math: atan2(-u, -v) in degrees converted to 0-360
    wind_dir_rad = np.arctan2(-df["u700"], -df["v700"])
    df["wind_dir_700"] = (np.degrees(wind_dir_rad) + 360.0) % 360.0

    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    
    # Seasons: Winter (12,1,2), Spring (3,4,5), Summer (6,7,8), Autumn (9,10,11)
    def get_season(m):
        if m in [12, 1, 2]: return "Winter"
        elif m in [3, 4, 5]: return "Spring"
        elif m in [6, 7, 8]: return "Summer"
        else: return "Autumn"
    df["season"] = df["month"].apply(get_season)

    return df

if __name__ == "__main__":
    df = load_forensic_table()
    print(f"Loaded Forensic Table: {len(df)} rows total, {len(df[df['is_daytime']])} daytime rows.")
    print("Columns:", df.columns.tolist())
