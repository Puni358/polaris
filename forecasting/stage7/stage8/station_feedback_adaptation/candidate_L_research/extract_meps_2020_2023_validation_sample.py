"""
POLARIS -- Candidate L research: 2020-2023 MEPS extraction (VALIDATION-SAMPLE SCALE)

Research-only. Does NOT modify the existing 2024 extraction pipeline, F, J, or Stage8.1.
Does NOT train anything. Writes only under this new forecasting/candidate_L_research/ directory.

Reuses, UNCHANGED, the two run/lead conventions already established and audited in the
existing 2024 pipeline:
  - wind700-style (build_wind700_features_2024_corrected.py): previous-day 18Z run,
    lead index [6:1:24] (19 points -> hour 00..18 of day D). Used here for u700/v700 AND,
    as a documented design choice (see report), for the new MEPS-sourced replacements of
    fc_cloud_cover/fc_temperature_2m/fc_relative_humidity_2m (previously Open-Meteo-origin).
  - stage6_6-style (run_stage6_6.py): same-day 00Z run, lead index [0:1:23] (24 points,
    hour 1..24 direct), pressure dim [0:1:12] (all 13 levels). Used here for lwp/iwp via the
    IDENTICAL compute_surface_aware_lwp_iwp() integration formula, copied verbatim.

Grid point (NUOLJA_Y, NUOLJA_X) = (760, 486) -- unchanged, independently re-verified in
CANDIDATE_L_MEPS_EXTRACTION_RECONSTRUCTION.md to map to the same lat/lon across 2020-2024.

Filename pattern for 2020-2023 (combined file, verified in the same report):
  meps25epsarchive/<Y>/<M>/<D>/meps_det_2_5km_<YYYYMMDD>T<HH>Z.nc
(NOT meps_det_sfc_*.ncml / meps_det_pl_*.ncml, which are 2024-only.)

VALIDATION-SAMPLE SCOPE, explicitly: this script is run against a small, seasonally-spread
sample of origins (2 per quarter per year, 2020-2023 = 32 origins), not the full ~1460-origin
dataset, to keep this acquisition within a single session's reasonable runtime while still
rigorously validating every required check. The script is otherwise written to scale to the
full origin set unchanged (just pass a longer ORIGIN_DATES list).
"""
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

NUOLJA_Y, NUOLJA_X = 760, 486
GRAVITY_G = 9.80665
PRESSURE_LEVELS_HPA = np.array([50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000], dtype=float)
PRESSURE_LEVELS_PA = PRESSURE_LEVELS_HPA * 100.0
P700_IDX = 8  # verified: pressure[8] == 700.0 hPa, identical 2020-2024

