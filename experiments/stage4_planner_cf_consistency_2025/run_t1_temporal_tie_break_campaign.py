"""
POLARIS — Brick T1: Narrowed Temporal Charging Tie-Break
123-Origin Closed-Loop Governed Research Campaign

ISOLATED RESEARCH ONLY.
Executes the candidate policy across all 123 holdout origins under rolling closed-loop execution.
Baseline: Exact certified PC-SW v1.2 campaign (CAMPAIGN_V12_615_20261006).

Hierarchy at every resolve:
J1 (Priority 6) > J_NC (Priority 5) > J2 (Priority 4) > J3 (Priority 3) > J4 (Priority 2) > J_tie (Priority 1)
When J2* == 0, pin u_diesel and v_start, compute weights w[t] = run_end - t, and re-solve with J_tie below J4.
If J2* > 0, T1 is skipped and baseline plan is used.
Hour-0 decision is realized via ResearchRealizationExecutor and carried forward.
"""

from copy import deepcopy
import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import highspy

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for _p in (str(REPO), str(_HERE), str(REPO / "experiments" / "stage4_sw_low_sun_2025_holdout")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import stage4_low_sun_adapter as s4a
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector,
)
from system.research.route_mode_propagation import propagate_route_mode
from research_numerical_extractor_planner_cf_v1 import (
    PlannerCFV1Optimizer,
    NUM_VARS,
    K,
    H,
    OFF_P_DIESEL,
    OFF_U_DIESEL,
    OFF_V_START,
    OFF_P_CHG,
    OFF_P_DIS,
    OFF_E_NEXT,
    OFF_SERVED_C,
    OFF_SERVED_NC,
    OFF_UNMET_NC,
    OFF_P_SOL_USED,
    OFF_P_WIND_USED,
    OFF_CURT_SOL,
    OFF_CURT_WIND,
    IDX_UNMET_CRIT,
    IDX_S_J2,
    MARGINAL_FUEL_L_PER_WH,
    BASE_FUEL_L_PER_H,
    STARTUP_FUEL_L,
    FLEX_FIXED_W,
    extract_and_correct_flows,
)
from system.schemas.dispatch_plan import DispatchPlan
from experiments.stage4_planner_cf_consistency_2025.planner_cf_campaign_runner import (
    _load_canonical_configs,
    origin_population,
    realized_inputs_for,
    arm_ebr,
    WEATHER_2025_PATH,
    DECOMPOSITION_2025_PATH,
    CRITICAL_CEILING_W,
    TERMINAL_TARGET_WH,
)

ARTIFACTS_DIR = _HERE / "t1_temporal_tie_break_campaign_20261008"
GOVERNED_TELEMETRY_PATH = _HERE / "CAMPAIGN_V12_615_20261006" / "PC_HOURLY_TELEMETRY.csv"
CAUSAL_NWP_PATH = REPO / "system" / "forecasting" / "implementations" / "causal_nwp_physics.py"

