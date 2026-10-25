#!/usr/bin/env python3
"""
POLARIS — Stage 8.1 upstream dependency: LWP/IWP cloud microphysics
(surface-aware vertical integration), 2025.

Exact replica of the extraction method in
forecasting/stage6/stage6_6_lwp_iwp/run_stage6_6.py (2024, LOCKED):
same source (MET Norway meps25epsarchive deterministic surface +
pressure-level files via THREDDS OPeNDAP ASCII, same-day 00Z run),
same station grid cell, same 13 pressure levels, same surface-aware
trapezoidal vertical integration formula
(compute_surface_aware_lwp_iwp, unchanged), same checkpointed/
resumable/atomic extraction pattern.

CAUSAL ALIGNMENT FIX (reported, not silently applied): the 2024
artifact (lwp_iwp_extracted_features.csv) has horizon_hour=1 ==
valid_time = forecast_start + 1h (independently confirmed: its row
forecast_start=2024-01-20, horizon_hour=1 has valid_time=
2024-01-20 01:00:00, not 00:00:00). Every other Stage 8.1 feature
source (Stage 3b/4, NWP, and this session's rebuilt terrain and
u700/v700 dependencies) uses horizon_hour=1 == forecast_start + 0h.
Because the eventual merge in stage8_1 is a plain join on
(forecast_start, horizon_hour), this is the same one-hour
misalignment bug found independently in the 700hPa wind dependency.
This script fixes it (valid_time = forecast_start + (horizon_hour-1)h)
rather than reproducing it; the 2024 file is left untouched.

Origins: unique forecast_start values from the 2025 Stage 4
ensemble predictions (364 origins, 2025-01-02..2025-12-31) --
exactly mirroring the 2024 script's origin source
(forecasting/stage4/stage4_results/ensemble_predictions.csv -> 347 origins).
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

import numpy as np
import pandas as pd

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage6" / "stage6_6_lwp_iwp_2025"
STAGE_DIR.mkdir(parents=True, exist_ok=True)

STAGE4_PREDS_PATH = BASE_DIR / "forecasting/stage4" / "stage4_results_2025" / "ensemble_predictions.csv"

CHECKPOINT_PATH = STAGE_DIR / "extraction_checkpoint.json"
FEATURES_PATH = STAGE_DIR / "lwp_iwp_extracted_features_2025.csv"
AUDIT_PATH = STAGE_DIR / "pre_cv_integrity_audit_2025.csv"
MANIFEST_PATH = STAGE_DIR / "lwp_iwp_2025_MANIFEST.json"

NUOLJA_Y, NUOLJA_X = 760, 486  # same station grid cell as 2024 (same archived grid definition)
PRESSURE_LEVELS_HPA = np.array([50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000], dtype=float)
PRESSURE_LEVELS_PA = PRESSURE_LEVELS_HPA * 100.0
GRAVITY_G = 9.80665


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
            elif r.status_code == 429:
                time.sleep(2 ** attempt + 1)
        except Exception:
            time.sleep(attempt)
    return None


def compute_surface_aware_lwp_iwp(ps_pa, ql_profile, qi_profile):
    """Unchanged from run_stage6_6.py (2024, LOCKED)."""
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
    return lwp_sa * 1000.0, iwp_sa * 1000.0


def process_single_origin(origin_idx, origin_ts_str):
    origin_dt = pd.Timestamp(origin_ts_str)
    date_str = origin_dt.strftime("%Y/%m/%d")
    tag_str = origin_dt.strftime("%Y%m%dT00Z")
    meps_run_id = f"meps_det_{tag_str}"

    url_ps = (f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/'
               f'meps_det_sfc_{tag_str}.ncml.ascii?surface_air_pressure[0:1:23][0:1:0]'
               f'[{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]')
    ps_pa = fetch_meps_variable(url_ps, 'surface_air_pressure')
    if ps_pa is None or len(ps_pa) != 24:
        return {"status": "FAILED", "reason": "Failed to fetch surface_air_pressure", "origin": origin_ts_str, "origin_index": origin_idx}

    url_ql = (f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/'
               f'meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:23][0:1:12]'
               f'[{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]')
    ql_raw = fetch_meps_variable(url_ql, 'mass_fraction_of_cloud_condensed_water_in_air_pl')
    if ql_raw is None or len(ql_raw) != 312:
        return {"status": "FAILED", "reason": "Failed to fetch cloud_condensed_water (ql)", "origin": origin_ts_str, "origin_index": origin_idx}

    url_qi = (f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/'
               f'meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_ice_in_air_pl[0:1:23][0:1:12]'
               f'[{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]')
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
            # FIX vs 2024: valid_time = forecast_start + (h-1), not + h,
            # so horizon_hour=1 == forecast_start + 0h (matches rest of pipeline).
            "valid_time": (origin_dt + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%d %H:%M:%S"),
            "forecast_reference_time": origin_ts_str,
            "surface_air_pressure_hpa": round(float(ps / 100.0), 2),
            "lwp_latest": round(float(lwp_sa), 6),
            "iwp_latest": round(float(iwp_sa), 6),
            "meps_run_id": meps_run_id,
        })

    return {"status": "COMPLETE", "records": records, "meps_run": meps_run_id, "origin": origin_ts_str, "origin_index": origin_idx}


def run_extraction(origins_list, num_workers=6):
    print("=" * 80)
    print("POLARIS — LWP/IWP feature extraction (2025)")
    print("=" * 80)

    checkpoint = {}
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            checkpoint = json.load(f)
        print(f"Resuming from checkpoint: {len(checkpoint)}/{len(origins_list)} origins already complete.")

    all_records = []
    if FEATURES_PATH.exists():
        all_records = pd.read_csv(FEATURES_PATH).to_dict("records")

    pending = [o for o in origins_list if o not in checkpoint or checkpoint[o].get("status") != "COMPLETE"]
    print(f"Total origins: {len(origins_list)} | Pending: {len(pending)} | Workers: {num_workers}")

    def task(origin_str):
        idx = origins_list.index(origin_str)
        return process_single_origin(idx, origin_str)

    completed = len(origins_list) - len(pending)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_origin = {executor.submit(task, o): o for o in pending}
        for future in concurrent.futures.as_completed(future_to_origin):
            origin_str = future_to_origin[future]
            try:
                res = future.result()
            except Exception as exc:
                res = {"status": "FAILED", "reason": str(exc), "origin": origin_str}

            if res["status"] == "COMPLETE":
                all_records.extend(res["records"])
                checkpoint[origin_str] = {"status": "COMPLETE", "meps_run": res["meps_run"]}
                completed += 1
            else:
                checkpoint[origin_str] = {"status": res["status"], "error": res.get("reason")}
                print(f"  FAILED origin {origin_str}: {res.get('reason')}")

            atomic_write_csv(pd.DataFrame(all_records), FEATURES_PATH)
            atomic_write_json(checkpoint, CHECKPOINT_PATH)

            if completed % 20 == 0 or completed == len(origins_list):
                print(f"[{completed}/{len(origins_list)}] complete")
                sys.stdout.flush()

    failed = [o for o, v in checkpoint.items() if v.get("status") != "COMPLETE"]
    if failed:
        raise RuntimeError(f"{len(failed)} origins failed extraction: {failed[:5]}...")

    return pd.DataFrame(all_records)


def main():
    s4_hash = sha256_of(STAGE4_PREDS_PATH)
    s4_preds = pd.read_csv(STAGE4_PREDS_PATH)
    origins_list = sorted([str(o) for o in s4_preds["forecast_start"].unique()])
    print(f"2025 origins (from Stage 4 ensemble predictions, hash {s4_hash[:12]}...): {len(origins_list)}")

    df_feat = run_extraction(origins_list)

    # ============================================================
    # VALIDATION (mirrors run_integrity_audit in run_stage6_6.py)
    # ============================================================
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    audit_checks = []

    def add_check(name, passed, detail):
        audit_checks.append({"check_name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")

    unique_origs = df_feat["forecast_start"].nunique()
    add_check(f"{len(origins_list)} Origins Present", unique_origs == len(origins_list), f"Found {unique_origs} / {len(origins_list)} origins")
    assert unique_origs == len(origins_list)

    horizons_per_orig = df_feat.groupby("forecast_start")["horizon_hour"].count()
    correct_horizons = (horizons_per_orig == 24).all()
    add_check("24 Horizons / Origin", correct_horizons, f"Origins with 24 horizons: {(horizons_per_orig == 24).sum()} / {unique_origs}")
    assert correct_horizons

    expected_rows = len(origins_list) * 24
    add_check("Total Row Count", len(df_feat) == expected_rows, f"Total rows: {len(df_feat)} / {expected_rows}")
    assert len(df_feat) == expected_rows

    dups = df_feat.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    add_check("No Duplicate Rows", dups == 0, f"Duplicate rows found: {dups}")
    assert dups == 0

    nans = df_feat[["lwp_latest", "iwp_latest", "surface_air_pressure_hpa"]].isna().sum().sum()
    infs = np.isinf(df_feat[["lwp_latest", "iwp_latest"]].values).sum()
    add_check("No NaN/Inf Values", nans == 0 and infs == 0, f"NaNs: {nans}, Infs: {infs}")
    assert nans == 0 and infs == 0

    lwp_min, lwp_max = df_feat["lwp_latest"].min(), df_feat["lwp_latest"].max()
    iwp_min, iwp_max = df_feat["iwp_latest"].min(), df_feat["iwp_latest"].max()
    ps_min, ps_max = df_feat["surface_air_pressure_hpa"].min(), df_feat["surface_air_pressure_hpa"].max()
    range_pass = (lwp_min >= 0.0 and lwp_max <= 3000.0) and (iwp_min >= 0.0 and iwp_max <= 500.0) and (ps_min >= 800.0 and ps_max <= 1050.0)
    add_check("Physical Ranges", range_pass,
               f"LWP: [{lwp_min:.2f}, {lwp_max:.2f}] g/m2, IWP: [{iwp_min:.2f}, {iwp_max:.2f}] g/m2, Ps: [{ps_min:.1f}, {ps_max:.1f}] hPa "
               f"(2024 reference: LWP [0,1598.28], IWP [0,157.86], Ps [891.8,974.1])")
    assert range_pass

    add_check("Surface Pressure Bound", ps_max <= 1000.0, f"Max surface pressure: {ps_max:.2f} hPa (< 1000 hPa)")
    assert ps_max <= 1000.0

    # Causal alignment check (the fix vs 2024)
    df_feat["_valid"] = pd.to_datetime(df_feat["valid_time"])
    df_feat["_fs"] = pd.to_datetime(df_feat["forecast_start"])
    alignment_ok = ((df_feat["_valid"] - df_feat["_fs"]) == pd.to_timedelta(df_feat["horizon_hour"] - 1, unit="h")).all()
    add_check("Horizon/valid_time alignment (fix vs 2024 off-by-one)", alignment_ok,
               "valid_time == forecast_start + (horizon_hour-1)h for all rows (2024 artifact used +horizon_hour, confirmed off by 1h)")
    assert alignment_ok
    df_feat = df_feat.drop(columns=["_valid", "_fs"])

    expected_cols = ["origin_index", "forecast_start", "horizon_hour", "valid_time",
                      "forecast_reference_time", "surface_air_pressure_hpa", "lwp_latest",
                      "iwp_latest", "meps_run_id"]
    add_check("Schema matches 2024", list(df_feat.columns) == expected_cols, str(list(df_feat.columns)))
    assert list(df_feat.columns) == expected_cols

    atomic_write_csv(pd.DataFrame(audit_checks), AUDIT_PATH)
    atomic_write_csv(df_feat, FEATURES_PATH)
    out_hash = sha256_of(FEATURES_PATH)
    print(f"\nOutput SHA256: {out_hash}")
    print(f"Output path:   {FEATURES_PATH}")

    manifest = {
        "output_file": str(FEATURES_PATH),
        "sha256": out_hash,
        "row_count": int(len(df_feat)),
        "unique_origins": int(unique_origs),
        "columns": expected_cols,
        "input_hashes": {"stage4_predictions_2025": s4_hash},
        "source": "MET Norway meps25epsarchive (meps_det_sfc + meps_det_pl, same-day 00Z run), via thredds.met.no OPeNDAP ASCII",
        "method": "surface-aware trapezoidal vertical integration, unchanged from forecasting/stage6/stage6_6_lwp_iwp/run_stage6_6.py (2024, LOCKED)",
        "station_grid_cell": {"y": NUOLJA_Y, "x": NUOLJA_X, "reused_from_2024": True},
        "defect_found_in_2024_artifact_and_fixed_here": {
            "defect": "off_by_one_horizon_hour",
            "detail": "2024's horizon_hour=1 == forecast_start+1h; downstream merges join purely on (forecast_start, horizon_hour) against sources that use horizon_hour=1 == forecast_start+0h.",
            "evidence": "independently confirmed: 2024 row (forecast_start=2024-01-20, horizon_hour=1) has valid_time=2024-01-20 01:00:00, not 00:00:00.",
            "action": "fixed in this 2025 build; 2024 file left unmodified",
        },
        "causal_design_note": (
            "Same-day 00Z run is used (reference_time == forecast_start), identical to "
            "the 2024 method -- not changed here. At horizon_hour=1 this makes "
            "reference_time == valid_time exactly (zero lead), a pre-existing "
            "property of the 2024 design, not something this script altered."
        ),
        "validation": {c["check_name"]: c["status"] for c in audit_checks},
    }
    atomic_write_json(manifest, MANIFEST_PATH)
    print(f"\nManifest written to: {MANIFEST_PATH}")
    print("Done!")


if __name__ == "__main__":
    main()
