#!/usr/bin/env python3
"""
POLARIS L2 Uncertainty-Aware Risk Interface — Split-Conformal EBR Evaluation
============================================================================
Bridges the frozen Candidate N6 ensemble (`candidate_n6_model.joblib`) to the
GAP19 / HiGHS MILP `ebr_target_wh` dynamic battery reserve vector.

Governance & Protocol:
  1. Strictly verifies SHA-256 checksums of frozen models before execution.
  2. Calibrates Split-Conformal non-conformity quantiles strictly on 2024-ODD
     validation origins (N = 173 origins, 2,883 daytime rows).
  3. Evaluates out-of-sample empirical coverage, 6-hour forward cumulative energy
     shortfall protection (J1 safety objective), and average reserve sizing (J3)
     on the 2025 Blind Set (N = 364 origins, 5,978 daytime rows).
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
RESEARCH_ROOT = SCRIPT_DIR.parent
ARTIFACTS_DIR = SCRIPT_DIR / "artifacts"

# Input datasets
MATRIX_2024 = RESEARCH_ROOT / "candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
BLIND_2025_FEATURES = RESEARCH_ROOT / "candidate_f_successor_18z/dataset_v2/blind.csv"
BLIND_2025_BASELINE = RESEARCH_ROOT / "candidate_f_successor_18z/stage4_clean_baseline/blind_baseline.csv"

# Frozen model binaries
MODEL_CAND_K = RESEARCH_ROOT / "candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib"
MODEL_CAND_N6 = ARTIFACTS_DIR / "candidate_n6_model.joblib"

EXPECTED_HASHES = {
    "candidate_k": "8fa57cedd6aa9ad0f8e4077f82dff3d550a22acaee44e924869b94360165b8e7",
    "candidate_n6": "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197",
}

# Microgrid Physical Conversion Constants (L2 EMS Interface Contract)
K_PV: float = 51.0            # 300 m^2 * 0.20 * 0.85 = 51.0 W / (W/m^2)
P_INV_MAX_W: float = 60000.0  # Inverter clipping ceiling (60 kW)
ETA_DIS: float = 0.95         # Battery discharge efficiency
EBR_BASE_WH: float = 15000.0  # Baseline minimum Emergency Battery Reserve (15 kWh)
WINDOW_W: int = 6             # 6-hour forward survivability lookahead window W_t


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def irrad_to_pv_power_w(irrad_wm2: np.ndarray) -> np.ndarray:
    """Converts surface irradiance (W/m^2) to AC PV power (W) with inverter clipping."""
    return np.minimum(P_INV_MAX_W, K_PV * np.maximum(0.0, irrad_wm2))


def prepare_2024_odd() -> pd.DataFrame:
    df = pd.read_parquet(MATRIX_2024)
    df = df.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)
    is_trans = ((df["cloud_frac"] >= 0.2) & (df["cloud_frac"] < 0.6)).astype(np.float64)
    df["elevation_x_transition_cloud"] = df["solar_elevation"] * is_trans
    df["causal_day_mask"] = (df["solar_elevation"] > 0.0) & (df["clearsky_ghi"] > 0.0)
    df_odd = df[~df["is_even_origin"]].reset_index(drop=True)
    assert len(df_odd) == 4152 and df_odd["origin_dt"].nunique() == 173
    return df_odd


def prepare_2025_blind() -> pd.DataFrame:
    df_raw = pd.read_csv(BLIND_2025_FEATURES)
    df_base = pd.read_csv(BLIND_2025_BASELINE)
    df_raw["origin_dt"] = pd.to_datetime(df_raw["forecast_start"], utc=True)
    df_base["origin_dt"] = pd.to_datetime(df_base["forecast_start"], utc=True)

    df = df_raw.merge(
        df_base[["origin_dt", "horizon_hour", "pred_stage4_clean"]],
        on=["origin_dt", "horizon_hour"],
        how="inner",
    )
    df = df.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)
    df["clean_attenuation"] = df["clearsky_ghi"] - df["pred_stage4_clean"]
    is_trans = ((df["cloud_frac"] >= 0.2) & (df["cloud_frac"] < 0.6)).astype(np.float64)
    df["elevation_x_transition_cloud"] = df["solar_elevation"] * is_trans
    df["causal_day_mask"] = (df["solar_elevation"] > 0.0) & (df["clearsky_ghi"] > 0.0)
    assert len(df) == 8736 and df["origin_dt"].nunique() == 364
    return df


def infer_n6_with_ensemble_spread(
    bundle: dict, df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns:
      - y_pred: Candidate N6 point forecast (W/m^2)
      - ens_std: Standard deviation across the 40 constituent trees (W/m^2)
      - scale_s: Heteroscedastic conformal scale s(t) (W/m^2)
    """
    features = bundle["features"]
    X = df[features].values
    st4 = df["pred_stage4_clean"].values
    cday = df["causal_day_mask"].values

    # 25 additive trees
    preds_add = np.zeros((len(bundle["additive_models"]), len(df)), dtype=np.float64)
    for i, m_add in enumerate(bundle["additive_models"]):
        preds_add[i] = np.clip(st4 + m_add.predict(X), 0.0, None)
    y_add_mean = np.mean(preds_add, axis=0)

    # 15 k_t specialist trees
    eps_kt = bundle["eps_kt"]
    denom = df["clearsky_ghi_terrain_adjusted"].values + eps_kt
    ceiling = np.maximum(df["clearsky_ghi"].values * 1.25, st4)
    preds_kt = np.zeros((len(bundle["kt_models"]), len(df)), dtype=np.float64)
    for i, m_kt in enumerate(bundle["kt_models"]):
        y_kt_i = st4 + m_kt.predict(X) * denom
        preds_kt[i] = np.clip(y_kt_i, 0.0, ceiling)
    y_kt_mean = np.mean(preds_kt, axis=0)

    # Smooth ramp weight
    elev = df["solar_elevation"].values
    ramp_denom = bundle["ramp_full_deg"] - bundle["ramp_start_deg"]
    alpha_he = bundle["max_ramp_weight"] * np.clip(
        (elev - bundle["ramp_start_deg"]) / ramp_denom, 0.0, 1.0
    )
    unshaded = (df["terrain_solar_obstruction_flag"].values == 0).astype(np.float64)
    w = alpha_he * unshaded

    y_pred = np.where(cday, (1.0 - w) * y_add_mean + w * y_kt_mean, 0.0)

    # Combine all 40 member predictions to measure epistemic + structural spread
    all_members = np.vstack([preds_add, preds_kt])
    ens_std = np.where(cday, np.std(all_members, axis=0), 0.0)

    # Physical heteroscedastic uncertainty scale: ensemble spread + 10% terrain clearsky + floor
    cs_terr = df["clearsky_ghi_terrain_adjusted"].values
    scale_s = np.where(cday, ens_std + 0.10 * cs_terr + 5.0, 0.0)
    return y_pred, ens_std, scale_s


