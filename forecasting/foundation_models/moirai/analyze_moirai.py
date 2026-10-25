import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Files
# ============================================================

MOIRAI_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv"

BASELINE_FILE = "/home/punith-bs/01polaris/POLARIS_v0_1_fixed_24h_benchmark.csv"

OUTPUT_DIR = Path.home() / "01polaris" / "moirai_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load data
# ============================================================

print("Loading data...")

moirai = pd.read_csv(MOIRAI_FILE)
baseline = pd.read_csv(BASELINE_FILE)

moirai["timestamp"] = pd.to_datetime(moirai["timestamp"])
baseline["timestamp"] = pd.to_datetime(baseline["timestamp"])

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

print("Rows:", len(df))


# ============================================================
# Error columns
# ============================================================

df["moirai_error"] = (
    df["moirai2"] - df["actual_SW_IN"]
)

df["naive_error"] = (
    df["seasonal_naive_24h"] - df["actual_SW_IN"]
)

df["moirai_abs_error"] = np.abs(
    df["moirai_error"]
)

df["naive_abs_error"] = np.abs(
    df["naive_error"]
)

df["moirai_sq_error"] = (
    df["moirai_error"] ** 2
)

df["naive_sq_error"] = (
    df["naive_error"] ** 2
)


# ============================================================
# 1. HORIZON ANALYSIS
# ============================================================

print()
print("========================================")
print("HORIZON ANALYSIS")
print("========================================")

horizon_results = []

for horizon in range(1, 25):

    h = df[df["horizon_hour"] == horizon]

    moirai_mae = h["moirai_abs_error"].mean()

    moirai_rmse = np.sqrt(
        h["moirai_sq_error"].mean()
    )

    naive_mae = h["naive_abs_error"].mean()

    naive_rmse = np.sqrt(
        h["naive_sq_error"].mean()
    )

    mae_improvement = (
        (naive_mae - moirai_mae)
        / naive_mae
        * 100
    )

    rmse_improvement = (
        (naive_rmse - moirai_rmse)
        / naive_rmse
        * 100
    )

    horizon_results.append(
        {
            "horizon_hour": horizon,
            "moirai_MAE_W_m2": moirai_mae,
            "naive_MAE_W_m2": naive_mae,
            "MAE_improvement_percent": mae_improvement,
            "moirai_RMSE_W_m2": moirai_rmse,
            "naive_RMSE_W_m2": naive_rmse,
            "RMSE_improvement_percent": rmse_improvement,
        }
    )


horizon_df = pd.DataFrame(horizon_results)

horizon_file = (
    OUTPUT_DIR
    / "POLARIS_v0_1_moirai2_horizon_analysis.csv"
)

horizon_df.to_csv(
    horizon_file,
    index=False,
)


print()
print(horizon_df.to_string(index=False))


# ============================================================
# Horizon win/loss summary
# ============================================================

mae_wins = (
    horizon_df["MAE_improvement_percent"] > 0
).sum()

rmse_wins = (
    horizon_df["RMSE_improvement_percent"] > 0
).sum()

print()
print(
    f"Moirai MAE wins: {mae_wins}/24 horizons"
)

print(
    f"Moirai RMSE wins: {rmse_wins}/24 horizons"
)


# ============================================================
# Horizon MAE plot
# ============================================================

plt.figure(figsize=(13, 7))

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["moirai_MAE_W_m2"],
    marker="o",
    linewidth=2,
    label="Moirai 2.0 R-small",
)

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["naive_MAE_W_m2"],
    marker="o",
    linestyle="--",
    linewidth=2,
    label="Seasonal Naive 24h",
)

plt.xlabel("Forecast horizon (hours)")
plt.ylabel("MAE (W/m²)")
plt.title("POLARIS — Moirai 2.0 R-small Horizon MAE")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "POLARIS_moirai2_horizon_MAE.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# Horizon RMSE plot
# ============================================================

plt.figure(figsize=(13, 7))

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["moirai_RMSE_W_m2"],
    marker="o",
    linewidth=2,
    label="Moirai 2.0 R-small",
)

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["naive_RMSE_W_m2"],
    marker="o",
    linestyle="--",
    linewidth=2,
    label="Seasonal Naive 24h",
)

plt.xlabel("Forecast horizon (hours)")
plt.ylabel("RMSE (W/m²)")
plt.title("POLARIS — Moirai 2.0 R-small Horizon RMSE")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "POLARIS_moirai2_horizon_RMSE.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# Horizon improvement plot
# ============================================================

plt.figure(figsize=(13, 7))

plt.axhline(
    0,
    linewidth=1,
)

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["MAE_improvement_percent"],
    marker="o",
    linewidth=2,
    label="MAE improvement",
)

