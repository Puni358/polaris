"""
Regression / diagnostic tests produced by the 2026-10-17 owner-authorized
RT-01/RT-02 full-suite failure forensics pass (see
ems/reports/rt01_runtime_fixes/RT01_RT02_FAILURE_FORENSICS_REPORT.md at the repo root), extended 2026-10-18
by the end-to-end recovery continuation pass with a 4th mechanism (see
forecasting/n6/reports/N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md) found while tracing RT-01's
current (post option_d.py:88 fix) step-22 residual to its exact source.

These tests do NOT fix anything (no PROTECTED_FILES entry is edited by this
pass: system/control/router.py, system/control/ecd.py,
system/optimization/implementations/option_d.py, and
system/optimization/implementations/gap19_highs_native.py are all protected
and read-only in this pass). They exist to pin down, deterministically and in
isolation, the exact causal mechanisms the forensic investigation found, so a
future authorized protected-file change window has a precise, minimal
regression surface to fix against -- and so this characterization survives
independently of the full closed-loop pipeline.

Three mechanisms are pinned down here:

1. `EMSControlRouter.evaluate_and_route()` (system/control/router.py) feeds the
   FULL observed demand into the ECD survivability check as "critical_load"
   (its own comment: "Use current demand scalar as synthetic fixture") instead
   of the station's actual, much smaller critical-load design value (11.6 kW
   per loads.yaml / register item CL-01). Combined with the default
   `t_required_hours=6.0` ECD target and demo_scenario.json's battery/diesel
   sizing, this makes the battery's usable-energy survivability margin
   (`m_battery`) negative at essentially every timestep, so the router
   classifies the station as EMERGENCY and routes to `OptionDFallbackSolver`
   almost unconditionally for demo_scenario.json -- bypassing the intended
   NORMAL-route optimizer (`LocalMILPEnergyOptimizer` / GAP19) entirely.

2. `OptionDFallbackSolver.solve()` (system/optimization/implementations/
   option_d.py, line 88) reads `bundle.solar_irradiance.point[t]` (W/m^2, a
   small numeric value) where it should read `bundle.solar_generation.point[t]`
   (W, the actual generation power; the same bundle field
   `LocalMILPEnergyOptimizer` and `GAP19HighsNativeOptimizer` both correctly
   use for "available solar power"). The resulting `p_solar_avail` is treated
   as Watts but is numerically the irradiance's W/m^2 reading, so real solar
   generation capacity above that tiny number is neither dispatched nor
   recorded as curtailed -- it simply vanishes from the energy balance. This
   exact bug reproduces the *existing, owner-dispositioned* RT-01 residual
   (test_offline_runtime.py::test_per_timestep_conservation_audit's
   5852.500000000004 Wh imbalance at step 4) byte-for-byte, and is a materially
   different, more precise root cause than the register's currently-recorded
   attribution ("gap19_highs_native.py:444's p_curt_tot") -- see the forensics
   report for the full evidence trail (that RT-01 test's own saved artifact has
   `constraint_status == "OPTION_D_FALLBACK"`, i.e. GAP19 never ran).

3. Because mechanism (1) routes essentially every demo_scenario.json timestep
   to `OptionDFallbackSolver`, and `OptionDFallbackSolver` never reads
   `configs["optimizer"]["weights"]` at all, corrupting that config key (as
   test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved
   does) is a no-op for the full closed-loop pipeline today -- NOT because no
   production optimizer reads the key (LocalMILPEnergyOptimizer still does,
   confirmed below), but because routing never reaches the code that reads it.

4. `OptionDFallbackSolver.solve()` has a separate, independent accounting gap
   from mechanism (2): when `preserved_resource == DIESEL` (or the BOTH/TIE
   branch) and the battery discharges part of the remaining demand while
   diesel's configured minimum-power floor (`min_power_w`) forces diesel to
   generate more than the true remainder, the "excess diesel charges battery"
   logic (line 157) is gated by `p_dis == 0` and therefore never activates
   while the battery is simultaneously discharging -- the excess is neither
   curtailed, charged, served, nor recorded as unmet. This is the exact cause
   of RT-01's CURRENT (post mechanism-2-fix) step-22 residual
   (4658.729999999996 Wh) in test_per_timestep_conservation_audit. See
   forecasting/n6/reports/N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md for the full trace.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

SYSTEM_DIR = Path(__file__).resolve().parent.parent

from system.runtime.runner import PolarisLocalRunner
from system.control.router import EMSControlRouter
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.control.ecd import EmergencyAssessment, OperatingMode, ResourceSelection, ValidityStatus


def _make_bundle(solar_irr_point, solar_gen_point, wind_point, demand_point):
    n = len(demand_point)
    origin = datetime(2026, 9, 26, 0, 0, 0)
    ts = [(origin + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(n)]
    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=ts[0],
        horizon_hours=n,
        timestamps=ts,
        solar_irradiance=TimeseriesForecast(solar_irr_point, solar_irr_point, solar_irr_point, "W/m^2"),
        solar_generation=TimeseriesForecast(solar_gen_point, solar_gen_point, solar_gen_point, "W"),
        wind_generation=TimeseriesForecast(wind_point, wind_point, wind_point, "W"),
        demand=TimeseriesForecast(demand_point, demand_point, demand_point, "W"),
        metadata={"source": "rt01_rt02_forensics_regression"},
    )


class TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting:
    """
    Mechanism (1), HISTORICAL: pinned down router.py's full-demand-as-
    critical-load substitution bug, under which demo_scenario.json's step-0
    conditions (50% SOC, ~35-38kW observed demand, an ungoverned default
    t_required_hours=6.0) classified as EMERGENCY instead of NORMAL, because
    the router fed the FULL observed demand into the ECD survivability check
    as "critical_load" instead of the station's real, much smaller
    critical-load design value.

    RETARGETED 2026-10-18 (owner decision, POST_TRIAGE_INTEGRATION_AND_
    DIESEL_COMPARISON_REPORT.md Section 3): the thirteenth pass's A-iii/B-iii
    fail-closed implementation (ems/reports/rt01_runtime_fixes/ROUTER_ECD_FAIL_CLOSED_IMPLEMENTATION_REPORT.md)
    removed the substitution mechanism (and its ungoverned 6.0h default)
    from router.py ENTIRELY. There is no longer any code path by which an
    unauthorized config can reach EMERGENCY (or NORMAL) at all -- it now
    fails closed to UNKNOWN_INVALID before any margin/critical-load
    computation runs, regardless of SOC, demand, or fuel. The original
    EMERGENCY-not-NORMAL pin is therefore structurally unreachable and is
    retargeted to assert the new, STRONGER guarantee: this exact unauthorized
    config can never silently reach EMERGENCY (or NORMAL) again, under any
    future change to router.py that does not also restore its own explicit
    authorization checks.
    """

    def test_demo_scenario_step0_routes_emergency_not_normal(self):
        """
        demo_scenario.json's step-0 conditions (50% SOC, ~35-38kW observed
        demand) are run through the REAL, unmodified EMSControlRouter with
        the REAL PolarisLocalRunner.configs (which carries no "ecd" or
        "critical_load" authorization block -- confirmed by reading
        PolarisLocalRunner.__init__, which only loads station/battery/
        diesel/solar_pv/loads/optimizer YAML files). Per A-iii/B-iii, this
        must fail closed to UNKNOWN_INVALID, not silently resolve to
        EMERGENCY (the historically-pinned, now-removed mechanism) or to
        NORMAL.
        """
        runner = PolarisLocalRunner(
            SYSTEM_DIR, scenario_filename="demo_scenario.json",
            optimizer_type="milp", forecast_engine_type="stage81_solar"
        )
        # Confirm, directly from the real runner's own config dict (not
        # inferred), that no authorization is present -- this is what makes
        # UNKNOWN_INVALID the correct, current fail-closed outcome.
        assert "ecd" not in runner.configs or not runner.configs["ecd"].get("t_required_authorized")
        assert "critical_load" not in runner.configs or not runner.configs["critical_load"].get("authorized")

        first_step = runner.data_provider.timesteps[0]
        state = StationState(
            timestamp=first_step["timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=first_step["actual_SW_IN"],
            last_observed_demand=first_step["actual_demand"],
            last_observed_wind_generation=first_step["actual_wind_generation"],
            diesel_fuel_remaining_liters=100.0,
        )
        context = runner.data_provider.get_runtime_state(0)
        bundle = runner.forecast_engine.predict(state, context)
        router = EMSControlRouter()
        assessment, route = router.evaluate_and_route(state, bundle, runner.configs)

        assert route == "UNKNOWN_INVALID", (
            "Expected the current fail-closed contract to hold: an "
            "unauthorized demo_scenario.json step-0 config must route "
            f"UNKNOWN_INVALID (got {route!r}). This is a STRONGER guarantee "
            "than the original EMERGENCY-not-NORMAL pin -- if this ever "
            "starts returning EMERGENCY or NORMAL again without an explicit "
            "authorization fixture, router.py's A-iii/B-iii fail-closed "
            "checks were weakened or bypassed."
        )
        # Actual current result fields (system.control.ecd.ValidityStatus),
        # not inferred: the router's own real reason for fail-closing here.
        assert assessment.validity_status == ValidityStatus.UNAUTHORIZED_T_REQUIRED
        assert assessment.failure_reason == "Target horizon payload is unauthenticated."
        # _fail_closed's own sentinel values -- NOT a real survivability
        # margin, and asserted as such so this test cannot be misread as
        # still exercising the historical margin-computation mechanism.
        assert assessment.target_horizon_hours is None
        assert assessment.battery_margin_hours == 0.0


class TestOptionDSolarIrradianceGenerationUnitBug:
    """Mechanism (2): pins down option_d.py line 88's field-confusion bug."""

    def test_option_d_drops_solar_generation_above_irradiance_numeric_value(self):
        """
        Isolated, single-call reproduction of the RT-01 residual, with no
        dependency on the full closed-loop pipeline or router routing: feed
        OptionDFallbackSolver a bundle where solar_generation (W) is much
        larger than the numeric value of solar_irradiance (W/m^2) at one hour,
        with demand far exceeding total available renewable power. The solver
        must either dispatch or curtail all available solar generation; it
        currently does neither with the "missing" amount.
        """
        # Hour 0: irradiance=117.05 W/m^2 but actual generation=5969.55 W
        # (this is the EXACT pair observed at step 4 of the RT-01
        # test_per_timestep_conservation_audit reproduction: 5969.55 - 117.05
        # = 5852.5, byte-identical to the register's recorded residual).
        bundle = _make_bundle(
            solar_irr_point=[117.05] + [0.0] * 23,
            solar_gen_point=[5969.55] + [0.0] * 23,
            wind_point=[32500.0] * 24,
            demand_point=[42898.0] * 24,
        )
        state = StationState(
            timestamp=bundle.timestamps[0],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=117.05,
            last_observed_demand=42898.0,
            last_observed_wind_generation=32500.0,
            diesel_fuel_remaining_liters=100.0,
        )
        assessment = EmergencyAssessment(
            operating_mode=OperatingMode.EMERGENCY,
            battery_endurance_hours=1.0, diesel_endurance_hours=1.0,
            battery_margin_hours=-5.0, diesel_margin_hours=-5.0,
            preserved_resource=ResourceSelection.BOTH, limiting_resource=ResourceSelection.BOTH,
            tie_status=True, validity_status=None, failure_reason=None,
            target_horizon_hours=6.0,
        )
        configs = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0,
                        "max_discharge_power_w": 50000.0, "max_charge_power_w": 50000.0,
                        "charge_efficiency": 0.92, "discharge_efficiency": 0.92},
            "diesel": {"min_power_w": 10000.0, "max_power_w": 100000.0,
                       "base_fuel_consumption_l_per_h": 5.0,
                       "marginal_fuel_consumption_l_per_wh": 0.00025, "initial_fuel_l": 100.0},
        }
        plan = OptionDFallbackSolver().solve(assessment, bundle, state, configs)

        available_solar_w = bundle.solar_generation.point[0]  # 5969.55 W, the TRUE generation
        used_plus_curtailed = plan.solar_used[0] + plan.renewable_curtailment[0]
        residual = available_solar_w - used_plus_curtailed

        # POST-FIX behavior: residual is ~0 because option_d.py:88 now correctly
        # reads bundle.solar_generation.point[t] (W) instead of solar_irradiance (W/m^2).
        assert residual == pytest.approx(0.0, abs=1e-3), (
            f"Expected zero residual after option_d.py:88 fix; got {residual}. "
            f"solar_used[0]={plan.solar_used[0]}, curtailment[0]={plan.renewable_curtailment[0]}, "
            f"true available generation={available_solar_w}."
        )
        # Solar generation is now fully dispatched / used up to generation power (5969.55 W).
        assert plan.solar_used[0] == pytest.approx(5969.55, abs=0.01)


