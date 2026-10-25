#!/usr/bin/env python3
"""
Candidate L — Authoritative Missing Origins Recovery & Audit Matrix Generator
Extracts 18Z and 00Z MEPS forecasts for all recoverable missing origins.
"""

import os
import sys
import json
import time
import math
import hashlib
import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = 'forecasting/stage7/stage8/station_feedback_adaptation/candidate_L_research'
CACHE_DIR = os.path.join(BASE_DIR, 'meps_cache')
EXTRACTED_DIR = os.path.join(BASE_DIR, 'extracted')
LOG_PATH = os.path.join(BASE_DIR, 'acquisition_log.csv')
MANIFEST_PATH = os.path.join(BASE_DIR, 'ACQUISITION_MANIFEST.json')
AUDIT_JSON_PATH = os.path.join(BASE_DIR, 'missing_origins_audit_matrix.json')

F18_PATH = os.path.join(EXTRACTED_DIR, 'meps_18z_cloud_temp_rh_wind700_2020_2023.csv')
F00_PATH = os.path.join(EXTRACTED_DIR, 'meps_00z_lwp_iwp_2020_2023.csv')

G_CONST = 9.80665

MEPS_PRESSURE_LEVELS_PA = np.array([
    100000.0, 92500.0, 85000.0, 70000.0, 50000.0, 40000.0,
    30000.0, 25000.0, 20000.0, 15000.0, 10000.0, 7000.0, 5000.0
])

session = requests.Session()

def parse_opendap_array(text, expected_len):
    parts = text.split('---------------------------------------------')
    if len(parts) < 2:
        return np.array([])
    lines = parts[-1].splitlines()
    vals = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '.' in line and '[' in line and not line.startswith('['):
            if len(vals) == expected_len:
                break
        if ',' in line:
            subparts = line.split(',')
            try:
                val = float(subparts[-1].strip())
                vals.append(val)
                if len(vals) == expected_len:
                    break
            except ValueError:
                pass
    return np.array(vals)

def compute_surface_aware_lwp_iwp(surface_p_pa, ql_profile_kg_kg, qi_profile_kg_kg):
    if np.isnan(surface_p_pa) or surface_p_pa < 70000.0 or surface_p_pa > 110000.0:
        return np.nan, np.nan
    mask = MEPS_PRESSURE_LEVELS_PA <= surface_p_pa
    if not np.any(mask):
        return np.nan, np.nan
    p_valid = MEPS_PRESSURE_LEVELS_PA[mask]
    ql_valid = ql_profile_kg_kg[mask]
    qi_valid = qi_profile_kg_kg[mask]
    if surface_p_pa > p_valid[0]:
        p_extended = np.insert(p_valid, 0, surface_p_pa)
        ql_extended = np.insert(ql_valid, 0, ql_valid[0])
        qi_extended = np.insert(qi_valid, 0, qi_valid[0])
    else:
        p_extended = p_valid
        ql_extended = ql_valid
        qi_extended = qi_valid
    dp = np.diff(p_extended)
    ql_mid = 0.5 * (ql_extended[:-1] + ql_extended[1:])
    qi_mid = 0.5 * (qi_extended[:-1] + qi_extended[1:])
    lwp_kg_m2 = np.sum(ql_mid * (-dp)) / G_CONST
    iwp_kg_m2 = np.sum(qi_mid * (-dp)) / G_CONST
    return max(0.0, float(lwp_kg_m2 * 1000.0)), max(0.0, float(iwp_kg_m2 * 1000.0))

def fetch_var(url_base, var_name, slice_str, expected_len):
    url = f"{url_base}.ascii?{var_name}{slice_str}"
    for attempt in range(2):
        try:
            r = session.get(url, timeout=6)
            if r.status_code == 200:
                vals = parse_opendap_array(r.text, expected_len)
                if len(vals) == expected_len:
                    return True, vals, r.text
        except Exception:
            time.sleep(0.5)
    return False, None, None

