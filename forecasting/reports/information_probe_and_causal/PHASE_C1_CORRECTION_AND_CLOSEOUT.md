# POLARIS — PHASE C-1 CORRECTION AND CLOSEOUT REPORT

**Date (UTC):** 2026-09-16 00:43:17+0000  
**Governance Status:** PHASE C-1 OFFICIALLY CLOSED AND FROZEN  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Executive Summary & Governance Closure

Phase C-1 (`POLARIS Horizon-Decomposed Transmission Diagnostic`) is officially **COMPLETE AND CLOSED**.

- **Initial Execution:** Invalidated due to a canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved strictly as historical invalid artifacts (`PHASE_C1_HORIZON_DIAGNOSTIC.json` / `.md`).
- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with **PASS** status (`PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json` / `.md`).
- **ODD Firewall:** 100% sealed (0 rows accessed).
- **Secondary Analysis:** None authorized. Phase C-1 closes without triggering adaptive reruns or new feature/model sweeps.

---

## 2. Historical Record of Initial Execution Defect

- **Root Cause:** Canonical fold labels in `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` are 1-indexed (1, 2, 3, 4, 5). The initial script iterated over `0..4`.
- **Defect Impact:** Fold 0 was empty; Fold 5 (21 origins) was omitted from validation, leaked into training for Folds 1–4, and received unpredicted zero-filled placeholders.
- **Preservation Policy:** Initial invalid artifacts are retained for historical auditability and MUST NEVER be used as benchmarks, tuning references, or supporting evidence.

---

## 3. Authoritative Corrected Results & Accounting

### Population & Fold Accounting
- **Parent EVEN Origins:** 104 Phase-A-eligible origins.
- **Theoretical Max Cells:** 624 cells ($104 \times 6$).
- **Aggregate Valid Target Cells:** 609 cells (15 omitted cells at H7 due to clear-sky GHI $< 20\text{ W/m}^2$).

| Horizon | Target | Valid $N_h$ | Omitted Cells | Canonical Fold 1–5 Breakdown | Sum |
| :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | $k_{t+7}$ | 89 | 15 | 18 / 17 / 18 / 18 / 18 | **89** |
| H8 | $k_{t+8}$ | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H9 | $k_{t+9}$ | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H10 | $k_{t+10}$ | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H11 | $k_{t+11}$ | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H12 | $k_{t+12}$ | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |

---

### Quantitative Results Table

| Horizon | Ridge $\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | -0.7366 | — | — | **+0.5146** | [+0.2639, +0.7858] | 0.0010 |
| H8 | -0.4308 | — | — | **+0.5317** | [+0.3024, +0.7740] | 0.0010 |
| H9 | -0.2484 | — | — | **+0.7013** | [+0.4795, +0.9302] | 0.0010 |
| H10 | -0.3494 | — | — | **+0.4718** | [+0.2216, +0.7408] | 0.0010 |
| H11 | -0.2729 | — | — | **+0.6373** | [+0.3904, +0.8996] | 0.0010 |
| H12 | -0.4332 | — | — | **+0.3037** | [+0.0276, +0.5850] | 0.0010 |

---

## 4. Controlled Scientific Interpretation

> "Across all six H7–H12 horizons, the specified nonlinear GBDT probe extracted positive incremental out-of-fold predictive information from the frozen P1 causal state relative to P0. The GBDT ΔR² values ranged from +0.3037 to +0.7013, with the prespecified origin-level bootstrap 95% confidence intervals excluding zero at every horizon. The corresponding finite-sample within-month permutation p-values were 0.0010 at all six horizons.

> This demonstrates that the frozen P1 causal state contains information that the specified GBDT probe can extract for individual hourly transmission targets k(t+h) beyond the deterministic P0 state.

> This does NOT establish that the Stage8.1 representation itself is inadequate, because the GBDT probe and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure."

---

## 5. Hypothesis Ledger Summary

- **M1 (Information Absent):** DISFAVORED for tested hourly transmission targets.
- **M2 (Representation Limitation):** NOT ESTABLISHED BY C-1 (probe extraction does not prove architecture inadequacy).
- **M3 (Point-Loss / Uncertainty Limitation):** NOT ESTABLISHED BY C-1 (Phase B hedging diagnostics remain consistent, but C-1 does not independently test M3).
- **Event-Timing Uncertainty:** NOT ESTABLISHED BY C-1 (timing error not directly isolated).
- **ODD Performance:** UNKNOWN (sealed).

---

PHASE C-1 CORRECTION AND CLOSEOUT COMPLETE.
NO SECONDARY ANALYSIS AUTHORIZED.
ODD REMAINS SEALED.
