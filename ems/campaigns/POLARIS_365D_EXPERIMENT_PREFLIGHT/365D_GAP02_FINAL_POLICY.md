# 365D GATE-02 OPTION C FINAL POLICY SPECIFICATION

## Governed Human Policy Status
- **Sealed Policy Designation**: `GATE02_HUMAN_DECISION = OPTION_C`
- **Governance Policy Status**: `GATE02_POLICY_STATUS = SEALED`
- **Mid-Campaign Human Decision Required**: `GATE02_MID_CAMPAIGN_HUMAN_DECISION_REQUIRED = FALSE`

## Hard Constraints (Never Relaxed)
1. **Critical Load**: Compulsory ($P_{\text{demand\_critical}}$). Never shed, degraded, or relaxed by Gate-02 under any circumstance.
2. **Physical Bus-Bar Power Balance**: Active power supply equals active power demand plus charge and flexible demand at every hour $t$.
3. **Physical Battery Safety Limits**: $E_{\text{battery}} \in [E_{\text{min}}, E_{\text{max}}]$, max charge/discharge power limits.
4. **Physical Generator Safety Limits**: $P_{\text{diesel}} \in [P_{\text{min}}, P_{\text{max}}]$ when active.

## Deterministic Option C Relaxation Hierarchy & Re-Solve Flow
1. **Initial MILP Execution**: Native HiGHS lexicographic solver optimizes $J_1 \to J_2 \to J_3 \to J_4$.
   - If initial MILP is `OPTIMAL`: Adopts valid dispatch plan.
2. **Option C Governed Relaxation Re-Solve**:
   - If initial MILP returns `OPTIMIZATION_INFEASIBLE`:
   - Preserves compulsory hard critical load.
   - Executes Option C governed relaxation pass on noncritical flexible load bounds.
   - Re-solves the MILP model.
3. **Re-Solve Outcome Handling**:
   - **If Re-Solve is FEASIBLE (`OPTIMAL`)**:
     - Emits machine-readable operator relaxation event (`GATE02_EVT_<run_id>_<cell>_k<step>`).
     - Adopts valid relaxed dispatch plan.
     - Digital Twin advances normally.
   - **If Re-Solve is STILL INFEASIBLE**:
     - Execution halts fail-closed (`status = "BLOCKED_INFEASIBLE"`).
     - **NO** further invented relaxations.
     - **NO** zero-dispatch execution.
     - **NO** automatic Option D invocation.
     - **NO** Digital Twin advancement.
