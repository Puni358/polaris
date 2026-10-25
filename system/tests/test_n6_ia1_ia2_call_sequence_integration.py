"""
POLARIS -- IA-1 / IA-2 Design Resolution: End-to-End Call-Sequence Lock-In Tests
=====================================================================================
Companion to `forecasting/reports/other/IA1_IA2_DESIGN_RESOLUTION_REPORT.md`. Resolves the directive's
"Tests and integrity" requirement: fake-based tests that lock in the
DOCUMENTED call-sequence assumptions for IA-1 (single-shot-plan-then-slice,
not receding-horizon) and IA-2 (router folded into the optimizer adapter),
exercised through the REAL, UNMODIFIED `execute_origin_dispatch_cell` loop in
`system/evaluation/n6_multi_origin_harness/harness.py` and the REAL,
UNMODIFIED adapter classes in
`system/evaluation/n6_multi_origin_harness/adapters.py` -- neither file is
edited by this test or by the pass that added it.

GOVERNANCE STATUS: NON-PRODUCTION / NOT EXECUTED / NO NEW EXECUTION PATH
-------------------------------------------------------------------------
- Every forecast engine / router / optimizer / simulator / safety-evaluator
  object used below is a small hand-written Fake local to this file. Nothing
  here imports, constructs, or calls a real `N6SolarForecastEngine`,
  `EMSControlRouter`, `GAP19HighsNativeOptimizer`, `DigitalTwinSimulator`, or
  `reserve_policy_guard.evaluate_dispatch_safety`.
- `execute_origin_dispatch_cell` is called directly (as
  `test_n6_multi_origin_harness.py` already does), never through
  `MultiOriginCampaignHarness.execute_campaign` -- the unconditional
  `CampaignExecutionNotAuthorizedError` gate is untouched and not exercised
  here.
- No sealed/blind-partition path, frozen model artifact, or real dataset is
  read.

WHAT THIS FILE ADDS BEYOND `test_n6_multi_origin_harness_adapters.py`
-------------------------------------------------------------------------
The existing adapter test suite validates each adapter class in isolation.
Wiring all four (now five, with the router) together through the actual
`execute_origin_dispatch_cell` loop (this file's contribution) surfaces
interface gaps beyond the four `IntegrationAssumption`s (`IA-1`..`IA-4`)
documented in `adapters.py`.

**UPDATED THIS PASS (forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md):** the owner decided
IA-1 (use receding-horizon as the production-representative comparison) and
IA-2 (add a fifth `RouterProtocol` + an explicit `OriginRunResult.route`
field) this pass. As part of IA-2's implementation, `harness.py`'s
`execute_origin_dispatch_cell` loop now threads its own already-tracked
`state` dict into the `context` passed to `forecast_provider.predict` (under
a `"state"` key) every step -- this is the EXACT mechanical gap
`TestRawWiringSurfacesStateGap` below used to lock in as a fail-closed
`KeyError`. That mechanical gap is now CLOSED: wiring the real,
unshimmed `N6ForecastProviderAdapter` directly into the loop now succeeds,
because the loop itself supplies the state the adapter needs, using
precisely the simulated state the loop already owns (seeded from
`initial_state`, advanced by `simulator.step` every iteration) -- no new
value is invented to make this work.

This is a MECHANICAL/plumbing fix only. It does NOT close the deeper,
still-open evidence gap: `initial_state` itself must still come from an
authoritative, cited per-origin source, and no such source exists anywhere
in this repository for a real multi-origin N6 comparison (IA-3, unchanged,
confirmed absent again this pass by repository-wide search -- see
`forecasting/n6/reports/N6_IA1_IA2_REMEDIATION_REPORT.md` Section 5 / Blocker B). `TestRawWiringSurfacesStateGap`
below is UPDATED, not deleted, to lock in the NEW correct behavior (the
mechanical gap is closed) and a NEW test
(`TestMalformedOrMissingAuthoritativeStateStillFailsClosed`) locks in that a
malformed or incomplete `initial_state` -- i.e. the evidence gap, as opposed
to the plumbing gap -- still fails closed with a `KeyError`, never a
zero-filled/guessed substitute.

    `TestFullChainWithTestOnlyStateShim` below still uses the small, clearly
    -labeled TEST-ONLY shim (not a change to `adapters.py` or `harness.py`)
    from the prior pass. It is NOW REDUNDANT (the loop supplies `"state"`
    itself), but kept because it is harmless (it overwrites `"state"` with
    the exact same value the loop already put there) and because
    `test_22b_full_chain_without_shim_also_holds` directly demonstrates the
    redundancy, proving the shim is no longer load-bearing. Confirms the
    full real call-sequence assumption holds end-to-end: the forecast
    engine, router, and optimizer are each called EXACTLY ONCE per origin,
    and the simulator is stepped once per hour -- i.e. single-shot-then
    -slice, not receding-horizon, for THIS specific adapter wiring (the
    separate receding-horizon adapters this pass also adds are tested in
    `system/tests/test_n6_receding_horizon_adapters.py`), and the router
    folded into the optimizer adapter's upstream `RoutedOptimizerAdapter`
    call, not routed through the new `RouterProtocol` slot (that slot is
    exercised by the receding-horizon adapters instead, in the new file
    above).

    `TestSafetyEvidenceStaysUnknownThroughThisWiring` documents a related,
    smaller consequence: `DispatchOutcomeView.at_hour`'s returned dict never
    carries a `"_real_plan_dict"` key, so `ReservePolicyGuardSafetyEvaluatorAdapter`
    always returns `None` or (through this exact chain) leaves safety
    evidence `UNKNOWN_NOT_VERIFIED` -- consistent with the repository's
    existing "missing evidence is never a pass" rule, not a new bug, but
    relevant to IA-2's "effects on result provenance" question.
"""
from __future__ import annotations

