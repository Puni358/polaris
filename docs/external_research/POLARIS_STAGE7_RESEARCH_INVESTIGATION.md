# POLARIS — Stage 7 Research Investigation
**Question:** Is there a scientifically credible path from 28.7026% ODD daytime nMAE toward <15% (stretch: <10%)?
**Scope of this document:** research only. No code, no implementation. Evidence is explicitly separated by type.

---

## 1. Reconstructed Experimental History

| Stage | Method | ODD nMAE (daytime) | Δ vs prior | What it added |
|---|---|---|---|---|
| Baseline | Seasonal Naive | 42.76% | — | Climatology only |
| — | Chronos-2 (foundation TS model) | 41.91% | −0.85 pp | Generic sequence model, no physics |
| 3B | Solar/cloud neural model | 41.06% | −0.85 pp | NWP cloud cover as NN input |
| 4 | Physical/ML ensemble | 33.70% | **−7.36 pp** | Physical clear-sky model blended with ML residual |
| 5.2 | Residual GBDT | 30.32% | −3.38 pp | Context/persistence features (`ctx_*`), disagreement features |
| 6.6 | + LWP/IWP cloud microphysics | 28.7026% | −1.61 pp | Column-integrated liquid + ice water path, surface-pressure-truncated |

**Pattern in the evidence, not inference:** the size of each improvement is shrinking — 7.36 pp → 3.38 pp → 1.61 pp. This is the single most important empirical fact governing what to expect from Stage 7, and it is discussed in Section 5.

### Rejected / non-winning directions (evidence about what does *not* help here)
- **Spatial cloud probes** — horizontal cloud-field information around the station did not add value.
- **Wind/advection probes** — cloud motion/advection features did not help.
- **MEPS ensemble spread** — forecast uncertainty/spread across ensemble members did not help the *point* forecast.
- **Thermal-IR satellite observation features** — did not help.
- **Deterministic forecast revisions** (successive NWP run-to-run updates) — did not help.
- **Snow/cloud interaction** — did not help.

Taken together, these six rejections are informative: everything that tried to capture *where clouds are, how they move, or how uncertain the forecast is* has failed. The one thing that worked (LWP/IWP) instead captures *how radiatively thick the cloud column is*. This is a meaningful pattern: **the dominant remaining error source at this site looks like a column radiative-transfer problem, not a cloud-nowcasting/advection problem.** (This is my inference from the pattern of results — not a separate documented conclusion in your files.)

---

## 2. Screening the 24 candidate directions against this evidence

I grouped your 24 directions into six clusters and checked each against (a) whether POLARIS has already tested it, (b) whether it's causally available at t0, and (c) whether it's *new information* relative to LWP/IWP.

| Cluster | Directions | Already tested? | Verdict |
|---|---|---|---|
| Cloud microphysics / optical properties (1,2,3) | COD, effective optical thickness, LWP/IWP | LWP/IWP tested & won | COD is a *reframing* of the same physical quantity POLARIS already has, not new information, **unless** paired with an explicit transmittance model (see §4.1) |
| Cloud geometry (4,5,6) | Vertical structure, base/top, multi-layer | Not tested | Genuinely new — column integration discards the *shape* of the profile |
| Radiation budget / decomposition (7,8,9,10) | Radiation-budget vars, direct/diffuse, DNI/DHI/GHI relations, clear-sky index | **Not tested** — POLARIS uses `clearsky_ghi` (PVLIB) but never ingests MEPS's *own* radiative-transfer output | Genuinely new, and the single biggest gap identified below (§4.1) |
| Motion / spatial (11,13) | Cloud advection, terrain/horizon effects | Advection tested & rejected; terrain/horizon **not tested** | Terrain/horizon is genuinely new and mechanistically distinct from advection |
| Satellite (14,19) | Additional satellite cloud products | Thermal-IR rejected; VIS/COD not tried | See §3 — largely blocked by geography at this latitude |
| Modeling strategy (20–24) | Sequence models, physics-informed hybrids, horizon/regime-specific, probabilistic | Ensemble spread (≈24) rejected; others not tried | Regime-specific modeling is a plausible, cheap structural change (§4.5) |

