import os
import json
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime

WORKSPACE = "/home/punith-bs/01polaris (Copy)"
REAL_REVAL_DIR = os.path.join(WORKSPACE, "forecasting/stage7", "stage8", "real_revalidation")
BRAIN_DIR = "/home/punith-bs/.gemini/antigravity/brain/78d43461-fb6a-495e-9d93-9d263bdcf970"
SCRATCH_DIR = os.path.join(WORKSPACE, "scratch")

os.makedirs(REAL_REVAL_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

# 1. Build forecasting/reports/other/POLARIS_MODEL_HORIZON_ERROR_SUMMARY.csv
# We calculate horizon H1-H24 metrics for recoverable models
prediction_sources = [
    {
        "model_id": "Stage8.1_HGB_Control",
        "stage": "Stage 8.1",
        "file": os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"),
        "y_true_col": "y_true",
        "y_pred_col": "y_pred",
        "horizon_col": "horizon",
        "daytime_col": "daytime_flag",
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
        "split": "Full 347 origins"
    },
    {
        "model_id": "Chronos2_Multivariate",
        "stage": "Chronos-2 Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_multivariate_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "chronos2_multivariate",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    },
    {
        "model_id": "TimesFM3",
        "stage": "TimesFM Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "timesfm3",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    },
    {
        "model_id": "Moirai2",
        "stage": "Moirai Evaluation",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "moirai2",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    },
    {
        "model_id": "Kt_Persistence_24h",
        "stage": "Persistence Baseline",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "kt_persistence_24h",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    },
    {
        "model_id": "Stage4_Ensemble_Hybrid",
        "stage": "Stage 4.3",
        "file": os.path.join(WORKSPACE, "forecasting/stage4/stage4_results/ensemble_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_ensemble",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    },
    {
        "model_id": "Stage3C_Full_NWP",
        "stage": "Stage 3C",
        "file": os.path.join(WORKSPACE, "forecasting/stage3/stage3c_full_nwp_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_stage3c_full_nwp",
        "horizon_col": "horizon_hour",
        "daytime_col": None,
        "split": "Full 347 origins"
    }
]

horizon_rows = []

for src in prediction_sources:
    path = src["file"]
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path)
    y_true = df[src["y_true_col"]].values
    y_pred = df[src["y_pred_col"]].values
    h = df[src["horizon_col"]].values
    
    if src["daytime_col"] is not None and src["daytime_col"] in df.columns:
        day_mask = df[src["daytime_col"]].astype(bool).values
    else:
        if 'solar_elevation' in df.columns:
            day_mask = (df['solar_elevation'] > 0).values
        else:
            day_mask = (y_true > 0.0)

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
                "split": src["split"],
                "horizon": horz,
                "n_daytime": int(np.sum(h_mask)),
                "mean_y_true": float(m_yt),
                "mae": float(h_mae),
                "nmae": float(h_nmae),
                "rmse": float(h_rmse),
                "bias": float(h_bias)
            })

horizon_summary_df = pd.DataFrame(horizon_rows)
horizon_csv_path = os.path.join(WORKSPACE, "forecasting/reports/other/POLARIS_MODEL_HORIZON_ERROR_SUMMARY.csv")
horizon_summary_df.to_csv(horizon_csv_path, index=False)
print("Wrote forecasting/reports/other/POLARIS_MODEL_HORIZON_ERROR_SUMMARY.csv shape:", horizon_summary_df.shape)

# Mirror CSV files
for fname in ["forecasting/reports/other/POLARIS_MODEL_HORIZON_ERROR_SUMMARY.csv"]:
    src = os.path.join(WORKSPACE, fname)
    dst = os.path.join(BRAIN_DIR, fname)
    if os.path.exists(src):
        with open(src, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())
        print(f"Mirrored {fname} to brain dir")

