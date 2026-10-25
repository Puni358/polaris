"""
POLARIS Research-Only Causal NWP + Physics Solar Forecaster
Implementation: CausalNwpPhysicsForecastEngine

RESEARCH USE ONLY / BENCHMARK HARNESS BASELINE:
- Consumes MEPS 18Z causal cloud forecast trajectory supplied via runtime_context.
- Computes deterministic PVLIB Ineichen clear-sky global horizontal irradiance (GHI).
- Applies physical clear-sky attenuation formula:
    forecast_GHI = max(0.0, clear_sky_GHI * (1.0 - cloud_fraction))
  where:
    cloud_fraction = fc_cloud_cover / 100.0
- Night zeroing:
    if solar_elevation <= 0.0 or clear_sky_GHI <= 0.0:
        forecast_GHI = 0.0
- Applies authorized D3 engineering PV transformation:
    raw_power = forecast_GHI * 300 m^2 * 0.20 * 0.85 = forecast_GHI * 51.0
    solar_generation = min(raw_power, 60000.0 W)
- Interval semantics: D1/D2 authorized degenerate point representation (lower == point == upper).
- Non-solar channels (wind, demand): delegated to LocalBaselineForecastEngine.

CAUSAL FIREWALL:
- Fails closed (PermissionError) if any ground-truth observation, actual SW_IN,
  or future state is detected in runtime_context.
- Fails closed (ValueError) on missing MEPS trajectory, invalid horizon, unaligned timestamps,
  negative cloud cover, cloud cover > 100%, or NaN/Inf values.

GOVERNANCE & COMPLIANCE DISCLAIMER:
- This is a research baseline assumption for closed-loop benchmark design.
- NOT physically validated against empirical ground truth.
- NOT authorized for production.
- NO parameter tuning or k-coefficients (Stage 4 k_h ≈ 0.50 is NOT used).
- Frozen Stage 8.1 models and artifacts are NOT modified.
"""

import math
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union

import pandas as pd
import pvlib
from pvlib.location import Location

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine


# Nuolja Research Station Coordinates (established in POLARIS)
NUOLJA_LATITUDE = 68.362074
NUOLJA_LONGITUDE = 18.738752
NUOLJA_ELEVATION_M = 702.0
NUOLJA_TZ = "UTC"

CAUSAL_NWP_PROVENANCE_KEY = "causal_nwp_physics_provenance"

# Forbidden keywords in runtime_context triggering Causal Firewall block
FORBIDDEN_FIREWALL_KEYWORDS = [
    "actual_sw_in",
    "actual_solar",
    "actual_irradiance",
    "actual_ghi",
    "actual_generation",
    "ground_truth",
    "future_actual",
    "future_observation",
    "future_state",
    "sites_actual",
    "sites_obs",
    "sites_sw_in",
    "sw_in_actual",
    "observed_sw_in",
    "observed_irradiance",
]


def check_causal_firewall(context: Any) -> None:
    """
    Recursively scans runtime_context for forbidden ground-truth observation keys.
    Fails closed with PermissionError if any ground truth or future actuals are detected.
    """
    if isinstance(context, dict):
        for k, v in context.items():
            k_lower = str(k).lower().strip()
            for forbidden in FORBIDDEN_FIREWALL_KEYWORDS:
                if forbidden in k_lower:
                    raise PermissionError(
                        f"Causal firewall violation: forbidden ground-truth key '{k}' "
                        f"detected in runtime_context. Forecaster must not access actual observations."
                    )
            check_causal_firewall(v)
    elif isinstance(context, (list, tuple)):
        for item in context:
            check_causal_firewall(item)


