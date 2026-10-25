# PHASE9 CANDIDATE DESIGN CHECKPOINT — PHASE 7

## Critical scoping note (read first)

The five handoff files contain **predictions, errors, and metadata** — they do NOT contain the raw
Stage 8.1 feature matrix (the actual 37 MEPS/geometry/wind columns fed to the HGB model). This limits
what can be *empirically tested* in this session to signals derivable from (date, horizon, prediction,
actual, error) alone: calendar/day-of-year, horizon, and cross-model prediction disagreement. Candidates
that require the raw cloud-fraction/LWP/IWP NWP trajectories are describable and rankable on theoretical
grounds, but **cannot be preregistered as a ready EVEN experiment without that additional data access**.
This distinction — tested-and-rejected vs. theoretically-promising-but-blocked-on-data-access — is load
bearing for the final recommendation below, and is reported explicitly rather than glossed over.

---
## Candidate 1: Calendar/shoulder-season residual bias correction (targets H9–H12, Apr–May)

1. **Error mode targeted:** the systematic negative bias in H9–H12 during April–May (−41 to −43 W/m²)
   found in Phase 3.
2. **Why it should improve that error:** if the bias is a stable, repeatable function of
   (day-of-year, horizon), subtracting a learned estimate of it should reduce both bias and MAE in that
   slice without touching other slices.
3. **Causal information at t0:** day-of-year and forecast horizon are both 100% known at t0 with zero
   leakage risk — this is the cleanest possible causal signal available.
4. **Existing Stage 8.1 features that could carry this regime:** day-of-year / solar-geometry features
   are already inputs to the champion HGB model (per the historical record, Stage 3A onward), so this
   candidate is not proposing new information, only a different way of using information already
   present.
5. **Observable before the horizon:** yes, trivially — the whole point of a calendar feature.
6. **Could it be learning noise:** yes, and this is exactly what the testing below was designed to
   check, since the seasonal-bias pattern was found by inspecting error broken into month × horizon
   cells with a moderate number of observations per cell (~10–90).
7. **Leakage prevention:** tested three ways — (a) coarse oracle binning in-sample, (b) forward-chaining
   chronological OOF, (c) interleaved (shuffled-by-date) K-fold OOF, discussed below.
8. **EVEN / OOF evaluation performed this session (diagnostic, not final):**
   - **In-sample oracle, coarse bins (month × H1-5/H6-12/H13-24):** MAE 36.19 → 36.54 (**+0.35, worse**).
   - **In-sample oracle, narrow scope (only Apr/May × H9–12 mean-bias subtracted, rest untouched):**
     MAE 36.19 → 35.92 (**−0.27**). This is the best-case, in-sample, no-OOF-penalty upper bound for the
     exact effect Phase 3 flagged, and it is *already below* the G1 gate threshold (≥ −0.50 W/m²) even
     before accounting for any OOF degradation.
   - **In-sample oracle, finest grain (month × individual horizon, ~10 obs/bin):** MAE 36.19 → 34.65
     (−1.54). This *looks* attractive but is a textbook small-bin overfitting signature — arbitrarily
     fine binning will always show an in-sample "improvement" by fitting per-bin noise; it is not
     evidence of a real, generalizable effect.
   - **Forward-chaining OOF** (expanding window, train on earlier dates only, small Ridge model on
     [day-of-year sin/cos, horizon sin/cos, H9–12 flag, shoulder×H9–12 interaction]): MAE **38.72 →
     46.39 (+7.67 W/m², 0/4 folds improved)**. Forward-chaining is structurally unable to learn a
     within-year seasonal pattern here, because with a single year of data, "predict a season using only
     earlier-in-the-year data" means every spring/summer fold is extrapolating into a season the model
     has effectively never seen — a genuine data-availability limitation, not just a modeling failure.
   - **Interleaved (shuffled-by-date) 5-fold OOF**, same model/features, giving the model fair exposure
     to all seasons in training: MAE **36.19 → 37.47 (+1.28 W/m², 0/5 folds improved, worst fold
     +1.82)**. This is the fairest test available and it is unambiguous: the correction hurts in every
     single fold.
