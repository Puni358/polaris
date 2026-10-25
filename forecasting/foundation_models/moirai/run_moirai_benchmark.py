import pandas as pd
import torch
import time

from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module


CSV = "/home/punith-bs/01polaris/(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"

OUTPUT = "/home/punith-bs/01polaris/POLARIS_v0_1_moirai2_predictions.csv"


# ============================================================
# Load data
# ============================================================

print("Loading POLARIS data...")

df = pd.read_csv(CSV)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df = df.sort_values("TIMESTAMP").reset_index(drop=True)

print("Rows:", len(df))


# ============================================================
# Load Moirai 2.0 R-small
# ============================================================

print("\nLoading Moirai 2.0 R-small...")

module = Moirai2Module.from_pretrained(
    "Salesforce/moirai-2.0-R-small"
)

model = Moirai2Forecast(
    module=module,
    prediction_length=24,
    context_length=24,
    target_dim=1,
    feat_dynamic_real_dim=0,
    past_feat_dynamic_real_dim=0,
)

model.eval()


# ============================================================
# Compatibility fix
# ============================================================

# Uni2TS currently creates sample_id as int32.
# The Moirai attention path requires int64 indexing.

original_convert = model._convert


def fixed_convert(*args, **kwargs):
    result = original_convert(*args, **kwargs)

    (
        target,
        observed_mask,
        sample_id,
        time_id,
        variate_id,
        prediction_mask,
    ) = result

    return (
        target,
        observed_mask,
        sample_id.long(),
        time_id,
        variate_id,
        prediction_mask,
    )


model._convert = fixed_convert


# ============================================================
# Locked POLARIS benchmark
# ============================================================

# 365 non-overlapping daily windows.
#
# Window 1:
#   context = Jan 1, 2024
#   forecast = Jan 2, 2024
#
# Window 365:
#   context = Dec 30, 2024
#   forecast = Dec 31, 2024

results = []

start_time = time.time()

for window in range(365):

    context_start = window * 24
    forecast_start = context_start + 24
    forecast_end = forecast_start + 24

    context = df.iloc[
        context_start:forecast_start
    ]["SW_IN"].to_numpy()

    actual = df.iloc[
        forecast_start:forecast_end
    ]["SW_IN"].to_numpy()

    timestamps = df.iloc[
        forecast_start:forecast_end
    ]["TIMESTAMP"].to_numpy()

    forecast_date = timestamps[0]

    # --------------------------------------------------------
    # Prepare input
    # --------------------------------------------------------

    past_target = torch.tensor(
        context,
        dtype=torch.float32
    ).reshape(1, 24, 1)

    past_observed = torch.ones(
        1, 24, 1,
        dtype=torch.bool
    )

    past_is_pad = torch.zeros(
        1, 24,
        dtype=torch.bool
    )

    # --------------------------------------------------------
    # Forecast
    # --------------------------------------------------------

    with torch.no_grad():

        prediction = model(
            past_target=past_target,
            past_observed_target=past_observed,
            past_is_pad=past_is_pad,
        )

    # prediction shape:
    # [batch, 9 quantiles, 24 hours]
    #
    # Quantiles:
    # 0.1, 0.2, ..., 0.9
    #
    # Median / 0.5 quantile = index 4

    median_forecast = (
        prediction[0, 4, :]
        .cpu()
        .numpy()
    )

    # --------------------------------------------------------
    # Store results
    # --------------------------------------------------------

    for h in range(24):

        results.append(
            {
                "forecast_start": forecast_date,
                "horizon_hour": h + 1,
                "timestamp": timestamps[h],
                "actual_SW_IN": actual[h],
                "moirai2": median_forecast[h],
            }
        )

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    if (window + 1) % 25 == 0 or window == 0:

        elapsed = time.time() - start_time

        print(
            f"Completed {window + 1}/365 windows "
            f"({elapsed:.1f}s elapsed)"
        )


# ============================================================
# Save
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT,
    index=False
)


# ============================================================
# Verification
# ============================================================

print("\n========================================")
print("MOIRAI 2.0 BENCHMARK COMPLETE")
print("========================================")

print("\nOutput:")
print(OUTPUT)

print("\nShape:")
print(result_df.shape)

print("\nColumns:")
print(list(result_df.columns))

print("\nUnique forecast windows:")
print(result_df["forecast_start"].nunique())

print("\nNaN predictions:")
print(result_df["moirai2"].isna().sum())

print("\nPrediction statistics:")
print(result_df["moirai2"].describe())

print("\nFirst 5 rows:")
print(result_df.head())

print("\nLast 5 rows:")
print(result_df.tail())

print("\nDone.")
