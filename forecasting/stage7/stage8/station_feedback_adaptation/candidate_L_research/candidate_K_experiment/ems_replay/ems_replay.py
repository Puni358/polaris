#!/usr/bin/env python3
"""
CANDIDATE F vs CANDIDATE K -- ACTUAL-SOLAR EMS REPLAY. RESEARCH-ONLY.
NOT a production run. NOT a re-optimization. NOT a promotion decision.

SCOPE EXTENSION (explicit, user-authorized): Candidate K was tuned on 2022 and blind-
evaluated on Jan-Sep 2023 (see ../candidate_K_report.md, ../candidate_K_manifest.json).
The only validated EMS fixture with actual wind/demand/station-state ground truth in this
repository (ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv, hash-pinned, used unmodified by
run_actual_solar_replay.py / run_candidateF_actual_solar_replay.py) covers ONLY calendar
year 2024 -- no validated 2023 wind/demand/station-state fixture exists anywhere in this
repository (verified by exhaustive search before writing this script). 2023 is therefore
NOT reproducible as an EMS replay. Per explicit user instruction, this script instead runs
Candidate F vs Candidate K as a SEPARATE, clearly-labeled 2024 operational EMS evaluation,
using:
  - Candidate F's frozen model, applied read-only to the frozen 2024 feature matrix (the
    SAME model, SAME application method already used and disclosed in
    run_candidateF_actual_solar_replay.py -- not retrained, not modified).
  - Candidate K's ALREADY-LOCKED configuration, taken verbatim from
    candidate_K_manifest.json: variant=A_global, alpha=0.1, min_history=1, max_clip=75.0
    W/m^2, scale_mode=unscaled. NOT retuned. NOT selected using 2024 outcomes.
  - Candidate K's own causal EWMA update function (`run_simulation` in
    candidate_K_experiment.py), imported UNMODIFIED. 2024 K predictions are produced by
    continuing that exact causal state forward from the end of the frozen 2020-2023
    historical residual dataset into the 2024 origins, in chronological order -- i.e. K's
    mu_global EWMA state at 2024-01-01 is whatever it already was at the end of
    2023-09-30 per the frozen, hash-verified history. This is application of an existing,
    frozen procedure to new inputs, NOT retraining and NOT hyperparameter selection.
  - The SAME validated 2024 EMS replay methodology already used for the Candidate F vs
    frozen-Stage-8.1 comparison: `replay_plan_against_actual_solar` / `pv_from_sw_in`
    (run_actual_solar_replay.py) and `predict_solar_bundle` / `sw_in_to_power_w`
    (run_candidateF_actual_solar_replay.py), imported UNMODIFIED. GAP19 (the real,
    unmodified optimizer) is called exactly once per origin per arm for PLANNING only; it
    is NEVER re-run with actual solar as an input. Origins, actual solar, actual wind,
    actual demand, station state, initial SOC, diesel state, optimizer, optimizer
    configuration, terminal/reserve policy, MPC/replay mechanics and timestep are IDENTICAL
    between the F arm and the K arm for every origin -- the ONLY difference is which solar
    forecast (F's vs K's) feeds the optimizer's planning step.

No production code, config, frozen artifact, Stage 8.1, F, K, or the validated EMS fixture
is modified by this script. All new files are written under
forecasting/candidate_L_research/candidate_K_experiment/ems_replay/.
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

K_EXPERIMENT_DIR = BASE / "forecasting/candidate_L_research" / "candidate_K_experiment"
sys.path.insert(0, str(K_EXPERIMENT_DIR))

THIS_DIR = Path(__file__).parent

import run_full_experiment as rfe
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_actual_solar_replay import pv_from_sw_in, replay_plan_against_actual_solar
from run_candidateF_actual_solar_replay import predict_solar_bundle, sw_in_to_power_w, ADDITIVE_FEATURE_NAME

import candidate_K_experiment as ck  # imported UNMODIFIED; run_simulation reused by import

CANDIDATE_F_MODEL_PATH = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib"
EXPECTED_CANDIDATE_F_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"

MATRIX_2024_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"

HISTORICAL_RESIDUAL_DATASET_PATH = BASE / "forecasting/candidate_L_research" / "CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv"
EXPECTED_HISTORICAL_RESIDUAL_HASH = "1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab"

# Candidate K's ALREADY-LOCKED configuration (candidate_K_manifest.json, selected_hyperparameters).
# NOT retuned here. Reused verbatim.
K_VARIANT = "A_global"
K_ALPHA = 0.1
K_MIN_HISTORY = 1
K_MAX_CLIP = 75.0
K_SCALE_MODE = "unscaled"

N_BOOTSTRAP = 2000
BOOTSTRAP_SEED = 42


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_all_hashes():
    print("--- Verifying frozen/immutable input hashes ---")
    checks = [
        ("candidate_F_model", sha256_of(CANDIDATE_F_MODEL_PATH), EXPECTED_CANDIDATE_F_HASH),
        ("matrix_2024", sha256_of(MATRIX_2024_PATH), EXPECTED_MATRIX_2024_HASH),
        ("historical_residual_dataset_2020_2023", sha256_of(HISTORICAL_RESIDUAL_DATASET_PATH),
         EXPECTED_HISTORICAL_RESIDUAL_HASH),
    ]
    all_ok = True
    for name, actual, expected in checks:
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"  {name}: {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            print(f"    expected={expected}\n    actual  ={actual}")
    if not all_ok:
        raise RuntimeError("STOP: input hash verification FAILED. Halting -- no improvisation.")
    print("All hashes verified OK.\n")
    return {name: actual for name, actual, _ in checks}


def load_historical_origin_map():
    """Loads the frozen 2020-2023 historical residual dataset exactly as
    candidate_K_experiment.py's main() does (same field parsing, same dict shape), so that
    `ck.run_simulation` can be called unmodified over 2020-2023 + 2024 combined."""
    with open(HISTORICAL_RESIDUAL_DATASET_PATH, mode="r") as f:
        import csv
        reader = csv.DictReader(f)
        rows = list(reader)
    for r in rows:
        r["solar_elevation"] = float(r["solar_elevation"])
        r["cloud_frac"] = float(r["cloud_frac"])
        r["prediction"] = float(r["prediction"])
        r["actual"] = float(r["actual"])
        r["residual"] = float(r["residual"])
        r["horizon_hour"] = int(r["horizon_hour"])

    origin_map = {}
    origin_order = []
    for r in rows:
        o = r["forecast_start"]
        if o not in origin_map:
            origin_map[o] = []
            origin_order.append(o)
        origin_map[o].append(r)
    return origin_order, origin_map


def build_2024_rows(model_f, candidate_f_features, df_2024):
    """For every 2024 origin, computes Candidate F's own frozen prediction (same model,
    same `predict_solar_bundle` reconstruction already used and disclosed in
    run_candidateF_actual_solar_replay.py) for all 24 horizon hours, and packages each row
    in the exact dict shape `ck.run_simulation` expects (solar_elevation, cloud_frac,
    prediction, actual, residual). F is NOT re-called later; these are the same values
    reused for both the EWMA-state continuation and the EMS solar_generation bundle."""
    origin_order_2024 = []
    origin_map_2024 = {}
    origin_f_pred_sw_in = {}  # forecast_start -> list[24] of F's pred_sw_in, horizon-sorted

    for origin, origin_rows_all in df_2024.groupby("forecast_start", sort=True):
        origin_rows_all = origin_rows_all.sort_values("horizon_hour").reset_index(drop=True)
        solar_gen_f_w = predict_solar_bundle(
            model_f, candidate_f_features, origin_rows_all,
            extra_feature_fn=lambda d: d["solar_elevation"] * d["cloud_frac"])
        # Recover pred_sw_in (pre-power-conversion) the same way predict_solar_bundle does,
        # needed in SW_IN units for the EWMA residual stream (same units as 2020-2023 data).
        solar_elevation = origin_rows_all["solar_elevation"].values
        clearsky_ghi = origin_rows_all["clearsky_ghi"].values
        is_night_causal = (solar_elevation <= 0.0) | (clearsky_ghi == 0.0)
        df_feat = origin_rows_all.copy()
        df_feat[ADDITIVE_FEATURE_NAME] = df_feat["solar_elevation"] * df_feat["cloud_frac"]
        X = df_feat[candidate_f_features].values.astype(np.float64)
        residual_model = model_f.predict(X)
        pred_stage4 = origin_rows_all["pred_stage4_fold"].values
        pred_sw_in = np.maximum(0.0, pred_stage4 + residual_model)
        pred_sw_in = np.where(is_night_causal, 0.0, pred_sw_in)

        origin_str = str(origin)
        rows = []
        for i in range(len(origin_rows_all)):
            actual_v = float(origin_rows_all["actual_SW_IN"].values[i])
            pred_v = float(pred_sw_in[i])
            rows.append({
                "forecast_start": origin_str,
                "horizon_hour": int(origin_rows_all["horizon_hour"].values[i]),
                "solar_elevation": float(solar_elevation[i]),
                "cloud_frac": float(origin_rows_all["cloud_frac"].values[i]),
                "prediction": pred_v,
                "actual": actual_v,
                "residual": actual_v - pred_v,
            })
        origin_order_2024.append(origin_str)
        origin_map_2024[origin_str] = rows
        origin_f_pred_sw_in[origin_str] = [round(v, 2) for v in sw_in_to_power_w_vec(pred_sw_in)]

    return origin_order_2024, origin_map_2024, origin_f_pred_sw_in


def sw_in_to_power_w_vec(arr):
    return [sw_in_to_power_w(v) for v in arr]


def arrsum(a):
    return round(float(sum(a)), 4)


def paired_bootstrap_ci(deltas, n_iterations=N_BOOTSTRAP, seed=BOOTSTRAP_SEED):
    """Origin-level paired bootstrap CI on a list of per-origin (F - K) deltas (F worse is
    positive, i.e. K improvement). New, read-only analysis code -- does not touch GAP19 or
    any frozen artifact."""
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
    print("CANDIDATE F vs CANDIDATE K -- 2024 ACTUAL-SOLAR EMS REPLAY. RESEARCH-ONLY.")
    print("SCOPE EXTENSION: 2024 operational EMS evaluation, NOT the frozen 2023 blind test.")
    print("K config taken verbatim from candidate_K_manifest.json. NOT retuned on 2024.")
    print("=" * 80)

    hashes = verify_all_hashes()
    rfe.verify_frozen_manifest()

    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)
    candidate_f_features = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]

    print("Loading frozen 2020-2023 historical residual dataset (carries K's causal EWMA "
          "state forward into 2024, unmodified)...")
    origin_order_hist, origin_map_hist = load_historical_origin_map()
    print(f"  {len(origin_order_hist)} historical origins (2020-01-01 .. 2023-09-30) loaded.")

    print("Computing Candidate F's own frozen predictions on the 2024 matrix "
          "(same model, same method as run_candidateF_actual_solar_replay.py)...")
    df_2024 = pd.read_csv(MATRIX_2024_PATH)
    df_2024["forecast_start"] = pd.to_datetime(df_2024["forecast_start"], utc=True)
    origin_order_2024, origin_map_2024, origin_f_pred_power_w = build_2024_rows(
        model_f, candidate_f_features, df_2024)
    print(f"  {len(origin_order_2024)} 2024 origins loaded.\n")

    print(f"Running Candidate K's own causal EWMA procedure (variant={K_VARIANT}, "
          f"alpha={K_ALPHA}, min_history={K_MIN_HISTORY}, max_clip={K_MAX_CLIP}, "
          f"scale_mode={K_SCALE_MODE}) continuously across 2020-2023 + 2024, via "
          f"candidate_K_experiment.run_simulation (imported UNMODIFIED)...")
    combined_origin_order = origin_order_hist + origin_order_2024
    combined_origin_map = dict(origin_map_hist)
    combined_origin_map.update(origin_map_2024)
    history_records = ck.run_simulation(
        combined_origin_order, combined_origin_map,
        K_VARIANT, K_ALPHA, K_MIN_HISTORY, K_MAX_CLIP, K_SCALE_MODE,
    )
    k_pred_lookup = {}  # (forecast_start, horizon_hour) -> k_prediction (SW_IN, W/m^2)
    for r in history_records:
        if r["forecast_start"] in origin_map_2024:
            k_pred_lookup[(r["forecast_start"], r["horizon_hour"])] = r["k_prediction"]
    print(f"  K predictions generated for {len(k_pred_lookup)} 2024 (origin, horizon) pairs.\n")

    # --- EMS replay: real GAP19 components, real 2024 fixture, F arm vs K arm ---
    components = rfe.build_components()
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components

    eta_chg = float(configs_base.get("battery", {}).get("charge_efficiency", 0.92))
    eta_dis = float(configs_base.get("battery", {}).get("discharge_efficiency", 0.92))
    min_soc_pct = float(configs_base.get("battery", {}).get("min_soc_pct", 20.0))
    max_soc_pct = float(configs_base.get("battery", {}).get("max_soc_pct", 95.0))

    results = {}
    origin_level_rows = []
    t_start = time.time()
    n_normal = 0

    for i, origin_str in enumerate(origin_order_2024):
        origin_ts = pd.Timestamp(origin_str)
        origin_rows_all = df_2024[df_2024["forecast_start"] == origin_ts].sort_values(
            "horizon_hour").reset_index(drop=True)
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

        critical_load_baseline_w = float(
            configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
        )
        critical_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]
        timestamps = [(origin_ts + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                      for h in range(1, 25)]

        # --- Candidate F solar bundle (frozen model, already computed above) ---
        solar_gen_f = origin_f_pred_power_w[origin_str]
        bundle_f = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_f, solar_gen_f, solar_gen_f, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "candidate_F_elevation_x_cloud"},
            demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"),
        )

        # --- Candidate K solar bundle (K's causal EWMA correction on F, this origin) ---
        horizons_sorted = sorted(int(h) for h in origin_rows_all["horizon_hour"].values)
        k_sw_in_by_h = {h: k_pred_lookup.get((origin_str, h)) for h in horizons_sorted}
        solar_gen_k = []
        for h in horizons_sorted:
            v = k_sw_in_by_h[h]
            solar_gen_k.append(round(sw_in_to_power_w(v), 2) if v is not None else 0.0)
        bundle_k = ForecastBundle(
            schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_k, solar_gen_k, solar_gen_k, "W"),
            wind_generation=wind_gen, demand=demand_fc,
            metadata={"source": "candidate_K_ewma_correction"},
            demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"),
        )

        origin_result = {}
        origin_metrics = {"forecast_start": origin_str}
        for label, bundle in [("candidate_F", bundle_f), ("candidate_K", bundle_k)]:
            configs = dict(configs_base)
            configs["critical_demand_w"] = critical_demand_w
            configs["terminal_target_wh"] = rfe.compute_terminal_target_wh(bundle)

            assessment, route = router.evaluate_and_route(st_k, bundle, configs)
            if route != "NORMAL":
                origin_result[label] = {"route": route}
                origin_metrics[f"{label}_route"] = route
                continue

            t0 = time.perf_counter()
            plan = optimizer.optimize(bundle, st_k, configs)  # real, frozen, unmodified GAP19
            solve_time_s = time.perf_counter() - t0

            optimizer_failed = plan.constraint_status != "OPTIMAL"

            planned = {
                "constraint_status": plan.constraint_status,
                "planned_diesel_fuel_l": round(sum(
                    (base_fuel_lph if p > 0 else 0.0) + marginal_fuel_lpwh * p for p in plan.diesel_power), 4),
                "planned_curtailment_wh": arrsum(plan.renewable_curtailment),
                "planned_battery_charge_wh": arrsum(plan.battery_charge),
                "planned_battery_discharge_wh": arrsum(plan.battery_discharge),
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

            origin_result[label] = {"route": route, "planned": planned, "replay": replay}
            origin_metrics[f"{label}_route"] = route
            origin_metrics[f"{label}_optimizer_failed"] = optimizer_failed
            origin_metrics[f"{label}_solve_time_s"] = planned["solve_time_s"]
            origin_metrics[f"{label}_planned_diesel_fuel_l"] = planned["planned_diesel_fuel_l"]
            origin_metrics[f"{label}_realized_diesel_fuel_l"] = replay["realized_diesel_fuel_l"]
            origin_metrics[f"{label}_diesel_on_hours"] = diesel_on_hours
            origin_metrics[f"{label}_diesel_startups"] = startups
            origin_metrics[f"{label}_realized_unmet_load_wh"] = replay["realized_unmet_load_energy_wh"]
            origin_metrics[f"{label}_realized_curtailment_wh"] = replay["realized_curtailment_energy_wh"]
            origin_metrics[f"{label}_realized_charge_wh"] = replay["realized_battery_charge_energy_wh"]
            origin_metrics[f"{label}_realized_discharge_wh"] = replay["realized_battery_discharge_energy_wh"]
            origin_metrics[f"{label}_realized_soc_min_pct"] = min(replay["realized_soc_pct"])
            origin_metrics[f"{label}_realized_soc_max_pct"] = max(replay["realized_soc_pct"])
            origin_metrics[f"{label}_terminal_soc_pct"] = replay["realized_soc_pct"][-1]
            origin_metrics[f"{label}_soc_floor_violations"] = len(replay["soc_violations"])
            origin_metrics[f"{label}_battery_efc"] = round(efc, 6)
            origin_metrics[f"{label}_critical_demand_total_wh"] = arrsum(critical_demand_w)

        results[origin_str] = origin_result
        if origin_result.get("candidate_F", {}).get("route") == "NORMAL":
            n_normal += 1
        origin_level_rows.append(origin_metrics)

        if (i + 1) % 50 == 0 or (i + 1) == len(origin_order_2024):
            print(f"  ... {i+1}/{len(origin_order_2024)} origins processed ({n_normal} NORMAL) "
                  f"[{round(time.time()-t_start,1)}s elapsed]")

    elapsed_s = round(time.time() - t_start, 1)

    # --- Write origin-level CSV ---
    origin_df = pd.DataFrame(origin_level_rows)
    origin_df.to_csv(THIS_DIR / "ems_replay_origin_level.csv", index=False)

    # --- Paired statistics (only origins where BOTH arms routed NORMAL) ---
    both_normal = origin_df[
        (origin_df.get("candidate_F_route") == "NORMAL") & (origin_df.get("candidate_K_route") == "NORMAL")
    ].copy()
    n_both_normal = len(both_normal)
    n_route_mismatch = len(origin_df[origin_df.get("candidate_F_route") != origin_df.get("candidate_K_route")])

    def paired_metric(colname_f, colname_k):
        f_vals = both_normal[colname_f].astype(float).values
        k_vals = both_normal[colname_k].astype(float).values
        deltas = f_vals - k_vals  # positive = F worse than K (for "higher is worse" metrics)
        return {
            "f_mean": round(float(f_vals.mean()), 4) if len(f_vals) else None,
            "k_mean": round(float(k_vals.mean()), 4) if len(k_vals) else None,
            "f_total": round(float(f_vals.sum()), 4) if len(f_vals) else None,
            "k_total": round(float(k_vals.sum()), 4) if len(k_vals) else None,
            "paired_delta_f_minus_k": paired_bootstrap_ci(deltas),
        }

    summary_stats = {
        "n_origins_2024": len(origin_order_2024),
        "n_both_normal": n_both_normal,
        "n_route_mismatch": n_route_mismatch,
        "unmet_load_wh": paired_metric("candidate_F_realized_unmet_load_wh", "candidate_K_realized_unmet_load_wh"),
        "diesel_fuel_l": paired_metric("candidate_F_realized_diesel_fuel_l", "candidate_K_realized_diesel_fuel_l"),
        "diesel_on_hours": paired_metric("candidate_F_diesel_on_hours", "candidate_K_diesel_on_hours"),
        "diesel_startups": paired_metric("candidate_F_diesel_startups", "candidate_K_diesel_startups"),
        "curtailment_wh": paired_metric("candidate_F_realized_curtailment_wh", "candidate_K_realized_curtailment_wh"),
        "battery_efc": paired_metric("candidate_F_battery_efc", "candidate_K_battery_efc"),
        "soc_floor_violations": paired_metric("candidate_F_soc_floor_violations", "candidate_K_soc_floor_violations"),
        "solve_time_s": paired_metric("candidate_F_solve_time_s", "candidate_K_solve_time_s"),
        "optimizer_failures_F": int(origin_df.get("candidate_F_optimizer_failed", pd.Series(dtype=bool)).sum()),
        "optimizer_failures_K": int(origin_df.get("candidate_K_optimizer_failed", pd.Series(dtype=bool)).sum()),
        "reliability_F": None,
        "reliability_K": None,
    }
    tot_crit_f = both_normal["candidate_F_critical_demand_total_wh"].astype(float).sum() if n_both_normal else 0.0
    tot_unmet_f = both_normal["candidate_F_realized_unmet_load_wh"].astype(float).sum() if n_both_normal else 0.0
    tot_crit_k = both_normal["candidate_K_critical_demand_total_wh"].astype(float).sum() if n_both_normal else 0.0
    tot_unmet_k = both_normal["candidate_K_realized_unmet_load_wh"].astype(float).sum() if n_both_normal else 0.0
    if tot_crit_f > 0:
        summary_stats["reliability_F"] = round(1.0 - tot_unmet_f / tot_crit_f, 6)
    if tot_crit_k > 0:
        summary_stats["reliability_K"] = round(1.0 - tot_unmet_k / tot_crit_k, 6)

    # --- Results CSV (flat summary table, one row per metric) ---
    summary_rows = []
    for metric, v in summary_stats.items():
        if isinstance(v, dict) and "f_mean" in v:
            summary_rows.append({
                "metric": metric, "f_mean": v["f_mean"], "k_mean": v["k_mean"],
                "f_total": v["f_total"], "k_total": v["k_total"],
                "paired_delta_f_minus_k_mean": v["paired_delta_f_minus_k"]["mean"],
                "ci_95_lower": v["paired_delta_f_minus_k"]["ci_95_lower"],
                "ci_95_upper": v["paired_delta_f_minus_k"]["ci_95_upper"],
                "n_paired": v["paired_delta_f_minus_k"]["n"],
            })
    pd.DataFrame(summary_rows).to_csv(THIS_DIR / "ems_replay_results.csv", index=False)

    # --- Full JSON (per-origin detail, for forensic traceability) ---
    manifest = {
        "disclaimer": (
            "CANDIDATE F vs CANDIDATE K 2024 EMS REPLAY. RESEARCH-ONLY. SCOPE EXTENSION: "
            "this is a 2024 operational EMS evaluation period, NOT the original frozen 2023 "
            "blind forecast test (candidate_K_blind_results.csv / candidate_K_report.md). "
            "Candidate K's configuration (A_global, alpha=0.1, min_history=1, max_clip=75, "
            "unscaled) is taken verbatim from candidate_K_manifest.json and was NOT retuned "
            "or selected using 2024 outcomes. GAP19 was called once per origin per arm for "
            "planning only, and never re-run with actual solar as an input. Diesel and "
            "battery-discharge commands are held exactly as planned in the replay; only "
            "renewable usage/curtailment, battery charge, realized SOC, and realized unmet "
            "load are recomputed against actual 2024 solar. Candidate K is NOT promoted by "
            "this experiment. Not a production run. Not stakeholder-authorized."
        ),
        "input_hashes": hashes,
        "k_config_verbatim_from_manifest": {
            "variant": K_VARIANT, "alpha": K_ALPHA, "min_history": K_MIN_HISTORY,
            "max_clip": K_MAX_CLIP, "scale_mode": K_SCALE_MODE,
        },
        "num_origins_2024": len(origin_order_2024),
        "num_normal_candidate_F": n_normal,
        "n_both_normal": n_both_normal,
        "n_route_mismatch": n_route_mismatch,
        "elapsed_s": elapsed_s,
        "summary_stats": summary_stats,
        "results": results,
    }
    with open(THIS_DIR / "EMS_REPLAY_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"\nResults written to {THIS_DIR}")
    print(f"Elapsed: {elapsed_s}s")
    print("EMS REPLAY COMPLETE. No production/config/freeze file, F, K, Stage 8.1, or the "
          "validated EMS fixture modified. Candidate K remains research-only / NOT promoted.")


if __name__ == "__main__":
    main()
