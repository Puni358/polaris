# POLARIS — FINAL GAP19 SOLVER ARCHITECTURE HUMAN DECISION PACKAGE
## GOVERNANCE DECISION PREPARATION PHASE

============================================================
GOVERNANCE MANDATE & ABSOLUTE NEUTRALITY
============================================================

This document constitutes the final, neutral, evidence-backed human decision package for **GAP19: POLARIS EMS SOLVER ARCHITECTURE SELECTION**.

The sole purpose of this package is to provide the human project owner with factual technical evidence, detailed trade-offs, and governance constraints required to make the final GAP19 decision.

**STRICT NEUTRALITY GUARANTEES:**
- NO SOLVER ARCHITECTURE HAS BEEN SELECTED, RANKED, OR SCORED.
- EVALUATIVE ARCHITECTURAL JUDGMENTS ARE EXPLICITLY OMITTED.
- THE HUMAN DECISION FORM IS LEFT COMPLETELY BLANK FOR THE HUMAN PROJECT OWNER.

---

## 1. EXECUTIVE FACTUAL SUMMARY

The POLARIS EMS objective was defined in *EMS Objective Specification V2* as a four-stage lexicographic hierarchy:
1. **Stage 1 — Critical Reliability**: Minimization of unserved critical load energy shortfall.
2. **Stage 2 — Emergency Battery Reserve**: Minimization of EBR target shortfall.
3. **Stage 3 — Fuel Conservation**: Minimization of liters-based diesel fuel consumption.
4. **Stage 4 — Renewable Utilization**: Minimization of avoidable renewable curtailment.

The current system implementation (`system/optimization/implementations/milp.py`) employs a single composite scalar cost objective and does not yet implement the multi-stage lexicographic architecture. GAP19 exists to select the solver architecture for implementing the approved 4-stage hierarchy.

---

## 2. GAP19 DECISION QUESTION

```text
"Which solver architecture should POLARIS authorize for implementation
of the approved four-stage lexicographic EMS objective?"
```

Candidate options:
- **OPTION A**: Sequential MILP lexicographic implementation using the current SciPy/HiGHS stack.
- **OPTION B**: Solver-native multi-objective implementation requiring an API/solver path that explicitly exposes objective-priority semantics.
- **OPTION C**: Weighted scalarization / penalty architecture (Status: `ENGINEERING_RISK_ONLY` reference).

---

## 3. EXISTING GOVERNANCE CONSTRAINTS

```yaml
STAKEHOLDER_POLICY: HUMAN_APPROVED
OBJECTIVE_SPECIFICATION_GOVERNANCE: PASS
IMPLEMENTATION_ARCHITECTURE_REVIEW: PASS
GAP19_SOLVER_ARCHITECTURE: REQUIRES_GOVERNANCE_DECISION
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
CODE_MODIFICATION: NOT_AUTHORIZED
OPTIMIZER_MODIFICATION: NOT_AUTHORIZED
SCHEMA_MODIFICATION: NOT_AUTHORIZED
EMS_EXECUTION: NOT_AUTHORIZED
MPC_EXECUTION: NOT_AUTHORIZED
DIGITAL_TWIN_EXECUTION: NOT_AUTHORIZED
CURRENT_EMS_IMPLEMENTATION: FROZEN
CURRENT_MILP_IMPLEMENTATION: FROZEN
```

---

## 4. CURRENT SOLVER & API AUDIT

Static inspection of the active POLARIS execution environment confirms:

- **Python Version**: `3.12.3` (`ESTABLISHED`)
- **SciPy Version**: `1.18.1` (`ESTABLISHED`)
- **Solver Engine**: HiGHS C++ MILP engine via SciPy (`ESTABLISHED`)
- **`scipy.optimize.milp` Signature**: `scipy.optimize.milp(c, *, integrality=None, bounds=None, constraints=None, options=None)` (`ESTABLISHED`)
- **Multiple Cost Vectors**: `NOT_EXPOSED`. Accepts single 1D cost array `c` only.
- **Objective Priority Exposure**: `NOT_EXPOSED` by current SciPy API.
- **Native HiGHS Multi-Objective Capability**: `NOT_VERIFIED` for current wrapper path.
- **Direct HiGHS C++ Bindings**: `NOT_INSTALLED` / `REQUIRES_EXTERNAL_DEPENDENCY`.

---

## 5. OPTION A — TECHNICAL ANALYSIS

