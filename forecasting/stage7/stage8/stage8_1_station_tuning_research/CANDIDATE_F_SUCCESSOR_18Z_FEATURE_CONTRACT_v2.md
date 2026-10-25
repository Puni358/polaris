# Candidate F Successor — 18Z Causal Feature Contract (v2, SPECIFICATION ONLY, NOT IMPLEMENTED, NOT YET APPROVED)

**Date:** 2026-10-12. **Status: DRAFT — pending explicit project-lead approval.** This document does not modify, overwrite, or supersede `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md`, which **remains unchanged and remains the record of the original (now-corrected-here) design**. Nothing in this document authorizes any code change, acquisition, or dataset build — those require separate, explicit authorization per the governing task's Phase 1 stop gate.

## 0. Why v2 exists

Three independent, live-verified spot-checks (`CANDIDATE_F_LWP_IWP_SINGLE_ROW_LIVE_VERIFICATION.md`, `CANDIDATE_F_LWP_IWP_ADDITIONAL_SPOT_CHECKS.md`) established that the base Candidate F feature matrix's `horizon_hour=h` corresponds to source lead time `h−1` (valid at `origin+(h−1)`), not lead `h`. The v1 successor contract instead defined `lead=6+h` (valid at `origin+h`) — one hour later than the now-confirmed-correct convention. v2 corrects this for the successor path only; it does not touch v1, the legacy Stage 6.6 extraction, or the base matrix.

## 1. Base horizon definition and target timestamp

`base horizon_hour = h`, for `h = 1..24`, targets **valid time `origin + (h−1)` hours**, where `origin` = the POLARIS forecast origin (`forecast_start`, 00:00 UTC). This is identical to the base matrix's own `timestamp` convention (`timestamp = forecast_start + (horizon_hour − 1)`), confirmed in the prior reconciliation reports, and is **not** a new invention — it is the pre-existing convention this contract now aligns to.

## 2. Required source lead mapping

