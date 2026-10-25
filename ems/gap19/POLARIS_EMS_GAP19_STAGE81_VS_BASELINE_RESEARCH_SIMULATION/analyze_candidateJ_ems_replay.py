#!/usr/bin/env python3
"""
CANDIDATE J EMS REPLAY -- ANALYSIS. RESEARCH-ONLY. Pure post-hoc analysis of the raw results
already written by run_candidateJ_actual_solar_replay.py (Candidate J arm) and the existing
CANDIDATE_F_EMS_REPLAY_RESULTS.json (frozen Stage 8.1 control + Candidate F arms, NOT re-run).
No .fit(), no GAP19 call, no model load here -- this script only reads two already-written
JSON files and computes aggregates / per-origin comparisons / a corrected bootstrap CI.
"""
import json
import hashlib
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).parent

F_REPLAY_PATH = THIS_DIR / "CANDIDATE_F_EMS_REPLAY_RESULTS.json"
J_REPLAY_PATH = THIS_DIR / "CANDIDATE_J_EMS_REPLAY_RESULTS.json"

TIE_EPS_WH = 1e-3  # 1 milli-Wh; matches the F report's own "(+-1 mWh)" tie convention


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def bootstrap_paired_diff_ci_corrected(origin_list, values_a, values_b, n_boot=2000, seed=42):
    """Origin-level paired bootstrap for a per-origin scalar difference (a - b), CORRECTED
    convention (adapted from research_utils.bootstrap_mae_diff_ci_corrected): each origin is
    ONE row here (already an aggregate per origin, unlike the MAE utility's ~24 rows/origin),
    so resampling origins with replacement via rng.randint directly IS the correct per-draw
    duplication (an origin drawn k times contributes its single value k times to the sum) --
    no row-index pool is needed since there is exactly one row per origin already."""
    rng = np.random.RandomState(seed)
    origins = np.asarray(origin_list)
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    n = len(origins)
    diffs = []
    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        diffs.append(float(np.sum(a[idx]) - np.sum(b[idx])))
    diffs = np.array(diffs)
    return {
        "point_estimate_sum_diff": round(float(np.sum(a) - np.sum(b)), 4),
        "mean_diff": round(float(diffs.mean()), 4),
        "ci95_lo": round(float(np.percentile(diffs, 2.5)), 4),
        "ci95_hi": round(float(np.percentile(diffs, 97.5)), 4),
        "n_boot": int(len(diffs)),
        "method": "corrected_origin_level_paired_bootstrap_sum_diff",
    }


