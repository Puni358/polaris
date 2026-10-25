# POLARIS Governance Decision Record: Planner-CF v1.2 (Amendment A2)

**Record ID:** `GOV-DECISION-PLANNER-CF-V1-2-A2-2026-10-06`
**Date (UTC):** 2026-10-06
**Status:** DECIDED — governance and archive step only. v1.2 implementation NOT performed. No experiment run. Production promotion UNAUTHORIZED.
**Relates to:** `experiments/EXP_PLANNER_CUSTOMER_FIRST_CONSISTENCY_PREREGISTRATION.md` §17 (Amendment A2).
**Does not overwrite:** `POST_STAGE4_GOVERNANCE_DECISION_RECORD.md` or `GOV_DECISION_LOWER_BOUND_CERTIFICATION_2026-10-06.md`.

## Decisions
1. Planner-CF v1.1 is archived as a completed, non-accepted campaign under `archive/v1.1/`. Its outputs are not reclassified.
2. Class B (70 rows, objective-equivalent ties): explicit governance admission under the seven-condition rule of A2 §17.3. No secondary planner tie-break is added.
3. Class C (2 rows, terminal-hour fuel starvation): Planner-CF v1.2 adds the hour-0 constraint `5·u_diesel[0] + 0.00025·p_diesel[0] ≤ F_rem`.
4. NG1 remains ACTIVE and is evaluated against G1 as amended by A2 §17.3. Only ORACLE-PHYS audit results count toward NG1.
5. v1.2 results become eligible for acceptance only after the fresh ORACLE-PHYS v1.2 G1 and G12 audits pass and the post-run gates pass.
6. ORACLE-CTRL outputs are not required by G1 and are not regenerated under v1.2. They remain archived v1.1 artifacts.

## Non-changes
The lower-bound certification, its pins, the realization executor, GAP19, DispatchPlan, the causal forecaster, the router, the frozen extractor, the safety gates, the E1 gate, the 40 % target, and the decision rule are all unchanged.

## Authorization
This record authorizes the archive and governance text only. It does not authorize implementation, oracle execution or a campaign. Each of those requires its own step in the approved sequence.

**Production promotion: none follows from this record.**
