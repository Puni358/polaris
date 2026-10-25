# POLARIS — Regime-Conditioned Prefix Envelope Validation Audit
## Statistical Qualification of Season-Conditioned and Cloud-Regime-Conditioned Prefix Cumulative-Error Envelopes on Blind 2023 Data

**Date**: October 05, 2026  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Audit Purpose**: Statistical validation of regime-conditioned prefix cumulative solar forecast-error envelopes. Evaluates whether conditioning on causal forecast-issuance state (calendar season vs. forecast cloud cover) resolves the trajectory under-coverage failure of global unconditioned prefix envelopes.  
**Strict Governance Boundary**: RESEARCH EVALUATION ONLY. Zero modifications to production code, GAP19 MILP, EMS dispatch logic, Stage 8.1/Candidate F frozen artifacts, or governance registers. Zero controller or optimizer runs. Zero threshold tuning on 2023. Missing horizons $k \in [20..24]$ remain **BLOCKED**.  
**Companion Artifact**: [`REGIME_CONDITIONED_PREFIX_ENVELOPE_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/REGIME_CONDITIONED_PREFIX_ENVELOPE_AUDIT.json)

---

## Executive Summary & Core Verdict

Following the rejection of global unconditioned prefix envelopes ($q_{80}, q_{85}, q_{90}$) due to simultaneous trajectory collapse ($67.77\%$ overall, $33.70\%$ in summer), this audit evaluates two regime conditioning schemes using **only information causally available at forecast issuance**:

1. **Scheme A: Season-Conditioned** (DJF, MAM, JJA, SON)
2. **Scheme B: Cloud-Regime-Conditioned** (Clear $<0.20$, Partial $0.20$--$0.80$, Overcast $>0.80$ mean forecast cloud fraction)

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                    EXECUTIVE SUMMARY: REGIME-CONDITIONED TRAJECTORY COVERAGE                            |
+---------------------------+-------------------+--------------------+------------------------+---------------------------+
| Conditioning Scheme       | Regime            | Train+Val N (20-22)| Blind 2023 N (2023)    | Blind 2023 Simult Cov q90 |
+---------------------------+-------------------+--------------------+------------------------+---------------------------+
| Unconditioned Baseline    | Global            | 1,096              | 273                    | 67.77% [62.27%, 72.89%]   |
+---------------------------+-------------------+--------------------+------------------------+---------------------------+
| Scheme A: Season          | DJF (Winter)      | 271                | 59                     | 77.97% [67.75%, 88.14%]   |
|                           | MAM (Spring)      | 276                | 92                     | 66.30% [55.43%, 76.09%]   |
|                           | JJA (Summer)      | 276                | 92                     | 64.13% [54.35%, 73.91%]   |
|                           | SON (Autumn)      | 273                | 30 (Sep only)          | 20.00% [ 6.67%, 36.67%]   |
|                           | Combined Scheme A | 1,096              | 273                    | 63.00% [57.50%, 68.86%]   |
+---------------------------+-------------------+--------------------+------------------------+---------------------------+
| Scheme B: Cloud Regime    | Clear (<0.20)     | 111                | 35                     | 77.14% [62.86%, 88.57%]   |
|                           | Partial (0.2-0.8) | 533                | 134                    | 67.16% [58.94%, 74.63%]   |
|                           | Overcast (>0.80)  | 452                | 104                    | 65.38% [56.73%, 75.00%]   |
|                           | Combined Scheme B | 1,096              | 273                    | 67.77% [62.64%, 73.26%]   |
+---------------------------+-------------------+--------------------+------------------------+---------------------------+
```

### Critical Findings:
1. **Neither scheme achieves defensible simultaneous trajectory coverage**:
   - **Season Conditioning** actually **worsens** annual simultaneous coverage from $67.77\%$ to **$63.00\%$**. Summer coverage improves modestly (from $33.7\%$ to $64.1\%$), but remains an unacceptable 1-in-3 daily failure rate, while Autumn collapses catastrophically to **$20.00\%$** due to calendar truncation in the 2023 dataset.
   - **Cloud Regime Conditioning** produces an annual simultaneous coverage of **$67.77\%$**—literally identical to the unconditioned global baseline. Individual regimes remain trapped between $65.4\%$ and $77.1\%$.
2. **Catastrophic Failure Modes Remain**:
   - When Clear-day forecasts fail (cloud unexpectedly rolls in), realized shortfalls exceed the bound by up to **$2,076.10\text{ Wh/m}^2$**.
   - Overcast and Partial days experience simultaneous breach rates of $34.6\%$ and $32.8\%$ respectively.
3. **Core Architectural Verdict**:
   - **Regime-conditioning scales the variance of the marginal distributions, but it does NOT eliminate temporal autocorrelation or multi-step drift.**
   - Consequently, **NO REGIME-CONDITIONED PREFIX ENVELOPE IS CURRENTLY STATISTICALLY DEFENSIBLE FOR CLOSED-LOOP EMS TESTING** (**VERIFIED**).

---

## 1. Scheme A: Season-Conditioned Prefix Envelopes

### 1.1 Methodology and Data Partition
Seasons are defined strictly by calendar month at forecast issuance:
- **DJF (Winter)**: December, January, February ($N_{\text{train+val}} = 271$, $N_{2023} = 59$)
- **MAM (Spring)**: March, April, May ($N_{\text{train+val}} = 276$, $N_{2023} = 92$)
- **JJA (Summer)**: June, July, August ($N_{\text{train+val}} = 276$, $N_{2023} = 92$)
- **SON (Autumn)**: September, October, November ($N_{\text{train+val}} = 273$, $N_{2023} = 30$)  
  *(Note on SON: 2023 blind test ends on September 30, so SON 2023 consists exclusively of September).*

### 1.2 Pointwise and Simultaneous Performance by Season on Blind 2023

| Season | Nominal Quantile | Pointwise Coverage Range ($k=1..19$) | Simultaneous Trajectory Coverage | Bootstrap 95% CI | Max Violation ($Wh/m^2$) | Peak Violation Prefix ($k$) |
|---|---|---|---|---|---|---|
| **DJF** | $q_{80}$ | $79.66\% \text{--} 100.0\%$ | $72.88\%$ (43 / 59) | $[61.02\%, 84.75\%]$ | $244.6\text{ Wh}$ | $k=15$ |
| | $q_{85}$ | $79.66\% \text{--} 100.0\%$ | $72.88\%$ (43 / 59) | $[61.02\%, 84.75\%]$ | $238.8\text{ Wh}$ | $k=15$ |
| | **$q_{90}$** | **$79.66\% \text{--} 100.0\%$** | **$77.97\%$ (46 / 59)** | **$[67.75\%, 88.14\%]$** | **$211.3\text{ Wh}$** | $k=15$ ($61.5\%$) |
| **MAM** | $q_{80}$ | $64.13\% \text{--} 95.65\%$ | $43.48\%$ (40 / 92) | $[33.70\%, 52.20\%]$ | $1,967.1\text{ Wh}$| $k=19$ |
| | $q_{85}$ | $70.65\% \text{--} 95.65\%$ | $54.35\%$ (50 / 92) | $[44.57\%, 64.16\%]$ | $1,818.5\text{ Wh}$| $k=19$ |
| | **$q_{90}$** | **$77.17\% \text{--} 95.65\%$** | **$66.30\%$ (61 / 92)** | **$[55.43\%, 76.09\%]$** | **$1,619.5\text{ Wh}$**| $k=19$ ($38.7\%$) |
| **JJA** | $q_{80}$ | $75.00\% \text{--} 82.61\%$ | $53.26\%$ (49 / 92) | $[43.48\%, 64.13\%]$ | $1,925.5\text{ Wh}$| $k=4$ |
| | $q_{85}$ | $79.35\% \text{--} 86.96\%$ | $58.70\%$ (54 / 92) | $[48.91\%, 68.51\%]$ | $1,751.0\text{ Wh}$| $k=4$ |
| | **$q_{90}$** | **$83.70\% \text{--} 92.39\%$** | **$64.13\%$ (59 / 92)** | **$[54.35\%, 73.91\%]$** | **$1,525.9\text{ Wh}$**| $k=4$ ($21.2\%$) |
| **SON** | $q_{80}$ | $26.67\% \text{--} 100.0\%$ | $20.00\%$ (6 / 30) | $[ 6.67\%, 36.67\%]$ | $1,001.4\text{ Wh}$| $k=15$ |
| | $q_{85}$ | $36.67\% \text{--} 100.0\%$ | $20.00\%$ (6 / 30) | $[ 6.67\%, 36.67\%]$ | $915.5\text{ Wh}$ | $k=15$ |
| | **$q_{90}$** | **$46.67\% \text{--} 100.0\%$** | **$20.00\%$ (6 / 30)** | **$[ 6.67\%, 36.67\%]$** | **$825.6\text{ Wh}$** | $k=15$ ($29.2\%$) |

### 1.3 Forensics of Season-Conditioned Collapse
1. **The SON Collapse Mechanism**:
   In 2020–2022, SON ($N=273$) consists of September (high solar), October (low solar), and November (polar night approaching zero). Because October and November comprise two-thirds of the training sample, the resulting empirical quantiles are heavily weighted toward near-zero errors ($B_{19, 90} = 575.02\text{ Wh/m}^2$). When tested on 2023, where only September is present, high solar generation and early autumn cloud variability easily breach this bound, causing an **$80.0\%$ violation rate** (**VERIFIED**).
2. **Summer (JJA) Insufficiency**:
   Although tightening the summer envelope to its own distribution raises $B_{19, 90}$ from $1,320.3\text{ Wh/m}^2$ to $1,973.26\text{ Wh/m}^2$ (raising trajectory coverage from $33.7\%$ to $64.1\%$), **$35.9\%$ of summer days still fail**. Summer errors exhibit severe burstiness during early morning ramps ($k=4$), breaching the bound before noon.
3. **Winter (DJF) Degradation**:
   Under global bounds ($B_{19} = 1,320\text{ Wh/m}^2$), DJF had $100\%$ coverage because winter solar is negligible. Season-conditioning tightens the DJF bound to $8.77\text{ Wh/m}^2$. Consequently, small diffuse shortfalls in late February cause **$22.0\%$ of DJF days to breach the bound** (**VERIFIED**).

---

## 2. Scheme B: Cloud-Regime-Conditioned Prefix Envelopes

### 2.1 Methodology and Data Partition
Regimes are determined strictly by the **mean forecast cloud fraction** (NWP `fc_cloud_cover / 100`) across the lookahead horizon available at forecast issuance:
- **Clear**: $\bar{c}_{\text{fc}} < 0.20$ ($N_{\text{train+val}} = 111$, $N_{2023} = 35$)
- **Partial**: $0.20 \le \bar{c}_{\text{fc}} \le 0.80$ ($N_{\text{train+val}} = 533$, $N_{2023} = 134$)
- **Overcast**: $\bar{c}_{\text{fc}} > 0.80$ ($N_{\text{train+val}} = 452$, $N_{2023} = 104$)

No actual solar radiation or ground-truth cloud observation is used for regime assignment.

### 2.2 Pointwise and Simultaneous Performance by Cloud Regime on Blind 2023

| Cloud Regime | Nominal Quantile | Pointwise Coverage Range ($k=1..19$) | Simultaneous Trajectory Coverage | Bootstrap 95% CI | Max Violation ($Wh/m^2$) | Peak Violation Prefix ($k$) |
|---|---|---|---|---|---|---|
| **Clear** | $q_{80}$ | $80.00\% \text{--} 88.57\%$ | $68.57\%$ (24 / 35) | $[54.29\%, 82.86\%]$ | $2,433.7\text{ Wh}$| $k=19$ |
| | $q_{85}$ | $82.86\% \text{--} 91.43\%$ | $71.43\%$ (25 / 35) | $[57.14\%, 85.71\%]$ | $2,259.1\text{ Wh}$| $k=19$ |
| | **$q_{90}$** | **$82.86\% \text{--} 91.43\%$** | **$77.14\%$ (27 / 35)** | **$[62.86\%, 88.57\%]$** | **$2,076.1\text{ Wh}$**| $k=19$ ($50.0\%$) |
| **Partial** | $q_{80}$ | $66.42\% \text{--} 85.07\%$ | $47.01\%$ (63 / 134) | $[38.81\%, 55.97\%]$ | $2,073.4\text{ Wh}$| $k=19$ |
| | $q_{85}$ | $73.13\% \text{--} 85.07\%$ | $55.97\%$ (75 / 134) | $[47.76\%, 64.18\%]$ | $1,832.6\text{ Wh}$| $k=19$ |
| | **$q_{90}$** | **$85.07\% \text{--} 88.81\%$** | **$67.16\%$ (90 / 134)** | **$[58.94\%, 74.63\%]$** | **$1,475.1\text{ Wh}$**| $k=19$ ($18.2\%$) |
| **Overcast**| $q_{80}$ | $64.42\% \text{--} 90.38\%$ | $47.12\%$ (49 / 104) | $[37.50\%, 56.73\%]$ | $1,864.7\text{ Wh}$| $k=19$ |
| | $q_{85}$ | $70.19\% \text{--} 90.38\%$ | $55.77\%$ (58 / 104) | $[46.15\%, 64.45\%]$ | $1,704.4\text{ Wh}$| $k=19$ |
| | **$q_{90}$** | **$79.81\% \text{--} 90.38\%$** | **$65.38\%$ (68 / 104)** | **$[56.73\%, 75.00\%]$** | **$1,310.0\text{ Wh}$**| $k=6$ ($19.4\%$) |

### 2.3 Forensics of Cloud-Regime Failures
1. **The "Clear Day" Catastrophic Breach**:
   On days forecasted to be clear ($ar{c}_{\text{fc}} < 0.20$), the model expects uninterrupted high solar irradiance ($>500\text{ W/m}^2$). If an unpredicted cloud deck forms over Mount Nuolja, actual irradiance collapses toward zero. Even though simultaneous coverage is highest in this regime ($77.14\%$), **the violations are catastrophic**: the maximum shortfall reaches **$2,076.10\text{ Wh/m}^2$** at sunset ($k=19$). In an operational EMS, this would wipe out battery reserves completely.
2. **Sample Size Limitations for Clear Regime**:
   The Clear regime has only $N=111$ origins in 2020–2022 and $N=35$ in 2023 (due to high sub-Arctic cloudiness). With $N=35$, the $95\%$ confidence interval on simultaneous coverage is wide ($[62.9\%, 88.6\%]$). While mathematically computable, it rests on thin empirical support compared to Partial ($N=533$) and Overcast ($N=452$).
3. **Persistent Under-Coverage in Partial and Overcast**:
   In Partial and Overcast regimes (comprising $87.2\%$ of all days), simultaneous coverage under $q_{90}$ is only **$67.16\%$** and **$65.38\%$**. More than one in three days breaches the reserve bound (**VERIFIED**).

---

## 3. Direct Comparison: Season vs. Cloud Conditioning

```
+---------------------------------------------------------------------------------------------------------------+
|                                    DIRECT COMPARISON: SCHEME A vs. SCHEME B                                   |
+------------------------------+---------------------------------------+----------------------------------------+
| Dimension                    | Scheme A: Season-Conditioned          | Scheme B: Cloud-Regime-Conditioned     |
+------------------------------+---------------------------------------+----------------------------------------+
| 2023 Aggregate Simult Cov    | 63.00% (Worse than global baseline)   | 67.77% (Identical to global baseline)  |
| Best Regime Simult Cov       | 77.97% (DJF, Winter)                  | 77.14% (Clear, <0.20)                  |
| Worst Regime Simult Cov      | 20.00% (SON, Autumn - Collapsed)      | 65.38% (Overcast, >0.80)               |
| Peak Violation Magnitude     | 1,619.45 Wh/m² (Spring)               | 2,076.10 Wh/m² (Clear)                 |
| Physical Causal Grounding    | Weak (arbitrary calendar months)      | Strong (forecast atmospheric state)    |
| Sample Balance               | Even (~275 per season)                | Highly skewed (Clear N=111, Part N=533)|
| Sensitivity to Truncation    | Severe (SON failed due to Sep cutoff) | Robust (weather occurs across months)  |
| Trajectory Viability         | REJECTED (20% to 78% range)           | REJECTED (65% to 77% range)            |
+------------------------------+---------------------------------------+----------------------------------------+
```

---

## 4. Year-by-Year Trajectory Stability (2020–2023)

To ensure these results are not an anomaly of 2023, simultaneous coverage of the $q_{90}$ bound was audited across all four years:

### Season-Conditioned Year-by-Year $q_{90}$ Trajectory Coverage:
- **2020 (Train, N=366)**: DJF $78.0\%$, MAM $83.7\%$, JJA $75.0\%$, SON $80.2\%$ | **Total: $79.23\%$**
- **2021 (Train, N=365)**: DJF $78.9\%$, MAM $73.9\%$, JJA $66.3\%$, SON $74.7\%$ | **Total: $73.42\%$**
- **2022 (Val, N=365)**: DJF $81.1\%$, MAM $68.5\%$, JJA $71.7\%$, SON $82.4\%$ | **Total: $75.89\%$**
- **2023 (Blind, N=273)**: DJF $78.0\%$, MAM $66.3\%$, JJA $64.1\%$, SON $20.0\%$ | **Total: $63.00\%$**

### Cloud-Conditioned Year-by-Year $q_{90}$ Trajectory Coverage:
- **2020 (Train, N=366)**: Clear $80.0\%$, Partial $83.1\%$, Overcast $84.2\%$ | **Total: $83.33\%$**
- **2021 (Train, N=365)**: Clear $81.0\%$, Partial $72.6\%$, Overcast $79.7\%$ | **Total: $76.16\%$**
- **2022 (Val, N=365)**: Clear $70.5\%$, Partial $78.8\%$, Overcast $77.0\%$ | **Total: $76.99\%$**
- **2023 (Blind, N=273)**: Clear $77.1\%$, Partial $67.2\%$, Overcast $65.4\%$ | **Total: $67.77\%$**

*Key Finding*: Even in the training years (2020–2021), simultaneous trajectory coverage **never reached $90\%$** in any regime under either scheme. It peaked at $83\%	ext{--}84\%$ and continuously drifted downward (**VERIFIED**).

---

## Final Decision Answers

### A. Does season conditioning materially improve blind simultaneous coverage?
**NO.** (**VERIFIED**)  
Annual simultaneous trajectory coverage under Season Conditioning drops from $67.77\%$ (unconditioned global) to **$63.00\%$** ($95\%$ CI: $[57.50\%, 68.86\%]$). While Summer trajectory coverage improves from $33.7\%$ to $64.1\%$, it remains far below operational tolerance (failing on $35.9\%$ of summer days). Meanwhile, Winter coverage degrades from $100\%$ to $78.0\%$, and Autumn coverage collapses catastrophically to **$20.00\%$**.

### B. Does cloud conditioning materially improve it?
**NO.** (**VERIFIED**)  
Annual simultaneous trajectory coverage under Cloud-Regime Conditioning is **$67.77\%$** ($95\%$ CI: $[62.64\%, 73.26\%]$)—identical to the global unconditioned envelope ($185 / 273$ origins covered). Clear days reach $77.14\%$, Partial days reach $67.16\%$, and Overcast days reach $65.38\%$. None approach $90\%$, and Clear-day breaches produce devastating shortfalls up to $2,076.10	ext{ Wh/m}^2$.

### C. Which scheme is statistically more defensible?
**NEITHER SCHEME IS STATISTICALLY DEFENSIBLE FOR OPERATIONAL LOOKAHEAD DISPATCH.** (**VERIFIED**)  
Between the two:
- **Cloud Conditioning** is physically more defensible because it uses causal NWP atmospheric forecasts issued on the day of dispatch, avoiding calendar boundary artifacts like the SON collapse.
- However, because both schemes fail to achieve even $80\%$ simultaneous coverage on Blind 2023, neither provides a viable statistical foundation for microgrid reserve sizing.

### D. Are any regimes still catastrophically under-covered?
**YES.** (**VERIFIED**)  
1. **SON (Autumn) under Season Conditioning**: Suffers an catastrophic **$80.0\%$ failure rate** ($20.00\%$ coverage), caused by testing on September-only data against an October/November-diluted training distribution.
2. **JJA (Summer) under Season Conditioning**: Fails on **$35.9\%$ of days** ($64.13\%$ coverage), with breaches exceeding $1,500	ext{ Wh/m}^2$.
3. **Clear Days under Cloud Conditioning**: While achieving $77.14\%$ coverage, suffers catastrophic breaches up to **$2,076.10	ext{ Wh/m}^2$** when unexpected cloud decks invalidate the clear forecast.
4. **Partial and Overcast under Cloud Conditioning**: Fail on **$32.8\%$** and **$34.6\%$ of days**, respectively.

### E. Is there enough evidence to justify ONE regime-conditioned prefix envelope for a later EMS experiment?
**NO.** (**VERIFIED**)  
**Mandatory Validation Criterion**: An uncertainty representation must provide $\ge 90\%$ empirical simultaneous coverage across the lookahead horizon (or within an audited confidence bound) without catastrophic breach magnitudes before being tested in closed-loop control.

Because no regime-conditioned envelope achieves even $80\%$ simultaneous coverage, injecting any of these candidate envelopes into the EMS would cause persistent battery reserve depletion and unmet load. **Closed-loop controller experiments remain BLOCKED.**

---

## Status Classifications

- **VERIFIED**: Empirical failure of both Season-Conditioned ($63.00\%$) and Cloud-Conditioned ($67.77\%$) simultaneous trajectory coverage on Blind 2023.
- **VERIFIED**: Catastrophic under-coverage of SON ($20.00\%$), Summer ($64.13\%$), Overcast ($65.38\%$), and Partial ($67.16\%$) regimes.
- **VERIFIED**: Rejection of closed-loop EMS testing for all candidate regime-conditioned envelopes.
- **INFERRED**: Simultaneous trajectory failure stems from temporal error autocorrelation, which point-by-point quantiles (even when regime-conditioned) cannot absorb without conformal trajectory inflation or dynamic reserve scaling.
- **BLOCKED**: Historical lookahead horizons $k \in [20..24]$ remain 100% missing from MEPS archive.
- **BLOCKED**: Closed-loop EMS controller experiments with prefix envelopes remain blocked until a trajectory-valid uncertainty representation is constructed.
