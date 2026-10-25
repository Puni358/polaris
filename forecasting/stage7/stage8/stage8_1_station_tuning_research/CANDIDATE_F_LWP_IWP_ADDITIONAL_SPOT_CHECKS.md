# Candidate F LWP/IWP Additional Spot-Checks (A: different origin/h=1, B: h=24)

**Date:** 2026-10-12. New, separate report — does not overwrite `CANDIDATE_F_LWP_IWP_ROW_LEVEL_RECONCILIATION.md` or `CANDIDATE_F_LWP_IWP_SINGLE_ROW_LIVE_VERIFICATION.md`.

## Check A — different origin, horizon_hour=1

**Selected before querying:** origin `2024-01-21`, `horizon_hour=1` (array index 0, lead 0). Stored: `lwp_latest=0.0`, `iwp_latest=3.007815`, `surface_air_pressure_hpa=944.28`, `meps_run_id=meps_det_20240121T00Z`. Pressure reused from the stored CSV value (not independently re-fetched) — same documented compromise as the prior single-row verification, to stay at exactly one live request per check.

**One live request:**
```
https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/21/meps_det_pl_20240121T00Z.ncml.ascii?
mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:0][0:1:12][760:1:760][486:1:486],
mass_fraction_of_cloud_ice_in_air_pl[0:1:0][0:1:12][760:1:760][486:1:486]
```
Returned `time[0] = 1.7057952E9` s = **2024-01-21T00:00:00Z**, exactly the run's own init instant (lead 0), confirming the index-0-is-lead-0 convention again.

**Comparison (via the unmodified `compute_surface_aware_lwp_iwp`):**

| Feature | Stored | Recomputed | Abs. diff | Status |
|---|---|---|---|---|
| LWP | 0.0 | 0.0 | 0 | **MATCH** |
| IWP | 3.007815 | 3.0078148008749164 | ≈2×10⁻⁷ | **MATCH** (6-decimal CSV rounding) |

## Check B — horizon_hour=24 (final horizon)

**Selected before querying:** origin `2024-01-26`, `horizon_hour=24` (array index 23, lead 23 — `h_idx=23` per `run_stage6_6.py`'s `h=h_idx+1`). Stored: `lwp_latest=32.868589`, `iwp_latest=28.018135`, `surface_air_pressure_hpa=934.78`, `meps_run_id=meps_det_20240126T00Z`.

**One live request:**
```
https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/26/meps_det_pl_20240126T00Z.ncml.ascii?
mass_fraction_of_cloud_condensed_water_in_air_pl[23:1:23][0:1:12][760:1:760][486:1:486],
mass_fraction_of_cloud_ice_in_air_pl[23:1:23][0:1:12][760:1:760][486:1:486]
```
Returned `time[0] = 1.70631E9` s = **2024-01-26T23:00:00Z** = run_init (2024-01-26T00:00Z) + 23h exactly, confirming array index 23 = lead 23.

**Comparison:**

| Feature | Stored | Recomputed | Abs. diff | Status |
|---|---|---|---|---|
| LWP | 32.868589 | 32.86858896769029 | ≈3×10⁻⁸ | **MATCH** |
| IWP | 28.018135 | 28.018134809376253 | ≈2×10⁻⁷ | **MATCH** |

## Summary and the resulting precise finding

**All 4 comparisons (2 checks × LWP/IWP) MATCH.** Combined with the prior single-row verification, **3 of 3 independently spot-checked rows (spanning both horizon boundaries, h=1 and h=24, and 3 distinct origins) confirm the same precise rule: `stored_value(horizon_hour=h) == raw_array[index = h−1] == value valid at run_init+(h−1)`.**

Since Stage 6.6's same-day 00Z runs have `run_init == origin` exactly, this means: **`stored lwp_latest/iwp_latest at horizon_hour=h` is valid at `origin + (h−1)`** — the **same** convention as the base matrix's own `timestamp` column (established in the prior report: `timestamp = forecast_start + (h−1)`). **The legacy join is now empirically confirmed correct**, not merely inferred — Stage 6.6's `valid_time` *column* is still mislabeled (+1h), but the underlying *values*, joined by the existing `(forecast_start, horizon_hour)` key, are correctly aligned with the rest of each row.

**This directly implies a conflict for the new 18Z successor data**, reported in the accompanying Phase 2 response: the 18Z fetcher's own contract defines `horizon_hour=h → valid_time = origin + h` (one hour **later** than the now-confirmed-correct `origin + (h−1)` convention). Joining the already-acquired 18Z cache by `(forecast_start, horizon_hour)` label, as `build_dataset_v1.py` currently does, would pair each row with an 18Z value that is **one hour later** than what the row's other 34 features and label actually represent — a genuine, newly-surfaced misalignment specific to the new successor data, not the legacy one.

## Governance and scope confirmation

No source file, feature matrix, extracted CSV, acquisition cache, model, evaluation result, protocol, or governance artifact was modified. No training, evaluation, experiment, or Arm B activity occurred. Exactly two live HTTP requests were issued (one per check), no retries, no additional origins/horizons/variables. `winner: null` unchanged. These two checks, together with the prior single-row check, raise confidence to 3/3 but still do not prove all 17,064 legacy rows correct, and do not establish historical operational publication-time availability.
