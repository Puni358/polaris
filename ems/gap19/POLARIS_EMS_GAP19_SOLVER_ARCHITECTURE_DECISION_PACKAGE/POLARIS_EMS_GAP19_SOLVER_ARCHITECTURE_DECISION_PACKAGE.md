# POLARIS — GAP19 SOLVER ARCHITECTURE DECISION PACKAGE
## NEUTRAL GOVERNANCE DECISION PREPARATION PHASE (EVIDENCE-HARDENED)

============================================================
GOVERNANCE DECISION PREPARATION MANDATE
============================================================

This document constitutes the complete, neutral, evidence-based governance decision package for **GAP19 — EMS SOLVER ARCHITECTURE**.

This package exists to provide the human project owner with the factual information required to choose the future POLARIS EMS lexicographic solver architecture.

**ABSOLUTE NEUTRALITY MANDATE:**
- NO SOLVER ARCHITECTURE HAS BEEN SELECTED.
- NO SOLVER ARCHITECTURE IS RECOMMENDED.
- CANDIDATE ARCHITECTURES ARE NOT RANKED OR SCORED.
- NO ARCHITECTURE IS DECLARED "BEST", "PREFERRED", "OPTIMAL", OR "WINNER".

The human project owner will make the GAP19 decision after reviewing this package.

---

## 1. CURRENT GOVERNANCE STATE

```yaml
STAKEHOLDER_POLICY: HUMAN_APPROVED
OBJECTIVE_SPECIFICATION_GOVERNANCE: PASS
IMPLEMENTATION_ARCHITECTURE_REVIEW: PASS
GAP19_SOLVER_ARCHITECTURE: REQUIRES_GOVERNANCE_DECISION
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
CODE_MODIFICATION: NOT_AUTHORIZED
OPTIMIZER_MODIFICATION: NOT_AUTHORIZED
OBJECTIVE_COEFFICIENT_MODIFICATION: NOT_AUTHORIZED
SCHEMA_MODIFICATION: NOT_AUTHORIZED
EMS_EXECUTION: NOT_AUTHORIZED
MPC_EXECUTION: NOT_AUTHORIZED
DIGITAL_TWIN_EXECUTION: NOT_AUTHORIZED
NEW_EMS_EXPERIMENT: NOT_AUTHORIZED
MODEL_MODIFICATION: NOT_AUTHORIZED
FORECASTING_MODIFICATION: NOT_AUTHORIZED
CURRENT_EMS_IMPLEMENTATION: FROZEN
CURRENT_MILP_IMPLEMENTATION: FROZEN
```

---

## 2. AUTHORITATIVE INPUTS & AUDIT FINDINGS

The following read-only authoritative inputs established the baseline evidence:
1. `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION`
2. `POLARIS_EMS_STAKEHOLDER_DECISION_SHEET`
3. `POLARIS_EMS_OBJECTIVE_SPECIFICATION_V2/`
4. `POLARIS_EMS_OBJECTIVE_SPECIFICATION_GOVERNANCE_REVIEW/`
5. `POLARIS_EMS_IMPLEMENTATION_SPECIFICATION_ARCHITECTURE_REVIEW/`
6. `POLARIS_EMS_GAP19_INTERFACE_CORRECTION_REVIEW/`
7. Current optimizer: `system/optimization/implementations/milp.py`
8. Current optimizer config: `system/config/optimizer.yaml`

**Verified Baselines:**
- `GAP19_SOLVER_ARCHITECTURE` = `REQUIRES_GOVERNANCE_DECISION`
- `CURRENT_SCIPY_MILP_CAPABILITY` = `VERIFIED`
- `CURRENT_SCIPY_MILP_NATIVE_MULTIOBJECTIVE` = `NOT_EXPOSED`
- `HIGHS_NATIVE_MULTIOBJECTIVE` = `NOT_VERIFIED`
- `SEQUENTIAL_LEXICOGRAPHIC_ARCHITECTURE` = `TECHNICALLY_FEASIBLE`
- `OPTION_C_STATUS` = `ENGINEERING_RISK_ONLY`

---

## 3. DECISION SCOPE

