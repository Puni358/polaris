# POLARIS — PC-SW v1.2 Diesel Decision Causal Decomposition

**Date:** 2026-10-08
**Status:** READ-ONLY forensic research. No production code, PC-SW semantics, objective weights, priorities, battery parameters, or governed campaign outputs modified. No policy campaign executed. No parameter tuned.
**Hash verification:** `verify_protected_hashes(REPO)` — **0 mismatches** (VERIFIED), re-checked before this analysis.

**Governed baseline (VERIFIED, as supplied and cross-checked against certified telemetry):** Fuel 8,729.2446 L; Control 10,196.9712 L; saving 14.39%; diesel-on 547 h; diesel starts 335; diesel energy 23,976.98 kWh; diesel+charging 526/547 h; diesel+curtailment 147 h.

---

## Scope and method limitation (stated upfront, per the anti-hallucination rule)

Full 24-step internal MILP reconstruction (`last_planned[0..23]`, per-hour `J1..J4`) for **all 547 individual diesel-on hours** was **not performed** — that would require re-running the closed loop for all 123 origins while instrumenting every resolve's full internal vectors (not just the hour-0 slice the certified telemetry already persists), a scale of computation beyond what this pass completed. What **was** done, and is reported as such:

- **VERIFIED, full population (2,952 resolves):** every quantity already persisted in `PC_HOURLY_TELEMETRY.csv` for the certified baseline — diesel power, charge, discharge, SOC, EBR target, `j2_shortfall_wh`, curtailment, unmet load — aggregated and cross-tabulated across **all 547 diesel-on hours** (not a sample).
- **DIAGNOSTIC, full population:** the already-completed EBR-off closed-loop re-solve (`reserve_enabled=False`, prior session artifact `PC_SW_EBR_OFF_HOURLY_TELEMETRY_DIAGNOSTIC.csv`) reused here, not re-run.
- **DIAGNOSTIC, single resolve:** origin 2's full internal 24-step trajectory (baseline and EBR-relaxed), reconstructed and reused from prior turns.
- Per-hour `J1`/`J_NC` are **not** directly persisted as columns; they are reconstructed here from `unmet_load`/`critical_demand − critical_served_first`, which are mathematically equivalent (zero unmet ⟺ `J1=0` and/or `J_NC=0` for that hour, since both are defined as unmet-load objective terms).

---

## 1–2. Diesel causal taxonomy — population statistics (VERIFIED where stated)

### Fuel-type decomposition (VERIFIED, exact, non-overlapping by construction)

| Component | Formula | Liters | % of 8,729.2446 L |
|---|---|---|---|
| Base (idle) fuel | 547 h × 5.0 L/h | 2,735.0000 | 31.33% |
| Startup fuel | 335 starts × 2.0 L | 670.0000 | 7.68% |
| Marginal fuel | remainder | 5,324.2446 | 61.00% |
| **Total** | | **8,729.2446** | **100%** |

This is a structural (not causal) decomposition — it says nothing yet about *why* diesel ran, only how the governed fuel formula apportions cost once it does.

### Run-length / fragmentation (VERIFIED)

335 diesel runs total (exactly matching the certified start count). Distribution: **170 runs of 1 hour (50.7%)**, 127 of 2 hours (37.9%), 32 of 3 hours, 3 of 4 hours, 3 of 5 hours. Mean run length **1.63 hours**. Heavy fragmentation into short bursts is the dominant pattern, consistent with the "burst-then-discharge" structure already traced in detail at origin 2 (diesel bursts at hours 0-1, 8-9, 20-21, discharge-only in between).

### The "most interesting case" (Phase 8's explicit target): J1=J_NC=0 yet diesel>0

