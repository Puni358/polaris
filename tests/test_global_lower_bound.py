"""
Synthetic tests for the per-origin global relaxed lower bound (EXP-PLANNER-CF-CONSISTENCY-2025,
Study 1 governance K1–K8). No real 2025 origin, no oracle, no campaign, no production code.

Charging from diesel is NOT dominated: the 5 L/h base cost is paid per on-hour, so extra diesel
power in an hour that is already on is cheap at the margin, and the battery can store it. The
expected values below were derived with that in mind.
"""

import copy
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import linprog

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
sys.path.insert(0, str(EXP))

import global_lower_bound as g  # noqa: E402

Z = [0.0] * 24


def inst(oid=1, S=None, W=None, D=None, e0=100000.0):
    return g.OriginInputs(oid, S if S is not None else Z, W if W is not None else Z,
                          D if D is not None else Z, e0)


def one_hour(value, hours=1):
    return [value] * hours + [0.0] * (24 - hours)


def solve_cert(i, **kw):
    r = g.solve_origin(i, **kw)
    return r, g.certify_origin(r, i)


def brute_lp(D, e0):
    """Independent check on instances with no renewables. Enumerates diesel on/off and
    charge/discharge/idle modes over the active hours and solves each pattern as an LP (scipy).
    Hours with zero demand are provably unused: no later demand exists to be served from storage."""
    act = [t for t in range(len(D)) if D[t] > 0.0]
    n = len(act)
    emin = g.E_MIN_WH - g.SOC_MARGIN_WH
    emax = g.E_MAX_WH + g.SOC_MARGIN_WH
    best = np.inf
    for ys in itertools.product([0, 1], repeat=n):
        for modes in itertools.product([0, 1, 2], repeat=n):  # 0 idle, 1 charge, 2 discharge
            nv = 3 * n  # per active hour: d, ch, dis
            c = np.zeros(nv)
            fixed = 0.0
            bounds = []
            for k, t in enumerate(act):
                dmax = min(g.DIESEL_MAX_W, D[t] + g.BATTERY_POWER_W) if ys[k] else 0.0
                chm = g.BATTERY_POWER_W if modes[k] == 1 else 0.0
                dism = g.BATTERY_POWER_W if modes[k] == 2 else 0.0
                bounds += [(0.0, dmax), (0.0, chm), (0.0, dism)]
                c[3 * k] = g.MARGINAL_FUEL_L_PER_WH
                fixed += g.BASE_FUEL_L_PER_H * ys[k]
            A_eq = np.zeros((n, nv))
            b_eq = np.zeros(n)
            for k, t in enumerate(act):
                A_eq[k, 3 * k] = 1.0       # d
                A_eq[k, 3 * k + 1] = -1.0  # -ch
                A_eq[k, 3 * k + 2] = 1.0   # +dis
                b_eq[k] = D[t]
            A_ub, b_ub = [], []
            for j in range(1, n + 1):
                row = np.zeros(nv)
                for i in range(j):
                    row[3 * i + 1] = g.ETA_CHG
                    row[3 * i + 2] = -1.0 / g.ETA_DIS
                A_ub.append(row)
                b_ub.append(emax - e0)
                A_ub.append(-row)
                b_ub.append(e0 - emin)
            res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method="highs")
            if res.status == 0:
                best = min(best, res.fun + fixed)
    return best


CASES = [
    inst(S=[20000.0] * 24, D=[15000.0] * 24),                 # renewables cover demand
    inst(D=one_hour(15000.0), e0=40000.0),                    # short diesel-required run
    inst(D=one_hour(5000.0), e0=40000.0),                     # 5 kW deficit, no 10 kW minimum
    inst(S=[5000.0] * 24, D=[15000.0] * 24, e0=40000.0),      # partial renewables
    inst(S=[12000.0] * 24, D=[15000.0] * 24, e0=40000.0),     # small deficit over 24 h
    inst(D=one_hour(20000.0, 17), e0=40000.0),                # 340 kWh over 17 h
]


# ---------------------------------------------------------------------------
# 1–9: required formulation cases
# ---------------------------------------------------------------------------

def test_01_simple_no_diesel_case():
    r, c = solve_cert(inst(S=[20000.0] * 24, D=[15000.0] * 24))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] == pytest.approx(0.0, abs=1e-9)
    assert r["checks"]["diesel_on_hours"] == 0


