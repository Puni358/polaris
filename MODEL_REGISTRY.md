# POLARIS Model Registry

Every forecasting model trained or evaluated in POLARIS, in the order it was tried, with
where its code, saved model and results live, and why it was kept or dropped.

All paths are relative to the repository root. Metrics are **daytime MAE in W/m²** on
Nuolja station solar irradiance (SW_IN) unless noted. Splits:

- **2024-EVEN** origins: training. **2024-ODD** origins: validation.
- **2025**: blind test, run once with frozen models.
- A candidate "passes" only if the paired origin-level bootstrap 95% CI of its MAE gain is entirely below zero and bias does not get worse.

Long-form write-up: [`docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/ALL_FORECASTERS_COMPARED_compendium.md`](docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/ALL_FORECASTERS_COMPARED_compendium.md).

`ST` below means `forecasting/stage7/stage8/stage8_1_station_tuning_research/`.

---

## Status at a glance

| # | Model | Status | One-line reason |
|---|---|---|---|
| 1 | Seasonal naive 24 h | Reference | Yesterday-repeats baseline |
| 2 | TimesFM 3.0 (zero-shot) | Dropped | No weather inputs; carries clear-sky shapes into storms |
| 3 | Moirai 2.0 R-small (zero-shot) | Dropped | Worst foundation model (MAE 72 all-hours) |
| 4 | Chronos-2 (zero-shot, univariate / multivariate / k_t) | Dropped as forecaster, kept inside the Stage 4 baseline | Lags sudden overcast; blurs midday peaks |
| 5 | Chronos-2 LoRA fine-tunes (pilot, 500, 1000, expB, expC) | Dropped | ~46.5 daytime MAE, still behind the Stage 4 physics ensemble (43.4); no weather inputs |
| 6 | Stage 3a/3b/3c physics + NWP baselines | Superseded | Became inputs to Stage 4 |
| 7 | Stage 4 horizon-adaptive ensemble (Chronos + cloud-damped clear-sky) | **Kept as physical baseline** (clean re-fit) | Strong, simple, physically grounded |
| 8 | Stage 4.x residual corrections (5 variants) | Dropped | Every one made test MAE worse (+1.5 to +32) |
| 9 | Stage 5.2 non-linear architectures (A–D) | Arch A evolved into the GBDT line; B–D dropped | Arch A GBDT residual corrector beat Stage 4 (ODD 39.08 vs 43.45) |
| 10 | Stage 7.3 clear-sky index (k_t) target | Idea reused in N6 | Lower MAE, higher bias on its own |
| 11 | Stage 8.1 frozen control (37-feature HGB) | **Withdrawn** | Later audit found non-causal 00Z inputs and 2025 target leakage |
| 12 | Candidate B – more history | Infeasible | No clean third data year at the time |
| 13 | Candidate C – 4 horizon-bucket models | Failed | Too few samples per bucket |
| 14 | Candidate D – two-stage residual | Failed | Overfit 2024, flat on 2025 |
| 15 | Candidate E – 144-point grid search | Failed | Gain not significant; bias +32% |
| 16 | Phase 3 – solar-elevation sample weights | Failed | High-sun bias got worse |
| 17 | Candidate F – `elevation × cloud_frac` | Passed, then withdrawn with 8.1 lineage | Significant gain, but on leaky features |
| 18 | Candidate G – transition-cloud flag | Redundant | Did not beat F |
| 19 | Candidate H – quantile loss τ=0.35 | Failed | Bias swung to −10 |
| 20 | Candidate I – high-sun residual model | Failed | 489 training rows; overfit |
| 21 | Candidate J – F + `elevation × transition` | Passed, then withdrawn with 8.1 lineage | Best of the leaky lineage |
| 22 | Clean Successor v1 / **v2** (33 causal features) | Clean baseline | First fully causal model |
| 23 | **Candidate K** (35 features, baseline-conditioned residual) | Clean control | Significant gain over Successor v2 |
| 24 | Candidate L1–L3 (k_t + advection, τ=0.47, 1D-TCN) | Failed | None beat K |
| 25 | Candidate M (monotonic advection) | Not adopted | Script only, no saved result; superseded by Candidate N |
| 26 | Candidate N1 (36 features, one tree) | Hold | Gain over K not significant |
| 27 | **Candidate N6** (25+15 seed blend) | **PRODUCTION** | Only model significantly better than K on blind 2025 |
| 28 | L2 quantile models (q10/q50/q90) + conformal reserve | **In use for the battery reserve** | Heavy-tailed, autocorrelated errors need distribution-free bounds |
| 29 | Branch-01 HGB / Ridge | Infrastructure test | Pipeline / governance validation, not a science result |
| 30 | Wind ARX forecaster | In use | Wind input to the EMS |

