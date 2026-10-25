import numpy as np
import pandas as pd
from timesfm3 import TimesFM3Evaluator, ModelConfig

DATA = "/home/punith-bs/01polaris/(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"

DATES = [
    "2024-04-27",
    "2024-05-10",
    "2024-06-18",
    "2024-06-22",
    "2024-06-23",
]

CONTEXT_LENGTHS = [24, 48, 96, 168]
HORIZON = 24

print("=" * 70)
print("POLARIS — TimesFM 3.0 Context-Length Sensitivity Test")
print("=" * 70)

df = pd.read_csv(DATA)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df = df.sort_values("TIMESTAMP").reset_index(drop=True)

values = df["SW_IN"].to_numpy(dtype=np.float32)
timestamps = df["TIMESTAMP"]

print("\nLoading TimesFM 3.0...")

config = ModelConfig(
    checkpoint_path="google/timesfm-3.0-pytorch",
    per_core_batch_size=1,
    device="cpu",
)

forecaster = TimesFM3Evaluator(config)

print("Model loaded.")

results = []

for date in DATES:

    forecast_start_idx = df.index[
        df["TIMESTAMP"] == pd.Timestamp(date)
    ][0]

    actual = values[
        forecast_start_idx:forecast_start_idx + HORIZON
    ]

    print("\n" + "-" * 70)
    print(f"Forecast date: {date}")
    print(f"Actual peak: {actual.max():.2f} W/m²")

    for context_len in CONTEXT_LENGTHS:

        context_start = forecast_start_idx - context_len

        if context_start < 0:
            print(
                f"Context {context_len}: SKIPPED "
                f"(not enough historical data)"
            )
            continue

        context = values[
            context_start:forecast_start_idx
        ]

        output = list(
            forecaster.predict_batch(
                [context],
                horizon=HORIZON,
                return_quantiles=True,
                use_symmetric_averaging=False,
            )
        )[0]

        forecast = np.asarray(
            output.forecast,
            dtype=np.float32
        )

        mae = np.mean(np.abs(forecast - actual))
        rmse = np.sqrt(
            np.mean((forecast - actual) ** 2)
        )

        peak = forecast.max()

        results.append({
            "date": date,
            "context_hours": context_len,
            "actual_peak": float(actual.max()),
            "timesfm_peak": float(peak),
            "MAE": float(mae),
            "RMSE": float(rmse),
        })

        print(
            f"Context {context_len:3d}h | "
            f"Peak {peak:7.2f} | "
            f"MAE {mae:7.2f} | "
            f"RMSE {rmse:7.2f}"
        )

result_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(
    result_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

print("\nAverage across the five diagnostic dates:")

summary = (
    result_df
    .groupby("context_hours")
    [["MAE", "RMSE"]]
    .mean()
    .reset_index()
)

print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