plt.plot(
    horizon_df["horizon_hour"],
    horizon_df["RMSE_improvement_percent"],
    marker="o",
    linewidth=2,
    label="RMSE improvement",
)

plt.xlabel("Forecast horizon (hours)")
plt.ylabel("Improvement vs Seasonal Naive (%)")
plt.title(
    "POLARIS — Moirai 2.0 R-small Improvement by Horizon"
)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "POLARIS_moirai2_horizon_improvement.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# 2. SOLAR REGIME ANALYSIS
# ============================================================

print()
print("========================================")
print("SOLAR REGIME ANALYSIS")
print("========================================")


def classify_solar_regime(value):

    if value <= 0:
        return "Night / near-zero"

    elif value <= 100:
        return "Low solar"

    elif value <= 400:
        return "Moderate solar"

    else:
        return "High solar"


df["solar_regime"] = df["actual_SW_IN"].apply(
    classify_solar_regime
)


regime_order = [
    "Night / near-zero",
    "Low solar",
    "Moderate solar",
    "High solar",
]


regime_results = []

for regime in regime_order:

    r = df[
        df["solar_regime"] == regime
    ]

    count = len(r)

    moirai_mae = r["moirai_abs_error"].mean()

    moirai_rmse = np.sqrt(
        r["moirai_sq_error"].mean()
    )

    naive_mae = r["naive_abs_error"].mean()

    naive_rmse = np.sqrt(
        r["naive_sq_error"].mean()
    )

    if naive_mae > 1e-12:

        mae_improvement = (
            (naive_mae - moirai_mae)
            / naive_mae
            * 100
        )

    else:

        mae_improvement = np.nan


    if naive_rmse > 1e-12:

        rmse_improvement = (
            (naive_rmse - moirai_rmse)
            / naive_rmse
            * 100
        )

    else:

        rmse_improvement = np.nan


    regime_results.append(
        {
            "solar_regime": regime,
            "count": count,
            "percentage_of_all_hours": (
                count / len(df) * 100
            ),
            "moirai_MAE_W_m2": moirai_mae,
            "naive_MAE_W_m2": naive_mae,
            "MAE_improvement_percent": mae_improvement,
            "moirai_RMSE_W_m2": moirai_rmse,
            "naive_RMSE_W_m2": naive_rmse,
            "RMSE_improvement_percent": rmse_improvement,
        }
    )


regime_df = pd.DataFrame(
    regime_results
)


regime_file = (
    OUTPUT_DIR
    / "POLARIS_v0_1_moirai2_solar_regime_analysis.csv"
)

regime_df.to_csv(
    regime_file,
    index=False,
)


print()
print(
    regime_df.to_string(index=False)
)


# ============================================================
# Solar regime MAE plot
# ============================================================

x = np.arange(len(regime_df))
width = 0.35

plt.figure(figsize=(12, 7))

plt.bar(
    x - width / 2,
    regime_df["moirai_MAE_W_m2"],
    width,
    label="Moirai 2.0 R-small",
)

plt.bar(
    x + width / 2,
    regime_df["naive_MAE_W_m2"],
    width,
    label="Seasonal Naive 24h",
)

plt.xticks(
    x,
    regime_df["solar_regime"],
    rotation=15,
)

plt.ylabel("MAE (W/m²)")
plt.title(
    "POLARIS — Moirai 2.0 R-small Solar-Regime MAE"
)
plt.grid(
    axis="y",
    alpha=0.3,
)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "POLARIS_moirai2_solar_regime_MAE.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# Solar regime RMSE plot
# ============================================================

plt.figure(figsize=(12, 7))

plt.bar(
    x - width / 2,
    regime_df["moirai_RMSE_W_m2"],
    width,
    label="Moirai 2.0 R-small",
)

plt.bar(
    x + width / 2,
    regime_df["naive_RMSE_W_m2"],
    width,
    label="Seasonal Naive 24h",
)

plt.xticks(
    x,
    regime_df["solar_regime"],
    rotation=15,
)

plt.ylabel("RMSE (W/m²)")
plt.title(
    "POLARIS — Moirai 2.0 R-small Solar-Regime RMSE"
)
plt.grid(
    axis="y",
    alpha=0.3,
)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "POLARIS_moirai2_solar_regime_RMSE.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ============================================================
# Final summary
# ============================================================

print()
print("========================================")
print("MOIRAI DIAGNOSTIC ANALYSIS COMPLETE")
print("========================================")

print()
print("Output directory:")
print(OUTPUT_DIR)

print()
print("Files created:")

for file in sorted(OUTPUT_DIR.iterdir()):
    print(" ", file.name)
