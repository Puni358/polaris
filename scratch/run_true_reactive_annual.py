#!/usr/bin/env python3
"""
POLARIS — True Reactive Annual Simulation (Real Solar Data, Zero Forecast, Greedy)
File: scratch/run_true_reactive_annual.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

def run_true_reactive_simulation():
    print("=" * 70)
    print("RUNNING TRUE REACTIVE BASELINE (REAL SOLAR, ZERO FORECAST)")
    print("=" * 70)
    
    # 1. Load Real Historical Solar & Clearsky Data
    csv_path = "data/POLARIS_v0_1_clearsky_decomposition.csv"
    if not Path(csv_path).exists():
        print(f"[FAIL] Could not locate dataset at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df):,} hourly records from {csv_path}")
    
    # System Parameters (Nuolja Station Specs)
    array_area_m2 = 300.0
    panel_efficiency = 0.20
    performance_ratio = 0.85
    max_inverter_power_w = 60000.0
    
    battery_capacity_wh = 200_000.0
    battery_energy_wh = 100_000.0  # Start at 50% SOC (100 kWh)
    min_energy_wh = 0.0          # Pure reactive: No minimum SOC safety floor
    max_energy_wh = 200_000.0
    eta_chg = 0.92
    eta_dis = 0.92
    max_power_w = 50_000.0       # Max battery charge/discharge power
    
    diesel_min_w = 10_000.0      # 10 kW minimum operating floor when active
    diesel_max_w = 100_000.0     # 100 kW generator capacity
    fuel_base_l_h = 5.0          # Base fuel burn liters/hour
    fuel_marginal_l_wh = 0.00025 # Marginal fuel burn per Watt-hour
    
    total_diesel_liters = 0.0
    total_unmet_load_wh = 0.0
    diesel_run_hours = 0
    curtailed_solar_wh = 0.0
    
    # 2. Iterate over every hourly step (True reactive loop)
    for idx, row in df.iterrows():
        # Real measured solar irradiance (W/m^2)
        actual_ghi = max(0.0, float(row.get('actual_SW_IN', 0.0)))
        
        # Convert GHI to PV Solar Generation (W)
        solar_gen_w = actual_ghi * array_area_m2 * panel_efficiency * performance_ratio
        solar_gen_w = min(solar_gen_w, max_inverter_power_w)
        
        # Synthetic baseline demand & wind typical of high-latitude polar stations
        hour = pd.to_datetime(row['TIMESTAMP']).hour
        demand_w = 30_000.0 + 5_000.0 * np.sin(hour * np.pi / 12.0)
        wind_gen_w = 15_000.0 + 10_000.0 * np.sin((idx % 24) * np.pi / 6.0)
        
        total_renewable_w = solar_gen_w + wind_gen_w
        net_load_w = demand_w - total_renewable_w
        
        diesel_w = 0.0
        
        if net_load_w > 0:
            # Deficit: Reactive controller tries discharging battery first
            # CORRECTED: Divide by eta_dis to account for internal conversion losses
            max_dis_possible_wh = (battery_energy_wh - min_energy_wh) / eta_dis
            dis_w = min(net_load_w, max_power_w, max_dis_possible_wh)
            
            battery_energy_wh -= (dis_w / eta_dis)
            remaining_deficit_w = net_load_w - dis_w
            
            if remaining_deficit_w > 0:
                # Battery can't cover it: Fire up Diesel immediately
                diesel_w = max(diesel_min_w, min(remaining_deficit_w, diesel_max_w))
                diesel_run_hours += 1
                
                # Fuel accounting (Liters consumed in this hour)
                fuel_l = fuel_base_l_h + (diesel_w * fuel_marginal_l_wh)
                total_diesel_liters += fuel_l
                
                # Check if even diesel couldn't meet load
                unmet_w = remaining_deficit_w - diesel_w
                if unmet_w > 0:
                    total_unmet_load_wh += unmet_w
                    
        else:
            # Surplus Renewable Energy Processing
            surplus_w = -net_load_w
            
            # Inverter Clipping: Anything exceeding the 50 kW inverter threshold is instantly lost
            inverter_clipped_w = max(0.0, surplus_w - max_power_w)
            net_surplus_after_inverter_w = min(surplus_w, max_power_w)
            
            # Battery Absorption
            max_chg_possible_wh = (max_energy_wh - battery_energy_wh) / eta_chg
            chg_w = min(net_surplus_after_inverter_w, max_chg_possible_wh)
            
            battery_energy_wh += (chg_w * eta_chg)
            
            # Battery Overflow: Any surplus remaining after max battery charge rate & capacity
            battery_unabsorbed_w = net_surplus_after_inverter_w - chg_w
            
            # Total hourly curtailment = Inverter Clipping + Battery Overflow
            curtailed_wh = inverter_clipped_w + battery_unabsorbed_w
            curtailed_solar_wh += curtailed_wh

    print("-" * 50)
    print(f"TRUE REACTIVE BASELINE ANNUAL RESULTS (CORRECTED):")
    print(f"  Total Diesel Consumed:   {total_diesel_liters:,.2f} Liters")
    print(f"  Diesel Run Hours:        {diesel_run_hours:,} hours")
    print(f"  Total Unmet Load:        {total_unmet_load_wh / 1000:,.2f} kWh")
    print(f"  Total Curtailed Energy:  {curtailed_solar_wh / 1000:,.2f} kWh")
    print("=" * 70)
    return total_diesel_liters

if __name__ == "__main__":
    run_true_reactive_simulation()