For base horizon `h`, the required source lead time (hours after the 18Z run's own initialization) is:

```
lead = 5 + h
```

Derivation: the 18Z run initializes at `origin − 6h`. A value valid at `origin + (h−1)` is therefore at lead `(origin + (h−1)) − (origin − 6h) = 5 + h` hours from that run's own init. For `h = 1..24`, this spans **lead 6 through lead 29**.

## 3. Mapping existing cache (leads 7–30) plus the new lead-6 record

| Base horizon `h` | Required lead | Source |
|---|---|---|
| 1 | 6 | **New** — not in `cache_full_acquisition/`; requires the Phase 2 lead-6 acquisition |
| 2 | 7 | Existing `cache_full_acquisition/` record's own horizon label `h_cache=1` (which the v1 contract computed as `lead=6+1=7`) |
| 3 | 8 | Existing cache, `h_cache=2` |
| ... | ... | ... |
| 24 | 29 | Existing cache, `h_cache=23` |

**General rule: `base h ← existing cache horizon (h−1)` for `h=2..24`; `base h=1 ← new lead-6 record`.** This was independently arithmetically verified in the Phase 1 review preceding this contract (`lead=6+h_cache` with `h_cache=h−1` gives `lead=6+(h−1)=5+h`, matching §2 exactly) and is **not re-derived differently here**.

**No other remapping is introduced.** The existing cache's own lead 30 (`h_cache=24`) is **not used** under v2 — it corresponds to `base h=25`, which does not exist in the 24-horizon contract. This is a harmless, intentional non-use, not a data-quality problem with the existing cache.

## 4. Variable names, pressure level, units, valid-time checks, key conventions, missing-value behavior

**Unchanged from v1** (not restated in full to avoid duplicating the frozen document; referenced by exact name):

- Source product: `meps_det_pl`, THREDDS `meps25epsarchive`, prior-day 18Z run relative to `forecast_start`.
- Variables: `mass_fraction_of_cloud_condensed_water_in_air_pl` (LWP source), `mass_fraction_of_cloud_ice_in_air_pl` (IWP source).
- Pressure level: index 8 of 13 (≈700 hPa), grid point `(y=760, x=486)`.
- Units: raw `kg/kg` mass fraction; output in g/m² per the existing, unmodified conversion.
- Valid-time check: `forecast_reference_time` of the selected run must equal `origin − 6h` exactly (unchanged — the run itself is still the same prior-day 18Z run; only which lead index is read from it changes).
- Key convention: cache identity (`cache_key`) remains a function of `(product, run tag, variables, pressure index, grid point)` — **unchanged**, since the run and product are unchanged; only the **requested lead index** differs between v1's `6+h` and v2's `5+h`.
- Missing-value behavior: **unchanged** — a structurally invalid or missing value fails that origin closed (no silent substitution, no interpolation), per v1 §7 and the existing `validate_response` design.

**New requirement specific to v2, Base horizon 1:** since lead 6 was never requested under v1, a **new, narrowly-scoped fetch** (lead 6 only, same two variables, same pressure level, same grid point) is required — see Phase 2 of the governing task, not performed by this document.

## 5. Cache schema, manifest, and content-hash requirements

**Unchanged in structure from the existing fetcher's schema** (`ProvenanceRecord`, atomic JSON writes, `content_sha256`, `cache_key`-keyed filenames). The lead-6 acquisition (Phase 2, not yet authorized) must write to a **new, isolated cache directory**, distinct from `cache_full_acquisition/`, with its own `ACQUISITION_MANIFEST.json` following the same format already proven for the 711-origin acquisition. No schema change is introduced by v2 — only the requested lead index changes.

## 6. Split and leakage controls (inherited, unchanged)

Fully inherited from `CANDIDATE_F_SUCCESSOR_CLEAN_SPLIT_PROTOCOL_v1.md`: 2024-EVEN → train, 2024-ODD → validation, all 2025 origins → blind (ignoring the 2025 matrix's own irrelevant EVEN/ODD column, per the already-documented methodology note). v2 does not alter the split protocol in any way — it only corrects which raw value is joined to each existing row.

## 7. Backward compatibility

`CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md` **remains unchanged, in place, as the historical record** of the original (one-hour-late) design. v2 is additive documentation plus, once separately authorized, one additional small acquisition — it does not require deleting, invalidating, or reprocessing anything already built under v1 beyond the dataset build that was itself never completed (Phase 2 of the earlier governing task stopped before any v1-based dataset was written, per that task's own report). No v1-based dataset artifact exists to be made backward-incompatible.

## 8. Historical publication-time availability — unresolved limitation, restated

**Unchanged from every prior report in this investigation:** successful retrieval of MEPS 18Z data today does not establish that the same data was operationally available at the historical forecast-origin decision cutoff. This remains an open, unresolved limitation, carried forward unchanged by v2, and is not claimed to be resolved by any of the arithmetic or mapping corrections in this document.

## 9. Arithmetic/consistency check performed before writing this contract

- Re-verified against `fetcher.py`: `RUN_OFFSET_HOURS=6`, `lead=RUN_OFFSET_HOURS+h` for `h=1..24` → lead 7–30, confirmed unchanged in the existing (v1) code.
- Re-verified against one representative cache record (`44facd445b0f3e87a6cc201c.json`, origin 2024-01-24): `min lead=7, max lead=30`, consistent with v1's formula and with §3's table above.
- Re-verified against `ACQUISITION_MANIFEST.json`: `planned_unique_origins=711, ok=711, failed=0` — confirming the existing cache has no gaps across all 711 origins for leads 7–30, so the §3 mapping has no missing-origin risk for `h=2..24`.
- Re-verified against `CANDIDATE_F_SUCCESSOR_CLEAN_SPLIT_PROTOCOL_v1.md`: no conflict — the split protocol operates on origins and rows, not on which lead index supplies a feature value, so §6's inheritance is exact.
- No unrelated contract element was changed.

## 10. Scope boundary

This document is specification only. No code was changed, no network request was made, no acquisition was performed, and no dataset was built in the course of writing it.
