"""
Unit and Integration Tests for POLARIS Option B Wind-Speed Forecast Engine Adapter
(WindSpeedARXForecastEngine) and Governed Metadata Transport.
"""

import json
from pathlib import Path
import pytest

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.forecasting.implementations.wind_arx import (
    WindSpeedARXForecastEngine,
    validate_wind_speed_metadata,
    WIND_SPEED_METADATA_KEY
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
        last_observed_wind_generation=0.0
    )


def test_forecast_engine_interface_compliance(pv_config_path):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    assert isinstance(engine, ForecastEngine)
    assert hasattr(engine, "predict")


def test_wind_speed_metadata_structure_and_validation(pv_config_path, sample_station_state):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    runtime_context = {"last_observed_wind_speed": 6.2}
    
    bundle = engine.predict(sample_station_state, runtime_context)
    
    assert WIND_SPEED_METADATA_KEY in bundle.metadata
    assert validate_wind_speed_metadata(bundle) is True
    
    meta = bundle.metadata[WIND_SPEED_METADATA_KEY]
    assert meta["quantity"] == "wind_speed"
    assert meta["unit"] == "m/s"
    assert meta["reference_height"] == "10m"
    assert meta["resolution"] == "hourly"
    assert meta["horizon_hours"] == 24
    assert meta["target_station"] == "SMHI Abisko Aut (188790)"
    assert meta["site_interpretation"] == "CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA"
    assert meta["direct_nuolja_measurement"] is False
    assert meta["model_id"] == "autoregressive_ridge_arx"
    assert meta["model_status"] == "VERIFIED_WITH_LIMITATIONS"


def test_24h_horizon_and_timestamps(pv_config_path, sample_station_state):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})
    
    meta = bundle.metadata[WIND_SPEED_METADATA_KEY]
    points = meta["point"]
    timestamps = meta["timestamps"]
    
    assert len(points) == 24
    assert len(timestamps) == 24
    assert all(p >= 0.0 for p in points)
    assert timestamps[0] == "2026-09-18T07:00:00Z"
    assert timestamps[23] == "2026-09-19T06:00:00Z"


def test_deterministic_execution(pv_config_path, sample_station_state):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    runtime_context = {"last_observed_wind_speed": 5.5, "nwp_wind_speed_forecast": [5.0]*24}
    
    bundle_1 = engine.predict(sample_station_state, runtime_context)
    bundle_2 = engine.predict(sample_station_state, runtime_context)
    
    meta_1 = bundle_1.metadata[WIND_SPEED_METADATA_KEY]
    meta_2 = bundle_2.metadata[WIND_SPEED_METADATA_KEY]
    
    assert meta_1["point"] == meta_2["point"]
    assert meta_1["timestamps"] == meta_2["timestamps"]


def test_json_serialization(pv_config_path, sample_station_state):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})
    
    bundle_dict = bundle.to_dict() if hasattr(bundle, "to_dict") else bundle.__dict__
    json_str = json.dumps(bundle_dict)
    reconstituted = json.loads(json_str)
    
    assert "metadata" in reconstituted
    assert WIND_SPEED_METADATA_KEY in reconstituted["metadata"]
    assert reconstituted["metadata"][WIND_SPEED_METADATA_KEY]["unit"] == "m/s"
    assert reconstituted["metadata"][WIND_SPEED_METADATA_KEY]["horizon_hours"] == 24


def test_top_level_forecastbundle_firewall(pv_config_path, sample_station_state):
    engine = WindSpeedARXForecastEngine(pv_config_path)
    bundle = engine.predict(sample_station_state, {})
    
    assert hasattr(bundle, "schema_version")
    assert bundle.schema_version == "1.0.0"
    assert not hasattr(bundle, "wind_speed")  # Schema v1.0.0 firewall
    assert hasattr(bundle, "wind_generation")  # Untouched wind_generation in Watts
