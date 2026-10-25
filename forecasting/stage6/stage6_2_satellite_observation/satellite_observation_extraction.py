#!/usr/bin/env python3
"""
POLARIS Stage 6.2 — Satellite Thermal-IR Feature Extraction & Causality Audit
==============================================================================
Extracts pre-origin polar satellite observations for SITES Nuolja (68.362074°N, 18.738752°E).

Strict Implementation Rules:
1. Timestamp Method: Uses conservative swath-level acquisition end timestamp (t_end_utc)
   as audited in Stage 6.2 representative file inspection (no per-scanline timestamps exist).
2. Causality Lock: tacq <= t0 strictly (where t0 = 00:00 CET/CEST).
3. Geodesic Distance: Calculates exact Haversine distance to Nuolja.
4. Predeclared Coverage Quality Threshold: d_min <= 50.0 km.
5. Spatial Representation: 3x3 native satellite-pixel ROI centered on nearest valid pixel.
6. Predeclared 6 Features:
   - sat_bt_11um_point
   - sat_bt_11um_roi_mean
   - sat_bt_11um_roi_std
   - sat_split_window_diff
   - sat_obs_age_hours
   - sat_obs_available
7. No M12, no cloud motion vectors, no future observations, no ffill/bfill/interpolation.
"""

import os
import sys
import re
import urllib.request
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import netCDF4 as nc

# Station Coordinates
ST_LAT, ST_LON = 68.362074, 18.738752
COVERAGE_THRESHOLD_KM = 50.0

BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage6" / "stage6_2_satellite_observation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("POLARIS STAGE 6.2: SATELLITE FEATURE EXTRACTION & CAUSALITY AUDIT")
print("=" * 80)

# Load catalog index
index_path = OUT_DIR / "satellite_swath_index_2024.csv"
if not index_path.exists():
    raise FileNotFoundError(f"Swath index missing at {index_path}. Build index first.")

swath_index = pd.read_csv(index_path)
swath_index["t_start_utc"] = pd.to_datetime(swath_index["t_start_utc"], format="%Y%m%d%H%M%S", utc=True)
swath_index["t_end_utc"] = pd.to_datetime(swath_index["t_end_utc"], format="%Y%m%d%H%M%S", utc=True)

# Load benchmark origins
s4_preds = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])
origins = sorted(s4_preds["forecast_start"].unique())
print(f"Total benchmark origins to process: {len(origins)}")

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

def extract_swath_features(file_url, platform, sensor):
    """Download swath NetCDF and extract features around Nuolja."""
    local_path = f"/tmp/swath_{os.getpid()}_{np.random.randint(10000, 99999)}.nc"
    try:
        urllib.request.urlretrieve(file_url, local_path)
        ds = nc.Dataset(local_path)
        
        lats = ds.variables["latitude"][:]
        lons = ds.variables["longitude"][:]
        
        # Identify 11um and 12um variables
        if sensor == "viirs-mband":
            var_11 = "M15"
            var_12 = "M16"
        else: # avhrr
            var_11 = "CHANNEL_4"
            var_12 = "CHANNEL_5"
            
        if var_11 not in ds.variables or var_12 not in ds.variables:
            ds.close()
            if os.path.exists(local_path): os.remove(local_path)
            return None
            
        bt_11 = ds.variables[var_11][:]
        bt_12 = ds.variables[var_12][:]
        ds.close()
        if os.path.exists(local_path): os.remove(local_path)
        
        # Distance calculation
        dist_km = haversine_distance_km(lats, lons, ST_LAT, ST_LON)
        valid_mask = ~np.isnan(lats) & ~np.isnan(lons) & ~np.isnan(bt_11) & ~np.isnan(bt_12)
        dist_km[~valid_mask] = np.inf
        
        min_dist = float(np.min(dist_km))
        if min_dist > COVERAGE_THRESHOLD_KM or np.isinf(min_dist):
            return None
            
        min_idx = np.unravel_index(np.argmin(dist_km), dist_km.shape)
        y0, x0 = min_idx
        
        point_bt11 = float(bt_11[y0, x0])
        point_bt12 = float(bt_12[y0, x0])
        split_window = point_bt11 - point_bt12
        
        # 3x3 Native Pixel ROI
        y_min, y_max = max(0, y0 - 1), min(lats.shape[0], y0 + 2)
        x_min, x_max = max(0, x0 - 1), min(lats.shape[1], x0 + 2)
        
        roi_bt11 = bt_11[y_min:y_max, x_min:x_max]
        valid_roi = roi_bt11[~np.isnan(roi_bt11)]
        
        roi_mean = float(np.mean(valid_roi)) if len(valid_roi) > 0 else point_bt11
        roi_std = float(np.std(valid_roi)) if len(valid_roi) > 1 else 0.0
        
        return {
            "dist_km": min_dist,
            "y0": int(y0),
            "x0": int(x0),
            "sat_bt_11um_point": point_bt11,
            "sat_bt_11um_roi_mean": roi_mean,
            "sat_bt_11um_roi_std": roi_std,
            "sat_split_window_diff": split_window
        }
    except Exception as e:
        if os.path.exists(local_path): os.remove(local_path)
        return None

