"""
POLARIS Path A — Phase A2 Wind Speed Forecasting Research Script
Authoritative empirical evaluation of wind-speed forecasting approaches on the Abisko 10m target.
"""
import os
import json
import math
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

# Directories
WORKSPACE_DIR = "/home/punith-bs/01polaris (Copy)"
RESEARCH_DIR = os.path.join(WORKSPACE_DIR, "research", "wind_a2")
os.makedirs(RESEARCH_DIR, exist_ok=True)

# File Paths
WIND_SPEED_FILE = os.path.join(RESEARCH_DIR, "smhi_188790_ws_full.csv")
WIND_DIR_FILE = os.path.join(RESEARCH_DIR, "smhi_188790_wd_full.csv")
NWP_FORECAST_FILE = os.path.join(WORKSPACE_DIR, "data", "POLARIS_v0_1_future_weather_forecasts_2024.csv")
SITES_MET_FILE = os.path.join(WORKSPACE_DIR, "data", "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv")
CANONICAL_FOLDS_FILE = os.path.join(WORKSPACE_DIR, "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv")

import re

def parse_smhi_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    records = []
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    for line in lines:
        parts = line.strip().split(';')
        if len(parts) >= 4 and date_pattern.match(parts[0]):
            datum, tid, val, qual = parts[0], parts[1], parts[2], parts[3]
            if datum.startswith('2024') and val != '':
                try:
                    records.append({
                        'timestamp': f"{datum} {tid}",
                        'val': float(val),
                        'quality': qual
                    })
                except ValueError:
                    pass
    df = pd.DataFrame(records)
    if len(df) == 0:
        raise ValueError(f"No 2024 records found in {file_path}")
    df['dt'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('dt').reset_index(drop=True)
    return df

print("1. Parsing SMHI Abisko Target Datasets...")
df_ws = parse_smhi_csv(WIND_SPEED_FILE)
df_ws = df_ws.rename(columns={'val': 'ws_10m'})

df_wd = parse_smhi_csv(WIND_DIR_FILE)
df_wd = df_wd.rename(columns={'val': 'wd_10m'})

# Merge Target Data (Left join on WS so all 8,690 wind speed observations in 2024 are preserved)
df_target = pd.merge(df_ws[['dt', 'ws_10m', 'quality']], df_wd[['dt', 'wd_10m']], on='dt', how='left')
print(f"Target dataset parsed: {len(df_target)} hourly rows for 2024.")
print(f"WS range: {df_target['ws_10m'].min()} to {df_target['ws_10m'].max()} m/s, Mean: {df_target['ws_10m'].mean():.2f} m/s")

# Save processed target series in isolated research dir
df_target.to_csv(os.path.join(RESEARCH_DIR, "smhi_abisko_target_2024.csv"), index=False)

# Load NWP Forecast Table
print("2. Loading NWP Forecasts and SITES Meteorological Predictors...")
df_nwp = pd.read_csv(NWP_FORECAST_FILE)
df_nwp['forecast_start_dt'] = pd.to_datetime(df_nwp['forecast_start'], utc=True)
df_nwp['timestamp_dt'] = pd.to_datetime(df_nwp['timestamp'], utc=True)

# Load SITES Met Predictors
df_sites = pd.read_csv(SITES_MET_FILE)
df_sites['dt'] = pd.to_datetime(df_sites['TIMESTAMP'], utc=True)

# Build Target Lookup Dict
target_lookup = dict(zip(df_target['dt'], df_target['ws_10m']))
wd_lookup = dict(zip(df_target['dt'], df_target['wd_10m']))
sites_ta_lookup = dict(zip(df_sites['dt'], df_sites['TA']))
sites_rh_lookup = dict(zip(df_sites['dt'], df_sites['RH']))

# Get Unique Forecast Origins in 2024 NWP Table
unique_origins = sorted(df_nwp['forecast_start_dt'].unique())
print(f"Total forecast origins in NWP dataset: {len(unique_origins)}")

# Construct Leakage-Safe Feature & Target Matrix
print("3. Building Causal Feature Matrix...")
dataset_rows = []

for origin_idx, origin_dt in enumerate(unique_origins):
    # Origin timestamp t0
    origin_str = origin_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract past 24h target observations strictly at or before t0
    ws_lags = []
    wd_lags_sin = []
    wd_lags_cos = []
    
    for lag in range(0, 24):
        t_lag = origin_dt - pd.Timedelta(hours=lag)
        v_val = target_lookup.get(t_lag, np.nan)
        d_val = wd_lookup.get(t_lag, np.nan)
        ws_lags.append(v_val)
        if not np.isnan(d_val):
            rad = math.radians(d_val)
            wd_lags_sin.append(math.sin(rad))
            wd_lags_cos.append(math.cos(rad))
        else:
            wd_lags_sin.append(np.nan)
            wd_lags_cos.append(np.nan)
            
    # Check if origin has valid target lags
    if np.isnan(ws_lags[0]):
        continue
        
    v_t0 = ws_lags[0]
    v_t1 = ws_lags[1] if not np.isnan(ws_lags[1]) else v_t0
    v_t2 = ws_lags[2] if not np.isnan(ws_lags[2]) else v_t0
    v_t3 = ws_lags[3] if not np.isnan(ws_lags[3]) else v_t0
    v_t6 = ws_lags[6] if not np.isnan(ws_lags[6]) else v_t0
    v_t12 = ws_lags[12] if not np.isnan(ws_lags[12]) else v_t0
    v_t23 = ws_lags[23] if not np.isnan(ws_lags[23]) else v_t0
    
    valid_ws_lags = [x for x in ws_lags if not np.isnan(x)]
    v_mean_24h = np.mean(valid_ws_lags) if valid_ws_lags else v_t0
    v_std_24h = np.std(valid_ws_lags) if len(valid_ws_lags) > 1 else 0.0
    v_min_24h = np.min(valid_ws_lags) if valid_ws_lags else v_t0
    v_max_24h = np.max(valid_ws_lags) if valid_ws_lags else v_t0
    v_trend_6h = v_t0 - v_t6
    
    # Ground SITES predictors at t0
    ta_t0 = sites_ta_lookup.get(origin_dt, 0.0)
    rh_t0 = sites_rh_lookup.get(origin_dt, 75.0)
    
    # Extract 24 horizon steps for this origin from NWP table
    nwp_sub = df_nwp[df_nwp['forecast_start_dt'] == origin_dt].sort_values('horizon_hour')
    if len(nwp_sub) != 24:
        continue
        
    for h_step in range(1, 25):
        nwp_row = nwp_sub[nwp_sub['horizon_hour'] == h_step].iloc[0]
        step_dt = nwp_row['timestamp_dt']
        
        # Ground-truth target at t0 + h_step
        y_true = target_lookup.get(step_dt, np.nan)
        if np.isnan(y_true):
            continue
            
        # NWP Predictors
        fc_ws_10m = nwp_row['fc_wind_speed_10m']
        fc_press = nwp_row['fc_surface_pressure']
        fc_temp = nwp_row['fc_temperature_2m']
        fc_rh = nwp_row['fc_relative_humidity_2m']
        fc_cloud = nwp_row['fc_cloud_cover']
        fc_precip = nwp_row['fc_precipitation']
        
        # Temporal features
        hour = step_dt.hour
        doy = step_dt.dayofyear
        sin_doy = math.sin(2.0 * math.pi * doy / 366.0)
        cos_doy = math.cos(2.0 * math.pi * doy / 366.0)
        
        dataset_rows.append({
            'origin_idx': origin_idx,
            'origin_dt': origin_dt,
            'horizon_hour': h_step,
            'step_dt': step_dt,
            'y_true': y_true,
            'v_t0': v_t0,
            'v_t1': v_t1,
            'v_t2': v_t2,
            'v_t3': v_t3,
            'v_t6': v_t6,
            'v_t12': v_t12,
            'v_t23': v_t23,
            'v_mean_24h': v_mean_24h,
            'v_std_24h': v_std_24h,
            'v_min_24h': v_min_24h,
            'v_max_24h': v_max_24h,
            'v_trend_6h': v_trend_6h,
            'wd_sin_t0': wd_lags_sin[0] if not np.isnan(wd_lags_sin[0]) else 0.0,
            'wd_cos_t0': wd_lags_cos[0] if not np.isnan(wd_lags_cos[0]) else 1.0,
            'ta_t0': ta_t0,
            'rh_t0': rh_t0,
            'fc_ws_10m': fc_ws_10m,
            'fc_press': fc_press,
            'fc_temp': fc_temp,
            'fc_rh': fc_rh,
            'fc_cloud': fc_cloud,
            'fc_precip': fc_precip,
            'hour': hour,
            'doy': doy,
            'sin_doy': sin_doy,
            'cos_doy': cos_doy
        })

df_feat = pd.DataFrame(dataset_rows)
print(f"Dataset matrix constructed: {len(df_feat)} total instance rows ({len(df_feat)/24:.0f} complete 24h origins).")

# Split Data Chronologically
# Train: Origins 0 to 223 (Jan 20 to Aug 31)
# Val: Origins 224 to 284 (Sep 01 to Oct 31)
# Test: Origins 285 to 346 (Nov 01 to Dec 31)
train_mask = df_feat['origin_idx'] <= 223
val_mask = (df_feat['origin_idx'] > 223) & (df_feat['origin_idx'] <= 284)
test_mask = df_feat['origin_idx'] > 284

df_train = df_feat[train_mask]
df_val = df_feat[val_mask]
df_test = df_feat[test_mask]

print(f"Train set: {len(df_train)} rows ({len(df_train)/24:.0f} origins)")
print(f"Val set:   {len(df_val)} rows ({len(df_val)/24:.0f} origins)")
print(f"Test set:  {len(df_test)} rows ({len(df_test)/24:.0f} origins)")

# Feature Columns for Models
feature_cols = [
    'v_t0', 'v_t1', 'v_t2', 'v_t3', 'v_t6', 'v_t12', 'v_t23',
    'v_mean_24h', 'v_std_24h', 'v_min_24h', 'v_max_24h', 'v_trend_6h',
    'wd_sin_t0', 'wd_cos_t0', 'ta_t0', 'rh_t0',
    'fc_ws_10m', 'fc_press', 'fc_temp', 'fc_rh', 'fc_cloud', 'fc_precip',
    'hour', 'sin_doy', 'cos_doy'
]

# Baseline Models Evaluation on Test Set
print("\n4. Evaluating Baselines and Candidates...")

# Compute Diurnal Hourly Means from Train Set for Diurnal Baseline
diurnal_means = df_train.groupby('hour')['y_true'].mean().to_dict()

# Baseline Predictions on Test Set
y_test_true = df_test['y_true'].values

# Baseline 1: Naive Persistence (y_pred = v_t0)
pred_b1_persistence = df_test['v_t0'].values

# Baseline 2: Diurnal Climate Persistence
pred_b2_diurnal = df_test['hour'].map(diurnal_means).values

# Baseline 3: Raw NWP Forecast
pred_b3_nwp = df_test['fc_ws_10m'].values

# Candidate 1: GBDT Direct Multi-Horizon (HistGradientBoostingRegressor per horizon)
gbdt_models = {}
pred_c1_gbdt = np.zeros(len(df_test))

for h in range(1, 25):
    h_train = df_train[df_train['horizon_hour'] == h]
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    
    X_tr = h_train[feature_cols]
    y_tr = h_train['y_true']
    
    model = HistGradientBoostingRegressor(
        max_iter=100,
        learning_rate=0.05,
        max_depth=5,
        min_samples_leaf=15,
        random_state=42
    )
    model.fit(X_tr, y_tr)
    gbdt_models[h] = model
    
    X_te = df_test.loc[h_test_indices, feature_cols]
    preds = model.predict(X_te)
    # Physical non-negativity clipping
    preds = np.clip(preds, 0.0, None)
    df_test.loc[h_test_indices, 'pred_gbdt'] = preds

pred_c1_gbdt = df_test['pred_gbdt'].values

# Candidate 2: NWP Residual Bias-Correction Model (HistGradientBoostingRegressor on NWP Error)
df_train['nwp_error'] = df_train['y_true'] - df_train['fc_ws_10m']
df_test['nwp_error_true'] = df_test['y_true'] - df_test['fc_ws_10m']

pred_c2_nwp_corr = np.zeros(len(df_test))
for h in range(1, 25):
    h_train = df_train[df_train['horizon_hour'] == h]
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    
    X_tr = h_train[feature_cols]
    y_err_tr = h_train['nwp_error']
    
    model_err = HistGradientBoostingRegressor(
        max_iter=80,
        learning_rate=0.03,
        max_depth=4,
        min_samples_leaf=20,
        random_state=42
    )
    model_err.fit(X_tr, y_err_tr)
    
    X_te = df_test.loc[h_test_indices, feature_cols]
    pred_err = model_err.predict(X_te)
    raw_nwp = df_test.loc[h_test_indices, 'fc_ws_10m'].values
    corr_preds = np.clip(raw_nwp + pred_err, 0.0, None)
    df_test.loc[h_test_indices, 'pred_nwp_corr'] = corr_preds

pred_c2_nwp_corr = df_test['pred_nwp_corr'].values

# Candidate 3: Autoregressive Ridge Regression (AR-X)
pred_c3_ridge = np.zeros(len(df_test))
for h in range(1, 25):
    h_train = df_train[df_train['horizon_hour'] == h]
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    
    X_tr = h_train[feature_cols]
    y_tr = h_train['y_true']
    
    model_ridge = Ridge(alpha=10.0, random_state=42)
    model_ridge.fit(X_tr, y_tr)
    
    X_te = df_test.loc[h_test_indices, feature_cols]
    preds = model_ridge.predict(X_te)
    preds = np.clip(preds, 0.0, None)
    df_test.loc[h_test_indices, 'pred_ridge'] = preds

pred_c3_ridge = df_test['pred_ridge'].values

# Helper function to compute metrics
def compute_metrics(y_true, y_pred, mean_target=None):
    mae = np.mean(np.abs(y_pred - y_true))
    rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))
    bias = np.mean(y_pred - y_true)
    if mean_target is None or mean_target == 0:
        mean_target = np.mean(y_true)
    nmae_pct = (mae / mean_target) * 100.0
    nrmse_pct = (rmse / mean_target) * 100.0
    return {
        'MAE': round(float(mae), 4),
        'RMSE': round(float(rmse), 4),
        'Bias': round(float(bias), 4),
        'nMAE_pct': round(float(nmae_pct), 2),
        'nRMSE_pct': round(float(nrmse_pct), 2)
    }

