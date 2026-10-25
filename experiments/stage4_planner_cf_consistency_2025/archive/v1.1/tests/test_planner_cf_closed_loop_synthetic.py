"""
Synthetic closed-loop invariant test for the Planner-CF v1 arm runner (EXP-PLANNER-CF-CONSISTENCY-2025).

Uses a FAKE future origin (forecast_start 2099-01-01 00:00:00) built from synthetic weather rows.
It is NOT one of the 123 preregistered origins and is not an evaluation. It checks that one
closed-loop origin produces 24 hourly rows and 24 executed-hour records, with the invariants the
campaign gates depend on (G2, G3, G4, G6, G10).
"""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import planner_cf_campaign_runner as runner  # noqa: E402
import planned_execution_telemetry as pet  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402
import stage4_low_sun_adapter as s4a  # noqa: E402

FAKE_FS = "2099-01-01 00:00:00"
FAKE_T0 = "2098-12-31T23:00:00Z"


def _synthetic_weather():
    # 72 hourly rows: the causal cloud lookup needs 47 hours past the origin; only the first 24 rows
    # carry the fake forecast_start, so realized inputs for the fake origin are exactly 24 rows.
    ts = pd.date_range("2099-01-01 00:00:00", periods=72, freq="h")
    cloud = np.linspace(10.0, 60.0, 72)
    sw = np.clip(800.0 * np.sin(np.linspace(0, np.pi, 72)), 0, None)
    fs = [FAKE_FS] * 24 + ["2099-01-02 00:00:00"] * 48
    return pd.DataFrame({
        "forecast_start": fs,
        "timestamp": [t.strftime("%Y-%m-%d %H:%M:%S") for t in ts],
        "fc_cloud_cover": cloud,
        "actual_SW_IN": sw,
    })


@pytest.fixture(scope="module")
def pc_control_origin():
    configs, make_initial_state = runner._load_canonical_configs()
    solar = s4a.SolarElevationProvider(runner.DECOMPOSITION_2025_PATH)
    weather = _synthetic_weather()
    rs, rw, rd, rts = runner.realized_inputs_for(weather, FAKE_FS)
    arm = runner.PlannerCFArmRunner(configs, "PC-Control", solar)
    hourly, executed = arm.run_origin(999, make_initial_state(FAKE_T0), weather, rs, rw, rd, rts)
    return hourly, executed


def test_one_origin_produces_24_hourly_and_24_executed_records(pc_control_origin):
    hourly, executed = pc_control_origin
    assert len(hourly) == 24 and len(executed) == 24
    assert [r["hour"] for r in hourly] == list(range(24))
    assert all(r["plan_hour"] == 0 for r in executed)


def test_busbar_and_soc_invariants_hold(pc_control_origin):
    hourly, _ = pc_control_origin
    df = pd.DataFrame(hourly)
    assert gates.g6_busbar_soc_fuel(df)["PASS"] is True
    assert df["busbar_balance_error_w"].abs().max() <= 1e-3


def test_all_solves_optimal_and_route_propagated(pc_control_origin):
    hourly, _ = pc_control_origin
    df = pd.DataFrame(hourly)
    assert gates.g4_optimizer_status(df)["PASS"] is True
    assert gates.g10_route_propagation(df)["PASS"] is True


def test_executed_records_satisfy_G2_and_G3(pc_control_origin):
    _, executed = pc_control_origin
    ex = pd.DataFrame(executed)
    assert gates.g2_priority_inversion(ex)["PASS"] is True
    assert gates.g3_critical_infeasibility(ex)["PASS"] is True


def test_E_t_is_start_of_hour_realized_energy(pc_control_origin):
    hourly, executed = pc_control_origin
    # E_t of hour 0 is the initial state (100,000 Wh). Each later E_t matches the previous realized
    # SOC converted to energy. The SOC in telemetry is rounded to 0.01 %, i.e. up to 10 Wh on 200 kWh,
    # so the tolerance is 10 Wh; E_t itself is the unrounded realized energy.
    assert executed[0]["E_t_wh"] == pytest.approx(100000.0)
    for k in range(1, 24):
        assert executed[k]["E_t_wh"] == pytest.approx(hourly[k - 1]["soc_after"] / 100.0 * 200000.0, abs=10.0)


def test_served_critical_never_exceeds_realized_critical(pc_control_origin):
    hourly, _ = pc_control_origin
    for r in hourly:
        assert r["critical_served_first"] <= r["critical_demand"] + 1e-6
