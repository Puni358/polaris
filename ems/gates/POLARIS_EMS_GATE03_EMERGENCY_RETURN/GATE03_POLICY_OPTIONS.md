# POLARIS GATE-03 — POLICY OPTIONS
## DESCRIPTIVE EVALUATION OF CANDIDATE EMERGENCY RETURN POLICIES

---

## 1. COMPREHENSIVE POLICY OPTION MATRIX

| Option ID & Title | Transition Mechanism (`EMERGENCY → NORMAL`) | Return Prerequisites | Risk & Governance Evaluation | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **OPTION A**<br>Automatic Stateless Return | Instantaneous return on step $k$ when ECD evaluates `NORMAL`. | ECD `OperatingMode.NORMAL` on single timestep. | Current code behavior. High risk of mode chatter/instability near boundary conditions. | **UNGOVERNED / CURRENT CODE** |
| **OPTION B**<br>Governed Automatic Return with Cooldown | Automatic return after $N_{\text{stable}}$ consecutive `NORMAL` steps & SOC hysteresis. | $N_{\text{stable}}$ consecutive `NORMAL` cycles + SOC hysteresis threshold. | Prevents chatter. Requires human governance to define cooldown cycles & thresholds. | **GOVERNANCE_REQUIRED** |
| **OPTION C**<br>Mandatory Operator-Confirmed Return | EMS remains in emergency/protected mode until manual operator reset command. | Operator authorization & manual reset command. | Maximum operational safety; prevents unauthorized auto-resume. Requires operator interface. | **GOVERNANCE_REQUIRED** |
| **OPTION D**<br>Hybrid Governed Return | Automatic return for transient events; mandatory operator reset for deep asset depletion. | Event severity classification + operator reset for deep depletion. | Balances autonomy and safety. Requires complex severity classification policy. | **GOVERNANCE_REQUIRED** |
| **OPTION F**<br>Remain Unresolved *(Baseline)* | Retain `EMERGENCY_RETURN_POLICY = GOVERNANCE_DECISION_REQUIRED`. | Formal Human Governance Decision. | Prevents unauthorized policy implementation prior to project owner decision. | **CURRENT BASELINE** |

---

## 2. DETAILED DESCRIPTIVE ANALYSIS OF OPTIONS

### OPTION A — AUTOMATIC STATELESS RETURN
- **Behavior**: As soon as `ecd.evaluate()` returns `OperatingMode.NORMAL` on step $k$, `router.py` returns `"NORMAL"` and `runner.py` resumes Option B MILP optimization.
- **Flaw**: If fuel or SOC is hovering near the emergency boundary, the system will oscillate between Option B and Option D on alternating timesteps (mode chatter), causing optimization instability and physical wear.

### OPTION B — GOVERNED AUTOMATIC RETURN WITH COOLDOWN
- **Behavior**: System tracks historical state. After entering `EMERGENCY`, system requires ECD to report `NORMAL` for $N$ consecutive timesteps (and SOC to exceed $SOC_{\text{recovery}}$) before re-activating Option B.
- **Governance Requirement**: Numerical values for $N_{\text{stable}}$ and $SOC_{\text{recovery}}$ MUST NOT be invented by developers or AI assistants; they require explicit human governance authorization.

### OPTION C — MANDATORY OPERATOR-CONFIRMED RETURN
- **Behavior**: Entering `EMERGENCY` latches the emergency state. Even if fuel is replenished or demand drops, the system remains in Option D / protected dispatch until an authorized human operator verifies station health and executes a manual return to `NORMAL`.
- **Governance Requirement**: Requires specification of operator interface, control authority, and override protocols.

---

## 3. PROHIBITED AUTOMATED SELECTION STATEMENT

No automated policy selection is made in this document. Selecting between Options A, B, C, D, or F is strictly reserved for the **human project owner**.
