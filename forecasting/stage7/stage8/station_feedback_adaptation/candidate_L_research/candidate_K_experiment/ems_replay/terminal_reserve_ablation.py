#!/usr/bin/env python3
"""
TERMINAL RESERVE ON/OFF ABLATION. RESEARCH-ONLY. NOT a production run. NOT a promotion.

Question: does the terminal-reserve target/constraint itself (the mechanism identified in
K_EMS_DEGRADATION_FORENSICS.md) cause K's EMS degradation, or does it persist even with that
one mechanism neutralized?

2x2: {F, K forecast} x {terminal reserve ON, OFF}, over the same 347 2024 origins / 245
NORMAL-routed-by-both-arms subset already used throughout this research line.

ON: configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle) -- the existing,
unmodified, frozen formula, exactly as in ems_replay.py. Identical to the already-reported
F/K EMS replay.

OFF: configs["terminal_target_wh"] = 0.0 -- removes ONLY the extra terminal-reserve override
at hour 23 (system/optimization/implementations/gap19_highs_native.py line 151:
`e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)`). Setting
terminal_target_wh=0.0 makes this max() a no-op (EBR's own governed 6h-lookahead
survivability requirement, which is never negative, always dominates), so the ONLY thing
removed is the terminal-reserve override itself. The EBR requirement (every hour, including
hour 23's own baseline EBR value), the normal battery SOC floor/ceiling bounds (`min_e_wh`/
`max_e_wh`, enforced as hard variable bounds elsewhere, independent of terminal_target_wh),
charge/discharge limits, diesel constraints, load constraints, optimizer settings, and
replay mechanics are completely unchanged -- confirmed by direct inspection of
gap19_highs_native.py (see TERMINAL_RESERVE_ABLATION_REPORT.md for the exact lines).

No production, Stage 8.1, F, or K code/artifact is modified. Candidate K is not retrained,
regenerated, or promoted. GAP19 (frozen, unmodified) is called once per origin per
(forecast, reserve_mode) cell for planning only, never re-run with actual solar.
"""
import sys
import json
import time
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
GAP19_DIR = BASE / "ems/gap19/POLARIS_EMS_GAP19_STAGE81_VS_BASELINE_RESEARCH_SIMULATION"
sys.path.insert(0, str(GAP19_DIR))
K_DIR = BASE / "forecasting/candidate_L_research" / "candidate_K_experiment"
sys.path.insert(0, str(K_DIR))
THIS_DIR = Path(__file__).parent

import run_full_experiment as rfe
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_actual_solar_replay import pv_from_sw_in, replay_plan_against_actual_solar
from run_candidateF_actual_solar_replay import predict_solar_bundle, sw_in_to_power_w, ADDITIVE_FEATURE_NAME
import candidate_K_experiment as ck

CANDIDATE_F_MODEL_PATH = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib"
EXPECTED_CANDIDATE_F_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"
MATRIX_2024_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
HISTORICAL_RESIDUAL_DATASET_PATH = BASE / "forecasting/candidate_L_research" / "CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv"
EXPECTED_HISTORICAL_RESIDUAL_HASH = "1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab"

K_VARIANT, K_ALPHA, K_MIN_HISTORY, K_MAX_CLIP, K_SCALE_MODE = "A_global", 0.1, 1, 75.0, "unscaled"
N_BOOTSTRAP, BOOTSTRAP_SEED = 2000, 42


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_all_hashes():
    checks = [
        ("candidate_F_model", sha256_of(CANDIDATE_F_MODEL_PATH), EXPECTED_CANDIDATE_F_HASH),
        ("matrix_2024", sha256_of(MATRIX_2024_PATH), EXPECTED_MATRIX_2024_HASH),
        ("historical_residual_dataset_2020_2023", sha256_of(HISTORICAL_RESIDUAL_DATASET_PATH), EXPECTED_HISTORICAL_RESIDUAL_HASH),
    ]
    all_ok = True
    for name, actual, expected in checks:
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"  {name}: {'MATCH' if ok else 'MISMATCH'}")
    if not all_ok:
        raise RuntimeError("STOP: hash verification FAILED.")
    return {name: actual for name, actual, _ in checks}


