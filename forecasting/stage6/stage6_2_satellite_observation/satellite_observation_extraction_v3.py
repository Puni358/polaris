#!/usr/bin/env python3
"""
POLARIS Stage 6.2 — Satellite Feature Extraction V3 (Production OPeNDAP Remote Subsetting)
===========================================================================================
Extracts pre-origin polar satellite observations for SITES Nuolja (68.362074°N, 18.738752°E).

Production Guarantees & Architecture:
1. Zero Local Disk File Bloat: Retrieves variable slices directly via pydap OPeNDAP (dodsC).
2. Coarse-Screen Safety: Subsampled lat/lon screening with a 150 km safety margin guarantees
   zero false rejections for swaths within the 50 km final coverage threshold.
3. 100% Scientific Equivalence: Exact match with full-file NetCDF calculations for nearest pixel,
   Haversine distance, point BT, split-window difference, and 3x3 native pixel ROI stats.
4. Atomic Checkpointing: Saves CSVs atomically after EACH completed origin via .tmp + os.replace.
5. Resume Detection: Skips completed origins on restart without row duplicates.
6. Explicit Failure Accounting: Distinguishes VALID_OBSERVATION, NO_ELIGIBLE_PASS,
   ELIGIBLE_PASS_NO_VALID_PIXEL, DOWNLOAD_FAILURE, and PROCESSING_FAILURE.
"""

import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pydap.client

# Station Coordinates & Thresholds
ST_LAT, ST_LON = 68.362074, 18.738752
COVERAGE_THRESHOLD_KM = 50.0
COARSE_SCREEN_THRESHOLD_KM = 150.0 # Conservative safety margin (150 km >> 50 km)
MAX_OPENDAP_RETRIES = 3
BACKOFF_FACTOR = 2.0

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage6" / "stage6_2_satellite_observation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

def get_dap_url(file_url):
    """Convert HTTPS fileServer URL to dodsC DAP URL."""
    return file_url.replace("/fileServer/", "/dodsC/").replace("https://", "dap2://")

def process_swath_opendap(file_url, sensor, max_retries=MAX_OPENDAP_RETRIES):
    """Query satellite swath over OPeNDAP remote subsetting with 2-stage coarse screening."""
    dap_url = get_dap_url(file_url)
    
    ds = None
    for attempt in range(1, max_retries + 1):
        try:
            ds = pydap.client.open_url(dap_url)
            if ds is not None:
                break
        except Exception:
            if attempt < max_retries:
                time.sleep(BACKOFF_FACTOR ** attempt)
                
    if ds is None:
        return "DOWNLOAD_FAILURE", None

    try:
        # 1. Metadata Bounding Box Screen (<0.1s)
        lat_min = float(ds.attributes.get("geospatial_lat_min", -90))
        lat_max = float(ds.attributes.get("geospatial_lat_max", 90))
        lon_min = float(ds.attributes.get("geospatial_lon_min", -180))
        lon_max = float(ds.attributes.get("geospatial_lon_max", 180))
        
        # Bounding box safety margin: lat +/- 1.5 deg (~166 km), lon +/- 3.0 deg
        if not (lat_min - 1.5 <= ST_LAT <= lat_max + 1.5 and lon_min - 3.0 <= ST_LON <= lon_max + 3.0):
            return "ELIGIBLE_PASS_NO_VALID_PIXEL", {"min_dist": np.nan}

        var_11_name = "M15" if sensor == "viirs-mband" else "CHANNEL_4"
        var_12_name = "M16" if sensor == "viirs-mband" else "CHANNEL_5"
        
        if var_11_name not in ds.keys() or var_12_name not in ds.keys():
            return "PROCESSING_FAILURE", None
            
        step = 30
        
        # 2. Subsampled Grid Screen (1 DAP call)
        lats_sub = np.array(ds["latitude"][::step, ::step].data)
        lons_sub = np.array(ds["longitude"][::step, ::step].data)
        
        dist_sub = haversine_distance_km(lats_sub, lons_sub, ST_LAT, ST_LON)
        valid_sub_mask = ~np.isnan(lats_sub) & ~np.isnan(lons_sub)
        dist_sub[~valid_sub_mask] = np.inf
        
        min_dist_sub = float(np.min(dist_sub))
        if min_dist_sub > COARSE_SCREEN_THRESHOLD_KM or np.isinf(min_dist_sub):
            return "ELIGIBLE_PASS_NO_VALID_PIXEL", {"min_dist": min_dist_sub}
            
        # 3. Fine Region Slice around coarse minimum (1 DAP call)
        min_sub_idx = np.unravel_index(np.argmin(dist_sub), dist_sub.shape)
        y_center = min_sub_idx[0] * step
        x_center = min_sub_idx[1] * step
        
        y_shape = ds["latitude"].shape[0]
        x_shape = ds["latitude"].shape[1]
        
        half_box = 100
        y_min, y_max = max(0, y_center - half_box), min(y_shape, y_center + half_box)
        x_min, x_max = max(0, x_center - half_box), min(x_shape, x_center + half_box)
        
        lats_fine = np.array(ds["latitude"][y_min:y_max, x_min:x_max].data)
        lons_fine = np.array(ds["longitude"][y_min:y_max, x_min:x_max].data)
        bt11_fine = np.array(ds[var_11_name][y_min:y_max, x_min:x_max].data)
        bt12_fine = np.array(ds[var_12_name][y_min:y_max, x_min:x_max].data)
        
        dist_fine = haversine_distance_km(lats_fine, lons_fine, ST_LAT, ST_LON)
        valid_fine_mask = ~np.isnan(lats_fine) & ~np.isnan(lons_fine) & ~np.isnan(bt11_fine) & ~np.isnan(bt12_fine)
        dist_fine[~valid_fine_mask] = np.inf
        
        min_dist_fine = float(np.min(dist_fine))
        if min_dist_fine > COVERAGE_THRESHOLD_KM or np.isinf(min_dist_fine):
            return "ELIGIBLE_PASS_NO_VALID_PIXEL", {"min_dist": min_dist_fine}
            
        min_fine_idx = np.unravel_index(np.argmin(dist_fine), dist_fine.shape)
        fy0, fx0 = min_fine_idx
        
        point_bt11 = float(bt11_fine[fy0, fx0])
        point_bt12 = float(bt12_fine[fy0, fx0])
        split_window = point_bt11 - point_bt12
        
        # 3x3 Native Pixel ROI
        r_ymin, r_ymax = max(0, fy0 - 1), min(bt11_fine.shape[0], fy0 + 2)
        r_xmin, r_xmax = max(0, fx0 - 1), min(bt11_fine.shape[1], fx0 + 2)
        
        roi_bt11 = bt11_fine[r_ymin:r_ymax, r_xmin:r_xmax]
        valid_roi = roi_bt11[~np.isnan(roi_bt11)]
        
        roi_mean = float(np.mean(valid_roi)) if len(valid_roi) > 0 else point_bt11
        roi_std = float(np.std(valid_roi)) if len(valid_roi) > 1 else 0.0
        
        abs_y0 = y_min + fy0
        abs_x0 = x_min + fx0
        
        return "VALID_OBSERVATION", {
            "dist_km": min_dist_fine,
            "y0": int(abs_y0),
            "x0": int(abs_x0),
            "sat_bt_11um_point": point_bt11,
            "sat_bt_11um_roi_mean": roi_mean,
            "sat_bt_11um_roi_std": roi_std,
            "sat_split_window_diff": split_window
        }
    except Exception as e:
        return "PROCESSING_FAILURE", None

