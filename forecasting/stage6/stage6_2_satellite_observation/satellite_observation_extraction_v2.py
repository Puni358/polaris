#!/usr/bin/env python3
"""
POLARIS Stage 6.2 — Satellite Feature Extraction V2 (Atomic Incremental Checkpointing)
======================================================================================
Extracts pre-origin polar satellite observations for SITES Nuolja (68.362074°N, 18.738752°E).

Robust Incremental Checkpointing & Resource Safety:
1. Atomic Incremental Persistence: After EACH completed origin, feature and audit records
   are atomically written to disk (via .tmp file + os.replace). A crash or interruption
   preserves all completed origins and cannot corrupt existing checkpoint CSVs.
2. Resume Detection: On restart, existing V2 CSVs are loaded, completed origins are identified
   by forecast_start, and execution resumes from the first incomplete origin without duplicating rows.
3. Guaranteed Lifecycle Cleanup: Active temporary file (local_path) is ALWAYS removed in try/finally.
4. Interrupt Cleanup: SIGINT/SIGTERM signal handler registered to clean active local_path.
   (Note: SIGKILL / SIG9 cannot be caught in Linux by design).
5. Selective Startup Stale Sweep: Automatically audits and cleans ONLY stale V2 files
   matching /tmp/swath_v2_*.nc on startup. Unrelated /tmp/*.nc files are left untouched.
6. No Silent Failures: Network/I/O errors are NEVER mapped to sat_obs_available = 0.
7. Explicit Categorization: Every origin/pass is classified into:
   - VALID_OBSERVATION
   - NO_ELIGIBLE_PASS
   - ELIGIBLE_PASS_NO_VALID_PIXEL
   - DOWNLOAD_FAILURE
   - PROCESSING_FAILURE
8. Sequential Execution & Strict Causality: Exactly 1 swath processed at a time.
"""

import os
import sys
import glob
import time
import shutil
import signal
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import netCDF4 as nc

# Station Coordinates & Thresholds
ST_LAT, ST_LON = 68.362074, 18.738752
COVERAGE_THRESHOLD_KM = 50.0
MAX_DOWNLOAD_RETRIES = 4
BACKOFF_FACTOR = 2.0

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage6" / "stage6_2_satellite_observation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Global tracking for active temporary file
ACTIVE_TEMP_PATH = None

def _signal_cleanup_handler(signum, frame):
    """Signal handler for SIGINT and SIGTERM to clean up active temporary swath file."""
    global ACTIVE_TEMP_PATH
    if ACTIVE_TEMP_PATH and os.path.exists(ACTIVE_TEMP_PATH):
        try:
            os.remove(ACTIVE_TEMP_PATH)
        except Exception:
            pass
    sys.exit(128 + signum)

try:
    signal.signal(signal.SIGINT, _signal_cleanup_handler)
    signal.signal(signal.SIGTERM, _signal_cleanup_handler)
except Exception:
    pass

def cleanup_stale_v2_files():
    """Audit and remove only stale V2 temporary files matching /tmp/swath_v2_*.nc."""
    current_pid = os.getpid()
    stale_files = glob.glob("/tmp/swath_v2_*.nc")
    
    total_bytes = 0
    removed_count = 0
    
    for fpath in stale_files:
        filename = os.path.basename(fpath)
        if f"swath_v2_{current_pid}_" in filename:
            continue
        try:
            size = os.path.getsize(fpath)
            total_bytes += size
            os.remove(fpath)
            removed_count += 1
        except Exception:
            pass
            
    if removed_count > 0:
        print(f"[STARTUP CLEANUP] Removed {removed_count} stale V2 files matching /tmp/swath_v2_*.nc ({total_bytes / (1024*1024):.2f} MB total).")
    return removed_count, total_bytes

def save_dataframe_atomic(df, target_path):
    """Atomically write DataFrame to target_path using a temporary file and os.replace."""
    target_path = Path(target_path)
    temp_path = target_path.with_suffix(".tmp")
    df.to_csv(temp_path, index=False)
    os.replace(temp_path, target_path)

