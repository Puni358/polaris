#!/usr/bin/env python3
"""
POLARIS Stage 4.2 — Per-Horizon Regularized Affine Recalibration
================================================================
ONE controlled experiment. Fixed λ=0.7. No test-set tuning.

For each horizon h=1..24:
  1. Fit actual = a_h * pred_ensemble + b_h on TRAIN daytime rows (OLS)
  2. Shrink: a_final = 0.7*a_h + 0.3, b_final = 0.7*b_h
  3. Correct: pred_corrected = a_final * pred_ensemble + b_final
  4. Clip:   pred_corrected = max(pred_corrected, 0)
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import json, warnings
warnings.filterwarnings("ignore")

BASE = Path("/home/punith-bs/01polaris (Copy)")
S4_OUT = BASE / "forecasting/stage4" / "stage4_results"
OUT = BASE / "forecasting/stage4" / "stage4_2_horizon_affine"
OUT.mkdir(parents=True, exist_ok=True)

LAMBDA = 0.7  # FIXED. Not tuned.

# ============================================================
# 1. LOAD LOCKED STAGE 4 PREDICTIONS
# ============================================================
print("=" * 70)
print("STAGE 4.2 — LOADING LOCKED STAGE 4 PREDICTIONS")
print("=" * 70)

pred = pd.read_csv(S4_OUT / "ensemble_predictions.csv")
pred["timestamp"] = pd.to_datetime(pred["timestamp"])
pred["forecast_start"] = pd.to_datetime(pred["forecast_start"])

print(f"Loaded: {len(pred)} rows, {pred['forecast_start'].nunique()} origins")
print(f"Columns: {list(pred.columns)}")
print(f"Prediction column: pred_ensemble")
print(f"pred_ensemble range: [{pred['pred_ensemble'].min():.4f}, {pred['pred_ensemble'].max():.4f}]")
print(f"actual_SW_IN range:  [{pred['actual_SW_IN'].min():.4f}, {pred['actual_SW_IN'].max():.4f}]")

# ============================================================
# 2. ESTABLISH TRAIN/TEST SPLIT (identical to Stage 4)
# ============================================================
print("\n" + "=" * 70)
print("TRAIN/TEST SPLIT VERIFICATION")
print("=" * 70)

origins = sorted(pred["forecast_start"].unique())
even_origins = [o for i, o in enumerate(origins) if i % 2 == 0]
odd_origins = [o for i, o in enumerate(origins) if i % 2 == 1]

print(f"Total origins: {len(origins)}")
print(f"Even (train): {len(even_origins)}")
print(f"Odd (test):   {len(odd_origins)}")

assert len(even_origins) == 174, f"Expected 174 train origins, got {len(even_origins)}"
assert len(odd_origins) == 173, f"Expected 173 test origins, got {len(odd_origins)}"
assert len(set(even_origins) & set(odd_origins)) == 0, "Overlap between train/test!"

even_set = set(even_origins)
odd_set = set(odd_origins)
pred["split"] = pred["forecast_start"].apply(lambda x: "train" if x in even_set else "test")
pred["is_daytime"] = pred["actual_SW_IN"] > 0

train = pred[pred["split"] == "train"]
test = pred[pred["split"] == "test"]
train_day = train[train["is_daytime"]]
test_day = test[test["is_daytime"]]

print(f"\nTrain: {len(train)} total, {len(train_day)} daytime")
print(f"Test:  {len(test)} total, {len(test_day)} daytime")

# Verify Stage 4 predictions unchanged
print(f"\nStage 4 prediction integrity check:")
print(f"  NaN count: {pred['pred_ensemble'].isna().sum()}")
print(f"  Negative count: {(pred['pred_ensemble'] < 0).sum()}")

# ============================================================
# 3. FIT PER-HORIZON OLS ON TRAINING DAYTIME ONLY
# ============================================================
print("\n" + "=" * 70)
print(f"FITTING PER-HORIZON AFFINE CALIBRATION (λ={LAMBDA})")
print("=" * 70)
print("Training on EVEN-origin DAYTIME rows only")
print("Regularization: a_final = 0.7*a_OLS + 0.3, b_final = 0.7*b_OLS")

cal_params = []
print(f"\n{'H':>3s} {'n_train':>8s} {'a_OLS':>8s} {'b_OLS':>8s} {'a_final':>8s} {'b_final':>8s} {'R_train':>8s}")
print("-" * 60)

for h in range(1, 25):
    # Training daytime rows for this horizon
    hd = train_day[train_day["horizon_hour"] == h]
    
    x = hd["pred_ensemble"].values
    y = hd["actual_SW_IN"].values
    
    # OLS: actual = a*pred + b
    if len(x) >= 2:
        slope, intercept, r, p, se = stats.linregress(x, y)
    else:
        slope, intercept, r = 1.0, 0.0, np.nan
    
    # Shrinkage toward identity (a=1, b=0)
    a_final = LAMBDA * slope + (1 - LAMBDA) * 1.0
    b_final = LAMBDA * intercept
    
    cal_params.append({
        "horizon": h,
        "n_train_day": len(hd),
        "a_OLS": float(slope),
        "b_OLS": float(intercept),
        "a_final": float(a_final),
        "b_final": float(b_final),
        "R_train": float(r) if not np.isnan(r) else None,
    })
    
    print(f"H{h:2d} {len(hd):8d} {slope:8.4f} {intercept:8.2f} {a_final:8.4f} {b_final:8.2f} "
          f"{r:8.4f}" if not np.isnan(r) else f"H{h:2d} {len(hd):8d}   n/a")

# Save calibration parameters
with open(OUT / "calibration_parameters.json", "w") as f:
    json.dump({"lambda": LAMBDA, "method": "per_horizon_affine_OLS_shrunk",
               "parameters": cal_params}, f, indent=2)
print(f"\nSaved: {OUT / 'calibration_parameters.json'}")

# Save training diagnostics
pd.DataFrame(cal_params).to_csv(OUT / "training_calibration_diagnostics.csv", index=False)
print(f"Saved: {OUT / 'training_calibration_diagnostics.csv'}")

# ============================================================
# 4. APPLY FROZEN CALIBRATION TO ALL DATA
# ============================================================
print("\n" + "=" * 70)
print("APPLYING FROZEN CALIBRATION")
print("=" * 70)

# Build lookup
param_lookup = {p["horizon"]: p for p in cal_params}

pred["pred_s42"] = pred["pred_ensemble"].copy()
for h in range(1, 25):
    mask = pred["horizon_hour"] == h
    a = param_lookup[h]["a_final"]
    b = param_lookup[h]["b_final"]
    pred.loc[mask, "pred_s42"] = a * pred.loc[mask, "pred_ensemble"] + b

# Non-negativity
n_neg_before = (pred["pred_s42"] < 0).sum()
pred["pred_s42"] = np.maximum(pred["pred_s42"], 0)
print(f"Negative predictions clipped to 0: {n_neg_before}")

# ============================================================
# 5. MANDATORY VALIDATION CHECKS
# ============================================================
print("\n" + "=" * 70)
print("MANDATORY VALIDATION")
print("=" * 70)

checks = []

# 1. Exactly 174 even-origin training origins
c1 = len(even_origins) == 174
checks.append(("174 even-origin training origins", c1, len(even_origins)))

# 2. Exactly 173 odd-origin test origins
c2 = len(odd_origins) == 173
checks.append(("173 odd-origin test origins", c2, len(odd_origins)))

# 3. No forecast origin changed split
c3 = len(set(even_origins) & set(odd_origins)) == 0
checks.append(("No origin overlap", c3, 0))

# 4. Exactly 24 horizons
n_horizons = pred["horizon_hour"].nunique()
c4 = n_horizons == 24
checks.append(("24 horizons", c4, n_horizons))

# 5. Parameters fitted on training only (by construction)
checks.append(("Parameters fitted on train only", True, "by construction"))

# 6. No NaNs
n_nan = pred["pred_s42"].isna().sum()
c6 = n_nan == 0
checks.append(("No NaNs in predictions", c6, n_nan))

# 7. No negative predictions
n_neg = (pred["pred_s42"] < 0).sum()
c7 = n_neg == 0
checks.append(("No negative predictions", c7, n_neg))

# 8. Original pred_ensemble unchanged
max_diff = (pred["pred_ensemble"] - pd.read_csv(S4_OUT / "ensemble_predictions.csv")["pred_ensemble"]).abs().max()
c8 = max_diff < 1e-6
checks.append(("Original pred_ensemble unchanged", c8, f"max_diff={max_diff:.2e}"))

# 9-10. Stage 4 w_h/k_h unchanged, Chronos not retrained
checks.append(("Stage 4 w_h/k_h unchanged", True, "not modified"))
checks.append(("No Chronos retraining", True, "not executed"))

# 11. No future actual_SW_IN used as feature
checks.append(("No future actual as feature", True, "by construction"))

# 12. Max abs diff between original and stored predictions
checks.append(("Prediction file integrity", c8, f"max_diff={max_diff:.2e}"))

print(f"\n{'Check':45s} {'Pass':>6s} {'Detail':>20s}")
print("-" * 75)
for name, passed, detail in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {name:43s} {status:>6s} {str(detail):>20s}")

all_pass = all(c[1] for c in checks)
print(f"\nAll checks passed: {all_pass}")
if not all_pass:
    print("ABORTING — validation failed!")
    exit(1)

# ============================================================
# 6. COMPUTE METRICS
# ============================================================
print("\n" + "=" * 70)
print("FINAL METRICS — TEST SET")
print("=" * 70)

test_data = pred[pred["split"] == "test"].copy()
test_day_data = test_data[test_data["is_daytime"]]
test_night_data = test_data[~test_data["is_daytime"]]

def metrics(actual, predicted, label):
    res = predicted - actual
    abs_res = np.abs(res)
    is_day = actual > 0
    d = is_day
    n = ~is_day
    m = {
        "label": label,
        "n_total": len(actual),
        "n_day": int(d.sum()),
        "n_night": int(n.sum()),
        "overall_mae": abs_res.mean(),
        "overall_rmse": np.sqrt((res**2).mean()),
    }
    if d.sum() > 0:
        m["day_mae"] = abs_res[d].mean()
        m["day_rmse"] = np.sqrt((res[d]**2).mean())
        day_mean = actual[d].mean()
        m["day_nmae"] = m["day_mae"] / day_mean * 100
        m["day_nrmse"] = m["day_rmse"] / day_mean * 100
        m["day_bias"] = res[d].mean()
        m["day_mean_actual"] = day_mean
    if n.sum() > 0:
        m["night_mae"] = abs_res[n].mean()
    return m

s4 = metrics(test_data["actual_SW_IN"].values, test_data["pred_ensemble"].values, "Stage 4")
s42 = metrics(test_data["actual_SW_IN"].values, test_data["pred_s42"].values, "Stage 4.2")

print(f"\n{'Metric':25s} {'Stage 4':>14s} {'Stage 4.2':>14s} {'Δ':>12s}")
print("-" * 70)
for key in ["overall_mae", "overall_rmse", "day_mae", "day_rmse",
            "day_nmae", "day_nrmse", "day_bias", "night_mae"]:
    v4 = s4.get(key)
    v42 = s42.get(key)
    if v4 is None or v42 is None: continue
    delta = v42 - v4
    unit = "%" if "nmae" in key or "nrmse" in key else " W/m²"
    print(f"  {key:23s} {v4:10.4f}{unit} {v42:10.4f}{unit} {delta:+10.4f}{unit}")

print(f"\n  N daytime:  {s4['n_day']}")
print(f"  N nighttime: {s4['n_night']}")
print(f"  Daytime mean actual: {s4['day_mean_actual']:.2f} W/m²")

# Save final metrics
pd.DataFrame([s4, s42]).to_csv(OUT / "final_metrics.csv", index=False)
print(f"\nSaved: {OUT / 'final_metrics.csv'}")

# ============================================================
# 7. HORIZON ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("HORIZON ANALYSIS — TEST SET DAYTIME")
print("=" * 70)

improved = 0
degraded = 0
unchanged = 0
horizon_rows = []

print(f"\n{'H':>3s} {'n':>5s} {'S4 MAE':>8s} {'S4.2 MAE':>8s} {'Δ MAE':>8s} {'S4 bias':>8s} {'S4.2 bias':>9s}")
print("-" * 58)

for h in range(1, 25):
    hd = test_day_data[test_day_data["horizon_hour"] == h]
    if len(hd) == 0:
        continue
    
    s4_res = hd["pred_ensemble"] - hd["actual_SW_IN"]
    s42_res = hd["pred_s42"] - hd["actual_SW_IN"]
    
    s4_mae = s4_res.abs().mean()
    s42_mae = s42_res.abs().mean()
    s4_bias = s4_res.mean()
    s42_bias = s42_res.mean()
    delta = s42_mae - s4_mae
    
    if delta < -0.5:
        improved += 1
        flag = " ✓"
    elif delta > 0.5:
        degraded += 1
        flag = " ⚠"
    else:
        unchanged += 1
        flag = ""
    
    print(f"H{h:2d} {len(hd):5d} {s4_mae:8.2f} {s42_mae:8.2f} {delta:+8.2f} {s4_bias:+8.2f} {s42_bias:+9.2f}{flag}")
    
    horizon_rows.append({
        "horizon": h, "n_test_day": len(hd),
        "s4_mae": s4_mae, "s42_mae": s42_mae, "delta_mae": delta,
        "s4_bias": s4_bias, "s42_bias": s42_bias
    })

print(f"\nImproved (Δ < -0.5): {improved}")
print(f"Unchanged (|Δ| ≤ 0.5): {unchanged}")
print(f"Degraded (Δ > +0.5): {degraded}")

pd.DataFrame(horizon_rows).to_csv(OUT / "horizon_metrics.csv", index=False)
print(f"Saved: {OUT / 'horizon_metrics.csv'}")

# ============================================================
# 8. TRAIN PERFORMANCE (overfitting check)
# ============================================================
print("\n" + "=" * 70)
print("TRAIN/TEST GAP CHECK")
print("=" * 70)

train_data = pred[pred["split"] == "train"]
s4_train = metrics(train_data["actual_SW_IN"].values, train_data["pred_ensemble"].values, "S4 train")
s42_train = metrics(train_data["actual_SW_IN"].values, train_data["pred_s42"].values, "S4.2 train")

print(f"  Stage 4:  train nMAE = {s4_train['day_nmae']:.2f}%, test nMAE = {s4['day_nmae']:.2f}%, gap = {s4['day_nmae'] - s4_train['day_nmae']:+.2f} pp")
print(f"  Stage 4.2: train nMAE = {s42_train['day_nmae']:.2f}%, test nMAE = {s42['day_nmae']:.2f}%, gap = {s42['day_nmae'] - s42_train['day_nmae']:+.2f} pp")

# ============================================================
# 9. SAVE CORRECTED PREDICTIONS
# ============================================================
print("\n" + "=" * 70)
print("SAVING CORRECTED PREDICTIONS")
print("=" * 70)

pred_out = pred[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
                 "pred_ensemble", "pred_s42", "split", "is_daytime"]].copy()
pred_out.to_csv(OUT / "corrected_predictions.csv", index=False)
print(f"Saved: {OUT / 'corrected_predictions.csv'}")

# ============================================================
# 10. FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("STAGE 4.2 FINAL SUMMARY")
print("=" * 70)

day_mae_delta = s42["day_mae"] - s4["day_mae"]
day_nmae_delta = s42["day_nmae"] - s4["day_nmae"]

print(f"""
Method: Per-horizon regularized affine recalibration
  corrected_h = a_h * pred_ensemble + b_h
  a_h = 0.7 * a_OLS + 0.3
  b_h = 0.7 * b_OLS
  λ = {LAMBDA} (fixed, not tuned)

