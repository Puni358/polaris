# Formulation Audit: `p_served` / `p_unmet` / `p_unmet_crit` Interaction

**Scope**: Audit only, of GAP19's existing source code, `loads.yaml`, and the governance
documents already in this repository. **No code, config, or model was changed. No
experiment was rerun.** This extends the finding first surfaced in
`DIESEL_CHARGING_NECESSITY_FORENSIC_REPORT.md` §1a.

---

## 1. Exact trace of definitions and usage (confirmed code facts)

### Variable definitions
- `p_served` (variable index `base+8`): bounded `[0, demand[t]]`
  (`gap19_highs_native.py:187-188`).
- `p_unmet` (`base+9`, reported as `DispatchPlan.unmet_load`): bounded `[0, demand[t]]`
  (`gap19_highs_native.py:188`).
- `P_unmet_crit[t]` (`idx_unmet_crit_start+t`, reported as part of `j1_objective`): bounded
  `[0, critical_demand[t]]` (`gap19_highs_native.py:198-199`).

### Constraints (both equalities, both involving `p_served`)
- **#4, "Total Demand Deficit Balance"** (`gap19_highs_native.py:233-236`):
  `p_served[t] + p_unmet[t] = demand[t]`.
- **Layer B, "Critical Demand Balance"** (`gap19_highs_native.py:288-295`):
  `p_served[t] + P_unmet_crit[t] = critical_demand[t]`.

