# 365D CAMPAIGN EXECUTION COMMAND INTERFACE

## Command Line Interface (`python -m system.orchestration.cli`)

### 1. Dry-Run Infrastructure Test
```bash
.venv/bin/python3 -m system.orchestration.cli --dry-run
```
Executes a 48-step multi-worker test with checkpointing, terminal UI, and aggregation verification.

### 2. Campaign Status Check
```bash
.venv/bin/python3 -m system.orchestration.cli --status <RUN_ID>
```
Displays current progress, completed cycles, active workers, and resource telemetry for an active or completed run.

### 3. Resume Interrupted Campaign
```bash
.venv/bin/python3 -m system.orchestration.cli --resume <RUN_ID>
```
Resumes an interrupted campaign run from its latest verified checkpoints.

### 4. Verify & Aggregate Completed Run
```bash
.venv/bin/python3 -m system.orchestration.cli --verify <RUN_ID>
```
Validates 8,784-step coverage and generates official matrix comparison results.

### 5. Authorized Campaign Execution (GOVERNED)
```bash
.venv/bin/python3 -m system.orchestration.cli --execute-authorized
```
Requires explicit human execution authorization in manifest (`HUMAN_EXECUTION_AUTHORIZATION = GRANTED`).
