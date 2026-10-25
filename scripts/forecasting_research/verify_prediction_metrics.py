#!/usr/bin/env python3
"""
POLARIS — INDEPENDENT METRIC VERIFICATION SCRIPT
=================================================
Independent Verification Script for POLARIS Reproducible Baseline ODD Predictions.
Reads prediction CSV directly from disk.
MUST NOT import evaluator variables, stored metrics, or hardcoded literal targets.
"""

import sys
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
PRED_CSV_PATH = BASE_DIR / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def verify_metrics():
    print("==================================================")
    print("POLARIS — INDEPENDENT METRIC VERIFICATION")
    print("==================================================")
    
    if not PRED_CSV_PATH.exists():
        print(f"ERROR: Prediction CSV not found at {PRED_CSV_PATH}")
        sys.exit(1)
        
    csv_hash = compute_sha256(PRED_CSV_PATH)
    print(f"Prediction CSV Path: {PRED_CSV_PATH}")
    print(f"Prediction CSV SHA-256: {csv_hash}")
    
    df = pd.read_csv(PRED_CSV_PATH)
    total_rows = len(df)
    print(f"Total Rows Loaded: {total_rows}")
    
    if total_rows != 4152:
        print(f"ERROR: Expected 4152 rows (173 origins x 24 horizons), got {total_rows}")
        sys.exit(1)
        
    # Identify daytime rows independently
    daytime_mask = df["y_true"] > 0
    daytime_rows = df[daytime_mask].copy()
    night_rows = df[~daytime_mask].copy()
    
    num_daytime = len(daytime_rows)
    num_night = len(night_rows)
    print(f"Daytime Rows (y_true > 0): {num_daytime} | Night Rows: {num_night}")
    
    y_true_day = daytime_rows["y_true"].values
    y_pred_day = daytime_rows["y_pred"].values
    
    mean_actual_day = np.mean(y_true_day)
    
    # Calculate metrics
    mae = np.mean(np.abs(y_pred_day - y_true_day))
    nmae_pct = (mae / mean_actual_day) * 100.0
    rmse = np.sqrt(np.mean((y_pred_day - y_true_day) ** 2))
    bias = np.mean(y_pred_day - y_true_day)
    
    y_true_night = night_rows["y_true"].values
    y_pred_night = night_rows["y_pred"].values
    night_mae = np.mean(np.abs(y_pred_night - y_true_night))
    
    metrics = {
        "prediction_csv_sha256": csv_hash,
        "total_prediction_rows": total_rows,
        "daytime_rows_count": num_daytime,
        "night_rows_count": num_night,
        "mean_daytime_actual_w_m2": float(mean_actual_day),
        "daytime_mae_w_m2": float(mae),
        "daytime_nmae_pct": float(nmae_pct),
        "daytime_rmse_w_m2": float(rmse),
        "daytime_bias_w_m2": float(bias),
        "night_mae_w_m2": float(night_mae)
    }
    
    print("\n--- INDEPENDENTLY RECOMPUTED METRICS ---")
    print(f"Mean Daytime Actual: {mean_actual_day:.6f} W/m²")
    print(f"Daytime MAE:         {mae:.6f} W/m²")
    print(f"Daytime nMAE:        {nmae_pct:.4f}%")
    print(f"Daytime RMSE:        {rmse:.6f} W/m²")
    print(f"Daytime Bias:        {bias:+.6f} W/m²")
    print(f"Night MAE:           {night_mae:.6f} W/m²")
    print("----------------------------------------")
    
    # Write output JSON manifest
    output_json = BASE_DIR / "forecasting/reports/stage8/POLARIS_INDEPENDENT_METRIC_VERIFICATION.json"
    with open(output_json, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved independent verification manifest: {output_json}")
    
    return metrics

if __name__ == "__main__":
    verify_metrics()
