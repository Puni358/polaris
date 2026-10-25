# PERFORMANCE OBSERVATIONS

## NON-CLAIM RUNTIME OBSERVATIONS

> [!NOTE]
> The runtime observations below are recorded for informational purposes only. No scientific superiority or production scaling claims are made based on this test.

- **Option A Wall-Clock Time (4 passes)**: ~15 ms
- **Option B Wall-Clock Time (1 pass)**: ~4 ms
- **Observations**: Option B requires a single native solver invocation, avoiding Python-level problem re-assembly and solver re-initialization overhead across sequential passes.