### Algebraic consequence (confirmed, not interpretation)
Both equalities share the identical `p_served[t]` variable. Since `P_unmet_crit[t] ≥ 0`,
Layer B forces `p_served[t] ≤ critical_demand[t]` for every `t`, unconditionally — this
bound does not depend on available generation, battery state, or diesel capacity.
Substituting into constraint #4: `p_unmet[t] = demand[t] − p_served[t] ≥ demand[t] −
critical_demand[t]`, which is strictly positive whenever `demand[t] > critical_demand[t]`
(true at essentially every hour, since `critical_demand[t] = min(11,600 W, demand[t])` per
`run_research_simulation.py`/`run_full_experiment.py`'s construction of
`config["critical_demand_w"]`). **`p_served` cannot exceed `critical_demand` no matter how
much solar, wind, battery, or diesel capacity is available — it is not a decision the
solver is free to make differently.**

### Objective penalties (confirmed code facts)
- `P_unmet_crit[t]` is costed: `c1[idx_unmet_crit_start+t] = 1.0 · dt`
  (`gap19_highs_native.py:331`) — priority 4 (highest), i.e. `J1`.
- `p_unmet[t]` (`unmet_load`) is **never referenced in `c1`, `c2`, `c3`, or `c4`
  anywhere in the file** — confirmed by reading the full objective-construction block
  (`gap19_highs_native.py:322-343`). It carries **zero cost at every priority tier.**

### Comparison with the prior (older) optimizer, `milp.py` — confirms this is a deliberate
redesign, not an accidental omission of a cost term

`system/optimization/implementations/milp.py` (the earlier "Phase D2" optimizer, still
present in the repo) has **no critical/non-critical split at all** — only
`p_served + p_unmet = demand` (`milp.py:188`), with `p_unmet` costed directly:
`c[base+9] = unmet_penalty_per_wh · dt` (`milp.py:116`), reading
`unmet_penalty_per_wh = 10.0` ($10,000/kWh) from `loads.yaml: critical_load.unmet_penalty_per_wh`.
**GAP19 is a later formulation that introduces the critical/non-critical split and, in doing
so, removes the economic penalty on `p_unmet` entirely** — it does not merely forget to port
the penalty over; it replaces the *entire mechanism* (soft economic penalty on all unmet
load) with a *different mechanism* (hard priority-4 treatment of critical-only unmet load,
zero treatment of the rest). `loads.yaml`'s `unmet_penalty_per_wh: 10.0` value still exists
in config (read only by the older, still-present `milp.py`) but is **never read by GAP19**.

## 2. Governed policy semantics (from `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`) — policy
interpretation, clearly separated from the code facts above

- **D01/D02** (`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md:166-177`): a **three**-tier load
  structure is `HUMAN_SELECTED_POLICY` — Critical (protected), Essential/Flexible (managed
  shedding), Interruptible/Noncritical (shed first). The *exact* shedding/restoration logic
  for tiers 2–3 is explicitly `NEXT_EMS_OBJECTIVE_SPECIFICATION` — **not yet specified** by
  any governance document.
- **D03/D04/D05** (`...:227-246`): Critical load must receive 100% service / 0 kWh unmet in
  normal operation, and — explicitly — **"must be implemented as a hard constraint... not as
  a soft economic penalty."** The same document explicitly flags the *older* `milp.py`'s
  $10,000/kWh soft penalty as a `CURRENT_IMPLEMENTATION_FACT` that is **"explicitly NOT the
  policy SLA."**
- **loads.yaml** currently models only `critical_load` (single value) plus separate
  `deferrable_loads` / `curtailable_loads` lists intended for a middle tier — **but GAP19's
  code never reads `deferrable_loads` or `curtailable_loads` at all** (confirmed: no
  reference to either key anywhere in `gap19_highs_native.py`).

**Policy interpretation (not a direct code fact)**: GAP19's hard treatment of critical load
(capped `p_served`, zero-cost-but-highest-priority `P_unmet_crit`) is **well-aligned** with
D03/D04/D05's explicit instruction to use a hard constraint rather than a soft penalty — in
this respect GAP19 is a *closer* match to governed policy than the older `milp.py` was.
However, the governed three-tier structure (D01/D02) calls for *managed* shedding of the
middle (Essential/Flexible) tier — not the same as GAP19's actual behavior, which collapses
everything beyond critical load into a single, permanently, unconditionally, costlessly
unserved category with no tier distinction and no "managed" logic of any kind.

## 3. Quantified consequences

### Unmet-demand metrics
**Confirmed, from R1/R2's own stored results**: `planned_unmet_load_wh` is **identical
between the baseline and Stage 8.1 arms at every one of the 347 origins**
(29,661,600.0 Wh total, both arms — already reported in `RESEARCH_SIMULATION_RESULTS_R1_FULL_WINDOW.md`
and `R2_SOLAR_ABLATION_RESULTS.md`). The formulation trace in §1 explains **why**, precisely:
`unmet_load[t] = demand[t] − p_served[t]`, and since `p_served[t]` is capped at
`critical_demand[t]` (a function of `demand[t]` alone, never of solar/wind), **`unmet_load`
is structurally incapable of varying with the solar forecast at all.** This is a stronger,
more precise statement than the earlier reports' observation that the metric "happened to be
identical because demand is shared" — it could not have differed under *any* solar forecast
difference, given this formulation.

### Reliability
`j1_objective` (critical deficit) was `0.0` for both arms in every `OPTIMAL` NORMAL-route
cycle in R1/R2 (confirmed, already reported). Given `p_unmet` carries zero cost, the
"reliability" this model can report is limited to **critical-load service only** — it says
nothing about total-demand service, because total-demand service was never an optimization
objective to begin with.

### Diesel dispatch
Already established in `DIESEL_CHARGING_NECESSITY_FORENSIC_REPORT.md` §1a: diesel dispatch
decisions have no mechanism by which serving non-critical demand could influence them
(`p_served`'s cap means generating more to serve non-critical load is not even a feasible
choice, let alone a cost-driven one). All diesel dispatch in R1/R2 is attributable to
critical demand + reserve envelope + fuel/curtailment minimization only.

### Battery dispatch
Same conclusion as diesel: battery charge/discharge decisions cannot be driven by a desire
to serve more non-critical demand, because doing so is not a variable the solver has access
to (there is no feasible dispatch that serves more than `critical_demand[t]`, regardless of
battery state).

### Objective value
**Confirmed**: because `p_unmet` has zero coefficient in `c1`–`c4`, its value is **never
part of what the solver optimizes** — two solutions with identical `J1`–`J4` but different
`p_unmet`/`unmet_load` values would be treated as equally optimal by this objective (though
in practice `p_unmet` is pinned by the equality constraints once `p_served` is fixed, so it
has no independent degree of freedom at all). **This formulation issue has zero effect on
which dispatch the solver selects — it only affects what the reported `unmet_load` metric
means.**

### R1/R2 baseline vs. Stage 8.1 comparison
Every prior report's "unmet demand" row (`R1`, `R2`, `R2 ablation`, and the counterfactual
isolation) is **not a measurement of comparative reliability or demand service between the
two forecast engines** — it is a fixed arithmetic function of `demand − critical_demand`,
identical by construction regardless of which forecast engine, or even which optimizer input
scenario, is used. This does not invalidate those reports' other metrics (diesel,
curtailment, SOC, J1–J4), which remain as reported; it specifically narrows what the
"unmet demand" row in each of them can be read to mean.

## 4. Classification: A, B, C, or D?

This audit finds **two distinct issues that classify differently**:

### 4a. The critical-load hard-priority treatment itself: **(A) intentional governed policy**
GAP19's capping of `p_served` at `critical_demand`, with zero-cost-but-top-priority
`P_unmet_crit`, is a deliberate redesign relative to the older `milp.py` (confirmed by the
direct comparison in §1) and is well-supported by the explicit D03/D04/D05 instruction to
use a hard constraint, not a soft penalty, for critical load. This part is **(A)**.

### 4b. The complete absence of any treatment (cost, tier, or "managed shedding") for
non-critical demand: **(C) unresolved governance ambiguity — but see caveat below**
The governed three-tier structure (D01/D02) calls for managed shedding of an
Essential/Flexible middle tier, which GAP19 does not implement at all (it also does not read
`deferrable_loads`/`curtailable_loads`, which exist in config as if intended for this
purpose). However, the *exact* mechanics of that managed shedding are explicitly marked
`NEXT_EMS_OBJECTIVE_SPECIFICATION` in governance — i.e., **not yet specified by any governed
decision**. GAP19 implementing nothing for this tier is therefore not a deviation from an
existing specification; it is the absence of one. This is most accurately classified as
**(C)**: the ambiguity is real (there is no governed answer to "what should happen to
Essential/Flexible load"), but it is better described as *pending* rather than
*contradicted* policy.

### 4c. The specific interaction/redundancy between constraint #4 and Layer B, and the
resulting non-informative `unmet_load` output metric: **(D) insufficient evidence to
classify as intentional or a bug**
No governance document or code comment addresses whether `unmet_load` was *meant* to remain
in the schema as a now-largely-decorative, non-optimized value once the critical-demand
split was introduced, or whether constraint #4 is a leftover from the pre-split formulation
that was never reconciled with Layer B. Both are plausible; neither is confirmable from
existing evidence without asking whoever authored this specific change. This narrow point is
**(D)**.

## 5. Summary table

| Aspect | Confirmed code fact | Policy interpretation | Classification |
|---|---|---|---|
| `p_served ≤ critical_demand` always | Yes (§1, algebraic) | — | — |
| `p_unmet` ("unmet_load") uncosted | Yes (§1) | — | — |
| Hard-priority treatment of critical load | Yes (design, vs. `milp.py`) | Matches D03/D04/D05's "hard constraint not soft penalty" instruction | **(A)** |
| No tier/managed-shedding treatment of non-critical load | Yes (no `deferrable_loads`/`curtailable_loads` read) | D01/D02 call for a 3-tier structure whose mechanics are not yet governed-specified | **(C)** |
| Whether `unmet_load`'s resulting non-informativeness was intended | — | No document addresses it | **(D)** |

## STOP

Formulation/forensic audit complete. No code, config, or model was changed; no optimizer
redesign was proposed or implemented; no experiment was rerun.
