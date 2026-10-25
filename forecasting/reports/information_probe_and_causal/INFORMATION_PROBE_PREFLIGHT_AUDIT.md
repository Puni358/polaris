# POLARIS — INFORMATION PROBE PREFLIGHT AUDIT

**Date (UTC):** 2026-09-16  
**Status:** PREFLIGHT AUDIT RECONCILED & GOVERNANCE FROZEN  
**Preregistration Target:** `newhope/POLARIS_INFORMATION_PROBE_PREREGISTRATION.md`  

---

## 1. Executive Summary & Preflight Findings

This preflight audit inspects the existing POLARIS codebase, Stage 8.1 artifacts, and `POLARIS_INFORMATION_PROBE_PREREGISTRATION.md` prior to target computation or model fitting.

### Governance & Technical Declarations

> [!WARNING]
> **1. T4 Reconstruction Blocker & Required Drop:**  
> Genuine matching-fold Stage 8.1 EVEN out-of-fold (OOF) predictions do not exist as a pre-existing artifact. Stage 8.1 official development in `run_stage8_1.py` utilized a 5-fold expanding-window / forward-chaining CV (leaving the first 29 EVEN origins unpredicted OOF), while the official champion evaluated on ODD was fit on all 174 EVEN origins simultaneously. Furthermore, the probe preregistration specifies a 5-fold `GroupKFold` protocol. Per Section 2 & 5 of the preregistration, **T4 IS DROPPED / UNAVAILABLE**. In-sample, approximate, or non-matching fold predictions are strictly prohibited.

> [!IMPORTANT]
> **2. Corrected Section 9 Decision Rule & Governance:**  
> - **Original formal hit criterion:** At least 2 of 4 targets individually satisfy $\Delta R^2 \ge 0.03$ AND bootstrap 95% CI excludes zero.  
> - **T4 status:** Unavailable/dropped because genuine matching-fold Stage 8.1 EVEN OOF predictions cannot be reconstructed.  
> - **T1, T2, and T3 status:** Active and will be computed and reported descriptively/inferentially.  
> - **Formal Hit Governance:** With T4 unavailable, the original 2-of-4 formal hit criterion **cannot be satisfied** using only T1–T3.  
> - **Prohibition:** A formal Section 9 hit MUST NOT be declared based on 2 of 3 targets. The decision rule MUST NOT be silently modified or weakened.  
> - **Amendment Rule:** Any future change to the formal decision rule would require an explicit methodological amendment made before inspecting target results.

---

## 2. Reconciled Audit Checklist (13 Items)

### 1. Current Preregistration Version/Status
- **Location:** `newhope/POLARIS_INFORMATION_PROBE_PREREGISTRATION.md`
- **Version:** v1.0 (FROZEN PRE-COMPUTATION)
- **Status:** Reconciled with corrected governance wording. Zero target values computed. Zero models fitted. Zero ODD access.

### 2. Exact P0 Definition (Deterministic Solar/Seasonal Baseline)
- Deterministic solar and astronomical state containing **22 features total** (zero measured cloud/weather observations):
  1. `solar_elevation` at $t_0$
  2. `solar_elevation` at H7, H8, H9, H10, H11, H12 (6 features)
  3. `solar_azimuth` at H7, H8, H9, H10, H11, H12 (6 features)
  4. `clearsky_ghi` at H7, H8, H9, H10, H11, H12 (6 features)
  5. `doy_sin`, `doy_cos` (Day of year, 2 features)
  6. `daylight_duration` for origin date (1 feature)

