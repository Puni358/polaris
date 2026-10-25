# POLARIS — PHASE C-1 HORIZON DIAGNOSTIC REPORT

**Date (UTC):** 2026-09-16 00:28:58+0000  
**Governance Status:** FORENSICALLY AUDITED PHASE C-1 DIAGNOSTIC RESULT  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Population & Fold Accounting

- **Parent Phase-A-Eligible Origins:** 104
- **Theoretical Maximum Target Cells:** 624
- **Aggregate Valid Target Cells:** 609
- **Total Omitted Cells:** 15
- **Target Imputation:** Zero imputation performed. Invalid cells omitted per horizon.

### Horizon × Fold Breakdown

| Horizon | Target | Parent Origins | Valid $N_h$ | Omitted Cells | Fold 0 Val | Fold 1 Val | Fold 2 Val | Fold 3 Val | Fold 4 Val |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | $k_{t+7}$ | 104 | 89 | 15 | 0 | 18 | 17 | 18 | 18 |
| H8 | $k_{t+8}$ | 104 | 104 | 0 | 0 | 21 | 21 | 21 | 20 |
| H9 | $k_{t+9}$ | 104 | 104 | 0 | 0 | 21 | 21 | 21 | 20 |
| H10 | $k_{t+10}$ | 104 | 104 | 0 | 0 | 21 | 21 | 21 | 20 |
| H11 | $k_{t+11}$ | 104 | 104 | 0 | 0 | 21 | 21 | 21 | 20 |
| H12 | $k_{t+12}$ | 104 | 104 | 0 | 0 | 21 | 21 | 21 | 20 |

---

## 2. Quantitative Diagnostic Results

| Horizon | Ridge $P0$ $R^2$ | Ridge $P1$ $R^2$ | Ridge $\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | -0.9794 | -1.1992 | -0.2198 | -1.0367 | -0.5702 | **+0.4665** | [+0.2460, +0.7083] | 0.0010 |
| H8 | -0.6927 | -1.0283 | -0.3356 | -0.7785 | -0.3560 | **+0.4224** | [+0.2259, +0.6383] | 0.0010 |
| H9 | -1.0623 | -1.3432 | -0.2809 | -1.2439 | -0.7177 | **+0.5262** | [+0.3062, +0.7485] | 0.0010 |
| H10 | -1.1604 | -1.5119 | -0.3515 | -1.3000 | -0.8959 | **+0.4041** | [+0.1732, +0.6618] | 0.0010 |
| H11 | -1.1109 | -1.3079 | -0.1970 | -1.2443 | -0.7637 | **+0.4806** | [+0.2437, +0.7262] | 0.0010 |
| H12 | -1.2566 | -1.5322 | -0.2756 | -1.2663 | -1.0126 | **+0.2537** | [-0.0069, +0.5130] | 0.0010 |

---

## 3. Controlled Scientific Interpretation

> "GBDT probes show horizon-specific incremental out-of-fold predictive power, with uncertainty quantified by the prespecified origin-level bootstrap confidence interval and within-month permutation procedure. Successful GBDT extraction of horizon-specific information demonstrates that the specified probe can extract information from P1. It does not establish that Stage8.1 has a representation limitation, because GBDT and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure."

### Demonstrated / Supported / Not Established Hierarchy

- **DEMONSTRATED:** GBDT probes achieve positive out-of-fold incremental predictive power ($\Delta R^2$) for individual hourly targets $k_{t+h}$ relative to $P0$.
- **SUPPORTED / CONSISTENT WITH:** Descriptive patterns in the horizon distribution of $\Delta R^2$.
- **NOT ESTABLISHED:** M2 representation limitation; M3 point-loss / uncertainty limitation; Event-timing uncertainty; Any unique mechanism explaining Stage8.1 point-error behavior; Any ODD performance implication.

---

PHASE C-1 DIAGNOSTIC COMPLETE.
NO ODD DATA ACCESSED.
ODD REMAINS SEALED.
