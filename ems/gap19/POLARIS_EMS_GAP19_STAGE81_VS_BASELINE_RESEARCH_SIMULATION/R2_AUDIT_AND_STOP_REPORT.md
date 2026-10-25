# R2 Pre-Flight Audit — Q1/Q2/Q3 Findings, then STOP

**Scope**: Audit only, per instruction. No production code, config, or frozen R1 assumption
was changed. No R2 manifest was created, no smoke test was run, no MILP/simulator experiment
was executed. The Q1 computation below is a read-only statistical comparison against existing
frozen data (the `actual_SW_IN` ground-truth column already present in the frozen, hash-verified
feature matrix) — it does not call the optimizer, router, or simulator, and is not a rerun of
any experiment.

**Outcome up front**: Q1 is fully measurable and answered. **Q2 cannot be established — no
authorized, reproducible wind-generation forecast pipeline exists in this repository.** Per
the explicit stop condition in the task, this means R2 does not proceed: no R2 manifest, no
smoke test, no full 347-origin run. Everything below §A/§B/§C is the required audit; there is
no §4-§6 execution.

---

## Q1 — SOLAR ACCURACY

**Method**: Computed directly from the frozen, hash-verified
`stage8_1_full_37_feature_matrix_2024_CORRECTED.csv` (8,328 rows = 347 origins × 24 horizon
hours — the exact rows R1 used), which already contains a ground-truth `actual_SW_IN` column
(present for validation only — confirmed by code comment in
`s81_corrected_solar.py`: `"actual_SW_IN is never read by this engine"`). Stage 8.1's
prediction was recomputed exactly as the frozen model computes it (`pred_stage4_fold +
residual`, clipped at night) — the identical formula used in R1, not a different model. The
baseline's prediction was recomputed exactly as `LocalBaselineForecastEngine` computes it
(the fixed diurnal `sin()` curve, hour-of-day only) for the same 8,328 timestamps, using the
same horizon convention R1 used (`horizon_hour=1 == forecast_start + 0h`).

### Overall (n = 8,328 hourly rows)

| Engine | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) | nMAE (MAE / mean actual) |
|---|---|---|---|---|
| Baseline | 179.03 | 257.74 | **+164.57** | 2.006 |
| Stage 8.1 corrected | **22.85** | **50.25** | **−0.92** | **0.256** |

(mean actual SW_IN across all rows = 89.26 W/m²)

### Daytime only (actual_SW_IN > 0, n = 5,768)

| Engine | MAE | RMSE | Bias | nMAE |
|---|---|---|---|---|
| Baseline | 228.40 | 295.09 | +207.52 | 1.772 |
| Stage 8.1 corrected | 32.99 | 60.38 | −1.33 | 0.256 |

### Horizon breakdown (n = 2,082 each)

| Horizon bucket | Baseline MAE / RMSE / bias | Stage 8.1 MAE / RMSE / bias |
|---|---|---|
| h1–6 | 27.85 / 55.82 / −2.12 | 7.77 / 21.30 / −0.24 |
| h7–12 | 280.04 / 323.12 / **+260.38** | 43.41 / 73.22 / −4.60 |
| h13–18 | 354.36 / 386.20 / **+351.71** | 37.01 / 64.87 / +1.62 |
| h19–24 | 53.88 / 95.18 / +48.31 | 3.21 / 8.88 / −0.46 |

### Determination

**Stage 8.1 corrected is unambiguously, substantially more accurate than the R1 baseline**
on these 2024 rows: ~8× lower MAE overall (22.85 vs. 179.03 W/m²), ~5× lower RMSE, and
near-zero bias (−0.92) versus the baseline's large systematic over-prediction (+164.57,
driven by the baseline always assuming a clear-sky-shaped curve regardless of actual
cloud cover). The baseline's error is worst exactly at midday (h7–18, bias +260 to +352
W/m²) — i.e. it most overstates solar precisely when solar matters most for dispatch,
which is also where the R1 diesel/curtailment effect (prior forensic report) was
concentrated. **Q1 is fully measurable and answered: yes, Stage 8.1 is more accurate.**

