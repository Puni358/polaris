# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING EXECUTION CONTRACT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `TRAINING EXECUTION CONTRACT`  
**Status:** `GOVERNED EXECUTION SPECIFICATION`  

---

## 1. Hardware & Worker Configuration

- **Default Worker Count**: `8` workers where technically appropriate (parallel feature extraction / GBDT thread pool).
- **Resource Logging**: Live monitoring of CPU utilization, RAM consumption, GPU VRAM (if applicable), disk I/O, and thermal state.
- **Worker Justification Rule**: If a training run utilizes fewer than 8 workers (e.g. single-threaded GBDT solver), the exact worker count and technical reason MUST be recorded in `MODEL_RUN_MANIFEST.json`.

---

## 2. Immutable Run Directory Structure

Future authorized training runs MUST create a unique, non-overwritable run directory:
`artifacts/model_runs/RUN_<unique_id>/`

Inside `RUN_<unique_id>/`:
- `model.joblib`: Serialized fitted model binary.
- `scaler.joblib`: Serialized preprocessor binary.
- `MODEL_RUN_MANIFEST.json`: 20-point machine-readable provenance manifest.
- `TRAINING_REPRODUCIBILITY_CHECKLIST.md`: 34-item completed checklist.
- `training_execution.log`: Full stdout/stderr execution log.
- `resource_utilization.csv`: CPU, RAM, and thermal time series telemetry.
- `REPLAY_REPORT.json`: Independent process replay verification report.

---

## 3. Checkpointing & Interrupt Safety

- **Checkpoint Frequency**: Every 10 iterations / epochs.
- **Interruption Handling**: Traps `SIGINT` / `SIGTERM` signals, flushes open logs, serializes current checkpoint, and writes `run_status = "INTERRUPTED"`.
- **Non-Overwrite Rule**: Re-running or resuming an interrupted job MUST write to a NEW run directory (`RUN_<new_unique_id>`) referencing the prior checkpoint hash.

---

## 4. Failed & Abandoned Run Retention

- **Policy**: Failed or aborted training runs MUST NOT be deleted.
- **Retention**: Retains run directory, failure stack trace, partial logs, and marks `governance_status = "NOT_REPRODUCIBLE"`.
