import pandas as pd
import numpy as np

TIMESFM = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"
CHRONOS = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_horizon_analysis.csv"

print("=" * 70)
print("POLARIS — TimesFM 3.0 Horizon Analysis")
print("=" * 70)

tfm = pd.read_csv(TIMESFM)
chronos = pd.read_csv(CHRONOS)

df = tfm.merge(
    chronos[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "seasonal_naive_24h",
            "chronos2",
        ]
    ],
    on=["forecast_start", "horizon_hour", "timestamp"],
    how="inner",
)

results = []

for h in range(1, 25):

    subset = df[df["horizon_hour"] == h]

    actual = subset["actual_SW_IN"].to_numpy()
    tfm_pred = subset["timesfm3"].to_numpy()
    naive_pred = subset["seasonal_naive_24h"].to_numpy()

    tfm_error = tfm_pred - actual
    naive_error = naive_pred - actual

    tfm_mae = np.mean(np.abs(tfm_error))
    naive_mae = np.mean(np.abs(naive_error))

    tfm_rmse = np.sqrt(np.mean(tfm_error ** 2))
    naive_rmse = np.sqrt(np.mean(naive_error ** 2))

    mae_improvement = (
        (naive_mae - tfm_mae) / naive_mae * 100
        if naive_mae > 1e-12 else np.nan
    )

    rmse_improvement = (
        (naive_rmse - tfm_rmse) / naive_rmse * 100
        if naive_rmse > 1e-12 else np.nan
    )

    results.append({
        "horizon_hour": h,
        "timesfm_MAE": tfm_mae,
        "naive_MAE": naive_mae,
        "MAE_improvement_percent": mae_improvement,
        "timesfm_RMSE": tfm_rmse,
        "naive_RMSE": naive_rmse,
        "RMSE_improvement_percent": rmse_improvement,
    })

result_df = pd.DataFrame(results)

result_df.to_csv(OUTPUT, index=False)

print("\nHorizon results:")
print(
    result_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

mae_wins = (result_df["MAE_improvement_percent"] > 0).sum()
rmse_wins = (result_df["RMSE_improvement_percent"] > 0).sum()

print("\n" + "-" * 70)
print(f"MAE wins : {mae_wins}/24")
print(f"RMSE wins: {rmse_wins}/24")

best_mae = result_df.loc[
    result_df["MAE_improvement_percent"].idxmax()
]

worst_mae = result_df.loc[
    result_df["MAE_improvement_percent"].idxmin()
]

best_rmse = result_df.loc[
    result_df["RMSE_improvement_percent"].idxmax()
]

worst_rmse = result_df.loc[
    result_df["RMSE_improvement_percent"].idxmin()
]

print("\nBest MAE horizon:")
print(best_mae.to_string())

print("\nWorst MAE horizon:")
print(worst_mae.to_string())

print("\nBest RMSE horizon:")
print(best_rmse.to_string())

print("\nWorst RMSE horizon:")
print(worst_rmse.to_string())

print("\nSaved to:")
print(OUTPUT)

print("=" * 70)
