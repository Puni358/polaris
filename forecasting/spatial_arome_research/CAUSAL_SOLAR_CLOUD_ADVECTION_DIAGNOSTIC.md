# POLARIS — CAUSAL SOLAR-AWARE CLOUD-ADVECTION DIAGNOSTIC REPORT

**Date:** September 14, 2026  
**Audit Classification:** `C — NO ACTIONABLE SIGNAL`  
**Final Recommendation:** **`DO NOT PROCEED — SPATIAL INFORMATION NOT ACTIONABLE`**  

---
## 1. Governance & Data Integrity Lock

> **STRICT DIAGNOSTIC SAFEGUARDS VERIFIED:**
> 1. *No model training was performed.*
> 2. *No ODD data accessed (174 ODD origins completely sealed).*
> 3. *Network fetches performed = 0.*
> 4. *EVEN origins ONLY (173 origins × 24 horizons = 4,152 rows).*
> 5. *Evaluated strictly on 2,216 causal daytime forecast hours (`solar_elevation > 0` & `clearsky_ghi > 1e-6`).*
> 6. *Future SW_IN used strictly post-hoc as a diagnostic correlation outcome.*

---
## 2. Cloud-Field Motion Estimation (H_t → H_{t+1})

- **Total Horizon Steps Evaluated:** `4152`
- **Valid Motion Estimates:** `3005 / 4152` (`72.4%`)
- **Mean Apparent Cloud Speed:** `1.63` km/h

---
## 3. Wind Advection Comparison (10m vs 700hPa)

| Steering Level | Mean Wind Speed | Mean Angular Disagreement vs Cloud Motion | Superior Steering Level? |
| :--- | :---: | :---: | :---: |
| **10 m Surface Wind** | `16.4` km/h | `79.3`° | `NO` |
| **700 hPa Upper-Air Wind** | `40.67` km/h | `79.1`° | **`YES (Superior Steering Level)`** |

---
## 4. Station-Relative & Solar-Relative Geometry

- **Mean Upstream Cloud Fraction (700hPa Wind):** `0.6585`
- **Mean Downstream Cloud Fraction (700hPa Wind):** `0.6276`
- **Mean Sunward Cloud Fraction (Solar Azimuth):** `0.6473`
- **Mean Anti-Sunward Cloud Fraction:** `0.6383`
- **Upstream vs Downstream Asymmetry:** `0.0309`

---
## 5. Horizon-Stratified Correlation Analysis

| Horizon Group | Daytime Sample Size (N) | Upstream Cloud Spearman Rho | Upstream p-val | Sunward Cloud Spearman Rho | Sunward p-val |
| :---: | :---: | :---: | :---: | :---: | :---: |
| H1–H3 | `92` | `-0.3024` | `3.40e-03` | `-0.2606` | `1.21e-02` |
| H4–H6 | `201` | `-0.3440` | `5.73e-07` | `-0.3469` | `4.55e-07` |
| H7–H12 | `783` | `-0.1593` | `7.52e-06` | `-0.1698` | `1.78e-06` |
| H13–H18 | `810` | `-0.0535` | `1.28e-01` | `-0.0313` | `3.74e-01` |
| H19–H24 | `330` | `+0.0249` | `6.53e-01` | `+0.0203` | `7.13e-01` |

---
## 6. Error-Alignment & Null Test Correlations

| Physical Feature | Spearman Rho | p-value | Pearson r | Statistically Significant? |
| :--- | :---: | :---: | :---: | :---: |
| NULL CONTROL: Upstream Cloud (Randomized Vector) | **`-0.1077`** | `3.75e-07` | `-0.0219` | `YES (p<0.01)` |
| Upstream Cloud Fraction (Real 700hPa Wind) | **`-0.1075`** | `3.93e-07` | `-0.0210` | `YES (p<0.01)` |
| Downstream Cloud Fraction (Real 700hPa Wind) | **`-0.1059`** | `5.89e-07` | `-0.0233` | `YES (p<0.01)` |
| Sunward Cloud Fraction (Solar Azimuth) | **`-0.1033`** | `1.11e-06` | `-0.0114` | `YES (p<0.01)` |
| 700hPa Wind vs Cloud Motion Angular Disagreement | **`+0.0473`** | `2.60e-02` | `+0.0640` | `NO` |
| 700hPa Wind vs Cloud Speed Ratio | **`+0.0464`** | `2.90e-02` | `+0.0609` | `NO` |
| Upstream Liquid Water Path (LWP) | **`-0.0252`** | `2.36e-01` | `+0.0133` | `NO` |
| Upstream / Downstream Ratio | **`+0.0208`** | `3.27e-01` | `-0.0139` | `NO` |
| Sunward Liquid Water Path (LWP) | **`-0.0044`** | `8.35e-01` | `+0.0192` | `NO` |

### Null Control Test Outcome:
- **Real 700hPa Upstream Cloud Rho:** `-0.1075`
- **Randomized Null Upstream Cloud Rho:** `-0.1077`
- **Signal Exceeds Null:** **`False`**

---
## 7. Final Audit Classification & Recommendation

### **Classification Outcome: `C — NO ACTIONABLE SIGNAL`**

No robust, physically aligned relationship was found that outperforms random null controls.

### **Final Scientific Recommendation:**
> **`DO NOT PROCEED — SPATIAL INFORMATION NOT ACTIONABLE`**

---
## 8. Cryptographic Provenance

- **Control Predictions Artifact CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)
  - SHA256: `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`
- **Diagnostic Script SHA256:** `29e9e1d16a10486487a4c3f46ce3c78b59f11d5b960e514566b4f0c6c7098283`
- **Diagnostic JSON Artifact:** [`CAUSAL_SOLAR_CLOUD_ADVECTION_DIAGNOSTIC.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/CAUSAL_SOLAR_CLOUD_ADVECTION_DIAGNOSTIC.json)
  - SHA256: `458dc58ea450f118972afb354037473521902485711b630cae179580c44b9509`