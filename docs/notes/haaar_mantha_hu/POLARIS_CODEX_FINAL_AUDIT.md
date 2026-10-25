# POLARIS — CODEX INDEPENDENT RESEARCH RECORD

**Reconstructed:** 2026-09-14  
**Method:** repository-only reconstruction from prediction tables, experiment outputs, executable scripts, freeze manifests, registries, and forensic corrections. Historical reports were evidence, never ground truth. No new model fitting, ODD evaluation, data acquisition, or benchmark mutation was performed.

## Executive result

The current *reproducible* official champion is **Stage 8.1, `Stage8.1_700hPa_Wind_Control`**, a 37-feature `HistGradientBoostingRegressor` residual correction. Its protected ODD CSV has 4,152 rows and SHA-256 `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`. Independent row-level recomputation gives daytime MAE **36.188657 W/m²**, nMAE **28.068774%**, RMSE **64.219495 W/m²**, bias **+1.439399 W/m²**, and night MAE **0.0 W/m²**.

This conclusion separates reproducibility from historical promotion. Stage 8.17A was later described as a 35.241085 W/m² / 27.3337% champion, but its raw AROME inputs and 40-feature extractor are absent and the executable reconstruction instead yields 36.188657 W/m². It is a historical, unverified reference—not a current reproducible champion. Stage 8.19's purported 34.821405 W/m² / 27.0081% result is invalid: its forensic record identifies hard-coded metrics, synthetic AROME/ABIS fallbacks, and no authoritative 173×24 ODD prediction table.

## 1. Benchmark reconstruction

- **Target/data:** 2024 hourly `SW_IN` at SITES Nuolja (Mount Nuolja, ~68.362°N, 18.739°E). Original source is 10-minute SITES observations (`data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv`), aggregated into project hourly tables. A forecast row is hourly—not a 10-minute nowcast.
- **Origins/horizon/time:** 347 PASS daily origins × H1–H24 = **8,328 rows**. Scripts represent an origin as 00:00 UTC on day D; H1 is the first future valid hour and H24 the 24th. UTC is the data contract; solar/local timing is represented by geometry features.
- **Split:** even-indexed development origins: 174 / 4,176 rows; odd holdout origins: 173 / 4,152 rows. Both cover all months. A historical manifest reverses 173/174, but the freeze and 4,152-row ODD artifact settle the current contract.
- **Day/night:** scoring daytime is `y_true > 0`, yielding 2,883 ODD day and 1,269 night rows. Frozen output forces zero for `solar_elevation <= 0` or `clearsky_ghi == 0`, hence night MAE is 0. Mean daytime actual is 128.928528 W/m².
- **Metrics:** primary nMAE = `daytime MAE / mean(daytime actual) × 100`. Secondary metrics: daytime MAE, RMSE, bias (`prediction - actual`), night MAE, folds and horizons. `total 24h MAE / mean daytime actual` is **not** daytime nMAE; it mixes night rows into the numerator.
- **Causality:** observations/context must stop at t0; forecast NWP must have issue time <=t0 and horizon-valid time; no future actual/NWP, no bfill across t0. Forward fill is permissible only from already available values. Satellite needs auditable publication time <=t0, not merely a valid time.
- **Promotion:** later routes use G1 aggregate improvement, G2 improved folds, G3 worst-fold degradation, G4 nMAE, G5 RMSE, G6 exact control reproduction. These gates are not retrospectively imposed on old exploration.

## 2. Experiment timeline and evidence

Each entry gives the strongest recoverable result. “Not recoverable” means no number is invented. ODD means the protected split was accessed.

### Foundations

**Seasonal Naive, raw Persistence, smart k_t Persistence.** Same 347-window target; 24h recurrence baselines, no training/NWP, causal at t0. Accepted baselines, not champions. Evidence: `clear_sky/run_347window_baseline.py`, baseline metrics and prediction CSVs. Confidence A.

**Chronos-2 (raw, k_t, multivariate, LoRA).** Pretrained time-series forecasts from target history and variants of clear-sky/context. Outputs establish these were evaluated, but no common governed promotion chain covers every LoRA run. Raw Chronos is historical baseline; other variants superseded/diagnostic. Confidence B (files), C (cross-run comparability).

**TimesFM / Moirai.** Alternate foundation-model attempts (`timesfm/`, `POLARIS_v0_1_moirai2_*`). TimesFM H12 error is 170.034984 W/m² in the project horizon summary, versus later Stage8.1 64.837218. Neither became champion. Rejected/superseded; confidence B.

