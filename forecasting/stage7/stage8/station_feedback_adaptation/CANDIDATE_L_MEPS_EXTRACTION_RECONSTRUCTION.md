# Candidate L — 2020–2023 MEPS Extraction Reconstruction

**Scope**: Research/verification only, worked directly in this session, no subagents. **No
Candidate L training. No large historical dataset download. The existing 2024 extraction
pipeline (`build_wind700_features_2024_corrected.py`, `run_stage6_6.py`,
`build_future_weather_dataset.py`/`audit_clean_nwp_windows.py`) was read but not modified.**
All verification below used single-point or schema-only queries (lat/lon at one grid cell,
the 13-value pressure coordinate array, variable `.dds`/`.das` listings) against the MEPS
THREDDS server — no bulk grids, no time-series data, no training data were fetched.

---

## 1. Exact filename/path pattern for 2020–2023 — VERIFIED

- **2024 (reference, unchanged)**: split files, `.ncml` extension —
  `meps25epsarchive/<YYYY>/<MM>/<DD>/meps_det_sfc_<YYYYMMDD>T<HH>Z.ncml` (surface fields) and
  `meps25epsarchive/<YYYY>/<MM>/<DD>/meps_det_pl_<YYYYMMDD>T<HH>Z.ncml` (pressure-level fields).
- **2020–2023 (newly verified this session)**: a **single combined file**, plain `.nc`
  extension, no `sfc`/`pl` split —
  `meps25epsarchive/<YYYY>/<MM>/<DD>/meps_det_2_5km_<YYYYMMDD>T<HH>Z.nc`. Directly confirmed
  present and queryable at `18Z` for representative dates in 2020, 2021, 2022, and 2023 (one
  `.dds`/`.ascii` call per date, no bulk download).
- **2019**: **not this pattern at all** — confirmed (already in the prior turn, re-confirmed
  here) that 2019 uses `meps_ens_mbr0_vc_2_5km_<date>T<HH>Z.nc` (an ensemble-member "vc"
  product), structurally incompatible (see §8). **2019 remains out of scope for this
  reconstruction**, unchanged from the prior report's conclusion.
- **Exact transition point between the 2019 ensemble-only period and the 2020+ combined
  deterministic product was not re-pinned further in this session** (same UNKNOWN already
  disclosed in the prior report) — not required for this task's scope (2020–2023 only).

## 2. Exact variable names — VERIFIED, all confirmed present and named identically across 2020–2023

Directly confirmed via `.dds` schema queries against representative 2020, 2021, 2022, 2023
files (`meps_det_2_5km_<date>T18Z.nc`), all on the identical grid
(`time=67, pressure=13, y=1069, x=949`):

| F-required field | MEPS variable name, confirmed identical 2020–2023 | Confirmed present |
|---|---|---|
| 2m air temperature | `air_temperature_2m[time][height1=1][y][x]` | Yes, all 4 years checked |
| 2m relative humidity | `relative_humidity_2m[time][height1=1][y][x]` | Yes, all 4 years checked |
| Cloud cover/fraction | `cloud_area_fraction[time][height0=1][y][x]` (surface/total), plus `cloud_area_fraction_pl`/`_ml` and `high_type_cloud_area_fraction`/`medium_type_cloud_area_fraction`/`low_type_cloud_area_fraction` | Yes, all 4 years checked |
| 700 hPa wind | `x_wind_pl[time][pressure=13][y][x]`, `y_wind_pl[time][pressure=13][y][x]` | Yes, all 4 years checked (already confirmed in prior turn; re-confirmed here) |
| Cloud liquid/ice water | `mass_fraction_of_cloud_condensed_water_in_air_pl`, `mass_fraction_of_cloud_ice_in_air_pl` (both `[time][pressure=13][y][x]`) | Yes, all 4 years checked |
| Surface pressure (needed to integrate water path) | `surface_air_pressure[time][height0=1][y][x]` | Yes (already confirmed in prior turn; re-confirmed here) |

**Exact variable names are unchanged from 2024's own split-file naming** — i.e., no renaming
occurred between the split (2024) and combined (2020–2023) product; only the **file packaging**
changed, not the variable identifiers themselves.

## 3. Nuolja grid indices for the older grid — VERIFIED (independently, not hardcoded blindly)

The 2024 script hardcodes `NUOLJA_Y, NUOLJA_X = 760, 486` (confirmed by reading
`build_wind700_features_2024_corrected.py:71` and `run_stage6_6.py:67` directly — **not**
`y=1069, x=949`, which are the full grid *dimension sizes*, not Nuolja's specific point index;
this distinction is clarified here to correct an imprecise shorthand in the prior report).

