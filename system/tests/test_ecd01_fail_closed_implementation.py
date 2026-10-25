"""
POLARIS EMS -- ECD-01 Fail-Closed Implementation Regression Suite
====================================================================

Verifies the router.py/ecd.py implementation of the project owner's recorded
decisions (docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md, item ECD-01, decided
2026-10-18; full text in docs/decision_registers/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md Section 9):

  Decision A = A-iii: T_required fails closed (UNKNOWN_INVALID) unless an
    explicitly authorized, explicit numeric value is supplied. The ungoverned
    6.0h code default is removed; no numerical T_required is invented here.
  Decision B = B-iii: critical-load-for-routing fails closed (UNKNOWN_INVALID)
    unless authoritative, explicitly authorized real-station evidence is
    supplied. Observed total demand, bundle.demand.point[0], and the old
    hardcoded 30,000 W floor are no longer accepted as that evidence.
  Decision C = M-A: UNKNOWN_INVALID is returned as its own distinct route,
    never remapped to EMERGENCY, with no invented fallback and no silent use
    of stale/last-known-good values (no freshness policy is authorized).

Config contract introduced by this implementation (router.py), used by every
test below to distinguish AUTHORIZED from UNAUTHORIZED evidence, exactly as
the implementing directive requires:

  configs["ecd"] = {
      "t_required_hours": <float>,       # explicit numeric value
      "t_required_authorized": True,     # explicit authorization flag
  }
  configs["critical_load"] = {
      "authorized": True,                     # explicit authorization flag
      "evidence_id": "EVID-02",                # must be an EVID-xx real-station
                                                # evidence record, NOT a research-
                                                # scoped design value like "CL-01"
      "authorized_critical_load_w": <float>,   # explicit numeric value
  }

Absent, incomplete, or improperly-scoped authorization on EITHER input causes
the router to fail closed to UNKNOWN_INVALID -- this is the intended,
honestly-reportable behavior, not a defect.
"""

import math
import unittest

from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.control.ecd import OperatingMode, ValidityStatus
from system.control.router import EMSControlRouter


def _make_bundle(demand=20000.0, solar=0.0):
    timestamps = [f"2026-09-26T{h:02d}:00:00Z" for h in range(24)]
    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=timestamps[0],
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=TimeseriesForecast(point=[solar] * 24, lower=[solar] * 24, upper=[solar] * 24, unit="W/m^2"),
        solar_generation=TimeseriesForecast(point=[solar] * 24, lower=[solar] * 24, upper=[solar] * 24, unit="W"),
        wind_generation=TimeseriesForecast(point=[0.0] * 24, lower=[0.0] * 24, upper=[0.0] * 24, unit="W"),
        demand=TimeseriesForecast(point=[demand] * 24, lower=[demand] * 24, upper=[demand] * 24, unit="W"),
        metadata={"source": "ecd01_fail_closed_test"},
    )


def _make_state(soc_pct=80.0, fuel_l=100.0, demand_w=20000.0):
    return StationState(
        timestamp="2026-09-26T00:00:00Z",
        battery_soc_pct=soc_pct,
        battery_energy_wh=160000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=demand_w,
        last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=fuel_l,
    )


# Explicitly authorized, EVID-02-sourced evidence used by the "legitimate
# path" tests. 10,000 W is picked only so NORMAL and EMERGENCY are both
# reachable by varying SOC/fuel -- it is NOT a claim about any real-station
# value (T_required real-station value remains NOT_ESTABLISHED).
AUTHORIZED_ECD_CFG = {"t_required_hours": 2.0, "t_required_authorized": True}
AUTHORIZED_CRITICAL_LOAD_CFG = {
    "authorized": True,
    "evidence_id": "EVID-02",
    "authorized_critical_load_w": 10000.0,
}

