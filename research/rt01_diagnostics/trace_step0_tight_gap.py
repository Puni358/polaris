#!/usr/bin/env python3
"""
POLARIS -- RT-01 Bounded Diagnostic: Tight-MIP-Gap Re-Solve of the Step-0
LocalMILPEnergyOptimizer Problem (168h endurance scenario)
====================================================================================

Owner-authorized, bounded, ONE-TIME, read-only diagnostic (directive dated
2026-10-18, "POLARIS -- RT-01 Tight-MIP-Gap Verification (Diagnostic Only)"),
continuing directly from RT01_FULL_HORIZON_MILP_DIAGNOSTIC_REPORT.md. That
report found a provable dominance violation at hour 20 of the step-0 24-hour
MILP solve (simultaneous wind curtailment and battery discharge that can be
swapped, bus-bar-neutral, for a strict $59.19 cost reduction with no
downside) and recommended -- as its own "smallest defensible next step" --
re-running the SAME solve with scipy.optimize.milp's `mip_rel_gap` option
tightened to 0.0, to test whether the violation is a solver-tolerance
artifact (disappears at a tight gap) or a genuine formulation degeneracy
(persists regardless of gap).

What this script is, precisely:
- A NEW, standalone, external harness, copied verbatim in structure and
  non-invasive philosophy from trace_step0_full_horizon.py in this same
  directory (same runner construction, same hand-reproduced step-0 setup,
  same monkey-patch-the-scipy-reference telemetry mechanism). It imports and
  calls the real, unmodified LocalMILPEnergyOptimizer.optimize(); no source
  file is edited; only in-process, module-level attribute wrapping is used,
  verified non-destructive by re-hashing on-disk files after the run.
- Does NOT call runner.run_pipeline() -- runner.artifacts_dir
  (system/artifacts/*.json) is never touched. Reproduces, by hand, from the
  PUBLIC methods of the same already-authorized PolarisLocalRunner instance,
  the EXACT sequence run_pipeline() performs for step_idx == 0 only (same
  StationState construction, same data_provider/forecast_engine/router calls
  as trace_step0_full_horizon.py).
- THE ONLY DIFFERENCE from trace_step0_full_horizon.py: the monkey-patched
  wrapper around `system.optimization.implementations.milp.milp` (the
  scipy.optimize.milp reference LocalMILPEnergyOptimizer.optimize() calls
  internally at its line
  `res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)`,
  which passes NO `options` kwarg today -- confirmed by direct inspection of
  milp.py line 297, so scipy's own default `mip_rel_gap=0.0001` (1e-4,
  scipy 1.18.1 docstring) applies to the baseline run) now INJECTS
  `options={"mip_rel_gap": 0.0}` into the forwarded call to the ORIGINAL,
  UNMODIFIED scipy.optimize.milp function. This is in-process attribute
  shadowing only, in this script's own Python process, exactly as the prior
  script's wrapper was authorized to do for pure observation -- here it is
  additionally authorized (per this directive) to inject exactly one solver
  OPTION (a termination tolerance, not a cost, bound, or constraint) into
  the forwarded call. No file on disk is edited; milp.py's on-disk content
  and SHA-256 hash are unchanged (verified in the hash manifest below); the
  real HiGHS solver computes the real answer under the tightened tolerance.
  The patch is restored immediately after the single call.
- Same scenario, forecast, initial state, configuration, objective,
  constraints, and variable ordering as the existing trace (same scenario
  file, same runner construction, same StationState, same bundle, same c/
  integrality/bounds/constraints matrices -- only the solver's termination
  tolerance differs).

Strict boundaries honored (see directive):
- Exactly ONE additional call to LocalMILPEnergyOptimizer.optimize()
  (equivalently, one call to the real scipy.optimize.milp solver), beyond
  the one already captured in trace_step0_full_horizon.py. No 168-step (or
  any multi-step) pipeline run. No test suite, campaign, tuning, training.
- No production code, test, config, register, or protected file is edited.
  No parameter, threshold, or config value is changed from its on-disk
  value -- the ONLY thing changed is an in-memory solver option on the one
  forwarded call.
- No counterfactual/alternative solve beyond this single tightened-gap run.
- Nothing staged, committed, or pushed by this script.
- All outputs are written only under research/rt01_diagnostics/ in this
  repo; system/artifacts/*.json is never opened by this script.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = Path(__file__).resolve().parent

from system.runtime.runner import PolarisLocalRunner  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402
from system.tests.test_offline_runtime import (  # noqa: E402
    SYSTEM_DIR,
    _authorize_router_for_offline_runtime_test,
)
import system.optimization.implementations.milp as milp_module  # noqa: E402

SCENARIO_FILENAME = "synthetic_168h_endurance_scenario.json"
BASELINE_TRACE_PATH = OUTPUT_DIR / "rt01_step0_full_horizon_trace.json"

# ---------------------------------------------------------------------------
# 0. Pre-execution hash manifest -- identical target list to
#    trace_step0_full_horizon.py, so pre/post hashes are directly comparable
#    across both diagnostic passes.
# ---------------------------------------------------------------------------
HASH_TARGETS = [
    "system/optimization/implementations/milp.py",
    "system/optimization/implementations/gap19_highs_native.py",
    "system/optimization/implementations/option_d.py",
    "system/control/ecd.py",
    "system/control/router.py",
    "system/simulation/simulator.py",
    "system/runtime/runner.py",
    "system/orchestration/manifest.py",
    "system/config/optimizer.yaml",
    "system/config/battery.yaml",
    "system/config/diesel.yaml",
    "system/config/loads.yaml",
    "system/config/solar_pv.yaml",
    "system/config/station.yaml",
    f"system/data/scenarios/{SCENARIO_FILENAME}",
]


def sha256_of(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_hash_manifest() -> Dict[str, Optional[str]]:
    return {rel: sha256_of(REPO_ROOT / rel) for rel in HASH_TARGETS}


# ---------------------------------------------------------------------------
# 1. Non-invasive capture of the exact arguments/result of the single
#    scipy.optimize.milp call made inside LocalMILPEnergyOptimizer.optimize(),
#    with mip_rel_gap=0.0 INJECTED into the forwarded call only.
# ---------------------------------------------------------------------------
_capture: Dict[str, Any] = {}
_orig_scipy_milp = milp_module.milp
TIGHTENED_OPTIONS = {"mip_rel_gap": 0.0}


def _wrapped_scipy_milp_tight_gap(c=None, *, integrality=None, bounds=None, constraints=None, **kwargs):
    # milp.py's call site passes no `options` kwarg (confirmed by inspection
    # of milp.py line 297), so kwargs will not already contain "options".
    # Inject the tightened gap here, purely in-memory, on the forwarded call
    # to the ORIGINAL unmodified scipy solver.
    assert "options" not in kwargs, (
        "milp.py's call site unexpectedly already passes an 'options' kwarg; "
        "refusing to silently override -- stop and report this as a blocker."
    )
    call_kwargs = dict(kwargs)
    call_kwargs["options"] = dict(TIGHTENED_OPTIONS)
    res = _orig_scipy_milp(
        c=c, integrality=integrality, bounds=bounds, constraints=constraints, **call_kwargs
    )
    _capture["c"] = list(c)
    _capture["integrality"] = list(integrality) if integrality is not None else None
    _capture["lb"] = list(bounds.lb) if bounds is not None else None
    _capture["ub"] = list(bounds.ub) if bounds is not None else None
    _capture["constraints_lb"] = list(constraints.lb)
    _capture["constraints_ub"] = list(constraints.ub)
    _capture["A"] = constraints.A.tolist()
    _capture["res_x"] = list(res.x) if res.x is not None else None
    _capture["res_fun"] = float(res.fun) if res.fun is not None else None
    _capture["res_status"] = int(res.status)
    _capture["res_message"] = str(res.message)
    _capture["res_success"] = bool(res.success)
    _capture["mip_gap_reported"] = getattr(res, "mip_gap", None)
    _capture["options_used"] = dict(TIGHTENED_OPTIONS)
    return res


def verify_hour20_swap(sol: List[float], A: List[List[float]], c_lb: List[float], c_ub: List[float],
                        v_lb: List[float], v_ub: List[float], integrality: List[int],
                        K: int, H: int, hour: int = 20) -> Dict[str, Any]:
    """
    Constraint-by-constraint feasibility verification of the candidate
    dominance swap at `hour`: move delta = min(curt_wind[hour], dis[hour])
    from curtailment to usage (reduce p_curt_wind, increase p_wind_used) and
    reduce p_dis[hour] by the same delta, then propagate the required change
    to every future E[t] (battery energy state variable, t > hour) that the
    Battery Energy Discrete Transition constraint forces as a consequence,
    and check every row of A and every variable bound for the modified
    vector. No re-solve is performed -- this is pure arithmetic / constraint
    algebra against the model's own A/bounds matrices as actually captured
    from the real solver call.
    """
    import numpy as np
    A_np = np.array(A)
    sol_np = np.array(sol, dtype=float)
    v_lb_np = np.array(v_lb, dtype=float)
    v_ub_np = np.array(v_ub, dtype=float)
    c_lb_np = np.array(c_lb, dtype=float)
    c_ub_np = np.array(c_ub, dtype=float)

    base = hour * K
    curt_wind = sol_np[base + 3]
    wind_used = sol_np[base + 1]
    dis = sol_np[base + 5]
    chg = sol_np[base + 4]
    u_dis = sol_np[base + 12]
    u_chg = sol_np[base + 11]

    delta = min(curt_wind, dis)

    report: Dict[str, Any] = {
        "hour": hour,
        "pre_swap": {
            "p_wind_used": float(wind_used),
            "p_curt_wind": float(curt_wind),
            "p_dis": float(dis),
            "p_chg": float(chg),
            "u_dis": float(u_dis),
            "u_chg": float(u_chg),
            "E_next_wh": float(sol_np[base + 6]),
        },
        "delta_wh": float(delta),
    }

    if delta <= 1e-9:
        report["swap_available"] = False
        report["reason"] = "No simultaneous curtailment+discharge at this hour in this solution (delta <= 0); pattern does not reproduce."
        return report

    report["swap_available"] = True

    # Build modified vector
    mod = sol_np.copy()
    mod[base + 1] += delta   # p_wind_used up
    mod[base + 3] -= delta   # p_curt_wind down
    mod[base + 5] -= delta   # p_dis down

    eta_dis = None  # filled by caller via closure if needed; recompute cascade generically below
    return _finish_hour20_verification(mod, sol_np, A_np, c_lb_np, c_ub_np, v_lb_np, v_ub_np,
                                        integrality, K, H, hour, delta, report)


def _finish_hour20_verification(mod, sol_np, A_np, c_lb_np, c_ub_np, v_lb_np, v_ub_np,
                                 integrality, K, H, hour, delta, report):
    import numpy as np

    # The Battery Energy Discrete Transition constraint (row type 8) ties
    # E[hour+1] to p_chg[hour]/p_dis[hour] via:
    #   E[hour+1] - E[hour] - eta_chg*p_chg[hour]*dt + (p_dis[hour]/eta_dis)*dt == 0
    # Reducing p_dis[hour] by delta with E[hour] and p_chg[hour] UNCHANGED
    # requires E[hour+1] to change by -delta*dt/eta_dis (since the dt/eta_dis
    # coefficient on p_dis is positive in the row, reducing p_dis reduces
    # that term, so E[hour+1] must also reduce by the same amount to keep
    # the row's value at its required rhs). We solve for the exact required
    # E[hour+1] delta directly from row coefficients rather than assuming
    # eta_dis, so this is exact given the real A matrix.
    base = hour * K
    e_next_idx = base + 6
    row_idx = None
    # Locate the transition row for `hour`: the unique row with a nonzero at
    # e_next_idx and at (base+4) and (base+5), and (for hour>0) at
    # (hour-1)*K+6.
    candidate_rows = [i for i in range(A_np.shape[0]) if A_np[i, e_next_idx] != 0.0 and A_np[i, base + 5] != 0.0]
    assert len(candidate_rows) == 1, f"Expected exactly one transition row touching E[{hour+1}], found {len(candidate_rows)}"
    row_idx = candidate_rows[0]
    coeff_e_next = A_np[row_idx, e_next_idx]
    coeff_p_dis = A_np[row_idx, base + 5]
    # row value = coeff_e_next*E_next + coeff_p_dis*p_dis + (other unchanged terms) = rhs (fixed)
    # d(row value)/d(p_dis) * (-delta) + d(row value)/d(E_next) * dE_next = 0
    # => dE_next = -coeff_p_dis * (-delta) / coeff_e_next = coeff_p_dis*delta/coeff_e_next
    d_e_next = (coeff_p_dis * delta) / coeff_e_next

    cascade_deltas = {}
    e_idx = e_next_idx
    cascade_deltas[hour] = d_e_next  # E[hour+1], stored keyed by "t+1 index of hour t"
    mod[e_idx] += d_e_next

    # Propagate the same delta forward through every subsequent transition
    # row (hour+1 .. H-1) since each later row has the SAME structural form
    # E[t+1] - E[t] - ... == 0 with p_chg/p_dis at those hours UNCHANGED, so
    # a +d_e_next shift at E[hour+1] forces the identical +d_e_next shift at
    # every E[t], t = hour+2 .. H (purely a parallel shift of the SOC path,
    # with no change to any power variable at hours > hour).
    future_e_indices = [((t) * K) + 6 for t in range(hour + 1, H)]
    for idx in future_e_indices:
        mod[idx] += d_e_next

    # ------------------------------------------------------------------
    # Full feasibility check of `mod` against EVERY row of A (lb<=Ax<=ub)
    # and EVERY variable bound (v_lb<=x<=v_ub), plus integrality (binaries
    # must remain exactly 0/1 -- they are untouched by this swap).
    # ------------------------------------------------------------------
    Ax = A_np @ mod
    row_tol = 1e-6
    row_violations = []
    for i in range(A_np.shape[0]):
        lo, hi = c_lb_np[i], c_ub_np[i]
        val = Ax[i]
        if val < lo - row_tol or val > hi + row_tol:
            row_violations.append({"row": i, "value": float(val), "lb": float(lo), "ub": float(hi)})

    bound_violations = []
    for i in range(len(mod)):
        if mod[i] < v_lb_np[i] - row_tol or mod[i] > v_ub_np[i] + row_tol:
            bound_violations.append({
                "var_index": i, "t": i // K, "k": i % K,
                "value": float(mod[i]), "lb": float(v_lb_np[i]), "ub": float(v_ub_np[i]),
            })

    integrality_violations = []
    for i in range(len(mod)):
        if integrality[i] == 1:
            if abs(mod[i] - sol_np[i]) > 1e-9:
                integrality_violations.append({"var_index": i, "note": "binary value changed by swap (should not happen)"})

    future_soc_pct_deltas = {
        t: float(d_e_next) for t in range(hour + 1, H)
    }

    report.update({
        "transition_row_used": int(row_idx),
        "coeff_E_next": float(coeff_e_next),
        "coeff_p_dis": float(coeff_p_dis),
        "required_d_E_next_wh": float(d_e_next),
        "future_E_shift_wh_all_hours_after": float(d_e_next),
        "num_constraint_rows_checked": int(A_np.shape[0]),
        "num_variable_bounds_checked": int(len(mod)),
        "row_violations": row_violations,
        "bound_violations": bound_violations,
        "integrality_violations": integrality_violations,
        "feasible": (len(row_violations) == 0 and len(bound_violations) == 0 and len(integrality_violations) == 0),
    })

    # Objective delta under the model's own cost coefficients for this swap:
    # cost change = c[curt_wind]*(-delta) + c[wind_used]*0 (wind_used uncosted)
    #             + c[dis]*(-delta)
    # (E_next / SOC path has no direct cost coefficient in this model.)
    report["post_swap"] = {
        "p_wind_used": float(mod[base + 1]),
        "p_curt_wind": float(mod[base + 3]),
        "p_dis": float(mod[base + 5]),
        "E_next_wh": float(mod[base + 6]),
    }
    return report


def main() -> None:
    pre_hashes = build_hash_manifest()

    baseline = None
    if BASELINE_TRACE_PATH.exists():
        with open(BASELINE_TRACE_PATH, "r", encoding="utf-8") as f:
            baseline = json.load(f)

    # --- Build the runner EXACTLY as the existing 168h/offline tests and
    # the prior full-horizon trace do ---
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=SCENARIO_FILENAME,
        optimizer_type="milp",
    )
    _authorize_router_for_offline_runtime_test(runner)

    optimizer_class_name = type(runner.optimizer).__name__
    assert optimizer_class_name == "LocalMILPEnergyOptimizer", (
        f"Expected LocalMILPEnergyOptimizer, got {optimizer_class_name}"
    )

    first_step = runner.data_provider.timesteps[0]
    initial_state = StationState(
        timestamp=first_step["timestamp"],
        battery_soc_pct=runner.configs.get("battery", {}).get("initial_soc_pct", 50.0),
        battery_energy_wh=runner.configs.get("battery", {}).get("capacity_wh", 200000.0)
        * (runner.configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=first_step["actual_SW_IN"],
        last_observed_demand=first_step["actual_demand"],
        last_observed_wind_generation=first_step["actual_wind_generation"],
        diesel_fuel_remaining_liters=runner.configs.get("diesel", {}).get("initial_fuel_l", 100.0),
    )

    runtime_context = runner.data_provider.get_runtime_state(0)
    bundle = runner.forecast_engine.predict(initial_state, runtime_context)

    assessment, route = runner.router.evaluate_and_route(initial_state, bundle, runner.configs)

    # --- Monkey-patch the scipy solver reference used INSIDE milp.py (this
    # process only), call the real optimize() EXACTLY ONCE with mip_rel_gap
    # tightened to 0.0 on the forwarded call, then restore. ---
    milp_module.milp = _wrapped_scipy_milp_tight_gap
    try:
        plan = runner.optimizer.optimize(bundle, initial_state, runner.configs)
    finally:
        milp_module.milp = _orig_scipy_milp

    post_hashes = build_hash_manifest()
    hash_diffs = {k: (pre_hashes[k], post_hashes[k]) for k in HASH_TARGETS if pre_hashes[k] != post_hashes[k]}

    K = 15
    H = 24
    sol = _capture["res_x"]
    c = _capture["c"]

    bat_cfg = runner.configs.get("battery", {})
    capacity_wh = float(bat_cfg.get("capacity_wh", 200000.0))
    max_soc_pct = float(bat_cfg.get("max_soc_pct", 95.0))
    min_soc_pct = float(bat_cfg.get("min_soc_pct", 20.0))

    solar_gen = bundle.solar_generation.point
    wind_gen = bundle.wind_generation.point
    demand = bundle.demand.point

    horizon_rows = []
    totals = {
        "curt_sol_cost": 0.0, "curt_wind_cost": 0.0,
        "chg_cost": 0.0, "dis_cost": 0.0,
        "diesel_marginal_cost": 0.0, "diesel_base_cost": 0.0,
        "startup_cost": 0.0, "unmet_cost": 0.0,
    }

    for t in range(H):
        base = t * K
        raw = sol[base: base + K]
        idx_cost = {
            "curt_sol": c[base + 2] * raw[2],
            "curt_wind": c[base + 3] * raw[3],
            "chg": c[base + 4] * raw[4],
            "dis": c[base + 5] * raw[5],
            "diesel_marginal": c[base + 7] * raw[7],
            "unmet": c[base + 9] * raw[9],
            "diesel_base": c[base + 13] * raw[13],
            "startup": c[base + 14] * raw[14],
        }
        for k2, v2 in idx_cost.items():
            totals[{"curt_sol": "curt_sol_cost", "curt_wind": "curt_wind_cost", "chg": "chg_cost",
                     "dis": "dis_cost", "diesel_marginal": "diesel_marginal_cost", "unmet": "unmet_cost",
                     "diesel_base": "diesel_base_cost", "startup": "startup_cost"}[k2]] += v2

        soc_pct_raw = (raw[6] / capacity_wh) * 100.0

        horizon_rows.append({
            "t": t,
            "forecast_solar_w": round(float(solar_gen[t]), 2),
            "forecast_wind_w": round(float(wind_gen[t]), 2),
            "forecast_demand_w": round(float(demand[t]), 2),
            "raw_p_sol_used": round(raw[0], 4),
            "raw_p_wind_used": round(raw[1], 4),
            "raw_p_curt_sol": round(raw[2], 4),
            "raw_p_curt_wind": round(raw[3], 4),
            "raw_p_chg": round(raw[4], 4),
            "raw_p_dis": round(raw[5], 4),
            "raw_E_next_wh": round(raw[6], 4),
            "raw_soc_pct": round(soc_pct_raw, 4),
            "raw_p_diesel": round(raw[7], 4),
            "raw_p_served": round(raw[8], 4),
            "raw_p_unmet": round(raw[9], 4),
            "raw_u_chg": round(raw[11], 6),
            "raw_u_dis": round(raw[12], 6),
            "cost_curt_wind": round(idx_cost["curt_wind"], 6),
            "cost_dis": round(idx_cost["dis"], 6),
            "plan_solar_used": plan.solar_used[t],
            "plan_wind_used": plan.wind_used[t],
            "plan_battery_charge": plan.battery_charge[t],
            "plan_battery_discharge": plan.battery_discharge[t],
            "plan_battery_soc_pct": plan.battery_soc[t],
            "plan_renewable_curtailment": plan.renewable_curtailment[t],
            "plan_unmet_load": plan.unmet_load[t],
            "energy_balance_error": plan.energy_balance_errors[t],
        })

    objective_breakdown_total = sum(totals.values())

    # Identify ALL hours in THIS (tightened-gap) solution exhibiting the
    # simultaneous curtailment+discharge pattern (generic scan, not assumed
    # to still be hour 20).
    simultaneous_curtail_and_discharge_hours = [
        r["t"] for r in horizon_rows
        if r["raw_p_curt_wind"] > 1e-6 and r["raw_p_dis"] > 1e-6
    ]

    # Constraint-by-constraint verification at hour 20 specifically (the
    # hour the baseline report demonstrated the violation at), regardless of
    # whether the pattern persists there in this run -- if it does not, the
    # verification function reports swap_available=False and why.
    hour20_verification = verify_hour20_swap(
        sol=sol,
        A=_capture["A"],
        c_lb=_capture["constraints_lb"],
        c_ub=_capture["constraints_ub"],
        v_lb=_capture["lb"],
        v_ub=_capture["ub"],
        integrality=_capture["integrality"],
        K=K, H=H, hour=20,
    )

    # ------------------------------------------------------------------
    # Baseline comparison
    # ------------------------------------------------------------------
    comparison: Dict[str, Any] = {"baseline_trace_found": baseline is not None}
    if baseline is not None:
        b_solver = baseline["solver"]
        b_rows = baseline["horizon_24h"]
        b_h20 = b_rows[20]
        comparison.update({
            "baseline_res_fun": b_solver["res_fun_total_objective"],
            "tightened_res_fun": _capture["res_fun"],
            "objective_delta": round(_capture["res_fun"] - b_solver["res_fun_total_objective"], 6),
            "baseline_res_status": b_solver["res_status"],
            "tightened_res_status": _capture["res_status"],
            "baseline_res_message": b_solver["res_message"],
            "tightened_res_message": _capture["res_message"],
            "baseline_hour20_curt_wind": b_h20["raw_p_curt_wind"],
            "tightened_hour20_curt_wind": horizon_rows[20]["raw_p_curt_wind"],
            "baseline_hour20_dis": b_h20["raw_p_dis"],
            "tightened_hour20_dis": horizon_rows[20]["raw_p_dis"],
            "baseline_simultaneous_curtail_and_discharge_hours": [
                r["t"] for r in b_rows if r["raw_p_curt_wind"] > 1e-6 and r["raw_p_dis"] > 1e-6
            ],
            "tightened_simultaneous_curtail_and_discharge_hours": simultaneous_curtail_and_discharge_hours,
        })
        comparison["violation_persists_at_hour20"] = (
            horizon_rows[20]["raw_p_curt_wind"] > 1e-6 and horizon_rows[20]["raw_p_dis"] > 1e-6
        )
    else:
        comparison["note"] = "Baseline trace rt01_step0_full_horizon_trace.json not found; cannot compare."

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    if comparison.get("baseline_trace_found") and comparison["violation_persists_at_hour20"] and hour20_verification["feasible"]:
        classification = "VIOLATION_PERSISTS"
    elif comparison.get("baseline_trace_found") and not comparison["violation_persists_at_hour20"]:
        classification = "VIOLATION_DISAPPEARS"
    else:
        classification = "INCONCLUSIVE"

    out_json = OUTPUT_DIR / "rt01_step0_tight_gap_trace.json"

    payload = {
        "scenario_filename": SCENARIO_FILENAME,
        "optimizer_class": optimizer_class_name,
        "route_confirmed": route,
        "operating_mode_confirmed": assessment.operating_mode.value,
        "solver_options_injected_in_memory_only": _capture["options_used"],
        "solver": {
            "res_success": _capture["res_success"],
            "res_status": _capture["res_status"],
            "res_message": _capture["res_message"],
            "res_fun_total_objective": _capture["res_fun"],
            "mip_gap_attribute_reported": _capture["mip_gap_reported"],
            "plan_objective_value_reported": plan.objective_value,
            "plan_constraint_status": plan.constraint_status,
            "objective_breakdown_total_reconstructed": round(objective_breakdown_total, 6),
            "objective_breakdown_matches_res_fun": abs(objective_breakdown_total - _capture["res_fun"]) < 1e-3,
        },
        "objective_breakdown_by_family_24h_total_usd": {k: round(v, 4) for k, v in totals.items()},
        "simultaneous_curtail_and_discharge_hours": simultaneous_curtail_and_discharge_hours,
        "hour20_constraint_by_constraint_verification": hour20_verification,
        "baseline_vs_tightened_comparison": comparison,
        "classification": classification,
        "horizon_24h": horizon_rows,
        "pre_execution_hash_manifest": pre_hashes,
        "post_execution_hash_manifest": post_hashes,
        "hash_diffs_detected": hash_diffs,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    print("=" * 80)
    print("POLARIS RT-01 BOUNDED DIAGNOSTIC -- step-0 TIGHT-MIP-GAP (mip_rel_gap=0.0) re-solve")
    print("=" * 80)
    print(f"route_confirmed: {route}   solver: {optimizer_class_name}")
    print(f"res_success: {_capture['res_success']}   res_status: {_capture['res_status']}   res_message: {_capture['res_message']}")
    print(f"res_fun (total objective): {_capture['res_fun']}")
    print(f"simultaneous_curtail_and_discharge_hours (this run): {simultaneous_curtail_and_discharge_hours}")
    print(f"hour20_verification: {json.dumps(hour20_verification, indent=2, default=str)}")
    print(f"comparison_vs_baseline: {json.dumps(comparison, indent=2, default=str)}")
    print(f"CLASSIFICATION: {classification}")
    print(f"hash_diffs_detected (should be empty): {hash_diffs}")
    print(f"\nWrote: {out_json}")
    print("=" * 80)


if __name__ == "__main__":
    main()
