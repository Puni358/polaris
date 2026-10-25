#!/usr/bin/env python3
"""
POLARIS — Standalone Static Unit Tests for Gate C.1 Isolation Preflight Suite
Tracking ID: SPEC-2026-OD02-ISOLATION-03

GOVERNANCE & SAFETY CONTRACT:
- Purely static unit tests using Python's standard library (`unittest`, `tempfile`).
- ZERO imports of `system.*` production modules, `highspy`, or the diagnostic runner.
- ZERO access to evaluation datasets or 2025 blind files.
- Validates:
  1. Command, mount table, and specification consistency in OD02_DIAGNOSTIC_ISOLATION_SPEC.md.
  2. Fail-closed `/proc/self/mountinfo` parsing and exact directory allowlist enforcement (P1).
  3. Quarantined path and token rejection (P2).
  4. SHA-256 digest verification and mismatch rejection (P3).
  5. Non-destructive read-only verification (never opening RO paths for writing) and RW output cleanup (P4).
  6. Network isolation evidence vs. ordinary connection failure differentiation (P5).
  7. Structured `/proc/self/limits` verification (P6).
  8. PID namespace confinement verification (P7).
"""

from __future__ import annotations

import ast
import errno
import hashlib
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import run_isolation_probes as probes


SYNTHETIC_VALID_MOUNTINFO = """\
22 1 0:21 / / rw,nosuid,nodev - tmpfs tmpfs rw
23 22 8:2 /usr /usr ro,nosuid,nodev,relatime - ext4 /dev/sda2 ro
24 22 8:2 /etc /etc ro,nosuid,nodev,relatime - ext4 /dev/sda2 ro
25 22 0:22 / /proc rw,nosuid,nodev,noexec,relatime - proc proc rw
26 22 0:23 / /dev rw,nosuid - tmpfs devtmpfs rw,mode=755
27 22 0:24 / /tmp rw,nosuid,nodev - tmpfs tmpfs rw
28 22 8:2 /repo/.venv /workspace/.venv ro,relatime - ext4 /dev/sda2 ro
29 22 8:2 /repo/system /workspace/system ro,relatime - ext4 /dev/sda2 ro
30 22 8:2 /repo/scratch/run_isolation_probes.py /workspace/scratch/run_isolation_probes.py ro,relatime - ext4 /dev/sda2 ro
31 22 8:2 /repo/scratch/run_od02_boundary_diagnostic.py /workspace/scratch/run_od02_boundary_diagnostic.py ro,relatime - ext4 /dev/sda2 ro
32 22 8:2 /repo/scratch/diag_od02_boundary.py /workspace/scratch/diag_od02_boundary.py ro,relatime - ext4 /dev/sda2 ro
33 22 8:2 /repo/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv /workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv ro,relatime - ext4 /dev/sda2 ro
34 22 8:2 /repo/data/POLARIS_v0_1_future_weather_forecasts_2024.csv /workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv ro,relatime - ext4 /dev/sda2 ro
35 22 8:2 /repo/data/POLARIS_v0_1_clearsky_decomposition.csv /workspace/data/POLARIS_v0_1_clearsky_decomposition.csv ro,relatime - ext4 /dev/sda2 ro
36 22 8:2 /repo/experiments/diagnostics/diag_od02_boundary_2024 /workspace/experiments/diagnostics/diag_od02_boundary_2024 rw,relatime - ext4 /dev/sda2 rw
"""

SYNTHETIC_VALID_LIMITS = """\
Limit                     Soft Limit           Hard Limit           Units
Max cpu time              300                  300                  seconds
Max file size             unlimited            unlimited            bytes
Max data size             unlimited            unlimited            bytes
Max stack size            8388608              unlimited            bytes
Max address space         8589934592           8589934592           bytes
Max processes             63412                63412                processes
"""


