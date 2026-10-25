"""
Synthetic/unit tests for the forensic planned-capture module (EXP-PLANNER-CF-CONSISTENCY-2025, §16.5).

No real origin, no population replay, no campaign. The one solve uses a fake 2099 origin.
"""

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(EXP))

import forensic_planned_capture as fp  # noqa: E402
import oracle_runner as oracle  # noqa: E402

# Planned 24-hour horizon at origin 46, step 11 (printed by the targeted replay; rounded to 0.1 W).
O46_SOLAR = [35795.2, 35392.3, 33426.3, 30435.9, 26539.5, 13381.9, 2857.4, 2452.3, 2047.6, 1716.6, 1301.4, 1008.9,
             1167.2, 1624.9, 2557.4, 4531.3, 7520.8, 11543.9, 16189.1, 20987.4, 25426.9, 28758.9, 26242.9, 29599.5]
O46_WIND = [4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0,
            4500.0, 7000.0, 8830.1, 9500.0, 8830.1, 7000.0, 4500.0, 2000.0, 169.9, 0.0, 169.9, 2000.0]
O46_DEMAND = [12000.0, 12102.2, 12401.9, 12878.7, 13500.0, 14223.5, 15000.0, 15776.5, 16500.0, 17121.3, 17598.1,
              17897.8, 18000.0, 17897.8, 17598.1, 17121.3, 16500.0, 15776.5, 15000.0, 14223.5, 13500.0, 12878.7,
              12401.9, 12102.2]
O46_PCHG = [21119.9, 30290.1, 29854.5, 27057.3, 21869.7, 6158.4] + [0.0] * 11 + [2767.4, 5689.1, 8763.8, 12096.8,
            15880.2, 14010.9, 19497.3]
O46_PCURT = [7175.3] + [0.0] * 23
O46_DIS = [0.0] * 6 + [7642.6, 11324.1, 14282.5, 15404.8, 16126.9, 14888.9, 12332.8, 9272.8, 6210.6, 3090.0,
                       149.1] + [0.0] * 7
O46_DIESEL = [0.0] * 24
O46_SERVED = O46_DEMAND[:]  # served = demand, no unmet, all hours (planned)


def _o46_horizon():
    return {"forecast_solar": O46_SOLAR, "forecast_wind": O46_WIND, "P_discharge": O46_DIS,
            "P_diesel": O46_DIESEL, "P_served": O46_SERVED, "P_curt": O46_PCURT, "P_charge": O46_PCHG,
            "demand": O46_DEMAND}


# ---------------------------------------------------------------------------
# Authorization and no-overwrite guard
# ---------------------------------------------------------------------------

def test_requires_authorization():
    with pytest.raises(PermissionError):
        fp.run_forensic_capture(authorized=False, timestamp="unit_noauth")


def test_refuses_to_overwrite_existing_forensic_directory():
    ts = "unit_exists_guard"
    d = EXP / f"forensic_planned_capture_{ts}"
    d.mkdir()
    try:
        with pytest.raises(FileExistsError):
            fp.run_forensic_capture(authorized=True, timestamp=ts)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_never_targets_original_oracle_outputs():
    src = (EXP / "forensic_planned_capture.py").read_text()
    assert "forensic_planned_capture_" in src
    for name in ("ORACLE_PHYS_HOURLY.csv", "ORACLE_CTRL_HOURLY.csv", "ORACLE_AUDIT_REPORT.json"):
        assert f'out_dir / "{name}"' not in src


# ---------------------------------------------------------------------------
# Reproduction check against the original ORACLE_PHYS rows
# ---------------------------------------------------------------------------

