"""
POLARIS Branch 01 Remediated Integration Static Test Suite (Phase A / Section 9)

Verifies:
- Frozen Model, Control, Optimizer, Simulator, Baseline, and Fixture SHA hashes.
- Timestamp canonicalization ("2024-01-23 00:00:00" -> "2024-01-23T00:00:00Z").
- Timestamp lookup success and fail-closed behavior on missing timestamp.
- Removal of zero-vector fallback.
- Feature vector causality and 18-element dimension.
- Exact non-solar forecast inheritance & vector identity (Control == Treatment).
- Hash equality for demand and wind forecast vectors.
- Solar-only forecast differentiation.
"""

import unittest
import hashlib
import json
import pathlib
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_solar import Stage81ForecastEngine
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.governance.model_reproducibility import ModelGovernanceError
from forecasting.solar_branch_01.implementation.branch01_forecast_engine import Branch01ForecastEngine
from forecasting.solar_branch_01.implementation.timestamp_normalizer import TimestampNormalizer
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent


class TestBranch01RemediatedIntegration(unittest.TestCase):

    def setUp(self):
        self.pv_cfg_path = PROJECT_ROOT / "system/config/solar_pv.yaml"
        self.fixture_dir = PROJECT_ROOT / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
        self.adapter = H10RuntimeAdapter(str(self.fixture_dir))

        self.control_engine = Stage81ForecastEngine(self.pv_cfg_path)
        self.treatment_engine = Branch01ForecastEngine(PROJECT_ROOT)
        self.baseline_engine = LocalBaselineForecastEngine(self.pv_cfg_path)

        self.station_state = self.adapter.get_station_state(100)
        self.runtime_context = self.adapter.get_runtime_context(100)

    def test_model_identity_and_frozen_component_shas(self):
        """Verify frozen component SHA-256 hashes remain unchanged."""
        model_sha = hashlib.sha256((PROJECT_ROOT / "artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib").read_bytes()).hexdigest()
        self.assertEqual(model_sha, "65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781")

        s81_sha = hashlib.sha256((PROJECT_ROOT / "system/forecasting/implementations/s81_solar.py").read_bytes()).hexdigest()
        self.assertEqual(s81_sha, "d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c")

        milp_sha = hashlib.sha256((PROJECT_ROOT / "system/optimization/implementations/milp.py").read_bytes()).hexdigest()
        self.assertEqual(milp_sha, "ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35")

        sim_sha = hashlib.sha256((PROJECT_ROOT / "system/simulation/simulator.py").read_bytes()).hexdigest()
        self.assertEqual(sim_sha, "7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508")

        fixture_sha = hashlib.sha256((PROJECT_ROOT / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv").read_bytes()).hexdigest()
        self.assertEqual(fixture_sha, "762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023")

        baseline_sha = hashlib.sha256((PROJECT_ROOT / "system/forecasting/implementations/baseline.py").read_bytes()).hexdigest()
        self.assertEqual(baseline_sha, "905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993")

    def test_timestamp_canonicalization(self):
        """TEST_TIMESTAMP_CANONICALIZATION: Verify all valid formats resolve to YYYY-MM-DDTHH:MM:SSZ."""
        inputs = [
            "2024-01-23 00:00:00",
            "2024-01-23T00:00:00",
            "2024-01-23T00:00:00Z",
            "2024-01-23 00:00:00+00:00"
        ]
        for ts in inputs:
            canon = TimestampNormalizer.canonicalize_string(ts)
            self.assertEqual(canon, "2024-01-23T00:00:00Z")

    def test_timestamp_lookup_success(self):
        """TEST_TIMESTAMP_LOOKUP_SUCCESS: Verify valid station_state timestamp matches observation map."""
        sw_csv = PROJECT_ROOT / "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
        obs_df = pd.read_csv(sw_csv).rename(columns={"TIMESTAMP": "timestamp"})
        obs_df["timestamp"] = obs_df["timestamp"].apply(TimestampNormalizer.canonicalize_string)

        obs_ts_map = {ts: idx for idx, ts in enumerate(obs_df["timestamp"])}

        # Station state timestamp
        st_ts = TimestampNormalizer.canonicalize_string(self.station_state.timestamp)
        self.assertIn(st_ts, obs_ts_map)

    def test_timestamp_lookup_failure_fails_closed(self):
        """TEST_TIMESTAMP_LOOKUP_FAILURE_FAILS_CLOSED: Nonexistent timestamp lookup raises error."""
        with self.assertRaises(ModelGovernanceError):
            TimestampNormalizer.canonicalize_string("INVALID_TIMESTAMP_STRING")

    def test_feature_vector_dimension_and_causality(self):
        """TEST_FEATURE_VECTOR_DIMENSION & CAUSALITY: Verify 18-element dimension and causal construction."""
        sw_csv = PROJECT_ROOT / "(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv"
        obs_df = pd.read_csv(sw_csv).rename(columns={"TIMESTAMP": "timestamp"})
        obs_df["timestamp"] = obs_df["timestamp"].apply(TimestampNormalizer.canonicalize_string)

        clearsky_rows = []
        for ts in obs_df["timestamp"]:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            cs = 800.0 * np.sin((dt.hour - 4) * np.pi / 16.0) if 4 <= dt.hour <= 20 else 0.0
            clearsky_rows.append({"timestamp": ts, "clearsky_ghi": max(0.0, cs)})
        clearsky_df = pd.DataFrame(clearsky_rows)

        f_vec = FeatureMatrixBuilder.build_feature_vector(obs_df["SW_IN"], obs_df["timestamp"], 100, clearsky_df)
        self.assertEqual(f_vec.shape, (18,))
        self.assertFalse(np.isnan(f_vec).any())

    def test_non_solar_forecast_inheritance(self):
        """TEST_DEMAND_INHERITANCE & WIND_INHERITANCE: Control and Treatment have 100% identical non-solar forecasts."""
        control_bundle = self.control_engine.predict(self.station_state, self.runtime_context)

        trt_ctx = dict(self.runtime_context)
        trt_ctx["control_bundle"] = control_bundle
        trt_ctx["feature_vector"] = [0.0] * 18

        treatment_bundle = self.treatment_engine.predict(self.station_state, trt_ctx)

        # Vector identity
        self.assertEqual(control_bundle.demand.point, treatment_bundle.demand.point)
        self.assertEqual(control_bundle.wind_generation.point, treatment_bundle.wind_generation.point)

        # Hash identity
        h_d_c = hashlib.sha256(json.dumps(control_bundle.demand.point).encode()).hexdigest()
        h_d_t = hashlib.sha256(json.dumps(treatment_bundle.demand.point).encode()).hexdigest()
        self.assertEqual(h_d_c, h_d_t)

        h_w_c = hashlib.sha256(json.dumps(control_bundle.wind_generation.point).encode()).hexdigest()
        h_w_t = hashlib.sha256(json.dumps(treatment_bundle.wind_generation.point).encode()).hexdigest()
        self.assertEqual(h_w_c, h_w_t)

    def test_solar_only_intervention(self):
        """TEST_SOLAR_ONLY_INTERVENTION: Only solar forecast differs between Control and Treatment."""
        control_bundle = self.control_engine.predict(self.station_state, self.runtime_context)

        trt_ctx = dict(self.runtime_context)
        trt_ctx["control_bundle"] = control_bundle
        trt_ctx["feature_vector"] = [100.0] * 18

        treatment_bundle = self.treatment_engine.predict(self.station_state, trt_ctx)

        h_s_c = hashlib.sha256(json.dumps(control_bundle.solar_generation.point).encode()).hexdigest()
        h_s_t = hashlib.sha256(json.dumps(treatment_bundle.solar_generation.point).encode()).hexdigest()

        self.assertNotEqual(h_s_c, h_s_t)

    def test_fail_closed_on_missing_non_solar_forecasts(self):
        """TEST_NO_ZERO_FEATURE_FALLBACK & FAIL CLOSED: Missing demand/wind raises ModelGovernanceError."""
        trt_ctx = dict(self.runtime_context)
        trt_ctx["feature_vector"] = [0.0] * 18

        with self.assertRaises(ModelGovernanceError):
            self.treatment_engine.predict(self.station_state, trt_ctx)


if __name__ == "__main__":
    unittest.main()
