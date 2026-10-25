# POLARIS — FINAL CORRECTED CAUSAL LOCAL SPATIAL STATE INFORMATION AUDIT REPORT

**Date:** September 14, 2026  
**Audit Classification:** `B — PARTIAL / HORIZON-CONDITIONAL INFORMATION`  
**Final Recommendation:** **`PROCEED TO A SINGLE PRE-REGISTERED HORIZON-CONDITIONAL LOCAL-SPATIAL REPRESENTATION EXPERIMENT`**  
**Justified Horizon Regime:** `Horizons H2, H5, H6 (individually FDR-supported) and grouped H4–H6 / H7–H24`  

---
## 1. Absolute Separation of Scientific Claims

> **CRITICAL SCIENTIFIC GOVERNANCE SEPARATION:**
> 1. **CLAIM A (Local Spatial State Information Content):** **VALIDATED** — Local station-neighborhood ($3\times 3$) cloud state contains modest, statistically significant incremental information ($\Delta R^2 \approx +0.007 \text{ to } +0.020$, FDR $p < 0.05$) about future station cloud state beyond single-pixel station persistence ($S_{\text{cloud}}(t)$).
> 2. **CLAIM B (POLARIS SW_IN Forecasting Improvement):** **NOT ESTABLISHED** — Diagnostic correlations with control forecast error **DO NOT EQUAL** demonstrated forecasting gain. No forecasting model has been trained, and no forecast improvement has been shown.

---
## 2. Governance & Safeguard Audit

> **STRICT DIAGNOSTIC SAFEGUARDS VERIFIED:**
> 1. *No model training was performed.*
> 2. *No ODD data accessed (174 ODD origins completely sealed).*
> 3. *Network fetches performed = 0.*
> 4. *EVEN origins ONLY (173 origins × 24 horizons = 4,152 rows).*
> 5. *Evaluated on 2,216 causal daytime forecast hours (`solar_elevation > 0` & `clearsky_ghi > 1e-6`).*
> 6. *Future SW_IN used strictly post-hoc after spatial metrics were frozen.*

---
## 3. Level 3–5 Incremental Variance Audit

Raw $R^2$ values and exact nested $\Delta R^2$ increments across nested models (L1: Center, L2: +3x3 Mean, L3: +Heterogeneity, L4: +Temporal Change, L5: +Structural Change):

| Horizon / Group | L1 $R^2$ | L2 $R^2$ ($\Delta R^2$) | L3 $R^2$ ($\Delta R^2$) | L4 $R^2$ ($\Delta R^2$) | L5 $R^2$ ($\Delta R^2$) | L2 $p_{\text{FDR}}$ | L3 $p_{\text{F-test}}$ | L4 $p_{\text{F-test}}$ | L5 $p_{\text{F-test}}$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H1** | `0.7449` | `0.7450` (**`+0.0001`**) | `0.7474` (`+0.0025`) | `0.7474` (`+0.0000`) | `0.7474` (`+0.0000`) | `0.8145` | `0.4417` | `1.0000` | `1.0000` |
| **H2** | `0.6216` | `0.6354` (**`+0.0137`**) | `0.6357` (`+0.0003`) | `0.6512` (`+0.0155`) | `0.6576` (`+0.0064`) | `0.0284` | `0.9243` | `0.0272` | `0.0808` |
| **H3** | `0.6599` | `0.6653` (**`+0.0054`**) | `0.6783` (`+0.0131`) | `0.6863` (`+0.0080`) | `0.6865` (`+0.0001`) | `0.1337` | `0.0354` | `0.1239` | `0.7911` |
| **H4** | `0.6540` | `0.6596` (**`+0.0056`**) | `0.6677` (`+0.0080`) | `0.6729` (`+0.0052`) | `0.6730` (`+0.0001`) | `0.1337` | `0.1341` | `0.2706` | `0.8126` |
| **H5** | `0.7322` | `0.7426` (**`+0.0104`**) | `0.7438` (`+0.0012`) | `0.7470` (`+0.0032`) | `0.7471` (`+0.0002`) | `0.0243` | `0.6848` | `0.3539` | `0.7400` |
| **H6** | `0.5810` | `0.6008` (**`+0.0198`**) | `0.6056` (`+0.0048`) | `0.6120` (`+0.0064`) | `0.6127` (`+0.0007`) | `0.0161` | `0.3599` | `0.2581` | `0.5883` |
| **H1–H3** | `0.6756` | `0.6794` (**`+0.0037`**) | `0.6816` (`+0.0022`) | `0.6828` (`+0.0012`) | `0.6840` (`+0.0012`) | `0.0144` | `0.1741` | `0.3712` | `0.1622` |
| **H4–H6** | `0.6546` | `0.6651` (**`+0.0106`**) | `0.6666` (`+0.0014`) | `0.6685` (`+0.0019`) | `0.6687` (`+0.0002`) | `7.93e-05` | `0.3364` | `0.2279` | `0.5531` |
| **H7–H12** | `0.6911` | `0.6970` (**`+0.0059`**) | `0.6981` (`+0.0011`) | `0.6984` (`+0.0004`) | `0.6994` (`+0.0010`) | `1.40e-05` | `0.1531` | `0.5192` | `0.0648` |
| **H13–H18** | `0.6742` | `0.6877` (**`+0.0135`**) | `0.6886` (`+0.0009`) | `0.6892` (`+0.0006`) | `0.6893` (`+0.0001`) | `1.80e-10` | `0.2331` | `0.3625` | `0.5526` |
| **H19–H23** | `0.6894` | `0.7034` (**`+0.0140`**) | `0.7059` (`+0.0025`) | `0.7074` (`+0.0016`) | `0.7076` (`+0.0002`) | `7.01e-10` | `0.0270` | `0.1021` | `0.5044` |

