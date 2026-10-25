import os
import pandas as pd
import numpy as np
from chronos import Chronos2Pipeline

# ============================================================
# POLARIS — Chronos-2 Clear-Sky Index (kt) Benchmark
#
# Protocol (LOCKED):
#   Context:         previous 24 hours of kt
#   Horizon:         next 24 hours of kt
#   Windows:         365 non-overlapping daily windows
#   Evaluated hours: 8,760
#
# Forecast Reconstruction:
#   forecast_SW_IN = max(0, forecast_kt * clearsky_ghi)
# ============================================================

DECOMPOSITION_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv"
BENCHMARK_FILE = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"
OUTPUT_PREDICTIONS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_chronos2_kt_predictions.csv"
OUTPUT_METRICS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_chronos2_kt_metrics.csv"

def calculate_metrics(actual, prediction):
    error = prediction - actual
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))
    return mae, rmse

def main():
    print("=" * 70)
    print("POLARIS — Chronos-2 Clear-Sky Index (kt) Benchmark")
    print("=" * 70)

    # 1. Load data
    print("\nLoading clear-sky decomposition...")
    decomp = pd.read_csv(DECOMPOSITION_FILE)
    decomp["TIMESTAMP"] = pd.to_datetime(decomp["TIMESTAMP"])
    decomp_indexed = decomp.set_index("TIMESTAMP")

    print("\nLoading benchmark...")
    benchmark = pd.read_csv(BENCHMARK_FILE)
    benchmark["forecast_start"] = pd.to_datetime(benchmark["forecast_start"])
    benchmark["timestamp"] = pd.to_datetime(benchmark["timestamp"])

    unique_starts = benchmark["forecast_start"].drop_duplicates().sort_values()
    assert len(unique_starts) == 365, f"Expected 365 windows, got {len(unique_starts)}"

    # 2. Build 24-hour kt contexts
    print("\nBuilding 24-hour kt contexts...")
    context_frames = []

    for forecast_start in unique_starts:
        context_start = forecast_start - pd.Timedelta(hours=24)
        context_end = forecast_start - pd.Timedelta(hours=1)

        context_kt = decomp_indexed.loc[context_start:context_end].copy()
        assert len(context_kt) == 24, f"{forecast_start}: expected 24 context rows, found {len(context_kt)}"

        context_frames.append(
            pd.DataFrame({
                "item_id": f"POLARIS_{forecast_start.strftime('%Y%m%d')}",
                "timestamp": context_kt.index,
                "target": context_kt["kt"].values,
            })
        )

    context_df = pd.concat(context_frames, ignore_index=True)
    assert len(context_df) == 365 * 24

    # 3. Load Chronos-2
    print("\nLoading Chronos-2 on CPU...")
    pipeline = Chronos2Pipeline.from_pretrained(
        "amazon/chronos-2",
        device_map="cpu",
    )

    # 4. Forecast kt series
    print("\nRunning Chronos-2 on kt series (365 windows × 24h)...")
    forecast = pipeline.predict_df(
        context_df,
        prediction_length=24,
    )

    # Extract 0.5 quantile
    if 0.5 in forecast.columns:
        median_col = 0.5
    elif "0.5" in forecast.columns:
        median_col = "0.5"
    else:
        raise RuntimeError("Chronos-2 output missing 0.5 quantile.")

    chronos_kt = forecast[["item_id", "timestamp", median_col]].copy()
    chronos_kt = chronos_kt.rename(columns={median_col: "pred_kt"})
    chronos_kt["forecast_start"] = pd.to_datetime(
        chronos_kt["item_id"].str.replace("POLARIS_", "", regex=False),
        format="%Y%m%d"
    )

    # 5. Merge with target clearsky_ghi and benchmark actuals
    print("\nReconstructing SW_IN forecasts...")
    result = benchmark[
        ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN"]
    ].copy()

    result = result.merge(
        chronos_kt[["forecast_start", "timestamp", "pred_kt"]],
        on=["forecast_start", "timestamp"],
        how="left",
        validate="one_to_one"
    )

    decomp_target = decomp[["TIMESTAMP", "clearsky_ghi"]].rename(columns={"TIMESTAMP": "timestamp"})
    decomp_target["timestamp"] = pd.to_datetime(decomp_target["timestamp"])

    result = result.merge(
        decomp_target,
        on="timestamp",
        how="left",
        validate="many_to_one"
    )

    # Reconstruct: forecast_SW_IN = pred_kt * clearsky_ghi
    # Clip pred_kt to [0, 1.5] and reconstructed SW_IN to >= 0
    result["pred_kt_clipped"] = np.clip(result["pred_kt"].values, 0.0, 1.5)
    result["chronos2_kt_reconstructed"] = np.clip(
        result["pred_kt_clipped"].values * result["clearsky_ghi"].values,
        0.0,
        None
    )

    # 6. Evaluate metrics
    actual = result["actual_SW_IN"].to_numpy(dtype=float)
    pred_sw_in = result["chronos2_kt_reconstructed"].to_numpy(dtype=float)

    daytime_mask = actual > 0.0

    mae_all, rmse_all = calculate_metrics(actual, pred_sw_in)
    mae_day, rmse_day = calculate_metrics(actual[daytime_mask], pred_sw_in[daytime_mask])

    print("\n" + "=" * 70)
    print("POLARIS FORECASTING LEADERBOARD (WITH KT DECOMPOSITION)")
    print("=" * 70)
    print(f"{'Model':<30} | {'MAE (W/m²)':<10} | {'RMSE (W/m²)':<10} | {'Day MAE':<10} | {'Day RMSE':<10}")
    print("-" * 78)
    print(f"{'Chronos-2 (Raw SW_IN)':<30} | {36.593:<10.3f} | {79.468:<10.3f} | {54.009:<10.3f} | {96.731:<10.3f}")
    print(f"{'Chronos-2 (kt Reconstructed)':<30} | {mae_all:<10.3f} | {rmse_all:<10.3f} | {mae_day:<10.3f} | {rmse_day:<10.3f}")
    print(f"{'24h Seasonal Naive':<30} | {37.186:<10.3f} | {85.127:<10.3f} | {55.099:<10.3f} | {103.622:<10.3f}")
    print(f"{'Smart Persistence (kt)':<30} | {37.154:<10.3f} | {84.861:<10.3f} | {55.052:<10.3f} | {103.299:<10.3f}")
    print(f"{'24h Persistence (Raw)':<30} | {83.489:<10.3f} | {169.374:<10.3f} | {123.708:<10.3f} | {206.173:<10.3f}")

    # Save results
    result.to_csv(OUTPUT_PREDICTIONS, index=False)

    metrics_df = pd.DataFrame([{
        "model": "Chronos-2 (kt Reconstructed)",
        "evaluation_windows": 365,
        "evaluation_hours": 8760,
        "MAE_W_m2": mae_all,
        "RMSE_W_m2": rmse_all,
        "daytime_MAE_W_m2": mae_day,
        "daytime_RMSE_W_m2": rmse_day
    }])
    metrics_df.to_csv(OUTPUT_METRICS, index=False)

    print(f"\nPredictions saved to: {OUTPUT_PREDICTIONS}")
    print(f"Metrics saved to:     {OUTPUT_METRICS}")
    print("Done!")

if __name__ == "__main__":
    main()
