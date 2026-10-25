"""
POLARIS -- N6 Receding-Horizon Adapters + IA-2 Route Provenance + IA-3
Authoritative-State Lookup Test Suite
=====================================================================================
Companion to `forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md`. Validates, EXCLUSIVELY against
hand-built Fakes:

  (1) IA-1 (owner decision): the receding-horizon adapter variant in
      `system/evaluation/n6_multi_origin_harness/adapters.py`
      (`N6RecedingHorizonForecastAdapter`, `N6RecedingHorizonRouterAdapter`,
      `N6RecedingHorizonOptimizerAdapter`, `RecedingHorizonPlanSlicingSimulatorAdapter`)
      -- re-forecasts/re-routes/re-optimizes FRESH every simulated step, no
      cross-step caching, exercised through the REAL, UNMODIFIED
      `execute_origin_dispatch_cell` loop in `harness.py`.
  (2) IA-2 (owner decision): `RouterProtocol`, `OriginRunResult.route` /
      `route_history`, `OriginRunStatus.FAILED_UNKNOWN_INVALID`, and
      `CampaignAggregateResult.route_counts` -- route provenance recorded
      explicitly, never inferred, never silently defaulted, never dropped
      through aggregation.
  (3) IA-3 (still OPEN -- not resolved by this pass): `resolve_authoritative_initial_state`
      / `AuthoritativeInitialStateUnavailableError` -- the fail-closed lookup
      that stands in for the still-nonexistent per-origin initial-state table.

GOVERNANCE STATUS: NON-PRODUCTION / NOT EXECUTED / NO NEW EXECUTION PATH
-------------------------------------------------------------------------
- Every forecast engine / router / optimizer / option-D solver / simulator /
  safety-evaluator object used below is a small hand-written Fake local to
  this file. Nothing here imports, constructs, or calls a real
  `N6SolarForecastEngine`, `EMSControlRouter`, `GAP19HighsNativeOptimizer`,
  `OptionDFallbackSolver`, `DigitalTwinSimulator`, or
  `reserve_policy_guard.evaluate_dispatch_safety`.
- `execute_origin_dispatch_cell` is called directly, never through
  `MultiOriginCampaignHarness.execute_campaign` -- the unconditional
  `CampaignExecutionNotAuthorizedError` gate is untouched and not exercised
  here (see `TestCampaignGuardStillUnauthorized` at the bottom, which
  confirms it is still unconditional without importing/constructing any
  real production object to do so).
- No sealed/blind-partition path, frozen model artifact, or real dataset is
  read.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import unittest

from system.evaluation.n6_multi_origin_harness.adapters import (
    AuthoritativeInitialStateUnavailableError,
    N6RecedingHorizonForecastAdapter,
    N6RecedingHorizonOptimizerAdapter,
    N6RecedingHorizonRouterAdapter,
    RecedingHorizonPlanSlicingSimulatorAdapter,
    StationStateCodec,
    _prepare_gap19_policy_b_config,
    _prepare_gap19_terminal_target_config,
    resolve_authoritative_initial_state,
    _align_timeseries_od02,
    _align_n6_bundle_od02,
)
from system.evaluation.n6_multi_origin_harness.harness import (
    OriginRunStatus,
    aggregate_origin_results,
    execute_origin_dispatch_cell,
)
from system.evaluation.replay_harness import (
    CampaignExecutionNotAuthorizedError,
    MatchedControllerSettings,
    ScenarioSpec,
)


# ---------------------------------------------------------------------------
# Fakes mirroring the REAL classes' shapes (never the real classes themselves).
# ---------------------------------------------------------------------------


_STATE_UNSET = object()


class _FakeStationState:
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
        # Mirrors the REAL StationState.from_dict: direct required-key
        # indexing (KeyError on a missing required field).
        return cls(
            data["timestamp"],
            data["battery_soc_pct"],
            data.get("diesel_fuel_remaining_liters", 0.0),
            battery_energy_wh=data.get("battery_energy_wh", _STATE_UNSET),
            terminal_target_wh_override=data.get("terminal_target_wh_override"),
        )


class _FakeTimeseries:
    def __init__(self, point):
        self.point = point
        self.lower = point
        self.upper = point


class _FakeForecastBundle:
    def __init__(self, tag):
        self.tag = tag  # lets a test assert WHICH call produced this bundle
        self.solar_irradiance = _FakeTimeseries([100.0] * 24)
        self.demand = _FakeTimeseries([5000.0] * 24)
        self.metadata = {"ebr_target_wh": [15000.0] * 24}


class _FakeN6Engine:
    def __init__(self):
        self.predict_call_count = 0
        self.seen_feature_matrices = []

    def predict(self, station_state, context):
        self.predict_call_count += 1
        self.seen_feature_matrices.append(context["n6_feature_matrix"])
        return _FakeForecastBundle(tag=f"bundle_{self.predict_call_count}")


class _FakeRouter:
    """Returns a caller-controlled, PER-CALL route from a fixed sequence."""

    def __init__(self, route_sequence):
        self._routes = list(route_sequence)
        self.call_count = 0

    def evaluate_and_route(self, station_state, bundle, configs):
        route = self._routes[self.call_count]
        self.call_count += 1
        return ({"ok": True, "which_call": self.call_count}, route)


class _FakeDispatchPlan:
    def __init__(self, schema_version, timestamps, solar_used, wind_used, battery_charge, battery_discharge,
                 battery_soc, diesel_power, load_served, flexible_load_schedule, renewable_curtailment,
                 unmet_load, objective_value, constraint_status, energy_balance_errors, unmet_essential=None,
                 tag=None):
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
        self.tag = tag


def _make_plan(diesel_power_hour0=200.0, tag="plan"):
    return _FakeDispatchPlan(
        schema_version="1.0.0",
        timestamps=[f"T{i}" for i in range(24)],
        solar_used=[10.0] * 24,
        wind_used=[0.0] * 24,
        battery_charge=[0.0] * 24,
        battery_discharge=[5.0] * 24,
        battery_soc=[150000.0] * 24,
        diesel_power=[diesel_power_hour0] * 24,
        load_served=[5000.0] * 24,
        flexible_load_schedule=[0.0] * 24,
        renewable_curtailment=[0.0] * 24,
        unmet_load=[0.0] * 24,
        objective_value=1.23,
        constraint_status="OPTIMAL",
        energy_balance_errors=[0.0] * 24,
        unmet_essential=[0.0] * 24,
        tag=tag,
    )


class _FakeGAP19Optimizer:
    def __init__(self):
        self.call_count = 0
        self.last_configs = None
        self.last_bundle = None
        self.seen_configs = []
        self.seen_states = []

    def optimize(self, bundle, station_state, configs):
        self.call_count += 1
        self.last_bundle = bundle
        self.last_configs = configs
        self.seen_configs.append(configs)
        self.seen_states.append(station_state)
        return _make_plan(diesel_power_hour0=200.0, tag=f"gap19_{self.call_count}")


class _FakeOptionDSolver:
    def __init__(self):
        self.call_count = 0
        self.last_configs = None
        self.seen_configs = []
        self.seen_states = []

    def solve(self, assessment, bundle, station_state, configs):
        self.call_count += 1
        self.last_configs = configs
        self.seen_configs.append(configs)
        self.seen_states.append(station_state)
        return _make_plan(diesel_power_hour0=999.0, tag=f"option_d_{self.call_count}")


class _FakeDigitalTwinSimulator:
    def __init__(self, fuel_burn_per_hour=0.5):
        self._fuel_burn_per_hour = fuel_burn_per_hour
        self.call_count = 0
        self.seen_plans = []

    def step(self, station_state, one_hour_slice, actual_t):
        self.call_count += 1
        # The receding-horizon simulator adapter rebuilds a fresh
        # `_FakeDispatchPlan` each call (never forwarding `tag`) -- record
        # `diesel_power[0]` instead, which DOES distinguish a GAP19 plan
        # (200.0, see `_make_plan`'s default) from an Option D plan (999.0).
        self.seen_plans.append(one_hour_slice.diesel_power[0])
        return _FakeStationState(
            timestamp=one_hour_slice.timestamps[0],
            battery_soc_pct=station_state.battery_soc_pct - 1.0,
            diesel_fuel_remaining_liters=station_state.diesel_fuel_remaining_liters - self._fuel_burn_per_hour,
        )


def _build_scenario(origin: str) -> ScenarioSpec:
    settings = MatchedControllerSettings(
        battery_params={},
        diesel_generator_constraints={},
        fuel_curve_params={},
        gap19_solver_settings={},
        objective_priorities={},
        termination_criteria={},
        demand_criticality_config={},
        scenario_inclusion_rules={},
    )
    return ScenarioSpec(
        scenario_key=origin,
        forecast_origin=origin,
        initial_battery_soc_wh=160000.0,
        controller_settings=settings,
        forecast_provider="n6_solar",
        reserve_policy_name="GOVERNED_DEFAULT_RESERVE_POLICY",
    )


def _build_initial_state(origin_tag="o1", soc=80.0, fuel=500.0):
    real_state = _FakeStationState(
        timestamp=f"2024-06-01T00:00:00Z|{origin_tag}", battery_soc_pct=soc, diesel_fuel_remaining_liters=fuel
    )
    plain = StationStateCodec.to_plain_dict(real_state)
    plain["_real_station_state_ref"] = real_state
    plain["_step_index"] = 0
    return plain


# ---------------------------------------------------------------------------
# (1) Receding-horizon call-sequence/cadence tests
# ---------------------------------------------------------------------------


class TestRecedingHorizonCadenceSingleOrigin(unittest.TestCase):
    """
    IA-1: verifies each step uses UPDATED simulated state and invokes
    forecast/routing/optimization at the intended cadence -- i.e. every
    step, never cached, in contrast to the single-shot adapters' "once per
    origin" cadence already locked in by
    `test_n6_ia1_ia2_call_sequence_integration.py`.
    """

    def test_01_forecast_router_optimizer_each_called_once_per_step(self):
        origin = "origin-A"
        expected_steps = 4
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("A")

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )

        router = _FakeRouter(route_sequence=["NORMAL"] * expected_steps)
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})

        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: {}})

        simulator = _FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5)
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "receding_horizon_cadence"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, expected_steps)

        # IA-1: fresh every step, NOT once per origin.
        self.assertEqual(engine.predict_call_count, expected_steps, "N6 engine must be called every step")
        self.assertEqual(router.call_count, expected_steps, "router must be called every step")
        self.assertEqual(gap19.call_count, expected_steps, "GAP19 must be called every step (receding horizon)")
        self.assertEqual(option_d.call_count, 0, "Option D must never be called on an all-NORMAL route sequence")
        self.assertEqual(simulator.call_count, expected_steps)

        # Route provenance (IA-2): one route recorded per step, all NORMAL.
        self.assertEqual(result.route, "NORMAL")
        self.assertEqual(result.route_history, ("NORMAL", "NORMAL", "NORMAL", "NORMAL"))

        # No future-information leakage: engine saw exactly the per-step
        # feature matrices supplied, in order, never a later step's entry
        # reused for an earlier one.
        self.assertEqual(engine.seen_feature_matrices, [{"step": i} for i in range(expected_steps)])

    def test_02_updated_simulated_state_flows_forward_each_step(self):
        """Each step's StationState the engine/router see reflects the PRIOR step's simulator output, not the initial state replayed."""
        origin = "origin-A"
        expected_steps = 3
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("A", soc=80.0, fuel=500.0)

        seen_socs = []

        class _RecordingEngine(_FakeN6Engine):
            def predict(self, station_state, context):
                seen_socs.append(station_state.battery_soc_pct)
                return super().predict(station_state, context)

        engine = _RecordingEngine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )
        router_adapter = N6RecedingHorizonRouterAdapter(
            _FakeRouter(["NORMAL"] * expected_steps), configs_by_origin={origin: {}}
        )
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(
            _FakeGAP19Optimizer(), _FakeOptionDSolver(), configs_by_origin={origin: {}}
        )
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "receding_horizon_state_flow"},
        )

        # SOC decrements by 1.0 each step (the Fake simulator's own rule) --
        # 80.0 at step 0, 79.0 at step 1, 78.0 at step 2. Never re-reads the
        # same initial 80.0 three times.
        self.assertEqual(seen_socs, [80.0, 79.0, 78.0])


class TestRecedingHorizonRouteBranchingAndUnknownInvalid(unittest.TestCase):
    """IA-2: NORMAL/EMERGENCY/UNKNOWN_INVALID are each preserved distinctly, never inferred from which solver ran."""

    def test_03_emergency_route_invokes_option_d_not_gap19(self):
        origin = "origin-B"
        expected_steps = 2
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("B")

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )
        router = _FakeRouter(["EMERGENCY", "EMERGENCY"])
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: {}})
        simulator = _FakeDigitalTwinSimulator()
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "emergency_route"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(option_d.call_count, 2, "EMERGENCY route must invoke Option D")
        self.assertEqual(gap19.call_count, 0, "EMERGENCY route must never invoke GAP19")
        self.assertEqual(result.route, "EMERGENCY")
        self.assertEqual(result.route_history, ("EMERGENCY", "EMERGENCY"))
        self.assertEqual(simulator.seen_plans, [999.0, 999.0], "simulator must receive the Option D plan's values")

    def test_04_route_can_change_mid_run_recorded_per_step(self):
        """A receding-horizon run can legitimately route NORMAL then EMERGENCY then back -- route_history must capture exactly that sequence, never collapse it to one value."""
        origin = "origin-C"
        expected_steps = 3
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("C")

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )
        router = _FakeRouter(["NORMAL", "EMERGENCY", "NORMAL"])
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: {}})
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "mixed_route"},
        )

        self.assertEqual(result.route_history, ("NORMAL", "EMERGENCY", "NORMAL"))
        self.assertEqual(result.route, "NORMAL", "final route must be the LAST step's, not the first or majority")
        self.assertEqual(gap19.call_count, 2)
        self.assertEqual(option_d.call_count, 1)

    def test_05_unknown_invalid_halts_fail_closed_before_optimizer(self):
        """Mirrors worker.py's Cell B `status = 'FAILED_UNKNOWN_INVALID'; break` branch exactly."""
        origin = "origin-D"
        expected_steps = 4
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("D")

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )
        # NORMAL at step 0, then UNKNOWN_INVALID at step 1 -- the loop must
        # halt there, never reaching steps 2/3.
        router = _FakeRouter(["NORMAL", "UNKNOWN_INVALID", "NORMAL", "NORMAL"])
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: {}})
        simulator = _FakeDigitalTwinSimulator()
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "unknown_invalid_halt"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.FAILED_UNKNOWN_INVALID)
        self.assertEqual(result.completed_steps, 1, "only step 0 (NORMAL) completed before the halt")
        self.assertEqual(result.route, "UNKNOWN_INVALID")
        self.assertEqual(result.route_history, ("NORMAL", "UNKNOWN_INVALID"))
        self.assertEqual(router.call_count, 2, "router must not be called again after the halt")
        self.assertEqual(gap19.call_count, 1, "GAP19 ran once, for step 0's NORMAL route, never for the halted step")
        self.assertEqual(option_d.call_count, 0)
        self.assertEqual(simulator.call_count, 1)
        self.assertTrue(
            any("UNKNOWN_INVALID" in reason for reason in result.failure_reasons),
            f"expected an UNKNOWN_INVALID failure reason, got: {result.failure_reasons}",
        )

    def test_06_router_optional_preexisting_callers_unaffected(self):
        """Backward compatibility: router=None (the default) keeps route/route_history empty/None, matching every pre-existing call site."""
        origin = "origin-E"
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("E")
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=_FakeN6Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}, {"step": 1}]},
        )
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(
            _FakeGAP19Optimizer(), _FakeOptionDSolver(), configs_by_origin={origin: {}}
        )

        # Without a router, N6RecedingHorizonOptimizerAdapter.optimize never
        # receives a "route" key in forecast -- it must fail closed, not
        # silently assume NORMAL. This documents that the receding-horizon
        # OPTIMIZER adapter is NOT usable without a paired router (unlike
        # the single-shot RoutedOptimizerAdapter, which folds routing in
        # itself) -- a deliberate IA-1/IA-2 consequence of splitting the
        # router into its own Protocol slot.
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * 2},
            _allow_synthetic_actuals_for_testing=True,
        )
        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=2,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            # router omitted entirely -- exercises the default.
            provenance={"test": "router_optional"},
        )
        self.assertEqual(result.run_status, OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION)
        self.assertIsNone(result.route)
        self.assertEqual(result.route_history, ())


