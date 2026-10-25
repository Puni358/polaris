# POLARIS — Bottleneck Diagnosis Update (Post Stage 8.11A)
### Stage 8.1 Champion (frozen): Daytime MAE 36.188657 W/m² · nMAE 28.0688% · RMSE 64.219495 W/m² (now reconciled per your instruction)

**Evidence base for this update:** full `POLARIS_MASTER_HANDOFF.md`, `STAGE8_10A_FEASIBILITY_REPORT.md`, `STAGE8_11A_FEATURE_SEMANTICS_AUDIT.md`.

**Still missing from my evidence base:** `STAGE8_9A_FEASIBILITY_REPORT.md` was again not supplied. Your task brief also references a "Stage 8.7 DNI direct/diffuse architecture" as a failed experiment — I have no record of Stage 8.7 either. Both gaps are treated as unknowns below, not inferred.

---

## 1. Updated Executive Verdict

**What changed:** Stage 8.11A is a direct code-level audit (not a re-run of the failed 8.11 idea, but an inspection of the actual Stage 6.6 extraction script plus a 7-origin empirical spot-check) showing `lwp_latest`/`iwp_latest` are computed independently per horizon from the MEPS pressure-level forecast valid at t0+h, with substantial variation across H1–H24 in every sampled origin. This is a reasonably strong form of evidence — source-code inspection plus empirical confirmation — and I'm accepting it. My previous top hypothesis ("the champion cannot see the NWP's forecast trajectory of cloud microphysics") is **retracted**. It was built on an unverified assumption about feature semantics, and that assumption has now been directly falsified.

**New verdict: the strongest remaining, evidence-supported bottleneck is NWP forecast uncertainty about the cloud/atmospheric state — the champion is given the NWP's single deterministic cloud-microphysics trajectory (now confirmed horizon-resolved) but no representation of how *confident* that trajectory is.**

**Confidence: moderate-low.** This is the best-supported candidate in the record, but I want to be explicit about why it isn't higher: the supporting evidence (Stage 6.1's ρ = 0.767 spread–error correlation) is correlational, was generated with a different, currently-superseded control model (Stage 5.2, not Stage 8.1), and the one attempt to operationalize it failed for a specific, fixable reason (raw scalar GBDT input, causing overfitting) rather than a fundamental one. I cannot rule out that spatial cloud-position/phase error (Hypothesis 1) is equally or more important — three independent spatial formulations have failed, but none of them cleanly isolates "spatial displacement of the cloud system" as a mechanism, so that hypothesis remains genuinely open too. **I do not think the evidence is strong enough to call this a unique, confidently-identified bottleneck — it is the best-supported candidate among several that remain plausible.**

---

## 2. Updated Evidence Matrix

| Hypothesis | Status after 8.11A | Reasoning |
|---|---|---|
| 1. Cloud-location / spatial representativeness | Plausible but unverified | Unaffected by 8.11A (that audit only concerns temporal, not spatial, structure of LWP/IWP). Three formulations (5.4, 8.3, 8.5) have failed, but none isolates cloud-position/phase error specifically — they tested grid-offset snapshots, an external point station, and wind-aligned gradients, none of which directly represents "is the NWP's cloud system displaced from where it should be." Remains open. |
| 2. Cloud evolution / formation / dissipation | **Largely resolved / weakened as primary bottleneck** | 8.11A shows the champion already receives the NWP's own per-horizon forecast of cloud liquid/ice water path — i.e., its predicted formation/dissipation trajectory at the station footprint. What remains missing is not the trajectory itself but *confidence in* that trajectory (folds into Hypothesis 6). |
| 3. Radiative-transfer mapping error | Contradicted | Unchanged from prior review — Stage 7.2 directly ruled this out. |
| 4. Broken-cloud / 3-D radiative effects | Plausible but unverified | Not tested by any experiment that isolates sub-grid cloud fraction texture or cloud-edge radiative enhancement specifically; 7.4/8.8 tested layer structure and boundaries, not broken-cloud radiative geometry per se. |
| 5. Solar geometry / terrain interaction | Directly demonstrated, resolved | Unchanged — captured in champion via Stage 7.5. |
| 6. NWP cloud-state forecast uncertainty | **Strongest surviving candidate** | Stage 6.1: ensemble spread correlates with |residual| at ρ = 0.767 (p<10⁻¹⁵), highest in transitional cloud regimes (0.2–0.8 cover). This information is **not** among the 37 champion features — spread-derived candidates were tested and rejected only as raw GBDT scalar inputs, which is a narrow test of one exploitation mechanism, not of the information's value. |
| 7. Observation / measurement uncertainty | Plausible but unverified | Untested in the supplied record; unaffected by 8.11A. |
| 8. Temporal-context limitations (t−23…t0 window) | Plausible but unverified | Untested; unaffected by 8.11A. |
| 9. Vertical cloud structure (layering/altitude) | Contradicted for tested formulations; genuinely novel form still blocked | 7.4 (layer fractions) and 8.8 (base/top/thickness) both failed EVEN-CV, and — by analogy with the 8.11A finding for LWP/IWP — these features likely were also horizon-resolved (both drawn from the same causal D-1 18Z MEPS forecast archive), so the "static snapshot" excuse likely doesn't apply here either, though this is inference, not verified by an 8.11A-equivalent audit. The one genuinely untested form (true 65-model-level profile shape, Stage 8.10A) remains operationally blocked, not falsified. |
| 10. Aerosol optical depth (atmospheric turbidity) | **Genuinely untested, never ruled in or out** | Identified in Stage 8.2 as "CONDITIONAL (product exists / unenumerated)" — CAMS AOD550 was never taken to a forecasting experiment, only flagged as a candidate. No evidence for or against exists yet. Physically distinct mechanism (aerosol extinction of the direct beam) from everything tested so far. |