Of the **547** diesel-on hours: **539 (98.5%) have zero unmet load of any kind** (critical or non-critical); only **1/547** has nonzero critical unmet (>0.01 W) and **8/547** have any unmet at all. **VERIFIED.** Combined with the already-established population fact that `j2_shortfall_wh=0` in **100% of all 2,952 resolves** (so `J2=0` always too), this means: **in the overwhelming majority of diesel-on hours, J1=J_NC=J2=0 simultaneously, yet diesel is positive.** By the lexicographic hierarchy, this is only possible if diesel is supported by something below J2 in priority — i.e., **J3's own structure in combination with the Layer-C row (still enforced even at `s_J2=0`), not by J1/J_NC/J2 being actively threatened.** This directly answers the central forensic question: diesel in PC-SW is overwhelmingly **not** driven by imminent critical/non-critical service risk.

### EBR margin at the moment diesel charges the battery (VERIFIED, decisive)

For all **526** diesel+charge hours, `margin = e_next − (ebr_target + min_e_wh)`: **minimum 7,280 Wh, median 86,985 Wh, mean 86,614 Wh, maximum 148,027 Wh.** **Zero of the 526 hours have margin ≤ 4,000 Wh (2% of capacity).** **No diesel+charging event in the entire certified population occurs at a tightly EBR-binding moment.** This is the single most important population-level finding in this report: it rules out "Category B — EBR/reserve banking because the row is about to bind right now" as the proximate local mechanism for essentially all diesel+charging hours. The row is always comfortably satisfied at the moment diesel fires; the banking is for a **future**, not current, binding point (established mechanistically at origin 2: bursts at hours 0-1 fund the battery specifically to survive the discharge-only stretch to the binding hour 7, 5-6 hours later).

### Diesel-only (no simultaneous charging) hours (VERIFIED + DIAGNOSTIC check)

**21/547 (3.8%) hours, 171.48 L (1.97% of total fuel).** A naive physical check (renewable + maximum *physically available* discharge, ignoring what the plan actually chose) found **zero of these 21 hours strictly required diesel in that narrow sense** — in every one, more discharge was physically available than was actually used. This does **not** mean diesel was unnecessary there; it means the planner chose to use diesel + partial discharge rather than full discharge, which is consistent with the *same* reserve-preservation logic (preserving battery energy for a future requirement) extending even into the "diesel-only" population, not only the charge-coincident one. **DERIVED, not independently re-solved per-hour** — the true local-feasibility answer would require a per-hour relaxation re-solve, not performed for all 21.

---

## 3. Central test — "could diesel be lower right now?" (DIAGNOSTIC, single resolve only; not generalized)

Only origin 2's hour-0 resolve was subjected to an exact isolated re-solve with Layer-C/`J2` removed (`reserve_enabled=False`, reused from the prior EBR audit). Result: `J3` drops from 117.408 L to 79.299 L with `J1=J_NC=0` unchanged in both — i.e., **32.5% of that one resolve's fuel was not required to preserve J1/J_NC/J2, only J2's row itself (once removed) permitted the reduction.** This was **not repeated for all 547 hours** — generalizing the exact minimum-diesel-compatible-with-higher-priorities figure population-wide was not performed; the **full-population EBR-off counterfactual (§ below, reused from the prior task) is the closest available substitute at aggregate scale**, and it gives a directly comparable number: **−724.5549 L (−8.30%) in aggregate**, with the crucial caveat that this is a *global* (all-hours-simultaneously) relaxation, not a per-hour "minimum compatible diesel" calculation.

---

## 4. Local vs. global diesel necessity (DERIVED, aggregate proxy — not individually classified per hour)

A true L1–L5 classification per diesel-on hour was not performed (would require, for each of 547 hours, an isolated local relaxation *and* a full downstream closed-loop replay to see whether the local reduction cascades). What the already-completed **full-population EBR-off diagnostic** gives, at the **origin level** (123 origins, reused from the prior task):