---

## 3. Literature findings — and why several headline results don't transfer here

**From literature (not from your experiments):**

- A 2025 physics-informed method forecasts satellite-derived cloud optical depth (COD) with deep learning, then converts COD to GHI via a physical transmittance relationship rather than a black-box regression — and this outperforms purely data-driven baselines.
- Satellite cloud-motion-vector and CNN/UNet nowcasting methods (Heliosat-style, HelioNet) report meaningful gains (roughly 8–11% RMSE) for intra-hour to few-hour horizons using **geostationary imagery**.
- Multiple independent sources confirm that **geostationary satellites are blind above roughly 60–66° latitude** — including a paper specifically on Arctic-circle solar forecasting in Norway, which notes geostationary coverage gaps, snow-as-cloud misclassification, and low-sun-angle retrieval problems as characteristic high-latitude failure modes.
- That same Arctic paper uses a NWP-derived **integral of surface net downward shortwave flux** (from NORA3, a sibling/precursor system to MEPS) as a direct model input — i.e., the NWP's own radiation-scheme output, not just cloud fraction or cloud fields.
- Cloud vertical-structure literature (multi-layer cloud radiative-effect studies, COD/CER retrieval-under-vertical-perturbation studies) consistently shows that column-integrated water content is an incomplete predictor of surface transmittance; the same LWP can correspond to very different attenuation depending on whether it is one thick low deck or a thin high layer over a thin low layer.
- Terrain/horizon-shading literature (glacier and mountain-PV studies, and commercial irradiance providers like Solcast/SolarAnywhere) shows that beam-blocking and reduced sky-view-factor from surrounding terrain are large, systematic, and purely geometric — solvable from a static digital elevation model with no forecast-time data at all.

**Conclusion on transferability (my inference, clearly separated from the literature itself):** Nuolja sits at 68.36°N — well inside the geostationary blind zone that the literature itself identifies. This means the flashiest recent result (satellite-COD-based hybrid GHI forecasting) is **not directly importable** at this site. The Arctic-forecasting paper is the more relevant precedent, and its key methodological idea — feed the NWP's *own radiative-transfer output*, not just its cloud inputs — is directly transferable to MEPS and is, as far as your uploaded documents show, **not yet done in POLARIS**.

---

## 4. Ranked breakthrough directions

Scoring: Potential (P), Physical novelty (N), Causal feasibility (C), Data availability (D), Implementation cost (Cost, lower=better), Leakage risk (Leak, lower=better), Generalization potential (G). Scale 1 (low) – 5 (high), except Cost/Leak where lower is better.

| Rank | Direction | P | N | C | D | Cost | Leak | G |
|---|---|---|---|---|---|---|---|---|
| 1 | MEPS native downwelling SW radiation-scheme output as a feature/base predictor | 4 | 5 | 5 | 5 | 1 | 1 | 4 |
| 2 | Static terrain/horizon shading correction to `clearsky_ghi` | 3 | 4 | 5 | 5 | 1 | 1 | 5 |
| 3 | Explicit physically-motivated transmittance function of LWP/IWP/cloud_frac (replacing/augmenting raw features fed to the GBDT) | 3 | 4 | 5 | 5 | 2 | 1 | 4 |
| 4 | Vertical-profile decomposition of existing MEPS 3D fields (low/mid/high layer LWP+IWP, cloud-base-pressure proxy) | 3 | 4 | 4 | 5 | 3 | 3 | 3 |
| 5 | Regime-specific (thin/broken-cloud vs. thick-overcast) two-model structure | 2 | 2 | 5 | 5 | 3 | 3 | 3 |
| 6 | CAMS/climatological aerosol (Linke turbidity) correction to the clear-sky baseline | 2 | 3 | 5 | 4 | 1 | 1 | 4 |
| 7 | Polar-orbiting satellite cloud products (VIIRS/AVHRR overpasses) | 1 | 4 | 2 | 3 | 4 | 2 | 2 |
| 8 | Snow/multiple-reflection diffuse-enhancement reformulation | 1 | 2 | 4 | 4 | 3 | 2 | 2 |

