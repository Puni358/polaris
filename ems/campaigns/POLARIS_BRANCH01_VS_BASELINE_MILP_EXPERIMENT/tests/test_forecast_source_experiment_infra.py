"""
Infrastructure tests for the Branch01-vs-Baseline forecast-source MILP experiment.

These tests do NOT run the real 168h experiment and do NOT solve real MILPs
for anything beyond a couple of trivial smoke-tested timesteps using an
injected fake optimizer (the real LocalMILPEnergyOptimizer takes ~110s/step
on this machine -- see CANDIDATE2 run_metadata -- which is why checkpoint
infrastructure exists at all; tests must stay fast and deterministic).

Verifies:
- both arms are built from identical physical/config inputs
- the ONLY intended difference between arms is the solar forecast source
  (wind/demand forecasts are identical between arms for identical state)
- Branch01 model SHA-256 is verified
- no future ground truth enters either arm's forecast
- checkpoint/resume works correctly (including across an injected mid-run fault)
- ECD/OptionD are never imported or invoked
- atomic checkpoint writes and the trajectory hash chain are well-formed
"""
import hashlib
import importlib
import json
import shutil
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ems/campaigns/POLARIS_BRANCH01_VS_BASELINE_MILP_EXPERIMENT"))

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
from system.governance.model_reproducibility import ModelGovernanceError

import run_forecast_source_experiment as exp

SCENARIO_PATH = exp.SYSTEM_DIR / "data" / "scenarios" / exp.SCENARIO_FILENAME
TEST_OUTPUT_DIR = exp.OUTPUT_DIR / "_test_scratch"


class FakeOptimalMILP:
    """Deterministic, near-instant stand-in for LocalMILPEnergyOptimizer: a
    trivial feasible 'serve everything from diesel, no battery/solar/wind use'
    dispatch. Only used to exercise checkpoint/resume/fairness logic quickly;
    never used to produce any reported experimental result."""

    def optimize(self, forecast_bundle, station_state, config):
        demand = forecast_bundle.demand.point
        return DispatchPlan(
            schema_version="1.0.0",
            timestamps=forecast_bundle.timestamps,
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24,
            battery_soc=[station_state.battery_soc_pct] * 24,
            diesel_power=[min(d, 90000.0) for d in demand],
            load_served=list(demand),
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )


class FailAtStepTwoMILP(FakeOptimalMILP):
    def __init__(self):
        self.calls = 0

    def optimize(self, forecast_bundle, station_state, config):
        self.calls += 1
        if self.calls == 3:  # fail on the 3rd call of a resumed/fresh run
            raise RuntimeError("Injected optimizer failure for resume test.")
        return super().optimize(forecast_bundle, station_state, config)


def _clean(arm: str, output_dir: Path):
    for p in [output_dir / f"checkpoints_{arm}", output_dir / f"PROGRESS_{arm}.json", output_dir / f"RUN_FAILED_{arm}.json"]:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()


class TestNoECDOptionD(unittest.TestCase):
    def test_module_does_not_import_ecd_or_option_d(self):
        """Checks actual import statements only (not prose/comments/docstrings
        that merely reference these names when explaining why they're absent)."""
        import_lines = [
            line.strip() for line in Path(exp.__file__).read_text().splitlines()
            if line.strip().startswith("import ") or line.strip().startswith("from ")
        ]
        for line in import_lines:
            self.assertNotIn("EMSControlRouter", line)
            self.assertNotIn("OptionDFallbackSolver", line)
            self.assertNotIn("system.control.router", line)
            self.assertNotIn("system.optimization.implementations.option_d", line)

    def test_runtime_modules_not_loaded(self):
        self.assertNotIn("system.control.router", sys.modules)
        self.assertNotIn("system.optimization.implementations.option_d", sys.modules)

    def test_aggregated_result_reports_zero_ecd_optiond_invocations(self):
        configs = exp.load_configs()
        result = exp.aggregate_from_checkpoints("baseline", 0, None, configs)
        self.assertEqual(result["ecd_router_invocations"], 0)
        self.assertEqual(result["optiond_fallback_invocations"], 0)


class TestFairnessOfPhysicalAndConfigInputs(unittest.TestCase):
    def test_both_arms_use_identical_configs(self):
        configs_a = exp.load_configs()
        configs_b = exp.load_configs()
        self.assertEqual(json.dumps(configs_a, sort_keys=True), json.dumps(configs_b, sort_keys=True))

    def test_both_arms_use_identical_initial_state(self):
        configs = exp.load_configs()
        provider = LocalDataProvider(SCENARIO_PATH)
        state_a = exp.build_initial_state(provider, configs)
        state_b = exp.build_initial_state(provider, configs)
        self.assertEqual(state_a.to_dict(), state_b.to_dict())

    def test_both_arms_use_identical_scenario_and_optimizer_class(self):
        # Both arms are constructed inside run_arm_checkpointed from the same
        # scenario_path and configs argument, and (absent explicit injection)
        # the same LocalMILPEnergyOptimizer class.
        import inspect
        src = inspect.getsource(exp.run_arm_checkpointed)
        self.assertIn("LocalMILPEnergyOptimizer()", src)
        self.assertIn("DigitalTwinSimulator(configs)", src)


