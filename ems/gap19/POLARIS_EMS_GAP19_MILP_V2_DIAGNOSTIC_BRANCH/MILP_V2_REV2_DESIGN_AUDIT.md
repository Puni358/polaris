# Design Audit: Rev. 2 vs. the Original Blockers

**Scope**: Audit only, of `MILP_V2_RESEARCH_SPECIFICATION_REV2.md` against
`MILP_V2_DESIGN_AUDIT.md`. **No code, config, or model changed; nothing implemented or
run.** GAP19 remains frozen as the control. This audit does not fix anything — it only
classifies.

---

## 1. Does Essential load actually flow through the energy balance correctly?

**Partially — a new BLOCKING gap found.** The bus-bar (generation-side) amendment is
correct: `p_served_essential` is now a real sink in the generation-balance equation.
**However, Rev. 2 never amends constraint #4** (`p_served + p_unmet = demand`, the
demand-side accounting equation) **to also subtract `p_served_essential`.** Since `p_served`
remains capped at `critical_demand` (Layer B, unchanged), `p_unmet` (`unmet_load`) is still
computed as `demand − p_served`, which is numerically unaffected by whether
`p_served_essential` is zero or at its maximum. **Consequence**: energy that is actually
being delivered to the Essential tier would still be counted as "unmet" in the reported
`unmet_load` metric — an internal double-counting/accounting inconsistency, not merely an
uninformative metric (which was the original, milder finding). This is worse than the
problem Rev. 2 was trying to fix for this specific output.
**Classification: BLOCKING.**

## 2. Is the `curtailable_loads` → Essential-tier mapping actually supported?

**Partially — reasonable, but not as firmly supported as Rev. 2 states.**
`curtailable_loads`' schema (a load with a per-Wh cost for not being served) is a better
structural fit than `deferrable_loads` for "may go unserved, at a cost" — that part of
Rev. 2's reasoning holds. But **nothing in `loads.yaml` or any governance document states
which tier `curtailable_loads` belongs to.** Rev. 2 assigns it to Tier 2
(Essential/Flexible); it could equally plausibly belong to Tier 3
(Interruptible/Noncritical, "shed first") — a load with only a modest $0.10/Wh penalty and
no other protection could just as easily be the *lowest*-priority tier, not the *middle*
one. This is a reasonable research choice, not a confirmed mapping.
**Classification: NEEDS CLARIFICATION** (not blocking — a defensible choice, but presented
with more certainty than the evidence supports).

## 3. Does an uncosted `P_unmet_essential` make the tier functionally meaningless?

**Yes, substantially — a new issue, more severe than Rev. 2 acknowledged.** Rev. 2 states
the variable "currently has no effect on the objective" but frames this as a disclosed
limitation. Tracing the mechanics further: because `p_served_essential`, `p_chg`, and
`p_flex` are **all equally zero-cost destinations** for any surplus solar/wind that would
otherwise be curtailed (reducing `p_curt_sol`/`p_curt_wind` identically regardless of which
of the three absorbs it), **the solver has no preference for serving Essential load over
simply charging the battery further** with the same surplus. There is a feasible pathway
for Essential load to be served "for free," but nothing makes it *happen* over the
equally-valid alternative of routing that energy into extra charging — the two are
objective-indistinguishable. This defeats the stated purpose of adding the tier at all
("give Tier 2 at least minimal accounting instead of none" — Rev. 2 gives it a variable, but
not differentiated behavior).
**Classification: BLOCKING** (undermines the feature's own stated purpose, not merely a
loose end).

## 4. Is the flat `essential_demand[t] = max_power_w` assumption internally valid and bounded?

**Yes.** `curtailable_loads.max_power_w` (5,000 W) is a fixed scalar with no time-of-day
field in its schema, so a flat 24h profile is the only conversion that adds no invented
data. Bounds (`[0, 5,000 W]` per hour) are well-defined and small relative to other
generation/load magnitudes in the model — no infeasibility or pathological-scale risk
identified.
**Classification: ACCEPTABLE RESEARCH ASSUMPTION** (clearly labeled simplification, as
Rev. 2 itself states).

## 5. Is reusing the router's `EmergencyAssessment` actually supported by the control flow?

**Mechanically plausible; semantically unverified.** Direct inspection of
`option_d.py` confirms `OptionDFallbackSolver.solve()` reads exactly one field off the
`assessment` object: `assessment.preserved_resource` (a `ResourceSelection` enum,
`BATTERY`/`DIESEL`). This field is computed by the router's ECD logic on *every* call,
independent of which route is ultimately selected — so mechanically, reusing it is sound
(the field exists and is populated regardless of `NORMAL`/`EMERGENCY`). **What remains
unverified**: whether a `preserved_resource` value computed under conditions the router
judged `NORMAL` remains a *sensible* recommendation once that same cycle's optimizer later
turns out infeasible — i.e., whether the ECD risk calculation that produced
`preserved_resource` implicitly assumed the `NORMAL` conditions held. This was not
checked (and would require deeper review of the router's ECD assessment logic, out of
scope for this audit).
**Classification: NEEDS CLARIFICATION** (downgraded from the audit's open question —
mechanical reuse is now confirmed sound; semantic validity under repurposing is not).

