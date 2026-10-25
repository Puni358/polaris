# Candidate F Through the Actual-Solar EMS Replay — vs. Frozen Stage 8.1

**Scope**: Runs Candidate F (the research-only `solar_elevation × cloud_frac` additive-feature
model, `CANDIDATE_F_REPORT.md`) through the exact same actual-solar EMS replay methodology
already used in `ACTUAL_SOLAR_REPLAY_REPORT.md`, on the same 245 NORMAL-route origins, same
warmed-up `StationState`, same critical-demand/terminal-reserve formula, same replay physics
(diesel/discharge held fixed from the plan; charge clipped to availability; critical load
protected before charging). **GAP19 was never re-run with actual solar as an input in
either arm** — only the forecast *model* producing `solar_generation` differs between the
two arms; the optimizer itself is called exactly once per arm per origin, in its normal
planning role. Script:
[run_candidateF_actual_solar_replay.py](run_candidateF_actual_solar_replay.py) (SHA256
`c81e8bb2...`). Raw results:
[CANDIDATE_F_EMS_REPLAY_RESULTS.json](CANDIDATE_F_EMS_REPLAY_RESULTS.json) (SHA256
`56974fce...`).

**Hashes, verified MATCH before the run proceeded** (frozen-manifest check reused unmodified,
plus three additional explicit assertions this script adds):
- Candidate F model: `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84`
- Frozen Stage 8.1 model: `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce`
- 2024 feature matrix: `aeca026d1acf62f530bd00220b5d85f180670ffa8de633599d779a205134de43`

**No production, config, or frozen artifact was modified.** Candidate F's model is a
research-only artifact, loaded read-only; the frozen Stage 8.1 model and GAP19 itself are
used exactly as in every prior EMS experiment in this diagnostic branch.

---

## Aggregate comparison (245 NORMAL origins) — VERIFIED

| Metric | Frozen Stage 8.1 | Candidate F | Δ (F − Stage8.1) |
|---|---|---|---|
| Planned diesel fuel (L) | 10,849.60 | 10,888.17 | **+38.57 (+0.36%)** |
| Realized diesel fuel (L) | 10,849.60 | 10,888.17 | +38.57 (identical to planned, both arms, by replay construction) |
| Planned curtailment (Wh) | 10,157,843.9 | 10,212,971.6 | +55,127.7 |
| Realized curtailment (Wh) | 8,869,721.3 | 8,855,806.5 | −13,914.8 |
| **Realized critical-load unmet (Wh)** | **1,739,283.7** | **1,658,490.2** | **−80,793.5 (−4.65%)** |
| Planned battery charge (Wh) | 38,658,765.0 | 38,736,403.3 | +77,638.3 |
| Realized battery charge (Wh) | 36,534,371.8 | 36,657,230.9 | +122,859.1 |
| Planned/realized battery discharge (Wh) | 26,575,094.9 / 26,575,094.1 | 26,629,563.4 / 26,629,563.5 | +54,468.5 (discharge is held fixed per-arm by the replay; the arms differ because the two forecast models produce different plans, not because of the replay itself) |
| **SOC violations** | **0 / 245** | **0 / 245** | no change |
| Origins with nonzero realized unmet | 220 / 245 | 219 / 245 | −1 |

**Candidate F reduces aggregate realized critical-load unmet by 80,793.5 Wh (−4.65%)**,
achieved via a very slightly *higher* committed diesel plan (+0.36%) — consistent with
Candidate F's measured lower overprediction bias (Phase 1/Candidate F report: blind bias
+3.70 vs. frozen's +4.08): a less-optimistic forecast commits marginally more generation
capacity, reducing the realized shortfall. **Reliability (SOC violations) is unchanged —
zero for both arms**, matching the prior full actual-solar-replay finding that Stage 8.1
(either variant) never breaches the SOC floor in this experiment design.

## Per-origin distribution — VERIFIED, NOT a uniform win

| | Count (of 245) |
|---|---|
| Origins where Candidate F has **less** realized unmet (improvement) | **138 (56.3%)** |
| Origins where Candidate F has **more** realized unmet (regression) | **80 (32.7%)** |
| Tied (±1 mWh) | 27 (11.0%) |

