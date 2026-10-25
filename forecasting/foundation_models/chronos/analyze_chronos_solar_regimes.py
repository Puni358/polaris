import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# POLARIS — Chronos-2 Solar-Regime Analysis
# ============================================================

INPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_solar_regime_analysis.csv"

# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

required = [
    "actual_SW_IN",
    "chronos2",
    "seasonal_naive_24h",
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

if len(df) != 8760:
    raise ValueError(f"Expected 8760 rows, found {len(df)}")

# ------------------------------------------------------------
# Solar regime classification
# ------------------------------------------------------------

def classify_solar(sw):

    if sw <= 0:
        return "Night / near-zero"

    elif sw <= 100:
        return "Low solar"

    elif sw <= 400:
        return "Moderate solar"

    else:
        return "High solar"


df["solar_regime"] = df["actual_SW_IN"].apply(classify_solar)

regime_order = [
    "Night / near-zero",
    "Low solar",
    "Moderate solar",
    "High solar",
]

# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

rows = []

for regime in regime_order:

    d = df[df["solar_regime"] == regime]

    actual = d["actual_SW_IN"].to_numpy()
    chronos = d["chronos2"].to_numpy()
    naive = d["seasonal_naive_24h"].to_numpy()

    chronos_mae = np.mean(np.abs(actual - chronos))
    chronos_rmse = np.sqrt(np.mean((actual - chronos) ** 2))

    naive_mae = np.mean(np.abs(actual - naive))
    naive_rmse = np.sqrt(np.mean((actual - naive) ** 2))

    mae_improvement = (
        (naive_mae - chronos_mae) / naive_mae
    ) * 100

    rmse_improvement = (
        (naive_rmse - chronos_rmse) / naive_rmse
    ) * 100

    rows.append({
        "solar_regime": regime,
        "observations": len(d),
        "percentage_of_dataset": len(d) / len(df) * 100,

        "chronos2_MAE": chronos_mae,
        "seasonal_naive_MAE": naive_mae,
        "MAE_improvement_pct": mae_improvement,

        "chronos2_RMSE": chronos_rmse,
        "seasonal_naive_RMSE": naive_rmse,
        "RMSE_improvement_pct": rmse_improvement,

        "MAE_result": (
            "WIN"
            if chronos_mae < naive_mae
            else "LOSS"
        ),

        "RMSE_result": (
            "WIN"
            if chronos_rmse < naive_rmse
            else "LOSS"
        ),
    })

results = pd.DataFrame(rows)

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

results.to_csv(OUTPUT, index=False)

# ------------------------------------------------------------
# Print
# ------------------------------------------------------------

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)
pd.set_option("display.float_format", "{:.3f}".format)

print("\n" + "=" * 110)
print("POLARIS — CHRONOS-2 SOLAR-REGIME ANALYSIS")
print("=" * 110)

print("\nREGIME PERFORMANCE")
print("-" * 110)

print(
    results[
        [
            "solar_regime",
            "observations",
            "percentage_of_dataset",
            "chronos2_MAE",
            "seasonal_naive_MAE",
            "MAE_improvement_pct",
            "MAE_result",
            "chronos2_RMSE",
            "seasonal_naive_RMSE",
            "RMSE_improvement_pct",
            "RMSE_result",
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# Counts
# ------------------------------------------------------------

print("\n" + "=" * 110)
print("WIN / LOSS SUMMARY")
print("=" * 110)

print(
    "\nMAE:"
    f"\n  Wins : {(results['MAE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['MAE_result'] == 'LOSS').sum()}"
)

print(
    "\nRMSE:"
    f"\n  Wins : {(results['RMSE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['RMSE_result'] == 'LOSS').sum()}"
)

# ------------------------------------------------------------
# Best / worst regimes
# ------------------------------------------------------------

best_mae = results.loc[
    results["MAE_improvement_pct"].idxmax()
]

worst_mae = results.loc[
    results["MAE_improvement_pct"].idxmin()
]

best_rmse = results.loc[
    results["RMSE_improvement_pct"].idxmax()
]

worst_rmse = results.loc[
    results["RMSE_improvement_pct"].idxmin()
]

print("\n" + "=" * 110)
print("BEST / WORST REGIMES")
print("=" * 110)

print(
    f"\nBest MAE regime:"
    f" {best_mae.solar_regime}"
    f" ({best_mae.MAE_improvement_pct:.2f}% improvement)"
)

print(
    f"Worst MAE regime:"
    f" {worst_mae.solar_regime}"
    f" ({worst_mae.MAE_improvement_pct:.2f}%)"
)

print(
    f"\nBest RMSE regime:"
    f" {best_rmse.solar_regime}"
    f" ({best_rmse.RMSE_improvement_pct:.2f}% improvement)"
)

print(
    f"Worst RMSE regime:"
    f" {worst_rmse.solar_regime}"
    f" ({worst_rmse.RMSE_improvement_pct:.2f}%)"
)

# ------------------------------------------------------------
# Plot 1 — MAE
# ------------------------------------------------------------

x = np.arange(len(results))

plt.figure(figsize=(10, 6))

plt.bar(
    x - 0.18,
    results["chronos2_MAE"],
    width=0.36,
    label="Chronos-2",
)

plt.bar(
    x + 0.18,
    results["seasonal_naive_MAE"],
    width=0.36,
    label="24h Seasonal Naive",
)

plt.xticks(x, results["solar_regime"], rotation=15)

plt.xlabel("Actual Solar Radiation Regime")
plt.ylabel("MAE (W/m²)")
plt.title("POLARIS — MAE by Solar Regime")

plt.grid(True, axis="y", alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_solar_regime_MAE.png",
    dpi=200,
)

plt.close()

# ------------------------------------------------------------
# Plot 2 — RMSE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    x - 0.18,
    results["chronos2_RMSE"],
    width=0.36,
    label="Chronos-2",
)

plt.bar(
    x + 0.18,
    results["seasonal_naive_RMSE"],
    width=0.36,
    label="24h Seasonal Naive",
)

plt.xticks(x, results["solar_regime"], rotation=15)

plt.xlabel("Actual Solar Radiation Regime")
plt.ylabel("RMSE (W/m²)")
plt.title("POLARIS — RMSE by Solar Regime")

plt.grid(True, axis="y", alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_solar_regime_RMSE.png",
    dpi=200,
)

plt.close()

print("\n" + "=" * 110)
print("DONE")
print("=" * 110)

print("\nSaved analysis:")
print(OUTPUT)

print("\nSaved plots:")
print(
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_chronos2_solar_regime_MAE.png"
)

print(
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_chronos2_solar_regime_RMSE.png"
)
