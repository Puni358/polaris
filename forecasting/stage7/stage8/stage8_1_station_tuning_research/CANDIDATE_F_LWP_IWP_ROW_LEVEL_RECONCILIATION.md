# Candidate F LWP/IWP Row-Level Reconciliation (Read-Only, Decision-Gated)

**Date:** 2026-10-12. **Nature:** a bounded, read-only reconciliation attempt using only existing local artifacts, per explicit instruction not to initiate new bulk acquisition. This report is a new, separate document — it does not overwrite `TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md` or any prior report.

## 1. Files inspected (with SHA-256)

| File | SHA-256 |
|---|---|
| `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` | `da6585c3a584f742d4e78f2d5ac5323479a765bcf74bb8b6da31cf1336f600a8` |
| `stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv` | `4c8019a03658ca32ec330b7ee7b8b69de9a3959d3cf74065d54ab1a07b16ade8` |

Also inspected (no independent raw data found; see §3): `stage6/stage6_6_lwp_iwp/run_stage6_6.py`, `extraction_checkpoint.json`, `sample_lwp_iwp_extraction_benchmark.csv`, `independent_read_only_audit.py`, `stage6/stage6_6_lwp_iwp_2025/extraction_checkpoint.json`, `build_corrected_feature_matrix.py` (merge logic, re-confirmed, not re-hashed — already cited in the prior report).

## 2. Verification method and timestamp/index mapping (recap, not re-derived)

- `build_corrected_feature_matrix.py:125-126` joins `lwp_latest`/`iwp_latest` onto the base matrix strictly by `(forecast_start, horizon_hour)` label — never by `timestamp`/`valid_time`.
- Base matrix `timestamp` convention: `horizon_hour=h → timestamp = forecast_start + (h−1)` hours (established in the prior report).
- Stage 6.6's own `valid_time` convention: `horizon_hour=h → valid_time = forecast_start + h` hours (`run_stage6_6.py`'s `h = h_idx+1; valid_time = origin+h`).
- Confirmed in the immediately preceding task (single bounded live query, not repeated here): `time[0] == forecast_reference_time` for both an 18Z and a 00Z `meps_det_pl` file — array index 0 is lead-hour 0, valid at the run's own init instant.

## 3. What could and could not be independently derived from local artifacts

**Could not be done:** independently recomputing the expected LWP/IWP value for any of the 711×24 = 17,064 `(forecast_start, horizon_hour)` rows requires the raw MEPS `mass_fraction_of_cloud_condensed_water_in_air_pl`/`...ice...` vertical profile arrays (and `surface_air_pressure`) for each of the 711 same-day 00Z runs, run through the existing `compute_surface_aware_lwp_iwp` function. **No such raw response (NetCDF or DODS-ASCII) was retained anywhere locally** — confirmed by searching `stage6_6_lwp_iwp/` and `stage6_6_lwp_iwp_2025/` for any `.nc`/`.ascii`/cache file (none found); `extraction_checkpoint.json` retains only per-origin completion status (`origin_index`, `status`, `meps_run`, `completed_horizons`, `retries`), not the fetched values themselves. `sample_lwp_iwp_extraction_benchmark.csv` is a timing/summary-statistics benchmark over 5 sample dates, not raw per-row data usable for exact comparison. **Per this task's own stop condition, I did not initiate a new fetch to obtain this** — doing so for all 711 origins would be exactly the "new bulk dataset" acquisition the task explicitly disallows; even a single-origin spot-fetch was outside this task's "existing local artifacts only" authorization (the previous task separately and explicitly authorized exactly one such live query; this task did not re-authorize another one).

**Could be done, and was done:** structural/internal-consistency verification of the existing Stage 6.6 output files, independent of needing the raw source arrays.

## 4. Structural verification performed (full 17,064-row coverage)

