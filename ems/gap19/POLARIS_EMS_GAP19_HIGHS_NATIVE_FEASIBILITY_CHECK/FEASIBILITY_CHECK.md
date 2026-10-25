# POLARIS GAP19 — FINAL HiGHS NATIVE MILP FEASIBILITY CHECK REPORT

**Phase**: GAP19 Solver Architecture Feasibility Inspection  
**Audit Date**: 2026-09-22  
**Status**: COMPLETED (READ-ONLY)  
**Scope**: Factual inspection of bundled SciPy HiGHS binary capabilities, Option B compatibility, tolerance semantics, and governance blockers.

---

## 1. Executive Summary & Required Final Classifications

This report provides the final neutral feasibility assessment of **Option B (Native HiGHS Lexicographic Multi-Objective)** for the POLARIS Predictive Energy Management System (EMS).

### Governed Final Classifications

| Metric | Governed Classification | Justification |
| :--- | :--- | :--- |
| **`HIGHS_NATIVE_MILP_MULTI_OBJECTIVE`** | **`CONFIRMED_BUT_QUALIFIED`** | Bundled HiGHS 1.12.0 C++ engine natively supports lexicographic multi-objective MILP via `_Highs` pybind11 methods (`addLinearObjective`), but requires `blend_multi_objectives=False` and is qualified by lack of public `scipy.optimize.milp()` support and uninstalled standalone `highspy`. |
| **`POLARIS_OPTION_B_TECHNICAL_FEASIBILITY`** | **`ESTABLISHED_WITH_VERSION_DEPENDENCY`** | Option B is technically feasible using SciPy 1.18.1+ (bundled HiGHS 1.12.0+), but depends on accessing private bindings (`scipy.optimize._highspy._core`) or adding standalone `highspy` to project dependencies. |
| **`MATHEMATICAL_TRANSFER`** | **`UNCHANGED_WITH_DEFINED_CONDITIONS`** | POLARIS 360-variable MILP constraints transfer without alteration, but transfer is conditional on resolving Stage 2 EBR formulation, battery degradation placement, and tolerance mapping. |

---

## 2. Categorized Evidence Summary

To ensure governance clarity, all findings are explicitly categorized under strict evidence classifications.

### A. VERIFIED FACT (Direct Empirical Evidence)
1. **SciPy Version**: SciPy version `1.18.1` is installed in the active POLARIS Python environment.
2. **Bundled HiGHS Engine**: The bundled C++ engine inside SciPy 1.18.1 is HiGHS version `1.12.0`.
3. **Standalone highspy Package**: Standalone `highspy` is **NOT installed** in the environment.
4. **Internal PyBind11 Bindings**: `scipy.optimize._highspy._core` exposes `_Highs` class methods:
   - `addLinearObjective()`
   - `clearLinearObjectives()`
   - `getNumLinearObjectives()`
   - `getLinearObjective()`
5. **Objective Struct Attributes**: `HighsLinearObjective` exposes `coefficients`, `weight`, `offset`, `abs_tolerance`, `rel_tolerance`, and `priority`.
6. **Public API Restriction**: `scipy.optimize.milp()` exposes only a single linear objective vector `c` and does not accept multi-objective parameters.
7. **Blending Default**: `HighsOptionsManager` confirms option `blend_multi_objectives` exists and defaults to `True` (blending mode).
8. **POLARIS MILP Scale**: POLARIS MILP problem structure comprises 360 decision variables and 12 constraint families.

### B. DOCUMENTED CAPABILITY (Verified via Official HiGHS Documentation / Engine Specification)
1. **Lexicographic Multi-Objective MILP**: HiGHS 1.12.0 supports lexicographic multi-objective optimization for LP and MILP problems.
2. **Quadratic Limitation Non-Applicability**: HiGHS multi-objective documentation notes QP (quadratic objective) restrictions, but POLARIS EMS is a pure MILP (linear objective with binary/continuous variables), making QP restrictions irrelevant.
3. **Multi-Objective Blending Control**: Setting `blend_multi_objectives = False` switches HiGHS multi-objective handling from weighted-sum blending to strict lexicographic priority optimization.

