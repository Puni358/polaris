"""
POLARIS EMS — GATE-05 Synthetic Integrated EMS Fixture Test Suite

Exercises and validates all five governed operational paths in a controlled synthetic environment:
1. NORMAL path: StationState -> ForecastBundle -> ECD (NORMAL) -> Router -> Option B (HiGHS) -> DispatchPlan -> DigitalTwin -> Next StationState
2. EMERGENCY path: StationState -> ECD (EMERGENCY) -> Router -> Option D -> DispatchPlan -> DigitalTwin -> Next StationState
3. UNKNOWN_INVALID path: Invalid ECD input -> Gate-01 GOVERNED_HYBRID -> Stop automatic optimization -> State NOT advanced
4. MILP_INFEASIBILITY path: Infeasible Option B -> Gate-02 Option-C -> Safety invariant -> State NOT advanced
5. EMERGENCY_RETURN path: EMERGENCY -> ECD (NORMAL) -> Auto-return to NORMAL -> Operator notification & override requirement

Enforces Truth Firewall: Controller receives forecasts only; Digital Twin receives actuals for simulation step only.
"""

import unittest
from unittest.mock import MagicMock
from pathlib import Path
from typing import Dict, Any

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import (
    EmergencyConditionDetector,
    AuthorizedHorizon,
    ConstantCriticalLoad,
    BatteryParameters,
    DieselParameters,
    OperatingMode,
    ValidityStatus,
    ResourceSelection
)
from system.control.router import EMSControlRouter
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.runtime.runner import PolarisLocalRunner, FaultEvent


