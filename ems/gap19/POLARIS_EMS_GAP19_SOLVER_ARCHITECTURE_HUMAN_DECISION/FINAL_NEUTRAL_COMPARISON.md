# FINAL NEUTRAL COMPARISON

## Comprehensive 19-Row Neutral Architecture Comparison Matrix

This document provides a strictly neutral, factual comparison matrix comparing **Option A** and **Option B** across 19 technical, architectural, and operational dimensions.

---

## 19-Row Neutral Comparison Matrix

| # | Comparison Dimension | OPTION A (Sequential Solves via SciPy `milp()`) | OPTION B (Native Solver Multi-Objective) | Evidence / Limitation |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Mathematical Formulation** | Sequential single-objective MILP solves with explicit linear lock constraints ($J_k(x) \le J_k^* + \varepsilon_k$). | Native C++ multi-objective lexicographic vector minimization. | Both solve identical mathematical sub-problems under matching tolerances (`ESTABLISHED_BY_SOURCE`). |
| **2** | **Objective Priority** | Enforced by strict Python execution sequence ($1 \rightarrow 2 \rightarrow 3 \rightarrow 4$). | Enforced by C++ integer priority indices (`priority=1, 2, 3, 4`). | Priority blending risk is zero in A; requires `blend_multi_objectives=False` in B (`ESTABLISHED_BY_SOURCE`). |
| **3** | **Tolerance Handling** | Explicit lock scalars $\varepsilon_k$ appended to constraint matrix between passes. | Native C++ solver fields `abs_tolerance` and `rel_tolerance`. | Option A permits custom Python tolerance rules; Option B uses solver-native tolerances (`ESTABLISHED_BY_SOURCE`). |
| **4** | **MILP Support** | Fully supported across integer, binary, and continuous variables. | Native HiGHS C++ engine supports multi-objective MILP (v1.5+). | Both support MILP variable integrality (`ESTABLISHED_BY_SOURCE`). |
| **5** | **Current Environment Support** | **100% Supported** out-of-the-box via installed SciPy. | **Not Supported** without `highspy` or private SciPy hacks. | `scipy.optimize.milp` in current environment lacks multi-obj params (`ESTABLISHED_BY_SOURCE`). |
| **6** | **Public API Dependency** | Uses standard public API (`scipy.optimize.milp`). | Does not use public SciPy API (Public API lacks multi-obj). | SciPy public API stability contract applies to Option A (`ESTABLISHED_BY_SOURCE`). |
| **7** | **Private API Dependency** | Zero private API dependency. | Requires private `scipy.optimize._highs` if `highspy` absent. | Private APIs are subject to unannounced deprecation (`ESTABLISHED_BY_SOURCE`). |
| **8** | **`highspy` Requirement** | Not required. | Required for official C++ Python class bindings. | `highspy` is not currently installed (`ESTABLISHED_BY_SOURCE`). |
| **9** | **Version Coupling** | Low. Tied to standard SciPy public releases. | High. Tied to specific HiGHS C++ C-API / Cython extension ABI. | Option B requires binary wheel management across releases (`ESTABLISHED_BY_SOURCE`). |
| **10** | **Solver Portability** | High. Can swap underlying solver (e.g. CBC, GLPK) via SciPy. | Low. Tied specifically to HiGHS solver C++ API. | Option A uses solver-agnostic LinearConstraint matrices (`ESTABLISHED_BY_SOURCE`). |
| **11** | **Reproducibility** | Bit-for-bit deterministic across repeated runs. | Bit-for-bit deterministic in C++ if random seeds fixed. | Both achieve determinism under single-threaded execution (`OBSERVED_IN_TOY_EXPERIMENT`). |
| **12** | **Implementation Surface** | $\approx 80\text{--}120$ lines of Python orchestration code. | $\approx 30\text{--}50$ lines of Python setup code. | Option A has larger Python code surface; Option B has larger dependency surface (`ESTABLISHED_BY_SOURCE`). |
| **13** | **Solver Calls per Step** | Exactly 4 solver function calls per MPC step. | 1 solver function call per MPC step. | Option B reduces Python invocation overhead (`ESTABLISHED_BY_SOURCE`). |
| **14** | **Objective Reporting** | Each pass returns explicit float optimal value $J_k^*$. | Requires parsing HiGHS C++ multi-obj attributes or log. | Option A provides immediate Python return values per stage (`ESTABLISHED_BY_SOURCE`). |
| **15** | **Option D Compatibility** | 100% Compatible with `ModeConstraintSet`. | 100% Compatible with `ModeConstraintSet`. | Neither option forces a redesign of Option D (`ESTABLISHED_BY_SOURCE`). |
| **16** | **Schema Impact** | Zero schema changes to `StationState` or `DispatchPlan`. | Zero schema changes to `StationState` or `DispatchPlan`. | Both use identical solver-neutral schemas (`ESTABLISHED_BY_SOURCE`). |
| **17** | **Offline Compatibility** | 100% Offline and locally runnable. | 100% Offline and locally runnable. | Neither option requires internet or license servers (`ESTABLISHED_BY_SOURCE`). |
| **18** | **Failure Modes** | Infeasibility isolated immediately to specific pass $k$. | Infeasibility returned for entire multi-objective solve. | Option A identifies exact failing stage in Python log (`ESTABLISHED_BY_SOURCE`). |
| **19** | **GAP19 Compatibility** | Fully compatible with 4-stage objective hierarchy. | Fully compatible with 4-stage objective hierarchy. | Both satisfy GAP19 mathematical requirements (`ESTABLISHED_BY_SOURCE`). |