### C. INFERENCE (Deducted Technical Behavior)
1. **Internal API Access Route**: Option B can be invoked without installing standalone `highspy` by directly utilizing SciPy's private `scipy.optimize._highspy._core._Highs` wrapper, though this introduces a dependency on private internal APIs.
2. **Tolerance Delegation**: In Option B, intermediate objective degradation tolerances during lexicographic solves are delegated to HiGHS internal branch-and-bound cut generator via `abs_tolerance` and `rel_tolerance`.

### D. NOT YET VERIFIED (Empirical or Mapping Gaps)
1. **Tolerance Semantics Mapping**: Exact native HiGHS MILP objective tolerance semantics (`abs_tolerance`, `rel_tolerance`) must be mapped to POLARIS priority/tolerance requirements.
2. **Empirical Solver Equivalence**: No empirical A-vs-B performance or numerical equivalence test has been run on actual POLARIS operational datasets.

### E. GOVERNANCE BLOCKER (Unresolved Formulation or Governance Issues)
1. **Stage 2 EBR / Terminal Reserve Formulation**: Stage 2 Emergency Battery Reserve (EBR) and terminal reserve objectives are missing from the current POLARIS MILP code. This is a governance/formulation issue that affects **BOTH Option A and Option B**.
2. **Battery Degradation Objective Placement**: Placement of battery degradation terms across the priority stages remains unresolved in POLARIS specifications.

---

## 3. Detailed Technical Assessment of Option B

### 3.1 Interface & Access Architecture
Native multi-objective functionality in HiGHS requires passing multiple objective vectors with assigned priorities. 
Currently, POLARIS calls `scipy.optimize.milp()`. Two implementation paths exist for Option B:

```
[Path B1: Standalone highspy] (NOT INSTALLED)
  POLARIS Optimizer -> highspy.Highs() -> HiGHS 1.12.0 Engine

[Path B2: SciPy Private Binding Bypass] (VERIFIED IN SCI PY 1.18.1)
  POLARIS Optimizer -> scipy.optimize._highspy._core._Highs() -> HiGHS 1.12.0 Engine
```

Path B1 requires dependency installation governance approval. Path B2 uses existing binaries but relies on an internal SciPy module (`_highspy._core`).

### 3.2 Lexicographic vs. Blended Configuration
In HiGHS 1.12.0, multi-objective optimization defaults to blended mode (`blend_multi_objectives = True`). If unconfigured, HiGHS will sum the weighted objectives into a single objective rather than solving them lexicographically. 
For Option B to achieve true lexicographic behavior matching POLARIS requirements, `blend_multi_objectives` must be explicitly set to `False`.

### 3.3 Tolerance and Priority Semantics
HiGHS native lexicographic optimization uses the `HighsLinearObjective` struct:
- `priority`: Integer priority level (0 = highest priority, matching Stage 1).
- `weight`: Intra-stage scalar multiplier.
- `offset`: Stage-specific constant scalar offset.
- `abs_tolerance` / `rel_tolerance`: Allowed degradation of higher-priority objective values in lower-priority solve stages.

In Option A (Sequential MILP), objective degradation bounds are enforced via explicit RHS constraint updates ($c_k^T x \le z_k^* + \epsilon$). In Option B, these are enforced within the HiGHS solver engine. Exact mapping and numerical verification between these two approaches remain an open item.

---

## 4. Summary of Unresolved Items

1. **Native HiGHS Tolerance Mapping**: Exact native HiGHS MILP objective semantics must be mapped to POLARIS tolerance/priority requirements.
2. **Stage 2 EBR Formulation**: Stage 2 EBR/terminal-reserve formulation remains a governance/formulation issue for **BOTH A and B**.
3. **Degradation Objective Placement**: Battery degradation objective placement across priority stages remains unresolved.
4. **API Access Path**: Option B requires an implementation path exposing the underlying `_Highs` API or installing `highspy`, rather than `scipy.optimize.milp()`.
5. **Standalone Package Installation**: Standalone `highspy` installation has **NOT** been performed.
6. **Empirical Testing**: No A-vs-B empirical equivalence test has been performed.

---

## 5. Non-Selection & Neutrality Affirmation

- Option B is **NOT declared better or preferred** over Option A.
- Option A and Option B are **NOT ranked or scored**.
- Implementation readiness is **NOT claimed** for either option.
- The final choice between Option A (Sequential MILP via public SciPy API) and Option B (Native HiGHS Multi-Objective) remains strictly with the human governance project owner.
