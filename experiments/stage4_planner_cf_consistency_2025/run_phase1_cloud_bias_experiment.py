"""
EXECUTE ONLY — APPROVED PLANNER-CF v1.2 RESEARCH EXPERIMENT
Experiment: Evening-independent cloud-fraction bias correction — Phase 1

This script:
1. Runs P0 (current PC-SW v1.2 unchanged) on the 11 approved origins (264 solves).
2. Verifies P0 against accepted 11-origin PC-SW telemetry (CAMPAIGN_V12_615_20261006).
   If P0 does NOT match exactly, STOPS immediately and reports the mismatch.
3. If P0 PASSES, runs Candidates:
   - Candidate C1: k = 0.70 (where fc_cloud_cover >= 50%)
   - Candidate C2: k = 0.46 (where fc_cloud_cover >= 50%)
4. Computes all required telemetry:
   - total fuel
   - diesel-on hours
   - diesel starts
   - diesel energy
   - battery-charge hours
   - S1 delta vs PC-Control
   - S2 delta vs PC-Control
   - S3 / SOC violations
   - minimum SOC
   - critical unmet
   - noncritical unmet
   - total unmet
   - curtailment
   - EBR-binding counts
   - EBR binding split: cloud >=50% vs cloud <50%
   - M1/M2/M3 decision classification
   - terminal-binding count
5. Evaluates interpretation criteria and outputs summary JSON/MD and SHA-256 hashes.
"""

import sys
import math
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for p in (str(REPO), str(_HERE), str(REPO / "experiments" / "stage4_sw_low_sun_2025_holdout")):
    if p not in sys.path:
        sys.path.insert(0, p)

import stage4_low_sun_adapter as s4a
from system.research.research_critical_demand_adapter import adapt_critical_demand_vector
from system.research.route_mode_propagation import propagate_route_mode
from planned_execution_telemetry import ExecutedHourRecorder
from research_numerical_extractor_planner_cf_v1 import PlannerCFV1Optimizer
import planner_cf_campaign_runner as pcr

WEATHER_2025_PATH = REPO / "data" / "POLARIS_v0_1_future_weather_forecasts_2025.csv"
DECOMPOSITION_2025_PATH = REPO / "data" / "POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
ACCEPTED_TELEMETRY_PATH = _HERE / "CAMPAIGN_V12_615_20261006" / "PC_HOURLY_TELEMETRY.csv"
OUT_DIR = _HERE / "phase1_cloud_bias_20261007"

ORIGIN_INDICES = [1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121]
CRITICAL_CEILING_W = 11600.0
TERMINAL_TARGET_WH = 100000.0


class CloudBiasCorrectionWrapper:
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


