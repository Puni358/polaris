"""
Research-only EBR reserve-envelope ablation, Arm B only, six traced origins.

The ONLY change: config["ebr_target_wh"] = 0.0 (the frozen config has no such key, so GAP19
falls back to the governed 6-h EBR formula). In GAP19 this sets ebr_target_wh_list = [0.0]*24, so:
  e_stage2_target[t] = 0 for t = 0..22        (EBR reserve envelope removed)
  e_stage2_target[23] = max(0, terminal) = terminal (terminal target preserved exactly)
With the reserve at zero, the only remaining SOC floor is the physical min_e bound (20%).

Baseline B and ablated B are both run here, in one process, with identical code, inputs, and state.
Nothing in production, GAP19, the campaign, or frozen artifacts is touched.
"""
import copy
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
HERE = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"
OUT = HERE / "ebr_ablation"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("trace", HERE / "trace_hourly.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
camp = tr.camp

ORIGINS = [77, 56, 66, 23, 8, 30]
FROZEN = {o["origin_index"]: o for o in json.load(open(
    "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))}

base_cfg = camp.load_canonical_configs()
abl_cfg = copy.deepcopy(base_cfg)
abl_cfg["ebr_target_wh"] = 0.0

# Config invariant: the ONLY difference is the EBR key; terminal target identical.
diff_keys = sorted(k for k in set(base_cfg) | set(abl_cfg) if base_cfg.get(k) != abl_cfg.get(k))
assert diff_keys == ["ebr_target_wh"], f"unexpected config diff: {diff_keys}"
assert abl_cfg["terminal_target_wh"] == base_cfg["terminal_target_wh"] == 100000.0
assert "ebr_target_wh" not in base_cfg, "baseline must use the governed EBR formula"

weather_df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")


def run(cfg, ebr_override, fs, t0):
    sub = weather_df[weather_df["forecast_start"] == fs]
    realized_solar = sub["actual_SW_IN"].tolist()
    realized_ts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    realized_wind = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    realized_demand = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    realized = (realized_solar, realized_wind, realized_demand, realized_ts)
    tr.EBR_OVERRIDE = ebr_override   # margin/record reference only; GAP19 reads the config
    rep, steps = tr.trace_arm("B", None, fs, t0, weather_df, realized, cfg)
    recs = tr.build_records("B", rep, steps, realized_solar)
    tr.EBR_OVERRIDE = None
    return rep, recs


def metrics(rep, recs):
    on = sum(1 for r in recs if r["realized_diesel_w"] > 0.0)
    starts, was = 0, False
    for r in recs:
        is_on = r["realized_diesel_w"] > 0.0
        if is_on and not was:
            starts += 1
        was = is_on
    chg = sum(r["realized_charge_w"] for r in recs)
    dis = sum(r["realized_discharge_w"] for r in recs)
    dsl_to_batt = sum(min(r["realized_diesel_w"], r["realized_charge_w"]) for r in recs)
    soc = [r["realized_soc_pct"] for r in recs]
    curt_same = sum(r["realized_curtailment_w"] for r in recs if r["curtailment_cause"] == "same_hour_discharge")
    return {
        "fuel_l": round(rep.cumulative_diesel_fuel_l, 4),
        "on_hours": on,
        "startups": starts,
        "diesel_energy_wh": round(sum(r["realized_diesel_w"] for r in recs), 2),
        "diesel_to_battery_wh_proxy": round(dsl_to_batt, 2),
        "battery_charge_wh": round(chg, 2),
        "battery_discharge_wh": round(dis, 2),
        "efc": round((chg + dis) / (2.0 * 200000.0), 4),
        "min_soc_pct": round(min(soc), 2),
        "max_soc_pct": round(max(soc), 2),
        "terminal_soc_pct_h24": round(soc[-1], 2),
        "unmet_wh": round(rep.cumulative_unmet_load_wh, 2),
        "curtail_wh": round(rep.cumulative_curtailment_wh, 2),
        "curtail_same_hour_discharge_wh": round(curt_same, 2),
        "step0_plan_diesel_w": recs[0]["plan_diesel_t0_w"],
        "step0_plan_charge_w": recs[0]["plan_charge_t0_w"],
        "diesel_charge_steps_t0": sum(1 for r in recs if r["plan_diesel_t0_w"] > 0 and r["plan_charge_t0_w"] > 0),
        "terminal_tight_steps": sum(1 for r in recs if abs(r["terminal_margin_t23_wh"]) < 100),
        "reserve_tight_steps": sum(1 for r in recs if r["reserve_margin_min_wh"] < 100),
        "soc_series_pct": soc,
    }


def first_divergence(R0, R1):
    for a, b in zip(R0, R1):
        differs = (abs(a["plan_diesel_t0_w"] - b["plan_diesel_t0_w"]) > 1.0
                   or abs(a["plan_charge_t0_w"] - b["plan_charge_t0_w"]) > 1.0
                   or abs(a["plan_discharge_t0_w"] - b["plan_discharge_t0_w"]) > 1.0)
        if differs:
            same_state = (abs(a["state_energy_wh"] - b["state_energy_wh"]) < 1e-2
                          and abs(a["state_fuel_l"] - b["state_fuel_l"]) < 1e-6)
            return {"step": a["step"], "target_ts": a["target_ts"], "same_state": same_state,
                    "base": {k: a[k] for k in ["plan_diesel_t0_w", "plan_charge_t0_w", "plan_discharge_t0_w"]},
                    "ablated": {k: b[k] for k in ["plan_diesel_t0_w", "plan_charge_t0_w", "plan_discharge_t0_w"]}}
    return None


def invariants(R0, R1):
    """Inputs that must be identical. ebr_target_t0_wh is EXCLUDED on purpose: it is the ablated quantity."""
    keys = ["state_t_origin", "target_ts", "forecast_solar_t1_wm2", "forecast_solar_24h_sum_wm2",
            "realized_solar_t1_wm2", "critical_demand_t1_w", "demand_forecast_t1_w",
            "terminal_margin_t23_wh", "j2_target_t23_wh"]
    bad = []
    for a, b in zip(R0, R1):
        for k in keys:
            if k == "terminal_margin_t23_wh":
                continue  # margin uses the ablated reserve; checked separately below
            if k == "j2_target_t23_wh":
                continue  # t23 target = max(EBR23, terminal); EBR23 changes in the ablation
            if a[k] != b[k]:
                bad.append((a["step"], k, a[k], b[k]))
    init_same = (R0[0]["state_energy_wh"] == R1[0]["state_energy_wh"]
                 and R0[0]["state_fuel_l"] == R1[0]["state_fuel_l"]
                 and R0[0]["state_soc_pct"] == R1[0]["state_soc_pct"])
    # Terminal target must be the same value in both arms: t23 floor = max(EBR23, 100000).
    # In the ablation EBR23 = 0, so the t23 requirement must equal 100000 + min_e exactly.
    term_ok = all(abs(r["j2_target_t23_wh"] - (100000.0 + 40000.0)) < 1e-6 for r in R1)
    return {"input_mismatches": bad, "n_mismatch": len(bad), "initial_state_identical": init_same,
            "terminal_floor_preserved_in_ablation": term_ok, "steps": len(R0) == len(R1) == 24}


summary = {}
for oi in ORIGINS:
    fr = FROZEN[oi]
    fs, t0 = fr["forecast_start"], fr["t0_timestamp"]
    repB0, recB0 = run(base_cfg, None, fs, t0)
    repB1, recB1 = run(abl_cfg, 0.0, fs, t0)
    gate = abs(repB0.cumulative_diesel_fuel_l - fr["arms"]["ARM_B_CANDIDATE"]["diesel_fuel_liters"]) < 1e-3
    m0, m1 = metrics(repB0, recB0), metrics(repB1, recB1)
    inv = invariants(recB0, recB1)
    div = first_divergence(recB0, recB1)
    out = {"origin_index": oi, "forecast_start": fs, "frozen_B_reproduced": gate,
           "frozen_B_fuel": fr["arms"]["ARM_B_CANDIDATE"]["diesel_fuel_liters"],
           "base": m0, "ablated": m1, "invariants": inv, "first_divergence": div,
           "records_base": recB0, "records_ablated": recB1}
    (OUT / f"origin_{oi}.json").write_text(json.dumps(out, indent=1))
    summary[oi] = {k: out[k] for k in ["frozen_B_reproduced", "invariants", "first_divergence"]}
    summary[oi]["base"] = {k: v for k, v in m0.items() if k != "soc_series_pct"}
    summary[oi]["ablated"] = {k: v for k, v in m1.items() if k != "soc_series_pct"}
    print(oi, fs[:10], "gate", gate, "fuel base/abl", m0["fuel_l"], m1["fuel_l"],
          "| input mismatches", inv["n_mismatch"], "| terminal floor kept", inv["terminal_floor_preserved_in_ablation"],
          "| first div", (div or {}).get("step"), flush=True)
(OUT / "summary.json").write_text(json.dumps(summary, indent=1))
