# POLARIS Governance Decision Record: Customer-First Realization Policy

**Record ID:** `GOV-DECISION-REALIZATION-POLICY-2026-10-06`
**Timestamp (UTC):** 2026-10-06T00:00:44Z
**Status:** DECIDED — research governance. Production promotion UNAUTHORIZED. Realization-consistency campaign results QUARANTINED.
**Scope:** research semantics only. No production code, frozen artifact, prior Stage 4 result, or experiment was modified or run to make this decision.

---

## 1. Decision

**Customer-first realization policy.** Policy hierarchy: **customer load service > battery charging > curtailment.**

## 2. Explicit Record

1. **Arm A is the governing research realization semantics.** This is the existing executor semantics used in the corrected Stage 4 reproduction (surplus-based realization, served load first).
2. **Arm B is an unapproved storage-first / brownout policy variant.** It is quarantined. It is **not** a winner under any reading of this record.
3. **Candidate S remains the current conditional, frozen Stage 4 research winner under Arm A, with 23.11% diesel reduction.** The winner status is conditional on the caveats in §6.
4. **Candidate SW is not the winner.** It fails Arm-A proportional reliability Gate 2 by **−0.5815 pp** versus Control B.
5. **Production promotion remains UNAUTHORIZED.**
6. **The realization-consistency campaign results are QUARANTINED** pending provenance and authorization resolution. They are not deleted or overwritten.
7. **The planner-versus-realization charging mismatch remains an unresolved research defect.** It requires a **new preregistered study** (§5).

## 3. Rationale (Grounded in Existing Artifacts)

- **Arm B's safety flip is a reference artefact, not a service improvement.** Under B, Control B's proportional reliability falls by 5.1945 pp, while Candidate SW's own falls by 3.2910 pp. SW passes Gate 2 only because the baseline degrades further (`POST_STAGE4_REALIZATION_CAUSAL_GOVERNANCE_AUDIT.md` §5). A safety conclusion that depends on a degraded reference is not an acceptable basis for a decision.
- **The optimizer never priced non-critical load.** The objective carries no penalty for non-critical service (J1–J4 only), and Layer B ties served load to critical demand. Arm B therefore operationalises a shedding policy that the optimizer never valued (`POST_STAGE4_REALIZATION_CAUSAL_GOVERNANCE_AUDIT.md` §2.2).
- **Arm B sheds customer load to charge batteries while supply is available.** It removes 2,557.44 kWh of Control B's customer load and a further 1,532.80 kWh of SW's (audit §3–4). Such a policy requires explicit governed authority that does not exist in the specification.
- **Arm A is the basis the freeze and corrected reproduction were written against.** Adopting it keeps the research basis unchanged and avoids changing policy and reference simultaneously.

## 4. Affected Experiments and Artifacts

| Identifier | Role | Status after this record |
|---|---|---|
| `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT` (frozen original) | Frozen Stage 4 | Unchanged. Remains the historical record. |
| `EXP-STAGE4-CORRECTED-REPRODUCTION-2025-HOLDOUT` | Arm A reference | Governing research basis. Unchanged. |
| `EXP-STAGE4-REALIZATION-CONSISTENCY-2025` | Arm A vs Arm B | Arm A retained as governing. Arm B quarantined. Results quarantined pending provenance. |
| Arm B executor `plan_consistent_realization.py` | Quarantined variant | Retained, not used for decisions. |
| Planner-realization charge mismatch (Issue 3) | Research defect | Unresolved. Needs new preregistered study. |

**Hashes of referenced artifacts (computed 2026-10-06T00:00:44Z):** see the JSON companion `POST_STAGE4_GOVERNANCE_DECISION_RECORD.json`, `hashes_of_record` field. Values are read directly from disk, not transcribed.

## 5. Next-Step Recommendation

1. **Resolve the provenance of the realization-consistency run.** Establish who executed it, when, and under what authority. The preregistration `EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION` was not frozen or authorized, and an earlier report in this chain stated the experiment had not been run. Record the finding in the governance log. Do not delete the artifacts.
2. **Locate the "CC review" cited in the decision request.** A search of `experiments/` did not find it. It is not characterized in this record. Its contents must be recorded before this decision can be treated as fully reviewed.
3. **Draft a new preregistration** that prices non-critical load in the planner objective, so the optimizer and the realization share one economic contract. The preregistered study must state its own realization semantics and must not reuse the quarantined Arm B results as confirmatory evidence.
4. **Correct the planner-realization documentation**: the corrected preregistration's "startup fuel 0.0 L" statement (optimizer value is 2.0 L), the fuel-cap wording, and the terminal indexing text. These are documentation corrections and do not change results.
5. **Keep production promotion blocked** until a governed operational policy exists and independent review is complete.

## 6. Caveats and Conditions (Remaining)

- **Winner status is conditional.** S's winner status depends on Arm A, on the planner defect remaining unresolved, and on the caveats below.
- **Provenance block.** The quarantined results exist on disk. Their authorization is unresolved.
- **The "CC review" is not located in the repository.** This record does not rely on its contents.
- **The planner still plans charging that Arm A cannot deliver.** Reported SOC and reliability describe the realized trajectory, not the plan.
- **S's diesel gate** was not reported in the corrected statistics. An offline check passes it (Wilcoxon p ≈ 2.45×10⁻¹⁰; BCa 95% lower bound ≈ 8.5 L/origin). Official reporting is still required.
- **Startup accounting:** the optimizer uses 2.0 L per start, and reported simulator fuel charges 0 L. Ranking is unchanged under either accounting, per the prior audit.
- **Production promotion is unauthorized.** Nothing in this record authorizes deployment.

## 7. Verification

- Hashes of all referenced artifacts were computed from disk at the timestamp above. No values were inferred or invented.
- No production file, frozen artifact, prior Stage 4 result, or experiment output was modified.
- No experiment was run in creating this record.