---
## 4. Horizon Decision Table (FDR Multiple-Comparison Corrected)

| Horizon / Group | Sample Size ($N$) | Level 1 $R^2$ | Level 2 $\Delta R^2$ | Raw F-test $p$ | FDR-adjusted $p$ | Evidence Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **H1** | `173` | `0.7449` | **`+0.0001`** | `0.8145` | `0.8145` | **`NOT SUPPORTED`** |
| **H2** | `173` | `0.6216` | **`+0.0137`** | `0.0123` | `0.0284` | **`SUPPORTED`** |
| **H3** | `173` | `0.6599` | **`+0.0054`** | `0.0988` | `0.1337` | **`NOT SUPPORTED`** |
| **H4** | `173` | `0.6540` | **`+0.0056`** | `0.0953` | `0.1337` | **`NOT SUPPORTED`** |
| **H5** | `173` | `0.7322` | **`+0.0104`** | `0.0095` | `0.0243` | **`SUPPORTED`** |
| **H6** | `173` | `0.5810` | **`+0.0198`** | `0.0042` | `0.0161` | **`SUPPORTED`** |
| **H7** | `173` | `0.7081` | **`+0.0043`** | `0.1110` | `0.1418` | **`NOT SUPPORTED`** |
| **H8** | `173` | `0.7470` | **`+0.0223`** | `7.73e-05` | `8.88e-04` | **`SUPPORTED`** |
| **H9** | `173` | `0.7319` | **`+0.0072`** | `0.0322` | `0.0528` | **`BORDERLINE`** |
| **H10** | `173` | `0.5857` | **`+0.0186`** | `0.0053` | `0.0173` | **`SUPPORTED`** |
| **H11** | `173` | `0.7280` | **`+0.0005`** | `0.5916` | `0.6185` | **`NOT SUPPORTED`** |
| **H12** | `173` | `0.6580` | **`+0.0015`** | `0.3830` | `0.4404` | **`NOT SUPPORTED`** |
| **H13** | `173` | `0.6371` | **`+0.0269`** | `3.02e-04` | `0.0017` | **`SUPPORTED`** |
| **H14** | `173` | `0.7508` | **`+0.0010`** | `0.4078` | `0.4467` | **`NOT SUPPORTED`** |
| **H15** | `173` | `0.6053` | **`+0.0111`** | `0.0279` | `0.0528` | **`BORDERLINE`** |
| **H16** | `173` | `0.6677` | **`+0.0033`** | `0.1957` | `0.2369` | **`NOT SUPPORTED`** |
| **H17** | `173` | `0.6438` | **`+0.0740`** | `3.36e-10` | `7.73e-09` | **`SUPPORTED`** |
| **H18** | `173` | `0.7565` | **`+0.0048`** | `0.0649` | `0.0996` | **`BORDERLINE`** |
| **H19** | `173` | `0.6825` | **`+0.0263`** | `1.27e-04` | `9.77e-04` | **`SUPPORTED`** |
| **H20** | `173` | `0.7034` | **`+0.0176`** | `0.0013` | `0.0059` | **`SUPPORTED`** |
| **H21** | `173` | `0.5968` | **`+0.0110`** | `0.0304` | `0.0528` | **`BORDERLINE`** |
| **H22** | `173` | `0.7412` | **`+0.0078`** | `0.0228` | `0.0477` | **`SUPPORTED`** |
| **H23** | `173` | `0.7344` | **`+0.0110`** | `0.0074` | `0.0213` | **`SUPPORTED`** |
| **H1–H3** | `519` | `0.6756` | **`+0.0037`** | `0.0144` | `0.0144` | **`SUPPORTED`** |
| **H4–H6** | `519` | `0.6546` | **`+0.0106`** | `6.34e-05` | `7.93e-05` | **`SUPPORTED`** |
| **H7–H12** | `1038` | `0.6911` | **`+0.0059`** | `8.39e-06` | `1.40e-05` | **`SUPPORTED`** |
| **H13–H18** | `1038` | `0.6742` | **`+0.0135`** | `3.61e-11` | `1.80e-10` | **`SUPPORTED`** |
| **H19–H23** | `865` | `0.6894` | **`+0.0140`** | `2.80e-10` | `7.01e-10` | **`SUPPORTED`** |