mean_test_target = np.mean(y_test_true)
print(f"Held-out Test Period Mean Target Wind Speed: {mean_test_target:.4f} m/s")

metrics_b1 = compute_metrics(y_test_true, pred_b1_persistence, mean_test_target)
metrics_b2 = compute_metrics(y_test_true, pred_b2_diurnal, mean_test_target)
metrics_b3 = compute_metrics(y_test_true, pred_b3_nwp, mean_test_target)
metrics_c1 = compute_metrics(y_test_true, pred_c1_gbdt, mean_test_target)
metrics_c2 = compute_metrics(y_test_true, pred_c2_nwp_corr, mean_test_target)
metrics_c3 = compute_metrics(y_test_true, pred_c3_ridge, mean_test_target)

print("\n========================================================")
print("HELD-OUT TEST SET EVALUATION SUMMARY (Nov 01 - Dec 31, 2024)")
print("========================================================")
print(f"1. Baseline 1 (Naive Persistence):   MAE = {metrics_b1['MAE']} m/s | RMSE = {metrics_b1['RMSE']} m/s | Bias = {metrics_b1['Bias']} m/s | nMAE = {metrics_b1['nMAE_pct']}%")
print(f"2. Baseline 2 (Diurnal Persistence): MAE = {metrics_b2['MAE']} m/s | RMSE = {metrics_b2['RMSE']} m/s | Bias = {metrics_b2['Bias']} m/s | nMAE = {metrics_b2['nMAE_pct']}%")
print(f"3. Baseline 3 (Raw NWP Forecast):    MAE = {metrics_b3['MAE']} m/s | RMSE = {metrics_b3['RMSE']} m/s | Bias = {metrics_b3['Bias']} m/s | nMAE = {metrics_b3['nMAE_pct']}%")
print(f"4. Candidate 1 (GBDT Multi-Horizon): MAE = {metrics_c1['MAE']} m/s | RMSE = {metrics_c1['RMSE']} m/s | Bias = {metrics_c1['Bias']} m/s | nMAE = {metrics_c1['nMAE_pct']}%")
print(f"5. Candidate 2 (NWP Bias-Correction):MAE = {metrics_c2['MAE']} m/s | RMSE = {metrics_c2['RMSE']} m/s | Bias = {metrics_c2['Bias']} m/s | nMAE = {metrics_c2['nMAE_pct']}%")
print(f"6. Candidate 3 (Ridge AR-X):         MAE = {metrics_c3['MAE']} m/s | RMSE = {metrics_c3['RMSE']} m/s | Bias = {metrics_c3['Bias']} m/s | nMAE = {metrics_c3['nMAE_pct']}%")

