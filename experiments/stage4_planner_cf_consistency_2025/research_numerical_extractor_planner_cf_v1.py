"""
POLARIS Planner-CF v1 — research-only customer-first MILP (EXP-PLANNER-CF-CONSISTENCY-2025).

Implements preregistered corrections C1–C4 (PLANNER-CF-PREREG-v1.1, §3):

  C1  served load split into served_c (critical), served_nc (non-critical) and
      unmet_nc. Layer B: served_c + unmet_crit = critical. Non-critical balance
      (replaces R4): served_nc + unmet_nc = D - critical. R3 bus balance uses total
      served = served_c + served_nc.
  C2  objective priorities (complete order, §3.3):
        J1  unmet_crit   priority 5
        J_nc unmet_nc    priority 4
        J2  reserve s_j2 priority 3
        J3  fuel+startup priority 2
        J4  curtailment  priority 1
  C3  flexible sink removed: p_flex fixed at 0 W; no flex variable and no flex term.
  C4  EMERGENCY-only row references total served (served_c + served_nc).

Unchanged from the frozen research extractor (research_numerical_extractor.py):
  - reserve/EBR coefficients and Layer C form, terminal e_stage2[23] = max(ebr[23], terminal);
  - battery bounds, efficiencies, SOC bounds, charge/discharge limits;
  - diesel bounds, base 5 L/h, marginal 0.25 L/kWh, startup 2.0 L in the optimizer objective;
  - tau = 0.055 W residue protocol (extract_and_correct_flows, imported unmodified);
  - HiGHS options: output_flag False, threads 1, blend_multi_objectives False, default tolerances.

Production GAP19 (system/optimization/implementations/gap19_highs_native.py) and the frozen
research extractor are imported, never modified. DispatchPlan (production) is not modified.

Harness-only outputs (not DispatchPlan fields):
  self.last_planned          per-hour planned served_c, served_nc, unmet_crit, unmet_nc, charge, ...
  self.last_objectives       J1, J_nc, J2, J3, J4 values
  self.last_em_rows_built    number of EMERGENCY-only rows built (for audit gate G10)
  self.last_row_count        number of rows added to the HiGHS model
"""

import math
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

_REPO = Path(__file__).resolve().parents[2]
_CAND = _REPO / "experiments" / "candidate_s_sw_campaign_2024"
if str(_CAND) not in sys.path:
    sys.path.insert(0, str(_CAND))

from research_numerical_extractor import (  # noqa: E402  (frozen extractor, imported unmodified)
    ResearchNumericalGAP19Optimizer,
    TAU_RESIDUE_W,
    extract_and_correct_flows,
)

# ---------------------------------------------------------------------------
# Model layout (K = 15 per hour; no flex column; C3)
# ---------------------------------------------------------------------------
H = 24
K = 15
OFF_P_SOL_USED = 0
OFF_P_WIND_USED = 1
OFF_CURT_SOL = 2
OFF_CURT_WIND = 3
OFF_P_CHG = 4
OFF_P_DIS = 5
OFF_E_NEXT = 6
OFF_P_DIESEL = 7
OFF_SERVED_C = 8
OFF_SERVED_NC = 9
OFF_UNMET_NC = 10
OFF_U_CHG = 11
OFF_U_DIS = 12
OFF_U_DIESEL = 13
OFF_V_START = 14
IDX_UNMET_CRIT = H * K          # 360
IDX_S_J2 = IDX_UNMET_CRIT + H   # 384
NUM_VARS = IDX_S_J2 + H         # 408

# C3: flexible sink is not a variable. Its fixed value is 0 W.
FLEX_FIXED_W = 0.0

# C2: complete objective priority order (higher value = optimized first by HiGHS).
PRIORITY = {"J1": 5, "J_NC": 4, "J2": 3, "J3": 2, "J4": 1}

# Operating-mode and fuel constants (identical to the frozen extractor)
MARGINAL_FUEL_L_PER_WH = 0.00025
BASE_FUEL_L_PER_H = 5.0
STARTUP_FUEL_L = 2.0  # U8 option A: optimizer objective value, held constant