---

## Q2 — WIND FORECAST AUDIT

### Candidate found: `WindSpeedARXForecastEngine` (`system/forecasting/implementations/wind_arx.py`)

This is the only non-baseline wind-related forecast implementation in the repository. On
inspection it does **not** qualify as a usable, authorized, reproducible wind-*generation*
forecast, for four independent reasons, each confirmed directly from code or governance
documents:

1. **It does not actually produce `wind_generation` (W), the field GAP19 consumes.**
   `wind_arx.py:99-153`: `predict()` calls `bundle = self.baseline_engine.predict(...)` at
   line 101 and never overwrites `bundle.wind_generation`. It only *adds* a separate wind
   **speed** (m/s) series into `bundle.metadata["wind_speed_forecast"]`
   (`wind_arx.py:131-148`) — a side-channel GAP19's `optimize()` never reads. **Wiring this
   engine in would change nothing about the MILP's actual wind input**: it would still be the
   same baseline persistence formula.
2. **No governed wind-speed-to-power mapping exists to even convert its output if it were
   wired in.** `POLARIS_WIND_GENERATION_MAPPING_FINAL_QUALIFICATION.md`: `WIND_POWER_MAPPING_IMPLEMENTATION_READINESS = NOT_READY`,
   `TURBINE_SPECIFICATION_STATUS = NOT_ESTABLISHED`, `POWER_CURVE_STATUS = NOT_ESTABLISHED`,
   `WIND_SPEED_TO_POWER_MAPPING = NOT_ESTABLISHED`, `WIND_GENERATION_REPRESENTATION = NOT_ESTABLISHED`.
3. **The model itself is explicitly not authorized for integration.**
   `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D4_WIND_SOURCE.md:13-14,49,66`:
   `D4_WIND_SOURCE = EXISTING_TECHNICAL_SOURCE_NOT_AUTHORIZED`, `Implementation Status: NOT_AUTHORIZED`,
   *"Authorization for Stage8.1 Integration: UNAUTHORIZED ... NO AUTHORIZED WIND FORECAST
   SOURCE IS CURRENTLY ESTABLISHED."* The companion decision record
   `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D4_DEFERRED_WIND.md:23-27,54,64` is even more
   explicit: `CURRENT_WIND_FORECAST_AUTHORIZATION = NOT_AUTHORIZED`,
   `EXISTING_TECHNICAL_WIND_SOURCE = PROTOTYPE_UNVALIDATED_NOT_AUTHORIZED`, and *"Wind
   forecasting SHALL REMAIN A DEFERRED FUTURE RESEARCH AND ENGINEERING CAPABILITY."*
4. **Even its narrower wind-*speed* validation is qualified, not a clean pass, and not a
   direct site measurement.** `wind_arx.py:141`: `model_status = "VERIFIED_WITH_LIMITATIONS"`.
   `wind_arx.py:138-139`: `site_interpretation = "CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA"`,
   `direct_nuolja_measurement = False` — the target is SMHI Abisko Aut station 188790, a
   regional proxy, not a direct Nuolja measurement
   (`POLARIS_A2_WIND_SPEED_FORECAST_OPERATIONAL_READINESS.md:28-29`:
   `A2_DIRECT_NUOLJA_MEASUREMENT = NOT_ESTABLISHED`, `ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED`).
   Separately, `POLARIS_WIND_MODEL_DEVELOPMENT_AUTHORIZATION.md:9` records that even wind
   model *execution/inference* is authorized only as a "Protocol Freeze" — actual
   execution/training/inference is explicitly **NOT AUTHORIZED**.
