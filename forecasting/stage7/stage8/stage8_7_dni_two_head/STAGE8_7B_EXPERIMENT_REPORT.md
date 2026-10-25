# POLARIS STAGE 8.7B — CAUSAL MEPS DNI-ANCHORED DIRECT/DIFFUSE TWO-HEAD ARCHITECTURE EXPERIMENT REPORT

## 1. Executive Summary

Stage 8.7B evaluated the **Causal MEPS DNI-Anchored Direct/Diffuse Two-Head Residual Target Architecture** against the frozen **Stage 8.1 37-Feature Champion Control** using the strict 5-Fold Forward-Chaining EVEN Cross-Validation protocol across 174 development forecast origins.

The candidate architecture failed all four performance gates (G1, G2, G3, G4) on EVEN CV:
- **Aggregate EVEN CV MAE:** **49.445841 W/m²** vs Control **37.620054 W/m²** (Delta MAE: **+11.825787 W/m²**, severe degradation).
- **Folds Improved:** **0 / 5 folds improved** (100% fold degradation).
- **Worst Fold Degradation:** **+28.022026 W/m²** (Fold 1).
- **nMAE & RMSE:** Candidate nMAE **46.83%** (vs Control 37.97%), Candidate RMSE **81.33 W/m²** (vs Control 60.16 W/m²).

**FINAL STAGE 8.7B GATE DECISION:** **REJECTED**

Per strict governance protocols, the **ODD Firewall was fully enforced**: zero ODD target reads, zero ODD predictions generated, zero ODD metrics computed, and zero ODD tuning performed. The official POLARIS champion remains **Stage 8.1** (ODD MAE: **36.188657 W/m²**, nMAE: **28.0688%**). `POLARIS_MASTER_HANDOFF.md` was left completely untouched.

---

## 2. Frozen Physical Proxy & Verification Audit Summary

Prior to model training, Stage 8.7A completed independent verification and prospectively frozen the exact physical direct solar proxy:

$$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\gamma_{s, h})) \times (1 - \text{terrain\_solar\_obstruction\_flag}_h)$$

- **Check 1 — Terrain Flag Integrity:** **PASSED**. Proven that `terrain_solar_obstruction_flag` is derived from 360° azimuth-resolved Copernicus 30m DEM horizon ray-marching ($\gamma_{s, h} \le \theta_{\text{horizon}}(\phi_{s, h})$), 100% deterministic and leak-free.
- **Check 2 — Solar-Elevation Timestamp Convention:** **PASSED**. Confirmed that `solar_elevation` in the frozen benchmark is evaluated at top-of-hour CET (aligned with MEPS hourly mean DNI).
- **Proxy Freeze Hash:** `a7f3e891c94b20d3671f845d098e21a44e5f7b88`.
- **Pre-execution Guarantee:** The exact proxy was frozen BEFORE inspecting any Stage 8.7B experimental model outputs.

---

## 3. Experimental Protocol & Feature Locks

To ensure strict comparability with Stage 8.1:
- **Feature Manifest:** 37 frozen Stage 8.1 features (0 features added, 0 removed).
- **Model Hyperparameters:** `loss="absolute_error"`, `max_depth=4`, `min_samples_leaf=30`, `l2_regularization=10.0`, `random_state=42`.
- **Target Decomposition:**
  - **Head 1 (Direct Head):** $\text{Target}_{\text{Direct}} = \text{DirectProxy}$
  - **Head 2 (Diffuse Head):** $\text{Target}_{\text{Diffuse}} = \text{actual\_SW\_IN} - \text{DirectProxy}$
  - **Recombination:** $\widehat{\text{SW\_IN}} = \max(0, \hat{y}_{\text{Direct}} + \hat{y}_{\text{Diffuse}})$
- **Strict Leakage Rule:** `actual_SW_IN` was accessed ONLY to compute `DiffuseResidual` on training origins. Validation and test sets never accessed `actual_SW_IN` before predictions were emitted.

---

## 4. 5-Fold Forward-Chaining EVEN CV Results

### Fold-by-Fold Metric Breakdown

| Fold | Val Origins | Daytime Rows | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | 29 | 696 | 49.311419 | 77.333445 | +28.022026 | DEGRADED |
| **F2** | 29 | 696 | 70.568800 | 79.536802 | +8.968001 | DEGRADED |
| **F3** | 29 | 696 | 40.345573 | 59.864250 | +19.518677 | DEGRADED |
| **F4** | 29 | 696 | 25.770418 | 28.184598 | +2.414180 | DEGRADED |
| **F5** | 29 | 696 | 2.104058 | 2.310108 | +0.206050 | DEGRADED |
| **Aggregate (Mean)** | **145** | **3,480** | **37.620054** | **49.445841** | **+11.825787** | **DEGRADED** |

### Aggregate Performance Comparison

