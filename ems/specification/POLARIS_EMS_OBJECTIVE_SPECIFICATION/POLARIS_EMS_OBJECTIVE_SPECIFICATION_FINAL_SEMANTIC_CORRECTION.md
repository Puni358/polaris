# POLARIS EMS — OBJECTIVE SPECIFICATION FINAL SURGICAL SEMANTIC CORRECTION

**Package Directory**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Document Version**: 2.3.0 (Final Bounded Governed Draft)  
**Governance Status**: `EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT`  
**Policy Mapping Status**: `POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS`  
**D15 Reconciliation**: `D15_RECONCILIATION = PASS`  
**Next Governed Gate**: `NEXT_GOVERNED_STEP = EMS_OBJECTIVE_SPECIFICATION_REVIEW`  
**Date**: 2026-09-22  

---

## 1. EXECUTIVE GOVERNANCE STATUS & SURGICAL CORRECTION SUMMARY

This surgical correction addresses three narrow semantic and boundary items in `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`:

1. **Stage 2 Objective Semantics Clarification**:
   - Mathematical Objective: `TARGET_SHORTFALL_MINIMIZATION` ($\min \sum \max(0, 	ext{SOC}_{	ext{EBR\_target}}(t) - 	ext{SOC}(t))$).
   - Descriptive Wording: `"RESERVE_HEADROOM_MAXIMIZATION IS DESCRIPTIVE, NOT AN INDEPENDENT MATHEMATICAL OBJECTIVE."`
   - Boundary Handling Explicitly Bounded:
     - Case A ($	ext{SOC}_{	ext{EBR\_target}} \le 	ext{SOC}_{	ext{EBR\_floor}}$): Target does not exceed baseline floor $	o$ `STAGE2_OPTIMIZATION_BEHAVIOR = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
     - Case B ($	ext{SOC}_{	ext{EBR\_floor}} < 	ext{SOC}_{	ext{EBR\_target}} \le 	ext{SOC}_{	ext{max}}$): Target lies within physical SOC range.
     - Case C ($	ext{SOC}_{	ext{EBR\_target}} > 	ext{SOC}_{	ext{max}}$): Target exceeds battery capacity $	o$ `STAGE2_TARGET_HANDLING = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
     - Case D ($	ext{SOC}_{	ext{EBR\_target}} < 0$): Target invalid $	o$ `TARGET_VALIDITY_HANDLING = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
   - Status: `STAGE2_OBJECTIVE_SEMANTICS = TARGET_SHORTFALL_MINIMIZATION`, `RESERVE_HEADROOM_MAXIMIZATION = DESCRIPTIVE_INTERPRETATION_ONLY`, `STAGE2_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.

2. **D8 Fuel-Budget Mathematics Boundary**:
   - Candidate Inequality: $\sum_t 	ext{Fuel}_{	ext{liter}}(t) \le F_{	ext{budget\_remaining}}(t_0)$ is designated a `CONCEPTUAL / CANDIDATE FUEL-BUDGET CONSTRAINT` and `NOT YET AN AUTHORIZED EXECUTABLE FORMULATION`.
   - Explicit Governance Wording: *"The candidate fuel-budget inequality does not by itself implement the D14 lexicographic hierarchy. Fuel conservation is a policy objective subordinate to Critical reliability; the physical fuel inventory is a feasibility constraint. The mathematical interaction between seasonal/resupply accounting, the receding MPC horizon, and physical fuel exhaustion requires future implementation specification."*
   - Status: `FUEL_BUDGET_CONSTRAINT_FORM = REQUIRES_IMPLEMENTATION_SPECIFICATION`, `D8_SEASONAL_FUEL_ACCOUNTING = REQUIRES_IMPLEMENTATION_SPECIFICATION`, `FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`.

3. **Single Governed Gate Alignment**:
   - Changed `NEXT_GOVERNED_STEP` to strictly: `EMS_OBJECTIVE_SPECIFICATION_REVIEW`.

