# MILP v2 — Research-Only Design Specification (Rev. 3)

**Status**: Design document only. **No code, config, or model is modified or implemented.
No MILP is run.** GAP19 (`gap19_highs_native.py`) remains frozen, unmodified, as the
control. This revision fixes the two `BLOCKING` findings from
`MILP_V2_REV2_DESIGN_AUDIT.md` and addresses (not necessarily resolves favorably) the two
`NEEDS CLARIFICATION` items. Nothing below invents a policy decision, a numerical value, or
an objective stage beyond what existing evidence supports.

---

## 1. Load-tier formulation (Fix 1: demand-side accounting)

### Essential-demand clipping (new, required for feasibility)

**Why needed**: `essential_demand[t] = secondary_heating.max_power_w` (flat, 5,000 W) and
`critical_demand[t] = min(11,600 W, demand[t])` are computed independently. If both were
subtracted from `demand[t]` without adjustment, `p_unmet` could be forced negative at hours
where `demand[t]` is small — infeasible. **Fix** (mirrors the existing clipping pattern
already used for `critical_demand`, not a new convention):

```
essential_demand[t] = min(5,000 W, max(0, demand[t] − critical_demand[t]))
```

This guarantees `critical_demand[t] + essential_demand[t] ≤ demand[t]` at every hour.

### Demand-side balance — corrected (Blocker #1 from Rev. 2 audit)

**Audit finding**: constraint #4 (`p_served + p_unmet = demand`) was never amended in
Rev. 2 to also account for `p_served_essential`, causing `unmet_load` to double-count
Essential-tier-served energy as unmet.

**Fix**: constraint #4 is amended to a three-way split:
```
p_served[t] + p_served_essential[t] + p_unmet[t] = demand[t]
```
Combined with Layer B (`p_served + P_unmet_crit = critical_demand`, **unchanged**) and the
new Essential-tier balance (`p_served_essential + P_unmet_essential = essential_demand`,
**unchanged from Rev. 2**), `p_unmet` now correctly reflects only the genuinely-unserved
remainder: `p_unmet[t] = demand[t] − p_served[t] − p_served_essential[t]`, which is
guaranteed non-negative by the clipping above. Energy actually delivered to the Essential
tier is no longer double-counted as unmet.

### Bus-bar (generation-side) balance

**Unchanged from Rev. 2** (already correct per the prior audit):
```
p_sol_used[t] + p_wind_used[t] + p_dis[t] + p_diesel[t]
    = p_served[t] + p_served_essential[t] + p_chg[t] + p_flex[t]
```

### Tier source and mapping (addressing NEEDS CLARIFICATION item 1)

**Unchanged data source**: `curtailable_loads` (`secondary_heating`), not `deferrable_loads`
— rationale unchanged from Rev. 2.

**Tier 2 vs. Tier 3 assignment — now explicitly marked a judgment call, not a confirmed
mapping**: no document in this repository states which tier `curtailable_loads` belongs to.
Rev. 2 assigned it to Tier 2 (Essential/Flexible) with more confidence than the evidence
supports. **This revision states plainly: assignment to Tier 2 rather than Tier 3
(Interruptible/Noncritical) is a `SIMULATED_RESEARCH_ASSUMPTION`, not a derived fact.** A
load with only a modest per-Wh cost and no other protection could equally plausibly belong
to Tier 3. **Both readings remain open**; this specification proceeds with the Tier 2
assignment for concreteness, but this is a labeled choice, not a settled question, and a
future revision or real governance input could reassign it without changing any other part
of this design.

### Flexible / Interruptible-Noncritical (Tier 3)

**Unchanged from Rev. 1/2**: fully uncosted, unconditionally unmet.

## 2. Critical-load hard constraint and infeasibility handling (Fix 2 downgraded to
UNRESOLVED — new evidence found)

### Hard constraint mechanism

**Unchanged.** `p_served ≤ critical_demand`, `P_unmet_crit` at `J1`. Unaffected by §1's
corrected accounting.

### Infeasibility → OptionD routing — **reusing the router's `NORMAL`-route
`EmergencyAssessment` is now confirmed semantically INVALID, not merely unverified**

**New finding, from direct inspection of `system/control/ecd.py`** (not examined at the
Rev. 2 audit stage): `EmergencyAssessment.preserved_resource` is computed as follows
(`ecd.py:291-313`):
```python
if mode == OperatingMode.NORMAL:
    if is_tie:
        preserved = ResourceSelection.BOTH
    else:
        preserved = ResourceSelection.NONE
else:  # EMERGENCY
    ... preserved = ResourceSelection.BATTERY  # or DIESEL, based on margins
```
**By construction, any assessment produced under `mode == NORMAL` has
`preserved_resource ∈ {NONE, BOTH}` — it can never be `BATTERY` or `DIESEL`.**
`OptionDFallbackSolver.solve()` (`option_d.py:122,135`) branches **only** on
`assessment.preserved_resource == ResourceSelection.BATTERY` or `== ResourceSelection.DIESEL`
— neither branch would ever trigger for a reused `NORMAL`-route assessment. **This
confirms, rather than merely leaves open, that Rev. 1/2's proposed reuse mechanism does not
do anything meaningful when invoked**: OptionD would fall through both conditionals,
producing undefined/unspecified behavior for this case (not examined further here).