The decision concerns the future implementation architecture for the approved four-stage lexicographic EMS objective:
- **Stage 1**: Critical Reliability (Unserved demand minimization)
- **Stage 2**: Emergency Battery Reserve Target-Shortfall Minimization
- **Stage 3**: Fuel Conservation (Liters-based diesel fuel minimization)
- **Stage 4**: Renewable Utilization / Avoidable Curtailment Minimization

The architecture must preserve strict priority semantics ($J_1 \succ J_2 \succ J_3 \succ J_4$).

---

## 4. CURRENT SOLVER STACK AUDIT

Static inspection of the current POLARIS execution environment confirms:
- **Python Version**: `3.12`
- **SciPy Version**: `1.18.1`
- **Solver Engine**: HiGHS C++ MILP engine (invoked internally by SciPy)
- **`scipy.optimize.milp` Signature**: `scipy.optimize.milp(c, *, integrality=None, bounds=None, constraints=None, options=None)`
- **Native Multi-Objective Exposure**: `CURRENT_SCIPY_MILP_NATIVE_MULTIOBJECTIVE` = `NOT_EXPOSED`. `scipy.optimize.milp` accepts only a single 1D array `c` for objective coefficients.
- **HiGHS Native Multi-Objective Capability**: Classified as `NOT_VERIFIED` in this environment until demonstrated by direct API evidence.

---

## 5. CANDIDATE ARCHITECTURE ANALYSIS

### OPTION A — Sequential MILP Lexicographic Orchestration
- **Conceptual Structure**: Python solver orchestration layer executing 4 sequential MILP solves per MPC cycle (`ARCHITECTURAL_PROPOSAL`).
  1. Solve Stage 1 $\to$ obtain $J_1^*$ $\to$ add lock constraint $J_1(x) \le J_1^* + \epsilon_1$.
  2. Solve Stage 2 $\to$ obtain $J_2^*$ $\to$ add lock constraint $J_2(x) \le J_2^* + \epsilon_2$.
  3. Solve Stage 3 $\to$ obtain $J_3^*$ $\to$ add lock constraint $J_3(x) \le J_3^* + \epsilon_3$.
  4. Solve Stage 4 $\to$ extract optimal decision vector $x^*$ for `DispatchPlan`.
- **Invocations per Cycle**: 4 solver calls per MPC cycle (`ARCHITECTURAL_PROPOSAL`).
- **Priority Leakage**: Lexicographic priority is enforced through explicit stage-lock constraints, subject to calibrated lock tolerances and solver numerical tolerances (`STATIC_TECHNICAL_FINDING`).
- **Dependencies**: Uses existing SciPy 1.18.1 stack. Zero new Python or binary dependencies required (`STATIC_TECHNICAL_FINDING`).
- **Status**: `TECHNICALLY_FEASIBLE`.

### OPTION B — Solver-Native Lexicographic / Multi-Objective Architecture
- **Conceptual Structure**: Direct solver invocation passing native objective priority levels to a multi-objective MILP engine (`ARCHITECTURAL_PROPOSAL`).
- **Invocations per Cycle**: 1 solver call per MPC cycle (`ARCHITECTURAL_PROPOSAL`).
- **Priority Leakage**: Native lexicographic semantics would represent objective priority at the solver layer, subject to the selected solver's documented multi-objective semantics and tolerances (`NOT_VERIFIED`).
- **Dependency Impact**: POTENTIAL IMPLEMENTATION PATH (`REQUIRES_SEPARATE_DEPENDENCY_AND_API_VERIFICATION`).
- **Status**: `EXTERNAL_SOLVER_DEPENDENCY_REQUIRED`.

### OPTION C — Penalty-Encoded Scalar Objective
- **Conceptual Structure**: Single MILP solve combining all 4 objective stages into a single scalar cost vector $c_{total} = w_1 c_1 + w_2 c_2 + w_3 c_3 + w_4 c_4$ (`ARCHITECTURAL_PROPOSAL`).
- **Invocations per Cycle**: 1 solver call per MPC cycle (`ARCHITECTURAL_PROPOSAL`).
- **Penalty Weight Derivation**: Penalty weights must be derived from the bounded numerical ranges of the individual objective terms and selected solver tolerances. Large scale separation can create numerical-conditioning and priority-leakage risks (`STATIC_TECHNICAL_FINDING`).
- **Illustrative Values**: Example coefficients (e.g. $10^{12}, 10^8, 10^4, 1$) are `ILLUSTRATIVE_ONLY` and `UNAUTHORIZED`.
- **Status**: `ENGINEERING_RISK_ONLY`. Option C remains classified as engineering risk only and is NOT governance-rejected without formal decision.

