# 365D MANDATORY CAMPAIGN STOP CONDITIONS

Execution of the campaign MUST HALT IMMEDIATELY if any of the following occur:
1. **Hash Mismatch**: Any protected component SHA256 checksum differs from sealed pre-flight register.
2. **Truth Leakage**: Any component accesses future ground truth data during optimization step $k$.
3. **State Discontinuity**: Unauthorized reset of battery SOC, diesel running state, or cumulative fuel.
4. **Gate-02 Option C Violation**: Automatic Option D invocation on MILP infeasibility, or Digital Twin advancement on unresolved infeasible state.
5. **Critical Load Drop**: Unmet critical load exceeds 0.0 Wh.
6. **Physical Constraint Breach**: Battery SOC violates 20%-95% boundaries or charge/discharge power exceeds 50 kW.
7. **Source Code Mutation**: Any source file under `system/` is modified during execution.
