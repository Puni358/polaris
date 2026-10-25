#!/usr/bin/env python3
"""
POLARIS — Official One-Shot 2025 Blind Evaluation for Clean 18Z Lineage
======================================================================
Strictly evaluates frozen models (Clean Stage 4, Candidate F Successor v2,
Candidate K, Candidate N1, and Candidate N6) on the 2025 Blind Partition.

Governance Enforced:
  - ZERO model training, tuning, or parameter refitting.
  - Strict SHA-256 pre-asserted verification of frozen model joblib files.
  - 2,000 paired origin-level clustered block bootstrap CIs (N = 364 clusters).
  - Low-elevation (<30 deg) and high-elevation (>=30 deg) sub-regime breakdowns.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
RESEARCH_ROOT = SCRIPT_DIR.parent
POLARIS_ROOT = SCRIPT_DIR.parents[3]
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Input data files
BLIND_DATASET_V2 = RESEARCH_ROOT / "candidate_f_successor_18z/dataset_v2/blind.csv"
BLIND_BASELINE = RESEARCH_ROOT / "candidate_f_successor_18z/stage4_clean_baseline/blind_baseline.csv"

# Frozen model artifacts
MODEL_SUCC_V2 = RESEARCH_ROOT / "candidate_f_successor_18z/artifacts_v2/candidate_f_successor_v2_model.joblib"
MODEL_CAND_K = RESEARCH_ROOT / "candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib"
MODEL_CAND_N1 = ARTIFACTS_DIR / "candidate_n1_model.joblib"
MODEL_CAND_N6 = ARTIFACTS_DIR / "candidate_n6_model.joblib"

# Pre-asserted SHA-256 Hashes
EXPECTED_HASHES = {
    "successor_v2": "fb4ce1020fe8259acaf23cf0762cc0548266a409679bf98626643dc704399fa4",
    "candidate_k": "8fa57cedd6aa9ad0f8e4077f82dff3d550a22acaee44e924869b94360165b8e7",
    "candidate_n1": "7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7",
    "candidate_n6": "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197",
}

SUCCESSOR_33_FEATURES: List[str] = [
    "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700", "lwp_18z_fc", "iwp_18z_fc", "lwp_x_cloud_18z",
    "elevation_x_cloud_frac"
]

CANDIDATE_K_35_FEATURES: List[str] = SUCCESSOR_33_FEATURES + [
    "pred_stage4_clean",
    "clean_attenuation"
]

CANDIDATE_N1_36_FEATURES: List[str] = CANDIDATE_K_35_FEATURES + [
    "elevation_x_transition_cloud"
]


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_models():
    print("=" * 80)
    print("VERIFYING FROZEN MODEL SHA-256 INTEGRITY (ZERO RETRAINING)")
    print("=" * 80)
    for key, path, exp_hash in [
        ("Candidate F Successor v2", MODEL_SUCC_V2, EXPECTED_HASHES["successor_v2"]),
        ("Candidate K", MODEL_CAND_K, EXPECTED_HASHES["candidate_k"]),
        ("Candidate N1", MODEL_CAND_N1, EXPECTED_HASHES["candidate_n1"]),
        ("Candidate N6", MODEL_CAND_N6, EXPECTED_HASHES["candidate_n6"]),
    ]:
        act_hash = sha256_file(path)
        assert act_hash == exp_hash, f"Hash mismatch for {key}: {act_hash} != {exp_hash}"
        print(f"  [MATCH] {key:<26}: {act_hash}")
    print("All model cryptographic checksums verified successfully.\n")


def compute_metrics(y_p: np.ndarray, y_t: np.ndarray, mask: np.ndarray) -> Dict[str, float]:
    err = (y_p - y_t)[mask]
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    bias = float(np.mean(err))
    mean_obs = float(np.mean(y_t[mask]))
    nmae = float((mae / mean_obs) * 100.0) if mean_obs > 0 else 0.0
    return {"mae": mae, "rmse": rmse, "bias": bias, "nmae_pct": nmae}


def run_paired_bootstrap(
    df: pd.DataFrame,
    y_cand: np.ndarray,
    y_ref: np.ndarray,
    day_mask: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42,
) -> Dict[str, float]:
    n_orig = df["fs_dt"].nunique()
    y_t = df["actual_SW_IN"].values
    y_t_3d = y_t.reshape(n_orig, 24)
    y_c_3d = y_cand.reshape(n_orig, 24)
    y_r_3d = y_ref.reshape(n_orig, 24)
    d_3d = day_mask.reshape(n_orig, 24)

    cand_abs = np.sum(np.abs(y_c_3d - y_t_3d) * d_3d, axis=1)
    ref_abs = np.sum(np.abs(y_r_3d - y_t_3d) * d_3d, axis=1)
    day_counts = np.sum(d_3d, axis=1)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n_orig, size=n_orig)
        diffs[b] = (np.sum(cand_abs[idx]) - np.sum(ref_abs[idx])) / np.sum(day_counts[idx])

    delta = float(np.mean(np.abs((y_cand - y_t)[day_mask])) - np.mean(np.abs((y_ref - y_t)[day_mask])))
    ci_lo = float(np.percentile(diffs, 2.5))
    ci_hi = float(np.percentile(diffs, 97.5))
    return {
        "delta_mae": delta,
        "ci95_lo": ci_lo,
        "ci95_hi": ci_hi,
        "passes_gate": bool(ci_hi < 0.0),
    }


def main():
    verify_models()

    print("[DATA] Loading 2025 blind dataset and clean Stage 4 baseline...")
    df_raw = pd.read_csv(BLIND_DATASET_V2)
    df_base = pd.read_csv(BLIND_BASELINE)

    df_raw["fs_dt"] = pd.to_datetime(df_raw["forecast_start"], utc=True)
    df_base["fs_dt"] = pd.to_datetime(df_base["forecast_start"], utc=True)

    join_cols = ["fs_dt", "horizon_hour", "pred_stage4_clean"]
    df = df_raw.merge(df_base[join_cols], on=["fs_dt", "horizon_hour"], how="inner")
    df = df.sort_values(["fs_dt", "horizon_hour"]).reset_index(drop=True)

    assert len(df) == 8736, f"Expected 8736 rows, got {len(df)}"
    n_orig = df["fs_dt"].nunique()
    assert n_orig == 364, f"Expected 364 origins, got {n_orig}"
    assert (df["fs_dt"].dt.year == 2025).all(), "Non-2025 rows found in blind partition!"

    # Feature Engineering
    df["clean_attenuation"] = df["clearsky_ghi"] - df["pred_stage4_clean"]
    is_trans = ((df["cloud_frac"] >= 0.2) & (df["cloud_frac"] < 0.6)).astype(np.float64)
    df["elevation_x_transition_cloud"] = df["solar_elevation"] * is_trans

    # Night Zeroing & Daytime Evaluation Masks
    causal_day_mask = (df["solar_elevation"].values > 0.0) & (df["clearsky_ghi"].values > 0.0)
    day_mask = df["is_daytime"].values
    n_day = int(day_mask.sum())
    print(f"[DATA] 2025 Blind: {len(df)} total rows across {n_orig} origins (Daytime rows: {n_day})\n")

    # 1. Clean Stage 4 Physical Baseline
    print("[INFERENCE] Evaluating Clean Stage 4 Physical Baseline...")
    pred_stage4 = np.where(causal_day_mask, np.maximum(0.0, df["pred_stage4_clean"].values), 0.0)

    # 2. Candidate F Successor v2 (33 features)
    print("[INFERENCE] Evaluating Candidate F Successor v2...")
    m_succ = joblib.load(MODEL_SUCC_V2)
    r_succ = m_succ.predict(df[SUCCESSOR_33_FEATURES].values)
    pred_succ_raw = np.maximum(0.0, df["pred_stage4_clean"].values + r_succ)
    pred_successor_v2 = np.where(causal_day_mask, pred_succ_raw, 0.0)

    # 3. Candidate K (35 features)
    print("[INFERENCE] Evaluating Candidate K...")
    m_k = joblib.load(MODEL_CAND_K)
    r_k = m_k.predict(df[CANDIDATE_K_35_FEATURES].values)
    pred_k_raw = np.clip(df["pred_stage4_clean"].values + r_k, 0.0, None)
    pred_cand_k = np.where(causal_day_mask, pred_k_raw, 0.0)

    # 4. Candidate N1 (36 features, single tree)
    print("[INFERENCE] Evaluating Candidate N1...")
    m_n1 = joblib.load(MODEL_CAND_N1)
    r_n1 = m_n1.predict(df[CANDIDATE_N1_36_FEATURES].values)
    pred_n1_raw = np.clip(df["pred_stage4_clean"].values + r_n1, 0.0, None)
    pred_cand_n1 = np.where(causal_day_mask, pred_n1_raw, 0.0)

    # 5. Candidate N6 (36 features, 25-seed bagged additive + 15-seed kt specialist ramp)
    print("[INFERENCE] Evaluating Candidate N6...")
    b_n6 = joblib.load(MODEL_CAND_N6)
    
    # 25 additive models
    preds_add = np.zeros((len(b_n6["additive_models"]), len(df)), dtype=np.float64)
    for i, m_add in enumerate(b_n6["additive_models"]):
        r_i = m_add.predict(df[CANDIDATE_N1_36_FEATURES].values)
        preds_add[i] = np.clip(df["pred_stage4_clean"].values + r_i, 0.0, None)
    y_add_bagged = np.mean(preds_add, axis=0)

    # 15 kt specialist models
    eps_kt = b_n6["eps_kt"]
    denom_blind = df["clearsky_ghi_terrain_adjusted"].values + eps_kt
    ceiling = np.maximum(df["clearsky_ghi"].values * 1.25, df["pred_stage4_clean"].values)
    preds_kt = np.zeros((len(b_n6["kt_models"]), len(df)), dtype=np.float64)
    for i, m_kt in enumerate(b_n6["kt_models"]):
        rkt_i = m_kt.predict(df[CANDIDATE_N1_36_FEATURES].values)
        y_kt_i = df["pred_stage4_clean"].values + rkt_i * denom_blind
        preds_kt[i] = np.clip(y_kt_i, 0.0, ceiling)
    y_kt_bagged = np.mean(preds_kt, axis=0)

    # Smooth Ramp Blending
    elev = df["solar_elevation"].values
    ramp_denom = b_n6["ramp_full_deg"] - b_n6["ramp_start_deg"]
    alpha_he = b_n6["max_ramp_weight"] * np.clip((elev - b_n6["ramp_start_deg"]) / ramp_denom, 0.0, 1.0)
    unshaded = (df["terrain_solar_obstruction_flag"].values == 0).astype(np.float64)
    w = alpha_he * unshaded
    y_blend = (1.0 - w) * y_add_bagged + w * y_kt_bagged
    pred_cand_n6 = np.where(causal_day_mask, y_blend, 0.0)

    # Save Predictions CSV
    print("\n[EXPORT] Saving blind_2025_predictions.csv...")
    df_out = pd.DataFrame({
        "forecast_start": df["fs_dt"].dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "horizon_hour": df["horizon_hour"].astype(int),
        "timestamp": pd.to_datetime(df["timestamp"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "actual_SW_IN": df["actual_SW_IN"].astype(float),
        "is_daytime": day_mask,
        "is_night_causal": (~causal_day_mask),
        "solar_elevation": df["solar_elevation"].astype(float),
        "cloud_frac": df["cloud_frac"].astype(float),
        "pred_stage4_clean": df["pred_stage4_clean"].astype(float),
        "clean_attenuation": df["clean_attenuation"].astype(float),
        "elevation_x_transition_cloud": df["elevation_x_transition_cloud"].astype(float),
        "pred_clean_stage4_baseline": pred_stage4,
        "pred_successor_v2": pred_successor_v2,
        "pred_candidate_k": pred_cand_k,
        "pred_candidate_n1": pred_cand_n1,
        "pred_candidate_n6": pred_cand_n6,
    })
    preds_out_path = ARTIFACTS_DIR / "blind_2025_predictions.csv"
    df_out.to_csv(preds_out_path, index=False)
    print(f"Saved {preds_out_path.name} (SHA-256: {sha256_file(preds_out_path)})")

    # Metrics Computation
    y_true = df["actual_SW_IN"].values
    he_mask = day_mask & (df["solar_elevation"].values >= 30.0)
    le_mask = day_mask & (df["solar_elevation"].values < 30.0)

    models = [
        ("Clean Stage 4 Baseline", pred_stage4),
        ("Candidate F Successor v2", pred_successor_v2),
        ("Candidate K", pred_cand_k),
        ("Candidate N1", pred_cand_n1),
        ("Candidate N6", pred_cand_n6),
    ]

    metrics_dict = {}
    for name, p in models:
        metrics_dict[name] = {
            "overall": compute_metrics(p, y_true, day_mask),
            "high_elevation": compute_metrics(p, y_true, he_mask),
            "low_elevation": compute_metrics(p, y_true, le_mask),
        }

    # 2,000-draw paired bootstrap comparisons
    print("[BOOTSTRAP] Computing 2,000-resample paired origin block bootstrap CIs...")
    boot_dict = {
        "N6_vs_Clean_Stage4": run_paired_bootstrap(df, pred_cand_n6, pred_stage4, day_mask),
        "N6_vs_Successor_v2": run_paired_bootstrap(df, pred_cand_n6, pred_successor_v2, day_mask),
        "N6_vs_Candidate_K": run_paired_bootstrap(df, pred_cand_n6, pred_cand_k, day_mask),
        "N1_vs_Candidate_K": run_paired_bootstrap(df, pred_cand_n1, pred_cand_k, day_mask),
        "K_vs_Successor_v2": run_paired_bootstrap(df, pred_cand_k, pred_successor_v2, day_mask),
        "K_vs_Clean_Stage4": run_paired_bootstrap(df, pred_cand_k, pred_stage4, day_mask),
    }

    # Save BLIND_2025_RESULTS.json
    results_json = {
        "evaluation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "2025 Blind Partition (364 origins, 8736 rows, 5978 daytime rows)",
        "models_evaluated": metrics_dict,
        "bootstrap_comparisons": boot_dict,
    }
    results_path = ARTIFACTS_DIR / "BLIND_2025_RESULTS.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2)
    print(f"Saved {results_path.name} (SHA-256: {sha256_file(results_path)})\n")

    # Print Official Terminal Table
    print("=" * 128)
    print("POLARIS — OFFICIAL 2025 BLIND EVALUATION RESULTS (5 CLEAN 18Z MODELS, N=5,978 DAYTIME ROWS)")
    print("=" * 128)
    header = f"{'Model Architecture':<26} | {'Blind MAE':>9} | {'RMSE':>8} | {'Bias':>7} | {'LE MAE':>7} | {'HE MAE':>8} | {'HE Bias':>8} | {'vs K (95% Bootstrap CI)':<26} | {'Gate'}"
    print(header)
    print("-" * 128)

    ref_k_pred = pred_cand_k
    for name, p in models:
        m_ov = metrics_dict[name]["overall"]
        m_he = metrics_dict[name]["high_elevation"]
        m_le = metrics_dict[name]["low_elevation"]
        
        if name == "Candidate K":
            ci_str = "+0.0000 [+0.0000, +0.0000]"
            gate_str = "CTRL"
        elif name == "Candidate N6":
            b = boot_dict["N6_vs_Candidate_K"]
            ci_str = f"{b['delta_mae']:+.4f} [{b['ci95_lo']:+.4f}, {b['ci95_hi']:+.4f}]"
            gate_str = "PASS" if b["passes_gate"] else "HOLD"
        elif name == "Candidate N1":
            b = boot_dict["N1_vs_Candidate_K"]
            ci_str = f"{b['delta_mae']:+.4f} [{b['ci95_lo']:+.4f}, {b['ci95_hi']:+.4f}]"
            gate_str = "PASS" if b["passes_gate"] else "HOLD"
        else:
            b = run_paired_bootstrap(df, p, ref_k_pred, day_mask)
            ci_str = f"{b['delta_mae']:+.4f} [{b['ci95_lo']:+.4f}, {b['ci95_hi']:+.4f}]"
            gate_str = "BASE"

        print(
            f"{name:<26} | {m_ov['mae']:9.4f} | {m_ov['rmse']:8.4f} | {m_ov['bias']:+7.4f} | "
            f"{m_le['mae']:7.4f} | {m_he['mae']:8.4f} | {m_he['bias']:+8.4f} | {ci_str:<26} | {gate_str}"
        )
    print("=" * 128)
    print(f"Paired Bootstrap N6 vs Clean Stage 4: Delta MAE = {boot_dict['N6_vs_Clean_Stage4']['delta_mae']:+.4f} W/m^2 (95% CI: [{boot_dict['N6_vs_Clean_Stage4']['ci95_lo']:+.4f}, {boot_dict['N6_vs_Clean_Stage4']['ci95_hi']:+.4f}])")
    print(f"Paired Bootstrap N6 vs Successor v2 : Delta MAE = {boot_dict['N6_vs_Successor_v2']['delta_mae']:+.4f} W/m^2 (95% CI: [{boot_dict['N6_vs_Successor_v2']['ci95_lo']:+.4f}, {boot_dict['N6_vs_Successor_v2']['ci95_hi']:+.4f}])")
    print(f"Paired Bootstrap N6 vs Candidate K  : Delta MAE = {boot_dict['N6_vs_Candidate_K']['delta_mae']:+.4f} W/m^2 (95% CI: [{boot_dict['N6_vs_Candidate_K']['ci95_lo']:+.4f}, {boot_dict['N6_vs_Candidate_K']['ci95_hi']:+.4f}])")
    print("=" * 128)

if __name__ == "__main__":
    main()
