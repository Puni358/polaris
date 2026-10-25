# MILP v2 — Research-Only Design Specification (Rev. 2)

**Status**: Design document only. **No code, config, or model is modified or implemented.
No MILP is run.** GAP19 (`gap19_highs_native.py`) remains frozen, unmodified, as the
control. This revision addresses the four `BLOCKING` findings and the three flagged
clarification items from `MILP_V2_DESIGN_AUDIT.md`. Per instruction, nothing below invents a
policy decision, a numerical value, or a load-scheduling semantic beyond what existing
`loads.yaml`/governance evidence actually supports; where evidence is insufficient, the item
is marked **UNRESOLVED**, not silently decided.

---

## 1. Load-tier formulation (revised)

### Essential / managed-shedding tier — re-grounded in `curtailable_loads`, not `deferrable_loads`

**Audit finding addressed**: Blocker #2 and #4.

`loads.yaml` contains two distinct candidate structures, which the original spec conflated:

- **`deferrable_loads`** (`water_pumping_heat_store`: `power_w`, `duration_hours`,
  `earliest_start_h`, `latest_finish_h`, `priority`) — this schema describes a load whose
  **total required energy must eventually be served somewhere within an allowed time
  window** (a *rescheduling* concept). It contains no field representing "may be partially
  or permanently unserved." Using it as a shortfall-with-cost tier, as Rev. 1 did, **is not
  supported by the schema's own semantics** and is withdrawn.
- **`curtailable_loads`** (`secondary_heating`: `max_power_w`, `curtailment_penalty_per_wh`)
  — this schema already represents exactly the concept needed: a load that **may be reduced
  / not served, at an explicit existing per-Wh cost**. This is the correct, evidence-grounded
  source for the Essential/managed-shedding tier.

**Revised representation**: the Essential/managed-shedding tier is built from
`curtailable_loads` only. `deferrable_loads`' true scheduling/deferral semantics are **not**
modeled in this v2 (that would be a separate, larger mechanism — true horizon-spanning
deferral constraints — and is explicitly marked **UNRESOLVED / OUT OF SCOPE** for this
revision, not silently folded into shedding).

