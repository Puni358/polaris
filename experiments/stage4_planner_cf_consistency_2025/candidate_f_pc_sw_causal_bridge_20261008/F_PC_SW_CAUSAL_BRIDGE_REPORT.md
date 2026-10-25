# POLARIS — Candidate-F → PC-SW Causal Forecast Bridge Forensics

**Date:** 2026-10-08
**Status:** READ-ONLY forensic research. No production/model/PC-SW changes. No training. No EMS campaign. No AGY execution.
**Hash verification:** `verify_protected_hashes(REPO)` — 0 mismatches (VERIFIED). `causal_nwp_physics.py` SHA-256 re-confirmed: `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` (VERIFIED, matches governed value exactly).

---

## 1. Governance / hash verification (VERIFIED)

PC-SW forecaster hash confirmed exact. Candidate-F artifacts re-confirmed present and hash-matched (reused from the immediately preceding task, not re-hashed a third time): `candidateF_elevation_x_cloud.joblib` = `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84`; frozen Stage 8.1 model = `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce`.

---

## 2. Candidate F reconstructed exactly (VERIFIED, from `FINAL_STAGE8_1_FORECASTING_FREEZE.md §2` and `CANDIDATE_F_REPORT.md`)

**The complete, governed, fixed-order 37-feature contract** (Candidate F = this + `elevation_x_cloud_frac`, 38 total):

```
horizon_hour, month, hour, solar_elevation, solar_zenith, clearsky_ghi,
fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, cloud_frac,
pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold,
ctx_std_3h, ctx_std_6h, ctx_std_12h, ctx_std_24h,
ctx_abs_change_1h, ctx_abs_change_3h, ctx_abs_change_6h,
ctx_max_diff_6h, ctx_mean_diff_6h, ctx_slope_6h,
ctx_kt_std_6h, ctx_last_obs, ctx_mean_24h, ctx_max_24h,
lwp_latest, iwp_latest, lwp_x_cloud,
terrain_horizon_elevation_deg, terrain_elevation_margin_deg,
terrain_solar_obstruction_flag, clearsky_ghi_terrain_adjusted,
u700, v700
```
plus `elevation_x_cloud_frac` (Candidate F's own addition, §1 of the prior report).

**Model:** `HistGradientBoostingRegressor(max_depth=4, min_samples_leaf=30, l2_regularization=10.0, loss="absolute_error", random_state=42)`. **Training/validation/blind:** 2024 EVEN / 2024 ODD / 2025 whole-year. `actual_SW_IN` never a feature (asserted in the inference script). Night/clearsky/clipping handling specific to the GBDT pipeline is not separately re-derived here — not needed for the bridge question, which concerns inputs, not output post-processing.

---

## 3. LWP/IWP timestamp verification (VERIFIED, reused from the STAGE8_11A forensic audit, re-confirmed data exists for the 2025 population)

- **Source:** MEPS `D-1 18:00 UTC` run profile data (`q_l`, `q_i` at 13 pressure levels), independently computed per horizon hour `h∈[1,24]` (`stage6_6/run_stage6_6.py:211-262`).
- **Issuance timestamp:** `D-1 18:00 UTC`, strictly before `t0` (forecast origin, `D 00:00 UTC`). **Issuance margin confirmed ≥6h before `t0`, and the full 24h horizon extends to `t0+24h` — the MEPS run issued at `D-1 18Z` causally covers the entire target period.**
- **Not SITES/realized:** confirmed absent any `actual_SW_IN` dependency in the construction path (STAGE8_11A audit §6, re-confirmed here by file inspection: `lwp_iwp_extracted_features.csv` schema contains only `surface_air_pressure_hpa`, `lwp_latest`, `iwp_latest`, `meps_run_id` — no observation column).
- **2025 coverage confirmed to exist:** `stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv` (815,078 bytes, columns `origin_index, forecast_start, horizon_hour, valid_time, forecast_reference_time, surface_air_pressure_hpa, lwp_latest, iwp_latest, meps_run_id`) — **VERIFIED present** for the same 2025 calendar year PC-SW's holdout population uses.

**No part of the LWP/IWP claim is UNKNOWN; all parts verified.**

---

## 4/6. Feature-by-feature bridge audit, with PC-SW's exact mathematical structure traced (VERIFIED, `system/forecasting/implementations/causal_nwp_physics.py` read in full)

**PC-SW's entire solar pathway, exactly:**
```
forecast_GHI = 0                                    if solar_elevation <= 0 or clearsky_GHI <= 0
forecast_GHI = max(0, clearsky_GHI * (1 - cloud_fraction))   otherwise
solar_generation = min(forecast_GHI * 300 * 0.20 * 0.85, 60000 W)
```
where `clearsky_GHI` is PVLIB's deterministic Ineichen model (pure astronomy, same family as Stage 8.1's `clearsky_ghi`) and `cloud_fraction = fc_cloud_cover/100` (the *same* MEPS field Stage 8.1 also uses). **This is the entire input set: two quantities (cloud fraction, solar elevation/clearsky), a night-zero rule, and a fixed linear PV clip.** No LWP/IWP, no terrain, no humidity/temperature, no lagged-observation context, no ensemble/disagreement, no u700/v700, and no Stage-4 physics correction (`k_h`) enter this formula at all — the module's own docstring explicitly states `"Stage 4 k_h ≈ 0.50 is NOT used"`.

