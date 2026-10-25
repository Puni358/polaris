# 365D LOCAL TERMINAL PROGRESS VISIBILITY SPECIFICATION

## Live ASCII Terminal UI Layout
The `CampaignMaster` process renders a live terminal interface (`TerminalProgressRenderer`) updating every 1.0 second:

```
======================================================================
 POLARIS 2024 ANNUAL CAMPAIGN — EXECUTION INFRASTRUCTURE MONITOR
======================================================================
 Run ID       : polaris_365d_run_20260926_211325
 Mode         : ANNUAL CAMPAIGN
 Fuel Scenario: SCENARIO_FUEL_1_INFINITE_CUMULATIVE
 Workers      : 4/4 Active
 Elapsed Time : 00:01:45
 System RAM   : 3.04 GB free / 7.5 GB total
 Disk Free    : 240.18 GB
 Thermals     : {'x86_pkg_temp': 42.0, 'TCPU': 42.0}
----------------------------------------------------------------------
 cell_1  | [####################]   8784/ 8784 (100.0%) | Fuel: 112450.2 L | Status: COMPLETED
 cell_2  | [####################]   8784/ 8784 (100.0%) | Fuel: 104230.1 L | Status: COMPLETED
 cell_3  | [####################]   8784/ 8784 (100.0%) | Fuel: 112450.2 L | Status: COMPLETED
 cell_4  | [####################]   8784/ 8784 (100.0%) | Fuel: 104230.1 L | Status: COMPLETED
----------------------------------------------------------------------
 Latest Event: All workers finished.
======================================================================
```

## Observability Guarantees
- Displays exact completed cycles, total target cycles, percentage progress, cumulative fuel ($L$), worker status, system RAM, free disk space, CPU package temperature, and latest status events.
- Zero silent background execution. Progress is visible live on the local machine terminal.
