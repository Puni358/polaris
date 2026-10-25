#!/usr/bin/env python3
"""
POLARIS — Candidate N6 -> L2 Uncertainty -> EBR -> GAP19/MILP Offline Integration Test
======================================================================================
Strictly Offline, Non-Production Simulation Mode.
Preserves winner: null. Does not modify frozen assets or production dispatch.

Tests:
  1. N6 input schema and causal feature handling (36 features).
  2. Forecast generation and physical night-time zeroing.
  3. Split-conformal uncertainty lower-bound calculations (GHI_lower <= GHI_pred).
  4. 6-hour forward rolling EBR calculation, units (Wh), and baseline floor (>=15,000 Wh).
  5. End-to-end integration with GAP19 HighsNativeOptimizer in simulation mode.
  6. Failure-closed security & causal firewall safeguards against corrupted/leaked inputs.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
import yaml

# Repository base path
BASE = Path("/home/punith-bs/01polaris (Copy)")
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

# Candidate N6 Runner Path
CAND_N_DIR = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics"
ARTIFACTS_DIR = CAND_N_DIR / "artifacts"
if str(ARTIFACTS_DIR) not in sys.path:
    sys.path.insert(0, str(ARTIFACTS_DIR))

import polaris_inference_runner as runner
from polaris_inference_runner import (
    DEFAULT_ARTIFACT_PATH,
    EXPECTED_SHA256,
    FEATURE_NAMES,
    K_PV,
    P_INV_MAX_W,
    EBR_BASE_WH,
    InputValidationError,
    ArtifactIntegrityError,
    load_candidate_n6_bundle,
    run_candidate_n6_inference,
    compute_conformal_lower_and_ebr,
    validate_input_features,
    generate_dispatch_payload,
)

# System Components
from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState

# Protected Hashes to verify immutability
PROTECTED_ASSETS = {
    "candidate_n6_model.joblib": (
        ARTIFACTS_DIR / "candidate_n6_model.joblib",
        "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197",
    ),
    "candidate_n1_model.joblib": (
        ARTIFACTS_DIR / "candidate_n1_model.joblib",
        "7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7",
    ),
    "CANDIDATE_N_MANIFEST.json": (
        ARTIFACTS_DIR / "CANDIDATE_N_MANIFEST.json",
        "1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031",
    ),
    "ensemble_parameters.json": (
        BASE / "forecasting/stage4/stage4_results/ensemble_parameters.json",
        "26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0",
    ),
}

FIXTURE_DIR = BASE / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0"
SMOKE_ORIGIN = pd.Timestamp("2024-06-01T00:00:00Z")
SMOKE_INDEX = 3648  # Index corresponding to 2024-06-01T00:00:00Z in H1.0 fixture


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestN6GAP19OfflineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Assert immutability of protected assets
        for name, (path, expected_hash) in PROTECTED_ASSETS.items():
            actual = sha256_of(path)
            assert actual == expected_hash, f"Protected asset {name} altered! {actual} != {expected_hash}"

        # 2. Load candidate N6 model bundle
        cls.bundle = load_candidate_n6_bundle(DEFAULT_ARTIFACT_PATH)

        # 3. Load 2024 development matrix and build 36-feature input for smoke origin
        matrix_path = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet"
        df_mat = pd.read_parquet(matrix_path)
        df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
        origin_df = df_mat[df_mat["forecast_start"] == SMOKE_ORIGIN].sort_values("horizon_hour").reset_index(drop=True)
        assert len(origin_df) == 24, f"Expected 24 rows for origin {SMOKE_ORIGIN}, got {len(origin_df)}"

        # Synthesize 36th feature: elevation_x_transition_cloud
        is_trans = ((origin_df["cloud_frac"] >= 0.2) & (origin_df["cloud_frac"] < 0.6)).astype(np.float64)
        origin_df["elevation_x_transition_cloud"] = origin_df["solar_elevation"] * is_trans

        # Drop forbidden evaluation labels (simulating genuine inference payload)
        cls.features_df = origin_df.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")

        # 4. Load microgrid configs
        cls.configs = {}
        for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
            cfg_file = BASE / "system" / "config" / f"{cfg_name}.yaml"
            if cfg_file.exists():
                with open(cfg_file) as f:
                    cls.configs[cfg_name] = yaml.safe_load(f)

        # 5. Load H1.0 runtime adapter
        cls.adapter = H10RuntimeAdapter(str(FIXTURE_DIR))
        st_k_raw = cls.adapter.get_station_state(SMOKE_INDEX, battery_soc_pct=50.0)

        # Warm up station state to test NORMAL/MILP branch
        cls.st_k = StationState(
            timestamp=st_k_raw.timestamp,
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=True,
            diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )

        cls.next_actual = cls.adapter.get_future_ground_truth(SMOKE_INDEX, horizon_hours=24)[0]

    def test_01_feature_schema_and_causal_contract(self):
        """Test 1: N6 input schema, contract ordering, and absence of target labels."""
        validate_input_features(self.features_df)
        self.assertEqual(len(self.features_df), 24)
        for feat in FEATURE_NAMES:
            self.assertIn(feat, self.features_df.columns)
        self.assertNotIn("actual_SW_IN", self.features_df.columns)
        self.assertNotIn("actual_ghi", self.features_df.columns)
        self.assertNotIn("residual_target", self.features_df.columns)

        # Confirm u700/v700 NaN handling: horizons 20..24 are NaN, permitted by design
        u700_nans = self.features_df["u700"].isna().tolist()
        self.assertEqual(u700_nans, [False] * 19 + [True] * 5)

    def test_02_forecast_generation_and_night_zeroing(self):
        """Test 2: Point forecast generation and strict night-zeroing."""
        preds, ens_std = run_candidate_n6_inference(self.bundle, self.features_df)
        self.assertEqual(preds.shape, (24,))
        self.assertEqual(ens_std.shape, (24,))
        self.assertTrue(np.all(preds >= 0.0), "Forecast contains negative irradiance")
        self.assertTrue(np.all(preds <= 1200.0), "Forecast exceeds physical ceiling")

        # Night hours: solar_elevation <= 0 or clearsky_ghi <= 0 must be strictly 0.0
        elev = self.features_df["solar_elevation"].values
        cs_ghi = self.features_df["clearsky_ghi"].values
        is_night = (elev <= 0.0) | (cs_ghi <= 0.0)
        self.assertTrue(np.all(preds[is_night] == 0.0), "Night-time irradiance non-zero!")

    def test_03_conformal_uncertainty_lower_bound(self):
        """Test 3: Conformal 90% lower bound satisfies GHI_lower <= GHI_pred and lower >= 0."""
        preds, ens_std = run_candidate_n6_inference(self.bundle, self.features_df)
        ghi_lower, ebr_wh = compute_conformal_lower_and_ebr(preds, ens_std, self.features_df)

        self.assertEqual(len(ghi_lower), 24)
        self.assertTrue(np.all(ghi_lower >= 0.0), "Lower bound contains negative values")
        self.assertTrue(np.all(ghi_lower <= preds + 1e-9), "Lower bound exceeds point prediction!")

    def test_04_ebr_calculation_units_and_floor(self):
        """Test 4: 6-hour rolling EBR calculation, Wh units, and baseline floor."""
        preds, ens_std = run_candidate_n6_inference(self.bundle, self.features_df)
        ghi_lower, ebr_wh = compute_conformal_lower_and_ebr(preds, ens_std, self.features_df)

        self.assertEqual(len(ebr_wh), 24)
        for t, val in enumerate(ebr_wh):
            self.assertIsInstance(val, float)
            self.assertGreaterEqual(val, EBR_BASE_WH, f"EBR at index {t} below 15 kWh floor: {val}")

    def test_05_gap19_milp_end_to_end_simulation(self):
        """Test 5: Passing forecast and dynamic EBR into GAP19/MILP in simulation mode."""
        preds, ens_std = run_candidate_n6_inference(self.bundle, self.features_df)
        ghi_lower, ebr_wh = compute_conformal_lower_and_ebr(preds, ens_std, self.features_df)

        # Convert irradiance (W/m^2) to power generation (W) for microgrid inverter
        p_pv_point = np.minimum(P_INV_MAX_W, preds * K_PV).tolist()
        p_pv_lower = np.minimum(P_INV_MAX_W, ghi_lower * K_PV).tolist()
        # Upper bound for interval: bounded above by clearsky or 1.25 * point
        cs_ghi = self.features_df["clearsky_ghi"].values
        p_pv_upper = np.minimum(P_INV_MAX_W, np.maximum(preds, cs_ghi) * K_PV).tolist()

        timestamps = [
            (SMOKE_ORIGIN + timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for h in range(1, 25)
        ]

        # Extract demand and wind from fixture context
        future_gt = self.adapter.get_future_ground_truth(SMOKE_INDEX, horizon_hours=24)
        demand_vals = [float(row["actual_demand"]) for row in future_gt]
        wind_vals = [float(row["actual_wind_generation"]) for row in future_gt]

        # Critical demand baseline
        critical_baseline_w = float(
            self.configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        crit_vals = [min(critical_baseline_w, d) for d in demand_vals]

        # Construct legal ForecastBundle
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=SMOKE_ORIGIN.strftime("%Y-%m-%dT%H:%M:%SZ"),
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast(
                point=np.round(preds, 4).tolist(),
                lower=np.round(ghi_lower, 4).tolist(),
                upper=np.round(np.maximum(preds, cs_ghi), 4).tolist(),
                unit="W/m^2",
            ),
            solar_generation=TimeseriesForecast(
                point=np.round(p_pv_point, 2).tolist(),
                lower=np.round(p_pv_lower, 2).tolist(),
                upper=np.round(p_pv_upper, 2).tolist(),
                unit="W",
            ),
            wind_generation=TimeseriesForecast(
                point=wind_vals,
                lower=wind_vals,
                upper=wind_vals,
                unit="W",
            ),
            demand=TimeseriesForecast(
                point=demand_vals,
                lower=demand_vals,
                upper=demand_vals,
                unit="W",
            ),
            metadata={"forecaster": "Candidate N6", "ebr_target_wh": ebr_wh},
            demand_critical=TimeseriesForecast(
                point=crit_vals,
                lower=crit_vals,
                upper=crit_vals,
                unit="W",
            ),
        )

        # Configure GAP19 optimizer with dynamic EBR vector
        configs = dict(self.configs)
        configs["ebr_target_wh"] = ebr_wh
        configs["terminal_reserve_model"] = "INITIAL_STATE"
        configs["critical_demand_w"] = crit_vals

        router = EMSControlRouter()
        assessment, route = router.evaluate_and_route(self.st_k, bundle, configs)
        self.assertEqual(route, "NORMAL", f"Expected NORMAL route, got {route}")

        optimizer = GAP19HighsNativeOptimizer()
        plan = optimizer.optimize(bundle, self.st_k, configs)

        self.assertEqual(plan.constraint_status, "OPTIMAL", f"MILP failed: {plan.constraint_status}")
        self.assertEqual(len(plan.battery_charge), 24)
        self.assertEqual(len(plan.battery_discharge), 24)
        self.assertEqual(len(plan.diesel_power), 24)
        self.assertEqual(plan.j1_objective, 0.0, "Critical deficit occurred in J1!")

        # Step simulator for one closed-loop timestep
        simulator = DigitalTwinSimulator(configs)
        next_state = simulator.step(self.st_k, plan, self.next_actual)
        self.assertEqual(next_state.timestamp, "2024-06-01T01:00:00Z")
        self.assertGreater(next_state.battery_energy_wh, 0.0)

    def test_06_fail_closed_security_and_causal_firewall(self):
        """Test 6: Safe fail-closed rejection on invalid, corrupted, or leaking inputs."""
        # 6a. Target leakage attempt: forbidden column present
        leaked_df = self.features_df.copy()
        leaked_df["actual_SW_IN"] = 100.0
        with self.assertRaises(InputValidationError):
            validate_input_features(leaked_df)

        # 6b. Missing critical physical feature
        missing_df = self.features_df.drop(columns=["solar_elevation"])
        with self.assertRaises(InputValidationError):
            validate_input_features(missing_df)

        # 6c. NaN in critical feature
        nan_df = self.features_df.copy()
        nan_df.loc[0, "clearsky_ghi"] = np.nan
        with self.assertRaises(InputValidationError):
            validate_input_features(nan_df)

        # 6d. Truncated horizon count (< 24 rows)
        short_df = self.features_df.iloc[:20].copy()
        with self.assertRaises(InputValidationError):
            validate_input_features(short_df)


if __name__ == "__main__":
    unittest.main()
