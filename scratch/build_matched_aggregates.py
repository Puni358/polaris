#!/usr/bin/env python3
"""
Aggregates the matched re-runs (identical demand / wind / solar for every scenario) into
dashboard/public/data/matched/aggregates.json, used by the System Behavior and Proof pages.

Sources: dashboard/public/data/trace/<variant>/day_*.json (POLARIS variants) and
dashboard/public/data/matched/reactive.json (reactive baseline).
Cycles = total energy taken out of the battery / 150 kWh usable (95% - 20% of 200 kWh).
Usage: .venv/bin/python scratch/build_matched_aggregates.py [--loop]
"""
import glob, json, os, sys, time

ROOT = "dashboard/public/data"
USABLE_KWH = 150.0
PRICE = 2.5
POLARIS = [
    ("scenario4", "Forecast, no safety cushion"),
    ("scenario3", "Forecast, fixed big cushion"),
    ("scenario2", "POLARIS — forecast + smart cushion"),
    ("scenario2_initial_state_exact", "POLARIS + end-of-day fix"),
]

CAND = [
    ("cand_baseline", "Physical baseline"),
    ("cand_successor_v2", "Successor v2"),
    ("cand_k", "Candidate K"),
    ("cand_n1", "Candidate N1"),
]

def cycles_from_soc(socs, start_kwh=100.0):
    e_prev, out = start_kwh, 0.0
    for s in socs:
        e = s * 2.0
        out += max(0.0, e_prev - e)
        e_prev = e
    return out / USABLE_KWH

def polaris_agg(variant):
    man_p = f"{ROOT}/trace/{variant}/manifest.json"
    if not os.path.exists(man_p):
        return None
    man = json.load(open(man_p))
    litres = hours_on = starts = 0
    unserved = unserved_h = curtailed = 0.0
    socs = []
    crit_unmet = noncrit_unmet = 0.0
    n = 0
    for f in sorted(glob.glob(f"{ROOT}/trace/{variant}/day_*.json")):
        for r in json.load(open(f)):
            e = r["executed"]
            n += 1
            litres += e["fuel_l"]
            hours_on += 1 if e["diesel_kw"] > 0 else 0
            starts += 1 if e["generator_started"] else 0
            unserved += e["physics_unserved_kwh"]
            unserved_h += 1 if e["physics_unserved_kwh"] > 0.001 else 0
            curtailed += e["physics_curtailed_kwh"]
            # the solver's own J1 / J1b split for the hour that is actually carried out (step 0)
            u0 = r["plan"]["unmet_kw"][0]
            nc0 = r["plan"]["unmet_noncrit_kw"][0]
            crit_unmet += max(0.0, u0 - nc0)
            noncrit_unmet += nc0
            socs.append(e["soc_after_pct"])
    return dict(hours=n, hours_total=man["hours_total"], diesel_liters=litres, diesel_run_hours=hours_on,
                diesel_starts=starts, unmet_load_kwh=unserved, unmet_load_hours=int(unserved_h),
                renewable_curtailed_kwh=curtailed, battery_cycles=cycles_from_soc(socs), min_soc_pct=min(socs) if socs else None,
                critical_unmet_kwh=crit_unmet, noncritical_unmet_kwh=noncrit_unmet)

def reactive_agg():
    p = f"{ROOT}/matched/reactive.json"
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    litres = sum(r["diesel_fuel_cost"] for r in d) / PRICE
    prev = 0.0
    starts = 0
    for r in d:
        if r["diesel_kw"] > 0 and prev <= 0:
            starts += 1
        prev = r["diesel_kw"]
    return dict(hours=len(d), hours_total=8328, diesel_liters=litres,
                diesel_run_hours=sum(1 for r in d if r["diesel_kw"] > 0), diesel_starts=starts,
                unmet_load_kwh=sum(r["unmet_load_w"] for r in d) / 1000.0,
                unmet_load_hours=sum(1 for r in d if r["unmet_load_w"] > 1),
                renewable_curtailed_kwh=sum(r["renewable_curtailment_wh"] for r in d) / 1000.0,
                battery_cycles=cycles_from_soc([r["battery_soc_pct"] for r in d]),
                min_soc_pct=min(r["battery_soc_pct"] for r in d))

def build():
    out = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "scenarios": {}}
    r = reactive_agg()
    if r:
        out["scenarios"]["reactive"] = dict(label="Basic controller", **r)
    for v, label in POLARIS:
        a = polaris_agg(v)
        if a:
            out["scenarios"][v] = dict(label=label, **a)
    for a in out["scenarios"].values():
        a["fuel_cost"] = a["diesel_liters"] * PRICE
        a["complete"] = a["hours"] >= a["hours_total"]
    out["candidates"] = {}
    for v, label in CAND:
        a = polaris_agg(v)
        if a:
            a["label"] = label
            a["fuel_cost"] = a["diesel_liters"] * PRICE
            a["complete"] = a["hours"] >= a["hours_total"]
            out["candidates"][v] = a
    out["cand_ready"] = len(out["candidates"]) == len(CAND) and all(a["complete"] for a in out["candidates"].values())
    out["ready"] = len(out["scenarios"]) == 5 and all(a["complete"] for a in out["scenarios"].values())
    tmp = f"{ROOT}/matched/aggregates.json.tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, f"{ROOT}/matched/aggregates.json")
    return out

if __name__ == "__main__":
    loop = "--loop" in sys.argv
    while True:
        o = build()
        print(time.strftime("%H:%M:%S"), {k: f"{v['hours']}/{v['hours_total']} {v['diesel_liters']:.0f}L" for k, v in o["scenarios"].items()}, "ready" if o["ready"] else "", flush=True)
        if not loop or (o["ready"] and o.get("cand_ready")):
            break
        time.sleep(900)
