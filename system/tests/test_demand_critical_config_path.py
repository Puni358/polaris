"""
Regression coverage for the demand_critical / GAP19 integration fix
(system/orchestration/worker.py, Cell B execution path).

Scope: this tests EXACTLY the one-line fix added to worker.py --
    critical_demand_w = [min(loads.yaml critical_load.baseline_power_w, d)
                          for d in bundle.demand.point]
against the REAL, UNMODIFIED GAP19HighsNativeOptimizer -- not a mock --
to pin both:
  1. the config path: GAP19's existing top-level `critical_demand_w`
     fallback (gap19_highs_native.py lines 90-94) correctly accepts the
     worker-computed list and proceeds past the
     MISSING_GOVERNED_INPUT(demand_critical) error.
  2. the low-demand edge case: an UNCLIPPED flat critical_demand_w (the
     bug this fix avoids) raises when forecast demand dips below the
     11600W baseline; the CLIPPED version (what worker.py now computes)
     does not raise for that same reason, for any demand level.

Does not modify GAP19, ECD, OptionD, the simulator, or any forecasting
model. Uses GAP19's `terminal_reserve_model: "INITIAL_STATE"` governed
fallback (an existing, named GAP19 config option -- not an invented
value) to get past the unrelated terminal_target_wh requirement so
these tests can reach a real solve.
"""
import math
from datetime import datetime, timedelta

import pytest
import yaml

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

CANONICAL_BASELINE_POWER_W = 11600.0  # must match system/config/loads.yaml critical_load.baseline_power_w


def _load_canonical_baseline_from_yaml() -> float:
    with open("system/config/loads.yaml") as f:
        loads_cfg = yaml.safe_load(f)
    return float(loads_cfg["critical_load"]["baseline_power_w"])


def _make_bundle(demand_flat_w: float, origin: str = "2024-01-01T00:00:00Z") -> ForecastBundle:
    origin_dt = datetime.fromisoformat(origin.replace("Z", "+00:00"))
    ts = [(origin_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]
    demand = [demand_flat_w] * 24
    return ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=origin,
        horizon_hours=24,
        timestamps=ts,
        solar_irradiance=TimeseriesForecast([0.0] * 24, [0.0] * 24, [0.0] * 24, "W/m^2"),
        solar_generation=TimeseriesForecast([0.0] * 24, [0.0] * 24, [0.0] * 24, "W"),
        wind_generation=TimeseriesForecast([0.0] * 24, [0.0] * 24, [0.0] * 24, "W"),
        demand=TimeseriesForecast(demand, demand, demand, "W"),
        metadata={"model_id": "test_demand_critical_config_path"},
    )


def _make_station_state(origin: str = "2024-01-01T00:00:00Z") -> StationState:
    return StationState(
        timestamp=origin,
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=30000.0,
        last_observed_wind_generation=0.0,
    )


def _worker_formula(baseline_w: float, demand_points: list) -> list:
    """Exact replica of the one-line fix in worker.py's Cell B path."""
    return [min(baseline_w, d) for d in demand_points]


def test_canonical_value_matches_loads_yaml():
    """Pin the canonical governed value this fix reads -- no invented constant."""
    assert _load_canonical_baseline_from_yaml() == CANONICAL_BASELINE_POWER_W


def test_config_path_normal_demand_reaches_gap19_solve():
    """Normal demand (>= baseline): worker-computed critical_demand_w passes
    GAP19's top-level config fallback and GAP19 proceeds past the
    MISSING_GOVERNED_INPUT(demand_critical) check (unmodified GAP19 code)."""
    demand_w = 30000.0
    bundle = _make_bundle(demand_w)
    state = _make_station_state()
    critical_demand_w = _worker_formula(CANONICAL_BASELINE_POWER_W, bundle.demand.point)

    assert critical_demand_w == [CANONICAL_BASELINE_POWER_W] * 24  # baseline is below demand here

    opt = GAP19HighsNativeOptimizer()
    config = {
        "critical_demand_w": critical_demand_w,
        "terminal_reserve_model": "INITIAL_STATE",  # existing GAP19 governed fallback, not invented
    }
    plan = opt.optimize(bundle, state, config)
    assert plan.constraint_status in ("OPTIMAL", "OPTIMIZATION_INFEASIBLE_RELAXABLE", "OPTIMIZATION_INFEASIBLE")
    # Specifically: it must NOT be the demand_critical governance error we fixed.
    assert "demand_critical" not in str(plan.constraint_status).lower()


def test_low_demand_edge_case_unclipped_flat_value_raises():
    """Documents the exact bug this fix avoids: a flat (unclipped) critical_demand_w
    at the governed baseline raises when forecast demand dips below it."""
    low_demand_w = 5000.0  # below the 11600W baseline
    bundle = _make_bundle(low_demand_w)
    state = _make_station_state()

    opt = GAP19HighsNativeOptimizer()
    unclipped = [CANONICAL_BASELINE_POWER_W] * 24

    with pytest.raises(ValueError, match="Protected critical load .* exceeds total demand"):
        opt.optimize(bundle, state, {"critical_demand_w": unclipped, "terminal_reserve_model": "INITIAL_STATE"})


def test_low_demand_edge_case_clipped_worker_formula_does_not_raise_on_critical_load():
    """The actual worker.py fix (min-clipped) must never trigger the
    'exceeds total demand' error, at any demand level, including below baseline."""
    low_demand_w = 5000.0
    bundle = _make_bundle(low_demand_w)
    state = _make_station_state()
    critical_demand_w = _worker_formula(CANONICAL_BASELINE_POWER_W, bundle.demand.point)

    assert critical_demand_w == [low_demand_w] * 24  # clipped down to demand itself
    assert all(cp <= dp for cp, dp in zip(critical_demand_w, bundle.demand.point))
    assert all(cp >= 0.0 and not math.isnan(cp) and not math.isinf(cp) for cp in critical_demand_w)

    opt = GAP19HighsNativeOptimizer()
    plan = opt.optimize(bundle, state, {
        "critical_demand_w": critical_demand_w,
        "terminal_reserve_model": "INITIAL_STATE",
    })
    # Must get past the critical-load governance check; result may still be
    # infeasible for other physical reasons, but never due to demand_critical.
    assert "demand_critical" not in str(plan.constraint_status).lower()
    assert "exceeds total demand" not in str(plan.constraint_status).lower()


def test_clipped_formula_is_always_safe_for_arbitrary_demand_profiles():
    """Property check across a range of demand levels (above, at, and below
    baseline): the clipped worker formula never violates cp <= dp or cp < 0."""
    for demand_w in [0.0, 100.0, 11600.0, 11599.99, 20000.0, 45000.0]:
        points = [demand_w] * 24
        clipped = _worker_formula(CANONICAL_BASELINE_POWER_W, points)
        for cp, dp in zip(clipped, points):
            assert cp >= 0.0
            assert cp <= dp + 1e-9