def extract_and_validate_cloud_fractions(runtime_context: Dict[str, Any]) -> List[float]:
    """
    Extracts MEPS cloud cover trajectory from runtime_context and validates:
    - Must be provided under 'fc_cloud_cover', 'meps_cloud_cover', 'cloud_cover', or 'cloud_fraction'.
    - Must have exactly 24 hourly steps.
    - No NaN or Inf values.
    - Values must be within valid range:
      - [0.0, 100.0] for percentage cloud cover
      - [0.0, 1.0] for fraction
    Returns cloud_fractions as a list of 24 floats in [0.0, 1.0].
    """
    is_fraction = False
    raw_cloud: Optional[Union[List[Any], Any]] = None

    if "fc_cloud_cover" in runtime_context:
        raw_cloud = runtime_context["fc_cloud_cover"]
    elif "meps_cloud_cover" in runtime_context:
        raw_cloud = runtime_context["meps_cloud_cover"]
    elif "cloud_cover" in runtime_context:
        raw_cloud = runtime_context["cloud_cover"]
    elif "cloud_fraction" in runtime_context:
        raw_cloud = runtime_context["cloud_fraction"]
        is_fraction = True
    else:
        raise ValueError(
            "Missing required MEPS cloud forecast in runtime_context "
            "(expected key 'fc_cloud_cover' or 'meps_cloud_cover')."
        )

    if raw_cloud is None:
        raise ValueError("MEPS cloud forecast trajectory is None.")

    try:
        cloud_list = list(raw_cloud)
    except Exception as e:
        raise ValueError(f"MEPS cloud forecast cannot be converted to list: {e}")

    if len(cloud_list) != 24:
        raise ValueError(f"Expected exactly 24 forecast steps for MEPS cloud forecast, got {len(cloud_list)}.")

    fractions: List[float] = []
    for idx, val in enumerate(cloud_list):
        if val is None:
            raise ValueError(f"MEPS cloud forecast contains None at index {idx}.")
        try:
            fval = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"MEPS cloud forecast value '{val}' at index {idx} cannot be converted to float.")

        if math.isnan(fval) or math.isinf(fval):
            raise ValueError(f"MEPS cloud forecast contains NaN or Inf at index {idx}.")

        if is_fraction:
            if fval < 0.0 or fval > 1.0:
                raise ValueError(f"MEPS cloud_fraction {fval} at index {idx} is out of bounds [0.0, 1.0].")
            fractions.append(fval)
        else:
            if fval < 0.0 or fval > 100.0:
                raise ValueError(f"MEPS cloud cover {fval} at index {idx} is out of bounds [0.0, 100.0].")
            fractions.append(fval / 100.0)

    return fractions


def validate_causal_nwp_bundle(bundle: ForecastBundle) -> bool:
    """
    Validates Causal NWP + Physics bundle metadata, interval semantics, PV mapping,
    horizon, non-negativity, and provenance structure.
    """
    if bundle.schema_version != "1.0.0":
        raise ValueError(f"Invalid schema_version '{bundle.schema_version}', expected '1.0.0'.")

    if bundle.horizon_hours != 24:
        raise ValueError(f"Invalid horizon_hours {bundle.horizon_hours}, expected 24.")

    if len(bundle.timestamps) != 24:
        raise ValueError(f"Expected 24 timestamps, got {len(bundle.timestamps)}.")

    if CAUSAL_NWP_PROVENANCE_KEY not in bundle.metadata:
        raise ValueError(f"Missing required metadata key '{CAUSAL_NWP_PROVENANCE_KEY}'.")

    prov = bundle.metadata[CAUSAL_NWP_PROVENANCE_KEY]
    if not isinstance(prov, dict):
        raise ValueError(f"Metadata entry '{CAUSAL_NWP_PROVENANCE_KEY}' must be a dictionary.")

    if prov.get("causality_preserved") is not True:
        raise ValueError("Causality preservation flag must be True.")

    if prov.get("research_only") is not True:
        raise ValueError("Research only flag must be True.")

    # Validate D1/D2 degenerate interval equality and D3 conversion
    for idx in range(24):
        irr_p = bundle.solar_irradiance.point[idx]
        irr_l = bundle.solar_irradiance.lower[idx]
        irr_u = bundle.solar_irradiance.upper[idx]

        if not (irr_l == irr_p == irr_u):
            raise ValueError(
                f"Degenerate interval violated for solar_irradiance at index {idx}: "
                f"lower ({irr_l}) == point ({irr_p}) == upper ({irr_u})."
            )

        if irr_p < 0.0:
            raise ValueError(f"Negative irradiance at index {idx}: {irr_p}")

        gen_p = bundle.solar_generation.point[idx]
        gen_l = bundle.solar_generation.lower[idx]
        gen_u = bundle.solar_generation.upper[idx]

        if not (gen_l == gen_p == gen_u):
            raise ValueError(
                f"Degenerate interval violated for solar_generation at index {idx}: "
                f"lower ({gen_l}) == point ({gen_p}) == upper ({gen_u})."
            )

        if gen_p < 0.0:
            raise ValueError(f"Negative generation at index {idx}: {gen_p}")

        # Check D3 conversion consistency: gen_p == round(min(irr_p * 51.0, 60000.0), 2)
        expected_raw = irr_p * 300.0 * 0.20 * 0.85
        expected_gen = round(max(0.0, min(expected_raw, 60000.0)), 2)
        if abs(gen_p - expected_gen) > 1e-2:
            raise ValueError(
                f"D3 PV transformation mismatch at index {idx}: "
                f"solar_generation ({gen_p}) != expected ({expected_gen}) from GHI ({irr_p})."
            )

    return True


