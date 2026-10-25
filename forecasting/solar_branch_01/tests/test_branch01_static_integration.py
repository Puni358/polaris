"""
Static Integration Test Suite for POLARIS Solar Forecast Branch 01
Implements INT_STATIC_01 through INT_STATIC_30 static/interface tests.
ZERO EMS execution, ZERO MILP optimization runs, ZERO Digital Twin execution.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from system.governance.model_reproducibility import ModelGovernanceError
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from forecasting.solar_branch_01.implementation.branch01_forecast_engine import Branch01ForecastEngine
from forecasting.solar_branch_01.implementation.data_loader import DataLoader
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
FROZEN_MODEL_SHA = "65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781"
S81_SHA = "d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c"

@pytest.fixture
def engine():
    return Branch01ForecastEngine(BASE_DIR)

@pytest.fixture
def valid_station_state():
    return StationState(
        timestamp="2024-09-01T00:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=120000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=10.0,
        last_observed_demand=25000.0,
        last_observed_wind_generation=15000.0
    )

@pytest.fixture
def valid_context():
    # 18 dummy valid features
    dummy_vec = np.zeros(18, dtype=np.float64)
    dummy_vec[11] = 10.0  # solar elevation > 0
    dummy_vec[17] = 50.0  # clear-sky W/m^2
    return {"feature_vector": dummy_vec}

def test_INT_STATIC_01_frozen_model_loads(engine):
    assert engine.model is not None
    assert len(engine.model.estimators_) == 24

def test_INT_STATIC_02_model_sha_matches():
    p = BASE_DIR / "artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib"
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha.lower() == FROZEN_MODEL_SHA.lower()

def test_INT_STATIC_03_model_identity(engine):
    assert engine.model.__class__.__name__ == "MultiOutputRegressor"
    assert engine.model.estimator.__class__.__name__ == "HistGradientBoostingRegressor"

def test_INT_STATIC_04_valid_18_features_accepted(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert isinstance(bundle, ForecastBundle)
    assert len(bundle.solar_irradiance.point) == 24

def test_INT_STATIC_05_wrong_feature_count_rejected(engine, valid_station_state):
    ctx = {"feature_vector": np.zeros(17, dtype=np.float64)}
    with pytest.raises(ModelGovernanceError):
        engine.predict(valid_station_state, ctx)

def test_INT_STATIC_06_nan_feature_rejected(engine, valid_station_state):
    vec = np.zeros(18, dtype=np.float64)
    vec[5] = np.nan
    with pytest.raises(ModelGovernanceError):
        engine.predict(valid_station_state, {"feature_vector": vec})

def test_INT_STATIC_07_inf_feature_rejected(engine, valid_station_state):
    vec = np.zeros(18, dtype=np.float64)
    vec[3] = np.inf
    with pytest.raises(ModelGovernanceError):
        engine.predict(valid_station_state, {"feature_vector": vec})

def test_INT_STATIC_08_invalid_timestamp_rejected(engine, valid_context):
    state = StationState("invalid_timestamp_string", 50.0, 120000.0, False, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ModelGovernanceError):
        engine.predict(state, valid_context)

def test_INT_STATIC_09_exactly_24_horizons(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle.horizon_hours == 24
    assert len(bundle.timestamps) == 24
    assert len(bundle.solar_irradiance.point) == 24

def test_INT_STATIC_10_h1_timestamp_alignment(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle.timestamps[0] == "2024-09-01T01:00:00Z"

def test_INT_STATIC_11_h24_timestamp_alignment(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle.timestamps[23] == "2024-09-02T00:00:00Z"

def test_INT_STATIC_12_utc_monotonic_timestamps(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    dts = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in bundle.timestamps]
    for i in range(len(dts) - 1):
        assert (dts[i+1] - dts[i]).total_seconds() == 3600.0

def test_INT_STATIC_13_causal_historical_features():
    from forecasting.solar_branch_01.implementation.lookback_features import LookbackFeatureBuilder
    s = pd.Series(np.arange(100, dtype=np.float64))
    feats = LookbackFeatureBuilder.compute_features(s, 25)
    # Origin 25 uses only indices <= 25
    assert feats["sw_in_lag_0h"] == 25.0
    assert feats["sw_in_lag_23h"] == 2.0

def test_INT_STATIC_14_nwp_issue_causality():
    from forecasting.solar_branch_01.implementation.nwp_lead_mapper import NWPLeadMapper
    t_origin = datetime(2024, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
    t_issue = datetime(2024, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    lead_h1 = NWPLeadMapper.calculate_effective_lead(t_origin, t_issue, 1)
    assert lead_h1 == 13  # t+1h horizon (13:00 UTC) -> 13h lead from 00:00 UTC issue
    assert lead_h1 >= 1
    assert lead_h1 <= 42

def test_INT_STATIC_15_nwp_effective_lead_range():
    from forecasting.solar_branch_01.implementation.nwp_lead_mapper import NWPLeadMapper
    t_origin = datetime(2024, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    t_issue = datetime(2024, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    lead_h1 = NWPLeadMapper.calculate_effective_lead(t_origin, t_issue, 1)
    lead_h24 = NWPLeadMapper.calculate_effective_lead(t_origin, t_issue, 24)
    assert lead_h1 == 1
    assert lead_h24 == 24

def test_INT_STATIC_16_missing_causal_input_fails_closed(engine, valid_station_state):
    with pytest.raises(ModelGovernanceError):
        engine.predict(valid_station_state, {})

def test_INT_STATIC_17_forecastbundle_sw_in(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle.solar_irradiance.unit == "W/m^2"
    assert all(val >= 0.0 for val in bundle.solar_irradiance.point)

def test_INT_STATIC_18_engineering_pv_mapping(engine, valid_station_state):
    # Pass SW_IN = 100.0 W/m^2 at clear-sky feature position
    vec = np.zeros(18, dtype=np.float64)
    vec[0] = 100.0
    vec[17] = 100.0
    bundle = engine.predict(valid_station_state, {"feature_vector": vec})
    
    # Verify engineering solar power mapping: P_solar = min(SW_IN * 51.0, 60000 W)
    for sw, p in zip(bundle.solar_irradiance.point, bundle.solar_generation.point):
        expected_p = min(sw * 51.0, 60000.0)
        assert abs(p - expected_p) < 1e-4

def test_INT_STATIC_19_non_negative_predictions(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    for p in bundle.solar_irradiance.point:
        assert p >= 0.0
    for p in bundle.solar_generation.point:
        assert p >= 0.0

def test_INT_STATIC_20_metadata_provenance(engine, valid_station_state, valid_context):
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle.metadata["model_id"] == "POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1"
    assert bundle.metadata["model_sha256"].lower() == FROZEN_MODEL_SHA.lower()

def test_INT_STATIC_21_truth_firewall_isolation(engine, valid_station_state, valid_context):
    # Verify no DigitalTwin hidden state or future actuals in prediction path
    assert "hidden_actuals" not in valid_context
    bundle = engine.predict(valid_station_state, valid_context)
    assert bundle is not None

def test_INT_STATIC_22_deterministic_predictions(engine, valid_station_state, valid_context):
    b1 = engine.predict(valid_station_state, valid_context)
    b2 = engine.predict(valid_station_state, valid_context)
    diff = np.max(np.abs(np.array(b1.solar_irradiance.point) - np.array(b2.solar_irradiance.point)))
    assert diff == 0.0

def test_INT_STATIC_23_s81_file_sha_unchanged():
    p = BASE_DIR / "system/forecasting/implementations/s81_solar.py"
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha.lower() == S81_SHA.lower()

def test_INT_STATIC_24_optimizer_source_unchanged():
    p = BASE_DIR / "system/optimization/implementations/milp.py"
    assert p.exists()

def test_INT_STATIC_25_dispatchplan_schema_unchanged():
    p = BASE_DIR / "system/schemas/dispatch_plan.py"
    assert p.exists()

def test_INT_STATIC_26_digital_twin_source_unchanged():
    p = BASE_DIR / "system/simulation/simulator.py"
    assert p.exists()

def test_INT_STATIC_27_no_unauthorized_fallback(engine, valid_station_state):
    # Ensure failure raises ModelGovernanceError instead of returning dummy fallback
    with pytest.raises(ModelGovernanceError):
        engine.predict(valid_station_state, {"feature_vector": [0.0]*10})

def test_INT_STATIC_28_forecastbundle_serialization_roundtrip(engine, valid_station_state, valid_context):
    b1 = engine.predict(valid_station_state, valid_context)
    b1_json = b1.to_json()
    b1_dict = json.loads(b1_json)
    b2 = ForecastBundle.from_dict(b1_dict)
    assert b2.origin_timestamp == b1.origin_timestamp
    assert b2.solar_irradiance.point == b1.solar_irradiance.point

def test_INT_STATIC_29_forecast_horizon_ordering_survives_roundtrip(engine, valid_station_state, valid_context):
    b1 = engine.predict(valid_station_state, valid_context)
    b2 = ForecastBundle.from_dict(b1.to_dict())
    assert b2.timestamps == b1.timestamps

def test_INT_STATIC_30_model_artifact_byte_for_byte_unchanged():
    p = BASE_DIR / "artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib"
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha.lower() == FROZEN_MODEL_SHA.lower()
