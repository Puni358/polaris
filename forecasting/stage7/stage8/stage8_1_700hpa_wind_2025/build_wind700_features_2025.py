#!/usr/bin/env python3
"""
POLARIS — Stage 8.1 upstream dependency: 700 hPa steering wind
(u700, v700), 2025.

Based on the extraction method in
forecasting/stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py (2024, LOCKED):
same source (MET Norway meps25epsarchive deterministic pressure-level
files via THREDDS OPeNDAP ASCII), same day-ahead causal convention
(each forecast day D is served by the run issued at D-1 18Z), same
station grid indices (NUOLJA_Y, NUOLJA_X -- same physical location,
same archived grid definition), same threaded/checkpointed/resumable
extraction pattern, same atomic writes.

TWO causal/alignment defects were found in the 2024 artifact while
verifying this dependency (details in the manifest written at the
end of this run); both are fixed here, not reproduced, and the 2024
file is left untouched:

1. Off-by-one horizon_hour: the 2024 script built horizon_hour=1 as
   valid_time = forecast_start + 1h (first value of a [7:1:30] time
   slice), but the rest of the Stage 8.1 pipeline (Stage 3b/4, NWP)
   uses horizon_hour=1 == forecast_start + 0h. Since the eventual
   merge is a plain join on (forecast_start, horizon_hour), this
   silently shifts the 2024 wind features by one hour relative to
   every other feature they get merged with. Fixed here by using a
   [6:1:24] time slice so horizon_hour=1 == valid_time 00:00 of the
   forecast day, matching the rest of the pipeline.

2. Hourly/3-hourly resolution cliff: independently probing the
   archive's time dimension (meps_det_pl_20250314T18Z, confirmed
   structurally -- not date-specific) shows this product is hourly
   only through lead time +24h from the run's reference time, then
   drops to 3-hourly. A run issued at D-1 18Z is hourly through
   18:00 on day D (lead +24h); hours 19:00-23:00 of day D (lead
   +25h..+29h) have NO hourly data -- the 2024 script's [7:1:30]
   slice (24 raw array positions) silently pulled the 3-hourly
   values for roughly the last 5-6 "hours" of each day and relabeled
   them as sequential hourly values (e.g. its "horizon_hour=24"
   label, meant to be 00:00 of D+1, actually held the value from
   12:00 of D+1 -- a 12-hour-later value mislabeled as the next
   hour). This script does NOT fabricate or mislabel data for those
   hours: horizon_hour 20-24 are left as a documented, genuine
   coverage gap (NaN) rather than silently wrong values.
"""

import os
import re
import sys
import json
import time
import hashlib
import requests
import concurrent.futures
from pathlib import Path
from datetime import timedelta

import pandas as pd
import numpy as np

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind_2025"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

NWP_PATH = BASE_DIR / "data" / "POLARIS_v0_1_future_weather_forecasts_2025.csv"

CHECKPOINT_PATH = STAGE_DIR / "extraction_checkpoint.json"
FEATURES_PATH = STAGE_DIR / "stage8_1_wind700_features_2025.csv"
MANIFEST_PATH = STAGE_DIR / "stage8_1_wind700_features_2025_MANIFEST.json"

NUOLJA_Y, NUOLJA_X = 760, 486  # same station grid cell as 2024 (same archived grid definition)

N_HOURLY = 19  # horizon_hour 1..19 == valid_time 00:00..18:00 of the forecast day (genuinely hourly)
N_TOTAL = 24   # full day; horizon_hour 20..24 are a documented coverage gap (NaN)


