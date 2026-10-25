"""
Deterministic 168-Hour Synthetic Scenario Generator for POLARIS Phase D4
Generates synthetic_168h_endurance_scenario.json for closed-loop engineering endurance testing.
Classification: SYNTHETIC ENGINEERING TEST DATA
Research Firewall: 100% Offline, Zero Research Data Access, Seed = 42
"""
import json
import math
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone

def generate_synthetic_scenario(seed: int = 42) -> dict:
    random.seed(seed)
    
    start_dt = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
    duration_hours = 168
    
    timesteps = []
    
    # Cloud attenuation smooth random walk initial state
    cloud_attenuation = 0.85
    
    for t in range(duration_hours):
        dt = start_dt + timedelta(hours=t)
        timestamp_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        hour_of_day = dt.hour
        
        # 1. Synthetic Solar Irradiance & Clear-sky GHI Model
        # Daylight curve between 06:00 and 18:00
        if 6 <= hour_of_day <= 18:
            sun_angle = math.pi * (hour_of_day - 6) / 12.0
            clearsky_ghi = round(800.0 * math.sin(sun_angle), 2)
        else:
            clearsky_ghi = 0.0
            
        # Smooth random walk for cloud attenuation in [0.4, 1.0]
        step_delta = random.uniform(-0.08, 0.08)
        cloud_attenuation = max(0.40, min(1.00, cloud_attenuation + step_delta))
        
        actual_sw_in = round(clearsky_ghi * cloud_attenuation, 2)
        
        # 2. Synthetic Wind Generation Model (Diurnal + Synoptic Wave)
        wind_diurnal = 12500.0 * math.sin(2.0 * math.pi * t / 24.0)
        wind_synoptic = 7500.0 * math.cos(2.0 * math.pi * t / 72.0)
        wind_noise = random.uniform(-2000.0, 2000.0)
        actual_wind = round(max(0.0, min(50000.0, 25000.0 + wind_diurnal + wind_synoptic + wind_noise)), 2)
        
        # 3. Synthetic Demand Model (Double-peak diurnal load curve)
        morning_peak = 15000.0 * math.exp(-((hour_of_day - 8) ** 2) / 6.0)
        evening_peak = 12000.0 * math.exp(-((hour_of_day - 19) ** 2) / 8.0)
        demand_noise = random.uniform(-1000.0, 1000.0)
        actual_demand = round(max(15000.0, min(60000.0, 25000.0 + morning_peak + evening_peak + demand_noise)), 2)
        
        timesteps.append({
            "timestep_index": t,
            "timestamp": timestamp_str,
            "actual_SW_IN": actual_sw_in,
            "clearsky_ghi": clearsky_ghi,
            "actual_wind_generation": actual_wind,
            "actual_demand": actual_demand
        })
        
    scenario_data = {
        "scenario_id": "synthetic_168h_endurance_scenario",
        "description": "Deterministic 168-hour synthetic engineering endurance test fixture for POLARIS Phase D4",
        "status_label": "SYNTHETIC_ENGINEERING_TEST_DATA",
        "provenance_metadata": {
            "scenario_type": "synthetic",
            "real_station_data": False,
            "research_data_used": False,
            "generation_method": "deterministic_physics_wave_model",
            "generation_seed": seed,
            "duration_hours": duration_hours,
            "timestep_hours": 1.0
        },
        "total_timesteps": duration_hours,
        "timesteps": timesteps
    }
    
    return scenario_data

def main():
    script_dir = Path(__file__).resolve().parent
    system_dir = script_dir.parent
    target_path = system_dir / "data" / "scenarios" / "synthetic_168h_endurance_scenario.json"
    
    scenario = generate_synthetic_scenario(seed=42)
    
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w") as f:
        json.dump(scenario, f, indent=2)
        
    print(f"Successfully generated 168h synthetic scenario at: {target_path}")

if __name__ == "__main__":
    main()
