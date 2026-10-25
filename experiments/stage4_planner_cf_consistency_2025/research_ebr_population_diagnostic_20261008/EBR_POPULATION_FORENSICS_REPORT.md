# POLARIS — PC-SW v1.2 EBR Population Attribution Forensics

**Date:** 2026-10-08
**Status:** READ-ONLY forensic research report. No production code, planner semantics, configs, telemetry, or governance files modified. No policy campaign executed. No candidate promoted.
**Scope:** Full certified PC-SW v1.2 population (123 origins × 24 executed hours = 2,952 rolling resolves), 2025 holdout.
**Hash verification:** `verify_protected_hashes(REPO)` run before analysis — **0 mismatches** (VERIFIED).

---

## 1. Exact EBR formulation (VERIFIED)

Source: `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py:191-232`, function `compute_variant_sw_ebr` — the function PC-SW actually invokes via `arm_ebr("PC-SW", …)` in `planner_cf_campaign_runner.py:71`.

```
E_SW[t] = (1/η_dis) · Σ_{k=t}^{min(t+5,23)} max(0, critical_demand[k] − solar[k] − wind[k]) · dt
```

- **Critical-demand source:** `adapt_critical_demand_vector(11600.0, bundle.demand.point)` — forecast total demand clipped to the governed 11,600 W critical ceiling (`system/research/research_critical_demand_adapter.py:37-42`).
- **Solar forecast source:** `bundle.solar_generation.point` — causal-NWP 24h-ahead point forecast (`system/forecasting/implementations/causal_nwp_physics.py`).
- **Wind forecast source:** `bundle.wind_generation.point` — deterministic baseline-engine formula, `last_observed_wind_generation + 5000·sin(h·π/6)` (`system/forecasting/implementations/baseline.py:75`), **not** weather-driven.
- **η_dis = 0.92**, governed (`system/config/battery.yaml`).
- **Horizon:** rolling 6-hour lookahead `[t, min(t+5,23)]`, recomputed fresh at every one of the 2,952 resolves from that resolve's own forecast only.
- **min_e_wh** = `200,000 × 20% = 40,000 Wh`.
- **Insertion:** `e_stage2_target[t] = ebr[t]` for `t<23`; `e_stage2_target[23] = max(ebr[23], terminal_target_wh=100,000)`. Layer-C row (`research_numerical_extractor_planner_cf_v1.py:306-310`): `e_next[t] + s_J2[t] ≥ e_stage2_target[t] + min_e_wh`, present only when `reserve_enabled=True`.
- **J2 slack semantics:** `s_J2[t]≥0` is a shortfall/relief variable, not a hard floor by itself; it becomes a hard per-hour floor only once the hierarchy pins `ΣJ2=0`.
- **Priority ordering, VERIFIED from source:** `PRIORITY = {"J1":5, "J_NC":4, "J2":3, "J3":2, "J4":1}` (`research_numerical_extractor_planner_cf_v1.py:85`).
- **Causal/non-anticipative:** VERIFIED — every EBR input is computed from forecast + current state only, before the MILP is built; no optimizer decision variable feeds back into EBR.
- **Terminal-target interaction:** only enters the horizon-end slot (`t=23`) of whichever 24-hour plan is being solved "right now" — this is *not* the same thing as the calendar-day's actual hour 23, because the rolling architecture re-plans every real hour (see §4).

No part of this formulation was altered for this investigation.

---

## 2. Population-level EBR binding audit (VERIFIED, from persisted `PC_HOURLY_TELEMETRY.csv`, no re-solve required)

`margin[t] = e_next[t] − (ebr_target[t] + min_e_wh)`, where `e_next[t]` is the *realized* post-execution battery energy (`soc_after/100 × 200,000`) and `ebr_target[t]` is that same real hour's own freshly-computed target (both fields persisted directly in the certified telemetry).

Binding tolerance definitions (documented, not tuned to produce a result): **binding** = `margin ≤ 200 Wh` (0.1% of capacity); **near-binding** = `200 Wh < margin ≤ 4,000 Wh` (2% of capacity); **slack** = `margin > 4,000 Wh`.

