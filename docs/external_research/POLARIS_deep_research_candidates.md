# POLARIS — Deep Research: Unexplored Information Sources for 24h SW_IN Forecasting at Nuolja (68.36°N)

## 0. Framing finding that changes how you should read everything below

Before the individual routes: there is a **structural, latitude-driven reason** several of your already-rejected routes (esp. #11 thermal-IR satellite point/ROI, and the fragility of #12 MEPS revision trajectories) underperformed, and it should discipline which new routes are worth a day of your remaining 48 hours.

**MSG/SEVIRI viewing geometry degrades sharply above ~60–65°N.** At Nuolja's latitude (68.36°N, ~18.7°E, i.e. close to the 0°/9.5°E MSG sub-satellite longitudes), the satellite elevation angle is very low (in the ~10–20° range), close to the limb. Documented consequences directly relevant to you:
- Weighting functions and narrow/broadband-to-flux conversions become unreliable near the viewing-zenith limit.
- A dedicated Arctic-circle solar forecasting study states plainly: *"geostationary satellites lack coverage into the Arctic circle… Low solar elevation and the prevalence of snow may lead to further issues, such as satellite misinterpretation of snow as clouds, or not accurately quantifying ground albedo"* (Erdmann et al. 2024, arXiv:2410.07806).
- An independent high-latitude benchmark (34 stations, 58–76°N, Norway) explicitly separates "horizon-shaded" and "snow-affected" and ">65°N" station categories because satellite-derived products (CAMS, PVGIS-SARAH2, Solargis — all Heliosat/SEVIRI-based) degrade measurably in exactly these categories (Bright et al., *Solar Energy* 2024, S0038092X24006704).
- A 2016 paper states outright: *"Indirect measured radiation data received from geostationary satellites is unreliable at latitudes above 60 degrees due to the resulting flat viewing angle"* (Renewable Energy and Environmental Sustainability, DOAJ 14394cf7221641088ef43765e32428df).

**Implication:** any further single-satellite (MSG) geometric/radiometric feature — including cloud-motion vectors derived from MSG imagery — inherits this ceiling. This is very likely *why* your thermal-IR point/ROI features (#11) gave little signal, and it caps the expected value of "do more with MSG" ideas. This doesn't make satellite data useless, but it reweights priority toward (a) genuinely different physical information not exposed to this geometric limitation, and (b) satellite sources with better high-latitude geometry (polar orbiters).

---

## 1. Static terrain horizon-shading / sky-view-factor features (DEM-based)

**Physical information added:** For each hour, the true local horizon elevation angle in the sun's azimuth direction (from a real digital elevation model around the station), used to (a) hard-block direct beam when solar elevation < local horizon elevation, and (b) reduce the diffuse component via a sky-view factor (fraction of the hemisphere not obstructed by terrain). This is a purely geometric correction, independent of clouds.

**Why it could reduce error:** Nuolja is a mountain-flank station (station at treeline on Mt. Njulla/Nuolja, peak 1169 m, surrounded by mountains, on the shore of Torneträsk in a glacial valley — confirmed via SITES/Polarforskningssekretariatet documentation). Generic clear-sky models (and MEPS's own radiation scheme, run on a ~2.5 km grid that cannot resolve the local ridge line) assume a flat, open horizon. At 68°N the sun is low for a large fraction of daytime hours even in summer, and civil-twilight-adjacent hours dominate spring/autumn — exactly the situations where a blocked or partially blocked horizon changes measured SW_IN by tens of W/m² relative to a geometric clear-sky/MEPS estimate that assumes open sky. This is a systematic, time-of-day/season-dependent bias source that is completely different in kind from anything on your rejected list (none of your rejected approaches touch static geometry).

**Tested in literature:** Yes, well established. Solcast's operational irradiance model explicitly adds a horizon-profile/sky-view-factor correction (Dozier & Frew 1990 algorithm, 90 m DEM, 30 km radius) as a documented production feature. Academic literature on DEM-based terrain shading for clear-sky and all-sky radiation is extensive (e.g., glacier/mountain radiation-balance modeling, Frontiers 2019; "Explicit validation of a surface shortwave radiation balance model over snow-covered complex terrain").

**Reported quantitative improvements:** Not reported as a single universal number (effect is site- and hour-specific, ranging from negligible at midday-high-sun to a full zeroing of direct beam at low sun angles); Solcast reports it materially changes DNI/DHI in complex terrain but doesn't publish a global %.

**Required data source:** A digital elevation model — Copernicus GLO-30 (30 m, global, free via Copernicus Dataspace) or SRTM 30 m; for higher fidelity, Lantmäteriet's Swedish national DEM (2 m grid) is open data and would resolve the actual local ridgelines around Nuolja far better than SRTM.

**Exists for Nuolja 2024:** Yes — DEM is static, not time-dependent; any 2024 use is trivially covered.

**Temporal resolution:** N/A (time-invariant); combined with solar position it becomes hour-of-day/day-of-year-dependent deterministically.

**Spatial resolution:** 30 m (Copernicus/SRTM) or 2 m (Lantmäteriet) around the exact station coordinate.

**Causal availability at t0:** Perfect — it's static terrain, known before the data even exists. Zero leakage risk of any kind.

**Implementation difficulty (≤1 day):** Low. Download DEM tile, compute horizon-angle-vs-azimuth profile once (Dozier–Frew style ray casting, well-documented algorithm, a few hundred lines), derive per-hour "sun-blocked" flag and sky-view-factor scalar for all of 2024, feed as two additional static-context features (or use to gate/rescale the existing clear-sky-irradiance feature that Stage 5.2 already consumes). This is almost pure geometry — no model retraining risk, no distributional shift risk.

**Expected upside:** Moderate, concentrated in low-sun hours (which are common in the daytime window at this latitude) and in spring/autumn when the sun elevation crosses the local horizon threshold repeatedly. Because your metric is *daytime* nMAE and daytime at 68°N includes many low-elevation hours, this could plausibly nudge several tenths of a % nMAE — a similar order of magnitude to the 0.27 W/m² MAE gain you saw (and rejected for instability) in Stage 6.4, but with the advantage of being a deterministic feature rather than a learned correction, so it shouldn't introduce fold-to-fold instability.

**Main failure modes:** (a) If Stage 4/5 already implicitly learns this pattern from temporal + solar-geometry features and historical SW_IN autocorrelation, the marginal gain could be small; (b) if the true instrument horizon differs from what a coarse DEM implies (e.g., vegetation/tree-line canopy near the sensor not captured by bare-earth DEM), the correction could be biased — worth a quick sanity check against the diurnal SW_IN curve on clear days.

**Leakage risk:** None — this is entirely pre-computable, static, physically causal information.

---

## 2. Day-ahead CAMS aerosol optical depth (AOD) forecast for clear-sky correction

**Physical information added:** Forecasted atmospheric aerosol loading (total AOD, and speciated: black carbon/organic matter from wildfire smoke, sulfate, sea salt, dust) from the Copernicus Atmosphere Monitoring Service (CAMS) global or regional composition forecast, used to correct the clear-sky irradiance baseline (via e.g. a McClear-style clear-sky model driven by forecast AOD instead of a fixed climatology).

**Why it could reduce error:** Your Stage 5.2 pipeline already uses "clear-sky irradiance" as an input, presumably from a geometric/climatological clear-sky model. Under episodic events — Canadian/Siberian wildfire smoke transport into Scandinavia (well documented in summer 2023 and recurrent in recent years) or Arctic haze (a known late-winter/spring phenomenon at these latitudes) — actual clear-sky-day AOD can deviate sharply from climatology, producing systematic under/over-forecasts on clear days that a generic climatological clear-sky model cannot capture, and that MEPS (a weather model, not typically running prognostic smoke aerosol) may also miss. This is a genuinely different information channel: atmospheric composition forecast, not weather-model cloud/radiation output.

**Tested in literature:** Yes, directly. "Assessment of aerosol optical depth forecast for day-ahead clear-sky direct irradiance" (AMT, 2025) evaluates exactly this use case — CAMS day-ahead AOD forecasts vs. AERONET-persistence for next-day clear-sky DNI, finding CAMS forecasts outperform persistence at most sites. Multiple other papers quantify AOD-driven clear-sky-irradiance sensitivity and CAMS AOD skill (Gueymard & Yang 2020 AOD validation vs. AERONET; EGUsphere 2026 aerosol-uncertainty-propagation study).

**Reported quantitative improvements:** CAMS AOD forecasts shown to beat naive persistence for day-ahead clear-sky DNI at most AERONET sites (AMT 2025); typical clear-sky-irradiance sensitivity to AOD uncertainty is on the order of several percent of clear-sky GHI/DNI under elevated-aerosol conditions (EGUsphere 2026: ~47% relative AOD uncertainty translating into a non-trivial GHI/DNI sensitivity via radiative kernels). Gains are event-concentrated (they matter a lot on smoke/haze days, ~0 otherwise), so aggregate annual nMAE impact will be smaller than the event-day impact, but for a metric like yours dominated by tail errors this can still move the aggregate.

**Required data source:** CAMS global atmospheric composition forecast (Copernicus Atmosphere Data Store, `cams-global-atmospheric-composition-forecasts`), archived operational forecasts going back to ~2015 at ~40 km resolution, updated daily (00 UTC cycle), forecast length out to 5 days — comfortably covers a 24h-ahead horizon causally.

**Exists for Nuolja 2024:** Yes — CAMS forecast archive covers all of 2024 globally, including this location; no gap expected at this latitude (this is a global chemistry-transport model, not satellite-retrieval-based, so it does not suffer the MSG viewing-angle problem).

**Temporal resolution:** 3-hourly (typical CAMS forecast output step).

**Spatial resolution:** ~40 km (0.4°) grid — coarser than MEPS but adequate for a slowly-varying aerosol-loading feature.

**Causal availability at t0:** Yes — use the forecast *issued* at or before t0 (i.e., the most recent CAMS cycle available before your forecast origin), exactly analogous to how you already use MEPS forecasts. No leakage if you discipline the forecast-issue-time bookkeeping the same way you presumably already do for MEPS.

**Implementation difficulty (≤1 day):** Medium. Requires registering for/using the CDS/ADS API, pulling a single grid-point time series for 2024 (a modest one-time download), and either (a) directly using AOD-derived variables as corrector features, or (b) running a lightweight McClear-style clear-sky adjustment. Option (a) is very achievable in a day; option (b) is more physics-heavy and probably not worth attempting in the remaining time — use (a).

**Expected upside:** Small-to-moderate in aggregate nMAE (effect is concentrated on a minority of clear-sky days with anomalous aerosol loading), but this is exactly the kind of tail-risk source your residual corrector hasn't seen at all, and it's causally clean and cheap to add as 2–3 extra columns.

**Main failure modes:** Nuolja/Abisko is a remote, generally low-aerosol background site most of the year, so the *median* impact of adding AOD features could be ~zero — the gain, if any, will show up as reduced error variance on the (rare) smoke/haze days rather than a uniform MAE shift, so evaluate with a stratified breakdown (smoke-episode days vs. rest) rather than only the aggregate metric, or you may conclude "no effect" prematurely.

**Leakage risk:** Low, provided you strictly use only the CAMS forecast cycle available at/before t0 (same discipline as MEPS).

---

## 3. Phase-partitioned cloud condensate (liquid water path vs. ice water path) from MEPS, instead of only cloud fraction/cover

**Physical information added:** Vertically-integrated cloud liquid water content and cloud ice water content *separately* (not just "cloud cover fraction" or a single combined cloud variable), taken directly from MEPS's own prognostic microphysics fields if not already extracted.

**Why it could reduce error:** Arctic low/mid-level clouds are predominantly mixed-phase (liquid + ice coexisting), and their shortwave transmittance is controlled far more by liquid water content/effective droplet size than by cloud fraction alone — for equivalent cloud fraction, a liquid-dominated cloud attenuates SW very differently from an ice-dominated one (Arctic cloud-radiation literature: Kim et al. 2024 JGR-Atmospheres; Advances in Understanding Cloud Fraction and Its Impact on Surface SW in the Arctic, 2024, which explicitly flags cloud-fraction-based SW estimation as the dominant error source at high latitude because it collapses this phase information). **This is a real gap only if your current "MEPS radiation/cloud/weather variables" feature set uses cloud cover/fraction and/or a single combined condensate variable rather than phase-partitioned water content — verify this first**, since if you already ingest MEPS's separate liquid/ice specific-humidity fields at model levels, this route is already covered and should be dropped.

**Tested in literature:** Yes, extensively for *understanding* Arctic SW radiation biases (Kim et al. 2024; Advances in Understanding Cloud Fraction and Its Impact on Surface Shortwave Radiation in the Arctic, Journal of Remote Sensing 2024–2025), but rarely as an explicit ML feature-engineering step in a solar-forecasting residual corrector — this is a case of importing a known atmospheric-physics finding into your feature set rather than following an existing ML paper's recipe.

**Reported quantitative improvements:** No single published %-nMAE number for this exact use (it's drawn from cloud-physics literature, not solar-forecasting benchmarking), so treat expected gain as **hypothesis-driven, not literature-quantified** — flag this honestly.

**Required data source:** MEPS's own native model-level output (cloud liquid water content, cloud ice water content — these are standard AROME/MEPS microphysics prognostic variables, typically available in the full model-level GRIB files even if not in the surface/derived product you're currently consuming).

**Exists for Nuolja 2024:** Yes, if your MEPS archive retains model-level fields (need to check what subset of MEPS fields you archived — if you only kept surface/2D radiation and cloud-cover diagnostics, you'd need to re-extract from raw MEPS archives, e.g., MET Norway's Thredds/S3 archive).

**Temporal resolution:** Same as your existing MEPS ingestion (hourly forecast steps).

**Spatial resolution:** MEPS native (~2.5 km), same as your existing spatial features.

**Causal availability at t0:** Yes — same forecast-cycle discipline as your existing MEPS features, no new leakage vector.

**Implementation difficulty (≤1 day):** Low-medium *if* the raw MEPS archive with model-level condensate fields is accessible to you; potentially not doable in a day if it requires a fresh bulk re-download/re-processing pipeline you don't already have. This is the main practical risk for this route — check data availability before committing time.

**Expected upside:** Plausible moderate gain specifically in cloud-transmittance accuracy under mixed-phase conditions (common at this site much of the year), but genuinely uncertain magnitude — this is the most "basic-science-plausible, not yet forecasting-literature-quantified" of the routes here.

**Main failure modes:** MEPS's own microphysics scheme may already have first-order errors in partitioning liquid vs. ice that swamp the informational benefit; also risk that your HistGradientBoosting corrector already implicitly infers phase information from the correlated weather variables you already feed it (temperature, humidity, existing cloud variables), making the explicit phase split redundant.

**Leakage risk:** None beyond what you already manage for MEPS-derived features.

---

## 4. Structural (heterogeneous) multi-model NWP disagreement: MEPS vs. an independently-built global model (ECMWF)

**Physical information added:** The *disagreement* between two structurally different NWP systems — MEPS (regional, convection-permitting, AROME-based physics) and ECMWF's global IFS (HRES deterministic and/or ENS) — at the same forecast valid time. This differs fundamentally from your rejected "MEPS ensemble spread" (#10), which captures *within-model* perturbed-initial-condition uncertainty from a single model's own physics package. Cross-model disagreement instead captures *structural/parameterization* uncertainty (different convection schemes, different cloud microphysics, different radiation schemes, different data assimilation) — a distinct error source not exposed by perturbing one model's ICs.

**Why it could reduce error:** When two independently engineered models agree closely on cloud/radiation state at t0+lead, the joint forecast is more trustworthy; when they diverge sharply, this is itself informative about local forecast uncertainty and — used as a feature rather than just an uncertainty flag — the corrector may learn systematic MEPS bias directions conditional on the sign/magnitude of MEPS-vs-ECMWF divergence (i.e., ECMWF acts as an independent second opinion on cloud state, catching cases where MEPS's specific parameterizations are known to misbehave, e.g., over complex terrain or under specific synoptic regimes).

**Tested in literature:** The general principle (heterogeneous/"poor man's" multi-model ensembles outperforming single-model ensembles for weather uncertainty) is well established in NWP verification literature broadly; direct application specifically to solar-irradiance residual correction is less common in the papers surfaced here — this is a reasonably well-grounded meteorological principle applied somewhat novelly to your specific correction task, rather than a directly reproduced published solar-forecasting result. Be transparent with yourself that the evidence base here is "sound meteorological reasoning + established multi-model-ensemble literature in NWP generally," not "a paper that did exactly this for SW_IN and reported X% improvement."

**Reported quantitative improvements:** Not found as a directly comparable solar-forecasting number in this search; treat as unquantified-but-plausible.

**Required data source:** ECMWF Open Data (free, real-time-ish global HRES + ENS output at 0.25°, available from 2023 onward under ECMWF's open-data policy) — covers 2024. Alternatively, ERA5-based short "forecast" reanalysis fields could substitute at reduced fidelity but with reanalysis-leakage risk (ERA5 uses observations after t0 in some fields — must use ERA5T/forecast-only fields or ECMWF's actual archived forecasts, not the reanalysis, to stay causal).

**Exists for Nuolja 2024:** Yes, ECMWF Open Data / TIGGE archives cover 2024 globally.

**Temporal resolution:** 3–6 hourly (typical ECMWF Open Data step for the relevant fields).

**Spatial resolution:** 0.25° (~25–28 km) — coarser than MEPS, adequate for a disagreement/divergence signal.

**Causal availability at t0:** Yes, provided you use the ECMWF forecast cycle issued at/before t0 (same discipline as MEPS forecasts) — do not use ERA5 reanalysis fields for the future portion of your window, only genuine forecast archives.

**Implementation difficulty (≤1 day):** Medium — new data source integration (download, regrid to station point, align forecast-issue times with your existing MEPS bookkeeping) is the main time cost; the feature engineering itself (differences/ratios of cloud cover, radiation, or derived clear-sky-index between the two models per horizon) is simple once data is in hand. This is tight for one day but plausible if ECMWF Open Data access is straightforward in your environment.

**Expected upside:** Moderate — this is the route most likely to surface a genuinely new, decorrelated error signal (since it's not a variant of anything on your rejected list), but with real execution risk given the day budget.

**Main failure modes:** (a) Data engineering overrun eating your full day before any model training happens; (b) ECMWF's global model, lacking MEPS's convection-permitting resolution, may simply be *worse* at resolving Nuolja's local terrain/cloud regime, making the "disagreement" signal mostly reflect ECMWF's coarseness rather than useful uncertainty information; (c) stability risk analogous to your Stage 6.4 rejection — cross-model divergence features could show a fold-inconsistent aggregate improvement, so evaluate per-fold, not just aggregate, before accepting.

**Leakage risk:** Low if forecast-issue-time discipline is enforced (same pattern as your existing MEPS usage); moderate leakage risk if you accidentally substitute reanalysis-informed fields for genuine forecasts.

---

## 5. Snow-cover / high-albedo cloud-enhancement diffuse-irradiance correction

**Physical information added:** An explicit feature (or interaction term) capturing the known radiative effect whereby a highly reflective snow-covered surface under broken/thin cloud increases diffuse (and sometimes total) irradiance above what a snow-agnostic cloud-transmittance model predicts, via multiple reflection between the snowpack and cloud base (documented effect: Gueymard & Ruiz-Arias 2016; "Cloud and albedo enhancement impacts on solar irradiance," *Solar Energy* 2017).

**Why it could reduce error:** Nuolja/Abisko carries seasonal snow cover for much of the year (subarctic mountain environment), and this specific multi-scattering enhancement is a documented, non-negligible, and commonly mis-modeled effect in high-albedo regions — distinct from anything in your rejected list (your "cloud-damped clear-sky ensemble" and "cloud-regime isotonic correction" approaches operated on cloud regimes, not on an explicit albedo-conditioned interaction).

**Tested in literature:** Yes, for the underlying physical effect (Gueymard & Ruiz-Arias 2016; Solar Energy 2017 paper explicitly quantifying cloud+albedo enhancement impacts on GHI); less so as a direct ML forecasting-correction feature.

**Reported quantitative improvements:** Effect magnitude reported as "non-negligible, and even large under cloudy conditions" for backscattered irradiance over snowy areas (Solar Energy 2017), but not as a standardized %-nMAE improvement number applicable to your exact task.

**Required data source:** Snow-cover extent/depth, obtainable from MEPS's own land-surface/snow analysis (likely already present in "MEPS spatial statistics"/"weather variables" if you ingest snow depth or surface albedo), or independently from a satellite snow product (e.g., NASA/NSIDC IMS daily snow/ice product, or Copernicus H SAF snow products) as a cross-check.

**Exists for Nuolja 2024:** Yes, via either MEPS's own snow analysis or the satellite snow products noted.

**Temporal resolution:** Daily (satellite snow products) to hourly (MEPS surface analysis).

**Spatial resolution:** ~1–4 km (MEPS) to ~4 km (IMS/H SAF).

**Causal availability at t0:** Yes if drawn from MEPS's own analysis/forecast (already causal in your pipeline) or from an already-observed satellite snow state at t0 (snow cover doesn't change materially hour-to-hour, so even a slightly-lagged satellite product is safely causal).

**Implementation difficulty (≤1 day):** Low if MEPS surface albedo/snow-depth is already in your feature set (verify — you may already implicitly have this and simply not be forming the explicit *cloud × albedo interaction* term); the novel and cheap step is adding a multiplicative/interaction feature (e.g., surface-albedo × cloud-optical-depth-proxy) rather than a wholly new data ingestion pipeline.

**Expected upside:** Small-to-moderate, likely to matter most in a specific and fairly common local regime (broken/thin cloud + fresh snow), which could plausibly recur often enough at Nuolja to matter for the aggregate metric — but the effect is likely partially already captured indirectly by MEPS's own radiation scheme (which does condition on its own surface albedo internally), so the marginal information gain from an *explicit* interaction feature on top of what MEPS already outputs is the open, testable question, not a certainty.

**Main failure modes:** Redundancy with information MEPS's radiation scheme already encodes (in which case this is a near-duplicate of features you already have, just recombined); MEPS's own snow/albedo analysis may itself have known Arctic biases (independently documented — MODIS/Arctic albedo literature notes recurring snow-albedo characterization difficulties at high latitude), which could propagate rather than correct error.

**Leakage risk:** None beyond standard MEPS-feature discipline.

---

## 6. Polar-orbiter (VIIRS/Suomi-NPP, NOAA-20/21) multispectral cloud-phase/optical-depth snapshot at t0 — as a *replacement/complement* for the rejected MSG thermal-IR point/ROI features

**Physical information added:** At-t0 cloud optical depth, cloud phase (liquid/ice), and cloud-top properties from VIIRS, which — unlike MSG — is a genuinely different viewing geometry at this latitude (near-polar orbit gives Nuolja multiple overpasses per day rather than one continuously oblique geostationary view) and richer multispectral information (22 bands vs. your tested single/few-channel thermal-IR feature) than what you already tested and rejected.

**Why it could reduce error:** Since your rejected route #11 was specifically "thermal-IR satellite point/3×3 ROI" (implicitly MSG-derived, and thus subject to the geometric degradation discussed in Section 0), a polar-orbiter alternative is a **different representation addressing that specific known limitation** — better viewing geometry near the pole, explicit cloud-phase discrimination (directly relevant to Section 3's physics), rather than more of the same oblique-geostationary information.

**Tested in literature:** VIIRS/MODIS cloud products are extensively validated generally, but their use as ML input features specifically for high-latitude solar-forecasting correction (as opposed to satellite-retrieval-based irradiance products themselves) is less commonly published; treat as a reasonable extrapolation, not a directly reproduced result.

**Reported quantitative improvements:** Not found as a directly comparable number for this exact application.

**Required data source:** NASA VIIRS Cloud Products (VNP04/CLDPROP) or MODIS MOD06/MYD06 equivalents, via NASA Earthdata/LAADS DAAC.

**Exists for Nuolja 2024:** Yes.

**Temporal resolution:** 2–4 overpasses/day at this latitude (better than MSG's single continuous-but-degraded view, worse than MEPS's hourly cadence) — this is instantaneous snapshot information at irregular times, not a continuous time series.

**Spatial resolution:** 375 m–750 m native.

**Causal availability at t0:** Only the most recent overpass *before* t0 is usable — this is strictly a t0-state feature (like your rejected thermal-IR feature), not information about the forecast horizon itself, so its value is bounded to improving the model's characterization of the *starting* cloud state, not the future.

**Implementation difficulty (≤1 day):** Medium — new data source, new access pattern (NASA Earthdata authentication, granule search/download for specific overpass times), some processing to extract point/small-ROI values; tight for a single day if you're not already set up with Earthdata tooling.

**Expected upside:** Low-to-moderate, and importantly: since this is conceptually adjacent to your already-rejected #11 (a t0-state satellite snapshot feature), there's a real chance it fails for the *same underlying reason* (t0 satellite state alone may simply not carry enough information to correct 24 discrete future hourly values, regardless of which satellite supplies it) — this route should be considered **lower priority than routes 1–4** unless you have strong reason to believe the phase/geometry improvement specifically (not satellite-snapshot-in-general) was the limiting factor in #11.

**Main failure modes:** Same generic limitation as your rejected route (single-time-snapshot information decorrelates fast from cloud state 6–24h later); sparse overpass timing may not align well with your forecast origin t0, forcing you to use stale (several-hours-old) satellite state.

**Leakage risk:** Must strictly enforce "most recent overpass before t0 only" — same discipline as any t0-state feature.

---

## 7. Lower-priority / explicitly discouraged extensions of the rejected list

- **MSG cloud-motion vectors / optical flow (point 1/2 of your priority list):** Directly exposed to the Section 0 geometric ceiling; literature on CMV shows strong performance mainly for 0–2h nowcasting and clear degradation by hour 4–5 even in good-geometry regions — at 24h lead and Nuolja's poor viewing angle, expected value is low relative to effort. Not recommended as a priority given your remaining time.
- **CERES/EBAF or other coarse satellite radiation-budget products:** Monthly/daily resolution, far too coarse for hourly correction.
- **Ceilometer/Cloudnet cloud-radar data (e.g., FMI Sodankylä ACTRIS site):** Real physical richness (vertically-resolved cloud boundaries), but the nearest such site is ~300 km away — at that distance for a mountain-valley site with strong local terrain effects, representativeness is doubtful; not worth the day given the distance mismatch.
- **GNSS-derived integrated water vapor:** Physically real (water-vapor absorption modulates clear-sky irradiance a few %), but a small effect relative to cloud/terrain/aerosol signals already covered above; low priority for a 1-day budget.

---

## 8. Published high-latitude/polar solar-forecasting benchmarks: are any genuinely comparable to your 30.32% daytime nMAE?

**Short answer: no benchmark found uses an identical metric (daytime-only nMAE against a 24h-ahead reconstructed-SW_IN target at a comparable subarctic mountain site), so treat any cross-paper number as context, not a scoreboard.** Specifics:

- **Bright et al., "Benchmark of estimated solar irradiance data at high latitude locations," *Solar Energy* 2024** (34 Norwegian stations, 58–76°N) is the most *geographically* comparable reference — it explicitly stratifies by ">65°N," "snow-affected," and "horizon-shaded" station categories and reports relative MAE (rMAE) for CAMS/PVGIS-SARAH2/Solargis/Meteonorm/ERA5/NASA-POWER **as retrospective irradiance estimates**, not as a 24h-ahead *forecast* — this is a nowcasting/estimation accuracy benchmark, not a forecasting one, so it is not a directly comparable number to your 30.32% forecast nMAE, but it is strong independent confirmation that horizon-shading and snow are first-order, named error categories at this latitude range (directly supporting routes 1 and 5 above).
- **Erdmann et al., "Deep and Probabilistic Solar Irradiance Forecast at the Arctic Circle," arXiv:2410.07806 (2024)** is the most *task*-comparable reference (36h-ahead hourly forecast, LSTM-based, southern-Norway stations, clear-sky-injection architecture) but is **not metric-comparable**: it reports raw MAE (not normalized by daytime-mean, i.e., not nMAE), includes night-time zero values in its MAE computation (which mechanically deflates MAE relative to a daytime-only metric like yours), and its stations are southern Norway (lower latitude, less extreme seasonality) rather than a true Arctic mountain site. Their best MAE (~48–53 W/m², all-hours) should **not** be compared numerically to your 39.08 W/m² daytime MAE — the metrics measure different things.
- **SolarCrossFormer (arXiv:2509.15827, 2025)** reports day-ahead NMAE for Neuchâtel, Switzerland (~47°N) — useful as a methodological reference (satellite+ground fusion for day-ahead) but at a latitude and satellite-geometry regime with none of Nuolja's structural challenges, so again not a fair numeric comparison.
- **Conclusion:** there is currently no published benchmark that lets you say "our 30.32% is X% better/worse than the field" in an apples-to-apples way. If you want one for the writeup, the most defensible framing is qualitative: published high-latitude work consistently identifies *terrain shading* and *snow* as the dominant named failure modes above 65°N (Bright et al. 2024), which independently corroborates that Route 1 (and to a lesser extent Route 5) targets a documented, not speculative, high-latitude error source.

---

## 9. Top 5 ranked by (scientific plausibility × expected information gain × data feasibility × implementation speed within ~1 day)

| Rank | Route | Plausibility | Info gain (independent of rejected list) | Feasibility in 1 day | Net priority rationale |
|---|---|---|---|---|---|
| **1** | DEM-based terrain horizon-shading / sky-view factor (Route 1) | Very high — physically certain given station is on a mountain flank; independently corroborated by Bright et al. 2024 naming "horizon-shaded" as a distinct high-latitude error category | High — zero overlap with anything tested; purely geometric, not a variant of any rejected residual-correction technique | Very high — static DEM, no new live data feed, no leakage, deterministic computation | Best plausibility-to-effort ratio; safest against the kind of fold-instability that sank Stage 6.4, since it's not a learned/probabilistic correction |
| **2** | CAMS day-ahead AOD forecast for clear-sky bias (Route 2) | High — well-documented aerosol effect on clear-sky SW; directly validated in AMT 2025 for exactly this day-ahead use case | Moderate — genuinely new atmospheric-composition channel, not weather-model output | Medium-high — one new but well-documented API/data source, small point-extraction job | Strong literature backing with a directly relevant validation paper; upside concentrated in tail/event days which may matter disproportionately for your metric |
| **3** | Structural multi-model NWP disagreement, MEPS vs. ECMWF (Route 4) | Medium-high — sound general NWP-ensemble principle, but not found directly validated for SW_IN correction in the literature searched | Moderate-high — most likely of all routes to be genuinely decorrelated from your rejected "within-model ensemble spread" (#10) | Medium — new data source integration is real work; tight for one day | Highest "genuinely new signal" potential, traded against real execution-time risk and the same fold-instability risk pattern seen in Stage 6.4, so evaluate per-fold before accepting |
| **4** | Phase-partitioned MEPS cloud condensate, LWP vs. IWP (Route 3) | High as atmospheric physics (well-established Arctic cloud-radiation literature) | Uncertain — contingent entirely on whether your current MEPS features already implicitly include this; needs a 10-minute audit of your existing feature list before investing more time | Medium — depends on whether your archive already retains model-level MEPS fields | Verify feasibility first; if the raw fields are already accessible, this is nearly free and physically well-motivated; if not, drop for time reasons |
| **5** | Snow-cover × cloud diffuse-enhancement interaction (Route 5) | Medium — real, documented effect, but likely partially already implicit in MEPS's own albedo-aware radiation scheme | Low-moderate — marginal gain on top of existing MEPS radiation output is the open question | High — cheap interaction feature if snow/albedo data is already present | Lowest-risk, lowest-effort of the remaining routes, but also probably the smallest expected marginal gain; good "if time remains" addition, not a headline bet |

**Practical sequencing recommendation for your 48 hours:** Do Route 1 first (cheapest, safest, well-grounded, and directly explains a documented high-latitude/mountain-site failure mode your current architecture has no mechanism to capture). If Route 1 shows any positive, stable signal, layer Route 2 next (different physical channel, similarly low leakage risk, strong direct literature support). Only attempt Route 4 if the first two are done early and you have time left, given its higher data-engineering overhead and the instability risk that already burned Stage 6.4. Treat Routes 3 and 6 as conditional on a quick feasibility check of your existing data assets before committing real time.
