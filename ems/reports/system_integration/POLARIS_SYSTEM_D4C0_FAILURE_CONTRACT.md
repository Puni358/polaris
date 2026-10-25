# POLARIS SYSTEM D4-C0 — FORMAL FAILURE CONTRACT SPECIFICATION (CORRECTED)

**Phase**: D4-C0 — Closed-Loop Runtime Failure Contract Specification  
**Governance Status**: COMPLETED & FROZEN *(Supersedes previous pre-correction draft)*  
**Phase Freeze Status**: **D4-C0 STATUS = FROZEN / APPROVED**  
**Preceding Phases**: D4-A = FROZEN / APPROVED | D4-B = FROZEN / APPROVED  
**Authorization**: SPECIFICATION ONLY — NO D4-C1 CODE IMPLEMENTATION OR TEST EXECUTION AUTHORIZED  

> [!IMPORTANT]
> **CLAIM BOUNDARY**: SYNTHETIC ENGINEERING TEST DATA — NOT REAL NUOLJA MEASUREMENTS.  
> This document specifies the observable software failure-handling contract for the local POLARIS closed-loop microgrid EMS runtime. It does not alter frozen D4-A/D4-B endurance fixtures, research artifacts, or ODD datasets.

---

## 1. DETERMINISM PRECEDENCE & GOVERNANCE RULES

### 1.1 Determinism Criterion Precedence
> **Governance Rule**: **C11 defines the single authoritative deterministic replay standard for D4-C.** Individual acceptance gates MUST NOT impose a stricter, conflicting, or bitwise-log requirement unless explicitly approved as a separate architectural decision.

**Authoritative C11 Replay Criterion**:
> *"Repeated identical fault-injection runs must produce identical failure classifications, governed responses, execution statuses, state transitions, and equivalent reported physical metrics within predefined deterministic tolerances."*

### 1.2 Observable Contract vs. Implementation Mechanism
This C0 contract defines **WHAT** observable failure containment behavior must occur. It does NOT restrict C1 implementation mechanisms (such as specific Python exception class names, internal helper functions, or exact log text) unless strictly necessary to satisfy an observable interface contract.

---

## 2. DECISION TRACEABILITY TABLE

| Architectural Topic | Selected Response / Contract | Governance Rationale |
| :--- | :--- | :--- |
| **MILP Infeasibility** | **`GOVERNED ZERO-DISPATCH DEGRADED STATE`** | Genuine mathematical infeasibility executes an authorized zero-power dispatch ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0, P_{\text{unmet}}=P_{\text{demand}}$), records an explicit `FaultEvent`, advances state via 0-power physics, and completes as `SUCCESS_WITH_GOVERNED_FAULTS`. |
| **Solver Runtime Failure** | **`FAILED_TERMINATED`** | Solver exception, unavailable solver, or numerical crash is classified as `OPTIMIZATION_RUNTIME_FAILURE` and immediately terminates execution with `FAILED_TERMINATED`. *(Must NOT become zero-dispatch)*. |
| **SOC Boundary Excursion** | **`STRICT BOUNDARY TERMINATION`** | If physically calculated next SOC after applying executed dispatch is $< 20\%$ or $> 95\%$, transition is rejected with `FAILED_STATE_VIOLATION` and run terminates immediately with `FAILED_TERMINATED` without clamping or state reset. |
| **Historical SOC Clamping** | **`SUPERSEDED IMPLEMENTATION BEHAVIOR`** | Silent SOC clamping in current simulator identified during D4-C0 audit is classified as historical code behavior to be replaced by strict boundary termination in D4-C1. |
| **Execution Status Model** | **`3-STATE ENUM`** | Formally adopts `SUCCESS_CLEAN`, `SUCCESS_WITH_GOVERNED_FAULTS`, and `FAILED_TERMINATED`. |
| **No Silent Fallback** | **`STRICT PROHIBITION`** | Prohibits Rule-Based substitution, previous-action persistence, fabricated dispatches/forecasts, swallowed exceptions, and reporting `SUCCESS_CLEAN` after faults. |
| **Future-Truth Firewall** | **`STRICT ISOLATION`** | Failure handling logic MUST NOT access hidden future ground truth actuals outside simulator/evaluator contexts. |
| **Offline Isolation** | **`100% OFFLINE ENFORCEMENT`** | Any network access attempt raises an unhandled network error and terminates execution immediately. |

