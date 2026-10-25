# POLARIS L2 Uncertainty-Aware Forecasting — L2-CALIBRATION-EXP-01 Execution Report

**Date**: October 4, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Experiment ID**: `L2-CALIBRATION-EXP-01`  
**Experiment Type**: Post-Hoc Validation-Only Calibration (NO MODEL RETRAINING)  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l.)  
**Overall Status**: **NO-GO**  

---

## 1. Executive Summary & Research Question Answer

### Research Question:
> *"Can validation-only conditional calibration of the existing L2-EXP-01 quantile predictions produce a blind 2023 interval that satisfies the calibration gates, without retraining or changing the underlying uncertainty model?"*

### Definitive Answer: **NO**

Validation-only conditional calibration **cannot** rescue the frozen L2-EXP-01 quantile predictions under the required qualification gates:
1. **Primary Coverage Gate (P1) Failed**: Across all four evaluated calibration schemes (Global, Horizon-Conditional, Solar-Elevation-Conditional, and Horizon+Elevation-Conditional), the post-hoc Stage C blind empirical coverage remained between **71.14% and 71.79%**, failing the pre-registered $[76.0\%, 84.0\%]$ nominal coverage band.
2. **Sub-Slice Collapse (P3) Unresolved**: Conditional calibration failed to resolve the catastrophic under-coverage in late horizons ($h \in [21..24]$, where blind coverage remained frozen at **25.00%**) and low solar elevation angles ($0^\circ < \theta \le 15^\circ$, where blind coverage remained at **55.04% – 56.31%**, failing the 60.0% floor).
3. **Root Mechanism Diagnosed**: In unconstrained statistical space (Stage B), conformal calibration achieves **80.18% – 81.08%** blind coverage. However, applying the pre-registered physical upper bound ($U = 1.25 \times \text{clearsky\_ghi}$) forcibly clips legitimate solar radiation observations during low-sun and twilight hours where cloud enhancement and diffuse scattering exceed clear-sky geometry. Furthermore, late horizon lead times ($h \in [21..24]$) had zero daytime calibration samples in 2022, forcing all conditional methods to fall back to global calibration on those hours.

---

## 2. Authoritative Input Artifacts & Verification Hashes

All inputs were verified before execution; all hashes matched authoritative records:

