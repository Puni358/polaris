"""
Unit and Integration Tests for Research-Only Causal NWP + Physics Solar Forecaster
(CausalNwpPhysicsForecastEngine)

Covers Tests A through L:
- Test A: 24-hour output shape
- Test B: Timestamp alignment (t+1 ... t+24)
- Test C: Night-time zeroing (solar_elevation <= 0 or GHI_cs <= 0)
- Test D: Cloud fraction 0 -> clear-sky output
- Test E: Cloud fraction 1 (or 100%) -> zero output
- Test F: Negative cloud -> fail closed (ValueError)
- Test G: Cloud > 100% -> fail closed (ValueError)
- Test H: NaN/Inf cloud -> fail closed (ValueError)
- Test I: Missing MEPS / wrong horizon -> fail closed (ValueError)
- Test J: Causal firewall: actual_SW_IN in input -> fail closed (PermissionError)
- Test K: Deterministic repeatability
- Test L: ForecastBundle v1.0 schema compatibility & roundtrip serialization
- Single-origin smoke test on 2024 MEPS weather forecast data
"""

import json
import math
from pathlib import Path
import pytest
import pandas as pd
import pvlib
from pvlib.location import Location

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.forecasting.implementations.causal_nwp_physics import (
    CausalNwpPhysicsForecastEngine,
    validate_causal_nwp_bundle,
    CAUSAL_NWP_PROVENANCE_KEY,
    NUOLJA_LATITUDE,
    NUOLJA_LONGITUDE,
    NUOLJA_ELEVATION_M,
    NUOLJA_TZ
)


@pytest.fixture
def pv_config_path(tmp_path) -> Path:
    config_file = tmp_path / "pv_config.yaml"
    config_file.write_text(
        "array_area_m2: 300.0\npanel_efficiency: 0.20\nperformance_ratio: 0.85\nmax_inverter_power_w: 60000.0\n"
    )
    return config_file


@pytest.fixture
def sample_station_state() -> StationState:
    return StationState(
        timestamp="2024-06-20T23:00:00Z",
        battery_soc_pct=75.0,
        battery_energy_wh=15000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=12000.0,
        last_observed_wind_generation=5000.0
    )


def test_a_24_hour_output_shape(pv_config_path, sample_station_state):
    """Test A: Output arrays all have exactly 24 hourly steps."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    assert isinstance(engine, ForecastEngine)

    context = {"fc_cloud_cover": [50.0] * 24}
    bundle = engine.predict(sample_station_state, context)

    assert isinstance(bundle, ForecastBundle)
    assert bundle.schema_version == "1.0.0"
    assert bundle.horizon_hours == 24
    assert len(bundle.timestamps) == 24
    assert len(bundle.solar_irradiance.point) == 24
    assert len(bundle.solar_irradiance.lower) == 24
    assert len(bundle.solar_irradiance.upper) == 24
    assert len(bundle.solar_generation.point) == 24
    assert len(bundle.solar_generation.lower) == 24
    assert len(bundle.solar_generation.upper) == 24
    assert len(bundle.wind_generation.point) == 24
    assert len(bundle.demand.point) == 24


def test_b_timestamp_alignment(pv_config_path, sample_station_state):
    """Test B: 24 hourly timestamps are aligned to t+1 ... t+24 strictly monotonic UTC."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [25.0] * 24}
    bundle = engine.predict(sample_station_state, context)

    assert bundle.timestamps[0] == "2024-06-21T00:00:00Z"
    assert bundle.timestamps[1] == "2024-06-21T01:00:00Z"
    assert bundle.timestamps[23] == "2024-06-21T23:00:00Z"

    # Matching explicit timestamps succeeds
    context_with_ts = {
        "fc_cloud_cover": [25.0] * 24,
        "timestamps": list(bundle.timestamps)
    }
    bundle_ts = engine.predict(sample_station_state, context_with_ts)
    assert bundle_ts.timestamps == bundle.timestamps

    # Mismatched timestamps fail closed
    bad_ts = list(bundle.timestamps)
    bad_ts[5] = "2024-06-21T07:00:00Z"  # Skip hour 5
    with pytest.raises(ValueError, match="Timestamp alignment failure"):
        engine.predict(sample_station_state, {"fc_cloud_cover": [25.0] * 24, "timestamps": bad_ts})


