import os
import json
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE7_5_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
STAGE8_1_WIND_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"

OUTPUT_MATRIX_PATH = STAGE_DIR / "stage8_1_full_37_feature_matrix_2024.csv"

def build_stage8_1_matrix():
    print("Loading component data files...")
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"], utc=True)
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"], utc=True)
    
    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["timestamp"] = pd.to_datetime(df_nwp["timestamp"], utc=True)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)
    
    df_sites = pd.read_csv(SITES_PATH)
    df_sites["timestamp"] = pd.to_datetime(df_sites["TIMESTAMP"], utc=True)
    
    df_cs = pd.read_csv(CLEARSKY_PATH)
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)
    
    df_66 = pd.read_csv(STAGE6_6_FEAT_PATH)
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)
    
    df_75 = pd.read_csv(STAGE7_5_FEAT_PATH)
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)
    
    df_wind = pd.read_csv(STAGE8_1_WIND_PATH)
    df_wind["forecast_start"] = pd.to_datetime(df_wind["forecast_start"], utc=True)
    
    df = s4_preds.copy()
    
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    
    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]
    df = df.merge(df_cs[cs_cols], on="timestamp", how="left")
    
    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]
    
    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    df = df.merge(df_75[terrain_cols], on="timestamp", how="left")
    
    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df = df.merge(df_wind[wind_cols], on=["forecast_start", "horizon_hour"], how="left")
    
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["is_daytime"] = df["actual_SW_IN"] > 0
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    
    with open(STAGE4_PARAMS_PATH) as f:
        ensemble_params_full = json.load(f)
        
    phys_preds_full = []
    for idx, row in df.iterrows():
        h = str(int(row["horizon_hour"]))
        p = ensemble_params_full[h]
        k_h = p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        phys_preds_full.append(phys)
        
    df["phys_pred_fold"] = phys_preds_full
    df["pred_stage4_fold"] = df["pred_ensemble"]
    df["disagreement_fold"] = (df["pred_stage3b_cloud_nwp"] - df["phys_pred_fold"]).abs()
    
    all_origins = sorted(df["forecast_start"].unique())
    ctx_feature_rows = []
    
    for origin_ts in all_origins:
        context_start = origin_ts - timedelta(hours=24)
        ctx_sites = df_sites[(df_sites["timestamp"] >= context_start) & (df_sites["timestamp"] < origin_ts)].sort_values("timestamp")
        
        if len(ctx_sites) < 24:
            ctx_feature_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue
            
        sw_vals = ctx_sites["SW_IN"].values
        s3, s6, s12, s24 = sw_vals[-3:], sw_vals[-6:], sw_vals[-12:], sw_vals[-24:]
        
        std_3h = np.std(s3) if len(s3) > 1 else 0.0
        std_6h = np.std(s6) if len(s6) > 1 else 0.0
        std_12h = np.std(s12) if len(s12) > 1 else 0.0
        std_24h = np.std(s24) if len(s24) > 1 else 0.0
        
        abs_chg_1h = abs(sw_vals[-1] - sw_vals[-2]) if len(sw_vals) >= 2 else 0.0
        abs_chg_3h = abs(sw_vals[-1] - sw_vals[-4]) if len(sw_vals) >= 4 else 0.0
        abs_chg_6h = abs(sw_vals[-1] - sw_vals[-7]) if len(sw_vals) >= 7 else 0.0
        
        diffs_6h = np.abs(np.diff(s6)) if len(s6) > 1 else [0.0]
        max_diff_6h = np.max(diffs_6h)
        mean_diff_6h = np.mean(diffs_6h)
        slope_6h = np.polyfit(np.arange(len(s6)), s6, 1)[0] if len(s6) >= 3 else 0.0
        
        ctx_cs = df_cs[(df_cs["timestamp"] >= context_start) & (df_cs["timestamp"] < origin_ts)].sort_values("timestamp")
        if len(ctx_cs) == len(ctx_sites):
            cs_ghi_vals = ctx_cs["clearsky_ghi"].values
            valid_cs = cs_ghi_vals > 10.0
            kt_vals = np.zeros_like(sw_vals)
            kt_vals[valid_cs] = np.clip(sw_vals[valid_cs] / cs_ghi_vals[valid_cs], 0.0, 1.5)
            kt_std_6h = np.std(kt_vals[-6:]) if len(kt_vals) >= 6 else 0.0
        else:
            kt_std_6h = 0.0
            
        ctx_feature_rows.append({
            "forecast_start": origin_ts,
            "ctx_std_3h": std_3h, "ctx_std_6h": std_6h, "ctx_std_12h": std_12h, "ctx_std_24h": std_24h,
            "ctx_abs_change_1h": abs_chg_1h, "ctx_abs_change_3h": abs_chg_3h, "ctx_abs_change_6h": abs_chg_6h,
            "ctx_max_diff_6h": max_diff_6h, "ctx_mean_diff_6h": mean_diff_6h, "ctx_slope_6h": slope_6h,
            "ctx_kt_std_6h": kt_std_6h, "ctx_last_obs": sw_vals[-1],
            "ctx_mean_24h": np.mean(s24), "ctx_max_24h": np.max(s24)
        })
        
    ctx_df = pd.DataFrame(ctx_feature_rows)
    df = df.merge(ctx_df, on="forecast_start", how="left")
    
    # Assign origin index (1 to 347)
    origin_map = {orig: i + 1 for i, orig in enumerate(all_origins)}
    df["origin_id"] = df["forecast_start"].map(origin_map)
    df["split"] = np.where(df["origin_id"] % 2 == 0, "EVEN", "ODD")
    
    candidate_37_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
        "lwp_latest", "iwp_latest", "lwp_x_cloud",
        "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
        "u700", "v700"
    ]
    
    meta_cols = ["origin_id", "forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "split", "is_daytime", "is_night_causal"]
    export_cols = meta_cols + candidate_37_features
    
    df_export = df[export_cols].copy()
    df_export.to_csv(OUTPUT_MATRIX_PATH, index=False)
    
    sha256 = hashlib.sha256(open(OUTPUT_MATRIX_PATH, "rb").read()).hexdigest()
    print("Matrix generated successfully!")
    print(f"File Path: {OUTPUT_MATRIX_PATH}")
    print(f"Dimensions: {df_export.shape}")
    print(f"SHA256: {sha256}")
    print(f"EVEN Origins: {len(df_export[df_export['split'] == 'EVEN']['origin_id'].unique())} (4,152 rows)")
    print(f"ODD Origins: {len(df_export[df_export['split'] == 'ODD']['origin_id'].unique())} (4,176 rows)")
    print(f"NaN count in 37 features: {df_export[candidate_37_features].isna().sum().sum()}")
    return df_export, sha256

if __name__ == "__main__":
    df_export, sha256 = build_stage8_1_matrix()
