# PHASE10_ARCHITECTURE_DESIGN_CHECKPOINT

Status: **DESIGN ONLY — NO TRAINING PERFORMED**
ODD firewall: **INTACT** (no ODD rows read, aggregated, or referenced numerically in this document)
Protected champion: Stage 8.1 37-feature HGB (official ODD metrics fixed, see below) — **NOT MODIFIED**

---

## 0. Official Benchmark (fixed, unchanged)

| Metric | Value |
|---|---|
| MAE | 36.188657 W/m² |
| RMSE | 64.219495 W/m² |
| bias | +1.439399 W/m² |
| nMAE | 28.0688% |

This is the only number this phase is ultimately trying to beat, and it will only ever be touched again under a separate, explicit ODD-authorization request after a candidate has cleared every EVEN-only gate below.

---

## 1. Architecture Audit

### 1.1 What was actually inspected
- `stage8_1_full_37_feature_matrix_2024.csv`: 8,328 rows = 347 origins × 24 horizons (173 EVEN origins / 174 ODD origins, i.e. 4,152 / 4,176 rows).
- `PHASE9_MASTER_CLOSURE_CHECKPOINT.json` and the Phase 3–9 experiment history, for what has already been tried and rejected.

### 1.2 Row structure and what that implies about the current model
Each row is one `(origin_id, horizon_hour)` pair. For a fixed `origin_id`, all 24 rows share **identical** values of every feature derived from the trailing 24-hour observation window (`ctx_std_3h/6h/12h/24h`, `ctx_last_obs`, `ctx_mean_24h`, `ctx_max_24h`, `ctx_slope_6h`, etc.). Verified directly in the matrix: for origin 1, `ctx_std_3h`, `ctx_std_6h`, `ctx_last_obs`, `ctx_mean_24h` are constant across all 24 horizon rows, while `fc_cloud_cover`, `fc_temperature_2m`, `solar_elevation` vary row-to-row with horizon.

This means the model's only per-horizon information comes from horizon-indexed NWP/astronomical features (`horizon_hour`, `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `u700`, `v700`, `lwp_latest`, `iwp_latest`, terrain features) plus the three model-derived columns (`phys_pred_fold`, `pred_stage4_fold`, `disagreement_fold`, `pred_stage3b_cloud_nwp`). Origin-level context is a fixed vector broadcast identically to all 24 rows of that origin.

### 1.3 Direct answers to the seven audit questions

1. **Does HGB explicitly model temporal relationships between H1…H24?** No. HistGradientBoostingRegressor is fit on i.i.d. rows. `horizon_hour` is just one more scalar feature; the model can split on it but cannot represent "this horizon's error should be informed by the model's behavior at the adjacent horizon" as a structural relationship — each prediction is computed independently at inference time.

2. **Does it explicitly model dependencies between forecast horizons?** No. There is no shared hidden state, no autoregressive coupling of predictions, and no output-to-output constraint (e.g. smoothness across H_h → H_{h+1}). Two rows from the same origin at H9 and H10 are scored by the same tree ensemble but with no mechanism forcing or even encouraging consistency between them.

3. **Does it have a shared representation across horizons?** Only implicitly, and only to the extent the *same trained trees* are reused across all horizon values — this is parameter sharing by default (single model), not representation sharing in the sense of a learned embedding that ties horizons together. There is no explicit multi-task structure.

4. **Does it exploit the sequential structure of the 24-hour NWP trajectory?** No. We measured lag-1 (horizon-to-horizon) autocorrelation of the horizon-varying NWP inputs within each origin (EVEN split only): `fc_temperature_2m` ρ≈0.93, `v700` ρ≈0.84, `u700` ρ≈0.82, `fc_relative_humidity_2m` ρ≈0.80, `fc_cloud_cover` / `cloud_frac` ρ≈0.67. The forecast trajectory is strongly autocorrelated — there is real sequential structure sitting in the input space — but the current feature set exposes each horizon's *own* NWP value only, with no explicit neighbor-horizon deltas, trends, or momentum terms, and no architecture that treats the 24 rows of an origin as a sequence.

