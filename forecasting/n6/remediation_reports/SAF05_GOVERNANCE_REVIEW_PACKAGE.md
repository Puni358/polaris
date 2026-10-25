# SAF-05 — Formal Governance Review Package: The Four Proposed Safety Gates

**Date prepared:** 2026-10-17
**Prepared by:** this pass, on the project owner's explicit instruction ("prepare a concise governance review package").
**Status of this document:** Briefing material for the designated governance authority. **Preparing this package is not approval of the gates it describes.** All four gates named below remain `authorized=False` in `system/safety/reserve_policy_guard.py`'s `SAFETY_GATE_REGISTRY` as of this writing, and remain unauthorized after this document is published. Only the governance authority named in the register (`decision_authority: "governance authority"` for SAF-05) can change that, by a formal, dated, named-approver decision — not by this package existing, and not by the project owner's instruction to prepare it.
**Companion register entries:** `POLARIS_MASTER_DECISION_REGISTER.md`/`.json`, item `SAF-05` (see also `SAF-02`, `SAF-03`, `SAF-04`, `EVID-03`, which this package draws on).

---

## 1. What is being asked of the governance authority

A decision on whether to formally authorize (`authorized: True`), reject, or revise each of the four gates currently registered in `system/safety/reserve_policy_guard.py`'s `SAFETY_GATE_REGISTRY` (lines ~86–112). Today, every evaluation of these gates by any report-generation code produces `proposed_gate_would_pass` / `WOULD_FAIL` — descriptive, advisory output — never an authorized governance verdict, because every entry's `authorized` field is `False`. No candidate (N6 or any other) can be said to have "passed safety governance" until at least one gate is formally authorized.

This package does not ask the governance authority to approve a diesel-savings number, a replay result, or any specific candidate. It asks only: **should these four gate definitions (name, description, threshold) become the formally authorized bar**, and if so, in what form.

---

## 2. The four proposed gates, verbatim from source

| Gate key | Description (as coded) | Proposed threshold | Current `authorized` |
|---|---|---|---|
| `critical_unmet_not_worse_than_baseline` | Candidate critical unmet load must not exceed baseline (Control). | No specific numeric threshold beyond "not worse than baseline" | `False` |
| `unserved_energy_origin_failure_rate` | Candidate must not increase unserved energy in more than 5% of origins. | 5% ceiling | `False` |
| `diesel_savings_significance` | Diesel savings must exceed 2% with p < 0.01. | >2% AND p<0.01 | `False` |
| `critical_service_ratio_floor` | Critical service ratio must exceed 99.95%. | 99.95% floor | `False` |

Source: `system/safety/reserve_policy_guard.py`, `SAFETY_GATE_REGISTRY` dict, each entry carrying its own `proposed_threshold_note` stating `"AUTHORIZATION_REQUIRED: proposed ... not formally authorized"`. These are the only concrete, already-coded candidate-acceptance gates anywhere in the repository.

---

## 3. Evidence available for each gate

- **`critical_unmet_not_worse_than_baseline`:** The underlying metric (`critical_unmet_total_wh`) is correctly computed as `None`/`"UNKNOWN_NOT_VERIFIED"` when genuinely absent, and as a disclosed, conservative `FALLBACK_TO_TOTAL_UNMET_LOAD` proxy otherwise (owner-confirmed, SAF-02, Section 14). No regression on this metric's correctness is open. **However**, the "baseline" it would compare against is itself built on a `SYNTHETIC_ENGINEERING_SCENARIO` critical-load figure (EVID-02 unresolved; CL-01 decided 11.6 kW as provisional/synthetic only, Section 14 item 8) — so even a technically-correct gate evaluation would be judging unmet load against a non-station-verified demand curve.
- **`unserved_energy_origin_failure_rate` (5% ceiling):** No empirical distribution of per-origin unserved-energy-increase rates specific to this gate's framing has been computed in any pass. `DIESEL_REDUCTION_CONTROL_DESIGN.md`'s existing campaign evidence (123-origin `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024`) reports Arm B's unmet-load figures at the aggregate level, not framed as this gate's specific "exceeds baseline in >5% of origins" test.
- **`diesel_savings_significance` (>2%, p<0.01):** DSL-01's own preregistered research-acceptance criterion (p<0.05 AND BCa CI>0, no % floor) is a *different*, independently-authored standard for a *different* decision point (research-experiment acceptance, not production promotion) — traced to source in the register's Section 19.2 and reaffirmed by owner decision in Section 21.1 (this pass). They are not interchangeable evidence for each other.
- **`critical_service_ratio_floor` (99.95%):** The gate's own `proposed_threshold_note` states plainly that **no `critical_service_ratio` metric currently exists in production evaluator code** — there is nothing to evaluate this gate against today, regardless of authorization status.
- **Reserve-shortfall/solar-credit context (SAF-03/SAF-04):** EVID-03's completed offline analysis (`research/evid03_reserve_margin_analysis/`) supplies units/horizon/margin evidence relevant to interpreting any future reserve-shortfall-related gate revision, but — per the owner's explicit decision recorded this pass (Section 21.1, items 1 and 4) — is evidence, not authorization, and does not itself justify any of the four gates' thresholds.

**Net evidentiary state:** two of the four gates (`diesel_savings_significance`, `critical_service_ratio_floor`) rest on criteria or metrics that are either a different decision's criterion or simply do not exist yet in evaluator code. The other two depend on a critical-load baseline (EVID-02) that remains synthetic/unverified. No gate currently has a complete, directly-applicable evidentiary basis for formal authorization as worded.

