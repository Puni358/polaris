import json
import math
from pathlib import Path

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
DEMO_PATH = BASE_DIR / "system" / "data" / "scenarios" / "demo_scenario.json"

def generate_demo_dataset():
    records = []
    # 48 hours starting 2024-06-01 00:00:00 UTC
    for t in range(48):
        day = t // 24
        hour = t % 24
        ts_str = f"2024-06-0{day+1}T{hour:02d}:00:00Z"
        
        # Diurnal solar cycle peaking at 12:00
        if 4 <= hour <= 20:
            solar_sin = math.sin((hour - 4) * math.pi / 16.0)
            clearsky_ghi = round(800.0 * solar_sin, 2)
            # Cloud attenuation factor
            cloud_factor = 0.85 if t < 24 else 0.60
            actual_SW_IN = round(clearsky_ghi * cloud_factor, 2)
        else:
            clearsky_ghi = 0.0
            actual_SW_IN = 0.0

        # Wind power profile with variability
        wind_gen = round(25000.0 + 15000.0 * math.sin(t * math.pi / 12.0) + 5000.0 * math.cos(t * math.pi / 6.0), 2)
        wind_gen = max(0.0, wind_gen)

        # Demand profile (morning peak 08:00, evening peak 19:00)
        base_demand = 35000.0
        diurnal_demand = 10000.0 * math.sin((hour - 6) * math.pi / 12.0) if 6 <= hour <= 22 else 0.0
        actual_demand = round(base_demand + max(0.0, diurnal_demand), 2)

        records.append({
            "timestep_index": t,
            "timestamp": ts_str,
            "actual_SW_IN": actual_SW_IN,
            "clearsky_ghi": clearsky_ghi,
            "actual_wind_generation": wind_gen,
            "actual_demand": actual_demand
        })

    payload = {
        "scenario_id": "sites_nuolja_demo_48h_scenario",
        "description": "Deterministic 48-hour offline demo evaluation dataset for POLARIS Phase D1",
        "status_label": "PROTOTYPE_DEMO_DATA",
        "total_timesteps": 48,
        "timesteps": records
    }

    DEMO_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEMO_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Generated demo scenario with 48 timesteps at {DEMO_PATH}")

if __name__ == "__main__":
    generate_demo_dataset()
