import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# POLARIS — Chronos-2 24-Horizon Analysis
# ============================================================

PREDICTIONS = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"
OUTPUT_CSV = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_horizon_analysis.csv"

# ------------------------------------------------------------
# Load predictions
# ------------------------------------------------------------

df = pd.read_csv(PREDICTIONS)

required = [
    "forecast_start",
    "horizon_hour",
    "timestamp",
    "actual_SW_IN",
    "seasonal_naive_24h",
    "persistence_24h",
    "chronos2",
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

# ------------------------------------------------------------
# Basic validation
# ------------------------------------------------------------

if len(df) != 8760:
    raise ValueError(f"Expected 8760 rows, found {len(df)}")

counts = df.groupby("horizon_hour").size()

if len(counts) != 24 or not (counts == 365).all():
    raise ValueError(
        "Horizon structure is invalid. "
        "Expected 24 horizons with 365 rows each."
    )

if df["chronos2"].isna().any():
    raise ValueError("Chronos-2 contains NaN predictions.")

# Locked POLARIS daytime definition
df["daytime"] = df["actual_SW_IN"] > 0

# ------------------------------------------------------------
# Error functions
# ------------------------------------------------------------

def mae(actual, predicted):
    return np.mean(np.abs(actual - predicted))


def rmse(actual, predicted):
    return np.sqrt(np.mean((actual - predicted) ** 2))


# ------------------------------------------------------------
# Horizon-by-horizon analysis
# ------------------------------------------------------------

rows = []

for horizon in range(1, 25):

    h = df[df["horizon_hour"] == horizon]

    actual = h["actual_SW_IN"].to_numpy()

    chronos = h["chronos2"].to_numpy()
    naive = h["seasonal_naive_24h"].to_numpy()
    persistence = h["persistence_24h"].to_numpy()

    # Overall
    chronos_mae = mae(actual, chronos)
    chronos_rmse = rmse(actual, chronos)

    naive_mae = mae(actual, naive)
    naive_rmse = rmse(actual, naive)

    persistence_mae = mae(actual, persistence)
    persistence_rmse = rmse(actual, persistence)

    # Improvement: positive means Chronos is better
    mae_improvement = ((naive_mae - chronos_mae) / naive_mae) * 100
    rmse_improvement = ((naive_rmse - chronos_rmse) / naive_rmse) * 100

    # Daytime
    daytime = h[h["actual_SW_IN"] > 0]

    daytime_actual = daytime["actual_SW_IN"].to_numpy()
    daytime_chronos = daytime["chronos2"].to_numpy()
    daytime_naive = daytime["seasonal_naive_24h"].to_numpy()

    if len(daytime) > 0:

        daytime_chronos_mae = mae(
            daytime_actual,
            daytime_chronos
        )

        daytime_chronos_rmse = rmse(
            daytime_actual,
            daytime_chronos
        )

        daytime_naive_mae = mae(
            daytime_actual,
            daytime_naive
        )

        daytime_naive_rmse = rmse(
            daytime_actual,
            daytime_naive
        )

        daytime_mae_improvement = (
            (daytime_naive_mae - daytime_chronos_mae)
            / daytime_naive_mae
        ) * 100

        daytime_rmse_improvement = (
            (daytime_naive_rmse - daytime_chronos_rmse)
            / daytime_naive_rmse
        ) * 100

    else:

        daytime_chronos_mae = np.nan
        daytime_chronos_rmse = np.nan
        daytime_naive_mae = np.nan
        daytime_naive_rmse = np.nan
        daytime_mae_improvement = np.nan
        daytime_rmse_improvement = np.nan

    rows.append({
        "horizon_hour": horizon,

        "chronos2_MAE": chronos_mae,
        "seasonal_naive_MAE": naive_mae,
        "MAE_improvement_pct": mae_improvement,

        "chronos2_RMSE": chronos_rmse,
        "seasonal_naive_RMSE": naive_rmse,
        "RMSE_improvement_pct": rmse_improvement,

        "persistence_MAE": persistence_mae,
        "persistence_RMSE": persistence_rmse,

        "daytime_chronos2_MAE": daytime_chronos_mae,
        "daytime_seasonal_naive_MAE": daytime_naive_mae,
        "daytime_MAE_improvement_pct": daytime_mae_improvement,

        "daytime_chronos2_RMSE": daytime_chronos_rmse,
        "daytime_seasonal_naive_RMSE": daytime_naive_rmse,
        "daytime_RMSE_improvement_pct": daytime_rmse_improvement,

        "daytime_rows": len(daytime),
    })

results = pd.DataFrame(rows)

# ------------------------------------------------------------
# WIN / LOSS classification
# ------------------------------------------------------------

results["MAE_result"] = np.where(
    results["chronos2_MAE"] < results["seasonal_naive_MAE"],
    "WIN",
    np.where(
        results["chronos2_MAE"] > results["seasonal_naive_MAE"],
        "LOSS",
        "TIE",
    ),
)

results["RMSE_result"] = np.where(
    results["chronos2_RMSE"] < results["seasonal_naive_RMSE"],
    "WIN",
    np.where(
        results["chronos2_RMSE"] > results["seasonal_naive_RMSE"],
        "LOSS",
        "TIE",
    ),
)

results["daytime_MAE_result"] = np.where(
    results["daytime_chronos2_MAE"]
    < results["daytime_seasonal_naive_MAE"],
    "WIN",
    np.where(
        results["daytime_chronos2_MAE"]
        > results["daytime_seasonal_naive_MAE"],
        "LOSS",
        "TIE",
    ),
)

results["daytime_RMSE_result"] = np.where(
    results["daytime_chronos2_RMSE"]
    < results["daytime_seasonal_naive_RMSE"],
    "WIN",
    np.where(
        results["daytime_chronos2_RMSE"]
        > results["daytime_seasonal_naive_RMSE"],
        "LOSS",
        "TIE",
    ),
)

# ------------------------------------------------------------
# Save CSV
# ------------------------------------------------------------

results.to_csv(OUTPUT_CSV, index=False)

# ------------------------------------------------------------
# Print results
# ------------------------------------------------------------

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)
pd.set_option("display.float_format", "{:.3f}".format)