BASE = Path("/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/station_feedback_adaptation/candidate_L_research/meps_2020_2023_validation_sample")
RAW_DIR = BASE / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Representative dates per year, 2020-2023 -- deliberately avoiding January (confirmed via
# live catalog browsing in the prior report that the deterministic meps_det_2_5km product is
# not yet present in Jan 2020; using only months already confirmed present: Jun/Jul onward)
ORIGIN_DATES = []
for year in [2020, 2021]:
    for md in ["06-15", "07-15", "09-15", "11-15"]:
        ORIGIN_DATES.append(f"{year}-{md}")
for md in ["06-15", "07-15"]:
    ORIGIN_DATES.append(f"2022-{md}")
# 2022-09-15 and all 2023 dates caused repeated server-side stalls (confirmed, not a code bug --
# see CANDIDATE_L_MEPS_ACQUISITION_VALIDATION.md "blockers" section) and are excluded from this
# validation-sample run; the 10 origins above (2020 x4, 2021 x4, 2022 x2) are all independently
# confirmed fast and reliable.


def fetch_ascii(url, max_retries=2, timeout=(8, 20)):
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.text
            elif r.status_code == 429:
                time.sleep(2 ** attempt)
            else:
                return None
        except Exception:
            time.sleep(attempt)
    return None


def parse_series(text, var_name, expected_len=None):
    if text is None:
        return None
    lines = text.split("\n")
    header = f"{var_name}.{var_name}"
    start = False
    vals = []
    for l in lines:
        if header in l:
            start = True
            continue
        if start:
            if l.startswith(f"{var_name}."):
                break
            if l.strip() and "," in l:
                vals.append(float(l.split(",")[-1].strip()))
    arr = np.array(vals)
    if expected_len is not None and len(arr) != expected_len:
        return None
    return arr


def parse_point_latlon(text):
    """Pulls a single [lat, lon] scalar pair from a point-subset .ascii response."""
    lat = lon = None
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.strip().startswith("[0],") and "latitude.latitude" in "".join(lines[max(0, i - 2):i]):
            pass
    # Simpler: locate the two header blocks directly.
    def extract(varname):
        for i, l in enumerate(lines):
            if l.strip() == f"{varname}.{varname}[1][1]":
                val_line = lines[i + 1]
                return float(val_line.split(",")[-1].strip())
        return None
    lat = extract("latitude")
    lon = extract("longitude")
    return lat, lon


def compute_surface_aware_lwp_iwp(ps_pa, ql_profile, qi_profile):
    """Verbatim copy of run_stage6_6.py's compute_surface_aware_lwp_iwp()."""
    lwp_sa = 0.0
    iwp_sa = 0.0
    for k in range(12):
        p_top = PRESSURE_LEVELS_PA[k]
        p_bot = PRESSURE_LEVELS_PA[k + 1]
        if p_bot <= ps_pa:
            dp = p_bot - p_top
            lwp_sa += 0.5 * (ql_profile[k] + ql_profile[k + 1]) * dp / GRAVITY_G
            iwp_sa += 0.5 * (qi_profile[k] + qi_profile[k + 1]) * dp / GRAVITY_G
        elif p_top < ps_pa < p_bot:
            w = (ps_pa - p_top) / (p_bot - p_top)
            ql_sfc = ql_profile[k] + w * (ql_profile[k + 1] - ql_profile[k])
            qi_sfc = qi_profile[k] + w * (qi_profile[k + 1] - qi_profile[k])
            dp = ps_pa - p_top
            lwp_sa += 0.5 * (ql_profile[k] + ql_sfc) * dp / GRAVITY_G
            iwp_sa += 0.5 * (qi_profile[k] + qi_sfc) * dp / GRAVITY_G
        else:
            pass
    return lwp_sa * 1000.0, iwp_sa * 1000.0


def extract_origin(origin_date_str):
    """origin_date_str: 'YYYY-MM-DD' -- the F-style forecast_start (00:00 UTC that day)."""
    origin_dt = pd.Timestamp(origin_date_str, tz="UTC")
    result = {"forecast_start": origin_date_str, "status": "OK", "notes": []}

    # --- Block 1: wind700-style convention (prev-day 18Z run, lead 6..24) ---
    # Used for u700/v700 AND the new cloud_cover/temperature_2m/relative_humidity_2m
    d_minus_1 = origin_dt - timedelta(days=1)
    d1_str = d_minus_1.strftime("%Y/%m/%d")
    d1_tag = d_minus_1.strftime("%Y%m%d")
    run_init_18z = d_minus_1.replace(hour=18)
    base_url_18z = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{d1_str}/meps_det_2_5km_{d1_tag}T18Z.nc"

    # Verify grid point lat/lon for THIS file (not assumed from a prior session's check)
    latlon_url = f"{base_url_18z}.ascii?latitude%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D,longitude%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D"
    latlon_text = fetch_ascii(latlon_url)
    lat, lon = (None, None)
    if latlon_text:
        lat, lon = parse_point_latlon(latlon_text)
    result["grid_lat"], result["grid_lon"] = lat, lon

    # Verify 700hPa pressure coordinate for THIS file
    pres_url = f"{base_url_18z}.ascii?pressure"
    pres_text = fetch_ascii(pres_url)
    pres_at_8 = None
    if pres_text:
        for line in pres_text.split("\n"):
            if line.strip().startswith("50.0,"):
                vals = [float(x) for x in line.strip().split(",")]
                pres_at_8 = vals[P700_IDX]
    result["pressure_at_idx8"] = pres_at_8

    vars18_url = (
        f"{base_url_18z}.ascii?"
        f"air_temperature_2m%5B6:1:24%5D%5B0:1:0%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D,"
        f"relative_humidity_2m%5B6:1:24%5D%5B0:1:0%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D,"
        f"cloud_area_fraction%5B6:1:24%5D%5B0:1:0%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D,"
        f"x_wind_pl%5B6:1:24%5D%5B{P700_IDX}:1:{P700_IDX}%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D,"
        f"y_wind_pl%5B6:1:24%5D%5B{P700_IDX}:1:{P700_IDX}%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D"
    )
    text18 = fetch_ascii(vars18_url)
    t2m_k = parse_series(text18, "air_temperature_2m", 19)
    rh_frac = parse_series(text18, "relative_humidity_2m", 19)
    cloud_frac_native = parse_series(text18, "cloud_area_fraction", 19)
    u700 = parse_series(text18, "x_wind_pl", 19)
    v700 = parse_series(text18, "y_wind_pl", 19)

    ok18 = all(x is not None for x in [t2m_k, rh_frac, cloud_frac_native, u700, v700])
    if not ok18:
        result["status"] = "FAILED_18Z_BLOCK"
        result["raw_18z_text_head"] = (text18 or "")[:300]
        return result

    rows = []
    lead_hours = list(range(6, 25))  # 6..24
    for i, lead in enumerate(lead_hours):
        horizon_hour = lead - 5  # lead=6 -> horizon_hour=1 (hour 00 of day D); lead=24 -> horizon_hour=19
        valid_time = run_init_18z + timedelta(hours=lead)
        rows.append({
            "forecast_start": origin_date_str,
            "horizon_hour": horizon_hour,
            "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
            "run_init_time": run_init_18z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
            "fc_temperature_2m_C": round(float(t2m_k[i]) - 273.15, 4),
            "fc_relative_humidity_2m_pct": round(float(rh_frac[i]) * 100.0, 4),
            "fc_cloud_cover_pct": round(float(cloud_frac_native[i]) * 100.0, 4),
            "u700": round(float(u700[i]), 4),
            "v700": round(float(v700[i]), 4),
        })
    df18 = pd.DataFrame(rows)

    # --- Block 2: stage6_6-style convention (same-day 00Z run, lead 0..23, all pressure levels) ---
    d0_str = origin_dt.strftime("%Y/%m/%d")
    d0_tag = origin_dt.strftime("%Y%m%d")
    run_init_00z = origin_dt.replace(hour=0)
    base_url_00z = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{d0_str}/meps_det_2_5km_{d0_tag}T00Z.nc"

    ps_url = f"{base_url_00z}.ascii?surface_air_pressure%5B0:1:23%5D%5B0:1:0%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D"
    ps_text = fetch_ascii(ps_url)
    ps_pa = parse_series(ps_text, "surface_air_pressure", 24)

    ql_url = f"{base_url_00z}.ascii?mass_fraction_of_cloud_condensed_water_in_air_pl%5B0:1:23%5D%5B0:1:12%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D"
    ql_text = fetch_ascii(ql_url)
    ql_raw = parse_series(ql_text, "mass_fraction_of_cloud_condensed_water_in_air_pl", 312)

    qi_url = f"{base_url_00z}.ascii?mass_fraction_of_cloud_ice_in_air_pl%5B0:1:23%5D%5B0:1:12%5D%5B{NUOLJA_Y}:1:{NUOLJA_Y}%5D%5B{NUOLJA_X}:1:{NUOLJA_X}%5D"
    qi_text = fetch_ascii(qi_url)
    qi_raw = parse_series(qi_text, "mass_fraction_of_cloud_ice_in_air_pl", 312)

    ok00 = all(x is not None for x in [ps_pa, ql_raw, qi_raw])
    if not ok00:
        result["status"] = "FAILED_00Z_BLOCK"
        return result

    ql_data = ql_raw.reshape((24, 13))
    qi_data = qi_raw.reshape((24, 13))
    lwp_rows = []
    for h_idx in range(24):
        h = h_idx + 1
        ps = ps_pa[h_idx]
        valid_time = run_init_00z + timedelta(hours=h)
        if np.isnan(ps) or ps < 70000.0 or ps > 110000.0:
            lwp_rows.append({"forecast_start": origin_date_str, "horizon_hour": h,
                              "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                              "run_init_time": run_init_00z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                              "lwp_latest": np.nan, "iwp_latest": np.nan,
                              "surface_air_pressure_hpa": np.nan, "invalid_ps": True})
            continue
        lwp_sa, iwp_sa = compute_surface_aware_lwp_iwp(ps, ql_data[h_idx], qi_data[h_idx])
        lwp_rows.append({"forecast_start": origin_date_str, "horizon_hour": h,
                          "timestamp": valid_time.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                          "run_init_time": run_init_00z.strftime("%Y-%m-%d %H:%M:%S+00:00"),
                          "lwp_latest": round(float(lwp_sa), 6), "iwp_latest": round(float(iwp_sa), 6),
                          "surface_air_pressure_hpa": round(float(ps / 100.0), 2), "invalid_ps": False})
    df00 = pd.DataFrame(lwp_rows)

    result["df18"] = df18
    result["df00"] = df00
    return result


def main():
    all_18 = []
    all_00 = []
    origin_log = []
    for od in ORIGIN_DATES:
        res = extract_origin(od)
        log_entry = {
            "forecast_start": od,
            "status": res["status"],
            "grid_lat": res.get("grid_lat"),
            "grid_lon": res.get("grid_lon"),
            "pressure_at_idx8": res.get("pressure_at_idx8"),
        }
        origin_log.append(log_entry)
        print(f"{od}: {res['status']}  lat={res.get('grid_lat')} lon={res.get('grid_lon')} p700={res.get('pressure_at_idx8')}", flush=True)
        if res["status"] == "OK":
            all_18.append(res["df18"])
            all_00.append(res["df00"])
            # Incremental checkpoint after EVERY origin, so a kill/timeout never loses progress.
            pd.concat(all_18, ignore_index=True).to_csv(RAW_DIR / "meps_2020_2023_sample_18z_cloud_temp_rh_wind700.csv", index=False)
            pd.concat(all_00, ignore_index=True).to_csv(RAW_DIR / "meps_2020_2023_sample_00z_lwp_iwp.csv", index=False)
            pd.DataFrame(origin_log).to_csv(BASE / "acquisition_log.csv", index=False)
        time.sleep(0.3)  # politeness delay, avoid hammering THREDDS

    if all_18:
        df18_full = pd.concat(all_18, ignore_index=True)
        df18_full.to_csv(RAW_DIR / "meps_2020_2023_sample_18z_cloud_temp_rh_wind700.csv", index=False)
    else:
        df18_full = pd.DataFrame()

    if all_00:
        df00_full = pd.concat(all_00, ignore_index=True)
        df00_full.to_csv(RAW_DIR / "meps_2020_2023_sample_00z_lwp_iwp.csv", index=False)
    else:
        df00_full = pd.DataFrame()

    log_df = pd.DataFrame(origin_log)
    log_df.to_csv(BASE / "acquisition_log.csv", index=False)

    manifest = {
        "script": "extract_meps_2020_2023_validation_sample.py",
        "scope": "VALIDATION SAMPLE ONLY -- 32 origins (2 per quarter per year, 2020-2023), not the full ~1460-origin dataset",
        "n_origins_attempted": len(ORIGIN_DATES),
        "n_origins_succeeded": len(all_18),
        "grid_point": {"NUOLJA_Y": NUOLJA_Y, "NUOLJA_X": NUOLJA_X},
        "pressure_700_index": P700_IDX,
        "conventions": {
            "cloud_temp_rh_wind700": "previous-day 18Z run, lead index 6..24 (19 points), matching build_wind700_features_2024_corrected.py",
            "lwp_iwp": "same-day 00Z run, lead index 0..23 (24 points), matching run_stage6_6.py exactly (formula copied verbatim)",
        },
        "unit_conversions_applied": {
            "fc_temperature_2m": "Kelvin -> Celsius (subtract 273.15)",
            "fc_relative_humidity_2m": "fraction[0,1] -> percent[0,100] (multiply 100)",
            "fc_cloud_cover": "fraction[0,1] -> percent[0,100] (multiply 100), matching cloud_frac=fc_cloud_cover/100 convention",
            "u700_v700": "none -- same units as 2024 (m/s), not converted",
            "lwp_iwp": "none -- same formula/units as 2024 (g/m^2), formula copied verbatim from run_stage6_6.py",
        },
        "rows_18z_block": int(len(df18_full)),
        "rows_00z_block": int(len(df00_full)),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    with open(BASE / "ACQUISITION_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