| Metric | Control (Stage 8.1) | Candidate (Stage 8.7B Two-Head) | Delta (Candidate - Control) | Acceptance Threshold | Result |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EVEN CV MAE** | **37.620054 W/m²** | **49.445841 W/m²** | **+11.825787 W/m²** | $\le -0.50 \text{ W/m}^2$ | **FAIL (G1)** |
| **Folds Improved** | -- | **0 / 5** | -- | $\ge 4 / 5$ | **FAIL (G2)** |
| **Max Degradation** | -- | **+28.022026 W/m²** | -- | $\le +0.50 \text{ W/m}^2$ | **FAIL (G3)** |
| **nMAE (%)** | **37.9745%** | **46.8266%** | **+8.8521 pp** | $\le 37.9745\%$ | **FAIL (G4)** |
| **RMSE (W/m²)** | **60.160645** | **81.330841** | **+21.170196** | $\le 60.160645$ | **FAIL (G4)** |
| **Bias (W/m²)** | **+4.218739** | **+8.741205** | **+4.522466** | -- | Informational |

---

## 5. Strict Acceptance Gates Audit

```
Gate Evaluation Summary:
--------------------------------------------------------------------------------
G1: Candidate MAE <= Control MAE - 0.50 W/m²   --> FAIL (Actual Delta: +11.825787 W/m²)
G2: At least 4/5 folds improve                 --> FAIL (0/5 folds improved)
G3: Worst fold degradation <= +0.50 W/m²       --> FAIL (Max degradation: +28.022026 W/m²)
G4: Candidate nMAE & RMSE <= Control           --> FAIL (nMAE: 46.83% vs 37.97%, RMSE: 81.33 vs 60.16)
G5: 100% Forecast-Hour Causality               --> PASS (100% causal)
G6: Exact Control Reproduction                 --> PASS (37.620054 W/m² exact match)
--------------------------------------------------------------------------------
FINAL STAGE 8.7B EVEN CV GATE DECISION:          REJECTED
```

---

## 6. ODD Firewall Status & Governance Audit

- **ODD Dataset Status:** **100% UNTOUCHED & UNREAD**.
- **ODD Target Reads:** `0`
- **ODD Predictions Generated:** `0`
- **ODD Metrics Computed:** `0`
- **Champion Protection:** Stage 8.1 Champion remains official champion ($36.188657 \text{ W/m}^2$ ODD MAE). `POLARIS_MASTER_HANDOFF.md` was not modified.

---

## 7. Scientific & Architectural Forensics

The severe performance degradation (**+11.83 W/m² EVEN CV MAE**) of the two-head direct/diffuse residual target architecture stems from three distinct physical and mathematical factors:

1. **Uncertainty Amplification in Disjoint Target Heads:**
   MEPS DNI forecasts carry significant spatial phase errors, cloud edge timing discrepancies, and atmospheric opacity uncertainty. When DNI is multiplied by $\sin(\gamma_s) \times (1 - \text{flag})$, these uncertainties are projected into `DirectProxy`. When two independent HistGradientBoosting regressors fit `DirectProxy` and `DiffuseResidual` separately, the errors of the two models accumulate additively upon recombination ($\widehat{\text{SW\_IN}} = \hat{y}_{\text{Direct}} + \hat{y}_{\text{Diffuse}}$).

2. **Non-Subadditivity of Absolute Error ($L_1$) Loss:**
   HistGradientBoosting optimizes $L_1$ loss (`loss="absolute_error"`). $L_1$ loss is non-linear and not subadditive:
   $$\mathbb{E}[|(X_{\text{dir}} + X_{\text{diff}}) - (\hat{X}_{\text{dir}} + \hat{X}_{\text{diff}})|] \not\le \mathbb{E}[|X_{\text{dir}} - \hat{X}_{\text{dir}}|] + \mathbb{E}[|X_{\text{diff}} - \hat{X}_{\text{diff}}|]$$
   Independently minimizing MAE on the direct head and diffuse head does **not** minimize the MAE of their sum.

3. **Superiority of Single End-to-End Residual Correction:**
   The Stage 8.1 champion fits a single tree ensemble directly on total surface GHI residual ($y - \hat{y}_{\text{Stage 4}}$). This enables the decision trees to directly learn non-linear interactions between cloud fraction, 700 hPa winds, boundary layer humidity, and clearsky radiation without imposing an artificial physical split that forces the trees to learn noisy intermediate targets.

---

## 8. Final Decision & Provenance Manifest

- **Stage 8.7B Decision:** **REJECTED**
- **Champion Maintained:** Stage 8.1 700 hPa Steering Wind Champion
- **Artifacts Recorded:**
  - `STAGE8_7A_PROXY_APPROVAL.md` / `.json`
  - `STAGE8_7B_GATE_DECISION.json`
  - `stage8_7b_fold_results.csv`
  - `stage8_7b_even_cv_summary.csv`
  - `stage8_7b_control_reproduction_audit.json`
  - `stage8_7b_causality_audit.json`
  - `stage8_7b_leakage_audit.json`
  - `stage8_7b_reproducibility_manifest.json`
