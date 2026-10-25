# Comparison: `curtailable_loads` vs. `deferrable_loads` as the Essential/Tier-2 Source

**Scope**: Comparison/audit only. No code, config, or model changed; nothing implemented
or run. GAP19 remains frozen as the control. Nothing below is chosen based on diesel
impact — the comparison is purely about schema fit, governance textual support, and MILP
representability.

---

## A. `curtailable_loads` (`secondary_heating`)

| Aspect | Finding |
|---|---|
| **Schema semantics** | `{id, max_power_w: 5000, curtailment_penalty_per_wh: 0.10}` — a load that may be reduced/not served at a stated per-Wh cost. No ambiguity about what the fields mean. |
| **Priority field** | **Absent.** No ranking relative to any other load. |
| **Schedule/window field** | **Absent.** No time-of-day structure at all — any hourly profile applied to it is necessarily invented (addressed in Rev. 3 by using a flat profile, the only non-inventive choice given no time field exists). |
| **Existing POLARIS usage** | **Zero.** Never read by `gap19_highs_native.py` or the older `milp.py`. Pure unused config stub. |
| **Governance references** | No document names `curtailable_loads` or `secondary_heating` specifically. However, D02's own policy text — *"Flexible/deferrable/interruptible loads may be **curtailed** or deferred following a predefined priority shedding structure"* — uses "curtailed" as one of the two authorized *mechanisms* (alongside "deferred") for managing the non-critical load group collectively. This gives the *mechanism* (curtailment-with-cost) real textual grounding, though it does not name this specific config entry or assign it a tier number. |
| **24h MILP representability** | **Clean, direct fit.** A per-hour `p_served_essential[t] ∈ [0, max_power_w]` with shortfall costed at the existing per-Wh rate is exactly what the schema already describes — no new variable *type* or constraint *class* is needed beyond what Rev. 3 already specified. |
| **Assumptions required** | (1) That "curtailable" here means load-side curtailment, not renewable curtailment (reasonably clear from field names, but not stated in any governance document); (2) the flat time profile (schema has no time field, so unavoidable); (3) which tier number this belongs to (unresolved — see below). |
| **What would be lost/distorted** | Minimal. The per-hour shortfall-cost representation matches the schema's own apparent intent closely; nothing in the schema is discarded or overridden. |

## B. `deferrable_loads` (`water_pumping_heat_store`)

| Aspect | Finding |
|---|---|
| **Schema semantics** | `{id, power_w: 10000, duration_hours: 4, earliest_start_h: 8, latest_finish_h: 18, priority: 2}` — a load requiring a **total** of `duration_hours × power_w` energy, which may be scheduled **anywhere within** `[earliest_start_h, latest_finish_h]`. This is a rescheduling/assignment concept, not a per-hour shortfall concept. |
| **Priority field** | **Present: `priority: 2`.** No other entries exist to cross-check this against, so it cannot be confirmed whether "2" is a tier label matching D01's numbering or an internal rank with a different meaning — but it is real, existing evidence this candidate carries that `curtailable_loads` does not. |
| **Schedule/window field** | **Present** (`duration_hours`, `earliest_start_h`, `latest_finish_h`) — these are substantive data, not decorative; representing them correctly requires genuine scheduling constraints (see below). |
| **Existing POLARIS usage** | **Zero.** Also never read by either optimizer implementation. |
| **Governance references** | Same D02 text covers "deferred" as the other authorized mechanism, applied to the same load group — equal textual footing to `curtailable_loads` on this point. |
| **24h MILP representability** | **Requires a different, larger mechanism than Rev. 3's.** Correctly representing `duration_hours`/`earliest_start_h`/`latest_finish_h` needs new binary scheduling variables `z[t] ∈ {0,1}` for `t` in the allowed window, a constraint `Σ_t z[t] · \Delta t = duration\_hours` (or equivalent energy-total requirement), and `power\_served[t] = power\_w · z[t]`. **This is not an invented semantic** — it is the standard, textbook MILP representation of exactly the data the schema already provides. But it is a **different constraint class** from the simple per-hour shortfall-with-cost pattern Rev. 3 built for the Essential tier, and nothing in Rev. 1–3 specifies it. |
| **Assumptions required** | (1) That `priority: 2` denotes a D01 tier number (unconfirmed, only one data point); (2) the scheduling formulation above, which — unlike the flat-profile issue for `curtailable_loads` — is *not* an invented assumption, but *is* new, unspecified design scope; (3) what "unmet" even means for this load type (a binary "not fully scheduled within the window" condition, not a continuous hourly shortfall — a different reporting concept than `P_unmet_essential` as currently defined). |
| **What would be lost/distorted** | **If forced into Rev. 3's existing per-hour-shortfall mechanism** (treating `deferrable_loads` as if it were `curtailable_loads`-shaped, ignoring `duration_hours`/`earliest_start_h`/`latest_finish_h`), the load's actual scheduling flexibility and total-energy requirement would be silently discarded — this *would* be an invented, unsupported simplification. **If represented correctly** (via the scheduling constraints above), nothing is lost, but this is materially more design/implementation scope than anything currently specified. |