def main():
    f_hash_before = sha256_of(F_REPLAY_PATH)
    j_hash_before = sha256_of(J_REPLAY_PATH)

    with open(F_REPLAY_PATH) as f:
        f_data = json.load(f)
    with open(J_REPLAY_PATH) as f:
        j_data = json.load(f)

    f_results = f_data["results"]
    j_results = j_data["results"]

    normal_origins = sorted(
        o for o, v in f_results.items()
        if v.get("stage81_frozen", {}).get("route") == "NORMAL"
        and v.get("candidate_F", {}).get("route") == "NORMAL"
    )
    assert len(normal_origins) == 245, f"STOP: expected 245 NORMAL origins, got {len(normal_origins)}"
    for o in normal_origins:
        assert j_results.get(o, {}).get("candidate_J", {}).get("route") == "NORMAL", \
            f"STOP: origin {o} is NORMAL for control/F but not for Candidate J -- arms not aligned."
    print(f"Confirmed {len(normal_origins)} NORMAL origins identical across all three arms (control, F, J).\n")

    # --- Per-origin pull: realized unmet (Wh), SOC violations, diesel L, curtailment Wh ---
    rows = {"stage81_frozen": [], "candidate_F": [], "candidate_J": []}
    for o in normal_origins:
        stage81 = f_results[o]["stage81_frozen"]["replay"]
        cand_f = f_results[o]["candidate_F"]["replay"]
        cand_j = j_results[o]["candidate_J"]["replay"]
        for label, r in [("stage81_frozen", stage81), ("candidate_F", cand_f), ("candidate_J", cand_j)]:
            rows[label].append({
                "origin": o,
                "unmet_wh": r["realized_unmet_load_energy_wh"],
                "soc_violations": len(r["soc_violations"]),
                "diesel_l": r["realized_diesel_fuel_l"],
                "curtailment_wh": r["realized_curtailment_energy_wh"],
                "charge_wh": r["realized_battery_charge_energy_wh"],
                "discharge_wh": r["realized_battery_discharge_energy_wh"],
            })

    def agg(label, field):
        return sum(r[field] for r in rows[label])

    def planned_agg(label, field, source):
        return sum(source[o][label]["planned"][field] for o in normal_origins)

    agg_results = {}
    for label, source in [("stage81_frozen", f_results), ("candidate_F", f_results), ("candidate_J", j_results)]:
        unmet_sum = round(agg(label, "unmet_wh"), 1)
        soc_v = sum(r["soc_violations"] for r in rows[label])
        diesel_sum = round(agg(label, "diesel_l"), 4)
        curt_sum = round(agg(label, "curtailment_wh"), 1)
        charge_sum = round(agg(label, "charge_wh"), 1)
        discharge_sum = round(agg(label, "discharge_wh"), 1)
        n_nonzero_unmet = sum(1 for r in rows[label] if r["unmet_wh"] > 1e-6)
        planned_curt = round(planned_agg(label, "planned_curtailment_wh", source), 1)
        planned_charge = round(planned_agg(label, "planned_battery_charge_wh", source), 1)
        planned_discharge = round(planned_agg(label, "planned_battery_discharge_wh", source), 1)
        planned_diesel = round(planned_agg(label, "planned_diesel_fuel_l", source), 4)
        agg_results[label] = {
            "n": len(normal_origins),
            "planned_diesel_fuel_l": planned_diesel,
            "realized_diesel_fuel_l": diesel_sum,
            "planned_curtailment_wh": planned_curt,
            "realized_curtailment_wh": curt_sum,
            "realized_critical_load_unmet_wh": unmet_sum,
            "planned_battery_charge_wh": planned_charge,
            "realized_battery_charge_wh": charge_sum,
            "planned_battery_discharge_wh": planned_discharge,
            "realized_battery_discharge_wh": discharge_sum,
            "soc_violations": soc_v,
            "origins_with_nonzero_realized_unmet": n_nonzero_unmet,
        }

    print("=== Aggregate (245 NORMAL origins) ===")
    for label, a in agg_results.items():
        print(f"  {label}: unmet={a['realized_critical_load_unmet_wh']} Wh  "
              f"diesel={a['realized_diesel_fuel_l']} L  soc_viol={a['soc_violations']}  "
              f"curtailment={a['realized_curtailment_wh']} Wh")

    diff_jf = round(agg_results["candidate_J"]["realized_critical_load_unmet_wh"] -
                     agg_results["candidate_F"]["realized_critical_load_unmet_wh"], 1)
    diff_jc = round(agg_results["candidate_J"]["realized_critical_load_unmet_wh"] -
                     agg_results["stage81_frozen"]["realized_critical_load_unmet_wh"], 1)
    pct_jf = round(100 * diff_jf / agg_results["candidate_F"]["realized_critical_load_unmet_wh"], 4)
    pct_jc = round(100 * diff_jc / agg_results["stage81_frozen"]["realized_critical_load_unmet_wh"], 4)
    print(f"\nJ - F unmet diff: {diff_jf} Wh ({pct_jf}%)")
    print(f"J - control unmet diff: {diff_jc} Wh ({pct_jc}%)")

    diesel_diff_jf = round(agg_results["candidate_J"]["realized_diesel_fuel_l"] -
                            agg_results["candidate_F"]["realized_diesel_fuel_l"], 4)
    diesel_diff_jc = round(agg_results["candidate_J"]["realized_diesel_fuel_l"] -
                            agg_results["stage81_frozen"]["realized_diesel_fuel_l"], 4)

    # --- Per-origin win/tie/regression: J vs F, J vs control (on realized unmet) ---
    unmet_by = {label: {r["origin"]: r["unmet_wh"] for r in rows[label]} for label in rows}

    def classify(diffs):
        wins = sum(1 for d in diffs if d < -TIE_EPS_WH)
        regressions = sum(1 for d in diffs if d > TIE_EPS_WH)
        ties = sum(1 for d in diffs if abs(d) <= TIE_EPS_WH)
        return wins, ties, regressions

    diffs_jf = [unmet_by["candidate_J"][o] - unmet_by["candidate_F"][o] for o in normal_origins]
    diffs_jc = [unmet_by["candidate_J"][o] - unmet_by["stage81_frozen"][o] for o in normal_origins]
    wins_jf, ties_jf, regress_jf = classify(diffs_jf)
    wins_jc, ties_jc, regress_jc = classify(diffs_jc)

    print(f"\n=== J vs F per-origin (unmet Wh, tie eps={TIE_EPS_WH}) ===")
    print(f"  wins(J<F)={wins_jf}  ties={ties_jf}  regressions(J>F)={regress_jf}")
    print(f"=== J vs control per-origin ===")
    print(f"  wins(J<control)={wins_jc}  ties={ties_jc}  regressions(J>control)={regress_jc}")

    # Largest single-origin swings
    idx_sorted_jf = sorted(range(len(normal_origins)), key=lambda i: diffs_jf[i])
    largest_improve_jf = (normal_origins[idx_sorted_jf[0]], diffs_jf[idx_sorted_jf[0]])
    largest_regress_jf = (normal_origins[idx_sorted_jf[-1]], diffs_jf[idx_sorted_jf[-1]])
    print(f"  Largest J improvement vs F: {largest_improve_jf}")
    print(f"  Largest J regression vs F: {largest_regress_jf}")

    # Regression origins -- month distribution, for mechanistic characterization
    def month_of(origin_str):
        return origin_str[5:7]

    regress_origins_jf = [o for o, d in zip(normal_origins, diffs_jf) if d > TIE_EPS_WH]
    month_counts_regress = {}
    for o in regress_origins_jf:
        m = month_of(o)
        month_counts_regress[m] = month_counts_regress.get(m, 0) + 1
    all_month_counts = {}
    for o in normal_origins:
        m = month_of(o)
        all_month_counts[m] = all_month_counts.get(m, 0) + 1
    print(f"\n  Regression-origin (J vs F) month distribution: {sorted(month_counts_regress.items())}")
    print(f"  All-origin month distribution: {sorted(all_month_counts.items())}")

    # --- Corrected bootstrap 95% CI for aggregate realized-unmet diff ---
    boot_jf = bootstrap_paired_diff_ci_corrected(
        normal_origins,
        [unmet_by["candidate_J"][o] for o in normal_origins],
        [unmet_by["candidate_F"][o] for o in normal_origins],
    )
    boot_jc = bootstrap_paired_diff_ci_corrected(
        normal_origins,
        [unmet_by["candidate_J"][o] for o in normal_origins],
        [unmet_by["stage81_frozen"][o] for o in normal_origins],
    )
    print(f"\n=== Bootstrap 95% CI (corrected, origin-level paired, n_boot=2000, seed=42) ===")
    print(f"  (J - F): {boot_jf}")
    print(f"  (J - control): {boot_jc}")

    ci_jf_excludes_zero = not (boot_jf["ci95_lo"] <= 0.0 <= boot_jf["ci95_hi"])
    ci_jc_excludes_zero = not (boot_jc["ci95_lo"] <= 0.0 <= boot_jc["ci95_hi"])
    print(f"\n  (J-F) CI excludes zero: {ci_jf_excludes_zero}")
    print(f"  (J-control) CI excludes zero: {ci_jc_excludes_zero}")

    f_hash_after = sha256_of(F_REPLAY_PATH)
    j_hash_after = sha256_of(J_REPLAY_PATH)
    assert f_hash_before == f_hash_after, "STOP: CANDIDATE_F_EMS_REPLAY_RESULTS.json changed during analysis."
    assert j_hash_before == j_hash_after, "STOP: CANDIDATE_J_EMS_REPLAY_RESULTS.json changed during analysis."

    out = {
        "disclaimer": (
            "CANDIDATE J EMS REPLAY ANALYSIS. RESEARCH-ONLY. Post-hoc analysis of two "
            "already-written raw-results files (CANDIDATE_F_EMS_REPLAY_RESULTS.json for "
            "control+F, CANDIDATE_J_EMS_REPLAY_RESULTS.json for J). No model load, no GAP19 "
            "call, no .fit() in this script."
        ),
        "normal_origins_n": len(normal_origins),
        "tie_epsilon_wh": TIE_EPS_WH,
        "aggregate": agg_results,
        "aggregate_diffs": {
            "unmet_wh_J_minus_F": diff_jf, "unmet_pct_J_minus_F": pct_jf,
            "unmet_wh_J_minus_control": diff_jc, "unmet_pct_J_minus_control": pct_jc,
            "diesel_l_J_minus_F": diesel_diff_jf, "diesel_l_J_minus_control": diesel_diff_jc,
        },
        "per_origin_win_tie_regression": {
            "J_vs_F": {"wins": wins_jf, "ties": ties_jf, "regressions": regress_jf,
                       "largest_improvement": largest_improve_jf, "largest_regression": largest_regress_jf,
                       "regression_month_distribution": month_counts_regress,
                       "all_origin_month_distribution": all_month_counts},
            "J_vs_control": {"wins": wins_jc, "ties": ties_jc, "regressions": regress_jc},
        },
        "bootstrap_95ci_realized_unmet_diff": {
            "J_minus_F": boot_jf, "J_minus_F_excludes_zero": ci_jf_excludes_zero,
            "J_minus_control": boot_jc, "J_minus_control_excludes_zero": ci_jc_excludes_zero,
        },
        "input_hashes": {
            "CANDIDATE_F_EMS_REPLAY_RESULTS.json": {"before": f_hash_before, "after": f_hash_after},
            "CANDIDATE_J_EMS_REPLAY_RESULTS.json": {"before": j_hash_before, "after": j_hash_after},
        },
    }
    out_path = THIS_DIR / "CANDIDATE_J_EMS_REPLAY_ANALYSIS.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nAnalysis written to {out_path}")


if __name__ == "__main__":
    main()