def test_c_night_time_zeroing(pv_config_path):
    """Test C: Night-time zeroing when solar elevation <= 0 or clear-sky GHI <= 0."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)

    # Polar night in Nuolja: winter solstice (sun is below horizon 24h)
    winter_state = StationState(
        timestamp="2024-12-20T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=10000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=3000.0
    )

    # Even with 0% cloud cover (perfectly clear), winter solstice output must be strictly 0.0
    context = {"fc_cloud_cover": [0.0] * 24}
    bundle = engine.predict(winter_state, context)

    for h, (irr, gen) in enumerate(zip(bundle.solar_irradiance.point, bundle.solar_generation.point)):
        assert irr == 0.0, f"Expected 0.0 irradiance during polar night at step {h}, got {irr}"
        assert gen == 0.0, f"Expected 0.0 generation during polar night at step {h}, got {gen}"

    # Autumn equinox: night hours (e.g. 00:00 UTC) must be 0.0
    autumn_state = StationState(
        timestamp="2024-09-17T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=10000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=10000.0,
        last_observed_wind_generation=3000.0
    )
    bundle_autumn = engine.predict(autumn_state, {"fc_cloud_cover": [0.0] * 24})
    # Step 0 is 2024-09-18 00:00:00Z, elevation < 0
    assert bundle_autumn.solar_irradiance.point[0] == 0.0
    assert bundle_autumn.solar_generation.point[0] == 0.0


def test_d_cloud_fraction_zero_clearsky(pv_config_path, sample_station_state):
    """Test D: Cloud fraction 0 (0% cloud) produces exact clear-sky irradiance."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [0.0] * 24}
    bundle = engine.predict(sample_station_state, context)

    # Independently compute PVLIB clear sky for verification
    loc = Location(
        latitude=NUOLJA_LATITUDE,
        longitude=NUOLJA_LONGITUDE,
        tz=NUOLJA_TZ,
        altitude=NUOLJA_ELEVATION_M,
        name="Nuolja"
    )
    times = pd.to_datetime(bundle.timestamps, utc=True)
    solpos = loc.get_solarposition(times)
    cs = loc.get_clearsky(times, model="ineichen")

    for h in range(24):
        elev = float(solpos["elevation"].iloc[h])
        cs_ghi = float(cs["ghi"].iloc[h])
        expected = 0.0 if (elev <= 0 or cs_ghi <= 0) else round(cs_ghi, 2)
        assert bundle.solar_irradiance.point[h] == pytest.approx(expected, abs=1e-2)


def test_e_cloud_fraction_one_zero_output(pv_config_path, sample_station_state):
    """Test E: Cloud fraction 1 (100% cloud cover) produces 0.0 output."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)

    # Test via fc_cloud_cover = 100.0
    context_pct = {"fc_cloud_cover": [100.0] * 24}
    bundle_pct = engine.predict(sample_station_state, context_pct)
    for h in range(24):
        assert bundle_pct.solar_irradiance.point[h] == 0.0
        assert bundle_pct.solar_generation.point[h] == 0.0

    # Test via cloud_fraction = 1.0
    context_frac = {"cloud_fraction": [1.0] * 24}
    bundle_frac = engine.predict(sample_station_state, context_frac)
    for h in range(24):
        assert bundle_frac.solar_irradiance.point[h] == 0.0
        assert bundle_frac.solar_generation.point[h] == 0.0


def test_f_negative_cloud_fails_closed(pv_config_path, sample_station_state):
    """Test F: Negative cloud cover fails closed with ValueError."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [-5.0] + [20.0] * 23}
    with pytest.raises(ValueError, match="out of bounds"):
        engine.predict(sample_station_state, context)

    # Also test negative cloud_fraction
    context_frac = {"cloud_fraction": [-0.1] + [0.5] * 23}
    with pytest.raises(ValueError, match="out of bounds"):
        engine.predict(sample_station_state, context_frac)


def test_g_cloud_over_100_fails_closed(pv_config_path, sample_station_state):
    """Test G: Cloud cover > 100% fails closed with ValueError."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [105.0] + [20.0] * 23}
    with pytest.raises(ValueError, match="out of bounds"):
        engine.predict(sample_station_state, context)

    # Also test cloud_fraction > 1.0
    context_frac = {"cloud_fraction": [1.05] + [0.5] * 23}
    with pytest.raises(ValueError, match="out of bounds"):
        engine.predict(sample_station_state, context_frac)


def test_h_nan_inf_cloud_fails_closed(pv_config_path, sample_station_state):
    """Test H: NaN or Inf cloud values fail closed with ValueError."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)

    # NaN test
    context_nan = {"fc_cloud_cover": [float("nan")] + [20.0] * 23}
    with pytest.raises(ValueError, match="NaN or Inf"):
        engine.predict(sample_station_state, context_nan)

    # Inf test
    context_inf = {"fc_cloud_cover": [float("inf")] + [20.0] * 23}
    with pytest.raises(ValueError, match="NaN or Inf"):
        engine.predict(sample_station_state, context_inf)


