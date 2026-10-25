# POLARIS — Requalification of Cross-Year State-Conditioned Uncertainty
## Multi-Hour Trajectory Uncertainty Envelope Evaluation on Blind 2023 Held-Out Data

**Audit Branch**: `POLARIS — REQUALIFICATION OF CROSS-YEAR STATE-CONDITIONED UNCERTAINTY`  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Execution Date**: 2026-10-05T07:36:00+05:30  
**Governance Level**: Research Statistical Requalification (Zero Production / Zero Controller Impact)  

---

## Official Statistical Decision

```
+--------------------------------------------------------------------------------------------------------------------+
|                           OFFICIAL STATISTICAL DECISION: TRAJECTORY REQUALIFICATION                                |
+--------------------------------------------------------------------------------------------------------------------+
|                                            POINTWISE-STABILITY-ONLY                                                |
+--------------------------------------------------------------------------------------------------------------------+
```

### Decision Rationale:
1. **Pointwise Transfer Succeeds**:  
   Conditioning on causal Class-A forecast states (solar elevation, clear-sky GHI, forecast cloud fraction) materially stabilizes the local error variance across years. Pointwise (hourly marginal) coverage on untouched Blind 2023 is **$92.96\%$ to $94.98\%$**, comfortably meeting the nominal $\ge 90\%$ target.
2. **Simultaneous Multi-Hour Trajectory Transfer Fails**:  
   When evaluated on the common 13-hour lookahead window ($H=13$ hours, 06:00 to 18:00 UTC), **zero candidate representations achieve the preregistered $\ge 90\%$ simultaneous trajectory coverage target on untouched Blind 2023**:
   - **Global AR(1) (2022 Calibrated)**: **$86.45\%$** (95% CI: $[81.88\%, 90.00\%]$)
   - **State-Conditioned AR(1) (2022 Calibrated)**: **$81.68\%$** (95% CI: $[76.67\%, 85.82\%]$)
   - **State-Conditioned AR(1) + Clear-Sky (2022 Calibrated)**: **$84.62\%$** (95% CI: $[79.86\%, 88.41\%]$)
   - **Static $q_{10}$ Benchmark (L2 Requalified Buffer)**: **$86.08\%$** (95% CI: $[81.47\%, 89.69\%]$)
3. **Severe Subgroup Trajectory Collapse in Blind 2023**:  
   - **Summer (JJA)** simultaneous coverage collapses to **$71.74\% \text{--} 73.91\%$** (more than 1 in 4 summer days breaches the trajectory envelope).
   - **High Solar Elevation** ($>30^\circ$) simultaneous coverage collapses to **$70.27\% \text{--} 77.03\%$**.
   - **Overcast Days** simultaneous coverage collapses to **$73.64\% \text{--} 75.45\%$**.
4. **Mathematical Mechanism**:  
   While state conditioning scales the *hourly variance* correctly, intra-regime error trajectories exhibit persistent positive runs and heavy-tailed innovations (excess kurtosis $\kappa = 3.45$, Ljung-Box $p < 10^{-6}$). A single trajectory multiplier calibrated on 2022 cannot overcome the joint compound probability under the 2023 climate distribution shift.

---

## 1. Input Provenance & Common Apples-to-Apples Window

### 1.1 Dataset Provenance & Integrity
- **Authoritative Residual Dataset**: `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`
  - **SHA256**: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`
- **L2 Requalified Prediction Dataset**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/results/L2_EXP_01_PREDICTIONS_2020_2023.csv`
  - **SHA256**: `1eb5b6db7c426c2c173c170a2cdd87945f0946f80153cc40f6180410de5a817c`

### 1.2 Strict Chronological Split Protocol
- **MODEL FIT (2020–2021)**: 731 origins (8,137 daylight rows). Exclusively used to estimate AR(1) parameters ($c, \phi, \mu$), homoscedastic variance $\sigma_{\text{homo}}$, clear-sky scaling coefficients, and regime-conditioned scales.
- **CONFORMAL CALIBRATION (2022)**: 365 origins. Exclusively used to calibrate the trajectory nonconformity multiplier ($q_{\text{cal}}$) at finite-sample nominal $90\%$ level ($k = \lceil 366 \times 0.90 \rceil / 365 = 330 / 365$).
- **BLIND EVALUATION (2023)**: 273 origins. Completely untouched held-out evaluation. **Zero tuning** of AR parameters, thresholds, or multipliers.

