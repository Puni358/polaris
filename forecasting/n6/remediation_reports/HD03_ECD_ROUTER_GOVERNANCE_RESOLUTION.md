# POLARIS — HD-03 / ECD Router Governance Resolution: Decision-Ready Package

**Date:** 2026-10-18 — **amended 2026-10-18** (same day, second pass: the project owner reviewed Section 3 and selected Decision A = A-iii, Decision B = B-iii, and the follow-on Decision C = M-A; see new **Section 9**. This amendment is documentation-only: no code was changed, no value/evidence was newly established, no authorization beyond the decision selections themselves was granted.)
**Nature of this document:** Governance-package preparation only, per the governing directive. No routing, dispatch-policy, or `T_required` value is implemented, selected, or inferred-authorized here. `system/control/router.py`, `system/control/ecd.py`, `system/optimization/implementations/gap19_highs_native.py`, and `system/optimization/implementations/option_d.py` were read-only inspected; **none was edited.**
**Relationship to prior work:** This document independently re-verifies and consolidates `ECD_ROUTER_DECISION_RECORD.md` (2026-10-18) and `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` (2026-10-17/18) into the single decision-ready package the directive requests. It does not supersede either; it cites them and adds the explicit owner-choice/consequence/rollback structure the directive requires, plus a proposed (not applied) register amendment. **Section 9 (added 2026-10-18, second pass) records the owner's subsequent decision among the options this document presents.**

---

## 1. Governing sources, decision-register entries, current code behavior — re-verified this pass

**Verification performed this pass (exact commands, exact outcomes):**

```
sha256sum system/optimization/implementations/gap19_highs_native.py system/optimization/implementations/option_d.py \
          system/control/ecd.py system/control/router.py system/simulation/simulator.py system/runtime/runner.py
```
→ `gap19_highs_native.py = fd1afe10a60c6e9...`, `option_d.py = 15179e83e11797...`, `ecd.py = d97c680ca8f4c1c...`, `router.py = 041fc2525acf8f3...`, `simulator.py = 8c44f757058e4bd...`, `runner.py = 6d1671b6efbf6ac...` — all six identical to the values recorded in every prior pass (`N6_END_TO_END_RECOVERY_CONTINUATION_REPORT.md` Section 26.7 et al.). **No protected file changed.**

```
grep -rn "t_required_hours" system/config/   → no match (exit 1)
find . -iname "ecd.yaml" -not -path "./.venv/*"   → no result
```
→ Re-confirms `configs.get("ecd", {})` is always `{}`; `router.py` line 45's `6.0`-hour default is the value actually in effect in every execution.

Direct reads performed this pass: `system/control/router.py` lines 1–107 (full `evaluate_and_route`), `system/control/ecd.py` lines 200–333 (full `evaluate` + `_fail_closed`), `POLARIS_EMS_HD03_T_REQUIRED_DECISION_INPUT.md`, `POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE.md`, `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md`, `POLARIS_MASTER_DECISION_REGISTER.md` Sections 2–3 and 26.

**Exact citations:**

