# Candidate F Successor — 18Z Causal Feature Contract (v1, SPECIFICATION ONLY, NOT IMPLEMENTED)

**Date:** 2026-10-12. **Status: DRAFT SPECIFICATION — no code implementing this contract has been written, no feature matrix has been built, no model has been trained.** This document freezes the *design* for a future successor to `candidateF_elevation_x_cloud.joblib`; it does not modify, supersede, or overwrite the existing Candidate F feature contract (`CANDIDATE_37_FEATURES`/`CANDIDATE_F_38_FEATURES` in `phase2_candidateF_additive_feature.py`) or any existing audit document. It is a new, separate, versioned artifact per the task that requested it.

## 1. Scope

Replaces exactly two of Candidate F's 38 features — `lwp_latest`, `iwp_latest` — and the one feature derived from them, `lwp_x_cloud`. All other 35 features are unchanged and are not re-specified here.

## 2. Source product (verified live, this session and the prior session)

- **Product family:** `meps_det_pl` (MET Norway MEPS, deterministic, pressure-level), THREDDS archive `meps25epsarchive`.
- **URL pattern:** `https://thredds.met.no/thredds/dodsC/meps25epsarchive/{YYYY}/{MM}/{DD}/meps_det_pl_{YYYYMMDD}T18Z.ncml`, where `{YYYY}/{MM}/{DD}` is the **prior calendar day** relative to the POLARIS forecast origin.
- **This is the same file family already fetched by the existing pipeline** for `u700`/`v700` (`acquire_extract_meps_2020_2023.py:140-148`) — no new product, only new variables requested from an already-targeted file.

## 3. Variables

| New feature name | Source variable | Units | Standard name | Dimensions |
|---|---|---|---|---|
| `lwp_18z_fc` (replaces `lwp_latest`) | `mass_fraction_of_cloud_condensed_water_in_air_pl` | `kg/kg` (raw NWP variable; converted via the existing `compute_surface_aware_lwp_iwp` vertical integration to the reported g/m² LWP, unchanged conversion logic) | `mass_fraction_of_cloud_condensed_water_in_air` | `[time=67][pressure=13][y=1069][x=949]`, grid-point-indexed to Nuolja (`NUOLJA_Y=760`, `NUOLJA_X=486`) |
| `iwp_18z_fc` (replaces `iwp_latest`) | `mass_fraction_of_cloud_ice_in_air_pl` | `kg/kg` → g/m² via the same conversion | `mass_fraction_of_cloud_ice_in_air` | Same |

**Verification evidence (live THREDDS queries, confirmed this session):**
- `.dds` query, `meps_det_pl_20240119T18Z.ncml`: both variables present, dimensions as above.
- `.dds` query, `meps_det_pl_20250614T18Z.ncml`: both variables present, identical dimensions — one representative 2025 sample confirming the structure persists past the 2023-09-30 archive-regime change.
- `.das` query, `meps_det_pl_20240119T18Z.ncml`: `units=kg/kg` confirmed for both variables; the identical attributes on the corresponding 00Z file were **not separately re-queried** in this contract and are assumed unchanged (same variable name, same product definition) — flagged as an assumption, not an independently re-verified fact.

## 4. Initialization time, valid time, and the 00Z decision cutoff