### 3. Exact P1 Definition (P0 + Frozen Stage8.1 Causal State)
- P1 = P0 + full **37-feature frozen Stage 8.1 causal state** at $t_0$.
- Reconciled Canonical Feature Registry (37 features):
  - Base 28 features: `horizon_hour`, `month`, `hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `cloud_frac`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, 14 context features (`ctx_std_3h` through `ctx_max_24h`).
  - Stage 6.6 features (3): `lwp_latest`, `iwp_latest`, `lwp_x_cloud`.
  - Stage 7.5 terrain features (4): `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted`.
  - Stage 8.1 wind features (2): `u700`, `v700`.
- Unrolled Origin Dimensionality: 147 feature columns (15 origin scalars + 22 horizon features $\times$ 6 hours). Zero feature selection or latent transformation.

### 4. P2 Status
- **UNSPECIFIED / PROHIBITED in v1.0**.
- P2 cannot be specified, built, or evaluated until P1 completes and demonstrates an information gap ($P1 > P0$).
- When introduced, P2 requires a formal written amendment naming exactly ONE candidate source, backed by a causal availability audit and no data leakage.

### 5. Exact Target Definitions & T4 Status
All targets are defined on clear-sky index $k_t(h) = \text{SW\_IN\_actual}(h) / \text{clearsky\_GHI}(h)$ across horizon hours H7–H12 (06:00–11:00 UTC), where $\text{clearsky\_GHI}(h) \ge 20\text{ W/m}^2$, clipped to $[0.0, 1.2]$.
- **T1 — Future Transmission Volatility:** $\text{std}(k_t(h))$ over defined $h \in [\text{H7}, \text{H12}]$, population standard deviation ($\text{ddof}=0$).
- **T2 — Maximum Transition Magnitude:** $\max |k_t(h+1) - k_t(h)|$ over consecutive defined hours in H7–H12.
- **T3 — Mean Transmission Level:** $\text{mean}(k_t(h))$ over defined $h \in [\text{H7}, \text{H12}]$.
- **T4 — Champion Difficulty:** DROPPED / UNAVAILABLE.

### 6. Exact Eligibility Rule
- Origin window: H7–H12 (06:00–11:00 UTC).
- An origin is eligible iff **at least 5 of the 6 hours** have defined $k_t$ ($\text{clearsky\_GHI} \ge 20\text{ W/m}^2$).
- **Power Floor:** If eligible EVEN $N < 60$, study results are strictly descriptive; Section 9 decision rules cannot be invoked.

### 7. Exact Probe Models
1. **Model A — Ridge Regression:** $\alpha = 1.0$, standardization fit inside training fold only. No hyperparameter tuning.
2. **Model B — GBDT:** `HistGradientBoostingRegressor(max_depth=3, n_estimators=200, learning_rate=0.05, min_samples_leaf=10, random_state=42)`. No tuning.
- Strictly no neural networks, latent embeddings, or feature selection.

### 8. Exact CV Rule
- 5-fold `GroupKFold` grouped by forecast origin over EVEN origins.
- Fold labels assigned strictly across all 174 EVEN origins prior to eligibility filtering to preserve canonical group structure.
- Saved in `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv`.

### 9. Exact Bootstrap Rule
- Paired origin-level bootstrap on per-origin squared-error differences: $d_i = (y_i - \hat{y}_{i, P0})^2 - (y_i - \hat{y}_{i, P1})^2$.
- 10,000 resamples.
- 95% percentile confidence interval ($2.5\%$ to $97.5\%$).

### 10. Exact Permutation Null
- 1,000 permutations.
- Shuffling target values across origins **strictly within calendar-month blocks**. Unblocked shuffles prohibited.

### 11. Exact Section 9 Decision Rule Wording (Strict Governance)
- **Original formal hit criterion:** At least 2 of 4 targets individually satisfy $\Delta R^2 \ge 0.03$ AND bootstrap 95% CI excludes zero.
- **T4 is unavailable/dropped** because genuine matching-fold Stage 8.1 EVEN OOF predictions cannot be reconstructed.
- **T1, T2, and T3 remain active** and may be computed and reported descriptively/inferentially.
- **With T4 unavailable, the original 2-of-4 formal hit criterion cannot be satisfied using only T1–T3.**
- **Do NOT declare a formal Section 9 hit based on 2 of 3 targets.**
- **Do NOT silently modify the decision rule.**
- Any future change to the formal decision rule would require an explicit methodological amendment made before inspecting target results.

### 12. Phase B Specification (Hedging Diagnostic)
- Evaluates Hypothesis M3 using $k = 5$ nearest causal-state neighbours in EVEN origins (inheriting distance metric & standardization from `POLARIS_CAUSAL_STATE_ALIASING_AUDIT`).
- Evaluates: B1 (PIT rank), B2 (pinball loss vs ensemble median), B3 (bimodality MAE conditional).

---

## 3. Artifact Freeze Summary

| Artifact Name | Path | Row Count | SHA-256 Hash |
| :--- | :--- | :---: | :--- |
| **Canonical Fold Assignment** | `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | 174 | `0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad` |