BASE_CONFIGS = {
    "battery": {
        "capacity_wh": 200000.0,
        "min_soc_pct": 20.0,
        "max_soc_pct": 95.0,
        "discharge_efficiency": 0.92,
        "max_discharge_power_w": 50000.0,
    },
    "diesel": {
        "base_fuel_consumption_l_per_h": 5.0,
        "marginal_fuel_consumption_l_per_wh": 0.00025,
        "initial_fuel_l": 100.0,
        "min_power_w": 10000.0,
        "max_power_w": 50000.0,
        "physical_startup_fuel_l": 0.0,
    },
}


def _configs(ecd_cfg=None, critical_load_cfg=None, extra=None):
    cfg = dict(BASE_CONFIGS)
    cfg["battery"] = dict(BASE_CONFIGS["battery"])
    cfg["diesel"] = dict(BASE_CONFIGS["diesel"])
    if ecd_cfg is not None:
        cfg["ecd"] = dict(ecd_cfg)
    if critical_load_cfg is not None:
        cfg["critical_load"] = dict(critical_load_cfg)
    if extra:
        cfg.update(extra)
    return cfg


class TestDecisionATRequiredFailClosed(unittest.TestCase):
    """Decision A = A-iii."""

    def test_1_missing_t_required_fails_closed(self):
        """Required test 1: no configs['ecd'] at all -> UNKNOWN_INVALID."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        configs = _configs(ecd_cfg=None, critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.operating_mode, OperatingMode.UNKNOWN_INVALID)

    def test_1b_present_but_unauthorized_t_required_fails_closed(self):
        """A numeric value present without the authorization flag is still unauthorized."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        configs = _configs(
            ecd_cfg={"t_required_hours": 6.0},  # no t_required_authorized flag
            critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG,
        )
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.validity_status, ValidityStatus.UNAUTHORIZED_T_REQUIRED)

    def test_2_invalid_nonfinite_nonpositive_t_required_fails_closed(self):
        """Required test 2: authorized but malformed numeric T_required fails closed."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()

        for bad_value in (0.0, -5.0, float("nan"), float("inf")):
            configs = _configs(
                ecd_cfg={"t_required_hours": bad_value, "t_required_authorized": True},
                critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG,
            )
            assessment, route = router.evaluate_and_route(state, bundle, configs)
            self.assertEqual(route, "UNKNOWN_INVALID", f"t_required_hours={bad_value} must fail closed")
            self.assertEqual(assessment.operating_mode, OperatingMode.UNKNOWN_INVALID)

    def test_72h_prototype_value_not_silently_promoted(self):
        """The 72h prototype value is not implementation-authorized; this router does
        not promote it on its own -- it only behaves as any other explicitly
        authorized numeric value would (fail-closed rules apply equally)."""
        router = EMSControlRouter()
        # Authorized, deep-discharge/low-fuel state: with a 72h bar, both
        # battery-only and diesel-only endurance are far short -> EMERGENCY,
        # not a silently "easier" NORMAL outcome.
        state = _make_state(soc_pct=80.0, fuel_l=100.0)
        bundle = _make_bundle(demand=10000.0)
        configs = _configs(
            ecd_cfg={"t_required_hours": 72.0, "t_required_authorized": True},
            critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG,
        )
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(assessment.validity_status, ValidityStatus.VALID)
        self.assertEqual(route, "EMERGENCY")


class TestDecisionBCriticalLoadFailClosed(unittest.TestCase):
    """Decision B = B-iii."""

    def test_4_missing_critical_load_evidence_fails_closed(self):
        """Required test 4: configs['critical_load'] absent -> UNKNOWN_INVALID."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=None)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.validity_status, ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION)

    def test_5a_observed_total_demand_not_accepted_as_authoritative(self):
        """Required test 5: a large, positive last_observed_demand must NOT leak into
        routing as critical-load evidence just because it is available and finite."""
        router = EMSControlRouter()
        # last_observed_demand is deliberately large & positive -- under the
        # pre-fix substitution chain this alone would have produced a valid
        # (non-fail-closed) critical_load_w. It must now be irrelevant.
        state = _make_state(demand_w=999999.0)
        bundle = _make_bundle(demand=999999.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=None)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.validity_status, ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION)

    def test_5b_hardcoded_30kw_default_not_accepted_as_authoritative(self):
        """Required test 5 (continued): the old 30,000 W synthetic floor is gone --
        even a station state that previously would have hit that floor
        (zero/non-positive observed demand) must fail closed, not default to 30 kW."""
        router = EMSControlRouter()
        state = _make_state(demand_w=0.0)
        bundle = _make_bundle(demand=0.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=None)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.operating_mode, OperatingMode.UNKNOWN_INVALID)  # sanity: didn't crash
        self.assertEqual(assessment.validity_status, ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION)

    def test_6_synthetic_cli_input_does_not_become_authoritative(self):
        """Required test 6: the synthetic CLI's critical-load input is fed to
        GAP19 via configs['critical_demand_w'] (a separate, documented optimizer
        input slot) -- supplying that key must have NO effect on routing, which
        remains fail-closed absent configs['critical_load'] authorization."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        configs = _configs(
            ecd_cfg=AUTHORIZED_ECD_CFG,
            critical_load_cfg=None,
            extra={"critical_demand_w": [11600.0] * 24},  # synthetic CLI's slot
        )
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.validity_status, ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION)

    def test_research_scoped_cl01_evidence_id_rejected(self):
        """CL-01's decision record is scoped 'research', not 'safety_enforcement' --
        citing it as the evidence_id must not satisfy the authorization check."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        configs = _configs(
            ecd_cfg=AUTHORIZED_ECD_CFG,
            critical_load_cfg={
                "authorized": True,
                "evidence_id": "CL-01",  # research-scoped design value, not EVID-xx
                "authorized_critical_load_w": 11600.0,
            },
        )
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertEqual(assessment.validity_status, ValidityStatus.MISSING_CRITICAL_LOAD_AUTHORIZATION)

    def test_invalid_authorized_critical_load_value_fails_closed(self):
        """Authorized + correctly-scoped evidence, but a malformed numeric value,
        still fails closed via ECD's own numeric validation (not a crash, not a
        silent substitution)."""
        router = EMSControlRouter()
        state = _make_state()
        bundle = _make_bundle()
        for bad_value in (0.0, -1.0, float("nan")):
            configs = _configs(
                ecd_cfg=AUTHORIZED_ECD_CFG,
                critical_load_cfg={
                    "authorized": True,
                    "evidence_id": "EVID-02",
                    "authorized_critical_load_w": bad_value,
                },
            )
            assessment, route = router.evaluate_and_route(state, bundle, configs)
            self.assertEqual(route, "UNKNOWN_INVALID")
            self.assertEqual(assessment.validity_status, ValidityStatus.INVALID_CRITICAL_LOAD)


