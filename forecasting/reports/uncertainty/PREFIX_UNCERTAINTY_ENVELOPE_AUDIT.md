# POLARIS — Prefix Envelope Statistical Validation Audit
## Statistical Qualification of Global Prefix Cumulative-Error Envelopes on Blind 2023 Held-Out Data

**Date**: October 05, 2026  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Audit Purpose**: Statistical validation only. Evaluate global unconditioned prefix cumulative forecast-error envelopes constructed from 2020–2022 historical data against the untouched, single-use blind 2023 test partition.  
**Strict Governance Boundary**: STATISTICAL EVALUATION ONLY. Zero modifications to production code, GAP19, EMS, Stage 8.1/Candidate F frozen artifacts, or governance files. Zero controller or optimizer runs. Zero tuning on 2023 data. Zero cloud-regime conditioning added. Zero missing horizon synthesis for $k \in [20..24]$.  
**Companion Artifact**: [`PREFIX_UNCERTAINTY_ENVELOPE_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/PREFIX_UNCERTAINTY_ENVELOPE_AUDIT.json)

---

## Executive Summary & Strict Terminology Definition

This audit evaluates whether global, unconditioned prefix cumulative solar forecast-error envelopes derived from 2020–2022 historical observations can provide a defensible statistical guarantee on the held-out 2023 blind test dataset ($N=273$ origins, 5,187 rows).

### Mathematical Definition of Cumulative Error
Instantaneous error is defined as:
$$e_t = \hat{y}_{\text{pred}, t} - y_{\text{actual}, t} \quad [\text{W/m}^2]$$
where positive $e_t$ represents **solar over-prediction** (a realized solar generation shortfall).

The cumulative solar shortfall up to prefix horizon $k \in \{1, \dots, 19\}$ is:
$$C_k = \sum_{t=1}^k e_t \cdot \Delta t \quad [\text{Wh/m}^2] \quad (\Delta t = 1.0\text{ h})$$

### Pointwise vs. Simultaneous Coverage Distinction
A rigorous distinction is maintained throughout this report:
- **Pointwise Coverage at Step $k$**: The probability that cumulative shortfall at step $k$ does not exceed bound $B_k$:
  $$\text{Coverage}_{\text{pt}}(k) = P\left(C_k \le B_k\right)$$
- **Simultaneous Trajectory Coverage Across All 19 Horizons**: The probability that the entire 19-hour trajectory satisfies the bound at every single prefix step:
  $$\text{Coverage}_{\text{simult}} = P\left(C_k \le B_k \quad \forall k \in \{1, \dots, 19\}\right)$$

> **Mandatory Scientific Warning**:  
> A pointwise $q_{90}$ envelope cannot be claimed to be "90% reliable" for trajectory planning. While each individual step $k$ satisfies $P(C_k \le B_k) \approx 86\%$, the probability of satisfying the bound across **all 19 steps simultaneously collapses to $67.77\%$**. Nearly **one in three days ($32.23\%$) violates the envelope** at some point during the dispatch lookahead window.

---

## 1. Frozen Candidate Envelopes (Estimated on 2020–2022 Train+Val, $N=1,096$)

The candidate bounds were estimated strictly from the 1,096 origins in the combined 2020–2021 Training and 2022 Validation partitions:

| Prefix ($k$) | Target Hour (UTC) | $q_{80}$ Bound ($B_{k, 80}$) | $q_{85}$ Bound ($B_{k, 85}$) | $q_{90}$ Bound ($B_{k, 90}$) | Monotone? | Historical Status |
|---|---|---|---|---|---|---|
| **$k=1$** | 00:00 UTC | $0.00\text{ Wh/m}^2$ | $0.00\text{ Wh/m}^2$ | $0.00\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=2$** | 01:00 UTC | $0.00\text{ Wh/m}^2$ | $0.00\text{ Wh/m}^2$ | $10.65\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=3$** | 02:00 UTC | $0.00\text{ Wh/m}^2$ | $15.01\text{ Wh/m}^2$ | $44.82\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=4$** | 03:00 UTC | $26.37\text{ Wh/m}^2$ | $60.13\text{ Wh/m}^2$ | $117.70\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=5$** | 04:00 UTC | $73.40\text{ Wh/m}^2$ | $125.35\text{ Wh/m}^2$ | $216.54\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=6$** | 05:00 UTC | $110.75\text{ Wh/m}^2$ | $175.19\text{ Wh/m}^2$ | $256.87\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=7$** | 06:00 UTC | $147.18\text{ Wh/m}^2$ | $239.89\text{ Wh/m}^2$ | $344.64\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=8$** | 07:00 UTC | $198.05\text{ Wh/m}^2$ | $297.73\text{ Wh/m}^2$ | $420.56\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=9$** | 08:00 UTC | $204.14\text{ Wh/m}^2$ | $322.52\text{ Wh/m}^2$ | $475.16\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=10$** | 09:00 UTC | $233.33\text{ Wh/m}^2$ | $363.32\text{ Wh/m}^2$ | $543.50\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=11$** | 10:00 UTC | $263.10\text{ Wh/m}^2$ | $406.12\text{ Wh/m}^2$ | $619.44\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=12$** | 11:00 UTC | $285.81\text{ Wh/m}^2$ | $457.82\text{ Wh/m}^2$ | $638.99\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=13$** | 12:00 UTC | $327.98\text{ Wh/m}^2$ | $480.04\text{ Wh/m}^2$ | $706.09\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=14$** | 13:00 UTC | $361.74\text{ Wh/m}^2$ | $514.41\text{ Wh/m}^2$ | $802.52\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=15$** | 14:00 UTC | $432.05\text{ Wh/m}^2$ | $578.21\text{ Wh/m}^2$ | $863.40\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=16$** | 15:00 UTC | $489.47\text{ Wh/m}^2$ | $670.52\text{ Wh/m}^2$ | $925.59\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=17$** | 16:00 UTC | $630.02\text{ Wh/m}^2$ | $869.37\text{ Wh/m}^2$ | $1,137.51\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=18$** | 17:00 UTC | $698.72\text{ Wh/m}^2$ | $931.70\text{ Wh/m}^2$ | $1,220.49\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=19$** | 18:00 UTC | $755.57\text{ Wh/m}^2$ | $1,006.19\text{ Wh/m}^2$ | $1,320.27\text{ Wh/m}^2$ | Yes | **VERIFIED** |
| **$k=20..24$**| 19:00–23:00 UTC | N/A | N/A | N/A | N/A | **BLOCKED ON ARCHIVE GAP** |

*Note on Missing Horizons*: In [`candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv), MEPS 18Z data stops at $+24\text{h}$ lead time from 18:00 UTC, terminating at 18:00 UTC of the target day. Target hours 19:00 to 23:00 UTC ($k \in [20..24]$) are **100% absent across all 1,369 historical origins**. They are **NOT silently filled** (**BLOCKED**).

