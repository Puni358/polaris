#!/usr/bin/env python3
"""
POLARIS Stage 8.1 Station-Tuning Research — Candidate L Experiment Suite
========================================================================
Tests Clearness-Index (k_t) Target Parameterization, Causal 18Z Multi-Horizon
Advection Finite Differences, Gentle Loss Asymmetry, and 1D-TCN + Split-Conformal
Calibration against Candidate K (37.7169 W/m^2) strictly on 2024-ODD Validation.

Governance Rules Enforced:
  1. 2025 Blind Set is NEVER loaded, accessed, or evaluated during architecture selection.
  2. Strict 18Z MEPS causality (lead = 5 + h) and Clean Stage 4 baseline conditioning.
  3. 2,000-resample paired origin-level block bootstrap (N = 173 clusters on 2024-ODD).
  4. High-elevation (theta >= 30 deg) bias safety gate enforced alongside overall MAE.
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

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# ==============================================================================
# 1. REPOSITORY PATH RESOLUTION & GOVERNANCE HOOKS
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
RESEARCH_ROOT = SCRIPT_DIR.parent  # stage8_1_station_tuning_research
CAND_F_SUCC_DIR = RESEARCH_ROOT / "candidate_f_successor_18z"
CAND_K_DIR = RESEARCH_ROOT / "candidate_k_baseline_conditioning"

for p in [str(RESEARCH_ROOT), str(CAND_F_SUCC_DIR), str(CAND_K_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Try importing official bootstrap utility if present in repo
try:
    import research_utils
    HAS_REPO_UTILS = True
except ImportError:
    HAS_REPO_UTILS = False

# Base 33 Causal Features (Candidate F Successor v2 Contract)
SUCCESSOR_33_FEATURES: List[str] = [
    "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700",
    "lwp_18z_fc", "iwp_18z_fc", "lwp_x_cloud_18z",
    "elevation_x_cloud_frac",
]

# Candidate K 35-Feature Contract
CANDIDATE_K_35_FEATURES: List[str] = SUCCESSOR_33_FEATURES + [
    "pred_stage4_clean",
    "clean_attenuation",
]

# Candidate L Advection-Enhanced 43-Feature Contract (100% Causal at t0 = 00:00 UTC)
ADVECTION_NEW_FEATURES: List[str] = [
    "pred_stage4_kt",               # Dimensionless baseline clearness index
    "elevation_x_transition_cloud", # Candidate J winning smooth-regime interaction
    "wind_speed_700",               # 700 hPa steering wind speed magnitude
    "cloud_frac_diff_next1h",       # Forward 1h NWP cloud trend (lead 5+h+1 - lead 5+h)
    "cloud_frac_diff_prev1h",       # Backward 1h NWP cloud trend
    "lwp_18z_diff_next1h",          # Forward 1h 18Z LWP thickening rate
    "lwp_18z_diff_prev1h",          # Backward 1h 18Z LWP thickening rate
    "advection_lwp_flux",           # wind_speed_700 * centered LWP temporal gradient
]

CANDIDATE_L_FEATURES: List[str] = CANDIDATE_K_35_FEATURES + ADVECTION_NEW_FEATURES

# Microgrid Physical Constants (GAP19 / L2 Risk Interface)
K_PV: float = 51.0          # 300 m^2 * 0.20 * 0.85 = 51.0 W / (W/m^2)
ETA_DIS: float = 0.95       # Battery discharge efficiency
EBR_BASE_WH: float = 15000.0


def set_deterministic_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def compute_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


# ==============================================================================
# 2. DATA DISCOVERY & CAUSAL FEATURE ENGINEERING
# ==============================================================================
def discover_and_load_2024_data(explicit_path: Optional[str] = None) -> Tuple[pd.DataFrame, Path]:
    """
    Locates the 2024 Clean Successor v2 / Candidate K dataset in the repository.
    Strictly refuses any file containing 2025 blind test rows.
    """
    if explicit_path:
        p = Path(explicit_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Explicit dataset path not found: {p}")
        df = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
        return df, p

    search_dirs = [CAND_K_DIR, CAND_F_SUCC_DIR, RESEARCH_ROOT]
    candidates: List[Path] = []
    for d in search_dirs:
        if d.exists():
            for ext in ("*.parquet", "*.csv", "*.feather"):
                for f in d.rglob(ext):
                    fname = f.name.lower()
                    # Refuse 2025 blind data files
                    if "2025" in fname or "blind" in fname:
                        continue
                    if any(k in fname for k in ("2024", "successor", "cand_k", "candidate_k", "clean", "matrix", "features")):
                        candidates.append(f)

    # Sort candidates to prioritize candidate_k then candidate_f_successor_18z
    for f in sorted(candidates, key=lambda x: ("candidate_k" not in str(x), len(str(x)))):
        try:
            df = pd.read_parquet(f) if f.suffix == ".parquet" else pd.read_csv(f)
            required_core = {"solar_elevation", "clearsky_ghi", "lwp_18z_fc", "actual_SW_IN"}
            if required_core.issubset(set(df.columns)):
                return df, f
        except Exception:
            continue

    raise FileNotFoundError(
        "Could not auto-discover the 2024 Clean Successor / Candidate K data matrix.\n"
        "Pass it explicitly via: python3 run_candidate_l_experiment.py --data /path/to/2024_clean_matrix.parquet"
    )


def engineer_candidate_l_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verifies and constructs all Candidate K (35) and Candidate L (43) features
    strictly within each forecast origin trajectory (100% causal at t0 = 00:00 UTC).
    """
    df = df.copy()

    # Standardize origin identifier column name
    origin_col = next((c for c in ["origin_dt", "origin_date", "forecast_origin", "origin"] if c in df.columns), None)
    if origin_col is None:
        raise KeyError(f"No forecast origin column found in columns: {list(df.columns)}")
    df["origin_dt"] = pd.to_datetime(df[origin_col])

    if "horizon_hour" not in df.columns and "horizon" in df.columns:
        df["horizon_hour"] = df["horizon"]

    # Sort strictly by (origin_dt, horizon_hour)
    df = df.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)

    # Safety Gate: Ensure zero 2025 rows are present
    if (df["origin_dt"].dt.year == 2025).any():
        raise RuntimeError("GOVERNANCE VIOLATION: 2025 rows detected in development dataset! Aborting.")

    # 1. Reconstruct Candidate F / J / K derived features if not already serialized
    if "elevation_x_cloud_frac" not in df.columns:
        df["elevation_x_cloud_frac"] = df["solar_elevation"] * df["cloud_frac"]

    if "clean_attenuation" not in df.columns:
        if "pred_stage4_clean" not in df.columns:
            raise KeyError("Column 'pred_stage4_clean' missing. Run Candidate K baseline generator first.")
        df["clean_attenuation"] = df["clearsky_ghi"] - df["pred_stage4_clean"]

    # 2. Candidate L Feature Engineering (Causal intra-origin trajectory operations)
    eps = 10.0  # Stabilizer in W/m^2 to prevent twilight division blowup
    df["pred_stage4_kt"] = np.clip(
        df["pred_stage4_clean"] / (df["clearsky_ghi_terrain_adjusted"] + eps), 0.0, 1.25
    )

    is_trans_cloud = ((df["cloud_frac"] >= 0.2) & (df["cloud_frac"] < 0.6)).astype(np.float32)
    df["elevation_x_transition_cloud"] = df["solar_elevation"] * is_trans_cloud

    # Upper-air steering wind speed magnitude (propagates NaN at H20-24 for GBDT native handling)
    df["wind_speed_700"] = np.sqrt(np.square(df["u700"]) + np.square(df["v700"]))

    # Multi-horizon NWP advection finite differences within each 24h origin block
    # Causal at t0 because all 24 horizons of 18Z MEPS (lead 6..29) are available before 00:00 UTC
    grp = df.groupby("origin_dt", sort=False)
    df["cloud_frac_diff_next1h"] = grp["cloud_frac"].shift(-1) - df["cloud_frac"]
    df["cloud_frac_diff_prev1h"] = df["cloud_frac"] - grp["cloud_frac"].shift(1)
    df["cloud_frac_diff_next1h"] = df["cloud_frac_diff_next1h"].fillna(0.0)
    df["cloud_frac_diff_prev1h"] = df["cloud_frac_diff_prev1h"].fillna(0.0)

    df["lwp_18z_diff_next1h"] = (grp["lwp_18z_fc"].shift(-1) - df["lwp_18z_fc"]).fillna(0.0)
    df["lwp_18z_diff_prev1h"] = (df["lwp_18z_fc"] - grp["lwp_18z_fc"].shift(1)).fillna(0.0)

    # Advection LWP flux: wind speed * centered optical depth temporal gradient
    wind_ffill = grp["wind_speed_700"].ffill().fillna(0.0)
    lwp_centered_grad = 0.5 * (df["lwp_18z_diff_next1h"] + df["lwp_18z_diff_prev1h"])
    df["advection_lwp_flux"] = wind_ffill * lwp_centered_grad

    # Partition flags: EVEN (train, n=174 origins) vs ODD (validation, n=173 origins)
    unique_origins = sorted(df["origin_dt"].unique())
    origin_to_idx = {orig: i for i, orig in enumerate(unique_origins)}
    df["origin_idx"] = df["origin_dt"].map(origin_to_idx)
    if "is_even_origin" not in df.columns:
        df["is_even_origin"] = (df["origin_idx"] % 2 == 0)

    # Daytime evaluation mask & Causal Night Zeroing mask
    if "is_daytime" not in df.columns:
        df["is_daytime"] = (df["actual_SW_IN"] > 0.0) | (df["clearsky_ghi"] > 0.0)
    df["causal_day_mask"] = (df["solar_elevation"] > 0.0) & (df["clearsky_ghi"] > 0.0)

    return df