### Stage 3

**Stage3A solar geometry.** Question: resolve deterministic diurnal structure with solar geometry/clear-sky features. Accepted component, causal, not champion. Evidence `stage3a_*`; confidence A.

**Stage3B cloud NWP.** Hypothesis: horizon-valid cloud forecast plus Chronos and geometry helps. `stage3b_cloud_nwp_predictions.csv` and script establish an upstream component of Stage4. Causal if the stated issued forecast selection holds. Historical accepted component; confidence B.

**Stage3C full NWP.** Broader NWP comparator (`stage3c_*`); did not displace 3B/Stage4. Rejected/superseded; confidence B.

### Stage 4

**Stage4 horizon-adaptive cloud-damped clear-sky ensemble.** Model: `max(0, w_h Chronos3B + (1-w_h) clearsky(1-k_h cloud_frac))`; `w_h,k_h` are fit per horizon on EVEN daytime rows. Evidence `stage4/METHODOLOGY.md`, pipeline, full predictions and parameters. Historical champion/component; ODD used; confidence A.

**Stage4.1 cloud-regime correction; Stage4.2 horizon-affine correction.** Hypothesis: systematic regime/horizon residual bias is calibratable. Outputs exist, but neither robustly improved raw Stage4. Rejected/superseded; no later gates retroactively claimed. Confidence B.

**Stage4.3 dynamic blending.** Learned blend / feature-importance experiment. ODD-era exploratory result without durable promotion. Rejected; confidence B.

**Stage4.4 hard-weather forensics.** Error association/classifier/oracle audit by horizon, cloud, solar geometry and disagreement. Diagnostic association—not forecast improvement. Confidence A.

**Stage4.4B hard-weather routing.** Oracle headroom did not translate into robust classifier routing; CV and ODD results retained. Rejected; ODD accessed; confidence B.

**Stage4.5 residual predictability; Stage4.6 causal residual audit.** Stage4.5 residual autocorrelation is confounded by overlapping forecast errors. Stage4.6 explicitly audits overlap/leakage and causal lag/context correction and finds little actionable causal residual signal. This is a correction from association to failed predictive test. Closed diagnostic route; confidence A.

### Stage 5

**Stage5.1 amplitude/volatility audit.** Error is associated with amplitude/volatility; calibration/correction did not establish a stable gain. Diagnostic/rejected predictive route; confidence A.

**Stage5.2 nonlinear Architecture A / champion audit.** Historical frozen-pipeline ODD control: **39.084821 W/m²**, 30.315107%, RMSE 68.993487, bias +1.934725. The 39.392734 value is a different pipeline that refitted Stage4 parameters. Historical champion/control; confidence A.

**Stage5.3 champion forensics.** Gain/horizon/cloud/volatility/residual analysis. Diagnostic evidence only; its “ceiling” language is hypothesis-level. Confidence A.

**Stage5.4 spatial NWP.** Early spatial feasibility, but no governed forecast improvement. Diagnostic precursor; confidence C.

### Stage 6

**Stage6.1 MEPS ensemble.** Spread/quantile information route; extraction, causality and fold artifacts exist. It did not beat Stage5.2. Rejected; confidence A.

**Stage6.2 satellite observations.** Swath/source extraction with latency/coverage causality audits; no promoted model. Feasibility/blocked, not a forecast improvement. Confidence A.

**Stage6.4 MEPS revision.** Revised extraction/information audit; no robust promotion. Rejected/superseded; confidence A.

**Stage6.5 snow/cloud.** Snow/cloud features failed to give robust improvement. Rejected; confidence A.

**Stage6.6 LWP/IWP.** Added causally extracted LWP/IWP/interactions. EVEN: control 39.423598, candidate **38.280605 W/m²**, nMAE 40.391805%, RMSE 60.750856; 4 improved folds, all then-defined gates pass. Authorized ODD: frozen Stage5.2 control 39.084821 versus candidate **37.005888**, nMAE 28.702638%, RMSE 65.671702, bias +1.144965, night 0; paired-origin bootstrap ΔMAE CI [-2.809838, -1.344760]. Historical new champion; confidence A. Causality is supported by its extraction/physics audits; its result must retain its own control chain.

### Stage 7

**Stage7.1 MEPS radiation feasibility.** Inventory/causality only; no eligible candidate. Feasibility; confidence A.

