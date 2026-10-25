# 1e9 Objective Value Forensics

Forensic analysis of `objective_value = 1e9` in `UNKNOWN_INVALID` mode:

1. **Enters HiGHS?**: NO. Solver execution is bypassed.
2. **Enters J1?**: NO.
3. **Enters J2?**: NO.
4. **Enters J3?**: NO.
5. **Enters J4?**: NO.
6. **Affects Future Optimization?**: NO. The optimizer is stateless per call.
7. **Downstream Control Logic?**: pure reporting field on `DispatchPlan`.

`UNKNOWN_INVALID_SENTINEL_ROLE = REPORTING_ONLY`
