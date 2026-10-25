# Phase 1 — Error Forensics: Frozen Stage 8.1 CORRECTED Model, 2025 Blind Predictions

**Scope**: Read-only analysis of the frozen model's own already-computed 2025 blind
predictions and the frozen 2025 feature matrix. **No training. No modification of the
frozen artifact, freeze manifest, or production code.** Script:
[phase1_error_forensics.py](phase1_error_forensics.py) (SHA256 `77c2a11f...`). Raw results:
[ERROR_FORENSICS_RESULTS.json](ERROR_FORENSICS_RESULTS.json) (SHA256 `96336667...`).

**Input provenance, confirmed unchanged**: `stage8_1_CORRECTED_2025_blind_predictions.csv`
(SHA256 `65e0a0ac...`, matches the freeze doc's own recorded hash exactly) and
`stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` (SHA256 `9fe6b9f8...`, matches). Overall
daytime metrics reproduced exactly from these inputs (MAE 35.9745, RMSE 65.9427, bias
+4.0802, nMAE 28.2478% — identical to `FINAL_STAGE8_1_FORECASTING_FREEZE.md §5`), confirming
correct, uncorrupted data use before any further slicing.

---

## 1. Error by forecast horizon (H1–H24)

MAE grows with horizon length in absolute terms (H1=3.71 W/m² → H12=59.8 W/m², roughly) —
but this is **confounded with solar magnitude** (short horizons disproportionately fall in
low-sun hours by the 24h-ahead convention). The **largest absolute-error contributors by
horizon** (full table in the JSON) are **H12 (10.85% of total |error|), H13 (10.63%), H14
(9.97%), H11 (9.31%), H10 (8.81%)** — i.e. late-morning-to-early-afternoon horizons, which
coincide with peak solar magnitude, not necessarily with degraded relative accuracy at long
lead times per se.

## 2. Error by month/season

| Month | MAE | Bias | nMAE% |
|---|---|---|---|
| Jan | 2.23 | −1.65 | 50.5 |
| Feb | 10.60 | +1.61 | 28.4 |
| Mar | 24.45 | +0.35 | 22.4 |
| **Apr** | 37.51 | **−6.82** | 22.5 |
| May | 54.12 | +2.51 | 26.8 |
| Jun | 59.28 | +8.82 | 32.8 |
| Jul | 47.51 | +7.84 | 22.9 |
| **Aug** | 45.99 | **+10.75** | 35.5 |
| **Sep** | 37.74 | **+13.24** | 38.6 |
| Oct | 17.05 | +3.58 | 33.3 |
| Nov | 4.30 | −2.79 | 41.3 |
| Dec | 1.00 | −1.00 | 100.0 |

**Bias is positive (overprediction) in 8 of 12 months**, and grows to its two largest
positive values in **August (+10.75) and September (+13.24)** — late-summer/early-autumn,
the exact seasonal window the EMS actual-solar-replay investigation (separately, in the
EMS diagnostic branch) identified as containing the bulk of the realized-unmet-driving
origins (March–October spread, October a major contributor). April is the one month with a
large **negative** bias (−6.82, underprediction) — an asymmetric, non-obvious pattern.

## 3. Error by solar elevation

| Elevation bin | n | MAE | Bias | nMAE% | Share of total \|error\| |
|---|---|---|---|---|---|
| [0,5) | 940 | 7.90 | −1.49 | 38.2 | 3.45% |
| [5,10) | 652 | 18.08 | +1.10 | 32.1 | 5.48% |
| [10,20) | 1,049 | 37.40 | +6.53 | 30.3 | 18.24% |
| [20,30) | 827 | 66.51 | +9.29 | 29.0 | 25.58% |
| **[30,90)** | 978 | **100.93** | **+13.75** | 25.8 | **45.90%** |

**Bias increases monotonically with solar elevation, from −1.49 at the lowest elevations to
+13.75 at the highest** — a clean, systematic, monotonic relationship. **The highest-elevation
bucket alone accounts for 45.9% of all absolute error** — the single largest avoidable-error
regime identified in this forensics pass. This is also precisely the regime (peak-sun,
midday) that drives the largest absolute energy quantities in any EMS dispatch decision.

## 4. Error by cloud regime

| Regime | Cloud cover | n | MAE | Bias | nMAE% |
|---|---|---|---|---|---|
| Clear | [0,0.2) | 886 | 33.49 | +8.72 | **17.8** |
| Transition | [0.2,0.6) | 958 | 46.67 | **+12.74** | 27.7 |
| Cloudy | [0.6,1.01) | 4,134 | 34.03 | +1.08 | 32.5 |

**Transition (partly-cloudy) conditions show both the highest absolute MAE and the largest
positive bias** — the hardest regime to forecast, as expected (cloud-cover forecasts
themselves are least certain in transitional conditions). **Cloudy conditions show the
lowest bias (+1.08, nearly unbiased)** but the highest *relative* error (nMAE 32.5%,
reflecting the lower absolute magnitudes typical of cloudy sky).

## 5. Error by solar intensity (clear-sky GHI bucket)

| Clear-sky GHI bin | n | MAE | Bias | nMAE% |
|---|---|---|---|---|
| [0,50) | 2,549 | 4.43 | −1.81 | 43.8 |
| [50,150) | 749 | 20.41 | +1.45 | 32.6 |
| [150,300) | 839 | 38.21 | +7.58 | 30.0 |
| [300,1200) | 1,841 | 84.96 | +11.71 | 26.9 |

Consistent with the elevation finding: bias grows with intensity, absolute MAE grows with
intensity (expected, larger quantities → larger absolute errors), but *relative* error
(nMAE) actually **improves** at higher intensity — the model is directionally worst (most
overconfident upward) exactly where the raw Wh stakes are largest.

## 6. Residual predictability from forecast-time information

**R² = 0.4457** for a simple linear regression of `|error|` on
`[month, hour, solar_elevation, cloud_frac, clearsky_ghi, horizon_hour]` — all six features
**already available at forecast time and already present in the model's own 37-feature
input**. **44.6% of the variance in absolute error is linearly explainable from information
the model already has access to.** This does **not** by itself prove a materially better
model is easy to build (a linear probe on |error| is a diagnostic, not a model comparison),
but it is a clear, quantified signal that **systematic, forecast-time-knowable structure
remains in the current model's residuals** — directly motivating Phase 2's residual-correction
(Candidate D) and sample-weighting (Phase 3) experiments.

## 7. Largest sources of avoidable residual error — ranked

1. **High solar elevation (≥30°)**: 45.9% of total absolute error, systematic positive bias
   (+13.75 W/m²) that grows monotonically with elevation.
2. **Transition cloud regime**: highest absolute MAE (46.67) and highest bias (+12.74) of
   the three cloud regimes.
3. **Late summer / early autumn (Aug–Sep)**: the two largest positive-bias months, in the
   same seasonal window that drives the EMS realized-unmet problem.
4. **Mid-day horizons (H10–H14)**: largest horizon-bucketed absolute-error contributors,
   confounded with (not necessarily independent of) solar-magnitude effects.

**Overall direction, stated plainly**: the frozen model's dominant, systematic error mode is
**overprediction, concentrated at high solar elevation / high intensity / late-summer
conditions** — the same error *direction* (forecast too optimistic) already identified, via
an entirely separate investigation, as the proximate trigger for 100% of the realized
critical-load unmet hours in the EMS actual-solar-replay decomposition.

## STOP (Phase 1)

Forensics complete. No frozen artifact modified. All findings above are VERIFIED directly
from the frozen model's own recorded blind predictions and feature matrix, re-hashed and
confirmed unchanged before analysis.