class TestRecedingHorizonMultiOriginIsolation(unittest.TestCase):
    """IA-1 directive requirement: test multiple origins to ensure state and route data cannot leak between origins."""

    def test_07_two_origins_through_shared_adapter_instances_do_not_leak(self):
        origin_x, origin_y = "origin-X", "origin-Y"
        steps = 3

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={
                origin_x: [{"origin": "X", "step": i} for i in range(steps)],
                origin_y: [{"origin": "Y", "step": i} for i in range(steps)],
            },
        )
        router = _FakeRouter(["NORMAL"] * steps + ["EMERGENCY"] * steps)
        router_adapter = N6RecedingHorizonRouterAdapter(
            router, configs_by_origin={origin_x: {"cfg": "x"}, origin_y: {"cfg": "y"}}
        )
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(
            gap19, option_d, configs_by_origin={origin_x: {"cfg": "x"}, origin_y: {"cfg": "y"}}
        )
        simulator = _FakeDigitalTwinSimulator()
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={
                origin_x: [{"actual_SW_IN": 11.0}] * steps,
                origin_y: [{"actual_SW_IN": 22.0}] * steps,
            },
            _allow_synthetic_actuals_for_testing=True,
        )

        result_x = execute_origin_dispatch_cell(
            origin=origin_x,
            arm="candidate",
            scenario=_build_scenario(origin_x),
            expected_steps=steps,
            initial_state=_build_initial_state("X", soc=80.0),
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"origin": origin_x},
        )
        result_y = execute_origin_dispatch_cell(
            origin=origin_y,
            arm="candidate",
            scenario=_build_scenario(origin_y),
            expected_steps=steps,
            initial_state=_build_initial_state("Y", soc=50.0),
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"origin": origin_y},
        )

        # Route isolation: X ran all-NORMAL (first `steps` router calls),
        # Y ran all-EMERGENCY (the next `steps`) -- neither origin's route
        # history leaks into the other's.
        self.assertEqual(result_x.route_history, ("NORMAL",) * steps)
        self.assertEqual(result_y.route_history, ("EMERGENCY",) * steps)
        self.assertEqual(gap19.call_count, steps, "GAP19 only for X's NORMAL steps")
        self.assertEqual(option_d.call_count, steps, "Option D only for Y's EMERGENCY steps")

        # Feature-matrix isolation: the engine saw X's own tagged matrices
        # for the first `steps` calls and Y's own tagged matrices for the
        # next `steps` -- never cross-assigned.
        seen = engine.seen_feature_matrices
        self.assertTrue(all(m["origin"] == "X" for m in seen[:steps]))
        self.assertTrue(all(m["origin"] == "Y" for m in seen[steps:]))

        # State isolation: X started at SOC 80.0, Y at SOC 50.0 -- their
        # final completed_steps/run_status must not reflect each other's
        # initial condition.
        self.assertEqual(result_x.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result_y.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result_x.completed_steps, steps)
        self.assertEqual(result_y.completed_steps, steps)


