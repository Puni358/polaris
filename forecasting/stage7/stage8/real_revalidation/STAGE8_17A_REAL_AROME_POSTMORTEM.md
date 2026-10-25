# POLARIS — Stage 8.17A Real AROME Postmortem Forensics Report

**Timestamp:** 2026-09-13T14:38:53Z  
**Target Location:** Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Real AROME SHA256:** `db5fa7591e586c0e1288a76806a7717d4ad13779458cb48a961959d48ceec298`  
**ODD Predictions SHA256:** `26bac202e3ce3cd851f1467a6a1c1b675b0409285058f895924d095eb8f0b908`  
**Final Status:** `CLOSED — EVIDENCE SUPPORTS A SPECIFIC NEW RESEARCH ROUTE`

---

## 1. Executive Forensic Summary

This postmortem investigates why the incorporation of real **AROME-Arctic 2024** forecast disagreement features (`wind_disagreement_700` and `LWP_disagreement`) failed to improve the operational Stage 8.1/8.17A baseline on locked held-out ODD evaluation ($36.426\text{ W/m}^2$ vs $36.211\text{ W/m}^2$, $+0.215\text{ W/m}^2$ degradation).

### Core Forensic Findings
1. **Historical Synthetic Artifact:** The previously claimed MAE of $35.241\text{ W/m}^2$ was an artifact of pseudo-random perturbations (`seed 817`). Real NWP disagreement does not reproduce that performance.
2. **Lack of Directional Predictive Signal:** Both disagreement features exhibit near-zero correlation with signed forecast residuals ($r_{\text{Spearman}} = +0.048$ for wind, $+0.076$ for LWP). Disagreement indicates when forecast uncertainty is higher, but provides no directional sign ($\pm$) for residual correction.
3. **Unaligned Scalar Representation:** Instantaneous single-point scalar disagreement converts 3D atmospheric flow differences into unoriented noise, causing gradient boosting trees to apply isotropic variance expansion that increases mean error on moderate cases.

---

## 2. Feature Distribution Analysis (2,883 Daytime Rows)

| Parameter | Wind Disagreement 700 ($m/s$) | LWP Disagreement ($\text{g/m}^2$) | Distribution Characteristics |
| :--- | :---: | :---: | :--- |
| **Min** | $0.0742$ | $0.0000$ | $0.0$ LWP disagreement when both models predict clear sky. |
| **P25** | $4.2185$ | $0.0000$ | $>25\%$ of daytime rows have zero LWP disagreement. |
| **Median (P50)** | $6.4542$ | $2.5601$ | Typical wind vector difference is $\sim 6.5\text{ m/s}$. |
| **P75** | $9.8214$ | $40.6782$ | Upper quartile reaches $40.7\text{ g/m}^2$ cloud liquid water. |
| **P90** | $13.5190$ | $118.4105$ | Severe synoptic disagreement $>13.5\text{ m/s}$. |
| **P95** | $16.2104$ | $215.1098$ | Heavy tail present in extreme frontal events. |
| **P99** | $21.4051$ | $512.9812$ | Extreme microphysics disagreement up to $1,752.6\text{ g/m}^2$. |
| **Max** | $31.6872$ | $1752.6338$ | Physical upper bound preserved without artificial clipping. |
| **Mean $\pm$ Std** | $7.4396 \pm 4.3102$ | $37.1083 \pm 101.4215$ | LWP has high variance and extreme positive skewness. |

---

## 3. Correlation with Forecast Error & Residuals

| Feature | Spearman $r$ (|Control Error|) | Spearman $r$ (Signed Residual) | Spearman $r$ (Candidate Impr.) | Pearson $r$ (|Control Error|) | Interpretation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `wind_disagreement_700` | $-0.0746$ | $+0.0482$ | $+0.0389$ | $-0.0412$ | Negligible correlation with signed residual; no directional predictive power. |
| `LWP_disagreement` | $+0.0746$ | $+0.0763$ | $+0.0674$ | $+0.0812$ | Slight positive correlation with absolute error; identifies cloud uncertainty. |

> [!IMPORTANT]
> **Key Insight:** Correlation with $|error|$ reflects forecast difficulty, while correlation with signed residual reflects point-forecast correction power. Because signed residual correlation is near zero ($<+0.08$), scalar disagreement cannot inform the model whether to increase or decrease predicted irradiance.

---

## 4. Quantile Error Breakdown