class TestDecisionCUnknownInvalidDistinctFromEmergency(unittest.TestCase):
    """Decision C = M-A."""

    def test_7_unknown_invalid_distinguishable_from_emergency_no_optimizer(self):
        """Required test 7: UNKNOWN_INVALID is never EMERGENCY, and the route
        value itself is what callers (e.g. runner.py) must use to avoid invoking
        any optimizer -- confirmed here on a station state that WOULD have
        classified EMERGENCY under the pre-fix substitution chain (low SOC, low
        fuel), proving fail-closed takes precedence over a plausible-looking
        emergency classification when inputs are unauthorized."""
        router = EMSControlRouter()
        state = _make_state(soc_pct=20.0, fuel_l=2.0)  # would be EMERGENCY if authorized
        bundle = _make_bundle(demand=40000.0)
        configs = _configs(ecd_cfg=None, critical_load_cfg=None)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "UNKNOWN_INVALID")
        self.assertNotEqual(route, "EMERGENCY")
        self.assertNotEqual(assessment.operating_mode, OperatingMode.EMERGENCY)
        self.assertEqual(assessment.validity_status, ValidityStatus.UNAUTHORIZED_T_REQUIRED)

    def test_runner_does_not_dispatch_or_advance_twin_on_unknown_invalid(self):
        """UNKNOWN_INVALID, as produced by this implementation, propagates through
        system/runtime/runner.py (read-only; not edited by this pass) exactly as
        its existing, unmodified code already does for any UNKNOWN_INVALID route:
        FAILED_TERMINATED, no optimizer invoked, no simulator step taken."""
        from pathlib import Path
        from system.runtime.runner import PolarisLocalRunner

        base_dir = Path(__file__).resolve().parent.parent
        runner = PolarisLocalRunner(
            system_dir=base_dir,
            scenario_filename="demo_scenario.json",
            optimizer_type="highs_native",
        )
        # No configs["ecd"] / configs["critical_load"] authorization supplied
        # anywhere -- this is runner.py's real, unmodified default state today.
        simulator_called = False

        def mock_step(s, p, a):
            nonlocal simulator_called
            simulator_called = True
            return s

        runner.simulator.step = mock_step
        report = runner.run_pipeline(steps_to_run=3)

        self.assertFalse(simulator_called, "DigitalTwin.step MUST NOT be called on UNKNOWN_INVALID")
        self.assertEqual(report["completed_steps"], 0)
        self.assertEqual(report["execution_status"], "FAILED_TERMINATED")
        self.assertIn("UNKNOWN_INVALID", "".join(report["fault_classes"]) + str(report["termination_reason"]))