5. **Could H9–H12 difficulty plausibly arise from limitations of independent/tabular horizon treatment?** Plausibly, but this is confounded with a simpler explanation. Per-horizon MAE of the existing model-derived columns (EVEN split) peaks sharply mid-sequence: e.g. `pred_stage4_fold` error rises from ~1.7 W/m² at H1 to ~77.5 W/m² at H11–H12 before falling again — closely tracking the diurnal solar cycle (H9–H14 correspond to the highest-elevation, highest-clearsky-irradiance hours for this site in 2024, per `solar_elevation`/`clearsky_ghi`). This is consistent with H9–H12 simply being where the *physical magnitude* of SW_IN (and therefore of any error) is largest, not necessarily direct proof of an architectural failure. The audit can establish that tabular/independent treatment is a real, demonstrable gap (points 1–4 above) and that it is *co-located* with the worst-error region, but cannot establish that closing the gap will fix H9–H12 specifically — that is exactly what Phase 10 experimentation is for.

6. **Which information is already encoded in the 37 features?** Full trailing-24h observation summary statistics (std/mean/max/slope/kt-std at multiple windows), last observation, per-horizon NWP forecast fields (cloud cover, temperature, humidity, wind components), liquid/ice water path, clearsky GHI (raw and terrain-adjusted), solar geometry, terrain obstruction, and three prior-stage model predictions plus their disagreement.

7. **What architectural capability could exploit that same information differently?** Two independent capabilities are missing today and are both derivable from the existing 37 features without adding any new external data: (a) an explicit mechanism for letting a horizon's prediction be informed by neighboring horizons' feature values and/or predictions (temporal/sequence modeling), and (b) an explicit shared multi-task representation that jointly optimizes H1–H24 for one origin instead of scoring each independently (multi-horizon modeling). A third possibility is architectural in a different sense: keep the horizon-independent tabular treatment but add a second learned stage whose sole job is to model the *residual structure* of the first stage, using the same inputs (dual-stage/residual modeling).

### 1.4 What this audit does — and does not — establish
- **Established:** HGB has no explicit temporal or cross-horizon coupling mechanism (points 1–4, directly verifiable from the algorithm and the row structure).
- **Established:** the horizon-varying NWP inputs are strongly autocorrelated, i.e., real unused sequential structure exists in the input space.
- **Not established:** that exploiting this structure will reduce error specifically at H9–H12, or reduce error at all. H9–H12 severity is at least partly a magnitude effect from the diurnal cycle, and Phase 9 already showed several plausible-sounding regime/volatility hypotheses failed empirically. This audit is a basis for hypothesis generation, not a conclusion of expected success.

---

## 2. Candidate Architectures

All three candidates use **only** the existing 37-feature space (or origin-level reshapings/derivations of it that are intrinsic to the architecture, e.g. stacking a feature across the 24 rows of one origin into a sequence tensor — no new external variables, no new data sources).

### Candidate A — Temporal sequence model (per-origin trajectory encoder)
- **HGB limitation addressed:** absence of any temporal/sequence-aware processing (audit points 1, 4).
- **Information used:** the 24-step sequence, per origin, of the horizon-varying features (`fc_cloud_cover`, `fc_temperature_2m`, `fc_relative_humidity_2m`, `u700`, `v700`, `solar_elevation`, `clearsky_ghi`, `lwp_latest`, `iwp_latest`, terrain features), plus the constant origin-level context vector (`ctx_*`) as a static input.
- **Why available:** all of it is already in the 37-feature matrix; the only change is *reshaping* rows into a per-origin (24 × n_features) tensor instead of treating them as 24 independent rows — a representation transform intrinsic to the architecture, not a new feature.
- **Why it could improve H9–H12:** a sequence encoder (small GRU or 1D temporal convolution) can let the model use the *trend/momentum* of the incoming NWP trajectory (e.g., how cloud cover is evolving into H9–H12 from H1–H8) rather than only that hour's snapshot value — directly targeting the measured ρ≈0.67–0.93 autocorrelation that HGB does not exploit explicitly.
- **Why genuinely different from previously rejected experiments:** Phase 9's rejected candidates were single-feature additions (a cloud-volatility summary statistic, a calendar correction) bolted onto the same row-independent HGB. Candidate A changes *how* the existing information is processed, not *what* information is available.
- **Main overfitting risk:** highest of the three. Only 173 EVEN origins (≈4,152 rows) is a small dataset for a sequence neural network; risk of memorizing origin-specific trajectories rather than generalizing.
- **Computational cost:** low-moderate (small GRU/TCN, CPU-trainable in minutes), but requires more careful regularization and more careful OOF discipline than a tree model.
- **Evaluation without ODD leakage:** 5-fold OOF on EVEN only, folds split by `origin_id` (never split horizons of one origin across folds), early stopping on the held-out fold only.

