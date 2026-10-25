import os
import pandas as pd
import numpy as np

# ============================================================
# POLARIS — Smart Persistence Baseline (kt Persistence)
#
# Baseline definition:
#   forecast_kt[day D, hour H] = actual_kt[day D-1, hour H]
#   forecast_SW_IN = forecast_kt * clearsky_GHI[day D, hour H]
#
# Protocol (LOCKED):
#   365 non-overlapping 24h daily windows (8,760 total hours)
#   Evaluated against SITES Nuolja actual_SW_IN
# ============================================================

DECOMPOSITION_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv"
BENCHMARK_FILE = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"
OUTPUT_PREDICTIONS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"
OUTPUT_METRICS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_metrics.csv"

def calculate_metrics(actual, prediction):
    error = prediction - actual
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))
    return mae, rmse

def main():
    print("=" * 70)
    print("POLARIS — Smart Persistence Baseline (kt Persistence)")
    print("=" * 70)

    # 1. Load data & benchmark
    print("\nLoading files...")
    decomp = pd.read_csv(DECOMPOSITION_FILE)
    decomp["TIMESTAMP"] = pd.to_datetime(decomp["TIMESTAMP"])
    decomp_indexed = decomp.set_index("TIMESTAMP")

    benchmark = pd.read_csv(BENCHMARK_FILE)
    benchmark["forecast_start"] = pd.to_datetime(benchmark["forecast_start"])
    benchmark["timestamp"] = pd.to_datetime(benchmark["timestamp"])

    print(f"Decomposition rows: {len(decomp)}")
    print(f"Benchmark rows:     {len(benchmark)}")

    unique_starts = benchmark["forecast_start"].drop_duplicates().sort_values()
    assert len(unique_starts) == 365, f"Expected 365 windows, got {len(unique_starts)}"

    # 2. Build kt persistence forecast for each window
    predictions = []

    for forecast_start in unique_starts:
        # Context window: 24h before forecast_start
        context_start = forecast_start - pd.Timedelta(hours=24)
        context_end = forecast_start - pd.Timedelta(hours=1)

        # Context kt series
        context_kt = decomp_indexed.loc[context_start:context_end, "kt"].values
        assert len(context_kt) == 24, f"Window {forecast_start}: expected 24 context hours, got {len(context_kt)}"

        # Target window: forecast_start to forecast_start + 23h
        target_end = forecast_start + pd.Timedelta(hours=23)
        target_decomp = decomp_indexed.loc[forecast_start:target_end]
        assert len(target_decomp) == 24, f"Window {forecast_start}: expected 24 target hours, got {len(target_decomp)}"

        target_clearsky = target_decomp["clearsky_ghi"].values

        # kt persistence forecast: future kt = past 24h kt
        pred_kt = context_kt.copy()

        # Reconstruct SW_IN
        pred_sw_in = pred_kt * target_clearsky
        pred_sw_in = np.clip(pred_sw_in, 0.0, None)  # SW_IN cannot be negative

        window_df = pd.DataFrame({
            "forecast_start": forecast_start,
            "horizon_hour": list(range(1, 25)),
            "timestamp": target_decomp.index,
            "actual_SW_IN": target_decomp["actual_SW_IN"].values,
            "clearsky_ghi": target_clearsky,
            "pred_kt": pred_kt,
            "kt_persistence_24h": pred_sw_in
        })
        predictions.append(window_df)

    pred_df = pd.concat(predictions, ignore_index=True)
    assert len(pred_df) == 8760, f"Expected 8760 rows, got {len(pred_df)}"

    # 3. Calculate metrics
    actual = pred_df["actual_SW_IN"].to_numpy(dtype=float)
    pred_sw_in = pred_df["kt_persistence_24h"].to_numpy(dtype=float)

    daytime_mask = actual > 0.0

    mae_all, rmse_all = calculate_metrics(actual, pred_sw_in)
    mae_day, rmse_day = calculate_metrics(actual[daytime_mask], pred_sw_in[daytime_mask])

    # 4. Print comparison against existing baselines & Chronos-2
    print("\n" + "=" * 65)
    print("POLARIS FORECASTING LEADERBOARD (UPDATED)")
    print("=" * 65)
    print(f"{'Model':<30} | {'MAE (W/m²)':<10} | {'RMSE (W/m²)':<10} | {'Day MAE':<10} | {'Day RMSE':<10}")
    print("-" * 78)

    # Reference values from docs/decision_registers/POLARIS_MASTER_HANDOFF.md
    print(f"{'Chronos-2 (Champion)':<30} | {36.593:<10.3f} | {79.468:<10.3f} | {54.009:<10.3f} | {96.731:<10.3f}")
    print(f"{'24h Seasonal Naive':<30} | {37.186:<10.3f} | {85.127:<10.3f} | {55.099:<10.3f} | {103.622:<10.3f}")
    print(f"{'Smart Persistence (kt)':<30} | {mae_all:<10.3f} | {rmse_all:<10.3f} | {mae_day:<10.3f} | {rmse_day:<10.3f}")
    print(f"{'24h Persistence (Raw)':<30} | {83.489:<10.3f} | {169.374:<10.3f} | {123.708:<10.3f} | {206.173:<10.3f}")

    # 5. Save outputs
    pred_df.to_csv(OUTPUT_PREDICTIONS, index=False)
    metrics_df = pd.DataFrame([{
        "model": "Smart Persistence (kt)",
        "evaluation_windows": 365,
        "evaluation_hours": 8760,
        "MAE_W_m2": mae_all,
        "RMSE_W_m2": rmse_all,
        "daytime_MAE_W_m2": mae_day,
        "daytime_RMSE_W_m2": rmse_day
    }])
    metrics_df.to_csv(OUTPUT_METRICS, index=False)

    print(f"\nSaved predictions: {OUTPUT_PREDICTIONS}")
    print(f"Saved metrics:     {OUTPUT_METRICS}")
    print("Done!")

if __name__ == "__main__":
    main()
