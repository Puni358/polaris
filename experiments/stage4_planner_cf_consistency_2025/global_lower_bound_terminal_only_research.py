"""
Terminal-only per-origin relaxed lower bound (EXP-PLANNER-CF-CONSISTENCY-2025 diagnostic variant).

RESEARCH-ONLY. Isolated diagnostic module.
Quantifies the effect of restoring ONE soft terminal SOC constraint while keeping EBR fully relaxed.

Base reference:
  Certified lower bound without terminal: 1,397.8483 L
  PC-SW realization reference: 8,729.2446 L
  40% target: 6,118.1827 L

Formulation changes relative to certified lower bound (global_lower_bound.py):
  1. Terminal row added: E[24] + s_term >= 100,000 Wh
  2. Terminal slack: s_term >= 0 with objective penalty coefficient = 1.0 (J2-equivalent)
  3. All other constraints and relaxations preserved:
     - Hard service (critical + noncritical fully served, zero unmet)
     - Initial energy E0 = 100,000 Wh
     - SOC bounds [40000 Wh - 2 Wh, 190000 Wh + 2 Wh]
     - Battery power ±50 kW
     - Charge/discharge exclusivity binaries
     - Diesel max 100 kW with on/off binary
     - 5 L/h on-cost + 0.00025 L/Wh marginal fuel
     - Startup fuel = 0 L
     - Fuel inventory relaxed
     - 10 kW diesel minimum relaxed
     - EBR / reserve REMAIN FULLY RELAXED (no EBR constraints, no reserve slacks)
     - No forecast solar/wind used (same actuals data as base lower bound)
     - HiGHS solver settings identical (threads=1, mip_rel_gap=1e-9, time_limit=60s)
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import highspy
import numpy as np

# ---------------------------------------------------------------------------
# Governed constants (identical to certified lower bound except terminal)
# ---------------------------------------------------------------------------
T_HOURS = 24
CAPACITY_WH = 200000.0
E_MIN_WH = 0.20 * CAPACITY_WH          # 40,000 Wh
E_MAX_WH = 0.95 * CAPACITY_WH          # 190,000 Wh
SOC_MARGIN_WH = 2.0                    # numerical margin
BATTERY_POWER_W = 50000.0
ETA_CHG = 0.92
ETA_DIS = 0.92
DIESEL_MAX_W = 100000.0
BASE_FUEL_L_PER_H = 5.0
MARGINAL_FUEL_L_PER_WH = 0.00025
STARTUP_FUEL_L_PRIMARY = 0.0           # primary accounting
STARTUP_FUEL_L_DIAGNOSTIC = 2.0        # diagnostic only
GAP_LIMIT_L = 0.01                     # absolute per-origin tight-certification gap
TIME_LIMIT_S = 60.0                    # time limit per origin
RECOMPUTE_TOL_L = 1e-6
FEAS_TOL_W = 1e-6
BUS_TOL_W = 1e-3
BATT_TOL_WH = 1e-3

# Terminal-only specification
TERMINAL_TARGET_WH = 100000.0
TERMINAL_PENALTY_COEF = 1.0            # J2-equivalent penalty on s_term
TERMINAL_STATEMENT = "soft_terminal_anchor_E24_plus_s_term_ge_100000_penalty_1.0"

BLOCK_SIZE = 8                          # s, w, ch, dis, bch, bdis, d, y
COL_S, COL_W, COL_CH, COL_DIS, COL_BCH, COL_BDIS, COL_D, COL_Y = range(BLOCK_SIZE)


@dataclass(frozen=True)
class OriginInputs:
    origin_id: int
    solar_w: Sequence[float]
    wind_w: Sequence[float]
    demand_w: Sequence[float]
    e0_wh: float = 100000.0


def formulation_config() -> Dict[str, Any]:
    """Exact configuration used for the formulation hash."""
    return {
        "T": T_HOURS,
        "capacity_wh": CAPACITY_WH,
        "e_min_wh": E_MIN_WH,
        "e_max_wh": E_MAX_WH,
        "soc_margin_wh": SOC_MARGIN_WH,
        "battery_power_w": BATTERY_POWER_W,
        "eta_chg": ETA_CHG,
        "eta_dis": ETA_DIS,
        "diesel_max_w": DIESEL_MAX_W,
        "base_fuel_l_per_h": BASE_FUEL_L_PER_H,
        "marginal_fuel_l_per_wh": MARGINAL_FUEL_L_PER_WH,
        "startup_fuel_l_primary": STARTUP_FUEL_L_PRIMARY,
        "gap_limit_l": GAP_LIMIT_L,
        "terminal": TERMINAL_STATEMENT,
        "terminal_target_wh": TERMINAL_TARGET_WH,
        "terminal_penalty_coef": TERMINAL_PENALTY_COEF,
        "fuel_inventory": "relaxed",
        "diesel_min_w": "relaxed (0)",
        "reserve": "removed",
        "service": "full critical and non-critical; no unmet variables",
    }


def config_hash() -> str:
    blob = json.dumps(formulation_config(), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def _col(t: int, which: int) -> int:
    return t * BLOCK_SIZE + which


def _e_col(t: int) -> int:
    return T_HOURS * BLOCK_SIZE + t


def _s_term_col() -> int:
    return T_HOURS * BLOCK_SIZE + (T_HOURS + 1)


def _n_cols() -> int:
    # 24 * 8 variables + 25 energy states + 1 terminal slack
    return T_HOURS * BLOCK_SIZE + (T_HOURS + 1) + 1


@dataclass
class Model:
    lb: np.ndarray
    ub: np.ndarray
    integral: List[int]
    cost: np.ndarray
    rows: List[Dict[str, Any]] = field(default_factory=list)
    names: List[str] = field(default_factory=list)


def build_model(inp: OriginInputs) -> Model:
    if len(inp.solar_w) != T_HOURS or len(inp.wind_w) != T_HOURS or len(inp.demand_w) != T_HOURS:
        raise ValueError("origin inputs must have 24 hourly values")
    if not (E_MIN_WH - SOC_MARGIN_WH <= inp.e0_wh <= E_MAX_WH + SOC_MARGIN_WH):
        raise ValueError("initial energy outside SOC bounds")

    n = _n_cols()
    lb = np.zeros(n)
    ub = np.zeros(n)
    cost = np.zeros(n)
    integral: List[int] = []
    names = [""] * n

    for t in range(T_HOURS):
        S, W, D = float(inp.solar_w[t]), float(inp.wind_w[t]), float(inp.demand_w[t])
        if min(S, W, D) < 0:
            raise ValueError("negative renewable or demand input")
        for which, label in enumerate(["s", "w", "ch", "dis", "bch", "bdis", "d", "y"]):
            names[_col(t, which)] = f"{label}[{t}]"
        ub[_col(t, COL_S)] = S
        ub[_col(t, COL_W)] = W
        ub[_col(t, COL_CH)] = BATTERY_POWER_W
        ub[_col(t, COL_DIS)] = BATTERY_POWER_W
        ub[_col(t, COL_BCH)] = 1.0
        ub[_col(t, COL_BDIS)] = 1.0
        ub[_col(t, COL_D)] = min(DIESEL_MAX_W, D + BATTERY_POWER_W)
        ub[_col(t, COL_Y)] = 1.0
        integral += [_col(t, COL_BCH), _col(t, COL_BDIS), _col(t, COL_Y)]
        cost[_col(t, COL_Y)] = BASE_FUEL_L_PER_H
        cost[_col(t, COL_D)] = MARGINAL_FUEL_L_PER_WH

    for t in range(T_HOURS + 1):
        names[_e_col(t)] = f"E[{t}]"
        lb[_e_col(t)] = E_MIN_WH - SOC_MARGIN_WH
        ub[_e_col(t)] = E_MAX_WH + SOC_MARGIN_WH
    lb[_e_col(0)] = ub[_e_col(0)] = inp.e0_wh

    # Terminal slack: s_term >= 0, penalty coefficient = 1.0 (J2-equivalent)
    col_st = _s_term_col()
    names[col_st] = "s_term"
    lb[col_st] = 0.0
    ub[col_st] = np.inf
    cost[col_st] = TERMINAL_PENALTY_COEF

    model = Model(lb=lb, ub=ub, integral=integral, cost=cost, names=names)

    for t in range(T_HOURS):
        S, W, D = float(inp.solar_w[t]), float(inp.wind_w[t]), float(inp.demand_w[t])
        # Busbar balance: s + w + dis + d - ch = D
        model.rows.append({
            "name": f"busbar[{t}]",
            "lhs": D,
            "rhs": D,
            "idx": [_col(t, COL_S), _col(t, COL_W), _col(t, COL_DIS), _col(t, COL_D), _col(t, COL_CH)],
            "coef": [1.0, 1.0, 1.0, 1.0, -1.0],
        })
        # Battery energy transition: E[t+1] - E[t] - eta_chg*ch + dis/eta_dis = 0
        model.rows.append({
            "name": f"battery[{t}]",
            "lhs": 0.0,
            "rhs": 0.0,
            "idx": [_e_col(t + 1), _e_col(t), _col(t, COL_CH), _col(t, COL_DIS)],
            "coef": [1.0, -1.0, -ETA_CHG, 1.0 / ETA_DIS],
        })
        # Charge / discharge tied to binaries
        model.rows.append({
            "name": f"charge_bin[{t}]",
            "lhs": -np.inf,
            "rhs": 0.0,
            "idx": [_col(t, COL_CH), _col(t, COL_BCH)],
            "coef": [1.0, -BATTERY_POWER_W],
        })
        model.rows.append({
            "name": f"discharge_bin[{t}]",
            "lhs": -np.inf,
            "rhs": 0.0,
            "idx": [_col(t, COL_DIS), _col(t, COL_BDIS)],
            "coef": [1.0, -BATTERY_POWER_W],
        })
        model.rows.append({
            "name": f"exclusivity[{t}]",
            "lhs": -np.inf,
            "rhs": 1.0,
            "idx": [_col(t, COL_BCH), _col(t, COL_BDIS)],
            "coef": [1.0, 1.0],
        })
        # Diesel on/off
        model.rows.append({
            "name": f"diesel_on[{t}]",
            "lhs": -np.inf,
            "rhs": 0.0,
            "idx": [_col(t, COL_D), _col(t, COL_Y)],
            "coef": [1.0, -min(DIESEL_MAX_W, D + BATTERY_POWER_W)],
        })

    # Exact one-shot soft terminal anchor row: E[24] + s_term >= 100000 Wh
    model.rows.append({
        "name": "terminal_soc",
        "lhs": TERMINAL_TARGET_WH,
        "rhs": np.inf,
        "idx": [_e_col(T_HOURS), _s_term_col()],
        "coef": [1.0, 1.0],
    })

    return model


def _solve(model: Model, time_limit_s: float, mip_rel_gap: float) -> Dict[str, Any]:
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("time_limit", float(time_limit_s))
    h.setOptionValue("mip_rel_gap", float(mip_rel_gap))
    n = len(model.lb)
    h.addVars(n, model.lb, model.ub)
    for j in model.integral:
        h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
    for j in range(n):
        if model.cost[j] != 0.0:
            h.changeColCost(j, float(model.cost[j]))
    for r in model.rows:
        lhs = -highspy.kHighsInf if r["lhs"] == -np.inf else float(r["lhs"])
        rhs = highspy.kHighsInf if r["rhs"] == np.inf else float(r["rhs"])
        h.addRow(lhs, rhs, len(r["idx"]), np.array(r["idx"], dtype=np.int32), np.array(r["coef"], dtype=np.float64))
    h.run()
    status = str(h.getModelStatus())
    info = h.getInfo()
    sol = h.getSolution()
    has_incumbent = (
        info.primal_solution_status == highspy.SolutionStatus.kSolutionStatusFeasible
        and len(sol.col_value) == n
    )
    x = np.array(sol.col_value) if has_incumbent else None
    raw_dual = float(info.mip_dual_bound)
    dual = raw_dual if (np.isfinite(raw_dual) and status != str(highspy.HighsModelStatus.kInfeasible)) else None
    return {
        "status": status,
        "x": x,
        "primal": float(info.objective_function_value) if x is not None else None,
        "dual": dual,
        "mip_gap": float(info.mip_gap),
    }


def independent_checks(inp: OriginInputs, x: np.ndarray, primal_obj: float, model_names: Sequence[str]) -> Dict[str, Any]:
    """Recomputes everything from the incumbent without trusting the solver's objective or rows."""
    res: Dict[str, Any] = {}
    S = np.asarray(inp.solar_w, float)
    W = np.asarray(inp.wind_w, float)
    D = np.asarray(inp.demand_w, float)
    s = np.array([x[_col(t, COL_S)] for t in range(T_HOURS)])
    w = np.array([x[_col(t, COL_W)] for t in range(T_HOURS)])
    ch = np.array([x[_col(t, COL_CH)] for t in range(T_HOURS)])
    dis = np.array([x[_col(t, COL_DIS)] for t in range(T_HOURS)])
    d = np.array([x[_col(t, COL_D)] for t in range(T_HOURS)])
    y = np.array([x[_col(t, COL_Y)] for t in range(T_HOURS)])
    bch = np.array([x[_col(t, COL_BCH)] for t in range(T_HOURS)])
    bdis = np.array([x[_col(t, COL_BDIS)] for t in range(T_HOURS)])
    E = np.array([x[_e_col(t)] for t in range(T_HOURS + 1)])
    s_term = float(x[_s_term_col()])

    # Busbar balance
    busbar = s + w + dis + d - ch - D
    res["busbar_residual_max_w"] = float(np.max(np.abs(busbar)))

    # Battery transition
    batt = E[1:] - E[:-1] - ETA_CHG * ch + dis / ETA_DIS
    res["battery_residual_max_wh"] = float(np.max(np.abs(batt)))
    res["soc_min_wh"] = float(E.min())
    res["soc_max_wh"] = float(E.max())
    res["soc_min_pct"] = float(E.min() / CAPACITY_WH * 100.0)
    res["soc_max_pct"] = float(E.max() / CAPACITY_WH * 100.0)

    # Terminal constraint: E[24] + s_term >= 100000 Wh
    e24 = float(E[T_HOURS])
    res["e24_wh"] = e24
    res["s_term_value"] = s_term
    terminal_lhs = e24 + s_term
    terminal_deficit = max(0.0, TERMINAL_TARGET_WH - terminal_lhs)
    res["terminal_residual_wh"] = float(terminal_deficit)

    soc_ok = bool(
        E.min() >= E_MIN_WH - SOC_MARGIN_WH - FEAS_TOL_W
        and E.max() <= E_MAX_WH + SOC_MARGIN_WH + FEAS_TOL_W
    )
    excl_ok = bool(
        np.all(bch + bdis <= 1 + FEAS_TOL_W)
        and np.all(ch <= BATTERY_POWER_W * bch + FEAS_TOL_W)
        and np.all(dis <= BATTERY_POWER_W * bdis + FEAS_TOL_W)
    )
    diesel_ok = bool(np.all(d <= DIESEL_MAX_W * y + FEAS_TOL_W) and np.all(d >= -FEAS_TOL_W))
    renew_ok = bool(
        np.all(s <= S + FEAS_TOL_W)
        and np.all(w <= W + FEAS_TOL_W)
        and np.all(s >= -FEAS_TOL_W)
        and np.all(w >= -FEAS_TOL_W)
    )
    binaries_ok = bool(np.all(np.isclose(np.round(np.r_[bch, bdis, y]), np.r_[bch, bdis, y], atol=1e-6)))
    terminal_ok = bool(terminal_deficit <= BATT_TOL_WH and s_term >= -FEAS_TOL_W)
    res["terminal_ok"] = terminal_ok

    res["feasible"] = bool(
        res["busbar_residual_max_w"] <= BUS_TOL_W
        and res["battery_residual_max_wh"] <= BATT_TOL_WH
        and soc_ok
        and excl_ok
        and diesel_ok
        and renew_ok
        and binaries_ok
        and terminal_ok
    )

    # zero-unmet: no unmet variable exists
    no_unmet_vars = not any(str(nm).startswith("unmet") for nm in model_names)
    res["no_unmet_variables"] = bool(no_unmet_vars)
    res["served_minus_demand_max_w"] = res["busbar_residual_max_w"]
    res["zero_unmet"] = bool(no_unmet_vars and res["busbar_residual_max_w"] <= BUS_TOL_W)

    # Recomputed objective: fuel + terminal penalty
    recomputed_fuel = float(np.sum(BASE_FUEL_L_PER_H * y + MARGINAL_FUEL_L_PER_WH * d))
    recomputed_obj = float(recomputed_fuel + TERMINAL_PENALTY_COEF * s_term)
    res["recomputed_fuel_l"] = recomputed_fuel
    res["recomputed_obj"] = recomputed_obj
    res["recompute_diff_l"] = abs(recomputed_obj - primal_obj)
    res["recompute_ok"] = bool(res["recompute_diff_l"] <= RECOMPUTE_TOL_L)
    res["diesel_on_hours"] = int(np.sum(y > 0.5))
    res["starts"] = int(np.sum((y[1:] > 0.5) & (y[:-1] < 0.5)) + (1 if y[0] > 0.5 else 0))
    return res


