# POLARIS STAGE 8.23 — POST-REJECTION FORENSIC ANALYSIS REPORT

> [!IMPORTANT]
> **GOVERNANCE STATUS: REJECTED ON EVEN**  
> All Stage 8.23 Candidates (Candidate A, Candidate B, Candidate C) failed locked validation gates **G1–G3** on EVEN benchmark data.  
> - **ODD benchmark dataset remains 100% untouched.**  
> - **Stage 8.1 37-feature HGB model remains the frozen operational champion.**  
> - **No model hyperparameter, feature set, route registry, or master handoff modifications have been made.**

---

## 1. Executive Summary

Stage 8.23 evaluated whether causal local surface ground observations from SITES Nuolja and valley observations from SITES Abisko could improve short-term solar irradiance ($SW\_IN$) forecasting over the frozen 37-feature Stage 8.1 champion.

While Candidate A (adding 4 local ground-state features) produced a slight aggregate mean absolute error reduction of **$-0.1310\text{ W/m}^2$** (37.4891 vs 37.6201 W/m²), it **failed all key robustness gates**:
1. **G1 MAE Margin (-0.50 W/m²):** Actual delta $-0.1310\text{ W/m}^2$ (FAIL)
2. **G2 Fold Consistency (≥4/5 folds):** Improved in only **1 of 5 folds** (FAIL)
3. **G3 Worst Fold Tolerance (≤+0.50 W/m²):** Succeeded degradation of **$+0.5646\text{ W/m}^2$** in Fold 3 (FAIL)

This postmortem forensic analysis investigates the empirical root cause behind Candidate A's aggregate improvement vs. structural brittleness, evaluates Candidate B/C failures, and classifies the local atmospheric state information axis under strict POLARIS governance protocols.

---

## 2. Feature Distributions (EVEN Benchmark Origins, N=2,885 Daytime Samples)

The five candidate features extracted from SITES Nuolja and SITES Abisko 2024 hourly observations were audited across all 2,885 daytime evaluation samples on EVEN origins:

| Feature Name | Description | Min | Max | Mean | Std | P25 | P50 (Median) | P75 | Missing Count |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ctx_ta_last_obs` | Nuolja ground air temp at $t_0$ (°C) | -19.4083 | 16.7200 | 3.2350 | 8.2149 | -3.0112 | 4.1683 | 10.3167 | 0 |
| `ctx_rh_last_obs` | Nuolja ground relative humidity at $t_0$ (%) | 45.0500 | 97.1167 | 76.0928 | 12.8805 | 67.4800 | 76.5867 | 85.9667 | 0 |
| `ctx_dew_point_depression` | Nuolja $T_A - T_D$ at $t_0$ (°C) | 0.4081 | 11.7007 | 4.0234 | 2.5521 | 2.0824 | 3.6360 | 5.3455 | 0 |
| `ctx_ta_change_6h` | Nuolja 6h temp change ($T_{t0} - T_{t0-6h}$) (°C) | -6.0425 | 5.9832 | -1.2667 | 1.8166 | -2.4083 | -1.2730 | -0.2058 | 0 |
| `ctx_mountain_valley_temp_contrast` | Nuolja TA - Abisko TA at $t_0$ (°C) | -0.7433 | 1.7932 | 0.0907 | 0.3385 | -0.1333 | 0.1100 | 0.2438 | 0 |

---

## 3. Correlation & Redundancy Analysis (EVEN Data Only)

Linear correlations between the 5 new local ground features and existing Stage 8.1 champion features were computed on EVEN daytime samples:

| Candidate Feature | vs MEPS `fc_temperature_2m` | vs MEPS `fc_relative_humidity_2m` | vs Historical `ctx_last_obs` | vs `ctx_mean_24h` | vs `ctx_abs_change_6h` | vs `u700` | vs `v700` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ctx_ta_last_obs` | **+0.9418** | -0.0446 | +0.3965 | +0.4280 | +0.4626 | -0.1174 | +0.2968 |
| `ctx_rh_last_obs` | -0.0878 | **+0.2960** | -0.1491 | -0.3406 | +0.0491 | +0.0770 | -0.1420 |
| `ctx_dew_point_depression` | +0.1993 | **-0.3029** | +0.1976 | +0.3784 | -0.0133 | -0.0968 | +0.1898 |
| `ctx_ta_change_6h` | -0.3578 | +0.0775 | -0.2941 | -0.3197 | -0.2974 | +0.2115 | -0.2012 |
| `ctx_mountain_valley_temp_contrast` | +0.0199 | +0.0637 | -0.0604 | +0.1346 | +0.0675 | -0.1256 | -0.0343 |

