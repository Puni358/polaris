"""
POLARIS -- N6 Multi-Origin Harness Production-Adapter Test Suite
=====================================================================
Validates `system/evaluation/n6_multi_origin_harness/adapters.py`'s
translation-only adapter classes EXCLUSIVELY against hand-built Fake
objects whose method shapes mirror the REAL `N6SolarForecastEngine` /
`EMSControlRouter` / `GAP19HighsNativeOptimizer` / `DigitalTwinSimulator` /
`reserve_policy_guard.evaluate_dispatch_safety` / `StationState` /
`DispatchPlan` call signatures, as confirmed by direct read of
`run_n6_closed_loop_simulation.py` and the relevant schema modules this
pass (see `adapters.py`'s own module docstring for the exact line
references).

Nothing in this file imports, constructs, or calls any REAL production
class (`N6SolarForecastEngine`, `EMSControlRouter`,
`GAP19HighsNativeOptimizer`, `DigitalTwinSimulator`,
`reserve_policy_guard.evaluate_dispatch_safety`, the real `StationState`/
`DispatchPlan`/`ForecastBundle`). Every Fake below is a small, local,
hand-written stand-in with no connection to a frozen model artifact, a
sealed dataset, or any solver. None of these adapters is ever passed to
`execute_origin_dispatch_cell`, `MultiOriginCampaignHarness`, or
`execute_campaign` in this file -- that remains untouched and
unconditionally gated (see `test_n6_multi_origin_harness.py`'s own
regression tests for that).
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import unittest
from datetime import timedelta
import pandas as pd

from system.evaluation.n6_multi_origin_harness.adapters import (
    INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW,
    DispatchOutcomeView,
    ForecastBundleStepView,
    N6ForecastProviderAdapter,
    ReservePolicyGuardSafetyEvaluatorAdapter,
    RoutedOptimizerAdapter,
    SingleShotPlanSlicingSimulatorAdapter,
    StationStateCodec,
    _compute_gap19_six_hour_critical_reserve,
    _extract_and_validate_demands,
    _prepare_gap19_policy_b_config,
    _prepare_gap19_terminal_target_config,
    _validate_conformal_ebr,
    _align_timeseries_od02,
    _align_n6_bundle_od02,
    _compute_boundary_clearsky_ratio,
)


# ---------------------------------------------------------------------------
# Fakes mirroring the REAL classes' shapes (never the real classes themselves)
# ---------------------------------------------------------------------------


_STATE_UNSET = object()


class _FakeStationState:
    """Mirrors the REAL StationState's to_dict/from_dict contract only."""

    def __init__(
        self,
        timestamp,
        battery_soc_pct,
        diesel_fuel_remaining_liters=0.0,
        battery_energy_wh=_STATE_UNSET,
        terminal_target_wh_override=None,
    ):
        self.timestamp = timestamp
        self.battery_soc_pct = battery_soc_pct
        self.diesel_fuel_remaining_liters = diesel_fuel_remaining_liters
        if battery_energy_wh is _STATE_UNSET:
            self.battery_energy_wh = (
                (float(battery_soc_pct) / 100.0) * 200000.0 if battery_soc_pct is not None else None
            )
        else:
            self.battery_energy_wh = battery_energy_wh
        self.terminal_target_wh_override = terminal_target_wh_override

    def to_dict(self):
        d = {
            "timestamp": self.timestamp,
            "battery_soc_pct": self.battery_soc_pct,
            "diesel_fuel_remaining_liters": self.diesel_fuel_remaining_liters,
        }
        if self.battery_energy_wh is not None:
            d["battery_energy_wh"] = self.battery_energy_wh
        if self.terminal_target_wh_override is not None:
            d["terminal_target_wh_override"] = self.terminal_target_wh_override
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["timestamp"],
            data["battery_soc_pct"],
            data.get("diesel_fuel_remaining_liters", 0.0),
            battery_energy_wh=data.get("battery_energy_wh", _STATE_UNSET),
            terminal_target_wh_override=data.get("terminal_target_wh_override"),
        )


class _FakeTimeseries:
    def __init__(self, point, lower=None, upper=None):
        self.point = point
        self.lower = lower or point
        self.upper = upper or point


class _FakeForecastBundle:
    """Mirrors the REAL ForecastBundle's solar_irradiance/demand/metadata shape only."""

    def __init__(self):
        self.solar_irradiance = _FakeTimeseries([100.0] * 24, [80.0] * 24, [120.0] * 24)
        self.demand = _FakeTimeseries([5000.0] * 24)
        self.metadata = {"ebr_target_wh": [15000.0] * 24}


class _FakeN6Engine:
    """Mirrors the REAL N6SolarForecastEngine.predict(state, context) -> bundle shape only."""

    def __init__(self):
        self.predict_call_count = 0

    def predict(self, station_state, context):
        self.predict_call_count += 1
        assert "n6_feature_matrix" in context
        return _FakeForecastBundle()


class _FakeRouter:
    """Mirrors the REAL EMSControlRouter.evaluate_and_route(state, bundle, configs) -> (assessment, route)."""

    def __init__(self, route="NORMAL"):
        self._route = route
        self.call_count = 0

    def evaluate_and_route(self, station_state, bundle, configs):
        self.call_count += 1
        return ({"ok": True}, self._route)


class _FakeDispatchPlan:
    """Mirrors the REAL DispatchPlan's 24-length-list field shape only."""

    def __init__(self, schema_version, timestamps, solar_used, wind_used, battery_charge, battery_discharge,
                 battery_soc, diesel_power, load_served, flexible_load_schedule, renewable_curtailment,
                 unmet_load, objective_value, constraint_status, energy_balance_errors, unmet_essential=None):
        for name, arr in (("timestamps", timestamps), ("solar_used", solar_used), ("unmet_load", unmet_load)):
            assert len(arr) == 24, f"{name} must have 24 entries"
        self.schema_version = schema_version
        self.timestamps = timestamps
        self.solar_used = solar_used
        self.wind_used = wind_used
        self.battery_charge = battery_charge
        self.battery_discharge = battery_discharge
        self.battery_soc = battery_soc
        self.diesel_power = diesel_power
        self.load_served = load_served
        self.flexible_load_schedule = flexible_load_schedule
        self.renewable_curtailment = renewable_curtailment
        self.unmet_load = unmet_load
        self.objective_value = objective_value
        self.constraint_status = constraint_status
        self.energy_balance_errors = energy_balance_errors
        self.unmet_essential = unmet_essential


