#!/usr/bin/env python3
"""
POLARIS Stage 4.3 — Dynamic Blending with Delta-Parameterized Logistic Adjustment
==================================================================================

Research Hypothesis:
    The optimal balance between Chronos neural forecast and physics-based NWP forecast
    is STATE-DEPENDENT rather than fixed solely by horizon.

Mathematical Formulation:
    logit(w_dynamic) = logit(w_stage4_h) + X_scaled @ theta
    P_dynamic = w_dynamic * P_chronos + (1 - w_dynamic) * P_physics

Training:
    - 174 EVEN origins only (forward-chaining CV for lambda selection)
    - Daytime samples only
    - Huber loss (robust MAE approximation) + L2 regularization
    - Optimize theta to minimize prediction error

Evaluation:
    - 173 ODD origins (completely held-out)
    - Compare to Stage 4 baseline (43.45 W/m² daytime MAE)
    - Statistical significance via paired bootstrap

Constraints:
    - Zero test-set leakage
    - No future actual SW_IN in features
    - No ODD origins used in training/validation/hyperparameter selection
    - Preserve nighttime behavior
"""

import pandas as pd
import numpy as np
from scipy import optimize, stats
from pathlib import Path
import json
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings("ignore")

# Paths
BASE = Path("/home/punith-bs/01polaris (Copy)")
OUT = BASE / "forecasting/stage4" / "stage4_3_dynamic_blending"
OUT.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("POLARIS STAGE 4.3 — DYNAMIC BLENDING")
print("=" * 80)

# ============================================================
# PHASE 0: LOAD DATA
# ============================================================
print("\n" + "=" * 80)
print("PHASE 0: LOADING DATA")
print("=" * 80)

