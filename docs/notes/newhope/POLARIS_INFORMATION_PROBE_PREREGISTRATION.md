# POLARIS — INCREMENTAL-INFORMATION PROBE
## Preregistration v1.0 (DRAFT — unfrozen until Section 12 is signed)

**Classification:** DIAGNOSTIC ONLY
**Development data:** EVEN origins only
**ODD access:** PROHIBITED for the entirety of this study
**Champion:** Stage8.1 remains frozen and untouched. This study cannot promote, demote or modify any champion.

This document must be frozen (hash recorded) **before any target is computed**. No result in this study is admissible if its target definition was written or amended after the corresponding number was seen.

---

## 1. Research question

> Does the causal state available at t0 contain incremental information about future H7–H12 cloud/transmission evolution that is not already represented by the Stage8.1 37-feature state — and if so, does that information have value for point prediction or primarily for uncertainty estimation?

This is an **information test**, not a forecasting candidate. A positive result does not produce a model. It produces permission to preregister one narrow feature-addition experiment under G1–G6.

---

## 2. The three competing failure modes

| Mode | Statement | Discriminating evidence |
|---|---|---|
| **M1 — information absent** | The t0 causal state does not contain the information | P1 ≈ P0 on all targets |
| **M2 — representation hides it** | Information exists but the 37 features don't expose it | P2 > P1 for some preregistered source |
| **M3 — loss hides it** | Information is present and used, but MAE rewards hedging | P1 ≫ P0, **and** Phase B hedging test positive |

These are not mutually exclusive. The study is designed to assign evidence weight, not to pick a single winner.

---

## 3. Phase structure — ordering is binding

**Phase A** consumes no new data and must complete first. Phase C requires a written amendment.

| Phase | Question | New data required |
|---|---|---|
| **A** | Does the Stage8.1 state predict future H7–H12 evolution at all, beyond solar/season? | None |
| **B** | Does the champion's H7–H12 error behave like correct hedging under a bimodal future? | None |
| **C** | Does one specific candidate source add information beyond the Stage8.1 state? | One named source, per amendment |

Rationale for this ordering: Phase A and B are free, use only existing artifacts, and are decisive for M3 and M1. Phase C costs data ingestion and is only interpretable once we know whether P1 clears P0.

---

## 4. Probe ladder — exact feature sets

Feature sets are nested. Each is frozen here by definition, and must be reconciled against the actual frozen Stage8.1 feature registry before execution (canonical column names, not the conceptual names below).

**P0 — deterministic solar/seasonal state**
- solar elevation at t0 and at each of H7–H12
- solar azimuth at H7–H12
- clear-sky GHI at H7–H12
- day-of-year, encoded as sin/cos
- daylight duration for the origin date

**P1 — P0 + the frozen Stage8.1 causal state at t0**
- the full 37-feature Stage8.1 vector as constructed by the frozen pipeline
- where a Stage8.1 feature is horizon-indexed (per-horizon valid-time NWP), take the H7–H12 subvector only
- no re-engineering, no re-scaling beyond fold-internal standardisation, no selection

**P2 — P1 + one candidate information source**
- NOT SPECIFIED IN v1.0. Requires an amendment naming exactly one source, its causal availability audit, and its exact tensor/table representation.
- Combining two or more candidate sources into a single P2 is prohibited. If P2 wins, attribution must be unambiguous.

---

## 5. Targets — frozen definitions

All targets are defined on the **clear-sky index** `k_t`, not raw SW_IN. Raw SW_IN is dominated by solar amplitude, which would let P0 win trivially and collapse the ladder.

**k_t definition**
```
k_t(h) = SW_IN_actual(h) / clearsky_GHI(h)
```
- computed only where `clearsky_GHI(h) >= 20 W/m²`; otherwise `k_t(h)` is undefined
- clipped to `[0.0, 1.2]`
- clear-sky GHI comes from the existing frozen clear-sky model, unchanged

**Horizon window:** H7–H12 inclusive (06:00–11:00 UTC), fixed.

**Origin eligibility:** an origin enters the analysis only if **at least 5 of the 6** hours H7–H12 have defined `k_t`. Otherwise the origin is dropped. The eligible-N must be reported before any modelling. This is a real constraint at 68.36°N: winter origins will be excluded wholesale.

**T1 — future transmission volatility**
`std(k_t(h))` over defined h in H7–H12, population std (ddof=0).

**T2 — maximum transition magnitude**
`max |k_t(h+1) − k_t(h)|` over consecutive defined pairs in H7–H12.

**T3 — mean transmission level**
`mean(k_t(h))` over defined h in H7–H12.

**T4 — champion difficulty**
`mean |SW_IN_actual(h) − SW_IN_pred_OOF(h)|` over defined h in H7–H12, in W/m².

> **T4 contamination rule.** `SW_IN_pred_OOF` must be the **out-of-fold** prediction of the Stage8.1 pipeline refit under the same fold assignment used in this study. In-sample champion predictions are prohibited as a target. If OOF EVEN predictions under a matching fold assignment cannot be reconstructed, T4 is dropped from the study rather than approximated.

All four targets are continuous. No binarisation. No thresholding. No "transition/no-transition" labels in this study.

---

## 6. Models and fitting

Permitted probe models, both reported for every (ladder rung × target) cell:

1. **Ridge regression**, standardisation fit inside the training fold only, `alpha` fixed at 1.0. No alpha search.
2. **Gradient-boosted trees**, `max_depth=3`, `n_estimators=200`, `learning_rate=0.05`, `min_samples_leaf=10`, fixed seed. No tuning.

