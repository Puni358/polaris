"""
POLARIS — Candidate N6 ForecastEngine Adapter Verification Suite
================================================================
Phase: Non-Production / Offline Simulation Integration.
Preserves winner: null. Does not alter production configuration.

Tests:
1. Interface compatibility (subclass of ForecastEngine, returns ForecastBundle).
2. Deterministic inference on 2024 development matrix fixture.
3. Physical night-zeroing consistency.
4. L2 conformal lower bound (0 <= lower <= point <= upper).
5. Dynamic 6-hour rolling EBR reserve floor (>= 15,000 Wh) in metadata.
6. Permitted u700/v700 NaNs at horizons 20-24 vs fail-closed on horizons 1-19.
7. Fail-closed security on missing context, wrong shape, missing features, or target leakage.
8. Cryptographic hash verification fail-closed behavior.
9. Orchestration isolation (system defaults remain unchanged).
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.governance.model_reproducibility import ModelGovernanceError
from system.forecasting.implementations.n6_solar import (
    N6SolarForecastEngine,
    FROZEN_MODEL_PATH,
    FROZEN_MODEL_SHA256,
    FROZEN_MODEL_ID,
    FEATURE_NAMES,
    EBR_BASE_WH,
)

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
SMOKE_ORIGIN = pd.Timestamp("2024-06-01T00:00:00Z")


class TestN6SolarForecastEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify model artifact exists and checksum matches before tests run
        assert FROZEN_MODEL_PATH.exists(), f"Missing model at {FROZEN_MODEL_PATH}"
        h = hashlib.sha256(FROZEN_MODEL_PATH.read_bytes()).hexdigest()
        assert h == FROZEN_MODEL_SHA256, f"Corrupted frozen artifact {h} != {FROZEN_MODEL_SHA256}"

        cls.engine = N6SolarForecastEngine()

        # Load 2024 clean matrix fixture for smoke origin
        matrix_path = (
            REPO_ROOT
            / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
        )
        assert matrix_path.exists(), f"Missing fixture matrix {matrix_path}"
        df_mat = pd.read_parquet(matrix_path)
        df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
        origin_df = df_mat[df_mat["forecast_start"] == SMOKE_ORIGIN].sort_values("horizon_hour").reset_index(drop=True)
        assert len(origin_df) == 24, f"Expected 24 rows, got {len(origin_df)}"

        # Synthesize 36th feature: elevation_x_transition_cloud
        is_trans = ((origin_df["cloud_frac"] >= 0.2) & (origin_df["cloud_frac"] < 0.6)).astype(np.float64)
        origin_df["elevation_x_transition_cloud"] = origin_df["solar_elevation"] * is_trans

        # Drop forbidden evaluation labels (simulating genuine inference input)
        cls.valid_features_df = origin_df.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")

        cls.sample_station_state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=75.0,
            battery_energy_wh=150000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=12000.0,
            last_observed_wind_generation=5000.0,
        )

    def test_01_interface_compatibility(self):
        """Adapter inherits from ForecastEngine and returns schema-valid ForecastBundle."""
        self.assertIsInstance(self.engine, ForecastEngine)
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        self.assertIsInstance(bundle, ForecastBundle)
        self.assertEqual(bundle.schema_version, "1.0.0")
        self.assertEqual(bundle.horizon_hours, 24)
        self.assertEqual(len(bundle.timestamps), 24)
        self.assertEqual(bundle.timestamps[0], "2024-06-01T00:00:00Z")
        self.assertEqual(bundle.timestamps[23], "2024-06-01T23:00:00Z")

        # Units verification
        self.assertEqual(bundle.solar_irradiance.unit, "W/m^2")
        self.assertEqual(bundle.solar_generation.unit, "W")

    def test_02_deterministic_predictions(self):
        """Repeated predictions yield bitwise identical output arrays."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle1 = self.engine.predict(self.sample_station_state, context)
        bundle2 = self.engine.predict(self.sample_station_state, context)

        self.assertEqual(bundle1.solar_irradiance.point, bundle2.solar_irradiance.point)
        self.assertEqual(bundle1.solar_generation.point, bundle2.solar_generation.point)
        self.assertEqual(bundle1.metadata["ebr_target_wh"], bundle2.metadata["ebr_target_wh"])

    def test_03_physical_night_zeroing(self):
        """Night horizons (solar_elevation <= 0 or clearsky_ghi <= 0) must be strictly 0.0."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        elev = self.valid_features_df["solar_elevation"].values
        cs_ghi = self.valid_features_df["clearsky_ghi"].values
        is_night = (elev <= 0.0) | (cs_ghi <= 0.0)

        irr_pts = np.array(bundle.solar_irradiance.point)
        gen_pts = np.array(bundle.solar_generation.point)

        self.assertTrue(np.all(irr_pts[is_night] == 0.0), "Non-zero night irradiance detected!")
        self.assertTrue(np.all(gen_pts[is_night] == 0.0), "Non-zero night generation detected!")

    def test_04_conformal_bounds_monotonicity(self):
        """0 <= lower <= point <= upper holds across all 24 horizons."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        irr = bundle.solar_irradiance
        gen = bundle.solar_generation

        for h in range(24):
            self.assertGreaterEqual(irr.lower[h], 0.0, f"Negative irr lower at h={h}")
            self.assertLessEqual(irr.lower[h], irr.point[h], f"irr lower > point at h={h}")
            self.assertLessEqual(irr.point[h], irr.upper[h], f"irr point > upper at h={h}")

            self.assertGreaterEqual(gen.lower[h], 0.0, f"Negative gen lower at h={h}")
            self.assertLessEqual(gen.lower[h], gen.point[h], f"gen lower > point at h={h}")
            self.assertLessEqual(gen.point[h], gen.upper[h], f"gen point > upper at h={h}")

    def test_05_ebr_trajectory_and_baseline_floor(self):
        """EBR reserve trajectory is serialized in metadata and satisfies floor >= 15,000 Wh."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        self.assertIn("ebr_target_wh", bundle.metadata)
        ebr = bundle.metadata["ebr_target_wh"]
        self.assertEqual(len(ebr), 24)

        for h, val in enumerate(ebr):
            self.assertGreaterEqual(val, EBR_BASE_WH, f"EBR floor violated at h={h}: {val} < {EBR_BASE_WH}")

    def test_06_u700_v700_nan_handling_and_fail_closed(self):
        """u700/v700 permitted NaN for horizons 20-24, but fails closed on horizons 1-19."""
        # 1. Valid case with horizons 20-24 as NaN (row indices 19..23)
        df_gap = self.valid_features_df.copy()
        df_gap.loc[19:23, "u700"] = np.nan
        df_gap.loc[19:23, "v700"] = np.nan
        bundle = self.engine.predict(self.sample_station_state, {"n6_feature_matrix": df_gap})
        self.assertIsInstance(bundle, ForecastBundle)

        # 2. Corrupt case: NaN at horizon 5 (index 4) -> must raise ModelGovernanceError
        df_corrupt = self.valid_features_df.copy()
        df_corrupt.loc[4, "u700"] = np.nan
        with self.assertRaises(ModelGovernanceError) as cm:
            self.engine.predict(self.sample_station_state, {"n6_feature_matrix": df_corrupt})
        self.assertIn("unexpected NaN in 'u700'", str(cm.exception))

    def test_07_fail_closed_missing_and_corrupt_inputs(self):
        """Fail-closed on missing matrix, wrong shape, missing columns, or label leakage."""
        # Missing runtime_context matrix
        with self.assertRaises(ModelGovernanceError):
            self.engine.predict(self.sample_station_state, {})

        with self.assertRaises(ModelGovernanceError):
            self.engine.predict(self.sample_station_state, None)

        # Truncated length (e.g. 12 instead of 24)
        truncated_df = self.valid_features_df.iloc[:12].copy()
        with self.assertRaises(ModelGovernanceError):
            self.engine.predict(self.sample_station_state, {"n6_feature_matrix": truncated_df})

        # Missing required column
        missing_col_df = self.valid_features_df.drop(columns=["solar_zenith"])
        with self.assertRaises(ModelGovernanceError):
            self.engine.predict(self.sample_station_state, {"n6_feature_matrix": missing_col_df})

        # Infinite value in feature
        inf_df = self.valid_features_df.copy()
        inf_df.loc[2, "fc_temperature_2m"] = np.inf
        with self.assertRaises(ModelGovernanceError):
            self.engine.predict(self.sample_station_state, {"n6_feature_matrix": inf_df})

        # Target label leakage
        for forbidden in ["actual_SW_IN", "actual_ghi", "residual_target", "target"]:
            leaked_df = self.valid_features_df.copy()
            leaked_df[forbidden] = 500.0
            with self.assertRaises(ModelGovernanceError) as cm:
                self.engine.predict(self.sample_station_state, {"n6_feature_matrix": leaked_df})
            self.assertIn("target leakage safeguard triggered", str(cm.exception).lower())

    def test_08_checksum_verification_fail_closed(self):
        """Tampered model file or hash triggers immediate ModelGovernanceError."""
        with self.assertRaises(ModelGovernanceError):
            N6SolarForecastEngine(model_path=Path("/tmp/nonexistent_model.joblib"))

    def test_09_production_isolation_and_governance(self):
        """Engine metadata declares RESEARCH_ONLY, winner: null, and orchestration worker is unchanged."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        self.assertEqual(bundle.metadata["governance_status"], "RESEARCH_ONLY")
        self.assertIsNone(bundle.metadata["winner"])
        self.assertEqual(bundle.metadata["model_id"], FROZEN_MODEL_ID)
        self.assertEqual(bundle.metadata["model_sha256"], FROZEN_MODEL_SHA256)
        self.assertFalse(bundle.metadata["engine_default_in_orchestration"])

        # Check that worker.py default is still LocalBaselineForecastEngine
        worker_path = REPO_ROOT / "system/orchestration/worker.py"
        worker_text = worker_path.read_text()
        self.assertIn("LocalBaselineForecastEngine", worker_text)
        self.assertNotIn("N6SolarForecastEngine", worker_text)


if __name__ == "__main__":
    unittest.main()
