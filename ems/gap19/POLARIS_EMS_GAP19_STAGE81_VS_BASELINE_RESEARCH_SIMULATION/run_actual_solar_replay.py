#!/usr/bin/env python3
"""
ACTUAL-SOLAR REPLAY. RESEARCH-ONLY. NOT a production run. NOT a re-optimization.

For every NORMAL-route origin (of the frozen 347-origin R1/R2 window), generates the GAP19
dispatch plan exactly as the ORIGINAL (unablated) R1/R2 harness does -- same
compute_terminal_target_wh formula, same config, same router, same optimizer, same
StationState construction, imported and called unmodified from run_full_experiment.py /
run_research_simulation.py (no monkeypatch in this script; this is the real R1/R2 planning
step, re-run only because the frozen result-collection code did not retain full per-hour
arrays, only per-cycle sums).

Then REPLAYS each plan's already-decided, FIXED controllable commands
(battery_charge[t], battery_discharge[t], diesel_power[t] -- never re-decided here) against
the REAL ground-truth realized solar (`actual_SW_IN`, converted via the same
provenance-documented PV formula already used in this diagnostic branch) for that origin's
24-hour horizon. Wind and demand (and critical_demand derived from it) are held IDENTICAL to
what the plan already used -- this experiment isolates solar-forecast accuracy only, exactly
matching R1/R2's own "solar ablation" design; it does not introduce a new wind/demand
ground-truth substitution.

Replay physics (new analysis code, not a GAP19 re-optimization -- GAP19 is never called a
second time for any origin):
  - diesel_power[t] and battery_discharge[t]: executed EXACTLY as planned, unconditionally
    (these are committed hardware dispatch commands in this model; they do not depend on
    solar and are never reduced or increased by this script).
  - battery_charge[t]: executed up to the PLANNED amount, but clipped down to whatever
    energy is actually available after critical load is served (critical load always has
    priority over charging -- the same priority GAP19's own J1 >> J4 structure encodes;
    stated explicitly here as a replay-only modeling assumption, not discovered from GAP19
    code, since GAP19 itself is never asked to resolve this across-plan, not a single
    MILP solve, question).
  - unmet_load[t]: whatever of critical_demand[t] cannot be covered even after fully
    reducing the realized charge to zero.
  - curtailment[t]: whatever actual solar+wind is not needed once critical load and the
    (possibly-clipped) charge are both satisfied.
  - realized battery SOC trajectory: computed hour-by-hour with the exact
    `curr_e_wh += (p_chg*eta_chg - p_dis/eta_dis)` formula already used, unmodified, in
    `system/simulation/simulator.py:44` (reused as the same physics, not re-derived) --
    checked against the configured [min_soc_pct, max_soc_pct] bounds at every hour, flagged
    if violated (this IS the reliability check this experiment is for).

No production code, config, or frozen artifact is modified. GAP19 is called only in its
normal, frozen way (planning), never with actual solar as an input.
"""
import sys
import json
import time
from pathlib import Path

import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

import run_full_experiment as rfe
from system.schemas.station_state import StationState
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES

MATRIX_PATH = rfe.MATRIX_PATH


def pv_from_sw_in(sw_in_w_m2: float) -> float:
    """VERIFIED formula from the frozen fixture's own provenance_manifest
    (system/data/scenarios/h10_scenario_temp.json): min(SW_IN * 300 * 0.20 * 0.85, 60000)."""
    return min(float(sw_in_w_m2) * 300.0 * 0.20 * 0.85, 60000.0)