**Stage7.2 native MEPS radiation.** E1–E4 all rejected against Stage6.6 38.280605 EVEN control; ODD locked. Confidence A.

**Stage7.3 k_t reformulation.** E1 36.382758 versus 38.280605 but only 3/5 folds improve, worst degradation 1.701954, nMAE worsens. G1/G5 pass; G2/G3/G4 fail; ODD not accessed. Rejected; confidence A.

**Stage7.4 vertical cloud.** E1 38.286927 versus 38.280605; 3/5 improved, worst degradation 1.041087. All gates fail; ODD not accessed. Rejected; confidence A.

**Stage7.5 terrain/horizon.** DEM-horizon/terrain-adjusted clear-sky route. ODD candidate 36.613571 vs Stage6.6 37.005888, nMAE 28.398347, RMSE 65.347064; bootstrap CI [-0.791521, 0.001941] barely includes zero. Historical champion, but only borderline benefit; confidence B.

### Stage 8

**Stage8.0 / 8.10 model-level profiles.** MEPS vertical condensate is NWP-derived, not independent observation. Closed duplicate/model-derived route; confidence A.

**Stage8.1 700-hPa steering wind.** Initial EVEN development: 31-feature E0 38.280605 vs 37-feature E1 **37.620054** under per-fold dynamic Stage4 refit. Later frozen ODD reconstruction is the current champion in the executive result. Exact 37 features: time/solar/clear-sky, NWP cloud/T/RH, upstream predictions/disagreement, past-only observation variability, LWP/IWP, terrain horizon, and u700/v700. Champion; confidence A for frozen ODD, not for treating 37.620054 as ODD.

**Stage8.2 observability.** Independent causal-cloud-state feasibility negative; no candidate. Closed feasibility route; confidence B.

**Stage8.3 Abisko direct/diffuse.** Candidate 35.696286 vs frozen-pipeline Stage8.1 control 35.069059, +0.627227 and 4/5 folds degrade. Valid rejection; no ODD; confidence A.

**Stage8.4 / 8.14B VIIRS and external satellite.** Publication latency (3–8h; NRT 1–3h), polar-night fill, coverage/publication evidence failures. Operationally non-causal/blocked; confidence A.

**Stage8.5 spatial cloud/advection.** Spatial features/advection causally audited but did not improve; reported degradation is about +0.38 pp nMAE. Rejected. It does not imply spatial fields lack information. Confidence B.

**Stage8.6 CAMS.** AOD550/TCWV candidate 37.867306 vs 37.620054 (+0.247252), failed 4/6 gates. Rejected; confidence A.

**Stage8.7 DNI/two-head.** 49.445841 vs 37.620054 (+11.825787), 0/5 folds improved. Severe valid rejection; confidence A.

**Stage8.8 cloud radiative path/geometry.** Feasible NWP geometry proxies were redundant/non-improving. Rejected; confidence B.

**Stage8.9A independent cloud-state audit.** No independent causal source identified. Feasibility negative, not proof no observation could exist. Closed; confidence B.

**Stage8.11A LWP/IWP semantics.** Re-audits feature meaning/origin sampling/provenance; diagnostic correction, not a new gain. Confidence A.

**Stage8.16A/16B-1 uncertainty.** Feasibility identified uncertainty signals. sigma-LWP failed: 2/5 folds improved and worst-fold +1.3385 > +0.50. Rejected; confidence A.

**Stage8.16B-2 Phi inconsistency.** Later real-revalidation record has 44.718895 candidate vs 45.091280 control, a different reconstruction/control family. Conflicting control definitions make it non-comparable to current ODD. Conditional/superseded; confidence C.

**Stage8.17A AROME structural disagreement.** Historical report: 35.241085, 27.3337%, RMSE 63.290812, bias +1.810421. Later revalidation says NOT RECONSTRUCTABLE because raw AROME/extractor are missing. Historical champion only; confidence C for historical metrics, A for non-reconstructability.

**Stage8.19 ABIS/GNSS + AROME.** Claimed 34.821405 / 27.0081. Forensic files show synthetic `np.random.seed(819)` ZTD/AROME, hard-coded metrics after dynamic-control failure, and missing authoritative ODD table. **Invalid**, not merely rejected; confidence A.

### Phase 9 and 10

**Phase9 calendar/disagreement/NWP-cloud-volatility/complementarity.** Error-forensics and candidate-space study; checkpoint says no robust improvement. Diagnostic/closed predictive route; confidence B/C.

