"""
Tests for system/monitoring/operational_evidence/ (EVID-01 / FOR-01
instrumentation). Covers: timestamp/timezone validation, missing-field
rejection, duplicate/retried fetches, failed fetches, malformed records,
and provenance requirements -- per the governing directive's explicit
test-coverage list for this workstream.

These tests exercise ONLY this new, non-production instrumentation
package. No production dispatch/safety/control-flow module is imported.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest

from system.monitoring.operational_evidence.schema import (
    OperationalEvidenceRecord,
    EvidenceSchemaError,
    InputType,
    FetchOutcome,
    SCHEMA_VERSION,
)
from system.monitoring.operational_evidence.logger import (
    AppendOnlyEvidenceLogger,
    EvidenceLoggingError,
    build_record_or_raise,
)
from system.monitoring.operational_evidence.summarizer import (
    summarize_evidence_log,
    EvidenceSummaryError,
    MIN_SAMPLES_FOR_READINESS_CLAIM,
)


def _success_record(**overrides) -> OperationalEvidenceRecord:
    base = dict(
        input_type=InputType.MEPS_18Z.value,
        source_identity="MET Norway MEPS THREDDS",
        station_or_origin_identity="2024-06-01T18:00:00+00:00",
        process_run_id="run-0001",
        software_version="daemon-v0.0.0-test",
        source_cycle="2024-06-01T18:00:00+00:00",
        valid_time="2024-06-02T00:00:00+00:00",
        lead_time_hours=6.0,
        provider_publication_time="2024-06-01T19:05:00+00:00",
        local_receipt_time="2024-06-01T19:07:30+00:00",
        fetch_start_time="2024-06-01T19:07:00+00:00",
        fetch_end_time="2024-06-01T19:07:30+00:00",
        ingestion_time="2024-06-01T19:07:45+00:00",
        validation_time="2024-06-01T19:07:50+00:00",
        downstream_ready_time="2024-06-01T19:08:00+00:00",
        outcome=FetchOutcome.SUCCESS.value,
        provenance_note="test fixture: synthetic timestamps for unit test only, not real evidence",
    )
    base.update(overrides)
    return OperationalEvidenceRecord(**base)


class TestSchemaTimestampAndTimezoneValidation(unittest.TestCase):
    def test_valid_utc_offset_accepted(self):
        rec = _success_record()
        self.assertEqual(rec.schema_version, SCHEMA_VERSION)

    def test_z_suffix_accepted_as_utc(self):
        rec = _success_record(local_receipt_time="2024-06-01T19:07:30Z")
        self.assertEqual(rec.local_receipt_time, "2024-06-01T19:07:30Z")

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(EvidenceSchemaError) as ctx:
            _success_record(local_receipt_time="2024-06-01T19:07:30")
        self.assertIn("explicit", str(ctx.exception).lower())

    def test_non_utc_offset_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(local_receipt_time="2024-06-01T19:07:30+05:30")

    def test_unparseable_timestamp_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(local_receipt_time="not-a-timestamp")

    def test_none_timestamp_is_explicitly_allowed(self):
        rec = _success_record(
            provider_publication_time=None,
            outcome=FetchOutcome.MISSING.value,
            is_missing=True,
            downstream_ready_time=None,
        )
        self.assertIsNone(rec.provider_publication_time)


class TestMissingAndIdentityFields(unittest.TestCase):
    def test_blank_source_identity_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(source_identity="")

    def test_blank_process_run_id_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(process_run_id="   ")

    def test_invalid_input_type_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(input_type="NOT_A_REAL_INPUT_TYPE")

    def test_missing_outcome_requires_is_missing_flag(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(outcome=FetchOutcome.MISSING.value, is_missing=False)

    def test_success_outcome_requires_downstream_ready_time(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(downstream_ready_time=None)

    def test_success_outcome_inconsistent_with_is_missing(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(is_missing=True)


class TestProvenanceRequirement(unittest.TestCase):
    def test_blank_provenance_note_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(provenance_note="")

    def test_whitespace_only_provenance_note_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(provenance_note="   ")

    def test_mtime_proxy_flag_requires_receipt_time(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(receipt_time_is_mtime_proxy=True, local_receipt_time=None,
                             provider_publication_time=None)

    def test_mtime_proxy_flag_allowed_when_receipt_time_present(self):
        rec = _success_record(receipt_time_is_mtime_proxy=True)
        self.assertTrue(rec.receipt_time_is_mtime_proxy)


class TestFailedAndRetriedAndTimeoutOutcomes(unittest.TestCase):
    def test_failure_requires_reason(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(
                outcome=FetchOutcome.FAILURE.value,
                downstream_ready_time=None,
                failure_reason=None,
            )

    def test_failure_with_reason_accepted(self):
        rec = _success_record(
            outcome=FetchOutcome.FAILURE.value,
            downstream_ready_time=None,
            failure_reason="connection_refused",
        )
        self.assertEqual(rec.outcome, FetchOutcome.FAILURE.value)

    def test_timeout_requires_reason(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(
                outcome=FetchOutcome.TIMEOUT.value,
                downstream_ready_time=None,
                failure_reason="",
            )

    def test_negative_retry_count_rejected(self):
        with self.assertRaises(EvidenceSchemaError):
            _success_record(retry_count=-1)

    def test_retry_outcome_with_positive_retry_count_accepted(self):
        rec = _success_record(
            outcome=FetchOutcome.RETRY.value,
            downstream_ready_time=None,
            retry_count=3,
        )
        self.assertEqual(rec.retry_count, 3)

    def test_duplicate_retried_fetch_logged_as_separate_records(self):
        """Two attempts of the SAME logical fetch (same source_cycle) must
        both be logged as distinct records -- the logger must never merge,
        dedupe, or overwrite a prior attempt."""
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            logger = AppendOnlyEvidenceLogger(log_path)
            attempt_1 = _success_record(
                outcome=FetchOutcome.RETRY.value,
                downstream_ready_time=None,
                retry_count=1,
                process_run_id="run-dup-1",
            )
            attempt_2 = _success_record(process_run_id="run-dup-2")
            logger.append(attempt_1)
            logger.append(attempt_2)
            lines = list(logger.read_all_lines())
            self.assertEqual(len(lines), 2)
            parsed = [json.loads(l) for l in lines]
            self.assertEqual(parsed[0]["process_run_id"], "run-dup-1")
            self.assertEqual(parsed[1]["process_run_id"], "run-dup-2")


class TestMalformedRecordRejection(unittest.TestCase):
    def test_logger_rejects_non_record_object(self):
        with tempfile.TemporaryDirectory() as d:
            logger = AppendOnlyEvidenceLogger(os.path.join(d, "evidence.jsonl"))
            with self.assertRaises(EvidenceLoggingError):
                logger.append({"not": "a record"})  # type: ignore[arg-type]

    def test_logger_rejects_schema_version_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            logger = AppendOnlyEvidenceLogger(os.path.join(d, "evidence.jsonl"))
            rec = _success_record()
            object.__setattr__(rec, "schema_version", "99.0.0")
            with self.assertRaises(EvidenceLoggingError):
                logger.append(rec)

    def test_summarizer_rejects_malformed_json_line(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            with open(log_path, "w", encoding="utf-8") as fh:
                fh.write("{not valid json\n")
            with self.assertRaises(EvidenceSummaryError):
                summarize_evidence_log(log_path)

    def test_summarizer_rejects_record_missing_required_field(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            with open(log_path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"input_type": "MEPS_18Z_FORECAST_INPUT"}) + "\n")
            with self.assertRaises(EvidenceSummaryError):
                summarize_evidence_log(log_path)

    def test_build_record_or_raise_propagates_schema_error(self):
        with self.assertRaises(EvidenceSchemaError):
            build_record_or_raise(
                input_type=InputType.SITES_TELEMETRY.value,
                source_identity="",
                station_or_origin_identity="x",
                process_run_id="r1",
                software_version="v1",
                outcome=FetchOutcome.MISSING.value,
                is_missing=True,
                provenance_note="x",
            )


class TestLoggerFailureIsExplicit(unittest.TestCase):
    def test_append_raises_on_unwritable_directory(self):
        with tempfile.TemporaryDirectory() as d:
            unwritable_dir = os.path.join(d, "ro")
            os.mkdir(unwritable_dir, mode=0o500)
            log_path = os.path.join(unwritable_dir, "nested", "evidence.jsonl")
            try:
                with self.assertRaises(EvidenceLoggingError):
                    AppendOnlyEvidenceLogger(log_path)
            finally:
                os.chmod(unwritable_dir, 0o700)

    def test_read_all_lines_on_nonexistent_file_is_empty_not_error(self):
        with tempfile.TemporaryDirectory() as d:
            logger = AppendOnlyEvidenceLogger(os.path.join(d, "evidence.jsonl"))
            self.assertEqual(list(logger.read_all_lines()), [])


class TestSummarizerCoverageAndMissingness(unittest.TestCase):
    def test_empty_log_summarizes_to_zero_with_small_sample_warning(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            AppendOnlyEvidenceLogger(log_path)  # creates parent dirs only
            summary = summarize_evidence_log(log_path)
            self.assertEqual(summary["total_records"], 0)
            meps_summary = summary["per_input_type"][InputType.MEPS_18Z.value]
            self.assertEqual(meps_summary["n_records"], 0)
            self.assertTrue(meps_summary["small_sample_warning"])

    def test_small_sample_warning_true_below_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            logger = AppendOnlyEvidenceLogger(log_path)
            self.assertLess(5, MIN_SAMPLES_FOR_READINESS_CLAIM)
            for i in range(5):
                logger.append(_success_record(process_run_id=f"run-{i}"))
            summary = summarize_evidence_log(log_path)
            meps_summary = summary["per_input_type"][InputType.MEPS_18Z.value]
            self.assertEqual(meps_summary["n_records"], 5)
            self.assertEqual(meps_summary["n_success"], 5)
            self.assertTrue(meps_summary["small_sample_warning"])

    def test_missing_and_failure_counts_tracked_separately(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            logger = AppendOnlyEvidenceLogger(log_path)
            logger.append(_success_record(process_run_id="run-ok"))
            logger.append(_success_record(
                process_run_id="run-missing",
                outcome=FetchOutcome.MISSING.value,
                is_missing=True,
                downstream_ready_time=None,
                provider_publication_time=None,
                local_receipt_time=None,
                fetch_start_time=None,
                fetch_end_time=None,
                ingestion_time=None,
                validation_time=None,
            ))
            logger.append(_success_record(
                process_run_id="run-fail",
                outcome=FetchOutcome.FAILURE.value,
                downstream_ready_time=None,
                failure_reason="server_error_500",
            ))
            summary = summarize_evidence_log(log_path)
            meps_summary = summary["per_input_type"][InputType.MEPS_18Z.value]
            self.assertEqual(meps_summary["n_records"], 3)
            self.assertEqual(meps_summary["n_success"], 1)
            self.assertEqual(meps_summary["n_missing"], 1)
            self.assertEqual(meps_summary["n_failure"], 1)

    def test_no_deadline_supplied_yields_none_margin_percentiles(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            logger = AppendOnlyEvidenceLogger(log_path)
            logger.append(_success_record())
            summary = summarize_evidence_log(log_path)  # no deadlines_by_input_type
            meps_summary = summary["per_input_type"][InputType.MEPS_18Z.value]
            self.assertIsNone(meps_summary["arrival_margin_seconds_percentiles"])

    def test_deadline_supplied_yields_margin_percentiles(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            logger = AppendOnlyEvidenceLogger(log_path)
            logger.append(_success_record())
            summary = summarize_evidence_log(
                log_path,
                deadlines_by_input_type={InputType.MEPS_18Z.value: "2024-06-01T20:00:00+00:00"},
            )
            meps_summary = summary["per_input_type"][InputType.MEPS_18Z.value]
            self.assertIsNotNone(meps_summary["arrival_margin_seconds_percentiles"])
            self.assertAlmostEqual(
                meps_summary["arrival_margin_seconds_percentiles"]["p50"],
                3120.0,  # 20:00:00 - 19:08:00 = 52 minutes = 3120s
                places=1,
            )

    def test_honest_disclaimer_present_and_mentions_small_sample(self):
        with tempfile.TemporaryDirectory() as d:
            log_path = os.path.join(d, "evidence.jsonl")
            AppendOnlyEvidenceLogger(log_path)
            summary = summarize_evidence_log(log_path)
            self.assertIn("NOT", summary["honest_disclaimer"])
            self.assertIn("small_sample_warning", summary["honest_disclaimer"])


if __name__ == "__main__":
    unittest.main()
