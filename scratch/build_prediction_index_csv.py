import os
import json
import hashlib
import numpy as np
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"
BRAIN_DIR = "/home/punith-bs/.gemini/antigravity/brain/78d43461-fb6a-495e-9d93-9d263bdcf970"

prediction_sources = [
    {
        "stage": "Stage 8.1",
        "model_family": "GBDT",
        "model_version": "HistGradientBoostingRegressor 37-feature",
        "configuration": "Stage8.1 Control (u700, v700)",
        "file": os.path.join(WORKSPACE, "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"),
        "y_true_col": "y_true",
        "y_pred_col": "y_pred",
        "origin_col": "origin_id",
        "horizon_col": "horizon",
        "timestamp_col": "valid_timestamp",
        "daytime_col": "daytime_flag",
        "eval_split": "ODD"
    },
    {
        "stage": "Stage 8.17A",
        "model_family": "GBDT",
        "model_version": "HistGradientBoostingRegressor 40-feature",
        "configuration": "Stage8.17A Real AROME Disagreement",
        "file": os.path.join(WORKSPACE, "forecasting/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv"),
        "y_true_col": "actual_sw_in",
        "y_pred_col": "candidate_prediction",
        "origin_col": "origin_t0",
        "horizon_col": "horizon_h",
        "timestamp_col": "valid_time",
        "daytime_col": "daytime_flag",
        "eval_split": "ODD"
    },
    {
        "stage": "Stage 8.19",
        "model_family": "GBDT",
        "model_version": "HistGradientBoostingRegressor 42-feature",
        "configuration": "Stage8.19 ABIS GNSS Reproduced",
        "file": os.path.join(WORKSPACE, "forecasting/stage7/stage8/STAGE8_19_ODD_PREDICTIONS_REPRODUCED.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "predicted_SW_IN",
        "origin_col": "origin_timestamp",
        "horizon_col": "horizon_hour",
        "timestamp_col": "target_timestamp",
        "daytime_col": "daytime_flag",
        "eval_split": "ODD"
    },
    {
        "stage": "Stage 0",
        "model_family": "Foundation Model",
        "model_version": "Chronos-2 Small Raw",
        "configuration": "Univariate Zero-Shot",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "chronos2",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "Full 347 origins"
    },
    {
        "stage": "Stage 0",
        "model_family": "Foundation Model",
        "model_version": "Chronos-2 Small Multivariate",
        "configuration": "Multivariate Covariates (GHI + ClearSky)",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_chronos2_multivariate_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "chronos2_multivariate",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "Full 347 origins"
    },
    {
        "stage": "Stage 0",
        "model_family": "Foundation Model",
        "model_version": "TimesFM 3.0",
        "configuration": "Univariate Zero-Shot",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "timesfm3",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "Full 347 origins"
    },
    {
        "stage": "Stage 0",
        "model_family": "Foundation Model",
        "model_version": "Moirai 2.0",
        "configuration": "Univariate Zero-Shot",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "moirai2",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "Full 347 origins"
    },
    {
        "stage": "Stage 0",
        "model_family": "Naive Baseline",
        "model_version": "Kt Persistence 24h",
        "configuration": "Clearsky Index Persistence",
        "file": os.path.join(WORKSPACE, "forecasting/foundation_models/results/POLARIS_v0_1_kt_persistence_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "kt_persistence_24h",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "Full 347 origins"
    },
    {
        "stage": "Stage 4.3",
        "model_family": "GBDT + Ridge Ensemble",
        "model_version": "Dynamic Ensemble Hybrid",
        "configuration": "Stage 3B + 3C + Affine Residual Blend",
        "file": os.path.join(WORKSPACE, "forecasting/stage4/stage4_results/ensemble_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_ensemble",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "347 origins (8,328 horizon tuples)"
    },
    {
        "stage": "Stage 3C",
        "model_family": "GBDT",
        "model_version": "LightGBM 22-feature",
        "configuration": "Full Single-Level MEPS NWP",
        "file": os.path.join(WORKSPACE, "forecasting/stage3/stage3c_full_nwp_predictions.csv"),
        "y_true_col": "actual_SW_IN",
        "y_pred_col": "pred_stage3c_full_nwp",
        "origin_col": "forecast_start",
        "horizon_col": "horizon_hour",
        "timestamp_col": "timestamp",
        "daytime_col": None,
        "eval_split": "347 origins (8,328 horizon tuples)"
    }
]

consolidated_dfs = []

for src in prediction_sources:
    path = src["file"]
    if not os.path.exists(path):
        continue
    df = pd.read_csv(path)
    
    exp_id = src["model_version"].replace(" ", "_")
    stage = src["stage"]
    mf = src["model_family"]
    mv = src["model_version"]
    cfg = src["configuration"]
    
    yt = df[src["y_true_col"]].values
    yp = df[src["y_pred_col"]].values
    orig = df[src["origin_col"]].values
    h = df[src["horizon_col"]].values
    ts = df[src["timestamp_col"]].values if src["timestamp_col"] in df.columns else np.nan
    
    if src["daytime_col"] is not None and src["daytime_col"] in df.columns:
        day_mask = df[src["daytime_col"]].astype(bool).values
    else:
        if 'solar_elevation' in df.columns:
            day_mask = (df['solar_elevation'] > 0).values
        else:
            day_mask = (yt > 0.0)

    err = yp - yt
    abs_err = np.abs(err)
    
    cdf = pd.DataFrame({
        "experiment_id": exp_id,
        "stage": stage,
        "model_family": mf,
        "model_version": mv,
        "configuration": cfg,
        "origin": orig,
        "forecast_horizon": h,
        "timestamp": ts,
        "actual": yt,
        "prediction": yp,
        "error": err,
        "abs_error": abs_err,
        "is_daytime": day_mask,
        "evaluation_split": src["eval_split"],
        "artifact_source": os.path.basename(path)
    })
    
    consolidated_dfs.append(cdf)

index_df = pd.concat(consolidated_dfs, ignore_index=True)
index_csv_path = os.path.join(WORKSPACE, "forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv")
index_df.to_csv(index_csv_path, index=False)
print("Wrote forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv shape:", index_df.shape)

dst = os.path.join(BRAIN_DIR, "forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv")
with open(index_csv_path, "rb") as f_in, open(dst, "wb") as f_out:
    f_out.write(f_in.read())
print("Mirrored forecasting/reports/other/POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv to brain dir")
