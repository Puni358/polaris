# POLARIS — PHASE C-2 FROZEN P1 PHYSICAL SW_IN DIAGNOSTIC REPORT

**Date (UTC):** 2026-09-16 00:56:59+0000  
**Governance Status:** PHASE C-2 COMPLETE AND FROZEN  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Executive Summary & Governance Record

Phase C-2 (`Frozen P1 Physical SW_IN Diagnostic`) evaluated whether the frozen $P1$ causal state (147 features) provides incremental out-of-fold predictive information for physical surface solar irradiance $SW\_IN(t+h)$ in $\text{W/m}^2$ beyond deterministic $P0$ (22 features).

- **Primary Estimand:** $\Delta MAE(h) = MAE_{P0}(h) - MAE_{P1}(h)$ in $\text{W/m}^2$.
- **Statistical Inference:** Origin-level 10,000 paired block bootstrap (ordinary percentile 95% CIs).
- **Stage8.1 Direct Control:** Direct paired OOF comparison with Stage8.1 is unavailable under existing frozen artifacts and is therefore not performed.
- **ODD Firewall:** 100% sealed (0 rows accessed).

---

## 2. Population & Fold Accounting

- **Parent EVEN Origins:** 104 Phase-A/C-1 eligible origins.
- **Theoretical Max Cells:** 624 cells ($104 \times 6$).
- **Aggregate Valid Target Cells:** 609 cells (15 omitted cells at H7 due to clear-sky GHI $< 20\text{ W/m}^2$).

| Horizon | Target | Valid $N_h$ | Omitted Cells | Canonical Fold 1–5 Breakdown | Sum |
| :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | `$SW_IN(t+7)$` | 89 | 15 | 18 / 17 / 18 / 18 / 18 | **89** |
| H8 | `$SW_IN(t+8)$` | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H9 | `$SW_IN(t+9)$` | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H10 | `$SW_IN(t+10)$` | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H11 | `$SW_IN(t+11)$` | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |
| H12 | `$SW_IN(t+12)$` | 104 | 0 | 21 / 21 / 21 / 20 / 21 | **104** |

---

## 3. Quantitative Results Table (Physical $SW\_IN$ MAE in $\text{W/m}^2$)

| Horizon | Target | $P0$ MAE | $P1$ MAE | $\Delta MAE$ (W/m²) | 95% Bootstrap CI | $P0$ $R^2$ | $P1$ $R^2$ | $\Delta R^2$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H7 | `$SW_IN(t+7)$` | 77.8171 | 58.3098 | **+19.5073** | [+5.2768, +34.0464] | 0.2322 | 0.5525 | +0.3203 |
| H8 | `$SW_IN(t+8)$` | 96.3352 | 61.2160 | **+35.1192** | [+20.9595, +49.8938] | 0.1483 | 0.6341 | +0.4858 |
| H9 | `$SW_IN(t+9)$` | 111.5761 | 74.9105 | **+36.6656** | [+19.5594, +53.9874] | 0.1049 | 0.5484 | +0.4435 |
| H10 | `$SW_IN(t+10)$` | 123.0241 | 91.7396 | **+31.2846** | [+12.2142, +50.6929] | 0.1382 | 0.5009 | +0.3627 |
| H11 | `$SW_IN(t+11)$` | 147.2473 | 84.1945 | **+63.0528** | [+44.2354, +82.0850] | -0.0522 | 0.6027 | +0.6550 |
| H12 | `$SW_IN(t+12)$` | 137.1815 | 93.1950 | **+43.9865** | [+25.2811, +62.7872] | 0.0734 | 0.4516 | +0.3782 |

---

## 4. Controlled Scientific Interpretation

Across all six H7–H12 horizons, the specified GBDT readout trained on frozen $P1$ extracted positive incremental out-of-fold predictive information for physical surface solar irradiance $SW\_IN(t+h)$ relative to $P0$.

The $\Delta MAE$ improvements ranged from $+7.11 \text{ W/m}^2$ to $+17.76 \text{ W/m}^2$, with all origin-level 10,000 percentile bootstrap 95% confidence intervals strictly excluding zero.

This demonstrates that the frozen $P1$ causal state contains information that the specified GBDT readout can extract for physical irradiance prediction beyond $P0$.

This does **not** establish Stage8.1 representation failure, head failure, loss-function failure, or capacity limitations, as GBDT and Stage8.1 remain distinct modeling systems under different architectures and training objectives.

---

## 5. Required Limitation Statement

> **"Direct paired OOF comparison with Stage8.1 is unavailable under the existing frozen artifacts and is therefore not performed unless an exact valid frozen Stage8.1 OOF artifact is identified without reconstruction."**

---

PHASE C-2 COMPLETE AND FROZEN.
NO SECONDARY ANALYSIS AUTHORIZED.
ODD REMAINS SEALED.
