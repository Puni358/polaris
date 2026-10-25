import pandas as pd
import numpy as np

PREDICTIONS = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"
OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_metrics.csv"

df = pd.read_csv(PREDICTIONS)

actual = df["actual_SW_IN"].to_numpy()
pred = df["timesfm3"].to_numpy()

errors = pred - actual

mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(errors ** 2))

# Exact POLARIS daytime definition
daytime = actual > 0

daytime_mae = np.mean(np.abs(errors[daytime]))
daytime_rmse = np.sqrt(np.mean(errors[daytime] ** 2))

metrics = pd.DataFrame([{
    "model": "TimesFM-3.0",
    "evaluation_windows": df["forecast_start"].nunique(),
    "evaluation_hours": len(df),
    "MAE_W_m2": mae,
    "RMSE_W_m2": rmse,
    "daytime_MAE_W_m2": daytime_mae,
    "daytime_RMSE_W_m2": daytime_rmse,
}])

metrics.to_csv(OUTPUT, index=False)

print("=" * 70)
print("POLARIS — TimesFM 3.0 Metrics")
print("=" * 70)

print(f"\nEvaluation windows : {df['forecast_start'].nunique()}")
print(f"Evaluation hours   : {len(df)}")

print(f"\nOverall MAE        : {mae:.6f} W/m²")
print(f"Overall RMSE       : {rmse:.6f} W/m²")

print(f"\nDaytime MAE        : {daytime_mae:.6f} W/m²")
print(f"Daytime RMSE       : {daytime_rmse:.6f} W/m²")

print(f"\nSaved to:")
print(OUTPUT)

print("=" * 70)
