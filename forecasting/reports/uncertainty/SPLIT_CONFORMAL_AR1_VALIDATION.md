# POLARIS — Split-Conformal AR(1) Trajectory Validation Audit
## Empirical Transfer Testing of Trajectory-Level Conformal Prediction on Blind 2023 Held-Out Data

**Date**: October 05, 2026  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Audit Purpose**: Formal empirical test of whether a trajectory-level split-conformal AR(1) model calibrated on 2022 validation data can achieve the preregistered $\ge 90\%$ empirical simultaneous-coverage target on the untouched 2023 blind evaluation.  
**Strict Governance Boundary**: RESEARCH EVALUATION ONLY. Zero modifications to production code, GAP19 MILP, EMS dispatch logic, Stage 8.1/Candidate F frozen artifacts, or governance registers. Zero controller or optimizer runs. Zero parameter tuning on blind 2023. Missing horizons $k \in [20..24]$ remain **BLOCKED**.  
**Companion Artifact**: [`SPLIT_CONFORMAL_AR1_VALIDATION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/SPLIT_CONFORMAL_AR1_VALIDATION.json)

---

## Official Statistical Decision

```
+----------------------------------------------------------------------------------------------------------------+
|                                  OFFICIAL STATISTICAL DECISION: SPLIT-CONFORMAL AR(1)                          |
+----------------------------------------------------------------------------------------------------------------+
|                                                    CONFORMAL-FAILS                                             |
+----------------------------------------------------------------------------------------------------------------+
```

### Rationale for Decision:
1. **Failure of the Simultaneous Coverage Threshold**:
   On the untouched Blind 2023 dataset, simultaneous trajectory coverage of the split-conformal AR(1) envelope is **$84.62\%$** ($95\%$ CI: $[79.85\%, 88.64\%]$), strictly **below the preregistered $\ge 90\%$ empirical simultaneous-coverage target**.
2. **Severe Subgroup Trajectory Collapse**:
   - **Summer (JJA)** simultaneous coverage collapses to **$75.00\%$** (1 in 4 summer days breaches the trajectory bound).
   - **Autumn (SON)** simultaneous coverage collapses to **$73.33\%$**.
   - **Mid-Elevation daylight periods** suffer an under-coverage rate of **$23.08\%$** ($76.92\%$ coverage).
3. **Forensic Mechanism (Observed Distribution Shift & Exchangeability Interpretation)**:
   - **VERIFIED**: A material distribution shift in trajectory/nonconformity behavior between the 2022 calibration year and 2023 blind year is observed ($C_{19}$ mean shifted from $+318.3\text{ Wh/m}^2$ in 2022 to $+531.8\text{ Wh/m}^2$ in 2023, reflecting $+67\%$ higher cumulative shortfall volatility). Consequently, the $90\%$ quantile of nonconformity scores calibrated on 2022 ($q_{\text{conf}} = 1.3331$) achieved $84.62\%$ simultaneous coverage on 2023.
   - **INFERRED**: The observed 2022→2023 distribution shift means the exchangeability assumption required for the standard split-conformal finite-sample coverage guarantee cannot be assumed for this calibration-to-blind transfer. Calibration on 2022 does NOT guarantee $90\%$ coverage under distribution shift in 2023.

---

## 1. Experimental Setup & Common Apples-to-Apples Window

To ensure strict scientific integrity, all candidate representations were evaluated on the **exact same origins, start hour, and lookahead horizon**:

- **Lookahead Window**: Start hour $t_0 = 05:00\text{ UTC}$, Horizon $H = 13\text{ hours}$ (Target Hours 06:00 to 18:00 UTC).
  - *Rationale*: Captures **$90.43\%$ of total annual solar generation** at Mount Nuolja while maintaining contiguous daylight coverage for all 1,369 historical origins.
- **Data Partition**:
  - **2020–2021 Train ($N=731$ origins)**: AR(1) model fitting and clear-sky scaling estimation ONLY.
  - **2022 Validation ($N=365$ origins)**: Split-conformal nonconformity calibration ONLY.
  - **2023 Blind Test ($N=273$ origins)**: Untouched held-out out-of-distribution evaluation.

---

## 2. AR(1) Model & Clear-Sky Scaling (Fitted on 2020–2021 Train Only)

Fitted strictly on the 731 origins of 2020–2021:
- Autoregressive Parameter: $\phi = 0.6435$ ($se = 0.0094$)
- Innovation Drift Intercept: $c = 11.7258\text{ W/m}^2$
- Unconditional Daylight Mean: $\mu = 32.8918\text{ W/m}^2$
- Homoscedastic Innovation Spread: $\sigma_{\text{homo}} = 85.34\text{ W/m}^2$
- Clear-Sky Scaling Function: $\sigma(cs) = 24.03 + 0.1464 \cdot \text{clearsky\_ghi}_t\text{ [W/m}^2]$

---

## 3. Trajectory-Level Conformal Calibration on 2022 ($N=365$ Origins)

### 3.1 Nonconformity Score Construction
For each calibration origin $i$ in 2022, the cumulative predicted trajectory $\hat{C}_i[k]$ and clear-sky uncertainty scale $S_i[k]$ were computed over $k=1..13$:
$$\hat{C}_i[k] = \sum_{j=1}^k \left( \mu + \phi^j (e_{i, t_0} - \mu) \right)$$
$$S_i[k] = \sqrt{ \sum_{j=1}^k \left( \sum_{m=j}^k \phi^{m-j} \right)^2 \left( 24.03 + 0.1464 \cdot \text{clearsky\_ghi}_{i, t_0 + j} \right)^2 }$$

The single origin-level simultaneous nonconformity score was defined as:
$$\text{score}_i = \max_{k \in [1..13]} \frac{C_{\text{actual}, i}[k] - \hat{C}_i[k]}{S_i[k]}$$

### 3.2 2022 Score Distribution & Quantile Selection
- **Score Distribution on 2022**: Minimum: $-0.94$, 25th pct: $-0.55$, Median: $-0.18$, 75th pct: $+0.65$, 90th pct: $+1.28$, 95th pct: $+1.56$, Maximum: $+2.94$.
- **Conformal Finite-Sample Quantile Index**: $\lceil (365 + 1) \times (1 - 0.10) \rceil / 365 = 330 / 365 = 0.9041$.
- **Calibrated Multiplier ($q_{\text{conf}}$)**: **$1.3331$**
- **Empirical 2022 Calibration Coverage**: **$90.68\%$** (331 / 365 origins covered simultaneously).

---

## 4. Apples-to-Apples Blind 2023 Evaluation ($N=273$ Origins)

All five candidate representations evaluated on the exact same lookahead window ($t_0=05:00\text{ UTC}, H=13\text{ h}$):

```
+--------------------------------------------------------------------------------------------------------------------+
|                                    APPLES-TO-APPLES BLIND 2023 TRAJECTORY EVALUATION                               |
+------------------------------------+--------------------+------------------------+---------------------------------+
| Representation                     | Calibration Source | Blind 2023 Simult Cov  | Mean Sunset Bound (Wh/m²)       |
+------------------------------------+--------------------+------------------------+---------------------------------+
| Static q10 Benchmark               | Pointwise Heuristic| 86.08% [81.7%, 90.1%]  | 1,510.0 Wh/m² (Severe buffer)   |
| Global Prefix q90                  | 2020-22 Empirical  | 73.99% [68.9%, 79.1%]  | 1,116.6 Wh/m² (Heavy breach)    |
| Arm A: Gaussian AR(1) Homo (z=1.28)| 2020-21 Normality  | 85.71% [81.3%, 89.7%]  | 1,374.3 Wh/m²                   |
| Arm B: Gaussian AR(1) CS (z=1.28)  | 2020-21 Clear-Sky  | 83.52% [79.1%, 87.5%]  | 1,256.4 Wh/m²                   |
| Arm C: Split-Conformal AR(1)       | 2022 Trajectory Cal| 84.62% [79.8%, 88.6%]  | 1,290.9 Wh/m²                   |
+------------------------------------+--------------------+------------------------+---------------------------------+
```

### Detailed Observations:
1. **Arm C vs. Static $q_{10}$**:
   - Split-conformal AR(1) reduces the sunset reserve bound from $1,510.0\text{ Wh/m}^2$ down to **$1,290.9\text{ Wh/m}^2$** (a **$-14.5\%$ reduction in reserve conservatism**).
   - However, because the buffer is leaner, simultaneous coverage drops from $86.08\%$ to **$84.62\%$**, failing the $90\%$ target.
2. **Arm C vs. Global Prefix $q_{90}$**:
   - Conditioning dynamically on real-time error $e_{t_0}$ via AR(1) lifts simultaneous coverage by **$+10.63$ percentage points** ($73.99\% \to 84.62\%$).
   - Nevertheless, transferring the static scalar $q_{\text{conf}} = 1.3331$ from 2022 to 2023 achieves $84.62\%$, remaining below the $90\%$ target on the blind evaluation.

---

## 5. Subgroup Trajectory Coverage on Blind 2023 (Arm C)

Evaluating Arm C ($q_{\text{conf}} = 1.3331$) across operational subgroups reveals severe seasonal and meteorological vulnerabilities:

| Subgroup Dimension | Category | Origin Count ($N$) | Simultaneous Coverage | Status |
|---|---|---|---|---|
| **Season** | **Winter (DJF)** | 59 | **$100.00\%$** (59 / 59) | Over-buffered |
| | **Spring (MAM)** | 92 | **$88.04\%$** (81 / 92) | Near target |
| | **Summer (JJA)** | 92 | **$75.00\%$** (69 / 92) | **SEVERE COLLAPSE** (1 in 4 fails) |
| | **Autumn (SON)** | 30 | **$73.33\%$** (22 / 30) | **SEVERE COLLAPSE** |
| **Cloud Regime** | **Clear ($<0.20$)** | 35 | $88.57\%$ (31 / 35) | Near target |
| | **Overcast ($>0.80$)**| 104 | $86.54\%$ (90 / 104) | Marginal |
| | **Partial ($0.2\text{--}0.8$)**| 134 | **$82.09\%$** (110 / 134) | Below target |
| **Solar Elevation** | **Night ($\le 0^\circ$)** | 78 | $96.15\%$ (75 / 78) | Polar night |
| | **Low ($0\text{--}15^\circ$)** | 91 | $83.52\%$ (76 / 91) | Below target |
| | **Mid ($15\text{--}30^\circ$)** | 104 | **$76.92\%$** (80 / 104) | **COLLAPSE** |

---

## 6. Multi-Year Diagnostic Tracking (Arm C, 2020–2023)

Applying the 2022-calibrated multiplier across all four historical years confirms non-stationarity:
- **2020 (Train)**: **$91.52\%$** (335 / 366 origins covered)
- **2021 (Train)**: **$87.14\%$** (318 / 365 origins covered)
- **2022 (Calibration)**: **$90.68\%$** (331 / 365 origins covered)
- **2023 (Blind Test)**: **$84.62\%$** (231 / 273 origins covered)

*Core Diagnostic Finding*:
In 2020 and 2022, the model achieved $\ge 90\%$. In 2021 and 2023, coverage dropped to $87\%$ and $84\%$. The nonconformity score distribution fluctuates significantly from year to year due to inter-annual storm frequency (**VERIFIED**).

---

## 7. Failure Forensics & Why Conformal Transfer Did Not Reach Target

1. **Distribution Shift Between Calibration and Blind Test Years**:
   Split-conformal prediction provides a formal finite-sample coverage guarantee only under its required exchangeability assumption. In this empirical transfer test from 2022 to 2023, a material distribution shift occurred: 2022 had relatively moderate shortfall volatility, whereas summer 2023 experienced active convective storms. The observed 2022→2023 distribution shift means the exchangeability assumption required for the standard split-conformal finite-sample coverage guarantee cannot be assumed for this calibration-to-blind transfer.
2. **What Multiplier Would Have Been Required on 2023?**:
   To achieve approximately $90.0\%$ simultaneous coverage on Blind 2023, the required retrospective score would be **$q_{90, 2023} \approx 1.7610$** ($+32.1\%$ higher than the 2022 calibrated value of $1.3331$).
   Setting $q \approx 1.7610$ would inflate the sunset bound to approximately $1,566.2\text{ Wh/m}^2$, exceeding the static q10 benchmark of $1,510.0\text{ Wh/m}^2$. This indicates that achieving approximately 90% empirical blind-year trajectory coverage through a single larger multiplier would approach or exceed q10-level conservatism. No EMS/controller experiment was run with $q=1.7610$ in this branch, so no fuel-impact claim is made.

---

## Final Scientific Decision & Next Path

### Decision:
**`CONFORMAL-FAILS`** (**VERIFIED**)

While split-conformal AR(1) provides a material improvement over static prefix envelopes ($84.62\%$ vs. $73.99\%$) and reduces reserve conservatism relative to static $q_{10}$, it **fails to achieve the preregistered $\ge 90\%$ empirical simultaneous-coverage target on untouched 2023 blind evaluation** and suffers severe summer collapse ($75.00\%$).

### Scientific Implication:
**Closed-loop EMS controller experiments remain strictly BLOCKED.**

NEXT RESEARCH QUESTION:
Determine whether forecast-error uncertainty can be characterized across multiple historical years and conditioned on causal forecast state/regime in a way that remains stable under cross-year transfer. Any adaptive conformal or state-dependent reserve method remains a research hypothesis and requires separate preregistration and validation.

---

## Status Classifications

**VERIFIED**:
- Blind 2023 simultaneous coverage = $84.62\%$, below the preregistered $\ge 90\%$ target.
- 2023 subgroup coverage collapses to $75.00\%$ in JJA and $73.33\%$ in SON.
- 2022→2023 trajectory/nonconformity distribution shift is observed.
- 2022 empirical calibration coverage is $90.68\%$.
- $q_{\text{conf}} = 1.3331$ was calibrated only from 2022.

**INFERRED**:
- The observed distribution shift means exchangeability between the 2022 calibration sample and 2023 blind sample cannot be assumed.
- A larger multiplier would be required to recover approximately 90% empirical coverage on 2023, but such a multiplier would be at least as conservative as the tested q10 benchmark according to the reported blind-year calculation.

**NOT CLAIMED / NOT TESTED**:
- $q = 1.7610$ was NOT tested in the EMS.
- No fuel penalty for $q = 1.7610$ was measured.
- No online/adaptive conformal method was tested.
- No production/controller change was validated.

**BLOCKED**:
- Historical horizons $k \in [20..24]$ remain unavailable.
- Closed-loop EMS controller experiments remain blocked for this uncertainty branch.
