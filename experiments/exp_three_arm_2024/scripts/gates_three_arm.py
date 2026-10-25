"""
Post-run gate evaluation for EXP-THREE-ARM-2024 (research only). Pure functions over hourly telemetry.

Implements only what config/EXPERIMENT_CONFIG.json `gates` records (decisions in DECISIONS_LOG.md and
reports/DECISION_RESOLUTION_2026-10-11.md):
  S1, S2, S3   recorded baseline gates (frozen planner_cf_statistics.safety_gates).
  S4 (D2)      point-estimate non-regression of total realized unmet energy:
               U(arm) = sum over the identical paired (origin, hour) cells of unmet_load_w x 1 h  [Wh];
               PASS iff U(arm) <= U(PC-Control); exact ties pass; no tolerance. Any missing, duplicate,
               unpaired, non-finite or non-optimal cell makes the comparison NOT EVALUABLE = FAIL.
  S4_strict    (D6) reported SEPARATELY from S4: stationary block bootstrap (Politis-Romano, circular,
               geometric block lengths) of the mean paired per-origin delta U = U_arm,o - U_ctrl,o over
               origins in chronological order; PASS iff the configured upper bound <= 0 Wh/origin.
  E1 (D10)     two-sided paired Wilcoxon on Delta_o = Fuel(PC-Control,o) - Fuel(arm,o) [L/origin],
               Holm across the CONFIGURED family only (family size fixed in advance, never shrunk),
               AND the preregistered iid BCa 95% (two-sided) lower bound > 0 for that arm. No CI
               multiplicity correction. E1 counts only if the arm's reliability gates pass.
  Primary fuel (D4): unadjusted realized diesel litres. The SoC-parity-adjusted analysis (PROTOCOL §7)
               is secondary, reported separately, and computed only if its configuration has a passing status
               (PASSING_STATUSES, same tuple as preflight.py). Applied per origin (M9, delegated technical
               authority): the PROTOCOL §7 formula is evaluated for each origin and the results are summed.
  Arm C coverage (PROTOCOL §4, M9): evaluation-window coverage of C's lower bound per calibration bin, computed
               AFTER the run from the hourly C rows; diagnostic only, never decision-bearing.
Any unresolved gate setting raises GateConfigError: nothing is evaluated with a guessed rule.

Arm B is NONCAUSAL and is never eligible. Nothing in this experiment is promotion-eligible; the output
carries `winner: None` by construction. A fuel reduction with any failed reliability gate is labelled
NOT AN IMPROVEMENT.
"""
import math
from typing import Any, Dict, List

import numpy as np
import pandas as pd

CONTROL = "PC-Control"
ELIGIBLE = ("A", "A_FIX", "C")
REPORTED_ARMS = ("A", "A_FIX", "B", "C")
PASSING_STATUSES = ("APPROVED", "APPROVED BY EXISTING AUTHORITY", "RESOLVED BY DELEGATED TECHNICAL AUTHORITY")
STRICT_INTERVALS = {"two_sided_95_upper": 97.5, "one_sided_95_upper": 95.0}
BOOTSTRAP_ALGORITHM = ("Politis-Romano stationary bootstrap, circular wrap-around, geometric block lengths "
                       "with mean = mean_block_days origins, numpy.random.default_rng(seed) (PCG64), "
                       "percentile interval of the resampled means")


class GateConfigError(RuntimeError):
    pass


def _require_resolved(g: Dict[str, Any]) -> None:
    if not isinstance(g.get("E1_holm_family"), list) or not g["E1_holm_family"]:
        raise GateConfigError("E1_holm_family unresolved (D10)")
    for a in g["E1_holm_family"]:
        if a not in ELIGIBLE:
            raise GateConfigError(f"{a} cannot be in the E1 family")
    if len(set(g["E1_holm_family"])) != len(g["E1_holm_family"]):
        raise GateConfigError("duplicate arm in E1 family")
    for k in ("S4", "S4_strict"):
        if g.get(k) not in ("ADOPTED", "NOT_ADOPTED"):
            raise GateConfigError(f"{k} unresolved")
    if g["S4_strict"] == "ADOPTED":
        if g.get("S4_strict_interval") not in STRICT_INTERVALS:
            raise GateConfigError("S4_strict_interval unresolved (D6)")
        if not isinstance(g.get("S4_strict_bootstrap_seed"), int):
            raise GateConfigError("S4_strict_bootstrap_seed unresolved (D6)")
    if g.get("primary_fuel_metric") != "unadjusted":
        raise GateConfigError("primary_fuel_metric must be 'unadjusted' (D4)")


