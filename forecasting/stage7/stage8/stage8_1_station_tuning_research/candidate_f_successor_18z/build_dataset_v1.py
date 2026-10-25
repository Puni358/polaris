"""
Build the clean, origin-grouped Candidate F 18Z successor dataset (v1).

Dataset construction and validation ONLY. No model is trained or tuned here, no blind
metric is computed, no network request is made, and nothing under
forecasting/stage7/stage8/stage8_1_corrected_2025/ (the frozen base matrices), the acquisition
cache, the frozen Candidate F model, or any governance record is modified.

Inputs (read-only):
  - forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv
  - forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv
  - candidate_f_successor_18z/cache_full_acquisition/*.json (711 validated 18Z records)

Output (new, versioned, isolated):
  - candidate_f_successor_18z/dataset_v1/{train,validation,blind}.csv
  - candidate_f_successor_18z/dataset_v1/split_manifest.csv
  - candidate_f_successor_18z/dataset_v1/FEATURE_SCHEMA.md
  - candidate_f_successor_18z/dataset_v1/DATASET_BUILD_REPORT.md
  - candidate_f_successor_18z/dataset_v1/HASHES.sha256
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.acquire_full import (
    full_inventory, _structurally_valid, _parse_origin,
)
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.fetcher import cache_key

BASE = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_2024 = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
MATRIX_2025 = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
ACQUISITION_CACHE = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/cache_full_acquisition"
OUT_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v1"

# Features dropped from the 37-feature contract: lwp_latest/iwp_latest/lwp_x_cloud are
# replaced by the causal 18Z-sourced equivalents (per CANDIDATE_F_SUCCESSOR_18Z_FEATURE_
# CONTRACT_v1.md); pred_stage3b_cloud_nwp/phys_pred_fold/pred_stage4_fold/
# disagreement_fold are EXCLUDED entirely (not recomputed, not substituted) because
# their only existing generation path for 2025 rows depends on
# forecasting/stage4/stage4_results_2025/ensemble_parameters.json, whose k_h/w_h were fit on
# realized 2025-EVEN actual_SW_IN -- a verified contamination (see
# TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md, Section D). Dropped
# uniformly from ALL partitions (not just 2025) so the feature contract is identical
# across train/validation/blind.
DROPPED_REPLACED = ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
DROPPED_CONTAMINATED = ["pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold"]
NON_FEATURE_COLUMNS = ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "split",
                       "is_daytime", "is_night_causal", "origin_id"]


class BuildError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def load_acquisition_lookup() -> dict:
    """Returns {(forecast_start_iso, horizon_hour): (lwp, iwp, record_sha256)}, and a
    separate {forecast_start_iso: record_sha256} for the manifest. Every record is
    independently re-validated structurally here (not merely trusted from the
    manifest) before being used."""
    lookup = {}
    origin_hash = {}
    files = sorted(ACQUISITION_CACHE.glob("*.json"))
    files = [f for f in files if f.name != "ACQUISITION_MANIFEST.json"]
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("retrieval_status") != "OK":
            raise BuildError(f"non-OK record found in acquisition cache: {f.name} status={rec.get('retrieval_status')}")
        origin = _parse_origin(rec["forecast_start"])
        if cache_key(origin) != rec.get("cache_key"):
            raise BuildError(f"cache_key mismatch on {f.name}")
        payload = rec["payload"]
        if not _structurally_valid(payload, origin):
            raise BuildError(f"record failed structural re-validation: {f.name}")
        fs_iso = rec["forecast_start"]
        origin_hash[fs_iso] = rec["content_sha256"]
        for h in payload["per_horizon"]:
            lookup[(fs_iso, h["horizon_hour"])] = (h["lwp_mass_fraction"], h["iwp_mass_fraction"])
    return lookup, origin_hash, len(files)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_csv(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def build() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=False) if not OUT_DIR.exists() else None

    # --- Step 1: independent inventory + acquisition reconciliation -----------------
    planned = full_inventory()
    planned_iso = sorted(o.isoformat() for o in planned)
    log(f"Independently recomputed planned inventory: {len(planned)} origins")

    lookup, origin_hash, n_files = load_acquisition_lookup()
    acquired_iso = sorted(origin_hash.keys())
    if n_files != 711:
        raise BuildError(f"expected 711 acquisition records, found {n_files}")
    if acquired_iso != planned_iso:
        missing = set(planned_iso) - set(acquired_iso)
        unexpected = set(acquired_iso) - set(planned_iso)
        raise BuildError(f"acquisition cache does not exactly match planned inventory: "
                          f"missing={len(missing)} unexpected={len(unexpected)}")
    log("Acquisition cache reconciled exactly against the independently recomputed 711-origin inventory.")

    # --- Step 2: load base matrices ---------------------------------------------------
    df24 = pd.read_csv(MATRIX_2024)
    df25 = pd.read_csv(MATRIX_2025)
    log(f"Loaded base matrices: 2024 rows={len(df24)} origins={df24['forecast_start'].nunique()}, "
        f"2025 rows={len(df25)} origins={df25['forecast_start'].nunique()}")

    expected_2024_origins = [ts for ts in planned_iso if ts.startswith("2024")]
    expected_2025_origins = [ts for ts in planned_iso if ts.startswith("2025")]

    def normalize_fs(s: str) -> str:
        return _parse_origin(s).isoformat()

    for df, year, expected in ((df24, 2024, expected_2024_origins), (df25, 2025, expected_2025_origins)):
        actual = sorted(set(normalize_fs(s) for s in df["forecast_start"].unique()))
        if actual != sorted(expected):
            raise BuildError(f"{year} base matrix origin set does not match planned inventory for that year "
                              f"(actual={len(actual)}, expected={len(expected)})")
    log("Base-matrix origin sets match the planned inventory exactly for both years.")

    # --- Step 3: attach causal 18Z features, drop replaced/contaminated columns ------
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["_fs_norm"] = df["forecast_start"].apply(normalize_fs)
        lwp_vals, iwp_vals = [], []
        for fs_norm, h in zip(df["_fs_norm"], df["horizon_hour"]):
            key = (fs_norm, int(h))
            if key not in lookup:
                raise BuildError(f"missing 18Z acquisition value for origin={fs_norm} horizon={h}")
            lwp, iwp = lookup[key]
            lwp_vals.append(lwp)
            iwp_vals.append(iwp)
        df["lwp_18z_fc"] = lwp_vals
        df["iwp_18z_fc"] = iwp_vals
        df["lwp_x_cloud_18z"] = df["lwp_18z_fc"] * df["cloud_frac"]
        df["elevation_x_cloud_frac"] = df["solar_elevation"] * df["cloud_frac"]
        df = df.drop(columns=DROPPED_REPLACED + DROPPED_CONTAMINATED)
        return df

    df24t = transform(df24)
    df25t = transform(df25)
    log("Attached causal 18Z features (lwp_18z_fc, iwp_18z_fc, lwp_x_cloud_18z) and elevation_x_cloud_frac; "
        f"dropped {DROPPED_REPLACED + DROPPED_CONTAMINATED}.")

    # --- Step 4: partition per the frozen protocol ------------------------------------
    # 2024: use the matrix's OWN 'split' column (EVEN/ODD) -- this is the existing,
    # already-frozen Candidate F train/validation assignment, reused verbatim.
    train_df = df24t[df24t["split"] == "EVEN"].copy()
    val_df = df24t[df24t["split"] == "ODD"].copy()
    # 2025: per CANDIDATE_F_REPORT.md's own explicit note, 2025 has no EVEN/ODD split
    # of its own in this pipeline -- it is used WHOLE as the blind set. The 'split'
    # column present in the 2025 CORRECTED matrix (an artifact of the shared
    # matrix-builder always computing one) is explicitly IGNORED for partitioning here,
    # exactly as the frozen methodology requires -- not used, not silently relied upon.
    blind_df = df25t.copy()

    train_origins = set(train_df["_fs_norm"])
    val_origins = set(val_df["_fs_norm"])
    blind_origins = set(blind_df["_fs_norm"])

    if train_origins & val_origins:
        raise BuildError("train/validation origin overlap detected")
    if train_origins & blind_origins or val_origins & blind_origins:
        raise BuildError("2024/2025 origin overlap detected")
    if (train_origins | val_origins | blind_origins) != set(planned_iso):
        raise BuildError("union of partition origins does not exactly equal the planned inventory")
    log(f"Partitions: train origins={len(train_origins)} rows={len(train_df)}, "
        f"validation origins={len(val_origins)} rows={len(val_df)}, "
        f"blind origins={len(blind_origins)} rows={len(blind_df)}")

    expected_counts = {"train": (174, 174 * 24), "validation": (173, 173 * 24), "blind": (364, 364 * 24)}
    actual_counts = {"train": (len(train_origins), len(train_df)),
                      "validation": (len(val_origins), len(val_df)),
                      "blind": (len(blind_origins), len(blind_df))}
    count_mismatches = {k: (expected_counts[k], actual_counts[k]) for k in expected_counts
                         if expected_counts[k] != actual_counts[k]}
    if count_mismatches:
        raise BuildError(f"origin/row counts differ from protocol expectation: {count_mismatches}")
    log("Origin/row counts match protocol expectation exactly: "
        f"train={actual_counts['train']}, validation={actual_counts['validation']}, blind={actual_counts['blind']}")

    # --- Step 5: time-alignment / causality structural re-check on the FINAL dataset --
    for name, part in (("train", train_df), ("validation", val_df), ("blind", blind_df)):
        bad = 0
        for fs_norm, h, ts in zip(part["_fs_norm"], part["horizon_hour"], part["timestamp"]):
            origin_dt = _parse_origin(fs_norm)
            expected_valid = origin_dt + timedelta(hours=int(h))
            actual_valid = _parse_origin(ts)
            if actual_valid != expected_valid:
                bad += 1
        if bad:
            raise BuildError(f"{name}: {bad} rows with valid_time != origin+horizon_hour")
    log("Time-alignment re-check passed for all rows in all three partitions.")

    feature_cols = [c for c in train_df.columns if c not in NON_FEATURE_COLUMNS and c != "_fs_norm"]
    for forbidden in ("actual_SW_IN",):
        if forbidden in feature_cols:
            raise BuildError(f"label column '{forbidden}' leaked into the feature set")
    log(f"Final feature count: {len(feature_cols)} (excludes label 'actual_SW_IN' and bookkeeping columns).")

    # --- Step 6: write outputs ---------------------------------------------------------
    out_cols_order = NON_FEATURE_COLUMNS + feature_cols
    for df in (train_df, val_df, blind_df):
        df.drop(columns=["_fs_norm"], inplace=True)

    atomic_write_csv(train_df[out_cols_order], OUT_DIR / "train.csv")
    atomic_write_csv(val_df[out_cols_order], OUT_DIR / "validation.csv")
    atomic_write_csv(blind_df[out_cols_order], OUT_DIR / "blind.csv")
    log("Wrote train.csv, validation.csv, blind.csv (atomic writes).")

    manifest_rows = []
    for fs_norm in planned_iso:
        if fs_norm in train_origins:
            partition = "TRAIN"
        elif fs_norm in val_origins:
            partition = "VALIDATION"
        else:
            partition = "BLIND"
        manifest_rows.append({
            "forecast_start": fs_norm, "partition": partition,
            "acquisition_record_sha256": origin_hash[fs_norm], "row_count": 24,
        })
    manifest_df = pd.DataFrame(manifest_rows)
    atomic_write_csv(manifest_df, OUT_DIR / "split_manifest.csv")
    log(f"Wrote split_manifest.csv ({len(manifest_df)} origin rows).")

    return len(feature_cols)


if __name__ == "__main__":
    try:
        n_features = build()
        print(f"BUILD_OK features={n_features}")
    except BuildError as e:
        print(f"BUILD_BLOCKED: {e}")
        sys.exit(2)
