"""
Regression test for the step-82 Candidate 2 frozen-forecast failure:

    OPTIMIZATION_RUNTIME_FAILURE (step 82): DispatchPlan violates charge/discharge
    exclusivity at index 8: charge=0.04, discharge=45942.94.

Root cause (forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION/diagnostics_step82): HiGHS
returns binary decision variables within its integrality tolerance of 0/1
rather than exactly 0/1 (observed: u_chg ~= 7.8e-7 instead of 0.0). Constraint
5 (p_chg <= max_p_chg * u_chg) is then satisfied by a tiny nonzero p_chg
(~0.039W) even though the binary "means" charging is off, and if u_dis == 1
with a large p_dis in the same hour, DispatchPlan's exclusivity check
(battery_charge > 1e-3 and battery_discharge > 1e-3) raises.

This test does not re-solve the step-82 MILP (that requires full scenario
replay); it isolates the post-solve snapping logic in LocalMILPEnergyOptimizer
by stubbing scipy's milp() to return the exact pathological raw vector from
the forensic diagnostic, and asserts the returned DispatchPlan is valid and
physically correct instead of raising.
"""
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import numpy as np

from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState


def _make_bundle() -> ForecastBundle:
    timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
    zero = TimeseriesForecast(point=[0.0] * 24, lower=[0.0] * 24, upper=[0.0] * 24, unit="W")
    irr = TimeseriesForecast(point=[0.0] * 24, lower=[0.0] * 24, upper=[0.0] * 24, unit="W/m^2")
    demand = TimeseriesForecast(point=[30000.0] * 24, lower=[25000.0] * 24, upper=[35000.0] * 24, unit="W")
    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=timestamps[0],
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=irr,
        solar_generation=zero,
        wind_generation=zero,
        demand=demand,
        metadata={},
    )


def _make_station_state() -> StationState:
    return StationState(
        timestamp="2026-09-26T00:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=True,
        diesel_hours_running=5.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=30000.0,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=100.0,
    )


class TestMILPBinarySnapping(unittest.TestCase):
    def test_near_zero_binary_does_not_trip_exclusivity(self):
        """Known step-82 case: u_chg~=7.8e-7, p_chg~=0.039W, u_dis=1, p_dis=45942.94W."""
        K = 15
        H = 24
        num_vars = H * K
        sol = np.zeros(num_vars)

        pathological_hour = 8
        for t in range(H):
            base = t * K
            if t == pathological_hour:
                sol[base + 4] = 0.039       # p_chg (numerical noise)
                sol[base + 5] = 45942.94    # p_dis
                sol[base + 11] = 7.8e-7     # u_chg (should-be-zero binary)
                sol[base + 12] = 1.0        # u_dis
            sol[base + 13] = 1.0            # u_diesel
            sol[base + 7] = 15000.0         # p_diesel
            sol[base + 8] = 15000.0         # p_served
            sol[base + 6] = 50000.0         # E_next

        fake_result = SimpleNamespace(
            success=True,
            status=0,
            message="Optimal",
            x=sol,
            fun=1234.5,
        )

        optimizer = LocalMILPEnergyOptimizer()
        config = {
            "battery": {"capacity_wh": 200000.0},
            "diesel": {},
            "loads": {},
            "optimizer": {},
        }

        with patch("system.optimization.implementations.milp.milp", return_value=fake_result):
            plan = optimizer.optimize(_make_bundle(), _make_station_state(), config)

        self.assertEqual(plan.constraint_status, "OPTIMAL")
        self.assertEqual(plan.battery_charge[pathological_hour], 0.0)
        self.assertEqual(plan.battery_discharge[pathological_hour], 45942.94)

    def test_binary_at_exactly_one_half_rounds_up(self):
        K = 15
        H = 24
        num_vars = H * K
        sol = np.zeros(num_vars)
        for t in range(H):
            base = t * K
            sol[base + 13] = 1.0
            sol[base + 7] = 15000.0
            sol[base + 8] = 15000.0
            sol[base + 6] = 50000.0
        sol[0 * K + 11] = 0.5
        sol[0 * K + 4] = 25000.0

        fake_result = SimpleNamespace(success=True, status=0, message="Optimal", x=sol, fun=0.0)
        optimizer = LocalMILPEnergyOptimizer()
        config = {"battery": {"capacity_wh": 200000.0}, "diesel": {}, "loads": {}, "optimizer": {}}

        with patch("system.optimization.implementations.milp.milp", return_value=fake_result):
            plan = optimizer.optimize(_make_bundle(), _make_station_state(), config)

        self.assertEqual(plan.battery_charge[0], 25000.0)


if __name__ == "__main__":
    unittest.main()
