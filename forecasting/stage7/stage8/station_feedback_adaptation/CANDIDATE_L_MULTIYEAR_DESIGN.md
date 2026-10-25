# Candidate L — Multi-Year (2019–2024) Training Design

**Scope**: Design audit only, worked directly in this session, no subagents. **No data
downloaded. No model trained. No modification of F, Stage8.1, or any artifact. No experiment
run.** This report checks the task's own premise against what is actually present in this
repository before designing around it — the premise ("the same Nuolja ANS_NMS station provides
SW_IN data from 2019–2025") is **upstream-source-level true but repository-level incomplete**,
and that gap is the central finding of this design audit.

---

## 0. Premise check — what "2019–2025 availability" actually means here

Two files already exist in this repository (not created in this session) that bear directly on
this design and must be reconciled before proceeding:

1. **`stage7/stage8/station_feedback_adaptation/NUOLJA_HISTORICAL_DATA_SOURCE_AUDIT.md`**
   (pre-existing): confirms the **upstream SITES data portal** publishes Nuolja `ANS_NMS`
   station-observed `SW_IN` (and a handful of co-located met variables: `TA`, `RH`,
   `TS_-0.01m`, `PRECIP`, `D_SNOW`) for **2019–2025**, but explicitly states **"DOWNLOAD
   PERFORMED: NO"** — none of 2019–2023's raw files exist locally. Only **2024 and 2025** raw
   station files are actually present in this repo, confirmed directly:
   `data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv` and
   `data/raw_2025_sites_download/SITES_MET_ANS_NMS_20250101-20251231_L2_SH.csv`.
2. **`stage7/stage8/STAGE8_EXTERNAL_SOURCE_REACQUISITION_AUDIT.md`** (pre-existing): confirms
   that even the **2024** AROME-Arctic NWP grid archive (the forecast source underlying
   `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, and the upstream
   `pred_stage3b_cloud_nwp`/`pred_stage4_fold` pipeline stages) was **not retrievable through
   the live THREDDS server** (which only retains a rolling 14–30-day operational window) and
   required a **separate, non-standard acquisition effort**, explicitly logged there as
   `SOURCE EXISTS BUT REQUIRED 2024 DATA UNAVAILABLE` before being resolved for 2024 alone.

**Consequence**: "the station provides SW_IN from 2019–2025" is true only for the **target
variable** (and a few raw met co-variates), via the station's own archive. It says nothing
about the **NWP-forecast-origin features** that make up the majority of F's 37/38-feature
contract, nor about the **multi-stage upstream model outputs** (`pred_stage3b_cloud_nwp`,
`pred_stage4_fold`, `lwp_latest`/`iwp_latest`, `u700`/`v700`, terrain features) that F also
depends on. **No evidence was found in this repository that any of these NWP-forecast-origin
or multi-stage-model inputs exist, or are even retrievable via a standard process, for any year
before 2024** — and 2024's own NWP grid archive already required nonstandard effort. This
directly shapes every answer below, especially §2 and §5.

---

## 1. Exact 2019–2024 data required, and how it would combine

To train Candidate L with **F's current feature contract unchanged**, every year from 2019–2023
would need, in addition to the already-available station `SW_IN`:

| Feature group | Source | Confirmed present for 2019–2023? |
|---|---|---|
| `solar_elevation`, `solar_zenith`, `clearsky_ghi` (pure astronomy/geometry) | Computable from date/location alone, no external data needed | **Yes — trivially computable for any year**, no acquisition risk |
| `terrain_horizon_elevation_deg`, `terrain_elevation_margin_deg`, `terrain_solar_obstruction_flag`, `clearsky_ghi_terrain_adjusted` | Static terrain profile (`stage7_5_terrain_horizon/nuolja_horizon_profile_360deg.csv`) | **Yes — terrain geometry is time-invariant**, the same profile applies to any year |
| `ctx_*` (trailing actual-observation statistics) | Derived purely from the station's own `SW_IN` series | **Yes, once the raw 2019–2023 station files are downloaded** (not yet done, and out of this task's scope — "do NOT download data") |
| `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m` (NWP **forecast**-origin) | AROME-Arctic / MEPS archive | **NOT confirmed available** — even 2024's archive required non-standard acquisition (§0); no evidence any 2019–2023 archive is retrievable at all |
| `pred_stage3b_cloud_nwp`, `pred_stage4_fold` (upstream pipeline model outputs) | Outputs of this project's own earlier Stage 3b/Stage 4 models, themselves trained/run on NWP inputs | **NOT confirmed available** — these are derived artifacts of this project's own pipeline for 2024/2025 specifically; no evidence they have ever been generated for any other year |
| `lwp_latest`, `iwp_latest`, `u700`, `v700` | Additional NWP-derived fields (liquid/ice water path, 700hPa wind) | **NOT confirmed available** pre-2024, same NWP-archive constraint |

**If and only if** all of the above were resolved (explicitly not attempted here — "do NOT
download data"), combination would follow exactly the existing pattern in
`build_corrected_feature_matrix.py`: per-year raw ingestion, merge on `(forecast_start,
horizon_hour)` / `timestamp` keys, then concatenate years into a single matrix before any
EVEN/ODD assignment (§3).

**Realistic near-term combination, given confirmed availability**: only the **station-SW_IN
and pure-geometry/terrain features** can be reliably extended to 2019–2023 without new NWP
acquisition work. A reduced-feature Candidate L (fewer than F's 37/38 inputs) is the only
version of this design currently supported by confirmed data — **not** a straightforward
multi-year retrain of F's existing architecture (§5 returns to this directly).

---

## 2. Whether F's current feature construction remains valid across all years

**No, not without further, unperformed data acquisition** — for two independent reasons, not
one:

1. **Data-availability reason** (§1): the majority of F's features are NWP-forecast-origin or
   derived from this project's own upstream pipeline stages, neither of which is confirmed to
   exist for 2019–2023, and the one confirmed precedent (2024's own NWP archive) was already a
   non-trivial acquisition exercise, not a routine download.
2. **Instrumentation/measurement-continuity reason** (flagged, not yet audited — see §7): even
   where raw station data nominally exists (SW_IN itself), the pre-existing
   `NUOLJA_HISTORICAL_DATA_SOURCE_AUDIT.md` only *infers* (`[INFERRED]`, not `[VERIFIED]`) that
   2019–2023 completeness is similar to 2024/2025's near-100% continuity — it does not confirm
   sensor consistency, calibration history, or any instrument replacement/recalibration event
   across 2019–2025. `build_corrected_feature_matrix.py`'s feature construction (e.g. `ctx_*`
   trailing statistics) implicitly assumes a continuous, consistently-calibrated sensor series
   — an assumption **not yet verified** for the pre-2024 years.

**Partial exception**: the pure-geometry features (`solar_elevation`, `solar_zenith`,
`clearsky_ghi`, terrain features) are time-invariant in construction and **do** remain valid
across any year by definition — they depend only on date/location/static terrain, not on any
externally-sourced time series.

---

## 3. Correct temporal train/validation design

**If** a multi-year feature matrix were eventually built (not attempted here), the correct
design, consistent with this investigation's own established governance pattern
(`train_corrected_stage8_1_model.py`'s EVEN/ODD split, reused byte-identically by every
candidate A–K so far):

- **Training window**: 2019–2024 (six years, per the task's framing), split **EVEN/ODD by the
  same positional-alternation-on-sorted-origins rule** already used for 2024 alone — i.e. sort
  *all* origins across 2019–2024 chronologically, then `i % 2`. This preserves the existing
  convention rather than inventing a new one, and keeps the same "tune on ODD, never on 2025"
  discipline.
- **Caveat carried over from the Candidate J/K analyses already in this directory** (see
  `F_TRAINING_STRATEGY_DECISION.md` §8, `CANDIDATE_K_DESIGN_AUDIT.md` §6): positional EVEN/ODD
  interleaving on a now much longer multi-year sequence still produces temporally-adjacent
  EVEN/ODD pairs, not a block split — the same entanglement caveat applies, just over a longer
  calendar span.
- **Validation**: 2024-ODD (or, if 2024 origins are redistributed across EVEN/ODD within the
  2019–2024 pool, whichever ODD-labeled origins fall in 2024, to remain comparable to F's own
  ODD metric) — used only for any hyperparameter choices, never for final comparison.
- **Blind**: **2025, untouched**, exactly as for every prior candidate (F, G, H, I, J, K-design)
  — this is non-negotiable per the task's own instruction and this investigation's standing
  rule.

**This design question is answerable in the abstract regardless of the data-availability
blocker in §1/§2** — it is a protocol question, not a data question, and the answer is: reuse
the existing EVEN/ODD/blind convention exactly, extended over more years, with the same
disclosed interleaving caveat.

---

## 4. Avoiding leakage / preserving 2025 as a true blind set

- **2025 must never appear in training or hyperparameter selection** — identical rule to every
  prior candidate (A through K-design). No new leakage vector is introduced by adding more
  pre-2024 years; the only new consideration is making sure any pre-2024 NWP/station data
  acquisition (if ever performed, not here) pulls data **strictly dated before 2025-01-01**, so
  no future information from the blind period is accidentally bundled into the "historical"
  download.
- **Within the training pool itself** (now spanning 2019–2024), the EVEN/ODD interleaving
  caveat (§3) is the main structural risk to document, not a new leakage mode — it was already
  disclosed for the single-year case and simply persists at larger scale.
- **Instrumentation-consistency risk** (§7) is a distinct, non-leakage risk: if the sensor or
  its calibration changed at some point in 2019–2023, naively pooling those years with 2024
  could inject a **distribution-shift confound**, not a temporal leak — i.e., Candidate L could
  appear to "learn" something from additional years that is actually an artifact of a sensor
  change, not a genuine solar-irradiance pattern. This must be screened (§7) before any training
  is attempted, not discovered after the fact.

---

## 5. Should F's existing architecture/features be retained unchanged for the first test?

**No — not as currently specified, and this is the single most important answer in this
report.** Retaining F's exact 37/38-feature contract unchanged for a first Candidate L test
would require every NWP-forecast-origin and multi-stage-pipeline-output feature to exist for
2019–2023, which **§1/§2 establish is not currently confirmed, and the one close precedent
(2024's own NWP grid archive) was already a non-standard acquisition effort** — attempting this
as the *first* test would front-load the hardest, least-certain part of the whole design before
any evidence of benefit exists.

**A more defensible first test, if this line of research is pursued at all**: a **deliberately
reduced-feature variant** of Candidate L, restricted to the features confirmed extendable
without new NWP acquisition (§1's "Yes" rows): `solar_elevation`, `solar_zenith`,
`clearsky_ghi`, terrain features, and the `ctx_*` station-history statistics (once 2019–2023
raw SW_IN is downloaded — itself out of this task's scope). This is **explicitly not the same
architecture as F** (F's 37/38 features), so any comparison would need to be framed as "does
more station-history-only data help a geometry+persistence-only model," a different and
narrower question than "does more data improve F" — stated plainly so the eventual experiment
is not misdescribed as a direct F extension.

---

## 6. Exact metrics and statistical comparison against frozen F

If Candidate L (in whichever feature form ends up buildable) is eventually trained, the
comparison protocol should be **identical in form** to every prior candidate's evaluation in
this investigation, for direct comparability:

- Blind-2025 MAE, RMSE, bias, nMAE (daytime rows, `is_night_causal` convention preserved).
- H1–H24 horizon breakdown.
- Targeted-regime breakdowns already established as informative in this investigation:
  high-elevation (≥30°), transition-cloud, Aug–Sep, and (if L retains the relevant features)
  the joint high-elevation×transition-cloud cell.
- **Corrected** bootstrap 95% CI (`research_utils.bootstrap_mae_diff_ci_corrected()`) for
  (L − F), not the uncorrected original utility — same standard applied to every candidate from
  J onward.
- If L's feature set is the reduced (non-F-equivalent) variant from §5, the comparison must
  also explicitly report **(L − control)**, not only (L − F), since L in that form is testing a
  different, narrower hypothesis than "improving F" per se, and conflating the two comparisons
  would overstate what a reduced-feature L vs. F result actually shows.

---

## 7. Whether 2019–2024 distribution/measurement changes need auditing before training

**Yes — required, not optional, and not yet done.** Specifically needed before any training
(not performed in this report):

- **Instrument/calibration history**: confirm whether the Apogee SP110 pyranometer (or any
  other sensor contributing to the feature set) was replaced, recalibrated, or relocated at any
  point 2019–2024 — the pre-existing source audit only names the *current* instrument and
  height, without confirming it has been constant since 2019.
- **Missing-data patterns**: the pre-existing source audit explicitly marks pre-2024
  completeness as `[INFERRED]`, not `[VERIFIED]` — actual gap patterns (e.g. extended winter
  rime-icing outages) must be checked per year once (if ever) downloaded, since the `ctx_*`
  feature construction already has an explicit minimum-history fallback (`< 24` context
  readings → zero-filled, per `build_corrected_feature_matrix.py:175-176`) that silently
  degrades feature quality during gaps — more gap-prone years could systematically inject more
  zero-filled `ctx_*` rows, a distribution shift the model would need to tolerate, not benefit
  from.
- **Any station relocation or structural change** (e.g. a change in sensor height, which the
  current audit lists precisely at `2.86 m` — any change to this would alter the physical
  meaning of the measured irradiance, not just its statistics) must be ruled out.
- **Climate-driven distribution shift itself is not a disqualifying issue** (more years of
  genuine solar-irradiance variability is exactly what more training data is supposed to
  capture) — the audit requirement here is specifically to separate genuine inter-annual
  variability from **instrumentation artifacts**, which would corrupt rather than inform
  training.

---

## 8. Should Candidate L be compared against both F and frozen Stage8.1?

**Yes, both, for different reasons:**
- **Against F**: F is the current research control (confirmed standing fact, carried over from
  every report in this investigation) — the primary question for any new candidate is "does
  this beat F," per the existing promotion-bar convention.
- **Against frozen Stage8.1**: retained as the ultimate production-governance reference point
  throughout this entire investigation (every candidate A–K has reported this comparison) —
  dropping it for L would break the one consistent comparison axis that spans the whole
  investigation and would make L's result harder to place in context against the full history
  (e.g. Candidate J passed vs. control but not vs. F — the same three-way framing must be
  preserved for L).

---

## DESIGN VALID: **NO** (as scoped — full F-architecture multi-year retrain on 2019–2024)

**Blocking issue**: F's feature contract is dominated by NWP-forecast-origin fields and
upstream multi-stage pipeline outputs (`fc_cloud_cover`, `fc_temperature_2m`,
`fc_relative_humidity_2m`, `pred_stage3b_cloud_nwp`, `pred_stage4_fold`, `lwp_latest`,
`iwp_latest`, `u700`, `v700`) that are **not confirmed to exist, or to be retrievable through
any standard process, for 2019–2023** — and the one directly relevant precedent in this
repository (`STAGE8_EXTERNAL_SOURCE_REACQUISITION_AUDIT.md`) shows that even **2024's** own NWP
grid archive required non-standard acquisition effort, not a routine download. Only the
station-observed `SW_IN` target and a handful of co-located met variables are confirmed
available upstream for 2019–2025 (and not yet downloaded for 2019–2023 even for those).
**A full-feature-parity Candidate L, as the task frames it ("train a new station-specific
solar model" implicitly using F's existing feature construction), cannot be designed as
data-ready today** — this is a data-acquisition blocker, not a methodological one; §3/§4/§6/§8
(temporal design, leakage control, metrics, and comparison targets) are all independently
resolved and valid, and would apply immediately once/if the data blocker in §1/§2/§5 is
resolved through a separate, explicitly-authorized acquisition effort (which this task
correctly did not authorize: "do NOT download data").

A **narrower, currently-buildable variant** (§5: geometry + terrain + station-history-only
features, explicitly not F-equivalent) is more defensible as a first test once 2019–2023 raw
station files are downloaded — but that download, and that narrower model, are each separate,
smaller follow-on decisions, not what was asked for in this task's framing of "Candidate L" as
an F-equivalent multi-year retrain.

TRAINING DATA: **2019–2024, conditional on (a) downloading and auditing 2019–2023 raw station data for instrumentation/continuity issues (§7), and (b) either acquiring equivalent NWP-forecast/multi-stage-pipeline features for those years or redefining Candidate L as a reduced, non-F-equivalent feature set (§5) — neither has been done**
BLIND DATA: 2025
BASELINE: F
NEXT STEP: Authorize and perform the already-scoped 2019–2023 raw station `SW_IN` download (per the pre-existing `NUOLJA_HISTORICAL_DATA_SOURCE_AUDIT.md` §10 plan) and a parallel feasibility check for whether equivalent NWP-forecast data for those years can be acquired at all, before any Candidate L feature design is finalized.