| Fact | Source (exact) |
|---|---|
| `router.py` runtime default | `system/control/router.py:45` — `t_required = float(ecd_cfg.get("t_required_hours", 6.0))` |
| No config backs this value | `system/config/` contains `battery.yaml, diesel.yaml, loads.yaml, optimizer.yaml, solar_pv.yaml, station.yaml` only; no `ecd.yaml`, no `t_required_hours` key anywhere (re-confirmed by `grep`/`find` above) |
| Critical-load substitution | `system/control/router.py:54-59` — `critical_load_w = float(current_state.last_observed_demand)` → falls back to `bundle.demand.point[0]` → falls back to `30000.0` |
| ECD's independent-margin rule | `system/control/ecd.py:283-291` — `m_battery = t_battery - t_target; m_diesel = t_diesel - t_target`; `NORMAL` iff both `>= 0.0` |
| ECD fail-closed structure | `system/control/ecd.py:220-266` (validation checks) and `:329-333` (`_fail_closed`, sets `OperatingMode.UNKNOWN_INVALID`) |
| Router's pass-through of ECD's three-way result | `system/control/router.py:99-105` |
| HD-03 prohibition on promoting 6h to `T_required` | `POLARIS_EMS_HD03_T_REQUIRED_OPERATIONAL_EVIDENCE/POLARIS_EMS_HD03_T_REQUIRED_DECISION_INPUT.md` §3 item 1: *"Human governance MUST NOT: 1. Promote H=24h or N=6h to T_required policy."* |
| 72h prototype value decided, implementation withheld | `POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE/POLARIS_EMS_HD03_PROTOTYPE_T_REQUIRED_72H_CLOSURE.md` §5: `HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED`, `HD03_EXECUTION_AUTHORIZATION = NOT_GRANTED`, `HD03_DEPLOYMENT_T_REQUIRED = NOT_AUTHORIZED` |
| Missing-input policy still open | `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE/POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` §5: `EXACT_HUMAN_DECISION_REQUIRED` among M-A/M-B/M-C/M-D, none selected |
| Survivability math requirement | `POLARIS_EMS_SURVIVABILITY_DETECTOR_SPECIFICATION_AUDIT/SURVIVABILITY_SPECIFICATION_AUDIT.md` line 91 (battery-only AND diesel-only, independently, against the same `T_required`) |
| CL-01 (11.6 kW) scope | `POLARIS_MASTER_DECISION_REGISTER.md` line 89 / `.json` `items[id=CL-01]` — decided 2026-10-17, `blocking_scope: "research"` |
| Prior narrative register note (no tracked ID yet) | `POLARIS_MASTER_DECISION_REGISTER.md` §26.1, §26.6 — records the finding in prose but assigns it to no canonical register ID (see §5 of this document, which proposes one) |

