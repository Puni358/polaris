# EVID-03 — Reserve-Shortfall / Solar-Credit Numeric-Basis Evidence (offline, research-only)

**Commissioned by:** project owner, this pass (2026-10-17), per the directive: *"I commission the bounded, offline, research-only EVID-03 analysis described in the register."*
**Scope authority:** `POLARIS_MASTER_DECISION_REGISTER.json` item `EVID-03`; `N6_REMEDIATION_REPORTS/SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` Section 4.
**Nature:** Evidence-only. **No numeric reserve-shortfall ceiling or solar-credit cap is proposed, selected, or adopted anywhere in this directory.**

---

## What this directory contains

- `compute_evid03_reserve_margin_analysis.py` — stdlib-only analysis script.
- `test_evid03_reserve_margin_analysis.py` — 14 focused unit tests on synthetic fixtures.
- `outputs/evid03_reserve_margin_evidence.json` — full evidence report (both datasets, both horizon bases).
- `outputs/HASHES.txt` — input/output SHA-256 hashes.

## Reproduction

```
cd research/evid03_reserve_margin_analysis
python3 -m unittest test_evid03_reserve_margin_analysis -v   # 14/14 pass
python3 compute_evid03_reserve_margin_analysis.py            # regenerates outputs/
```

No third-party dependency; no network access; no write outside this directory's own `outputs/`.

## Exact question this analysis answers

`SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md` Section 4 states that before any reserve-shortfall ceiling or solar-credit cap can be authorized, the project owner needs: *"Wh vs. kWh; per-step vs. cumulative-over-horizon vs. cumulative-over-campaign; whether the ceiling scales with the EBR target (a percentage) or is a fixed absolute Wh figure; whether it differs for the 6-hour EBR window vs. the 24h terminal target."* This analysis populates those specific units/horizon/margin dimensions with empirical numbers drawn from existing historical data — it does not answer *what the ceiling should be*.

## Inputs (identical to PCEEB Part (a); both already-used, non-sealed, read-only)

