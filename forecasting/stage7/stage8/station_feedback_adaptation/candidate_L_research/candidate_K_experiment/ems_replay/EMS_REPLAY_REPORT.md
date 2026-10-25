# Candidate F vs Candidate K — 2024 Actual-Solar EMS Replay

**RESEARCH-ONLY. NOT a production run. NOT a re-optimization. NOT a promotion decision.**

## Scope extension (explicit, user-authorized)

Candidate K (`../candidate_K_report.md`, `../candidate_K_manifest.json`) was tuned on 2022
and blind-evaluated on Jan–Sep 2023. Before writing this script, an exhaustive repository
search was performed for a validated wind/demand/station-state EMS fixture covering 2023.
**None exists.** The only validated EMS fixture with actual wind/demand/station-state ground
truth (`POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv`, hash-pinned, used unmodified by
`run_actual_solar_replay.py` / `run_candidateF_actual_solar_replay.py`) covers **only
calendar year 2024**. 2023 is therefore not reproducible as an EMS replay in this
repository.

Per explicit user instruction, this experiment is a **separate, clearly-labeled 2024
operational EMS evaluation** — not the original frozen 2023 blind forecast test. Candidate
K's configuration was **not retuned** on 2024; it was taken verbatim from
`candidate_K_manifest.json` (`variant=A_global, alpha=0.1, min_history=1, max_clip=75.0
W/m², scale_mode=unscaled`) and K's own frozen causal EWMA update function
(`candidate_K_experiment.run_simulation`) was imported and called **unmodified**, with its
`mu_global` state continued forward in strict chronological order from the end of the frozen
2020–2023 historical residual dataset into the 2024 origins. This is application of an
already-locked procedure to new inputs, not retraining or hyperparameter selection.

## Methodology (reused, unmodified, by import)