---

## 2. Pointwise Blind 2023 Evaluation ($N=273$ Origins)

Each candidate envelope was tested on the untouched 273 origins of the Blind 2023 test set:

| Prefix ($k$) | $q_{80}$ Cov [95% CI] | $q_{80}$ Max Viol | $q_{85}$ Cov [95% CI] | $q_{85}$ Max Viol | $q_{90}$ Cov [95% CI] | $q_{90}$ Max Viol | Static $q_{10}$ Benchmark Cov | Static $q_{10}$ Buffer |
|---|---|---|---|---|---|---|---|---|
| **$k=1$** | $87.18\%$ $[83.2\%, 90.8\%]$ | $34.3\text{ Wh}$ | $87.18\%$ $[83.2\%, 90.8\%]$ | $34.3\text{ Wh}$ | **$87.18\%$** $[83.2\%, 90.8\%]$ | $34.3\text{ Wh}$ | $100.0\%$ | $4.2\text{ Wh}$ |
| **$k=2$** | $81.32\%$ $[76.6\%, 85.7\%]$ | $101.0\text{ Wh}$ | $81.32\%$ $[76.6\%, 85.7\%]$ | $101.0\text{ Wh}$ | **$86.81\%$** $[82.8\%, 90.5\%]$ | $90.3\text{ Wh}$ | $100.0\%$ | $13.9\text{ Wh}$ |
| **$k=3$** | $74.36\%$ $[69.2\%, 79.5\%]$ | $207.0\text{ Wh}$ | $79.49\%$ $[74.4\%, 84.2\%]$ | $192.0\text{ Wh}$ | **$85.71\%$** $[81.3\%, 89.7\%]$ | $162.2\text{ Wh}$ | $100.0\%$ | $36.4\text{ Wh}$ |
| **$k=4$** | $71.79\%$ $[66.3\%, 76.9\%]$ | $365.5\text{ Wh}$ | $78.02\%$ $[72.9\%, 83.2\%]$ | $331.7\text{ Wh}$ | **$86.08\%$** $[81.7\%, 90.1\%]$ | $274.2\text{ Wh}$ | $99.27\%$ | $83.4\text{ Wh}$ |
| **$k=5$** | $71.43\%$ $[65.9\%, 76.6\%]$ | $508.9\text{ Wh}$ | $77.66\%$ $[72.5\%, 82.4\%]$ | $456.9\text{ Wh}$ | **$85.71\%$** $[81.3\%, 89.7\%]$ | $365.8\text{ Wh}$ | $97.80\%$ | $152.5\text{ Wh}$ |
| **$k=6$** | $72.16\%$ $[67.0\%, 77.3\%]$ | $626.9\text{ Wh}$ | $80.22\%$ $[75.1\%, 84.6\%]$ | $562.5\text{ Wh}$ | **$85.71\%$** $[81.3\%, 89.7\%]$ | $480.8\text{ Wh}$ | $97.07\%$ | $230.0\text{ Wh}$ |
| **$k=7$** | $71.79\%$ $[66.3\%, 76.9\%]$ | $819.6\text{ Wh}$ | $80.22\%$ $[75.1\%, 85.0\%]$ | $726.9\text{ Wh}$ | **$86.45\%$** $[82.1\%, 90.5\%]$ | $622.1\text{ Wh}$ | $95.97\%$ | $327.9\text{ Wh}$ |
| **$k=8$** | $71.79\%$ $[66.3\%, 76.9\%]$ | $1,077.8\text{ Wh}$| $79.12\%$ $[74.0\%, 83.9\%]$ | $978.1\text{ Wh}$ | **$85.35\%$** $[81.0\%, 89.4\%]$ | $855.3\text{ Wh}$ | $95.24\%$ | $440.7\text{ Wh}$ |
| **$k=9$** | $70.70\%$ $[65.2\%, 76.2\%]$ | $1,437.7\text{ Wh}$| $79.12\%$ $[74.0\%, 83.9\%]$ | $1,319.4\text{ Wh}$| **$85.71\%$** $[81.3\%, 89.7\%]$ | $1,166.7\text{ Wh}$| $95.60\%$ | $561.6\text{ Wh}$ |
| **$k=10$** | $71.43\%$ $[65.9\%, 76.6\%]$ | $1,527.8\text{ Wh}$| $76.92\%$ $[71.8\%, 81.7\%]$ | $1,397.9\text{ Wh}$| **$87.18\%$** $[82.8\%, 91.2\%]$ | $1,217.7\text{ Wh}$| $97.44\%$ | $692.8\text{ Wh}$ |
| **$k=11$** | $71.79\%$ $[66.3\%, 76.9\%]$ | $1,594.1\text{ Wh}$| $77.29\%$ $[72.2\%, 82.1\%]$ | $1,451.1\text{ Wh}$| **$86.45\%$** $[82.1\%, 90.5\%]$ | $1,237.8\text{ Wh}$| $97.44\%$ | $830.4\text{ Wh}$ |
| **$k=12$** | $69.60\%$ $[64.1\%, 75.1\%]$ | $1,751.4\text{ Wh}$| $76.56\%$ $[71.4\%, 81.7\%]$ | $1,579.4\text{ Wh}$| **$86.08\%$** $[81.7\%, 90.1\%]$ | $1,398.2\text{ Wh}$| $97.80\%$ | $976.5\text{ Wh}$ |
| **$k=13$** | $70.70\%$ $[65.2\%, 75.8\%]$ | $1,867.4\text{ Wh}$| $75.82\%$ $[70.7\%, 81.0\%]$ | $1,715.3\text{ Wh}$| **$84.98\%$** $[80.6\%, 89.0\%]$ | $1,489.3\text{ Wh}$| $97.07\%$ | $1,112.9\text{ Wh}$|
| **$k=14$** | $69.23\%$ $[63.7\%, 74.4\%]$ | $2,045.9\text{ Wh}$| $73.99\%$ $[68.9\%, 78.8\%]$ | $1,893.2\text{ Wh}$| **$85.71\%$** $[81.3\%, 89.7\%]$ | $1,605.1\text{ Wh}$| $97.07\%$ | $1,250.5\text{ Wh}$|
| **$k=15$** | $69.23\%$ $[63.7\%, 74.4\%]$ | $2,205.8\text{ Wh}$| $74.73\%$ $[69.2\%, 79.9\%]$ | $2,059.7\text{ Wh}$| **$86.08\%$** $[81.7\%, 90.1\%]$ | $1,774.5\text{ Wh}$| $96.70\%$ | $1,366.6\text{ Wh}$|
| **$k=16$** | $68.50\%$ $[63.0\%, 74.0\%]$ | $2,417.2\text{ Wh}$| $76.56\%$ $[71.4\%, 81.7\%]$ | $2,236.2\text{ Wh}$| **$84.25\%$** $[79.9\%, 88.3\%]$ | $1,981.1\text{ Wh}$| $96.70\%$ | $1,465.4\text{ Wh}$|
| **$k=17$** | $68.50\%$ $[63.0\%, 74.0\%]$ | $2,555.4\text{ Wh}$| $78.02\%$ $[73.3\%, 82.8\%]$ | $2,316.1\text{ Wh}$| **$85.71\%$** $[81.3\%, 89.7\%]$ | $2,047.9\text{ Wh}$| $97.07\%$ | $1,615.5\text{ Wh}$|
| **$k=18$** | $67.03\%$ $[61.5\%, 72.5\%]$ | $2,653.7\text{ Wh}$| $76.92\%$ $[71.8\%, 81.7\%]$ | $2,420.7\text{ Wh}$| **$85.71\%$** $[81.3\%, 89.7\%]$ | $2,131.9\text{ Wh}$| $97.07\%$ | $1,686.7\text{ Wh}$|
| **$k=19$** | $67.03\%$ $[61.5\%, 72.5\%]$ | $2,743.6\text{ Wh}$| $78.02\%$ $[73.3\%, 82.8\%]$ | $2,493.0\text{ Wh}$| **$86.45\%$** $[82.4\%, 90.5\%]$ | $2,178.9\text{ Wh}$| $97.07\%$ | $1,740.0\text{ Wh}$|