class _FakeGAP19Optimizer:
    """Mirrors the REAL GAP19HighsNativeOptimizer.optimize(bundle, state, configs) -> plan shape only."""

    def __init__(self):
        self.call_count = 0
        self.last_configs = None
        self.last_bundle = None
        self.seen_configs = []

    def optimize(self, bundle, station_state, configs):
        self.call_count += 1
        self.last_bundle = bundle
        self.last_configs = configs
        self.seen_configs.append(configs)
        return _FakeDispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"T{i}" for i in range(24)],
            solar_used=[10.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[5.0] * 24,
            battery_soc=[150000.0] * 24,
            diesel_power=[200.0] * 24,
            load_served=[5000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=1.23,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )


class _FakeDigitalTwinSimulator:
    """Mirrors the REAL DigitalTwinSimulator.step(state, one_hour_slice, actual) -> next_state shape only."""

    def __init__(self, fuel_burn_per_hour=0.5):
        self._fuel_burn_per_hour = fuel_burn_per_hour
        self.call_count = 0

    def step(self, station_state, one_hour_slice, actual_t):
        self.call_count += 1
        return _FakeStationState(
            timestamp=one_hour_slice.timestamps[0],
            battery_soc_pct=station_state.battery_soc_pct - 1.0,
            diesel_fuel_remaining_liters=station_state.diesel_fuel_remaining_liters - self._fuel_burn_per_hour,
        )


def _fake_evaluate_dispatch_safety(plan_dict, min_e_wh, reserve_shortfall_authorization_wh):
    """Mirrors the REAL reserve_policy_guard.evaluate_dispatch_safety(...) shape only."""
    return {
        "passed": True,
        "reserve_shortfall_authorization_wh_seen": reserve_shortfall_authorization_wh,
        "min_e_wh_seen": min_e_wh,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIntegrationAssumptionsRegistry(unittest.TestCase):
    def test_01_four_assumptions_documented_with_all_required_fields(self):
        self.assertEqual(len(INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW), 4)
        for ia in INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW:
            self.assertTrue(ia.id)
            self.assertTrue(ia.assumption)
            self.assertTrue(ia.why_unresolved)
            self.assertTrue(ia.required_before_real_use)

    def test_02_ia_ids_are_unique(self):
        ids = [ia.id for ia in INTEGRATION_ASSUMPTIONS_REQUIRING_REVIEW]
        self.assertEqual(len(ids), len(set(ids)))


class TestStationStateCodec(unittest.TestCase):
    def test_03_round_trips_through_plain_dict(self):
        real = _FakeStationState("2024-01-01T00:00:00Z", 80.0, 500.0)
        as_dict = StationStateCodec.to_plain_dict(real)
        self.assertEqual(as_dict["battery_soc_pct"], 80.0)
        back = StationStateCodec.from_plain_dict(as_dict, _FakeStationState)
        self.assertEqual(back.battery_soc_pct, 80.0)
        self.assertEqual(back.diesel_fuel_remaining_liters, 500.0)


class TestForecastBundleStepView(unittest.TestCase):
    def test_04_extracts_correct_per_step_values(self):
        bundle = _FakeForecastBundle()
        view = ForecastBundleStepView.step_view(bundle, 5)
        self.assertEqual(view["solar_irradiance_point"], 100.0)
        self.assertEqual(view["demand_point"], 5000.0)
        self.assertEqual(view["ebr_target_wh"], [15000.0] * 24)
        self.assertEqual(view["step_index"], 5)


class TestDispatchOutcomeView(unittest.TestCase):
    def test_05_extracts_scalar_fields_at_given_hour_no_critical_split(self):
        plan = _FakeGAP19Optimizer().optimize(None, None, None)
        outcome = DispatchOutcomeView.at_hour(plan, 3, fuel_consumed_liters_this_hour=0.5)
        self.assertEqual(outcome["diesel_consumed_liters"], 0.5)
        self.assertIsNone(outcome["critical_unmet_load_wh"])  # no unmet_essential on this fake plan
        self.assertEqual(outcome["total_unmet_load_wh"], 0.0)
        self.assertEqual(outcome["constraint_status"], "OPTIMAL")

    def test_06_extracts_critical_unmet_when_present(self):
        plan = _FakeGAP19Optimizer().optimize(None, None, None)
        plan.unmet_essential = [1.0] * 24
        outcome = DispatchOutcomeView.at_hour(plan, 0, fuel_consumed_liters_this_hour=None)
        self.assertEqual(outcome["critical_unmet_load_wh"], 1.0)
        self.assertIsNone(outcome["diesel_consumed_liters"])  # never coerced to 0.0


class TestN6ForecastProviderAdapter(unittest.TestCase):
    def test_07_calls_real_engine_exactly_once_per_origin_not_per_step(self):
        engine = _FakeN6Engine()
        adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={"origin-1": {"fake": "matrix"}},
        )
        state_dict = StationStateCodec.to_plain_dict(_FakeStationState("t0", 80.0, 500.0))
        context = {"state": state_dict}
        for step in range(5):
            view = adapter.predict("origin-1", step, context)
            self.assertEqual(view["origin"], "origin-1")
            self.assertEqual(view["step_index"], step)
        self.assertEqual(engine.predict_call_count, 1, "real engine must be called once per origin, not per step")

    def test_08_fails_closed_on_missing_feature_matrix(self):
        adapter = N6ForecastProviderAdapter(_FakeN6Engine(), _FakeStationState, feature_matrix_by_origin={})
        with self.assertRaises(ValueError):
            adapter.predict("unknown-origin", 0, {"state": {"timestamp": "t0", "battery_soc_pct": 1.0}})


class TestRoutedOptimizerAdapter(unittest.TestCase):
    def _forecast_for(self, origin, bundle):
        return {"origin": origin, "_real_bundle_ref": bundle, "step_index": 0}

    def test_09_folds_router_decision_into_returned_dict(self):
        router = _FakeRouter(route="NORMAL")
        optimizer = _FakeGAP19Optimizer()
        adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={"origin-1": {"some": "config"}})
        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        forecast = self._forecast_for("origin-1", _FakeForecastBundle())
        result = adapter.optimize(state, forecast, controller_settings=None)
        self.assertEqual(result["route"], "NORMAL")
        self.assertIn("_real_plan_ref", result)

    def test_10_optimizes_exactly_once_per_origin_caching_across_calls(self):
        router = _FakeRouter()
        optimizer = _FakeGAP19Optimizer()
        adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={"origin-1": {}})
        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        forecast = self._forecast_for("origin-1", _FakeForecastBundle())
        for _ in range(24):
            adapter.optimize(state, forecast, controller_settings=None)
        self.assertEqual(optimizer.call_count, 1, "optimizer must be called once per origin (single-shot plan)")
        self.assertEqual(router.call_count, 1)

    def test_11_fails_closed_without_real_bundle_ref(self):
        adapter = RoutedOptimizerAdapter(_FakeRouter(), _FakeGAP19Optimizer(), configs_by_origin={"origin-1": {}})
        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        with self.assertRaises(ValueError):
            adapter.optimize(state, {"origin": "origin-1"}, controller_settings=None)

    def test_12_fails_closed_on_missing_config_for_origin(self):
        adapter = RoutedOptimizerAdapter(_FakeRouter(), _FakeGAP19Optimizer(), configs_by_origin={})
        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        with self.assertRaises(ValueError):
            adapter.optimize(state, self._forecast_for("origin-1", _FakeForecastBundle()), controller_settings=None)


