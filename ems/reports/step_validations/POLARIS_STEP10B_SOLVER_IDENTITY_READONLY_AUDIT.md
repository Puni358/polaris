# POLARIS Step 10B: Solver Identity Read-Only Audit

## Executive Summary

A static, read-only code path audit of the frozen H1.0 hybrid runtime entry point was performed to verify the actual MILP solver identity prior to trajectory execution.

- **Classification:** **`C — GOVERNANCE MISMATCH`**
- **Declared Solver in Step 10B Text (G17):** `PULP CBC`
- **Actual Solver in Source Code:** `scipy.optimize.milp` (SciPy / HiGHS C++ solver)
- **Optimizer Source File:** [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris (Copy)/system/optimization/implementations/milp.py)
- **Optimizer Source Hash:** `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` (**`PASS`** — matches protected baseline)
- **MILP Solves Executed During Audit:** `0`
- **Simulator Steps Executed During Audit:** `0`
- **Execution Authorization Status:** **`HOLD`**

---

## 1. Execution Entry Point & Code Path Trace

1. **Entry Point:** [`system/runtime/runner.py`](file:///home/punith-bs/01polaris (Copy)/system/runtime/runner.py) (`PolarisLocalRunner.run_pipeline`)
2. **Optimizer Instantiation:** `PolarisLocalRunner.__init__()` instantiates `LocalMILPEnergyOptimizer()`.
3. **Optimizer Invocation:** `PolarisLocalRunner.run_pipeline()` calls `self.optimizer.optimize(bundle, current_state, self.configs)`.
4. **Solver Invocation:** Inside [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris (Copy)/system/optimization/implementations/milp.py):
   - **Line 9:** `from scipy.optimize import milp, LinearConstraint, Bounds`
   - **Line 283:** `res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)`

The execution path directly calls **`scipy.optimize.milp`**, which invokes the **HiGHS** C++ MILP solver embedded within SciPy. No calls to `pulp` or `PULP_CBC_CMD` exist anywhere in the `system/` runtime codebase.

---

## 2. Governance Mismatch Rationale

- **Discrepancy:** The Step 10B authorization gate G17 text stated: `"G17_solver_runtime_config_frozen = PULP CBC"`. However, the protected frozen optimizer source code (`system/optimization/implementations/milp.py`, SHA-256 `ee913b68...`) statically invokes `scipy.optimize.milp` (HiGHS).
- **Classification:** Per governance rules, when the authorization text states `CBC` but the execution path uses another solver (`scipy.optimize.milp`), the audit must be classified as **`C — GOVERNANCE MISMATCH`**.
- **Governance Action:** No code or configuration files were modified. The trajectory execution remains **`NOT_EXECUTED`** and authorization is placed on **`HOLD`** until the G17 authorization text is formally reconciled to reference `scipy.optimize.milp (HiGHS)`.

---

## 3. Detailed Audit Matrix

```plain
SOLVER_IDENTITY_CLASSIFICATION = C
DECLARED_SOLVER = PULP CBC
ACTUAL_SOLVER = scipy.optimize.milp (HiGHS)
SOLVER_CLASS = scipy.optimize.milp
SOLVER_SOURCE_FILE = system/optimization/implementations/milp.py
SOLVER_SOURCE_LINE = Line 9 & Line 283
OPTIMIZER_SOURCE_HASH = ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35
OPTIMIZER_HASH_MATCH = PASS
RUNTIME_SOLVER_SELECTION = Hardcoded scipy.optimize.milp
H10_ADAPTER_SOLVER_EFFECT = NONE
SOLVER_FALLBACK_PRESENT = NO
FALLBACK_AUTHORIZED = NOT_APPLICABLE
SOLVER_ENVIRONMENT_AVAILABLE = PASS
MILP_SOLVES_DURING_AUDIT = 0
SIMULATOR_STEPS_DURING_AUDIT = 0
SOURCE_FILES_MODIFIED = NO
CONFIGURATION_MODIFIED = NO
AUTHORIZATION_MODIFIED = NO
H1.0_FIXTURE_MODIFIED = NO
STEP10B_EXECUTION_STATUS = NOT_EXECUTED
STEP10B_EXECUTION_AUTHORIZATION = HOLD
```

---

## 4. Final Decision & Required Action

```plain
STEP10B_SOLVER_IDENTITY = DISCREPANCY_IDENTIFIED
STEP10B_EXECUTION_AUTHORIZATION = HOLD
```

**Required Governance Action:**
Formally update the Step 10B authorization gate G17 description from `PULP CBC` to `scipy.optimize.milp (HiGHS)` via a governance text amendment. Once G17 text agrees with the protected on-disk solver implementation, execution authorization can be re-validated.
