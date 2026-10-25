#!/usr/bin/env python3
"""
POLARIS — Annual Receding-Horizon Control (RHC) Simulation Script with N6 & C.2 Pipeline
File: scratch/run_n6_rhc_annual.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
    from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
    from system.schemas.station_state import StationState
    from system.evaluation.n6_multi_origin_harness.adapters import _align_n6_bundle_od02
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    print("Ensure you run this script with: PYTHONPATH=$(pwd) python3 scratch/run_n6_rhc_annual.py")
    exit(1)

def build_timeseries(values, unit="W"):
    return TimeseriesForecast(
        point=values,
        lower=values,
        upper=values,
        unit=unit
    )

def run_n6_rhc_annual_simulation():
    print("=" * 80)
    print("POLARIS — ANNUAL N6 RHC PIPELINE SIMULATION (2024 DATASET)")
    print("=" * 80)
    
    csv_path = "data/POLARIS_v0_1_clearsky_decomposition.csv"
    if not Path(csv_path).exists():
        print(f"[FAIL] Could not locate dataset at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], utc=True)
    print(f"Loaded {len(df):,} hourly records from {csv_path}")
    
    optimizer = GAP19HighsNativeOptimizer()
    
    battery_energy_wh = 100_000.0  # Start at 50% SOC (100 kWh)
    total_diesel_liters = 0.0
    diesel_run_hours = 0
    
    horizon = 24
    max_steps = len(df) - horizon
    
    print(f"Starting closed-loop RHC simulation across {max_steps} steps...")
    
    for idx in range(max_steps):
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
        
        # Apply OD-02 C.2 adapter alignment
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
            batt_discharge_step0 = plan.battery_discharge[0] if hasattr(plan, 'battery_discharge') else 0.0
            batt_charge_step0 = plan.battery_charge[0] if hasattr(plan, 'battery_charge') else 0.0
            
            if diesel_w_step0 > 0:
                diesel_run_hours += 1
                fuel_l = 5.0 + (diesel_w_step0 * 0.00025)
                total_diesel_liters += fuel_l
                
            eta_chg, eta_dis = 0.92, 0.92
            battery_energy_wh += (batt_charge_step0 * eta_chg) - (batt_discharge_step0 / eta_dis)
            battery_energy_wh = max(0.0, min(200_000.0, battery_energy_wh))
            
        except Exception:
            pass
            
        if (idx + 1) % 1000 == 0:
            print(f"Processed {idx + 1} / {max_steps} steps... Current Diesel Burn: {total_diesel_liters:,.2f} L")
            
    print("=" * 80)
    print("ANNUAL N6 RHC PIPELINE SIMULATION RESULTS:")
    print(f"  Total Diesel Consumed:   {total_diesel_liters:,.2f} Liters")
    print(f"  Diesel Run Hours:        {diesel_run_hours:,} hours")
    print("=" * 80)

if __name__ == "__main__":
    run_n6_rhc_annual_simulation()