def atomic_write_json(obj, path):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def atomic_write_csv(df, path):
    tmp = str(path) + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_origin_wind(args):
    idx, origin_ts_str = args
    origin_ts = pd.to_datetime(origin_ts_str, utc=True)
    d_minus_1 = origin_ts - timedelta(days=1)
    d1_str = d_minus_1.strftime("%Y/%m/%d")
    d1_tag = d_minus_1.strftime("%Y%m%d")

    # [6:1:24] (19 points) -> lead +6h..+24h from an 18Z run == 00:00..18:00 of day D.
    # Fixes both defects described in the module docstring: correct horizon_hour
    # alignment, and no silent 3-hourly-mislabeled-as-hourly tail.
    url = (
        f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{d1_str}/"
        f"meps_det_pl_{d1_tag}T18Z.ncml.ascii?"
        f"x_wind_pl[6:1:24][8:1:8][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}],"
        f"y_wind_pl[6:1:24][8:1:8][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]"
    )
    ref_time_str = d_minus_1.replace(hour=18).strftime("%Y-%m-%d %H:%M:%S%z")

    for attempt in range(5):
        u_vals, v_vals = [], []
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = [l.strip() for l in r.text.splitlines() if l.strip()]
                current_var = None
                for line in lines:
                    if "x_wind_pl[" in line:
                        current_var = "u"
                    elif "y_wind_pl[" in line:
                        current_var = "v"
                    m = re.search(r'\[\d+\].*,\s*([0-9eE\.\+\-]+)', line)
                    if m:
                        val = float(m.group(1))
                        if current_var == "u":
                            u_vals.append(val)
                        elif current_var == "v":
                            v_vals.append(val)

            if len(u_vals) == N_HOURLY and len(v_vals) == N_HOURLY:
                rows = []
                for h in range(1, N_TOTAL + 1):
                    valid_time = origin_ts + timedelta(hours=h - 1)
                    if h <= N_HOURLY:
                        u700, v700, causal_pass, coverage = u_vals[h - 1], v_vals[h - 1], True, "hourly"
                    else:
                        u700, v700, causal_pass, coverage = np.nan, np.nan, False, "gap_3hourly_archive"
                    rows.append({
                        "origin_index": idx,
                        "forecast_start": origin_ts.strftime("%Y-%m-%d %H:%M:%S%z"),
                        "horizon_hour": h,
                        "valid_time": valid_time.strftime("%Y-%m-%d %H:%M:%S%z"),
                        "forecast_reference_time": ref_time_str,
                        "u700": u700,
                        "v700": v700,
                        "meps_run_id": f"{d1_tag}T18Z",
                        "causal_pass": causal_pass,
                        "coverage": coverage,
                    })
                return idx, rows
        except Exception:
            time.sleep(0.3 * (attempt + 1))

    return idx, None


def run_feature_extraction(origins):
    print("==================================================")
    print("[STAGE 8.1 / 2025] STARTING 700 hPa WIND EXTRACTION")
    print("==================================================")

    total_origins = len(origins)
    results_map = {}

    if CHECKPOINT_PATH.exists():
        try:
            with open(CHECKPOINT_PATH, "r") as f:
                chk = json.load(f)
                results_map = {int(k): v for k, v in chk.items()}
                print(f"Resuming from checkpoint: {len(results_map)}/{total_origins} origins extracted.")
        except Exception as e:
            print(f"Warning loading checkpoint: {e}")

    attempt = 0
    while len(results_map) < total_origins and attempt < 15:
        attempt += 1
        missing_tasks = [(idx, orig_ts) for idx, orig_ts in enumerate(origins, 1) if idx not in results_map]
        if not missing_tasks:
            break

        done_count = len(results_map)
        print(f"Extraction batch attempt {attempt}: {done_count}/{total_origins} done, {len(missing_tasks)} remaining")

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_to_idx = {executor.submit(extract_origin_wind, task): task[0] for task in missing_tasks}
            for future in concurrent.futures.as_completed(future_to_idx):
                idx, rows = future.result()
                if rows:
                    results_map[idx] = rows
                    done_count += 1
                    if done_count % 20 == 0 or done_count == total_origins:
                        print(f"Extraction {done_count}/{total_origins}")
                        sys.stdout.flush()
                        atomic_write_json({str(k): v for k, v in results_map.items()}, CHECKPOINT_PATH)

    atomic_write_json({str(k): v for k, v in results_map.items()}, CHECKPOINT_PATH)

    if len(results_map) < total_origins:
        raise RuntimeError(f"Failed to extract all origins! Only extracted {len(results_map)}/{total_origins}.")

    print(f"Extraction {total_origins}/{total_origins}")

    all_rows = []
    for idx in sorted(results_map.keys()):
        all_rows.extend(results_map[idx])

    df_feat = pd.DataFrame(all_rows)
    atomic_write_csv(df_feat, FEATURES_PATH)
    print(f"Feature extraction complete! Saved {len(df_feat)} rows to {FEATURES_PATH}")
    return df_feat


