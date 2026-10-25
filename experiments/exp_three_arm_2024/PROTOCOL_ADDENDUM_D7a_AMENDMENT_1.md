# Protocol Addendum D7a, Amendment 1: classification of Arm C

**Version:** 1 (2026-10-11). **Decision:** D10a, RESOLVED BY DELEGATED TECHNICAL AUTHORITY. Recorded by the technical PM (CC) under the project lead's delegation in M9 (`cmsg_017TpQv3UrTPMkzn658LmXvX2WPEGQjqxQQ7wSucS9sxg4`, 2026-10-11T04:29:38Z).

**Timing.** This amendment is recorded before any calibration or evaluation run. It does not date from the original D7a addendum, and it is not a project-lead approval of that addendum.

**Historical record kept unchanged.** `reports/source_prep/PROTOCOL_ADDENDUM_D7a.md` and `reports/source_prep/PROTOCOL.md` are not edited. The proposal this amendment adopts is `reports/PROPOSED_AMENDMENT_D7a-1.md` (M8), also kept unchanged.

## Amended text

One cell of the D7a addendum's §1 table changes: the result label of C.

| | D7a §1, row C, column "Result label" |
|---|---|
| Before (historical) | `DIAGNOSTIC` |
| **After (this amendment)** | `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE` |

## Why

PROTOCOL.md §7 is the controlling classification. Quoted verbatim:

- Row "Classes": "**Diagnostic:** B, any classification of unmet hours. **Research-only candidate:** C passing S1–S4 + E1. **Promotion-eligible:** nothing from this experiment. Promotion would need a fresh holdout plus separate authorization".
- Row "B": "Any 40% claim needs a non-diagnostic arm passing all gates".

The D7a label contradicted the first passage. It also made the second impossible to satisfy, because no arm in the experiment would have been non-diagnostic. The D7a addendum gives no reason for labelling C diagnostic; its §4 is about C's geometry and its comparison partner. The amendment is the smallest change that restores consistency. The alternative, amending PROTOCOL §7, would remove the experiment's only research-only candidate.

## Arm eligibility after this amendment

| Arm | Class | In E1 family (D10) | Promotion-eligible |
|---|---|---|---|
| PC-Control | Reference (denominator) | — | — |
| A | `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT` | Yes | No |
| A-Fix | `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE`; geometry-fix diagnostic | No | No |
| B | `NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE`; perfect-solar diagnostic | Never | Never |
| C | `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE` | Yes | No |

**Unchanged:**
- C is compared with A-Fix as the diagnostic comparison that isolates calibration from the timestamp fix (D7a §4).
- C vs PC-Control mixes the geometry fix and the calibration, and must be reported as such.
- Nothing from this experiment is promotion-eligible.
- No result from this experiment alone may be presented as independently validated, or as proof of a 40% diesel reduction. The evaluation window is not a fresh holdout (D1).

## Implementation

- `scripts/run_three_arm_2024.py` `LABEL_C` = `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)`.
- `promotion_eligible` stays `False` for every arm. `preflight.check_arms` and `test_nothing_is_promotion_eligible_and_b_is_noncausal` enforce this.
- Tests: `tests/test_decision_resolution_m9.py`.