import unittest

from system.evaluation.n6_multi_origin_harness.adapters import (
    N6ForecastProviderAdapter,
    ReservePolicyGuardSafetyEvaluatorAdapter,
    RoutedOptimizerAdapter,
    SingleShotPlanSlicingSimulatorAdapter,
    StationStateCodec,
)
from system.evaluation.n6_multi_origin_harness.harness import (
    SAFETY_EVIDENCE_UNKNOWN,
    OriginRunStatus,
    execute_origin_dispatch_cell,
)
from system.evaluation.replay_harness import MatchedControllerSettings, ScenarioSpec


# ---------------------------------------------------------------------------
# Fakes mirroring the REAL classes' shapes (never the real classes themselves).
# Deliberately duplicated, small, and local to this file rather than imported
# from test_n6_multi_origin_harness_adapters.py, so this file stays
# self-contained and does not couple two test modules together.
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
        # indexing (KeyError on a missing required field), confirmed by
        # direct read of system/schemas/station_state.py this pass.
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
    def __init__(self):
        self.solar_irradiance = _FakeTimeseries([100.0] * 24)
        self.demand = _FakeTimeseries([5000.0] * 24)
        self.metadata = {"ebr_target_wh": [15000.0] * 24}


class _FakeN6Engine:
    def __init__(self):
        self.predict_call_count = 0

    def predict(self, station_state, context):
        self.predict_call_count += 1
        assert "n6_feature_matrix" in context
        return _FakeForecastBundle()


class _FakeRouter:
    def __init__(self, route="NORMAL"):
        self._route = route
        self.call_count = 0

    def evaluate_and_route(self, station_state, bundle, configs):
        self.call_count += 1
        return ({"ok": True}, self._route)


class _FakeDispatchPlan:
    def __init__(self, schema_version, timestamps, solar_used, wind_used, battery_charge, battery_discharge,
                 battery_soc, diesel_power, load_served, flexible_load_schedule, renewable_curtailment,
                 unmet_load, objective_value, constraint_status, energy_balance_errors, unmet_essential=None):
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
    def __init__(self):
        self.call_count = 0
        self.last_configs = None
        self.seen_configs = []

    def optimize(self, bundle, station_state, configs):
        self.call_count += 1
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
            unmet_essential=[0.0] * 24,
        )


