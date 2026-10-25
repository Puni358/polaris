"""
Versioned schema for POLARIS operational-evidence records (EVID-01/FOR-01).

This module defines the ONE structured record shape used by the append-only
logger (`logger.py`) for all three required evidence streams named in
`remediation_plan.md` / register item `EVID-01`:
    1. MEPS 18Z forecast-input + wind/pressure-level product fetches.
    2. SITES Nuolja station-telemetry fetches.
    3. Stage 3b benchmark/inference executions.

Design rules (binding on every field in this module):
  - A timestamp field is either `None` (explicitly missing -- never silently
    defaulted) or an ISO-8601 string with an EXPLICIT UTC offset
    (`+00:00` or `Z`). A naive (offset-less) timestamp is a validation
    error, not something this module "helpfully" coerces -- an ingestion
    daemon that cannot tell this module what timezone a timestamp is in
    has a bug, and this module must not paper over it.
  - `source_identity`/`station_identity`/`process_run_id` are always
    non-empty strings when a record is CONSTRUCTED successfully; a record
    that cannot name its own source is rejected at construction, not
    logged with a blank field.
  - No field in this schema is ever filled with a smoke-test constant, a
    filesystem mtime (see `receipt_time_is_mtime_proxy` below, which exists
    specifically to make a weak proxy EXPLICIT rather than indistinguishable
    from a real process-arrival timestamp), or any other invented value.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

SCHEMA_VERSION = "1.0.0"


class InputType(str, Enum):
    """The three evidence streams EVID-01 / FOR-01 require evidence for."""

    MEPS_18Z = "MEPS_18Z_FORECAST_INPUT"
    SITES_TELEMETRY = "SITES_STATION_TELEMETRY"
    STAGE_3B_BENCHMARK = "STAGE_3B_BENCHMARK_EXECUTION"


class FetchOutcome(str, Enum):
    """
    Explicit outcome of one fetch/execution attempt. `SUCCESS` is the only
    outcome for which downstream-ready timestamps are expected to be
    non-None; every other value is a first-class, loggable outcome in its
    own right -- never silently dropped or merged into `SUCCESS`.
    """

    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    TIMEOUT = "TIMEOUT"
    FAILURE = "FAILURE"
    MISSING = "MISSING"
    STALE = "STALE"


class EvidenceSchemaError(ValueError):
    """
    Raised when a caller attempts to construct an `OperationalEvidenceRecord`
    that violates this schema's explicit rules (naive timestamp, blank
    identity field, inconsistent outcome/timestamp combination, etc). This
    is a construction-time, fail-closed error -- it is never caught and
    silently downgraded to a logged-anyway record.
    """


def _require_tz_aware_iso8601(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Returns `value` unchanged if it is `None` (explicitly missing -- a
    legitimate, honest state) or a syntactically valid ISO-8601 string that
    carries an EXPLICIT UTC offset. Raises `EvidenceSchemaError` for a
    naive timestamp (no offset) or an unparseable string. Never invents, un-
    sets, or "repairs" a bad value -- this is validation, not correction.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise EvidenceSchemaError(f"{field_name}: must be None or a non-empty ISO-8601 string, got {value!r}")
    normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except Exception as exc:
        raise EvidenceSchemaError(f"{field_name}: unparseable ISO-8601 timestamp {value!r}: {exc}") from exc
    if parsed.tzinfo is None:
        raise EvidenceSchemaError(
            f"{field_name}: timestamp {value!r} has no explicit UTC offset. This schema requires "
            "explicit timezone handling (e.g. '...+00:00' or '...Z') -- a naive timestamp is rejected "
            "rather than silently assumed to be UTC."
        )
    if parsed.utcoffset() != timezone.utc.utcoffset(None):
        raise EvidenceSchemaError(
            f"{field_name}: timestamp {value!r} carries a non-UTC offset. All operational-evidence "
            "timestamps must be recorded in UTC explicitly."
        )
    return value


def _non_empty_str(value: Optional[str], field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceSchemaError(f"{field_name}: must be a non-empty string, got {value!r}")
    return value


@dataclass(frozen=True)
class OperationalEvidenceRecord:
    """
    One immutable evidence record for a single fetch/execution attempt of
    one of the three EVID-01 input streams. Every instance is validated at
    construction time (`__post_init__`) -- there is no "construct now,
    validate later" path, so a malformed record can never reach the logger.
    """

    # --- identity -----------------------------------------------------
    schema_version: str = SCHEMA_VERSION
    input_type: str = ""                     # one of InputType values
    source_identity: str = ""                # e.g. "MET Norway MEPS THREDDS", "SITES Nuolja Middle Station"
    station_or_origin_identity: str = ""      # station id, or forecast-origin timestamp, as applicable
    process_run_id: str = ""                  # unique id for the daemon/process invocation that produced this record
    software_version: str = ""                # ingestion daemon / client software+config version string

    # --- forecast/telemetry addressing (None when not applicable) ------
    source_cycle: Optional[str] = None        # e.g. the 18Z NWP cycle, ISO-8601 UTC
    valid_time: Optional[str] = None          # timestamp the fetched value applies to, ISO-8601 UTC
    lead_time_hours: Optional[float] = None   # forecast lead time in hours, if applicable

    # --- lifecycle timestamps (ISO-8601, explicit UTC offset, or None) -
    provider_publication_time: Optional[str] = None   # when the UPSTREAM PROVIDER published/made available
    local_receipt_time: Optional[str] = None           # when THIS process first observed/received it
    fetch_start_time: Optional[str] = None
    fetch_end_time: Optional[str] = None
    ingestion_time: Optional[str] = None                # when raw payload ingestion completed
    validation_time: Optional[str] = None               # when schema/sanity validation completed
    downstream_ready_time: Optional[str] = None         # when the value became usable by a downstream consumer

    # --- outcome ---------------------------------------------------------
    outcome: str = FetchOutcome.MISSING.value
    retry_count: int = 0
    is_missing: bool = False
    is_stale: bool = False
    failure_reason: Optional[str] = None

    # --- weak-proxy flag (per directive: never substitute mtime for
    # process-arrival time unless explicitly labeled and excluded from
    # acceptance evidence) --------------------------------------------
    receipt_time_is_mtime_proxy: bool = False

    # --- provenance --------------------------------------------------
    provenance_note: str = ""                 # free text: exactly where this record's data/timestamps came from
    extra: Dict[str, str] = field(default_factory=dict)  # scalar-only, no raw payload

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _non_empty_str(self.schema_version, "schema_version"))
        valid_input_types = {t.value for t in InputType}
        if self.input_type not in valid_input_types:
            raise EvidenceSchemaError(
                f"input_type: must be one of {sorted(valid_input_types)}, got {self.input_type!r}"
            )
        _non_empty_str(self.source_identity, "source_identity")
        _non_empty_str(self.station_or_origin_identity, "station_or_origin_identity")
        _non_empty_str(self.process_run_id, "process_run_id")
        _non_empty_str(self.software_version, "software_version")
        _non_empty_str(self.provenance_note, "provenance_note")

        valid_outcomes = {o.value for o in FetchOutcome}
        if self.outcome not in valid_outcomes:
            raise EvidenceSchemaError(f"outcome: must be one of {sorted(valid_outcomes)}, got {self.outcome!r}")

        for fname in (
            "source_cycle", "valid_time", "provider_publication_time", "local_receipt_time",
            "fetch_start_time", "fetch_end_time", "ingestion_time", "validation_time",
            "downstream_ready_time",
        ):
            _require_tz_aware_iso8601(getattr(self, fname), fname)

        if self.retry_count < 0:
            raise EvidenceSchemaError("retry_count: must be >= 0")

        if self.outcome == FetchOutcome.SUCCESS.value:
            if self.is_missing:
                raise EvidenceSchemaError("outcome=SUCCESS is inconsistent with is_missing=True")
            if self.downstream_ready_time is None:
                raise EvidenceSchemaError(
                    "outcome=SUCCESS requires a non-None downstream_ready_time -- a successful fetch "
                    "that never became downstream-ready is a contradiction, not a loggable success."
                )
        if self.outcome == FetchOutcome.MISSING.value and not self.is_missing:
            raise EvidenceSchemaError("outcome=MISSING requires is_missing=True")
        if self.outcome == FetchOutcome.STALE.value and not self.is_stale:
            raise EvidenceSchemaError("outcome=STALE requires is_stale=True")
        if self.outcome in (FetchOutcome.FAILURE.value, FetchOutcome.TIMEOUT.value) and not self.failure_reason:
            raise EvidenceSchemaError(
                f"outcome={self.outcome} requires a non-empty failure_reason naming what went wrong."
            )
        if self.receipt_time_is_mtime_proxy and self.local_receipt_time is None:
            raise EvidenceSchemaError(
                "receipt_time_is_mtime_proxy=True requires local_receipt_time to be set (the proxy value "
                "itself) -- the flag exists to LABEL a weak proxy, not to excuse an absent timestamp."
            )

    def to_dict(self) -> Dict[str, object]:
        """Scalar-only serialization (JSON-safe), one evidence record per call."""
        d = asdict(self)
        return d

    # ------------------------------------------------------------------
    # Derived, read-only metrics (never written back into the record)
    # ------------------------------------------------------------------
    def provider_to_receipt_latency_seconds(self) -> Optional[float]:
        """
        Provider-publication-time to local-receipt-time latency, computed
        ONLY from the two timestamps this record actually carries. Returns
        None (never 0.0 or any other invented value) when either timestamp
        is absent.
        """
        if self.provider_publication_time is None or self.local_receipt_time is None:
            return None
        pub = datetime.fromisoformat(self.provider_publication_time.replace("Z", "+00:00"))
        recv = datetime.fromisoformat(self.local_receipt_time.replace("Z", "+00:00"))
        return (recv - pub).total_seconds()

    def fetch_duration_seconds(self) -> Optional[float]:
        if self.fetch_start_time is None or self.fetch_end_time is None:
            return None
        start = datetime.fromisoformat(self.fetch_start_time.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.fetch_end_time.replace("Z", "+00:00"))
        return (end - start).total_seconds()

    def margin_to_deadline_seconds(self, deadline_iso8601_utc: str) -> Optional[float]:
        """
        Computes (deadline - downstream_ready_time) in seconds against a
        CALLER-SUPPLIED deadline (this module invents no deadline of its
        own -- see `summarizer.py`, which only accepts deadlines already
        documented elsewhere in the repository). Returns None if this
        record has no downstream_ready_time.
        """
        if self.downstream_ready_time is None:
            return None
        deadline = _require_tz_aware_iso8601(deadline_iso8601_utc, "deadline_iso8601_utc")
        ready = datetime.fromisoformat(self.downstream_ready_time.replace("Z", "+00:00"))
        dl = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        return (dl - ready).total_seconds()
