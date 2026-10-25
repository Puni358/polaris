import csv
import json
import math
import numpy as np
from pathlib import Path

raw_csv_path = Path("ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv")
manifest_json_path = Path("ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_EXECUTION.json")

with open(raw_csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

with open(manifest_json_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Loaded {len(rows)} telemetry rows from V4G execution CSV.")

# 1. Group by origin
origins = {}
for r in rows:
    oid = int(r["origin_id"])
    if oid not in origins:
        origins[oid] = []
    origins[oid].append(r)

# 2. Objective weight comparison for t=0..23
w_v3 = [0.95**t for t in range(24)]
w_v4g = [0.5133 if t == 13 else 1.0 for t in range(24)]

abs_diff = [w_v4g[t] - w_v3[t] for t in range(24)]
rel_diff = [(w_v4g[t] - w_v3[t]) / w_v3[t] for t in range(24)]

print("\n--- Objective Weight Comparison (t=0..23) ---")
print("t\tw_V3\t\tw_V4G\t\tAbs Diff (V4G - V3)\tRel Diff")
for t in range(24):
    print(f"{t}\t{w_v3[t]:.6f}\t{w_v4g[t]:.6f}\t{abs_diff[t]:+.6f}\t\t{rel_diff[t]:+.4f}")

# 3. First timestep divergence analysis per origin
first_commitment_div = []
first_power_div = []
first_soc_div = []
first_curtailment_div = []

total_v4g_commit_steps = 0
total_v3_commit_steps = 0
total_ctrl_commit_steps = 0

for oid in sorted(origins.keys()):
    o_rows = sorted(origins[oid], key=lambda x: int(x["mpc_timestep_idx"]))
    
    div_commit = None
    div_power = None
    div_soc = None
    div_curtail = None
    
    for r in o_rows:
        k = int(r["mpc_timestep_idx"])
        v4g_commit = float(r["diesel_commitment"])
        v3_commit = float(r["v3_diesel_commitment"])
        ctrl_commit = float(r["ctrl_diesel_commitment"])
        
        total_v4g_commit_steps += v4g_commit
        total_v3_commit_steps += v3_commit
        total_ctrl_commit_steps += ctrl_commit
        
        v4g_power = float(r["h1_diesel_power"])
        v3_power = float(r["v3_h1_diesel_power"])
        
        v4g_soc = float(r["soc_after"])
        v3_soc = float(r["v3_soc_after"])
        
        v4g_curtail = float(r["h1_renewable_curtailment"])
        v3_curtail = float(r["v3_h1_renewable_curtailment"])
        
        if div_commit is None and abs(v4g_commit - v3_commit) > 1e-3:
            div_commit = k
        if div_power is None and abs(v4g_power - v3_power) > 1e-3:
            div_power = k
        if div_soc is None and abs(v4g_soc - v3_soc) > 1e-3:
            div_soc = k
        if div_curtail is None and abs(v4g_curtail - v3_curtail) > 1e-3:
            div_curtail = k
            
    if div_commit is not None: first_commitment_div.append(div_commit)
    if div_power is not None: first_power_div.append(div_power)
    if div_soc is not None: first_soc_div.append(div_soc)
    if div_curtail is not None: first_curtailment_div.append(div_curtail)

print("\n--- Timestep Divergence Summary ---")
print(f"Total Diesel Commitment Steps across 173 origins:")
print(f"  Control: {int(total_ctrl_commit_steps)} steps")
print(f"  V3 Reference: {int(total_v3_commit_steps)} steps")
print(f"  V4.G Candidate: {int(total_v4g_commit_steps)} steps")
print(f"Origins with Diesel Commitment Divergence (V4G vs V3): {len(first_commitment_div)} / 173")
if first_commitment_div:
    print(f"  First Commitment Divergence Timestep: Min={min(first_commitment_div)}, Mean={np.mean(first_commitment_div):.2f}, Median={np.median(first_commitment_div)}")
print(f"Origins with Diesel Power Divergence (V4G vs V3): {len(first_power_div)} / 173")
if first_power_div:
    print(f"  First Power Divergence Timestep: Min={min(first_power_div)}, Mean={np.mean(first_power_div):.2f}, Median={np.median(first_power_div)}")
print(f"Origins with SOC Divergence (V4G vs V3): {len(first_soc_div)} / 173")
if first_soc_div:
    print(f"  First SOC Divergence Timestep: Min={min(first_soc_div)}, Mean={np.mean(first_soc_div):.2f}, Median={np.median(first_soc_div)}")

# 4. Heterogeneity analysis on origin level fuel differences
origins_summary = manifest["origins_summary"]
deltas = [r["delta_v4g_vs_v3_diesel_fuel_liters"] for r in origins_summary]

print("\n--- Origin-Level Fuel Delta (V4G - V3) Distribution ---")
print(f"Mean Delta: {np.mean(deltas):+.4f} L")
print(f"Median Delta: {np.median(deltas):+.4f} L")
print(f"Min Delta: {np.min(deltas):+.4f} L")
print(f"Max Delta: {np.max(deltas):+.4f} L")
print(f"Quantiles (25%, 50%, 75%, 90%, 95%, 99%): {np.percentile(deltas, [25, 50, 75, 90, 95, 99])}")

# Largest fuel increases
sorted_by_delta = sorted(origins_summary, key=lambda x: x["delta_v4g_vs_v3_diesel_fuel_liters"], reverse=True)
print("\nTop 5 Largest Fuel Increases (V4G vs V3):")
for r in sorted_by_delta[:5]:
    print(f"  Origin {r['origin_id']} ({r['origin_timestamp']}): V3={r['v3_reference_diesel_fuel_liters']:.2f}L, V4G={r['v4g_candidate_diesel_fuel_liters']:.2f}L, Delta={r['delta_v4g_vs_v3_diesel_fuel_liters']:+.2f}L")

# Largest fuel decreases
print("\nTop 5 Largest Fuel Decreases / Lowest Deltas (V4G vs V3):")
for r in sorted_by_delta[-5:]:
    print(f"  Origin {r['origin_id']} ({r['origin_timestamp']}): V3={r['v3_reference_diesel_fuel_liters']:.2f}L, V4G={r['v4g_candidate_diesel_fuel_liters']:.2f}L, Delta={r['delta_v4g_vs_v3_diesel_fuel_liters']:+.2f}L")

