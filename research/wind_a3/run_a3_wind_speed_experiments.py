"""
POLARIS Path A — Phase A3 Wind Speed Forecasting Research Execution Script
Deterministic execution of authorized EXP-01 through EXP-05 research protocol.
"""
import os
import json
import math
import re
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.preprocessing import StandardScaler

# Directories
WORKSPACE_DIR = "/home/punith-bs/01polaris (Copy)"
A2_DIR = os.path.join(WORKSPACE_DIR, "research", "wind_a2")
A3_DIR = os.path.join(WORKSPACE_DIR, "research", "wind_a3")
os.makedirs(A3_DIR, exist_ok=True)

# File Paths
WIND_SPEED_FILE = os.path.join(A2_DIR, "smhi_188790_ws_full.csv")
WIND_DIR_FILE = os.path.join(A2_DIR, "smhi_188790_wd_full.csv")
NWP_FORECAST_FILE = os.path.join(WORKSPACE_DIR, "data", "POLARIS_v0_1_future_weather_forecasts_2024.csv")
SITES_MET_FILE = os.path.join(WORKSPACE_DIR, "data", "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv")

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
df_ws = parse_smhi_csv(WIND_SPEED_FILE).rename(columns={'val': 'ws_10m'})
df_wd = parse_smhi_csv(WIND_DIR_FILE).rename(columns={'val': 'wd_10m'})

# Merge Target Data
df_target = pd.merge(df_ws[['dt', 'ws_10m', 'quality']], df_wd[['dt', 'wd_10m']], on='dt', how='left')
print(f"Target dataset parsed: {len(df_target)} hourly rows for 2024.")

# Load NWP Forecast Table
print("2. Loading NWP Forecasts and SITES Meteorological Predictors...")
df_nwp = pd.read_csv(NWP_FORECAST_FILE)
df_nwp['forecast_start_dt'] = pd.to_datetime(df_nwp['forecast_start'], utc=True)
df_nwp['timestamp_dt'] = pd.to_datetime(df_nwp['timestamp'], utc=True)

# Load SITES Met Predictors
df_sites = pd.read_csv(SITES_MET_FILE)
df_sites['dt'] = pd.to_datetime(df_sites['TIMESTAMP'], utc=True)

# Build Lookups
target_lookup = dict(zip(df_target['dt'], df_target['ws_10m']))
wd_lookup = dict(zip(df_target['dt'], df_target['wd_10m']))
sites_ta_lookup = dict(zip(df_sites['dt'], df_sites['TA']))
sites_rh_lookup = dict(zip(df_sites['dt'], df_sites['RH']))

unique_origins = sorted(df_nwp['forecast_start_dt'].unique())

print("3. Building Causal Feature Matrix...")
dataset_rows = []

for origin_idx, origin_dt in enumerate(unique_origins):
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
    
    ta_t0 = sites_ta_lookup.get(origin_dt, 0.0)
    rh_t0 = sites_rh_lookup.get(origin_dt, 75.0)
    
    nwp_sub = df_nwp[df_nwp['forecast_start_dt'] == origin_dt].sort_values('horizon_hour')
    if len(nwp_sub) != 24:
        continue
        
    for h_step in range(1, 25):
        nwp_row = nwp_sub[nwp_sub['horizon_hour'] == h_step].iloc[0]
        step_dt = nwp_row['timestamp_dt']
        y_true = target_lookup.get(step_dt, np.nan)
        if np.isnan(y_true):
            continue
            
        fc_ws_10m = nwp_row['fc_wind_speed_10m']
        fc_press = nwp_row['fc_surface_pressure']
        fc_temp = nwp_row['fc_temperature_2m']
        fc_rh = nwp_row['fc_relative_humidity_2m']
        fc_cloud = nwp_row['fc_cloud_cover']
        fc_precip = nwp_row['fc_precipitation']
        
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
print(f"Dataset matrix constructed: {len(df_feat)} total instance rows ({len(df_feat)/24:.0f} origins).")