# ---------------------------------------------------------------------------
# (2) Route provenance through aggregation/summary
# ---------------------------------------------------------------------------


class TestRouteProvenanceThroughAggregation(unittest.TestCase):
    def test_08_route_counts_aggregate_correctly_and_exclude_none(self):
        origin_a, origin_b, origin_c = "a", "b", "c"
        steps = 1

        def _run_with_route(origin, route):
            forecast_adapter = N6RecedingHorizonForecastAdapter(
                real_forecast_engine=_FakeN6Engine(),
                station_state_cls=_FakeStationState,
                feature_matrix_by_origin_and_step={origin: [{"step": 0}]},
            )
            router_adapter = N6RecedingHorizonRouterAdapter(
                _FakeRouter([route]), configs_by_origin={origin: {}}
            )
            optimizer_adapter = N6RecedingHorizonOptimizerAdapter(
                _FakeGAP19Optimizer(), _FakeOptionDSolver(), configs_by_origin={origin: {}}
            )
            simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
                real_simulator=_FakeDigitalTwinSimulator(),
                dispatch_plan_cls=_FakeDispatchPlan,
                actuals_by_origin_and_step={origin: [{"actual_SW_IN": 1.0}] * steps},
            _allow_synthetic_actuals_for_testing=True,
            )
            return execute_origin_dispatch_cell(
                origin=origin,
                arm="candidate",
                scenario=_build_scenario(origin),
                expected_steps=steps,
                initial_state=_build_initial_state(origin),
                forecast_provider=forecast_adapter,
                optimizer=optimizer_adapter,
                simulator=simulator_adapter,
                safety_evaluator=None,
                router=router_adapter,
                provenance={},
            )

        r_a = _run_with_route(origin_a, "NORMAL")
        r_b = _run_with_route(origin_b, "NORMAL")
        r_c = _run_with_route(origin_c, "EMERGENCY")

        agg = aggregate_origin_results([r_a, r_b, r_c], arm="candidate")
        self.assertEqual(agg.route_counts, {"NORMAL": 2, "EMERGENCY": 1})
        self.assertEqual(agg.n_origins, 3)
        # Every individual OriginRunResult's own route/route_history survives
        # untouched inside per_origin -- aggregation never strips it.
        self.assertEqual({r.origin: r.route for r in agg.per_origin}, {"a": "NORMAL", "b": "NORMAL", "c": "EMERGENCY"})

    def test_09_route_counts_excludes_router_less_runs(self):
        """A run with router=None contributes nothing to route_counts, never defaulted into a bucket."""
        from system.evaluation.n6_multi_origin_harness.harness import record_origin_outcome

        no_router_result = record_origin_outcome(
            origin="z", arm="candidate", scenario_key="z", forecast_provider="n6_solar",
            completed_steps=1, expected_steps=1,
            dispatch_outcome={"constraint_status": "OPTIMAL"}, safety_evaluation=None, provenance={},
        )
        agg = aggregate_origin_results([no_router_result], arm="candidate")
        self.assertEqual(agg.route_counts, {})
        self.assertIsNone(no_router_result.route)


