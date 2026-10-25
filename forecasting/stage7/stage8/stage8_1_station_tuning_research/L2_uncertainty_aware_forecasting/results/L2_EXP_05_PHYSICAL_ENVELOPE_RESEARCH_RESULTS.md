# POLARIS L2-EXP-05 — Physical Uncertainty Envelope Research Results

**Execution Timestamp**: 2026-10-04 05:43:57 UTC  
**Scientific Causal Decision**: **FORMULATION-SUPPORTED-NUMERIC-BOUND-UNRESOLVED**  
**Overall Status**: **PASS**  

---

## 1. Central Research Question & Definitive Finding

> **Central Question**: *"What physical upper-envelope formulation can constrain the calibrated SKGBDT+CQR interval without reproducing the demonstrated failure of the existing U = 1.25 * clearsky_ghi bound?"*

### Definitive Scientific Disposition: **FORMULATION-SUPPORTED-NUMERIC-BOUND-UNRESOLVED**

1. **Multiplicative Bound Definitively Refuted**: The multiplicative clear-sky formulation ($U = k \times \text{clearsky\_ghi}$) is fundamentally incapable of bounding pyranometer irradiance near the horizon. At solar elevation $\le 1^\circ$, clear-sky GHI collapses towards zero (mean $0.12\text{ W/m}^2$), causing **100.00%** of actual pyranometer observations to exceed the bound.
2. **Physical Floor / Elevation-Aware Envelope Supported**: Formulations incorporating a non-zero background diffuse/scattered radiation envelope (Formulation B: $\max(k \cdot \text{cs}, F)$ or Formulation C: $k \cdot \text{cs} + D(\theta_{\text{elev}})$) are physically justified by persistent diffuse sky radiation, terrain reflection, and high-latitude twilight.
3. **Numeric Boundary Unresolved**: The reference value $80\text{ W/m}^2$ (used in L2-EXP-04) is strictly a research ablation reference. Because the Nuolja AWS station measures only total hemispherical GHI without direct/diffuse separation, setting a specific numerical production boundary cannot be justified from first principles without direct diffuse sensor measurements.

## 2. Low-Sun Observational Envelope Across Elevation Bins (Historical 2020–2022, N=12,206)

| Elevation Bin | N | Mean Elev (°) | Mean Actual | Median Actual | 95th Pct | 99th Pct | Max Actual | Mean Clear-Sky | Actual > 1.25*cs (%) |
|---|---|---|---|---|---|---|---|---|---|
| **0-5 deg** | 2079 | 2.5° | 23.87 W/m² | 16.75 W/m² | 74.09 W/m² | 99.64 W/m² | 165.45 W/m² | 16.95 W/m² | **61.09%** |
| **>5-10 deg** | 1652 | 7.5° | 62.66 W/m² | 48.50 W/m² | 147.74 W/m² | 190.48 W/m² | 258.93 W/m² | 92.53 W/m² | **13.86%** |
| **>10-15 deg** | 1600 | 12.5° | 102.25 W/m² | 86.16 W/m² | 230.15 W/m² | 274.38 W/m² | 364.40 W/m² | 182.65 W/m² | **5.62%** |
| **>15-20 deg** | 1459 | 17.4° | 155.50 W/m² | 133.03 W/m² | 322.12 W/m² | 374.09 W/m² | 429.43 W/m² | 271.19 W/m² | **3.36%** |
| **>20 deg** | 5416 | 31.4° | 327.82 W/m² | 297.86 W/m² | 673.15 W/m² | 729.42 W/m² | 910.17 W/m² | 509.09 W/m² | **0.72%** |

## 3. Horizon Collapse Gradient (0° to >30°)

| Elevation Slice | N | Mean Elev | Mean Actual | 95th Pct Actual | Mean Clear-Sky | Mean 1.25*cs Bound | Actual > Bound (%) |
|---|---|---|---|---|---|---|---|
| **0-1 deg** | 413 | 0.49° | 11.01 W/m² | 30.06 W/m² | 0.12 W/m² | 0.15 W/m² | **100.00%** |
| **1-2 deg** | 418 | 1.50° | 15.64 W/m² | 43.28 W/m² | 3.52 W/m² | 4.40 W/m² | **91.15%** |
| **2-3 deg** | 455 | 2.50° | 23.43 W/m² | 61.20 W/m² | 13.13 W/m² | 16.42 W/m² | **56.48%** |
| **3-4 deg** | 368 | 3.50° | 28.73 W/m² | 77.18 W/m² | 26.47 W/m² | 33.09 W/m² | **27.72%** |
| **4-5 deg** | 425 | 4.54° | 40.73 W/m² | 95.78 W/m² | 42.35 W/m² | 52.94 W/m² | **27.53%** |
| **5-10 deg** | 1652 | 7.48° | 62.66 W/m² | 147.74 W/m² | 92.53 W/m² | 115.66 W/m² | **13.86%** |
| **10-15 deg** | 1600 | 12.50° | 102.25 W/m² | 230.15 W/m² | 182.65 W/m² | 228.31 W/m² | **5.62%** |
| **15-20 deg** | 1459 | 17.39° | 155.50 W/m² | 322.12 W/m² | 271.19 W/m² | 338.99 W/m² | **3.36%** |
| **20-30 deg** | 2486 | 24.75° | 237.75 W/m² | 480.91 W/m² | 400.62 W/m² | 500.77 W/m² | **1.21%** |
| **>30 deg** | 2930 | 37.13° | 404.23 W/m² | 699.59 W/m² | 601.13 W/m² | 751.41 W/m² | **0.31%** |

## 4. Candidate Envelope Formulation Comparison

| ID | Formulation Class | Mathematical Definition | Horizon Asymptotics | Low-Sun Violations (Dev / Val / Blind) | SKGBDT Blind PICP | Scientific Defensibility |
|---|---|---|---|---|---|---|
| **A** | Multiplicative Clear-Sky Bound | `U = 1.25 * clearsky_ghi` | Enforces U -> 0 as elev -> 0. Fails... | 29.7% / 30.1% / 31.3% | **70.05%** | **REFUTED** |
| **B** | Clear-Sky + Positive Floor | `U = max(1.25 * clearsky_ghi, 80.0)` | Maintains positive floor as elev ->... | 7.4% / 7.4% / 10.1% | **77.70%** | **FORMULATION-SUPPORTED** |
| **C** | Elevation-Aware Continuous Envelope | `U = 1.25 * clearsky_ghi + 80.0 * exp(-elev / 10.0)` | Continuous decay from horizon diffu... | 2.1% / 1.9% / 4.6% | **79.17%** | **FORMULATION-SUPPORTED** |
| **D** | Empirical Historical Regime Envelope | `U = Q_0.99(actual | elev_bin)` | Step-function empirical upper quant... | 1.0% / 1.3% / 3.0% | **79.55%** | **INSUFFICIENT** |