| Origin-level outcome | Count | Interpretation |
|---|---|---|
| Globally beneficial to remove reserve (fuel ↓) | 77/123 | Consistent with **L2/L3** dominating for diesel hours in these origins |
| Globally harmful to remove reserve (fuel ↑) | 44/123 | Consistent with **L4** dominating — local reduction cascades into *more* diesel later |
| Tie | 2/123 | — |

**The prior discriminator-search task (same session, immediately preceding this one) found no decision-time feature that separates these two groups** (all tested features `p>0.2`; forecast-error difference between groups `p=0.78–0.92`). This is directly relevant here: **it is not merely that we haven't labeled L1–L5 per hour — it is that, even at the coarser origin level, there is no known way to predict in advance which category a given hour's local reduction would fall into.** This is carried forward as the single largest obstacle to any lever in §13.

---

## 5. Diesel + renewable simultaneously (VERIFIED, reused from the 147-event forensics)

Reusing the already-verified 147-event classification (prior "Diesel-While-Curtailing" forensics, not re-derived here per your instruction not to duplicate Rule-D): of the 147 diesel+curtailment events, **35/147 (23.8%) have renewable alone ≥ demand** (diesel wholly unnecessary for immediate load that hour); **112/147** have renewable below demand (some diesel load-necessity, but typically far exceeded by the diesel actually dispatched — mean "diesel exceeding load-deficit" ≈ 43,198 W, VERIFIED in the prior pass). This confirms, for the curtailing subset, that most diesel there funds charging/banking rather than the immediate deficit.

---

## 6. Diesel + battery charging (VERIFIED — see §2's margin finding; this is the largest mechanism)

