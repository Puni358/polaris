import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE81_PREDS_PATH = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind" / "stage8_1_official_odd_predictions.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
OUTPUT_PREDS_PATH = BASE_DIR / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"
STAGE8_OUTPUT_PREDS_PATH = BASE_DIR / "forecasting/stage7" / "stage8" / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"

# Load source predictions
df_preds = pd.read_csv(STAGE81_PREDS_PATH)
df_preds["timestamp"] = pd.to_datetime(df_preds["timestamp"], utc=True)
df_preds["forecast_start"] = pd.to_datetime(df_preds["forecast_start"], utc=True)

# Load clear-sky for solar_elevation
df_cs = pd.read_csv(CLEARSKY_PATH)
df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)

# Merge solar_elevation
df_merged = df_preds.merge(df_cs[["timestamp", "solar_elevation"]], on="timestamp", how="left")

# Assign origin_id (1..173)
unique_origins = sorted(df_merged["forecast_start"].unique())
origin_map = {orig: i + 1 for i, orig in enumerate(unique_origins)}
df_merged["origin_id"] = df_merged["forecast_start"].map(origin_map)

# Construct final reproducible prediction table
df_final = pd.DataFrame({
    "origin_id": df_merged["origin_id"],
    "origin_timestamp": df_merged["forecast_start"].dt.strftime("%Y-%m-%d %H:%M:%S+00:00"),
    "horizon": df_merged["horizon_hour"],
    "valid_timestamp": df_merged["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S+00:00"),
    "y_true": df_merged["actual_SW_IN"],
    "y_pred": df_merged["pred_stage8_1_candidate"],
    "daytime_flag": df_merged["actual_SW_IN"] > 0,
    "solar_elevation": df_merged["solar_elevation"]
})

df_final.to_csv(OUTPUT_PREDS_PATH, index=False)
df_final.to_csv(STAGE8_OUTPUT_PREDS_PATH, index=False)

print(f"Successfully generated reproducible prediction artifact with {len(df_final)} rows.")
print(f"Root path: {OUTPUT_PREDS_PATH}")
print(f"Stage 8 path: {STAGE8_OUTPUT_PREDS_PATH}")