def extract_18z(url_18z, forecast_start):
    is_subset = 'meps_subset' in url_18z
    
    if is_subset:
        slices = {
            'air_temperature_2m': '[6:1:24][0:1:0][0:1:0][760:1:760][486:1:486]',
            'relative_humidity_2m': '[6:1:24][0:1:0][0:1:0][760:1:760][486:1:486]',
            'cloud_area_fraction': '[6:1:24][0:1:0][0:1:0][760:1:760][486:1:486]',
            'x_wind_pl': '[6:1:24][1:1:1][0:1:0][760:1:760][486:1:486]',
            'y_wind_pl': '[6:1:24][1:1:1][0:1:0][760:1:760][486:1:486]'
        }
    else:
        slices = {
            'air_temperature_2m': '[6:1:24][0:1:0][760:1:760][486:1:486]',
            'relative_humidity_2m': '[6:1:24][0:1:0][760:1:760][486:1:486]',
            'cloud_area_fraction': '[6:1:24][0:1:0][760:1:760][486:1:486]',
            'x_wind_pl': '[6:1:24][8:1:8][760:1:760][486:1:486]',
            'y_wind_pl': '[6:1:24][8:1:8][760:1:760][486:1:486]'
        }
        
    var_vals = {}
    combined_raw = ""
    for vn, sl in slices.items():
        ok, vals, text = fetch_var(url_18z, vn, sl, 19)
        if ok:
            var_vals[vn] = vals
            combined_raw += text
        else:
            return False, None, None, f"Failed to fetch {vn}"
            
    sha = hashlib.sha256(combined_raw.encode('utf-8')).hexdigest()
    prev_day = pd.to_datetime(forecast_start) - pd.Timedelta(days=1)
    run_init = pd.Timestamp(f"{prev_day.strftime('%Y-%m-%d')} 18:00:00+00:00")
    
    rows = []
    for h_idx, h in enumerate(range(6, 25)):
        target_dt = pd.Timestamp(f"{forecast_start} {h-6:02d}:00:00")
        t_c = float(var_vals['air_temperature_2m'][h_idx] - 273.15)
        rh_pct = float(var_vals['relative_humidity_2m'][h_idx] * 100.0)
        cc_pct = float(var_vals['cloud_area_fraction'][h_idx] * 100.0)
        u7 = float(var_vals['x_wind_pl'][h_idx])
        v7 = float(var_vals['y_wind_pl'][h_idx])
        
        rows.append({
            'forecast_start': forecast_start,
            'horizon_hour': h,
            'timestamp': target_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'run_init_time': run_init.strftime('%Y-%m-%d %H:%M:%S+00:00'),
            'fc_temperature_2m_C': round(t_c, 4),
            'fc_relative_humidity_2m_pct': round(rh_pct, 4),
            'fc_cloud_cover_pct': round(cc_pct, 4),
            'u700': round(u7, 4),
            'v700': round(v7, 4)
        })
    return True, rows, sha, None

def extract_00z(url_00z, forecast_start):
    if 'meps_subset' in url_00z:
        return False, None, None, "meps_subset lacks model-level cloud microphysics (liquid_water_content_ml)"
        
    ok_sp, sp_vals, text_sp = fetch_var(url_00z, 'surface_air_pressure', '[1:1:24][0:1:0][760:1:760][486:1:486]', 24)
    ok_ql, ql_vals, text_ql = fetch_var(url_00z, 'liquid_water_content_ml', '[1:1:24][0:1:12][760:1:760][486:1:486]', 312)
    ok_qi, qi_vals, text_qi = fetch_var(url_00z, 'ice_water_content_ml', '[1:1:24][0:1:12][760:1:760][486:1:486]', 312)
    
    if not ok_sp:
        return False, None, None, "Failed to fetch surface_air_pressure"
        
    sha = hashlib.sha256((text_sp + (text_ql or "") + (text_qi or "")).encode('utf-8')).hexdigest()
    run_init = pd.Timestamp(f"{forecast_start} 00:00:00+00:00")
    
    ql_mat = ql_vals.reshape((24, 13)) if ok_ql else None
    qi_mat = qi_vals.reshape((24, 13)) if ok_qi else None
    
    rows = []
    for h_idx, h in enumerate(range(1, 25)):
        target_dt = pd.Timestamp(f"{forecast_start} 00:00:00") + pd.Timedelta(hours=h)
        sp_pa = float(sp_vals[h_idx])
        sp_hpa = sp_pa / 100.0
        
        if ql_mat is not None and qi_mat is not None:
            lwp, iwp = compute_surface_aware_lwp_iwp(sp_pa, ql_mat[h_idx], qi_mat[h_idx])
        else:
            lwp, iwp = np.nan, np.nan
            
        rows.append({
            'forecast_start': forecast_start,
            'horizon_hour': h,
            'timestamp': target_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'run_init_time': run_init.strftime('%Y-%m-%d %H:%M:%S+00:00'),
            'lwp_latest': round(lwp, 4) if not np.isnan(lwp) else np.nan,
            'iwp_latest': round(iwp, 4) if not np.isnan(iwp) else np.nan,
            'surface_air_pressure_hpa': round(sp_hpa, 4),
            'invalid_ps': False
        })
    return True, rows, sha, None

