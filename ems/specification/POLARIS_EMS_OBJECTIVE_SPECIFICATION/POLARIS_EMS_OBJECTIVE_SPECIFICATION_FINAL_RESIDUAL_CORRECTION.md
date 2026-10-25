# POLARIS EMS — OBJECTIVE SPECIFICATION FINAL RESIDUAL-AMBIGUITY CORRECTION REVIEW

**Package Directory**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Document Version**: 2.2.0 (Final Bounded Governed Draft)  
**Governance Status**: `EMS_OBJECTIVE_SPECIFICATION = ESTABLISHED_AS_GOVERNED_DRAFT`  
**Policy Mapping Status**: `POLICY_TO_MATH_MAPPING = COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS`  
**D15 Reconciliation**: `D15_RECONCILIATION = PASS`  
**Date**: 2026-09-22  

---

## 1. EXECUTIVE GOVERNANCE STATUS & RESIDUAL AUDIT SUMMARY

This audit eliminates the three remaining residual ambiguities in `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`:

1. **Stage 2 Emergency Battery Resilience**: Explicitly bounded. Separated physical cell floor ($	ext{SOC}_{	ext{min\_tech}} = 20\%$), baseline reserve floor ($	ext{SOC}_{	ext{EBR\_floor}}$), dynamic reserve target ($	ext{SOC}_{	ext{EBR\_target}}(t)$), and terminal SOC target ($	ext{SOC}_{	ext{terminal\_target}}(H)$). Boundary cases and non-tautological objective formulation are explicitly defined; dynamic target generation math is marked `STAGE2_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
2. **D10 Curtailment Decomposition**: Explicitly bounded. $P_{	ext{curt}} = P_{	ext{curt, necessary}} + P_{	ext{curt, avoidable}}$ is designated `CONCEPTUAL_DECOMPOSITION_ONLY` and `NOT_AN_AUTHORIZED_RUNTIME_CLASSIFICATION_RULE`. The policy exemption is preserved while marking `D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.
3. **D8 Fuel Budget vs Critical Reliability**: Explicitly bounded. Separated physical fuel inventory ($F_{	ext{rem}}(t) \ge 0$), resupply policy, and emergency fuel exhaustion response. Preserved D14 absolute reliability priority while marking physical fuel exhaustion response as `FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`.

```yaml
STAKEHOLDER_POLICY_APPROVAL:           APPROVED
D1_D16_TRACEABILITY:                   COMPLETE
D15_RECONCILIATION:                    PASS
POLICY_TO_MATH_MAPPING:                COMPLETE_WITH_EXPLICIT_UNRESOLVED_ELEMENTS
EMS_OBJECTIVE_SPECIFICATION:           ESTABLISHED_AS_GOVERNED_DRAFT

STAGE2_POLICY:                         RESOLVED
STAGE2_CONCEPTUAL_INTERFACE:           RESOLVED
STAGE2_TAUTOLOGY:                      CORRECTED
STAGE2_FORMULATION:                    REQUIRES_IMPLEMENTATION_SPECIFICATION

D10_POLICY:                            RESOLVED
D10_CURTAILMENT_DECOMPOSITION:         CONCEPTUAL_DECOMPOSITION_ONLY
D10_EXECUTABLE_CLASSIFICATION:         REQUIRES_IMPLEMENTATION_SPECIFICATION

D8_POLICY:                             RESOLVED
D8_PHYSICAL_FUEL_INVENTORY:            PHYSICAL_CONSTRAINT
D8_SEASONAL_FUEL_ACCOUNTING:           REQUIRES_IMPLEMENTATION_SPECIFICATION
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
NEXT_GOVERNED_STEP:                    EMS_OBJECTIVE_SPECIFICATION_REVIEW_AND_IMPLEMENTATION_SPECIFICATION_REVIEW
```

---

## 2. DETAILED RESIDUAL CORRECTION LOG

### CORR_STAGE2_01 — Storage Layer Separation & Non-Tautology
- **Original Ambiguity**: Stage 2 reserve objective and EBR lower bound lacked strict conceptual separation between hard floors and optimization targets.
- **Problem**: Conflating hard bounds with optimization targets risks mathematical tautologies ($\max(0, 	ext{Target} - 	ext{SOC}) = 0$).
- **Correction**: Established 4 explicit, distinct storage concepts:
  1. *Technical SOC Floor* ($	ext{SOC}_{	ext{min\_tech}} = 20\%$): Hard cell protection floor (`CURRENT_IMPLEMENTATION_FACT`).
  2. *Baseline Emergency Reserve Floor* ($	ext{SOC}_{	ext{EBR\_floor}}$): Hard operational reserve floor constraint ($	ext{SOC}(t) \ge 	ext{SOC}_{	ext{EBR\_floor}}$).
  3. *Dynamic EBR Target* ($	ext{SOC}_{	ext{EBR\_target}}(t)$): Dynamic risk-adaptive reserve headroom target optimized in Stage 2.
  4. *Terminal SOC Requirement* ($	ext{SOC}_{	ext{terminal\_target}}(H)$): Dynamic end-of-horizon storage requirement.