- **POLARIS decision cutoff, as used throughout this contract: `forecast_start`, 00:00 UTC.** This is the convention inferred from the existing matrix's own row structure (`horizon_hour=1` row has `timestamp == forecast_start`), not an explicitly named code constant — stated here once, applied consistently, and not re-derived differently elsewhere in this document.
- **Run initialization:** the selected 18Z run's `forecast_reference_time` = the prior calendar day at 18:00:00 UTC. Verified live for one date: `forecast_reference_time = 1705687200` (epoch seconds) = **2024-01-19T18:00:00Z**, for a 2024-01-20 origin.
- **Age of the run at the decision cutoff: exactly 6 hours**, for every origin under this convention (the offset is constant by construction, not origin-dependent).
- **Valid time / horizon mapping:** for origin `O` (00:00 UTC) and horizon `h ∈ {1..24}`, the required valid time is `O + h` hours. The selected run's lead hour for that target is `6 + h` (since the run started 6 hours before the origin). Verified: `time[0..5]` on the sample 18Z file step hourly from the run's own init instant, confirming 1-hour spacing; the file's 67-step range (0–66h from run init) covers lead hours 7 through 30, i.e. every `h ∈ {1..24}` **with no horizon unreachable**.
- **Admissibility rule (the contract's core causality gate):** a value is admissible for horizon `h` of origin `O` **only if** it is read from the single 18Z run initialized at `O − 6h`, at lead hour `6 + h`, from the file whose `forecast_reference_time` exactly equals `O − 6h`. Any value read from a different run (earlier or later), or from the same-day 00Z run, or from `sites_hourly`/realized `SW_IN`, is **inadmissible** under this contract.

## 5. Publication/availability evidence — explicitly distinguished from design feasibility

- **Documented operational latency (external, provider-partner-published, not THREDDS-archive-specific or year-specific):** MEPS output reaches users ≈135 minutes after nominal run time (MetCoOp conference poster, cited in `TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md` §I.3).
- **Margin at this contract's cutoff:** the selected 18Z run is 6 hours old at the 00:00Z cutoff — a margin of **+3h45m beyond the ≈135-minute documented latency figure**. This margin is **comfortably positive**, in contrast to the current same-day 00Z source's margin, which is negative by construction (0 hours old at cutoff, against a positive required latency).
- **What this evidence does NOT establish:** no `meps_det_pl`-specific, 2024/2025-dated, archive-level publication timestamp was found for either the 00Z or the 18Z product. The 6-hour-margin argument is a **design-feasibility judgment, backed by a general external latency figure**, not a historically verified, date-specific publication record. **This distinction is preserved explicitly and must not be collapsed into a claim of verified historical availability.** If this contract is ever implemented, this remains the single largest piece of residual evidence risk, carried forward unchanged from `TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md` §I/§J.

## 6. `lwp_x_cloud` redefinition

`lwp_x_cloud_18z = lwp_18z_fc × cloud_frac`, where `cloud_frac` is unchanged from the existing contract (sourced from the 18Z `cloud_area_fraction_pl`/`fc_cloud_cover`, already causal and already ordering-verified). **Both operands must be read from a run admissible under §4 for the same origin/horizon pair** — i.e., `cloud_frac` already comes from the prior-day 18Z run under the existing pipeline, and `lwp_18z_fc` would now also come from that same run under this contract, so no cross-vintage mixing is introduced. This is a design requirement for any implementation, not yet verified against actual code, since no implementation exists.

## 7. Naming, ordering, missing-value handling, validation rules

- **Renamed features:** `lwp_latest` → `lwp_18z_fc`; `iwp_latest` → `iwp_18z_fc`; `lwp_x_cloud` → `lwp_x_cloud_18z`. Renaming is mandatory under this contract — per the existing semantics audit (`STAGE8_11A_FEATURE_SEMANTICS_AUDIT.md`), "latest" already meant "most recent forecast trajectory," and changing the source run without renaming would let a reader silently assume the old (00Z, same-instant) provenance.
- **Feature ordering:** unchanged position within the existing 37+1 list — the three features are replaced in place, not reordered, appended, or removed from the contract's length (still 38 features total for a GBDT architecture matching Candidate F's).
- **Missing-value handling:** per the existing live 2024/2025 extractor's own (safer) convention (`run_stage6_6.py:245-246`), an out-of-physical-range or missing `surface_air_pressure` for any horizon must mark the **entire origin** `INVALID` and exclude it — never a per-row `NaN`→`fillna(0.0)` substitution (the pattern found only in the separate, 2020–2023 `candidate_L_research` reconstruction and explicitly not to be reused). This is a requirement for any implementation; no implementation exists to verify it against yet.
- **Validation rules (must all hold before any row is accepted):** (a) `forecast_reference_time` of the selected run equals `origin − 6h` exactly; (b) the lead-hour index used is `6 + h` for horizon `h`; (c) no fallback to a different run is permitted on fetch failure — the origin fails closed; (d) the 67-step time array covers the required lead hour for every `h ∈ {1..24}` (verified true at the file-structure level in §4, must be re-checked per-origin at implementation time in case any individual day's file has fewer steps).

## 8. Fetcher reuse and isolation

- **The existing fetch mechanism (DODS `.ascii` query against `meps_det_pl`) can be reused as a pattern** — same URL base, same retrieval/caching code shape. **It cannot reuse already-cached response bytes**: the existing 18Z cache (`cache_18z_path` in `acquire_extract_meps_2020_2023.py`) stores a DODS query response restricted to the variables already requested (`air_temperature_2m`, `relative_humidity_2m`, `cloud_area_fraction`, `x_wind_pl`, `y_wind_pl`); it does **not** contain LWP/IWP data. A new network request with an expanded query string (adding `mass_fraction_of_cloud_condensed_water_in_air_pl[...]`/`...ice...`) against the same file would be required for every origin needing this feature — this is a direct correction of an earlier same-day overstatement in this investigation, preserved here for accuracy.
- **Isolation requirement:** any implementation of this contract must write to a new cache directory and new output files, never touching `stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv`, `stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv`, or any existing `*_CORRECTED.csv` matrix.
- **Expected network/cache effect if ever implemented:** one new DODS request per historical origin (≈347 for 2024, ≈364 for 2025, per the existing matrices' own origin counts) against the prior-day 18Z file — i.e., roughly 700 new external HTTP requests against MET Norway's archive. **This has not been performed.** It constitutes the large-scale data acquisition this contract document explicitly does not undertake.

## 9. What this contract does and does not establish

- **Does establish:** a precise, versioned, implementable specification for a causal 18Z-sourced replacement of the two flagged features, grounded in live-verified product/variable/dimension facts.
- **Does not establish:** that the replacement is historically proven available (§5), that any code implementing it exists, that any feature matrix using it exists, or that a model trained on it would be valid without the separate 2025 ensemble-parameter remediation (see the companion protocol document, `CANDIDATE_F_SUCCESSOR_CLEAN_SPLIT_PROTOCOL_v1.md`).
