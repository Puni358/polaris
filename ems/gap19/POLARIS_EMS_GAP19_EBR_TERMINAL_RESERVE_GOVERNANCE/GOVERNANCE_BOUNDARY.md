# Governance Boundary Statement

```text
POLICY_DECISIONS_BY_AGENT = ZERO
NUMERICAL_VALUES_SELECTED_BY_AGENT = ZERO
CODE_MODIFICATIONS_PERFORMED = NONE
SCHEMA_MODIFICATIONS_PERFORMED = NONE
SOLVER_EXECUTION_PERFORMED = NONE
```

This package maintains strict role separation:
- **Human Stakeholder:** Decides operational policy, reserve semantics, and numerical values.
- **Engineering Team:** Provides physical asset telemetry and asset limits.
- **Agent/Auditor:** Performs objective static analysis, dataflow tracing, and governance verification.
