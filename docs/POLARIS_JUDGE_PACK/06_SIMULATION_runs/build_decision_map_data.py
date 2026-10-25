#!/usr/bin/env python3
"""
Builds dashboard/public/data/trace/<variant>/stakes_index.json: one compact row per hour
that has BOTH a trace record and a what-if result, so the dashboard can rank the decisions
that mattered without loading hundreds of day files.

row = [timestamp, model_diesel_on(0/1), model_plan_fuel_L, d_load_Wh, d_reserve_kWh, d_fuel_L]
where d_* = alternative minus the model's choice (J1+J1b in Wh, J2 in kWh, J3 in litres).
Usage: .venv/bin/python scratch/build_stakes_index.py --variant scenario2_initial_state_exact [--loop]
"""
import argparse, glob, json, os, time

def build(variant):
    d = f"dashboard/public/data/trace/{variant}"
    rows = []
    for wf in sorted(glob.glob(f"{d}/whatif_*.json")):
        day = os.path.basename(wf)[7:-5]
        tf = f"{d}/day_{day}.json"
        if not os.path.exists(tf):
            continue
        try:
            wi = {w["timestamp"]: w for w in json.load(open(wf))}
            tr = json.load(open(tf))
        except Exception:
            continue
        for r in tr:
            w = wi.get(r["timestamp"])
            if not w:
                continue
            b, a = r["objectives"], w["alt"]
            rows.append([
                r["timestamp"], 1 if r["plan"]["diesel_kw"][0] > 0 else 0, round(b["j3_litres"], 2),
                round((a["j1_wh"] + (a["j1b_wh"] or 0)) - (b["j1_wh"] + (b["j1b_wh"] or 0)), 2),
                round((a["j2_wh"] - b["j2_wh"]) / 1000, 3), round(a["j3_litres"] - b["j3_litres"], 3),
            ])
    tmp = f"{d}/stakes_index.json.tmp"
    json.dump({"variant": variant, "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": rows}, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, f"{d}/stakes_index.json")
    return len(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="scenario2")
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args()
    while True:
        n = build(a.variant)
        print(time.strftime("%H:%M:%S"), a.variant, n, "hours indexed", flush=True)
        if not a.loop:
            break
        man = json.load(open(f"dashboard/public/data/trace/{a.variant}/manifest.json"))
        if man["hours_done"] >= man["hours_total"] and n >= man["hours_total"]:
            break
        time.sleep(60)
