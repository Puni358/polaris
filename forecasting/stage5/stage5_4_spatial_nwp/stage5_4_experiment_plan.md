# POLARIS Stage 5.4 — Spatial NWP Feature Extraction & Evaluation Plan

## 1. Context & Scientific Objective

Stage 5.3 forensic analysis demonstrated that the frozen Stage 5.2 champion (Architecture A: GBDT Non-Linear Residual Corrector) achieved a daytime MAE reduction from 43.4508 W/m² to 39.0848 W/m² (+10.05% gain). However, the results indicate that the current 1D point-based NWP representation may limit the atmospheric information available to the forecasting model by providing only a single vertical cloud fraction estimate at Nuolja, omitting directional cloud motion vectors, spatial cloud cover gradients, and localized advection across the surrounding mountain terrain.

**Scientific Goal:** Test whether additional spatial atmospheric information causally available in the previous-day NWP forecast (`_previous_day1`) provides incremental predictive information beyond the frozen Stage 5.2 feature set.

---

## 2. Strict Experimental & Methodological Controls

1. **Frozen Benchmark Baseline:** Stage 5.2 Architecture A remains frozen as the active champion baseline:
   - **Stage 4 Baseline:** 43.4508 W/m² Daytime MAE (33.70% nMAE) on ODD test split.
   - **Stage 5.2 Baseline:** 39.0848 W/m² Daytime MAE (30.32% nMAE) on ODD test split.
2. **Untouched ODD Test Set Rule:** ODD test split (173 origins) remains 100% untouched during discovery, feature engineering, feature selection, and EVEN cross-validation.
3. **Causal Integrity:** All new NWP variables use `_previous_day1` information available before forecast origin $t_0 = \text{00:00 CET}$. Zero forward data leakage.
4. **Spatial Geometry Terminology:** Spatial NWP variables are referred to strictly as *"spatial NWP probes at approximately the native model-grid scale"* (~2.5 km offset).
5. **Model Architecture Control:** Exact Stage 5.2 Architecture A implementation (`HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_regularization=10.0, random_state=42)`).

---

## 3. Candidate Feature Definitions

### A. Wind Vector Components (E1)
- Source: `wind_direction_10m_previous_day1` and `wind_speed_10m_previous_day1`.
- Zonal Wind: $U_{10m} = -w_{\text{speed}} \cdot \sin(w_{\text{dir}} \cdot \pi / 180)$ (East-West wind)
- Meridional Wind: $V_{10m} = -w_{\text{speed}} \cdot \cos(w_{\text{dir}} \cdot \pi / 180)$ (North-South wind)

### B. Cardinal Spatial Cloud Probes (E2)
- Spatial Offsets: ~2.5 km at native model-grid scale ($\Delta\text{lat} = \pm 0.0225^\circ$, $\Delta\text{lon} = \pm 0.06^\circ$).
- Features: `cloud_frac_N`, `cloud_frac_S`, `cloud_frac_E`, `cloud_frac_W`.
- Spatial Gradients:
  - Zonal Cloud Gradient: $\Delta C_{\text{E-W}} = \text{cloud\_frac\_E} - \text{cloud\_frac\_W}$
  - Meridional Cloud Gradient: $\Delta C_{\text{N-S}} = \text{cloud\_frac\_N} - \text{cloud\_frac\_S}$

### C. Wind $\times$ Spatial Cloud / Advection Proxies (E3)
- Zonal Advection Proxy: $U_{10m} \cdot \Delta C_{\text{E-W}}$
- Meridional Advection Proxy: $V_{10m} \cdot \Delta C_{\text{N-S}}$
- Total Advection Proxy: $\text{advection\_proxy} = U_{10m} \cdot \Delta C_{\text{E-W}} + V_{10m} \cdot \Delta C_{\text{N-S}}$
- Upwind Cloud Cover: Directionally selected cloud fraction based on wind vector orientation.

---

## 4. Experiment Ladder (E0–E4)

- **E0 (Base Stage 5.2 Reproducibility):** 28 Stage 5.2 baseline features on EVEN 5-fold forward-chaining CV. Must match Stage 5.2 CV result.
- **E1 (Wind Vectors):** Stage 5.2 + $U_{10m}, V_{10m}$.
- **E2 (Spatial Cloud):** Stage 5.2 + Cardinal Cloud Probes & Spatial Gradients.
- **E3 (Wind $\times$ Spatial Advection):** Stage 5.2 + Spatial Cloud + Advection Proxies.
- **E4 (Combined Candidate):** Stage 5.2 + E1 + E2 + E3 (evaluated if supported by EVEN-CV).

---

## 5. Decision Gate & ODD Rules

- **EVEN-CV Decision Gate Criteria:**
  - **A — STRONG GO:** Meaningful, consistent EVEN-CV improvement beyond Stage 5.2 ($\ge 0.50\text{ W/m}^2$ MAE drop across folds).
  - **B — WEAK SIGNAL:** Slight improvement ($0.10\text{--}0.49\text{ W/m}^2$) but inconsistent across folds.
  - **C — NO IMPROVEMENT:** Spatial inputs do not improve frozen champion.
  - **D — DATA/CAUSALITY FAILURE:** Leakage or extraction failure.
- **ODD Evaluation Protocol:** ODD test split is evaluated ONLY if E0 succeeds, E1–E4 EVEN-CV completes, candidate model is frozen, and gate is selected.