**Phase10 architecture audit (A BiGRU, B shared MLP, C disagreement-gated residual MLP).** Designed against a reconstructed EVEN control often called 26.3668. A/C have unreproduced G6 control; B’s apparent 26.0112 cannot be promoted absent exact control reproduction. Rejected/closed, no ODD promotion. These are failures of the tested designs, not all sequence architectures. Confidence B.

### Labels requested but not independently recoverable as distinct experiments

Recursive filename/content search found no standalone result, prediction table, script, or freeze artifact uniquely naming **Stage8.10A, Stage8.21A, Stage8.22, Stage8.23, Stage8.24, or Stage8.25**. They must therefore not be silently mapped to nearby Stage8 routes. Their status in this reconstruction is **inconclusive / not recoverable**, ODD unknown, confidence **D**. “Stage8.10” is recoverable only as the MEPS model-level-profile feasibility/duplicate route described above. The request’s cloud-advection, trajectory-consistency, state-aliasing, local-spatial-state, 21×21, topology-preserving, and 3×3 labels do have artifacts and are covered in sections 5–6.

## 3. Control-number ledger

- **39.084821:** Stage5.2 frozen-pipeline ODD daytime control. **39.392734/39.3927:** refitted-Stage4 control, a different pipeline, corrected.
- **38.280605:** Stage6.6 31-feature EVEN CV / legacy E0 used by Stage7 and early Stage8.
- **37.620054:** Stage8.1 37-feature development EVEN CV with dynamic per-fold Stage4 refitting.
- **35.069059:** Stage8.1 frozen-Stage4 `pred_ensemble` EVEN control used in Stage8.3 reconciliation; valid for that pipeline, not a universal ODD value.
- **44.718895:** later 8.16B-2 real-revalidation candidate/control family; changed setup, not an official benchmark decline.
- **26.3668:** reported Phase10 EVEN 24h control, no surviving authoritative model/prediction artifact; retired from exact reproducibility.
- **25.639318:** later reproducible REAL_AROME_21X21 *24h* EVEN MAE; its daytime MAE is **47.451469** (nMAE 36.8045%, RMSE 74.376601). Never compare it as daytime MAE.
- **24.7820:** independent forensic reconstruction, unexplained 1.58 better than 26.3668; not official.

## 4. Causality / leakage audit

Strengths: origin-level EVEN/ODD isolation, fold fitting, zero night forcing, later G6 checks. Weaknesses: historical Stage4 calibration scope drift; total/daytime metric conflation; absent raw later AROME/ABIS assets.

- Stage6.6 has no direct future-target-leakage evidence; its LWP/IWP causal claim rests on extraction/physics audits.
- Satellite valid time alone is insufficient; latency blocks several products.
- Stage8.17A fails current provenance/reproducibility, not proven leakage.
- Stage8.19 fails provenance outright and is invalid.
- Corrected aliasing diagnostics use EVEN-only scaling, t0 state, exclude model-derived outputs, and do not touch ODD. They are valid diagnostic—not predictive—studies.
- Any feature requiring future backfill is non-causal. The freeze permits past-derived fill only; historical outputs do not provide one universal fill log.

## 5. Spatial research: three distinct claims

1. **Spatial information exists:** AROME/MEPS grids and 21×21/local field audits establish structure. Feasibility evidence.
2. **Spatial information correlates with error:** cloud-motion/state diagnostics establish associations. Diagnostic evidence.
3. **Spatial information improves forecasts:** not established. Topology-preserving 21×21 candidate was 63.286275 vs 47.451469 daytime control; local 3×3 was 50.471940 vs 47.451469 (+3.020471). Both fail EVEN gates.

Simple cloud advection/trajectory consistency can be measured but mountain formation/dissipation breaks frozen-flow assumptions. Failure does not prove spatial information absent. The 3×3 representation is legitimately closed; reopen only with a new causal spatial observation or mechanism—not seeds/tuning.

## 6. Error and bottleneck evidence

- Errors are concentrated in daytime transitions/longer horizons. Stage8.1 H1 MAE is 4.049545; H12 is 64.837218 W/m². This is concentration, not a ceiling.
- State-to-trajectory audit (147 EVEN daytime origins): transition count, sign changes and cumulative |Δk_t| correlate with MAE (Pearson r ~0.50, 0.53, 0.54; permutation p≈0.0005). Complex H7–H12 trajectories: 80.67 vs 46.29 W/m². Strong diagnostic association, not a causal feature gain.
- Corrected causal aliasing calls itself **weak/inconclusive**, nearest-neighbour/random trajectory ratio ~0.52. Statements that aliasing is proven are corrected.