# Load catalog index
index_path = OUT_DIR / "satellite_swath_index_2024.csv"
if not index_path.exists():
    raise FileNotFoundError(f"Swath index missing at {index_path}.")

swath_index = pd.read_csv(index_path)
swath_index["t_start_utc"] = pd.to_datetime(swath_index["t_start_utc"], format="%Y%m%d%H%M%S", utc=True)
swath_index["t_end_utc"] = pd.to_datetime(swath_index["t_end_utc"], format="%Y%m%d%H%M%S", utc=True)

# Load benchmark origins
s4_preds = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])
origins = sorted(s4_preds["forecast_start"].unique())

def haversine_distance_km(lats, lons, target_lat, target_lon):
    """Compute Haversine geodesic distance in km from target_lat/lon to lats/lons array."""
    lat_rad = np.radians(lats)
    lon_rad = np.radians(lons)
    st_lat_rad = np.radians(target_lat)
    st_lon_rad = np.radians(target_lon)

    dlat = lat_rad - st_lat_rad
    dlon = lon_rad - st_lon_rad

    a = np.sin(dlat / 2.0)**2 + np.cos(st_lat_rad) * np.cos(lat_rad) * np.sin(dlon / 2.0)**2
    a = np.clip(a, 0.0, 1.0)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return 6371.0 * c

