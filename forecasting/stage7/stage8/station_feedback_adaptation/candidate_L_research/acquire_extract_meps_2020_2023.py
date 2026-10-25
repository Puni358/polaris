import os
import sys
import json
import time
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Paths
BASE_DIR = Path("/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/station_feedback_adaptation/candidate_L_research")
CACHE_DIR = BASE_DIR / "meps_cache"
CACHE_18Z_DIR = CACHE_DIR / "18z"
CACHE_00Z_DIR = CACHE_DIR / "00z"
EXTRACTED_DIR = BASE_DIR / "extracted"

CACHE_18Z_DIR.mkdir(parents=True, exist_ok=True)
CACHE_00Z_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

# Grid & Coordinate Invariants
NUOLJA_Y = 760
NUOLJA_X = 486
P700_IDX = 8
TARGET_LAT = 68.36207412
TARGET_LON = 18.73875158

MEPS_PRESSURE_LEVELS_PA = np.array([1000, 925, 850, 700, 500, 400, 300, 250, 200, 150, 100, 70, 50], dtype=float) * 100.0
G_CONST = 9.80665

lock = threading.Lock()

def compute_sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def compute_haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
    return float(2.0 * R * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a)))

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

def parse_ascii_series(ascii_text: str, var_name: str, expected_count: int):
    if not ascii_text or var_name not in ascii_text:
        return None
    try:
        lines = ascii_text.splitlines()
        values = []
        in_var = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith(var_name + "[") or line_str.startswith(var_name + "."):
                in_var = True
                continue
            if in_var:
                if line_str.startswith("Dataset") or (line_str and line_str[0].isalpha() and "[" in line_str):
                    in_var = False
                    continue
                parts = line_str.split(",")
                for p in parts:
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    if "[" in p_clean:
                        p_clean = p_clean.split("]")[-1].strip()
                    try:
                        v = float(p_clean)
                        values.append(v)
                    except ValueError:
                        pass
        if len(values) >= expected_count:
            return np.array(values[:expected_count], dtype=float)
        return None
    except Exception:
        return None

def fetch_url_with_retry(url: str, max_retries=3, base_timeout=12, pacing=0.4):
    time.sleep(pacing)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'POLARIS-CandidateL/1.0'})
            with urllib.request.urlopen(req, timeout=base_timeout) as resp:
                if resp.status == 200:
                    return resp.read().decode('utf-8', errors='ignore'), 200, attempt
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, 404, attempt
            time.sleep((attempt + 1) * 1.5)
        except Exception:
            time.sleep((attempt + 1) * 1.5)
    return None, 500, max_retries

