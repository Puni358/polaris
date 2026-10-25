"""
Tests for the Candidate 2 checkpointed-runner infrastructure (atomic writes,
contiguous-prefix resume detection, progress reporting) in isolation from the
expensive MILP solve itself.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = PROJECT_ROOT / "forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION" / "run_candidate2_checkpointed.py"

sys.path.insert(0, str(PROJECT_ROOT / "forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION"))
sys.path.insert(0, str(PROJECT_ROOT))

spec = importlib.util.spec_from_file_location("run_candidate2_checkpointed", MODULE_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class TestCheckpointInfra(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.ckpt_dir = Path(self._tmpdir.name) / "checkpoints"
        self.progress_path = Path(self._tmpdir.name) / "PROGRESS.json"
        self._orig_ckpt_dir = runner.CHECKPOINT_DIR
        self._orig_progress_path = runner.PROGRESS_PATH
        runner.CHECKPOINT_DIR = self.ckpt_dir
        runner.PROGRESS_PATH = self.progress_path
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        runner.CHECKPOINT_DIR = self._orig_ckpt_dir
        runner.PROGRESS_PATH = self._orig_progress_path
        self._tmpdir.cleanup()

    def test_atomic_write_produces_valid_json_never_partial(self):
        path = self.ckpt_dir / "step_0000.json"
        runner.atomic_write_json(path, {"step": 0, "value": 42})
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text()), {"step": 0, "value": 42})
        tmp_files = list(self.ckpt_dir.glob("*.tmp*"))
        self.assertEqual(tmp_files, [])

    def test_list_completed_steps_contiguous_prefix_only(self):
        for i in [0, 1, 2]:
            runner.atomic_write_json(runner.checkpoint_path(i), {"step": i})
        # Gap at step 3: step 4 exists but 3 doesn't.
        runner.atomic_write_json(runner.checkpoint_path(4), {"step": 4})
        self.assertEqual(runner.list_completed_steps(), [0, 1, 2])

    def test_list_completed_steps_ignores_corrupt_trailing_checkpoint(self):
        runner.atomic_write_json(runner.checkpoint_path(0), {"step": 0})
        runner.atomic_write_json(runner.checkpoint_path(1), {"step": 1})
        (runner.checkpoint_path(2)).write_text("{not valid json")
        self.assertEqual(runner.list_completed_steps(), [0, 1])

    def test_write_progress_atomic_and_readable(self):
        runner.write_progress(5, 168, "running", {"solve_time_ms": 12.3})
        payload = json.loads(self.progress_path.read_text())
        self.assertEqual(payload["step"], 5)
        self.assertEqual(payload["total_steps"], 168)
        self.assertEqual(payload["status"], "running")
        self.assertIn("updated_at_utc", payload)

    def test_resume_uses_state_after_of_last_contiguous_checkpoint(self):
        from system.schemas.station_state import StationState

        state0 = StationState(
            timestamp="2024-06-01T00:00:00Z", battery_soc_pct=50.0, battery_energy_wh=100000.0,
            diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0, last_observed_wind_generation=0.0, diesel_fuel_remaining_liters=100.0,
        )
        state1 = StationState(
            timestamp="2024-06-01T01:00:00Z", battery_soc_pct=48.3, battery_energy_wh=96600.0,
            diesel_running=True, diesel_hours_running=1.0, last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0, last_observed_wind_generation=0.0, diesel_fuel_remaining_liters=94.5,
        )
        runner.atomic_write_json(runner.checkpoint_path(0), {
            "step": 0, "state_before": state0.to_dict(), "state_after": state1.to_dict(),
            "per_step_summary": {"step": 0}, "dispatch_plan": {}, "forecast_bundle": {}, "actual_scenario": [],
        })

        completed = runner.list_completed_steps()
        self.assertEqual(completed, [0])
        last_ckpt = runner.load_checkpoint(completed[-1])
        resumed_state = StationState.from_dict(last_ckpt["state_after"])
        self.assertEqual(resumed_state.battery_energy_wh, 96600.0)
        self.assertEqual(resumed_state.diesel_fuel_remaining_liters, 94.5)
        self.assertTrue(resumed_state.diesel_running)


if __name__ == "__main__":
    unittest.main()
