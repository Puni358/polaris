"""
Isolated Synthetic Component Tests for POLARIS GAP19 ECD -> Option D
Validates isolated component interfaces (Router, Option D Solver, Digital Twin Simulator)
without running full multi-cycle MPC or 24h EMS pipeline.
"""

import unittest
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.control.ecd import EmergencyConditionDetector, OperatingMode, ResourceSelection
from system.control.router import EMSControlRouter
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator

class TestIsolatedComponents(unittest.TestCase):
    def setUp(self):
        self.config = {
            "battery": {
                "capacity_wh": 200000.0,
                "min_soc_pct": 20.0,
                "max_soc_pct": 95.0,
                "charge_efficiency": 0.92,
                "discharge_efficiency": 0.92,
                "max_charge_power_w": 50000.0,
                "max_discharge_power_w": 50000.0
            },
            "diesel": {
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025,
                "initial_fuel_l": 100.0,
                "min_power_w": 10000.0,
                "max_power_w": 50000.0,
                "physical_startup_fuel_l": 0.0
            },
            "ecd": {
                # Explicit authorization required by the ECD-01 fail-closed
                # implementation (Decision A = A-iii) -- without this flag,
                # evaluate_and_route() fails closed to UNKNOWN_INVALID
                # regardless of t_required_hours's numeric value.
                "t_required_hours": 6.0,
                "t_required_authorized": True
            },
            "critical_load": {
                # Explicit authorization required by the ECD-01 fail-closed
                # implementation (Decision B = B-iii). This is a synthetic
                # test fixture value, NOT a real-station measurement; it is
                # labeled with a placeholder EVID-xx id only so these isolated
                # component tests can continue to exercise genuine NORMAL/
                # EMERGENCY classification and dispatch mechanics.
                "authorized": True,
                "evidence_id": "EVID-TEST-ISOLATED",
                "authorized_critical_load_w": 10000.0
            }
        }
        self.router = EMSControlRouter()
        self.solver = OptionDFallbackSolver()
        self.simulator = DigitalTwinSimulator(self.config)

    def _create_bundle(self, demand=20000.0, solar=0.0):
        timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=timestamps[0],
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast(point=[solar]*24, lower=[solar]*24, upper=[solar]*24, unit="W/m^2"),
            solar_generation=TimeseriesForecast(point=[solar]*24, lower=[solar]*24, upper=[solar]*24, unit="W"),
            wind_generation=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W"),
            demand=TimeseriesForecast(point=[demand]*24, lower=[demand]*24, upper=[demand]*24, unit="W"),
            metadata={"source": "isolated_test"}
        )

    def test_isolated_router_normal(self):
        bundle = self._create_bundle(demand=10000.0)
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0
        )
        assessment, route = self.router.evaluate_and_route(state, bundle, self.config)
        self.assertEqual(route, "NORMAL")
        self.assertEqual(assessment.operating_mode, OperatingMode.NORMAL)

    def test_isolated_router_emergency(self):
        bundle = self._create_bundle(demand=40000.0)
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=40000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=1.0
        )
        assessment, route = self.router.evaluate_and_route(state, bundle, self.config)
        self.assertEqual(route, "EMERGENCY")
        self.assertEqual(assessment.operating_mode, OperatingMode.EMERGENCY)

    def test_isolated_option_d_solver_generation(self):
        bundle = self._create_bundle(demand=25000.0, solar=10000.0)
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=10000.0,
            last_observed_demand=25000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=50.0
        )
        assessment, route = self.router.evaluate_and_route(state, bundle, self.config)
        plan = self.solver.solve(assessment, bundle, state, self.config)
        self.assertEqual(len(plan.timestamps), 24)
        self.assertEqual(plan.constraint_status, "OPTION_D_FALLBACK")
        self.assertAlmostEqual(plan.solar_used[0], 10000.0, places=2)
        # Diesel fills remaining 15 kW
        self.assertAlmostEqual(plan.diesel_power[0], 15000.0, places=2)

    def test_isolated_simulator_step(self):
        state = StationState(
            timestamp="2026-09-26T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=20000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=50.0
        )
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=[state.timestamp]*24,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[20000.0]*24,
            load_served=[20000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[0.0]*24,
            objective_value=0.0,
            constraint_status="FEASIBLE",
            energy_balance_errors=[0.0]*24
        )
        actuals = {"timestamp": "2026-09-26T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 20000.0, "actual_wind_generation": 0.0}
        next_state = self.simulator.step(state, plan, actuals)
        self.assertEqual(next_state.timestamp, "2026-09-26T01:00:00Z")
        self.assertAlmostEqual(next_state.diesel_fuel_remaining_liters, 40.0, places=2)

if __name__ == "__main__":
    unittest.main()
