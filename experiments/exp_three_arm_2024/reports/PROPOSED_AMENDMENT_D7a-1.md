# Proposed Amendment D7a-1: classification of Arm C. **PROPOSED, NOT APPLIED**

Prepared 2026-10-11 by CC under M8 item 4 ("If the documents remain contradictory, leave the decision blocked and propose the smallest explicit amendment for my review"). Nothing has been applied. `reports/source_prep/PROTOCOL_ADDENDUM_D7a.md` and `reports/source_prep/PROTOCOL.md` are unchanged. Decision D10a stays blocked until the project lead accepts, changes or rejects this amendment.

## The contradiction

| Document | Exact text |
|---|---|
| PROTOCOL.md §7, row "Classes" | "**Diagnostic:** B, any classification of unmet hours. **Research-only candidate:** C passing S1–S4 + E1. **Promotion-eligible:** nothing from this experiment. Promotion would need a fresh holdout plus separate authorization" |
| PROTOCOL.md §7, row "B" | "Any 40% claim needs a non-diagnostic arm passing all gates" |
| PROTOCOL_ADDENDUM_D7a.md §1, table | "\| C \| corrected (see §4) \| DIAGNOSTIC \|" |

PROTOCOL classifies C as a research-only candidate and does not list it as diagnostic. The D7a addendum labels C `DIAGNOSTIC`. Under the D7a label, no arm in this experiment could support the "non-diagnostic arm" condition for a 40% claim. The contradiction is about the diagnostic-only status. It is not about family inclusion or promotion eligibility (see `reports/DECISION_FOLLOWUP_M8_2026-10-11.md` §1).

## Smallest amendment proposed

Change one cell of the D7a addendum §1 table, the result label of C:

| | Text |
|---|---|
| Current | `DIAGNOSTIC` |
| Proposed | `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE` |

**Unchanged:**
- A-Fix stays `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE` and "a diagnostic comparison".
- B stays diagnostic and non-deployable.
- A stays `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT`.
- The E1 family stays {A, C} (D10).
- D7a §4 still makes C-vs-A-Fix the diagnostic comparison that isolates calibration from the timestamp fix.
- Nothing becomes promotion-eligible.

**Mechanism if accepted:**
1. The amendment would be recorded as a new file, `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`. The historical copy in `reports/source_prep/` is never edited.
2. The runner's result label `LABEL_C` in `scripts/run_three_arm_2024.py:66` would change to match.
3. The manifests would be regenerated.
4. D10a would be recorded as resolved.

**Alternative if rejected:** keep C as `DIAGNOSTIC`. Then PROTOCOL §7 would need an explicit amendment instead, because it would no longer have any research-only candidate, and its 40% claim condition could never be met by this experiment. That is a larger change, so it is not the recommendation.

**Status: PROPOSED — awaiting project-lead review.**

**Status update 2026-10-11 (M9):** adopted as decision D10a, RESOLVED BY DELEGATED TECHNICAL AUTHORITY under the project lead's M9 delegation, and recorded in `PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md`. The text above is unchanged from M8.
