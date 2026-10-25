"""
Unit and Contract Integration Tests for Stage 8.1 ForecastEngine Adapter
(Stage81ForecastEngine) and ForecastBundle v1.0 Compliance.

Phase S8.1-C2 Verification Suite.
"""

import json
from pathlib import Path
import pytest

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.forecasting.implementations.s81_solar import (
    Stage81ForecastEngine,
    validate_stage81_solar_metadata,
    STAGE8_1_PROVENANCE_KEY
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
        timestamp="2026-09-18T06:00:00Z",
        battery_soc_pct=75.0,
        battery_energy_wh=15000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=450.0,
        last_observed_demand=12000.0,
        last_observed_wind_generation=5000.0
    )


def test_1_adapter_constructs_valid_forecast_bundle(pv_config_path, sample_station_state):
    """Req 1: Adapter constructs a valid ForecastBundle."""
    engine = Stage81ForecastEngine(pv_config_path)
    assert isinstance(engine, ForecastEngine)
    bundle = engine.predict(sample_station_state, {})
    assert isinstance(bundle, ForecastBundle)
    assert bundle.schema_version == "1.0.0"


def test_2_24_hourly_timestamps_preserved(pv_config_path, sample_station_state):
    """Req 2: 24 hourly timestamps are preserved and monotonic."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})
    assert len(bundle.timestamps) == 24
    assert bundle.horizon_hours == 24
    assert bundle.timestamps[0] == "2026-09-18T07:00:00Z"
    assert bundle.timestamps[23] == "2026-09-19T06:00:00Z"


def test_3_sw_in_point_forecast_represented(pv_config_path, sample_station_state):
    """Req 3: SW_IN point forecast is represented correctly in solar_irradiance."""
    engine = Stage81ForecastEngine(pv_config_path)
    custom_sw_in = [float(i * 30) for i in range(24)]
    runtime_context = {"stage81_sw_in_forecast": custom_sw_in}
    bundle = engine.predict(sample_station_state, runtime_context)

    assert bundle.solar_irradiance.unit == "W/m^2"
    assert bundle.solar_irradiance.point == custom_sw_in


def test_4_degenerate_interval_bounds(pv_config_path, sample_station_state):
    """Req 4: lower == point == upper for both solar_irradiance and solar_generation."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})

    for i in range(24):
        assert bundle.solar_irradiance.lower[i] == bundle.solar_irradiance.point[i] == bundle.solar_irradiance.upper[i]
        assert bundle.solar_generation.lower[i] == bundle.solar_generation.point[i] == bundle.solar_generation.upper[i]


def test_5_d3_solar_generation_mapping(pv_config_path, sample_station_state):
    """Req 5: solar-generation transformation follows frozen D3 mapping (SW_IN * 51.0)."""
    engine = Stage81ForecastEngine(pv_config_path)
    custom_sw_in = [100.0, 200.0, 500.0] + [0.0]*21
    bundle = engine.predict(sample_station_state, {"stage81_sw_in_forecast": custom_sw_in})

    # 100 * 300 * 0.20 * 0.85 = 5100.0 W
    assert bundle.solar_generation.point[0] == pytest.approx(5100.0, abs=1e-2)
    # 200 * 51 = 10200.0 W
    assert bundle.solar_generation.point[1] == pytest.approx(10200.0, abs=1e-2)
    # 500 * 51 = 25500.0 W
    assert bundle.solar_generation.point[2] == pytest.approx(25500.0, abs=1e-2)


def test_6_inverter_60kw_clipping(pv_config_path, sample_station_state):
    """Req 6: 60 kW clipping is preserved."""
    engine = Stage81ForecastEngine(pv_config_path)
    # 1500 W/m^2 * 51 = 76,500 W -> clipped to 60,000 W
    custom_sw_in = [1500.0]*24
    bundle = engine.predict(sample_station_state, {"stage81_sw_in_forecast": custom_sw_in})

    for val in bundle.solar_generation.point:
        assert val == 60000.0


def test_7_non_negativity_preserved(pv_config_path, sample_station_state):
    """Req 7: non-negativity is preserved."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})

    for irr in bundle.solar_irradiance.point:
        assert irr >= 0.0
    for gen in bundle.solar_generation.point:
        assert gen >= 0.0


def test_8_forecast_bundle_validation_succeeds(pv_config_path, sample_station_state):
    """Req 8: ForecastBundle validation succeeds."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})
    assert validate_stage81_solar_metadata(bundle) is True


def test_9_metadata_provenance_present_and_consistent(pv_config_path, sample_station_state):
    """Req 9: metadata/provenance is present and internally consistent."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})

    assert STAGE8_1_PROVENANCE_KEY in bundle.metadata
    prov = bundle.metadata[STAGE8_1_PROVENANCE_KEY]
    assert prov["model_identity"] == "stage8_1_histgradientboosting_37_features"
    assert prov["target"] == "SW_IN"
    assert prov["unit"] == "W/m^2"
    assert prov["horizon_hours"] == 24
    assert prov["pv_transformation"]["max_inverter_power_w"] == 60000.0


def test_10_deterministic_repeated_execution(pv_config_path, sample_station_state):
    """Req 10: deterministic repeated execution produces equivalent outputs."""
    engine = Stage81ForecastEngine(pv_config_path)
    runtime_context = {"stage81_sw_in_forecast": [300.0]*24}

    bundle_1 = engine.predict(sample_station_state, runtime_context)
    bundle_2 = engine.predict(sample_station_state, runtime_context)

    assert bundle_1.solar_irradiance.point == bundle_2.solar_irradiance.point
    assert bundle_1.solar_generation.point == bundle_2.solar_generation.point
    assert bundle_1.timestamps == bundle_2.timestamps


def test_11_serialization_deserialization(pv_config_path, sample_station_state):
    """Req 11: serialization/deserialization preserves the bundle."""
    engine = Stage81ForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})

    json_str = bundle.to_json()
    dict_data = json.loads(json_str)
    reconstituted = ForecastBundle.from_dict(dict_data)

    assert reconstituted.schema_version == "1.0.0"
    assert reconstituted.solar_irradiance.point == bundle.solar_irradiance.point
    assert reconstituted.solar_generation.point == bundle.solar_generation.point
    assert STAGE8_1_PROVENANCE_KEY in reconstituted.metadata


def test_12_causality_preserved_no_future_truth(pv_config_path, sample_station_state):
    """Req 12: future truth is not required by the adapter."""
    engine = Stage81ForecastEngine(pv_config_path)
    # Empty context relies solely on station_state at t0
    bundle = engine.predict(sample_station_state, {})
    assert bundle.origin_timestamp == sample_station_state.timestamp
    assert len(bundle.solar_generation.point) == 24
    assert bundle.metadata[STAGE8_1_PROVENANCE_KEY]["causality_preserved"] is True