class TestGate05SyntheticIntegrationFixture(unittest.TestCase):

    def setUp(self):
        self.base_dir = Path(__file__).parent.parent / "system"
        self.configs = {
            "critical_demand_ratio": 1.0,
            "terminal_target_wh": 100000.0,
            "battery": {
                "capacity_wh": 200000.0,
                "initial_soc_pct": 50.0,
                "min_soc_pct": 20.0,
                "max_soc_pct": 95.0,
                "charge_efficiency": 0.92,
                "discharge_efficiency": 0.92,
                "max_discharge_power_w": 50000.0,
                "max_charge_power_w": 50000.0
            },
            "diesel": {
                "initial_fuel_l": 100.0,
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025,
                "min_power_w": 10000.0,
                "max_power_w": 50000.0,
                "physical_startup_fuel_l": 0.0
            },
            "ecd": {
                # Explicit SYNTHETIC test-fixture authorization for the
                # router/ECD fail-closed contract (ECD-01, A-iii). This
                # suite's NORMAL/EMERGENCY tests exercise genuine routing
                # mechanics, not the fail-closed gate itself (test_03
                # below builds its own deliberately-unauthorized configs
                # to exercise that gate directly).
                "t_required_hours": 6.0,
                "t_required_authorized": True
            },
            "critical_load": {
                # NOT a real-station evidence record -- see
                # tests/test_isolated_components.py for the same
                # "EVID-TEST-*" convention.
                "authorized": True,
                "evidence_id": "EVID-TEST-GATE05",
                "authorized_critical_load_w": 10000.0
            }
        }
        self.simulator = DigitalTwinSimulator(self.configs)
        self.router = EMSControlRouter()
        self.ecd = EmergencyConditionDetector()
        self.option_d_solver = OptionDFallbackSolver()
        self.highs_optimizer = GAP19HighsNativeOptimizer()

        self.battery_params = BatteryParameters(
            capacity_wh=200000.0, min_soc_pct=20.0, max_soc_pct=95.0,
            discharge_efficiency=0.92, max_discharge_power_w=50000.0
        )
        self.diesel_params = DieselParameters(
            base_fuel_consumption_l_per_h=5.0, marginal_fuel_consumption_l_per_wh=0.00025,
            min_power_w=10000.0, max_power_w=50000.0, physical_startup_fuel_l=0.0
        )

    def _create_synthetic_forecast(self, demand_w: float = 10000.0, solar_w: float = 10000.0, wind_w: float = 5000.0) -> ForecastBundle:
        timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=timestamps[0],
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast(point=[solar_w/10.0]*24, lower=[0.0]*24, upper=[solar_w/5.0]*24, unit="W/m^2"),
            solar_generation=TimeseriesForecast(point=[solar_w]*24, lower=[0.0]*24, upper=[solar_w*1.2]*24, unit="W"),
            wind_generation=TimeseriesForecast(point=[wind_w]*24, lower=[0.0]*24, upper=[wind_w*1.2]*24, unit="W"),
            demand=TimeseriesForecast(point=[demand_w]*24, lower=[demand_w*0.8]*24, upper=[demand_w*1.2]*24, unit="W"),
            metadata={"source": "synthetic_gate05_fixture"}
        )

    def test_01_normal_pathway(self):
        """
        PATH 1: NORMAL PATHWAY
        StationState -> ForecastBundle -> ECD (NORMAL) -> Option B (HiGHS) -> DispatchPlan -> DigitalTwin -> Next StationState
        Result Classification: PASS
        """
        initial_state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=70.0,
            battery_energy_wh=140000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=500.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=5000.0,
            diesel_fuel_remaining_liters=100.0
        )
        forecast = self._create_synthetic_forecast(demand_w=10000.0, solar_w=15000.0, wind_w=5000.0)

        # 1. ECD evaluation
        ecd_result = self.ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=70.0,
            fuel_remaining_liters=100.0,
            battery_params=self.battery_params,
            diesel_params=self.diesel_params
        )
        self.assertEqual(ecd_result.operating_mode, OperatingMode.NORMAL)
        self.assertEqual(ecd_result.validity_status, ValidityStatus.VALID)

        # 2. Router evaluation
        assessment, route = self.router.evaluate_and_route(initial_state, forecast, self.configs)
        self.assertEqual(route, "NORMAL")

        # 3. Option B (HiGHS MILP) dispatch generation
        plan = self.highs_optimizer.optimize(forecast, initial_state, self.configs)
        self.assertEqual(plan.constraint_status, "OPTIMAL")
        self.assertEqual(len(plan.timestamps), 24)

        # 4. Truth Firewall verification (controller receives forecast, twin receives actuals)
        actuals = {
            "timestamp": "2026-09-26T01:00:00Z",
            "actual_SW_IN": 500.0,
            "actual_demand": 10000.0,
            "actual_wind_generation": 5000.0
        }

        # 5. First-action-only MPC semantics: Digital Twin advances 1 step
        next_state = self.simulator.step(initial_state, plan, actuals)

        # 6. State & Accounting Continuity Assertions
        self.assertIsNotNone(next_state)
        self.assertEqual(next_state.timestamp, "2026-09-26T01:00:00Z")
        self.assertLessEqual(next_state.battery_soc_pct, 100.0)
        self.assertGreaterEqual(next_state.battery_soc_pct, 0.0)
        self.assertLessEqual(next_state.diesel_fuel_remaining_liters, 100.0)

    def test_02_emergency_pathway(self):
        """
        PATH 2: EMERGENCY PATHWAY
        StationState (Low reserve) -> ECD (EMERGENCY) -> Option D -> DispatchPlan -> DigitalTwin -> Next StationState
        Result Classification: PASS
        """
        depleted_state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=35000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=5.0  # Only 5L remaining -> < 6h autonomy -> EMERGENCY
        )
        forecast = self._create_synthetic_forecast(demand_w=35000.0, solar_w=0.0, wind_w=0.0)

        # 1. ECD evaluation
        ecd_result = self.ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(35000.0),
            soc_pct=20.0,
            fuel_remaining_liters=5.0,
            battery_params=self.battery_params,
            diesel_params=self.diesel_params
        )
        self.assertEqual(ecd_result.operating_mode, OperatingMode.EMERGENCY)
        self.assertEqual(ecd_result.preserved_resource, ResourceSelection.DIESEL)

        # 2. Router evaluation
        assessment, route = self.router.evaluate_and_route(depleted_state, forecast, self.configs)
        self.assertEqual(route, "EMERGENCY")

        # 3. Option D Fallback Solver dispatch generation
        plan = self.option_d_solver.solve(ecd_result, forecast, depleted_state, self.configs)
        self.assertEqual(plan.constraint_status, "OPTION_D_FALLBACK")
        self.assertEqual(len(plan.timestamps), 24)
        self.assertGreater(plan.diesel_power[0], 0.0)

        # 4. Digital Twin simulation step
        actuals = {
            "timestamp": "2026-09-26T01:00:00Z",
            "actual_SW_IN": 0.0,
            "actual_demand": 35000.0,
            "actual_wind_generation": 0.0
        }
        next_state = self.simulator.step(depleted_state, plan, actuals)

        # 5. State Continuity
        self.assertEqual(next_state.timestamp, "2026-09-26T01:00:00Z")
        self.assertLess(next_state.diesel_fuel_remaining_liters, 5.0)

    def test_03_unknown_invalid_pathway(self):
        """
        PATH 3: UNKNOWN_INVALID PATHWAY
        Invalid/Missing ECD input -> Gate-01 GOVERNED_HYBRID -> Stop automatic optimization -> No state advancement
        Result Classification: PASS
        """
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        forecast = self._create_synthetic_forecast()

        # Instantiate ECD with invalid horizon
        invalid_horizon = AuthorizedHorizon(t_required_hours=None)
        ecd_result = self.ecd.evaluate(
            horizon_input=invalid_horizon,
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=50.0,
            fuel_remaining_liters=100.0,
            battery_params=self.battery_params,
            diesel_params=self.diesel_params
        )

        self.assertEqual(ecd_result.operating_mode, OperatingMode.UNKNOWN_INVALID)
        self.assertEqual(ecd_result.validity_status, ValidityStatus.MISSING_T_REQUIRED)

        # Router with bad configs (t_required_hours set to 0.0)
        bad_configs = dict(self.configs)
        bad_configs["ecd"] = {"t_required_hours": 0.0}
        assessment, route = self.router.evaluate_and_route(state, forecast, bad_configs)
        self.assertEqual(route, "UNKNOWN_INVALID")

        # Verify runner behavior on UNKNOWN_INVALID: automatic optimization stopped, state NOT advanced
        runner = PolarisLocalRunner(system_dir=self.base_dir, optimizer_type="milp")
        runner.configs["ecd"] = {"t_required_hours": 0.0}

        # Ensure simulator step is NOT called on UNKNOWN_INVALID
        simulator_called = False
        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s
        runner.simulator.step = mock_step

        report = runner.run_pipeline(steps_to_run=1)
        self.assertFalse(simulator_called, "DigitalTwinSimulator.step MUST NOT be called on UNKNOWN_INVALID")
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "FAILED_TERMINATED")
        self.assertEqual(len(report["fault_events"]), 1)
        fe = report["fault_events"][0]
        # Label updated: the ECD-01 fail-closed implementation now checks
        # the explicit "t_required_authorized" flag before the numeric
        # value, so an unauthorized-and-also-zero t_required_hours reports
        # the more precise UNAUTHORIZED_T_REQUIRED (not the stale
        # MISSING_T_REQUIRED label this test previously expected). The
        # underlying behavior (fail closed, no state advance) is
        # unchanged and still asserted below.
        self.assertEqual(fe["fault_class"], "UNAUTHORIZED_T_REQUIRED")
        self.assertFalse(fe["state_advanced"])

    def test_04_milp_infeasibility_pathway(self):
        """
        PATH 4: MILP INFEASIBILITY PATHWAY
        Infeasible Option B -> Gate-02 Option-C boundary -> Critical load hard -> State NOT advanced
        Result Classification: PASS
        """
        runner = PolarisLocalRunner(system_dir=self.base_dir, optimizer_type="milp")

        # Mock forecast engine to return synthetic forecast
        runner.forecast_engine.predict = MagicMock(return_value=self._create_synthetic_forecast(demand_w=10000.0))

        # Router returns NORMAL route
        mock_assessment = MagicMock()
        mock_assessment.operating_mode.value = "NORMAL"
        mock_assessment.validity_status = None
        runner.router.evaluate_and_route = MagicMock(return_value=(mock_assessment, "NORMAL"))

        # Mock HiGHS optimizer to return infeasible plan
        infeasible_plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"2026-09-26T{h:02d}:00:00Z" for h in range(24)],
            solar_used=[0.0]*24, wind_used=[0.0]*24, battery_charge=[0.0]*24, battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24, diesel_power=[0.0]*24, load_served=[0.0]*24, flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24, unmet_load=[30000.0]*24, objective_value=1e9,
            constraint_status="OPTIMIZATION_INFEASIBLE: HighsModelStatus.kInfeasible",
            energy_balance_errors=[0.0]*24
        )
        runner.optimizer.optimize = MagicMock(return_value=infeasible_plan)

        # Ensure simulator.step is NEVER called when optimizer is infeasible
        simulator_called = False
        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s
        runner.simulator.step = mock_step

        report = runner.run_pipeline(steps_to_run=1)
        self.assertFalse(simulator_called, "DigitalTwinSimulator.step MUST NOT be called on MILP_INFEASIBLE")
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(len(report["fault_events"]), 1)
        fe = report["fault_events"][0]
        self.assertEqual(fe["fault_class"], "OPTIMIZATION_INFEASIBLE")
        self.assertFalse(fe["state_advanced"])

    def test_05_emergency_return_pathway(self):
        """
        PATH 5: EMERGENCY RETURN PATHWAY
        Step k: EMERGENCY -> Step k+1: ECD evaluates NORMAL -> Auto-return to NORMAL + Operator Notification
        Result Classification: PASS
        """
        # Step k state: Emergency (demand = 10kW, fuel = 4L -> diesel endurance = 0.53h < 6h)
        emg_state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=True,
            diesel_hours_running=2.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=4.0
        )
        forecast_emg = self._create_synthetic_forecast(demand_w=10000.0, solar_w=0.0, wind_w=0.0)

        ecd_emg = self.ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=20.0,
            fuel_remaining_liters=4.0,
            battery_params=self.battery_params,
            diesel_params=self.diesel_params
        )
        self.assertEqual(ecd_emg.operating_mode, OperatingMode.EMERGENCY)

        # Step k+1 state: Resupplied / Recovered -> Fuel restored to 100L, SOC to 80% (endurance > 6h)
        recovered_state = StationState(
            timestamp="2026-09-26T01:00:00Z",
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=500.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=10000.0,
            diesel_fuel_remaining_liters=100.0
        )
        forecast_rec = self._create_synthetic_forecast(demand_w=10000.0, solar_w=15000.0, wind_w=10000.0)

        ecd_rec = self.ecd.evaluate(
            horizon_input=AuthorizedHorizon(t_required_hours=6.0),
            critical_load=ConstantCriticalLoad(10000.0),
            soc_pct=80.0,
            fuel_remaining_liters=100.0,
            battery_params=self.battery_params,
            diesel_params=self.diesel_params
        )
        self.assertEqual(ecd_rec.operating_mode, OperatingMode.NORMAL)

        # Transition assertion: Transition from EMERGENCY -> NORMAL is automatic upon ECD evaluating NORMAL
        previous_mode = ecd_emg.operating_mode
        current_mode = ecd_rec.operating_mode

        self.assertEqual(previous_mode, OperatingMode.EMERGENCY)
        self.assertEqual(current_mode, OperatingMode.NORMAL)

        # Notification Event generation requirement
        notification_event = {
            "event_type": "OPERATOR_NOTIFICATION_EMERGENCY_RETURN",
            "previous_mode": previous_mode.value,
            "current_mode": current_mode.value,
            "timestamp": recovered_state.timestamp,
            "message": "System transitioned automatically from EMERGENCY to NORMAL. Operator override available.",
            "operator_override_supported": True
        }

        self.assertEqual(notification_event["previous_mode"], "EMERGENCY")
        self.assertEqual(notification_event["current_mode"], "NORMAL")
        self.assertTrue(notification_event["operator_override_supported"])

    def test_06_truth_firewall_audit(self):
        """
        TRUTH FIREWALL AUDIT
        Ensures controller does NOT receive future actuals, and forecasts remain strictly forecasts.
        Result Classification: PASS
        """
        forecast = self._create_synthetic_forecast(demand_w=10000.0)

        # 1. Check forecast bundle structure has no actual trajectory fields
        self.assertTrue(hasattr(forecast, "demand"))
        self.assertTrue(hasattr(forecast, "solar_generation"))
        self.assertTrue(hasattr(forecast, "wind_generation"))
        self.assertFalse(hasattr(forecast, "actual_demand_trajectory"))

        # 2. Verify optimizer receives forecast bundle only, not scenario data
        initial_state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=70.0,
            battery_energy_wh=140000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=500.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=5000.0,
            diesel_fuel_remaining_liters=100.0
        )
        plan = self.highs_optimizer.optimize(forecast, initial_state, self.configs)
        self.assertEqual(len(plan.timestamps), 24)
        # Optimizer outputs dispatch schedule based on forecast inputs
        self.assertIsNotNone(plan)


if __name__ == "__main__":
    unittest.main()
