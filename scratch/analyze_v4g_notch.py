import csv
import numpy as np
from pathlib import Path

raw_csv_path = Path("ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv")

with open(raw_csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Analyze timestep-level diesel commitment distribution (mpc_timestep_idx 0..23)
commit_v4g_by_k = np.zeros(24)
commit_v3_by_k = np.zeros(24)
commit_ctrl_by_k = np.zeros(24)

curtail_v4g_by_k = np.zeros(24)
curtail_v3_by_k = np.zeros(24)
curtail_ctrl_by_k = np.zeros(24)

fuel_inc_v4g_by_k = np.zeros(24)
fuel_inc_v3_by_k = np.zeros(24)
fuel_inc_ctrl_by_k = np.zeros(24)

for r in rows:
    k = int(r["mpc_timestep_idx"])
    commit_v4g_by_k[k] += float(r["diesel_commitment"])
    commit_v3_by_k[k] += float(r["v3_diesel_commitment"])
    commit_ctrl_by_k[k] += float(r["ctrl_diesel_commitment"])
    
    curtail_v4g_by_k[k] += float(r["h1_renewable_curtailment"])
    curtail_v3_by_k[k] += float(r["v3_h1_renewable_curtailment"])
    curtail_ctrl_by_k[k] += float(r["ctrl_h1_renewable_curtailment"])
    
    # Calculate fuel increment at step k
    fuel_after_v4g = float(r["cumulative_diesel_fuel_after"])
    fuel_before_v4g = float(r["cumulative_diesel_fuel_before"])
    fuel_inc_v4g_by_k[k] += max(0.0, fuel_after_v4g - fuel_before_v4g)
    
    fuel_after_v3 = float(r["v3_cumulative_diesel_fuel_after"])
    fuel_after_ctrl = float(r["ctrl_cumulative_diesel_fuel_after"])

print("--- Commitment Steps by MPC Timestep Index k (0..23) ---")
print("k\tControl\t\tV3 Ref\t\tV4.G Cand\tV4G - V3")
for k in range(24):
    print(f"{k}\t{commit_ctrl_by_k[k]:.0f}\t\t{commit_v3_by_k[k]:.0f}\t\t{commit_v4g_by_k[k]:.0f}\t\t{commit_v4g_by_k[k] - commit_v3_by_k[k]:+.0f}")

print("\n--- Renewable Curtailment (kWh) by MPC Timestep Index k (0..23) ---")
print("k\tControl (kWh)\tV3 Ref (kWh)\tV4.G Cand (kWh)\tV4G - V3")
for k in range(24):
    print(f"{k}\t{curtail_ctrl_by_k[k]:.2f}\t\t{curtail_v3_by_k[k]:.2f}\t\t{curtail_v4g_by_k[k]:.2f}\t\t{curtail_v4g_by_k[k] - curtail_v3_by_k[k]:+.2f}")
