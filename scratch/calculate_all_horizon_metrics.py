import os
import glob
import hashlib
import numpy as np
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"

# 1. Map of Prediction Files and their attributes
prediction_sources = [
    {
        "model_id": "Stage8.1_HGB_Control",
        "stage": "Stage 8.1 / Baseline",
        "file": os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"),
        "y_true_col": "y_true",
        "y_pred_col": "y_pred",
        "horizon_col": "horizon",
        "daytime_col": "daytime_flag",
        "split": "ODD (173 origins)"
    },
    {
        "model_id": "Stage8.1_Official_ODD",
        "stage": "Stage 8.1",
        "file": os.path.join(WORKSPACE, "forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_stage8_1_candidate",
        "horizon_col": "horizon_hour",
        "daytime_col": "is_daytime",
        "split": "ODD (173 origins)"
    },
    {
        "model_id": "Stage8.17A_Real_AROME",
        "stage": "Stage 8.17A",
        "file": os.path.join(WORKSPACE, "forecasting/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv"),
        "y_true_col": "actual_sw_in",
        "y_pred_col": "candidate_prediction",
        "horizon_col": "horizon_h",
        "daytime_col": "daytime_flag",
        "split": "ODD (173 origins)"
    },
    {
        "model_id": "Stage8.19_ABIS_GNSS_Reproduced",
        "stage": "Stage 8.19",
        "file": os.path.join(WORKSPACE, "forecasting/stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "predicted_SW_IN",
        "horizon_col": "horizon_hour",
        "daytime_col": "daytime_flag",
        "split": "ODD (173 origins)"
    },
    {
        "model_id": "Chronos2_Raw",
        "stage": "Chronos-2 Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "chronos2",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins (8,760 hours)"
    },
    {
        "model_id": "Chronos2_Multivariate",
        "stage": "Chronos-2 Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_multivariate_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "chronos2_multivariate",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins (8,760 hours)"
    },
    {
        "model_id": "TimesFM3",
        "stage": "TimesFM Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "timesfm3",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins (8,760 hours)"
    },
    {
        "model_id": "Moirai2",
        "stage": "Moirai Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "moirai2",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins (8,760 hours)"
    },
    {
        "model_id": "Kt_Persistence_24h",
        "stage": "Persistence Baseline",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "kt_persistence_24h",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins (8,760 hours)"
    },
    {
        "model_id": "Stage4_Ensemble_Hybrid",
        "stage": "Stage 4.3",
        "file": os.path.join(WORKSPACE, "forecasting/stage4/stage4_results/ensemble_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_ensemble",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "347 origins (8,328 daytime/night horizon tuples)"
    },
    {
        "model_id": "Stage3C_Full_NWP",
        "stage": "Stage 3C",
        "file": os.path.join(WORKSPACE, "forecasting/stage3/stage3c_full_nwp_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_stage3c_full_nwp",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "347 origins (8,328 horizon tuples)"
    }
]

# We need solar elevation / daytime flag for files that don't have it explicitly
# We can load forecasting/foundation_models/results/POLARIS_v0_1_fixed_24h_benchmark.csv or SITES data if needed to map daytime flag.
# Let's inspect solar elevation mapping.
sites_path = os.path.join(WORKSPACE, "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv")
# Or benchmark cleared GHI / solar elevation file
clear_sky_path = os.path.join(WORKSPACE, "data/POLARIS_v0_1_clearsky_decomposition.csv")
if os.path.exists(clear_sky_path):
    cs_df = pd.read_csv(clear_sky_path)
    print("Clearsky df shape:", cs_df.shape, "cols:", cs_df.columns.tolist()[:8])

results = []
horizon_rows = []

for src in prediction_sources:
    path = src["file"]
    if not os.path.exists(path):
        print(f"Skipping {src['model_id']} - file not found: {path}")
        continue
    df = pd.read_csv(path)
    y_true = df[src["y_true_col"]].values
    y_pred = df[src["y_pred_col"]].values
    h = df[src["horizon_col"]].values
    
    # Daytime mask determination
    if src["daytime_col"] is not None and src["daytime_col"] in df.columns:
        day_mask = df[src["daytime_col"]].astype(bool).values
    else:
        # If actual_SW_IN > 0 or if we can use timestamp / zenith
        # In POLARIS benchmark, daytime is strictly solar_elevation > 0
        # Let's check if solar_elevation is in df
        if 'solar_elevation' in df.columns:
            day_mask = (df['solar_elevation'] > 0).values
        elif 'actual_SW_IN' in df.columns:
            # Approx daytime flag for raw 8760 files: where actual_SW_IN > 0 or timestamp solar zenith
            # Let's check if we can join with clearsky or solar_elevation
            day_mask = (y_true > 0.0)
        else:
            day_mask = np.ones(len(df), dtype=bool)

    # Compute overall daytime metrics
    y_true_day = y_true[day_mask]
    y_pred_day = y_pred[day_mask]
    mean_y_true_day = np.mean(y_true_day) if len(y_true_day) > 0 else np.nan
    mae = np.mean(np.abs(y_true_day - y_pred_day))
    nmae = (mae / mean_y_true_day) * 100 if mean_y_true_day > 0 else np.nan
    rmse = np.sqrt(np.mean((y_true_day - y_pred_day)**2))
    bias = np.mean(y_pred_day - y_true_day)
    
    results.append({
        "model_id": src["model_id"],
        "stage": src["stage"],
        "split": src["split"],
        "total_rows": len(df),
        "daytime_rows": int(np.sum(day_mask)),
        "mean_y_true_day": float(mean_y_true_day),
        "daytime_mae": float(mae),
        "daytime_nmae": float(nmae),
        "daytime_rmse": float(rmse),
        "daytime_bias": float(bias)
    })
    
    # Horizon breakdown
    for horz in range(1, 25):
        h_mask = (h == horz) & day_mask
        if np.sum(h_mask) > 0:
            yt_h = y_true[h_mask]
            yp_h = y_pred[h_mask]
            m_yt = np.mean(yt_h)
            h_mae = np.mean(np.abs(yt_h - yp_h))
            h_nmae = (h_mae / m_yt) * 100 if m_yt > 0 else np.nan
            h_rmse = np.sqrt(np.mean((yt_h - yp_h)**2))
            h_bias = np.mean(yp_h - yt_h)
            horizon_rows.append({
                "model_id": src["model_id"],
                "stage": src["stage"],
                "horizon": horz,
                "n_daytime": int(np.sum(h_mask)),
                "mean_y_true": float(m_yt),
                "mae": float(h_mae),
                "nmae": float(h_nmae),
                "rmse": float(h_rmse),
                "bias": float(h_bias)
            })

summary_df = pd.DataFrame(results)
print("=== AGGREGATE DAYTIME METRICS SUMMARY ===")
print(summary_df.to_string())

horizon_df = pd.DataFrame(horizon_rows)
print("\n=== SAMPLE HORIZON METRICS (H1 to H5 for Stage8.1) ===")
print(horizon_df[horizon_df['model_id'] == 'Stage8.1_HGB_Control'].head(5).to_string())
