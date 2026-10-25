# POLARIS EMS — GAP19 OPTION B ISOLATED NATIVE HIGHS VALIDATION PACKAGE

## Executive Overview & Navigational Manifest

This package contains the **Independent Isolated Native HiGHS Technical Validation** for **Option B** (Standalone `highspy` / Native Multi-Objective Optimization) prepared for the POLARIS EMS GAP19 human decision-makers.

> [!IMPORTANT]
> **ISOLATION & NEUTRALITY FIREWALL**:
> This validation was executed entirely within a disposable virtual environment outside the POLARIS codebase. Zero POLARIS source files, schemas, configs, or data were touched or executed.
> **This validation establishes technical facts about the highspy/HiGHS package only. It does NOT select Option A or Option B.**

---

## Validation Package Manifest

| File | Technical Topic |
| :--- | :--- |
| [`README.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/README.md) | Package overview, manifest, status register, and neutrality statement. |
| [`ENVIRONMENT_MANIFEST.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/ENVIRONMENT_MANIFEST.md) | Host environment, python venv, and isolated workspace details. |
| [`PYTHON_VERSION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/PYTHON_VERSION.md) | Python runtime version audit (Python 3.12.3 GCC 13.3.0). |
| [`HIGHSPY_VERSION_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/HIGHSPY_VERSION_AUDIT.md) | Pinned `highspy` wheel installation audit (`highspy-1.15.1`). |
| [`HIGHS_VERSION_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/HIGHS_VERSION_AUDIT.md) | Underlying HiGHS C++ engine version audit (`1.15.1`). |
| [`HIGHSPY_PUBLIC_API_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/HIGHSPY_PUBLIC_API_AUDIT.md) | Public API inspection of `highspy.Highs` and `HighsLinearObjective`. |
| [`NATIVE_OBJECTIVE_API_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/NATIVE_OBJECTIVE_API_AUDIT.md) | Method signature audit of `addLinearObjective` and objective structures. |
| [`LEXICOGRAPHIC_MODE_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_OPTION_B_ISOLATED_NATIVE_VALIDATION/LEXICOGRAPHIC_MODE_AUDIT.md) | Audit of `blend_multi_objectives = False` option for strict lexicographic mode. |
| [`PRIORITY_SEMANTICS_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/PRIORITY_SEMANTICS_AUDIT.md) | Audit of C++ priority semantics (Lower integer = Higher priority). |
| [`TOLERANCE_SEMANTICS_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOLERANCE_SEMANTICS_AUDIT.md) | Audit of `abs_tolerance` and `rel_tolerance` fields in `HighsLinearObjective`. |
| [`TOY_MILP_01_SPEC.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_01_SPEC.md) | Specification of Toy MILP 01 (Basic 2-variable integer problem). |
| [`TOY_MILP_01_EXPECTED.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_01_EXPECTED.md) | Analytical mathematical solution for Toy MILP 01. |
| [`TOY_MILP_01_RESULT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_01_RESULT.json) | Empirical JSON execution output for Toy MILP 01 (`[5.0, 5.0]`). |
| [`TOY_MILP_02_PRIORITY_SPEC.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_02_PRIORITY_SPEC.md) | Specification of Toy MILP 02 (Priority discrimination test). |
| [`TOY_MILP_02_PRIORITY_EXPECTED.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_02_PRIORITY_EXPECTED.md) | Analytical solution for Lexicographic vs Blended modes on Toy 02. |
| [`TOY_MILP_02_RESULT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_02_RESULT.json) | Empirical JSON result confirming Lexicographic `[10.0, 0.0]` vs Blended `[1.0, 3.0]`. |
| [`TOY_MILP_03_REVERSED_PRIORITY_SPEC.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_03_REVERSED_PRIORITY_SPEC.md) | Specification of Toy MILP 03 (Reversed priority test). |
| [`TOY_MILP_03_REVERSED_PRIORITY_EXPECTED.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_03_REVERSED_PRIORITY_EXPECTED.md) | Analytical solution for reversed priority order. |
| [`TOY_MILP_03_RESULT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_OPTION_B_ISOLATED_NATIVE_VALIDATION/TOY_MILP_03_RESULT.json) | Empirical JSON result confirming decision vector shift to `[1.0, 3.0]`. |
| [`REPRODUCIBILITY_TEST.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/REPRODUCIBILITY_TEST.md) | Multi-process reproducibility audit across 3 clean process runs. |
| [`THREADING_OBSERVATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/THREADING_OBSERVATION.md) | Solver threading test observation (`threads=1` vs `threads=4`). |
| [`FAILURE_MODE_TEST.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/FAILURE_MODE_TEST.md) | Infeasibility and invalid setup failure handling audit. |
| [`OFFLINE_RUNTIME_TEST.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/OFFLINE_RUNTIME_TEST.md) | Offline local execution verification (`RUNTIME_NETWORK_REQUIRED = NO`). |
| [`PUBLIC_VS_PRIVATE_API.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/PUBLIC_VS_PRIVATE_API.md) | Classification of public `highspy` API vs private SciPy internal modules. |
| [`VERSION_STABILITY.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/VERSION_STABILITY.md) | Version stability analysis for highspy 1.15.1 PyPI wheel. |
| [`OPTION_A_COMPARISON.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/OPTION_A_COMPARISON.md) | Neutral factual comparison table comparing Option A and Option B. |
| [`GAP19_POLARIS_MAPPING.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/GAP19_POLARIS_MAPPING.md) | Structural mapping of GAP19 Stages 1–4 to `highspy` linear objectives. |
| [`LIMITATIONS.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/LIMITATIONS.md) | Boundaries of toy validation vs real POLARIS EMS production requirements. |
| [`HUMAN_DECISION_IMPACT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/HUMAN_DECISION_IMPACT.md) | Impact statement for human decision-makers. |
| [`FINAL_NEUTRAL_VALIDATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/FINAL_NEUTRAL_VALIDATION.md) | Final neutral validation synthesis and verdict (`READY_FOR_HUMAN_DECISION`). |
| [`HASH_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_OPTION_B_ISOLATED_NATIVE_VALIDATION/HASH_AUDIT.json) | Cryptographic SHA-256 fingerprint register for all validation package artifacts. |

---

## Final Validation Status Register

```text
OPTION_B_ISOLATED_VALIDATION_STATUS = PASS
HIGHSPY_INSTALLATION = PASS
HIGHSPY_PUBLIC_API = CONFIRMED
NATIVE_MULTI_OBJECTIVE_MILP = CONFIRMED
LEXICOGRAPHIC_MODE = CONFIRMED
OBJECTIVE_PRIORITY = CONFIRMED
OBJECTIVE_TOLERANCE = QUALIFIED
TOY_MILP_EXECUTION = PASS
PRIORITY_DISCRIMINATION = PASS
REVERSED_PRIORITY_TEST = PASS
REPRODUCIBILITY = PASS
OFFLINE_RUNTIME = PASS
PRIVATE_API_REQUIRED = NO
POLARIS_SOURCE_MODIFIED = NO
POLARIS_RUNTIME_EXECUTED = NO
POLARIS_DATA_USED = NO
POLARIS_FIXTURE_USED = NO
OPTION_A_SELECTED = NO
OPTION_B_SELECTED = NO
GAP19_HUMAN_DECISION = UNDECIDED
```

---

## Final Verdict

```text
READY_FOR_HUMAN_DECISION
```