*(Bootstrap CIs: 1,000 resamples of the $N=273$ origins in 2023 blind test. Units: $\text{Wh/m}^2$).*

---

## 3. Simultaneous Trajectory Coverage & Violation Forensics

### 3.1 Simultaneous Trajectory Coverage on Blind 2023

$$\text{Coverage}_{\text{simult}} = P\left(C_k \le B_k \quad \forall k \in [1..19]\right)$$

```
+----------------------------------------------------------------------------------------------------+
|                                SIMULTANEOUS TRAJECTORY QUALIFICATION                               |
+-------------------+--------------------+------------------------+----------------------------------+
| Candidate         | Nominal Level      | Blind 2023 Coverage    | Bootstrap 95% Confidence Interval|
+-------------------+--------------------+------------------------+----------------------------------+
| q80 Prefix        | 80% (Candidate)    | 50.18% (137 / 273)     | [43.95%, 56.04%]                 |
| q85 Prefix        | 85% (Candidate)    | 57.51% (157 / 273)     | [51.65%, 63.00%]                 |
| q90 Prefix        | 90% (Candidate)    | 67.77% (185 / 273)     | [62.27%, 72.89%]                 |
+-------------------+--------------------+------------------------+----------------------------------+
| Static q10 Bench  | Heuristic          | 90.11% (246 / 273)     | [86.45%, 93.41%]                 |
+-------------------+--------------------+------------------------+----------------------------------+
```

