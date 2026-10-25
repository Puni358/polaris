import pandas as pd
import numpy as np
from chronos import Chronos2Pipeline


# ============================================================
# POLARIS — Chronos-2 24h Forecast Benchmark
#
# Locked protocol:
#   Context:         previous 24 hours
#   Horizon:         next 24 hours
#   Windows:         365 non-overlapping daily windows
#   Evaluated hours: 8,760
#
# Point forecast:
#   Chronos-2 median / 0.5 quantile
# ============================================================


DATA_FILE = (
    "/home/punith-bs/01polaris/"
    "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
)

BENCHMARK_FILE = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"
)

OUTPUT_FILE = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"
)


# ============================================================
# 1. Load data
# ============================================================

print("=" * 70)
print("POLARIS — Chronos-2 Benchmark")
print("=" * 70)

print("\nLoading SITES data...")
data = pd.read_csv(DATA_FILE)

data["TIMESTAMP"] = pd.to_datetime(data["TIMESTAMP"])

print(f"SITES rows: {len(data)}")


print("\nLoading benchmark...")
benchmark = pd.read_csv(BENCHMARK_FILE)

benchmark["forecast_start"] = pd.to_datetime(
    benchmark["forecast_start"]
)

benchmark["timestamp"] = pd.to_datetime(
    benchmark["timestamp"]
)

print(f"Benchmark rows: {len(benchmark)}")


# ============================================================
# 2. Validate benchmark structure
# ============================================================

print("\nValidating benchmark structure...")

unique_starts = (
    benchmark["forecast_start"]
    .drop_duplicates()
    .sort_values()
)

assert len(unique_starts) == 365, (
    f"Expected 365 windows, found {len(unique_starts)}"
)

rows_per_window = benchmark.groupby(
    "forecast_start"
).size()

assert (rows_per_window == 24).all(), (
    "Not every forecast window contains exactly 24 rows."
)

assert len(benchmark) == 8760, (
    f"Expected 8760 rows, found {len(benchmark)}"
)

assert benchmark["horizon_hour"].tolist() == (
    benchmark.groupby("forecast_start")["horizon_hour"]
    .transform(lambda x: list(x))
    .explode()
    .astype(int)
    .tolist()
), "Unexpected horizon structure."


# ============================================================
# 3. Validate benchmark actuals against original SITES data
# ============================================================

print("Validating benchmark actuals against SITES data...")

sites_lookup = data.set_index("TIMESTAMP")["SW_IN"]

benchmark_actual_from_sites = benchmark["timestamp"].map(
    sites_lookup
)

assert benchmark_actual_from_sites.notna().all(), (
    "Some benchmark timestamps are missing from the original "
    "SITES hourly dataset."
)

actual_match = np.allclose(
    benchmark["actual_SW_IN"].to_numpy(dtype=float),
    benchmark_actual_from_sites.to_numpy(dtype=float),
    rtol=1e-10,
    atol=1e-10,
)

assert actual_match, (
    "Benchmark actual_SW_IN does not exactly match the "
    "original SITES hourly data."
)

print("Actual values: VERIFIED")


# ============================================================
# 4. Build 24-hour contexts
# ============================================================

print("\nBuilding 24-hour contexts...")

context_frames = []

for forecast_start in unique_starts:

    context_start = forecast_start - pd.Timedelta(hours=24)
    context_end = forecast_start - pd.Timedelta(hours=1)

    context = data[
        (data["TIMESTAMP"] >= context_start)
        & (data["TIMESTAMP"] <= context_end)
    ].copy()

    # Must be exactly 24 observations.
    assert len(context) == 24, (
        f"{forecast_start}: expected 24 context rows, "
        f"found {len(context)}"
    )

    # Verify hourly spacing.
    time_diff = context["TIMESTAMP"].diff().dropna()

    assert (
        time_diff == pd.Timedelta(hours=1)
    ).all(), (
        f"{forecast_start}: context is not strictly hourly."
    )

    context_frames.append(
        pd.DataFrame(
            {
                "item_id": (
                    f"POLARIS_{forecast_start.strftime('%Y%m%d')}"
                ),
                "timestamp": context["TIMESTAMP"].values,
                "target": context["SW_IN"].values,
            }
        )
    )

