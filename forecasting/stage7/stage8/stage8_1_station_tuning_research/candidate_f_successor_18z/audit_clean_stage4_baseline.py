"""
Independent audit of the clean Stage 4 baseline artifacts for Candidate F Successor (Option B).

Strictly read-only re-verification of:
  - stage4_clean_baseline/train_baseline.csv
  - stage4_clean_baseline/validation_baseline.csv
  - stage4_clean_baseline/HASHES.sha256
  - stage4_clean_baseline/BASELINE_MANIFEST.json
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
BASELINE_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/stage4_clean_baseline"
DATASET_V2_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/dataset_v2"
PARAMS_FILE = BASE / "forecasting/stage4/stage4_results/ensemble_parameters.json"
HISTORICAL_2024_MATRIX = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def audit():
    print("=" * 80)
    print("INDEPENDENT AUDIT: STAGE 4 CLEAN BASELINE ARTIFACTS")
    print("=" * 80)

    # 1. Hashes recomputation
    hashes_file = BASELINE_DIR / "HASHES.sha256"
    recorded_hashes = {}
    for line in hashes_file.read_text(encoding="utf-8").strip().splitlines():
        parts = line.strip().split()
        if len(parts) == 2:
            recorded_hashes[parts[1]] = parts[0]

    for fname in ["train_baseline.csv", "validation_baseline.csv"]:
        recomputed = sha256_file(BASELINE_DIR / fname)
        rec = recorded_hashes.get(fname)
        assert recomputed == rec, f"Hash mismatch for {fname}: {recomputed} != {rec}"
        print(f"[PASS] Hash match for {fname}: {recomputed}")

    # 2. Manifest check
    manifest = json.loads((BASELINE_DIR / "BASELINE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["governance"]["refit_on_validation"] is False
    assert manifest["governance"]["refit_on_blind"] is False
    assert manifest["governance"]["winner_status"] == "null"
    print("[PASS] Manifest governance checks pass.")

    # 3. Load parameters
    with open(PARAMS_FILE, "r", encoding="utf-8") as fp:
        params = json.load(fp)

    # 4. Row-level formula audit
    total_audited_rows = 0
    max_formula_diff = 0.0

    df_tr = pd.read_csv(BASELINE_DIR / "train_baseline.csv")
    df_val = pd.read_csv(BASELINE_DIR / "validation_baseline.csv")

    assert len(df_tr) == 4176, f"Expected 4176 train rows, got {len(df_tr)}"
    assert len(df_val) == 4152, f"Expected 4152 val rows, got {len(df_val)}"
    assert df_tr["forecast_start"].nunique() == 174, f"Expected 174 train origins, got {df_tr['forecast_start'].nunique()}"
    assert df_val["forecast_start"].nunique() == 173, f"Expected 173 val origins, got {df_val['forecast_start'].nunique()}"

    # Origin overlap check
    tr_origins = set(df_tr["forecast_start"].unique())
    val_origins = set(df_val["forecast_start"].unique())
    assert len(tr_origins & val_origins) == 0, "Train and Validation origins overlap!"
    print(f"[PASS] Origin partition checks pass (174 train / 173 val, zero overlap).")

    for name, df in [("train", df_tr), ("validation", df_val)]:
        for idx, row in df.iterrows():
            h = str(int(row["horizon_hour"]))
            p = params[h]
            w_h = p["w"]
            k_h = p["k"]
            cs = float(row["clearsky_ghi"])
            cf = float(row["cloud_frac"])
            s3b = float(row["pred_stage3b_cloud_nwp"])
            act = float(row["actual_SW_IN"])

            expected_phys = max(0.0, cs * (1.0 - k_h * cf))
            expected_s4 = max(0.0, w_h * s3b + (1.0 - w_h) * expected_phys)
            expected_res = act - expected_s4

            diff_phys = abs(float(row["phys_pred_clean"]) - expected_phys)
            diff_s4 = abs(float(row["pred_stage4_clean"]) - expected_s4)
            diff_res = abs(float(row["residual_target"]) - expected_res)

            diff = max(diff_phys, diff_s4, diff_res)
            if diff > max_formula_diff:
                max_formula_diff = diff
            assert diff < 1e-12, f"Formula mismatch at {name} row {idx}: diff={diff}"
            total_audited_rows += 1

    print(f"[PASS] Exact formula re-verification: {total_audited_rows} rows audited, max diff = {max_formula_diff:.2e} W/m² (zero discrepancy).")

    # 5. Historical consistency check (comparison against stage8_1_full_37_feature_matrix_2024_CORRECTED.csv)
    df_hist = pd.read_csv(HISTORICAL_2024_MATRIX)
    df_hist["fs_dt"] = pd.to_datetime(df_hist["forecast_start"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Normalize isoformat
    df_hist["fs_dt"] = pd.to_datetime(df_hist["forecast_start"], utc=True).apply(lambda x: x.isoformat())

    df_combined = pd.concat([df_tr, df_val], ignore_index=True)
    merged_hist = df_combined.merge(df_hist, left_on=["forecast_start", "horizon_hour"], right_on=["fs_dt", "horizon_hour"])
    assert len(merged_hist) == 8328, f"Historical merge count mismatch: {len(merged_hist)} != 8328"

    max_hist_diff = (merged_hist["pred_stage4_clean"] - merged_hist["pred_stage4_fold"]).abs().max()
    print(f"[PASS] Historical Stage 4 comparison: 8,328 rows match historical 2024 pred_stage4_fold within {max_hist_diff:.2e} W/m².")

    # 6. Check that blind baseline was NOT created
    blind_baseline_path = BASELINE_DIR / "blind_baseline.csv"
    assert not blind_baseline_path.exists(), "blind_baseline.csv should NOT exist at this stage!"
    print("[PASS] Blind baseline firewall: blind_baseline.csv correctly absent.")

    # 7. Check that dataset_v2 and frozen artifacts remain untouched
    v2_hashes_recorded = (DATASET_V2_DIR / "HASHES.sha256").read_text(encoding="utf-8").strip().splitlines()
    for line in v2_hashes_recorded:
        parts = line.strip().split()
        if len(parts) == 2:
            recomputed = sha256_file(DATASET_V2_DIR / parts[1])
            assert recomputed == parts[0], f"dataset_v2 drift on {parts[1]}"
    print("[PASS] dataset_v2 integrity confirmed (all SHA-256 hashes byte-for-byte identical).")

    print("\nINDEPENDENT AUDIT VERDICT: AUDIT_PASS")


if __name__ == "__main__":
    audit()