| Dataset | Path | Origins | SHA-256 |
|---|---|---|---|
| Primary | `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | 1,369 | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` |
| Secondary (corroboration) | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | 173 | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` |

Both hashes independently re-verified this pass and re-confirmed identical to the values PCEEB Part (a) already recorded (`pceeb_recorded_input_sha256_matches: true` for both datasets in the output JSON).

Also read (not recomputed): `research/pceeb_part_a_offline/outputs/pceeb_quantile_envelope_2020_2023.json` and `.../pceeb_quantile_envelope_2024_odd_fixture.json` — the already-authorized (UNC-01 Part (a)) prefix-cumulative solar-forecast-error quantile envelopes.

Also read-only, for GAP19's own horizon/units facts (E1/E2 below; neither file edited): `system/optimization/implementations/gap19_highs_native.py` (a `PROTECTED_FILES` entry — read only, never edited, in this or any pass) and `system/safety/reserve_policy_guard.py` (not protected, read only).

## Method, in one paragraph

GAP19 defines two reserve-target horizon bases: a 6-hour rolling EBR window (`E_EBR_target[t]`) and a full-horizon/terminal target applied at the final step (`E_term_target`, at t=23). This script re-expresses PCEEB's already-computed prefix-cumulative solar-forecast-error quantile envelope at exactly those two lookahead-step ranks (step 6, and the dataset's final step — 19 for the primary dataset, 24 for the secondary), converts the irradiance-error quantiles (Wh/m²) into generation-energy-equivalent Wh via the existing `K_PV = 51.0 W/(W/m²)` constant (already hard-coded identically in `n6_solar.py` and `polaris_inference_runner.py`), and expresses the result both in absolute Wh and as a percentage of two existing reference constants: `EBR_BASE_WH = 15,000 Wh` and the default hard-SOC-floor `min_e_wh = 40,000 Wh`. It additionally computes a new descriptive statistic — the empirical rate and magnitude of "forecast-overestimate" events (cumulative realized irradiance below cumulative predicted) at the same two horizon bases — as the direct empirical analogue of the risk a solar-credit cap exists to bound.

## Methodological choices made and documented (not silently invented)

See the module docstring in `compute_evid03_reserve_margin_analysis.py` for the full statement of E1–E5 (horizon-basis citation, existing-guard-formula citation, units conversion, reference-scale choice, overestimate-event definition) and M1/M2/M4/M5 (sign convention, horizon indexing, missing-data rule, quantile estimator — identical to PCEEB Part (a)'s own choices, restated here for a standalone directory).

## Results summary (see `outputs/evid03_reserve_margin_evidence.json` for full detail)

**Primary dataset (2020–2023, 1,369 origins), generation-energy-equivalent, 5th percentile (adverse tail):**

| Horizon basis | q05 (Wh) | as % of EBR_BASE_WH (15,000 Wh) | as % of hard SOC floor (40,000 Wh) |
|---|---|---|---|
| 6h rolling EBR window (step 6) | −21,961 Wh | −146.4% | −54.9% |
| Full horizon / terminal (step 19) | −89,327 Wh | −595.5% | −223.3% |

**Overestimate-event rate (forecast-credits-would-have-been-wrong proxy), primary dataset:**

| Horizon basis | Event rate | Median overestimate magnitude (Wh) |
|---|---|---|
| 6h rolling EBR window | 39.0% (534/1,369 origins) | 6,810 Wh (45.4% of EBR_BASE_WH) |
| Full horizon / terminal | 54.9% (752/1,369 origins) | 29,376 Wh (195.8% of EBR_BASE_WH) |

The secondary (2024-ODD, 173 origins) dataset shows the same qualitative pattern (widening tail magnitude with horizon; overestimate rate near 40–50%); full figures are in the output JSON's `datasets.secondary_corroboration` block.

**What this evidence shows, stated as empirical fact only:** at both horizon bases, the 5th-percentile adverse-tail solar-forecast-error magnitude already exceeds the existing `EBR_BASE_WH` (15,000 Wh) reference constant, and at the full-horizon basis it exceeds even the default hard-SOC-floor (40,000 Wh). This is evidence that a reserve-shortfall ceiling set equal to, or a solar-credit cap scaled against, either existing constant would be exceeded by historical tail-case forecast error alone (before any wind/demand/battery-trajectory interaction) at a non-negligible rate. **This is not a recommendation for any specific ceiling or cap value** — it is a description of how large historical forecast error has actually been, in the same units and horizon bases a future ceiling would need to use, for the owner's own risk-tolerance judgment.

## Limitations (documented, not extrapolated past)

1. **Solar-only proxy, not a replay-validated measurement.** Actual GAP19 `reserve_shortfall` (`s_J2`) depends jointly on solar, wind, demand, battery SOC trajectory, and the optimizer's own lexicographic objective (J1 > J2 > J3 > J4) — none of which this script models. A full measurement requires Part (b)-style closed-loop replay, which remains gated behind `CampaignExecutionNotAuthorizedError` and is **not** performed here.
2. **Linear K_PV scaling, no inverter clip.** The conversion ignores the `P_INV_MAX_W = 60,000 W` inverter ceiling and clearsky/terrain shading adjustments the real plant model applies.
3. **No ensemble/uncertainty spread in these datasets.** Neither input carries per-origin `ensemble_std`, so the N6 conformal lower-bound (`Q_HAT_NORM = 1.8590`) coverage computation cannot be reproduced here. `FORECAST_UNCERTAINTY_AUDIT.md`'s own, already-published finding on that exact question (static q10: 88.53% pooled one-sided coverage, but "operationally excessive" in closed-loop replay: +38.18% diesel, +92.87% curtailment) is **cited**, not recomputed.
4. **Not Nuolja-station-specific critical-load data.** EVID-02's `REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED` finding is unchanged.
5. **`EBR_BASE_WH` and `reserve_shortfall_total_wh`'s "sum over 24 steps" basis are existing, but not owner-authorized, conventions.** This analysis uses them only as reference points already present in the repository (SAF-07's "unverified, no provenance found" disposition for the 15 kWh figure is unchanged and reiterated).

## What this directory does not do

Does not invoke, bypass, or reimplement `system/evaluation/replay_harness.py`. Does not run any dispatch campaign, closed-loop simulation, or replay-equivalent comparison. Does not edit `gap19_highs_native.py` or any other `PROTECTED_FILES` entry (both are read-only inspected for their existing horizon/units definitions). Does not access the sealed 2025 blind partition. Does not fit, train, tune, recalibrate, or promote any model. Does not change any production default, reserve policy, solar-credit behavior, or control flow. Does not select, propose, recommend, or adopt any numeric reserve-shortfall ceiling or solar-credit cap.
