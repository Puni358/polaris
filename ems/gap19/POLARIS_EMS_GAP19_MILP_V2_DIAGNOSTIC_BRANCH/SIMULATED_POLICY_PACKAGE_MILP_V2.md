# Simulated Policy Package — MILP v2 Research Track

**Role**: `SIMULATED_POLAR_STATION_MANAGER` — a role-played research stand-in. **No decision
in this document carries real governance, stakeholder, or organizational authority.** Real
station/vendor data and real named approvers remain unavailable; nothing here changes that.
No code, config, or model is modified. No MILP experiment is run. GAP19 remains frozen as
the control. Nothing in this package overwrites, amends, or supersedes any real governance
document — all of those remain exactly as previously audited.

---

## SIMULATED POLICY PACKAGE

### 1. Critical-service infeasibility fallback

- **Decision**: When Stage 1 (zero unmet critical load) is infeasible under the current
  cycle's forecast/physical constraints, the EMS treats this as an Emergency condition and
  routes to the existing, already-implemented `OptionDFallbackSolver` path. Critical load
  may be shed only as an absolute last resort, and every such event is logged (timestamp,
  duration, energy magnitude) for mandatory post-event review.
- **Exact assumption/value selected**: reuse the *existing, already-coded* OptionD dispatch
  logic as the "separately defined emergency policy" that D04 says must exist but never
  specifies.
- **Why defensible**: D02 (last resort shedding), D04 (mandatory logging), and D06
  (lexicographic fallback during infeasibility, not a soft penalty) are already
  `HUMAN_SELECTED_POLICY`. OptionD already exists in the codebase and is already the
  router's EMERGENCY-route target — this assumption invents no new mechanism, it only
  labels the existing one as fulfilling D04's reference to a separate policy.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION`.
- **Real-world evidence needed to replace it**: an explicit stakeholder-authored emergency
  reliability policy (exact shedding sequence, review-trigger thresholds) and engineering
  validation that OptionD's actual behavior satisfies it.
- **Conflicts with authorized policy?** No — consistent with D02/D04/D06.

### 2. Emergency Mode entry and policy mapping

- **Decision**: Emergency Mode entry is governed by the EMS's existing, already-coded
  `EMSControlRouter.evaluate_and_route` logic (ECD survivability assessment against the
  governance-authorized `T_REQUIRED = 6h` horizon).
- **Exact assumption/value selected**: treat the *existing router code's* trigger logic,
  evaluated against the one value already marked `GOVERNANCE_AUTHORIZED`/`ESTABLISHED` in
  this entire space ($T_{\text{REQUIRED}}=6\text{h}$), as the provisional "mapping."
- **Why defensible**: this is the only concrete, already-implemented trigger mechanism in
  the repository, built on the single number that is genuinely authorized rather than
  provisional.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION` (the *designation* of this code as the governed
  mapping is simulated; the code and the 6h value it uses are real/authorized facts).
- **Real-world evidence needed to replace it**: formal stakeholder/technical review and
  explicit authorization of the router's trigger logic as the governed Emergency Mode
  mapping (or a different, newly specified one).
- **Conflicts with authorized policy?** No.

### 3. 3-tier load structure

- **Decision**: For this research track, the 3-tier structure (Critical / Essential-Flexible
  / Interruptible-Noncritical) governs, and `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md`
  v2.5.0's conflicting `LOAD_TIER_COUNT: 5` is treated as a non-conforming draft defect, not
  a second authorization.
- **Exact assumption/value selected**: 3 tiers.
- **Why defensible**: this is not actually a new assumption — D01 already authorizes 3
  tiers, and v2.5.0 itself names the 3-tier document as its own policy input. This decision
  simply applies the documents' own already-stated hierarchy; nothing is invented.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION` only in the narrow sense that *formally
  correcting* v2.5.0's text still requires a real governance action — the underlying content
  decision is already real, authorized policy, not simulated.
- **Real-world evidence needed to replace it**: formal amendment of v2.5.0 by its real
  governance owners (administrative, not a new policy question).
- **Conflicts with authorized policy?** No — this *enforces* authorized policy (D01) against
  an unauthorized draft figure.

### 4. Terminal-reserve physical unit (DEC-TR-03)

