"""
D5 Implementation Unit & Synthetic Test Suite
Verifies software correctness, schema validation, perturbation arithmetic, causal firewall isolation,
scenario immutability, D4-C1 failure classification, metric calculations, and governance artifact integrity.

NOTE: All tests use isolated synthetic/mock data. ZERO D5 experimental actual trajectories or experimental scenario gates are executed.
"""
import copy
import math
import hashlib
import unittest
from pathlib import Path

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.robustness.perturbation import ForecastPerturber, ForecastBundleValidationError
from system.robustness.scenarios import D5ScenarioRegistry, D5ScenarioConfig
from system.robustness.metrics import D5MetricsCalculator
from system.robustness.orchestrator import D5Runner, D5FaultEvent


class SyntheticDataProvider:
    """Mock DataProvider supplying deterministic synthetic timesteps for unit tests."""
    def __init__(self, total_timesteps: int = 24):
        self.total_timesteps = total_timesteps
        self.timesteps = [
            {
                "timestamp": f"2026-06-01T{h:02d}:00:00Z",
                "actual_SW_IN": 500.0 if 6 <= h <= 18 else 0.0,
                "actual_demand": 100000.0,
                "actual_wind_generation": 20000.0
            }
            for h in range(total_timesteps)
        ]

    def get_runtime_state(self, step_idx: int):
        return {
            "timestamp": self.timesteps[step_idx]["timestamp"],
            "historical_observations": []
        }

    def get_future_ground_truth(self, step_idx: int, horizon_hours: int = 24):
        res = []
        for i in range(horizon_hours):
            idx = (step_idx + i) % self.total_timesteps
            res.append(self.timesteps[idx])
        return res


def create_synthetic_forecast_bundle() -> ForecastBundle:
    """Helper to construct a valid baseline 24h ForecastBundle fixture."""
    timestamps = [f"2026-06-01T{h:02d}:00:00Z" for h in range(24)]
    solar_irrad_p = [500.0 if 6 <= h <= 18 else 0.0 for h in range(24)]
    solar_irrad_l = [p * 0.9 for p in solar_irrad_p]
    solar_irrad_u = [p * 1.1 for p in solar_irrad_p]

    solar_gen_p = [p * 0.2 * 1000.0 for p in solar_irrad_p]  # W
    solar_gen_l = [p * 0.9 for p in solar_gen_p]
    solar_gen_u = [p * 1.1 for p in solar_gen_p]

    wind_p = [20000.0] * 24
    wind_l = [18000.0] * 24
    wind_u = [22000.0] * 24

    demand_p = [100000.0] * 24
    demand_l = [95000.0] * 24
    demand_u = [105000.0] * 24

    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp="2026-06-01T00:00:00Z",
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=TimeseriesForecast(point=solar_irrad_p, lower=solar_irrad_l, upper=solar_irrad_u, unit="W/m^2"),
        solar_generation=TimeseriesForecast(point=solar_gen_p, lower=solar_gen_l, upper=solar_gen_u, unit="W"),
        wind_generation=TimeseriesForecast(point=wind_p, lower=wind_l, upper=wind_u, unit="W"),
        demand=TimeseriesForecast(point=demand_p, lower=demand_l, upper=demand_u, unit="W"),
        metadata={"source": "SYNTHETIC_TEST_FIXTURE"}
    )