9. **Gates:** fails G1 (no configuration tested clears −0.50 W/m² OOF) and fails G2 (0/5 and 0/4 folds
   improving in the two honest OOF schemes tested).

**Interpretation:** HGB is a flexible, nonlinear tree ensemble that already has access to day-of-year and
horizon (directly or via correlated features) as raw inputs. A small linear/ridge post-hoc correction on
the same information is not adding orthogonal signal — it is a much weaker model re-fitting variance HGB
has already captured, and in every honestly-validated configuration it makes things worse, not better.
**This candidate is empirically rejected, not merely deprioritized.**

---
## Candidate 2: Cross-model disagreement as a t0-available uncertainty/regime signal

1. **Error mode targeted:** identifying, at t0, which forecasts are likely to have large error (does not
   by itself correct direction/bias).
2. **Why it should help:** if models that were fit differently (HGB vs. the Stage 4.3 Dynamic Ensemble
   Hybrid, which blends different GBDT variants) disagree more on a given forecast, that disagreement may
   flag genuinely harder atmospheric situations — consistent with the volatility-driven error mode found
   in Phase 3.
3. **Causal information at t0:** both models' predictions are generated at t0 from t0-available NWP
   inputs, so their disagreement is itself t0-available — no leakage.
4. **Existing features:** none needed beyond predictions already in the handoff files.
5. **Observable before horizon:** yes.
6. **Could it be noise:** tested directly (below) rather than assumed.
7. **Leakage prevention:** disagreement is computed only from t0-generated forecasts, not from actuals.
8. **Evaluation performed this session:** correlation between |HGB − Dynamic Ensemble Hybrid| prediction
   disagreement and |HGB error|, on the 173-date daytime set: **r = 0.41** (moderate, real, and
   consistent with the volatility-driven story). However, correlation between *signed* disagreement and
   *signed* HGB error is weak (Pearson −0.12, Spearman −0.07, p<0.001 but small effect) — disagreement
   tells you a forecast is likely to be *harder*, not which *direction* to correct it.
9. **Gates:** not directly testable against G1–G4 as a standalone MAE-reducing intervention, because a
   magnitude-only signal with no reliable direction cannot, by itself, produce a bias correction. It
   would need to be paired with something else (e.g. as an input feature in a full retrain, or as a
   confidence flag for downstream use) to plausibly move MAE.

**Interpretation:** this is a real, legitimate, t0-causal signal — the first one in this session that
*didn't* fail its empirical check — but it is a partial ingredient (uncertainty flag), not a complete
candidate. It's the strongest evidence in this session that "hard instances" are identifiable in advance,
which supports investing effort in Candidate 3 rather than abandoning regime-awareness altogether.

---
## Candidate 3: NWP-forecast-volatility-aware residual/regime modeling (theoretical — blocked on data access)

1. **Error mode targeted:** the H9–H12 error mode itself, via its strongest correlate — within-day
   irradiance volatility (r = 0.73 with H9–H12 MAE, from Phase 3).
2. **Why it should improve that error:** if the *predicted* (not actual) cloud fraction/LWP/IWP
   trajectory across daytime horizons — already part of the Stage 8.1 / Stage 3B feature lineage —
   shows high predicted variability for a given origin, that is a t0-available proxy for the same
   broken-cloud/transition regime that Phase 3 showed (using actuals, post-hoc) drives the worst errors.
3. **Causal information at t0:** the NWP forecast itself is fully available at t0 by construction — this
   would be causally valid *if* the predicted variability is a decent proxy for the true variability.
4. **Existing features:** MEPS 2D cloud fraction, LWP, and IWP are already Stage 3B+ inputs to the
   champion lineage — this reuses existing approved feature sources, it does not reopen closed feature
   research.
