"""
POLARIS — N6 Feature-Ingestion Observability Test Suite
==========================================================
N6 Operational Readiness Remediation, Section 3.

Exercises `system/monitoring/n6_feature_ingestion_monitor.py` against
synthetic, injectable timestamps -- never live network data. Covers: schema
and failure paths including delayed data, missing horizons, timestamp
misalignment, NaN/u700-v700 provenance, stale telemetry, and the documented
MEPS lead-window convention vs. the known legacy truncation defect.

GOVERNANCE: non-production, fixture-only. No network access. Does not alter
winner: null or production configuration.
"""

from __future__ import annotations

import unittest

from system.monitoring.n6_feature_ingestion_monitor import (
    FeatureIngestionMonitor,
    IngestionIntegrityError,
    DOCUMENTED_MEPS_LEAD_START,
    DOCUMENTED_MEPS_LEAD_STRIDE,
    DOCUMENTED_MEPS_LEAD_STOP,
)


class TestFeatureIngestionMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = FeatureIngestionMonitor()

    def test_01_healthy_feature_readiness_records_latency(self):
        """A feature that arrives and is processed before cutoff records positive latencies, no failure."""
        rec = self.monitor.record_feature_readiness(
            feature_name="fc_cloud_cover",
            expected_source="MEPS_18Z_PRESSURE_ARCHIVE",
            forecast_origin="2024-06-01T00:00:00Z",
            decision_cutoff="2024-05-31T22:00:00Z",
            source_cycle="2024-05-31T18:00:00Z",
            acquisition_time="2024-05-31T19:30:00Z",
            processing_completion_time="2024-05-31T19:45:00Z",
            provenance_tag="meps_opendap_live_fetch",
        )
        self.assertFalse(rec.validation_failed)
        self.assertFalse(rec.stale)
        self.assertEqual(rec.arrival_latency_seconds, 5400.0)   # 1.5h
        self.assertEqual(rec.processing_latency_seconds, 900.0)  # 15min
        self.assertEqual(rec.margin_to_cutoff_seconds, 8100.0)   # 2h15m before cutoff

    def test_02_missing_feature_fails_closed(self):
        """A feature explicitly flagged missing raises IngestionIntegrityError."""
        with self.assertRaises(IngestionIntegrityError) as cm:
            self.monitor.record_feature_readiness(
                feature_name="u700",
                expected_source="MEPS_18Z_PRESSURE_ARCHIVE",
                forecast_origin="2024-06-01T00:00:00Z",
                decision_cutoff="2024-05-31T22:00:00Z",
                missing=True,
            )
        self.assertIn("feature_missing", str(cm.exception))

    def test_03_late_arrival_after_cutoff_fails_closed_and_flags_stale(self):
        """Processing completing AFTER decision_cutoff must fail closed and set stale=True."""
        with self.assertRaises(IngestionIntegrityError) as cm:
            self.monitor.record_feature_readiness(
                feature_name="lwp_18z_fc",
                expected_source="MEPS_18Z_PRESSURE_ARCHIVE",
                forecast_origin="2024-06-01T00:00:00Z",
                decision_cutoff="2024-05-31T22:00:00Z",
                source_cycle="2024-05-31T18:00:00Z",
                acquisition_time="2024-05-31T23:00:00Z",
                processing_completion_time="2024-05-31T23:15:00Z",
                provenance_tag="meps_opendap_live_fetch",
            )
        self.assertIn("late_arrival", str(cm.exception))
        self.assertEqual(len(self.monitor.records), 1)
        self.assertTrue(self.monitor.records[0].stale)

    def test_04_fail_closed_can_be_disabled_for_non_blocking_audit_mode(self):
        """With fail_closed=False, the record is still captured (and marked failed) without raising."""
        rec = self.monitor.record_feature_readiness(
            feature_name="iwp_18z_fc",
            expected_source="MEPS_18Z_PRESSURE_ARCHIVE",
            forecast_origin="2024-06-01T00:00:00Z",
            decision_cutoff="2024-05-31T22:00:00Z",
            missing=True,
            fail_closed=False,
        )
        self.assertTrue(rec.validation_failed)
        self.assertEqual(self.monitor.summary()["n_missing"], 1)

    def test_05_missing_acquisition_timestamp_fails_closed(self):
        """A non-missing feature with no acquisition/processing timestamps still fails closed."""
        with self.assertRaises(IngestionIntegrityError) as cm:
            self.monitor.record_feature_readiness(
                feature_name="ctx_std_6h",
                expected_source="SITES_NUOLJA_TELEMETRY",
                forecast_origin="2024-06-01T00:00:00Z",
                decision_cutoff="2024-05-31T22:00:00Z",
            )
        self.assertIn("missing_acquisition_or_processing_timestamp", str(cm.exception))

    def test_06_horizon_alignment_rejects_wrong_count(self):
        timestamps = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        FeatureIngestionMonitor.validate_horizon_alignment(timestamps)  # 24 -> OK

        with self.assertRaises(IngestionIntegrityError):
            FeatureIngestionMonitor.validate_horizon_alignment(timestamps[:19])  # missing horizons

    def test_07_horizon_alignment_rejects_misaligned_spacing(self):
        timestamps = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        timestamps[10] = "2024-06-01T10:30:00Z"  # introduce a half-hour skew
        with self.assertRaises(IngestionIntegrityError):
            FeatureIngestionMonitor.validate_horizon_alignment(timestamps)

    def test_08_meps_lead_window_accepts_documented_convention(self):
        FeatureIngestionMonitor.validate_meps_lead_window(
            DOCUMENTED_MEPS_LEAD_START, DOCUMENTED_MEPS_LEAD_STRIDE, DOCUMENTED_MEPS_LEAD_STOP
        )  # should not raise

    def test_09_meps_lead_window_rejects_legacy_truncated_defect(self):
        """The known legacy truncated slice lead[7:1:25] (19 leads, missing h20-24) must fail closed."""
        with self.assertRaises(IngestionIntegrityError) as cm:
            FeatureIngestionMonitor.validate_meps_lead_window(7, 1, 25)
        self.assertIn("19 leads", str(cm.exception))

    def test_10_meps_lead_window_rejects_right_count_wrong_window(self):
        """A slice that coincidentally produces 24 leads but drifts from the documented window still fails."""
        with self.assertRaises(IngestionIntegrityError):
            FeatureIngestionMonitor.validate_meps_lead_window(5, 1, 28)  # 24 leads, wrong start/stop

    def test_11_u700_v700_permitted_nan_gap_h20_to_h24(self):
        for h in range(20, 25):
            FeatureIngestionMonitor.check_u700_v700_provenance(h, provenance_tag=None, is_nan=True)

    def test_12_u700_v700_unexpected_nan_before_h20_fails_closed(self):
        with self.assertRaises(IngestionIntegrityError):
            FeatureIngestionMonitor.check_u700_v700_provenance(5, provenance_tag=None, is_nan=True)

    def test_13_u700_v700_fabricated_provenance_fails_closed(self):
        with self.assertRaises(IngestionIntegrityError) as cm:
            FeatureIngestionMonitor.check_u700_v700_provenance(
                3, provenance_tag="synthetic_default", is_nan=False
            )
        self.assertIn("fabricated/imputed", str(cm.exception))

    def test_14_u700_v700_genuine_provenance_passes(self):
        FeatureIngestionMonitor.check_u700_v700_provenance(
            3, provenance_tag="meps_opendap_live_fetch", is_nan=False
        )  # should not raise

    def test_15_u700_v700_unrecognized_provenance_fails_closed(self):
        with self.assertRaises(IngestionIntegrityError):
            FeatureIngestionMonitor.check_u700_v700_provenance(
                3, provenance_tag="unknown_source_xyz", is_nan=False
            )

    def test_16_summary_contains_no_raw_payload_fields(self):
        """Summary/records must only ever contain scalar metadata, never a raw series/payload key."""
        self.monitor.record_feature_readiness(
            feature_name="fc_temperature_2m",
            expected_source="MEPS_18Z_PRESSURE_ARCHIVE",
            forecast_origin="2024-06-01T00:00:00Z",
            decision_cutoff="2024-05-31T22:00:00Z",
            source_cycle="2024-05-31T18:00:00Z",
            acquisition_time="2024-05-31T19:00:00Z",
            processing_completion_time="2024-05-31T19:05:00Z",
            provenance_tag="meps_opendap_live_fetch",
        )
        summary = self.monitor.summary()
        for rec in summary["records"]:
            for forbidden_key in ("raw_payload", "raw_series", "telemetry_values", "credentials", "token"):
                self.assertNotIn(forbidden_key, rec)


if __name__ == "__main__":
    unittest.main()
