"""
POLARIS Microgrid EMS: Candidate N6 Inference Runner & GAP19 Dispatch Interface
================================================================================
Cryptographic Verification | Frozen 36-Feature Contract | L2 Conformal Reserve Engine

GOVERNANCE STATUS: RESEARCH ONLY (Non-Production)
  - Model: Candidate N6 (Bagged Additive + Unshaded kt Specialist Ramp)
  - Governance State: winner: null (No production promotion authorized)
  - Operational Blocker: Historical availability of MEPS 18Z pressure levels
    prior to the 00:00 UTC dispatch cutoff remains unestablished.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Authoritative Artifact Configuration
# ---------------------------------------------------------------------------
# FOR-03 consolidation (2026-10-17, bounded/authorized pass): EXPECTED_SHA256
# used to be a second, independently hand-maintained literal here, separate
# from n6_solar.py's own FROZEN_MODEL_SHA256. Both now derive from the same
# canonical CANDIDATE_N_MANIFEST.json (models.candidate_n6.sha256), which
# already existed alongside the frozen artifacts, removing the two-copy
# drift risk. Resulting value is unchanged (re-verified via sha256sum in the
# companion report); this is evaluated once at import time.
CANDIDATE_N_MANIFEST_PATH = Path(__file__).resolve().parent / "CANDIDATE_N_MANIFEST.json"


def _load_frozen_model_sha256_from_manifest(
    manifest_path: Path, model_key: str = "candidate_n6"
) -> str:
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest["models"][model_key]["sha256"]


EXPECTED_SHA256 = _load_frozen_model_sha256_from_manifest(CANDIDATE_N_MANIFEST_PATH)
DEFAULT_ARTIFACT_PATH = (
    Path(__file__).resolve().parent / "candidate_n6_model.joblib"
)

# Physical Microgrid Plant & Inverter Constraints
K_PV: float = 51.0            # Power conversion factor: A_pv * eta_mod * PR [W / (W/m^2)]
P_INV_MAX_W: float = 60000.0  # Inverter saturation ceiling (60 kW)
ETA_DIS: float = 0.95         # Battery discharge efficiency
EBR_BASE_WH: float = 15000.0  # Baseline minimum Emergency Battery Reserve (15 kWh)
WINDOW_HOURS: int = 6         # Rolling forward survivability lookahead (W_t = 6 h)
SCALE_FLOOR_WH: float = 100.0 # Regularization floor for rolling window scale

# Conformal L2 Calibration Parameters (Calibrated on 2024-ODD, verified on 2025 blind)
Q_HAT_NORM: float = 1.8590    # One-sided 90% lower bound quantile score
Q90_W: float = 1.5702         # 6-hour forward cumulative shortfall multiplier on S_W

# Frozen 36-Feature Contract (Exact Order)
FEATURE_NAMES: List[str] = [
    # Datetime & Solar Geometry (5)
    "month",
    "hour",
    "solar_elevation",
    "solar_zenith",
    "clearsky_ghi",
    # Surface NWP (4)
    "fc_cloud_cover",
    "fc_temperature_2m",
    "fc_relative_humidity_2m",
    "cloud_frac",
    # Context Statistics (14)
    "ctx_std_3h",
    "ctx_std_6h",
    "ctx_std_12h",
    "ctx_std_24h",
    "ctx_abs_change_1h",
    "ctx_abs_change_3h",
    "ctx_abs_change_6h",
    "ctx_max_diff_6h",
    "ctx_mean_diff_6h",
    "ctx_slope_6h",
    "ctx_kt_std_6h",
    "ctx_last_obs",
    "ctx_mean_24h",
    "ctx_max_24h",
    # Topography & Upper Atmospheric Winds (5)
    "terrain_horizon_elevation_deg",
    "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag",
    "clearsky_ghi_terrain_adjusted",
    "u700",
    "v700",
    # Causal 18Z MEPS Microphysics (3)
    "lwp_18z_fc",
    "iwp_18z_fc",
    "lwp_x_cloud_18z",
    # Baseline Conditioning & Interactions (4)
    "elevation_x_cloud_frac",
    "pred_stage4_clean",
    "clean_attenuation",
    "elevation_x_transition_cloud",
]


class ArtifactIntegrityError(RuntimeError):
    """Raised when an artifact is missing or fails cryptographic verification."""
    pass


class InputValidationError(ValueError):
    """Raised when inference inputs violate contract, causality, or shape constraints."""
    pass


def verify_artifact_checksum(
    file_path: Path, expected_hash: str = EXPECTED_SHA256
) -> str:
    """Verifies the SHA-256 checksum of the frozen model artifact before loading."""
    if not file_path.is_file():
        raise ArtifactIntegrityError(f"Missing candidate N6 artifact: {file_path}")

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)

    computed_hash = sha256.hexdigest()
    if computed_hash != expected_hash:
        raise ArtifactIntegrityError(
            f"Cryptographic integrity mismatch for {file_path.name}!\n"
            f"  Expected: {expected_hash}\n"
            f"  Computed: {computed_hash}"
        )
    print(f"[VERIFIED] Checksum matched SHA-256: {computed_hash}")
    return computed_hash


def load_candidate_n6_bundle(
    file_path: Path = DEFAULT_ARTIFACT_PATH,
) -> Dict[str, Any]:
    """Cryptographically validates and loads the Candidate N6 model bundle."""
    verify_artifact_checksum(file_path, EXPECTED_SHA256)
    bundle = joblib.load(file_path)

    if not isinstance(bundle, dict):
        raise ArtifactIntegrityError(f"Invalid bundle format; expected dict, got {type(bundle)}")

    required_keys = [
        "additive_models",
        "kt_models",
        "features",
        "max_ramp_weight",
        "ramp_start_deg",
        "ramp_full_deg",
        "eps_kt",
    ]
    missing_keys = [k for k in required_keys if k not in bundle]
    if missing_keys:
        raise ArtifactIntegrityError(f"Candidate N6 bundle missing required keys: {missing_keys}")

    if len(bundle["additive_models"]) != 25:
        raise ArtifactIntegrityError(f"Expected 25 additive models, found {len(bundle['additive_models'])}")
    if len(bundle["kt_models"]) != 15:
        raise ArtifactIntegrityError(f"Expected 15 kt specialist models, found {len(bundle['kt_models'])}")
    if list(bundle["features"]) != FEATURE_NAMES:
        raise ArtifactIntegrityError("Candidate N6 bundle feature list does not match FEATURE_NAMES contract")

    print("[OK] Candidate N6 40-member model bundle verified and loaded.")
    return bundle


def validate_input_features(features_df: pd.DataFrame) -> None:
    """Validates input feature schema, horizon alignment, and causal integrity."""
    if not isinstance(features_df, pd.DataFrame):
        raise InputValidationError(f"features_df must be a pandas DataFrame, got {type(features_df)}")

    if len(features_df) != 24:
        raise InputValidationError(f"Payload requires exactly 24 hourly rows (horizons 1..24), got {len(features_df)}")

    missing = [f for f in FEATURE_NAMES if f not in features_df.columns]
    if missing:
        raise InputValidationError(f"Input DataFrame is missing required features: {missing}")

    # Check for infinite values across all features
    inf_cols = {col: int(np.isinf(features_df[col]).sum()) for col in FEATURE_NAMES if np.isinf(features_df[col]).any()}
    if inf_cols:
        raise InputValidationError(f"Input DataFrame contains infinite values: {inf_cols}")

    # Core physical and astronomical features must never be NaN (HistGradientBoosting handles missing u700/v700 natively)
    critical_features = [
        "solar_elevation",
        "solar_zenith",
        "clearsky_ghi",
        "clearsky_ghi_terrain_adjusted",
        "pred_stage4_clean",
        "clean_attenuation",
        "elevation_x_cloud_frac",
        "elevation_x_transition_cloud",
        "cloud_frac",
    ]
    nan_cols = {col: int(features_df[col].isna().sum()) for col in critical_features if features_df[col].isna().any()}
    if nan_cols:
        raise InputValidationError(f"Input DataFrame contains NaN values in critical features: {nan_cols}")

    # Causal firewall: prevent realized target or label leakage
    forbidden = ["actual_SW_IN", "actual_ghi", "residual_target", "target", "realized_generation"]
    leaked = [col for col in forbidden if col in features_df.columns]
    if leaked:
        raise InputValidationError(f"Target leakage safeguard triggered: forbidden label columns present {leaked}")


def run_candidate_n6_inference(
    bundle: Dict[str, Any], features_df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Executes Candidate N6 40-member ensemble adhering strictly to the frozen bundle contract:
      - 25-seed additive residual models: r = actual - pred_stage4_clean
      - 15-seed kt specialist models: r_kt = (actual - pred_stage4_clean) / (cs_terrain + eps_kt)
      - Elevation-ramped shading-gated blending
    """
    validate_input_features(features_df)

    X = features_df[FEATURE_NAMES].to_numpy(dtype=np.float64)
    st4 = features_df["pred_stage4_clean"].to_numpy(dtype=np.float64)
    cs_terrain = features_df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
    cs_ghi = features_df["clearsky_ghi"].to_numpy(dtype=np.float64)
    elev = features_df["solar_elevation"].to_numpy(dtype=np.float64)
    shaded = features_df["terrain_solar_obstruction_flag"].to_numpy(dtype=np.int64)

    # 1. Additive Residual Ensemble (25 seeds)
    additive_models = bundle["additive_models"]
    preds_add = np.array([np.clip(st4 + model.predict(X), 0.0, None) for model in additive_models])
    y_additive = np.mean(preds_add, axis=0)

    # 2. Clearness Index (kt) Specialist Ensemble (15 seeds)
    kt_models = bundle["kt_models"]
    eps_kt = float(bundle["eps_kt"])
    denom = cs_terrain + eps_kt
    ceiling = np.maximum(cs_ghi * 1.25, st4)
    preds_kt = np.array([np.clip(st4 + model.predict(X) * denom, 0.0, ceiling) for model in kt_models])
    y_kt = np.mean(preds_kt, axis=0)

    # 3. Elevation-Ramped Shading-Gated Blending
    ramp_start = float(bundle["ramp_start_deg"])  # 22.0
    ramp_full = float(bundle["ramp_full_deg"])    # 32.0
    max_weight = float(bundle["max_ramp_weight"]) # 0.55
    ramp_denom = ramp_full - ramp_start           # 10.0

    alpha_he = max_weight * np.clip((elev - ramp_start) / ramp_denom, 0.0, 1.0)
    unshaded = (shaded == 0).astype(np.float64)
    w = alpha_he * unshaded
    y_blend = (1.0 - w) * y_additive + w * y_kt

    # 4. Hard Night-Zeroing & Causal Day Mask
    causal_day_mask = (elev > 0.0) & (cs_ghi > 0.0)
    y_pred = np.where(causal_day_mask, y_blend, 0.0)

    # 5. Epistemic Ensemble Spread across all 40 members
    all_members = np.vstack([preds_add, preds_kt])
    ensemble_std = np.where(causal_day_mask, np.std(all_members, axis=0), 0.0)

    return y_pred, ensemble_std


