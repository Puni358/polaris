# POLARIS STAGE 8.6 — NEXT-ROUTE SCIENTIFIC FEASIBILITY STUDY
## Nuolja SW_IN H1–H24 Forecasting: Candidate Causal Information Sources Beyond Stage 8.5

**Project:** POLARIS
**Stage:** 8.6 (Research / Feasibility — post Stage 8.5 closure)
**Status:** **RESEARCH ONLY. NO CODE. NO EXPERIMENT STARTED. NO ODD ACCESS.**
**Current Operational Champion (unchanged):** Stage 8.1 U700+V700 Steering Wind Model — Held-out ODD MAE = **36.188657 W/m²**, ODD nMAE = **28.0688%**

---

## 0. Scope and Method

This report evaluates candidate causal information sources for the *next* POLARIS feature experiment, in the decision-oriented format requested, using:

- The full tested/rejected history in `POLARIS_MASTER_HANDOFF.md` and Stage 8.0–8.5 reports (treated as authoritative and not re-litigated).
- Current documentation from ECMWF/Copernicus ADS, MET Norway, and NASA sources (web-verified during this stage; citations given inline).
- A strict three-way epistemic tag on every factual claim:
  - **[VERIFIED]** — confirmed against a Stage 8.x file-level audit, or against current authoritative documentation retrieved during this stage.
  - **[INFERENCE]** — a reasonable derived conclusion from verified facts, not itself directly measured.
  - **[CONDITIONAL/UNVERIFIED]** — plausible but not empirically confirmed for the Nuolja 2024 archive; requires a feasibility sub-step before a forecasting experiment can be authorized.

No route below is treated as "untested" simply because it wasn't in the rejected list — each is individually assessed against the actual Stage 8.0–8.5 evidence.

---

## 1. Candidate A — CAMS Aerosol / Atmospheric Composition (Global Atmospheric Composition Forecasts)

### 1. Physical mechanism
Aerosol particles (dust, biomass-burning smoke, sulphate, sea salt) attenuate direct-beam shortwave radiation via scattering and absorption, and increase the diffuse fraction, **independently of cloud presence**. This is a distinct error mechanism from anything POLARIS has tested: it operates under nominally clear or thin-cloud skies where cloud-based features (LWP/IWP, cloud fraction, steering wind) carry little or no signal, so residual error under those conditions is currently unexplained by any champion feature. **[INFERENCE]**

### 2. Information novelty
No prior POLARIS stage has ingested any atmospheric-composition variable (aerosol optical depth, water vapor column, ozone column). Stage 6.6 (LWP/IWP), Stage 7.5 (terrain), Stage 8.1 (U700/V700), and Stage 8.5 (spatial cloud/advection) are all cloud- or dynamics-based. CAMS aerosol data is a genuinely new physical axis, not a renamed cloud or wind feature. **[VERIFIED — by exclusion, cross-checked against the full tested/rejected list]**

### 3. Causality
- CAMS Global Atmospheric Composition Forecasts are issued twice daily at 00 and 12 UTC. **[VERIFIED — ECMWF Confluence documentation]**
- Documented data-availability guarantee: the 00 UTC run is guaranteed available by **10:00 UTC** same day; the 12 UTC run is guaranteed available by **22:00 UTC** same day. **[VERIFIED — ECMWF Confluence "CAMS: Global atmospheric composition forecast data documentation"]**
- For a forecast origin at $t_0 = 00{:}00$ UTC on day D, the most recent run satisfying strict operational causality ($t_{\text{pub}} \le t_0$) is the **D-1 12Z run**, guaranteed available by 22:00 UTC on D-1 — a full **2-hour causal safety margin before $t_0$**, and a **12-hour minimum lead time** at $t_0$ itself (H1…H24 correspond to forecast lead hours 13–36, well inside the 120-hour forecast range). **[INFERENCE from verified issuance/availability facts]**
- This is a *cleaner* causal margin than the currently-frozen champion's own U700/V700 features, which use the D-1 18Z MEPS run (6-hour lead at $t_0$). **[INFERENCE]**
- Distinguishing acquisition/issuance/publication/valid time exactly as required: model issuance = 12:00 UTC D-1; publication/availability guarantee = 22:00 UTC D-1; valid times used = D 00:00 through D+1 00:00 (H1–H24); all four are causal relative to $t_0$. **[VERIFIED reasoning chain]**