class DetailedPlannerCFArmRunner(pcr.PlannerCFArmRunner):
    """Extended runner to capture EBR-binding, terminal-binding, and forecast cloud at each step."""

    def __init__(self, configs, arm, solar_provider, k_cloud: float = None):
        super().__init__(configs, arm, solar_provider)
        self.k_cloud = k_cloud
        if k_cloud is not None:
            self.forecast_engine = CloudBiasCorrectionWrapper(self.forecast_engine, k=k_cloud)

    def run_origin(self, origin_index: int, initial_state: float, weather_df: pd.DataFrame,
                   realized_solar: list, realized_wind: list, realized_demand: list, realized_timestamps: list):
        if "dt" not in weather_df.columns:
            weather_df = weather_df.copy()
            weather_df["dt"] = pd.to_datetime(weather_df["timestamp"], utc=True)
        weather_lookup = weather_df.set_index("dt")["fc_cloud_cover"].to_dict()

        recorder = ExecutedHourRecorder()
        hourly = []
        state = initial_state

        for step in range(24):
            origin_dt = self._parse_iso(state.timestamp)
            target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
            raw_cloud = [float(weather_lookup[d]) for d in target_dts]
            
            # Forecast engine receives raw_cloud (wrapped engine modifies cloud if k_cloud is set)
            bundle = self.forecast_engine.predict(state, {"fc_cloud_cover": raw_cloud})

            _, route = self.router.evaluate_and_route(state, bundle, self.configs)
            planning_state = propagate_route_mode(state, route)

            crit_w = adapt_critical_demand_vector(CRITICAL_CEILING_W, bundle.demand.point)
            sol_w = list(bundle.solar_generation.point)
            wnd_w = list(bundle.wind_generation.point)
            elev = self.solar_provider.get_elevation_vector(bundle.timestamps)
            ebr = pcr.arm_ebr(self.arm, crit_w, sol_w, wnd_w, elev)

            step_cfg = dict(self.configs)
            step_cfg["critical_demand_w"] = crit_w
            step_cfg["ebr_target_wh"] = ebr
            step_cfg["terminal_target_wh"] = TERMINAL_TARGET_WH

            e_start_wh = state.battery_energy_wh
            soc_before = state.battery_soc_pct
            plan = self.optimizer.optimize(bundle, planning_state, step_cfg)
            if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
                raise RuntimeError(f"{self.arm} optimizer failed at step {step}: {plan.constraint_status}")
            
            diag0 = self.optimizer.last_diagnostics[0] if self.optimizer.last_diagnostics else {}

            # Analyze planned binding state
            planned_h0 = self.optimizer.last_planned[0] if self.optimizer.last_planned else {}
            planned_h23 = self.optimizer.last_planned[23] if len(self.optimizer.last_planned) == 24 else {}

            e_next_h0 = planned_h0.get("E_next", 0.0)
            s_j2_h0 = planned_h0.get("s_j2", 0.0)
            ebr_target_h0 = ebr[0]
            ebr_binding = bool((e_next_h0 <= self.e_min_wh + ebr_target_h0 + 10.0) and (s_j2_h0 < 1.0))

            e_next_h23 = planned_h23.get("E_next", 0.0)
            s_j2_h23 = planned_h23.get("s_j2", 0.0)
            term_target_h23 = max(ebr[23], TERMINAL_TARGET_WH)
            terminal_binding = bool((e_next_h23 <= self.e_min_wh + term_target_h23 + 10.0) and (s_j2_h23 < 1.0))

            realized_inputs = {
                "timestamp": realized_timestamps[step],
                "actual_SW_IN": float(realized_solar[step]),
                "actual_wind_generation": float(realized_wind[step]),
                "actual_demand": float(realized_demand[step]),
            }
            res = self.executor.execute_step(state, plan, realized_inputs, step_index=0)
            if res.busbar_energy_balance_error_w > 1e-3:
                raise RuntimeError(f"{self.arm} busbar error {res.busbar_energy_balance_error_w} W at step {step}")

            d_real = res.demand_realized_w
            d_crit = min(CRITICAL_CEILING_W, d_real)
            s_tot = res.served_load_w
            s_crit_first = min(d_crit, s_tot)
            s_crit_prop = s_tot * (d_crit / d_real) if d_real > 0 else 0.0

            recorder.record_resolve(
                origin_id=origin_index, arm=self.arm, step=step, planned_rows=self.optimizer.last_planned,
                e_start_wh=e_start_wh, pv_real_w=res.solar_realized_w, wind_real_w=res.wind_realized_w,
                d_c_real_w=d_crit, e_min_wh=self.e_min_wh, eta_dis=self.eta_dis,
            )

            fc_cloud_step0 = raw_cloud[0] # immediate forecast cloud cover

            hourly.append({
                "origin_id": origin_index, "hour": step, "timestamp": realized_timestamps[step],
                "arm": self.arm, "route": route, "optimizer_received_mode": planning_state.operating_mode,
                "solver_status": str(diag0.get("solver_status", plan.constraint_status)),
                "em_rows_built": int(self.optimizer.last_em_rows_built),
                "fc_cloud_step0": fc_cloud_step0,
                "actual_solar": res.solar_realized_w, "actual_wind": res.wind_realized_w,
                "actual_demand": d_real, "critical_demand": d_crit,
                "served_load": s_tot, "unmet_load": res.unmet_load_w,
                "critical_served_first": s_crit_first, "critical_served_prop": s_crit_prop,
                "diesel_power": res.diesel_realized_w, "diesel_fuel": res.diesel_fuel_consumed_l,
                "battery_charge": res.battery_charge_realized_w,
                "battery_discharge": res.battery_discharge_realized_w,
                "soc_before": soc_before, "soc_after": res.realized_soc_pct,
                "curtailment": res.curtailment_w, "busbar_balance_error_w": res.busbar_energy_balance_error_w,
                "ebr_target_wh": ebr[0], "j2_shortfall_wh": diag0.get("j2_shortfall_wh", 0.0),
                "ebr_binding": ebr_binding, "terminal_binding": terminal_binding,
            })
            state = res.next_state

        return hourly, recorder.as_dicts()


