# 365D SYSTEM SLEEP INHIBITION & DISPLAY TIMEOUT SPECIFICATION

## Governed Status Register
- **`PRIMARY_EXECUTION_PLATFORM`**: UBUNTU_LINUX
- **`SLEEP_INHIBITION_REQUIRED`**: TRUE
- **`SLEEP_INHIBITION_PLATFORM`**: LINUX_SYSTEMD
- **`SLEEP_INHIBITION_MODE`**: PROCESS_SCOPED
- **`LID_STATE_EXPECTED`**: OPEN
- **`DISPLAY_SLEEP_ALLOWED`**: TRUE
- **`SYSTEM_IDLE_SLEEP_BLOCKED`**: TRUE
- **`SLEEP_INHIBITION_ACQUISITION`**: PASS
- **`SLEEP_INHIBITION_VERIFICATION`**: PASS
- **`SLEEP_INHIBITION_LIFECYCLE_TEST`**: PASS
- **`SLEEP_INHIBITION_CLEANUP_TEST`**: PASS
- **`VERIFICATION_LIMITATION`**: FALSE (Independently verified via systemd-inhibit --list)

## Forensic Verification of Executed CampaignMaster Runtime Path

### 1. Startup Order & Pre-Worker Acquisition
`CampaignMaster.initialize()` acquires `SleepInhibitor` prior to spawning any worker process (`worker_01` .. `worker_04`). If acquisition fails, execution halts immediately with status `FAILED_SLEEP_INHIBITION`.

### 2. Pre-Worker Verification
`CampaignMaster` calls `sleep_inhibitor.verify()` prior to worker process initialization, executing `/usr/bin/systemd-inhibit --list` to confirm active logind registration.

### 3. In-Run Liveness Monitoring & Reacquisition Protocol
During master loop execution, `CampaignMaster` polls `sleep_inhibitor.verify()`. If liveness loss is detected:
1. Master halts work unit assignment.
2. Safe state checkpointing is allowed.
3. Master attempts controlled reacquisition via `sleep_inhibitor.acquire()`.
4. Reacquisition is verified via systemd-inhibit query.
5. If reacquisition fails, campaign halts cleanly with status `FAILED_SLEEP_INHIBITION_LOST`.

### 4. Lifecycle & Cleanup Guarantees
Wrapped in `try ... finally` block inside `CampaignMaster.run()`:
- **Normal Completion**: Released cleanly in `finally` block via SIGTERM/wait.
- **Graceful Interruption (Ctrl+C / SIGINT / SIGTERM)**: Trapped, workers stopped, released cleanly in `finally` block.
- **Exception / Failure**: Trapped, error logged, released cleanly in `finally` block.

### 5. Ubuntu Execution Mechanism
- **Subprocess Call**: `/usr/bin/systemd-inhibit --what=idle:sleep --who=POLARIS_EMS --why="..." sleep 864000`.
- **Display Timeout Compliance**: `--what=idle:sleep` excludes `handle-lid-switch` and `idle:display`. Display is permitted to dim, blank, or lock screen while CPU execution continues.
- **Lid-Open Operating Rule**: Expected operating condition is laptop lid **OPEN**. Zero persistent modifications to `/etc/systemd/logind.conf`, GNOME power settings, system power plans, or system configuration.

### 6. Verification Analysis
- **`VERIFICATION_LIMITATION = FALSE`**
- **Technical Explanation**: On Ubuntu Linux systemd, `/usr/bin/systemd-inhibit --list` provides independent OS-level inspection of logind DBus inhibitor locks, returning PID, WHO, WHY, and WHAT fields for direct verification.