**Per instruction not to invent a workaround where none is defensible**: this item is
**downgraded from "proposed mechanism" to explicitly UNRESOLVED.** No existing evidence
supports a valid way to obtain a genuinely `EMERGENCY`-conditioned `EmergencyAssessment` for
a cycle the router already classified `NORMAL` — doing so would require re-running the ECD
assessment under different (currently unspecified) assumptions, which is itself a new
mechanism this specification does not invent. **The infeasibility → OptionD routing
proposal from Rev. 1/2 is withdrawn**; GAP19's own existing infeasibility fallback (a
degenerate zero-dispatch `DispatchPlan`, already in current code) remains the only
evidence-grounded behavior for this case until a real design for this gap is produced.

## 3. Emergency Mode entry/mapping using the simulated 6h assumption

**Unchanged from Rev. 1/2.**

## 4. Terminal reserve

**Unchanged from Rev. 1/2, in full** — unit, formula, mechanical entry, and priority all
preserved exactly.

## 5. Diesel

**Unchanged from Rev. 2** (minimum output, fuel coefficients, minimum-up-time enforcement
and its `t=0` boundary convention using `diesel_hours_running`).

## 6. Battery

**Unchanged from Rev. 1/2, in full.**

## 7. Objective / lexicographic priority order (Fix 2: Essential-tier indifference)

### The indifference problem (Blocker #2 from Rev. 2 audit)

**Audit finding**: with `P_unmet_essential` entirely uncosted, the solver has no preference
between serving Essential load with otherwise-curtailed surplus and simply routing that
same surplus into extra battery charging — both are equally zero-cost, so the tier's
intended behavior was not guaranteed to occur.

### Fix: reuse the existing `J4` coefficient exactly — no new stage, no new number

**Mechanism**: add `P_unmet_essential[t]` into the existing `c4` (`J4`, curtailment)
objective vector, at the **identical existing coefficient already used for curtailment**
(`1.0` per Wh — `gap19_highs_native.py:342-343`), rather than any newly-chosen value:
```
c4[idx_unmet_essential_start + t] = 1.0 · dt    # identical to the existing curtailment coefficient
```
**Why this is not an invented number**: GAP19's existing `1.0` curtailment coefficient is
not a tuned economic value — it is the natural "count Wh directly" scaling already used
throughout `J4` (which is denominated in raw Wh, not currency). Applying the same
direct-count convention to `P_unmet_essential` (also denominated in Wh) introduces no new
coefficient; it reuses the one that already exists for the same unit.

**Does this break the indifference?** Yes: minimizing `J4 = Σ(curtailment) +
Σ(P_unmet_essential)` gives the solver a real incentive to set `p_served_essential` as high
as feasible whenever doing so is free in every higher-priority tier (`J1`–`J3`), since doing
so reduces `P_unmet_essential` (lowering `J4`) at no cost elsewhere — whereas routing the
same surplus into extra battery charging reduces neither `P_unmet_essential` nor
curtailment-adjacent cost beyond what charging already achieves. The two destinations are no
longer objective-indistinguishable.

**Stage count**: **unchanged** — still D15's four stages; no 5th stage introduced; no
weighting between `J1`–`J4` altered. This is an addition to an existing vector's contents,
not a new priority level.

**Disclosed, inherited (not new) tension**: GAP19's existing `J4` curtailment coefficient
(`1.0`, nonzero) already sits in some tension with D10's "necessary curtailment... allowed
*without* explicit objective penalty" language — this tension is **pre-existing in the
frozen control**, not introduced by this revision. Folding `P_unmet_essential` into the same
vector inherits this existing, uncorrected tension rather than creating a new one; it is
flagged here for completeness, not as a new defect.

---

## What Rev. 3 fixes, relative to Rev. 2

- Demand-side accounting (constraint #4) now correctly excludes Essential-tier-served
  energy from `unmet_load` — no more double-counting.
- Essential-tier indifference resolved by reusing the existing, identical `J4` coefficient
  — no new stage, no new number.
- Essential-demand clipping added (necessary for feasibility, mirrors the existing
  `critical_demand` clipping pattern — not a new convention).

## What Rev. 3 explicitly downgrades (new evidence, not oversight)

- **Infeasibility → OptionD routing**: the Rev. 1/2 proposal to reuse the router's
  `NORMAL`-route `EmergencyAssessment` is now **confirmed invalid** (not merely unverified)
  by direct code inspection of `ecd.py`'s `preserved_resource` logic. This item is
  **withdrawn and marked UNRESOLVED** rather than replaced with an invented alternative.

## Tier 2 vs. Tier 3 mapping

Explicitly marked a labeled judgment call (`SIMULATED_RESEARCH_ASSUMPTION`), not a derived
fact — both tier assignments remain defensible; this spec proceeds with Tier 2 for
concreteness only.

---

## STOP

Revised design specification only. No code was written, no config changed, no model
modified, no experiment run. GAP19 remains the frozen, unmodified control.
