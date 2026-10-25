# POLARIS — PHASE A + PHASE B + PHASE C-1 SCIENTIFIC SYNTHESIS CHECKPOINT

**Date (UTC):** 2026-09-16 00:43:17+0000  
**Governance Status:** CONSOLIDATED SCIENTIFIC SYNTHESIS CHECKPOINT  
**Phase C-1 Status:** COMPLETE AND CLOSED  
**Phase C-2 Status:** NOT AUTHORIZED  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Executive Purpose & Governance Record

This document provides the consolidated, forensically audited scientific synthesis checkpoint spanning **Phase A** (Information Probe), **Phase B** (Local Causal-State Diagnostics), and **Phase C-1** (Horizon-Decomposed Transmission Diagnostic).

- **Phase A:** COMPLETE + FORENSICALLY AUDITED  
- **Phase B:** COMPLETE + FORENSICALLY AUDITED  
- **Phase C-1:** COMPLETE + FORENSICALLY AUDITED (Authoritative Corrected Execution)  
- **T4 Target:** DROPPED / UNAVAILABLE  
- **Section 9 Decision Rule:** ORIGINAL 2-OF-4 RULE UNCHANGED  
- **ODD Firewall:** SEALED (0 rows accessed)  
- **Phase C-2 Authorization:** NOT AUTHORIZED  

---

## 2. Phase A — Established Findings

Phase A evaluated the incremental predictive information in the frozen Stage8.1 causal state $P1$ (147 features) vs deterministic astronomical state $P0$ (22 features) across 104 eligible EVEN origins.

- **T1 (Volatility):** GBDT $\Delta R^2 = +0.3098$, 95% CI `[+0.0506, +0.5886]`, $p < 0.0001$
- **T2 (Max Transition):** GBDT $\Delta R^2 = +0.3052$, 95% CI `[+0.0470, +0.5837]`, $p < 0.0001$
- **T3 (Mean Transmission):** GBDT $\Delta R^2 = +0.5988$, 95% CI `[+0.3639, +0.8421]`, $p < 0.0001$

> **Established Finding:** *M1 (information absent) is inconsistent with the tested aggregate targets. The frozen Stage8.1 causal state contains nonlinear predictive information about future H7–H12 transmission statistics beyond P0.*

---

## 3. Phase B — Established Findings & Limitations

- **B1 Rank Diagnostic:** Champion forecasts concentrate near the local 5-neighbour ensemble median (mean normalized rank $0.4459$, raw $2.2219/5$). Descriptively compatible with central positioning.
- **B2 Pinball Loss:** Champion $q=0.5$ loss ($0.1058$) is lower than crude 5-neighbour empirical median loss ($0.1267$, $\Delta = +0.0209$, reported $p < 0.0001$).
  - *Dependence Caveat:* Reported $p < 0.0001$ treated 604 hourly observations as independent without origin-level clustering.
- **B3 Procedural Limitation:** B3 threshold was NOT frozen before computation. B3 is procedurally compromised and remains exploratory only.

---

## 4. Phase C-1 — Horizon-Decomposed Transmission Diagnostic

- **Initial Execution:** Invalidated due to canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved as historical invalid artifact (`PHASE_C1_HORIZON_DIAGNOSTIC.json`).
- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with PASS status.
- **Population:** 104 parent origins, 609 aggregate valid target cells (H7: 89 valid; H8–H12: 104 valid each; 15 omitted cells at H7).

### Authoritative Horizon Results Table

| Horizon | Target | Valid $N_h$ | Ridge $\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | $k_{t+7}$ | 89 | — | — | — | **+0.5146** | [+0.2639, +0.7858] | 0.0010 |
| H8 | $k_{t+8}$ | 104 | — | — | — | **+0.5317** | [+0.3024, +0.7740] | 0.0010 |
| H9 | $k_{t+9}$ | 104 | — | — | — | **+0.7013** | [+0.4795, +0.9302] | 0.0010 |
| H10 | $k_{t+10}$ | 104 | — | — | — | **+0.4718** | [+0.2216, +0.7408] | 0.0010 |
| H11 | $k_{t+11}$ | 104 | — | — | — | **+0.6373** | [+0.3904, +0.8996] | 0.0010 |
| H12 | $k_{t+12}$ | 104 | — | — | — | **+0.3037** | [+0.0276, +0.5850] | 0.0010 |

> **Controlled Interpretation:** *Across all six H7–H12 horizons, the specified GBDT probe extracted positive incremental out-of-fold predictive information from P1 relative to P0 (ΔR² from +0.3037 to +0.7013, all 95% CIs exclude 0, permutation p = 0.0010). This demonstrates that P1 contains information extractable by the GBDT probe for individual hourly targets. It does NOT establish that the Stage8.1 representation itself is inadequate, because GBDT and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure.*

---

## 5. Demonstrated / Supported / Not Established Hierarchy

### A. DEMONSTRATED
- P1 contains substantial nonlinear predictive information about aggregate targets T1-T3 (Phase A).
- M1 (information absent) is inconsistent with tested aggregate targets (Phase A) and individual hourly transmission targets k(t+h) (Phase C-1).
- The champion point forecasts have a mean normalized rank of 0.4459 within tested five-neighbour ensembles (Phase B).
- Champion q=.5 pinball loss (0.1058) is lower than crude 5-neighbour empirical median loss (0.1267) (Phase B).
- GBDT probes achieve positive out-of-fold incremental predictive power (ΔR² from +0.3037 to +0.7013) for individual hourly targets k(t+7) to k(t+12) relative to P0 (Phase C-1).

### B. SUPPORTED / CONSISTENT WITH
- Phase B diagnostics are consistent with conditional-median/hedging behavior.
- The Ridge vs GBDT contrast is consistent with nonlinear information structure, but does not establish inherent physical nonlinearity.

### C. NOT ESTABLISHED
- Stage8.1 representation limitation (M2 is not established by C-1 due to model-class, loss, and capacity confounders).
- M3 point-loss / uncertainty limitation (not established by C-1).
- Event-timing uncertainty as a sole mechanism (not established by C-1).
- Any unique mechanism explaining Stage8.1 hourly point forecast error.
- Any ODD performance implication.

---

PHASE A + PHASE B + PHASE C-1 SYNTHESIS CHECKPOINT COMPLETE.
NO SECONDARY ANALYSIS AUTHORIZED.
ODD REMAINS SEALED.
