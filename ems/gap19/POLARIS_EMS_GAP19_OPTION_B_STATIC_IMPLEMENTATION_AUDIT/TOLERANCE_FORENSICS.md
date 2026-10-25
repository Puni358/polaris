# Tolerance Forensics

- `abs_tolerance` and `rel_tolerance` on `HighsLinearObjective` objects are set to `0.0`.
- Internal HiGHS solver tolerances (`SOLVER_INTERNAL_TOLERANCE`) govern sub-problem lexicographic tolerance.
- Zero test-only constants (such as 0.01 L or 1e-5) were promoted into governed solver tolerances.

`TOLERANCE_FIREWALL = PASS`
