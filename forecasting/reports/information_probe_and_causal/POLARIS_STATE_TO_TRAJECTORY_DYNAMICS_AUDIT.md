# POLARIS State → Trajectory Dynamics Audit

## FINAL DIAGNOSIS

**Transition-dynamics limitation: C — WEAK / INCONCLUSIVE.** The frozen-control errors are associated with realised trajectory complexity, but this diagnostic does not establish a stable transition-timing/shape failure that justifies a sequence-model experiment. State-aliasing remains **C — weak/inconclusive** from v2.

## Governance status

- ODD accessed: NO
- Training performed: NO
- New predictive features: NO
- Existing champion modified: NO
- New data fetched: NO
- Rejected routes reopened: NO

## Pre-registered definitions

- Causal state: ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h, ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h, ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h, ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h, fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac, lwp_latest, iwp_latest, lwp_x_cloud, u700, v700
- Daytime transmission: `actual_SW_IN / clearsky_ghi` only where clear-sky GHI >20 W/m².
- Stable / major-change cutoffs (global EVEN realised daytime adjacent increments): Q25=0.0395; Q75=0.2246.
- High-complexity split: strict median split of the pre-specified standardized composite.

## Evidence

- Approved EVEN origins: 173. Usable daytime trajectories: 147; excluded because no daytime trajectory: 26. Major-transition origins: 130.
- Transition vs no-transition total daytime MAE difference: 22.79 W/m².
- Major-transition mean MAE: pre / during / post = 43.26 / 47.85 / 64.27 W/m².
- Median absolute detected timing error: 0.00 h (actual-defined event detector; missing prediction event is excluded from this timing summary).

## Horizon associations (Spearman; origin-level permutation, FDR across five pre-specified regimes)

| Regime | n | rho | permutation p | FDR q |
|---|---:|---:|---:|
| H1–H3 | 20 | 0.368 | 0.0985 | 0.1231 |
| H4–H6 | 72 | 0.304 | 0.0090 | 0.0150 |
| H7–H12 | 146 | 0.460 | 0.0005 | 0.0012 |
| H13–H18 | 147 | 0.326 | 0.0005 | 0.0012 |
| H19–H24 | 81 | 0.076 | 0.4913 | 0.4913 |

## Limits and decision

This is an association between realised future trajectory and error, not a causal effect or a forecast-improvement estimate. Future trajectory descriptors were not used as inputs. Target autocorrelation alone is not predictive opportunity. Because the pre-registered diagnostics do not demonstrate reproducible timing/phase dominance beyond amplitude and regime difficulty, the sequence-model route is **closed**; no model specification is proposed.

## Reproducibility

Input hashes, all origin-level metrics, bootstrap/permutation settings, definitions, and full results are in the companion JSON.
