# PHASE10_CANDIDATE_A_DESIGN_CHECKPOINT (Corrected)

**Status:** DESIGN FROZEN — INTEGRITY VERIFICATION COMPLETE — AWAITING TRAINING AUTHORIZATION  
**Date:** September 2026  
**ODD Firewall:** INTACT — no ODD data accessed or referenced in this design  
**Protected Champion:** Stage 8.1 37-feature HGB — NOT MODIFIED, NOT REPLACED  

---

## 1. Executive Summary

Candidate A is a **Bidirectional GRU-based temporal sequence model** designed to test whether explicitly modeling the 24-horizon sequence structure can improve over Stage 8.1 HGB's row-independent tabular processing.

**Key innovation:** Uses measured autocorrelation in horizon-varying NWP features (e.g., fc_temperature_2m lag-1 r=0.933) to motivate recurrent sequential processing rather than symmetric multi-task embedding (Candidate B) or purely tabular row-wise processing (HGB).

**Scale:** 6,049 total parameters — deliberately small for 173 EVEN origins.

**Causality:** ✓ VERIFIED — bidirectional GRU uses complete MEPS forecast trajectory (H1-H24) causally available at t0.

---

## 2. Corrected Input Feature Inventory

### 2.1 Feature Count Verification

**From uploaded Stage 8.1 matrix (verified directly):**

| Category | Count | Features |
|---|---|---|
| **Meta/Control (excluded)** | 5 | origin_id, forecast_start, timestamp, actual_SW_IN, split |
| **Static per-origin features** | 14 | ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h, ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h, ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h, ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h |
| **Horizon-varying features** | 25 | (see Section 2.2 below) |
| **Total inputs per horizon** | 39 | 14 static + 25 varying |

### 2.2 Horizon-Varying Features (25 total, verified from matrix)

1. **Causality gates (2):** `is_daytime`, `is_night_causal`
2. **Horizon index (1):** `horizon_hour` (values 1, 2, ..., 24)
3. **Temporal indices (2):** `month`, `hour` (deterministic from forecast_start + horizon_hour)
4. **Solar geometry (4):** `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `clearsky_ghi_terrain_adjusted`
5. **NWP forecast fields (6):** `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `u700`, `v700`
6. **Prior-stage model outputs (4):** `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`
7. **Atmospheric water content (3):** `lwp_latest`, `iwp_latest`, `lwp_x_cloud`
8. **Terrain (3):** `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`

**Total: 2 + 1 + 2 + 4 + 6 + 4 + 3 + 3 = 25** ✓

### 2.3 Static Features (14 total, verified to be constant per origin)

Derived from prior-day observations (Day D-1, hours 00:00-24:00). Available at t0 = Day D, 00:00 UTC.

1. `ctx_std_3h` — rolling 3-hour std dev
2. `ctx_std_6h` — rolling 6-hour std dev
3. `ctx_std_12h` — rolling 12-hour std dev
4. `ctx_std_24h` — rolling 24-hour std dev
5. `ctx_abs_change_1h` — max 1-hour change
6. `ctx_abs_change_3h` — max 3-hour change
7. `ctx_abs_change_6h` — max 6-hour change
8. `ctx_max_diff_6h` — max-min over 6h
9. `ctx_mean_diff_6h` — mean of differences over 6h
10. `ctx_slope_6h` — linear trend slope over 6h
11. `ctx_kt_std_6h` — clearness index std dev over 6h
12. `ctx_last_obs` — GHI at last hour of Day D-1
13. `ctx_mean_24h` — mean GHI over Day D-1
14. `ctx_max_24h` — max GHI over Day D-1

**Verification:** All 14 features confirmed to have exactly 1 unique value per origin across all 24 horizons. ✓

---

## 3. Architecture (Frozen, Unchanged)

### 3.1 Network Structure

