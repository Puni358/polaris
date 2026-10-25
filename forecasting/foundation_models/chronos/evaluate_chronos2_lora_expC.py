from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chronos import Chronos2Pipeline
from chronos.chronos2.preprocess import from_data_frame


DATA_PATH = "/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"

BASELINE_PATH = "/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv"

ZERO_SHOT_PATH = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

CHECKPOINT_DIR = (
    "/home/punith-bs/01polaris/chronos/"
    "polaris_lora_expC_500/finetuned-ckpt"
)

OUTPUT_DIR = Path(
    "/home/punith-bs/01polaris/chronos/"
    "polaris_lora_expC_500_test"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PREDICTION_LENGTH = 24
CONTEXT_LENGTH = 24

TARGET = "SW_IN"
COVARIATES = ["TA", "RH", "TS_-0.01m", "PRECIP"]

TEST_START = pd.Timestamp("2024-09-01 00:00:00")
TEST_END = pd.Timestamp("2024-12-31 23:00:00")


print("=" * 80)
print("POLARIS — Chronos-2 LoRA EXPERIMENT B — HELD-OUT TEST")
print("=" * 80)

print(f"\nPyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

df = pd.read_csv(DATA_PATH)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

print(f"\nFull dataset: {df.shape}")
print(f"Full range: {df['TIMESTAMP'].min()} -> {df['TIMESTAMP'].max()}")


# ============================================================
# Build exact daily test windows
# ============================================================

windows = []

current = TEST_START

while current <= TEST_END - pd.Timedelta(hours=23):

    context_start = current - pd.Timedelta(hours=24)
    context_end = current - pd.Timedelta(hours=1)
    forecast_end = current + pd.Timedelta(hours=23)

    context = df[
        (df["TIMESTAMP"] >= context_start)
        & (df["TIMESTAMP"] <= context_end)
    ]

    actual = df[
        (df["TIMESTAMP"] >= current)
        & (df["TIMESTAMP"] <= forecast_end)
    ]

    if len(context) != 24:
        raise RuntimeError(
            f"Bad context length for {current}: {len(context)}"
        )

    if len(actual) != 24:
        raise RuntimeError(
            f"Bad forecast length for {current}: {len(actual)}"
        )

    windows.append((current, context.copy(), actual.copy()))

    current += pd.Timedelta(hours=24)


print(f"\nTest windows: {len(windows)}")
print("Expected: 122")
print(f"Test hours: {len(windows) * 24}")
print(f"Test period: {TEST_START} -> {TEST_END}")

if len(windows) != 122:
    raise RuntimeError(
        f"Expected 122 test windows, found {len(windows)}"
    )


# ============================================================
# Load LoRA checkpoint
# ============================================================

print("\nLoading LoRA checkpoint...")
print(f"Checkpoint: {CHECKPOINT_DIR}")

pipeline = Chronos2Pipeline.from_pretrained(
    CHECKPOINT_DIR,
    import_allowlist=["chronos.chronos2.model"],
)

print("LoRA checkpoint loaded.")


# ============================================================
# Forecast
# ============================================================

results = []

print("\nRunning held-out Sep-Dec forecasts...")

for i, (forecast_start, context_df, actual_df) in enumerate(
    windows, start=1
):

    input_df = context_df[
        ["TIMESTAMP", TARGET] + COVARIATES
    ].copy()

    input_df = input_df.rename(
        columns={"TIMESTAMP": "timestamp"}
    )

    input_df["item_id"] = "Nuolja"

    input_df = input_df[
        ["item_id", "timestamp", TARGET] + COVARIATES
    ]

    prepared = from_data_frame(
        input_df,
        target_columns=[TARGET],
        prediction_length=PREDICTION_LENGTH,
        id_column="item_id",
        timestamp_column="timestamp",
    )

    predictions = pipeline.predict(
        prepared,
        prediction_length=PREDICTION_LENGTH,
        context_length=CONTEXT_LENGTH,
        batch_size=1,
        limit_prediction_length=False,
    )

    pred_tensor = predictions[0]

    # Chronos quantile index 10 = median / 0.5
    forecast = (
        pred_tensor[0, 10, :]
        .detach()
        .cpu()
        .numpy()
    )

    actual_values = actual_df[TARGET].to_numpy(dtype=float)
    timestamps = actual_df["TIMESTAMP"].to_numpy()

    for h in range(24):
        results.append(
            {
                "forecast_start": forecast_start,
                "horizon_hour": h + 1,
                "timestamp": timestamps[h],
                "actual_SW_IN": actual_values[h],
                "chronos2_lora_expC_500": forecast[h],
            }
        )

    if i == 1 or i % 20 == 0 or i == len(windows):
        print(
            f"  Window {i:3d}/{len(windows)} "
            f"| {forecast_start.date()} "
            f"| forecast max = {forecast.max():.3f}"
        )


pred_df = pd.DataFrame(results)

prediction_path = (
    OUTPUT_DIR /
    "POLARIS_v0_1_chronos2_lora_expC_500_test_predictions.csv"
)

pred_df.to_csv(prediction_path, index=False)

print("\nPredictions saved:")
print(prediction_path)


# ============================================================
# Metric helper
# ============================================================

def calculate_metrics(actual, forecast):

    errors = forecast - actual

    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))

    daytime = actual > 0

    daytime_mae = np.mean(
        np.abs(errors[daytime])
    )

    daytime_rmse = np.sqrt(
        np.mean(errors[daytime] ** 2)
    )

    return (
        mae,
        rmse,
        daytime_mae,
        daytime_rmse,
    )


# ============================================================
# LoRA metrics
# ============================================================