**Distinguishing approved decision / implementation authorization / execution authorization (directive's explicit requirement):**

| Value | Decided? | Implementation authorized? | Execution authorized? |
|---|---|---|---|
| `N=6h` (HD-01B EBR buffer) | Yes — as the *normal-operation* buffer, a different quantity | N/A for this role — **explicitly prohibited** from being promoted to `T_required` | N/A |
| `72h` (HD-03 prototype) | Yes, `PROTOTYPE_T_REQUIRED = 72 HOURS`, dated 2026-09-23 | **NOT_GRANTED** | **NOT_GRANTED** |
| Real-station `T_required` | **NOT_ESTABLISHED** (no resupply schedule, recovery window, or logistics contract exists anywhere in the repository) | N/A (no value to implement) | N/A |
| 11.6 kW (CL-01) *as a design value* | Yes, decided 2026-10-17, scope `research` | N/A (not code) | N/A |
| 11.6 kW *as a routing input* | **Not decided** — this is a distinct, unaddressed scope-extension question | Not authorized | Not authorized |

No prior pass's documentation licenses treating "a value was decided" as "implementation is authorized," or "implementation was authorized" as "execution is authorized." All three are separate gates in this repository's own governance vocabulary, and for every numeric candidate examined, at least one gate is open.

---

## 2. Reconciling the 6h prohibition with the current 6h runtime default

The prohibition (`POLARIS_EMS_HD03_T_REQUIRED_DECISION_INPUT.md` §3 item 1) and the runtime default (`router.py:45`) are not in tension by coincidence — they are about the **same number reused for two different purposes** that the repository's own naming conflates. `N=6h` is HD-01B's normal-operation critical-load battery buffer (a reserve-sizing lookahead inside the NORMAL-mode optimizer — see `gap19_highs_native.py:111`'s own comment, a legitimately governed quantity for *that* purpose). `router.py:45`'s `6.0` is not sourced from HD-01B at all; it is a bare Python default with no config backing, that happens to be numerically identical. Nothing in the repository establishes that `router.py`'s author intended to invoke HD-01B's governed value — the identity is either an unexamined coincidence or an implicit (and explicitly prohibited) promotion. Either way, **the 72-hour prototype value is not implementation-authorized**, and this document does not treat its existence as licensing its use: `HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED` is dispositive on its own terms, independent of whether 6h or 72h would be "better."

---

## 3. Owner decision surface — presented separately, per the directive

### Decision A — `T_required` (the ECD survivability horizon)

| Option | Authorization scope needed | Safety consequence | Effect on NORMAL | Effect on EMERGENCY | Effect on UNKNOWN_INVALID | Required evidence | Focused tests | Rollback |
|---|---|---|---|---|---|---|---|---|
| **A-i: Keep the ungoverned 6.0h default** | None — this is the status quo, but it is a *continuation* of running on a number HD-03 flags as ineligible for this role, not a neutral no-op | Unchanged from today: battery/diesel margins against a real station's full demand are negative almost everywhere, so `EMERGENCY` is near-unconditional | Rarely reachable for realistic demand levels | Nearly unconditional for `demo_scenario.json`-class loads | Unreachable in practice (see §4) | None — no new evidence needed to *continue* current behavior | `system/tests/test_offline_runtime.py::TestPolarisD3ClosedLoopRuntime` (5 tests, currently failing for other reasons — unaffected either way) | N/A, nothing changes |
| **A-ii: Authorize the 72h prototype value for prototype testing only** | A new, explicit `HD03_IMPLEMENTATION_AUTHORIZATION = GRANTED` decision, scoped strictly to prototype/offline testing, logged as such — **not yet made** | Makes `EMERGENCY` classification *less* likely to trigger (72h is a larger, harder-to-clear bar than 6h, so margins must be *less* negative, which — since margin = endurance − target — actually makes NORMAL *harder* to reach, not easier; see note below) | Becomes effectively unreachable for most battery/diesel sizings (a 72h-survivability bar is a demanding target) | Becomes the default outcome for almost all realistic sizings | Unreachable in practice (same substitution-chain floor applies) | A dated authorization record naming the 72h closure as the implementation source, explicitly scoped prototype-only, with a rollback trigger | New regression test asserting `t_required_hours == 72.0` is read from an explicit config key (not a code literal) and that `NORMAL`/`EMERGENCY` boundary tests reflect the new target | Remove the `ecd.yaml`/config key; router reverts to the 6.0h code default |
| **A-iii: Fail closed (`UNKNOWN_INVALID`) until a real-station value is explicitly authorized** | Consistent with existing HD-03 fail-closed precedent (`POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` Option M1, `SUPPORTED_BY_EXISTING_GOVERNANCE`); requires only a routing-policy decision, no numeric authorization | Most conservative with respect to *honesty of classification* (the system stops claiming a `NORMAL`/`EMERGENCY` verdict it cannot actually ground), but **operationally** every run becomes `UNKNOWN_INVALID` until a real value exists | Unreachable (blocked upstream of the margin test) | Unreachable (blocked upstream of the margin test) | Becomes the only reachable outcome | None beyond the policy decision itself | New test asserting `router.evaluate_and_route()` returns `route == "UNKNOWN_INVALID"` when no `ecd.t_required_hours` config key is present | Re-enable the current default to restore A-i behavior |

**Note on A-ii's counterintuitive direction:** a *larger* `T_required` is a *harder* survivability bar to clear, not an easier one — so authorizing 72h does not, by itself, "fix" the near-unconditional-`EMERGENCY` problem; it would need to be paired with Decision B's resolution (a smaller, authorized critical-load figure) to free the optimizer. This is stated plainly because `ECD_ROUTER_DECISION_RECORD.md` §5 frames 72h-authorization as "mak[ing] NORMAL routing... reachable for many more scenarios" when combined with Decision B — that combination, not 72h alone, is what changes reachability; this document is explicit that the two decisions interact and neither alone determines the outcome.

### Decision B — critical-load source for routing

| Option | Authorization scope needed | Safety consequence | Effect on NORMAL | Effect on EMERGENCY | Effect on UNKNOWN_INVALID | Required evidence | Focused tests | Rollback |
|---|---|---|---|---|---|---|---|---|
| **B-i: Keep full-observed-demand substitution (status quo)** | None | Maximally conservative by accident, not by design; the code's own comment calls it a "synthetic fixture" | Rarely reachable | Nearly unconditional | Unreachable (substitution chain floors at `30000.0`, never `<=0`) | None | Same as A-i | N/A |
| **B-ii: Authorize CL-01's 11.6 kW value for routing use** | A **new** decision extending CL-01's `blocking_scope` from `research` to `safety_enforcement`/`production_promotion` — CL-01's existing decision record does not reach this use, per its own recorded scope | Genuine reduction in routing conservatism — must be reviewed and authorized as a safety-relevant change, not treated as already covered by CL-01 | Becomes reachable for realistic demand levels | No longer near-unconditional | Unreachable (11.6 kW is always `>0`) | `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` Section 7's regression tests, run and passing, plus an explicit scope-extension authorization record | `ROUTER_CRITICAL_LOAD_FIX_PROPOSAL.md` §5-7 proposed tests (config-sourced value, fail-safe fallback to B-i when absent) | Remove/ignore the `loads.critical_load.baseline_power_w` read in `router.py`; reverts to B-i |
| **B-iii: Fail closed when no real (EVID-02) measurement exists** | Consistent with HD-03's fail-closed precedent, applied by analogy to this input | Most conservative with respect to classification honesty; operationally `UNKNOWN_INVALID` until EVID-02 (real Nuolja measurement) is satisfied | Unreachable | Unreachable | Becomes the only reachable outcome (absent EVID-02) | EVID-02 itself (currently `EXTERNAL_EVIDENCE_REQUIRED`, blocked) | New test asserting `UNKNOWN_INVALID` when no live/validated critical-load signal exists | Re-enable B-i |

---

## 4. Invalid/unavailable ECD input vs. a valid `EMERGENCY` classification — explicit distinction (not invented here)

These are structurally different outcomes in `ecd.py`'s own design, and the directive's instruction not to invent the `UNKNOWN_INVALID` system response is respected by describing — not resolving — the gap:

- **A valid `EMERGENCY` classification** (`ecd.py:283-291`) means the ECD successfully validated every input (horizon, critical load, telemetry, config) and then computed that `m_battery < 0.0` or `m_diesel < 0.0` — a *grounded* finding that the station cannot sustain the target horizon on battery-alone or diesel-alone. This is a meaningful safety signal when its inputs are authorized.
- **`UNKNOWN_INVALID`** (`ecd.py:329-333`, `_fail_closed`) means the ECD could *not* evaluate survivability at all — the horizon input was missing/malformed/unauthenticated/unauthorized/expired, the critical load was non-positive/NaN/infinite, telemetry was out of range, or config parameters were invalid (`ecd.py:220-266`). This says nothing about whether the station is actually safe; it is a refusal to classify.
- **These are not interchangeable**, and `router.py:99-105` already respects the distinction mechanically (it passes through `OperatingMode.UNKNOWN_INVALID` as its own `"UNKNOWN_INVALID"` route, never remapping it to `"EMERGENCY"`).
- **The gap this document does not fill:** *what the rest of the EMS/dispatch system should do, operationally, when it receives route `"UNKNOWN_INVALID"`* is not specified anywhere in the repository — `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` §5 names this exact open question (`EXACT_HUMAN_DECISION_REQUIRED`, options M-A through M-D, none selected) and this document does not select one. Today the question is moot in practice only because `router.py`'s current substitution chain for both inputs (A-i's `6.0` default is always finite/positive; B-i's chain floors at `30000.0`) means `UNKNOWN_INVALID` is **architecturally unreachable from this call site** — not because the question has been answered, but because neither input is ever allowed to go invalid upstream. Any move toward A-iii or B-iii would make `UNKNOWN_INVALID` reachable for the first time in practice, which is exactly why the operational response to it needs to be decided *before*, not after, adopting a fail-closed option.

---

## 5. Smallest governance-compliant next step (recommended; not selected on the owner's behalf)

The smallest step that does not select a numerical value, does not extend CL-01's scope, and does not infer authorization from existing proposals is: **the owner formally answers Decision A and Decision B above** (six total options, independently), and — only once at least one fail-closed option (A-iii or B-iii) is chosen for either input — **separately** decides the `UNKNOWN_INVALID` operational response (`POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` M-A/M-B/M-C/M-D). Until then, the only register-level action available to a documentation pass is to give this decision surface a tracked canonical ID (it currently exists only as prose in `POLARIS_MASTER_DECISION_REGISTER.md` §26.1/§26.6, under no ID) — proposed in Section 6 below, as a **tracking entry only**, with no option pre-selected.

---

## 6. Proposed register amendment (diff — not applied to close anything; owner selection still required)

**Proposed new canonical item `ECD-01`**, added to `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (version `1.9.0` → `1.9.1`). This tracks the governance gap described above; it does **not** record an owner decision, does **not** select a value, and does **not** extend CL-01's scope — those remain open, exactly as before this amendment.

```diff
--- POLARIS_MASTER_DECISION_REGISTER.md (table, after EVID-03 row)
+++ POLARIS_MASTER_DECISION_REGISTER.md (table, after EVID-03 row)
+ | ECD-01 | Resolve ECD/router `T_required` source and critical-load-for-routing authorization (HD-03 governance gap) | ECD / Router | A | **ready_for_decision** (§27) — two linked but separable owner choices (T_required: keep 6h / authorize 72h-prototype / fail-closed; critical-load-for-routing: keep full-demand / extend CL-01 to safety_enforcement scope / fail-closed), none selected | safety_enforcement |
```

```diff
--- POLARIS_MASTER_DECISION_REGISTER.json (items[], appended)
+++ POLARIS_MASTER_DECISION_REGISTER.json (items[], appended)
+ {
+   "id": "ECD-01",
+   "title": "Resolve ECD/router T_required source and critical-load-for-routing authorization (HD-03 governance gap)",
+   "workstream": "ECD / Router",
+   "item_type": "A",
+   "current_state": "ready_for_decision",
+   "exact_question": "See HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md Section 3, Decisions A and B (six options total, two linked but separable decisions).",
+   "blocking_scope": "safety_enforcement",
+   "decision_authority": "project owner",
+   "evidence_and_provenance": "ECD_ROUTER_DECISION_RECORD.md; HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md; POLARIS_EMS_HD03_* governance track (~20 documents); SURVIVABILITY_SPECIFICATION_AUDIT.md.",
+   "dependencies": ["CL-01 (critical-load design value; a scope extension of CL-01, not a restatement of it)"],
+   "owner_decision_record": null,
+   "note": "Tracking entry only. No value, implementation, or execution authorization is recorded by this entry's creation."
+ }
```

Full narrative detail (new Section 27) and the corresponding `headline_counts` arithmetic update (`total_distinct_items: 33 → 34`, `owner_decisions_typeA: 7 → 8`, `ready_for_decision_now: 5 → 6`, `blocking_scope_tally.safety_enforcement: 5 → 6`) are applied directly to `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` by this pass (both root and `N6_REMEDIATION_REPORTS/` mirrors), since adding a tracking entry for an already-evidenced gap is itself evidence-justified bookkeeping, not a decision on the owner's behalf. **No `current_state` other than this new item's was changed; no existing item's `owner_decision_record` was touched.**

---

## 7. Independent, already-authorized engineering work considered for this pass

Checked for qualifying work with zero dependency on Decisions A/B and quick/focused scope: `SAF-08` (HiGHS timeout-vs-infeasibility ambiguity) and RT-01's remaining `option_d.py` defects both require editing `system/optimization/implementations/gap19_highs_native.py` or `option_d.py` — both `PROTECTED_FILES` (`system/orchestration/manifest.py:10-17`), both out of scope for this pass's strict boundaries regardless of authorization status. `SAF-06` (runner/worker control-flow change) remains `BLOCKED_BY_AUTHORIZATION` (depends on SAF-01, decided "defer"). No item was found that is simultaneously independent of Decisions A/B, already fully authorized, and editable without touching a protected file. **No independent engineering work was performed this pass.**

---

## 8. Actions that remain blocked

- Any edit to `router.py` implementing A-i/ii/iii or B-i/ii/iii — blocked pending explicit owner selection of both decisions.
- Any numeric `T_required` value for the real station — blocked, `HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`, no resupply/recovery/logistics evidence exists.
- 72h prototype implementation — blocked, `HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED`, `HD03_EXECUTION_AUTHORIZATION = NOT_GRANTED`.
- CL-01's 11.6 kW value used for routing — blocked, scope extension not authorized.
- The `UNKNOWN_INVALID` operational response (M-A/B/C/D) — blocked, `EXACT_HUMAN_DECISION_REQUIRED`, not addressed by this pass per the directive's explicit instruction not to invent it.
- EVID-02 (real Nuolja critical-load measurement) and EVID-01 (live arrival-time logging) — both `EXTERNAL_EVIDENCE_REQUIRED`, unchanged.
- SAF-06, SAF-08, RT-01's remaining `option_d.py` mechanisms — blocked on protected-file governance review windows, unrelated to this pass's scope.
- `winner: null`, the sealed 2025 blind partition, all 4 `SAFETY_GATE_REGISTRY` entries (`authorized: False`), and the campaign lock (`replay_harness.py`'s `CampaignExecutionNotAuthorizedError`) — all re-confirmed unchanged, none touched, none to be touched by this pass.

**This governance issue is NOT resolved.** No owner selection among Decision A's three options or Decision B's three options has been made, and no implementation/execution authorization record has been created. This document is the decision-ready package the directive requested — the decision itself remains the owner's.

---

**Files produced this pass:** this file (repo root) + mirror `N6_REMEDIATION_REPORTS/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md`; `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` amendment (v1.9.0 → v1.9.1, new tracking item `ECD-01` only) + mirrors. No other file was created or edited. `router.py`, `ecd.py`, `gap19_highs_native.py`, `option_d.py` hashes independently re-verified unchanged (Section 1). Nothing staged, committed, or pushed.

---

## 9. Owner decisions recorded — 2026-10-18 (second pass, documentation-only)

The project owner reviewed Section 3's Decision A/Decision B option tables and Section 4's distinction between `UNKNOWN_INVALID` and a valid `EMERGENCY` classification, together with `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE/POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` Section 5's M-A/B/C/D options, and made three explicit, recorded selections. This section records those selections; it does not implement them, and nothing in Sections 1–8 above is retracted or superseded — the option tables, the architectural-unreachability analysis, and the "actions that remain blocked" list all stand exactly as written, except that three of the previously-open rows are now the owner's selected options rather than open options.

**9.1 Decision A (`T_required`) — A-iii selected.** "When no valid, authorized T_required is available, fail closed with UNKNOWN_INVALID." Per Section 3's own A-iii row: this is consistent with existing HD-03 fail-closed precedent (`POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` Option M1/M-A, `SUPPORTED_BY_EXISTING_GOVERNANCE`) and requires only a routing-policy decision, no numeric authorization. The owner's selection explicitly does **not**: (a) silently continue relying on the ungoverned 6.0h default (A-i, not selected); (b) promote the 72-hour prototype value into implementation or operational use (A-ii, not selected — `HD03_IMPLEMENTATION_AUTHORIZATION` and `HD03_EXECUTION_AUTHORIZATION` remain `NOT_GRANTED` exactly as Section 1's table already stated); (c) establish a real-station numerical value (remains `NOT_ESTABLISHED`, unchanged — no resupply/recovery/logistics evidence exists anywhere in the repository, per Section 1). The detector continues to consume an authorized, resolved value only (`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`); it is not authorized to invent or self-select one.

**9.2 Decision B (critical-load routing source) — B-iii selected.** "Fail closed when authoritative real-station critical-load evidence is unavailable." Per Section 3's own B-iii row: consistent with HD-03's fail-closed precedent applied by analogy to this input; operationally `UNKNOWN_INVALID` until `EVID-02` (real Nuolja measurement) is satisfied. The owner's selection explicitly does **not**: (a) treat observed total demand as authoritative critical-load demand (B-i, not selected); (b) treat the hardcoded 30,000 W fallback as an authoritative source (B-i's substitution chain, not selected as a design); (c) extend `CL-01`'s `blocking_scope` from `research` to `safety_enforcement`/`production_promotion` (B-ii, not selected — `CL-01`'s existing decision record is unchanged and does not reach this use, exactly as Section 3's B-ii row already noted). `EVID-02` remains `EXTERNAL_EVIDENCE_REQUIRED`, unsatisfied, until genuine station evidence and its provenance are validated.

**9.3 Decision C — the follow-on `UNKNOWN_INVALID` operational-response decision — M-A selected.** Section 5's "smallest governance-compliant next step" noted this follow-on decision becomes live "only once at least one fail-closed option (A-iii or B-iii) is chosen for either input" — both were chosen (9.1, 9.2), so this decision is now in scope. Per `POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE/POLARIS_EMS_HD03_MISSING_T_REQUIRED_GOVERNANCE.md` Section 5 (options labeled M-A/M-B/M-C/M-D there; the same four options are labeled M1/M2/M3/M4 in that same document's Sections 3–4 policy table — one option set, two label conventions used internally by that source document): **M-A ("Fail Closed / Block Decision") selected.** This is the option that document's own Section 3 table marks `SUPPORTED_BY_EXISTING_GOVERNANCE`. The selection means: the ECD/router must emit an explicit invalid-input fault/status; it must block a survivability classification that cannot be supported by valid governed inputs; `UNKNOWN_INVALID` must **not** be automatically reinterpreted as `EMERGENCY`; stale last-known-good values must **not** be used absent a separately governed freshness policy (M-C/M3 was not selected, and is independently classified `CONFLICTS_WITH_GOVERNANCE` by that document's own Section 3); no numerical fallback is to be invented (M-D/M4 was not selected). **M-A, by itself, specifies the missing-input decision behavior only.** It does not authorize a particular dispatch fallback, worker-termination behavior, automatic safety halt, or any other production control-flow change — that remains a separate, not-yet-written specification (Section 9.5, prerequisite 3).

**9.4 What remains exactly as before this section — restated for clarity.** Section 1's authorization-gate table, Section 4's `UNKNOWN_INVALID`-vs-`EMERGENCY` distinction, and Section 8's "actions that remain blocked" list are **not** superseded by this section except where explicitly noted above (A-iii/B-iii/M-A are no longer "open options" — they are the owner's recorded selections). In particular, still unchanged: `router.py`'s and `ecd.py`'s hashes (neither file was edited to produce this section — a documentation-only amendment requires no re-verification of files it does not touch); `winner: null`; the sealed 2025 blind partition (not accessed); all 4 `SAFETY_GATE_REGISTRY` entries (`authorized: False`); the campaign-execution guard (unconditional). The governance issue described by this document is **still not operationally resolved** — a decision has been recorded, but `router.py`/`ecd.py` do not yet implement it, and the orchestration/dispatch-level response to `UNKNOWN_INVALID` (Section 9.5, prerequisite 3) has not been specified.

**9.5 Remaining prerequisites, explicitly retained (none satisfied by recording these decisions):**

1. Authorized `T_required` — real-station operational evidence, numerical provenance, and a separate governed value/override decision (`HD03_NUMERICAL_VALUE` remains `NOT_ESTABLISHED`).
2. Critical-load source — genuine station measurement, provenance, and validation (`EVID-02`), plus explicit separate authorization for operational routing use.
3. Safe response to invalid inputs at the orchestration/dispatch level — a separate, reviewed specification for what the rest of the EMS/dispatch system does upon receiving route/status `UNKNOWN_INVALID`; not written here, must not be invented.
4. Implementation authorization — a separate, explicit scope decision authorizing any edit to `router.py`/`ecd.py` (both `PROTECTED_FILES`) to implement A-iii/B-iii/M-A in code.
5. Verification and deployment — focused regression tests (Section 3's per-option test columns), review, and a separate deployment authorization.
6. Campaign/replay authorization — remains locked (`replay_harness.py`'s `CampaignExecutionNotAuthorizedError` guard, unconditional) pending these independent prerequisites.
7. `EVID-01`/`EVID-02` — both retain `EXTERNAL_EVIDENCE_REQUIRED` status, unchanged.

**Files changed by this amendment (exact paths, repo-relative):** this file (new Section 9 appended, repo root) + mirror `N6_REMEDIATION_REPORTS/HD03_ECD_ROUTER_GOVERNANCE_RESOLUTION.md`; `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (v1.9.1 → v1.9.2, `ECD-01` → `decided`) + mirrors; new companion report `ECD01_OWNER_DECISIONS_RECORDED_REPORT.md` (repo root) + mirror. `router.py`, `ecd.py`, `gap19_highs_native.py`, `option_d.py` were not opened for writing by this amendment. Nothing staged, committed, or pushed.

**AMENDMENT COMPLETE — DECISION A = A-III, DECISION B = B-III, DECISION C = M-A RECORDED AS THE PROJECT OWNER'S SELECTED OPTIONS; IMPLEMENTATION AUTHORIZATION, EXECUTION AUTHORIZATION, REAL-STATION T_REQUIRED VALUE, AND REAL CRITICAL-LOAD EVIDENCE ALL EXPLICITLY REMAIN NOT GRANTED/NOT_ESTABLISHED/UNAVAILABLE; SEVEN PREREQUISITES EXPLICITLY RETAINED AS OPEN; NO CODE CHANGED; NO PROTECTED/FROZEN FILE TOUCHED; NOTHING STAGED, COMMITTED, OR PUSHED**
