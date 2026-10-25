# POLARIS L2 Uncertainty-Aware Forecasting — First Experiment Design Specification

**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Date**: October 4, 2026  
**Status**: PROPOSED EXPERIMENT DESIGN SPECIFICATION (RESEARCH-ONLY), REVISED PRE-TRAINING  
**Target Station**: Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l.)  
**Governance Status**: LOCKED — Design specification only. No training or experiment executed in this step.

---

## DESIGN REVISION — PRE-TRAINING

This revision makes L2-EXP-01 scientifically cleaner before any training. No training, fitting, or experiment was run. Frozen artifacts, F, GAP19, and production code are unchanged; no hashes or data splits were altered.

**What changed and why:**

1. **Training, calibration, and blind evaluation are now explicitly separated (§5, §8, §9).** The earlier text listed "conformal calibration" inside the Validation role without stating the order of operations. The pipeline is now: TRAIN 2020–2021 fits the quantile model only; VALIDATION 2022 tunes only the permitted hyperparameters and fits post-hoc calibration, then freezes the full specification; BLIND Jan–Sep 2023 is a single untouched evaluation of the frozen, calibrated model. Raw quantile outputs are no longer called "calibrated."
2. **The first model is minimized (§6).** BatchNorm and the second dropout layer were removed. The architecture is now a small 2-hidden-layer MLP with no normalization layers and a single dropout-free configuration, trained with the pinball objective. Architecture search is explicitly out of scope.
3. **The output chain is distinguished (§2, §7).** Raw model quantile offsets, calibrated quantiles, and the final physically bounded output are three separately named stages. The residual-quantile formulation is retained; F point predictions are unchanged.
4. **The Winkler 10%-improvement hard gate is removed (§9).** Qualification now rests on nominal coverage/calibration on Validation and Blind, with horizon and regime coverage examined. Sharpness (MPIW, Winkler) is a secondary quality criterion, assessed against empirical residual baselines in a calibration-versus-sharpness framing, so a model cannot pass merely by widening intervals.
5. **Ambiguous specifications are marked as design decisions requiring approval (§12).** Values not justified by the existing record (e.g., the 1.25× GHI bound, the coverage tolerance band, learning-rate/weight-decay/patience values, cloud-regime thresholds) are no longer presented as settled.
6. **New blocking issues surfaced and flagged, not silently resolved (§12).** Provenance of the 2020–2023 station context features and target, and the validity status of the frozen 2020–2023 F prediction artifact, must be confirmed before training. Both are recorded as unresolved.

**Preserved unchanged:** F frozen; GAP19 unchanged; 2024 quarantined; no L2 output supplied to GAP19 in L2-EXP-01; exact input hashes (§10); temporal TRAIN/VALIDATION/BLIND split (§5); causal lag-1 residual history only.

---

## 1. Experiment Objective

The primary objective of L2-EXP-01 (**Quantile Residual Network**) is to:
1. Construct a minimal, low-capacity uncertainty model that learns conditional prediction intervals around frozen Candidate F point forecasts.
2. Ingest only causal, forecast-time inputs, including lag-1 completed-origin residual statistics.
3. Establish whether an uncertainty layer can achieve calibrated nominal coverage (80% interval; 10th–90th percentile) with useful sharpness relative to empirical residual baselines across solar regimes.
4. Evaluate once, untouched, on the 2023 Blind Test, after freezing the specification on the 2022 Validation set. Candidate F and GAP19 are not modified.

The first experiment is designed to answer whether uncertainty modelling works at all, not to optimize neural architecture.

---

## 2. Formulation and Output Chain

```
Causal inputs X_t (§3)
   |
   v
Small quantile MLP (§6) --> RAW residual quantile offsets [dq_10, dq_50, dq_90]     (stage A: raw model output)
   |
   v
Calibration (fit on VALIDATION 2022 only, §5) --> CALIBRATED offsets [dq'_10, dq'_50, dq'_90]   (stage B)
   |
   v
Physical bounding (§2.1) --> FINAL bounded interval [q_10, q_50, q_90]               (stage C: deliverable)
   |
   Candidate F point forecast y_hat_F is added to offsets and is NEVER modified.
```

