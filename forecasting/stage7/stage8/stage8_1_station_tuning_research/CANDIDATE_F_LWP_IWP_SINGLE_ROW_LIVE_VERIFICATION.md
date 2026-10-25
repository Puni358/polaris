# Candidate F LWP/IWP Single-Row Live Verification

**Date:** 2026-10-12. **Nature:** one explicitly authorized, bounded live query, used to independently recompute and compare exactly one existing stored LWP/IWP value. This report is new and separate; it does not overwrite `CANDIDATE_F_LWP_IWP_ROW_LEVEL_RECONCILIATION.md` or any prior report.

## 1. Selected row and selection rationale

| Field | Value |
|---|---|
| `forecast_start` | 2024-01-22 |
| `horizon_hour` | 1 |
| Stored `valid_time` | 2024-01-22 01:00:00 |
| Stored `surface_air_pressure_hpa` | 928.77 |
| Stored `lwp_latest` | 5.382813 |
| Stored `iwp_latest` | 37.168788 |
| `meps_run_id` | `meps_det_20240122T00Z` |

**Rationale:** `horizon_hour=1` (i.e. Stage 6.6's `h_idx=0`) was selected deliberately — it is the exact index where the suspected one-hour labeling offset matters most (per the prior reports, `h_idx=0` is claimed "valid at origin+1h" but independently confirmed, via live `time[0]==forecast_reference_time` checks on both an 18Z and a 00Z file, to actually be lead-hour 0, valid at the run's own init instant). Among all rows with `horizon_hour=1`, this origin was chosen because it has a strong, clearly nonzero signal (`iwp_latest=37.17`), satisfying "prefer a representative row with a nonzero stored signal."

## 2. Exact request scope and source identity

The original extractor (`run_stage6_6.py:217-230`) uses **three** separate HTTP requests for one full origin: `surface_air_pressure` from a `meps_det_sfc_*` file, and `ql`/`qi` from a `meps_det_pl_*` file. Honoring this task's **exactly one request** limit, I reused the already-stored `surface_air_pressure_hpa=928.77` (converted to Pa: `92877.0`) rather than re-fetching it, and issued **one** combined request for both `ql` and `qi` (same file, same request) restricted to lead-index 0 only:

```
https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/22/meps_det_pl_20240122T00Z.ncml.ascii?
mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:0][0:1:12][760:1:760][486:1:486],
mass_fraction_of_cloud_ice_in_air_pl[0:1:0][0:1:12][760:1:760][486:1:486]
```

**This is explicitly flagged as a methodological compromise**, not a silent deviation: fetching all three original variables fresh would have required 2–3 requests; reusing the already-stored, already-public `surface_air_pressure_hpa` value kept this to exactly one live request while still exercising the part of the calculation most directly in question (the raw ql/qi profile at the disputed index). This was decided and recorded before issuing the request.

**Source identity confirmed in the response:** `pressure[13] = 50.0 … 1000.0` hPa (same 13 levels as `PRESSURE_LEVELS_HPA`); `time[1] = 1.7058816E9` s epoch = 2024-01-22T00:00:00Z — exactly the run's own initialization instant (lead hour 0), consistent with the index-0-is-lead-0 finding already established for this product family.

## 3. Calculation function used

`compute_surface_aware_lwp_iwp` — imported and executed **unmodified** from `stage6/stage6_6_lwp_iwp/run_stage6_6.py:187-209` (loaded via `importlib`, not reimplemented or copied by hand).

## 4. Stored vs. independently recomputed values

| Feature | Stored value | Recomputed value | Absolute difference | Tolerance | Status |
|---|---|---|---|---|---|
| LWP (g/m²) | 5.382813 | 5.382813014638027 | ≈1.5×10⁻⁸ | floating-point rounding of a 6-decimal stored value | **MATCH** |
| IWP (g/m²) | 37.168788 | 37.168788069454266 | ≈7×10⁻⁸ | floating-point rounding of a 6-decimal stored value | **MATCH** |

No rounding was applied to manufacture agreement — the recomputed values are reported at full `float64` precision; the differences shown are exactly what full-precision subtraction gives against the stored 6-decimal-place CSV values, consistent with the CSV simply having been written with fewer printed digits than the underlying float.

**Units/conventions:** input `ql`/`qi` in kg/kg (raw MEPS mass fraction, confirmed via `.das` metadata in an earlier session); `surface_air_pressure_hpa` converted hPa→Pa (`×100`) before passing to the function, matching the function's own expected input convention (`ps_pa`); output in g/m² (`×1000.0` inside the function), matching the stored column's own units.

## 5. Verdict: **`MATCH`**

The independently recomputed LWP and IWP values, derived from one live-fetched raw profile at **array index 0** (confirmed to be lead-hour 0, valid at the run's own init instant) and the existing, unmodified calculation function, **exactly match** the value stored in `lwp_iwp_extracted_features.csv` under `horizon_hour=1` for this origin.

### What this establishes

- For this one row, the **data value** stored under `horizon_hour=1` is genuinely the array's lead-0 value — confirming, for this specific case, the "likely correctly paired" inference from the prior reconciliation report.
- The extraction mechanism (fetch → reshape → `compute_surface_aware_lwp_iwp` → store) is functioning correctly for this row.

### What this does NOT establish

- This is **one row out of 17,064**. It does not prove every other row is correctly paired — a systematic bug could still be origin- or horizon-specific in a way this single check cannot rule out.
- It does **not** resolve the separate, already-established **label** discrepancy: the stored `valid_time` for this row still says "2024-01-22 01:00:00" (`origin+1h`) while the value is now directly confirmed to be the lead-0 value, truly valid at "2024-01-22 00:00:00" (`origin+0h`). The **label is still wrong**; only the **underlying value's correct correspondence to the `horizon_hour` index** is newly confirmed.
- It does **not** establish or claim anything about historical operational publication-time availability (a separate, still-open question from earlier reports).

## 6. SHA-256 hashes

| Artifact | SHA-256 |
|---|---|
| `stage6/stage6_6_lwp_iwp/run_stage6_6.py` | `671f3152d3fdc6caab3e9d5644d3cb73585be55fba5a93a39fdb36094a31c1ce` |
| `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` | `da6585c3a584f742d4e78f2d5ac5323479a765bcf74bb8b6da31cf1336f600a8` |
| This report (computed after writing, see final response) | — |

## 7. Recommendation, based only on this observed result

Since the single spot-check **matched**, the smallest safe next step — if further confidence is wanted before any governance decision — would be a small (not bulk) number of **additional** spot-checks of this same kind, spanning different origins and horizons (including `horizon_hour=24`, the other boundary case), each requiring its own explicit one-request authorization as this one did. This report does **not** request or perform that; it reports only what was observed from the one authorized query.

## 8. Governance and scope confirmation

No source file, feature matrix, extracted CSV, acquisition cache, model, evaluation result, protocol, or governance artifact was modified. No dataset was constructed, no model was trained or evaluated, no experiment or Arm B activity occurred. Exactly one live HTTP request was issued, with no retry and no alternate origin/horizon/variable. `winner: null` is unchanged. This single matching row is not claimed to prove all 17,064 rows correct, and historical operational publication-time availability remains unestablished.
