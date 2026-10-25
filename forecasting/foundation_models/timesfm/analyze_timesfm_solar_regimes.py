import pandas as pd
import numpy as np

PREDICTIONS = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"
CHRONOS = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_solar_regime_analysis.csv"

print("=" * 70)
print("POLARIS — TimesFM 3.0 Solar Regime Analysis")
print("=" * 70)

tfm = pd.read_csv(PREDICTIONS)
chronos = pd.read_csv(CHRONOS)

# Merge Chronos so the comparison uses exactly the same rows.
df = tfm.merge(
    chronos[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "seasonal_naive_24h",
        ]
    ],
    on=["forecast_start", "horizon_hour", "timestamp"],
    how="inner",
)

# ------------------------------------------------------------
# Solar regime classification
# Based ONLY on actual SW_IN
# ------------------------------------------------------------

def classify(value):
    if value <= 0:
        return "Night / near-zero"
    elif value <= 100:
        return "Low solar"
    elif value <= 400:
        return "Moderate solar"
    else:
        return "High solar"

df["regime"] = df["actual_SW_IN"].apply(classify)

regime_order = [
    "Night / near-zero",
    "Low solar",
    "Moderate solar",
    "High solar",
]

results = []

for regime in regime_order:

    subset = df[df["regime"] == regime]

    actual = subset["actual_SW_IN"].to_numpy()
    tfm_pred = subset["timesfm3"].to_numpy()
    naive_pred = subset["seasonal_naive_24h"].to_numpy()

    tfm_error = tfm_pred - actual
    naive_error = naive_pred - actual

    tfm_mae = np.mean(np.abs(tfm_error))
    tfm_rmse = np.sqrt(np.mean(tfm_error ** 2))

    naive_mae = np.mean(np.abs(naive_error))
    naive_rmse = np.sqrt(np.mean(naive_error ** 2))

    mae_improvement = (
        (naive_mae - tfm_mae) / naive_mae * 100
        if naive_mae != 0 else np.nan
    )

    rmse_improvement = (
        (naive_rmse - tfm_rmse) / naive_rmse * 100
        if naive_rmse != 0 else np.nan
    )

    results.append({
        "regime": regime,
        "rows": len(subset),
        "percentage_of_hours": len(subset) / len(df) * 100,
        "timesfm_MAE": tfm_mae,
        "naive_MAE": naive_mae,
        "MAE_improvement_percent": mae_improvement,
        "timesfm_RMSE": tfm_rmse,
        "naive_RMSE": naive_rmse,
        "RMSE_improvement_percent": rmse_improvement,
    })

result_df = pd.DataFrame(results)

result_df.to_csv(OUTPUT, index=False)

print("\nResults:")
print(
    result_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print("\nInterpretation:")

for _, row in result_df.iterrows():

    if row["MAE_improvement_percent"] > 0:
        mae_result = "WIN"
    else:
        mae_result = "LOSS"

    if row["RMSE_improvement_percent"] > 0:
        rmse_result = "WIN"
    else:
        rmse_result = "LOSS"

    print(
        f"\n{row['regime']}: "
        f"MAE {mae_result}, "
        f"RMSE {rmse_result}"
    )

print("\nSaved to:")
print(OUTPUT)

print("=" * 70)
