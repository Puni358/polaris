from pathlib import Path

import numpy as np
import pandas as pd
import torch

from chronos import Chronos2Pipeline
from chronos.chronos2.preprocess import from_data_frame


# ============================================================
# POLARIS — Chronos-2 LoRA 1000-step HELD-OUT TEST
# ============================================================

DATA_PATH = "/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"

BASELINE_PATH = "/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv"

CHECKPOINT_DIR = "/home/punith-bs/01polaris/chronos/polaris_lora_1000/finetuned-ckpt"

OUTPUT_DIR = Path("/home/punith-bs/01polaris/chronos/polaris_lora_1000_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PREDICTION_LENGTH = 24
CONTEXT_LENGTH = 24

TARGET = "SW_IN"
COVARIATES = ["TA", "RH", "TS_-0.01m", "PRECIP"]

TEST_START = pd.Timestamp("2024-11-01 00:00:00")
TEST_END = pd.Timestamp("2024-12-31 23:00:00")


print("=" * 80)
print("POLARIS — Chronos-2 LoRA 1000-step HELD-OUT TEST")
print("=" * 80)

print(f"\nPyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

df = pd.read_csv(DATA_PATH)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

print(f"\nFull dataset: {df.shape}")
print(f"Full range: {df['TIMESTAMP'].min()} -> {df['TIMESTAMP'].max()}")

# ------------------------------------------------------------
# Build the exact test windows
#
# Each forecast:
#   context = previous 24 hours
#   target  = next 24 hours
#
# Test windows:
#   Nov 1 -> Dec 31
# ------------------------------------------------------------

all_windows = []

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

    if len(context) == 24 and len(actual) == 24:
        all_windows.append(
            (current, context.copy(), actual.copy())
        )

    current += pd.Timedelta(hours=24)

print(f"\nTest windows: {len(all_windows)}")
print(f"Expected: 61")
print(f"Test hours: {len(all_windows) * 24}")
print(f"Test period: {TEST_START} -> {TEST_END}")

if len(all_windows) != 61:
    raise RuntimeError(
        f"Expected exactly 61 test windows, found {len(all_windows)}"
    )

# ------------------------------------------------------------
# Load base Chronos-2 + LoRA checkpoint
# ------------------------------------------------------------

print("\nLoading Chronos-2 base model...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2"
)

print("Base model loaded.")

# ------------------------------------------------------------
# Load LoRA adapter
#
# Chronos-2's pipeline.fit() checkpoint is loaded by passing
# the adapter checkpoint through from_pretrained().
# ------------------------------------------------------------

print("\nLoading LoRA checkpoint...")
print(f"Checkpoint: {CHECKPOINT_DIR}")

finetuned_pipeline = Chronos2Pipeline.from_pretrained(
    CHECKPOINT_DIR,
    import_allowlist=["chronos.chronos2.model"],
)

print("LoRA checkpoint loaded.")

# ------------------------------------------------------------
# Run forecasts
# ------------------------------------------------------------

results = []

print("\nRunning held-out Nov-Dec forecasts...")

for i, (forecast_start, context_df, actual_df) in enumerate(
    all_windows, start=1
):

    # Chronos long-format input
    input_df = context_df[
        ["TIMESTAMP", TARGET] + COVARIATES
    ].copy()

    input_df = input_df.rename(
        columns={"TIMESTAMP": "timestamp"}
    )

    input_df["item_id"] = "Nuolja"

    # Reorder columns
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

    predictions = finetuned_pipeline.predict(
        prepared,
        prediction_length=PREDICTION_LENGTH,
        context_length=CONTEXT_LENGTH,
        batch_size=1,
        limit_prediction_length=False,
    )

    # Output shape:
    # [n_variates, n_quantiles, prediction_length]
    pred_tensor = predictions[0]

    # Quantile index 10 = 0.5 median
    median_forecast = (
        pred_tensor[0, 10, :]
        .detach()
        .cpu()
        .numpy()
    )

    actual_values = actual_df[TARGET].to_numpy(dtype=np.float64)

    timestamps = actual_df["TIMESTAMP"].to_numpy()

    for h in range(24):
        results.append(
            {
                "forecast_start": forecast_start,
                "horizon_hour": h + 1,
                "timestamp": timestamps[h],
                "actual_SW_IN": actual_values[h],
                "chronos2_lora_500": median_forecast[h],
            }
        )

    if i == 1 or i % 10 == 0 or i == len(all_windows):
        print(
            f"  Window {i:2d}/{len(all_windows)} "
            f"| {forecast_start.date()} "
            f"| forecast max = {median_forecast.max():.3f}"
        )

# ------------------------------------------------------------
# Save predictions
# ------------------------------------------------------------

pred_df = pd.DataFrame(results)

prediction_path = (
    OUTPUT_DIR
    / "POLARIS_v0_1_chronos2_lora_1000_test_predictions.csv"
)

pred_df.to_csv(prediction_path, index=False)

print("\nPredictions saved:")
print(prediction_path)

# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

actual = pred_df["actual_SW_IN"].to_numpy(dtype=float)
forecast = pred_df["chronos2_lora_500"].to_numpy(dtype=float)

errors = forecast - actual

mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(errors ** 2))

daytime_mask = actual > 0

daytime_mae = np.mean(
    np.abs(errors[daytime_mask])
)

daytime_rmse = np.sqrt(
    np.mean(errors[daytime_mask] ** 2)
)

print("\n" + "=" * 80)
print("HELD-OUT TEST RESULTS — NOVEMBER + DECEMBER")
print("=" * 80)

print(f"\nTest observations: {len(actual)}")
print(f"Daytime observations: {daytime_mask.sum()}")

print("\nChronos-2 LoRA 1000:")
print(f"  MAE:          {mae:.6f} W/m²")
print(f"  RMSE:         {rmse:.6f} W/m²")
print(f"  Daytime MAE:  {daytime_mae:.6f} W/m²")
print(f"  Daytime RMSE: {daytime_rmse:.6f} W/m²")

# ------------------------------------------------------------
# Compare with zero-shot Chronos-2
# ------------------------------------------------------------

zero_shot_path = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"
)