def test_02_diesel_required_case():
    # One hour of 15 kW, no renewables, battery at the SOC floor. The only battery energy available
    # is the 2 Wh margin, so diesel carries about 15 kW for 5 + 0.00025 * 15,000 = 8.75 L.
    r, c = solve_cert(inst(D=one_hour(15000.0), e0=40000.0))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] == pytest.approx(5.0 + 0.00025 * (15000.0 - 1.84), abs=1e-3)
    assert r["checks"]["diesel_on_hours"] == 1


def test_03_battery_discharge_case():
    r, c = solve_cert(inst(D=one_hour(15000.0)))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] == pytest.approx(0.0, abs=1e-9)
    assert r["checks"]["diesel_on_hours"] == 0


def test_04_battery_charge_and_curtailment_case():
    S = [50000.0] + [0.0] * 23
    D = one_hour(10000.0)
    r, c = solve_cert(inst(S=S, D=D))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] == pytest.approx(0.0, abs=1e-9)
    assert r["checks"]["busbar_residual_max_w"] <= g.BUS_TOL_W
    x = np.array(r["x_list"])
    assert x[g._col(0, g.COL_CH)] <= min(g.BATTERY_POWER_W,
                                          (g.E_MAX_WH + g.SOC_MARGIN_WH - 100000.0) / g.ETA_CHG) + 1e-6


def test_05_full_service_enforcement_case():
    r, c = solve_cert(inst(S=[5000.0] * 24, D=[15000.0] * 24, e0=40000.0))
    assert c["certification"] == "CERTIFIED"
    assert r["checks"]["zero_unmet"] is True and r["checks"]["no_unmet_variables"] is True
    assert r["checks"]["busbar_residual_max_w"] <= g.BUS_TOL_W


def test_06_fuel_inventory_relaxation_case():
    # 340 kWh of demand with no renewables and no stored energy. Diesel energy must be at least the
    # demand energy, and the hours it runs must be at least E_d / 100 kW. The fuel is therefore at
    # least 0.00025 * 340,000 + 5 * 3.4 = 102.0 L, which exceeds the 100 L inventory.
    r, c = solve_cert(inst(D=one_hour(20000.0, 17), e0=40000.0))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] > 100.0
    assert c["U_o"] >= 0.00025 * 340000.0 + 5.0 * 3.4 - 1e-6
    assert c["L_o"] <= c["U_o"] + 1e-9


def test_07_ten_kw_diesel_minimum_relaxation_case():
    # 5 kW deficit for one hour. With the 10 kW minimum, diesel would run at 10 kW and charge 5 kW
    # into the battery, costing 5 + 0.00025 * 10,000 = 7.5 L. The relaxed bound runs 5 kW: 6.25 L.
    r, c = solve_cert(inst(D=one_hour(5000.0), e0=40000.0))
    assert c["certification"] == "CERTIFIED"
    x = np.array(r["x_list"])
    d0 = x[g._col(0, g.COL_D)]
    assert d0 < 10000.0 - 1.0
    assert c["U_o"] == pytest.approx(5.0 + 0.00025 * (5000.0 - 1.84), abs=1e-3)
    assert c["U_o"] < 5.0 + 0.00025 * 10000.0 - 1.0


def test_08_no_terminal_soc_case():
    # The battery serves 45 kWh and ends at about 51 %. A terminal target of 100 kWh would force charging.
    r, c = solve_cert(inst(D=[15000.0] * 3 + [0.0] * 21))
    assert c["certification"] == "CERTIFIED"
    assert c["U_o"] == pytest.approx(0.0, abs=1e-9)
    x = np.array(r["x_list"])
    assert x[g._e_col(24)] == pytest.approx(100000.0 - 45000.0 / g.ETA_DIS, abs=1e-3)
    assert r["has_terminal_row"] is False


def test_09_zero_vs_two_litre_startup_diagnostic():
    r, c = solve_cert(inst(D=one_hour(15000.0), e0=40000.0))
    assert c["certification"] == "CERTIFIED"
    primary = c["U_o"]
    starts = r["checks"]["starts"]
    assert starts == 1
    assert g.STARTUP_FUEL_L_PRIMARY == 0.0
    assert primary + g.STARTUP_FUEL_L_DIAGNOSTIC * starts == pytest.approx(primary + 2.0)


