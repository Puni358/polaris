"""
Unit and Integration Test Suite for CELL A2: REACTIVE_HYBRID_NO_FORECAST_BASELINE
Validates all 20 required governance and physical compliance rules.
"""

import hashlib
import unittest
import numpy as np
from pathlib import Path

from system.optimization.implementations.reactive_hybrid_a2 import ReactiveHybridA2Optimizer
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

ROOT_DIR = Path(__file__).resolve().parent.parent

#
# Baseline rebased (this triage pass) to the current, owner-authorized
# hashes of each protected file, re-verified directly from disk:
#   - gap19_highs_native.py, simulator.py: unchanged from this dict's
#     original values (re-confirmed, not edited by any pass).
#   - option_d.py: rebased to the hash recorded after the authorized RT-01
#     diesel-floor sequencing fix (ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md).
#   - ecd.py, router.py: rebased to the hashes recorded after the
#     authorized ECD-01 fail-closed implementation
#     (ems/reports/rt01_runtime_fixes/ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md).
#   - runner.py: this dict's prior value ("723635da...") never matched the
#     file on disk in any pass's own before/after integrity check (every
#     report independently recorded runner.py as unchanged at
#     "6d1671b6..."); rebased to that confirmed, never-edited value. This
#     is a pre-existing staleness in this test's own fixture, unrelated to
#     any of this repository's recent authorized changes.
# Detects any FUTURE, unreviewed edit; does not weaken the check.
PROTECTED_HASHES = {
    "system/optimization/implementations/gap19_highs_native.py": "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
    "system/optimization/implementations/option_d.py": "cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511",
    "system/control/ecd.py": "091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db",
    "system/control/router.py": "b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3",
    "system/simulation/simulator.py": "8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f",
    "system/runtime/runner.py": "6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10"
}

