import numpy as np
import pandas as pd
import torch

from chronos import Chronos2Pipeline

DATA = "/home/punith-bs/01polaris/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"

OUT = "/home/punith-bs/01polaris/POLARIS_v0_1_chronos2_multivariate_predictions.csv"

# ============================================================
# LOCKED POLARIS BENCHMARK
# ============================================================

CONTEXT = 24
HORIZON = 24

# Same 365 forecast origins as the existing benchmark:
# Jan 2 through Dec 31, 2024.
#
# Each forecast:
#   previous 24h -> next 24h
#
# Target:
#   SW_IN
#
# Past covariates:
#   TA
#   RH
#   TS_-0.01m
#   PRECIP
#
# NO FUTURE COVARIATES.
# ============================================================


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------

df = pd.read_csv(DATA)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df = df.sort_values("TIMESTAMP").reset_index(drop=True)

required = [
    "TIMESTAMP",
    "TA",
    "RH",
    "SW_IN",
    "TS_-0.01m",
    "PRECIP",
]

missing_columns = [c for c in required if c not in df.columns]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

if df[required].isna().any().any():
    raise ValueError("NaN values found in required 5-variable dataset.")

print("Dataset shape:", df.shape)
print("Dataset start:", df["TIMESTAMP"].min())
print("Dataset end:", df["TIMESTAMP"].max())


# ------------------------------------------------------------
# Load Chronos-2
# ------------------------------------------------------------

print("\nLoading Chronos-2...")

pipeline = Chronos2Pipeline.from_pretrained(
    "amazon/chronos-2"
)

print("Chronos-2 loaded.")
print("Quantiles:", pipeline.quantiles)


# ------------------------------------------------------------
# Locate median quantile
# ------------------------------------------------------------

quantiles = np.asarray(pipeline.quantiles)

median_idx = int(
    np.argmin(np.abs(quantiles - 0.5))
)

print("Median quantile index:", median_idx)
print("Median quantile:", quantiles[median_idx])


# ------------------------------------------------------------
# Generate exact forecast windows
# ------------------------------------------------------------

forecast_starts = pd.date_range(
    start="2024-01-02 00:00:00",
    end="2024-12-31 00:00:00",
    freq="24h",
)

assert len(forecast_starts) == 365

print("\nForecast windows:", len(forecast_starts))


# ------------------------------------------------------------
# Forecast loop
# ------------------------------------------------------------

results = []

for i, forecast_start in enumerate(forecast_starts, start=1):

    history_start = forecast_start - pd.Timedelta(hours=CONTEXT)
    forecast_end = forecast_start + pd.Timedelta(hours=HORIZON)

    history = df[
        (df["TIMESTAMP"] >= history_start)
        & (df["TIMESTAMP"] < forecast_start)
    ]

    future = df[
        (df["TIMESTAMP"] >= forecast_start)
        & (df["TIMESTAMP"] < forecast_end)
    ]

    if len(history) != CONTEXT:
        raise ValueError(
            f"Window {forecast_start}: expected "
            f"{CONTEXT} history rows, got {len(history)}"
        )

    if len(future) != HORIZON:
        raise ValueError(
            f"Window {forecast_start}: expected "
            f"{HORIZON} future rows, got {len(future)}"
        )

    # --------------------------------------------------------
    # Target history
    # --------------------------------------------------------

    target = history["SW_IN"].to_numpy(
        dtype=np.float32
    )

    # --------------------------------------------------------
    # Past-only environmental covariates
    # --------------------------------------------------------

    past_covariates = {
        "TA": history["TA"].to_numpy(dtype=np.float32),
        "RH": history["RH"].to_numpy(dtype=np.float32),
        "TS_-0.01m": history["TS_-0.01m"].to_numpy(dtype=np.float32),
        "PRECIP": history["PRECIP"].to_numpy(dtype=np.float32),
    }

    inputs = [
        {
            "target": target,
            "past_covariates": past_covariates,
        }
    ]

    # --------------------------------------------------------
    # Forecast
    # --------------------------------------------------------

    predictions = pipeline.predict(
        inputs,
        prediction_length=HORIZON,
        context_length=CONTEXT,
        batch_size=1,
    )

    pred_tensor = predictions[0]

    # Shape:
    # (1, n_quantiles, 24)

    forecast = (
        pred_tensor[0, median_idx]
        .detach()
        .cpu()
        .numpy()
    )

    if forecast.shape != (HORIZON,):
        raise ValueError(
            f"Unexpected forecast shape: {forecast.shape}"
        )

    # --------------------------------------------------------
    # Save each forecast hour
    # --------------------------------------------------------

    actual = future["SW_IN"].to_numpy(dtype=float)

    # Seasonal naive from exactly 24h earlier.
    seasonal_naive = history["SW_IN"].to_numpy(dtype=float)

    # Persistence: last observed SW_IN repeated 24 times.
    persistence = np.repeat(
        history["SW_IN"].iloc[-1],
        HORIZON
    )

    for h in range(HORIZON):

        results.append(
            {
                "forecast_start": forecast_start,
                "horizon_hour": h + 1,
                "timestamp": future["TIMESTAMP"].iloc[h],
                "actual_SW_IN": actual[h],
                "seasonal_naive_24h": seasonal_naive[h],
                "persistence_24h": persistence[h],
                "chronos2_multivariate": float(forecast[h]),
            }
        )

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if i == 1 or i % 25 == 0 or i == len(forecast_starts):
        print(
            f"[{i:3d}/{len(forecast_starts)}] "
            f"{forecast_start.date()} "
            f"forecast_peak={forecast.max():.3f} "
            f"actual_peak={actual.max():.3f}"
        )


# ------------------------------------------------------------
# Create output dataframe
# ------------------------------------------------------------

predictions_df = pd.DataFrame(results)

expected_rows = 365 * 24

if len(predictions_df) != expected_rows:
    raise ValueError(
        f"Expected {expected_rows} rows, "
        f"got {len(predictions_df)}"
    )


# ------------------------------------------------------------
# Final validation
# ------------------------------------------------------------

print("\n==============================================")
print("FINAL VALIDATION")
print("==============================================")

print("Rows:", len(predictions_df))
print(
    "Unique forecast windows:",
    predictions_df["forecast_start"].nunique()
)
print(
    "Rows per forecast window:",
    predictions_df.groupby("forecast_start").size().value_counts().to_dict()
)

print(
    "NaNs in Chronos predictions:",
    predictions_df["chronos2_multivariate"].isna().sum()
)

print(
    "Negative Chronos predictions:",
    (predictions_df["chronos2_multivariate"] < 0).sum()
)

assert len(predictions_df) == 8760
assert predictions_df["forecast_start"].nunique() == 365
assert (
    predictions_df.groupby("forecast_start").size() == 24
).all()
assert predictions_df["chronos2_multivariate"].isna().sum() == 0


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

predictions_df.to_csv(
    OUT,
    index=False,
    float_format="%.10f"
)

print("\nSaved:")
print(OUT)

print("\nPrediction statistics:")
print(
    predictions_df["chronos2_multivariate"]
    .describe()
    .to_string()
)

print("\nSUCCESS")
