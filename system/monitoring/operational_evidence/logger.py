"""
Append-only, versioned-schema structured logger for POLARIS operational
evidence (EVID-01 / FOR-01).

GOVERNANCE STATUS: NON-PRODUCTION INSTRUMENTATION ONLY. This module writes
to a plain, local, append-only JSONL file. It never performs network I/O,
never deletes or rewrites a previously-written line, and is never imported
by any production dispatch/safety/control-flow module.

Failure policy (binding): a logging failure is ALWAYS explicit. If a write
cannot be completed (disk full, permission denied, path missing, a record
that fails schema validation), this module raises -- it never swallows the
error and returns as if the write succeeded. A caller that wants
best-effort logging must choose to catch the raised exception itself; this
module will not make that choice silently on the caller's behalf.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Iterator, Optional

from .schema import OperationalEvidenceRecord, SCHEMA_VERSION, EvidenceSchemaError


class EvidenceLoggingError(Exception):
    """
    Raised whenever a write to the append-only evidence log cannot be
    completed, or a record fails schema validation before the write is
    attempted. Never caught internally and converted to a silent no-op.
    """


class AppendOnlyEvidenceLogger:
    """
    Writes one JSON object per line (JSONL) to `log_path`, opening the file
    in append mode ('a') on every write so a crash mid-write can never
    truncate or corrupt previously-written lines. Thread-safe for use from
    a single process via an internal lock; NOT safe for concurrent writers
    across separate processes to the same file without external
    coordination (a future live daemon should use one logger instance per
    process, one file per process-run-id, or an external lock -- this
    module does not implement cross-process locking itself).
    """

    def __init__(self, log_path: str, create_parent_dirs: bool = True) -> None:
        self.log_path = Path(log_path)
        if create_parent_dirs:
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise EvidenceLoggingError(
                    f"Could not create parent directory for evidence log '{log_path}': {exc}"
                ) from exc
        self._lock = threading.Lock()

    def append(self, record: OperationalEvidenceRecord) -> None:
        """
        Validates `record` is actually an `OperationalEvidenceRecord` of
        the schema version this logger expects, serializes it to one JSON
        line, and appends it. Raises `EvidenceLoggingError` on ANY failure
        -- malformed input, schema-version mismatch, or an OS-level write
        failure -- rather than returning normally.
        """
        if not isinstance(record, OperationalEvidenceRecord):
            raise EvidenceLoggingError(
                f"append() requires an OperationalEvidenceRecord instance, got {type(record).__name__}"
            )
        if record.schema_version != SCHEMA_VERSION:
            raise EvidenceLoggingError(
                f"Record schema_version {record.schema_version!r} does not match this logger's "
                f"expected version {SCHEMA_VERSION!r}. Refusing to log a version-mismatched record "
                "rather than silently writing it as if it conformed."
            )
        try:
            line = json.dumps(record.to_dict(), sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise EvidenceLoggingError(f"Record could not be JSON-serialized: {exc}") from exc

        with self._lock:
            try:
                with open(self.log_path, "a", encoding="utf-8") as fh:
                    fh.write(line)
                    fh.write("\n")
                    fh.flush()
                    os.fsync(fh.fileno())
            except OSError as exc:
                raise EvidenceLoggingError(
                    f"Failed to append evidence record to '{self.log_path}': {exc}"
                ) from exc

    def read_all_lines(self) -> Iterator[str]:
        """
        Read-only iteration over the raw JSONL lines currently on disk.
        Does not validate or parse -- see `summarizer.py` for that. Raises
        `EvidenceLoggingError` if the file cannot be read (NOT if it simply
        does not exist yet -- an unopened log is empty, not an error).
        """
        if not self.log_path.exists():
            return iter(())
        try:
            with open(self.log_path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            raise EvidenceLoggingError(f"Failed to read evidence log '{self.log_path}': {exc}") from exc
        return iter(lines)


def build_record_or_raise(**kwargs) -> OperationalEvidenceRecord:
    """
    Thin, explicit construction helper: builds an `OperationalEvidenceRecord`
    from keyword arguments and lets `EvidenceSchemaError` propagate
    unchanged on any violation. Exists only so call sites can write
    `build_record_or_raise(...)` instead of `OperationalEvidenceRecord(...)`
    directly -- behavior is identical; this is a readability aid, not a
    different validation path.
    """
    return OperationalEvidenceRecord(**kwargs)
