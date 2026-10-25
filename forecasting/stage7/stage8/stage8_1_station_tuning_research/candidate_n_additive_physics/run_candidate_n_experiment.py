#!/usr/bin/env python3
"""
POLARIS Stage 8.1 Station-Tuning Research — Candidate N (N1–N7) Ablation Suite
==============================================================================
Tests the pure 36-feature synthesis (Candidate K 35 features + Candidate J's
`elevation_x_transition_cloud`) combined with 25-Seed Feature-Subsampled GBDT
Bagging and the Unshaded High-Elevation k_t Specialist Ramp.

Strictly evaluated on 2024-EVEN -> 2024-ODD (2,000 paired origin bootstrap draws).
Zero 2025 blind data is loaded or touched.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

SCRIPT_DIR = Path(__file__).resolve().parent
RESEARCH_ROOT = SCRIPT_DIR.parent
CAND_K_DIR = RESEARCH_ROOT / "candidate_k_baseline_conditioning"

# Candidate K 35-Feature Contract
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

# Candidate N1: Candidate K + Candidate J's proven interaction (36 features)
CANDIDATE_N1_36_FEATURES: List[str] = CANDIDATE_K_35_FEATURES + [
    "elevation_x_transition_cloud",
]

# Candidate N2: 40 features (with W/m^2 basis for comparison with N5)
CANDIDATE_N2_40_FEATURES: List[str] = CANDIDATE_N1_36_FEATURES + [
    "clearsky_terrain_x_cloud",
    "terrain_shade_deficit_wm2",
    "shade_diffuse_recovery_wm2",
    "advection_beam_tendency_wm2",
]


def load_2024_clean_matrix() -> Tuple[pd.DataFrame, Path]:
    p = CAND_K_DIR / "candidate_k_2024_clean_matrix.parquet"
    if not p.exists():
        raise FileNotFoundError(f"Expected clean matrix not found at {p}")
    return pd.read_parquet(p), p


def engineer_candidate_n_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)

    if (df["origin_dt"].dt.year == 2025).any():
        raise RuntimeError("GOVERNANCE VIOLATION: 2025 rows detected!")

    if "causal_day_mask" not in df.columns:
        df["causal_day_mask"] = (df["solar_elevation"] > 0.0) & (df["clearsky_ghi"] > 0.0)
    if "is_daytime" not in df.columns:
        df["is_daytime"] = (df["actual_SW_IN"] > 0.0) | (df["clearsky_ghi"] > 0.0)

    # 1. Candidate J Transition Cloud Interaction
    is_trans = ((df["cloud_frac"] >= 0.2) & (df["cloud_frac"] < 0.6)).astype(np.float64)
    df["elevation_x_transition_cloud"] = df["solar_elevation"] * is_trans

    # 2. Multiplicative W/m^2 Optical & Topographic Shading Basis (for N2/N4/N5 comparison)
    df["clearsky_terrain_x_cloud"] = df["clearsky_ghi_terrain_adjusted"] * df["cloud_frac"]
    df["terrain_shade_deficit_wm2"] = np.maximum(
        0.0, df["clearsky_ghi"] - df["clearsky_ghi_terrain_adjusted"]
    )
    df["shade_diffuse_recovery_wm2"] = df["terrain_shade_deficit_wm2"] * df["cloud_frac"]

    grp = df.groupby("origin_dt", sort=False)
    cloud_next1h = grp["cloud_frac"].shift(-1).fillna(df["cloud_frac"])
    cloud_prev1h = grp["cloud_frac"].shift(1).fillna(df["cloud_frac"])
    df["advection_beam_tendency_wm2"] = (
        df["clearsky_ghi_terrain_adjusted"] * 0.5 * (cloud_next1h - cloud_prev1h)
    )

    return df


def fit_predict_single_gbdt(
    df_even: pd.DataFrame,
    df_odd: pd.DataFrame,
    features: List[str],
    seed: int = 42,
    max_features: float = 1.0,
    min_samples_leaf: int = 30,
    l2_reg: float = 10.0,
) -> np.ndarray:
    tr_day = df_even[df_even["is_daytime"]]
    y_res_tr = tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values

    model = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_depth=4,
        min_samples_leaf=min_samples_leaf,
        l2_regularization=l2_reg,
        max_features=max_features,
        random_state=seed,
    )
    model.fit(tr_day[features], y_res_tr)

    r_hat = model.predict(df_odd[features])
    y_hat = np.clip(df_odd["pred_stage4_clean"].values + r_hat, 0.0, None)
    return np.where(df_odd["causal_day_mask"].values, y_hat, 0.0)


def fit_predict_bagged_gbdt(
    df_even: pd.DataFrame,
    df_odd: pd.DataFrame,
    features: List[str],
    n_seeds: int = 25,
    max_features: float = 0.78,
    min_samples_leaf: int = 25,
    l2_reg: float = 15.0,
) -> np.ndarray:
    preds = np.zeros((n_seeds, len(df_odd)), dtype=np.float64)
    for i in range(n_seeds):
        preds[i] = fit_predict_single_gbdt(
            df_even,
            df_odd,
            features,
            seed=100 + i,
            max_features=max_features,
            min_samples_leaf=min_samples_leaf,
            l2_reg=l2_reg,
        )
    y_hat = np.mean(preds, axis=0)
    return np.where(df_odd["causal_day_mask"].values, y_hat, 0.0)


def fit_predict_high_elev_kt_specialist(
    df_even: pd.DataFrame,
    df_odd: pd.DataFrame,
    features: List[str],
    y_additive_pred: np.ndarray,
    max_ramp_weight: float = 0.55,
) -> np.ndarray:
    tr_day = df_even[df_even["is_daytime"]]
    eps_kt = 15.0
    denom_tr = tr_day["clearsky_ghi_terrain_adjusted"].values + eps_kt
    y_rkt_tr = (tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values) / denom_tr

    n_seeds = 15
    kt_preds = np.zeros((n_seeds, len(df_odd)), dtype=np.float64)
    denom_odd = df_odd["clearsky_ghi_terrain_adjusted"].values + eps_kt

    for i in range(n_seeds):
        m_kt = HistGradientBoostingRegressor(
            loss="absolute_error",
            max_depth=4,
            min_samples_leaf=30,
            l2_regularization=15.0,
            max_features=0.80,
            random_state=500 + i,
        )
        m_kt.fit(tr_day[features], y_rkt_tr, sample_weight=denom_tr)
        rkt_hat = m_kt.predict(df_odd[features])
        y_kt_i = df_odd["pred_stage4_clean"].values + rkt_hat * denom_odd
        ceiling = np.maximum(df_odd["clearsky_ghi"].values * 1.25, df_odd["pred_stage4_clean"].values)
        kt_preds[i] = np.clip(y_kt_i, 0.0, ceiling)

    y_kt_bagged = np.mean(kt_preds, axis=0)

    # Smooth ramp weight alpha(elev): 0 below 22 deg, ramps linearly to max_ramp_weight at >= 32 deg
    elev = df_odd["solar_elevation"].values
    alpha_he = max_ramp_weight * np.clip((elev - 22.0) / 10.0, 0.0, 1.0)
    unshaded = (df_odd["terrain_solar_obstruction_flag"].values == 0).astype(np.float64)
    w = alpha_he * unshaded

    y_blend = (1.0 - w) * y_additive_pred + w * y_kt_bagged
    return np.where(df_odd["causal_day_mask"].values, y_blend, 0.0)


def compute_metrics_and_bootstrap(
    df_odd: pd.DataFrame,
    y_cand: np.ndarray,
    y_base: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42,
) -> Dict[str, float]:
    day_mask = df_odd["is_daytime"].values
    he_mask = day_mask & (df_odd["solar_elevation"].values >= 30.0)
    le_mask = day_mask & (df_odd["solar_elevation"].values < 30.0)

    y_t = df_odd["actual_SW_IN"].values
    err_c = (y_cand - y_t)[day_mask]
    err_he = (y_cand - y_t)[he_mask]
    err_le = (y_cand - y_t)[le_mask]

    n_orig = df_odd["origin_dt"].nunique()
    y_t_3d = y_t.reshape(n_orig, 24)
    y_c_3d = y_cand.reshape(n_orig, 24)
    y_b_3d = y_base.reshape(n_orig, 24)
    d_3d = day_mask.reshape(n_orig, 24)

    cand_abs = np.sum(np.abs(y_c_3d - y_t_3d) * d_3d, axis=1)
    base_abs = np.sum(np.abs(y_b_3d - y_t_3d) * d_3d, axis=1)
    day_counts = np.sum(d_3d, axis=1)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n_orig, size=n_orig)
        diffs[b] = (np.sum(cand_abs[idx]) - np.sum(base_abs[idx])) / np.sum(day_counts[idx])

    return {
        "mae": float(np.mean(np.abs(err_c))),
        "bias": float(np.mean(err_c)),
        "le_mae": float(np.mean(np.abs(err_le))),
        "he_mae": float(np.mean(np.abs(err_he))),
        "he_bias": float(np.mean(err_he)),
        "delta": float(np.mean(np.abs(err_c)) - np.mean(np.abs((y_base - y_t)[day_mask]))),
        "ci_lower": float(np.percentile(diffs, 2.5)),
        "ci_upper": float(np.percentile(diffs, 97.5)),
        "pass": bool(np.percentile(diffs, 97.5) < 0.0),
    }


def main():
    df_raw, p = load_2024_clean_matrix()
    print(f"[PROVENANCE] Loaded {p.name} (rows={len(df_raw)})")

    df = engineer_candidate_n_features(df_raw)
    df_even = df[df["is_even_origin"]].reset_index(drop=True)
    df_odd = df[~df["is_even_origin"]].reset_index(drop=True)

    # 0. Candidate K Reproduction (35 features, single tree)
    pred_k = fit_predict_single_gbdt(df_even, df_odd, CANDIDATE_K_35_FEATURES, seed=42)
    res_k = compute_metrics_and_bootstrap(df_odd, pred_k, pred_k)

    # 1. Cand N1: Single Tree on 36 features (K + Cand J interaction)
    pred_n1 = fit_predict_single_gbdt(df_even, df_odd, CANDIDATE_N1_36_FEATURES, seed=42)
    res_n1 = compute_metrics_and_bootstrap(df_odd, pred_n1, pred_k)

    # 2. Cand N3: 25-Seed Bagged K (35 features)
    pred_n3 = fit_predict_bagged_gbdt(df_even, df_odd, CANDIDATE_K_35_FEATURES)
    res_n3 = compute_metrics_and_bootstrap(df_odd, pred_n3, pred_k)

    # 3. Cand N5 (Previous Best): 25-Seed Bagged N2 (40 features) + HE k_t Ramp
    pred_n4 = fit_predict_bagged_gbdt(df_even, df_odd, CANDIDATE_N2_40_FEATURES)
    pred_n5 = fit_predict_high_elev_kt_specialist(df_even, df_odd, CANDIDATE_N2_40_FEATURES, pred_n4)
    res_n5 = compute_metrics_and_bootstrap(df_odd, pred_n5, pred_k)

    # 4. Cand N6a: 25-Seed Bagged N1 (Pure 36 features, no noisy W/m^2 collinear features)
    pred_n6a = fit_predict_bagged_gbdt(df_even, df_odd, CANDIDATE_N1_36_FEATURES)
    res_n6a = compute_metrics_and_bootstrap(df_odd, pred_n6a, pred_k)

    # 5. Cand N6 (Pure Synthesis): Bagged N1 (36 features) + HE k_t Specialist Ramp (36 features)
    pred_n6 = fit_predict_high_elev_kt_specialist(df_even, df_odd, CANDIDATE_N1_36_FEATURES, pred_n6a)
    res_n6 = compute_metrics_and_bootstrap(df_odd, pred_n6, pred_k)
    res_n6_vs_n5 = compute_metrics_and_bootstrap(df_odd, pred_n6, pred_n5)

    suites = [
        ("Candidate K (Control)", res_k),
        ("Cand N1 (K + CandJ 36-feat)", res_n1),
        ("Cand N3 (Bagged K 35-feat)", res_n3),
        ("Cand N5 (Bagged 40 + HE kt)", res_n5),
        ("Cand N6a (Bagged N1 36-feat)", res_n6a),
        ("Cand N6 (Bagged 36 + HE kt)", res_n6),
    ]

    print("=" * 116)
    print(f"{'Candidate Architecture':<27} | {'ODD MAE':>8} | {'Bias':>7} | {'LE MAE':>7} | {'HE MAE':>8} | {'HE Bias':>8} | {'vs K (95% Bootstrap CI)':<26} | {'Gate'}")
    print("-" * 116)
    for name, m in suites:
        ci_str = f"{m['delta']:+.4f} [{m['ci_lower']:+.4f}, {m['ci_upper']:+.4f}]"
        gate = "PASS" if m["pass"] else ("CTRL" if "Control" in name else "HOLD")
        print(
            f"{name:<27} | {m['mae']:8.4f} | {m['bias']:+7.4f} | {m['le_mae']:7.4f} | "
            f"{m['he_mae']:8.4f} | {m['he_bias']:+8.4f} | {ci_str:<26} | {gate}"
        )
    print("=" * 116)
    print(
        f"[HEAD-TO-HEAD] Cand N6 vs Cand N5: Delta MAE = {res_n6_vs_n5['delta']:+.4f} W/m^2 "
        f"(95% CI: [{res_n6_vs_n5['ci_lower']:+.4f}, {res_n6_vs_n5['ci_upper']:+.4f}])"
    )

    out_path = SCRIPT_DIR / "CANDIDATE_N_VALIDATION_REPORT.json"
    with open(out_path, "w") as f:
        json.dump({name: m for name, m in suites}, f, indent=2)
    print(f"[SAVED] Report written to: {out_path}")


if __name__ == "__main__":
    main()
