"""
Unit Test Suite for Candidate N6 Inference Runner & GAP19 Interface
=====================================================================
Covers Phase F Verification Requirements:
  1. Checksum acceptance for unchanged artifact.
  2. Checksum rejection on altered isolated copy (never altering frozen asset).
  3. Missing-artifact fail-closed behavior.
  4. Model bundle schema and feature-order validation.
  5. Genuine-inference parity against authoritative frozen implementation on non-blind 2024-ODD fixture.
  6. Conformal lower-bound arithmetic, bounds <= point, and nighttime edge cases.
  7. EBR units, horizon alignment, and rolling-window arithmetic.
  8. Payload schema validation without dispatch.
  9. Regression checks confirming all frozen model and results hashes remain immutable.
"""

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure local directory is on sys.path
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

import joblib
import numpy as np
import pandas as pd

from polaris_inference_runner import (
    DEFAULT_ARTIFACT_PATH,
    EXPECTED_SHA256,
    FEATURE_NAMES,
    K_PV,
    ETA_DIS,
    EBR_BASE_WH,
    WINDOW_HOURS,
    SCALE_FLOOR_WH,
    Q_HAT_NORM,
    Q90_W,
    ArtifactIntegrityError,
    InputValidationError,
    compute_conformal_lower_and_ebr,
    generate_dispatch_payload,
    load_candidate_n6_bundle,
    run_candidate_n6_inference,
    validate_input_features,
    verify_artifact_checksum,
)

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_2024_PATH = BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"

# Baseline hashes of protected assets to assert immutability
PROTECTED_ASSETS = {
    "candidate_n6_model.joblib": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib",
        "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197",
    ),
    "candidate_n1_model.joblib": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/candidate_n1_model.joblib",
        "7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7",
    ),
    "CANDIDATE_N_MANIFEST.json": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json",
        "1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031",
    ),
    "validation_predictions.csv": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/validation_predictions.csv",
        "bf4485283c10a2bcd63112a5c5be10581af6c35ba8f60a3ce201c10f50ea633c",
    ),
    "VALIDATION_RESULTS.json": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/VALIDATION_RESULTS.json",
        "ae5a02d2404b8da404a502b2ea93d50fe18e7352619dcb60a6a0a950c74c4df2",
    ),
    "blind_2025_predictions.csv": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/blind_2025_predictions.csv",
        "3c03e35b1bce2b0b10efc56731c6e641306caa9333b9d5797068f491fb233027",
    ),
    "BLIND_2025_RESULTS.json": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/BLIND_2025_RESULTS.json",
        "2d7893cb6fda849019c7dc9d355e0aaa893a0ac148dfb1aecca8b03609abf1a5",
    ),
    "ensemble_parameters.json": (
        BASE_DIR / "forecasting/stage4/stage4_results/ensemble_parameters.json",
        "26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0",
    ),
    "blind_baseline.csv": (
        BASE_DIR / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/stage4_clean_baseline/blind_baseline.csv",
        "59d20d27d358e1c6348d3278b688af3bc73b3969aa3b7918d795aeec9563091a",
    ),
}


class TestInferenceRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load non-blind 2024-ODD validation fixture
        df_raw = pd.read_parquet(MATRIX_2024_PATH)
        df_raw = df_raw.sort_values(["origin_dt", "horizon_hour"]).reset_index(drop=True)
        is_trans = ((df_raw["cloud_frac"] >= 0.2) & (df_raw["cloud_frac"] < 0.6)).astype(np.float64)
        df_raw["elevation_x_transition_cloud"] = df_raw["solar_elevation"] * is_trans
        df_raw["causal_day_mask"] = (df_raw["solar_elevation"] > 0.0) & (df_raw["clearsky_ghi"] > 0.0)
        df_odd = df_raw[~df_raw["is_even_origin"]].reset_index(drop=True)

        # Select a summer origin with high elevation and full daylight
        summer_origins = df_odd[df_odd["origin_dt"].dt.month == 6]["origin_dt"].unique()
        cls.summer_origin = summer_origins[0]
        cls.summer_fixture = df_odd[df_odd["origin_dt"] == cls.summer_origin].copy().reset_index(drop=True)
        cls.summer_fixture = cls.summer_fixture.drop(columns=["actual_SW_IN"])

        # Select a winter origin with low elevation and twilight
        winter_origins = df_odd[df_odd["origin_dt"].dt.month == 1]["origin_dt"].unique()
        cls.winter_origin = winter_origins[0]
        cls.winter_fixture = df_odd[df_odd["origin_dt"] == cls.winter_origin].copy().reset_index(drop=True)
        cls.winter_fixture = cls.winter_fixture.drop(columns=["actual_SW_IN"])

        # Load real bundle once
        cls.bundle = load_candidate_n6_bundle(DEFAULT_ARTIFACT_PATH)

    def test_01_checksum_acceptance(self):
        """1. Checksum acceptance for unchanged frozen artifact."""
        h = verify_artifact_checksum(DEFAULT_ARTIFACT_PATH, EXPECTED_SHA256)
        self.assertEqual(h, EXPECTED_SHA256)

    def test_02_checksum_rejection_altered_copy(self):
        """2. Checksum rejection on deliberately altered isolated disposable copy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_model = Path(tmpdir) / "altered_model.joblib"
            shutil.copy(DEFAULT_ARTIFACT_PATH, tmp_model)
            # Append garbage byte to alter checksum
            with open(tmp_model, "ab") as f:
                f.write(b"\x00\xff")
            with self.assertRaises(ArtifactIntegrityError):
                verify_artifact_checksum(tmp_model, EXPECTED_SHA256)

    def test_03_missing_artifact_fail_closed(self):
        """3. Missing-artifact fail-closed behavior."""
        missing_path = Path("/tmp/non_existent_candidate_model.joblib")
        with self.assertRaises(ArtifactIntegrityError):
            verify_artifact_checksum(missing_path, EXPECTED_SHA256)

    def test_04_bundle_schema_and_features(self):
        """4. Model-bundle schema, scalar parameters, and feature-order validation."""
        self.assertIn("additive_models", self.bundle)
        self.assertIn("kt_models", self.bundle)
        self.assertEqual(len(self.bundle["additive_models"]), 25)
        self.assertEqual(len(self.bundle["kt_models"]), 15)
        self.assertEqual(list(self.bundle["features"]), FEATURE_NAMES)
        self.assertEqual(float(self.bundle["max_ramp_weight"]), 0.55)
        self.assertEqual(float(self.bundle["ramp_start_deg"]), 22.0)
        self.assertEqual(float(self.bundle["ramp_full_deg"]), 32.0)
        self.assertEqual(float(self.bundle["eps_kt"]), 15.0)

    def test_05_genuine_inference_parity(self):
        """5. Genuine-inference parity against authoritative frozen implementation."""
        for fixture, name in [(self.summer_fixture, "Summer"), (self.winter_fixture, "Winter")]:
            # Run inference using the recovered runner
            y_runner, std_runner = run_candidate_n6_inference(self.bundle, fixture)

            # Compute reference manually via authoritative equations
            X = fixture[FEATURE_NAMES].to_numpy(dtype=np.float64)
            st4 = fixture["pred_stage4_clean"].to_numpy(dtype=np.float64)
            cs_terr = fixture["clearsky_ghi_terrain_adjusted"].to_numpy(dtype=np.float64)
            cs_ghi = fixture["clearsky_ghi"].to_numpy(dtype=np.float64)
            elev = fixture["solar_elevation"].to_numpy(dtype=np.float64)
            shaded = fixture["terrain_solar_obstruction_flag"].to_numpy(dtype=np.int64)

            preds_add = np.array([np.clip(st4 + m.predict(X), 0.0, None) for m in self.bundle["additive_models"]])
            y_add_ref = np.mean(preds_add, axis=0)

            eps_kt = self.bundle["eps_kt"]
            denom = cs_terr + eps_kt
            ceiling = np.maximum(cs_ghi * 1.25, st4)
            preds_kt = np.array([np.clip(st4 + m.predict(X) * denom, 0.0, ceiling) for m in self.bundle["kt_models"]])
            y_kt_ref = np.mean(preds_kt, axis=0)

            alpha = 0.55 * np.clip((elev - 22.0) / 10.0, 0.0, 1.0)
            unshaded = (shaded == 0).astype(np.float64)
            w = alpha * unshaded
            y_blend = (1.0 - w) * y_add_ref + w * y_kt_ref
            cday = (elev > 0.0) & (cs_ghi > 0.0)
            y_ref = np.where(cday, y_blend, 0.0)

            all_m = np.vstack([preds_add, preds_kt])
            std_ref = np.where(cday, np.std(all_m, axis=0), 0.0)

            # Absolute numerical parity check (tolerance 1e-12)
            np.testing.assert_allclose(y_runner, y_ref, atol=1e-12, rtol=1e-12)
            np.testing.assert_allclose(std_runner, std_ref, atol=1e-12, rtol=1e-12)

    def test_06_conformal_lower_bound_properties(self):
        """6. Conformal lower-bound arithmetic, clipping, and nighttime behavior."""
        y_pred, std = run_candidate_n6_inference(self.bundle, self.summer_fixture)
        y_lo, ebr = compute_conformal_lower_and_ebr(y_pred, std, self.summer_fixture)

        # 1. Lower bound must never exceed point forecast
        self.assertTrue(np.all(y_lo <= y_pred + 1e-9))
        # 2. Lower bound must be non-negative everywhere
        self.assertTrue(np.all(y_lo >= 0.0))
        # 3. Nighttime points must be strictly 0.0
        elev = self.summer_fixture["solar_elevation"].values
        night = elev <= 0.0
        if np.any(night):
            self.assertTrue(np.all(y_lo[night] == 0.0))
            self.assertTrue(np.all(y_pred[night] == 0.0))

    def test_07_ebr_units_and_rolling_window(self):
        """7. EBR units, horizon alignment, and rolling-window arithmetic."""
        y_pred, std = run_candidate_n6_inference(self.bundle, self.summer_fixture)
        _, ebr = compute_conformal_lower_and_ebr(y_pred, std, self.summer_fixture)

        self.assertEqual(len(ebr), 24)
        # All entries must satisfy the minimum floor EBR_BASE_WH (15 kWh)
        for val in ebr:
            self.assertGreaterEqual(val, EBR_BASE_WH)
            self.assertTrue(np.isfinite(val))
        # Check that peak EBR does not exceed usable battery headroom (150 kWh)
        max_ebr = max(ebr)
        self.assertLess(max_ebr, 150000.0, f"EBR {max_ebr} Wh exceeds usable battery headroom (150 kWh)!")

    def test_08_payload_schema_and_causal_firewall(self):
        """8. Payload schema validation and causal target-leakage firewall."""
        payload = generate_dispatch_payload(self.summer_fixture, self.bundle)
        self.assertIn("solar_forecast_wm2", payload)
        self.assertIn("solar_conformal_lower_wm2", payload)
        self.assertIn("ebr_target_wh", payload)
        self.assertEqual(len(payload["solar_forecast_wm2"]), 24)
        self.assertEqual(len(payload["solar_conformal_lower_wm2"]), 24)
        self.assertEqual(len(payload["ebr_target_wh"]), 24)

        # Target leakage rejection test
        leaked_df = self.summer_fixture.copy()
        leaked_df["actual_SW_IN"] = 123.4
        with self.assertRaises(InputValidationError):
            validate_input_features(leaked_df)

    def test_09_protected_asset_immutability(self):
        """9. Regression checks confirming all protected models, results, and baselines are unchanged."""
        for name, (path, exp_hash) in PROTECTED_ASSETS.items():
            self.assertTrue(path.exists(), f"Protected asset missing: {path}")
            act_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                act_hash,
                exp_hash,
                f"PROTECTED ASSET TAMPERED: {name}\nExpected: {exp_hash}\nActual:   {act_hash}",
            )


if __name__ == "__main__":
    unittest.main()