---

## 1. Foundation time-series models (zero-shot / LoRA)

All-hours and daytime MAE over 347 rolling 24 h windows of 2024
([`forecasting/foundation_models/final_model_comparison/final_leaderboard.csv`](forecasting/foundation_models/final_model_comparison/final_leaderboard.csv)):

| Model | All-hours MAE | Daytime MAE | Daytime RMSE |
|---|---:|---:|---:|
| Chronos-2 | 36.59 | 54.01 | 96.73 |
| Seasonal naive 24 h | 37.19 | 55.10 | 103.62 |
| TimesFM 3.0 | 58.25 | 86.17 | 150.11 |
| Moirai 2.0 R-small | 72.26 | 106.56 | 179.96 |

| Model | Scripts | Results |
|---|---|---|
| TimesFM 3.0 | `forecasting/foundation_models/timesfm/run_timesfm_benchmark.py`, `score_timesfm.py`, `analyze_*` | `forecasting/foundation_models/results/POLARIS_v0_1_timesfm3_*.csv`, `forecasting/foundation_models/plots/timesfm_forecast_plots/` |
| Moirai 2.0 | `forecasting/foundation_models/moirai/run_moirai_benchmark.py`, `score_moirai.py`, `final_model_comparison.py` | `forecasting/foundation_models/results/POLARIS_v0_1_moirai2_predictions.csv`, `forecasting/foundation_models/moirai_analysis/`, `forecasting/foundation_models/plots/moirai_forecast_plots/` |
| Chronos-2 zero-shot | `forecasting/foundation_models/chronos/run_chronos_benchmark.py`, `run_chronos_multivariate_benchmark.py`, `score_chronos.py` | `forecasting/foundation_models/results/POLARIS_v0_1_chronos2_*.csv` (incl. `_multivariate_`, `_kt_`), `forecasting/foundation_models/plots/chronos_forecast_plots/`, `forecasting/foundation_models/results/POLARIS_chronos2_*.png` |
| Chronos-2 LoRA | `forecasting/foundation_models/chronos/polaris_chronos2_lora_{pilot,500,1000,expB,expC}.py`, `evaluate_chronos2_lora_*.py` | **Saved adapters:** `forecasting/foundation_models/chronos/polaris_lora_*/finetuned-ckpt/adapter_model.safetensors` (+ intermediate checkpoints) |
| Side-by-side | `forecasting/foundation_models/moirai/final_model_comparison.py` | `forecasting/foundation_models/final_model_comparison/` (leaderboard, horizon and regime plots) |

**Why dropped:** none of them use weather-model forecasts. TimesFM and Moirai repeat
clear-sky shapes into Arctic storm fronts. Chronos-2 was best, but it lags behind sudden
overcast, and multivariate conditioning blurred midday peaks. LoRA fine-tuning did not
fix that: the fine-tunes reached about 46.5 daytime MAE (Nov–Dec held-out windows), still behind the
Stage 4 physics ensemble. Chronos survives only as one input of the Stage 4 baseline.

## 2. Physics baselines and the Stage 4 ensemble

| Model | Code | Results |
|---|---|---|
| Stage 3a solar geometry (Ineichen clear-sky) | `forecasting/stage3/run_stage3_experiments.py` | `forecasting/stage3/stage3a_*.csv` |
| Stage 3b Chronos-2 + cloud NWP (~46.5) | `forecasting/stage3/run_stage3_experiments.py`, `run_stage3b_2025.py` | `forecasting/stage3/stage3b_*`, `forecasting/stage3/stage3b_2025/` |
| Stage 3c full NWP | `forecasting/stage3/run_stage3_experiments.py` | `forecasting/stage3/stage3c_*.csv`, `stage3_model_comparison.csv` |
| **Stage 4 ensemble** `max(0, w_h·Chronos + (1−w_h)·GHI_cs·(1−k_h·cloud))` | `forecasting/stage4/run_stage4_pipeline.py`, `run_stage4_pipeline_2025.py` | `forecasting/stage4/stage4_results/`, `forecasting/stage4/stage4_results_2025/`, `forecasting/stage4/METHODOLOGY.md` |
| Stage 4.1–4.6 residual corrections (global ridge, horizon affine, regime affine, physics-interaction ridge, isotonic, hard-weather routing, dynamic blending) | `forecasting/stage4/stage4_{1..6}*/` | each folder's report |