def compute_conformal_lower_and_ebr(
    y_pred: np.ndarray,
    ensemble_std: np.ndarray,
    features_df: pd.DataFrame,
    q_norm: float = Q_HAT_NORM,
    q_w: float = Q90_W,
) -> Tuple[np.ndarray, List[float]]:
    """
    Computes split-conformal 90% lower irradiance bound and forward rolling EBR trajectory.
    """
    cs_terrain = features_df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
    cs_ghi = features_df["clearsky_ghi"].to_numpy(dtype=np.float64)
    elev = features_df["solar_elevation"].to_numpy(dtype=np.float64)
    causal_day_mask = (elev > 0.0) & (cs_ghi > 0.0)

    # Heteroscedastic scale s(t) in W/m^2 (conformal non-conformity scale)
    scale_s = np.where(causal_day_mask, ensemble_std + 0.10 * cs_terrain + 5.0, 0.0)

    # 1. Split-Conformal One-Sided 90% Lower Irradiance Bound (Pointwise W/m^2)
    y_lower = np.where(causal_day_mask, np.maximum(0.0, y_pred - q_norm * scale_s), 0.0)

    # 2. Rolling 6-Hour Cumulative Shortfall Reserve Trajectory
    # Heteroscedastic hourly scale in Wh: S_W = (K_PV * scale_s / ETA_DIS)
    s_hourly_wh = K_PV * scale_s / ETA_DIS

    ebr_target_wh: List[float] = []
    for t in range(24):
        t_end = min(t + WINDOW_HOURS, 24)
        scale_w_t = np.sum(s_hourly_wh[t:t_end]) + SCALE_FLOOR_WH
        ebr_t = max(EBR_BASE_WH, q_w * scale_w_t)
        ebr_target_wh.append(float(ebr_t))

    return y_lower, ebr_target_wh


