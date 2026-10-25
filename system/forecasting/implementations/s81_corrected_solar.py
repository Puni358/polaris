"""
Stage 8.1 CORRECTED Solar Irradiance -> ForecastBundle Adapter
Stage81CorrectedForecastEngine

Wires the frozen CORRECTED Stage 8.1 37-feature model
(forecasting/stage7/stage8/stage8_1_corrected_2025/model_artifact/
stage8_1_CORRECTED_candidate_37feature_model.joblib) into the ForecastEngine
interface, following the exact pattern already used by
forecasting/solar_branch_01/implementation/branch01_forecast_engine.py
(hash-verified load, fail-closed on any missing/invalid input).

SCOPE / DESIGN DECISIONS (read before changing anything):

- This is a NEW, separately-named, explicitly-instantiated engine. It does
  NOT modify system/forecasting/implementations/baseline.py (the existing
  fallback) or system/forecasting/implementations/s81_solar.py (the older
  stub adapter, which never loaded a real model and is left untouched).
  Neither system/orchestration/worker.py nor any MILP/EMS/ECD/OptionD code
  is modified -- the existing baseline-by-default selection in worker.py is
  completely unchanged. This engine becomes available for EXPLICIT use
  (e.g. `Stage81CorrectedForecastEngine()` instantiated directly, or wired
  into a cell's engine selection in a SEPARATE, later change) without
  silently replacing anything today.

- Stage 8.1's architecture is fundamentally different from Branch01's: it
  needs 37 features PER (origin, horizon_hour) ROW -- not one vector per
  origin -- because `horizon_hour` and several horizon-specific NWP/cloud/
  wind/terrain values are themselves features that vary across the 24
  rows of one origin. So this engine does NOT build features itself (that
  would require re-implementing the entire upstream merge pipeline --
  NWP, Stage 3b, Stage 4, terrain, u700/v700, LWP/IWP, context stats --
  as new production code, which is explicitly out of scope and is exactly
  the kind of "fabricate missing features" risk this task forbids). It
  instead REQUIRES the caller to supply an already-assembled (24, 37)
  feature matrix for the origin, in the exact frozen column order, via
  runtime_context["stage8_1_feature_matrix"]. If that is missing,
  malformed, or contains any unexpected NaN, this engine fails closed
  (raises ModelGovernanceError) rather than inventing values.

- Horizon/timestamp convention: this project's established convention
  (verified across Stage 3b/4, NWP, terrain, u700/v700 throughout this
  investigation) is horizon_hour=1 == forecast_start + 0h. This engine
  uses that convention for its output timestamps -- NOT the +1h convention
  used by Branch01's engine / the older s81_solar.py stub. ForecastBundle
  permits a 0h or 1h gap between origin_timestamp and timestamps[0], so
  this is schema-legal; it is called out explicitly here and in bundle
  metadata so a caller comparing against those other engines' timestamp
  conventions is not misled.

- actual_SW_IN is never read by this engine. Night-hour zeroing uses only
  solar_elevation and clearsky_ghi, which are themselves two of the 37
  frozen input features (not derived from any future/target value).
"""

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
import joblib

from system.governance.model_reproducibility import ModelGovernanceError
from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine

FROZEN_MODEL_PATH = Path(
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_corrected_2025/"
    "model_artifact/stage8_1_CORRECTED_candidate_37feature_model.joblib"
)
FROZEN_MODEL_SHA256 = "64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce"
FROZEN_MODEL_ID = "STAGE8_1_CORRECTED_37FEATURE_HGB_V1"

# Exact frozen feature order (identical to
# forecasting/stage7/stage8/stage8_1_corrected_2025/build_corrected_feature_matrix.py
# and train_corrected_stage8_1_model.py). DO NOT reorder.
CANDIDATE_37_FEATURES = [
    "horizon_hour", "month", "hour", "solar_elevation", "solar_zenith", "clearsky_ghi",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h",
    "ctx_kt_std_6h", "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg",
    "terrain_solar_obstruction_flag", "clearsky_ghi_terrain_adjusted",
    "u700", "v700",
]
# u700/v700 may be legitimately NaN for horizon_hour 20-24 (documented archive
# resolution gap); every other column must be fully populated, no exceptions.
FEATURES_ALLOWING_NAN = {"u700", "v700"}

STAGE8_1_CORRECTED_PROVENANCE_KEY = "stage8_1_corrected_provenance"


