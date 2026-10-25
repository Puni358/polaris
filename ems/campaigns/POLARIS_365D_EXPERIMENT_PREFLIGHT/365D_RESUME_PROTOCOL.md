# 365D DETERMINISTIC RESUME PROTOCOL

## Pre-Resume Verification Pipeline
Before resuming an interrupted campaign run, `CheckpointManager.verify_and_load()` executes a 9-step verification sequence:

1. **File Existence & JSON Validity**: Verifies checkpoint JSON parses cleanly.
2. **Schema Version Match**: Verifies `schema_version == 1`.
3. **Run ID & Cell Ownership**: Asserts `run_id` and `cell_id` match current target.
4. **Self-Hash Verification**: Recalculates payload SHA256 and asserts equality with `current_checkpoint_hash`.
5. **Chain Hash Verification**: Asserts `previous_checkpoint_hash` matches prior checkpoint hash.
6. **Protected Component Hash Audit**: Asserts all 6 protected files match preflight SHA256 checksums.
7. **Canonical Fixture Hash Audit**: Asserts fixture CSV hash matches `POLARIS_HYBRID_FIXTURE_H1_0`.
8. **Physical State Consistency**: Verifies battery SOC is within 20.0% to 95.0%, cumulative fuel is non-negative and monotonic.
9. **Integrity Counter Continuity**: Restores integrity metric counters continuously without zeroing.

## Verification Failure Action
If any check fails, the resume process IMMEDIATELY HALTS with error `CHECKPOINT_VERIFICATION_FAILED`. Unverified or corrupted checkpoints are NEVER loaded.