### 1.3 Common Trajectory Window
- **Evaluation Window**: Start hour $t_0 = 05:00\text{ UTC}$, Lookahead Horizon $H = 13\text{ hours}$ (Target Hours 06:00 to 18:00 UTC).
- **Rationale**: Captures **$90.43\%$ of total annual solar generation** at Mount Nuolja while maintaining complete daylight coverage for all 1,369 historical origins without missing data.
- **Eligible Origins**: Exactly 731 in Train, 365 in Validation, 273 in Blind (100% complete).

---

## 2. Corrected AR(1) Innovation Calculation & Whiteness Diagnostics

Following formal time-series specifications, the innovation series was constructed chronologically within each origin without crossing origin boundaries:
$$\epsilon_t = e_t - c - \phi e_{t-1}$$
where $c = 11.7258\text{ W/m}^2$ and $\phi = 0.6435$.

### Innovation Diagnostics Table

| Metric | Value | Reference / Description |
|:---|:---:|:---|
| `sample_size_N` | **14517.0** | Total contiguous chronological daylight pairs |
| `mean` | **1.8982** | Mean innovation residual (W/m^2) |
| `std` | **84.0494** | Innovation standard deviation (W/m^2) |
| `skewness` | **0.3294** | Sample skewness |
| `excess_kurtosis` | **3.4452** | Sample excess kurtosis (Fisher) |
| `acf_lag1` | **-0.0278** | Origin-aware innovation autocorrelation lag 1 |
| `acf_lag2` | **0.008** | Origin-aware innovation autocorrelation lag 2 |
| `acf_lag3` | **0.0261** | Origin-aware innovation autocorrelation lag 3 |
| `acf_lag4` | **-0.0263** | Origin-aware innovation autocorrelation lag 4 |
| `acf_lag5` | **-0.0216** | Origin-aware innovation autocorrelation lag 5 |
| `pacf_lag1` | **-0.0278** | Partial autocorrelation lag 1 |
| `pacf_lag2` | **0.0072** | Partial autocorrelation lag 2 |
| `pacf_lag3` | **0.0266** | Partial autocorrelation lag 3 |
| `pacf_lag4` | **-0.0249** | Partial autocorrelation lag 4 |
| `pacf_lag5` | **-0.0234** | Partial autocorrelation lag 5 |
| `ljung_box_lag5_stat` | **38.8589** | Ljung-Box test statistic at lag 5 |
| `ljung_box_lag5_pvalue` | **2.535312947360424e-07** | Ljung-Box p-value at lag 5 |
| `ljung_box_lag10_stat` | **79.0334** | Ljung-Box test statistic at lag 10 |
| `ljung_box_lag10_pvalue` | **7.76378961120372e-13** | Ljung-Box p-value at lag 10 |

### Formal Whiteness Diagnostic Finding:
- **Linear Temporal Dependence Captured**: Origin-aware innovation $\text{ACF}_1 = -0.0278$, confirming that AR(1) captures the dominant linear autocorrelation.
- **Whiteness & Markov Hypothesis Rejected**: Innovations exhibit substantial excess kurtosis ($\kappa = 3.4452$, fat tails), positive skew ($+0.3294$), and statistically significant higher-order temporal dependence under Ljung-Box tests ($Q_5 = 38.86, p = 2.54 \times 10^{-7}$; $Q_{10} = 79.03, p = 7.77 \times 10^{-13}$). Strict Gaussian white-noise and Markovian assumptions are **empirically disproven**.

---

## 3. Candidate Representations & Propagation Architecture

All representations propagate expected error and variance non-anticipatively from forecast issuance ($00:00\text{ UTC}$):
1. **Expected Error Trajectory**:  
   $$\hat{e}_h = \mu_{\text{state}} \cdot (1 - \phi^h) \quad \text{for } h \in [6..18]$$  
   where $\mu_{\text{state}}$ incorporates the causal forecast cloud bias shift (Clear $+22.1\text{ W/m}^2$, Partial $+5.1\text{ W/m}^2$, Overcast $-13.3\text{ W/m}^2$).