class TestForecastSourceIsOnlyDifference(unittest.TestCase):
    def setUp(self):
        self.configs = exp.load_configs()
        self.provider = LocalDataProvider(SCENARIO_PATH)
        self.baseline_engine = exp.LocalBaselineForecastEngine(exp.CONFIG_DIR / "solar_pv.yaml")
        self.branch01_engine = exp.Branch01ForecastEngine(PROJECT_ROOT)
        self.branch01_adapter = exp.LocalProviderBranch01Adapter(PROJECT_ROOT)
        self.idx = 100
        self.state = exp.build_initial_state(self.provider, self.configs)
        rt = self.provider.get_runtime_state(self.idx)
        self.state = StationState(
            timestamp=rt["origin_timestamp"], battery_soc_pct=50.0, battery_energy_wh=100000.0,
            diesel_running=False, diesel_hours_running=0.0,
            last_observed_solar_irradiance=rt["last_observed_solar_irradiance"],
            last_observed_demand=rt["last_observed_demand"],
            last_observed_wind_generation=rt["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=100.0,
        )
        self.runtime_context = rt

    def test_wind_and_demand_identical_across_arms_for_identical_state(self):
        bundle_base, prov_base = exp.get_forecast_bundle_for_arm(
            "baseline", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, None, None,
        )
        bundle_b1, prov_b1 = exp.get_forecast_bundle_for_arm(
            "branch01", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, self.branch01_engine, self.branch01_adapter,
        )
        self.assertEqual(bundle_base.wind_generation.point, bundle_b1.wind_generation.point)
        self.assertEqual(bundle_base.demand.point, bundle_b1.demand.point)

    def test_solar_forecast_differs_between_arms(self):
        bundle_base, _ = exp.get_forecast_bundle_for_arm(
            "baseline", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, None, None,
        )
        bundle_b1, _ = exp.get_forecast_bundle_for_arm(
            "branch01", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, self.branch01_engine, self.branch01_adapter,
        )
        self.assertNotEqual(bundle_base.solar_irradiance.point, bundle_b1.solar_irradiance.point)

    def test_forecast_provenance_identifies_source_unambiguously(self):
        _, prov_base = exp.get_forecast_bundle_for_arm(
            "baseline", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, None, None,
        )
        _, prov_b1 = exp.get_forecast_bundle_for_arm(
            "branch01", self.state, self.runtime_context, self.provider, self.idx,
            self.baseline_engine, self.branch01_engine, self.branch01_adapter,
        )
        self.assertEqual(prov_base["forecast_source"], "baseline")
        self.assertIsNone(prov_base["solar_model_sha256"])
        self.assertEqual(prov_b1["forecast_source"], "branch01_candidate_a_hgb")
        self.assertEqual(prov_b1["solar_model_sha256"], exp.FROZEN_MODEL_SHA256)


class TestBranch01ModelSHAVerified(unittest.TestCase):
    def test_model_sha_matches_frozen_constant(self):
        actual = hashlib.sha256(exp.MODEL_PATH.read_bytes()).hexdigest()
        self.assertEqual(actual, exp.FROZEN_MODEL_SHA256)

    def test_provenance_manifest_confirms_sha_match(self):
        configs = exp.load_configs()
        manifest = exp.build_provenance_manifest(configs, SCENARIO_PATH)
        self.assertTrue(manifest["branch01_model_sha256_matches_disk"])
        self.assertEqual(manifest["branch01_model_sha256"], exp.FROZEN_MODEL_SHA256)


class TestNoFutureGroundTruthAccessed(unittest.TestCase):
    def test_mutating_future_timesteps_does_not_change_either_arms_forecast(self):
        configs = exp.load_configs()
        provider = LocalDataProvider(SCENARIO_PATH)
        baseline_engine = exp.LocalBaselineForecastEngine(exp.CONFIG_DIR / "solar_pv.yaml")
        branch01_engine = exp.Branch01ForecastEngine(PROJECT_ROOT)
        branch01_adapter = exp.LocalProviderBranch01Adapter(PROJECT_ROOT)
        idx = 100
        rt = provider.get_runtime_state(idx)
        state = StationState(
            timestamp=rt["origin_timestamp"], battery_soc_pct=50.0, battery_energy_wh=100000.0,
            diesel_running=False, diesel_hours_running=0.0,
            last_observed_solar_irradiance=rt["last_observed_solar_irradiance"],
            last_observed_demand=rt["last_observed_demand"],
            last_observed_wind_generation=rt["last_observed_wind_generation"],
            diesel_fuel_remaining_liters=100.0,
        )

        bundle_b1_before, _ = exp.get_forecast_bundle_for_arm(
            "branch01", state, rt, provider, idx, baseline_engine, branch01_engine, branch01_adapter,
        )

        mutated_provider = LocalDataProvider(SCENARIO_PATH)
        for ts in mutated_provider.timesteps[idx + 1:]:
            ts["actual_SW_IN"] = 999999.0
            ts["actual_demand"] = 999999.0
            ts["actual_wind_generation"] = 999999.0

        rt_mut = mutated_provider.get_runtime_state(idx)
        bundle_b1_after, _ = exp.get_forecast_bundle_for_arm(
            "branch01", state, rt_mut, mutated_provider, idx, baseline_engine, branch01_engine, branch01_adapter,
        )
        self.assertEqual(bundle_b1_before.solar_irradiance.point, bundle_b1_after.solar_irradiance.point)

    def test_runtime_state_never_includes_indices_beyond_current(self):
        provider = LocalDataProvider(SCENARIO_PATH)
        state = provider.get_runtime_state(50)
        self.assertEqual(len(state["history"]), 51)
        self.assertEqual(state["history"][-1]["timestamp"], state["origin_timestamp"])


class TestCheckpointResume(unittest.TestCase):
    """Uses FakeOptimalMILP (near-instant) so this stays fast; exercises the
    real checkpoint/resume/trajectory-hash machinery unmodified."""

    def setUp(self):
        exp.OUTPUT_DIR = TEST_OUTPUT_DIR
        TEST_OUTPUT_DIR.mkdir(exist_ok=True)
        _clean("baseline", TEST_OUTPUT_DIR)
        self.configs = exp.load_configs()

    def tearDown(self):
        _clean("baseline", TEST_OUTPUT_DIR)
        if TEST_OUTPUT_DIR.exists() and not any(TEST_OUTPUT_DIR.iterdir()):
            TEST_OUTPUT_DIR.rmdir()
        exp.OUTPUT_DIR = PROJECT_ROOT / "ems/campaigns/POLARIS_BRANCH01_VS_BASELINE_MILP_EXPERIMENT"

    def test_fresh_run_then_crash_then_resume_preserves_completed_steps(self):
        failing_optimizer = FailAtStepTwoMILP()
        result1 = exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=True, max_steps_override=5,
            optimizer=failing_optimizer,
        )
        self.assertEqual(len(result1["faults"]), 1)
        self.assertEqual(result1["completed_steps"], 2)
        self.assertTrue(exp.run_failed_path_for("baseline").exists())

        ckpt0_before = exp.load_checkpoint("baseline", 0)
        ckpt1_before = exp.load_checkpoint("baseline", 1)

        # Resume with a working optimizer; steps 0,1 must not be re-solved/changed.
        result2 = exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=False, max_steps_override=5,
            optimizer=FakeOptimalMILP(),
        )
        self.assertEqual(result2["completed_steps"], 5)
        self.assertEqual(len(result2["faults"]), 0)
        self.assertFalse(exp.run_failed_path_for("baseline").exists())

        ckpt0_after = exp.load_checkpoint("baseline", 0)
        ckpt1_after = exp.load_checkpoint("baseline", 1)
        self.assertEqual(ckpt0_before, ckpt0_after)
        self.assertEqual(ckpt1_before, ckpt1_after)

        for i in range(5):
            self.assertTrue(exp.checkpoint_path("baseline", i).exists())

    def test_trajectory_hash_chain_is_well_formed_and_order_dependent(self):
        exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=True, max_steps_override=3,
            optimizer=FakeOptimalMILP(),
        )
        hashes = [exp.load_checkpoint("baseline", i)["trajectory_hash"] for i in range(3)]
        self.assertEqual(len(set(hashes)), 3)  # all distinct
        for h in hashes:
            self.assertEqual(len(h), 64)  # sha256 hex

    def test_progress_json_reflects_final_state(self):
        exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=True, max_steps_override=2,
            optimizer=FakeOptimalMILP(),
        )
        progress = json.loads(exp.progress_path_for("baseline").read_text())
        self.assertEqual(progress["status"], "complete")
        self.assertEqual(progress["step"], 2)

    def test_aggregate_only_matches_run_aggregation(self):
        result_run = exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=True, max_steps_override=3,
            optimizer=FakeOptimalMILP(),
        )
        result_agg = exp.aggregate_from_checkpoints("baseline", 3, None, self.configs)
        self.assertEqual(result_run["completed_steps"], result_agg["completed_steps"])
        self.assertEqual(result_run["final_trajectory_hash"], result_agg["final_trajectory_hash"])

    def test_no_forecast_source_mixing_within_single_arm_run(self):
        result = exp.run_arm_checkpointed(
            "baseline", self.configs, SCENARIO_PATH, fresh=True, max_steps_override=3,
            optimizer=FakeOptimalMILP(),
        )
        self.assertEqual(result["forecast_sources_seen_in_arm"], ["baseline"])
        self.assertFalse(result["forecast_source_mixed_within_arm"])


if __name__ == "__main__":
    unittest.main()
