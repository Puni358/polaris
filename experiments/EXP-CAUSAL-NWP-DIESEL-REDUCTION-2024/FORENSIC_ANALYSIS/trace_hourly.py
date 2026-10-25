"""
Research-only instrumented hourly trace for a SMALL subset of frozen origins.

Reuses the frozen campaign functions unchanged (run_diesel_reduction_campaign.py,
AdaptedClosedLoopRunner, GAP19, executor). Observation only: wrappers record
forecast bundles, GAP19 plans, and StationState at every reoptimization.
No dispatch rule, config, or frozen result is modified.

Reproduction gate: per-arm fuel for each traced origin must equal the frozen
per_origin_results.json value, otherwise the trace is refused.
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import pandas as pd

REPO = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(REPO))
import os
os.chdir(REPO)

spec = importlib.util.spec_from_file_location("camp", "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(camp)

from system.schemas.station_state import StationState
from system.research.research_critical_demand_adapter import AdaptedClosedLoopRunner, adapt_critical_demand_vector
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine

OUT = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace"
OUT.mkdir(parents=True, exist_ok=True)

FROZEN = json.load(open("experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))
FROZEN_BY_IDX = {o["origin_index"]: o for o in FROZEN}

# Subset: worst B-vs-A fuel gap origins + typical (near-zero gap) origins, chosen from frozen data.
ORIGINS = [77, 56, 66, 23, 8, 30]

BAT_CAP = 200000.0
MIN_E = 40000.0
MAX_CHG_W = 50000.0
ETA_CHG = 0.92
TERMINAL_WH = 100000.0
# Set only by ablation harnesses; None = governed EBR formula (baseline). Margin reference only.
EBR_OVERRIDE = None


class Rec:
    """Transparent observer around an existing engine or optimizer."""
    def __init__(self, inner, sink, kind):
        self.inner = inner
        self.sink = sink
        self.kind = kind

    def predict(self, state, ctx):
        b = self.inner.predict(state, ctx)
        self.sink["bundle"] = b
        return b

    def optimize(self, bundle, state, cfg):
        plan = self.inner.optimize(bundle, state, cfg)
        self.sink["plan"] = plan
        self.sink["state"] = state
        return plan

    def __getattr__(self, name):
        return getattr(self.inner, name)


def trace_arm(arm, origin_idx, fs, t0, weather_df, realized, configs):
    sink = {}
    runner = AdaptedClosedLoopRunner(configs)
    if arm == "A":
        runner.forecast_engine = Rec(LocalBaselineForecastEngine(Path("system/config/solar_pv.yaml")), sink, "fc")
    else:
        runner.forecast_engine = Rec(CausalNwpPhysicsForecastEngine(), sink, "fc")
    runner.optimizer = Rec(runner.optimizer, sink, "opt")

    # Per-step capture: the runner calls predict -> optimize in order each step.
    steps = []
    orig_predict = runner.forecast_engine.predict

    def predict_and_capture(state, ctx):
        b = orig_predict(state, ctx)
        steps.append({"origin_state": state, "bundle": b})
        return b

    runner.forecast_engine.predict = predict_and_capture
    orig_opt = runner.optimizer.optimize

    def opt_and_capture(bundle, state, cfg):
        plan = orig_opt(bundle, state, cfg)
        steps[-1]["plan"] = plan
        steps[-1]["cfg_cd"] = cfg.get("critical_demand_w")
        return plan

    runner.optimizer.optimize = opt_and_capture

    state = camp.make_initial_state(t0)
    rep = runner.run_closed_loop(state, 24, weather_df, *realized)
    return rep, steps


def build_records(arm, rep, steps, realized_solar):
    recs = []
    for i, (st, sr) in enumerate(zip(steps, rep.step_records)):
        b, plan, s0 = st["bundle"], st["plan"], st["origin_state"]
        crit = adapt_critical_demand_vector(11600.0, b.demand.point)
        # Recompute GAP19 EBR (governed 6h lookahead) from the same bundle, for the J2 target.
        ebr = []
        if EBR_OVERRIDE is not None:
            ebr = [EBR_OVERRIDE] * 24
        else:
            for t in range(24):
                end_k = min(t + 6, 24)
                ebr.append((1.0 / 0.92) * sum(crit[k] for k in range(t, end_k)))
        e_stage2_0 = ebr[0]
        e_stage2_23 = max(ebr[23], TERMINAL_WH)
        # Planned reserve/terminal margins: E_next[t] - (target[t] + min_e). ~0 means the constraint is tight.
        stage2 = ebr[:23] + [e_stage2_23]
        e_next = [p / 100.0 * BAT_CAP for p in plan.battery_soc]
        margins = [e_next[t] - (stage2[t] + MIN_E) for t in range(24)]
        reserve_margin_min = min(margins[:23])
        terminal_margin = margins[23]
        cur = sr.curtailment_w
        dis = sr.realized_battery_discharge_w
        chg = sr.realized_battery_charge_w
        room = max(0.0, 0.95 * BAT_CAP - s0.battery_energy_wh)
        chg_cap = min(MAX_CHG_W, room / ETA_CHG)
        if cur > 1e-6:
            if dis > 1e-4:
                cause = "same_hour_discharge"
            elif chg >= chg_cap - 1e-3:
                cause = "charge_cap"
            else:
                cause = "other"
        else:
            cause = "none"
        recs.append({
            "arm": arm,
            "step": i,
            "state_t_origin": s0.timestamp,
            "target_ts": sr.target_timestamp,
            "state_soc_pct": round(s0.battery_energy_wh / BAT_CAP * 100.0, 4),
            "state_energy_wh": round(s0.battery_energy_wh, 2),
            "state_fuel_l": round(s0.diesel_fuel_remaining_liters, 4),
            "state_diesel_running": bool(s0.diesel_running),
            "forecast_solar_t1_wm2": round(b.solar_irradiance.point[0], 2),
            "forecast_solar_24h_sum_wm2": round(sum(b.solar_irradiance.point), 2),
            "realized_solar_t1_wm2": round(realized_solar[i], 2),
            "forecast_error_t1_wm2": round(b.solar_irradiance.point[0] - realized_solar[i], 2),
            "critical_demand_t1_w": round(crit[0], 2),
            "demand_forecast_t1_w": round(b.demand.point[0], 2),
            "plan_diesel_t0_w": round(plan.diesel_power[0], 2),
            "plan_charge_t0_w": round(plan.battery_charge[0], 2),
            "plan_discharge_t0_w": round(plan.battery_discharge[0], 2),
            "plan_E_next_t0_wh": round(plan.battery_soc[0] / 100.0 * BAT_CAP, 2),
            "ebr_target_t0_wh": round(e_stage2_0 + MIN_E, 2),
            "j2_target_t23_wh": round(e_stage2_23 + MIN_E, 2),
            "j2_shortfall_t0_wh": round(plan.reserve_shortfall[0], 4),
            "terminal_shortfall_t23_wh": round(plan.reserve_shortfall[23], 4),
            "reserve_margin_min_wh": round(reserve_margin_min, 2),
            "terminal_margin_t23_wh": round(terminal_margin, 2),
            "plan_E_next_t23_wh": round(e_next[23], 2),
            "j1_critical_unmet": round(plan.j1_objective, 4),
            "j3_fuel_objective": round(plan.j3_objective, 4),
            "j4_curtail_objective": round(plan.j4_objective, 4),
            "realized_diesel_w": round(sr.realized_diesel_w, 2),
            "realized_charge_w": round(chg, 2),
            "realized_discharge_w": round(dis, 2),
            "realized_curtailment_w": round(cur, 2),
            "realized_unmet_w": round(sr.unmet_load_w, 2),
            "realized_soc_pct": round(sr.realized_soc_pct, 4),
            "step_fuel_l": round(sr.diesel_fuel_consumed_l, 4),
            "curtailment_cause": cause,
        })
    return recs


def first_divergence(recA, recB):
    """First hour where the arms are in the SAME physical state (SOC, fuel, diesel running)
    but make DIFFERENT step-0 decisions (diesel/charge/discharge)."""
    out = {"same_state_different_decision": None, "first_any_decision_difference": None,
           "first_any_state_difference": None}
    for a, b in zip(recA, recB):
        same_state = (abs(a["state_energy_wh"] - b["state_energy_wh"]) < 1e-2
                      and abs(a["state_fuel_l"] - b["state_fuel_l"]) < 1e-6
                      and a["state_diesel_running"] == b["state_diesel_running"])
        diff_dec = (abs(a["plan_diesel_t0_w"] - b["plan_diesel_t0_w"]) > 1.0
                    or abs(a["plan_charge_t0_w"] - b["plan_charge_t0_w"]) > 1.0
                    or abs(a["plan_discharge_t0_w"] - b["plan_discharge_t0_w"]) > 1.0)
        if out["first_any_decision_difference"] is None and diff_dec:
            out["first_any_decision_difference"] = a["step"]
        if out["first_any_state_difference"] is None and not same_state:
            out["first_any_state_difference"] = a["step"]
        if out["same_state_different_decision"] is None and same_state and diff_dec:
            out["same_state_different_decision"] = {
                "step": a["step"], "target_ts": a["target_ts"],
                "A": {k: a[k] for k in ["forecast_solar_t1_wm2", "forecast_solar_24h_sum_wm2", "plan_diesel_t0_w",
                                        "plan_charge_t0_w", "plan_discharge_t0_w", "plan_E_next_t0_wh",
                                        "ebr_target_t0_wh", "j2_shortfall_t0_wh", "terminal_shortfall_t23_wh",
                                        "j3_fuel_objective", "j4_curtail_objective"]},
                "B": {k: b[k] for k in ["forecast_solar_t1_wm2", "forecast_solar_24h_sum_wm2", "plan_diesel_t0_w",
                                        "plan_charge_t0_w", "plan_discharge_t0_w", "plan_E_next_t0_wh",
                                        "ebr_target_t0_wh", "j2_shortfall_t0_wh", "terminal_shortfall_t23_wh",
                                        "j3_fuel_objective", "j4_curtail_objective"]},
            }
    return out


def main():
    configs = camp.load_canonical_configs()
    weather_df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    summary = {}
    for oi in ORIGINS:
        fr = FROZEN_BY_IDX[oi]
        fs = fr["forecast_start"]
        t0 = fr["t0_timestamp"]
        sub = weather_df[weather_df["forecast_start"] == fs]
        realized_solar = sub["actual_SW_IN"].tolist()
        realized_ts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
        realized_wind = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
        realized_demand = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
        realized = (realized_solar, realized_wind, realized_demand, realized_ts)

        repA, stepsA = trace_arm("A", oi, fs, t0, weather_df, realized, configs)
        repB, stepsB = trace_arm("B", oi, fs, t0, weather_df, realized, configs)
        recA = build_records("A", repA, stepsA, realized_solar)
        recB = build_records("B", repB, stepsB, realized_solar)

        fA = round(repA.cumulative_diesel_fuel_l, 4)
        fB = round(repB.cumulative_diesel_fuel_l, 4)
        frA = fr["arms"]["ARM_A_BASELINE"]["diesel_fuel_liters"]
        frB = fr["arms"]["ARM_B_CANDIDATE"]["diesel_fuel_liters"]
        reproduced = abs(fA - frA) < 1e-3 and abs(fB - frB) < 1e-3

        div = first_divergence(recA, recB)
        out = {
            "origin_index": oi, "forecast_start": fs, "t0": t0,
            "reproduction_gate": {"A_trace_fuel": fA, "A_frozen_fuel": frA,
                                  "B_trace_fuel": fB, "B_frozen_fuel": frB, "PASS": reproduced},
            "divergence": div,
            "records_A": recA, "records_B": recB,
        }
        (OUT / f"origin_{oi}.json").write_text(json.dumps(out, indent=1))
        summary[oi] = {"fs": fs, "PASS": reproduced, "fuelA": fA, "fuelB": fB, "divergence": div}
        print(oi, fs, "reproduced" if reproduced else "MISMATCH", fA, frA, fB, frB, flush=True)
        print("   first_any_decision_difference:", div["first_any_decision_difference"],
              " same_state_diff_decision step:", (div["same_state_different_decision"] or {}).get("step"), flush=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
