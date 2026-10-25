"""
Six-origin critical-aware EBR experiment (research-only).

Arms (same origins, forecasts, initial states, executor, terminal target, GAP19 unmodified):
  A = frozen Arm B  : governed EBR formula (config has no ebr_target_wh key)
  B = EBR-OFF       : config ebr_target_wh = 0.0          (diagnostic only, not a success target)
  C = critical-aware: per-hour EBR list computed by the research wrapper from the bundle:
        EBR_ca[t] = (1/eta_dis) * sum_{k=t}^{min(t+5,23)} max(0, crit[k] - solar_gen[k] - wind_gen[k]) * dt
      with crit = min(11600 W, forecast demand[k]) (the frozen adapter rule), solar_gen/wind_gen in W
      from the same bundle, dt = 1 h, eta_dis = 0.92. Units: W x h = Wh. Floor max(0, .) >= 0.
      Terminal target unchanged (GAP19 applies max(EBR_ca[23], terminal)). min_e 20% floor unchanged.

Critical convention for PASS/FAIL (fixed BEFORE running, same as the completed load-class diagnostic):
  critical_realized[t] = min(11600 W, realized total demand[t]); critical served first, then non-critical.
Accounting only: the split does not change any dispatch.
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
OUT = HERE / "critical_aware_ebr"
OUT.mkdir(parents=True, exist_ok=True)

ORIGINS = [77, 56, 66, 23, 8, 30]
CRIT_W = 11600.0
ETA_DIS = 0.92
DT = 1.0
FROZEN = {o["origin_index"]: o for o in json.load(open(
    "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))}
WEATHER = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")

_camp = None
_CFG = {}


def ebr_critical_aware(crit, solar_w, wind_w):
    """Reserve over 6 h of critical energy not covered by forecast renewables. Returns Wh per hour t."""
    assert len(crit) == len(solar_w) == len(wind_w) == 24
    out = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            s += max(0.0, crit[k] - solar_w[k] - wind_w[k]) * DT
        out.append(s / ETA_DIS)
    assert all(math.isfinite(v) and v >= 0.0 for v in out), "reserve must be finite and non-negative"
    return out


def ebr_governed(crit):
    """Governed formula as implemented in GAP19 (lines 127-131), for the identity check."""
    out = []
    for t in range(24):
        end_k = min(t + 6, 24)
        out.append((1.0 / ETA_DIS) * sum(crit[k] * DT for k in range(t, end_k)))
    return out


def _init():
    global _camp
    spec = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
    _camp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_camp)
    base = _camp.load_canonical_configs()
    abl = copy.deepcopy(base)
    abl["ebr_target_wh"] = 0.0
    assert "ebr_target_wh" not in base
    assert sorted(k for k in set(base) | set(abl) if base.get(k) != abl.get(k)) == ["ebr_target_wh"]
    assert base["terminal_target_wh"] == abl["terminal_target_wh"] == 100000.0
    _CFG["base"] = base
    _CFG["off"] = abl
    # Identity check: with zero renewables the critical-aware formula must equal the governed formula.
    from system.research.research_critical_demand_adapter import adapt_critical_demand_vector
    crit = adapt_critical_demand_vector(CRIT_W, [9000.0 + 500.0 * h for h in range(24)])
    z = [0.0] * 24
    assert all(abs(a - b) < 1e-9 for a, b in zip(ebr_critical_aware(crit, z, z), ebr_governed(crit))), \
        "unit/identity check failed"


class CaptureOpt:
    """Wraps GAP19 without changing it. Mode C injects the per-hour reserve list into a copied config."""
    def __init__(self, inner, mode, sink):
        self.inner, self.mode, self.sink = inner, mode, sink

    def optimize(self, bundle, state, cfg):
        from system.research.research_critical_demand_adapter import adapt_critical_demand_vector
        crit = list(cfg["critical_demand_w"])
        ebr_used = None
        cfg2 = cfg
        if self.mode == "C":
            ebr_used = ebr_critical_aware(crit, bundle.solar_generation.point, bundle.wind_generation.point)
            cfg2 = dict(cfg)
            cfg2["ebr_target_wh"] = ebr_used
        plan = self.inner.optimize(bundle, state, cfg2)
        self.sink.append({
            "forecast_solar_w": list(bundle.solar_generation.point),
            "forecast_wind_w": list(bundle.wind_generation.point),
            "forecast_demand_w": list(bundle.demand.point),
            "crit_w": crit,
            "ebr_used_wh": ebr_used,
            "plan_soc_pct": list(plan.battery_soc),
            "plan_reserve_shortfall": list(plan.reserve_shortfall),
            "plan_status": plan.constraint_status,
        })
        return plan


def run_arm(mode, fs, t0):
    from system.research.research_critical_demand_adapter import AdaptedClosedLoopRunner
    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    cfg = _CFG["off"] if mode == "B" else _CFG["base"]
    sub = WEATHER[WEATHER["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    runner = AdaptedClosedLoopRunner(cfg)
    runner.forecast_engine = CausalNwpPhysicsForecastEngine()
    sink = []
    runner.optimizer = CaptureOpt(runner.optimizer, "C" if mode == "C" else "AB", sink)
    state = _camp.make_initial_state(t0)
    rep = runner.run_closed_loop(state, 24, WEATHER, rs, rw, rd, rts)
    return rep, sink


def hourly_rows(rep, sink, mode):
    rows = []
    for i, (sr, cap) in enumerate(zip(rep.step_records, sink)):
        D = sr.realized_demand_w
        S = sr.realized_solar_w + sr.realized_wind_w + sr.realized_diesel_w + sr.realized_battery_discharge_w
        Dc = min(CRIT_W, D)
        Dn = D - Dc
        sc = min(Dc, S)
        sn = min(Dn, max(0.0, S - sc))
        cur = sr.curtailment_w
        dis = sr.realized_battery_discharge_w
        chg = sr.realized_battery_charge_w
        if cur > 1e-6:
            cause = "same_hour_discharge" if dis > 1e-4 else "other"
        else:
            cause = "none"
        ebr0 = cap["ebr_used_wh"][0] if cap["ebr_used_wh"] is not None else None
        rows.append({
            "mode": mode, "step": i, "origin_ts": sr.origin_timestamp, "target_ts": sr.target_timestamp,
            "critical_demand_w": round(Dc, 2), "realized_demand_w": D,
            "forecast_solar_t1_w": round(cap["forecast_solar_w"][0], 2),
            "forecast_wind_t1_w": round(cap["forecast_wind_w"][0], 2),
            "ebr_target_t0_wh": round(ebr0, 2) if ebr0 is not None else None,
            "realized_soc_pct": round(sr.realized_soc_pct, 4),
            "plan_diesel_w": round(sr.planned_diesel_power_w, 2), "realized_diesel_w": round(sr.realized_diesel_w, 2),
            "plan_charge_w": round(sr.planned_battery_charge_w, 2), "realized_charge_w": round(chg, 2),
            "plan_discharge_w": round(sr.planned_battery_discharge_w, 2), "realized_discharge_w": round(dis, 2),
            "total_served_w": round(sr.served_load_w, 2), "total_unmet_w": round(sr.unmet_load_w, 2),
            "critical_served_w": round(sc, 2), "critical_unmet_w": round(Dc - sc, 2),
            "noncritical_served_w": round(sn, 2), "noncritical_unmet_w": round(Dn - sn, 2),
            "curtailment_w": round(cur, 2), "curtailment_cause": cause,
            "plan_terminal_soc_pct_h24": round(cap["plan_soc_pct"][23], 4),
            "plan_terminal_shortfall_wh": round(cap["plan_reserve_shortfall"][23], 4),
            "plan_status": cap["plan_status"],
        })
    return rows


def summarize(rep, rows):
    served = rep.cumulative_served_load_wh
    unmet = rep.cumulative_unmet_load_wh
    cdem = sum(r["critical_demand_w"] for r in rows)
    csrv = sum(r["critical_served_w"] for r in rows)
    ndem = sum(r["realized_demand_w"] - r["critical_demand_w"] for r in rows)
    nsrv = sum(r["noncritical_served_w"] for r in rows)
    soc = [r["realized_soc_pct"] for r in rows]
    on = sum(1 for r in rows if r["realized_diesel_w"] > 0)
    starts, was = 0, False
    for r in rows:
        cur = r["realized_diesel_w"] > 0
        if cur and not was:
            starts += 1
        was = cur
    return {
        "fuel_l": round(rep.cumulative_diesel_fuel_l, 4), "on_hours": on, "startups": starts,
        "curtail_wh": round(rep.cumulative_curtailment_wh, 2),
        "curtail_same_hour_discharge_wh": round(sum(r["curtailment_w"] for r in rows if r["curtailment_cause"] == "same_hour_discharge"), 2),
        "total_served_wh": round(served, 2), "total_unmet_wh": round(unmet, 2),
        "total_reliability_pct": round(100 * served / (served + unmet), 4),
        "critical_demand_wh": round(cdem, 2), "critical_served_wh": round(csrv, 2),
        "critical_unmet_wh": round(cdem - csrv, 2),
        "critical_reliability_pct": round(100 * csrv / cdem, 4),
        "noncritical_demand_wh": round(ndem, 2), "noncritical_served_wh": round(nsrv, 2),
        "noncritical_unmet_wh": round(ndem - nsrv, 2),
        "min_soc_pct": round(min(soc), 4), "max_soc_pct": round(max(soc), 4),
        "soc_floor_violations": sum(1 for s in soc if s < 19.999),
        "terminal_plan_shortfall_steps": sum(1 for r in rows if r["plan_terminal_shortfall_wh"] > 1e-3),
        "terminal_soc_realized_h24": round(soc[-1], 4),
        "optimizer_failures": sum(1 for r in rows if r["plan_status"] not in ("OPTIMAL", "FEASIBLE")),
    }


def work(oi):
    fr = FROZEN[oi]
    fs, t0 = fr["forecast_start"], fr["t0_timestamp"]
    res = {"origin_index": oi, "forecast_start": fs}
    arms = {}
    for mode, label in [("A", "frozen_B"), ("B", "ebr_off"), ("C", "critical_aware")]:
        try:
            rep, sink = run_arm(mode, fs, t0)
            rows = hourly_rows(rep, sink, mode)
            arms[label] = {"summary": summarize(rep, rows), "hourly": rows}
        except RuntimeError as e:
            arms[label] = {"error": str(e)}
    fb = fr["arms"]["ARM_B_CANDIDATE"]
    a = arms["frozen_B"]["summary"]
    res["frozen_B_reproduced"] = (
        abs(a["fuel_l"] - fb["diesel_fuel_liters"]) < 1e-3
        and abs(a["total_unmet_wh"] - fb["unmet_critical_load_wh"]) < 1e-2
        and abs(a["curtail_wh"] - fb["curtailment_wh"]) < 1e-2
        and abs(a["total_served_wh"] - fb["served_load_wh"]) < 1e-2)
    res["arms"] = arms
    (OUT / f"origin_{oi}.json").write_text(json.dumps(res))
    return res


if __name__ == "__main__":
    with Pool(processes=4, initializer=_init) as pool:
        results = pool.map(work, ORIGINS, chunksize=1)
    (OUT / "all_results.json").write_text(json.dumps(results))
    print("DONE", flush=True)