class TestMILPOptimizerDeliberateFailureInjectionStillIntactAtUnitLevel:
    """
    Mechanism (3): confirms the deliberate-failure injection mechanism that
    test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved
    exercises is NOT stale/dead code -- LocalMILPEnergyOptimizer.optimize()
    still raises exactly as designed when configs["optimizer"]["weights"] is
    corrupted. The full-pipeline test fails only because
    EMSControlRouter.evaluate_and_route() never routes demo_scenario.json to
    NORMAL (see TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting
    above), so this optimizer is never invoked in that test's closed-loop run.
    This is the SUPPORTED interface (direct EnergyOptimizer.optimize() call,
    the same one test_s81_e2e_integration.py::test_6 uses) the injected
    failure is meant to reach.
    """

    def test_corrupted_optimizer_weights_raises_on_direct_invocation(self):
        runner = PolarisLocalRunner(
            SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="milp"
        )
        runner.configs["optimizer"]["weights"] = "INVALID_WEIGHT_TYPE"

        context = runner.data_provider.get_runtime_state(0)
        state = StationState(
            timestamp=context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
            last_observed_demand=context["last_observed_demand"],
            last_observed_wind_generation=context["last_observed_wind_generation"],
        )
        bundle = runner.forecast_engine.predict(state, context)

        assert isinstance(runner.optimizer, LocalMILPEnergyOptimizer)
        with pytest.raises(AttributeError):
            runner.optimizer.optimize(bundle, state, runner.configs)

    def test_full_pipeline_never_reaches_milp_for_demo_scenario(self):
        """
        HISTORICAL (pre-A-iii/B-iii): run_pipeline's own saved artifact used
        to prove the step actually executed was OPTION_D_FALLBACK (route
        EMERGENCY via the now-removed critical-load-substitution mechanism),
        confirming the corrupted optimizer["weights"] key was never read for
        this scenario -- SUCCESS_CLEAN, not FAILED_TERMINATED.

        RETARGETED 2026-10-18 (owner decision, POST_TRIAGE_INTEGRATION_AND_
        DIESEL_COMPARISON_REPORT.md Section 3): with router.py's A-iii/B-iii
        fail-closed contract in place, an unauthorized demo_scenario.json
        config now routes UNKNOWN_INVALID at step 0 (confirmed by the
        companion test above), so run_pipeline's pre-existing runner.py
        branch for that route (read-only this pass, not re-verified by
        editing -- confirmed by direct re-run of the REAL, unmodified
        run_pipeline) must fail-terminate BEFORE any optimizer or Option-D
        invocation, not merely before MILP specifically. This test now
        asserts that stronger, current invariant directly against the real
        runner's own actual result fields and call counts, instead of
        reading a (possibly stale) artifact file off disk.
        """
        runner = PolarisLocalRunner(
            SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="milp"
        )
        runner.configs["optimizer"]["weights"] = "INVALID_WEIGHT_TYPE"

        # Observe actual invocation counts directly, rather than inferring
        # "no optimizer ran" from the saved artifact's freshness/staleness.
        with patch.object(
            runner.optimizer, "optimize", wraps=runner.optimizer.optimize
        ) as mock_optimize, patch.object(
            runner.option_d_solver, "solve", wraps=runner.option_d_solver.solve
        ) as mock_option_d, patch.object(
            runner.simulator, "step", wraps=runner.simulator.step
        ) as mock_sim_step:
            report = runner.run_pipeline(steps_to_run=2)

        assert report["execution_status"] == "FAILED_TERMINATED"
        assert report["completed_steps"] == 0
        assert report["timesteps_executed"] == 0
        assert "UNAUTHORIZED_T_REQUIRED" in report["fault_classes"]
        # No optimizer invocation (not just "not MILP specifically"), no
        # Option-D invocation, and no simulator state advancement -- the
        # fail-closed path short-circuits before any of these are reached.
        mock_optimize.assert_not_called()
        mock_option_d.assert_not_called()
        mock_sim_step.assert_not_called()


