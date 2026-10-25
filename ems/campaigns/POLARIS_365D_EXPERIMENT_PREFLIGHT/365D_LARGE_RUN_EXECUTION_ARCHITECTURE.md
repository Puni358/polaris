# 365D LARGE-RUN EXECUTION ARCHITECTURE & GOVERNANCE

## Architectural Purpose & Scope
This document specifies the execution infrastructure built for conducting long-running, reproducible closed-loop annual microgrid EMS experiments without risking data loss, silent state corruption, or unrecoverable process crashes.

## Core Architectural Components
1. **Master Orchestrator Process (`CampaignMaster`)**: Coordinates worker process pool, directory setup, signal traps, terminal progress rendering, and run completion status.
2. **Worker Process Model (`CampaignWorker`)**: Multi-process worker instances (`worker_01` .. `worker_04`) executing assigned experiment cells sequentially across closed-loop timesteps ($k 	o k+1$).
3. **Checkpoint & Resume Engine (`CheckpointManager`)**: Manages SHA256-chained JSON state checkpoints (`checkpoint_000500.json`) every 500 steps, enforcing strict integrity validation prior to resumption.
4. **Live Terminal Monitor (`TerminalProgressRenderer`)**: Renders real-time local terminal ASCII dashboard showing per-cell completion percentages, active workers, cumulative fuel, RAM/CPU/thermal status, and ETA.
5. **Deterministic Aggregator (`CampaignAggregator`)**: Verifies exact 8,784-step coverage per cell ($N_{obs} = 8,784$), checking for zero gaps or overlapping ranges before computing matrix performance metrics.
6. **Resource & Sleep Inhibitor (`ResourceMonitor`)**: Tracks CPU %, RAM %, disk free space, thermal sensor readings, and process-scoped sleep inhibition (`systemd-inhibit`).

## Governance Guarantees
- **Zero Protected Component Modification**: Production solvers, ECD, router, simulator, and runner files remain 100% untouched (`SOURCE_MODIFICATIONS = 0`).
- **Sequential Closed-Loop Trajectory Continuity**: Timesteps $k 	o k+1$ within each single cell remain strictly ordered and stateful. Parallelism is applied across independent matrix cells.
- **Execution Authorization Guard**: Annual campaign execution is locked behind an explicit governance flag (`--execute-authorized`), maintaining `HUMAN_EXECUTION_AUTHORIZATION = NOT_GRANTED`.
