"""
POLARIS — Candidate N6 Solar Irradiance -> ForecastBundle Adapter
N6SolarForecastEngine

Wires the frozen Candidate N6 40-member ensemble model
(forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib)
into the standard ForecastEngine interface.

GOVERNANCE STATUS: NON-PRODUCTION / RESEARCH ONLY
- Preserves winner: null. Does not promote any model or alter production defaults.
- This is a separate, explicitly-instantiated adapter class.
- Neither system/orchestration/worker.py nor production configuration is altered.

ARCHITECTURE & DATA CONTRACT:
- 36 input features per horizon row (horizons 1..24).
- 40-member bagged ensemble:
    * 25-seed additive residual models (r = actual - pred_stage4_clean)
    * 15-seed kt specialist models (r_kt = (actual - pred_stage4_clean) / (cs_terrain + eps_kt))
    * Elevation-ramped, shading-gated blending
- Conformal uncertainty & reserve calculation:
    * Split-conformal 90% lower bound (Q_hat_norm = 1.8590)
    * 6-hour rolling Emergency Battery Reserve trajectory (ebr_target_wh >= 15,000 Wh)
- Documented archive resolution gap:
    * u700 and v700 are legitimately NaN for horizons 20-24 due to MEPS 18Z pressure
      level archive coverage (leads 0-18).
    * Horizons 1-19 must be strictly non-NaN.
- Fail-closed security:
    * Rejects missing or malformed feature matrices with ModelGovernanceError.
    * Rejects any presence of realized target labels (actual_SW_IN, residual_target, etc.).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

from system.governance.model_reproducibility import ModelGovernanceError
from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine

# Authoritative paths and checksums
REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
CAND_N_ARTIFACTS_DIR = (
    REPO_ROOT
    / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts"
)
FROZEN_MODEL_PATH = CAND_N_ARTIFACTS_DIR / "candidate_n6_model.joblib"
CANDIDATE_N_MANIFEST_PATH = CAND_N_ARTIFACTS_DIR / "CANDIDATE_N_MANIFEST.json"


def _load_frozen_model_sha256_from_manifest(
    manifest_path: Path, model_key: str = "candidate_n6"
) -> str:
    """Read the frozen N6 model's expected SHA-256 from the single canonical
    manifest (``CANDIDATE_N_MANIFEST.json``) instead of a second,
    independently hand-maintained literal in this module.

    FOR-03 consolidation (2026-10-17, bounded/authorized pass): this constant
    used to be a hard-coded string literal here, duplicated independently in
    ``polaris_inference_runner.py``'s own ``EXPECTED_SHA256``. Both now read
    the same ``models.candidate_n6.sha256`` field of the one manifest that
    was already generated alongside the frozen artifacts, removing the
    two-copy drift risk a future re-freeze would otherwise create. The
    resulting value is unchanged (independently re-verified via
    ``sha256sum`` against the on-disk artifact in the companion report) and
    this function is evaluated once at import time, so all consumers of the
    module-level ``FROZEN_MODEL_SHA256`` constant see no behavioral change.
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest["models"][model_key]["sha256"]


FROZEN_MODEL_SHA256 = _load_frozen_model_sha256_from_manifest(CANDIDATE_N_MANIFEST_PATH)
FROZEN_MODEL_ID = "CANDIDATE_N6_25ADD_15KT_SPECIALIST"

# Plant conversion parameters
DEFAULT_K_PV: float = 51.0            # W / (W/m^2)
DEFAULT_P_INV_MAX_W: float = 60000.0  # 60 kW inverter ceiling
ETA_DIS: float = 0.95                 # Battery discharge efficiency
EBR_BASE_WH: float = 15000.0          # Minimum EBR floor (15 kWh)
WINDOW_HOURS: int = 6                 # Rolling forward lookahead
SCALE_FLOOR_WH: float = 100.0         # Regularization floor for rolling scale

# L2 Split-Conformal Calibration (Calibrated on 2024-ODD)
Q_HAT_NORM: float = 1.8590            # One-sided 90% lower bound score
Q90_W: float = 1.5702                 # 6-hour forward shortfall multiplier