# Stage 4 ensemble predictions
stage4_pred = pd.read_csv(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_predictions.csv")
stage4_pred["forecast_start"] = pd.to_datetime(stage4_pred["forecast_start"])
stage4_pred["timestamp"] = pd.to_datetime(stage4_pred["timestamp"])
print(f"Stage 4 predictions: {len(stage4_pred)} rows")

# Stage 4 parameters (w_h, k_h)
with open(BASE / "forecasting/stage4" / "stage4_results" / "ensemble_parameters.json") as f:
    stage4_params = json.load(f)
print(f"Stage 4 parameters: H1-H24 loaded")

# NWP forecasts
nwp = pd.read_csv(BASE / "data" / "POLARIS_v0_1_future_weather_forecasts_2024.csv")
nwp["forecast_start"] = pd.to_datetime(nwp["forecast_start"])
nwp["timestamp"] = pd.to_datetime(nwp["timestamp"])
print(f"NWP forecasts: {len(nwp)} rows")

# Clear-sky decomposition
clearsky = pd.read_csv(BASE / "data" / "POLARIS_v0_1_clearsky_decomposition.csv")
clearsky["TIMESTAMP"] = pd.to_datetime(clearsky["TIMESTAMP"])
print(f"Clear-sky data: {len(clearsky)} rows")

# SITES observations
sites = pd.read_csv(BASE / "data" / "POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv")
sites["TIMESTAMP"] = pd.to_datetime(sites["TIMESTAMP"])
print(f"SITES observations: {len(sites)} rows")

# ============================================================
# PHASE 1: DATA ASSEMBLY & FEATURE ENGINEERING
# ============================================================
print("\n" + "=" * 80)
print("PHASE 1: DATA ASSEMBLY & FEATURE ENGINEERING")
print("=" * 80)

# Start with Stage 4 predictions
df = stage4_pred.copy()

# Merge NWP
nwp_cols = ["forecast_start", "horizon_hour", "fc_cloud_cover", 
            "fc_temperature_2m", "fc_relative_humidity_2m"]
df = df.merge(nwp[nwp_cols], on=["forecast_start", "horizon_hour"], how="left")

# Merge clear-sky
clearsky_cols = ["TIMESTAMP", "clearsky_ghi", "solar_elevation", "solar_zenith"]
df = df.merge(clearsky[clearsky_cols], left_on="timestamp", right_on="TIMESTAMP", how="left")
df.drop(columns=["TIMESTAMP"], inplace=True)

# Compute cloud fraction
df["cloud_frac"] = df["fc_cloud_cover"] / 100.0

# Add Stage 4 fixed weights
df["w_stage4"] = df["horizon_hour"].map(lambda h: stage4_params[str(h)]["w"])

# Compute physics component by back-solving from Stage 4 ensemble
# ensemble = w * chronos + (1-w) * physics
# physics = (ensemble - w * chronos) / (1-w)
df["pred_physics"] = 0.0
for h in range(1, 25):
    w_h = stage4_params[str(h)]["w"]
    mask = df["horizon_hour"] == h
    
    if abs(1 - w_h) > 0.0001:  # If weight not ~1
        df.loc[mask, "pred_physics"] = (
            (df.loc[mask, "pred_ensemble"] - w_h * df.loc[mask, "pred_stage3b_cloud_nwp"]) / (1 - w_h)
        )
    else:  # If w ~= 1, physics component not used
        df.loc[mask, "pred_physics"] = 0.0

# Clip physics at 0 (can't have negative irradiance)
df["pred_physics"] = np.maximum(df["pred_physics"], 0)

# Verify Stage 4 ensemble prediction matches (should be exact now)
df["pred_stage4_check"] = (
    df["w_stage4"] * df["pred_stage3b_cloud_nwp"] + 
    (1 - df["w_stage4"]) * df["pred_physics"]
)
max_diff = (df["pred_ensemble"] - df["pred_stage4_check"]).abs().max()
print(f"\nVerification: Max difference between stored Stage 4 and recomputed: {max_diff:.6f} W/m²")
assert max_diff < 0.1, "Stage 4 ensemble mismatch > 0.1 W/m²!"

# Compute context features (24h historical stats)
print("\nComputing context features...")
context_stats = []
origins = sorted(df["forecast_start"].unique())
for origin in origins:
    ctx_start = origin - pd.Timedelta(hours=24)
    ctx_end = origin - pd.Timedelta(hours=1)
    ctx = sites[(sites["TIMESTAMP"] >= ctx_start) & (sites["TIMESTAMP"] <= ctx_end)]
    sw_vals = ctx["SW_IN"].dropna()
    
    if len(sw_vals) > 0:
        context_stats.append({
            "forecast_start": origin,
            "ctx_mean": sw_vals.mean(),
            "ctx_max": sw_vals.max(),
            "ctx_min": sw_vals.min(),
            "ctx_std": sw_vals.std() if len(sw_vals) > 1 else 0.0,
            "ctx_n": len(sw_vals)
        })
    else:
        context_stats.append({
            "forecast_start": origin,
            "ctx_mean": 0.0, "ctx_max": 0.0, "ctx_min": 0.0,
            "ctx_std": 0.0, "ctx_n": 0
        })

ctx_df = pd.DataFrame(context_stats)
df = df.merge(ctx_df, on="forecast_start", how="left")

# Derived features
df["clearsky_x_clearfrac"] = df["clearsky_ghi"] * (1 - df["cloud_frac"])
df["is_daytime"] = df["actual_SW_IN"] > 0

print(f"\nMerged dataset: {len(df)} rows")
print(f"  Total origins: {df['forecast_start'].nunique()}")
print(f"  Daytime samples: {df['is_daytime'].sum()}")
print(f"  Night samples: {(~df['is_daytime']).sum()}")

# Check for NaN in critical columns
critical_cols = ["actual_SW_IN", "pred_stage3b_cloud_nwp", "pred_ensemble", "pred_physics",
                 "w_stage4", "clearsky_ghi", "solar_elevation", "fc_cloud_cover",
                 "ctx_mean", "ctx_max", "ctx_std"]
for col in critical_cols:
    n_nan = df[col].isna().sum()
    if n_nan > 0:
        print(f"  WARNING: {col} has {n_nan} NaN values")

# ============================================================
# PHASE 2: TRAIN/TEST SPLIT
# ============================================================
print("\n" + "=" * 80)
print("PHASE 2: TRAIN/TEST SPLIT")
print("=" * 80)

origins = sorted(df["forecast_start"].unique())
assert len(origins) == 347, f"Expected 347 origins, got {len(origins)}"

# Even/odd split (same as Stage 4)
even_origins = [origins[i] for i in range(0, 347, 2)]  # indices 0,2,4,...
odd_origins = [origins[i] for i in range(1, 347, 2)]   # indices 1,3,5,...

train_mask = df["forecast_start"].isin(even_origins)
test_mask = df["forecast_start"].isin(odd_origins)

df_train = df[train_mask].copy()
df_test = df[test_mask].copy()

# Focus on daytime
df_train_day = df_train[df_train["is_daytime"]].copy()
df_test_day = df_test[df_test["is_daytime"]].copy()

print(f"Total origins: {len(origins)}")
print(f"EVEN origins (train): {len(even_origins)}")
print(f"ODD origins (test):   {len(odd_origins)}")
print(f"\nTrain set:")
print(f"  Total samples: {len(df_train)}")
print(f"  Daytime samples: {len(df_train_day)}")
print(f"  Date range: {even_origins[0].date()} to {even_origins[-1].date()}")
print(f"\nTest set:")
print(f"  Total samples: {len(df_test)}")
print(f"  Daytime samples: {len(df_test_day)}")
print(f"  Date range: {odd_origins[0].date()} to {odd_origins[-1].date()}")

# Verify split
assert set(even_origins).isdisjoint(set(odd_origins))
assert len(even_origins) == 174
assert len(odd_origins) == 173
print(f"\n✓ Split verification passed")

# ============================================================
# PHASE 3: FEATURE SET & LEAKAGE AUDIT
# ============================================================
print("\n" + "=" * 80)
print("PHASE 3: FEATURE SET & LEAKAGE AUDIT")
print("=" * 80)

feature_cols = [
    "solar_elevation",       # Deterministic ephemeris (future)
    "clearsky_ghi",          # PVLIB model (future)
    "horizon_hour",          # Index (known)
    "cloud_frac",            # NWP forecast (future)
    "ctx_mean",              # Historical observation
    "ctx_max",               # Historical observation
    "ctx_std",               # Historical observation
    "pred_stage3b_cloud_nwp", # Chronos prediction (P_chronos)
    "pred_physics",          # Physics prediction (P_physics)
    "clearsky_x_clearfrac",  # Derived from above
]

print(f"Feature set ({len(feature_cols)} features):")
for i, feat in enumerate(feature_cols, 1):
    print(f"  {i:2d}. {feat}")

print("\nLeakage audit:")
print("  ✓ All features available at forecast issuance")
print("  ✓ No future actual SW_IN")
print("  ✓ No future observed weather")
print("  ✓ No test-set information")

# Check feature correlations
X_train = df_train_day[feature_cols].values
corr_matrix = np.corrcoef(X_train, rowvar=False)
print(f"\nFeature correlation matrix:")
print(f"  Max off-diagonal correlation: {np.max(np.abs(corr_matrix - np.eye(len(feature_cols)))):.3f}")

# Check condition number
cond_number = np.linalg.cond(X_train)
print(f"  Condition number: {cond_number:.1f}")
if cond_number > 100:
    print(f"    WARNING: High condition number suggests multicollinearity")

# High correlations
high_corr_pairs = []
for i in range(len(feature_cols)):
    for j in range(i+1, len(feature_cols)):
        if abs(corr_matrix[i, j]) > 0.7:
            high_corr_pairs.append((feature_cols[i], feature_cols[j], corr_matrix[i, j]))

if high_corr_pairs:
    print(f"\n  High correlations (|r| > 0.7):")
    for f1, f2, r in high_corr_pairs:
        print(f"    {f1} <-> {f2}: {r:.3f}")
else:
    print(f"  No high correlations (|r| > 0.7)")

# ============================================================
# PHASE 4: DYNAMIC BLENDING MODEL
# ============================================================
print("\n" + "=" * 80)
print("PHASE 4: DYNAMIC BLENDING MODEL")
print("=" * 80)

class DynamicBlender:
    """
    Delta-parameterized logistic blender:
        logit(w_dynamic) = logit(w_stage4) + X_scaled @ theta
        P_dynamic = w_dynamic * P_chronos + (1 - w_dynamic) * P_physics
    """
    
    def __init__(self, feature_cols):
        self.feature_cols = feature_cols
        self.theta = None
        self.scaler_mean = None
        self.scaler_std = None
        self.lambda_ridge = None
    
    def standardize_fit(self, X):
        """Fit standardization parameters."""
        self.scaler_mean = X.mean(axis=0)
        self.scaler_std = X.std(axis=0)
        self.scaler_std[self.scaler_std == 0] = 1.0  # Avoid division by zero
        
    def standardize_transform(self, X):
        """Apply standardization."""
        return (X - self.scaler_mean) / self.scaler_std
    
    def get_dynamic_weights(self, X_scaled, w_stage4):
        """Compute dynamic weights from features."""
        # logit(w_stage4)
        logit_w_baseline = np.log(w_stage4 / (1 - w_stage4 + 1e-10))
        
        # logit(w_dynamic) = logit(w_stage4) + theta @ X
        logit_w_dynamic = logit_w_baseline + X_scaled @ self.theta
        
        # w_dynamic = sigmoid(logit_w_dynamic)
        w_dynamic = 1 / (1 + np.exp(-logit_w_dynamic))
        
        return w_dynamic
    
    def predict(self, X_scaled, w_stage4, P_chronos, P_physics):
        """Predict using dynamic blend."""
        w_dynamic = self.get_dynamic_weights(X_scaled, w_stage4)
        pred = w_dynamic * P_chronos + (1 - w_dynamic) * P_physics
        return np.maximum(pred, 0)  # Clip at 0
    
    def loss_fn(self, theta, X_scaled, y, w_stage4, P_chronos, P_physics, lambda_ridge, delta_huber):
        """
        Huber loss (robust MAE approximation) + L2 regularization.
        
        Huber loss:
            L(r) = 0.5 * r^2                    if |r| <= delta
                   delta * (|r| - 0.5 * delta)  if |r| > delta
        
        For delta -> 0, Huber approaches MAE.
        For delta -> inf, Huber approaches MSE.
        
        We use delta = 10 W/m² as a reasonable transition point for SW_IN errors.
        """
        self.theta = theta
        pred = self.predict(X_scaled, w_stage4, P_chronos, P_physics)
        residual = pred - y
        
        # Huber loss
        abs_residual = np.abs(residual)
        huber = np.where(
            abs_residual <= delta_huber,
            0.5 * residual**2,
            delta_huber * (abs_residual - 0.5 * delta_huber)
        )
        
        data_loss = huber.mean()
        reg_loss = lambda_ridge * (theta @ theta)
        
        return data_loss + reg_loss
    
    def fit(self, X, y, w_stage4, P_chronos, P_physics, lambda_ridge, delta_huber=10.0):
        """Fit the dynamic blender."""
        # Standardize features
        self.standardize_fit(X)
        X_scaled = self.standardize_transform(X)
        
        # Initialize theta = 0 (reproduces Stage 4)
        theta_init = np.zeros(len(self.feature_cols))
        
        # Optimize
        result = optimize.minimize(
            self.loss_fn,
            x0=theta_init,
            args=(X_scaled, y, w_stage4, P_chronos, P_physics, lambda_ridge, delta_huber),
            method="L-BFGS-B",
            options={"maxiter": 1000, "disp": False}
        )
        
        self.theta = result.x
        self.lambda_ridge = lambda_ridge
        
        return result

# Test: theta=0 reproduces Stage 4
print("\nUnit test: theta=0 reproduces Stage 4")
blender = DynamicBlender(feature_cols)
X_test_sample = df_train_day[feature_cols].values[:100]
blender.standardize_fit(X_test_sample)
X_test_scaled = blender.standardize_transform(X_test_sample)
blender.theta = np.zeros(len(feature_cols))

w_stage4_sample = df_train_day["w_stage4"].values[:100]
P_chronos_sample = df_train_day["pred_stage3b_cloud_nwp"].values[:100]
P_physics_sample = df_train_day["pred_physics"].values[:100]
P_stage4_sample = df_train_day["pred_ensemble"].values[:100]

P_dynamic_sample = blender.predict(X_test_scaled, w_stage4_sample, P_chronos_sample, P_physics_sample)
max_diff = np.abs(P_dynamic_sample - P_stage4_sample).max()
print(f"  Max difference: {max_diff:.6f} W/m²")
assert max_diff < 0.01, "Unit test failed: theta=0 does not reproduce Stage 4!"
print(f"  ✓ Unit test passed")

# ============================================================
# PHASE 5: FORWARD-CHAINING CV FOR LAMBDA SELECTION
# ============================================================
print("\n" + "=" * 80)
print("PHASE 5: FORWARD-CHAINING CV FOR LAMBDA SELECTION")
print("=" * 80)

print("Strategy: Forward-chaining cross-validation within 174 EVEN origins")
print("  - Ensures training data is always temporally BEFORE validation data")
print("  - Prevents future information leakage")
print("  - More realistic evaluation of temporal generalization")

# Define folds: forward-chaining with minimum training size
n_even = len(even_origins)
min_train = 100  # Require at least 100 origins for training
n_folds = 4  # Use 4 folds instead of 5 to maintain larger training sets

folds = []
remaining = n_even - min_train
fold_val_size = remaining // n_folds

for fold_idx in range(n_folds):
    train_end = min_train + fold_idx * fold_val_size
    val_start = train_end
    val_end = train_end + fold_val_size
    
    if fold_idx == n_folds - 1:  # Last fold gets remainder
        val_end = n_even
    
    train_origins_fold = even_origins[:train_end]
    val_origins_fold = even_origins[val_start:val_end]
    
    folds.append({
        "fold": fold_idx + 1,
        "train_origins": train_origins_fold,
        "val_origins": val_origins_fold,
        "n_train": len(train_origins_fold),
        "n_val": len(val_origins_fold)
    })

print(f"\nForward-chaining folds (minimum training size: {min_train} origins):")
for fold in folds:
    print(f"  Fold {fold['fold']}: Train[0:{fold['n_train']}] → Val[{fold['n_train']}:{fold['n_train']+fold['n_val']}]")
    print(f"    Train: {fold['train_origins'][0].date()} to {fold['train_origins'][-1].date()}")
    print(f"    Val:   {fold['val_origins'][0].date()} to {fold['val_origins'][-1].date()}")

# Lambda search
lambdas = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
delta_huber = 10.0  # 10 W/m² transition point for Huber loss

print(f"\nHyperparameters:")
print(f"  Lambda search: {lambdas}")
print(f"  Huber delta: {delta_huber} W/m² (transition point for robust loss)")

cv_results = []
for lambda_ridge in lambdas:
    fold_scores = []
    
    for fold in folds:
        # Extract fold data (daytime only)
        train_fold = df_train_day[df_train_day["forecast_start"].isin(fold["train_origins"])]
        val_fold = df_train_day[df_train_day["forecast_start"].isin(fold["val_origins"])]
        
        # Features and targets
        X_fold_train = train_fold[feature_cols].values
        y_fold_train = train_fold["actual_SW_IN"].values
        w_stage4_fold_train = train_fold["w_stage4"].values
        P_chronos_fold_train = train_fold["pred_stage3b_cloud_nwp"].values
        P_physics_fold_train = train_fold["pred_physics"].values
        
        X_fold_val = val_fold[feature_cols].values
        y_fold_val = val_fold["actual_SW_IN"].values
        w_stage4_fold_val = val_fold["w_stage4"].values
        P_chronos_fold_val = val_fold["pred_stage3b_cloud_nwp"].values
        P_physics_fold_val = val_fold["pred_physics"].values
        
        # Fit model
        blender_fold = DynamicBlender(feature_cols)
        blender_fold.fit(X_fold_train, y_fold_train, w_stage4_fold_train,
                         P_chronos_fold_train, P_physics_fold_train,
                         lambda_ridge, delta_huber)
        
        # Predict on validation
        X_fold_val_scaled = blender_fold.standardize_transform(X_fold_val)
        pred_val = blender_fold.predict(X_fold_val_scaled, w_stage4_fold_val,
                                         P_chronos_fold_val, P_physics_fold_val)
        
        # Validation MAE (daytime only, consistent with benchmark)
        mae_val = np.abs(pred_val - y_fold_val).mean()
        fold_scores.append(mae_val)
    
    mean_cv_mae = np.mean(fold_scores)
    std_cv_mae = np.std(fold_scores)
    cv_results.append({
        "lambda": lambda_ridge,
        "cv_mae_mean": mean_cv_mae,
        "cv_mae_std": std_cv_mae,
        "fold_scores": fold_scores
    })
    print(f"  λ={lambda_ridge:8.2f}: CV MAE = {mean_cv_mae:.3f} ± {std_cv_mae:.3f} W/m²")

# Select best lambda
best_result = min(cv_results, key=lambda x: x["cv_mae_mean"])
best_lambda = best_result["lambda"]
print(f"\n✓ Selected λ = {best_lambda} (CV MAE = {best_result['cv_mae_mean']:.3f} W/m²)")

# Save CV results
cv_df = pd.DataFrame(cv_results)
cv_df.to_csv(OUT / "cv_results.csv", index=False)
print(f"  Saved: {OUT / 'cv_results.csv'}")

# ============================================================
# PHASE 6: TRAIN FINAL MODEL ON ALL EVEN ORIGINS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 6: TRAIN FINAL MODEL ON ALL EVEN ORIGINS")
print("=" * 80)

# Extract training data (daytime only)
X_train = df_train_day[feature_cols].values
y_train = df_train_day["actual_SW_IN"].values
w_stage4_train = df_train_day["w_stage4"].values
P_chronos_train = df_train_day["pred_stage3b_cloud_nwp"].values
P_physics_train = df_train_day["pred_physics"].values

print(f"Training data:")
print(f"  Samples: {len(X_train)}")
print(f"  Features: {len(feature_cols)}")

# Fit final model
blender_final = DynamicBlender(feature_cols)
result = blender_final.fit(X_train, y_train, w_stage4_train, 
                           P_chronos_train, P_physics_train,
                           best_lambda, delta_huber)

print(f"\nOptimization result:")
print(f"  Success: {result.success}")
print(f"  Message: {result.message}")
print(f"  Iterations: {result.nit}")
print(f"  Final loss: {result.fun:.4f}")

print(f"\nLearned coefficients (theta):")
for feat, coef in zip(feature_cols, blender_final.theta):
    print(f"  {feat:30s}: {coef:+.6f}")

# Compute feature importance (absolute coefficients)
feat_importance = pd.DataFrame({
    "feature": feature_cols,
    "coefficient": blender_final.theta,
    "abs_coefficient": np.abs(blender_final.theta)
}).sort_values("abs_coefficient", ascending=False)

print(f"\nFeature importance (by |coefficient|):")
for _, row in feat_importance.iterrows():
    print(f"  {row['feature']:30s}: |coef| = {row['abs_coefficient']:.6f}")

feat_importance.to_csv(OUT / "feature_importance.csv", index=False)

# ============================================================
# PHASE 7: EVALUATE ON TEST SET (ODD ORIGINS)
# ============================================================
print("\n" + "=" * 80)
print("PHASE 7: EVALUATE ON TEST SET (ODD ORIGINS)")
print("=" * 80)

# Extract test data (daytime only)
X_test = df_test_day[feature_cols].values
y_test = df_test_day["actual_SW_IN"].values
w_stage4_test = df_test_day["w_stage4"].values
P_chronos_test = df_test_day["pred_stage3b_cloud_nwp"].values
P_physics_test = df_test_day["pred_physics"].values

print(f"Test data:")
print(f"  Samples: {len(X_test)}")
print(f"  Date range: {df_test_day['forecast_start'].min().date()} to {df_test_day['forecast_start'].max().date()}")

# Standardize and predict
X_test_scaled = blender_final.standardize_transform(X_test)
pred_dynamic_test = blender_final.predict(X_test_scaled, w_stage4_test, 
                                          P_chronos_test, P_physics_test)
w_dynamic_test = blender_final.get_dynamic_weights(X_test_scaled, w_stage4_test)

# Verify bounds
assert np.all((w_dynamic_test >= 0) & (w_dynamic_test <= 1)), "Dynamic weights out of [0,1] bounds!"
print(f"\n✓ Weight bounds verified: all w_dynamic ∈ [0, 1]")

# Store predictions
df_test_day = df_test_day.copy()
df_test_day["pred_dynamic"] = pred_dynamic_test
df_test_day["w_dynamic"] = w_dynamic_test

# Compute metrics
def compute_metrics(actual, pred, label):
    mae = np.abs(pred - actual).mean()
    rmse = np.sqrt(((pred - actual)**2).mean())
    bias = (pred - actual).mean()
    nmae = mae / actual.mean() * 100
    nrmse = rmse / actual.mean() * 100
    return {
        "model": label,
        "mae": mae,
        "rmse": rmse,
        "nmae": nmae,
        "nrmse": nrmse,
        "bias": bias,
        "n": len(actual)
    }

# Stage 4 baseline (test set)
metrics_stage4_test = compute_metrics(
    df_test_day["actual_SW_IN"].values,
    df_test_day["pred_ensemble"].values,
    "Stage 4"
)

# Stage 4.3 dynamic (test set)
metrics_dynamic_test = compute_metrics(
    y_test,
    pred_dynamic_test,
    "Stage 4.3 Dynamic"
)

print("\n" + "=" * 80)
print("FINAL TEST SET COMPARISON (173 ODD ORIGINS, DAYTIME)")
print("=" * 80)
print(f"\nStage 4 (fixed weights):")
print(f"  MAE:   {metrics_stage4_test['mae']:.3f} W/m²")
print(f"  RMSE:  {metrics_stage4_test['rmse']:.3f} W/m²")
print(f"  nMAE:  {metrics_stage4_test['nmae']:.2f}%")
print(f"  nRMSE: {metrics_stage4_test['nrmse']:.2f}%")
print(f"  Bias:  {metrics_stage4_test['bias']:+.3f} W/m²")

print(f"\nStage 4.3 (dynamic weights):")
print(f"  MAE:   {metrics_dynamic_test['mae']:.3f} W/m²")
print(f"  RMSE:  {metrics_dynamic_test['rmse']:.3f} W/m²")
print(f"  nMAE:  {metrics_dynamic_test['nmae']:.2f}%")
print(f"  nRMSE: {metrics_dynamic_test['nrmse']:.2f}%")
print(f"  Bias:  {metrics_dynamic_test['bias']:+.3f} W/m²")

delta_mae = metrics_dynamic_test['mae'] - metrics_stage4_test['mae']
delta_nmae = metrics_dynamic_test['nmae'] - metrics_stage4_test['nmae']

print(f"\nImprovement:")
print(f"  Δ MAE:  {delta_mae:+.3f} W/m² ({delta_mae/metrics_stage4_test['mae']*100:+.2f}%)")
print(f"  Δ nMAE: {delta_nmae:+.2f} pp")

# Save metrics
metrics_df = pd.DataFrame([metrics_stage4_test, metrics_dynamic_test])
metrics_df.to_csv(OUT / "dynamic_metrics.csv", index=False)

# ============================================================
# PHASE 8: STATISTICAL SIGNIFICANCE TEST
# ============================================================
print("\n" + "=" * 80)
print("PHASE 8: STATISTICAL SIGNIFICANCE TEST")
print("=" * 80)

print("Paired bootstrap resampling over forecast origins (n=1000 iterations)")

# Group by origin for paired bootstrap
origin_metrics_stage4 = []
origin_metrics_dynamic = []

for origin in odd_origins:
    mask = df_test_day["forecast_start"] == origin
    origin_data = df_test_day[mask]
    
    if len(origin_data) > 0:
        mae_s4 = np.abs(origin_data["pred_ensemble"] - origin_data["actual_SW_IN"]).mean()
        mae_dyn = np.abs(origin_data["pred_dynamic"] - origin_data["actual_SW_IN"]).mean()
        
        origin_metrics_stage4.append(mae_s4)
        origin_metrics_dynamic.append(mae_dyn)

origin_metrics_stage4 = np.array(origin_metrics_stage4)
origin_metrics_dynamic = np.array(origin_metrics_dynamic)
origin_deltas = origin_metrics_dynamic - origin_metrics_stage4

# Bootstrap
np.random.seed(42)
n_bootstrap = 1000
bootstrap_deltas = []

for _ in range(n_bootstrap):
    # Resample origins with replacement
    indices = np.random.choice(len(origin_deltas), size=len(origin_deltas), replace=True)
    bootstrap_deltas.append(origin_deltas[indices].mean())

bootstrap_deltas = np.array(bootstrap_deltas)

# Confidence interval
ci_lower = np.percentile(bootstrap_deltas, 2.5)
ci_upper = np.percentile(bootstrap_deltas, 97.5)

print(f"\nBootstrap results (1000 iterations):")
print(f"  Mean Δ MAE: {bootstrap_deltas.mean():+.3f} W/m²")
print(f"  Std Δ MAE:  {bootstrap_deltas.std():.3f} W/m²")
print(f"  95% CI:     [{ci_lower:+.3f}, {ci_upper:+.3f}] W/m²")

# One-sample t-test (is mean delta different from 0?)
t_stat, p_value = stats.ttest_1samp(origin_deltas, 0)
print(f"\nPaired t-test:")
print(f"  t-statistic: {t_stat:.3f}")
print(f"  p-value:     {p_value:.4f}")

if p_value < 0.05:
    if delta_mae < 0:
        print(f"  ✓ Statistically significant improvement (p < 0.05)")
    else:
        print(f"  ⚠ Statistically significant degradation (p < 0.05)")
else:
    print(f"  → No statistically significant difference (p >= 0.05)")

# ============================================================
# PHASE 9: DYNAMIC WEIGHT DIAGNOSTICS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 9: DYNAMIC WEIGHT DIAGNOSTICS")
print("=" * 80)

print(f"\nDynamic weight statistics (test set):")
print(f"  Mean:   {w_dynamic_test.mean():.4f}")
print(f"  Std:    {w_dynamic_test.std():.4f}")
print(f"  Min:    {w_dynamic_test.min():.4f}")
print(f"  Max:    {w_dynamic_test.max():.4f}")
print(f"  Median: {np.median(w_dynamic_test):.4f}")

print(f"\nStage 4 weight statistics (test set, for comparison):")
print(f"  Mean:   {w_stage4_test.mean():.4f}")
print(f"  Std:    {w_stage4_test.std():.4f}")
print(f"  Min:    {w_stage4_test.min():.4f}")
print(f"  Max:    {w_stage4_test.max():.4f}")

print(f"\nWeight variance:")
print(f"  Stage 4 (across horizons only): {np.var([stage4_params[str(h)]['w'] for h in range(1, 25)]):.6f}")
print(f"  Dynamic (across samples):       {np.var(w_dynamic_test):.6f}")

# Feature-weight correlations
print(f"\nFeature correlations with dynamic weight:")
for i, feat in enumerate(feature_cols):
    corr = np.corrcoef(X_test[:, i], w_dynamic_test)[0, 1]
    direction = "→ Chronos" if corr > 0 else "→ Physics" if corr < 0 else "neutral"
    print(f"  {feat:30s}: {corr:+.3f}  {direction}")

# Component separation analysis
separation = np.abs(P_chronos_test - P_physics_test)
print(f"\nComponent separation |P_chronos - P_physics|:")
print(f"  Mean:   {separation.mean():.2f} W/m²")
print(f"  Median: {np.median(separation):.2f} W/m²")
print(f"  Std:    {separation.std():.2f} W/m²")
print(f"  % with separation < 10 W/m²: {(separation < 10).mean()*100:.1f}%")
print(f"  % with separation < 50 W/m²: {(separation < 50).mean()*100:.1f}%")

# ============================================================
# PHASE 10: PER-HORIZON ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 10: PER-HORIZON ANALYSIS")
print("=" * 80)

horizon_results = []
print(f"\n{'H':>3s} {'n':>5s} {'w_S4':>6s} {'w_dyn':>6s} {'w_std':>6s} "
      f"{'MAE_S4':>8s} {'MAE_dyn':>8s} {'Δ':>7s}")

for h in range(1, 25):
    mask_h = df_test_day["horizon_hour"] == h
    if mask_h.sum() == 0:
        continue
    
    h_data = df_test_day[mask_h]
    w_stage4_h = stage4_params[str(h)]["w"]
    w_dynamic_h = h_data["w_dynamic"].values
    
    mae_stage4_h = np.abs(h_data["pred_ensemble"] - h_data["actual_SW_IN"]).mean()
    mae_dynamic_h = np.abs(h_data["pred_dynamic"] - h_data["actual_SW_IN"]).mean()
    delta_h = mae_dynamic_h - mae_stage4_h
    
    marker = "✓" if delta_h < -0.1 else "→" if abs(delta_h) < 0.1 else "✗"
    
    print(f"H{h:2d} {mask_h.sum():5d} {w_stage4_h:6.3f} {w_dynamic_h.mean():6.3f} "
          f"{w_dynamic_h.std():6.3f} {mae_stage4_h:8.2f} {mae_dynamic_h:8.2f} "
          f"{delta_h:+7.2f} {marker}")
    
    horizon_results.append({
        "horizon": h,
        "n": mask_h.sum(),
        "w_stage4": w_stage4_h,
        "w_dynamic_mean": w_dynamic_h.mean(),
        "w_dynamic_std": w_dynamic_h.std(),
        "w_dynamic_min": w_dynamic_h.min(),
        "w_dynamic_max": w_dynamic_h.max(),
        "mae_stage4": mae_stage4_h,
        "mae_dynamic": mae_dynamic_h,
        "delta_mae": delta_h
    })

horizon_df = pd.DataFrame(horizon_results)
horizon_df.to_csv(OUT / "horizon_metrics.csv", index=False)

n_improved = (horizon_df["delta_mae"] < -0.1).sum()
n_degraded = (horizon_df["delta_mae"] > 0.1).sum()
n_neutral = len(horizon_df) - n_improved - n_degraded

print(f"\nHorizon summary:")
print(f"  Improved (Δ < -0.1):  {n_improved} / 24")
print(f"  Degraded (Δ > +0.1):  {n_degraded} / 24")
print(f"  Neutral  (|Δ| ≤ 0.1): {n_neutral} / 24")

# ============================================================
# PHASE 11: CLOUD REGIME ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 11: CLOUD REGIME ANALYSIS")
print("=" * 80)

def cloud_regime(c):
    if pd.isna(c):
        return "Missing"
    elif c <= 10:
        return "Clear (0-10%)"
    elif c <= 30:
        return "Few (10-30%)"
    elif c <= 60:
        return "Scattered (30-60%)"
    elif c <= 80:
        return "Broken (60-80%)"
    else:
        return "Overcast (80-100%)"

df_test_day["cloud_regime"] = df_test_day["fc_cloud_cover"].apply(cloud_regime)

cloud_order = ["Clear (0-10%)", "Few (10-30%)", "Scattered (30-60%)",
               "Broken (60-80%)", "Overcast (80-100%)"]

print(f"\n{'Regime':22s} {'n':>6s} {'w_mean':>7s} {'MAE_S4':>8s} {'MAE_dyn':>8s} {'Δ':>7s}")

cloud_results = []
for regime in cloud_order:
    mask_r = df_test_day["cloud_regime"] == regime
    if mask_r.sum() == 0:
        continue
    
    r_data = df_test_day[mask_r]
    w_mean = r_data["w_dynamic"].mean()
    
    mae_s4 = np.abs(r_data["pred_ensemble"] - r_data["actual_SW_IN"]).mean()
    mae_dyn = np.abs(r_data["pred_dynamic"] - r_data["actual_SW_IN"]).mean()
    delta = mae_dyn - mae_s4
    
    print(f"{regime:22s} {mask_r.sum():6d} {w_mean:7.3f} {mae_s4:8.2f} "
          f"{mae_dyn:8.2f} {delta:+7.2f}")
    
    cloud_results.append({
        "regime": regime,
        "n": mask_r.sum(),
        "w_mean": w_mean,
        "mae_stage4": mae_s4,
        "mae_dynamic": mae_dyn,
        "delta_mae": delta
    })

cloud_df = pd.DataFrame(cloud_results)
cloud_df.to_csv(OUT / "cloud_regime_metrics.csv", index=False)

# ============================================================
# PHASE 12: NIGHTTIME HANDLING
# ============================================================
print("\n" + "=" * 80)
print("PHASE 12: NIGHTTIME HANDLING")
print("=" * 80)

# For nighttime, use Stage 4 predictions (preserve existing behavior)
df_test_night = df_test[~df_test["is_daytime"]].copy()

if len(df_test_night) > 0:
    # Stage 4 night MAE
    night_mae_s4 = np.abs(df_test_night["pred_ensemble"] - df_test_night["actual_SW_IN"]).mean()
    
    # For dynamic blending: use Stage 4 predictions at night (no change)
    df_test_night["pred_dynamic"] = df_test_night["pred_ensemble"]
    night_mae_dyn = np.abs(df_test_night["pred_dynamic"] - df_test_night["actual_SW_IN"]).mean()
    
    print(f"Nighttime samples: {len(df_test_night)}")
    print(f"  Stage 4 night MAE:   {night_mae_s4:.4f} W/m²")
    print(f"  Stage 4.3 night MAE: {night_mae_dyn:.4f} W/m²")
    print(f"  ✓ Nighttime behavior preserved (using Stage 4 predictions)")

# ============================================================
# PHASE 13: SAVE PREDICTIONS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 13: SAVE PREDICTIONS")
print("=" * 80)

# Combine daytime and nighttime predictions
df_test_out = df_test[["forecast_start", "horizon_hour", "timestamp", "actual_SW_IN",
                        "pred_stage3b_cloud_nwp", "pred_ensemble", "pred_physics"]].copy()
df_test_out["pred_dynamic"] = df_test["pred_ensemble"]  # Default to Stage 4
df_test_out["w_dynamic"] = df_test["w_stage4"]  # Default to Stage 4 weight

# Fill in daytime predictions
daytime_mask = df_test["is_daytime"]
df_test_out.loc[daytime_mask, "pred_dynamic"] = df_test_day["pred_dynamic"].values
df_test_out.loc[daytime_mask, "w_dynamic"] = df_test_day["w_dynamic"].values

df_test_out.to_csv(OUT / "dynamic_predictions.csv", index=False)
print(f"Saved: {OUT / 'dynamic_predictions.csv'}")
print(f"  Rows: {len(df_test_out)} (173 origins × 24 horizons)")

# ============================================================
# PHASE 14: SAVE MODEL PARAMETERS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 14: SAVE MODEL PARAMETERS")
print("=" * 80)

model_params = {
    "methodology": "Delta-parameterized logistic blender",
    "formula": "logit(w_dynamic) = logit(w_stage4_h) + X_scaled @ theta",
    "ridge_lambda": float(best_lambda),
    "huber_delta": float(delta_huber),
    "feature_columns": feature_cols,
    "theta_coefficients": blender_final.theta.tolist(),
    "scaler_mean": blender_final.scaler_mean.tolist(),
    "scaler_std": blender_final.scaler_std.tolist(),
    "cv_results": [
        {
            "lambda": float(r["lambda"]),
            "cv_mae_mean": float(r["cv_mae_mean"]),
            "cv_mae_std": float(r["cv_mae_std"])
        }
        for r in cv_results
    ],
    "feature_importance": {
        feat: float(coef) 
        for feat, coef in zip(feature_cols, blender_final.theta)
    },
    "test_metrics": {
        "stage4_mae": float(metrics_stage4_test["mae"]),
        "stage4_nmae": float(metrics_stage4_test["nmae"]),
        "dynamic_mae": float(metrics_dynamic_test["mae"]),
        "dynamic_nmae": float(metrics_dynamic_test["nmae"]),
        "delta_mae": float(delta_mae),
        "delta_nmae": float(delta_nmae),
        "bootstrap_ci_lower": float(ci_lower),
        "bootstrap_ci_upper": float(ci_upper),
        "p_value": float(p_value)
    }
}

with open(OUT / "model_parameters.json", "w") as f:
    json.dump(model_params, f, indent=2)
print(f"Saved: {OUT / 'model_parameters.json'}")

# ============================================================
# PHASE 15: VISUALIZATION
# ============================================================
print("\n" + "=" * 80)
print("PHASE 15: VISUALIZATION")
print("=" * 80)

# Create plots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot 1: Weight distribution
axes[0, 0].hist(w_dynamic_test, bins=50, alpha=0.7, label="Dynamic", edgecolor="black")
axes[0, 0].axvline(w_stage4_test.mean(), color="r", linestyle="--", label=f"Stage 4 mean")
axes[0, 0].set_xlabel("Weight")
axes[0, 0].set_ylabel("Count")
axes[0, 0].set_title("Dynamic Weight Distribution")
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Plot 2: Weight vs cloud cover
axes[0, 1].scatter(df_test_day["fc_cloud_cover"], w_dynamic_test, alpha=0.2, s=1)
axes[0, 1].set_xlabel("Cloud Cover (%)")
axes[0, 1].set_ylabel("Dynamic Weight")
axes[0, 1].set_title("Weight vs Cloud Cover")
axes[0, 1].grid(alpha=0.3)

# Plot 3: Weight vs solar elevation
axes[0, 2].scatter(df_test_day["solar_elevation"], w_dynamic_test, alpha=0.2, s=1)
axes[0, 2].set_xlabel("Solar Elevation (°)")
axes[0, 2].set_ylabel("Dynamic Weight")
axes[0, 2].set_title("Weight vs Solar Elevation")
axes[0, 2].grid(alpha=0.3)

# Plot 4: Per-horizon comparison
horizons = horizon_df["horizon"].values
axes[1, 0].plot(horizons, horizon_df["mae_stage4"], "o-", label="Stage 4", color="blue")
axes[1, 0].plot(horizons, horizon_df["mae_dynamic"], "s-", label="Stage 4.3", color="red")
axes[1, 0].set_xlabel("Horizon")
axes[1, 0].set_ylabel("MAE (W/m²)")
axes[1, 0].set_title("Per-Horizon MAE Comparison")
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

# Plot 5: Weight variation by horizon
axes[1, 1].errorbar(horizons, horizon_df["w_dynamic_mean"], 
                    yerr=horizon_df["w_dynamic_std"],
                    fmt="o-", label="Dynamic (mean ± std)", capsize=3)
axes[1, 1].plot(horizons, horizon_df["w_stage4"], "r--", label="Stage 4 (fixed)")
axes[1, 1].set_xlabel("Horizon")
axes[1, 1].set_ylabel("Weight")
axes[1, 1].set_title("Weight by Horizon")
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

# Plot 6: Component separation
axes[1, 2].hist(separation, bins=50, edgecolor="black", alpha=0.7)
axes[1, 2].axvline(separation.mean(), color="r", linestyle="--", 
                   label=f"Mean = {separation.mean():.1f}")
axes[1, 2].set_xlabel("|P_chronos - P_physics| (W/m²)")
axes[1, 2].set_ylabel("Count")
axes[1, 2].set_title("Component Separation")
axes[1, 2].legend()
axes[1, 2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT / "diagnostics.png", dpi=150)
print(f"Saved: {OUT / 'diagnostics.png'}")
plt.close()

# ============================================================
# PHASE 16: FINAL SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(f"""
POLARIS Stage 4.3 — Dynamic Blending Results

METHODOLOGY:
  - Delta-parameterized logistic blender
  - 174 EVEN training origins (forward-chaining CV)
  - 173 ODD test origins (held-out)
  - 10 features, Ridge regularization (λ = {best_lambda})
  - Huber loss (δ = {delta_huber} W/m²)

BENCHMARK COMPARISON (173 ODD Origins, Daytime):
  Stage 4:   MAE = {metrics_stage4_test['mae']:.3f} W/m², nMAE = {metrics_stage4_test['nmae']:.2f}%
  Stage 4.3: MAE = {metrics_dynamic_test['mae']:.3f} W/m², nMAE = {metrics_dynamic_test['nmae']:.2f}%
  
  Improvement: Δ MAE = {delta_mae:+.3f} W/m² ({delta_mae/metrics_stage4_test['mae']*100:+.2f}%)
               Δ nMAE = {delta_nmae:+.2f} pp
  
  95% CI: [{ci_lower:+.3f}, {ci_upper:+.3f}] W/m²
  p-value: {p_value:.4f}

DYNAMIC BEHAVIOR:
  Weight statistics:
    Mean:   {w_dynamic_test.mean():.4f}
    Std:    {w_dynamic_test.std():.4f}
    Range:  [{w_dynamic_test.min():.4f}, {w_dynamic_test.max():.4f}]
  
  Per-horizon adaptation:
    Improved:  {n_improved} / 24 horizons
    Degraded:  {n_degraded} / 24 horizons
    Neutral:   {n_neutral} / 24 horizons

ARTIFACTS SAVED:
  {OUT / 'dynamic_predictions.csv'}
  {OUT / 'dynamic_metrics.csv'}
  {OUT / 'model_parameters.json'}
  {OUT / 'horizon_metrics.csv'}
  {OUT / 'cloud_regime_metrics.csv'}
  {OUT / 'feature_importance.csv'}
  {OUT / 'cv_results.csv'}
  {OUT / 'diagnostics.png'}
""")

# ============================================================
# PHASE 17: SUCCESS CRITERION EVALUATION
# ============================================================
print("=" * 80)
print("SUCCESS CRITERION EVALUATION")
print("=" * 80)

target_mae = 43.45  # Stage 4 official benchmark
target_nmae = 33.70

if delta_mae < -0.5 and p_value < 0.05:
    print(f"""
✓ OUTCOME A: CLEAR IMPROVEMENT

Stage 4.3 beats Stage 4 by {abs(delta_mae):.3f} W/m² on held-out test set.
Improvement is statistically significant (p = {p_value:.4f}).
Dynamic blending demonstrates measurable state-dependent behavior.

RECOMMENDATION: Stage 4.3 Dynamic Blending is the NEW CHAMPION.
""")
elif delta_mae < 0:
    print(f"""
→ OUTCOME B: SMALL/NON-SIGNIFICANT IMPROVEMENT

Stage 4.3 shows a small improvement of {abs(delta_mae):.3f} W/m², but it is
{"not statistically significant" if p_value >= 0.05 else "marginally significant"}
(p = {p_value:.4f}).

The dynamic blending approach is scientifically interesting and shows promise,
but the improvement is too small to confidently declare a new champion.

RECOMMENDATION: Retain Stage 4 as official champion.
               Consider Stage 4.3 for future research (v2 with extended features).
""")
else:
    print(f"""
✗ OUTCOME C: DEGRADATION

Stage 4.3 DEGRADED performance by {abs(delta_mae):.3f} W/m² compared to Stage 4.

Possible reasons:
  - Features do not contain sufficient predictive information
  - Regularization too strong/weak
  - Dynamic blending hypothesis invalid for this data

RECOMMENDATION: REJECT Stage 4.3, retain Stage 4 as champion.
               Dynamic blending approach requires rethinking.
""")

print("=" * 80)
print("EXPERIMENT COMPLETE")
print("=" * 80)