def test_i_missing_meps_fails_closed(pv_config_path, sample_station_state):
    """Test I: Missing MEPS trajectory or wrong horizon length fails closed with ValueError."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)

    # Missing entirely
    with pytest.raises(ValueError, match="Missing required MEPS cloud forecast"):
        engine.predict(sample_station_state, {})

    # Trajectory is None
    with pytest.raises(ValueError, match="is None"):
        engine.predict(sample_station_state, {"fc_cloud_cover": None})

    # Wrong horizon length: 23 steps
    with pytest.raises(ValueError, match="Expected exactly 24 forecast steps"):
        engine.predict(sample_station_state, {"fc_cloud_cover": [50.0] * 23})

    # Wrong horizon length: 25 steps
    with pytest.raises(ValueError, match="Expected exactly 24 forecast steps"):
        engine.predict(sample_station_state, {"fc_cloud_cover": [50.0] * 25})


def test_j_actual_sw_in_detected_fails_closed(pv_config_path, sample_station_state):
    """Test J: Causal firewall blocks actual observations / ground-truth with PermissionError."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)

    # actual_SW_IN in context
    context_actual_sw_in = {
        "fc_cloud_cover": [50.0] * 24,
        "actual_SW_IN": [100.0] * 24
    }
    with pytest.raises(PermissionError, match="Causal firewall violation"):
        engine.predict(sample_station_state, context_actual_sw_in)

    # ground_truth in context
    context_ground_truth = {
        "fc_cloud_cover": [50.0] * 24,
        "ground_truth": True
    }
    with pytest.raises(PermissionError, match="Causal firewall violation"):
        engine.predict(sample_station_state, context_ground_truth)

    # Nested actual observation
    context_nested = {
        "fc_cloud_cover": [50.0] * 24,
        "nested_data": {
            "future_actual_irradiance": [50.0] * 24
        }
    }
    with pytest.raises(PermissionError, match="Causal firewall violation"):
        engine.predict(sample_station_state, context_nested)


def test_k_deterministic_repeatability(pv_config_path, sample_station_state):
    """Test K: Deterministic repeated execution yields identical outputs."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [float(i * 4) for i in range(24)]}

    bundle_1 = engine.predict(sample_station_state, context)
    bundle_2 = engine.predict(sample_station_state, context)

    assert bundle_1.solar_irradiance.point == bundle_2.solar_irradiance.point
    assert bundle_1.solar_generation.point == bundle_2.solar_generation.point
    assert bundle_1.timestamps == bundle_2.timestamps
    assert bundle_1.metadata[CAUSAL_NWP_PROVENANCE_KEY] == bundle_2.metadata[CAUSAL_NWP_PROVENANCE_KEY]


def test_l_forecast_bundle_schema_compatibility(pv_config_path, sample_station_state):
    """Test L: ForecastBundle v1.0 schema compliance and JSON roundtrip serialization."""
    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    context = {"fc_cloud_cover": [30.0] * 24}
    bundle = engine.predict(sample_station_state, context)

    # Schema validation succeeds
    assert validate_causal_nwp_bundle(bundle) is True

    # Interval degenerate equality (lower == point == upper)
    for i in range(24):
        assert bundle.solar_irradiance.lower[i] == bundle.solar_irradiance.point[i] == bundle.solar_irradiance.upper[i]
        assert bundle.solar_generation.lower[i] == bundle.solar_generation.point[i] == bundle.solar_generation.upper[i]

    # JSON roundtrip
    json_str = bundle.to_json()
    dict_data = json.loads(json_str)
    reconstituted = ForecastBundle.from_dict(dict_data)

    assert reconstituted.schema_version == "1.0.0"
    assert reconstituted.horizon_hours == 24
    assert reconstituted.solar_irradiance.point == bundle.solar_irradiance.point
    assert reconstituted.solar_generation.point == bundle.solar_generation.point
    assert CAUSAL_NWP_PROVENANCE_KEY in reconstituted.metadata
    assert reconstituted.metadata[CAUSAL_NWP_PROVENANCE_KEY]["research_only"] is True


def test_smoke_single_origin_2024_meps(pv_config_path):
    """Smoke test: 1 representative 24h MEPS trajectory from POLARIS 2024 weather dataset."""
    weather_csv = Path("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    if not weather_csv.exists():
        pytest.skip(f"Weather dataset {weather_csv} not present, skipping smoke test.")

    df = pd.read_csv(weather_csv)
    # Select first origin: 2024-01-20 00:00:00 (origin t0 is 2024-01-19 23:00:00Z)
    sub = df[df["forecast_start"] == "2024-01-20 00:00:00"]
    assert len(sub) == 24

    cloud_trajectory = sub["fc_cloud_cover"].tolist()

    state = StationState(
        timestamp="2024-01-19T23:00:00Z",
        battery_soc_pct=80.0,
        battery_energy_wh=16000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0
    )

    engine = CausalNwpPhysicsForecastEngine(pv_config_path)
    bundle = engine.predict(state, {"fc_cloud_cover": cloud_trajectory})

    assert validate_causal_nwp_bundle(bundle) is True
    assert bundle.horizon_hours == 24
    assert bundle.origin_timestamp == "2024-01-19T23:00:00Z"
    assert bundle.timestamps[0] == "2024-01-20T00:00:00Z"
    assert bundle.timestamps[23] == "2024-01-20T23:00:00Z"

    # January 20 at 68.36°N is polar twilight/night; check values are non-negative and physically plausible
    for irr in bundle.solar_irradiance.point:
        assert irr >= 0.0
    for gen in bundle.solar_generation.point:
        assert gen >= 0.0
