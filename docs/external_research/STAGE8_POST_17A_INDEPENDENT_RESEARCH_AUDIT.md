# POLARIS — Independent Research Audit: Beyond Stage 8.17A (AROME-Arctic vs MEPS Disagreement)

**Scope:** Independent verification of the Stage 8.17A real-AROME evidence package, followed by a literature-grounded evaluation of whether a directional/vector reformulation of AROME-MEPS disagreement is a scientifically defensible next research route for Nuolja solar-irradiance forecasting.

**No model experiment was run. No tuning was performed.** This is an audit and a research-design recommendation only.

---

## Part 1 — Independent Audit of the Provided Evidence

### 1.1 What I could and could not verify

I was given the actual row-level prediction file (`STAGE8_17A_REAL_AROME_ODD_PREDICTIONS.csv`, 4,152 rows), the machine-generated correlation table (`FEATURE_FORENSICS.csv`), the error-quantile table (`ERROR_REGIMES.csv`), the structured `POSTMORTEM.json`, and the two narrative reports (`POSTMORTEM.md`, `RESEARCH_HANDOFF.md`, `REBUILD_FINAL_REPORT.md`). I do **not** have the raw AROME-Arctic/MEPS NetCDF extraction, the feature-engineering code, or the "seed 817" historical artifact, so several provenance claims are auditable only at the level of internal consistency, not against ground truth.

**Reproduced independently from the raw prediction CSV (trustworthy):**

| Metric | Reported | Recomputed from CSV | Match |
|---|---:|---:|---|
| Control Daytime MAE | 36.211027 | 36.211027 | ✅ exact |
| Candidate Daytime MAE | 36.426418 | 36.426418 | ✅ exact |
| Delta MAE | +0.215391 | +0.215391 | ✅ exact |
| Control RMSE / Candidate RMSE | 64.230507 / 64.611649 | 64.230507 / 64.611649 | ✅ exact |
| Control Bias / Candidate Bias | +0.994557 / +0.537993 | +0.994557 / +0.537993 | ✅ exact |
| Night MAE | 0.000000 | 0.000000 | ✅ exact |
| Spearman(wind_disagreement_700, |error|) | −0.0746 | −0.0746 | ✅ exact |
| Spearman(wind_disagreement_700, signed residual) | +0.0482 | +0.0482 | ✅ exact |
| Spearman(LWP_disagreement, |error| / signed residual) | +0.0746 / +0.0763 | +0.0746 / +0.0763 | ✅ exact |
| Row count structure | 173 ODD origins × 24 h = 4,152; 2,883 flagged daytime | 4,152 rows, 2,883 daytime | ✅ consistent |

So the **headline degradation result and the signed-residual/absolute-error correlations are genuinely reproducible from the artifact you have on disk**, not just asserted in prose. That is the single most important finding in the package, and it holds up.

### 1.2 A material inconsistency I found — treat the "redundancy" narrative with caution

The postmortem's argument that the disagreement features are "redundant" with existing baseline features is its main evidence for *why* the model failed, and it is used to steer the reader away from the disagreement signal entirely. I checked this against `FEATURE_FORENSICS.csv`, the machine-generated correlation table that is supposed to be the source of that argument — and the numbers **do not match**:

| Claim (in `POSTMORTEM.md` §5) | `POSTMORTEM.md` value | `FEATURE_FORENSICS.csv` value | Discrepancy |
|---|---:|---:|---|
| `wind_disagreement_700` vs `ctx_std_6h` | **+0.4218** | **−0.1905** | Wrong sign *and* wrong magnitude |
| `wind_disagreement_700` vs `u700` | **−0.3812** | **+0.5694** | Wrong sign *and* wrong magnitude |
| `LWP_disagreement` vs `lwp_latest` | **+0.6812** | **+0.8939** | Same sign, magnitude off by 0.21 (understates the true redundancy) |
| `LWP_disagreement` vs `fc_cloud_cover`/`cloud_frac`* | +0.5419 | +0.6053 | Close but not exact |

