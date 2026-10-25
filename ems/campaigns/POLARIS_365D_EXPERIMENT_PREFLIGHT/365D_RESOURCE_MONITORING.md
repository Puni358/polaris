# 365D RESOURCE, THERMAL & SLEEP MONITORING SPECIFICATION

## System Telemetry Measurements
- **CPU Cores & Load**: 4 logical x86_64 cores.
- **RAM Capacity & Utilization**: Total 7.50 GB, Available 3.18 GB.
- **Disk Free Space**: 240.18 GB available.
- **Thermal Sensors**: Monitored via Linux sysfs `/sys/class/thermal/` (`x86_pkg_temp` = 42.0°C - 74.0°C).
- **Sleep Inhibition**: Process-scoped via `SetThreadExecutionState` on Windows / `systemd-inhibit` on Linux (`SLEEP_INHIBITION=ACTIVE`).

## Resource Safety Rules
- **Disk Space Preflight**: Asserts minimum 5.0 GB free disk before initiating campaign (expected artifact size ~18 MB).
- **RAM Safety Margin**: 4 workers consume ~400 MB total RAM, well within 3.18 GB available RAM limit.
