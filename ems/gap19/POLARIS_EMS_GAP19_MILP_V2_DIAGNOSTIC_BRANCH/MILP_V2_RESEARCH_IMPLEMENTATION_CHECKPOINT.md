# MILP v2 — Research-Only Implementation Checkpoint

**Checkpoint timestamp**: 2026-10-03T08:15:32Z (UTC)
**Status**: Implementation + focused validation + smoke test complete. Research-only.
**No broad simulation has yet been run.** This checkpoint records what exists so far; it
does not authorize, schedule, or constitute the 347-origin (or any other) experiment.

This document is a point-in-time record only. It does not modify, and was not produced by
modifying, any control or V2 code. No code, config, or model was changed to create it.

---

## CONTROL

The frozen, unmodified GAP19 Option-B MILP and its supporting production infrastructure.
None of these files were edited at any point in this work. Hashes below are the current
on-disk SHA256 of each file, recorded for future drift detection — not evidence of a
change (none occurred).

| File | Role | SHA256 |
|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | Frozen control MILP (GAP19 Option B) | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/optimization/implementations/option_d.py` | Frozen Option D fallback solver | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` |
| `system/control/ecd.py` | Frozen Emergency/Control Decision logic | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` |
| `system/orchestration/worker.py` | Production orchestration (optimizer selection, Gate-02 infeasibility handling) | `829a06556e7085858ec816ac7d0d1e8dbc99c8c41e3da0cde4e453566fbc0323` |
| `system/runtime/runner.py` | Production runtime optimizer dispatch | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` |
| `system/orchestration/manifest.py` | Protected-file integrity manifest (lists GAP19/OptionD/ECD/router/simulator/runner as `PROTECTED_FILES`) | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` |
| `system/config/loads.yaml` | Production loads configuration (`critical_load`, `deferrable_loads`, `curtailable_loads`) | `eacb84d1c25f8768de0ee0cf8fdb286d4dbc9254824d7c17aea738cbe9774467` |
| `system/tests/test_gap19_j2_option_b.py` | Pre-existing GAP19 unit tests (used here as control-regression check, not modified) | `7f84b6d45e70c12049d7d074c5d0701466e9a5ceb90b318441750f65aef00a52` |

None of `gap19_highs_native.py`, `option_d.py`, `ecd.py`, `worker.py`, `runner.py`,
`manifest.py`, or `loads.yaml` appear in the "RESEARCH V2" section below as modified — they
are listed here solely as fixed reference points.

---

## RESEARCH V2

Files created or modified to implement the v2 Essential-tier extension. These are the
**only** files touched during this work.

| File | Status | Role | SHA256 |
|---|---|---|---|
| `system/optimization/implementations/gap19_highs_native_milp_v2_research.py` | **Created** (535 lines) | Isolated research-only optimizer, `GAP19HighsNativeOptimizerMILPV2Research` | `5e24ecc17abe4104746425b2fb96c0594473a3bbdf43201fc50a60c98835e6c0` |
| `system/tests/test_gap19_milp_v2_research.py` | **Created** (249 lines) | 10 focused unit tests for the V2 implementation | `89fc0bbabf30fcf1398ef24718194998023d86f418106d15cc66880177c82a3b` |
| `system/schemas/dispatch_plan.py` | **Modified** — additive only | Added two optional fields: `load_served_essential`, `unmet_essential` (keyword-only, default `None`, omitted from `to_dict()` when unset) | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` |

**Isolation, confirmed by repo-wide grep**: `GAP19HighsNativeOptimizerMILPV2Research` /
`gap19_highs_native_milp_v2_research` appear in no file other than the two created above.
Not referenced in `worker.py`'s or `runner.py`'s optimizer-selection branches, not added to
`manifest.py`'s `PROTECTED_FILES`, not in any production config.

**V2 is research-only and not production-wired or authorized for production use.** No
human execution authorization has been sought or granted for any production run of this
optimizer. It exists solely to produce offline dispatch plans for comparison against GAP19.

