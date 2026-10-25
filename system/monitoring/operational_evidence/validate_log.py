"""
Standalone validation script for an operational-evidence JSONL log
(EVID-01 / FOR-01). Read-only: never writes to the log it checks.

Usage:
    python3 -m system.monitoring.operational_evidence.validate_log <path-to-log.jsonl>

Exit code 0: every line parsed as valid JSON and validated against
`OperationalEvidenceRecord`'s schema (including the explicit-UTC-offset
timestamp rule). Exit code 1: at least one line failed; every failure is
printed with its 0-based line number and the exact validation error, never
silently skipped.

This script performs no network access and imports no production
dispatch/safety/control-flow module.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .schema import OperationalEvidenceRecord, EvidenceSchemaError


def validate_file(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"VALIDATION FAILED: log file does not exist: {path}")
        return 1

    n_lines = 0
    n_ok = 0
    failures = []
    with open(p, "r", encoding="utf-8") as fh:
        for i, raw in enumerate(fh):
            raw = raw.strip()
            if not raw:
                continue
            n_lines += 1
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                failures.append((i, f"malformed JSON: {exc}"))
                continue
            try:
                OperationalEvidenceRecord(**payload)
            except (EvidenceSchemaError, TypeError) as exc:
                failures.append((i, f"schema validation failed: {exc}"))
                continue
            n_ok += 1

    print(f"Checked {n_lines} non-blank line(s): {n_ok} valid, {len(failures)} invalid.")
    for line_no, reason in failures:
        print(f"  Line {line_no}: {reason}")

    if failures:
        print("VALIDATION FAILED.")
        return 1
    print("VALIDATION PASSED (schema-conformance only -- this does NOT certify the records "
          "describe a real live-collection window; see the summarizer for coverage/sample-count context).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 -m system.monitoring.operational_evidence.validate_log <path-to-log.jsonl>")
        sys.exit(2)
    sys.exit(validate_file(sys.argv[1]))