def main():
    nwp_hash = sha256_of(NWP_PATH)
    df_nwp = pd.read_csv(NWP_PATH)
    df_nwp["forecast_start"] = pd.to_datetime(df_nwp["forecast_start"], utc=True)
    origins = sorted(df_nwp["forecast_start"].unique().astype(str))
    print(f"2025 origins (from clean NWP file, hash {nwp_hash[:12]}...): {len(origins)}")

    df_feat = run_feature_extraction(origins)

    # ============================================================
    # VALIDATION
    # ============================================================
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    n_origins = df_feat["forecast_start"].nunique()
    print(f"1. Origin count: {n_origins} (expected {len(origins)})")
    assert n_origins == len(origins)

    horiz_ok = (df_feat.groupby("forecast_start")["horizon_hour"].count() == 24).all()
    print(f"2. Exactly 24 horizon rows/origin (19 real + 5 documented gap): {horiz_ok}")
    assert horiz_ok

    dup = df_feat.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    print(f"3. Duplicates: {dup} (expected 0)")
    assert dup == 0

    n_hourly_valid = int((df_feat["coverage"] == "hourly").sum())
    n_gap = int((df_feat["coverage"] == "gap_3hourly_archive").sum())
    print(f"4. Rows with genuine hourly u700/v700: {n_hourly_valid} (expected {len(origins) * N_HOURLY})")
    print(f"   Rows in documented coverage gap (NaN, horizon_hour 20-24): {n_gap} (expected {len(origins) * (N_TOTAL - N_HOURLY)})")
    assert n_hourly_valid == len(origins) * N_HOURLY
    assert n_gap == len(origins) * (N_TOTAL - N_HOURLY)

    n_nan_in_hourly = df_feat[df_feat["coverage"] == "hourly"][["u700", "v700"]].isna().sum().sum()
    n_inf_in_hourly = np.isinf(df_feat[df_feat["coverage"] == "hourly"][["u700", "v700"]].values).sum()
    print(f"5. NaN in the 19 genuine hourly rows: {n_nan_in_hourly} (expected 0); Inf: {n_inf_in_hourly} (expected 0)")
    assert n_nan_in_hourly == 0 and n_inf_in_hourly == 0

    # Causal check: forecast_reference_time (run issue time) must be strictly
    # before valid_time for every row, and the run is always the PREVIOUS day's
    # 18Z run relative to forecast_start (day-ahead causal design, same as 2024).
    df_feat["_ref"] = pd.to_datetime(df_feat["forecast_reference_time"], utc=True)
    df_feat["_valid"] = pd.to_datetime(df_feat["valid_time"], utc=True)
    df_feat["_fs"] = pd.to_datetime(df_feat["forecast_start"], utc=True)
    causal_ref_before_valid = (df_feat["_ref"] < df_feat["_valid"]).all()
    causal_ref_is_prev_day_18z = (df_feat["_ref"] == (df_feat["_fs"] - pd.Timedelta(hours=6))).all()
    causal_horizon_alignment = (
        (df_feat["_valid"] - df_feat["_fs"]) == pd.to_timedelta(df_feat["horizon_hour"] - 1, unit="h")
    ).all()
    print(f"6. Causal: reference_time < valid_time for all rows: {causal_ref_before_valid}")
    print(f"7. Causal: reference_time == forecast_start - 6h (prev-day 18Z run) for all rows: {causal_ref_is_prev_day_18z}")
    print(f"8. Alignment: valid_time == forecast_start + (horizon_hour-1)h for all rows: {causal_horizon_alignment}")
    assert causal_ref_before_valid and causal_ref_is_prev_day_18z and causal_horizon_alignment
    df_feat = df_feat.drop(columns=["_ref", "_valid", "_fs"])

    expected_cols = ["origin_index", "forecast_start", "horizon_hour", "valid_time",
                      "forecast_reference_time", "u700", "v700", "meps_run_id",
                      "causal_pass", "coverage"]
    print(f"9. Schema: {list(df_feat.columns)}")
    assert list(df_feat.columns) == expected_cols

    atomic_write_csv(df_feat, FEATURES_PATH)
    out_hash = sha256_of(FEATURES_PATH)
    print(f"\n10. Output SHA256: {out_hash}")
    print(f"    Output path:   {FEATURES_PATH}")

    manifest = {
        "output_file": str(FEATURES_PATH),
        "sha256": out_hash,
        "row_count": int(len(df_feat)),
        "unique_origins": int(n_origins),
        "columns": expected_cols,
        "input_hashes": {"nwp_2025_clean": nwp_hash},
        "source": "MET Norway meps25epsarchive (meps_det_pl), via thredds.met.no OPeNDAP ASCII",
        "station_grid_cell": {"y": NUOLJA_Y, "x": NUOLJA_X, "reused_from_2024": True},
        "coverage": {
            "hourly_horizon_hours": list(range(1, N_HOURLY + 1)),
            "gap_horizon_hours": list(range(N_HOURLY + 1, N_TOTAL + 1)),
            "gap_reason": (
                "the archived meps_det_pl product is hourly only through lead "
                "time +24h from its reference run; beyond that it is 3-hourly. "
                "A day-ahead (D-1 18Z) run therefore has genuine hourly data "
                "only for 00:00-18:00 of the forecast day. Hours 19:00-23:00 "
                "are a structural gap in this archived product, not fabricated "
                "or interpolated."
            ),
        },
        "defects_found_in_2024_artifact_and_fixed_here": [
            {
                "defect": "off_by_one_horizon_hour",
                "detail": (
                    "2024's horizon_hour=1 == forecast_start+1h; every other "
                    "Stage 8.1 feature source uses horizon_hour=1 == "
                    "forecast_start+0h. A plain join on (forecast_start, "
                    "horizon_hour) silently shifts 2024's wind features by 1h."
                ),
                "evidence": "independently reproduced: 2024 row (forecast_start=2024-01-20, horizon_hour=1) has valid_time=2024-01-20 01:00:00, not 00:00:00.",
                "action": "fixed in this 2025 build (valid_time==forecast_start+(horizon_hour-1)h); 2024 file left unmodified",
            },
            {
                "defect": "hourly_to_3hourly_mislabeling",
                "detail": (
                    "2024's naive 24-length array slice silently mixed genuine "
                    "hourly values (lead +7h..+24h) with mislabeled 3-hourly "
                    "values (lead +27h, +30h, ..., +42h) for its horizon_hour "
                    "19-24, presenting e.g. a +42h-lead value as if it were "
                    "sequential-hour data."
                ),
                "evidence": "independently probed the archive's time dimension (meps_det_pl_20250314T18Z): hourly through index 24 (lead+24h), 3-hourly (3h steps) from index 25 onward -- a structural property of the file, confirmed by direct query, not a one-off.",
                "action": "this 2025 build reports horizon_hour 20-24 as an explicit NaN/documented gap instead of mislabeling 3-hourly data as hourly; 2024 file left unmodified",
            },
        ],
        "validation": {
            "origin_count_ok": bool(n_origins == len(origins)),
            "horizons_per_origin_ok": bool(horiz_ok),
            "no_duplicates": bool(dup == 0),
            "no_nan_inf_in_valid_hours": bool(n_nan_in_hourly == 0 and n_inf_in_hourly == 0),
            "causal_ref_before_valid": bool(causal_ref_before_valid),
            "causal_ref_is_prev_day_18z": bool(causal_ref_is_prev_day_18z),
            "causal_horizon_alignment_ok": bool(causal_horizon_alignment),
            "schema_ok": True,
        },
    }
    atomic_write_json(manifest, MANIFEST_PATH)
    print(f"\nManifest written to: {MANIFEST_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
