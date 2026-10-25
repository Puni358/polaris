import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Files
# ============================================================

MOIRAI_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv"

BASELINE_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv"

CHRONOS_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"

TIMESFM_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_timesfm3_predictions.csv"

OUTPUT_DIR = Path.home() / "01polaris" / "forecasting/foundation_models/plots/moirai_forecast_plots"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load files
# ============================================================

print("Loading prediction files...")

moirai = pd.read_csv(MOIRAI_FILE)
baseline = pd.read_csv(BASELINE_FILE)
chronos = pd.read_csv(CHRONOS_FILE)
timesfm = pd.read_csv(TIMESFM_FILE)


# Make timestamps consistent
for df in [moirai, baseline, chronos, timesfm]:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["forecast_start"] = pd.to_datetime(df["forecast_start"])


# ============================================================
# Representative dates
# ============================================================

dates = [
    "2024-04-27",
    "2024-05-10",
    "2024-06-18",
    "2024-06-22",
    "2024-06-23",
]


# ============================================================
# Plot each date
# ============================================================

for date in dates:

    date = pd.Timestamp(date)

    m = moirai[
        moirai["forecast_start"] == date
    ].copy()

    b = baseline[
        baseline["forecast_start"] == date
    ].copy()

    c = chronos[
        chronos["forecast_start"] == date
    ].copy()

    t = timesfm[
        timesfm["forecast_start"] == date
    ].copy()


    # --------------------------------------------------------
    # Merge on timestamp
    # --------------------------------------------------------

    plot_df = b[
        [
            "timestamp",
            "actual_SW_IN",
            "seasonal_naive_24h",
        ]
    ].copy()

    plot_df = plot_df.merge(
        c[
            [
                "timestamp",
                "chronos2",
            ]
        ],
        on="timestamp",
        how="left",
    )

    plot_df = plot_df.merge(
        t[
            [
                "timestamp",
                "timesfm3",
            ]
        ],
        on="timestamp",
        how="left",
    )

    plot_df = plot_df.merge(
        m[
            [
                "timestamp",
                "moirai2",
            ]
        ],
        on="timestamp",
        how="left",
    )


    # --------------------------------------------------------
    # Metrics for this window
    # --------------------------------------------------------

    actual = plot_df["actual_SW_IN"].to_numpy()

    naive = plot_df["seasonal_naive_24h"].to_numpy()
    chronos_pred = plot_df["chronos2"].to_numpy()
    timesfm_pred = plot_df["timesfm3"].to_numpy()
    moirai_pred = plot_df["moirai2"].to_numpy()


    def mae(pred):
        return np.mean(np.abs(pred - actual))


    def rmse(pred):
        return np.sqrt(
            np.mean((pred - actual) ** 2)
        )


    naive_mae = mae(naive)
    naive_rmse = rmse(naive)

    chronos_mae = mae(chronos_pred)
    chronos_rmse = rmse(chronos_pred)

    timesfm_mae = mae(timesfm_pred)
    timesfm_rmse = rmse(timesfm_pred)

    moirai_mae = mae(moirai_pred)
    moirai_rmse = rmse(moirai_pred)


    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    plt.figure(figsize=(17, 8))

    plt.plot(
        plot_df["timestamp"],
        actual,
        marker="o",
        linewidth=2.5,
        label="Actual",
    )

    plt.plot(
        plot_df["timestamp"],
        naive,
        marker="o",
        linestyle="--",
        linewidth=1.8,
        label="Seasonal Naive 24h",
    )

    plt.plot(
        plot_df["timestamp"],
        chronos_pred,
        marker="o",
        linestyle="--",
        linewidth=1.8,
        label="Chronos-2",
    )

    plt.plot(
        plot_df["timestamp"],
        timesfm_pred,
        marker="o",
        linestyle="--",
        linewidth=1.8,
        label="TimesFM 3.0",
    )

    plt.plot(
        plot_df["timestamp"],
        moirai_pred,
        marker="o",
        linestyle="--",
        linewidth=1.8,
        label="Moirai 2.0 R-small",
    )


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = (
        f"POLARIS — {date.strftime('%Y-%m-%d')} — "
        f"24h Forecast Comparison\n"
        f"Chronos MAE={chronos_mae:.1f}, RMSE={chronos_rmse:.1f} | "
        f"TimesFM MAE={timesfm_mae:.1f}, RMSE={timesfm_rmse:.1f} | "
        f"Moirai MAE={moirai_mae:.1f}, RMSE={moirai_rmse:.1f} | "
        f"Naive MAE={naive_mae:.1f}, RMSE={naive_rmse:.1f}"
    )

    plt.title(title, fontsize=15)

    plt.xlabel("Timestamp", fontsize=12)

    plt.ylabel(
        "SW_IN (W/m²)",
        fontsize=12,
    )

    plt.grid(True, alpha=0.3)

    plt.legend(
        loc="upper right",
        fontsize=10,
    )

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.tight_layout()


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR
        / f"POLARIS_moirai2_{date.strftime('%Y-%m-%d')}.png"
    )

    plt.savefig(
        output_file,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


print()
print("========================================")
print("MOIRAI FORECAST PLOTS COMPLETE")
print("========================================")
print("Output directory:")
print(OUTPUT_DIR)