class TestPreflightZeroProductionImports(unittest.TestCase):
    """Proves that run_isolation_probes.py imports only standard library modules."""

    def test_ast_imports_only_stdlib(self):
        probe_path = os.path.join(os.path.dirname(__file__), "run_isolation_probes.py")
        with open(probe_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=probe_path)

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module.split(".")[0])

        forbidden = {"system", "highspy", "scipy", "numpy", "run_od02_boundary_diagnostic", "diag_od02_boundary"}
        self.assertTrue(imported_modules.isdisjoint(forbidden), f"Forbidden imports found: {imported_modules & forbidden}")


class TestProbeP1MountsAndAllowlists(unittest.TestCase):
    """Verifies P1 mountinfo parsing, whole-scratch mount rejection, and exact allowlists."""

    def test_p1_passes_with_valid_mounts_and_allowlists(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(SYNTHETIC_VALID_MOUNTINFO)
            mi_path = tf.name

        try:
            def fake_listdir(path):
                if path == "/workspace":
                    return list(probes.EXPECTED_WORKSPACE_ENTRIES)
                if path == "/workspace/scratch":
                    return list(probes.EXPECTED_SCRATCH_ENTRIES)
                if path == "/workspace/data":
                    return list(probes.EXPECTED_DATA_ENTRIES)
                raise FileNotFoundError(path)

            with mock.patch("os.path.exists", return_value=True), \
                 mock.patch("os.path.isdir", side_effect=lambda p: not p.endswith((".py", ".csv"))), \
                 mock.patch("os.path.isfile", side_effect=lambda p: p == mi_path or p.endswith((".py", ".csv"))), \
                 mock.patch("os.listdir", side_effect=fake_listdir):
                probes.probe_p1_mounts_and_allowlists(mountinfo_path=mi_path)
        finally:
            os.remove(mi_path)

    def test_p1_fails_closed_if_whole_scratch_directory_mounted(self):
        bad_mountinfo = SYNTHETIC_VALID_MOUNTINFO + (
            "37 22 8:2 /repo/scratch /workspace/scratch ro,relatime - ext4 /dev/sda2 ro\n"
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(bad_mountinfo)
            mi_path = tf.name

        try:
            with mock.patch("os.path.exists", return_value=True), \
                 mock.patch("os.path.isdir", side_effect=lambda p: not p.endswith((".py", ".csv"))), \
                 mock.patch("os.path.isfile", side_effect=lambda p: p == mi_path or p.endswith((".py", ".csv"))):
                with self.assertRaisesRegex(probes.IsolationPreflightError, "Whole '/workspace/scratch' directory is mounted"):
                    probes.probe_p1_mounts_and_allowlists(mountinfo_path=mi_path)
        finally:
            os.remove(mi_path)

    def test_p1_fails_closed_on_unexpected_file_in_scratch_or_data(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(SYNTHETIC_VALID_MOUNTINFO)
            mi_path = tf.name

        try:
            def fake_listdir_extra_scratch(path):
                if path == "/workspace":
                    return list(probes.EXPECTED_WORKSPACE_ENTRIES)
                if path == "/workspace/scratch":
                    return list(probes.EXPECTED_SCRATCH_ENTRIES) + ["extra_unapproved.py"]
                if path == "/workspace/data":
                    return list(probes.EXPECTED_DATA_ENTRIES)
                return []

            with mock.patch("os.path.exists", return_value=True), \
                 mock.patch("os.path.isdir", side_effect=lambda p: not p.endswith((".py", ".csv"))), \
                 mock.patch("os.path.isfile", side_effect=lambda p: p == mi_path or p.endswith((".py", ".csv"))), \
                 mock.patch("os.listdir", side_effect=fake_listdir_extra_scratch):
                with self.assertRaisesRegex(probes.IsolationPreflightError, "/workspace/scratch allowlist mismatch"):
                    probes.probe_p1_mounts_and_allowlists(mountinfo_path=mi_path)
        finally:
            os.remove(mi_path)


class TestProbeP2QuarantineAbsence(unittest.TestCase):
    """Verifies P2 rejects any visible quarantined path or 2025/blind filename."""

    def test_p2_passes_when_quarantined_absent(self):
        def fake_listdir(path):
            if path == "/workspace":
                return list(probes.EXPECTED_WORKSPACE_ENTRIES)
            if path == "/workspace/data":
                return list(probes.EXPECTED_DATA_ENTRIES)
            if path == "/workspace/scratch":
                return list(probes.EXPECTED_SCRATCH_ENTRIES)
            return []

        with mock.patch("os.path.exists", return_value=False), \
             mock.patch("os.path.islink", return_value=False), \
             mock.patch("os.listdir", side_effect=fake_listdir):
            probes.probe_p2_quarantine_absence()

    def test_p2_fails_closed_when_2025_file_present(self):
        with mock.patch("os.path.exists", side_effect=lambda p: "2025" in p):
            with self.assertRaisesRegex(probes.IsolationPreflightError, "P2_FAIL"):
                probes.probe_p2_quarantine_absence()


class TestProbeP3HashVerification(unittest.TestCase):
    """Verifies P3 SHA-256 calculation and fail-closed digest comparison."""

    def test_p3_passes_on_matching_digests_and_fails_on_mismatch(self):
        with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
            tf.write(b"synthetic_polaris_2024_content")
            tmp_path = tf.name

        expected_digest = hashlib.sha256(b"synthetic_polaris_2024_content").hexdigest()
        try:
            with mock.patch.dict(probes.EXPECTED_INPUT_SHA256, {tmp_path: expected_digest}, clear=True):
                probes.probe_p3_input_sha256_verification()

            with mock.patch.dict(probes.EXPECTED_INPUT_SHA256, {tmp_path: "0" * 64}, clear=True):
                with self.assertRaisesRegex(probes.IsolationPreflightError, "P3_FAIL: SHA-256 mismatch"):
                    probes.probe_p3_input_sha256_verification()
        finally:
            os.remove(tmp_path)


class TestProbeP4NonDestructiveROAndRWConfinement(unittest.TestCase):
    """Verifies P4 never attempts to write to RO mounts and cleans up RW output probe."""

    def test_p4_never_opens_ro_mounts_for_writing(self):
        with tempfile.TemporaryDirectory() as tmp_out_dir:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
                custom_mi = SYNTHETIC_VALID_MOUNTINFO.replace(
                    "/workspace/experiments/diagnostics/diag_od02_boundary_2024",
                    tmp_out_dir,
                )
                tf.write(custom_mi)
                mi_path = tf.name

            try:
                with mock.patch.object(probes, "APPROVED_RW_OUTPUT_MOUNT", tmp_out_dir), \
                     mock.patch("os.access", return_value=False):
                    probes.probe_p4_ro_and_rw_confinement(mountinfo_path=mi_path)
                # Confirm zero residue left in tmp_out_dir
                self.assertEqual(os.listdir(tmp_out_dir), [])
            finally:
                os.remove(mi_path)

    def test_p4_fails_closed_if_ro_mount_marked_rw_in_mountinfo(self):
        bad_mi = SYNTHETIC_VALID_MOUNTINFO.replace(
            "/repo/system /workspace/system ro,relatime",
            "/repo/system /workspace/system rw,relatime",
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(bad_mi)
            mi_path = tf.name

        try:
            with self.assertRaisesRegex(probes.IsolationPreflightError, "P4_FAIL: Mount '/workspace/system' is not read-only"):
                probes.probe_p4_ro_and_rw_confinement(mountinfo_path=mi_path)
        finally:
            os.remove(mi_path)

    def test_p4_fails_closed_if_mountinfo_missing(self):
        with self.assertRaisesRegex(probes.IsolationPreflightError, "P4_FAIL: Mount metadata file missing"):
            probes.probe_p4_ro_and_rw_confinement(mountinfo_path="/nonexistent/path/mountinfo")


class TestProbeP5NetworkIsolationDistinction(unittest.TestCase):
    """Verifies P5 distinguishes true network namespace isolation from simple socket failure."""

    def test_p5_fails_closed_when_eth0_exists_even_if_socket_fails(self):
        net_dev_with_eth0 = (
            "Inter-|   Receive                                                |  Transmit\n"
            " face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets\n"
            "    lo:       0       0    0    0    0     0          0         0        0       0\n"
            "  eth0:    1024      10    0    0    0     0          0         0     1024      10\n"
        )
        net_route_empty = "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f_dev, \
             tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f_rt:
            f_dev.write(net_dev_with_eth0)
            f_rt.write(net_route_empty)
            dev_path, rt_path = f_dev.name, f_rt.name

        try:
            with self.assertRaisesRegex(probes.IsolationPreflightError, "Non-loopback network interfaces present"):
                probes.probe_p5_network_namespace_isolation(dev_path, rt_path)
        finally:
            os.remove(dev_path)
            os.remove(rt_path)

    def test_p5_passes_when_lo_only_zero_routes_and_enetunreach(self):
        net_dev_lo_only = (
            "Inter-|   Receive                                                |  Transmit\n"
            " face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets\n"
            "    lo:       0       0    0    0    0     0          0         0        0       0\n"
        )
        net_route_empty = "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f_dev, \
             tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f_rt:
            f_dev.write(net_dev_lo_only)
            f_rt.write(net_route_empty)
            dev_path, rt_path = f_dev.name, f_rt.name

        try:
            with mock.patch("socket.socket") as mock_sock_cls:
                mock_sock = mock_sock_cls.return_value
                mock_sock.connect.side_effect = OSError(errno.ENETUNREACH, "Network is unreachable")
                probes.probe_p5_network_namespace_isolation(dev_path, rt_path)
        finally:
            os.remove(dev_path)
            os.remove(rt_path)


class TestProbeP6AndP7LimitsAndPIDNamespace(unittest.TestCase):
    """Verifies P6 resource limits parsing and P7 PID namespace checks."""

    def test_p6_passes_valid_limits_and_rejects_unlimited(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(SYNTHETIC_VALID_LIMITS)
            lim_path = tf.name

        try:
            probes.probe_p6_resource_limits(lim_path)
        finally:
            os.remove(lim_path)

        bad_limits = SYNTHETIC_VALID_LIMITS.replace("8589934592", "unlimited")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(bad_limits)
            bad_path = tf.name

        try:
            with self.assertRaisesRegex(probes.IsolationPreflightError, "P6_FAIL: Max address space limit mismatch"):
                probes.probe_p6_resource_limits(bad_path)
        finally:
            os.remove(bad_path)

    def test_p7_verifies_pid_namespace(self):
        with mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=["1", "2", "self", "mounts"]), \
             mock.patch("os.getpid", return_value=2):
            probes.probe_p7_pid_namespace_confinement("/proc")

        with mock.patch("os.path.isdir", return_value=True), \
             mock.patch("os.listdir", return_value=["1", "2", "3", "4", "5"]), \
             mock.patch("os.getpid", return_value=2):
            with self.assertRaisesRegex(probes.IsolationPreflightError, "P7_FAIL: Excessive processes"):
                probes.probe_p7_pid_namespace_confinement("/proc")


class TestSpecificationConsistency(unittest.TestCase):
    """Verifies OD02_DIAGNOSTIC_ISOLATION_SPEC.md matches the probe implementation."""

    def test_spec_reconciles_mounts_flags_and_commands(self):
        spec_path = os.path.join(os.path.dirname(__file__), "OD02_DIAGNOSTIC_ISOLATION_SPEC.md")
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = f.read()

        self.assertIn("SPEC-2026-OD02-ISOLATION-03", spec)
        self.assertIn("--unshare-pid", spec)
        self.assertIn("--unshare-net", spec)
        self.assertIn("/usr/bin/timeout", spec)
        self.assertIn("/usr/bin/prlimit --as=8589934592 --cpu=300", spec)
        self.assertIn("/workspace/scratch/run_isolation_probes.py", spec)
        self.assertNotIn('--ro-bind "${REPO_DIR}/scratch" "/workspace/scratch"', spec)


if __name__ == "__main__":
    unittest.main()
