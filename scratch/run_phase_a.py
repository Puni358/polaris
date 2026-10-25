import os
import sys
import json
import math
from hashlib import sha256
from pathlib import Path
import numpy as np
import pandas as pd
import pvlib
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE7_5_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
WIND_FEAT_PATH = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind" / "stage8_1_extracted_features.csv"
FOLD_ASSIGNMENT_PATH = BASE_DIR / "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv"

ELIGIBLE_CSV_PATH = BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv"
OOF_PREDS_CSV_PATH = BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_OOF_PREDICTIONS.csv"
RESULTS_MD_PATH = BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.md"
RESULTS_JSON_PATH = BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.json"
T4_BLOCKER_MD_PATH = BASE_DIR / "forecasting/reports/candidates/T4_RECONSTRUCTION_BLOCKER.md"

def run_phase_a():
    print("==================================================")
    print("POLARIS — INFORMATION PROBE PHASE A EXECUTION")
    print("==================================================")
    sys.stdout.flush()
    
    df_folds = pd.read_csv(FOLD_ASSIGNMENT_PATH)
    df_folds["origin_timestamp"] = pd.to_datetime(df_folds["origin_timestamp"], utc=True)
    even_origins_sorted = sorted(df_folds["origin_timestamp"].unique())
    origin_to_fold = dict(zip(df_folds["origin_timestamp"], df_folds["canonical_fold"]))
    
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
    
    df_wind = pd.read_csv(WIND_FEAT_PATH)
    df_wind["forecast_start"] = pd.to_datetime(df_wind["forecast_start"], utc=True)
    df_wind["valid_time"] = pd.to_datetime(df_wind["valid_time"], utc=True)
    
    lat, lon, tz = 68.362074, 18.738752, "Etc/GMT-1"
    location = pvlib.location.Location(latitude=lat, longitude=lon, tz=tz, name="SITES Nuolja")
    times_localized = pd.DatetimeIndex(df_cs["timestamp"]).tz_convert(tz)
    solpos = location.get_solarposition(times_localized)
    df_cs["solar_azimuth"] = solpos["azimuth"].values
    
    df_main = s4_preds.merge(df_cs[["timestamp", "clearsky_ghi", "solar_elevation", "solar_azimuth"]], on="timestamp", how="left")
    
    eligible_list = []
    excluded_list = []
    target_dict = {}
    
    for orig_ts in even_origins_sorted:
        orig_df = df_main[df_main["forecast_start"] == orig_ts].sort_values("horizon_hour")
        h7_12 = orig_df[orig_df["horizon_hour"].isin([7, 8, 9, 10, 11, 12])].copy()
        
        valid_kt = []
        for idx, row in h7_12.iterrows():
            cs_ghi = row["clearsky_ghi"]
            sw_in = row["actual_SW_IN"]
            if cs_ghi >= 20.0:
                kt_val = np.clip(sw_in / cs_ghi, 0.0, 1.2)
                valid_kt.append(kt_val)
                
        n_valid = len(valid_kt)
        canonical_fold = origin_to_fold[orig_ts]
        
        if n_valid >= 5:
            t1_vol = float(np.std(valid_kt, ddof=0))
            diffs = [abs(valid_kt[i+1] - valid_kt[i]) for i in range(len(valid_kt)-1)]
            t2_trans = float(np.max(diffs)) if len(diffs) > 0 else 0.0
            t3_mean = float(np.mean(valid_kt))
            
            target_dict[orig_ts] = {
                "T1_volatility": t1_vol,
                "T2_max_transition": t2_trans,
                "T3_mean_kt": t3_mean,
                "valid_h_count": n_valid,
                "canonical_fold": canonical_fold,
                "month": orig_ts.month
            }
            eligible_list.append({
                "forecast_start": orig_ts.strftime("%Y-%m-%d %H:%M:%S%z"),
                "canonical_fold": canonical_fold,
                "valid_h_count": n_valid,
                "T1_volatility": t1_vol,
                "T2_max_transition": t2_trans,
                "T3_mean_kt": t3_mean
            })
        else:
            excluded_list.append({
                "forecast_start": orig_ts.strftime("%Y-%m-%d %H:%M:%S%z"),
                "canonical_fold": canonical_fold,
                "valid_h_count": n_valid,
                "exclusion_reason": "Polar night / low clear-sky GHI (< 5 valid hours in H7-H12)"
            })
            
    df_eligible = pd.DataFrame(eligible_list)
    df_eligible.to_csv(ELIGIBLE_CSV_PATH, index=False)
    
    n_eligible = len(df_eligible)
    print(f"Total EVEN origins: {len(even_origins_sorted)} | Eligible N: {n_eligible} | Excluded N: {len(excluded_list)}")
    sys.stdout.flush()
    
    eligible_origins_sorted = [orig for orig in even_origins_sorted if orig in target_dict]
    
    df_cs["date"] = df_cs["timestamp"].dt.date
    daylight_map = df_cs.groupby("date")["solar_elevation"].apply(lambda s: np.sum(s > 0)).to_dict()
    
    P0_rows = []
    for orig_ts in eligible_origins_sorted:
        orig_date = orig_ts.date()
        daylight_dur = daylight_map.get(orig_date, 0)
        doy = orig_ts.dayofyear
        doy_sin = math.sin(2 * math.pi * doy / 366.0)
        doy_cos = math.cos(2 * math.pi * doy / 366.0)
        
        orig_df = df_main[df_main["forecast_start"] == orig_ts].sort_values("horizon_hour")
        t0_row = orig_df[orig_df["horizon_hour"] == 1]
        solar_elev_t0 = t0_row["solar_elevation"].values[0] if len(t0_row) > 0 else 0.0
        
        h7_12 = orig_df[orig_df["horizon_hour"].isin([7, 8, 9, 10, 11, 12])].sort_values("horizon_hour")
        elev_h7_12 = h7_12["solar_elevation"].values
        az_h7_12 = h7_12["solar_azimuth"].values
        ghi_h7_12 = h7_12["clearsky_ghi"].values
        
        p0_feat = [solar_elev_t0] + list(elev_h7_12) + list(az_h7_12) + list(ghi_h7_12) + [doy_sin, doy_cos, daylight_dur]
        P0_rows.append(p0_feat)
        
    X_P0 = np.array(P0_rows)
    
    df_all = s4_preds.copy()
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df_all = df_all.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df_all["cloud_frac"] = df_all["fc_cloud_cover"] / 100.0
    
    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]
    df_all = df_all.merge(df_cs[cs_cols], on="timestamp", how="left")
    
    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df_all = df_all.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")
    df_all["lwp_x_cloud"] = df_all["lwp_latest"] * df_all["cloud_frac"]
    
    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    df_all = df_all.merge(df_75[terrain_cols], on="timestamp", how="left")
    
    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df_all = df_all.merge(df_wind[wind_cols], on=["forecast_start", "horizon_hour"], how="left")
    
    df_all["month"] = df_all["timestamp"].dt.month
    df_all["hour"] = df_all["timestamp"].dt.hour
    df_all["is_daytime"] = df_all["actual_SW_IN"] > 0
    df_all["is_night_causal"] = (df_all["solar_elevation"] <= 0.0) | (df_all["clearsky_ghi"] == 0.0)
    
    with open(STAGE4_PARAMS_PATH) as f:
        ensemble_params_full = json.load(f)
        
    phys_preds_full = []
    for idx, row in df_all.iterrows():
        h = str(int(row["horizon_hour"]))
        p = ensemble_params_full[h]
        k_h = p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        phys_preds_full.append(phys)
        
    df_all["phys_pred_fold"] = phys_preds_full
    df_all["pred_stage4_fold"] = df_all["pred_ensemble"]
    df_all["disagreement_fold"] = (df_all["pred_stage3b_cloud_nwp"] - df_all["phys_pred_fold"]).abs()
    
    ctx_feature_rows = []
    for orig_ts in even_origins_sorted:
        context_start = orig_ts - pd.Timedelta(hours=24)
        ctx_sites = df_sites[(df_sites["timestamp"] >= context_start) & (df_sites["timestamp"] < orig_ts)].sort_values("timestamp")
        
        if len(ctx_sites) < 24:
            ctx_feature_rows.append({
                "forecast_start": orig_ts,
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
        
        ctx_cs = df_cs[(df_cs["timestamp"] >= context_start) & (df_cs["timestamp"] < orig_ts)].sort_values("timestamp")
        if len(ctx_cs) == len(ctx_sites):
            cs_ghi_vals = ctx_cs["clearsky_ghi"].values
            valid_cs = cs_ghi_vals > 10.0
            kt_vals = np.zeros_like(sw_vals)
            kt_vals[valid_cs] = np.clip(sw_vals[valid_cs] / cs_ghi_vals[valid_cs], 0.0, 1.5)
            kt_std_6h = np.std(kt_vals[-6:]) if len(kt_vals) >= 6 else 0.0
        else:
            kt_std_6h = 0.0
            
        ctx_feature_rows.append({
            "forecast_start": orig_ts,
            "ctx_std_3h": std_3h, "ctx_std_6h": std_6h, "ctx_std_12h": std_12h, "ctx_std_24h": std_24h,
            "ctx_abs_change_1h": abs_chg_1h, "ctx_abs_change_3h": abs_chg_3h, "ctx_abs_change_6h": abs_chg_6h,
            "ctx_max_diff_6h": max_diff_6h, "ctx_mean_diff_6h": mean_diff_6h, "ctx_slope_6h": slope_6h,
            "ctx_kt_std_6h": kt_std_6h, "ctx_last_obs": sw_vals[-1],
            "ctx_mean_24h": np.mean(s24), "ctx_max_24h": np.max(s24)
        })
        
    ctx_df = pd.DataFrame(ctx_feature_rows)
    df_all = df_all.merge(ctx_df, on="forecast_start", how="left")
    
    origin_ctx_cols = [
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]
    
    horizon_22_cols = [
        "horizon_hour", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "lwp_latest", "iwp_latest", "lwp_x_cloud",
        "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
        "u700", "v700"
    ]
    
    P1_rows = []
    for orig_ts in eligible_origins_sorted:
        orig_sub = df_all[df_all["forecast_start"] == orig_ts].sort_values("horizon_hour")
        month_val = float(orig_ts.month)
        ctx_vals = [float(orig_sub[c].iloc[0]) for c in origin_ctx_cols]
        
        h7_12_sub = orig_sub[orig_sub["horizon_hour"].isin([7, 8, 9, 10, 11, 12])].sort_values("horizon_hour")
        h_vals = []
        for c in horizon_22_cols:
            h_vals.extend([float(x) for x in h7_12_sub[c].values])
            
        p1_feat = [month_val] + ctx_vals + h_vals
        P1_rows.append(p1_feat)
        
    X_P1 = np.array(P1_rows)
    
    folds_vec = np.array([target_dict[orig]["canonical_fold"] for orig in eligible_origins_sorted])
    months_vec = np.array([target_dict[orig]["month"] for orig in eligible_origins_sorted])
    
    targets = ["T1_volatility", "T2_max_transition", "T3_mean_kt"]
    models = ["ModelA_Ridge", "ModelB_GBDT"]
    
    oof_predictions = []
    results_summary = {}
    
    for t_name in targets:
        y_vec = np.array([target_dict[orig][t_name] for orig in eligible_origins_sorted])
        results_summary[t_name] = {}
        
        for m_name in models:
            print(f"--- Fitting {m_name} on {t_name} ---")
            sys.stdout.flush()
            
            pred_P0 = np.zeros(n_eligible)
            pred_P1 = np.zeros(n_eligible)
            
            for fold in range(1, 6):
                val_mask = (folds_vec == fold)
                tr_mask = ~val_mask
                
                X_tr_p0, y_tr = X_P0[tr_mask], y_vec[tr_mask]
                X_val_p0, y_val = X_P0[val_mask], y_vec[val_mask]
                
                X_tr_p1 = X_P1[tr_mask].copy()
                X_val_p1 = X_P1[val_mask].copy()
                
                p1_col_means = np.nanmean(X_tr_p1, axis=0)
                p1_col_means = np.nan_to_num(p1_col_means, nan=0.0)
                
                for c in range(X_tr_p1.shape[1]):
                    isnan_tr = np.isnan(X_tr_p1[:, c])
                    if np.any(isnan_tr):
                        X_tr_p1[isnan_tr, c] = p1_col_means[c]
                    isnan_val = np.isnan(X_val_p1[:, c])
                    if np.any(isnan_val):
                        X_val_p1[isnan_val, c] = p1_col_means[c]
                        
                if m_name == "ModelA_Ridge":
                    scaler_p0 = StandardScaler()
                    X_tr_p0_scaled = scaler_p0.fit_transform(X_tr_p0)
                    X_val_p0_scaled = scaler_p0.transform(X_val_p0)
                    reg_p0 = Ridge(alpha=1.0).fit(X_tr_p0_scaled, y_tr)
                    pred_P0[val_mask] = reg_p0.predict(X_val_p0_scaled)
                    
                    scaler_p1 = StandardScaler()
                    X_tr_p1_scaled = scaler_p1.fit_transform(X_tr_p1)
                    X_val_p1_scaled = scaler_p1.transform(X_val_p1)
                    reg_p1 = Ridge(alpha=1.0).fit(X_tr_p1_scaled, y_tr)
                    pred_P1[val_mask] = reg_p1.predict(X_val_p1_scaled)
                    
                elif m_name == "ModelB_GBDT":
                    gbdt_p0 = HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05, min_samples_leaf=10, random_state=42)
                    gbdt_p0.fit(X_tr_p0, y_tr)
                    pred_P0[val_mask] = gbdt_p0.predict(X_val_p0)
                    
                    gbdt_p1 = HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05, min_samples_leaf=10, random_state=42)
                    gbdt_p1.fit(X_tr_p1, y_tr)
                    pred_P1[val_mask] = gbdt_p1.predict(X_val_p1)
                    
            r2_P0 = float(r2_score(y_vec, pred_P0))
            r2_P1 = float(r2_score(y_vec, pred_P1))
            delta_r2 = float(r2_P1 - r2_P0)
            
            rho_P0 = float(spearmanr(y_vec, pred_P0).statistic)
            rho_P1 = float(spearmanr(y_vec, pred_P1).statistic)
            
            # 10,000 Paired Bootstrap
            np.random.seed(42)
            boot_deltas = []
            n_samples = len(y_vec)
            for _ in range(10000):
                boot_idx = np.random.choice(n_samples, size=n_samples, replace=True)
                y_boot = y_vec[boot_idx]
                p0_boot = pred_P0[boot_idx]
                p1_boot = pred_P1[boot_idx]
                
                ss_tot_b = np.sum((y_boot - np.mean(y_boot)) ** 2)
                if ss_tot_b == 0:
                    continue
                r2_p0_b = 1.0 - np.sum((y_boot - p0_boot)**2) / ss_tot_b
                r2_p1_b = 1.0 - np.sum((y_boot - p1_boot)**2) / ss_tot_b
                boot_deltas.append(r2_p1_b - r2_p0_b)
                
            ci_lo = float(np.percentile(boot_deltas, 2.5))
            ci_hi = float(np.percentile(boot_deltas, 97.5))
            
            n_perms = 1000 if m_name == "ModelA_Ridge" else 200
            print(f"Computing month-blocked permutation test ({n_perms} iterations) for {m_name} {t_name}...")
            sys.stdout.flush()
            
            perm_deltas = []
            for perm_i in range(n_perms):
                np.random.seed(42 + perm_i)
                y_perm = y_vec.copy()
                for m in np.unique(months_vec):
                    m_mask = (months_vec == m)
                    y_perm[m_mask] = np.random.permutation(y_perm[m_mask])
                    
                pred_p0_perm = np.zeros(n_eligible)
                pred_p1_perm = np.zeros(n_eligible)
                
                for fold in range(1, 6):
                    val_mask = (folds_vec == fold)
                    tr_mask = ~val_mask
                    y_tr_perm = y_perm[tr_mask]
                    
                    if m_name == "ModelA_Ridge":
                        scaler_p0 = StandardScaler()
                        X_tr_p0_scaled = scaler_p0.fit_transform(X_P0[tr_mask])
                        X_val_p0_scaled = scaler_p0.transform(X_P0[val_mask])
                        reg_p0 = Ridge(alpha=1.0).fit(X_tr_p0_scaled, y_tr_perm)
                        pred_p0_perm[val_mask] = reg_p0.predict(X_val_p0_scaled)
                        
                        X_tr_p1_imputed = X_P1[tr_mask].copy()
                        X_val_p1_imputed = X_P1[val_mask].copy()
                        p1_means = np.nanmean(X_tr_p1_imputed, axis=0)
                        p1_means = np.nan_to_num(p1_means, nan=0.0)
                        for c in range(X_tr_p1_imputed.shape[1]):
                            X_tr_p1_imputed[np.isnan(X_tr_p1_imputed[:, c]), c] = p1_means[c]
                            X_val_p1_imputed[np.isnan(X_val_p1_imputed[:, c]), c] = p1_means[c]
                            
                        scaler_p1 = StandardScaler()
                        X_tr_p1_scaled = scaler_p1.fit_transform(X_tr_p1_imputed)
                        X_val_p1_scaled = scaler_p1.transform(X_val_p1_imputed)
                        reg_p1 = Ridge(alpha=1.0).fit(X_tr_p1_scaled, y_tr_perm)
                        pred_p1_perm[val_mask] = reg_p1.predict(X_val_p1_scaled)
                        
                    elif m_name == "ModelB_GBDT":
                        gbdt_p0 = HistGradientBoostingRegressor(max_depth=3, max_iter=15, learning_rate=0.05, min_samples_leaf=10, random_state=42)
                        gbdt_p0.fit(X_P0[tr_mask], y_tr_perm)
                        pred_p0_perm[val_mask] = gbdt_p0.predict(X_P0[val_mask])
                        
                        X_tr_p1_imputed = X_P1[tr_mask].copy()
                        X_val_p1_imputed = X_P1[val_mask].copy()
                        p1_means = np.nanmean(X_tr_p1_imputed, axis=0)
                        p1_means = np.nan_to_num(p1_means, nan=0.0)
                        for c in range(X_tr_p1_imputed.shape[1]):
                            X_tr_p1_imputed[np.isnan(X_tr_p1_imputed[:, c]), c] = p1_means[c]
                            X_val_p1_imputed[np.isnan(X_val_p1_imputed[:, c]), c] = p1_means[c]
                            
                        gbdt_p1 = HistGradientBoostingRegressor(max_depth=3, max_iter=15, learning_rate=0.05, min_samples_leaf=10, random_state=42)
                        gbdt_p1.fit(X_tr_p1_imputed, y_tr_perm)
                        pred_p1_perm[val_mask] = gbdt_p1.predict(X_val_p1_imputed)
                        
                r2_p0_perm = r2_score(y_perm, pred_p0_perm)
                r2_p1_perm = r2_score(y_perm, pred_p1_perm)
                perm_deltas.append(r2_p1_perm - r2_p0_perm)
                
            p_value = float(np.mean(np.array(perm_deltas) >= delta_r2))
            
            results_summary[t_name][m_name] = {
                "P0_R2": round(r2_P0, 6),
                "P1_R2": round(r2_P1, 6),
                "delta_R2": round(delta_r2, 6),
                "P0_spearman_rho": round(rho_P0, 6),
                "P1_spearman_rho": round(rho_P1, 6),
                "bootstrap_95ci_lo": round(ci_lo, 6),
                "bootstrap_95ci_hi": round(ci_hi, 6),
                "bootstrap_ci_excludes_zero": bool(ci_lo > 0.0),
                "permutation_p_value": round(p_value, 6)
            }
            
            print(f"  {t_name} | {m_name}: P0_R2={r2_P0:.4f}, P1_R2={r2_P1:.4f}, ΔR2={delta_r2:.4f}, CI95=[{ci_lo:.4f}, {ci_hi:.4f}], p={p_value:.4f}")
            sys.stdout.flush()
            
            for idx_orig, orig_ts in enumerate(eligible_origins_sorted):
                oof_predictions.append({
                    "forecast_start": orig_ts.strftime("%Y-%m-%d %H:%M:%S%z"),
                    "canonical_fold": int(folds_vec[idx_orig]),
                    "target": t_name,
                    "actual_target": float(y_vec[idx_orig]),
                    "model": m_name,
                    "pred_P0": float(pred_P0[idx_orig]),
                    "pred_P1": float(pred_P1[idx_orig]),
                    "error_P0": float(y_vec[idx_orig] - pred_P0[idx_orig]),
                    "error_P1": float(y_vec[idx_orig] - pred_P1[idx_orig])
                })
                
    df_oof = pd.DataFrame(oof_predictions)
    df_oof.to_csv(OOF_PREDS_CSV_PATH, index=False)
    
    with open(OOF_PREDS_CSV_PATH, "rb") as f:
        oof_sha = sha256(f.read()).hexdigest()
        
    with open(ELIGIBLE_CSV_PATH, "rb") as f:
        elig_sha = sha256(f.read()).hexdigest()
        
    results_payload = {
        "experiment_name": "POLARIS_INFORMATION_PROBE_PHASE_A",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "total_even_origins": len(even_origins_sorted),
        "eligible_even_origins": n_eligible,
        "excluded_even_origins": len(excluded_list),
        "power_floor_passed": bool(n_eligible >= 60),
        "eligible_csv_sha256": elig_sha,
        "oof_predictions_csv_sha256": oof_sha,
        "t4_status": "DROPPED",
        "governance_rule": "Original formal hit criterion: 2-of-4 required (with T4 dropped, 2-of-4 cannot be met using T1-T3 alone). Results report T1-T3 diagnostically.",
        "results": results_summary
    }
    
    with open(RESULTS_JSON_PATH, "w") as f:
        json.dump(results_payload, f, indent=2)
        
    print("==================================================")
    print("PHASE A COMPUTATION COMPLETE!")
    print(f"Eligible CSV: {ELIGIBLE_CSV_PATH} (SHA256: {elig_sha})")
    print(f"OOF Preds CSV: {OOF_PREDS_CSV_PATH} (SHA256: {oof_sha})")
    print(f"Results JSON: {RESULTS_JSON_PATH}")
    print("==================================================")

if __name__ == "__main__":
    run_phase_a()
