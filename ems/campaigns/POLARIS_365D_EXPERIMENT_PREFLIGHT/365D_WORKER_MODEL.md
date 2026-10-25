# 365D WORKER PROCESS MODEL & DECOMPOSITION SPECIFICATION

## Worker Architecture & Decomposition
Closed-loop MPC simulation is stateful ($k 	o 	ext{observe} 	o 	ext{forecast} 	o 	ext{optimize} 	o 	ext{commit } k=0 	o 	ext{step twin} 	o k+1$). Therefore, individual timesteps within a trajectory CANNOT be arbitrarily parallelized out-of-order.

Parallelism is achieved by executing independent experiment matrix cells concurrently on isolated worker processes.

## Worker Assignment Matrix
- **Cell 1 (`cell_1`)**: Same Forecast + Baseline Controller (`LocalRuleBasedEnergyOptimizer`) $	o$ Worker 1 (`worker_01`)
- **Cell 2 (`cell_2`)**: Same Forecast + POLARIS Controller (`GAP19HighsNativeOptimizer`) $	o$ Worker 2 (`worker_02`)
- **Cell 3 (`cell_3`)**: Baseline Forecast + Baseline Controller (`LocalRuleBasedEnergyOptimizer`) $	o$ Worker 3 (`worker_03`)
- **Cell 4 (`cell_4`)**: POLARIS Forecast + POLARIS Controller (`GAP19HighsNativeOptimizer`) $	o$ Worker 4 (`worker_04`)

## Hardware Selection Parameters
- **Requested Workers**: 8
- **Available CPU Cores**: 4 logical x86_64 cores
- **Available RAM**: 7.50 GB Total (3.18 GB Available)
- **Selected Workers**: **4 Workers**
- **Selection Rationale**: "Selected 4 workers to match the 4 CPU cores and the 4-cell experiment matrix, ensuring 1 core per cell with zero process thrashing, safe RAM usage (~100 MB per worker), and optimal thermal stability."

## Isolation Boundaries
Each worker process operates inside a strictly isolated directory layout:
`POLARIS_365D_CAMPAIGN_RUN_<ID>/workers/worker_XX/`
`POLARIS_365D_CAMPAIGN_RUN_<ID>/cells/cell_XX/`
`POLARIS_365D_CAMPAIGN_RUN_<ID>/checkpoints/cell_XX/`

No two workers ever write to the same mutable result file or checkpoint directory.
