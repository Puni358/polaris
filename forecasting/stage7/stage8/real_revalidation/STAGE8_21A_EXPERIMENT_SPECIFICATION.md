# POLARIS STAGE 8.21A — EXPERIMENT SPECIFICATION REPORT

## 1. Executive Summary & Experiment Status

- **Route Identifier:** STAGE 8.21A (3D Solar Slant-Path Hydrometeor Geometry)
- **Status:** **FROZEN EXPERIMENT SPECIFICATION — READY FOR IMPLEMENTATION**
- **Governance Audit Firewall Verification:**
  - `EXPERIMENT_RUN` = **FALSE**
  - `MODEL_TRAINING` = **FALSE**
  - `ODD_ACCESS` = **FALSE**
  - `ODD_PREDICTIONS` = **FALSE**
  - `ODD_METRICS` = **FALSE**
  - `CHAMPION_CHANGED` = **FALSE**
  - `MASTER_HANDOFF_CHANGED` = **FALSE**
  - `ROUTE_REGISTRY_CHANGED` = **FALSE**

---

## 2. Locked Experiment Scope & Parameters

| Parameter Dimension | Locked Specification | Empirical / Justification Evidence |
|---|---|---|
| **Spatial Extraction Window** | **$47 \times 47$ MEPS Grid Points** | $57.5\text{ km}$ cardinal radius, $81.32\text{ km}$ corner radius, $115.0\text{ km}$ physical span. |
| **Solar Elevation Domain** | **Solar Elevation $\ge 5.0^\circ$** | $\theta_z \le 85.0^\circ$. Predeclared geometric feature domain boundary. |
| **Predeclared Coverage Criterion** | **$\ge 99.0\%$ Spatial Coverage** | Pre-locked coverage requirement for relevant solar ray tuples. |
| **Empirically Verified Coverage** | **$99.30\%$** ($3,262 / 3,285$ rays) | $47 \times 47$ window satisfies the predeclared $\ge 99.0\%$ coverage criterion. |
| **Outside-Window Handling** | **Deterministic 1D Fallback** | For $23$ rays ($0.70\%$) outside window, feature falls back to 1D station column vertical value without altering benchmark denominator. |
| **Low-Sun & Night Domain** | **Causally Forced / Excluded** | $0^\circ < \text{elev} < 5^\circ$ outside feature domain; $\text{elev} \le 0^\circ$ forced to $0.0\text{ W/m}^2$. |

---

## 3. Incremental Experimental Architecture

Stage 8.21A is designed as a strict **incremental feature addition** to the **Stage 8.1 Reproducible Champion Baseline**:

- **Baseline Architecture:** HistGradientBoostingRegressor (37 baseline features)
- **Frozen ODD Control Metrics:**
  - MAE $= 36.188657\text{ W/m}^2$
  - nMAE $= 28.0688\%$
  - RMSE $= 64.219495\text{ W/m}^2$
  - Bias $= +1.439399\text{ W/m}^2$
- **Candidate Architecture:** Stage 8.1 (37 baseline features) $+$ 4 Stage 8.21A compact 3D slant-path features $= \mathbf{41\text{ candidate features}}$.

---

## 4. Predeclared Acceptance Gates (G1–G6)

1. **G1 (MAE Improvement):** Candidate ODD MAE must improve over frozen control ($36.188657\text{ W/m}^2$).
2. **G2 (Fold Consistency):** $\ge 4 / 5$ EVEN forward-chaining cross-validation folds must improve over control.
3. **G3 (Worst Fold Tolerance):** Worst fold degradation must remain within locked tolerance ($+0.50\text{ W/m}^2$).
4. **G4 (nMAE & RMSE Non-Degradation):** Candidate nMAE and RMSE must not degrade vs control.
5. **G5 (Causal Lineage):** $100\%$ causal availability ($t_{\text{init}} \le t_0$) with $0$ future leakage.
6. **G6 (Exact Control Reproduction):** Baseline Stage 8.1 control MAE ($36.188657\text{ W/m}^2$) reproduced exactly before candidate training.

---

## 5. Frozen EVEN/ODD Split Protocol

- **Training & CV Population (EVEN Origins):** 173 even-indexed origins. Used exclusively for feature preprocessing, hydrostatic height calculation, and model fitting across 5 forward-chaining folds.
- **Official Test Population (ODD Origins):** 174 odd-indexed origins. Kept strictly untouched and un-accessed until candidate model freeze.