**This is a net-positive but not uniform effect.** A majority, not an overwhelming
majority, of origins improve; roughly a third get measurably worse. Largest single-origin
improvement: 2024-06-22 (−5,114.5 Wh). Largest single-origin regression: 2024-06-11
(+3,143.2 Wh). The effect is **real and net-positive in aggregate, but not something every
origin benefits from** — a materially different (more honest, less sweeping) picture than
"Candidate F is simply better."

## Statistical significance of the aggregate EMS effect — VERIFIED

**Bootstrap 95% CI (2,000 resamples over origins) for the aggregate (sum) realized-unmet
difference: [−112,308.8, −49,407.8] Wh.** **The interval excludes zero and lies entirely on
the improving side** — the aggregate −80,793.5 Wh reduction **is statistically
distinguishable from no effect** at the 95% level, consistent with (and smaller in relative
terms than, see below) the forecast-level significance already established in
`CANDIDATE_F_REPORT.md`.

## Is this operationally meaningful? — VERIFIED, with an explicit scale comparison

- **Relative to Stage 8.1's own total realized unmet, the EMS-level improvement is −4.65%.**
- **Relative to the full forecast-error-driven unmet component isolated in
  `STAGE81_UNMET_DECOMPOSITION_REPORT.md` (1,418,551.2 Wh, the residual-forecast-error share
  of the frozen model's own unmet)**, Candidate F's 80,793.5 Wh reduction represents
  **5.7% of that specific component** — a modest, not transformative, share.
- **The forecast-level improvement (Candidate F report) was −1.33% relative MAE** on the
  blind 2025 set; the EMS-level improvement, measured here on the 2024 origin set, is
  **−4.65% relative unmet** — a *larger* relative effect at the EMS level than at the raw
  forecast-metric level, though these are measured on different years/samples (2025 blind
  for the forecast claim, 2024 for this EMS replay — see UNKNOWN below) so this is not a
  like-for-like multiplier, only a directional observation.

**Determination, as requested**: Candidate F's statistically significant forecast
improvement (Phase 4, blind 2025) **does produce a statistically significant EMS-level
improvement** on this replay (bootstrap CI excludes zero) — **but the effect is modest in
absolute/relative magnitude (−4.65% of total realized unmet, 56% of origins improving) and
is not uniform across origins (33% of origins get measurably worse).** This is **not** a
transformative operational fix for the underlying 1,739 MWh-scale unmet problem; it is a
small, statistically real, partial improvement.

## UNKNOWN / not established by this replay

- **This EMS replay uses the 2024 origin set (all 347, same as every EMS experiment in this
  diagnostic branch), not the 2025 set Candidate F's own blind-forecast claim was measured
  on.** For the 174 2024-EVEN origins, Candidate F's forecast is **in-sample** (it was
  trained on exactly that data); for the 173 2024-ODD origins it is out-of-sample. This
  mirrors how the frozen Stage 8.1 model has been evaluated in every prior EMS experiment in
  this branch (also trained on 2024-EVEN, also evaluated EMS-side across the full 347-origin
  set) — so the comparison between the two arms is internally consistent and fair — **but
  neither arm's EMS-side numbers in this report are a "blind" test** in the same strict sense
  as the Phase 4 forecast-only comparison. This was not a new inconsistency introduced for
  Candidate F; it is the pre-existing convention this whole diagnostic branch has used
  throughout.
- **Whether the −4.65% EMS effect would hold on a true 2025 EMS replay** (which would require
  2025-dated station/battery/demand fixture data this repository does not have in the EMS
  pipeline's format) — not tested, not available.
- **Why roughly a third of origins get measurably worse** — not decomposed in this report;
  would require an origin-level forensic pass similar to `STAGE81_UNMET_DECOMPOSITION_REPORT.md`,
  not performed here (out of the requested scope).
- **Whether the small increase in planned diesel (+38.57 L aggregate) has any cost/governance
  implication** — not evaluated; no authorized cost function exists for diesel vs. unmet
  trade-offs in this research track (same limitation stated in every prior report in this
  chain).

## STOP

Candidate F EMS replay complete. No production, config, or frozen artifact modified; all
three model/matrix hashes re-verified MATCH before the run. Result: a real, bootstrap-
significant, but modest (−4.65%, non-uniform across origins) reduction in realized
critical-load unmet — reported as such, not amplified into a larger operational claim than
the data supports.