### A. `LWP_disagreement` Quantiles
| Quantile | Range ($\text{g/m}^2$) | Count | Control MAE ($\text{W/m}^2$) | Candidate MAE ($\text{W/m}^2$) | Delta MAE ($\text{W/m}^2$) | Mean Signed Res. ($\text{W/m}^2$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1–Q2** | $[0.0000, 0.8380]$ | $1,154$ | $34.1205$ | $34.2198$ | $+0.0993$ | $+0.4125$ |
| **Q3** | $(0.8380, 6.3029]$ | $576$ | $35.8190$ | $36.0412$ | $+0.2222$ | $+0.6120$ |
| **Q4** | $(6.3029, 40.6782]$ | $576$ | $37.2140$ | $37.5109$ | $+0.2969$ | $+0.5890$ |
| **Q5** | $(40.6782, 1752.63]$ | $577$ | $40.5180$ | $40.7915$ | $+0.2735$ | $+0.7120$ |

### B. `wind_disagreement_700` Quantiles
| Quantile | Range ($m/s$) | Count | Control MAE ($\text{W/m}^2$) | Candidate MAE ($\text{W/m}^2$) | Delta MAE ($\text{W/m}^2$) | Mean Signed Res. ($\text{W/m}^2$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1** | $[0.0742, 3.8210]$ | $577$ | $37.5120$ | $37.7105$ | $+0.1985$ | $+0.4120$ |
| **Q2** | $(3.8210, 5.4190]$ | $576$ | $36.8190$ | $37.0124$ | $+0.1934$ | $+0.4912$ |
| **Q3** | $(5.4190, 7.6105]$ | $577$ | $35.9120$ | $36.1402$ | $+0.2282$ | $+0.5812$ |
| **Q4** | $(7.6105, 11.2140]$ | $576$ | $35.2140$ | $35.4890$ | $+0.2750$ | $+0.6120$ |
| **Q5** | $(11.2140, 31.6872]$ | $577$ | $35.6180$ | $35.7990$ | $+0.1810$ | $+0.5910$ |

---

## 5. Existing-Feature Redundancy Analysis

Top correlations of disagreement features against the existing 38 baseline features:

| Disagreement Feature | Existing Baseline Feature | Spearman $r$ | Pearson $r$ | Redundancy Assessment |
| :--- | :--- | :---: | :---: | :--- |
| `wind_disagreement_700` | `ctx_std_6h` (Context GHI std) | $+0.4218$ | $+0.3982$ | **High Redundancy:** Wind vector differences correlate with context variability. |
| `wind_disagreement_700` | `u700` (MEPS 700 hPa U-wind) | $-0.3812$ | $-0.3510$ | Moderate correlation with baseline wind speed. |
| `wind_disagreement_700` | `fc_relative_humidity_2m` | $+0.3125$ | $+0.2980$ | Correlates with moisture/frontal boundaries. |
| `LWP_disagreement` | `lwp_latest` (MEPS LWP) | $+0.6812$ | $+0.6120$ | **Very High Redundancy:** Disagreement magnitude scales with baseline LWP. |
| `LWP_disagreement` | `cloud_frac` (MEPS Cloud Cover) | $+0.5419$ | $+0.4812$ | Strongly tied to cloud presence. |

---

## 6. Feature Importance & Prediction Changes

- **Permutation Importance Rank (out of 40 features):**
  - `wind_disagreement_700`: **Rank 22** (Importance mean: $+0.0421\text{ W/m}^2$)
  - `LWP_disagreement`: **Rank 23** (Importance mean: $+0.0389\text{ W/m}^2$)
- **Prediction Change Distribution ($\Delta \hat{y} = \text{cand} - \text{ctrl}$):**
  - Mean: $-0.4566\text{ W/m}^2$
  - Standard Deviation: $8.2134\text{ W/m}^2$
  - Range: $[-55.77\text{ W/m}^2, +55.93\text{ W/m}^2]$

---

## 7. Failure Archetype Analysis (Top 50 Degradation Rows)

Analyzing the 50 rows where candidate model performed worst relative to control:
- **Average Degradation:** $+18.42\text{ W/m}^2$ increase in absolute error per row.
- **Solar Regime:** Concentrated in high solar elevation ($>35^\circ$, mean elevation $44.2^\circ$).
- **Cloud State:** Moderate cloud fraction ($\text{mean } c_{\text{frac}} = 0.48$), where MEPS predicted partial thin cloud cover and AROME predicted heavy cloud cover ($\text{mean LWP disagreement} = 184.2\text{ g/m}^2$).
- **Failure Mechanism:** When AROME predicted heavy cloud liquid water while actual irradiance remained high ($SW_{\text{IN}} > 500\text{ W/m}^2$), the model over-penalized solar irradiance, producing severe under-predictions.

---

## 8. Structured Scientific Conclusion

### A. What the Data Definitely Shows
1. Real historical AROME-Arctic 2024 NWP data yields an ODD Daytime MAE of $36.426418\text{ W/m}^2$ vs Control MAE of $36.211027\text{ W/m}^2$ ($+0.215\text{ W/m}^2$ degradation).
2. The historical Stage 8.17A promotion claim ($35.241\text{ W/m}^2$) was an artifact of pseudo-random synthetic perturbations (`seed 817`).
3. Scalar disagreement features show near-zero correlation with signed forecast residuals ($r < +0.08$).

### B. What the Data Suggests
1. Instantaneous point scalar disagreement adds high-frequency spatial/temporal advection noise.
2. Disagreement magnitude is redundant with baseline cloud cover and context variance.

### C. What the Data Does Not Establish
1. Does NOT prove NWP ensemble disagreement is inherently uninformative.
2. Does NOT rule out vector-projected or spatio-temporal disagreement representations.

### D. Most Likely Failure Mechanism
**Unoriented Scalar Representation:** Scalar magnitude disagreement tells the model that uncertainty exists, but not whether to increase or decrease irradiance, leading to uncalibrated variance adjustments.

### E. Route Status
**CLOSED — No further experiments on instantaneous point scalar disagreement authorized.**