---

## 6. LEXICOGRAPHIC SEMANTICS & LOCK-CONSTRAINT ANALYSIS

Mathematically, Option A proposes to enforce lexicographic ordering via linear inequality lock constraints:

$$\text{Stage 1: } \min J_1(x) \implies \text{Lock: } J_1(x) \le J_1^* + \epsilon_1$$
$$\text{Stage 2: } \min J_2(x) \implies \text{Lock: } J_2(x) \le J_2^* + \epsilon_2$$
$$\text{Stage 3: } \min J_3(x) \implies \text{Lock: } J_3(x) \le J_3^* + \epsilon_3$$
$$\text{Stage 4: } \min J_4(x) \text{ subject to Stage 1, 2, and 3 locks.}$$

Tolerances $\epsilon_1, \epsilon_2, \epsilon_3$ require calibration (`REQUIRES_VALIDATION`).

---

## 7. NEUTRAL DECISION MATRIX

The neutral comparison matrix is stored in `POLARIS_EMS_GAP19_SOLVER_COMPARISON_MATRIX.csv`. It presents technical facts, dependencies, interface impacts, and risks across all 3 candidate architectures without scoring, ranking, or declaring a winner.

---

## 8. GAP19 HUMAN GOVERNANCE DECISION FORM

```text
============================================================
GAP19 HUMAN GOVERNANCE DECISION
============================================================

Decision question:
"Which solver architecture should POLARIS authorize for implementation
of the approved four-stage lexicographic EMS objective?"

Decision options:
OPTION A — Sequential MILP Lexicographic Orchestration
OPTION B — Solver-Native Lexicographic / Multi-Objective Architecture
OPTION C — Penalty-Encoded Scalar Objective

HUMAN_DECISION = __________________

DECISION_DATE = __________________

DECISION_AUTHORITY = __________________

RATIONALE = __________________
```

---

## 9. GOVERNANCE BOUNDARY & OPERATIONAL RESPONSE

Operational fallback behavior, emergency dispatch, load shedding, EBR relaxation policy, fuel emergency behavior, solver selection, penalty coefficients, and lock tolerances require separate authorization (`REQUIRES_GOVERNANCE_DECISION`). Failure handling in candidate architectures is strictly limited to detecting and recording failure events (`RESPONSE_POLICY_REQUIRED`).

---

## 10. REPRODUCIBILITY & PLATFORM COMPATIBILITY

- **Reproducibility**: Defined as deterministic replay within authorized numerical and structural replay tolerances (`GOVERNANCE_REQUIREMENT`).
- **Platform Compatibility**: Packages are classified as `DEPENDENCY_AVAILABILITY_VERIFIED`, while full runtime compatibility is classified as `POLARIS_RUNTIME_COMPATIBILITY_REQUIRES_VALIDATION`.
- **Deployment**: Architecturally compatible with offline deployment, subject to runtime/package validation.

---

## 11. FINAL GOVERNANCE STATUS

```yaml
CORRECTION_REVIEW_STATUS: PASS
GAP19_SOLVER_ARCHITECTURE: REQUIRES_HUMAN_DECISION
HIGHS_NATIVE_MULTIOBJECTIVE: NOT_VERIFIED
SCIPY_NATIVE_MULTIOBJECTIVE: NOT_EXPOSED
OPTION_A: TECHNICALLY_FEASIBLE
OPTION_B: EXTERNAL_SOLVER_DEPENDENCY_REQUIRED
OPTION_C: ENGINEERING_RISK_ONLY
UNAUTHORIZED_OPERATIONAL_POLICY_FOUND: NO
HASH_AUDIT: PASS
PROTECTED_ARTIFACT_INTEGRITY: PASS
EXECUTION_FIREWALL: PASS
SOLVER_SELECTION: NONE
SOLVER_RECOMMENDATION: NONE
SOLVER_RANKING: NONE
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
```

**HARD STOP.**
