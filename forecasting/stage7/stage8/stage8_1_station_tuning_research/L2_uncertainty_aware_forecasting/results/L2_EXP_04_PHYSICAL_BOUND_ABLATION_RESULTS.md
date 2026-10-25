# POLARIS L2-EXP-04 — Physical-Bound Ablation Results

**Execution Timestamp**: 2026-10-04 05:35:03 UTC  
**Scientific Causal Conclusion**: **PHYSICAL-BOUND-DRIVEN**  

---

## 1. Executive Summary & Variant Comparison

| Ablation Variant | Description / Label | Blind Stage C PICP | 95% Bootstrap CI | MPIW | Winkler Score | Low-Sun (<=15°) PICP |
|---|---|---|---|---|---|---|
| **Variant A** | NO UPPER BOUND (Diagnostic Only) | **80.40%** | [79.09%, 81.62%] | 151.85 W/m² | 228.77 | **86.38%** |
| **Variant B** | EXISTING RESEARCH BASELINE (1.25*cs) | **70.05%** | [68.53%, 71.49%] | 146.08 W/m² | 244.94 | **60.00%** |
| **Variant C** | RESEARCH ABLATION (80 W/m² Floor) | **77.70%** | [76.31%, 78.95%] | 149.34 W/m² | 234.15 | **79.93%** |

## 2. Low Solar Elevation Forensic Findings (<= 15 deg, N=1,410)

- **Observed Actual Irradiance**: Mean observed solar irradiance during low-sun hours is **61.55 W/m²** (pyranometer recording diffuse and horizon scattering).
- **Variant B Clamping Pathology**: The geometric clear-sky model forces $U_B = 1.25 \times \text{clearsky\_ghi}$ towards zero near the horizon (mean $U_B = 117.71\text{ W/m}^2$). Consequently, **51.21%** of calibrated upper quantiles are clipped downward, and in **31.28%** of all low-sun observations, the actual solar irradiance strictly exceeds the physical upper bound itself!
- **Variant C Correction**: Allowing a conservative positive diffuse floor ($80\text{ W/m}^2$) raises low-sun coverage from **60.00%** to **79.93%**, reducing clipping to 22.20% and bound violations to 10.07%.

## 3. Paired Bootstrap Statistical Comparison

- **A vs B (No Upper Bound vs Existing)**:
  - Delta PICP: **+10.34%** (95% CI: [+9.37%, +11.27%])
  - Delta MPIW: **+5.78 W/m²** (95% CI: [+5.36, +6.22])
  - Delta Winkler: **-16.17** (95% CI: [-18.54, -13.83])

- **C vs B (80 W/m² Diffuse Floor vs Existing)**:
  - Delta PICP: **+7.65%** (95% CI: [+6.78%, +8.49%])
  - Delta MPIW: **+3.26 W/m²** (95% CI: [+2.96, +3.59])
  - Delta Winkler: **-10.79** (95% CI: [-12.67, -9.01])

## 4. Required Blind Slices Breakdown

| Slice Definition | N | Variant A PICP | Variant B PICP | Variant C PICP | Variant C MPIW | Variant C Winkler |
|---|---|---|---|---|---|---|
| **1. h06_h10** | 1065 | 78.69% | 69.20% | **73.71%** | 183.08 W/m² | 300.02 |
| **2. h11_h15** | 1260 | 78.73% | 73.73% | **78.57%** | 187.70 W/m² | 290.73 |
| **3. h16_h20** | 789 | 82.89% | 78.71% | **82.89%** | 91.30 W/m² | 128.08 |
| **4. h21_h24** | 20 | 90.00% | 75.00% | **90.00%** | 26.32 W/m² | 33.25 |
| **5. elev_le15** | 1410 | 86.38% | 60.00% | **79.93%** | 66.47 W/m² | 109.88 |
| **6. elev_gt15** | 2263 | 76.67% | 76.31% | **76.31%** | 200.97 W/m² | 311.58 |
| **7. clear_lt0.20** | 988 | 82.69% | 66.60% | **75.00%** | 139.98 W/m² | 235.99 |
| **8. partial_0.20_0.80** | 727 | 80.74% | 69.33% | **78.40%** | 162.14 W/m² | 239.69 |
| **9. overcast_gt0.80** | 1958 | 79.11% | 72.06% | **78.80%** | 149.30 W/m² | 231.16 |