- **Boundary Cases Bounded**:
  - $	ext{SOC}_{	ext{EBR\_target}}(t) \le 	ext{SOC}_{	ext{EBR\_floor}}$: Target is fully satisfied by the baseline floor; Stage 2 objective penalty is 0.
  - $	ext{SOC}_{	ext{EBR\_floor}} < 	ext{SOC}_{	ext{EBR\_target}}(t) \le 	ext{SOC}_{	ext{max}}$: Active Stage 2 optimization headroom zone.
  - $	ext{SOC}_{	ext{EBR\_target}}(t) > 	ext{SOC}_{	ext{max}}$: Clamped to $	ext{SOC}_{	ext{max}}$ by physical hardware limits.
- **Classification**: `STAGE2_POLICY = RESOLVED`, `STAGE2_TAUTOLOGY = CORRECTED`, `STAGE2_FORMULATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.

### CORR_D10_01 — Curtailment Decomposition Classification
- **Original Ambiguity**: $P_{	ext{curt}} = P_{	ext{curt, necessary}} + P_{	ext{curt, avoidable}}$ was presented alongside partial classification rules.
- **Problem**: Stakeholder decision D10 establishes policy intent (necessary curtailment unpenalized; avoidable curtailment minimized), but does NOT authorize a runtime mathematical classification algorithm.
- **Correction**: Designated the decomposition equation as `CONCEPTUAL_DECOMPOSITION_ONLY` and `NOT_AN_AUTHORIZED_RUNTIME_CLASSIFICATION_RULE`. Marked executable decomposition math as `D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION`.

### CORR_D8_01 — Physical Fuel Inventory vs Policy Priority
- **Original Ambiguity**: Fuel budget constraint $\sum 	ext{Fuel}_{	ext{liter}}(t) \le F_{	ext{budget\_remaining}}$ interacted ambiguously with Stage 1 Critical Reliability ($P_{	ext{unmet, C}} = 0$).
- **Problem**: Implied fuel budget might force critical load shedding, violating D14 reliability priority, or implied fuel could be created when physically exhausted.
- **Correction**: Separated physical fuel inventory ($F_{	ext{rem}}(t) \ge 0$, physical constraint), seasonal fuel resupply policy (Stage 3 optimization & dynamic tracking), and physical fuel exhaustion infeasibility response (`FUEL_RELIABILITY_INFEASIBILITY = REQUIRES_GOVERNANCE_CLARIFICATION`).

---

## 3. RESIDUAL CORRECTION REGISTER

| CORRECTION_ID | AREA | ORIGINAL_TEXT_OR_FORMULATION | PROBLEM | CORRECTED_TEXT_OR_FORMULATION | POLICY_STATUS | MATHEMATICAL_STATUS | IMPLEMENTATION_STATUS | EVIDENCE | HASH |
|---------------|------|------------------------------|---------|-------------------------------|---------------|---------------------|-----------------------|----------|------|
| CORR_STAGE2_01 | Stage 2 Storage Layers | Stage 2 objective $\max(0, 	ext{SOC}_{	ext{EBR}} - 	ext{SOC})$ combined with hard $	ext{SOC} \ge 	ext{SOC}_{	ext{EBR}}$ | Tautological objective ($=0$ everywhere feasible) | Explicit 4-layer separation: Tech Floor ($20\%$), Baseline Reserve Floor ($	ext{SOC}_{	ext{EBR\_floor}}$), Dynamic EBR Target ($	ext{SOC}_{	ext{EBR\_target}}$), Terminal Target | RESOLVED | CONCEPTUAL_INTERFACE_RESOLVED | REQUIRES_IMPLEMENTATION_SPECIFICATION | D11, D12 | Calculated |
| CORR_STAGE2_02 | Stage 2 Boundary Cases | Unspecified behavior when target $\le$ floor or target $>$ max | Missing boundary case definitions | Explicitly bounded: Target $\le$ floor yields 0 penalty; Target $> 	ext{SOC}_{	ext{max}}$ clamped to max | RESOLVED | BOUNDARY_CASES_DEFINED | REQUIRES_IMPLEMENTATION_SPECIFICATION | D11, Math bounds | Calculated |
| CORR_D10_01 | D10 Curtailment | $P_{	ext{curt}} = P_{	ext{curt, necessary}} + P_{	ext{curt, avoidable}}$ presented without status label | Conflated policy principle with executable math | Designated `CONCEPTUAL_DECOMPOSITION_ONLY`; runtime formula marked `D10_EXECUTABLE_CLASSIFICATION = REQUIRES_IMPLEMENTATION_SPECIFICATION` | RESOLVED | CONCEPTUAL_DECOMPOSITION_ONLY | REQUIRES_IMPLEMENTATION_SPECIFICATION | D10, Prompt Sec 6 | Calculated |
| CORR_D8_01 | D8 Fuel vs Reliability | Single fuel constraint equation $\sum 	ext{Fuel} \le F_{	ext{budget}}$ | Conflated physical inventory, budget policy, and exhaustion infeasibility | Separated Physical Inventory ($F_{	ext{rem}} \ge 0$), Budget Policy (Stage 3), and Exhaustion Response (`REQUIRES_GOVERNANCE_CLARIFICATION`) | RESOLVED | PHYSICAL_VS_POLICY_SEPARATED | REQUIRES_IMPLEMENTATION_SPECIFICATION | D08, D14, Prompt Sec 7 | Calculated |
