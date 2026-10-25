import pandas as pd
import torch
from chronos import Chronos2Pipeline

# --------------------------------------------------
# POLARIS paths
# --------------------------------------------------

DATA_FILE = "/home/punith-bs/01polaris/(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
BENCHMARK_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv"

# --------------------------------------------------
# Load original SITES hourly data
# --------------------------------------------------

data = pd.read_csv(DATA_FILE)
data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])

# First POLARIS forecast window
forecast_start = pd.Timestamp("2024-01-02 00:00:00")

context_start = forecast_start - pd.Timedelta(hours=24)
context_end = forecast_start - pd.Timedelta(hours=1)

context = data[
    (data["TIMESTAMP"] >= context_start)
    & (data["TIMESTAMP"] <= context_end)
].copy()

print("Context:")
print(context.to_string(index=False))

print("\nContext length:", len(context))

# --------------------------------------------------
# Load Chronos-2
# --------------------------------------------------

print("\nLoading Chronos-2...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2",
    device_map="cpu",
)

print("Chronos-2 loaded.")

# --------------------------------------------------
# Prepare Chronos-2 input
# --------------------------------------------------

context_df = pd.DataFrame({
    "item_id": ["POLARIS_SW_IN"] * len(context),
    "timestamp": context["TIMESTAMP"].values,
    "target": context["SW_IN"].values,
})

# --------------------------------------------------
# Forecast next 24 hours
# --------------------------------------------------

print("\nRunning 24-hour forecast...")

forecast = pipeline.predict_df(
    context_df,
    prediction_length=24,
)

print("\nForecast output:")
print(forecast)

print("\nSmoke test completed successfully.")
