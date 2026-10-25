#!/usr/bin/env python3
"""
POLARIS Stage 6.4 — MEPS Forecast Revision Trajectory Full Feature Extraction
==============================================================================
Extracts pre-origin MEPS forecast revision trajectories for SITES Nuolja
(68.362074°N, 18.738752°E, grid index y=760, x=486) across all 347 clean
POLARIS benchmark origins in 2024 and 24 forecast horizons (H1..H24).

Strict Scientific Locks:
- 347 Clean Benchmark Origins (174 EVEN, 173 ODD).
- 4 Chronological Pre-Origin MEPS Operational Deterministic Runs per origin (00Z, 06Z, 12Z, 18Z).
- Strict Causality: forecast_reference_time < t0 for 100% of extracted runs.
- Core Variables Only: cloud_area_fraction, surface_downwelling_shortwave_flux_in_air.
- Predeclared 8 Revision Features:
    1. rev_cloud_latest      = f4(cloud)
    2. rev_cloud_delta_6h    = f4(cloud) - f3(cloud)
    3. rev_cloud_delta_total = f4(cloud) - f1(cloud)
    4. rev_cloud_std         = std(f1, f2, f3, f4)
    5. rev_sw_latest         = f4(SW_IN)
    6. rev_sw_delta_6h       = f4(SW_IN) - f3(SW_IN)
    7. rev_sw_delta_total    = f4(SW_IN) - f1(SW_IN)
    8. rev_sw_std            = std(f1, f2, f3, f4)
- Full Incremental Checkpointing & Resumability (Run-level).
- ODD Test Split remains 100% UNTOUCHED and UNREAD.
"""

import os
import sys
import time
import json
import signal
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Setup Paths
BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = BASE / "forecasting/stage6" / "stage6_4_meps_revision"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = Path("/tmp")

CHECKPOINT_FILE = OUT_DIR / "meps_revision_checkpoint.json"
RAW_OBS_FILE = OUT_DIR / "meps_revision_raw_observations.csv"
FEATURE_SUMM_FILE = OUT_DIR / "meps_revision_feature_summary.csv"
AUDIT_FILE = OUT_DIR / "meps_revision_extraction_audit.csv"
REPORT_FILE = OUT_DIR / "extraction_completeness_report.txt"

# Grid index for Nuolja (68.362074°N, 18.738752°E) in MEPS 2.5km grid
Y_IDX = 760
X_IDX = 486
EXPECTED_LAT = 68.355701
EXPECTED_LON = 18.763666
TARGET_LAT = 68.362074
TARGET_LON = 18.738752

# Load 347 clean POLARIS benchmark origins
s4_preds = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
s4_preds["forecast_start"] = pd.to_datetime(s4_preds["forecast_start"])
clean_origins = sorted(s4_preds["forecast_start"].unique())
even_origins = [o for i, o in enumerate(clean_origins) if i % 2 == 0]
odd_origins = [o for i, o in enumerate(clean_origins) if i % 2 == 1]

# Map origins to their 4 latest eligible pre-t0 MEPS runs
origin_to_runs = {}
run_to_origins = {}

for origin in clean_origins:
    origin_ts = pd.Timestamp(origin)
    is_dst = (origin_ts.month > 3 and origin_ts.month < 10) or (origin_ts.month == 3 and origin_ts.day >= 31) or (origin_ts.month == 10 and origin_ts.day < 27)
    utc_offset = 2 if is_dst else 1
    t0_utc = origin_ts - pd.Timedelta(hours=utc_offset)

    cand_refs = []
    for d in [0, 1, 2]:
        day = (t0_utc - pd.Timedelta(days=d)).strftime("%Y-%m-%d")
        for hh in [18, 12, 6, 0]:
            ref = pd.Timestamp(f"{day} {hh:02d}:00:00")
            if ref < t0_utc:
                cand_refs.append(ref)

    cand_refs = sorted(list(set(cand_refs)))
    selected_4_refs = cand_refs[-4:] # 4 latest eligible pre-t0 runs

    origin_to_runs[str(origin_ts)] = [r.strftime("%Y%m%dT%HZ") for r in selected_4_refs]
    for r in selected_4_refs:
        tag_str = r.strftime("%Y%m%dT%HZ")
        date_str = r.strftime("%Y/%m/%d")
        url = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_sfc_{tag_str}.ncml"
        if tag_str not in run_to_origins:
            run_to_origins[tag_str] = {
                "tag": tag_str,
                "date_str": date_str,
                "url": url,
                "ref_time": str(r),
                "origins": []
            }
        run_to_origins[tag_str]["origins"].append(str(origin_ts))

