import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# POLARIS — Chronos-2 Forecast Behavior
# ============================================================

INPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_predictions.csv"
OUTPUT_DIR = Path("/home/punith-bs/01polaris/chronos_forecast_plots")

OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

df = pd.read_csv(INPUT)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["forecast_start"] = pd.to_datetime(df["forecast_start"])

# ------------------------------------------------------------
# Selected windows
# ------------------------------------------------------------

selected_dates = [
    "2024-04-27",
    "2024-05-10",
    "2024-06-18",
    "2024-06-22",
    "2024-06-23",
]

# ------------------------------------------------------------
# Plot each forecast window
# ------------------------------------------------------------

for date in selected_dates:

    start = pd.Timestamp(date)

    d = df[df["forecast_start"] == start].copy()

    if len(d) != 24:
        print(f"WARNING: {date} has {len(d)} rows, expected 24.")
        continue

    d = d.sort_values("horizon_hour")

    actual = d["actual_SW_IN"]
    chronos = d["chronos2"]
    naive = d["seasonal_naive_24h"]

    mae_chronos = (actual - chronos).abs().mean()
    rmse_chronos = ((actual - chronos) ** 2).mean() ** 0.5

    mae_naive = (actual - naive).abs().mean()
    rmse_naive = ((actual - naive) ** 2).mean() ** 0.5

    actual_peak = actual.max()
    chronos_peak = chronos.max()
    naive_peak = naive.max()

    plt.figure(figsize=(11, 6))

    plt.plot(
        d["horizon_hour"],
        actual,
        marker="o",
        label="Actual SW_IN",
    )

    plt.plot(
        d["horizon_hour"],
        chronos,
        marker="o",
        label="Chronos-2",
    )

    plt.plot(
        d["horizon_hour"],
        naive,
        marker="o",
        label="24h Seasonal Naive",
    )

    plt.axhline(0, linewidth=1)

    plt.xlabel("Forecast Horizon (hours ahead)")
    plt.ylabel("SW_IN (W/m²)")

    plt.title(
        f"POLARIS — Forecast Starting {date}\n"
        f"Chronos MAE={mae_chronos:.1f}, RMSE={rmse_chronos:.1f} | "
        f"Naive MAE={mae_naive:.1f}, RMSE={rmse_naive:.1f}"
    )

    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()

    output = OUTPUT_DIR / f"chronos_forecast_{date}.png"

    plt.savefig(
        output,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\n{date}")
    print("-" * 60)
    print(f"Actual peak :  {actual_peak:.3f} W/m²")
    print(f"Chronos peak:  {chronos_peak:.3f} W/m²")
    print(f"Naive peak  :  {naive_peak:.3f} W/m²")
    print(f"Chronos MAE :  {mae_chronos:.3f}")
    print(f"Chronos RMSE:  {rmse_chronos:.3f}")
    print(f"Naive MAE   :  {mae_naive:.3f}")
    print(f"Naive RMSE  :  {rmse_naive:.3f}")
    print(f"Saved       :  {output}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

print(f"\nPlots saved to:")
print(OUTPUT_DIR)
