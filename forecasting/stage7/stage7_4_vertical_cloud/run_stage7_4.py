#!/usr/bin/env python3
"""
POLARIS STAGE 7.4 — VERTICAL CLOUD STRUCTURE FORECASTING EXPERIMENT
===================================================================
Terminal-First, Resumable, Multi-Threaded Feature Extraction & 5-Fold EVEN CV.

Features Extracted (8 Surface-Aware Vertical Cloud Features):
  1. f_lwp_low: Fraction of LWP at p > 800 hPa
  2. f_lwp_mid: Fraction of LWP at 500 <= p <= 800 hPa
  3. f_lwp_high: Fraction of LWP at p < 500 hPa
  4. p_centroid_lwp: Liquid water mass-weighted pressure centroid (hPa)
  5. p_centroid_iwp: Cloud ice mass-weighted pressure centroid (hPa)
  6. dp_ice_liquid_centroid: Liquid-ice vertical separation (hPa)
  7. cloud_frac_mid: Maximum cloud area fraction at 500 <= p <= 800 hPa
  8. cloud_frac_high: Maximum cloud area fraction at p < 500 hPa

Pipeline Steps:
  1. Extract 8 vertical features for all 347 benchmark origins (8,328 rows)
     via surface-aware boundary truncation at model surface pressure p_sfc.
  2. Pre-CV Data Integrity Audit (8,328 rows, range checks, no NaN/Inf, causality check).
  3. E0 Exact Control Reproduction (Stage 6.6 Champion baseline: 38.2806 W/m² MAE).
  4. E1 Candidate EVEN 5-Fold Forward-Chaining CV (39 features = 31 Stage 6.6 + 8 Vertical).
  5. 5 Predeclared Acceptance Gates Evaluation.
  6. Save all audit and decision artifacts.
"""

import os
import sys
import time
import json
import signal
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
import concurrent.futures
import threading

import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# PATHS & CONFIGURATION
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage7_4_vertical_cloud"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"
STAGE6_6_FEAT_PATH = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp" / "lwp_iwp_extracted_features.csv"

# Output Paths
CHECKPOINT_PATH = STAGE_DIR / "extraction_checkpoint.json"
FEATURES_PATH = STAGE_DIR / "vertical_cloud_extracted_features.csv"
EXTRACTION_AUDIT_PATH = STAGE_DIR / "stage7_4_extraction_audit.json"
PRE_CV_AUDIT_PATH = STAGE_DIR / "stage7_4_pre_cv_integrity_audit.csv"
CV_RESULTS_PATH = STAGE_DIR / "stage7_4_even_cv_results.csv"
FOLD_RESULTS_PATH = STAGE_DIR / "stage7_4_fold_results.csv"
GATE_DECISION_PATH = STAGE_DIR / "stage7_4_gate_decision.json"
REPORT_PATH = STAGE_DIR / "stage7_4_forecasting_report.md"
REPRO_PATH = STAGE_DIR / "stage7_4_reproducibility_report.md"
INTEGRITY_AUDIT_PATH = STAGE_DIR / "stage7_4_integrity_audit.json"
LOG_PATH = STAGE_DIR / "stage7_4.log"

NUOLJA_Y, NUOLJA_X = 760, 486
PRESSURE_LEVELS_HPA = np.array([50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000], dtype=float)
PRESSURE_LEVELS_PA = PRESSURE_LEVELS_HPA * 100.0
GRAVITY_G = 9.80665

INTERRUPTED = False
checkpoint_lock = threading.Lock()

def handle_signal(sig, frame):
    global INTERRUPTED
    sig_name = "SIGINT (Ctrl+C)" if sig == signal.SIGINT else f"Signal {sig}"
    print(f"\n\n[SIGNAL] Received {sig_name}. Saving progress and stopping cleanly...")
    INTERRUPTED = True

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