print("\n" + "=" * 100)
print("POLARIS — CHRONOS-2 HORIZON ANALYSIS")
print("=" * 100)

print("\nOVERALL PERFORMANCE BY HORIZON")
print("-" * 100)

print(
    results[
        [
            "horizon_hour",
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
# Win/loss summary
# ------------------------------------------------------------

print("\n" + "=" * 100)
print("WIN / LOSS SUMMARY")
print("=" * 100)

print(
    "\nOverall MAE:"
    f"\n  Wins : {(results['MAE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['MAE_result'] == 'LOSS').sum()}"
    f"\n  Ties : {(results['MAE_result'] == 'TIE').sum()}"
)

print(
    "\nOverall RMSE:"
    f"\n  Wins : {(results['RMSE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['RMSE_result'] == 'LOSS').sum()}"
    f"\n  Ties : {(results['RMSE_result'] == 'TIE').sum()}"
)

print(
    "\nDaytime MAE:"
    f"\n  Wins : {(results['daytime_MAE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['daytime_MAE_result'] == 'LOSS').sum()}"
    f"\n  Ties : {(results['daytime_MAE_result'] == 'TIE').sum()}"
)

print(
    "\nDaytime RMSE:"
    f"\n  Wins : {(results['daytime_RMSE_result'] == 'WIN').sum()}"
    f"\n  Losses: {(results['daytime_RMSE_result'] == 'LOSS').sum()}"
    f"\n  Ties : {(results['daytime_RMSE_result'] == 'TIE').sum()}"
)

# ------------------------------------------------------------
# Best / worst horizons
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

print("\n" + "=" * 100)
print("MOST IMPORTANT HORIZONS")
print("=" * 100)

print(
    f"\nBest MAE improvement:"
    f"  H+{int(best_mae.horizon_hour)}"
    f"  ({best_mae.MAE_improvement_pct:.2f}% better)"
)

print(
    f"Worst MAE improvement:"
    f"  H+{int(worst_mae.horizon_hour)}"
    f"  ({worst_mae.MAE_improvement_pct:.2f}%)"
)

print(
    f"\nBest RMSE improvement:"
    f"  H+{int(best_rmse.horizon_hour)}"
    f"  ({best_rmse.RMSE_improvement_pct:.2f}% better)"
)

print(
    f"Worst RMSE improvement:"
    f"  H+{int(worst_rmse.horizon_hour)}"
    f"  ({worst_rmse.RMSE_improvement_pct:.2f}%)"
)

# ------------------------------------------------------------
# Plot 1 — MAE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    results["horizon_hour"],
    results["chronos2_MAE"],
    marker="o",
    label="Chronos-2",
)

plt.plot(
    results["horizon_hour"],
    results["seasonal_naive_MAE"],
    marker="o",
    label="24h Seasonal Naive",
)

plt.xlabel("Forecast Horizon (hours ahead)")
plt.ylabel("MAE (W/m²)")
plt.title("POLARIS — MAE by Forecast Horizon")
plt.xticks(range(1, 25))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_horizon_MAE.png",
    dpi=200,
)

plt.close()

# ------------------------------------------------------------
# Plot 2 — RMSE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    results["horizon_hour"],
    results["chronos2_RMSE"],
    marker="o",
    label="Chronos-2",
)

