# PHASE9 AUDIT CHECKPOINT

## Scope
Independent audit of the five supplied handoff files prior to any error forensics or candidate design.

## Verification: champion figure reproducibility
Recomputing Stage 8.1 (`HistGradientBoostingRegressor 37-feature`) daytime MAE directly from
`POLARIS_MODEL_HORIZON_ERROR_SUMMARY.csv` (horizon-weighted sum of abs. error / total daytime obs)
reproduces **36.188657 W/m²** exactly, matching the frozen operational champion figure in both the
`.md` and `.json` handoff files. Independently recomputing per-horizon MAE/bias directly from the raw
per-observation rows in `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv` (aggregated to daytime, by horizon)
reproduces the same per-horizon values reported in the horizon summary CSV to the 6th decimal. **The
champion metric is internally consistent across all three artifact layers (summary stat, horizon
breakdown, raw predictions).**

## Discrepancies found

### 1. `origin` key format is inconsistent across model families
- ORIGINAL (implicit assumption): `origin` is a shared, directly joinable key across all models in
  `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`.
- CORRECTED: Stage 8.1 (37-feature) encodes `origin` as a plain integer index (1–173). Stage 8.17A
  (40-feature) and Stage 8.19 (42-feature) encode `origin` as a full ISO datetime string. Foundation
  models (Chronos/TimesFM/Moirai/Persistence) and Stage 3C/4.3 encode `origin` as a `YYYY-MM-DD` date
  string. All are equivalent in *meaning* (forecast-day start) but incompatible in *format* — a naive
  merge on `origin` silently fails/misaligns.
- WHY THIS MATTERS: Phase 4/5 (model forensics, complementarity) require row-level joins across models.
- SOURCE: raw rows compared across `model_version` groups; fixed here by deriving a canonical `date` key
  from the `timestamp` column for every model and re-verifying that all 10 models share identical ground
  truth (`actual`) at every (date, horizon) — confirmed, cross-model actual std ≈ 9e-6 (float noise only).

### 2. Bulk timestamp parsing fails silently unless format is treated as mixed
- ORIGINAL: `timestamp` column appears uniformly parseable.
- CORRECTED: some artifact sources use `2024-01-21 00:00:00+00:00` and others use
  `2024-01-21T00:00:00Z`. A single `pd.to_datetime(..., utc=True)` call across the full file returns
  `NaT` for 9 of 10 models (all but Stage 8.1) unless `format='mixed'` is specified. This would have
  silently produced empty/garbage joins in any downstream script that didn't check for `NaT`.
- WHY THIS MATTERS: Same as above — a real reproducibility hazard.
- SOURCE: `timestamp` column, per-`model_version` inspection.

### 3. Foundation-model / Stage 3C / Stage 4.3 "347 origins" label does not match actual origin count
- ORIGINAL: `evaluation_split` label "Full 347 origins" for Chronos/TimesFM/Moirai/Persistence implies
  evaluation on the official 347-origin benchmark set.
- CORRECTED: these five models actually contain **365 unique origins** (a full calendar year,
  2024-01-02 through 2024-12-31), not 347. Stage 3C / Stage 4.3 ("347 origins (8,328 horizon tuples)")
  do correctly contain 347 unique origins. This means the aggregate metrics reported for
  Chronos/TimesFM/Moirai/Persistence in `POLARIS_MODEL_COMPARISON_MATRIX.csv` (e.g. 42.94% nMAE for
  Chronos2_ZeroShot_Raw) are computed over a different, larger origin set than the official
  benchmark protocol, and are **not directly comparable** to Stage 8.1's 173-origin ODD figure without
  restricting to matching dates first.
- WHY THIS MATTERS: Any Phase 4/5 "which model is best" comparison must restrict all models to the same
  173 ODD dates before comparing, or the comparison is confounded by a different (and non-overlapping)
  evaluation calendar.
- SOURCE: `evaluation_split` label vs. `origin.nunique()` per `model_version`.
- ACTION TAKEN: all Phase 3–5 forensics in this session restrict every model to the 173 dates used for
  the official Stage 8.1 ODD evaluation (verified via shared ground-truth `actual` values), so the
  comparisons in the following checkpoint are apples-to-apples.

### 4. Confirms two corrections already present in the historical record (no new issue)
- Stage 8.19's "27.0081% nMAE" claim is correctly marked `INVALIDATED_HISTORICAL_CLAIM` in the
  comparison matrix, consistent with the `expunged_invalid_claims` entry in the JSON (synthetic
  `np.random.seed(819)` ZTD fallback).
- Stage 8.24's 27.32% figure is explicitly labeled EVEN-only (`odd_run=False`) in the matrix, so it is
  correctly *not* being compared apples-to-apples against the ODD-based champion number.

## Conclusion
No corruption of the champion result was found. The real risk is in the model-comparison layer: three
separate formatting/labeling inconsistencies would cause a naive Phase 4/5 analysis to silently compare
mismatched populations or fail joins outright. All three have been corrected for in this session by
deriving a canonical date key and restricting every model to the verified 173 ODD dates before any
cross-model statistic is computed.

**Status: AUDIT COMPLETE. Proceeding to Phase 3–5 on the corrected, aligned dataset.**