- **Decision**: Watt-hours (Wh).
- **Exact assumption/value selected**: Wh.
- **Why defensible**: `StationState.terminal_target_wh_override` and GAP19's own
  `config["terminal_target_wh"]` input are already typed in Wh throughout the existing,
  unmodified codebase — this is the only unit the existing code can accept without a code
  change, which is explicitly out of scope.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION`.
- **Real-world evidence needed to replace it**: an explicit stakeholder decision on
  DEC-TR-03 (which could, in principle, select a different unit, requiring a code change).
- **Conflicts with authorized policy?** No — DEC-TR-03 is open; no document specifies a
  different unit.

### 5. Terminal-reserve numerical policy/value (DEC-RES-03)

- **Decision**: Reuse, unchanged, the exact R1/R2-frozen formula:
  `terminal_target_wh = 40,000 Wh (floor) + max(0, Σ_{k=19..24}(demand[k] − renewables[k])·1h) × 1.10`.
- **Exact assumption/value selected**: as above — floor = 20% technical minimum SOC
  (`CURRENT_IMPLEMENTATION_FACT`, `battery.yaml`); look-ahead = 6h
  (`GOVERNANCE_AUTHORIZED`, $T_{\text{REQUIRED}}$); margin = +10% (borrowed from the
  pre-existing, explicitly unauthorized advisory figure NC-07, not newly invented).
- **Why defensible**: every component traces to an existing document or code fact (see
  `RESEARCH_EXCEPTION_DECISION_RECORD.md`); no number is fabricated from nothing. Re-using
  the *same* formula (rather than drafting a new one) also avoids introducing a second,
  competing unauthorized assumption into the research record.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION` (unchanged from R1/R2).
- **Real-world evidence needed to replace it**: resolution of DEC-RES-03 itself, which per
  tension T-02 requires SD-07/SD-08 station data first.
- **Conflicts with authorized policy?** No new conflict beyond what R1/R2 already
  disclosed — still explicitly `NOT_STAKEHOLDER_AUTHORIZED`, but consistent with the
  already-decided *structure* (D11/D12: dynamic + floor).

### 6. Battery assumptions where SD-07/SD-08 are unavailable

- **Decision**: (a) Use the existing, frozen `battery.yaml` technical minimum SOC (20%) as
  the provisional stand-in for SD-07 (vendor-confirmed minimum), explicitly flagged as
  *prototype*, not vendor-confirmed. (b) Do not introduce any degradation-vs-depth-of-
  discharge model for this research track — GAP19 does not currently read `battery.yaml`'s
  `deg_penalty_per_wh` field at all (confirmed by code inspection), so the *current* MILP
  scope does not depend on SD-08; SD-08 is treated as blocking only a *future*,
  degradation-aware v2 feature, not this track's baseline scope.
- **Exact assumption/value selected**: 20% SOC floor (unchanged, frozen,
  `CURRENT_IMPLEMENTATION_FACT`); zero explicit degradation modeling.