**Stage A — raw quantile offsets.** Direct network outputs. Not calibrated and not used for any claim of coverage.

**Stage B — calibrated offsets.** Raw offsets after post-hoc calibration fitted on the 2022 Validation set only (see §5). Only these may be described as calibrated.

**Stage C — final bounded output.** Stage B offsets added to the frozen F point forecast, then bounded per §2.1. This is the only artifact released for evaluation.

Target formulation is retained: the model predicts residual quantile offsets around the F point forecast, so that solar prediction intervals are `y_hat_F + dq`, followed by bounding.

### 2.1 Physical bounding (stage C)

1. Night zeroing: if `solar_elevation <= 0`, all three outputs are set to 0.0 W/m².
2. Non-crossing: sort the three values so that `q_10 <= q_50 <= q_90`. Count pre-sort crossings for the diagnostic in §8.
3. Clamping: `q = max(0, min(U, y_hat_F + dq))`, where U is the upper physical bound. The value of U is an unresolved design decision (§12); the earlier value `1.25 × clearsky_ghi` is not justified by the existing record and is not adopted as a settled value.

---

## 3. Inputs

Twelve causal, forecast-time features, available at forecast issuance `t_0` (or ending strictly before `t_0`):

| # | Feature | Description | Source | Causality |
|---|---|---|---|---|
| 1 | `pred_candidate_F_total` | Frozen Candidate F point prediction ($\hat{y}_F$) | `candidateF_elevation_x_cloud.joblib` | Computed at $t_0$ |
| 2 | `solar_elevation` | Solar elevation (deg) | Deterministic astronomy | Exact for target $t$ |
| 3 | `clearsky_ghi` | Clear-sky GHI ($W/m^2$) | Deterministic geometry | Exact for target $t$ |
| 4 | `horizon_hour` | Lead time $h \in [1..24]$ | Origin-to-target offset | Known at $t_0$ |
| 5 | `fc_cloud_cover` | MEPS cloud cover (0–100%) | MET Norway MEPS 18Z | Initialized at $t_0 - 6$h |
| 6 | `cloud_frac` | MEPS cloud fraction (0–1) | MEPS 18Z | Initialized at $t_0 - 6$h |
| 7 | `elevation_x_cloud_frac` | $\theta \times c_f$ | Derived | Known at $t_0$ |
| 8 | `ctx_last_obs` | Last observed $SW_{IN}$ at $t_0 - 1$h | Station pyranometer | **Provenance unresolved for 2020–2023 (§12, U-1)** |
| 9 | `ctx_std_3h` | Observation std over $[t_0-3\text{h}, t_0-1\text{h}]$ | Station pyranometer | **Provenance unresolved for 2020–2023 (§12, U-1)** |
| 10 | `ctx_mean_24h` | Observation mean over $[t_0-24\text{h}, t_0-1\text{h}]$ | Station pyranometer | **Provenance unresolved for 2020–2023 (§12, U-1)** |
| 11 | `lag1_origin_mean_residual` | Daytime mean residual of completed origin $n-1$ | Origin $n-1$ residuals | Concluded before $t_0$; lag-1 only |
| 12 | `lag1_origin_daytime_mae` | Daytime MAE of completed origin $n-1$ | Origin $n-1$ residuals | Concluded before $t_0$; lag-1 only |

No feature may use origin $n$ or any later origin's residuals, actuals, or outcomes.

---

## 4. Target

- **Ground truth**: `actual` ($SW_{IN}$, $W/m^2$). Provenance for 2020–2023 is unresolved (§12, U-1).
- **Quantile targets**: $\tau \in \{0.10, 0.50, 0.90\}$, expressed on residuals relative to $\hat{y}_F$.
- **Nominal interval**: 80%, $I_{0.80}(t) = [\hat{q}_{0.10}(t), \hat{q}_{0.90}(t)]$.
- **Loss**: multi-quantile pinball loss averaged over the three $\tau$ values:
  $$\mathcal{L} = \frac{1}{N}\sum_{i}\sum_{\tau\in\{0.10,0.50,0.90\}} \max\big(\tau(y_i-\hat{q}_{\tau,i}),\,(\tau-1)(y_i-\hat{q}_{\tau,i})\big)$$

