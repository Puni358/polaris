"""
POLARIS — Candidate N6 Live Operational Execution & Data Availability Test Suite
===============================================================================
Tests:
1. Resolution of u700/v700 truncation (horizons 20-24 contain real physical data, 0 NaNs).
2. Real-time data arrival evidence (18Z MEPS Fimex creation >3.5h before 00:00 UTC).
3. Dynamic telemetry context calculation (14 features from trailing [t0-24h, t0)).
4. End-to-end execution of N6SolarForecastEngine within operational runner context.
5. GAP19 integration with dynamic EBR reserve trajectory.
6. Cryptographic model hash preservation and winner: null governance assertion.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from system.forecasting.implementations.n6_solar import (
    N6SolarForecastEngine,
    FEATURE_NAMES,
    FROZEN_MODEL_PATH,
    FROZEN_MODEL_SHA256,
)
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_n_additive_physics.meps_wind_extractor import (
    fetch_untruncated_meps_wind,
)
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_n_additive_physics.n6_operational_pipeline import (
    build_n6_live_feature_matrix,
    execute_n6_live_operational_cycle,
    compute_telemetry_context_features,
)

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
CAND_N_DIR = REPO_ROOT / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics"


class TestN6LiveOperationalExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify frozen model hash
        assert FROZEN_MODEL_PATH.exists()
        h = hashlib.sha256(FROZEN_MODEL_PATH.read_bytes()).hexdigest()
        assert h == FROZEN_MODEL_SHA256

    def test_01_u700_v700_untruncated_recovery(self):
        """Verifies that u700 and v700 for horizons 20-24 are non-NaN physical values."""
        wind_data = fetch_untruncated_meps_wind("2024-06-01")
        u_vals = wind_data["u700"]
        v_vals = wind_data["v700"]

        self.assertEqual(len(u_vals), 24)
        self.assertEqual(len(v_vals), 24)

        # Check horizons 20..24 specifically (indices 19..23)
        h20_24_u = u_vals[19:24]
        h20_24_v = v_vals[19:24]

        self.assertFalse(any(np.isnan(x) for x in h20_24_u), "u700 contains NaN in horizons 20..24")
        self.assertFalse(any(np.isnan(x) for x in h20_24_v), "v700 contains NaN in horizons 20..24")

        # Physical wind magnitude checks (polar troposphere range)
        for u, v in zip(h20_24_u, h20_24_v):
            speed = np.sqrt(u**2 + v**2)
            self.assertGreater(speed, 0.1, "Physical wind speed should be > 0.1 m/s")
            self.assertLess(speed, 100.0, "Physical wind speed should be < 100 m/s")

    def test_02_real_time_meps_arrival_margin_evidence(self):
        """Verifies that 18Z MEPS provider creation occurs well before the 00:00 UTC deadline."""
        wind_data = fetch_untruncated_meps_wind("2024-06-01")
        prov_creation = wind_data.get("provider_creation_utc")
        margin_s = wind_data.get("provider_margin_seconds")

        self.assertIsNotNone(prov_creation)
        self.assertIsNotNone(margin_s)
        # Margin must be > 3 hours (10,800 s) before 00:00 UTC
        self.assertGreater(margin_s, 10800.0, f"Margin {margin_s}s is less than 3 hours")
        self.assertTrue(wind_data.get("cutoff_satisfied"))

    def test_03_dynamic_telemetry_freshness_computation(self):
        """Verifies that 14 context features are computed dynamically from trailing observations."""
        synthetic_history = [float(x) for x in range(1, 25)]  # 24 steps
        ctx = compute_telemetry_context_features(synthetic_history)

        self.assertEqual(len(ctx), 14)
        for k, v in ctx.items():
            self.assertFalse(np.isnan(v), f"NaN in context feature {k}")
            self.assertFalse(np.isinf(v), f"Inf in context feature {k}")

        self.assertEqual(ctx["ctx_last_obs"], 24.0)
        self.assertAlmostEqual(ctx["ctx_abs_change_1h"], 1.0)
        self.assertAlmostEqual(ctx["ctx_mean_24h"], float(np.mean(synthetic_history)))

    def test_04_live_operational_feature_matrix_completeness(self):
        """Verifies that the assembled feature matrix has shape (24, 36) and zero NaNs."""
        feature_df, meta = build_n6_live_feature_matrix("2024-06-01T00:00:00Z")

        self.assertEqual(feature_df.shape, (24, 36))
        self.assertEqual(list(feature_df.columns), FEATURE_NAMES)
        self.assertEqual(int(feature_df.isna().sum().sum()), 0)
        self.assertEqual(meta["total_nans"], 0)

        # Check that u700 and v700 have zero NaNs across all 24 horizons
        self.assertEqual(int(feature_df["u700"].isna().sum()), 0)
        self.assertEqual(int(feature_df["v700"].isna().sum()), 0)

    def test_05_end_to_end_operational_execution_and_ebr(self):
        """Executes full live operational cycle through ForecastEngine, Router, and GAP19."""
        result = execute_n6_live_operational_cycle(origin="2024-06-01T00:00:00Z", fixture_index=3648)

        self.assertTrue(result["execution_success"])
        self.assertEqual(result["bundle_schema"], "1.0.0")
        self.assertEqual(result["router_assessment"], "NORMAL")
        self.assertEqual(result["gap19_status"], "OPTIMAL")
        self.assertGreater(result["solar_point_max_w"], 0.0)
        self.assertGreaterEqual(result["ebr_floor_wh"], 15000.0)
        self.assertGreater(result["next_battery_soc_pct"], 20.0)
        self.assertLess(result["next_battery_soc_pct"], 95.0)

    def test_06_model_governance_and_hash_invariants(self):
        """Asserts that all protected model artifacts remain unmodified and winner: null is preserved."""
        # 1. Candidate N6
        h6 = hashlib.sha256((CAND_N_DIR / "artifacts/candidate_n6_model.joblib").read_bytes()).hexdigest()
        self.assertEqual(h6, "b1b54c93e2dbefdcb562e4229394a2492b299b66426beaafead17f6777395197")

        # 2. Candidate N1
        h1 = hashlib.sha256((CAND_N_DIR / "artifacts/candidate_n1_model.joblib").read_bytes()).hexdigest()
        self.assertEqual(h1, "7265dabe6ea2c81bc38e724b41e0c02dd1e485cd124939b7249320b3f4abf9d7")

        # 3. Candidate N Manifest
        hm = hashlib.sha256((CAND_N_DIR / "artifacts/CANDIDATE_N_MANIFEST.json").read_bytes()).hexdigest()
        self.assertEqual(hm, "1666a6860706ab266eec7d7995b7ee31308d21263aa1112485e229b916be1031")

        # 4. Stage 4 Ensemble Parameters
        hp = hashlib.sha256((REPO_ROOT / "forecasting/stage4/stage4_results/ensemble_parameters.json").read_bytes()).hexdigest()
        self.assertEqual(hp, "26cfbd19744a4a01719470d20808b5316af7262aed6c2cd84376d8987ce0abc0")

        # 5. Check CANDIDATE_N_MANIFEST winner status
        with open(CAND_N_DIR / "artifacts/CANDIDATE_N_MANIFEST.json", "r") as f:
            manifest = json.load(f)
        self.assertIsNone(manifest.get("winner"), "Governance violation: winner must remain null!")


if __name__ == "__main__":
    unittest.main()
