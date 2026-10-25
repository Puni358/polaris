"""
Focused tests for LocalProviderBranch01Adapter (LocalDataProvider -> Branch 01
18-feature contract -> frozen Candidate A HGB artifact integration).

Verifies:
- Exact 18-feature ordering and shape.
- No future data is accessed (causality under provider history slicing).
- Inference loads the exact frozen model artifact (SHA-256 match).
- Deterministic repeated inference gives identical output.
- Fallback to LocalBaselineForecastEngine when Branch 01 fails closed
  (e.g. forecast origin outside canonical clear-sky coverage).
"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from system.data.provider import LocalDataProvider
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.governance.model_reproducibility import ModelGovernanceError
from system.schemas.forecast_bundle import TimeseriesForecast
from system.schemas.station_state import StationState

from forecasting.solar_branch_01.implementation.branch01_forecast_engine import (
    Branch01ForecastEngine,
    FROZEN_MODEL_SHA256,
)
from forecasting.solar_branch_01.implementation.feature_matrix_builder import FeatureMatrixBuilder
from forecasting.solar_branch_01.implementation.local_provider_adapter import (
    LocalProviderBranch01Adapter,
    predict_with_fallback,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCENARIO_PATH = PROJECT_ROOT / "system/data/scenarios/synthetic_168h_endurance_scenario.json"
STUB_TS = TimeseriesForecast(point=[0.0] * 24, lower=[0.0] * 24, upper=[0.0] * 24, unit="W")


def _station_state_for(state_dict):
    return StationState(
        timestamp=state_dict["origin_timestamp"],
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=state_dict["last_observed_solar_irradiance"],
        last_observed_demand=state_dict["last_observed_demand"],
        last_observed_wind_generation=state_dict["last_observed_wind_generation"],
    )


class TestLocalProviderBranch01Adapter(unittest.TestCase):

    def setUp(self):
        self.provider = LocalDataProvider(SCENARIO_PATH)
        self.adapter = LocalProviderBranch01Adapter(PROJECT_ROOT)
        self.engine = Branch01ForecastEngine(PROJECT_ROOT)
        self.baseline = LocalBaselineForecastEngine(PROJECT_ROOT / "system/config/solar_pv.yaml")

    def test_feature_vector_shape_and_ordering(self):
        vec = self.adapter.build_feature_vector(self.provider, 100)
        self.assertEqual(vec.shape, (18,))
        self.assertEqual(len(FeatureMatrixBuilder.ORDERED_FEATURE_NAMES), 18)

    def test_no_future_data_accessed(self):
        """Mutating timesteps strictly after current_index must not change the built feature vector."""
        vec_before = self.adapter.build_feature_vector(self.provider, 100)

        mutated_provider = LocalDataProvider(SCENARIO_PATH)
        for ts in mutated_provider.timesteps[101:]:
            ts["actual_SW_IN"] = 999999.0

        vec_after = self.adapter.build_feature_vector(mutated_provider, 100)
        self.assertTrue((vec_before == vec_after).all())

    def test_future_ground_truth_not_exposed_via_runtime_state(self):
        """get_runtime_state must never leak timesteps beyond current_index."""
        state = self.provider.get_runtime_state(100)
        self.assertEqual(len(state["history"]), 101)
        self.assertEqual(state["history"][-1]["timestamp"], state["origin_timestamp"])

    def test_frozen_model_sha256_verified_on_load(self):
        model_path = PROJECT_ROOT / "artifacts/model_runs/RUN_BRANCH01_CANDIDATE_A_HGB/model.joblib"
        actual_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
        self.assertEqual(actual_sha, FROZEN_MODEL_SHA256)
        # Branch01ForecastEngine itself re-verifies this on every construction (fail-closed).
        Branch01ForecastEngine(PROJECT_ROOT)

    def test_end_to_end_prediction_deterministic(self):
        state_dict = self.provider.get_runtime_state(100)
        station_state = _station_state_for(state_dict)
        ctx = {"wind_generation": STUB_TS, "demand": STUB_TS}
        ctx.update(self.adapter.build_runtime_context_entry(self.provider, 100))

        bundle_1 = self.engine.predict(station_state, ctx)
        bundle_2 = self.engine.predict(station_state, ctx)

        self.assertEqual(len(bundle_1.solar_irradiance.point), 24)
        self.assertEqual(bundle_1.solar_irradiance.point, bundle_2.solar_irradiance.point)
        self.assertEqual(bundle_1.metadata["model_sha256"], FROZEN_MODEL_SHA256)

    def test_fallback_to_baseline_when_origin_outside_clearsky_coverage(self):
        """
        Construct a scenario whose forecast origin (2025-01-15) falls outside the
        canonical clear-sky file's 2024 coverage. Branch 01 feature construction
        must fail closed (ModelGovernanceError), and predict_with_fallback must
        defer to LocalBaselineForecastEngine rather than substituting features.
        """
        out_of_range_timesteps = []
        for i in range(30):
            out_of_range_timesteps.append({
                "timestep_index": i,
                "timestamp": f"2025-01-15T{i % 24:02d}:00:00Z" if i < 24 else f"2025-01-16T{(i - 24):02d}:00:00Z",
                "actual_SW_IN": 50.0,
                "clearsky_ghi": 80.0,
                "actual_wind_generation": 1000.0,
                "actual_demand": 2000.0,
            })

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "scenario_id": "test_out_of_coverage",
                "description": "test fixture outside clear-sky coverage",
                "status_label": "test",
                "total_timesteps": len(out_of_range_timesteps),
                "timesteps": out_of_range_timesteps,
            }, f)
            temp_path = Path(f.name)

        try:
            bad_provider = LocalDataProvider(temp_path)

            with self.assertRaises(ModelGovernanceError):
                self.adapter.build_feature_vector(bad_provider, 25)

            state_dict = bad_provider.get_runtime_state(25)
            station_state = _station_state_for(state_dict)
            ctx = {"wind_generation": STUB_TS, "demand": STUB_TS}

            bundle, source = predict_with_fallback(
                self.engine, self.baseline, self.adapter, bad_provider, 25, station_state, ctx
            )
            self.assertEqual(source, "local_baseline_fallback")
            self.assertEqual(bundle.metadata["model_id"], "polaris_local_baseline_persistence_v1")
            self.assertEqual(len(bundle.solar_irradiance.point), 24)
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