def _pair(n=3, noise=0.0):
    rep = pd.DataFrame({"origin_id": [1] * n, "step": list(range(n)),
                        "R_charge": [100.0 + noise, 200.0, 300.0], "R_discharge": [0.0] * n,
                        "P_diesel": [0.0] * n, "R_served": [1.0] * n, "R_unmet": [0.0] * n,
                        "R_fuel": [0.0] * n, "R_soc_after": [50.0] * n, "R_solar": [0.0] * n,
                        "R_wind": [0.0] * n, "R_demand": [1.0] * n})
    orig = pd.DataFrame({"origin_id": [1] * n, "step": list(range(n)),
                         "charge_w": [100.0, 200.0, 300.0], "discharge_w": [0.0] * n, "diesel_w": [0.0] * n,
                         "served_w": [1.0] * n, "unmet_w": [0.0] * n, "fuel_l": [0.0] * n,
                         "soc_pct": [50.0] * n, "solar_w": [0.0] * n, "wind_w": [0.0] * n, "demand_w": [1.0] * n})
    return rep, orig


def test_reproduction_passes_on_identical_rows():
    rep, orig = _pair()
    assert fp.compare_to_original(rep, orig)["PASS"] is True


def test_reproduction_fails_on_any_altered_field():
    rep, orig = _pair(noise=0.5)
    r = fp.compare_to_original(rep, orig)
    assert r["PASS"] is False and r["max_abs_diff"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Classification rules (A/B/C/D/E) on synthetic flags
# ---------------------------------------------------------------------------

def _flags(**kw):
    base = dict(data_error=False, executor_dev=False, starvation=False, pcc=False)
    base.update(kw)
    return base


@pytest.mark.parametrize("flags,expected", [
    (_flags(data_error=True), "D"),
    (_flags(executor_dev=True), "A"),
    (_flags(pcc=True), "B"),
    (_flags(starvation=True), "C"),
    (_flags(starvation=True, pcc=True), "C"),
    (_flags(executor_dev=True, pcc=True), "C"),
    (_flags(), "E"),
    (_flags(data_error=True, pcc=True), "D"),
])
def test_classification_rules(flags, expected):
    assert fp.classify_row(flags)["class"] == expected


def test_greedy_alternative_reproduces_origin46_tie():
    alt = fp.greedy_alternative_curtailment(_o46_horizon(), e_start_wh=64558.2, e_max_wh=190000.0)
    plan_total = sum(O46_PCURT)
    assert plan_total == pytest.approx(7175.3, abs=0.05)
    assert abs(alt["alt_total_curtailment_wh"] - plan_total) <= fp.TIE_TOL_WH + 5.0  # rounded horizon inputs
    tie = fp.planner_curtailment_tie(_o46_horizon(), 64558.2, 190000.0, plan_total)
    assert tie["equal_cost_tie"] is True


def test_greedy_alternative_charges_first_hour_at_surplus():
    alt = fp.greedy_alternative_curtailment(_o46_horizon(), 64558.2, 190000.0)
    assert alt["alt_charge_w"][0] == pytest.approx(28295.2, abs=0.2)


def _row(**kw):
    horizon = {"forecast_solar": O46_SOLAR, "forecast_wind": O46_WIND, "P_discharge": O46_DIS,
               "P_diesel": O46_DIESEL, "P_served": O46_SERVED, "P_curt": O46_PCURT,
               "P_soc_pct": [50.0] * 24, "P_solar_used": [0.0] * 24, "P_wind_used": [0.0] * 24, "demand": O46_DEMAND}
    base = dict(origin_id=46, step=11, route="EMERGENCY", solver_status="HighsModelStatus.kOptimal",
                E_before_wh=64558.2, fuel_before_l=100.0, demand_w=12000.0, solar_w=35795.2, wind_w=4500.0,
                forecast_solar_w=35795.2, forecast_wind_w=4500.0,
                P_charge_w=21119.94, R_charge_w=28295.2, P_curt_w=7175.26, R_curt_w=0.0,
                P_discharge_w=0.0, R_discharge_w=0.0, P_diesel_w=0.0, R_diesel_w=0.0,
                P_served_w=12000.0, R_served_w=12000.0, P_unmet_w=0.0, R_unmet_w=0.0,
                P_solar_used_w=28619.94, P_wind_used_w=4500.0, charge_cap_w=50000.0, room_ac_w=136349.8,
                R_fuel_l=0.0, R_fuel_after_l=0.0, R_busbar_err_w=0.0, R_E_after_wh=90580.0,
                horizon_json=__import__("json").dumps(horizon))
    base.update(kw)
    return pd.Series(base)


def test_origin46_row_classified_B_with_equal_cost_tie():
    df = pd.DataFrame([_row()])
    out = fp.classify_all(df, e_max_wh=190000.0)
    assert len(out) == 1
    r = out.iloc[0]
    assert r["class"] == "B" and bool(r["pcc"]) and bool(r["equal_cost_tie"])
    assert bool(r["executor_dev"]) is False and bool(r["starvation"]) is False


def test_starvation_row_classified_C():
    # Planned balance closes: solar_used 0 + wind 4500 + diesel 16305.87 = served 18000 + charge 2805.87.
    row = _row(P_charge_w=2805.87, R_charge_w=1349.56, P_diesel_w=16305.87, R_diesel_w=14849.2,
               R_fuel_l=8.7123, fuel_before_l=8.7123, P_curt_w=0.0, P_solar_used_w=0.0,
               P_served_w=18000.0, demand_w=18000.0, solar_w=0.36, wind_w=4500.0, E_before_wh=140000.0,
               charge_cap_w=50000.0, P_discharge_w=0.0, R_discharge_w=0.0, R_busbar_err_w=0.0,
               P_wind_used_w=4500.0, room_ac_w=40000.0)
    out = fp.classify_all(pd.DataFrame([row]), e_max_wh=190000.0)
    assert out.iloc[0]["starvation"] == True  # noqa: E712 (numpy bool)
    assert out.iloc[0]["class"] == "C"


def test_non_optimal_solve_classified_D():
    out = fp.classify_all(pd.DataFrame([_row(solver_status="HighsModelStatus.kInfeasible")]), 190000.0)
    assert out.iloc[0]["class"] == "D"


def test_rows_within_tolerance_are_excluded():
    out = fp.classify_all(pd.DataFrame([_row(P_charge_w=28295.5, R_charge_w=28295.2)]), 190000.0)
    assert len(out) == 0


# ---------------------------------------------------------------------------
# Capture loop on a FAKE 2099 origin (synthetic; exercises the real solver once)
# ---------------------------------------------------------------------------

def test_capture_origin_on_fake_origin_is_optimal_and_identities_hold():
    origin = pd.Timestamp("2099-01-01")
    lookup = {(origin + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S"): 300.0 for j in range(0, 60)}
    cfg = dict(oracle.canonical_configs())
    # Explicit SYNTHETIC test-fixture authorization for the router/ECD
    # fail-closed contract (ECD-01, A-iii/B-iii). This test exercises the
    # real solver on a fake 2099 origin to check solver/identity
    # invariants, not the authorization gate itself.
    # "EVID-TEST-FORENSIC-PLANNED-CAPTURE" is NOT a real-station evidence
    # record -- see tests/test_isolated_components.py for the convention.
    cfg.setdefault("ecd", {}).update({"t_required_hours": 6.0, "t_required_authorized": True})
    cfg.setdefault("critical_load", {}).update({
        "authorized": True,
        "evidence_id": "EVID-TEST-FORENSIC-PLANNED-CAPTURE",
        "authorized_critical_load_w": 5000.0,
    })
    rows = fp.capture_origin(origin, 999, lookup, cfg)
    assert len(rows) == 24
    assert all(r["solver_status"] == "HighsModelStatus.kOptimal" for r in rows)
    for r in rows:
        planned_balance = r["P_solar_used_w"] + r["P_wind_used_w"] + r["P_discharge_w"] + r["P_diesel_w"] \
            - r["P_served_w"] - r["P_charge_w"]
        assert abs(planned_balance) < 1e-2
        assert abs(r["R_busbar_err_w"]) <= 1e-3
        assert r["R_soc_after_pct"] >= 19.999 - 1e-9 and r["R_soc_after_pct"] <= 95.001 + 1e-9
    assert rows[0]["E_before_wh"] == pytest.approx(100000.0)
    for k in range(1, 24):
        assert rows[k]["E_before_wh"] == pytest.approx(rows[k - 1]["R_E_after_wh"], abs=1e-6)
