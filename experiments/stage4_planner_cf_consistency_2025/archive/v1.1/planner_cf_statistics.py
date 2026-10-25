"""
Planner-CF v1 statistics and result reports (EXP-PLANNER-CF-CONSISTENCY-2025, §5, §10, §11).

Pure functions over the campaign telemetry. No solve, no realization, no file writes except via
the explicit report writer.

  S1  dR_CF = R_CF(candidate) - R_CF(PC-Control) >= 0.00 pp            (aggregate, 123 origins)
  S2  dR_P  = R_P(candidate)  - R_P(PC-Control)  >= 0.00 pp            (aggregate, 123 origins)
  S3  zero candidate hours with realized SOC < 20.00 %
  E1  two-sided paired Wilcoxon on Delta_o = Fuel(PC-Control,o) - Fuel(candidate,o),
      Holm across the four candidate tests (PC-S, PC-SW, PC-S-L, PC-SW-L), adj p < 0.05,
      AND BCa 95% lower bound > 0.0 L/origin (10,000 resamples, random_state = default_rng(42)).
      E1 is evaluated only if S1-S3 pass.
  T40 report-only: (Fuel(PC-Control) - Fuel(candidate)) / Fuel(PC-Control) >= 40.0 %.
  Winner: highest diesel saving among candidates passing S1-S3 and E1.
  D1  PC-Control vs old Control; D2 PC-S vs old S; D3 PC-S - PC-Control and PC-SW-L - PC-Control.
  Accounting alternative (reported, not decision-bearing): MILP-objective fuel = accounted fuel + 2.0 L x starts.

Reliability definitions match the corrected reproduction: R_CF = 100 * sum(served_crit_first) /
sum(critical_demand); R_P = 100 * sum(served_crit_prop) / sum(critical_demand).
"""

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd
import scipy.stats as stats

CANDIDATES = ("PC-S", "PC-SW", "PC-S-L", "PC-SW-L")
CONTROL = "PC-Control"
SOC_FLOOR_PCT = 20.00
BCA_RESAMPLES = 10000
ALPHA = 0.05
TARGET_SAVING_PCT = 40.0
STARTUP_OBJECTIVE_L = 2.0


def arm_rows(df: pd.DataFrame, arm: str) -> pd.DataFrame:
    sub = df[df["arm"] == arm].sort_values(["origin_id", "hour"]).reset_index(drop=True)
    return sub


def origin_fuel(df: pd.DataFrame, arm: str) -> pd.Series:
    """Fuel (L) per origin, sorted ascending by origin id (preregistered pairing)."""
    return arm_rows(df, arm).groupby("origin_id")["diesel_fuel"].sum().sort_index()


def origin_startups(df: pd.DataFrame, arm: str) -> pd.Series:
    rows = arm_rows(df, arm)
    out = {}
    for oid, g in rows.groupby("origin_id"):
        on = (g["diesel_power"].to_numpy() > 1e-3).astype(int)
        prev = np.concatenate(([0], on[:-1]))
        out[oid] = int(np.sum((on == 1) & (prev == 0)))
    return pd.Series(out).sort_index()


def origin_reliability(df: pd.DataFrame, arm: str) -> pd.DataFrame:
    """Per-origin R_CF and R_P in percent."""
    rows = arm_rows(df, arm)
    g = rows.groupby("origin_id")
    crit = g["critical_demand"].sum()
    r_cf = 100.0 * g["critical_served_first"].sum() / crit
    r_p = 100.0 * g["critical_served_prop"].sum() / crit
    return pd.DataFrame({"r_cf": r_cf, "r_p": r_p}).sort_index()


def aggregate_reliability(df: pd.DataFrame, arm: str) -> Tuple[float, float]:
    rows = arm_rows(df, arm)
    crit = rows["critical_demand"].sum()
    return (100.0 * rows["critical_served_first"].sum() / crit,
            100.0 * rows["critical_served_prop"].sum() / crit)


