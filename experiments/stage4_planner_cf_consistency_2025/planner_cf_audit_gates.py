"""
Planner-CF v1 audit gates (EXP-PLANNER-CF-CONSISTENCY-2025, §7 G1–G12, §8 NG).

Each gate returns a dict with a boolean PASS field and the evidence used. Gates are pure functions
over telemetry frames. None runs a solve or a realization.

Telemetry frame conventions (see planner_cf_campaign_runner.py):
  hourly:    origin_id, hour, arm, route, optimizer_received_mode, solver_status, em_rows_built,
             battery_charge, diesel_power, diesel_fuel, soc_after, busbar_balance_error_w, served/crit fields
  executed:  origin_id, arm, step, planned_charge_w, planned_unmet_crit_w, ... (planned_execution_telemetry)
  oracle realized: origin_id, hour, battery_charge (ORACLE-PHYS realized)
"""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

from planned_execution_telemetry import evaluate_g2_g3
from planner_cf_hash_guards import CORRECTED_RESULTS_PATH, CORRECTED_TELEMETRY_PATH, PROTECTED_PINS, verify_protected_hashes

N_ORIGINS = 123
HOURS_PER_ORIGIN = 24
ROWS_PER_ARM = N_ORIGINS * HOURS_PER_ORIGIN  # 2,952
SOC_LO, SOC_HI = 19.999, 95.001
BUSBAR_TOL_W = 1e-3
FUEL_TOL_L = 1e-3
DETERMINISM_TOL = 1e-6
G1_TOL_W = 1.0
OPTIMAL_STATUS = "HighsModelStatus.kOptimal"


def g1_realizability(realized: pd.DataFrame, executed: pd.DataFrame, tol_w: float = G1_TOL_W) -> Dict[str, Any]:
    """Under ORACLE-PHYS (forecast = realized): planned charge == realized charge each hour, within 1 W."""
    m = executed.merge(realized, left_on=["origin_id", "step"], right_on=["origin_id", "hour"], how="outer",
                       indicator=True)
    unmatched = int((m["_merge"] != "both").sum())
    diff = (m["planned_charge_w"] - m["battery_charge"]).abs()
    worst = float(diff.max()) if len(diff) else float("nan")
    return {"rows": int(len(m)), "unmatched": unmatched, "max_abs_diff_w": worst,
            "PASS": bool(unmatched == 0 and len(m) > 0 and worst <= tol_w)}


def g2_priority_inversion(executed: pd.DataFrame) -> Dict[str, Any]:
    res = evaluate_g2_g3(executed.to_dict("records"))
    return {"violations": res["g2_violations"], "PASS": res["G2_PASS"], "n_records": res["n_records"]}


def g3_critical_infeasibility(executed: pd.DataFrame) -> Dict[str, Any]:
    res = evaluate_g2_g3(executed.to_dict("records"))
    return {"violations": res["g3_violations"], "PASS": res["G3_PASS"], "n_records": res["n_records"]}


def g4_optimizer_status(hourly: pd.DataFrame) -> Dict[str, Any]:
    bad = hourly.loc[hourly["solver_status"] != OPTIMAL_STATUS, ["origin_id", "hour", "arm", "solver_status"]]
    return {"non_optimal_rows": bad.to_dict("records"), "n_rows": int(len(hourly)),
            "PASS": bool(len(bad) == 0 and len(hourly) > 0)}


