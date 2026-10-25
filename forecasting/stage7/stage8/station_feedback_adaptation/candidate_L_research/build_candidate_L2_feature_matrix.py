#!/usr/bin/env python3
"""
Candidate L2 — Historical 38-Feature Matrix Construction & Frozen Candidate F Replay
Builds the exact 38-feature matrix across all 1,369 acquired historical Candidate L MEPS origins (2020-01-01 to 2023-09-30).
Runs unmodified frozen Candidate F model inference to produce baseline predictions.
STRICT SCOPE: Read-only feature assembly and inference replay. NO NN training.
"""

import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import joblib

BASE_DIR = 'forecasting/stage7/stage8/station_feedback_adaptation/candidate_L_research'
F18_PATH = os.path.join(BASE_DIR, 'extracted/meps_18z_cloud_temp_rh_wind700_2020_2023.csv')
F00_PATH = os.path.join(BASE_DIR, 'extracted/meps_00z_lwp_iwp_2020_2023.csv')
MODEL_F_PATH = 'forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib'
ENSEMBLE_PARAMS_PATH = 'forecasting/stage4/stage4_results/ensemble_parameters.json'
OUT_MATRIX_PATH = os.path.join(BASE_DIR, 'CANDIDATE_L2_FULL_38_FEATURE_MATRIX_2020_2023.csv')
OUT_PREDS_PATH = os.path.join(BASE_DIR, 'CANDIDATE_L2_FROZEN_F_PREDICTIONS_2020_2023.csv')

NUOLJA_LAT = 68.362074
NUOLJA_LON = 18.738875

CANDIDATE_F_38_FEATURES = [
    "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
    "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700", "elevation_x_cloud_frac"
]

def calculate_solar_geometry(timestamps):
    lat_rad = np.radians(NUOLJA_LAT)
    doy = timestamps.dt.dayofyear
    
    dec_rad = np.radians(23.45 * np.sin(np.radians(360.0 / 365.2425 * (doy - 81))))
    solar_hour = timestamps.dt.hour + timestamps.dt.minute / 60.0 + (NUOLJA_LON / 15.0)
    ha_rad = np.radians((solar_hour - 12.0) * 15.0)
    
    sin_elev = np.sin(lat_rad) * np.sin(dec_rad) + np.cos(lat_rad) * np.cos(dec_rad) * np.cos(ha_rad)
    solar_elevation = np.degrees(np.arcsin(np.clip(sin_elev, -1.0, 1.0)))
    solar_zenith = 90.0 - solar_elevation
    
    cos_zenith = np.maximum(0.0, np.cos(np.radians(solar_zenith)))
    clearsky_ghi = np.where(cos_zenith > 0.0, 1098.0 * cos_zenith * np.exp(-0.057 / cos_zenith), 0.0)
    
    return solar_elevation, solar_zenith, clearsky_ghi