- `replay_plan_against_actual_solar`, `pv_from_sw_in` — `run_actual_solar_replay.py`
- `predict_solar_bundle`, `sw_in_to_power_w` — `run_candidateF_actual_solar_replay.py`
- `compute_terminal_target_wh` — `run_research_simulation.py` (via `run_full_experiment.py`)
- `verify_frozen_manifest`, `build_components` — `run_full_experiment.py`
- `run_simulation` (K's causal EWMA correction) — `candidate_K_experiment.py`

GAP19 (`GAP19HighsNativeOptimizer`, frozen, unmodified) is called **exactly once per origin
per arm**, for planning only, and is **never** re-run with actual solar as an input. Origins
(347, 2024), actual solar, actual wind, actual demand, station state, initial SOC (80%,
160,000 Wh), diesel state, optimizer, optimizer configuration, terminal/reserve policy,
MPC/replay mechanics, and timestep (1h, 24h horizon) are **identical** between the F arm and
the K arm for every origin. The only difference is which solar forecast (F's own frozen
prediction vs F corrected by K's EWMA) feeds the optimizer's planning step.

## Integrity

| Input | Hash status |
|---|---|
| Candidate F model (`candidateF_elevation_x_cloud.joblib`) | MATCH, unmodified |
| 2024 feature matrix (`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv`) | MATCH, unmodified |
| 2020–2023 historical residual dataset | MATCH, unmodified |
| Frozen R1 manifest (matrix/model/script/config hashes) | All MATCH |

F was never re-trained or re-called with new logic — only applied read-only to the 2024
matrix with the exact method already disclosed for the F-vs-Stage-8.1 replay. K was never
retuned — its locked config and causal update function were reused verbatim; only its
*inputs* (F's 2024 predictions) were new.

## Results

- **347** 2024 origins; **245** routed `NORMAL` for both arms (**0 route mismatches**
  between F and K across all 347 origins); **0 optimizer failures**; **0 SOC-floor
  violations** for either arm.
- Reliability (1 − unmet / critical demand, summed over the 245 paired NORMAL origins):
  **F = 97.57%**, **K = 97.38%**.

Paired (origin-level), 245 NORMAL-routed origins common to both arms. Positive
`paired_delta_f_minus_k` = F worse / higher than K; negative = K worse / higher than F.
95% CIs from a 2000-iteration origin-level paired bootstrap.

| Metric | F mean | K mean | Δ (F−K) mean | 95% CI | Significant? |
|---|---|---|---|---|---|
| Unmet load (Wh/origin) | 6,769.35 | 7,285.95 | **−516.60** | [−729.60, −300.45] | **Yes — K worse** |
| Diesel fuel (L/origin) | 44.44 | 44.25 | +0.19 | [−0.05, 0.44] | No |
| Diesel-on hours | 2.64 | 2.65 | −0.008 | [−0.037, 0.020] | No |
| Diesel startups | 1.37 | 1.39 | −0.020 | [−0.053, 0.012] | No |
| Curtailment (Wh/origin) | 36,146.15 | 36,164.48 | −18.33 | [−401.94, 366.86] | No |
| Battery EFC (origin) | 0.6458 | 0.6430 | +0.0028 | [0.0002, 0.0052] | Marginal — F slightly more throughput |
| SOC-floor violations | 0 | 0 | 0 | [0, 0] | No (both zero) |
| Solve time (s) | 0.404 | 0.567 | −0.164 | [−0.467, 0.005] | No |

## Interpretation

Over this 2024 operational window, Candidate K's forecast correction does **not** translate
into a better EMS outcome — it produces **statistically significantly more unmet critical
load** than frozen Candidate F (paired 95% CI excludes zero, K worse by ~517 Wh/origin,
~1,785,057 Wh vs 1,658,490 Wh total over 245 origins). Diesel fuel, diesel-on hours,
startups, curtailment, and SOC-floor violations are statistically indistinguishable between
the two arms. This is consistent with K's forecast-accuracy gain (lower MAE/bias on 2023
blind SW_IN) not being the same thing as a gain under the optimizer's actual planning
objective and constraint structure on this different (2024) operational year — a result a
pure forecast-error metric cannot see.

**This result does not override, and is not directly comparable to, K's frozen 2023 blind
forecast-accuracy result** (`candidate_K_blind_results.csv`): that was a different year,
and this experiment never re-validates or retunes K's forecast performance — it only asks
whether applying K's already-locked correction, unchanged, to a different year's F
predictions helps or hurts the EMS outcome in that year.

## Governance

- **FORECAST RESULT** (already established, unchanged by this experiment): on the frozen
  2023 blind test, K improved SW_IN MAE by 10.15% (53.87 → 48.40 W/m²) and bias by ~90%
  (+27.99 → +2.76 W/m²).
- **EMS RESULT** (this experiment, 2024 operational scope extension): K produces
  significantly **more** unmet critical load than F (paired 95% CI excludes zero); all
  other operational metrics (diesel fuel, diesel-on hours, startups, curtailment, SOC-floor
  violations, optimizer failures, route mismatches) are statistically indistinguishable
  between F and K.
- **STATISTICAL RESULT**: origin-level paired bootstrap (2000 iterations, seed 42), n=245
  NORMAL-routed-by-both origins. See table above and `ems_replay_results.csv`.
- **INTEGRITY**: all frozen inputs (F model, 2024 matrix, 2020–2023 historical residual
  dataset, R1 manifest hashes) verified MATCH before execution. F and K were never
  retrained, retuned, or regenerated — K's inputs were extended (2024 F predictions), not
  its procedure or hyperparameters. No production code, config, frozen artifact, Stage 8.1
  model, or the validated EMS fixture was modified.
- **GOVERNANCE**: Candidate K remains **research-only** and is **NOT promoted**. This
  experiment, if anything, adds evidence against promoting K as-is: its forecast-accuracy
  gain on 2023 solar does not reproduce as an EMS-outcome gain on the 2024 operational
  fixture — it is associated with worse reliability (more unmet critical load) under the
  real optimizer, on this one year of operational data.

## Files

- `ems_replay.py` — the replay script (this experiment)
- `ems_replay_results.csv` — paired summary metrics + bootstrap CIs
- `ems_replay_origin_level.csv` — per-origin, per-arm raw metrics (345 origins × ~20 columns)
- `EMS_REPLAY_MANIFEST.json` — full per-origin/per-hour detail, hashes, config, summary
- `EMS_REPLAY_REPORT.md` — this report
