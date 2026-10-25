# STAGE 4 — 2025 Holdout Governance Resolution

**Status:** CLEAR (all four blockers from the previous review resolved, with the caveats recorded below).
**Scope:** input provenance and completeness only. This record does not authorize, perform, or inspect any S-L or SW-L candidate run, and it does not inspect any 2025 candidate outcome.
**Governing references (unchanged):** `EXP_CANDIDATE_S_SW_PREREGISTRATION.md/.json`, `EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md/.json`, `STAGE8_1_FORECASTING_FREEZE` (not altered).

The Stage 4 preregistration (`EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION`) is **not** created by this record. It may be drafted only after this record is reviewed.

---

## 1. NWP chain equivalence

**CONCLUSION: SAME CAUSAL FORECAST CHAIN** (generator, source, model, transformations, feature schema, origin/horizon convention). One known documentation inconsistency is classified as a label error, not a chain difference (§1.6). One shared semantic caveat applies equally to both years and is not a difference between them (§1.7).

### 1.1 Files and hashes

| Role | File | SHA-256 |
|---|---|---|
| 2024 generator (LOCKED) | `clear_sky/audit_clean_nwp_windows.py` | `c8f1a2204af1703296e32658e5d8890e2bd7f876d554a2b1a5ee46f1bc50ad21` |
| 2025 generator (replica) | `clear_sky/audit_clean_nwp_windows_2025.py` | `5d38d1c4976bffd53a114b652e610d299a713a0bd62e14031a9b661150ce724c` |
| 2024 NWP (used by the frozen campaign) | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16` |
| 2025 NWP (proposed holdout) | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` | `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5` |
| 2025 NWP manifest | `data/POLARIS_v0_1_future_weather_forecasts_2025_MANIFEST.json` | `534ed055d632950c474e4a38ff11b4b31f16955e6dff5968b7acabd31edf14cf` |

The 2024 file's hash was not recorded in any manifest before this review. Its hash is recorded here. Its modification time (2026-09-09 21:17) is earlier than the frozen campaign's execution (2026-10-05, 16:26–19:01), so the file was not changed by the campaign.

### 1.2 Source, model, and method

Both generators call the same endpoint, `https://previous-runs-api.open-meteo.com/v1/forecast`, with `models=metno_seamless` and the same six `*_previous_day1` variables. The only substitution in the request is `start_date`/`end_date` (2024 vs 2025). Both write the same ten-column schema: `forecast_start, horizon_hour, timestamp, actual_SW_IN, fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, fc_precipitation, fc_surface_pressure, fc_wind_speed_10m`.

The 2025 manifest states "exact replica of audit_clean_nwp_windows.py (2024, LOCKED), year substituted." A line-by-line diff confirms this. Differences are limited to:
- year substitution in the URL and output paths;
- retry, backoff, timeout and checkpoint wrappers around the fetch (no effect on values);
- atomic CSV writes and additional assertions (no effect on values);
- a 2025 origin list derived from the SITES SW_IN timeline, instead of the locked benchmark file (see §1.4).

### 1.3 Transformations and missingness

Both scripts apply the same PASS/FAIL rule: an origin is usable only if all 24 horizon hours have non-null values for all six genuine variables. No filling, interpolation, or imputation is applied (`synthetic_imputation: none`). Both use the same horizon mapping: horizon 1 is at the origin hour (verified: `timestamp − forecast_start = 0 h` for horizon 1 in both files and in the benchmark).

Within the frozen holdout window (2025-05-01 to 2025-08-31), the 2025 file has 123 complete origins, 2,952 rows, and zero NaN values (§3). The 2024 campaign window (2024-05-01 to 2024-08-31) is also complete. Missingness elsewhere in 2024 (18 FAIL origins in the full year) does not touch the campaign window or the holdout window.

### 1.4 Known provenance difference — origin source

- 2024: origins are read from the locked benchmark CSV, `POLARIS_v0_1_fixed_24h_benchmark.csv` (365 origins).
- 2025: origins are derived from the SITES SW_IN timeline (`forecast_start = floor(timestamp, day)`, 365 origins).

Both define an origin as 00:00 UTC of a day, with the same 24 horizon hours. The derivation method differs but produces the same origin convention for the holdout window. This is recorded as a difference in origin source, not in the forecast chain.

### 1.5 Output-file semantics