### Candidate B — Multi-horizon shared-representation model
- **HGB limitation addressed:** absence of a shared multi-task representation across H1–H24 for the same origin (audit points 2, 3).
- **Information used:** the same 37 features per row, but training jointly optimizes all 24 horizons of an origin under one shared representation (e.g., a small feed-forward network with a shared trunk and a horizon-embedding, or a multi-output head producing all 24 predictions from the origin's static context plus horizon-indexed inputs stacked side-by-side).
- **Why available:** identical inputs to today's model; the only change is the training objective/architecture jointly scoring an origin's 24 horizons instead of 24 independent row-level fits.
- **Why it could improve H9–H12:** if H9–H12 errors are structurally related to systematic mis-calibration that is *consistent within an origin* (e.g., an origin-specific cloud regime that affects several adjacent horizons together), a shared representation can borrow strength across horizons of the same origin, rather than each horizon "re-learning" the pattern independently from a global row pool.
- **Why genuinely different from previously rejected experiments:** distinct from Candidate A (no explicit sequence/recurrence — the coupling is via shared parameters/multi-task loss, not via processing order) and from all Phase 9 candidates (which were feature engineering, not a change in what is jointly optimized).
- **Main overfitting risk:** moderate — smaller than Candidate A's risk because it needs no recurrent state, but multi-task heads with only 173 EVEN origins can still overfit per-origin idiosyncrasies if the shared trunk is too large.
- **Computational cost:** low (small MLP, seconds to low minutes on CPU).
- **Evaluation without ODD leakage:** same 5-fold OOF-by-origin scheme as Candidate A.

### Candidate C — Residual/dual-stage architecture
- **HGB limitation addressed:** none of HGB's structure is changed; this instead tests whether a *second* learned stage can model systematic residual structure that a single-stage tabular model leaves on the table, using the same information (audit point 7, third option).
- **Information used:** Stage 1 = a same-pipeline HGB reproduction (clearly labeled as the *reconstructed control*, per the Phase 9 caveat, since the exact original training code/hyperparameters remain unavailable). Stage 2 = a second model (e.g., a small gradient-boosted or linear model) trained on Stage 1's OOF residuals, using the same 37 features plus a small number of within-origin derived terms (e.g., a horizon's residual context relative to neighboring horizons) that are intrinsic transforms of existing columns.
- **Why available:** same inputs; the residual target is derived from Stage 1's own OOF predictions on EVEN data, not from anything new.
- **Why it could improve H9–H12:** if Stage 1's errors at H9–H12 have exploitable structure (e.g., a consistent sign or magnitude pattern conditional on other features) that a single HGB fit under-fits or averages away, a dedicated residual model focused only on that structure could recover some of it.
- **Why genuinely different from previously rejected experiments:** different from Phase 9's Candidate 2 ("cross-model disagreement signal") because that was a single new *feature* fed into the same one-stage HGB; here the change is architectural — a second, separately trained/optimized stage — not an added input column to the original model.
- **Main overfitting risk:** lowest of the three, but also the least likely to meaningfully address audit points 1–4 (it does not add temporal or cross-horizon coupling at all, only residual capacity) — main risk is that it re-produces the outcome of Phase 9 Candidate 3/A (a small but gate-failing improvement).
- **Computational cost:** lowest of the three.
- **Evaluation without ODD leakage:** Stage 1 trained/evaluated via 5-fold OOF-by-origin on EVEN; Stage 2 trained only on Stage 1's *out-of-fold* residuals (never in-fold) to avoid leakage, itself validated with a nested or a nominally separate 5-fold OOF-by-origin scheme.

---

## 3. Ranking

| Rank | Candidate | Rationale |
|---|---|---|
| 1 | **B — Multi-horizon shared representation** | Most directly targets the clearest, best-evidenced architectural gap (no cross-horizon coupling / no shared representation, audit points 2–3); lower overfitting risk than a full sequence model given only 173 EVEN origins; cheap to train and easy to keep leakage-safe. |
| 2 | **A — Temporal sequence model** | Also well-motivated (measured autocorrelation ρ≈0.67–0.93 in horizon-varying inputs), but higher overfitting risk and complexity for a dataset this size; kept as a secondary hypothesis if B fails outright. |
| 3 | **C — Residual/dual-stage** | Lowest risk but weakest connection to the audited architectural gap; closest in spirit to Phase 9's already-rejected disagreement-signal candidate, so lowest expected marginal value. |

