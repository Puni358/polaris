#!/usr/bin/env python3
"""
POLARIS — Container Isolation Preflight Validation Suite (P1–P7)
Tracking ID: SPEC-2026-OD02-ISOLATION-03 (Gate C.1 Preflight Probe Only)
Authoritative Governance: MDR v1.9.13, Pass 23

GOVERNANCE & SAFETY CONTRACT:
- Executes ONLY inside the Bubblewrap preflight sandbox (when Gate C.1 is authorized)
  or under mocked static unit tests.
- Imports ONLY Python standard library modules.
- NEVER imports or invokes production `system.*` modules, `highspy`, or the diagnostic runner.
- NEVER attempts to create, modify, or unlink files on any read-only host-backed source mount.
- Verifies mount read-only/read-write enforcement through `/proc/self/mountinfo` metadata
  and `os.access` checks; tests actual file creation ONLY inside the approved writable
  output mount (`/workspace/experiments/diagnostics/diag_od02_boundary_2024`) with
  guaranteed immediate cleanup.
- Fails closed whenever any expected mount, allowlist entry, hash, network state,
  resource limit, or PID namespace evidence is missing or unexpected.
"""

from __future__ import annotations

import errno
import hashlib
import os
import socket
import sys
from typing import Dict, List, Set, Tuple

# ==============================================================================
# 1. GOVERNED ALLOWLISTS, MOUNT CONTRACTS & SHA-256 PROVENANCE
# ==============================================================================

SPEC_TRACKING_ID = "SPEC-2026-OD02-ISOLATION-03"
MDR_CANONICAL_VERSION = "1.9.13"

# Exact directory listing allowlists inside /workspace
EXPECTED_WORKSPACE_ENTRIES: Set[str] = {
    ".venv",
    "system",
    "scratch",
    "data",
    "experiments",
    "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv",
}

EXPECTED_SCRATCH_ENTRIES: Set[str] = {
    "run_isolation_probes.py",
    "run_od02_boundary_diagnostic.py",
    "diag_od02_boundary.py",
}

EXPECTED_DATA_ENTRIES: Set[str] = {
    "POLARIS_v0_1_future_weather_forecasts_2024.csv",
    "POLARIS_v0_1_clearsky_decomposition.csv",
}

# Required read-only mounts and their expected node types ("dir" or "file")
REQUIRED_RO_MOUNTS: Dict[str, str] = {
    "/usr": "dir",
    "/etc": "dir",
    "/workspace/.venv": "dir",
    "/workspace/system": "dir",
    "/workspace/scratch/run_isolation_probes.py": "file",
    "/workspace/scratch/run_od02_boundary_diagnostic.py": "file",
    "/workspace/scratch/diag_od02_boundary.py": "file",
    "/workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv": "file",
    "/workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv": "file",
    "/workspace/data/POLARIS_v0_1_clearsky_decomposition.csv": "file",
}

# Sole approved writable bind mount
APPROVED_RW_OUTPUT_MOUNT = "/workspace/experiments/diagnostics/diag_od02_boundary_2024"

# Quarantined paths that must be physically absent (ENOENT)
QUARANTINED_PATHS: Tuple[str, ...] = (
    "/workspace/data/POLARIS_v0_1_future_weather_forecasts_2025.csv",
    "/workspace/data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_multivariate.csv",
    "/workspace/data/raw_2025_sites_download",
    "/workspace/data/_checkpoints_2025_nwp_fetch",
    "/workspace/POLARIS_v0_1_future_weather_forecasts_2025.csv",
    "/workspace/experiments/stage4_blind",
    "/workspace/scratch/test_diag_od02_boundary_static.py",
    "/workspace/scratch/OD02_DIAGNOSTIC_ISOLATION_SPEC.md",
    "/data",
    "/home",
)

