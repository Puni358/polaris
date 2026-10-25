# HiGHS Solver & Environment Record

This document records the exact runtime environment and solver library versions used for the forensic priority inversion investigation and toy MILP verification.

## Environment Metadata

| Parameter | Recorded Value |
| :--- | :--- |
| **Python Version** | `3.12.3` |
| **SciPy Version** | `1.18.1` |
| **highspy Package Version** | `1.15.1` |
| **HiGHS C++ Engine Version** | `1.15.1` |
| **Operating System** | `Linux` |
| **Solver Output PAGER** | `cat` |

## API Verification Note

The version check was verified directly against the installed C++ dynamic library via Python reflection:
```python
import highspy
h = highspy.Highs()
assert h.version() == "1.15.1"
```
