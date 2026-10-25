# POLARIS — ECD / Router Design-Decision Record (Documentation Only — No Implementation)

**Date:** 2026-10-18
**Repository:** `/home/punith-bs/01polaris (Copy)` (branch `master`, no commits exist)
**Nature of this document:** Design-decision analysis only, per the governing directive's Part 2. `system/control/router.py` and `system/control/ecd.py` were read-only inspected. **No edit was made to either file, or to `gap19_highs_native.py` or `manifest.py`, in producing this record.** Neither alternative discussed below — nor any other behavior change — is implemented here. This supersedes nothing in `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (2026-10-18); it extends that proposal with a second, previously unexamined defect (the `t_required_hours` default) and a tighter decision surface covering both.

---

## 0. Summary of what this record adds to prior evidence

`RT01_RT02_FAILURE_FORENSICS_REPORT.md` and `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (both 2026-10-17/18) already evidenced that `router.py` substitutes the station's **full observed demand** for `critical_load_w`. This record independently re-confirms that finding and adds one that neither document examined: **`router.py`'s `t_required_hours` default of `6.0` hours is itself ungoverned, and the only numeric value ever proposed for this role was explicitly withheld from implementation.** Both defects compound: the router is currently running on two numbers, neither of which has standing production authorization, and both happen to be more conservative (`EMERGENCY`-biased) than a properly governed input would produce. That is not a safety problem by itself, but it means the `EMERGENCY`/`NORMAL` classification the whole dispatch-routing decision rests on is not currently backed by any authorized policy for either of its two load-bearing inputs.

---

## 1. What exactly does the six-hour survivability rule require?

**Source:** `system/control/ecd.py` lines 283–291 (direct inspection):

```python
# 6. Calculate survivability margins against t_target
m_battery = t_battery - t_target
m_diesel = t_diesel - t_target

# 7. Evaluate emergency operating mode
if m_battery >= 0.0 and m_diesel >= 0.0:
    mode = OperatingMode.NORMAL
else:
    mode = OperatingMode.EMERGENCY
