# POLARIS EMS GAP19 — OPTION B PRIORITY INVERSION FORENSIC ANALYSIS & CORRECTION GATE

## Executive Summary

This package documents the forensic analysis and governance audit for the **POLARIS EMS GAP19 Option B Priority Inversion Correction Gate**.

The recent 409-variable / 313-constraint A-vs-B experiment established that:
1. **Model Identity**: Option A and Option B construct identical 409-variable, 313-constraint MILP formulations (`A_B_MODEL_IDENTITY = ESTABLISHED`).
2. **Feasible Region & Objective Vectors**: Matrix $A$, bounds, integrality, and objective vectors $c_1, c_2, c_3, c_4$ match 100% (`A_B_FEASIBLE_REGION_EQUIVALENCE = ESTABLISHED`, `A_B_OBJECTIVE_VECTOR_EQUIVALENCE = ESTABLISHED`).
3. **Lexicographic Disagreement**: The current Option B implementation (`gap19_highs_native.py`) assigns priorities `1, 2, 3, 4` to objectives $J_1, J_2, J_3, J_4$ respectively. Empirical testing of `highspy` 1.15.1 proved that **larger integer priority values are treated as higher lexicographic priority**.
4. **Priority Inversion**: Consequently, current Option B executes objectives in reverse order ($J_4 > J_3 > J_2 > J_1$), causing severe operational disagreement in regimes such as `DIESEL_REQUIRED` ($J_1=24000\text{ Wh}, J_2=397200\text{ Wh}, J_3=0\text{ L}$ vs Option A $J_1=0\text{ Wh}, J_2=0\text{ Wh}, J_3=17.3652\text{ L}$).
5. **Aligned Priority Validation**: Experimental test runs with descending priorities ($100 > 80 > 60 > 40$) produced 100% exact objective vector equivalence with Option A across all test regimes.

## Required Final Register

```text
HIGHS_PRIORITY_CONVENTION = HIGHER_NUMBER_IS_HIGHER_PRIORITY
CURRENT_J1_PRIORITY = 1
CURRENT_J2_PRIORITY = 2
CURRENT_J3_PRIORITY = 3
CURRENT_J4_PRIORITY = 4
CURRENT_LEXICOGRAPHIC_ORDER = J4 > J3 > J2 > J1
REQUIRED_LEXICOGRAPHIC_ORDER = J1 > J2 > J3 > J4
PRIORITY_INVERSION = YES
DISAGREEMENT_ROOT_CAUSE = HIGHS_PRIORITY_NUMERIC_DIRECTION_INVERSION
OBJECTIVE_VECTORS_REQUIRE_CHANGE = NO
BLEND_MODE_CHANGE_REQUIRED = NO
TOLERANCE_CHANGE_REQUIRED = NO
PROPOSED_PRIORITY_CORRECTION = J1: 4 (or 100), J2: 3 (or 80), J3: 2 (or 60), J4: 1 (or 40)
IMPLEMENTATION_MODIFICATION = NOT_PERFORMED
A_B_EQUIVALENCE_CURRENT_STATUS = NOT_ESTABLISHED
A_B_EQUIVALENCE_AFTER_CORRECTION = REQUIRES_REVALIDATION
NEXT_GATE = IMPLEMENT_PRIORITY_CORRECTION FOLLOWED_BY_STATIC_REAUDIT FOLLOWED_BY_409_MODEL_A_B_REVALIDATION
```

## Package File Index

- `HIGHS_PRIORITY_TOY_PROOF.md`: Empirical proof of HiGHS priority sorting convention.
- `HIGHS_VERSION_RECORD.md`: Environment version details for Python, highspy, and HiGHS engine.
- `CURRENT_PRIORITY_SOURCE_TRACE.md`: Source trace of `gap19_highs_native.py` objective registration.
- `CURRENT_PRIORITY_MAPPING.md`: Semantic mapping of current priorities vs effective HiGHS order.
- `A_B_DISAGREEMENT_FORENSICS.md`: Deep forensic breakdown of DIESEL_REQUIRED disagreement.
- `MULTI_REGIME_PRIORITY_EVIDENCE.md`: Evaluation of aligned priority results across all 3 regimes.
- `CORRECT_PRIORITY_ORDER_SPECIFICATION.md`: Mathematical and semantic specification of required priority order.
- `PRIORITY_NUMERIC_ENCODING_AUDIT.md`: Analysis of valid numeric encodings (e.g. 4,3,2,1 vs 100,80,60,40).
- `OBJECTIVE_WEIGHT_FIREWALL.md`: Audit confirming objective coefficient vectors remain unmodified.
- `TOLERANCE_FIREWALL.md`: Audit confirming objective tolerances remain zero.
- `BLEND_MODE_AUDIT.md`: Audit confirming `blend_multi_objectives = False` is preserved.
- `OPTION_A_REFERENCE_PRESERVATION.md`: Verification that Option A reference solver remains unedited.
- `PROPOSED_SOURCE_CORRECTION.md`: Exact code diff specification for the upcoming code modification gate.
- `CORRECTION_IMPACT_ANALYSIS.md`: Impact assessment of priority correction on solver behavior.
- `REVALIDATION_PLAN.md`: Protocol for static audit and 409-model revalidation following code change.
- `CORRECTION_REGISTER.md`: Tabular correction register of audited issues.
- `FINAL_PRIORITY_CORRECTION_VERDICT.md`: Official verdict and key-value governance declaration.
- `HASH_AUDIT.json`: SHA-256 integrity hash audit for all package artifacts.