---

## 3. FORMAL SPECIFICATION OF CONTRACT COMPONENTS

### 3.1 MILP Infeasibility vs. Solver Runtime Failure
1. **`OPTIMIZATION_INFEASIBLE`**:
   - Trigger: MILP solver runs to completion and formally establishes that no feasible solution exists (`res.status != 0` after input validation passes).
   - Response: `GOVERNED_ZERO_DISPATCH_DEGRADED_STATE`.
   - Execution: $P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0, P_{\text{served}}=0, P_{\text{unmet}}=P_{\text{demand}}$.
   - Tracking: Logged as a `FaultEvent`. State advances via zero-power physics. Run completes as `SUCCESS_WITH_GOVERNED_FAULTS`.
   - Precise Wording: *"POLARIS permits a governed zero-dispatch degraded response to optimizer infeasibility."* Zero dispatch is NOT described as inherently "safe."
2. **`OPTIMIZATION_RUNTIME_FAILURE`**:
   - Trigger: Solver exception, missing binary library, numerical solver error, or malformed solver output.
   - Response: `FAILED_TERMINATED`. Execution halts immediately; no zero-dispatch substitution permitted.

### 3.2 Strict SOC Boundary Termination
- Normal operation within $[20\%, 95\%]$ SOC is normal execution (not a fault).
- Physical validation rule: The next state SOC ($\text{SOC}_{t+1}$) is calculated using Digital Twin energy transition equations:
  $$E_{t+1} = E_t + \left( \eta_{\text{chg}} P_{\text{chg}} - \frac{P_{\text{dis}}}{\eta_{\text{dis}}} \right) \Delta t$$
- If $\text{SOC}_{t+1} < 20.0\%$ or $\text{SOC}_{t+1} > 95.0\%$:
  - Transition is **REJECTED**.
  - No energy clamping occurs.
  - No state reset occurs.
  - Execution terminates immediately with status `FAILED_TERMINATED` and reason `FAILED_STATE_VIOLATION`.

### 3.3 Approved Execution Status Enum
1. **`SUCCESS_CLEAN`**:
   - All requested $N$ timesteps completed.
   - Zero governed or runtime faults occurred.
   - All physical invariants verified.
2. **`SUCCESS_WITH_GOVERNED_FAULTS`**:
   - All requested $N$ timesteps completed.
   - One or more explicitly authorized governed faults (`OPTIMIZATION_INFEASIBLE`) occurred and executed governed zero-dispatch actions.
   - Every fault was recorded in the execution report.
   - *This status indicates degraded operation and MUST NOT be represented as clean operation.*
3. **`FAILED_TERMINATED`**:
   - Execution halted prior to completing all requested timesteps due to schema rejection, solver runtime failure, SOC boundary violation, or uncaught exception.

### 3.4 FaultEvent Record Contract
When D4-C1 is implemented, every fault MUST record an explicit `FaultEvent` structure:
```json
{
  "timestep": 83,
  "fault_class": "OPTIMIZATION_INFEASIBLE",
  "source": "MILP_OPTIMIZER",
  "severity": "GOVERNED_DEGRADED",
  "response": "GOVERNED_ZERO_DISPATCH",
  "state_advanced": true,
  "message": "Solver established infeasibility; governed zero-dispatch executed."
}
```

### 3.5 State-Continuity Contract Rules
- **Valid Executed Action**: State advances normally according to Digital Twin physical equations.
- **Governed Zero-Dispatch Action**: State advances strictly according to zero-power physics ($P=0$).
- **Rejected Action / Invalid Schema**: Zero state advancement; run terminates.
- **SOC Boundary Violation**: Zero state advancement, zero clamping, zero reset; run terminates.
- **Unhandled Failure**: Zero state advancement; run terminates.