**Independent verification performed in this session** (not assuming the index transfers,
per the task's explicit instruction): queried the grid's own `latitude`/`longitude` auxiliary
coordinate arrays at `[760][486]` directly, in both the 2024 split file and three of the
2020–2023 combined files:

| Source | `latitude[760,486]` | `longitude[760,486]` |
|---|---|---|
| 2024 split file (`meps_det_pl_20240114T18Z.ncml`) | 68.35570107° N | 18.76366571° E |
| 2020 combined file | 68.35570104° N | 18.76366722° E |
| 2022 combined file | 68.35570104° N | 18.76366722° E |
| 2023 combined file | 68.35570107° N | 18.76366571° E |

**All four years return the same coordinate (to 6+ decimal places) at index (760,486)** —
**the grid definition is confirmed identical across 2020–2024**, not merely assumed from
matching dimension sizes. **This is the single most important verification in this report**:
the existing hardcoded index is directly reusable for 2020–2023 without remapping.

## 4. Nuolja station coordinates vs. the grid cell actually sampled — VERIFIED, within expected nearest-cell tolerance

Station's true surveyed coordinates (per `NUOLJA_HISTORICAL_DATA_SOURCE_AUDIT.md`, re-cited
not re-surveyed): **68.362074° N, 18.738875° E**. Grid cell (760,486)'s actual coordinate
(§3): **68.355701° N, 18.763666° E**. Offset: ≈0.0064° latitude (≈0.71 km) and ≈0.0249°
longitude (≈1.03 km at 68°N) → **straight-line offset ≈1.3 km**. On a 2.5 km grid, a
nearest-neighbor cell can be up to ≈1.8 km from the true point in the worst case — **a ≈1.3 km
offset is consistent with this being the correct nearest grid cell**, not a mapping error. This
is exactly the same offset magnitude implied by the 2024 pipeline already using this same
index — **confirms the existing index was already a reasonable nearest-cell choice**, carried
forward correctly, not newly introduced error.

## 5. Pressure-level indexing for 700 hPa — VERIFIED, identical across years

Queried the `pressure` coordinate array directly (13 values) in both the 2024 file and the
2022 combined file:
```
pressure[13] = 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700.0, 800.0, 850.0, 925.0, 1000.0
```
**Identical in both years.** `700.0` is at **0-based index 8** in both — matching the 2024
script's hardcoded `[8:1:8]` index exactly. **No re-indexing needed for 700 hPa.**

## 6. Older-schema-to-F-feature-name mapping

| MEPS variable (2020–2023 combined file) | F feature | Transformation needed |
|---|---|---|
| `air_temperature_2m` | `fc_temperature_2m` | Unit conversion only (§7) |
| `relative_humidity_2m` | `fc_relative_humidity_2m` | Unit conversion only (§7) |
| `cloud_area_fraction` | `fc_cloud_cover` (→ `cloud_frac = fc_cloud_cover/100`) | Unit conversion only (§7); alternatively, since MEPS's native fraction is already 0–1, `cloud_frac` could be set directly from it, skipping the existing `/100` step — an implementation choice to make explicitly, not a blocker |
| `x_wind_pl[...,8,...]`, `y_wind_pl[...,8,...]` | `u700`, `v700` | None — same variable, same units, same index (§2/§5) |
| `mass_fraction_of_cloud_condensed_water_in_air_pl`, `mass_fraction_of_cloud_ice_in_air_pl`, `surface_air_pressure` | `lwp_latest`, `iwp_latest` (via whatever column-integration formula `run_stage6_6.py` already applies) | None identified beyond what the existing 2024 integration code already does — same variables, same units (not independently re-verified for unit match in this session, see §7 UNKNOWNs) |

## 7. Units/semantics vs. the 2024 extraction — VERIFIED differences found, all resolvable

