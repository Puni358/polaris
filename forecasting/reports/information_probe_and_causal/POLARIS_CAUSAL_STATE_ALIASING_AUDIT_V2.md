# POLARIS Causal State Aliasing Audit v2

**EVEN-only diagnostic; no fitting.** H1 timestamp equals `forecast_start` (= t0), but the prior audit was invalid to treat all H1 columns as automatically causal without provenance. This implementation uses only audited H1 atmospheric/context variables; H2–H24 fields, target, predictions, and deterministic solar trajectory are excluded from state matching.

## Pre-registered design

Stage A: same-month pool, then the 20 nearest deterministic clear-sky trajectories. Stage B: nearest atmospheric/context state within that pool. Three fixed sensitivity distances are reported in the JSON: standardized Euclidean, this solar-conditioned atmospheric distance, and rank-normalized distance. Clear-sky-normalized transmission is evaluated *after* matching, on pairwise daytime horizons with clear-sky GHI >20 W/m².

## Result

**No statistically defensible divergence-dominance horizon was identified.** The effect is NN transmission divergence minus the deterministic-solar matched random-pair null. Bootstrap resamples origin pairs (2,000, seed 12345); Benjamini–Hochberg FDR is across 24 horizons. This is association/conditional-uncertainty evidence only, never forecasting gain or proof of a ceiling.

| Horizon | Raw SW_IN MAE (W/m²) | Transmission MAE | Clear-sky residual MAE (W/m²) | Effect vs det-solar null | 95% CI | FDR q |
|---|---:|---:|---:|---:|---|---:|
| H01 | NA | NA | NA | NA | NA | 1.0000 |
| H02 | NA | NA | NA | NA | NA | 1.0000 |
| H03 | 32.571 | 0.4769 | 32.849 | -0.4662 | -0.7047, -0.1910 | 0.0120 |
| H04 | 46.936 | 0.6410 | 47.344 | 0.0514 | -0.0755, 0.1872 | 0.6169 |
| H05 | 71.364 | 0.6257 | 71.527 | -0.0601 | -0.1876, 0.0711 | 0.5488 |
| H06 | 86.326 | 0.5309 | 87.421 | -0.0885 | -0.1904, 0.0162 | 0.3090 |
| H07 | 111.055 | 0.4679 | 114.919 | -0.0678 | -0.1451, 0.0117 | 0.3051 |
| H08 | 110.039 | 0.3910 | 114.628 | -0.0659 | -0.1318, 0.0077 | 0.3051 |
| H09 | 121.421 | 0.4178 | 118.564 | -0.0603 | -0.1316, 0.0186 | 0.3360 |
| H10 | 139.723 | 0.3965 | 134.861 | -0.0364 | -0.0842, 0.0142 | 0.3469 |
| H11 | 153.576 | 0.3632 | 142.240 | -0.0717 | -0.1177, -0.0240 | 0.0120 |
| H12 | 147.784 | 0.3455 | 140.452 | -0.0025 | -0.0475, 0.0423 | 1.0000 |
| H13 | 124.738 | 0.2611 | 117.715 | -0.0300 | -0.0620, 0.0030 | 0.3051 |
| H14 | 117.954 | 0.2386 | 112.825 | -0.0551 | -0.0883, -0.0212 | 0.0240 |
| H15 | 113.819 | 0.2422 | 104.505 | -0.0166 | -0.0503, 0.0179 | 0.5488 |
| H16 | 96.034 | 0.2236 | 92.955 | -0.0240 | -0.0559, 0.0111 | 0.3660 |
| H17 | 53.591 | 0.1533 | 61.693 | -0.0020 | -0.0262, 0.0232 | 1.0000 |
| H18 | 40.201 | 0.1388 | 49.182 | -0.0236 | -0.0446, -0.0009 | 0.2580 |
| H19 | 26.361 | 0.1207 | 35.013 | -0.0162 | -0.0380, 0.0067 | 0.3469 |
| H20 | 21.817 | 0.1553 | 26.951 | 0.0202 | -0.0105, 0.0516 | 0.3785 |
| H21 | 15.071 | 0.1482 | 16.568 | 0.0134 | -0.0202, 0.0488 | 0.6169 |
| H22 | 15.091 | 0.3225 | 16.727 | 0.0670 | -0.0812, 0.2568 | 0.6693 |
| H23 | NA | NA | NA | NA | NA | 1.0000 |
| H24 | NA | NA | NA | NA | NA | 1.0000 |

## Causality and limits

The full per-feature causality table, all nulls, all three distance sensitivity results, high-solar exploratory subgroup, hashes, and origin-level error association are in the JSON artifact. High solar is the pre-registered top quartile of **peak H1–H24 clear-sky GHI**; it is diagnostic stratification only and never part of neighbour selection.