---

## 5. Split, Calibration Pipeline, and Blind Protocol

| Partition | Date range (UTC) | Rows | Daytime rows | Origins | Permitted use |
|---|---|---|---|---|---|
| **TRAIN** | 2020-01-01 00:00 – 2021-12-31 23:00 | 13,889 | 9,052 | 730 | **Fit the quantile model weights only.** |
| **VALIDATION** | 2022-01-01 00:00 – 2022-12-31 23:00 | 6,935 | 4,528 | 365 | **(a)** Tune the permitted hyperparameters (§6.2). **(b)** Fit post-hoc calibration (stage B). **(c)** Freeze the complete specification. |
| **BLIND** | 2023-01-01 00:00 – 2023-09-30 23:00 | 5,187 | 3,466 | 274 | **Single untouched evaluation** of the frozen, calibrated model. No calibration, fitting, threshold setting, or model selection. |

Quarantine: calendar year 2024 is not accessed.

**Order of operations (binding):**
1. Fit weights on TRAIN only.
2. On VALIDATION only: select permitted hyperparameters and early-stopping epoch; fit the calibration map; freeze everything (weights, calibration map, bounding rule, output schema).
3. Only after freeze, run the BLIND evaluation once, producing the metrics in §8. Any change after this point invalidates the blind result and requires a new blind partition, not a re-run.

**Validation coverage is a calibration diagnostic, not a qualification result**, because the calibration map was fitted on the same Validation data. Qualification relies on Blind coverage (§9).

---

## 6. Model Class and Architecture (minimal)

### 6.1 Fixed architecture

- Input: 12 standardized continuous features. Standardization statistics are fitted on TRAIN only.
- Hidden 1: 32 units, ReLU.
- Hidden 2: 16 units, ReLU.
- Output: 3 linear units $[\delta q_{0.10}, \delta q_{0.50}, \delta q_{0.90}]$ (stage A).
- Excluded by design: BatchNorm (unnecessary for a small MLP on standardized inputs; adds train/eval discrepancy), Dropout (unnecessary at this capacity; the parameter-to-sample ratio is already low). Any regularization change requires a documented justification and approval (§12).
- Parameter count: approximately 1,000. Stated as a low-capacity target, not a claimed guarantee against overfitting.

### 6.2 Training and tuning

- Loss: pinball (§4). Optimizer: AdamW.
- Learning rate, weight decay, batch size, maximum epochs: fixed pre-training values, not tuned. Proposed values are retained from the prior draft (lr 1e-3, weight decay 1e-4) and are **DESIGN DECISIONS REQUIRING APPROVAL** (§12, D-3).
- **Only permitted validation-tuned hyperparameter: the early-stopping epoch**, selected on VALIDATION 2022 pinball loss, patience fixed at a value requiring approval (§12, D-3).
- No architecture search. No hyperparameter search beyond the epoch selection above.

### 6.3 Baselines (no training required beyond counting)

- **Benchmark 0 (static empirical residual quantiles)**: unconditional 10th, 50th, and 90th percentiles of TRAIN daytime residuals, applied to all rows.
- **Benchmark 1 (regime-stratified empirical quantiles)**: the same percentiles stratified by cloud regime, with regime thresholds from §12 (D-5), computed on TRAIN only.

Baselines are fitted on TRAIN only and are evaluated on the same VALIDATION and BLIND partitions.

---

## 7. Output Format

Every target row $(n, h)$ carries all three stages, so calibration effects are auditable:

- `raw_dq_10`, `raw_dq_50`, `raw_dq_90` — stage A offsets (W/m²).
- `cal_dq_10`, `cal_dq_50`, `cal_dq_90` — stage B calibrated offsets (W/m²).
- `l2_q10`, `l2_q50`, `l2_q90` — stage C final bounded outputs (W/m²).
- `l2_interval_width` = `l2_q90 − l2_q10`.
- `pred_candidate_F_total` — unchanged frozen F point forecast.
- `split` — TRAIN, VALIDATION, or BLIND.

