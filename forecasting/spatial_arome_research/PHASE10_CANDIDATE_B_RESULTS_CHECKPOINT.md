# PHASE10_CANDIDATE_B_RESULTS_CHECKPOINT

Status: **CANDIDATE B — EVEN-ONLY EVALUATION COMPLETE — GATES FAILED — REJECTED**
ODD firewall: **INTACT** — no ODD row was loaded into any array, model, or metric in this phase.
Protected champion: Stage 8.1 37-feature HGB — **NOT MODIFIED, NOT REPLACED**

---

## 0. Official Benchmark (fixed, unchanged, untouched by this experiment)

| Metric | Value |
|---|---|
| MAE | 36.188657 W/m² |
| RMSE | 64.219495 W/m² |
| bias | +1.439399 W/m² |
| nMAE | 28.0688% |

This number was **not** used anywhere in training, validation, model selection, or gate computation below. All gate comparisons use the EVEN-only reconstructed control (Section 2).

---

## 1. Leakage Audit (verified programmatically, not just asserted)

| # | Check | Result |
|---|---|---|
| 1 | No ODD rows read or used anywhere in training/validation | **PASS** — data loaded, immediately filtered to `split == 'EVEN'` (4,152 rows / 173 origins); ODD rows (4,176) were counted for confirmation but never entered any feature array, model fit, or prediction. |
| 2 | No future actual `SW_IN` or future errors in inputs | **PASS** — the 39-feature input set was checked programmatically for any column name containing `actual_SW_IN` or `future`; none found. All per-horizon inputs are forecast/geometry/terrain fields or prior-stage model outputs, not realized target values. |
| 3 | All 24 horizons of each origin stayed in the same fold | **PASS** — verified twice: (a) an explicit assertion during `GroupKFold` splitting that no `origin_id` appears in both a fold's train and test index sets, for both the control and Candidate B; (b) a direct cross-check comparing per-origin fold assignment between the control run and the Candidate B run — **0 mismatches across all 173 EVEN origins**, confirming both models were scored on identical fold partitions for a fair fold-by-fold comparison. |
| 4 | Architecture/hyperparameters fixed before OOF results were inspected | **PASS** — architecture (2 hidden layers, width 64/32, embedding dim 8, dropout 0.2, weight decay 1e-4, Adam lr 1e-3, batch = 8 origins, patience 20, max 300 epochs) was frozen in `PHASE10_ARCHITECTURE_DESIGN_CHECKPOINT` before this run. The script was executed once, end-to-end, with these fixed values; no value was changed after seeing a fold or aggregate result. |
| 5 | Reconstructed control clearly distinguished from official champion | **PASS** — see Section 2. The EVEN-only reconstructed control (MAE 26.37 W/m²) is explicitly a different, non-comparable number from the official ODD champion (MAE 36.19 W/m²) because it is evaluated on a different split; it is never presented as, or substituted for, the official champion. |

**Implementation note (leakage-safety refinement, not an architecture change):** the frozen design specified early stopping "on the held-out OOF fold." To avoid even soft leakage of the test fold's target values into the stopping decision, an internal validation subset (20% of the *training* origins only, never the held-out fold) was carved out per fold for early stopping instead. This is strictly more conservative than the literal wording of the frozen design and does not alter the model architecture, inputs, loss, or batching in any way.

---

## 2. Reconstructed Same-Pipeline Control (EVEN-only, 5-fold OOF by origin)

Because the original Stage 8.1 training code/hyperparameters remain unavailable (per the Phase 9 caveat, carried forward unchanged), the control used for gates G1–G4 is a **same-pipeline `sklearn.HistGradientBoostingRegressor` reconstruction with default hyperparameters (no sweep)**, trained/evaluated with the identical 39-feature input space and identical 5-fold group-by-origin OOF scheme as Candidate B, on EVEN data only.

| Metric | Reconstructed Control (EVEN-OOF) |
|---|---|
| MAE | 26.3668 W/m² |
| RMSE | 55.2513 W/m² |
| bias | −0.1291 W/m² |
| nMAE | 20.4507% |

This number is **not** the official champion and is **not** claimed to be. It exists solely as the like-for-like EVEN-only OOF baseline this phase's design checkpoint called for. (It is also numerically distinct from the separate historical Phase 9 "reconstructed control" figure of MAE 35.41 / nMAE 27.49%, which was computed under a different, ODD-adjacent comparison context in a prior phase — the two are not interchangeable and neither should be confused with the official champion.)

nMAE for both models in this report uses the fixed normalizer **128.9284 W/m²**, derived once from the official champion's own MAE/nMAE ratio (36.188657 / 0.280688), so that nMAE values reported here are on a consistent, comparable scale — this constant was not recomputed from EVEN data and does not use any EVEN or ODD actuals beyond what is already public in the official benchmark.

---

