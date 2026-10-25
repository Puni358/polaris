"""
Executable Pytest Suite for POLARIS Solar Forecast Branch 01 Implementation
Covers all 20 required implementation test areas using TEST_ONLY mock fixtures.
"""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.timestamp_normalizer import TimestampNormalizer
from forecasting.solar_branch_01.implementation.source_validator import SourceValidator
from forecasting.solar_branch_01.implementation.hash_generator import HashGenerator
from forecasting.solar_branch_01.implementation.target_builder import TargetBuilder
from forecasting.solar_branch_01.implementation.origin_generator import OriginGenerator
from forecasting.solar_branch_01.implementation.nwp_selector import NWPSelector
from forecasting.solar_branch_01.implementation.nwp_lead_mapper import NWPLeadMapper
from forecasting.solar_branch_01.implementation.astronomical_features import AstronomicalFeatureBuilder
from forecasting.solar_branch_01.implementation.lookback_features import LookbackFeatureBuilder
from forecasting.solar_branch_01.implementation.clearsky_features import ClearSkyFeatureBuilder
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder
from forecasting.solar_branch_01.implementation.split_builder import SplitBuilder
from forecasting.solar_branch_01.implementation.baseline_interface import PersistenceBaseline, ClearSkyRatioBaseline
from forecasting.solar_branch_01.implementation.model_interface import TestOnlyMockModel
from forecasting.solar_branch_01.implementation.preprocessing_interface import PreprocessingInterface
from forecasting.solar_branch_01.implementation.model_serializer import ModelSerializer
from forecasting.solar_branch_01.implementation.manifest_generator import ManifestGenerator
from forecasting.solar_branch_01.implementation.replay_runner import IsolatedReplayRunner
from forecasting.solar_branch_01.implementation.evaluation_interface import EvaluationInterface
from forecasting.solar_branch_01.implementation.governance_integration import GovernanceIntegration

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")

def test_01_timestamp_normalization():
    s = pd.Series(["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z", "2024-01-01T02:00:00Z"])
    norm = TimestampNormalizer.normalize_series(s)
    assert len(norm) == 3
    assert norm.is_monotonic_increasing

    with pytest.raises(ModelGovernanceError):
        # Out-of-order timestamps fail closed
        TimestampNormalizer.normalize_series(pd.Series(["2024-01-01T02:00:00Z", "2024-01-01T01:00:00Z"]))

def test_02_source_validator():
    sites_path = BASE_DIR / "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
    df = SourceValidator.validate_csv_source(sites_path, ["timestamp", "SW_IN"], min_rows=8700)
    assert len(df) >= 8700

    with pytest.raises(ModelGovernanceError):
        SourceValidator.validate_csv_source(sites_path, ["missing_column_foo"])

def test_03_target_builder():
    sw_series = pd.Series(np.arange(100, dtype=np.float64))
    y_vec = TargetBuilder.build_target_vector(sw_series, 10)
    assert len(y_vec) == 24
    assert y_vec[0] == 11.0
    assert y_vec[-1] == 34.0

    with pytest.raises(ModelGovernanceError):
        TargetBuilder.build_target_vector(sw_series, 90)

def test_04_origin_generator():
    dates = pd.date_range("2024-01-01", periods=100, freq="1h", tz="UTC")
    df = pd.DataFrame({"timestamp": dates})
    og = OriginGenerator(lookback_hours=24, target_hours=24)
    origins = og.derive_supported_origins(df)
    assert len(origins) == 100 - 48

def test_05_nwp_selector():
    origin = datetime(2024, 6, 1, 6, 0, tzinfo=timezone.utc)
    issue1 = datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    issue2 = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    selected = NWPSelector.select_latest_valid_issue(origin, [issue1, issue2])
    assert selected == issue1

    with pytest.raises(ModelGovernanceError):
        NWPSelector.select_latest_valid_issue(origin, [issue2])

def test_06_nwp_lead_mapper():
    origin = datetime(2024, 6, 1, 6, 0, tzinfo=timezone.utc)
    issue = datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    eff_lead = NWPLeadMapper.calculate_effective_lead(origin, issue, horizon_step=1)
    assert eff_lead == 7

def test_07_nwp_coverage_assertion():
    # Verify lead mapping bounds
    origin = datetime(2024, 6, 1, 18, 0, tzinfo=timezone.utc)
    issue = datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    max_lead = NWPLeadMapper.calculate_effective_lead(origin, issue, horizon_step=24)
    assert max_lead == 42

