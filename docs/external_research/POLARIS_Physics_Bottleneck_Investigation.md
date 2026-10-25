# POLARIS — Independent Atmospheric-Physics Bottleneck Investigation

**Champion (frozen, unchanged):** Stage 8.1, ODD MAE 36.188657 W/m², nMAE 28.0688%, RMSE 64.219495 W/m², Bias +1.439399 W/m², Night MAE 0.

**Evidence-integrity note up front:** Stages 8.6, 8.7 (as a standalone stage), and 8.9A referenced in your brief do not appear in the master handoff I was given. They are marked **REQUIRES ARTIFACT VERIFICATION** throughout and are *not* used as evidence that any hypothesis is closed. Everything else below is traceable to a section of the master handoff you uploaded.

---

## 1. Remaining Physical Error Decomposition

| # | Error source | Info needed to observe/predict it | Does POLARIS have it? | Experiment(s) that touched it | Tested the *representation* or the *hypothesis*? | Genuinely untested remainder |
|---|---|---|---|---|---|---|
| A | Cloud position error | Independent spatial cloud observation/motion tracking vs. NWP forecast position | No independent cross-check; only NWP's own gridded field | 5.4 (grid-offset probes), 8.5 (wind-aligned spatial gradients) | Representation only — both used the NWP's *own* spatial field, never an independent observation to check if that field is right | **Yes — independent position verification never attempted** |
| B | Cloud timing error | High-time-resolution cloud tracking / nowcasting vs. NWP arrival time | No | 6.4 (forecast-revision trajectory) tests run-to-run consistency, not ground-truth timing | Adjacent, not equivalent — revision consistency ≠ actual arrival-time verification | **Yes** |
| C | Cloud amount error | Column water/ice content, cloud fraction | Yes — LWP/IWP (horizon-resolved, confirmed by 8.11), `fc_cloud_cover`, `cloud_frac` | 6.6 (accepted) | Hypothesis tested and largely resolved | Low priority — best-covered error mode in the record |
| D | Cloud optical-property error (beyond mass content: effective radius, optical depth) | MEPS's internal radiative-transfer output or explicit optical-property fields | Indirectly — Stage 7.2 fed MEPS's own RT-scheme surface output (which internally uses these properties) | 7.2 (rejected — redundant) | Hypothesis-level: giving the *full* RT output (built from these properties) added nothing | Reasonably ruled out as a large remaining source, via 7.2's redundancy finding |
| E | Cloud phase error (liquid vs. ice) | Separate liquid/ice partitioning | Partially — LWP and IWP are separate features | 6.6 (accepted) | Partial — phase is split but never tested as an isolated hypothesis | Not cleanly isolated, but partially addressed |
| F | Cloud vertical-structure error | Layer-resolved cloud fraction, base/top/thickness, or full profile shape | No — tested and rejected at coarse granularity | 7.4 (layer fractions/centroids), 8.8 (base/top/thickness) | Two representations tested and rejected; deeper form (8.10A model-level profile shape) causally blocked, not falsified | Genuinely untested at the profile-shape level; blocked, not resolved |
| G | Aerosol attenuation | Aerosol optical depth / total column water vapor | No | Identified as candidate only (Stage 8.2: CAMS "CONDITIONAL, product exists / unenumerated") | **Never taken to a forecasting experiment in the verified record** | **Yes — fully untested per master handoff** (your brief's "8.6" claim unverified) |
| H | Radiation-model (RT mapping) error | MEPS's own cloud→flux radiative-transfer output | Yes, tested directly | 7.2 (rejected — redundant) | Hypothesis directly tested | Ruled out as dominant remaining source |
| I | Terrain/horizon representation | Local 360° horizon geometry | Yes | 7.5 (accepted) | Hypothesis tested and resolved for static shading | Resolved for the tested mechanism; terrain × broken-cloud interaction (item K below) not tested |
| J | Boundary-layer / mesoscale circulation | Local valley/lake circulation, low-level cloud/fog formation distinct from synoptic (700 hPa) transport | No — only synoptic-scale wind (U700/V700) and 10 m surface wind (rejected, 5.4) are in the record | 5.4 (10 m wind — rejected), 8.1 (700 hPa steering wind — accepted) | Neither tests genuine local mesoscale circulation (e.g., lake-effect or terrain-channeled flow near Torneträsk) | **Yes — genuinely untested**, and physically plausible given Nuolja's complex terrain |
| K | Other (e.g., snow-cover/surface-albedo multiple-reflection effects under high-latitude snow cover) | Surface albedo / snow-cover time series | Not identified anywhere in the record | None | — | Untested; flagged as speculative, lower priority |

---

## 2. What POLARIS Has Already Ruled Out (verified against the handoff)

- **Radiative-transfer mapping (H)** — directly tested (7.2), redundant, not the bottleneck.
- **Terrain/solar-geometry shading (I)** — directly tested (7.5), resolved, now inside the champion.
- **Cloud amount / column water-ice content, including its horizon evolution (C)** — directly tested (6.6, confirmed horizon-resolved by 8.11), largely captured.
- **Vertical structure at coarse resolution (F, partial)** — two independent representations (7.4, 8.8) tested and rejected, though the deeper model-level form remains blocked rather than falsified.
- **Raw ensemble spread as a flat GBDT feature** — tested (6.1) and rejected as *that specific mechanism*; the underlying correlation (ρ=0.767) with error is not rejected.

## 3. What Remains Genuinely Unresolved

- **Cloud position/timing error (A, B)** — no experiment has used an observation *independent of the NWP's own field* to check whether the forecast cloud system is correctly located or correctly timed. This is the one major hypothesis class with essentially zero direct testing in the verified record.
- **Aerosol attenuation (G)** — identified, never tested.
- **Boundary-layer/mesoscale circulation (J)** — never identified as a hypothesis or tested.
- **NWP forecast confidence/uncertainty, properly exploited (carried over from prior review)** — information exists (ensemble spread), never successfully used.

---

## 4. Top 5 Candidate Information Sources

### #1 — Independent cloud-position/motion observation (satellite cloud-motion vectors or equivalent nowcasting product)
| Axis | Score | Note |
|---|---|---|
| Physical novelty | HIGH | Targets position/timing error, a mode nothing in the record directly checks |
| Causal feasibility | MEDIUM | Standard science-product satellite data showed 3–13h dissemination latency in Stage 8.4 (for cloud-property products); whether a motion-vector product has different latency is unverified |
| Historical coverage | MEDIUM | VIIRS constellation union gave 64.8% usable origins (Stage 8.4); polar-night gaps apply |
| Spatial representativeness | HIGH | Direct imagery over/near the station, unlike point-station substitutes that already failed (8.3) |
| Information independence | HIGH | Not reconstructable from any of the 37 existing features — none of them cross-checks the NWP's cloud field against an outside observation |
| Operational feasibility | MEDIUM | At 68°N, geostationary viewing geometry is poor (near-limb); polar-orbiter revisit is intermittent — needs a dedicated feasibility audit |
| Implementation complexity | HIGH | Motion-vector extraction, spatial/temporal alignment, new pipeline |
| Evidence confidence | LOW–MEDIUM | Mechanism plausible and untested; no positive or negative experimental evidence yet |

### #2 — NWP ensemble forecast-confidence conditioning (reframed exploitation of Stage 6.1 data)
| Axis | Score | Note |
|---|---|---|
| Physical novelty | MEDIUM | Same underlying ensemble, different exploitation mechanism |
| Causal feasibility | HIGH | 100% causal coverage already verified (Stage 6.1) |
| Historical coverage | HIGH | 262,800 member-hours audited |
| Spatial representativeness | HIGH | Same grid as champion |
| Information independence | MEDIUM | Correlated with, but not identical to, the point forecast already in use |
| Operational feasibility | HIGH | No new data acquisition needed |
| Implementation complexity | MEDIUM | Needs a genuinely different exploitation mechanism than the one that already failed |
| Evidence confidence | MEDIUM–HIGH | ρ=0.767 correlation with error is the strongest single quantitative signal in the whole record |

### #3 — Aerosol optical depth / atmospheric turbidity (CAMS AOD550, TCWV)
| Axis | Score | Note |
|---|---|---|
| Physical novelty | HIGH | Mechanism (particulate extinction of direct beam) entirely uncaptured elsewhere |
| Causal feasibility | MEDIUM | Never empirically audited (Stage 8.2 only flagged it as a candidate) |
| Historical coverage | MEDIUM (unverified) | Needs a Stage-8.0-style archive audit before anything else |
| Spatial representativeness | LOW–MEDIUM | ~40 km × 15 km grid, coarse relative to 2.5 km MEPS / 30 m DEM already used |
| Information independence | HIGH | Not reconstructable from any existing feature |
| Operational feasibility | MEDIUM | Unknown until audited |
| Implementation complexity | LOW–MEDIUM | Straightforward scalar feature if available |
| Evidence confidence | LOW | Zero experimental evidence either way in the verified record |

### #4 — Local boundary-layer / mesoscale circulation near Nuolja
| Axis | Score | Note |
|---|---|---|
| Physical novelty | MEDIUM–HIGH | Distinct from synoptic 700 hPa transport already captured |
| Causal feasibility | MEDIUM | Plausibly extractable from existing 2.5 km MEPS fields, but no specific variable has been identified or audited |
| Historical coverage | UNKNOWN | No audit performed |
| Spatial representativeness | MEDIUM | High-resolution local grid could represent boundary-layer effects reasonably, in principle |
| Information independence | MEDIUM | Some overlap with existing terrain/wind features; a genuine circulation signal would be distinct |
| Operational feasibility | LOW–MEDIUM | No formulation exists yet — would need scoping before a feasibility audit even makes sense |
| Implementation complexity | HIGH | Undefined feature family |
| Evidence confidence | LOW | Speculative but physically grounded given the complex terrain (mountain station, adjacent lake) |

### #5 — True model-level vertical cloud-condensate profile shape (Stage 8.10B route)
| Axis | Score | Note |
|---|---|---|
| Physical novelty | MEDIUM | Distinct from column-integrated LWP/IWP already in use, since shape ≠ integral |
| Causal feasibility | LOW | 0/347 at the required D-1 18Z lead (Stage 8.10A); only the 00Z alternative exists, with an 18h lead-time penalty that contaminates the test |
| Historical coverage | HIGH (at wrong lead time) | 347/347 at D-1 00Z, but not a clean continuation of the benchmark |
| Spatial representativeness | HIGH | Same MEPS grid |
| Information independence | MEDIUM | Column integrals already redundant per 8.10A; only vertical shape would be new |
| Operational feasibility | LOW | Blocked |
| Implementation complexity | HIGH | 65-level reconstruction, >1.46 TB storage burden |
| Evidence confidence | LOW | Blocked, not falsified |

---

## 5. Strongest Candidate

**#1 — Independent cloud-position/motion observation.** It is the only major hypothesis class in the entire record that has never been tested in any form — not the representation, not the underlying physical question. Every other surviving hypothesis (ensemble uncertainty, aerosol, mesoscale circulation) has either partial supporting evidence or at least a defined feasibility path from prior stages; cloud displacement/timing has neither, despite being physically one of the more intuitive ways a single-point 24h forecast could go wrong (a frontal boundary or cloud band arriving a few hours early/late or a few kilometers off-track would degrade a point forecast in exactly the way a magnitude-only correction cannot fix).

## 6. Strongest Competing Hypothesis

**#2 — NWP ensemble forecast-confidence conditioning.** This has actual positive quantitative evidence (ρ=0.767) behind it, which #1 currently lacks entirely. It is the more evidence-backed candidate; #1 is the more physically distinctive and clearly-unaddressed one. These are not mutually exclusive — ensemble spread may itself be elevated specifically *because* of position/timing uncertainty in the ensemble members, in which case they could be two views of the same underlying phenomenon rather than competing explanations.

## 7. Evidence That Would Discriminate Between Them

Before committing to any new data pipeline, a cheap diagnostic (analysis only, no new data, no ODD access) could help distinguish:
- Stratify existing Stage 8.1 EVEN-fold residuals by ensemble-spread tercile (data already extracted in Stage 6.1) **and separately** by whether the forecast origin falls near a synoptic transition (e.g., large day-over-day change in `fc_cloud_cover` or `U700/V700`, both already in the feature set) as a rough proxy for "displacement-prone" situations.
- If residual error concentrates specifically around transition/frontal-passage-like origins more than it concentrates by spread alone, that favors displacement/timing (#1) as the sharper diagnosis. If spread alone explains the error pattern about as well, that favors #2.
- This analysis uses only data already extracted in prior stages and would not require new acquisition, satellite data, or ODD access — it is a reasonable precursor to justify (or de-prioritize) a full feasibility audit for #1.

## 8. Is a Feasibility Audit Justified?

**Yes — for candidate #1 (cloud-position/motion observation) specifically**, following the same pattern as Stage 8.0 (MEPS model-level feasibility), 8.2 (observability audit), and 8.4 (VIIRS empirical extraction) before any forecasting experiment is considered. Key open questions such an audit would need to resolve: viewing-geometry adequacy at 68°N for candidate products, true acquisition-to-publication latency for a motion-vector or nowcasting product specifically (not just the cloud-property L2 products already characterized in 8.4), and 2024 historical coverage. A lighter feasibility scoping is also reasonable for #3 (CAMS, since it was only ever flagged, never audited) if #1's audit doesn't resolve the question on its own.

## 9. Is Stage 8.12 Justified?

**No — its status is unchanged: PROPOSED / REQUIRES FORENSIC AUDIT, not authorized.** Nothing in this investigation changes that. If anything, this review suggests Stage 8.12 (ensemble-confidence conditioning) is the *second*-priority candidate, not the first, pending the diagnostic comparison in Section 7 — but that comparison, and any feasibility audit, should happen before Stage 8.12 is run, not instead of it being considered later.
