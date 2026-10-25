# Dual HiGHS Runtime Audit

| Runtime | Version | Provider | Status |
| :--- | :--- | :--- | :--- |
| SciPy-bundled HiGHS | 1.12.0 | SciPy 1.18.1 | PASS |
| Native highspy HiGHS | 1.15.1 | highspy 1.15.1 | PASS |

Both native HiGHS engines exist simultaneously in the environment without symbol collisions or memory degradation.
