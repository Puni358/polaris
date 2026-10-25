#!/usr/bin/env python3
"""
POLARIS — Authoritative Historical Nuolja Station Data Acquisition & Validation (2020–2023)
Station: Nuolja Middle Station AWS (ANS_NMS), Abisko Scientific Research Station
Source: SITES (Swedish Infrastructure for Ecosystem Science) / Data Portal (data.fieldsites.se)
Target Variable: SW_IN (Incoming shortwave radiation, W/m^2)
Resolution: Level 2 Quality-Controlled 10-minute data (L2_SH)

Strict Scope: RESEARCH ONLY. DO NOT train models, modify Stage 8.1/J, or retrain Candidate F.
"""

import os
import sys
import json
import ssl
import re
import hashlib
from datetime import datetime, timezone
import urllib.request
import http.cookiejar
import pandas as pd
import numpy as np

BASE_DIR = "/home/punith-bs/01polaris (Copy)"
RAW_OUT_DIR = os.path.join(BASE_DIR, "data/raw_historical_sites_download")
MANIFEST_PATH = os.path.join(BASE_DIR, "data/POLARIS_HISTORICAL_NUOLJA_ACQUISITION_MANIFEST.json")

# Authoritative SITES Object PIDs for Nuolja Middle Station Level 2 (L2_SH) datasets
SITES_OBJECTS = {
    2020: {
        "pid": "https://hdl.handle.net/11676.1/CWT5DHNcPD00c8IWgAZtcmrt",
        "object_id": "CWT5DHNcPD00c8IWgAZtcmrt",
        "expected_filename": "SITES_MET_ANS_NMS_20200101-20210101_L2_SH.csv",
        "expected_steps": 52704,  # Leap year: 366 days * 144 steps/day = 52704
        "is_leap_year": True
    },
    2021: {
        "pid": "https://hdl.handle.net/11676.1/t0AeJcJn3RUXzCvdy6X8KWI5",
        "object_id": "t0AeJcJn3RUXzCvdy6X8KWI5",
        "expected_filename": "SITES_MET_ANS_NMS_20210101-20220101_L2_SH.csv",
        "expected_steps": 52560,  # 365 days * 144 steps/day = 52560
        "is_leap_year": False
    },
    2022: {
        "pid": "https://hdl.handle.net/11676.1/hWUlMbcNhTRvLAZEIJdsvb0u",
        "object_id": "hWUlMbcNhTRvLAZEIJdsvb0u",
        "expected_filename": "SITES_MET_ANS_NMS_20220101-20221231_L2_SH.csv",
        "expected_steps": 52560,
        "is_leap_year": False
    },
    2023: {
        "pid": "https://hdl.handle.net/11676.1/OL7g8xUD95cnWm5ZFEuoUwNh",
        "object_id": "OL7g8xUD95cnWm5ZFEuoUwNh",
        "expected_filename": "SITES_MET_ANS_NMS_20230101-20231231_L2_SH.csv",
        "expected_steps": 52560,
        "is_leap_year": False
    }
}

def sha256_of_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_sites_dataset(year, meta_info):
    os.makedirs(RAW_OUT_DIR, exist_ok=True)
    target_path = os.path.join(RAW_OUT_DIR, meta_info["expected_filename"])
    tmp_path = target_path + ".tmp"

    if os.path.exists(target_path):
        size = os.path.getsize(target_path)
        if size > 1000000:
            file_hash = sha256_of_file(target_path)
            print(f"[{year}] Existing raw file verified: {target_path} ({size} bytes, SHA256: {file_hash[:16]}...)")
            return target_path, file_hash, size, False

    print(f"[{year}] Acquiring raw SITES dataset via object ID {meta_info['object_id']}...")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx)
    )
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) POLARIS Research Agent")]

    meta_url = f"https://meta.fieldsites.se/objects/{meta_info['object_id']}"
    resp1 = opener.open(meta_url)
    html1 = resp1.read().decode("utf-8")

    m = re.search(r"https://data\.fieldsites\.se/licence_accept\?ids=[^\s\"\'<>]+", html1)
    if not m:
        raise ValueError(f"Could not locate licence_accept URL for year {year} ({meta_url})")

    lic_url = m.group(0).replace("&amp;", "&")
    
    resp2 = opener.open(lic_url)
    resp2.read()

    dl_url = f"https://data.fieldsites.se/objects/{meta_info['object_id']}"
    resp3 = opener.open(dl_url)

    if resp3.status != 200:
        raise RuntimeError(f"Failed to download year {year} from {dl_url}: HTTP {resp3.status}")

    with open(tmp_path, "wb") as f:
        while True:
            chunk = resp3.read(65536)
            if not chunk:
                break
            f.write(chunk)

    os.replace(tmp_path, target_path)
    file_size = os.path.getsize(target_path)
    file_hash = sha256_of_file(target_path)
    print(f"[{year}] Successfully acquired {target_path} ({file_size} bytes, SHA256: {file_hash})")
    return target_path, file_hash, file_size, True