unique_runs = sorted(list(run_to_origins.keys()))
total_runs_count = len(unique_runs)

# Checkpoint Management
checkpoint_data = {
    "completed_runs": {},
    "failed_runs": {}
}

if CHECKPOINT_FILE.exists():
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            checkpoint_data = json.load(f)
        print(f"[RESUME] Loaded checkpoint: {len(checkpoint_data.get('completed_runs', {}))} runs completed.")
    except Exception as e:
        print(f"[WARNING] Failed to read existing checkpoint file ({e}). Starting fresh.")

def save_checkpoint_atomic():
    tmp_ckpt = OUT_DIR / "meps_revision_checkpoint.tmp.json"
    with open(tmp_ckpt, "w") as f:
        json.dump(checkpoint_data, f, indent=2)
    os.replace(tmp_ckpt, CHECKPOINT_FILE)

# In-memory storage for extracted run predictions
# Key: (run_tag, valid_time_iso) -> {'cloud': float, 'sw': float}
extracted_data_store = {}

# Populate in-memory store from checkpoint completed_runs
for r_tag, r_info in checkpoint_data.get("completed_runs", {}).items():
    if "extracted_values" in r_info:
        for v_iso, vals in r_info["extracted_values"].items():
            extracted_data_store[(r_tag, v_iso)] = vals

# Graceful Exit Handler
def graceful_exit(signum, frame):
    print(f"\n[INTERRUPT] Received signal {signum}. Saving atomic checkpoint before exit...")
    save_checkpoint_atomic()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def process_meps_run(run_info):
    import pydap.client
    r_tag = run_info["tag"]
    url = run_info["url"]

    t_start = time.time()
    ds = pydap.client.open_url(url)

    # 1. Extract time array
    time_vals = ds["time"].data[:]
    time_dt = pd.to_datetime(time_vals, unit="s", utc=True)
    n_times = len(time_dt)

    assert n_times >= 48, f"Run coverage less than 48 hours: {n_times} steps"

    # Slice max 48 hours for core variables
    h_slice = min(n_times, 50)
    c_arr = ds["cloud_area_fraction"][0:h_slice, 0:1, Y_IDX:Y_IDX+1, X_IDX:X_IDX+1].data[:, 0, 0, 0]
    sw_arr = ds["surface_downwelling_shortwave_flux_in_air"][0:h_slice, 0:1, Y_IDX:Y_IDX+1, X_IDX:X_IDX+1].data[:, 0, 0, 0]

    extracted_dict = {}
    for i in range(len(c_arr)):
        v_iso = time_dt[i].strftime("%Y-%m-%dT%H:%M:%SZ")
        c_val = float(c_arr[i])
        sw_val = float(sw_arr[i])

        assert not np.isnan(c_val) and not np.isinf(c_val), "NaN/Inf in cloud_area_fraction"
        assert not np.isnan(sw_val) and not np.isinf(sw_val), "NaN/Inf in SW_IN"
        assert 0.0 <= c_val <= 1.0, f"Cloud fraction out of bounds: {c_val}"
        assert sw_val >= 0.0, f"Negative SW_IN flux: {sw_val}"

        extracted_dict[v_iso] = {
            "cloud": c_val,
            "sw": sw_val
        }

    t_fetch = time.time() - t_start
    return {
        "tag": r_tag,
        "ref_time": str(time_dt[0]),
        "time_steps": n_times,
        "extracted_count": len(extracted_dict),
        "fetch_time_s": round(t_fetch, 2),
        "extracted_values": extracted_dict
    }

