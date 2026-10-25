# POLARIS STAGE 8.24 — FAITHFUL OROGRAPHIC FLOW EVEN RESULTS REPORT

> [!CAUTION]
> **GOVERNANCE VERDICT: REJECTED_BY_EVEN_GATES**
> - **Experiment ID:** `POLARIS_STAGE8_24_FAITHFUL_OROGRAPHIC_GOVERNED_EXPERIMENT`
> - **Route Name:** Stage 8.24 Faithful Orographic Flow (`ctx_u_perp` + `ctx_mountain_froude`)
> - **Operational Champion Status:** **UNCHANGED (Stage 8.1 37-feature HGB champion preserved)**
> - **ODD Benchmark Dataset:** **100% UNTOUCHED (`ODD_RUN = FALSE`)**

---

## 1. Governed Experiment Identification & Protocol

- **Experiment Name:** Stage 8.24 — Faithful Scandes Orographic Flow-Regime Expansion
- **Candidate Features (2):** `ctx_u_perp` (Barrier-Normal Wind) + `ctx_mountain_froude` (Faithful Mountain Froude Number)
- **Validation Protocol:** 5-fold forward-chaining EVEN-only cross-validation on 173 locked EVEN origins.
- **ODD Firewall:** **ABSOLUTE FIREWALL MAINTAINED (Zero ODD access)**

---

## 2. Empirical EVEN Validation Performance Metrics

| Metric | Control (Stage 8.1, 37 features) | Candidate (39 features) | Delta |
| :--- | :---: | :---: | :---: |
| **MAE** | **37.5529 W/m²** | **37.8072 W/m²** | **+0.2543 W/m²** |
| **nMAE** | **27.1324%** | **27.3161%** | **+0.1837%** |
| **RMSE** | **76.9839 W/m²** | **77.4707 W/m²** | **+0.4869 W/m²** |
| **Bias** | **+5.6407 W/m²** | **+4.9987 W/m²** | **-0.6420 W/m²** |
| **Improving Folds** | — | **1 / 5 folds** | — |
| **Worst Fold Delta** | — | **+0.7186 W/m²** | — |

---

## 3. Fold-by-Fold Cross-Validation Breakdown

| Fold | Daytime N | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | 591 | 49.2812 | 49.4249 | +0.1438 | 29.5084% | 29.5945% |
| Fold 2 | 696 | 70.7021 | 70.5377 | -0.1644 | 36.9894% | 36.9034% |
| Fold 3 | 648 | 40.3225 | 41.0411 | +0.7186 | 28.1261% | 28.6274% |
| Fold 4 | 396 | 25.6368 | 26.1147 | +0.4780 | 36.5408% | 37.2220% |
| Fold 5 | 221 | 1.8218 | 1.9173 | +0.0955 | 50.6984% | 53.3566% |

---

## 4. Gate Audit Matrix (G1 – G6)

| Gate ID | Description | Required Threshold | Empirical Value | Status |
| :--- | :--- | :--- | :---: | :---: |
| **G1** | MAE Margin | $\Delta 	ext{MAE} \le -0.50	ext{ W/m}²$ | `+0.2543 W/m²` | **FAIL** |
| **G2** | Fold Consistency | $\ge 4 / 5	ext{ folds improve}$ | `1 / 5 folds` | **FAIL** |
| **G3** | Worst Fold Tolerance | Worst fold $\le +0.50	ext{ W/m}²$ | `+0.7186 W/m²` | **FAIL** |
| **G4** | nMAE & RMSE Non-Degradation | $	ext{nMAE} \le 	ext{ctrl} \land 	ext{RMSE} \le 	ext{ctrl}$ | nMAE: `27.3161%`, RMSE: `77.4707` | **FAIL** |
| **G5** | Causal Integrity | 100% causal features ($t_0 = 00:00	ext{ UTC}$) | 100% causal (173 origins) | **PASS** |
| **G6** | Control Reproduction | Exact Stage 8.1 control match | `37.5529 W/m²` | **PASS** |

---

## 5. Diagnostic N² Floor Activation Summary

- **Total Sublayers Evaluated:** 21694
- **Sublayers N² Floor Activations:** 0 (0.0%)
- **Total Origins Evaluated:** 347
- **Origins Affected by N² Floor:** 0 (0.0%)
- **N_layer Distribution (s⁻¹):**
  - Mean: `1.076341e-02`
  - Std: `2.849525e-04`
  - Min: `1.006799e-02`
  - Median: `1.080808e-02`
  - Max: `1.145097e-02`

---

## 6. Final Status & Verdict

```
REJECTED_BY_EVEN_GATES
```

*Report generated under POLARIS Stage 8 Governance Protocol on 2026-09-13T15:22:29.533035+00:00.*