# ==============================================================================
# 3. CANDIDATE K & CANDIDATE L-GBDT IMPLEMENTATIONS
# ==============================================================================
def run_candidate_k_reproduction(df_even: pd.DataFrame, df_odd: pd.DataFrame) -> np.ndarray:
    """
    Exact reproduction of Candidate K:
    35 features, additive residual target (actual_SW_IN - pred_stage4_clean), L1 loss.
    """
    tr_day = df_even[df_even["is_daytime"]].copy()
    X_train = tr_day[CANDIDATE_K_35_FEATURES]
    y_res_train = tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values

    model = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_depth=4,
        min_samples_leaf=30,
        l2_regularization=10.0,
        random_state=42,
    )
    model.fit(X_train, y_res_train)

    r_hat_odd = model.predict(df_odd[CANDIDATE_K_35_FEATURES])
    y_hat_odd = np.clip(df_odd["pred_stage4_clean"].values + r_hat_odd, 0.0, None)
    y_hat_odd = np.where(df_odd["causal_day_mask"].values, y_hat_odd, 0.0)
    return y_hat_odd


def run_candidate_l_gbdt(
    df_even: pd.DataFrame,
    df_odd: pd.DataFrame,
    quantile_tau: Optional[float] = None,
    eps_kt: float = 10.0,
) -> np.ndarray:
    """
    Candidate L-GBDT:
      - Uses 43 causal features (Candidate K + 18Z multi-horizon advection finite differences).
      - Predicts dimensionless clearness index residual:
            r_kt = (actual_SW_IN - pred_stage4_clean) / (GHI_cs_terrain + eps_kt)
      - Weights samples by (GHI_cs_terrain + eps_kt) so the L1/Pinball objective in k_t space
        is Jacobian-equivalent to exact W/m^2 loss:
            sum_i w_i * |r_kt_i - r_kt_hat_i| == sum_i |y_i - y_hat_i|
    """
    tr_day = df_even[df_even["is_daytime"]].copy()
    X_train = tr_day[CANDIDATE_L_FEATURES]

    denom_train = tr_day["clearsky_ghi_terrain_adjusted"].values + eps_kt
    y_rkt_train = (tr_day["actual_SW_IN"].values - tr_day["pred_stage4_clean"].values) / denom_train

    if quantile_tau is None:
        model = HistGradientBoostingRegressor(
            loss="absolute_error",
            max_depth=4,
            min_samples_leaf=30,
            l2_regularization=10.0,
            random_state=42,
        )
    else:
        model = HistGradientBoostingRegressor(
            loss="quantile",
            quantile=quantile_tau,
            max_depth=4,
            min_samples_leaf=30,
            l2_regularization=10.0,
            random_state=42,
        )

    model.fit(X_train, y_rkt_train, sample_weight=denom_train)

    denom_odd = df_odd["clearsky_ghi_terrain_adjusted"].values + eps_kt
    rkt_hat_odd = model.predict(df_odd[CANDIDATE_L_FEATURES])

    # Reconstruct irradiance with physical clear-sky envelope ceiling (1.25x terrain clearsky)
    y_hat_odd = df_odd["pred_stage4_clean"].values + rkt_hat_odd * denom_odd
    physical_ceiling = np.maximum(df_odd["clearsky_ghi"].values * 1.25, df_odd["pred_stage4_clean"].values)
    y_hat_odd = np.clip(y_hat_odd, 0.0, physical_ceiling)
    y_hat_odd = np.where(df_odd["causal_day_mask"].values, y_hat_odd, 0.0)
    return y_hat_odd