# Pre-registered SHA-256 digests for the 3 approved 2024 input files
EXPECTED_INPUT_SHA256: Dict[str, str] = {
    "/workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv": (
        "0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad"
    ),
    "/workspace/data/POLARIS_v0_1_clearsky_decomposition.csv": (
        "596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a"
    ),
    "/workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv": (
        "8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16"
    ),
}

# Resource limit requirements
EXPECTED_MAX_AS_BYTES = 8589934592  # 8 GiB
EXPECTED_MAX_CPU_SECONDS = 300      # 300 seconds


class IsolationPreflightError(RuntimeError):
    """Raised when any P1–P7 container isolation probe fails closed."""


# ==============================================================================
# 2. HELPER FUNCTIONS (MOUNTINFO, HASHING, LIMITS)
# ==============================================================================

def _unescape_mountinfo_path(raw_path: str) -> str:
    """Unescapes octal sequences (e.g. \\040 for space) in /proc/self/mountinfo."""
    return (
        raw_path.replace("\\040", " ")
        .replace("\\011", "\t")
        .replace("\\012", "\n")
        .replace("\\134", "\\")
    )


def parse_mountinfo(mountinfo_text: str) -> Dict[str, Dict[str, object]]:
    """
    Parses /proc/self/mountinfo text into a dictionary keyed by mount point.
    If a mount point appears multiple times, later entries override earlier ones
    (reflecting the active top-most mount in the VFS namespace).
    """
    if not mountinfo_text or not mountinfo_text.strip():
        raise IsolationPreflightError("FAIL-CLOSED: /proc/self/mountinfo is empty or missing.")

    mounts: Dict[str, Dict[str, object]] = {}
    for raw_line in mountinfo_text.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if " - " not in line:
            raise IsolationPreflightError(f"FAIL-CLOSED: Malformed mountinfo line: {line!r}")

        lhs, rhs = line.split(" - ", 1)
        lhs_parts = lhs.split()
        rhs_parts = rhs.split()
        if len(lhs_parts) < 6 or len(rhs_parts) < 3:
            raise IsolationPreflightError(f"FAIL-CLOSED: Incomplete mountinfo fields: {line!r}")

        mount_point = _unescape_mountinfo_path(lhs_parts[4])
        vfs_options = set(lhs_parts[5].split(","))
        fs_type = rhs_parts[0]
        mount_source = _unescape_mountinfo_path(rhs_parts[1])
        super_options = set(rhs_parts[2].split(","))

        mounts[mount_point] = {
            "mount_point": mount_point,
            "vfs_options": vfs_options,
            "fs_type": fs_type,
            "mount_source": mount_source,
            "super_options": super_options,
        }

    return mounts


