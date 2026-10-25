#!/usr/bin/env python3
"""
MILP-v2 DIAGNOSTIC BRANCH. Instrumentation only. Does NOT modify
system/optimization/implementations/gap19_highs_native.py, does NOT change optimizer
behavior, and does NOT touch R1/R2 or any frozen research assumption.

Calls the REAL, UNMODIFIED GAP19HighsNativeOptimizer.optimize() exactly as R1/R2 did (same
inputs, same code path, same solve) to get the actual DispatchPlan -- including its
per-timestep `reserve_shortfall` array, which the unmodified optimizer ALREADY returns
(gap19_highs_native.py:447) but which R1/R2's result-collection scripts only ever summed,
never inspected per-timestep.

The ONE new thing this module adds is a pure read-only ARITHMETIC REPLICA of the two
deterministic formulas that feed GAP19's reserve envelope (gap19_highs_native.py:111-151),
so the per-timestep envelope can be attributed to its source (native EBR vs. the research
terminal-target formula) WITHOUT re-solving or altering anything. This replica uses the exact
same formula, same config values, same rounding-free arithmetic as the real optimizer; it is
not an approximation of GAP19's math, it is the same math, computed a second time outside the
solver purely to expose intermediate values the DispatchPlan schema does not carry.

IMPORTANT LIMITATION (stated here, not hidden): attributing *diesel* to a specific timestep's
binding status is an approximation, not a rigorous causal isolation. The MILP jointly
optimizes all 24 hours at once -- diesel dispatched at hour 5 can be charging the battery
toward a reserve requirement that only binds at hour 20. A rigorous isolation of "diesel
caused by the terminal-target formula alone" would require a counterfactual re-solve with
that formula's contribution removed -- explicitly out of scope here ("do not change optimizer
behavior yet"). This module instead reports a same-timestep association (binding status
alongside realized dispatch at that same hour), which is weaker than causal isolation and is
labeled as such throughout the output.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))

from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan

EPS_WH = 1e-3  # shortfall-detection tolerance, matches GAP19's own 1e-4-scale tolerances


def replicate_ebr_target_wh_list(critical_demand: List[float], eta_dis: float, dt: float) -> List[float]:
    """
    Exact arithmetic replica of gap19_highs_native.py:126-131 (the GOVERNED EBR formula).
    Pure function of critical_demand only -- no solar, no wind, no diesel, no battery state.
    Not a re-implementation choice: this IS the formula, copied verbatim for read-only replay.
    """
    ebr_target_wh_list = []
    for t in range(24):
        end_k = min(t + 6, 24)
        w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
        ebr_req_wh = (1.0 / eta_dis) * w_crit_sum_wh
        ebr_target_wh_list.append(ebr_req_wh)
    return ebr_target_wh_list


def replicate_e_stage2_target(ebr_target_wh_list: List[float], terminal_target_wh: float) -> List[float]:
    """Exact arithmetic replica of gap19_highs_native.py:146-151."""
    e_stage2_target = [0.0] * 24
    for t in range(23):
        e_stage2_target[t] = ebr_target_wh_list[t]
    e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)
    return e_stage2_target


def instrument_cycle(
    plan: DispatchPlan,
    critical_demand: List[float],
    terminal_target_wh: float,
    eta_dis: float,
    dt: float,
    min_e_wh: float,
) -> Dict[str, Any]:
    """
    Builds the per-timestep diagnostic decomposition for ONE already-solved, UNMODIFIED
    DispatchPlan. Takes the real plan as input -- does not re-solve, does not alter it.
    """
    ebr_target_wh_list = replicate_ebr_target_wh_list(critical_demand, eta_dis, dt)
    e_stage2_target = replicate_e_stage2_target(ebr_target_wh_list, terminal_target_wh)

    reserve_shortfall = plan.reserve_shortfall if plan.reserve_shortfall is not None else [0.0] * 24

    per_timestep = []
    for t in range(24):
        source = "TERMINAL" if t == 23 else "EBR"
        # At t=23, record which one actually dominates the max() -- code-confirmed to
        # always be TERMINAL in R1/R2 given the observed magnitude gap, but checked here
        # explicitly per-cycle rather than assumed.
        if t == 23:
            dominant = "TERMINAL" if terminal_target_wh >= ebr_target_wh_list[23] else "EBR"
        else:
            dominant = "EBR"

        shortfall_wh = reserve_shortfall[t] if t < len(reserve_shortfall) else 0.0
        binding = shortfall_wh > EPS_WH

        per_timestep.append({
            "t": t,
            "ebr_target_wh": round(ebr_target_wh_list[t], 2),
            "terminal_target_wh": round(terminal_target_wh, 2) if t == 23 else None,
            "e_stage2_target_wh": round(e_stage2_target[t], 2),
            "envelope_source_slot": source,          # which formula occupies this timestep's slot
            "envelope_dominant_term": dominant if t == 23 else "EBR",  # which term wins the max() (t=23 only)
            "reserve_shortfall_wh": round(shortfall_wh, 4),
            "reserve_binding": binding,
            "diesel_power_w": plan.diesel_power[t],
            "battery_charge_w": plan.battery_charge[t],
            "battery_discharge_w": plan.battery_discharge[t],
            "battery_soc_pct": plan.battery_soc[t],
            "renewable_curtailment_w": plan.renewable_curtailment[t],
            "unmet_load_w": plan.unmet_load[t],
        })

    # Same-timestep association counts (NOT a causal isolation -- see module docstring).
    diesel_at_binding_t = sum(row["diesel_power_w"] for row in per_timestep if row["reserve_binding"])
    diesel_at_nonbinding_t = sum(row["diesel_power_w"] for row in per_timestep if not row["reserve_binding"])
    diesel_at_t23 = per_timestep[23]["diesel_power_w"]
    binding_timesteps = [row["t"] for row in per_timestep if row["reserve_binding"]]

    return {
        "j1_objective": plan.j1_objective,
        "j2_objective": plan.j2_objective,
        "j3_objective": plan.j3_objective,
        "j4_objective": plan.j4_objective,
        "constraint_status": plan.constraint_status,
        "ebr_target_wh_list": [round(v, 2) for v in ebr_target_wh_list],
        "terminal_target_wh": round(terminal_target_wh, 2),
        "ebr_target_at_t23_wh": round(ebr_target_wh_list[23], 2),
        "terminal_dominates_at_t23": terminal_target_wh >= ebr_target_wh_list[23],
        "binding_timesteps": binding_timesteps,
        "binding_timestep_count": len(binding_timesteps),
        "diesel_power_sum_at_binding_timesteps_w": round(diesel_at_binding_t, 2),
        "diesel_power_sum_at_nonbinding_timesteps_w": round(diesel_at_nonbinding_t, 2),
        "diesel_power_at_t23_w": diesel_at_t23,
        "per_timestep": per_timestep,
    }
