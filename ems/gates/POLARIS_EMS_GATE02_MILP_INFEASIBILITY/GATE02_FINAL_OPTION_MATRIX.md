# POLARIS GATE-02 — FINAL OPTION MATRIX
## FINAL EVALUATION & DECISION SELECTION MATRIX

---

## 1. OPERATIONAL POLICY OPTION MATRIX

| Option ID & Title | Operational Description | State Advances? | Physical Station Impact | Governance Prerequisites | Final Decision Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OPTION A**<br>Terminate Automatic Optimization | Stop EMS dispatch generation. Hand over control to external physical fallback. | **NO** | Dependent on local microgrid hardware protection. | Requires formal policy specifying hardware fallback setpoints. | **UNGOVERNED / CANDIDATE** |
| **OPTION B**<br>Retry / Re-Solve | Re-attempt optimization solve with altered numerical solver settings. | **NO** (pending) | Holds state step $k$ during solver retry. | Requires technical vs policy retry distinction, max retry count, and timeout limits. | **UNGOVERNED / CANDIDATE** |
| **OPTION C**<br>Governed Constraint Relaxation | Soften non-critical constraints using penalty variables to find feasible dispatch. | **YES** (relaxed) | Dispatches relaxed plan; non-critical load may drop. | Requires formal relaxation hierarchy, priority sequence, and max violation bounds. | **UNGOVERNED / CANDIDATE** |
| **OPTION E**<br>Operator Intervention | Transfer operational dispatch authority to an authorized human operator. | **NO** (auto) | Operator commands dictate station hardware setpoints. | Requires operator interface API, authentication, and manual override audit trail. | **UNGOVERNED / CANDIDATE** |
| **OPTION F**<br>Remain Temporarily Unresolved *(Sealed)* | Retain `GOVERNANCE_DECISION_REQUIRED` while strictly enforcing safety invariants. | **NO** | Holds authoritative `StationState` $k$; blocks state drift. | None required for temporary safety containment. | **SEALED DECISION** |

---

## 2. FAULT RESPONSE LABEL DECISION MATRIX

| Option ID & Title | Description | Code Modifications Required? | Metric & Test Impact | Final Decision Status |
| :--- | :--- | :--- | :--- | :--- |
| **OPTION L1**<br>Retain Temporarily *(Sealed)* | Retain `GOVERNED_ZERO_DISPATCH` as historical metadata only. | **NONE** | Zero downstream breakage; 100% backward compatible. | **SEALED DECISION** |
| **OPTION L2**<br>Authorize Semantically Accurate Label | Replace string with new diagnostic label (e.g. `GOVERNED_STATE_HELD`). | Requires updating `runner.py`, `metrics.py`, and test assertions. | Breaks historical metric filters until downstream audit is completed. | **CANDIDATE FOR FUTURE RELEASE** |

---

## 3. SUMMARY OF SEALED POLICY SELECTIONS

- **Operational Response**: **OPTION F (REMAIN TEMPORARILY UNRESOLVED)**.
- **Fault Response Label**: **OPTION L1 (RETAIN TEMPORARILY)**.
- **Emergency Coupling**: **NO (SEALED REJECTION)**.
- **Unknown Invalid Coupling**: **NO (SEALED REJECTION)**.
- **State Advancement**: **NO (SEALED INVARIANT)**.
