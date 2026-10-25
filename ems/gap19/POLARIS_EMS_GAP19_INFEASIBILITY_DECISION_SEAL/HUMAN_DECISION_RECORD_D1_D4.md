# POLARIS EMS GAP19 — HUMAN DECISION RECORD D1–D4

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Decision Authority**: `HUMAN GOVERNANCE DECISION`  
**Decision Status**: `FINAL_SELECTED_AND_SEALED`  

---

## 1. Decision D1 — J2 / Emergency Reserve Semantics

* **Selected Option**: `HYBRID / MODE-DEPENDENT`
* **Conceptual Behavior**:
  * In **NORMAL** mode, MPC attempts to maintain the governed emergency battery reserve envelope ($E_{\text{stage2\_target}}$).
  * Reserve failure ($J2 > 0$) does **NOT** by itself mean that $J2$ is the emergency detector.
  * Reserve shortfall is represented/measured by $J2$ as an informational and soft penalty metric.
  * Emergency determination belongs exclusively to the governed Emergency Condition Detector (ECD) survivability pathway.
  * Option D is the selected protected-critical-load fallback once emergency handling is invoked by ECD.
* **Numerical Bounds**: Production numerical reserve values are `NOT_ESTABLISHED`.

---

## 2. Decision D2 — $s_{\text{J2}}$ Upper-Bound Policy

* **Selected Option**: `GOVERNED MAXIMUM RESERVE-SHORTFALL BOUND`
* **Status**:
  * `S_J2_BOUND_POLICY = GOVERNED_MAXIMUM_SHORTFALL`
  * `NUMERICAL_VALUE = NOT_ESTABLISHED`
  * `BASIS = STATION_SURVIVABILITY_REQUIREMENT`
  * `CURRENT_200KWH_CAP = IMPLEMENTATION_FACT / NOT_GOVERNED`
* **Directive**:
  * The current implementation-derived $s_{\text{J2}} \le 200,000\text{ Wh}$ cap MUST NOT be treated as governed policy.
  * It MUST NOT be silently preserved as policy, nor silently removed without governance input.
  * The future governed bound must be derived mathematically from station survivability/operational requirements rather than simply nominal battery capacity.

---

## 3. Decision D3 — Emergency Authority

* **Selected Option**: `ECD IS THE EMERGENCY AUTHORITY`
* **Conceptual Separation**:
  * **$J2$**: *"The desired reserve is not fully maintained."* (Informational / Soft penalty)
  * **ECD**: *"Does the station's actual survivability condition constitute an emergency?"* (Emergency Authority)
  * **Option D**: *"What protected-critical-load fallback behavior applies after emergency handling is invoked?"* (Fallback Dispatch Policy)
* **Rule**: $J2 > 0$ **MUST NOT** automatically imply `EMERGENCY = TRUE`.

---

## 4. Decision D4 — MILP Infeasibility Handling

* **Selected Option**: `MILP INFEASIBILITY → ECD ASSESSMENT`
* **Conceptual Path**:
  ```text
  MILP INFEASIBLE
         │
         ▼
  ECD survivability assessment
         │
         ├── survivable / governed non-emergency handling
         │
         └── emergency
                │
                ▼
            Option D fallback
                │
                ▼
        protected critical service
                │
                ▼
        authorized authority escalation
  ```
* **Directive**: When the optimizer returns `OPTIMIZATION_INFEASIBLE`, the solver status itself MUST NOT be treated as the emergency detector. The current zero-dispatch fallback (`GOVERNED_ZERO_DISPATCH`) is NOT accepted as final governed behavior.

---

## 5. Emergency Authority Escalation

* **Selected Option**: `REQUIRED`
* **Rule**: When ECD determines `EMERGENCY = TRUE`, authorized authority / operator escalation is **REQUIRED**.
* **Status**: Emergency escalation is selected conceptually, but concrete mechanisms (communications, auth, watchdogs, acknowledgements) are `NOT_YET_IMPLEMENTED`.