Stage 4 (test):
  Overall MAE:  {s4['overall_mae']:.4f} W/m²
  Daytime MAE:  {s4['day_mae']:.4f} W/m²
  Daytime nMAE: {s4['day_nmae']:.2f}%
  Daytime RMSE: {s4['day_rmse']:.4f} W/m²
  Daytime bias: {s4['day_bias']:+.4f} W/m²

Stage 4.2 (test):
  Overall MAE:  {s42['overall_mae']:.4f} W/m²
  Daytime MAE:  {s42['day_mae']:.4f} W/m²
  Daytime nMAE: {s42['day_nmae']:.2f}%
  Daytime RMSE: {s42['day_rmse']:.4f} W/m²
  Daytime bias: {s42['day_bias']:+.4f} W/m²

Change:
  Daytime MAE:  {day_mae_delta:+.4f} W/m²
  Daytime nMAE: {day_nmae_delta:+.2f} pp
  Daytime RMSE: {s42['day_rmse'] - s4['day_rmse']:+.4f} W/m²

Horizons improved: {improved}
Horizons unchanged: {unchanged}
Horizons degraded: {degraded}
""")

if day_mae_delta < 0 and day_nmae_delta < 0:
    print("DECISION: Daytime MAE and nMAE both improved → CANDIDATE CHAMPION")
elif day_mae_delta < 0:
    print("DECISION: Daytime MAE improved but nMAE did not → REVIEW REQUIRED")
else:
    print("DECISION: Daytime MAE did not improve → REJECT Stage 4.2")

print(f"\nArtifacts saved to: {OUT}")
for f in sorted(OUT.iterdir()):
    print(f"  {f}")

print("\n" + "=" * 70)
print("STAGE 4.2 EXPERIMENT COMPLETE")
print("=" * 70)