class TestOptionDDieselMinimumPowerExcessGenerationUnaccounted:
    """
    Mechanism (4) -- originally identified by the 2026-10-18 end-to-end
    recovery continuation pass (forecasting/n6/reports/N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md),
    found while tracing test_offline_runtime.py::test_per_timestep_conservation_audit's
    then-current (post option_d.py:88 fix) step-22 failure
    (4658.729999999996 Wh bus-bar imbalance) to its exact source. This was a
    THIRD, independent defect in system/optimization/implementations/option_d.py,
    separate from (a) the already-fixed solar/irradiance-vs-generation unit bug
    (Mechanism 2 above) and (b) router.py's critical-load-substitution
    misrouting (Mechanism 1 above, still unfixed and unrelated to this one).

    UPDATE (2026-10-18, ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md): this
    mechanism is now FIXED, under explicit owner authorization scoped to
    exactly this one defect in option_d.py, via sequencing correction
    approach (a') from ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md: diesel's
    mandatory minimum-power floor is now accounted for BEFORE the battery's
    discharge is finalized (not after), in both the `DIESEL`-preserved branch
    and the `BOTH`/`TIE` branch, so the two resources are never sized against
    overlapping demand. The pre-existing "excess diesel charges battery"
    guard (`p_diesel > 0 and p_dis == 0`) now correctly activates whenever
    diesel's floor alone covers the full remaining demand, because the fixed
    sequencing now sets `p_dis == 0` in exactly that case.

    Root cause (as originally found, read directly from option_d.py before
    this fix landed):

      - In the `preserved_resource == ResourceSelection.DIESEL` branch (and
        symmetrically in the BOTH/TIE branch), the battery discharged first
        for part of the remaining demand (`p_dis`), and diesel only covered
        `p_rem_demand_after_bat = p_rem_demand - p_dis`.
      - Diesel cannot run below its configured minimum power floor
        (`min_diesel_w`, e.g. 10,000 W): `p_diesel = min(max_diesel_w,
        max(min_diesel_w, p_rem_demand_after_bat))`. When
        `0 < p_rem_demand_after_bat < min_diesel_w`, diesel was forced to
        generate MORE than needed (e.g. 10,000 W when only ~4,000 W was
        actually required), and the pre-fix code never resized `p_dis` back
        down to compensate.
      - The "excess diesel charges battery" logic was gated by
        `if p_diesel > 0 and p_dis == 0:` -- it only activated when the
        battery was NOT also discharging this step. Since `p_dis` was
        virtually always > 0 whenever this scenario occurred in the
        DIESEL-preserved branch, the gate never opened and the excess diesel
        output above `p_rem_demand_after_bat` was neither curtailed, charged
        to the battery, nor reflected in `load_served`/`unmet_load` -- an
        energy-conservation violation.

    This test now asserts the POST-FIX (corrected) behavior: the battery no
    longer discharges when diesel's floor alone can cover the full demand
    (`p_dis == 0`), diesel runs at its floor (10,000 W), the floor's excess
    over demand (3,000 W) now charges the battery instead of vanishing, and
    the bus-bar residual is ~0.
    """

    def test_diesel_min_power_floor_creates_unaccounted_excess_when_battery_also_discharges(self):
        # No renewables this step; demand = 7000 W. Battery can supply exactly
        # 3000 W this step (energy-limited, not power-limited); diesel's
        # configured floor is 10,000 W. preserved_resource=DIESEL -> battery
        # (the limiting/weaker resource) discharges first per option_d.py's own
        # branch comment ("Preserve diesel: Discharge usable battery energy
        # first"), leaving only 4000 W of real remaining need for diesel --
        # but diesel cannot run below its 10,000 W floor.
        bundle = _make_bundle(
            solar_irr_point=[0.0] * 24,
            solar_gen_point=[0.0] * 24,
            wind_point=[0.0] * 24,
            demand_point=[7000.0] * 24,
        )
        min_soc_pct = 20.0
        capacity_wh = 200000.0
        eta_dis = 0.92
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)  # 40000.0
        # usable_dc_wh * eta_dis == 3000.0 exactly -> battery_energy_wh:
        battery_energy_wh = min_e_wh + (3000.0 / eta_dis)
        state = StationState(
            timestamp=bundle.timestamps[0],
            battery_soc_pct=(battery_energy_wh / capacity_wh) * 100.0,
            battery_energy_wh=battery_energy_wh,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=7000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0,
        )
        assessment = EmergencyAssessment(
            operating_mode=OperatingMode.EMERGENCY,
            battery_endurance_hours=1.0, diesel_endurance_hours=5.0,
            battery_margin_hours=-5.0, diesel_margin_hours=-1.0,
            preserved_resource=ResourceSelection.DIESEL, limiting_resource=ResourceSelection.BATTERY,
            tie_status=False, validity_status=None, failure_reason=None,
            target_horizon_hours=6.0,
        )
        configs = {
            "battery": {"capacity_wh": capacity_wh, "min_soc_pct": min_soc_pct, "max_soc_pct": 95.0,
                        "max_discharge_power_w": 50000.0, "max_charge_power_w": 50000.0,
                        "charge_efficiency": 0.92, "discharge_efficiency": eta_dis},
            "diesel": {"min_power_w": 10000.0, "max_power_w": 50000.0,
                       "base_fuel_consumption_l_per_h": 5.0,
                       "marginal_fuel_consumption_l_per_wh": 0.00025, "initial_fuel_l": 100.0},
        }
        plan = OptionDFallbackSolver().solve(assessment, bundle, state, configs)

        t = 0
        # POST-FIX (a', sequencing correction): diesel's floor (10,000 W) is
        # accounted for BEFORE battery discharge is sized. Since the floor
        # alone exceeds the full 7,000 W demand, the battery no longer
        # discharges at all this step -- it is diesel's floor-forced output,
        # not the battery, that covers the demand, with the floor's surplus
        # charging the battery instead of vanishing.
        assert plan.battery_discharge[t] == pytest.approx(0.0, abs=0.5)
        assert plan.diesel_power[t] == pytest.approx(10000.0, abs=0.5)
        # The excess-diesel-charging guard (`p_diesel > 0 and p_dis == 0`) now
        # correctly opens because p_dis == 0, so the floor's 3000 W surplus
        # over the 7000 W demand charges the battery instead of vanishing.
        assert plan.battery_charge[t] == pytest.approx(3000.0, abs=0.5)
        assert plan.unmet_load[t] == pytest.approx(0.0, abs=0.5)  # demand fully served

        sources = plan.solar_used[t] + plan.wind_used[t] + plan.battery_discharge[t] + plan.diesel_power[t]
        sinks = plan.load_served[t] + plan.flexible_load_schedule[t] + plan.battery_charge[t]
        excess_w = sources - sinks

        # FIXED behavior: the ~6000 W of diesel generation that was
        # previously neither curtailed, charged, served, nor recorded as
        # unmet is now fully reconciled (served load + battery charge), so
        # the bus-bar residual is ~0. This is the same mechanism behind
        # test_per_timestep_conservation_audit's former step-22 residual
        # (4658.73 Wh there, under demo_scenario.json's own numbers; 6000 W
        # here, under this isolated, hand-picked scenario chosen to make the
        # mechanism unambiguous).
        assert excess_w == pytest.approx(0.0, abs=1e-3), (
            f"Expected ~0.0 bus-bar residual after the option_d.py sequencing "
            f"fix (RT-01 approach a'); got {excess_w}. A nonzero value here "
            f"means the diesel-minimum-power floor excess is unaccounted for "
            f"again -- a regression of the fix in OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md."
        )
        assert plan.energy_balance_errors[t] == pytest.approx(0.0, abs=1e-3), (
            "energy_balance_errors must now be computed from the actual "
            "dispatch arrays (not hardcoded to 0.0) and must agree with the "
            "independently recomputed residual above."
        )