class _FakeDigitalTwinSimulator:
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
    return {"passed": True}


class _StatePassingForecastShim:
    """
    TEST-ONLY. Not part of `adapters.py` or `harness.py`, and not a proposed
    production fix. Bridges the gap documented above (`context` carries no
    `"state"` key) by supplying the one, fixed, pre-loop-known initial
    station-state dict that `N6ForecastProviderAdapter` needs on its first
    (and only, since it caches) call per origin. Its existence is evidence
    that this gap needs a real decision (thread `state` through the
    `ForecastProviderProtocol.predict` call, or source it another way)
    before `N6ForecastProviderAdapter` is wired into
    `execute_origin_dispatch_cell` for real -- see
    `forecasting/reports/other/IA1_IA2_DESIGN_RESOLUTION_REPORT.md`.
    """

    def __init__(self, inner: N6ForecastProviderAdapter, initial_state_plain_dict):
        self._inner = inner
        self._initial_state_plain_dict = initial_state_plain_dict

    def predict(self, origin, step_index, context):
        enriched_context = dict(context)
        enriched_context["state"] = self._initial_state_plain_dict
        return self._inner.predict(origin, step_index, enriched_context)


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
    # "n6_solar" is CAUSAL_PROVIDER_NAMES-classified (forecast_lineage.py),
    # confirmed this pass -- required so ScenarioSpec.__post_init__'s
    # reject_if_oracle call does not raise.
    return ScenarioSpec(
        scenario_key=origin,
        forecast_origin=origin,
        initial_battery_soc_wh=160000.0,
        controller_settings=settings,
        forecast_provider="n6_solar",
        reserve_policy_name="GOVERNED_DEFAULT_RESERVE_POLICY",
    )


def _build_initial_state():
    """Returns (initial_state_for_loop, initial_state_plain_dict_for_shim)."""
    real_state = _FakeStationState(
        timestamp="2024-06-01T00:00:00Z", battery_soc_pct=80.0, diesel_fuel_remaining_liters=500.0
    )
    plain = StationStateCodec.to_plain_dict(real_state)
    for_loop = dict(plain)
    for_loop["_real_station_state_ref"] = real_state
    for_loop["_step_index"] = 0
    return for_loop, plain


class TestRawWiringSurfacesStateGap(unittest.TestCase):
    """
    UPDATED THIS PASS. Used to lock in that wiring `N6ForecastProviderAdapter`
    into `execute_origin_dispatch_cell` with no test-only shim failed CLOSED
    at step 0, because the loop's `context` dict carried no `"state"` key.
    This pass's IA-2 implementation fixed that exact mechanical gap in
    `harness.py` (the loop now threads its own tracked `state` dict into
    `context["state"]` every step) -- so this test now locks in the OPPOSITE,
    CORRECT behavior: the raw, unshimmed adapter chain now succeeds, with no
    test-only bridge required.
    """

    def test_21_unshimmed_forecast_adapter_now_succeeds_state_gap_fixed(self):
        origin = "origin-1"
        scenario = _build_scenario(origin)
        initial_state, _ = _build_initial_state()

        engine = _FakeN6Engine()
        forecast_adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin: {"fake": "matrix"}},
        )
        optimizer_adapter = RoutedOptimizerAdapter(
            _FakeRouter(), _FakeGAP19Optimizer(), configs_by_origin={origin: {}}
        )
        simulator_adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * 4},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=4,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,  # unshimmed -- the mechanical gap is now fixed in harness.py
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            provenance={"test": "ia1_ia2_raw_wiring_gap_fixed"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, 4)
        self.assertEqual(
            engine.predict_call_count, 1,
            "real engine is called exactly once per origin now that the loop supplies 'state' itself",
        )