def safety_gates(df: pd.DataFrame, cand: str) -> Dict[str, Any]:
    """S1, S2, S3 for one candidate against PC-Control, using aggregate reliability."""
    cf_c, p_c = aggregate_reliability(df, cand)
    cf_b, p_b = aggregate_reliability(df, CONTROL)
    d_cf = cf_c - cf_b
    d_p = p_c - p_b
    rows = arm_rows(df, cand)
    soc_viol = int((rows["soc_after"] < SOC_FLOOR_PCT).sum())
    return {
        "arm": cand,
        "dR_CF_pp": d_cf, "S1_PASS": bool(d_cf >= 0.0),
        "dR_P_pp": d_p, "S2_PASS": bool(d_p >= 0.0),
        "soc_violations_below_20": soc_viol, "S3_PASS": bool(soc_viol == 0),
        "min_soc_pct": float(rows["soc_after"].min()),
    }


def holm_adjust(pvals: Sequence[float]) -> List[float]:
    """Holm step-down adjusted p-values, returned in the input order."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * p[idx])
        running = max(running, val)
        adj[idx] = running
    return adj.tolist()


def bca_lower_mean(values: Sequence[float]) -> Tuple[float, float]:
    """BCa 95% CI of the mean. Preregistered call: scipy bootstrap, BCa, 10,000 resamples, seed 42."""
    data = np.asarray(values, dtype=float)
    res = stats.bootstrap((data,), np.mean, method="BCa", confidence_level=0.95,
                          n_resamples=BCA_RESAMPLES, random_state=np.random.default_rng(42))
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def paired_wilcoxon_p(values: Sequence[float]) -> float:
    return float(stats.wilcoxon(np.asarray(values, dtype=float), alternative="two-sided").pvalue)


def e1_tests(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Diesel gate statistics for all four candidates, Holm-adjusted across the four tests."""
    control = origin_fuel(df, CONTROL)
    raw: Dict[str, Dict[str, Any]] = {}
    for cand in CANDIDATES:
        fuel_c = origin_fuel(df, cand)
        if list(fuel_c.index) != list(control.index):
            raise ValueError(f"origin pairing mismatch for {cand}")
        delta = (control - fuel_c).to_numpy()
        lo, hi = bca_lower_mean(delta)
        raw[cand] = {"delta_L_per_origin": delta.tolist(), "mean_delta_L": float(delta.mean()),
                     "wilcoxon_p": paired_wilcoxon_p(delta), "bca_low": lo, "bca_high": hi}
    adj = holm_adjust([raw[c]["wilcoxon_p"] for c in CANDIDATES])
    for cand, a in zip(CANDIDATES, adj):
        raw[cand]["holm_adj_p"] = a
        raw[cand]["E1_STAT_PASS"] = bool(a < ALPHA and raw[cand]["bca_low"] > 0.0)
    return raw


def evaluate(df: pd.DataFrame) -> Dict[str, Any]:
    """Full decision evaluation: S1-S3, E1 (only if S1-S3 pass), T40 report, winner."""
    control_fuel = float(origin_fuel(df, CONTROL).sum())
    e1 = e1_tests(df)
    out: Dict[str, Any] = {"control_fuel_L": control_fuel, "candidates": {}}
    eligible = []
    for cand in CANDIDATES:
        s = safety_gates(df, cand)
        fuel = float(origin_fuel(df, cand).sum())
        saving_pct = 100.0 * (control_fuel - fuel) / control_fuel
        safety_ok = s["S1_PASS"] and s["S2_PASS"] and s["S3_PASS"]
        e1_ok = bool(safety_ok and e1[cand]["E1_STAT_PASS"])
        if e1_ok:
            eligible.append((cand, control_fuel - fuel))
        out["candidates"][cand] = {
            **s,
            "fuel_L": fuel, "saving_pct": saving_pct,
            "E1": {k: v for k, v in e1[cand].items() if k != "delta_L_per_origin"},
            "E1_EVALUATED": bool(safety_ok),
            "E1_PASS": e1_ok,
            "T40_REPORT": bool(saving_pct >= TARGET_SAVING_PCT),
            "startups": int(origin_startups(df, cand).sum()),
            "accounting_alt_fuel_L": fuel + STARTUP_OBJECTIVE_L * int(origin_startups(df, cand).sum()),
        }
    out["winner"] = max(eligible, key=lambda kv: kv[1])[0] if eligible else None
    out["control_accounting_alt_fuel_L"] = control_fuel + STARTUP_OBJECTIVE_L * int(origin_startups(df, CONTROL).sum())
    return out