The 2024 file on disk has 347 usable origins (the 2024 PASS rule excluded 18 origins over the full year). The 2025 file on disk has 365 origins (zero excluded). The different numbers reflect the data availability of each year and do not change the chain.

### 1.6 Label inconsistency (classified as label error)

The Stage 8.1 freeze labels the 2025 NWP file "NWP (clean, audit-only)". The 2025 manifest describes the same file as an exact replica of the locked 2024 method. The 2024 file used by the frozen campaign is the output of the same method. Evidence supports reading "audit-only" as a documentation label for the Stage 8.1 forecast-evaluation role, not as a statement that the chain differs. This classification rests on the identical generator, source, model, transformation, and schema. The freeze document itself is **not** altered. This record annotates the inconsistency so it cannot be silently relied on.

### 1.7 Shared semantic caveat (not a difference)

The `*_previous_day1` variables are day-ahead model values as returned by the archive. The exact forecast release time relative to each origin is not established by the repository for either year. This caveat applies identically to the 2024 campaign and to the 2025 holdout. It is recorded so that any confirmatory claim states the causal release convention as assumed, not verified.

---

## 2. Frozen origin-selection rule (2025)

**Rule (deterministic, route-independent):** every 00:00 UTC origin with `forecast_start` from **2025-05-01 through 2025-08-31 inclusive**, whose required inputs are complete (§4). No origin is excluded on the basis of route, solar elevation, candidate behaviour, forecast performance, reliability, diesel consumption, or low-sun hours.

**Equivalence with the frozen 2024 population:** the 2024 campaign selected its origins with a filter on the same May–August window of the causal weather file and asserted a count of 123 (`run_diesel_reduction_campaign.py` L199–205). The 2025 rule is the same filter applied to the 2025 file.

### 2.1 Counts

| Quantity | Value |
|---|---|
| Expected calendar origins (2025-05-01 to 2025-08-31 inclusive) | 123 |
| Available origins in the 2025 NWP file | 123 |
| Missing origins | none (listed: none) |
| Eligible origins under the frozen rule | **123** |

No origin is removed. There are no missing dates to report.

---

## 3. Route counts (diagnostic only)

Route is recorded as a diagnostic. It is not an inclusion or exclusion criterion.

- **Origin population label** (`operating_mode` set at initial state, as in the frozen campaign): **NORMAL = 123** for all 2025 origins, and the same for all 2024 origins.
- **Router route at step 0** (computed with the causal engine and `EMSControlRouter` at the frozen initial state): **EMERGENCY = 123, NORMAL = 0** for 2025; **EMERGENCY = 123, NORMAL = 0** for 2024.

The step-0 router reconstruction was validated against the campaign's archived telemetry: the campaign's hour-0 Control B route is EMERGENCY for all 123 origins, matching the reconstruction exactly.

The population label "NORMAL" therefore names an initial-state setting, not a router decision. All origins are retained.

---

## 4. Holdout input completeness (input audit only — no candidate outcomes inspected)