def load_historical_origin_map():
    import csv
    with open(HISTORICAL_RESIDUAL_DATASET_PATH, mode="r") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["solar_elevation"] = float(r["solar_elevation"]); r["cloud_frac"] = float(r["cloud_frac"])
        r["prediction"] = float(r["prediction"]); r["actual"] = float(r["actual"])
        r["residual"] = float(r["residual"]); r["horizon_hour"] = int(r["horizon_hour"])
    origin_map, origin_order = {}, []
    for r in rows:
        o = r["forecast_start"]
        if o not in origin_map:
            origin_map[o] = []; origin_order.append(o)
        origin_map[o].append(r)
    return origin_order, origin_map


def build_2024_rows(model_f, candidate_f_features, df_2024):
    origin_order_2024, origin_map_2024, origin_f_pred_power_w = [], {}, {}
    for origin, g in df_2024.groupby("forecast_start", sort=True):
        g = g.sort_values("horizon_hour").reset_index(drop=True)
        solar_gen_f_w = predict_solar_bundle(model_f, candidate_f_features, g,
                                              extra_feature_fn=lambda d: d["solar_elevation"] * d["cloud_frac"])
        solar_elevation = g["solar_elevation"].values
        clearsky_ghi = g["clearsky_ghi"].values
        is_night = (solar_elevation <= 0.0) | (clearsky_ghi == 0.0)
        gf = g.copy()
        gf[ADDITIVE_FEATURE_NAME] = gf["solar_elevation"] * gf["cloud_frac"]
        X = gf[candidate_f_features].values.astype(np.float64)
        residual_model = model_f.predict(X)
        pred_stage4 = g["pred_stage4_fold"].values
        pred_sw_in = np.maximum(0.0, pred_stage4 + residual_model)
        pred_sw_in = np.where(is_night, 0.0, pred_sw_in)
        origin_str = str(origin)
        rows = []
        for i in range(len(g)):
            actual_v = float(g["actual_SW_IN"].values[i]); pred_v = float(pred_sw_in[i])
            rows.append({"forecast_start": origin_str, "horizon_hour": int(g["horizon_hour"].values[i]),
                         "solar_elevation": float(solar_elevation[i]), "cloud_frac": float(g["cloud_frac"].values[i]),
                         "prediction": pred_v, "actual": actual_v, "residual": actual_v - pred_v})
        origin_order_2024.append(origin_str)
        origin_map_2024[origin_str] = rows
        origin_f_pred_power_w[origin_str] = [round(v, 2) for v in [sw_in_to_power_w(x) for x in pred_sw_in]]
    return origin_order_2024, origin_map_2024, origin_f_pred_power_w


def arrsum(a):
    return round(float(sum(a)), 4)