# Splits
train_mask = df_feat['origin_idx'] <= 223
val_mask = (df_feat['origin_idx'] > 223) & (df_feat['origin_idx'] <= 284)
test_mask = df_feat['origin_idx'] > 284

df_train = df_feat[train_mask].copy()
df_val = df_feat[val_mask].copy()
df_test = df_feat[test_mask].copy()

print(f"Train set: {len(df_train)} rows ({len(df_train)/24:.0f} origins)")
print(f"Val set:   {len(df_val)} rows ({len(df_val)/24:.0f} origins)")
print(f"Test set:  {len(df_test)} rows ({len(df_test)/24:.0f} origins)")

feature_cols = [
    'v_t0', 'v_t1', 'v_t2', 'v_t3', 'v_t6', 'v_t12', 'v_t23',
    'v_mean_24h', 'v_std_24h', 'v_min_24h', 'v_max_24h', 'v_trend_6h',
    'wd_sin_t0', 'wd_cos_t0', 'ta_t0', 'rh_t0',
    'fc_ws_10m', 'fc_press', 'fc_temp', 'fc_rh', 'fc_cloud', 'fc_precip',
    'hour', 'sin_doy', 'cos_doy'
]

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

mean_val_target = np.mean(df_val['y_true'].values)
mean_test_target = np.mean(df_test['y_true'].values)

# ============================================================
# EXECUTION MATRIX: EXP-01 THROUGH EXP-05
# ============================================================
print("\n4. Executing Authorized Experiments (EXP-01 to EXP-05)...")

# --- EXP-01: Reference Baselines (3 runs) ---
# EXP-01.1: Naive Persistence
pred_exp01_1_val = df_val['v_t0'].values
pred_exp01_1_test = df_test['v_t0'].values
met_exp01_1_val = compute_metrics(df_val['y_true'].values, pred_exp01_1_val, mean_val_target)
met_exp01_1_test = compute_metrics(df_test['y_true'].values, pred_exp01_1_test, mean_test_target)

# EXP-01.2: Diurnal Climate Persistence
diurnal_means = df_train.groupby('hour')['y_true'].mean().to_dict()
pred_exp01_2_val = df_val['hour'].map(diurnal_means).values
pred_exp01_2_test = df_test['hour'].map(diurnal_means).values
met_exp01_2_val = compute_metrics(df_val['y_true'].values, pred_exp01_2_val, mean_val_target)
met_exp01_2_test = compute_metrics(df_test['y_true'].values, pred_exp01_2_test, mean_test_target)

# EXP-01.3: Raw NWP Forecast
pred_exp01_3_val = df_val['fc_ws_10m'].values
pred_exp01_3_test = df_test['fc_ws_10m'].values
met_exp01_3_val = compute_metrics(df_val['y_true'].values, pred_exp01_3_val, mean_val_target)
met_exp01_3_test = compute_metrics(df_test['y_true'].values, pred_exp01_3_test, mean_test_target)

# --- EXP-02: Frozen A2 AR-X Comparator (1 run) ---
# Ridge(alpha=10.0) evaluated on Test set
pred_exp02_test = np.zeros(len(df_test))
for h in range(1, 25):
    h_train = df_train[df_train['horizon_hour'] == h]
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    
    X_tr = h_train[feature_cols]
    y_tr = h_train['y_true']
    
    model_arx = Ridge(alpha=10.0, random_state=42)
    model_arx.fit(X_tr, y_tr)
    
    X_te = df_test.loc[h_test_indices, feature_cols]
    preds = np.clip(model_arx.predict(X_te), 0.0, None)
    df_test.loc[h_test_indices, 'pred_arx'] = preds

pred_exp02_test = df_test['pred_arx'].values
met_exp02_test = compute_metrics(df_test['y_true'].values, pred_exp02_test, mean_test_target)