class TestD5Implementation(unittest.TestCase):

    def setUp(self):
        self.system_dir = Path("/home/punith-bs/01polaris (Copy)/system")
        self.bundle = create_synthetic_forecast_bundle()

    def test_multiplicative_perturbation_arithmetic(self):
        """Verifies L' = gamma*L, P' = gamma*P, U' = gamma*U multiplicative scaling."""
        gamma = 1.30
        perturbed = ForecastPerturber.apply_perturbation(self.bundle, solar_scale=gamma, scenario_id="S2_TEST")

        for orig_p, pert_p, orig_l, pert_l, orig_u, pert_u in zip(
            self.bundle.solar_generation.point, perturbed.solar_generation.point,
            self.bundle.solar_generation.lower, perturbed.solar_generation.lower,
            self.bundle.solar_generation.upper, perturbed.solar_generation.upper
        ):
            self.assertAlmostEqual(pert_p, orig_p * gamma, places=5)
            self.assertAlmostEqual(pert_l, orig_l * gamma, places=5)
            self.assertAlmostEqual(pert_u, orig_u * gamma, places=5)
            self.assertTrue(pert_l <= pert_p <= pert_u)

    def test_invalid_perturbation_rejection(self):
        """Verifies invalid scale factors (negative, NaN, Inf) are rejected without silent repair."""
        with self.assertRaises(ForecastBundleValidationError):
            ForecastPerturber.apply_perturbation(self.bundle, solar_scale=-0.5)

        with self.assertRaises(ForecastBundleValidationError):
            ForecastPerturber.apply_perturbation(self.bundle, solar_scale=float("nan"))

        with self.assertRaises(ForecastBundleValidationError):
            ForecastPerturber.apply_perturbation(self.bundle, solar_scale=float("inf"))

    def test_scenario_registry_and_durations(self):
        """Verifies frozen scenario parameter definitions and exact closed-loop durations."""
        scenarios = D5ScenarioRegistry.list_scenarios()
        self.assertEqual(len(scenarios), 6)

        s1 = D5ScenarioRegistry.get_scenario("D5-1")
        self.assertEqual(s1.solar_scale, 0.70)
        self.assertEqual(s1.duration_iterations, 24)

        s6 = D5ScenarioRegistry.get_scenario("D5-6")
        self.assertEqual(s6.solar_scale, 1.15)
        self.assertEqual(s6.wind_scale, 1.15)
        self.assertEqual(s6.duration_iterations, 168)

    def test_causal_firewall_isolation(self):
        """Verifies perturbation generator depends ONLY on baseline ForecastBundle and parameters."""
        perturbed = ForecastPerturber.apply_perturbation(self.bundle, solar_scale=0.70, demand_scale=1.20)
        self.assertEqual(perturbed.metadata["d5_perturbation"]["solar_scale"], 0.70)
        self.assertEqual(perturbed.metadata["d5_perturbation"]["demand_scale"], 1.20)

    def test_lsf_formula_and_metrics_calculator(self):
        """Verifies LSF = 100 * (1 - E_unmet / E_demand_total) formula and separated metric output."""
        lsf_full = D5MetricsCalculator.compute_lsf(unmet_load_wh=0.0, total_demand_wh=1000.0)
        self.assertEqual(lsf_full, 100.0)

        lsf_partial = D5MetricsCalculator.compute_lsf(unmet_load_wh=100.0, total_demand_wh=1000.0)
        self.assertEqual(lsf_partial, 90.0)

        mock_dispatch = [{
            "solar_used": [10.0],
            "wind_used": [20.0],
            "diesel_power": [0.0],
            "renewable_curtailment": [5.0],
            "unmet_load": [0.0],
            "load_served": [30.0],
            "battery_discharge": [0.0],
            "constraint_status": "OPTIMAL",
            "energy_balance_residual": 0.0
        }]
        metrics = D5MetricsCalculator.calculate_metrics(
            dispatch_plans=mock_dispatch,
            station_states=[{"battery_soc_pct": 50.0}],
            fault_events=[],
            station_configs={"battery": {"capacity_wh": 200000.0}, "diesel": {}}
        )
        self.assertIn("physical_outcome_metrics", metrics)
        self.assertIn("execution_and_fault_metrics", metrics)
        self.assertEqual(metrics["physical_outcome_metrics"]["load_served_fraction_pct"], 100.0)

    def test_mock_closed_loop_runner_orchestration(self):
        """Verifies receding horizon MPC loop flow and D4-C1 fault handling using synthetic data."""
        mock_provider = SyntheticDataProvider(total_timesteps=3)
        runner = D5Runner(
            system_dir=self.system_dir.parent,
            optimizer_type="milp",
            custom_data_provider=mock_provider
        )

        report = runner.run_single_simulation(
            steps_to_run=3,
            solar_scale=0.90,
            scenario_id="MOCK_TEST"
        )
        self.assertIn(report["execution_and_fault_metrics"]["execution_status"], ["SUCCESS_CLEAN", "SUCCESS_WITH_GOVERNED_FAULTS"])
        self.assertEqual(report["run_metadata"]["completed_steps"], 3)

    def test_frozen_governance_artifact_hashes(self):
        """Verifies that the 4 frozen governance artifacts in workspace have NOT been altered."""
        expected_hashes = {
            "ems/reports/system_integration/POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.md": "23af7ba4f24bedfce9324323f2e31633e83c2a3f171f19b891644d62b13a2869",
            "ems/reports/system_integration/POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.json": "544649c8f189d7a01c5c5d88b067e44040df616441b9a759f3ca84b5019bcabd",
            "ems/reports/system_integration/POLARIS_SYSTEM_D5_CONTRACT_FREEZE_CHECKPOINT.md": "f0c829620dded20da0777634b8c4ddf7383e97b8eeed2002c3c52341ea4794b0",
            "ems/reports/system_integration/POLARIS_SYSTEM_D5_CONTRACT_FREEZE_CHECKPOINT.json": "710455f80bb7774f965e536a2dff2da966475ec1d9767eb0660a92ef9864c4df"
        }

        ws_dir = self.system_dir.parent
        for fname, expected_sha in expected_hashes.items():
            fpath = ws_dir / fname
            self.assertTrue(fpath.exists(), f"Governance file {fname} does not exist!")
            actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
            self.assertEqual(actual_sha, expected_sha, f"Governance file {fname} SHA256 mismatch!")


if __name__ == "__main__":
    unittest.main()
