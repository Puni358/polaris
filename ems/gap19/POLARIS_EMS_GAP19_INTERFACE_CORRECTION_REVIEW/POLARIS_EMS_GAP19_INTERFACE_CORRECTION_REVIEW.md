# POLARIS — GAP19 SOLVER ARCHITECTURE & EMS INTERFACE IMPACT
## Correction and Verification Review (Narrow Governance Correction Phase — Read-Only)

**Governance Document ID**: `POLARIS_EMS_GAP19_INTERFACE_CORRECTION_REVIEW`  
**Correction Status**: `CORRECTION_REQUIRED`  
**GAP19 Solver Architecture Status**: `REQUIRES_GOVERNANCE_DECISION`  
**Current SciPy MILP Capability**: `VERIFIED`  
**Native Multi-Objective API**: `NOT_EXPOSED_BY_CURRENT_API`  
**Sequential Lexicographic Architecture**: `TECHNICALLY_FEASIBLE`  
**Option C Status**: `ENGINEERING_RISK_ONLY`  
**Schema Impact Status**: `ADDITIVE_EXTENSION_REQUIRED`  

---

## 1. Locked Governance Status & Absolute Firewall

```
STAKEHOLDER_POLICY = HUMAN_APPROVED
OBJECTIVE_SPECIFICATION_GOVERNANCE = PASS
CURRENT_EMS_IMPLEMENTATION = FROZEN
MILP_IMPLEMENTATION = FROZEN

IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
CODE_MODIFICATION = NOT_AUTHORIZED
OPTIMIZER_MODIFICATION = NOT_AUTHORIZED
OBJECTIVE_COEFFICIENT_MODIFICATION = NOT_AUTHORIZED

EMS_EXECUTION = NOT_AUTHORIZED
MPC_EXECUTION = NOT_AUTHORIZED
DIGITAL_TWIN_EXECUTION = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
MODEL_MODIFICATION = NOT_AUTHORIZED
FORECASTING_MODIFICATION = NOT_AUTHORIZED
```

---

## 2. Issue A — GAP19 Solver Architecture Audit & Capability Verification

### A1. Authoritative History Audit
Inspection of historical governance records (`POLARIS_EMS_IMPLEMENTATION_SPECIFICATION_REVIEW_V2.md`, `POLARIS_EMS_IMPLEMENTATION_AUTHORIZATION_READINESS_REVIEW/`) confirms:
- GAP19 solver realization (4-pass sequential MILP vs solver-native lexicographic vs penalty weights) was explicitly classified as **`IMPLEMENTATION_DEFERRED`**.
- GAP19 has **NOT** been resolved by any prior governance decision and remains an open architecture question.
- Status:
  $$ \text{GAP19\_SOLVER\_ARCHITECTURE} = \mathbf{REQUIRES\_GOVERNANCE\_DECISION} $$

### A2. Static Audit of Installed SciPy / HiGHS Stack
- **Installed Version**: `scipy 1.18.1`
- **Current Python API**: `scipy.optimize.milp(c, *, integrality=None, bounds=None, constraints=None, options=None)`
- **Capability Breakdown**:
  - `HIGH_LEVEL_SOLVER_CAPABILITY`: HiGHS C++ solver engine supports multi-objective optimization natively in C++ API.
  - `CURRENT_PYTHON_API_CAPABILITY`: `scipy.optimize.milp` exposes only a **single 1D cost vector `c`**. Native lexicographic priority parameters are **NOT EXPOSED** by the current SciPy Python interface.
  - `CURRENT_POLARIS_IMPLEMENTATION_CAPABILITY`: `LocalMILPEnergyOptimizer` (`milp.py`) passes a single composite scalar vector `c`.

### A3. Candidate Option Verification
1. **Option A (Sequential 4-Pass MILP Solves)**:
   - *Classification*: `TECHNICALLY_FEASIBLE`.
   - *Verification*: Static analysis confirms `scipy.optimize.milp` can support sequential solves ($J_1^* 	o J_2^* 	o J_3^* 	o J_4^*$) if an external solver orchestration layer generates linear equality/inequality lock constraints ($J_k(x) \le J_k^* + \epsilon_k$) between passes.
2. **Option B (Solver-Native Lexicographic API)**:
   - *Classification*: `NOT_EXPOSED_BY_CURRENT_API` / `EXTERNAL_SOLVER_DEPENDENCY_REQUIRED`.
   - *Verification*: Not supported by standard `scipy.optimize.milp 1.18.1`. Would require direct C++ bindings or external multi-objective solver libraries (e.g., Gurobi / CPLEX).