zero_df = pd.read_csv(zero_shot_path)

zero_df["forecast_start"] = pd.to_datetime(
    zero_df["forecast_start"]
)

zero_test = zero_df[
    (zero_df["forecast_start"] >= TEST_START)
    & (zero_df["forecast_start"] <= TEST_END)
].copy()

zero_actual = zero_test["actual_SW_IN"].to_numpy(dtype=float)
zero_forecast = zero_test["chronos2"].to_numpy(dtype=float)

zero_errors = zero_forecast - zero_actual

zero_mae = np.mean(np.abs(zero_errors))
zero_rmse = np.sqrt(np.mean(zero_errors ** 2))

zero_day_mask = zero_actual > 0

zero_day_mae = np.mean(
    np.abs(zero_errors[zero_day_mask])
)

zero_day_rmse = np.sqrt(
    np.mean(zero_errors[zero_day_mask] ** 2)
)

print("\nZero-shot Chronos-2:")
print(f"  MAE:          {zero_mae:.6f} W/m²")
print(f"  RMSE:         {zero_rmse:.6f} W/m²")
print(f"  Daytime MAE:  {zero_day_mae:.6f} W/m²")
print(f"  Daytime RMSE: {zero_day_rmse:.6f} W/m²")

# ------------------------------------------------------------
# Seasonal naive
# ------------------------------------------------------------

baseline_df = pd.read_csv(BASELINE_PATH)

baseline_df["forecast_start"] = pd.to_datetime(
    baseline_df["forecast_start"]
)

baseline_test = baseline_df[
    (baseline_df["forecast_start"] >= TEST_START)
    & (baseline_df["forecast_start"] <= TEST_END)
].copy()

baseline_actual = baseline_test["actual_SW_IN"].to_numpy(dtype=float)
baseline_forecast = (
    baseline_test["seasonal_naive_24h"]
    .to_numpy(dtype=float)
)

baseline_errors = baseline_forecast - baseline_actual

baseline_mae = np.mean(np.abs(baseline_errors))
baseline_rmse = np.sqrt(np.mean(baseline_errors ** 2))

baseline_day_mask = baseline_actual > 0

baseline_day_mae = np.mean(
    np.abs(baseline_errors[baseline_day_mask])
)

baseline_day_rmse = np.sqrt(
    np.mean(baseline_errors[baseline_day_mask] ** 2)
)

print("\nSeasonal Naive 24h:")
print(f"  MAE:          {baseline_mae:.6f} W/m²")
print(f"  RMSE:         {baseline_rmse:.6f} W/m²")
print(f"  Daytime MAE:  {baseline_day_mae:.6f} W/m²")
print(f"  Daytime RMSE: {baseline_day_rmse:.6f} W/m²")

# ------------------------------------------------------------
# Improvement calculations
# ------------------------------------------------------------

def improvement(reference, model):
    return 100.0 * (reference - model) / reference


print("\n" + "-" * 80)
print("IMPROVEMENT OF LoRA 500")
print("-" * 80)

print(
    f"vs Zero-shot Chronos-2:"
)
print(
    f"  MAE:          {improvement(zero_mae, mae):+.2f}%"
)
print(
    f"  RMSE:         {improvement(zero_rmse, rmse):+.2f}%"
)
print(
    f"  Daytime MAE:  {improvement(zero_day_mae, daytime_mae):+.2f}%"
)
print(
    f"  Daytime RMSE: {improvement(zero_day_rmse, daytime_rmse):+.2f}%"
)

print(
    f"\nvs Seasonal Naive:"
)
print(
    f"  MAE:          {improvement(baseline_mae, mae):+.2f}%"
)
print(
    f"  RMSE:         {improvement(baseline_rmse, rmse):+.2f}%"
)
print(
    f"  Daytime MAE:  {improvement(baseline_day_mae, daytime_mae):+.2f}%"
)
print(
    f"  Daytime RMSE: {improvement(baseline_day_rmse, daytime_rmse):+.2f}%"
)

# ------------------------------------------------------------
# Save metrics
# ------------------------------------------------------------

metrics = pd.DataFrame(
    [
        {
            "model": "Chronos-2 LoRA 1000",
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
    OUTPUT_DIR
    / "POLARIS_v0_1_chronos2_lora_1000_test_metrics.csv"
)

metrics.to_csv(metrics_path, index=False)

print("\nMetrics saved:")
print(metrics_path)

print("\n" + "=" * 80)
print("EVALUATION COMPLETE")
print("=" * 80)