5. **Its own runtime interface requires data this experiment does not have.** Without a
   real `nwp_wind_speed_forecast` supplied via `runtime_context` (R1 never supplied one, and
   no governed source for one was found), `wind_arx.py:120-124` falls back to a bare
   persistence-decay heuristic (`v_t0 * exp(-0.02h) + 4.5*(1-exp(-0.02h))`) — itself another
   unvalidated formula, not the trained/audited AR-X model.

### Answers to the specific audit questions

| Question | Answer |
|---|---|
| Most authoritative reproducible wind forecast that can legally/technically be used in POLARIS today | **None.** No candidate satisfies both "authorized" and "actually feeds `wind_generation`." |
| Forecast engine/class | `WindSpeedARXForecastEngine` is the only non-baseline candidate; it produces wind *speed* metadata only, not `wind_generation` |
| Source inputs | SMHI Abisko Aut (188790) regional proxy station wind speed + an NWP wind-speed forecast input the engine's own interface requires but which is not sourced anywhere in this repository |
| Horizon coverage | 24h hourly, matching schema — but moot given §1–3 above |
| Artifact/model/data provenance | Research-phase only; `A2_Audit_Status = VERIFIED_WITH_LIMITATIONS`; direct Nuolja measurement and altitude transfer both `NOT_ESTABLISHED` |
| Runtime interface | `predict(station_state, runtime_context)`, requires `runtime_context["nwp_wind_speed_forecast"]` for a real (non-heuristic-fallback) prediction — no governed source for that input exists |

**Q2 cannot be established.** No wind-generation forecast pipeline in this repository is
simultaneously (a) authorized, (b) reproducible from a governed data source, and (c) wired
into the `wind_generation` field GAP19 actually reads.

---

## Q3 — EXPECTED R2 DESIGN (description only; not executed)

Had Q1 and Q2 both cleared, R2 would have been designed as follows:

- **Baseline vs. Stage 8.1 solar**: unchanged from R1 — same two engines, same frozen model
  and matrix hashes.
- **Validated wind forecast**: would replace the shared baseline-persistence `wind_generation`
  in *both* arms with the identified validated source, applied identically to both arms (so
  wind remains a controlled, non-varying input between arms, exactly as in R1 — only solar
  would still differ between arms).
- **Demand forecast**: unchanged from R1 (still the shared baseline-persistence demand series
  for both arms — no validated demand-forecast alternative was in scope for this audit, and
  none was identified in passing).
- **Simulator/MILP/reserve assumptions**: identical to R1 — same frozen `terminal_target_wh`
  formula/constants, same config YAMLs, same initial `StationState`, same 347-origin window —
  changing only the wind input's provenance, nothing else.
- **Only forecast inputs would differ between arms**: solar (as in R1); wind would be held
  identical between arms (upgraded from persistence to validated, but still shared).

### Remaining blockers (why R2 as designed cannot proceed now)

1. **No authorized wind-generation forecast source exists** (Q2, governance decision D4:
   `NOT_AUTHORIZED`, explicitly deferred as a future capability).
2. **No governed wind-speed-to-power mapping exists**, even if a validated wind-speed series
   existed, so `wind_generation` (W) could not be legitimately derived from it today.
3. **The one candidate model's own execution/inference is itself not authorized**
   (`POLARIS_WIND_MODEL_DEVELOPMENT_AUTHORIZATION.md`: protocol freeze only).
4. **The candidate's runtime dependency (`nwp_wind_speed_forecast`) has no governed data
   source in this repository**, so even an unauthorized trial run would fall back to an
   additional, separate heuristic rather than the audited model.

---

## STOP

Per the task's explicit instruction — *"If Q1/Q2 cannot be established from existing
evidence, STOP. Do not substitute baseline/persistence or an unvalidated model."* — this
investigation stops here. No R2 manifest was created. No smoke test was run. No full
347-origin comparison was run. No diesel/curtailment/unmet-demand/EFC/SOC/reliability/solve-time
results exist for R2, because R2 was never executed.