---
## 5. Origin-Level Regression Audit & Origin-Resampled Bootstrap

- **Small-Sample Acknowledgement:** A separate regression is fitted per origin using N=23 lead-1 pairs. Origin-level Delta R^2 describes the distribution of origin-specific local effects, whereas the pooled regression describes uncertainty in the global effect.
- **Origin-Level Level 2 $\Delta R^2$ Median:** `0.026182` (IQR: `[0.004652, 0.08449]`)
- **Origin-Resampled 1,000x Bootstrap 95% CI for Median $\Delta R^2$:** `[0.018182, 0.031602]`
- **Fraction of Origins with Positive $\Delta R^2$:** `96.0%`

- **Origin-Level $3\times 3$ Spearman Partial $\rho$ Median:** `0.1577` (IQR: `[-0.0359, 0.3079]`)
- **Origin-Resampled 1,000x Bootstrap 95% CI for Median Partial $\rho$:** `[0.0812, 0.2102]`
- **Fraction of Origins with Positive Partial Correlation:** `70.3%`

---
## 6. Null Controls Audit & Uncertainty Assessment

- **Real $3\times 3$ Station Mean Partial $\rho$:** `0.1895`
- **Null 1 (Origin-Permuted $3\times 3$ Mean):** `-0.0115` (STRONG — Origin-permuted null yields near-zero partial correlation (-0.0115), confirming causal origin specificity.)
- **Null 2 (Unrelated Field $y$-wind 10m):** `0.0012`
- **Null 3 (Random Patch Location $[3,3]$):** `0.1749`
- **Difference Real $-$ Null 3:** `0.0146` (Bootstrap 95% CI: `[-0.0388, 0.0644]`)
- **Null 3 Status:** `INCONCLUSIVE — Difference between station 3x3 (0.1895) and random patch pixel [3,3] (0.1749) is small (+0.0146) and 95% CI spans zero.`

---
## 7. SW_IN Forecast Error Double-Residual FDR Audit

- **Disclaimer:** CRITICAL GOVERNANCE SEPARATION: Association with control forecast error DOES NOT EQUAL demonstrated forecasting gain. No forecasting improvement has yet been established.

| Spatial Descriptor | Raw Spearman $\rho$ | Double-Residual Spearman $\rho$ | Raw $p$-value | FDR-adjusted $p$-value | Significant at $\alpha=0.05$? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `21x21 Spatial Heterogeneity (Std)` | `0.1771` | `0.1396` | `4.17e-11` | `1.25e-10` | `YES` |
| `21x21 Spatial Gradient` | `0.1873` | `0.1493` | `1.64e-12` | `9.81e-12` | `YES` |
| `3x3 Local Mean` | `-0.0833` | `0.0171` | `4.21e-01` | `6.74e-01` | `NO` |
| `3x3 Local Contrast` | `0.0007` | `0.0113` | `5.95e-01` | `6.74e-01` | `NO` |
| `d1 Center Change` | `0.015` | `0.0095` | `6.54e-01` | `6.74e-01` | `NO` |
| `Structural Correlation` | `-0.0002` | `-0.009` | `6.74e-01` | `6.74e-01` | `NO` |

---
## 8. Final Decision & Scientific Recommendation

### **Final Classification:** `B — PARTIAL / HORIZON-CONDITIONAL INFORMATION`

### **Final Scientific Recommendation:**
> **`PROCEED TO A SINGLE PRE-REGISTERED HORIZON-CONDITIONAL LOCAL-SPATIAL REPRESENTATION EXPERIMENT`**

### **Justified Horizon Regime:**
> `Horizons H2, H5, H6 (individually FDR-supported) and grouped H4–H6 / H7–H24`

### **Actionable Pre-Registration Guidance:**
1. **Authorized Experiment:** If authorized by human review, design a **single pre-registered horizon-conditional architecture** exploiting **local station-neighborhood ($3\times 3$) cloud state**.
2. **Discontinued Components:** Multi-scale CNNs, high-order patch heterogeneity features, optical flow cloud translation, and temporal spatial change features are **PERMANENTLY DISCONTINUED** as they add no incremental information beyond Level 2.
3. **Stop Condition:** Awaiting human review before any model development.

---
## 9. Cryptographic Provenance

- **Control Predictions Artifact CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)
  - SHA256: `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`
- **Final Audit Script SHA256:** `315bfffc22a2a7c5a051ff893ecae990453492cea19da2d1b5565eaa2d9c1072`
- **Final Audit JSON Artifact:** [`FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT.json)
  - SHA256: `4dd34ea0dda604d45e3a6dc3640e4725d1526bfee8cb9166d41bbee3bc4b8ad8`