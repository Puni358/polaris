"""
Forensic planned-capture replay of ORACLE-PHYS (EXP-PLANNER-CF-CONSISTENCY-2025, §16.5).

DIAGNOSIS ONLY. Not a campaign, not a production run, not a formulation change, not a replacement
for the original ORACLE outputs. It re-runs ORACLE-PHYS over the governed 123-origin population
with the same Planner-CF v1 formulation, the same realization executor and the same G1 definition,
and keeps the planned DispatchPlan at every hour so each G1 mismatch can be classified.

Writes only to a NEW timestamped directory. Never overwrites ORACLE_PHYS_HOURLY.csv,
ORACLE_CTRL_HOURLY.csv or ORACLE_AUDIT_REPORT.json.

Integrity checks (run by run_forensic_capture):
  - explicit authorization; §9 protected hashes verified before and after;
  - every solve must be OPTIMAL; 123 x 24 = 2952 rows;
  - replay realized outputs must reproduce the original ORACLE_PHYS_HOURLY.csv exactly
    (else FORENSIC_REPLAY_NONREPRODUCIBLE, and the classification is not reported).
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for _p in (str(REPO), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import oracle_runner as oracle  # noqa: E402
from system.control.router import EMSControlRouter  # noqa: E402
from system.research.route_mode_propagation import propagate_route_mode  # noqa: E402
from system.simulation.research_realization_executor import ResearchRealizationExecutor  # noqa: E402
from research_numerical_extractor_planner_cf_v1 import PlannerCFV1Optimizer  # noqa: E402
from planned_telemetry_harness import PlannedTelemetryHarness  # noqa: E402
from planner_cf_hash_guards import verify_protected_hashes  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402

ORACLE_PHYS_ORIGINAL = _HERE / "ORACLE_PHYS_HOURLY.csv"
G1_TOL_W = gates.G1_TOL_W
MAX_BATTERY_W = 50000.0
ETA_CHG = 0.92
EXACT_TOL = 1e-6
TIE_TOL_WH = 1.0
CODE_FILES = [
    "experiments/stage4_planner_cf_consistency_2025/forensic_planned_capture.py",
    "experiments/stage4_planner_cf_consistency_2025/oracle_runner.py",
    "experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py",
    "experiments/stage4_planner_cf_consistency_2025/planned_telemetry_harness.py",
    "experiments/stage4_planner_cf_consistency_2025/planner_cf_audit_gates.py",
    "experiments/stage4_planner_cf_consistency_2025/planner_cf_hash_guards.py",
    "experiments/stage4_planner_cf_consistency_2025/ORACLE_PHYS_HOURLY.csv",
    "experiments/stage4_planner_cf_consistency_2025/ORACLE_AUDIT_REPORT.json",
]


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested on synthetic data)
# ---------------------------------------------------------------------------

def greedy_alternative_curtailment(horizon: Dict[str, Sequence[float]], e_start_wh: float,
                                   e_max_wh: float, eta: float = ETA_CHG) -> Dict[str, Any]:
    """Keep the plan's discharge, diesel and served load; recompute charge hour by hour as
    min(surplus, 50 kW, room/eta). Returns total curtailment (Wh) of this customer-first alternative."""
    e = float(e_start_wh)
    total = 0.0
    chg: List[float] = []
    for t in range(24):
        avail = horizon["forecast_solar"][t] + horizon["forecast_wind"][t] + horizon["P_discharge"][t] + horizon["P_diesel"][t]
        surplus = max(0.0, avail - horizon["P_served"][t])
        dis = horizon["P_discharge"][t]
        if dis > 1e-4:
            c = 0.0
            curt = surplus
        else:
            room = max(0.0, e_max_wh - e)
            c = min(surplus, MAX_BATTERY_W, room / eta)
            curt = surplus - c
        total += curt
        chg.append(c)
        e = e + eta * c - dis / eta
    return {"alt_total_curtailment_wh": total, "alt_charge_w": chg}


def classify_row(r: Dict[str, Any]) -> Dict[str, Any]:
    """Assign exactly one of A/B/C/D/E to a mismatch row, with the flags that justify it.

    Flags:
      data_error  (D): non-optimal solve, busbar residual, or planned identity residual.
      executor_dev (A): realized charge differs from min(realized surplus, cap, room).
      starvation  : planned diesel needs more fuel than remains; realized diesel reduced.
      pcc         : planner curtailed while charge capacity was physically available.
    Class rule: D > (C if starvation and another cause) > C (starvation alone) > A > B > E.
    """
    d = r["data_error"]
    if d:
        cls = "D"
    elif r["starvation"] and (r["pcc"] or r["executor_dev"]):
        cls = "C"
    elif r["starvation"]:
        cls = "C"
    elif r["executor_dev"] and r["pcc"]:
        cls = "C"
    elif r["executor_dev"]:
        cls = "A"
    elif r["pcc"]:
        cls = "B"
    else:
        cls = "E"
    out = dict(r)
    out["class"] = cls
    return out


def planner_curtailment_tie(horizon: Dict[str, Sequence[float]], e_start_wh: float, e_max_wh: float,
                            planned_total_curtailment_wh: float) -> Dict[str, Any]:
    alt = greedy_alternative_curtailment(horizon, e_start_wh, e_max_wh)
    diff = alt["alt_total_curtailment_wh"] - planned_total_curtailment_wh
    return {"alt_total_curtailment_wh": alt["alt_total_curtailment_wh"],
            "alt_minus_plan_wh": diff,
            "equal_cost_tie": bool(abs(diff) <= TIE_TOL_WH)}


def compare_to_original(replay: pd.DataFrame, original: pd.DataFrame, tol: float = EXACT_TOL) -> Dict[str, Any]:
    """Exact reproduction check against ORACLE_PHYS_HOURLY.csv on every comparable field."""
    key = ["origin_id", "step"]
    m = replay.merge(original, left_on=key, right_on=["origin_id", "step"], how="outer", indicator=True,
                     suffixes=("_rep", "_orig"))
    if (m["_merge"] != "both").any() or len(m) != len(original) or len(m) != len(replay):
        return {"PASS": False, "reason": "row-set mismatch", "max_abs_diff": float("nan")}
    pairs = {"charge_w": ("R_charge", "charge_w"), "discharge_w": ("R_discharge", "discharge_w"),
             "diesel_w": ("P_diesel", "diesel_w"), "served_w": ("R_served", "served_w"),
             "unmet_w": ("R_unmet", "unmet_w"), "fuel_l": ("R_fuel", "fuel_l"),
             "soc_pct": ("R_soc_after", "soc_pct"), "solar_w": ("R_solar", "solar_w"),
             "wind_w": ("R_wind", "wind_w"), "demand_w": ("R_demand", "demand_w")}
    worst = 0.0
    per_field: Dict[str, float] = {}
    for orig_col, (rep_col, orig_c) in pairs.items():
        a = m[rep_col + "_rep"] if rep_col + "_rep" in m else m[rep_col]
        b = m[orig_c + "_orig"] if orig_c + "_orig" in m else m[orig_c]
        diff = float((a.astype(float) - b.astype(float)).abs().max())
        per_field[orig_col] = diff
        worst = max(worst, diff)
    return {"PASS": bool(worst <= tol), "max_abs_diff": worst, "per_field": per_field,
            "rows": int(len(m))}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Replay of one origin (mirrors oracle_runner.run_oracle_origin, keeps DispatchPlan)
# ---------------------------------------------------------------------------

def capture_origin(origin: pd.Timestamp, origin_index: int, lookup: Dict[str, float], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    optimizer = PlannerCFV1Optimizer(reserve_enabled=False)  # ORACLE-PHYS
    harness = PlannedTelemetryHarness(optimizer)
    router = EMSControlRouter()
    executor = ResearchRealizationExecutor(cfg)
    bat = cfg["battery"]
    cap = float(bat.get("capacity_wh", 200000.0))
    e_max = cap * float(bat.get("max_soc_pct", 95.0)) / 100.0

    state = oracle._initial_state(origin)
    rows: List[Dict[str, Any]] = []
    for step in range(24):
        e_before = float(state.battery_energy_wh)
        fuel_before = float(state.diesel_fuel_remaining_liters)
        bundle = oracle.build_horizon(origin, step, lookup)
        crit = [oracle.critical_w(j) for j in range(step, step + 24)]
        _, route = router.evaluate_and_route(state, bundle, cfg)
        planning_state = propagate_route_mode(state, route)
        step_cfg = dict(cfg)
        step_cfg["critical_demand_w"] = crit
        plan = harness.optimize(bundle, planning_state, step_cfg, origin_id=origin_index, arm="ORACLE-PHYS", step=step)
        lp = optimizer.last_planned[0]
        status = str(optimizer.last_diagnostics[0]["solver_status"]) if optimizer.last_diagnostics else str(plan.constraint_status)
        realized = {"timestamp": oracle.ts_label(origin, step),
                    "actual_SW_IN": lookup[(origin + pd.Timedelta(hours=step)).strftime("%Y-%m-%d %H:%M:%S")],
                    "actual_wind_generation": oracle.wind_w(step), "actual_demand": oracle.demand_w(step)}
        res = executor.execute_step(state, plan, realized, step_index=0)
        if res.busbar_energy_balance_error_w > 1e-3:
            raise RuntimeError(f"busbar error {res.busbar_energy_balance_error_w} W at origin {origin_index} step {step}")
        room_ac = max(0.0, e_max - e_before) / ETA_CHG
        charge_cap = min(MAX_BATTERY_W, room_ac)
        horizon = {"P_charge": list(plan.battery_charge), "P_discharge": list(plan.battery_discharge),
                   "P_diesel": list(plan.diesel_power), "P_served": list(plan.load_served),
                   "P_unmet": list(plan.unmet_load), "P_curt": list(plan.renewable_curtailment),
                   "P_solar_used": list(plan.solar_used), "P_wind_used": list(plan.wind_used),
                   "P_soc_pct": list(plan.battery_soc),
                   "forecast_solar": list(bundle.solar_generation.point),
                   "forecast_wind": list(bundle.wind_generation.point),
                   "demand": list(bundle.demand.point)}
        rows.append({
            "origin_id": origin_index, "step": step, "route": route, "solver_status": status,
            "E_before_wh": e_before, "soc_before_pct": e_before / cap * 100.0, "fuel_before_l": fuel_before,
            "demand_w": realized["actual_demand"], "solar_w": res.solar_realized_w, "wind_w": res.wind_realized_w,
            "forecast_solar_w": bundle.solar_generation.point[0], "forecast_wind_w": bundle.wind_generation.point[0],
            "P_charge_w": float(lp["charge"]), "P_discharge_w": float(plan.battery_discharge[0]),
            "P_diesel_w": float(plan.diesel_power[0]), "P_served_w": float(plan.load_served[0]),
            "P_unmet_w": float(plan.unmet_load[0]), "P_curt_w": float(plan.renewable_curtailment[0]),
            "P_solar_used_w": float(plan.solar_used[0]), "P_wind_used_w": float(plan.wind_used[0]),
            "P_E_next_wh": float(lp["E_next"]), "P_soc_after_pct": float(plan.battery_soc[0]),
            "P_objectives": json.dumps(optimizer.last_objectives, default=float),
            "charge_cap_w": charge_cap, "room_ac_w": room_ac,
            "R_charge_w": res.battery_charge_realized_w, "R_discharge_w": res.battery_discharge_realized_w,
            "R_diesel_w": res.diesel_realized_w, "R_served_w": res.served_load_w, "R_unmet_w": res.unmet_load_w,
            "R_curt_w": res.curtailment_w, "R_soc_after_pct": res.realized_soc_pct,
            "R_E_after_wh": float(res.next_state.battery_energy_wh), "R_fuel_l": res.diesel_fuel_consumed_l,
            "R_fuel_after_l": res.diesel_fuel_remaining_l, "R_busbar_err_w": res.busbar_energy_balance_error_w,
            "horizon_json": json.dumps(horizon, default=float), "e_max_wh": e_max,
        })
        state = res.next_state
    return rows


def classify_all(rows: pd.DataFrame, e_max_wh: float) -> pd.DataFrame:
    """Builds the forensic table for every G1 mismatch > 1 W with class A/B/C/D/E and flags."""
    out: List[Dict[str, Any]] = []
    for _, r in rows.iterrows():
        mismatch = abs(r.P_charge_w - r.R_charge_w)
        if mismatch <= G1_TOL_W:
            continue
        horizon = json.loads(r.horizon_json)
        tie = planner_curtailment_tie(horizon, r.E_before_wh, e_max_wh, float(np.sum(horizon["P_curt"])))
        greedy_real = min(max(0.0, r.solar_w + r.wind_w + r.R_diesel_w + r.R_discharge_w - r.demand_w),
                          r.charge_cap_w)
        if r.R_discharge_w > 1e-4:
            greedy_real = 0.0
        executor_dev = abs(r.R_charge_w - greedy_real) > G1_TOL_W
        starv_need = 5.0 + 0.25 * r.P_diesel_w / 1000.0
        starvation = bool(r.R_fuel_l > 0 and r.R_diesel_w < r.P_diesel_w - 1.0 and r.fuel_before_l < starv_need)
        pcc = bool(r.P_curt_w > G1_TOL_W and r.P_charge_w < r.charge_cap_w - G1_TOL_W
                   and r.P_charge_w < r.R_charge_w)
        plan_busbar = r.P_solar_used_w + r.P_wind_used_w + r.P_discharge_w + r.P_diesel_w - r.P_served_w - r.P_charge_w
        data_error = bool(r.solver_status != gates.OPTIMAL_STATUS or abs(r.R_busbar_err_w) > 1e-3
                          or abs(plan_busbar) > 1e-2)
        rec = {"origin_id": int(r.origin_id), "step": int(r.step), "route": r.route,
               "P_charge_w": r.P_charge_w, "R_charge_w": r.R_charge_w, "mismatch_w": mismatch,
               "P_curt_w": r.P_curt_w, "R_curt_w": r.R_curt_w, "P_discharge_w": r.P_discharge_w,
               "R_discharge_w": r.R_discharge_w, "P_diesel_w": r.P_diesel_w, "R_diesel_w": r.R_diesel_w,
               "P_served_w": r.P_served_w, "P_unmet_w": r.P_unmet_w, "R_served_w": r.R_served_w,
               "R_unmet_w": r.R_unmet_w, "E_before_wh": r.E_before_wh, "R_E_after_wh": r.R_E_after_wh,
               "solar_w": r.solar_w, "wind_w": r.wind_w, "demand_w": r.demand_w,
               "charge_cap_w": r.charge_cap_w, "room_ac_w": r.room_ac_w, "fuel_before_l": r.fuel_before_l,
               "R_fuel_after_l": r.R_fuel_after_l, "plan_busbar_residual_w": plan_busbar,
               "R_busbar_err_w": r.R_busbar_err_w, "solver_status": r.solver_status,
               "data_error": data_error, "executor_dev": bool(executor_dev), "starvation": starvation,
               "pcc": pcc, "equal_cost_tie": tie["equal_cost_tie"], "alt_minus_plan_curtailment_wh": tie["alt_minus_plan_wh"]}
        out.append(classify_row(rec))
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Population driver (AUTHORIZATION REQUIRED; not executed by CC)
# ---------------------------------------------------------------------------

def run_forensic_capture(*, authorized: bool = False, timestamp: Optional[str] = None,
                         repo: Path = REPO) -> Dict[str, Any]:
    if not authorized:
        raise PermissionError("forensic planned-capture requires explicit authorization")
    pre = verify_protected_hashes(repo)
    if pre:
        return {"status": "FORENSIC_BLOCKED", "reason": "protected hashes failed before run", "details": pre}

    ts = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = _HERE / f"forensic_planned_capture_{ts}"
    if out_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing forensic directory {out_dir}")

    origins = oracle.origins_2025_may_aug()
    if len(origins) != 123:
        return {"status": "FORENSIC_BLOCKED", "reason": f"population size {len(origins)} != 123"}
    lookup = oracle.load_sw_in_lookup()
    cfg = dict(oracle.canonical_configs())
    e_max = float(cfg["battery"].get("capacity_wh", 200000.0)) * 0.95

    all_rows: List[Dict[str, Any]] = []
    for idx, o in enumerate(origins, start=1):
        all_rows.extend(capture_origin(o, idx, lookup, cfg))
    rep = pd.DataFrame(all_rows)

    statuses_ok = bool((rep["solver_status"] == gates.OPTIMAL_STATUS).all())
    rows_ok = len(rep) == 123 * 24

    orig = pd.read_csv(ORACLE_PHYS_ORIGINAL)
    orig = orig.rename(columns={"step": "step"})
    orig_map = orig.rename(columns={"charge_w": "charge_w"})
    replay_for_cmp = pd.DataFrame({
        "origin_id": rep["origin_id"], "step": rep["step"],
        "R_charge": rep["R_charge_w"], "R_discharge": rep["R_discharge_w"], "P_diesel": rep["P_diesel_w"],
        "R_served": rep["R_served_w"], "R_unmet": rep["R_unmet_w"], "R_fuel": rep["R_fuel_l"],
        "R_soc_after": rep["R_soc_after_pct"], "R_solar": rep["solar_w"], "R_wind": rep["wind_w"],
        "R_demand": rep["demand_w"]})
    cmp = compare_to_original(replay_for_cmp, orig_map)

    g1_rows = rep.assign(mismatch=(rep.P_charge_w - rep.R_charge_w).abs())
    g1_count = int((g1_rows["mismatch"] > G1_TOL_W).sum())
    result: Dict[str, Any] = {"timestamp": ts, "rows": int(len(rep)), "rows_ok": rows_ok,
                              "statuses_all_optimal": statuses_ok, "g1_mismatch_rows": g1_count,
                              "reproduction": cmp, "protected_pre": pre}
    if not cmp["PASS"]:
        result["status"] = "FORENSIC_REPLAY_NONREPRODUCIBLE"
        return result

    out_dir.mkdir(parents=True, exist_ok=False)
    rep.drop(columns=["horizon_json"]).to_csv(out_dir / "FORENSIC_PLANNED_HOURLY.csv", index=False)
    rep[["origin_id", "step", "horizon_json"]].to_csv(out_dir / "FORENSIC_HORIZON_PLANS.csv", index=False)
    classified = classify_all(rep, e_max)
    classified.to_csv(out_dir / "FORENSIC_G1_MISMATCH_CLASSIFIED.csv", index=False)
    counts = classified["class"].value_counts().to_dict() if len(classified) else {}
    result["class_counts"] = counts
    result["starvation_rows"] = int(classified["starvation"].sum()) if len(classified) else 0
    result["planner_curtailment_tie_rows"] = int(classified["equal_cost_tie"].sum()) if len(classified) else 0
    result["max_mismatch_w_by_class"] = (classified.groupby("class")["mismatch_w"].max().to_dict()
                                         if len(classified) else {})

    post = verify_protected_hashes(repo)
    manifest = {"code_hashes": {f: sha256_file(repo / f) for f in CODE_FILES if (repo / f).exists()},
                "population": [str(o.date()) for o in origins],
                "forensic_replay": True, "campaign": False, "variant": "ORACLE-PHYS only",
                "protected_post": post}
    (out_dir / "FORENSIC_MANIFEST.json").write_text(json.dumps(manifest, indent=2, default=str))
    result["protected_post"] = post
    result["out_dir"] = str(out_dir)
    result["status"] = "FORENSIC_COMPLETE" if not post else "FORENSIC_BLOCKED"
    (out_dir / "FORENSIC_RESULT.json").write_text(json.dumps(result, indent=2, default=str))
    return result