class TestSingleShotPlanSlicingSimulatorAdapter(unittest.TestCase):
    def _build_dispatch_dict(self, origin, plan):
        return {"origin": origin, "_real_plan_ref": plan}

    def test_13_steps_through_real_simulator_and_tracks_fuel_delta(self):
        simulator = _FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5)
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={"origin-1": [{"actual_SW_IN": 90.0}] * 24},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        state_dict["_step_index"] = 0
        plan = _FakeGAP19Optimizer().optimize(None, None, None)
        dispatch_dict = self._build_dispatch_dict("origin-1", plan)

        result = adapter.step(state_dict, dispatch_dict)
        self.assertFalse(result["stop_early"])
        self.assertEqual(result["dispatch_outcome"]["diesel_consumed_liters"], 0.5)
        self.assertEqual(result["state"]["_step_index"], 1)
        self.assertEqual(simulator.call_count, 1)

    def test_14_fails_closed_on_missing_ground_truth_actual(self):
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={},  # no actuals supplied at all
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        state_dict["_step_index"] = 0
        plan = _FakeGAP19Optimizer().optimize(None, None, None)
        with self.assertRaises(ValueError):
            adapter.step(state_dict, self._build_dispatch_dict("origin-1", plan))

    def test_15_fails_closed_without_step_index(self):
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={"origin-1": [{"actual_SW_IN": 1.0}]},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        plan = _FakeGAP19Optimizer().optimize(None, None, None)
        with self.assertRaises(ValueError):
            adapter.step(state_dict, self._build_dispatch_dict("origin-1", plan))

    def test_15b_physical_fuel_accumulation_24h_single_shot(self):
        """
        Regression test: In single-shot mode, generator ON for hours 0-3 at 10,000 W,
        then OFF for hours 4-23. Under the physical fuel formula
        (5.0 * (P>0) + 0.00025 * P) * 1.0 h:
          Hours 0-3: (5.0 + 0.00025 * 10000.0) * 1.0 = 7.5 L/hr * 4 hr = 30.0 L.
          Hours 4-23: 0.0 L/hr * 20 hr = 0.0 L.
        Expected 24-hour total is 30.0 L, even though the final step (hour 23) consumes 0.0 L.
        Verifies that earlier realized steps are NOT overwritten by the final step.
        """
        class _PhysicalFuelSimulator:
            def __init__(self, base_fuel_lph=5.0, marginal_fuel_lpwh=0.00025, missing_step_indices=None):
                self.base_fuel_lph = base_fuel_lph
                self.marginal_fuel_lpwh = marginal_fuel_lpwh
                self.missing_step_indices = set(missing_step_indices or [])
                self.call_count = 0

            def step(self, station_state, one_hour_slice, actual_t):
                step_idx = self.call_count
                self.call_count += 1
                if step_idx in self.missing_step_indices or station_state.diesel_fuel_remaining_liters is None:
                    return _FakeStationState(
                        timestamp=one_hour_slice.timestamps[0],
                        battery_soc_pct=station_state.battery_soc_pct,
                        diesel_fuel_remaining_liters=None,
                    )
                p_diesel = one_hour_slice.diesel_power[0]
                diesel_running = p_diesel > 0
                required_fuel = (
                    (self.base_fuel_lph if diesel_running else 0.0)
                    + (self.marginal_fuel_lpwh * p_diesel)
                ) * 1.0
                next_fuel = max(0.0, station_state.diesel_fuel_remaining_liters - required_fuel)
                return _FakeStationState(
                    timestamp=one_hour_slice.timestamps[0],
                    battery_soc_pct=station_state.battery_soc_pct,
                    diesel_fuel_remaining_liters=round(next_fuel, 4),
                )

        simulator = _PhysicalFuelSimulator()
        actuals = [{"actual_SW_IN": 0.0}] * 24
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={"origin-1": actuals},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        state_dict["_step_index"] = 0

        # Plan with generator ON for hours 0-3 (10,000 W) and OFF for hours 4-23 (0 W)
        diesel_power_profile = [10000.0, 10000.0, 10000.0, 10000.0] + [0.0] * 20
        plan = _FakeDispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"T{i}" for i in range(24)],
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24,
            battery_soc=[160000.0] * 24,
            diesel_power=diesel_power_profile,
            load_served=[10000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )
        dispatch_dict = self._build_dispatch_dict("origin-1", plan)

        # Step through all 24 hours of the dispatch plan
        last_step_result = None
        for step in range(24):
            step_result = adapter.step(state_dict, dispatch_dict)
            state_dict = step_result["state"]
            last_step_result = step_result
            if step < 4:
                expected_cumulative = 7.5 * (step + 1)
                self.assertEqual(step_result["dispatch_outcome"]["diesel_consumed_liters"], expected_cumulative)
            else:
                self.assertEqual(step_result["dispatch_outcome"]["diesel_consumed_liters"], 30.0)

        self.assertEqual(simulator.call_count, 24)
        self.assertIsNotNone(last_step_result)
        # Final step (hour 23) consumed 0.0 L physically
        final_real_state = last_step_result["state"]["_real_station_state_ref"]
        self.assertEqual(final_real_state.diesel_fuel_remaining_liters, 470.0)
        # Outcome reported across all realized steps MUST be 30.0 L, not 0.0 L
        self.assertEqual(last_step_result["dispatch_outcome"]["diesel_consumed_liters"], 30.0)
        self.assertEqual(last_step_result["state"]["_cumulative_diesel_consumed_liters"], 30.0)

    def test_15c_physical_fuel_accumulation_missing_intermediate_step_reports_none(self):
        """
        Fail-closed regression test: If one intermediate step lacks a valid fuel reading,
        the cumulative total becomes None and does NOT resume numeric totals even if subsequent
        readings are available or zero. Ensures missing data cannot be mistaken for zero consumption.
        """
        class _PhysicalFuelSimulator:
            def __init__(self, base_fuel_lph=5.0, marginal_fuel_lpwh=0.00025, missing_step_indices=None):
                self.base_fuel_lph = base_fuel_lph
                self.marginal_fuel_lpwh = marginal_fuel_lpwh
                self.missing_step_indices = set(missing_step_indices or [])
                self.call_count = 0

            def step(self, station_state, one_hour_slice, actual_t):
                step_idx = self.call_count
                self.call_count += 1
                if step_idx in self.missing_step_indices or station_state.diesel_fuel_remaining_liters is None:
                    return _FakeStationState(
                        timestamp=one_hour_slice.timestamps[0],
                        battery_soc_pct=station_state.battery_soc_pct,
                        diesel_fuel_remaining_liters=None,
                    )
                p_diesel = one_hour_slice.diesel_power[0]
                diesel_running = p_diesel > 0
                required_fuel = (
                    (self.base_fuel_lph if diesel_running else 0.0)
                    + (self.marginal_fuel_lpwh * p_diesel)
                ) * 1.0
                next_fuel = max(0.0, station_state.diesel_fuel_remaining_liters - required_fuel)
                return _FakeStationState(
                    timestamp=one_hour_slice.timestamps[0],
                    battery_soc_pct=station_state.battery_soc_pct,
                    diesel_fuel_remaining_liters=round(next_fuel, 4),
                )

        # Missing fuel observation at step 2 (intermediate step)
        simulator = _PhysicalFuelSimulator(missing_step_indices={2})
        actuals = [{"actual_SW_IN": 0.0}] * 24
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={"origin-1": actuals},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        state_dict["_step_index"] = 0

        diesel_power_profile = [10000.0, 10000.0, 10000.0, 10000.0] + [0.0] * 20
        plan = _FakeDispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"T{i}" for i in range(24)],
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24,
            battery_soc=[160000.0] * 24,
            diesel_power=diesel_power_profile,
            load_served=[10000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )
        dispatch_dict = self._build_dispatch_dict("origin-1", plan)

        last_step_result = None
        for step in range(24):
            step_result = adapter.step(state_dict, dispatch_dict)
            state_dict = step_result["state"]
            last_step_result = step_result
            if step < 2:
                # Valid steps before the gap
                self.assertIsNotNone(step_result["dispatch_outcome"]["diesel_consumed_liters"])
            else:
                # Gap occurred at step 2; all subsequent outcomes MUST report None
                self.assertIsNone(
                    step_result["dispatch_outcome"]["diesel_consumed_liters"],
                    f"Step {step} must report None once a fuel gap has occurred"
                )

        # Steps 0, 1, 2 called simulator (step 2 returned fuel=None).
        # Steps 3..23 were rejected pre-call, so simulator was NEVER called on steps 3..23.
        self.assertEqual(simulator.call_count, 3)
        self.assertTrue(last_step_result["stop_early"])
        self.assertTrue(last_step_result["state"]["_has_fuel_failure"])
        self.assertIsNone(last_step_result["dispatch_outcome"]["diesel_consumed_liters"])
        self.assertIsNone(last_step_result["state"]["_cumulative_diesel_consumed_liters"])

    def test_15d_physical_fuel_accumulation_missing_first_step_reports_none(self):
        """
        Fail-closed regression test: If fuel observation is missing at step 0 (e.g. uninitialized initial state),
        the pre-call check rejects and simulator.step() is NEVER called. The cumulative total is None.
        """
        class _PhysicalFuelSimulator:
            def __init__(self, base_fuel_lph=5.0, marginal_fuel_lpwh=0.00025):
                self.base_fuel_lph = base_fuel_lph
                self.marginal_fuel_lpwh = marginal_fuel_lpwh
                self.call_count = 0

            def step(self, station_state, one_hour_slice, actual_t):
                self.call_count += 1
                return _FakeStationState(
                    timestamp=one_hour_slice.timestamps[0],
                    battery_soc_pct=station_state.battery_soc_pct,
                    diesel_fuel_remaining_liters=None,
                )

        simulator = _PhysicalFuelSimulator()
        actuals = [{"actual_SW_IN": 0.0}] * 24
        adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={"origin-1": actuals},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        real_state = _FakeStationState("t0", 80.0, None)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state
        state_dict["_step_index"] = 0

        diesel_power_profile = [10000.0] * 4 + [0.0] * 20
        plan = _FakeDispatchPlan(
            schema_version="1.0.0",
            timestamps=[f"T{i}" for i in range(24)],
            solar_used=[0.0] * 24,
            wind_used=[0.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24,
            battery_soc=[160000.0] * 24,
            diesel_power=diesel_power_profile,
            load_served=[10000.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            unmet_load=[0.0] * 24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0] * 24,
        )
        dispatch_dict = self._build_dispatch_dict("origin-1", plan)

        last_step_result = None
        for step in range(24):
            step_result = adapter.step(state_dict, dispatch_dict)
            state_dict = step_result["state"]
            last_step_result = step_result
            self.assertIsNone(
                step_result["dispatch_outcome"]["diesel_consumed_liters"],
                f"Step {step} must report None when step 0 fuel was missing"
            )

        # Pre-call fuel check rejects immediately; simulator.step() is NEVER called.
        self.assertEqual(simulator.call_count, 0)
        self.assertTrue(last_step_result["stop_early"])
        self.assertTrue(last_step_result["state"]["_has_fuel_failure"])
        self.assertIsNone(last_step_result["dispatch_outcome"]["diesel_consumed_liters"])
        self.assertIsNone(last_step_result["state"]["_cumulative_diesel_consumed_liters"])


class TestReservePolicyGuardSafetyEvaluatorAdapter(unittest.TestCase):
    def test_16_calls_real_function_with_none_authorization_by_default(self):
        adapter = ReservePolicyGuardSafetyEvaluatorAdapter(_fake_evaluate_dispatch_safety)
        result = adapter.evaluate_dispatch_safety({"_real_plan_dict": {"unmet_load": [0.0] * 24}})
        self.assertTrue(result["passed"])
        self.assertIsNone(result["reserve_shortfall_authorization_wh_seen"], "SAF-03 remains unset by default (IA-4)")

    def test_17_returns_none_unknown_when_no_real_plan_dict_supplied(self):
        adapter = ReservePolicyGuardSafetyEvaluatorAdapter(_fake_evaluate_dispatch_safety)
        result = adapter.evaluate_dispatch_safety({})
        self.assertIsNone(result, "missing safety evidence must be None (unknown), never fabricated")

    def test_18_passes_through_an_explicit_non_none_authorization_if_caller_supplies_one(self):
        adapter = ReservePolicyGuardSafetyEvaluatorAdapter(
            _fake_evaluate_dispatch_safety, min_e_wh=1000.0, reserve_shortfall_authorization_wh=5000.0
        )
        result = adapter.evaluate_dispatch_safety({"_real_plan_dict": {"unmet_load": [0.0] * 24}})
        self.assertEqual(result["reserve_shortfall_authorization_wh_seen"], 5000.0)
        self.assertEqual(result["min_e_wh_seen"], 1000.0)


class TestNoProductionImportAndNoCampaignWiring(unittest.TestCase):
    """Static regression proof, mirroring test_n6_multi_origin_harness.py's test_35/test_36 convention."""

    def test_19_adapters_module_imports_no_real_production_class_at_runtime(self):
        import inspect
        import system.evaluation.n6_multi_origin_harness.adapters as adapters_module

        source = inspect.getsource(adapters_module)
        # Split off the `if TYPE_CHECKING:` block (never executed) before checking for
        # production-module import lines -- those lines are type-hint-only by design.
        before_type_checking = source.split("if TYPE_CHECKING:")[0]
        forbidden_substrings = [
            "from system.control.router import",
            "from system.forecasting.implementations.n6_solar import",
            "from system.optimization.implementations.gap19_highs_native import",
            "from system.simulation.simulator import",
            "from system.safety import reserve_policy_guard",
        ]
        for forbidden in forbidden_substrings:
            self.assertNotIn(
                forbidden,
                before_type_checking,
                f"adapters.py must not import a real production module outside TYPE_CHECKING: {forbidden!r}",
            )

    def test_20_adapters_not_referenced_by_harness_or_campaign_execution(self):
        import inspect
        import system.evaluation.n6_multi_origin_harness.harness as harness_module

        source = inspect.getsource(harness_module)
        self.assertNotIn("adapters", source, "harness.py must not import or reference adapters.py")


class TestOD01TerminalTargetDerivation(unittest.TestCase):
    """
    Validates OD-01 dynamic terminal target derivation helper and its integration
    with RoutedOptimizerAdapter per POLARIS Master Decision Register v1.9.12 Section 38.
    """

    def test_21_dynamic_calculation_with_standard_defaults(self):
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=100000.0)
        configs = {}
        # Defaults: capacity=200,000 Wh, min_soc=20% (40,000 Wh), max_soc=95% (190,000 Wh)
        # initial_e_wh = 100,000 Wh
        # terminal_target_wh = 100,000 - 40,000 = 60,000 Wh
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertEqual(res["terminal_target_wh"], 60000.0)
        self.assertNotIn("terminal_target_wh", configs, "caller configs must not be mutated")

    def test_22_boundary_clamping_below_min_soc(self):
        # 10% SOC -> 20,000 Wh, below min_e_wh of 40,000 Wh
        state = _FakeStationState("t0", 10.0, 500.0, battery_energy_wh=20000.0)
        res = _prepare_gap19_terminal_target_config(state, {})
        # Clamped initial_e_wh = 40,000 -> terminal_target_wh = 40,000 - 40,000 = 0.0
        self.assertEqual(res["terminal_target_wh"], 0.0)

    def test_23_boundary_clamping_above_max_soc(self):
        # 98% SOC -> 196,000 Wh, above max_soc 95% = 190,000 Wh
        state = _FakeStationState("t0", 98.0, 500.0, battery_energy_wh=196000.0)
        res = _prepare_gap19_terminal_target_config(state, {})
        # Clamped initial_e_wh = 190,000 -> terminal_target_wh = 190,000 - 40,000 = 150,000.0
        self.assertEqual(res["terminal_target_wh"], 150000.0)

    def test_24_custom_battery_configuration(self):
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=50000.0)
        configs = {
            "battery": {
                "capacity_wh": 100000.0,
                "min_soc_pct": 10.0,
                "max_soc_pct": 90.0,
            }
        }
        # min_e = 10,000, max_e = 90,000, initial_e = 50,000 -> target = 40,000
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertEqual(res["terminal_target_wh"], 40000.0)
        self.assertNotIn("terminal_target_wh", configs)

    def test_25_state_override_takes_precedence(self):
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=100000.0, terminal_target_wh_override=12345.0)
        configs = {}
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertNotIn("terminal_target_wh", res, "helper must not inject target when state override is active")

    def test_26_explicit_config_target_takes_precedence(self):
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=100000.0)
        configs = {"terminal_target_wh": 54321.0}
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertEqual(res["terminal_target_wh"], 54321.0, "explicit config value must not be overridden")

    def test_27_both_overrides_present(self):
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=100000.0, terminal_target_wh_override=11111.0)
        configs = {"terminal_target_wh": 22222.0}
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertEqual(res["terminal_target_wh"], 22222.0)

    def test_28_immutability_guaranteed_for_routed_optimizer_adapter(self):
        origin = "origin-immutability"
        router = _FakeRouter()
        optimizer = _FakeGAP19Optimizer()
        origin_cfg = {"battery": {"capacity_wh": 200000.0}}
        adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={origin: origin_cfg})

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        forecast = {"origin": origin, "_real_bundle_ref": _FakeForecastBundle()}

        adapter.optimize(state, forecast, controller_settings=None)

        self.assertNotIn("terminal_target_wh", origin_cfg, "origin configuration dictionary must remain immutable")
        self.assertIsNotNone(optimizer.last_configs)
        self.assertEqual(optimizer.last_configs["terminal_target_wh"], 120000.0)

    def test_29_fail_closed_on_invalid_inputs(self):
        valid_state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=100000.0)

        # configs not a dict
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, "not_a_dict")  # type: ignore

        # station_state is None
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(None, {})

        # battery_energy_wh is None
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(_FakeStationState("t0", 50.0, battery_energy_wh=None), {})

        # battery_energy_wh is NaN
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(_FakeStationState("t0", 50.0, battery_energy_wh=float("nan")), {})

        # battery_energy_wh is inf
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(_FakeStationState("t0", 50.0, battery_energy_wh=float("inf")), {})

        # battery_energy_wh is non-numeric
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(_FakeStationState("t0", 50.0, battery_energy_wh="invalid"), {})

        # battery_energy_wh is bool
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(_FakeStationState("t0", 50.0, battery_energy_wh=True), {})

        # configs['battery'] not a dict
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": "invalid"})

        # capacity_wh <= 0 or invalid
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"capacity_wh": 0.0}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"capacity_wh": -50.0}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"capacity_wh": float("nan")}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"capacity_wh": True}})

        # SOC bounds invalid
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"min_soc_pct": -5.0}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"min_soc_pct": 98.0, "max_soc_pct": 95.0}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"max_soc_pct": 105.0}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"min_soc_pct": float("nan")}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"max_soc_pct": float("nan")}})
        with self.assertRaises(ValueError):
            _prepare_gap19_terminal_target_config(valid_state, {"battery": {"min_soc_pct": True}})

    def test_30_explicit_state_override_bypasses_invalid_dynamic_inputs(self):
        # State override present, but battery_energy_wh is None and battery config has invalid parameters
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=None, terminal_target_wh_override=12345.0)
        configs = {"battery": {"capacity_wh": -999.0, "min_soc_pct": -50.0}}
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertNotIn("terminal_target_wh", res, "explicit state override must bypass dynamic derivation without error")
        self.assertNotIn("terminal_target_wh", configs, "caller configs must not be mutated")

    def test_31_explicit_config_target_bypasses_invalid_dynamic_inputs(self):
        # Explicit config target present, but battery_energy_wh is None and battery config is malformed
        state = _FakeStationState("t0", 50.0, 500.0, battery_energy_wh=None)
        configs = {"terminal_target_wh": 54321.0, "battery": "not_a_dictionary"}
        res = _prepare_gap19_terminal_target_config(state, configs)
        self.assertEqual(res["terminal_target_wh"], 54321.0, "explicit config value must be preserved without error")
        self.assertEqual(configs["terminal_target_wh"], 54321.0)

    def test_32_explicit_config_target_usable_when_state_is_none(self):
        # Config has explicit target; station_state is None
        configs = {"terminal_target_wh": 50000.0}
        res = _prepare_gap19_terminal_target_config(None, configs)
        self.assertEqual(res["terminal_target_wh"], 50000.0)

    def test_33_real_gap19_optimizer_entry_receives_prepared_terminal_target_config(self):
        import unittest.mock
        from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

        real_opt = GAP19HighsNativeOptimizer()
        self.assertIsInstance(real_opt, GAP19HighsNativeOptimizer)

        captured_calls = []

        def spy_optimize(bundle, station_state, config):
            captured_calls.append({
                "bundle": bundle,
                "station_state": station_state,
                "config": config,
            })
            return _FakeDispatchPlan(
                schema_version="1.0.0",
                timestamps=[f"T{i}" for i in range(24)],
                solar_used=[10.0] * 24,
                wind_used=[0.0] * 24,
                battery_charge=[0.0] * 24,
                battery_discharge=[5.0] * 24,
                battery_soc=[150000.0] * 24,
                diesel_power=[200.0] * 24,
                load_served=[5000.0] * 24,
                flexible_load_schedule=[0.0] * 24,
                renewable_curtailment=[0.0] * 24,
                unmet_load=[0.0] * 24,
                objective_value=1.23,
                constraint_status="OPTIMAL",
                energy_balance_errors=[0.0] * 24,
            )

        with unittest.mock.patch.object(real_opt, "optimize", side_effect=spy_optimize):
            origin = "origin-real-gap19-routed"
            origin_cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
            adapter = RoutedOptimizerAdapter(
                real_router=_FakeRouter(),
                real_optimizer=real_opt,
                configs_by_origin={origin: origin_cfg},
            )

            real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)
            state_dict = {"_real_station_state_ref": real_state}
            forecast_dict = {"origin": origin, "_real_bundle_ref": _FakeForecastBundle()}

            result = adapter.optimize(state_dict, forecast_dict, controller_settings=None)

            # Assert real optimizer entry was invoked
            self.assertEqual(len(captured_calls), 1)
            call_record = captured_calls[0]
            passed_config = call_record["config"]

            # Verify that the REAL GAP19 optimizer entry receives the prepared terminal target
            self.assertEqual(passed_config["terminal_target_wh"], 120000.0)
            # Verify origin_cfg remained strictly immutable
            self.assertNotIn("terminal_target_wh", origin_cfg)
            self.assertIs(call_record["station_state"], real_state)
            self.assertEqual(result["route"], "NORMAL")

    def test_34_real_gap19_optimizer_entry_in_receding_horizon_adapter(self):
        import unittest.mock
        from system.evaluation.n6_multi_origin_harness.adapters import N6RecedingHorizonOptimizerAdapter
        from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

        real_opt = GAP19HighsNativeOptimizer()
        self.assertIsInstance(real_opt, GAP19HighsNativeOptimizer)

        captured_calls = []

        def spy_optimize(bundle, station_state, config):
            captured_calls.append({
                "bundle": bundle,
                "station_state": station_state,
                "config": config,
            })
            return _FakeDispatchPlan(
                schema_version="1.0.0",
                timestamps=[f"T{i}" for i in range(24)],
                solar_used=[10.0] * 24,
                wind_used=[0.0] * 24,
                battery_charge=[0.0] * 24,
                battery_discharge=[5.0] * 24,
                battery_soc=[150000.0] * 24,
                diesel_power=[200.0] * 24,
                load_served=[5000.0] * 24,
                flexible_load_schedule=[0.0] * 24,
                renewable_curtailment=[0.0] * 24,
                unmet_load=[0.0] * 24,
                objective_value=1.23,
                constraint_status="OPTIMAL",
                energy_balance_errors=[0.0] * 24,
            )

        with unittest.mock.patch.object(real_opt, "optimize", side_effect=spy_optimize):
            origin = "origin-real-gap19-rh"
            origin_cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
            rh_adapter = N6RecedingHorizonOptimizerAdapter(
                real_gap19_optimizer=real_opt,
                real_option_d_solver=unittest.mock.MagicMock(),
                configs_by_origin={origin: origin_cfg},
            )

            real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)
            forecast = {
                "origin": origin,
                "route": "NORMAL",
                "_real_bundle_ref": _FakeForecastBundle(),
                "_real_station_state_ref": real_state,
            }
            rh_adapter.optimize(state={}, forecast=forecast, controller_settings=None)

            self.assertEqual(len(captured_calls), 1)
            self.assertEqual(captured_calls[0]["config"]["terminal_target_wh"], 120000.0)
            self.assertNotIn("terminal_target_wh", origin_cfg)

    def test_35_real_gap19_native_ingestion_accepts_prepared_config(self):
        import unittest.mock
        from datetime import datetime, timedelta
        from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
        from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
        from system.schemas.station_state import StationState

        origin = "2024-01-01T00:00:00Z"
        origin_dt = datetime.fromisoformat(origin.replace("Z", "+00:00"))
        ts = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin,
            horizon_hours=24,
            timestamps=ts,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            wind_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            demand=TimeseriesForecast([5000.0]*24, [5000.0]*24, [5000.0]*24, "W"),
            demand_critical=TimeseriesForecast([1000.0]*24, [1000.0]*24, [1000.0]*24, "W"),
            metadata={"model_id": "test_real_gap19"},
        )
        real_state = StationState(
            timestamp=origin,
            battery_soc_pct=80.0,
            battery_energy_wh=160000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=5000.0,
            last_observed_wind_generation=0.0,
        )

        real_opt = GAP19HighsNativeOptimizer()

        # 1. Unprepared config raises MISSING_GOVERNED_INPUT at real GAP19 entry
        raw_config = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
        with self.assertRaises(ValueError) as ctx:
            real_opt.optimize(bundle, real_state, raw_config)
        self.assertIn("MISSING_GOVERNED_INPUT: Terminal reserve target", str(ctx.exception))

        # 2. Config prepared via _prepare_gap19_terminal_target_config injects terminal_target_wh
        prepared_config = _prepare_gap19_terminal_target_config(real_state, raw_config)
        self.assertEqual(prepared_config["terminal_target_wh"], 120000.0)

        # 3. Real GAP19 accepts prepared config and successfully ingests terminal target past the error
        # Spy on the HiGHS solver execution to verify ingestion without running full branch-and-bound
        with unittest.mock.patch("highspy.Highs") as mock_highs:
            instance = unittest.mock.MagicMock()
            mock_highs.return_value = instance
            instance.getModelStatus.return_value = 7  # kOptimal
            instance.getSolution.return_value = unittest.mock.MagicMock(col_value=[0.0]*360)
            instance.getInfo.return_value = unittest.mock.MagicMock(objective_function_value=1.0)

            plan = real_opt.optimize(bundle, real_state, prepared_config)
            self.assertIsNotNone(plan)