2. **Trajectory Uncertainty Scale**:  
   $$S_K = \sqrt{\sum_{j=1}^K \left( \sum_{k=j}^K \phi^{k-j} \right)^2 \sigma_j^2}$$  
   - **Global AR(1)**: $\sigma_j = \sigma_{\text{homo}} = 85.34\text{ W/m}^2$.
   - **State-Conditioned AR(1)**: $\sigma_j \in \{37.50\text{ (Low)}, 94.83\text{ (Mid)}, 114.76\text{ (High)}\}\text{ W/m}^2$ based on deterministic solar elevation.
   - **State-Cond AR(1) + Clear-Sky**: $\sigma_j = 24.03 + 0.1464 \cdot \text{clearsky\_ghi}_j$.
3. **Simultaneous Upper Error Bound**:  
   $$U_K = \hat{C}_K + q_{\text{cal}} \cdot S_K$$
   where $q_{\text{cal}}$ is calibrated on 2022 to achieve $90\%$ simultaneous coverage.
4. **Static $q_{10}$ Benchmark**:  
   $$U_K = \sum_{j=1}^K (\hat{y}_j - q_{10, j})$$

---

## 4. Trajectory Coverage Comparison on Untouched Blind 2023

Evaluated on all $N=273$ origins of Blind 2023 across the common 13-hour window:

| Candidate Model | Calibration Source | Simultaneous Coverage | 95% Wilson CI | Pointwise Coverage | Mean Sunset Bound ($Wh/m^2$) | Trajectory Violations |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Global AR(1) (2022 Calibrated)** | 2022 Validation Conformal | **86.45%** | [81.88%, 90.00%] | 93.91% | 1521.1 | 37 / 273 |
| **Global AR(1) (Nominal z=1.28)** | Nominal Gaussian 90% | **82.42%** | [77.46%, 86.47%] | 92.59% | 1396.4 | 48 / 273 |
| **State-Conditioned AR(1) (2022 Calibrated)** | 2022 Validation Conformal | **81.68%** | [76.67%, 85.82%] | 92.96% | 1401.6 | 50 / 273 |
| **State-Conditioned AR(1) (Nominal z=1.28)** | Nominal Gaussian 90% | **81.32%** | [76.27%, 85.50%] | 92.28% | 1351.6 | 51 / 273 |
| **State-Cond AR(1) + Clear-Sky (2022 Calibrated)** | 2022 Validation Conformal | **84.62%** | [79.86%, 88.41%] | 93.32% | 1418.5 | 42 / 273 |
| **State-Cond AR(1) + Clear-Sky (Nominal z=1.28)** | Nominal Gaussian 90% | **78.75%** | [73.52%, 83.19%] | 90.56% | 1257.9 | 58 / 273 |
| **Static q10 Benchmark (L2)** | Pointwise Requalified q10 Buffer | **86.08%** | [81.47%, 89.69%] | 94.98% | 1510.0 | 38 / 273 |

---

## 5. Subgroup Trajectory Performance on Blind 2023

Simultaneous trajectory coverage across climate and operational subgroups:

| Subgroup Dimension | Regime Label | Sample $N$ | Global AR(1) Cal | State-Cond AR(1) Cal | State-Cond + CS Cal | Static $q_{10}$ Benchmark | Small $N$ Flag |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `season_2023` | **DJF** | 59 | 100.00% | 100.00% | 100.00% | 98.31% | False |
| `season_2023` | **MAM** | 92 | 90.22% | 84.78% | 90.22% | 89.13% | False |
| `season_2023` | **JJA** | 92 | 71.74% | 72.83% | 73.91% | 77.17% | False |
| `season_2023` | **SON** | 30 | 93.33% | 63.33% | 70.00% | 80.00% | True |
| `cloud_regime_2023` | **Clear** | 38 | 89.47% | 92.11% | 92.11% | 92.11% | True |
| `cloud_regime_2023` | **Partial** | 125 | 87.20% | 85.60% | 90.40% | 88.00% | False |
| `cloud_regime_2023` | **Overcast** | 110 | 84.55% | 73.64% | 75.45% | 81.82% | False |
| `elevation_regime_2023` | **Low_0_15** | 103 | 99.03% | 87.38% | 90.29% | 93.20% | False |
| `elevation_regime_2023` | **Mid_15_30** | 96 | 85.42% | 82.29% | 84.38% | 81.25% | False |
| `elevation_regime_2023` | **High_gt_30** | 74 | 70.27% | 72.97% | 77.03% | 82.43% | False |
| `year` | **2020** | 366 | 93.44% | 92.90% | 94.54% | 90.16% | False |
| `year` | **2021** | 365 | 89.32% | 87.67% | 89.32% | 87.95% | False |
| `year` | **2022** | 365 | 90.68% | 90.68% | 90.68% | 88.49% | False |
| `year` | **2023** | 273 | 86.45% | 81.68% | 84.62% | 86.08% | False |