class Stage81CorrectedForecastEngine(ForecastEngine):
    """
    Explicit, non-default ForecastEngine adapter for the frozen CORRECTED
    Stage 8.1 37-feature model. Must be instantiated and invoked
    deliberately; nothing in the existing orchestration selects it
    automatically.
    """

    def __init__(self, pv_config_path: Optional[Path] = None, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path("/home/punith-bs/01polaris (Copy)")
        self.model_path = FROZEN_MODEL_PATH
        self.model = self._load_and_verify_model()

        if pv_config_path is not None and Path(pv_config_path).exists():
            import yaml
            with open(pv_config_path, "r") as f:
                self.pv_config = yaml.safe_load(f)
        else:
            self.pv_config = {
                "array_area_m2": 300.0,
                "panel_efficiency": 0.20,
                "performance_ratio": 0.85,
                "max_inverter_power_w": 60000.0,
            }

        # Baseline engine used SOLELY to provide wind/demand channels when no
        # control_bundle is supplied -- same inheritance pattern Branch01's
        # engine uses. Solar fields from this sub-engine are never used.
        self.baseline_engine = LocalBaselineForecastEngine(
            Path(pv_config_path) if pv_config_path else self.base_dir / "config" / "solar_pv.yaml"
        )

    def _load_and_verify_model(self) -> Any:
        if not self.model_path.exists():
            raise ModelGovernanceError(f"Fail-closed: frozen Stage 8.1 corrected model missing at {self.model_path}")

        sha256 = hashlib.sha256(self.model_path.read_bytes()).hexdigest()
        if sha256.lower() != FROZEN_MODEL_SHA256.lower():
            raise ModelGovernanceError(
                f"Fail-closed: Stage 8.1 corrected model SHA-256 mismatch. "
                f"Expected {FROZEN_MODEL_SHA256}, got {sha256}"
            )
        try:
            return joblib.load(self.model_path)
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: unable to deserialize Stage 8.1 corrected model: {e}")

    def _sw_in_to_solar_power_w(self, sw_in_w_m2: float) -> float:
        raw_power = (
            sw_in_w_m2 * self.pv_config["array_area_m2"]
            * self.pv_config["panel_efficiency"] * self.pv_config["performance_ratio"]
        )
        return max(0.0, min(raw_power, self.pv_config["max_inverter_power_w"]))

    @staticmethod
    def _validate_feature_matrix(fm: Any) -> pd.DataFrame:
        """Fail-closed validation. Never fabricates a missing value."""
        if fm is None:
            raise ModelGovernanceError(
                "Fail-closed: runtime_context['stage8_1_feature_matrix'] not provided. "
                "This engine does not build Stage 8.1 features itself -- the caller "
                "must supply the already-assembled (24, 37) feature matrix."
            )

        if isinstance(fm, pd.DataFrame):
            df = fm.copy()
            if list(df.columns) != CANDIDATE_37_FEATURES:
                missing = [c for c in CANDIDATE_37_FEATURES if c not in df.columns]
                extra = [c for c in df.columns if c not in CANDIDATE_37_FEATURES]
                if missing:
                    raise ModelGovernanceError(f"Fail-closed: feature matrix missing required columns: {missing}")
                # Reorder if all present but out of order; do not silently accept wrong order.
                df = df[CANDIDATE_37_FEATURES]
                if extra:
                    pass  # extra columns ignored only after confirming nothing required is missing
        else:
            arr = np.asarray(fm, dtype=np.float64)
            if arr.shape != (24, 37):
                raise ModelGovernanceError(f"Fail-closed: feature matrix shape mismatch. Expected (24, 37), got {arr.shape}")
            df = pd.DataFrame(arr, columns=CANDIDATE_37_FEATURES)

        if df.shape != (24, 37):
            raise ModelGovernanceError(f"Fail-closed: feature matrix shape mismatch. Expected (24, 37), got {df.shape}")

        if "actual_SW_IN" in getattr(fm, "columns", []):
            raise ModelGovernanceError("Fail-closed: actual_SW_IN must never be supplied as a model input.")

        expected_horizon = list(range(1, 25))
        if list(df["horizon_hour"].astype(int)) != expected_horizon:
            raise ModelGovernanceError(
                f"Fail-closed: horizon_hour column must be exactly [1..24] in order, got "
                f"{list(df['horizon_hour'].astype(int))}"
            )

        for col in CANDIDATE_37_FEATURES:
            if col in FEATURES_ALLOWING_NAN:
                continue
            if df[col].isna().any() or np.isinf(df[col].values).any():
                raise ModelGovernanceError(f"Fail-closed: NaN/Inf detected in required feature '{col}' (not an allowed-NaN feature).")

        # u700/v700 may only be NaN for horizon_hour 20-24 (documented gap); any NaN
        # outside that window means an upstream feature-builder problem, not a known gap.
        for col in FEATURES_ALLOWING_NAN:
            bad = df[col].isna() & (df["horizon_hour"] < 20)
            if bad.any():
                raise ModelGovernanceError(
                    f"Fail-closed: unexpected NaN in '{col}' for horizon_hour < 20 "
                    f"(only horizon_hour 20-24 may be NaN, per the documented MEPS archive gap)."
                )

        if np.isinf(df.drop(columns=list(FEATURES_ALLOWING_NAN)).values).any():
            raise ModelGovernanceError("Fail-closed: Inf detected in feature matrix.")

        return df

    def predict(self, station_state: StationState, runtime_context: Optional[Dict[str, Any]] = None) -> ForecastBundle:
        if not isinstance(station_state, StationState):
            raise ModelGovernanceError("Fail-closed: invalid StationState object provided.")
        if runtime_context is None:
            runtime_context = {}

        origin_ts_str = station_state.timestamp
        try:
            origin_dt = datetime.fromisoformat(origin_ts_str.replace("Z", "+00:00"))
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: invalid origin timestamp '{origin_ts_str}': {e}")

        fm = runtime_context.get("stage8_1_feature_matrix")
        feature_df = self._validate_feature_matrix(fm)

        X = feature_df[CANDIDATE_37_FEATURES].values.astype(np.float64)

        try:
            residual = self.model.predict(X)
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Stage 8.1 corrected model inference exception: {e}")

        if len(residual) != 24:
            raise ModelGovernanceError(f"Fail-closed: expected 24 residual predictions, got {len(residual)}")
        if np.isnan(residual).any() or np.isinf(residual).any():
            raise ModelGovernanceError("Fail-closed: NaN or Inf in Stage 8.1 corrected model residual output.")

        pred_stage4_fold = feature_df["pred_stage4_fold"].values
        solar_elevation = feature_df["solar_elevation"].values
        clearsky_ghi = feature_df["clearsky_ghi"].values
        is_night_causal = (solar_elevation <= 0.0) | (clearsky_ghi == 0.0)

        pred_sw_in = np.maximum(0.0, pred_stage4_fold + residual)
        pred_sw_in = np.where(is_night_causal, 0.0, pred_sw_in)

        # Convention (see module docstring): horizon_hour=1 == forecast_start + 0h.
        timestamps = [(origin_dt + timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        solar_irr_pts = [float(v) for v in pred_sw_in]
        solar_gen_pts = [round(self._sw_in_to_solar_power_w(v), 2) for v in solar_irr_pts]

        solar_irradiance = TimeseriesForecast(solar_irr_pts, solar_irr_pts, solar_irr_pts, unit="W/m^2")
        solar_generation = TimeseriesForecast(solar_gen_pts, solar_gen_pts, solar_gen_pts, unit="W")

        control_bundle = runtime_context.get("control_bundle")
        if "wind_generation" in runtime_context and isinstance(runtime_context["wind_generation"], TimeseriesForecast):
            wind_gen = runtime_context["wind_generation"]
        elif control_bundle is not None and hasattr(control_bundle, "wind_generation"):
            wind_gen = control_bundle.wind_generation
        else:
            wind_gen = self.baseline_engine.predict(station_state, runtime_context).wind_generation

        if "demand" in runtime_context and isinstance(runtime_context["demand"], TimeseriesForecast):
            demand_fc = runtime_context["demand"]
        elif control_bundle is not None and hasattr(control_bundle, "demand"):
            demand_fc = control_bundle.demand
        else:
            demand_fc = self.baseline_engine.predict(station_state, runtime_context).demand

        provenance = {
            "model_identity": FROZEN_MODEL_ID,
            "model_path": str(self.model_path),
            "model_sha256": FROZEN_MODEL_SHA256,
            "feature_count": 37,
            "feature_order": CANDIDATE_37_FEATURES,
            "target": "SW_IN (reconstructed from residual-on-Stage4: max(0, pred_stage4_fold + residual), night forced to 0)",
            "unit": "W/m^2",
            "forecast_origin": origin_ts_str,
            "horizon_hours": 24,
            "horizon_convention": "horizon_hour=1 == forecast_start + 0h (NOT +1h; differs from Branch01/legacy s81_solar.py stub)",
            "trained_on": "2024 EVEN origins only (174 origins); never trained on 2025 data",
            "corrected_vs_historical": "terrain (4 features) + u700/v700 (2 features) rebuilt with corrected causal semantics; other 31 features unchanged",
            "causality_preserved": True,
            "actual_SW_IN_used_as_input": False,
            "engine_default_in_orchestration": False,
            "fallback_available": "system.forecasting.implementations.baseline.LocalBaselineForecastEngine (unchanged, still default)",
        }

        metadata = {
            "model_id": FROZEN_MODEL_ID,
            "model_sha256": FROZEN_MODEL_SHA256,
            "engine_class": "Stage81CorrectedForecastEngine",
            "SOLAR_FORECAST_SOURCE": FROZEN_MODEL_ID,
            "SOLAR_MODEL_SHA": FROZEN_MODEL_SHA256,
            STAGE8_1_CORRECTED_PROVENANCE_KEY: provenance,
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
            metadata=metadata,
        )