def compute_sha256(file_path: str) -> str:
    """Computes SHA-256 hex digest of a file in 64 KiB chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_proc_limits(limits_text: str) -> Dict[str, Tuple[str, str, str]]:
    """
    Parses /proc/self/limits into a mapping:
    limit_name -> (soft_limit, hard_limit, units)
    """
    if not limits_text or not limits_text.strip():
        raise IsolationPreflightError("FAIL-CLOSED: /proc/self/limits is empty or missing.")

    parsed: Dict[str, Tuple[str, str, str]] = {}
    lines = limits_text.strip().splitlines()
    for line in lines[1:]:  # Skip header row
        tokens = line.split()
        if len(tokens) < 3:
            continue
        # Units column is optional (e.g. "Max processes" has no units on some kernels,
        # whereas "Max cpu time" has "seconds" and "Max address space" has "bytes").
        if tokens[-1] in ("seconds", "bytes", "processes", "files", "locks", "signals", "us", "kbytes"):
            units = tokens[-1]
            hard = tokens[-2]
            soft = tokens[-3]
            name = " ".join(tokens[:-3])
        else:
            units = ""
            hard = tokens[-1]
            soft = tokens[-2]
            name = " ".join(tokens[:-2])
        parsed[name] = (soft, hard, units)
    return parsed


# ==============================================================================
# 3. INDIVIDUAL PROBE IMPLEMENTATIONS (P1 – P7)
# ==============================================================================

def probe_p1_mounts_and_allowlists(mountinfo_path: str = "/proc/self/mountinfo") -> None:
    """
    P1: Verifies required mount points in /proc/self/mountinfo, node types, and
    exact directory allowlists for /workspace, /workspace/scratch, and /workspace/data.
    """
    if not os.path.isfile(mountinfo_path):
        raise IsolationPreflightError(f"P1_FAIL: Mount metadata file missing: '{mountinfo_path}'")

    with open(mountinfo_path, "r", encoding="utf-8") as f:
        mounts = parse_mountinfo(f.read())

    # 1. Verify root (/) and /tmp are tmpfs
    for tmpfs_target in ("/", "/tmp"):
        if tmpfs_target not in mounts:
            raise IsolationPreflightError(f"P1_FAIL: Missing mount entry for '{tmpfs_target}'")
        if mounts[tmpfs_target]["fs_type"] != "tmpfs":
            raise IsolationPreflightError(
                f"P1_FAIL: Expected tmpfs at '{tmpfs_target}', got '{mounts[tmpfs_target]['fs_type']}'"
            )

    # 2. Verify all required RO mounts exist in mountinfo and have matching node types
    for path, expected_type in REQUIRED_RO_MOUNTS.items():
        if path not in mounts:
            raise IsolationPreflightError(f"P1_FAIL: Required mount missing from mountinfo: '{path}'")
        if not os.path.exists(path):
            raise IsolationPreflightError(f"P1_FAIL: Required mount path does not exist: '{path}'")
        if expected_type == "dir" and not os.path.isdir(path):
            raise IsolationPreflightError(f"P1_FAIL: Expected directory at '{path}'")
        if expected_type == "file" and not os.path.isfile(path):
            raise IsolationPreflightError(f"P1_FAIL: Expected regular file at '{path}'")

    # 3. Verify sole writable output mount exists in mountinfo and is a directory
    if APPROVED_RW_OUTPUT_MOUNT not in mounts:
        raise IsolationPreflightError(
            f"P1_FAIL: Output mount missing from mountinfo: '{APPROVED_RW_OUTPUT_MOUNT}'"
        )
    if not os.path.isdir(APPROVED_RW_OUTPUT_MOUNT):
        raise IsolationPreflightError(
            f"P1_FAIL: Output mount is not a directory: '{APPROVED_RW_OUTPUT_MOUNT}'"
        )

    # 4. Verify /workspace/scratch is an in-memory tmpfs directory (NOT a full directory bind mount)
    if "/workspace/scratch" in mounts:
        raise IsolationPreflightError(
            "P1_FAIL: Whole '/workspace/scratch' directory is mounted! Only individual approved "
            "scripts may be bound into /workspace/scratch."
        )

    # 5. Verify exact visible allowlists in /workspace, /workspace/scratch, and /workspace/data
    actual_workspace = set(os.listdir("/workspace"))
    if actual_workspace != EXPECTED_WORKSPACE_ENTRIES:
        raise IsolationPreflightError(
            f"P1_FAIL: /workspace allowlist mismatch. Expected {sorted(EXPECTED_WORKSPACE_ENTRIES)}, "
            f"got {sorted(actual_workspace)}"
        )

    actual_scratch = set(os.listdir("/workspace/scratch"))
    if actual_scratch != EXPECTED_SCRATCH_ENTRIES:
        raise IsolationPreflightError(
            f"P1_FAIL: /workspace/scratch allowlist mismatch. Expected {sorted(EXPECTED_SCRATCH_ENTRIES)}, "
            f"got {sorted(actual_scratch)}"
        )

    actual_data = set(os.listdir("/workspace/data"))
    if actual_data != EXPECTED_DATA_ENTRIES:
        raise IsolationPreflightError(
            f"P1_FAIL: /workspace/data allowlist mismatch. Expected {sorted(EXPECTED_DATA_ENTRIES)}, "
            f"got {sorted(actual_data)}"
        )


def probe_p2_quarantine_absence() -> None:
    """
    P2: Verifies physical non-existence (ENOENT) of known 2025/blind paths and ensures
    no entry under /workspace/data or /workspace/scratch contains '2025' or 'blind'.
    """
    for q_path in QUARANTINED_PATHS:
        if os.path.exists(q_path) or os.path.islink(q_path):
            raise IsolationPreflightError(f"P2_FAIL: Quarantined or unapproved path visible: '{q_path}'")

    for check_dir in ("/workspace", "/workspace/data", "/workspace/scratch"):
        for entry in os.listdir(check_dir):
            lower = entry.lower()
            if "2025" in lower or "blind" in lower:
                raise IsolationPreflightError(
                    f"P2_FAIL: Quarantined token detected in '{check_dir}/{entry}'"
                )


def probe_p3_input_sha256_verification() -> None:
    """
    P3: Verifies bit-for-bit SHA-256 digests of the three approved 2024 input files.
    """
    for path, expected_hex in EXPECTED_INPUT_SHA256.items():
        if not os.path.isfile(path):
            raise IsolationPreflightError(f"P3_FAIL: Approved input file missing: '{path}'")
        actual_hex = compute_sha256(path)
        if actual_hex != expected_hex:
            raise IsolationPreflightError(
                f"P3_FAIL: SHA-256 mismatch on '{path}': expected {expected_hex}, got {actual_hex}"
            )


def probe_p4_ro_and_rw_confinement(mountinfo_path: str = "/proc/self/mountinfo") -> None:
    """
    P4: Verifies read-only enforcement on all required RO mounts via /proc/self/mountinfo
    metadata and os.access WITHOUT attempting to create or modify files on host-backed
    source mounts. Verifies writable confinement on the approved output directory with
    immediate cleanup.
    """
    if not os.path.isfile(mountinfo_path):
        raise IsolationPreflightError(f"P4_FAIL: Mount metadata file missing: '{mountinfo_path}'")

    with open(mountinfo_path, "r", encoding="utf-8") as f:
        mounts = parse_mountinfo(f.read())

    # 1. Non-destructive verification of read-only mounts via kernel mountinfo (primary) + os.access (secondary)
    for ro_path in REQUIRED_RO_MOUNTS:
        entry = mounts.get(ro_path)
        if entry is None:
            raise IsolationPreflightError(f"P4_FAIL: Missing mountinfo entry for '{ro_path}'")
        vfs_opts: Set[str] = entry["vfs_options"]  # type: ignore[assignment]
        if "ro" not in vfs_opts or "rw" in vfs_opts:
            raise IsolationPreflightError(
                f"P4_FAIL: Mount '{ro_path}' is not read-only in mountinfo (options: {sorted(vfs_opts)})"
            )
        if os.access(ro_path, os.W_OK):
            raise IsolationPreflightError(
                f"P4_FAIL: os.access reports write permission (W_OK) on read-only mount '{ro_path}'"
            )

    # 2. Verify no other host-backed bind mount is writable anywhere in the namespace
    for m_point, m_info in mounts.items():
        fs_type = m_info["fs_type"]
        vfs_opts = m_info["vfs_options"]  # type: ignore[assignment]
        # Ignore synthetic kernel/memory filesystems
        if fs_type in ("tmpfs", "proc", "devtmpfs", "devpts", "sysfs", "cgroup", "cgroup2", "mqueue"):
            continue
        if m_point == APPROVED_RW_OUTPUT_MOUNT:
            if "rw" not in vfs_opts:
                raise IsolationPreflightError(
                    f"P4_FAIL: Approved output mount '{m_point}' is not mounted 'rw' in mountinfo"
                )
        else:
            if "ro" not in vfs_opts:
                raise IsolationPreflightError(
                    f"P4_FAIL: Unexpected writable host-backed mount '{m_point}' (options: {sorted(vfs_opts)})"
                )

    # 3. Verify controlled write and immediate unlink inside the approved output directory
    probe_file = os.path.join(APPROVED_RW_OUTPUT_MOUNT, ".p4_preflight_write_probe")
    try:
        with open(probe_file, "w", encoding="utf-8") as f:
            f.write("probe_ok")
        with open(probe_file, "r", encoding="utf-8") as f:
            content = f.read()
        if content != "probe_ok":
            raise IsolationPreflightError("P4_FAIL: Output write verification content mismatch.")
    except OSError as err:
        raise IsolationPreflightError(
            f"P4_FAIL: Could not write to approved output directory '{APPROVED_RW_OUTPUT_MOUNT}': {err}"
        ) from err
    finally:
        if os.path.exists(probe_file):
            os.remove(probe_file)

    if os.path.exists(probe_file):
        raise IsolationPreflightError(f"P4_FAIL: Temporary probe file '{probe_file}' was not cleaned up.")


def probe_p5_network_namespace_isolation(
    net_dev_path: str = "/proc/net/dev",
    net_route_path: str = "/proc/net/route",
) -> None:
    """
    P5: Distinguishes true kernel network namespace isolation (--unshare-net) from
    ordinary external connection failures by requiring:
      1. /proc/net/dev exists and lists ONLY the loopback ('lo') interface (no eth*, wlan*, enp*, etc.).
      2. /proc/net/route exists and contains zero routing table entries (header line only).
      3. Attempting a UDP socket send/connect to an external IPv4 address fails immediately
         with ENETUNREACH (errno 101) or EADDRNOTAVAIL/EPERM/EACCES.
    """
    if not os.path.isfile(net_dev_path):
        raise IsolationPreflightError(f"P5_FAIL: Kernel network device table missing: '{net_dev_path}'")
    if not os.path.isfile(net_route_path):
        raise IsolationPreflightError(f"P5_FAIL: Kernel routing table missing: '{net_route_path}'")

    with open(net_dev_path, "r", encoding="utf-8") as f:
        dev_lines = [line.strip() for line in f.read().splitlines() if ":" in line]

    interfaces = [line.split(":", 1)[0].strip() for line in dev_lines]
    if interfaces != ["lo"]:
        raise IsolationPreflightError(
            f"P5_FAIL: Non-loopback network interfaces present in /proc/net/dev: {interfaces}"
        )

    with open(net_route_path, "r", encoding="utf-8") as f:
        route_lines = [line.strip() for line in f.read().splitlines() if line.strip()]

    if len(route_lines) != 1:
        raise IsolationPreflightError(
            f"P5_FAIL: Active network routes found in /proc/net/route ({len(route_lines) - 1} routes)"
        )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 53))  # RFC 5737 TEST-NET-1
        raise IsolationPreflightError("P5_FAIL: Outbound socket connect succeeded inside unshared netns!")
    except OSError as err:
        if err.errno not in (errno.ENETUNREACH, errno.EPERM, errno.EACCES, errno.EADDRNOTAVAIL):
            raise IsolationPreflightError(
                f"P5_FAIL: Unexpected socket errno {err.errno} ({err}); expected ENETUNREACH"
            ) from err
    finally:
        sock.close()


def probe_p6_resource_limits(limits_path: str = "/proc/self/limits") -> None:
    """
    P6: Verifies static kernel resource limits (Max address space = 8 GiB, Max cpu time = 300s)
    by parsing structured rows in /proc/self/limits.
    """
    if not os.path.isfile(limits_path):
        raise IsolationPreflightError(f"P6_FAIL: Kernel limits file missing: '{limits_path}'")

    with open(limits_path, "r", encoding="utf-8") as f:
        limits = parse_proc_limits(f.read())

    if "Max address space" not in limits:
        raise IsolationPreflightError("P6_FAIL: 'Max address space' missing from /proc/self/limits")
    as_soft, as_hard, _ = limits["Max address space"]
    if as_soft != str(EXPECTED_MAX_AS_BYTES) or as_hard != str(EXPECTED_MAX_AS_BYTES):
        raise IsolationPreflightError(
            f"P6_FAIL: Max address space limit mismatch: expected ({EXPECTED_MAX_AS_BYTES}, "
            f"{EXPECTED_MAX_AS_BYTES}), got ({as_soft}, {as_hard})"
        )

    if "Max cpu time" not in limits:
        raise IsolationPreflightError("P6_FAIL: 'Max cpu time' missing from /proc/self/limits")
    cpu_soft, cpu_hard, _ = limits["Max cpu time"]
    if cpu_soft != str(EXPECTED_MAX_CPU_SECONDS) or cpu_hard != str(EXPECTED_MAX_CPU_SECONDS):
        raise IsolationPreflightError(
            f"P6_FAIL: Max cpu time limit mismatch: expected ({EXPECTED_MAX_CPU_SECONDS}, "
            f"{EXPECTED_MAX_CPU_SECONDS}), got ({cpu_soft}, {cpu_hard})"
        )


def probe_p7_pid_namespace_confinement(proc_dir: str = "/proc") -> None:
    """
    P7: Verifies PID namespace isolation (--unshare-pid) by confirming that PID 1 exists
    inside /proc, the visible process count is <= 3, and the current process PID is <= 3.
    """
    if not os.path.isdir(proc_dir):
        raise IsolationPreflightError(f"P7_FAIL: Proc filesystem missing at '{proc_dir}'")

    pids = sorted(int(entry) for entry in os.listdir(proc_dir) if entry.isdigit())
    if not pids or 1 not in pids:
        raise IsolationPreflightError(
            f"P7_FAIL: PID 1 not present in '{proc_dir}'; PID namespace not isolated: {pids}"
        )
    if len(pids) > 3:
        raise IsolationPreflightError(
            f"P7_FAIL: Excessive processes visible in container PID namespace ({len(pids)}): {pids}"
        )
    current_pid = os.getpid()
    if current_pid > 3:
        raise IsolationPreflightError(
            f"P7_FAIL: Current process PID ({current_pid}) exceeds isolated namespace bound (<= 3)"
        )


# ==============================================================================
# 4. PREFLIGHT SUITE ENTRYPOINT
# ==============================================================================

def run_all_probes() -> int:
    """Executes P1 through P7 sequentially and fails closed on any error."""
    print(f"[PREFLIGHT] Starting {SPEC_TRACKING_ID} Isolation Verification Suite (P1-P7)...")

    probe_p1_mounts_and_allowlists()
    print("  [PASS] P1: Mount metadata (/proc/self/mountinfo) and exact directory allowlists verified.")

    probe_p2_quarantine_absence()
    print("  [PASS] P2: Physical absence of 2025/blind quarantined paths confirmed (ENOENT).")

    probe_p3_input_sha256_verification()
    print("  [PASS] P3: SHA-256 digests of all 3 approved 2024 input files verified.")

    probe_p4_ro_and_rw_confinement()
    print("  [PASS] P4: Non-destructive RO mount metadata and RW output confinement verified.")

    probe_p5_network_namespace_isolation()
    print("  [PASS] P5: Network namespace isolation confirmed (lo-only, 0 routes, ENETUNREACH).")

    probe_p6_resource_limits()
    print("  [PASS] P6: Kernel resource limits (8 GiB AS, 300s CPU) verified via /proc/self/limits.")

    probe_p7_pid_namespace_confinement()
    print("  [PASS] P7: PID namespace isolation confirmed (PID 1 present, <= 3 processes).")

    print("[SUCCESS] ALL PREFLIGHT PROBES (P1-P7) PASSED.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_all_probes())
    except IsolationPreflightError as exc:
        print(f"\n[PREFLIGHT FAILED CLOSED] {exc}", file=sys.stderr)
        sys.exit(1)
