# POLARIS — PHASE B HEDGING DIAGNOSTIC REPORT

**Date (UTC):** 2026-09-16  
**Scope:** Diagnostic evaluation of Hypothesis M3 (Hedging under conditional/bimodal future regimes)  
**Data Split:** EVEN origins only ($N=104$ eligible origins)  
**ODD Access:** ZERO ACCESS (Firewall confirmed)  
**JSON SHA-256:** `d376296878b42c0a7981e81550c7077caee81b478669594a7af0c89899b874ca`  

---

## 1. Executive Summary & Preserved Phase A Context

> **Preserved Phase A Mandatory Conclusion:**  
> "Phase A provides strong evidence that the frozen Stage8.1 causal state contains nonlinear predictive information about future H7–H12 transmission statistics beyond deterministic solar/seasonal information. This is inconsistent with M1 (information absent) for the tested targets. Phase A does not by itself distinguish representation limitations from point-prediction/loss limitations or unresolved event timing; these remain hypotheses for subsequent diagnostic testing."

**Controlled Phase B Summary:**  
Phase B provides diagnostic evidence consistent with conditional-median hedging in the tested local causal-state neighbourhoods: champion forecasts tend to occupy central positions within the five-neighbour empirical ensembles, while the neighbour-ensemble median does not outperform the champion under the $q=0.5$ pinball-loss comparison. The reported bimodality/high-spread diagnostic is also associated with elevated champion MAE. However, these results do not by themselves establish M3, because the five-neighbour empirical ensemble is a small local approximation and the diagnostics do not exclude representation limitations or unresolved event-timing uncertainty.

---

## 2. Methodology & Parameters

- **Population:** 104 eligible EVEN forecast origins from `INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv`.
- **Causal State:** 32-feature $t_0$ state vector extracted at $h=1$ from Stage 8.1 matrix, standardized on EVEN-only statistics.
- **Distance Metric:** Weighted Euclidean distance on standardized features; self-matches excluded ($i \ne j$).
- **Neighbourhood Size:** $k = 5$ nearest causal neighbours per origin.
- **Evaluated Horizons:** H7–H12 daytime hours (06:00–11:00 UTC, $\text{clearsky\_GHI} \ge 20\text{ W/m}^2$).
- **Total Hours Evaluated:** 604 daytime origin-hours.

---

## 3. Diagnostic Results

### B1 — Champion Forecast Position (PIT-Style Rank)
- **Mean Rank:** 2.2219 / 5.0 (Normalized: **0.4459**)
- **Median Rank:** 2.0
- **Rank Distribution (0 to 5):**
  - Rank 0 (below min neighbour): 63 (10.4%)
  - Rank 1: 117 (19.4%)
  - Rank 2: 173 (28.6%)
  - Rank 3: 152 (25.2%)
  - Rank 4: 72 (11.9%)
  - Rank 5 (above max neighbour): 27 (4.5%)

### B2 — Quantile $q=0.5$ Pinball Loss
- **Champion Point Forecast Loss:** 0.105774
- **Neighbour Ensemble Median Loss:** 0.126686
- **Pinball Loss Difference ($\text{Loss}_{\text{median}} - \text{Loss}_{\text{champ}}$):** +0.020912
- **Ensemble Median Win Rate (Descriptive):** 42.88% of hours
- **Statistical Significance:** Paired $t$-test $p = 0.000001$

### B3 — Bimodality & Conditional Error (Descriptive Only)
- **Bimodality Threshold:** Sarle's coefficient $B > 0.555$ or range $> 0.40$
- **Bimodal Hours:** 500 / 604 (**82.78%**)
- **Unimodal Hours:** 104 / 604 (17.22%)
- **Champion MAE on Bimodal Hours:** **0.2145**
- **Champion MAE on Unimodal Hours:** **0.1974**
- **MAE Elevation Ratio:** **1.09x**

---

## 4. Controlled Interpretation & Limitations

> Phase B provides diagnostic evidence consistent with conditional-median hedging in the tested local causal-state neighbourhoods: champion forecasts tend to occupy central positions within the five-neighbour empirical ensembles, while the neighbour-ensemble median does not outperform the champion under the q=0.5 pinball-loss comparison. The reported bimodality/high-spread diagnostic is also associated with elevated champion MAE. However, these results do not by themselves establish M3, because the five-neighbour empirical ensemble is a small local approximation and the diagnostics do not exclude representation limitations or unresolved event-timing uncertainty.