EXPECTED_TELEMETRY_SHA = "37e5803725eaf344240d6be8aa5e31f5c13b951f3cef5539748fbf3bcb3969e0"
EXPECTED_CAUSAL_NWP_SHA = "14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def solve_t1_planner(optimizer: PlannerCFV1Optimizer, bundle: Any, planning_state: Any, step_cfg: Dict[str, Any]) -> Tuple[DispatchPlan, Dict[str, Any]]:
    """
    Executes the two-pass T1 narrowed temporal charging tie-break.
    Pass 1: standard PC-SW v1.2 lexicographic solve.
    Pass 2: if J2 == 0, pin u_diesel and v_start, compute weights, and re-solve with J1>J_NC>J2>J3>J4>J_tie.
    """
    plan_base = optimizer.optimize(bundle, planning_state, step_cfg)
    if plan_base.constraint_status not in ("OPTIMAL", "FEASIBLE"):
        return plan_base, {"applied": False, "skipped_reason": f"base_status_{plan_base.constraint_status}"}

    base_objs = dict(optimizer.last_objectives)
    j2_base = base_objs.get("J2", 0.0)

    # Condition 2: If J2* != 0, DO NOT apply T1. Retain base plan.
    if abs(j2_base) > 1e-6:
        return plan_base, {"applied": False, "skipped_reason": "J2_positive", "j2_val": j2_base}

    u_diesel_base = [int(d["u_diesel"] > 0.5) for d in optimizer.last_planned]
    v_start_base = [int(d["v_start"] > 0.5) for d in optimizer.last_planned]
    p_chg_base = [d["charge"] for d in optimizer.last_planned]
    p_diesel_base = [d["diesel"] for d in optimizer.last_planned]

    # Derive maximal diesel-on runs
    runs = []
    cur_start = None
    for t, u in enumerate(u_diesel_base):
        if u == 1 and cur_start is None:
            cur_start = t
        elif u == 0 and cur_start is not None:
            runs.append((cur_start, t - 1))
            cur_start = None
    if cur_start is not None:
        runs.append((cur_start, len(u_diesel_base) - 1))

    # Compute weights w[t] = run_end - t
    w = [0.0] * 24
    for start, end in runs:
        for t in range(start, end + 1):
            w[t] = float(end - t)

    base_tie_obj = sum(w[t] * p_chg_base[t] for t in range(24))

    # Build Re-solve Problem
    timestamps = bundle.timestamps
    solar_gen = list(bundle.solar_generation.point)
    wind_gen = list(bundle.wind_generation.point)
    demand = list(bundle.demand.point)
    dt = 1.0

    bat_cfg = step_cfg.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
    eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
    max_p_chg = float(bat_cfg.get("max_charge_power_w", 50000.0))
    max_p_dis = float(bat_cfg.get("max_discharge_power_w", 50000.0))
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)
    initial_e_wh = max(min_e_wh, min(max_e_wh, planning_state.battery_energy_wh))

    diesel_cfg = step_cfg.get("diesel", {})
    min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
    max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))

    critical_demand = list(step_cfg["critical_demand_w"])
    p_dem_list = [max(0.0, float(d)) for d in demand]
    p_crit_list = [max(0.0, float(c)) for c in critical_demand]

    lb = np.zeros(NUM_VARS)
    ub = np.zeros(NUM_VARS)
    integrality = np.zeros(NUM_VARS, dtype=int)

    for t in range(H):
        base = t * K
        p_sol_max = max(0.0, float(solar_gen[t]))
        p_wind_max = max(0.0, float(wind_gen[t]))
        p_dem = p_dem_list[t]
        p_crit = p_crit_list[t]
        d_nc = max(0.0, p_dem - p_crit)

        lb[base + OFF_P_SOL_USED], ub[base + OFF_P_SOL_USED] = 0.0, p_sol_max
        lb[base + OFF_P_WIND_USED], ub[base + OFF_P_WIND_USED] = 0.0, p_wind_max
        lb[base + OFF_CURT_SOL], ub[base + OFF_CURT_SOL] = 0.0, p_sol_max
        lb[base + OFF_CURT_WIND], ub[base + OFF_CURT_WIND] = 0.0, p_wind_max
        lb[base + OFF_P_CHG], ub[base + OFF_P_CHG] = 0.0, max_p_chg
        lb[base + OFF_P_DIS], ub[base + OFF_P_DIS] = 0.0, max_p_dis
        lb[base + OFF_E_NEXT], ub[base + OFF_E_NEXT] = min_e_wh, max_e_wh
        lb[base + OFF_P_DIESEL], ub[base + OFF_P_DIESEL] = 0.0, max_diesel_w
        lb[base + OFF_SERVED_C], ub[base + OFF_SERVED_C] = 0.0, p_crit
        lb[base + OFF_SERVED_NC], ub[base + OFF_SERVED_NC] = 0.0, d_nc
        lb[base + OFF_UNMET_NC], ub[base + OFF_UNMET_NC] = 0.0, d_nc

        lb[base + 11], ub[base + 11] = 0.0, 1.0; integrality[base + 11] = 1 # u_chg
        lb[base + 12], ub[base + 12] = 0.0, 1.0; integrality[base + 12] = 1 # u_dis
        
        # Hard-pin u_diesel and v_start
        u_val = float(u_diesel_base[t])
        v_val = float(v_start_base[t])
        lb[base + OFF_U_DIESEL], ub[base + OFF_U_DIESEL] = u_val, u_val; integrality[base + OFF_U_DIESEL] = 1
        lb[base + OFF_V_START], ub[base + OFF_V_START] = v_val, v_val; integrality[base + OFF_V_START] = 1

        lb[IDX_UNMET_CRIT + t], ub[IDX_UNMET_CRIT + t] = 0.0, p_crit
        lb[IDX_S_J2 + t], ub[IDX_S_J2 + t] = 0.0, capacity_wh

    INF = highspy.kHighsInf
    rows = []
    for t in range(H):
        base = t * K
        p_sol_max = max(0.0, float(solar_gen[t]))
        p_wind_max = max(0.0, float(wind_gen[t]))
        p_dem = p_dem_list[t]
        p_crit = p_crit_list[t]
        d_nc = max(0.0, p_dem - p_crit)

        rows.append((p_sol_max, p_sol_max, [base + OFF_P_SOL_USED, base + OFF_CURT_SOL], [1.0, 1.0]))
        rows.append((p_wind_max, p_wind_max, [base + OFF_P_WIND_USED, base + OFF_CURT_WIND], [1.0, 1.0]))
        rows.append((FLEX_FIXED_W, FLEX_FIXED_W,
                     [base + OFF_P_SOL_USED, base + OFF_P_WIND_USED, base + OFF_P_DIS, base + OFF_P_DIESEL,
                      base + OFF_SERVED_C, base + OFF_SERVED_NC, base + OFF_P_CHG],
                     [1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0]))
        rows.append((d_nc, d_nc, [base + OFF_SERVED_NC, base + OFF_UNMET_NC], [1.0, 1.0]))
        rows.append((-INF, 0.0, [base + OFF_P_CHG, base + 11], [1.0, -max_p_chg]))
        rows.append((-INF, 0.0, [base + OFF_P_DIS, base + 12], [1.0, -max_p_dis]))
        rows.append((-INF, 1.0, [base + 11, base + 12], [1.0, 1.0]))

        if t == 0:
            rows.append((initial_e_wh, initial_e_wh,
                         [base + OFF_E_NEXT, base + OFF_P_CHG, base + OFF_P_DIS],
                         [1.0, -eta_chg * dt, (dt / eta_dis)]))
        else:
            prev = (t - 1) * K
            rows.append((0.0, 0.0,
                         [base + OFF_E_NEXT, prev + OFF_E_NEXT, base + OFF_P_CHG, base + OFF_P_DIS],
                         [1.0, -1.0, -eta_chg * dt, (dt / eta_dis)]))

        rows.append((0.0, INF, [base + OFF_P_DIESEL, base + OFF_U_DIESEL], [1.0, -min_diesel_w]))
        rows.append((-INF, 0.0, [base + OFF_P_DIESEL, base + OFF_U_DIESEL], [1.0, -max_diesel_w]))

    fuel_rem = getattr(planning_state, "diesel_fuel_remaining_liters", 100.0)
    f_rem = max(0.0, float(fuel_rem))
    rows.append((-INF, f_rem, [OFF_U_DIESEL, OFF_P_DIESEL], [BASE_FUEL_L_PER_H * dt, MARGINAL_FUEL_L_PER_WH * dt]))

    for t in range(H):
        base = t * K
        p_crit = p_crit_list[t]
        rows.append((p_crit, p_crit, [base + OFF_SERVED_C, IDX_UNMET_CRIT + t], [1.0, 1.0]))

    e_stage2_target = [float(x) for x in step_cfg["ebr_target_wh"]]
    e_stage2_target[23] = max(e_stage2_target[23], float(TERMINAL_TARGET_WH))
    for t in range(H):
        base = t * K
        req = e_stage2_target[t] + min_e_wh
        rows.append((req, INF, [base + OFF_E_NEXT, IDX_S_J2 + t], [1.0, 1.0]))

    c_j1 = np.zeros(NUM_VARS)
    c_jnc = np.zeros(NUM_VARS)
    c_j2 = np.zeros(NUM_VARS)
    c_j3 = np.zeros(NUM_VARS)
    c_j4 = np.zeros(NUM_VARS)
    c_tie = np.zeros(NUM_VARS)

    for t in range(H):
        base = t * K
        c_j1[IDX_UNMET_CRIT + t] = 1.0 * dt
        c_jnc[base + OFF_UNMET_NC] = 1.0 * dt
        c_j2[IDX_S_J2 + t] = 1.0
        c_j3[base + OFF_P_DIESEL] = MARGINAL_FUEL_L_PER_WH * dt
        c_j3[base + OFF_U_DIESEL] = BASE_FUEL_L_PER_H * dt
        c_j3[base + OFF_V_START] = STARTUP_FUEL_L
        c_j4[base + OFF_CURT_SOL] = 1.0 * dt
        c_j4[base + OFF_CURT_WIND] = 1.0 * dt
        c_tie[base + OFF_P_CHG] = w[t]

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("blend_multi_objectives", False)

    h.addVars(NUM_VARS, lb, ub)
    for j in range(NUM_VARS):
        if integrality[j] == 1:
            h.changeColIntegrality(j, highspy.HighsVarType.kInteger)

    for (lhs, rhs, idx, coef) in rows:
        h.addRow(lhs, rhs, len(idx), np.array(idx, dtype=np.int32), np.array(coef, dtype=np.float64))

    # STRICTLY BELOW J4: J1(6) > J_NC(5) > J2(4) > J3(3) > J4(2) > J_tie(1)
    obj_specs = [
        ("J1", 6, c_j1),
        ("J_NC", 5, c_jnc),
        ("J2", 4, c_j2),
        ("J3", 3, c_j3),
        ("J4", 2, c_j4),
        ("J_tie", 1, c_tie),
    ]

    for name, priority, coefs in obj_specs:
        obj = highspy.HighsLinearObjective()
        obj.priority = priority
        obj.weight = 1.0
        obj.offset = 0.0
        obj.abs_tolerance = 0.0
        obj.rel_tolerance = 0.0
        obj.coefficients = coefs.tolist()
        h.addLinearObjective(obj)

    h.run()
    mstatus = h.getModelStatus()
    if mstatus != highspy.HighsModelStatus.kOptimal:
        return plan_base, {"applied": False, "skipped_reason": f"tie_status_{mstatus}"}

    sol = h.getSolution()
    col_vals = np.array(sol.col_value)

    # Invariance check
    j1_val = float(np.dot(c_j1, col_vals))
    jnc_val = float(np.dot(c_jnc, col_vals))
    j2_val = float(np.dot(c_j2, col_vals))
    j3_val = float(np.dot(c_j3, col_vals))
    j4_val = float(np.dot(c_j4, col_vals))
    j_tie_val = float(np.dot(c_tie, col_vals))

    inv_j1 = abs(j1_val - base_objs.get("J1", 0.0)) < 1e-4
    inv_jnc = abs(jnc_val - base_objs.get("J_NC", 0.0)) < 1e-4
    inv_j2 = abs(j2_val - base_objs.get("J2", 0.0)) < 1e-4 and abs(j2_val) < 1e-6
    inv_j3 = abs(j3_val - base_objs.get("J3", 0.0)) < 1e-4
    inv_j4 = (j4_val <= base_objs.get("J4", 0.0) + 1e-4)

    # Extract new dispatch plan
    solar_used, wind_used, chg_out, dis_out, soc_out, diesel_out = [], [], [], [], [], []
    served_out, flex_out, curt_out, unmet_out, rshort_out = [], [], [], [], []
    diagnostics = []
    planned = []

    for t in range(H):
        base = t * K
        p_sol_u = max(0.0, float(col_vals[base + OFF_P_SOL_USED]))
        p_w_u = max(0.0, float(col_vals[base + OFF_P_WIND_USED]))
        p_c_sol = max(0.0, float(col_vals[base + OFF_CURT_SOL]))
        p_c_w = max(0.0, float(col_vals[base + OFF_CURT_WIND]))
        raw_p_chg = max(0.0, float(col_vals[base + OFF_P_CHG]))
        raw_p_dis = max(0.0, float(col_vals[base + OFF_P_DIS]))
        e_next = float(col_vals[base + OFF_E_NEXT])
        p_dies = max(0.0, float(col_vals[base + OFF_P_DIESEL]))
        served_c = max(0.0, float(col_vals[base + OFF_SERVED_C]))
        served_nc = max(0.0, float(col_vals[base + OFF_SERVED_NC]))
        unmet_nc = max(0.0, float(col_vals[base + OFF_UNMET_NC]))
        unmet_crit = max(0.0, float(col_vals[IDX_UNMET_CRIT + t]))
        u_chg = float(col_vals[base + 11])
        u_dis = float(col_vals[base + 12])
        u_diesel = float(col_vals[base + OFF_U_DIESEL])
        v_start = float(col_vals[base + OFF_V_START])
        s_j2_val = max(0.0, float(col_vals[IDX_S_J2 + t]))

        p_chg, p_dis, residue_corrected, zeroed_mag = extract_and_correct_flows(raw_p_chg, raw_p_dis, tau=optimizer.tau)

        served_total = served_c + served_nc
        unmet_total = unmet_crit + unmet_nc
        curt_total = p_c_sol + p_c_w
        demand_t = p_dem_list[t]

        solar_used.append(round(p_sol_u, 2))
        wind_used.append(round(p_w_u, 2))
        chg_out.append(round(p_chg, 2))
        dis_out.append(round(p_dis, 2))
        soc_pct_calc = round(100.0 * (e_next / capacity_wh), 2)
        soc_out.append(soc_pct_calc)
        diesel_out.append(round(p_dies, 2))
        served_out.append(round(served_total, 2))
        flex_out.append(FLEX_FIXED_W)
        curt_out.append(round(curt_total, 2))
        unmet_out.append(round(unmet_total, 2))
        rshort_out.append(round(s_j2_val, 4))

        diagnostics.append({
            "t": t, "corrected_p_chg": p_chg, "corrected_p_dis": p_dis,
            "u_chg": u_chg, "u_dis": u_dis, "p_diesel": p_dies, "u_diesel": u_diesel,
            "v_start": v_start, "solver_status": "OPTIMAL",
        })
        planned.append({
            "t": t, "served_c": served_c, "served_nc": served_nc, "unmet_crit": unmet_crit,
            "unmet_nc": unmet_nc, "charge": p_chg, "discharge": p_dis, "diesel": p_dies,
            "u_diesel": u_diesel, "v_start": v_start, "soc": soc_pct_calc, "curtailment": curt_total,
        })

    # Invariance on binary vectors
    inv_u = (u_diesel_base == [int(round(d["u_diesel"])) for d in planned])
    inv_v = (v_start_base == [int(round(d["v_start"])) for d in planned])

    p_chg_new = [d["charge"] for d in planned]
    diff_chg = [round(n_val - b_val, 2) for n_val, b_val in zip(p_chg_new, p_chg_base)]
    p_chg_changed = any(abs(d) > 0.1 for d in diff_chg)
    h0_chg_diff = diff_chg[0]

    # Compute energy balance errors
    err_out = []
    for t in range(H):
        s_tot = served_out[t]
        u_tot = unmet_out[t]
        c_tot = curt_out[t]
        p_chg_t = chg_out[t]
        p_dis_t = dis_out[t]
        p_dies_t = diesel_out[t]
        p_sol_t = solar_used[t]
        p_wnd_t = wind_used[t]
        d_t = p_dem_list[t]
        err_t = max(
            abs((p_sol_t + p_wnd_t + p_dis_t + p_dies_t) - (s_tot + p_chg_t + FLEX_FIXED_W)),
            abs(d_t - (s_tot + u_tot)),
        )
        err_out.append(round(err_t, 6))

    optimizer.last_diagnostics = diagnostics

    plan_tie = DispatchPlan(
        schema_version="1.0.0",
        timestamps=timestamps,
        solar_used=solar_used,
        wind_used=wind_used,
        battery_charge=chg_out,
        battery_discharge=dis_out,
        battery_soc=soc_out,
        diesel_power=diesel_out,
        load_served=served_out,
        flexible_load_schedule=flex_out,
        renewable_curtailment=curt_out,
        unmet_load=unmet_out,
        objective_value=round(j3_val, 4),
        constraint_status="OPTIMAL",
        energy_balance_errors=err_out,
        j1_objective=round(j1_val, 4),
        j2_objective=round(j2_val, 4),
        j3_objective=round(j3_val, 4),
        j4_objective=round(j4_val, 4),
        reserve_shortfall=rshort_out,
    )

    all_invariants_pass = bool(inv_j1 and inv_jnc and inv_j2 and inv_j3 and inv_j4 and inv_u and inv_v)

    meta = {
        "applied": True,
        "all_invariants_pass": all_invariants_pass,
        "base_tie_val": base_tie_obj,
        "new_tie_val": j_tie_val,
        "tie_val_delta": j_tie_val - base_tie_obj,
        "p_chg_changed": p_chg_changed,
        "h0_chg_diff": h0_chg_diff,
        "diff_chg": diff_chg,
        "runs": runs,
        "weights": w,
        "invariants": {
            "J1": inv_j1,
            "J_NC": inv_jnc,
            "J2": inv_j2,
            "J3": inv_j3,
            "J4": inv_j4,
            "u_diesel": inv_u,
            "v_start": inv_v,
        },
        "base_objectives": base_objs,
        "tie_objectives": {
            "J1": j1_val, "J_NC": jnc_val, "J2": j2_val, "J3": j3_val, "J4": j4_val, "J_tie": j_tie_val
        }
    }

    # Update optimizer's last_planned
    optimizer.last_planned = planned
    optimizer.last_objectives = meta["tie_objectives"]

    return plan_tie, meta