### 3.6 ForecastBundle Interface Contract
The contract enforces validation at the `ForecastEngine` $\rightarrow$ `EnergyOptimizer` execution boundary:
- `horizon_hours == 24` and `len(timestamps) == 24`.
- Parseable timestamps with strict monotonic progression ($t_{k+1} = t_k + 1\text{ h}$).
- `origin_timestamp == timestamps[0]`.
- Compatible schema version.
- Finite numerical values (`!isnan`, `!isinf`) across all arrays.
- Field-specific non-negativity: $SW\_IN \ge 0$, $P_{\text{solar\_gen}} \ge 0$, $P_{\text{wind\_gen}} \ge 0$, $P_{\text{demand}} \ge 0$.
- Interval consistency: $\text{lower} \le \text{point} \le \text{upper}$ and $\text{lower} \le \text{upper}$.

---

## 4. FINAL D4-C ACCEPTANCE GATES

All gates reflect observable behavioral contracts governed by C11 determinism precedence:

| Gate | Category | Falsifiable Pass / Fail Criterion |
| :--- | :--- | :--- |
| **C1** | Deterministic Fault Injection | PASS only if predefined fault injections produce the specified failure classification, governed response, and execution status reproducibly under the C11 deterministic criterion. |
| **C2** | ForecastBundle Boundary Validation | PASS only if malformed `ForecastBundles` (NaN, negative values, unparseable dates) are detected at the defined interface boundary and execution follows the prescribed failure response without fabricated forecasts or unauthorized fallback. |
| **C3** | DispatchPlan Validation | PASS only if invalid `DispatchPlans` are detected at the defined interface boundary and rejected without silent fallback. |
| **C4** | Infeasibility Governed Response | PASS only if genuine MILP infeasibility produces exactly the authorized governed zero-dispatch degraded response and records a `FaultEvent`. |
| **C5** | No Unauthorized Fallback | PASS only if zero Rule-Based substitution, previous-action fallback, fabricated forecast, or swallowed exception occurs. |
| **C6** | Strict SOC Boundary Termination | PASS only if executed transitions attempting to produce $\text{SOC} < 20\%$ or $> 95\%$ terminate execution with `FAILED_STATE_VIOLATION` without clamping, reset, or state advancement. |
| **C7** | State Continuity | PASS only if valid actions and authorized governed zero-dispatch actions advance state according to defined physics, while rejected actions halt state advancement. |
| **C8** | Explicit Execution Status | PASS only if completed runs populate `execution_status` (`SUCCESS_CLEAN`, `SUCCESS_WITH_GOVERNED_FAULTS`, `FAILED_TERMINATED`) correctly. |
| **C9** | Future-Truth Firewall | PASS only if failure-handling routines access zero future ground truth rows. |
| **C10** | Offline Isolation | PASS only if failure-handling routines operate 100% offline. |
| **C11** | Deterministic Replay (AUTHORITATIVE) | PASS only if repeated identical fault-injection runs produce identical failure classifications, governed responses, execution statuses, state transitions, and equivalent reported physical metrics within predefined deterministic tolerances. |
| **C12** | Invariant Preservation | PASS only if all existing frozen physical invariants from D1, D2, D3, D4-A, and D4-B remain satisfied. |
| **C13** | Research / ODD Firewall | PASS only if D4-C introduces zero forecasting research, ODD research, or forecast-error robustness experiments. |

---

## 5. D4-C1 IMPLEMENTATION BOUNDARY

D4-C1 implementation (when explicitly authorized) shall modify ONLY the following components to enforce this contract:

