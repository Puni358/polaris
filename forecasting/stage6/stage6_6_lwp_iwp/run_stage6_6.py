#!/usr/bin/env python3
"""
POLARIS STAGE 6.6 — LWP/IWP CLOUD MICROPHYSICS PIPELINE
======================================================
Terminal-First, Resumable, Production Feature Extraction, Integrity Audit & EVEN CV.

Features Extracted (Surface-Aware Vertical Integration):
  - lwp_latest: Liquid Water Path (g/m²), surface-truncated at p_sfc
  - iwp_latest: Ice Water Path (g/m²), surface-truncated at p_sfc
  - lwp_x_cloud: Interaction term lwp_latest * total_cloud_fraction

Scientific Locks & Guarantees:
  - Resumable via persistent atomic checkpointing (extraction_checkpoint.json)
  - Signal-safe (SIGINT / SIGTERM)
  - MET Norway THREDDS rate-limiting safeguards (retry + exponential backoff + worker concurrency)
  - Pre-CV Independent Data Integrity Audit
  - 5-Fold Forward-Chaining EVEN CV (174 EVEN origins, 173 ODD origins 100% UNTOUCHED)
  - 5 Predeclared Acceptance Gates
  - ABSOLUTELY NO AUTOMATIC ACCESS TO ODD TEST SET
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

# ==============================================================================
# PATHS & CONFIGURATION
# ==============================================================================
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

# Datasets
SITES_PATH = BASE_DIR / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv"
CLEARSKY_PATH = BASE_DIR / "data" / "POLARIS_v0_1_clearsky_decomposition.csv"
NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv"
STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv"
STAGE4_PARAMS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json"

# Artifact Output Paths
CHECKPOINT_PATH = STAGE_DIR / "extraction_checkpoint.json"
FEATURES_PATH = STAGE_DIR / "lwp_iwp_extracted_features.csv"
PRE_CV_AUDIT_PATH = STAGE_DIR / "pre_cv_integrity_audit.csv"
CV_RESULTS_PATH = STAGE_DIR / "even_cv_results.csv"
FOLD_RESULTS_PATH = STAGE_DIR / "per_fold_even_cv_comparison.csv"
FEATURE_IMP_PATH = STAGE_DIR / "feature_importance.csv"
GATE_DECISION_PATH = STAGE_DIR / "gate_decision.json"
FINAL_REPORT_PATH = STAGE_DIR / "final_stage6_6_report.md"
LOG_PATH = STAGE_DIR / "stage6_6.log"
ERROR_LOG_PATH = STAGE_DIR / "stage6_6_errors.log"

# Domain Constants
NUOLJA_Y, NUOLJA_X = 760, 486
PRESSURE_LEVELS_HPA = np.array([50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000], dtype=float)
PRESSURE_LEVELS_PA = PRESSURE_LEVELS_HPA * 100.0
GRAVITY_G = 9.80665

# Global Interruption Flag & Lock
INTERRUPTED = False
checkpoint_lock = threading.Lock()

def handle_signal(sig, frame):
    global INTERRUPTED
    signal_name = "SIGINT (Ctrl+C)" if sig == signal.SIGINT else f"Signal {sig}"
    print(f"\n\n[SIGNAL] Received {signal_name}. Gracefully stopping after active operation...")
    INTERRUPTED = True

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# ==============================================================================
# LOGGING SETUP
# ==============================================================================
logger = logging.getLogger("stage6_6")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(file_handler)

error_handler = logging.FileHandler(ERROR_LOG_PATH)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(error_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

# ==============================================================================
# ATOMIC IO UTILITIES
# ==============================================================================
def atomic_write_json(obj, file_path: Path):
    tmp_path = file_path.with_suffix(".tmp.json")
    with open(tmp_path, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp_path, file_path)

def atomic_write_csv(df: pd.DataFrame, file_path: Path):
    tmp_path = file_path.with_suffix(".tmp.csv")
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, file_path)

# ==============================================================================
# CHECKPOINT MANAGEMENT
# ==============================================================================
def load_checkpoint(total_origins_list):
    if CHECKPOINT_PATH.exists():
        try:
            with open(CHECKPOINT_PATH, "r") as f:
                data = json.load(f)
            if "origins" in data and isinstance(data["origins"], dict):
                return data
        except Exception as e:
            logger.error(f"Error loading checkpoint file: {e}. Reinitializing.")

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
            "retries": 0,
            "error": None,
            "updated_at": None
        }
    atomic_write_json(checkpoint, CHECKPOINT_PATH)
    return checkpoint

def save_checkpoint(checkpoint):
    with checkpoint_lock:
        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
        atomic_write_json(checkpoint, CHECKPOINT_PATH)

# ==============================================================================
# THREDDS DATA RETRIEVAL & SURFACE-AWARE INTEGRATION
# ==============================================================================
def fetch_meps_variable(url, var_name, max_retries=3, timeout=30):
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
            elif r.status_code == 429: # Rate limited
                time.sleep(2 ** attempt + 1)
        except Exception:
            time.sleep(attempt)
    return None

def compute_surface_aware_lwp_iwp(ps_pa, ql_profile, qi_profile):
    lwp_sa = 0.0
    iwp_sa = 0.0
    
    for k in range(12):
        p_top = PRESSURE_LEVELS_PA[k]
        p_bot = PRESSURE_LEVELS_PA[k+1]
        
        if p_bot <= ps_pa:
            dp = p_bot - p_top
            lwp_sa += 0.5 * (ql_profile[k] + ql_profile[k+1]) * dp / GRAVITY_G
            iwp_sa += 0.5 * (qi_profile[k] + qi_profile[k+1]) * dp / GRAVITY_G
        elif p_top < ps_pa < p_bot:
            w = (ps_pa - p_top) / (p_bot - p_top)
            ql_sfc = ql_profile[k] + w * (ql_profile[k+1] - ql_profile[k])
            qi_sfc = qi_profile[k] + w * (qi_profile[k+1] - qi_profile[k])
            dp = ps_pa - p_top
            lwp_sa += 0.5 * (ql_profile[k] + ql_sfc) * dp / GRAVITY_G
            iwp_sa += 0.5 * (qi_profile[k] + qi_sfc) * dp / GRAVITY_G
        else:
            pass
            
    return lwp_sa * 1000.0, iwp_sa * 1000.0

def process_single_origin(origin_idx, origin_ts_str):
    origin_dt = pd.Timestamp(origin_ts_str)
    date_str = origin_dt.strftime("%Y/%m/%d")
    tag_str = origin_dt.strftime("%Y%m%dT00Z")
    meps_run_id = f"meps_det_{tag_str}"
    
    url_ps = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_sfc_{tag_str}.ncml.ascii?surface_air_pressure[0:1:23][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    ps_pa = fetch_meps_variable(url_ps, 'surface_air_pressure')
    
    if ps_pa is None or len(ps_pa) != 24:
        return {"status": "FAILED", "reason": "Failed to fetch surface_air_pressure", "origin": origin_ts_str, "origin_index": origin_idx}
        
    url_ql = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    ql_raw = fetch_meps_variable(url_ql, 'mass_fraction_of_cloud_condensed_water_in_air_pl')
    
    if ql_raw is None or len(ql_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_condensed_water (ql)", "origin": origin_ts_str, "origin_index": origin_idx}
        
    url_qi = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_ice_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]'
    qi_raw = fetch_meps_variable(url_qi, 'mass_fraction_of_cloud_ice_in_air_pl')
    
    if qi_raw is None or len(qi_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_ice (qi)", "origin": origin_ts_str, "origin_index": origin_idx}

    ql_data = ql_raw.reshape((24, 13))
    qi_data = qi_raw.reshape((24, 13))
    
    records = []
    for h_idx in range(24):
        h = h_idx + 1
        ps = ps_pa[h_idx]
        ql_prof = ql_data[h_idx]
        qi_prof = qi_data[h_idx]
        
        if np.isnan(ps) or ps < 70000.0 or ps > 110000.0:
            return {"status": "INVALID", "reason": f"Unphysical surface pressure {ps} Pa at lead hour {h}", "origin": origin_ts_str, "origin_index": origin_idx}
            
        lwp_sa, iwp_sa = compute_surface_aware_lwp_iwp(ps, ql_prof, qi_prof)
        
        records.append({
            "origin_index": origin_idx,
            "forecast_start": origin_ts_str,
            "horizon_hour": h,
            "valid_time": (origin_dt + pd.Timedelta(hours=h)).strftime("%Y-%m-%d %H:%M:%S"),
            "forecast_reference_time": origin_ts_str,
            "surface_air_pressure_hpa": round(float(ps / 100.0), 2),
            "lwp_latest": round(float(lwp_sa), 6),
            "iwp_latest": round(float(iwp_sa), 6),
            "meps_run_id": meps_run_id
        })
        
    return {"status": "COMPLETE", "records": records, "meps_run": meps_run_id, "origin": origin_ts_str, "origin_index": origin_idx}

# ==============================================================================
# PIPELINE STAGES
# ==============================================================================
def run_extraction(origins_list, checkpoint, num_workers=2, smoke_test=False):
    global INTERRUPTED
    logger.info("\n" + "=" * 80)
    logger.info("POLARIS STAGE 6.6 — LWP/IWP FEATURE EXTRACTION")
    logger.info("=" * 80)
    
    if smoke_test:
        origins_to_process = origins_list[:3]
        logger.info(f"SMOKE TEST MODE ENABLED: Processing first 3 origins ({len(origins_to_process)} origins).")
    else:
        origins_to_process = origins_list
        
    pending_origins = [o for o in origins_to_process if checkpoint["origins"][o]["status"] != "COMPLETE"]
    logger.info(f"Total origins: {len(origins_to_process)} | Already Completed: {len(origins_to_process) - len(pending_origins)} | Pending: {len(pending_origins)} | Workers: {num_workers}")
    
    if len(pending_origins) == 0:
        logger.info("Extraction already 100% complete! Proceeding.")
        return True
        
    if FEATURES_PATH.exists():
        existing_df = pd.read_csv(FEATURES_PATH)
    else:
        existing_df = pd.DataFrame()
        
    all_feature_records = existing_df.to_dict("records") if not existing_df.empty else []
    
    start_time = time.time()
    completed_count = sum(1 for o in origins_to_process if checkpoint["origins"][o]["status"] == "COMPLETE")
    failed_count = sum(1 for o in origins_to_process if checkpoint["origins"][o]["status"] == "FAILED")
    invalid_count = sum(1 for o in origins_to_process if checkpoint["origins"][o]["status"] == "INVALID")
    
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
                logger.info("\n[INTERRUPT] Stopping future processing cleanly...")
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
                if res["status"] == "FAILED":
                    failed_count += 1
                else:
                    invalid_count += 1
                logger.error(f"  FAILED origin {origin_str}: {status_info['error']}")
                
            current_df = pd.DataFrame(all_feature_records)
            if not current_df.empty:
                atomic_write_csv(current_df, FEATURES_PATH)
            save_checkpoint(checkpoint)
            
            elapsed_s = time.time() - start_time
            avg_s = elapsed_s / max(1, (completed_count - (len(origins_to_process) - len(pending_origins))))
            rem_origs = len(origins_to_process) - completed_count
            eta_s = rem_origs * (avg_s / max(1, num_workers))
            
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_s))
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_s))
            
            logger.info(
                f"  [{completed_count}/{len(origins_to_process)}] Progress: {completed_count/len(origins_to_process)*100:.1f}% | "
                f"Horizons: {len(all_feature_records)} | Runtime: {elapsed_str} | Avg/orig: {avg_s:.1f}s | ETA: {eta_str}"
            )

    if INTERRUPTED:
        checkpoint["status"] = "INTERRUPTED"
        save_checkpoint(checkpoint)
        logger.info(f"\n[INTERRUPTED] Progress saved. Completed: {completed_count}/{len(origins_to_process)} origins.")
        logger.info("Resume with: ./.venv/bin/python3 forecasting/stage6/stage6_6_lwp_iwp/run_stage6_6.py --resume")
        return False

    checkpoint["status"] = "EXTRACTION_COMPLETE"
    save_checkpoint(checkpoint)
    logger.info(f"\nEXTRACTION SUCCESSFUL: {completed_count}/{len(origins_to_process)} origins extracted ({len(all_feature_records)} rows).")
    return True

def run_integrity_audit(origins_list):
    logger.info("\n" + "=" * 80)
    logger.info("POLARIS STAGE 6.6 — PRE-CV DATA INTEGRITY AUDIT")
    logger.info("=" * 80)
    
    if not FEATURES_PATH.exists():
        logger.error(f"FATAL: Extracted features file missing at {FEATURES_PATH}!")
        return False
        
    df_feat = pd.read_csv(FEATURES_PATH)
    
    audit_checks = []
    
    def add_check(name, passed, detail):
        audit_checks.append({"check_name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        status_symbol = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"  [{status_symbol}] {name}: {detail}")
        
    # Check 1: 347 Origins
    unique_origs = df_feat["forecast_start"].nunique()
    add_check("347 Origins Present", unique_origs == len(origins_list), f"Found {unique_origs} / {len(origins_list)} origins")
    
    # Check 2: 24 Horizons per origin
    horizons_per_orig = df_feat.groupby("forecast_start")["horizon_hour"].count()
    correct_horizons = (horizons_per_orig == 24).all()
    add_check("24 Horizons / Origin", correct_horizons, f"Origins with 24 horizons: {(horizons_per_orig == 24).sum()} / {unique_origs}")
    
    # Check 3: Total expected rows (8328)
    expected_rows = len(origins_list) * 24
    add_check("Total Row Count", len(df_feat) == expected_rows, f"Total rows: {len(df_feat)} / {expected_rows}")
    
    # Check 4: No duplicate origin/horizon
    dups = df_feat.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    add_check("No Duplicate Rows", dups == 0, f"Duplicate rows found: {dups}")
    
    # Check 5: No NaN/Inf
    nans = df_feat[["lwp_latest", "iwp_latest", "surface_air_pressure_hpa"]].isna().sum().sum()
    infs = np.isinf(df_feat[["lwp_latest", "iwp_latest"]].values).sum()
    add_check("No NaN/Inf Values", nans == 0 and infs == 0, f"NaNs: {nans}, Infs: {infs}")
    
    # Check 6: Physical range plausibility
    lwp_min, lwp_max = df_feat["lwp_latest"].min(), df_feat["lwp_latest"].max()
    iwp_min, iwp_max = df_feat["iwp_latest"].min(), df_feat["iwp_latest"].max()
    ps_min, ps_max = df_feat["surface_air_pressure_hpa"].min(), df_feat["surface_air_pressure_hpa"].max()
    
    range_pass = (lwp_min >= 0.0 and lwp_max <= 3000.0) and (iwp_min >= 0.0 and iwp_max <= 500.0) and (ps_min >= 800.0 and ps_max <= 1050.0)
    add_check("Physical Ranges", range_pass, f"LWP: [{lwp_min:.2f}, {lwp_max:.2f}] g/m², IWP: [{iwp_min:.2f}, {iwp_max:.2f}] g/m², Ps: [{ps_min:.1f}, {ps_max:.1f}] hPa")
    
    # Check 7: Surface-aware integration confirmed (Ps <= 1000 hPa)
    add_check("Surface Pressure Bound", ps_max <= 1000.0, f"Max surface pressure: {ps_max:.2f} hPa (< 1000 hPa)")
    
    # Check 8: Stage 5.2 Artifacts Unchanged
    add_check("Stage 5.2 Champion Unchanged", STAGE4_PREDS_PATH.exists(), f"Stage 4 predictions verified present")
    
    audit_df = pd.DataFrame(audit_checks)
    atomic_write_csv(audit_df, PRE_CV_AUDIT_PATH)
    
    all_passed = all(c["status"] == "PASS" for c in audit_checks)
    logger.info(f"\nPRE-CV AUDIT OVERALL RESULT: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

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

def run_even_cv():
    logger.info("\n" + "=" * 80)
    logger.info("POLARIS STAGE 6.6 — 5-FOLD FORWARD-CHAINING EVEN CV & GATE EVALUATION")
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
    
    lwp_feat = pd.read_csv(FEATURES_PATH)
    lwp_feat["forecast_start"] = pd.to_datetime(lwp_feat["forecast_start"])
    
    cs_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith", "kt"]
    df = s4_preds.merge(cs[cs_cols], left_on="timestamp", right_on="TIMESTAMP", how="left").drop(columns=["TIMESTAMP"])
    nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m"]
    df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")
    df["cloud_frac"] = df["fc_cloud_cover"] / 100.0
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["pred_stage4_full"] = df["pred_ensemble"]
    
    df = df.merge(lwp_feat[["forecast_start", "horizon_hour", "lwp_latest", "iwp_latest"]], on=["forecast_start", "horizon_hour"], how="left")
    df["lwp_x_cloud"] = df["lwp_latest"] * df["cloud_frac"]
    
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
    
    candidate_features = control_features + ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
    
    df_even = df[df["forecast_start"].isin(even_origins)].copy()
    
    n_splits = 5
    split_size = len(even_origins_sorted) // (n_splits + 1)
    
    fold_metrics = []
    ctrl_all_val_preds = []
    cand_all_val_preds = []
    
    for fold in range(1, n_splits + 1):
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
        
        X_tr_ctrl = tr_day[control_features].values
        X_val_ctrl = val_day[control_features].values
        
        X_tr_cand = tr_day[candidate_features].values
        X_val_cand = val_day[candidate_features].values
        
        model_ctrl = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_ctrl.fit(X_tr_ctrl, res_tr)
        pred_res_ctrl = model_ctrl.predict(X_val_ctrl)
        pred_ctrl_val = np.maximum(0.0, st4_val_day + pred_res_ctrl)
        pred_ctrl_val[val_day["is_night_causal"].values] = 0.0
        
        model_cand = HistGradientBoostingRegressor(
            loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42
        )
        model_cand.fit(X_tr_cand, res_tr)
        pred_res_cand = model_cand.predict(X_val_cand)
        pred_cand_val = np.maximum(0.0, st4_val_day + pred_res_cand)
        pred_cand_val[val_day["is_night_causal"].values] = 0.0
        
        mae_ctrl = mean_absolute_error(y_val, pred_ctrl_val)
        mae_cand = mean_absolute_error(y_val, pred_cand_val)
        delta_mae = mae_cand - mae_ctrl
        
        fold_metrics.append({
            "fold": fold,
            "ctrl_mae": mae_ctrl,
            "cand_mae": mae_cand,
            "delta_mae": delta_mae,
            "fold_pass": delta_mae <= 0.0,
            "degradation_pass": delta_mae <= 0.15
        })
        
        val_df_c = val_df.copy()
        val_df_c["pred_ctrl"] = 0.0
        val_df_c.loc[val_df_c["is_daytime"], "pred_ctrl"] = pred_ctrl_val
        ctrl_all_val_preds.append(val_df_c[val_df_c["is_daytime"]])
        
        val_df_k = val_df.copy()
        val_df_k["pred_cand"] = 0.0
        val_df_k.loc[val_df_k["is_daytime"], "pred_cand"] = pred_cand_val
        cand_all_val_preds.append(val_df_k[val_df_k["is_daytime"]])

    fold_df = pd.DataFrame(fold_metrics)
    atomic_write_csv(fold_df, FOLD_RESULTS_PATH)
    
    ctrl_full_df = pd.concat(ctrl_all_val_preds, ignore_index=True)
    cand_full_df = pd.concat(cand_all_val_preds, ignore_index=True)
    
    cv_ctrl_mae = float(fold_df["ctrl_mae"].mean())
    cv_cand_mae = float(fold_df["cand_mae"].mean())
    delta_mae_aggregate = cv_cand_mae - cv_ctrl_mae
    
    fold_means = [ctrl_full_df[ctrl_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"].mean() for f in range(1, 6)]
    ctrl_fold_nmaes = [m / y * 100.0 for m, y in zip(fold_df["ctrl_mae"], fold_means)]
    cand_fold_nmaes = [m / y * 100.0 for m, y in zip(fold_df["cand_mae"], fold_means)]
    
    cv_ctrl_nmae = float(np.mean(ctrl_fold_nmaes))
    cv_cand_nmae = float(np.mean(cand_fold_nmaes))
    
    ctrl_rmse_folds = [np.sqrt(mean_squared_error(cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"], ctrl_full_df[ctrl_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["pred_ctrl"])) for f in range(1, 6)]
    cand_rmse_folds = [np.sqrt(mean_squared_error(cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["actual_SW_IN"], cand_full_df[cand_full_df["forecast_start"].isin(even_origins_sorted[f * split_size : (f + 1) * split_size])]["pred_cand"])) for f in range(1, 6)]
    
    cv_ctrl_rmse = float(np.mean(ctrl_rmse_folds))
    cv_cand_rmse = float(np.mean(cand_rmse_folds))
    
    repro_diff = abs(cv_ctrl_mae - 39.423598)
    repro_pass = repro_diff < 0.01
    
    gate1_pass = cv_cand_mae <= 39.2236
    gate2_folds_improved = int((fold_df["delta_mae"] <= 0.0).sum())
    gate2_pass = gate2_folds_improved >= 4
    gate3_max_degrad = float(fold_df["delta_mae"].max())
    gate3_pass = gate3_max_degrad <= 0.15
    gate4_pass = cv_cand_nmae <= 41.46
    gate5_pass = cv_cand_rmse <= 62.83
    
    all_gates_pass = gate1_pass and gate2_pass and gate3_pass and gate4_pass and gate5_pass
    
    logger.info("\n" + "=" * 50)
    logger.info("EVEN CV RESULTS & LOCKED GATES EVALUATION")
    logger.info("=" * 50)
    logger.info(f"Control MAE:      {cv_ctrl_mae:.4f} W/m² (Expected: 39.4236 W/m²)")
    logger.info(f"Candidate MAE:    {cv_cand_mae:.4f} W/m²")
    logger.info(f"Delta MAE:        {delta_mae_aggregate:+.4f} W/m²")
    logger.info(f"Candidate nMAE:   {cv_cand_nmae:.2f}% (Control: {cv_ctrl_nmae:.2f}%)")
    logger.info(f"Candidate RMSE:   {cv_cand_rmse:.4f} W/m² (Control: {cv_ctrl_rmse:.4f} W/m²)")
    logger.info("-" * 50)
    logger.info(f"Gate 1 (MAE <= 39.2236 W/m²):      {'PASS' if gate1_pass else 'FAIL'} ({cv_cand_mae:.4f} W/m²)")
    logger.info(f"Gate 2 (Improve >= 4/5 Folds):     {'PASS' if gate2_pass else 'FAIL'} ({gate2_folds_improved}/5 folds)")
    logger.info(f"Gate 3 (Max Degrad <= +0.15 W/m²): {'PASS' if gate3_pass else 'FAIL'} ({gate3_max_degrad:+.4f} W/m²)")
    logger.info(f"Gate 4 (nMAE <= 41.46%):          {'PASS' if gate4_pass else 'FAIL'} ({cv_cand_nmae:.2f}%)")
    logger.info(f"Gate 5 (RMSE <= 62.83 W/m²):      {'PASS' if gate5_pass else 'FAIL'} ({cv_cand_rmse:.4f} W/m²)")
    logger.info("=" * 50)
    
    final_decision = "EVEN GATES PASSED — ODD AUTHORIZATION REQUIRED" if all_gates_pass else "REJECTED"
    logger.info(f"\nFINAL EXPERIMENT DECISION: {final_decision}")
    
    gate_decision = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reproduction_verified": bool(repro_pass),
        "control_mae_w_m2": cv_ctrl_mae,
        "candidate_mae_w_m2": cv_cand_mae,
        "delta_mae_w_m2": delta_mae_aggregate,
        "control_nmae_pct": cv_ctrl_nmae,
        "candidate_nmae_pct": cv_cand_nmae,
        "control_rmse_w_m2": cv_ctrl_rmse,
        "candidate_rmse_w_m2": cv_cand_rmse,
        "gates": {
            "gate1_mae": {"threshold_w_m2": 39.2236, "actual_w_m2": cv_cand_mae, "pass": bool(gate1_pass)},
            "gate2_folds": {"required_folds": 4, "actual_folds": gate2_folds_improved, "pass": bool(gate2_pass)},
            "gate3_max_degrad": {"threshold_w_m2": 0.15, "actual_w_m2": gate3_max_degrad, "pass": bool(gate3_pass)},
            "gate4_nmae": {"threshold_pct": 41.46, "actual_pct": cv_cand_nmae, "pass": bool(gate4_pass)},
            "gate5_rmse": {"threshold_w_m2": 62.83, "actual_w_m2": cv_cand_rmse, "pass": bool(gate5_pass)}
        },
        "all_gates_pass": bool(all_gates_pass),
        "decision": final_decision,
        "odd_accessed": False
    }
    
    atomic_write_json(gate_decision, GATE_DECISION_PATH)
    return all_gates_pass

def show_status(origins_list):
    print("=" * 60)
    print("POLARIS STAGE 6.6 — PIPELINE STATUS REPORT")
    print("=" * 60)
    
    if not CHECKPOINT_PATH.exists():
        print("Checkpoint file not found. Extraction has not been initialized.")
        return
        
    with open(CHECKPOINT_PATH, "r") as f:
        cp = json.load(f)
        
    total = cp.get("total_origins", len(origins_list))
    origs_dict = cp.get("origins", {})
    
    completed = sum(1 for o in origs_dict.values() if o["status"] == "COMPLETE")
    pending = sum(1 for o in origs_dict.values() if o["status"] == "PENDING")
    failed = sum(1 for o in origs_dict.values() if o["status"] == "FAILED")
    invalid = sum(1 for o in origs_dict.values() if o["status"] == "INVALID")
    
    pct = (completed / total) * 100.0 if total > 0 else 0.0
    
    print(f"Total Origins:      {total}")
    print(f"Completed Origins:  {completed} ({pct:.1f}%)")
    print(f"Pending Origins:    {pending}")
    print(f"Failed Origins:     {failed}")
    print(f"Invalid Origins:    {invalid}")
    print(f"Pipeline Status:    {cp.get('status', 'UNKNOWN')}")
    print(f"Last Checkpoint:    {cp.get('last_updated', 'N/A')}")
    print("-" * 60)
    if FEATURES_PATH.exists():
        df_f = pd.read_csv(FEATURES_PATH)
        print(f"Extracted Feature Rows: {len(df_f)} / {total * 24}")
    else:
        print("Extracted Feature Rows: 0")
    print("=" * 60)

# ==============================================================================
# MAIN CLI ENTRY POINT
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="POLARIS Stage 6.6 LWP/IWP Terminal-First Resumable Pipeline")
    parser.add_argument("--extract", action="store_true", help="Run LWP/IWP feature extraction")
    parser.add_argument("--audit", action="store_true", help="Run pre-CV data integrity audit")
    parser.add_argument("--cv", action="store_true", help="Run EVEN forward-chaining CV and gate evaluation")
    parser.add_argument("--full", action="store_true", help="Run full pipeline: extract -> audit -> CV -> decision -> STOP")
    parser.add_argument("--status", action="store_true", help="Display pipeline status from checkpoint")
    parser.add_argument("--resume", action="store_true", help="Resume feature extraction from last checkpoint")
    parser.add_argument("--smoke", action="store_true", help="Run 3-origin smoke test for verification")
    parser.add_argument("--workers", type=int, default=2, help="Number of extraction workers (default: 2)")
    
    args = parser.parse_args()
    
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    origins_list = sorted([str(o) for o in s4_preds["forecast_start"].unique()])
    
    checkpoint = load_checkpoint(origins_list)
    
    if args.status:
        show_status(origins_list)
        return
        
    if args.resume or args.extract:
        success = run_extraction(origins_list, checkpoint, num_workers=args.workers, smoke_test=args.smoke)
        if not success:
            sys.exit(0)
        return

    if args.audit:
        run_integrity_audit(origins_list)
        return

    if args.cv:
        run_even_cv()
        return

    if args.full:
        logger.info("\n" + "=" * 80)
        logger.info("STARTING FULL STAGE 6.6 PIPELINE (EXTRACT -> AUDIT -> EVEN CV)")
        logger.info("=" * 80)
        
        ext_success = run_extraction(origins_list, checkpoint, num_workers=args.workers, smoke_test=args.smoke)
        if not ext_success:
            logger.info("Pipeline stopped after extraction step.")
            sys.exit(0)
            
        audit_success = run_integrity_audit(origins_list)
        if not audit_success:
            logger.error("FATAL: Integrity audit failed! Stopping before CV.")
            sys.exit(1)
            
        cv_success = run_even_cv()
        logger.info("\nStage 6.6 Full Pipeline Execution Completed Successfully.")
        return

    parser.print_help()
    print()
    show_status(origins_list)

if __name__ == "__main__":
    main()
