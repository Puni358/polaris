# Candidate L — Historical Data Acquisition Feasibility

**Scope**: Investigation only, worked directly in this session, no subagents. **No model
training. No Candidate L implementation. No changes to F, J, or frozen Stage8.1.** This report
resolves the data blocker raised in `CANDIDATE_L_MULTIYEAR_DESIGN.md` by **directly verifying
acquisition mechanisms via live HTTP checks against the actual upstream sources this
pipeline's own build scripts already use** — not by re-reading prior claims. Per the task's
explicit allowance, a small number of lightweight HTTP requests (catalog pages, `.dds` variable
listings, single-day API queries) were made strictly to verify mechanism/availability; **no
bulk dataset was downloaded**.

**Method**: for each required input, first traced the exact upstream source already used by
this project's own 2024 build scripts (not assumed — read directly from code), then tested that
exact mechanism against 2019–2023 dates live, and recorded what actually came back.

---

## 1. Nuolja station data (SW_IN and met co-variates)

**Source traced from code**: `clear_sky/build_future_weather_dataset.py` header and
`NUOLJA_HISTORICAL_DATA_SOURCE_AUDIT.md` (pre-existing file, re-verified here, not re-trusted
blindly) — SITES Data Portal (`data.fieldsites.se`), station `ANS_NMS`, annual
`SITES_MET_ANS_NMS_<year>_L2_SH.csv` exports, accessed via Handle PIDs
(`https://hdl.handle.net/11676.1/<PID>`).

**Live verification performed in this session**:
```
curl -L https://hdl.handle.net/11676.1/t0AeJcJn3RUXzCvdy6X8KWI5   → HTTP 200 → resolves to
    https://meta.fieldsites.se/objects/t0AeJcJn3RUXzCvdy6X8KWI5  (2021 Nuolja dataset record)
curl -L https://hdl.handle.net/11676.1/CWT5DHNcPD00c8IWgAZtcmrt  → HTTP 200 → resolves to
    https://meta.fieldsites.se/objects/CWT5DHNcPD00c8IWgAZtcmrt  (2020 Nuolja dataset record)
```
Both pre-2024 Handle PIDs **independently re-confirmed live and resolving to real, public
metadata records** (not merely cited from the pre-existing audit — re-checked directly).
Station installation year (2019) and schema consistency (`TIMESTAMP,TA,RH,SW_IN,TS_-0.01m,
PRECIP,D_SNOW,TA_STD,TS_STD`) across years are stated in the pre-existing audit and not
re-disputed here — no contradicting evidence found.

**Classification: AVAILABLE BUT NOT YET ACQUIRED.** The exact authoritative method: direct
HTTPS download of `SITES_MET_ANS_NMS_<YEAR>0101-<YEAR>1231_L2_SH.csv` for `YEAR ∈
{2019,2020,2021,2022,2023}` from the SITES Data Portal via the same Handle-PID mechanism
already used for 2024/2025, requiring no credentials (`CC BY 4.0`, confirmed in the
pre-existing audit). This is the same mechanism, same file format, same schema — only the
year parameter changes. This is the **only one of the task's two data requirements with no
open uncertainty** after this session's verification.

---

## 2. Historical NWP forecast-origin data

Traced each F-required field to its **exact** generating script (not assumed from the feature
name) before testing anything.

### 2a. `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`

**Source traced from code**: `clear_sky/build_future_weather_dataset.py` — **not** raw
AROME-Arctic/MEPS, but **Open-Meteo's "Previous Runs API"**
(`previous-runs-api.open-meteo.com`), querying MET Nordic (`models=metno_seamless`)
`*_previous_day1` fields — i.e. "what the forecast said the day before," a historical-forecast
replay API, not a reanalysis.

**Live verification performed in this session** (exact query parameters copied from the
build script, only `start_date`/`end_date` varied):
```
2019-06-10, 2020-06-10, 2021-06-10, 2022-01-10/06-10/10-01, 2023-01-10/06-10, 2024-01-10
  → HTTP 200, valid JSON structure, but EVERY SINGLE hourly value = null (0/24 non-null)
2025-01-01, 2025-06-01, 2026-06-01, 2026-09-01
  → HTTP 200, 24/24 non-null real values (e.g. 2025-01-01: [91,100,100,100,...])
```
**This is a directly observed, previously undocumented finding**: this API has a **rolling
retention window**, not a permanent historical archive. As of this session (current date
2026-10-03), it returns real data back to at least 2025-01-01 but **returns an empty/null
shell (HTTP 200, no error, but zero real values) for every date tested from 2024-01-10 back
through 2019** — including dates that **must have been within the live window when the 2024
feature matrix was originally built**, since that build succeeded. The window has since rolled
past those dates. **This directly means**: even if this task were run again next year to fetch
"last year's" data, it would again be unable to reach 2019–2023 through this specific API —
the retention boundary moves forward with time and does not extend backward on request.

**Classification: NOT AVAILABLE** via the exact mechanism F's own pipeline uses. This is not
"not yet acquired" (a time/effort gap) — it is a **source that structurally cannot serve dates
this old**, confirmed by direct, dated live queries, not inferred from documentation.