*`fc_cloud_cover` and `cloud_frac` are the identical column in the forensics file (both rows show 0.6053), so this row alone should have been unambiguous.

This means the specific causal story in the postmortem — "wind disagreement is basically a repackaged version of `ctx_std_6h` and `u700`" — is **not supported by its own cited evidence**. The forensics CSV actually shows the *opposite* sign relationship with `u700` and a much weaker relationship with `ctx_std_6h` than claimed. Conversely, the LWP redundancy is understated, not overstated, in the prose (0.89 vs the claimed 0.68 — genuinely very high, arguably even more damaging to the LWP feature's novelty than the postmortem says).

**Implication for this audit:** I am treating `FEATURE_FORENSICS.csv` (machine-generated, directly computable, and internally self-consistent) as authoritative over the narrative correlation claims in `POSTMORTEM.md`, and I recommend POLARIS do the same going forward. This doesn't overturn the headline MAE result (that part is independently reproducible from raw predictions, see 1.1), but it means the *explanation* for why the feature failed is partly unverified/incorrect prose, not verified analysis. Future postmortems should be generated programmatically from the underlying tables rather than narrated, or at minimum spot-checked before being treated as settled science.

### 1.3 Other provenance notes (lower confidence, flagged not resolved)

- The claim that the historical +$35.24$ W/m² figure came from `np.random.seed(817)` synthetic noise is plausible (it would explain a suspiciously clean improvement) but **no artifact in this package lets me verify it independently** — I did not receive the historical feature-extraction code. It should be cited as "asserted by the team that ran the rebuild," not as independently confirmed.
- The point-estimate delta (+0.2154 W/m²) and the reported bootstrap mean delta (+0.1774 W/m²) differ by about 18%. This is plausible if the bootstrap resamples by *origin* (173 units) rather than by row (2,883 daytime rows), which would reweight horizons unevenly relative to a flat row-mean — but the resampling unit isn't documented anywhere in the package. Worth a one-line clarification in future write-ups; it doesn't change the conclusion (the CI still spans zero either way).
- I have no way to verify the THREDDS extraction, the SHA256 provenance chain, or the causal-gate claims beyond internal arithmetic consistency (4,152 = 173 × 24 checks out; 2,883 daytime rows is internally consistent with the reported solar-elevation-based flag). These are consistent, not independently verified against MET Norway's archive.

### 1.4 Bottom line on the audit

The **decision to close the raw-scalar-magnitude route is well-supported** — the reproducible numbers back it up, and the near-zero signed-residual correlation is real. But the **specific mechanistic explanation offered (pure redundancy with existing features) is only partly correct**, and one of its two headline correlations is actually backwards. That matters, because it changes which follow-up hypotheses are worth taking seriously (see Part 3).

---

## Part 2 — Literature-Grounded Review of the Physical Questions

### 2.1 AROME-Arctic and MEPS are not a "high-res vs ensemble" pair — they are the same model family at the same resolution

The handoff document frames the comparison as "a high-resolution non-hydrostatic convection-permitting model (AROME-Arctic) vs the operational ensemble control (MEPS)," implying AROME contributes resolution-driven independent information. This framing is not accurate. MET Norway's own documentation states that <cite index="5-1">AROME-Arctic provides short term forecasts and the horizontal geographic resolution is 2.5 kilometres, and the model system is built on HARMONIE-Arome</cite>, and MEPS is described as <cite index="11-1">the MetCoOp Ensemble Prediction System, which provides 30 ensemble members every six hours with leadtimes out to 61 hours and a spatial grid spacing of 2.5 km</cite>, itself <cite index="9-1">an implementation of the ensemble version HarmonEPS of the convection-permitting NWP model HARMONIE-AROME</cite>.

**Both models are HARMONIE-AROME at the same 2.5 km grid spacing.** They differ in domain (Arctic vs Nordic), lateral boundary conditions, and (for MEPS) ensemble perturbations — not in physics or resolution. This is a real weakness in the project's framing, independent of the postmortem's analysis: "AROME disagrees with MEPS" is closer to "two runs of the same model system disagree because of different boundary conditions/domain configuration," not "a fundamentally different, higher-fidelity model disagrees with a coarser one." That doesn't make the comparison worthless (boundary-condition/domain differences are a legitimate, if weaker, source of independent information — this is exactly the "poor man's ensemble" logic, see §2.4), but it does lower the prior that AROME is contributing some qualitatively superior physical representation that MEPS lacks.

### 2.2 Cloud advection is wind-driven — but the appropriate level is cloud-height-dependent, not a fixed pressure surface

The core physical premise behind any wind-disagreement feature is that cloud motion tracks the wind at cloud height. The solar-forecasting literature treats this as a working assumption with known failure modes: <cite index="15-1">cloud advection is expected to be a direct result of wind patterns at cloud-height levels, an idea reflected in various works where wind information at cloud height is used as a driver of solar variability in solar forecasting applications. However, relating spatio-temporal characteristics of the solar radiation to the wind speed is not obvious. In some meteorological situations, such as orographic clouds, the wind speed and the apparent cloud movement can be decoupled. More generally, the coexistence of different layers of clouds advecting in different directions questions the validity of the use of wind information at a single level.</cite>

Operational multi-layer solar nowcasting systems handle this explicitly rather than picking one fixed level: NOAA's CIRACast-style scheme <cite index="23-1">groups pixels into contiguous cloud objects whose future positions are predicted using four-dimensional model wind fields, selecting steering levels corresponding to the cloud height properties of each cloud group</cite>. This is a direct, citable precedent for **level-matching to cloud height rather than using a fixed 700 hPa surface**, and it is a stronger, better-grounded critique of Stage 8.17A's design than anything in the postmortem: the feature wasn't just "unoriented," it was very likely applied at the *wrong vertical level* for a large fraction of cloud regimes (Nuolja summit sits under orographic and low-level stratiform cloud a substantial fraction of the time, which is exactly the regime the literature flags as most likely to decouple from a mid-tropospheric steering wind).

### 2.3 Nuolja is a mountain-summit station — 700 hPa is defensible for free-tropospheric transport but mismatched to boundary-layer/orographic cloud

The mountain-meteorology literature is consistent on two points relevant here. First, complex terrain degrades NWP skill most in the near-surface layer, not the free troposphere: <cite index="32-1">the improvements from higher-resolution coupling are most pronounced for 10-m wind speed in mountainous regions, where a realistic representation of the topography is necessary to account for local topographic effects</cite>, and near-surface wind/temperature errors in complex terrain are <cite index="33-1">primarily due to random turbulent processes not appropriately represented in the models</cite>. This is a point in *favor* of using 700 hPa (well above the boundary layer, less contaminated by unresolved terrain effects) as a relatively "clean" comparison level between two models.

Second, and cutting the other way: the actual predictand — solar irradiance at a mountain summit — is disproportionately shaped by boundary-layer and orographically-forced cloud (cap cloud, upslope stratus), which is precisely the regime least well captured by a 700 hPa steering-wind comparison, and single-point mountain stations are known to be poorly representative of the surrounding model grid volume in general: <cite index="35-1">the classical grid point-by-grid point model validation is likely unsuitable for mountainous terrain, because the question of representativeness of a single station in time and space arises, and single point observations cannot assess whether the numerical model is able to account for heterogeneity in space</cite>. So there is a genuine **level/process mismatch**: the feature compares free-tropospheric transport winds, but a large share of Nuolja's cloud variability is boundary-layer/orographic in origin and not well steered by 700 hPa flow at all. This is a second, independent reason (beyond simple magnitude-vs-direction) that the original feature could fail even if AROME and MEPS genuinely disagreed about something real.

### 2.4 The correlation pattern found (difficulty, not direction) is the textbook signature of a "poor man's ensemble," and it points to a different *use* of the signal, not necessarily a dead end

Using disagreement between independently-run operational NWP models as an uncertainty proxy is an established technique with its own name and literature: a <cite index="24-1">poor man's ensemble is a set of independent numerical weather prediction model forecasts from several operational centers, which samples uncertainties in both the initial conditions and model formulation</cite>. Critically, this literature's own verification results show the same signature Stage 8.17A found: <cite index="27-1">low values of the spread-skill correlation indicate that it is not possible to predict the forecast skill from the spread of the ensemble alone; however, the number of models predicting a particular event gives a good indication of the likelihood of the ensemble to envelop the location and magnitude of that event</cite>. In other words: **model disagreement routinely fails to predict the sign of the error while still carrying real information about the width/uncertainty of the outcome.** That is exactly the pattern in the Stage 8.17A data (weak/near-zero signed-residual correlation, weak-but-nonzero absolute-error correlation).

This literature converts what the postmortem treats as a dead end into a specific, falsifiable redirection: **the feature may be structurally unsuited to a mean-point regressor trained under an absolute-error loss, while still being useful as an input to an uncertainty/interval model** (e.g., quantile regression, a prediction-interval width model, or a ramp-probability classifier). That is a different modeling target, not a rerun of the same experiment.

---

## Part 3 — Assessment of the Postmortem's Proposed Route, and What I Think Is Actually Defensible

### 3.1 Where the postmortem's own candidate direction is weaker than it looks

The postmortem proposes "directional wind vector disagreement (angle & along-solar-axis projection)" as the one route requiring independent research. Taken at face value this is physically reasonable (§2.2 supports the general idea that direction matters, not just magnitude). But two things make me skeptical that this specific proposal, as stated, is likely to work if implemented literally:

1. **It doesn't address the level-mismatch problem.** Projecting the *same* 700 hPa vector difference onto the solar azimuth still uses a steering level that the literature says is often wrong for the cloud types actually affecting a mountain summit (§2.2, §2.3). A better-aimed but still-mis-leveled feature can still fail.
2. **It doesn't address the averaging-dilution problem.** Stage 8.17A evaluated the feature against *all* daytime rows. But directional cloud-edge information should only matter in transitional/broken-cloud regimes where a cloud edge is plausibly crossing the sun-target line; in persistently clear or persistently overcast conditions (a large fraction of any dataset, especially at a high-latitude site with long stable synoptic regimes), wind direction is close to irrelevant to irradiance. Averaging a real but localized signal across all conditions is exactly the mechanism that could produce a "near-zero" correlation even if the effect is genuinely present in the subset where it should matter. The postmortem's own quantile tables partially hint at this (delta MAE is not monotonic across the disagreement quantiles) but this was never tested directly.

Neither of these is addressed by "add sin/cos of the angle" alone. That is a red flag that the proposed route, if implemented exactly as written, risks reproducing the same failure mode for a different reason: not "unoriented," but "wrong level, wrong regime."

### 3.2 What I consider the actual defensible next hypothesis

**Physical hypothesis:** Among Nuolja daytime periods with elevated short-term irradiance variability (a proxy for broken/transitional cloud, i.e. periods where clouds are plausibly moving across the sun-target line rather than persisting or being absent), the along-solar-azimuth component of AROME-vs-MEPS wind-vector disagreement, evaluated at a wind level matched to the actual/forecast cloud layer rather than a fixed 700 hPa, carries directional information about short-horizon (1–3 h) GHI residuals that is diluted to near-zero when averaged over all-sky conditions and a physically mismatched level, as was done in Stage 8.17A.

**Required variables** (beyond what Stage 8.1/8.17A already extracted):
- U/V wind components at multiple pressure levels (e.g. 925, 850, 700, 500 hPa) from *both* AROME-Arctic and MEPS at the same 347 origins — not just 700 hPa.
- A cloud-layer indicator to select the matching level: cloud base/top height or the pressure level of maximum liquid/ice water content, from either model's vertical profile fields (if archived) or a documented proxy if full profiles aren't available.
- Solar azimuth at each valid time (already computable from existing geometry features).
- A regime/subset flag for "transitional" conditions, defined causally (e.g. top tercile of `ctx_std_3h`/`ctx_std_6h`, or a clear-sky-index-based ramp detector) — must be defined and frozen on EVEN-fold data only, before any correlation is computed, to avoid leakage into the eventual test.

**Exact feature formulation** (for the level(s) selected):
- `Δu_L = arome_u_L − meps_u_L`, `Δv_L = arome_v_L − meps_v_L`
- Along-sun component: `Δ_along = Δu_L·sin(azimuth) + Δv_L·cos(azimuth)`
- Cross-sun component: `Δ_cross = −Δu_L·cos(azimuth) + Δv_L·sin(azimuth)`
- Vector angle disagreement: `θ_diff = atan2(arome_v_L, arome_u_L) − atan2(meps_v_L, meps_u_L)`, wrapped to [−π, π]

**Causal availability requirement:** confirm, before any further work, that multi-level U/V and a cloud-layer height/profile field are actually retrievable from MET Norway's THREDDS archive for both models at hourly resolution across all 347 origins at tractable extraction cost — the original 8.17A pull was a single-level slice; a multi-level, dual-model pull is a materially larger OPeNDAP job and should be scoped (or explicitly ruled out) before committing further effort.

**Why this is genuinely different from Stage 8.17A**, not a rerun: (i) direction-resolved, not magnitude-only; (ii) level-matched to cloud height rather than a fixed free-tropospheric level chosen for reasons unrelated to cloud physics; (iii) evaluated on a pre-registered transitional-regime subset rather than blanket daytime averaging, which is the specific mechanism by which a real, localized signal could have been averaged into invisibility in the original test; (iv) explicitly tested first as an *uncertainty/interval* signal (per the poor-man's-ensemble literature, §2.4) in addition to — not instead of — a point-correction test, since the existing evidence (near-zero signed-residual correlation, weak-but-real |error| correlation) is the classic spread-vs-skill pattern for that use case.

**Why it could contain information Stage 8.1 doesn't already have:** Stage 8.1 already includes MEPS-side `u700`/`v700`. It does not include any AROME-side wind at any level, nor any cross-model direction comparison. A genuinely level-matched, direction-resolved, regime-conditioned disagreement encodes "do two independently-initialized convection-permitting runs agree on which way the relevant cloud layer is moving right now" — a piece of information that is not linearly reconstructable from either model's wind field alone, and is conceptually distinct from the generic "how much are these two runs disagreeing overall" signal that `ctx_std_6h` and `cloud_frac` already capture (and which, per the corrected redundancy numbers in §1.2, the *scalar* magnitude features were substantially redundant with).

**What would falsify this** (all to be checked on EVEN-fold data before any retraining):
- If, restricted to the pre-registered transitional subset, `|Spearman(signed residual, Δ_along)| < 0.10` for the level-matched feature — this falsifies the directional-information hypothesis outright; the disagreement is noise/difficulty proxy only, even after fixing level and regime.
- If level-matching to cloud height produces materially the same (weak) correlation as the fixed-700 hPa version — this falsifies the level-mismatch explanation specifically (the problem was orientation/regime, not level, or the problem is unfixable).
- If, used purely as an input to a quantile/interval model, it fails to improve CRPS or pinball loss relative to a baseline without it, on the same transitional subset — this falsifies the "uncertainty information" fallback hypothesis and would close the entire AROME-MEPS-disagreement research line at Nuolja, not just the point-correction variant.

**Recommended pre-registered experiment** (to be designed, not run, at this stage):
1. Freeze the transitional-regime subset definition and the cloud-layer level-selection rule using EVEN-fold data only.
2. Primary pre-registered test: Spearman correlation of `Δ_along` (and separately `θ_diff`) against signed 1–3 h residuals, on the frozen transitional subset, EVEN folds only, with a pre-declared minimum effect size (e.g. |r| > 0.15) required to proceed.
3. Secondary pre-registered test: CRPS/pinball-loss improvement from adding the directional features to an uncertainty/quantile model, EVEN folds only, same subset.
4. Only if both gates pass does a full retrain proceed to the 173-origin ODD held-out evaluation, using the same rigor already demonstrated in 8.17A (bootstrap CI, quantile error tables, permutation importance).
5. Given this is now the second-to-third attempt to extract value from AROME-MEPS disagreement at this site (raw scalar → historical synthetic-seed episode → this proposal), apply a stricter-than-usual bar and report effect sizes with correction for repeated testing, not just a single point estimate.

---

## Part 4 — Direct Answers to the Closing Questions

**1. Strongest scientifically justified route:**
A cloud-layer-matched, direction-resolved (azimuth-projected and angle-differenced) AROME-vs-MEPS wind disagreement, evaluated first as a pre-registered correlation test restricted to transitional/broken-cloud regimes, and tested as an uncertainty/quantile-model input before (or alongside) any point-correction use — not the blanket-daytime, fixed-700-hPa, magnitude-only design used in 8.17A.

**2. Strongest argument against it:**
AROME-Arctic and MEPS are the same HARMONIE-AROME model system at the identical 2.5 km resolution, differing mainly in domain and boundary conditions — so their "disagreement" may be substantially generic synoptic-activity noise rather than independent cloud-motion physics. The corrected feature-forensics numbers (§1.2) show the LWP disagreement feature is even *more* redundant with existing cloud/context features than the postmortem claimed (r≈0.89 with `lwp_latest`, not 0.68), and the poor-man's-ensemble literature shows disagreement-as-uncertainty signals routinely fail exactly this kind of directional test even when the underlying models are genuinely independent. A regime-conditioned, level-matched reformulation could simply relocate the same weak signal rather than reveal a new one.

**3. Required evidence before experimentation:**
- Confirmation that multi-level, dual-model wind and cloud-layer data are causally retrievable from THREDDS at tractable cost for all 347 origins.
- A corrected, code-generated (not narrated) redundancy analysis, since the current one contains a sign error and a magnitude error on its two headline claims (§1.2).
- The EVEN-fold-only pre-registered correlation and CRPS/pinball-loss gate tests described above, passed *before* any retraining is authorized.

**4. Recommended experiment design:**
As specified in §3.2, steps 1–5: freeze subset/level rules on EVEN data → pre-registered directional-correlation gate → pre-registered uncertainty-calibration gate → only then a full retrain and ODD evaluation with the same rigor (bootstrap CI, quantile tables, permutation importance) already used in 8.17A.

**5. Routes that should NOT be pursued:**
- Any further work on raw, un-leveled, un-conditioned point-scalar magnitude disagreement — correctly closed.
- Lead-time delta/trajectory of the scalar disagreement — already tested and weak, and nothing in the literature reviewed here suggests a mechanism that would reverse that finding.
- Adding a solar-azimuth-projected wind term directly into the existing all-daytime, MAE-optimized point regressor without first fixing level-matching and regime-conditioning — this is very likely to reproduce the original averaging-dilution failure for a different reason.
- Continuing to frame AROME-Arctic as a "higher-resolution" model relative to MEPS in any future write-up — both are 2.5 km HARMONIE-AROME; this premise is factually incorrect and should be dropped from the project's internal narrative regardless of what happens to the research route itself.