# ---------------------------------------------------------------------------- pairing (D2)
def paired_cells(df: pd.DataFrame, arm: str, ref: str = CONTROL) -> Dict[str, Any]:
    """Returns {'valid': bool, 'problems': [...], 'arm': Series, 'ref': Series} with unmet Wh indexed by
    (origin_id, hour). Never drops a cell to make a comparison possible."""
    probs: List[str] = []
    out = {}
    for name in (arm, ref):
        sub = df[df["arm"] == name]
        if sub.empty:
            probs.append(f"{name}: no rows (failed or missing arm)")
            continue
        if sub.duplicated(["origin_id", "hour"]).any():
            probs.append(f"{name}: duplicate (origin, hour) cells")
        if not np.all(np.isfinite(sub["unmet_load"].to_numpy(dtype=float))):
            probs.append(f"{name}: non-finite unmet_load")
        if "solver_status" in sub.columns and not sub["solver_status"].isin(["OPTIMAL", "FEASIBLE"]).all():
            probs.append(f"{name}: non-optimal solver status")
        out[name] = sub.set_index(["origin_id", "hour"])["unmet_load"].astype(float).sort_index()
    if not probs:
        ka, kr = set(out[arm].index), set(out[ref].index)
        if ka != kr:
            probs.append(f"unpaired cells: {len(ka - kr)} only in {arm}, {len(kr - ka)} only in {ref}")
        hours = out[ref].index.get_level_values("hour")
        if set(hours) != set(range(24)) or out[ref].groupby(level="origin_id").size().ne(24).any():
            probs.append("every origin must have exactly hours 0..23")
    return {"valid": not probs, "problems": probs, "arm": out.get(arm), "ref": out.get(ref)}


def s4_point(df: pd.DataFrame, arm: str, ref: str = CONTROL) -> Dict[str, Any]:
    pc = paired_cells(df, arm, ref)
    if not pc["valid"]:
        return {"status": "NOT EVALUABLE", "problems": pc["problems"], "PASS": False}
    ua = math.fsum(pc["arm"].to_numpy())  # W over 1 h steps = Wh; fsum: exact, order-independent
    ur = math.fsum(pc["ref"].to_numpy())
    per_o = (pc["arm"].groupby(level="origin_id").apply(lambda s: math.fsum(s))
             - pc["ref"].groupby(level="origin_id").apply(lambda s: math.fsum(s))).sort_index()
    worst = per_o.sort_values(ascending=False).head(5)
    return {"status": "EVALUATED", "U_arm_Wh": ua, "U_ref_Wh": ur, "delta_Wh": ua - ur,
            "n_origins": int(per_o.size), "n_cells": int(pc["arm"].size),
            "origins_worse": int((per_o > 0).sum()), "origins_equal": int((per_o == 0).sum()),
            "origins_better": int((per_o < 0).sum()),
            "per_origin_delta_Wh": {"mean": float(per_o.mean()), "median": float(per_o.median()),
                                    "min": float(per_o.min()), "max": float(per_o.max())},
            "worst_5_origins": {int(k): float(v) for k, v in worst.items()},
            "rule": "U_arm <= U_ref (ties pass, no tolerance)", "PASS": bool(ua <= ur)}