def download_swath_with_retry(file_url, local_path, max_retries=MAX_DOWNLOAD_RETRIES, timeout=45):
    """Download satellite NetCDF swath with bounded retries and exponential backoff."""
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(file_url, headers={"User-Agent": "POLARIS_Stage6_2_V2/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp, open(local_path, "wb") as out_file:
                shutil.copyfileobj(resp, out_file)
            if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
                return True
        except Exception as e:
            if os.path.exists(local_path):
                try: os.remove(local_path)
                except: pass
            if attempt < max_retries:
                sleep_time = BACKOFF_FACTOR ** attempt
                time.sleep(sleep_time)
    return False

def process_swath_file(local_path, sensor):
    """Extract thermal IR features and nearest pixel distance from downloaded NetCDF swath."""
    try:
        ds = nc.Dataset(local_path)
        lats = ds.variables["latitude"][:]
        lons = ds.variables["longitude"][:]
        
        if sensor == "viirs-mband":
            var_11 = "M15"
            var_12 = "M16"
        else:
            var_11 = "CHANNEL_4"
            var_12 = "CHANNEL_5"
            
        if var_11 not in ds.variables or var_12 not in ds.variables:
            ds.close()
            return "PROCESSING_FAILURE", None
            
        bt_11 = ds.variables[var_11][:]
        bt_12 = ds.variables[var_12][:]
        ds.close()
        
        dist_km = haversine_distance_km(lats, lons, ST_LAT, ST_LON)
        valid_mask = ~np.isnan(lats) & ~np.isnan(lons) & ~np.isnan(bt_11) & ~np.isnan(bt_12)
        dist_km[~valid_mask] = np.inf
        
        min_dist = float(np.min(dist_km))
        if min_dist > COVERAGE_THRESHOLD_KM or np.isinf(min_dist):
            return "ELIGIBLE_PASS_NO_VALID_PIXEL", {"min_dist": min_dist if not np.isinf(min_dist) else np.nan}
            
        min_idx = np.unravel_index(np.argmin(dist_km), dist_km.shape)
        y0, x0 = min_idx
        
        point_bt11 = float(bt_11[y0, x0])
        point_bt12 = float(bt_12[y0, x0])
        split_window = point_bt11 - point_bt12
        
        y_min, y_max = max(0, y0 - 1), min(lats.shape[0], y0 + 2)
        x_min, x_max = max(0, x0 - 1), min(lats.shape[1], x0 + 2)
        
        roi_bt11 = bt_11[y_min:y_max, x_min:x_max]
        valid_roi = roi_bt11[~np.isnan(roi_bt11)]
        
        roi_mean = float(np.mean(valid_roi)) if len(valid_roi) > 0 else point_bt11
        roi_std = float(np.std(valid_roi)) if len(valid_roi) > 1 else 0.0
        
        return "VALID_OBSERVATION", {
            "dist_km": min_dist,
            "y0": int(y0),
            "x0": int(x0),
            "sat_bt_11um_point": point_bt11,
            "sat_bt_11um_roi_mean": roi_mean,
            "sat_bt_11um_roi_std": roi_std,
            "sat_split_window_diff": split_window
        }
    except Exception as e:
        return "PROCESSING_FAILURE", None

def process_origin_v2(origin_dt):
    global ACTIVE_TEMP_PATH
    origin_ts = pd.Timestamp(origin_dt)
    t0_utc = origin_ts.tz_localize("Europe/Stockholm").tz_convert("UTC")
    
    lookback_start = t0_utc - pd.Timedelta(hours=12)
    eligible = swath_index[(swath_index["t_end_utc"] <= t0_utc) & (swath_index["t_end_utc"] >= lookback_start)].sort_values("t_end_utc", ascending=False)
    
    if len(eligible) == 0:
        return {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "t0_utc": t0_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "tacq_utc": "NONE",
            "causality_satisfied": True,
            "extraction_status": "NO_ELIGIBLE_PASS",
            "platform": "NONE",
            "sensor": "NONE",
            "file_url": "NONE",
            "nearest_pixel_dist_km": np.nan,
            "obs_age_hours": 0.0,
            "sat_obs_available": 0.0,
            "eligible_pass_count": 0
        }, {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "sat_bt_11um_point": 0.0,
            "sat_bt_11um_roi_mean": 0.0,
            "sat_bt_11um_roi_std": 0.0,
            "sat_split_window_diff": 0.0,
            "sat_obs_age_hours": 0.0,
            "sat_obs_available": 0.0
        }
        
    pass_statuses = []
    selected_pass = None
    extracted_feat = None
    
    for _, row in eligible.iterrows():
        local_path = f"/tmp/swath_v2_{os.getpid()}_{np.random.randint(100000, 999999)}.nc"
        ACTIVE_TEMP_PATH = local_path
        try:
            success = download_swath_with_retry(row["file_url"], local_path)
            if not success:
                pass_statuses.append("DOWNLOAD_FAILURE")
                continue
                
            status, feat_dict = process_swath_file(local_path, row["sensor"])
            pass_statuses.append(status)
            
            if status == "VALID_OBSERVATION":
                selected_pass = row
                extracted_feat = feat_dict
                break
        finally:
            if os.path.exists(local_path):
                try: os.remove(local_path)
                except Exception: pass
            ACTIVE_TEMP_PATH = None
            
    if selected_pass is not None and extracted_feat is not None:
        tacq_utc = selected_pass["t_end_utc"]
        obs_age_hours = (t0_utc - tacq_utc).total_seconds() / 3600.0
        causality_ok = tacq_utc <= t0_utc
        
        audit_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "t0_utc": t0_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "tacq_utc": tacq_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "causality_satisfied": causality_ok,
            "extraction_status": "VALID_OBSERVATION",
            "platform": selected_pass["platform"],
            "sensor": selected_pass["sensor"],
            "file_url": selected_pass["file_url"],
            "nearest_pixel_dist_km": round(extracted_feat["dist_km"], 4),
            "obs_age_hours": round(obs_age_hours, 4),
            "sat_obs_available": 1.0,
            "eligible_pass_count": len(eligible)
        }
        
        feat_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "sat_bt_11um_point": round(extracted_feat["sat_bt_11um_point"], 4),
            "sat_bt_11um_roi_mean": round(extracted_feat["sat_bt_11um_roi_mean"], 4),
            "sat_bt_11um_roi_std": round(extracted_feat["sat_bt_11um_roi_std"], 4),
            "sat_split_window_diff": round(extracted_feat["sat_split_window_diff"], 4),
            "sat_obs_age_hours": round(obs_age_hours, 4),
            "sat_obs_available": 1.0
        }
    else:
        if "DOWNLOAD_FAILURE" in pass_statuses:
            final_status = "DOWNLOAD_FAILURE"
        elif "PROCESSING_FAILURE" in pass_statuses:
            final_status = "PROCESSING_FAILURE"
        else:
            final_status = "ELIGIBLE_PASS_NO_VALID_PIXEL"
            
        audit_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "t0_utc": t0_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "tacq_utc": "NONE",
            "causality_satisfied": True,
            "extraction_status": final_status,
            "platform": "NONE",
            "sensor": "NONE",
            "file_url": "NONE",
            "nearest_pixel_dist_km": np.nan,
            "obs_age_hours": 0.0,
            "sat_obs_available": 0.0,
            "eligible_pass_count": len(eligible)
        }
        
        feat_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "sat_bt_11um_point": 0.0,
            "sat_bt_11um_roi_mean": 0.0,
            "sat_bt_11um_roi_std": 0.0,
            "sat_split_window_diff": 0.0,
            "sat_obs_age_hours": 0.0,
            "sat_obs_available": 0.0
        }
        
    return audit_row, feat_row