## 3. Candidate B — Architecture (as frozen, unchanged)

Shared MLP (input → 64 → 32 → 1) with a learned 24-row horizon embedding (dim 8) concatenated to each horizon's feature vector; trained jointly per origin (batches of 8 origins = 192 rows/step) under mean-absolute-error loss averaged across the 24 horizons; dropout 0.2, L2 weight decay 1e-4, Adam optimizer, lr 1e-3. Exactly the 39 inputs specified in the frozen design checkpoint (14 static + 25 per-horizon features). No feature was added, removed, or transformed beyond per-fold standardization (mean/std fit on training-fold data only).

| Metric | Candidate B (EVEN-OOF) |
|---|---|
| MAE | 26.0112 W/m² |
| RMSE | 54.2820 W/m² |
| bias | −2.7713 W/m² |
| nMAE | 20.1750% |

---

## 4. Fold-by-Fold Results

| Fold | n origins | Control MAE | Candidate B MAE | ΔMAE (B − Control) | Improved? |
|---|---|---|---|---|---|
| 0 | 35 | 29.1137 | 27.0406 | **−2.0731** | Yes |
| 1 | 35 | 22.8351 | 24.0944 | **+1.2593** | No |
| 2 | 35 | 25.5086 | 25.6572 | +0.1486 | No |
| 3 | 34 | 30.0997 | 28.8913 | **−1.2084** | Yes |
| 4 | 34 | 24.3254 | 24.4093 | +0.0839 | No |

Aggregate ΔMAE (Candidate B − Control) = **−0.3556 W/m²**
Folds improved: **2/5**
Max fold degradation: **+1.2593 W/m²** (Fold 1)

## 5. H9–H12 Specific Result

| | Control MAE | Candidate B MAE | ΔMAE |
|---|---|---|---|
| H9–H12 | 60.5587 W/m² | 61.0898 W/m² | **+0.5311 W/m² (worse)** |

Candidate B did **not** improve the H9–H12 region that motivated this phase — if anything it is marginally worse there (H9 alone is +5.46 W/m² worse; H12 is −2.61 W/m² better; the region nets slightly negative). The full per-horizon breakdown shows a mixed, non-systematic pattern (improvements at some horizons, degradations at others), not the H9–H12-focused correction the architecture hypothesis was designed to test for.

---

## 6. Gate Results (G1–G6, locked, exact thresholds)

| Gate | Requirement | Result | Verdict |
|---|---|---|---|
| G1 | aggregated ΔMAE ≤ −0.50 W/m² | −0.3556 W/m² | **FAIL** |
| G2 | ≥4/5 folds improved | 2/5 | **FAIL** |
| G3 | max fold degradation ≤ +0.50 W/m² | +1.2593 W/m² | **FAIL** |
| G4 | candidate nMAE ≤ control nMAE AND candidate RMSE ≤ control RMSE | nMAE 20.175 ≤ 20.451 ✓; RMSE 54.282 ≤ 55.251 ✓ | **PASS** |
| G5 | causal/parser compliance | verified (Section 1) | **PASS** |
| G6 | exact control reproduction | control is an approximate same-pipeline reconstruction, not exact — honestly reported, official champion untouched | **HONEST / NOT CLAIMED EXACT** |

---

## 7. Final Verdict

**CANDIDATE B IS REJECTED.**

It fails G1, G2, and G3 — the aggregate improvement is small (−0.36 W/m², under the −0.50 W/m² bar), inconsistent across folds (only 2 of 5 improved, with one fold degrading by +1.26 W/m², more than double the allowed +0.50 W/m² tolerance), and does not deliver a robust or consistent gain, let alone a targeted one in the H9–H12 region this phase was opened to investigate. Passing G4 alone (a modest edge in nMAE/RMSE on the full aggregate) is not sufficient without G1–G3, since the locked gate set requires **all** gates to pass before any candidate may proceed toward ODD authorization.

Per the locked experiment rules:
- **No rescue variants (B1/B2/B3) will be created.**
- **ODD was not accessed and will not be accessed** for this candidate.
- This result stands as the honest outcome of the one pre-registered configuration.

## 8. What this does and does not establish

- **Does not** establish that shared multi-horizon representation learning is a dead end in general — only that this specific minimal, pre-registered configuration, on this dataset size (173 EVEN origins), did not clear the bar.
- **Does not** re-open the question of whether Stage 8.1's 28.0688% nMAE is a lower bound — no such claim is made.
- **Does** conclude, for this phase: no robust architectural improvement was found under Candidate B.

If you want to pursue Candidate A (temporal sequence model) or Candidate C (residual/dual-stage) as previously ranked alternatives, that would require a new, separate design-freeze step — not a variant of Candidate B — consistent with the "no rescue variants" rule.

**PHASE10_CANDIDATE_B_NO_ROBUST_IMPROVEMENT_FOUND**
