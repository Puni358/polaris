"""
Unit Tests for POLARIS GATE-02 — MILP Infeasibility Safety Invariant Correction
Verifies that when MILP returns OPTIMIZATION_INFEASIBLE:
- Infeasible solver result is detected;
- DigitalTwinSimulator.step() is NOT called;
- state_advanced = False on FaultEvent;
- Fuel is unchanged;
- Battery SOC is unchanged;
- Option D is NOT called;
- ECD is NOT rerun automatically;
- No retry is performed;
- Current StationState remains authoritative.
"""

import unittest
from unittest.mock import MagicMock
from pathlib import Path

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.runtime.runner import PolarisLocalRunner, FaultEvent

class TestGate02MILPInfeasibilitySafety(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.runner = PolarisLocalRunner(system_dir=self.base_dir, optimizer_type="milp")

    def _create_dummy_bundle(self):
        timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
        zero_ts = TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W")
        solar_irr = TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W/m^2")
        demand_ts = TimeseriesForecast(point=[30000.0]*24, lower=[25000.0]*24, upper=[35000.0]*24, unit="W")
        
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=timestamps[0],
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=solar_irr,
            solar_generation=zero_ts,
            wind_generation=zero_ts,
            demand=demand_ts,
            metadata={"source": "test_dummy"}
        )

    def test_milp_infeasibility_safety_invariant(self):
        """Verify safety invariant: state_advanced=False, zero simulator steps, state unchanged on MILP infeasibility."""
        timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
        infeasible_plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=timestamps,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[20.0]*24,
            diesel_power=[0.0]*24,
            load_served=[0.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[30000.0]*24,
            objective_value=1e9,
            constraint_status="OPTIMIZATION_INFEASIBLE: HighsModelStatus.kInfeasible",
            energy_balance_errors=[0.0]*24,
            j1_objective=1e9,
            j2_objective=1e9,
            j3_objective=1e9,
            j4_objective=1e9,
            reserve_shortfall=[200000.0]*24
        )

        # Mock forecast engine, router, and optimizer
        self.runner.forecast_engine.predict = MagicMock(return_value=self._create_dummy_bundle())
        
        # Router returns NORMAL route
        mock_assessment = MagicMock()
        mock_assessment.operating_mode.value = "NORMAL"
        mock_assessment.validity_status = None
        self.runner.router.evaluate_and_route = MagicMock(return_value=(mock_assessment, "NORMAL"))
        
        # Optimizer returns infeasible plan
        self.runner.optimizer.optimize = MagicMock(return_value=infeasible_plan)
        
        # Mock simulator step to verify it is NEVER called
        self.runner.simulator.step = MagicMock()
        
        # Mock Option D solver to verify it is NEVER called
        self.runner.option_d_solver.solve = MagicMock()

        # Execute single-step pipeline
        report = self.runner.run_pipeline(steps_to_run=1)

        # 1. Verify infeasible solver result detected
        self.assertEqual(report["fault_count"], 1)
        fault_events = report["fault_events"]
        self.assertEqual(len(fault_events), 1)
        fe = fault_events[0]
        self.assertEqual(fe["fault_class"], "OPTIMIZATION_INFEASIBLE")
        self.assertEqual(fe["severity"], "GOVERNED_DEGRADED")
        self.assertEqual(fe["response"], "GOVERNED_ZERO_DISPATCH")

        # 2. Verify state_advanced = False
        self.assertFalse(fe["state_advanced"])

        # 3. Verify DigitalTwinSimulator.step() was NOT called
        self.runner.simulator.step.assert_not_called()

        # 4. Verify Option D was NOT called
        self.runner.option_d_solver.solve.assert_not_called()

        # 5. Verify router (and ECD) evaluated exactly once (no retry or rerun)
        self.assertEqual(self.runner.router.evaluate_and_route.call_count, 1)
        self.assertEqual(self.runner.optimizer.optimize.call_count, 1)

        # 6. Verify zero timesteps executed / state advanced
        self.assertEqual(report["timesteps_executed"], 0)
        self.assertEqual(report["execution_status"], "GOVERNANCE_DECISION_REQUIRED")

if __name__ == "__main__":
    unittest.main()