def _has_terminal_row(model: Model) -> bool:
    e_end = _e_col(T_HOURS)
    st = _s_term_col()
    for r in model.rows:
        if r["name"] == "terminal_soc" and r["idx"] == [e_end, st] and r["coef"] == [1.0, 1.0]:
            return True
    return False


def _has_ebr_row(model: Model) -> bool:
    for r in model.rows:
        name_lower = r["name"].lower()
        if "ebr" in name_lower or "reserve" in name_lower:
            return True
    return False


def solve_origin(inp: OriginInputs, *, time_limit_s: float = TIME_LIMIT_S, mip_rel_gap: float = 1e-9) -> Dict[str, Any]:
    model = build_model(inp)
    out = _solve(model, time_limit_s, mip_rel_gap)
    out["origin_id"] = inp.origin_id
    out["config_hash"] = config_hash()
    out["n_rows"] = len(model.rows)
    out["n_cols"] = len(model.lb)
    out["n_binaries"] = len(model.integral)
    out["has_terminal_row"] = _has_terminal_row(model)
    out["has_ebr_row"] = _has_ebr_row(model)
    if out["x"] is not None:
        out["s_term_value"] = float(out["x"][_s_term_col()])
        out["checks"] = independent_checks(inp, out["x"], out["primal"], model.names)
        out["x_list"] = [float(v) for v in out["x"]]
    else:
        out["s_term_value"] = None
    return out