## 4. Selected Primary Architecture: **Candidate B — Multi-horizon shared-representation model**

### 4.1 Exact inputs
- Per-origin static context vector: `ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h, ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h, ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h, ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h` (identical across the 24 rows of an origin — used once per origin, not duplicated as 24 independent copies inside the loss).
- Per-horizon inputs (24 steps per origin): `horizon_hour, month, hour, solar_elevation, solar_zenith, clearsky_ghi, clearsky_ghi_terrain_adjusted, fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac, lwp_latest, iwp_latest, lwp_x_cloud, terrain_horizon_elevation_deg, terrain_elevation_margin_deg, terrain_solar_obstruction_flag, u700, v700, pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold, is_daytime, is_night_causal`.
- No ODD rows, no future actual `SW_IN`, no future errors.

### 4.2 Output structure
A single shared trunk (small MLP, e.g. 2 hidden layers, width ≤ 64, dropout regularized) consumes the static context concatenated with a learned horizon embedding + the per-horizon inputs, and emits one predicted SW_IN value per `(origin, horizon)` row — but trained under a multi-task loss that batches all 24 horizons of an origin together per gradient step, so the shared trunk is optimized to be consistent across the whole origin rather than fit row-by-row in isolation.

### 4.3 Training procedure
- Data: EVEN split only (173 origins / 4,152 rows).
- Batching: one origin (24 rows) per training example group; batch size in origins, not rows.
- Loss: mean absolute error, summed/averaged over the 24 horizons of each origin.
- Regularization: dropout + weight decay, small hidden width, deliberately minimal architecture (no large sweep — a single, justified configuration chosen up front, not tuned to maximize OOF score).
- Early stopping: on the held-out OOF fold, by origin.

### 4.4 Validation procedure
- 5-fold OOF, folds assigned by `origin_id` (all 24 horizons of one origin stay in the same fold) — identical fold discipline to what Phase 9 used.
- Control: the **official Stage 8.1 champion metrics** are the ultimate benchmark (fixed, per Section 0); a **same-pipeline HGB reconstruction** (explicitly labeled as reconstructed, per the Phase 9 caveat) will be used as the like-for-like EVEN-only OOF control for gates G1–G4, since the official champion's OOF fold predictions are not available outside ODD evaluation.

### 4.5 Leakage controls
- Train/validate on EVEN only; ODD is not read, aggregated, or inspected at any point in this stage.
- No future actual SW_IN or future errors used as inputs.
- Fold split strictly by origin_id (no horizon of a given origin leaks across folds).
- Model selection (architecture choice, hidden width, regularization strength) fixed **before** looking at any OOF result — no iterative tuning against the EVEN OOF score, to avoid the "sweep in disguise" failure mode this project has explicitly locked against.

### 4.6 Preregistered gates (locked, unchanged from Phase 9)
- G1: aggregated ΔMAE ≤ −0.50 W/m² (vs. same-pipeline EVEN control)
- G2: ≥ 4/5 folds improved
- G3: max fold degradation ≤ +0.50 W/m²
- G4: candidate nMAE ≤ control nMAE AND candidate RMSE ≤ control RMSE
- G5: causal/parser compliance (no future information used)
- G6: exact control reproduction — will be reported honestly as **approximate** (same caveat as Phase 9) unless the original Stage 8.1 training code/hyperparameters are located; the official champion numbers in Section 0 will never be replaced by any reconstructed value.

### 4.7 Why this is scientifically justified
Candidate B is chosen because it is the smallest, lowest-risk architectural change that directly targets a concretely demonstrated gap (no shared/multi-task representation across an origin's 24 horizons) rather than a speculative one. It reuses 100% of the existing feature space, requires no new hyperparameter sweep, and its failure or success will cleanly answer the scientific question this phase was opened to ask — whether cross-horizon shared representation extracts more signal from the same inputs than fully independent per-row tabular treatment does — without touching ODD or reopening feature research.

---

## 5. Explicit non-claims (carried forward)
Nothing in this checkpoint claims that Candidate B will pass its gates, that H9–H12 error is caused by architecture rather than input-magnitude/physical volatility, or that Stage 8.1's 28.0688% nMAE is a lower bound. This document only freezes the design; no training has been performed under it.

**Next step, pending your go-ahead:** train Candidate B only, under the procedure above, on EVEN data only, and report G1–G6 plus fold-by-fold and H9–H12-specific ΔMAE.
