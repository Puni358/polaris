# MODE VARIABLE MINIMUMITY AUDIT

## AUDIT OF OPERATING MODE REPRESENTATION

- **Authority Rule**: The optimizer MUST NOT decide its own operating mode; mode is determined externally by ECD.
- **Variable Audit**: Operating mode is an external parameter (`config["operating_mode"]`), NOT a set of optimization binary variables.

```text
MODE_VARIABLE_STATUS = EXTERNAL_PARAMETER_SUFFICIENT
MODE_OPTIMIZATION_VARIABLES = 0
```
