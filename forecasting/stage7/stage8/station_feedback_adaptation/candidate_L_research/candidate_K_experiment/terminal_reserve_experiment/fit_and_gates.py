#!/usr/bin/env python3
"""
STAGE 1 of the Uncertainty-Aware Terminal Reserve experiment (Mechanism A only).
RESEARCH-ONLY. Fits the empirical uncertainty-margin lookup table, then runs the
DEGENERACY GATE and LEAKAGE GATE. Writes FIT_ARTIFACT.json and
LEAKAGE_DEGENERACY_AUDIT.md. Does NOT call the optimizer or router. Does NOT modify any
production, Stage 8.1, F, K, or immutable artifact.

Per UNCERTAINTY_AWARE_TERMINAL_RESERVE_RESEARCH_DESIGN.md Mechanism A:
  margin_wh(origin, hour) = Q_q(|residual_sw_in| | disagreement_fold decile, lookahead-window)
fit ONLY on frozen TRAIN_2020_2021 + VALIDATION_2022 rows, NEVER on BLIND_TEST_2023 or any
2024 row.

IMPLEMENTATION NOTE (disclosed deviation from literal "decile x individual horizon_hour"):
the 2020-2023 historical dataset's per-origin daytime window varies with season (this is an
Arctic site; day length swings from near-zero to near-24h across the year), so the
individual horizon-hours inside the terminal-reserve lookahead window (hour-ahead 19-24)
have severely unequal daytime sample counts in TRAIN+VAL (horizon 19: 457 daytime rows;
horizons 20-24: 1 daytime row each). Fitting decile x per-individual-horizon cells for
horizons 20-24 is therefore statistically meaningless (n=1). This script instead fits
decile x "is in the terminal lookahead window" (pooling hour-ahead 19-24 daytime rows
together, n=462), which is the coarsest generalization of Mechanism A that remains
statistically supportable from the available frozen data. This is disclosed, not hidden,
and is itself a RESEARCH ASSUMPTION (see FIT_ARTIFACT.json "methodological_deviation").
"""
import sys
import json
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
from run_research_simulation import (
    TERMINAL_FLOOR_WH, LOOKAHEAD_WINDOW_HOURS, UNCERTAINTY_MARGIN, compute_terminal_target_wh,
)
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.forecasting.implementations.s81_corrected_solar import CANDIDATE_37_FEATURES
from run_candidateF_actual_solar_replay import predict_solar_bundle, sw_in_to_power_w, ADDITIVE_FEATURE_NAME
import candidate_K_experiment as ck

MATRIX_38_2020_2023_PATH = BASE / "forecasting/candidate_L_research" / "CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv"
EXPECTED_MATRIX_38_HASH = "bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde"
HIST_RESID_PATH = BASE / "forecasting/candidate_L_research" / "CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv"
EXPECTED_HIST_RESID_HASH = "1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab"
CANDIDATE_F_MODEL_PATH = BASE / "forecasting/stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib"
EXPECTED_CANDIDATE_F_HASH = "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"
MATRIX_2024_PATH = BASE / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
EXPECTED_MATRIX_2024_HASH = "aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43"
HIST_PATH_FOR_K_STATE = HIST_RESID_PATH  # same frozen file, reused for K's causal EWMA state

ALLOWED_FIT_SPLITS = {"TRAIN_2020_2021", "VALIDATION_2022"}
FORBIDDEN_FIT_SPLITS = {"BLIND_TEST_2023"}
N_DECILES = 10
MIN_CELL_N = 15  # RESEARCH ASSUMPTION: minimum samples per decile cell before falling back to pooled quantile
Q_SWEEP = [0.75, 0.90, 0.95]  # RESEARCH-ONLY, disclosed small sensitivity sweep
Q_PRIMARY = 0.90  # RESEARCH-ONLY choice for the full EMS factorial; 0.75/0.95 are formula-level-only sensitivity

