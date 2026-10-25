"""
Regression tests: router-assessed operating mode must reach the research MILP.

Bug (pre-fix): EMSControlRouter.evaluate_and_route computed EMERGENCY, but the
research closed-loop runners passed the unchanged StationState (operating_mode
NORMAL, carried forward by the realization executor) to the optimizer. The
EMERGENCY-only constraint (discharge <= served) therefore never activated.

These tests use the real router and the real research extractor. The MILP is
observed through a HiGHS spy that records every addRow call.
"""

import ast
import copy
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments" / "candidate_s_sw_campaign_2024"))

import highspy  # noqa: E402

from system.control.router import EMSControlRouter  # noqa: E402
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine  # noqa: E402
from system.research.route_mode_propagation import propagate_route_mode  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402
import research_numerical_extractor as extractor  # noqa: E402


CRITICAL_CEILING_W = 11600.0
K_PER_HOUR = 15


def _canonical_configs():
    # Mirrors experiments/run_diesel_reduction_campaign.py::load_canonical_configs
    with open(REPO / "system/config/battery.yaml") as f:
        bat = yaml.safe_load(f)
    with open(REPO / "system/config/diesel.yaml") as f:
        die = yaml.safe_load(f)
    with open(REPO / "system/config/solar_pv.yaml") as f:
        sol = yaml.safe_load(f)
    with open(REPO / "system/config/loads.yaml") as f:
        loads = yaml.safe_load(f)
    return {
        "battery": bat,
        "diesel": die,
        "solar_pv": sol,
        "loads": loads,
        "critical_demand_baseline_w": CRITICAL_CEILING_W,
        "terminal_target_wh": 100000.0,
        # Explicit SYNTHETIC test-fixture authorization for the router/ECD
        # fail-closed contract (ECD-01, A-iii/B-iii). This suite tests
        # genuine router->MILP mode-propagation mechanics (NORMAL_STATE is
        # 95% SOC/100L fuel, EMERGENCY_STATE is 20% SOC/0L fuel -- either
        # routes the same way at effectively any small critical load), not
        # the authorization gate itself. "EVID-TEST-ROUTE-MODE-PROPAGATION"
        # is NOT a real-station evidence record -- see
        # tests/test_isolated_components.py for the convention.
        "ecd": {"t_required_hours": 6.0, "t_required_authorized": True},
        "critical_load": {
            "authorized": True,
            "evidence_id": "EVID-TEST-ROUTE-MODE-PROPAGATION",
            "authorized_critical_load_w": 5000.0,
        },
    }


def _state(soc, energy_wh, fuel_l, wind_w, operating_mode):
    return StationState(
        timestamp="2025-05-01T00:00:00Z",
        battery_soc_pct=soc,
        battery_energy_wh=energy_wh,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=wind_w,
        diesel_fuel_remaining_liters=fuel_l,
        operating_mode=operating_mode,
    )


NORMAL_STATE = dict(soc=95.0, energy_wh=190000.0, fuel_l=100.0, wind_w=20000.0)
EMERGENCY_STATE = dict(soc=20.0, energy_wh=40000.0, fuel_l=0.0, wind_w=4500.0)


class _SpyHighs(highspy.Highs):
    """Records every addRow call so tests can count MILP rows by type."""

    instances = []

    def __init__(self):
        super().__init__()
        self.recorded_rows = []
        _SpyHighs.instances.append(self)

    def addRow(self, lhs, rhs, n, idx, coef):
        self.recorded_rows.append((float(lhs), float(rhs), int(n), list(idx), list(coef)))
        return super().addRow(lhs, rhs, n, idx, coef)


def _emergency_rows(rows):
    """Rows of the EMERGENCY-only form: p_dis(t) - p_served(t) <= 0 for some hour t."""
    found = []
    for lhs, rhs, n, idx, coef in rows:
        if n != 2 or rhs != 0.0 or not math.isinf(lhs) or lhs > 0:
            continue
        pairs = dict(zip(idx, coef))
        for t in range(24):
            base = t * K_PER_HOUR
            if pairs.get(base + 5) == 1.0 and pairs.get(base + 8) == -1.0:
                found.append(t)
                break
    return sorted(found)


def _run_optimizer(planning_state, monkeypatch):
    _SpyHighs.instances.clear()
    monkeypatch.setattr(highspy, "Highs", _SpyHighs)

    configs = _canonical_configs()
    engine = LocalBaselineForecastEngine(Path("config/pv_config.yaml"))
    bundle = engine.predict(planning_state, {})
    configs["critical_demand_w"] = [min(CRITICAL_CEILING_W, d) for d in bundle.demand.point]

    opt = extractor.ResearchNumericalGAP19Optimizer(tau=extractor.TAU_RESIDUE_W)
    plan = opt.optimize(bundle, planning_state, configs)
    assert len(_SpyHighs.instances) == 1
    return plan, _SpyHighs.instances[0].recorded_rows


