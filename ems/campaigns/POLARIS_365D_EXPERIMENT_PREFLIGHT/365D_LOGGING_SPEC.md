# 365D PERSISTENT LOGGING SPECIFICATION

## Log Directory Hierarchy
All execution events are written to persistent log files inside:
`POLARIS_365D_CAMPAIGN_RUN_<ID>/logs/`

- `MASTER.log`: Master process initialization, worker spawning, signal traps, resource warnings, run completion status.
- `WORKER_01.log`: Worker 1 step-by-step progress, optimizer solve times, checkpoint events, warnings.
- `WORKER_02.log`: Worker 2 execution log.
- `WORKER_03.log`: Worker 3 execution log.
- `WORKER_04.log`: Worker 4 execution log.
- `RESOURCE_MONITOR.csv`: Periodic time-series log of CPU, RAM, disk space, and thermal telemetry.

## Log Format Standard
All log entries follow ISO 8601 UTC timestamp format:
`[2024-01-01T00:00:00Z] [worker_01] [cell_1] Saved checkpoint at step 499 -> checkpoint_000499.json`