class CausalNwpPhysicsForecastEngine(ForecastEngine):
    """
    Research-Only Causal NWP + Physics Solar ForecastEngine.

    Combines:
    - MET Norway MEPS 18Z causal cloud cover forecast
    - Deterministic PVLIB Ineichen clear-sky astronomical radiation model
    - Night zeroing when solar elevation <= 0 or clear-sky GHI <= 0
    - Authorized D3 engineering PV transformation (300 m^2, 20% eff, 0.85 PR, 60 kW clip)
    - Authorized D1/D2 degenerate point interval bounds (lower == point == upper)
    - Full causal firewall preventing ingestion of ground-truth observations.
    """

    def __init__(self, pv_config_path: Optional[Path] = None):
        if pv_config_path is not None and Path(pv_config_path).exists():
            with open(pv_config_path, "r") as f:
                self.pv_config = yaml.safe_load(f)
        else:
            self.pv_config = {
                "array_area_m2": 300.0,
                "panel_efficiency": 0.20,
                "performance_ratio": 0.85,
                "max_inverter_power_w": 60000.0
            }

        # Baseline engine used solely to provide baseline wind & demand channels
        self.baseline_engine = LocalBaselineForecastEngine(pv_config_path or Path("config/pv_config.yaml"))

        # PVLIB Location object for Nuolja
        self.location = Location(
            latitude=NUOLJA_LATITUDE,
            longitude=NUOLJA_LONGITUDE,
            tz=NUOLJA_TZ,
            altitude=NUOLJA_ELEVATION_M,
            name="Nuolja"
        )

    def _ghi_to_solar_power_w(self, ghi_w_m2: float) -> float:
        raw_power = (
            ghi_w_m2 *
            self.pv_config["array_area_m2"] *
            self.pv_config["panel_efficiency"] *
            self.pv_config["performance_ratio"]
        )
        clipped_power = min(raw_power, self.pv_config["max_inverter_power_w"])
        return max(0.0, float(clipped_power))

    def predict(
        self,
        station_state: StationState,
        runtime_context: Optional[Dict[str, Any]] = None
    ) -> ForecastBundle:
        """
        Generates a 24-hour causal solar ForecastBundle using MEPS cloud forecast + PVLIB.
        Fails closed if causal firewall is breached or inputs are invalid.
        """
        if runtime_context is None:
            runtime_context = {}

        # 1. Causal Firewall Check: Block any ground-truth / observation data
        check_causal_firewall(runtime_context)

        # 2. Extract and validate MEPS cloud cover forecast
        cloud_fractions = extract_and_validate_cloud_fractions(runtime_context)

        # 3. Parse origin timestamp t0 and build t+1 ... t+24 horizons
        origin_ts_str = station_state.timestamp
        try:
            if origin_ts_str.endswith("Z"):
                origin_dt = datetime.fromisoformat(origin_ts_str[:-1] + "+00:00")
            else:
                origin_dt = datetime.fromisoformat(origin_ts_str)
                if origin_dt.tzinfo is None:
                    origin_dt = origin_dt.replace(tzinfo=timezone.utc)
        except Exception as e:
            raise ValueError(f"Invalid station_state.timestamp format '{origin_ts_str}': {e}")

        timestamps: List[str] = []
        for h in range(1, 25):
            step_dt = origin_dt + timedelta(hours=h)
            timestamps.append(step_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

        # 4. Validate runtime_context timestamps if provided
        if "timestamps" in runtime_context:
            provided_ts = runtime_context["timestamps"]
            if not isinstance(provided_ts, (list, tuple)) or len(provided_ts) != 24:
                raise ValueError(
                    f"Provided timestamps must have 24 values, got {len(provided_ts) if isinstance(provided_ts, (list, tuple)) else type(provided_ts)}"
                )
            for h_idx, (exp, act) in enumerate(zip(timestamps, provided_ts)):
                try:
                    exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
                    act_dt = datetime.fromisoformat(str(act).replace("Z", "+00:00"))
                    if exp_dt != act_dt:
                        raise ValueError(
                            f"Timestamp alignment failure at index {h_idx}: expected {exp}, got {act}"
                        )
                except Exception as e:
                    raise ValueError(f"Timestamp parsing error at index {h_idx}: {e}")

        # 5. Baseline channels for wind and demand
        base_bundle = self.baseline_engine.predict(station_state, runtime_context)

        # 6. Compute deterministic clear-sky solar position and irradiance via PVLIB
        dt_index = pd.to_datetime(timestamps, utc=True)
        solpos = self.location.get_solarposition(dt_index)
        clearsky = self.location.get_clearsky(dt_index, model="ineichen")

        solar_irr_pts: List[float] = []
        solar_gen_pts: List[float] = []

        for h in range(24):
            elev = float(solpos["elevation"].iloc[h])
            cs_ghi = float(clearsky["ghi"].iloc[h])
            c_frac = cloud_fractions[h]

            # Physical night zeroing: if elevation <= 0 or clear-sky GHI <= 0
            if elev <= 0.0 or cs_ghi <= 0.0:
                forecast_ghi = 0.0
            else:
                # Baseline attenuation formula: GHI = max(0, cs_ghi * (1 - cloud_fraction))
                forecast_ghi = max(0.0, cs_ghi * (1.0 - c_frac))

            forecast_ghi = round(forecast_ghi, 2)
            solar_irr_pts.append(forecast_ghi)

            # Authorized D3 engineering PV transformation
            p_solar = round(self._ghi_to_solar_power_w(forecast_ghi), 2)
            solar_gen_pts.append(p_solar)

        # 7. D1/D2 degenerate point-only interval bounds
        solar_irr_forecast = TimeseriesForecast(
            point=solar_irr_pts,
            lower=solar_irr_pts,
            upper=solar_irr_pts,
            unit="W/m^2"
        )

        solar_gen_forecast = TimeseriesForecast(
            point=solar_gen_pts,
            lower=solar_gen_pts,
            upper=solar_gen_pts,
            unit="W"
        )

        # 8. Provenance metadata recording
        provenance = {
            "model_identity": "causal_nwp_physics_meps18z_pvlib",
            "model_architecture": "Deterministic Clear-Sky Physics + MEPS Cloud Attenuation",
            "method": "NWP_CLOUD_COVER_PHYSICAL_CLEARSKY",
            "formulation": "forecast_GHI = max(0.0, clear_sky_GHI * (1.0 - cloud_fraction))",
            "cloud_source": "MET_Norway_MEPS_18Z",
            "clearsky_model": "pvlib_ineichen",
            "station_coordinates": {
                "latitude": NUOLJA_LATITUDE,
                "longitude": NUOLJA_LONGITUDE,
                "elevation_m": NUOLJA_ELEVATION_M,
                "station_name": "Nuolja"
            },
            "research_only": True,
            "status": "RESEARCH_BASELINE_ONLY",
            "production_authorized": False,
            "empirical_pv_validation_claimed": False,
            "parameter_tuning_applied": False,
            "stage4_kh_applied": False,
            "disclaimer": (
                "Research baseline assumption only. Not physically validated. "
                "No empirical parameter tuning. Stage 4 k_h parameter is NOT used."
            ),
            "causality_preserved": True,
            "forecast_origin": origin_ts_str,
            "horizon_hours": 24,
            "pv_transformation": {
                "authorized_governance_decision": "D3_AUTHORIZED_ENGINEERING_REPRESENTATION",
                "formula": "raw_power = GHI * 300m^2 * 0.20 * 0.85; solar_generation = min(raw_power, 60000W)",
                "array_area_m2": self.pv_config["array_area_m2"],
                "panel_efficiency": self.pv_config["panel_efficiency"],
                "performance_ratio": self.pv_config["performance_ratio"],
                "max_inverter_power_w": self.pv_config["max_inverter_power_w"],
                "empirical_pv_validation_claimed": False
            },
            "interval_representation": {
                "governance_decision_d1": "LOWER_UPPER_SEMANTICS = FORECAST_UNCERTAINTY_BOUNDS_WITHOUT_CLAIMED_STATISTICAL_COVERAGE",
                "governance_decision_d2": "AUTHORIZED_DEGENERATE_POINT_REPRESENTATION",
                "array_mapping": "lower = point = upper",
                "statistical_coverage_claimed": False
            },
            "timestamps": timestamps,
            "solar_irradiance_point": solar_irr_pts,
            "solar_generation_point": solar_gen_pts
        }

        combined_metadata = dict(base_bundle.metadata)
        combined_metadata[CAUSAL_NWP_PROVENANCE_KEY] = provenance
        combined_metadata["engine_identity"] = "CausalNwpPhysicsForecastEngine"
        combined_metadata["research_status"] = "RESEARCH_ONLY"

        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin_ts_str,
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=solar_irr_forecast,
            solar_generation=solar_gen_forecast,
            wind_generation=base_bundle.wind_generation,
            demand=base_bundle.demand,
            metadata=combined_metadata
        )

        # 9. Verify contract compliance
        validate_causal_nwp_bundle(bundle)

        return bundle