| Population (n=2,952) | Count | % |
|---|---|---|
| EBR binding | 41 | 1.4% |
| EBR near-binding | 19 | 0.6% |
| EBR slack | 2,892 | **98.0%** |

Margin distribution (Wh): min **−47,063.0**, P10 **25,140.0**, P25 **49,240.0**, median **78,691.2**, mean **75,415.2**, P75 **101,060.0**, P90 **122,815.9**.

By hour-of-horizon: margin is tightest (more binding events) around real-hours 3–7 and 20–23 (overnight/evening low-solar stretches); slackest around hours 13–16 (midday, post-solar-charge). Negative margins (realized SOC below that hour's own fresh target) occur only at hours 3–7, 20–23 and are attributable to the already-documented plan-vs-realization divergence (Arm-A executor), not to EBR itself being violated at the *planning* level — `J2_shortfall = 0` in **100% of all 2,952 resolves** (VERIFIED), confirming the planned row is never left unsatisfied; the margin's occasional negativity is a *realized*-state phenomenon downstream of the plan.

By origin: tightest-margin origins (most binding pressure somewhere in their day) are **origin 91 (min margin −47,063 Wh)**, origin 10 (−27,253 Wh), origin 36 (−10,743 Wh) — a small minority; most origins never approach binding.

**Important distinction preserved (per your instruction): `J2_shortfall=0` is a planning-level statement (the row's relief variable is unused); it is not the same claim as "the row is physically tight" — 98.0% of resolves have the row satisfied with large slack, not merely satisfied.**

---

## 3. Diesel-funded banking (VERIFIED, from persisted telemetry)

| Metric | Value |
|---|---|
| Diesel-on resolves | 547 / 2,952 (18.5%) |
| Diesel-on **and** simultaneously charging | 526 / 547 (96.2%) |
| **Fuel consumed in diesel+charging hours** | **8,557.77 L of 8,729.2446 L total (98.04%)** |
| Diesel+charging hours that also curtail | 135 / 526 |

**Almost all certified PC-SW fuel (98.04%) is burned in hours where diesel is simultaneously charging the battery** — pure load-only diesel (no concurrent charge) is a rare event (21/547 hours). This is consistent with, but does not by itself prove, EBR as the cause (charging could in principle be opportunistic rather than reserve-driven) — causality is established separately in §6/§7, not inferred from this correlation alone.

---

## 4. EBR vs. terminal-target separation (VERIFIED/DERIVED)

The rolling EBR row is recomputed and enforced at **every** one of the 2,952 real-hour resolves — it is not a once-per-day artifact. The fixed 100,000 Wh terminal floor, by contrast, only ever enters the *last* slot of whichever 24-hour plan is currently being solved; because the controller re-plans every real hour, the calendar-day's actual hour 23 is reached as "hour 0" of dozens of intervening re-plans before the terminal slot it was originally computed for is ever realized. **The rolling EBR does not inherit the previously-identified "fixed-terminal-constraint invalid as a universal realized bound" defect** — its per-hour floor is the slice that is actually executed at realization time. This matches the finding already established in the Rule-D governance record and is not contradicted here.

---

## 5. Forecast-error contribution (DIAGNOSTIC for one representative case; UNKNOWN at population scale)

For origin 2 (previously examined, re-confirmed here): forecast solar = realized solar = 0 at hour 0 (midnight); forecast wind = realized wind exactly, hours 0-5 (`[7000, 8830.1, 9500, 8830.1, 7000, 4500]` both). For this resolve, **forecast error contributes ~zero** to the EBR target — the mechanism is the formula's inherent forward-provisioning requirement, not forecast pessimism.

**A population-scale forecast-vs-realized shortfall decomposition (Phase 5/6 of the request, at full granularity) was NOT performed** — it would require re-deriving the forecast bundle (not just the realized values, which are persisted) for all 2,952 resolves and tracing each EBR-binding episode's 6-hour window individually. This is marked **UNKNOWN** rather than extrapolated from the single case above.

---

## 6. Full-population counterfactual diagnostic (DIAGNOSTIC — explicitly not a policy candidate)

Using the model's own already-existing `reserve_enabled` constructor flag (unmodified code) to remove Layer-C/`J2` entirely, the **full closed-loop, 123-origin, read-only re-solve** was run (not a single isolated hour — the complete rolling-horizon simulation, fuel-state feedback included). Output persisted at `PC_SW_EBR_OFF_HOURLY_TELEMETRY_DIAGNOSTIC.csv` in this directory; solver status checked clean (0 non-optimal rows, 0 busbar errors >1e-2 W, 0 SOC bound violations).

| Metric | Baseline (EBR on) | Diagnostic (EBR off) | Δ |
|---|---|---|---|
| **Total fuel (L)** | 8,729.2446 | **8,004.6897** | **−724.5549 L (−8.30%)** |
| Diesel energy (Wh) | 23,976,984.68 | 21,638,755.27 | −2,338,229.4 |
| Diesel-on hours | 547 | 519 | −28 |
| Critical unmet (Wh) | 279,056.33 | 279,599.90 | **+543.57** |
| Total unmet (Wh) | 985,870.15 | 1,015,209.32 | +29,339.17 |
| Curtailment (Wh) | 13,209,785.48 | 12,613,127.64 | −596,657.84 |
| Battery charge (Wh) | 25,086,130.82 | 23,836,590.83 | −1,249,540.0 |
| Battery discharge (Wh) | 17,503,789.63 | 17,966,481.98 | +462,692.4 |
| **R_CF (critical reliability, %)** | 99.185075 | 99.183488 | **−0.0016 pp** |
| **R_P (proportional reliability, %)** | 97.773554 | 97.707296 | **−0.0663 pp** |

**Per-origin heterogeneity (DIAGNOSTIC, decisive for the "mixture" question):** removing EBR is **not** uniformly beneficial. **77 / 123 origins** show *less* fuel with EBR off (median −4.42 L, best −52.39 L); **44 / 123 origins** show *more* fuel with EBR off (up to +22.62 L); 2 origins are unchanged. This is a genuine, population-verified **mixture** — in roughly a third of origins, the reserve mechanism's forward provisioning is closed-loop fuel-*saving* once its downstream effect on that origin's specific weather trajectory is played out; in the majority it is a net fuel cost with no compensating benefit realized in this specific 2025 holdout weather.

**Mechanism breakdown (DERIVED):** fuel reduction comes with **less** total charging (−1.25 MWh) **and more** discharging (+0.46 MWh) — consistent with "eliminated banking, relying on direct discharge instead" (mechanism 1/3 of the Phase-7 menu), not from increased renewable utilization (curtailment *decreased*, not increased, under EBR-off) and not primarily from shifted diesel timing alone (diesel-on hour count also dropped, −28). The modest increase in **non-critical** unmet load (+28,795 Wh, i.e. total-unmet increase minus critical-unmet increase) — while critical unmet is essentially flat (+543.57 Wh, 0.19% relative, consistent with closed-loop numerical noise rather than a systematic degradation) — shows the reserve's realized protective value falls almost entirely on **non-critical service smoothing**, not on critical-load survival, in this population.

---

## 7. Future-need test (Phase 8 — central output)

**Full per-episode A/B/C/D classification (hundreds of individual diesel-funded charging events, each traced through its own forward discharge path) was NOT performed at full granularity** — this would require event-by-event energy tracing across all 526 diesel+charge hours, which was not completed in this pass. This is marked **UNKNOWN** at the per-episode level, per the anti-hallucination instruction, rather than estimated.

What **is** established, at the aggregate/population level (DIAGNOSTIC, not per-episode):
- **44/123 origins** (fuel increases when EBR removed) are consistent with category **A/B (needed)** — removing the reserve there costs more fuel downstream, meaning the banked energy was, at the population level, doing real protective work in the realized trajectory of those specific origins.
- **77/123 origins** (fuel decreases when EBR removed, with **no** origin-level critical-unmet penalty large enough to show in the ~flat aggregate R_CF) are consistent with category **C (not needed in the realized trajectory)** for the *portion* of reserve attributable to those origins — the banked energy's insurance value was never called upon.
- Because the ±0.0016pp aggregate R_CF delta is within plausible closed-loop/realization noise, no population-level claim of a **D (indeterminate)** boundary case being resolved either way is made.

**This aggregate-level A/B/C split (44 vs. 77 origins) is the closest defensible answer to the per-episode question posed; it is explicitly a DERIVED, origin-level proxy, not the requested per-event classification.**

---

## 8. Battery round-trip loss accounting (DERIVED, aggregate only — not per-event traced)

Aggregate Δcharge (−1,249,540 Wh) and Δdischarge (+462,692.4 Wh) between baseline and EBR-off are not directly comparable as a clean "loss" figure, because they reflect two different realized trajectories (not a single traced energy parcel). A rigorous per-event charge→store→discharge trace (as Phase 6 requests) was **not performed** — marked **UNKNOWN**. The theoretical round-trip loss rate for *any* fully-cycled banked unit of energy under this battery's governed efficiencies is `1 − η_chg·η_dis = 1 − 0.92×0.92 ≈ 15.4%` (VERIFIED from `system/config/battery.yaml`), cited here as the governed physical constant, not as a population-attributed total.

---

## 9. Non-arbitrary lever search (Phase 9)

No parameter-free, non-arbitrary lever is supported by this evidence. The decisive obstacle is the **44-vs-77 origin split (§6)**: any rule that reduces EBR conservatism *uniformly* would help the 77 "unneeded" origins but actively harm the 44 "needed" origins — and distinguishing which type a given origin/day will be, **before** its outcome is realized, is exactly the information a non-hindsight, non-anticipative rule cannot have (using the realized split to build the rule would itself be the forbidden hindsight pattern). No governed quantity in the existing formulation (solar/wind/demand forecast, SOC, fuel-remaining, current EBR target) was found, by this analysis, to reliably separate the two populations *in advance* — establishing that would require a forecast-skill/confidence-interval study genuinely absent from this investigation, not a threshold choice. **No causal lever is proposed.**

---

## 10. Safety / governance

No governed safety requirement was touched. Critical-first service (`J1`), `J_NC` priority, SOC floor, fuel feasibility, EBR causal/non-anticipative semantics, and S1/S2/S3 gate definitions are all unmodified; the diagnostic re-solve used only the existing `reserve_enabled=False` constructor path, already present in the frozen research optimizer, applied read-only and not promoted. The diagnostic's own R_CF delta (−0.0016pp) is reported, not concealed, and is explicitly **not** used here to argue reserve protection is unnecessary — it is one data point under one specific realized 2025 weather trajectory, not a generalizable safety claim.

---

## 11. Governance classification

**D — EBR driver confirmed, but no safe parameter-free lever exists.**

EBR is unambiguously a material, population-verified causal driver of PC-SW diesel fuel (−8.30% aggregate fuel under full closed-loop removal, §6) — not primarily forecast-error-driven (§5, to the extent tested) and not uniformly "wasted" conservatism either: it is a genuine **mixture** (§6/§7), beneficial in roughly a third of origins and a net cost with no realized benefit in the remaining two-thirds, for this specific holdout year. The population-level evidence is now substantially more complete than the prior single-resolve pass, but it does not surface any mechanism — parameter-free or otherwise — capable of separating the "needed" from the "unneeded" portion in advance without either hindsight or an invented threshold. This is classification **D**, not B (more evidence-gathering would need to target forecast-skill/confidence structure specifically, a different kind of study, not simply "more of the same"), and not A (no intervention is specified).

---

## 12. AGY specification

Not applicable — classification is D, not A. No experiment is specified.

## Limitations

- Per-event (Phase 3/4) energy tracing and per-episode (Phase 8) A/B/C/D classification were not performed at full granularity — only aggregate/origin-level proxies are reported, explicitly labeled.
- Forecast-vs-realized shortfall decomposition (Phase 5/6) was only verified for one representative resolve (origin 2); population-scale forecast reconstruction was not performed.
- The EBR-off diagnostic removes the mechanism entirely (the only variant the existing code supports via `reserve_enabled`); no intermediate/partial-reserve variant was tested, since any such variant would require inventing a parameter, explicitly disallowed.

"NO POLICY EXPERIMENT WAS EXECUTED."