def test_10_tiny_instance_matches_independent_enumeration():
    D = one_hour(30000.0, 3)
    e0 = 100000.0
    brute = brute_lp(D, e0)
    r, c = solve_cert(inst(D=D, e0=e0))
    assert c["certification"] == "CERTIFIED"
    assert r["primal"] == pytest.approx(brute, abs=1e-6)
    assert c["L_o"] <= brute + 1e-6


def test_13_soc_plus_minus_2wh_margin_is_used():
    assert g.SOC_MARGIN_WH == 2.0
    model = g.build_model(inst())
    assert model.lb[g._e_col(5)] == pytest.approx(g.E_MIN_WH - 2.0)
    assert model.ub[g._e_col(5)] == pytest.approx(g.E_MAX_WH + 2.0)
    # with the battery at the floor, the solver uses the 2 Wh margin exactly
    r, c = solve_cert(inst(D=one_hour(15000.0), e0=40000.0))
    assert r["checks"]["soc_min_wh"] == pytest.approx(g.E_MIN_WH - g.SOC_MARGIN_WH, abs=1e-3)


# ---------------------------------------------------------------------------
# 11–16: invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("i", CASES)
def test_11_dual_bound_not_above_primal(i):
    r, c = solve_cert(i)
    assert c["certification"] == "CERTIFIED"
    assert c["L_o"] <= c["U_o"] + 1e-6


def test_12_deterministic_repeated_solve():
    i = inst(D=one_hour(15000.0), e0=40000.0)
    a = g.solve_origin(i)
    b = g.solve_origin(i)
    assert a["primal"] == b["primal"] and a["dual"] == b["dual"]
    assert a["x_list"] == b["x_list"]


@pytest.mark.parametrize("i", CASES)
def test_14_busbar_and_accounting_identity(i):
    r, c = solve_cert(i)
    chk = r["checks"]
    assert chk["busbar_residual_max_w"] <= g.BUS_TOL_W
    assert chk["battery_residual_max_wh"] <= g.BATT_TOL_WH
    assert chk["recompute_ok"] is True
    assert chk["recompute_diff_l"] <= g.RECOMPUTE_TOL_L


@pytest.mark.parametrize("i", CASES)
def test_15_zero_unmet_invariant(i):
    r, c = solve_cert(i)
    assert r["checks"]["zero_unmet"] is True
    assert not any(str(n).startswith("unmet") for n in g.build_model(i).names)


def test_16_origins_are_independent_and_share_no_state():
    a = inst(oid=1, D=one_hour(15000.0), e0=40000.0)
    b = inst(oid=2, S=[20000.0] * 24, D=[15000.0] * 24)
    before = {k: copy.deepcopy(v) for k, v in vars(g).items()
              if isinstance(v, (list, dict, set)) and not k.startswith("__")}
    g.solve_origin(a)
    rb_after_a = g.solve_origin(b)
    rb_alone = g.solve_origin(b)
    assert rb_after_a["primal"] == rb_alone["primal"]
    assert rb_after_a["x_list"] == rb_alone["x_list"]
    g.solve_origin(inst(oid=1, D=one_hour(5000.0), e0=40000.0))  # change A's inputs
    assert g.solve_origin(b)["primal"] == rb_alone["primal"]
    after = {k: v for k, v in vars(g).items() if isinstance(v, (list, dict, set)) and not k.startswith("__")}
    assert set(after) == set(before)
    for k in before:
        assert after[k] == before[k], f"module-level mutable state changed: {k}"


# ---------------------------------------------------------------------------
# Governance edge cases (certification rule, K6/K7)
# ---------------------------------------------------------------------------

def _good(i=None):
    i = i or inst(D=one_hour(15000.0), e0=40000.0)
    return g.solve_origin(i), i


def test_gap_above_limit_is_blocked():
    r, i = _good()
    r = dict(r)
    r["dual"] = r["primal"] - 0.5
    c = g.certify_origin(r, i)
    assert c["certification"] == "BLOCKED"
    assert any("absolute gap" in x for x in c["reasons"])


def test_gap_at_limit_is_certified():
    r, i = _good()
    r = dict(r)
    r["dual"] = r["primal"] - g.GAP_LIMIT_L
    assert g.certify_origin(r, i)["certification"] == "CERTIFIED"


