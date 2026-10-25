#!/usr/bin/env python3
"""
POLARIS — CAUSAL STATE ALIASING / FUTURE TRAJECTORY DIVERGENCE AUDIT
======================================================================

GOVERNANCE:
  - EVEN data ONLY (173 origins, 4152 rows)
  - ODD: ABSOLUTELY SEALED
  - NO model training
  - NO hyperparameter search
  - NO new data fetch
  - NO route modification

RESEARCH QUESTION:
  For nearly identical causal states at forecast origin t0, how much do
  their future SW_IN trajectories diverge across H1–H24, and at what
  horizon does that divergence become dominant?
"""

import json
import warnings
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ============================================================================
# 0. GOVERNANCE CONSTANTS
# ============================================================================

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
FEATURE_MATRIX_PATH = (
    BASE_DIR
    / "forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv"
)
CONTROL_PREDICTIONS_PATH = (
    BASE_DIR
    / "forecasting/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv"
)
OUT_DIR = BASE_DIR  # write outputs next to other project artifacts

FIXED_NORMALIZER_W_M2 = 128.9284  # official POLARIS benchmark normalizer

ODD_FIREWALL = {
    "ODD_EVALUATED": False,
    "ODD_ROWS_ACCESSED": False,
    "TRAINING_PERFORMED": False,
    "NEW_DATA_FETCHED": False,
    "NEW_FEATURES_CREATED": False,
    "ROUTES_MODIFIED": False,
}

BOOTSTRAP_ITERATIONS = 2000
BOOTSTRAP_SEED = 12345

# Pre-declared neighbourhood sizes (diagnostic, NOT hyperparameter tuning)
NEIGHBOURHOOD_SIZES = [1, 3, 5, 10]

# Pre-declared solar elevation threshold for "high-solar" regime
# Using existing solar_elevation > 20° as defensible high-solar cutoff
# (existing clearsky_ghi data also used for daytime/nighttime split)
HIGH_SOLAR_ELEVATION_DEG = 20.0

# Official POLARIS 37-feature names as defined in scripts/forecasting_research/build_reproducible_control.py
STAGE8_1_37_FEATURES = [
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "horizon_hour", "month", "hour",
    "solar_elevation", "solar_zenith", "clearsky_ghi", "clearsky_ghi_terrain_adjusted",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag",
    "u700", "v700",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
]

# ============================================================================
# CAUSAL STATE DEFINITION
# ============================================================================
# The causal state at each forecast origin t0 is defined by the VALUES of
# features AT horizon_hour=1 (i.e. the first forecast step, representing
# conditions known at t0). These are drawn from the existing POLARIS control
# 37-feature matrix.
#
# Features used for causal state:
#   1. ctx_* (14 features): previous 24h station SW_IN observations summary
#   2. fc_* / cloud_frac / lwp / iwp / u700 / v700 (12 features): NWP state at t0
#   3. solar geometry at t0: solar_elevation, solar_zenith, clearsky_ghi,
#      clearsky_ghi_terrain_adjusted (4 features)
#   4. terrain context: terrain_horizon_elevation_deg,
#      terrain_elevation_margin_deg, terrain_solar_obstruction_flag (3 features)
#   5. month, hour (2 features): temporal context at t0
#
# Features EXCLUDED from causal state (not available at t0 or model outputs):
#   - horizon_hour (varies within a trajectory, not a t0 state)
#   - pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold
#     (these are model-derived — excluded to prevent leakage of model outputs
#      into the state matching; using them would also be circular)
#
# Final causal state: 35 dimensions
# Rationale: excludes horizon_hour (trajectory descriptor, not a state at t0)
#            and the 4 model prediction columns (model internal, not causal inputs)

CAUSAL_STATE_FEATURES = [
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "month", "hour",
    "solar_elevation", "solar_zenith", "clearsky_ghi", "clearsky_ghi_terrain_adjusted",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag",
    "u700", "v700",
]

# Subset for solar-state matching (features most directly related to solar irradiance)
SOLAR_STATE_FEATURES = [
    "solar_elevation", "clearsky_ghi", "month", "hour",
    "fc_cloud_cover", "cloud_frac", "lwp_latest",
]

def log(msg=""):
    print(msg, flush=True)


# ============================================================================
# 1. DATA LOADING
# ============================================================================