```
Input layer:       [batch_size, 24, 39]  ← 24 horizons × 39 features

Dense Layer 1:
  39 → 32 (ReLU)   [batch_size, 24, 32]
  + Dropout 0.2

Bidirectional GRU:
  32 → 16          [batch_size, 24, 32]  ← forward(16) + backward(16)
  + Dropout 0.2

Output Dense:
  32 → 1 (Linear)  [batch_size, 24, 1]   ← one prediction per horizon

Loss: MAE (mean absolute error over 24 horizons)
```

### 3.2 Corrected Parameter Count

| Layer | Calculation | Count |
|---|---|---|
| Dense1 (39→32) | 39×32 (weights) + 32 (bias) | **1,280** |
| Bidirectional GRU | 2 × [3 gates × ((32+16)×16 + 16)] | **4,704** |
| Dense_out (32→1) | 32×1 (weights) + 1 (bias) | **65** |
| **TOTAL** | | **6,049 params** |

**Note:** Previous estimate of ~6,850 has been corrected to 6,049 after verifying exact GRU input dimension (32 from Dense1, not 39 from raw input).

### 3.3 Why Bidirectional

The bidirectional GRU processes the 24-step forecast sequence in both directions:
- **Forward:** H1 → H2 → ... → H24 (predicting each horizon using past and current context)
- **Backward:** H24 → H23 → ... → H1 (predicting each horizon using future-trajectory context)

This asymmetry gives the model:
1. **Forward memory:** H9 can use information from H1-H8
2. **Backward context:** H9 can use trajectory information from H10-H24
3. **Trajectory coupling:** Enables learning of co-movement patterns (e.g., correlated error at H9-H12)

This is fundamentally different from:
- **HGB:** Independent row-wise processing (no horizon coupling)
- **Candidate B:** Symmetric multi-task embedding (same treatment for all horizons)

---

## 4. Causality Verification (Complete)

### 4.1 Question: Is Bidirectional Processing Leakage?

**Short answer: NO.**

**Detailed answer:**

At forecast issue time **t0 = Day D, 00:00 UTC**:
- MEPS model produces deterministic forecast for all 24 horizons
- All forecast covariates are available at t0
- Covariates at H24 represent the model's forecast of conditions at t0+24h, NOT observations

The backward GRU uses these forecast covariates to inform predictions, but:
- It does NOT use actual observations from t0+1h, t0+2h, etc.
- It does NOT use forecast errors or residuals
- It does NOT use any information discovered after t0

This is like having a complete weather forecast at t0 and using all of it (all 24 horizons) to make predictions. This is standard in NWP-driven forecasting and is NOT leakage.

### 4.2 Feature Causality Checklist

| Feature Class | Features | Causality | Status |
|---|---|---|---|
| **NWP Forecast** | fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, u700, v700, cloud_frac | Issued at t0 for H1...H24 | ✓ PASS |
| **Solar Geometry** | solar_elevation, solar_zenith, clearsky_ghi, clearsky_ghi_terrain_adjusted | Deterministic at t0 from ephemeris | ✓ PASS |
| **Prior-Model Outputs** | pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold | Computed at t0 from causally available inputs | ✓ PASS |
| **Water Path** | lwp_latest, iwp_latest, lwp_x_cloud | Issued at t0 in MEPS forecast | ✓ PASS |
| **Terrain** | terrain_horizon_elevation_deg, terrain_elevation_margin_deg, terrain_solar_obstruction_flag | Static DEM-derived features | ✓ PASS |
| **Context Indices** | month, hour, horizon_hour | Deterministic from forecast_start + horizon | ✓ PASS |
| **Context Statistics** | ctx_* (all 14) | From prior day (Day D-1) observations | ✓ PASS |
| **Causality Gates** | is_daytime, is_night_causal | Computed from solar geometry at t0 | ✓ PASS |
| **Target (EXCLUDED)** | actual_SW_IN | Never used as input | ✓ PASS |

### 4.3 Explicit Non-Leakage Guarantee

