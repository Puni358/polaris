# Change Log: Rev. 2 → Rev. 3 (addressing `MILP_V2_REV2_DESIGN_AUDIT.md`)

| Finding | Severity | How addressed in Rev. 3 |
|---|---|---|
| #1 Constraint #4 not amended; `unmet_load` double-counts Essential-served energy | BLOCKING | Constraint #4 rewritten to a three-way split: `p_served + p_served_essential + p_unmet = demand`. Added `essential_demand[t]` clipping (`min(5,000W, max(0, demand−critical_demand))`) to keep `p_unmet ≥ 0` feasible — mirrors the existing `critical_demand` clipping pattern, not a new convention. |
| #3 Uncosted `P_unmet_essential` indistinguishable from routing surplus into extra charging | BLOCKING | `P_unmet_essential` added into the existing `J4` vector at the **identical existing coefficient** already used for curtailment (`1.0`/Wh) — not a new number, reused directly. Breaks the indifference: serving Essential load now measurably lowers `J4` when free to do so; routing the same surplus into extra charging does not. Stage count and `J1`–`J4` ordering unchanged. |
| #2 Tier 2 vs. Tier 3 mapping stated with more confidence than evidence supports | NEEDS CLARIFICATION | Explicitly re-labeled a `SIMULATED_RESEARCH_ASSUMPTION`/judgment call — both tier assignments stated as equally defensible; Rev. 3 proceeds with Tier 2 only for concreteness, not as a resolved fact. |
| #5 Semantic validity of reusing the `NORMAL`-route `EmergencyAssessment` unverified | NEEDS CLARIFICATION → **new finding: CONFIRMED INVALID** | Direct inspection of `system/control/ecd.py` shows `preserved_resource` is *always* `NONE` or `BOTH` under `mode == NORMAL` — never `BATTERY`/`DIESEL`, the only two values `OptionDFallbackSolver.solve()` actually branches on. Reuse would trigger neither branch. **The Rev. 1/2 infeasibility→OptionD proposal is withdrawn and marked UNRESOLVED**, per instruction not to invent a replacement mechanism where none is defensible. |

## Preserved, unchanged, re-confirmed in Rev. 3

- 4-stage lexicographic structure (D15) — untouched.
- Terminal reserve (unit, formula, mechanical entry, priority) — untouched.
- No diesel-reduction tuning — re-confirmed; neither fix touches any fuel coefficient, the
  reserve mechanism, or `J1`–`J3`.
- Current GAP19 — frozen as the control throughout.
- All prior `SIMULATED_RESEARCH_ASSUMPTION` labels preserved; new/downgraded items labeled
  consistently.

## STOP

No code, config, or model changed. No implementation performed.
