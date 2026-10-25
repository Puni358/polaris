# STAGE 8.19 REVALIDATION FREEZE MANIFEST

**Date:** September 13, 2026  
**Scope:** Pre-ODD Model Architecture & Feature Matrix Freeze Contract  
**Status:** FROZEN CONTRACT BEFORE ODD ACCESS  

---

## 1. Frozen Model Architecture & Hyperparameters

Per Step 5 of the Stage 8.19 Clean Revalidation Protocol, the candidate model architecture and hyperparameters are strictly frozen as follows:

| Property | Value / Specification |
| :--- | :--- |
| **Model Class** | `sklearn.ensemble.HistGradientBoostingRegressor` |
| **Loss Function** | `'absolute_error'` (MAE loss) |
| **Max Depth** | `4` |
| **Min Samples Leaf** | `30` |
| **L2 Regularization** | `10.0` |
| **Random State** | `42` |
| **Early Stopping** | `False` |

---

## 2. Pre-Declared Candidate Feature Matrix (42 Features)

The 42-feature candidate matrix consists of the **Stage 8.17A 40-feature baseline** plus exactly 4 pre-declared real candidate features:

### A. Stage 8.17A Base Feature Inventory (40 Features)
- Standard POLARIS surface meteorological, clear-sky, persistence, horizon-resolved LWP/IWP, and steering wind features (37 features from Stage 8.1 + 3 Stage 8.17A structural features).

### B. Stage 8.19 Real Candidate Features (4 Features)
1. `wind_disagreement_700`: Real AROME-Arctic vs MEPS 700 hPa steering wind vector disagreement ($\text{m/s}$).
2. `LWP_disagreement`: Real AROME-Arctic vs MEPS liquid water path column disagreement ($\text{kg/m}^2$).
3. `abis_ztd_latest`: Real ABIS/SWEPOS GNSS Zenith Total Delay observation valid at $t \le t_0 - \text{margin}$ ($\text{m}$).
4. `abis_ztd_trend_3h`: 3-hour temporal trend in real ABIS GNSS ZTD observations ($\text{m/h}$).

---

## 3. Freeze & Governance Contract Rules

1. **Zero ODD Influence:**  
   NO information from the 173 held-out ODD origins has influenced hyperparameter selection, feature engineering, missing-value imputation, or model tuning.
2. **Real Data Requirement:**  
   This frozen model contract MUST ONLY execute on 100% real, hashed, causally valid feature inputs derived from raw input artifacts. Synthetic replacements are prohibited.
3. **Control Dependency Gate:**  
   Model execution on ODD is strictly CONDITIONAL upon Step 3 control baseline reproduction success.