```yaml
STAKEHOLDER_POLICY_APPROVAL:           APPROVED
D1_D16_TRACEABILITY:                   COMPLETE
D15_RECONCILIATION:                    PASS
POLICY_TO_MATH_MAPPING:                COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS
EMS_OBJECTIVE_SPECIFICATION:           ESTABLISHED_AS_GOVERNED_DRAFT

STAGE2_POLICY:                         RESOLVED
STAGE2_CONCEPTUAL_INTERFACE:           RESOLVED
STAGE2_OBJECTIVE_SEMANTICS:            TARGET_SHORTFALL_MINIMIZATION
RESERVE_HEADROOM_MAXIMIZATION:         DESCRIPTIVE_INTERPRETATION_ONLY
STAGE2_TAUTOLOGY:                      CORRECTED
STAGE2_FORMULATION:                    REQUIRES_IMPLEMENTATION_SPECIFICATION

D10_POLICY:                            RESOLVED
D10_CURTAILMENT_DECOMPOSITION:         CONCEPTUAL_DECOMPOSITION_ONLY
D10_EXECUTABLE_CLASSIFICATION:         REQUIRES_IMPLEMENTATION_SPECIFICATION

D8_POLICY:                             RESOLVED
D8_PHYSICAL_FUEL_INVENTORY:            PHYSICAL_CONSTRAINT
D8_SEASONAL_FUEL_ACCOUNTING:           REQUIRES_IMPLEMENTATION_SPECIFICATION
D8_FUEL_BUDGET_CONSTRAINT_FORM:        REQUIRES_IMPLEMENTATION_SPECIFICATION
FUEL_RELIABILITY_INFEASIBILITY:        REQUIRES_GOVERNANCE_CLARIFICATION

UNAUTHORIZED_POLICY_INFERENCE:          0
UNAUTHORIZED_NUMERICAL_POLICY_VALUES:  0

CURRENT_EMS_IMPLEMENTATION:            FROZEN
EMS_CODE_MODIFIED:                    NO
OPTIMIZER_MODIFIED:                   NO
MILP_MODIFIED:                        NO
CONFIG_MODIFIED:                      NO
MODEL_MODIFIED:                       NO
MODEL_TRAINED:                        NO
MODEL_INFERRED:                       NO
EMS_EXECUTED:                         NO
MPC_EXECUTED:                         NO
MILP_EXECUTED:                        NO
DIGITAL_TWIN_EXECUTED:                NO
V2_RERUN:                             NO
NEW_EMS_EXPERIMENT:                   NO

IMPLEMENTATION_AUTHORIZATION:          NOT_GRANTED
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW
```

---

## 2. SURGICAL CORRECTION LOG

| CORRECTION_ID | AREA | ORIGINAL_TEXT_OR_FORMULATION | PROBLEM | CORRECTED_TEXT_OR_FORMULATION | POLICY_STATUS | MATHEMATICAL_STATUS | IMPLEMENTATION_STATUS | EVIDENCE | HASH |
|---------------|------|------------------------------|---------|-------------------------------|---------------|---------------------|-----------------------|----------|------|
| CORR_SEM_01 | Stage 2 Semantics | "Maximize BESS reserve headroom" | Conflated descriptive wording with formal mathematical objective | Formally defined as `TARGET_SHORTFALL_MINIMIZATION`; noted `"RESERVE_HEADROOM_MAXIMIZATION IS DESCRIPTIVE, NOT AN INDEPENDENT MATHEMATICAL OBJECTIVE."` | RESOLVED | TARGET_SHORTFALL_MINIMIZATION | REQUIRES_IMPLEMENTATION_SPECIFICATION | D11, Math logic | Calculated |
| CORR_SEM_02 | Stage 2 Boundaries | Target boundary handling implicit | Boundary edge-cases needed explicit governance classification | Target $\le$ Floor marked `STAGE2_OPTIMIZATION_BEHAVIOR = REQUIRES_IMPLEMENTATION_SPECIFICATION`; Target $> 	ext{SOC}_{	ext{max}}$ marked `STAGE2_TARGET_HANDLING = REQUIRES_IMPLEMENTATION_SPECIFICATION` | RESOLVED | BOUNDARY_CASES_BOUNDED | REQUIRES_IMPLEMENTATION_SPECIFICATION | D11, Math bounds | Calculated |
| CORR_D8_SEM_01 | D8 Fuel Budget Math | $\sum 	ext{Fuel} \le F_{	ext{budget}}$ presented without explicit boundary wording | Risk of misinterpreting candidate inequality as final D14 hierarchy implementation | Labeled `CONCEPTUAL / CANDIDATE FUEL-BUDGET CONSTRAINT`; added explicit disclaimer: *"The candidate fuel-budget inequality does not by itself implement the D14 lexicographic hierarchy."* | RESOLVED | CANDIDATE_CONSTRAINT_ONLY | REQUIRES_IMPLEMENTATION_SPECIFICATION | D08, D14, Prompt Sec 7 | Calculated |
| CORR_GATE_01 | Governance Gate | `EMS_OBJECTIVE_SPECIFICATION_REVIEW_AND_IMPLEMENTATION_SPECIFICATION_REVIEW` | Combined two distinct governed gates | Changed strictly to `EMS_OBJECTIVE_SPECIFICATION_REVIEW` | RESOLVED | SINGLE_GATE_ALIGNED | OBJECTIVE_SPECIFICATION_REVIEW_ONLY | Prompt Sec 9 | Calculated |