| Artifact Description | File Path | SHA256 Checksum | Gate Status |
|---|---|---|---|
| Frozen Candidate F Model | `stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **PASS** |
| Exact 38-Feature Matrix | `candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv` | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` | **PASS** |
| Exact Frozen F Predictions | `candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv` | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` | **PASS** |
| Authoritative Residual Dataset | `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` | **PASS** |
| Frozen L2-EXP-01 Full Predictions | `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/results/L2_EXP_01_PREDICTIONS_2020_2023.csv` | `1eb5b6db7c426c2c173c170a2cdd87945f0946f80153cc40f6180410de5a817c` | **PASS** |

---

## 3. Calibration Methods & Parameter Estimation (2022 Validation Only)

All calibration corrections were estimated strictly from the **4,069 daytime observations** in the 2022 Validation partition. Zero 2023 data was used during calibration parameter estimation.

### Calibration Schemes Summary:

| Method | Conditioning Dimension | Distinct Calibration Cells | Fallback Hierarchy | Min Samples / Cell | Correction Range ($s$) |
|---|---|---|---|---|---|
| **A. Global** | None (marginal) | 1 | None | $N=4,069$ | `+0.7917 W/m²` |
| **B. Horizon-Conditional** | `horizon_hour` ($h \in [1..24]$) | 24 | Horizon $\rightarrow$ Global if $N < 50$ | $N \in [58, 319]$ (for $h \le 19$) | `-4.0928` to `+8.4254 W/m²` |
| **C. Solar-Elevation** | $\theta \le 15^\circ$ vs $\theta > 15^\circ$ | 2 | Regime $\rightarrow$ Global if $N < 50$ | $N \in [1775, 2294]$ | `+0.4535` to `+2.1679 W/m²` |
| **D. Horizon x Elevation** | 4 blocks x 2 elev bins | 8 | Cell -> Elev Bin -> Global | $N \in [386, 1034]$ (for $h \le 20$) | `-2.6230` to `+5.7664 W/m²` |

### Fallback Governance & Cell Sample Support:
- **Method A**: $N=4,069 \gg 50$; zero fallbacks.
- **Method B**: Horizons 1 to 19 have between 58 and 319 daytime samples in 2022; each received an individual horizon correction. Horizons 20–24 have zero samples in 2022 (only present in 48 recovered MEPS runs); these cleanly triggered the pre-declared fallback to global calibration.
- **Method C**: Low Sun ($N=1,775$) and High Sun ($N=2,294$) both exceed the 50-sample floor by over $35\times$; zero fallbacks.
- **Method D**: Cells covering horizons 1–20 have $N \in [386, 1034]$; the peripheral block $h \in [21..24]$ had zero samples and fell back to the elevation-bin correction.

---

## 4. Comprehensive Evaluation Results

### A. VALIDATION 2022 Diagnostic Consistency (4,069 Daytime Rows)

| Calibration Method | Stage B PICP (Unbounded) | Stage C PICP (Physical) | MPIW (Sharpness) | Winkler Score ($\alpha=0.20$) | Median q50 MAE |
|---|---|---|---|---|---|
| **A_global** | 80.02% | **69.80%** | 169.00 W/m² | 245.61 | 55.77 W/m² |
| **B_horizon_conditional** | 80.51% | **70.43%** | 170.30 W/m² | 245.25 | 55.77 W/m² |
| **C_solar_elevation_conditional** | 80.04% | **69.97%** | 170.33 W/m² | 245.57 | 55.77 W/m² |
| **D_horizon_plus_elevation_conditional** | 80.17% | **70.16%** | 171.98 W/m² | 245.33 | 55.77 W/m² |

### B. BLIND 2023 Qualification Evaluation (3,673 Daytime Rows, Single-Use)

| Calibration Method | Stage B PICP | Stage C PICP | 95% Bootstrap CI | MPIW | Winkler Score | Gate P1 | Gate P2 | Gate P3 | Status |
|---|---|---|---|---|---|---|---|---|---|
| **A_global** | 80.34% | **71.22%** | [69.75%, 72.72%] | 182.27 W/m² | 258.22 | FAIL | FAIL | FAIL | **NO-GO** |
| **B_horizon_conditional** | 81.08% | **71.79%** | [70.30%, 73.24%] | 183.63 W/m² | 258.41 | FAIL | FAIL | FAIL | **NO-GO** |
| **C_solar_elevation_conditional** | 80.18% | **71.14%** | [69.67%, 72.64%] | 183.76 W/m² | 258.33 | FAIL | FAIL | FAIL | **NO-GO** |
| **D_horizon_plus_elevation_conditional** | 80.64% | **71.66%** | [70.21%, 73.16%] | 185.45 W/m² | 258.51 | FAIL | FAIL | FAIL | **NO-GO** |

---

## 5. Required Blind Slices Breakdown (Stage C Physically Bounded)

| Slice Definition | Sample Count ($N$) | Method A (Global) | Method B (Horizon) | Method C (Solar Elev) | Method D (Horizon+Elev) |
|---|---|---|---|---|---|
| **1. h06_h10** | 1065 | 72.39% | 72.77% | 72.58% | 73.52% |
| **2. h11_h15** | 1260 | 77.14% | 78.17% | 77.06% | 77.94% |
| **3. h16_h20** |  789 | 74.27% | 74.52% | 74.02% | 73.64% |
| **4. h21_h24** |   20 | 25.00% | 25.00% | 25.00% | 25.00% |
| **5. elev_le15** | 1410 | 55.67% | 56.31% | 55.04% | 55.39% |
| **6. elev_gt15** | 2263 | 80.91% | 81.44% | 81.18% | 81.79% |
| **7. clear_lt0.20** |  988 | 67.71% | 68.42% | 67.51% | 68.52% |
| **8. partial_0.20_0.80** |  727 | 67.26% | 67.95% | 67.40% | 67.13% |
| **9. overcast_gt0.80** | 1958 | 74.46% | 74.92% | 74.36% | 74.92% |

---

## 6. Pre-Registered Gate-by-Gate Assessment

| Gate | Requirement | Best Method Observed | Gate Status |
|---|---|---|---|
| **P1 — Blind Overall PICP** | $[76.0\%, 84.0\%]$ | **71.79%** (Method B) | **FAIL** |
| **P2 — Validation Consistency PICP** | $[76.0\%, 84.0\%]$ | **70.43%** (Method B) | **FAIL** |
| **P3 — Blind Sub-Slice Floor** | $\ge 60.0\%$ across all slices | **25.00%** (4. h21_h24) | **FAIL** |
| **P4 — Physical Constraints** | Lower $\ge 0$, Upper $\le U$, night zeroed | 100% rows satisfied | **PASS** |
| **P5 — F Point Forecast Invariance** | Max diff from Candidate F $== 0.0$ | Diff: **0.000000 W/m²** | **PASS** |

---

## 7. Answers to Mandatory Protocol Questions

1. **Did calibration-only processing materially improve blind coverage?**  
   **No.** Blind Stage C coverage increased only from 71.22% (Global) to 71.79% (Horizon-Conditional), a marginal gain of +0.57% that remains far below the 76.0% qualification floor.

2. **Which calibration method performed best?**  
   **Method B (Horizon-Conditional Conformal)** achieved the highest blind coverage (71.79%), followed by Method D (71.66%), Method A (71.22%), and Method C (71.14%). All four methods performed within 0.65% of each other.

3. **Did it pass P1/P2/P3/P4/P5?**  
   **P1, P2, and P3 FAILED** on all four methods. P4 (physical constraints) and P5 (point forecast invariance) PASSED on all four methods.

4. **Did conditional calibration solve the h21–24 failure?**  
   **No.** Coverage for $h \in [21..24]$ was exactly 25.00% across all four methods. Because 2022 validation contained zero daytime rows for horizons 21–24, conditional calibration cleanly fell back to global calibration and could not learn horizon-specific adjustments for late lead times.

5. **Did conditional calibration solve the low-sun failure?**  
   **No.** Low-sun ($0 < \theta \le 15^\circ$) coverage remained between 55.04% and 56.31% across all four methods in Stage C, failing the 60.0% floor.

   MPIW widened slightly from 182.27 W/m² (Global) to 183.63 W/m² (Horizon), 183.76 W/m² (Solar Elevation), and 185.45 W/m² (Horizon+Elevation).

7. **Were calibration cells adequately populated?**  
   Yes for all supported regimes ($N \ge 50$). Where sample support was zero (horizons 20–24 in 2022), the pre-declared fallback rule triggered deterministically.

8. **Was any 2023 information used before blind evaluation?**  
   **No.** 2023 data was evaluated strictly once as a single-use blind test after all calibration parameters and fallback hierarchies were frozen.

9. **Did the F point forecast remain bit-identical?**  
   **Yes.** Maximum absolute difference across all 26,011 rows was exactly 0.000000 W/m².

10. **Is the current L2 architecture worth retaining?**  
    **No.** The low-capacity MLP exhibits fundamental structural under-dispersion at peripheral lead times and low solar angles that cannot be rescued by post-hoc validation calibration.

11. **Should the next experiment be: further calibration research, a different uncertainty model, or stopping L2 research?**  
    **A different uncertainty model.** Calibration alone on a mis-specified base network cannot resolve conditional non-stationarity. Future work must investigate intrinsically adaptive models (such as Quantile GBDT or regime-specialized quantile networks) rather than further post-hoc recalibration.

---

## 8. Evidence Categorization: VERIFIED, INFERRED, UNKNOWN

### A. VERIFIED (Empirically Proven by Authoritative Artifacts)
- **Unconstrained vs Constrained Discrepancy**: In unconstrained statistical space (Stage B), conformal calibration achieves 80.18%–81.08% blind coverage. Applying the physical upper bound $1.25 \times \text{clearsky\_ghi}$ causes a ~9.3% absolute drop in coverage (to 71.14%–71.79%) because actual solar irradiance under broken clouds and low sun frequently exceeds clear-sky model geometry.
- **Sample Horizon Asymmetry**: Horizons 20–24 exist only in 48 recovered MEPS runs and have 0 daytime rows in 2022, making horizon-conditional calibration impossible for those hours using 2022 validation alone.
- **F Point Forecast Integrity**: Candidate F point predictions were preserved with 0.0 W/m² maximum deviation across all 26,011 rows.

### B. INFERRED (Scientifically Grounded Deductions)
- **Physical Clamping Mis-Specification**: The upper bound $U = 1.25 \times \text{clearsky\_ghi}$ is scientifically sound during midday peak sun, but acts as a pathological constraint near the horizon where clear-sky GHI approaches zero while diffuse pyranometer readings remain positive.
- **Network Capacity Bottleneck**: The 995-parameter MLP lacked the feature interaction capacity to distinguish diffuse cloud irradiance from direct beam irradiance at low solar elevations.

### C. UNKNOWN (Requires Subsequent Experimental Testing)
- **Alternative Physical Bounding**: Whether a diffuse-aware upper bound (e.g., $U = \max(50.0, 1.25 \times \text{clearsky\_ghi})$) would restore nominal Stage C coverage without violating EMS safety constraints.
- **Quantile GBDT Viability**: Whether tree-based quantile models that directly partition the 38-feature matrix can achieve valid coverage natively without requiring post-hoc shifts.

---

## 9. Final Governance Status Block

```
L2 CALIBRATION EXP-01
STATUS: NO-GO

MODEL CHANGED: NO
F CHANGED: NO
GAP19 CHANGED: NO
2024 USED: NO
2023 USED FOR CALIBRATION: NO

BEST METHOD: B_horizon_conditional
BLIND PICP: 0.7179 (71.79%)
BLIND PICP CI: [0.7030, 0.7324]
WORST REQUIRED SLICE: 4. h21_h24 = 0.2500 (25.00%)
MPIW: 183.63 W/m²

POINT FORECAST INVARIANCE: PASS
OVERALL GATE: FAIL

RECOMMENDED NEXT ACTION: Transition from post-hoc MLP calibration to an intrinsically adaptive uncertainty architecture (e.g., Quantile GBDT) that can natively accommodate solar elevation and horizon non-stationarities.
```