---

## Revisiting the prior objection directly

> "`deferrable_loads` represents rescheduling within a window, not arbitrary shedding."

**This objection is correct and is *not* resolved away by existing evidence — but it was
previously aimed at the wrong target.** The schema fields (`duration_hours`,
`earliest_start_h`, `latest_finish_h`) **do** fully and non-inventively support a proper
scheduling formulation — so *representing `deferrable_loads` correctly* requires no
invented semantics at all. What *would* require inventing semantics is the specific thing
Rev. 1 originally proposed: treating it as a simple shortfall-with-cost tier, which
discards the window/duration structure the schema actually specifies. **Conclusion: using
`deferrable_loads` as Rev. 3's existing Essential-tier mechanism (per-hour shortfall cost)
is not defensible; using it via a proper scheduling sub-formulation would be defensible,
but is a larger, currently unspecified design addition, not a drop-in data-source swap.**

---

## Classification

| Candidate | As a data source for *Rev. 3's existing* per-hour shortfall mechanism | As a correctly-modeled load type in its own right |
|---|---|---|
| **`curtailable_loads`** | **BETTER-SUPPORTED RESEARCH ASSUMPTION** — fits the existing mechanism cleanly, mechanism echoed in D02's "curtailed" language; tier-*number* assignment remains unresolved | n/a (its native representation already *is* the shortfall-cost mechanism) |
| **`deferrable_loads`**, forced into the existing shortfall mechanism | **NOT DEFENSIBLE** — discards `duration_hours`/window fields, inventing an unsupported simplification | — |
| **`deferrable_loads`**, modeled via proper scheduling constraints | n/a (different mechanism than Rev. 3 specifies) | **BETTER-SUPPORTED RESEARCH ASSUMPTION** on schema fit — arguably *stronger* than `curtailable_loads` on the tier-number question (the `priority: 2` field), but requires new, unspecified MILP machinery not present anywhere in Rev. 1–3 |

**Neither candidate is `GOVERNANCE-SUPPORTED`** — no document assigns a tier number to
either `loads.yaml` entry; D01/D02 themselves mark the exact tier-mapping mechanics
`NEXT_EMS_OBJECTIVE_SPECIFICATION`.

---

## Conclusion: can MILP v2 proceed with one explicitly labeled simulated assumption?

**Yes — with `curtailable_loads`, for Rev. 3's current scope — this is not a governance
blocker for proceeding to research-only implementation.** It is the only candidate that (a)
fits the mechanism already specified in Rev. 3 without further design work, and (b) does
not require discarding or distorting any schema field to use it. It must be labeled
`SIMULATED_RESEARCH_ASSUMPTION` for the tier-*number* assignment specifically (Tier 2 vs.
Tier 3 remains unconfirmed by any document), which Rev. 3 already does.

**`deferrable_loads` is not currently usable as a drop-in alternative** for the *same*
mechanism — adopting it properly would require designing and auditing a new scheduling
sub-formulation (new variables, a new constraint class), which is out of scope for the
current Rev. 3 and would need its own design/audit pass, not a one-line substitution. The
`priority: 2` evidence means this remains a live, better-than-previously-thought candidate
for a **future** revision, but choosing it now would require inventing the scheduling
mechanism's details beyond what any document specifies for *this* v2's timeline.

**This is a labeled simulated assumption, not a governance blocker**, because: (1) no
document would resolve the tier-number question even given more time to search (D01/D02
explicitly defer it), and (2) the `curtailable_loads` choice does not contradict any
authorized policy — it operationalizes D02's "curtailed" mechanism using the only existing
schema entry that supports it without invention. Proceeding is defensible as long as this
is disclosed exactly as above, not represented as resolved.

## STOP
