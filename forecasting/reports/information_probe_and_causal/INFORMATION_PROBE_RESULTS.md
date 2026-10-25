# POLARIS — INFORMATION PROBE PHASE A RESULTS REPORT

**Date (UTC):** 2026-09-16  
**Phase:** Phase A — Incremental Information Test (P0 vs P1)  
**Data Partition:** EVEN origins only ($N=174$)  
**ODD Access:** ZERO ACCESS (Firewall confirmed)  

---

## 1. Executive Summary & Controlled Scientific Finding

> Phase A provides strong evidence that the frozen Stage8.1 causal state contains nonlinear predictive information about future H7–H12 transmission statistics beyond deterministic solar/seasonal information. This is inconsistent with M1 (information absent) for the tested targets. Phase A does not by itself distinguish representation limitations from point-prediction/loss limitations or unresolved event timing; these remain hypotheses for subsequent diagnostic testing.

**Key Quantitative Results:**
- Using non-linear GBDT (Model B), **P1 achieves OOF $R^2 = 0.5274$ and Spearman $\rho = 0.7221$** on mean transmission level (T3), yielding $\Delta R^2 = +0.5988$ ($p < 0.0001$, 95% bootstrap CI $[+0.3639, +0.8421]$).
- Linear Ridge regression (Model A) yields negative out-of-fold $R^2$ ($R^2 < 0$), proving that the causal information in the Stage 8.1 state is non-linear and requires decision-tree interactions.
- Phase A does NOT by itself establish M2 (representation) or M3 (loss hedging) as the definitive cause, nor does it infer that improved prediction of T1–T3 necessarily translates to reduced point SW_IN MAE.

---

## 2. Data & Eligibility Summary

- **Total EVEN Origins:** 174
- **Eligible EVEN Origins ($N_{\text{eligible}}$):** **104** (Satisfies $\ge 5/6$ valid $k_t$ hours in H7–H12 where $\text{clearsky\_GHI} \ge 20\text{ W/m}^2$)
- **Excluded EVEN Origins:** 70 (Polar-night winter origins)
- **Power Floor ($N \ge 60$):** **PASSED** ($104 \ge 60$)
- **Eligible CSV Hash:** `d2beca0747bfe18a4541bdfc664afcd9e9af838f324ecbf586fbec82ea4da88e`
- **OOF Predictions CSV Hash:** `3652f298268e3e41393aa2ae79b6943dac826745e997403309bbb74d3937cce5`

### Canonical GroupKFold Distribution (104 Eligible Origins)
Fold assignments were fixed across all 174 EVEN origins prior to eligibility filtering:
- Fold 1: 21 eligible origins
- Fold 2: 21 eligible origins
- Fold 3: 21 eligible origins
- Fold 4: 20 eligible origins
- Fold 5: 21 eligible origins

---

## 3. Ladder Feature Sets

- **P0 — Deterministic Solar/Seasonal State (22 features):** Solar elevation $t_0$ & H7–H12 (7), solar azimuth H7–H12 (6), clear-sky GHI H7–H12 (6), DOY sin/cos (2), daylight duration (1).
- **P1 — P0 + Frozen Stage 8.1 Causal State (147 features):** Unrolled origin-level representation of the 37 Stage 8.1 features (15 origin-level context/month features + 22 horizon features $\times$ 6 hours H7–H12). Zero feature selection, transformations, or latent tuning.

---

## 4. Phase A Performance & Statistical Test Matrix

### Target T1 — Future Transmission Volatility ($\text{std}(k_t)$)

| Model | P0 OOF $R^2$ | P1 OOF $R^2$ | $\Delta R^2$ (P1 - P0) | P0 Spearman $\rho$ | P1 Spearman $\rho$ | Paired Bootstrap 95% CI | Month-Permutation $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A (Ridge)** | -0.0818 | -1.4102 | -1.3284 | -0.1132 | 0.0601 | [-2.2078, -0.7182] | 0.3420 |
| **Model B (GBDT)** | -0.4617 | -0.1518 | **+0.3098** | -0.2713 | 0.1230 | **[+0.0506, +0.5886]** | **< 0.0001** |

### Target T2 — Maximum Transition Magnitude ($\max |\Delta k_t|$)

| Model | P0 OOF $R^2$ | P1 OOF $R^2$ | $\Delta R^2$ (P1 - P0) | P0 Spearman $\rho$ | P1 Spearman $\rho$ | Paired Bootstrap 95% CI | Month-Permutation $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A (Ridge)** | -0.0780 | -1.2588 | -1.1808 | -0.2188 | 0.0842 | [-1.9753, -0.6187] | 0.2600 |
| **Model B (GBDT)** | -0.4434 | -0.1382 | **+0.3052** | -0.2224 | 0.1717 | **[+0.0470, +0.5837]** | **< 0.0001** |

### Target T3 — Mean Transmission Level ($\text{mean}(k_t)$)

| Model | P0 OOF $R^2$ | P1 OOF $R^2$ | $\Delta R^2$ (P1 - P0) | P0 Spearman $\rho$ | P1 Spearman $\rho$ | Paired Bootstrap 95% CI | Month-Permutation $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A (Ridge)** | 0.0309 | -0.0952 | -0.1261 | 0.2204 | 0.5273 | [-0.7079, +0.3033] | < 0.0001 |
| **Model B (GBDT)** | -0.0714 | **0.5274** | **+0.5988** | 0.2505 | **0.7221** | **[+0.3639, +0.8421]** | **< 0.0001** |

### Target T4 — Champion Difficulty

> **Status:** DROPPED / UNAVAILABLE. Genuine matching-fold Stage 8.1 EVEN OOF predictions could not be reconstructed without violating protocol. T4 was dropped per Section 2 & 5.

---

## 5. Governance Decision Rule Interpretation

- **Original formal hit criterion:** Require at least 2 of 4 targets individually to satisfy $\Delta R^2 \ge 0.03$ AND bootstrap 95% CI excluding zero.
- **T4 status:** Dropped / unavailable.
- **Enforced Governance Rule:** With T4 unavailable, the original 2-of-4 formal hit criterion **cannot be satisfied using T1–T3 alone**. No formal Section 9 hit is declared based on 2 of 3 targets, preserving governance integrity.

---

## 6. Controlled Diagnostic Interpretation

Phase A provides strong evidence that the frozen Stage8.1 causal state contains nonlinear predictive information about future H7–H12 transmission statistics beyond deterministic solar/seasonal information. This is inconsistent with M1 (information absent) for the tested targets. Phase A does not by itself distinguish representation limitations from point-prediction/loss limitations or unresolved event timing; these remain hypotheses for subsequent diagnostic testing.