# ---------------------------------------------------------------------------
# (3) IA-3: authoritative initial-state lookup (fail-closed, not resolved)
# ---------------------------------------------------------------------------


class TestAuthoritativeInitialStateLookup(unittest.TestCase):
    def test_10_valid_handoff_returns_a_copy_not_a_reference(self):
        registry = {"origin-1": {"timestamp": "T0", "battery_soc_pct": 80.0}}
        resolved = resolve_authoritative_initial_state("origin-1", registry)
        self.assertEqual(resolved, registry["origin-1"])
        resolved["battery_soc_pct"] = 999.0
        self.assertEqual(registry["origin-1"]["battery_soc_pct"], 80.0, "must return a copy, never the live registry dict")

    def test_11_missing_origin_fails_closed_never_invents(self):
        registry = {"origin-1": {"timestamp": "T0", "battery_soc_pct": 80.0}}
        with self.assertRaises(AuthoritativeInitialStateUnavailableError) as ctx:
            resolve_authoritative_initial_state("origin-999-not-in-registry", registry)
        self.assertIn("origin-999-not-in-registry", str(ctx.exception))
        self.assertIn("IA-3", str(ctx.exception))

    def test_12_empty_registry_fails_closed_for_every_origin(self):
        """As of this pass, NO caller anywhere in this repository supplies a non-empty registry -- this is the current, honest state of IA-3."""
        with self.assertRaises(AuthoritativeInitialStateUnavailableError):
            resolve_authoritative_initial_state("any-origin-at-all", {})


