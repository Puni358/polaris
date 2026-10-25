"""
Validation script for Narrowed Temporal Tie-Break Formulation.
Tests Origins: 2, 3, 4, 9, 11, 14
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import highspy

from experiments.stage4_planner_cf_consistency_2025.planner_cf_campaign_runner import (
    _load_canonical_configs,
    origin_population,
    WEATHER_2025_PATH,
    DECOMPOSITION_2025_PATH,
    arm_ebr,
    CRITICAL_CEILING_W,
    TERMINAL_TARGET_WH,
)
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
import stage4_low_sun_adapter as s4a
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector,
)
from system.research.route_mode_propagation import propagate_route_mode

def run_validation_for_origin(origin_id, origins, weather_lookup, configs, make_initial_state, solar_provider):
    fs = origins[origin_id - 1]
    t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    state = make_initial_state(t0)
    runner = AdaptedClosedLoopRunner(configs)
    opt = PlannerCFV1Optimizer(reserve_enabled=True)

    origin_dt = runner._parse_iso(state.timestamp)
    target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
    cloud = [float(weather_lookup[d]) for d in target_dts]
    bundle = runner.forecast_engine.predict(state, {'fc_cloud_cover': cloud})

    _, route = runner.router.evaluate_and_route(state, bundle, runner.configs)
    planning_state = propagate_route_mode(state, route)

    crit_w = adapt_critical_demand_vector(CRITICAL_CEILING_W, bundle.demand.point)
    sol_w = list(bundle.solar_generation.point)
    wnd_w = list(bundle.wind_generation.point)
    elev = solar_provider.get_elevation_vector(bundle.timestamps)
    ebr = arm_ebr('PC-SW', crit_w, sol_w, wnd_w, elev)

    step_cfg = dict(runner.configs)
    step_cfg['critical_demand_w'] = crit_w
    step_cfg['ebr_target_wh'] = ebr
    step_cfg['terminal_target_wh'] = TERMINAL_TARGET_WH

    # 1. Baseline Solve
    plan_base = opt.optimize(bundle, planning_state, step_cfg)
    obj_base = dict(opt.last_objectives)
    
    # Check J2 == 0 requirement
    j2_base = obj_base.get('J2', 0.0)
    if abs(j2_base) > 1e-6:
        return {
            'origin_id': origin_id,
            'status': 'SKIPPED',
            'reason': f'J2_optimal = {j2_base} != 0',
        }

    u_diesel_base = [int(d['u_diesel'] > 0.5) for d in opt.last_planned]
    v_start_base = [int(d['v_start'] > 0.5) for d in opt.last_planned]
    p_chg_base = [d['charge'] for d in opt.last_planned]
    p_diesel_base = [d['diesel'] for d in opt.last_planned]

    # 2. Derive diesel runs
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

    # 3. Compute fixed weights w[t] = run_end - t
    w = [0.0] * 24
    for start, end in runs:
        for t in range(start, end + 1):
            w[t] = float(end - t)

    base_tie_val = sum(w[t] * p_chg_base[t] for t in range(24))

    # 4. Build Re-solve Problem
    solar_gen = list(bundle.solar_generation.point)
    wind_gen = list(bundle.wind_generation.point)
    demand = list(bundle.demand.point)
    dt = 1.0

    bat_cfg = step_cfg.get('battery', {})
    capacity_wh = float(bat_cfg.get('capacity_wh', 200000.0))
    min_soc_pct = float(bat_cfg.get('min_soc_pct', 20.0))
    max_soc_pct = float(bat_cfg.get('max_soc_pct', 95.0))
    eta_chg = float(bat_cfg.get('charge_efficiency', 0.92))
    eta_dis = float(bat_cfg.get('discharge_efficiency', 0.92))
    max_p_chg = float(bat_cfg.get('max_charge_power_w', 50000.0))
    max_p_dis = float(bat_cfg.get('max_discharge_power_w', 50000.0))
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)
    initial_e_wh = max(min_e_wh, min(max_e_wh, planning_state.battery_energy_wh))

    diesel_cfg = step_cfg.get('diesel', {})
    min_diesel_w = float(diesel_cfg.get('min_power_w', 10000.0))
    max_diesel_w = float(diesel_cfg.get('max_power_w', 100000.0))

    critical_demand = list(crit_w)
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
        
        # PINNED u_diesel and v_start:
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

    fuel_rem = getattr(planning_state, 'diesel_fuel_remaining_liters', 100.0)
    f_rem = max(0.0, float(fuel_rem))
    rows.append((-INF, f_rem, [OFF_U_DIESEL, OFF_P_DIESEL], [BASE_FUEL_L_PER_H * dt, MARGINAL_FUEL_L_PER_WH * dt]))

    for t in range(H):
        base = t * K
        p_crit = p_crit_list[t]
        rows.append((p_crit, p_crit, [base + OFF_SERVED_C, IDX_UNMET_CRIT + t], [1.0, 1.0]))

    e_stage2_target = [float(x) for x in ebr]
    e_stage2_target[23] = max(e_stage2_target[23], float(TERMINAL_TARGET_WH))
    for t in range(H):
        base = t * K
        req = e_stage2_target[t] + min_e_wh
        rows.append((req, INF, [base + OFF_E_NEXT, IDX_S_J2 + t], [1.0, 1.0]))

    c_j1 = np.zeros(NUM_VARS)
    c_jnc = np.zeros(NUM_VARS)
    c_j2 = np.zeros(NUM_VARS)
    c_j3 = np.zeros(NUM_VARS)
    c_tie = np.zeros(NUM_VARS)
    c_j4 = np.zeros(NUM_VARS)

    for t in range(H):
        base = t * K
        c_j1[IDX_UNMET_CRIT + t] = 1.0 * dt
        c_jnc[base + OFF_UNMET_NC] = 1.0 * dt
        c_j2[IDX_S_J2 + t] = 1.0
        c_j3[base + OFF_P_DIESEL] = MARGINAL_FUEL_L_PER_WH * dt
        c_j3[base + OFF_U_DIESEL] = BASE_FUEL_L_PER_H * dt
        c_j3[base + OFF_V_START] = STARTUP_FUEL_L
        c_tie[base + OFF_P_CHG] = w[t]
        c_j4[base + OFF_CURT_SOL] = 1.0 * dt
        c_j4[base + OFF_CURT_WIND] = 1.0 * dt

    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    h.setOptionValue('threads', 1)
    h.setOptionValue('blend_multi_objectives', False)

    h.addVars(NUM_VARS, lb, ub)
    for j in range(NUM_VARS):
        if integrality[j] == 1:
            h.changeColIntegrality(j, highspy.HighsVarType.kInteger)

    for (lhs, rhs, idx, coef) in rows:
        h.addRow(lhs, rhs, len(idx), np.array(idx, dtype=np.int32), np.array(coef, dtype=np.float64))

    obj_specs = [
        ('J1', 6, c_j1),
        ('J_NC', 5, c_jnc),
        ('J2', 4, c_j2),
        ('J3', 3, c_j3),
        ('J_tie', 2, c_tie),
        ('J4', 1, c_j4),
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
        return {'origin_id': origin_id, 'status': 'INFEASIBLE', 'reason': str(mstatus)}

    sol = h.getSolution()
    col_vals = np.array(sol.col_value)

    p_chg_tie = []
    p_diesel_tie = []
    u_diesel_tie = []
    v_start_tie = []
    for t in range(H):
        base = t * K
        raw_p_chg = max(0.0, float(col_vals[base + OFF_P_CHG]))
        raw_p_dis = max(0.0, float(col_vals[base + OFF_P_DIS]))
        chg, _, _, _ = extract_and_correct_flows(raw_p_chg, raw_p_dis, tau=0.055)
        p_chg_tie.append(chg)
        p_diesel_tie.append(max(0.0, float(col_vals[base + OFF_P_DIESEL])))
        u_diesel_tie.append(int(round(col_vals[base + OFF_U_DIESEL])))
        v_start_tie.append(int(round(col_vals[base + OFF_V_START])))

    obj_tie_results = {
        'J1': float(np.dot(c_j1, col_vals)),
        'J_NC': float(np.dot(c_jnc, col_vals)),
        'J2': float(np.dot(c_j2, col_vals)),
        'J3': float(np.dot(c_j3, col_vals)),
        'J_tie': float(np.dot(c_tie, col_vals)),
        'J4': float(np.dot(c_j4, col_vals)),
    }

    fuel_base = sum(5.0 * u + 0.00025 * d for u, d in zip(u_diesel_base, p_diesel_base))
    fuel_tie = sum(5.0 * u + 0.00025 * d for u, d in zip(u_diesel_tie, p_diesel_tie))

    diff_chg = [round(t_val - b_val, 2) for t_val, b_val in zip(p_chg_tie, p_chg_base)]
    reallocated = any(abs(d) > 0.1 for d in diff_chg)

    # Gate evaluations
    gate_j1 = abs(obj_tie_results['J1'] - obj_base['J1']) < 1e-4
    gate_jnc = abs(obj_tie_results['J_NC'] - obj_base['J_NC']) < 1e-4
    gate_j2 = abs(obj_tie_results['J2'] - obj_base['J2']) < 1e-4 and abs(obj_tie_results['J2']) < 1e-6
    gate_j3 = abs(obj_tie_results['J3'] - obj_base['J3']) < 1e-4
    gate_u = (u_diesel_tie == u_diesel_base)
    gate_v = (v_start_tie == v_start_base)
    gate_fuel = abs(fuel_tie - fuel_base) < 1e-4
    gate_tie_val = (obj_tie_results['J_tie'] <= base_tie_val + 1e-4)
    gate_j4 = (obj_tie_results['J4'] <= obj_base['J4'] + 1e-4)

    all_gates_pass = (
        gate_j1 and gate_jnc and gate_j2 and gate_j3 and
        gate_u and gate_v and gate_fuel and gate_tie_val and gate_j4
    )

    return {
        'origin_id': origin_id,
        'status': 'SUCCESS',
        'all_gates_pass': all_gates_pass,
        'reallocated': reallocated,
        'runs': runs,
        'weights': w,
        'base': {
            'J1': obj_base['J1'],
            'J_NC': obj_base['J_NC'],
            'J2': obj_base['J2'],
            'J3': obj_base['J3'],
            'J4': obj_base['J4'],
            'J_tie': base_tie_val,
            'fuel': fuel_base,
            'u_diesel': u_diesel_base,
            'v_start': v_start_base,
            'p_chg': [round(x, 2) for x in p_chg_base],
            'p_diesel': [round(x, 2) for x in p_diesel_base],
        },
        'tie_break': {
            'J1': obj_tie_results['J1'],
            'J_NC': obj_tie_results['J_NC'],
            'J2': obj_tie_results['J2'],
            'J3': obj_tie_results['J3'],
            'J4': obj_tie_results['J4'],
            'J_tie': obj_tie_results['J_tie'],
            'fuel': fuel_tie,
            'u_diesel': u_diesel_tie,
            'v_start': v_start_tie,
            'p_chg': [round(x, 2) for x in p_chg_tie],
            'p_diesel': [round(x, 2) for x in p_diesel_tie],
        },
        'diff_chg': diff_chg,
        'gates': {
            'J1_identical': gate_j1,
            'J_NC_identical': gate_jnc,
            'J2_identical_and_zero': gate_j2,
            'J3_identical': gate_j3,
            'u_diesel_identical': gate_u,
            'v_start_identical': gate_v,
            'fuel_identical': gate_fuel,
            'tie_break_obj_le_base': gate_tie_val,
            'J4_not_increased': gate_j4,
        }
    }

def main():
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    if 'dt' not in weather_df.columns:
        weather_df['dt'] = pd.to_datetime(weather_df['timestamp'], utc=True)
    origins = origin_population(weather_df)
    solar_provider = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)
    configs, make_initial_state = _load_canonical_configs()
    weather_lookup = weather_df.set_index('dt')['fc_cloud_cover'].to_dict()

    test_origins = [2, 3, 4, 9, 11, 14]
    results = []
    for oi in test_origins:
        res = run_validation_for_origin(oi, origins, weather_lookup, configs, make_initial_state, solar_provider)
        results.append(res)

    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
