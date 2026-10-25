import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE = Path("/home/punith-bs/01polaris")

BASELINE_FILE = BASE / "forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"
CHRONOS_FILE = BASE / "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"
TIMESFM_FILE = BASE / "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"
MOIRAI_FILE = BASE / "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"

OUTPUT_DIR = BASE / "final_model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading benchmark files...")

baseline = pd.read_csv(BASELINE_FILE)
chronos = pd.read_csv(CHRONOS_FILE)
timesfm = pd.read_csv(TIMESFM_FILE)
moirai = pd.read_csv(MOIRAI_FILE)

for df in [baseline, chronos, timesfm, moirai]:

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["forecast_start"] = pd.to_datetime(
        df["forecast_start"]
    )


# ============================================================
# CREATE MASTER DATAFRAME
# ============================================================

df = baseline[
    [
        "forecast_start",
        "horizon_hour",
        "timestamp",
        "actual_SW_IN",
        "seasonal_naive_24h",
    ]
].copy()


df = df.merge(
    chronos[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "chronos2",
        ]
    ],
    on=[
        "forecast_start",
        "horizon_hour",
        "timestamp",
    ],
    how="left",
)


df = df.merge(
    timesfm[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "timesfm3",
        ]
    ],
    on=[
        "forecast_start",
        "horizon_hour",
        "timestamp",
    ],
    how="left",
)


df = df.merge(
    moirai[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "moirai2",
        ]
    ],
    on=[
        "forecast_start",
        "horizon_hour",
        "timestamp",
    ],
    how="left",
)


print("Master rows:", len(df))


# ============================================================
# MODEL DEFINITIONS
# ============================================================

models = {
    "Chronos-2": "chronos2",
    "TimesFM 3.0": "timesfm3",
    "Moirai 2.0 R-small": "moirai2",
    "Seasonal Naive 24h": "seasonal_naive_24h",
}


# ============================================================
# 1. OVERALL LEADERBOARD
# ============================================================

print()
print("========================================")
print("1. OVERALL LEADERBOARD")
print("========================================")


leaderboard = []


for model_name, column in models.items():

    actual = df["actual_SW_IN"].to_numpy()
    pred = df[column].to_numpy()

    error = pred - actual

    mae = np.mean(np.abs(error))

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    daytime = actual > 0

    daytime_error = (
        pred[daytime] - actual[daytime]
    )

    daytime_mae = np.mean(
        np.abs(daytime_error)
    )

    daytime_rmse = np.sqrt(
        np.mean(daytime_error ** 2)
    )

    leaderboard.append(
        {
            "model": model_name,
            "MAE_W_m2": mae,
            "RMSE_W_m2": rmse,
            "daytime_MAE_W_m2": daytime_mae,
            "daytime_RMSE_W_m2": daytime_rmse,
        }
    )


leaderboard_df = pd.DataFrame(leaderboard)

leaderboard_df = leaderboard_df.sort_values(
    "MAE_W_m2"
).reset_index(drop=True)

leaderboard_df.insert(
    0,
    "rank",
    np.arange(1, len(leaderboard_df) + 1),
)


print(
    leaderboard_df.to_string(index=False)
)


leaderboard_df.to_csv(
    OUTPUT_DIR / "final_leaderboard.csv",
    index=False,
)


# ------------------------------------------------------------
# Leaderboard plot
# ------------------------------------------------------------

x = np.arange(len(leaderboard_df))

width = 0.36

plt.figure(figsize=(13, 7))

plt.bar(
    x - width / 2,
    leaderboard_df["MAE_W_m2"],
    width,
    label="MAE",
)

plt.bar(
    x + width / 2,
    leaderboard_df["RMSE_W_m2"],
    width,
    label="RMSE",
)

plt.xticks(
    x,
    leaderboard_df["model"],
    rotation=15,
)

plt.ylabel("Error (W/m²)")