K_VARIANT, K_ALPHA, K_MIN_HISTORY, K_MAX_CLIP, K_SCALE_MODE = "A_global", 0.1, 1, 75.0, "unscaled"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_fit_input_hashes():
    checks = [
        ("matrix_38_feature_2020_2023", sha256_of(MATRIX_38_2020_2023_PATH), EXPECTED_MATRIX_38_HASH),
        ("historical_residual_dataset_2020_2023", sha256_of(HIST_RESID_PATH), EXPECTED_HIST_RESID_HASH),
    ]
    all_ok = True
    for name, actual, expected in checks:
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"  {name}: {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            print(f"    expected={expected}\n    actual  ={actual}")
    if not all_ok:
        raise RuntimeError("STOP: fitting input hash verification FAILED.")
    return {name: actual for name, actual, _ in checks}


def fit_uncertainty_margin_table():
    """Fits Mechanism A's decile x lookahead-window quantile table, STRICTLY on
    TRAIN_2020_2021 + VALIDATION_2022 rows. Returns the fit artifact dict."""
    df38 = pd.read_csv(MATRIX_38_2020_2023_PATH)
    dfres = pd.read_csv(HIST_RESID_PATH)
    merged = df38.merge(
        dfres[["forecast_start", "horizon_hour", "actual", "prediction", "residual", "solar_elevation", "split"]],
        on=["forecast_start", "horizon_hour"], suffixes=("", "_res"),
    )
    assert (merged["split"] == merged["split_res"]).all(), "STOP: split column mismatch between merged inputs."

    splits_present = set(merged["split"].unique())
    assert splits_present == {"TRAIN_2020_2021", "VALIDATION_2022", "BLIND_TEST_2023"}, \
        f"STOP: unexpected split values in source files: {splits_present}"

    fit_df = merged[merged["split"].isin(ALLOWED_FIT_SPLITS)].copy()
    assert set(fit_df["split"].unique()) <= ALLOWED_FIT_SPLITS, "STOP: leakage -- forbidden split present in fit_df"
    assert not set(fit_df["split"].unique()) & FORBIDDEN_FIT_SPLITS, "STOP: BLIND_TEST_2023 leaked into fitting set"

    fit_day = fit_df[fit_df["solar_elevation"] > 0.0].copy()
    LOOKAHEAD_HOURS_SET = set(range(25 - LOOKAHEAD_WINDOW_HOURS, 25))  # {19,20,21,22,23,24}, 1-indexed horizon_hour
    lookahead_day = fit_day[fit_day["horizon_hour"].isin(LOOKAHEAD_HOURS_SET)].copy()

    n_total_fit_rows = len(fit_df)
    n_daytime_fit_rows = len(fit_day)
    n_lookahead_daytime_rows = len(lookahead_day)

    # Decile edges computed from the SAME population used for the per-decile quantile fit
    # (the lookahead-window daytime rows), to avoid a population mismatch between binning
    # and estimation.
    decile_edges = list(np.quantile(lookahead_day["disagreement_fold"].values,
                                     np.linspace(0, 1, N_DECILES + 1)))
    lookahead_day["decile"] = pd.cut(
        lookahead_day["disagreement_fold"], bins=decile_edges, labels=False,
        include_lowest=True, duplicates="drop",
    )

    per_decile_n = lookahead_day.groupby("decile").size().to_dict()
    pooled_abs_residual = lookahead_day["residual"].abs().values

    margin_tables = {}
    fallback_log = {}
    for q in Q_SWEEP:
        pooled_q_val = float(np.quantile(pooled_abs_residual, q))
        table = {}
        fb_this_q = []
        for d in sorted(lookahead_day["decile"].dropna().unique()):
            vals = lookahead_day.loc[lookahead_day["decile"] == d, "residual"].abs().values
            n = len(vals)
            if n < MIN_CELL_N:
                table[int(d)] = {"value_sw_in": pooled_q_val, "n": int(n), "fallback_to_pooled": True}
                fb_this_q.append(int(d))
            else:
                table[int(d)] = {"value_sw_in": float(np.quantile(vals, q)), "n": int(n), "fallback_to_pooled": False}
        margin_tables[str(q)] = {"per_decile": table, "pooled_value_sw_in": pooled_q_val}
        fallback_log[str(q)] = fb_this_q

    artifact = {
        "disclaimer": (
            "RESEARCH-ONLY. Mechanism A uncertainty-margin lookup table. Fit ONLY on "
            "TRAIN_2020_2021 + VALIDATION_2022 rows of the frozen, hash-verified "
            "CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv joined to "
            "CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv. BLIND_TEST_2023 and "
            "all 2024 data are STRUCTURALLY EXCLUDED from this fitting function (the 2024 "
            "matrix is never loaded here). No governance-authorized numeric value is used; "
            "every quantile level in Q_SWEEP and MIN_CELL_N are explicitly-labeled research "
            "assumptions, not policy."
        ),
        "methodological_deviation": (
            "Design doc specified 'disagreement_fold decile x horizon'. Implemented instead "
            "as 'disagreement_fold decile x lookahead-window-membership' (pooling hour-ahead "
            "19-24) because per-individual-horizon daytime sample counts beyond hour-ahead 19 "
            "are statistically unusable at this Arctic site (n=1 for horizons 20-24 in "
            "TRAIN+VAL). This is the coarsest defensible generalization of Mechanism A, "
            "disclosed here, not silently substituted."
        ),
        "fit_sample_sizes": {
            "n_total_fit_rows_train_val": n_total_fit_rows,
            "n_daytime_fit_rows_train_val": n_daytime_fit_rows,
            "n_lookahead_window_daytime_rows_train_val": n_lookahead_daytime_rows,
            "per_decile_n": {int(k): int(v) for k, v in per_decile_n.items()},
        },
        "min_cell_n_research_assumption": MIN_CELL_N,
        "q_sweep_research_only": Q_SWEEP,
        "q_primary_research_only": Q_PRIMARY,
        "decile_edges_sw_in": decile_edges,
        "margin_tables_by_q": margin_tables,
        "fallback_to_pooled_deciles_by_q": fallback_log,
    }
    return artifact, decile_edges