**Stage 4 status:** kept. Its clean re-fit on 2024-EVEN only is the "clean physical
baseline" (ODD 43.43, blind 2025 41.77) that Candidates K and N6 correct.
**Stage 4.x corrections dropped:** each one made test MAE worse by +1.5 to +32,
because they learned quirks of the training days.

## 3. Feature-expansion research (Stages 5–7)

| Stage | Folder | Outcome |
|---|---|---|
| 5.1–5.4 amplitude audit, champion forensics, **non-linear architectures**, spatial NWP (3×3, 21×21) | `forecasting/stage5/` | 5.2: Arch A (GBDT residual corrector) beat Stage 4 on ODD, 39.08 vs 43.45, CI −5.56…−3.10, and became the starting point for the HGB models below; Archs B–D (blend delta, volatility specialists, stacked meta-learner) were weaker and dropped (`forecasting/stage5/stage5_2_nonlinear_architecture/final_summary.txt`). Coarse grids miss the local terrain cloud trapping. |
| 6.1 MEPS ensemble, 6.2 satellite, 6.4 MEPS revision, 6.5 snow/cloud, 6.6 LWP/IWP | `forecasting/stage6/` | LWP/IWP and snow flags adopted as features |
| 7.1–7.2 MEPS radiation, 7.3 **k_t target reformulation**, 7.4 vertical cloud, 7.5 **terrain horizon** | `forecasting/stage7/stage7_*` | Terrain shading (from the Copernicus DEM) and 700 hPa wind adopted. k_t: MAE −1.9 but bias +4.8 (`forecasting/stage7/stage7_3_kt_reformulation/stage7_3_decision.json`); later reused as the N6 specialist. |
| 8.0–8.16 feasibility studies (model levels, CAMS, VIIRS, DNI two-head, independent cloud, NWP uncertainty) | `forecasting/stage7/stage8/stage8_*`, `STAGE8_*.md` | Mostly closed as infeasible or no gain; see each `*_CLOSED`/`*_AUDIT` file |

## 4. Stage 8.1 lineage — Candidates A to J (withdrawn)

Model: `HistGradientBoostingRegressor(loss="absolute_error", max_depth=4, min_samples_leaf=30, l2_regularization=10)`.
Saved models: `ST/model_artifacts/candidate*.joblib`, `forecasting/stage7/stage8/stage8_1_corrected_2025/model_artifact/`, `forecasting/stage7/stage8/stage8_1_700hpa_wind/model_artifact/`.

| Candidate | Script | Report / results | ODD MAE (bias) | Blind 2025 MAE (bias) | Verdict |
|---|---|---|---|---|---|
| A – Stage 8.1 control (37 features) | `ST/phase2_train_candidates.py` | `ST/CANDIDATE_COMPARISON_REPORT.md` | 36.20 (+0.96) | 35.97 (+4.08) | Control |
| B – multi-year history | — | `ST/CANDIDATE_COMPARISON_REPORT.md` | — | — | Infeasible |
| C – 4 horizon buckets | `ST/phase2_train_candidates.py` | `ST/CANDIDATE_RESULTS.json` | 36.20 | 36.38 (+5.10) | Failed: sample starvation |
| D – two-stage OOF residual | `ST/phase2_train_candidates.py` | `ST/CANDIDATE_RESULTS.json` | 35.53 | 36.07 | Failed: overfit 2024 |
| E – 144-point grid | `ST/phase2_train_candidates.py` | `ST/CANDIDATE_RESULTS.json` | 34.63 | 35.79 (+5.37) | Failed: CI spans 0, bias +32% |
| Phase 3 – elevation weights | `ST/phase3_weight_experiment.py` | `ST/WEIGHT_EXPERIMENT_RESULTS.json` | 35.49 | 35.86 | Failed: high-sun bias +19.95 |
| F – `elevation × cloud_frac` | `ST/phase2_candidateF_additive_feature.py` | `ST/CANDIDATE_F_REPORT.md`, `CANDIDATE_F_RESULTS.json` | 35.44 | 35.49 | Passed (CI −0.80…−0.15) |
| G – transition flag | `ST/phase6_candidateG_transition_indicator.py` | `ST/CANDIDATE_G_REPORT.md` | 35.41 | 35.54 | Redundant |
| H – pinball τ=0.35 | `ST/phase7_candidateH_asymmetric_quantile_loss.py` | `ST/CANDIDATE_H_REPORT.md` | 36.45 (−9.80) | 36.32 (−10.33) | Failed: bias overshoot |
| I – high-sun residual | `ST/phase8_candidateI_targeted_high_elevation_residual.py` | `ST/CANDIDATE_I_REPORT.md` | 35.42 | 35.52 | Failed: n=489 overfit |
| J – F + `elevation × transition` | `ST/phase10_candidateJ_training.py` | `ST/CANDIDATE_J_REPORT.md`, `CANDIDATE_J_PRE_EMS_AUDIT.md` | 35.30 | 35.30 | Passed (CI vs F −0.35…−0.04) |