class TestMalformedOrMissingAuthoritativeStateStillFailsClosed(unittest.TestCase):
    """
    NEW THIS PASS. The mechanical plumbing gap (`context` carrying no
    `"state"` key) is fixed -- but that is NOT the same claim as "the
    StationState handoff is evidence-backed". `initial_state` itself must
    still be an authoritative, complete StationState for the origin; this
    harness still invents nothing to compensate for a bad or incomplete one.
    Locks in that a malformed/incomplete `initial_state` still fails CLOSED
    (a `KeyError` from the real `StationState.from_dict`-equivalent contract,
    never a zero-filled/guessed substitute), exactly as before this pass.
    """

    def test_24_missing_required_station_state_field_fails_closed(self):
        origin = "origin-1"
        scenario = _build_scenario(origin)
        # Deliberately missing "battery_soc_pct" -- a REQUIRED StationState
        # field (system/schemas/station_state.py's `from_dict` indexes it
        # directly, no `.get()` fallback) -- never defaulted by this adapter.
        incomplete_initial_state = {
            "timestamp": "2024-06-01T00:00:00Z",
            "diesel_fuel_remaining_liters": 500.0,
        }

        engine = _FakeN6Engine()
        forecast_adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin: {"fake": "matrix"}},
        )
        optimizer_adapter = RoutedOptimizerAdapter(
            _FakeRouter(), _FakeGAP19Optimizer(), configs_by_origin={origin: {}}
        )
        simulator_adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * 4},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=4,
            initial_state=incomplete_initial_state,
            forecast_provider=forecast_adapter,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=None,
            provenance={"test": "ia3_missing_authoritative_state_evidence"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.FAILED_OPTIMIZATION_EXCEPTION)
        self.assertEqual(result.completed_steps, 0)
        self.assertEqual(engine.predict_call_count, 0, "real engine must never be called with an incomplete state")
        self.assertTrue(
            any("KeyError" in reason for reason in result.failure_reasons),
            f"expected a fail-closed KeyError, got: {result.failure_reasons}",
        )


class TestFullChainWithTestOnlyStateShim(unittest.TestCase):
    """
    With the state-passing gap bridged by a clearly-labeled TEST-ONLY shim
    (never a production change), locks in the full, documented IA-1/IA-2
    call-sequence assumption end-to-end through the real, unmodified
    `execute_origin_dispatch_cell` loop: forecast engine, router, and
    optimizer each called EXACTLY ONCE per origin (single-shot, router
    folded into the optimizer adapter -- not a per-step receding-horizon
    replan), and the simulator stepped once per expected step.
    """

    def test_22_single_shot_call_counts_hold_end_to_end(self):
        origin = "origin-1"
        expected_steps = 4
        scenario = _build_scenario(origin)
        initial_state, initial_state_plain = _build_initial_state()

        engine = _FakeN6Engine()
        forecast_adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin: {"fake": "matrix"}},
        )
        shimmed_forecast_provider = _StatePassingForecastShim(forecast_adapter, initial_state_plain)

        router = _FakeRouter(route="NORMAL")
        optimizer = _FakeGAP19Optimizer()
        optimizer_adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={origin: {}})

        simulator = _FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5)
        simulator_adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        safety_adapter = ReservePolicyGuardSafetyEvaluatorAdapter(_fake_evaluate_dispatch_safety)

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=shimmed_forecast_provider,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=safety_adapter,
            provenance={"test": "ia1_ia2_full_chain"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, expected_steps)

        # IA-1: single-shot-then-slice, not receding-horizon.
        self.assertEqual(engine.predict_call_count, 1, "N6 forecast engine must be called once per origin")
        self.assertEqual(optimizer.call_count, 1, "GAP19 optimizer must be called once per origin, not per step")

        # IA-2: router folded into the optimizer adapter, called once (paired with the one optimize() call).
        self.assertEqual(router.call_count, 1, "router must be called once per origin, paired with the single optimize()")

        # The simulator, by contrast, genuinely steps once per hour -- this is the part of the
        # real sequence that IS per-step, confirming the test isn't just asserting "everything is 1".
        self.assertEqual(simulator.call_count, expected_steps)

    def test_22b_full_chain_without_shim_also_holds(self):
        """
        NEW THIS PASS. Identical to `test_22` above except the TEST-ONLY
        `_StatePassingForecastShim` is removed entirely -- `forecast_adapter`
        is wired directly into `execute_origin_dispatch_cell`. Proves the
        shim is no longer load-bearing: `harness.py`'s own state-threading
        fix is sufficient on its own.
        """
        origin = "origin-1"
        expected_steps = 4
        scenario = _build_scenario(origin)
        initial_state, _ = _build_initial_state()

        engine = _FakeN6Engine()
        forecast_adapter = N6ForecastProviderAdapter(
            real_forecast_engine=engine,
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin: {"fake": "matrix"}},
        )

        router = _FakeRouter(route="NORMAL")
        optimizer = _FakeGAP19Optimizer()
        optimizer_adapter = RoutedOptimizerAdapter(router, optimizer, configs_by_origin={origin: {}})

        simulator = _FakeDigitalTwinSimulator(fuel_burn_per_hour=0.5)
        simulator_adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=simulator,
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )

        safety_adapter = ReservePolicyGuardSafetyEvaluatorAdapter(_fake_evaluate_dispatch_safety)

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="candidate",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=forecast_adapter,  # no shim
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=safety_adapter,
            provenance={"test": "ia1_ia2_full_chain_no_shim"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.completed_steps, expected_steps)
        self.assertEqual(engine.predict_call_count, 1)
        self.assertEqual(optimizer.call_count, 1)
        self.assertEqual(router.call_count, 1)
        self.assertEqual(simulator.call_count, expected_steps)