def process_origin_date(origin_dt: datetime):
    date_str = origin_dt.strftime("%Y-%m-%d")
    year_str = origin_dt.strftime("%Y")
    month_str = origin_dt.strftime("%m")
    day_str = origin_dt.strftime("%d")

    cache_18z_path = CACHE_18Z_DIR / f"meps_18z_{origin_dt.strftime('%Y%m%d')}.ascii"
    cache_00z_path = CACHE_00Z_DIR / f"meps_00z_{origin_dt.strftime('%Y%m%d')}.ascii"

    prev_dt = origin_dt - timedelta(days=1)
    prev_year = prev_dt.strftime("%Y")
    prev_month = prev_dt.strftime("%m")
    prev_day = prev_dt.strftime("%d")
    prev_tag = prev_dt.strftime("%Y%m%d")

    base_18z = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{prev_year}/{prev_month}/{prev_day}/meps_det_2_5km_{prev_tag}T18Z.nc.ascii"
    query_18z = (
        f"latitude[{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"longitude[{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"pressure[{P700_IDX}:1:{P700_IDX}],"
        f"air_temperature_2m[6:1:24][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"relative_humidity_2m[6:1:24][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"cloud_area_fraction[6:1:24][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"x_wind_pl[6:1:24][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"y_wind_pl[6:1:24][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]"
    )
    url_18z = f"{base_18z}?{urllib.parse.quote(query_18z, safe='=:')}"

    tag_00z = origin_dt.strftime("%Y%m%d")
    base_00z = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{year_str}/{month_str}/{day_str}/meps_det_2_5km_{tag_00z}T00Z.nc.ascii"
    query_00z = (
        f"surface_air_pressure[0:1:23][0:1:0][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"mass_fraction_of_cloud_ice_in_air_pl[0:1:23][0:1:12][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]"
    )
    url_00z = f"{base_00z}?{urllib.parse.quote(query_00z, safe='=:')}"

    text_18z, text_00z = None, None
    sha_18z, sha_00z = None, None

    # 18Z Fetch / Cache
    if cache_18z_path.exists():
        with open(cache_18z_path, 'r', encoding='utf-8') as fp:
            text_18z = fp.read()
        sha_18z = compute_sha256_text(text_18z)
    else:
        text_18z, status_18z, _ = fetch_url_with_retry(url_18z)
        if text_18z:
            sha_18z = compute_sha256_text(text_18z)
            with open(cache_18z_path, 'w', encoding='utf-8') as fp:
                fp.write(text_18z)
        else:
            return {"forecast_start": date_str, "status": f"FAILED_18Z_HTTP_{status_18z}"}

    # 00Z Fetch / Cache
    if cache_00z_path.exists():
        with open(cache_00z_path, 'r', encoding='utf-8') as fp:
            text_00z = fp.read()
        sha_00z = compute_sha256_text(text_00z)
    else:
        text_00z, status_00z, _ = fetch_url_with_retry(url_00z)
        if text_00z:
            sha_00z = compute_sha256_text(text_00z)
            with open(cache_00z_path, 'w', encoding='utf-8') as fp:
                fp.write(text_00z)
        else:
            return {"forecast_start": date_str, "status": f"FAILED_00Z_HTTP_{status_00z}"}

    # Parse 18Z metadata
    lat_val = parse_ascii_series(text_18z, "latitude", 1)
    lon_val = parse_ascii_series(text_18z, "longitude", 1)
    p700_val = parse_ascii_series(text_18z, "pressure", 1)

    grid_lat = float(lat_val[0]) if lat_val is not None else np.nan
    grid_lon = float(lon_val[0]) if lon_val is not None else np.nan
    p700_hpa = float(p700_val[0]) if p700_val is not None else np.nan
    dist_km = compute_haversine_km(TARGET_LAT, TARGET_LON, grid_lat, grid_lon) if not np.isnan(grid_lat) else np.nan

    # Parse 18Z Variables
    t2m_k = parse_ascii_series(text_18z, "air_temperature_2m", 19)
    rh_frac = parse_ascii_series(text_18z, "relative_humidity_2m", 19)
    cloud_frac_native = parse_ascii_series(text_18z, "cloud_area_fraction", 19)
    u700 = parse_ascii_series(text_18z, "x_wind_pl", 19)
    v700 = parse_ascii_series(text_18z, "y_wind_pl", 19)

    ok18 = all(x is not None for x in [t2m_k, rh_frac, cloud_frac_native, u700, v700])
    if not ok18:
        return {"forecast_start": date_str, "status": "FAILED_18Z_PARSE"}

    # Parse 00Z Variables
    ps_pa = parse_ascii_series(text_00z, "surface_air_pressure", 24)
    ql_raw = parse_ascii_series(text_00z, "mass_fraction_of_cloud_condensed_water_in_air_pl", 312)
    qi_raw = parse_ascii_series(text_00z, "mass_fraction_of_cloud_ice_in_air_pl", 312)

    ok00 = all(x is not None for x in [ps_pa, ql_raw, qi_raw])
    if not ok00:
        return {"forecast_start": date_str, "status": "FAILED_00Z_PARSE"}

    # Build 18Z Dataframe
    run_init_18z = prev_dt.replace(hour=18, minute=0, second=0)
    rows_18z = []
    for i, lead in enumerate(range(6, 25)):
        horizon_hour = lead - 5
        valid_time = run_init_18z + timedelta(hours=lead)
        rows_18z.append({
            "forecast_start": date_str,
            "horizon_hour": horizon_hour,
            "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
            "run_init_time": run_init_18z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
            "fc_temperature_2m_C": round(float(t2m_k[i]) - 273.15, 4),
            "fc_relative_humidity_2m_pct": round(float(rh_frac[i]) * 100.0, 4),
            "fc_cloud_cover_pct": round(float(cloud_frac_native[i]) * 100.0, 4),
            "u700": round(float(u700[i]), 4),
            "v700": round(float(v700[i]), 4),
        })

    # Build 00Z Dataframe
    run_init_00z = origin_dt.replace(hour=0, minute=0, second=0)
    ql_data = ql_raw.reshape((24, 13))
    qi_data = qi_raw.reshape((24, 13))
    rows_00z = []
    for h_idx in range(24):
        h = h_idx + 1
        ps = ps_pa[h_idx]
        valid_time = run_init_00z + timedelta(hours=h)
        if np.isnan(ps) or ps < 70000.0 or ps > 110000.0:
            rows_00z.append({
                "forecast_start": date_str,
                "horizon_hour": h,
                "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "run_init_time": run_init_00z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "lwp_latest": np.nan,
                "iwp_latest": np.nan,
                "surface_air_pressure_hpa": np.nan,
                "invalid_ps": True
            })
        else:
            lwp_sa, iwp_sa = compute_surface_aware_lwp_iwp(ps, ql_data[h_idx], qi_data[h_idx])
            rows_00z.append({
                "forecast_start": date_str,
                "horizon_hour": h,
                "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "run_init_time": run_init_00z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                "lwp_latest": round(float(lwp_sa), 6),
                "iwp_latest": round(float(iwp_sa), 6),
                "surface_air_pressure_hpa": round(float(ps / 100.0), 2),
                "invalid_ps": False
            })

    return {
        "forecast_start": date_str,
        "status": "SUCCESS",
        "grid_lat": round(grid_lat, 6),
        "grid_lon": round(grid_lon, 6),
        "grid_distance_km": round(dist_km, 4),
        "p700_hpa": round(p700_hpa, 2),
        "sha256_18z": sha_18z,
        "sha256_00z": sha_00z,
        "df_18z": pd.DataFrame(rows_18z),
        "df_00z": pd.DataFrame(rows_00z)
    }

def main():
    start_year, end_year = 2020, 2023
    all_dates = pd.date_range(f"{start_year}-01-01", f"{end_year}-12-31", freq='D')
    log_csv = BASE_DIR / "acquisition_log.csv"
    extracted_18z_file = EXTRACTED_DIR / "meps_18z_cloud_temp_rh_wind700_2020_2023.csv"
    extracted_00z_file = EXTRACTED_DIR / "meps_00z_lwp_iwp_2020_2023.csv"

    existing_log = {}
    if log_csv.exists():
        df_log_exist = pd.read_csv(log_csv)
        for _, r in df_log_exist.iterrows():
            existing_log[str(r['forecast_start'])] = dict(r)

    print(f"=== Starting Candidate L Parallel Acquisition (3 Workers) for {len(all_dates)} origins ({start_year}-{end_year}) ===")
    print(f"Existing logged origins: {len(existing_log)}")

    dates_to_process = [dt for dt in all_dates if dt.strftime("%Y-%m-%d") not in existing_log or existing_log[dt.strftime("%Y-%m-%d")].get('status') not in ['SUCCESS', 'FAILED_18Z_HTTP_404']]
    print(f"Origins left to process: {len(dates_to_process)}")

    all_18z_dfs = []
    all_00z_dfs = []
    if extracted_18z_file.exists():
        all_18z_dfs.append(pd.read_csv(extracted_18z_file))
    if extracted_00z_file.exists():
        all_00z_dfs.append(pd.read_csv(extracted_00z_file))

    def worker(dt):
        return process_origin_date(dt)

    max_workers = 3
    completed_count = 0
    total_to_process = len(dates_to_process)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_date = {executor.submit(worker, dt): dt for dt in dates_to_process}
        for future in as_completed(future_to_date):
            dt = future_to_date[future]
            d_str = dt.strftime("%Y-%m-%d")
            completed_count += 1
            try:
                res = future.result()
                status = res['status']
                entry = {
                    "forecast_start": d_str,
                    "target_date_range": f"{d_str} 01:00 to {d_str} 24:00",
                    "source_18z_url": f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/.../{d_str}T18Z.nc",
                    "source_00z_url": f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/.../{d_str}T00Z.nc",
                    "status": status,
                    "grid_lat": res.get("grid_lat", np.nan),
                    "grid_lon": res.get("grid_lon", np.nan),
                    "grid_distance_km": res.get("grid_distance_km", np.nan),
                    "p700_hpa": res.get("p700_hpa", np.nan),
                    "sha256_18z": res.get("sha256_18z", ""),
                    "sha256_00z": res.get("sha256_00z", ""),
                    "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                with lock:
                    existing_log[d_str] = entry
                    log_entries = list(existing_log.values())
                    pd.DataFrame(log_entries).to_csv(log_csv, index=False)

                    if status == "SUCCESS":
                        all_18z_dfs.append(res['df_18z'])
                        all_00z_dfs.append(res['df_00z'])
                        pd.concat(all_18z_dfs, ignore_index=True).to_csv(extracted_18z_file, index=False)
                        pd.concat(all_00z_dfs, ignore_index=True).to_csv(extracted_00z_file, index=False)
                        print(f"[{completed_count}/{total_to_process}] {d_str}: SUCCESS | Grid: ({res['grid_lat']}, {res['grid_lon']}) | p700: {res['p700_hpa']} hPa | dist: {res['grid_distance_km']} km", flush=True)
                    else:
                        print(f"[{completed_count}/{total_to_process}] {d_str}: {status}", flush=True)

            except Exception as e:
                print(f"[{completed_count}/{total_to_process}] {d_str}: EXCEPTION {e}", flush=True)

    # Save final manifest
    log_entries = list(existing_log.values())
    n_success = sum(1 for e in log_entries if e.get('status') == 'SUCCESS')
    n_failed = sum(1 for e in log_entries if e.get('status') != 'SUCCESS')

    manifest = {
        "project": "POLARIS",
        "task": "CANDIDATE L — 2020–2023 MEPS ACQUISITION AND EXTRACTION",
        "requested_years": f"{start_year}-{end_year}",
        "total_origins_requested": len(all_dates),
        "successfully_acquired_origins": n_success,
        "failed_origins": n_failed,
        "grid_point": {"y": NUOLJA_Y, "x": NUOLJA_X, "lat": 68.355701, "lon": 18.763667},
        "pressure_700_idx": P700_IDX,
        "pressure_700_value_hpa": 700.0,
        "cache_dir": str(CACHE_DIR),
        "extracted_dir": str(EXTRACTED_DIR),
        "log_file": str(log_csv),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    with open(BASE_DIR / "ACQUISITION_MANIFEST.json", "w") as fp:
        json.dump(manifest, fp, indent=2)

    print("\n=== ACQUISITION & EXTRACTION RUN COMPLETE ===")
    print(f"Total: {len(all_dates)} | Success: {n_success} | Failed: {n_failed}")

if __name__ == "__main__":
    main()