### Rev. 3 design elements implemented
- Essential-demand clipping: `essential_demand[t] = min(max_power_w, max(0, demand[t] - critical_demand[t]))`
- `p_served_essential[t]`, `P_unmet_essential[t]` decision variables (vars 408–455, N=456 total)
- Bus-bar balance amended to sink `p_served_essential`
- Demand-side balance amended to the 3-way split `p_served + p_served_essential + p_unmet = demand`
- New Essential-tier balance constraint: `p_served_essential + P_unmet_essential = essential_demand`
- `P_unmet_essential` folded into the existing `J4` objective at the **identical** existing
  curtailment coefficient (`1.0 * dt`) — no new stage, no new number
- Infeasibility → OptionD routing: **withdrawn**, not implemented; V2 returns the same
  fail-closed `OPTIMIZATION_INFEASIBLE` shape as GAP19 and never calls `OptionDFallbackSolver`
- `deferrable_loads` scheduling semantics: **not implemented** (out of scope, confirmed absent by grep)

---

## SIMULATED ASSUMPTIONS

- **`curtailable_loads` (`secondary_heating`) → Tier 2 (Essential/Flexible) is labeled a
  `SIMULATED_RESEARCH_ASSUMPTION`, not a derived fact.** No governance document in this
  repository states which tier `curtailable_loads` belongs to; `TIER2_MAPPING_COMPARISON.md`
  and `REV3_UNRESOLVED_ITEMS_AUDIT.md` item 2 both leave this open, and the latter surfaces
  new counter-evidence (`deferrable_loads`' `priority: 2` field) that *weakens* rather than
  resolves this assumption. V2's code and docstring state this explicitly rather than
  presenting it as resolved.
- Flat (time-invariant) hourly `essential_demand[t]` profile — the only non-inventive choice
  given `curtailable_loads`' schema has no time-of-day field.
- `max_power_w` for the Essential tier is read from `config["loads"]["curtailable_loads"][0]`
  (defaulting to the schema's `5000.0` W if absent), not from a governed input.

---

## KNOWN LIMITATIONS

- **Infeasibility → OptionD routing remains unresolved** (per `REV3_UNRESOLVED_ITEMS_AUDIT.md`
  item 1): the real existing fallback for MILP-level infeasibility lives in
  `worker.py` (Gate-02 Option C relaxed re-solve → `BLOCKED_INFEASIBLE` halt if the relaxed
  re-solve also fails), not in `OptionDFallbackSolver`. That relaxation mechanism is itself a
  **pre-existing, inherited defect in the frozen control**
  (`allow_flexible_load_relaxation` is set by `worker.py` but never read anywhere in
  `gap19_highs_native.py`) — not introduced or fixed by V2, and not a blocker for V2's scope.
- **`deferrable_loads` scheduling semantics are not modeled.** Out of scope for v2 as
  specified.
- **Tier 2 vs. Tier 3 mapping for `curtailable_loads` remains genuinely open**, with new
  counter-evidence (the `priority: 2` field on `deferrable_loads`, which has no counterpart
  on `curtailable_loads`) not yet resolved by any governance input.
- **MILP tie-breaking / solver-path degeneracy** (see Smoke Test, Scenarios 3 & 5 below):
  when multiple battery/diesel dispatch schedules achieve bit-identical J1–J4 objective
  values, GAP19 and V2 can land on different specific hour-placements, because V2's larger
  variable count (456 vs. 408) changes HiGHS's branch-and-bound traversal order. This is an
  inherent characteristic of the frozen diesel unit-commitment formulation under ties, not a
  behavior change to GAP19, and does not affect any audited invariant (critical service,
  essential service, demand/energy balance, battery/diesel physical validity, or any
  objective-stage value).
- **No broad simulation has been run.** All validation to date is: (a) 24/24 focused unit
  tests, and (b) 6 small, deterministic, hand-checkable smoke-test scenarios. The
  347-origin experiment (or any comparable large-scale run) has explicitly **not** been
  executed.
- Solve time in the current sandboxed environment is slow for harder MIP instances (up to
  ~140s per solve observed in the reserve-driven-charging smoke scenario) due to CPU/memory
  constraints of this environment — an environment characteristic, not a defect in either
  optimizer.

---

## Focused test result

```
24 passed in 1517.93s (0:25:17)
```
- 10/10 `system/tests/test_gap19_milp_v2_research.py` — V2-specific: clipping bounds,
  no double-counting, essential-vs-charging indifference resolved, 4-objective stage count
  unchanged, `DispatchPlan` round-trip, fail-closed on missing input, explicit confirmation
  GAP19's own output is unaffected (additive-only schema fields `None`/absent for GAP19 plans).
- 14/14 `system/tests/test_gap19_j2_option_b.py` — pre-existing GAP19 tests, unmodified,
  still passing — frozen control confirmed intact.

---

## Smoke test result (6/6 scenarios, all PASS)

Each scenario run through both GAP19 and V2, deterministic/hand-checkable inputs, no broad
simulation.

| # | Scenario | Result |
|---|---|---|
| 1 | Critical-only demand (essential_demand=0 everywhere) | **PASS** — V2 structurally inert, identical to GAP19 on every shared field |
| 2 | Critical+Essential, sufficient renewable | **PASS** — demonstrates the Rev.3 double-counting fix directly: GAP19 reports `unmet_load=4000` despite energy existing to serve it; V2 correctly serves it (`unmet_load=0`) |
| 3 | Critical+Essential, insufficient renewable | **PASS** — essential correctly never served (fuel-cost priority, J3 > J4, respected for all 24h); J1–J3 bit-identical between GAP19 and V2; J4 diverges by exactly the expected `4000×24×1.0dt = 96000` |
| 4 | Surplus renewable, Essential vs. battery charging | **PASS** — essential served 100% of all 24 hours; GAP19's charge rate exceeds V2's by exactly 4000W (the diverted essential amount) at every hour, confirming essential service strictly dominates charging in the objective |
| 5 | Reserve requirements legitimately require charging (essential_demand=0 by construction) | **PASS** — all four objective values (J1, J2, J3, J4) bit-identical between GAP19 and V2, confirming terminal reserve/EBR/diesel/battery logic is completely unmodified |
| 6 | Solver infeasibility / fail-closed (inverted SOC bounds) | **PASS** — both return identical `OPTIMIZATION_INFEASIBLE` fail-closed zero-dispatch plans; V2 confirmed not to invoke `OptionDFallbackSolver` |

**Scenario 3 / 5 equal-objective schedule-degeneracy finding** (explicitly carried forward,
not hidden): in both scenarios, the specific hour-by-hour diesel/battery charge-discharge
*schedule* differs between GAP19 and V2, while the J1–J4 *objective values* remain
bit-identical (Scenario 5: all four stages identical; Scenario 3: J1–J3 identical, J4
diverging only by the expected essential-tier term). This is attributed to MILP
branch-and-bound tie-breaking sensitivity to problem size (456 vs. 408 variables), inherent
to the frozen diesel unit-commitment formulation under degenerate ties — not a change to
GAP19's behavior, and verified not to affect any of the ten audited invariants.

---

## Terminal reserve / 4-stage lexicographic structure — unchanged, confirmed

- Terminal reserve target computation, EBR 6-hour lookahead formula, and the pointwise
  maximum reserve envelope are copied verbatim from GAP19 into V2 (line-by-line diff
  confirms no deviation beyond intended Rev.3 additions).
- The objective hierarchy remains exactly 4 stages: `J1 (Critical Deficit) > J2 (Governed
  Reserve Shortfall) > J3 (Diesel Fuel) > J4 (Curtailment [+ Essential, Rev.3])`, with
  priorities `4,3,2,1` and `blend_multi_objectives=False`, identical to GAP19. No 5th stage
  was introduced. Smoke-test Scenario 5 independently confirms this: when the essential tier
  is inert, all four objective values are bit-identical to GAP19.
- Fail-closed infeasibility behavior is preserved: V2 returns the same
  `OPTIMIZATION_INFEASIBLE: {status}` zero-dispatch `DispatchPlan` shape GAP19 returns on a
  non-`kOptimal` HiGHS status, and never calls `OptionDFallbackSolver`. Confirmed
  empirically in smoke-test Scenario 6.

## STOP

Checkpoint and manifest recorded. No control or V2 code altered to produce this document.
No new experiment run.