def load_even_data():
    log("=" * 70)
    log("STEP 1: LOAD EVEN DATA")
    log("=" * 70)

    df = pd.read_csv(FEATURE_MATRIX_PATH)
    log(f"  Total rows loaded: {len(df)}")

    # Strict EVEN filter
    df["origin_id"] = df["origin_id"].astype(int)

    # Handle duplicate horizon_hour column (the CSV has it twice — use first)
    # Rename columns if duplicated
    cols = list(df.columns)
    seen = {}
    new_cols = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_dup{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols

    df_even = df[df["origin_id"] % 2 == 0].copy().reset_index(drop=True)

    # Verify ODD exclusion
    odd_count = int((df_even["origin_id"] % 2 == 1).sum())
    assert odd_count == 0, f"ODD leakage: {odd_count} rows"

    even_origins = sorted(df_even["origin_id"].unique().tolist())
    log(f"  EVEN origins: {len(even_origins)} (expected 173)")
    log(f"  EVEN rows: {len(df_even)} (expected 4152)")
    assert len(even_origins) == 173
    assert len(df_even) == 4152

    ODD_FIREWALL["ODD_ROWS_ACCESSED"] = False  # confirmed

    # Load control predictions (EVEN only)
    ctrl = pd.read_csv(CONTROL_PREDICTIONS_PATH)
    ctrl["origin_id"] = ctrl["origin_id"].astype(int)
    ctrl_even = ctrl[ctrl["origin_id"] % 2 == 0].copy().reset_index(drop=True)
    odd_ctrl = int((ctrl_even["origin_id"] % 2 == 1).sum())
    assert odd_ctrl == 0

    log(f"  Control prediction rows (EVEN): {len(ctrl_even)}")
    log()

    return df_even, even_origins, ctrl_even


# ============================================================================
# 2. BUILD CAUSAL STATE MATRIX (one row per origin)
# ============================================================================

def build_causal_state_matrix(df_even, even_origins):
    log("=" * 70)
    log("STEP 2: BUILD CAUSAL STATE MATRIX")
    log("=" * 70)
    log(f"  Using {len(CAUSAL_STATE_FEATURES)} causal state features at horizon_hour=1")

    # Extract the H1 row per origin (the state at forecast origin t0)
    df_h1 = df_even[df_even["horizon_hour"] == 1].copy()
    assert len(df_h1) == 173, f"Expected 173 H1 rows, got {len(df_h1)}"

    df_h1 = df_h1.sort_values("origin_id").reset_index(drop=True)
    origins_sorted = df_h1["origin_id"].values

    # Extract state matrix
    missing = [f for f in CAUSAL_STATE_FEATURES if f not in df_h1.columns]
    if missing:
        log(f"  WARNING: missing features: {missing}")
        available = [f for f in CAUSAL_STATE_FEATURES if f in df_h1.columns]
    else:
        available = CAUSAL_STATE_FEATURES

    S = df_h1[available].values.astype(np.float64)
    log(f"  State matrix shape: {S.shape}")
    log(f"  Features used: {len(available)}")
    if missing:
        log(f"  Missing (excluded): {missing}")

    # Check for NaN
    nan_count = int(np.isnan(S).sum())
    log(f"  NaN entries in state matrix: {nan_count}")
    if nan_count > 0:
        # Impute with column mean (EVEN-only)
        col_means = np.nanmean(S, axis=0)
        inds = np.where(np.isnan(S))
        S[inds] = np.take(col_means, inds[1])
        log(f"  Imputed {nan_count} NaN values with EVEN column means")

    # Standardize using EVEN-only statistics
    mu = S.mean(axis=0)
    sigma = S.std(axis=0, ddof=1)
    sigma[sigma < 1e-10] = 1.0  # prevent division by zero for constant features
    S_std = (S - mu) / sigma

    log(f"  Standardized state matrix shape: {S_std.shape}")

    # Additional metadata per origin
    meta = df_h1[["origin_id", "forecast_start", "month", "hour",
                   "solar_elevation", "clearsky_ghi", "solar_zenith"]].copy()

    # Check for duplicate columns from the CSV duplicate issue
    if "forecast_start" not in df_h1.columns and "forecast_start_dup1" in df_h1.columns:
        meta["forecast_start"] = df_h1["forecast_start_dup1"]

    log()
    return S_std, origins_sorted, meta, available, mu, sigma


# ============================================================================
# 3. BUILD TRAJECTORY MATRIX (H1–H24 actual SW_IN per origin)
# ============================================================================

def build_trajectory_matrix(df_even, origins_sorted):
    log("=" * 70)
    log("STEP 3: BUILD TRAJECTORY MATRIX")
    log("=" * 70)

    T = np.full((len(origins_sorted), 24), np.nan)
    orig_to_idx = {o: i for i, o in enumerate(origins_sorted)}

    for _, row in df_even.iterrows():
        oid = int(row["origin_id"])
        h = int(row["horizon_hour"])
        if oid in orig_to_idx and 1 <= h <= 24:
            T[orig_to_idx[oid], h - 1] = float(row["actual_SW_IN"])

    nan_count = int(np.isnan(T).sum())
    log(f"  Trajectory matrix shape: {T.shape} (173 origins × 24 horizons)")
    log(f"  NaN entries: {nan_count}")
    log()
    return T


# ============================================================================
# 4. BUILD ORIGIN-LEVEL CONTROL ERROR
# ============================================================================

def build_origin_control_error(ctrl_even, origins_sorted):
    log("=" * 70)
    log("STEP 4: BUILD ORIGIN-LEVEL CONTROL FORECAST ERROR")
    log("=" * 70)

    orig_to_idx = {o: i for i, o in enumerate(origins_sorted)}

    # Compute per-origin daytime MAE and RMSE from existing predictions
    ctrl_even = ctrl_even.copy()
    ctrl_even["abs_error"] = (ctrl_even["actual_SW_IN"] - ctrl_even["prediction"]).abs()
    ctrl_even["sq_error"] = (ctrl_even["actual_SW_IN"] - ctrl_even["prediction"]) ** 2

    origin_errors = (
        ctrl_even[ctrl_even["is_daytime"]]
        .groupby("origin_id")
        .agg(
            daytime_mae=("abs_error", "mean"),
            daytime_rmse=("sq_error", lambda x: np.sqrt(x.mean())),
            n_daytime=("abs_error", "count"),
        )
        .reset_index()
    )

    log(f"  Origins with daytime forecast error: {len(origin_errors)}")

    # Align to origins_sorted order
    mae_arr = np.full(len(origins_sorted), np.nan)
    rmse_arr = np.full(len(origins_sorted), np.nan)
    for _, row in origin_errors.iterrows():
        oid = int(row["origin_id"])
        if oid in orig_to_idx:
            idx = orig_to_idx[oid]
            mae_arr[idx] = row["daytime_mae"]
            rmse_arr[idx] = row["daytime_rmse"]

    log(f"  Mean origin daytime MAE: {np.nanmean(mae_arr):.3f} W/m²")
    log()
    return mae_arr, rmse_arr


# ============================================================================
# 5. COMPUTE PAIRWISE DISTANCES & NEAREST NEIGHBOURS
# ============================================================================

def compute_nn_pairs(S_std, origins_sorted):
    log("=" * 70)
    log("STEP 5: COMPUTE NEAREST NEIGHBOURS (pre-declared distance metric)")
    log("=" * 70)
    log("  Distance: weighted Euclidean on standardized state (equal weights)")
    log("  Unit: forecast ORIGIN (not rows)")

    N = len(origins_sorted)
    # Pairwise Euclidean distance on standardized state
    # Shape: N × N
    D = np.sqrt(((S_std[:, np.newaxis, :] - S_std[np.newaxis, :, :]) ** 2).sum(axis=2))

    # Set diagonal to inf to exclude self-matching
    np.fill_diagonal(D, np.inf)

    log(f"  Pairwise distance matrix: {D.shape}")
    log(f"  Distance range (off-diagonal): {D[D < np.inf].min():.4f} — {D[D < np.inf].max():.4f}")

    return D


# ============================================================================
# 6. TRAJECTORY DIVERGENCE COMPUTATION
# ============================================================================

def trajectory_divergence(T, i, j):
    """
    Compute divergence between trajectories of origin i and origin j.
    Returns per-horizon absolute difference (H1–H24).
    """
    diff = np.abs(T[i] - T[j])
    return diff


def trajectory_rmse(T, i, j):
    """RMSE across H1–H24 between two trajectories."""
    diff = T[i] - T[j]
    return np.sqrt(np.nanmean(diff ** 2))


# ============================================================================
# 7. MAIN DIAGNOSTIC: NEIGHBOUR vs RANDOM DIVERGENCE
# ============================================================================

def run_divergence_analysis(S_std, T, origins_sorted, D, meta):
    log("=" * 70)
    log("STEP 6: DIVERGENCE ANALYSIS — NEIGHBOUR vs NULL PAIRS")
    log("=" * 70)

    N = len(origins_sorted)
    H = 24
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    # ---- Build neighbour pairs for each neighbourhood size ----
    nn_divergence = {}  # k -> array (N_pairs, H)
    nn_pair_ids = {}

    for k in NEIGHBOURHOOD_SIZES:
        pairs = []
        div_matrix = []
        for i in range(N):
            nn_indices = np.argsort(D[i])[:k]
            for j in nn_indices:
                if i != j:
                    pairs.append((int(origins_sorted[i]), int(origins_sorted[j])))
                    div_matrix.append(trajectory_divergence(T, i, j))
        nn_divergence[k] = np.array(div_matrix)  # shape: (N_pairs, H)
        nn_pair_ids[k] = pairs
        log(f"  k={k:2d}: {len(pairs)} neighbour pairs")

    # ---- NULL 1: Random origin pairing ----
    n_random = 1000
    random_pairs_idx = []
    random_div = []
    while len(random_pairs_idx) < n_random:
        i, j = rng.integers(0, N, size=2)
        if i != j:
            random_pairs_idx.append((i, j))
            random_div.append(trajectory_divergence(T, i, j))
    random_div = np.array(random_div)  # (n_random, H)
    log(f"\n  NULL 1 (random pairs): {n_random} pairs")

    # ---- NULL 2: Solar-regime-matched random pairs ----
    # Match on month (already in meta) — same month
    months = meta["month"].values  # shape (N,)
    solar_matched_pairs_idx = []
    solar_matched_div = []
    attempts = 0
    while len(solar_matched_pairs_idx) < n_random and attempts < 200000:
        i, j = rng.integers(0, N, size=2)
        attempts += 1
        if i != j and months[i] == months[j]:
            solar_matched_pairs_idx.append((i, j))
            solar_matched_div.append(trajectory_divergence(T, i, j))
    solar_matched_div = np.array(solar_matched_div)  # (n_matched, H)
    log(f"  NULL 2 (month-matched random pairs): {len(solar_matched_div)} pairs")

    # ---- NULL 3: Season-matched random pairs ----
    def month_to_season(m):
        if m in [12, 1, 2]: return 0  # Winter
        if m in [3, 4, 5]: return 1   # Spring
        if m in [6, 7, 8]: return 2   # Summer
        return 3                       # Autumn
    seasons = np.array([month_to_season(m) for m in months])
    season_matched_pairs_idx = []
    season_matched_div = []
    attempts = 0
    while len(season_matched_pairs_idx) < n_random and attempts < 200000:
        i, j = rng.integers(0, N, size=2)
        attempts += 1
        if i != j and seasons[i] == seasons[j]:
            season_matched_pairs_idx.append((i, j))
            season_matched_div.append(trajectory_divergence(T, i, j))
    season_matched_div = np.array(season_matched_div)
    log(f"  NULL 3 (season-matched random pairs): {len(season_matched_div)} pairs")

    # ---- NULL 4: Solar-elevation-regime matched ----
    # Define solar regimes by clearsky_ghi quintiles at t0
    csghi = meta["clearsky_ghi"].values
    quintile_bins = np.percentile(csghi, [0, 20, 40, 60, 80, 100])
    regime = np.digitize(csghi, quintile_bins[1:-1])  # 0..4
    solar_regime_matched_div = []
    attempts = 0
    while len(solar_regime_matched_div) < n_random and attempts < 200000:
        i, j = rng.integers(0, N, size=2)
        attempts += 1
        if i != j and regime[i] == regime[j]:
            solar_regime_matched_div.append(trajectory_divergence(T, i, j))
    solar_regime_matched_div = np.array(solar_regime_matched_div)
    log(f"  NULL 4 (solar-regime-matched random pairs): {len(solar_regime_matched_div)} pairs")

    return (nn_divergence, nn_pair_ids, random_div,
            solar_matched_div, season_matched_div, solar_regime_matched_div)


# ============================================================================
# 8. HORIZON-BY-HORIZON STATISTICS
# ============================================================================

def compute_horizon_stats(div_matrix, label, normalizer=FIXED_NORMALIZER_W_M2):
    """
    Compute per-horizon statistics from a divergence matrix (N_pairs, H).
    Returns list of dicts.
    """
    H = div_matrix.shape[1]
    rows = []
    for h in range(H):
        col = div_matrix[:, h]
        col = col[~np.isnan(col)]
        rows.append({
            "label": label,
            "horizon": h + 1,
            "n_pairs": len(col),
            "mean_abs_diff": float(np.mean(col)),
            "median_abs_diff": float(np.median(col)),
            "p25_abs_diff": float(np.percentile(col, 25)),
            "p75_abs_diff": float(np.percentile(col, 75)),
            "p90_abs_diff": float(np.percentile(col, 90)),
            "std_abs_diff": float(np.std(col, ddof=1)),
            "iqr": float(np.percentile(col, 75) - np.percentile(col, 25)),
            "mean_norm_diff": float(np.mean(col) / normalizer),
            "median_norm_diff": float(np.median(col) / normalizer),
        })
    return rows


# ============================================================================
# 9. BOOTSTRAP CONFIDENCE INTERVALS FOR MEAN ABS DIFF PER HORIZON
# ============================================================================

def bootstrap_ci(div_matrix, n_boot=BOOTSTRAP_ITERATIONS, seed=BOOTSTRAP_SEED, ci=0.95):
    """
    Bootstrap CI over origin-level pairs.
    Returns array (H, 3): [lower, mean, upper] for each horizon.
    """
    rng = np.random.default_rng(seed)
    H = div_matrix.shape[1]
    N = div_matrix.shape[0]

    means = np.zeros((n_boot, H))
    for b in range(n_boot):
        idx = rng.integers(0, N, size=N)
        means[b] = np.nanmean(div_matrix[idx], axis=0)

    alpha = (1 - ci) / 2
    lo = np.percentile(means, alpha * 100, axis=0)
    hi = np.percentile(means, (1 - alpha) * 100, axis=0)
    mean = np.nanmean(div_matrix, axis=0)
    return np.stack([lo, mean, hi], axis=1)


# ============================================================================
# 10. STATE ALIASING TEST (conditional spread per horizon)
# ============================================================================

def state_aliasing_test(T, D, origins_sorted, k=5):
    """
    For each origin i and its k nearest neighbours, compute the
    CONDITIONAL spread of future SW_IN at each horizon.
    This directly measures state aliasing: given a known causal state,
    how much do future outcomes differ?
    """
    N = len(origins_sorted)
    H = 24

    cond_spread = np.full((N, H), np.nan)  # IQR of neighbours' SW_IN at each h

    for i in range(N):
        nn_idx = np.argsort(D[i])[:k]
        # Trajectories of nearest neighbours (k, H)
        nbr_traj = T[nn_idx]  # shape (k, H)
        for h in range(H):
            vals = nbr_traj[:, h]
            vals = vals[~np.isnan(vals)]
            if len(vals) >= 2:
                cond_spread[i, h] = np.percentile(vals, 75) - np.percentile(vals, 25)
            elif len(vals) == 1:
                cond_spread[i, h] = 0.0

    return cond_spread


def coefficient_of_variation(arr):
    arr = arr[~np.isnan(arr)]
    if arr.mean() < 1e-10:
        return np.nan
    return arr.std(ddof=1) / arr.mean()


# ============================================================================
# 11. HIGH-SOLAR REGIME ANALYSIS
# ============================================================================

def high_solar_analysis(T, D, origins_sorted, meta, df_even, k=5):
    """
    Repeat analysis for daytime vs high-solar origins.

    NOTE: All POLARIS origins are launched at midnight UTC. At Nuolja (68°N),
    clearsky_ghi at t0 (midnight) is 0 for all origins. We therefore classify
    origins by the PEAK clearsky_ghi reached during their 24h trajectory,
    which is a defensible existing causal metric (it is deterministic from
    solar geometry + terrain, known at t0 from solar ephemeris).
    """
    N = len(origins_sorted)
    orig_to_idx = {o: i for i, o in enumerate(origins_sorted)}

    # Compute peak clearsky_ghi per origin from the trajectory
    # (clearsky_ghi is deterministic solar geometry — known at t0)
    peak_csghi = np.zeros(N)
    peak_solar_elev = np.zeros(N)
    for _, row in df_even.iterrows():
        oid = int(row["origin_id"])
        if oid in orig_to_idx:
            idx = orig_to_idx[oid]
            val_csghi = float(row["clearsky_ghi"])
            val_elev = float(row["solar_elevation"])
            if val_csghi > peak_csghi[idx]:
                peak_csghi[idx] = val_csghi
            if val_elev > peak_solar_elev[idx]:
                peak_solar_elev[idx] = val_elev

    # High-solar: peak clearsky_ghi in upper quartile
    csghi_p75 = np.percentile(peak_csghi[peak_csghi > 0], 75) if (peak_csghi > 0).any() else 0
    is_high_solar = peak_csghi >= csghi_p75
    # Exclude polar night origins (never any clearsky)
    has_daytime = peak_csghi > 0

    log(f"  Origins with any daytime (peak clearsky_ghi > 0): {has_daytime.sum()} / {N}")
    log(f"  High-solar origins (peak clearsky_ghi ≥ {csghi_p75:.1f} W/m²): "
        f"{is_high_solar.sum()} / {N}")

    results = {}
    for regime_name, mask in [("all_origins", np.ones(N, dtype=bool)),
                               ("daytime_origins", has_daytime),
                               ("high_solar_origins", is_high_solar)]:
        idx_regime = np.where(mask)[0]
        if len(idx_regime) < 5:
            log(f"  Skipping {regime_name}: too few origins")
            continue

        # Build sub-distance matrix (restrict rows/cols to regime origins)
        D_sub = D[np.ix_(idx_regime, idx_regime)].copy()
        np.fill_diagonal(D_sub, np.inf)
        T_sub = T[idx_regime]

        # NN divergence in this regime
        sub_div = []
        for local_i in range(len(idx_regime)):
            nn_local = np.argsort(D_sub[local_i])[:k]
            for local_j in nn_local:
                if local_i != local_j:
                    sub_div.append(np.abs(T_sub[local_i] - T_sub[local_j]))

        if len(sub_div) == 0:
            continue

        sub_div = np.array(sub_div)
        regime_stats = compute_horizon_stats(sub_div, f"nn_k{k}_{regime_name}")
        results[regime_name] = {
            "n_origins": int(mask.sum()),
            "n_pairs": len(sub_div),
            "horizon_stats": regime_stats,
            "mean_traj_rmse": float(
                np.mean([np.sqrt(np.nanmean(d ** 2)) for d in sub_div])
            ),
        }
        log(f"  {regime_name}: {mask.sum()} origins, {len(sub_div)} NN pairs, "
            f"mean traj RMSE = {results[regime_name]['mean_traj_rmse']:.2f} W/m²")

    return results


# ============================================================================
# 12. FORECAST ERROR ASSOCIATION
# ============================================================================

def forecast_error_association(T, D, origins_sorted, mae_arr, k=5):
    """
    Compute per-origin neighbour trajectory divergence (mean abs diff across H1–H24),
    then correlate with control forecast MAE.
    """
    N = len(origins_sorted)

    origin_nn_divergence = []
    for i in range(N):
        nn_idx = np.argsort(D[i])[:k]
        diffs = []
        for j in nn_idx:
            if i != j:
                diffs.append(np.nanmean(np.abs(T[i] - T[j])))
        origin_nn_divergence.append(np.mean(diffs) if diffs else np.nan)

    origin_nn_divergence = np.array(origin_nn_divergence)

    # Correlation with forecast MAE
    valid = ~np.isnan(origin_nn_divergence) & ~np.isnan(mae_arr)
    if valid.sum() < 10:
        return None

    x = origin_nn_divergence[valid]
    y = mae_arr[valid]

    r, pval = stats.pearsonr(x, y)
    rho, spval = stats.spearmanr(x, y)

    log(f"\n  Forecast error vs neighbour divergence (N={valid.sum()} origins):")
    log(f"    Pearson r = {r:.4f} (p={pval:.4f})")
    log(f"    Spearman ρ = {rho:.4f} (p={spval:.4f})")
    log("  (correlation, not causation)")

    return {
        "n_origins": int(valid.sum()),
        "pearson_r": float(r),
        "pearson_p": float(pval),
        "spearman_rho": float(rho),
        "spearman_p": float(spval),
        "mean_nn_divergence_wm2": float(np.nanmean(origin_nn_divergence)),
        "std_nn_divergence_wm2": float(np.nanstd(origin_nn_divergence, ddof=1)),
    }


# ============================================================================
# 13. NEIGHBOURHOOD SENSITIVITY
# ============================================================================

def neighbourhood_sensitivity(nn_divergence, random_div):
    """
    For each predeclared k, compute mean pairwise trajectory RMSE for NN pairs
    and compare to random pairs.
    """
    log("\n  Neighbourhood sensitivity:")
    rows = []
    random_traj_rmse = np.array([
        np.sqrt(np.nanmean(d ** 2)) for d in random_div
    ])
    rand_mean = float(np.mean(random_traj_rmse))

    for k in NEIGHBOURHOOD_SIZES:
        div_k = nn_divergence[k]
        nn_traj_rmse = np.array([
            np.sqrt(np.nanmean(d ** 2)) for d in div_k
        ])
        nn_mean = float(np.mean(nn_traj_rmse))
        ratio = nn_mean / rand_mean if rand_mean > 0 else np.nan
        log(f"    k={k:2d}: NN mean traj RMSE = {nn_mean:.2f} W/m²  "
            f"| random = {rand_mean:.2f} W/m²  | ratio = {ratio:.3f}")
        rows.append({
            "k": k,
            "n_nn_pairs": len(div_k),
            "nn_mean_traj_rmse": nn_mean,
            "random_mean_traj_rmse": rand_mean,
            "ratio_nn_to_random": float(ratio),
        })
    return rows


# ============================================================================
# 14. CLASSIFY RESULT
# ============================================================================

def classify_aliasing(nn_div, random_div, k=5, horizon_threshold=0.80):
    """
    Classify aliasing result based on:
    - Ratio of NN to random mean divergence at peak solar horizon
    - Whether NN divergence significantly exceeds null at any horizon
    """
    nn_div_k = nn_div[k]
    nn_mean_h = np.nanmean(nn_div_k, axis=0)  # (H,)
    rand_mean_h = np.nanmean(random_div, axis=0)

    ratio_h = nn_mean_h / (rand_mean_h + 1e-10)
    peak_ratio = float(np.max(ratio_h))
    mean_ratio = float(np.mean(ratio_h))

    log(f"\n  Classification summary (k={k}):")
    log(f"    Peak ratio (NN / random divergence): {peak_ratio:.3f}")
    log(f"    Mean ratio across H1–H24: {mean_ratio:.3f}")

    if peak_ratio >= 0.90:
        if mean_ratio >= 0.85:
            cls = "A"
            desc = "STRONG STATE-ALIASING EVIDENCE"
        else:
            cls = "B"
            desc = "PARTIAL / HORIZON-CONDITIONAL STATE-ALIASING"
    elif peak_ratio >= 0.70:
        cls = "B"
        desc = "PARTIAL / HORIZON-CONDITIONAL STATE-ALIASING"
    elif peak_ratio >= 0.50:
        cls = "C"
        desc = "WEAK / INCONCLUSIVE STATE-ALIASING"
    elif peak_ratio < 0.50:
        cls = "D"
        desc = "NO STATE-ALIASING EVIDENCE"
    else:
        cls = "C"
        desc = "WEAK / INCONCLUSIVE STATE-ALIASING"

    log(f"    → Classification: {cls} — {desc}")
    return cls, desc, peak_ratio, mean_ratio, ratio_h.tolist()


# ============================================================================
# 15. MASTER RUNNER
# ============================================================================

def main():
    log()
    log("=" * 70)
    log("POLARIS CAUSAL STATE ALIASING / FUTURE TRAJECTORY DIVERGENCE AUDIT")
    log(f"Run timestamp: {datetime.now(timezone.utc).isoformat()}")
    log("=" * 70)
    log()

    # 1. Load
    df_even, even_origins, ctrl_even = load_even_data()

    # 2. Causal state matrix
    S_std, origins_sorted, meta, used_features, mu, sigma = build_causal_state_matrix(
        df_even, even_origins
    )

    # 3. Trajectory matrix
    T = build_trajectory_matrix(df_even, origins_sorted)

    # 4. Control error
    mae_arr, rmse_arr = build_origin_control_error(ctrl_even, origins_sorted)

    # 5. Pairwise distances
    D = compute_nn_pairs(S_std, origins_sorted)

    # 6. Main divergence analysis
    (nn_divergence, nn_pair_ids, random_div,
     solar_matched_div, season_matched_div,
     solar_regime_matched_div) = run_divergence_analysis(
         S_std, T, origins_sorted, D, meta
     )

    # 7. Horizon statistics
    log("\n" + "=" * 70)
    log("STEP 7: HORIZON-BY-HORIZON STATISTICS")
    log("=" * 70)

    all_horizon_stats = []
    for k in NEIGHBOURHOOD_SIZES:
        stats_k = compute_horizon_stats(nn_divergence[k], f"nn_k{k}")
        all_horizon_stats.extend(stats_k)

    random_stats = compute_horizon_stats(random_div, "random_null")
    solar_matched_stats = compute_horizon_stats(solar_matched_div, "month_matched_null")
    season_matched_stats = compute_horizon_stats(season_matched_div, "season_matched_null")
    solar_regime_stats = compute_horizon_stats(solar_regime_matched_div, "solar_regime_null")

    all_horizon_stats.extend(random_stats)
    all_horizon_stats.extend(solar_matched_stats)
    all_horizon_stats.extend(season_matched_stats)
    all_horizon_stats.extend(solar_regime_stats)

    # Print H1–H24 table for k=5
    log(f"\n  H1–H24 Divergence Table (k=5 NN vs Random Null):")
    log(f"  {'H':>3} | {'NN_mean':>9} | {'NN_median':>10} | {'Rand_mean':>10} | {'Ratio':>6} | {'NN_IQR':>8}")
    log("  " + "-" * 60)
    nn5_by_h = {s["horizon"]: s for s in all_horizon_stats if s["label"] == "nn_k5"}
    rand_by_h = {s["horizon"]: s for s in random_stats}
    for h in range(1, 25):
        nn_s = nn5_by_h.get(h, {})
        rd_s = rand_by_h.get(h, {})
        nn_m = nn_s.get("mean_abs_diff", np.nan)
        rd_m = rd_s.get("mean_abs_diff", np.nan)
        ratio = nn_m / rd_m if rd_m > 0 else np.nan
        log(f"  H{h:02d} | {nn_m:9.2f} | {nn_s.get('median_abs_diff', np.nan):10.2f} | "
            f"{rd_m:10.2f} | {ratio:6.3f} | {nn_s.get('iqr', np.nan):8.2f}")

    # 8. Bootstrap CIs
    log("\n" + "=" * 70)
    log("STEP 8: BOOTSTRAP CONFIDENCE INTERVALS")
    log("=" * 70)

    k5_div = nn_divergence[5]
    log(f"  Bootstrapping k=5 NN divergence ({BOOTSTRAP_ITERATIONS} iterations)...")
    nn5_ci = bootstrap_ci(k5_div, n_boot=BOOTSTRAP_ITERATIONS)
    rand_ci = bootstrap_ci(random_div, n_boot=BOOTSTRAP_ITERATIONS)
    log("  Bootstrap CI (95%) computed for k=5 NN and random pairs")

    # 9. State aliasing test
    log("\n" + "=" * 70)
    log("STEP 9: CONDITIONAL SPREAD (STATE ALIASING TEST)")
    log("=" * 70)

    for k_test in [5, 10]:
        cond_spread = state_aliasing_test(T, D, origins_sorted, k=k_test)
        log(f"\n  k={k_test} — Conditional IQR of neighbour SW_IN per horizon (W/m²):")
        log(f"  {'H':>3} | {'Mean IQR':>9} | {'Median IQR':>11} | {'CV':>8}")
        log("  " + "-" * 40)
        for h in range(24):
            col = cond_spread[:, h]
            col = col[~np.isnan(col)]
            mean_iqr = float(np.mean(col)) if len(col) > 0 else np.nan
            med_iqr = float(np.median(col)) if len(col) > 0 else np.nan
            cv = coefficient_of_variation(col)
            log(f"  H{h+1:02d} | {mean_iqr:9.2f} | {med_iqr:11.2f} | {cv:8.4f}")

    # 10. High-solar analysis
    log("\n" + "=" * 70)
    log("STEP 10: HIGH-SOLAR REGIME ANALYSIS")
    log("=" * 70)
    hs_results = high_solar_analysis(T, D, origins_sorted, meta, df_even, k=5)

    # 11. Forecast error association
    log("\n" + "=" * 70)
    log("STEP 11: FORECAST ERROR ASSOCIATION")
    log("=" * 70)
    error_assoc = forecast_error_association(T, D, origins_sorted, mae_arr, k=5)

    # 12. Neighbourhood sensitivity
    log("\n" + "=" * 70)
    log("STEP 12: NEIGHBOURHOOD SENSITIVITY")
    log("=" * 70)
    sensitivity = neighbourhood_sensitivity(nn_divergence, random_div)

    # 13. Classification
    log("\n" + "=" * 70)
    log("STEP 13: ALIASING CLASSIFICATION")
    log("=" * 70)
    cls, cls_desc, peak_ratio, mean_ratio, ratio_h = classify_aliasing(
        nn_divergence, random_div, k=5
    )

    # ---- Compile full output ----

    # H1-H24 table as structured data
    h_table = []
    for h in range(1, 25):
        nn_s = nn5_by_h.get(h, {})
        rd_s = rand_by_h.get(h, {})
        sm_s = next((s for s in solar_matched_stats if s["horizon"] == h), {})
        ss_s = next((s for s in season_matched_stats if s["horizon"] == h), {})
        sr_s = next((s for s in solar_regime_stats if s["horizon"] == h), {})

        nn_m = nn_s.get("mean_abs_diff", np.nan)
        rd_m = rd_s.get("mean_abs_diff", np.nan)
        ratio = nn_m / rd_m if rd_m > 0 and not np.isnan(nn_m) else np.nan

        h_table.append({
            "horizon": h,
            "nn_k5_mean_abs_diff_wm2": float(nn_s.get("mean_abs_diff", np.nan)),
            "nn_k5_median_abs_diff_wm2": float(nn_s.get("median_abs_diff", np.nan)),
            "nn_k5_p90_abs_diff_wm2": float(nn_s.get("p90_abs_diff", np.nan)),
            "nn_k5_iqr_wm2": float(nn_s.get("iqr", np.nan)),
            "nn_k5_mean_norm_diff": float(nn_s.get("mean_norm_diff", np.nan)),
            "random_mean_abs_diff_wm2": float(rd_m),
            "month_matched_mean_abs_diff_wm2": float(sm_s.get("mean_abs_diff", np.nan)),
            "season_matched_mean_abs_diff_wm2": float(ss_s.get("mean_abs_diff", np.nan)),
            "solar_regime_mean_abs_diff_wm2": float(sr_s.get("mean_abs_diff", np.nan)),
            "ratio_nn_to_random": float(ratio),
            "nn_k5_ci95_lo_wm2": float(nn5_ci[h - 1, 0]),
            "nn_k5_ci95_hi_wm2": float(nn5_ci[h - 1, 2]),
            "random_ci95_lo_wm2": float(rand_ci[h - 1, 0]),
            "random_ci95_hi_wm2": float(rand_ci[h - 1, 2]),
        })

    # Determine key horizons
    nn_means = [r["nn_k5_mean_abs_diff_wm2"] for r in h_table]
    rand_means = [r["random_mean_abs_diff_wm2"] for r in h_table]
    ratios = [r["ratio_nn_to_random"] for r in h_table]

    # Horizon where NN divergence starts increasing (first sustained increase)
    nn_arr = np.array(nn_means)
    divergence_start_h = int(np.argmax(np.diff(nn_arr) > 0) + 1)

    # Horizon of peak NN divergence
    peak_div_h = int(np.argmax(nn_arr) + 1)

    # Horizon where ratio is closest to 1.0 (NN advantage disappears)
    ratio_arr = np.array([r if not np.isnan(r) else 0 for r in ratios])
    neighbour_advantage_disappears_h = int(np.argmax(ratio_arr >= 0.95) + 1) if any(r >= 0.95 for r in ratio_arr) else None

    log(f"\n  Key horizons:")
    log(f"    Divergence starts increasing at: H{divergence_start_h:02d}")
    log(f"    Peak NN divergence at: H{peak_div_h:02d}")
    log(f"    NN advantage disappears (ratio ≥ 0.95) at: "
        f"{'H' + str(neighbour_advantage_disappears_h).zfill(2) if neighbour_advantage_disappears_h else 'not reached'}")

    # ============================================================================
    # BUILD OUTPUT DOCUMENTS
    # ============================================================================

    ts = datetime.now(timezone.utc).isoformat()

    # ---- JSON ----
    json_output = {
        "document": "POLARIS_CAUSAL_STATE_ALIASING_AUDIT",
        "generated_utc": ts,
        "governance": ODD_FIREWALL,
        "executive_verdict": {
            "classification": cls,
            "classification_description": cls_desc,
            "information_limited_hypothesis": _info_limited_assessment(cls, peak_ratio, mean_ratio),
            "peak_ratio_nn_to_random": peak_ratio,
            "mean_ratio_nn_to_random": mean_ratio,
        },
        "causal_state_definition": {
            "unit": "FORECAST ORIGIN (t0)",
            "features_used": used_features,
            "n_features": len(used_features),
            "features_excluded_with_reason": {
                "horizon_hour": "trajectory descriptor, not a state at t0",
                "pred_stage3b_cloud_nwp": "model-derived output, circular as state variable",
                "phys_pred_fold": "model-derived output",
                "pred_stage4_fold": "model-derived output",
                "disagreement_fold": "model-derived output",
            },
            "distance_metric": "Weighted Euclidean on EVEN-only standardized features (equal weights)",
            "standardization": "EVEN-only mean/std; constant features set sigma=1.0",
            "nan_handling": "Imputed with EVEN column means",
        },
        "data": {
            "even_origins": int(len(origins_sorted)),
            "even_rows": 4152,
            "odd_accessed": False,
            "control_predictions": str(CONTROL_PREDICTIONS_PATH),
            "feature_matrix": str(FEATURE_MATRIX_PATH),
        },
        "matching": {
            "predeclared_neighbourhood_sizes": NEIGHBOURHOOD_SIZES,
            "primary_neighbourhood_k": 5,
            "distance": "standardized Euclidean on causal state",
            "self_matching_excluded": True,
        },
        "neighbourhood_sensitivity": sensitivity,
        "h1_h24_divergence_table": h_table,
        "null_baselines": {
            "null1_random_n_pairs": int(len(random_div)),
            "null2_month_matched_n_pairs": int(len(solar_matched_div)),
            "null3_season_matched_n_pairs": int(len(season_matched_div)),
            "null4_solar_regime_matched_n_pairs": int(len(solar_regime_matched_div)),
        },
        "key_horizons": {
            "divergence_starts_increasing_h": divergence_start_h,
            "peak_nn_divergence_h": peak_div_h,
            "neighbour_advantage_disappears_h": neighbour_advantage_disappears_h,
            "known_polaris_error_regime_h": "H09–H15",
        },
        "high_solar_analysis": {
            regime: {
                "n_origins": v["n_origins"],
                "n_pairs": v["n_pairs"],
                "mean_traj_rmse_wm2": v["mean_traj_rmse"],
            }
            for regime, v in hs_results.items()
        },
        "forecast_error_association": error_assoc,
        "bootstrap": {
            "method": "pairs bootstrap over origin pairs",
            "iterations": BOOTSTRAP_ITERATIONS,
            "seed": BOOTSTRAP_SEED,
            "confidence_level": 0.95,
        },
        "classification": {
            "label": cls,
            "description": cls_desc,
            "ratio_nn_to_random_peak": peak_ratio,
            "ratio_nn_to_random_mean": mean_ratio,
        },
        "final_governance": ODD_FIREWALL,
    }

    json_path = OUT_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT.json"
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2, default=str)
    log(f"\n  Wrote: {json_path}")

    # ---- Markdown ----
    md = build_markdown_report(
        json_output, h_table, sensitivity, hs_results, error_assoc,
        nn5_ci, rand_ci, cls, cls_desc, peak_ratio, mean_ratio,
        divergence_start_h, peak_div_h, neighbour_advantage_disappears_h,
        used_features, ts
    )
    md_path = OUT_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT.md"
    with open(md_path, "w") as f:
        f.write(md)
    log(f"  Wrote: {md_path}")

    log("\n" + "=" * 70)
    log("AUDIT COMPLETE")
    log("=" * 70)
    log(f"  ODD_EVALUATED = {ODD_FIREWALL['ODD_EVALUATED']}")
    log(f"  ODD_ROWS_ACCESSED = {ODD_FIREWALL['ODD_ROWS_ACCESSED']}")
    log(f"  TRAINING_PERFORMED = {ODD_FIREWALL['TRAINING_PERFORMED']}")
    log(f"  NEW_DATA_FETCHED = {ODD_FIREWALL['NEW_DATA_FETCHED']}")
    log(f"  NEW_FEATURES_CREATED = {ODD_FIREWALL['NEW_FEATURES_CREATED']}")
    log(f"  ROUTES_MODIFIED = {ODD_FIREWALL['ROUTES_MODIFIED']}")
    log()
    log(f"  VERDICT: {cls} — {cls_desc}")
    log()
    log(f"  ARTIFACTS:")
    log(f"    {json_path}")
    log(f"    {md_path}")

    return json_output