- **Conceptual Structure**: Python solver orchestration layer executing 4 sequential MILP solves per MPC cycle (`ARCHITECTURAL_PROPOSAL`).
  - **Pass 1**: Minimize Stage 1 $J_1(x) \implies$ record $J_1^*$ $\implies$ add lock $J_1(x) \le J_1^* + \epsilon_1$.
  - **Pass 2**: Minimize Stage 2 $J_2(x)$ s.t. $J_1(x) \le J_1^* + \epsilon_1 \implies$ record $J_2^*$ $\implies$ add lock $J_2(x) \le J_2^* + \epsilon_2$.
  - **Pass 3**: Minimize Stage 3 $J_3(x)$ s.t. Stage 1 & 2 locks $\implies$ record $J_3^*$ $\implies$ add lock $J_3(x) \le J_3^* + \epsilon_3$.
  - **Pass 4**: Minimize Stage 4 $J_4(x)$ s.t. Stage 1, 2, and 3 locks $\implies$ extract $x^*$.
- **Status**: `TECHNICALLY_FEASIBLE` with current SciPy 1.18.1 / HiGHS stack. Zero external dependencies required.
- **Priority Preservation**: Preserved via explicit lock constraints, subject to bounded numerical lock tolerances ($\epsilon_1, \epsilon_2, \epsilon_3$) and solver feasibility tolerances (`STATIC_TECHNICAL_FINDING`).
- **Failure Handling**: Detect and record failure (`RESPONSE_POLICY_REQUIRED`). Zero unauthorized operational fallback policies (no auto load shedding, no auto diesel fallback, no auto emergency mode).

---

## 6. OPTION B — TECHNICAL ANALYSIS

- **Conceptual Structure**: Direct solver invocation passing native objective priority levels to a multi-objective MILP engine (`ARCHITECTURAL_PROPOSAL`).
- **Status**: `NOT_AVAILABLE` through current `scipy.optimize.milp()` API.
- **Dependencies**: `POTENTIAL_IMPLEMENTATION_PATH` (`REQUIRES_SEPARATE_DEPENDENCY_AND_API_VERIFICATION`). Would require introducing an external binding or solver package (e.g. `highspy`, Gurobi, CPLEX).
- **Architectural Characteristics**: Direct multi-objective priority specification at solver layer, subject to selected solver's documented semantics and tolerances. (Note: Directness is an architectural trait, NOT demonstrated outcome superiority).

---

## 7. OPTION C — FACTUAL REFERENCE

- **Status**: `ENGINEERING_RISK_ONLY`. Option C is NOT formally governance-rejected unless an explicit human decision states so.
- **Conceptual Structure**: Single MILP solve combining all 4 stages into a single scalar cost vector $c_{total} = \sum w_k c_k$.
- **Technical Risks**: Extreme scale separation degrades constraint matrix condition number; high risk of lower-priority stage accumulation polluting higher-priority stage boundaries (`STATIC_TECHNICAL_FINDING`).
- **Illustrative Values**: Example weights ($10^{12}, 10^8, 10^4, 1$) are `ILLUSTRATIVE_ONLY` and `UNAUTHORIZED`.

---

## 8. NUMERICAL TOLERANCE REGISTER

| PARAMETER | TYPE | UNITS | FORMULATION / VALUE | JUSTIFICATION | GOVERNANCE STATUS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `eps_1` | Stage 1 Lock | kWh | $J_1(x) \le J_1^* + \epsilon_1$ | Absolute energy tolerance for critical load lock | `PROVISIONAL / NOT AUTHORIZED` |
| `eps_2` | Stage 2 Lock | kWh | $J_2(x) \le J_2^* + \epsilon_2$ | Absolute energy tolerance for EBR shortfall lock | `PROVISIONAL / NOT AUTHORIZED` |
| `eps_3` | Stage 3 Lock | Liters | $J_3(x) \le J_3^* + \epsilon_3$ | Absolute fuel volume tolerance for fuel lock | `PROVISIONAL / NOT AUTHORIZED` |
| `feasibility_tol` | Solver Primal | - | `1e-6` | HiGHS default primal feasibility tolerance | `CURRENT_DEFAULT` |
| `integrality_tol` | Solver Integer | - | `1e-6` | HiGHS default integrality tolerance | `CURRENT_DEFAULT` |
| `optimality_tol` | Solver Dual | - | `1e-6` | HiGHS default dual optimality tolerance | `CURRENT_DEFAULT` |
| `replay_tol_abs` | Replay Abs | Physical | `1e-5` | Authorized numerical replay tolerance | `GOVERNANCE_REQUIREMENT` |

---

## 9. PERFORMANCE & REPRODUCIBILITY

- **Performance**: Execution time status is `STATUS = NOT_MEASURED`. Zero fabricated timing estimates are provided.
- **Reproducibility Contract**: Requires locking solver identity (HiGHS), solver version (1.18.1), Python version (3.12.3), dependency lock (`pyproject.toml`), objective vectors ($c_1..c_4$), intermediate stage objectives ($J_1^*..J_4^*$), lock tolerances ($\epsilon_1..\epsilon_3$), solver options, model inputs, initial state, return status, and fresh-process replay within authorized tolerances (`GOVERNANCE_REQUIREMENT`).

---

## 10. INTERFACE & SCHEMA IMPACT