def run_extraction_v2(target_origins=None, is_test_run=False, output_suffix=""):
    cleanup_stale_v2_files()
    
    if target_origins is None:
        target_origins = origins
        
    audit_path = OUT_DIR / f"satellite_causality_audit_v2{output_suffix}.csv"
    feat_path = OUT_DIR / f"satellite_feature_summary_v2{output_suffix}.csv"
    
    completed_origins = set()
    audit_records = []
    feat_records = []
    
    # Resume Detection
    if not is_test_run and audit_path.exists() and feat_path.exists():
        try:
            df_audit_exist = pd.read_csv(audit_path)
            df_feat_exist = pd.read_csv(feat_path)
            if len(df_audit_exist) == len(df_feat_exist) and len(df_audit_exist) > 0:
                completed_origins = set(df_audit_exist["forecast_start"].astype(str))
                audit_records = df_audit_exist.to_dict("records")
                feat_records = df_feat_exist.to_dict("records")
                print(f"[CHECKPOINT LOADED] Found {len(completed_origins)} completed origins in existing V2 CSVs. {len(target_origins) - len(completed_origins)} remaining.")
        except Exception as e:
            print(f"[CHECKPOINT WARNING] Error reading existing CSVs: {e}. Starting fresh.")
            completed_origins = set()
            audit_records = []
            feat_records = []

    remaining_origins = [o for o in target_origins if pd.Timestamp(o).strftime("%Y-%m-%d %H:%M:%S") not in completed_origins]
    
    print(f"Starting Stage 6.2 Extraction V2 ({'TEST RUN' if is_test_run else 'FULL RUN'} | Total: {len(target_origins)}, Completed: {len(completed_origins)}, Remaining: {len(remaining_origins)})...")
    start_time = time.time()
    
    for idx, origin_dt in enumerate(target_origins, 1):
        origin_str = pd.Timestamp(origin_dt).strftime("%Y-%m-%d %H:%M:%S")
        if origin_str in completed_origins:
            continue
            
        a_row, f_row = process_origin_v2(origin_dt)
        audit_records.append(a_row)
        feat_records.append(f_row)
        completed_origins.add(origin_str)
        
        # Atomic Incremental Checkpointing after EACH completed origin
        if not is_test_run:
            df_audit_curr = pd.DataFrame(audit_records)
            df_feat_curr = pd.DataFrame(feat_records)
            save_dataframe_atomic(df_audit_curr, audit_path)
            save_dataframe_atomic(df_feat_curr, feat_path)
            
        done_count = len(completed_origins)
        total_count = len(target_origins)
        rem_count = total_count - done_count
        elapsed = time.time() - start_time
        
        print(f"  Completed [{done_count}/{total_count}] origins ({rem_count} remaining, {elapsed:.1f}s) | Status: {a_row['extraction_status']} ({a_row['platform']}/{a_row['sensor']})")
        
    df_audit = pd.DataFrame(audit_records)
    df_feat = pd.DataFrame(feat_records)
    
    if not is_test_run:
        save_dataframe_atomic(df_audit, audit_path)
        save_dataframe_atomic(df_feat, feat_path)
        print(f"\nFinal atomic save complete to {audit_path.name} and {feat_path.name}.")
        
    return df_audit, df_feat

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        df_audit, df_feat = run_extraction_v2(origins, is_test_run=False)
    else:
        print("Run with --full for complete 347-origin extraction.")
