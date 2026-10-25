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