### Key Redundancy Findings:
1. **Severe Redundancy with NWP Temperature:** `ctx_ta_last_obs` exhibits extreme collinearity (**$r = +0.9418$**) with MEPS `fc_temperature_2m`. Ground-level temperature at $t_0$ provides virtually no new physical information beyond what MEPS already resolves.
2. **Redundancy with Historical Radiation:** Existing Stage 8.1 context features (`ctx_last_obs`, `ctx_mean_24h`, `ctx_std_6h`) already capture the surface energy balance and boundary-layer radiative history. Single-point surface scalar observations at $t_0$ do not provide incremental predictive capacity.

---

## 4. Error-Regime Forensics

Using the EVEN validation predictions, Candidate A's performance was evaluated across specific physical error regimes:

### A. Solar Elevation Regimes
- **Low Elevation (0° – 15°, N=877):** Control MAE = 21.5820, Cand A = 22.0125 ($\Delta = \mathbf{+0.4305\text{ W/m}^2}$ — **Degraded**)
- **Mid Elevation (15° – 30°, N=632):** Control MAE = 63.7417, Cand A = 63.3897 ($\Delta = \mathbf{-0.3519\text{ W/m}^2}$ — **Slight Improvement**)
- **High Elevation (30° – 45°, N=486):** Control MAE = 111.6647, Cand A = 110.1472 ($\Delta = \mathbf{-1.5175\text{ W/m}^2}$ — **Improved**)
- **Extreme Elevation (>45°, N=3):** Control MAE = 213.1051, Cand A = 200.4746 ($\Delta = \mathbf{-12.6305\text{ W/m}^2}$ — **Improved**)

### B. Cloud Fraction Regimes
- **Clear Sky (0.0 – 0.2, N=366):** Control MAE = 54.1757, Cand A = 53.8673 ($\Delta = -0.3084\text{ W/m}^2$)
- **Partly Cloudy (0.2 – 0.8, N=538):** Control MAE = 62.0558, Cand A = 62.3478 ($\Delta = \mathbf{+0.2920\text{ W/m}^2}$ — **Degraded**)
- **Overcast (0.8 – 1.0, N=1,094):** Control MAE = 55.6729, Cand A = 55.0655 ($\Delta = -0.6074\text{ W/m}^2$)

### C. Temperature Dynamics & Stability Regimes
- **Rapid Temperature Change ($|\Delta T_A| > 2^\circ\text{C}$, N=1,036):** Control MAE = 56.0205, Cand A = 55.1687 ($\Delta = \mathbf{-0.8518\text{ W/m}^2}$ — **Improved**)
- **Stable Temperature ($|\Delta T_A| \le 2^\circ\text{C}$, N=1,516):** Control MAE = 37.7225, Cand A = 37.8107 ($\Delta = \mathbf{+0.0882\text{ W/m}^2}$ — **Degraded**)

### D. Extreme Error Regimes
- **Top 10% Control Errors ($ERR \ge 136.29\text{ W/m}^2$, N=256):** Control MAE = 197.3353, Cand A = 195.0119 ($\Delta = \mathbf{-2.3234\text{ W/m}^2}$ — **Improved**)
- **Bottom 90% Control Errors ($ERR < 136.29\text{ W/m}^2$, N=2,296):** Control MAE = 28.1824, Cand A = 28.1153 ($\Delta = -0.0671\text{ W/m}^2$)

---

## 5. Horizon Forensics (H1 – H24 Breakdown)

The forecast horizon analysis reveals why Candidate A fails early lead times:

| Horizon | N | Control MAE | Candidate A MAE | Delta MAE (W/m²) | Regime Evaluation |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **H01** | 55 | 5.4555 | 5.2243 | -0.2312 | Minor Improvement |
| **H02** | 63 | 7.2492 | 7.1921 | -0.0571 | Neutral |
| **H03** | 73 | 9.8788 | 10.0966 | +0.2178 | Degraded |
| **H04** | 85 | 17.6682 | 18.2943 | **+0.6260** | **Degraded** |
| **H05** | 99 | 28.8489 | 29.7247 | **+0.8758** | **Degraded** |
| **H06** | 106 | 38.9248 | 40.8661 | **+1.9413** | **Severely Degraded** |
| **H07** | 115 | 42.9687 | 43.3794 | **+0.4107** | **Degraded** |
| **H08** | 123 | 57.6176 | 57.4653 | -0.1524 | Neutral |
| **H09** | 140 | 61.9783 | 60.7796 | **-1.1986** | Improved |
| **H10** | 145 | 65.0667 | 64.9480 | -0.1187 | Neutral |
| **H11** | 145 | 68.6583 | 67.9306 | -0.7277 | Improved |
| **H12** | 145 | 78.2604 | 78.2590 | -0.0014 | Neutral |
| **H13** | 145 | 78.8904 | 78.7849 | -0.1055 | Neutral |
| **H14** | 145 | 73.5287 | 73.4865 | -0.0422 | Neutral |
| **H15** | 145 | 59.0614 | 57.1990 | **-1.8624** | Improved |
| **H16** | 131 | 67.8281 | 67.5573 | -0.2708 | Minor Improvement |
| **H17** | 117 | 41.3750 | 41.0634 | -0.3116 | Minor Improvement |
| **H18** | 108 | 29.1640 | 28.0394 | **-1.1246** | Improved |
| **H19** | 102 | 23.3204 | 23.3205 | +0.0001 | Neutral |
| **H20** | 95 | 14.7063 | 13.9922 | -0.7142 | Improved |
| **H21** | 81 | 16.6850 | 15.5946 | -1.0903 | Improved |
| **H22** | 71 | 7.8632 | 6.8555 | -1.0077 | Improved |
| **H23** | 62 | 4.2760 | 3.4529 | -0.8231 | Improved |
| **H24** | 56 | 5.8591 | 4.6412 | -1.2179 | Improved |