class TestCampaignGuardStillUnauthorized(unittest.TestCase):
    """Confirms this pass did not touch the campaign-execution guard, without constructing any real production object."""

    def test_13_execute_campaign_still_raises_unconditionally(self):
        from system.evaluation.n6_multi_origin_harness.harness import (
            MultiOriginCampaignConfig,
            MultiOriginCampaignHarness,
        )

        harness = MultiOriginCampaignHarness()
        # `execute_experiment_a` raises UNCONDITIONALLY, before touching its
        # argument at all (confirmed by direct read of replay_harness.py
        # this pass) -- so a bare placeholder config is sufficient here;
        # this is a guard-presence check, not a configuration-validity
        # check (that is `validate_campaign_config`'s job, untouched by
        # this pass, tested elsewhere).
        placeholder_config = MultiOriginCampaignConfig(origins=["x"], experiment_a_config=None)  # type: ignore[arg-type]
        with self.assertRaises(CampaignExecutionNotAuthorizedError):
            harness.execute_campaign(config=placeholder_config)


class TestRecedingHorizonOD01DynamicTerminalTarget(unittest.TestCase):
    """
    Validates OD-01 dynamic terminal target behavior in N6RecedingHorizonOptimizerAdapter
    per POLARIS Master Decision Register v1.9.12 Section 38:
      1. Dynamic per-step recalculation using each simulated step's state.
      2. Strict immutability of the caller's configs_by_origin dictionary.
      3. Complete isolation and bypass of helper when route is EMERGENCY.
      4. Overrides taking precedence over dynamic derivation.
    """

    def test_14_receding_horizon_per_step_recalculation_and_immutability(self):
        origin = "origin-od01-recalc"
        expected_steps = 3
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("od01", soc=80.0, fuel=500.0)

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )

        router = _FakeRouter(route_sequence=["NORMAL"] * expected_steps)
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})

        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin_cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
        configs_by_origin = {origin: origin_cfg}
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin=configs_by_origin)

        simulator = _FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5)
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            provenance={"test": "od01_per_step_recalc"},
            router=router_adapter,
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(gap19.call_count, 3)

        # 1. Verify per-step dynamic recalculation
        # Step 0: SOC 80% -> 160,000 Wh -> target = 160,000 - 40,000 = 120,000 Wh
        # Step 1: SOC 79% -> 158,000 Wh -> target = 158,000 - 40,000 = 118,000 Wh
        # Step 2: SOC 78% -> 156,000 Wh -> target = 156,000 - 40,000 = 116,000 Wh
        self.assertEqual(len(gap19.seen_configs), 3)
        self.assertEqual(gap19.seen_configs[0]["terminal_target_wh"], 120000.0)
        self.assertEqual(gap19.seen_configs[1]["terminal_target_wh"], 118000.0)
        self.assertEqual(gap19.seen_configs[2]["terminal_target_wh"], 116000.0)

        # 2. Verify strict immutability of caller configs_by_origin
        self.assertNotIn("terminal_target_wh", origin_cfg, "origin configuration dictionary must remain immutable")

    def test_15_emergency_route_completely_bypasses_helper(self):
        origin = "origin-emergency-bypass"
        expected_steps = 1
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("emerg", soc=80.0, fuel=500.0)

        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=_FakeN6Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}]},
        )
        router = _FakeRouter(route_sequence=["EMERGENCY"])
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})

        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin_cfg = {"battery": {"capacity_wh": 200000.0}}
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        simulator = _FakeDigitalTwinSimulator()
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}]},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            provenance={"test": "emergency_bypass"},
            router=router_adapter,
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(gap19.call_count, 0, "GAP19 optimizer must NOT be invoked on EMERGENCY route")
        self.assertEqual(option_d.call_count, 1, "Option D solver must be invoked on EMERGENCY route")
        self.assertNotIn("terminal_target_wh", option_d.last_configs, "Option D solver must not receive terminal_target_wh")
        self.assertNotIn("terminal_target_wh", origin_cfg, "caller config must remain untouched")

    def test_16_state_override_precedence_in_receding_horizon(self):
        origin = "origin-state-override"
        # Explicit state override present, but battery_energy_wh is None and battery config is invalid
        real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=None, terminal_target_wh_override=45000.0)
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin_cfg = {"battery": {"capacity_wh": -200000.0, "min_soc_pct": -10.0}}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": _FakeForecastBundle(tag="b1"),
            "_real_station_state_ref": real_state,
        }
        adapter.optimize(state={}, forecast=forecast, controller_settings=None)

        self.assertEqual(gap19.call_count, 1)
        self.assertNotIn("terminal_target_wh", gap19.last_configs, "terminal_target_wh must not be injected when state override is active")
        self.assertNotIn("terminal_target_wh", origin_cfg, "caller origin config must remain untouched")

    def test_17_explicit_config_target_precedence_in_receding_horizon(self):
        origin = "origin-config-override"
        # Explicit config target present, but battery_energy_wh is None and battery config is malformed
        real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=None)
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin_cfg = {"battery": "invalid_battery_cfg", "terminal_target_wh": 99999.0}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": _FakeForecastBundle(tag="b1"),
            "_real_station_state_ref": real_state,
        }
        adapter.optimize(state={}, forecast=forecast, controller_settings=None)

        self.assertEqual(gap19.call_count, 1)
        self.assertEqual(gap19.last_configs["terminal_target_wh"], 99999.0, "explicit config value must be preserved")
        self.assertEqual(origin_cfg["terminal_target_wh"], 99999.0)