### 3.2 Violation Forensics & Worst-Prefix Analysis
- **Candidate $q_{80}$**: **136 out of 273 origins ($49.82\%$)** suffered at least one prefix violation.  
  Overall maximum violation was **$2,743.57\text{ Wh/m}^2$**, occurring on origin `2023-07-02` at prefix $k=19$.
- **Candidate $q_{85}$**: **116 out of 273 origins ($42.49\%$)** suffered at least one prefix violation.  
  Overall maximum violation was **$2,492.95\text{ Wh/m}^2$**, occurring on origin `2023-07-02` at prefix $k=19$.
- **Candidate $q_{90}$**: **88 out of 273 origins ($32.23\%$)** suffered at least one prefix violation.  
  Overall maximum violation was **$2,178.86\text{ Wh/m}^2$**, occurring on origin `2023-07-02` at prefix $k=19$.

#### Distribution of Prefix Where Worst Violation Occurs ($q_{90}$ Candidate):
Across the 88 origins that violated the $q_{90}$ envelope:
- Early morning ($k \in [1..5]$): 17 origins ($19.3\%$)
- Midday entrance & solar noon ($k \in [6..12]$): 28 origins ($31.8\%$)
- Afternoon trough ($k \in [13..16]$): 20 origins ($22.7\%$)
- Evening sunset ramp ($k \in [17..19]$): 23 origins ($26.1\%$)

