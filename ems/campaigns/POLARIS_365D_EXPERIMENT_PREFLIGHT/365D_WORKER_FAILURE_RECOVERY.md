# 365D WORKER FAILURE & RECOVERY SPECIFICATION

## Worker Failure Containment
Worker process crashes (e.g. process termination, unhandled exception, SIGKILL) are completely isolated within that worker's assigned cell. Other workers continue unaffected.

## Recovery Protocol
1. **Detection**: `CampaignMaster` polls worker subprocess handle and detects non-zero exit code (`FAILED_EXIT_X`).
2. **Checkpoint Audit**: `CampaignMaster` inspects `checkpoints/cell_XX/` for the latest verified checkpoint.
3. **State Restoration**: Worker process is re-spawned with `--resume-checkpoint <path>`.
4. **Resumption**: Worker restores exact state, cumulative fuel, and step index $k_{resume} = k_{cp} + 1$, resuming closed-loop execution.
5. **Deduplication**: Step records prior to $k_{resume}$ are preserved without duplication. Work unit IDs guarantee zero double-counting during final aggregation.
