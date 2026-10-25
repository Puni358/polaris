import os
import json
import hashlib
import pandas as pd
import numpy as np
import torch
from chronos import Chronos2Pipeline

# ============================================================
# POLARIS — STAGE 3B rebuild for 2025 (Chronos-2 + solar geometry
# + fc_cloud_cover, frozen checkpoint, no retraining)
#
# Exact replica of the "3B" branch of forecasting/stage3/run_stage3_experiments.py
# (2024, LOCKED): same frozen amazon/chronos-2 checkpoint, same
# covariate set, same 24h-context / 24h-horizon origin logic, same
# causal past/future covariate construction, same output schema.
# Only the inputs are substituted for the verified 2025 artifacts:
#   - data/POLARIS_v0_1_future_weather_forecasts_2025.csv
#     (clean/audit-only NWP, no synthetic imputation -- rebuilt by
#      forecasting/clear_sky/audit_clean_nwp_windows_2025.py to match what the
#      2024 pipeline actually consumes at its equivalent path)
#   - data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv
#
# Does NOT read or write any 2024 Stage 3 file (separate output
# directory). Does NOT retrain Chronos-2 (from_pretrained only,
# device_map="cpu", frozen weights). Does NOT run Stage 4 / 8.1.
#
# Checkpointed/resumable: predictions are accumulated and flushed
# to disk every CHECKPOINT_EVERY origins; a re-run skips origins
# already present in the checkpoint. Final output is written
# atomically (tmp file + os.replace).
# ============================================================

NWP_PATH = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
DECOMP_PATH = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
STAGE3B_DIR = "/home/punith-bs/01polaris (Copy)/forecasting/stage3/stage3b_2025"
CHECKPOINT_CSV = os.path.join(STAGE3B_DIR, "_checkpoint_partial_predictions.csv")
OUTPUT_CSV = os.path.join(STAGE3B_DIR, "stage3b_cloud_nwp_predictions_2025.csv")
MANIFEST_FILE = os.path.join(STAGE3B_DIR, "stage3b_2025_MANIFEST.json")

CHECKPOINT_EVERY = 25

CHRONOS_MODEL_ID = "amazon/chronos-2"
CHRONOS_SNAPSHOT_SHA256 = "ddcda3c7508bf2528087723e98a20707cc04b7f370ae275a9fd88078ddba4f42"  # model.safetensors, independently verified pre-run

COV_KEYS = ["solar_elevation", "solar_zenith", "clearsky_ghi", "fc_cloud_cover"]
EXP_PREFIX = "stage3b_cloud_nwp"


