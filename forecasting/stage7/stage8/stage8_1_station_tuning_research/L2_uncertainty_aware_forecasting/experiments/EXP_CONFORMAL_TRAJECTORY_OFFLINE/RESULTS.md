# SUPERSEDING SCIENTIFIC STATUS: EXPERIMENT NOT QUALIFIED FOR STAGE 8.1

> [!CAUTION]
> **SUPERSEDING AUDIT NOTICE (2026-10-05):**
> - This document records the historical execution of `EXP-CONFORMAL-TRAJECTORY-OFFLINE`.
> - The original `CONFORMAL-TRAJECTORY-SUPPORTED` verdict is **SUPERSEDED**.
> - The experiment is **NOT qualified** as Stage 8.1 uncertainty calibration.
> - **2022** is a Candidate F calibration set, not independent validation.
> - **2023** is a Candidate F prior/reference evaluation; not a fresh blind calibration test.
> - **2025** uses corrected Stage 8.1 predictions and therefore has a different forecaster from the calibration data.
> - The observed **99.73%** 2025 coverage is **over-coverage under forecaster mismatch**, NOT evidence of Stage 8.1 calibration.
> - **No GAP19 or EMS integration is authorized from this experiment.**
> - The claims below ("CONFORMAL-TRAJECTORY-SUPPORTED", "Validation of Method C", "untouched 2025", "first mathematically defensible, distribution-free trajectory envelope", or any statement implying Stage 8.1 uncertainty was calibrated) are **SUPERSEDED HISTORICAL INTERPRETATIONS** preserved solely for provenance.

---

# POLARIS EXPERIMENTAL RESULTS: EXP-CONFORMAL-TRAJECTORY-OFFLINE (HISTORICAL ARTIFACT)
## Trajectory-Level Cumulative Solar-Energy Shortfall Validation on Blind 2025 Data

**Experiment ID:** `EXP-CONFORMAL-TRAJECTORY-OFFLINE`  
**Target Station:** Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Execution Timestamp:** `2026-10-05T02:39:48.484932+00:00`  
**Governance Status:** Research-Only Offline Statistical Validation (SUPERSEDED / NOT QUALIFIED FOR STAGE 8.1)  

---

## HISTORICAL EXPERIMENTAL VERDICT (SUPERSEDED)

```
+----------------------------------------------------------------------------------------------------+
|                               HISTORICAL RESEARCH VERDICT (SUPERSEDED)                             |
+----------------------------------------------------------------------------------------------------+
|                       CONFORMAL-TRAJECTORY-SUPPORTED [SUPERSEDED — SEE AUDIT]                       |
+----------------------------------------------------------------------------------------------------+
```

### Historical Decision Rationale (SUPERSEDED HISTORICAL INTERPRETATION):
Method C achieved 99.73% simultaneous coverage on untouched 2025 data at nominal 90% (threshold >= 87.0%), and 99.73% at nominal 95% (threshold >= 92.5%). Zero eligible regimes (n>=30) collapsed below 80% (worst regime: JJA at 98.91%). Envelope width ratio vs empirical benchmark is 1.78x (threshold <= 2.0x).
*(Note: 99.73% is over-coverage due to forecaster mismatch between 2022 Candidate F calibration and 2025 Stage 8.1 evaluation).*

---

## 1. Input Verification & Provenance Firewalls

