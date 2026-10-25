import pandas as pd
import numpy as np


# ============================================================
# POLARIS — Chronos-2 Evaluation
#
# Same evaluation protocol as the existing baseline metrics.
#
# Overall:
#   All 8,760 forecast hours
#
# Daytime:
#   actual_SW_IN > 0
#
# Point forecast:
#   Chronos-2 0.5 quantile
# ============================================================


PREDICTIONS_FILE = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"
)

BASELINE_METRICS_FILE = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_baseline_metrics.csv"
)

OUTPUT_FILE = (
    "/home/punith-bs/01polaris/"
    "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_metrics.csv"
)


# ============================================================
# 1. Load files
# ============================================================

print("=" * 70)
print("POLARIS — Chronos-2 Evaluation")
print("=" * 70)

df = pd.read_csv(PREDICTIONS_FILE)

baseline = pd.read_csv(BASELINE_METRICS_FILE)


# ============================================================
# 2. Basic validation
# ============================================================

assert len(df) == 8760
assert df["forecast_start"].nunique() == 365

assert (
    df.groupby("forecast_start").size() == 24
).all()

assert df["chronos2"].notna().all()

print("\nPrediction file validated.")
print("Windows:", df["forecast_start"].nunique())
print("Hours:", len(df))


# ============================================================
# 3. Metric function
# ============================================================

def calculate_metrics(actual, prediction):

    error = prediction - actual

    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))

    return mae, rmse


# ============================================================
# 4. Verify baseline metrics
# ============================================================

print("\nVerifying existing baseline metrics...")

actual = df["actual_SW_IN"].to_numpy(dtype=float)

sn = df["seasonal_naive_24h"].to_numpy(dtype=float)
persistence = df["persistence_24h"].to_numpy(dtype=float)

daytime_mask = actual > 0


# Seasonal Naive
sn_mae, sn_rmse = calculate_metrics(actual, sn)

sn_day_mae, sn_day_rmse = calculate_metrics(
    actual[daytime_mask],
    sn[daytime_mask],
)


# Persistence
p_mae, p_rmse = calculate_metrics(actual, persistence)

p_day_mae, p_day_rmse = calculate_metrics(
    actual[daytime_mask],
    persistence[daytime_mask],
)


# Published values
published_sn = baseline[
    baseline["model"] == "24h Seasonal Naive"
].iloc[0]

published_p = baseline[
    baseline["model"] == "24h Persistence"
].iloc[0]


print("\nSeasonal Naive:")
print(f"  Overall MAE:       {sn_mae:.6f}")
print(f"  Published:         {published_sn['MAE_W_m2']:.6f}")
print(f"  Overall RMSE:      {sn_rmse:.6f}")
print(f"  Published:         {published_sn['RMSE_W_m2']:.6f}")
print(f"  Daytime MAE:       {sn_day_mae:.6f}")
print(f"  Published:         {published_sn['daytime_MAE_W_m2']:.6f}")
print(f"  Daytime RMSE:      {sn_day_rmse:.6f}")
print(f"  Published:         {published_sn['daytime_RMSE_W_m2']:.6f}")


print("\nPersistence:")
print(f"  Overall MAE:       {p_mae:.6f}")
print(f"  Published:         {published_p['MAE_W_m2']:.6f}")
print(f"  Overall RMSE:      {p_rmse:.6f}")
print(f"  Published:         {published_p['RMSE_W_m2']:.6f}")
print(f"  Daytime MAE:       {p_day_mae:.6f}")
print(f"  Published:         {published_p['daytime_MAE_W_m2']:.6f}")
print(f"  Daytime RMSE:      {p_day_rmse:.6f}")
print(f"  Published:         {published_p['daytime_RMSE_W_m2']:.6f}")


# Require exact numerical agreement to tight tolerance.
assert np.isclose(
    sn_mae,
    published_sn["MAE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    sn_rmse,
    published_sn["RMSE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    sn_day_mae,
    published_sn["daytime_MAE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    sn_day_rmse,
    published_sn["daytime_RMSE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    p_mae,
    published_p["MAE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    p_rmse,
    published_p["RMSE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    p_day_mae,
    published_p["daytime_MAE_W_m2"],
    atol=1e-6,
)

assert np.isclose(
    p_day_rmse,
    published_p["daytime_RMSE_W_m2"],
    atol=1e-6,
)

print("\nBaseline verification: PASSED")


# ============================================================
# 5. Chronos-2 metrics
# ============================================================

chronos = df["chronos2"].to_numpy(dtype=float)


chronos_mae, chronos_rmse = calculate_metrics(
    actual,
    chronos,
)


chronos_day_mae, chronos_day_rmse = calculate_metrics(
    actual[daytime_mask],
    chronos[daytime_mask],
)


# ============================================================
# 6. Create results table
# ============================================================

results = pd.DataFrame(
    [
        {
            "model": "24h Seasonal Naive",
            "evaluation_windows": 365,
            "evaluation_hours": 8760,
            "MAE_W_m2": sn_mae,
            "RMSE_W_m2": sn_rmse,
            "daytime_MAE_W_m2": sn_day_mae,
            "daytime_RMSE_W_m2": sn_day_rmse,
        },
        {
            "model": "24h Persistence",
            "evaluation_windows": 365,
            "evaluation_hours": 8760,
            "MAE_W_m2": p_mae,
            "RMSE_W_m2": p_rmse,
            "daytime_MAE_W_m2": p_day_mae,
            "daytime_RMSE_W_m2": p_day_rmse,
        },
        {
            "model": "Chronos-2",
            "evaluation_windows": 365,
            "evaluation_hours": 8760,
            "MAE_W_m2": chronos_mae,
            "RMSE_W_m2": chronos_rmse,
            "daytime_MAE_W_m2": chronos_day_mae,
            "daytime_RMSE_W_m2": chronos_day_rmse,
        },
    ]
)


# ============================================================
# 7. Save
# ============================================================

results.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# 8. Display final result
# ============================================================

print("\n" + "=" * 70)
print("FINAL POLARIS RESULTS")
print("=" * 70)

print(
    results.to_string(
        index=False,
        float_format=lambda x: f"{x:.6f}",
    )
)

print("\nOutput:")
print(OUTPUT_FILE)

print("\nChronos-2 evaluation complete.")