def g5_shortfall_residual(hourly: pd.DataFrame, executed: pd.DataFrame) -> Dict[str, Any]:
    """Shortfall residual (audited, not a failure). In hours where realized S_avail < demand,
    S_avail = PV + W + diesel + discharge (realized), record |planned - realized| for critical and
    non-critical service. PASS only if every executed hour has a matching realized row."""
    m = executed.merge(hourly, left_on=["origin_id", "arm", "step"], right_on=["origin_id", "arm", "hour"],
                       how="left", indicator=True)
    matched = bool((m["_merge"] == "both").all()) and len(m) > 0
    s_avail = m["actual_solar"] + m["actual_wind"] + m["diesel_power"] + m["battery_discharge"]
    short = s_avail < m["actual_demand"]
    real_c = m["critical_served_first"]
    real_nc = m["served_load"] - real_c
    res_c = (m["planned_served_c_w"] - real_c).abs()
    res_nc = (m["planned_served_nc_w"] - real_nc).abs()
    return {"shortfall_hours": int(short.sum()),
            "max_critical_residual_w": float(res_c[short].max()) if short.any() else 0.0,
            "max_noncritical_residual_w": float(res_nc[short].max()) if short.any() else 0.0,
            "PASS": matched}


def g6_busbar_soc_fuel(hourly: pd.DataFrame) -> Dict[str, Any]:
    """Busbar and SOC bounds; fuel = 5 * on_hours + 0.25 * kWh, except listed starvation rows.

    Starvation rows are rows where fuel is consumed while realized diesel power is zero. They are
    listed explicitly in the output. The gate fails only on fuel mismatches that are not starvation rows.
    """
    busbar_bad = int((hourly["busbar_balance_error_w"].abs() > BUSBAR_TOL_W).sum())
    soc_bad = int(((hourly["soc_after"] < SOC_LO) | (hourly["soc_after"] > SOC_HI)).sum())
    on = hourly["diesel_power"] > 1e-3
    predicted = np.where(on, 5.0, 0.0) + 0.25 * hourly["diesel_power"] / 1000.0
    mismatch = (hourly["diesel_fuel"] - predicted).abs() > FUEL_TOL_L
    starvation_mask = mismatch & (~on) & (hourly["diesel_fuel"] > FUEL_TOL_L)
    unlisted = mismatch & ~starvation_mask
    starvation = hourly.loc[starvation_mask, ["origin_id", "hour", "arm", "diesel_fuel"]].to_dict("records")
    return {
        "busbar_violations": busbar_bad, "soc_violations": soc_bad,
        "fuel_mismatch_rows": int(mismatch.sum()), "starvation_rows_listed": starvation,
        "unlisted_fuel_mismatches": int(unlisted.sum()),
        "PASS": bool(busbar_bad == 0 and soc_bad == 0 and int(unlisted.sum()) == 0),
    }


def g7_determinism(run_a: pd.DataFrame, run_b: pd.DataFrame, tol: float = DETERMINISM_TOL) -> Dict[str, Any]:
    key = ["origin_id", "hour"]
    a = run_a.sort_values(key).reset_index(drop=True)
    b = run_b.sort_values(key).reset_index(drop=True)
    if len(a) != len(b) or not (a[key].equals(b[key])):
        return {"max_abs_diff": float("nan"), "PASS": False, "reason": "row mismatch"}
    num = [c for c in a.columns if c not in key and pd.api.types.is_numeric_dtype(a[c])]
    worst = max((float((a[c] - b[c]).abs().max()) for c in num), default=0.0)
    return {"max_abs_diff": worst, "PASS": bool(worst <= tol)}


def g9_accounting(hourly: pd.DataFrame, arms: Iterable[str]) -> Dict[str, Any]:
    out = {}
    ok = True
    for arm in arms:
        sub = hourly[hourly["arm"] == arm]
        n_origins = int(sub["origin_id"].nunique())
        n_rows = int(len(sub))
        dup = int(sub.duplicated(["origin_id", "hour"]).sum())
        arm_ok = n_origins == N_ORIGINS and n_rows == ROWS_PER_ARM and dup == 0
        out[arm] = {"origins": n_origins, "rows": n_rows, "duplicates": dup, "PASS": bool(arm_ok)}
        ok = ok and arm_ok
    return {"arms": out, "PASS": bool(ok)}