def per_origin_delta_unmet(df: pd.DataFrame, arm: str, ref: str = CONTROL) -> pd.Series:
    pc = paired_cells(df, arm, ref)
    if not pc["valid"]:
        raise ValueError("; ".join(pc["problems"]))
    a = pc["arm"].groupby(level="origin_id").apply(lambda s: math.fsum(s))
    r = pc["ref"].groupby(level="origin_id").apply(lambda s: math.fsum(s))
    return (a - r).sort_index()  # origin_id ascending == chronological (runner numbers sorted origins 1..n)


# ---------------------------------------------------------------------------- bootstrap (D6)
def stationary_bootstrap_means(x: np.ndarray, mean_block: float, n_resamples: int, seed: int) -> np.ndarray:
    """Politis-Romano stationary bootstrap of the mean, vectorized.
    For each resample: position 0 starts a block; each later position starts a new block with
    probability p = 1/mean_block, otherwise continues the previous index + 1 (mod n). Block starts are
    uniform on 0..n-1. Draw order (fixed): starts = rng.integers(n, size=(B, n)); then
    u = rng.random((B, n))."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 2 or not np.all(np.isfinite(x)):
        raise ValueError("bootstrap needs >= 2 finite values")
    rng = np.random.default_rng(seed)
    p = 1.0 / float(mean_block)
    starts = rng.integers(n, size=(n_resamples, n))
    new = rng.random((n_resamples, n)) < p
    new[:, 0] = True
    t = np.arange(n)
    last = np.maximum.accumulate(np.where(new, t, 0), axis=1)          # position of the current block's start
    start_val = np.take_along_axis(starts, last, axis=1)
    idx = (start_val + (t - last)) % n
    return x[idx].mean(axis=1)


def s4_strict(df: pd.DataFrame, arm: str, g: Dict[str, Any]) -> Dict[str, Any]:
    try:
        du = per_origin_delta_unmet(df, arm).to_numpy()
    except ValueError as e:
        return {"status": "NOT EVALUABLE", "problems": [str(e)], "PASS": False}
    block, nres, seed = g["S4_strict_mean_block_days"]["value"], g["S4_strict_resamples"]["value"], g["S4_strict_bootstrap_seed"]
    means = stationary_bootstrap_means(du, block, nres, seed)
    q = STRICT_INTERVALS[g["S4_strict_interval"]]
    ub = float(np.percentile(means, q))
    return {"status": "EVALUATED", "mean_delta_U_Wh_per_origin": float(du.mean()),
            "upper_bound_Wh_per_origin": ub, "percentile": q, "interval": g["S4_strict_interval"],
            "bootstrap": {"algorithm": BOOTSTRAP_ALGORITHM, "seed": seed, "mean_block_days": block,
                          "resamples": nres, "numpy": np.__version__, "n_origins": int(du.size)},
            "rule": "upper bound of mean paired delta U <= 0", "PASS": bool(ub <= 0.0)}


# ---------------------------------------------------------------------------- fuel (D4)
def origin_end_energy_wh(df: pd.DataFrame, arm: str) -> pd.Series:
    sub = df[df["arm"] == arm].sort_values(["origin_id", "hour"])
    return sub.groupby("origin_id")["e_after_wh"].last().sort_index()


def secondary_soc_parity(df: pd.DataFrame, arm: str, g: Dict[str, Any], stat) -> Dict[str, Any]:
    """PROTOCOL §7: fuel + max(0, E_end,ctrl - E_end,arm) x (1/0.92) x f, f in {0.30, 0.75} L/kWh.
    Reported only; never decision-bearing; never overrides the primary metric or a reliability gate."""
    sec = g.get("soc_parity_secondary") or {}
    if sec.get("status") not in PASSING_STATUSES:
        return {"status": f"BLOCKED ({sec.get('status')!r}: secondary analysis not approved)"}
    if sec.get("application") != "per_origin":
        raise GateConfigError("soc_parity_secondary.application must be 'per_origin' when approved")
    gap_kwh = (origin_end_energy_wh(df, CONTROL) - origin_end_energy_wh(df, arm)).clip(lower=0.0) / 1000.0
    ctrl, fuel = stat.origin_fuel(df, CONTROL), stat.origin_fuel(df, arm)
    out = {"status": "REPORTED (secondary, not decision-bearing)", "protocol_text": sec.get("protocol_text_verbatim"),
           "applied_form": sec.get("per_origin_form"),
           "limitations": sec.get("limitations"),
           "mean_end_energy_gap_kwh": float(gap_kwh.mean()),
           "origins_arm_ends_lower": int((gap_kwh > 0).sum()), "by_f": {}}
    for f in sec["f_values_l_per_kwh"]:
        adj = fuel + gap_kwh * (1.0 / 0.92) * float(f)
        out["by_f"][f"{f:.2f}"] = {"adjusted_fuel_L": float(adj.sum()),
                                   "saving_pct_vs_control": 100.0 * float((ctrl.sum() - adj.sum()) / ctrl.sum()),
                                   "mean_saving_L_per_origin": float((ctrl - adj).mean())}
    return out


def arm_metrics(df: pd.DataFrame, arm: str, stat) -> Dict[str, Any]:
    sub = df[df["arm"] == arm]
    crit = float(sub["critical_demand"].sum())
    return {
        "fuel_L": float(sub["diesel_fuel"].sum()),
        "unmet_total_Wh": float(sub["unmet_load"].sum()),
        "critical_unmet_first_Wh": float((sub["critical_demand"] - sub["critical_served_first"]).sum()),
        "critical_unmet_prop_Wh": float((sub["critical_demand"] - sub["critical_served_prop"]).sum()),
        "noncritical_unmet_Wh": float(sub["unmet_load"].sum() - (sub["critical_demand"] - sub["critical_served_first"]).sum()),
        "R_CF_pct": 100.0 * float(sub["critical_served_first"].sum()) / crit,
        "R_P_pct": 100.0 * float(sub["critical_served_prop"].sum()) / crit,
        "hours_soc_below_20": int((sub["soc_after"] < 20.0).sum()),
        "min_soc_pct": float(sub["soc_after"].min()),
        "curtailment_Wh": float(sub["curtailment"].sum()),
        "diesel_on_hours": int((sub["diesel_power"] > 1e-3).sum()),
        "diesel_starts": int(stat.origin_startups(df, arm).sum()),
        "held_cloud_hours": int(sub["held_cloud_hours"].sum()),
        "optimizer_status_counts": sub["solver_status"].value_counts().to_dict(),
        # D7a §6 reporting items (M9): reserve slack, fuel exhaustion, final SoC. None if the column is absent.
        "j2_reserve_shortfall_Wh": float(sub["j2_shortfall_wh"].sum()) if "j2_shortfall_wh" in sub else None,
        "fuel_exhausted_hours": (int((sub["diesel_fuel_remaining_l"] <= 1e-9).sum())
                                 if "diesel_fuel_remaining_l" in sub else None),
        "final_soc_pct_mean": (float(sub.sort_values(["origin_id", "hour"]).groupby("origin_id")["soc_after"].last().mean())
                               if "hour" in sub else None),
    }


def evaluate(df: pd.DataFrame, cfg: Dict[str, Any], arm_configs: Dict[str, Dict[str, Any]], stat) -> Dict[str, Any]:
    import scipy.stats as sst
    g = cfg["gates"]
    _require_resolved(g)
    family: List[str] = list(g["E1_holm_family"])
    ctrl_fuel = stat.origin_fuel(df, CONTROL)
    ctrl_fuel_total = float(ctrl_fuel.sum())
    out: Dict[str, Any] = {"control": arm_metrics(df, CONTROL, stat), "arms": {}, "winner": None,
                           "winner_note": "No arm in EXP-THREE-ARM-2024 is promotion-eligible; a winner change needs a separate governance decision.",
                           "E1_family": family, "E1_family_size": len(family), "gates_config": g,
                           "primary_fuel_metric": "unadjusted realized diesel litres; saving = control - arm"}
    safety: Dict[str, bool] = {}
    for arm in REPORTED_ARMS:
        spec = arm_configs[arm]
        m = arm_metrics(df, arm, stat)
        s = stat.safety_gates(df, arm)
        rec: Dict[str, Any] = {"result_label": spec["result_label"], "causal": spec["causal"],
                               "promotion_eligible": False, "in_E1_family": arm in family, **m,
                               "saving_pct_vs_control": 100.0 * (ctrl_fuel_total - m["fuel_L"]) / ctrl_fuel_total,
                               "S1": {"dR_CF_pp": s["dR_CF_pp"], "PASS": s["S1_PASS"]},
                               "S2": {"dR_P_pp": s["dR_P_pp"], "PASS": s["S2_PASS"]},
                               "S3": {"violations": s["soc_violations_below_20"], "PASS": s["S3_PASS"]}}
        ok = s["S1_PASS"] and s["S2_PASS"] and s["S3_PASS"]
        if g["S4"] == "ADOPTED":
            rec["S4_point"] = s4_point(df, arm)
            ok = ok and rec["S4_point"]["PASS"]
            rec["S4_point_vs_A_reported"] = s4_point(df, arm, "A") if arm != "A" else None
        else:
            rec["S4_point"] = {"status": "NOT_ADOPTED (decision D2)"}
        if g["S4_strict"] == "ADOPTED":
            rec["S4_strict"] = s4_strict(df, arm, g)
            ok = ok and rec["S4_strict"]["PASS"]
        else:
            rec["S4_strict"] = {"status": "NOT_ADOPTED (decision D6)"}
        rec["secondary_soc_parity_fuel"] = secondary_soc_parity(df, arm, g, stat)
        safety[arm] = ok
        rec["reliability_gates_PASS"] = ok
        out["arms"][arm] = rec

    raw = {}
    for arm in family:
        fa = stat.origin_fuel(df, arm)
        if list(fa.index) != list(ctrl_fuel.index):
            raise ValueError(f"origin pairing mismatch for {arm}")
        delta = (ctrl_fuel - fa).to_numpy()
        lo, hi = stat.bca_lower_mean(delta)
        w = sst.wilcoxon(delta, alternative="two-sided")  # same call as the frozen paired_wilcoxon_p
        raw[arm] = {"mean_saving_L_per_origin": float(delta.mean()), "total_saving_L": float(delta.sum()),
                    "wilcoxon_statistic": float(w.statistic), "wilcoxon_p": stat.paired_wilcoxon_p(delta),
                    "bca95_low": lo, "bca95_high": hi}
    adj = stat.holm_adjust([raw[a]["wilcoxon_p"] for a in family])
    for arm, a in zip(family, adj):
        e1_stat = bool(a < 0.05 and raw[arm]["bca95_low"] > 0.0)
        out["arms"][arm]["E1"] = {**raw[arm], "holm_adj_p": a, "holm_family_size": len(family),
                                  "E1_STAT_PASS": e1_stat, "EVALUATED": safety[arm],
                                  "PASS": bool(safety[arm] and e1_stat)}
    for arm in REPORTED_ARMS:
        rec = out["arms"][arm]
        if arm == "B":
            rec["verdict"] = "NONCAUSAL DIAGNOSTIC — NOT DEPLOYABLE — NEVER ELIGIBLE"
        elif arm not in family:
            rec["verdict"] = "REPORTED ONLY (not in the E1 family)"
        elif not safety[arm]:
            rec["verdict"] = "NOT AN IMPROVEMENT (reliability gate failed or not evaluable)"
        elif rec["E1"]["PASS"]:
            rec["verdict"] = "GATES PASSED (research-only result; not promotion-eligible)"
        else:
            rec["verdict"] = "NOT AN IMPROVEMENT (E1 failed)"
    out["diagnostic_comparisons"] = {
        "A_vs_A_FIX": _paired(df, "A_FIX", "A", stat),
        "A_FIX_vs_C": _paired(df, "C", "A_FIX", stat),
    }
    out["arm_c_evaluation_coverage"] = arm_c_evaluation_coverage(df)
    if g["S4_strict"] == "ADOPTED":
        out["secondary_block_bootstrap_fuel"] = {
            arm: _block_ci((ctrl_fuel - stat.origin_fuel(df, arm)).to_numpy(), g) for arm in REPORTED_ARMS}
    return out


def _block_ci(x: np.ndarray, g: Dict[str, Any]) -> Dict[str, Any]:
    """Secondary (PROTOCOL §7): stationary block-bootstrap 95% CI for mean fuel saving. Not E1."""
    means = stationary_bootstrap_means(x, g["S4_strict_mean_block_days"]["value"], g["S4_strict_resamples"]["value"],
                                       g["S4_strict_bootstrap_seed"])
    return {"mean_saving_L_per_origin": float(np.mean(x)), "ci95_low": float(np.percentile(means, 2.5)),
            "ci95_high": float(np.percentile(means, 97.5)), "role": "secondary, not decision-bearing"}


def _paired(df: pd.DataFrame, arm: str, ref: str, stat) -> Dict[str, Any]:
    fa, fb = stat.origin_fuel(df, arm).to_numpy(), stat.origin_fuel(df, ref).to_numpy()
    ra, rb = stat.origin_reliability(df, arm), stat.origin_reliability(df, ref)
    ua = df[df["arm"] == arm].groupby("origin_id")["unmet_load"].sum().sort_index().to_numpy()
    ub = df[df["arm"] == ref].groupby("origin_id")["unmet_load"].sum().sort_index().to_numpy()
    return {"definition": f"{arm} minus {ref}, paired by origin (diagnostic, not confirmatory)",
            "fuel_L": stat.paired_difference(fa, fb),
            "unmet_Wh": stat.paired_difference(ua, ub),
            "R_CF_pct": stat.paired_difference(ra["r_cf"].to_numpy(), rb["r_cf"].to_numpy()),
            "R_P_pct": stat.paired_difference(ra["r_p"].to_numpy(), rb["r_p"].to_numpy())}


# ---------------------------------------------------------------------------- Arm C coverage (PROTOCOL §4)
C_COVERAGE_COLUMNS = ("c_daylight_h0", "c_elevation_bin_h0", "c_cloud_bin_h0", "c_lower_bound_h0", "c_actual_h0")


def arm_c_evaluation_coverage(df: pd.DataFrame, arm: str = "C") -> Dict[str, Any]:
    """Evaluation-window coverage of Arm C's lower bound, per calibration bin, computed after the run
    (PROTOCOL §4: 'Report calibration-window coverage only (in-sample) and evaluation-window coverage after the
    run, as a diagnostic'). One row per executed hour: the bound for that hour from the step's own forecast
    (horizon index 0) against the realized value in the same residual space. Daylight hours only.
    covered = actual >= lower bound. Nominal coverage is about 1 - alpha for an unclamped split-conformal bound;
    the clamp max(0, min(point, point + q)) can only lower the bound, so it can only raise coverage.
    Reported only; never decision-bearing; never used to change the calibration."""
    sub = df[df["arm"] == arm] if "arm" in df.columns else df.iloc[0:0]
    if sub.empty or any(c not in sub.columns for c in C_COVERAGE_COLUMNS):
        return {"status": "NOT AVAILABLE (no Arm C rows with coverage fields)"}
    d = sub[sub["c_daylight_h0"].astype(bool)]
    bins = []
    for (e, c), g in d.groupby(["c_elevation_bin_h0", "c_cloud_bin_h0"], sort=True):
        cov = (g["c_actual_h0"].astype(float) >= g["c_lower_bound_h0"].astype(float))
        bins.append({"elevation_bin": int(e), "cloud_bin": int(c), "n_hours": int(len(g)),
                     "origin_days": int(g["origin_id"].nunique()), "coverage": float(cov.mean())})
    allcov = (d["c_actual_h0"].astype(float) >= d["c_lower_bound_h0"].astype(float))
    return {"status": "REPORTED (diagnostic, never decision-bearing)",
            "definition": "share of daylight executed hours with realized value >= Arm C lower bound for that hour",
            "n_daylight_hours": int(len(d)), "overall_coverage": float(allcov.mean()) if len(d) else None,
            "by_bin": bins}