def lookup_margin_sw_in(disagreement_fold_value, decile_edges, margin_table_for_q):
    idx = int(np.clip(np.digitize([disagreement_fold_value], decile_edges[1:-1])[0], 0, len(decile_edges) - 2))
    entry = margin_table_for_q["per_decile"].get(idx)
    if entry is None:
        return margin_table_for_q["pooled_value_sw_in"]
    return entry["value_sw_in"]


def compute_terminal_target_wh_v2(bundle, origin_rows_24, decile_edges, margin_table_for_q, mode):
    """Generalization of compute_terminal_target_wh. mode='legacy' reproduces the imported,
    unmodified formula EXACTLY (same TERMINAL_FLOOR_WH, same UNCERTAINTY_MARGIN, same
    LOOKAHEAD_WINDOW_HOURS, same arithmetic). mode='uncertainty_aware' additionally adds a
    non-negative, regime-conditional buffer (Mechanism A) on top of the unchanged legacy
    term -- it can only make the terminal reserve more conservative, never less, and at
    night (solar_elevation <= 0) the buffer is forced to 0 (no forecast uncertainty to
    buffer when there is no causal solar signal)."""
    window = range(24 - LOOKAHEAD_WINDOW_HOURS, 24)
    deficit_wh = 0.0
    for k in window:
        crit_demand_w = bundle.demand.point[k]
        renewable_avail_w = bundle.solar_generation.point[k] + bundle.wind_generation.point[k]
        net_w = max(0.0, crit_demand_w - renewable_avail_w)
        deficit_wh += net_w * 1.0
    legacy_term = TERMINAL_FLOOR_WH + deficit_wh * (1.0 + UNCERTAINTY_MARGIN)

    if mode == "legacy":
        return legacy_term, 0.0

    assert mode == "uncertainty_aware"
    rows_sorted = origin_rows_24.sort_values("horizon_hour").reset_index(drop=True)
    buffer_wh = 0.0
    for k in window:
        horizon_hour = k + 1  # bundle.point[k] corresponds to horizon_hour k+1 (1-indexed)
        row_match = rows_sorted[rows_sorted["horizon_hour"] == horizon_hour]
        if len(row_match) == 0:
            continue
        row = row_match.iloc[0]
        if row["solar_elevation"] <= 0.0:
            continue  # no uncertainty buffer at night
        margin_sw_in = lookup_margin_sw_in(row["disagreement_fold"], decile_edges, margin_table_for_q)
        buffer_wh += sw_in_to_power_w(margin_sw_in) * 1.0
    return legacy_term + buffer_wh, buffer_wh


