import pandas as pd
import torch

from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module


CSV = "/home/punith-bs/01polaris/(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"


print("Loading POLARIS data...")

# Load data
df = pd.read_csv(CSV)
df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df = df.sort_values("TIMESTAMP").reset_index(drop=True)

# First locked POLARIS benchmark window
# Context: previous 24 hours
# Forecast: next 24 hours
context = df.iloc[0:24]["SW_IN"].to_numpy()
actual = df.iloc[24:48]["SW_IN"].to_numpy()

print("Data loaded.")
print("Context:", df.iloc[0]["TIMESTAMP"], "to", df.iloc[23]["TIMESTAMP"])
print("Forecast:", df.iloc[24]["TIMESTAMP"], "to", df.iloc[47]["TIMESTAMP"])


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

print("Model loaded.")


# Prepare tensors
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


# Compatibility fix:
# Uni2TS creates sample_id as int32,
# but this Moirai attention path requires int64.
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


print("\nRunning Moirai forecast...")

with torch.no_grad():
    prediction = model(
        past_target=past_target,
        past_observed_target=past_observed,
        past_is_pad=past_is_pad,
    )


# Moirai outputs 9 quantiles:
# 0.1, 0.2, ..., 0.9
# The 0.5 median is index 4.
median_forecast = prediction[0, 4, :].cpu().numpy()


print("\n========================================")
print("MOIRAI 2.0 R-SMALL POLARIS SMOKE TEST")
print("========================================")

print("\nPrediction shape:")
print(prediction.shape)

print("\nMedian forecast shape:")
print(median_forecast.shape)

print("\nActual peak SW_IN:")
print(actual.max())

print("\nMoirai peak forecast:")
print(median_forecast.max())

print("\nActual mean SW_IN:")
print(actual.mean())

print("\nMoirai mean forecast:")
print(median_forecast.mean())

print("\nFirst 10 forecast values:")
print("----------------------------------------")

for i in range(10):
    timestamp = df.iloc[24 + i]["TIMESTAMP"]

    print(
        f"{timestamp} | "
        f"actual={actual[i]:8.3f} | "
        f"moirai={median_forecast[i]:8.3f}"
    )

print("\nMoirai smoke test completed successfully.")
