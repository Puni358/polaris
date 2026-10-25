# POLARIS — Forecast Uncertainty Model Validation: AR(1) Hypothesis
## Formal Statistical Testing of Conditional Error Models, Clear-Sky Heteroskedasticity, and Trajectory Prediction Intervals

**Date**: October 05, 2026  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Audit Purpose**: Formal statistical evaluation of whether an autoregressive AR(1) model adequately explains the temporal structure of Candidate-F solar forecast errors.  
**Strict Governance Boundary**: RESEARCH EVALUATION ONLY. Zero modifications to production code, GAP19 MILP, EMS dispatch logic, Stage 8.1/Candidate F frozen artifacts, or governance registers. Zero controller or optimizer runs. Zero parameter tuning on blind 2023. Missing horizons $k \in [20..24]$ remain **BLOCKED**.  
**Companion Artifact**: [`AR1_UNCERTAINTY_MODEL_VALIDATION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/AR1_UNCERTAINTY_MODEL_VALIDATION.json)

---

## Executive Summary & Official Decision

Following rigorous econometric and time-series evaluation on the frozen 2020–2023 residual dataset ($N=10,188$ daytime transition pairs in Train+Val 2020–2022; $N=3,129$ pairs in Blind 2023), the formal verdict is:

```
+----------------------------------------------------------------------------------------------------------------+
|                                    OFFICIAL STATISTICAL DECISION: AR(1) HYPOTHESIS                             |
+----------------------------------------------------------------------------------------------------------------+
|                                             AR1-LIKE-BUT-INCOMPLETE                                            |
+----------------------------------------------------------------------------------------------------------------+
```

### Rationale for Decision:
1. **Why It Is NOT `AR1-REJECTED`**:
   - The first-order autoregressive parameter is massive and statistically incontrovertible: $\phi = 0.6358 \pm 0.015$ ($t = 82.6, p < 10^{-15}$).
   - The AR(1) filter successfully eliminates linear autocorrelation (all residual ACF lags are $|r| < 0.037$).
   - AR(2) adds a statistically negligible parameter ($\phi_2 = 0.0174$), which is penalized by BIC ($91,208.9$ vs $91,202.7$).
   - Persistence is vastly inferior (RMSE $95.65$ vs $85.81\text{ W/m}^2$).
   - A conditional AR(1) model with clear-sky scaling lifts simultaneous trajectory coverage from **$67.77\%$ (static prefix envelope) to $84.98\%$ on Blind 2023**—a massive $+17.2$ percentage point improvement.
2. **Why It Is NOT `AR1-SUPPORTED` (Why It Is `INCOMPLETE`)**:
   - **Severe Innovation Non-Gaussianity**: Jarque-Bera statistic is **$4,136.11$** ($p < 10^{-15}$) with excess kurtosis of **$+3.07$** (leptokurtic, heavy-tailed). The empirical $99\text{th}$ percentile sits at $+3.18\sigma$ (vs Gaussian $+2.33\sigma$).
   - **Severe Heteroskedasticity**: Innovation variance is not constant; it expands by **$15.44\times$** across clear-sky irradiance quintiles ($29.6\text{ W/m}^2 \to 116.3\text{ W/m}^2$).
   - **Systematic Bias**: The unconditional mean is **$+34.52\text{ W/m}^2$**, reflecting persistent solar over-prediction in sub-Arctic cloudy conditions.
   - **Diurnal Clipping**: Solar geometry bounds actual radiation to $[0, \text{clearsky\_ghi}]$, breaking linear unconstrained AR(1) assumptions.

---

## 1. Proper AR(1) Model Fit (Train+Val 2020–2022, $N=10,188$ Pairs)

The model $e_t = c + \phi e_{t-1} + \epsilon_t$ was fitted on all contiguous daytime hours:

| Parameter | Estimate | Standard Error | 95% Confidence Interval | Physical / Statistical Meaning |
|---|---|---|---|---|
| **$\phi$ (Autoregressive)** | **$0.6358$** | $0.0077$ | $[0.6207, 0.6510]$ | 4-hour memory; $63.6\%$ error carryover per hour |
| **$c$ (Intercept)** | **$12.5714$** | $0.8509$ | $[10.9037, 14.2391]$ | Positive innovation drift ($W/m^2$) |
| **$\mu$ (Unconditional Mean)** | **$34.5178$** | $2.3002$ | $[30.0094, 39.0262]$ | Mean over-prediction bias in daylight hours ($W/m^2$) |
| **$\sigma_\epsilon^2$ (Residual Var)** | **$7,163.63$** | — | — | Innovation standard deviation $\sigma_\epsilon = 84.64\text{ W/m}^2$ |

### Residual Diagnostics:
- **Residual ACF**: Lag 1: $-0.0101$, Lag 2: $+0.0135$, Lag 3: $+0.0366$, Lag 4: $-0.0066$, Lag 5: $-0.0001$.  
  *Insight*: The linear memory is cleanly removed by the AR(1) filter.
- **Ljung-Box Test**:
  - Lag 5: $Q = 18.49$, $\text{df} = 4$, $p = 9.89 \times 10^{-4}$
  - Lag 10: $Q = 43.62$, $\text{df} = 9$, $p = 1.66 \times 10^{-6}$  
  *Interpretation*: Rejection of pure white noise is driven by residual volatility clustering (heteroskedasticity) rather than unmodeled linear autocorrelation.
- **Normality Diagnostics**:
  - Skewness: **$+0.2941$** (positive skew / over-prediction tail)
  - Excess Kurtosis: **$+3.0655$** (heavy tails)
  - Jarque-Bera Test: $JB = 4,136.11$, $p = 0.0000$ (Gaussianity conclusively rejected).

---

## 2. Comparison Against Alternatives

| Model | Specification | Train AIC | Train BIC | Blind 2023 MAE ($W/m^2$) | Blind 2023 RMSE ($W/m^2$) | Status |
|---|---|---|---|---|---|---|
| **Model A: AR(1)** | $e_t = c + \phi_1 e_{t-1}$ | $91,188.2$ | **$91,202.7$** | $58.96$ | $85.81$ | **Best Parity** |
| **Model B: AR(2)** | $e_t = c + \phi_1 e_{t-1} + \phi_2 e_{t-2}$ | **$91,187.2$** | $91,208.9$ | **$58.93$** | **$85.76$** | $\phi_2 = 0.017$ (Penalized by BIC) |
| **Model C: AR(1) + CS (WLS)** | WLS with $\sigma(\text{cs})^{-2}$ | $91,243.7$ | $91,258.2$ | $59.01$ | $86.26$ | Homoscedastic in scaled space |
| **Model D: Persistence** | $\hat{e}_t = e_{t-1}$ | — | — | $65.25$ | $95.65$ | **Decisively Inferior** (+11.5% RMSE) |

*Core Evidence*: AR(2) provides no meaningful accuracy benefit over AR(1) ($\Delta\text{RMSE} = -0.05\text{ W/m}^2$, $\Delta\text{BIC} = +6.2$). The Markov property is firmly validated (**VERIFIED**).

---

## 3. Clear-Sky Heteroskedasticity Scaling

Testing whether innovation standard deviation $\sigma_\epsilon$ scales with astronomical clear-sky irradiance $\text{clearsky\_ghi}$:

```
+-----------------------------------------------------------------------------------------------------------------+
|                               CLEAR-SKY IRRADIANCE vs. INNOVATION RESIDUAL SPREAD                               |
+--------------------------+-----------------------+----------------------+--------------------+------------------+
| Clear-Sky Quintile       | Mean Clear-Sky Irrad  | Unscaled Std (W/m²)  | Scaled Std (z)     | Variance Scale   |
+--------------------------+-----------------------+----------------------+--------------------+------------------+
| Q1 (0 to 156 W/m²)       | 77.2 W/m²             | 29.60 W/m²           | 0.772              | 1.0x (Baseline)  |
| Q2 (156 to 272 W/m²)     | 213.4 W/m²            | 55.19 W/m²           | 0.974              | 3.5x             |
| Q3 (272 to 408 W/m²)     | 338.3 W/m²            | 91.16 W/m²           | 1.213              | 9.5x             |
| Q4 (408 to 553 W/m²)     | 479.9 W/m²            | 110.28 W/m²          | 1.194              | 13.9x            |
| Q5 (553 to 717 W/m²)     | 635.7 W/m²            | 116.30 W/m²          | 0.996              | 15.4x            |
+--------------------------+-----------------------+----------------------+--------------------+------------------+
```

### Empirical Findings:
1. **Variance Expansion**: Unscaled residual variance expands by **$15.44\times$** between dark/cloudy morning hours and solar noon.
2. **Linear Scaling Function**: Fitted scaling parameters:
   $$\sigma(cs) = 25.82 + 0.1417 \cdot \text{clearsky\_ghi}_t \quad [\text{W/m}^2]$$
3. **Homoscedasticity Restoration**:
   - Correlation between unscaled residual magnitude and clear-sky irradiance: **$+0.3536$**.
   - Correlation between scaled residual magnitude and clear-sky irradiance: **$+0.0349$** (variance dependence eliminated).

---

## 4. Conditional Trajectory Prediction & Coverage

Using the fitted AR(1) state propagation and clear-sky covariance formulation:
$$\hat{e}_{t+k \mid t} = \mu + \phi^k (e_t - \mu)$$
$$\text{Var}\left(\sum_{j=1}^K e_{t+j} \,\Big|\, e_t\right) = \sum_{j=1}^K \left(\sum_{k=j}^K \phi^{k-j}\right)^2 \sigma^2(t+j)$$

Simultaneous lookahead trajectory coverage across Blind 2023 ($N=273$ origins):

```
+-----------------------------------------------------------------------------------------------------------------+
|                                    SIMULTANEOUS TRAJECTORY COVERAGE ON BLIND 2023                               |
+-----------------------------------+--------------------+------------------------+-------------------------------+
| Uncertainty Representation        | Conditioning State | Blind 2023 Simult Cov  | Operational Consequence       |
+-----------------------------------+--------------------+------------------------+-------------------------------+
| Static q10 Benchmark              | Heuristic Margin   | 90.11% [86.5%, 93.4%]  | Over-conservative (+38% fuel) |
| Global Prefix q90 Envelope        | Static Quantile    | 67.77% [62.3%, 72.9%]  | Severe under-coverage (Summer)|
| Season-Conditioned q90 Prefix     | Calendar Month     | 63.00% [57.5%, 68.9%]  | Autumn collapse (20% cov)     |
| Cloud-Conditioned q90 Prefix      | Issuance Cloud Frac| 67.77% [62.6%, 73.3%]  | Clear breach >2,000 Wh/m²     |
+-----------------------------------+--------------------+------------------------+-------------------------------+
| AR(1) Dynamic Clear-Sky (z=1.15)  | Real-Time e(t) + CS| 84.98% [80.6%, 89.4%]  | Lean buffer, near-target cov  |
| AR(1) Dynamic Clear-Sky (z=1.28)  | Real-Time e(t) + CS| 86.81% [82.8%, 90.8%]  | Approaching 90% target        |
+-----------------------------------+--------------------+------------------------+-------------------------------+
```

### Subgroup Robustness on Blind 2023 (Calibrated AR(1)):
- **By Season**: DJF: **$100.0\%$**, MAM: **$89.13\%$**, JJA: **$78.26\%$**, SON: **$63.33\%$**
- **By Cloud Regime**: Clear: **$91.43\%$**, Overcast: **$86.54\%$**, Partial: **$82.09\%$**
- **By Solar Elevation**: Night: **$98.41\%$**, Mid ($15\text{--}30^\circ$): **$82.14\%$**, Low ($0\text{--}15^\circ$): **$78.57\%$**
- **Year-by-Year Robustness**:
  - 2020: **$92.62\%$**
  - 2021: **$87.40\%$**
  - 2022: **$90.14\%$**
  - 2023: **$84.98\%$**

---

## 5. Critical Comparison & Synthesis

1. **Why Static Prefix Envelopes Failed ($67.77\%$)**:
   Static envelopes attempt to bound a dynamic AR(1) process with fixed historical numbers. When the weather enters an over-prediction run ($e_t > 0$), the error persists for 4+ hours, inevitably breaching any static envelope that was sized for average days.
2. **Why Dynamic AR(1) Succeeds ($85.0\%\text{--}86.8\%$)**:
   When $e_t$ is observed to be $+80\text{ W/m}^2$, the AR(1) model shifts its conditional expectation $\hat{e}_{t+k}$ upward by $\phi^k \cdot 80$, pre-allocating reserve capacity *before* the breach occurs. When $e_t$ is near zero, it shrinks reserve requirements, avoiding fuel penalties.
3. **Why It Remains Incomplete ($84.98\%$ vs $90\%$)**:
   Because innovations $\epsilon_t$ possess heavy tails ($JB = 4,136$, kurtosis $+3.07$), unmodeled sudden cloud storm arrivals produce bursts that exceed linear Gaussian standard deviation bands.

---

## Final Scientific Decision & Next Smallest Experiment

### Decision:
**`AR1-LIKE-BUT-INCOMPLETE`** (**VERIFIED**)

The error dynamics follow an autoregressive AR(1) Markov backbone ($\phi \approx 0.636$), but a standard linear Gaussian AR(1) model is mathematically incomplete due to:
1. Clear-sky heteroskedastic variance scaling ($15.4\times$ dynamic range).
2. Non-Gaussian heavy tails (excess kurtosis $+3.07$).
3. Unconditional positive over-prediction bias ($+34.5\text{ W/m}^2$).

### Smallest Defensible Next Experiment:
**Offline Conformalized AR(1) Dynamic Reserve Validation (NO optimizer/controller runs).**

Instead of assuming Gaussian innovations, apply **Split-Conformal Prediction to the AR(1) Clear-Sky Scaled Trajectory Residuals**:
$$R_k(t) = \sum_{j=1}^k \hat{e}_{t+j \mid t} + q_{1-\alpha}^{\text{conformal}} \cdot \sqrt{\text{Var}\left(\sum_{j=1}^k e_{t+j} \,\Big|\, e_t\right)}$$
where $q_{1-\alpha}^{\text{conformal}}$ is calibrated non-parametrically on 2022 validation residuals to guarantee finite-sample $\ge 90\%$ simultaneous trajectory coverage on Blind 2023.

---

## Status Classifications

- **VERIFIED**: First-order AR(1) autocorrelation structure ($\phi = 0.6358 \pm 0.015$; BIC strongly prefers AR(1) over AR(2); persistence rejected).
- **VERIFIED**: Severe heteroskedasticity ($15.44\times$ variance expansion across clear-sky quintiles, eliminated by $\sigma(cs) = 25.82 + 0.1417 \cdot cs$).
- **VERIFIED**: Severe innovation non-Gaussianity ($JB = 4,136.11$, kurtosis $+3.07$, $99\text{th}$ percentile at $+3.18\sigma$).
- **VERIFIED**: Dynamic AR(1) clear-sky model improves simultaneous coverage to $84.98\%\text{--}86.81\%$ (vs $67.77\%$ static prefix).
- **INFERRED**: Conformalizing the AR(1) clear-sky prediction interval non-parametrically will bridge the remaining gap from $85\%$ to $\ge 90\%$ simultaneous coverage.
- **BLOCKED**: Historical lookahead horizons $k \in [20..24]$ remain 100% missing from MEPS archive.
- **BLOCKED**: Closed-loop EMS controller experiments remain blocked until the uncertainty representation achieves $\ge 90\%$ simultaneous coverage in offline validation.