| Input | Source | Window rows | Expected | NaN | Result |
|---|---|---|---|---|---|
| Timestamps | SITES SW_IN timeline | 2,952 | 2,952 | 0 | PASS |
| Causal NWP (6 genuine vars, 24 h per origin) | `POLARIS_v0_1_future_weather_forecasts_2025.csv` | 2,952 (123 origins) | 2,952 | 0 | PASS |
| Actual SW_IN (realization, simulator-only) | `POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv` | 2,952 | 2,952 | 0 | PASS (range 0.0 to 796.35 W/m²) |
| Clear-sky GHI and solar elevation | `POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv` | full year 8,760 | 8,760 | 0 | PASS |
| Solar elevation (feature matrix) | `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | 2,952 | 2,952 | 0 | PASS |
| Demand | Synthetic formula, no data input | — | — | — | PASS (`max(10,000, 15,000 + 3,000·cos(hπ/12))`) |
| Wind (realized) | Synthetic formula, no data input | — | — | — | PASS (`max(0, 4,500 + 5,000·sin(hπ/6))`) |
| Wind (forecast) | Baseline heuristic from the frozen initial state | — | — | — | PASS (no data input) |

**INPUT COMPLETENESS: PASS.** 2025 window: 123 origins, zero missing or NaN values in any required input.

The realized SW_IN appears in this table only as an input completeness check. No candidate outcome was computed or inspected.

---

## 5. Solar-elevation computation

### 5.1 Exact existing implementation

- **Module:** `clear_sky/compute_clearsky_2025.py` (2025 input), mirroring `clear_sky/compute_clearsky.py` (2024, LOCKED). Both files contain the same calculation; the diff differs only in the input path, output path, and row-count assertion.
- **Library:** pvlib 0.16.1, `pvlib.location.Location(...).get_solarposition(times)['elevation']`.
- **Location (locked in the file header):** latitude 68.362074° N, longitude 18.738752° E. Elevation argument not supplied (pvlib default).
- **Timestamp convention:** the naive `TIMESTAMP` value is localized with `tz_localize("Etc/GMT-1")`. The file header states "Timezone: UTC+1 (CET) (LOCKED)". The result is that each naive timestamp T is interpreted as the instant T − 1 h in UTC.
- **Units:** degrees above the horizon.
- **Atmospheric assumptions:** none supplied to `get_solarposition` (the pvlib default solar-position algorithm is used).

### 5.2 Known convention offset (documented, not corrected)

The observed diurnal SW_IN peak (Jun–Jul, 2024 and 2025) sits at wall-clock hour 11:00 in the SITES timestamps. Local solar noon at this longitude is about 10:45 UTC. This is consistent with the SITES timestamps being UTC-labelled, not CET. The elevation code interprets them as UTC+1, so the elevation at timestamp T is the true elevation at T − 1 h.

This offset is a property of the locked implementation. It is not corrected in this record, because the implementation is the frozen one used by the 2024 campaign and by the 2025 feature matrices. The Stage 4 preregistration must state the offset explicitly.

### 5.3 Feature-equivalence check (provenance only, not a candidate run)

Recomputed elevation with the exact code path (naive timestamps, `tz = "Etc/GMT-1"`, pvlib `get_solarposition`) and compared with the `solar_elevation` columns in the frozen feature matrices.

| Matrix | Rows compared | Max \|diff\| (deg) | Mean \|diff\| (deg) | Rows within 1e-6 deg |
|---|---|---|---|---|
| 2025 CORRECTED | 8,736 | 0.000000 | 0.000000 | 8,736 / 8,736 |
| 2024 CORRECTED | 8,328 | 0.000000 | 0.000000 | 8,328 / 8,328 |

For comparison, the alternative reading (`tz = "UTC"`) differs by up to 5.53° (mean 3.60°) and matches 0 rows. The implementation is therefore established as the one that generated the existing feature columns.

**Equivalence result: EXACT** (all compared rows, zero difference within numerical tolerance).

The 2025 May–August window has 2,952 hours with zero NaN elevation (§4).

---

## 6. Holdout status statements

- **2025 candidate results inspected:** NO. No S-L or SW-L run was performed, and no candidate outcome was computed or read.
- **2025 remains untouched confirmatory data** for the Stage 4 direction. The 2025 Stage 8.1 forecast metrics in the freeze pre-date this direction and are not used for it.
- **2024 is discovery data only** for this direction. The 123 2024 origins were examined in Stage 3 and are not confirmatory.

---

## 7. Governance decisions recorded

1. The NWP chain is classified **SAME CAUSAL FORECAST CHAIN**, with the label inconsistency classified as documentation error (§1.6) and the shared release-time caveat recorded (§1.7).
2. The 2025 origin rule is the frozen calendar rule in §2. Route is diagnostic only and is not used for inclusion.
3. The solar-elevation implementation is the existing `compute_clearsky_2025.py` calculation, unchanged, including its documented one-hour offset (§5.2).
4. The 15° low-sun boundary is an existing research regime convention (`CROSS_YEAR_ERROR_STABILITY_AUDIT.md`, modified 2026-10-05 07:29, before the S/SW campaign; the same `Low_0_15` bin appears in `EXP_CONFORMAL_TRAJECTORY_OFFLINE/run_offline_validation.py` L119). It is not changed here.

---

## 8. Files and hashes

Hashes of inputs cited by this record are listed in §1.1 and §5.3 and in the companion JSON. The companion JSON file and this Markdown file are hashed in the JSON record (`experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json`).

---

**STATUS: CLEAR** — Stage 4 preregistration may now be drafted for review. The preregistration itself has not been created.