class TestRecedingHorizonPhysicalFuelAccumulation(unittest.TestCase):
    """
    Deterministic regression test: In receding-horizon mode, generator ON
    for hours 0-3 at 10,000 W, then OFF for hours 4-23.
    Under physical fuel formula (5.0 * (P>0) + 0.00025 * P) * 1.0 h:
      Hours 0-3: (5.0 + 0.00025 * 10000.0) * 1.0 = 7.5 L/hr * 4 hr = 30.0 L.
      Hours 4-23: 0.0 L/hr * 20 hr = 0.0 L.
    Expected 24-hour total is 30.0 L, even though the final step (hour 23) consumes 0.0 L.
    Verifies that execute_origin_dispatch_cell reports 30.0 L in OriginRunResult.diesel_consumed_liters.
    Also verifies fail-closed handling when intermediate or initial fuel observations are missing.
    """

    def _execute_run(self, missing_step_indices=None, initial_fuel=500.0):
        class _PhysicalFuelSimulator:
            def __init__(self, base_fuel_lph=5.0, marginal_fuel_lpwh=0.00025, missing_steps=None):
                self.base_fuel_lph = base_fuel_lph
                self.marginal_fuel_lpwh = marginal_fuel_lpwh
                self.missing_steps = set(missing_steps) if missing_steps is not None else set()
                self.call_count = 0

            def step(self, station_state, one_hour_slice, actual_t):
                step_idx = self.call_count
                self.call_count += 1
                if step_idx in self.missing_steps or station_state.diesel_fuel_remaining_liters is None:
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

        class _SequencedDieselOptimizer:
            def __init__(self, diesel_powers):
                self._diesel_powers = list(diesel_powers)
                self.call_count = 0

            def optimize(self, bundle, station_state, configs):
                power = self._diesel_powers[self.call_count]
                self.call_count += 1
                return _make_plan(diesel_power_hour0=power, tag=f"step_{self.call_count}")

        origin = "origin-diesel-test"
        expected_steps = 24
        scenario = _build_scenario(origin)
        initial_state = _build_initial_state("diesel", soc=80.0, fuel=initial_fuel)

        engine = _FakeN6Engine()
        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": i} for i in range(expected_steps)]},
        )

        router = _FakeRouter(route_sequence=["NORMAL"] * expected_steps)
        router_adapter = N6RecedingHorizonRouterAdapter(router, configs_by_origin={origin: {}})

        # Generator ON for hours 0-3 (10,000 W), OFF for hours 4-23 (0 W)
        diesel_power_sequence = [10000.0] * 4 + [0.0] * 20
        sequenced_optimizer = _SequencedDieselOptimizer(diesel_power_sequence)
        option_d = _FakeOptionDSolver()
        optimizer_adapter = N6RecedingHorizonOptimizerAdapter(
            sequenced_optimizer, option_d, configs_by_origin={origin: {}}
        )

        simulator = _PhysicalFuelSimulator(missing_steps=missing_step_indices)
        simulator_adapter = RecedingHorizonPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 0.0}] * expected_steps},
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            router=router_adapter,
            provenance={"test": "receding_horizon_physical_fuel_accumulation"},
        )
        return result, simulator

    def test_physical_fuel_accumulation_24h_receding_horizon(self):
        result, simulator = self._execute_run()
        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, 24)
        self.assertEqual(simulator.call_count, 24)
        # 4 hours * 7.5 L = 30.0 L; hours 4-23 consume 0.0 L.
        # Outcome MUST report 30.0 L across all realized steps, not the final step's 0.0 L.
        self.assertEqual(result.diesel_consumed_liters, 30.0)

    def test_physical_fuel_accumulation_missing_intermediate_step_reports_none(self):
        result, simulator = self._execute_run(missing_step_indices={2})
        # Step 2 returned None for fuel -> tracking gap latched -> pre-call rejects step 3 and stops early
        self.assertEqual(result.run_status, OriginRunStatus.INCOMPLETE_RUN)
        self.assertEqual(result.completed_steps, 3)
        self.assertEqual(simulator.call_count, 3)
        self.assertTrue(result.has_fuel_failure)
        self.assertIsNone(result.diesel_consumed_liters)

    def test_physical_fuel_accumulation_missing_first_step_reports_none(self):
        result, simulator = self._execute_run(initial_fuel=None)
        # Step 0 initial fuel is None -> pre-call fuel check rejects immediately without calling simulator
        self.assertEqual(result.run_status, OriginRunStatus.INCOMPLETE_RUN)
        self.assertEqual(result.completed_steps, 1)
        self.assertEqual(simulator.call_count, 0)
        self.assertTrue(result.has_fuel_failure)
        self.assertIsNone(result.diesel_consumed_liters)