### 4. Spatial representativeness
Grid spacing is $\approx 0.4^\circ \times 0.4^\circ$, roughly 44 km (N–S) × 17 km (E–W) at 68°N. **[VERIFIED — ADS/Confluence documentation]** This is coarse relative to MEPS (2.5 km) and the 30 m DEM — but aerosol/smoke plumes are synoptic-to-regional-scale phenomena (typically 10s–100s of km), unlike the sub-grid-scale terrain-driven cloud variability that caused Stage 8.5's spatial cloud features to fail. A 40 km cell is a physically appropriate resolution for *this* variable family, even though the same resolution was inadequate for cloud fields. **[INFERENCE, but well-grounded in the physical scale difference between aerosol transport and orographic cloud formation]**

### 5. Temporal resolution
Single-level fields (including total/species-resolved aerosol optical depth) are archived **hourly** to lead hour 120; multi-level fields are 3-hourly. **[VERIFIED — ECMWF documentation]** Aerosol optical depth is a single-level (total-column) diagnostic, so hourly H1–H24 alignment is directly supported without interpolation.

### 6. Polar conditions
- Aerosol optical depth in the CAMS composition model is computed from the assimilation/forecast system itself (not a solar-channel retrieval), so — unlike VIIRS/NWC SAF cloud microphysics — **it does not go blind during polar night**; it remains defined at all solar zenith angles. **[VERIFIED — CAMS provides AOD "not only for daytime but also for nighttime," per literature on CAMS vs geostationary AOD products]**
- Its *predictive relevance* to SW_IN is naturally zero when SZA is such that there is no sunlight to attenuate — this is not a data-availability problem but a physically correct null effect, and is already consistent with POLARIS's causal night-zero-forcing rule.
- Baseline background AOD over Arctic Scandinavia is low (roughly 0.02–0.08 at 550 nm in clean conditions) **[CONDITIONAL — consistent with Baltic/Fennoscandian AERONET climatology literature, but not verified against the specific Nuolja/Abisko grid cell for 2024]**, punctuated by episodic long-range wildfire-smoke transport events (documented Canadian/Siberian smoke intrusions into Scandinavia) during which AOD can spike sharply and surface irradiance can be measurably reduced. **[VERIFIED mechanism from literature; magnitude and frequency specifically at Nuolja in 2024 is CONDITIONAL/UNVERIFIED until the archive is pulled]**
- Net implication: expected effect size is small most of the year and episodically large — a plausible signature for an error-*reducing* feature that a tree-based model can exploit without hurting the median case, but only if the small number of high-AOD 2024 origins land with enough weight in the loss.

### 7. Data availability
- **Exact product:** `cams-global-atmospheric-composition-forecasts`, ECMWF Atmosphere Data Store (ADS). **[VERIFIED — product exists, documented, historical archive since 2015]**
- **Exact variables (minimal set):** `total_aerosol_optical_depth_550nm` (or the species-resolved variant if total is judged too smoothed: `dust_aerosol_optical_depth_550nm`, `biomass_burning_aerosol_optical_depth_550nm`), `total_column_water_vapour`, `total_column_ozone`.
- File-level extraction for the specific 347 Nuolja origins in 2024 has **not** been performed (no Stage 8.x file-level CAMS pull exists yet). This must be treated as **CONDITIONAL until extracted**, exactly as required by the audit standard applied to every other candidate in this study.
- Format: GRIB/NetCDF via `cdsapi`. **[VERIFIED]**