Additive schema extensions are required to support multi-stage lexicographic dispatch:
- **`ForecastBundle`**: `ADDITIVE_EXTENSION_REQUIRED` (Adds 5-tier demand forecast arrays).
- **`StationState`**: `ADDITIVE_EXTENSION_REQUIRED` (Adds generator operating modes and EBR state).
- **`DispatchPlan`**: `ADDITIVE_EXTENSION_REQUIRED` (Adds Stage 1–4 objective values $J_1^*..J_4^*$).
- **`LocalMILPEnergyOptimizer`**: Structural modification depending on chosen solver architecture (`SOLVER_ARCHITECTURE_DEPENDENT`).

---

## 11. NEUTRAL IMPLEMENTATION IMPACT MATRIX

The complete neutral comparison matrix is stored in `POLARIS_EMS_GAP19_IMPLEMENTATION_IMPACT_MATRIX.csv`. It contains zero scores, zero rankings, and zero evaluative assignments.

---

## 12. GAP19 HUMAN GOVERNANCE DECISION FORM

```text
============================================================
POLARIS EMS — GAP19 HUMAN GOVERNANCE DECISION FORM
============================================================

DECISION ID: GAP19
DECISION TITLE: Selection of EMS Lexicographic Solver Architecture

SOLVER ARCHITECTURE SELECTION:

[ ] Option A — Sequential MILP lexicographic implementation
               (Uses current SciPy 1.18.1 / HiGHS stack with Python stage-locking loop)

[ ] Option B — Solver-native multi-objective implementation
               (Requires an API/solver path that explicitly exposes objective-priority semantics)

[ ] Option C — Weighted scalarization / penalty architecture
               (Status: engineering-risk reference only)

DECISION MAKER: __________________

DECISION DATE: __________________

RATIONALE: __________________

DECISION CONDITIONS: __________________

REQUIRED DEPENDENCIES: __________________

IMPLEMENTATION AUTHORIZATION: [ ] NOT GRANTED (Requires separate Implementation Authorization Review)

VALIDATION AUTHORIZATION: [ ] NOT GRANTED (Requires separate Validation Authorization Review)

NOTES: __________________
```

---

## 13. WHAT MUST BE TRUE AFTER THE HUMAN DECISION

- **If Option A is selected**:
  1. Exact sequential orchestration architecture specified in an Implementation Specification.
  2. Stage lock formulations ($J_k \le J_k^* + \epsilon_k$) and tolerances ($\epsilon_1, \epsilon_2, \epsilon_3$) formally governed.
  3. Additive schema extensions specified for `ForecastBundle`, `StationState`, `DispatchPlan`.
  4. Separate Implementation Authorization Review performed before writing code.
- **If Option B is selected**:
  1. Target solver engine and API bindings explicitly selected and verified.
  2. Dependency footprint, licensing, and cross-platform (Windows/Linux) packaging verified.
  3. Native multi-objective priority semantics and solver tolerances documented.
  4. Separate Implementation Authorization Review performed before writing code.

---

## 14. FULL-RUN READINESS PATH

```text
GAP19 Human Decision
        ↓
Solver Architecture Lock
        ↓
Implementation Specification
        ↓
Implementation Authorization
        ↓
Optimized EMS Implementation
        ↓
Static Integration Audit
        ↓
Controlled Single-Trajectory Validation
        ↓
Objective-Stage Validation
        ↓
Energy Conservation Validation
        ↓
Truth-Firewall Validation
        ↓
Controlled Multi-Trajectory Validation
        ↓
Full 173 × 24h Run Authorization
        ↓
Full Optimized EMS Experiment
```

---

## 15. PROTECTED ARTIFACTS & EXECUTION FIREWALL

```text
MILP Solves Executed = 0
EMS Optimization Steps = 0
MPC Simulation Steps = 0
Digital Twin Runs = 0
Model Inference Runs = 0
Dependency Installs = 0
Code Modifications = 0
Schema Modifications = 0
PROTECTED_ARTIFACT_INTEGRITY = PASS
EXECUTION_FIREWALL = PASS
```

---

## 16. FINAL PACKAGE GOVERNANCE STATUS

```yaml
PACKAGE_STATUS: READY_FOR_HUMAN_DECISION
HUMAN_DECISION_REQUIRED: YES
OPTION_A_STATUS: TECHNICALLY_FEASIBLE
OPTION_B_STATUS: EXTERNAL_SOLVER_DEPENDENCY_REQUIRED
OPTION_C_STATUS: ENGINEERING_RISK_ONLY
IMPLEMENTATION_AUTHORIZATION: NOT_GRANTED
EXECUTION_FIREWALL: PASS
PROTECTED_ARTIFACT_INTEGRITY: PASS
PACKAGE_COMPLETENESS: COMPLETE
FINAL_GOVERNANCE_STATUS: READY_FOR_HUMAN_DECISION
```

**HARD STOP.**