class TestPolicyBReserveIntegration(unittest.TestCase):
    """
    Validates Policy B reserve preparation and integration with RoutedOptimizerAdapter
    per POLARIS Master Decision Register Section 4 item 7 and Gemini review conditions:
      combined_reserve_wh[t] = max(existing_GAP19_critical_reserve_wh[t], conformal_ebr_wh[t])
    """

    def _build_test_bundle(
        self,
        demand_pt=None,
        critical_demand_pt=None,
        conformal_ebr=None,
        metadata_source="CANDIDATE_N6_25ADD_15KT_SPECIALIST",
    ):
        demand_vals = demand_pt or [5000.0] * 24
        crit_vals = critical_demand_pt
        ebr_vals = conformal_ebr if conformal_ebr is not None else [15000.0] * 24
        meta = {}
        if metadata_source:
            meta["SOLAR_FORECAST_SOURCE"] = metadata_source
        if ebr_vals is not None:
            meta["ebr_target_wh"] = ebr_vals

        class _Bundle:
            def __init__(self):
                self.demand = _FakeTimeseries(demand_vals)
                self.demand_critical = _FakeTimeseries(crit_vals) if crit_vals is not None else None
                self.solar_irradiance = _FakeTimeseries([100.0] * 24)
                self.metadata = meta

        return _Bundle()

    def test_33_pointwise_max_below_equal_above(self):
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[0.0] * 24)
        configs = {"battery": {"discharge_efficiency": 0.92}, "optimizer": {"timestep_hours": 1.0}}

        crit_reserve = _compute_gap19_six_hour_critical_reserve([1000.0] * 24, configs)
        self.assertAlmostEqual(crit_reserve[0], 6000.0 / 0.92, places=6)

        # 1. Conformal below critical (conformal = 2000 Wh) -> output must equal critical reserve
        bundle.metadata["ebr_target_wh"] = [2000.0] * 24
        res_below = _prepare_gap19_policy_b_config(bundle, configs)
        self.assertAlmostEqual(res_below["ebr_target_wh"][0], crit_reserve[0], places=6)

        # 2. Conformal equal to critical -> output equals critical reserve
        bundle.metadata["ebr_target_wh"] = list(crit_reserve)
        res_equal = _prepare_gap19_policy_b_config(bundle, configs)
        self.assertAlmostEqual(res_equal["ebr_target_wh"][0], crit_reserve[0], places=6)

        # 3. Conformal above critical (conformal = 25000 Wh) -> output must equal conformal EBR
        bundle.metadata["ebr_target_wh"] = [25000.0] * 24
        res_above = _prepare_gap19_policy_b_config(bundle, configs)
        self.assertEqual(res_above["ebr_target_wh"][0], 25000.0)

    def test_34_critical_demand_precedence(self):
        # Tier 1: bundle.demand_critical overrides configs
        bundle = self._build_test_bundle(
            demand_pt=[10000.0] * 24,
            critical_demand_pt=[3000.0] * 24,
            conformal_ebr=[1000.0] * 24,
        )
        configs = {
            "critical_demand_w": [1500.0] * 24,
            "critical_demand_ratio": 0.5,
            "battery": {"discharge_efficiency": 1.0},
        }
        res_t1 = _prepare_gap19_policy_b_config(bundle, configs)
        self.assertEqual(res_t1["ebr_target_wh"][0], 18000.0)

        # Tier 2: bundle.demand_critical is None, config["critical_demand_w"] used
        bundle_t2 = self._build_test_bundle(
            demand_pt=[10000.0] * 24,
            critical_demand_pt=None,
            conformal_ebr=[1000.0] * 24,
        )
        res_t2 = _prepare_gap19_policy_b_config(bundle_t2, configs)
        self.assertEqual(res_t2["ebr_target_wh"][0], 9000.0)

        # Tier 3: critical_demand_w is absent, config["critical_demand_ratio"] used
        configs_t3 = {
            "critical_demand_ratio": 0.4,
            "battery": {"discharge_efficiency": 1.0},
        }
        res_t3 = _prepare_gap19_policy_b_config(bundle_t2, configs_t3)
        self.assertEqual(res_t3["ebr_target_wh"][0], 24000.0)

        # Tier 4: all absent -> fails closed
        configs_t4 = {"battery": {"discharge_efficiency": 1.0}}
        with self.assertRaises(ValueError) as ctx:
            _prepare_gap19_policy_b_config(bundle_t2, configs_t4)
        self.assertIn("MISSING_GOVERNED_INPUT", str(ctx.exception))

    def test_35_critical_demand_validation_errors(self):
        bundle = self._build_test_bundle(critical_demand_pt=None, conformal_ebr=[5000.0] * 24)
        # Length != 24
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_w": [1000.0] * 23})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_w": [1000.0] * 25})
        # Invalid ratio
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_ratio": -0.1})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_ratio": 1.5})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_ratio": float("nan")})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"critical_demand_ratio": True})

        # Critical demand exceeds total demand
        bundle_excess = self._build_test_bundle(
            demand_pt=[1000.0] * 24,
            critical_demand_pt=[2000.0] * 24,
            conformal_ebr=[1000.0] * 24,
        )
        with self.assertRaises(ValueError) as ctx:
            _prepare_gap19_policy_b_config(bundle_excess, {})
        self.assertIn("exceeds total demand", str(ctx.exception))

        # NaN, Inf, Negative
        bundle_nan = self._build_test_bundle(demand_pt=[1000.0] * 24, critical_demand_pt=[float("nan")] * 24)
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle_nan, {})
        bundle_inf = self._build_test_bundle(demand_pt=[1000.0] * 24, critical_demand_pt=[float("inf")] * 24)
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle_inf, {})
        bundle_neg = self._build_test_bundle(demand_pt=[1000.0] * 24, critical_demand_pt=[-10.0] * 24)
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle_neg, {})

    def test_36_conformal_ebr_validation_errors(self):
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24)
        # Length != 24
        bundle.metadata["ebr_target_wh"] = [15000.0] * 23
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        bundle.metadata["ebr_target_wh"] = [15000.0] * 25
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        # Non-sequence
        bundle.metadata["ebr_target_wh"] = 15000.0
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        # NaN, Inf, Negative, Boolean
        bundle.metadata["ebr_target_wh"] = [float("nan")] * 24
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        bundle.metadata["ebr_target_wh"] = [float("inf")] * 24
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        bundle.metadata["ebr_target_wh"] = [-1.0] * 24
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})
        bundle.metadata["ebr_target_wh"] = [True] * 24
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {})

        # Valid string numeric conversion
        bundle.metadata["ebr_target_wh"] = ["12000.5"] * 24
        res = _prepare_gap19_policy_b_config(bundle, {"battery": {"discharge_efficiency": 1.0}})
        self.assertEqual(res["ebr_target_wh"][0], 12000.5)

    def test_37_exact_gap19_arithmetic_parity_and_window_truncation(self):
        cd_pt = [100.0 * (i + 1) for i in range(24)]
        bundle = self._build_test_bundle(
            demand_pt=[10000.0] * 24,
            critical_demand_pt=cd_pt,
            conformal_ebr=[0.0] * 24,
        )
        configs = {
            "battery": {"discharge_efficiency": 0.92},
            "optimizer": {"timestep_hours": 1.0},
        }

        expected_native = []
        eta_dis = 0.92
        dt = 1.0
        for t in range(24):
            end_k = min(t + 6, 24)
            w_sum = sum(cd_pt[k] * dt for k in range(t, end_k))
            expected_native.append((1.0 / eta_dis) * w_sum)

        res = _prepare_gap19_policy_b_config(bundle, configs)
        actual = res["ebr_target_wh"]

        self.assertEqual(len(actual), 24)
        for t in range(24):
            self.assertEqual(actual[t], expected_native[t], f"Mismatch at timestep {t}")

        # Explicitly verify window truncation at timesteps 18..23
        self.assertEqual(actual[18], (1.0 / 0.92) * sum(cd_pt[18:24]))
        self.assertEqual(actual[19], (1.0 / 0.92) * sum(cd_pt[19:24]))
        self.assertEqual(actual[20], (1.0 / 0.92) * sum(cd_pt[20:24]))
        self.assertEqual(actual[21], (1.0 / 0.92) * sum(cd_pt[21:24]))
        self.assertEqual(actual[22], (1.0 / 0.92) * sum(cd_pt[22:24]))
        self.assertEqual(actual[23], (1.0 / 0.92) * sum(cd_pt[23:24]))

    def test_38_efficiency_and_timestep_parameterization(self):
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[0.0] * 24)

        # Default efficiency 0.92 and default dt 1.0
        res_default = _prepare_gap19_policy_b_config(bundle, {})
        self.assertAlmostEqual(res_default["ebr_target_wh"][0], 6000.0 / 0.92, places=6)

        # Override efficiency 0.90 and dt 0.5 (6 steps = 3.0 h -> 3000 Wh -> 3000 / 0.90)
        configs_override = {
            "battery": {"discharge_efficiency": 0.90},
            "optimizer": {"timestep_hours": 0.5},
        }
        res_override = _prepare_gap19_policy_b_config(bundle, configs_override)
        self.assertAlmostEqual(res_override["ebr_target_wh"][0], 3000.0 / 0.90, places=6)

        # Malformed configs
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"battery": "not_a_dict"})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"battery": {"discharge_efficiency": -0.5}})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"optimizer": "not_a_dict"})
        with self.assertRaises(ValueError):
            _prepare_gap19_policy_b_config(bundle, {"optimizer": {"timestep_hours": -1.0}})

    def test_39_od01_terminal_target_and_policy_b_coexistence(self):
        state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[15000.0] * 24)
        raw_config = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}

        cfg_step1 = _prepare_gap19_terminal_target_config(state, raw_config)
        self.assertEqual(cfg_step1["terminal_target_wh"], 120000.0)

        cfg_step2 = _prepare_gap19_policy_b_config(bundle, cfg_step1)
        self.assertEqual(cfg_step2["terminal_target_wh"], 120000.0)
        self.assertIn("ebr_target_wh", cfg_step2)
        self.assertEqual(len(cfg_step2["ebr_target_wh"]), 24)

        # Case 1: terminal target (120,000 Wh) > combined ebr (~15,000 Wh)
        self.assertGreater(cfg_step2["terminal_target_wh"], cfg_step2["ebr_target_wh"][23])

        # Case 2: high conformal EBR at t=23 (150,000 Wh) > terminal target (120,000 Wh)
        high_ebr = [15000.0] * 23 + [150000.0]
        bundle_high = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=high_ebr)
        cfg_high = _prepare_gap19_policy_b_config(bundle_high, cfg_step1)
        self.assertEqual(cfg_high["terminal_target_wh"], 120000.0)
        self.assertEqual(cfg_high["ebr_target_wh"][23], 150000.0)
        self.assertGreater(cfg_high["ebr_target_wh"][23], cfg_high["terminal_target_wh"])

    def test_40_routed_optimizer_adapter_policy_b_execution(self):
        origin = "origin-policy-b"
        router = _FakeRouter(route="NORMAL")
        optimizer = _FakeGAP19Optimizer()
        origin_cfg = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "discharge_efficiency": 0.92},
            "critical_demand_w": [1000.0] * 24,
            "reserve_policy": "POLICY_B",
        }
        configs_by_origin = {origin: origin_cfg}
        adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin=configs_by_origin)

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[20000.0] * 24)
        forecast = {"origin": origin, "_real_bundle_ref": bundle, "step_index": 0}

        adapter.optimize(state, forecast, controller_settings=None)

        self.assertEqual(optimizer.call_count, 1)
        last_configs = optimizer.last_configs
        self.assertEqual(last_configs["terminal_target_wh"], 120000.0)
        self.assertEqual(last_configs["ebr_target_wh"][0], 20000.0)
        self.assertNotIn("terminal_target_wh", origin_cfg)
        self.assertNotIn("ebr_target_wh", origin_cfg)

    def test_41_policy_b_activation_signals_and_non_n6_compatibility(self):
        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        router = _FakeRouter()

        # Non-N6 / baseline bundle without Policy B
        base_bundle = self._build_test_bundle(
            critical_demand_pt=None,
            conformal_ebr=None,
            metadata_source="LocalBaselineForecastEngine",
        )
        base_cfg = {"battery": {"capacity_wh": 200000.0}}
        opt_base = _FakeGAP19Optimizer()
        adapter_base = RoutedOptimizerAdapter(router, opt_base, configs_by_origin={"orig-base": base_cfg})
        adapter_base.optimize(state, {"origin": "orig-base", "_real_bundle_ref": base_bundle, "step_index": 0}, None)

        self.assertNotIn("ebr_target_wh", opt_base.last_configs)

        # N6 Policy B missing required EBR fails closed
        n6_bundle_no_ebr = self._build_test_bundle(
            critical_demand_pt=[1000.0] * 24,
            conformal_ebr=None,
            metadata_source="CANDIDATE_N6_25ADD_15KT_SPECIALIST",
        )
        n6_bundle_no_ebr.metadata.pop("ebr_target_wh", None)
        n6_cfg = {"battery": {"capacity_wh": 200000.0}, "critical_demand_w": [1000.0] * 24}
        adapter_n6_fail = RoutedOptimizerAdapter(router, _FakeGAP19Optimizer(), configs_by_origin={"orig-n6": n6_cfg})
        with self.assertRaises(ValueError) as ctx:
            adapter_n6_fail.optimize(state, {"origin": "orig-n6", "_real_bundle_ref": n6_bundle_no_ebr, "step_index": 0}, None)
        self.assertIn("requires conformal 'ebr_target_wh'", str(ctx.exception))

    def test_42_multi_origin_isolation_no_leakage(self):
        router = _FakeRouter()
        optimizer = _FakeGAP19Optimizer()
        shared_cfg = {
            "battery": {"capacity_wh": 200000.0, "discharge_efficiency": 1.0},
            "reserve_policy": "POLICY_B",
        }
        configs_by_origin = {
            "origin-1": shared_cfg,
            "origin-2": shared_cfg,
        }
        adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin=configs_by_origin)

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        bundle_1 = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[10000.0] * 24)
        bundle_2 = self._build_test_bundle(critical_demand_pt=[3000.0] * 24, conformal_ebr=[5000.0] * 24)

        adapter.optimize(state, {"origin": "origin-1", "_real_bundle_ref": bundle_1, "step_index": 0}, None)
        cfg_1 = optimizer.last_configs
        self.assertEqual(cfg_1["ebr_target_wh"][0], 10000.0)

        adapter.optimize(state, {"origin": "origin-2", "_real_bundle_ref": bundle_2, "step_index": 0}, None)
        cfg_2 = optimizer.last_configs
        self.assertEqual(cfg_2["ebr_target_wh"][0], 18000.0)

        self.assertNotIn("ebr_target_wh", shared_cfg)
        self.assertNotIn("terminal_target_wh", shared_cfg)

    def test_43_override_bypass_forbidden_under_policy_b(self):
        bundle = self._build_test_bundle(critical_demand_pt=[1000.0] * 24, conformal_ebr=[15000.0] * 24)
        configs = {
            "policy": "POLICY_B",
            "ebr_target_wh_override": 5000.0,
        }
        with self.assertRaises(ValueError) as ctx:
            _prepare_gap19_policy_b_config(bundle, configs)
        self.assertIn("cannot be used to bypass Policy B", str(ctx.exception))

    def test_44_exact_nested_optimizer_timestep_hours_parity(self):
        bundle = self._build_test_bundle(critical_demand_pt=[2000.0] * 24, conformal_ebr=[10000.0] * 24)
        # Nested optimizer timestep_hours = 0.5 h
        configs = {
            "battery": {"discharge_efficiency": 0.90},
            "optimizer": {"timestep_hours": 0.5},
            "policy": "POLICY_B",
        }
        res = _prepare_gap19_policy_b_config(bundle, configs)
        # 6 timesteps * 0.5h = 3 hours * 2000W = 6000Wh / 0.90 = 6666.666... Wh
        # Pointwise max with conformal_ebr 10000.0 -> max(6666.67, 10000.0) = 10000.0
        self.assertEqual(res["ebr_target_wh"][0], 10000.0)
        # For a low conformal EBR, verify exact arithmetic
        bundle_low = self._build_test_bundle(critical_demand_pt=[2000.0] * 24, conformal_ebr=[1000.0] * 24)
        res_low = _prepare_gap19_policy_b_config(bundle_low, configs)
        self.assertAlmostEqual(res_low["ebr_target_wh"][0], 6000.0 / 0.90, places=6)