class TestSafetyEvidenceStaysUnknownThroughThisWiring(unittest.TestCase):
    """
    Documents a smaller, related IA-2 "result provenance" consequence:
    `DispatchOutcomeView.at_hour`'s returned dict never carries a
    `"_real_plan_dict"` key, so safety evidence recorded by
    `record_origin_outcome` stays `UNKNOWN_NOT_VERIFIED` through this exact
    adapter chain even on a clean `OPTIMAL` run -- consistent with the
    repository's existing "missing evidence is never a pass" rule, not a
    new bug, but relevant to whether a future `RouterProtocol` split would
    change how/where real safety evidence gets attached.
    """

    def test_23_safety_evidence_unknown_even_on_clean_run(self):
        origin = "origin-1"
        expected_steps = 2
        scenario = _build_scenario(origin)
        initial_state, initial_state_plain = _build_initial_state()

        forecast_adapter = N6ForecastProviderAdapter(
            real_forecast_engine=_FakeN6Engine(),
            station_state_cls=_FakeStationState,
            feature_matrix_by_origin={origin: {"fake": "matrix"}},
        )
        shimmed_forecast_provider = _StatePassingForecastShim(forecast_adapter, initial_state_plain)
        optimizer_adapter = RoutedOptimizerAdapter(
            _FakeRouter(), _FakeGAP19Optimizer(), configs_by_origin={origin: {}}
        )
        simulator_adapter = SingleShotPlanSlicingSimulatorAdapter(
            real_simulator=_FakeDigitalTwinSimulator(),
            dispatch_plan_cls=_FakeDispatchPlan,
            actuals_by_origin_and_step={origin: [{"actual_SW_IN": 90.0}] * expected_steps},
            station_state_cls=_FakeStationState,
            _allow_synthetic_actuals_for_testing=True,
        )
        safety_adapter = ReservePolicyGuardSafetyEvaluatorAdapter(_fake_evaluate_dispatch_safety)

        result = execute_origin_dispatch_cell(
            origin=origin,
            arm="baseline",
            scenario=scenario,
            expected_steps=expected_steps,
            initial_state=initial_state,
            forecast_provider=shimmed_forecast_provider,
            optimizer=optimizer_adapter,
            simulator=simulator_adapter,
            safety_evaluator=safety_adapter,
            provenance={"test": "ia1_ia2_safety_evidence"},
        )

        self.assertEqual(result.run_status, OriginRunStatus.OPTIMAL)
        self.assertEqual(result.safety_evidence_status, SAFETY_EVIDENCE_UNKNOWN)
        self.assertIsNone(result.safety_passed)


if __name__ == "__main__":
    unittest.main()