def generate_dispatch_payload(
    features_df: pd.DataFrame,
    bundle: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generates Candidate N6 point forecast, split-conformal lower bounds,
    and 24-hour dynamic Emergency Battery Reserve (EBR) vector for HiGHS MILP.
    """
    y_pred, ensemble_std = run_candidate_n6_inference(bundle, features_df)
    y_lower, ebr_target_wh = compute_conformal_lower_and_ebr(y_pred, ensemble_std, features_df)
    return {
        "solar_forecast_wm2": np.round(y_pred, 4).tolist(),
        "solar_conformal_lower_wm2": np.round(y_lower, 4).tolist(),
        "ebr_target_wh": np.round(ebr_target_wh, 2).tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description="POLARIS Candidate N6 Inference Runner")
    parser.add_argument("--input", type=Path, default=None, help="Path to 24-hour input CSV with 36 features")
    parser.add_argument("--output", type=Path, default=Path("candidate_n6_verified_payload.json"), help="Output JSON path")
    parser.add_argument("--model", type=Path, default=DEFAULT_ARTIFACT_PATH, help="Path to candidate_n6_model.joblib")
    args = parser.parse_args()

    print("[POLARIS EMS] Starting Candidate N6 inference pipeline...")
    bundle = load_candidate_n6_bundle(args.model)

    if args.input is None:
        print("[INFO] No --input file provided. Use --input <path_to_24h_csv> to execute operational inference.")
        print("[INFO] For automated unit verification, run test_inference_runner.py.")
        return

    print(f"[DATA] Ingesting inference features from {args.input}...")
    df_in = pd.read_csv(args.input)
    payload = generate_dispatch_payload(df_in, bundle)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[OK] Verified payload saved to {args.output}")


if __name__ == "__main__":
    main()