**Conversion to the 24h horizon (Blocker #4)**: `curtailable_loads`' schema has no
time-of-day field at all (`max_power_w` only). The only conversion that does not invent
unsupported data is a **flat profile**: `essential_demand[t] = secondary_heating.max_power_w`
for all `t = 0..23`. This is stated explicitly as a simplification forced by the schema's
own lack of time information, not a hidden assumption — a real circuit-level load profile
(SD-01, still missing) would very likely not be flat.

### Mathematical/bus-bar integration (Blocker #1)

New variables (mirroring the existing critical-load layer exactly):
- `p_served_essential[t] ∈ [0, essential_demand[t]]`
- `P_unmet_essential[t] ∈ [0, essential_demand[t]]`

New constraint (per `t`, mirroring Layer B):
`p_served_essential[t] + P_unmet_essential[t] = essential_demand[t]`

**Bus-bar balance equation is amended** (this is the fix for Blocker #1 — the prior
revision omitted it):
```
p_sol_used[t] + p_wind_used[t] + p_dis[t] + p_diesel[t]
    = p_served[t] + p_served_essential[t] + p_chg[t] + p_flex[t]
```
`p_served_essential` is now a real sink with a real generation pathway, on equal footing
with `p_served`, `p_chg`, and `p_flex` in the same equality.

### Flexible / Interruptible-Noncritical (Tier 3)

**Unchanged from Rev. 1**: remains fully uncosted, unconditionally unmet — D02 explicitly
authorizes this tier to be deprioritized most heavily ("shed first"), and no other
`loads.yaml` category is available to populate it with real data.

## 2. Critical-load hard constraint and infeasibility handling (revised)

### Hard constraint mechanism

**Unchanged.** `p_served ≤ critical_demand`, `P_unmet_crit` at `J1`. With §1's bus-bar
amendment, `p_served` and `p_served_essential` are now both explicit, separate sinks —
`p_served`'s cap at `critical_demand` is untouched by the amendment, so Critical's hard
priority is preserved (addresses audit item #3).

### Infeasibility → OptionD routing (Blocker #3)

**Audit finding**: the original proposal did not identify who performs the routing or
how a valid `EmergencyAssessment` would be obtained for a cycle the router had already
classified `NORMAL`.

**Revised ownership and mechanism**: `EMSControlRouter.evaluate_and_route()` **already
returns an `EmergencyAssessment` object on every call, regardless of which route
(`NORMAL`/`EMERGENCY`) it selects** — confirmed from its own signature/contract
(`-> Tuple[EmergencyAssessment, str]`). The calling/orchestration layer (`worker.py` or
equivalent — **not** `gap19_highs_native.py`, which correctly has no knowledge of the
router or OptionD) already holds this `assessment` object from the single router call made
*before* either solver is invoked. The revised proposal is:

> If the `NORMAL`-route optimizer call returns `constraint_status` indicating infeasibility,
> the calling/orchestration layer invokes `OptionDFallbackSolver.solve(assessment, bundle,
> st_k, configs)` using the **same `assessment` object already produced by the router call
> that selected `NORMAL`** — no new assessment is constructed.

**Explicitly flagged as unverified (research assumption, not a confirmed fact)**: whether
`OptionDFallbackSolver`'s internal logic assumes/requires an assessment that reflects a
genuine `EMERGENCY`-level risk classification, such that reusing a `NORMAL`-classified
assessment object (repurposed outside its originally intended use) could produce incorrect
or misleading OptionD output. This would need to be checked against `option_d.py`'s actual
internal use of the `assessment` fields before any implementation — **not verified in this
design pass**.

## 3. Emergency Mode entry/mapping using the simulated 6h assumption

**Unchanged from Rev. 1.** No code change; formally designates the existing, unmodified
`EMSControlRouter` logic (built on the `GOVERNANCE_AUTHORIZED` $T_{\text{REQUIRED}}=6h$) as
satisfying the governed mapping requirement.

## 4. Terminal reserve

**Unchanged from Rev. 1, in full.** Unit (Wh), formula (40,000 Wh floor + 6h trailing
deficit × 1.10), and its mechanical entry into the optimization (`e_stage2_target[23]`,
strict `J2` priority, no weighting) are all preserved exactly as before. The counterfactual
isolation (`COUNTERFACTUAL_CAUSAL_ISOLATION_REPORT.md`) remains the reason: this mechanism
is not implicated in the diesel increase, so there is no basis to touch it, and touching it
would risk appearing diesel-motivated.

## 5. Diesel (revised: minimum-up-time boundary condition)

| | Rev. 1 | Rev. 2 | Reason |
|---|---|---|---|
| Minimum output, base/marginal/startup fuel | Unchanged | **Unchanged** | No new evidence |
| Minimum-up-time enforcement | Proposed, boundary condition unspecified | Proposed, **boundary condition now specified**: at `t=0`, if diesel is already running (`station_state.diesel_running = True`), the already-elapsed `station_state.diesel_hours_running` counts toward the minimum. The constraint only forces continued operation if `diesel_hours_running < min_up_time_hours` at the start of the horizon; it does not retroactively re-require a fresh 2h commitment for a unit that has already satisfied it. | This is a standard unit-commitment **modeling convention**, not a stakeholder policy choice — it uses the already-tracked `diesel_hours_running` field, nothing invented. Labeled a modeling convention requiring engineering (not governance) review, since it has not itself been reviewed. |

## 6. Battery

**Unchanged from Rev. 1, in full** (SOC limits, charge/discharge mechanics, reserve
interaction, deferred degradation modeling).

## 7. Objective / lexicographic priority order (revised: `J4` placement marked unresolved)

**Audit finding addressed**: audit item #2/#9 (D10 tension).

**Revised position**: whether/how Essential-tier shortfall (`P_unmet_essential`) should be
numerically weighted relative to curtailment within the existing `J4` vector is **marked
UNRESOLVED, not decided**, for the following reason found on inspection: `loads.yaml`'s
`curtailable_loads.curtailment_penalty_per_wh = 0.10` is denominated in **$/Wh** (an
economic cost), while GAP19's existing `J4` curtailment term is denominated in **raw Wh**
with coefficient `1.0` (no dollar conversion exists anywhere in the current objective).
Combining these would require either (a) reinterpreting the entire `J4` vector's units (a
structural change beyond this revision's scope) or (b) treating `0.10` as a dimensionless
relative weight (an invented reinterpretation of an economic figure, which this revision
declines to do). **No numeric treatment of Essential-tier shortfall within `J4` is proposed.**
The variable `P_unmet_essential[t]` exists (§1) and is bounded/balanced, but **is not yet
assigned a cost coefficient anywhere** — its priority/costing placement is left as an open
design question for a future revision or for real governance input, rather than silently
defaulted.

**Stage count and ordering**: **unchanged** — still exactly D15's four stages
(Critical → Resilience/Reserve → Fuel → Curtailment), no 5th stage introduced, no weighting
between existing stages. (Because `P_unmet_essential` is not yet costed at all per the
paragraph above, it currently has **no effect on the objective** — it is tracked/balanced
but not yet optimized against. This is an explicit, disclosed limitation of this revision,
not a hidden one.)

---

## What v2 (Rev. 2) fixes, relative to Rev. 1

- Bus-bar integration for the Essential-tier sink (Blocker #1) — now explicit.
- Essential-tier data source corrected from `deferrable_loads` to `curtailable_loads`,
  removing the semantic mismatch (Blocker #2).
- Infeasibility→OptionD ownership and assessment-reuse mechanism specified (Blocker #3),
  with the remaining uncertainty (OptionD's internal assumptions about the assessment)
  explicitly flagged rather than assumed away.
- `essential_demand[t]` conversion rule specified (flat profile, forced by schema
  limitation) (Blocker #4).
- Minimum-up-time boundary condition at `t=0` specified as a standard modeling convention.

## What remains explicitly UNRESOLVED (not decided, not invented)

- Whether/how `P_unmet_essential` should be costed at all (no proposal made; currently
  uncosted and therefore non-binding on the objective).
- Whether `deferrable_loads`' true scheduling/deferral semantics should be modeled in some
  future v3 — out of scope here, not addressed.
- Whether `OptionDFallbackSolver` can correctly consume a `NORMAL`-classified, reused
  `assessment` object — not verified against `option_d.py`'s internals.
- Whether the flat-profile approximation for `essential_demand[t]` is an acceptable research
  simplification or needs real circuit-level timing data (SD-01) before being usable even
  for research purposes.

## What is preserved unchanged from the original design intent (confirmed, not re-litigated)

- Terminal reserve: unit, formula, and mechanical entry into optimization — **unchanged**.
- Current GAP19 — **frozen**, unmodified, as the control throughout.
- No diesel-reduction tuning — confirmed again in this revision: none of the changes touch
  any fuel coefficient, the reserve mechanism, or introduce a weighted trade-off; the newly
  uncosted `P_unmet_essential` has zero objective effect, so it cannot bias diesel either.
- 4-stage lexicographic structure — **unchanged**; no 5th stage was introduced even after
  resolving the `J4`-placement question (it was resolved by *deferring* costing, not by
  adding a stage).

## STOP

Revised design specification only. No code was written, no config changed, no model
modified, no experiment run. GAP19 remains the frozen, unmodified control.
