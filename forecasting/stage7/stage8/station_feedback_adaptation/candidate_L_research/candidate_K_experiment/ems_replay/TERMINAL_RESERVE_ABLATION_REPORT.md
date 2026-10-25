# Terminal Reserve ON/OFF Ablation — Does the Terminal-Reserve Constraint Cause K's EMS Degradation?

**RESEARCH-ONLY. No production, Stage 8.1, F, or K code/artifact was modified. F and K were
not retrained or regenerated. Nothing promoted. Candidate K remains research-only.**

## Question

`K_EMS_DEGRADATION_FORENSICS.md` identified the terminal-reserve target/constraint as the
primary channel through which K's late-window solar forecast shifts translate into more
unmet critical load — based on strong correlational evidence (r≈0.8) and two worked hourly
examples, explicitly flagged as "solver-level isolation: partial." This experiment runs the
**controlled ablation** that forensic analysis alone could not: does removing the
terminal-reserve constraint make K's degradation largely disappear, or does it persist?

## Method

2×2 factorial, same 347 2024 origins, same validated EMS replay methodology
(`run_actual_solar_replay.replay_plan_against_actual_solar`, `pv_from_sw_in`,
`run_candidateF_actual_solar_replay.predict_solar_bundle`, `run_full_experiment.build_components`
/ `verify_frozen_manifest`, all imported unmodified) used throughout this research line:

| | Terminal reserve ON (existing, unmodified) | Terminal reserve OFF (new) |
|---|---|---|
| **F forecast** | Control, already measured (`EMS_REPLAY_REPORT.md`) | New |
| **K forecast** | Already measured (the original degradation result) | New |

**OFF implementation** (`terminal_reserve_ablation.py`): `configs["terminal_target_wh"] = 0.0`,
in place of the frozen `rfe.compute_terminal_target_wh(bundle)` call. Verified by direct
inspection of `system/optimization/implementations/gap19_highs_native.py` (lines 129–151):
the only place `terminal_target_wh` is used is

```python
e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)
```

Setting it to `0.0` makes this `max()` reduce to `ebr_target_wh_list[23]` alone (the
governed EBR 6-hour-lookahead survivability requirement, which is never negative) — i.e.
**only the terminal-reserve override is removed**. Confirmed unchanged by the same
inspection:
- `ebr_target_wh_list[t]` for all `t`, including `t=23`'s own baseline value — computed
  purely from `critical_demand`, independent of `terminal_target_wh` and of which solar
  forecast is used.
- The normal battery SOC floor/ceiling (`min_e_wh`/`max_e_wh`, `lb`/`ub` on the energy
  variable) — hard bounds set elsewhere, untouched by this config key.
- Charge/discharge limits, diesel constraints, load constraints, optimizer settings
  (`optimizer.yaml`, verified by hash via `rfe.verify_frozen_manifest()`), and all replay
  mechanics (`replay_plan_against_actual_solar`, imported unmodified).

No other parameter was changed in either arm.

## Results

Origin-level: `terminal_reserve_ablation_origin_level.csv` (347 origins, 4 cells each).
Aggregate: `terminal_reserve_ablation_results.csv`. Full detail: `TERMINAL_RESERVE_ABLATION_MANIFEST.json`.

245 of 347 origins routed `NORMAL` in all four cells (F×ON, K×ON, F×OFF, K×OFF) — identical
`NORMAL` count to the original two-arm replay (0 route mismatches introduced by turning the
reserve off). 0 optimizer failures in any cell.

Paired (origin-level, n=245), positive `paired_delta_f_minus_k` = F worse than K; negative =
K worse than F. 95% CIs from a 2000-iteration origin-level paired bootstrap, seed 42.

| Metric | ON: Δ(F−K) mean | ON 95% CI | OFF: Δ(F−K) mean | OFF 95% CI |
|---|---|---|---|---|
| Unmet load (Wh/origin) | **−516.60** | [−729.60, −300.45] | **−474.67** | [−671.10, −279.92] |
| Diesel fuel (L/origin) | +0.19 | [−0.05, 0.44] | +0.04 | [−0.11, 0.21] |
| Diesel-on hours | −0.008 | [−0.037, 0.020] | +0.025 | [0.004, 0.049] |
| Diesel startups | −0.020 | [−0.053, 0.012] | −0.025 | [−0.045, −0.008] |
| Curtailment (Wh/origin) | −18.33 | [−401.94, 366.86] | +67.68 | [−290.52, 450.12] |
| Battery EFC | +0.0028 | [0.0002, 0.0052] | −0.0015 | [−0.0029, −0.0001] |
| SOC-floor violations | 0.0 | [0, 0] | 0.0 | [0, 0] |
| Terminal SOC (%) | +0.22 | [0.081, 0.353] | −0.354 | [−0.530, −0.200] |
| Solve time (s) | −0.187 | [−0.544, 0.014] | −0.200 | [−0.632, 0.036] |