*Insight*: Violations do not occur exclusively at sunset; in **$73.9\%$ of violating origins**, the peak violation occurred during morning or midday hours ($k \le 16$), proving that intra-day dynamics frequently breach static bounds before the end of the solar day (**VERIFIED**).

---

## 4. Seasonal & Year-by-Year Robustness

### 4.1 Seasonal Collapse in Blind 2023
Evaluating simultaneous trajectory coverage by season reveals an **extreme seasonal disparity**:

| Season in 2023 | Origin Count ($N$) | $q_{80}$ Trajectory Coverage | $q_{85}$ Trajectory Coverage | $q_{90}$ Trajectory Coverage |
|---|---|---|---|---|
| **Winter (DJF)** | 59 | **$100.00\%$** (59 / 59) | **$100.00\%$** (59 / 59) | **$100.00\%$** (59 / 59) |
| **Spring (MAM)** | 92 | $57.61\%$ (53 / 92) | $66.30\%$ (61 / 92) | **$79.35\%$** (73 / 92) |
| **Summer (JJA)** | 92 | **$13.04\%$** (12 / 92) | **$22.83\%$** (21 / 92) | **$33.70\%$** (31 / 92) |
| **Autumn (SON)** | 30 | $43.33\%$ (13 / 30) | $53.33\%$ (16 / 30) | **$73.33\%$** (22 / 30) |

*Core Forensic Finding*:
In Summer 2023, simultaneous coverage of the global $q_{90}$ envelope collapsed to **$33.70\%$** (**two out of three summer days violated the envelope**). Because the unconditioned global envelope averages across all seasons, it over-buffers Winter ($100\%$ coverage on polar night days requiring $<10\text{ Wh/m}^2$) while drastically under-buffering Summer, where unexpected cloud storms create cumulative shortfalls exceeding $2,000\text{ Wh/m}^2$ (**VERIFIED**).

### 4.2 Year-by-Year Trajectory Stability (2020–2023)

| Year | Origin Count ($N$) | $q_{80}$ Trajectory Coverage | $q_{85}$ Trajectory Coverage | $q_{90}$ Trajectory Coverage |
|---|---|---|---|---|
| **2020 (Train)** | 366 | $68.58\%$ | $75.14\%$ | **$82.51\%$** |
| **2021 (Train)** | 365 | $61.10\%$ | $69.86\%$ | **$76.99\%$** |
| **2022 (Validation)** | 365 | $60.82\%$ | $68.22\%$ | **$76.99\%$** |
| **2023 (Blind Test)** | 273 | **$50.18\%$** | **$57.51\%$** | **$67.77\%$** |

*Core Forensic Finding*:
Across all four historical years, unconditioned simultaneous coverage of the $q_{90}$ bound never exceeds $82.5\%$, and monotonically drifts downward from $82.5\%$ in 2020 to $67.8\%$ in 2023 (**VERIFIED**).

---

## 5. Comparison with Static $q_{10}$ Benchmark

Evaluating the existing static $q_{10}$ benchmark under the identical cumulative shortfall metric on Blind 2023 yields a striking contrast:

