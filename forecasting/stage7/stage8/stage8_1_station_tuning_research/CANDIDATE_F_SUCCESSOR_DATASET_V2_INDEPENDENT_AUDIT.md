# Candidate F Successor Dataset v2 — Independent Audit

**Date:** 2026-10-12. **Nature:** independent, read-only re-verification of `dataset_v2/`, performed fresh (not reusing `build_dataset_v2.py`'s own in-process state) against the raw caches and base matrices. No dataset, cache, contract, or governance file was modified.

## 1. Hash recomputation — **ALL MATCH**

| File | Recorded | Recomputed | Status |
|---|---|---|---|
| `train.csv` | `7f2435fe5b2b239c...` | identical | MATCH |
| `validation.csv` | `24e6828ee7cb7d45...` | identical | MATCH |
| `blind.csv` | `7563669248b90640...` | identical | MATCH |
| `split_manifest.csv` | `d6c053aadddcc95f...` | identical | MATCH |

## 2. Origin/row counts, split exclusivity, frozen split definitions

- Counts: train 174 origins/4,176 rows; validation 173/4,152; blind 364/8,736 — **exactly matches protocol expectation.**
- **Zero** pairwise origin overlap between any two partitions.
- Union of all three partitions' origins == the independently recomputed 711-origin planned inventory — **exact match.**
- `train` origins == base matrix's own `EVEN`-labeled origins; `validation` origins == base matrix's own `ODD`-labeled origins — **exact match**, confirming the frozen split was reused verbatim, not recomputed differently.
- `split_manifest.csv`'s partition assignment matches the dataset files' actual partition membership exactly, for all three partitions.

## 3/4/5. Independent 24-horizon join re-verification, derived-feature checks, timestamp alignment, label/contamination exclusion, duplicates, spot-trace

- **Fresh reload of both raw caches** (not the build script's cached lookup): 711 lead-6 records, 16,353 lead-7..30-mapped entries (`711×23`, matching the expected v2 mapping exactly).
- **All 17,064 rows** in the assembled dataset re-checked against these freshly-reloaded raw values: **0 mismatches.**
- `lwp_x_cloud_18z == lwp_18z_fc × cloud_frac`: **0 mismatches**, all 17,064 rows.
- `elevation_x_cloud_frac == solar_elevation × cloud_frac`: **0 mismatches**, all 17,064 rows.
- Timestamp/target alignment (`timestamp == origin+(horizon_hour−1)`): **0 mismatches**, all 17,064 rows.
- `actual_SW_IN` confirmed present as the label column only (not among the 33 features).
- All 7 excluded columns (`lwp_latest`, `iwp_latest`, `lwp_x_cloud`, `pred_stage3b_cloud_nwp`, `phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`) confirmed **absent** from the dataset.
- Feature count: **33**, including all 4 new causal features (`lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z`, `elevation_x_cloud_frac`).
- Duplicate `(forecast_start, horizon_hour)` keys: **0** in all three partitions.
- **Random 5-row spot-trace, each traced directly to its exact source cache JSON file by independently recomputed `cache_key`:** all 5 **MATCH** (2024-09-30/h22, 2024-12-04/h7, 2025-08-19/h11, 2025-12-15/h6, 2025-07-26/h21) — covering both the lead-6 path (h=1 not sampled but separately verified in bulk above) and the lead-7..30 path, both years, no cross-origin or cross-horizon mixing detected.

## Finding: pre-existing missing values in `u700`/`v700` (not a build defect)

The audit's finite/missing-value check found non-zero `NaN` counts: 1,740 cells in `train.csv`, 1,730 in `validation.csv`, 3,640 in `blind.csv` — all located in exactly two columns, `u700` and `v700` (870/865/1,820 rows respectively, both columns missing together on the same rows).

**Traced to source and confirmed pre-existing:** the identical counts (1,735 for all of 2024, 1,820 for all of 2025) are present in the **original, frozen** `stage8_1_full_37_feature_matrix_{2024,2025}_CORRECTED.csv` files, independently verified by reading those files directly — this dataset build inherited them unchanged; it did not introduce, hide, or fabricate them. **Precisely characterized here for the first time in this investigation:** every affected row has `horizon_hour ∈ {20, 21, 22, 23, 24}` — exactly 5 of 24 horizons, for every one of the 347 (2024) origins, with an identical pattern implied for 2025. This matches the known lead-restriction convention (`horizon_hour 1–19` populated, `20–24` not) documented earlier in this investigation for a related wind700/u700/v700 extraction script. This is a **real, pre-existing limitation of the frozen base matrix**, now precisely documented, not a defect of `dataset_v2`'s own construction.

## 6. Historical operational publication-time availability

**Not established by this dataset or its provenance, and not claimed to be.** All records in both caches were fetched from the live MET Norway archive in 2026; successful retrieval today does not establish that the same data was operationally available at the historical forecast-origin decision cutoff (2024/2025). This limitation is carried forward unchanged from every prior report in this investigation and is explicitly preserved here, not resolved.

## 7. Verdict

**`AUDIT_PASS`**, with one documented pre-existing data-quality note (not a build defect): `u700`/`v700` are missing for `horizon_hour 20–24` in every origin, inherited unchanged from the frozen base matrix. No discrepancy was found in hashes, counts, split definitions, the 24-horizon join (fully re-verified independently against fresh cache reads for all 17,064 rows), derived-feature formulas, timestamp alignment, label/contamination exclusion, or duplicate keys.

## Governance and scope confirmation

No dataset file, cache, frozen base matrix, frozen Candidate F model, contract (v1 or v2), or governance record was modified. No training, evaluation, benchmarking, experiment, planner/controller, or Arm B activity occurred. No network request was made during this audit (all checks were performed against already-local files). `winner: null` is unchanged. Training on this dataset requires its own, separate, explicit authorization — none is implied by this audit passing.
