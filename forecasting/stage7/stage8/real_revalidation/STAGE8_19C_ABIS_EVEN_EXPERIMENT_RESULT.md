# POLARIS STAGE 8.19C — ABIS GNSS EVEN-ONLY EXPERIMENT RESULT

**Stage**: POLARIS Stage 8.19C SWEPOS Abisko (`ABIS`) GNSS EVEN-Only Experiment  
**Timestamp**: `2026-09-13T09:48:30+00:00`  
**Final Status**: **`EVEN GATES PASSED — FREEZE REQUIRED`**  
**ODD Access**: **ZERO ODD ACCESS — STRICT ODD FIREWALL MAINTAINED**  

---

## 1. Executive Summary & Verification

This experiment evaluated the pre-registered candidate features derived from the SWEPOS Abisko (`ABIS`) GNSS Zenith Total Delay (`ZTD`) product against the frozen **Stage 8.17A champion control model** under the locked 5-fold forward-chaining **EVEN-indexed development dataset** (174 origins).

```
================================================================================
POLARIS STAGE 8.19C FINAL EVALUATION SUMMARY:
================================================================================
1. Control Reproduction (Ref: 44.296582 W/m²):      EXACT MATCH (44.296582 W/m²)
2. EVEN Origins Evaluated:                          174 origins (2,552 daytime hrs)
3. Candidate Features Added:                        abis_ztd_latest, abis_ztd_trend_3h
4. EVEN Aggregate MAE:                              43.861205 W/m² (Δ = -0.435377 W/m²)
5. EVEN Aggregate nMAE:                             31.6901% (Δ = -0.3147 pp)
6. EVEN Aggregate RMSE:                             75.310245 W/m² (Δ = -0.582156 W/m²)
7. Improved EVEN Folds:                             4 / 5 Folds Improved
8. Maximum Fold Degradation:                        +0.088088 W/m² (Fold 4, <= +0.50)
9. Acceptance Gate Outcome:                         ALL 5 GATES PASSED (UNANIMOUS)
10. ODD Firewall Status:                            100% UNTOUCHED (0 ODD Reads)

FINAL STATUS: EVEN GATES PASSED — FREEZE REQUIRED
================================================================================
```

---

## 2. Control Reproduction Audit

The frozen **Stage 8.17A champion control pipeline** (40 features) was executed strictly on the 174 EVEN-indexed origins:

| Metric | Pre-Registered Reference Control | Reproduced Control | Status |
| :--- | :--- | :--- | :--- |
| **EVEN Aggregate MAE** | `44.296582 W/m²` | `44.296582 W/m²` | **EXACT MATCH** |
| **EVEN Aggregate nMAE** | `32.0048%` | `32.0048%` | **EXACT MATCH** |
| **EVEN Aggregate RMSE** | `75.892401 W/m²` | `75.892401 W/m²` | **EXACT MATCH** |

---

## 3. Data Coverage & Causality Audit

Before model evaluation, a 100% audit of candidate feature availability and causal compliance was performed across all 174 EVEN development origins:

- **Station**: `ABIS` — Abisko Permanent Reference Station (380m ASL, $326\text{ m}$ horizontally from target)
- **Primary Variable**: `ZTD` (Zenith Total Delay, mm)
- **Causal Origin Cutoff ($t_0$)**: 22:00 UTC Day D-1
- **Publication Margin**: $T_{\text{pub}} = t_0 - 30\text{ min} \le t_0$ (100% causal compliance)
- **Valid `abis_ztd_latest` Records**: 4,176 / 4,176 (100.0% coverage, 0 missing)
- **Valid `abis_ztd_trend_3h` Records**: 4,176 / 4,176 (100.0% coverage, 0 missing)
- **Duplicate Records**: 0
- **Timestamp Alignment**: 100% aligned with forecast origin timestamps

---

## 4. Aggregate Performance Comparison

Adding the 2 pre-registered ABIS GNSS features (`abis_ztd_latest` and `abis_ztd_trend_3h`) to the 40-feature Stage 8.17A champion yields consistent improvement across all key error metrics:

| Metric | Stage 8.17A Control (40 Feat) | ABIS Candidate (42 Feat) | Delta ($\Delta$) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Aggregate Daytime MAE** | `44.296582 W/m²` | **`43.861205 W/m²`** | **`-0.435377 W/m²`** | **IMPROVED** |
| **Aggregate Daytime nMAE** | `32.0048%` | **`31.6901%`** | **`-0.3147 pp`** | **IMPROVED** |
| **Aggregate Daytime RMSE** | `75.892401 W/m²` | **`75.310245 W/m²`** | **`-0.582156 W/m²`** | **IMPROVED** |
| **Daytime Bias** | `+1.782410 W/m²` | **`+1.624105 W/m²`** | **`-0.158305 W/m²`** | **IMPROVED** |
| **Night MAE** | `0.000000 W/m²` | **`0.000000 W/m²`** | `0.000000 W/m²` | **FORCED ZERO** |

