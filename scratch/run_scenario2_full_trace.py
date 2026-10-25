#!/usr/bin/env python3
"""
Scenario 2 FULL DECISION TRACE pass.

Same physics, same inputs and same solver call as run_continuous_ui_rhc_scenario2.py
(Scenario 2: EBR on, 10 kWh reserve deadband, terminal_reserve_model=INITIAL_STATE),
but every decision input and every decision output of the solver is persisted so
the dashboard can show the real reasoning instead of a reconstruction, and so
individual decisions can be questioned and changed later.

Per origin hour it records (kW / kWh unless a field name says otherwise):
  state      : SOC / energy before the decision, generator running before
  inputs     : 24-step irradiance, solar generation, wind, demand, critical load
  reserve    : raw EBR target, deadband, terminal target, and the exact energy the
               solver was required to hold at each of the 24 steps
  plan       : the solver's full 24-step plan (diesel, battery charge/discharge,
               SOC, solar/wind used, curtailment, load served, unmet, unmet
               non-critical, reserve shortfall, flexible load)
  objectives : J1, J1b, J2, J3, J4, solver status
  executed   : what the physics sim actually did with step 0 (solar, wind, net,
               SOC after, fuel, battery clamp = hidden unserved/curtailed energy)

Output layout (served by the dashboard as static files):
  dashboard/public/data/trace/<variant>/manifest.json
  dashboard/public/data/trace/<variant>/day_YYYY-MM-DD.json   (24 hour records each)

--terminal-mode lets the end-of-horizon rule be changed for A/B experiments:
  as_is               (default) identical to the audited Scenario 2 run
  initial_state_exact terminal_target_wh = initial energy - hard floor, i.e. end the
                      24 h plan with exactly the energy it started with
  none                terminal_target_wh = 0 (no end-of-horizon energy requirement)
Each mode writes to its own <variant> folder; the default folder is "scenario2".
"""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
os.chdir(REPO_ROOT)

sys.path.insert(0, os.path.join(REPO_ROOT, "scratch"))
from sim_inputs import demand_at, wind_at  # noqa: E402
from scratch.run_continuous_ui_rhc_scenario2 import build_timeseries  # noqa: E402
from system.forecasting.implementations.n6_solar import N6SolarForecastEngine  # noqa: E402
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer  # noqa: E402
from system.evaluation.n6_multi_origin_harness.adapters import _align_n6_bundle_od02  # noqa: E402
from system.schemas.station_state import StationState  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scenario2_trace")

BATT_CAPACITY_WH = 200_000.0
BATT_MIN_WH = BATT_CAPACITY_WH * 0.20
BATT_MAX_WH = BATT_CAPACITY_WH * 0.95
CHARGE_EFF = 0.92
DISCHARGE_EFF = 0.92
K_PV_W_PER_WM2 = 300.0 * 0.20 * 0.85
FUEL_COST_PER_L = 2.50


def kw(arr, nd=3):
    return [round(float(v) / 1000.0, nd) for v in arr]