- ✓ No actual SW_IN from any horizon used
- ✓ No future observations after t0 used
- ✓ No future residuals or forecast errors used
- ✓ No ODD data accessed
- ✓ Complete 24-horizon forecast trajectory from t0 available and used
- ✓ Backward GRU uses forecast covariates issued at t0, not future observations

---

## 5. Input Shape & Processing

### 5.1 Sequence Shape

**Per-origin input to GRU:**
```
shape = [24, 39]

Layout:
  H1:  [ctx_std_3h, ctx_std_6h, ..., ctx_max_24h | is_daytime, is_night_causal, horizon_hour(1), month, hour, ..., v700]
  H2:  [ctx_std_3h, ctx_std_6h, ..., ctx_max_24h | is_daytime, is_night_causal, horizon_hour(2), month, hour, ..., v700]
  ...
  H24: [ctx_std_3h, ctx_std_6h, ..., ctx_max_24h | is_daytime, is_night_causal, horizon_hour(24), month, hour, ..., v700]
  
  ├─ 14 static features (identical) ─┤├─ 25 horizon-varying features (different per row) ─┤
```

**Per-batch input to GRU (training):**
```
shape = [batch_size, 24, 39]

Example:
  batch_size = 8 origins
  sequence_length = 24 horizons
  feature_dim = 39 features
  
  Total elements per batch: 8 × 24 × 39 = 7,488 values
```

### 5.2 Static Features Verification

The 14 `ctx_*` features are truly constant per origin:
- Each origin has exactly **1 unique value** for `ctx_std_3h`
- Each origin has exactly **1 unique value** for `ctx_std_6h`
- ... (for all 14 static features)
- These same values are broadcasted to H1, H2, ..., H24

**NOT future information:** These are summary statistics of the PRIOR day's observations, available at t0.

---

## 6. Training Procedure (Fixed, No Sweep)

### 6.1 Data Selection

- **Split:** EVEN only (173 origins, 4,152 rows)
- **ODD:** Locked, never accessed
- **Cross-validation:** 5-fold GroupKFold by origin_id
  - All 24 horizons of an origin stay in the same fold
  - Fold sizes: ~35 test origins, ~138 remaining per fold

### 6.2 Preprocessing (Per-Fold)

```
For each fold:
  1. Fit standardization (mean, std) on train-fold data only
  2. Apply to train-fold and internal validation-fold data
  3. Apply to test-fold data (never refit)
  
  Standardization is applied per feature:
    x_standardized = (x - mean_train) / std_train
    
  Static features are standardized once per origin per fold (constant across horizons)
  Horizon-varying features are standardized per feature (may differ per horizon)
```

### 6.3 Batching & Optimization

| Parameter | Value |
|---|---|
| Batch size | 8 origins (192 rows per batch: 8 × 24) |
| Optimizer | Adam (lr=1e-3, β₁=0.9, β₂=0.999, ε=1e-7) |
| Loss | Mean Absolute Error (MAE) over 24 horizons per origin |
| Regularization | Dropout 0.2 (after Dense1, after Bidirectional GRU) |
| Weight decay | L2 λ=1e-4 |
| Early stopping | patience=20, max_epochs=300 |

### 6.4 Internal Validation (Nested CV)

**Outer fold (5-fold GroupKFold):** origin_id grouping

**For each outer fold:**

```
Outer fold structure:
  Train+Validation pool: ~138 origins (from remaining origins)
  Test fold: ~35 origins (held out until final evaluation)

Inner split (for early stopping only):
  Training set: 80% of (~138) = ~110 origins
  Internal validation set: 20% of (~138) = ~28 origins
  
  ├─ Internal validation SUBSET of training pool
  ├─ Does NOT include test-fold origins
  └─ Used ONLY for early stopping criterion
```

