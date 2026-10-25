# POLARIS — Independent Scientific Error-Bottleneck Review
### Stage 8.1 Champion (frozen): Daytime MAE 36.188657 W/m² · nMAE 28.0688%
*(RMSE reported as 54.912301 W/m² in your brief and the 8.10A report; 64.219495 W/m² in the master handoff's official ODD leaderboard entry — unreconciled discrepancy, flagged not resolved.)*

**Evidence base:** `POLARIS_MASTER_HANDOFF.md` (full, 2,063 lines) and `STAGE8_10A_FEASIBILITY_REPORT.md`. `STAGE8_9A_FEASIBILITY_REPORT.md` was **not supplied and not found embedded elsewhere** — treated as a genuine gap, not inferred.

---

## 1. Executive Verdict

**Most likely bottleneck: NWP cloud-evolution forecast error — specifically, POLARIS does not currently give its model any representation of how MEPS's own cloud/microphysical state is predicted to *change* over the 24-hour horizon.** Every feature the champion currently uses that touches clouds (`cloud_frac`, `lwp_latest`, `iwp_latest`, `U700/V700`) describes the atmosphere *at or near t0*, not the NWP's forecast trajectory of that state through H1…H24.

**Confidence: moderate — this is an inference, not a directly demonstrated result.** No experiment in the record isolates "temporal cloud-evolution information" as a variable and tests it cleanly; the case is built by elimination (ruling out radiative-transfer mapping and terrain, which *were* directly tested) plus one strong correlational datum (ensemble spread ↔ error).

**Why this over the alternatives:**
- Radiative-transfer mapping was **directly tested and ruled out** (Stage 7.2: feeding MEPS's own RRTMG-derived surface SW output produced no improvement — the champion's empirical GBDT mapping already extracts equivalent information from `clearsky_ghi` + `cloud_frac` + LWP/IWP).
- Solar-geometry/terrain interaction was **directly tested and resolved** (Stage 7.5: real but small, concentrated in low-sun-angle transition hours; now inside the champion).
- Spatial representativeness has failed **three independent formulations** (5.4 grid-offset probes, 8.3 external station, 8.5 wind-aligned advection features) — a consistent pattern, though each failure alone is not proof of irrelevance.
- Vertical cloud structure/geometry has failed **two independent formulations** (7.4 layer fractions/centroids, 8.8 base/top/thickness) — also consistent but not conclusive, and the one formulation that could be genuinely different (Stage 8.10A model-level condensate profile) is **operationally blocked**, not falsified.
- The single strongest quantitative signal in the whole record is Stage 6.1's finding that MEPS ensemble spread correlates with |residual| at ρ = 0.767 (p < 10⁻¹⁵) — direct evidence that when the driving NWP is less certain about the atmospheric/cloud state, POLARIS's forecast error grows. This points at the *predictability ceiling of the NWP's cloud forecast itself*, not at a missing static feature.

---

## 2. Evidence Matrix

| Hypothesis | Evidence For | Evidence Against | Strength | Status |
|---|---|---|---|---|
| 1. Cloud-location / spatial representativeness | 5.4 spatial probes improved EVEN-CV but failed ODD (overfit, not generalized); 8.3 Abisko (3.23 km, −287 m) failed all gates; 8.5 wind-aligned upstream/downstream cloud fraction failed 3/5 gates | No spatial formulation has ever passed ODD; repeated failure could mean the *representations* tested were wrong, not that location info is worthless | Indirectly supported (pattern of failure, not proof) | Plausible but unverified |
| 2. Cloud evolution (t0 → t0+24h) | 6.4 MEPS forecast-revision trajectory passed the primary MAE gate (−0.27 W/m²) but failed fold-stability gates — real signal, unstable exploitation; champion's cloud features (`lwp_latest`, `iwp_latest`) are t0 snapshots, not per-horizon trajectories | No experiment has cleanly isolated horizon-indexed cloud-state trajectory as a feature; 8.5's *temporal tendency* feature was bundled with spatial features and can't be separated from that failure | Indirectly supported | Plausible but unverified (never cleanly isolated) |
| 3. Radiative-transfer mapping error | None found | 7.2: feeding MEPS's own surface-SW radiative-transfer output produced **no improvement** — redundant with existing empirical features | Directly demonstrated (against) | Contradicted |
| 4. Broken-cloud / 3-D structure effects | Physically plausible mechanism (partial cloud, cloud-edge brightening) never directly tested | 7.4 (layer fractions/centroids) and 8.8 (base/top/thickness) both failed EVEN-CV gates; genuinely novel test (8.10A model-level profile shape) blocked by archive gap, not tried | Directly tested (2 formulations) and rejected; deeper test unavailable | Contradicted for tested formulations; unverified for untested ones |
| 5. Solar-geometry / terrain interaction | 7.5 terrain-horizon features passed all 5 EVEN gates and improved held-out ODD (−0.39 to −0.44 W/m²), concentrated at low-elevation transition hours | Effect is small and now captured in the champion; residual error after 7.5 is still ~36 W/m² | Directly demonstrated | Directly demonstrated, and already resolved (no longer "missing" info) |
| 6. NWP cloud-state forecast error (predictability ceiling) | 6.1: ensemble spread ↔ |residual| Spearman ρ = 0.767 (p<10⁻¹⁵); spread is highest in transitional cloud regimes (0.2–0.8 cover, 41.9 W/m² spread) vs clear/overcast (23.8 / 14.3 W/m²) | Direct-feature use of spread caused GBDT overfitting (6.1 EVEN-CV failed); correlational, not causal | Indirectly supported (strong correlation) | Indirectly supported |
| 7. Observation / measurement uncertainty | Not tested anywhere in the supplied record | — | None | Plausible but unverified |
| 8. Temporal-context information bottleneck (t−23…t0 window) | 14 ground-context statistics (`ctx_*`) already summarize the full 24h lookback at multiple scales | No experiment tests a longer lookback window or alternative temporal encodings | None found | Plausible but unverified |
| 9. Other — column-integrated vs. per-horizon cloud microphysics gap | `lwp_latest`/`iwp_latest` are single t0 snapshots (Stage 6.6 naming and usage); `fc_cloud_cover` appears to be horizon-varying but coarse (binary/fractional cover, not water/ice path); no experiment has fed per-horizon LWP/IWP trajectory | Not directly tested — this is a structural observation about the feature set, not a result | Plausible, structurally grounded | Plausible but unverified |

---

## 3. What POLARIS Already Knows

The frozen Stage 8.1 champion (37 features) already captures, at forecast origin t0:
- **Clear-sky solar potential and geometry**: `solar_elevation`, `solar_zenith`, `clearsky_ghi`.
- **Local terrain shading**: 360° DEM-derived horizon obstruction, terrain-adjusted clear-sky GHI (Stage 7.5).
- **Column-integrated cloud microphysical state at t0**: liquid/ice water path (`lwp_latest`, `iwp_latest`) via surface-truncated pressure-level integration (Stage 6.6), plus coarse NWP cloud-cover forecast (`fc_cloud_cover`, `cloud_frac`).
- **Synoptic-scale steering flow**: 700 hPa free-atmosphere wind components (`U700`, `V700`) — a proxy for large-scale transport direction, not cloud state itself (Stage 8.1).
- **Recent ground-truth volatility**: 14 statistics over the trailing 24h (std, slope, max/min diff, clear-sky-index std, last observation).
- **Model-internal state**: Stage 4 base forecast and its disagreement/fold diagnostics.

Radiative-transfer mapping from cloud state to surface irradiance is effectively saturated — giving the model the NWP's *own* RT-scheme output (7.2) added nothing beyond what the empirical GBDT already infers from `clearsky_ghi` + cloud features.

---

## 4. What POLARIS Still Does Not Know

The most defensible gap, built by elimination and one structural observation:

**How the cloud/atmospheric state at t0 is expected to *change* by each future hour t0+h.** The champion's cloud-microphysics features are anchored to t0 ("latest"); the only genuinely future-varying atmospheric inputs are the coarse NWP cloud-cover forecast and a static synoptic wind vector, neither of which encodes a forecast trajectory of cloud water/ice content. Secondarily, and less certainly: whether the *true* spatial location of cloud relative to the station and the fine 3-D cloud geometry matter, given they have failed every tested representation to date without a formulation that unambiguously isolates the physical mechanism.

---

## 5. Why Previous Experiments Did Not Resolve It

- **Stage 5.4 / 8.5 (spatial probes, wind-aligned gradients):** tested spatial cloud information as *static grid-offset snapshots* or simple upstream/downstream differences at t0. Neither tested whether the spatial cloud field's *future* position (i.e., where the model predicts the cloud to be at t0+h) matters — they tested "where is the cloud now, relative to the station," not "where will the cloud be."
- **Stage 8.3 (Abisko):** tested whether an external station's *observed* direct/diffuse ratio transfers to Nuolja. This tests spatial transferability of ground observations, not NWP-forecast spatial/temporal cloud information — a different question than 1/2/4 above, and its failure doesn't bear directly on NWP-based cloud evolution.
- **Stage 6.1 (ensemble spread):** demonstrated that forecast uncertainty correlates with error, but tested spread only as a static scalar GBDT input — not as a mechanism for representing evolution or for conditioning predictions. The failure was an overfitting/feature-utility failure, not a refutation of the underlying signal (which the correlation analysis independently supports).
- **Stage 6.4 (forecast revision trajectory):** closest existing test to "cloud evolution," but it tested *run-to-run forecast revision* (how MEPS's forecast of t0 changed across earlier issuance times), not the *forward trajectory* the current forecast predicts for t0+1…t0+24. It showed real but unstable signal — consistent with genuine information being present but poorly captured by the tested feature construction.
- **Stage 7.4 / 8.8 (vertical structure):** tested layer-resolved cloud fraction and cloud-boundary altitude at/near t0 — a structural (3-D) hypothesis, not a temporal (evolution) one. Their failure doesn't bear on the evolution hypothesis.
- **Stage 8.10A (model-level condensate):** the one route that could have tested genuine vertical *and* temporal novelty is operationally blocked — the causally required D-1 18Z archive doesn't exist; the alternative D-1 00Z archive exists but imposes an 18-hour longer lead time, which changes the information set too much for a clean test.

---

## 6. Highest-Value Next Research Route

### Stage 8.11 (proposed) — Per-Horizon MEPS Cloud Microphysics Forecast Trajectory

**What new information it provides:** Instead of extracting LWP/IWP at a single "latest" (t0) snapshot as Stage 6.6 did, extract the MEPS pressure-level LWP/IWP integration *at each forecast horizon h* (i.e., `lwp_forecast(t0+h)`, `iwp_forecast(t0+h)` for h = 1…24), so the model sees the NWP's own predicted cloud-water/ice trajectory across the forecast window, not just the current state.

**Why it is genuinely different from prior work:**
- Different from Stage 6.6 (t0-only snapshot) and Stage 6.4 (forecast revision across issuance times, not forward horizon) — this is the forward trajectory neither tested.
- Different from Stage 7.4/8.8 (vertical *layer* structure at a point in time) — this is temporal, not vertical, structure.
- Different from Stage 8.10A (blocked model-level 65-layer profile *shape*) — this reuses the already-verified, already-causal pressure-level integration pipeline from Stage 6.6, at a coarser (column-integrated) but operationally available resolution.

**Why it directly attacks the suspected bottleneck:** If the dominant remaining error source is uncertainty about how clouds evolve over the horizon, giving the model the NWP's own explicit forecast of that evolution (rather than forcing it to infer evolution implicitly from `horizon_hour` and a static t0 snapshot) is the most direct test available.

**What would constitute a scientifically clean test:**
- Confirm empirically (do not assume) whether `lwp_latest`/`iwp_latest` in the existing pipeline are in fact t0-only values repeated across all 24 horizon rows, or already horizon-varying — this must be verified against the actual feature-extraction code before designing Stage 8.11, since the entire premise depends on it.
- Reuse the exact frozen Stage 6.6 pressure-level surface-truncation methodology (`p_sfc` boundary truncation, D-1 18Z issuance) — already verified 100% causal and complete for `meps_det_pl` at 347/347 origins (Stage 8.0), avoiding the archive gap that blocked 8.10A.
- Candidate feature set should remain compact (e.g., `lwp_forecast_h`, `iwp_forecast_h`, and their first differences from t0, ≤5 features) to control against the overfitting pattern seen in 6.1 and 8.5.
- Evaluate under the same 5-fold EVEN forward-chaining CV and the same 5 predeclared acceptance gates used throughout Stage 7–8, with ODD held out until EVEN gates pass.

**Major causal/operational risks:**
- If `lwp_latest`/`iwp_latest` turn out to already be horizon-varying in the current pipeline, this route collapses to a re-test of something already implicitly tried, and the premise needs revisiting before running anything.
- MEPS's own cloud-microphysics forecast skill degrades with lead time; by hour 24 the "forecast trajectory" may carry little more information than persistence of the t0 value, which would show up as no improvement at long horizons specifically (worth checking per-horizon, not just aggregate).

---

## 7. Alternative Routes (ranked below the primary)

**A. Ensemble-spread-based uncertainty conditioning (not a raw GBDT feature).** Stage 6.1 established a strong correlation between MEPS ensemble spread and |residual| but failed when spread was added as a flat tabular input. A genuinely different formulation — using spread to produce prediction intervals, or to gate/weight between a "confident" and "uncertain" regime model — attacks the NWP-predictability-ceiling hypothesis (Hyp. 6) without repeating the exact failed mechanism.

**B. Latency-engineered satellite cloud observation (NRT, not standard science L2).** Stage 8.2/8.4 established that VIIRS/NWC-SAF cloud products exist with reasonable physical coverage (64.8% VIIRS constellation union) but are operationally non-causal because standard L2 products publish 3–13 hours after acquisition. If a genuinely near-real-time feed (cloud mask rather than full science product) can be verified to publish within the causal window, this attacks spatial representativeness (Hyp. 1) via direct observation rather than NWP inference — a materially different data pathway than the AVHRR/Abisko routes already rejected.

---

## 8. Routes We Should Stop Pursuing

- **Model-level 65-layer vertical condensate profile (Stage 8.10B)** — blocked at the required D-1 18Z lead time (0/347 archive coverage); the only causal alternative (D-1 00Z) changes the lead-time protocol too much to constitute a clean continuation. Not worth pursuing until/unless the archive gap is independently resolved.
- **Point-source spatial-transfer substitutes (external ground stations, single-pixel satellite retrievals)** — Abisko (8.3) and AVHRR point obs (6.2) both failed for what looks like the same underlying reason: a single off-site point measurement doesn't represent the cloud field over Nuolja. Further point-substitution experiments are low-value without first addressing *why* representativeness fails, which none of the current experiments diagnose.
- **Additional static scalar NWP variables bolted onto the existing GBDT** — native MEPS radiation (7.2), spatial cloud gradients (8.5), and cloud-boundary geometry (8.8) all failed for a consistent reason: the architecture appears to already saturate on tabular scalar cloud/radiation inputs at t0. More of the same feature *type* is unlikely to move the needle regardless of source.
- **Target reformulation (kt / clear-sky index, Stage 7.3)** — its failure was diagnosed as a numerical-stability artifact near sunrise/sunset, not an information-content issue; it doesn't inform the bottleneck question either way and shouldn't be revisited on these grounds.

---

## 9. Final Recommendation

Run **Stage 8.11 — Per-Horizon MEPS Cloud Microphysics Forecast Trajectory**, but only after a precursor verification step: confirm from the actual feature-extraction code whether `lwp_latest`/`iwp_latest` are truly single t0 snapshots repeated across horizons, since the entire scientific rationale for this route depends on that not yet being the case. If confirmed, extract MEPS pressure-level LWP/IWP integration per forecast horizon (not just at t0) using the already-verified Stage 6.6 causal pipeline (D-1 18Z, 100% archive coverage), keep the candidate feature set compact (≤5 features), and evaluate under the standard 5-gate EVEN-CV protocol before any ODD access. This is the one proposed direction in the record that is simultaneously causally available today, genuinely untested, and directly targeted at the strongest evidence-based hypothesis — that the remaining error is bounded by the model's blindness to the NWP's own predicted cloud-state *evolution*, not by spatial mismatch, 3-D cloud geometry, or radiative-transfer mapping (the latter of which has already been directly ruled out).