**Why the whole lineage was withdrawn:** the October 2026 audit
(`ST/TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md`) found two problems:

1. `lwp_latest` / `iwp_latest` came from the **00Z MEPS run**, which is not published until about 02:15 UTC, so it is not available at the 00:00 decision time.
2. The four Stage 4 derived features for 2025 used ensemble weights fitted on **2025 actuals**, which leaks the target into the "blind" test.

The ideas that worked (the `elevation × cloud` and `elevation × transition` interactions) were carried into the clean rebuild.
Historical replay of F on 2020–2023: `forecasting/candidate_L_research/`, `forecasting/reports/candidates/CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md`.

## 5. Clean causal lineage — Successor, K, L, M, N (current)

The leaky features were removed. Cloud microphysics now come from the previous day's
**18Z MEPS run** (lead = 5 + h).

| Model | Training script | Saved model | Results | ODD MAE (bias) | Blind 2025 MAE (bias) | Verdict |
|---|---|---|---|---|---|---|
| Clean Stage 4 baseline | `ST/candidate_f_successor_18z/build_clean_stage4_baseline.py` | parameters in folder | `ST/candidate_f_successor_18z/` | 43.43 (−2.35) | 41.77 (−7.15) | Physical baseline |
| Successor v2 (33 features) | `ST/candidate_f_successor_18z/train_successor_v2.py` | `ST/candidate_f_successor_18z/artifacts_v2/candidate_f_successor_v2_model.joblib` | `SUCCESSOR_MODEL_MANIFEST.json` | 38.77 (+1.66) | 38.19 (−2.20) | Clean baseline |
| **K** (35 features, residual on clean baseline) | `ST/candidate_k_baseline_conditioning/train_candidate_k.py` | `ST/candidate_k_baseline_conditioning/artifacts/candidate_k_model.joblib` | `CANDIDATE_K_MANIFEST.json`, `docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/Candidate_K_experiment_report.md` | 37.72 (+0.11) | 37.46 (−4.00) | Clean control |
| L1 GBDT k_t + advection / L2 k_t τ=0.47 / L3 1D-TCN | `ST/candidate_l_kt_advection/run_candidate_l_experiment.py` | — | `CANDIDATE_L_VALIDATION_REPORT.json` | 38.04 / 37.99 / 38.94 | — | Failed: none beat K on ODD |
| M – monotonic advection | `ST/candidate_m_monotonic_advection/run_candidate_m_experiment.py` | — | none saved | — | — | Not adopted; superseded by N |
| N1 (36 features, one tree) | `ST/candidate_n_additive_physics/run_candidate_n_experiment.py` | `ST/candidate_n_additive_physics/artifacts/candidate_n1_model.joblib` | `artifacts/CANDIDATE_N_MANIFEST.json` | 37.46 (+0.04) | 37.27 (−3.87) | Hold: CI vs K −0.49…+0.10 |
| **N6** (25-seed additive + 15-seed k_t, elevation-ramped blend) | `ST/candidate_n_additive_physics/run_candidate_n_experiment.py`, `export_artifacts.py` | `ST/candidate_n_additive_physics/artifacts/candidate_n6_model.joblib` | `artifacts/BLIND_2025_RESULTS.json`, `blind_2025_predictions.csv`, `validation_predictions.csv` | **37.20 (+0.37)** | **36.79 (−2.99)** | **Production**: CI vs K −1.10…−0.28 |