**526/547 hours, 8,557.77 L (98.04% of total fuel)** — already established as the dominant population. The margin evidence (§2) shows this is **not** tightly EBR-binding at the moment of charging in any of the 526 cases. Whether charging reaches the 50 kW cap: **DERIVED from the origin-2 trace** (hours 1, 8, 20 saturate the cap; hours 0, 9, 21 do not) — not recomputed for all 526 at this pass; marked **UNKNOWN** at full-population granularity. Whether the stored energy is "subsequently discharged" and "ultimately needed": **UNKNOWN at per-event granularity** (same limitation as the prior EBR task's Phase 8); only the **aggregate** 77/44 origin-level proxy (§4) stands in for this.

---

## 7. Diesel + curtailment (VERIFIED, reused — not re-derived, per your explicit instruction not to duplicate Rule-D)

Reusing the already-closed forensics: of the 147 events, **68/147** are power-cap-limited (diesel exceeds load-deficit *and* charge is pinned at 50 kW), **33/147** are SOC/energy-ceiling-limited (`soc_after≈95%`), **11/147** are charge/discharge-exclusivity-limited (any nonzero discharge that hour forces zero charge, dumping 100% of surplus as curtailment), **35/147** need no diesel at all for load. This population was already fully classified in the prior pass and is not reopened here; it is cited only to confirm it is a **subset** of the larger diesel+charging population (§6), not a separate, additive bucket — see the overlap note in §12.

---

## 8. Objective-hierarchy audit (VERIFIED — this is the key structural finding)

For diesel-on hours where **J1=J_NC=J2=0** (539/547, 98.5%): reducing diesel at that hour, *holding everything else in that hour's own resolve fixed*, would **only ever risk increasing J2 and/or J4** (reserve shortfall or curtailment) — **never J1 or J_NC directly**, since those are driven by critical/non-critical demand satisfaction, not diesel/charge magnitude, and are already at their floor (0) independent of exactly how much diesel ran. **This is the central structural fact of the whole investigation: PC-SW's diesel is overwhelmingly a J2-protective (reserve) and J3-cost (fuel-minimizing-subject-to-J2) decision, not a J1/J_NC-protective one, in the vast majority of hours it runs.** (`VERIFIED` for the J1/J_NC=0 fact; `DERIVED` for the "only J2/J4 at risk" inference, which follows from the model structure traced in §1/§2 of the earlier EBR-formulation audit, not from a fresh per-hour re-solve of all 539 hours.)

---

## 9. Terminal-target separation (VERIFIED, reused from the prior EBR population audit — not re-derived)

Rolling EBR is enforced at every one of the 2,952 real-hour resolves; the fixed terminal floor only ever enters the *last* slot of whichever 24-hour plan is currently being solved, and because of the rolling re-plan cadence, the calendar-day's actual hour 23 is reached as "hour 0" of many intervening re-plans before the specific terminal slot it was computed for is ever realized. This was established in the prior EBR population forensics and is not reopened here. No diesel-on hour in this decomposition is attributed to the terminal target as a *separate* bucket from rolling EBR (see §12 overlap note).

---

## 10. Battery "usable energy" test (DERIVED from §2/§6, not independently re-verified per hour)

The exact constraint preventing substitution of diesel by discharge, where the battery has energy above its floor, is **not SOC alone** — it is the Layer-C reserve row (`e_next[t]+s_J2[t] ≥ target[t]+min_e_wh`), which treats "energy above the SOC floor" and "energy above the *reserve* floor" as two different quantities. Discharging below the reserve-adjusted floor would raise `s_J2[t]` above 0, which the hierarchy forbids once `J2` is pinned at its optimum (0, in practice, population-wide). So: **the battery "has usable energy" in the SOC sense, but much of it is not "usable" in the governed sense, because using it would violate the (already-optimal) reserve requirement, not the SOC floor itself.** This is consistent with, and explains, why discharge in the §2/§6 diesel-only population was observed below its physical maximum even when more was available.

---

## 11. Fuel/startup semantics and fragmentation causality (DERIVED)

Given the run-length distribution (§2: 50.7% single-hour runs) and the margin finding (§2: diesel+charge never tightly EBR-binding), fragmentation is most consistent with category **B (induced by reserve/battery banking)** — short bursts fire exactly long enough to rebuild the battery ahead of a future binding point (as traced exactly at origin 2: 2-hour bursts at 0-1, 8-9, 20-21), not with category A (forced by a higher-priority constraint at that specific hour — ruled out by the J1=J_NC=J2=0 finding) nor cleanly with category E (pure solver degeneracy — the governance audit two tasks prior established genuine degeneracy *within* a burst's internal split, but not in *whether* a burst happens at all). **This was not independently verified for every one of the 335 runs — DERIVED from the structural/margin evidence and the one fully-traced representative case.**

---

## 12. Fuel accounting — causal buckets (hierarchical attribution; overlaps explicitly flagged, per your instruction that an exact mutually-exclusive partition may be impossible)

| Bucket | Liters | % of total | Hours | Basis | Overlap note |
|---|---|---|---|---|---|
| **Diesel+charging (reserve/banking-adjacent)** | 8,557.77 | 98.04% | 526 | VERIFIED | **Superset** containing the next two rows |
| — of which: diesel+curtailment (subset) | 2,619.3851 | 30.01% | 147 | VERIFIED (reused) | Subset of the row above |
| — of which: EBR-attributable (DIAGNOSTIC global estimate) | 724.5549 | 8.30% | n/a (aggregate, not hour-mapped) | DIAGNOSTIC (full population EBR-off) | Estimated at the *aggregate fuel* level, not hour-by-hour; overlaps with both rows above |
| Diesel-only, no charging | 171.48 | 1.97% | 21 | VERIFIED | Disjoint from the charging bucket |
| **By fuel-formula type (orthogonal decomposition, sums exactly)** | | | | | |
| — Base (idle) fuel | 2,735.00 | 31.33% | 547 | VERIFIED | Orthogonal axis — not causal, structural |
| — Startup fuel | 670.00 | 7.68% | 335 starts | VERIFIED | Orthogonal axis |
| — Marginal fuel | 5,324.2446 | 61.00% | — | VERIFIED | Orthogonal axis |
| Terminal-driven (separate from rolling EBR) | UNKNOWN | — | — | Not isolated as a separate bucket; believed near-zero/overlapping with EBR per §9 | — |
| Fuel-inventory-feasibility-driven | UNKNOWN | — | — | Not isolated; Amendment A2 row only binds hour 0 of each resolve and was not found to be the proximate driver in the one traced case (origin 2) | — |
| Solver-degeneracy-driven (within-burst split only) | not separately quantifiable in liters | — | — | Governance-audited two tasks prior: real but does not change total fuel by definition (tie among equal-cost allocations) | Zero net liters by construction |
| Indeterminate | remainder | — | — | The gap between "98.5% of diesel-on hours have J1=J_NC=J2=0" and a fully-traced per-hour local/global necessity split | UNKNOWN |

**Ranking by liters:** diesel+charging (8,557.77 L) ≫ EBR-attributable aggregate (724.55 L) ≈ diesel+curtailment subset (2,619.39 L, itself inside the charging bucket) > diesel-only (171.48 L).

**The largest remaining mechanism, after excluding the already-closed Rule-D (diesel+curtailment, 147h) and the already-closed EBR population/discriminator work (724.55 L aggregate), is the residual ~7,200+ L of diesel+charging fuel that is neither in the 147-event curtailment population nor cleanly attributable to the single global EBR-off aggregate figure** — i.e., the broader "diesel banks the battery well ahead of a future binding point, with large local margin, in a pattern (§2, §8, §11) that is structurally forced by the J2-above-J3 priority but whose *specific timing and magnitude at any given hour* has no demonstrated local-necessity proof and no demonstrated decision-time discriminator (per the immediately preceding task).**

---

## 13. Legitimate lever search

No candidate survives the required bar. The decisive obstacle, established in the immediately preceding task and reconfirmed structurally here, is that **the mechanism's local appearance (large margin, J1=J_NC=J2=0, short bursts) is indistinguishable, at decision time, between the 77-origin population where removing it is globally beneficial and the 44-origin population where removing it is globally harmful.** Any lever that acts on "diesel+charging with large EBR margin" (the one robust, population-wide pattern found) would necessarily act on *all* 526 such hours, including the 44-origin subset where doing so provably costs more fuel overall (§4) — this is not a hypothetical risk, it is the directly measured outcome of the one global intervention (EBR-off) actually tested.

---

## 14. Anti-hindsight audit

| Mechanism/feature | Source | Available at decision time? | Uses realized future? | Uses future SOC/fuel/curtailment? | Uses EBR-off trajectory? | Post-treatment? | Valid online? |
|---|---|---|---|---|---|---|---|
| EBR margin at charging hour | persisted telemetry (realized `soc_after`, fresh `ebr_target`) | Partially — the *target* is decision-time; the realized `soc_after` reflects that hour's own execution, available only *after* acting | No | No | No | **Yes — the margin reported here is measured post-execution**, not the planner's ex-ante decision variable | **No — disqualified as an online feature as reported; the planner's own ex-ante `e_next` plan satisfies the row by construction, so this margin is descriptive/retrospective, not a new online signal** |
| 77/44 origin split | EBR-off diagnostic | No | N/A (origin-level outcome) | N/A | **Yes** | Yes | **No — explicitly a retrospective label, never proposed as an online feature** |
| Run-length / fragmentation pattern | certified telemetry | Pattern is observable only after a run completes | No | No | No | Yes | **No — descriptive only** |
| J1=J_NC=J2=0 while diesel>0 | certified telemetry | Realized, not ex-ante | No | No | No | Yes | **No — descriptive, confirms a structural fact, not a usable trigger** |

**No feature in this report is proposed as, or qualifies as, a valid online lever.** This table exists to document why each one fails, consistent with the preceding task's discriminator-search conclusion.

---

## 15. Governance classification

**D — Mechanism is real but no safe online lever exists.**

The dominant mechanism (diesel+battery-charging, 98.04% of fuel, systematically non-EBR-tight at the moment it occurs, structurally explained by the J2-above-J3 priority forcing forward reserve-building) is now confirmed at full population scale, not merely a single-resolve finding. It is the same mechanism already shown (prior task) to be a genuine population-wide **mixture** (77 origins net-beneficial to relax, 44 net-harmful) with no decision-time discriminator found despite a systematic, causally-screened search across 13+ candidate features. This report adds population-scale confirmation of the *local* signature of that mechanism (never tightly EBR-binding, 98.5% zero-unmet-coincident) without finding any new separating information. Classification stands at **D**, consistent with and reinforcing the immediately preceding task's conclusion.

---

## 17. Required final answers

1. **Of 547 diesel-on hours, how many are physically unavoidable at the current resolve?** Not independently re-solved per hour; the population-wide proxy (J1=J_NC=J2=0 in 539/547, margin never tight in 526/526 charging hours) strongly suggests the number of hours with *strict, immediate, no-alternative* necessity is small — plausibly a minority of the 21 diesel-only hours at most — but an exact count requires per-hour re-solves not performed here. **DERIVED, bounded, not exact.**
2. **How many are primarily reserve/banking driven?** 526/547 (96.2%) co-occur with charging and show zero tight-margin cases — the population most consistent with reserve/banking as the proximate local driver. **VERIFIED (co-occurrence) + DERIVED (causal label).**
3. **How many are caused by objective hierarchy rather than physical necessity?** Consistent with the 539/547 (98.5%) J1=J_NC=J2=0 population — diesel there is only supportable by J3/J2-structural reasons, not immediate physical threat to J1/J_NC. **VERIFIED underlying fact, DERIVED interpretation.**
4. **How many involve diesel charging despite renewable availability?** 526/547; a finer "renewable was available but diesel charged anyway" breakdown matches the already-reported 68+33+11 = 112/147 non-trivial-renewable subset of the curtailment population (prior task), not independently recomputed for the full 526 here. **VERIFIED (the 147-event subset), UNKNOWN (full 526 at this granularity).**
5. **How much fuel per mechanism?** See §12 table — 8,557.77 L charging-adjacent (98.04%), 2,619.3851 L curtailment subset (30.01%, nested), 724.5549 L EBR-attributable aggregate (8.30%, nested/overlapping), 171.48 L diesel-only (1.97%).
6. **What exact constraint prevents replacing diesel with discharge when the battery has usable (above-SOC-floor) energy?** The **Layer-C reserve row**, not the SOC floor — discharging further would raise `s_J2` above its pinned optimum of 0 (§10). **VERIFIED structurally.**
7. **How much diesel is genuinely required to preserve higher-priority objectives?** Only the portion needed to keep `J1=J_NC=0` (negligible — only 1/547 hours show any critical-unmet risk even under full realized conditions) plus whatever is needed to keep `J2=0` — which, per the preceding task's full-population EBR-off diagnostic, is **724.5549 L in aggregate (8.30%)**, unevenly distributed (net cost in 44/123 origins, net benefit in 77/123). **DIAGNOSTIC, reused.**
8. **Largest remaining mechanism after excluding Rule-D and EBR-discriminator work?** The residual diesel+charging fuel outside the 147-event curtailment population and not captured by the single global EBR-off aggregate — i.e., the general forward-banking pattern itself (§12), for which no finer non-arbitrary decomposition or lever was found.
9. **Is there a non-arbitrary online lever for that mechanism?** **No** (§13).
10. N/A.
11. **Next-largest mechanism worth investigating:** a trajectory-shape (multi-hour-ahead, not static hour-0 scalar) decision-time signal — explicitly flagged as untested in the immediately preceding task's §8 ("What remains UNKNOWN") and not addressed in this pass either.

"NO POLICY EXPERIMENT WAS EXECUTED."