---

## 4. Assumptions underlying each gate (stated, not re-litigated)

- All four gates assume a "baseline" comparison exists that is itself governance-approved and station-representative. Today's only candidate baseline is the 123-origin `Control_Frozen_B` campaign result, built on the synthetic critical-load figure above.
- `diesel_savings_significance` and `critical_service_ratio_floor` assume statistical/metric infrastructure (a significance test pipeline, a `critical_service_ratio` computation) that partially does not exist in production evaluator code yet.
- All four assume N6 (or any future candidate) will eventually be run through a multi-origin campaign comparable to the existing 123-origin framework. Per `DIESEL_COMPARISON_PREREQUISITE_PLAN.md` (this pass's companion report), **no such N6-integrated multi-origin harness currently exists** — this is a prerequisite independent of gate authorization itself.

---

## 5. Risks of authorizing now, vs. risks of continued non-authorization

**Risk of authorizing now:**
- Locking in thresholds (5%, 2%/p<0.01, 99.95%) that were "proposed in prior audit," not independently derived from Nuolja-specific risk tolerance, EVID-02 real critical-load data, or a completed PCEEB/EVID-03-informed reserve analysis. Section 20.1's EVID-03 finding (5th-percentile adverse-tail forecast error already exceeding `EBR_BASE_WH` by 146% and the hard-SOC floor by 223% at full horizon) suggests the existing reserve-policy assumptions implicit in these gates may be more fragile than the gates' own thresholds assume.
- Authorizing `critical_service_ratio_floor` would authorize a gate against a metric that does not yet exist in evaluator code, creating a gate that can never be truthfully evaluated until separate engineering work (out of this pass's scope) adds that metric.

**Risk of continued non-authorization:**
- No candidate (N6 or otherwise) can ever be said to have formally passed a safety-governed acceptance bar; every result remains advisory indefinitely, as it has across all five prior passes.
- Production-promotion review (SAF-05's own `unlocks_after_resolution`) stays blocked regardless of how much offline evidence accumulates elsewhere (EVID-01, EVID-02, UNC-02, a future diesel comparison), since there is no authorized bar to measure any of it against.

---

## 6. Dependencies on other register items

| Dependency | State as of this pass | Effect on SAF-05 |
|---|---|---|
| SAF-02 (critical-load labeling policy) | Decided 2026-10-17 (Section 14) — keep current conservative labeling | Satisfied; no longer blocks SAF-05. |
| EVID-03 (reserve-margin/solar-credit evidence) | `RESOLVED_WITH_EVIDENCE` 2026-10-17 (Section 20.1) | Satisfied as a named prerequisite; does not itself authorize any gate value (Section 21.1, item 1). |
| SAF-03 (reserve-shortfall ceiling) | Deferred by owner 2026-10-17 (Section 21.1, item 1) — kept unset | Still open; any future reserve-shortfall-flavored gate revision would want this settled first. |
| SAF-04 (solar-credit cap) | Deferred by owner (Section 14, reaffirmed Section 21.1 item 4) | Still open; not a blocker for these four gates specifically (none directly references a solar-credit fraction), but relevant context. |
| EVID-02 (real Nuolja critical-load measurement) | `EXTERNAL_EVIDENCE_REQUIRED`, unresolved | Not a hard blocker for *authorizing* a gate definition, but materially affects what any "baseline" comparison under these gates would mean operationally. |
| `critical_service_ratio` metric (evaluator-code gap) | Does not exist | Blocks any truthful evaluation of `critical_service_ratio_floor`, independent of its authorization status. |

---

## 7. Decisions required from the governance authority

For each of the four gates, the governance authority is asked to choose one of:

1. **Authorize as-is** (`authorized: True`, threshold unchanged).
2. **Reject** (leave `authorized: False` indefinitely, or formally retire the gate).
3. **Defer** (explicitly, with a named reason/prerequisite — distinct from today's de facto, unexplained `False`).
4. **Revise** (change the threshold or description before authorizing — e.g., informed by EVID-03's evidence for any reserve-shortfall-flavored revision, or by building the missing `critical_service_ratio` metric first for gate 4).

The governance authority is also asked to name:
- The approving authority and date, for the register's own closure test (`"At least one SAFETY_GATE_REGISTRY entry has authorized=True with a named approving authority and date"`).
- Whether authorization of any gate is contingent on the still-open SAF-03 (reserve-shortfall ceiling) or EVID-02 (real critical-load data) items, or can proceed independently.

---

## 8. What this package explicitly does not do

- It does not authorize any gate. All four remain `authorized=False` after this document exists.
- It does not propose a specific numeric revision to any threshold — that would itself be inventing a safety-relevant number, which this pass's governing boundaries forbid.
- It does not claim EVID-03's evidence, or any other evidence cited above, settles any gate's threshold question.
- It does not authorize, recommend, or imply authorization for any replay, campaign, or dispatch-evaluation execution — SAF-05's resolution is a governance-authorization question, separate from, and not a substitute for, the campaign-execution authorization `system/evaluation/replay_harness.py` independently requires (see `DIESEL_COMPARISON_PREREQUISITE_PLAN.md`).

---

**END OF GOVERNANCE REVIEW PACKAGE — PREPARED, NOT APPROVED. ALL FOUR GATES REMAIN `authorized=False`.**
