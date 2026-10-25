# Demand-Tier Policy Audit (pre-MILP-v2)

**Scope**: Audit only. No code, config, or model changed; no experiment run. Current GAP19
remains the unmodified control. Sources: `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md`,
`POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`, `loads.yaml`, `gap19_highs_native.py`,
`milp.py` (prior optimizer, for contrast). No value or policy rule is invented below;
anything not found in these sources is marked unresolved.

---

## 1. Current authorized policy

| Tier | Authorized (HUMAN_SELECTED, per D01/D02/D03-05) | What GAP19 actually implements |
|---|---|---|
| **Critical** | Must exist as a distinct tier (D01); protected, 100% service, 0 kWh unmet in normal operation, 0 min interruption, enforced as a **hard constraint, not a soft economic penalty** (D03/D04/D05 + explicit note rejecting `milp.py`'s $10,000/kWh penalty as "NOT the policy SLA") | `p_served ≤ critical_demand` (hard cap via equality constraint), `P_unmet_crit` costed at the top lexicographic priority (`J1`). **Matches authorized policy** for the hard-constraint requirement. |
| **Essential / Flexible** (managed shedding) | Must exist as a distinct tier (D01); may be curtailed/deferred, but only via a "predefined priority shedding structure" (D02) | **Not implemented.** No tier-2 logic exists; `loads.yaml`'s `deferrable_loads`/`curtailable_loads` entries (intended for this tier) are never read by `gap19_highs_native.py`. |
| **Interruptible / Noncritical** | Shed first (D01/D02) | **Not implemented as its own category** — collapsed together with the Essential/Flexible tier into one undifferentiated `p_unmet`, uncosted, unlimited, unlogged. |

**`unmet_load` interpretation**: `p_unmet = demand − p_served`, and `p_served` is capped at
`critical_demand` by a separate equality constraint, independent of generation availability.
`p_unmet` has **zero coefficient in every objective term** (`c1`–`c4`). **It is therefore
not a valid performance metric for anything except "total demand minus critical demand"** —
it does not measure shedding of a managed Essential/Flexible tier (none exists), does not
respond to solar/wind/diesel/battery availability, and is not something the solver ever
tries to minimize. It cannot be used to compare reliability, dispatch quality, or forecast
value between scenarios (confirmed: it was identical between the R1/R2 baseline and Stage
8.1 arms at every origin, for exactly this reason).

## 2. Unresolved decisions (confirmed `PENDING`/`NEXT_EMS_OBJECTIVE_SPECIFICATION`, not
invented here)

- **Circuit-level mapping** of actual station loads into Critical/Essential/Interruptible —
  `PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION` (D01).
- **Exact shedding/restoration logic** for the Essential/Flexible and Interruptible tiers:
  priority sequence, restoration triggers, dwell/chattering-prevention timing —
  `PENDING_STAKEHOLDER_OR_ENGINEERING_DEFINITION` (D02); the "5-minute dwell" figure
  sometimes cited is explicitly `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE`.
- **Mathematical formulation of the critical-load hard constraint** — the *policy* (hard
  constraint) is decided; the *governed mathematical specification* of it is
  `NEXT_EMS_OBJECTIVE_SPECIFICATION`. GAP19's current `p_served ≤ critical_demand` formulation
  is an engineering implementation, not itself a ratified specification.
- **Whether/how Essential-Flexible load curtailment should be costed or bounded** — no
  governed numeric value exists (`loads.yaml`'s `curtailment_penalty_per_wh: 0.10` and
  `deferrable_loads` priority fields are `CURRENT_IMPLEMENTATION_FACT` / prototype only, not
  stakeholder-authorized, and are not even read by GAP19).
- **Hardware validation** of the 0-minute/0-kWh critical targets (ATS switching gap, UPS
  hold-up time) — `STATION_SPECIFIC_VALIDATION_REQUIRED` (SD-02, SD-03).
- **Whether `unmet_load` should be redefined, removed, or given a real cost/role** once a
  tier-2/3 formulation exists — not addressed by any existing document (this is the (D)
  finding from the prior formulation audit, not a settled question).

## 3. What must be decided before a MILP v2 can be designed

1. A governed **mathematical specification** for the already-authorized critical-load hard
   constraint (translating D03/D04/D05 into an explicit, ratified formulation — GAP19's
   current one is engineering-only, not yet a governed spec).
2. A **governed shedding/restoration structure** for the Essential/Flexible and
   Interruptible/Noncritical tiers (priority sequence, dwell/restoration timing) — currently
   entirely unspecified (D02's own mechanics are `NEXT_EMS_OBJECTIVE_SPECIFICATION`).
3. **Station-specific circuit mapping** of real loads into the three tiers (D01) — without
   this, any tiered MILP v2 would still be running on synthetic/prototype load data.
4. An explicit decision on **what `unmet_load` (or its replacement) should mean and cost**
   once tiers 2/3 exist — otherwise a v2 model risks inheriting the same
   non-informative-metric problem found in GAP19 today.
5. (Carried over from the earlier terminal-reserve audits, still open and relevant to any v2
   scope) — DEC-TR-03/DEC-RES-03 and SD-07/SD-08, since a v2 would still need a governed
   reserve formulation independent of whatever load-tier changes are made.

## STOP

Audit complete. Current GAP19 remains the unmodified control. No redesign proposed.