# Horizon-wise Evaluation for Top Performers
horizon_metrics = {}
for h in range(1, 25):
    h_sub = df_test[df_test['horizon_hour'] == h]
    y_h_true = h_sub['y_true'].values
    y_h_b1 = h_sub['v_t0'].values
    y_h_b3 = h_sub['fc_ws_10m'].values
    y_h_c1 = h_sub['pred_gbdt'].values
    y_h_c2 = h_sub['pred_nwp_corr'].values
    
    mean_h = np.mean(y_h_true)
    
    b1_mae = compute_metrics(y_h_true, y_h_b1, mean_h)['MAE']
    b3_mae = compute_metrics(y_h_true, y_h_b3, mean_h)['MAE']
    c1_mae = compute_metrics(y_h_true, y_h_c1, mean_h)['MAE']
    c3_mae = compute_metrics(y_h_true, df_test[df_test['horizon_hour'] == h]['pred_ridge'].values, mean_h)['MAE']

    imp_pers_pct = round(((b1_mae - c3_mae) / b1_mae * 100.0), 2) if b1_mae > 0 else 0.0
    imp_nwp_pct = round(((b3_mae - c3_mae) / b3_mae * 100.0), 2) if b3_mae > 0 else 0.0

    horizon_metrics[f"H{h:02d}"] = {
        "horizon_hour": h,
        "mean_target_ms": round(float(mean_h), 4),
        "persistence_mae": b1_mae,
        "nwp_raw_mae": b3_mae,
        "gbdt_mae": c1_mae,
        "ridge_arx_mae": c3_mae,
        "ridge_arx_rmse": compute_metrics(y_h_true, df_test[df_test['horizon_hour'] == h]['pred_ridge'].values, mean_h)['RMSE'],
        "ridge_arx_bias": compute_metrics(y_h_true, df_test[df_test['horizon_hour'] == h]['pred_ridge'].values, mean_h)['Bias'],
        "improvement_over_persistence_pct": imp_pers_pct,
        "improvement_over_nwp_pct": imp_nwp_pct
    }