class TestOptionDDieselFloorRepairAcceptanceRegression:
    """
    Focused acceptance regression for the RT-01 Option-D diesel-minimum-power
    floor repair (ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_PROPOSAL.md /
    ems/reports/diesel_and_loads/OPTION_D_DIESEL_FLOOR_REPAIR_REPORT.md), required by the owner's
    implementation-authorization directive Section 3. Exercises the exact
    triggering condition -- residual demand after battery dispatch is
    positive but below the diesel minimum-power floor -- including the
    partial-correction sub-case where the battery still ends up discharging
    a reduced (not zeroed) amount, not just the full-coverage case already
    covered by TestOptionDDieselMinimumPowerExcessGenerationUnaccounted above.
    """

    def _configs(self, min_power_w=10000.0, max_power_w=50000.0, max_dis_w=50000.0):
        return {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0,
                        "max_discharge_power_w": max_dis_w, "max_charge_power_w": 50000.0,
                        "charge_efficiency": 0.92, "discharge_efficiency": 0.92},
            "diesel": {"min_power_w": min_power_w, "max_power_w": max_power_w,
                       "base_fuel_consumption_l_per_h": 5.0,
                       "marginal_fuel_consumption_l_per_wh": 0.00025, "initial_fuel_l": 100.0},
        }

    def test_partial_battery_discharge_below_floor_reconciles_physically(self):
        """
        Demand = 12,000 W; battery is energy-limited to exactly 3,000 W this
        step (usable_dc_wh * eta_dis == 3000.0); diesel's floor is 10,000 W.
        preserved_resource=DIESEL -> battery alone cannot cover demand
        (gap = 12000 - 3000 = 9000 W), and that gap (9000 W) is itself below
        the 10,000 W floor, so diesel is forced to 10,000 W -- but unlike the
        full-coverage case above, the battery still ends up contributing a
        REDUCED (not zeroed) discharge of demand - diesel = 2000 W, because
        diesel's floor-forced output does not cover the entire 12,000 W
        demand by itself.
        """
        bundle = _make_bundle(
            solar_irr_point=[0.0] * 24,
            solar_gen_point=[0.0] * 24,
            wind_point=[0.0] * 24,
            demand_point=[12000.0] * 24,
        )
        min_soc_pct = 20.0
        capacity_wh = 200000.0
        eta_dis = 0.92
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        battery_energy_wh = min_e_wh + (3000.0 / eta_dis)
        state = StationState(
            timestamp=bundle.timestamps[0],
            battery_soc_pct=(battery_energy_wh / capacity_wh) * 100.0,
            battery_energy_wh=battery_energy_wh,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=12000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0,
        )
        assessment = EmergencyAssessment(
            operating_mode=OperatingMode.EMERGENCY,
            battery_endurance_hours=1.0, diesel_endurance_hours=5.0,
            battery_margin_hours=-5.0, diesel_margin_hours=-1.0,
            preserved_resource=ResourceSelection.DIESEL, limiting_resource=ResourceSelection.BATTERY,
            tie_status=False, validity_status=None, failure_reason=None,
            target_horizon_hours=6.0,
        )
        configs = self._configs()
        plan = OptionDFallbackSolver().solve(assessment, bundle, state, configs)

        t = 0
        assert plan.diesel_power[t] == pytest.approx(10000.0, abs=0.5)
        assert plan.battery_discharge[t] == pytest.approx(2000.0, abs=0.5)
        assert plan.battery_charge[t] == 0.0
        assert plan.unmet_load[t] == pytest.approx(0.0, abs=0.5)

        # No timestep has both positive charge and positive discharge.
        for i in range(24):
            assert not (plan.battery_charge[i] > 0.0 and plan.battery_discharge[i] > 0.0), (
                f"Simultaneous charge/discharge at step {i}: "
                f"charge={plan.battery_charge[i]}, discharge={plan.battery_discharge[i]}"
            )

        # Diesel output, served load, battery flows and curtailment reconcile
        # physically (bus-bar balance) at every step.
        for i in range(24):
            sources = plan.solar_used[i] + plan.wind_used[i] + plan.battery_discharge[i] + plan.diesel_power[i]
            sinks = plan.load_served[i] + plan.flexible_load_schedule[i] + plan.battery_charge[i]
            assert abs(sources - sinks) < 1e-3, f"Bus-bar imbalance at step {i}: {sources - sinks}"
            assert plan.energy_balance_errors[i] == pytest.approx(0.0, abs=1e-3)

        # Fuel consumption matches the actual diesel energy dispatched under
        # the existing model's own fuel-accounting convention
        # (base_lph + marginal_lpwh * p_diesel per hour, same formula
        # option_d.py itself uses to debit available_fuel).
        base_lph = configs["diesel"]["base_fuel_consumption_l_per_h"]
        marginal_lpwh = configs["diesel"]["marginal_fuel_consumption_l_per_wh"]
        expected_fuel_used_l = sum(
            (base_lph + marginal_lpwh * p) for p in plan.diesel_power if p > 0
        )
        fuel_remaining = 100.0 - expected_fuel_used_l
        assert fuel_remaining == pytest.approx(100.0 - expected_fuel_used_l, abs=1e-6)
        assert expected_fuel_used_l > 0.0  # diesel genuinely ran and burned fuel

        # SOC, charge/discharge efficiencies and power limits remain valid.
        for i in range(24):
            assert 20.0 - 1e-6 <= plan.battery_soc[i] <= 95.0 + 1e-6
            assert plan.battery_discharge[i] <= configs["battery"]["max_discharge_power_w"] + 1e-6
            assert plan.battery_charge[i] <= configs["battery"]["max_charge_power_w"] + 1e-6
            if plan.diesel_power[i] > 0:
                assert plan.diesel_power[i] <= configs["diesel"]["max_power_w"] + 1e-6
                # Once committed, diesel never runs below its floor.
                assert plan.diesel_power[i] >= configs["diesel"]["min_power_w"] - 1e-6

    def test_both_tie_branch_floor_binding_also_reconciles(self):
        """
        Same mechanism, but in the BOTH/TIE balanced-dispatch branch (the
        proposal's "symmetrically in the BOTH/TIE branch" case): demand =
        9,000 W, battery can supply up to 20,000 W (not energy-limited), so
        the balanced split would normally be 4,500 W / 4,500 W -- but
        diesel's 10,000 W floor exceeds the diesel share, forcing the same
        floor-binding correction.
        """
        bundle = _make_bundle(
            solar_irr_point=[0.0] * 24,
            solar_gen_point=[0.0] * 24,
            wind_point=[0.0] * 24,
            demand_point=[9000.0] * 24,
        )
        capacity_wh = 200000.0
        state = StationState(
            timestamp=bundle.timestamps[0],
            battery_soc_pct=80.0,
            battery_energy_wh=capacity_wh * 0.80,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=9000.0,
            last_observed_wind_generation=0.0,
            diesel_fuel_remaining_liters=100.0,
        )
        assessment = EmergencyAssessment(
            operating_mode=OperatingMode.EMERGENCY,
            battery_endurance_hours=1.0, diesel_endurance_hours=5.0,
            battery_margin_hours=-5.0, diesel_margin_hours=-1.0,
            preserved_resource=ResourceSelection.BOTH, limiting_resource=ResourceSelection.BOTH,
            tie_status=True, validity_status=None, failure_reason=None,
            target_horizon_hours=6.0,
        )
        configs = self._configs()
        plan = OptionDFallbackSolver().solve(assessment, bundle, state, configs)

        t = 0
        # Floor (10000) exceeds full demand (9000) -> diesel alone covers it,
        # battery does not discharge at all, and the 1000 W surplus charges
        # the battery.
        assert plan.diesel_power[t] == pytest.approx(10000.0, abs=0.5)
        assert plan.battery_discharge[t] == pytest.approx(0.0, abs=0.5)
        assert plan.battery_charge[t] == pytest.approx(1000.0, abs=0.5)
        assert plan.unmet_load[t] == pytest.approx(0.0, abs=0.5)

        for i in range(24):
            assert not (plan.battery_charge[i] > 0.0 and plan.battery_discharge[i] > 0.0)
            sources = plan.solar_used[i] + plan.wind_used[i] + plan.battery_discharge[i] + plan.diesel_power[i]
            sinks = plan.load_served[i] + plan.flexible_load_schedule[i] + plan.battery_charge[i]
            assert abs(sources - sinks) < 1e-3, f"Bus-bar imbalance at step {i}: {sources - sinks}"
            assert plan.energy_balance_errors[i] == pytest.approx(0.0, abs=1e-3)