class TestRecedingHorizonPolicyBReserveIntegration(unittest.TestCase):
    """
    Validates Policy B reserve integration with N6RecedingHorizonOptimizerAdapter
    per POLARIS Master Decision Register Section 4 item 7 and Gemini review conditions.
    """

    def _build_test_bundle(self, crit_pt=None, conformal_ebr=None, source="CANDIDATE_N6_25ADD_15KT_SPECIALIST"):
        class _Bundle:
            def __init__(self):
                self.demand = _FakeTimeseries([5000.0] * 24)
                self.demand_critical = _FakeTimeseries(crit_pt) if crit_pt is not None else None
                self.solar_irradiance = _FakeTimeseries([100.0] * 24)
                self.metadata = {
                    "SOLAR_FORECAST_SOURCE": source,
                    "ebr_target_wh": conformal_ebr if conformal_ebr is not None else [15000.0] * 24,
                }
        return _Bundle()

    def test_receding_horizon_policy_b_pointwise_max_on_normal_route(self):
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-pol-b"
        origin_cfg = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0, "discharge_efficiency": 0.92},
            "critical_demand_w": [1000.0] * 24,
        }
        configs_by_origin = {origin: origin_cfg}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin=configs_by_origin)

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        # Conformal EBR = 25000 Wh > Critical reserve (6000 / 0.92 = 6521.74 Wh)
        bundle = self._build_test_bundle(crit_pt=[1000.0] * 24, conformal_ebr=[25000.0] * 24)
        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": bundle,
            "_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0),
        }

        adapter.optimize(state, forecast, controller_settings=None)
        self.assertEqual(gap19.call_count, 1)
        self.assertEqual(option_d.call_count, 0)
        # GAP19 receives both OD-01 terminal target AND Policy B combined reserve
        self.assertEqual(gap19.last_configs["terminal_target_wh"], 120000.0)
        self.assertEqual(gap19.last_configs["ebr_target_wh"][0], 25000.0)
        # Caller config remains unmutated
        self.assertNotIn("ebr_target_wh", origin_cfg)

    def test_receding_horizon_policy_b_bypassed_on_emergency_route(self):
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-emergency"
        origin_cfg = {"battery": {"capacity_wh": 200000.0}}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        bundle = self._build_test_bundle(crit_pt=[1000.0] * 24, conformal_ebr=[25000.0] * 24)
        forecast = {
            "origin": origin,
            "route": "EMERGENCY",
            "_real_bundle_ref": bundle,
            "_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0),
            "_real_assessment_ref": {"emergency": True},
        }

        adapter.optimize(state, forecast, controller_settings=None)
        self.assertEqual(gap19.call_count, 0)
        self.assertEqual(option_d.call_count, 1)

    def test_receding_horizon_policy_b_missing_ebr_fails_closed(self):
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-fail-ebr"
        origin_cfg = {"critical_demand_w": [1000.0] * 24}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        bundle = self._build_test_bundle(crit_pt=[1000.0] * 24, conformal_ebr=None)
        bundle.metadata.pop("ebr_target_wh", None)
        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": bundle,
            "_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0),
        }

        with self.assertRaises(ValueError) as ctx:
            adapter.optimize(state, forecast, controller_settings=None)
        self.assertIn("requires conformal 'ebr_target_wh'", str(ctx.exception))

    def test_receding_horizon_non_n6_preserves_native_behavior(self):
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-base"
        origin_cfg = {"battery": {"capacity_wh": 200000.0}}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0)}
        base_bundle = self._build_test_bundle(source="LocalBaselineForecastEngine", conformal_ebr=None)
        base_bundle.metadata.pop("ebr_target_wh", None)
        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": base_bundle,
            "_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0),
        }

        adapter.optimize(state, forecast, controller_settings=None)
        self.assertEqual(gap19.call_count, 1)
        self.assertNotIn("ebr_target_wh", gap19.last_configs)

    def test_receding_horizon_caller_config_immutability_per_step(self):
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-immutability"
        origin_cfg = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0, "discharge_efficiency": 0.92},
            "critical_demand_w": [1000.0] * 24,
        }
        configs_by_origin = {origin: origin_cfg}
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin=configs_by_origin)

        state = {"_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)}
        bundle = self._build_test_bundle(crit_pt=[1000.0] * 24, conformal_ebr=[25000.0] * 24)
        forecast = {
            "origin": origin,
            "route": "NORMAL",
            "_real_bundle_ref": bundle,
            "_real_station_state_ref": _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0),
        }

        # Step 0
        adapter.optimize(state, forecast, controller_settings=None)
        self.assertNotIn("ebr_target_wh", origin_cfg)
        self.assertNotIn("terminal_target_wh", origin_cfg)

        # Step 1 with changed battery state
        state_step1 = {"_real_station_state_ref": _FakeStationState("t1", 50.0, 480.0, battery_energy_wh=100000.0)}
        forecast_step1 = dict(forecast)
        forecast_step1["_real_station_state_ref"] = _FakeStationState("t1", 50.0, 480.0, battery_energy_wh=100000.0)

        adapter.optimize(state_step1, forecast_step1, controller_settings=None)
        self.assertEqual(gap19.call_count, 2)
        # Step 1 terminal target recalculated dynamically to 100000 - 40000 = 60000 Wh
        self.assertEqual(gap19.last_configs["terminal_target_wh"], 60000.0)
        self.assertEqual(gap19.last_configs["ebr_target_wh"][0], 25000.0)
        self.assertNotIn("ebr_target_wh", origin_cfg)
        self.assertNotIn("terminal_target_wh", origin_cfg)


