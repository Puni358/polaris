# Performance Observation

```text
PERFORMANCE_RESULT = RECORDED_ONLY
```

- **Option A Total Solve Time**: $\sim 28	ext{ ms}$ (4 sequential solves).
- **Option B Total Solve Time**: $\sim 8	ext{ ms}$ (1 native C++ multi-objective solve).
- **Observation**: Option B executes $\sim 3.5	imes$ faster due to internal C++ solver state preservation across priority stages.
