# POLARIS GATE-02 — MILP INFEASIBILITY OPTION MATRIX
## EVALUATION OF CANDIDATE OPERATIONAL OPTIONS

---

## 1. COMPREHENSIVE OPTION EVALUATION MATRIX

| Option ID & Title | Summary of Behavior | State Advances? | Physical Station Status | Governance & Technical Evaluation | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OPTION A**<br>Terminate Automatic Optimization | Stop EMS execution, produce no plan, do not advance Digital Twin. | **NO** | Dependent on local microgrid controller / hardware protection relays. | Creates software-hardware divergence. Requires defined operator handover or physical fallback policy. Shares Gate-01 termination ambiguity. | **UNGOVERNED** |
| **OPTION B**<br>Retry / Re-solve Optimization | Re-attempt MILP solve with altered solver tolerances or settings. | **NO** (during retry) | Holds current hardware state until solve completes or times out. | Safe only if solver settings do NOT alter physical constraint semantics. Requires strict distinction between technical retry and policy constraint relaxation. | **UNGOVERNED** |
| **OPTION C**<br>Relax Constraints | Soften non-critical constraints using penalty variables to achieve feasibility. | **YES** (if feasible plan produced) | Follows relaxed dispatch plan. Non-critical load may be shed. | High operational utility, but requires explicit policy defining relaxation hierarchy, maximum violation limits, and critical-load protection bounds. | **UNGOVERNED** |
| **OPTION D**<br>Automatic Option-D Fallback | Immediately route to Option D emergency optimizer upon MILP infeasibility. | **YES** (under Option D) | Operates under emergency heuristic dispatch. | **INVALID / REJECTED**. Infeasibility is a mathematical model artifact, not proof of physical emergency. Conflates model failure with physical crisis. | **REJECTED** |
| **OPTION E**<br>Operator / Manual Intervention | Transfer control to human operator via dedicated interface. | **NO** (automatic) | Operator commands dictate physical dispatch. | Safe in principle, but no operator interface, hardware interlock, or manual recovery protocol currently exists in POLARIS codebase. | **UNGOVERNED** |
| **OPTION F**<br>Remain Unresolved *(Selected)* | Retain `NOT_IMPLEMENTED` & `ENGINEERING_INTERFACE_BLOCKER`. Prohibit state advancement. | **NO** | Static / Hold state. Requires governance decision before runtime deployment. | **SELECTED**. Preserves safety by preventing unauthorized state advancement or incorrect emergency declarations. | **SELECTED** |

---

## 2. DETAILED FORENSIC & GOVERNANCE ANALYSIS BY OPTION

### OPTION A — TERMINATE AUTOMATIC OPTIMIZATION
- **Mechanics**: Upon solver infeasibility, EMS halts pipeline execution. No `DispatchPlan` is published.
- **State Advancement**: `STATE_ADVANCES = NO`. Digital Twin simulator is not stepped.
- **Physical Reality**: The microgrid hardware continues running independently. If no fallback controller exists, generator/battery governors freeze or hardware trips.
- **Governance Finding**: Option A exposes the system to un-governed physical behavior. Like Gate-01, terminating software without a defined physical fallback leaves the hardware in an undefined state.

### OPTION B — RETRY / RE-SOLVE OPTIMIZATION
- **Mechanics**: Re-invoke HiGHS with modified numerical settings (e.g. presolve options, feasibility tolerance `1e-7` → `1e-6`, or solver algorithms).
- **Technical vs. Policy Retry**:
  - *Technical Solver Retry*: Modifying internal solver parameters without altering mathematical problem constraints. Valid technically, but has no guarantee of resolving physical infeasibility.
  - *Policy-Level Relaxation Retry*: Softening constraints (e.g., terminal SOC target). This changes the physical problem and constitutes a governance decision.
- **Governance Finding**: Technical retries can be authorized without policy change, but policy-level retries require Option C governance. No retry budget or timeout currently exists.

### OPTION C — RELAX CONSTRAINTS
- **Mechanics**: Formulate soft constraints with linear/quadratic penalties (e.g. slack variables $\epsilon \ge 0$ on terminal SOC or ramping constraints).
- **Required Policy Specification**:
  1. Priority order of relaxation (e.g., 1. Terminal SOC target $\rightarrow$ 2. Flexible load $\rightarrow$ 3. Generator ramp rates).
  2. Absolute bounds on maximum permissible constraint violation.
  3. Absolute prohibition of critical-load relaxation (Critical Load must remain a hard constraint).
- **Governance Finding**: Constraint relaxation is a **governance policy decision**, not merely an engineering implementation detail. Implementing relaxation without formal policy approval is unauthorized.

### OPTION D — AUTOMATIC OPTION-D FALLBACK
- **Mechanics**: Upon receiving `OPTIMIZATION_INFEASIBLE` from Option B, the system automatically calls `Option D` (emergency optimizer).
- **Flaws & Governance Rejection**:
  1. *Mathematical vs. Physical Reality*: MILP infeasibility can be caused by an overly restrictive forecast input, uncoordinated terminal SOC boundary conditions, or numerical solver issues—NONE of which imply physical danger to the microgrid.
  2. *Bypassing ECD*: Option D is strictly reserved for `EMERGENCY` assessments validated by ECD. Automatically calling Option D on MILP infeasibility bypasses ECD authority and falsely declares a physical emergency.
  3. *Policy Prohibition*: Explicitly rejected under current governance rules (`NO_AUTOMATIC_OPTION_D_ROUTING`).

### OPTION E — OPERATOR / MANUAL INTERVENTION
- **Mechanics**: EMS emits an alert and surrenders dispatch control to an authorized human operator.
- **Requirements**: Requires a real-time operator interface, manual control API, hardware transfer switch, and audit logging system.
- **Governance Finding**: Undefined in software. POLARIS currently lacks an operator interface layer (`MILP_INFEASIBILITY_RUNTIME_INTERFACE = ENGINEERING_INTERFACE_BLOCKER`).

### OPTION F — REMAIN UNRESOLVED (SELECTED FOR GATE-02)
- **Mechanics**: Retain governance status as `GOVERNANCE_DECISION_REQUIRED`. Set `STATE_ADVANCES = NO`. Prohibit automatic execution or state modification.
- **Governance Rationale**: This is the only option that honors all frozen boundaries, prevents false emergency declarations, and avoids un-governed state advancement until an authorized operational response is specified.