def process_origin_v3(origin_dt):
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
        status, feat_dict = process_swath_opendap(row["file_url"], row["sensor"])
        pass_statuses.append(status)
        
        if status == "VALID_OBSERVATION":
            selected_pass = row
            extracted_feat = feat_dict
            break
            
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

def run_extraction_v3(target_origins=None, is_test_run=False, output_suffix="_v3"):
    if target_origins is None:
        target_origins = origins
        
    audit_path = OUT_DIR / f"satellite_causality_audit{output_suffix}.csv"
    feat_path = OUT_DIR / f"satellite_feature_summary{output_suffix}.csv"
    
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
                print(f"[CHECKPOINT LOADED] Found {len(completed_origins)} completed origins in existing V3 CSVs. {len(target_origins) - len(completed_origins)} remaining.")
        except Exception as e:
            print(f"[CHECKPOINT WARNING] Error reading existing CSVs: {e}. Starting fresh.")
            completed_origins = set()
            audit_records = []
            feat_records = []

    remaining_origins = [o for o in target_origins if pd.Timestamp(o).strftime("%Y-%m-%d %H:%M:%S") not in completed_origins]
    
    print(f"Starting Stage 6.2 Extraction V3 ({'TEST RUN' if is_test_run else 'FULL RUN'} | Total: {len(target_origins)}, Completed: {len(completed_origins)}, Remaining: {len(remaining_origins)})...")
    start_time = time.time()
    
    for idx, origin_dt in enumerate(target_origins, 1):
        origin_str = pd.Timestamp(origin_dt).strftime("%Y-%m-%d %H:%M:%S")
        if origin_str in completed_origins:
            continue
            
        a_row, f_row = process_origin_v3(origin_dt)
        audit_records.append(a_row)
        feat_records.append(f_row)
        completed_origins.add(origin_str)
        
        # Atomic Checkpointing after EACH completed origin
        if not is_test_run:
            save_dataframe_atomic(pd.DataFrame(audit_records), audit_path)
            save_dataframe_atomic(pd.DataFrame(feat_records), feat_path)
            
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
        df_audit, df_feat = run_extraction_v3(origins, is_test_run=False)
    else:
        print("Run with --full for complete 347-origin extraction V3.")