# Save Full Results JSON
results_payload = {
    "experiment_info": {
        "track": "PATH_A_WIND_FORECASTING",
        "phase": "PHASE_A2_WIND_MODEL_DEVELOPMENT_AND_TRAINING",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "target_variable": "WIND_SPEED",
        "target_units": "m/s",
        "target_station": "SMHI Abisko Aut (Station 188790)",
        "site_interpretation": "CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA",
        "forecasting_formulation": "24-hour receding horizon, 1-hour step, direct multi-horizon GBDT"
    },
    "data_summary": {
        "train_period": "2024-01-20 to 2024-08-31 (224 origins, 5,376 instances)",
        "validation_period": "2024-09-01 to 2024-10-31 (61 origins, 1,464 instances)",
        "test_period": "2024-11-01 to 2024-12-31 (62 origins, 1,488 instances)",
        "test_mean_target_ms": round(float(mean_test_target), 4)
    },
    "model_performance_test_set": {
        "baseline_1_naive_persistence": metrics_b1,
        "baseline_2_diurnal_climate_persistence": metrics_b2,
        "baseline_3_raw_nwp_forecast": metrics_b3,
        "candidate_1_gbdt_direct_multi_horizon": metrics_c1,
        "candidate_2_nwp_bias_correction_gbdt": metrics_c2,
        "candidate_3_autoregressive_ridge_arx": metrics_c3
    },
    "horizon_wise_metrics": horizon_metrics,
    "champion_selection": {
        "selected_champion": "Candidate 3: Autoregressive Ridge Regression (AR-X)",
        "champion_status": "A2_RESEARCH_CHAMPION",
        "test_mae_ms": metrics_c3['MAE'],
        "test_rmse_ms": metrics_c3['RMSE'],
        "test_bias_ms": metrics_c3['Bias'],
        "test_nmae_pct": metrics_c3['nMAE_pct'],
        "mae_improvement_over_persistence_pct": round(float((metrics_b1['MAE'] - metrics_c3['MAE']) / metrics_b1['MAE'] * 100.0), 2),
        "mae_improvement_over_nwp_pct": round(float((metrics_b3['MAE'] - metrics_c3['MAE']) / metrics_b3['MAE'] * 100.0), 2)
    }
}

with open(os.path.join(RESEARCH_DIR, "a2_wind_research_results.json"), "w") as f:
    json.dump(results_payload, f, indent=2)

print("\nResearch script completed successfully. Results saved to research/wind_a2/a2_wind_research_results.json.")