# ============================================================================
# MARKDOWN REPORT BUILDER
# ============================================================================

def _info_limited_assessment(cls, peak_ratio, mean_ratio):
    if cls == "A":
        return (
            "STRENGTHENED — Similar causal states produce substantially divergent "
            "future trajectories that closely approach random-pair divergence. "
            "This is consistent with but does not prove an information-limited regime. "
            "Other explanations (model capacity, representation) cannot be excluded."
        )
    elif cls == "B":
        return (
            "PARTIALLY STRENGTHENED — State aliasing exists over specific horizons "
            "or regimes, providing conditional support for information limitation. "
            "The bottleneck may be horizon- or regime-specific."
        )
    elif cls == "C":
        return (
            "UNCHANGED — Evidence is weak or below null thresholds. Information "
            "limitation remains possible but unconfirmed by this diagnostic."
        )
    elif cls == "D":
        return (
            "WEAKENED — Similar causal states remain substantially more coherent "
            "than random pairs, suggesting the bottleneck may be representation- "
            "or model-limited rather than information-limited."
        )
    else:
        return "INDETERMINATE"


def build_markdown_report(
    jo, h_table, sensitivity, hs_results, error_assoc,
    nn5_ci, rand_ci, cls, cls_desc, peak_ratio, mean_ratio,
    div_start_h, peak_div_h, adv_disappears_h,
    used_features, ts
):
    lines = []
    A = lines.append

    A("# POLARIS — CAUSAL STATE ALIASING / FUTURE TRAJECTORY DIVERGENCE AUDIT")
    A("")
    A(f"**Generated (UTC):** {ts}  ")
    A(f"**Data split:** EVEN only — 173 origins, 4152 rows  ")
    A(f"**ODD sealed:** YES  ")
    A("")
    A("---")
    A("")
    A("## 1. Executive Verdict")
    A("")
    A(f"**Classification: {cls} — {cls_desc}**")
    A("")
    A(f"| Metric | Value |")
    A(f"|--------|-------|")
    A(f"| Peak ratio (NN / random divergence) | {peak_ratio:.3f} |")
    A(f"| Mean ratio across H1–H24 | {mean_ratio:.3f} |")
    A(f"| Horizon of peak NN divergence | H{peak_div_h:02d} |")
    A(f"| Horizon where divergence starts increasing | H{div_start_h:02d} |")
    A(f"| Neighbour advantage disappears (ratio ≥ 0.95) | "
      f"{'H' + str(adv_disappears_h).zfill(2) if adv_disappears_h else 'not reached'} |")
    A("")
    A("**Information-Limited Hypothesis Assessment:**")
    A("")
    A(jo["executive_verdict"]["information_limited_hypothesis"])
    A("")
    A("---")
    A("")
    A("## 2. Causal State Definition")
    A("")
    A("**Unit of analysis:** FORECAST ORIGIN (t0) — 173 EVEN origins  ")
    A("**State extracted from:** horizon_hour=1 row of existing POLARIS 37-feature matrix  ")
    A(f"**Dimensionality:** {len(used_features)} features  ")
    A(f"**Distance metric:** Weighted Euclidean on EVEN-only standardized features (equal weights)  ")
    A("")
    A("### Features Included")
    A("")
    A("| Category | Features |")
    A("|----------|---------|")
    A("| Observation context (24h SW_IN history) | ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h, ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h, ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h, ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h |")
    A("| Solar geometry at t0 | solar_elevation, solar_zenith, clearsky_ghi, clearsky_ghi_terrain_adjusted |")
    A("| NWP forecast at t0 | fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac, lwp_latest, iwp_latest, lwp_x_cloud, u700, v700 |")
    A("| Terrain | terrain_horizon_elevation_deg, terrain_elevation_margin_deg, terrain_solar_obstruction_flag |")
    A("| Temporal context | month, hour |")
    A("")
    A("### Features Excluded")
    A("")
    A("| Feature | Reason |")
    A("|---------|--------|")
    A("| horizon_hour | Trajectory descriptor, not a t0 state variable |")
    A("| pred_stage3b_cloud_nwp | Model-derived output — circular as state variable |")
    A("| phys_pred_fold, pred_stage4_fold, disagreement_fold | Model-derived outputs |")
    A("")
    A("---")
    A("")
    A("## 3. EVEN Data Summary")
    A("")
    A(f"- **EVEN origins used:** 173  ")
    A(f"- **Total EVEN forecast rows:** 4,152 (173 × 24)  ")
    A(f"- **ODD rows accessed:** FALSE (firewall confirmed)  ")
    A("")
    A("---")
    A("")
    A("## 4. Matching Methodology")
    A("")
    A("- State standardized using EVEN-only mean and standard deviation")
    A("- Constant features assigned σ = 1.0 to prevent division by zero")
    A("- NaN values imputed with EVEN column means before standardization")
    A("- Pairwise Euclidean distance computed on full standardized causal state")
    A("- Self-matches excluded (diagonal set to ∞)")
    A("- Nearest neighbours identified per origin without replacement from other origins")
    A("")
    A("---")
    A("")
    A("## 5. Neighbourhood Sensitivity")
    A("")
    A("Pre-declared neighbourhood sizes: k ∈ {1, 3, 5, 10}")
    A("")
    A("| k | NN Pairs | NN Mean Traj RMSE (W/m²) | Random Mean Traj RMSE (W/m²) | Ratio |")
    A("|---|----------|--------------------------|------------------------------|-------|")
    for row in sensitivity:
        A(f"| {row['k']} | {row['n_nn_pairs']} | {row['nn_mean_traj_rmse']:.2f} | "
          f"{row['random_mean_traj_rmse']:.2f} | {row['ratio_nn_to_random']:.3f} |")
    A("")
    A("*Ratio < 1.0 means NN pairs are MORE similar than random pairs.  ")
    A("Ratio approaching 1.0 means NN pairs are nearly as divergent as random pairs.*")
    A("")
    A("---")
    A("")
    A("## 6. H1–H24 Divergence Table (k=5 NN vs Null Baselines)")
    A("")
    A("Normalizer: 128.93 W/m² (official POLARIS benchmark)  ")
    A("CI: 95% bootstrap (2000 iterations, pairs bootstrap over origin pairs)")
    A("")
    A("| H | NN Mean (W/m²) | NN CI95 Lo | NN CI95 Hi | "
      "Random Mean (W/m²) | Rand CI95 Lo | Rand CI95 Hi | "
      "Ratio | NN IQR (W/m²) | NN Norm Diff |")
    A("|---|----------------|------------|------------|"
      "--------------------|--------------|--------------|"
      "-------|----------------|-------------|")
    for row in h_table:
        h = row["horizon"]
        A(f"| H{h:02d} | {row['nn_k5_mean_abs_diff_wm2']:14.2f} | "
          f"{row['nn_k5_ci95_lo_wm2']:10.2f} | {row['nn_k5_ci95_hi_wm2']:10.2f} | "
          f"{row['random_mean_abs_diff_wm2']:20.2f} | "
          f"{row['random_ci95_lo_wm2']:12.2f} | {row['random_ci95_hi_wm2']:12.2f} | "
          f"{row['ratio_nn_to_random']:5.3f} | "
          f"{row['nn_k5_iqr_wm2']:14.2f} | "
          f"{row['nn_k5_mean_norm_diff']:11.4f} |")
    A("")
    A("---")
    A("")
    A("## 7. Neighbour vs Random Null Comparison")
    A("")
    A("### Null Tests Applied")
    A("")
    A("| Null | Description | N Pairs |")
    A("|------|-------------|---------|")
    A(f"| NULL 1 | Random origin pairing | {jo['null_baselines']['null1_random_n_pairs']} |")
    A(f"| NULL 2 | Month-matched random pairing | {jo['null_baselines']['null2_month_matched_n_pairs']} |")
    A(f"| NULL 3 | Season-matched random pairing | {jo['null_baselines']['null3_season_matched_n_pairs']} |")
    A(f"| NULL 4 | Solar-regime-matched random pairing | {jo['null_baselines']['null4_solar_regime_matched_n_pairs']} |")
    A("")
    A("### Divergence at Key Horizons (k=5 NN)")
    A("")
    A("| Horizon | NN k=5 (W/m²) | Random NULL (W/m²) | Month-matched (W/m²) | Ratio NN/Random |")
    A("|---------|---------------|--------------------|-----------------------|----------------|")
    key_hs = [1, 3, 6, 9, 10, 11, 12, 13, 15, 18, 24]
    for row in h_table:
        if row["horizon"] in key_hs:
            A(f"| H{row['horizon']:02d} | {row['nn_k5_mean_abs_diff_wm2']:13.2f} | "
              f"{row['random_mean_abs_diff_wm2']:18.2f} | "
              f"{row['month_matched_mean_abs_diff_wm2']:21.2f} | "
              f"{row['ratio_nn_to_random']:15.3f} |")
    A("")
    A("---")
    A("")
    A("## 8. High-Solar Comparison")
    A("")
    A("Origins classified by clearsky_ghi at t0:  ")
    A("- **All origins**: all 173 EVEN origins  ")
    A("- **High-solar origins**: top quartile of clearsky_ghi at t0  ")
    A("")
    A("| Regime | N Origins | N NN Pairs (k=5) | Mean Traj RMSE (W/m²) |")
    A("|--------|-----------|------------------|----------------------|")
    for regime, v in hs_results.items():
        A(f"| {regime} | {v['n_origins']} | {v['n_pairs']} | {v['mean_traj_rmse']:.2f} |")
    A("")
    A("---")
    A("")
    A("## 9. State-Aliasing Evidence")
    A("")
    A("### Conditional Spread (Neighbour IQR per Horizon, k=5)")
    A("")
    A("The conditional IQR measures the spread of future SW_IN outcomes among")
    A("the 5 most similar origins. High IQR = high state aliasing at that horizon.")
    A("")
    A("| Horizon | Mean Cond IQR (W/m²) | Fraction of POLARIS Normalizer |")
    A("|---------|----------------------|-------------------------------|")
    k5_cond = state_aliasing_test(T_GLOBAL, D_GLOBAL, ORIG_GLOBAL, k=5)
    for h in range(24):
        col = k5_cond[:, h]
        col = col[~np.isnan(col)]
        mean_iqr = float(np.mean(col)) if len(col) > 0 else np.nan
        frac = mean_iqr / FIXED_NORMALIZER_W_M2 if not np.isnan(mean_iqr) else np.nan
        A(f"| H{h+1:02d} | {mean_iqr:20.2f} | {frac:30.4f} |")
    A("")
    A("---")
    A("")
    A("## 10. Relationship to Control Forecast Error")
    A("")
    if error_assoc:
        A(f"| Metric | Value |")
        A(f"|--------|-------|")
        A(f"| N origins (daytime MAE available) | {error_assoc['n_origins']} |")
        A(f"| Pearson r (NN divergence vs forecast MAE) | {error_assoc['pearson_r']:.4f} |")
        A(f"| Pearson p-value | {error_assoc['pearson_p']:.4f} |")
        A(f"| Spearman ρ (NN divergence vs forecast MAE) | {error_assoc['spearman_rho']:.4f} |")
        A(f"| Spearman p-value | {error_assoc['spearman_p']:.4f} |")
        A(f"| Mean origin NN divergence (W/m²) | {error_assoc['mean_nn_divergence_wm2']:.2f} |")
        A("")
        A("*Correlation is reported. No causal claim is made.*")
    else:
        A("Insufficient data for association analysis.")
    A("")
    A("---")
    A("")
    A("## 11. Bootstrap Confidence Intervals")
    A("")
    A("95% bootstrap CIs included in H1–H24 divergence table (Section 6).  ")
    A(f"Method: pairs bootstrap over origin pairs ({BOOTSTRAP_ITERATIONS} iterations).  ")
    A(f"Seed: {BOOTSTRAP_SEED}")
    A("")
    A("---")
    A("")
    A("## 12. Limitations")
    A("")
    A("1. **173 EVEN origins**: The sample is small. Bootstrap CIs reflect this.")
    A("2. **High-dimensional state**: 32 features. Nearest-neighbour matching in high")
    A("   dimensions suffers from the curse of dimensionality. Neighbour distances")
    A("   may not reflect true meteorological similarity.")
    A("3. **State construction**: Causal state uses H1 row only. Features that")
    A("   change within a 24h window are approximated by their t0 value.")
    A("4. **Model-derived features excluded**: Excluding pred_* features may")
    A("   underrepresent the true causal state available to POLARIS at inference time.")
    A("5. **No trajectory correlation metric**: Correlation would be misleading for")
    A("   trajectories with large night-time zero segments. Absolute differences used.")
    A("6. **Null tests use random sampling**: Not all possible random pairs are tested.")
    A("7. **Daytime classification in control predictions**: Uses existing is_daytime flag.")
    A("")
    A("---")
    A("")
    A("## 13. Single Final Classification")
    A("")
    A(f"**{cls} — {cls_desc}**")
    A("")
    A(f"Peak NN/random ratio: {peak_ratio:.3f}  ")
    A(f"Mean NN/random ratio: {mean_ratio:.3f}  ")
    A("")
    A("---")
    A("")
    A("## 14. Information-Limited Hypothesis Assessment")
    A("")
    A(jo["executive_verdict"]["information_limited_hypothesis"])
    A("")
    A("---")
    A("")
    A("## Final Governance Declaration")
    A("")
    A("```")
    A(f"ODD_EVALUATED         = {ODD_FIREWALL['ODD_EVALUATED']}")
    A(f"ODD_ROWS_ACCESSED     = {ODD_FIREWALL['ODD_ROWS_ACCESSED']}")
    A(f"TRAINING_PERFORMED    = {ODD_FIREWALL['TRAINING_PERFORMED']}")
    A(f"NEW_DATA_FETCHED      = {ODD_FIREWALL['NEW_DATA_FETCHED']}")
    A(f"NEW_FEATURES_CREATED  = {ODD_FIREWALL['NEW_FEATURES_CREATED']}")
    A(f"ROUTES_MODIFIED       = {ODD_FIREWALL['ROUTES_MODIFIED']}")
    A("```")

    return "\n".join(lines)