context_df = pd.concat(
    context_frames,
    ignore_index=True,
)

assert len(context_df) == 365 * 24

print(f"Context rows: {len(context_df)}")
print("Contexts: VERIFIED")


# ============================================================
# 5. Load Chronos-2
# ============================================================

print("\nLoading Chronos-2 on CPU...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2",
    device_map="cpu",
)

print("Chronos-2 loaded successfully.")


# ============================================================
# 6. Forecast all 365 windows
# ============================================================

print("\nRunning Chronos-2...")
print("365 windows × 24 forecast hours")
print("This may take some time on CPU.\n")

forecast = pipeline.predict_df(
    context_df,
    prediction_length=24,
)


# ============================================================
# 7. Extract median / 0.5 quantile
# ============================================================

print("Forecast generated.")

if 0.5 in forecast.columns:
    median_column = 0.5
elif "0.5" in forecast.columns:
    median_column = "0.5"
else:
    raise RuntimeError(
        "Chronos-2 output does not contain the 0.5 quantile."
    )

chronos_predictions = forecast[
    ["item_id", "timestamp", median_column]
].copy()

chronos_predictions = chronos_predictions.rename(
    columns={median_column: "chronos2"}
)


# ============================================================
# 8. Recover forecast_start from item_id
# ============================================================

chronos_predictions["forecast_start"] = pd.to_datetime(
    chronos_predictions["item_id"]
    .str.replace("POLARIS_", "", regex=False),
    format="%Y%m%d",
)


# ============================================================
# 9. Validate Chronos output
# ============================================================

print("\nValidating Chronos output...")

assert len(chronos_predictions) == 8760, (
    f"Expected 8760 Chronos predictions, "
    f"found {len(chronos_predictions)}"
)

prediction_counts = (
    chronos_predictions
    .groupby("forecast_start")
    .size()
)

assert len(prediction_counts) == 365

assert (prediction_counts == 24).all(), (
    "Chronos did not produce exactly 24 predictions "
    "for every window."
)


# ============================================================
# 10. Align with benchmark
# ============================================================

result = benchmark[
    [
        "forecast_start",
        "horizon_hour",
        "timestamp",
        "actual_SW_IN",
        "seasonal_naive_24h",
        "persistence_24h",
    ]
].copy()

chronos_predictions = chronos_predictions[
    [
        "forecast_start",
        "timestamp",
        "chronos2",
    ]
]

result = result.merge(
    chronos_predictions,
    on=["forecast_start", "timestamp"],
    how="left",
    validate="one_to_one",
)


# ============================================================
# 11. Final alignment checks
# ============================================================

assert len(result) == 8760

assert result["chronos2"].notna().all(), (
    "Some benchmark timestamps have no Chronos prediction."
)

assert result["forecast_start"].nunique() == 365

assert (
    result.groupby("forecast_start").size() == 24
).all()

# Ensure timestamp order is exactly the benchmark order.
assert (
    result["timestamp"].reset_index(drop=True)
    .equals(
        benchmark["timestamp"].reset_index(drop=True)
    )
), "Chronos output changed benchmark timestamp ordering."


# ============================================================
# 12. Save predictions
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(f"Forecast windows: {result['forecast_start'].nunique()}")
print(f"Forecast rows:    {len(result)}")
print(f"Output file:      {OUTPUT_FILE}")

print("\nFirst 10 Chronos predictions:")
print(
    result[
        [
            "forecast_start",
            "horizon_hour",
            "timestamp",
            "actual_SW_IN",
            "chronos2",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nChronos-2 benchmark prediction generation complete.")
