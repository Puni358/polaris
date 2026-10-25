# MILP-v2 Diagnostic Branch: Full 347-Origin Causal Decomposition

**Scope**: Read-only instrumentation pass over all 347 R2 origins (490 NORMAL-route + 204
EMERGENCY-route cycles, 694 total). **No optimizer behavior, R1/R2 assumption, model,
production code/config, objective weight, or terminal formula was changed.** The real,
unmodified `GAP19HighsNativeOptimizer.optimize()` was called exactly as R1/R2 call it, using
the exact same R2 baseline and Stage 8.1 inputs (hashes re-verified: matrix and model both
MATCH R1/R2's values). **No counterfactual re-solve was performed** — every cycle was
solved exactly once, under the single real objective. Raw data:
`FULL_DIAGNOSTIC_RAW_RESULTS.json`.

**Limitation, stated once and carried throughout**: every "binding vs. non-binding"
diesel split below is a **same-timestep association** (what diesel is dispatched at an hour
where that hour's own reserve constraint happens to be active), not a causal isolation. The
MILP solves all 24 hours jointly; this report does not claim to isolate what diesel would
disappear if a given mechanism were removed — that would require a counterfactual re-solve,
explicitly not done here.

---

## 1. Native EBR (t = 0–22): zero contribution, confirmed at full scale

Across all 490 NORMAL-route cycles (245 per arm), **the native EBR constraint (t<23) never
binds, for either arm, in a single cycle.** `binding_timesteps` contains only `[23]` or `[]`
in every one of the 490 cycles — never any other index. This fully generalizes the 3-origin
validation finding to the complete window: the governed EBR formula is not a measurable
contributor to the diesel difference anywhere in R2.

## 2. Research terminal-target (t = 23): binds more often under Stage 8.1, confirmed exactly

| | Baseline | Stage 8.1 corrected |
|---|---|---|
| Cycles where t=23 binds (of 245) | 98 | 125 |

These counts match R2's own `planned_reserve_shortfall_wh` nonzero counts exactly (98/245
and 125/245, as reported in the prior causal forensic report) — the instrumentation is
internally consistent with R2's own stored results.

## 3. Diesel decomposition by same-timestep binding status (full window, both arms, W-sum
over all 24 hourly values × 245 NORMAL cycles each)

| | Baseline | Stage 8.1 | Δ (Stage8.1 − baseline) | Δ share of total |
|---|---|---|---|---|
| Diesel at binding timesteps (always t=23, since EBR never binds) | 5,637,054.1 | 7,485,776.9 | +1,848,722.7 | **11.73%** |
| Diesel at non-binding timesteps (t=0–22, and t=23 in non-binding cycles) | 9,116,213.0 | 23,032,628.5 | +13,916,415.5 | **88.27%** |
| **Total** | 14,753,267.1 | 30,518,405.4 | **+15,765,138.2** | 100% |

**This confirms, at full scale, the correction identified in the small-sample validation:
the large majority of the measured diesel increase (88.27%) occurs at hours where that
cycle's own reserve constraint is not binding at all.** Only 11.73% of the total diesel
increase is associated with an hour where the terminal-reserve envelope is actively
constraining the solution.

## 4. Diesel at hour t=23 specifically, aggregated across ALL cycles (binding or not)

| | Baseline | Stage 8.1 | Δ | Δ as % of total diesel delta |
|---|---|---|---|---|
| Diesel at t=23, summed over all 245 cycles | 11,320,035.9 | 11,351,813.3 | +31,777.3 | **0.20%** |

Even accounting for *every* cycle's hour-23 diesel (not only the binding ones), the
aggregate difference between arms at that one hour is **negligible (+0.20% of the total
diesel delta)**. The terminal-reserve mechanism's own hour is not where the diesel increase
is concentrated, in the aggregate.

## 5. Battery charge / discharge / SOC (full window, NORMAL cycles)

| Metric | Baseline | Stage 8.1 corrected | Δ |
|---|---|---|---|
| Battery charge, W-sum (24h × 245 cycles) | 41,269,236.8 | 38,658,765.1 | −2,610,471.7 |
| Battery discharge, W-sum | 28,635,627.8 | 26,575,094.9 | −2,060,532.9 |
| SOC % — min / mean / max (across all timesteps, all cycles) | 52.08 / 75.04 / 95.0 | 45.22 / 73.68 / 95.0 |

(These W-sum figures match the previously-reported planned charge/discharge Wh totals from
R2 to within rounding — confirms this instrumentation pass reproduces R2's own physical
results exactly, as expected since nothing about the optimizer or inputs changed.) Stage
8.1's SOC trajectory reaches a lower minimum (45.22% vs. 52.08%) — consistent with less
solar being available to keep the battery charged, independent of whether the reserve
constraint happens to bind at any given hour.

## 6. Strict J2-before-J3 priority

Not separately quantifiable as a diesel amount — it is the rule, confirmed unchanged in code
(`gap19_highs_native.py:349,365-385`), that allows §3's binding-timestep diesel to occur at
all. Its "contribution" is structural, not a quantity measured in liters or watts; this
report does not assign it a number, consistent with the instruction not to infer causality
beyond what the instrumentation supports.

---

## Summary: full-window quantified decomposition

| Mechanism | Measured full-window contribution |
|---|---|
| Native GAP19 EBR (t<23) | **0%** — never binds in any of 490 cycles |
| Research terminal-target, same-hour (t=23) effect | **11.73%** of the total diesel delta (same-timestep association, binding cycles only); **0.20%** of the total delta when measured as the aggregate hour-23 difference across all cycles regardless of binding |
| Direct energy balance (diesel at non-binding hours) | **88.27%** of the total diesel delta |
| Strict J2-before-J3 lexicographic priority | Structural enabler only — not a quantity; without it, the 11.73%/0.20% figures above would not exist, but it contributes nothing on its own in the absence of a binding reserve constraint |

**This full-window pass confirms and sharpens, rather than contradicts, the 3-origin
validation finding**: the direct energy-balance effect — diesel dispatched at hours where
the reserve envelope is not the active constraint — is the dominant, same-timestep-associated
driver of the measured diesel increase. The terminal-reserve mechanism's own same-hour
footprint is real but small (11.73% of the delta when binding; a mere 0.20% of the delta
when averaged across all cycles including non-binding ones).

## What this does NOT establish (explicitly, per instruction)

- This is an **association**, not a causal isolation. The MILP solves jointly; diesel at a
  non-binding hour could still, in principle, be partly motivated by anticipating a *later*
  binding hour's requirement (e.g., pre-charging). This report does not measure or rule out
  that possibility — doing so would require a counterfactual re-solve, not performed here.
- No new terminal-reserve formula, objective weighting, or optimizer change was chosen or
  implemented.
- R1 and R2 remain frozen, unmodified controls; this diagnostic branch
  (`POLARIS_EMS_GAP19_MILP_V2_DIAGNOSTIC_BRANCH/`) is additive instrumentation only and is
  not wired into `worker.py` or any production path.

## STOP

Full 347-origin instrumentation pass complete. No optimizer behavior changed. No
counterfactual re-solve performed. R1/R2 untouched.