### 8. Operational feasibility
Medium complexity: one authenticated `cdsapi` client call per D-1 12Z run, single-level hourly variables, small file size (~4 MB/day per the Stage 8.2 audit's own estimate for CAMS). No spatial subsetting complexity comparable to VIIRS HDF5 swath handling or NWC SAF polar-stereographic reprojection. This is the *lowest engineering complexity* of any conditional external source evaluated across Stage 8.2–8.5. **[INFERENCE, consistent with the Stage 8.2 practical-extraction table]**

### 9. Expected error attack
Primarily **aerosol attenuation** and **clear-sky transmittance**, secondarily improving the diffuse/direct partition on nominally clear origins. This is explicitly a mechanism none of the current 37 champion features represent.

### 10. Redundancy risk
- vs. Stage 6.6 LWP/IWP: none (LWP/IWP is condensed cloud water; AOD is aerosol, a physically disjoint atmospheric constituent).
- vs. Stage 7.5 terrain: none (terrain/horizon is static geometry; AOD is a dynamic atmospheric field).
- vs. Stage 8.1 U700/V700: none directly, though AOD forecasts do depend on the same wind field for transport — this is a shared *underlying* dynamical driver, not a redundant *feature*, and is not a concern for a gradient-boosted model.
- vs. MEPS cloud fraction / clear-sky GHI / historical SITES SW_IN context: low. Clear-sky GHI already captures the geometric ceiling; AOD would modulate that ceiling under low-cloud conditions, which is new information, not a restatement.
- **Overall redundancy risk: LOW.**

### 11. Experiment design (smallest scientifically clean test)
- **Architecture:** frozen Stage 8.1 `HistGradientBoostingRegressor`, unchanged hyperparameters.
- **Candidate feature set:** the existing 37 champion features **plus exactly 2 new causal time-varying features** (mirroring the minimal, successful two-variable addition pattern of Stage 8.1's U700/V700):
  1. `aod550_h` — total aerosol optical depth at 550 nm, per forecast valid hour H1…H24, from the D-1 12Z CAMS run.
  2. `tcwv_h` — total column water vapor, per forecast valid hour H1…H24, same run.
- 5-fold forward-chaining EVEN-only CV on the 174 EVEN origins, identical protocol to Stage 8.1/8.3/8.5.
- No hyperparameter search; no architecture change.

### 12. Ranking
**HIGH feasibility and expected value** — subject to the CONDITIONAL empirical file-level pull described in item 7 being completed first (a data-verification sub-step, not itself a forecasting experiment).

---

## 2. Candidate B — Cloud Radiative-Path Geometry (cloud base/top + LWP/IWP + solar geometry)

### 1. Physical mechanism
The optical path length of sunlight through a cloud layer depends on solar zenith angle and cloud geometric thickness; combining cloud base/top altitude (Stage 8.0-verified MEPS variable, not yet used in the champion) with existing LWP/IWP and solar geometry could sharpen the estimate of *cloud optical thickness along the actual solar ray*, rather than treating LWP/IWP as a vertically-integrated scalar.

### 2. Information novelty
**Partial.** Cloud base/top altitude itself is a genuinely unused MEPS variable (Stage 8.0 verified it is available in 100% of origins but it has never been placed into a candidate feature set). However, the *combination* — LWP/IWP × solar geometry × cloud depth — is a re-derivation from three already-available ingredients rather than a new external data source. This risks being read as a reformulation adjacent to the already-rejected "vertical cloud structure alone" and "kt reformulation" experiments. **[INFERENCE — the *raw variable* (cloud base/top) is novel; the *combination logic* is only moderately novel.]**

### 3. Causality
Cloud base/top altitude is sourced from the same D-1 18Z `meps_det_sfc` product already used causally by the champion. **[VERIFIED — Stage 8.0, 100% availability, fill-value masking required at $9.96921\times10^{36}$]** No new causality question is introduced.

### 4. Spatial representativeness
Identical to existing MEPS-derived features (2.5 km grid, already used causally). No degradation or improvement versus current champion inputs.

### 5. Temporal resolution
Fully compatible with H1–H24 (same product already used for U700/V700).

### 6. Polar conditions
Solar geometry (SZA) is deterministic and always available (no external dependency); cloud base/top altitude is a thermal/structural NWP diagnostic, not a solar-channel retrieval, so it remains defined through polar night — though the resulting geometry feature is only *physically meaningful* when the sun is above the horizon, which the existing night-zero rule already handles.

### 7. Data availability
Already verified 100/347 in Stage 8.0. **[VERIFIED]**

### 8. Operational feasibility
Low complexity — no new external product, purely an in-pipeline feature-engineering exercise.

### 9. Expected error attack
Cloud optical thickness / radiative geometry, overlapping partially with what LWP/IWP and terrain/horizon already encode.

### 10. Redundancy risk
**MEDIUM-HIGH.** This is largely a recombination of Stage 6.6, Stage 7.5, and an unused Stage 8.0 variable, rather than a new information channel. Given that Stage 8.5 already showed that *adding* structurally related cloud-geometry information (spatial cloud fields) to the same architecture produced only a ~0.19 W/m² MAE gain that failed gates, there is a real risk this candidate would show a similarly marginal, gate-failing improvement for the same underlying reason: the champion's 37 features may already saturate what linear/tree-based recombinations of cloud + geometry can extract.

### 11. Experiment design
If pursued: frozen champion + 3 features (`cloud_base_altitude`, `cloud_top_altitude`, `cloud_geometric_thickness = top - base`) interacted implicitly by the tree model with existing solar-zenith-angle inputs already present in the base feature set. Same 5-fold EVEN CV protocol.

### 12. Ranking
**MEDIUM feasibility, LOW-to-MEDIUM expected value.** Cheap to test, but the redundancy risk and the Stage 8.5 precedent make this a plausible second-tier or "cheap fill-in" experiment rather than the primary next route.

---

## 3. Candidate C — Causal Observed-Cloud Temporal Evolution from Recent SITES Observations

### 1. Physical mechanism
Persistence and short-term trend in the observed clear-sky index (derived from the previous 24 h of actual SW_IN observations, which are already the model's raw input window) could carry information about ongoing synoptic cloud regime (e.g., a stratocumulus deck currently overhead is likely to persist a few hours) beyond what the raw 24 h SW_IN sequence already implicitly encodes to the model.

### 2. Information novelty
**LOW.** The previous-24-hour SW_IN observation window is *already* the benchmark's mandated input; a tree/boosting model conditioned on that full sequence has access to any persistence or trend signal already, unless the current champion's feature engineering fails to expose it explicitly (e.g., only summary statistics of the window are fed rather than the full trajectory). Absent a specific engineering gap identified in the champion's current 37-feature list (not documented in the provided reports), this candidate is very likely to duplicate information the model can already extract. It is also adjacent to the previously-rejected "kt reformulation" and the Stage 8.3 Abisko transmissivity-history experiment (rejected on Nuolja's own analog).

### 3. Causality
Trivially causal — it is Nuolja's own historical data, already inside the causal window by construction.

### 4. Spatial representativeness
Perfect (it is the target site itself), but this is exactly why it is unlikely to be *new* information.

### 5–9. (Resolution / polar conditions / availability / feasibility / error attack)
All trivially satisfied since this uses data already inside the pipeline; the open question is purely whether current feature engineering under-exposes persistence/trend structure to the model — an audit question, not a data-feasibility question.

### 10. Redundancy risk
**HIGH.** This is the most redundant of the candidates evaluated: it re-derives information from data the model already sees, and closely parallels both the rejected kt reformulation and the rejected Stage 8.3 Abisko transmissivity-history route (which tested essentially this hypothesis one station over, and failed on all 5 gates).

### 11. Experiment design
If pursued at all, this should first be an **audit of the existing 37-feature encoding** of the raw 24 h window (do explicit trend/tendency/persistence summary features already exist? if not, add 2–3 minimal ones) rather than a new "data source" experiment. This is not analogous in kind to the other candidates in this report — it is a feature-engineering completeness check on existing data, not a genuinely new causal information source.

### 12. Ranking
**LOW feasibility as a "next route."** Worth a cheap internal audit, but does not meet the bar of "genuinely new information" set by the research question, and has a directly analogous prior rejection (Stage 8.3).

---

## 4. Other Candidates Considered and Why They Are Not Recommended

- **Standard VIIRS L2 cloud products (any framing):** Per explicit governance instruction, and per the Stage 8.2/8.4 empirical finding, standard science L2 products have a **3–13 hour publication latency**, making $t_{\text{pub}} \le t_0$ fail for essentially all standard-archive origins. **[VERIFIED — Stage 8.4]** This is unchanged by re-labeling or re-scoping the request; it is not recommended as the next route.
- **NWC SAF/PPS:** Real-time latency is fast (~30–60 min) **[per Stage 8.2 audit]**, but retrospective bulk 2024 archive access for the exact Nuolja/Lapland domain is restricted/incomplete on open endpoints — the *feasibility* of reconstructing a clean historical training set is the blocker, not causality. **CONDITIONAL, not recommended next.**
- **CAMS European Air Quality Forecasts (0.1°, ~10 km, EU domain incl. up to 72°N):** Higher spatial resolution than the global CAMS product and does cover Nuolja's latitude. **[VERIFIED — ADS documentation, domain north boundary 72°N]** However, this regional product is built around surface pollutant concentrations (PM2.5, PM10, NO2, O3, CO) for air-quality purposes; column aerosol optical depth — the variable with a direct, well-established radiative-transfer link to solar attenuation — is a first-class output of the *global* composition product, not confirmed as a direct output of the regional one. Using regional PM fields would require an additional, unverified optical-properties conversion step. **CONDITIONAL/UNVERIFIED, higher implementation complexity, not clearly superior to Candidate A; not recommended as the primary route, but worth a later resolution-upgrade experiment if Candidate A succeeds.**
- **AERONET ground sun-photometers:** No confirmed AERONET (or equivalent calibrated sun-photometer) station at Abisko/Nuolja/Kiruna is established in this project's file-level record. Nearest confirmed stations in Fennoscandia are hundreds of km away or unverified for 2024 continuity — **CONDITIONAL/UNVERIFIED, not pursued further** without a specific station identified and file-level checked.
- **ERA5 / ERA5-Land reanalysis:** Reanalysis products are non-causal by construction (they assimilate the full future observation record for the analysis date) and are explicitly excluded by the "no future observations" benchmark rule. **Not eligible.**
- **CAMS Solar Radiation Service (CRS) / McClear all-sky product directly:** The satellite-imagery-based CAMS Radiation Service (Heliosat-4) is documented as covering only **-66° to +66° latitude** (Meteosat disk view) — Nuolja at 68.36°N is **outside this coverage**. **[VERIFIED — soda-pro.com CAMS services documentation]** The clear-sky-only McClear component is computed independently of satellite imagery and *is* defined globally, but the standard delivered McClear/CRS *archive* product itself carries a ~2-day delivery delay, and in any case duplicates exactly the atmospheric composition inputs already captured more directly and more causally via Candidate A. **Not recommended as a separate route** — Candidate A already captures the underlying physical information without the satellite-coverage and delay complications of the packaged CRS/McClear product.

---

## 5. Ranking Summary

| Candidate | Novelty | Causality | Redundancy Risk | Feasibility | Overall |
|---|---|---|---|---|---|
| **A. CAMS Aerosol (AOD/TCWV, global composition forecasts)** | High | Verified, generous margin | Low | High (medium engineering effort) | **HIGH** |
| **B. Cloud radiative-path geometry (base/top + LWP/IWP + geometry)** | Partial | Verified (existing product) | Medium-High | High (cheap to test) | **MEDIUM** |
| **C. Observed cloud/clear-sky persistence from SITES history** | Low | Trivial | High | High (cheap) | **LOW** |
| VIIRS (any standard framing) | High | Fails ($t_{pub}>t_0$) | Low | Blocked | Not recommended |
| NWC SAF/PPS | High | Conditional (archive gap) | Low | Blocked (historical archive) | Not recommended |
| CAMS European regional AQ | Medium | Verified | Low-Medium | Conditional (variable gap) | Secondary/later |

---

## 6. Answer to the Main Research Question

**The single strongest genuinely causal information source not yet tested, with a credible physical pathway to improve Nuolja SW_IN H1–H24 forecasting, is CAMS aerosol optical depth and total column water vapor from the CAMS Global Atmospheric Composition Forecasts (Candidate A).**

**Top 3, ranked, and why #1 beats #2 and #3:**

1. **CAMS Aerosol/AOD (HIGH)** — the only candidate representing a physically disjoint atmospheric constituent (aerosol) never touched by Stage 6.6, 7.5, 8.1, or 8.5, with a verified and unusually generous causal margin (12h+ lead vs. the champion's own 6h margin), low redundancy, and the lowest engineering complexity of any conditional external source assessed across this entire project.
2. **Cloud radiative-path geometry (MEDIUM)** — beaten by #1 because its novelty is only partial (recombination of three already-tested/available ingredients) and it carries a direct precedent for marginal, gate-failing results (Stage 8.5's structurally similar cloud-geometry expansion).
3. **Observed cloud/clear-sky persistence (LOW)** — beaten by both because its information content is very likely already implicitly available to the model from the mandated 24 h input window, and it has a close direct precedent for rejection (Stage 8.3's Abisko transmissivity-history test).

---

## 7. Final Decision Block

**1. SINGLE BEST NEXT ROUTE**
CAMS Global Atmospheric Composition Forecasts — causal aerosol optical depth and total column water vapor, added to the frozen Stage 8.1 champion.

**2. WHY IT IS NEW**
No POLARIS stage to date has ingested any atmospheric-composition (aerosol/water-vapor/ozone) variable. Every prior tested/rejected route (Stages 6.6, 7.5, 8.1, 8.3, 8.5) is cloud-, wind-, terrain-, or ground-radiation-based. This candidate targets a physically disjoint attenuation mechanism (aerosol scattering/absorption) that operates even under clear or thin-cloud skies where all current champion features carry little signal.

**3. EXACT DATA PRODUCT**
ECMWF Atmosphere Data Store dataset `cams-global-atmospheric-composition-forecasts`.

**4. EXACT VARIABLES (minimal set)**
`total_aerosol_optical_depth_550nm`, `total_column_water_vapour` (optionally, if the total-AOD signal proves too smoothed in later diagnosis: `dust_aerosol_optical_depth_550nm` and `biomass_burning_aerosol_optical_depth_550nm` as species-resolved alternatives).

**5. CAUSALITY RULE**
For forecast origin $t_0 = $ 00:00 UTC day D, use only the **D-1 12Z CAMS run**, guaranteed available by 22:00 UTC on D-1 (≥2 h before $t_0$, ≥12 h lead time at $t_0$ itself). Never use the same-day 00Z CAMS run (guaranteed only by 10:00 UTC day D, which is after $t_0$) or any run issued after 12Z D-1.

**6. MINIMAL FEATURE SET**
Exactly 2 new causal per-forecast-hour features — `aod550_h` and `tcwv_h` for H1…H24 — mirroring the proven minimal-addition pattern of the Stage 8.1 U700/V700 experiment. No architecture or hyperparameter changes.

**7. EVEN-ONLY EXPERIMENT DESIGN**
Frozen Stage 8.1 `HistGradientBoostingRegressor`, 37 existing features + 2 new features (39 total). 5-fold forward-chaining cross-validation on the 174 EVEN origins only, identical protocol to Stages 8.1/8.3/8.5. Before any CV run: a mandatory file-level empirical pull of the D-1 12Z CAMS archive for all 347 origins, to convert the current CONDITIONAL data-availability status to VERIFIED — exactly as Stage 8.4 did for VIIRS before any forecasting claim was made.

**8. PREDECLARED ACCEPTANCE GATES**
- Gate 1 (Primary MAE): ΔMAE ≤ −0.50 W/m² vs. Stage 8.1 EVEN control.
- Gate 2 (Fold consistency): ≥4/5 EVEN folds improved.
- Gate 3 (Worst-fold degradation): ≤ +0.50 W/m² on any single fold.
- Gate 4 (Consistency): Candidate nMAE ≤ Control nMAE **and** Candidate RMSE ≤ Control RMSE (both, not either — this is the exact criterion Stage 8.5 failed on nMAE despite passing on MAE).
- Gate 5 (Causality): 100% of the 347 origins verified causal under the Section 5 rule above (no exceptions permitted).
- Gate 6 (Control reproduction): Exact reproduction of the Stage 8.1 EVEN control MAE before the candidate is evaluated.

**9. WHAT RESULT WOULD CAUSE US TO REJECT IT**
Any single gate failure — in particular, a repeat of the Stage 8.5 pattern (small aggregate MAE gain with nMAE degradation, or improvement in fewer than 4/5 folds) would be treated as REJECTED, exactly as Stage 8.5 was, regardless of directional promise.

**10. WHAT RESULT WOULD JUSTIFY FREEZING IT AND REQUESTING ODD AUTHORIZATION**
All six gates passing simultaneously, with the improvement concentrated plausibly (though not necessarily exclusively) on higher-AOD or lower-cloud-fraction EVEN origins — i.e., a result pattern consistent with the aerosol-attenuation mechanism actually being exercised, not an artifact of a single fold or a generic regularization effect. Only then should Stage 8.7 request ODD evaluation, under the same frozen-architecture, no-further-tuning discipline used for the Stage 8.1 champion promotion.

---

*No implementation code was written. No POLARIS files were modified. No experiment was started. ODD access: NO. This report is a research/feasibility deliverable only.*