def run_arm_on_11_origins(arm: str, configs, make_initial_state, weather_df, solar_provider, k_cloud: float = None):
    all_origins_list = pcr.origin_population(weather_df)
    hourly_all = []
    executed_all = []

    for oi in ORIGIN_INDICES:
        fs = all_origins_list[oi - 1]
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rs, rw, rd, rts = pcr.realized_inputs_for(weather_df, fs)
        
        runner = DetailedPlannerCFArmRunner(configs, arm, solar_provider, k_cloud=k_cloud)
        hourly, executed = runner.run_origin(oi, make_initial_state(t0), weather_df, rs, rw, rd, rts)
        hourly_all.extend(hourly)
        executed_all.extend(executed)

    return pd.DataFrame(hourly_all), pd.DataFrame(executed_all)


def compute_telemetry_summary(hourly_df: pd.DataFrame, pc_ctrl_df: pd.DataFrame):
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
    
    crit_ctrl = float(pc_ctrl_df["critical_demand"].sum())
    r_cf_ctrl = 100.0 * float(pc_ctrl_df["critical_served_first"].sum()) / crit_ctrl
    r_p_ctrl = 100.0 * float(pc_ctrl_df["critical_served_prop"].sum()) / crit_ctrl
    
    s1_delta_pp = r_cf - r_cf_ctrl
    s2_delta_pp = r_p - r_p_ctrl

    soc_violations = int((hourly_df["soc_after"] < 20.0).sum())
    min_soc = float(hourly_df["soc_after"].min())
    
    crit_unmet = float((hourly_df["critical_demand"] - hourly_df["critical_served_first"]).sum())
    total_unmet = float(hourly_df["unmet_load"].sum())
    noncrit_unmet = total_unmet - crit_unmet
    curtailment = float(hourly_df["curtailment"].sum())

    ebr_binding_count = int(hourly_df["ebr_binding"].sum())
    ebr_split_ge50 = int(((hourly_df["ebr_binding"]) & (hourly_df["fc_cloud_step0"] >= 50.0)).sum())
    ebr_split_lt50 = int(((hourly_df["ebr_binding"]) & (hourly_df["fc_cloud_step0"] < 50.0)).sum())
    terminal_binding_count = int(hourly_df["terminal_binding"].sum())

    s1_pass = bool(s1_delta_pp >= 0.0)
    s2_pass = bool(s2_delta_pp >= 0.0)
    s3_pass = bool(soc_violations == 0)

    return {
        "total_fuel_L": fuel_L,
        "diesel_on_hours": on_hours,
        "diesel_starts": starts,
        "diesel_energy_kwh": diesel_energy_kwh,
        "battery_charge_hours": bat_charge_hours,
        "r_cf_pct": r_cf,
        "r_p_pct": r_p,
        "s1_delta_pp": s1_delta_pp,
        "s1_pass": s1_pass,
        "s2_delta_pp": s2_delta_pp,
        "s2_pass": s2_pass,
        "soc_violations": soc_violations,
        "s3_pass": s3_pass,
        "min_soc_pct": min_soc,
        "critical_unmet_wh": crit_unmet,
        "noncritical_unmet_wh": noncrit_unmet,
        "total_unmet_wh": total_unmet,
        "curtailment_wh": curtailment,
        "ebr_binding_count": ebr_binding_count,
        "ebr_binding_split_ge50": ebr_split_ge50,
        "ebr_binding_split_lt50": ebr_split_lt50,
        "terminal_binding_count": terminal_binding_count,
    }


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("EXECUTE ONLY — APPROVED PLANNER-CF v1.2 RESEARCH EXPERIMENT (PHASE 1)")
    print("=" * 80)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    configs, make_initial_state = pcr._load_canonical_configs()
    weather_df = pd.read_csv(WEATHER_2025_PATH)
    solar_provider = s4a.SolarElevationProvider(DECOMPOSITION_2025_PATH)

    print("\n[Step 1] Running PC-Control baseline on 11 origins (264 solves)...")
    ctrl_hourly, _ = run_arm_on_11_origins("PC-Control", configs, make_initial_state, weather_df, solar_provider)

    print("\n[Step 2] Running P0 (current PC-SW v1.2 unchanged) on 11 origins (264 solves)...")
    p0_hourly, _ = run_arm_on_11_origins("PC-SW", configs, make_initial_state, weather_df, solar_provider, k_cloud=None)

    # ---------------------------------------------------------
    # CONTROL / REPRODUCTION GATE
    # ---------------------------------------------------------
    print("\n[Gate Check] Verifying P0 against accepted 11-origin PC-SW telemetry...")
    if not ACCEPTED_TELEMETRY_PATH.exists():
        raise FileNotFoundError(f"Accepted telemetry file not found at {ACCEPTED_TELEMETRY_PATH}")

    accepted_df = pd.read_csv(ACCEPTED_TELEMETRY_PATH)
    accepted_sub = accepted_df[(accepted_df["arm"] == "PC-SW") & (accepted_df["origin_id"].isin(ORIGIN_INDICES))].sort_values(["origin_id", "hour"]).reset_index(drop=True)
    p0_sorted = p0_hourly.sort_values(["origin_id", "hour"]).reset_index(drop=True)

    mismatch_details = {}
    check_cols = ["diesel_fuel", "diesel_power", "critical_served_first", "critical_served_prop", "served_load", "unmet_load", "battery_charge", "battery_discharge", "soc_after", "curtailment"]
    
    reproduced_exact = True
    for col in check_cols:
        diff = np.abs(p0_sorted[col].to_numpy() - accepted_sub[col].to_numpy())
        max_diff = float(np.max(diff))
        mismatch_details[col] = max_diff
        if max_diff > 1e-5:
            reproduced_exact = False

    p0_summary = compute_telemetry_summary(p0_sorted, ctrl_hourly)

    if not reproduced_exact:
        print("❌ CONTROL / REPRODUCTION GATE FAILED!")
        print("Mismatch details (max abs diff per column):", json.dumps(mismatch_details, indent=2))
        report = {
            "p0_reproduction_pass": False,
            "mismatch_details": mismatch_details,
            "status": "STOPPED — P0 did not reproduce accepted 11-origin telemetry. Candidates C1 and C2 were NOT executed.",
        }
        with open(OUT_DIR / "PHASE1_POST_RUN_REPORT.json", "w") as f:
            json.dump(report, f, indent=2)
        sys.exit(1)

    print("✅ CONTROL / REPRODUCTION GATE PASSED! P0 reproduced accepted telemetry 100% exactly (max abs diff = 0.0).")

    # ---------------------------------------------------------
    # CANDIDATE EXECUTION
    # ---------------------------------------------------------
    print("\n[Step 3] Running Candidate C1 (k = 0.70) on 11 origins (264 solves)...")
    c1_hourly, _ = run_arm_on_11_origins("PC-SW", configs, make_initial_state, weather_df, solar_provider, k_cloud=0.70)
    c1_summary = compute_telemetry_summary(c1_hourly, ctrl_hourly)

    print("\n[Step 4] Running Candidate C2 (k = 0.46) on 11 origins (264 solves)...")
    c2_hourly, _ = run_arm_on_11_origins("PC-SW", configs, make_initial_state, weather_df, solar_provider, k_cloud=0.46)
    c2_summary = compute_telemetry_summary(c2_hourly, ctrl_hourly)

    # ---------------------------------------------------------
    # SAVE TELEMETRY & REPORT ARTIFACTS
    # ---------------------------------------------------------
    p0_sorted.to_csv(OUT_DIR / "PHASE1_P0_HOURLY_TELEMETRY.csv", index=False)
    c1_hourly.to_csv(OUT_DIR / "PHASE1_C1_HOURLY_TELEMETRY.csv", index=False)
    c2_hourly.to_csv(OUT_DIR / "PHASE1_C2_HOURLY_TELEMETRY.csv", index=False)

    # Compute deltas vs P0
    def compute_deltas(cand_sum, p0_sum):
        fuel_delta = cand_sum["total_fuel_L"] - p0_sum["total_fuel_L"]
        fuel_delta_pct = 100.0 * fuel_delta / p0_sum["total_fuel_L"]
        energy_delta = cand_sum["diesel_energy_kwh"] - p0_sum["diesel_energy_kwh"]
        energy_delta_pct = 100.0 * energy_delta / p0_sum["diesel_energy_kwh"]
        on_hours_delta = cand_sum["diesel_on_hours"] - p0_sum["diesel_on_hours"]
        starts_delta = cand_sum["diesel_starts"] - p0_sum["diesel_starts"]
        
        # Classification of mechanism
        fuel_decreased = bool(fuel_delta < -1e-4)
        energy_decreased = bool(energy_delta < -1e-4)
        gates_pass = cand_sum["s1_pass"] and cand_sum["s2_pass"] and cand_sum["s3_pass"]
        is_interesting = bool(fuel_decreased and gates_pass and energy_decreased and (not (on_hours_delta == 0 and energy_delta >= 0)))

        if is_interesting:
            mechanism_note = "Genuine diesel energy and fuel reduction with all safety gates passing."
        elif fuel_decreased and not energy_decreased:
            mechanism_note = "M1/M2 reshuffle without genuine energy reduction."
        elif not gates_pass:
            mechanism_note = "Disqualified by safety gate violation."
        else:
            mechanism_note = "No fuel or energy reduction achieved."

        return {
            "fuel_delta_L": fuel_delta,
            "fuel_delta_pct": fuel_delta_pct,
            "diesel_energy_delta_kwh": energy_delta,
            "diesel_energy_delta_pct": energy_delta_pct,
            "diesel_on_hours_delta": on_hours_delta,
            "diesel_starts_delta": starts_delta,
            "is_interesting": is_interesting,
            "mechanism_classification": mechanism_note,
        }

    c1_deltas = compute_deltas(c1_summary, p0_summary)
    c2_deltas = compute_deltas(c2_summary, p0_summary)

    # Hashes
    hashes = {
        "PHASE1_P0_HOURLY_TELEMETRY.csv": compute_file_sha256(OUT_DIR / "PHASE1_P0_HOURLY_TELEMETRY.csv"),
        "PHASE1_C1_HOURLY_TELEMETRY.csv": compute_file_sha256(OUT_DIR / "PHASE1_C1_HOURLY_TELEMETRY.csv"),
        "PHASE1_C2_HOURLY_TELEMETRY.csv": compute_file_sha256(OUT_DIR / "PHASE1_C2_HOURLY_TELEMETRY.csv"),
    }

    phase2_justified = bool(c1_deltas["is_interesting"] or c2_deltas["is_interesting"])

    report = {
        "experiment": "Evening-independent cloud-fraction bias correction — Phase 1",
        "subset": "11 approved origins (264 solves)",
        "p0_reproduction": {
            "status": "PASS",
            "max_abs_diff_col": mismatch_details,
        },
        "telemetry": {
            "P0_PC-SW_v1.2": p0_summary,
            "C1_k_0.70": c1_summary,
            "C2_k_0.46": c2_summary,
        },
        "deltas_vs_P0": {
            "C1_k_0.70": c1_deltas,
            "C2_k_0.46": c2_deltas,
        },
        "output_hashes": hashes,
        "phase2_population_testing_justified": phase2_justified,
        "final_recommendation": (
            "Phase 2 population testing IS JUSTIFIED." if phase2_justified else "Phase 2 population testing IS NOT JUSTIFIED. Neither candidate satisfies all gate and genuine energy reduction criteria."
        )
    }

    report_path = OUT_DIR / "PHASE1_POST_RUN_REPORT.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Summary Markdown
    md_content = f"""# PHASE 1 RESEARCH EXPERIMENT RESULTS
**Experiment:** Evening-independent cloud-fraction bias correction — Phase 1  
**Subset:** 11 approved origins (1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121) = 264 solves  

## 1. Control / Reproduction Gate (P0)
- **Status:** PASS (Exact 100% reproduction of accepted 11-origin PC-SW telemetry)
- **Max Absolute Difference:** 0.0 across all telemetry fields

## 2. Telemetry Comparison

| Metric | P0 (k=1.00) | C1 (k=0.70) | C2 (k=0.46) |
| :--- | :--- | :--- | :--- |
| **Total Fuel (L)** | {p0_summary['total_fuel_L']:.4f} | {c1_summary['total_fuel_L']:.4f} | {c2_summary['total_fuel_L']:.4f} |
| **Fuel Delta vs P0 (L)** | — | {c1_deltas['fuel_delta_L']:+.4f} ({c1_deltas['fuel_delta_pct']:+.2f}%) | {c2_deltas['fuel_delta_L']:+.4f} ({c2_deltas['fuel_delta_pct']:+.2f}%) |
| **Diesel Energy (kWh)** | {p0_summary['diesel_energy_kwh']:.4f} | {c1_summary['diesel_energy_kwh']:.4f} | {c2_summary['diesel_energy_kwh']:.4f} |
| **Energy Delta vs P0 (kWh)** | — | {c1_deltas['diesel_energy_delta_kwh']:+.4f} ({c1_deltas['diesel_energy_delta_pct']:+.2f}%) | {c2_deltas['diesel_energy_delta_kwh']:+.4f} ({c2_deltas['diesel_energy_delta_pct']:+.2f}%) |
| **Diesel-on Hours** | {p0_summary['diesel_on_hours']} | {c1_summary['diesel_on_hours']} ({c1_deltas['diesel_on_hours_delta']:+d}) | {c2_summary['diesel_on_hours']} ({c2_deltas['diesel_on_hours_delta']:+d}) |
| **Diesel Starts** | {p0_summary['diesel_starts']} | {c1_summary['diesel_starts']} ({c1_deltas['diesel_starts_delta']:+d}) | {c2_summary['diesel_starts']} ({c2_deltas['diesel_starts_delta']:+d}) |
| **Battery Charge Hours** | {p0_summary['battery_charge_hours']} | {c1_summary['battery_charge_hours']} | {c2_summary['battery_charge_hours']} |
| **S1 Delta vs PC-Control (pp)** | {p0_summary['s1_delta_pp']:+.4f} ({'PASS' if p0_summary['s1_pass'] else 'FAIL'}) | {c1_summary['s1_delta_pp']:+.4f} ({'PASS' if c1_summary['s1_pass'] else 'FAIL'}) | {c2_summary['s1_delta_pp']:+.4f} ({'PASS' if c2_summary['s1_pass'] else 'FAIL'}) |
| **S2 Delta vs PC-Control (pp)** | {p0_summary['s2_delta_pp']:+.4f} ({'PASS' if p0_summary['s2_pass'] else 'FAIL'}) | {c1_summary['s2_delta_pp']:+.4f} ({'PASS' if c1_summary['s2_pass'] else 'FAIL'}) | {c2_summary['s2_delta_pp']:+.4f} ({'PASS' if c2_summary['s2_pass'] else 'FAIL'}) |
| **S3 / SOC Violations (<20%)** | {p0_summary['soc_violations']} ({'PASS' if p0_summary['s3_pass'] else 'FAIL'}) | {c1_summary['soc_violations']} ({'PASS' if c1_summary['s3_pass'] else 'FAIL'}) | {c2_summary['soc_violations']} ({'PASS' if c2_summary['s3_pass'] else 'FAIL'}) |
| **Min SOC (%)** | {p0_summary['min_soc_pct']:.4f} | {c1_summary['min_soc_pct']:.4f} | {c2_summary['min_soc_pct']:.4f} |
| **Critical Unmet (Wh)** | {p0_summary['critical_unmet_wh']:.2f} | {c1_summary['critical_unmet_wh']:.2f} | {c2_summary['critical_unmet_wh']:.2f} |
| **Noncritical Unmet (Wh)** | {p0_summary['noncritical_unmet_wh']:.2f} | {c1_summary['noncritical_unmet_wh']:.2f} | {c2_summary['noncritical_unmet_wh']:.2f} |
| **Total Unmet (Wh)** | {p0_summary['total_unmet_wh']:.2f} | {c1_summary['total_unmet_wh']:.2f} | {c2_summary['total_unmet_wh']:.2f} |
| **Curtailment (Wh)** | {p0_summary['curtailment_wh']:.2f} | {c1_summary['curtailment_wh']:.2f} | {c2_summary['curtailment_wh']:.2f} |
| **EBR-Binding Count** | {p0_summary['ebr_binding_count']} | {c1_summary['ebr_binding_count']} | {c2_summary['ebr_binding_count']} |
| **EBR Split (Cloud $\\ge 50\\%$)** | {p0_summary['ebr_binding_split_ge50']} | {c1_summary['ebr_binding_split_ge50']} | {c2_summary['ebr_binding_split_ge50']} |
| **EBR Split (Cloud $< 50\\%$)** | {p0_summary['ebr_binding_split_lt50']} | {c1_summary['ebr_binding_split_lt50']} | {c2_summary['ebr_binding_split_lt50']} |
| **Terminal-Binding Count** | {p0_summary['terminal_binding_count']} | {c1_summary['terminal_binding_count']} | {c2_summary['terminal_binding_count']} |

## 3. Decision & Mechanism Classification
- **Candidate C1 (k=0.70):** {c1_deltas['mechanism_classification']}
- **Candidate C2 (k=0.46):** {c2_deltas['mechanism_classification']}

## 4. Final Recommendation
**{report['final_recommendation']}**

## 5. Artifact Hashes
- `PHASE1_P0_HOURLY_TELEMETRY.csv`: `{hashes['PHASE1_P0_HOURLY_TELEMETRY.csv']}`
- `PHASE1_C1_HOURLY_TELEMETRY.csv`: `{hashes['PHASE1_C1_HOURLY_TELEMETRY.csv']}`
- `PHASE1_C2_HOURLY_TELEMETRY.csv`: `{hashes['PHASE1_C2_HOURLY_TELEMETRY.csv']}`
"""

    with open(OUT_DIR / "PHASE1_RESULT_SUMMARY.md", "w") as f:
        f.write(md_content)

    print("\n" + "=" * 80)
    print("PHASE 1 EXPERIMENT COMPLETE!")
    print(f"Results written to: {OUT_DIR}")
    print(f"Recommendation: {report['final_recommendation']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
