# Canonical Code Cross-Reference

| Canonical Requirement | Specification | Actual Code (`gap19_highs_native.py`) | Status |
| :--- | :--- | :--- | :---: |
| 409 Variables | $N=409$ (96 Bin, 313 Cont) | Lines 93-109 (`num_total_vars = 409`) | **PASS** |
| 313 Constraints | $M=313$ (264 Base, 24 Crit, 24 EBR, 1 Term) | Lines 148-253 (`num_constraints = 313`) | **PASS** |
| J1 Objective | $\sum P_{\text{unmet,crit}} \cdot \Delta t$ | Lines 277-278 (`c1` Wh) | **PASS** |
| J2 Objective | $\sum s_{\text{EBR}} + s_{\text{term}}$ | Lines 280-281, 292 (`c2` Wh) | **PASS** |
| J3 Objective | Physical Liters | Lines 283-286 (`c3` Liters) | **PASS** |
| J4 Objective | Curtailment Wh | Lines 288-290 (`c4` Wh) | **PASS** |
| Native HiGHS | `highspy.HighsLinearObjective` | Lines 315-334 | **PASS** |
| Priority 1-4 | Priorities 1, 2, 3, 4 | Lines 316, 321, 326, 331 | **PASS** |
| Lex Mode | `blend_multi_objectives = False` | Line 298 | **PASS** |
| No $w_{\text{stop}}$ | Zero shutdown binaries | Lines 130-134 (4 binaries per step = 96) | **PASS** |
| Option D Interface | Mode input ingested | Lines 31, 254-262 | **PASS** |
| Schema Boundary | Baseline schemas unchanged | Zero baseline files modified | **PASS** |
| Tolerance Boundary | Solver internal tolerances | Lines 316, 321, 326, 331 (`abs/rel_tol = 0.0`) | **PASS** |