def replay_plan_against_actual_solar(plan, actual_solar_w, critical_demand_w, eta_chg, eta_dis,
                                      capacity_wh, min_soc_pct, max_soc_pct, initial_e_wh,
                                      base_fuel_lph, marginal_fuel_lpwh):
    """Pure read-only replay. Does not call the optimizer. Returns per-hour realized arrays
    plus summary aggregates. diesel_power/battery_discharge taken verbatim from `plan`."""
    H = 24
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)

    realized_charge = []
    realized_curtailment = []
    realized_unmet = []
    realized_soc_pct = []
    soc_violations = []

    curr_e_wh = initial_e_wh
    for t in range(H):
        p_dis = plan.battery_discharge[t]
        p_diesel = plan.diesel_power[t]
        p_chg_planned = plan.battery_charge[t]
        critical_demand_t = critical_demand_w[t]  # the actual critical-demand input GAP19 was given for this hour

        wind_used_t = plan.wind_used[t]  # wind unchanged from planning (shared, not replayed)
        actual_renewable_t = actual_solar_w[t] + wind_used_t  # only solar is replaced; wind held identical

        available_total = actual_renewable_t + p_dis + p_diesel
        served = min(critical_demand_t, available_total)
        unmet = critical_demand_t - served
        remaining_after_critical = available_total - served

        p_chg_realized = min(p_chg_planned, max(0.0, remaining_after_critical))
        remaining_after_charge = remaining_after_critical - p_chg_realized
        curtail = max(0.0, remaining_after_charge)

        realized_charge.append(round(p_chg_realized, 4))
        realized_curtailment.append(round(curtail, 4))
        realized_unmet.append(round(unmet, 4))

        curr_e_wh = curr_e_wh + (p_chg_realized * eta_chg - (p_dis / eta_dis)) * 1.0
        soc_pct = (curr_e_wh / capacity_wh) * 100.0
        realized_soc_pct.append(round(soc_pct, 4))
        if soc_pct < (min_soc_pct - 1e-4) or soc_pct > (max_soc_pct + 1e-4):
            soc_violations.append({"hour": t, "soc_pct": round(soc_pct, 4)})

    # Diesel fuel: IDENTICAL to planned by construction (diesel_power never changed by replay).
    realized_diesel_fuel_l = sum(
        (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power
    )

    return {
        "realized_battery_charge_w": realized_charge,
        "realized_curtailment_w": realized_curtailment,
        "realized_unmet_load_w": realized_unmet,
        "realized_soc_pct": realized_soc_pct,
        "soc_violations": soc_violations,
        "realized_diesel_fuel_l": round(realized_diesel_fuel_l, 4),
        "realized_diesel_energy_wh": round(sum(plan.diesel_power), 1),
        "realized_battery_discharge_energy_wh": round(sum(plan.battery_discharge), 1),
        "realized_battery_charge_energy_wh": round(sum(realized_charge), 1),
        "realized_unmet_load_energy_wh": round(sum(realized_unmet), 1),
        "realized_curtailment_energy_wh": round(sum(realized_curtailment), 1),
    }


def main():
    print("=" * 80)
    print("ACTUAL-SOLAR REPLAY -- planned (R1/R2, unablated) dispatch vs. realized outcomes")
    print("Actual solar used ONLY to evaluate already-generated plans. GAP19 never re-run")
    print("with actual solar as input. NOT a production run. RESEARCH-ONLY.")
    print("=" * 80)

    rfe.verify_frozen_manifest()
    print("(No monkeypatch in this script -- original, unablated compute_terminal_target_wh "
          "formula used, exactly as R1/R2's own frozen harness.)\n")

    components = rfe.build_components()
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))

    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]
    print(f"Evaluation window (same as R1/R2): {len(origins)} origins\n")

    results = {}
    t_start = time.time()
    n_normal = 0
    n_emergency = 0
    for i, origin in enumerate(origins):
        origin_str = origin.strftime("%Y-%m-%dT%H:%M:%SZ")
        index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)

        st_k_raw = adapter.get_station_state(index, battery_soc_pct=50.0)
        st_k = StationState(
            timestamp=st_k_raw.timestamp, battery_soc_pct=80.0, battery_energy_wh=160000.0,
            diesel_running=True, diesel_hours_running=2.0,
            last_observed_solar_irradiance=st_k_raw.last_observed_solar_irradiance,
            last_observed_demand=st_k_raw.last_observed_demand,
            last_observed_wind_generation=st_k_raw.last_observed_wind_generation,
            diesel_fuel_remaining_liters=500.0,
        )
        initial_e_wh = 160000.0

        # Real, measured solar for this origin's 24h horizon, from the frozen matrix's own
        # ground-truth column (same column, same PV formula, already used in this branch's
        # DIRECT_BUS_BAR_PATHWAY_INVESTIGATION.md).
        origin_rows_all = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        actual_solar_w = [pv_from_sw_in(v) for v in origin_rows_all["actual_SW_IN"].values]

        origin_result = {}
        for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
            if engine_label == "stage8_1_corrected":
                feature_matrix = origin_rows_all[CANDIDATE_37_FEATURES].copy()
                bundle = engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})
            else:
                bundle = engine.predict(st_k, {})

            configs = dict(configs_base)
            critical_load_baseline_w = float(
                configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
            )
            critical_demand_w = [min(critical_load_baseline_w, d) for d in bundle.demand.point]
            configs["critical_demand_w"] = critical_demand_w
            configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)  # ORIGINAL formula, unmodified

            assessment, route = router.evaluate_and_route(st_k, bundle, configs)
            if route != "NORMAL":
                origin_result[engine_label] = {"route": route}
                continue
            plan = optimizer.optimize(bundle, st_k, configs)  # the ONE real GAP19 planning call; never re-called

            planned = {
                "constraint_status": plan.constraint_status,
                "planned_diesel_fuel_l": round(sum(
                    (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power
                ), 4),
                "planned_diesel_energy_wh": round(sum(plan.diesel_power), 1),
                "planned_unmet_load_wh": round(sum(plan.unmet_load), 1),
                "planned_curtailment_wh": round(sum(plan.renewable_curtailment), 1),
                "planned_battery_charge_wh": round(sum(plan.battery_charge), 1),
                "planned_battery_discharge_wh": round(sum(plan.battery_discharge), 1),
                "planned_soc_min_pct": round(min(plan.battery_soc), 2),
                "planned_soc_max_pct": round(max(plan.battery_soc), 2),
            }

            replay = replay_plan_against_actual_solar(
                plan, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
                min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,
            )

            origin_result[engine_label] = {"route": route, "planned": planned, "replay": replay}

        results[origin_str] = origin_result
        if origin_result.get("baseline", {}).get("route") == "NORMAL":
            n_normal += 1
        else:
            n_emergency += 1

        if (i + 1) % 50 == 0 or (i + 1) == len(origins):
            print(f"  ... {i+1}/{len(origins)} origins processed "
                  f"[{round(time.time()-t_start,1)}s elapsed]")

    out_path = THIS_DIR / "ACTUAL_SOLAR_REPLAY_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "ACTUAL-SOLAR REPLAY. RESEARCH-ONLY. Plans generated by the REAL, unmodified "
                "GAP19HighsNativeOptimizer using the ORIGINAL (unablated) R1/R2 "
                "terminal_target_wh formula. Replay against actual_SW_IN-derived real solar "
                "performed by NEW, separate analysis code in this script -- GAP19 itself was "
                "NEVER called with actual solar as an input. Diesel and battery-discharge "
                "commands are held exactly as planned in the replay; only renewable "
                "usage/curtailment, battery charge, realized SOC, and realized unmet load are "
                "recomputed. Not a production run. Not stakeholder-authorized."
            ),
            "num_origins": len(origins),
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {round(time.time() - t_start, 1)}s")
    print("ACTUAL-SOLAR REPLAY COMPLETE. No production code, config, or frozen artifact modified.")


if __name__ == "__main__":
    main()
