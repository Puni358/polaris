"""
R1 Prompt 2: genuine-scarcity objective-priority verification for Planner-CF v1
(EXP-PLANNER-CF-CONSISTENCY-2025). Real HiGHS solver, no mocks.

These fixtures do NOT evaluate any origin, run any campaign, or touch
experiments/exp_three_arm_2024/ in any way. They construct small, hand-computed,
genuinely resource-scarce synthetic instances of the existing frozen
PlannerCFV1Optimizer and verify, from the returned plan and optimizer.last_objectives,
that the real solver enforces J1 > J_NC > J2 > J3 > J4 as configured via
HighsLinearObjective priorities (research_numerical_extractor_planner_cf_v1.py:85,
344-367), not merely that the PRIORITY dict and source ordering declare it.

Each fixture documents, before asserting, the exact supply/demand arithmetic that
makes the expected outcome the unique optimum -- so a test failure here is evidence
about the solver's actual behavior, not an arbitrary expected value.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import research_numerical_extractor_planner_cf_v1 as planner  # noqa: E402
import oracle_runner as oracle  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402

TOL = 1e-3  # W / Wh tolerance for linear MILP outputs; matches the existing suite's convention
               # (e.g. tests/test_planner_cf_v1.py uses 1e-3/1e-2 throughout for the same reason:
               # HiGHS's own default MILP feasibility/optimality tolerances are not configured by
               # this project, so results are exact up to those defaults, not to full float precision).


class _Series:
    def __init__(self, point):
        self.point = list(point)


class _Bundle:
    def __init__(self, solar, wind, demand):
        self.timestamps = [f"2025-05-01T{h:02d}:00:00Z" for h in range(24)]
        self.solar_generation = _Series(solar)
        self.wind_generation = _Series(wind)
        self.demand = _Series(demand)
        self.demand_critical = None


def _state(e0_wh=100000.0, fuel_l=1000.0):
    return StationState(
        timestamp="2025-04-30T23:00:00Z", battery_soc_pct=50.0, battery_energy_wh=e0_wh,
        diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
        last_observed_demand=0.0, last_observed_wind_generation=0.0,
        diesel_fuel_remaining_liters=fuel_l, operating_mode="NORMAL",
    )


def _cfg(critical, battery_overrides=None, diesel_overrides=None, ebr_wh=None):
    cfg = oracle.canonical_configs()
    cfg["critical_demand_w"] = list(critical)
    cfg["battery"] = dict(cfg["battery"])
    cfg["diesel"] = dict(cfg["diesel"])
    if battery_overrides:
        cfg["battery"].update(battery_overrides)
    if diesel_overrides:
        cfg["diesel"].update(diesel_overrides)
    if ebr_wh is not None:
        cfg["ebr_target_wh"] = ebr_wh
    return cfg


def _check_feasibility_independent(plan, crit, demand, max_supply_w, tol=TOL):
    """Independent, hand-derived sanity check not relying on the optimizer's own bus-balance
    identity test: total served load at every hour must not exceed the fixture's own
    independently-stated maximum deliverable power."""
    for t in range(24):
        served = plan.load_served[t]
        assert served <= max_supply_w + tol, f"hour {t}: served {served} exceeds stated max supply {max_supply_w}"
        assert served <= demand[t] + tol, f"hour {t}: served {served} exceeds demand {demand[t]}"


# ---------------------------------------------------------------------------
# Fixture A: J1 (unmet_crit) vs J_NC (unmet_nc), with embedded J1/J_NC vs J3
# ---------------------------------------------------------------------------
#
# No solar/wind. Battery discharge disabled (max_discharge_power_w=0) so only diesel
# can serve load. Diesel capped at max_power_w=15000 (min_power_w left at the
# system default, 10000, so diesel is either off or in [10000,15000]).
# critical = 12000 W/h constant, demand = 20000 W/h constant -> d_nc = 8000 W/h constant.
# reserve disabled (reserve_enabled=False) to isolate J1/J_NC from J2 entirely.
#
# Maximum deliverable power is 15000 W (diesel only). Since J1 >> J_NC in priority,
# the unique optimum must serve critical (12000 W) FIRST, leaving exactly 15000-12000
# = 3000 W for non-critical of the 8000 W/h needed -> unmet_nc = 5000 W/h, every hour,
# unmet_crit = 0. This also requires diesel to run at its cap (15000 W) despite its
# fuel cost (J3), because reducing unmet load dominates J3 in priority -- so this one
# fixture evidences J1 > J_NC AND J1,J_NC > J3 simultaneously.
def test_priority_A_critical_before_noncritical_under_diesel_only_scarcity():
    crit = [12000.0] * 24
    demand = [20000.0] * 24
    bundle = _Bundle([0.0] * 24, [0.0] * 24, demand)
    cfg = _cfg(crit, battery_overrides={"max_discharge_power_w": 0.0},
               diesel_overrides={"max_power_w": 15000.0})
    opt = planner.PlannerCFV1Optimizer(reserve_enabled=False)
    plan = opt.optimize(bundle, _state(), cfg)

    assert plan.constraint_status == "OPTIMAL", f"unexpected termination: {plan.constraint_status}"
    _check_feasibility_independent(plan, crit, demand, max_supply_w=15000.0)

    for t in range(24):
        unmet_total = plan.unmet_load[t]
        unmet_crit = max(0.0, crit[t] - min(plan.load_served[t], crit[t]))
        # independent re-derivation from the returned plan, not trusting a single field:
        served = plan.load_served[t]
        assert abs(served - 15000.0) < TOL, f"hour {t}: diesel-limited supply not fully used ({served})"
        assert served >= crit[t] - TOL, f"hour {t}: critical demand not met first (served={served}, crit={crit[t]})"
        assert abs(unmet_total - 5000.0) < TOL, f"hour {t}: expected exactly 5000 W unmet (non-critical), got {unmet_total}"
        assert plan.diesel_power[t] >= 15000.0 - TOL, f"hour {t}: diesel not run at its cap despite scarcity ({plan.diesel_power[t]})"

    assert opt.last_objectives["J1"] < TOL, f"J1 (unmet_crit) should be ~0, got {opt.last_objectives['J1']}"
    j_nc_expected = 5000.0 * 24
    assert abs(opt.last_objectives["J_NC"] - j_nc_expected) < 1.0, \
        f"J_NC expected ~{j_nc_expected}, got {opt.last_objectives['J_NC']}"


# ---------------------------------------------------------------------------
# Fixture B: J1 (unmet_crit) vs J2 (reserve shortfall)
# ---------------------------------------------------------------------------
#
# No solar/wind, no non-critical load (critical == demand, so J_NC stays identically 0,
# isolating this fixture to J1 vs J2 only). Diesel capped at exactly 12000 W = critical
# demand, battery charging left at the system default (max_charge_power_w=50000) but
# there is NO supply slack to charge with: diesel can deliver at most exactly enough
# to cover critical load, with zero watts left over for charging without creating
# unmet_crit > 0. Reserve target is set (via ebr_target_wh override) higher than the
# battery's starting energy, so meeting it fully requires charging -- which is only
# possible by taking power away from critical load.
#
# Since J1 > J2 in priority, the unique optimum must set charge = 0 (zero unmet_crit)
# and accept the full reserve shortfall: with no charge/discharge, e_next stays at the
# initial battery energy for all 24 hours (battery transition row, t=0 initial_e_wh;
# t>0 carries forward unchanged when charge=discharge=0).
def test_priority_B_critical_load_before_reserve_under_zero_slack_scarcity():
    crit = [12000.0] * 24
    bundle = _Bundle([0.0] * 24, [0.0] * 24, crit)  # demand == critical: no non-critical load at all
    initial_e_wh = 100000.0  # battery.yaml: capacity 200000, min_soc 20% -> 40000, max_soc 95% -> 190000
    ebr_target = 150000.0    # requires e_next >= 150000 + 40000 = 190000 (= max_e_wh exactly) to zero s_j2
    cfg = _cfg(crit, diesel_overrides={"max_power_w": 12000.0, "min_power_w": 0.0}, ebr_wh=ebr_target)
    opt = planner.PlannerCFV1Optimizer(reserve_enabled=True)
    plan = opt.optimize(bundle, _state(e0_wh=initial_e_wh), cfg)

    assert plan.constraint_status == "OPTIMAL", f"unexpected termination: {plan.constraint_status}"
    _check_feasibility_independent(plan, crit, crit, max_supply_w=12000.0)

    for t in range(24):
        assert plan.unmet_load[t] < TOL, f"hour {t}: unmet_crit should be exactly 0, got {plan.unmet_load[t]}"
        assert plan.battery_charge[t] < TOL, f"hour {t}: charging occurred, which would require stealing supply from critical load ({plan.battery_charge[t]} W)"
        assert plan.battery_discharge[t] < TOL, f"hour {t}: unexpected discharge ({plan.battery_discharge[t]} W)"

    assert opt.last_objectives["J1"] < TOL, f"J1 should be 0, got {opt.last_objectives['J1']}"
    req = ebr_target + 40000.0  # e_stage2_target[t] (= ebr_target, since terminal override not set here matters only at t=23) + min_e_wh
    expected_j2_per_hour = max(0.0, req - initial_e_wh)
    # hour 23 uses max(ebr_target, terminal_target_wh); terminal default from canonical_configs is 100000,
    # which is below ebr_target (150000), so it does not change the bound at hour 23.
    expected_j2_total = expected_j2_per_hour * 24
    assert abs(opt.last_objectives["J2"] - expected_j2_total) < 1.0, \
        f"J2 expected ~{expected_j2_total} (no charging possible without stealing from critical load), got {opt.last_objectives['J2']}"


# ---------------------------------------------------------------------------
# Fixture C: J3 (diesel fuel) kept at its true minimum; J4 (curtailment) only
# forced by a genuinely binding battery-charge cap, never traded away from J3.
# ---------------------------------------------------------------------------
#
# Large solar surplus (80000 W), no wind. critical = demand = 12000 W/h (no
# non-critical load). Diesel available (system defaults) but should be entirely
# unused, because solar alone exceeds load + the battery's max charge cap. Reserve
# enabled with a modest target reachable well inside the charge cap, so charging is
# rewarded (lowers J2) without needing diesel at all.
#
# Max usable solar = load (12000) + max_charge_power_w (50000) = 62000 W.
# Forced curtailment = 80000 - 62000 = 18000 W/h exactly (every extra W of charge
# strictly reduces curtailment with no downside in any objective, so the optimum
# charges to its cap and curtails only the physically unusable remainder).
def test_priority_C_diesel_stays_idle_and_curtailment_is_the_forced_residual():
    crit = [12000.0] * 24
    bundle = _Bundle([80000.0] * 24, [0.0] * 24, crit)
    initial_e_wh = 100000.0
    ebr_target = 30000.0  # req = 30000 + 40000 = 70000 < initial_e_wh + max_charge*eta -> easily reachable
    # max_discharge_power_w=0: removes battery cycling as an option, so the only way to reduce
    # curtailment is monotonic charging. (An earlier version of this fixture left discharge
    # enabled and found the real solver chooses a non-obvious charge/discharge cycling pattern
    # that achieves LOWER total curtailment than monotonic charging -- a legitimate, better
    # solution, not a defect: curtailment is counted at the generation side, so repeatedly
    # freeing SOC headroom to keep absorbing solar at the 50000 W/hour cap beats permanently
    # saturating the battery after ~2 hours, despite round-trip efficiency losses. That
    # observation is reported in the investigation below; it is deliberately excluded here so
    # this fixture has one clean, hand-verifiable prediction.)
    cfg = _cfg(crit, ebr_wh=ebr_target, battery_overrides={"max_discharge_power_w": 0.0})
    opt = planner.PlannerCFV1Optimizer(reserve_enabled=True)
    plan = opt.optimize(bundle, _state(e0_wh=initial_e_wh), cfg)

    assert plan.constraint_status == "OPTIMAL", f"unexpected termination: {plan.constraint_status}"

    # Note on per-hour allocation: the objective is time-invariant (every hour's curtailment
    # costs the same), so WHEN the 90826.09 Wh of total charging happens is not uniquely
    # determined -- only the total matters. A first run of this fixture assumed front-loaded
    # charging (charge early, saturate, then sit at the cap) and asserted exact hour-0 values;
    # the real solver instead returned an equally optimal, back-loaded solution (sit at zero
    # charge for hours 0-21, then charge at hours 22-23) with the IDENTICAL total J4 -- a
    # genuine tied/degenerate optimum, not a defect. Per-hour assertions below therefore check
    # only what's invariant across any optimal allocation; the exact total is checked separately
    # against an independently hand-derived figure.
    for t in range(24):
        assert plan.unmet_load[t] < TOL, f"hour {t}: unmet load should be 0 (solar surplus is ample), got {plan.unmet_load[t]}"
        assert plan.diesel_power[t] < TOL, f"hour {t}: diesel ran despite zero need, wasting fuel (J3) ({plan.diesel_power[t]} W)"
        # hard lower bound independent of SOC state/allocation: at most load (12000) + charge cap
        # (50000) = 62000 W of the 80000 W available can ever be absorbed in any single hour.
        assert plan.renewable_curtailment[t] >= 18000.0 - TOL, \
            f"hour {t}: curtailment {plan.renewable_curtailment[t]} below the physically forced minimum 18000 W"
        # hard upper bound: with no charging at all, curtailment can never exceed 80000-12000=68000.
        assert plan.renewable_curtailment[t] <= 68000.0 + TOL, \
            f"hour {t}: curtailment {plan.renewable_curtailment[t]} exceeds the no-charge maximum 68000 W"

    assert opt.last_objectives["J3"] < TOL, f"J3 (fuel) should be exactly 0 -- diesel was not needed, got {opt.last_objectives['J3']}"
    assert opt.last_objectives["J2"] < TOL, f"J2 should be 0 -- reserve target easily reachable within the charge cap, got {opt.last_objectives['J2']}"

    # Independently hand-derived total (eta_chg=0.92, dt=1.0, max_e_wh=190000, from battery.yaml),
    # using ONE possible optimal allocation -- front-loaded charging -- as the derivation vehicle.
    # The true optimum is degenerate (any allocation of the same total charge across the horizon
    # gives the same total curtailment, since the objective is time-invariant); this derivation
    # is a valid way to compute the OPTIMAL TOTAL even though the real solve chose a different
    # (back-loaded) allocation of that same total, confirmed above:
    #   hour 0: e=100000 -> room 90000Wh -> charge capped at 50000W -> e1 = 100000+0.92*50000 = 146000
    #   hour 1: e=146000 -> room 44000Wh -> charge = 44000/0.92 = 47826.09W (now the binding limit) -> e2 = 190000 (saturated)
    #   hours 2-23 (22 hours): room = 0 -> charge = 0
    # curtailment[t] = 80000 - 12000 - charge[t] = 68000 - charge[t] under this allocation:
    #   hour 0: 18000; hour 1: 20173.91; hours 2-23: 68000 each. Total charged: 50000+47826.09=97826.09 Wh.
    j4_expected = 18000.0 + (68000.0 - 44000.0 / 0.92) + 22 * 68000.0
    assert abs(opt.last_objectives["J4"] - j4_expected) < 5.0, \
        f"J4 expected ~{j4_expected} (hand-derived from the exact SOC-saturation trajectory), got {opt.last_objectives['J4']}"