Side effect of removing the terminal reserve (both arms, as expected): diesel fuel drops
sharply (~44 L → ~11 L mean), diesel-on hours drop (~2.6 h → ~0.8 h), battery EFC drops
(~0.65 → ~0.51), and terminal SOC collapses from ~90% to ~43% — the optimizer no longer has
any incentive to end the day with a high battery reserve, exactly as expected when the only
mechanism requiring that reserve is removed. A small number of SOC-floor violations appear
under OFF (mean 0.0122/origin, ≈3 of 245 origins) that were absent under ON — consistent
with removing a reserve constraint occasionally letting SOC run closer to its hard floor.

## Primary comparison: (F+OFF vs K+OFF) vs (F+ON vs K+ON)

**Direct double-difference test** (same 245 origins, paired within-origin):

```
ON  unmet-load gap  (F − K): −516.60 Wh/origin
OFF unmet-load gap  (F − K): −474.67 Wh/origin
double-difference (ON gap − OFF gap): −41.93 Wh/origin
double-difference 95% CI (2000-iter paired bootstrap): [−119.35, +41.58]
```

The double-difference CI **includes zero**. The reduction in K's disadvantage when the
terminal reserve is removed (−516.60 → −474.67, an 8.1% reduction) is **not
statistically distinguishable from no change** at the 95% level. The two single-mode CIs
(ON: [−729.60, −300.45]; OFF: [−671.10, −279.92]) overlap heavily, visually confirming the
same conclusion.

## Interpretation

**K's EMS degradation does NOT largely disappear with the terminal reserve removed. It
remains, at a statistically indistinguishable magnitude, even with that mechanism switched
off entirely** (and with the governed EBR requirement, SOC bounds, and all other constraints
held fixed). This is a clear, controlled, negative result for the terminal-reserve
hypothesis as the *primary* cause.

This **corrects, rather than merely qualifies**, the strength of
`K_EMS_DEGRADATION_FORENSICS.md`'s conclusion. That report was explicit that its
solver-level isolation was "partial," built from correlational evidence (r≈0.8 between
late-window solar delta and unmet-load delta) and two hand-picked worked examples — it never
ran a controlled ablation. This experiment supplies that ablation, and the result is that
the terminal-reserve channel, while real and mechanistically coherent (it is still visibly
present in the hourly worked examples the forensics report showed, and the terminal-SOC/
EFC/diesel side-effects here confirm the mechanism itself operates as described), accounts
for at most a small, statistically unconfirmed fraction (point estimate ~8%, CI consistent
with zero) of the aggregate ~517 Wh/origin degradation. **The dominant driver of K's EMS
degradation lies elsewhere** — most plausibly in how K's differing (and, per the forensics
report, highly volatile day-to-day) solar point forecast changes the optimizer's ordinary
daytime charge/discharge/diesel allocation through the governed EBR requirement and the base
dispatch objective, independent of any terminal-SOC target. This experiment does not
identify what that other mechanism is — that would require a further, differently-scoped
ablation (e.g. an EBR-off or solar-forecast-blend ablation), not attempted here.

This also means: a future "uncertainty-aware terminal reserve" fix (the research line this
ablation was launched to help validate) would, even if successfully implemented, very likely
leave most of K's EMS degradation unaddressed, because the terminal-reserve mechanism is not
where most of the degradation originates.

## Files

- `terminal_reserve_ablation.py` — the ablation script
- `terminal_reserve_ablation_origin_level.csv` — per-origin, per-cell raw metrics (347 origins × 4 cells)
- `terminal_reserve_ablation_results.csv` — paired summary metrics + bootstrap CIs, both reserve modes
- `TERMINAL_RESERVE_ABLATION_MANIFEST.json` — full per-origin detail, hashes, config, summary
- `TERMINAL_RESERVE_ABLATION_REPORT.md` — this report

## Governance

K remains research-only. Nothing is promoted. This experiment is evidence *against* the
terminal-reserve constraint being the primary, actionable lever for fixing K's EMS behavior
— it does not, by itself, support or motivate implementing an uncertainty-aware terminal
reserve as a sufficient remedy. The underlying forecast-accuracy-vs-EMS-outcome disconnect
documented in `EMS_REPLAY_REPORT.md` stands; this experiment narrows down (and revises) where
that disconnect comes from, without yet locating it.