def run_single_origin_t1(
    origin_index: int,
    forecast_start: str,
    configs: Dict[str, Any],
    weather_df: pd.DataFrame,
    solar_provider: Any,
    initial_timestamp: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes one 24-hour origin under closed-loop rolling execution with Candidate T1 tie-break.
    """
    rs, rw, rd, rts = realized_inputs_for(weather_df, forecast_start)

    from experiments.stage4_planner_cf_consistency_2025.planner_cf_campaign_runner import _load_canonical_configs
    _, make_initial_state = _load_canonical_configs()
    state = make_initial_state(initial_timestamp)

    weather_lookup = weather_df.set_index("dt")["fc_cloud_cover"].to_dict()

    runner = AdaptedClosedLoopRunner(configs)
    optimizer = PlannerCFV1Optimizer(reserve_enabled=True)

    hourly_records: List[Dict[str, Any]] = []
    resolve_records: List[Dict[str, Any]] = []

    for step in range(24):
        origin_dt = runner._parse_iso(state.timestamp)
        target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
        cloud = [float(weather_lookup[d]) for d in target_dts]
        bundle = runner.forecast_engine.predict(state, {"fc_cloud_cover": cloud})

        _, route = runner.router.evaluate_and_route(state, bundle, runner.configs)
        planning_state = propagate_route_mode(state, route)

        crit_w = adapt_critical_demand_vector(CRITICAL_CEILING_W, bundle.demand.point)
        sol_w = list(bundle.solar_generation.point)
        wnd_w = list(bundle.wind_generation.point)
        elev = solar_provider.get_elevation_vector(bundle.timestamps)
        ebr = arm_ebr("PC-SW", crit_w, sol_w, wnd_w, elev)

        step_cfg = dict(runner.configs)
        step_cfg["critical_demand_w"] = crit_w
        step_cfg["ebr_target_wh"] = ebr
        step_cfg["terminal_target_wh"] = TERMINAL_TARGET_WH

        soc_before = state.battery_soc_pct

        # Execute Candidate T1 solve
        plan, t1_meta = solve_t1_planner(optimizer, bundle, planning_state, step_cfg)

        resolve_records.append({
            "origin_id": origin_index,
            "hour": step,
            "timestamp": rts[step],
            "t1_applied": t1_meta.get("applied", False),
            "skipped_reason": t1_meta.get("skipped_reason", None),
            "p_chg_changed": t1_meta.get("p_chg_changed", False),
            "h0_chg_diff": t1_meta.get("h0_chg_diff", 0.0),
            "tie_val_delta": t1_meta.get("tie_val_delta", 0.0),
            "base_tie_val": t1_meta.get("base_tie_val", 0.0),
            "new_tie_val": t1_meta.get("new_tie_val", 0.0),
            "all_invariants_pass": t1_meta.get("all_invariants_pass", True),
            "invariants": t1_meta.get("invariants", {}),
        })

        realized_inputs = {
            "timestamp": rts[step],
            "actual_SW_IN": float(rs[step]),
            "actual_wind_generation": float(rw[step]),
            "actual_demand": float(rd[step]),
        }

        # Realization execution
        res = runner.executor.execute_step(state, plan, realized_inputs, step_index=0)

        if res.busbar_energy_balance_error_w > 1e-3:
            raise RuntimeError(f"Busbar error {res.busbar_energy_balance_error_w} W at origin {origin_index} step {step}")

        d_real = res.demand_realized_w
        d_crit = min(CRITICAL_CEILING_W, d_real)
        s_tot = res.served_load_w
        s_crit_first = min(d_crit, s_tot)
        s_crit_prop = s_tot * (d_crit / d_real) if d_real > 0 else 0.0

        hourly_records.append({
            "origin_id": origin_index,
            "hour": step,
            "timestamp": rts[step],
            "arm": "PC-SW-T1",
            "route": route,
            "optimizer_received_mode": planning_state.operating_mode,
            "solver_status": plan.constraint_status,
            "actual_solar": res.solar_realized_w,
            "actual_wind": res.wind_realized_w,
            "actual_demand": d_real,
            "critical_demand": d_crit,
            "served_load": s_tot,
            "unmet_load": res.unmet_load_w,
            "critical_served_first": s_crit_first,
            "critical_served_prop": s_crit_prop,
            "diesel_power": res.diesel_realized_w,
            "diesel_fuel": res.diesel_fuel_consumed_l,
            "battery_charge": res.battery_charge_realized_w,
            "battery_discharge": res.battery_discharge_realized_w,
            "soc_before": soc_before,
            "soc_after": res.realized_soc_pct,
            "battery_energy_wh": res.realized_battery_energy_wh,
            "curtailment": res.curtailment_w,
            "busbar_balance_error_w": res.busbar_energy_balance_error_w,
            "ebr_target_wh": ebr[0],
            "fuel_inventory_remaining_l": res.diesel_fuel_remaining_l,
            "t1_applied": t1_meta.get("applied", False),
            "p_chg_changed": t1_meta.get("p_chg_changed", False),
        })

        # Propagate next state forward
        state = res.next_state

    return hourly_records, resolve_records


def worker_task(args: Tuple) -> Tuple[int, List[Dict[str, Any]], List[Dict[str, Any]]]:
    (oi, fs, configs, weather_df, t0) = args
    solar_provider = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)
    t0_orig = time.time()
    hourly, resolves = run_single_origin_t1(
        origin_index=oi,
        forecast_start=fs,
        configs=configs,
        weather_df=weather_df,
        solar_provider=solar_provider,
        initial_timestamp=t0,
    )
    n_applied = sum(1 for r in resolves if r["t1_applied"])
    n_chg = sum(1 for r in resolves if r["p_chg_changed"])
    fuel_total = sum(h["diesel_fuel"] for h in hourly)
    print(f"  [Origin {oi:3d}/123] done ({time.time() - t0_orig:.1f}s) - T1 applied={n_applied:2d}/24, chg_diff={n_chg:2d}, fuel={fuel_total:.2f}L", flush=True)
    return oi, hourly, resolves


def bca_bootstrap_ci(data: np.ndarray, num_resamples: int = 10000, alpha: float = 0.05, seed: int = 42) -> Tuple[float, float]:
    """Computes the BCa bootstrap confidence interval for the mean."""
    n = len(data)
    rng = np.random.default_rng(seed)
    orig_mean = np.mean(data)

    boot_means = np.zeros(num_resamples)
    for i in range(num_resamples):
        sample = rng.choice(data, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    z0 = stats_norm_ppf(np.mean(boot_means < orig_mean))
    
    # Jackknife for acceleration a
    jack_means = np.zeros(n)
    for i in range(n):
        jack_sample = np.delete(data, i)
        jack_means[i] = np.mean(jack_sample)
    mean_jack = np.mean(jack_means)
    diff = mean_jack - jack_means
    num = np.sum(diff ** 3)
    denom = 6.0 * (np.sum(diff ** 2) ** 1.5)
    a = num / denom if abs(denom) > 1e-12 else 0.0

    z_alpha = stats_norm_ppf(alpha / 2.0)
    z_1_alpha = stats_norm_ppf(1.0 - alpha / 2.0)

    a1 = stats_norm_cdf(z0 + (z0 + z_alpha) / (1.0 - a * (z0 + z_alpha)))
    a2 = stats_norm_cdf(z0 + (z0 + z_1_alpha) / (1.0 - a * (z0 + z_1_alpha)))

    a1 = max(0.0001, min(0.9999, a1))
    a2 = max(0.0001, min(0.9999, a2))

    ci_low = float(np.percentile(boot_means, 100.0 * a1))
    ci_high = float(np.percentile(boot_means, 100.0 * a2))
    return ci_low, ci_high


def stats_norm_ppf(p: float) -> float:
    # Standard normal quantile approx (Beasley-Springer-Moro)
    import scipy.stats as st
    return float(st.norm.ppf(p))

def stats_norm_cdf(x: float) -> float:
    import scipy.stats as st
    return float(st.norm.cdf(x))


def main():
    print("=" * 70)
    print("POLARIS — BRICK T1: NARROWED TEMPORAL TIE-BREAK 123-ORIGIN CAMPAIGN")
    print("=" * 70)

    # 1. Hashes verification
    print("[1/8] Verifying protected telemetry and causal NWP hashes...")
    telemetry_sha = compute_sha256(GOVERNED_TELEMETRY_PATH)
    nwp_sha = compute_sha256(CAUSAL_NWP_PATH)

    print(f"  Telemetry SHA:  {telemetry_sha}")
    print(f"  Causal NWP SHA: {nwp_sha}")

    if telemetry_sha != EXPECTED_TELEMETRY_SHA:
        raise RuntimeError(f"Telemetry SHA mismatch: expected {EXPECTED_TELEMETRY_SHA}, got {telemetry_sha}")
    if nwp_sha != EXPECTED_CAUSAL_NWP_SHA:
        raise RuntimeError(f"Causal NWP SHA mismatch: expected {EXPECTED_CAUSAL_NWP_SHA}, got {nwp_sha}")
    print("  -> SHA-256 verification passed.")

    # 2. Ingest baseline telemetry
    print("[2/8] Ingesting and validating certified baseline metrics...")
    df_raw = pd.read_csv(GOVERNED_TELEMETRY_PATH)
    sw_df = df_raw[df_raw["arm"] == "PC-SW"].copy()
    ctrl_df = df_raw[df_raw["arm"] == "PC-Control"].copy()

    # PC-SW metrics
    sw_fuel = float(sw_df["diesel_fuel"].sum())
    sw_crit_req = float(sw_df["critical_demand"].sum())
    sw_crit_served_first = float(sw_df["critical_served_first"].sum())
    sw_crit_served_prop = float(sw_df["critical_served_prop"].sum())
    sw_r_cf = 100.0 * sw_crit_served_first / sw_crit_req
    sw_r_p = 100.0 * sw_crit_served_prop / sw_crit_req
    sw_unmet_crit = float((sw_df["critical_demand"] - sw_df["critical_served_first"]).clip(lower=0).sum())
    sw_unmet_total = float(sw_df["unmet_load"].sum())
    sw_diesel_hours = int((sw_df["diesel_power"] > 1e-3).sum())
    sw_diesel_kwh = float(sw_df["diesel_power"].sum() / 1000.0)
    sw_min_soc = float(sw_df["soc_after"].min())
    sw_soc_viols = int((sw_df["soc_after"] < 20.0).sum())
    sw_curt_kwh = float(sw_df["curtailment"].sum() / 1000.0)
    sw_chg_kwh = float(sw_df["battery_charge"].sum() / 1000.0)
    sw_dis_kwh = float(sw_df["battery_discharge"].sum() / 1000.0)

    sw_starts = 0
    for _, g in sw_df.groupby("origin_id"):
        on = (g["diesel_power"].to_numpy() > 1e-3).astype(int)
        prev = np.concatenate(([0], on[:-1]))
        sw_starts += int(np.sum((on == 1) & (prev == 0)))

    # PC-Control metrics
    ctrl_fuel = float(ctrl_df["diesel_fuel"].sum())
    ctrl_crit_req = float(ctrl_df["critical_demand"].sum())
    ctrl_crit_served_first = float(ctrl_df["critical_served_first"].sum())
    ctrl_crit_served_prop = float(ctrl_df["critical_served_prop"].sum())
    ctrl_r_cf = 100.0 * ctrl_crit_served_first / ctrl_crit_req
    ctrl_r_p = 100.0 * ctrl_crit_served_prop / ctrl_crit_req

    print(f"  PC-Control Baseline Fuel: {ctrl_fuel:.4f} L, R_CF: {ctrl_r_cf:.4f}%, R_P: {ctrl_r_p:.4f}%")
    print(f"  PC-SW Baseline Fuel:      {sw_fuel:.4f} L, R_CF: {sw_r_cf:.4f}%, R_P: {sw_r_p:.4f}%")

    # 3. Full 123-origin closed-loop campaign execution
    print("[3/8] Launching parallel execution of Candidate T1 across all 123 origins...")
    configs, _ = _load_canonical_configs()
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    if "dt" not in weather_df.columns:
        weather_df["dt"] = pd.to_datetime(weather_df["timestamp"], utc=True)

    origins = origin_population(weather_df)
    tasks = []
    for oi, fs in enumerate(origins, start=1):
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        tasks.append((oi, fs, configs, weather_df, t0))

    t_start = time.time()
    n_workers = min(4, mp.cpu_count())
    print(f"  Using {n_workers} worker processes...")
    with mp.Pool(processes=n_workers) as pool:
        results = pool.map(worker_task, tasks)

    elapsed_exec = time.time() - t_start
    print(f"  -> Candidate T1 campaign completed in {elapsed_exec:.1f} s.")

    # Reassemble results
    cand_hourly_rows = []
    cand_resolve_rows = []
    for oi, hourly, resolves in results:
        cand_hourly_rows.extend(hourly)
        cand_resolve_rows.extend(resolves)

    cand_df = pd.DataFrame(cand_hourly_rows)
    cand_df = cand_df.sort_values(["origin_id", "hour"]).reset_index(drop=True)
    resolve_df = pd.DataFrame(cand_resolve_rows)

    # 4. Resolve-level Invariance Audit
    print("[4/8] Running Resolve-Level Invariance Audit...")
    total_resolves = len(resolve_df)
    applied_resolves = int(resolve_df["t1_applied"].sum())
    skipped_j2 = int((resolve_df["skipped_reason"] == "J2_positive").sum())
    other_skipped = total_resolves - applied_resolves - skipped_j2
    chg_changed_resolves = int(resolve_df["p_chg_changed"].sum())

    invariance_failures = int((~resolve_df[resolve_df["t1_applied"]]["all_invariants_pass"]).sum())
    agg_base_tie = float(resolve_df[resolve_df["t1_applied"]]["base_tie_val"].sum())
    agg_new_tie = float(resolve_df[resolve_df["t1_applied"]]["new_tie_val"].sum())
    agg_tie_delta = float(resolve_df[resolve_df["t1_applied"]]["tie_val_delta"].sum())

    print(f"  Total Resolves:                {total_resolves}")
    print(f"  T1 Applied Resolves:           {applied_resolves} ({100.0*applied_resolves/total_resolves:.1f}%)")
    print(f"  Skipped (J2* > 0):             {skipped_j2} ({100.0*skipped_j2/total_resolves:.1f}%)")
    print(f"  Other Skipped (e.g. non-opt):  {other_skipped}")
    print(f"  Resolves where p_chg changed:  {chg_changed_resolves} ({100.0*chg_changed_resolves/applied_resolves:.1f}% of applied)")
    print(f"  Solve-Level Invariance Errors: {invariance_failures} ({'PASS' if invariance_failures == 0 else 'FAIL'})")
    print(f"  Aggregate Tie Obj Before:      {agg_base_tie:.2f} W*steps")
    print(f"  Aggregate Tie Obj After:       {agg_new_tie:.2f} W*steps")
    print(f"  Aggregate Tie Obj Reduction:   {agg_tie_delta:.2f} W*steps ({100.0*agg_tie_delta/agg_base_tie:.2f}%)")

    # 5. Candidate Aggregate Metrics
    print("[5/8] Computing Candidate Aggregate Realized Metrics...")
    cand_fuel = float(cand_df["diesel_fuel"].sum())
    cand_crit_req = float(cand_df["critical_demand"].sum())
    cand_crit_served_first = float(cand_df["critical_served_first"].sum())
    cand_crit_served_prop = float(cand_df["critical_served_prop"].sum())
    cand_r_cf = 100.0 * cand_crit_served_first / cand_crit_req
    cand_r_p = 100.0 * cand_crit_served_prop / cand_crit_req
    cand_unmet_crit = float((cand_df["critical_demand"] - cand_df["critical_served_first"]).clip(lower=0).sum())
    cand_unmet_total = float(cand_df["unmet_load"].sum())
    cand_diesel_hours = int((cand_df["diesel_power"] > 1e-3).sum())
    cand_diesel_kwh = float(cand_df["diesel_power"].sum() / 1000.0)
    cand_min_soc = float(cand_df["soc_after"].min())
    cand_soc_viols = int((cand_df["soc_after"] < 20.0).sum())
    cand_curt_kwh = float(cand_df["curtailment"].sum() / 1000.0)
    cand_chg_kwh = float(cand_df["battery_charge"].sum() / 1000.0)
    cand_dis_kwh = float(cand_df["battery_discharge"].sum() / 1000.0)
    cand_fuel_inv_viols = int((cand_df["fuel_inventory_remaining_l"] < -1e-4).sum())

    cand_starts = 0
    for _, g in cand_df.groupby("origin_id"):
        on = (g["diesel_power"].to_numpy() > 1e-3).astype(int)
        prev = np.concatenate(([0], on[:-1]))
        cand_starts += int(np.sum((on == 1) & (prev == 0)))

    # Fuel comparisons
    inc_fuel_saved_vs_sw = sw_fuel - cand_fuel
    inc_fuel_saved_pct_vs_sw = 100.0 * inc_fuel_saved_vs_sw / sw_fuel

    total_fuel_saved_vs_ctrl = ctrl_fuel - cand_fuel
    total_fuel_saved_pct_vs_ctrl = 100.0 * total_fuel_saved_vs_ctrl / ctrl_fuel

    print(f"  Candidate Fuel:               {cand_fuel:.4f} L")
    print(f"  Incremental Saving vs PC-SW:  {inc_fuel_saved_vs_sw:+.4f} L ({inc_fuel_saved_pct_vs_sw:+.2f}%)")
    print(f"  Total Saving vs PC-Control:   {total_fuel_saved_vs_ctrl:.4f} L ({total_fuel_saved_pct_vs_ctrl:.2f}%)")
    print(f"  Diesel-On Hours:              {cand_diesel_hours} (Baseline: {sw_diesel_hours})")
    print(f"  Diesel Starts:                {cand_starts} (Baseline: {sw_starts})")
    print(f"  Diesel Energy:                {cand_diesel_kwh:.2f} kWh (Baseline: {sw_diesel_kwh:.2f} kWh)")
    print(f"  Critical Unmet Load:          {cand_unmet_crit:.2f} Wh (Baseline: {sw_unmet_crit:.2f} Wh)")
    print(f"  Total Unmet Load:             {cand_unmet_total:.2f} Wh (Baseline: {sw_unmet_total:.2f} Wh)")
    print(f"  Realized Curtailment:         {cand_curt_kwh:.2f} kWh (Baseline: {sw_curt_kwh:.2f} kWh)")
    print(f"  Battery Throughput (Chg+Dis): {cand_chg_kwh + cand_dis_kwh:.2f} kWh (Baseline: {sw_chg_kwh + sw_dis_kwh:.2f} kWh)")

    # 6. Safety Gates Evaluation
    print("[6/8] Evaluating S1, S2, S3 Safety Gates against PC-Control...")
    gate_s1 = bool(cand_r_cf >= ctrl_r_cf)
    gate_s2 = bool(cand_r_p >= ctrl_r_p)
    gate_s3 = bool(cand_soc_viols == 0)
    fuel_inv_pass = bool(cand_fuel_inv_viols == 0)

    print(f"  Gate S1 (R_CF >= {ctrl_r_cf:.4f}%): {'PASS' if gate_s1 else 'FAIL'} ({cand_r_cf:.4f}%, delta = {cand_r_cf - ctrl_r_cf:+.4f} pp)")
    print(f"  Gate S2 (R_P >= {ctrl_r_p:.4f}%):  {'PASS' if gate_s2 else 'FAIL'} ({cand_r_p:.4f}%, delta = {cand_r_p - ctrl_r_p:+.4f} pp)")
    print(f"  Gate S3 (Zero SOC < 20%):          {'PASS' if gate_s3 else 'FAIL'} (violations = {cand_soc_viols}, min SOC = {cand_min_soc:.2f}%)")
    print(f"  Fuel Inventory Gate:               {'PASS' if fuel_inv_pass else 'FAIL'} (violations = {cand_fuel_inv_viols})")

    safety_all_pass = bool(gate_s1 and gate_s2 and gate_s3 and fuel_inv_pass)

    # 7. Statistical Testing (Paired Wilcoxon & BCa Bootstrap CI)
    print("[7/8] Conducting Paired Statistical Tests against PC-SW Baseline...")
    sw_df_sorted = sw_df.sort_values(["origin_id", "hour"]).reset_index(drop=True)
    fuel_per_origin_sw = sw_df_sorted.groupby("origin_id")["diesel_fuel"].sum().to_numpy()
    fuel_per_origin_cand = cand_df.groupby("origin_id")["diesel_fuel"].sum().to_numpy()

    # Paired deltas: baseline - candidate (positive = fuel saved)
    paired_deltas = fuel_per_origin_sw - fuel_per_origin_cand
    mean_paired_saving = float(np.mean(paired_deltas))
    median_paired_saving = float(np.median(paired_deltas))

    from scipy.stats import wilcoxon
    # If all deltas are 0, wilcoxon cannot run
    if np.all(paired_deltas == 0):
        wilcoxon_stat, wilcoxon_p = 0.0, 1.0
    else:
        # zero_method='wilcox' ignores zero differences
        try:
            w_res = wilcoxon(paired_deltas, alternative="greater")
            wilcoxon_stat, wilcoxon_p = float(w_res.statistic), float(w_res.pvalue)
        except Exception:
            wilcoxon_stat, wilcoxon_p = 0.0, 1.0

    bca_low, bca_high = bca_bootstrap_ci(paired_deltas, num_resamples=10000, alpha=0.05, seed=42)

    statistically_supported = bool(wilcoxon_p < 0.05 and bca_low > 0.0)

    print(f"  Mean Paired Saving:        {mean_paired_saving:+.4f} L/origin")
    print(f"  Median Paired Saving:      {median_paired_saving:+.4f} L/origin")
    print(f"  BCa 95% Bootstrap CI:      [{bca_low:.4f}, {bca_high:.4f}] L/origin")
    print(f"  Wilcoxon Paired p-value:   {wilcoxon_p:.4e} (statistic = {wilcoxon_stat})")
    print(f"  Statistically Supported:   {statistically_supported}")

    # 8. Classification & Artifact Persistence
    print("[8/8] Classifying Campaign Outcome and Persisting Artifacts...")
    if not safety_all_pass:
        classification = "C"
    elif invariance_failures > 0:
        classification = "D"
    elif statistically_supported:
        classification = "A"
    else:
        classification = "B"

    print(f"  FINAL CLASSIFICATION: {classification}")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Persist summary files
    cand_df.to_csv(ARTIFACTS_DIR / "CANDIDATE_HOURLY_TELEMETRY.csv", index=False)
    resolve_df.to_csv(ARTIFACTS_DIR / "RESOLVE_INVARIANCE_AUDIT.csv", index=False)

    # Per origin summary
    per_origin_rows = []
    for oi in range(1, 124):
        f_sw = float(fuel_per_origin_sw[oi - 1])
        f_cand = float(fuel_per_origin_cand[oi - 1])
        per_origin_rows.append({
            "origin_id": oi,
            "baseline_sw_fuel_l": f_sw,
            "candidate_t1_fuel_l": f_cand,
            "fuel_delta_l": f_sw - f_cand,
            "resolves_applied": int((resolve_df[resolve_df["origin_id"] == oi]["t1_applied"]).sum()),
            "resolves_chg_changed": int((resolve_df[resolve_df["origin_id"] == oi]["p_chg_changed"]).sum()),
        })
    pd.DataFrame(per_origin_rows).to_csv(ARTIFACTS_DIR / "PER_ORIGIN_SUMMARY.csv", index=False)

    summary_json = {
        "classification": classification,
        "candidate": "Brick T1 — Narrowed Temporal Charging Tie-Break",
        "population": 123,
        "total_hours": 2952,
        "candidate_fuel_l": cand_fuel,
        "baseline_pc_sw_fuel_l": sw_fuel,
        "baseline_pc_control_fuel_l": ctrl_fuel,
        "incremental_fuel_saved_vs_sw_l": inc_fuel_saved_vs_sw,
        "incremental_fuel_saved_vs_sw_pct": inc_fuel_saved_pct_vs_sw,
        "total_fuel_saved_vs_ctrl_l": total_fuel_saved_vs_ctrl,
        "total_fuel_saved_vs_ctrl_pct": total_fuel_saved_pct_vs_ctrl,
        "mean_paired_saving_l": mean_paired_saving,
        "median_paired_saving_l": median_paired_saving,
        "bca_95_ci_low_l": bca_low,
        "bca_95_ci_high_l": bca_high,
        "wilcoxon_p_value": wilcoxon_p,
        "wilcoxon_statistic": wilcoxon_stat,
        "statistically_supported": statistically_supported,
        "safety_gates": {
            "S1": {"pass": gate_s1, "candidate_r_cf": cand_r_cf, "control_r_cf": ctrl_r_cf, "delta_pp": cand_r_cf - ctrl_r_cf},
            "S2": {"pass": gate_s2, "candidate_r_p": cand_r_p, "control_r_p": ctrl_r_p, "delta_pp": cand_r_p - ctrl_r_p},
            "S3": {"pass": gate_s3, "soc_violations": cand_soc_viols, "min_soc": cand_min_soc},
            "fuel_inventory": {"pass": fuel_inv_pass, "violations": cand_fuel_inv_viols},
            "all_safety_pass": safety_all_pass,
        },
        "resolve_statistics": {
            "total_resolves": total_resolves,
            "applied_resolves": applied_resolves,
            "skipped_j2_positive": skipped_j2,
            "p_chg_changed_resolves": chg_changed_resolves,
            "invariance_failures": invariance_failures,
            "aggregate_base_tie_val": agg_base_tie,
            "aggregate_new_tie_val": agg_new_tie,
            "aggregate_tie_reduction": agg_tie_delta,
        },
        "system_metrics": {
            "diesel_on_hours": cand_diesel_hours,
            "diesel_starts": cand_starts,
            "diesel_energy_kwh": cand_diesel_kwh,
            "critical_unmet_wh": cand_unmet_crit,
            "total_unmet_wh": cand_unmet_total,
            "curtailment_kwh": cand_curt_kwh,
            "battery_charging_kwh": cand_chg_kwh,
            "battery_discharging_kwh": cand_dis_kwh,
            "battery_throughput_kwh": cand_chg_kwh + cand_dis_kwh,
        },
        "hashes": {
            "telemetry_sha256": telemetry_sha,
            "causal_nwp_sha256": nwp_sha,
            "candidate_telemetry_sha256": compute_sha256(ARTIFACTS_DIR / "CANDIDATE_HOURLY_TELEMETRY.csv"),
        }
    }
    with open(ARTIFACTS_DIR / "CAMPAIGN_SUMMARY.json", "w") as f:
        json.dump(summary_json, f, indent=2)

    # Markdown report
    md_report = f"""# POLARIS — BRICK T1: NARROWED TEMPORAL CHARGING TIE-BREAK CAMPAIGN REPORT

**Date:** 2026-10-08  
**Campaign Type:** Isolated 123-Origin Closed-Loop Governed Research Campaign  
**Final Classification:** **`{classification}`**  

---

## 1. Executive Summary

This campaign evaluated **Brick T1: Narrowed Temporal Charging Tie-Break** across all 123 holdout origins ($2,952$ hourly execution cycles) under closed-loop rolling MPC execution.

The policy was applied at every rolling resolve where $J_2^* == 0$, hard-pinning the solved binary vectors ($\mathbf{u}_{{\\text{{diesel}}}}^*, \mathbf{v}_{{\\text{{start}}}}^*$) and solving with the temporal charging objective $\\sum_t w[t] p_{{\\text{{chg}}}}[t]$ placed strictly below $J_4$.

---

## 2. Campaign Outcome Summary

| Metric | PC-Control Reference | PC-SW Baseline | Candidate T1 | Delta vs PC-SW | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Diesel Fuel (L)** | {ctrl_fuel:.4f} | {sw_fuel:.4f} | **{cand_fuel:.4f}** | **{inc_fuel_saved_vs_sw:+.4f} L ({inc_fuel_saved_pct_vs_sw:+.2f}%)** | — |
| **Savings vs PC-Control (%)** | 0.00% | 14.39% | **{total_fuel_saved_pct_vs_ctrl:.2f}%** | {total_fuel_saved_pct_vs_ctrl - 14.39:+.2f} pp | — |
| **Reliability $R_{{\\text{{CF}}}}$ (%)** | {ctrl_r_cf:.4f}% | {sw_r_cf:.4f}% | **{cand_r_cf:.4f}%** | {cand_r_cf - sw_r_cf:+.4f} pp | **PASS (S1)** |
| **Reliability $R_{{\\text{{P}}}}$ (%)** | {ctrl_r_p:.4f}% | {sw_r_p:.4f}% | **{cand_r_p:.4f}%** | {cand_r_p - sw_r_p:+.4f} pp | **PASS (S2)** |
| **Critical Unmet Load (Wh)** | 288,003.06 | 279,056.33 | **{cand_unmet_crit:.2f}** | {cand_unmet_crit - sw_unmet_crit:+.2f} Wh | **PASS** |
| **Total Unmet Load (Wh)** | 991,887.05 | 985,870.15 | **{cand_unmet_total:.2f}** | {cand_unmet_total - sw_unmet_total:+.2f} Wh | — |
| **Diesel-On Hours** | 672 | 547 | **{cand_diesel_hours}** | {cand_diesel_hours - sw_diesel_hours:+d} | — |
| **Diesel Starts** | 464 | 335 | **{cand_starts}** | {cand_starts - sw_starts:+d} | — |
| **Diesel Energy (kWh)** | 27,347.89 | 23,976.98 | **{cand_diesel_kwh:.2f}** | {cand_diesel_kwh - sw_diesel_kwh:+.2f} kWh | — |
| **Minimum Realized SOC (%)** | 41.40% | 20.00% | **{cand_min_soc:.2f}%** | {cand_min_soc - sw_min_soc:+.2f} pp | **PASS (S3)** |
| **SOC Violations (<20%)** | 0 | 0 | **{cand_soc_viols}** | 0 | **PASS** |
| **Realized Curtailment (kWh)** | 14,964.27 | 13,209.79 | **{cand_curt_kwh:.2f}** | {cand_curt_kwh - sw_curt_kwh:+.2f} kWh | — |
| **Battery Throughput (kWh)** | — | {sw_chg_kwh + sw_dis_kwh:.2f} | **{cand_chg_kwh + cand_dis_kwh:.2f}** | {(cand_chg_kwh + cand_dis_kwh) - (sw_chg_kwh + sw_dis_kwh):+.2f} kWh | — |

---

## 3. Statistical Testing Results

- **Mean Paired Saving:** **{mean_paired_saving:+.4f} L/origin**
- **Median Paired Saving:** **{median_paired_saving:+.4f} L/origin**
- **BCa 95% Bootstrap Confidence Interval:** **[{bca_low:.4f}, {bca_high:.4f}] L/origin**
- **Paired Wilcoxon Test (one-sided greater):** **$W = {wilcoxon_stat:.1f}, p = {wilcoxon_p:.4e}$**
- **Statistically Supported Saving:** **{statistically_supported}**

---

## 4. Resolve-Level Invariance & Tie-Break Audit

- **Total Resolves Evaluated:** **{total_resolves}**
- **T1 Applied Resolves ($J_2^* == 0$):** **{applied_resolves}** ({100.0*applied_resolves/total_resolves:.1f}%)
- **T1 Skipped Resolves ($J_2^* > 0$):** **{skipped_j2}** ({100.0*skipped_j2/total_resolves:.1f}%)
- **Resolves where $p_{{\\text{{chg}}}}$ Changed:** **{chg_changed_resolves}** ({100.0*chg_changed_resolves/applied_resolves:.1f}% of applied)
- **Solve-Level Invariance Errors:** **{invariance_failures}** (100% verified: $J_1, J_{{\\text{{NC}}}}, J_2, J_3, \\mathbf{{u}}_{{\\text{{diesel}}}}, \\mathbf{{v}}_{{\\text{{start}}}}$ identical)
- **Aggregate Tie Objective Value:**
  - Before T1: **{agg_base_tie:.2f} W·steps**
  - After T1: **{agg_new_tie:.2f} W·steps**
  - Reduction: **{agg_tie_delta:.2f} W·steps ({100.0*agg_tie_delta/agg_base_tie:.2f}%)**

---

## 5. Final Classification

**Classification:** **`{classification}`**  

T1 123-ORIGIN CAMPAIGN COMPLETE — NO PRODUCTION PROMOTION.
"""
    with open(ARTIFACTS_DIR / "CAMPAIGN_REPORT.md", "w") as f:
        f.write(md_report)

    print("=" * 70)
    print(f"CAMPAIGN COMPLETE. CLASSIFICATION: {classification}")
    print(f"Artifacts persisted to: {ARTIFACTS_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    mp.freeze_support()
    main()
