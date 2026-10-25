"""
Build the clean, origin-grouped Candidate F 18Z successor dataset (v2).

Implements CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v2.md (approved SHA-256
98e5ce3a721eb3d0064412d9ce2cbdebb2f8bc59bad368f141c838feebc7a05f): base horizon_hour=h
is valid at origin+(h-1), sourced from source lead=5+h. For h=2..24 this comes from the
existing cache_full_acquisition/ records (cache's own horizon_hour=h-1, lead=6+(h-1)).
For h=1 (lead=6) it comes from the new cache_lead6_v2/ records.

Dataset construction and validation ONLY. No model training/evaluation, no network
request, no modification of either cache, the frozen base matrices, the frozen Candidate
F model, v1/v2 contracts, or any governance record.

Output: forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2/
(new, isolated; dataset_v1/ was never created since the v1 build stopped at a validation
gate, so there is nothing to overwrite there).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.acquire_full import (
    full_inventory, _structurally_valid, _parse_origin,
)
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.fetcher import cache_key

BASE = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_2024 = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
MATRIX_2025 = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"
CACHE_LEAD7_30 = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/cache_full_acquisition"
CACHE_LEAD6 = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/cache_lead6_v2"
OUT_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2"

DROPPED_REPLACED = ["lwp_latest", "iwp_latest", "lwp_x_cloud"]
DROPPED_CONTAMINATED = ["pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold"]
NON_FEATURE_COLUMNS = ["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN", "split",
                       "is_daytime", "is_night_causal", "origin_id"]


class BuildError(RuntimeError):
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


def load_lead6_lookup() -> tuple:
    lookup, origin_hash_6 = {}, {}
    files = sorted(CACHE_LEAD6.glob("*.json"))
    files = [f for f in files if f.name != "LEAD6_ACQUISITION_MANIFEST.json"]
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("retrieval_status") != "OK":
            raise BuildError(f"non-OK lead-6 record: {f.name}")
        origin = _parse_origin(rec["forecast_start"])
        if cache_key(origin) != rec.get("cache_key"):
            raise BuildError(f"lead-6 cache_key mismatch: {f.name}")
        payload = rec["payload"]
        h0 = payload["per_horizon"][0]
        if h0["horizon_hour"] != 1:
            raise BuildError(f"lead-6 record does not label horizon_hour=1: {f.name}")
        expected_valid = origin  # v2: base h=1 -> origin + (1-1) = origin
        if datetime.fromisoformat(h0["valid_time_utc"]) != expected_valid:
            raise BuildError(f"lead-6 valid_time mismatch for {rec['forecast_start']}")
        fs_iso = rec["forecast_start"]
        lookup[(fs_iso, 1)] = (h0["lwp_mass_fraction"], h0["iwp_mass_fraction"])
        origin_hash_6[fs_iso] = rec["content_sha256"]
    return lookup, origin_hash_6, len(files)


def load_lead7_30_lookup() -> tuple:
    """Maps base horizon h=2..24 to the existing cache's own horizon_hour=(h-1)."""
    lookup, origin_hash_730 = {}, {}
    files = sorted(CACHE_LEAD7_30.glob("*.json"))
    files = [f for f in files if f.name != "ACQUISITION_MANIFEST.json"]
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("retrieval_status") != "OK":
            raise BuildError(f"non-OK lead7-30 record: {f.name}")
        origin = _parse_origin(rec["forecast_start"])
        if cache_key(origin) != rec.get("cache_key"):
            raise BuildError(f"lead7-30 cache_key mismatch: {f.name}")
        payload = rec["payload"]
        if not _structurally_valid(payload, origin):
            raise BuildError(f"lead7-30 record failed structural re-validation: {f.name}")
        fs_iso = rec["forecast_start"]
        origin_hash_730[fs_iso] = rec["content_sha256"]
        for h in payload["per_horizon"]:
            h_cache = h["horizon_hour"]  # 1..24, lead=6+h_cache
            base_h = h_cache + 1  # v2 mapping; h_cache=24 -> base_h=25, unused (dropped below)
            if base_h > 24:
                continue
            expected_valid = origin + timedelta(hours=base_h - 1)
            if datetime.fromisoformat(h["valid_time_utc"]) != origin + timedelta(hours=h_cache):
                raise BuildError(f"lead7-30 internal valid_time inconsistency: {fs_iso} h_cache={h_cache}")
            # sanity: lead=6+h_cache should equal 5+base_h
            if 6 + h_cache != 5 + base_h:
                raise BuildError("lead/base_h arithmetic inconsistency (should be unreachable)")
            lookup[(fs_iso, base_h)] = (h["lwp_mass_fraction"], h["iwp_mass_fraction"])
    return lookup, origin_hash_730, len(files)