def compute_window_shortfall_wh(
    y_pred_3d: np.ndarray, y_true_3d: np.ndarray, window_w: int = WINDOW_W
) -> np.ndarray:
    """
    Computes realized forward cumulative battery energy shortfall (Wh) over W_t = [t .. min(t+W-1, 23)]
    caused by solar overprediction (y_pred > y_true), accounting for inverter saturation and eta_dis.
    """
    p_pred = irrad_to_pv_power_w(y_pred_3d)
    p_true = irrad_to_pv_power_w(y_true_3d)
    hourly_shortfall_wh = np.maximum(0.0, p_pred - p_true) / ETA_DIS

    n_orig = y_pred_3d.shape[0]
    cum_shortfall_wh = np.zeros((n_orig, 24), dtype=np.float64)
    for t in range(24):
        t_end = min(t + window_w, 24)
        cum_shortfall_wh[:, t] = np.sum(hourly_shortfall_wh[:, t:t_end], axis=1)
    return cum_shortfall_wh


def main():
    # 1. Verify Frozen Model Hashes
    for label, path, exp_hash in [
        ("Candidate K", MODEL_CAND_K, EXPECTED_HASHES["candidate_k"]),
        ("Candidate N6", MODEL_CAND_N6, EXPECTED_HASHES["candidate_n6"]),
    ]:
        actual = sha256_file(path)
        assert actual == exp_hash, f"SHA-256 mismatch on {label}: {actual}"
    print("[PROVENANCE] Verified frozen Candidate K & Candidate N6 model SHA-256 checksums.")

    df_odd = prepare_2024_odd()
    df_blind = prepare_2025_blind()

    b_n6 = joblib.load(MODEL_CAND_N6)
    m_k = joblib.load(MODEL_CAND_K)

    # 2. Run Inference on 2024-ODD (Calibration Set) and 2025-Blind (Evaluation Set)
    y_n6_odd, std_odd, scale_odd = infer_n6_with_ensemble_spread(b_n6, df_odd)
    y_n6_blind, std_blind, scale_blind = infer_n6_with_ensemble_spread(b_n6, df_blind)

    # Candidate K inference for comparison
    k_feats = b_n6["features"][:-1]
    y_k_odd = np.where(
        df_odd["causal_day_mask"].values,
        np.clip(df_odd["pred_stage4_clean"].values + m_k.predict(df_odd[k_feats].values), 0.0, None),
        0.0,
    )
    y_k_blind = np.where(
        df_blind["causal_day_mask"].values,
        np.clip(df_blind["pred_stage4_clean"].values + m_k.predict(df_blind[k_feats].values), 0.0, None),
        0.0,
    )

    # 3. Calibrate One-Sided Split-Conformal Lower Irradiance Bounds on 2024-ODD Daytime Rows
    day_odd = df_odd["is_daytime"].values
    day_blind = df_blind["is_daytime"].values
    y_true_odd = df_odd["actual_SW_IN"].values
    y_true_blind = df_blind["actual_SW_IN"].values

    # Normalized non-conformity score: (y_pred - y_true) / scale_s (positive when overpredicting)
    norm_scores_odd = ((y_n6_odd - y_true_odd) / np.maximum(scale_odd, 1e-6))[day_odd]
    n_cal = len(norm_scores_odd)

    conformal_irrad_summary = {}
    for alpha, label in [(0.10, "90%"), (0.05, "95%")]:
        q_level = min(np.ceil((n_cal + 1) * (1.0 - alpha)) / n_cal, 1.0)
        q_hat_norm = float(np.quantile(norm_scores_odd, q_level))

        # Construct lower bounds on 2024-ODD and 2025-Blind
        y_lo_odd = np.maximum(0.0, y_n6_odd - q_hat_norm * scale_odd)
        y_lo_blind = np.maximum(0.0, y_n6_blind - q_hat_norm * scale_blind)

        cov_odd = float(np.mean(y_true_odd[day_odd] >= y_lo_odd[day_odd])) * 100.0
        cov_blind = float(np.mean(y_true_blind[day_blind] >= y_lo_blind[day_blind])) * 100.0
        mean_width_blind = float(np.mean((y_n6_blind - y_lo_blind)[day_blind]))

        conformal_irrad_summary[label] = {
            "nominal_coverage_pct": (1.0 - alpha) * 100.0,
            "q_hat_normalized": q_hat_norm,
            "val_2024_odd_coverage_pct": cov_odd,
            "blind_2025_coverage_pct": cov_blind,
            "blind_2025_mean_safety_buffer_wm2": mean_width_blind,
        }

    # 4. Calibrate 6-Hour Forward Cumulative Energy Shortfall EBR(t) on 2024-ODD Origins (N=173)
    n_orig_odd = 173
    n_orig_blind = 364

    sf_n6_odd = compute_window_shortfall_wh(
        y_n6_odd.reshape(n_orig_odd, 24), y_true_odd.reshape(n_orig_odd, 24)
    )
    sf_n6_blind = compute_window_shortfall_wh(
        y_n6_blind.reshape(n_orig_blind, 24), y_true_blind.reshape(n_orig_blind, 24)
    )
    sf_k_blind = compute_window_shortfall_wh(
        y_k_blind.reshape(n_orig_blind, 24), y_true_blind.reshape(n_orig_blind, 24)
    )

    # Heteroscedastic window scale S_W(t) in Wh
    scale_w_odd = np.zeros((n_orig_odd, 24), dtype=np.float64)
    scale_w_blind = np.zeros((n_orig_blind, 24), dtype=np.float64)
    s_odd_3d = (K_PV * scale_odd / ETA_DIS).reshape(n_orig_odd, 24)
    s_blind_3d = (K_PV * scale_blind / ETA_DIS).reshape(n_orig_blind, 24)

    for t in range(24):
        t_end = min(t + WINDOW_W, 24)
        scale_w_odd[:, t] = np.sum(s_odd_3d[:, t:t_end], axis=1) + 100.0
        scale_w_blind[:, t] = np.sum(s_blind_3d[:, t:t_end], axis=1) + 100.0

    # Fit conformal window multiplier on 2024-ODD active windows
    active_odd = scale_w_odd > 100.0
    window_ratios_odd = (sf_n6_odd / scale_w_odd)[active_odd]
    n_wcal = len(window_ratios_odd)

    q90_w = float(np.quantile(window_ratios_odd, min(np.ceil((n_wcal + 1) * 0.90) / n_wcal, 1.0)))
    q95_w = float(np.quantile(window_ratios_odd, min(np.ceil((n_wcal + 1) * 0.95) / n_wcal, 1.0)))

    # Evaluate Reserve Policies on 2025 Blind Daytime Windows
    day_blind_3d = day_blind.reshape(n_orig_blind, 24)

    ebr_static = np.full_like(sf_n6_blind, EBR_BASE_WH)
    ebr_n6_90 = np.maximum(EBR_BASE_WH, q90_w * scale_w_blind)
    ebr_n6_95 = np.maximum(EBR_BASE_WH, q95_w * scale_w_blind)

    def eval_ebr_policy(sf_3d: np.ndarray, ebr_3d: np.ndarray, mask_3d: np.ndarray) -> Dict[str, float]:
        sf_act = sf_3d[mask_3d]
        ebr_act = ebr_3d[mask_3d]
        covered = sf_act <= ebr_act
        uncomp_deficit = np.maximum(0.0, sf_act - ebr_act)
        return {
            "window_survival_rate_pct": float(np.mean(covered)) * 100.0,
            "exceedance_hours_count": int(np.sum(~covered)),
            "mean_ebr_Allocation_kwh": float(np.mean(ebr_act)) / 1000.0,
            "mean_uncompensated_deficit_wh": float(np.mean(uncomp_deficit)),
            "max_uncompensated_deficit_kwh": float(np.max(uncomp_deficit)) / 1000.0,
        }

    policies = {
        "Candidate K + Static 15 kWh EBR": eval_ebr_policy(sf_k_blind, ebr_static, day_blind_3d),
        "Candidate N6 + Static 15 kWh EBR": eval_ebr_policy(sf_n6_blind, ebr_static, day_blind_3d),
        "Candidate N6 + Conformal 90% Dynamic EBR": eval_ebr_policy(sf_n6_blind, ebr_n6_90, day_blind_3d),
        "Candidate N6 + Conformal 95% Dynamic EBR": eval_ebr_policy(sf_n6_blind, ebr_n6_95, day_blind_3d),
    }

    print("\n" + "=" * 105)
    print("1. SPLIT-CONFORMAL ONE-SIDED LOWER IRRADIANCE BOUND (CALIBRATED ON 2024-ODD -> TESTED ON 2025 BLIND)")
    print("=" * 105)
    print(f"{'Target Level':<15} | {'Nominal':>9} | {'2024-ODD Val Cov':>18} | {'2025 Blind Cov':>16} | {'Mean Buffer (W/m^2)':>20} | {'q_hat_norm':>10}")
    print("-" * 105)
    for lvl, d in conformal_irrad_summary.items():
        print(
            f"{lvl + ' Safety':<15} | {d['nominal_coverage_pct']:8.2f}% | "
            f"{d['val_2024_odd_coverage_pct']:17.2f}% | {d['blind_2025_coverage_pct']:15.2f}% | "
            f"{d['blind_2025_mean_safety_buffer_wm2']:20.2f} | {d['q_hat_normalized']:10.4f}"
        )
    print("=" * 105)

    print("\n" + "=" * 118)
    print("2. GAP19 6-HOUR FORWARD CUMULATIVE SHORTFALL RESERVE (EBR) SURVIVABILITY ON 2025 BLIND (N=5,978 DAYTIME HOURS)")
    print("=" * 118)
    print(f"{'EMS Reserve Policy (GAP19 Injection)':<42} | {'Survival Rate':>13} | {'Exceed Hrs':>10} | {'Mean EBR (kWh)':>14} | {'Mean Deficit (Wh)':>17} | {'Max Deficit (kWh)':>17}")
    print("-" * 118)
    for pname, pm in policies.items():
        print(
            f"{pname:<42} | {pm['window_survival_rate_pct']:12.2f}% | "
            f"{pm['exceedance_hours_count']:10d} | {pm['mean_ebr_Allocation_kwh']:14.2f} | "
            f"{pm['mean_uncompensated_deficit_wh']:17.2f} | {pm['max_uncompensated_deficit_kwh']:17.2f}"
        )
    print("=" * 118)

    out_json = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "conformal_irradiance_bounds": conformal_irrad_summary,
        "gap19_ebr_window_policies_2025_blind": policies,
    }
    out_path = ARTIFACTS_DIR / "L2_CONFORMAL_EBR_2025_RESULTS.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_json, f, indent=2)
    print(f"\n[SAVED] L2 Conformal EBR evaluation written to: {out_path}")


if __name__ == "__main__":
    main()