LOWER_BOUND_AVAILABLE = "LOWER_BOUND_AVAILABLE"
CERTIFIED_TIGHT = "CERTIFIED_TIGHT"
BLOCKED_NO_DUAL = "BLOCKED_NO_DUAL"
BLOCKED_NO_FEASIBLE_INCUMBENT = "BLOCKED_NO_FEASIBLE_INCUMBENT"
DUAL_SANITY_TOL = 1e-6


def certify_origin(result: Dict[str, Any], inp: OriginInputs) -> Dict[str, Any]:
    """Per-origin certificate for the terminal-only lower bound diagnostic."""
    reasons: List[str] = []
    primal = result.get("primal")
    dual = result.get("dual")
    x = result.get("x")
    has_primal = x is not None and primal is not None

    checks: Dict[str, Any] = {}
    if has_primal:
        checks = independent_checks(inp, np.asarray(x, float), float(primal), build_model(inp).names)

    dual_ok = dual is not None and np.isfinite(dual)
    if not dual_ok:
        reasons.append("no dual bound")
    if not result.get("has_terminal_row", False):
        reasons.append("terminal row missing (violates terminal-only specification)")
        dual_ok = False
    if result.get("has_ebr_row", False):
        reasons.append("EBR row present (violates relaxation requirement)")
        dual_ok = False
    if dual_ok and has_primal and (primal - dual) < -DUAL_SANITY_TOL:
        reasons.append("dual bound exceeds primal (invariant violated)")
        dual_ok = False

    gap_abs = (primal - dual) if (has_primal and dual_ok) else None
    gap_rel = (gap_abs / abs(primal)) if (gap_abs is not None and primal) else None

    if not has_primal:
        reasons.append("no feasible incumbent")
    else:
        if not checks.get("feasible", False):
            reasons.append("primal feasibility check failed")
        if not checks.get("zero_unmet", False):
            reasons.append("service not fully served (zero-unmet check failed)")
        if not checks.get("recompute_ok", False):
            reasons.append("independent objective recomputation differs beyond tolerance")
        if not checks.get("terminal_ok", False):
            reasons.append("terminal constraint check failed")
        if gap_abs is not None and gap_abs > GAP_LIMIT_L:
            reasons.append(f"absolute gap {gap_abs:.6f} L > {GAP_LIMIT_L} L")

    if not has_primal and not dual_ok:
        status_code = BLOCKED_NO_FEASIBLE_INCUMBENT
    elif not dual_ok:
        status_code = BLOCKED_NO_DUAL
    elif (has_primal and not reasons):
        status_code = CERTIFIED_TIGHT
    else:
        status_code = LOWER_BOUND_AVAILABLE

    certification = "CERTIFIED" if status_code == CERTIFIED_TIGHT else "BLOCKED"
    if status_code == CERTIFIED_TIGHT:
        reasons = []

    return {
        "origin_id": inp.origin_id,
        "forecast_start": None,
        "status_code": status_code,
        "certification": certification,
        "reasons": reasons,
        "U_o": primal if has_primal else None,
        "L_o": dual if dual_ok else None,
        "gap_abs_L": gap_abs,
        "gap_rel": gap_rel,
        "s_term_value": result.get("s_term_value"),
        "solver_status": result.get("status"),
        "solver_settings_hash": result.get("solver_settings_hash"),
        "config_hash": result.get("config_hash", config_hash()),
        "checks": checks,
    }


