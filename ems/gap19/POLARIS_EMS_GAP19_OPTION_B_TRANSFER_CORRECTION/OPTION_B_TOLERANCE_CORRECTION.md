# OPTION B TOLERANCE CORRECTION

## Classification of Native HiGHS Objective Tolerances

This document classifies native HiGHS `HighsLinearObjective.abs_tolerance` and `rel_tolerance` parameters.

---

## Classification Specification

```text
abs_tolerance, rel_tolerance = SOLVER_CONFIGURATION_PARAMETERS
STATUS = REQUIRES_ENGINEERING_DEFINITION
```

### Key Technical Rule:
HiGHS native solver attributes `abs_tolerance` and `rel_tolerance` are **SOLVER CONFIGURATION PARAMETERS**.

They MUST NOT be assumed to be automatically identical to POLARIS lock parameters $\varepsilon_k$ without explicit mathematical equivalence demonstration.