- **Why defensible**: using the already-frozen config value (rather than guessing a
  "corrected" vendor number) avoids inventing station-specific data; deferring degradation
  modeling is defensible because the current, unmodified GAP19 control doesn't model it
  either — a v2 that also doesn't model it is not a regression relative to the frozen
  control.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION`.
- **Real-world evidence needed to replace it**: SD-07 (vendor datasheet or measurement) and,
  if a future v2 scope adds degradation modeling, SD-08 (degradation curves).
- **Conflicts with authorized policy?** No — SD-07/SD-08 remain `NOT_ESTABLISHED`; this
  decision does not claim otherwise, it only substitutes an already-frozen prototype number
  for research continuity.

### 7. Simulated D16 approval chain/roles — explicitly fictional

- **Decision**: For this research track only, three **fictional** placeholder roles are
  named, carrying **no real authority whatsoever**:
  - `SIMULATED_TECHNICAL_VALIDATOR` (fictional)
  - `SIMULATED_MISSION_OPS_REVIEWER` (fictional)
  - `SIMULATED_FINAL_APPROVER` (fictional)
  These three fictional roles "review" and "approve" *this simulated package only* — not
  any real governance document, not v2.5.0, not GAP19.
- **Exact assumption/value selected**: the three role labels above, with no named real
  person behind any of them.
- **Why defensible**: D16 authorizes the three-tier *structure*; naming placeholder research
  roles to exercise that structure internally (for this document's own self-consistency)
  does not claim to satisfy SD-13, and is clearly labeled as fictional throughout.
- **Label**: `SIMULATED_RESEARCH_ASSUMPTION` — more precisely, a **fictional research
  construct**, not an evidentiary claim at all.
- **Real-world evidence needed to replace it**: actual named individuals appointed by the
  station's real organizational authority (SD-13) — unresolved and untouched by this
  exercise.
- **Conflicts with authorized policy?** No — it does not alter, satisfy, or substitute for
  SD-13; it must never be cited as doing so.

---

## AUDIT FINDINGS

| # | Decision | Classification | Rationale |
|---|---|---|---|
| 1 | Infeasibility fallback → existing OptionD | **B** (reasonable research assumption, bordering A) | Reuses already-decided structural policy (D02/D04/D06) and already-existing code; invents no new mechanism, but the specific "last-resort sequencing" detail is still unspecified. |
| 2 | Emergency Mode entry → existing router + 6h | **A** (supported by existing evidence) | Adopts only already-authorized ($T_{\text{REQUIRED}}=6h$) and already-implemented (router code) facts; nothing new is assumed. |
| 3 | 3-tier structure | **A** (supported by existing evidence) | Not actually a new assumption — directly re-affirms D01 against a non-conforming draft figure. |
| 4 | Terminal-reserve unit = Wh | **B** (reasonable research assumption) | Matches existing code convention; not derivable from any governed decision, since DEC-TR-03 is open. |
| 5 | Terminal-reserve formula/value | **C** (weakly supported / requires real data) | Floor and look-ahead are grounded; the combination formula and the 10% margin are research constructs, explicitly not stakeholder-authorized, gated on SD-07/SD-08 for any real numeric authorization. |
| 6 | Battery floor=20%, no degradation modeling | **C** (weakly supported / requires real data) | 20% is a real frozen prototype value, not a vendor-confirmed one; deferring degradation modeling is defensible only as "no regression vs. frozen control," not as a technical validation. |
| 7 | Fictional D16 roles | **Not applicable to A–E** (explicitly fictional construct) | Carries zero evidentiary weight by design; included only as a clearly-labeled placeholder, never to be read as satisfying SD-13. |

**No item was classified D (conflicts with authorized governance).** **No item was
classified E (cannot be responsibly assumed)** — every item either reuses existing,
already-authorized facts/code, or is a transparently-labeled, traceable placeholder with an
explicit real-world replacement path stated.

---

## REMAINING REAL-WORLD GOVERNANCE REQUIREMENTS

Unchanged by this exercise, and not satisfied by it:
- Real stakeholder authorship of the critical-infeasibility and Emergency-Mode-mapping
  policies (items 1–2 remain simulated placeholders only).
- Formal governance amendment of v2.5.0's tier-count defect (item 3's content is already
  decided; only the paperwork is outstanding).
- Real stakeholder decision on DEC-TR-03 and DEC-RES-03 (items 4–5 remain simulated).
- Real SD-07/SD-08 station/vendor data (item 6 remains simulated; no real battery
  specification exists).
- Real named individuals for the D16 roles (item 7's fictional names satisfy nothing; SD-13
  remains fully open).

## Is this package sufficient to proceed to a RESEARCH-ONLY MILP v2 *design* (not
implementation)?

**Yes, for design discussion purposes only, with the limitations stated throughout this
package carried forward explicitly.** Every one of the six real blockers now has a
transparently-labeled, traceable placeholder (reused existing facts/code where possible,
clearly-flagged research constructs where not), with no item left silently unresolved and
no item classified as irresponsible to assume. This is sufficient to *sketch* what a
research-only MILP v2 formulation could look like for internal discussion. **It is not
sufficient, and is not represented as sufficient, for any real authorization, approval, or
production use** — none of the underlying real blockers (stakeholder decisions, station
data, named approvers) have actually been resolved; they have only been provisionally
stood in for, by a role-played research manager with no real authority, so that research
design discussion can proceed without waiting on them.

## STOP

No code, config, or model was modified. No MILP experiment was run. GAP19 remains frozen as
the control. This package does not overwrite, amend, or supersede any real governance
document.