def aggregate_certificate(certs: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    valid = [c for c in certs if c["L_o"] is not None]
    tight = [c for c in certs if c["status_code"] == CERTIFIED_TIGHT]
    with_inc = [c for c in certs if c["U_o"] is not None]
    both = [c for c in certs if c["U_o"] is not None and c["L_o"] is not None]
    s_terms = [c["s_term_value"] for c in certs if c.get("s_term_value") is not None]
    return {
        "n_origins": len(certs),
        "count_valid_dual": len(valid),
        "count_feasible_incumbent": len(with_inc),
        "count_meeting_gap_limit": len(tight),
        "count_lower_bound_not_tight": sum(1 for c in certs if c["status_code"] == LOWER_BOUND_AVAILABLE),
        "count_blocked_no_dual": sum(1 for c in certs if c["status_code"] == BLOCKED_NO_DUAL),
        "count_blocked_no_feasible_incumbent": sum(1 for c in certs if c["status_code"] == BLOCKED_NO_FEASIBLE_INCUMBENT),
        "sum_L_valid": float(sum(c["L_o"] for c in valid)) if valid else None,
        "sum_L_tight": float(sum(c["L_o"] for c in tight)) if tight else None,
        "sum_U_with_incumbent_NOT_A_BOUND": float(sum(c["U_o"] for c in with_inc)) if with_inc else None,
        "aggregate_gap_where_both_exist": (float(sum(c["U_o"] - c["L_o"] for c in both)) if both else None),
        "s_term_stats": {
            "min": float(min(s_terms)) if s_terms else None,
            "max": float(max(s_terms)) if s_terms else None,
            "mean": float(np.mean(s_terms)) if s_terms else None,
            "median": float(np.median(s_terms)) if s_terms else None,
        },
    }
