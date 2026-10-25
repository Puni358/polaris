"""
Branch 01 Forecast Engine Module
Implements stable ForecastEngine interface for POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1.
Constructs valid ForecastBundle Schema 1.0.0 containing solar irradiance (W/m^2) and PV generation power (W).
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
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder

FROZEN_MODEL_SHA256 = "65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781"
FROZEN_MODEL_ID = "POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1"
FROZEN_RUN_ID = "RUN_BRANCH01_CANDIDATE_A_HGB"

class Branch01ForecastEngine(ForecastEngine):
    """
    Branch 01 Solar Forecasting Engine.
    Consumes frozen Candidate A MultiOutputRegressor(HistGradientBoostingRegressor) artifact.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir) if base_dir else Path("/home/punith-bs/01polaris (Copy)")
        self.model_path = self.base_dir / "artifacts" / "model_runs" / FROZEN_RUN_ID / "model.joblib"
        self.model = self._load_and_verify_model()

    def _load_and_verify_model(self) -> Any:
        """Verify model file existence and exact SHA-256 hash before loading."""
        if not self.model_path.exists():
            raise ModelGovernanceError(f"Fail-closed: Frozen model artifact missing at {self.model_path}")

        sha256 = hashlib.sha256(self.model_path.read_bytes()).hexdigest()
        if sha256.lower() != FROZEN_MODEL_SHA256.lower():
            raise ModelGovernanceError(
                f"Fail-closed: Model SHA-256 mismatch. Expected {FROZEN_MODEL_SHA256}, got {sha256}"
            )

        try:
            model = joblib.load(self.model_path)
            return model
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Unable to deserialize frozen model artifact: {e}")

    def predict(self, station_state: StationState, runtime_context: Dict[str, Any]) -> ForecastBundle:
        """
        Generate 24-hour ForecastBundle for forecast origin t.
        Fails closed on missing or invalid inputs.
        """
        if not isinstance(station_state, StationState):
            raise ModelGovernanceError("Fail-closed: Invalid StationState object provided.")

        # Extract origin timestamp
        origin_str = station_state.timestamp
        try:
            origin_dt = datetime.fromisoformat(origin_str.replace("Z", "+00:00"))
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Invalid origin timestamp '{origin_str}': {e}")

        # Extract or build 18-element feature vector
        if "feature_vector" in runtime_context:
            x_vec = np.array(runtime_context["feature_vector"], dtype=np.float64)
        elif "obs_df" in runtime_context and "clearsky_df" in runtime_context and "origin_idx" in runtime_context:
            obs_df = runtime_context["obs_df"]
            clearsky_df = runtime_context["clearsky_df"]
            origin_idx = runtime_context["origin_idx"]
            x_vec = FeatureMatrixBuilder.build_feature_vector(
                obs_df["SW_IN"], obs_df["timestamp"], origin_idx, clearsky_df
            )
        else:
            raise ModelGovernanceError("Fail-closed: Neither 'feature_vector' nor ('obs_df', 'clearsky_df', 'origin_idx') provided in runtime_context.")

        # Fail closed on feature shape or NaN/Inf
        if x_vec.shape != (18,):
            raise ModelGovernanceError(f"Fail-closed: Feature count mismatch. Expected 18 features, got {x_vec.shape}")

        if np.isnan(x_vec).any() or np.isinf(x_vec).any():
            raise ModelGovernanceError("Fail-closed: NaN or Inf detected in runtime input feature vector.")

        # Run model inference
        try:
            sw_in_preds = self.model.predict(x_vec.reshape(1, -1))[0]
        except Exception as e:
            raise ModelGovernanceError(f"Fail-closed: Model inference exception: {e}")

        if len(sw_in_preds) != 24:
            raise ModelGovernanceError(f"Fail-closed: Expected 24 horizon predictions, got {len(sw_in_preds)}")

        if np.isnan(sw_in_preds).any() or np.isinf(sw_in_preds).any():
            raise ModelGovernanceError("Fail-closed: NaN or Inf detected in model predictions.")

        # Enforce non-negative irradiance physical bound
        sw_in_preds = np.maximum(0.0, sw_in_preds)

        # Engineering Solar PV Power Mapping
        # P_raw = SW_IN * 300 m^2 * 0.20 * 0.85 = SW_IN * 51.0; P_solar = min(P_raw, 60,000 W)
        p_raw = sw_in_preds * 51.0
        p_solar_preds = np.minimum(p_raw, 60000.0)

        # Construct 24 horizon timestamps (t+1h through t+24h)
        timestamps = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        # Construct TimeseriesForecast objects
        sw_in_list = [float(v) for v in sw_in_preds]
        p_solar_list = [float(v) for v in p_solar_preds]

        solar_irradiance = TimeseriesForecast(point=sw_in_list, lower=sw_in_list, upper=sw_in_list, unit="W/m^2")
        solar_generation = TimeseriesForecast(point=p_solar_list, lower=p_solar_list, upper=p_solar_list, unit="W")

        # Non-solar forecast inheritance & strict fail-closed contract check
        control_bundle = runtime_context.get("control_bundle")
        
        if "wind_generation" in runtime_context and isinstance(runtime_context["wind_generation"], TimeseriesForecast):
            wind_gen = runtime_context["wind_generation"]
        elif control_bundle is not None and hasattr(control_bundle, "wind_generation"):
            wind_gen = control_bundle.wind_generation
        else:
            raise ModelGovernanceError("Fail-closed: Missing or invalid 'wind_generation' forecast in runtime_context. Non-solar forecasts must be inherited from Control.")

        if "demand" in runtime_context and isinstance(runtime_context["demand"], TimeseriesForecast):
            demand_fc = runtime_context["demand"]
        elif control_bundle is not None and hasattr(control_bundle, "demand"):
            demand_fc = control_bundle.demand
        else:
            raise ModelGovernanceError("Fail-closed: Missing or invalid 'demand' forecast in runtime_context. Non-solar forecasts must be inherited from Control.")

        metadata = {
            "model_id": FROZEN_MODEL_ID,
            "model_sha256": FROZEN_MODEL_SHA256,
            "run_id": FROZEN_RUN_ID,
            "branch_id": "POLARIS_SOLAR_FORECAST_BRANCH_01",
            "schema_version": "1.0.0",
            "feature_count": 18,
            "engineering_solar_multiplier": 51.0,
            "engineering_solar_cap_w": 60000.0,
            "SOLAR_FORECAST_SOURCE": FROZEN_MODEL_ID,
            "SOLAR_MODEL_SHA": FROZEN_MODEL_SHA256,
            "DEMAND_FORECAST_SOURCE": "POLARIS_LOCAL_BASELINE_DEMAND_PERSISTENCE_V1",
            "DEMAND_FORECAST_SOURCE_SHA": "905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993",
            "WIND_FORECAST_SOURCE": "POLARIS_LOCAL_BASELINE_WIND_PERSISTENCE_V1",
            "WIND_FORECAST_SOURCE_SHA": "905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993",
            "DEMAND_FORECAST_INHERITED_FROM_CONTROL": True,
            "WIND_FORECAST_INHERITED_FROM_CONTROL": True,
            "DEMAND_FORECAST_REGENERATED_BY_TREATMENT": False,
            "WIND_FORECAST_REGENERATED_BY_TREATMENT": False
        }

        # Build and validate ForecastBundle
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin_str,
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=solar_irradiance,
            solar_generation=solar_generation,
            wind_generation=wind_gen,
            demand=demand_fc,
            metadata=metadata
        )

        return bundle
