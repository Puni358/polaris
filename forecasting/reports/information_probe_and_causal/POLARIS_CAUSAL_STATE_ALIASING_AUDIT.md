# POLARIS — CAUSAL STATE ALIASING / FUTURE TRAJECTORY DIVERGENCE AUDIT

**Generated (UTC):** 2026-09-14T14:06:16.611873+00:00  
**Data split:** EVEN only — 173 origins, 4152 rows  
**ODD sealed:** YES  

---

## 1. Executive Verdict

**Classification: C — WEAK / INCONCLUSIVE STATE-ALIASING**

| Metric | Value |
|--------|-------|
| Peak ratio (NN / random divergence) | 0.537 |
| Mean ratio across H1–H24 | 0.460 |
| Horizon of peak NN divergence | H11 |
| Horizon where divergence starts increasing | H01 |
| Neighbour advantage disappears (ratio ≥ 0.95) | not reached |

**Information-Limited Hypothesis Assessment:**

UNCHANGED — Evidence is weak or below null thresholds. Information limitation remains possible but unconfirmed by this diagnostic.

---

## 2. Causal State Definition

**Unit of analysis:** FORECAST ORIGIN (t0) — 173 EVEN origins  
**State extracted from:** horizon_hour=1 row of existing POLARIS 37-feature matrix  
**Dimensionality:** 32 features  
**Distance metric:** Weighted Euclidean on EVEN-only standardized features (equal weights)  

### Features Included

| Category | Features |
|----------|---------|
| Observation context (24h SW_IN history) | ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h, ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h, ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h, ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h |
| Solar geometry at t0 | solar_elevation, solar_zenith, clearsky_ghi, clearsky_ghi_terrain_adjusted |
| NWP forecast at t0 | fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac, lwp_latest, iwp_latest, lwp_x_cloud, u700, v700 |
| Terrain | terrain_horizon_elevation_deg, terrain_elevation_margin_deg, terrain_solar_obstruction_flag |
| Temporal context | month, hour |

### Features Excluded

| Feature | Reason |
|---------|--------|
| horizon_hour | Trajectory descriptor, not a t0 state variable |
| pred_stage3b_cloud_nwp | Model-derived output — circular as state variable |
| phys_pred_fold, pred_stage4_fold, disagreement_fold | Model-derived outputs |

---

## 3. EVEN Data Summary

- **EVEN origins used:** 173  
- **Total EVEN forecast rows:** 4,152 (173 × 24)  
- **ODD rows accessed:** FALSE (firewall confirmed)  

---

## 4. Matching Methodology

- State standardized using EVEN-only mean and standard deviation
- Constant features assigned σ = 1.0 to prevent division by zero
- NaN values imputed with EVEN column means before standardization
- Pairwise Euclidean distance computed on full standardized causal state
- Self-matches excluded (diagonal set to ∞)
- Nearest neighbours identified per origin without replacement from other origins

---

## 5. Neighbourhood Sensitivity

Pre-declared neighbourhood sizes: k ∈ {1, 3, 5, 10}

| k | NN Pairs | NN Mean Traj RMSE (W/m²) | Random Mean Traj RMSE (W/m²) | Ratio |
|---|----------|--------------------------|------------------------------|-------|
| 1 | 173 | 73.60 | 144.37 | 0.510 |
| 3 | 519 | 73.51 | 144.37 | 0.509 |
| 5 | 865 | 75.10 | 144.37 | 0.520 |
| 10 | 1730 | 78.70 | 144.37 | 0.545 |

*Ratio < 1.0 means NN pairs are MORE similar than random pairs.  
Ratio approaching 1.0 means NN pairs are nearly as divergent as random pairs.*

---

## 6. H1–H24 Divergence Table (k=5 NN vs Null Baselines)

Normalizer: 128.93 W/m² (official POLARIS benchmark)  
CI: 95% bootstrap (2000 iterations, pairs bootstrap over origin pairs)