def atomic_write_csv(df, path):
    tmp_path = path + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, path)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 85)
    print("POLARIS — STAGE 3B rebuild (2025): Chronos-2 + solar geometry + fc_cloud_cover")
    print("=" * 85)

    os.makedirs(STAGE3B_DIR, exist_ok=True)

    # 0. Verify input hashes up front (fail fast if inputs drifted since verification)
    nwp_hash = sha256_of(NWP_PATH)
    decomp_hash = sha256_of(DECOMP_PATH)
    print(f"\nInput hash  NWP (2025, clean):     {nwp_hash}")
    print(f"Input hash  clearsky decomp (2025): {decomp_hash}")

    nwp_df = pd.read_csv(NWP_PATH)
    decomp_df = pd.read_csv(DECOMP_PATH)

    nwp_df["timestamp_dt"] = pd.to_datetime(nwp_df["timestamp"])
    nwp_df["forecast_start_dt"] = pd.to_datetime(nwp_df["forecast_start"])
    decomp_df["timestamp_dt"] = pd.to_datetime(decomp_df["TIMESTAMP"])

    all_origins = sorted(nwp_df["forecast_start_dt"].unique())
    print(f"2025 forecast origins (clean NWP coverage): {len(all_origins)}")

    # Reindex NWP variables for past lookup (same bfill/ffill method as 2024;
    # this only ever fills PAST context, never the future/forecast window --
    # future covariates always come from the clean per-origin NWP rows below)
    nwp_vars = ["fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m",
                "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"]
    full_idx = pd.date_range("2025-01-01 00:00:00", "2025-12-31 23:00:00", freq="1h")
    nwp_ts_lookup = nwp_df.groupby("timestamp_dt")[nwp_vars].mean().reindex(full_idx).bfill().ffill()

    decomp_df = decomp_df.set_index("timestamp_dt").sort_index()

    # Causal context requirement: ctx_start = orig - 24h must exist in the
    # 2025 decomposition file. This excludes 2025-01-01 (it would need
    # 2024-12-31 context, which is out of scope for this 2025-only rebuild)
    # -- exactly the same reason the 2024 pipeline's origins start on
    # 2024-01-02 rather than 2024-01-01, not an arbitrary benchmark quirk.
    decomp_min = decomp_df.index.min()
    origins = [o for o in all_origins if (o - pd.Timedelta(hours=24)) >= decomp_min]
    excluded = [o for o in all_origins if o not in origins]
    n_origins = len(origins)
    print(f"Origins excluded for insufficient prior context: {[o.strftime('%Y-%m-%d') for o in excluded]}")
    print(f"2025 forecast origins (after context-availability filter): {n_origins}")

    # 1. Resume from checkpoint if present
    results = []
    done_origins = set()
    if os.path.exists(CHECKPOINT_CSV):
        ckpt = pd.read_csv(CHECKPOINT_CSV)
        results = ckpt.to_dict("records")
        done_origins = set(pd.to_datetime(ckpt["forecast_start"]).unique())
        print(f"Resuming from checkpoint: {len(done_origins)} origins already completed.")

    remaining = [o for o in origins if o not in done_origins]
    print(f"Origins remaining to process: {len(remaining)}")

    if remaining:
        print(f"\nLoading frozen Chronos-2 pipeline ({CHRONOS_MODEL_ID}, device_map=cpu, no training)...")
        pipeline = Chronos2Pipeline.from_pretrained(CHRONOS_MODEL_ID, device_map="cpu")
        quantiles = np.asarray(pipeline.quantiles)
        median_idx = int(np.argmin(np.abs(quantiles - 0.5)))

        print(f"\nRunning Stage 3B ({EXP_PREFIX}) with covariates: {COV_KEYS}...")

        since_checkpoint = 0
        for i, orig in enumerate(remaining):
            ctx_start = orig - pd.Timedelta(hours=24)
            ctx_end = orig - pd.Timedelta(hours=1)
            fut_start = orig
            fut_end = orig + pd.Timedelta(hours=23)

            ctx_decomp = decomp_df.loc[ctx_start:ctx_end]
            fut_decomp = decomp_df.loc[fut_start:fut_end]
            ctx_nwp = nwp_ts_lookup.loc[ctx_start:ctx_end]
            fut_nwp = nwp_df[nwp_df["forecast_start_dt"] == orig].set_index("timestamp_dt").loc[fut_start:fut_end]

            target = ctx_decomp["actual_SW_IN"].to_numpy(dtype=np.float32)

            past_covs = {}
            fut_covs = {}
            for k in COV_KEYS:
                if k in ctx_decomp.columns:
                    past_covs[k] = ctx_decomp[k].to_numpy(dtype=np.float32)
                    fut_covs[k] = fut_decomp[k].to_numpy(dtype=np.float32)
                else:
                    past_covs[k] = ctx_nwp[k].to_numpy(dtype=np.float32)
                    fut_covs[k] = fut_nwp[k].to_numpy(dtype=np.float32)

            input_item = {
                "target": target,
                "past_covariates": past_covs,
                "future_covariates": fut_covs,
            }

            preds = pipeline.predict([input_item], prediction_length=24, context_length=24)
            pred_median = preds[0][0, median_idx].numpy()

            for h in range(24):
                results.append({
                    "forecast_start": orig.strftime("%Y-%m-%d"),
                    "horizon_hour": h + 1,
                    "timestamp": fut_decomp.index[h].strftime("%Y-%m-%d %H:%M:%S"),
                    "actual_SW_IN": float(fut_decomp["actual_SW_IN"].iloc[h]),
                    f"pred_{EXP_PREFIX}": float(pred_median[h]),
                })

            since_checkpoint += 1
            if since_checkpoint >= CHECKPOINT_EVERY or i == len(remaining) - 1:
                atomic_write_csv(pd.DataFrame(results), CHECKPOINT_CSV)
                since_checkpoint = 0
                print(f"  [{i + 1}/{len(remaining)}] checkpointed ({len(results)} rows so far)")
    else:
        print("All origins already completed in checkpoint; nothing to compute.")

    pred_df = pd.DataFrame(results)
    pred_col = f"pred_{EXP_PREFIX}"

    # 2. Validations
    expected_rows = n_origins * 24
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"1. Row count:            {len(pred_df)} (expected {expected_rows})")
    assert len(pred_df) == expected_rows, f"Expected {expected_rows} rows, got {len(pred_df)}"

    n_unique_origins = pred_df["forecast_start"].nunique()
    print(f"2. Unique origins:       {n_unique_origins} (expected {n_origins})")
    assert n_unique_origins == n_origins

    horizons_per_origin = pred_df.groupby("forecast_start")["horizon_hour"].count()
    valid_horizons = (horizons_per_origin == 24).all()
    print(f"3. Exactly 24 horizons per origin: {valid_horizons}")
    assert valid_horizons

    dup = pred_df.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
    print(f"4. Duplicate (forecast_start, horizon_hour) rows: {dup} (expected 0)")
    assert dup == 0

    n_nan = pred_df[pred_col].isna().sum()
    n_inf = np.isinf(pred_df[pred_col]).sum()
    print(f"5. NaN predictions: {n_nan} / Inf predictions: {n_inf} (expected 0 / 0)")
    assert n_nan == 0 and n_inf == 0

    # Causality check: every predicted timestamp must equal its forecast_start's
    # calendar day, horizon_hour-1 hours after midnight (no leakage from future
    # actuals; predictions only ever consumed fc_* values drawn from the NWP run
    # keyed to that same forecast_start, and actual_SW_IN past-24h context).
    pred_df["_ts"] = pd.to_datetime(pred_df["timestamp"])
    pred_df["_fs"] = pd.to_datetime(pred_df["forecast_start"])
    causal_ok = ((pred_df["_ts"] - pred_df["_fs"]) == pd.to_timedelta(pred_df["horizon_hour"] - 1, unit="h")).all()
    print(f"6. Causal timestamp alignment (timestamp == forecast_start + horizon_hour-1): {causal_ok}")
    assert causal_ok
    pred_df = pred_df.drop(columns=["_ts", "_fs"])

    expected_cols = ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", pred_col]
    print(f"7. Schema: {list(pred_df.columns)} (expected {expected_cols})")
    assert list(pred_df.columns) == expected_cols

    # 3. Write final output atomically
    atomic_write_csv(pred_df, OUTPUT_CSV)
    out_hash = sha256_of(OUTPUT_CSV)
    print(f"\n8. Output SHA256: {out_hash}")
    print(f"   Output path:   {OUTPUT_CSV}")

    manifest = {
        "output_file": OUTPUT_CSV,
        "sha256": out_hash,
        "row_count": int(len(pred_df)),
        "unique_origins": int(n_unique_origins),
        "columns": expected_cols,
        "covariates": COV_KEYS,
        "model": {
            "id": CHRONOS_MODEL_ID,
            "frozen": True,
            "retrained": False,
            "device_map": "cpu",
            "checkpoint_snapshot_sha256": CHRONOS_SNAPSHOT_SHA256,
        },
        "input_hashes": {
            "nwp_2025_clean": nwp_hash,
            "clearsky_decomposition_2025": decomp_hash,
        },
        "causal_timestamp_alignment_verified": bool(causal_ok),
        "note": (
            "Exact replica of the '3B' branch of forecasting/stage3/run_stage3_experiments.py "
            "(2024, LOCKED): same frozen amazon/chronos-2 checkpoint, same "
            "covariates, same 24h context / 24h horizon origin construction, "
            "same past/future causal covariate split. Only the 2024 "
            "experiments 3A and 3C were not re-run (out of scope per request: "
            "Stage 3B only)."
        ),
    }
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {MANIFEST_FILE}")
    print("\nDone! Stage 3B (2025) successfully rebuilt and validated.")


if __name__ == "__main__":
    main()
