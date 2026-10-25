"""
Research-layer realized load-class DIAGNOSTIC, Arm B, 123 origins. NOT a frozen campaign result.

Definition (research layer only):
    critical_realized = min(11600 W, realized_total_demand)     per hour
    When supply is insufficient, critical load is served first, then non-critical.

Why this is exact and does not change dispatch:
    The executor's battery, diesel, curtailment, and SOC updates depend only on total supply
    (solar + wind + diesel + battery discharge) and total demand, never on how served load is split.
    The critical-first split is an allocation of the SAME total served energy, so fuel, SOC,
    startups, curtailment and total unmet are identical to the frozen dynamics. Only the
    critical / non-critical split of unmet is new. The split is computed from the recorded
    per-hour realized quantities, not by modifying the executor.

Arms (both run in worker processes, same code and inputs):
    A = frozen Arm B (governed EBR formula)
    B = Arm B with config ebr_target_wh = 0.0 (EBR removed), terminal target unchanged
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
OUT = HERE / "ebr_loadclass_123"
OUT.mkdir(parents=True, exist_ok=True)

CRIT_CEIL_W = 11600.0
FROZEN = json.load(open("experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))
WEATHER = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")

_tr = None
_cfg = {}


def _init():
    global _tr
    spec = importlib.util.spec_from_file_location("trace", HERE / "trace_hourly.py")
    _tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_tr)
    base = _tr.camp.load_canonical_configs()
    abl = copy.deepcopy(base)
    abl["ebr_target_wh"] = 0.0
    assert "ebr_target_wh" not in base
    diff = sorted(k for k in set(base) | set(abl) if base.get(k) != abl.get(k))
    assert diff == ["ebr_target_wh"], diff
    assert abl["terminal_target_wh"] == base["terminal_target_wh"] == 100000.0
    _cfg["A"] = base
    _cfg["B"] = abl


def load_class_split(step_records):
    """Critical-first split of the SAME served energy the executor produced."""
    dc_tot = sn_tot = sc_tot = sn_served = uc = un = 0.0
    served_mismatch = 0.0
    for sr in step_records:
        D = sr.realized_demand_w
        S = sr.realized_solar_w + sr.realized_wind_w + sr.realized_diesel_w + sr.realized_battery_discharge_w
        Dc = min(CRIT_CEIL_W, D)
        Dn = D - Dc
        served_c = min(Dc, S)
        served_n = min(Dn, max(0.0, S - served_c))
        served_mismatch += abs((served_c + served_n) - sr.served_load_w)
        dc_tot += Dc
        sc_tot += served_c
        uc += Dc - served_c
        un += Dn - served_n
        sn_tot += Dn
        sn_served += served_n
    return {
        "critical_demand_wh": round(dc_tot, 2),
        "critical_served_wh": round(sc_tot, 2),
        "critical_unmet_wh": round(uc, 2),
        "noncritical_demand_wh": round(sn_tot, 2),
        "noncritical_served_wh": round(sn_served, 2),
        "noncritical_unmet_wh": round(un, 2),
        "split_served_vs_executor_abs_residual_wh": round(served_mismatch, 4),
    }


def run_arm(arm, fs, t0):
    sub = WEATHER[WEATHER["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    ebr_override = 0.0 if arm == "B" else None
    _tr.EBR_OVERRIDE = ebr_override
    try:
        rep, steps = _tr.trace_arm("B", None, fs, t0, WEATHER, (rs, rw, rd, rts), _cfg[arm])
        recs = _tr.build_records("B", rep, steps, rs)
    finally:
        _tr.EBR_OVERRIDE = None
    split = load_class_split(rep.step_records)
    soc = [r["realized_soc_pct"] for r in recs]
    on = sum(1 for r in recs if r["realized_diesel_w"] > 0.0)
    starts, was = 0, False
    for r in recs:
        cur = r["realized_diesel_w"] > 0.0
        if cur and not was:
            starts += 1
        was = cur
    return {
        "fuel_l": round(rep.cumulative_diesel_fuel_l, 4),
        "on_hours": on,
        "startups": starts,
        "curtail_wh": round(rep.cumulative_curtailment_wh, 2),
        "unmet_total_wh": round(rep.cumulative_unmet_load_wh, 2),
        "served_total_wh": round(rep.cumulative_served_load_wh, 2),
        "min_soc_pct": round(min(soc), 4),
        "max_soc_pct": round(max(soc), 4),
        "soc_floor_violations": sum(1 for s in soc if s < 19.999),
        "terminal_soc_realized_h24": round(soc[-1], 4),
        **split,
    }


def work(fr):
    fs, t0, oi = fr["forecast_start"], fr["t0_timestamp"], fr["origin_index"]
    out = {"origin_index": oi, "forecast_start": fs, "status": {}}
    for arm in ["A", "B"]:
        try:
            out[arm] = run_arm(arm, fs, t0)
            out["status"][arm] = "OK"
        except RuntimeError as e:
            out[arm] = None
            out["status"][arm] = f"OPTIMIZER_OR_SAFETY_FAILURE: {e}"
    fb = fr["arms"]["ARM_B_CANDIDATE"]
    a = out["A"]
    out["A_reproduces_frozen"] = bool(a) and (
        abs(a["fuel_l"] - fb["diesel_fuel_liters"]) < 1e-3
        and abs(a["unmet_total_wh"] - fb["unmet_critical_load_wh"]) < 1e-2
        and abs(a["curtail_wh"] - fb["curtailment_wh"]) < 1e-2
        and abs(a["served_total_wh"] - fb["served_load_wh"]) < 1e-2
    )
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