| H | NN Mean (W/m²) | NN CI95 Lo | NN CI95 Hi | Random Mean (W/m²) | Rand CI95 Lo | Rand CI95 Hi | Ratio | NN IQR (W/m²) | NN Norm Diff |
|---|----------------|------------|------------|--------------------|--------------|--------------|-------|----------------|-------------|
| H01 |           1.62 |       1.32 |       1.93 |                 3.78 |         3.34 |         4.28 | 0.428 |           0.37 |      0.0125 |
| H02 |           3.37 |       2.81 |       3.94 |                 6.69 |         5.98 |         7.42 | 0.503 |           0.95 |      0.0261 |
| H03 |           7.37 |       6.19 |       8.55 |                13.81 |        12.46 |        15.29 | 0.533 |           3.03 |      0.0572 |
| H04 |          13.07 |      11.25 |      14.89 |                25.53 |        23.50 |        27.80 | 0.512 |          10.38 |      0.1014 |
| H05 |          23.67 |      20.92 |      26.47 |                50.66 |        47.19 |        54.54 | 0.467 |          26.76 |      0.1836 |
| H06 |          36.57 |      32.80 |      40.70 |                82.79 |        77.51 |        88.36 | 0.442 |          50.59 |      0.2837 |
| H07 |          56.51 |      51.25 |      62.07 |               115.57 |       108.67 |       122.44 | 0.489 |          83.84 |      0.4383 |
| H08 |          69.53 |      63.07 |      75.91 |               155.52 |       147.01 |       164.23 | 0.447 |          92.90 |      0.5393 |
| H09 |          91.39 |      83.65 |      99.08 |               195.70 |       185.62 |       205.97 | 0.467 |         116.42 |      0.7089 |
| H10 |         108.65 |     100.25 |     117.00 |               217.83 |       207.51 |       228.73 | 0.499 |         152.02 |      0.8427 |
| H11 |         127.16 |     118.47 |     136.28 |               236.79 |       226.14 |       247.93 | 0.537 |         158.71 |      0.9863 |
| H12 |         123.82 |     115.12 |     132.89 |               253.14 |       242.23 |       264.41 | 0.489 |         157.60 |      0.9604 |
| H13 |         106.04 |      98.73 |     113.84 |               232.33 |       221.88 |       243.05 | 0.456 |         136.94 |      0.8225 |
| H14 |         101.73 |      94.63 |     109.23 |               211.05 |       201.72 |       220.87 | 0.482 |         130.22 |      0.7891 |
| H15 |          92.43 |      84.73 |     100.23 |               188.20 |       179.22 |       198.26 | 0.491 |         123.78 |      0.7169 |
| H16 |          68.12 |      62.10 |      73.98 |               147.79 |       140.21 |       156.23 | 0.461 |          90.02 |      0.5284 |
| H17 |          37.52 |      33.99 |      40.96 |                85.06 |        80.45 |        89.78 | 0.441 |          55.91 |      0.2910 |
| H18 |          23.30 |      21.22 |      25.35 |                50.94 |        48.14 |        53.70 | 0.457 |          39.58 |      0.1807 |
| H19 |          14.66 |      13.17 |      16.15 |                34.49 |        32.42 |        36.66 | 0.425 |          22.21 |      0.1137 |
| H20 |           9.22 |       8.16 |      10.33 |                21.31 |        19.84 |        22.78 | 0.433 |          12.00 |      0.0715 |
| H21 |           4.92 |       4.30 |       5.55 |                12.70 |        11.78 |        13.68 | 0.387 |           6.52 |      0.0381 |
| H22 |           2.98 |       2.43 |       3.59 |                 7.52 |         6.84 |         8.33 | 0.397 |           1.77 |      0.0231 |
| H23 |           1.47 |       1.24 |       1.71 |                 3.72 |         3.39 |         4.09 | 0.394 |           0.92 |      0.0114 |
| H24 |           1.03 |       0.86 |       1.21 |                 2.55 |         2.29 |         2.83 | 0.404 |           0.27 |      0.0080 |

---

## 7. Neighbour vs Random Null Comparison

### Null Tests Applied

| Null | Description | N Pairs |
|------|-------------|---------|
| NULL 1 | Random origin pairing | 1000 |
| NULL 2 | Month-matched random pairing | 1000 |
| NULL 3 | Season-matched random pairing | 1000 |
| NULL 4 | Solar-regime-matched random pairing | 1000 |

### Divergence at Key Horizons (k=5 NN)

| Horizon | NN k=5 (W/m²) | Random NULL (W/m²) | Month-matched (W/m²) | Ratio NN/Random |
|---------|---------------|--------------------|-----------------------|----------------|
| H01 |          1.62 |               3.78 |                  2.64 |           0.428 |
| H03 |          7.37 |              13.81 |                  7.88 |           0.533 |
| H06 |         36.57 |              82.79 |                 43.64 |           0.442 |
| H09 |         91.39 |             195.70 |                103.42 |           0.467 |
| H10 |        108.65 |             217.83 |                118.11 |           0.499 |
| H11 |        127.16 |             236.79 |                127.33 |           0.537 |
| H12 |        123.82 |             253.14 |                133.67 |           0.489 |
| H13 |        106.04 |             232.33 |                116.98 |           0.456 |
| H15 |         92.43 |             188.20 |                102.02 |           0.491 |
| H18 |         23.30 |              50.94 |                 24.22 |           0.457 |
| H24 |          1.03 |               2.55 |                  1.42 |           0.404 |

