import numpy as np
import pandas as pd
import time
from timesfm3 import TimesFM3Evaluator, ModelConfig

# ============================================================
# POLARIS LOCKED BENCHMARK
# ============================================================

DATA = "/home/punith-bs/01polaris/(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"

CONTEXT_LENGTH = 24
HORIZON = 24

print("=" * 70)
print("POLARIS — TimesFM 3.0 Zero-Shot Benchmark")
print("=" * 70)

# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

print("\nLoading SITES Nuolja 2024...")

df = pd.read_csv(DATA)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df = df.sort_values("TIMESTAMP").reset_index(drop=True)

values = df["SW_IN"].to_numpy(dtype=np.float32)
timestamps = df["TIMESTAMP"].to_numpy()

print(f"Dataset shape: {df.shape}")
print(f"Start: {timestamps[0]}")
print(f"End:   {timestamps[-1]}")

# ------------------------------------------------------------
# Load TimesFM 3.0
# ------------------------------------------------------------

print("\nLoading TimesFM 3.0...")

config = ModelConfig(
    checkpoint_path="google/timesfm-3.0-pytorch",
    per_core_batch_size=1,
    device="cpu",
)

forecaster = TimesFM3Evaluator(config)

print("TimesFM 3.0 loaded successfully.")

# ------------------------------------------------------------
# Generate the exact same 365 windows
# ------------------------------------------------------------

results = []

start_time = time.time()

# First evaluation window starts at index 24
# because indices 0:24 are the first 24h context.
#
# Windows:
# Jan 2 00:00 -> Jan 2 23:00
# ...
# Dec 31 00:00 -> Dec 31 23:00
#
# 365 windows × 24 hours = 8760 predictions.

num_windows = 365

print(f"\nRunning {num_windows} forecast windows...")
print("Context = 24 hours")
print("Horizon = 24 hours")
print("-" * 70)

for window in range(num_windows):

    # Forecast starts at 24 + window*24
    forecast_start_idx = CONTEXT_LENGTH + window * HORIZON

    context_start_idx = forecast_start_idx - CONTEXT_LENGTH
    context_end_idx = forecast_start_idx

    forecast_end_idx = forecast_start_idx + HORIZON

    context = values[context_start_idx:context_end_idx]

    # Safety check
    if len(context) != CONTEXT_LENGTH:
        raise RuntimeError(
            f"Invalid context length at window {window + 1}: "
            f"{len(context)}"
        )

    if forecast_end_idx > len(values):
        raise RuntimeError(
            f"Forecast exceeds dataset at window {window + 1}"
        )

    # --------------------------------------------------------
    # TimesFM forecast
    # --------------------------------------------------------

    outputs = list(
        forecaster.predict_batch(
            [context],
            horizon=HORIZON,
            return_quantiles=True,
            use_symmetric_averaging=False,
        )
    )

    forecast = np.asarray(outputs[0].forecast, dtype=np.float32)

    if forecast.shape != (HORIZON,):
        raise RuntimeError(
            f"Unexpected forecast shape at window {window + 1}: "
            f"{forecast.shape}"
        )

    # --------------------------------------------------------
    # Store predictions
    # --------------------------------------------------------

    for h in range(HORIZON):

        actual_idx = forecast_start_idx + h

        results.append({
            "forecast_start": timestamps[forecast_start_idx],
            "horizon_hour": h + 1,
            "timestamp": timestamps[actual_idx],
            "actual_SW_IN": float(values[actual_idx]),
            "timesfm3": float(forecast[h]),
        })

    # Progress
    if (window + 1) % 25 == 0 or window == 0:
        elapsed = time.time() - start_time
        rate = (window + 1) / elapsed
        remaining = (num_windows - window - 1) / rate

        print(
            f"Window {window + 1:3d}/{num_windows} | "
            f"Elapsed: {elapsed/60:.1f} min | "
            f"ETA: {remaining/60:.1f} min"
        )

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

result_df = pd.DataFrame(results)

result_df.to_csv(OUTPUT, index=False)

elapsed = time.time() - start_time

print("\n" + "=" * 70)
print("BENCHMARK COMPLETE")
print("=" * 70)

print(f"Windows: {result_df['forecast_start'].nunique()}")
print(f"Rows:    {len(result_df)}")
print(f"Elapsed: {elapsed/60:.2f} minutes")

print("\nColumns:")
print(list(result_df.columns))

print("\nTimesFM 3.0 prediction statistics:")
print(result_df["timesfm3"].describe())

print("\nNaN count:")
print(result_df["timesfm3"].isna().sum())

print(f"\nSaved to:")
print(OUTPUT)

print("=" * 70)