| Hypothesis | Classification | Evidence boundary |
|---|---|---|
| Transitions/volatility associate with error | SUPPORTED | residual/trajectory diagnostics |
| Tested features/models failed to robustly improve | PROVEN for the specified tests | governed CV/ODD records |
| Information/representation limits dominate capacity | PLAUSIBLE | confounded by representation/sample/control |
| State aliasing is the causal mechanism | INCONCLUSIVE | corrected audit below own threshold |
| Irreducible accuracy ceiling | UNSUPPORTED | no lower-bound experiment |

## 7. Closure and next-scope audit

Legitimately closed in their tested form: Stage6.1 ensemble summaries, Stage6.5 snow/cloud, Stage7.2 native radiation, Stage7.3 k_t, Stage7.4 vertical cloud, Stage8.3 Abisko radiation, Stage8.5 simple spatial/advection, Stage8.6 CAMS candidate, Stage8.7 two-head DNI, sigma-LWP, local 3×3, and Phase10 A/B/C. Conclusions remain narrow.

Blocked rather than empirically defeated: low-latency satellite sources, summit camera/ceilometer, distant ceilometer/radar/radiosonde routes, and unrecoverable AROME raw assets. Reopen only if a timestamped, sufficiently complete operational archive or new near-site measurement exists.

## 8. System-level POLARIS

MAE is not automatically the operating objective. The workspace establishes forecasting results but no end-to-end battery SOC, diesel, load-shifting, curtailment, or dispatch optimization result. Forecasting and energy management remain separate programs. The justified next direction is calibrated uncertainty and forecast-risk-aware dispatch: quantify asymmetric underprediction cost, propagate scenarios through battery/diesel/curtailment decisions, and measure operational value. That is distinct from another point-model sweep.

## Evidence index

Freeze/metrics: `POLARIS_REPRODUCIBLE_BASELINE_FREEZE.{md,json}`, `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`, `verify_prediction_metrics.py`, `POLARIS_INDEPENDENT_METRIC_VERIFICATION.json`, `POLARIS_ROUTE_REGISTRY.json`. Benchmark/early model: `data/`, `clear_sky/`, `stage3/`, `stage4/`. Stage5–8: `stage5/`, `stage6/`, `stage7/`, `stage7/stage8/`. Invalidation: `STAGE8_17A_REVALIDATION_AUDIT.json`, `STAGE8_19_INVALIDATION_AND_GOVERNANCE_CORRECTION.json`, `STAGE8_REAL_DATA_REVALIDATION_FINAL_REPORT.json`. Spatial/architecture: `spatial_arome_research/`, `PHASE10_*`, `POLARIS_CAUSAL_STATE_ALIASING_AUDIT.json`, `POLARIS_STATE_TO_TRAJECTORY_DYNAMICS_AUDIT.json`.

# CODEX INDEPENDENT VERDICT

1. **Current official champion:** Stage8.1 37-feature 700-hPa-wind HGB, the only current real, hash-verified ODD artifact.
2. **Strongest proven findings:** Stage8.1 ODD metrics; defined zero-night behavior; Stage6.6 historical LWP/IWP gain; failure of the specified governed k_t, vertical-cloud, DNI, CAMS, local-spatial and Phase10 candidates.
3. **Important corrected findings:** 8.19 invalid; 8.17A non-reconstructable; 39.3927 is not 39.084821; all-hour MAE/daytime mean is not nMAE; 26.3668/24.7820 unresolved.
4. **Weak/inconclusive hypotheses:** state aliasing, a broad information bottleneck, spatial/advection mechanism, irreducible ceiling, broad sequence-capacity claims.
5. **Invalid experiments:** Stage8.19 ABIS/GNSS + AROME claim.
6. **Legitimately closed routes:** the narrow tested routes listed in section 7.
7. **Possible reopenings:** only timestamped causal near-site cloud observations, a sufficiently complete low-latency archive, or a validated new mountain-cloud mechanism.
8. **Most important unresolved question:** what causal observation distinguishes rapidly changing summit cloud transmission before H7–H12 transition errors occur?
9. **Highest-value next action:** develop a causally timestamped uncertainty product for frozen Stage8.1 and evaluate its operational decision value.
10. **Strategic decision:** pause broad point-forecast search; prioritize uncertainty-aware energy optimization while retaining the frozen benchmark for genuinely new information-source tests.
