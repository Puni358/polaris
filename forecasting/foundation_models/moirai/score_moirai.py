import pandas as pd
import numpy as np


INPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_metrics.csv"


df = pd.read_csv(INPUT)


actual = df["actual_SW_IN"].to_numpy()
pred = df["moirai2"].to_numpy()


# ============================================================
# Overall metrics
# ============================================================

errors = pred - actual

mae = np.mean(np.abs(errors))
rmse = np.sqrt(np.mean(errors ** 2))


# ============================================================
# Daytime metrics
# Locked definition:
# actual_SW_IN > 0
# ============================================================

daytime = actual > 0

daytime_actual = actual[daytime]
daytime_pred = pred[daytime]

daytime_errors = daytime_pred - daytime_actual

daytime_mae = np.mean(np.abs(daytime_errors))
daytime_rmse = np.sqrt(
    np.mean(daytime_errors ** 2)
)


# ============================================================
# Save metrics
# ============================================================

metrics = pd.DataFrame(
    [
        {
            "model": "Moirai-2.0-R-small",
            "MAE_W_m2": mae,
            "RMSE_W_m2": rmse,
            "daytime_MAE_W_m2": daytime_mae,
            "daytime_RMSE_W_m2": daytime_rmse,
        }
    ]
)

metrics.to_csv(
    OUTPUT,
    index=False
)


# ============================================================
# Display
# ============================================================

print()
print("========================================")
print("MOIRAI 2.0 R-SMALL METRICS")
print("========================================")

print()
print(f"Overall MAE:       {mae:.6f} W/m²")
print(f"Overall RMSE:      {rmse:.6f} W/m²")
print(f"Daytime MAE:       {daytime_mae:.6f} W/m²")
print(f"Daytime RMSE:      {daytime_rmse:.6f} W/m²")

print()
print("Daytime observations:")
print(f"{daytime.sum()} / {len(actual)}")

print()
print("Saved:")
print(OUTPUT)
