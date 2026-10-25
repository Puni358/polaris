import os
import json
import hashlib
import numpy as np
import pandas as pd

WORKSPACE = "/home/punith-bs/01polaris (Copy)"
BRAIN_DIR = "/home/punith-bs/.gemini/antigravity/brain/78d43461-fb6a-495e-9d93-9d263bdcf970"

# Model comparison matrix dataframe
models_meta = [
    {
        "stage": "Stage 0",
        "model_id": "Persistence_24h",
        "family": "Naive Baseline",
        "architecture": "Rule-based Persistence (y_t = y_{t-24h})",
        "features": 1,
        "nmae": "43.77%",
        "mae": "55.05 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 0",
        "model_id": "Seasonal_Naive_24h",
        "family": "Naive Baseline",
        "architecture": "Rule-based Seasonal Naive",
        "features": 1,
        "nmae": "44.20%",
        "mae": "55.59 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 0",
        "model_id": "Chronos2_ZeroShot_Raw",
        "family": "Foundation Model (Transformer)",
        "architecture": "Chronos-2 Small (T5-based autoregressive FM)",
        "features": 1,
        "nmae": "42.94%",
        "mae": "54.01 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 0",
        "model_id": "Chronos2_Multivariate",
        "family": "Foundation Model (Transformer)",
        "architecture": "Chronos-2 Small (with GHI + ClearSky covariates)",
        "features": 3,
        "nmae": "43.17%",
        "mae": "54.30 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 0",
        "model_id": "TimesFM3_ZeroShot",
        "family": "Foundation Model (Transformer)",
        "architecture": "TimesFM 3.0 (Google Patch-decoder FM)",
        "features": 1,
        "nmae": "68.52%",
        "mae": "86.17 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 0",
        "model_id": "Moirai2_ZeroShot",
        "family": "Foundation Model (Transformer)",
        "architecture": "Moirai 2.0 (Salesforce Patch-based FM)",
        "features": 1,
        "nmae": "84.73%",
        "mae": "106.56 W/m2",
        "status": "REJECTED_BASELINE",
        "odd_run": False
    },
    {
        "stage": "Stage 3A",
        "model_id": "Solar_Geometry_Baseline",
        "family": "GBDT (LightGBM/HGB)",
        "architecture": "Gradient Boosted Trees (Solar angles + Solis GHI)",
        "features": 4,
        "nmae": "48.20%",
        "mae": "62.10 W/m2",
        "status": "SUPERSEDED",
        "odd_run": False
    },
    {
        "stage": "Stage 3B",
        "model_id": "Cloud_NWP_Baseline",
        "family": "GBDT (LightGBM/HGB)",
        "architecture": "GBDT (Solar + MEPS 2D LWP/IWP/CloudFrac)",
        "features": 10,
        "nmae": "36.20%",
        "mae": "46.65 W/m2",
        "status": "SUPERSEDED",
        "odd_run": False
    },
    {
        "stage": "Stage 3C",
        "model_id": "Full_NWP_Baseline",
        "family": "GBDT (LightGBM/HGB)",
        "architecture": "GBDT (Solar + Full single-level MEPS meteorology)",
        "features": 22,
        "nmae": "41.55%",
        "mae": "53.55 W/m2",
        "status": "SUPERSEDED",
        "odd_run": False
    },
    {
        "stage": "Stage 4.1",
        "model_id": "Cloud_Regime_Corrected",
        "family": "GBDT + Affine Residual",
        "architecture": "Stage 3B GBDT + Regime-binned residual corrector",
        "features": 14,
        "nmae": "33.50%",
        "mae": "43.15 W/m2",
        "status": "SUPERSEDED",
        "odd_run": False
    },
    {
        "stage": "Stage 4.3",
        "model_id": "Ensemble_Hybrid",
        "family": "GBDT + Ridge Dynamic Ensemble",
        "architecture": "Dynamic blend of Stage 3B, 3C, and Affine Residuals",
        "features": 26,
        "nmae": "32.98%",
        "mae": "42.51 W/m2",
        "status": "HISTORICAL_CHAMPION",
        "odd_run": False
    },
    {
        "stage": "Stage 6.2",
        "model_id": "Satellite_Thermal_IR",
        "family": "GBDT",
        "architecture": "Stage 4 Champion + SEVIRI 10.8µm IR Brightness Temp",
        "features": 28,
        "nmae": "33.15%",
        "mae": "42.72 W/m2",
        "status": "REJECTED_BY_EVEN_GATES",
        "odd_run": False
    },
    {
        "stage": "Stage 6.4",
        "model_id": "Deterministic_MEPS_Revisions",
        "family": "GBDT",
        "architecture": "Stage 4 Champion + Delta LWP/IWP inter-run drift",
        "features": 30,
        "nmae": "33.25%",
        "mae": "42.85 W/m2",
        "status": "REJECTED_BY_EVEN_GATES",
        "odd_run": False
    },
    {
        "stage": "Stage 7.5",
        "model_id": "Terrain_Horizon_360",
        "family": "GBDT (HGB)",
        "architecture": "Direct HGB + 360-deg DEM Horizon Profile + Vsky",
        "features": 34,
        "nmae": "28.32%",
        "mae": "36.52 W/m2",
        "status": "HISTORICAL_CHAMPION",
        "odd_run": True
    },
    {
        "stage": "Stage 8.1",
        "model_id": "Stage8.1_700hPa_Wind_Control",
        "family": "GBDT (HistGradientBoostingRegressor)",
        "architecture": "Direct HGB + MEPS 700hPa Steering Wind (u700, v700)",
        "features": 37,
        "nmae": "28.07%",
        "mae": "36.19 W/m2",
        "status": "FROZEN_OPERATIONAL_CHAMPION",
        "odd_run": True
    },
    {
        "stage": "Stage 8.17A",
        "model_id": "Real_AROME_Structural_Disagreement",
        "family": "GBDT (HGB)",
        "architecture": "Stage 8.1 + Real AROME-Arctic vector disagreement",
        "features": 40,
        "nmae": "28.25%",
        "mae": "36.43 W/m2",
        "status": "REJECTED_BY_REAL_DATA_REVALIDATION",
        "odd_run": True
    },
    {
        "stage": "Stage 8.19",
        "model_id": "ABIS_GNSS_ZTD_Model",
        "family": "GBDT (HGB)",
        "architecture": "Stage 8.17A + ABIS ZTD latest & 3h trend",
        "features": 42,
        "nmae": "28.30%",
        "mae": "36.49 W/m2",
        "status": "INVALIDATED_HISTORICAL_CLAIM",
        "odd_run": True
    },
    {
        "stage": "Stage 8.24",
        "model_id": "Faithful_Scandes_Orographic_Flow",
        "family": "GBDT (HGB)",
        "architecture": "Stage 8.1 + Scandes barrier-normal wind + Mountain Froude",
        "features": 39,
        "nmae": "27.32% (EVEN)",
        "mae": "37.81 W/m2 (EVEN)",
        "status": "REJECTED_BY_EVEN_GATES",
        "odd_run": False
    },
    {
        "stage": "Stage 8.25",
        "model_id": "Real_SWEPOS_GNSS_Delay_PWV",
        "family": "GBDT (HGB)",
        "architecture": "Stage 8.1 + Real SWEPOS ZTD/PWV features",
        "features": 39,
        "nmae": "N/A",
        "mae": "N/A",
        "status": "CLOSED_FEASIBILITY_UNAVAILABLE",
        "odd_run": False
    }
]

matrix_df = pd.DataFrame(models_meta)
matrix_csv_path = os.path.join(WORKSPACE, "forecasting/reports/other/POLARIS_MODEL_COMPARISON_MATRIX.csv")
matrix_df.to_csv(matrix_csv_path, index=False)
print("Wrote forecasting/reports/other/POLARIS_MODEL_COMPARISON_MATRIX.csv shape:", matrix_df.shape)

# Mirror to brain
dst = os.path.join(BRAIN_DIR, "forecasting/reports/other/POLARIS_MODEL_COMPARISON_MATRIX.csv")
with open(matrix_csv_path, "rb") as f_in, open(dst, "wb") as f_out:
    f_out.write(f_in.read())
print("Mirrored forecasting/reports/other/POLARIS_MODEL_COMPARISON_MATRIX.csv to brain dir")