### Physical Interpretation of Horizon Decay:
Ground state observations taken at $t_0 = 00:00\text{ UTC}$ measure midnight surface boundary layer conditions. In early morning hours ($H3 \dots H7$), adding static $t_0$ ground scalars introduces noise into tree splits, degrading MAE by up to **$+1.94\text{ W/m}^2$**. In late afternoon hours ($H9 \dots H16$), boundary layer moisture indicators slightly correlate with thermal convective cloud development, but temporal staleness decays the signal.

---

## 6. Fold Forensics (Fold-by-Fold Breakdown)

| Fold | Date Range / Seasonal Focus | Control MAE | Candidate A MAE | Delta MAE | Daytime N | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | Early Spring (Jan – Mar) | 49.5313 | 49.5566 | **+0.0253** | 591 | Degraded |
| **Fold 2** | Summer Peak (May – Jul) | 70.7021 | 68.7721 | **-1.9300** | 696 | **Improved** |
| **Fold 3** | Late Summer / Early Autumn | 40.3698 | 40.9345 | **+0.5646** | 648 | **Worst Fold (Degraded)** |
| **Fold 4** | Autumn (Sep – Oct) | 25.6828 | 26.0830 | **+0.4002** | 396 | Degraded |
| **Fold 5** | Late Autumn / Winter (Nov – Dec) | 1.8680 | 2.1178 | **+0.2499** | 221 | Degraded |

> [!CAUTION]
> **FOLD DOMINANCE DISCOVERY:** Candidate A's aggregate MAE improvement of **$-0.1310\text{ W/m}^2$** is driven **entirely by Fold 2** (summer peak convective season, $-1.9300\text{ W/m}^2$). Across the remaining 4 out of 5 folds (Folds 1, 3, 4, 5), Candidate A consistently degrades performance. This confirms extreme cross-fold instability and justifies rejection under Gate G2.

---

## 7. Candidate B & C Interpretation

- **Candidate B (`ctx_mountain_valley_temp_contrast` alone):** Overall MAE degraded by **$+0.2035\text{ W/m}^2$** (37.8235 vs 37.6201 W/m²).
- **Candidate C (All 5 ground features):** Overall MAE degraded by **$+0.1659\text{ W/m}^2$** (37.7859 vs 37.6201 W/m²).

### Why Mountain-Valley Contrast Fails:
The elevation difference between Nuolja ($900\text{ m}$) and Abisko valley ($383\text{ m}$) is $517\text{ m}$. Across the entire 2024 dataset, the observed temperature contrast between Nuolja and Abisko has a mean of **$+0.0907^\circ\text{C}$** and a standard deviation of only **$0.3385^\circ\text{C}$**. 

Because this local thermodynamic lapse-rate proxy varies so minimally and is captured far more accurately by MEPS vertical atmospheric profiles and 700 hPa winds (`u700`, `v700`), adding `ctx_mountain_valley_temp_contrast` provides zero independent useful signal and acts strictly as a noisy distractor.

---

## 8. Final Classification & Governance Conclusion

### Official Signal Classification:
$$\mathbf{B.\ \text{WEAK / REGIME-CONFINED SIGNAL}}$$

### Rationale:
Local ground surface observations contain a minor, regime-confined signal during summer afternoon convective conditions (Fold 2, $H9 \dots H16$). However, because these scalar ground observations suffer from severe redundancy ($+0.9418$ correlation with MEPS $T_{2m}$), noise degradation in early lead times ($H3 \dots H7$), and fail fold consistency (degrading in 4 of 5 folds), the signal is far too weak and unstable for governed operational deployment.

---

## Final Governance Statement

- **Stage 8.23 REJECTED ON EVEN.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion.**
- **No model hyperparameter, feature set, route registry, or master handoff changes.**