class PlannerCFV1Optimizer(ResearchNumericalGAP19Optimizer):
    """Planner-CF v1 research-only optimizer. Subclasses the frozen research extractor for
    __init__ and tau; optimize() is the Planner-CF v1 model (C1–C4)."""

    def __init__(self, tau: float = TAU_RESIDUE_W, reserve_enabled: bool = True, fuel_inventory: bool = True):
        super().__init__(tau=tau)
        self.reserve_enabled: bool = bool(reserve_enabled)
        # v1.2 (Amendment A2 §17.2): hour-0 physical fuel-feasibility row. False reproduces v1.1 exactly.
        self.fuel_inventory: bool = bool(fuel_inventory)
        self.last_planned: List[Dict[str, Any]] = []
        self.last_objectives: Dict[str, float] = {}
        self.last_em_rows_built: int = 0
        self.last_row_count: int = 0

    # ------------------------------------------------------------------
    def optimize(self, forecast_bundle, station_state: StationState, config: Dict[str, Any]) -> DispatchPlan:
        import highspy

        self.last_planned = []
        self.last_objectives = {}
        self.last_em_rows_built = 0
        self.last_row_count = 0

        opt_cfg = config.get("optimizer", {})
        operating_mode = str(getattr(station_state, "operating_mode", config.get("operating_mode", "NORMAL"))).upper()

        timestamps = forecast_bundle.timestamps
        solar_gen = list(forecast_bundle.solar_generation.point)
        wind_gen = list(forecast_bundle.wind_generation.point)
        demand = list(forecast_bundle.demand.point)

        if operating_mode == "UNKNOWN_INVALID":
            self.last_diagnostics = []
            return self._failsafe_plan(timestamps, solar_gen, wind_gen, demand, station_state, config)

        # 2. Physical asset parameters (identical to frozen extractor)
        bat_cfg = config.get("battery", {})
        capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
        min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))
        max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
        eta_chg = float(bat_cfg.get("charge_efficiency", 0.92))
        eta_dis = float(bat_cfg.get("discharge_efficiency", 0.92))
        max_p_chg = float(bat_cfg.get("max_charge_power_w", 50000.0))
        max_p_dis = float(bat_cfg.get("max_discharge_power_w", 50000.0))
        min_e_wh = capacity_wh * (min_soc_pct / 100.0)
        max_e_wh = capacity_wh * (max_soc_pct / 100.0)
        initial_e_wh = max(min_e_wh, min(max_e_wh, station_state.battery_energy_wh))

        diesel_cfg = config.get("diesel", {})
        min_diesel_w = float(diesel_cfg.get("min_power_w", 10000.0))
        max_diesel_w = float(diesel_cfg.get("max_power_w", 100000.0))
        initial_diesel_running = 1 if station_state.diesel_running else 0

        # 3. Critical demand (identical to frozen extractor)
        if forecast_bundle.demand_critical is not None:
            critical_demand = list(forecast_bundle.demand_critical.point)
        elif "critical_demand_w" in config and config["critical_demand_w"] is not None:
            cd_cfg = config["critical_demand_w"]
            if not isinstance(cd_cfg, (list, tuple)) or len(cd_cfg) != 24:
                raise ValueError("Invalid critical_demand_w configuration array length; expected 24.")
            critical_demand = [float(v) for v in cd_cfg]
        else:
            raise ValueError("MISSING_GOVERNED_INPUT: critical load trajectory is missing or unspecified.")

        for idx, (cp, dp) in enumerate(zip(critical_demand, demand)):
            if math.isnan(cp) or math.isinf(cp) or cp < 0.0:
                raise ValueError(f"Invalid protected critical load value at index {idx}: {cp}.")
            if cp > dp + 1e-4:
                raise ValueError(f"Protected critical load ({cp}W) exceeds total demand ({dp}W) at index {idx}.")

        dt = float(opt_cfg.get("timestep_hours", 1.0))

        # 4. Reserve target (EBR) and terminal, identical to frozen extractor
        ebr_target_wh_list: List[float] = []
        if getattr(station_state, "ebr_target_wh_override", None) is not None:
            ebr_target_wh_list = [float(station_state.ebr_target_wh_override)] * 24
        elif "ebr_target_wh" in config and config["ebr_target_wh"] is not None:
            ebr_cfg = config["ebr_target_wh"]
            if isinstance(ebr_cfg, (list, tuple)) and len(ebr_cfg) == 24:
                ebr_target_wh_list = [float(v) for v in ebr_cfg]
            elif isinstance(ebr_cfg, (int, float)):
                ebr_target_wh_list = [float(ebr_cfg)] * 24
            else:
                raise ValueError("Invalid ebr_target_wh configuration format.")
        else:
            for t in range(24):
                end_k = min(t + 6, 24)
                w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
                ebr_target_wh_list.append((1.0 / eta_dis) * w_crit_sum_wh)

        if getattr(station_state, "terminal_target_wh_override", None) is not None:
            terminal_target_wh = float(station_state.terminal_target_wh_override)
        elif "terminal_target_wh" in config and config["terminal_target_wh"] is not None:
            terminal_target_wh = float(config["terminal_target_wh"])
        else:
            raise ValueError("MISSING_GOVERNED_INPUT: terminal_target_wh missing or unspecified.")

        e_stage2_target = [0.0] * 24
        for t in range(23):
            e_stage2_target[t] = ebr_target_wh_list[t]
        e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)

        # ------------------------------------------------------------------
        # Variable bounds and integrality (C1, C3)
        # ------------------------------------------------------------------
        lb = np.zeros(NUM_VARS)
        ub = np.zeros(NUM_VARS)
        integrality = np.zeros(NUM_VARS, dtype=int)
        reserve_ub = capacity_wh if self.reserve_enabled else 0.0

        p_dem_list = [max(0.0, d) for d in demand]
        p_crit_list = [max(0.0, c) for c in critical_demand]
        d_nc_list = [max(0.0, pd_ - pc) for pd_, pc in zip(p_dem_list, p_crit_list)]

        for t in range(H):
            base = t * K
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_dem = p_dem_list[t]
            p_crit = p_crit_list[t]
            d_nc = d_nc_list[t]

            lb[base + OFF_P_SOL_USED], ub[base + OFF_P_SOL_USED] = 0.0, p_sol_max
            lb[base + OFF_P_WIND_USED], ub[base + OFF_P_WIND_USED] = 0.0, p_wind_max
            lb[base + OFF_CURT_SOL], ub[base + OFF_CURT_SOL] = 0.0, p_sol_max
            lb[base + OFF_CURT_WIND], ub[base + OFF_CURT_WIND] = 0.0, p_wind_max
            lb[base + OFF_P_CHG], ub[base + OFF_P_CHG] = 0.0, max_p_chg
            lb[base + OFF_P_DIS], ub[base + OFF_P_DIS] = 0.0, max_p_dis
            lb[base + OFF_E_NEXT], ub[base + OFF_E_NEXT] = min_e_wh, max_e_wh
            lb[base + OFF_P_DIESEL], ub[base + OFF_P_DIESEL] = 0.0, max_diesel_w
            lb[base + OFF_SERVED_C], ub[base + OFF_SERVED_C] = 0.0, p_crit  # C1: p_served_c <= D_c
            lb[base + OFF_SERVED_NC], ub[base + OFF_SERVED_NC] = 0.0, d_nc
            lb[base + OFF_UNMET_NC], ub[base + OFF_UNMET_NC] = 0.0, d_nc
            for off in (OFF_U_CHG, OFF_U_DIS, OFF_U_DIESEL, OFF_V_START):
                lb[base + off], ub[base + off] = 0.0, 1.0
                integrality[base + off] = 1

            lb[IDX_UNMET_CRIT + t] = 0.0
            ub[IDX_UNMET_CRIT + t] = p_crit
            lb[IDX_S_J2 + t] = 0.0
            ub[IDX_S_J2 + t] = reserve_ub

        # ------------------------------------------------------------------
        # Rows (HiGHS addRow form: lhs, rhs, n, indices, coefficients)
        # ------------------------------------------------------------------
        rows: List[tuple] = []
        em_rows = 0
        INF = math.inf

        for t in range(H):
            base = t * K
            prev = (t - 1) * K if t > 0 else None
            p_sol_max = max(0.0, solar_gen[t])
            p_wind_max = max(0.0, wind_gen[t])
            p_crit = p_crit_list[t]
            d_nc = d_nc_list[t]

            # R1 solar decomposition
            rows.append((p_sol_max, p_sol_max, [base + OFF_P_SOL_USED, base + OFF_CURT_SOL], [1.0, 1.0]))
            # R2 wind decomposition
            rows.append((p_wind_max, p_wind_max, [base + OFF_P_WIND_USED, base + OFF_CURT_WIND], [1.0, 1.0]))
            # R3 bus balance with total served (C1), no flex (C3)
            rows.append((0.0, 0.0,
                         [base + OFF_P_SOL_USED, base + OFF_P_WIND_USED, base + OFF_P_DIS, base + OFF_P_DIESEL,
                          base + OFF_SERVED_C, base + OFF_SERVED_NC, base + OFF_P_CHG],
                         [1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0]))
            # R4' non-critical balance (C1 replaces total-demand balance)
            rows.append((d_nc, d_nc, [base + OFF_SERVED_NC, base + OFF_UNMET_NC], [1.0, 1.0]))
            # R5 charge vs binary
            rows.append((-INF, 0.0, [base + OFF_P_CHG, base + OFF_U_CHG], [1.0, -max_p_chg]))
            # R6 discharge vs binary
            rows.append((-INF, 0.0, [base + OFF_P_DIS, base + OFF_U_DIS], [1.0, -max_p_dis]))
            # R7 exclusivity
            rows.append((-INF, 1.0, [base + OFF_U_CHG, base + OFF_U_DIS], [1.0, 1.0]))
            # R8 battery transition
            if t == 0:
                rows.append((initial_e_wh, initial_e_wh,
                             [base + OFF_E_NEXT, base + OFF_P_CHG, base + OFF_P_DIS],
                             [1.0, -eta_chg * dt, dt / eta_dis]))
            else:
                rows.append((0.0, 0.0,
                             [base + OFF_E_NEXT, prev + OFF_E_NEXT, base + OFF_P_CHG, base + OFF_P_DIS],
                             [1.0, -1.0, -eta_chg * dt, dt / eta_dis]))
            # R9 diesel min
            rows.append((0.0, INF, [base + OFF_P_DIESEL, base + OFF_U_DIESEL], [1.0, -min_diesel_w]))
            # R10 diesel max
            rows.append((-INF, 0.0, [base + OFF_P_DIESEL, base + OFF_U_DIESEL], [1.0, -max_diesel_w]))
            # R11 startup tracking
            if t == 0:
                rows.append((-float(initial_diesel_running), INF,
                             [base + OFF_V_START, base + OFF_U_DIESEL], [1.0, -1.0]))
            else:
                rows.append((0.0, INF,
                             [base + OFF_V_START, base + OFF_U_DIESEL, prev + OFF_U_DIESEL], [1.0, -1.0, 1.0]))

        # v1.2 (Amendment A2 §17.2): hour-0 fuel feasibility, 5*u_diesel[0] + 0.00025*p_diesel[0] <= F_rem.
        # F_rem is the remaining diesel fuel carried in the planning state. Only hour 0 is constrained.
        if self.fuel_inventory:
            fuel_rem = getattr(station_state, "diesel_fuel_remaining_liters", None)
            if fuel_rem is None:
                raise ValueError("MISSING_GOVERNED_INPUT: diesel_fuel_remaining_liters required when fuel_inventory is enabled.")
            f_rem = max(0.0, float(fuel_rem))
            rows.append((-INF, f_rem,
                         [OFF_U_DIESEL, OFF_P_DIESEL],
                         [BASE_FUEL_L_PER_H * dt, MARGINAL_FUEL_L_PER_WH * dt]))

        # Layer B: critical balance (per hour)
        for t in range(H):
            base = t * K
            p_crit = p_crit_list[t]
            rows.append((p_crit, p_crit, [base + OFF_SERVED_C, IDX_UNMET_CRIT + t], [1.0, 1.0]))

        # Layer C: reserve (per hour) — present only when reserve_enabled (ORACLE-PHYS removes it)
        if self.reserve_enabled:
            for t in range(H):
                base = t * K
                req = e_stage2_target[t] + min_e_wh
                rows.append((req, INF, [base + OFF_E_NEXT, IDX_S_J2 + t], [1.0, 1.0]))

        # EMERGENCY-only row (C4): discharge <= total served
        if operating_mode == "EMERGENCY":
            for t in range(H):
                base = t * K
                rows.append((-INF, 0.0,
                             [base + OFF_P_DIS, base + OFF_SERVED_C, base + OFF_SERVED_NC],
                             [1.0, -1.0, -1.0]))
                em_rows += 1

        # ------------------------------------------------------------------
        # Objectives (C2)
        # ------------------------------------------------------------------
        c_j1 = np.zeros(NUM_VARS)
        c_jnc = np.zeros(NUM_VARS)
        c_j2 = np.zeros(NUM_VARS)
        c_j3 = np.zeros(NUM_VARS)
        c_j4 = np.zeros(NUM_VARS)
        for t in range(H):
            base = t * K
            c_j1[IDX_UNMET_CRIT + t] = 1.0 * dt
            c_jnc[base + OFF_UNMET_NC] = 1.0 * dt
            if self.reserve_enabled:
                c_j2[IDX_S_J2 + t] = 1.0
            c_j3[base + OFF_P_DIESEL] = MARGINAL_FUEL_L_PER_WH * dt
            c_j3[base + OFF_U_DIESEL] = BASE_FUEL_L_PER_H * dt
            c_j3[base + OFF_V_START] = STARTUP_FUEL_L
            c_j4[base + OFF_CURT_SOL] = 1.0 * dt
            c_j4[base + OFF_CURT_WIND] = 1.0 * dt

        # ------------------------------------------------------------------
        # Solve (HiGHS options unchanged from frozen extractor)
        # ------------------------------------------------------------------
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

        for name, coefs in (("J1", c_j1), ("J_NC", c_jnc), ("J2", c_j2), ("J3", c_j3), ("J4", c_j4)):
            obj = highspy.HighsLinearObjective()
            obj.priority = PRIORITY[name]
            obj.weight = 1.0
            obj.offset = 0.0
            obj.abs_tolerance = 0.0
            obj.rel_tolerance = 0.0
            obj.coefficients = coefs.tolist()
            h.addLinearObjective(obj)

        h.run()
        model_status = h.getModelStatus()
        self.last_em_rows_built = em_rows
        self.last_row_count = len(rows)

        if model_status != highspy.HighsModelStatus.kOptimal:
            self.last_diagnostics = []
            return self._infeasible_plan(timestamps, solar_gen, wind_gen, demand, station_state, config, model_status)

        sol = h.getSolution()
        col_vals = np.array(sol.col_value)
        info = h.getInfo()
        mip_gap = getattr(info, "mip_gap", 0.0)

        # ------------------------------------------------------------------
        # Extraction (planned values; residue protocol on raw flows)
        # ------------------------------------------------------------------
        solar_used, wind_used, chg_out, dis_out, soc_out, diesel_out = [], [], [], [], [], []
        served_out, flex_out, curt_out, unmet_out, err_out, rshort_out = [], [], [], [], [], []
        diagnostics: List[Dict[str, Any]] = []
        planned: List[Dict[str, Any]] = []

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
            u_chg = float(col_vals[base + OFF_U_CHG])
            u_dis = float(col_vals[base + OFF_U_DIS])
            u_diesel = float(col_vals[base + OFF_U_DIESEL])
            v_start = float(col_vals[base + OFF_V_START])
            s_j2_val = max(0.0, float(col_vals[IDX_S_J2 + t])) if self.reserve_enabled else 0.0

            p_chg, p_dis, residue_corrected, zeroed_mag = extract_and_correct_flows(
                raw_p_chg, raw_p_dis, tau=self.tau)

            served_total = served_c + served_nc
            unmet_total = unmet_crit + unmet_nc
            curt_total = p_c_sol + p_c_w
            demand_t = p_dem_list[t]
            err = max(
                abs((p_sol_u + p_w_u + p_dis + p_dies) - (served_total + p_chg + FLEX_FIXED_W)),
                abs(demand_t - (served_total + unmet_total)),
            )

            diagnostics.append({
                "t": t, "raw_p_chg": raw_p_chg, "raw_p_dis": raw_p_dis,
                "corrected_p_chg": p_chg, "corrected_p_dis": p_dis,
                "u_chg": u_chg, "u_dis": u_dis, "p_diesel": p_dies, "u_diesel": u_diesel,
                "v_start": v_start, "solver_status": str(model_status), "mip_gap": float(mip_gap),
                "residue_corrected": residue_corrected, "zeroed_magnitude_w": zeroed_mag,
            })
            self.last_planned.append({
                "t": t,
                "served_c": served_c,
                "served_nc": served_nc,
                "unmet_crit": unmet_crit,
                "unmet_nc": unmet_nc,
                "charge": p_chg,
                "discharge": p_dis,
                "diesel": p_dies,
                "E_next": e_next,
                "s_j2": s_j2_val,
                "u_diesel": u_diesel,
                "v_start": v_start,
                "residue_corrected": residue_corrected,
                "zeroed_magnitude_w": zeroed_mag,
            })

            solar_used.append(round(p_sol_u, 2))
            wind_used.append(round(p_w_u, 2))
            chg_out.append(round(p_chg, 2))
            dis_out.append(round(p_dis, 2))
            soc_out.append(round(e_next / capacity_wh * 100.0, 2))
            diesel_out.append(round(p_dies, 2))
            served_out.append(round(served_total, 2))
            flex_out.append(FLEX_FIXED_W)
            curt_out.append(round(curt_total, 2))
            unmet_out.append(round(unmet_total, 2))
            err_out.append(round(err, 6))
            rshort_out.append(round(s_j2_val, 4))

        self.last_diagnostics = diagnostics

        J1 = float(np.dot(c_j1, col_vals))
        JNC = float(np.dot(c_jnc, col_vals))
        J2 = float(np.dot(c_j2, col_vals))
        J3 = float(np.dot(c_j3, col_vals))
        J4 = float(np.dot(c_j4, col_vals))
        self.last_objectives = {"J1": J1, "J_NC": JNC, "J2": J2, "J3": J3, "J4": J4}

        return DispatchPlan(
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
            objective_value=round(J3, 4),
            constraint_status="OPTIMAL",
            energy_balance_errors=err_out,
            j1_objective=round(J1, 4),
            j2_objective=round(J2, 4),
            j3_objective=round(J3, 4),
            j4_objective=round(J4, 4),
            reserve_shortfall=rshort_out,
        )

    # ------------------------------------------------------------------
    def _failsafe_plan(self, timestamps, solar_gen, wind_gen, demand, station_state, config) -> DispatchPlan:
        capacity_wh = float(config.get("battery", {}).get("capacity_wh", 200000.0))
        soc = (station_state.battery_energy_wh / capacity_wh) * 100.0
        return DispatchPlan(
            schema_version="1.0.0", timestamps=timestamps,
            solar_used=[0.0] * 24, wind_used=[0.0] * 24, battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24, battery_soc=[soc] * 24, diesel_power=[0.0] * 24,
            load_served=[0.0] * 24, flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[(s + w) for s, w in zip(solar_gen, wind_gen)],
            unmet_load=list(demand), objective_value=1e9,
            constraint_status="DEGRADED_FAILSAFE_UNKNOWN_INVALID",
            energy_balance_errors=[0.0] * 24, j1_objective=1e9, j2_objective=0.0,
            j3_objective=0.0, j4_objective=0.0, reserve_shortfall=[0.0] * 24,
        )

    def _infeasible_plan(self, timestamps, solar_gen, wind_gen, demand, station_state, config, status) -> DispatchPlan:
        capacity_wh = float(config.get("battery", {}).get("capacity_wh", 200000.0))
        return DispatchPlan(
            schema_version="1.0.0", timestamps=timestamps,
            solar_used=[0.0] * 24, wind_used=[0.0] * 24, battery_charge=[0.0] * 24,
            battery_discharge=[0.0] * 24, battery_soc=[(station_state.battery_energy_wh / capacity_wh) * 100.0] * 24,
            diesel_power=[0.0] * 24, load_served=[0.0] * 24, flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[(s + w) for s, w in zip(solar_gen, wind_gen)],
            unmet_load=list(demand), objective_value=1e9,
            constraint_status=f"OPTIMIZATION_INFEASIBLE: {status}",
            energy_balance_errors=[0.0] * 24, j1_objective=1e9, j2_objective=1e9,
            j3_objective=1e9, j4_objective=1e9, reserve_shortfall=[capacity_wh] * 24,
        )