plt.plot(
    results["horizon_hour"],
    results["seasonal_naive_RMSE"],
    marker="o",
    label="24h Seasonal Naive",
)

plt.xlabel("Forecast Horizon (hours ahead)")
plt.ylabel("RMSE (W/m²)")
plt.title("POLARIS — RMSE by Forecast Horizon")
plt.xticks(range(1, 25))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_horizon_RMSE.png",
    dpi=200,
)

plt.close()

# ------------------------------------------------------------
# Plot 3 — Improvement
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.axhline(0, linewidth=1)

plt.plot(
    results["horizon_hour"],
    results["MAE_improvement_pct"],
    marker="o",
    label="MAE improvement",
)

plt.plot(
    results["horizon_hour"],
    results["RMSE_improvement_pct"],
    marker="o",
    label="RMSE improvement",
)

plt.xlabel("Forecast Horizon (hours ahead)")
plt.ylabel("Improvement vs Seasonal Naive (%)")
plt.title("POLARIS — Chronos-2 Improvement by Horizon")
plt.xticks(range(1, 25))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_horizon_improvement.png",
    dpi=200,
)

plt.close()

# ------------------------------------------------------------
# Plot 4 — Daytime RMSE
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.plot(
    results["horizon_hour"],
    results["daytime_chronos2_RMSE"],
    marker="o",
    label="Chronos-2",
)

plt.plot(
    results["horizon_hour"],
    results["daytime_seasonal_naive_RMSE"],
    marker="o",
    label="24h Seasonal Naive",
)

plt.xlabel("Forecast Horizon (hours ahead)")
plt.ylabel("Daytime RMSE (W/m²)")
plt.title("POLARIS — Daytime RMSE by Forecast Horizon")
plt.xticks(range(1, 25))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "/home/punith-bs/01polaris/POLARIS_chronos2_daytime_RMSE.png",
    dpi=200,
)

plt.close()

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)

print(f"\nSaved analysis:")
print(OUTPUT_CSV)

print("\nSaved plots:")
print("/home/punith-bs/01polaris/POLARIS_chronos2_horizon_MAE.png")
print("/home/punith-bs/01polaris/POLARIS_chronos2_horizon_RMSE.png")
print("/home/punith-bs/01polaris/POLARIS_chronos2_horizon_improvement.png")
print("/home/punith-bs/01polaris/POLARIS_chronos2_daytime_RMSE.png")