| # | Feature | Source | Causal? | Used by PC-SW? | Available to PC-SW? | Repo location | Class |
|---|---|---|---|---|---|---|---|
| 1 | `horizon_hour, month, hour` | time index | YES | implicitly (loop index) | YES | — | A |
| 2 | `solar_elevation, solar_zenith` | PVLIB astronomy | YES | YES (elevation, for night-zero) | YES | `causal_nwp_physics.py:342` | A |
| 3 | `clearsky_ghi` | PVLIB Ineichen | YES | YES | YES | `causal_nwp_physics.py:336` | A |
| 4 | `fc_cloud_cover` / `cloud_frac` | MEPS 18Z | YES | YES | YES | `causal_nwp_physics.py:113,351` | A |
| 5 | **`fc_temperature_2m`, `fc_relative_humidity_2m`** | MEPS 18Z, **same file PC-SW already loads** | YES | **NO** | **YES — already a column in `data/POLARIS_v0_1_future_weather_forecasts_2025.csv`, confirmed present (VERIFIED, `head -1` of the file)** | same weather CSV PC-SW's campaign runner already reads | **B — lowest-friction candidate, zero new data acquisition needed** |
| 6 | `pred_stage3b_cloud_nwp, phys_pred_fold, pred_stage4_fold, disagreement_fold` | prior POLARIS stage model outputs / Stage-4 `k_h` physics prediction / ensemble disagreement | mostly YES (forecast-time model outputs) | **NO — explicitly disclaimed** (`"Stage 4 k_h ... is NOT used"`) | Requires the Stage3b/Stage4 pipeline's own artifacts; not verified whether these specific intermediate predictions are persisted for the 2025 PC-SW population in a directly reusable form | `stage7/stage8/...` (Stage 3b/4 lineage, not independently re-traced in this pass) | **C — causal source plausibly exists upstream, but production-ready 2025-aligned integration not verified in this pass; UNKNOWN whether persisted for PC-SW's exact population** |
| 7 | `ctx_std_3h...ctx_max_24h` (14 lagged-observation context features) | computed inline from the station's own recent realized observations, ending strictly at `t0-1h` | YES (uses only past realized data, never future) | **NO** | **YES in principle — PC-SW's own closed-loop harness already tracks each origin's realized solar sequentially (`realized_inputs_for`), so the raw data to compute these exists in the harness's own state; simply not currently wired into the forecaster** | `planner_cf_campaign_runner.py` (realized trajectory already carried) | **B — causally available via the harness's own existing state, not currently consumed** |
| 8 | `lwp_latest, iwp_latest, lwp_x_cloud` | MEPS 18Z, §3 | YES | **NO** | **YES — 2025 file confirmed present** (§3) | `stage6/stage6_6_lwp_iwp_2025/lwp_iwp_extracted_features_2025.csv` | **B** |
| 9 | `terrain_horizon_elevation_deg, terrain_elevation_margin_deg, terrain_solar_obstruction_flag, clearsky_ghi_terrain_adjusted` | static terrain/horizon geometry | YES | **NO** | YES — 2025 file confirmed present (`data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv`) | same | **B, but ALREADY TESTED in the PC-SW/EMS context and found `SAFE-BUT-FUEL-WORSE`** (`phase1_terrain_correction_20261007/PHASE1_TERRAIN_RESULT_SUMMARY.md`, reused, not re-tested) — **effectively closed, not a promising bridge** |
| 10 | `u700, v700` | MEPS 700hPa wind | YES | **NO** (PC-SW's wind path is an unrelated deterministic synthetic formula, not weather-derived at all) | YES — 2025 file confirmed present | `stage7/stage8/stage8_1_700hpa_wind_2025/stage8_1_wind700_features_2025.csv` | **D — not transferable to PC-SW's solar path; PC-SW's wind generation doesn't use weather data of any kind, so this family has no entry point** |
| 11 | `elevation_x_cloud_frac` (Candidate F's own addition) | product of #2 and #4 | YES | **NO** (PC-SW applies cloud attenuation linearly, `1-cloud_fraction`, with no elevation interaction term) | YES — both inputs already present in PC-SW | — | **A-adjacent/B — the interaction term itself is trivially constructible from inputs PC-SW already has** |

---

## 5. What actually drives F's advantage (DIAGNOSTIC + UNKNOWN, reused — no new attribution computed)

The persisted Candidate-F evidence establishes the **aggregate** improvement (blind MAE −0.4797 W/m²) but, per the prior task's own finding, **no SHAP/permutation/ablation feature-importance breakdown for the 38 features was located in the repository** — the single disclosed mechanistic finding is the origin-level direction analysis (`CANDIDATE_F_PRE_TRAINING_AUDIT.md §9`): F's correction behaves as a *global* bias shift, improving diesel/unmet alignment at 138/245 origins where the correction moves dispatch in the forecast-favorable direction, worsening it at the remaining subset. **This describes the net *effect* of the model's correction, not which of the 38 individual features drives it — marked UNKNOWN at the per-feature level**, consistent with the prior task's disclosure. No new ablation was run in this pass (explicitly out of scope — "do not build a new model yet").

---

## 7. Forecast-horizon alignment check (VERIFIED, representative)

For PC-SW origin 2 (`forecast_start = 2025-05-02 00:00:00`): PC-SW's own decision timestamp is `t0 = 2025-05-01 23:00:00` (one hour before `forecast_start`, per `planner_cf_campaign_runner.py`'s `t0` construction), issuing a forecast over `t0+1h ... t0+24h`. The MEPS cloud trajectory PC-SW consumes for this window is drawn from `data/POLARIS_v0_1_future_weather_forecasts_2025.csv`'s `fc_cloud_cover` column — **the exact same underlying MEPS run family** (`D-1 18Z`) that feeds Stage 8.1/Candidate F's `fc_cloud_cover`, `lwp_latest`, `iwp_latest`, `u700`, `v700` for the same calendar dates. **No temporal mismatch found**: both pipelines draw from MEPS runs issued strictly before their respective `t0`, and the LWP/IWP/terrain/wind files confirmed in §4 cover the identical 2025 calendar range PC-SW's 123-origin population spans (`2025-05-01` through `2025-08-31`, per `origin_population()`). **The bridge is temporally legitimate for every feature classified B above** — none would require information not yet existing at PC-SW's own decision time.

---

## 8. Causal information gap table

| Information | F has it? | PC-SW has it? | Causal at decision time? | Solar relevance | Source | Bridge class |
|---|---|---|---|---|---|---|
| Cloud fraction | Yes | Yes | Yes | Primary attenuation driver | shared MEPS file | A (already shared) |
| `fc_temperature_2m`, `fc_relative_humidity_2m` | Yes | **No** (not consumed) | Yes | Physically relevant to cloud optical properties/atmospheric transmission, not currently exploited by either model's physics term directly (F uses it as a GBDT input, not a physics term) | same weather CSV PC-SW already loads | **B** |
| LWP/IWP (cloud liquid/ice water path) | Yes | **No** | Yes (§3) | Direct physical driver of cloud optical depth / shortwave attenuation — plausibly more informative than a single scalar cloud *fraction* for irradiance attenuation | `stage6/stage6_6_lwp_iwp_2025/` | **B** |
| Terrain horizon/obstruction | Yes | **No** | Yes | Local horizon blocking at a specific site/season | `data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv` | **B, but empirically tested and fuel-worse (closed)** |
| Lagged station context (`ctx_*`) | Yes | **No** | Yes (uses only past realized values) | Captures persistence/recent-trend information a single-timestep physics formula cannot | PC-SW's own existing closed-loop state | **B** |
| Stage3b/Stage4 ensemble/physics predictions | Yes | **No** | Plausible, not independently re-verified for 2025/PC-SW alignment in this pass | Captures a second, independently-derived cloud-NWP estimate (disagreement/ensemble signal) | Stage 3b/4 lineage | **C / UNKNOWN** |
| `u700/v700` | Yes | **No** | Yes | Not solar-relevant to PC-SW's current pathway (wind generation is unrelated to weather data) | `stage8_1_700hpa_wind_2025/` | **D** |

**Only LWP/IWP and the lagged-context family represent genuinely novel physical information** (not already redundant with cloud fraction) that is causally available and not yet tested in the PC-SW/EMS context (unlike terrain, which was already tested and rejected).

---

## 9/10. Impact path and the two distinguished questions (VERIFIED/DIAGNOSTIC, reused — no new population-scale test run)

**Question A (does F improve solar prediction?):** established, governed, VERIFIED (§2 of the prior report) — yes, modestly, for Stage 8.1's own GBDT architecture.

**Question B (would the same information improve PC-SW?):** **not established by A, and not tested in this pass.** PC-SW's physics formula is structurally different (a two-input deterministic attenuation law, not a 38-feature GBDT) — adding, e.g., LWP as a *third* input would require a **new physical attenuation formula**, not a drop-in feature addition, since PC-SW has no learned model to simply hand more columns to. This is a materially different, larger undertaking than "add a feature," and was not attempted here (explicitly out of scope, §9 of the task). **Whether an improved physics-based attenuation law using LWP/IWP would reduce PC-SW diesel is UNKNOWN** — it has a plausible physical rationale (cloud liquid/ice water path is a more direct driver of shortwave attenuation than a single cloud-fraction scalar) but no quantified causal path to diesel was established in this report, consistent with the task's explicit instruction not to assume MAE improvement automatically implies lower diesel.

**Reused finding on PC-SW's actual forecast-error/diesel linkage** (EBR population task, two tasks prior, not re-derived): wind forecast error ≡ 0 for PC-SW always (synthetic, not weather-driven — **this means the `u700/v700` gap (D above) is moot regardless of transferability**, since PC-SW's wind path doesn't use weather data at all); solar forecast error is mildly optimistic on average and shows no significant difference between the "EBR-off-beneficial" and "EBR-off-harmful" origin populations. **This does not by itself rule out a LWP/IWP-based attenuation improvement** — that prior finding characterized PC-SW's *existing* (cloud-fraction-only) forecast error, not a hypothetical LWP-informed one; it establishes only that the current error is not the EBR-split's driver, not that a *better* forecast couldn't change the diesel trajectory in some other way.

---

## 11. Distinguishing A from B — restated for clarity

Confirmed and preserved: Candidate F's blind-MAE/EMS-replay figures are **Stage-8.1-pipeline-specific** and are not claimed anywhere in this report as PC-SW numbers. The bridge classification (§4/§8) is built entirely from tracing **data availability and timestamp alignment**, not from assuming F's improvement transfers.

---

## 12. Repository search for existing causal sources (VERIFIED, per the priority list in task §12)

| Priority | Family | Found? | Location |
|---|---|---|---|
| 1 | MEPS forecast fields | Yes | `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` |
| 2 | NWP cloud microphysics | Yes (via LWP/IWP) | `stage6/stage6_6_lwp_iwp_2025/` |
| 3 | LWP/IWP forecast fields | Yes | as above |
| 4 | Cloud fraction forecast | Yes | shared weather CSV |
| 5 | Humidity/cloud-water/ice variables | Yes (`fc_relative_humidity_2m`) | shared weather CSV |
| 6 | Ensemble/spread information | Partially (`disagreement_fold` exists as a Stage 8.1 feature) | Stage 3b/4 lineage, not independently re-verified for 2025 PC-SW alignment |
| 7 | Terrain/solar geometry | Yes | `data/POLARIS_v0_1_SITES_Nuolja_2025_terrain_features.csv` — **already tested, fuel-worse** |
| 8 | Other persisted causal atmospheric variables | `fc_precipitation`, `fc_surface_pressure`, `fc_wind_speed_10m` also present in the shared weather CSV, **not used by Stage 8.1's 37-feature contract or PC-SW** — not analyzed further here, outside the F→PC-SW scope |

No external data source was introduced; everything cited already exists in the repository.

---

## 13. Bridge classification summary

| Family | Classification |
|---|---|
| Cloud fraction, elevation, clearsky | **A** (already shared) |
| `fc_temperature_2m`, `fc_relative_humidity_2m` | **B** |
| LWP/IWP, `lwp_x_cloud` | **B** |
| Lagged station context (`ctx_*`) | **B** |
| Terrain/horizon | **B, but empirically closed (fuel-worse)** |
| Stage3b/4 ensemble/physics predictions | **C/UNKNOWN** |
| `u700/v700` | **D** |

---

## 14. Future research specification (description only — NOT to be executed)

**If** a legitimate next step were authorized (it is not being proposed for execution here), the smallest well-scoped candidate per the evidence above would be: a **new physical attenuation term** in `causal_nwp_physics.py`'s *research-diagnostic copy* (not the governed file) that incorporates `lwp_latest`/`iwp_latest` as an additional optical-depth modifier to the existing `clearsky_GHI × (1−cloud_fraction)` formula, with:
- **Required causal input:** `lwp_latest`, `iwp_latest` from the already-existing 2025 file, joined on `(forecast_start, horizon_hour)` exactly as Stage 8.1 already does.
- **Timestamp requirement:** MEPS `D-1 18Z` issuance, already satisfied by the existing file (§3).
- **Feature definition:** a physically-motivated attenuation adjustment (not specified further — specifying the exact functional form is model design, explicitly out of scope for this forensic pass).
- **Validation dataset:** the same 2025 holdout PC-SW already uses, with the identical causal firewall (`check_causal_firewall`) applied.
- **Leakage gate:** re-run the same two-audit pattern already used for LWP/IWP in Stage 8.1 (temporal causality + target-exclusion check).
- **Forecast metric gates:** MAE/bias improvement on the 2025 blind set, independently reproduced (not merely read from a report), before any EMS-level test is even considered.

This specification is **not implemented, trained, or tested** in this pass.

---

## 15. Required F value assessment

**B — No, but only as a research/reference model; the useful signal (cloud microphysics, lagged context, humidity) is legitimate and causally available, but has not been shown to transfer into PC-SW's structurally different physics formula.** F was not wasted (§2/§3/§4 of the prior report already established this); this report adds that **some** of F's inputs (LWP/IWP, humidity, lagged context) are concretely, causally available for PC-SW's exact population and decision times (§4/§7/§8) — a stronger, more specific finding than the prior task reached — but transferring them requires a new physics formula, not a parameter change, and that redesign was not attempted here.

---

## 17. Final questions

1. **What did F learn that PC-SW doesn't have?** Cloud microphysics (LWP/IWP), humidity/temperature, lagged station-observation context, and (unverified) ensemble disagreement — none of which enter PC-SW's two-input attenuation formula.
2. **Are LWP/IWP legitimately causal for F?** **Yes — re-verified in this pass** (§3).
3. **Exact issuance timestamp?** `D-1 18:00 UTC`, ≥6h before `t0`.
4. **Which F features are actually useful per persisted evidence?** Only the aggregate effect is documented (§5); per-feature attribution is UNKNOWN.
5. **Which useful features already exist in PC-SW?** Cloud fraction, elevation/clearsky (§4, category A).
6. **Which useful features exist causally in the repository but are unused?** `fc_temperature_2m`, `fc_relative_humidity_2m`, LWP/IWP, lagged context, terrain (terrain already tested and rejected) — all category B.
7. **Can any be transferred without future leakage?** Yes, for all category-B families — timestamps align (§7), no future information required.
8. **Would it enter PC-SW's forecast at the correct decision time?** Yes, confirmed via the alignment check (§7).
9. **Plausible causal path to lower diesel?** Physically plausible (better attenuation estimate → better `e_stage2_target`/dispatch inputs) but **not quantified** — UNKNOWN, explicitly not assumed from MAE alone (task §11).
10. **Evidence required before implementation?** A new physics formula design, its own leakage/causality audit, and a 2025-blind forecast-metric gate — all before any EMS-level test (§14).
11. **Was F wasted?** **No** (§15, B).
12. **Single most valuable next forecasting experiment, if justified?** A physics-formula redesign incorporating LWP/IWP as an optical-depth modifier to PC-SW's existing clearsky×(1−cloud_fraction) term — **described only, not executed.**

"NO POLICY EXPERIMENT WAS EXECUTED."
