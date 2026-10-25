# Performance Observation

- Option A (4 sequential HiGHS solves): $\approx 0.042$ s total.
- Option B (1 native HiGHS multi-objective solve): $\approx 0.011$ s total.

Observation: Native HiGHS multi-objective Option B is $\approx 3.8\times$ faster than sequential Option A. Recorded for observation only (`A_B_PERFORMANCE_OBSERVATION = RECORDED_ONLY`).