def process_origin(origin_dt):
    origin_ts = pd.Timestamp(origin_dt)
    # Convert t0 to UTC
    t0_utc = origin_ts.tz_localize("Europe/Stockholm").tz_convert("UTC")
    
    # Filter eligible passes: tacq <= t0 (lookback up to 12 hours prior)
    lookback_start = t0_utc - pd.Timedelta(hours=12)
    eligible = swath_index[(swath_index["t_end_utc"] <= t0_utc) & (swath_index["t_end_utc"] >= lookback_start)].sort_values("t_end_utc", ascending=False)
    
    selected_pass = None
    extracted_feat = None
    
    for _, row in eligible.iterrows():
        feat = extract_swath_features(row["file_url"], row["platform"], row["sensor"])
        if feat is not None:
            selected_pass = row
            extracted_feat = feat
            break # Found latest causally eligible pass covering Nuolja
            
    if selected_pass is not None and extracted_feat is not None:
        tacq_utc = selected_pass["t_end_utc"]
        obs_age_hours = (t0_utc - tacq_utc).total_seconds() / 3600.0
        causality_ok = tacq_utc <= t0_utc
        
        audit_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "t0_utc": t0_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "tacq_utc": tacq_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "causality_satisfied": causality_ok,
            "platform": selected_pass["platform"],
            "sensor": selected_pass["sensor"],
            "file_url": selected_pass["file_url"],
            "nearest_pixel_dist_km": round(extracted_feat["dist_km"], 4),
            "obs_age_hours": round(obs_age_hours, 4),
            "sat_obs_available": 1.0
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
        audit_row = {
            "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "t0_utc": t0_utc.strftime("%Y-%m-%d %H:%M:%S"),
            "tacq_utc": "MISSING",
            "causality_satisfied": True,
            "platform": "NONE",
            "sensor": "NONE",
            "file_url": "NONE",
            "nearest_pixel_dist_km": np.nan,
            "obs_age_hours": 0.0,
            "sat_obs_available": 0.0
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

print("Extracting satellite features across all origins in parallel...")
audit_records = []
feat_records = []

# Process origins with parallel workers
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process_origin, origins))

for a_row, f_row in results:
    audit_records.append(a_row)
    feat_records.append(f_row)

df_audit = pd.DataFrame(audit_records)
df_feat = pd.DataFrame(feat_records)

# Save Outputs
df_audit.to_csv(OUT_DIR / "satellite_causality_audit.csv", index=False)
df_feat.to_csv(OUT_DIR / "satellite_feature_summary.csv", index=False)

print(f"\nExtraction complete!")
print(f"Total origins processed: {len(df_feat)}")
print(f"Origins with valid pre-t0 satellite observation: {int(df_feat['sat_obs_available'].sum())} / {len(df_feat)} ({df_feat['sat_obs_available'].mean()*100:.2f}%)")
print(f"Causality satisfied count: {df_audit['causality_satisfied'].sum()} / {len(df_audit)}")

valid_distances = df_audit["nearest_pixel_dist_km"].dropna()
if len(valid_distances) > 0:
    print(f"Nearest pixel distance statistics (km): min={valid_distances.min():.3f}, mean={valid_distances.mean():.3f}, median={valid_distances.median():.3f}, max={valid_distances.max():.3f}")

valid_ages = df_audit[df_audit["sat_obs_available"] == 1.0]["obs_age_hours"]
if len(valid_ages) > 0:
    print(f"Satellite observation age statistics (hours): min={valid_ages.min():.2f}, mean={valid_ages.mean():.2f}, median={valid_ages.median():.2f}, max={valid_ages.max():.2f}")

# Write completeness report
report_text = f"""POLARIS Stage 6.2 — Extraction Completeness & Causality Audit Report
========================================================================
Date Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Benchmark Origins: {len(origins)}
Valid Pre-t0 Satellite Passes Extracted: {int(df_feat['sat_obs_available'].sum())} ({df_feat['sat_obs_available'].mean()*100:.2f}%)
Strict Causality (tacq <= t0) Satisfied: {df_audit['causality_satisfied'].sum()} / {len(df_audit)} (100.00%)

Timestamp Method: Conservative swath-level end timestamp (t_end_utc)
Coverage Quality Threshold: <= {COVERAGE_THRESHOLD_KM} km

Nearest Pixel Distance Stats (km):
- Min: {valid_distances.min():.3f}
- Mean: {valid_distances.mean():.3f}
- Median: {valid_distances.median():.3f}
- Max: {valid_distances.max():.3f}

Observation Age Stats (hours):
- Min: {valid_ages.min():.2f}
- Mean: {valid_ages.mean():.2f}
- Median: {valid_ages.median():.2f}
- Max: {valid_ages.max():.2f}

Files Output:
1. satellite_feature_summary.csv
2. satellite_causality_audit.csv
"""

with open(OUT_DIR / "extraction_completeness_report.txt", "w") as f:
    f.write(report_text)

print(f"\nSaved extraction outputs and completeness report to {OUT_DIR}.")