def _route(state_kwargs):
    """Run the real router on a state built from the given kwargs and return its route."""
    st = _state(operating_mode="NORMAL", **state_kwargs)
    engine = LocalBaselineForecastEngine(Path("config/pv_config.yaml"))
    bundle = engine.predict(st, {})
    _, route = EMSControlRouter().evaluate_and_route(st, bundle, _canonical_configs())
    return st, route


# ---------------------------------------------------------------------------
# Router assessment and fixtures
# ---------------------------------------------------------------------------

def test_fixture_states_route_as_named():
    _, normal_route = _route(NORMAL_STATE)
    _, emergency_route = _route(EMERGENCY_STATE)
    assert normal_route == "NORMAL"
    assert emergency_route == "EMERGENCY"


# ---------------------------------------------------------------------------
# propagate_route_mode
# ---------------------------------------------------------------------------

def test_propagate_sets_mode_without_mutating_original():
    original = _state(operating_mode="NORMAL", **EMERGENCY_STATE)
    planning = propagate_route_mode(original, "EMERGENCY")
    assert planning.operating_mode == "EMERGENCY"
    assert original.operating_mode == "NORMAL"
    assert planning.battery_energy_wh == original.battery_energy_wh
    assert planning.diesel_fuel_remaining_liters == original.diesel_fuel_remaining_liters


def test_propagate_normalises_case():
    original = _state(operating_mode="NORMAL", **NORMAL_STATE)
    assert propagate_route_mode(original, "emergency").operating_mode == "EMERGENCY"


# ---------------------------------------------------------------------------
# Router -> MILP
# ---------------------------------------------------------------------------

def test_normal_assessment_reaches_milp_as_normal(monkeypatch):
    st, route = _route(NORMAL_STATE)
    assert route == "NORMAL"
    planning = propagate_route_mode(st, route)
    assert planning.operating_mode == "NORMAL"

    _, rows = _run_optimizer(planning, monkeypatch)
    assert _emergency_rows(rows) == [], "EMERGENCY-only constraint must be absent under NORMAL"


def test_emergency_assessment_reaches_milp_and_activates_constraint(monkeypatch):
    st, route = _route(EMERGENCY_STATE)
    assert route == "EMERGENCY"
    planning = propagate_route_mode(st, route)
    assert planning.operating_mode == "EMERGENCY"

    plan, rows = _run_optimizer(planning, monkeypatch)
    assert _emergency_rows(rows) == list(range(24)), "EMERGENCY-only constraint must be present for all 24 hours"
    assert "OPTIMAL" in str(plan.constraint_status).upper()

    dis = np.array(plan.battery_discharge, dtype=float)
    served = np.array(plan.load_served, dtype=float)
    assert np.all(dis <= served + 1e-6), "EMERGENCY plan must satisfy battery discharge <= served load"


def test_unpropagated_state_never_reaches_milp_as_emergency(monkeypatch):
    # Reproduces the pre-fix behaviour: router says EMERGENCY, but the state the
    # optimizer receives still carries NORMAL (as the executor always did).
    st, route = _route(EMERGENCY_STATE)
    assert route == "EMERGENCY"
    _, rows = _run_optimizer(copy.copy(st), monkeypatch)
    assert st.operating_mode == "NORMAL"
    assert _emergency_rows(rows) == [], "without propagation the EMERGENCY constraint is not built"


# ---------------------------------------------------------------------------
# Wiring: both research loops propagate before optimizing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "relpath",
    [
        "system/research/closed_loop_causal_nwp_runner.py",
        "system/research/research_critical_demand_adapter.py",
    ],
)
def test_research_loop_propagates_route_before_optimize(relpath):
    tree = ast.parse((REPO / relpath).read_text())
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
        names = [getattr(c.func, "attr", getattr(c.func, "id", "")) for c in calls]
        if "optimize" not in names:
            continue
        assert "propagate_route_mode" in names, f"{relpath}:{fn.name} calls optimize without propagating route"
        opt_call = next(c for c in calls if getattr(c.func, "attr", "") == "optimize")
        state_arg = opt_call.args[1]
        assert isinstance(state_arg, ast.Name) and state_arg.id == "planning_state", (
            f"{relpath}:{fn.name} must pass planning_state to optimize, not the execution state"
        )
