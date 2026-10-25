"""
POLARIS — N6 Decomposition Parity & Isolated-Operation Test Suite
===================================================================
N6 Operational Readiness Remediation, Section 2.7.

Background: `N6SolarForecastEngine.predict()` previously computed point
prediction, ensemble-uncertainty/conformal-bound, and EBR reserve-trajectory
math inline in one undifferentiated block, making each operation impossible
to unit test in isolation. The remediation extracted three pure helper
methods -- `_compute_point_prediction`, `_compute_uncertainty_bounds`, and
`_compute_ebr_reserve` -- WITHOUT changing any arithmetic, ordering, model
weights, or calibration constants.

This suite proves two things:
1. PARITY: the decomposed call sequence used inside `predict()` reproduces
   bit-identical output to direct, independent invocation of the three
   helper methods on the same fixture (i.e. the refactor introduced no
   numerical drift).
2. ISOLATION: each of the three operations is independently callable and
   testable with synthetic, non-production inputs, without needing to run
   the full 40-member ensemble bundle for the uncertainty/EBR stages.

GOVERNANCE: Read-only / non-production test. Does not modify the frozen
model bundle, weights, blend parameters, or calibration constants. Does not
alter `winner: null` or production orchestration defaults.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from system.schemas.station_state import StationState
from system.forecasting.implementations.n6_solar import (
    N6SolarForecastEngine,
    FROZEN_MODEL_PATH,
    FROZEN_MODEL_SHA256,
    FEATURE_NAMES,
    EBR_BASE_WH,
    Q_HAT_NORM,
    Q90_W,
)

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
SMOKE_ORIGIN = pd.Timestamp("2024-06-01T00:00:00Z")


class TestN6DecompositionParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert FROZEN_MODEL_PATH.exists(), f"Missing model at {FROZEN_MODEL_PATH}"
        h = hashlib.sha256(FROZEN_MODEL_PATH.read_bytes()).hexdigest()
        assert h == FROZEN_MODEL_SHA256, f"Corrupted frozen artifact {h} != {FROZEN_MODEL_SHA256}"

        cls.engine = N6SolarForecastEngine()

        matrix_path = (
            REPO_ROOT
            / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
        )
        assert matrix_path.exists(), f"Missing fixture matrix {matrix_path}"
        df_mat = pd.read_parquet(matrix_path)
        df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
        origin_df = df_mat[df_mat["forecast_start"] == SMOKE_ORIGIN].sort_values("horizon_hour").reset_index(drop=True)
        assert len(origin_df) == 24, f"Expected 24 rows, got {len(origin_df)}"

        is_trans = ((origin_df["cloud_frac"] >= 0.2) & (origin_df["cloud_frac"] < 0.6)).astype(np.float64)
        origin_df["elevation_x_transition_cloud"] = origin_df["solar_elevation"] * is_trans

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

    def _manually_recompute_via_helpers(self):
        """Directly invokes the three decomposed helper methods, independent of predict()."""
        feature_df = self.engine._validate_feature_matrix(self.valid_features_df)
        X_df = feature_df[FEATURE_NAMES]
        st4 = feature_df["pred_stage4_clean"].to_numpy(dtype=np.float64)
        cs_terrain = feature_df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
        cs_ghi = feature_df["clearsky_ghi"].to_numpy(dtype=np.float64)
        elev = feature_df["solar_elevation"].to_numpy(dtype=np.float64)
        shaded = feature_df["terrain_solar_obstruction_flag"].to_numpy(dtype=np.int64)

        point_result = self.engine._compute_point_prediction(X_df, st4, cs_terrain, cs_ghi, elev, shaded)
        unc_result = self.engine._compute_uncertainty_bounds(
            point_result["y_pred"],
            point_result["preds_add"],
            point_result["preds_kt"],
            point_result["causal_day_mask"],
            cs_terrain,
        )
        ebr_target_wh = self.engine._compute_ebr_reserve(unc_result["scale_s"])
        return point_result, unc_result, ebr_target_wh

    def test_01_parity_point_prediction_matches_full_predict(self):
        """Isolated _compute_point_prediction output matches predict()'s solar_irradiance.point exactly."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        point_result, _, _ = self._manually_recompute_via_helpers()
        expected = [float(round(v, 4)) for v in point_result["y_pred"]]

        np.testing.assert_array_equal(np.array(bundle.solar_irradiance.point), np.array(expected))

    def test_02_parity_uncertainty_bounds_match_full_predict(self):
        """Isolated _compute_uncertainty_bounds output matches predict()'s lower/upper exactly."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        point_result, unc_result, _ = self._manually_recompute_via_helpers()
        y_pred = point_result["y_pred"]
        y_lower = unc_result["y_lower"]
        y_upper = unc_result["y_upper"]

        expected_lower = [float(round(v, 4)) for v in y_lower]
        expected_upper = [float(round(v, 4)) for v in y_upper]
        # predict() clamps lower<=point<=upper as a final monotonicity guarantee;
        # replicate that same guarantee here before comparing (identical to predict()'s own logic).
        expected_pts = [float(round(v, 4)) for v in y_pred]
        for i in range(24):
            expected_lower[i] = min(expected_lower[i], expected_pts[i])
            expected_upper[i] = max(expected_upper[i], expected_pts[i])

        np.testing.assert_array_equal(np.array(bundle.solar_irradiance.lower), np.array(expected_lower))
        np.testing.assert_array_equal(np.array(bundle.solar_irradiance.upper), np.array(expected_upper))

    def test_03_parity_ebr_reserve_matches_full_predict(self):
        """Isolated _compute_ebr_reserve output matches predict()'s metadata['ebr_target_wh'] exactly."""
        context = {"n6_feature_matrix": self.valid_features_df}
        bundle = self.engine.predict(self.sample_station_state, context)

        _, _, ebr_target_wh = self._manually_recompute_via_helpers()

        self.assertEqual(bundle.metadata["ebr_target_wh"], ebr_target_wh)

    def test_04_point_prediction_isolated_from_uncertainty_and_ebr(self):
        """
        _compute_point_prediction can be called and asserted on WITHOUT ever computing
        uncertainty bounds or EBR reserve -- proving true separation of concerns.
        """
        feature_df = self.engine._validate_feature_matrix(self.valid_features_df)
        X_df = feature_df[FEATURE_NAMES]
        st4 = feature_df["pred_stage4_clean"].to_numpy(dtype=np.float64)
        cs_terrain = feature_df["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
        cs_ghi = feature_df["clearsky_ghi"].to_numpy(dtype=np.float64)
        elev = feature_df["solar_elevation"].to_numpy(dtype=np.float64)
        shaded = feature_df["terrain_solar_obstruction_flag"].to_numpy(dtype=np.int64)

        result = self.engine._compute_point_prediction(X_df, st4, cs_terrain, cs_ghi, elev, shaded)
        self.assertIn("y_pred", result)
        self.assertIn("causal_day_mask", result)
        self.assertEqual(len(result["y_pred"]), 24)
        # Night hours must be exactly zero (causal day mask applied within this operation alone).
        is_night = ~result["causal_day_mask"]
        self.assertTrue(np.all(result["y_pred"][is_night] == 0.0))

    def test_05_uncertainty_bounds_isolated_with_synthetic_inputs(self):
        """
        _compute_uncertainty_bounds is callable with purely synthetic (non-production,
        non-ensemble) arrays -- proving it needs no live model bundle to unit test.
        """
        causal_day_mask = np.array([True] * 12 + [False] * 12)
        y_pred = np.where(causal_day_mask, 300.0, 0.0)
        preds_add = np.tile(y_pred, (25, 1)) + np.random.default_rng(0).normal(0, 5, size=(25, 24))
        preds_kt = np.tile(y_pred, (15, 1)) + np.random.default_rng(1).normal(0, 5, size=(15, 24))
        cs_terrain = np.full(24, 400.0)

        result = N6SolarForecastEngine._compute_uncertainty_bounds(
            y_pred, preds_add, preds_kt, causal_day_mask, cs_terrain
        )
        self.assertTrue(np.all(result["y_lower"][~causal_day_mask] == 0.0))
        self.assertTrue(np.all(result["y_upper"][~causal_day_mask] == 0.0))
        self.assertTrue(np.all(result["y_lower"][causal_day_mask] <= y_pred[causal_day_mask]))

    def test_06_ebr_reserve_isolated_with_synthetic_scale(self):
        """
        _compute_ebr_reserve is callable with a purely synthetic scale_s array
        (e.g. the known Arm A_FIX low-solar/high-uncertainty failure-mode shape)
        without needing point prediction or the ensemble bundle at all.
        """
        # High uncertainty synthetic scenario (low-solar / high-ramp conditions)
        scale_s_high_unc = np.full(24, 500.0)
        ebr_high = self.engine._compute_ebr_reserve(scale_s_high_unc)
        self.assertEqual(len(ebr_high), 24)
        for v in ebr_high:
            self.assertGreaterEqual(v, EBR_BASE_WH)

        # Zero-uncertainty scenario must still respect the EBR floor.
        scale_s_zero = np.zeros(24)
        ebr_floor = self.engine._compute_ebr_reserve(scale_s_zero)
        for v in ebr_floor:
            self.assertEqual(v, EBR_BASE_WH)

        # Higher uncertainty must never produce a LOWER reserve requirement.
        for h in range(24):
            self.assertGreaterEqual(ebr_high[h], ebr_floor[h])


if __name__ == "__main__":
    unittest.main()