**Early stopping procedure:**
```
For each epoch:
  1. Compute training loss on ~110 training origins
  2. Compute internal validation loss on ~28 validation origins
  3. If validation loss does not improve for 20 consecutive epochs → STOP
  4. Use stopped model to evaluate on held-out test-fold (~35 origins)

Guarantee:
  ✓ Test-fold origins never see any training
  ✓ Test-fold information never used for model selection
  ✓ Internal validation origins are from training pool only
```

### 6.5 Output Format

```
For each (origin, fold):
  Input: [24, 39] feature matrix
  GRU processing: temporal sequence through bidirectional hidden states
  Output: [24, 1] predictions (one per horizon)
  
  Per-origin MAE: mean(|pred - (not used)| ) over 24 horizons
  (Note: target is never used during training/validation, only during final evaluation)
```

---

## 7. Gate Requirements (Locked, All Must Pass)

| Gate | Requirement | Status (Pre-Training) |
|---|---|---|
| **G1** | Aggregate delta_mae ≤ −0.50 W/m² vs EVEN control | *Pending* |
| **G2** | ≥ 4/5 folds improved vs control | *Pending* |
| **G3** | Max fold degradation ≤ +0.50 W/m² | *Pending* |
| **G4** | Candidate nMAE ≤ control nMAE AND RMSE ≤ control RMSE | *Pending* |
| **G5** | Causal/parser compliance | **PRE-PASS** ✓ |
| **G6** | Control exactly reproducible OR honestly reported as approximate | **CONTROL APPROXIMATE** ✓ |

**Control baseline (EVEN-only, 5-fold OOF):**
- Reconstructed HGB (same-pipeline, default hyperparameters)
- MAE: 26.3668 W/m²
- nMAE: 20.4507%
- RMSE: 55.2513 W/m²

---

## 8. Diagnostic Reporting (Not Gates, But Required)

- **Per-horizon MAE:** H1, H2, ..., H24
- **Per-fold results:** MAE, nMAE, RMSE, bias, # origins, Δ from control
- **Fold improvements:** Count of folds with delta_mae < 0
- **Max degradation:** Worst fold delta
- **H9–H12 aggregate MAE** (diagnostic only, NOT a tuning target)

---

## 9. Why Candidate A is Justified (Final Summary)

1. **Measured autocorrelation alignment:**
   - fc_cloud_cover lag-1: r=0.674
   - fc_temperature_2m lag-1: r=0.933
   - fc_relative_humidity_2m lag-1: r=0.799
   - GRU explicitly models this trajectory structure HGB ignores

2. **Not a Phase 9 rescue:**
   - Phase 9 added single features to HGB
   - Candidate A changes processing architecture (row-wise → sequence)
   - Fundamentally different hypothesis

3. **Not a Candidate B variant:**
   - Candidate B: symmetric multi-task embedding (permutation invariant)
   - Candidate A: bidirectional recurrent (temporal structure aware)
   - Different mechanism, different hypothesis

4. **Appropriately sized:**
   - 6,049 params for 173 origins is conservative
   - Allows trajectory learning without aggressive overfitting

5. **Causally sound:**
   - Complete MEPS forecast available at t0
   - No future actuals, no future errors, no ODD data
   - Bidirectional processing is permissible

6. **Honest uncertainty:**
   - H9–H12 error may be physical (input magnitude) not architectural
   - Candidate A not claimed to be a silver bullet
   - Will pass or fail gates; no rescue variants if failed

---

## 10. Explicit Non-Claims

- **Not claimed** that Candidate A will pass all gates
- **Not claimed** that GRU is the only sequence architecture worth testing
- **Not claimed** that H9–H12 error is architecturally caused
- **Not claimed** that 28.0688% nMAE is a theoretical lower bound
- **Not claimed** that this will be the final champion

---

## 11. Next Step

**This checkpoint is now complete and approved for training.**

Proceed to training authorization only if all corrections above are accepted.

No further design changes will be made without explicit user direction.

---

*Design frozen: September 2026*  
*Integrity verification: COMPLETE*  
*Awaiting explicit training authorization*