### 4.1 MEPS's own radiative-transfer output (Rank 1)
**Evidence type: inference, grounded in a documented MET Norway variable and a literature precedent.** MET Norway's post-processed products (MET Nordic / MEPS family) expose an `integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time`-type diagnostic — i.e., the actual output of the NWP's own radiation scheme, which already performs a real (if coarse) multi-scattering radiative-transfer calculation using the model's full 3D cloud fields, not just column-integrated LWP/IWP. POLARIS's current 31-feature set uses `fc_cloud_cover`, `cloud_frac`, `lwp_latest`, `iwp_latest` — but, based on the manifest, never ingests this NWP-computed flux itself. This matters because your GBDT currently has to *learn* the entire cloud→transmittance mapping empirically from only 174 EVEN-fold origins; the NWP's radiation scheme has already done that calculation using real physics on a much larger effective sample (the physical parameterization was tuned/validated over a huge multi-year, multi-site dataset by MET Norway). Feeding that computed flux in — either as a feature, or as an alternative/blended base predictor to `clearsky_ghi` — is low-cost, fully causal (same forecast cycle, same NWP run), and is the most novel gap identified in this investigation.

### 4.2 Terrain/horizon shading (Rank 2)
**Evidence type: literature-supported inference.** Nuolja is at 702 m elevation in mountainous Arctic terrain. `clearsky_ghi` from PVLIB's Ineichen model assumes a flat, unobstructed horizon by default. At high latitude, a large fraction of daytime hours occur at low solar elevation, which is exactly when horizon obstruction (beam-blocking + reduced sky-view-factor) matters most. This is a static, one-time DEM-derived correction — it requires no new forecast-time data, has essentially zero leakage risk, and directly targets the bias term (Stage 6.6 still carries +1.14 W/m² daytime bias). It is not mentioned anywhere in the uploaded experiment history, so it appears genuinely untested.

### 4.3 Explicit transmittance parameterization (Rank 3)
**Evidence type: inference from literature pattern + your own results.** The literature's physics-informed COD→GHI methods work by converting a physical quantity into GHI through an explicit, saturating transmittance relationship, rather than asking a generic regressor to discover that nonlinearity from scratch. Your Stage 6.6 win came from LWP/IWP fed as raw features into a `HistGradientBoostingRegressor` — the tree ensemble must implicitly learn the (steep, saturating) relationship between water path and attenuation from a small sample. Precomputing an explicit attenuation/transmittance term from LWP+IWP+cloud_frac using a simple physically-motivated functional form, then handing that single well-shaped feature to the model (in place of or alongside the raw quantities), costs no new data and directly reduces the burden on a tree ensemble trained on <200 origins.

### 4.4 Vertical-profile decomposition (Rank 4)
**Evidence type: literature-supported, moderate confidence.** Cloud vertical-structure literature is consistent: two columns with identical total LWP but different vertical placement (thin high cloud vs. thick low cloud) can have substantially different surface transmittance. POLARIS already extracts full 13-level MEPS pressure-level condensate fields to build `lwp_latest`/`iwp_latest` — splitting that same extraction into low/mid/high layer sums (rather than a single column integral) is a real experiment, not new data acquisition. Flagged lower than 1–3 because of overfitting risk: with 174 EVEN origins, adding several new correlated features increases variance, and this must be evaluated with the same EVEN-CV gates used previously.

### 4.5 Regime-specific modeling (Rank 5)
**Evidence type: hypothesis, weakly supported.** If thin/broken cloud (where LWP-to-transmittance is highly sensitive) and thick overcast (where it saturates) are physically distinct regimes, a single global tree ensemble may be compromising fit in both. A two-model or gated structure is cheap to test but is a modeling-strategy change rather than a new data source, and the "ensemble spread" rejection suggests uncertainty-based signals in general haven't helped here — mild negative prior.