class TestN6ForecastOD02TimeAlignment(unittest.TestCase):
    def test_45_od02_bundle_alignment_shifts_solar_and_injects_fallback(self):
        """
        Decision OD-02:
          - Forecast rows 1..23 are mapped to dispatch steps 0..22.
          - Dispatch step 23 receives 0.0 baseline solar fallback (and ONLY step 23).
          - Solar generation is aligned identically.
          - Timestamps are advanced by 1 hour (from t0..t0+23h to t0+1h..t0+24h).
          - Demand, critical demand, and ebr_target_wh remain strictly unshifted.
          - Alignment is idempotent and sets metadata['od02_time_aligned'] = True.
        """
        raw_solar_irr = [float(i * 10.0) for i in range(24)]       # [0.0, 10.0, ..., 230.0]
        raw_solar_gen = [float(i * 100.0) for i in range(24)]      # [0.0, 100.0, ..., 2300.0]
        raw_demand = [5000.0 + i * 50.0 for i in range(24)]
        raw_crit_demand = [1000.0 + i * 10.0 for i in range(24)]
        raw_ebr = [15000.0 + i * 20.0 for i in range(24)]
        raw_ts = [f"2024-01-01T{h:02d}:00:00Z" for h in range(24)]

        class _CustomBundle:
            def __init__(self):
                self.solar_irradiance = _FakeTimeseries(list(raw_solar_irr))
                self.solar_generation = _FakeTimeseries(list(raw_solar_gen))
                self.demand = _FakeTimeseries(list(raw_demand))
                self.demand_critical = _FakeTimeseries(list(raw_crit_demand))
                self.timestamps = list(raw_ts)
                self.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }

        bundle = _CustomBundle()
        aligned = _align_n6_bundle_od02(bundle)

        # 1. Solar irradiance: steps 0..22 take raw rows 1..23
        self.assertEqual(aligned.solar_irradiance.point[:23], raw_solar_irr[1:])
        self.assertEqual(aligned.solar_irradiance.point[0], 10.0)
        self.assertEqual(aligned.solar_irradiance.point[22], 230.0)
        # Step 23 takes 0.0 fallback
        self.assertEqual(aligned.solar_irradiance.point[23], 0.0)

        # 2. Solar generation: steps 0..22 take raw rows 1..23; step 23 takes 0.0
        self.assertEqual(aligned.solar_generation.point[:23], raw_solar_gen[1:])
        self.assertEqual(aligned.solar_generation.point[0], 100.0)
        self.assertEqual(aligned.solar_generation.point[22], 2300.0)
        self.assertEqual(aligned.solar_generation.point[23], 0.0)

        # 3. Demand and critical demand must NOT be shifted
        self.assertEqual(aligned.demand.point, raw_demand)
        self.assertEqual(aligned.demand_critical.point, raw_crit_demand)

        # 4. EBR reserve floor must NOT be shifted
        self.assertEqual(aligned.metadata["ebr_target_wh"], raw_ebr)

        # 5. Timestamps advanced from [t0..t23] to [t1..t24]
        self.assertEqual(aligned.timestamps[0], "2024-01-01T01:00:00Z")
        self.assertEqual(aligned.timestamps[22], "2024-01-01T23:00:00Z")
        self.assertEqual(aligned.timestamps[23], "2024-01-02T00:00:00Z")

        # 6. Metadata provenance
        self.assertTrue(aligned.metadata.get("od02_time_aligned"))

        # 7. Idempotency: re-aligning returns identical bundle without double-shifting
        re_aligned = _align_n6_bundle_od02(aligned)
        self.assertEqual(re_aligned.solar_irradiance.point, aligned.solar_irradiance.point)
        self.assertEqual(re_aligned.timestamps, aligned.timestamps)

    def test_46_single_shot_adapter_serves_od02_aligned_views_and_preserves_policy_b(self):
        """
        N6ForecastProviderAdapter must produce per-step views where:
          - Step 0 view has solar irradiance equal to raw row 1.
          - Step 22 view has solar irradiance equal to raw row 23.
          - Step 23 view has solar irradiance equal to 0.0 (OD-02 fallback).
          - All step views have unshifted demand and unshifted ebr_target_wh.
          - RoutedOptimizerAdapter passes the aligned bundle through to the solver.
        """
        raw_solar_irr = [float(i * 15.0) for i in range(24)]
        raw_demand = [4000.0] * 24
        raw_ebr = [16000.0] * 24

        class _DistinctEngine:
            def predict(self, state, context):
                bundle = _FakeForecastBundle()
                bundle.solar_irradiance = _FakeTimeseries(list(raw_solar_irr))
                bundle.solar_generation = _FakeTimeseries([s * 50.0 for s in raw_solar_irr])
                bundle.demand = _FakeTimeseries(list(raw_demand))
                bundle.demand_critical = _FakeTimeseries([1000.0] * 24)
                bundle.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }
                return bundle

        engine = _DistinctEngine()
        adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={"origin-1": {"matrix": True}},
        )
        state_dict = StationStateCodec.to_plain_dict(_FakeStationState("t0", 80.0, 500.0))

        # Check all 24 dispatch steps
        for step in range(24):
            view = adapter.predict("origin-1", step, {"state": state_dict})
            if step < 23:
                expected_solar = raw_solar_irr[step + 1]
            else:
                expected_solar = 0.0  # Step 23 OD-02 fallback
            self.assertEqual(view["solar_irradiance_point"], expected_solar, f"Mismatch at step {step}")
            self.assertEqual(view["demand_point"], 4000.0, f"Demand shifted at step {step}")
            self.assertEqual(view["ebr_target_wh"], raw_ebr, f"EBR shifted at step {step}")

        # Check that optimizer receives the aligned bundle with step 23 fallback
        optimizer = _FakeGAP19Optimizer()
        router = _FakeRouter()
        routed_adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={"origin-1": {}})
        real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)
        opt_state = {"_real_station_state_ref": real_state}

        view0 = adapter.predict("origin-1", 0, {"state": state_dict})
        routed_adapter.optimize(opt_state, view0, None)

        received_bundle = optimizer.last_bundle
        self.assertEqual(received_bundle.solar_irradiance.point[0], raw_solar_irr[1])
        self.assertEqual(received_bundle.solar_irradiance.point[22], raw_solar_irr[23])
        self.assertEqual(received_bundle.solar_irradiance.point[23], 0.0)
        self.assertEqual(received_bundle.solar_generation.point[23], 0.0)

        # Policy B and OD-01 remain fully applied on optimizer configs
        cfg = optimizer.last_configs
        self.assertIn("ebr_target_wh", cfg)
        self.assertEqual(cfg["terminal_target_wh"], 120000.0)  # OD-01 intact

    def test_47_fail_closed_on_non_24_element_solar_timeseries(self):
        """OD-02 alignment fails closed if solar forecast is not 24 elements."""
        bundle = _FakeForecastBundle()
        bundle.solar_irradiance = _FakeTimeseries([100.0] * 12)  # only 12 elements
        with self.assertRaises(ValueError) as ctx:
            _align_n6_bundle_od02(bundle)
        self.assertIn("OD-02 alignment requires 24-step forecast", str(ctx.exception))

    def test_48_od02_candidate_c2_clearsky_ratio_math_and_thresholds(self):
        """
        Decision OD-02-C (Pass 24) Candidate C.2 Clear-Sky Ratio math:
          - If clearsky_t23 < 5.0 W/m^2, uses threshold rule: 1.0 * clearsky_t24.
          - If clearsky_t23 >= 5.0 W/m^2, uses ML cloud transmittance Kt = min(forecast/clearsky, 1.2).
          - Non-negative guarantee: max(0.0, ...).
        """
        # 1. Low clear-sky threshold rule (< 5.0 W/m^2)
        val = _compute_boundary_clearsky_ratio(forecast_t23=0.0, clearsky_t23=2.0, clearsky_t24=3.5)
        self.assertAlmostEqual(val, 3.5, places=6)

        # 2. Polar night / zero clear-sky
        val_night = _compute_boundary_clearsky_ratio(forecast_t23=0.0, clearsky_t23=0.0, clearsky_t24=0.0)
        self.assertEqual(val_night, 0.0)

        # 3. Standard daytime Kt ratio
        # forecast 300 / clearsky 600 = Kt 0.5; clearsky_t24 = 500 -> 250.0
        val_day = _compute_boundary_clearsky_ratio(forecast_t23=300.0, clearsky_t23=600.0, clearsky_t24=500.0)
        self.assertAlmostEqual(val_day, 250.0, places=6)

        # 4. Cap at Kt = 1.2
        # forecast 800 / clearsky 500 = 1.6 -> clamped to 1.2; clearsky_t24 = 400 -> 480.0
        val_capped = _compute_boundary_clearsky_ratio(forecast_t23=800.0, clearsky_t23=500.0, clearsky_t24=400.0)
        self.assertAlmostEqual(val_capped, 480.0, places=6)

    def test_49_od02_bundle_and_adapter_clearsky_ratio_in_polar_day(self):
        """
        Decision OD-02-C (Pass 24):
        Under polar day (e.g. 2024-06-01), step 23 solar prediction must NOT be padded
        with [0.0], but dynamically computed from Candidate C.2 Clear-Sky Ratio.
        """
        raw_solar_irr = [100.0 + float(i * 10.0) for i in range(24)]
        raw_solar_gen = [(100.0 + float(i * 10.0)) * 51.0 for i in range(24)]
        raw_demand = [4000.0] * 24
        raw_crit_demand = [1000.0] * 24
        raw_ebr = [16000.0] * 24
        # 2024-06-01T00:00:00Z: polar day midnight
        origin_str = "2024-06-01T00:00:00Z"
        raw_ts = [(pd.to_datetime(origin_str) + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]

        class _PolarDayBundle:
            def __init__(self):
                self.solar_irradiance = _FakeTimeseries(list(raw_solar_irr))
                self.solar_generation = _FakeTimeseries(list(raw_solar_gen))
                self.demand = _FakeTimeseries(list(raw_demand))
                self.demand_critical = _FakeTimeseries(list(raw_crit_demand))
                self.timestamps = list(raw_ts)
                self.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }

        bundle = _PolarDayBundle()
        aligned = _align_n6_bundle_od02(bundle, origin_timestamp_str=origin_str)

        # Expected clear-sky values for 2024-06-01T00:00:00Z:
        # t23 is 2024-06-01 23:00 UTC (clearsky_ghi = 2.41016... W/m^2 < 5.0 W/m^2)
        # t24 is 2024-06-02 00:00 UTC (clearsky_ghi = 1.55864... W/m^2)
        # Under C.2 threshold rule (cs_t23 < 5.0), expected step 23 irradiance = 1.0 * cs_t24 = 1.5586416106335632
        expected_irr_23 = 1.5586416106335632
        self.assertAlmostEqual(aligned.solar_irradiance.point[23], expected_irr_23, places=5)
        self.assertGreater(aligned.solar_irradiance.point[23], 0.0)

        # Expected step 23 solar generation: 1.5586416... * 51.0 W
        expected_gen_23 = expected_irr_23 * 51.0
        self.assertAlmostEqual(aligned.solar_generation.point[23], expected_gen_23, places=4)
        self.assertGreater(aligned.solar_generation.point[23], 0.0)

        # Solar steps 0..22 shifted normally
        self.assertEqual(aligned.solar_irradiance.point[:23], raw_solar_irr[1:])
        self.assertEqual(aligned.solar_generation.point[:23], raw_solar_gen[1:])
        self.assertTrue(aligned.metadata.get("od02_time_aligned"))

        # Verify N6ForecastProviderAdapter passes non-zero step 23 to step view and optimizer
        class _Engine:
            def predict(self, state, context):
                b = _PolarDayBundle()
                return b

        adapter = N6ForecastProviderAdapter(
            real_forecast_engine=_Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin_str: {"matrix": True}},
        )
        state_dict = StationStateCodec.to_plain_dict(_FakeStationState("t0", 80.0, 500.0))
        view23 = adapter.predict(origin_str, 23, {"state": state_dict})
        self.assertAlmostEqual(view23["solar_irradiance_point"], expected_irr_23, places=5)


if __name__ == "__main__":
    unittest.main()


