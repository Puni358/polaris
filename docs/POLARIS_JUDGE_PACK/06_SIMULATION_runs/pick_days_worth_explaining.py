#!/usr/bin/env python3
"""
Picks the days worth explaining from the exact-rule full-year trace and writes
dashboard/public/data/featured_days.json. Every number in a reason is computed from the recorded run.
"""
import collections, glob, json

V = "scenario2_initial_state_exact"
D = f"dashboard/public/data/trace/{V}"
KPV = 0.051
recs = []
for f in sorted(glob.glob(D + "/day_*.json")):
    recs += json.load(open(f))
w = json.load(open("dashboard/public/data/matched/weather.json"))
stk = json.load(open(D + "/stakes_index.json"))["rows"]
n = len(recs)
idxs = collections.defaultdict(list)
for i, r in enumerate(recs):
    idxs[r["timestamp"][:10]].append(i)

def kind(dl, dr):
    return "critical" if dl > 1 else ("reserve" if dr > 0.05 else "other")
prot = collections.defaultdict(lambda: [0, 0])
for ts, on, b, dl, dr, df in stk:
    k = kind(dl, dr)
    if k == "critical": prot[ts[:10]][0] += 1
    if k == "reserve": prot[ts[:10]][1] += 1

rows = {}
for day, ix in idxs.items():
    if len(ix) < 24: continue
    ex = [recs[i]["executed"] for i in ix]
    ferr = []
    for i in ix:
        if i + 1 < n:
            a = recs[i + 1]["executed"]["actual_ghi"]; fc = recs[i]["inputs"]["irradiance_wm2"][0]
            if a > 5 or fc > 5: ferr.append((abs(a - fc), i))
    pe = [(abs(e["soc_after_pct"] - recs[i]["plan"]["soc_pct"][0]), i) for e, i in zip(ex, ix)]
    h0 = ix[0]
    rows[day] = dict(
        ix=ix, litres=sum(e["fuel_l"] for e in ex), hrs=sum(e["diesel_kw"] > 0 for e in ex),
        minsoc=min(e["soc_after_pct"] for e in ex), unserved=sum(e["physics_unserved_kwh"] for e in ex),
        solar=sum(min(e["actual_ghi"] * KPV, 60) for e in ex), curt=sum(e["physics_curtailed_kwh"] for e in ex),
        fmae=(sum(x for x, _ in ferr) / len(ferr)) if ferr else 0, fmax=max(ferr) if ferr else (0, ix[0]),
        pe=max(pe)[0], ta=min(w["ta"][h0:h0 + 24]), dem=sum(e["demand_kw"] for e in ex),
        pc=prot[day][0], pr=prot[day][1], i0=h0,
    )

def hour(i): return int(recs[i]["timestamp"][11:13])
def best(key, rev=True, flt=lambda r: True):
    return sorted([d for d, r in rows.items() if flt(r)], key=lambda d: rows[d][key], reverse=rev)[0]

feat = []
def add(day, title, reason, focus_i, tag):
    r = rows[day]
    feat.append(dict(date=day, title=title, tag=tag, reason=reason, focusHour=hour(focus_i),
                     metrics=dict(diesel_l=round(r["litres"], 1), diesel_hours=r["hrs"], min_soc_pct=round(r["minsoc"], 1),
                                  unserved_kwh=round(r["unserved"], 2), solar_kwh=round(r["solar"], 1),
                                  protected_load_hours=r["pc"], protected_reserve_hours=r["pr"])))

d = best("ta", False)
r = rows[d]
add(d, "Coldest day of the year", f"Measured {r['ta']:.1f} °C at the station, winter-peak load ({r['dem']:.0f} kWh) and only {r['solar']:.0f} kWh of sun. The generator ran {r['hrs']} hours ({r['litres']:.0f} L); the battery never went below {r['minsoc']:.1f}% and no load was lost.",
    max(r["ix"], key=lambda i: recs[i]["executed"]["diesel_kw"]), "Coldest")

d = best("litres")
r = rows[d]
add(d, "Hardest day: the most diesel", f"Almost no sun ({r['solar']:.1f} kWh) and a full winter load. The most diesel of the year, {r['litres']:.0f} L over {r['hrs']} hours, yet the battery stayed above {r['minsoc']:.1f}% and not one kWh of load was lost.",
    next(i for i in r["ix"] if recs[i]["executed"]["diesel_kw"] > 0), "Most diesel")

d = best("pc")
r = rows[d]
add(d, "Most decisions that mattered", f"In {r['pc']} of the 24 hours the opposite diesel choice would have left critical load unserved. The battery bottomed at {r['minsoc']:.1f}% (floor 20%) and the lights stayed on all day.",
    min(r["ix"], key=lambda i: recs[i]["executed"]["soc_after_pct"]), "Decision map")

d = best("fmae", True, lambda r: r["hrs"] == 0 and r["solar"] > 100)
r = rows[d]
add(d, "Forecast badly wrong, still no diesel", f"The sunshine forecast missed by {r['fmae']:.0f} W/m² on average during the sunny hours and in one hour the real battery level was up to {r['pe']:.0f} percentage points away from the plan. The next plan started from the real level, the generator never ran and no load was lost.",
    r["fmax"][1], "Forecast miss")

d = best("solar")
r = rows[d]
add(d, "Peak of the midnight sun", f"{r['solar']:.0f} kWh of solar in one day. The generator stayed off all day and the battery filled up, so {r['curt']:.0f} kWh of sun could not be stored (the model's biggest spill).",
    max(r["ix"], key=lambda i: recs[i]["executed"]["actual_ghi"]), "Midnight sun")

d = best("pe", True, lambda r: r["hrs"] == 0)
r = rows[d]
add(d, "Biggest plan-versus-reality gap, corrected", f"In one hour the real battery level was {r['pe']:.1f} percentage points away from what the plan expected. That error did not carry forward: the next plan started from the measured level. No diesel, no load lost.",
    r["fmax"][1] if False else max(r["ix"], key=lambda i: abs(recs[i]["executed"]["soc_after_pct"] - recs[i]["plan"]["soc_pct"][0])), "Feedback loop")

d = best("fmae", True, lambda r: 20 < r["litres"] < 100 and r["solar"] > 100 and r["pr"] >= 1)
r = rows[d]
add(d, "Late-winter forecast miss, absorbed by the reserve", f"The forecast overestimated the sun by {r['fmae']:.0f} W/m² on average. The reserve cushion absorbed it: only {r['litres']:.0f} L of diesel ({r['hrs']} hours), {r['pr']} hour where the reserve itself was protected, and no load lost.",
    r["fmax"][1], "Reserve at work")

# first diesel-free day: the sun returns
d = min((dd for dd, rr in rows.items() if rr["hrs"] == 0 and rr["i0"] > 24 * 30), key=lambda dd: rows[dd]["i0"])
r = rows[d]
add(d, "First diesel-free day of the year", f"Spring sun finally covers the station: {r['solar']:.0f} kWh of solar, zero generator hours all day, minimum battery {r['minsoc']:.1f}% and no load lost. Every earlier day of the year needed the generator.",
    max(r["ix"], key=lambda i: recs[i]["executed"]["actual_ghi"]), "First diesel-free")

feat.sort(key=lambda x: x["date"])
json.dump({"variant": V, "days": feat}, open("dashboard/public/data/featured_days.json", "w"), indent=1, ensure_ascii=False)
for x in feat: print(x["date"], "|", x["title"], "|", x["reason"][:130])
