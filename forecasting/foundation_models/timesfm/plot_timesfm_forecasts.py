import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# POLARIS — TimesFM 3.0 Forecast Diagnostics
# ============================================================

TIMESFM_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"
CHRONOS_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

OUTPUT_DIR = Path("/home/punith-bs/01polaris/timesfm_forecast_plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOWS = [
    "2024-04-27",
    "2024-05-10",
    "2024-06-18",
    "2024-06-22",
    "2024-06-23",
]

print("=" * 70)
print("POLARIS — TimesFM 3.0 Forecast Diagnostics")
print("=" * 70)

# ------------------------------------------------------------
# Load predictions
# ------------------------------------------------------------

print("\nLoading TimesFM predictions...")
tfm = pd.read_csv(TIMESFM_FILE)
tfm["forecast_start"] = pd.to_datetime(tfm["forecast_start"])
tfm["timestamp"] = pd.to_datetime(tfm["timestamp"])

print("Loading Chronos predictions...")
chronos = pd.read_csv(CHRONOS_FILE)
chronos["forecast_start"] = pd.to_datetime(chronos["forecast_start"])
chronos["timestamp"] = pd.to_datetime(chronos["timestamp"])

# ------------------------------------------------------------
# Merge
# ------------------------------------------------------------

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

print(f"Merged rows: {len(df)}")

# ------------------------------------------------------------
# Generate plots
# ------------------------------------------------------------

for date in WINDOWS:

    start = pd.Timestamp(date)

    subset = df[df["forecast_start"] == start].copy()

    if len(subset) != 24:
        print(f"WARNING: {date}: expected 24 rows, found {len(subset)}")
        continue

    actual = subset["actual_SW_IN"]
    naive = subset["seasonal_naive_24h"]
    chronos = subset["chronos2"]
    timesfm = subset["timesfm3"]

    # Metrics for this window
    chronos_mae = (chronos - actual).abs().mean()
    chronos_rmse = ((chronos - actual) ** 2).mean() ** 0.5

    timesfm_mae = (timesfm - actual).abs().mean()
    timesfm_rmse = ((timesfm - actual) ** 2).mean() ** 0.5

    naive_mae = (naive - actual).abs().mean()
    naive_rmse = ((naive - actual) ** 2).mean() ** 0.5

    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.plot(
        subset["timestamp"],
        actual,
        marker="o",
        linewidth=2,
        label="Actual",
    )

    plt.plot(
        subset["timestamp"],
        naive,
        marker=".",
        linestyle="--",
        label="Seasonal Naive 24h",
    )

    plt.plot(
        subset["timestamp"],
        chronos,
        marker=".",
        linestyle="--",
        label="Chronos-2",
    )

    plt.plot(
        subset["timestamp"],
        timesfm,
        marker=".",
        linestyle="--",
        label="TimesFM 3.0",
    )

    plt.title(
        f"POLARIS — {date} — 24h Forecast Comparison\n"
        f"Chronos MAE={chronos_mae:.1f}, RMSE={chronos_rmse:.1f} | "
        f"TimesFM MAE={timesfm_mae:.1f}, RMSE={timesfm_rmse:.1f} | "
        f"Naive MAE={naive_mae:.1f}, RMSE={naive_rmse:.1f}"
    )

    plt.xlabel("Timestamp")
    plt.ylabel("SW_IN (W/m²)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / f"POLARIS_timesfm3_{date}.png"

    plt.savefig(output, dpi=150)
    plt.close()

    print(f"\nSaved: {output}")

    print(
        f"  Peak actual:   {actual.max():.2f} W/m²"
    )
    print(
        f"  Peak Chronos:  {chronos.max():.2f} W/m²"
    )
    print(
        f"  Peak TimesFM:  {timesfm.max():.2f} W/m²"
    )

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)

print(f"\nPlots saved in:")
print(OUTPUT_DIR)