actual = pred_df["actual_SW_IN"].to_numpy(float)
forecast = pred_df[
    "chronos2_lora_expC_500"
].to_numpy(float)

(
    mae,
    rmse,
    daytime_mae,
    daytime_rmse,
) = calculate_metrics(actual, forecast)


# ============================================================
# Zero-shot Chronos-2 metrics
# ============================================================

zero_df = pd.read_csv(ZERO_SHOT_PATH)
zero_df["forecast_start"] = pd.to_datetime(
    zero_df["forecast_start"]
)

zero_test = zero_df[
    (zero_df["forecast_start"] >= TEST_START)
    & (zero_df["forecast_start"] <= TEST_END)
].copy()

zero_actual = zero_test["actual_SW_IN"].to_numpy(float)
zero_forecast = zero_test["chronos2"].to_numpy(float)

(
    zero_mae,
    zero_rmse,
    zero_day_mae,
    zero_day_rmse,
) = calculate_metrics(
    zero_actual,
    zero_forecast,
)


# ============================================================
# Seasonal Naive metrics
# ============================================================

baseline_df = pd.read_csv(BASELINE_PATH)
baseline_df["forecast_start"] = pd.to_datetime(
    baseline_df["forecast_start"]
)

baseline_test = baseline_df[
    (baseline_df["forecast_start"] >= TEST_START)
    & (baseline_df["forecast_start"] <= TEST_END)
].copy()

baseline_actual = baseline_test[
    "actual_SW_IN"
].to_numpy(float)

baseline_forecast = baseline_test[
    "seasonal_naive_24h"
].to_numpy(float)

(
    baseline_mae,
    baseline_rmse,
    baseline_day_mae,
    baseline_day_rmse,
) = calculate_metrics(
    baseline_actual,
    baseline_forecast,
)


# ============================================================
# Print results
# ============================================================

print("\n" + "=" * 80)
print("HELD-OUT TEST RESULTS — SEPTEMBER + OCTOBER + NOVEMBER + DECEMBER")
print("=" * 80)

print(f"\nTest observations: {len(actual)}")
print(f"Daytime observations: {(actual > 0).sum()}")

print("\nChronos-2 LoRA Experiment C — 500:")
print(f"  MAE:          {mae:.6f} W/m²")
print(f"  RMSE:         {rmse:.6f} W/m²")
print(f"  Daytime MAE:  {daytime_mae:.6f} W/m²")
print(f"  Daytime RMSE: {daytime_rmse:.6f} W/m²")

print("\nZero-shot Chronos-2:")
print(f"  MAE:          {zero_mae:.6f} W/m²")
print(f"  RMSE:         {zero_rmse:.6f} W/m²")
print(f"  Daytime MAE:  {zero_day_mae:.6f} W/m²")
print(f"  Daytime RMSE: {zero_day_rmse:.6f} W/m²")

print("\nSeasonal Naive 24h:")
print(f"  MAE:          {baseline_mae:.6f} W/m²")
print(f"  RMSE:         {baseline_rmse:.6f} W/m²")
print(f"  Daytime MAE:  {baseline_day_mae:.6f} W/m²")
print(f"  Daytime RMSE: {baseline_day_rmse:.6f} W/m²")


def improvement(reference, model):
    return 100.0 * (reference - model) / reference


print("\n" + "-" * 80)
print("IMPROVEMENT OF EXPERIMENT B LoRA")
print("-" * 80)

print("\nvs Zero-shot Chronos-2:")
print(f"  MAE:          {improvement(zero_mae, mae):+.2f}%")
print(f"  RMSE:         {improvement(zero_rmse, rmse):+.2f}%")
print(
    f"  Daytime MAE:  "
    f"{improvement(zero_day_mae, daytime_mae):+.2f}%"
)
print(
    f"  Daytime RMSE: "
    f"{improvement(zero_day_rmse, daytime_rmse):+.2f}%"
)

print("\nvs Seasonal Naive:")
print(f"  MAE:          {improvement(baseline_mae, mae):+.2f}%")
print(f"  RMSE:         {improvement(baseline_rmse, rmse):+.2f}%")
print(
    f"  Daytime MAE:  "
    f"{improvement(baseline_day_mae, daytime_mae):+.2f}%"
)
print(
    f"  Daytime RMSE: "
    f"{improvement(baseline_day_rmse, daytime_rmse):+.2f}%"
)


# ============================================================
# Save metrics
# ============================================================

metrics = pd.DataFrame(
    [
        {
            "model": "Chronos-2 LoRA ExpB 500",
            "MAE_W_m2": mae,
            "RMSE_W_m2": rmse,
            "daytime_MAE_W_m2": daytime_mae,
            "daytime_RMSE_W_m2": daytime_rmse,
        },
        {
            "model": "Chronos-2 zero-shot",
            "MAE_W_m2": zero_mae,
            "RMSE_W_m2": zero_rmse,
            "daytime_MAE_W_m2": zero_day_mae,
            "daytime_RMSE_W_m2": zero_day_rmse,
        },
        {
            "model": "Seasonal Naive 24h",
            "MAE_W_m2": baseline_mae,
            "RMSE_W_m2": baseline_rmse,
            "daytime_MAE_W_m2": baseline_day_mae,
            "daytime_RMSE_W_m2": baseline_day_rmse,
        },
    ]
)

metrics_path = (
    OUTPUT_DIR /
    "POLARIS_v0_1_chronos2_lora_expC_500_test_metrics.csv"
)

metrics.to_csv(metrics_path, index=False)

print("\nMetrics saved:")
print(metrics_path)

print("\n" + "=" * 80)
print("EXPERIMENT B EVALUATION COMPLETE")
print("=" * 80)
