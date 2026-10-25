import os
import pandas as pd
import numpy as np

# ============================================================
# POLARIS — 347-Window Same-Window Baseline Evaluation
#
# Target origins: The 347 PASS forecast origins (Jan 20 to Dec 31)
# Models evaluated:
#   1. Zero-shot Chronos-2 (Raw SW_IN)
#   2. 24h Seasonal Naive
#   3. 24h Persistence (Raw)
#   4. Smart Persistence (kt)
# ============================================================

PASS_FAIL_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_nwp_coverage_pass_fail.csv"
CHRONOS_FULL_PRED = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"
KT_PERSISTENCE_PRED = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"
BENCHMARK_FILE = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv"

OUTPUT_PREDICTIONS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_347window_chronos2_raw_baseline.csv"
OUTPUT_METRICS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_347window_baseline_metrics.csv"
OUTPUT_HORIZON_METRICS = "/home/punith-bs/01polaris (Copy)/forecasting/foundation_models/results/POLARIS_v0_1_347window_horizon_metrics.csv"

def calculate_metrics(actual, prediction):
    error = prediction - actual
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))
    return mae, rmse

def main():
    print("=" * 80)
    print("POLARIS — 347-Window Same-Window Baseline Evaluation")
    print("=" * 80)

    # 1. Load PASS/FAIL mapping
    pf_df = pd.read_csv(PASS_FAIL_FILE)
    pass_origins = set(pd.to_datetime(pf_df[pf_df["status"] == "PASS"]["forecast_start"]))

    print(f"Total PASS Origins Loaded: {len(pass_origins)} (Expected: 347)")
    assert len(pass_origins) == 347, f"Expected 347 PASS origins, got {len(pass_origins)}"

    # 2. Load Chronos-2 full predictions & benchmark
    chronos_df = pd.read_csv(CHRONOS_FULL_PRED)
    chronos_df["forecast_start_dt"] = pd.to_datetime(chronos_df["forecast_start"])

    # Filter strictly for the 347 PASS origins
    df_347 = chronos_df[chronos_df["forecast_start_dt"].isin(pass_origins)].copy()
    assert len(df_347) == 347 * 24, f"Expected 8328 rows, got {len(df_347)}"

    # Load kt persistence predictions if available for comparison
    if os.path.exists(KT_PERSISTENCE_PRED):
        kt_p_df = pd.read_csv(KT_PERSISTENCE_PRED)
        kt_p_df["forecast_start_dt"] = pd.to_datetime(kt_p_df["forecast_start"])
        kt_p_347 = kt_p_df[kt_p_df["forecast_start_dt"].isin(pass_origins)]
        df_347["smart_persistence_kt"] = kt_p_347["kt_persistence_24h"].values

    # 3. Calculate Overall & Daytime Metrics
    actual = df_347["actual_SW_IN"].to_numpy(dtype=float)
    chronos_pred = df_347["chronos2"].to_numpy(dtype=float)
    sn_pred = df_347["seasonal_naive_24h"].to_numpy(dtype=float)
    raw_p_pred = df_347["persistence_24h"].to_numpy(dtype=float)

    daytime_mask = actual > 0.0

    # Chronos-2 Metrics
    c_mae, c_rmse = calculate_metrics(actual, chronos_pred)
    c_day_mae, c_day_rmse = calculate_metrics(actual[daytime_mask], chronos_pred[daytime_mask])

    # Seasonal Naive Metrics
    sn_mae, sn_rmse = calculate_metrics(actual, sn_pred)
    sn_day_mae, sn_day_rmse = calculate_metrics(actual[daytime_mask], sn_pred[daytime_mask])

    # Raw Persistence Metrics
    p_mae, p_rmse = calculate_metrics(actual, raw_p_pred)
    p_day_mae, p_day_rmse = calculate_metrics(actual[daytime_mask], raw_p_pred[daytime_mask])

    # Smart Persistence Metrics
    if "smart_persistence_kt" in df_347.columns:
        s_p_pred = df_347["smart_persistence_kt"].to_numpy(dtype=float)
        sp_mae, sp_rmse = calculate_metrics(actual, s_p_pred)
        sp_day_mae, sp_day_rmse = calculate_metrics(actual[daytime_mask], s_p_pred[daytime_mask])

    # 4. Horizon-by-Horizon Breakdown (h = 1..24)
    horizon_results = []
    for h in range(1, 25):
        h_mask = df_347["horizon_hour"] == h
        h_act = actual[h_mask]
        h_c = chronos_pred[h_mask]
        h_sn = sn_pred[h_mask]

        h_c_mae, h_c_rmse = calculate_metrics(h_act, h_c)
        h_sn_mae, h_sn_rmse = calculate_metrics(h_act, h_sn)

        horizon_results.append({
            "horizon_hour": h,
            "chronos2_MAE": h_c_mae,
            "chronos2_RMSE": h_c_rmse,
            "seasonal_naive_MAE": h_sn_mae,
            "seasonal_naive_RMSE": h_sn_rmse,
            "mae_win": "Chronos-2" if h_c_mae < h_sn_mae else "Seasonal Naive",
            "rmse_win": "Chronos-2" if h_c_rmse < h_sn_rmse else "Seasonal Naive"
        })

    horizon_df = pd.DataFrame(horizon_results)

    # 5. Display Leaderboard & Comparison with Full 365 Windows
    print("\n" + "=" * 80)
    print("POLARIS 347-WINDOW SAME-WINDOW BASELINE LEADERBOARD")
    print("=" * 80)
    print(f"{'Model':<30} | {'MAE (W/m²)':<10} | {'RMSE (W/m²)':<10} | {'Day MAE':<10} | {'Day RMSE':<10}")
    print("-" * 80)
    print(f"{'Chronos-2 (Raw SW_IN)':<30} | {c_mae:<10.3f} | {c_rmse:<10.3f} | {c_day_mae:<10.3f} | {c_day_rmse:<10.3f}")
    if "smart_persistence_kt" in df_347.columns:
        print(f"{'Smart Persistence (kt)':<30} | {sp_mae:<10.3f} | {sp_rmse:<10.3f} | {sp_day_mae:<10.3f} | {sp_day_rmse:<10.3f}")
    print(f"{'24h Seasonal Naive':<30} | {sn_mae:<10.3f} | {sn_rmse:<10.3f} | {sn_day_mae:<10.3f} | {sn_day_rmse:<10.3f}")
    print(f"{'24h Persistence (Raw)':<30} | {p_mae:<10.3f} | {p_rmse:<10.3f} | {p_day_mae:<10.3f} | {p_day_rmse:<10.3f}")

    print("\n" + "=" * 80)
    print("COMPARISON: 347 PASS WINDOWS vs FULL 365 WINDOWS")
    print("=" * 80)
    print(f"{'Model / Metric':<30} | {'347 Windows (Usable)':<20} | {'Full 365 Windows':<20} | {'Delta':<10}")
    print("-" * 85)
    print(f"{'Chronos-2 Overall MAE':<30} | {c_mae:<20.3f} | {36.593:<20.3f} | {c_mae - 36.593:+10.3f}")
    print(f"{'Chronos-2 Overall RMSE':<30} | {c_rmse:<20.3f} | {79.468:<20.3f} | {c_rmse - 79.468:+10.3f}")
    print(f"{'Chronos-2 Daytime MAE':<30} | {c_day_mae:<20.3f} | {54.009:<20.3f} | {c_day_mae - 54.009:+10.3f}")
    print(f"{'Chronos-2 Daytime RMSE':<30} | {c_day_rmse:<20.3f} | {96.731:<20.3f} | {c_day_rmse - 96.731:+10.3f}")
    print("-" * 85)
    print(f"{'Seasonal Naive Overall MAE':<30} | {sn_mae:<20.3f} | {37.186:<20.3f} | {sn_mae - 37.186:+10.3f}")
    print(f"{'Seasonal Naive Overall RMSE':<30} | {sn_rmse:<20.3f} | {85.127:<20.3f} | {sn_rmse - 85.127:+10.3f}")
    print(f"{'Seasonal Naive Daytime MAE':<30} | {sn_day_mae:<20.3f} | {55.099:<20.3f} | {sn_day_mae - 55.099:+10.3f}")
    print(f"{'Seasonal Naive Daytime RMSE':<30} | {sn_day_rmse:<20.3f} | {103.622:<20.3f} | {sn_day_rmse - 103.622:+10.3f}")

    # 6. Save Predictions & Metrics
    df_347.to_csv(OUTPUT_PREDICTIONS, index=False)

    summary_metrics = pd.DataFrame([
        {
            "model": "Chronos-2 (Raw SW_IN)",
            "evaluation_windows": 347,
            "evaluation_hours": 8328,
            "MAE_W_m2": c_mae,
            "RMSE_W_m2": c_rmse,
            "daytime_MAE_W_m2": c_day_mae,
            "daytime_RMSE_W_m2": c_day_rmse
        },
        {
            "model": "24h Seasonal Naive",
            "evaluation_windows": 347,
            "evaluation_hours": 8328,
            "MAE_W_m2": sn_mae,
            "RMSE_W_m2": sn_rmse,
            "daytime_MAE_W_m2": sn_day_mae,
            "daytime_RMSE_W_m2": sn_day_rmse
        },
        {
            "model": "24h Persistence (Raw)",
            "evaluation_windows": 347,
            "evaluation_hours": 8328,
            "MAE_W_m2": p_mae,
            "RMSE_W_m2": p_rmse,
            "daytime_MAE_W_m2": p_day_mae,
            "daytime_RMSE_W_m2": p_day_rmse
        }
    ])
    summary_metrics.to_csv(OUTPUT_METRICS, index=False)
    horizon_df.to_csv(OUTPUT_HORIZON_METRICS, index=False)

    print(f"\nSaved 347-window baseline predictions to:\n  {OUTPUT_PREDICTIONS}")
    print(f"Saved 347-window baseline metrics to:\n  {OUTPUT_METRICS}")
    print(f"Saved 347-window horizon metrics to:\n  {OUTPUT_HORIZON_METRICS}")
    print("Done!")

if __name__ == "__main__":
    main()
