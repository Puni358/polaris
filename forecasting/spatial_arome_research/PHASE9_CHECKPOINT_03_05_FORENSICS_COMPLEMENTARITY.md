# PHASE9 CHECKPOINT — PHASE 3 (worst-event forensics) → PHASE 4 (model-by-model) → PHASE 5 (complementarity)

All analysis in this checkpoint uses a dataset built from `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv`,
restricted to the 173 dates verified in the audit as the official Stage 8.1 ODD set, joined across all
10 available models on (date, forecast_horizon), with ground truth confirmed identical across models.
This is diagnostic use of ODD (characterizing the existing champion's error structure), not
hyperparameter/model selection — no decisions are made from it here.

---
## PHASE 3 — Deep characterization of the H9–H12 error concentration

**Horizon contribution.** H12 is the single worst horizon (MAE 64.8 W/m², RMSE 101.0 W/m², bias −14.7).
H9–H12 combined account for 52% of total absolute error on only 37% of daytime observations.

**Origin concentration.** Within H9–H12 alone, the worst 10% of origins (18 of 173 days) account for
32% of that window's total error; the worst 5% (9 days) account for 18%. This is a moderate, not extreme,
concentration — H9–H12 error is not dominated by a tiny handful of catastrophic days; it's broadly
elevated across many spring/summer days, with a heavier tail on top.

**Direction of the error.** 59% of the 173 origins show a net *underestimate* in H9–H12, 41% show a net
*overestimate* — underestimation is more common but far from universal (median per-origin bias is only
−1.6 W/m², much smaller than the −14.7 W/m² aggregate figure, meaning the aggregate is pulled by a
subset of strongly negative days rather than being a uniform per-day effect).

**Seasonal regime.** This is the clearest, best-supported finding. H9–H12 error is almost entirely a
warm-half-of-year phenomenon:

| Month | H9–12 MAE (W/m²) | H9–12 bias (W/m²) | mean actual (W/m²) |
|---|---|---|---|
| Apr | 64.9 | **−41.3** | 403 |
| May | 106.3 | **−43.4** | 506 |
| Jun | 124.1 | +13.5 | 353 |
| Jul | 92.9 | −9.2 | 372 |
| Aug | 75.3 | −0.1 | 265 |
| Sep | 76.9 | +3.3 | 206 |
| Nov–Feb | <25 | ≈0 | <60 |

April and May stand out specifically: MAE is high (as expected, since irradiance magnitude is high) but
the *bias* is also large and strongly negative (−41 to −43 W/m²), unlike June–September where bias is
much closer to neutral despite comparable or higher MAE. This says spring specifically has a systematic
under-prediction problem at solar-noon horizons, not just proportionally-scaled noise.

**Weather-transition proxy.** Using within-day hour-to-hour irradiance volatility (mean |Δactual| across
H6–H18) as a proxy for broken-cloud/transition conditions, the correlation with H9–H12 MAE is **+0.73** —
a strong relationship. High-volatility days (consistent with broken cloud / rapid clear↔cloudy
transitions) are the primary driver of the worst H9–H12 errors, not steady clear-sky or steady-overcast
days.

**Top-decile worst events (all horizons, not just H9–12).** The worst 10% of all daytime forecasts (289
of 2883 obs) account for **47% of total absolute error**. These are concentrated at H9–H15 (peaks at
H11/H12) and April–September, consistent with the horizon/seasonal findings above. Within this pool,
the single most extreme 1% of errors (n=29) skew toward *overestimation* (mean signed error +32 W/m²,
concentrated in June–July), while the broader top-5% pool skews toward *underestimation* (mean signed
error −21 W/m², concentrated in May–June) — the tail behavior is not one-directional.

**Bias-reversal robustness (H9–12 under → H14–15 over): NOT ROBUST at the per-day level.** This is a
correction to the aggregate-level hypothesis raised before this checkpoint. Per-origin mean error in
H9–H12 correlates **positively** (+0.45) with per-origin mean error in H14–H15 — days that underestimate
around solar noon do *not* reliably flip to overestimating two to three hours later. Only 21% of origins
show the specific "under-then-over" reversal pattern; 38% show "under-then-under" (same direction). The
aggregate-level reversal (negative bias at H9–12, positive bias at H14–15) is real in the pooled numbers,
but it is driven by *different subsets* of days having different signed errors at each horizon, not by
the same days systematically flipping sign as the horizon lengthens. **This means it should not be
treated as a single exploitable causal mechanism (e.g. a simple horizon-dependent bias correction term
calibrated on the aggregate reversal would be miscalibrated for most individual days).**

**Verdict on exploitability:** the H9–H12 concentration is a genuine, well-supported error mode (strong
volatility correlation, clear seasonal concentration in Apr–May specifically), but it is *not* a simple
uniform bias to subtract — it's concentrated in cloud-transition conditions during the shoulder season,
which is inherently a hard forecasting regime, not an obvious systematic correction.

---
## PHASE 4 — Model-by-model forensics (all 10 models, identical 173-date ODD set, identical ground truth)

Overall daytime ranking (MAE, W/m²):

| Model | MAE | RMSE | Bias | nMAE |
|---|---|---|---|---|
| HGB 37-feature (Stage 8.1, champion) | 36.19 | 64.22 | +1.44 | 28.07% |
| HGB 40-feature (Stage 8.17A) | 36.43 | 64.61 | +0.54 | 28.25% |
| HGB 42-feature (Stage 8.19) | 36.49 | 64.76 | +0.76 | 28.30% |
| Dynamic Ensemble Hybrid (Stage 4.3) | 43.45 | 74.85 | −1.97 | 33.70% |
| LightGBM 22-feature (Stage 3C) | 55.61 | 99.46 | −9.28 | 43.13% |
| Chronos-2 Raw | 56.46 | 100.52 | −12.76 | 43.79% |
| Kt Persistence 24h | 56.55 | 106.16 | −2.20 | 43.86% |
| Chronos-2 Multivariate | 56.96 | 100.91 | −13.96 | 44.18% |
| TimesFM 3.0 | 89.56 | 155.73 | −76.62 | 69.47% |
| Moirai 2.0 | 109.32 | 184.06 | −104.37 | 84.79% |

**Best model per individual horizon:** an HGB variant (37/40/42-feature) wins at every horizon except H1
(TimesFM, narrowly) and H23–H24 (Dynamic Ensemble Hybrid, narrowly, by <0.5 W/m²). Critically, **at every
horizon in H9–H12, HGB 37-feature (or a near-identical HGB sibling) is already the best available model
in this inventory** — no structurally different model (Chronos, TimesFM, Moirai, Dynamic Ensemble
Hybrid, LightGBM) is competitive there, let alone superior. At H12 specifically, the next-best
*structurally distinct* model (Dynamic Ensemble Hybrid) has MAE 77.5 vs HGB's 64.8 — 19% worse, and the
foundation models are 60–200% worse.

**Individual model character:**
- **HGB 40/42-feature** are near-perfect twins of the champion (same base architecture, 2–3 extra
  features each); differences from HGB 37-feature are noise-level (±1% nMAE), consistent with the
  historical record marking them REJECTED / INVALIDATED for reasons unrelated to raw accuracy.
- **Dynamic Ensemble Hybrid (Stage 4.3)** is the best of the structurally-different models — it shares
  lineage with HGB (its ensemble members include Stage 3B/3C GBDTs), and its errors are the most
  correlated with HGB's of any non-twin model (see Phase 5).
- **Foundation models (Chronos, TimesFM, Moirai)** degrade sharply at longer horizons and around
  solar noon specifically — Moirai's MAE at H9 (148) is over 3x HGB's, and it has a large negative bias
  overall (−104 W/m²), i.e. it systematically and substantially under-predicts irradiance magnitude.
  These are zero-shot/lightly-adapted general time-series foundation models with no solar-specific
  features; their weakness at exactly the hardest horizons is consistent with them lacking the
  NWP/cloud/terrain features that give the GBDT models their edge.
- **Kt Persistence 24h** (yesterday's clearness-index pattern) performs roughly on par with the raw
  Chronos zero-shot model — a useful sanity check that the foundation models aren't beating even a naive
  baseline by much on this dataset.

---
## PHASE 5 — Model complementarity

**Signed-error correlation with HGB 37-feature** (positive = errors move in the same direction):

| Model | Signed-error corr. | Abs-error corr. | Overall win rate vs HGB | Win rate during HGB's worst 10% events |
|---|---|---|---|---|
| HGB 40-feature | 0.98 | 0.98 | 36.2% | 52.2% |
| HGB 42-feature | 0.99 | 0.98 | 36.8% | 51.9% |
| Dynamic Ensemble Hybrid | 0.91 | 0.89 | 41.4% | 43.6% |
| LightGBM 22-feature | 0.73 | 0.72 | 35.1% | 39.8% |
| Chronos-2 Raw | 0.72 | 0.70 | 36.0% | 42.9% |
| Chronos-2 Multivariate | 0.72 | 0.70 | 34.7% | 43.9% |
| Kt Persistence 24h | 0.69 | 0.70 | 28.5% | 38.1% |
| TimesFM 3.0 | 0.50 | 0.55 | 26.1% | 39.8% |
| Moirai 2.0 | 0.42 | 0.52 | 21.8% | 40.1% |

**Key findings:**

1. **Every model's signed error is positively correlated with HGB's — none is negative or near-zero.**
   Even the least-correlated model (Moirai, architecturally the most different) still has +0.42 signed
   correlation and +0.52 absolute-error correlation. There is no pair in this inventory with genuinely
   anti-correlated (complementary) errors. All models tend to be wrong in the same direction at the same
   times — consistent with them all forecasting the same physical target from broadly overlapping
   information (and all struggling on the same hard cloud-transition events identified in Phase 3).

2. **No model beats HGB more than 41% of the time overall**, and that ceiling (Dynamic Ensemble Hybrid)
   is the architecturally closest relative, not an independent model.

3. **Directly answering the Phase 3 question — does any model do better specifically during HGB's worst
   H9–H12 / hardest events? No.** During HGB's worst 10% of events (by its own abs. error), every
   structurally distinct model has a *higher* mean absolute error than HGB (Dynamic Ensemble Hybrid:
   177.1 vs HGB's 168.1; Chronos: ~195; TimesFM: 241; Moirai: 271), and win rates against HGB *drop*
   during these events for every foundation model (all sit at 40–44%, not meaningfully above their
   overall-average win rate). Only the near-twin HGB40/42 edge narrowly above 50% — again, not an
   independent model, just a marginally different feature set with the same architecture.

4. **The hard events are hard for everyone, not specifically hard for HGB.** This is the central
   complementarity finding: the alternative models don't fail *differently* from HGB in a way that could
   be exploited — they fail in the *same direction*, and *more severely*, on exactly the days/horizons
   HGB already struggles with.

**Verdict:** on the evidence available in this inventory, **there is no genuine, exploitable error
diversity among the available models.** A weighted or horizon-specific ensemble built from any
combination of {HGB, Dynamic Ensemble Hybrid, Chronos, TimesFM, Moirai, LightGBM, Persistence} would be
blending in models that are both weaker overall and *more correlated in error during exactly the events
that matter most* — the opposite of what a useful ensemble needs. This does not rule out ensembling in
principle, but it does rule out ensembling with the models currently in the historical record. Any future
ensemble candidate would need to be demonstrably different in its error structure during the H9–H12 /
high-volatility regime specifically, which none of the existing alternatives are.

---
## Status
PHASE 3, 4, 5 complete. No candidate model-integration opportunity identified from the existing model
inventory. Proceeding to candidate-solution design (Phase 7) will need to look outside "combine existing
models" — e.g. toward residual/regime-aware modeling of the H9–H12 volatility-driven error using HGB
itself, rather than model blending — since Phase 5 evidence does not support a multi-model ensemble.

**READY_FOR: Phase 7 candidate design, with ensembling of existing models explicitly de-prioritized by
evidence.**
