# Audit of the Two Remaining Unresolved Items in `MILP_V2_REV3_UNRESOLVED_ITEMS.md`

**Scope**: Audit/trace only. No code, config, or model changed; nothing implemented or run.
GAP19 remains frozen as the control.

---

## 1. MILP infeasibility fallback — traced through the real orchestration code

**Major finding: a real, already-running fallback path exists — and it is not OptionD.**
Rev. 1–3's entire line of inquiry (whether a `NORMAL`-route `EmergencyAssessment` could be
reused for `OptionDFallbackSolver`) was examining the wrong mechanism. Direct trace of
`system/orchestration/worker.py:245-293` (the Cell B closed-loop path) shows:

```python
if route == "NORMAL":
    plan = self.optimizer.optimize(bundle, st_k, self.configs)
elif route == "EMERGENCY":
    plan = self.option_d_solver.solve(assessment, bundle, st_k, self.configs)
else:
    status = "FAILED_UNKNOWN_INVALID"; break

if plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
    # "Gate-02 Option C governed relaxation re-solve"
    relaxed_config = dict(self.configs)
    relaxed_config["optimizer"]["allow_flexible_load_relaxation"] = True
    relaxed_plan = self.optimizer.optimize(bundle, st_k, relaxed_config)
    if relaxed_plan.constraint_status == "OPTIMAL":
        plan = relaxed_plan   # adopt, log an operator event
    else:
        status = "BLOCKED_INFEASIBLE"; break   # halt fail-closed, no dispatch, no Twin step
```

**`OptionDFallbackSolver` is never called for MILP-level infeasibility — only for the
router's own `EMERGENCY` classification, a completely separate decision made before either
solver runs.** The real existing answer for solver-level infeasibility is: attempt a
relaxed re-solve (Gate-02 Option C), and if that also fails, **halt the run fail-closed**
(`BLOCKED_INFEASIBLE`) — no zero-dispatch plan is executed, no simulator step occurs.

**However — the relaxation mechanism itself is confirmed non-functional.** Exhaustive
search confirms `allow_flexible_load_relaxation` is set by `worker.py` but **never read
anywhere in `gap19_highs_native.py`** (or anywhere else in the codebase). The "relaxed"
re-solve passes an identical MILP to the one that just failed — it will, in practice,
return the same `OPTIMIZATION_INFEASIBLE` status, and the loop will fall through to
`BLOCKED_INFEASIBLE` essentially every time this path is exercised.

**Conclusion for this item**:
- A real, existing, already-running control-flow path **does** exist, and it correctly does
  **not** force `OptionD` (confirming Rev. 3's withdrawal of that proposal was the right
  call, for the right underlying reason, even though Rev. 3 hadn't yet traced this far).
- That path's remediation step (the relaxation itself) is a **pre-existing defect in the
  frozen control**, not something v2's Essential-tier feature introduced or is responsible
  for fixing. v2, like everything else it doesn't explicitly change, **inherits this
  behavior unchanged**: on persistent infeasibility, the run halts (`BLOCKED_INFEASIBLE`).
- **This does not block v2 as scoped.** v2's Essential-tier addition does not depend on
  fixing this pre-existing gap — it operates entirely within the same MILP that is already
  infeasibility-handled (if bluntly) by the orchestration layer.
- **If a real (non-halting) remediation is ever wanted**, a new interface is required:
  `gap19_highs_native.py` would need to actually read `allow_flexible_load_relaxation` (or
  an equivalent signal) and loosen some currently-hard bound (most plausibly the Tier 3
  Flexible/Interruptible treatment, or — now that it exists — the new Essential-tier
  `essential_demand[t]` bound) when set. This is new MILP formulation work, not currently
  specified anywhere, and is explicitly **out of scope** for the Essential-tier feature
  itself.

**Classification**: **RESOLVED BY EXISTING EVIDENCE** (for v2's actual scope — inherit the
existing halt-on-infeasibility behavior unchanged, confirming no new mechanism is needed for
Rev. 3 to proceed) — with a separate, clearly-scoped **REQUIRES NEW ARCHITECTURE** finding
for the *pre-existing, inherited* defect (non-functional relaxation), which is not a v2
blocker but should be reported as a standing gap in the frozen control.

---

## 2. `curtailable_loads` Tier 2 vs. Tier 3 mapping — searched for distinguishing evidence

**Searched**: `loads.yaml` schema fields, `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`,
`POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md`, `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` v2.5.0.
**No document anywhere explicitly states which named tier either `deferrable_loads` or
`curtailable_loads` belongs to.**

**New evidence found, not previously weighed in Rev. 1–3**: `loads.yaml`'s
`deferrable_loads` entry (`water_pumping_heat_store`) carries an explicit `priority: 2`
field. `curtailable_loads`' entry (`secondary_heating`) carries **no priority field at
all**. If `loads.yaml`'s `priority` numbering were intended to correspond directly to
D01's tier numbering (Tier 1 = Critical, Tier 2 = Essential/Flexible, Tier 3 =
Interruptible/Noncritical), this would suggest **`deferrable_loads`, not
`curtailable_loads`, is the Tier 2 candidate** — the opposite of what Rev. 1–3 assumed.

**Why this is suggestive, not conclusive**: there is only one entry in each category, so
`priority: 2` cannot be cross-checked against other entries to confirm it is a *tier* label
rather than, e.g., an internal shedding-order rank within a category that happens to have
only one member today. No document defines what the `priority` field numbering scheme is
meant to represent, or ties it to D01's three named tiers. **The evidence points in a
direction but does not resolve the question.**

**Conclusion for this item**: still unresolved. This new evidence, if anything, weakens
Rev. 3's existing choice (curtailable_loads → Tier 2) rather than strengthening it — it
raises a real possibility that `deferrable_loads` is the better Tier-2 candidate (even
though Rev. 2's separate, still-valid finding that `deferrable_loads`' *scheduling*
semantics don't fit a shedding mechanism remains true and unaffected by this). **This
finding should be carried forward into any future revision of the Essential-tier data
source choice, not acted on here.**

**Classification**: **REQUIRES GOVERNANCE DECISION** — D01/D02 themselves state that exact
tier mechanics and mapping are `NEXT_EMS_OBJECTIVE_SPECIFICATION` (not yet governed); no
amount of further document search within this repository resolves it, since the documents
that would resolve it do not yet exist.

---

## Is Rev. 3 ready for implementation once these two items are resolved?

**Item 1 is, in effect, already resolved for v2's scope** — no further action is required
before implementation on this point; v2 simply inherits the existing (blunt, confirmed
non-functional-but-safe) halt-on-infeasibility behavior, unchanged. The separately-flagged
pre-existing defect (unimplemented relaxation) remains open but does not block v2.

**Item 2 remains genuinely open**, and this audit's new finding (the `priority: 2` field)
means it should not simply be waved through — accepting Rev. 3's `curtailable_loads` → Tier
2 assignment as a labeled judgment call is still defensible *if explicitly flagged
alongside this counter-evidence*, but a future revision or real governance input could
reasonably reverse it.

**Overall**: Rev. 3 can proceed to research-only implementation **once item 2 is either (a)
explicitly re-confirmed as a judgment call with this new counter-evidence disclosed
alongside it, or (b) revisited with `deferrable_loads` reconsidered as the Tier-2 source**
(noting Rev. 2's scheduling-semantics objection to `deferrable_loads` would then need to be
addressed on its own terms, not reopened lightly). Item 1 imposes no further precondition.

## STOP

Audit complete. No code, config, or model changed. No redesign performed. GAP19 remains
frozen as the control.
