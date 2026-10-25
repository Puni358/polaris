# Change Log: Rev. 1 → Rev. 2 (addressing `MILP_V2_DESIGN_AUDIT.md`)

| Audit finding | Severity | How addressed in Rev. 2 |
|---|---|---|
| #1 Bus-bar balance never amended for `p_served_essential` | BLOCKING | Bus-bar equation explicitly rewritten to include `p_served_essential` as a sink: `p_sol+p_wind+p_dis+p_diesel = p_served + p_served_essential + p_chg + p_flex`. |
| #4 `deferrable_loads` used to represent sheddable Essential demand, contradicting its own rescheduling semantics | BLOCKING | Essential-tier data source changed from `deferrable_loads` to `curtailable_loads`, whose schema (`max_power_w`, `curtailment_penalty_per_wh`) actually represents a "may be unserved, at a cost" concept. `deferrable_loads`' true scheduling semantics explicitly marked out of scope, not modeled. |
| #6 No defined owner for infeasibility→OptionD routing; no defined source for `EmergencyAssessment` | BLOCKING | Ownership assigned to the orchestration/calling layer (not `gap19_highs_native.py`); mechanism specified as reusing the `assessment` object the router's single call *already* returns on every route (`NORMAL` included). Residual uncertainty (whether OptionD's internals assume an `EMERGENCY`-classified assessment) explicitly flagged as unverified, not resolved. |
| #10 No conversion rule from load-schedule fields to `essential_demand[t]` | BLOCKING | Resolved as a consequence of switching to `curtailable_loads` (#4): since that schema has no time-of-day field, the only non-inventive conversion is a flat `essential_demand[t] = max_power_w` for all 24 hours — stated explicitly as a schema-forced simplification. |
| #2/#9 `J4` conflates essential-shedding cost with curtailment cost; unit mismatch with D10 | NEEDS CLARIFICATION | **Resolved by deferral, not by invention**: `P_unmet_essential` is now modeled (bounded, balanced) but explicitly left **uncosted** — no coefficient assigned in any objective tier. The $/Wh-vs-raw-Wh unit mismatch that blocked a clean numeric answer is stated plainly rather than papered over. |
| #5 Minimum-up-time boundary condition at `t=0` unspecified | NEEDS CLARIFICATION | Specified: already-elapsed `station_state.diesel_hours_running` counts toward the minimum; constraint only forces continuation if that value is still short of `min_up_time_hours` at the start of the horizon. Labeled a standard modeling convention, not a policy choice. |
| `curtailable_loads` never addressed | (raised alongside #9/#10) | Now explicitly the Essential tier's data source (see #4/#10 above) — no longer unaddressed. |

## Preserved, unchanged, re-confirmed in Rev. 2

- Terminal reserve unit/formula/mechanical entry — untouched.
- Current GAP19 — frozen as the control throughout.
- No diesel-reduction tuning — re-confirmed; the newly-added `P_unmet_essential` has zero
  objective cost, so it cannot bias diesel dispatch either.
- 4-stage lexicographic structure (D15) — untouched; the `J4`-placement question was
  resolved by deferring costing, not by adding a 5th stage.

## What is still open after Rev. 2 (by design, not oversight)

- Whether/how to eventually cost `P_unmet_essential`.
- Whether `deferrable_loads`' scheduling semantics should be modeled in a future revision.
- Whether `OptionDFallbackSolver` can correctly consume a reused, `NORMAL`-classified
  assessment (unverified against `option_d.py`).
- Whether the flat `essential_demand[t]` profile is acceptable even for research purposes,
  absent real circuit-level timing data (SD-01).

## STOP

No code, config, or model changed. No implementation performed.