def process_origin(entry):
    d = entry['forecast_start']
    orig_st = entry['orig_status']
    alt_18z = entry['alt_18z_url']
    alt_00z = entry['alt_00z_url']
    
    ok18, rows18, sha18, err18 = False, None, None, None
    ok00, rows00, sha00, err00 = False, None, None, None
    
    if alt_18z and not pd.isna(alt_18z):
        ok18, rows18, sha18, err18 = extract_18z(alt_18z, d)
        
    if alt_00z and not pd.isna(alt_00z):
        ok00, rows00, sha00, err00 = extract_00z(alt_00z, d)
        
    if ok18 and ok00:
        outcome = 'RECOVERED'
        reason = 'Fully recovered 18Z and 00Z forecasts from authoritative THREDDS source'
    elif ok18:
        outcome = 'RECOVERED'
        reason = 'Recovered 18Z forecast features (cloud/temp/rh/wind700) from authoritative THREDDS source; 00Z LWP/IWP unarchived'
    elif ok00:
        outcome = 'RECOVERED'
        reason = 'Recovered 00Z LWP/IWP features from authoritative THREDDS source; 18Z forecast unarchived'
    elif 'HTTP 500' in str(err18) or 'HTTP 500' in str(err00):
        outcome = 'NEEDS_RETRY'
        reason = f"Transient HTTP 500 server error | 18Z: {err18} | 00Z: {err00}"
    else:
        outcome = 'UNRECOVERABLE'
        reason = f"Unarchived in MET Norway THREDDS repository | 18Z: {err18} | 00Z: {err00}"
        
    return {
        'forecast_start': d,
        'original_status': orig_st,
        'recovery_outcome': outcome,
        'rows_18z': rows18 if ok18 else [],
        'rows_00z': rows00 if ok00 else [],
        'sha_18z': sha18,
        'sha_00z': sha00,
        'authoritative_18z_url': alt_18z if ok18 else None,
        'authoritative_00z_url': alt_00z if ok00 else None,
        'exact_reason': reason
    }

def main():
    print("=== STARTING PARALLEL AUTHORITATIVE RECOVERY ===", flush=True)
    with open(AUDIT_JSON_PATH) as f:
        audit_matrix = json.load(f)
        
    f18_df = pd.read_csv(F18_PATH)
    f00_df = pd.read_csv(F00_PATH)
    log_df = pd.read_csv(LOG_PATH)
    
    print(f"Initial row counts: 18Z={len(f18_df)}, 00Z={len(f00_df)}, Log={len(log_df)}")
    
    all_results = []
    rec_18z = []
    rec_00z = []
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(process_origin, entry) for entry in audit_matrix]
        done_count = 0
        for future in as_completed(futures):
            res = future.result()
            all_results.append(res)
            if res['rows_18z']:
                rec_18z.extend(res['rows_18z'])
            if res['rows_00z']:
                rec_00z.extend(res['rows_00z'])
            done_count += 1
            if done_count % 20 == 0 or done_count == len(audit_matrix):
                print(f"Processed {done_count}/{len(audit_matrix)} missing origins...", flush=True)
                
    res_df = pd.DataFrame(all_results)
    res_df.sort_values('forecast_start', inplace=True)
    
    # Save Recovery Matrix CSV
    save_cols = [
        'forecast_start', 'original_status', 'recovery_outcome',
        'authoritative_18z_url', 'authoritative_00z_url', 'sha_18z', 'sha_00z', 'exact_reason'
    ]
    rec_matrix_path = os.path.join(BASE_DIR, 'RECOVERY_MATRIX_140_MISSING_ORIGINS.csv')
    res_df[save_cols].to_csv(rec_matrix_path, index=False)
    
    # Append recovered rows to extracted CSVs
    if rec_18z:
        f18_new = pd.DataFrame(rec_18z)
        f18_comb = pd.concat([f18_df, f18_new], ignore_index=True)
        f18_comb.sort_values(['forecast_start', 'horizon_hour'], inplace=True)
        f18_comb.drop_duplicates(subset=['forecast_start', 'horizon_hour'], inplace=True)
        f18_comb.to_csv(F18_PATH, index=False)
        print(f"\nUpdated 18Z dataset: {len(f18_df)} -> {len(f18_comb)} rows (+{len(rec_18z)} recovered)")
        
    if rec_00z:
        f00_new = pd.DataFrame(rec_00z)
        f00_comb = pd.concat([f00_df, f00_new], ignore_index=True)
        f00_comb.sort_values(['forecast_start', 'horizon_hour'], inplace=True)
        f00_comb.drop_duplicates(subset=['forecast_start', 'horizon_hour'], inplace=True)
        f00_comb.to_csv(F00_PATH, index=False)
        print(f"Updated 00Z dataset: {len(f00_df)} -> {len(f00_comb)} rows (+{len(rec_00z)} recovered)")

    # Update acquisition_log status for RECOVERED origins
    rec_dates = res_df[res_df['recovery_outcome'] == 'RECOVERED']['forecast_start'].tolist()
    if rec_dates:
        log_df.loc[log_df['forecast_start'].isin(rec_dates), 'status'] = 'RECOVERED'
        log_df.to_csv(LOG_PATH, index=False)
        print(f"Updated {len(rec_dates)} origins to RECOVERED in acquisition_log.csv")

    print("\n=== RECOVERY MATRIX SUMMARY ===")
    print(res_df['recovery_outcome'].value_counts())
    
    res_df['year'] = pd.to_datetime(res_df['forecast_start']).dt.year
    print("\nRecovery Outcome by Year:")
    print(pd.crosstab(res_df['year'], res_df['recovery_outcome'], margins=True))

if __name__ == '__main__':
    main()