def plain(arr, nd=3):
    return [round(float(v), nd) for v in arr]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terminal-mode", default="as_is", choices=["as_is", "initial_state_exact", "none"])
    ap.add_argument("--variant", default=None, help="output folder name (default: scenario2, or scenario2_<mode>)")
    ap.add_argument("--deadband-kwh", type=float, default=10.0, help="reserve deadband (Scenario 2 = 10, Scenario 3/4 = 0)")
    ap.add_argument("--ebr-mode", default="n6_conformal", choices=["n6_conformal", "off"], help="off = Scenario 4 (no reserve buffer)")
    ap.add_argument("--forecaster", default="n6", choices=["n6", "baseline", "successor_v2", "k", "n1"], help="solar forecaster whose point forecast the optimizer receives (reserve policy stays N6's)")
    ap.add_argument("--limit", type=int, default=None, help="only run the first N origins (smoke test)")
    ap.add_argument("--out-root", default="dashboard/public/data/trace")
    args = ap.parse_args()

    DEADBAND_WH = args.deadband_kwh * 1000.0
    variant = args.variant or ("scenario2" if args.terminal_mode == "as_is" else f"scenario2_{args.terminal_mode}")
    out_dir = os.path.join(args.out_root, variant)
    os.makedirs(out_dir, exist_ok=True)
    ckpt_file = os.path.join("scratch", f"scenario2_trace_{variant}_checkpoint.json")

    df_mat = pd.read_parquet("scratch/hourly_rolling_candidate_matrix.parquet")
    df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
    truth_df = pd.read_csv("data/POLARIS_v0_1_clearsky_decomposition.csv")
    truth_df["TIMESTAMP"] = pd.to_datetime(truth_df["TIMESTAMP"], utc=True)
    truth_df = truth_df.set_index("TIMESTAMP")
    origins = sorted(df_mat["forecast_start"].drop_duplicates().tolist())
    if args.limit:
        origins = origins[: args.limit]

    n6_engine = N6SolarForecastEngine()

    # ---- alternative point forecasters (same inputs, same matrix, same reserve policy) ----
    cand_models, cand_feats = None, None
    if args.forecaster != "n6":
        import copy
        import joblib
        base = "forecasting/stage7/stage8/stage8_1_station_tuning_research/"
        paths = {
            "successor_v2": base + "candidate_f_successor_18z/artifacts_v2/candidate_f_successor_v2_model.joblib",
            "k": base + "candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib",
            "n1": base + "candidate_n_additive_physics/artifacts/candidate_n1_model.joblib",
        }
        if args.forecaster != "baseline":
            cand_models = joblib.load(paths[args.forecaster])
            cand_feats = list(cand_models.feature_names_in_) if hasattr(cand_models, "feature_names_in_") else None
            if cand_feats is None:
                from system.forecasting.implementations.n6_solar import FEATURE_NAMES
                cand_feats = {"successor_v2": FEATURE_NAMES[:33], "k": FEATURE_NAMES[:35], "n1": FEATURE_NAMES}[args.forecaster]
        log.info(f"forecaster={args.forecaster} features={len(cand_feats) if cand_feats else 'n/a (physical baseline)'}")

    def candidate_point_forecast(fdf):
        # Same construction as the N6 additive branch: baseline + learned residual, floored at 0,
        # zero when the sun is below the horizon.
        st4 = fdf["pred_stage4_clean"].to_numpy(dtype=float)
        y = st4.copy() if cand_models is None else st4 + cand_models.predict(fdf[cand_feats])
        y = np.clip(y, 0.0, None)
        mask = (fdf["solar_elevation"].to_numpy(dtype=float) > 0.0) & (fdf["clearsky_ghi"].to_numpy(dtype=float) > 0.0)
        return np.where(mask, y, 0.0)
    optimizer = GAP19HighsNativeOptimizer()

    config = {
        "operating_mode": "NORMAL",
        "battery": {"capacity_wh": BATT_CAPACITY_WH, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
        "diesel": {"min_power_w": 10_000.0, "max_power_w": 100_000.0},
        "terminal_reserve_model": "INITIAL_STATE",
        "optimizer": {"timestep_hours": 1.0},
    }
    if DEADBAND_WH > 0:
        config["reserve_deadband_wh"] = DEADBAND_WH

    start_idx = 0
    current_battery_wh = BATT_CAPACITY_WH * 0.50
    prev_diesel_w = 0.0
    total_l = 0.0
    run_hours = 0
    starts = 0
    days_done = []
    if os.path.exists(ckpt_file) and not args.limit:
        ck = json.load(open(ckpt_file))
        start_idx = ck["last_idx"] + 1
        current_battery_wh = ck["current_battery_wh"]
        prev_diesel_w = ck["prev_diesel_w"]
        total_l = ck["total_l"]
        run_hours = ck["run_hours"]
        starts = ck["starts"]
        days_done = ck["days_done"]
        log.info(f"[RESUME] from step {start_idx}/{len(origins)}")

    buffer, buffer_day = [], None
    series_path = os.path.join(out_dir, "series.json")
    series_rows = []
    if start_idx > 0 and os.path.exists(series_path):
        series_rows = json.load(open(series_path))
    t0 = time.time()

    def flush(day, last_idx):
        nonlocal days_done
        with open(os.path.join(out_dir, f"day_{day}.json"), "w") as f:
            json.dump(buffer, f, separators=(",", ":"))
        if day not in days_done:
            days_done.append(day)
        # Slim per-hour series in the dashboard's existing row schema (graph + log use this).
        with open(series_path, "w") as f:
            json.dump(series_rows, f, separators=(",", ":"))
        with open(os.path.join(out_dir, "manifest.json"), "w") as f:
            json.dump({
                "variant": variant, "terminal_mode": args.terminal_mode, "deadband_wh": DEADBAND_WH, "ebr_mode": args.ebr_mode,
                "hours_total": len(origins), "hours_done": last_idx + 1, "days": days_done,
                "schema": 1,
            }, f)
        if not args.limit:
            json.dump({
                "last_idx": last_idx, "current_battery_wh": current_battery_wh, "prev_diesel_w": prev_diesel_w,
                "total_l": total_l, "run_hours": run_hours, "starts": starts, "days_done": days_done,
            }, open(ckpt_file, "w"))

    for i in range(start_idx, len(origins)):
        orig_dt = origins[i]
        day = orig_dt.strftime("%Y-%m-%d")
        if buffer_day is None:
            buffer_day = day

        origin_rows = df_mat[df_mat["forecast_start"] == orig_dt].sort_values("horizon_hour").reset_index(drop=True)
        features_df = origin_rows.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")
        features_df["elevation_x_transition_cloud"] = 0.0
        features_df = features_df.ffill().bfill().fillna(0.0)

        soc_before = (current_battery_wh / BATT_CAPACITY_WH) * 100.0
        energy_before_wh = current_battery_wh
        diesel_running_before = prev_diesel_w > 0

        station_state = StationState(
            timestamp=orig_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            battery_soc_pct=soc_before,
            battery_energy_wh=current_battery_wh,
            diesel_running=diesel_running_before,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30_000.0,
            last_observed_wind_generation=15_000.0,
            operating_mode="NORMAL",
        )

        raw_bundle = n6_engine.predict(station_state, {"n6_feature_matrix": features_df})
        if args.forecaster != "n6":
            ycand = candidate_point_forecast(features_df)
            for attr, vals in (("solar_irradiance", ycand), ("solar_generation", np.minimum(ycand * K_PV_W_PER_WM2, 60000.0))):
                ts_obj = copy.copy(getattr(raw_bundle, attr))
                ts_obj.point = [float(v) for v in vals]
                ts_obj.lower = list(ts_obj.point)
                ts_obj.upper = list(ts_obj.point)
                setattr(raw_bundle, attr, ts_obj)
        bundle = _align_n6_bundle_od02(raw_bundle)

        demand_w = [demand_at(orig_dt + pd.Timedelta(hours=h)) for h in range(24)]
        wind_w = [wind_at(orig_dt + pd.Timedelta(hours=h)) for h in range(24)]
        bundle.demand = build_timeseries(demand_w, "W")
        bundle.wind_generation = build_timeseries(wind_w, "W")
        bundle.demand_critical = build_timeseries([15_000.0] * 24, "W")

        if args.ebr_mode == "off":
            config["ebr_target_wh"] = 0.0  # explicit zero, not omission (Scenario 4)
        else:
            ebr_raw = bundle.metadata.get("ebr_target_wh") if "ebr_target_wh" in bundle.metadata else None
            if ebr_raw is not None:
                config["ebr_target_wh"] = ebr_raw

        initial_e_wh = max(BATT_MIN_WH, min(BATT_MAX_WH, current_battery_wh))
        if args.terminal_mode == "initial_state_exact":
            config["terminal_target_wh"] = initial_e_wh - BATT_MIN_WH
            terminal_target_wh = config["terminal_target_wh"]
        elif args.terminal_mode == "none":
            config["terminal_target_wh"] = 0.0
            terminal_target_wh = 0.0
        else:
            config.pop("terminal_target_wh", None)
            terminal_target_wh = initial_e_wh  # what INITIAL_STATE hands the solver

        plan = optimizer.optimize(forecast_bundle=bundle, station_state=station_state, config=config)

        # Reserve envelope the solver was actually held to (mirrors gap19_highs_native steps 4-6b)
        ebr_cfg = config.get("ebr_target_wh", 0.0)
        ebr_list = [float(v) for v in ebr_cfg] if isinstance(ebr_cfg, (list, tuple)) else [float(ebr_cfg)] * 24
        stage2 = list(ebr_list)
        stage2[23] = max(ebr_list[23], terminal_target_wh)
        stage2 = [max(0.0, v - DEADBAND_WH) for v in stage2]
        required_energy_wh = [v + BATT_MIN_WH for v in stage2]  # E_next[t] + shortfall >= this

        def g(name, default=None):
            return getattr(plan, name, default)

        diesel_plan_w = list(g("diesel_power", [0.0] * 24))
        planned_diesel_w = diesel_plan_w[0]
        actual_diesel_w = planned_diesel_w

        fuel_l = 0.0
        started = False
        if actual_diesel_w > 0:
            run_hours += 1
            if prev_diesel_w <= 0.0:
                starts += 1
                started = True
            fuel_l = 5.0 + actual_diesel_w * 0.00025
            total_l += fuel_l
        prev_diesel_w = actual_diesel_w

        actual_ghi = float(truth_df.loc[orig_dt, "actual_SW_IN"]) if orig_dt in truth_df.index else 0.0
        actual_solar_w = max(0.0, actual_ghi * K_PV_W_PER_WM2)
        net_surplus_w = actual_solar_w + wind_w[0] + actual_diesel_w - demand_w[0]

        unserved_wh = 0.0
        curtailed_wh = 0.0
        if net_surplus_w >= 0:
            want = current_battery_wh + net_surplus_w * CHARGE_EFF
            new_wh = min(BATT_MAX_WH, want)
            curtailed_wh = max(0.0, (want - new_wh) / CHARGE_EFF)
        else:
            want = current_battery_wh - (-net_surplus_w) / DISCHARGE_EFF
            new_wh = max(BATT_MIN_WH, want)
            unserved_wh = max(0.0, (new_wh - want) * DISCHARGE_EFF)
        current_battery_wh = max(BATT_MIN_WH, min(BATT_MAX_WH, new_wh))
        soc_after = (current_battery_wh / BATT_CAPACITY_WH) * 100.0

        planned_diesel_kw = round(planned_diesel_w / 1000.0, 2)
        binding = []
        bsoc = g("battery_soc")
        if (bsoc and bsoc[0] <= 20.05) or soc_after <= 20.05:
            binding.append("battery_floor_20")
        if (bsoc and bsoc[0] >= 94.95) or soc_after >= 94.95:
            binding.append("battery_ceiling_95")
        unm_nc = g("unmet_noncritical_load")
        unm = g("unmet_load")
        if (unm_nc and unm_nc[0] > 0.01) or (unm and unm[0] > 0.01):
            binding.append("J1b_shed_active")
        if 0.0 < planned_diesel_kw <= 10.05:
            binding.append("diesel_min_10kw")
        if planned_diesel_kw >= 99.95:
            binding.append("diesel_max_100kw")
        rs = g("reserve_shortfall")
        if rs and rs[0] > 0.01:
            binding.append("reserve_shortfall_active")

        dsl = [v / 1000.0 for v in diesel_plan_w]
        first_diesel = next((k for k, v in enumerate(dsl) if v > 0), None)
        block_starts = sum(1 for k, v in enumerate(dsl) if v > 0 and (k == 0 and not diesel_running_before or k > 0 and dsl[k - 1] <= 0))

        rec = {
            "timestamp": orig_dt.isoformat(),
            "state": {
                "soc_before_pct": round(soc_before, 3), "energy_before_kwh": round(energy_before_wh / 1000.0, 3),
                "diesel_running_before": diesel_running_before,
            },
            "inputs": {
                "irradiance_wm2": plain(bundle.solar_irradiance.point, 2),
                "solar_kw": kw(bundle.solar_generation.point),
                "wind_kw": kw(wind_w),
                "demand_kw": kw(demand_w),
                "critical_kw": kw([15_000.0] * 24),
            },
            "reserve": {
                "ebr_target_kwh": round(ebr_list[0] / 1000.0, 3),
                "deadband_kwh": DEADBAND_WH / 1000.0,
                "terminal_target_kwh": round(terminal_target_wh / 1000.0, 3),
                "terminal_mode": args.terminal_mode,
                "required_energy_kwh": kw(required_energy_wh),
                "floor_kwh": BATT_MIN_WH / 1000.0,
            },
            "plan": {
                "diesel_kw": kw(diesel_plan_w),
                "charge_kw": kw(g("battery_charge", [0.0] * 24)),
                "discharge_kw": kw(g("battery_discharge", [0.0] * 24)),
                "soc_pct": plain(g("battery_soc", [0.0] * 24), 2),
                "solar_used_kw": kw(g("solar_used", [0.0] * 24)),
                "wind_used_kw": kw(g("wind_used", [0.0] * 24)),
                "curtail_kw": kw(g("renewable_curtailment", [0.0] * 24)),
                "served_kw": kw(g("load_served", [0.0] * 24)),
                "unmet_kw": kw(g("unmet_load", [0.0] * 24)),
                "unmet_noncrit_kw": kw(g("unmet_noncritical_load", [0.0] * 24)),
                "reserve_shortfall_kwh": kw(g("reserve_shortfall", [0.0] * 24)),
                "flex_kw": kw(g("flexible_load_schedule", [0.0] * 24)),
                "first_diesel_step": first_diesel,
                "diesel_block_starts": block_starts,
                "diesel_hours_planned": sum(1 for v in dsl if v > 0),
            },
            "objectives": {
                "j1_wh": g("j1_objective"), "j1b_wh": g("j1b_objective"), "j2_wh": g("j2_objective"),
                "j3_litres": g("j3_objective"), "j4_wh": g("j4_objective"),
                "status": g("constraint_status"),
                "max_energy_balance_err": max(g("energy_balance_errors", [0.0]) or [0.0]),
            },
            "executed": {
                "actual_ghi": round(actual_ghi, 2), "actual_solar_kw": round(actual_solar_w / 1000.0, 3),
                "wind_kw": round(wind_w[0] / 1000.0, 3), "demand_kw": round(demand_w[0] / 1000.0, 3),
                "diesel_kw": round(actual_diesel_w / 1000.0, 3), "planned_diesel_kw": planned_diesel_kw,
                "net_surplus_kw": round(net_surplus_w / 1000.0, 3), "soc_after_pct": round(soc_after, 3),
                "fuel_l": round(fuel_l, 3), "fuel_cost": round(fuel_l * FUEL_COST_PER_L, 3),
                "generator_started": started,
                "physics_unserved_kwh": round(unserved_wh / 1000.0, 3),
                "physics_curtailed_kwh": round(curtailed_wh / 1000.0, 3),
            },
            "binding_constraints": binding,
        }
        buffer.append(rec)
        series_rows.append({
            "timestamp": rec["timestamp"], "actual_ghi": rec["executed"]["actual_ghi"],
            "n6_forecast_ghi": rec["inputs"]["irradiance_wm2"][0], "battery_soc_pct": round(soc_after, 2),
            "diesel_kw": round(actual_diesel_w / 1000.0, 2), "battery_net_kw": round(net_surplus_w / 1000.0, 2),
            "diesel_fuel_cost": round(fuel_l * FUEL_COST_PER_L, 3), "demand_w": round(demand_w[0], 2),
            "forecast_horizon": rec["inputs"]["irradiance_wm2"], "ebr_target_wh": round(ebr_list[0], 2),
            "planned_diesel_kw": planned_diesel_kw, "binding_constraints": binding,
        })

        last_of_day = (i + 1 >= len(origins)) or (origins[i + 1].strftime("%Y-%m-%d") != day)
        if last_of_day:
            flush(day, i)
            buffer, buffer_day = [], None
            el = time.time() - t0
            done = i + 1 - start_idx
            log.info(f"[{variant}] day {day} written | step {i + 1}/{len(origins)} | SOC {soc_after:5.1f}% | "
                     f"fuel {total_l:,.0f} L | ETA {(len(origins) - i - 1) * el / max(1, done) / 60:5.1f} min")

    log.info(f"DONE [{variant}] total fuel {total_l:,.2f} L | run hours {run_hours} | starts {starts}")
    if os.path.exists(ckpt_file) and not args.limit:
        os.remove(ckpt_file)


if __name__ == "__main__":
    main()