def test_08_astronomical_features():
    dt = datetime(2024, 6, 21, 12, 0, tzinfo=timezone.utc)
    astro = AstronomicalFeatureBuilder.compute_features(dt)
    assert "solar_elevation" in astro
    assert "solar_zenith" in astro
    assert astro["solar_elevation"] > 0.0

def test_09_lookback_features():
    sw_series = pd.Series(np.arange(50, dtype=np.float64))
    feats = LookbackFeatureBuilder.compute_features(sw_series, origin_idx=30)
    assert "sw_in_lag_0h" in feats
    assert feats["sw_in_lag_0h"] == 30.0
    assert feats["sw_in_lag_1h"] == 29.0

def test_10_clearsky_features():
    dt = pd.Timestamp("2024-01-01T00:00:00Z")
    df = pd.DataFrame({"timestamp": [dt], "clearsky_sw_in": [123.4]})
    cs = ClearSkyFeatureBuilder.compute_features(df, dt)
    assert cs["clearsky_sw_in_origin"] == 123.4

def test_11_feature_matrix_builder():
    assert len(FeatureMatrixBuilder.ORDERED_FEATURE_NAMES) == 18

def test_12_split_builder():
    dates = pd.date_range("2024-01-01", "2024-12-31 23:00:00", freq="1h", tz="UTC")
    df_x = pd.DataFrame({"feat": np.zeros(len(dates))})
    df_y = pd.DataFrame({"target": np.zeros(len(dates))})
    splits = SplitBuilder.apply_split(dates, df_x, df_y)
    assert "train" in splits
    assert "validation" in splits
    assert "test" in splits

def test_13_baseline_interfaces():
    pb = PersistenceBaseline()
    pred = pb.predict_origin(pd.Timestamp("2024-01-01T00:00:00Z"), np.array([10.0, 20.0]), np.array([50.0]*25))
    assert len(pred) == 24
    assert pred[0] == 20.0

def test_14_model_interface_mock():
    model = TestOnlyMockModel()
    assert not model.is_fitted
    model.fit(pd.DataFrame({"clearsky_sw_in_origin": [10.0]}), np.zeros((1, 24)))
    assert model.is_fitted
    pred = model.predict(pd.DataFrame({"clearsky_sw_in_origin": [100.0]}))
    assert pred.shape == (1, 24)
    assert pred[0, 0] == 50.0

def test_15_preprocessing_interface():
    scaler = PreprocessingInterface()
    assert not scaler.is_fitted
    df_train = pd.DataFrame({"f1": [1.0, 2.0, 3.0]})
    scaled = scaler.fit_transform(df_train)
    assert scaler.is_fitted
    assert scaled.shape == (3, 1)

def test_16_sha256_hash_generator():
    b_hash = HashGenerator.compute_bytes_sha256(b"hello world")
    assert len(b_hash) == 64

def test_17_model_serialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        model = TestOnlyMockModel()
        model.fit(pd.DataFrame({"clearsky_sw_in_origin": [10.0]}), np.zeros((1, 24)))
        save_path = Path(tmpdir) / "test_model.joblib"
        sha = ModelSerializer.save_model(model, save_path)
        assert len(sha) == 64

        loaded = ModelSerializer.load_model(TestOnlyMockModel, save_path, expected_sha256=sha)
        assert loaded.is_fitted

def test_18_manifest_generator():
    data = {f: "val" for f in ManifestGenerator.REQUIRED_FIELDS}
    manifest = ManifestGenerator.build_manifest(data)
    assert manifest["branch_id"] == "val"

def test_19_replay_runner():
    with tempfile.TemporaryDirectory() as tmpdir:
        model = TestOnlyMockModel()
        model.fit(pd.DataFrame({"clearsky_sw_in_origin": [10.0]}), np.zeros((1, 24)))
        save_path = Path(tmpdir) / "test_model.joblib"
        sha = ModelSerializer.save_model(model, save_path)

        X_test = pd.DataFrame({"clearsky_sw_in_origin": [100.0]})
        preds = model.predict(X_test)
        pred_hash = HashGenerator.compute_bytes_sha256(preds.tobytes())

        runner = IsolatedReplayRunner()
        result = runner.verify_replay(save_path, X_test, pred_hash)
        assert result["replay_status"] == "REPRODUCIBLE"

def test_20_governance_integration_and_firewall():
    gov = GovernanceIntegration()
    run_ctx = gov.create_governed_run("RUN_TEST_001")
    assert run_ctx["run_id"] == "RUN_TEST_001"

    s81_path = BASE_DIR / "system/forecasting/implementations/s81_solar.py"
    assert s81_path.exists()
    s81_hash = HashGenerator.compute_file_sha256(s81_path)
    assert len(s81_hash) == 64