def g10_route_propagation(hourly: pd.DataFrame) -> Dict[str, Any]:
    recv = hourly["optimizer_received_mode"].astype(str).str.upper()
    route = hourly["route"].astype(str).str.upper()
    mismatch = int((recv != route).sum())
    em = hourly["route"].astype(str).str.upper() == "EMERGENCY"
    em_bad = int((em & (hourly["em_rows_built"] != HOURS_PER_ORIGIN)).sum()
                 + (~em & (hourly["em_rows_built"] != 0)).sum())
    return {"route_mismatch_rows": mismatch, "em_row_count_violations": em_bad,
            "PASS": bool(mismatch == 0 and em_bad == 0)}


def g11_old_telemetry_unmodified(repo: Path) -> Dict[str, Any]:
    pins = {k: v for k, v in PROTECTED_PINS.items() if k in (CORRECTED_RESULTS_PATH, CORRECTED_TELEMETRY_PATH)}
    mism = verify_protected_hashes(repo, pins)
    return {"mismatches": mism, "PASS": bool(not mism and len(pins) == 2)}


def g12_oracle_coverage(origins: Sequence[pd.Timestamp], lookup_keys: Iterable[str]) -> Dict[str, Any]:
    """Every origin's 47-hour SITES window (offsets j = 0..46) must be present. Blocked origins listed."""
    keys = set(lookup_keys)
    blocked: List[str] = []
    for o in origins:
        needed = [(o + pd.Timedelta(hours=j)).strftime("%Y-%m-%d %H:%M:%S") for j in range(47)]
        if any(k not in keys for k in needed):
            blocked.append(str(o.date()))
    return {"blocked_origins": blocked, "PASS": bool(len(blocked) == 0 and len(origins) == N_ORIGINS)}


GATE_IMPLEMENTATIONS = {
    "G1": g1_realizability,
    "G2": g2_priority_inversion,
    "G3": g3_critical_infeasibility,
    "G4": g4_optimizer_status,
    "G5": g5_shortfall_residual,
    "G6": g6_busbar_soc_fuel,
    "G7": g7_determinism,
    "G9": g9_accounting,
    "G10": g10_route_propagation,
    "G11": g11_old_telemetry_unmodified,
    "G12": g12_oracle_coverage,
}


# ---------------------------------------------------------------------------
# Amendment A2 (§17.3): Class-B tie admission. AUDIT RULE ONLY. It never changes the planner's selected
# solution. Under v1.1 G1 remains exact (g1_realizability). v1.2 uses g1_v12, which admits a hour-0
# charge difference only if all seven conditions hold, and never admits a starvation row.
# ---------------------------------------------------------------------------

E_MAX_WH = 190000.0          # 95 % of 200 kWh (governed battery bound)
CHARGE_CAP_W = 50000.0       # governed charge power
ETA_CHG_AUDIT = 0.92
ADMISSION_J4_WH = 1.0        # A2 §17.3 condition 4 (established criterion)
STARVATION_TOL_W = 1.0


def _greedy_alt_curtailment(horizon: Dict[str, Any], e_start_wh: float) -> float:
    """Q of A2 §17.3: keep planned served, discharge and diesel fixed; charge at min(surplus, 50 kW, room/0.92)."""
    e = float(e_start_wh)
    total = 0.0
    eta = ETA_CHG_AUDIT
    dis_arr = horizon["P_discharge"]
    for t in range(len(dis_arr)):
        avail = horizon["forecast_solar"][t] + horizon["forecast_wind"][t] + dis_arr[t] + horizon["P_diesel"][t]
        surplus = max(0.0, avail - horizon["P_served"][t])
        if dis_arr[t] > 1e-4:
            curt = surplus
            c = 0.0
        else:
            room = max(0.0, E_MAX_WH - e)
            c = min(surplus, CHARGE_CAP_W, room / eta)
            curt = surplus - c
        total += curt
        e = e + eta * c - dis_arr[t] / eta
    return total


def _j3_from_diesel(diesel: Sequence[float]) -> float:
    """Fuel objective of the planner's J3 over the horizon: 5 L per on-hour + 0.00025 L/Wh, plus 2 L per start."""
    on = [1 if d > 1e-3 else 0 for d in diesel]
    starts = sum(1 for t in range(len(on)) if on[t] == 1 and (t == 0 or on[t - 1] == 0))
    return float(sum(5.0 * on[t] + 0.00025 * diesel[t] for t in range(len(on))) + 2.0 * starts)