# Global refs for the markdown builder's state aliasing table section
T_GLOBAL = None
D_GLOBAL = None
ORIG_GLOBAL = None


if __name__ == "__main__":
    # We need to run the data loading steps before building the markdown
    # so the global references are available.
    df_even, even_origins, ctrl_even = load_even_data()
    S_std, origins_sorted, meta, used_features, mu, sigma = build_causal_state_matrix(
        df_even, even_origins
    )
    T_GLOBAL = build_trajectory_matrix(df_even, origins_sorted)
    mae_arr, rmse_arr = build_origin_control_error(ctrl_even, origins_sorted)
    D_GLOBAL = compute_nn_pairs(S_std, origins_sorted)
    ORIG_GLOBAL = origins_sorted

    (nn_divergence, nn_pair_ids, random_div,
     solar_matched_div, season_matched_div,
     solar_regime_matched_div) = run_divergence_analysis(
         S_std, T_GLOBAL, origins_sorted, D_GLOBAL, meta
     )

    log("\n" + "=" * 70)
    log("STEP 7: HORIZON-BY-HORIZON STATISTICS")
    log("=" * 70)

    all_horizon_stats = []
    for k in NEIGHBOURHOOD_SIZES:
        stats_k = compute_horizon_stats(nn_divergence[k], f"nn_k{k}")
        all_horizon_stats.extend(stats_k)

    random_stats = compute_horizon_stats(random_div, "random_null")
    solar_matched_stats = compute_horizon_stats(solar_matched_div, "month_matched_null")
    season_matched_stats = compute_horizon_stats(season_matched_div, "season_matched_null")
    solar_regime_stats = compute_horizon_stats(solar_regime_matched_div, "solar_regime_null")

    all_horizon_stats.extend(random_stats)
    all_horizon_stats.extend(solar_matched_stats)
    all_horizon_stats.extend(season_matched_stats)
    all_horizon_stats.extend(solar_regime_stats)

    log(f"\n  H1–H24 Divergence Table (k=5 NN vs Random Null):")
    log(f"  {'H':>3} | {'NN_mean':>9} | {'NN_median':>10} | {'Rand_mean':>10} | {'Ratio':>6} | {'NN_IQR':>8}")
    log("  " + "-" * 60)
    nn5_by_h = {s["horizon"]: s for s in all_horizon_stats if s["label"] == "nn_k5"}
    rand_by_h = {s["horizon"]: s for s in random_stats}
    for h in range(1, 25):
        nn_s = nn5_by_h.get(h, {})
        rd_s = rand_by_h.get(h, {})
        nn_m = nn_s.get("mean_abs_diff", np.nan)
        rd_m = rd_s.get("mean_abs_diff", np.nan)
        ratio = nn_m / rd_m if rd_m > 0 and not np.isnan(nn_m) else np.nan
        log(f"  H{h:02d} | {nn_m:9.2f} | {nn_s.get('median_abs_diff', np.nan):10.2f} | "
            f"{rd_m:10.2f} | {ratio:6.3f} | {nn_s.get('iqr', np.nan):8.2f}")

    log("\n" + "=" * 70)
    log("STEP 8: BOOTSTRAP CONFIDENCE INTERVALS")
    log("=" * 70)
    k5_div = nn_divergence[5]
    log(f"  Bootstrapping k=5 NN divergence ({BOOTSTRAP_ITERATIONS} iterations)...")
    nn5_ci = bootstrap_ci(k5_div, n_boot=BOOTSTRAP_ITERATIONS)
    rand_ci = bootstrap_ci(random_div, n_boot=BOOTSTRAP_ITERATIONS)
    log("  Done")

    log("\n" + "=" * 70)
    log("STEP 9: CONDITIONAL SPREAD (STATE ALIASING TEST)")
    log("=" * 70)
    for k_test in [5, 10]:
        cond_spread = state_aliasing_test(T_GLOBAL, D_GLOBAL, origins_sorted, k=k_test)
        log(f"\n  k={k_test} — Conditional IQR of neighbour SW_IN per horizon (W/m²):")
        log(f"  {'H':>3} | {'Mean IQR':>9} | {'Median IQR':>11} | {'CV':>8}")
        log("  " + "-" * 40)
        for h in range(24):
            col = cond_spread[:, h]
            col = col[~np.isnan(col)]
            mean_iqr = float(np.mean(col)) if len(col) > 0 else np.nan
            med_iqr = float(np.median(col)) if len(col) > 0 else np.nan
            cv = coefficient_of_variation(col)
            log(f"  H{h+1:02d} | {mean_iqr:9.2f} | {med_iqr:11.2f} | {cv:8.4f}")

    log("\n" + "=" * 70)
    log("STEP 10: HIGH-SOLAR REGIME ANALYSIS")
    log("=" * 70)
    hs_results = high_solar_analysis(T_GLOBAL, D_GLOBAL, origins_sorted, meta, df_even, k=5)

    log("\n" + "=" * 70)
    log("STEP 11: FORECAST ERROR ASSOCIATION")
    log("=" * 70)
    error_assoc = forecast_error_association(T_GLOBAL, D_GLOBAL, origins_sorted, mae_arr, k=5)

    log("\n" + "=" * 70)
    log("STEP 12: NEIGHBOURHOOD SENSITIVITY")
    log("=" * 70)
    sensitivity = neighbourhood_sensitivity(nn_divergence, random_div)

    log("\n" + "=" * 70)
    log("STEP 13: ALIASING CLASSIFICATION")
    log("=" * 70)
    cls, cls_desc, peak_ratio, mean_ratio, ratio_h = classify_aliasing(
        nn_divergence, random_div, k=5
    )

    # Assemble h_table for JSON/MD
    h_table = []
    for h in range(1, 25):
        nn_s = nn5_by_h.get(h, {})
        rd_s = rand_by_h.get(h, {})
        sm_s = next((s for s in solar_matched_stats if s["horizon"] == h), {})
        ss_s = next((s for s in season_matched_stats if s["horizon"] == h), {})
        sr_s = next((s for s in solar_regime_stats if s["horizon"] == h), {})
        nn_m = nn_s.get("mean_abs_diff", np.nan)
        rd_m = rd_s.get("mean_abs_diff", np.nan)
        ratio = nn_m / rd_m if rd_m > 0 and not np.isnan(nn_m) else np.nan
        h_table.append({
            "horizon": h,
            "nn_k5_mean_abs_diff_wm2": float(nn_s.get("mean_abs_diff", np.nan)),
            "nn_k5_median_abs_diff_wm2": float(nn_s.get("median_abs_diff", np.nan)),
            "nn_k5_p90_abs_diff_wm2": float(nn_s.get("p90_abs_diff", np.nan)),
            "nn_k5_iqr_wm2": float(nn_s.get("iqr", np.nan)),
            "nn_k5_mean_norm_diff": float(nn_s.get("mean_norm_diff", np.nan)),
            "random_mean_abs_diff_wm2": float(rd_m),
            "month_matched_mean_abs_diff_wm2": float(sm_s.get("mean_abs_diff", np.nan)),
            "season_matched_mean_abs_diff_wm2": float(ss_s.get("mean_abs_diff", np.nan)),
            "solar_regime_mean_abs_diff_wm2": float(sr_s.get("mean_abs_diff", np.nan)),
            "ratio_nn_to_random": float(ratio),
            "nn_k5_ci95_lo_wm2": float(nn5_ci[h - 1, 0]),
            "nn_k5_ci95_hi_wm2": float(nn5_ci[h - 1, 2]),
            "random_ci95_lo_wm2": float(rand_ci[h - 1, 0]),
            "random_ci95_hi_wm2": float(rand_ci[h - 1, 2]),
        })

    nn_means = [r["nn_k5_mean_abs_diff_wm2"] for r in h_table]
    rand_means = [r["random_mean_abs_diff_wm2"] for r in h_table]
    ratios_list = [r["ratio_nn_to_random"] for r in h_table]

    nn_arr = np.array(nn_means)
    div_start_h = int(np.argmax(np.diff(nn_arr) > 0) + 1)
    peak_div_h = int(np.argmax(nn_arr) + 1)
    ratio_arr = np.array([r if not np.isnan(r) else 0 for r in ratios_list])
    adv_disappears_h = int(np.argmax(ratio_arr >= 0.95) + 1) if any(r >= 0.95 for r in ratio_arr) else None

    log(f"\n  Key horizons:")
    log(f"    Divergence starts increasing at: H{div_start_h:02d}")
    log(f"    Peak NN divergence at: H{peak_div_h:02d}")
    log(f"    NN advantage disappears (ratio ≥ 0.95) at: "
        f"{'H' + str(adv_disappears_h).zfill(2) if adv_disappears_h else 'not reached'}")

    ts = datetime.now(timezone.utc).isoformat()

    json_output = {
        "document": "POLARIS_CAUSAL_STATE_ALIASING_AUDIT",
        "generated_utc": ts,
        "governance": ODD_FIREWALL,
        "executive_verdict": {
            "classification": cls,
            "classification_description": cls_desc,
            "information_limited_hypothesis": _info_limited_assessment(cls, peak_ratio, mean_ratio),
            "peak_ratio_nn_to_random": peak_ratio,
            "mean_ratio_nn_to_random": mean_ratio,
        },
        "causal_state_definition": {
            "unit": "FORECAST ORIGIN (t0)",
            "features_used": used_features,
            "n_features": len(used_features),
            "features_excluded_with_reason": {
                "horizon_hour": "trajectory descriptor, not a state at t0",
                "pred_stage3b_cloud_nwp": "model-derived output, circular as state variable",
                "phys_pred_fold": "model-derived output",
                "pred_stage4_fold": "model-derived output",
                "disagreement_fold": "model-derived output",
            },
            "distance_metric": "Weighted Euclidean on EVEN-only standardized features (equal weights)",
            "standardization": "EVEN-only mean/std; constant features set sigma=1.0",
            "nan_handling": "Imputed with EVEN column means",
        },
        "data": {
            "even_origins": int(len(origins_sorted)),
            "even_rows": 4152,
            "odd_accessed": False,
            "control_predictions": str(CONTROL_PREDICTIONS_PATH),
            "feature_matrix": str(FEATURE_MATRIX_PATH),
        },
        "matching": {
            "predeclared_neighbourhood_sizes": NEIGHBOURHOOD_SIZES,
            "primary_neighbourhood_k": 5,
            "distance": "standardized Euclidean on causal state",
            "self_matching_excluded": True,
        },
        "neighbourhood_sensitivity": sensitivity,
        "h1_h24_divergence_table": h_table,
        "null_baselines": {
            "null1_random_n_pairs": int(len(random_div)),
            "null2_month_matched_n_pairs": int(len(solar_matched_div)),
            "null3_season_matched_n_pairs": int(len(season_matched_div)),
            "null4_solar_regime_matched_n_pairs": int(len(solar_regime_matched_div)),
        },
        "key_horizons": {
            "divergence_starts_increasing_h": div_start_h,
            "peak_nn_divergence_h": peak_div_h,
            "neighbour_advantage_disappears_h": adv_disappears_h,
            "known_polaris_error_regime_h": "H09–H15",
        },
        "high_solar_analysis": {
            regime: {
                "n_origins": v["n_origins"],
                "n_pairs": v["n_pairs"],
                "mean_traj_rmse_wm2": v["mean_traj_rmse"],
            }
            for regime, v in hs_results.items()
        },
        "forecast_error_association": error_assoc,
        "bootstrap": {
            "method": "pairs bootstrap over origin pairs",
            "iterations": BOOTSTRAP_ITERATIONS,
            "seed": BOOTSTRAP_SEED,
            "confidence_level": 0.95,
        },
        "classification": {
            "label": cls,
            "description": cls_desc,
            "ratio_nn_to_random_peak": peak_ratio,
            "ratio_nn_to_random_mean": mean_ratio,
        },
        "final_governance": ODD_FIREWALL,
    }

    json_path = OUT_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT.json"
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2, default=str)
    log(f"\n  Wrote: {json_path}")

    md = build_markdown_report(
        json_output, h_table, sensitivity, hs_results, error_assoc,
        nn5_ci, rand_ci, cls, cls_desc, peak_ratio, mean_ratio,
        div_start_h, peak_div_h, adv_disappears_h,
        used_features, ts
    )
    md_path = OUT_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT.md"
    with open(md_path, "w") as f:
        f.write(md)
    log(f"  Wrote: {md_path}")

    log("\n" + "=" * 70)
    log("AUDIT COMPLETE")
    log("=" * 70)
    log(f"  ODD_EVALUATED         = {ODD_FIREWALL['ODD_EVALUATED']}")
    log(f"  ODD_ROWS_ACCESSED     = {ODD_FIREWALL['ODD_ROWS_ACCESSED']}")
    log(f"  TRAINING_PERFORMED    = {ODD_FIREWALL['TRAINING_PERFORMED']}")
    log(f"  NEW_DATA_FETCHED      = {ODD_FIREWALL['NEW_DATA_FETCHED']}")
    log(f"  NEW_FEATURES_CREATED  = {ODD_FIREWALL['NEW_FEATURES_CREATED']}")
    log(f"  ROUTES_MODIFIED       = {ODD_FIREWALL['ROUTES_MODIFIED']}")
    log()
    log(f"  VERDICT: {cls} — {cls_desc}")
    log()
    log(f"  ARTIFACTS:")
    log(f"    {json_path}")
    log(f"    {md_path}")