class TestN6RecedingHorizonOD02Alignment(unittest.TestCase):
    def test_od02_receding_horizon_forecast_adapter_shifts_solar(self):
        """
        N6RecedingHorizonForecastAdapter.predict:
          - Forecast row 1 becomes step view solar irradiance for hour 0 (the immediate next hour).
          - Attached _real_bundle_ref has solar rows 1..23 mapped to 0..22 and step 23 has 0.0 fallback.
          - Demand and EBR reserve targets remain unshifted.
        """
        origin = "rh-od02"
        raw_solar = [float(10.0 * i) for i in range(24)]  # [0, 10, 20, ..., 230]
        raw_demand = [4500.0 + i * 10 for i in range(24)]
        raw_ebr = [15000.0] * 24

        class _OD02Engine:
            def __init__(self):
                self.predict_call_count = 0
            def predict(self, state, context):
                self.predict_call_count += 1
                bundle = _FakeForecastBundle(tag=f"bundle_{self.predict_call_count}")
                bundle.solar_irradiance = _FakeTimeseries(list(raw_solar))
                bundle.demand = _FakeTimeseries(list(raw_demand))
                bundle.demand_critical = _FakeTimeseries([1000.0] * 24)
                bundle.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }
                return bundle

        engine = _OD02Engine()
        adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}, {"step": 1}]},
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state

        # Call predict for step 0
        view = adapter.predict(origin, 0, {"state": state_dict})

        # Step view at hour 0 sees raw row 1 (10.0 W/m^2)
        self.assertEqual(view["solar_irradiance_point"], 10.0)
        # Demand and EBR in step view remain unshifted
        self.assertEqual(view["demand_point"], raw_demand[0])
        self.assertEqual(view["ebr_target_wh"], raw_ebr)

        # Attached _real_bundle_ref is aligned for 24 hours
        bundle_ref = view["_real_bundle_ref"]
        self.assertEqual(bundle_ref.solar_irradiance.point[0], 10.0)
        self.assertEqual(bundle_ref.solar_irradiance.point[22], 230.0)
        self.assertEqual(bundle_ref.solar_irradiance.point[23], 0.0)  # Step 23 OD-02 fallback
        self.assertEqual(bundle_ref.demand.point, raw_demand)
        self.assertEqual(bundle_ref.metadata["ebr_target_wh"], raw_ebr)
        self.assertTrue(bundle_ref.metadata["od02_time_aligned"])

    def test_od02_receding_horizon_optimizer_receives_aligned_bundle_and_preserves_policy_b(self):
        """
        N6RecedingHorizonOptimizerAdapter receives the OD-02 aligned bundle from
        the forecast view and passes it to GAP19 with Policy B and OD-01 intact.
        """
        gap19 = _FakeGAP19Optimizer()
        option_d = _FakeOptionDSolver()
        origin = "rh-opt-od02"
        origin_cfg = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0, "discharge_efficiency": 0.92},
            "critical_demand_w": [1000.0] * 24,
        }
        adapter = N6RecedingHorizonOptimizerAdapter(gap19, option_d, configs_by_origin={origin: origin_cfg})

        raw_solar_gen = [float(50.0 * i) for i in range(24)]
        raw_solar_irr = [float(10.0 * i) for i in range(24)]
        raw_demand = [5000.0] * 24
        raw_ebr = [20000.0] * 24

        class _OD02Engine:
            def predict(self, state, context):
                bundle = _FakeForecastBundle(tag="od02_bundle")
                bundle.solar_irradiance = _FakeTimeseries(list(raw_solar_irr))
                bundle.solar_generation = _FakeTimeseries(list(raw_solar_gen))
                bundle.demand = _FakeTimeseries(list(raw_demand))
                bundle.demand_critical = _FakeTimeseries([1000.0] * 24)
                bundle.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }
                return bundle

        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=_OD02Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}]},
        )
        real_state = _FakeStationState("t0", 80.0, 500.0, battery_energy_wh=160000.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state

        forecast = forecast_adapter.predict(origin, 0, {"state": state_dict})
        forecast["route"] = "NORMAL"

        res = adapter.optimize(state_dict, forecast, None)
        self.assertEqual(res["route"], "NORMAL")
        self.assertEqual(gap19.call_count, 1)

        # Received bundle is aligned
        passed_bundle = gap19.last_bundle
        self.assertEqual(passed_bundle.solar_generation.point[0], 50.0)
        self.assertEqual(passed_bundle.solar_generation.point[22], 1150.0)
        self.assertEqual(passed_bundle.solar_generation.point[23], 0.0)
        self.assertEqual(passed_bundle.demand.point, raw_demand)

        # Policy B and OD-01 remain fully applied
        passed_cfg = gap19.last_configs
        self.assertEqual(passed_cfg["terminal_target_wh"], 120000.0)
        self.assertEqual(passed_cfg["ebr_target_wh"][0], 20000.0)

    def test_od02_receding_horizon_multi_step_alignment_integrity(self):
        """
        Verify across multiple receding-horizon steps that each step independently
        receives its aligned forecast (row 1 of its fresh prediction) and step 23
        fallback is preserved.
        """
        origin = "rh-multi-step"
        step_solar = [
            [float(10.0 * (i + step * 10)) for i in range(24)]
            for step in range(3)
        ]

        class _StepWiseEngine:
            def __init__(self):
                self.calls = 0
            def predict(self, state, context):
                idx = self.calls
                self.calls += 1
                b = _FakeForecastBundle(tag=f"step_{idx}")
                b.solar_irradiance = _FakeTimeseries(list(step_solar[idx]))
                b.demand = _FakeTimeseries([5000.0] * 24)
                b.metadata = {"ebr_target_wh": [15000.0] * 24}
                return b

        forecast_adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=_StepWiseEngine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}, {"step": 1}, {"step": 2}]},
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)

        for step in range(3):
            view = forecast_adapter.predict(origin, step, {"state": state_dict})
            # Step view gets index 0 of aligned bundle, which is raw index 1 of this step's forecast
            expected_val = step_solar[step][1]
            self.assertEqual(view["solar_irradiance_point"], expected_val)
            # Step 23 fallback is strictly 0.0 in every step's bundle
            self.assertEqual(view["_real_bundle_ref"].solar_irradiance.point[23], 0.0)

    def test_od02_receding_horizon_forecast_adapter_computes_c2_clearsky_ratio_polar_day(self):
        """
        Under polar day origin with valid ISO timestamp, N6RecedingHorizonForecastAdapter
        computes Candidate C.2 Clear-Sky Ratio for step 23 instead of 0.0 padding.
        """
        origin = "2024-06-01T00:00:00Z"
        raw_solar = [float(10.0 * i) for i in range(24)]
        raw_demand = [4500.0 + i * 10 for i in range(24)]
        raw_ebr = [15000.0] * 24

        class _OD02Engine:
            def predict(self, state, context):
                bundle = _FakeForecastBundle(tag="polar_day_bundle")
                bundle.solar_irradiance = _FakeTimeseries(list(raw_solar))
                bundle.demand = _FakeTimeseries(list(raw_demand))
                bundle.demand_critical = _FakeTimeseries([1000.0] * 24)
                bundle.metadata = {
                    "ebr_target_wh": list(raw_ebr),
                    "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
                }
                return bundle

        adapter = N6RecedingHorizonForecastAdapter(
            real_forecast_engine=_OD02Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin_and_step={origin: [{"step": 0}]},
        )
        real_state = _FakeStationState("t0", 80.0, 500.0)
        state_dict = StationStateCodec.to_plain_dict(real_state)
        state_dict["_real_station_state_ref"] = real_state

        view = adapter.predict(origin, 0, {"state": state_dict})
        bundle_ref = view["_real_bundle_ref"]

        # Step 23 receives non-zero C.2 clear-sky ratio value (~1.55864 W/m^2)
        expected_cs = 1.5586416106335632
        self.assertAlmostEqual(bundle_ref.solar_irradiance.point[23], expected_cs, places=5)
        self.assertTrue(bundle_ref.metadata["od02_time_aligned"])


if __name__ == "__main__":
    unittest.main()
