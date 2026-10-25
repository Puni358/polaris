# 365D CAMPAIGN RUN MANIFEST SPECIFICATION

## Run Manifest Schema & Parameters
- **Time Domain**: Full-calendar-year 2024 / 8,784 hourly cycles (`2024-01-01T00:00:00Z` through `2024-12-31T23:00:00Z`).
- **Primary Comparison Cells**:
  - `cell_a`: Simple Diesel-Only Baseline (Direct load coverage, no forecasting/optimization)
  - `cell_b`: Complete POLARIS Closed-Loop System (Option B Native HiGHS MILP / Router)
- **Primary Fuel Scenario**: `SCENARIO_FUEL_1_INFINITE_CUMULATIVE`
- **Secondary Fuel Scenario**: `SCENARIO_FUEL_2_SYNTHETIC_FINITE_RESUPPLY` (Not executed)
- **Primary Execution Platform**: `PRIMARY_EXECUTION_PLATFORM = UBUNTU_LINUX`
- **Sleep Inhibition**: `LINUX_SYSTEMD` (`/usr/bin/systemd-inhibit --what=idle:sleep`, process-scoped, lid open, display blanking allowed)
- **Worker Process Allocation**: 2 primary workers (`worker_01`, `worker_02`)
- **Checkpoint Interval**: 500 steps (SHA256 chained JSON snapshots)
- **Human Execution Authorization**: `NOT_GRANTED`
