#!/usr/bin/env python3
"""
What-if analysis on the recorded Scenario 2 decision trace.

For every traced hour this re-solves the SAME inputs (recorded in
dashboard/public/data/trace/<variant>/day_*.json) with the solver's step-0 diesel
decision flipped:
    solver chose diesel ON  -> re-solve with the generator banned at step 0
    solver chose diesel OFF -> re-solve with the generator forced ON at step 0
and records the real J1 / J1b / J2 / J3 / J4 of the alternative plan next to the
baseline, so the dashboard can show what a different decision would have cost.

A baseline re-solve (no override) is also run and compared with the recorded plan;
`baseline_match` tells whether the replay reproduced the recorded step-0 diesel.

Output: dashboard/public/data/trace/<variant>/whatif_YYYY-MM-DD.json
Usage : .venv/bin/python scratch/whatif_decisions.py [--variant scenario2] [--days 2024-01-20 ...]
Days already processed are skipped; with no --days it loops over every available day.
"""
import argparse, glob, json, os, sys, time
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO); os.chdir(REPO)
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import TimeseriesForecast, ForecastBundle
import pandas as pd

CAP = 200_000.0
opt = GAP19HighsNativeOptimizer()


def ts(v, u):
    return TimeseriesForecast(point=v, lower=v, upper=v, unit=u)


def solve(rec, overrides=None):
    t0 = pd.Timestamp(rec["timestamp"])
    stamps = [(t0 + pd.Timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]
    inp, res, st = rec["inputs"], rec["reserve"], rec["state"]
    w = lambda a: [v * 1000.0 for v in a]
    bundle = ForecastBundle(
        schema_version="1.0.0", origin_timestamp=stamps[0], horizon_hours=24, timestamps=stamps,
        solar_irradiance=ts(inp["irradiance_wm2"], "W/m^2"), solar_generation=ts(w(inp["solar_kw"]), "W"),
        wind_generation=ts(w(inp["wind_kw"]), "W"), demand=ts(w(inp["demand_kw"]), "W"),
        metadata={}, demand_critical=ts(w(inp["critical_kw"]), "W"))
    e0 = st["energy_before_kwh"] * 1000.0
    state = StationState(
        timestamp=stamps[0], battery_soc_pct=e0 / CAP * 100.0, battery_energy_wh=e0,
        diesel_running=st["diesel_running_before"], diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0, last_observed_demand=30000.0,
        last_observed_wind_generation=15000.0, operating_mode="NORMAL")
    cfg = {
        "operating_mode": "NORMAL",
        "battery": {"capacity_wh": CAP, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
        "diesel": {"min_power_w": 10000.0, "max_power_w": 100000.0},
        "terminal_reserve_model": "INITIAL_STATE", "optimizer": {"timestep_hours": 1.0},
        "reserve_deadband_wh": res["deadband_kwh"] * 1000.0, "ebr_target_wh": res["ebr_target_kwh"] * 1000.0,
    }
    mode = res.get("terminal_mode", "as_is")
    if mode != "as_is":
        cfg["terminal_target_wh"] = res["terminal_target_kwh"] * 1000.0
    if overrides:
        cfg["diesel_step_overrides"] = overrides
    return opt.optimize(forecast_bundle=bundle, station_state=state, config=cfg)


def summarize(plan):
    d = [round(v / 1000.0, 2) for v in plan.diesel_power]
    return {
        "status": plan.constraint_status,
        "j1_wh": plan.j1_objective, "j1b_wh": getattr(plan, "j1b_objective", None), "j2_wh": plan.j2_objective,
        "j3_litres": plan.j3_objective, "j4_wh": plan.j4_objective,
        "diesel_kw": d, "soc_pct": [round(v, 2) for v in plan.battery_soc],
        "unmet_kwh": round(sum(plan.unmet_load) / 1000.0, 3),
        "min_soc_pct": round(min(plan.battery_soc), 2),
        "diesel_hours": sum(1 for v in d if v > 0),
    }


def process_day(path, out_path):
    rows = json.load(open(path))
    out = []
    for rec in rows:
        base = solve(rec)
        rec_d0 = rec["plan"]["diesel_kw"][0]
        base_d0 = base.diesel_power[0] / 1000.0
        chose_on = rec_d0 > 0
        alt_plan = solve(rec, {0: "off" if chose_on else "on"})
        out.append({
            "timestamp": rec["timestamp"],
            "baseline_match": abs(base_d0 - rec_d0) < 0.05,
            "baseline_replay": summarize(base),
            "alt_kind": "diesel_banned" if chose_on else "diesel_forced",
            "alt": summarize(alt_plan),
        })
    json.dump(out, open(out_path, "w"), separators=(",", ":"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="scenario2")
    ap.add_argument("--days", nargs="*")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--loop", action="store_true", help="keep waiting for new days until the trace finishes")
    a = ap.parse_args()
    d = f"dashboard/public/data/trace/{a.variant}"
    while True:
        man = json.load(open(f"{d}/manifest.json"))
        days = a.days or man["days"]
        todo = [x for i, x in enumerate(man["days"]) if x in days and i % a.shards == a.shard and not os.path.exists(f"{d}/whatif_{x}.json")]
        for x in todo:
            t = time.time()
            out = process_day(f"{d}/day_{x}.json", f"{d}/whatif_{x}.json")
            m = sum(o["baseline_match"] for o in out)
            print(f"{x}: {len(out)} hours, replay match {m}/{len(out)}, {time.time()-t:.0f}s", flush=True)
        if not a.loop or (man["hours_done"] >= man["hours_total"] and not todo):
            break
        time.sleep(30)

if __name__ == "__main__":
    main()