## 6. Is the `diesel_hours_running` t=0 convention compatible with existing state handling?

**Yes.** `station_state.diesel_hours_running` is already a real, maintained field
(confirmed: incremented by `DigitalTwinSimulator.step` every cycle,
`diesel_hours = current_state.diesel_hours_running + 1.0 if diesel_running else 0.0`). Using
its carried-forward value to decide whether a t=0 minimum-up-time obligation is already
satisfied is consistent with how this field is already used elsewhere in the codebase; no
conflicting usage was found.
**Classification: NO ISSUE.**

## 7. Hidden 5th objective stage or unintended objective change?

**None found.** `P_unmet_essential` is explicitly uncosted in every tier; `J1`–`J4`'s
existing coefficients are untouched; no new priority level was added. (This narrow question
is answered cleanly — the *consequence* of leaving it uncosted is a separate problem,
covered in #3.)
**Classification: NO ISSUE.**

## 8. Indirect diesel-reduction tuning?

**None found.** The bus-bar amendment only adds a new possible *destination* for energy
whose *quantity* is still determined entirely by the unchanged `J1`–`J3` minimization; no
fuel coefficient, reserve mechanism, or priority weighting was altered.
**Classification: NO ISSUE.**

## 9. Is terminal reserve genuinely unchanged?

**Yes.** No part of Rev. 2's revisions touches `e_stage2_target`, the terminal-target
formula, or `J2`'s priority/role. Confirmed by direct re-reading of §4 of the revised spec.
**Classification: NO ISSUE.**

## 10. Remaining research assumptions / human governance decisions

Everything Rev. 2 itself already disclosed remains open (Essential-tier costing policy,
`deferrable_loads` deferred to future scope, flat-profile adequacy pending SD-01). This
audit adds two newly-identified items that need resolution **before** (not after) any
implementation, since they are coherence problems, not open policy questions:
- The constraint #4 / `unmet_load` double-counting gap (#1 above).
- The Essential-tier's lack of any mechanism to actually prefer being served over battery
  charging (#3 above).
- The Tier 2 vs. Tier 3 assignment of `curtailable_loads` (#2 above) — a choice, not a bug,
  but one that should be flagged as a judgment call rather than a settled mapping.

---

## Classification summary

| # | Check | Classification |
|---|---|---|
| 1 | Essential load energy-balance correctness | **BLOCKING** (new: demand-side constraint #4 not amended, causes double-counting) |
| 2 | `curtailable_loads` → Essential-tier mapping support | **NEEDS CLARIFICATION** |
| 3 | Uncosted `P_unmet_essential` functional meaningfulness | **BLOCKING** (new: indistinguishable from routing surplus to battery charge instead) |
| 4 | Flat 24h `essential_demand[t]` validity/bounds | **ACCEPTABLE RESEARCH ASSUMPTION** |
| 5 | Reusing router's `EmergencyAssessment` | **NEEDS CLARIFICATION** (narrowed: mechanically sound, semantically unverified) |
| 6 | `diesel_hours_running` t=0 convention | **NO ISSUE** |
| 7 | Hidden 5th stage / unintended objective change | **NO ISSUE** |
| 8 | Indirect diesel-reduction tuning | **NO ISSUE** |
| 9 | Terminal reserve unchanged | **NO ISSUE** |
| 10 | Remaining assumptions/decisions | (enumerated above; not a pass/fail item) |

---

## Conclusion

## NOT READY

**Exact blockers**:
1. Constraint #4 (`p_served + p_unmet = demand`) was not amended to also account for
   `p_served_essential` — the reported `unmet_load` metric would double-count served
   Essential-tier energy as unmet. (§1)
2. `P_unmet_essential` being entirely uncosted gives the solver no preference to serve
   Essential load over routing the same free surplus into additional battery charging —
   the tier's actual behavior is not guaranteed to differ from not having added it at all.
   (§3)

Both are specification-coherence defects, not missing data or unresolved policy — they are
fixable by revising the design again, the same way Rev. 1's blockers were. `NEEDS
CLARIFICATION` items (#2, #5) do not block a further revision pass but should be addressed
or explicitly carried forward as disclosed limitations.

## STOP

Second-pass design audit complete. No code, config, or model changed. No fix applied. GAP19
remains frozen as the control.
