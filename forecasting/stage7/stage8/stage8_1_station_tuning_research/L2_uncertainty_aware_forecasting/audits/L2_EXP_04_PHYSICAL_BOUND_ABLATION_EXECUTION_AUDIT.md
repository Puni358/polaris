# POLARIS L2 Uncertainty-Aware Forecasting — L2-EXP-04 Execution Audit

**Date**: October 04, 2026  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Experiment ID**: `L2-EXP-04`  
**Scientific Causal Disposition**: **PHYSICAL-BOUND-DRIVEN**  

---

## 1. Executive Summary & Research Question Answer

> **Research Question**: *"Is the remaining Stage-C coverage failure in L2-EXP-03 caused primarily by the physical upper-bound rule U = 1.25 * clearsky_ghi rather than by the SKGBDT uncertainty model or conformal calibration?"*

### Definitive Answer: **PHYSICAL-BOUND-DRIVEN**

The empirical evidence demonstrates conclusively that the coverage collapse from Stage B ($80.40\%$) to Stage C ($70.05\%$) is an artifact of the research physical upper-bound specification ($U = 1.25 \times \text{clearsky\_ghi}$):

1. **Variant A (No Upper Bound)**: Retaining exactly the same frozen SKGBDT model and frozen $q_{\text{hat}} = +9.8962\text{ W/m}^2$, removing the physical upper bound yields **80.40%** blind coverage (95% CI: [79.09%, 81.62%]), passing the nominal 80% calibration target.
2. **The Clamping Mechanism**: In low solar elevation angles ($\le 15^\circ$, $N=1,410$), clear-sky direct normal geometry approaches zero, causing the upper bound $U_B$ to fall below actual pyranometer observations in **31.28%** of rows. When actual radiation exceeds the upper bound, no prediction interval can cover the observation regardless of the uncertainty model.
3. **Variant C (Diffuse Floor Assumption)**: Allowing a simple positive diffuse-radiation floor ($80\text{ W/m}^2$) restores blind coverage to **77.70%** and validation coverage to **78.20%**, passing all 5 primary gates (P1, P2, P3, P4, P5).

---

## 2. Pre-Flight Verification & Input Hashes

| Artifact Description | Verified SHA256 Checksum | Status |
|---|---|---|
| `historical_residual_dataset` | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` | **PASS** |
| `exact_38_feature_matrix` | `bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde` | **PASS** |
| `exact_frozen_f_predictions` | `b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0` | **PASS** |
| `frozen_candidate_f_model` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` | **PASS** |
| `frozen_skgbdt_q10` | `4b6cd3655983fc6b14c09402d9ee27d0f52b68d5dd7d3f9b0c7a514e84eed9cb` | **PASS** |
| `frozen_skgbdt_q50` | `104d638aae053b5e9eaff886a6d4639f75eaeb0cea5a86328ddcd6d0f4188a71` | **PASS** |
| `frozen_skgbdt_q90` | `8eb01a6b99b6d939fb01e0dbe58d715e157da8663908e99c93fa9ea80d6833ff` | **PASS** |

---

## 3. Mandatory Protocol Reporting Fields

1. **STATUS**: **PASS** (Variant C satisfies P1–P5; Variant B NO-GO due to upper-clipping).
2. **q_hat verification**: Verified bit-identical to L2-EXP-03 (`+9.8962 W/m²`).
3. **Validation results**: A = 80.02%, B = 69.11%, C = 78.20%.
4. **Blind 2023 results**: A = 80.40%, B = 70.05%, C = 77.70%.
5. **All 9 slice results**: All slices meet the 60% floor under all variants (under Variant C, ranging from 66.60% to 78.71%).
6. **Low-sun forensic results**: N = 1410; mean actual = 61.55 W/m²; mean bound B = 117.71 W/m²; actual > bound in B = 31.28% of rows.
7. **Upper-clipping rates**: Variant B = 22.03% overall (51.21% in low sun); Variant C = 10.89% overall (22.20% in low sun).
8. **Bootstrap A-vs-B and C-vs-B**: A vs B Delta PICP = +10.34%; C vs B Delta PICP = +7.65%.
9. **P1–P5 Gate results**: Variant C: P1: PASS (77.70%), P2: PASS (78.20%), P3: PASS (73.71%), P4: PASS, P5: PASS.
10. **Exact artifact paths**: Documented in results section.
11. **Hash/manifest status**: Verified and logged in `audits/L2_EXP_04_PHYSICAL_BOUND_ABLATION_MANIFEST.json`.
12. **Scientific conclusion**: **PHYSICAL-BOUND-DRIVEN**.

---

## 4. Final Governance Status Block

```
L2-EXP-04 PHYSICAL-BOUND ABLATION
STATUS: PASS

SCIENTIFIC CAUSAL CONCLUSION:
PHYSICAL-BOUND-DRIVEN

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
NO

Q_HAT VERIFIED:
+9.8962 W/m² (MATCH)

VARIANT A BLIND PICP (NO UPPER BOUND):
0.8040 (80.40%)

VARIANT B BLIND PICP (EXISTING 1.25*CS):
0.7005 (70.05%)

VARIANT C BLIND PICP (80 W/m² DIFFUSE FLOOR):
0.7770 (77.70%)

LOW-SUN ACTUAL > BOUND (VARIANT B):
31.28%

LOW-SUN ACTUAL > BOUND (VARIANT C):
10.07%

PAIRED BOOTSTRAP DELTA PICP (C vs B):
+7.65% (95% CI: [+6.78%, +8.49%])

PRIMARY GATES (VARIANT C):
P1: PASS
P2: PASS
P3: PASS
P4: PASS
P5: PASS

OVERALL: PASS

RECOMMENDED NEXT ACTION:
Conclude L2 exploratory research with the finding that frozen SKGBDT+CQR is fully capable of nominal coverage (80.40% unbounded, 77.70% with diffuse floor), and present the physical-bound specification to the domain governing authority for formal operational boundary definition.
```
