import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

ODD_PREDS_PATH = STAGE_DIR / "stage8_1_official_odd_predictions.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
STAGE66_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"
STAGE75_PATH = BASE_DIR / "forecasting/stage7" / "stage7_5_terrain_horizon" / "nuolja_terrain_features_2024.csv"
STAGE81_FEAT_PATH = STAGE_DIR / "stage8_1_extracted_features.csv"
SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"

def load_data():
    df_preds = pd.read_csv(ODD_PREDS_PATH)
    df_preds["forecast_start"] = pd.to_datetime(df_preds["forecast_start"], utc=True)
    df_preds["timestamp"] = pd.to_datetime(df_preds["timestamp"], utc=True)

    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)
    df_nwp["timestamp"] = pd.to_datetime(df_nwp["timestamp"], utc=True)

    df_cs = pd.read_csv(CLEARSKY_PATH)
    df_cs["timestamp"] = pd.to_datetime(df_cs["TIMESTAMP"], utc=True)

    df_66 = pd.read_csv(STAGE66_PATH)
    df_66["forecast_start"] = pd.to_datetime(df_66["forecast_start"], utc=True)

    df_75 = pd.read_csv(STAGE75_PATH)
    df_75["timestamp"] = pd.to_datetime(df_75["TIMESTAMP"], utc=True)

    df_81 = pd.read_csv(STAGE81_FEAT_PATH)
    df_81["forecast_start"] = pd.to_datetime(df_81["forecast_start"], utc=True)

    df_sites = pd.read_csv(SITES_PATH)
    df_sites["timestamp"] = pd.to_datetime(df_sites["TIMESTAMP"], utc=True)

    # Merge
    df = df_preds.copy()
    
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(df_nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0

    cs_cols = ["timestamp", "clearsky_ghi", "solar_elevation", "solar_zenith"]
    cs_cols_present = [c for c in cs_cols if c in df_cs.columns]
    df = df.merge(df_cs[cs_cols_present], on="timestamp", how="left")

    stage66_cols = ["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]
    df = df.merge(df_66[stage66_cols], on=["forecast_start", "horizon_hour"], how="left")

    terrain_cols = ["timestamp", "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted"]
    terrain_cols_present = [c for c in terrain_cols if c in df_75.columns]
    df = df.merge(df_75[terrain_cols_present], on="timestamp", how="left")

    wind_cols = ["forecast_start", "horizon_hour", "u700", "v700"]
    df = df.merge(df_81[wind_cols], on=["forecast_start", "horizon_hour"], how="left")

    df["pred"] = df["pred_stage8_1_candidate"]
    df["actual"] = df["actual_SW_IN"]
    df["residual"] = df["pred"] - df["actual"]
    df["abs_error"] = df["residual"].abs()
    df["sq_error"] = df["residual"] ** 2

    # Wind calculations
    df["wind_speed_700"] = np.sqrt(df["u700"]**2 + df["v700"]**2)
    wind_dir_rad = np.arctan2(-df["u700"], -df["v700"])
    df["wind_dir_700"] = (np.degrees(wind_dir_rad) + 360.0) % 360.0

    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    
    def get_season(m):
        if m in [12, 1, 2]: return "Winter"
        elif m in [3, 4, 5]: return "Spring"
        elif m in [6, 7, 8]: return "Summer"
        else: return "Autumn"
    df["season"] = df["month"].apply(get_season)

    return df, df_sites

def compute_forensics():
    df, df_sites = load_data()
    daytime_df = df[df["is_daytime"]].copy().sort_values("timestamp")
    total_abs_error = daytime_df["abs_error"].sum()
    mean_actual_daytime = daytime_df["actual"].mean()
    n_daytime = len(daytime_df)

    results = {}

    # Section 1 & 3: Champions Verification
    results["verification"] = {
        "odd_origins": int(df["forecast_start"].nunique()),
        "forecast_hours_total": int(len(df)),
        "daytime_hours": n_daytime,
        "night_hours": int((~df["is_daytime"]).sum()),
        "daytime_mae": float(daytime_df["abs_error"].mean()),
        "daytime_nmae_pct": float((daytime_df["abs_error"].mean() / mean_actual_daytime) * 100.0),
        "daytime_rmse": float(np.sqrt(daytime_df["sq_error"].mean())),
        "daytime_bias": float(daytime_df["residual"].mean()),
        "night_mae": float(df[~df["is_daytime"]]["abs_error"].mean()),
        "mean_actual_daytime": float(mean_actual_daytime)
    }

    # Section 5: Basic Error Distribution
    abs_errs = daytime_df["abs_error"].values
    residuals = daytime_df["residual"].values

    results["basic_error_distribution"] = {
        "mae": float(np.mean(abs_errs)),
        "rmse": float(np.sqrt(np.mean(residuals**2))),
        "bias": float(np.mean(residuals)),
        "median_abs_error": float(np.median(abs_errs)),
        "p75_abs_error": float(np.percentile(abs_errs, 75)),
        "p90_abs_error": float(np.percentile(abs_errs, 90)),
        "p95_abs_error": float(np.percentile(abs_errs, 95)),
        "p99_abs_error": float(np.percentile(abs_errs, 99)),
        "max_abs_error": float(np.max(abs_errs)),
        "signed_residual_mean": float(np.mean(residuals)),
        "signed_residual_median": float(np.median(residuals)),
        "signed_residual_std": float(np.std(residuals)),
        "signed_residual_skewness": float(stats.skew(residuals)),
        "error_concentration": {
            "top_1pct_fraction": float(np.sort(abs_errs)[-int(n_daytime*0.01):].sum() / total_abs_error),
            "top_5pct_fraction": float(np.sort(abs_errs)[-int(n_daytime*0.05):].sum() / total_abs_error),
            "top_10pct_fraction": float(np.sort(abs_errs)[-int(n_daytime*0.10):].sum() / total_abs_error),
            "gt_50_w_m2": {
                "count": int((abs_errs > 50).sum()),
                "pct_hours": float((abs_errs > 50).mean() * 100),
                "error_fraction": float(abs_errs[abs_errs > 50].sum() / total_abs_error)
            },
            "gt_100_w_m2": {
                "count": int((abs_errs > 100).sum()),
                "pct_hours": float((abs_errs > 100).mean() * 100),
                "error_fraction": float(abs_errs[abs_errs > 100].sum() / total_abs_error)
            },
            "gt_150_w_m2": {
                "count": int((abs_errs > 150).sum()),
                "pct_hours": float((abs_errs > 150).mean() * 100),
                "error_fraction": float(abs_errs[abs_errs > 150].sum() / total_abs_error)
            },
            "gt_200_w_m2": {
                "count": int((abs_errs > 200).sum()),
                "pct_hours": float((abs_errs > 200).mean() * 100),
                "error_fraction": float(abs_errs[abs_errs > 200].sum() / total_abs_error)
            }
        }
    }

    # Section 6: Horizon Forensics
    horizon_stats = []
    for h in range(1, 25):
        h_df = daytime_df[daytime_df["horizon_hour"] == h]
        h_abs = h_df["abs_error"].values
        h_res = h_df["residual"].values
        h_act = h_df["actual"].values
        m_act = np.mean(h_act)
        mae = float(np.mean(h_abs))
        rmse = float(np.sqrt(np.mean(h_res**2)))
        bias = float(np.mean(h_res))
        tot_err = float(np.sum(h_abs))
        frac_err = float(tot_err / total_abs_error)
        n_samples = int(len(h_df))
        nmae = float((mae / m_act) * 100.0) if m_act > 0 else 0.0
        
        horizon_stats.append({
            "horizon": h,
            "sample_count": n_samples,
            "mae": mae,
            "rmse": rmse,
            "bias": bias,
            "mean_actual": float(m_act),
            "nmae_pct": nmae,
            "total_abs_error": tot_err,
            "error_fraction": frac_err
        })
    results["horizon_forensics"] = horizon_stats

    # Section 7: Solar-Elevation Forensics
    sol_bins = [0, 5, 10, 20, 30, 40, 50, 90]
    sol_labels = ["0-5 deg", "5-10 deg", "10-20 deg", "20-30 deg", "30-40 deg", "40-50 deg", "50+ deg"]
    daytime_df["sol_bin"] = pd.cut(daytime_df["solar_elevation"], bins=sol_bins, labels=sol_labels, include_lowest=True)
    
    sol_stats = []
    for lbl in sol_labels:
        b_df = daytime_df[daytime_df["sol_bin"] == lbl]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        b_act = b_df["actual"].values
        b_pred = b_df["pred"].values
        mae = float(np.mean(b_abs))
        rmse = float(np.sqrt(np.mean(b_res**2)))
        bias = float(np.mean(b_res))
        tot_err = float(np.sum(b_abs))
        sol_stats.append({
            "bin": lbl,
            "sample_count": int(len(b_df)),
            "mae": mae,
            "rmse": rmse,
            "bias": bias,
            "mean_actual": float(np.mean(b_act)),
            "mean_predicted": float(np.mean(b_pred)),
            "total_abs_error": tot_err,
            "error_fraction": float(tot_err / total_abs_error)
        })
    results["solar_elevation_forensics"] = sol_stats

    # Section 8: Cloud-Regime Forensics
    cf_bins = [-0.01, 0.1, 0.5, 0.9, 1.01]
    cf_labels = ["Near-Clear (0-10%)", "Partly Cloudy (10-50%)", "Mostly Cloudy (50-90%)", "Overcast (90-100%)"]
    daytime_df["cf_bin"] = pd.cut(daytime_df["cloud_frac"], bins=cf_bins, labels=cf_labels)
    
    cf_stats = []
    for lbl in cf_labels:
        b_df = daytime_df[daytime_df["cf_bin"] == lbl]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        cf_stats.append({
            "regime": lbl,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["cloud_fraction_forensics"] = cf_stats

    lwp_bins = [-0.001, 0.001, 0.05, 0.2, 10.0]
    lwp_labels = ["Zero/Near-Zero (<=0.001)", "Low (0.001-0.05)", "Medium (0.05-0.2)", "High (>0.2)"]
    daytime_df["lwp_bin"] = pd.cut(daytime_df["lwp_latest"], bins=lwp_bins, labels=lwp_labels)

    lwp_stats = []
    for lbl in lwp_labels:
        b_df = daytime_df[daytime_df["lwp_bin"] == lbl]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        lwp_stats.append({
            "regime": lbl,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["lwp_forensics"] = lwp_stats

    iwp_bins = [-0.001, 0.001, 0.02, 0.1, 10.0]
    iwp_labels = ["Zero/Near-Zero (<=0.001)", "Low (0.001-0.02)", "Medium (0.02-0.1)", "High (>0.1)"]
    daytime_df["iwp_bin"] = pd.cut(daytime_df["iwp_latest"], bins=iwp_bins, labels=iwp_labels)

    iwp_stats = []
    for lbl in iwp_labels:
        b_df = daytime_df[daytime_df["iwp_bin"] == lbl]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        iwp_stats.append({
            "regime": lbl,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["iwp_forensics"] = iwp_stats

    # Section 10: Terrain Forensics
    terrain_stats = []
    for flag, lbl in [(0.0, "Non-Obstructed"), (1.0, "Terrain-Obstructed")]:
        b_df = daytime_df[daytime_df["terrain_solar_obstruction_flag"] == flag]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        terrain_stats.append({
            "regime": lbl,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["terrain_forensics"] = terrain_stats

    # Section 11: Wind / Steering Forensics
    ws_bins = [0, 5, 12, 100]
    ws_labels = ["Low Wind (<5 m/s)", "Medium Wind (5-12 m/s)", "High Wind (>12 m/s)"]
    daytime_df["ws_bin"] = pd.cut(daytime_df["wind_speed_700"], bins=ws_bins, labels=ws_labels)

    ws_stats = []
    for lbl in ws_labels:
        b_df = daytime_df[daytime_df["ws_bin"] == lbl]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        ws_stats.append({
            "regime": lbl,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["wind_speed_forensics"] = ws_stats

    def get_wind_sector(d):
        if d >= 337.5 or d < 22.5: return "N"
        elif 22.5 <= d < 67.5: return "NE"
        elif 67.5 <= d < 112.5: return "E"
        elif 112.5 <= d < 157.5: return "SE"
        elif 157.5 <= d < 202.5: return "S"
        elif 202.5 <= d < 247.5: return "SW"
        elif 247.5 <= d < 292.5: return "W"
        else: return "NW"
    daytime_df["wind_sector"] = daytime_df["wind_dir_700"].apply(get_wind_sector)

    wdir_stats = []
    for sec in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
        b_df = daytime_df[daytime_df["wind_sector"] == sec]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        wdir_stats.append({
            "sector": sec,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error),
            "pct_obstructed": float((b_df["terrain_solar_obstruction_flag"] == 1.0).mean() * 100)
        })
    results["wind_direction_forensics"] = wdir_stats

    # Section 12: Seasonal / Monthly Forensics
    monthly_stats = []
    for m in range(1, 13):
        b_df = daytime_df[daytime_df["month"] == m]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        monthly_stats.append({
            "month": m,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "mean_actual": float(np.mean(b_df["actual"])),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["monthly_forensics"] = monthly_stats

    seasonal_stats = []
    for s in ["Winter", "Spring", "Summer", "Autumn"]:
        b_df = daytime_df[daytime_df["season"] == s]
        if len(b_df) == 0: continue
        b_abs = b_df["abs_error"].values
        b_res = b_df["residual"].values
        seasonal_stats.append({
            "season": s,
            "sample_count": int(len(b_df)),
            "mae": float(np.mean(b_abs)),
            "rmse": float(np.sqrt(np.mean(b_res**2))),
            "bias": float(np.mean(b_res)),
            "mean_actual": float(np.mean(b_df["actual"])),
            "total_abs_error": float(np.sum(b_abs)),
            "error_fraction": float(np.sum(b_abs) / total_abs_error)
        })
    results["seasonal_forensics"] = seasonal_stats

    # Section 13: Interaction Cross-Tabulations
    # 1. Cloud fraction x Solar elevation
    # Coarse solar elevation bins: Low (<15 deg), Mid (15-35 deg), High (>35 deg)
    sol_coarse_bins = [0, 15, 35, 90]
    sol_coarse_labels = ["Low Solar (<15 deg)", "Mid Solar (15-35 deg)", "High Solar (>35 deg)"]
    daytime_df["sol_coarse"] = pd.cut(daytime_df["solar_elevation"], bins=sol_coarse_bins, labels=sol_coarse_labels, include_lowest=True)

    interactions = {}
    
    # CF x Sol
    cf_sol_list = []
    for cf_lbl in cf_labels:
        for sol_lbl in sol_coarse_labels:
            sub = daytime_df[(daytime_df["cf_bin"] == cf_lbl) & (daytime_df["sol_coarse"] == sol_lbl)]
            if len(sub) > 0:
                cf_sol_list.append({
                    "cloud_regime": cf_lbl,
                    "solar_regime": sol_lbl,
                    "sample_count": int(len(sub)),
                    "mae": float(sub["abs_error"].mean()),
                    "rmse": float(np.sqrt((sub["residual"]**2).mean())),
                    "error_fraction": float(sub["abs_error"].sum() / total_abs_error)
                })
    interactions["cloud_frac_x_solar_elevation"] = cf_sol_list

    # Wind direction x Terrain obstruction
    wdir_ter_list = []
    for sec in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
        for flag, ter_lbl in [(0.0, "Non-Obstructed"), (1.0, "Terrain-Obstructed")]:
            sub = daytime_df[(daytime_df["wind_sector"] == sec) & (daytime_df["terrain_solar_obstruction_flag"] == flag)]
            if len(sub) > 0:
                wdir_ter_list.append({
                    "wind_sector": sec,
                    "terrain_regime": ter_lbl,
                    "sample_count": int(len(sub)),
                    "mae": float(sub["abs_error"].mean()),
                    "rmse": float(np.sqrt((sub["residual"]**2).mean())),
                    "error_fraction": float(sub["abs_error"].sum() / total_abs_error)
                })
    interactions["wind_dir_x_terrain_obstruction"] = wdir_ter_list

    # Wind speed x Cloud fraction
    ws_cf_list = []
    for ws_lbl in ws_labels:
        for cf_lbl in cf_labels:
            sub = daytime_df[(daytime_df["ws_bin"] == ws_lbl) & (daytime_df["cf_bin"] == cf_lbl)]
            if len(sub) > 0:
                ws_cf_list.append({
                    "wind_speed_regime": ws_lbl,
                    "cloud_regime": cf_lbl,
                    "sample_count": int(len(sub)),
                    "mae": float(sub["abs_error"].mean()),
                    "rmse": float(np.sqrt((sub["residual"]**2).mean())),
                    "error_fraction": float(sub["abs_error"].sum() / total_abs_error)
                })
    interactions["wind_speed_x_cloud_frac"] = ws_cf_list

    # Cloud regime x Horizon range (Short: H1-H8, Mid: H9-H16, Long: H17-H24)
    h_coarse_bins = [0, 8, 16, 24]
    h_coarse_labels = ["Short (H1-H8)", "Mid (H9-H16)", "Long (H17-H24)"]
    daytime_df["h_coarse"] = pd.cut(daytime_df["horizon_hour"], bins=h_coarse_bins, labels=h_coarse_labels)
    
    cf_h_list = []
    for cf_lbl in cf_labels:
        for h_lbl in h_coarse_labels:
            sub = daytime_df[(daytime_df["cf_bin"] == cf_lbl) & (daytime_df["h_coarse"] == h_lbl)]
            if len(sub) > 0:
                cf_h_list.append({
                    "cloud_regime": cf_lbl,
                    "horizon_range": h_lbl,
                    "sample_count": int(len(sub)),
                    "mae": float(sub["abs_error"].mean()),
                    "rmse": float(np.sqrt((sub["residual"]**2).mean())),
                    "error_fraction": float(sub["abs_error"].sum() / total_abs_error)
                })
    interactions["cloud_regime_x_horizon_range"] = cf_h_list

    results["interactions"] = interactions

    # Section 14: Top 50 Large Error Events
    top_50 = daytime_df.sort_values("abs_error", ascending=False).head(50)
    top_50_list = []

    for idx, row in top_50.iterrows():
        act = row["actual"]
        prd = row["pred"]
        res = row["residual"] # pred - actual
        cs = row["clearsky_ghi"]
        cf = row["cloud_frac"]
        lwp = row["lwp_latest"]
        iwp = row["iwp_latest"]
        sol_el = row["solar_elevation"]
        ter_obs = row["terrain_solar_obstruction_flag"]
        
        if sol_el < 10.0 and ter_obs == 1.0:
            phenotype = "terrain-shadow mismatch / low-sun transition"
        elif res > 100 and cf > 0.7:
            phenotype = "cloud optical-property / transmissivity overestimation"
        elif res > 100 and cf <= 0.3:
            phenotype = "missed cloud event (unobserved cloud)"
        elif res < -100 and cf > 0.7:
            phenotype = "missed clearing event (over-clouded forecast)"
        elif res < -100:
            phenotype = "irradiance amplitude underestimation / clearing"
        elif sol_el < 10.0:
            phenotype = "low-sun transition error"
        else:
            phenotype = "UNRESOLVED / mixed cloud-radiative error"

        top_50_list.append({
            "rank": len(top_50_list) + 1,
            "origin": row["forecast_start"].isoformat(),
            "valid_time": row["timestamp"].isoformat(),
            "horizon": int(row["horizon_hour"]),
            "actual_sw_in": float(act),
            "predicted_sw_in": float(prd),
            "residual": float(res),
            "abs_error": float(row["abs_error"]),
            "solar_elevation": float(sol_el),
            "clearsky_ghi": float(cs),
            "cloud_frac": float(cf),
            "lwp": float(lwp),
            "iwp": float(iwp),
            "terrain_obstructed": bool(ter_obs == 1.0),
            "u700": float(row["u700"]),
            "v700": float(row["v700"]),
            "month": int(row["month"]),
            "retrospective_phenotype": phenotype
        })
    results["top_50_error_events"] = top_50_list

    # Section 15: Residual Temporal Structure (Autocorrelation)
    full_day_res = daytime_df.sort_values("timestamp")["residual"].values
    
    def safe_autocorr(x, lag):
        if lag >= len(x): return 0.0
        x1 = x[:-lag]
        x2 = x[lag:]
        std1, std2 = np.std(x1), np.std(x2)
        if std1 == 0 or std2 == 0: return 0.0
        return float(np.corrcoef(x1, x2)[0, 1])

    autocorrs = {}
    for lag in [1, 2, 3, 6, 12, 24]:
        autocorrs[f"lag_{lag}"] = safe_autocorr(full_day_res, lag)

    origin_autocorrs = {1: [], 2: [], 3: [], 6: []}
    for orig, grp in daytime_df.groupby("forecast_start"):
        grp_sorted = grp.sort_values("horizon_hour")
        r_grp = grp_sorted["residual"].values
        if len(r_grp) > 6:
            for l in [1, 2, 3, 6]:
                if l < len(r_grp):
                    ac = safe_autocorr(r_grp, l)
                    if not np.isnan(ac):
                        origin_autocorrs[l].append(ac)
    
    intra_autocorrs = {f"intra_origin_lag_{l}": float(np.mean(origin_autocorrs[l])) for l in [1, 2, 3, 6]}

    results["residual_temporal_structure"] = {
        "sequence_autocorrelation": autocorrs,
        "intra_origin_autocorrelation": intra_autocorrs
    }

    # Save to JSON artifact
    json_path = STAGE_DIR / "STAGE8_14A_RESIDUAL_ERROR_FORENSICS.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Successfully computed forensics and saved to {json_path}")
    return results

if __name__ == "__main__":
    res = compute_forensics()