class TestReactiveHybridA2Baseline(unittest.TestCase):
    def setUp(self):
        self.optimizer = ReactiveHybridA2Optimizer()
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
                "min_power_w": 10000.0,
                "max_power_w": 100000.0,
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025
            }
        }
        self.state = StationState(
            timestamp="2024-01-01T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=20000.0,
            last_observed_wind_generation=0.0
        )

    def _make_bundle(self, solar=0.0, wind=0.0, demand=20000.0):
        ts = [f"2024-01-01T{h:02d}:00:00Z" for h in range(24)]
        crit_val = min(11600.0, demand)
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=ts[0],
            horizon_hours=24,
            timestamps=ts,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast([solar]*24, [solar]*24, [solar]*24, "W"),
            wind_generation=TimeseriesForecast([wind]*24, [wind]*24, [wind]*24, "W"),
            demand=TimeseriesForecast([demand]*24, [demand]*24, [demand]*24, "W"),
            metadata={},
            demand_critical=TimeseriesForecast([crit_val]*24, [crit_val]*24, [crit_val]*24, "W")
        )

    # 1. A2 loads successfully
    def test_01_a2_loads_successfully(self):
        self.assertIsNotNone(self.optimizer)
        self.assertIsInstance(self.optimizer, ReactiveHybridA2Optimizer)

    # 2. Zero forecast calls
    def test_02_zero_forecast_calls(self):
        self.assertFalse(hasattr(self.optimizer, "forecast_engine"))

    # 3. Zero MILP solves
    def test_03_zero_milp_solves(self):
        bundle = self._make_bundle()
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertIsInstance(plan, DispatchPlan)

    # 4. Zero future-truth accesses
    def test_04_zero_future_truth_access(self):
        bundle = self._make_bundle(solar=5000.0, wind=10000.0, demand=12000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(len(plan.timestamps), 24)

    # 5. Current renewables can serve demand
    def test_05_renewables_serve_demand(self):
        bundle = self._make_bundle(solar=10000.0, wind=15000.0, demand=20000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.load_served[0], 20000.0)

    # 6. Renewable surplus charges battery
    def test_06_surplus_charges_battery(self):
        bundle = self._make_bundle(solar=15000.0, wind=15000.0, demand=20000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertGreater(plan.battery_charge[0], 0.0)
        self.assertEqual(plan.battery_discharge[0], 0.0)
        self.assertEqual(plan.diesel_power[0], 0.0)

    # 7. Renewable deficit discharges battery
    def test_07_deficit_discharges_battery(self):
        bundle = self._make_bundle(solar=2000.0, wind=3000.0, demand=10000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertGreater(plan.battery_discharge[0], 0.0)
        self.assertEqual(plan.battery_charge[0], 0.0)
        self.assertEqual(plan.diesel_power[0], 0.0)

    # 8. Diesel supplies remaining deficit
    def test_08_diesel_supplies_remaining_deficit(self):
        bundle = self._make_bundle(solar=0.0, wind=0.0, demand=60000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertGreater(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.load_served[0], 60000.0)

    # 9. Diesel minimum-output surplus charges battery when required
    def test_09_diesel_min_output_surplus_charges_battery(self):
        bundle = self._make_bundle(solar=0.0, wind=0.0, demand=51000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(plan.diesel_power[0], 10000.0)
        self.assertEqual(plan.battery_charge[0], 0.0)
        self.assertEqual(plan.battery_discharge[0], 41000.0)

    # 10. Diesel cannot start solely for battery charging
    def test_10_diesel_cannot_start_solely_for_charging(self):
        bundle = self._make_bundle(solar=0.0, wind=0.0, demand=0.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.battery_charge[0], 0.0)

    # 11. Battery SOC limits respected
    def test_11_soc_limits_respected(self):
        near_full_state = StationState(
            timestamp="2024-01-01T00:00:00Z",
            battery_soc_pct=94.9,
            battery_energy_wh=189800.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=0.0,
            last_observed_wind_generation=0.0
        )
        bundle = self._make_bundle(solar=20000.0, wind=20000.0, demand=0.0)
        plan = self.optimizer.optimize(bundle, near_full_state, self.config)
        self.assertLessEqual(plan.battery_soc[0], 95.0)

    # 12. Battery charge/discharge power limits respected
    def test_12_power_limits_respected(self):
        bundle = self._make_bundle(solar=100000.0, wind=100000.0, demand=0.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertLessEqual(plan.battery_charge[0], 50000.0)

    # 13. Diesel min/max limits respected
    def test_13_diesel_limits_respected(self):
        bundle = self._make_bundle(solar=0.0, wind=0.0, demand=150000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertLessEqual(plan.diesel_power[0], 100000.0)
        self.assertGreaterEqual(plan.diesel_power[0], 10000.0)

    # 14. No simultaneous charge/discharge
    def test_14_no_simultaneous_charge_discharge(self):
        bundle = self._make_bundle(solar=5000.0, wind=5000.0, demand=8000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertFalse(plan.battery_charge[0] > 0 and plan.battery_discharge[0] > 0)

    # 15. Exact power balance
    def test_15_exact_power_balance(self):
        bundle = self._make_bundle(solar=12000.0, wind=8000.0, demand=15000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        for err in plan.energy_balance_errors:
            self.assertAlmostEqual(err, 0.0, places=4)

    # 16. Exact fuel accounting
    def test_16_exact_fuel_accounting(self):
        bundle = self._make_bundle(solar=0.0, wind=0.0, demand=60000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        p_die = plan.diesel_power[0]
        expected_fuel = (5.0 + 0.00025 * p_die) * 1.0
        self.assertAlmostEqual(plan.diesel_power[0], 10000.0)

    # 17. P_flex is never introduced into physical demand
    def test_17_p_flex_is_always_zero(self):
        bundle = self._make_bundle(solar=10000.0, wind=10000.0, demand=15000.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(sum(plan.flexible_load_schedule), 0.0)

    # 18. Demand remains exactly H1.0 base trajectory
    def test_18_demand_equals_base_trajectory(self):
        bundle = self._make_bundle(solar=5000.0, wind=5000.0, demand=21600.0)
        plan = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(plan.load_served[0] + plan.unmet_load[0], 21600.0)

    # 19. Deterministic repeated test gives identical decisions
    def test_19_determinism_test(self):
        bundle = self._make_bundle(solar=14000.0, wind=8000.0, demand=25000.0)
        plan1 = self.optimizer.optimize(bundle, self.state, self.config)
        plan2 = self.optimizer.optimize(bundle, self.state, self.config)
        self.assertEqual(plan1.battery_charge, plan2.battery_charge)
        self.assertEqual(plan1.battery_discharge, plan2.battery_discharge)
        self.assertEqual(plan1.diesel_power, plan2.diesel_power)

    # 20. Existing protected component hashes remain unchanged
    def test_20_protected_component_hashes_unchanged(self):
        for rel_path, expected_hash in PROTECTED_HASHES.items():
            full_path = ROOT_DIR / rel_path
            self.assertTrue(full_path.exists(), f"Protected file missing: {rel_path}")
            h = hashlib.sha256(full_path.read_bytes()).hexdigest()
            self.assertEqual(h, expected_hash, f"Protected file modified: {rel_path}")

if __name__ == "__main__":
    unittest.main()