### Code Modules To Modify in D4-C1
- [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) *(Add NaN, timestamp, and field-specific physical bounds validation)*
- [`system/schemas/dispatch_plan.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/dispatch_plan.py) *(Add NaN and physical bounds validation)*
- [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) *(Distinguish `OPTIMIZATION_INFEASIBLE` from `OPTIMIZATION_RUNTIME_FAILURE`)*
- [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py) *(Replace silent SOC clamping with strict boundary check raising `FAILED_STATE_VIOLATION`)*
- [`system/runtime/runner.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/runtime/runner.py) *(Add `FaultEvent` collection and `execution_status` logging)*
- [`system/tests/test_offline_runtime.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/tests/test_offline_runtime.py) *(Add D4-C1 fault-injection regression tests)*

### Prohibited Modifications
- **STRICTLY PROHIBITED**: Modifying D4-A generator or synthetic scenario files.
- **STRICTLY PROHIBITED**: Modifying or rerunning D4-B endurance validation artifacts.
- **STRICTLY PROHIBITED**: Modifying MILP objective weights, tuning solver parameters, or adding heuristic fallback solvers.
- **STRICTLY PROHIBITED**: Introducing forecast-error noise, perturbation experiments, or research dataset imports (reserved for D5).

---

## 6. D4-B IMMUTABILITY CONFIRMATION

```text
D4-A STATUS = FROZEN / APPROVED
D4-B STATUS = FROZEN / APPROVED
```
- Phase D4-C0 is purely additive and subsequent. D4-A and D4-B endurance execution results remain 100% frozen, valid, and immutable.

---

## 7. D4 / D5 BOUNDARY CONFIRMATION

```text
CONFIRMED: D4-C IS STRICTLY CONSTRAINED TO SOFTWARE/RUNTIME FAULT-HANDLING.
```
- **D4-C**: Schema boundary validation, solver error classification, zero-power governed degraded response, SOC strict boundary termination, execution status reporting.
- **D5**: Weather forecast error distributions, irradiance prediction noise, forecast bias sensitivity, EMS physical robustness under noisy predictions.

---

## 8. CONSISTENCY AUDIT & FREEZE VERIFICATION

| Audit Check | Status | Verification Summary |
| :--- | :--- | :--- |
| **1. Determinism Precedence** | **VERIFIED** | C11 established as single authoritative standard; C1 aligned; no bitwise log requirement. |
| **2. Observable Contract** | **VERIFIED** | Implementation-specific mechanisms (e.g. ValueError) replaced with observable boundary criteria. |
| **3. MILP Infeasibility** | **VERIFIED** | `OPTIMIZATION_INFEASIBLE` $\rightarrow$ `GOVERNED_ZERO_DISPATCH_DEGRADED_STATE` across all sections. |
| **4. Solver Runtime Failure** | **VERIFIED** | `OPTIMIZATION_RUNTIME_FAILURE` $\rightarrow$ `FAILED_TERMINATED` across all sections. |
| **5. SOC Boundary Violation** | **VERIFIED** | `FAILED_STATE_VIOLATION` $\rightarrow$ `FAILED_TERMINATED` across all sections. |
| **6. Execution Status Enum** | **VERIFIED** | `SUCCESS_CLEAN`, `SUCCESS_WITH_GOVERNED_FAULTS`, `FAILED_TERMINATED` preserved without alteration. |
| **7. D4-B Immutability** | **VERIFIED** | D4-B endurance results remain 100% frozen & untouched. |
| **8. D4/D5 Boundary** | **VERIFIED** | Forecast error experiments strictly reserved for D5. |
| **9. Zero Code/Simulation Run** | **VERIFIED** | 0 python code files modified, 0 simulations executed during this correction. |

---

## 9. FINAL FREEZE DECLARATION

```text
D4-C0 STATUS = FROZEN / APPROVED
```
*(The previous pre-correction D4-C0 draft is formally superseded by this corrected document.)*

---

### ABSOLUTE HARD STOP
D4-C0 Failure Contract Specification is frozen. No implementation code was written, no tests were added, no simulations were run, D4-A and D4-B remain 100% frozen, and D4-C1 implementation requires separate explicit authorization.