Prohibited at this stage, without exception:
- neural encoders of any depth
- latent spaces, latent ablation studies, multi-head architectures
- feature selection of any kind, including importance-based pruning
- hyperparameter search, seed shopping, architecture variants
- any model whose parameter count approaches the eligible origin count

**Rationale:** the effective independent sample is the origin count (order 100 after eligibility filtering), not the row count. Anything expressive enough to learn a representation is expressive enough to memorise this sample.

---

## 7. Evaluation protocol

- **Unit of analysis:** one row per eligible EVEN origin.
- **Folds:** 5-fold GroupKFold by forecast origin, using the same fold assignment as Stage8.1 development. Fold assignment is recorded before fitting.
- **Reported statistic:** out-of-fold R² and out-of-fold Spearman ρ, per target, per rung, per model.
- **Increment:** ΔR²(P1−P0) and ΔR²(P2−P1), computed on the same OOF predictions.
- **Interval:** paired origin-level bootstrap on per-origin squared-error differences, 10,000 resamples, 95% percentile CI.
- **Null:** permutation test shuffling the target across origins **within calendar-month blocks**, 1,000 permutations. Month blocking is mandatory. An unblocked shuffle null is not admissible — the aliasing audit already showed month-matched nulls behaving very differently from naive ones.

**Power floor.** If eligible N < 60, the study is reported as descriptive only and no decision in Section 9 may be invoked.

---

## 8. Phase B — hedging diagnostic

Purpose: test M3 directly, using only existing artifacts.

For each eligible EVEN origin, construct an empirical future-trajectory ensemble from the k = 5 nearest causal-state neighbours (EVEN-only, same distance definition as the existing aliasing audit, seasonal scaling documented).

Compute, over H7–H12 daytime hours:
- **B1:** where the champion's OOF point forecast sits within the neighbour ensemble distribution (PIT-style rank). A hedging model concentrates near the median.
- **B2:** the champion's pinball loss at the 0.5 quantile versus the neighbour-ensemble median's pinball loss.
- **B3:** the fraction of H7–H12 hours where the neighbour ensemble is empirically bimodal (documented bimodality criterion to be fixed in the amendment before computation), and the champion's MAE conditional on that fraction.

**Positive M3 evidence:** champion forecasts rank near the ensemble median, MAE rises with ensemble spread, and the ensemble median does not materially outperform the champion point forecast. That pattern means the champion is already behaving near-optimally for the loss it was given, and further point-MAE reduction on those hours is the wrong objective.

Phase B produces no candidate and touches no ODD data.

---

## 9. Decision rules — written before results

A **hit** requires both:
- bootstrap 95% CI for the increment excludes zero, **and**
- point-estimate ΔR² ≥ 0.03 on at least two of the four targets

Anything weaker is a miss. Marginal results are not to be rescued by changing the statistic, the window, the transformation, or the model.

| Result | Reading | Permitted next action |
|---|---|---|
| **P1 − P0 is a miss** | M1 strengthened: the 37-feature state says little about future evolution beyond solar/season | Stop re-representing existing inputs. Direction shifts to new observation sources (near-site cloud observation, low-latency satellite, ceilometer), each subject to its own causal availability audit |
| **P1 − P0 is a hit, Phase B positive** | M3 strengthened: the model knows, the loss hides it | Move to calibrated distributional forecasting on frozen Stage8.1 and to uncertainty-aware dispatch. Point-MAE stops being the sole objective |
| **P1 − P0 is a hit, Phase B negative** | Information present, not obviously hedged | Phase C becomes justified. Proceed to amendment |
| **P2 − P1 is a hit (Phase C)** | M2 supported for that one source | Preregister exactly one HGB feature-addition candidate using only the implicated features, judged on G1–G6 against the frozen control. Simplest possible representation first |
| **P2 − P1 is a miss** | That source adds nothing the champion lacks | That source closes as an information route, permanently, not just as a forecasting route |

---

## 10. Explicit failure conditions

The study is declared negative, and the corresponding route closed, if:
- eligible N < 60 (underpowered; no conclusions drawn either way)
- T4 cannot be reconstructed from genuine OOF champion predictions and the remaining targets all miss
- any target definition in Section 5 requires amendment after its values were computed
- ODD is touched at any point, for any reason

---

## 11. Prohibitions carried from POLARIS governance

- No ODD access. No ODD-informed decisions. No "quick check" against ODD.
- No change to the benchmark, split, horizons, target, timestamp convention, night handling or metric.
- No reopening of a closed route on the strength of this study alone. A positive information result licenses one preregistered candidate, nothing more.
- No promotion of a diagnostic association to a predictive claim. Every number in this study is an association.
- No description of any outcome as proving an irreducible ceiling.

---

## 12. Recorded before execution

- [ ] Stage8.1 feature registry inspected; canonical P1 column names and ordering recorded verbatim
- [ ] Clear-sky model version and source recorded
- [ ] Fold assignment file written and hashed
- [ ] Eligible EVEN origin list written and hashed; eligible N recorded
- [ ] Champion OOF prediction artifact built under the matching fold assignment, and hashed
- [ ] This document hashed and frozen
- [ ] Phase C amendment: named source, causal availability audit, exact representation — **pending, blocks Phase C only**

Signed / frozen by: __________  Date: __________  SHA-256 of this file: __________
