"""
Phase 1 Research Experiment Runner & Reproduction Gate Check
Evening-independent cloud-fraction bias correction — Phase 1
"""

import math
import sys
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parents[1]
_HERE = REPO / "experiments" / "stage4_planner_cf_consistency_2025"
for p in (str(REPO), str(_HERE), str(REPO / "experiments" / "stage4_sw_low_sun_2025_holdout")):
    if p not in sys.path:
        sys.path.insert(0, p)

import stage4_low_sun_adapter as s4a
from planner_cf_campaign_runner import (
    PlannerCFArmRunner,
    _load_canonical_configs,
    origin_population,
    realized_inputs_for,
    WEATHER_2025_PATH,
    DECOMPOSITION_2025_PATH,
)

ORIGIN_INDICES = [1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121]

class CandidateForecastEngineWrapper:
    """Input-boundary research wrapper for cloud-fraction bias correction.
    Replaces fc_cloud_cover with corrected_cloud = k * forecast_cloud only when forecast_cloud >= 50%.
    Does NOT modify causal_nwp_physics.py itself.
    """
    def __init__(self, inner_engine, k: float):
        self.inner_engine = inner_engine
        self.k = k

    def predict(self, state, forecast_inputs):
        inputs_copy = dict(forecast_inputs)
        if "fc_cloud_cover" in inputs_copy:
            cloud = inputs_copy["fc_cloud_cover"]
            inputs_copy["fc_cloud_cover"] = [
                self.k * float(c) if float(c) >= 50.0 else float(c)
                for c in cloud
            ]
        return self.inner_engine.predict(state, inputs_copy)


def run_arm_on_subset(arm: str, origins_subset, configs, make_initial_state, weather_df, solar_provider, k: float = None):
    all_origins_list = origin_population(weather_df)
    hourly_all = []
    executed_all = []
    binding_stats = []

    for oi in origins_subset:
        fs = all_origins_list[oi - 1]
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rs, rw, rd, rts = realized_inputs_for(weather_df, fs)
        
        runner = PlannerCFArmRunner(configs, arm, solar_provider)
        if k is not None:
            runner.forecast_engine = CandidateForecastEngineWrapper(runner.forecast_engine, k=k)
        
        # We wrap run_origin or instrument optimizer calls to capture EBR / terminal binding
        hourly, executed = runner.run_origin(oi, make_initial_state(t0), weather_df, rs, rw, rd, rts)
        hourly_all.extend(hourly)
        executed_all.extend(executed)

    return pd.DataFrame(hourly_all), pd.DataFrame(executed_all)


def compute_telemetry_metrics(hourly_df: pd.DataFrame, pc_ctrl_df: pd.DataFrame = None):
    fuel_L = float(hourly_df["diesel_fuel"].sum())
    on_hours = int((hourly_df["diesel_power"] > 1e-3).sum())
    
    starts = 0
    for oid, g in hourly_df.groupby("origin_id"):
        on = (g["diesel_power"].to_numpy() > 1e-3).astype(int)
        prev = np.concatenate(([0], on[:-1]))
        starts += int(np.sum((on == 1) & (prev == 0)))
        
    diesel_energy_kwh = float(hourly_df["diesel_power"].sum()) / 1000.0
    bat_charge_hours = int((hourly_df["battery_charge"] > 1e-3).sum())
    
    crit_total = float(hourly_df["critical_demand"].sum())
    r_cf = 100.0 * float(hourly_df["critical_served_first"].sum()) / crit_total
    r_p = 100.0 * float(hourly_df["critical_served_prop"].sum()) / crit_total
    
    if pc_ctrl_df is not None:
        crit_ctrl = float(pc_ctrl_df["critical_demand"].sum())
        r_cf_ctrl = 100.0 * float(pc_ctrl_df["critical_served_first"].sum()) / crit_ctrl
        r_p_ctrl = 100.0 * float(pc_ctrl_df["critical_served_prop"].sum()) / crit_ctrl
        s1_delta = r_cf - r_cf_ctrl
        s2_delta = r_p - r_p_ctrl
    else:
        s1_delta = 0.0
        s2_delta = 0.0

    soc_violations = int((hourly_df["soc_after"] < 20.0).sum())
    min_soc = float(hourly_df["soc_after"].min())
    
    crit_unmet = float((hourly_df["critical_demand"] - hourly_df["critical_served_first"]).sum())
    total_unmet = float(hourly_df["unmet_load"].sum())
    noncrit_unmet = total_unmet - crit_unmet
    curtailment = float(hourly_df["curtailment"].sum())

    return {
        "fuel_L": fuel_L,
        "diesel_on_hours": on_hours,
        "diesel_starts": starts,
        "diesel_energy_kwh": diesel_energy_kwh,
        "battery_charge_hours": bat_charge_hours,
        "s1_delta_pp": s1_delta,
        "s2_delta_pp": s2_delta,
        "soc_violations": soc_violations,
        "min_soc_pct": min_soc,
        "critical_unmet_wh": crit_unmet,
        "noncritical_unmet_wh": noncrit_unmet,
        "total_unmet_wh": total_unmet,
        "curtailment_wh": curtailment,
    }


if __name__ == "__main__":
    configs, make_initial_state = _load_canonical_configs()
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    solar_provider = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)

    print("--- Running PC-Control on 11 origins ---")
    ctrl_hourly, _ = run_arm_on_subset("PC-Control", ORIGIN_INDICES, configs, make_initial_state, weather_df, solar_provider)

    print("--- Running P0 (PC-SW v1.2 unchanged) on 11 origins ---")
    p0_hourly, _ = run_arm_on_subset("PC-SW", ORIGIN_INDICES, configs, make_initial_state, weather_df, solar_provider)

    p0_metrics = compute_telemetry_metrics(p0_hourly, ctrl_hourly)
    print("P0 Metrics:", json.dumps(p0_metrics, indent=2))
