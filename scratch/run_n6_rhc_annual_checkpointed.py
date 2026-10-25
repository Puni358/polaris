#!/usr/bin/env python3
"""
POLARIS — Annual N6 RHC Simulation with Checkpointing, Logging, ETA, and Vectorized Noise Filtering
File: scratch/run_n6_rhc_annual_checkpointed.py
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import pandas as pd
import numpy as np

try:
    from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
    from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
    from system.schemas.station_state import StationState
    from system.evaluation.n6_multi_origin_harness.adapters import _align_n6_bundle_od02
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    print("Ensure you run this script with: PYTHONPATH=$(pwd) python3 scratch/run_n6_rhc_annual_checkpointed.py")
    sys.exit(1)

# Configure Logging (Console + File)
LOG_DIR = Path("scratch")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "annual_n6_rhc_comparison.log"
CHECKPOINT_FILE = LOG_DIR / "rhc_checkpoint.json"
RESULTS_FILE = LOG_DIR / "n6_rhc_annual_results.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler(sys.stdout)
    ]
)

def build_timeseries(values, unit="W"):
    return TimeseriesForecast(
        point=values,
        lower=values,
        upper=values,
        unit=unit
    )

def run_checkpointed_n6_simulation():
    logging.info("=" * 80)
    logging.info("POLARIS — ANNUAL CHECKPOINTED N6 RHC PIPELINE SIMULATION (2024 DATASET)")
    logging.info("=" * 80)
    
    csv_path = "data/POLARIS_v0_1_clearsky_decomposition.csv"
    if not Path(csv_path).exists():
        logging.error(f"Could not locate dataset at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], utc=True)
    total_records = len(df)
    horizon = 24
    max_steps = total_records - horizon
    
    optimizer = GAP19HighsNativeOptimizer()
    
    # State variables (Defaults)
    start_idx = 0
    total_diesel_liters = 0.0
    diesel_run_hours = 0
    battery_energy_wh = 100_000.0  # 50% SOC start
    
    # Load Checkpoint if exists
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                ckpt = json.load(f)
                start_idx = ckpt.get("last_idx", 0) + 1
                total_diesel_liters = ckpt.get("total_diesel_liters", 0.0)
                diesel_run_hours = ckpt.get("diesel_run_hours", 0)
                battery_energy_wh = ckpt.get("battery_energy_wh", 100_000.0)
                logging.info(f"[RESUME] Checkpoint loaded successfully! Resuming from step {start_idx}/{max_steps}")
        except Exception as e:
            logging.warning(f"[WARN] Failed to load checkpoint: {e}. Starting from scratch.")
            
    logging.info(f"Simulation span: steps {start_idx} to {max_steps} ({max_steps - start_idx} steps remaining)")
    
    start_time = time.time()
    
    for idx in range(start_idx, max_steps):
        row = df.iloc[idx]
        origin_dt = row['TIMESTAMP']
        origin_str = origin_dt.isoformat()
        
        window_df = df.iloc[idx : idx + horizon]
        timestamps = [ts.isoformat() for ts in window_df['TIMESTAMP']]
        solar_ghi = window_df['actual_SW_IN'].fillna(0.0).values.tolist()
        
        array_area_m2 = 300.0
        panel_efficiency = 0.20
        performance_ratio = 0.85
        solar_gen = [max(0.0, g * array_area_m2 * panel_efficiency * performance_ratio) for g in solar_ghi]
        
        demand_w = [30_000.0 + 5_000.0 * np.sin((origin_dt.hour + h) * np.pi / 12.0) for h in range(horizon)]
        wind_w = [15_000.0 + 10_000.0 * np.sin(((idx + h) % 24) * np.pi / 6.0) for h in range(horizon)]
        critical_demand_w = [15_000.0] * horizon
        
        raw_solar_irradiance = [ghi * 0.8 for ghi in solar_ghi]
        
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin_str,
            horizon_hours=horizon,
            timestamps=timestamps,
            solar_irradiance=build_timeseries(raw_solar_irradiance, "W/m^2"),
            solar_generation=build_timeseries(solar_gen, "W"),
            wind_generation=build_timeseries(wind_w, "W"),
            demand=build_timeseries(demand_w, "W"),
            demand_critical=build_timeseries(critical_demand_w, "W"),
            metadata={"source": "annual_simulation"}
        )
        
        aligned_bundle = _align_n6_bundle_od02(bundle)
        
        station_state = StationState(
            timestamp=origin_str,
            battery_soc_pct=(battery_energy_wh / 200_000.0) * 100.0,
            battery_energy_wh=battery_energy_wh,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=solar_ghi[0],
            last_observed_demand=demand_w[0],
            last_observed_wind_generation=wind_w[0],
            operating_mode='NORMAL'
        )
        
        config = {
            "operating_mode": "NORMAL",
            "battery": {"capacity_wh": 200_000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
            "diesel": {"min_power_w": 10_000.0, "max_power_w": 100_000.0},
            "terminal_reserve_model": "INITIAL_STATE",
            "optimizer": {"timestep_hours": 1.0}
        }
        
        try:
            plan = optimizer.optimize(forecast_bundle=aligned_bundle, station_state=station_state, config=config)
            
            diesel_w_step0 = plan.diesel_power[0] if hasattr(plan, 'diesel_power') else 0.0
            
            # Vectorized cleaning: Extract full arrays and scrub micro-residuals (< 1.0W) across all steps
            batt_charge_arr = np.array(plan.battery_charge) if hasattr(plan, 'battery_charge') else np.zeros(24)
            batt_discharge_arr = np.array(plan.battery_discharge) if hasattr(plan, 'battery_discharge') else np.zeros(24)
            
            batt_charge_arr[batt_charge_arr < 1.0] = 0.0
            batt_discharge_arr[batt_discharge_arr < 1.0] = 0.0
            
            batt_charge_step0 = batt_charge_arr[0]
            batt_discharge_step0 = batt_discharge_arr[0]
            
            if diesel_w_step0 > 0:
                diesel_run_hours += 1
                fuel_l = 5.0 + (diesel_w_step0 * 0.00025)
                total_diesel_liters += fuel_l
                
            eta_chg, eta_dis = 0.92, 0.92
            battery_energy_wh += (batt_charge_step0 * eta_chg) - (batt_discharge_step0 / eta_dis)
            battery_energy_wh = max(0.0, min(200_000.0, battery_energy_wh))
            
        except Exception as e:
            logging.error(f"[ERROR] Optimization failed at step {idx} ({origin_str}): {e}")
            
        # Periodic Logging & Checkpointing (every 50 steps)
        if (idx + 1) % 50 == 0 or (idx + 1) == max_steps:
            elapsed = time.time() - start_time
            steps_done = (idx + 1) - start_idx
            avg_time_per_step = elapsed / max(1, steps_done)
            remaining_steps = max_steps - (idx + 1)
            eta_seconds = remaining_steps * avg_time_per_step
            
            logging.info(
                f"Progress: {idx + 1} / {max_steps} hours ({(idx + 1)/max_steps*100:.1f}%) | "
                f"Diesel Burn: {total_diesel_liters:,.2f} L | Run Hours: {diesel_run_hours:,} | "
                f"ETA: {eta_seconds/60:.1f} min"
            )
            
            # Save Checkpoint
            checkpoint_data = {
                "last_idx": idx,
                "total_diesel_liters": total_diesel_liters,
                "diesel_run_hours": diesel_run_hours,
                "battery_energy_wh": battery_energy_wh
            }
            with open(CHECKPOINT_FILE, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
                
    # Final Results Export
    final_results = {
        "pipeline": "POLARIS_N6_RHC_C2",
        "total_diesel_consumed_liters": total_diesel_liters,
        "diesel_run_hours": diesel_run_hours,
        "total_steps_executed": max_steps
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(final_results, f, indent=2)
        
    logging.info("=" * 80)
    logging.info("ANNUAL N6 RHC PIPELINE SIMULATION COMPLETED SUCCESSFULLY:")
    logging.info(f"  Total Diesel Consumed:   {total_diesel_liters:,.2f} Liters")
    logging.info(f"  Diesel Run Hours:        {diesel_run_hours:,} hours")
    logging.info(f"  Results saved to:        {RESULTS_FILE}")
    logging.info("=" * 80)
    
    # Cleanup checkpoint on successful completion
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

if __name__ == "__main__":
    run_checkpointed_n6_simulation()
