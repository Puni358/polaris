# POLARIS — PHASE C-1 CORRECTED HORIZON DIAGNOSTIC REPORT

**Date (UTC):** 2026-09-16 00:36:46+0000  
**Governance Status:** FORENSICALLY AUDITED CORRECTED PHASE C-1 DIAGNOSTIC RESULT  
**ODD Status:** SEALED (0 rows accessed)  
**Forensic Note:** Initial Phase C-1 execution invalidated due to canonical fold indexing defect; corrected execution authorized after forensic reconciliation.  

---

## 1. Population & Fold Accounting

- **Parent Phase-A-Eligible Origins:** 104
- **Theoretical Maximum Target Cells:** 624
- **Aggregate Valid Target Cells:** 609
- **Total Omitted Cells:** 15
- **Target Imputation:** Zero imputation performed. Invalid cells omitted per horizon.

### Horizon × Canonical Fold Breakdown (Folds 1–5)

| Horizon | Target | Parent Origins | Valid $N_h$ | Omitted Cells | Fold 1 Val | Fold 2 Val | Fold 3 Val | Fold 4 Val | Fold 5 Val | Sum |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | $k_{t+7}$ | 104 | 89 | 15 | 18 | 17 | 18 | 18 | 18 | **89** |
| H8 | $k_{t+8}$ | 104 | 104 | 0 | 21 | 21 | 21 | 20 | 21 | **104** |
| H9 | $k_{t+9}$ | 104 | 104 | 0 | 21 | 21 | 21 | 20 | 21 | **104** |
| H10 | $k_{t+10}$ | 104 | 104 | 0 | 21 | 21 | 21 | 20 | 21 | **104** |
| H11 | $k_{t+11}$ | 104 | 104 | 0 | 21 | 21 | 21 | 20 | 21 | **104** |
| H12 | $k_{t+12}$ | 104 | 104 | 0 | 21 | 21 | 21 | 20 | 21 | **104** |

---

## 2. Quantitative Diagnostic Results

| Horizon | Ridge $P0$ $R^2$ | Ridge $P1$ $R^2$ | Ridge $\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | 0.0371 | -0.6994 | -0.7366 | -0.0135 | 0.5011 | **+0.5146** | [+0.2639, +0.7858] | 0.0010 |
| H8 | -0.0205 | -0.4514 | -0.4308 | -0.1841 | 0.3477 | **+0.5317** | [+0.3024, +0.7740] | 0.0010 |
| H9 | -0.0122 | -0.2606 | -0.2484 | -0.2226 | 0.4787 | **+0.7013** | [+0.4795, +0.9302] | 0.0010 |
| H10 | 0.0177 | -0.3317 | -0.3494 | -0.1125 | 0.3593 | **+0.4718** | [+0.2216, +0.7408] | 0.0010 |
| H11 | -0.0233 | -0.2962 | -0.2729 | -0.2039 | 0.4334 | **+0.6373** | [+0.3904, +0.8996] | 0.0010 |
| H12 | -0.0500 | -0.4832 | -0.4332 | -0.0522 | 0.2515 | **+0.3037** | [+0.0276, +0.5850] | 0.0010 |

---

## 3. Controlled Scientific Interpretation

> "GBDT probes show horizon-specific incremental out-of-fold predictive power, with uncertainty quantified by the prespecified origin-level bootstrap confidence interval and within-month permutation procedure. Successful GBDT extraction of horizon-specific information demonstrates that the specified probe can extract information from P1. It does not establish that Stage8.1 has a representation limitation, because GBDT and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure."

### Demonstrated / Supported / Not Established Hierarchy

- **DEMONSTRATED:** GBDT probes achieve positive out-of-fold incremental predictive power ($\Delta R^2$) for individual hourly targets $k_{t+h}$ relative to $P0$.
- **SUPPORTED / CONSISTENT WITH:** Descriptive patterns in the horizon distribution of $\Delta R^2$.
- **NOT ESTABLISHED:** M2 representation limitation; M3 point-loss / uncertainty limitation; Event-timing uncertainty; Any unique mechanism explaining Stage8.1 point-error behavior; Any ODD performance implication.

---

CORRECTED PHASE C-1 DIAGNOSTIC COMPLETE.
NO ODD DATA ACCESSED.
ODD REMAINS SEALED.