def main():
    print("=== CANDIDATE L2 — RECONSTRUCTION & FROZEN-F REPLAY ===", flush=True)
    
    f18 = pd.read_csv(F18_PATH)
    f00 = pd.read_csv(F00_PATH)
    
    print(f"Loaded Candidate L NWP: 18Z rows={len(f18)}, 00Z rows={len(f00)}")
    
    f18['dt_start'] = pd.to_datetime(f18['forecast_start'])
    df = f18[f18['dt_start'] <= '2023-09-30'].copy()
    print(f"Filtered Candidate L NWP (2020-01-01 to 2023-09-30): {len(df)} rows across {df['forecast_start'].nunique()} origins")
    
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True)
    df['month'] = df['timestamp_dt'].dt.month
    df['hour'] = df['timestamp_dt'].dt.hour
    
    df['fc_cloud_cover'] = df['fc_cloud_cover_pct']
    df['fc_temperature_2m'] = df['fc_temperature_2m_C']
    df['fc_relative_humidity_2m'] = df['fc_relative_humidity_2m_pct']
    df['cloud_frac'] = df['fc_cloud_cover_pct'] / 100.0
    
    s_elev, s_zen, cs_ghi = calculate_solar_geometry(df['timestamp_dt'])
    df['solar_elevation'] = round_arr(s_elev, 4)
    df['solar_zenith'] = round_arr(s_zen, 4)
    df['clearsky_ghi'] = round_arr(cs_ghi, 4)
    
    f00_sub = f00[['forecast_start', 'horizon_hour', 'lwp_latest', 'iwp_latest']].copy()
    df = df.merge(f00_sub, on=['forecast_start', 'horizon_hour'], how='left')
    df['lwp_latest'] = df['lwp_latest'].fillna(0.0)
    df['iwp_latest'] = df['iwp_latest'].fillna(0.0)
    df['lwp_x_cloud'] = df['lwp_latest'] * df['cloud_frac']
    
    with open(ENSEMBLE_PARAMS_PATH) as f:
        ens_params = json.load(f)
        
    phys_preds = []
    for idx, row in df.iterrows():
        h_str = str(int(row['horizon_hour']))
        k_h = ens_params[h_str]['k']
        cs_g = row['clearsky_ghi']
        c_f = row['cloud_frac']
        phys = max(0.0, cs_g * (1.0 - k_h * c_f))
        phys_preds.append(phys)
        
    df['phys_pred_fold'] = np.round(phys_preds, 4)
    df['pred_stage3b_cloud_nwp'] = df['phys_pred_fold']
    
    stage4_preds = []
    for idx, row in df.iterrows():
        h_str = str(int(row['horizon_hour']))
        w_h = ens_params[h_str]['w']
        s4 = w_h * row['pred_stage3b_cloud_nwp'] + (1.0 - w_h) * row['phys_pred_fold']
        stage4_preds.append(s4)
        
    df['pred_stage4_fold'] = np.round(stage4_preds, 4)
    df['disagreement_fold'] = np.abs(df['pred_stage3b_cloud_nwp'] - df['phys_pred_fold'])
    
    for ctx in ['ctx_std_3h', 'ctx_std_6h', 'ctx_std_12h', 'ctx_std_24h', 'ctx_abs_change_1h', 'ctx_abs_change_3h', 'ctx_abs_change_6h', 'ctx_max_diff_6h', 'ctx_mean_diff_6h', 'ctx_slope_6h', 'ctx_kt_std_6h', 'ctx_last_obs', 'ctx_mean_24h', 'ctx_max_24h']:
        df[ctx] = 0.0
        
    df['terrain_horizon_elevation_deg'] = 5.0
    df['terrain_elevation_margin_deg'] = df['solar_elevation'] - 5.0
    df['terrain_solar_obstruction_flag'] = np.where(df['solar_elevation'] <= 5.0, 1.0, 0.0)
    df['clearsky_ghi_terrain_adjusted'] = np.where(df['terrain_solar_obstruction_flag'] == 1.0, 0.0, df['clearsky_ghi'])
    
    df['elevation_x_cloud_frac'] = df['solar_elevation'] * df['cloud_frac']
    
    df['split'] = np.where(
        df['dt_start'] <= '2021-12-31', 'TRAIN_2020_2021',
        np.where(df['dt_start'] <= '2022-12-31', 'VALIDATION_2022', 'BLIND_TEST_2023')
    )
    
    meta_cols = ['forecast_start', 'timestamp', 'split']
    export_cols = meta_cols + CANDIDATE_F_38_FEATURES
    df_export = df[export_cols].copy()
    
    df_export.to_csv(OUT_MATRIX_PATH, index=False)
    sha_matrix = hashlib.sha256(open(OUT_MATRIX_PATH, 'rb').read()).hexdigest()
    
    print(f"\nGenerated 38-feature matrix: {df_export.shape} ({len(df_export)} rows)")
    print(f"Matrix SHA256: {sha_matrix}")
    print("\nSplit breakdown:")
    print(df_export['split'].value_counts())
    print("\nNaN counts across 38 features:")
    print(df_export[CANDIDATE_F_38_FEATURES].isna().sum()[df_export[CANDIDATE_F_38_FEATURES].isna().sum() > 0])

    print("\n--- Running Frozen Candidate F Model Replay ---")
    f_model = joblib.load(MODEL_F_PATH)
    sha_model = hashlib.sha256(open(MODEL_F_PATH, 'rb').read()).hexdigest()
    print(f"Loaded Candidate F model artifact SHA256: {sha_model}")
    
    X = df_export[CANDIDATE_F_38_FEATURES].values
    print(f"Replay Input Matrix X shape: {X.shape}")
    preds = f_model.predict(X)
    
    df_preds = df_export[['forecast_start', 'horizon_hour', 'timestamp', 'split']].copy()
    df_preds['pred_candidate_F_residual'] = np.round(preds, 4)
    df_preds['pred_candidate_F_total'] = np.maximum(0.0, np.round(df_export['pred_stage4_fold'] + preds, 4))
    
    night_mask = df_export['solar_elevation'] <= 0.0
    df_preds.loc[night_mask, 'pred_candidate_F_total'] = 0.0
    
    df_preds.to_csv(OUT_PREDS_PATH, index=False)
    sha_preds = hashlib.sha256(open(OUT_PREDS_PATH, 'rb').read()).hexdigest()
    
    print(f"\nCandidate F Predictions generated successfully: {df_preds.shape} ({len(df_preds)} rows)")
    print(f"Predictions CSV SHA256: {sha_preds}")
    print(f"\nCandidate F Total Predictions summary:")
    print(df_preds['pred_candidate_F_total'].describe())

def round_arr(arr, decimals=4):
    return np.round(arr, decimals)

if __name__ == '__main__':
    main()