def build() -> int:
    if OUT_DIR.exists():
        raise BuildError(f"{OUT_DIR} already exists; refusing to overwrite a prior build")
    OUT_DIR.mkdir(parents=True)

    planned = full_inventory()
    planned_iso = sorted(o.isoformat() for o in planned)
    log(f"Independently recomputed planned inventory: {len(planned)} origins")

    lookup6, hash6, n6 = load_lead6_lookup()
    lookup730, hash730, n730 = load_lead7_30_lookup()
    if n6 != 711:
        raise BuildError(f"expected 711 lead-6 records, found {n6}")
    if n730 != 711:
        raise BuildError(f"expected 711 lead7-30 records, found {n730}")
    if sorted(hash6.keys()) != planned_iso or sorted(hash730.keys()) != planned_iso:
        raise BuildError("one or both caches do not exactly match the planned 711-origin inventory")
    log("Both caches (lead-6 v2, lead-7..30) reconciled exactly against the planned inventory.")

    combined_lookup = {}
    for fs_iso in planned_iso:
        combined_lookup[(fs_iso, 1)] = lookup6[(fs_iso, 1)]
        for base_h in range(2, 25):
            key = (fs_iso, base_h)
            if key not in lookup730:
                raise BuildError(f"missing v2-mapped 18Z value for {fs_iso} base_h={base_h}")
            combined_lookup[key] = lookup730[key]
    log(f"Combined v2 lookup built: {len(combined_lookup)} (origin, base_horizon) entries "
        f"(expected {len(planned)}*24={len(planned)*24}).")
    if len(combined_lookup) != len(planned) * 24:
        raise BuildError("combined lookup size mismatch")

    df24 = pd.read_csv(MATRIX_2024)
    df25 = pd.read_csv(MATRIX_2025)
    log(f"Loaded base matrices: 2024 rows={len(df24)} origins={df24['forecast_start'].nunique()}, "
        f"2025 rows={len(df25)} origins={df25['forecast_start'].nunique()}")

    def normalize_fs(s: str) -> str:
        return _parse_origin(s).isoformat()

    expected_2024 = [ts for ts in planned_iso if ts.startswith("2024")]
    expected_2025 = [ts for ts in planned_iso if ts.startswith("2025")]
    for df, year, expected in ((df24, 2024, expected_2024), (df25, 2025, expected_2025)):
        actual = sorted(set(normalize_fs(s) for s in df["forecast_start"].unique()))
        if actual != sorted(expected):
            raise BuildError(f"{year} base matrix origin set mismatch vs planned inventory")
    log("Base-matrix origin sets match the planned inventory exactly for both years.")

    def transform(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["_fs_norm"] = df["forecast_start"].apply(normalize_fs)
        lwp_vals, iwp_vals = [], []
        for fs_norm, h in zip(df["_fs_norm"], df["horizon_hour"]):
            key = (fs_norm, int(h))
            if key not in combined_lookup:
                raise BuildError(f"missing v2 18Z value for origin={fs_norm} horizon={h}")
            lwp, iwp = combined_lookup[key]
            lwp_vals.append(lwp)
            iwp_vals.append(iwp)
        df["lwp_18z_fc"] = lwp_vals
        df["iwp_18z_fc"] = iwp_vals
        df["lwp_x_cloud_18z"] = df["lwp_18z_fc"] * df["cloud_frac"]
        df["elevation_x_cloud_frac"] = df["solar_elevation"] * df["cloud_frac"]
        return df.drop(columns=DROPPED_REPLACED + DROPPED_CONTAMINATED)

    df24t, df25t = transform(df24), transform(df25)
    log(f"Attached v2-mapped causal 18Z features; dropped {DROPPED_REPLACED + DROPPED_CONTAMINATED}.")

    train_df = df24t[df24t["split"] == "EVEN"].copy()
    val_df = df24t[df24t["split"] == "ODD"].copy()
    blind_df = df25t.copy()  # 2025 used whole, its own EVEN/ODD column ignored (documented, unchanged from v1 design)

    train_o, val_o, blind_o = set(train_df["_fs_norm"]), set(val_df["_fs_norm"]), set(blind_df["_fs_norm"])
    if train_o & val_o or train_o & blind_o or val_o & blind_o:
        raise BuildError("partition origin overlap detected")
    if (train_o | val_o | blind_o) != set(planned_iso):
        raise BuildError("union of partition origins != planned inventory")

    expected_counts = {"train": (174, 174 * 24), "validation": (173, 173 * 24), "blind": (364, 364 * 24)}
    actual_counts = {"train": (len(train_o), len(train_df)), "validation": (len(val_o), len(val_df)),
                      "blind": (len(blind_o), len(blind_df))}
    if expected_counts != actual_counts:
        raise BuildError(f"origin/row counts differ from protocol: {actual_counts} != {expected_counts}")
    log(f"Partition counts match protocol exactly: {actual_counts}")

    # Time-alignment re-check: under v2, every horizon's valid 18Z target now equals the
    # row's OWN existing `timestamp` column exactly (both represent origin+(h-1)).
    for name, part in (("train", train_df), ("validation", val_df), ("blind", blind_df)):
        mism = 0
        for fs_norm, h, ts in zip(part["_fs_norm"], part["horizon_hour"], part["timestamp"]):
            origin_dt = _parse_origin(fs_norm)
            expected = origin_dt + timedelta(hours=int(h) - 1)
            if _parse_origin(ts) != expected:
                mism += 1
        if mism:
            raise BuildError(f"{name}: {mism} rows where timestamp != origin+(h-1)")
    log("Time-alignment re-check (18Z feature valid-time vs. row's own timestamp column) passed for all rows.")

    # Duplicate / missing-value / non-finite checks
    for name, part in (("train", train_df), ("validation", val_df), ("blind", blind_df)):
        dup = part.duplicated(subset=["forecast_start", "horizon_hour"]).sum()
        if dup:
            raise BuildError(f"{name}: {dup} duplicate (forecast_start, horizon_hour) rows")
        for col in ("lwp_18z_fc", "iwp_18z_fc", "lwp_x_cloud_18z", "elevation_x_cloud_frac"):
            n_na = part[col].isna().sum()
            n_inf = (~part[col].abs().lt(float("inf"))).sum()
            if n_na or n_inf:
                raise BuildError(f"{name}: column {col} has {n_na} NaN / {n_inf} non-finite values")
    log("Duplicate-key and NaN/Inf checks passed for all new/derived columns in all partitions.")

    feature_cols = [c for c in train_df.columns if c not in NON_FEATURE_COLUMNS and c != "_fs_norm"]
    if "actual_SW_IN" in feature_cols:
        raise BuildError("label leaked into feature set")
    log(f"Final feature count: {len(feature_cols)}")

    out_cols = NON_FEATURE_COLUMNS + feature_cols
    for df in (train_df, val_df, blind_df):
        df.drop(columns=["_fs_norm"], inplace=True)

    atomic_write_csv(train_df[out_cols], OUT_DIR / "train.csv")
    atomic_write_csv(val_df[out_cols], OUT_DIR / "validation.csv")
    atomic_write_csv(blind_df[out_cols], OUT_DIR / "blind.csv")
    log("Wrote train.csv, validation.csv, blind.csv.")

    manifest_rows = []
    for fs_iso in planned_iso:
        partition = "TRAIN" if fs_iso in train_o else ("VALIDATION" if fs_iso in val_o else "BLIND")
        manifest_rows.append({
            "forecast_start": fs_iso, "partition": partition,
            "lead6_record_sha256": hash6[fs_iso], "lead7_30_record_sha256": hash730[fs_iso],
            "row_count": 24,
        })
    atomic_write_csv(pd.DataFrame(manifest_rows), OUT_DIR / "split_manifest.csv")
    log(f"Wrote split_manifest.csv ({len(manifest_rows)} origin rows).")

    hashes = {}
    for fname in ("train.csv", "validation.csv", "blind.csv", "split_manifest.csv"):
        hashes[fname] = sha256_file(OUT_DIR / fname)
    (OUT_DIR / "HASHES.sha256").write_text(
        "\n".join(f"{h}  {f}" for f, h in hashes.items()) + "\n", encoding="utf-8"
    )
    log("Wrote HASHES.sha256: " + json.dumps(hashes, indent=2))

    return len(feature_cols)


if __name__ == "__main__":
    try:
        n = build()
        print(f"BUILD_OK features={n}")
    except BuildError as e:
        print(f"BUILD_BLOCKED: {e}")
        sys.exit(2)