def paired_difference(a: np.ndarray, b: np.ndarray) -> Dict[str, Any]:
    d = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    lo, hi = bca_lower_mean(d)
    return {"n": int(len(d)), "mean_diff": float(d.mean()), "bca_low": lo, "bca_high": hi}


def d_comparisons(df: pd.DataFrame, corrected_results: pd.DataFrame) -> Dict[str, Any]:
    """D1-D3 deterministic comparisons, paired by origin (descriptive, not gates)."""
    corr = corrected_results.sort_values("origin_id").reset_index(drop=True)
    out: Dict[str, Any] = {}

    def block(label: str, arm: str, fuel_old: str, cf_old: str, p_old: str) -> Dict[str, Any]:
        rel = origin_reliability(df, arm)
        fuel = origin_fuel(df, arm).to_numpy()
        return {
            "fuel_L": paired_difference(fuel, corr[fuel_old].to_numpy()),
            "R_CF_pct": paired_difference(rel["r_cf"].to_numpy(), corr[cf_old].to_numpy()),
            "R_P_pct": paired_difference(rel["r_p"].to_numpy(), corr[p_old].to_numpy()),
        }

    out["D1_PC-Control_minus_old_Control"] = block("D1", CONTROL, "control_b_fuel_l", "control_b_r_cf", "control_b_r_p")
    out["D2_PC-S_minus_old_S"] = block("D2", "PC-S", "candidate_s_fuel_l", "candidate_s_r_cf", "candidate_s_r_p")

    def arm_vs_ctrl(arm: str) -> Dict[str, Any]:
        fa = origin_fuel(df, arm).to_numpy()
        fb = origin_fuel(df, CONTROL).to_numpy()
        ra = origin_reliability(df, arm)
        rb = origin_reliability(df, CONTROL)
        return {
            "fuel_L": paired_difference(fa, fb),
            "R_CF_pct": paired_difference(ra["r_cf"].to_numpy(), rb["r_cf"].to_numpy()),
            "R_P_pct": paired_difference(ra["r_p"].to_numpy(), rb["r_p"].to_numpy()),
        }

    out["D3_PC-S_minus_PC-Control"] = arm_vs_ctrl("PC-S")
    out["D3_PC-SW-L_minus_PC-Control"] = arm_vs_ctrl("PC-SW-L")
    return out


def write_summary_markdown(result: Dict[str, Any], path) -> None:
    lines = ["# Planner-CF v1 Result Report (generated)", "",
             f"Control fuel (L): {result['control_fuel_L']:.4f}", f"Winner: {result['winner']}", "",
             "| Arm | dR_CF pp | S1 | dR_P pp | S2 | SOC<20 hrs | S3 | Fuel L | Saving % | E1 eval | E1 pass | T40 (report) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for cand, c in result["candidates"].items():
        lines.append(
            f"| {cand} | {c['dR_CF_pp']:.6f} | {c['S1_PASS']} | {c['dR_P_pp']:.6f} | {c['S2_PASS']} | "
            f"{c['soc_violations_below_20']} | {c['S3_PASS']} | {c['fuel_L']:.4f} | {c['saving_pct']:.4f} | "
            f"{c['E1_EVALUATED']} | {c['E1_PASS']} | {c['T40_REPORT']} |")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
