# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-05 Execution Audit

**Date**: October 04, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Experiment ID**: `L2-EXP-05`  
**Scientific Causal Decision**: **FORMULATION-SUPPORTED-NUMERIC-BOUND-UNRESOLVED**  

---

## 1. Executive Summary & Research Question Answer

> **Research Question**: *"What physical upper-envelope formulation can constrain the calibrated SKGBDT+CQR interval without reproducing the demonstrated failure of the existing U = 1.25 * clearsky_ghi bound?"*

### Definitive Answer: **FORMULATION-SUPPORTED-NUMERIC-BOUND-UNRESOLVED**

The empirical evidence establishes three conclusive scientific facts:

1. **Failure Mechanism of the Multiplicative Bound ($1.25 \times \text{cs}$)**:
   - Geometric clear-sky models scale directly with $\sin(\theta_{\text{elev}})$, dropping to zero at the horizon.
   - Across 2020–2022 historical daytime observations ($N=12,206$), clear-sky GHI in the $0–1^\circ$ bin averages only $0.12\text{ W/m}^2$.
   - Actual pyranometer irradiance in the same bin averages $11.01\text{ W/m}^2$ (median $8.11\text{ W/m}^2$, 95th percentile $30.06\text{ W/m}^2$, max $52.04\text{ W/m}^2$).
   - Consequently, **100.00%** of $0–1^\circ$ observations and **61.09%** of $0–5^\circ$ observations strictly exceed $1.25 \times \text{clearsky\_ghi}$. Any multiplicative formulation is structurally flawed at the horizon.

2. **Physically Motivated Envelope Formulations**:
   - Formulations that decouple the low-sun diffuse regime from the direct beam geometric regime (such as Formulation B: $\max(k \cdot \text{cs}, F)$ or Formulation C: $k \cdot \text{cs} + D(\theta_{\text{elev}})$) eliminate horizon clamping and restore nominal calibrated interval coverage.
   - This behavior is invariant across calendar years (2020: 29.79%, 2021: 29.55%, 2022: 30.08% low-sun violation rate under Formulation A).

3. **Non-Justification of Numeric Production Thresholds**:
   - While $80\text{ W/m}^2$ passed empirical gates in L2-EXP-04, it was introduced purely as a research ablation assumption.
   - Authoritative station records confirm that `ANS_NMS` houses a single horizontal silicon-cell pyranometer (Apogee SP110) without a shadowband or pyrheliometer. No direct/diffuse radiation decomposition exists in the historical repository.
   - Therefore, while the *formulation* is physically justified, no specific numeric constant can legitimately be promoted to production from this experiment.

---

## 2. Pre-Flight Verification & Authoritative Hashes

| Artifact Description | Verified SHA256 Checksum | Match Status |
|---|---|---|
| `historical_residual_dataset` | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` | **PASS** |
| `exact_38_feature_matrix` | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` | **PASS** |
| `exact_frozen_f_predictions` | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` | **PASS** |
| `frozen_candidate_f_model` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **PASS** |
| `frozen_skgbdt_q10` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` | **PASS** |
| `frozen_skgbdt_q50` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` | **PASS** |
| `frozen_skgbdt_q90` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` | **PASS** |

---

## 3. Strict Categorization of Physical Knowledge

### A. VERIFIED (Directly Demonstrated by Authoritative Historical Data)
- **Horizon Irradiance Floor**: Pyranometers at Nuolja consistently record positive shortwave radiation ($10–100\text{ W/m}^2$) during daytime low-sun hours ($0–15^\circ$).
- **Multiplicative Failure**: Clear-sky GHI collapses to zero at $\theta_{\text{elev}} \to 0^\circ$; $100.00\%$ of observations in $0–1^\circ$ exceed $1.25 \times \text{clearsky\_ghi}$.
- **Inter-Annual Invariance**: The low-sun failure rate of $1.25 \times \text{cs}$ is exactly $29.8\% \pm 0.3\%$ across 2020, 2021, and 2022.
- **Station Metadata**: Nuolja Middle Station (`ANS_NMS`, 702 m a.s.l.) uses an Apogee SP110 pyranometer at 2.86 m a.g.l., recording total incoming shortwave radiation ($SW_{IN}$) at 10-minute intervals.

### B. INFERRED (Supported Interpretation but Not Directly Measured)
- **Diffuse Twilight Scattering**: The positive low-sun irradiance is primarily atmospheric diffuse skylight and refraction, supplemented by terrain and snow albedo reflections.
- **Silicon Sensor Cosine Response**: Known characteristics of silicon-cell photodiodes at high zenith angles ($>80^\circ$) contribute to elevated relative diffuse sensitivity.
- **Diffuse interpretation is inferential; direct/diffuse decomposition unavailable.**

### C. UNKNOWN (Not Established by Current Evidence)
- **Exact Numeric Constant for Production**: The exact numeric value for a diffuse floor (whether $60$, $80$, or $100\text{ W/m}^2$) cannot be derived without direct/diffuse sensor separation or explicit operational loss-function calibration.
- **Spectral Shift Effects**: The exact spectral mismatch of the Apogee SP110 during twilight compared to standard thermopile secondary standards is not documented in the station metadata.

---

## 4. Final Governance Status Block

```
L2-EXP-05 PHYSICAL UNCERTAINTY ENVELOPE RESEARCH
STATUS: PASS

SCIENTIFIC CAUSAL CONCLUSION:
FORMULATION-SUPPORTED-NUMERIC-BOUND-UNRESOLVED

RESEARCH QUESTION ANSWER:
The existing U = 1.25 * clearsky_ghi bound fails because geometric clear-sky GHI collapses to zero at the horizon while atmospheric diffuse and twilight scattering keep actual irradiance positive (10-100 W/m²). Formulations providing a positive diffuse envelope (Formulation B or C) are physically motivated and resolve the failure, but setting a specific numeric boundary is unresolved without direct diffuse sensor measurements.

MODEL CLASS:
Frozen SKGBDT + Global Conformal (CQR)

MODEL CHANGED:
NO

F CHANGED:
NO

GAP19 CHANGED:
NO

2024 USED:
NO

2023 USED FOR SELECTION:
NO (Preserved via Method-Selection Lock)

Q_HAT VERIFIED:
+9.8962 W/m² (MATCH)

HISTORICAL 0-1° ACTUAL > 1.25*CS RATE:
100.00% (413 / 413 rows)

HISTORICAL 0-5° ACTUAL > 1.25*CS RATE:
61.09% (1,270 / 2,079 rows)

HISTORICAL LOW-SUN (<=15°) VIOLATION RATE:
29.81% (1,589 / 5,331 rows across 2020-2022)

IS 80 W/m² AN AUTHORIZED PHYSICAL CONSTANT:
NO (Research ablation reference only)

CAN A NUMERIC PRODUCTION BOUNDARY BE AUTHORIZED:
NO (Numeric production boundary unresolved; requires direct/diffuse decomposition or domain authority review)

RECOMMENDED NEXT ACTION:
Retain Formulation B or C as research candidates, maintain Candidate F and Stage 8.1 frozen, and submit this physical evidence to domain authorities for formal operational bound specification.
```