5. **Observable before horizon:** yes, in principle — this is exactly the caveat that matters.
6. **Could it be noise:** the specific concern here is different from Candidate 1's: the NWP's own
   *predicted* variability might be systematically smoother than reality (that's arguably part of why
   these are the hardest events for HGB in the first place — if the NWP cloud forecast cleanly captured
   the transition, HGB would likely already be using it correctly). This needs to be checked empirically
   before trusting the signal, not assumed.
7. **Leakage prevention:** straightforward in principle (forecast-only inputs), but must be verified once
   the actual feature values are available.
8. **Evaluation performed this session:** **not performed** — the raw MEPS cloud fraction/LWP/IWP time
   series are not present in the five handoff files, only final predictions and errors.
9. **Gates:** cannot be assessed against G1–G6 without the underlying feature matrix.

**Status: theoretically the best-targeted candidate (it directly addresses the strongest correlate found
in Phase 3, and Candidate 2's positive result is indirect supporting evidence that "hard instance"
detection is possible from t0 information), but it is NOT ready for a preregistered EVEN experiment.**
The concrete blocker is data access, not weak evidence.

---
## Ranking

| Rank | Candidate | Status |
|---|---|---|
| **A — theoretically best, currently blocked** | NWP-forecast-volatility-aware regime/residual modeling (Candidate 3) | Best-targeted hypothesis; requires the raw Stage 8.1 feature matrix (not in the five handoff files) before it can be preregistered. |
| **B — real but partial** | Cross-model disagreement as an uncertainty signal (Candidate 2) | Empirically confirmed (r=0.41 with abs error) but magnitude-only; not a standalone MAE-reduction mechanism on its own. |
| **C — empirically rejected** | Calendar/shoulder-season residual bias correction (Candidate 1) | Tested three ways with honest OOF; fails G1/G2 in every non-overfit configuration; actively hurts performance in the fairest test (interleaved CV: +1.28 W/m², 0/5 folds improved). |

Other candidates named in the brief (horizon-specific H9–H12 specialized model, mixture-of-experts within
the HGB family, interaction-based correction) all reduce, on inspection, to the same underlying signal
Candidate 1 already tested (day-of-year/horizon) unless they also incorporate the NWP volatility signal —
in which case they inherit Candidate 3's status (theoretically motivated, blocked on data access) rather
than being independently new options. A horizon-gated ensemble bringing in TimesFM/Real-AROME for H1–H3
(raised in the historical record's own open questions) was considered and deprioritized: H1–H5 contributes
only 5.2% of total error (Phase 3), so even a large relative improvement there has low expected value
against the ~28% nMAE target, and Phase 5 already showed these models are not reliably better once
evaluated on matched dates.

---
## Recommendation

**No candidate in this session meets the bar for a preregistered EVEN experiment.** Candidate 1 — the
one candidate fully testable with the current handoff files — was tested rigorously (in-sample oracle at
multiple granularities, forward-chaining OOF, interleaved OOF) and is **empirically rejected**: it does
not clear the G1 improvement threshold under any non-overfit configuration, and it actively degrades
performance under the two honest out-of-fold validations performed. Per Phase 7/Phase 10's explicit
guidance, this is reported as a negative result rather than forced into an experiment.

The one candidate with real theoretical promise and partial empirical support (Candidate 3, reinforced by
Candidate 2's positive but partial result) **cannot be preregistered today** because it requires access to
data outside the five audited handoff files — specifically the raw MEPS cloud fraction/LWP/IWP forecast
trajectories already used inside the Stage 8.1 feature set. This is a data-access request, not a new
feature-research route, and does not reopen Stage 6–8 (it reuses already-approved feature sources in a
new modeling structure, per the phase 9 mandate).

**Proposed next step:** request the Stage 8.1 training feature matrix (or equivalently, per-origin MEPS
cloud fraction/LWP/IWP forecast trajectories for the same 173+173 EVEN/ODD origins) so that Candidate 3
can be built and evaluated causally. Until that data is available, **PHASE9_NO_ROBUST_IMPROVEMENT
applies to the candidate space testable with current files.**

**Status: PHASE 7 COMPLETE. No ODD access used at any point. No EVEN experiment preregistered — evidence
does not support forcing one.**
