# POLARIS — Stage 8.17A Real AROME Postmortem Forensics Report (Corrected Version)

**Timestamp:** 2026-09-13T15:14:51Z  
**Authoritative Machine Artifact:** [`STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv)  
**Target Location:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Final Status:** `CLOSED — EVIDENCE SUPPORTS A SPECIFIC NEW RESEARCH ROUTE`

---

## 1. Corrected Executive Summary

This corrected postmortem documents the revalidated performance of **Stage 8.17A (AROME-Arctic Structural Disagreement)** on 100% real historical AROME-Arctic 2024 data.

### Verified Revalidation Metrics
- **Revalidated Real AROME ODD Daytime MAE:** **$36.426418\text{ W/m}^2$**
- **Control Baseline ODD Daytime MAE:** **$36.211027\text{ W/m}^2$**
- **Performance Delta (Cand - Ctrl):** **$+0.215391\text{ W/m}^2$** (Degradation on real data)
- **10,000 Bootstrap 95% CI:** $[-0.1127, +0.4749]\text{ W/m}^2$ (Spans zero, 11.8% improving)
- **Reproduction Verdict:** **`C. NOT REPRODUCED / DEGRADED ON REAL AROME DATA`**

---

## 2. Authoritative Feature Redundancies (Corrected Against Machine Artifact)

The following table presents the authoritative Spearman rank correlations extracted directly from [`STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv):

| Disagreement Feature | Existing Baseline Feature | Spearman $r$ (Machine CSV) | Pearson $r$ (Machine CSV) | Authoritative Interpretation |
| :--- | :--- | :---: | :---: | :--- |
| `wind_disagreement_700` | `u700` (MEPS 700 hPa U-wind) | **$+0.5694$** | $+0.6783$ | **Strong Positive Correlation:** Wind vector disagreement scales directly with 700 hPa wind speed. |
| `wind_disagreement_700` | `fc_cloud_cover` / `cloud_frac` | **$+0.3187$** | $+0.2959$ | Moderate correlation with cloud presence. |
| `wind_disagreement_700` | `ctx_std_6h` (Context GHI std) | **$-0.1905$** | $-0.2212$ | Slight negative correlation with context GHI variability. |
| `LWP_disagreement` | `lwp_latest` (MEPS LWP) | **$+0.8939$** | $+0.7212$ | **Extremely High Redundancy:** LWP disagreement scales almost linearly with baseline LWP. |
| `LWP_disagreement` | `lwp_x_cloud` | **$+0.8883$** | $+0.7106$ | Extremely high redundancy with cloud-weighted LWP. |
| `LWP_disagreement` | `cloud_frac` / `fc_cloud_cover` | **$+0.6053$** | $+0.2330$ | **Strong Redundancy:** Disagreement is heavily concentrated during cloudy hours. |
| `LWP_disagreement` | `fc_relative_humidity_2m` | **$+0.4703$** | $+0.2194$ | Moderate correlation with 2m humidity. |

---

## 3. Corrected Architectural & Scientific Notes

1. **Model Grid Architecture:**  
   Both AROME-Arctic and MEPS are **2.5 km HARMONIE-AROME family** model systems. Disagreement between them arises from domain configuration, boundary conditions, data assimilation (e.g. Arctic 3D-Var), ensemble/control setup, and initialization—not resolution superiority.
2. **Directional Sign Deficiency:**  
   `wind_disagreement_700` and `LWP_disagreement` have near-zero correlation with signed residuals ($r = +0.0482$ and $+0.0763$). Scalar magnitude disagreement indicates forecast difficulty but provides no directional sign ($\pm$) for point-forecast correction.
3. **Route Closure:**  
   Raw scalar wind and LWP disagreement magnitude features are **PERMANENTLY CLOSED**.