| Input Dataset | Path | SHA-256 Hash | Split / Governance Purpose |
|---|---|---|---|
| Historical Residual Dataset | `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | `1337a56896ba1ea2...` | 2020-2021 (Train), 2022 (Calibration), 2023 (Prior Evidence) |
| 2025 Blind Predictions | `stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196b...` | 2025 Blind Target Irradiance & Point Forecasts |
| 2025 Corrected Features | `stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e2...` | 2025 Clear-sky, Solar Elevation & Cloud Cover Features |
| Pre-Registration MD | `PREREGISTRATION.md` | `90d1fe2f7f654ed1...` | Frozen Prior to Execution |
| Pre-Registration JSON | `PREREGISTRATION.json` | `6c085d8fb86254e9...` | Frozen Prior to Execution |

---

## 2. Conformal Calibration Results (Year 2022, N = 365 Origins)

Conformal calibration was executed over the 365 origins of calendar year 2022 across all 63 forward lookahead windows ($s \in [6..18], w \in [1..6]$ with $s+w-1 \le 18$).
- **Studentized Score Definition:** $r_i(s, w) = (C_i(s, w) - \hat{C}_{AR, i}(s, w)) / \max(S_{AR, i}(s, w), 1.0)$
- **Trajectory Nonconformity Score:** $R_i = \max_(18, 6) r_i(s, w)$
- **Calibrated Conformal Multipliers on 2022 ($N = 365$):**
  - **Nominal 90% ($\alpha = 0.10$):** Rank $k = \lceil 366 \times 0.90 \rceil = 330 \implies \hat{q}_{cal}(0.10) = 3.4674$
  - **Nominal 95% ($\alpha = 0.05$):** Rank $k = \lceil 366 \times 0.95 \rceil = 348 \implies \hat{q}_{cal}(0.05) = 3.7664$

*Scientific Significance:*  
Nominal Gaussian $z_{0.90} \approx 1.2816$. The empirical conformal multiplier required to achieve $90\%$ simultaneous trajectory coverage across all 63 multi-horizon windows is $\hat{q}_{cal} = 3.4674$ (approximately **2.71x** the Gaussian value). This directly reflects the heavy-tailed innovation kurtosis ($\kappa = 3.4452$) and multi-window joint extreme value dynamics.

---

## 3. Primary Multi-Year Coverage Comparison

Evaluated on all eligible origins across all years:
- **Marginal Coverage:** Evaluates each window length independently.
- **Simultaneous Trajectory Coverage:** An origin is covered only if **all 63 forward windows** satisfy the upper bound.

### Simultaneous Trajectory Coverage Summary (Nominal 90%, $\alpha = 0.10$)

| Year | Split Role | Origins ($N$) | Method A: AR Variance (Nominal $z=1.28$) | Method B: Empirical Quantile (2022) | Method C: Split-Conformal Trajectory | 95% Wilson CI (Method C) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **2020** | Train | 366 | 44.54% | 64.48% | 85.79% | [81.84%, 89.00%] |
| **2021** | Train | 365 | 41.37% | 59.73% | 88.22% | [84.51%, 91.14%] |
| **2022** | Calibration | 365 | 41.92% | 62.19% | 90.41% | [86.96%, 93.02%] |
| **2023** | Prior Evidence | 273 | 27.84% | 43.96% | 82.05% | [77.06%, 86.15%] |
| **2025** | **Primary Blind** | 364 | **58.79%** | **71.15%** | **99.73%** | **[98.46%, 99.95%]** |

---

## 4. Envelope Width & Conservatism Trade-Off (Wh)

| Method | Split Role (Year) | Mean Width (Wh) | Median Width (Wh) | 90th Pct Width (Wh) | 1-Hour Window Mean (Wh) | 6-Hour Window Mean (Wh) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Method A (AR Variance)** | 2025 Blind | 11688.6 | 7959.1 | 27458.6 | 3684.1 | 21285.2 |
| **Method B (Empirical Quantile)** | 2025 Blind | 18305.0 | 18045.1 | 30483.6 | 6679.7 | 31256.7 |
| **Method C (Split-Conformal)** | 2025 Blind | 32520.0 | 21967.7 | 75349.5 | 10246.6 | 59246.2 |

---

## 5. Primary Findings & Falsification Analysis (SUPERSEDED HISTORICAL INTERPRETATION)

> [!WARNING]
> **SUPERSEDED INTERPRETATION NOTICE:**
> The interpretations below represent the original historical conclusions. As established in `CORRECTION_AUDIT.md`:
> - Method C's 99.73% simultaneous coverage on 2025 does NOT represent calibrated performance for Stage 8.1; it reflects over-coverage under forecaster mismatch (2022 Candidate F calibration evaluated on 2025 Stage 8.1 predictions).
> - Statements claiming "Validation of Method C" or "untouched 2025" or "first mathematically defensible, distribution-free trajectory envelope" are superseded and invalid for Stage 8.1 operational deployment.
> - The textual ranges cited below for Method A (49.8% to 65.0%) and Method B (80.5% to 83.2%) were erroneous; actual ranges from `COVERAGE.csv` are Method A: 27.84%–58.79%, Method B: 43.96%–71.15%.

1. **Definitive Falsification of Method A (Nominal AR Variance):**  
   Across all historical and blind evaluation years, Method A's simultaneous trajectory coverage hovers between **27.84% and 58.79%** (stated historically as 49.8% to 65.0%), completely collapsing under multi-horizon joint testing. This experimentally falsifies the analytical Gaussian variance summation used in Candidate D V1/V2.
2. **Empirical Quantile Benchmark (Method B):**  
   Method B achieves **43.96% to 71.15%** simultaneous trajectory coverage (stated historically as 80.5% to 83.2%), but because empirical quantiles ignore origin-specific clear-sky irradiance and cloud states, it produces static buffers that under-protect high-irradiance summer days.
3. **Historical Claim for Method C (Trajectory Split-Conformal) [SUPERSEDED]:**  
   Method C achieved **99.73% simultaneous coverage** on 2025 blind evaluation data, exceeding the pre-registered threshold ($\ge 87.0\%$). However, this was achieved under forecaster mismatch (Candidate F calibration transferred to Stage 8.1). It does NOT establish calibration for Stage 8.1, and no operational or EMS integration is authorized.