class TestLegitimateNormalEmergencyPathsPreserved(unittest.TestCase):
    """Required test 3 and 8: with explicit, correctly-scoped authorization on
    both inputs, NORMAL and EMERGENCY classification work exactly as the
    underlying ECD margin math (unchanged) always specified."""

    def test_3_valid_authorized_t_required_normal_classification(self):
        router = EMSControlRouter()
        state = _make_state(soc_pct=80.0, fuel_l=100.0)
        bundle = _make_bundle(demand=5000.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(assessment.validity_status, ValidityStatus.VALID)
        self.assertEqual(route, "NORMAL")
        self.assertEqual(assessment.operating_mode, OperatingMode.NORMAL)

    def test_8_valid_authorized_emergency_classification(self):
        router = EMSControlRouter()
        state = _make_state(soc_pct=20.0, fuel_l=2.0)
        bundle = _make_bundle(demand=40000.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(assessment.validity_status, ValidityStatus.VALID)
        self.assertEqual(route, "EMERGENCY")
        self.assertEqual(assessment.operating_mode, OperatingMode.EMERGENCY)

    def test_8b_emergency_dispatch_to_option_d_still_works(self):
        """Full chain: authorized EMERGENCY route still hands off to
        OptionDFallbackSolver exactly as before (router/ECD changes do not
        touch optimizer dispatch mechanics)."""
        from system.optimization.implementations.option_d import OptionDFallbackSolver

        router = EMSControlRouter()
        state = _make_state(soc_pct=20.0, fuel_l=2.0)
        bundle = _make_bundle(demand=40000.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG)
        assessment, route = router.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route, "EMERGENCY")

        solver = OptionDFallbackSolver()
        plan = solver.solve(assessment, bundle, state, configs)
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.diesel_power), 24)

    def test_determinism_under_repeated_evaluation(self):
        """Required test 9 (regression coverage): repeated evaluation with
        identical, fully-authorized inputs is deterministic."""
        router1 = EMSControlRouter()
        router2 = EMSControlRouter()
        state = _make_state(soc_pct=50.0, fuel_l=100.0)
        bundle = _make_bundle(demand=10000.0)
        configs = _configs(ecd_cfg=AUTHORIZED_ECD_CFG, critical_load_cfg=AUTHORIZED_CRITICAL_LOAD_CFG)

        ass1, route1 = router1.evaluate_and_route(state, bundle, configs)
        ass2, route2 = router2.evaluate_and_route(state, bundle, configs)
        self.assertEqual(route1, route2)
        self.assertEqual(ass1.operating_mode, ass2.operating_mode)
        self.assertEqual(ass1.validity_status, ass2.validity_status)


if __name__ == "__main__":
    unittest.main()