plt.title(
    "POLARIS — Overall Forecasting Leaderboard"
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "01_overall_leaderboard.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 2. HORIZON MAE
# ============================================================

print()
print("========================================")
print("2. HORIZON MAE")
print("========================================")


horizon_rows = []


for horizon in range(1, 25):

    h = df[
        df["horizon_hour"] == horizon
    ]

    actual = h["actual_SW_IN"].to_numpy()

    row = {
        "horizon_hour": horizon
    }

    for model_name, column in models.items():

        pred = h[column].to_numpy()

        mae = np.mean(
            np.abs(pred - actual)
        )

        row[
            model_name + "_MAE_W_m2"
        ] = mae

    horizon_rows.append(row)


horizon_df = pd.DataFrame(
    horizon_rows
)


horizon_df.to_csv(
    OUTPUT_DIR / "final_horizon_comparison.csv",
    index=False,
)


# ------------------------------------------------------------
# Horizon MAE plot
# ------------------------------------------------------------

plt.figure(figsize=(14, 8))

for model_name in models:

    plt.plot(
        horizon_df["horizon_hour"],
        horizon_df[
            model_name + "_MAE_W_m2"
        ],
        marker="o",
        linewidth=2,
        label=model_name,
    )


plt.xlabel("Forecast horizon (hours)")

plt.ylabel("MAE (W/m²)")

plt.title(
    "POLARIS — MAE by Forecast Horizon"
)

plt.xticks(
    range(1, 25)
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "02_horizon_MAE.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 3. HORIZON RMSE
# ============================================================

print()
print("========================================")
print("3. HORIZON RMSE")
print("========================================")


horizon_rmse_rows = []


for horizon in range(1, 25):

    h = df[
        df["horizon_hour"] == horizon
    ]

    actual = h["actual_SW_IN"].to_numpy()

    row = {
        "horizon_hour": horizon
    }

    for model_name, column in models.items():

        pred = h[column].to_numpy()

        rmse = np.sqrt(
            np.mean(
                (pred - actual) ** 2
            )
        )

        row[
            model_name + "_RMSE_W_m2"
        ] = rmse

    horizon_rmse_rows.append(row)


horizon_rmse_df = pd.DataFrame(
    horizon_rmse_rows
)


# ------------------------------------------------------------
# Horizon RMSE plot
# ------------------------------------------------------------

plt.figure(figsize=(14, 8))

for model_name in models:

    plt.plot(
        horizon_rmse_df["horizon_hour"],
        horizon_rmse_df[
            model_name + "_RMSE_W_m2"
        ],
        marker="o",
        linewidth=2,
        label=model_name,
    )


plt.xlabel("Forecast horizon (hours)")

plt.ylabel("RMSE (W/m²)")

plt.title(
    "POLARIS — RMSE by Forecast Horizon"
)

plt.xticks(
    range(1, 25)
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "03_horizon_RMSE.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 4 + 5. SOLAR REGIME ANALYSIS
# ============================================================

print()
print("========================================")
print("4 + 5. SOLAR REGIME ANALYSIS")
print("========================================")


def solar_regime(value):

    if value <= 0:
        return "Night / near-zero"

    elif value <= 100:
        return "Low solar"

    elif value <= 400:
        return "Moderate solar"

    else:
        return "High solar"


df["solar_regime"] = df[
    "actual_SW_IN"
].apply(solar_regime)


regime_order = [
    "Night / near-zero",
    "Low solar",
    "Moderate solar",
    "High solar",
]


regime_rows = []


for regime in regime_order:

    r = df[
        df["solar_regime"] == regime
    ]

    actual = r["actual_SW_IN"].to_numpy()

    row = {
        "solar_regime": regime,
        "count": len(r),
        "percentage_of_hours": (
            len(r) / len(df) * 100
        ),
    }

    for model_name, column in models.items():

        pred = r[column].to_numpy()

        error = pred - actual

        mae = np.mean(
            np.abs(error)
        )

        rmse = np.sqrt(
            np.mean(error ** 2)
        )

        row[
            model_name + "_MAE_W_m2"
        ] = mae

        row[
            model_name + "_RMSE_W_m2"
        ] = rmse

    regime_rows.append(row)


regime_df = pd.DataFrame(
    regime_rows
)


regime_df.to_csv(
    OUTPUT_DIR
    / "final_solar_regime_comparison.csv",
    index=False,
)


print(
    regime_df.to_string(index=False)
)


# ------------------------------------------------------------
# Solar regime MAE
# ------------------------------------------------------------

x = np.arange(
    len(regime_df)
)

width = 0.20

plt.figure(figsize=(14, 8))


for i, model_name in enumerate(models):

    plt.bar(
        x + (i - 1.5) * width,
        regime_df[
            model_name + "_MAE_W_m2"
        ],
        width,
        label=model_name,
    )


plt.xticks(
    x,
    regime_df["solar_regime"],
    rotation=15,
)

plt.ylabel("MAE (W/m²)")

plt.title(
    "POLARIS — Solar-Regime MAE Comparison"
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "04_solar_regime_MAE.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# Solar regime RMSE
# ------------------------------------------------------------

plt.figure(figsize=(14, 8))


for i, model_name in enumerate(models):

    plt.bar(
        x + (i - 1.5) * width,
        regime_df[
            model_name + "_RMSE_W_m2"
        ],
        width,
        label=model_name,
    )


plt.xticks(
    x,
    regime_df["solar_regime"],
    rotation=15,
)

plt.ylabel("RMSE (W/m²)")

plt.title(
    "POLARIS — Solar-Regime RMSE Comparison"
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "05_solar_regime_RMSE.png",
    dpi=200,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 6. REPRESENTATIVE FORECAST PLOTS
# ============================================================

print()
print("========================================")
print("6. REPRESENTATIVE FORECAST PLOTS")
print("========================================")


dates = [
    "2024-04-27",
    "2024-05-10",
    "2024-06-18",
    "2024-06-22",
    "2024-06-23",
]


for date in dates:

    date = pd.Timestamp(date)

    p = df[
        df["forecast_start"] == date
    ].copy()

    actual = p["actual_SW_IN"].to_numpy()


    # --------------------------------------------------------
    # Window metrics
    # --------------------------------------------------------

    window_metrics = {}

    for model_name, column in models.items():

        pred = p[column].to_numpy()

        error = pred - actual

        window_metrics[model_name] = (
            np.mean(np.abs(error)),
            np.sqrt(np.mean(error ** 2)),
        )


    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    plt.figure(figsize=(17, 8))


    plt.plot(
        p["timestamp"],
        actual,
        marker="o",
        linewidth=2.8,
        label="Actual",
    )


    for model_name, column in models.items():

        plt.plot(
            p["timestamp"],
            p[column],
            marker="o",
            linestyle="--",
            linewidth=1.8,
            label=model_name,
        )


    # --------------------------------------------------------
    # Metrics in title
    # --------------------------------------------------------

    title_lines = []

    for model_name in [
        "Chronos-2",
        "TimesFM 3.0",
        "Moirai 2.0 R-small",
        "Seasonal Naive 24h",
    ]:

        mae, rmse = window_metrics[
            model_name
        ]

        title_lines.append(
            f"{model_name} "
            f"MAE={mae:.1f}, RMSE={rmse:.1f}"
        )


    title = (
        f"POLARIS — {date.strftime('%Y-%m-%d')} — "
        f"24h Forecast Comparison\n"
        + " | ".join(title_lines)
    )


    plt.title(
        title,
        fontsize=13,
    )

    plt.xlabel(
        "Timestamp",
        fontsize=12,
    )

    plt.ylabel(
        "SW_IN (W/m²)",
        fontsize=12,
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend(
        loc="upper right"
    )

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.tight_layout()


    output = (
        OUTPUT_DIR
        / f"06_forecast_{date.strftime('%Y-%m-%d')}.png"
    )


    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print("Saved:", output)


# ============================================================
# FINAL VERIFICATION
# ============================================================

print()
print("========================================")
print("FINAL POLARIS COMPARISON COMPLETE")
print("========================================")

print()
print("Output directory:")
print(OUTPUT_DIR)

print()
print("Files:")

for file in sorted(OUTPUT_DIR.iterdir()):

    print(
        f"  {file.name}"
    )

print()
print("========================================")
print("FINAL LEADERBOARD")
print("========================================")

print(
    leaderboard_df.to_string(index=False)
)

print()
print("Done.")
