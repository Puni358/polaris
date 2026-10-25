"""
Build the clean, un-contaminated Stage 4 baseline for Candidate F Successor (Option B).

Computes pred_stage4_clean and residual_target for the Train (2024-EVEN) and
Validation (2024-ODD) partitions using the verified 2024-EVEN fitted parameters:
  forecasting/stage4/stage4_results/ensemble_parameters.json
(SHA-256: 26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0).

Formula per horizon h in 1..24:
  phys_pred_clean(h) = max(0.0, clearsky_ghi * (1.0 - k_h * cloud_frac))
  pred_stage4_clean(h) = max(0.0, w_h * pred_stage3b_cloud_nwp + (1.0 - w_h) * phys_pred_clean(h))
  residual_target(h) = actual_SW_IN - pred_stage4_clean(h)

NO parameters are fit on validation data.
NO blind (2025) data is generated, inspected, or touched in this step.
NO existing dataset, cache, or frozen artifact is modified.

Output: forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/stage4_clean_baseline/
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
PARAMS_FILE = BASE / "forecasting/stage4/stage4_results/ensemble_parameters.json"
S3B_PREDS_2024 = BASE / "forecasting/stage3/stage3b_cloud_nwp_predictions.csv"
DATASET_V2_TRAIN = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/train.csv"
DATASET_V2_VAL = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/validation.csv"
OUT_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/stage4_clean_baseline"

# Authoritative input hashes
EXPECTED_PARAMS_HASH = "26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0"
EXPECTED_S3B_HASH = "4a0db456d4b22ec25a0d26b92dfb45aca04d631dc3e9a3ff9b7ce0ed5ff961a9"
EXPECTED_TRAIN_HASH = "7f2435fe5b2b239c9a2950366d56ab4297f29f1e8813d23a9ab64f62ca50483d"
EXPECTED_VAL_HASH = "24e6828ee7cb7d45fd755844653e4ad9396f07bfe1a551b4411867bb07c948a9"


class BaselineBuildError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


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


def atomic_write_json(obj: dict, path: Path) -> None:
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fp:
        json.dump(obj, fp, indent=2)
    tmp.replace(path)


def verify_input_hashes() -> None:
    log("Verifying authoritative input hashes...")
    actual_params = sha256_file(PARAMS_FILE)
    if actual_params != EXPECTED_PARAMS_HASH:
        raise BaselineBuildError(f"Stage 4 params hash mismatch: {actual_params} != {EXPECTED_PARAMS_HASH}")

    actual_s3b = sha256_file(S3B_PREDS_2024)
    if actual_s3b != EXPECTED_S3B_HASH:
        raise BaselineBuildError(f"Stage 3b predictions hash mismatch: {actual_s3b} != {EXPECTED_S3B_HASH}")

    actual_train = sha256_file(DATASET_V2_TRAIN)
    if actual_train != EXPECTED_TRAIN_HASH:
        raise BaselineBuildError(f"dataset_v2 train.csv hash mismatch: {actual_train} != {EXPECTED_TRAIN_HASH}")

    actual_val = sha256_file(DATASET_V2_VAL)
    if actual_val != EXPECTED_VAL_HASH:
        raise BaselineBuildError(f"dataset_v2 validation.csv hash mismatch: {actual_val} != {EXPECTED_VAL_HASH}")
    log("All input hashes MATCH.")


def load_params() -> dict:
    with open(PARAMS_FILE, "r", encoding="utf-8") as fp:
        params = json.load(fp)
    if set(params.keys()) != set(str(h) for h in range(1, 25)):
        raise BaselineBuildError(f"Expected parameters for horizons 1..24, found: {sorted(params.keys())}")
    for h_str, p in params.items():
        if "w" not in p or "k" not in p:
            raise BaselineBuildError(f"Missing w or k in horizon {h_str}")
        if not (0.0 <= p["w"] <= 1.0):
            raise BaselineBuildError(f"Parameter w out of bounds in horizon {h_str}: {p['w']}")
        if not (0.0 <= p["k"] <= 1.0):
            raise BaselineBuildError(f"Parameter k out of bounds in horizon {h_str}: {p['k']}")
    return params


def load_s3b_lookup() -> dict:
    df_s3b = pd.read_csv(S3B_PREDS_2024)
    df_s3b["fs_dt"] = pd.to_datetime(df_s3b["forecast_start"], utc=True)
    lookup = {}
    for _, row in df_s3b.iterrows():
        fs_iso = row["fs_dt"].isoformat()
        h = int(row["horizon_hour"])
        key = (fs_iso, h)
        if key in lookup:
            raise BaselineBuildError(f"Duplicate key in Stage 3b predictions: {key}")
        lookup[key] = float(row["pred_stage3b_cloud_nwp"])
    log(f"Loaded Stage 3b predictions: {len(lookup)} rows ({df_s3b['fs_dt'].nunique()} origins).")
    return lookup


def build_partition_baseline(
    partition_name: str,
    dataset_v2_path: Path,
    s3b_lookup: dict,
    params: dict,
    expected_origins: int,
    expected_rows: int
) -> pd.DataFrame:
    log(f"Processing {partition_name} baseline from {dataset_v2_path.name}...")
    df = pd.read_csv(dataset_v2_path)
    df["fs_dt"] = pd.to_datetime(df["forecast_start"], utc=True)
    df["ts_dt"] = pd.to_datetime(df["timestamp"], utc=True)

    n_origins = df["fs_dt"].nunique()
    n_rows = len(df)
    if n_origins != expected_origins or n_rows != expected_rows:
        raise BaselineBuildError(
            f"{partition_name}: count mismatch (origins: {n_origins} vs {expected_origins}, rows: {n_rows} vs {expected_rows})"
        )

    # Duplicate / missing key check
    dup = df.duplicated(subset=["fs_dt", "horizon_hour"]).sum()
    if dup > 0:
        raise BaselineBuildError(f"{partition_name}: {dup} duplicate (forecast_start, horizon_hour) keys detected.")

    # Timestamp alignment check
    mismatched_ts = 0
    for _, row in df.iterrows():
        expected_ts = row["fs_dt"] + timedelta(hours=int(row["horizon_hour"]) - 1)
        if row["ts_dt"] != expected_ts:
            mismatched_ts += 1
    if mismatched_ts > 0:
        raise BaselineBuildError(f"{partition_name}: {mismatched_ts} timestamp alignment errors.")

    # Join pred_stage3b_cloud_nwp
    s3b_vals = []
    w_vals = []
    k_vals = []
    phys_vals = []
    s4_vals = []

    for _, row in df.iterrows():
        fs_iso = row["fs_dt"].isoformat()
        h = int(row["horizon_hour"])
        key = (fs_iso, h)
        if key not in s3b_lookup:
            raise BaselineBuildError(f"{partition_name}: missing Stage 3b prediction for key {key}")
        
        s3b = s3b_lookup[key]
        p = params[str(h)]
        w_h = p["w"]
        k_h = p["k"]
        cs_ghi = float(row["clearsky_ghi"])
        cf = float(row["cloud_frac"])

        # Exact Stage 4 physics and ensemble formula
        phys = max(0.0, cs_ghi * (1.0 - k_h * cf))
        s4 = max(0.0, w_h * s3b + (1.0 - w_h) * phys)

        s3b_vals.append(s3b)
        w_vals.append(w_h)
        k_vals.append(k_h)
        phys_vals.append(phys)
        s4_vals.append(s4)

    out_df = pd.DataFrame({
        "forecast_start": [dt.isoformat() for dt in df["fs_dt"]],
        "horizon_hour": df["horizon_hour"].astype(int),
        "timestamp": [dt.isoformat() for dt in df["ts_dt"]],
        "actual_SW_IN": df["actual_SW_IN"].astype(float),
        "is_daytime": df["is_daytime"].astype(bool),
        "is_night_causal": df["is_night_causal"].astype(bool),
        "clearsky_ghi": df["clearsky_ghi"].astype(float),
        "cloud_frac": df["cloud_frac"].astype(float),
        "pred_stage3b_cloud_nwp": s3b_vals,
        "w_h": w_vals,
        "k_h": k_vals,
        "phys_pred_clean": phys_vals,
        "pred_stage4_clean": s4_vals,
        "residual_target": df["actual_SW_IN"].astype(float) - np.array(s4_vals),
    })

    # Verification: NaN/Inf checks
    for col in ["pred_stage3b_cloud_nwp", "phys_pred_clean", "pred_stage4_clean", "residual_target"]:
        n_na = out_df[col].isna().sum()
        n_inf = (~out_df[col].abs().lt(float("inf"))).sum()
        if n_na > 0 or n_inf > 0:
            raise BaselineBuildError(f"{partition_name}: {col} has {n_na} NaN and {n_inf} Inf values.")

    log(f"{partition_name}: verified {len(out_df)} rows. Zero NaNs in calculated columns.")
    return out_df


def build() -> dict:
    if OUT_DIR.exists():
        existing_files = list(OUT_DIR.glob("*"))
        if existing_files:
            raise BaselineBuildError(f"Output directory {OUT_DIR} already exists and is non-empty; refusing to overwrite.")
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    verify_input_hashes()
    params = load_params()
    s3b_lookup = load_s3b_lookup()

    # Train (2024-EVEN): 174 origins / 4,176 rows
    train_baseline_df = build_partition_baseline(
        "TRAIN", DATASET_V2_TRAIN, s3b_lookup, params,
        expected_origins=174, expected_rows=4176
    )

    # Validation (2024-ODD): 173 origins / 4,152 rows
    val_baseline_df = build_partition_baseline(
        "VALIDATION", DATASET_V2_VAL, s3b_lookup, params,
        expected_origins=173, expected_rows=4152
    )

    # Origin mutual exclusivity assertion
    tr_origins = set(train_baseline_df["forecast_start"])
    val_origins = set(val_baseline_df["forecast_start"])
    if tr_origins & val_origins:
        raise BaselineBuildError("Train and Validation baseline origins overlap!")

    # Write CSVs atomically
    train_path = OUT_DIR / "train_baseline.csv"
    val_path = OUT_DIR / "validation_baseline.csv"
    atomic_write_csv(train_baseline_df, train_path)
    atomic_write_csv(val_baseline_df, val_path)
    log(f"Wrote {train_path.name} ({len(train_baseline_df)} rows) and {val_path.name} ({len(val_baseline_df)} rows).")

    # Hashes
    out_hashes = {
        "train_baseline.csv": sha256_file(train_path),
        "validation_baseline.csv": sha256_file(val_path),
    }
    hashes_file = OUT_DIR / "HASHES.sha256"
    hashes_file.write_text(
        "\n".join(f"{h}  {f}" for f, h in out_hashes.items()) + "\n", encoding="utf-8"
    )
    log("Wrote HASHES.sha256.")

    # Manifest
    manifest = {
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Clean, un-contaminated Stage 4 baseline for Candidate F Successor (Option B)",
        "protocol_reference": "CANDIDATE_F_SUCCESSOR_CLEAN_SPLIT_PROTOCOL_v1.md §2 (Option A reuse-forward)",
        "parameter_provenance": {
            "source_file": str(PARAMS_FILE),
            "sha256": EXPECTED_PARAMS_HASH,
            "fitted_on": "2024-EVEN actual_SW_IN daytime rows only (TRAINING_INTEGRITY_VERIFIED)",
            "horizons": 24,
        },
        "stage3b_source": {
            "source_file": str(S3B_PREDS_2024),
            "sha256": EXPECTED_S3B_HASH,
            "model": "amazon/chronos-2 (frozen weights, no retraining)",
        },
        "input_datasets": {
            "train.csv": EXPECTED_TRAIN_HASH,
            "validation.csv": EXPECTED_VAL_HASH,
        },
        "output_artifacts": {
            "train_baseline.csv": {
                "sha256": out_hashes["train_baseline.csv"],
                "origins": len(tr_origins),
                "rows": len(train_baseline_df),
                "columns": list(train_baseline_df.columns),
            },
            "validation_baseline.csv": {
                "sha256": out_hashes["validation_baseline.csv"],
                "origins": len(val_origins),
                "rows": len(val_baseline_df),
                "columns": list(val_baseline_df.columns),
            },
        },
        "formula": {
            "physics_model": "max(0.0, clearsky_ghi * (1.0 - k_h * cloud_frac))",
            "stage4_ensemble": "max(0.0, w_h * pred_stage3b_cloud_nwp + (1.0 - w_h) * phys_pred_clean)",
            "residual_target": "actual_SW_IN - pred_stage4_clean",
        },
        "blind_partition_policy": "BLIND (2025) NOT GENERATED OR INSPECTED AT THIS STAGE",
        "governance": {
            "refit_on_validation": False,
            "refit_on_blind": False,
            "winner_status": "null",
        }
    }
    manifest_path = OUT_DIR / "BASELINE_MANIFEST.json"
    atomic_write_json(manifest, manifest_path)
    log("Wrote BASELINE_MANIFEST.json.")

    return out_hashes


if __name__ == "__main__":
    try:
        hashes = build()
        print("STAGE4_CLEAN_BASELINE_BUILD_SUCCESS")
        for f, h in hashes.items():
            print(f"  {f}: {h}")
    except BaselineBuildError as e:
        print(f"STAGE4_CLEAN_BASELINE_BUILD_FAILED: {e}")
        sys.exit(2)