3. **Option C (Exponential Penalty Encoding)**:
   - *Classification*: `ENGINEERING_RISK_ONLY`.
   - *Verification*: High risk of numerical ill-conditioning and priority leakage ($10^12$ vs $1$). Preserved as an engineering risk finding, **NOT** a governance rejection.

---

## 3. Issue B — Interface & Schema Impact Audit

The previous claim `NO_SCHEMA_CHANGE_REQUIRED` was audited for semantic completeness. While existing Version 1.0.0 schemas (`ForecastBundle`, `StationState`, `DispatchPlan`) can technically execute baseline single-demand dispatch, full realization of the governed V2 objective without semantic degradation requires **`ADDITIVE_EXTENSION_REQUIRED`**:

### B1. ForecastBundle Semantic Audit
- **Current Fields**: `solar_irradiance`, `solar_generation`, `wind_generation`, `demand` (single composite demand vector).
- **Future Requirement**: 5-tier demand vector breakdown (`critical_demand`, `essential_demand`, `deferrable_demand`, `interruptible_demand`, `noncritical_demand`).
- **Audit Verdict**: Repurposing `demand.point` for Critical tier only would alter its baseline semantics. An additive schema extension or structured metadata payload is required for 5-tier demand. (`ADDITIVE_EXTENSION_REQUIRED`).

### B2. StationState Semantic Audit
- **Current Fields**: `battery_energy_wh`, `diesel_running`, `diesel_hours_running`, `last_observed_*`.
- **Future Requirement**: Fuel inventory remaining ($V_{\text{fuel,rem}}$), dynamic EBR target ($E_{\text{EBR,target}}$), and operating mode state.
- **Audit Verdict**: `ADDITIVE_EXTENSION_REQUIRED` for full multi-mode operational state tracking.

### B3. DispatchPlan Semantic Audit
- **Current Fields**: Composite `load_served`, `unmet_load`, `renewable_curtailment`.
- **Future Requirement**: 5-tier load served/unmet vectors, Stage 1–4 objective values ($J_1^*, J_2^*, J_3^*, J_4^*$), and avoidable vs necessary curtailment breakdown.
- **Audit Verdict**: `ADDITIVE_EXTENSION_REQUIRED` for governed diagnostic reporting.

### B4. Schema Impact Conclusion
- Previous Claim: `NO_SCHEMA_CHANGE_REQUIRED`
- Corrected Claim: **`ADDITIVE_EXTENSION_REQUIRED`** (Additive fields maintain 100% backward compatibility with Version 1.0.0 defaults while enabling full V2 governed semantics).

---

## 4. Final Governance Status Block

```
GAP19_SOLVER_ARCHITECTURE = REQUIRES_GOVERNANCE_DECISION
CURRENT_SCIPY_MILP_CAPABILITY = VERIFIED
NATIVE_MULTIOBJECTIVE_API = NOT_EXPOSED_BY_CURRENT_API
SEQUENTIAL_LEXICOGRAPHIC_ARCHITECTURE = TECHNICALLY_FEASIBLE
OPTION_C_STATUS = ENGINEERING_RISK_ONLY

FORECASTBUNDLE_SCHEMA = ADDITIVE_EXTENSION_REQUIRED
STATIONSTATE_SCHEMA = ADDITIVE_EXTENSION_REQUIRED
DISPATCHPLAN_SCHEMA = ADDITIVE_EXTENSION_REQUIRED

SEMANTIC_REUSE = PASS
UNIT_COMPATIBILITY = PASS
TIME_BASIS_COMPATIBILITY = PASS
BACKWARD_COMPATIBILITY = PASS

NO_SCHEMA_MODIFICATION = YES
NO_SOLVER_SELECTION = YES
NO_IMPLEMENTATION = YES

MILP_MODIFIED = NO
EMS_EXECUTED = NO
MPC_EXECUTED = NO
DIGITAL_TWIN_EXECUTED = NO
MODEL_MODIFIED = NO
FORECASTING_MODIFIED = NO

HASH_INTEGRITY = PASS
PROTECTED_ARTIFACT_INTEGRITY = PASS
EXECUTION_FIREWALL = PASS

CORRECTION_STATUS = CORRECTION_REQUIRED

NEXT_GOVERNED_STEP = GAP19_SOLVER_ARCHITECTURE_GOVERNANCE_DECISION
```
