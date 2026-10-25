# Design Audit: `MILP_V2_RESEARCH_SPECIFICATION.md` (pre-implementation stress test)

**Scope**: Audit only, of the design document itself. **No code, config, or model changed;
nothing implemented or run.** GAP19 remains frozen as the control. This audit is
deliberately critical of the author's own prior design — several genuine gaps were found
and are reported as such, not smoothed over.

---

## 1. Mathematical consistency

**Issue found — BLOCKING.** The spec introduces a new variable `p_served_essential[t]` and
a new demand-balance equality (`p_served_essential + P_unmet_essential = essential_demand`),
but **never specifies how `p_served_essential` connects to the bus-bar power balance**
(`gap19_highs_native.py:227-231`: `p_sol_used + p_wind_used + p_dis + p_diesel = p_served +
p_chg + p_flex`). As written, `p_served_essential` has no generation source feeding it — it
is bounded `[0, essential_demand]` but nothing in the stated formulation forces or even
permits it to be nonzero via any energy source. This is not a minor omission: without
amending the bus-bar equation to `... = p_served + p_served_essential + p_chg + p_flex`,
the new variable is mathematically disconnected from the rest of the model.

## 2. Lexicographic priority consistency

**Issue found — NEEDS CLARIFICATION.** Folding Essential-tier shortfall into the existing
`J4` vector alongside curtailment, both at coefficient `1.0` per Wh, makes 1 Wh of
*essential-load shedding* and 1 Wh of *renewable curtailment* **exactly interchangeable** in
the objective. These are not policy-equivalent: D10 explicitly authorizes curtailment
*without* objective penalty ("necessary renewable curtailment... allowed without explicit
objective penalty"), while D02 implies Essential-tier shedding should be actively *managed*
(implying it should matter more, not equally). Conflating them in one coefficient either
under-penalizes shedding or risks reading as adding an unauthorized penalty to curtailment
that D10 says should not exist. The stage-count preservation (no 5th tier) is sound; the
specific placement inside `J4` is not adequately justified as currently written.

## 3. Critical-load hard-constraint preservation

**Issue found — NEEDS CLARIFICATION (blocked by #1).** Whether adding
`p_served_essential` could ever compete with critical load for the same generation cannot be
fully verified until the bus-bar integration in #1 is actually written out — the current
spec does not contain enough detail to confirm `J1`'s priority and Layer B's cap on
`p_served` remain fully isolated from the new variable. No evidence of an actual violation
was found, but this is **unverified**, not **confirmed safe**.

## 4. Essential/managed-shedding behavior

**Issue found — BLOCKING.** The spec sources `essential_demand[t]` from `loads.yaml`'s
`deferrable_loads` entries. But a *deferrable* load (per `loads.yaml`'s own schema —
`earliest_start_h`, `latest_finish_h`, `duration_hours`) means the load's total required
energy must eventually be served *somewhere within its allowed time window* — it is a
**rescheduling** concept, not a **shedding** concept. The v2 spec instead treats it as a
per-hour quantity that may simply be partially unserved with a shortfall cost — this does
not capture (and is inconsistent with) the deferral semantics the chosen data source itself
implies. Using `deferrable_loads` to build a "may be shed" tier is a category mismatch, not
a research-acceptable simplification, because it contradicts the very config structure cited
as its evidence.

## 5. Diesel minimum-up-time formulation

**Issue found — NEEDS CLARIFICATION.** The spec states the standard constraint shape
("`u_diesel[t]` must remain 1 for ≥2 consecutive hours after a start") but does not specify
the boundary condition at `t=0`, where diesel may already be running
(`station_state.diesel_running`/`diesel_hours_running`, carried in from the prior cycle).
Does the already-elapsed run time count toward satisfying the minimum, or does the
constraint apply only to fresh in-horizon starts? Standard unit-commitment formulations
handle this, but the spec as written does not specify which convention is used, and
interaction with the existing `v_start` tracking constraint (`gap19_highs_native.py:277-285`)
is asserted, not demonstrated, to be conflict-free.

## 6. Infeasibility → OptionD fallback behavior

**Issue found — BLOCKING.** This is the most significant gap found. GAP19's own
infeasibility signal (`model_status != kOptimal`) occurs **inside** `optimizer.optimize()`,
called only *after* the router has already chosen the `NORMAL` route. `OptionDFallbackSolver`
is, in the current architecture, invoked by the **router** (`EMSControlRouter.evaluate_and_
route`) *before* the optimizer runs, and takes an `EmergencyAssessment` object the router
itself produces from its own ECD evaluation. The v2 spec's proposal — "on that same
infeasibility signal, route explicitly to OptionD" — does not identify *who* performs this
routing (it is not something `gap19_highs_native.py` itself can do, since it has no
reference to the router or an `EmergencyAssessment`), nor whether `OptionDFallbackSolver`
can function correctly when called from a code path where the router never flagged
`EMERGENCY` in the first place (no valid `assessment` object would exist to pass it). This
is an unresolved control-flow/integration question, not a detail to be filled in later.

## 7. Interaction between diesel, battery, reserve, and load shedding

**Blocked by #1.** Cannot be meaningfully assessed until the bus-bar integration for the new
Essential-tier variable is actually specified — there is currently no energy-balance pathway
through which diesel, battery, or renewables could serve Essential load at all.

## 8. Whether any change accidentally optimizes for lower diesel

**No issue found.** Reviewed each proposed change individually:
- Minimum-up-time enforcement: explicitly flagged direction-neutral in the spec, and
  correctly so — such constraints can increase or decrease total fuel depending on the
  scenario; no bias toward lower diesel is introduced.
- Essential-tier costing: does not touch any diesel/fuel coefficient, the reserve mechanism,
  or the `J1`–`J4` priority order. If anything, giving Essential load a nonzero cost creates
  pressure to serve *more* total load (which could *increase*, not decrease, diesel use, once
  #1 is resolved and the pathway exists) — the opposite of a diesel-reduction bias.
- Infeasibility→OptionD routing: only affects the rare infeasible case; does not alter the
  `OPTIMAL`-path fuel objective at all.
**Conclusion**: none of the three proposed changes optimizes for, or is biased toward, lower
diesel use, individually or in combination.

## 9. Contradictions with the simulated policy package or existing authorized governance

- The `J4`-coefficient conflation in #2 creates tension with D10 ("curtailment without
  explicit objective penalty") once Essential-tier shedding shares that same coefficient —
  flagged above, not a new finding here.
- The `deferrable_loads`-as-"sheddable" mismatch in #4 is itself a conflict with the
  config data's own intended semantics, though not with any stakeholder decision directly
  (no document authorizes treating deferrable loads as sheddable either way).
- The OptionD routing proposal is consistent *in intent* with D06 (dedicated fallback, not a
  soft-penalty trade-off) — no conflict on that narrow point; the conflict is purely
  technical/architectural (#6), not a governance contradiction.
- No change found that contradicts the critical-load hard-constraint policy (D03-05) or the
  4-stage lexicographic order (D15) — both are explicitly preserved as designed.

## 10. Missing required inputs/data

- **`essential_demand[t]` conversion logic**: `loads.yaml`'s `deferrable_loads` entries give
  `power_w`/`duration_hours`/`earliest_start_h`/`latest_finish_h`/`priority` for one load —
  no rule is specified for converting this into a 24-element per-hour demand array. This is
  missing, not merely unauthorized.
- **`curtailable_loads`** (`secondary_heating`, 5 kW, `curtailment_penalty_per_wh: 0.10`) is
  never addressed by the v2 spec at all — it is unclear whether this second `loads.yaml`
  category belongs to the new Essential tier, the unchanged Flexible/Interruptible tier, or
  neither.
- Real circuit-level load data (SD-01) — already disclosed as missing in the spec itself;
  no new finding, confirmed still open.

---

## Classification summary

| # | Area | Classification |
|---|---|---|
| 1 | Mathematical consistency (bus-bar integration) | **BLOCKING** |
| 2 | Lexicographic priority (`J4` conflation) | **NEEDS CLARIFICATION** |
| 3 | Critical hard-constraint preservation | **NEEDS CLARIFICATION** (blocked by #1) |
| 4 | Essential-tier semantics (`deferrable_loads` mismatch) | **BLOCKING** |
| 5 | Min-up-time boundary condition | **NEEDS CLARIFICATION** |
| 6 | Infeasibility → OptionD integration | **BLOCKING** |
| 7 | Diesel/battery/reserve/shedding interaction | **NEEDS CLARIFICATION** (blocked by #1) |
| 8 | Accidental diesel-reduction bias | **NO ISSUE** |
| 9 | Governance contradictions | **NEEDS CLARIFICATION** (D10 tension via #2) |
| 10 | Missing inputs | **BLOCKING** (`essential_demand[t]` mapping), **NEEDS CLARIFICATION** (`curtailable_loads` role) |

---

## Conclusion

## NOT READY

**Exact blockers**:
1. `p_served_essential` is not connected to the bus-bar energy balance — the Essential tier
   has no defined generation pathway (§1).
2. The Essential-tier data source (`deferrable_loads`) models a rescheduling concept, not a
   shedding concept — the v2 spec's use of it contradicts its own cited evidence (§4).
3. The infeasibility → OptionD routing proposal has no defined owner in the control flow and
   may call `OptionDFallbackSolver` without a valid `EmergencyAssessment` (§6).
4. No conversion rule exists from `deferrable_loads`' schedule fields to an
   `essential_demand[t]` array (§10).

These are design-specification gaps, not policy or data unavailability issues — they can be
addressed by revising the specification (not by waiting on real station data), but they must
be resolved **before** any implementation is attempted. The `J4`-coefficient conflation (§2)
and min-up-time boundary condition (§5) should also be clarified, though they are less severe
than the four blockers above.

## STOP

Design audit complete. No code, config, or model changed. No redesign performed. GAP19
remains frozen as the control.
