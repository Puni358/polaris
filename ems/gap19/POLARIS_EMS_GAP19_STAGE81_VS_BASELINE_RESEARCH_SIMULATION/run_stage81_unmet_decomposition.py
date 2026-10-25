#!/usr/bin/env python3
"""
STAGE 8.1 REALIZED-UNMET DECOMPOSITION. RESEARCH-ONLY. NOT a production run.

Investigates the ~1,739 kWh of realized critical-load unmet that remains for the Stage 8.1
arm in ACTUAL_SOLAR_REPLAY_RESULTS.json, by decomposing it into:
  (1) residual solar-forecast error (per-hour classification, no re-solve needed), and
  (2)+(3) GAP19 diesel/battery scheduling contribution, including the specific burst/banking
      behavior identified in DIRECT_BUS_BAR_PATHWAY_INVESTIGATION.md, via two SEPARATE,
      SMALL counterfactual re-plans per origin:

  COUNTERFACTUAL A ("perfect foresight"): GAP19 is given the ACTUAL realized solar AS ITS
  OWN forecast input (not as a replay evaluation -- a genuine new planning query: "what would
  GAP19 have planned, with its real, unmodified cost structure, if its forecast had been
  perfect?"). This isolates the PHYSICAL FEASIBILITY ceiling: if even perfect-foresight GAP19
  cannot avoid unmet load when replayed against the same actual solar it was given, the
  binding constraint is physical (diesel/battery power or energy bounds), not forecast
  accuracy. This is a new, additional GAP19 planning call (not a "re-optimization of the
  replay" -- the previous task's prohibition was against feeding actual solar into the
  REPLAY's evaluation of an EXISTING plan; this is a distinct, new counterfactual PLAN,
  explicitly requested by this task's item 4).

  COUNTERFACTUAL B ("no burst incentive"): GAP19 is given the SAME Stage 8.1 forecast as the
  original plan, but with `base_fuel_consumption_l_per_h` overridden to 0.0 IN THE IN-MEMORY
  CONFIG DICT PASSED TO THIS ONE CALL ONLY -- exactly the same technique already used and
  disclosed for `terminal_target_wh` in run_terminal_target_ablation.py. `system/config/diesel.yaml`
  is never read for this value in this call and is not modified on disk; `verify_frozen_manifest()`
  (reused, unmodified) is still run and still confirms the file's hash is unchanged. Removing
  the only fixed-per-on-hour cost term removes GAP19's incentive to concentrate diesel into
  few, large, battery-banking bursts (identified mechanism in the prior investigation) without
  changing the forecast, demand, critical-demand, terminal-reserve formula, or any other
  config value. This isolates the scheduling/burst-banking contribution specifically.

All three plans (original, A, B) are then replayed against the SAME actual solar using the
EXACT SAME replay function already defined and disclosed in run_actual_solar_replay.py
(imported, not duplicated) -- methodology held consistent with the prior report.

No production code, config, or frozen artifact is modified. GAP19 itself is never changed;
only the in-memory config dict passed to specific additional calls differs, exactly as
already established and disclosed in prior ablation experiments in this diagnostic branch.
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
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_actual_solar_replay import pv_from_sw_in, replay_plan_against_actual_solar

EPS = 1e-3


def main():
    print("=" * 80)
    print("STAGE 8.1 REALIZED-UNMET DECOMPOSITION -- forecast error vs. scheduling vs.")
    print("physical feasibility. NOT a production run. RESEARCH-ONLY.")
    print("=" * 80)

    rfe.verify_frozen_manifest()
    print("(Config diesel.yaml hash confirmed unchanged above. Counterfactual B below uses an "
          "in-memory override of base_fuel_consumption_l_per_h for specific extra calls only "
          "-- the file on disk is never touched, and this verification already proves that.)\n")

    components = rfe.build_components()
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))

    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]

    results = {}
    t_start = time.time()
    n_normal = 0
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

        origin_rows_all = df[df["forecast_start"] == origin].sort_values("horizon_hour").reset_index(drop=True)
        actual_solar_w = [pv_from_sw_in(v) for v in origin_rows_all["actual_SW_IN"].values]

        feature_matrix = origin_rows_all[CANDIDATE_37_FEATURES].copy()
        bundle_orig = stage81_engine.predict(st_k, {"stage8_1_feature_matrix": feature_matrix})

        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        critical_demand_w = [min(critical_load_baseline_w, d) for d in bundle_orig.demand.point]

        configs_orig = dict(configs_base)
        configs_orig["critical_demand_w"] = critical_demand_w
        configs_orig["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle_orig)

        assessment, route = router.evaluate_and_route(st_k, bundle_orig, configs_orig)
        if route != "NORMAL":
            results[origin_str] = {"route": route}
            continue
        n_normal += 1

        # --- Original Stage 8.1 plan (unmodified, as in R1/R2 and the prior replay report) ---
        plan_orig = optimizer.optimize(bundle_orig, st_k, configs_orig)
        replay_orig = replay_plan_against_actual_solar(
            plan_orig, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
            min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,
        )

        # --- Counterfactual A: perfect foresight (actual solar fed as GAP19's own forecast) ---
        bundle_perfect = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=bundle_orig.origin_timestamp,
            horizon_hours=24,
            timestamps=bundle_orig.timestamps,
            solar_irradiance=bundle_orig.solar_irradiance,  # unused by GAP19; kept as-is
            solar_generation=TimeseriesForecast(actual_solar_w, actual_solar_w, actual_solar_w, "W"),
            wind_generation=bundle_orig.wind_generation,  # unchanged -- isolates solar only
            demand=bundle_orig.demand,
            metadata={"source": "perfect_foresight_counterfactual"},
            demand_critical=bundle_orig.demand_critical,
        )
        configs_perfect = dict(configs_base)
        configs_perfect["critical_demand_w"] = critical_demand_w
        configs_perfect["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle_perfect)
        plan_perfect = optimizer.optimize(bundle_perfect, st_k, configs_perfect)
        replay_perfect = replay_plan_against_actual_solar(
            plan_perfect, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
            min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,
        )

        # --- Counterfactual B: Stage 8.1 forecast, base_fuel_consumption_l_per_h -> 0 (in-memory only) ---
        configs_nobase = dict(configs_base)
        configs_nobase["diesel"] = dict(configs_base.get("diesel", {}))
        configs_nobase["diesel"]["base_fuel_consumption_l_per_h"] = 0.0
        configs_nobase["critical_demand_w"] = critical_demand_w
        configs_nobase["terminal_target_wh"] = configs_orig["terminal_target_wh"]  # same as original
        plan_nobase = optimizer.optimize(bundle_orig, st_k, configs_nobase)
        replay_nobase = replay_plan_against_actual_solar(
            plan_nobase, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
            min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,  # realized fuel still priced at the REAL rate for comparability
        )

        # --- Per-hour forecast-error classification for the ORIGINAL plan's unmet hours ---
        forecast_solar_w = bundle_orig.solar_generation.point
        per_hour_class = []
        for t in range(24):
            if replay_orig["realized_unmet_load_w"][t] > EPS:
                overstated = forecast_solar_w[t] > actual_solar_w[t] + EPS
                per_hour_class.append({
                    "hour": t, "unmet_w": replay_orig["realized_unmet_load_w"][t],
                    "forecast_solar_w": round(forecast_solar_w[t], 1),
                    "actual_solar_w": round(actual_solar_w[t], 1),
                    "forecast_overstated_this_hour": overstated,
                })

        results[origin_str] = {
            "route": route,
            "diesel_on_hours_orig": sum(1 for p in plan_orig.diesel_power if p > EPS),
            "diesel_on_hours_perfect": sum(1 for p in plan_perfect.diesel_power if p > EPS),
            "diesel_on_hours_nobase": sum(1 for p in plan_nobase.diesel_power if p > EPS),
            "planned_diesel_energy_wh_orig": round(sum(plan_orig.diesel_power), 1),
            "planned_diesel_energy_wh_perfect": round(sum(plan_perfect.diesel_power), 1),
            "planned_diesel_energy_wh_nobase": round(sum(plan_nobase.diesel_power), 1),
            "realized_unmet_wh_orig": replay_orig["realized_unmet_load_energy_wh"],
            "realized_unmet_wh_perfect": replay_perfect["realized_unmet_load_energy_wh"],
            "realized_unmet_wh_nobase": replay_nobase["realized_unmet_load_energy_wh"],
            "soc_violations_orig": len(replay_orig["soc_violations"]),
            "soc_violations_perfect": len(replay_perfect["soc_violations"]),
            "soc_violations_nobase": len(replay_nobase["soc_violations"]),
            "constraint_status_perfect": plan_perfect.constraint_status,
            "constraint_status_nobase": plan_nobase.constraint_status,
            "per_hour_unmet_classification_orig": per_hour_class,
        }

        if (i + 1) % 50 == 0 or (i + 1) == len(origins):
            print(f"  ... {i+1}/{len(origins)} origins processed ({n_normal} NORMAL) "
                  f"[{round(time.time()-t_start,1)}s elapsed]")

    out_path = THIS_DIR / "STAGE81_UNMET_DECOMPOSITION_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": (
                "STAGE 8.1 REALIZED-UNMET DECOMPOSITION. RESEARCH-ONLY. Three plans per "
                "NORMAL origin: (orig) the real Stage 8.1 R1/R2 plan; (perfect) a NEW "
                "counterfactual plan given actual solar as GAP19's own forecast input "
                "(isolates physical feasibility); (nobase) a NEW counterfactual plan using "
                "the Stage 8.1 forecast with base_fuel_consumption_l_per_h overridden to 0.0 "
                "in-memory only (isolates burst/banking scheduling contribution). All three "
                "replayed against the same actual solar with the same replay methodology as "
                "ACTUAL_SOLAR_REPLAY_RESULTS.json. No production code, config, or frozen "
                "artifact modified."
            ),
            "num_origins": len(origins), "num_normal": n_normal,
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {round(time.time() - t_start, 1)}s")
    print("DECOMPOSITION COMPLETE. No production code, config, or frozen artifact modified.")


if __name__ == "__main__":
    main()