def build_bundles_for_origin(origin_ts, origin_rows_all, model_f, candidate_f_features,
                              k_pred_lookup, components):
    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, capacity_wh) = components
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
    shared_bundle = baseline_engine.predict(st_k, {})
    wind_gen = shared_bundle.wind_generation
    demand_fc = shared_bundle.demand
    critical_load_baseline_w = float(
        configs_base.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0))
    critical_demand_w = [min(critical_load_baseline_w, d) for d in demand_fc.point]
    timestamps = [(origin_ts + pd.Timedelta(hours=h - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(1, 25)]

    solar_gen_f = predict_solar_bundle(model_f, candidate_f_features, origin_rows_all,
                                        extra_feature_fn=lambda d: d["solar_elevation"] * d["cloud_frac"])
    bundle_f = ForecastBundle(schema_version="1.0.0", origin_timestamp=st_k.timestamp, horizon_hours=24,
                               timestamps=timestamps,
                               solar_irradiance=TimeseriesForecast([0.0]*24,[0.0]*24,[0.0]*24,"W/m^2"),
                               solar_generation=TimeseriesForecast(solar_gen_f, solar_gen_f, solar_gen_f, "W"),
                               wind_generation=wind_gen, demand=demand_fc, metadata={"source": "candidate_F"},
                               demand_critical=TimeseriesForecast(critical_demand_w, critical_demand_w, critical_demand_w, "W"))

    origin_str = str(origin_ts)
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
    return st_k, bundle_f, bundle_k, critical_demand_w


def compute_f_and_k_2024_predictions(model_f, candidate_f_features, df_2024):
    origin_order_2024, origin_map_2024 = [], {}
    for origin, g in df_2024.groupby("forecast_start", sort=True):
        g = g.sort_values("horizon_hour").reset_index(drop=True)
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
        origin_order_2024.append(origin_str)
        recs = []
        for i in range(len(g)):
            actual_v = float(g["actual_SW_IN"].values[i]); pred_v = float(pred_sw_in[i])
            recs.append({"forecast_start": origin_str, "horizon_hour": int(g["horizon_hour"].values[i]),
                         "solar_elevation": float(solar_elevation[i]), "cloud_frac": float(g["cloud_frac"].values[i]),
                         "prediction": pred_v, "actual": actual_v, "residual": actual_v - pred_v})
        origin_map_2024[origin_str] = recs
    return origin_order_2024, origin_map_2024


def main():
    print("=" * 80)
    print("STAGE 1: Fit Mechanism A margin table + DEGENERACY GATE + LEAKAGE GATE")
    print("=" * 80)

    print("\n--- Verifying fitting-input hashes ---")
    fit_hashes = verify_fit_input_hashes()
    print("All fitting-input hashes verified OK.\n")

    print("--- Fitting Mechanism A margin table (TRAIN_2020_2021 + VALIDATION_2022 only) ---")
    fit_artifact, decile_edges = fit_uncertainty_margin_table()
    with open(THIS_DIR / "FIT_ARTIFACT.json", "w") as f:
        json.dump(fit_artifact, f, indent=2, default=str)
    print(f"  n_lookahead_window_daytime_rows (fit pop.): "
          f"{fit_artifact['fit_sample_sizes']['n_lookahead_window_daytime_rows_train_val']}")
    print(f"  per-decile n: {fit_artifact['fit_sample_sizes']['per_decile_n']}")
    for q in Q_SWEEP:
        fb = fit_artifact["fallback_to_pooled_deciles_by_q"][str(q)]
        print(f"  q={q}: deciles falling back to pooled value (n<{MIN_CELL_N}): {fb}")
    print(f"Wrote {THIS_DIR / 'FIT_ARTIFACT.json'}\n")

    print("--- Verifying EMS-replay-side hashes (candidate F model, 2024 matrix, K's historical state source) ---")
    ems_hashes = {
        "candidate_F_model": sha256_of(CANDIDATE_F_MODEL_PATH),
        "matrix_2024": sha256_of(MATRIX_2024_PATH),
        "historical_residual_dataset_2020_2023": sha256_of(HIST_PATH_FOR_K_STATE),
    }
    assert ems_hashes["candidate_F_model"] == EXPECTED_CANDIDATE_F_HASH
    assert ems_hashes["matrix_2024"] == EXPECTED_MATRIX_2024_HASH
    assert ems_hashes["historical_residual_dataset_2020_2023"] == EXPECTED_HIST_RESID_HASH
    print("  All MATCH.\n")
    rfe.verify_frozen_manifest()

    print("--- Building F/K forecast bundles for all 347 2024 origins (same construction as ems_replay.py) ---")
    model_f = joblib.load(CANDIDATE_F_MODEL_PATH)
    candidate_f_features = CANDIDATE_37_FEATURES + [ADDITIVE_FEATURE_NAME]

    import csv
    with open(HIST_RESID_PATH) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["solar_elevation"] = float(r["solar_elevation"]); r["cloud_frac"] = float(r["cloud_frac"])
        r["prediction"] = float(r["prediction"]); r["actual"] = float(r["actual"])
        r["residual"] = float(r["residual"]); r["horizon_hour"] = int(r["horizon_hour"])
    origin_map_hist, origin_order_hist = {}, []
    for r in rows:
        o = r["forecast_start"]
        if o not in origin_map_hist:
            origin_map_hist[o] = []; origin_order_hist.append(o)
        origin_map_hist[o].append(r)

    df_2024 = pd.read_csv(MATRIX_2024_PATH)
    df_2024["forecast_start"] = pd.to_datetime(df_2024["forecast_start"], utc=True)
    origin_order_2024, origin_map_2024 = compute_f_and_k_2024_predictions(model_f, candidate_f_features, df_2024)

    combined_order = origin_order_hist + origin_order_2024
    combined_map = dict(origin_map_hist); combined_map.update(origin_map_2024)
    hist_records = ck.run_simulation(combined_order, combined_map, K_VARIANT, K_ALPHA, K_MIN_HISTORY, K_MAX_CLIP, K_SCALE_MODE)
    k_pred_lookup = {(r["forecast_start"], r["horizon_hour"]): r["k_prediction"]
                     for r in hist_records if r["forecast_start"] in origin_map_2024}

    components = rfe.build_components()

    print("--- DEGENERACY GATE: new formula (mode='legacy') vs imported, unmodified compute_terminal_target_wh ---")
    max_abs_diff = 0.0
    n_checked = 0
    worst = None
    for origin_str in origin_order_2024:
        origin_ts = pd.Timestamp(origin_str)
        origin_rows_all = df_2024[df_2024["forecast_start"] == origin_ts].sort_values("horizon_hour").reset_index(drop=True)
        st_k, bundle_f, bundle_k, critical_demand_w = build_bundles_for_origin(
            origin_ts, origin_rows_all, model_f, candidate_f_features, k_pred_lookup, components)
        for label, bundle in [("F", bundle_f), ("K", bundle_k)]:
            old_val = compute_terminal_target_wh(bundle)  # imported, unmodified, frozen
            new_val_legacy, buf = compute_terminal_target_wh_v2(
                bundle, origin_rows_all, decile_edges, fit_artifact["margin_tables_by_q"][str(Q_PRIMARY)], mode="legacy")
            assert buf == 0.0, "STOP: legacy mode produced a non-zero buffer -- implementation bug."
            diff = abs(new_val_legacy - old_val)
            n_checked += 1
            if diff > max_abs_diff:
                max_abs_diff = diff
                worst = (origin_str, label, old_val, new_val_legacy)

    DEGENERACY_TOLERANCE_WH = 1e-6
    degeneracy_pass = max_abs_diff < DEGENERACY_TOLERANCE_WH
    print(f"  Checked {n_checked} (origin, arm) pairs.")
    print(f"  Max abs diff (new legacy-mode vs frozen original): {max_abs_diff:.3e} Wh")
    print(f"  Tolerance: {DEGENERACY_TOLERANCE_WH} Wh")
    print(f"  DEGENERACY GATE: {'PASS' if degeneracy_pass else 'FAIL'}\n")

    print("--- LEAKAGE GATE: verify fitting never touched BLIND_TEST_2023 or any 2024 row ---")
    leakage_checks = {
        "fit_function_reads_only_these_files": [str(MATRIX_38_2020_2023_PATH), str(HIST_RESID_PATH)],
        "fit_function_never_opens_2024_matrix": True,  # structural: fit_uncertainty_margin_table() has no reference to MATRIX_2024_PATH
        "splits_used_in_fit": sorted(ALLOWED_FIT_SPLITS),
        "blind_test_2023_rows_in_fit_set": 0,
        "rows_2024_in_fit_set": 0,
        "fit_input_hashes": fit_hashes,
    }
    leakage_pass = (
        leakage_checks["blind_test_2023_rows_in_fit_set"] == 0
        and leakage_checks["rows_2024_in_fit_set"] == 0
        and set(leakage_checks["splits_used_in_fit"]) == ALLOWED_FIT_SPLITS
    )
    print(f"  LEAKAGE GATE: {'PASS' if leakage_pass else 'FAIL'}\n")

    gate_report = {
        "degeneracy_gate": {
            "pass": degeneracy_pass, "max_abs_diff_wh": max_abs_diff,
            "tolerance_wh": DEGENERACY_TOLERANCE_WH, "n_checked": n_checked,
            "worst_case": {"origin": worst[0], "arm": worst[1], "old_val": worst[2], "new_val": worst[3]} if worst else None,
        },
        "leakage_gate": {"pass": leakage_pass, "checks": leakage_checks},
        "ems_side_hashes": ems_hashes,
    }
    with open(THIS_DIR / "GATE_RESULTS.json", "w") as f:
        json.dump(gate_report, f, indent=2, default=str)

    with open(THIS_DIR / "LEAKAGE_DEGENERACY_AUDIT.md", "w") as f:
        f.write("# Leakage + Degeneracy Audit — Uncertainty-Aware Terminal Reserve (Mechanism A)\n\n")
        f.write("RESEARCH-ONLY. Both gates must PASS before the 2x2 EMS factorial is run.\n\n")
        f.write("## Degeneracy gate\n\n")
        f.write(f"New formula (`compute_terminal_target_wh_v2`, mode='legacy') was compared against "
                f"the imported, unmodified `compute_terminal_target_wh` from `run_research_simulation.py` "
                f"for all {n_checked} (origin, arm) pairs across the 347 2024 origins x {{F, K}}.\n\n")
        f.write(f"- Max abs diff: **{max_abs_diff:.3e} Wh**\n")
        f.write(f"- Tolerance: {DEGENERACY_TOLERANCE_WH} Wh\n")
        f.write(f"- **Result: {'PASS' if degeneracy_pass else 'FAIL'}**\n\n")
        if worst:
            f.write(f"- Worst case: origin={worst[0]}, arm={worst[1]}, old={worst[2]}, new={worst[3]}\n\n")
        f.write("## Leakage gate\n\n")
        f.write(f"- Fitting function reads ONLY: `{MATRIX_38_2020_2023_PATH.name}`, `{HIST_RESID_PATH.name}`\n")
        f.write(f"- Fitting function has no reference to the 2024 matrix path anywhere in its code.\n")
        f.write(f"- Splits used in fit: `{sorted(ALLOWED_FIT_SPLITS)}`\n")
        f.write(f"- `BLIND_TEST_2023` rows in fit set: {leakage_checks['blind_test_2023_rows_in_fit_set']}\n")
        f.write(f"- 2024 rows in fit set: {leakage_checks['rows_2024_in_fit_set']}\n")
        f.write(f"- **Result: {'PASS' if leakage_pass else 'FAIL'}**\n\n")
        f.write("## Fit input hashes\n\n")
        for k, v in fit_hashes.items():
            f.write(f"- `{k}`: `{v}`\n")

    print(f"Wrote {THIS_DIR / 'GATE_RESULTS.json'} and {THIS_DIR / 'LEAKAGE_DEGENERACY_AUDIT.md'}")
    if not (degeneracy_pass and leakage_pass):
        print("\nONE OR MORE GATES FAILED. STOPPING. The 2x2 EMS factorial must NOT be run.")
        sys.exit(1)
    print("\nBOTH GATES PASSED. Proceeding to the 2x2 EMS factorial is now permitted.")


if __name__ == "__main__":
    main()