# --- EXP-03: GBDT Direct Multi-Horizon (4 hyperparameter runs) ---
gbdt_configs = [
    {'lr': 0.05, 'depth': 5, 'leaf': 15, 'iter': 100},  # Config 1
    {'lr': 0.03, 'depth': 4, 'leaf': 20, 'iter': 100},  # Config 2
    {'lr': 0.08, 'depth': 6, 'leaf': 10, 'iter': 120},  # Config 3
    {'lr': 0.05, 'depth': 3, 'leaf': 25, 'iter': 80}    # Config 4
]

exp03_val_metrics = []
exp03_models = {}

for c_idx, cfg in enumerate(gbdt_configs):
    df_val_temp = df_val.copy()
    models_h = {}
    for h in range(1, 25):
        h_train = df_train[df_train['horizon_hour'] == h]
        h_val_indices = df_val_temp[df_val_temp['horizon_hour'] == h].index
        
        X_tr = h_train[feature_cols]
        y_tr = h_train['y_true']
        
        m = HistGradientBoostingRegressor(
            max_iter=cfg['iter'],
            learning_rate=cfg['lr'],
            max_depth=cfg['depth'],
            min_samples_leaf=cfg['leaf'],
            random_state=42
        )
        m.fit(X_tr, y_tr)
        models_h[h] = m
        
        X_va = df_val_temp.loc[h_val_indices, feature_cols]
        df_val_temp.loc[h_val_indices, 'pred'] = np.clip(m.predict(X_va), 0.0, None)
        
    val_met = compute_metrics(df_val_temp['y_true'].values, df_val_temp['pred'].values, mean_val_target)
    exp03_val_metrics.append((c_idx, cfg, val_met))
    exp03_models[c_idx] = models_h
    print(f"EXP-03 Config {c_idx+1}: Val MAE = {val_met['MAE']} m/s")

# Select best EXP-03 config on Validation set
best_exp03_idx = sorted(exp03_val_metrics, key=lambda x: x[2]['MAE'])[0][0]
best_exp03_cfg = gbdt_configs[best_exp03_idx]
best_exp03_models = exp03_models[best_exp03_idx]

# Evaluate best EXP-03 model on Test set
for h in range(1, 25):
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    X_te = df_test.loc[h_test_indices, feature_cols]
    df_test.loc[h_test_indices, 'pred_exp03'] = np.clip(best_exp03_models[h].predict(X_te), 0.0, None)

met_exp03_test = compute_metrics(df_test['y_true'].values, df_test['pred_exp03'].values, mean_test_target)

# --- EXP-04: NWP Residual GBDT (4 hyperparameter runs) ---
df_train['nwp_error'] = df_train['y_true'] - df_train['fc_ws_10m']

residual_configs = [
    {'lr': 0.03, 'depth': 4, 'leaf': 20, 'iter': 80},   # Config 1
    {'lr': 0.05, 'depth': 5, 'leaf': 15, 'iter': 100},  # Config 2
    {'lr': 0.02, 'depth': 3, 'leaf': 25, 'iter': 100},  # Config 3
    {'lr': 0.05, 'depth': 3, 'leaf': 30, 'iter': 60}    # Config 4
]

exp04_val_metrics = []
exp04_models = {}