Blind test script: `ST/candidate_n_additive_physics/evaluate_2025_blind_oneshot.py`.
Gate report: `docs/POLARIS_JUDGE_PACK/11_REPORTS_and_proofs/N6_gates_and_blind_test_report.md`.
Runtime engine: `system/forecasting/implementations/n6_solar.py`.
N6 remediation history: `forecasting/n6/remediation_reports/`.

Training data used by this lineage (committed):
`ST/candidate_f_successor_18z/dataset_v2/{train,validation,blind,split_manifest}.csv` and
`ST/candidate_k_baseline_conditioning/candidate_k_2024_clean_matrix.parquet`.

## 6. Uncertainty models and the battery reserve (L2)

Folder: `ST/L2_uncertainty_aware_forecasting/` (also linked at `forecasting/audits/`).

- **Quantile GBDTs** q10 / q50 / q90: `models/l2_exp_02_skgbdt_q{10,50,90}.joblib`.
- **AR(1) error model**: φ = 0.64, but innovations are heavy-tailed (excess kurtosis 3.4) and Ljung-Box rejects white noise, so a Gaussian reserve would be too small. See `forecasting/reports/uncertainty/AR1_UNCERTAINTY_MODEL_VALIDATION.md`, `forecasting/reports/uncertainty/FORECAST_ERROR_TRAJECTORY_AUDIT.md`, `forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md`.
- **Conformal 90% bound → battery reserve vector** fed to the optimizer: `ST/candidate_n_additive_physics/evaluate_l2_conformal_ebr_2025.py`.
- Risk-aware EMS experiments: `experiments/L2_EXP_10_RISK_AWARE_MULTI_SCENARIO/`, `L2_EXP_11_ADAPTIVE_Q_NN/`, `L2_EXP_12_HORIZON_RISK_BUDGET/`.

## 7. Other trained models

| Model | Where | Purpose / status |
|---|---|---|
| Branch-01 Candidate A HGB, Candidate B Ridge | `artifacts/model_runs/RUN_BRANCH01_*` (model, scaler, predictions); code in `forecasting/solar_branch_01/` | Governed-pipeline validation runs; campaigns in `POLARIS_BRANCH01_*` folders |
| Topology-preserving AROME candidate | `scripts/forecasting_research/train_topology_preserving_arome_candidate.py`, `run_real_arome_21x21_*.py` | 21×21 AROME spatial experiment (needs the AROME cache; see DATASET.md) |
| Candidate 2 forecast-content ablation | `forecasting/CANDIDATE2_FORECAST_CONTENT_ABLATION/` | Which forecast content matters to the EMS |
| Candidate S (SW safety campaign) | `experiments/candidate_s_sw_campaign_2024/` | EMS-level test; 123-origin safety gate |
| Wind ARX | `system/forecasting/implementations/wind_arx.py`, `research/wind_a2`, `research/wind_a3` | Wind forecast for the EMS |

## 8. Optimizers / controllers (not trained, but compared)

| Controller | Code | Status |
|---|---|---|
| Reactive hybrid A2 (no forecast) | `system/optimization/implementations/reactive_hybrid_a2.py` | Comparison baseline |
| Rule-based | `system/optimization/implementations/rule_based.py` | Early baseline |
| Generic MILP | `system/optimization/implementations/milp.py` | Superseded by GAP19 |
| **GAP19 HiGHS lexicographic J1–J4** | `system/optimization/implementations/gap19_highs_native.py` | **Production** |
| GAP19 MILP v2 (research) | `gap19_highs_native_milp_v2_research.py`, `ems/gap19/POLARIS_EMS_GAP19_MILP_V2_DIAGNOSTIC_BRANCH/` | Research branch |
| Option D diesel floor | `option_d.py` | Adopted repair (see decision register) |

Full-year comparison of forecasters under the same optimizer: `dashboard/public/data/trace/cand_*`
and `docs/POLARIS_JUDGE_PACK/09_RESULTS_data/`.

---

## Lessons that held up

- **Does not work:** splitting data into horizon or elevation buckets; unconstrained second-stage residual models; global loss asymmetry or sample weighting; hard on/off regime flags.
- **Works:** smooth physical interaction features (elevation × cloud); conditioning the tree on a clean physical baseline and predicting the residual; seed bagging; truly blind calendar-year tests with origin-level bootstrap CIs.