def test_time_limited_hard_origin_is_blocked_not_coerced():
    # Full 24 h, 18 kW, no renewables: HiGHS does not close the 0.01 L gap in one second.
    i = inst(D=[18000.0] * 24, e0=40000.0)
    r = g.solve_origin(i, time_limit_s=1.0)
    c = g.certify_origin(r, i)
    assert c["certification"] == "BLOCKED"


def test_no_dual_bound_is_blocked():
    r, i = _good()
    r = dict(r)
    r["dual"] = None
    c = g.certify_origin(r, i)
    assert c["certification"] == "BLOCKED" and "no dual bound" in c["reasons"]


def test_primal_infeasible_is_blocked():
    D = one_hour(200000.0)  # 200 kW exceeds diesel (100 kW) + battery (50 kW) + renewables (0)
    r = g.solve_origin(inst(D=D))
    c = g.certify_origin(r, inst(D=D))
    assert c["certification"] == "BLOCKED"
    assert "no feasible incumbent" in c["reasons"]


def test_objective_recomputation_mismatch_is_blocked():
    r, i = _good()
    r = dict(r)
    r["primal"] = r["primal"] + 0.5
    r["dual"] = r["primal"] - 0.001
    c = g.certify_origin(r, i)
    assert c["certification"] == "BLOCKED"
    assert any("recomputation" in x for x in c["reasons"])


def test_unmet_service_is_blocked():
    # Inject unserved load by cutting the renewable supply used in hour 0 by 100 W.
    r, i = _good()
    r = copy.deepcopy(r)
    r["x"] = np.array(r["x"])
    r["x"][g._col(0, g.COL_S)] -= 100.0
    c = g.certify_origin(r, i)
    assert c["certification"] == "BLOCKED"
    assert any("service not fully served" in x for x in c["reasons"])


def test_terminal_target_in_model_fails_the_test():
    # The standard formulation must carry no terminal row. A model that did would fail here.
    model = g.build_model(inst())
    assert g._has_terminal_row(model) is False
    model.rows.append({"name": "terminal", "lhs": 100000.0, "rhs": np.inf,
                       "idx": [g._e_col(g.T_HOURS)], "coef": [1.0]})
    assert g._has_terminal_row(model) is True
    r, i = _good()
    r = dict(r)
    r["has_terminal_row"] = True
    assert g.certify_origin(r, i)["certification"] == "BLOCKED"


def test_startup_fuel_in_primary_objective_fails_the_test():
    assert g.STARTUP_FUEL_L_PRIMARY == 0.0
    model = g.build_model(inst())
    assert not any("start" in str(n) for n in model.names)
    assert all(model.cost[j] == 0.0 for j, nm in enumerate(model.names) if "start" in str(nm))


def test_ng7_symbolic_rule_is_not_evaluated_without_real_fuel():
    assert g.ng7_inequality(None, None)["status"] == "NOT_EVALUABLE"
    assert g.ng7_inequality(100.0, None)["status"] == "NOT_EVALUABLE"


def test_ng7_strict_inequality_on_placeholder_numbers():
    # synthetic placeholder numbers only; F_c is not a campaign result
    assert g.ng7_inequality(61.0, 100.0)["status"] == "NG7_TRIGGERED"
    assert g.ng7_inequality(60.0, 100.0)["status"] == "NG7_NOT_TRIGGERED"


def test_aggregate_counts_certified_and_blocked():
    r, i1 = _good(inst(oid=1, D=one_hour(15000.0), e0=40000.0))
    bad = dict(r)
    bad["dual"] = None
    c1 = g.certify_origin(r, i1)
    c2 = g.certify_origin(bad, inst(oid=2))
    agg = g.aggregate([c1, c2])
    assert agg["count_certified"] == 1 and agg["count_blocked"] == 1
    assert agg["blocked_origins"] == [2]
    assert agg["sum_L"] == pytest.approx(c1["L_o"])


def test_config_hash_is_stable_and_declares_no_terminal_or_startup():
    cfg = g.formulation_config()
    assert cfg["terminal"] == "none" and cfg["startup_fuel_l_primary"] == 0.0
    assert g.config_hash() == g.config_hash()