for c_idx, cfg in enumerate(residual_configs):
    df_val_temp = df_val.copy()
    models_h = {}
    for h in range(1, 25):
        h_train = df_train[df_train['horizon_hour'] == h]
        h_val_indices = df_val_temp[df_val_temp['horizon_hour'] == h].index
        
        X_tr = h_train[feature_cols]
        y_err_tr = h_train['nwp_error']
        
        m_err = HistGradientBoostingRegressor(
            max_iter=cfg['iter'],
            learning_rate=cfg['lr'],
            max_depth=cfg['depth'],
            min_samples_leaf=cfg['leaf'],
            random_state=42
        )
        m_err.fit(X_tr, y_err_tr)
        models_h[h] = m_err
        
        X_va = df_val_temp.loc[h_val_indices, feature_cols]
        pred_err = m_err.predict(X_va)
        raw_nwp_val = df_val_temp.loc[h_val_indices, 'fc_ws_10m'].values
        df_val_temp.loc[h_val_indices, 'pred'] = np.clip(raw_nwp_val + pred_err, 0.0, None)
        
    val_met = compute_metrics(df_val_temp['y_true'].values, df_val_temp['pred'].values, mean_val_target)
    exp04_val_metrics.append((c_idx, cfg, val_met))
    exp04_models[c_idx] = models_h
    print(f"EXP-04 Config {c_idx+1}: Val MAE = {val_met['MAE']} m/s")

# Select best EXP-04 config on Validation set
best_exp04_idx = sorted(exp04_val_metrics, key=lambda x: x[2]['MAE'])[0][0]
best_exp04_cfg = residual_configs[best_exp04_idx]
best_exp04_models = exp04_models[best_exp04_idx]

# Evaluate best EXP-04 model on Test set
for h in range(1, 25):
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    X_te = df_test.loc[h_test_indices, feature_cols]
    pred_err = best_exp04_models[h].predict(X_te)
    raw_nwp_te = df_test.loc[h_test_indices, 'fc_ws_10m'].values
    df_test.loc[h_test_indices, 'pred_exp04'] = np.clip(raw_nwp_te + pred_err, 0.0, None)

met_exp04_test = compute_metrics(df_test['y_true'].values, df_test['pred_exp04'].values, mean_test_target)

# --- EXP-05: AR-ElasticNet Regularized Model (4 hyperparameter runs) ---
elasticnet_configs = [
    {'alpha': 0.1, 'l1_ratio': 0.5},  # Config 1
    {'alpha': 1.0, 'l1_ratio': 0.5},  # Config 2
    {'alpha': 0.1, 'l1_ratio': 0.1},  # Config 3
    {'alpha': 1.0, 'l1_ratio': 0.1}   # Config 4
]

exp05_val_metrics = []
exp05_models = {}
exp05_scalers = {}

for c_idx, cfg in enumerate(elasticnet_configs):
    df_val_temp = df_val.copy()
    models_h = {}
    scalers_h = {}
    for h in range(1, 25):
        h_train = df_train[df_train['horizon_hour'] == h]
        h_val_indices = df_val_temp[df_val_temp['horizon_hour'] == h].index
        
        X_tr = h_train[feature_cols].values
        y_tr = h_train['y_true'].values
        
        scaler = StandardScaler()
        X_tr_scaled = scaler.fit_transform(X_tr)
        scalers_h[h] = scaler
        
        m_en = ElasticNet(alpha=cfg['alpha'], l1_ratio=cfg['l1_ratio'], random_state=42, max_iter=2000)
        m_en.fit(X_tr_scaled, y_tr)
        models_h[h] = m_en
        
        X_va = df_val_temp.loc[h_val_indices, feature_cols].values
        X_va_scaled = scaler.transform(X_va)
        df_val_temp.loc[h_val_indices, 'pred'] = np.clip(m_en.predict(X_va_scaled), 0.0, None)
        
    val_met = compute_metrics(df_val_temp['y_true'].values, df_val_temp['pred'].values, mean_val_target)
    exp05_val_metrics.append((c_idx, cfg, val_met))
    exp05_models[c_idx] = models_h
    exp05_scalers[c_idx] = scalers_h
    print(f"EXP-05 Config {c_idx+1}: Val MAE = {val_met['MAE']} m/s")

# Select best EXP-05 config on Validation set
best_exp05_idx = sorted(exp05_val_metrics, key=lambda x: x[2]['MAE'])[0][0]
best_exp05_cfg = elasticnet_configs[best_exp05_idx]
best_exp05_models = exp05_models[best_exp05_idx]
best_exp05_scalers = exp05_scalers[best_exp05_idx]