### 4.6 Lower-priority / lower-confidence items
- **Polar-orbiting satellite products (VIIRS/AVHRR):** genuinely new information, but overpass frequency (1–2/day) is a poor match for hourly forecasting and complicates causal-at-t0 guarantees. Rank low on practical grounds, not physical grounds.
- **Aerosol/Linke turbidity correction:** plausible, cheap, but likely a second-order effect at high latitude where cloud attenuation dominates variance; worth a fast, cheap test rather than a headline bet.
- **Snow/multiple-reflection diffuse enhancement:** POLARIS's own history already lists "snow/cloud interaction" as rejected. Any resurrection of this idea should be framed differently (specifically, snow-albedo multiple-reflection between surface and cloud base, which is mechanistically distinct from whatever the earlier "snow/cloud interaction" test covered) — otherwise there is no reason to expect a different outcome.

---

## 5. The hard question: is there a credible route from 28.7% to 15%?

**Separating evidence from inference here is essential.**

*From your own experimental history (fact):* the gains have been strictly diminishing — 7.36 pp, then 3.38 pp, then 1.61 pp. Closing the remaining gap to 15% requires roughly **13.7 additional percentage points** of nMAE reduction — nearly **double** the entire cumulative improvement achieved across Stages 3B through 6.6 combined (12.36 pp total, four stages). Reaching 10% would require over 18.7 pp — more than triple that cumulative history.

*From the literature (fact):* the largest published gains in this space come from combining information genuinely unavailable to a purely NWP-cloud-based model — chiefly high-resolution geostationary satellite imagery for cloud motion/optical-depth nowcasting. That category of information is **structurally unavailable at this station's latitude**, which removes the single most productive lever seen in the broader literature.

*My inference, stated as inference:* there is no single item in Section 4 that plausibly delivers a double-digit-percentage-point jump on its own — nothing here resembles the Stage 4 discontinuity (physical/ML ensemble, −7.36 pp), which came from a structural change (blending a physical model with ML), not a single feature. The evidence instead points toward **a continued sequence of feature- and structure-level refinements**, each plausibly worth somewhere in the historical Stage 5.2/6.6 range (roughly 0.5–2 pp), if Rank 1–3 items pan out. Stacking Rank 1 (NWP radiation-scheme output), Rank 2 (terrain shading), and Rank 3 (transmittance parameterization) is the most defensible route toward **meaningful further reduction — plausibly into the mid-to-low 20s% range in a focused research cycle** — but I am not able to responsibly project this as reaching 15%, and I have deliberately not done so. Whether 15% (and especially 10%) is achievable at all, given a single station, one year of data, no usable satellite cloud retrieval, and an already-diminishing-returns curve, is genuinely uncertain rather than something the evidence lets me rule in or out.

---

## 6. Proposed Stage 7 roadmap (3–5 experiments, no code)

1. **Extract and test MEPS's native surface downwelling shortwave radiation-scheme output** as (a) an added feature to the current 31, and (b) an alternative/blended base predictor alongside `clearsky_ghi`. Highest expected value, lowest cost and leakage risk of anything identified.
2. **Build a static terrain-horizon profile for Nuolja from a DEM and apply it as a beam-blocking/sky-view-factor correction to `clearsky_ghi`.** Zero forecast-time data cost, zero leakage risk, targets the persistent positive bias directly.
3. **Replace or augment raw `lwp_latest`/`iwp_latest`/`lwp_x_cloud` with an explicit, physically-motivated transmittance/attenuation feature** derived from the same variables, reducing the burden on the GBDT to learn a saturating nonlinearity from a small sample.
4. **Decompose the existing 13-level MEPS condensate extraction into low/mid/high vertical-layer LWP+IWP sums** (reusing already-extracted data, no new acquisition) and gate strictly through the existing EVEN-CV protocol given overfitting risk at N=174.
5. *(Stretch, lower priority)* **Cheap test of a CAMS/Linke-turbidity aerosol correction to the clear-sky baseline**, primarily to rule in/out a second-order clear-sky bias source separate from cloud attenuation.

Do not promise 15% or 10% is reachable; treat each experiment as an independent EVEN-CV-gated, ODD-confirmed test exactly as Stages 4–6.6 were run, and expect continued diminishing returns unless one of these produces a structural (Stage-4-like) surprise.
