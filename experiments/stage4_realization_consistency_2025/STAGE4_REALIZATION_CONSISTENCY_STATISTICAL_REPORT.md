# POLARIS Stage 4: Realization Consistency Statistical Report

**Experiment ID:** `EXP-STAGE4-REALIZATION-CONSISTENCY-2025`  
**Governing Contract:** `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md`  
**Date:** 2026-10-06  
**Methodology:**
- Paired origins ($N = 123$), sorted ascending.
- Two-sided Wilcoxon signed-rank test on paired diesel differences $\Delta_o = \text{Fuel}_{\text{Control},r}(o) - \text{Fuel}_{\text{cand},r}(o)$.
- Holm-Bonferroni correction across the 4 candidates per realization.
- BCa 95% bootstrap confidence intervals (10,000 resamples, random_state=42).

---

## 1. Candidate Statistical Diesel Gates: Realization A (Current)

*Control B (A) Total Fuel:* 6,096.90 L

| Candidate | Total Fuel (L) | Saving (L) | Saving (%) | Mean $\Delta_o$ (L) | BCa 95% CI (L) | Wilcoxon Raw $p$ | Holm Adj. $p$ | Diesel Gate |
|---|---|---|---|---|---|---|---|---|
| **Candidate S** | 4,687.69 | 1,409.21 | 23.11% | 11.46 | [8.50, 14.32] | $2.45 \times 10^{-10}$ | $7.36 \times 10^{-10}$ | **PASS** |
| **Candidate SW** | 3,768.55 | 2,328.35 | 38.19% | 18.93 | [15.87, 21.84] | $5.08 \times 10^{-17}$ | $2.03 \times 10^{-16}$ | **FAIL (Safety Gate 2)** |
| **Candidate S-L** | 5,280.24 | 816.66 | 13.39% | 6.64 | [4.31, 8.84] | $7.20 \times 10^{-7}$ | $1.44 \times 10^{-6}$ | **PASS** |
| **Candidate SW-L** | 5,263.96 | 832.94 | 13.66% | 6.77 | [4.38, 9.12] | $8.17 \times 10^{-7}$ | $1.44 \times 10^{-6}$ | **PASS** |

*Winner under Realization A:* **Candidate S** (highest saving among safety-qualified candidates: 23.11%).

---

## 2. Candidate Statistical Diesel Gates: Realization B (Plan-Consistent)

*Control B (B) Total Fuel:* 5,685.23 L

| Candidate | Total Fuel (L) | Saving (L) | Saving (%) | Mean $\Delta_o$ (L) | BCa 95% CI (L) | Wilcoxon Raw $p$ | Holm Adj. $p$ | Diesel Gate |
|---|---|---|---|---|---|---|---|---|
| **Candidate S** | 4,750.83 | 934.40 | 16.44% | 7.60 | [5.40, 9.75] | $1.98 \times 10^{-9}$ | $5.93 \times 10^{-9}$ | **PASS** |
| **Candidate SW** | 4,333.90 | 1,351.33 | 23.77% | 10.99 | [8.55, 13.46] | $4.11 \times 10^{-12}$ | $1.64 \times 10^{-11}$ | **PASS** |
| **Candidate S-L** | 5,229.27 | 455.96 | 8.02% | 3.71 | [1.78, 5.52] | $8.49 \times 10^{-5}$ | $1.70 \times 10^{-4}$ | **PASS** |
| **Candidate SW-L** | 5,318.57 | 366.66 | 6.45% | 2.98 | [1.03, 4.90] | $3.58 \times 10^{-3}$ | $3.58 \times 10^{-3}$ | **PASS** |

*Winner under Realization B:* **Candidate SW** (highest saving among safety-qualified candidates: 23.77%).

---

## 3. Paired Differences Across Realizations ($B_o - A_o$)

For each arm, evaluated over all $N = 123$ holdout origins:

| Arm | $\Delta$ Total Fuel (L) | Mean Diff (L) | BCa 95% CI (L) | Holm $p$ | $\Delta R_{\text{CF}}$ (pp) | BCa 95% CI (pp) | $\Delta R_P$ (pp) | BCa 95% CI (pp) |
|---|---|---|---|---|---|---|---|---|
| **Control B** | $-411.67$ | $-3.35$ | [$-5.16$, $-1.43$] | $1.53 \times 10^{-3}$ | $+0.2213$ | [$+0.0412$, $+0.4079$] | $-5.1945$ | [$-5.9612$, $-4.4641$] |
| **Candidate S** | $+63.14$ | $+0.51$ | [$-1.22$, $+2.21$] | $1.00 \times 10^{0}$ | $+0.1760$ | [$+0.0436$, $+0.3129$] | $-4.2635$ | [$-5.0210$, $-3.5226$] |
| **Candidate SW** | $+565.35$ | $+4.60$ | [$+2.66$, $+6.72$] | $1.22 \times 10^{-4}$ | $+0.2345$ | [$+0.0712$, $+0.4182$] | $-3.2910$ | [$-4.0921$, $-2.5184$] |
| **Candidate S-L** | $-50.97$ | $-0.41$ | [$-2.18$, $+1.34$] | $1.00 \times 10^{0}$ | $+0.2182$ | [$+0.0521$, $+0.3941$] | $-4.5175$ | [$-5.2741$, $-3.7712$] |
| **Candidate SW-L** | $+54.60$ | $+0.44$ | [$-0.94$, $+1.85$] | $1.00 \times 10^{0}$ | $+0.1639$ | [$+0.0381$, $+0.3015$] | $-4.6759$ | [$-5.4218$, $-3.9312$] |

---

## 4. Preregistered Decision Rule Evaluation

- Precedence:
  1. `BLOCKED` $\to$ Audit gates G1–G11 all passed.
  2. `SAFETY-CHANGING` $\to$ Candidate SW Gate 2 flipped from FAIL (under A) to PASS (under B).
  3. `RANKING-CHANGING` $\to$ Winner flipped from Candidate S (23.11%) to Candidate SW (23.77%).
  4. `SENSITIVE` $\to$ Multiple material saving and reliability differences exceed thresholds.
  5. `ROBUST` $\to$ Inapplicable.

**Final Classification:** **SAFETY-CHANGING**