# Evaluate best EXP-05 model on Test set
for h in range(1, 25):
    h_test_indices = df_test[df_test['horizon_hour'] == h].index
    X_te = df_test.loc[h_test_indices, feature_cols].values
    X_te_scaled = best_exp05_scalers[h].transform(X_te)
    df_test.loc[h_test_indices, 'pred_exp05'] = np.clip(best_exp05_models[h].predict(X_te_scaled), 0.0, None)

met_exp05_test = compute_metrics(df_test['y_true'].values, df_test['pred_exp05'].values, mean_test_target)

# Print Final Summary
print("\n" + "=" * 70)
print("PHASE A3 HELD-OUT TEST SET EVALUATION SUMMARY (Nov 01 - Dec 31, 2024)")
print("=" * 70)
print(f"1. Naive Persistence (EXP-01.1):   MAE = {met_exp01_1_test['MAE']} m/s | RMSE = {met_exp01_1_test['RMSE']} m/s | Bias = {met_exp01_1_test['Bias']} m/s | nMAE = {met_exp01_1_test['nMAE_pct']}%")
print(f"2. Diurnal Persistence (EXP-01.2): MAE = {met_exp01_2_test['MAE']} m/s | RMSE = {met_exp01_2_test['RMSE']} m/s | Bias = {met_exp01_2_test['Bias']} m/s | nMAE = {met_exp01_2_test['nMAE_pct']}%")
print(f"3. Raw NWP Forecast (EXP-01.3):    MAE = {met_exp01_3_test['MAE']} m/s | RMSE = {met_exp01_3_test['RMSE']} m/s | Bias = {met_exp01_3_test['Bias']} m/s | nMAE = {met_exp01_3_test['nMAE_pct']}%")
print(f"4. Frozen A2 AR-X (EXP-02):        MAE = {met_exp02_test['MAE']} m/s | RMSE = {met_exp02_test['RMSE']} m/s | Bias = {met_exp02_test['Bias']} m/s | nMAE = {met_exp02_test['nMAE_pct']}%")
print(f"5. Direct GBDT (EXP-03 Best C1):   MAE = {met_exp03_test['MAE']} m/s | RMSE = {met_exp03_test['RMSE']} m/s | Bias = {met_exp03_test['Bias']} m/s | nMAE = {met_exp03_test['nMAE_pct']}%")
print(f"6. NWP Residual GBDT (EXP-04 C1):  MAE = {met_exp04_test['MAE']} m/s | RMSE = {met_exp04_test['RMSE']} m/s | Bias = {met_exp04_test['Bias']} m/s | nMAE = {met_exp04_test['nMAE_pct']}%")
print(f"7. AR-ElasticNet (EXP-05 Best C3): MAE = {met_exp05_test['MAE']} m/s | RMSE = {met_exp05_test['RMSE']} m/s | Bias = {met_exp05_test['Bias']} m/s | nMAE = {met_exp05_test['nMAE_pct']}%")

# Horizon-wise Metrics Breakdown for Frozen AR-X and Top New Candidates
horizon_metrics = {}
for h in range(1, 25):
    h_sub = df_test[df_test['horizon_hour'] == h]
    y_h_true = h_sub['y_true'].values
    y_h_b1 = h_sub['v_t0'].values
    y_h_b3 = h_sub['fc_ws_10m'].values
    y_h_arx = h_sub['pred_arx'].values
    y_h_exp03 = h_sub['pred_exp03'].values
    y_h_exp05 = h_sub['pred_exp05'].values
    
    mean_h = np.mean(y_h_true)
    
    b1_m = compute_metrics(y_h_true, y_h_b1, mean_h)['MAE']
    b3_m = compute_metrics(y_h_true, y_h_b3, mean_h)['MAE']
    arx_m = compute_metrics(y_h_true, y_h_arx, mean_h)['MAE']
    exp03_m = compute_metrics(y_h_true, y_h_exp03, mean_h)['MAE']
    exp05_m = compute_metrics(y_h_true, y_h_exp05, mean_h)['MAE']
    
    horizon_metrics[f"H{h:02d}"] = {
        "horizon_hour": h,
        "mean_target_ms": round(float(mean_h), 4),
        "persistence_mae": b1_m,
        "nwp_raw_mae": b3_m,
        "arx_comparator_mae": arx_m,
        "exp03_gbdt_mae": exp03_m,
        "exp05_elasticnet_mae": exp05_m,
        "arx_rmse": compute_metrics(y_h_true, y_h_arx, mean_h)['RMSE'],
        "arx_bias": compute_metrics(y_h_true, y_h_arx, mean_h)['Bias']
    }

