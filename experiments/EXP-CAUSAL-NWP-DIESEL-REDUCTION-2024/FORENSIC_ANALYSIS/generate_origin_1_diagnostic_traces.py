"""
Generate reproducible Origin-1 hourly traces for Control B, Candidate S, Candidate SW, and EBR-off.
Artifact: experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace/origin_1_hourly_traces.json

Captures all required fields per hour:
- origin_index
- hour
- forecast_demand_w
- critical_demand_w
- realized_demand_w
- forecast_solar_w
- realized_solar_w
- forecast_wind_w
- realized_wind_w
- candidate_ebr_target_wh
- terminal_target_wh
- stage2_target_wh
- diesel_power_w
- battery_charge_w
- battery_discharge_w
- served_load_w
- unmet_load_w
- curtailment_w
- realized_soc_pct
- diesel_fuel_consumed_l
- solver_status
"""

import copy
import hashlib
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
sys.path.insert(0, str(REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"))

import candidate_s_sw_adapter as csa
from system.research.research_critical_demand_adapter import (
    AdaptedClosedLoopRunner,
    adapt_critical_demand_vector
)

spec_camp = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec_camp)
spec_camp.loader.exec_module(camp)

OUT_DIR = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace"
OUT_DIR.mkdir(parents=True, exist_ok=True)

frozen_list = json.load(open("experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))
weather_df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")

o1 = next(o for o in frozen_list if o["origin_index"] == 1)
fs = o1["forecast_start"]
t0 = o1["t0_timestamp"]

sub = weather_df[weather_df["forecast_start"] == fs]
rs = sub["actual_SW_IN"].tolist()
rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

base_cfg = camp.load_canonical_configs()


class TraceObserverRunner(AdaptedClosedLoopRunner):
    """
    Subclasses AdaptedClosedLoopRunner to capture hourly forecast and stage-2 targets at each step.
    """
    def __init__(self, configs, variant):
        super().__init__(configs)
        self.variant = variant
        self.step_snapshots = []

        # Wrap optimizer to record exact targets and forecasts
        inner_opt = self.optimizer
        runner_ref = self

        class InstrumentedOpt:
            def optimize(self, bundle, station_state, config):
                crit_w = config.get("critical_demand_w")
                if crit_w is None:
                    crit_w = adapt_critical_demand_vector(runner_ref.critical_ceiling_w, bundle.demand.point)
                    config["critical_demand_w"] = crit_w

                sol_w = list(bundle.solar_generation.point)
                wnd_w = list(bundle.wind_generation.point)

                cfg_copy = dict(config)
                ebr_used = None
                if runner_ref.variant == "S":
                    ebr_used = csa.compute_variant_s_ebr(crit_w, sol_w)
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant == "SW":
                    ebr_used = csa.compute_variant_sw_ebr(crit_w, sol_w, wnd_w)
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant == "OFF":
                    ebr_used = [0.0] * 24
                    cfg_copy["ebr_target_wh"] = ebr_used
                elif runner_ref.variant == "FROZEN_B":
                    # Unconditional governed EBR computed inside GAP19
                    ebr_used = csa.compute_governed_ebr(crit_w)
                    cfg_copy.pop("ebr_target_wh", None)

                # Compute exact stage 2 target vector passed to GAP19
                stage2_vector = csa.compute_stage2_target_vector(ebr_used, terminal_target_wh=100000.0)

                plan = inner_opt.optimize(bundle, station_state, cfg_copy)

                runner_ref.step_snapshots.append({
                    "forecast_demand_step0": bundle.demand.point[0],
                    "critical_demand_step0": crit_w[0],
                    "forecast_solar_step0": sol_w[0],
                    "forecast_wind_step0": wnd_w[0],
                    "candidate_ebr_target_wh_step0": ebr_used[0],
                    "stage2_target_wh_step0": stage2_vector[0],
                    "terminal_target_wh": 100000.0,
                    "full_forecast_demand": list(bundle.demand.point),
                    "full_critical_demand": list(crit_w),
                    "full_forecast_solar": sol_w,
                    "full_forecast_wind": wnd_w,
                    "full_ebr_trajectory": ebr_used,
                    "full_stage2_trajectory": stage2_vector
                })
                return plan

            def __getattr__(self, name):
                return getattr(inner_opt, name)

        self.optimizer = InstrumentedOpt()


def execute_and_extract_arm(variant_name):
    cfg = dict(base_cfg)
    runner = TraceObserverRunner(cfg, variant=variant_name)
    init_state = camp.make_initial_state(t0)
    rep = runner.run_closed_loop(init_state, 24, weather_df, rs, rw, rd, rts)

    records = []
    for h in range(24):
        sr = rep.step_records[h]
        snap = runner.step_snapshots[h]

        rec = {
            "origin_index": 1,
            "hour": h,
            "forecast_start": fs,
            "target_timestamp": sr.target_timestamp,
            "forecast_demand_w": snap["forecast_demand_step0"],
            "critical_demand_w": snap["critical_demand_step0"],
            "realized_demand_w": sr.realized_demand_w,
            "forecast_solar_w": snap["forecast_solar_step0"],
            "realized_solar_w": sr.realized_solar_w,
            "forecast_wind_w": snap["forecast_wind_step0"],
            "realized_wind_w": sr.realized_wind_w,
            "candidate_ebr_target_wh": snap["candidate_ebr_target_wh_step0"],
            "terminal_target_wh": snap["terminal_target_wh"],
            "stage2_target_wh": snap["stage2_target_wh_step0"],
            "diesel_power_w": sr.realized_diesel_w,
            "battery_charge_w": sr.realized_battery_charge_w,
            "battery_discharge_w": sr.realized_battery_discharge_w,
            "served_load_w": sr.served_load_w,
            "unmet_load_w": sr.unmet_load_w,
            "curtailment_w": sr.curtailment_w,
            "realized_soc_pct": sr.realized_soc_pct,
            "diesel_fuel_consumed_l": sr.diesel_fuel_consumed_l,
            "solver_status": sr.optimizer_status,
            "plan_horizon_snapshots": {
                "forecast_demand_vector": snap["full_forecast_demand"],
                "critical_demand_vector": snap["full_critical_demand"],
                "forecast_solar_vector": snap["full_forecast_solar"],
                "forecast_wind_vector": snap["full_forecast_wind"],
                "ebr_trajectory_wh": snap["full_ebr_trajectory"],
                "stage2_trajectory_wh": snap["full_stage2_trajectory"]
            }
        }
        records.append(rec)

    socs = [r["realized_soc_pct"] for r in records]
    return {
        "variant": variant_name,
        "cumulative_fuel_l": rep.cumulative_diesel_fuel_l,
        "cumulative_unmet_wh": rep.cumulative_unmet_load_wh,
        "cumulative_served_wh": rep.cumulative_served_load_wh,
        "cumulative_curtailment_wh": rep.cumulative_curtailment_wh,
        "min_soc_pct": min(socs),
        "max_soc_pct": max(socs),
        "soc_violations_below_20": sum(1 for s in socs if s < 19.999),
        "hourly_records": records
    }


def main():
    print("Executing Origin 1 Diagnostic Traces...")
    control_b = execute_and_extract_arm("FROZEN_B")
    candidate_s = execute_and_extract_arm("S")
    candidate_sw = execute_and_extract_arm("SW")
    ebr_off = execute_and_extract_arm("OFF")

    artifact = {
        "origin_index": 1,
        "forecast_start": fs,
        "t0_timestamp": t0,
        "arms": {
            "Control_Frozen_B": control_b,
            "Candidate_S": candidate_s,
            "Candidate_SW": candidate_sw,
            "EBR_Off_Diagnostic": ebr_off
        }
    }

    out_file = OUT_DIR / "origin_1_hourly_traces.json"
    with open(out_file, "w") as f:
        json.dump(artifact, f, indent=2)

    sha256 = hashlib.sha256(out_file.read_bytes()).hexdigest()
    print(f"Archived Origin 1 traces to: {out_file}")
    print(f"Artifact SHA-256: {sha256}")

    # Reproduction check on Control B
    fb_origin_1 = o1["arms"]["ARM_B_CANDIDATE"]
    assert abs(control_b["cumulative_fuel_l"] - fb_origin_1["diesel_fuel_liters"]) < 1e-3
    assert abs(control_b["cumulative_unmet_wh"] - fb_origin_1["unmet_critical_load_wh"]) < 1e-2
    assert abs(control_b["min_soc_pct"] - 65.58) < 1e-2
    assert abs(control_b["max_soc_pct"] - 93.85) < 1e-2

    print("\nSummary Table:")
    print(f"  Control Frozen B: Fuel = {control_b['cumulative_fuel_l']:.4f} L, Unmet = {control_b['cumulative_unmet_wh']:.2f} Wh, SOC Range = [{control_b['min_soc_pct']:.2f}%, {control_b['max_soc_pct']:.2f}%]")
    print(f"  Candidate S:      Fuel = {candidate_s['cumulative_fuel_l']:.4f} L, Unmet = {candidate_s['cumulative_unmet_wh']:.2f} Wh, SOC Range = [{candidate_s['min_soc_pct']:.2f}%, {candidate_s['max_soc_pct']:.2f}%]")
    print(f"  Candidate SW:     Fuel = {candidate_sw['cumulative_fuel_l']:.4f} L, Unmet = {candidate_sw['cumulative_unmet_wh']:.2f} Wh, SOC Range = [{candidate_sw['min_soc_pct']:.2f}%, {candidate_sw['max_soc_pct']:.2f}%]")
    print(f"  EBR Off Diag:     Fuel = {ebr_off['cumulative_fuel_l']:.4f} L, Unmet = {ebr_off['cumulative_unmet_wh']:.2f} Wh, SOC Range = [{ebr_off['min_soc_pct']:.2f}%, {ebr_off['max_soc_pct']:.2f}%]")


if __name__ == "__main__":
    main()