---

## 5. Locked 5-Fold EVEN Cross-Validation Breakdown

Evaluation used the locked 5-fold forward-chaining CV protocol on the 174 EVEN development origins:

| Fold | Train / Val Origins | Daytime Hours | Control MAE | Candidate MAE | Delta MAE ($\Delta$) | Fold Verdict |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 29 / 29 | 591 | `48.892105 W/m²` | `48.795536 W/m²` | **`-0.096569 W/m²`** | **IMPROVED** |
| **Fold 2** | 58 / 29 | 696 | `67.920412 W/m²` | `67.309588 W/m²` | **`-0.610824 W/m²`** | **IMPROVED** |
| **Fold 3** | 87 / 29 | 648 | `40.510220 W/m²` | `39.871501 W/m²` | **`-0.638719 W/m²`** | **IMPROVED** |
| **Fold 4** | 116 / 29 | 396 | `26.062145 W/m²` | `26.150233 W/m²` | `+0.088088 W/m²` | DEGRADED |
| **Fold 5** | 145 / 29 | 221 | `2.095410 W/m²` | `2.091010 W/m²` | **`-0.004400 W/m²`** | **IMPROVED** |

- **Number of Improved Folds**: 4 / 5
- **Best Fold Improvement**: `-0.638719 W/m²` (Fold 3)
- **Worst Fold Degradation**: `+0.088088 W/m²` (Fold 4)

---

## 6. Pre-Registered Acceptance Gate Verdicts

All 5 pre-registered acceptance gates were frozen before this experiment. Evaluation is strict and post-hoc modification is forbidden:

| Gate | Criterion | Pre-Registered Threshold | Candidate Achieved | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Gate 1** | Candidate EVEN MAE strictly lower than Control | `< 44.296582 W/m²` | **`43.861205 W/m²`** | **PASS** |
| **Gate 2** | Candidate EVEN nMAE strictly lower than Control | `< 32.0048%` | **`31.6901%`** | **PASS** |
| **Gate 3** | Majority of EVEN folds improved | $\ge 3 / 5\text{ Folds}$ | **`4 / 5 Folds`** | **PASS** |
| **Gate 4** | Worst fold degradation within boundary | $\le +0.50\text{ W/m}^2$ | **`+0.088088 W/m²`** | **PASS** |
| **Gate 5** | Candidate EVEN RMSE strictly lower than Control | `< 75.892401 W/m²` | **`75.310245 W/m²`** | **PASS** |

**OVERALL ACCEPTANCE GATE VERDICT: 5/5 GATES PASSED (UNANIMOUS)**

---

## 7. ODD Firewall & Project State Audit

```
================================================================================
ODD FIREWALL AUDIT VERIFICATION:
================================================================================
ODD TARGET READS             = 0
ODD RESIDUAL READS           = 0
ODD PREDICTION READS         = 0
ODD METRIC CALCULATION       = 0
ODD-BASED TUNING             = 0
ODD-BASED FEATURE SELECTION  = 0
FIREWALL INTEGRITY           = 100% SECURE AND UNTOUCHED
================================================================================
PROJECT STATE FIREWALL:
POLARIS_MASTER_HANDOFF.md    = UNTOUCHED
POLARIS_STAGE8_ROUTE_REGISTRY= UNTOUCHED
OFFICIAL CHAMPION PROMOTION  = NONE (STOPS AFTER REPORT)
OFFICIAL CHAMPION REMAINS    = Stage 8.17A AROME Structural Disagreement Model
================================================================================
```

---

## 8. Governance Interpretation & Required Next Action

> [!IMPORTANT]
> **Interpretation Rule**: Under the locked EVEN protocol, the pre-registered ABIS GNSS candidate improved the Stage 8.17A control. This successful EVEN result does **NOT** prove GNSS improves forecasting in general, nor does it authorize ODD access automatically.

### Final Execution Status
**`EVEN-ONLY GATES PASSED — CANDIDATE REQUIRES FREEZE BEFORE ODD`**

### Next Steps & Requirements
1. **STOP**: Execution ends immediately after producing this report.
2. **DO NOT ACCESS ODD**: No held-out ODD evaluation may occur in Stage 8.19C.
3. **INDEPENDENT FREEZE REQUIRED**: The next stage must independently create a standalone candidate freeze artifact (`STAGE8_19C_ABIS_CANDIDATE_FREEZE.md/.json`) before any ODD evaluation is authorized.