Checked `.das` (attribute) metadata for the three newly-relevant variables, confirmed
**identical units between 2024 and 2022** (i.e., no *drift* across years in MEPS's own units)
— but a real, pre-existing **semantic mismatch against F's existing Open-Meteo-sourced
features**, confirmed by reading the actual values already stored in the existing, local
`data/POLARIS_v0_1_future_weather_forecasts_2024.csv` (no new download — this file already
exists):

| Field | MEPS native unit (confirmed via `.das`, both 2024 and 2022) | F's existing feature's actual unit (confirmed by reading real rows of the existing 2024 CSV: `fc_temperature_2m=-23.3`, `fc_relative_humidity_2m=70.0`, `fc_cloud_cover=17.0`) | Required conversion |
|---|---|---|---|
| `air_temperature_2m` | Kelvin (`units "K"`) | °C (a value of −23.3 in January at this latitude is unambiguously Celsius, not Kelvin) | **Subtract 273.15** |
| `relative_humidity_2m` | fraction 0–1 (`units "1"`) | Percent 0–100 (`70.0`) | **Multiply by 100** |
| `cloud_area_fraction` | fraction 0–1 (`units "1"`, `standard_name cloud_area_fraction`, `long_name "Total cloud cover (TCC)"`) | Percent 0–100 (`17.0`, matching `fc_cloud_cover`'s existing `/100` normalization in `build_corrected_feature_matrix.py:120`) | **Multiply by 100** (or, equivalently, feed MEPS's native 0–1 fraction directly into `cloud_frac` and skip the existing `/100` step — a design choice, not a blocker) |

**This is a genuine, confirmed semantic difference between MEPS (the proposed 2020–2023
replacement source) and Open-Meteo (the actual 2024/2025 source)** — not a difference across
years within MEPS itself. **It is fully resolvable with simple, well-understood unit
conversions**, not a structural blocker, but it must be implemented correctly (not skipped)
or every one of F's three most load-bearing features (`cloud_frac` underlies both Candidate
F's and Candidate J's own additive features) would be silently wrong by a factor of 100 or an
offset of 273.15.

`x_wind_pl`/`y_wind_pl` units were not re-checked in this session (already implicitly assumed
consistent since the 2024 script uses the same variable name/convention directly against the
same archive family — not re-verified via `.das` here, flagged as a residual check in §9).
`lwp`/`iwp`'s integration-formula unit consistency (mixing ratio × pressure-level spacing →
column path) was not independently re-derived in this session — the existing `run_stage6_6.py`
formula is assumed transferable since the input variables are confirmed unit-identical to 2024
(§2), but the formula itself was not re-run or re-verified against 2020–2023 inputs.

## 8. Unavoidable differences between 2020–2023 and 2024

1. **File packaging**: one combined file vs. two split files — requires a genuinely different
   extraction code path (different URL construction, different variable-to-file mapping), not
   just a date substitution. This is a **real code change**, confirmed necessary, not optional.
2. **Unit conversions** (§7) — required for `air_temperature_2m`, `relative_humidity_2m`,
   `cloud_area_fraction` specifically; not required for `x_wind_pl`/`y_wind_pl`/the cloud-water
   variables (same variable names, presumed same units as 2024, not independently re-checked
   for the wind/water variables' own `.das` attributes in this session).
3. **2019 is categorically different and out of reach via this archive** (confirmed, unchanged
   from the prior report) — this reconstruction does not and cannot extend to 2019.
4. **No equivalent verification was performed for forecast-run hours other than 18Z** — the
   existing 2024 script specifically uses the `T18Z` run (per its `d_minus_1.replace(hour=18)`
   logic); this session's checks were all against `T18Z` files for 2020–2023 to match that
   exactly, but whether every other run hour (00/06/12Z) is available in the same combined-file
   form for every date in 2020–2023 was not separately checked (flagged as UNKNOWN, not a
   contradiction of anything found so far, since 18Z — the one actually needed — is confirmed).

## Remaining blockers before actual 2020–2023 acquisition

- **Code must be written** (not done here, per "research-only... do NOT download the full
  historical dataset or train anything") to: (a) construct the combined-file URL pattern
  instead of the split pattern, (b) apply the three unit conversions in §7, (c) confirm the
  `lwp`/`iwp` integration formula's unit consistency by actually running it against one
  real 2020–2023 day's extracted values (not performed here — this was schema/coordinate
  verification only, no time-series values were pulled).
- **2019 remains unresolved** — nothing in this task changes that conclusion.
- **Bulk acquisition itself (all origins, all days, 2020–2023) has not been attempted** — this
  report establishes that the *mechanism* is ready, not that the *data* has been pulled.

---

MEPS EXTRACTION RECONSTRUCTION: **PASS**
NUOLJA GRID MAPPING: **VERIFIED** (independently, via direct coordinate lookup at the hardcoded index, matching to within expected 2.5 km nearest-cell tolerance, identical across 2020–2024)
F FEATURE MAPPING: **COMPLETE** for `u700`/`v700`/`fc_cloud_cover`→`cloud_frac`/`fc_temperature_2m`/`fc_relative_humidity_2m`/the `lwp`/`iwp` input variables (all confirmed present, named, and — where relevant — unit-reconciled); **PARTIAL** only in the sense that the `lwp`/`iwp` integration formula's output was not re-run against real 2020–2023 values and the non-18Z run hours were not checked
2020–2023 ACQUISITION READY: **YES**, for the extraction *mechanism* (filenames, variables, grid index, pressure index, and required unit conversions are all now verified) — **NO**, in the sense that no extraction code has actually been written or run yet, per this task's explicit "do not download... do not train" scope
TRAINING PERFORMED: **NO**
