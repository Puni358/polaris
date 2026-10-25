# POLARIS 23-Horizon OFAT Experiment — Checkpoint Hardening & Governance Amendment Report

## Governance Status: HARDENING_AMENDMENT_VERIFIED

### Executive Summary
Following the complete execution of 95,496 MILP solves during the initial OFAT launch and subsequent process crash in post-processing (`KeyError: 'origin_idx'`), the execution harness has been hardened with durable trajectory checkpointing, resume semantics, RAM-bounded memory management, atomic file operations, and post-processing bug fixes.

**NO real MILP solves were executed during this hardening task.**

---

### Key Technical Amendments

1. **Post-Processing Bug Fix**:
   - Corrected post-processing key references in `run_polaris_23_horizon_ofat_experiment.py` from `origin_idx` to `origin_id` to match worker return dictionary schema.

2. **Durable Trajectory Checkpointing**:
   - Checkpoint Directory: `POLARIS_23_HORIZON_OFAT_CHECKPOINT/`
   - Individual trajectory format: `arm_{j:02d}_origin_{oid:04d}.json` containing full 24-step telemetry records, evaluation metrics, and deterministic payload SHA-256 signatures.

3. **Atomic File Operations**:
   - Crash-safe atomic writes via temporary files, explicit `fsync()`, and OS-level atomic file replacement (`temp_path.replace(target_path)`).

4. **Durable Manifest**:
   - Tracked in `POLARIS_23_HORIZON_OFAT_CHECKPOINT/manifest.json` with harness hash, expected/completed trajectory counts, implied solve counts, and per-trajectory SHA-256 signatures.

5. **Resume & Pre-Execution Validation**:
   - Automatic startup validation verifying all existing trajectory checkpoints and SHA signatures.
   - Schedules ONLY uncompleted `(treatment_j, origin_id)` pairs. Already completed valid trajectories are skipped.

6. **Checkpoint-Based Finalization**:
   - Post-processing reads directly from validated disk checkpoints (`finalize_from_checkpoints`). Final artifact generation is rerunnable independently without executing any MILP solve.

7. **Pre-Flight Verification**:
   - Added `--test-checkpointing` CLI flag to run a complete pre-flight test suite (synthetic trajectory generation, atomic writes, SHA validation, error detection, resume calculation, and post-processing verification) executing **0 real MILP solves**.

---

### Hardened Artifact Provenance

- **Target File**: `run_polaris_23_horizon_ofat_experiment.py`
- **SHA-256**: `1140e9db048362a6ef4088175b3d462894263bfb6014233e9d444ac196cabb6a`
- **Pre-Flight Test Command**: `python3 run_polaris_23_horizon_ofat_experiment.py --test-checkpointing`
- **Pre-Flight Result**: `PASS` (0 MILP solves executed)
- **Scientific Protocol Status**: `UNCHANGED`