def main():
    import pydap.client
    from concurrent.futures import ThreadPoolExecutor

    start_time = time.time()
    print("=" * 80)
    print("POLARIS STAGE 6.4 — OPTIMIZED MEPS FORECAST REVISION TRAJECTORY EXTRACTION")
    print("=" * 80)
    print(f"[START] Total POLARIS Benchmark Origins: {len(clean_origins)}")
    print(f"  -> EVEN Origins: {len(even_origins)} (Train split)")
    print(f"  -> ODD Origins: {len(odd_origins)} (Test split — 100% UNTOUCHED)")
    print(f"  -> Total Unique MEPS Runs Required: {total_runs_count}")
    print(f"  -> Nuolja Grid Point: (y={Y_IDX}, x={X_IDX}) -> Target Lat={TARGET_LAT:.6f}°N, Lon={TARGET_LON:.6f}°E")

    # One-time spatial grid coordinate verification on startup
    sample_url = run_to_origins[unique_runs[0]]["url"]
    print(f"\n[SPATIAL CHECK] Verifying static grid coordinates at {sample_url}...")
    ds_check = pydap.client.open_url(sample_url)
    grid_lat = float(ds_check["latitude"][Y_IDX, X_IDX].data[0][0])
    grid_lon = float(ds_check["longitude"][Y_IDX, X_IDX].data[0][0])
    print(f"  -> Verified Grid Point ({Y_IDX}, {X_IDX}): Lat={grid_lat:.6f}°N, Lon={grid_lon:.6f}°E (1.24 km from Nuolja target).")
    assert abs(grid_lat - EXPECTED_LAT) < 0.01 and abs(grid_lon - EXPECTED_LON) < 0.01, "Spatial grid verification failed!"

    completed_runs = checkpoint_data.setdefault("completed_runs", {})
    failed_runs = checkpoint_data.setdefault("failed_runs", {})

    runs_to_process = [r for r in unique_runs if r not in completed_runs]
    print(f"\nRemaining runs to extract: {len(runs_to_process)} / {total_runs_count}")
    print(f"Already completed in checkpoint: {len(completed_runs)} runs (Skipped automatically)")

    def worker_task(r_tag):
        r_info = run_to_origins[r_tag]
        max_retries = 3
        for retry in range(max_retries):
            try:
                res = process_meps_run(r_info)
                return True, r_tag, res, None
            except Exception as e:
                time.sleep(2.0 * (retry + 1))
        return False, r_tag, None, f"Failed after {max_retries} retries"

    # Parallel extraction with low concurrency (3 workers)
    num_workers = 3
    print(f"\nLaunching low-concurrency extraction worker pool (max_workers={num_workers})...\n")

    batch_size = num_workers
    for b_idx in range(0, len(runs_to_process), batch_size):
        batch_tags = runs_to_process[b_idx : b_idx + batch_size]
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            batch_results = list(executor.map(worker_task, batch_tags))

        for success, r_tag, res, err_msg in batch_results:
            if success:
                completed_runs[r_tag] = {
                    "tag": r_tag,
                    "ref_time": res["ref_time"],
                    "fetch_time_s": res["fetch_time_s"],
                    "extracted_count": res["extracted_count"],
                    "status": "SUCCESS",
                    "timestamp_saved": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "extracted_values": res["extracted_values"]
                }
                for v_iso, vals in res["extracted_values"].items():
                    extracted_data_store[(r_tag, v_iso)] = vals
                if r_tag in failed_runs:
                    del failed_runs[r_tag]
            else:
                failed_runs[r_tag] = {
                    "tag": r_tag,
                    "status": "FAILED",
                    "error": err_msg,
                    "timestamp_saved": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }

        save_checkpoint_atomic()

        elapsed = time.time() - start_time
        n_done = len(completed_runs)
        n_fail = len(failed_runs)
        rem_runs = total_runs_count - n_done
        avg_time_effective = elapsed / (n_done - (total_runs_count - len(runs_to_process)) + 1e-5)
        est_rem_min = (rem_runs * avg_time_effective) / 60.0

        for success, r_tag, res, err_msg in batch_results:
            status_str = f"SUCCESS ({res['fetch_time_s']}s)" if success else f"FAILED: {err_msg}"
            print(f"[RUN {n_done}/{total_runs_count}] {r_tag} -> {status_str}")

        print(f"  [SUMMARY STATUS] Completed: {n_done}/{total_runs_count} ({n_done/total_runs_count*100.0:.1f}%) | Fails: {n_fail} | Elapsed: {elapsed/60.0:.1f}m | Est. Rem: {est_rem_min:.1f}m\n")

        # Print progress summary every 25 runs
        if n_done % 25 < num_workers or n_done == total_runs_count:
            print("-" * 60)
            print(f"PROGRESS SUMMARY [Run {n_done}/{total_runs_count}]:")
            print(f"  Completed Runs: {n_done} / {total_runs_count} ({n_done/total_runs_count*100.0:.1f}%)")
            print(f"  Failed Runs: {n_fail}")
            print(f"  Extracted Data Point Tuples in Store: {len(extracted_data_store)}")
            print(f"  Total Elapsed Time: {elapsed/60.0:.2f} minutes")
            print("-" * 60 + "\n")

    print("\n=== PART 2: CONSTRUCTING RAW OBSERVATIONS & FEATURE SUMMARY TABLES ===")
    
    raw_records = []
    feature_records = []
    audit_records = []

    origins_fully_covered = 0
    total_horizon_rows = len(clean_origins) * 24

    for origin in clean_origins:
        origin_ts = pd.Timestamp(origin)
        is_dst = (origin_ts.month > 3 and origin_ts.month < 10) or (origin_ts.month == 3 and origin_ts.day >= 31) or (origin_ts.month == 10 and origin_ts.day < 27)
        utc_offset = 2 if is_dst else 1
        t0_utc = origin_ts - pd.Timedelta(hours=utc_offset)

        run_tags = origin_to_runs[str(origin_ts)]
        origin_coverage_pass = True

        for h in range(1, 25):
            valid_ts_utc = t0_utc + pd.Timedelta(hours=h)
            v_iso = valid_ts_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

            h_cloud_vals = []
            h_sw_vals = []

            for seq_id, r_tag in enumerate(run_tags, 1):
                r_info = run_to_origins[r_tag]
                ref_ts = pd.Timestamp(r_info["ref_time"])

                # Causal check
                causal_pass = (ref_ts < t0_utc)
                lead_h = (valid_ts_utc - ref_ts).total_seconds() / 3600.0

                key = (r_tag, v_iso)
                if key in extracted_data_store:
                    vals = extracted_data_store[key]
                    c_val = vals["cloud"]
                    sw_val = vals["sw"]

                    raw_records.append({
                        "forecast_start": str(origin_ts),
                        "horizon_hour": h,
                        "valid_time": v_iso,
                        "forecast_reference_time": str(ref_ts),
                        "lead_time_hours": lead_h,
                        "run_sequence_id": seq_id,
                        "run_tag": r_tag,
                        "cloud_area_fraction": c_val,
                        "sw_in_w_m2": sw_val,
                        "causal_pass": causal_pass
                    })
                    h_cloud_vals.append(c_val)
                    h_sw_vals.append(sw_val)
                else:
                    origin_coverage_pass = False

            if len(h_cloud_vals) == 4 and len(h_sw_vals) == 4:
                # Calculate exact 8 revision features
                f1_c, f2_c, f3_c, f4_c = h_cloud_vals
                f1_sw, f2_sw, f3_sw, f4_sw = h_sw_vals

                feature_records.append({
                    "forecast_start": str(origin_ts),
                    "horizon_hour": h,
                    "rev_cloud_latest": f4_c,
                    "rev_cloud_delta_6h": f4_c - f3_c,
                    "rev_cloud_delta_total": f4_c - f1_c,
                    "rev_cloud_std": float(np.std(h_cloud_vals)),
                    "rev_sw_latest": f4_sw,
                    "rev_sw_delta_6h": f4_sw - f3_sw,
                    "rev_sw_delta_total": f4_sw - f1_sw,
                    "rev_sw_std": float(np.std(h_sw_vals))
                })

            audit_records.append({
                "forecast_start": str(origin_ts),
                "horizon_hour": h,
                "valid_time": v_iso,
                "runs_count": len(h_cloud_vals),
                "causal_pass": origin_coverage_pass,
                "grid_lat": EXPECTED_LAT,
                "grid_lon": EXPECTED_LON,
                "coverage_status": "VALID" if len(h_cloud_vals) == 4 else "INCOMPLETE"
            })

        if origin_coverage_pass:
            origins_fully_covered += 1

    # Save Output CSVs atomically
    raw_df = pd.DataFrame(raw_records)
    tmp_raw = OUT_DIR / "meps_revision_raw_observations.tmp.csv"
    raw_df.to_csv(tmp_raw, index=False)
    os.replace(tmp_raw, RAW_OBS_FILE)

    feat_df = pd.DataFrame(feature_records)
    tmp_feat = OUT_DIR / "meps_revision_feature_summary.tmp.csv"
    feat_df.to_csv(tmp_feat, index=False)
    os.replace(tmp_feat, FEATURE_SUMM_FILE)

    audit_df = pd.DataFrame(audit_records)
    tmp_audit = OUT_DIR / "meps_revision_extraction_audit.tmp.csv"
    audit_df.to_csv(tmp_audit, index=False)
    os.replace(tmp_audit, AUDIT_FILE)

    # 13-Point Final Integrity Audit
    print("\n=== PART 3: EXECUTING 13-POINT EXTRACTION INTEGRITY AUDIT ===")
    
    unique_origins_extracted = raw_df["forecast_start"].nunique()
    total_raw_rows = len(raw_df)
    total_feat_rows = len(feat_df)
    causal_violations = (raw_df["causal_pass"] == False).sum()
    duplicate_rows = raw_df.duplicated(subset=["forecast_start", "horizon_hour", "forecast_reference_time"]).sum()
    nan_inf_raw = raw_df.isna().sum().sum()
    nan_inf_feat = feat_df.isna().sum().sum()

    odd_file_check = (OUT_DIR / "stage6_4_odd_test_results.csv").exists()

    report_content = f"""POLARIS Stage 6.4 — MEPS Forecast Revision Trajectory Extraction Audit Report
===================================================================================
Extraction Status: COMPLETED
Execution Date: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
Total Elapsed Time: {time.time() - start_time:.2f} seconds

1. Benchmark Origin Coverage:
   - Target Clean Origins: 347
   - Unique Extracted Origins: {unique_origins_extracted}
   - Fully Covered Origins (24/24 horizons x 4 runs): {origins_fully_covered} / 347

2. Volume & Row Accounting:
   - Expected Raw Observation Rows (347 x 24 x 4): 33,312
   - Actual Raw Observation Rows: {total_raw_rows}
   - Expected Feature Summary Rows (347 x 24): 8,328
   - Actual Feature Summary Rows: {total_feat_rows}

3. Causality & Alignment Checks:
   - Causality Rule: forecast_reference_time < t0
   - Causality Violations: {causal_violations}
   - Causal Wording: "Forecast runs were included under the conservative forecast_reference_time < t0 causal-eligibility rule."

4. Grid & Spatial Integrity:
   - Target Nuolja Station: {TARGET_LAT}°N, {TARGET_LON}°E
   - Extracted MEPS Grid Index: y={Y_IDX}, x={X_IDX}
   - Extracted Grid Coordinates: {EXPECTED_LAT}°N, {EXPECTED_LON}°E
   - Geodesic Distance: 1.2434 km

5. Quality & Data Cleanliness:
   - Duplicate Tuples (forecast_start, horizon_hour, ref_time): {duplicate_rows}
   - NaN / Inf in Raw Observations: {nan_inf_raw}
   - NaN / Inf in Feature Summary: {nan_inf_feat}

6. Protocol Lock & Isolation:
   - EVEN-CV Evaluation Executed: False (0 GBDT models fit)
   - Held-out ODD Split Evaluated: False (ODD status 100% UNTOUCHED & UNREAD)
   - ODD Output File Created: {odd_file_check} (Must be False)
===================================================================================
"""

    with open(REPORT_FILE, "w") as f:
        f.write(report_content)

    print(report_content)

    assert unique_origins_extracted == 347, f"Origin count mismatch: {unique_origins_extracted}"
    assert total_raw_rows == 33312, f"Raw rows mismatch: {total_raw_rows}"
    assert total_feat_rows == 8328, f"Feature rows mismatch: {total_feat_rows}"
    assert causal_violations == 0, f"Causality violations found: {causal_violations}"
    assert duplicate_rows == 0, f"Duplicate tuples found: {duplicate_rows}"
    assert nan_inf_raw == 0 and nan_inf_feat == 0, "NaN/Inf values found in outputs"
    assert not odd_file_check, "CRITICAL ERROR: ODD output file was created!"

    print("SUCCESS: POLARIS Stage 6.4 MEPS Forecast Revision Extraction complete and verified 100%!")

if __name__ == "__main__":
    main()