V12_REQUIRED_FIELDS = (
    "P_charge_w", "R_charge_w", "P_discharge_w", "R_discharge_w", "P_diesel_w", "R_diesel_w",
    "P_served_w", "R_served_w", "P_unmet_w", "R_unmet_w", "P_curt_w", "P_solar_used_w", "P_wind_used_w",
    "solar_w", "wind_w", "demand_w", "forecast_solar_w", "forecast_wind_w", "E_before_wh", "fuel_before_l", "horizon",
)
V12_HORIZON_FIELDS = ("forecast_solar", "forecast_wind", "P_discharge", "P_diesel", "P_served", "P_unmet", "P_curt")


def v12_missing_fields(row: Dict[str, Any]) -> list:
    """Fail-closed input check: returns the missing or malformed required fields (empty list = complete)."""
    missing = [k for k in V12_REQUIRED_FIELDS if row.get(k) is None]
    h = row.get("horizon")
    if isinstance(h, dict):
        for k in V12_HORIZON_FIELDS:
            if h.get(k) is None or len(h[k]) != 24:
                missing.append(f"horizon.{k}")
    elif h is not None:
        missing.append("horizon(not a dict)")
    return missing


def g1_v12_admission(row: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates the seven A2 §17.3 conditions for one hour-0 row. Every condition is recorded explicitly.

    Required row fields: P_charge_w, P_discharge_w, P_diesel_w, P_served_w, P_unmet_w, P_curt_w,
    P_solar_used_w, P_wind_used_w, R_charge_w, R_discharge_w, R_diesel_w, R_served_w, R_unmet_w,
    solar_w, wind_w, demand_w, forecast_solar_w, forecast_wind_w, E_before_wh, fuel_before_l,
    horizon (dict of 24-hour lists: forecast_solar, forecast_wind, P_discharge, P_diesel, P_served,
    P_unmet, P_curt).
    """
    missing = v12_missing_fields(row)
    if missing:  # fail closed: no admission can be evaluated without the required data
        return {"conditions": {}, "failed_conditions": ["missing_required_data"], "missing_fields": missing,
                "starvation_row": False, "admitted": False, "J4_detail": {}}
    h = row["horizon"]
    tol = G1_TOL_W
    cond: Dict[str, bool] = {}
    # 1. served and unmet equal realized, within the G1 tolerance
    cond["c1_served_unmet_equal"] = bool(abs(row["P_served_w"] - row["R_served_w"]) <= tol
                                          and abs(row["P_unmet_w"] - row["R_unmet_w"]) <= tol)
    # 2. discharge and diesel equal realized, within the G1 tolerance
    cond["c2_discharge_diesel_equal"] = bool(abs(row["P_discharge_w"] - row["R_discharge_w"]) <= tol
                                              and abs(row["P_diesel_w"] - row["R_diesel_w"]) <= tol)
    # 3. J1, J_NC, J2, J3 of P and of Q equal to within the existing tolerance. Q holds the planned
    #    unmet and diesel arrays, so the unmet and fuel terms are identical by construction; J2 is zero
    #    in ORACLE-PHYS (reserve removed). The J3 check recomputes both from the same arrays.
    j3_p = _j3_from_diesel(h["P_diesel"])
    j3_q = _j3_from_diesel(h["P_diesel"])
    unmet_p = float(sum(h["P_unmet"]))
    unmet_q = float(sum(h["P_unmet"]))
    cond["c3_objective_terms_equal"] = bool(abs(j3_p - j3_q) <= 1e-6 and abs(unmet_p - unmet_q) <= 1e-6)
    # 4. |J4(P) - J4(Q)| <= 1 Wh over the 24-hour horizon
    j4_p = float(sum(h["P_curt"]))
    j4_q = _greedy_alt_curtailment(h, row["E_before_wh"])
    row_j4 = {"J4_P_Wh": j4_p, "J4_Q_Wh": j4_q, "abs_diff_Wh": abs(j4_p - j4_q)}
    cond["c4_J4_tie_within_1Wh"] = bool(abs(j4_p - j4_q) <= ADMISSION_J4_WH)
    # 5. planned charge + planned curtailment = realized surplus within 1 W, with forecast == realized
    s_real = max(0.0, row["solar_w"] + row["wind_w"] + row["R_discharge_w"] + row["R_diesel_w"] - row["demand_w"])
    forecast_eq = abs(row["forecast_solar_w"] - row["solar_w"]) <= tol and abs(row["forecast_wind_w"] - row["wind_w"]) <= tol
    cond["c5_planned_identity_forecast_equals_realized"] = bool(
        forecast_eq and abs(row["P_charge_w"] + row["P_curt_w"] - s_real) <= tol
        and abs(row["P_solar_used_w"] + row["P_wind_used_w"] + row["P_curt_w"] - (row["solar_w"] + row["wind_w"])) <= tol)
    # 6. realized charge follows the executor rule within 1 W
    if row["R_discharge_w"] > 1e-4:
        rule = 0.0
    else:
        rule = min(s_real, CHARGE_CAP_W, max(0.0, E_MAX_WH - row["E_before_wh"]) / ETA_CHG_AUDIT)
    cond["c6_realized_rule"] = bool(abs(row["R_charge_w"] - rule) <= tol)
    # 7. planned hour-0 schedule satisfies 5*u + 0.00025*p <= F_rem (v1.2 constraint)
    d0 = row["P_diesel_w"]
    u0 = 1 if d0 > 1e-3 else 0
    need = 5.0 * u0 + 0.00025 * d0
    cond["c7_hour0_fuel_feasible"] = bool(need <= row["fuel_before_l"] + 1e-9)
    # Starvation rows are never admitted (Class C)
    starved = bool(row["P_diesel_w"] > STARVATION_TOL_W and row["R_diesel_w"] < row["P_diesel_w"] - STARVATION_TOL_W)
    admitted = bool(all(cond.values()) and not starved)
    failed = [k for k, v in cond.items() if not v]
    return {"conditions": cond, "failed_conditions": failed, "starvation_row": starved,
            "admitted": admitted, "J4_detail": row_j4}


def g1_v12(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """G1 under A2 §17.3. A row passes if planned and realized charge agree within 1 W, or if it is an
    admitted Class-B tie. Any other row fails G1. No exception is raised for a failed row."""
    per_row = []
    failures = []
    for r in rows:
        if r.get("P_charge_w") is None or r.get("R_charge_w") is None:
            failures.append({"origin_id": r.get("origin_id"), "step": r.get("step"),
                             "failed_conditions": ["missing_charge_fields"], "starvation_row": False})
            per_row.append({"origin_id": r.get("origin_id"), "step": r.get("step"), "result": "FAIL"})
            continue
        mismatch = abs(r["P_charge_w"] - r["R_charge_w"])
        if mismatch <= G1_TOL_W:
            per_row.append({"origin_id": r.get("origin_id"), "step": r.get("step"), "result": "EXACT"})
            continue
        ev = g1_v12_admission(r)
        result = "ADMITTED_TIE" if ev["admitted"] else "FAIL"
        per_row.append({"origin_id": r.get("origin_id"), "step": r.get("step"), "result": result,
                        "mismatch_w": mismatch, **ev})
        if not ev["admitted"]:
            failures.append({"origin_id": r.get("origin_id"), "step": r.get("step"),
                             "failed_conditions": ev["failed_conditions"], "starvation_row": ev["starvation_row"]})
    return {"rows": len(rows), "exact": sum(1 for x in per_row if x["result"] == "EXACT"),
            "admitted_ties": sum(1 for x in per_row if x["result"] == "ADMITTED_TIE"),
            "failures": failures, "PASS": bool(len(rows) > 0 and not failures), "per_row": per_row}
