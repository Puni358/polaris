"""
Global per-origin relaxed lower bound — Formulation H: Full Realized-EBR + Diesel Minimum
(EXP-PLANNER-CF-CONSISTENCY-2025, Formulation H).

RESEARCH-ONLY ISOLATED MODULE.
Do not import into production code or overwrite certified governance baselines.

Mathematical Foundation:
Formulation H = Formulation G + real PC-SW diesel minimum-output constraint:
    diesel_power[t] >= 10000 * diesel_on[t]  for t = 0..23

The actual PC-SW realized trajectory x_real satisfies this constraint strictly
(verified: minimum positive diesel power = 10,000 W across all 2,952 telemetry rows).
Therefore, x_real remains admissible in Formulation H, and:
    LB_G <= LB_H <= objective_H(x_real) <= PC-SW realized fuel + slack.

Formulation H specifications:
1. Retains all relaxations and structure from Formulation G:
   - fuel inventory relaxed
   - startup fuel = 0 L
   - SOC bounds [40 kWh, 190 kWh] with ±2 Wh margin
   - battery power ±50 kW
   - charge/discharge exclusivity
   - diesel max 100 kW with on/off binary
   - busbar balance with hard service (no unmet variables)
   - 24 hourly EBR rows: E[t+1] + s_ebr[t] >= ebr_target_wh[origin_id, t] + min_e_wh
   - s_ebr[t] >= 0 with J2-equivalent penalty of 1.0
   - no terminal constraint
2. Adds 24 diesel minimum output constraints:
   For t = 0..23:
       d[t] >= 10000 * y[t]
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import highspy
import numpy as np

# ---------------------------------------------------------------------------
# Governed constants
# ---------------------------------------------------------------------------
T_HOURS = 24
CAPACITY_WH = 200000.0
E_MIN_WH = 0.20 * CAPACITY_WH          # 40,000 Wh
E_MAX_WH = 0.95 * CAPACITY_WH          # 190,000 Wh
SOC_MARGIN_WH = 2.0                    # numerical margin
BATTERY_POWER_W = 50000.0
ETA_CHG = 0.92
ETA_DIS = 0.92
DIESEL_MIN_W = 10000.0                 # Formulation H addition
DIESEL_MAX_W = 100000.0
BASE_FUEL_L_PER_H = 5.0
MARGINAL_FUEL_L_PER_WH = 0.00025
STARTUP_FUEL_L_PRIMARY = 0.0
GAP_LIMIT_L = 0.01                     # tight-certification gap
TIME_LIMIT_S = 60.0
RECOMPUTE_TOL_L = 1e-6
FEAS_TOL_W = 1e-6
BUS_TOL_W = 1e-3
BATT_TOL_WH = 1e-3
EBR_SLACK_COST = 1.0
TERMINAL_STATEMENT = "none (completely removed)"

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
    """Exact configuration used for the Formulation H hash."""
    return {
        "formulation_name": "FORMULATION_H_FULL_REALIZED_EBR_DIESEL_MIN_LOWER_BOUND",
        "T": T_HOURS,
        "capacity_wh": CAPACITY_WH,
        "e_min_wh": E_MIN_WH,
        "e_max_wh": E_MAX_WH,
        "soc_margin_wh": SOC_MARGIN_WH,
        "battery_power_w": BATTERY_POWER_W,
        "eta_chg": ETA_CHG,
        "eta_dis": ETA_DIS,
        "diesel_min_w": DIESEL_MIN_W,
        "diesel_max_w": DIESEL_MAX_W,
        "base_fuel_l_per_h": BASE_FUEL_L_PER_H,
        "marginal_fuel_l_per_wh": MARGINAL_FUEL_L_PER_WH,
        "startup_fuel_l_primary": STARTUP_FUEL_L_PRIMARY,
        "gap_limit_l": GAP_LIMIT_L,
        "terminal": TERMINAL_STATEMENT,
        "fuel_inventory": "relaxed",
        "reserve": "24-hour exogenous realized EBR profile",
        "ebr_slack_cost": EBR_SLACK_COST,
        "diesel_min_constraint": "d[t] >= 10000 * y[t] for all t=0..23",
        "service": "full critical and non-critical; no unmet variables",
    }


def config_hash() -> str:
    blob = json.dumps(formulation_config(), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def _col(t: int, which: int) -> int:
    return t * BLOCK_SIZE + which


def _e_col(t: int) -> int:
    return T_HOURS * BLOCK_SIZE + t


def _s_ebr_col(t: int) -> int:
    return T_HOURS * BLOCK_SIZE + (T_HOURS + 1) + t


def _n_cols() -> int:
    # 24 * 8 (dispatch) + 25 (E) + 24 (s_ebr) = 241
    return T_HOURS * BLOCK_SIZE + (T_HOURS + 1) + T_HOURS


@dataclass
class Model:
    lb: np.ndarray
    ub: np.ndarray
    integral: List[int]
    cost: np.ndarray
    rows: List[Dict[str, Any]] = field(default_factory=list)
    names: List[str] = field(default_factory=list)


def build_model_h(inp: OriginInputs, ebr_targets_wh: Sequence[float]) -> Model:
    """Builds Formulation H MILP for an origin."""
    if len(inp.solar_w) != T_HOURS or len(inp.wind_w) != T_HOURS or len(inp.demand_w) != T_HOURS:
        raise ValueError("origin inputs must have 24 hourly values")
    if len(ebr_targets_wh) != T_HOURS:
        raise ValueError("ebr_targets_wh must have exactly 24 values")
    if not (E_MIN_WH - SOC_MARGIN_WH <= inp.e0_wh <= E_MAX_WH + SOC_MARGIN_WH):
        raise ValueError("initial energy outside SOC bounds")

    n = _n_cols()
    lb = np.zeros(n)
    ub = np.zeros(n)
    cost = np.zeros(n)
    integral: List[int] = []
    names = [""] * n

    # Hourly dispatch variables
    for t in range(T_HOURS):
        S, W, D = float(inp.solar_w[t]), float(inp.wind_w[t]), float(inp.demand_w[t])
        if min(S, W, D) < 0:
            raise ValueError(f"negative renewable or demand input at hour {t}")
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

    # Battery state of energy variables E[0..24]
    for t in range(T_HOURS + 1):
        names[_e_col(t)] = f"E[{t}]"
        lb[_e_col(t)] = E_MIN_WH - SOC_MARGIN_WH
        ub[_e_col(t)] = E_MAX_WH + SOC_MARGIN_WH
    lb[_e_col(0)] = ub[_e_col(0)] = inp.e0_wh

    # EBR slack variables s_ebr[0..23]
    for t in range(T_HOURS):
        idx = _s_ebr_col(t)
        names[idx] = f"s_ebr[{t}]"
        lb[idx] = 0.0
        ub[idx] = np.inf
        cost[idx] = EBR_SLACK_COST

    model = Model(lb=lb, ub=ub, integral=integral, cost=cost, names=names)

    # Base rows
    for t in range(T_HOURS):
        S, W, D = float(inp.solar_w[t]), float(inp.wind_w[t]), float(inp.demand_w[t])
        # Busbar balance: s + w + dis + d - ch = D
        model.rows.append({
            "name": f"busbar[{t}]", "lhs": D, "rhs": D,
            "idx": [_col(t, COL_S), _col(t, COL_W), _col(t, COL_DIS), _col(t, COL_D), _col(t, COL_CH)],
            "coef": [1.0, 1.0, 1.0, 1.0, -1.0]
        })
        # Battery transition: E[t+1] - E[t] - eta_chg*ch + dis/eta_dis = 0
        model.rows.append({
            "name": f"battery[{t}]", "lhs": 0.0, "rhs": 0.0,
            "idx": [_e_col(t + 1), _e_col(t), _col(t, COL_CH), _col(t, COL_DIS)],
            "coef": [1.0, -1.0, -ETA_CHG, 1.0 / ETA_DIS]
        })
        # Charge/discharge binary bounds
        model.rows.append({
            "name": f"charge_bin[{t}]", "lhs": -np.inf, "rhs": 0.0,
            "idx": [_col(t, COL_CH), _col(t, COL_BCH)], "coef": [1.0, -BATTERY_POWER_W]
        })
        model.rows.append({
            "name": f"discharge_bin[{t}]", "lhs": -np.inf, "rhs": 0.0,
            "idx": [_col(t, COL_DIS), _col(t, COL_BDIS)], "coef": [1.0, -BATTERY_POWER_W]
        })
        model.rows.append({
            "name": f"exclusivity[{t}]", "lhs": -np.inf, "rhs": 1.0,
            "idx": [_col(t, COL_BCH), _col(t, COL_BDIS)], "coef": [1.0, 1.0]
        })
        # Diesel upper bound on/off
        model.rows.append({
            "name": f"diesel_on[{t}]", "lhs": -np.inf, "rhs": 0.0,
            "idx": [_col(t, COL_D), _col(t, COL_Y)], "coef": [1.0, -min(DIESEL_MAX_W, D + BATTERY_POWER_W)]
        })

    # Formulation G EBR rows (t = 0..23):
    # E[t+1] + s_ebr[t] >= ebr_target_wh[origin, t] + min_e_wh
    for t in range(T_HOURS):
        target_val = float(ebr_targets_wh[t])
        rhs_val = target_val + E_MIN_WH
        model.rows.append({
            "name": f"ebr[{t}]", "lhs": rhs_val, "rhs": np.inf,
            "idx": [_e_col(t + 1), _s_ebr_col(t)],
            "coef": [1.0, 1.0]
        })

    # Formulation H Addition: 24 Diesel Minimum Output rows (t = 0..23):
    # d[t] >= 10000 * y[t]  =>  d[t] - 10000 * y[t] >= 0
    for t in range(T_HOURS):
        model.rows.append({
            "name": f"diesel_min[{t}]", "lhs": 0.0, "rhs": np.inf,
            "idx": [_col(t, COL_D), _col(t, COL_Y)],
            "coef": [1.0, -DIESEL_MIN_W]
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
    has_incumbent = (info.primal_solution_status == highspy.SolutionStatus.kSolutionStatusFeasible
                     and len(sol.col_value) == n)
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


def _has_terminal_row(model: Model) -> bool:
    """Verifies that no terminal row or E[24]-only bound row exists."""
    e_end = _e_col(T_HOURS)
    for r in model.rows:
        if r["idx"] == [e_end]:
            return True
        if "terminal" in r["name"].lower():
            return True
    return False


def independent_checks_h(
    inp: OriginInputs,
    ebr_targets_wh: Sequence[float],
    x: np.ndarray,
    primal_obj: float,
    model_names: Sequence[str]
) -> Dict[str, Any]:
    """Independent verification of incumbent for Formulation H."""
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
    s_ebr = np.array([x[_s_ebr_col(t)] for t in range(T_HOURS)])

    busbar = s + w + dis + d - ch - D
    res["busbar_residual_max_w"] = float(np.max(np.abs(busbar)))
    batt = E[1:] - E[:-1] - ETA_CHG * ch + dis / ETA_DIS
    res["battery_residual_max_wh"] = float(np.max(np.abs(batt)))
    res["soc_min_wh"] = float(E.min())
    res["soc_max_wh"] = float(E.max())
    res["soc_min_pct"] = float(E.min() / CAPACITY_WH * 100.0)
    res["soc_max_pct"] = float(E.max() / CAPACITY_WH * 100.0)

    # EBR constraint check: E[t+1] + s_ebr[t] >= ebr_targets_wh[t] + E_MIN_WH
    ebr_targets = np.asarray(ebr_targets_wh, float)
    ebr_req = ebr_targets + E_MIN_WH
    ebr_violation = ebr_req - (E[1:] + s_ebr)
    res["ebr_residual_max_wh"] = float(np.max(np.maximum(0.0, ebr_violation)))
    res["s_ebr_min_wh"] = float(np.min(s_ebr))
    res["s_ebr_max_wh"] = float(np.max(s_ebr))
    res["s_ebr_sum_wh"] = float(np.sum(s_ebr))

    soc_ok = bool(E.min() >= E_MIN_WH - SOC_MARGIN_WH - FEAS_TOL_W and E.max() <= E_MAX_WH + SOC_MARGIN_WH + FEAS_TOL_W)
    excl_ok = bool(np.all(bch + bdis <= 1 + FEAS_TOL_W) and np.all(ch <= BATTERY_POWER_W * bch + FEAS_TOL_W)
                   and np.all(dis <= BATTERY_POWER_W * bdis + FEAS_TOL_W))
    diesel_ub_ok = bool(np.all(d <= DIESEL_MAX_W * y + FEAS_TOL_W) and np.all(d >= -FEAS_TOL_W))
    diesel_min_ok = bool(np.all(d >= DIESEL_MIN_W * y - FEAS_TOL_W))
    renew_ok = bool(np.all(s <= S + FEAS_TOL_W) and np.all(w <= W + FEAS_TOL_W) and np.all(s >= -FEAS_TOL_W)
                    and np.all(w >= -FEAS_TOL_W))
    binaries_ok = bool(np.all(np.isclose(np.round(np.r_[bch, bdis, y]), np.r_[bch, bdis, y], atol=1e-6)))
    ebr_ok = bool(res["ebr_residual_max_wh"] <= FEAS_TOL_W and res["s_ebr_min_wh"] >= -FEAS_TOL_W)

    res["diesel_min_satisfied"] = diesel_min_ok
    res["feasible"] = bool(res["busbar_residual_max_w"] <= BUS_TOL_W and res["battery_residual_max_wh"] <= BATT_TOL_WH
                           and soc_ok and excl_ok and diesel_ub_ok and diesel_min_ok and renew_ok and binaries_ok and ebr_ok)

    no_unmet_vars = not any(str(nm).startswith("unmet") for nm in model_names)
    res["no_unmet_variables"] = bool(no_unmet_vars)
    res["served_minus_demand_max_w"] = res["busbar_residual_max_w"]
    res["zero_unmet"] = bool(no_unmet_vars and res["busbar_residual_max_w"] <= BUS_TOL_W)

    recomputed = float(np.sum(BASE_FUEL_L_PER_H * y + MARGINAL_FUEL_L_PER_WH * d + EBR_SLACK_COST * s_ebr))
    res["recomputed_objective"] = recomputed
    recomputed_fuel_only = float(np.sum(BASE_FUEL_L_PER_H * y + MARGINAL_FUEL_L_PER_WH * d))
    res["recomputed_fuel_l"] = recomputed_fuel_only
    res["recompute_diff"] = abs(recomputed - primal_obj)
    res["recompute_ok"] = bool(res["recompute_diff"] <= RECOMPUTE_TOL_L)
    res["diesel_on_hours"] = int(np.sum(y > 0.5))
    res["starts"] = int(np.sum((y[1:] > 0.5) & (y[:-1] < 0.5)) + (1 if y[0] > 0.5 else 0))
    return res


def solve_origin_h(
    inp: OriginInputs,
    ebr_targets_wh: Sequence[float],
    *,
    time_limit_s: float = TIME_LIMIT_S,
    mip_rel_gap: float = 1e-9
) -> Dict[str, Any]:
    """Builds, solves, and independently audits Formulation H for one origin."""
    model = build_model_h(inp, ebr_targets_wh)
    out = _solve(model, time_limit_s, mip_rel_gap)
    out["origin_id"] = inp.origin_id
    out["config_hash"] = config_hash()
    out["n_rows"] = len(model.rows)
    out["n_cols"] = len(model.lb)
    out["n_binaries"] = len(model.integral)
    out["has_terminal_row"] = _has_terminal_row(model)
    if out["x"] is not None:
        out["checks"] = independent_checks_h(inp, ebr_targets_wh, out["x"], out["primal"], model.names)
        out["s_ebr_values"] = [float(out["x"][_s_ebr_col(t)]) for t in range(T_HOURS)]
        out["e_values"] = [float(out["x"][_e_col(t)]) for t in range(T_HOURS + 1)]
    return out