```

The rule is: compute `t_battery` (how long the battery alone, from its usable energy, can serve the critical-load trajectory) and `t_diesel` (how long the diesel generator alone, from remaining fuel, can serve the same trajectory), each independently, against the **same** target horizon `t_target` (= `t_required_hours`, read by `router.py` from `configs["ecd"]["t_required_hours"]`, defaulting to `6.0`). `NORMAL` requires **both** margins to be non-negative; if either is negative, the mode is `EMERGENCY`.

This is corroborated by governance, not just code: `POLARIS_EMS_SURVIVABILITY_DETECTOR_SPECIFICATION_AUDIT/SURVIVABILITY_SPECIFICATION_AUDIT.md` line 91 states the **Mathematical Requirement** explicitly: *"Directly comparing battery and fuel survivability under Human Decision E3 requires evaluating BOTH resources against the SAME required survival window T_required under the SAME critical demand trajectory. Comparing unmatched windows is mathematically invalid."* Line 106 adds Policy E3's limiting-resource rule (neither resource has permanent priority; whichever is weaker is "limiting"), which matches `ecd.py` lines 293–313 (`preserved_resource`/`limiting_resource` selection) exactly.

**Answer to the directive's Q2:** the requirement is **battery-only AND diesel-only, each independently, against the same `T_required`** — not combined/sequential endurance (e.g., "run on battery until exhausted, then diesel for the remainder"). The code and the governance document agree on this point; there is no ambiguity here, and no owner decision is needed on this specific sub-question.

---

## 2. Is `T_required` (the "six hours") itself a governed value?

**No — this is the central, previously unexamined finding of this record.**

`router.py` line 45: `t_required = float(ecd_cfg.get("t_required_hours", 6.0))`, where `ecd_cfg = configs.get("ecd", {})` (line 44). Direct inspection of every file in `system/config/` (`battery.yaml`, `diesel.yaml`, `loads.yaml`, `optimizer.yaml`, `solar_pv.yaml`, `station.yaml`) found **no `ecd.yaml` and no `t_required_hours` key anywhere**. This means `configs.get("ecd", {})` always evaluates to `{}` in every code path exercised by this repository's tests and runner, and the `6.0`-hour default is therefore **the value actually in effect in every pipeline execution**, not merely a fallback for an edge case.

The repository contains an extensive, dedicated governance track on exactly this question (`POLARIS_EMS_HD03_*` directories, ~20 sub-audits). Its findings, read directly:

- `POLARIS_EMS_HD03_T_REQUIRED_OPERATIONAL_EVIDENCE/POLARIS_EMS_HD03_T_REQUIRED_OPERATIONAL_EVIDENCE.md`: `HD03_NUMERICAL_VALUE = NOT_ESTABLISHED` for the real station. No resupply schedule, recovery timestamp, or autonomy requirement exists anywhere in the repository to derive a real `T_required`.
- `POLARIS_EMS_HD03_T_REQUIRED_OPERATIONAL_EVIDENCE/POLARIS_EMS_HD03_T_REQUIRED_DECISION_INPUT.md` Section 3, **"PROHIBITED ACTIONS"**, item 1 (verbatim): *"Human governance MUST NOT: 1. Promote H=24h or N=6h to T_required policy."*
- `POLARIS_EMS_HD03_T_REQUIRED_OPERATIONAL_EVIDENCE/POLARIS_EMS_HD03_T_REQUIRED_NUMERICAL_PROVENANCE.md` line 10: the number **6h** in this codebase has exactly one established meaning — `"EBR Interval (N) = 6h: HD-01B fixed normal-operation critical load battery buffer"`, classified `PROJECT_ENGINEERING_ASSUMPTION`, and explicitly marked **"NO (Conflates normal buffer with emergency survival)"** under the column "T_required Eligible?".
- `system/optimization/implementations/gap19_highs_native.py` line 111's own comment reads *"Governed survivability window T_REQUIRED = 6 hours (6 timesteps)"* for its EBR lookahead target — this is the legitimately-governed HD-01B `N=6h` EBR buffer, a different quantity serving a different purpose (a rolling 6-hour reserve-sizing lookahead inside the NORMAL-mode optimizer), not the ECD's emergency/normal classification threshold. The repository's own naming (reusing the token "T_REQUIRED" for both) is itself a source of the conflation this governance track explicitly warns against.
- A **formal governance closure exists** authorizing a numeric prototype value for this exact role: `POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE/POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE.md` — `PROTOTYPE_T_REQUIRED = 72 HOURS`, dated 2026-09-23 (filesystem mtime `2026-09-23 10:07:17`), i.e. **before** `router.py`'s own last modification (`2026-09-26 19:29:57`). This closure explicitly classifies `HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED` and `HD03_EXECUTION_AUTHORIZATION = NOT_GRANTED` — the 72h *value* was decided, but wiring it into code or running it was separately and explicitly withheld.

**What this means concretely:** `router.py`'s hardcoded `6.0`-hour default is not a neutral placeholder. It is numerically identical to the one value this repository's own governance track explicitly lists as prohibited from being promoted to `T_required` (HD-01B's `N=6h` EBR buffer), and it does not implement the one value that *was* formally authorized for prototype use (72h) — which in any case was authorized as a value only, with implementation/execution still not granted. There is no code path, config file, or governance record that establishes `6.0` as the intended `T_required` for the ECD's emergency classification. This is evidenced, not inferred from the proposed fix: it is a direct reading of `router.py`'s own source against `system/config/`'s contents and the HD-03 governance documents' own explicit prohibition.

---

## 3. What source is authoritative for actual critical-load demand, and what must happen if missing/stale/synthetic-only?

Re-confirmed, consistent with `RT01_RT02_FAILURE_FORENSICS_REPORT.md` and `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md`:

- **No authoritative source exists.** `EVID-02` (register): *"Real Nuolja critical-load measurement/circuit mapping"* — `EXTERNAL_EVIDENCE_REQUIRED`, blocked. No live telemetry-derived critical-load signal exists in `ForecastBundle`, `StationState`, or any config file.
- The only candidate value, `system/config/loads.yaml`'s `critical_load.baseline_power_w = 11600.0` (register **CL-01**, *"decided 2026-10-17: retain 11.6 kW, provisional/synthetic only"*), carries a **blocking scope of `research`**, not `safety_enforcement` or `production_promotion` (`POLARIS_MASTER_DECISION_REGISTER.md` line 89 / `.json` line 919 area). Using it as a **routing** input — a safety-classification decision — would extend CL-01's decided scope beyond what the owner actually authorized. This is a scope mismatch, not merely an unvalidated-value concern: the owner decided CL-01 *for research use*, and nothing in that decision reaches to "use this number to decide whether the station is in `EMERGENCY` mode."
- **What must happen when missing/stale/synthetic-only — governance answer, by direct analogy:** `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE/POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` (written for the structurally identical "missing governed input" problem on `T_required`, but its findings apply equally to critical load as another governed-but-absent EMS input) finds: (1) every other POLARIS subsystem enforces `FAIL_CLOSED` on missing/malformed input, raising explicit exceptions rather than silently substituting a placeholder (`"zero_placeholder_fallback": "FORBIDDEN_FAIL_CLOSED"`); (2) *"No existing POLARIS subsystem defaults to EMERGENCY mode upon encountering missing data"*; (3) arbitrary numeric substitution is explicitly listed among the forbidden options (Option M3, stale-value reuse, is `CONFLICTS_WITH_GOVERNANCE`; Option M4, an invented fallback, is `NOT_ESTABLISHED` and requires an explicit human decision).
- **What `router.py` actually does instead** (lines 54–59): `critical_load_w = float(current_state.last_observed_demand)`, falling back to `bundle.demand.point[0]`, falling back to a hardcoded `30000.0` floor — a three-level arbitrary numeric substitution chain, with the code's own comment admitting it ("synthetic fixture"). This is precisely the pattern the repository's own governance philosophy (as established for the structurally identical `T_required` problem) treats as forbidden, applied here to a different governed input with no corresponding closure document saying it is acceptable. Critically, **none of these three fallback values can ever be `<=0` in practice** (observed demand is always positive once dispatch has run once; the floor is `30000.0`), so **`ecd.py`'s own `INVALID_CRITICAL_LOAD` fail-closed path (line 247-248) can never be reached from `router.py`'s current call site** — the fail-closed mechanism that already exists in the protected ECD code is architecturally bypassed by the router's own upstream substitution, not absent from the design.

---

## 4. Which behavior is required by existing approved governance, and which would be a new safety-policy decision?

**Required by existing approved governance (no new decision needed to restate these):**
- ECD's battery-AND-diesel-independent-margin rule (Section 1 above) — already correctly implemented in `ecd.py`, consistent with Policy E3.
- `ecd.py`'s fail-closed structure for malformed/invalid inputs (`_fail_closed()`, `ValidityStatus` enum) — already correctly implemented, consistent with POLARIS's general fail-closed philosophy.
- HD-03's explicit prohibition on promoting `N=6h` to `T_required` (Section 2) and on inventing arbitrary numeric fallbacks for a missing governed input (Section 3) — these are **already decided governance**, and the current `router.py` code's hardcoded `6.0`-hour default and full-demand substitution chain are **not compliant with that already-decided governance**, independent of any new decision. Fixing *this* part — removing an unauthorized default/substitution that contradicts existing, already-approved governance — is arguably not even a new policy choice; it is closing a gap between decided governance and code that never implemented it.

**Would require a new safety-policy decision (not resolvable from existing governance alone):**
- **What `T_required` should actually be at runtime.** HD-03's own governance explicitly reserves this to the owner (`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`; `HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED` even for the one value — 72h — that was separately authorized as a *value*). No evidence in the repository licenses picking any specific number (not 6h, not 72h-as-implemented, not any other) without a fresh, explicit authorization to *implement* a chosen value, per the HD-03 closure's own terms.
- **What critical-load source `router.py` should use, and at what authorization scope.** Using CL-01's 11.6 kW figure for routing — even clearly labeled synthetic — would be extending a `research`-scoped decision into `safety_enforcement`/`production_promotion` scope, which `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` already correctly flags as "a reduction in conservatism... must be reviewed as a safety-relevant behavior change." This record concurs and does not relitigate that conclusion.
- **What should happen when no valid, authorized value exists for either input** — fail closed to `UNKNOWN_INVALID` (Option M1/M-A, supported by existing fail-closed precedent elsewhere in POLARIS but never implemented for this specific call site), or declare `EMERGENCY` by policy (M-B, "not currently defined in code" per the HD-03 missing-input audit), or something else. `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md`'s own Section 5 states this exact decision is still open: `EXACT_HUMAN_DECISION_REQUIRED` with four named options (M-A through M-D), none selected.

---

## 5. What specific owner decision is required before changing routing?

Two related but separable governed inputs feed the same routing decision; both need an explicit choice before `router.py` is touched. Phrased as the owner would need to answer it:

> **Decision A — `T_required` (the survivability horizon):** Should `router.py` (i) continue running on the current, ungoverned `6.0`-hour default (understood now to be the HD-01B `N=6h` EBR value, which HD-03 explicitly prohibits promoting to this role) until a real-station value is established; (ii) be authorized to implement the already-decided 72-hour **prototype-only** value (`POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE.md`), via a new, explicit `HD03_IMPLEMENTATION_AUTHORIZATION = GRANTED` decision (not yet made) strictly for prototype testing, clearly logged as such; or (iii) fail closed (`UNKNOWN_INVALID`) whenever no explicitly authorized `T_required` is configured, consistent with HD-03's own fail-closed-pattern precedent and leaving `NORMAL`/`EMERGENCY` classification entirely blocked until a real value exists?
>
> **Decision B — critical load for routing:** Should `router.py` (i) continue substituting full observed demand (today's behavior — maximally conservative, but the code's own comment calls it a placeholder, and it is why `EMERGENCY` routing is nearly unconditional); (ii) be authorized to use CL-01's 11.6 kW synthetic value for routing specifically, which requires extending CL-01's decision scope from `research` to `safety_enforcement`/`production_promotion` (a new decision, not a restatement of CL-01); or (iii) fail closed whenever no real (EVID-02) critical-load measurement exists, per the same fail-closed pattern as Decision A(iii)?

**Consequences, stated plainly, for the owner's benefit:**
- Choosing "keep current defaults" for both (A-i/B-i) is **not a neutral no-op** — it is implicitly choosing to keep running on two numbers this repository's own governance material independently flags as unauthorized for this exact purpose, which is why `EMERGENCY` routing is nearly unconditional for `demo_scenario.json`-like load levels and the ECD's own `UNKNOWN_INVALID` fail-closed branch is never reachable from this call site.
- Choosing to authorize 72h (A-ii) and/or 11.6 kW-for-routing (B-ii) would make `NORMAL` routing (and hence the intended MILP/GAP19 optimizer) reachable for many more scenarios, directly addressing most of RT-01's and the two previously-unmapped failures' root cause — but this is a genuine reduction in routing conservatism and must be evaluated and authorized as such, with the regression tests `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` Section 7 already specifies.
- Choosing fail-closed for either input (A-iii/B-iii) is the option most consistent with POLARIS's own stated fail-closed philosophy and would not reduce conservatism, but it would mean the pipeline cannot produce a `NORMAL`/`EMERGENCY` classification at all today (since neither input currently has an authorized value) — i.e., every run would report `UNKNOWN_INVALID` until an owner-authorized value for at least `T_required` exists. This has its own operational consequence (today's tests and demos would need to be re-scoped) that the owner should weigh explicitly, not discover incidentally.

**No implementation of A, B, or any variant was made or attempted by this record.** `router.py` and `ecd.py` hashes (Section 6, `N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md`) are confirmed unchanged before and after producing this record.

---

## 6. Relationship to `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md`

That proposal (2026-10-17/18) already covers Decision B in essentially the form restated here (config-sourced 11.6 kW with fail-safe fallback), and this record does not change its recommendation. This record's distinct contribution is **Decision A** — the `t_required_hours` default — which no prior pass in this remediation cycle examined, despite the repository already containing a dedicated ~20-document governance track on exactly that question. Any future governance review of the router should consider both decisions together, since both inputs feed the same `m_battery >= 0 and m_diesel >= 0` test and a fix to only one (e.g., critical load alone, leaving `T_required` at the ungoverned `6.0` default) would still leave the routing decision resting on one unauthorized number instead of two.
