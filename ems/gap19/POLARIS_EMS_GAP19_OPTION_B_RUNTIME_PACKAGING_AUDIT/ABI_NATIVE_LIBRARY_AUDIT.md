# ABI & Native Library Audit

- **SciPy Binary**: `scipy/optimize/_highspy/_highs_wrapper.cpython-312-x86_64-linux-gnu.so`
- **highspy Binary**: `highspy/highs_bindings.cpython-312-x86_64-linux-gnu.so`
- **Linkage**: Both use hidden symbol visibility (`-fvisibility=hidden`) for C++ symbols, preventing ABI name mangling conflicts.