---

## 3. What the 37-Feature Champion Already Knows (updated)

Everything from the prior memo, **plus** the now-confirmed fact that its cloud-microphysics inputs (`lwp_latest`, `iwp_latest`) are **per-horizon forecast trajectories**, not t0 snapshots — the model already sees the NWP's own predicted evolution of column liquid/ice water path at each lead hour H1…H24, extracted causally from the D-1 18Z MEPS pressure-level archive (100% coverage, verified in Stage 8.0/6.6).

This closes a real gap in my previous analysis: the champion's cloud-evolution information is richer than I had assumed.

---

## 4. What It Still Does Not Know

Two candidates now lead, with the evidence tilted toward the first:

- **How uncertain the NWP's own cloud-state forecast is, at each horizon.** The champion sees one deterministic trajectory (the control-member forecast) but nothing about the spread of the 30-member MEPS ensemble around that trajectory — despite that spread being the single strongest quantitative correlate of error magnitude anywhere in the record.
- **Whether the cloud system the NWP forecasts is correctly positioned relative to the station**, as opposed to correct in bulk water content but spatially displaced — a distinct failure mode from "how much cloud water" that none of the tested spatial formulations cleanly isolates.

Lower-confidence but genuinely open: atmospheric turbidity/aerosol loading (never tested), broken-cloud sub-grid radiative texture (never tested), and observation/temporal-context limitations (never tested, though I have no positive evidence they matter either).

---

## 5. Why Previous Experiments Do or Do Not Address These Gaps