def paired_bootstrap_ci(deltas, n_iterations=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    rng = np.random.default_rng(seed)
    deltas = np.asarray(deltas, dtype=np.float64)
    n = len(deltas)
    if n == 0:
        return {"mean": None, "ci_95_lower": None, "ci_95_upper": None, "n": 0}
    boot_means = np.empty(n_iterations)
    for b in range(n_iterations):
        idx = rng.integers(0, n, size=n)
        boot_means[b] = deltas[idx].mean()
    boot_means.sort()
    lo = boot_means[int(0.025 * n_iterations)]
    hi = boot_means[int(0.975 * n_iterations) - 1]
    return {"mean": round(float(deltas.mean()), 4), "ci_95_lower": round(float(lo), 4),
            "ci_95_upper": round(float(hi), 4), "n": int(n)}


def main():
    print("=" * 80)
    print("TERMINAL RESERVE ON/OFF ABLATION -- 2x2: {F,K} x {reserve ON, OFF}. RESEARCH-ONLY.")
    print("=" * 80)

    hashes = verify_all_hashes()
    rfe.verify_frozen_manifest()

    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)
    candidate_f_features = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]

    origin_order_hist, origin_map_hist = load_historical_origin_map()
    df_2024 = pd.read_csv(MATRIX_2024_PATH)
    df_2024["forecast_start"] = pd.to_datetime(df_2024["forecast_start"], utc=True)
    origin_order_2024, origin_map_2024, origin_f_pred_power_w = build_2024_rows(model_f, candidate_f_features, df_2024)

    combined_order = origin_order_hist + origin_order_2024
    combined_map = dict(origin_map_hist); combined_map.update(origin_map_2024)
    history_records = ck.run_simulation(combined_order, combined_map, K_VARIANT, K_ALPHA, K_MIN_HISTORY, K_MAX_CLIP, K_SCALE_MODE)
    k_pred_lookup = {(r["forecast_start"], r["horizon_hour"]): r["k_prediction"]
                     for r in history_records if r["forecast_start"] in origin_map_2024}

    components = rfe.build_components()
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components
    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))

    results = {}
    origin_rows_out = []
    t_start = time.time()

    for i, origin_str in enumerate(origin_order_2024):
        origin_ts = pd.Timestamp(origin_str)
        origin_rows_all = df_2024[df_2024["forecast_start"] == origin_ts].sort_values("horizon_hour").reset_index(drop=True)
        index = int((origin_ts - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)

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
        actual_solar_w = [pv_from_sw_in(v) for v in origin_rows_all["actual_SW_IN"].values]

        shared_bundle = baseline_engine.predict(st_k, {})
        wind_gen = shared_bundle.wind_generation
        demand_fc = shared_bundle.demand
        critical_load_baseline_w = float(configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0))
        critical_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]
        timestamps = [(origin_ts + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

        solar_gen_f = origin_f_pred_power_w[origin_str]
        bundle_f = ForecastBundle(schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
                                   timestamps=timestamps,
                                   solar_irradiance=TimeseriesForecast([0.0]*24,[0.0]*24,[0.0]*24,"W/m^2"),
                                   solar_generation=TimeseriesForecast(solar_gen_f, solar_gen_f, solar_gen_f, "W"),
                                   wind_generation=wind_gen, demand=demand_fc, metadata={"source": "candidate_F"},
                                   demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"))

        horizons_sorted = sorted(int(h) for h in origin_rows_all["horizon_hour"].values)
        k_sw_in_by_h = {h: k_pred_lookup.get((origin_str, h)) for h in horizons_sorted}
        solar_gen_k = [round(sw_in_to_power_w(k_sw_in_by_h[h]), 2) if k_sw_in_by_h[h] is not None else 0.0
                       for h in horizons_sorted]
        bundle_k = ForecastBundle(schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
                                   timestamps=timestamps,
                                   solar_irradiance=TimeseriesForecast([0.0]*24,[0.0]*24,[0.0]*24,"W/m^2"),
                                   solar_generation=TimeseriesForecast(solar_gen_k, solar_gen_k, solar_gen_k, "W"),
                                   wind_generation=wind_gen, demand=demand_fc, metadata={"source": "candidate_K"},
                                   demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"))

        origin_result = {}
        origin_metrics = {"forecast_start": origin_str}
        for forecast_label, bundle in [("F", bundle_f), ("K", bundle_k)]:
            for reserve_mode in ["ON", "OFF"]:
                cell_label = f"{forecast_label}_{reserve_mode}"
                configs = dict(configs_base)
                configs["critical_demand_w"] = critical_demand_w
                if reserve_mode == "ON":
                    configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)  # unmodified, frozen
                else:
                    configs["terminal_target_wh"] = 0.0  # removes ONLY the terminal-reserve override at hour 23

                assessment, route = router.evaluate_and_route(st_k, bundle, configs)
                if route != "NORMAL":
                    origin_result[cell_label] = {"route": route}
                    origin_metrics[f"{cell_label}_route"] = route
                    continue

                t0 = time.perf_counter()
                plan = optimizer.optimize(bundle, st_k, configs)
                solve_time_s = time.perf_counter() - t0
                optimizer_failed = plan.constraint_status != "OPTIMAL"

                planned = {
                    "constraint_status": plan.constraint_status,
                    "planned_diesel_fuel_l": round(sum(
                        (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power), 4),
                    "planned_soc_min_pct": round(min(plan.battery_soc), 2),
                    "planned_soc_max_pct": round(max(plan.battery_soc), 2),
                    "solve_time_s": round(solve_time_s, 4),
                }
                replay = replay_plan_against_actual_solar(
                    plan, actual_solar_w, critical_demand_w, eta_chg, eta_dis, capacity_wh,
                    min_soc_pct, max_soc_pct, initial_e_wh, base_fuel_lph, marginal_fuel_lpwh,
                )
                diesel_on_hours = sum(1 for p in plan.diesel_power if p > 0.0)
                startups = 0
                prev_on = st_k.diesel_running
                for p in plan.diesel_power:
                    on = p > 0.0
                    if on and not prev_on:
                        startups += 1
                    prev_on = on
                efc = (sum(replay["realized_battery_charge_w"]) + sum(plan.battery_discharge)) / (2.0 * capacity_wh)

                origin_result[cell_label] = {"route": route, "planned": planned, "replay": replay,
                                              "terminal_target_wh_used": configs["terminal_target_wh"]}
                origin_metrics[f"{cell_label}_route"] = route
                origin_metrics[f"{cell_label}_optimizer_failed"] = optimizer_failed
                origin_metrics[f"{cell_label}_terminal_target_wh"] = round(configs["terminal_target_wh"], 2)
                origin_metrics[f"{cell_label}_solve_time_s"] = planned["solve_time_s"]
                origin_metrics[f"{cell_label}_realized_diesel_fuel_l"] = replay["realized_diesel_fuel_l"]
                origin_metrics[f"{cell_label}_diesel_on_hours"] = diesel_on_hours
                origin_metrics[f"{cell_label}_diesel_startups"] = startups
                origin_metrics[f"{cell_label}_realized_unmet_load_wh"] = replay["realized_unmet_load_energy_wh"]
                origin_metrics[f"{cell_label}_realized_curtailment_wh"] = replay["realized_curtailment_energy_wh"]
                origin_metrics[f"{cell_label}_realized_charge_wh"] = replay["realized_battery_charge_energy_wh"]
                origin_metrics[f"{cell_label}_realized_discharge_wh"] = replay["realized_battery_discharge_energy_wh"]
                origin_metrics[f"{cell_label}_realized_soc_min_pct"] = min(replay["realized_soc_pct"])
                origin_metrics[f"{cell_label}_realized_soc_max_pct"] = max(replay["realized_soc_pct"])
                origin_metrics[f"{cell_label}_terminal_soc_pct"] = replay["realized_soc_pct"][-1]
                origin_metrics[f"{cell_label}_soc_floor_violations"] = len(replay["soc_violations"])
                origin_metrics[f"{cell_label}_battery_efc"] = round(efc, 6)
                origin_metrics[f"{cell_label}_critical_demand_total_wh"] = arrsum(critical_demand_w)

        results[origin_str] = origin_result
        origin_rows_out.append(origin_metrics)

        if (i + 1) % 50 == 0 or (i + 1) == len(origin_order_2024):
            print(f"  ... {i+1}/{len(origin_order_2024)} origins processed [{round(time.time()-t_start,1)}s elapsed]")

    elapsed_s = round(time.time() - t_start, 1)
    origin_df = pd.DataFrame(origin_rows_out)
    origin_df.to_csv(THIS_DIR / "terminal_reserve_ablation_origin_level.csv", index=False)

    both_normal_245 = origin_df[
        (origin_df.get("F_ON_route") == "NORMAL") & (origin_df.get("K_ON_route") == "NORMAL")
    ].copy()
    both_normal_off = origin_df[
        (origin_df.get("F_OFF_route") == "NORMAL") & (origin_df.get("K_OFF_route") == "NORMAL")
    ].copy()
    both_normal_all4 = origin_df[
        (origin_df.get("F_ON_route") == "NORMAL") & (origin_df.get("K_ON_route") == "NORMAL") &
        (origin_df.get("F_OFF_route") == "NORMAL") & (origin_df.get("K_OFF_route") == "NORMAL")
    ].copy()

    def paired_metric(df_subset, colname_f, colname_k):
        f_vals = df_subset[colname_f].astype(float).values
        k_vals = df_subset[colname_k].astype(float).values
        deltas = f_vals - k_vals
        return {
            "f_mean": round(float(f_vals.mean()), 4) if len(f_vals) else None,
            "k_mean": round(float(k_vals.mean()), 4) if len(k_vals) else None,
            "paired_delta_f_minus_k": paired_bootstrap_ci(deltas),
        }

    metrics_defs = [
        ("unmet_load_wh", "realized_unmet_load_wh"),
        ("diesel_fuel_l", "realized_diesel_fuel_l"),
        ("diesel_on_hours", "diesel_on_hours"),
        ("diesel_startups", "diesel_startups"),
        ("curtailment_wh", "realized_curtailment_wh"),
        ("battery_efc", "battery_efc"),
        ("soc_floor_violations", "soc_floor_violations"),
        ("terminal_soc_pct", "terminal_soc_pct"),
        ("solve_time_s", "solve_time_s"),
    ]
    summary = {"n_origins_2024": len(origin_order_2024),
               "n_both_normal_ON": len(both_normal_245),
               "n_both_normal_OFF": len(both_normal_off),
               "n_both_normal_ALL4": len(both_normal_all4)}
    for reserve_mode, df_subset in [("ON", both_normal_245), ("OFF", both_normal_off)]:
        summary[reserve_mode] = {}
        for metric_name, col_suffix in metrics_defs:
            summary[reserve_mode][metric_name] = paired_metric(
                df_subset, f"F_{reserve_mode}_{col_suffix}", f"K_{reserve_mode}_{col_suffix}")
        tot_crit_f = df_subset[f"F_{reserve_mode}_critical_demand_total_wh"].astype(float).sum() if len(df_subset) else 0.0
        tot_unmet_f = df_subset[f"F_{reserve_mode}_realized_unmet_load_wh"].astype(float).sum() if len(df_subset) else 0.0
        tot_crit_k = df_subset[f"K_{reserve_mode}_critical_demand_total_wh"].astype(float).sum() if len(df_subset) else 0.0
        tot_unmet_k = df_subset[f"K_{reserve_mode}_realized_unmet_load_wh"].astype(float).sum() if len(df_subset) else 0.0
        summary[reserve_mode]["reliability_F"] = round(1.0 - tot_unmet_f / tot_crit_f, 6) if tot_crit_f > 0 else None
        summary[reserve_mode]["reliability_K"] = round(1.0 - tot_unmet_k / tot_crit_k, 6) if tot_crit_k > 0 else None
        summary[reserve_mode]["optimizer_failures_F"] = int(df_subset.get(f"F_{reserve_mode}_optimizer_failed", pd.Series(dtype=bool)).sum())
        summary[reserve_mode]["optimizer_failures_K"] = int(df_subset.get(f"K_{reserve_mode}_optimizer_failed", pd.Series(dtype=bool)).sum())

    # Primary comparison: on the common ALL4-both-normal subset, (F_OFF vs K_OFF) vs (F_ON vs K_ON)
    primary = {}
    for reserve_mode in ["ON", "OFF"]:
        primary[reserve_mode] = {}
        for metric_name, col_suffix in metrics_defs:
            primary[reserve_mode][metric_name] = paired_metric(
                both_normal_all4, f"F_{reserve_mode}_{col_suffix}", f"K_{reserve_mode}_{col_suffix}")
    summary["primary_comparison_common_subset_n"] = len(both_normal_all4)
    summary["primary_comparison_ON_vs_OFF_same_subset"] = primary

    summary_rows = []
    for reserve_mode in ["ON", "OFF"]:
        for metric_name, _ in metrics_defs:
            v = summary[reserve_mode][metric_name]
            summary_rows.append({
                "reserve_mode": reserve_mode, "metric": metric_name,
                "f_mean": v["f_mean"], "k_mean": v["k_mean"],
                "paired_delta_f_minus_k_mean": v["paired_delta_f_minus_k"]["mean"],
                "ci_95_lower": v["paired_delta_f_minus_k"]["ci_95_lower"],
                "ci_95_upper": v["paired_delta_f_minus_k"]["ci_95_upper"],
                "n_paired": v["paired_delta_f_minus_k"]["n"],
            })
    pd.DataFrame(summary_rows).to_csv(THIS_DIR / "terminal_reserve_ablation_results.csv", index=False)

    manifest = {
        "disclaimer": (
            "TERMINAL RESERVE ON/OFF ABLATION. RESEARCH-ONLY. 2x2: {F,K} x {reserve ON,OFF}. "
            "OFF removes ONLY the terminal-reserve override at hour 23 "
            "(configs['terminal_target_wh']=0.0, which makes "
            "max(ebr_target_wh_list[23], terminal_target_wh) reduce to ebr_target_wh_list[23] "
            "-- the governed EBR 6h-lookahead requirement, battery SOC floor/ceiling bounds, "
            "charge/discharge limits, diesel constraints, load constraints, optimizer "
            "settings, and replay mechanics are all unchanged, confirmed by inspection of "
            "gap19_highs_native.py. F and K were never retrained, regenerated, or modified. "
            "GAP19 called once per origin per cell for planning only, never re-run with "
            "actual solar. Candidate K is NOT promoted by this experiment."
        ),
        "input_hashes": hashes,
        "k_config_verbatim": {"variant": K_VARIANT, "alpha": K_ALPHA, "min_history": K_MIN_HISTORY,
                               "max_clip": K_MAX_CLIP, "scale_mode": K_SCALE_MODE},
        "elapsed_s": elapsed_s,
        "summary": summary,
        "results": results,
    }
    with open(THIS_DIR / "TERMINAL_RESERVE_ABLATION_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"\nResults written to {THIS_DIR}")
    print(f"Elapsed: {elapsed_s}s")
    print("ABLATION COMPLETE. No production/F/K/Stage8.1 artifact modified. K remains research-only.")


if __name__ == "__main__":
    main()