---

## 8. High-Solar Comparison

Origins classified by clearsky_ghi at t0:  
- **All origins**: all 173 EVEN origins  
- **High-solar origins**: top quartile of clearsky_ghi at t0  

| Regime | N Origins | N NN Pairs (k=5) | Mean Traj RMSE (W/m²) |
|--------|-----------|------------------|----------------------|
| all_origins | 173 | 865 | 75.10 |
| daytime_origins | 158 | 790 | 81.99 |
| high_solar_origins | 40 | 200 | 145.68 |

---

## 9. State-Aliasing Evidence

### Conditional Spread (Neighbour IQR per Horizon, k=5)

The conditional IQR measures the spread of future SW_IN outcomes among
the 5 most similar origins. High IQR = high state aliasing at that horizon.

| Horizon | Mean Cond IQR (W/m²) | Fraction of POLARIS Normalizer |
|---------|----------------------|-------------------------------|
| H01 |                 1.62 |                         0.0126 |
| H02 |                 3.54 |                         0.0275 |
| H03 |                 7.20 |                         0.0559 |
| H04 |                12.62 |                         0.0978 |
| H05 |                26.77 |                         0.2076 |
| H06 |                41.99 |                         0.3257 |
| H07 |                58.40 |                         0.4530 |
| H08 |                74.55 |                         0.5783 |
| H09 |                94.49 |                         0.7329 |
| H10 |               107.22 |                         0.8316 |
| H11 |               122.11 |                         0.9471 |
| H12 |               124.56 |                         0.9661 |
| H13 |               102.77 |                         0.7971 |
| H14 |               104.04 |                         0.8070 |
| H15 |                92.24 |                         0.7155 |
| H16 |                72.77 |                         0.5645 |
| H17 |                32.20 |                         0.2498 |
| H18 |                24.31 |                         0.1886 |
| H19 |                13.72 |                         0.1064 |
| H20 |                 8.35 |                         0.0648 |
| H21 |                 4.60 |                         0.0357 |
| H22 |                 1.99 |                         0.0154 |
| H23 |                 1.27 |                         0.0099 |
| H24 |                 0.97 |                         0.0076 |

---

## 10. Relationship to Control Forecast Error

| Metric | Value |
|--------|-------|
| N origins (daytime MAE available) | 157 |
| Pearson r (NN divergence vs forecast MAE) | 0.6606 |
| Pearson p-value | 0.0000 |
| Spearman ρ (NN divergence vs forecast MAE) | 0.7496 |
| Spearman p-value | 0.0000 |
| Mean origin NN divergence (W/m²) | 46.92 |

*Correlation is reported. No causal claim is made.*

---

## 11. Bootstrap Confidence Intervals

95% bootstrap CIs included in H1–H24 divergence table (Section 6).  
Method: pairs bootstrap over origin pairs (2000 iterations).  
Seed: 12345

---

## 12. Limitations

1. **173 EVEN origins**: The sample is small. Bootstrap CIs reflect this.
2. **High-dimensional state**: 32 features. Nearest-neighbour matching in high
   dimensions suffers from the curse of dimensionality. Neighbour distances
   may not reflect true meteorological similarity.
3. **State construction**: Causal state uses H1 row only. Features that
   change within a 24h window are approximated by their t0 value.
4. **Model-derived features excluded**: Excluding pred_* features may
   underrepresent the true causal state available to POLARIS at inference time.
5. **No trajectory correlation metric**: Correlation would be misleading for
   trajectories with large night-time zero segments. Absolute differences used.
6. **Null tests use random sampling**: Not all possible random pairs are tested.
7. **Daytime classification in control predictions**: Uses existing is_daytime flag.

---

## 13. Single Final Classification

**C — WEAK / INCONCLUSIVE STATE-ALIASING**

Peak NN/random ratio: 0.537  
Mean NN/random ratio: 0.460  

---

## 14. Information-Limited Hypothesis Assessment

UNCHANGED — Evidence is weak or below null thresholds. Information limitation remains possible but unconfirmed by this diagnostic.

---

## Final Governance Declaration

```
ODD_EVALUATED         = False
ODD_ROWS_ACCESSED     = False
TRAINING_PERFORMED    = False
NEW_DATA_FETCHED      = False
NEW_FEATURES_CREATED  = False
ROUTES_MODIFIED       = False
```