Output path: `results/L2_EXP_01_PREDICTIONS_2020_2023.csv`.

---

## 8. Evaluation Metrics

Computed on VALIDATION (diagnostic) and BLIND (qualification), for final (stage C) outputs unless stated:

1. **PICP** — fraction of targets in $[l_{10}, l_{90}]$.
2. **MPIW** — mean of $l_{90}-l_{10}$ (sharpness).
3. **Winkler score** (80% interval, $\alpha=0.20$): $S = (u-l) + \frac{2}{\alpha}(l-y)\mathbb{I}(y<l) + \frac{2}{\alpha}(y-u)\mathbb{I}(y>u)$.
4. **Quantile crossing frequency**: fraction of rows where raw stage-A quantiles cross before sorting. Diagnostic; must be reported. The prior draft's `< 1.0%` threshold is a design decision (§12, D-6).
5. **Coverage by sub-slice**:
   - Horizon blocks: $h \in [1..6], [7..12], [13..18], [19..24]$.
   - Solar elevation: low sun $0^\circ < \theta \le 15^\circ$; high sun $\theta > 15^\circ$.
   - Cloud regime: boundaries per §12 (D-5).
6. **Baseline comparison**: MPIW and Winkler for L2 versus Benchmarks 0 and 1 on the same partition.

---

## 9. Qualification: Calibration-vs-Sharpness Assessment

The earlier hard gate ("Winkler ≥10% better than Benchmark 0") is **removed**. It is an arbitrary threshold without a stated basis, and it rewards width-insensitive scoring trade-offs in ways that do not reflect calibration quality.

**Primary qualification (both required):**
- **P1 — Nominal calibration on BLIND**: PICP reported with its binomial uncertainty. Pass tolerance is a design decision (§12, D-4); the prior draft's 78–84% band is retained as a candidate pending approval.
- **P2 — Nominal calibration on VALIDATION**: same criterion, as a consistency check (not an independent test, since calibration used this data).
- **P3 — Horizon and regime coverage**: coverage must be examined by horizon block and cloud regime on BLIND. Tolerances and pass criteria are design decisions (§12, D-4).
- **P4 — Physical consistency** (§9.1) on 100% of rows.
- **P5 — Point-forecast invariance** (§9.1) on 100% of rows.

**Secondary quality (reported, not a pass/fail gate by itself):**
- **S1 — Sharpness**: MPIW relative to Benchmarks 0 and 1, reported on BLIND.
- **S2 — Winkler score**: relative to Benchmarks 0 and 1, reported on BLIND.
- **S3 — Calibration-vs-sharpness interpretation**: a model must achieve nominal coverage (P1–P3) before its sharpness is credited. Narrower intervals that fail coverage do not qualify. Wider intervals that meet coverage, without a sharpness advantage over baselines, do not qualify as an improvement.

A model cannot pass merely by producing very wide intervals, because P1–P3 cap width from above through coverage *and* S1–S3 show whether width is informative.

### 9.1 Physical and invariance checks (hard)

- Night rows: interval width = 0.0 W/m²; all outputs = 0.0.
- Lower bound ≥ 0.0 on all rows.
- Upper bound ≤ U on all rows, where U is pending approval (§12, D-2).
- Candidate F point predictions identical to the frozen artifact within $10^{-5}$ W/m² on 100% of rows.

---

## 10. Required Provenance and Input Hashes

All inputs must match these SHA256 values exactly:

```json
{
  "frozen_f_model": {
    "path": "stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib",
    "sha256": "e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84"
  },
  "exact_2020_2023_f_38_feature_matrix": {
    "path": "candidate_L_research/CANDIDATE_L2_EXACT_38_FEATURE_MATRIX_2020_2023.csv",
    "sha256": "bb5700c9dc8aa1a81c3007717eb21fb0385aac97937f2b12940d3f99e569edde"
  },
  "exact_frozen_f_predictions_2020_2023": {
    "path": "candidate_L_research/CANDIDATE_L2_EXACT_FROZEN_F_PREDICTIONS_2020_2023.csv",
    "sha256": "b3e2044bb07e860189cf7eea1cbf239b43c621c4fc876801aa2bad59bf7694a0"
  },
  "historical_f_residual_dataset": {
    "path": "candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv",
    "sha256": "1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab"
  }
}
```

**Note (unresolved, §12, U-2):** the frozen 2020–2023 F prediction artifact above was produced with context-feature substitutions that a prior audit classified as invalid for F residual evaluation. Its hash is recorded here as required by the existing specification, not as an endorsement of its validity. Hashes are not changed by this revision.

---

## 11. Governance Boundaries

1. **Candidate F** remains the sole active control model. Weights, point predictions, and artifacts are frozen and not fine-tuned, retrained, or altered.
2. **GAP19** is unchanged. No code under `system/optimization/` or `gap19_highs_native.py` is modified. **No L2 output is supplied to the MILP in L2-EXP-01.**
3. **Quarantine**: calendar year 2024 data and EMS replay frameworks remain locked.
4. **Causality**: lag-1 completed-origin residuals only; no same-origin or future residuals.
5. **Execution protocol**: any future training script must be placed in `experiments/` in this workspace, log full provenance manifests, and write metrics for all three output stages.
6. **Blind discipline**: the 2023 Blind partition is evaluated exactly once after freeze (§5). Any post-blind change requires a new specification revision and a new blind partition.

---

## 12. Unresolved Design Decisions and Blockers

Items below are **not** settled by this revision. Each requires explicit approval before training. No values have been invented.

**Blockers (must be resolved before any training):**

- **U-1 — Provenance of 2020–2023 station context features (8–10) and the `actual` target.** The prior context-feature audit (`CANDIDATE_L2_CONTEXT_FEATURE_FORENSIC_AUDIT.md`) found no pre-2024 Mount Nuolja station SW_IN observations in the repository. This conflicts with §3 and §4, which assume station-derived inputs and targets for 2020–2023. Resolution options: (a) identify and verify an authoritative source with provenance; (b) restrict L2-EXP-01 to 2024–2025 data (conflicts with the quarantine and split design, requires approval); (c) withdraw the station-context inputs. Not decided here.
- **U-2 — Validity status of the frozen 2020–2023 F prediction artifact.** The prior audit classified it invalid for residual training and evaluation, yet §10 lists it as a required hash input. Approval needed on whether it may be used as the residual basis, and under what provenance statement.

**Design decisions requiring approval:**

- **D-1 — Calibration method.** Stage B method is not specified. Candidates include split conformal on VALIDATION residual quantiles and linear/isotonic quantile recalibration. Choice and its hyperparameters require approval; none is selected here.
- **D-2 — Upper physical bound U.** Prior draft used `1.25 × clearsky_ghi`; this is not justified by the record. Approval of U (and its basis) required.
- **D-3 — Training constants and early stopping.** Learning rate 1e-3, weight decay 1e-4, batch size, maximum epochs, and patience (prior draft: 15) are unjustified and require approval. Only the early-stopping epoch is permitted to be selected on VALIDATION.
- **D-4 — Coverage tolerance and per-slice pass criteria.** The 78–84% band and the per-horizon and per-regime floors/bands in the prior draft are candidate values only, pending approval.
- **D-5 — Cloud-regime boundaries.** Prior draft used Clear < 0.2, Partial 0.2–0.8, Overcast > 0.8. These are retained as candidate boundaries pending approval.
- **D-6 — Crossing-frequency threshold.** Prior draft used < 1.0%; approval required.
- **D-7 — Regularization.** Removal of BatchNorm and Dropout (§6.1) is a design choice that requires approval, or a written justification for reinstatement.

---

**Confirmation:** this revision is a specification edit only. No model was trained, no experiment runner was created, no data was modified, and no frozen artifact, F model, GAP19 code, or production code was altered.