```
+---------------------------------------------------------------------------------------------------------+
|                                    STATIC q10 vs. GLOBAL PREFIX q90 COMPARISON                          |
+------------------------------+---------------------------------------+----------------------------------+
| Metric                       | Static q10 Benchmark                  | Global Prefix q90 Envelope       |
+------------------------------+---------------------------------------+----------------------------------+
| Pointwise 2023 Coverage      | 95.2% to 100.0% across all prefixes   | 84.2% to 87.2% across prefixes   |
| Simultaneous 2023 Coverage   | 90.11% (246 / 273 origins)            | 67.77% (185 / 273 origins)       |
| Bootstrap 95% CI (Simult)    | [86.45%, 93.41%]                      | [62.27%, 72.89%]                 |
| Sunset Bound (k=19)          | 1,740.0 Wh/m² (mean cumulative buffer)| 1,320.3 Wh/m² (frozen quantile)  |
| Buffer Size Difference       | +419.7 Wh/m² (+31.8% higher buffer)   | Baseline                         |
| Operational Tradeoff         | Proven 93.4% unmet load cut, but      | Leaner buffer, but 32.2%         |
|                              | +38.2% fuel & +92.9% curtailment      | trajectory violation rate        |
+------------------------------+---------------------------------------+----------------------------------+
```

*Mechanism Synthesis*:
Static $q_{10}$ achieves $90.11\%$ simultaneous trajectory coverage on Blind 2023 **because its mean cumulative buffer reaches $1,740.0\text{ Wh/m}^2$** at sunset (applying a severe pointwise 95%–100% margin at every single hour). The global $q_{90}$ prefix bound ($1,320.3\text{ Wh/m}^2$) is $31.8\%$ leaner, but this reduction in conservatism causes its simultaneous coverage to fall to $67.77\%$ (**VERIFIED**).

---

## Mandatory Statistical Audit Conclusions

### A. Which envelope, if any, is statistically defensible?
**NO GLOBAL UNCONDITIONED PREFIX ENVELOPE IS STATISTICALLY DEFENSIBLE FOR TRAJECTORY COVERAGE.** (**VERIFIED**)

- **$q_{80}$ and $q_{85}$ Envelopes**: Suffer from severe under-coverage both pointwise ($67.0\%\text{--}78.0\%$) and simultaneously ($50.18\%$ and $57.51\%$). They are decisively disqualified.
- **$q_{90}$ Envelope**: While achieving respectable pointwise coverage ($84.25\%\text{--}87.18\%$, mean $85.9\%$), its simultaneous trajectory coverage is only **$67.77\%$** ($95\%$ CI: $[62.27\%, 72.89\%]$). Calling this envelope "90% reliable" is mathematically false. In Summer 2023, it fails on **$66.3\%$ of days** (achieving only $33.70\%$ coverage).

### B. Whether simultaneous coverage is achievable without excessive conservatism.
**SIMULTANEOUS COVERAGE $\ge 90\%$ IS NOT ACHIEVABLE WITH AN UNCONDITIONED STATIC PREFIX ENVELOPE WITHOUT EXCESSIVE CONSERVATISM.** (**VERIFIED**)

To achieve $\ge 90\%$ simultaneous coverage on Blind 2023, an unconditioned bound must either:
1. Adopt static $q_{10}$'s massive cumulative buffer of $1,740\text{ Wh/m}^2$, which incurs a $+38.18\%$ fuel and $+92.87\%$ curtailment penalty, OR
2. Adopt a split-conformal simultaneous multiplier ($\lambda = 2.9179$), inflating the sunset bound to **$3,852.4\text{ Wh/m}^2$** (a $2.9\times$ expansion).

An unconditioned global bound cannot reconcile the seasonal dynamic range between Winter ($<10\text{ Wh/m}^2$) and Summer ($>2,000\text{ Wh/m}^2$).

### C. Whether the prefix approach should proceed to a closed-loop EMS experiment.
**DO NOT PROCEED TO CLOSED-LOOP EMS EXPERIMENTS WITH AN UNCONDITIONED GLOBAL PREFIX ENVELOPE.** (**VERIFIED / INFERRED**)

Deploying an unconditioned global prefix envelope in closed-loop control would recreate the failure modes observed in L2-EXP-11 and L2-EXP-12: on summer days where the bound is breached by up to $2,178.9\text{ Wh/m}^2$, the battery reserve would be exhausted, precipitating critical unmet load.

The prefix formulation itself remains physically sound (matching battery energy integration), but it **must incorporate regime conditioning** (such as season or day-ahead forecast cloud cover) before any closed-loop experimental testing.

### D. Explicit Non-Defensibility Declaration
**VERIFIED**: All three candidate global unconditioned prefix envelopes ($q_{80}, q_{85}, q_{90}$) are **NOT STATISTICALLY DEFENSIBLE** as reliable operational uncertainty envelopes for microgrid lookahead dispatch.