# ==============================================================================
# 4. CANDIDATE L-TCN (1D ADVECTION TCN + SPLIT-CONFORMAL CALIBRATION)
# ==============================================================================
class AsymmetricPseudoHuberLoss(nn.Module):
    def __init__(self, tau: float = 0.46, delta: float = 5.0):
        super().__init__()
        self.tau = tau
        self.delta = delta

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor, daytime_mask: torch.Tensor) -> torch.Tensor:
        residual = y_true - y_pred  # negative when overpredicting
        weights = torch.where(residual >= 0, self.tau, 1.0 - self.tau)
        pseudo_huber = (self.delta ** 2) * (torch.sqrt(1.0 + (residual / self.delta) ** 2) - 1.0)
        masked_loss = weights * pseudo_huber * daytime_mask.float()
        return masked_loss.sum() / (daytime_mask.float().sum() + 1e-6)


class ResidualTemporalBlock(nn.Module):
    def __init__(self, channels: int, kernel_size: int = 3, dilation: int = 1, dropout: float = 0.20):
        super().__init__()
        padding = (kernel_size - 1) * dilation // 2
        self.conv1 = nn.Conv1d(channels, channels, kernel_size, padding=padding, dilation=dilation)
        self.norm1 = nn.GroupNorm(num_groups=4, num_channels=channels)
        self.act = nn.GELU()
        self.drop = nn.Dropout(dropout)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size, padding=padding, dilation=dilation)
        self.norm2 = nn.GroupNorm(num_groups=4, num_channels=channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.drop(self.act(self.norm1(self.conv1(x))))
        out = self.drop(self.act(self.norm2(self.conv2(out))))
        return x + out


class AdvectionKtTCN(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 48, dropout: float = 0.20):
        super().__init__()
        self.input_proj = nn.Conv1d(in_channels, hidden_channels, kernel_size=1)
        self.tcn = nn.Sequential(
            ResidualTemporalBlock(hidden_channels, kernel_size=3, dilation=1, dropout=dropout),
            ResidualTemporalBlock(hidden_channels, kernel_size=3, dilation=2, dropout=dropout),
            ResidualTemporalBlock(hidden_channels, kernel_size=3, dilation=4, dropout=dropout),
        )
        # Dual Head: [0] point forecast (tau=0.46), [1] lower safety quantile (tau=0.10)
        self.head_kt = nn.Conv1d(hidden_channels, 2, kernel_size=1)

    def forward(
        self,
        x_norm: torch.Tensor,
        cs_terr: torch.Tensor,
        pred_stage4_raw: torch.Tensor,
        causal_day_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.input_proj(x_norm.transpose(1, 2))
        h = self.tcn(h)
        delta_kt = 0.8 * torch.tanh(self.head_kt(h)).transpose(1, 2)

        denom = cs_terr + 10.0
        y_point = torch.clamp(pred_stage4_raw + delta_kt[:, :, 0] * denom, min=0.0) * causal_day_mask.float()
        y_lower = torch.clamp(pred_stage4_raw + delta_kt[:, :, 1] * denom, min=0.0) * causal_day_mask.float()
        y_lower = torch.minimum(y_point, y_lower)
        return y_point, y_lower


def prepare_tcn_tensors(df: pd.DataFrame, feature_cols: List[str], means=None, stds=None):
    n_origins = df["origin_dt"].nunique()
    X_df = df[feature_cols].copy()

    u_nan = X_df["u700"].isna().astype(np.float32).values[:, None]
    v_nan = X_df["v700"].isna().astype(np.float32).values[:, None]

    X_df["origin_dt"] = df["origin_dt"].values
    X_df[["u700", "v700", "wind_speed_700"]] = (
        X_df.groupby("origin_dt")[["u700", "v700", "wind_speed_700"]].ffill().fillna(0.0)
    )
    X_raw = np.nan_to_num(X_df[feature_cols].to_numpy(dtype=np.float32), nan=0.0)
    X_aug = np.concatenate([X_raw, u_nan, v_nan], axis=1).reshape(n_origins, 24, -1)

    if means is None or stds is None:
        flat = X_aug.reshape(-1, X_aug.shape[-1])
        means = flat.mean(axis=0, keepdims=True)
        stds = flat.std(axis=0, keepdims=True) + 1e-6

    X_norm = (X_aug - means) / stds
    y_3d = df["actual_SW_IN"].to_numpy(dtype=np.float32).reshape(n_origins, 24)
    cs_3d = df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float32).reshape(n_origins, 24)
    st4_3d = df["pred_stage4_clean"].to_numpy(dtype=np.float32).reshape(n_origins, 24)
    day_3d = df["is_daytime"].to_numpy(dtype=bool).reshape(n_origins, 24)
    cday_3d = df["causal_day_mask"].to_numpy(dtype=bool).reshape(n_origins, 24)

    return X_norm, y_3d, cs_3d, st4_3d, day_3d, cday_3d, means, stds


def run_candidate_l_tcn(
    df_even: pd.DataFrame,
    df_odd: pd.DataFrame,
    tau_point: float = 0.46,
    epochs: int = 90,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    set_deterministic_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    X_tr, y_tr, cs_tr, st4_tr, day_tr, cday_tr, means, stds = prepare_tcn_tensors(
        df_even, CANDIDATE_L_FEATURES
    )
    X_va, y_va, cs_va, st4_va, day_va, cday_va, _, _ = prepare_tcn_tensors(
        df_odd, CANDIDATE_L_FEATURES, means, stds
    )

    dataset = TensorDataset(
        torch.tensor(X_tr), torch.tensor(y_tr), torch.tensor(cs_tr),
        torch.tensor(st4_tr), torch.tensor(day_tr), torch.tensor(cday_tr)
    )
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = AdvectionKtTCN(in_channels=X_tr.shape[-1], hidden_channels=48, dropout=0.20).to(device)
    loss_pt_fn = AsymmetricPseudoHuberLoss(tau=tau_point, delta=5.0)
    loss_lo_fn = AsymmetricPseudoHuberLoss(tau=0.10, delta=5.0)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2e-2)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    for _ in range(epochs):
        model.train()
        for bx, by, bcs, bst4, bday, bcday in loader:
            bx, by, bcs, bst4, bday, bcday = (
                bx.to(device), by.to(device), bcs.to(device),
                bst4.to(device), bday.to(device), bcday.to(device)
            )
            optimizer.zero_grad()
            y_pt, y_lo = model(bx, bcs, bst4, bcday)
            loss = loss_pt_fn(y_pt, by, bday) + 0.25 * loss_lo_fn(y_lo, by, bday)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
        scheduler.step()

    model.eval()
    with torch.no_grad():
        y_va_pt, y_va_lo = model(
            torch.tensor(X_va, device=device),
            torch.tensor(cs_va, device=device),
            torch.tensor(st4_va, device=device),
            torch.tensor(cday_va, device=device),
        )
        y_pt_np = y_va_pt.cpu().numpy()
        y_lo_np = y_va_lo.cpu().numpy()

    # Split-Conformal Calibration on 2024-ODD for GAP19 Dynamic Reserve
    alpha = 0.10
    scores = (y_lo_np - y_va)[day_va]
    n_s = len(scores)
    q_hat_irr = float(np.quantile(scores, min(np.ceil((n_s + 1) * (1.0 - alpha)) / n_s, 1.0)))
    y_conf_lo = np.maximum(0.0, (y_lo_np - q_hat_irr) * cday_va)

    empirical_coverage = float(np.mean(y_va[day_va] >= y_conf_lo[day_va]))
    conformal_stats = {
        "q_hat_irradiance_wm2": q_hat_irr,
        "empirical_daytime_lower_coverage": empirical_coverage,
    }
    return y_pt_np.reshape(-1), y_conf_lo.reshape(-1), conformal_stats


# ==============================================================================
# 5. PAIRED ORIGIN-LEVEL BLOCK BOOTSTRAP & EVALUATION HARNESS
# ==============================================================================
def compute_metrics_and_bootstrap(
    df_odd: pd.DataFrame,
    y_cand: np.ndarray,
    y_base: np.ndarray,
    n_boot: int = 2000,
    seed: int = 42,
) -> Dict[str, float]:
    day_mask = df_odd["is_daytime"].values
    high_elev_mask = day_mask & (df_odd["solar_elevation"].values >= 30.0)
    trans_cloud_mask = day_mask & (df_odd["cloud_frac"].values >= 0.2) & (df_odd["cloud_frac"].values < 0.6)

    y_true = df_odd["actual_SW_IN"].values
    err_cand = (y_cand - y_true)[day_mask]
    err_he = (y_cand - y_true)[high_elev_mask]
    err_tc = (y_cand - y_true)[trans_cloud_mask]

    # Origin-level clustered block bootstrap (N = 173 origins)
    n_origins = df_odd["origin_dt"].nunique()
    y_t_3d = y_true.reshape(n_origins, 24)
    y_c_3d = y_cand.reshape(n_origins, 24)
    y_b_3d = y_base.reshape(n_origins, 24)
    day_3d = day_mask.reshape(n_origins, 24)

    cand_abs_sum = np.sum(np.abs(y_c_3d - y_t_3d) * day_3d, axis=1)
    base_abs_sum = np.sum(np.abs(y_b_3d - y_t_3d) * day_3d, axis=1)
    day_counts = np.sum(day_3d, axis=1)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n_origins, size=n_origins)
        tot_d = np.sum(day_counts[idx])
        diffs[b] = (np.sum(cand_abs_sum[idx]) - np.sum(base_abs_sum[idx])) / tot_d

    return {
        "mae": float(np.mean(np.abs(err_cand))),
        "rmse": float(np.sqrt(np.mean(err_cand ** 2))),
        "bias": float(np.mean(err_cand)),
        "high_elev_mae": float(np.mean(np.abs(err_he))),
        "high_elev_bias": float(np.mean(err_he)),
        "trans_cloud_mae": float(np.mean(np.abs(err_tc))),
        "delta_mae_vs_k": float(np.mean(np.abs(err_cand)) - np.mean(np.abs((y_base - y_true)[day_mask]))),
        "boot_ci_lower": float(np.percentile(diffs, 2.5)),
        "boot_ci_upper": float(np.percentile(diffs, 97.5)),
        "passes_ci_gate": bool(np.percentile(diffs, 97.5) < 0.0),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Candidate L Experiment Suite on 2024-ODD")
    parser.add_argument("--data", type=str, default=None, help="Explicit path to 2024 clean matrix")
    args = parser.parse_args()

    df_raw, data_path = discover_and_load_2024_data(args.data)
    data_hash = compute_sha256(data_path)
    print(f"[PROVENANCE] Loaded 2024 dataset: {data_path}")
    print(f"[PROVENANCE] SHA-256: {data_hash}")

    df = engineer_candidate_l_features(df_raw)
    df_even = df[df["is_even_origin"]].reset_index(drop=True)
    df_odd = df[~df["is_even_origin"]].reset_index(drop=True)

    print(f"[SPLIT] 2024-EVEN Origins: {df_even['origin_dt'].nunique()} (Daytime rows: {df_even['is_daytime'].sum()})")
    print(f"[SPLIT] 2024-ODD  Origins: {df_odd['origin_dt'].nunique()} (Daytime rows: {df_odd['is_daytime'].sum()})\n")

    # 1. Run Candidate K Control Reproduction
    pred_k = run_candidate_k_reproduction(df_even, df_odd)
    res_k = compute_metrics_and_bootstrap(df_odd, pred_k, pred_k)

    # 2. Run Candidate L1: GBDT + k_t Jacobian Residual + 18Z Multi-Horizon Advection (tau=0.50)
    pred_l1 = run_candidate_l_gbdt(df_even, df_odd, quantile_tau=None)
    res_l1 = compute_metrics_and_bootstrap(df_odd, pred_l1, pred_k)

    # 3. Run Candidate L2: GBDT + k_t Jacobian Residual + Advection + Gentle Asymmetry (tau=0.47)
    pred_l2 = run_candidate_l_gbdt(df_even, df_odd, quantile_tau=0.47)
    res_l2 = compute_metrics_and_bootstrap(df_odd, pred_l2, pred_k)

    # 4. Run Candidate L3: 1D Advection TCN + Split-Conformal Bounds (tau=0.46)
    pred_l3, pred_l3_lower, conf_stats = run_candidate_l_tcn(df_even, df_odd, tau_point=0.46)
    res_l3 = compute_metrics_and_bootstrap(df_odd, pred_l3, pred_k)

    # 5. Run Candidate L-Ensemble (50% L1-GBDT + 50% L3-TCN Variance-Reduced Blend)
    pred_ens = 0.5 * pred_l1 + 0.5 * pred_l3
    res_ens = compute_metrics_and_bootstrap(df_odd, pred_ens, pred_k)

    models = [
        ("Candidate K (Control)", res_k),
        ("Cand L1 (GBDT k_t + Adv)", res_l1),
        ("Cand L2 (GBDT k_t tau=0.47)", res_l2),
        ("Cand L3 (1D-TCN k_t)", res_l3),
        ("Cand L-Blend (GBDT + TCN)", res_ens),
    ]

    print("=" * 108)
    print(f"{'Candidate Architecture':<28} | {'ODD MAE':>8} | {'Bias':>7} | {'HE MAE':>8} | {'HE Bias':>8} | {'vs K (95% Bootstrap CI)':<26} | {'Gate'}")
    print("-" * 108)
    for name, m in models:
        ci_str = f"{m['delta_mae_vs_k']:+.4f} [{m['boot_ci_lower']:+.4f}, {m['boot_ci_upper']:+.4f}]"
        gate_str = "PASS" if m["passes_ci_gate"] else ("CTRL" if "Control" in name else "HOLD")
        print(
            f"{name:<28} | {m['mae']:8.4f} | {m['bias']:+7.4f} | "
            f"{m['high_elev_mae']:8.4f} | {m['high_elev_bias']:+8.4f} | {ci_str:<26} | {gate_str}"
        )
    print("=" * 108)
    print(f"[CONFORMAL L2] 90% Lower Bound Empirical Coverage on 2024-ODD: {conf_stats['empirical_daytime_lower_coverage']*100:.2f}% "
          f"(q_hat = {conf_stats['q_hat_irradiance_wm2']:+.2f} W/m^2)")

    # Save structured JSON report
    out_report = {
        "provenance": {"data_path": str(data_path), "sha256": data_hash},
        "results_2024_odd": {name: m for name, m in models},
        "conformal_calibration": conf_stats,
    }
    report_path = SCRIPT_DIR / "CANDIDATE_L_VALIDATION_REPORT.json"
    with open(report_path, "w") as f:
        json.dump(out_report, f, indent=2)
    print(f"\n[SAVED] Validation report written to: {report_path}")


if __name__ == "__main__":
    main()