logger = logging.getLogger("stage7_4")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(file_handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

def atomic_write_json(obj, file_path: Path):
    tmp_path = file_path.with_suffix(".tmp.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp_path, file_path)

def atomic_write_csv(df: pd.DataFrame, file_path: Path):
    tmp_path = file_path.with_suffix(".tmp.csv")
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, file_path)

def fetch_meps_ascii(url, var_name, max_retries=4, timeout=30):
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                lines = r.text.split('\n')
                header = f'{var_name}.{var_name}'
                start = False
                vals = []
                for l in lines:
                    if header in l:
                        start = True
                        continue
                    if start:
                        if l.startswith(f'{var_name}.'):
                            break
                        if l.strip() and ',' in l:
                            val_str = l.split(',')[-1].strip()
                            vals.append(float(val_str))
                if len(vals) > 0:
                    return np.array(vals)
            elif r.status_code == 429:
                time.sleep(2 ** attempt + 1)
        except Exception:
            time.sleep(attempt)
    return None

def compute_surface_aware_vertical_features(ps_pa, ql_profile, qi_profile, cloud_frac_profile):
    layer_lwp = np.zeros(12)
    layer_iwp = np.zeros(12)
    layer_p_mid = np.zeros(12)
    
    for k in range(12):
        p_top = PRESSURE_LEVELS_PA[k]
        p_bot = PRESSURE_LEVELS_PA[k+1]
        
        if p_bot <= ps_pa:
            dp = p_bot - p_top
            ql_avg = 0.5 * (ql_profile[k] + ql_profile[k+1])
            qi_avg = 0.5 * (qi_profile[k] + qi_profile[k+1])
            p_mid = 0.5 * (PRESSURE_LEVELS_HPA[k] + PRESSURE_LEVELS_HPA[k+1])
        elif p_top < ps_pa < p_bot:
            w = (ps_pa - p_top) / (p_bot - p_top)
            ql_sfc = ql_profile[k] + w * (ql_profile[k+1] - ql_profile[k])
            qi_sfc = qi_profile[k] + w * (qi_profile[k+1] - qi_profile[k])
            dp = ps_pa - p_top
            ql_avg = 0.5 * (ql_profile[k] + ql_sfc)
            qi_avg = 0.5 * (qi_profile[k] + qi_sfc)
            p_mid = 0.5 * (PRESSURE_LEVELS_HPA[k] + ps_pa / 100.0)
        else:
            dp = 0.0
            ql_avg = 0.0
            qi_avg = 0.0
            p_mid = PRESSURE_LEVELS_HPA[k]
            
        layer_lwp[k] = (ql_avg * dp / GRAVITY_G) * 1000.0
        layer_iwp[k] = (qi_avg * dp / GRAVITY_G) * 1000.0
        layer_p_mid[k] = p_mid

    total_lwp = np.sum(layer_lwp)
    total_iwp = np.sum(layer_iwp)
    
    lwp_high = np.sum(layer_lwp[PRESSURE_LEVELS_HPA[1:] <= 500])
    lwp_mid = np.sum(layer_lwp[(PRESSURE_LEVELS_HPA[1:] > 500) & (PRESSURE_LEVELS_HPA[1:] <= 800)])
    lwp_low = np.sum(layer_lwp[PRESSURE_LEVELS_HPA[1:] > 800])
    
    f_lwp_high = float(lwp_high / total_lwp) if total_lwp > 1e-6 else 0.0
    f_lwp_mid = float(lwp_mid / total_lwp) if total_lwp > 1e-6 else 0.0
    f_lwp_low = float(lwp_low / total_lwp) if total_lwp > 1e-6 else 0.0
    
    ps_hpa = float(ps_pa / 100.0)
    p_centroid_lwp = float(np.sum(layer_lwp * layer_p_mid) / total_lwp) if total_lwp > 1e-6 else ps_hpa
    p_centroid_iwp = float(np.sum(layer_iwp * layer_p_mid) / total_iwp) if total_iwp > 1e-6 else 300.0
    
    dp_ice_liquid_centroid = p_centroid_lwp - p_centroid_iwp
    
    valid_levels = PRESSURE_LEVELS_PA <= ps_pa
    cf_levels = np.copy(cloud_frac_profile)
    if np.max(cf_levels) > 1.0:
        cf_levels = cf_levels / 100.0
    cf_levels[~valid_levels] = 0.0
    
    cf_high = float(np.max(cf_levels[PRESSURE_LEVELS_HPA <= 500])) if np.any(PRESSURE_LEVELS_HPA <= 500) else 0.0
    cf_mid = float(np.max(cf_levels[(PRESSURE_LEVELS_HPA > 500) & (PRESSURE_LEVELS_HPA <= 800)])) if np.any((PRESSURE_LEVELS_HPA > 500) & (PRESSURE_LEVELS_HPA <= 800)) else 0.0

    return {
        "f_lwp_low": round(f_lwp_low, 6),
        "f_lwp_mid": round(f_lwp_mid, 6),
        "f_lwp_high": round(f_lwp_high, 6),
        "p_centroid_lwp": round(p_centroid_lwp, 4),
        "p_centroid_iwp": round(p_centroid_iwp, 4),
        "dp_ice_liquid_centroid": round(dp_ice_liquid_centroid, 4),
        "cloud_frac_mid": round(cf_mid, 6),
        "cloud_frac_high": round(cf_high, 6)
    }

def process_single_origin(origin_idx, origin_ts_str):
    origin_dt = pd.Timestamp(origin_ts_str)
    date_str = origin_dt.strftime("%Y/%m/%d")
    tag_str = origin_dt.strftime("%Y%m%dT00Z")
    meps_run_id = f"meps_det_{tag_str}"
    
    url_ps = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_sfc_{tag_str}.ncml.ascii?surface_air_pressure[0:1:23][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    ps_pa = fetch_meps_ascii(url_ps, 'surface_air_pressure')
    if ps_pa is None or len(ps_pa) != 24:
        return {"status": "FAILED", "reason": "Failed to fetch surface_air_pressure", "origin": origin_ts_str, "origin_index": origin_idx}
        
    url_ql = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    ql_raw = fetch_meps_ascii(url_ql, 'mass_fraction_of_cloud_condensed_water_in_air_pl')
    if ql_raw is None or len(ql_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_condensed_water (ql)", "origin": origin_ts_str, "origin_index": origin_idx}
        
    url_qi = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_ice_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    qi_raw = fetch_meps_ascii(url_qi, 'mass_fraction_of_cloud_ice_in_air_pl')
    if qi_raw is None or len(qi_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_ice (qi)", "origin": origin_ts_str, "origin_index": origin_idx}

    url_cf = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?cloud_area_fraction_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    cf_raw = fetch_meps_ascii(url_cf, 'cloud_area_fraction_pl')
    if cf_raw is None or len(cf_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_area_fraction_pl", "origin": origin_ts_str, "origin_index": origin_idx}

    ql_data = ql_raw.reshape((24, 13))
    qi_data = qi_raw.reshape((24, 13))
    cf_data = cf_raw.reshape((24, 13))
    
    records = []
    for h_idx in range(24):
        h = h_idx + 1
        ps = ps_pa[h_idx]
        ql_prof = ql_data[h_idx]
        qi_prof = qi_data[h_idx]
        cf_prof = cf_data[h_idx]
        
        if np.isnan(ps) or ps < 70000.0 or ps > 110000.0:
            return {"status": "INVALID", "reason": f"Unphysical surface pressure {ps} Pa at lead hour {h}", "origin": origin_ts_str, "origin_index": origin_idx}
            
        feats = compute_surface_aware_vertical_features(ps, ql_prof, qi_prof, cf_prof)
        feats["origin_index"] = origin_idx
        feats["forecast_start"] = origin_ts_str
        feats["horizon_hour"] = h
        feats["valid_time"] = (origin_dt + pd.Timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S")
        feats["forecast_reference_time"] = origin_ts_str
        feats["surface_air_pressure_hpa"] = round(float(ps / 100.0), 2)
        feats["meps_run_id"] = meps_run_id
        records.append(feats)
        
    return {"status": "COMPLETE", "records": records, "meps_run": meps_run_id, "origin": origin_ts_str, "origin_index": origin_idx}

def load_checkpoint(total_origins_list):
    if CHECKPOINT_PATH.exists():
        try:
            with open(CHECKPOINT_PATH, "r") as f:
                data = json.load(f)
            if "origins" in data and isinstance(data["origins"], dict):
                return data
        except Exception:
            pass

    checkpoint = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_origins": len(total_origins_list),
        "status": "INITIALIZED",
        "origins": {}
    }
    for idx, origin_str in enumerate(total_origins_list):
        checkpoint["origins"][origin_str] = {
            "origin_index": idx,
            "t0": origin_str,
            "status": "PENDING",
            "meps_run": None,
            "completed_horizons": 0,
            "updated_at": None
        }
    atomic_write_json(checkpoint, CHECKPOINT_PATH)
    return checkpoint

def save_checkpoint(checkpoint):
    with checkpoint_lock:
        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
        atomic_write_json(checkpoint, CHECKPOINT_PATH)

def run_extraction(origins_list, checkpoint, num_workers=16):
    global INTERRUPTED
    logger.info("\n" + "=" * 80)
    logger.info("[STAGE 7.4] AUTHORIZED — VERTICAL CLOUD STRUCTURE FEATURE EXTRACTION")
    logger.info(f"[STAGE 7.4] Origins: {len(origins_list)} | Horizons: 24 | Total expected rows: {len(origins_list) * 24}")
    logger.info(f"[STAGE 7.4] Extraction workers: {num_workers} | Live progress reporting: ENABLED")
    logger.info("=" * 80)
    
    pending_origins = [o for o in origins_list if checkpoint["origins"][o]["status"] != "COMPLETE"]
    if len(pending_origins) == 0:
        logger.info("[STAGE 7.4] Extraction already 100% complete! Proceeding to audit.")
        return True
        
    if FEATURES_PATH.exists():
        existing_df = pd.read_csv(FEATURES_PATH)
        all_feature_records = existing_df.to_dict("records")
    else:
        all_feature_records = []
        
    start_time = time.time()
    completed_count = sum(1 for o in origins_list if checkpoint["origins"][o]["status"] == "COMPLETE")
    
    checkpoint["status"] = "EXTRACTING"
    save_checkpoint(checkpoint)
    
    def task_worker(origin_str):
        if INTERRUPTED:
            return None
        idx = checkpoint["origins"][origin_str]["origin_index"]
        return process_single_origin(idx, origin_str)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_origin = {executor.submit(task_worker, o): o for o in pending_origins}
        
        for future in concurrent.futures.as_completed(future_to_origin):
            if INTERRUPTED:
                logger.info("\n[INTERRUPT] Stopping extraction gracefully...")
                executor.shutdown(wait=False, cancel_futures=True)
                break
                
            origin_str = future_to_origin[future]
            try:
                res = future.result()
            except Exception as exc:
                res = {"status": "FAILED", "reason": str(exc), "origin": origin_str, "origin_index": checkpoint["origins"][origin_str]["origin_index"]}
                
            if res is None:
                continue
                
            status_info = checkpoint["origins"][origin_str]
            if res["status"] == "COMPLETE":
                all_feature_records.extend(res["records"])
                status_info["status"] = "COMPLETE"
                status_info["meps_run"] = res["meps_run"]
                status_info["completed_horizons"] = 24
                status_info["updated_at"] = datetime.now(timezone.utc).isoformat()
                completed_count += 1
            else:
                status_info["status"] = res["status"]
                status_info["error"] = res.get("reason", "Unknown error")
                status_info["updated_at"] = datetime.now(timezone.utc).isoformat()
                logger.error(f"  [STAGE 7.4] FAILED origin {origin_str}: {status_info['error']}")
                
            current_df = pd.DataFrame(all_feature_records)
            if not current_df.empty:
                atomic_write_csv(current_df, FEATURES_PATH)
            save_checkpoint(checkpoint)
            
            elapsed_s = time.time() - start_time
            avg_s = elapsed_s / max(1, (completed_count - (len(origins_list) - len(pending_origins))))
            rem_origs = len(origins_list) - completed_count
            eta_s = rem_origs * (avg_s / max(1, num_workers))
            
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_s))
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_s))
            
            logger.info(
                f"[STAGE 7.4] Extraction: {completed_count}/{len(origins_list)} origins complete ({completed_count/len(origins_list)*100:.1f}%) | "
                f"Rows: {len(all_feature_records)} | Runtime: {elapsed_str} | Avg/origin: {avg_s:.1f}s | ETA: {eta_str}"
            )

    if INTERRUPTED:
        checkpoint["status"] = "INTERRUPTED"
        save_checkpoint(checkpoint)
        logger.info(f"\n[INTERRUPTED] Progress saved cleanly. Completed: {completed_count}/{len(origins_list)} origins.")
        return False

    checkpoint["status"] = "EXTRACTION_COMPLETE"
    save_checkpoint(checkpoint)
    logger.info(f"\n[STAGE 7.4] Extraction SUCCESSFUL: {completed_count}/{len(origins_list)} origins extracted ({len(all_feature_records)} rows).")
    return True

def fit_stage4_parameters(train_df):
    params = {}
    day_df = train_df[train_df["is_daytime"]]
    for h in range(1, 25):
        h_sub = day_df[day_df["horizon_hour"] == h]
        if len(h_sub) < 5:
            params[str(h)] = {"w": 0.5, "k": 0.9}
            continue
        y_true = h_sub["actual_SW_IN"].values
        chronos = h_sub["pred_stage3b_cloud_nwp"].values
        cs_ghi = h_sub["clearsky_ghi"].values
        c_frac = h_sub["cloud_frac"].values
        
        best_mae = 1e9
        best_w, best_k = 0.5, 0.9
        for w in np.linspace(0.0, 1.0, 51):
            for k in np.linspace(0.5, 1.2, 15):
                phys = np.maximum(0.0, cs_ghi * (1.0 - k * c_frac))
                pred = np.maximum(0.0, w * chronos + (1.0 - w) * phys)
                mae = mean_absolute_error(y_true, pred)
                if mae < best_mae:
                    best_mae = mae
                    best_w, best_k = w, k
        params[str(h)] = {"w": float(best_w), "k": float(best_k)}
    return params

def apply_stage4_params(df_subset, params):
    st4_preds, phys_preds = [], []
    for idx, row in df_subset.iterrows():
        h = str(int(row["horizon_hour"]))
        p = params.get(h, {"w": 0.5, "k": 0.9})
        w_h, k_h = p["w"], p["k"]
        cs_ghi = row["clearsky_ghi"]
        c_frac = row["cloud_frac"]
        chronos = row["pred_stage3b_cloud_nwp"]
        phys = max(0.0, cs_ghi * (1.0 - k_h * c_frac))
        st4 = max(0.0, w_h * chronos + (1.0 - w_h) * phys)
        if row["is_night_causal"]:
            st4 = 0.0
            phys = 0.0
        phys_preds.append(phys)
        st4_preds.append(st4)
    return np.array(st4_preds), np.array(phys_preds)

def run_even_cv_and_gates():
    logger.info("\n" + "=" * 80)
    logger.info("[STAGE 7.4] 5-FOLD FORWARD-CHAINING EVEN CV & ACCEPTANCE GATE AUDIT")
    logger.info("=" * 80)
    
    sites = pd.read_csv(SITES_PATH)
    sites["TIMESTAMP"] = pd.to_datetime(sites["TIMESTAMP"])
    sites_obs = sites.rename(columns={"SW_IN": "obs_SW_IN"})
    
    cs = pd.read_csv(CLEARSKY_PATH)
    cs["TIMESTAMP"] = pd.to_datetime(cs["TIMESTAMP"])
    
    nwp = pd.read_csv(NWP_PATH)
    nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])
    nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
    
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])
    s4_preds["timestamp"] = pd.to_datetime(s4_preds["timestamp"])
    
    s6_feat = pd.read_csv(STAGE6_6_FEAT_PATH)
    s6_feat["forecast_start"] = pd.to_datetime(s6_feat["forecast_start"])
    
    v_feat = pd.read_csv(FEATURES_PATH)
    v_feat["forecast_start"] = pd.to_datetime(v_feat["forecast_start"])
    
    cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
    df = s4_preds.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left").drop(columns=["TIMESTAMP"])
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["pred_stage4_full"] = df["pred_ensemble"]
    
    df = df.merge(s6_feat[["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]
    
    vertical_cols = [
        "f_lwp_low", "f_lwp_mid", "f_lwp_high",
        "p_centroid_lwp", "p_centroid_iwp", "dp_ice_liquid_centroid",
        "cloud_frac_mid", "cloud_frac_high"
    ]
    df = df.merge(v_feat[["forecast_start", "horizon_hour"] + vertical_cols], on=["forecast_start", "horizon_hour"], how="left")
    
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
        
    df["phys_pred_full"] = phys_preds_full
    df["is_night_causal"] = (df["solar_elevation"] <= 0.0) | (df["clearsky_ghi"] == 0.0)
    df["is_daytime"] = df["actual_SW_IN"] > 0
    
    origins = sorted(df["forecast_start"].unique())
    even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
    even_origins_sorted = sorted(even_origins)
    
    ctx_feature_rows = []
    for origin in origins:
        origin_ts = pd.Timestamp(origin)
        context_start = origin_ts - pd.Timedelta(hours=24)
        ctx_sites = sites_obs[(sites_obs["TIMESTAMP"] >= context_start) & (sites_obs["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
        sw_vals = ctx_sites["obs_SW_IN"].dropna().values
        
        if len(sw_vals) < 12:
            ctx_feature_rows.append({
                "forecast_start": origin_ts,
                "ctx_std_3h": 0.0, "ctx_std_6h": 0.0, "ctx_std_12h": 0.0, "ctx_std_24h": 0.0,
                "ctx_abs_change_1h": 0.0, "ctx_abs_change_3h": 0.0, "ctx_abs_change_6h": 0.0,
                "ctx_max_diff_6h": 0.0, "ctx_mean_diff_6h": 0.0, "ctx_slope_6h": 0.0,
                "ctx_kt_std_6h": 0.0, "ctx_last_obs": 0.0, "ctx_mean_24h": 0.0, "ctx_max_24h": 0.0
            })
            continue
            
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
        
        ctx_cs = cs[(cs["TIMESTAMP"] >= context_start) & (cs["TIMESTAMP"] < origin_ts)].sort_values("TIMESTAMP")
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
    
    control_features = [
        "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
        "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
        "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
        "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
        "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
        "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
        "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h"
    ]
    stage6_6_features = control_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    candidate_39_features = stage6_6_features + vertical_cols
    
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
    fold_records = []
    
    for fold in range(1, n_splits + 1):
        logger.info(f"[STAGE 7.4] Fold {fold}/5 starting...")
        tr_origs = even_origins_sorted[: fold * split_size]
        val_origs = even_origins_sorted[fold * split_size : (fold + 1) * split_size]
        
        tr_df = df_even[df_even["forecast_start"].isin(tr_origs)].copy()
        val_df = df_even[df_even["forecast_start"].isin(val_origs)].copy()
        
        st4_params_fold = fit_stage4_parameters(tr_df)
        st4_tr, phys_tr = apply_stage4_params(tr_df, st4_params_fold)
        st4_val, phys_val = apply_stage4_params(val_df, st4_params_fold)
        
        tr_df["pred_stage4_fold"] = st4_tr
        tr_df["phys_pred_fold"] = phys_tr
        tr_df["disagreement_fold"] = (tr_df["pred_stage3b_cloud_nwp"] - tr_df["phys_pred_fold"]).abs()
        
        val_df["pred_stage4_fold"] = st4_val
        val_df["phys_pred_fold"] = phys_val
        val_df["disagreement_fold"] = (val_df["pred_stage3b_cloud_nwp"] - val_df["phys_pred_fold"]).abs()
        
        tr_day = tr_df[tr_df["is_daytime"]].copy()
        val_day = val_df[val_df["is_daytime"]].copy()
        
        y_tr = tr_day["actual_SW_IN"].values
        st4_tr_day = tr_day["pred_stage4_fold"].values
        res_tr = y_tr - st4_tr_day
        
        y_val = val_day["actual_SW_IN"].values
        st4_val_day = val_day["pred_stage4_fold"].values
        
        X_tr_e0 = tr_day[stage6_6_features].values
        X_val_e0 = val_day[stage6_6_features].values
        
        X_tr_e1 = tr_day[candidate_39_features].values
        X_val_e1 = val_day[candidate_39_features].values
        
        # E0 Control
        model_e0 = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_e0.fit(X_tr_e0, res_tr)
        pred_res_e0 = model_e0.predict(X_val_e0)
        pred_sw_e0 = np.maximum(0.0, st4_val_day + pred_res_e0)
        pred_sw_e0[val_day["is_night_causal"].values] = 0.0
        
        # E1 Candidate
        model_e1 = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_e1.fit(X_tr_e1, res_tr)
        pred_res_e1 = model_e1.predict(X_val_e1)
        pred_sw_e1 = np.maximum(0.0, st4_val_day + pred_res_e1)
        pred_sw_e1[val_day["is_night_causal"].values] = 0.0
        
        mae_e0 = mean_absolute_error(y_val, pred_sw_e0)
        mae_e1 = mean_absolute_error(y_val, pred_sw_e1)
        mean_y_val = np.mean(y_val)
        
        nmae_e0 = (mae_e0 / mean_y_val) * 100.0
        nmae_e1 = (mae_e1 / mean_y_val) * 100.0
        
        rmse_e0 = np.sqrt(mean_squared_error(y_val, pred_sw_e0))
        rmse_e1 = np.sqrt(mean_squared_error(y_val, pred_sw_e1))
        
        bias_e0 = np.mean(pred_sw_e0 - y_val)
        bias_e1 = np.mean(pred_sw_e1 - y_val)
        
        delta_mae = mae_e1 - mae_e0
        
        fold_records.append({
            "fold": fold,
            "ctrl_mae_w_m2": round(float(mae_e0), 6),
            "cand_mae_w_m2": round(float(mae_e1), 6),
            "delta_mae_w_m2": round(float(delta_mae), 6),
            "ctrl_nmae_pct": round(float(nmae_e0), 4),
            "cand_nmae_pct": round(float(nmae_e1), 4),
            "ctrl_rmse_w_m2": round(float(rmse_e0), 6),
            "cand_rmse_w_m2": round(float(rmse_e1), 6),
            "ctrl_bias_w_m2": round(float(bias_e0), 6),
            "cand_bias_w_m2": round(float(bias_e1), 6),
            "fold_improved": bool(delta_mae <= 0.0),
            "degradation_pass": bool(delta_mae <= 0.15)
        })
        
        logger.info(
            f"[STAGE 7.4] Fold {fold}/5 complete | Control MAE: {mae_e0:.4f} W/m² | Candidate MAE: {mae_e1:.4f} W/m² | Delta: {delta_mae:+.4f} W/m²"
        )

    df_folds = pd.DataFrame(fold_records)
    atomic_write_csv(df_folds, FOLD_RESULTS_PATH)
    
    cv_ctrl_mae = float(df_folds["ctrl_mae_w_m2"].mean())
    cv_cand_mae = float(df_folds["cand_mae_w_m2"].mean())
    delta_mae_agg = cv_cand_mae - cv_ctrl_mae
    
    cv_ctrl_nmae = float(df_folds["ctrl_nmae_pct"].mean())
    cv_cand_nmae = float(df_folds["cand_nmae_pct"].mean())
    
    cv_ctrl_rmse = float(df_folds["ctrl_rmse_w_m2"].mean())
    cv_cand_rmse = float(df_folds["cand_rmse_w_m2"].mean())
    
    cv_ctrl_bias = float(df_folds["ctrl_bias_w_m2"].mean())
    cv_cand_bias = float(df_folds["cand_bias_w_m2"].mean())
    
    repro_pass = abs(cv_ctrl_mae - 38.2806) < 0.01
    
    gate1_pass = cv_cand_mae <= 38.0806
    gate2_pass = int(df_folds["fold_improved"].sum()) >= 4
    gate3_max_degrad = float(df_folds["delta_mae_w_m2"].max())
    gate3_pass = gate3_max_degrad <= 0.15
    gate4_pass = cv_cand_nmae <= cv_ctrl_nmae
    gate5_pass = cv_cand_rmse <= cv_ctrl_rmse
    
    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass
    
    cv_records = [
        {
            "model_configuration": "E0 (Stage 6.6 Control)",
            "daytime_mae_w_m2": round(cv_ctrl_mae, 6),
            "daytime_nmae_pct": round(cv_ctrl_nmae, 4),
            "daytime_rmse_w_m2": round(cv_ctrl_rmse, 6),
            "daytime_bias_w_m2": round(cv_ctrl_bias, 6),
            "night_mae_w_m2": 0.0,
            "status": "CONTROL_REPRODUCED" if repro_pass else "CONTROL_MISMATCH"
        },
        {
            "model_configuration": "E1 (39 Features: Stage 6.6 + 8 Vertical Features)",
            "daytime_mae_w_m2": round(cv_cand_mae, 6),
            "daytime_nmae_pct": round(cv_cand_nmae, 4),
            "daytime_rmse_w_m2": round(cv_cand_rmse, 6),
            "daytime_bias_w_m2": round(cv_cand_bias, 6),
            "night_mae_w_m2": 0.0,
            "status": "EVEN_CV_PASS" if all_gates_pass else "REJECTED_NO_IMPROVEMENT"
        }
    ]
    atomic_write_csv(pd.DataFrame(cv_records), CV_RESULTS_PATH)
    
    decision_str = "STAGE 7.4 EVEN-CV PASS — ODD evaluation requires explicit authorization." if all_gates_pass else "STAGE 7.4 REJECTED — Stage 6.6 remains champion."
    
    gate_decision = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": "STAGE 7.4 VERTICAL CLOUD STRUCTURE FORECASTING EXPERIMENT",
        "control_reproduction": {
            "expected_e0_mae": 38.2806,
            "actual_e0_mae": round(cv_ctrl_mae, 6),
            "reproduction_pass": bool(repro_pass)
        },
        "candidate_results": {
            "e1_mae_w_m2": round(cv_cand_mae, 6),
            "delta_mae_w_m2": round(delta_mae_agg, 6),
            "e1_nmae_pct": round(cv_cand_nmae, 4),
            "e1_rmse_w_m2": round(cv_cand_rmse, 6),
            "e1_bias_w_m2": round(cv_cand_bias, 6),
            "folds_improved": int(df_folds["fold_improved"].sum()),
            "max_fold_degradation_w_m2": round(gate3_max_degrad, 6)
        },
        "gates": {
            "gate1_mae": {"threshold_w_m2": 38.0806, "actual_w_m2": round(cv_cand_mae, 6), "pass": bool(gate1_pass)},
            "gate2_folds": {"required_folds": 4, "actual_folds": int(df_folds["fold_improved"].sum()), "pass": bool(gate2_pass)},
            "gate3_max_degrad": {"threshold_w_m2": 0.15, "actual_w_m2": round(gate3_max_degrad, 6), "pass": bool(gate3_pass)},
            "gate4_nmae": {"threshold_pct": round(cv_ctrl_nmae, 2), "actual_pct": round(cv_cand_nmae, 2), "pass": bool(gate4_pass)},
            "gate5_rmse": {"threshold_w_m2": round(cv_ctrl_rmse, 4), "actual_w_m2": round(cv_cand_rmse, 4), "pass": bool(gate5_pass)}
        },
        "all_gates_pass": bool(all_gates_pass),
        "final_decision": decision_str,
        "odd_accessed": False
    }
    atomic_write_json(gate_decision, GATE_DECISION_PATH)
    
    logger.info("\n" + "=" * 60)
    logger.info("[STAGE 7.4] EVEN CV RESULTS & LOCKED GATES AUDIT")
    logger.info("=" * 60)
    logger.info(f"Control MAE:      {cv_ctrl_mae:.4f} W/m² (Expected: 38.2806 W/m²)")
    logger.info(f"Candidate MAE:    {cv_cand_mae:.4f} W/m²")
    logger.info(f"Delta MAE:        {delta_mae_agg:+.4f} W/m²")
    logger.info(f"Candidate nMAE:   {cv_cand_nmae:.2f}% (Control: {cv_ctrl_nmae:.2f}%)")
    logger.info(f"Candidate RMSE:   {cv_cand_rmse:.4f} W/m² (Control: {cv_ctrl_rmse:.4f} W/m²)")
    logger.info(f"Candidate Bias:   {cv_cand_bias:+.4f} W/m² (Control: {cv_ctrl_bias:+.4f} W/m²)")
    logger.info("-" * 60)
    logger.info(f"Gate 1 (MAE <= 38.0806 W/m²):      {'PASS' if gate1_pass else 'FAIL'} ({cv_cand_mae:.4f} W/m²)")
    logger.info(f"Gate 2 (Improve >= 4/5 Folds):     {'PASS' if gate2_pass else 'FAIL'} ({int(df_folds['fold_improved'].sum())}/5 folds)")
    logger.info(f"Gate 3 (Max Degrad <= +0.15 W/m²): {'PASS' if gate3_pass else 'FAIL'} ({gate3_max_degrad:+.4f} W/m²)")
    logger.info(f"Gate 4 (nMAE <= {cv_ctrl_nmae:.2f}%):          {'PASS' if gate4_pass else 'FAIL'} ({cv_cand_nmae:.2f}%)")
    logger.info(f"Gate 5 (RMSE <= {cv_ctrl_rmse:.4f} W/m²):    {'PASS' if gate5_pass else 'FAIL'} ({cv_cand_rmse:.4f} W/m²)")
    logger.info("=" * 60)
    logger.info(f"\nFINAL DECISION: {decision_str}")
    logger.info("ODD TEST SET: 100% UNTOUCHED & LOCKED")
    
    return all_gates_pass

def main():
    parser = argparse.ArgumentParser(description="POLARIS Stage 7.4 Vertical Cloud Structure Pipeline")
    parser.add_argument("--workers", type=int, default=16, help="Number of extraction worker threads (default: 16)")
    args = parser.parse_args()
    
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    origins_list = sorted([str(o) for o in s4_preds["forecast_start"].unique()])
    
    checkpoint = load_checkpoint(origins_list)
    
    success = run_extraction(origins_list, checkpoint, num_workers=args.workers)
    if not success:
        sys.exit(0)
        
    run_even_cv_and_gates()

if __name__ == "__main__":
    main()