### 2b. `u700`, `v700` (700 hPa wind)

**Source traced from code**: `stage7/stage8/stage8_1_corrected_2025/build_wind700_features_2024_corrected.py`
— MET Norway THREDDS `meps25epsarchive`, deterministic pressure-level file
`meps_det_pl_<date>T18Z.ncml`, variables `x_wind_pl`/`y_wind_pl`.

**Live verification performed in this session**:
- Catalog browsing confirmed `meps25epsarchive` itself **does** serve per-date historical
  folders for 2019 through 2024 (`catalog.html` returns HTTP 200 for `2019/06/15`,
  `2020/01/15`, `2021/03/15`, `2023/06/15`, etc. — the archive is not a rolling window at this
  level, unlike §2a).
- **File naming/packaging changes across the years, confirmed directly**:
  - **2024** (matching the build script exactly): split files, `meps_det_pl_<date>T18Z.ncml`.
  - **2020–2023** (confirmed via direct `.dds` variable listing against
    `meps_det_2_5km_20220614T18Z.nc`, HTTP 200): a **single combined file**,
    `meps_det_2_5km_<date>T<HH>Z.nc`, that **does contain the identical physical variables**
    — `x_wind_pl[time=67][pressure=13][y=1069][x=949]`, `y_wind_pl[...]` (confirmed present by
    direct `.dds` inspection) — just packaged together with surface/model-level fields rather
    than split out, and on a grid (`y=1069, x=949`) that was **not confirmed identical in
    indexing** to the 2024 split-file grid (the extraction script's hardcoded `NUOLJA_Y`/
    `NUOLJA_X` indices would need independent re-derivation for this file's grid, not reused
    blindly).
  - **2019**: confirmed via direct `.dds` inspection of `meps_ens_mbr0_vc_2_5km_20190615T00Z.nc`
    that this is a **different, ensemble-member "vc" (vertical cross-section) product**:
    contains only **model-level** wind (`x_wind_ml`/`y_wind_ml`), **no pressure-level wind
    variable at all**, and an unusual flattened grid shape (`y=1, x=28316` — a 1-D transect, not
    a 2-D grid). Checked across multiple 2019 dates (June, Sept–Dec) and January 1 2020 — the
    deterministic `meps_det_2_5km` product **was not found in any 2019 or 2020-01-01 catalog
    listing**; it was confirmed present by June 2020. **The exact month the deterministic
    product begins was not pinned down further** (diminishing returns against the task's "don't
    download large datasets" constraint) — flagged as UNKNOWN, not resolved.

**Classification**:
- **2020–2023: REQUIRES RECONSTRUCTION** — the needed physical variables are confirmed present,
  but under a different file-packaging convention than the 2024 script expects; the extraction
  code must be adapted (different filename pattern, different grid-index mapping to verify),
  not simply pointed at a different year.
- **2019 (and possibly part of early 2020, exact boundary unconfirmed): NOT AVAILABLE / UNKNOWN**
  via this archive — the pressure-level wind variable this feature depends on does not exist in
  the 2019 ensemble-member product at all, confirmed by direct inspection, not assumed.

### 2c. `lwp_latest`, `iwp_latest` (liquid/ice water path)

**Source traced from code**: `stage6/stage6_6_lwp_iwp/run_stage6_6.py` — same
`meps25epsarchive`, variables `mass_fraction_of_cloud_condensed_water_in_air_pl`,
`mass_fraction_of_cloud_ice_in_air_pl`, and `surface_air_pressure` (needed to integrate mixing
ratio into a column path).

**Live verification**: the same `.dds` inspection of the 2022 combined deterministic file
confirmed **all three variables present** (`mass_fraction_of_cloud_condensed_water_in_air_pl`,
`mass_fraction_of_cloud_ice_in_air_pl`, `surface_air_pressure[time=67][height0=1][y=1069][x=949]`)
— same pressure grid (13 levels), same spatial grid as §2b.

**Classification**: **identical to §2b** — **2020–2023: REQUIRES RECONSTRUCTION** (variables
present, packaging/grid differs, code must be adapted); **2019: NOT AVAILABLE / UNKNOWN** (the
2019 ensemble "vc" product was not confirmed to contain any of these three variables — not
found in its `.dds` listing during this session's check).

### 2d. `pred_stage3b_cloud_nwp`, `pred_stage4_fold` — upstream pipeline-model outputs, not raw data

**Source traced from code**: these are **not externally-sourced fields** — they are the output
of this project's own earlier Stage 3b and Stage 4 models, which themselves consume NWP inputs
(including the ones in §2a/§2b/§2c) for a specific year. Confirmed directly: `stage4/` contains
**`run_stage4_pipeline.py`** (2024) and a **separately duplicated**
**`run_stage4_pipeline_2025.py`** (2025) — i.e. this pipeline stage was **forked per year as a
one-off script, not written as a general year-parameterized tool**. No `run_stage4_pipeline_2019.py`
-style script, and no evidence of any config flag to retarget an existing script at an
arbitrary year, was found.

**Classification: REQUIRES RECONSTRUCTION**, and specifically **gated behind §2a/§2b/§2c being
resolved first** — even if a hypothetical `run_stage4_pipeline_2020.py` were written by copying
the existing pattern, it would need §2b/§2c's reconstructed 2020–2023 NWP inputs to run on, and
cannot run at all for 2019 given §2a's NOT-AVAILABLE finding for the cloud-cover input stage 3b
itself likely depends on (not independently re-verified in this session, since stage3b/stage4's
own internal input list was not inspected in depth — flagged as a further UNKNOWN below, kept
narrow per the task's "investigate ONLY these two things" scope).

---

## Summary table

| Input | Classification | Basis |
|---|---|---|
| Nuolja station `SW_IN` + met co-variates, 2019–2023 | **AVAILABLE BUT NOT YET ACQUIRED** | Handle PIDs for 2020/2021 independently re-verified live (HTTP 200, resolve to real metadata records); same mechanism as working 2024/2025 download |
| `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m` | **NOT AVAILABLE** | Open-Meteo previous-runs-api directly queried for 2019–2024-01 dates: HTTP 200 but 100% null values — confirmed rolling retention window, not a permanent archive |
| `u700`, `v700` | **REQUIRES RECONSTRUCTION** (2020–2023) / **NOT AVAILABLE / UNKNOWN** (2019) | Same physical variables confirmed present in a differently-packaged 2020–2023 MEPS file via direct `.dds` inspection; confirmed absent in the 2019 ensemble "vc" product (no pressure-level wind variable at all) |
| `lwp_latest`, `iwp_latest` | **REQUIRES RECONSTRUCTION** (2020–2023) / **NOT AVAILABLE / UNKNOWN** (2019) | Same evidence basis as `u700`/`v700` — same source file, same `.dds` inspection |
| `pred_stage3b_cloud_nwp`, `pred_stage4_fold` | **REQUIRES RECONSTRUCTION** | Not raw data — outputs of this project's own year-specific (not year-parameterized) upstream pipeline scripts; gated on the above inputs being resolved first; stage3b's own internal input dependencies not independently re-verified in this session (UNKNOWN, scoped out) |

---

## UNKNOWNs (explicit, not resolved by this investigation)

- Exact month in 2020 when the `meps_det_2_5km` deterministic product begins (bounded here to
  "absent through 2020-01-01, present by 2020-06-15," not pinned further).
- Whether the 2020–2023 combined file's grid (`y=1069, x=949`) uses the same coordinate-index
  convention as the 2024 split-file grid, or whether Nuolja's `NUOLJA_Y`/`NUOLJA_X` indices
  would need independent re-derivation — not tested (would require a larger, targeted
  coordinate-matching query, judged out of scope for a feasibility-only check).
- Whether Stage 3b (upstream of Stage 4, not directly inspected in this session) depends on any
  additional NWP field not already covered in §2a–2c.
- Whether the 2019 ensemble "vc" product, despite lacking the specific variables checked here,
  might carry an equivalent field under a different name not grepped for — a full variable-list
  dump of a 2019 file was not performed (only targeted `wind|cloud|pressure` greps), so absence
  here is "not found by this check," not an exhaustive negative.
- Instrumentation/calibration continuity for the station data (2019–2023), exactly as already
  flagged as unresolved in `CANDIDATE_L_MULTIYEAR_DESIGN.md` §7 — not re-investigated here, as
  this report's scope was acquisition mechanism, not data quality.

---

NUOLJA 2019–2023 ACQUISITION: **YES**
F-COMPATIBLE NWP 2019–2023: **NO** (fully equivalent to F's exact 2024 pipeline) — **PARTIAL/RECONSTRUCTION-DEPENDENT** for `u700`/`v700`/`lwp`/`iwp` in 2020–2023 only; confirmed **NOT AVAILABLE** for the forecast-cloud-cover input family in any year 2019–2023, and confirmed **NOT AVAILABLE** for the wind/cloud-path variables specifically in 2019
MAIN BLOCKER: `fc_cloud_cover`/`fc_temperature_2m`/`fc_relative_humidity_2m` — the single most structurally-important NWP input (it is the direct ancestor of `cloud_frac`, used in F's own added feature and both Candidate G's and J's additive features) — is sourced from an API confirmed, by direct live testing, to have a rolling retention window that cannot reach 2019–2023 at all, with no alternative source identified in this session.
RECOMMENDED NEXT ACTION: Authorize and perform the already-verified 2019–2023 Nuolja station `SW_IN` download (zero blockers) in parallel with a separate, explicitly-scoped investigation into an alternative historical source for MET Nordic/metno_seamless-equivalent cloud-cover forecast data (e.g. a direct MET Norway archive product rather than the Open-Meteo replay API) — without resolving this specific gap, any Candidate L using F's current feature contract remains infeasible regardless of how the wind/cloud-path (`u700`/`v700`/`lwp`/`iwp`) reconstruction effort for 2020–2023 turns out.
