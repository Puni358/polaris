# POLARIS EMS GAP19 — 409-MODEL OPTION A VS OPTION B EQUIVALENCE EXPERIMENT

This package contains the scientific and computational experiment report comparing the independently constructed Option-A sequential MILP reference against the implemented native HiGHS Option-B solver (`gap19_highs_native.py`) on the canonical 409-variable / 313-constraint POLARIS EMS GAP19 model.

## Key Experimental Results
- **Model Identity**: `A_B_MODEL_IDENTITY = ESTABLISHED` ($N=409, M=313$, Fingerprint `8c0f5a7ea60712401a0cf24eccad1a7cadab0b02c5ba42820cc5b0677c1b08d2`).
- **Feasible Region**: `A_B_FEASIBLE_REGION_EQUIVALENCE = ESTABLISHED` (100% identical $A$ matrix and bounds).
- **Objective Vectors**: `A_B_OBJECTIVE_VECTOR_EQUIVALENCE = ESTABLISHED` (100% identical $c_1, c_2, c_3, c_4$).
- **Forensic Discovery**: Empirical testing of `highspy` revealed that HiGHS interprets larger integer priority numbers as higher lexicographic priority. As implemented (`obj1.priority = 1`, `obj4.priority = 4`), Option B executed priorities in reverse order ($J_4 > J_3 > J_2 > J_1$), causing lexicographic disagreement in regimes where $J_1/J_2$ conflict with $J_3$ (e.g. `DIESEL_REQUIRED`).
- **Priority Alignment Verification**: When HiGHS priorities are set to descending integer order ($100 > 80 > 60 > 40$), Option B achieves **100% EXACT LEXICOGRAPHIC OBJECTIVE EQUIVALENCE** with Option A across all test regimes ($dJ_1 = 0, dJ_2 = 0, dJ_3 \le 10^{-6}$ L, $dJ_4 = 0$).
- **Final Classification**: `A_B_MATHEMATICAL_EQUIVALENCE = NOT_ESTABLISHED` (under implemented code; requires implementation priority ordering correction gate).
