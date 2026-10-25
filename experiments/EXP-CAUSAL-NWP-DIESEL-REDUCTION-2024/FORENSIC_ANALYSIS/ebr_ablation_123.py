"""
Research-only 123-origin EBR-OFF diagnostic, Arm B only.

Same harness as ebr_ablation.py: the ONLY change is config["ebr_target_wh"] = 0.0.
Baseline B (governed EBR formula) and EBR-OFF B are both run for every origin, in worker processes,
with identical code, inputs, and initial state. Optimizer failures are caught and counted, not hidden.

Not measured here: realized critical vs non-critical unmet. The frozen executor serves
min(demand, supply) with no critical priority, and the critical rule is defined only on forecast demand,
so that split has no definition in the frozen code. See the report.
"""
import copy
import importlib.util
import json
import math
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
HERE = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"
OUT = HERE / "ebr_ablation_123"
OUT.mkdir(parents=True, exist_ok=True)

FROZEN = json.load(open("experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))
WEATHER = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")

_tr = None
_base_cfg = None
_abl_cfg = None


def _init():
    global _tr, _base_cfg, _abl_cfg
    spec = importlib.util.spec_from_file_location("trace", HERE / "trace_hourly.py")
    _tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_tr)
    _base_cfg = _tr.camp.load_canonical_configs()
    _abl_cfg = copy.deepcopy(_base_cfg)
    _abl_cfg["ebr_target_wh"] = 0.0
    assert "ebr_target_wh" not in _base_cfg
    diff = sorted(k for k in set(_base_cfg) | set(_abl_cfg) if _base_cfg.get(k) != _abl_cfg.get(k))
    assert diff == ["ebr_target_wh"], diff
    assert _abl_cfg["terminal_target_wh"] == _base_cfg["terminal_target_wh"] == 100000.0


def run_arm(cfg, ebr_override, fs, t0):
    sub = WEATHER[WEATHER["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    _tr.EBR_OVERRIDE = ebr_override
    try:
        rep, steps = _tr.trace_arm("B", None, fs, t0, WEATHER, (rs, rw, rd, rts), cfg)
        recs = _tr.build_records("B", rep, steps, rs)
    finally:
        _tr.EBR_OVERRIDE = None
    return rep, recs, sum(sub_d for sub_d in rd), sum(rd)


def summarize(rep, recs, demand_total):
    on = sum(1 for r in recs if r["realized_diesel_w"] > 0.0)
    starts, was = 0, False
    for r in recs:
        cur = r["realized_diesel_w"] > 0.0
        if cur and not was:
            starts += 1
        was = cur
    soc = [r["realized_soc_pct"] for r in recs]
    served = rep.cumulative_served_load_wh
    unmet = rep.cumulative_unmet_load_wh
    return {
        "fuel_l": round(rep.cumulative_diesel_fuel_l, 4),
        "on_hours": on,
        "startups": starts,
        "curtail_wh": round(rep.cumulative_curtailment_wh, 2),
        "unmet_wh": round(unmet, 2),
        "served_wh": round(served, 2),
        "reliability_pct": round(100.0 * served / (served + unmet), 4) if (served + unmet) > 0 else None,
        "min_soc_pct": round(min(soc), 4),
        "max_soc_pct": round(max(soc), 4),
        "terminal_soc_pct_realized_h24": round(soc[-1], 4),
        "soc_floor_violations": sum(1 for s in soc if s < 19.999),
        "soc_ceiling_violations": sum(1 for s in soc if s > 95.001),
        "planned_terminal_shortfall_steps": sum(1 for r in recs if r["terminal_shortfall_t23_wh"] > 1e-3),
        "planned_terminal_tight_steps": sum(1 for r in recs if abs(r["terminal_margin_t23_wh"]) < 100),
        "planned_J1_critical_positive_steps": sum(1 for r in recs if r["j1_critical_unmet"] > 1e-3),
        "planned_J2_shortfall_steps": sum(1 for r in recs if r["j2_shortfall_t0_wh"] > 1e-3),
        "reserve_tight_steps": sum(1 for r in recs if r["reserve_margin_min_wh"] < 100),
        "same_hour_discharge_curtail_wh": round(sum(r["realized_curtailment_w"] for r in recs
                                                     if r["curtailment_cause"] == "same_hour_discharge"), 2),
        "step0_plan_diesel_w": recs[0]["plan_diesel_t0_w"],
        "demand_total_wh": round(demand_total, 2),
    }


def work(item):
    fr = item
    fs, t0, oi = fr["forecast_start"], fr["t0_timestamp"], fr["origin_index"]
    rep0, rec0, _, dt0 = run_arm(_base_cfg, None, fs, t0)
    try:
        rep1, rec1, _, dt1 = run_arm(_abl_cfg, 0.0, fs, t0)
        status = "OK"
        abl = summarize(rep1, rec1, dt1)
    except RuntimeError as e:
        status = f"OPTIMIZER_OR_SAFETY_FAILURE: {e}"
        abl = None
        rec1 = None
    base = summarize(rep0, rec0, dt0)
    frozenB = fr["arms"]["ARM_B_CANDIDATE"]
    reproduced = abs(base["fuel_l"] - frozenB["diesel_fuel_liters"]) < 1e-3 \
        and abs(base["unmet_wh"] - frozenB["unmet_critical_load_wh"]) < 1e-2 \
        and abs(base["curtail_wh"] - frozenB["curtailment_wh"]) < 1e-2
    out = {"origin_index": oi, "forecast_start": fs, "reproduced_frozen_B": reproduced,
           "frozen_B": {"fuel_l": frozenB["diesel_fuel_liters"], "unmet_wh": frozenB["unmet_critical_load_wh"],
                        "curtail_wh": frozenB["curtailment_wh"]},
           "base": base, "ablated": abl, "ablated_status": status}
    (OUT / f"origin_{oi:03d}.json").write_text(json.dumps(out))
    return out


if __name__ == "__main__":
    with Pool(processes=4, initializer=_init) as pool:
        results = []
        for i, r in enumerate(pool.imap_unordered(work, FROZEN, chunksize=1), 1):
            results.append(r)
            if i % 10 == 0 or i == len(FROZEN):
                print(f"{i}/{len(FROZEN)} done", flush=True)
    results.sort(key=lambda r: r["origin_index"])
    (OUT / "all_results.json").write_text(json.dumps(results))
    print("DONE", flush=True)
