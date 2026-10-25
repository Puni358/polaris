#!/usr/bin/env python3
"""
POLARIS — Candidate C.2 vs Ground Truth Validation
File: scratch/demo_c2_csv_lookup.py
"""

import pandas as pd
from datetime import timedelta

def _compute_boundary_clearsky_ratio(forecast_t23: float, clearsky_t23: float, clearsky_t24: float) -> float:
    MIN_CLEARSKY_WM2 = 5.0
    if clearsky_t23 < MIN_CLEARSKY_WM2:
        return max(0.0, 1.0 * clearsky_t24)
    k_t = min(forecast_t23 / clearsky_t23, 1.2)
    return max(0.0, k_t * clearsky_t24)

def run_ground_truth_validation():
    print("=" * 70)
    print("C.2 BOUNDARY ESTIMATOR vs PHYSICAL GROUND TRUTH")
    print("=" * 70)
    
    csv_path = "data/POLARIS_v0_1_clearsky_decomposition.csv"
    try:
        df = pd.read_csv(csv_path)
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], utc=True)
        df.set_index('TIMESTAMP', inplace=True)
    except FileNotFoundError:
        print(f"[FAIL] Could not find {csv_path}")
        return

    # 1. Define the Origin
    origin_dt = pd.to_datetime("2024-03-21 18:00:00+00:00")
    time_t23 = origin_dt + timedelta(hours=23)  # 03-22 17:00
    time_t24 = origin_dt + timedelta(hours=24)  # 03-22 18:00

    # 2. Extract Data from CSV
    try:
        cs_t23 = df.loc[time_t23, 'clearsky_ghi']
        cs_t24 = df.loc[time_t24, 'clearsky_ghi']
        
        # We simulate the ML forecast by using the *actual* realized value at t23 
        # (this represents a "perfect" ML forecast at t23 to isolate the C.2 boundary error)
        perfect_forecast_t23 = df.loc[time_t23, 'actual_SW_IN']
        
        # Extract the real ground truth for the boundary hour (t24)
        actual_t24 = df.loc[time_t24, 'actual_SW_IN']
        
    except KeyError as e:
        print(f"[FAIL] Timestamp {e} not found.")
        return

    # 3. Calculate C.2 Boundary Estimate
    estimated_t24_c2 = _compute_boundary_clearsky_ratio(
        forecast_t23=perfect_forecast_t23,
        clearsky_t23=cs_t23,
        clearsky_t24=cs_t24
    )
    
    # 4. Calculate naive Persistence (Candidate C.1) for comparison
    estimated_t24_persistence = perfect_forecast_t23

    # 5. Output Results
    print(f"Origin Timestamp:  {origin_dt}")
    print(f"Boundary Time t24: {time_t24}")
    print("-" * 50)
    print(f"Realized conditions at t23 (17:00): {perfect_forecast_t23:.2f} W/m2 (Clear-sky was {cs_t23:.2f})")
    print("-" * 50)
    print(f"ACTUAL Ground Truth at t24:         {actual_t24:.2f} W/m2")
    print(f"C.2 (Clear-Sky Ratio) Estimate:     {estimated_t24_c2:.2f} W/m2  | Error: {abs(estimated_t24_c2 - actual_t24):.2f} W/m2")
    print(f"C.1 (Persistence) Estimate:         {estimated_t24_persistence:.2f} W/m2 | Error: {abs(estimated_t24_persistence - actual_t24):.2f} W/m2")
    print("-" * 50)

if __name__ == "__main__":
    run_ground_truth_validation()