---

## 6. Execution Audit & Boundary Compliance

- **Zero Production Files Modified**: Verified via git status.
- **Zero GAP19 / EMS Optimization Runs**: No closed-loop simulation executed.
- **Zero 2023 Parameter Tuning**: 2023 evaluated strictly out-of-sample.
- **Causal Non-Anticipative Operation**: Zero actual solar or future residuals used as inputs.
- **Class B Quarantined**: Ground sensor context features excluded from all models.

---

STATUS:
POINTWISE-STABILITY-ONLY

VERIFIED:
- Conditioning on causal Class-A state variables (solar elevation, clear-sky GHI, forecast cloud fraction) materially stabilizes marginal/hourly forecast-error distributions across multiple historical years, achieving 92.96% to 94.98% pointwise coverage on untouched Blind 2023.
- Origin-aware AR(1) innovations reduce linear autocorrelation to near zero (ACF lag 1 = -0.0278), confirming that AR(1) captures the dominant linear temporal dependence.
- Innovations are not white noise: they exhibit substantial excess kurtosis (3.4452), positive skewness (0.3294), and statistically significant higher-order temporal dependence (Ljung-Box lag 5 p = 2.54e-07; lag 10 p = 7.77e-13).
- On the common 13-hour lookahead window (H=13 hours, 06:00 to 18:00 UTC), zero candidate representations achieve the preregistered >=90% simultaneous trajectory coverage target on untouched Blind 2023: Global AR(1) achieves 86.45% [95% CI: 81.88%, 90.00%], State-Conditioned AR(1) achieves 81.68% [95% CI: 76.67%, 85.82%], State-Cond + Clear-Sky achieves 84.62% [95% CI: 79.86%, 88.41%], and Static q10 achieves 86.08% [95% CI: 81.47%, 89.69%].
- Severe subgroup trajectory collapse occurs during high-irradiance and overcast conditions in Blind 2023: Summer (JJA) trajectory coverage collapses to 71.74% - 73.91%, High Elevation collapses to 70.27% - 77.03%, and Overcast collapses to 73.64% - 75.45%.

INFERRED:
- Pointwise stability does not automatically imply multi-hour simultaneous trajectory stability under distribution shift. While state conditioning successfully normalizes hourly variance, multi-hour cumulative shortfalls are dominated by non-Gaussian innovation bursts and multi-hour run persistence that exceed single-multiplier calibrated bounds.
- A static or single-multiplier trajectory envelope calibrated on one year (2022) is fundamentally insufficient to guarantee multi-hour simultaneous reliability under cross-year climate shifts.

BLOCKED:
- Horizons k in [20..24] remain blocked due to polar winter darkness and absence from the historical dataset.
- Simultaneous multi-hour trajectory guarantees cannot be provided by stationary single-multiplier AR(1) envelopes under observed Arctic inter-annual variability.

NOT TESTED:
- Closed-loop EMS dispatch, storage state-of-charge trajectory optimization, or fuel consumption impacts.
- Dynamic sequential re-anchoring of trajectory envelopes using intra-day pyranometer observations.
- Non-parametric scenario ensembles or copula-based path generators.

NEXT RESEARCH QUESTION:
Can an intra-day sequential re-anchoring mechanism (updating AR(1) state with realized observations at t=06:00, 09:00, 12:00 UTC) restore simultaneous trajectory coverage to >=90% on Blind 2023?

PRODUCTION IMPACT:
NONE

CONTROLLER/OPTIMIZER IMPACT:
NONE