# Champion Selection Check per Pre-registered Rule
# Benchmark Bar: Frozen AR-X MAE = 2.0364 m/s. Required 2.0% improvement: MAE < 1.9957 m/s.
best_candidate_mae = min(met_exp03_test['MAE'], met_exp04_test['MAE'], met_exp05_test['MAE'])
if best_candidate_mae < 1.9957:
    if best_candidate_mae == met_exp05_test['MAE']:
        champion_name = "Candidate 3: AR-ElasticNet Regularized Model"
    elif best_candidate_mae == met_exp03_test['MAE']:
        champion_name = "Candidate 1: Direct Multi-Horizon GBDT"
    else:
        champion_name = "Candidate 2: NWP Residual Bias-Correction GBDT"
    champion_status = "AUTHORITATIVE_WIND_FORECASTING_CHAMPION"
else:
    champion_name = "Autoregressive Ridge AR-X (Frozen A2 Comparator)"
    champion_status = "A2_RESEARCH_CHAMPION_RETAINED"

print(f"\nFinal Research Selection Decision: {champion_name} ({champion_status})")

# Save Results JSON
results_payload = {
    "experiment_info": {
        "track": "PATH_A_WIND_FORECASTING",
        "phase": "PHASE_A3_WIND_MODEL_DEVELOPMENT_EXECUTION",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "target_variable": "WIND_SPEED",
        "target_units": "m/s",
        "target_station": "SMHI Abisko Aut (Station 188790)",
        "site_interpretation": "CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA",
        "total_executed_runs": 16,
        "global_run_ceiling": 16
    },
    "executed_experiments": {
        "EXP-01": {"name": "Reference Baselines", "runs": 3, "test_metrics": {"persistence": met_exp01_1_test, "diurnal": met_exp01_2_test, "raw_nwp": met_exp01_3_test}},
        "EXP-02": {"name": "Frozen A2 AR-X Comparator", "runs": 1, "test_metrics": met_exp02_test},
        "EXP-03": {"name": "GBDT Direct Multi-Horizon", "runs": 4, "best_config": best_exp03_cfg, "test_metrics": met_exp03_test},
        "EXP-04": {"name": "NWP Residual Bias-Correction GBDT", "runs": 4, "best_config": best_exp04_cfg, "test_metrics": met_exp04_test},
        "EXP-05": {"name": "AR-ElasticNet Regularized Model", "runs": 4, "best_config": best_exp05_cfg, "test_metrics": met_exp05_test}
    },
    "horizon_wise_metrics": horizon_metrics,
    "champion_selection": {
        "selected_champion": champion_name,
        "champion_status": champion_status,
        "frozen_arx_test_mae": met_exp02_test['MAE'],
        "best_new_candidate_test_mae": best_candidate_mae,
        "threshold_required_for_new_champion": 1.9957
    }
}

with open(os.path.join(A3_DIR, "a3_wind_research_results.json"), "w") as f:
    json.dump(results_payload, f, indent=2)

print(f"Phase A3 execution completed successfully. Results saved to research/wind_a3/a3_wind_research_results.json.")