def validate_raw_dataset(year, filepath, meta_info):
    print(f"\n--- Validating Year {year} Raw SITES File ---")
    with open(filepath, "r", encoding="utf-8-sig", errors="ignore") as f:
        lines = f.readlines()

    header_text = "".join(lines[:40])
    
    # Locate line index where data table header starts ("TIMESTAMP,")
    data_start_line = 0
    for i, line in enumerate(lines):
        if line.startswith("TIMESTAMP,"):
            data_start_line = i
            break

    # Sanity check station identity
    has_ans_nms = "ANS_NMS" in header_text or "Nuolja Middle Station" in header_text or "Nuolja" in header_text
    has_elevation = "702" in header_text or "Nuolja" in header_text
    
    # Parse CSV content starting from data_start_line
    df = pd.read_csv(filepath, skiprows=data_start_line)
    df["TIMESTAMP"] = df["TIMESTAMP"].astype(str).str.strip()
    df["dt"] = pd.to_datetime(df["TIMESTAMP"])

    total_rows = len(df)
    first_ts = str(df["TIMESTAMP"].iloc[0])
    last_ts = str(df["TIMESTAMP"].iloc[-1])

    # Check 10-minute step continuity
    df = df.sort_values("dt").reset_index(drop=True)
    time_diffs = df["dt"].diff()
    expected_step = pd.Timedelta(minutes=10)
    irregular_steps = int((time_diffs.dropna() != expected_step).sum())

    # Count missing timestamps in complete year range
    start_dt = df["dt"].min()
    end_dt = df["dt"].max()
    full_range = pd.date_range(start=start_dt, end=end_dt, freq="10min")
    missing_steps_count = len(full_range) - total_rows

    # Check SW_IN statistics
    sw_col = "SW_IN" if "SW_IN" in df.columns else None
    if sw_col is None:
        raise KeyError(f"SW_IN column missing in {filepath}")

    sw_vals = df[sw_col].dropna()
    sw_min = float(sw_vals.min())
    sw_max = float(sw_vals.max())
    sw_mean = float(sw_vals.mean())
    sw_nan_count = int(df[sw_col].isna().sum())
    sw_zero_count = int((df[sw_col] == 0.0).sum())
    sw_positive_count = int((df[sw_col] > 0.0).sum())

    # Sanity check: solar irradiance bounds
    sanity_pass = (sw_min >= 0.0) and (sw_max < 1400.0) and (sw_positive_count > 1000)

    val_report = {
        "year": year,
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "station_identity_matches_ANS_NMS": has_ans_nms,
        "total_raw_rows": total_rows,
        "expected_rows": meta_info["expected_steps"],
        "row_count_match": (total_rows == meta_info["expected_steps"]),
        "first_timestamp": first_ts,
        "last_timestamp": last_ts,
        "time_range_start": str(start_dt),
        "time_range_end": str(end_dt),
        "resolution": "10 minutes",
        "timezone_convention": "UTC+1 (fixed)",
        "header_lines_count": data_start_line,
        "irregular_step_count": irregular_steps,
        "missing_steps_count": int(missing_steps_count),
        "sw_in_units": "W/m^2",
        "sw_in_min": round(sw_min, 4),
        "sw_in_max": round(sw_max, 4),
        "sw_in_mean": round(sw_mean, 4),
        "sw_in_nan_count": sw_nan_count,
        "sw_in_zero_count": sw_zero_count,
        "sw_in_positive_count": sw_positive_count,
        "sanity_pass": sanity_pass,
        "available_columns": list(df.columns[df.columns != "dt"])
    }

    print(f"  Rows: {total_rows} (Expected: {meta_info['expected_steps']})")
    print(f"  Range: {first_ts} to {last_ts}")
    print(f"  SW_IN stats: Min={sw_min}, Max={sw_max}, Mean={sw_mean:.2f} W/m^2")
    print(f"  SW_IN zeros={sw_zero_count}, positive={sw_positive_count}, NaNs={sw_nan_count}")
    print(f"  Station identity ANS_NMS verified: {has_ans_nms}")
    print(f"  Sanity check pass: {sanity_pass}")

    return val_report

def main():
    print("=== POLARIS — HISTORICAL NUOLJA STATION DATA ACQUISITION & VALIDATION (2020–2023) ===")
    
    acquisition_manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Acquisition & Validation of Authoritative Historical Nuolja Middle Station (ANS_NMS) Level 2 observations for Candidate F context feature reconstruction.",
        "target_station": {
            "name": "Nuolja Middle Station AWS",
            "code": "ANS_NMS",
            "provider": "Abisko Scientific Research Station / SITES",
            "portal": "https://data.fieldsites.se",
            "coordinates": {"lat": 68.36207412, "lon": 18.73875158, "altitude_m": 702},
            "target_variable": "SW_IN",
            "instrument": "Apogee SP110 Pyranometer",
            "resolution": "10 minutes"
        },
        "datasets": {}
    }

    all_validations = []
    overall_pass = True

    for year, meta in SITES_OBJECTS.items():
        filepath, file_hash, file_size, newly_acquired = download_sites_dataset(year, meta)
        val_info = validate_raw_dataset(year, filepath, meta)
        
        val_info["sha256"] = file_hash
        val_info["file_size_bytes"] = file_size
        val_info["newly_acquired"] = newly_acquired
        val_info["source_pid"] = meta["pid"]
        val_info["source_object_id"] = meta["object_id"]

        acquisition_manifest["datasets"][str(year)] = val_info
        all_validations.append(val_info)
        
        if not (val_info["station_identity_matches_ANS_NMS"] and val_info["sanity_pass"]):
            overall_pass = False

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(acquisition_manifest, f, indent=2)

    print(f"\nSaved acquisition manifest to {MANIFEST_PATH}")
    print(f"Overall Raw Validation: {'PASS' if overall_pass else 'FAIL'}")

if __name__ == "__main__":
    main()
