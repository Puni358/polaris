# 365D CAMPAIGN ORCHESTRATION & 2-CELL MATRIX SPECIFICATION

## Primary 2-Cell Experiment Matrix Architecture
The primary campaign orchestrator ([`system/orchestration/master.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/orchestration/master.py)) launches exactly two primary experimental cells across parallel workers:

1. **Cell A (`cell_a`) — Simple Diesel-Only Baseline**:
   - Standalone reference execution path in [`system/orchestration/worker.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/orchestration/worker.py).
   - Supplies demand directly from diesel without predictive forecasting or optimization algorithms.
2. **Cell B (`cell_b`) — POLARIS Closed-Loop System**:
   - Full POLARIS EMS closed-loop strategy using `LocalBaselineForecastEngine` + `GAP19HighsNativeOptimizer` / Option B Native HiGHS MILP + `EMSControlRouter` + `OptionDFallbackSolver` + `DigitalTwinSimulator`.

## Infrastructure Features
- **Sleep Inhibition**: Ubuntu Linux `systemd-inhibit` (`--what=idle:sleep`, process-scoped, lid open, display blanking permitted).
- **Worker Allocation**: 2 primary workers (`worker_01` for `cell_a`, `worker_02` for `cell_b`).
- **Checkpointing**: SHA256-chained JSON state snapshots created every 500 steps with 100% bitwise resume equivalence.
- **Deterministic Aggregation**: [`system/orchestration/aggregator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/orchestration/aggregator.py) compiles `PAIRED_COMPARISON_MATRIX_RESULTS.json` evaluating fuel consumption difference ($\Delta L$ and $\%$) and physical metrics.
