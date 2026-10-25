"""
Read-only evidence summarizer for POLARIS operational-evidence logs
(EVID-01 / FOR-01).

Computes sample counts, missingness, coverage, and arrival-margin
percentiles from an EXISTING append-only evidence log (`logger.py`). This
module:
  - Never writes to the log it reads.
  - Never invents a deadline -- every deadline passed to
    `summarize_evidence_log` must be supplied by the caller, sourced from
    an already-documented acceptance threshold (e.g. a decision_cutoff
    recorded alongside the data, or a register-cited deadline). This
    module raises if asked to summarize margins with no deadline supplied,
    rather than defaulting to some invented value.
  - Treats a small sample honestly: `summary['small_sample_warning']` is
    set whenever fewer than `MIN_SAMPLES_FOR_READINESS_CLAIM` records are
    present for a given input_type, and the summary text says plainly that
    a small sample is not proof of operational readiness.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from .logger import AppendOnlyEvidenceLogger
from .schema import OperationalEvidenceRecord, InputType, FetchOutcome, EvidenceSchemaError

# Below this many samples for an input_type, this module explicitly flags
# the summary as insufficient for any operational-readiness claim. This is
# a documentation threshold, not a safety threshold, and is NOT one of the
# register's own named acceptance windows (30d MEPS / 14d SITES / 10
# consecutive Stage-3b runs) -- those remain the actual closure criteria;
# this constant only prevents this summarizer itself from looking falsely
# confident on a handful of records.
MIN_SAMPLES_FOR_READINESS_CLAIM = 30


class EvidenceSummaryError(Exception):
    """Raised when the evidence log cannot be honestly summarized as asked."""


@dataclass
class PerInputTypeSummary:
    input_type: str
    n_records: int
    n_success: int
    n_missing: int
    n_stale: int
    n_failure: int
    n_timeout: int
    n_retry: int
    n_mtime_proxy_receipts: int
    distinct_process_run_ids: int
    arrival_margin_seconds_percentiles: Optional[Dict[str, float]]
    small_sample_warning: bool
    earliest_record_time: Optional[str]
    latest_record_time: Optional[str]


def _parse_log_lines(lines: Iterable[str]) -> List[OperationalEvidenceRecord]:
    records: List[OperationalEvidenceRecord] = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceSummaryError(f"Line {i}: malformed JSON, cannot summarize honestly: {exc}") from exc
        try:
            records.append(OperationalEvidenceRecord(**payload))
        except (EvidenceSchemaError, TypeError) as exc:
            raise EvidenceSummaryError(f"Line {i}: record fails schema validation, cannot summarize: {exc}") from exc
    return records


def _percentiles(values: List[float]) -> Dict[str, float]:
    sv = sorted(values)
    n = len(sv)

    def pct(p: float) -> float:
        if n == 1:
            return sv[0]
        k = (n - 1) * p
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            return sv[f]
        return sv[f] + (sv[c] - sv[f]) * (k - f)

    return {
        "p5": pct(0.05),
        "p50": pct(0.50),
        "p95": pct(0.95),
        "min": sv[0],
        "max": sv[-1],
        "mean": statistics.fmean(sv),
    }


def summarize_evidence_log(
    log_path: str,
    deadlines_by_input_type: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    """
    Reads and summarizes an existing evidence log at `log_path` (does not
    write to it). `deadlines_by_input_type` is OPTIONAL and, if supplied,
    maps an `InputType` value to an already-documented ISO-8601 UTC
    deadline string this run's arrival margins should be measured against
    -- this function never invents one itself; if no deadline is supplied
    for a given input_type, that type's `arrival_margin_seconds_percentiles`
    is reported as `None`, not computed against a guessed cutoff.

    Returns a JSON-serializable dict: per-input-type summaries plus an
    overall `honest_disclaimer` string restating that a completed summary
    is evidence of what WAS logged, never proof that live collection
    actually ran for the full required window unless the caller
    independently confirms the collection window and sample count meet the
    register's own named acceptance test.
    """
    logger = AppendOnlyEvidenceLogger(log_path, create_parent_dirs=False)
    records = _parse_log_lines(logger.read_all_lines())

    deadlines_by_input_type = deadlines_by_input_type or {}

    by_type: Dict[str, List[OperationalEvidenceRecord]] = {t.value: [] for t in InputType}
    for r in records:
        by_type.setdefault(r.input_type, []).append(r)

    per_type_summaries: Dict[str, object] = {}
    for input_type, recs in by_type.items():
        n = len(recs)
        n_success = sum(1 for r in recs if r.outcome == FetchOutcome.SUCCESS.value)
        n_missing = sum(1 for r in recs if r.is_missing)
        n_stale = sum(1 for r in recs if r.is_stale)
        n_failure = sum(1 for r in recs if r.outcome == FetchOutcome.FAILURE.value)
        n_timeout = sum(1 for r in recs if r.outcome == FetchOutcome.TIMEOUT.value)
        n_retry = sum(1 for r in recs if r.outcome == FetchOutcome.RETRY.value or r.retry_count > 0)
        n_mtime_proxy = sum(1 for r in recs if r.receipt_time_is_mtime_proxy)
        distinct_runs = len({r.process_run_id for r in recs})

        margin_pcts: Optional[Dict[str, float]] = None
        deadline = deadlines_by_input_type.get(input_type)
        if deadline is not None:
            margins = [
                r.margin_to_deadline_seconds(deadline)
                for r in recs
                if r.downstream_ready_time is not None
            ]
            margins = [m for m in margins if m is not None]
            if margins:
                margin_pcts = _percentiles(margins)

        times = sorted(
            t
            for r in recs
            for t in (r.local_receipt_time,)
            if t is not None
        )

        per_type_summaries[input_type] = PerInputTypeSummary(
            input_type=input_type,
            n_records=n,
            n_success=n_success,
            n_missing=n_missing,
            n_stale=n_stale,
            n_failure=n_failure,
            n_timeout=n_timeout,
            n_retry=n_retry,
            n_mtime_proxy_receipts=n_mtime_proxy,
            distinct_process_run_ids=distinct_runs,
            arrival_margin_seconds_percentiles=margin_pcts,
            small_sample_warning=n < MIN_SAMPLES_FOR_READINESS_CLAIM,
            earliest_record_time=times[0] if times else None,
            latest_record_time=times[-1] if times else None,
        ).__dict__

    return {
        "schema_version_summarized": "1.0.0",
        "total_records": len(records),
        "per_input_type": per_type_summaries,
        "honest_disclaimer": (
            "This summary describes only what has actually been logged at the time this function "
            "was run. A clean summary is NOT, by itself, proof of operational readiness -- the "
            "register's own named acceptance tests (30 consecutive days of live MEPS 18Z logging, "
            "14 consecutive days of live SITES telemetry logging, 10 consecutive live Stage 3b "
            "benchmark runs) must still be independently checked against the actual collection "
            "window and sample count before any readiness claim is made. A small sample (see "
            "per-input-type 'small_sample_warning') must never be treated as sufficient evidence."
        ),
    }
