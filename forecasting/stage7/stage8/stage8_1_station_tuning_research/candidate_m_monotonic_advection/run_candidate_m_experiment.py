#!/usr/bin/env python3
"""
POLARIS Stage 8.1 Station-Tuning Research — Candidate M Experiment Suite
========================================================================
Tests Variance-Reduced Tabular Advection and Physical Monotonic Constraints.
Replaces deep temporal convolutions with Time-to-Impact advection fluxes and 
forces the GBDT to obey strict Beer-Lambert transmission laws (e.g., thicker 
clouds must never increase irradiance).
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

# ==============================================================================
# 1. REPOSITORY PATH RESOLUTION
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
RESEARCH_ROOT = SCRIPT_DIR.parent
CAND_K_DIR = RESEARCH_ROOT / "candidate_k_baseline_conditioning"

for p in [str(RESEARCH_ROOT), str(CAND_K_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Base 35 Features (Candidate K Contract)
CANDIDATE_K_35_FEATURES: List[str] = [
    "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700", "lwp_18z_fc", "iwp_18z_fc", "lwp_x_cloud_18z",
    "elevation_x_cloud_frac", "pred_stage4_clean", "clean_attenuation"
]

# Candidate M Features (Replaces neural advection with 2 Tabular impact scalars)
CANDIDATE_M_FEATURES: List[str] = CANDIDATE_K_35_FEATURES + [
    "wind_speed_700",
    "advection_lwp_flux_1h",
    "ema_cloud_frac_3h"
]

# Monotonic Constraints Matrix
# -1: Strictly decreasing (more cloud/water -> less irradiance)
# +1: Strictly increasing (higher clear-sky baseline -> more irradiance)
#  0: Unconstrained
MONOTONIC_MAP = {
    "cloud_frac": -1,
    "lwp_18z_fc": -1,
    "iwp_18z_fc": -1,
    "elevation_x_cloud_frac": -1,
    "pred_stage4_clean": 1,
    "clean_attenuation": 1,
    "ema_cloud_frac_3h": -1
}

def discover_and_load_2024_data() -> Tuple[pd.DataFrame, Path]:
    search_dirs = [CAND_K_DIR, RESEARCH_ROOT]
    for d in search_dirs:
        if d.exists():
            for f in d.rglob("*.parquet"):
                if "2025" in f.name or "blind" in f.name:
                    continue
                if "candidate_k_2024_clean_matrix" in f.name:
                    return pd.read_parquet(f), f
    raise FileNotFoundError("Could not auto-discover candidate_k_2024_clean_matrix.parquet.")

def engineer_candidate_m_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "causal_day_mask" not in df.columns:
        df["causal_day_mask"] = (df["solar_elevation"] > 0.0) & (df["clearsky_ghi"] > 0.0)
    df = df.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)
    grp = df.groupby("origin_dt", sort=False)

    # 1. 700 hPa Wind Speed Magnitude
    df["wind_speed_700"] = np.sqrt(np.square(df["u700"].fillna(0)) + np.square(df["v700"].fillna(0)))

    # 2. Time-to-Impact LWP Flux (100% Causal using 18Z MEPS forward trajectory)
    lwp_next1h = grp["lwp_18z_fc"].shift(-1).fillna(df["lwp_18z_fc"])
    df["advection_lwp_flux_1h"] = (lwp_next1h - df["lwp_18z_fc"]) * df["wind_speed_700"]

    # 3. Look-ahead EMA of incoming cloud cover density (3-hour window)
    c_h1 = grp["cloud_frac"].shift(-1).fillna(df["cloud_frac"])
    c_h2 = grp["cloud_frac"].shift(-2).fillna(c_h1)
    c_h3 = grp["cloud_frac"].shift(-3).fillna(c_h2)
    df["ema_cloud_frac_3h"] = (0.5 * c_h1) + (0.3 * c_h2) + (0.2 * c_h3)

    return df

def run_candidate_k_reproduction(df_even: pd.DataFrame, df_odd: pd.DataFrame) -> np.ndarray:
    tr_day = df_even[df_even["is_daytime"]].copy()
    model = HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)
    model.fit(tr_day[CANDIDATE_K_35_FEATURES], tr_day["actual_SW_IN"] - tr_day["pred_stage4_clean"])
    r_hat = model.predict(df_odd[CANDIDATE_K_35_FEATURES])
    y_hat = np.clip(df_odd["pred_stage4_clean"].values + r_hat, 0.0, None)
    return np.where(df_odd["causal_day_mask"].values, y_hat, 0.0)

def run_candidate_m_monotonic(df_even: pd.DataFrame, df_odd: pd.DataFrame) -> np.ndarray:
    tr_day = df_even[df_even["is_daytime"]].copy()
    eps_kt = 10.0
    denom_train = tr_day["clearsky_ghi_terrain_adjusted"].values + eps_kt
    
    # Target: dimensionless clearness residual
    y_rkt_train = (tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values) / denom_train
    
    # Build monotonic constraints array
    mono_cst = [MONOTONIC_MAP.get(f, 0) for f in CANDIDATE_M_FEATURES]

    model = HistGradientBoostingRegressor(
        loss="absolute_error", 
        max_depth=4, 
        min_samples_leaf=30, 
        l2_regularization=10.0, 
        monotonic_cst=mono_cst,
        random_state=42
    )
    
    # Fit with Jacobian weighting to equal W/m^2 L1 loss
    model.fit(tr_day[CANDIDATE_M_FEATURES], y_rkt_train, sample_weight=denom_train)
    
    denom_odd = df_odd["clearsky_ghi_terrain_adjusted"].values + eps_kt
    rkt_hat_odd = model.predict(df_odd[CANDIDATE_M_FEATURES])
    
    # Reconstruct physical irradiance
    y_hat = df_odd["pred_stage4_clean"].values + (rkt_hat_odd * denom_odd)
    physical_ceiling = np.maximum(df_odd["clearsky_ghi"].values * 1.25, df_odd["pred_stage4_clean"].values)
    y_hat = np.clip(y_hat, 0.0, physical_ceiling)
    return np.where(df_odd["causal_day_mask"].values, y_hat, 0.0)

def compute_metrics_and_bootstrap(df_odd: pd.DataFrame, y_cand: np.ndarray, y_base: np.ndarray, n_boot: int = 2000) -> Dict[str, float]:
    day_mask = df_odd["is_daytime"].values
    he_mask = day_mask & (df_odd["solar_elevation"].values >= 30.0)

    y_t = df_odd["actual_SW_IN"].values
    err_cand = (y_cand - y_t)[day_mask]
    err_he = (y_cand - y_t)[he_mask]

    n_orig = df_odd["origin_dt"].nunique()
    y_t_3d = y_t.reshape(n_orig, 24)
    y_c_3d = y_cand.reshape(n_orig, 24)
    y_b_3d = y_base.reshape(n_orig, 24)
    d_3d = day_mask.reshape(n_orig, 24)

    cand_abs = np.sum(np.abs(y_c_3d - y_t_3d) * d_3d, axis=1)
    base_abs = np.sum(np.abs(y_b_3d - y_t_3d) * d_3d, axis=1)
    day_counts = np.sum(d_3d, axis=1)

    rng = np.random.default_rng(42)
    diffs = np.zeros(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n_orig, size=n_orig)
        diffs[b] = (np.sum(cand_abs[idx]) - np.sum(base_abs[idx])) / np.sum(day_counts[idx])

    return {
        "mae": float(np.mean(np.abs(err_cand))),
        "bias": float(np.mean(err_cand)),
        "he_mae": float(np.mean(np.abs(err_he))),
        "he_bias": float(np.mean(err_he)),
        "delta": float(np.mean(np.abs(err_cand)) - np.mean(np.abs((y_base - y_t)[day_mask]))),
        "ci_lower": float(np.percentile(diffs, 2.5)),
        "ci_upper": float(np.percentile(diffs, 97.5)),
        "pass": bool(np.percentile(diffs, 97.5) < 0.0)
    }

def main():
    df_raw, p = discover_and_load_2024_data()
    print(f"[PROVENANCE] Loaded {p.name}")
    
    df = engineer_candidate_m_features(df_raw)
    df_even = df[df["is_even_origin"]].reset_index(drop=True)
    df_odd = df[~df["is_even_origin"]].reset_index(drop=True)

    pred_k = run_candidate_k_reproduction(df_even, df_odd)
    res_k = compute_metrics_and_bootstrap(df_odd, pred_k, pred_k)

    pred_m = run_candidate_m_monotonic(df_even, df_odd)
    res_m = compute_metrics_and_bootstrap(df_odd, pred_m, pred_k)

    print("=" * 105)
    print(f"{'Candidate Architecture':<28} | {'ODD MAE':>8} | {'Bias':>7} | {'HE MAE':>8} | {'HE Bias':>8} | {'vs K (95% CI)':<22} | {'Gate'}")
    print("-" * 105)
    for name, m in [("Candidate K (Control)", res_k), ("Cand M (Monotonic Adv)", res_m)]:
        ci_str = f"{m['delta']:+.4f} [{m['ci_lower']:+.4f}, {m['ci_upper']:+.4f}]"
        gate = "PASS" if m['pass'] else ("CTRL" if "Control" in name else "HOLD")
        print(f"{name:<28} | {m['mae']:8.4f} | {m['bias']:+7.4f} | {m['he_mae']:8.4f} | {m['he_bias']:+8.4f} | {ci_str:<22} | {gate}")
    print("=" * 105)

if __name__ == "__main__":
    main()