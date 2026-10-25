# Historical NWP Alternative Source Audit (2019–2023)

**Scope**: Research only, worked directly in this session, no subagents. **No new downloads
performed in this task** (per the task's explicit "do not download anything yet"). Evidence
below draws on (a) this investigation's own prior, already-performed live verification of the
MEPS archive (`CANDIDATE_L_DATA_ACQUISITION_FEASIBILITY.md` — lightweight catalog/`.dds`
checks already completed in an earlier turn, not re-fetched here) and (b) general domain
knowledge of publicly documented NWP archives, clearly labeled as such and not re-verified live
in this task. Where domain knowledge is used without live re-verification, it is marked
**[UNVERIFIED THIS SESSION]** rather than stated as confirmed fact.

---

## Candidate sources considered

### 1. MET Norway MEPS deterministic archive (`meps25epsarchive`) — already partially verified in this investigation

**This is not a new candidate** — it is the same archive already confirmed, in this
investigation's prior turn, to host `u700`/`v700`/`lwp_latest`/`iwp_latest`'s source variables
for 2020–2023 (packaged differently than 2024, requiring code reconstruction) and to be absent
the needed variables for 2019 (ensemble-only "vc" product that session's `.dds` check found).
Reusing that **already-obtained** evidence here rather than re-fetching:

- **Actual forecast runs, not reanalysis**: **YES, already confirmed** — MEPS is an
  operational, cycled NWP forecast system (8 runs/day, confirmed in
  `STAGE8_EXTERNAL_SOURCE_REACQUISITION_AUDIT.md`'s description of the related AROME-Arctic
  system, and directly in the file-naming convention `meps_det_2_5km_<date>T<HH>Z.nc` —
  `T18Z` etc. denotes a specific daily initialization/issue time, not a reanalysis timestamp).
- **Historical initialization/issue times**: **YES, already confirmed** — the archive is
  organized by exact date+init-hour folders (`meps25epsarchive/<YYYY>/<MM>/<DD>/`), already
  directly browsed for 2019 through 2023 in the prior turn.
- **Spatial resolution**: **YES** — 2.5 km grid, the same resolution F's own 2024 pipeline
  already uses (confirmed, same archive, same grid family).
- **Variables confirmed present for 2020–2023** (already directly inspected via `.dds` in the
  prior turn, not re-checked here): `x_wind_pl`/`y_wind_pl` (pressure-level wind, for
  `u700`/`v700`), `mass_fraction_of_cloud_condensed_water_in_air_pl`,
  `mass_fraction_of_cloud_ice_in_air_pl`, `surface_air_pressure` (for `lwp_latest`/`iwp_latest`).
  The 2019 ensemble "vc" product was already confirmed, in that same check, to lack all of
  these and to use an incompatible flattened 1-D grid.
- **`fc_cloud_cover`/`fc_temperature_2m`/`fc_relative_humidity_2m` equivalents in this same
  archive**: **UNKNOWN, not yet checked.** The prior turn's `.dds` grep for the 2022 combined
  file (`meps_det_2_5km_20220614T18Z.nc`) targeted `wind|cloud|pressure` and incidentally
  surfaced `cloud_area_fraction_ml` in the **2019** ensemble file's variable list (a model-level
  cloud-fraction field, physically close to but not identical in form to the percentage
  `fc_cloud_cover` F actually uses) — but **2m temperature and 2m relative humidity were never
  grepped for in either file**, and the 2022 file's full variable list was not dumped, only
  filtered for the specific wind/cloud/pressure terms already needed for §2b/§2c of the prior
  report. **This is the single most important open question this audit leaves unresolved**,
  and it was left unresolved deliberately, per this task's "do not download anything yet"
  instruction — confirming it would require one more light `.dds` listing call, not a bulk
  download, but that is explicitly out of scope for this turn.
- **Causal forecast-origin structure**: **YES, already established** — each file is indexed by
  issue time and lead time (confirmed by the `[6:1:24]` lead-time index range already used in
  F's own 2024 extraction script for this exact archive), meaning a 2019–2023 extraction using
  the same convention would preserve the identical "forecast made before the target
  observation" causal structure F already relies on — this is not a new causality question,
  it is the same archive and the same indexing convention already in use.

**Classification: VERIFIED historical forecast archive** for the wind/cloud-water variables
specifically (2020–2023 only, reconstruction-dependent per the prior report); **UNKNOWN** for
the cloud-cover/temperature/humidity family specifically, pending one unperformed, narrowly-
scoped variable-listing check.

### 2. ECMWF TIGGE (THORPEX Interactive Grand Global Ensemble) archive — domain knowledge only, not verified this session **[UNVERIFIED THIS SESSION]**

- **What it is**: a multi-center (ECMWF, NCEP, UKMO, Météo-France, and others) operational
  global ensemble **forecast** archive — genuine forecast runs at specific issue times, not
  reanalysis — maintained for research reproducibility, historically back to 2006, hosted at
  ECMWF and mirrored at NCAR's Research Data Archive.
- **Variables**: known to include total cloud cover, 2m temperature, and (via dewpoint or
  specific humidity) a route to 2m relative humidity, plus pressure-level wind — **variable
  coverage is plausibly compatible with F's needs**, but this is stated from general knowledge
  of the TIGGE variable catalogue, **not independently confirmed in this session**.
- **Spatial resolution**: TIGGE's native grids are coarse by this project's standards — on the
  order of 0.25°–0.5° (tens of km), far coarser than MEPS's 2.5 km. Given this investigation's
  own prior finding (the CAMS source, already evaluated for a different purpose in
  `STAGE8_2_ARCHIVE_EVIDENCE.md`, was explicitly down-rated for being "coarse relative to MEPS
  2.5 km... physical upside... low"), the same reasoning plausibly applies here, though not
  re-verified for TIGGE specifically.
- **Access mechanism**: typically requires a free ECMWF/NCAR account, not a fully open
  unauthenticated download — a real but modest access barrier, not independently tested here.
- **Classification: FORECAST ARCHIVE BUT WRONG SPATIAL/TEMPORAL RESOLUTION** (tentative,
  based on known TIGGE grid specs, not re-verified against this session's own data) —
  **flagged, not asserted as final**, since actual resolution adequacy for Nuolja's terrain was
  not tested here.

### 3. NOAA GFS historical forecast archive (NOMADS / NCEI model archive) — domain knowledge only **[UNVERIFIED THIS SESSION]**

- **What it is**: NOAA's Global Forecast System, archived operational forecast runs (not
  reanalysis), publicly available via NOMADS/NCEI, with a long historical record extending well
  before 2019.
- **Variables**: total/low/mid/high cloud cover, 2m temperature, 2m relative humidity (or
  specific humidity convertible to RH), pressure-level wind — all plausibly present, consistent
  with GFS's well-documented standard output variable set, **not independently confirmed here**.
- **Spatial resolution**: GFS's historical archive resolution has varied (0.5° earlier, 0.25°
  more recently) — still substantially coarser than MEPS's 2.5 km, same concern as TIGGE.
- **Classification: FORECAST ARCHIVE BUT WRONG SPATIAL/TEMPORAL RESOLUTION** (tentative, same
  caveat as TIGGE — not independently verified in this session).

### 4. DWD ICON / other European national NWP archives — domain knowledge only, low confidence **[UNVERIFIED THIS SESSION]**

- German, French, and other national NWP centers maintain operational forecast archives, but
  public, open, long-historical (2019–2023) access without institutional credentials is **not
  reliably known to this audit** for the Nuolja domain specifically — this is a genuine
  knowledge gap, not a negative finding. **Classification: UNKNOWN.**

### 5. ERA5 / any reanalysis product — explicitly excluded per task instruction

ERA5 and other reanalysis products **are not forecast-origin data** — they assimilate
observations from *after* the nominal time they describe, which would **break the exact causal
property this entire investigation has enforced from Candidate F onward** (every feature must
be derivable from information available strictly before the target observation). Per the
task's explicit instruction, reanalysis is **not** treated as an equivalent substitute here.
**Classification: REANALYSIS ONLY — excluded from consideration as a direct substitute.**

---

## Why MEPS remains the best-evidenced candidate rather than switching sources entirely

Switching to TIGGE or GFS would **trade a confirmed resolution match (2.5 km, same grid family
F already uses) for a confirmed resolution mismatch (tens of km)** — on a mountain station
(Nuolja, 702 m a.s.l., in complex terrain per the station source audit) where terrain-driven
cloud/radiation effects are already a first-order concern elsewhere in this investigation (the
terrain-horizon/obstruction features are part of F's own 37-feature contract). A resolution
downgrade of this magnitude is a real, substantive risk to feature comparability, not a minor
detail — and this concern is not speculative, it echoes this investigation's own prior
down-rating of CAMS for the same reason. **MEPS is also the only candidate in this audit with
any of its 2019–2023 availability independently, directly verified in this investigation**
(rather than asserted from general knowledge) — for the wind/cloud-water variables specifically.
The one open question (whether MEPS's own files also carry 2m-temperature/humidity/cloud-cover
equivalents) is a **small, well-scoped follow-up check against an already-identified archive**,
not a reason to search further afield first.

---

## ALTERNATIVE HISTORICAL FORECAST SOURCE: **PARTIAL**

BEST CANDIDATE: **MET Norway MEPS deterministic archive (`meps25epsarchive`) — same archive already confirmed in this investigation for `u700`/`v700`/`lwp`/`iwp`, 2020–2023**
F-COMPATIBLE CLOUD FORECAST: **UNKNOWN** — MEPS's own cloud-cover/2m-temperature/2m-humidity equivalents were not yet checked for 2019–2023 (deliberately not checked in this task, per "do not download anything yet"); no other candidate source's compatibility was independently verified either
F-COMPATIBLE OTHER NWP FEATURES: **PARTIAL** — `u700`/`v700`/`lwp`/`iwp` already confirmed present (2020–2023 only) and reconstructable in MEPS; not present for 2019
2019–2023 COVERAGE: **PARTIAL** — 2020–2023 confirmed reachable (MEPS); 2019 confirmed unreachable for the wind/cloud-water family via MEPS and not evaluated via any other source in this task
CAUSAL FORECAST-ORIGIN DATA: **YES** (for MEPS specifically, already established by this investigation's own prior indexing-convention check) — **UNKNOWN** for every other candidate listed, since none were independently re-verified this session
CANDIDATE L STILL VIABLE: **PARTIAL** — only if (a) the MEPS cloud-cover/temperature/humidity question above resolves favorably, (b) 2019 is either dropped from Candidate L's training window or solved by a still-unidentified source, and (c) the already-known reconstruction work (file-format adaptation, grid-index remapping) for 2020–2023 is actually carried out — none of which has been done
NEXT ACTION: Perform one additional, narrowly-scoped `.dds` variable-listing check against the already-identified 2020–2023 MEPS combined file (no data values, just the variable list) to determine whether `air_temperature_2m`, `relative_humidity_2m`, and a surface/near-surface cloud-cover-equivalent field exist in the same archive already confirmed for wind/cloud-water — this single check would resolve the one open question blocking a full classification, without searching for any new external source.