# Frozen 36-feature contract (Exact Order)
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

# Critical features that must NEVER contain NaN
CRITICAL_FEATURES: List[str] = [
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

# Target leakage blacklist
FORBIDDEN_COLUMNS: List[str] = [
    "actual_SW_IN",
    "actual_ghi",
    "residual_target",
    "target",
    "realized_generation",
]


class N6SolarForecastEngine(ForecastEngine):
    """
    Explicit, non-default ForecastEngine adapter for Candidate N6.
    Must be instantiated explicitly for offline simulation and evaluation.
    """

    def __init__(
        self,
        pv_config_path: Optional[Path] = None,
        base_dir: Optional[Path] = None,
        model_path: Optional[Path] = None,
    ):
        self.base_dir = Path(base_dir) if base_dir else REPO_ROOT
        self.model_path = Path(model_path) if model_path else FROZEN_MODEL_PATH
        self.bundle = self._load_and_verify_bundle()

        # Load PV plant configuration
        if pv_config_path is not None and Path(pv_config_path).exists():
            import yaml
            with open(pv_config_path, "r", encoding="utf-8") as f:
                self.pv_config = yaml.safe_load(f)
        else:
            default_yaml = self.base_dir / "system" / "config" / "solar_pv.yaml"
            if default_yaml.exists():
                import yaml
                with open(default_yaml, "r", encoding="utf-8") as f:
                    self.pv_config = yaml.safe_load(f)
            else:
                self.pv_config = {
                    "array_area_m2": 300.0,
                    "panel_efficiency": 0.20,
                    "performance_ratio": 0.85,
                    "max_inverter_power_w": DEFAULT_P_INV_MAX_W,
                }

        # Calculate effective K_PV
        area = float(self.pv_config.get("array_area_m2", 300.0))
        eff = float(self.pv_config.get("panel_efficiency", 0.20))
        pr = float(self.pv_config.get("performance_ratio", 0.85))
        self.k_pv = area * eff * pr
        self.max_inv_w = float(self.pv_config.get("max_inverter_power_w", DEFAULT_P_INV_MAX_W))

        # Baseline engine for non-solar fallback channels (wind, demand)
        baseline_cfg = pv_config_path if pv_config_path else self.base_dir / "system" / "config" / "solar_pv.yaml"
        self.baseline_engine = LocalBaselineForecastEngine(
            Path(baseline_cfg) if Path(baseline_cfg).exists() else None
        )

    def _load_and_verify_bundle(self) -> Dict[str, Any]:
        """Loads and cryptographically verifies the Candidate N6 model bundle."""
        if not self.model_path.is_file():
            raise ModelGovernanceError(
                f"Fail-closed: Candidate N6 model artifact missing at {self.model_path}"
            )

        sha256 = hashlib.sha256()
        with open(self.model_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        computed_hash = sha256.hexdigest()

        if computed_hash.lower() != FROZEN_MODEL_SHA256.lower():
            raise ModelGovernanceError(
                f"Fail-closed: Candidate N6 model SHA-256 mismatch!\n"
                f"  Expected: {FROZEN_MODEL_SHA256}\n"
                f"  Computed: {computed_hash}"
            )

        try:
            bundle = joblib.load(self.model_path)
        except Exception as e:
            raise ModelGovernanceError(
                f"Fail-closed: unable to deserialize Candidate N6 model bundle: {e}"
            )

        if not isinstance(bundle, dict):
            raise ModelGovernanceError(
                f"Fail-closed: invalid bundle format; expected dict, got {type(bundle)}"
            )

        required_keys = [
            "additive_models",
            "kt_models",
            "features",
            "max_ramp_weight",
            "ramp_start_deg",
            "ramp_full_deg",
            "eps_kt",
        ]
        missing = [k for k in required_keys if k not in bundle]
        if missing:
            raise ModelGovernanceError(
                f"Fail-closed: Candidate N6 bundle missing required keys: {missing}"
            )

        if len(bundle["additive_models"]) != 25:
            raise ModelGovernanceError(
                f"Fail-closed: expected 25 additive models, found {len(bundle['additive_models'])}"
            )
        if len(bundle["kt_models"]) != 15:
            raise ModelGovernanceError(
                f"Fail-closed: expected 15 kt specialist models, found {len(bundle['kt_models'])}"
            )
        if list(bundle["features"]) != FEATURE_NAMES:
            raise ModelGovernanceError(
                "Fail-closed: Candidate N6 bundle feature list does not match FEATURE_NAMES contract"
            )

        return bundle

    def _sw_in_to_solar_power_w(self, sw_in_w_m2: float) -> float:
        """Converts SW_IN irradiance (W/m^2) to plant electrical power output (W)."""
        raw_power = sw_in_w_m2 * self.k_pv
        return max(0.0, min(raw_power, self.max_inv_w))

    @staticmethod
    def _validate_feature_matrix(fm: Any) -> pd.DataFrame:
        """Validates input feature schema, causality, and missingness."""
        if fm is None:
            raise ModelGovernanceError(
                "Fail-closed: runtime_context['n6_feature_matrix'] not provided. "
                "This engine does not build upstream NWP features itself -- caller "
                "must supply the pre-assembled (24, 36) feature matrix."
            )

        if not isinstance(fm, pd.DataFrame):
            raise ModelGovernanceError(
                f"Fail-closed: feature matrix must be a pandas DataFrame, got {type(fm)}"
            )

        df = fm.copy()

        if len(df) != 24:
            raise ModelGovernanceError(
                f"Fail-closed: payload requires exactly 24 hourly rows (horizons 1..24), got {len(df)}"
            )

        missing_features = [f for f in FEATURE_NAMES if f not in df.columns]
        if missing_features:
            raise ModelGovernanceError(
                f"Fail-closed: feature matrix missing required columns: {missing_features}"
            )

        # Check for forbidden target/label leakage
        leaked = [col for col in FORBIDDEN_COLUMNS if col in df.columns]
        if leaked:
            raise ModelGovernanceError(
                f"Fail-closed: target leakage safeguard triggered! Forbidden columns present: {leaked}"
            )

        # Ensure correct column ordering
        df = df[FEATURE_NAMES]

        # Check for non-finite values across all features
        inf_cols = {col: int(np.isinf(df[col]).sum()) for col in FEATURE_NAMES if np.isinf(df[col]).any()}
        if inf_cols:
            raise ModelGovernanceError(
                f"Fail-closed: infinite values detected in feature matrix: {inf_cols}"
            )

        # Critical features must never contain NaN
        nan_critical = {col: int(df[col].isna().sum()) for col in CRITICAL_FEATURES if df[col].isna().any()}
        if nan_critical:
            raise ModelGovernanceError(
                f"Fail-closed: NaN detected in critical features: {nan_critical}"
            )

        # u700/v700: permitted to be NaN ONLY for horizon_hour >= 20 (rows 19..23)
        # Any NaN in rows 0..18 (horizons 1..19) indicates upstream failure.
        for col in ["u700", "v700"]:
            bad_nans = df[col].iloc[:19].isna()
            if bad_nans.any():
                bad_idx = list(bad_nans[bad_nans].index)
                raise ModelGovernanceError(
                    f"Fail-closed: unexpected NaN in '{col}' at indices {bad_idx} (horizons 1..19). "
                    f"Only horizons 20..24 (indices 19..23) are permitted to have MEPS pressure level NaNs."
                )

        return df

    def _compute_point_prediction(
        self,
        X_df: pd.DataFrame,
        st4: np.ndarray,
        cs_terrain: np.ndarray,
        cs_ghi: np.ndarray,
        elev: np.ndarray,
        shaded: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """
        N6 REMEDIATION (Section 2.7, forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md):
        Isolated, independently-testable point-prediction operation.

        Computes the blended 25-additive / 15-kt ensemble point forecast and the
        causal day mask. Pure refactor of the original inline logic in `predict()`
        (previously lines ~358-385) -- NO numerical change: identical arithmetic,
        identical ordering of operations, identical inputs/outputs. Guarded by
        `system/tests/test_n6_decomposition_parity.py`, which asserts this
        decomposed path reproduces the original entangled computation bit-for-bit
        on fixture inputs.

        Returns a dict with keys: y_pred, causal_day_mask, preds_add, preds_kt,
        y_additive, y_kt (the last two retained for diagnostics/testability).
        """
        # 1. Additive Residual Ensemble (25 seeds)
        additive_models = self.bundle["additive_models"]
        preds_add = np.array([np.clip(st4 + m.predict(X_df), 0.0, None) for m in additive_models])
        y_additive = np.mean(preds_add, axis=0)

        # 2. Clearness Index (kt) Specialist Ensemble (15 seeds)
        kt_models = self.bundle["kt_models"]
        eps_kt = float(self.bundle["eps_kt"])
        denom = cs_terrain + eps_kt
        ceiling = np.maximum(cs_ghi * 1.25, st4)
        preds_kt = np.array([np.clip(st4 + m.predict(X_df) * denom, 0.0, ceiling) for m in kt_models])
        y_kt = np.mean(preds_kt, axis=0)

        # 3. Elevation-Ramped Shading-Gated Blending
        ramp_start = float(self.bundle["ramp_start_deg"])
        ramp_full = float(self.bundle["ramp_full_deg"])
        max_weight = float(self.bundle["max_ramp_weight"])
        ramp_denom = ramp_full - ramp_start

        alpha_he = max_weight * np.clip((elev - ramp_start) / ramp_denom, 0.0, 1.0)
        unshaded = (shaded == 0).astype(np.float64)
        w = alpha_he * unshaded
        y_blend = (1.0 - w) * y_additive + w * y_kt

        # 4. Hard Night-Zeroing & Causal Day Mask
        causal_day_mask = (elev > 0.0) & (cs_ghi > 0.0)
        y_pred = np.where(causal_day_mask, y_blend, 0.0)

        return {
            "y_pred": y_pred,
            "causal_day_mask": causal_day_mask,
            "preds_add": preds_add,
            "preds_kt": preds_kt,
            "y_additive": y_additive,
            "y_kt": y_kt,
        }

    @staticmethod
    def _compute_uncertainty_bounds(
        y_pred: np.ndarray,
        preds_add: np.ndarray,
        preds_kt: np.ndarray,
        causal_day_mask: np.ndarray,
        cs_terrain: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """
        N6 REMEDIATION (Section 2.7): Isolated, independently-testable
        uncertainty / conformal-lower-bound operation. Deliberately excludes the
        EBR reserve trajectory (see `_compute_ebr_reserve`), so reserve logic can
        be tested and audited separately from the forecast point/bound logic, per
        the remediation protocol's requirement that point prediction, uncertainty,
        and EBR reserve calculation be "clearly separated, testable operations."

        Pure refactor of the original inline logic (previously lines ~387-394) --
        no numerical change.

        Returns dict with keys: ensemble_std, scale_s, y_lower, y_upper.
        """
        # 5. Epistemic Ensemble Spread across all 40 members
        all_members = np.vstack([preds_add, preds_kt])
        ensemble_std = np.where(causal_day_mask, np.std(all_members, axis=0), 0.0)

        # 6a. Conformal 90% Lower/Upper Bound
        scale_s = np.where(causal_day_mask, ensemble_std + 0.10 * cs_terrain + 5.0, 0.0)
        y_lower = np.where(causal_day_mask, np.maximum(0.0, y_pred - Q_HAT_NORM * scale_s), 0.0)
        y_upper = np.where(causal_day_mask, np.maximum(y_pred, y_pred + Q_HAT_NORM * scale_s), 0.0)

        return {
            "ensemble_std": ensemble_std,
            "scale_s": scale_s,
            "y_lower": y_lower,
            "y_upper": y_upper,
        }

    def _compute_ebr_reserve(self, scale_s: np.ndarray) -> List[float]:
        """
        N6 REMEDIATION (Section 2.7 / Section 4): Isolated, independently-testable
        EBR (Emergency Battery Reserve) reserve-trajectory operation. Deliberately
        separated from point prediction and uncertainty-bound computation so that
        reserve-policy regression tests (Section 4) can exercise this exact
        function with synthetic `scale_s` fixtures, including the known Arm A_FIX
        failure-mode shape (low-solar / high-uncertainty), without re-running the
        full N6 ensemble inference.

        Pure refactor of the original inline logic (previously lines ~396-403) --
        no numerical change; units are explicit Wh throughout (see
        `system/safety/reserve_policy_guard.py` for downstream unit/consistency
        enforcement against this output).

        Returns ebr_target_wh: List[float] of length 24, each entry >= EBR_BASE_WH.
        """
        # Rolling 6-hour forward shortfall scale in Wh
        s_hourly_wh = self.k_pv * scale_s / ETA_DIS
        ebr_target_wh: List[float] = []
        for t in range(24):
            t_end = min(t + WINDOW_HOURS, 24)
            scale_w_t = np.sum(s_hourly_wh[t:t_end]) + SCALE_FLOOR_WH
            ebr_t = max(EBR_BASE_WH, Q90_W * scale_w_t)
            ebr_target_wh.append(float(round(ebr_t, 2)))
        return ebr_target_wh

    def predict(
        self,
        station_state: StationState,
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> ForecastBundle:
        """
        Executes Candidate N6 inference, computes split-conformal 90% lower bound,
        and constructs the 24-hour ForecastBundle with EBR reserve trajectory metadata.
        """
        if not isinstance(station_state, StationState):
            raise ModelGovernanceError("Fail-closed: invalid StationState object provided.")
        if runtime_context is None:
            runtime_context = {}

        origin_ts_str = station_state.timestamp
        try:
            origin_dt = datetime.fromisoformat(origin_ts_str.replace("Z", "+00:00"))
        except Exception as e:
            raise ModelGovernanceError(
                f"Fail-closed: invalid origin timestamp '{origin_ts_str}': {e}"
            )

        fm = runtime_context.get("n6_feature_matrix")
        if fm is None:
            # Fallback alias check
            fm = runtime_context.get("feature_matrix")
        feature_df = self._validate_feature_matrix(fm)

        # Extract feature DataFrame and arrays for computation
        X_df = feature_df[FEATURE_NAMES]
        st4 = feature_df["pred_stage4_clean"].to_numpy(dtype=np.float64)
        cs_terrain = feature_df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
        cs_ghi = feature_df["clearsky_ghi"].to_numpy(dtype=np.float64)
        elev = feature_df["solar_elevation"].to_numpy(dtype=np.float64)
        shaded = feature_df["terrain_solar_obstruction_flag"].to_numpy(dtype=np.int64)

        try:
            # Step A: isolated point-prediction operation (Section 2.7)
            point_result = self._compute_point_prediction(
                X_df, st4, cs_terrain, cs_ghi, elev, shaded
            )
            y_pred = point_result["y_pred"]
            causal_day_mask = point_result["causal_day_mask"]
            preds_add = point_result["preds_add"]
            preds_kt = point_result["preds_kt"]

            # Step B: isolated uncertainty / conformal-bound operation (Section 2.7)
            unc_result = self._compute_uncertainty_bounds(
                y_pred, preds_add, preds_kt, causal_day_mask, cs_terrain
            )
            scale_s = unc_result["scale_s"]
            y_lower = unc_result["y_lower"]
            y_upper = unc_result["y_upper"]

            # Step C: isolated EBR reserve-trajectory operation (Section 2.7 / 4)
            ebr_target_wh = self._compute_ebr_reserve(scale_s)

        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Candidate N6 inference failure: {e}")

        # Check finite outputs
        if np.isnan(y_pred).any() or np.isinf(y_pred).any():
            raise ModelGovernanceError("Fail-closed: NaN or Inf in Candidate N6 prediction.")

        # Timestamps convention: horizon 1 == forecast_start + 0h
        timestamps = [
            (origin_dt + timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for h in range(1, 25)
        ]

        # Power conversions
        solar_irr_pts = [float(round(v, 4)) for v in y_pred]
        solar_irr_lower = [float(round(v, 4)) for v in y_lower]
        solar_irr_upper = [float(round(v, 4)) for v in y_upper]

        solar_gen_pts = [round(self._sw_in_to_solar_power_w(v), 2) for v in y_pred]
        solar_gen_lower = [round(self._sw_in_to_solar_power_w(v), 2) for v in y_lower]
        solar_gen_upper = [round(self._sw_in_to_solar_power_w(v), 2) for v in y_upper]

        # Ensure exact monotonicity: lower <= point <= upper
        for i in range(24):
            solar_irr_lower[i] = min(solar_irr_lower[i], solar_irr_pts[i])
            solar_irr_upper[i] = max(solar_irr_upper[i], solar_irr_pts[i])
            solar_gen_lower[i] = min(solar_gen_lower[i], solar_gen_pts[i])
            solar_gen_upper[i] = max(solar_gen_upper[i], solar_gen_pts[i])

        solar_irradiance = TimeseriesForecast(
            point=solar_irr_pts,
            lower=solar_irr_lower,
            upper=solar_irr_upper,
            unit="W/m^2",
        )
        solar_generation = TimeseriesForecast(
            point=solar_gen_pts,
            lower=solar_gen_lower,
            upper=solar_gen_upper,
            unit="W",
        )

        # Baseline fallbacks for non-solar channels
        control_bundle = runtime_context.get("control_bundle")
        if "wind_generation" in runtime_context and isinstance(
            runtime_context["wind_generation"], TimeseriesForecast
        ):
            wind_gen = runtime_context["wind_generation"]
        elif control_bundle is not None and hasattr(control_bundle, "wind_generation"):
            wind_gen = control_bundle.wind_generation
        else:
            wind_gen = self.baseline_engine.predict(station_state, runtime_context).wind_generation

        if "demand" in runtime_context and isinstance(
            runtime_context["demand"], TimeseriesForecast
        ):
            demand_fc = runtime_context["demand"]
        elif control_bundle is not None and hasattr(control_bundle, "demand"):
            demand_fc = control_bundle.demand
        else:
            demand_fc = self.baseline_engine.predict(station_state, runtime_context).demand

        if "demand_critical" in runtime_context and isinstance(
            runtime_context["demand_critical"], TimeseriesForecast
        ):
            demand_crit = runtime_context["demand_critical"]
        elif control_bundle is not None and getattr(control_bundle, "demand_critical", None) is not None:
            demand_crit = control_bundle.demand_critical
        else:
            demand_crit = None

        metadata = {
            "model_id": FROZEN_MODEL_ID,
            "model_sha256": FROZEN_MODEL_SHA256,
            "engine_class": "N6SolarForecastEngine",
            "SOLAR_FORECAST_SOURCE": FROZEN_MODEL_ID,
            "SOLAR_MODEL_SHA": FROZEN_MODEL_SHA256,
            "ebr_target_wh": ebr_target_wh,
            "q_hat_norm": Q_HAT_NORM,
            "q90_w": Q90_W,
            "k_pv": self.k_pv,
            "max_inverter_power_w": self.max_inv_w,
            "u700_v700_nan_policy": (
                "Documented MEPS 18Z archive gap: u700/v700 legitimately NaN for "
                "horizons 20-24 (indices 19-23); strictly verified non-NaN for horizons 1-19."
            ),
            "governance_status": "RESEARCH_ONLY",
            "winner": None,
            "causality_preserved": True,
            "actual_SW_IN_used_as_input": False,
            "engine_default_in_orchestration": False,
            "fallback_available": "system.forecasting.implementations.baseline.LocalBaselineForecastEngine",
        }

        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin_ts_str,
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=solar_irradiance,
            solar_generation=solar_generation,
            wind_generation=wind_gen,
            demand=demand_fc,
            demand_critical=demand_crit,
            metadata=metadata,
        )