- **Stage 6.1 (ensemble spread as GBDT feature):** addresses Hypothesis 6 directly but narrowly — it tested only "add spread as a flat scalar input to the existing residual-correction GBDT," which failed on EVEN-CV (mild overfitting, 1/5 folds improved). This tests one specific exploitation mechanism, not the information's underlying value, which the correlation analysis (same stage) supports independently.
- **Stage 5.4 / 8.3 / 8.5 (spatial formulations):** each addresses a different slice of Hypothesis 1 — grid-offset snapshots, an off-site point station, and wind-aligned gradients — but none tests cloud-system position/phase error directly (e.g., cross-correlating the forecast cloud field's spatial pattern against a slightly shifted version of itself to quantify displacement). Their failures are informative about the specific representations tried, not about the underlying mechanism.
- **Stage 8.2 (CAMS identification):** only catalogued aerosol data as theoretically available; no forecasting experiment exists, so Hypothesis 10 is entirely untested, not rejected.
- **Stage 7.4 / 8.8 (vertical structure):** address Hypothesis 9 but not Hypothesis 4 (broken-cloud sub-grid radiative texture) — layer fraction and cloud-boundary altitude describe vertical extent, not horizontal cloud-field heterogeneity within a grid cell.
- **Stage 8.11A:** resolves Hypothesis 2 (or substantially weakens it as the *primary* bottleneck) by direct code/data audit — the strongest-quality evidence in the entire record, since it inspects ground-truth implementation rather than testing a downstream model outcome.

---

## 6. One Primary Next Route

### Proposed: Stage 8.12 — Ensemble-Derived Forecast-Confidence Features (reframed exploitation of already-audited Stage 6.1 signal)

**Exact missing information:** A representation of the NWP's own uncertainty about the cloud/atmospheric state at each forecast horizon — not the mean/control forecast (already present via per-horizon LWP/IWP and cloud_frac), but the spread of the 30-member MEPS ensemble around that forecast.

**Physical mechanism:** When ensemble members disagree about cloud state at a given lead time, this signals a genuinely less-predictable atmospheric situation (typically transitional cloud regimes) in which any single deterministic forecast — and any residual-correction model trained on it — has a structurally higher expected error. This isn't error the model can currently learn to reduce from the point forecast alone; it's information about the *reliability* of the point forecast it's already using.

**Why genuinely novel:** This is not a re-run of Stage 6.1. Stage 6.1 tested exactly one exploitation mechanism (spread as a flat additive GBDT feature) and that mechanism failed. The information itself — ensemble spread — is not among the 37 champion features under any formulation. A genuinely different route would use spread as a **conditioning/regime signal** rather than a raw additive feature: e.g., training the residual corrector with spread-derived sample weights, or producing a wider predictive interval / lower-confidence flag in high-spread regimes, rather than asking the same architecture to fold spread into a point-estimate correction the way it already tried and failed to.

**Causal feasibility requirements:** Already established in Stage 6.1 — 30-member MEPS ensemble, D-1 18Z issuance, 100% causal coverage across all 347 origins (262,800 member-hours audited). No new data-access work is required; this reuses an already-verified, already-extracted data source.

**Clean experiment design (conceptual, not to be executed yet):** Keep the frozen Stage 8.1 point-forecast pipeline exactly as is. Use ensemble spread only as (a) a regime label (e.g., high/medium/low spread tercile) for stratified evaluation and, if that shows a clean signal, (b) a sample-weighting or two-stage conditional architecture rather than a bolted-on scalar feature — explicitly avoiding the mechanism that already failed in Stage 6.1. Evaluate under the same 5-gate EVEN-CV protocol before any ODD access, exactly as every other stage in the record.

---

## 7. Fallback Routes (at most two)

**A. Cloud-system spatial displacement / phase-error feature.** Rather than grid-offset snapshots (5.4) or wind-aligned upstream/downstream differences (8.5), directly quantify how much the forecast cloud field appears shifted relative to some reference (e.g., cross-correlation of the forecast cloud fraction field against itself at short lead-time lags, or comparison of forecast cloud position against the persistence-extrapolated position of the last observed cloud state). This is a genuinely different formulation of Hypothesis 1 that neither prior spatial experiment tested.

**B. CAMS aerosol optical depth (AOD550) feasibility audit and, if warranted, forecasting experiment.** Identified in Stage 8.2 as a candidate but never taken further. Before any forecasting experiment, this needs a Stage-8.0-style empirical causal-availability audit (archive coverage, issuance-time alignment, spatial resolution mismatch against the ~2.5 km MEPS/30 m DEM grids already in use). This attacks a mechanism (direct-beam attenuation by atmospheric particulates) that nothing in the current 37 features captures at all.

---

## 8. Routes to Stop Pursuing

- **Per-horizon LWP/IWP trajectory work (the previous Stage 8.11 proposal)** — formally closed by 8.11A; the information is already present.
- **Model-level 65-layer vertical condensate profile (Stage 8.10B)** — unchanged from prior review, still blocked on archive availability at the required lead time.
- **Point-source spatial-transfer substitutes (external ground stations, single-pixel satellite retrievals)** — unchanged; Abisko and AVHRR point observations both failed for what looks like the same representativeness problem, and neither diagnoses the mechanism.
- **Additional static scalar NWP variables bolted onto the existing GBDT (native radiation outputs, wind-aligned spatial gradients, cloud-boundary geometry)** — unchanged; consistent pattern of the architecture saturating on tabular scalar inputs regardless of source.
- **Raw ensemble spread as a flat additive GBDT feature** — already tested and failed (Stage 6.1); any future ensemble-uncertainty work should use a different exploitation mechanism (Route 6 above), not repeat this one.

---

## 9. Final Recommendation

Pursue **Stage 8.12 (ensemble-derived forecast-confidence features, reframed exploitation)** as the primary next feasibility study, on the strength of the one clearly positive quantitative signal in the record (ρ = 0.767 spread–error correlation) that has never been properly exploited. But I want to be explicit that this is a best-supported guess among live candidates, not a resolved diagnosis: cloud-position/phase error (Fallback A) remains a live, untested-in-its-cleanest-form alternative, and aerosol optical depth (Fallback B) is a genuinely open mechanism with zero evidence either way. If Stage 8.12 fails to show a clean signal even with a reframed exploitation mechanism, that would be reasonably strong evidence the NWP-uncertainty hypothesis is not the dominant lever, and Fallback A should become the next priority — at that point spatial phase-error, not magnitude error, would be the most defensible remaining candidate in the record.