| Check | 2024 (8,328 rows / 347 origins) | 2025 (8,736 rows / 364 origins) |
|---|---|---|
| Duplicate `(forecast_start, horizon_hour)` keys | 0 | 0 |
| `NaN` in `lwp_latest` | 0 | 0 |
| `NaN` in `iwp_latest` | 0 | 0 |
| Origins with a horizon set other than exactly `{1..24}` | 0 | 0 |
| `meps_run_id` matches the same-day 00Z run for its origin (spot-checked, origin 2024-01-20 → `meps_det_20240120T00Z`) | consistent | consistent (not separately spot-checked for a 2025 row in this pass) |
| `surface_air_pressure_hpa` varies by horizon within one origin (checked for origin 2024-01-20: 938.50, 939.64, 939.75, 940.15, 940.59 hPa for horizons 1–5) | varies as expected | not separately re-checked in this pass |

The varying per-horizon surface pressure indicates the extraction is genuinely reading sequential array elements for each horizon, not a static or corrupted readout — this supports the extraction mechanism's sequencing being intact, but says nothing about whether the sequence is offset by one position relative to the base matrix's own `horizon_hour` labeling (the open question).

**Total rows checked structurally: 17,064 of 17,064 (100%). Total rows checked against an independently recomputed source value: 0 of 17,064 (0% — blocked per §3).**

## 5. Missing, duplicate, mismatched, and unverifiable counts

- **Missing values:** 0 (both files, both LWP and IWP, all 17,064 rows).
- **Duplicate keys:** 0.
- **Value-level mismatches against an independent recomputation:** **not determined — 17,064 unverifiable**, for lack of retained raw source data (§3).

## 6. Representative mismatch details

None available — no independent value was computed to compare against, so no mismatch (or match) at the value level can be reported for any row.

## 7. Verdict: **`INCONCLUSIVE`**

### What this verdict establishes

- The existing Stage 6.6 output is **structurally sound**: complete, non-duplicated, fully covering the expected 711-origin × 24-horizon grid, with no missing values in either file.
- The row-key join mechanism in `build_corrected_feature_matrix.py` is confirmed (by code reading) to operate purely on the `(forecast_start, horizon_hour)` label.
- The one-hour `valid_time`-vs-`timestamp` label discrepancy identified in the prior report is **reconfirmed to be a labeling-convention difference**, not a sign of corrupted or missing extraction.

### What this verdict does NOT establish

- Whether the LWP/IWP **values** stored under each `horizon_hour` label are the value that *should* be there under a corrected, lead-0-aligned indexing — this cannot be determined without the raw per-origin MEPS profile data, which does not exist locally for any of the 711 origins.
- Whether the previously reported Candidate F MAE would change under a corrected join — unresolved, same as the prior report.

This is **not** a disproof of the earlier "likely correctly paired" inference, nor a confirmation of it — it is a report that the full-scale check the task asked for cannot be completed from what is available locally, stated precisely rather than guessed at.

## 8. Smallest next action to unblock the project

A **single**, explicitly authorized, bounded live query (the same pattern already used and authorized twice in this investigation) against **one** real same-day 00Z `meps_det_pl` file — requesting the raw `mass_fraction_of_cloud_condensed_water_in_air_pl`/`...ice...`/`surface_air_pressure` profile for one already-known origin (e.g., 2024-01-20, horizon_hour=1) — followed by running the existing, unmodified `compute_surface_aware_lwp_iwp` function on that raw response and comparing the result to `lwp_iwp_extracted_features.csv`'s stored value for that exact row. This is a **single-row spot-check**, not a bulk fetch, and would directly convert this `INCONCLUSIVE` verdict into either a confirmed match (strong support for "likely correctly paired") or a confirmed mismatch (direct evidence of a value-level, not just label-level, misalignment) — without needing to re-acquire all 711 origins. This action requires its own explicit authorization, not implied by this task's local-artifacts-only scope.

## 9. Governance and scope confirmation

No source file, feature matrix, cache, model, evaluation result, protocol, or governance artifact was modified or regenerated. No training, retraining, evaluation, benchmarking, or experiment was run. No Arm B or planner/controller activity occurred. `winner: null` is unchanged. No new bulk acquisition was performed; no network request was made in this task at all. The historical operational publication-time question remains unresolved and is not claimed to be settled by this report.
