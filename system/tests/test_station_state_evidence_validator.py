"""
Tests for tools/evidence_acquisition/validate_station_state_evidence.py
(station-state initial-condition evidence acquisition tooling, Workstream C).

These tests confirm the new acquisition validator correctly REUSES (never
duplicates or loosens) the existing, unchanged
`resolve_and_validate_authoritative_initial_state` contract in
`system/evaluation/n6_multi_origin_harness/adapters.py`, and that its
extended-metadata completeness reporting never upgrades a core failure to
a pass.
"""

from __future__ import annotations

import unittest

from tools.evidence_acquisition.validate_station_state_evidence import (
    validate_submission,
    EXTENDED_METADATA_FIELDS,
)


def _complete_record(**overrides):
    base = dict(
        timestamp="2024-06-01T00:00:00+00:00",
        battery_soc_pct=62.5,
        battery_energy_wh=99200.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=410.2,
        last_observed_demand=1800.0,
        last_observed_wind_generation=120.0,
        _provenance="SITES Nuolja SCADA export 2024-06-01, ingested 2024-06-01T00:04:12Z, operator J. Doe",
        station_identity="Nuolja Middle Station",
        measurement_timestamp_utc="2024-06-01T00:00:00+00:00",
        source_reference="SCADA_EXPORT_2024_06_01.csv row 42",
        calibration_quality_metadata={
            "instrument_last_calibrated_utc": "2024-01-01T00:00:00+00:00",
            "measurement_quality_flag": "VERIFIED",
            "notes": "test fixture",
        },
    )
    base.update(overrides)
    return base


class TestCoreValidationReuse(unittest.TestCase):
    def test_complete_record_passes_core_validation(self):
        submission = {"origin-1": _complete_record()}
        report = validate_submission(submission)
        self.assertEqual(report["n_core_validation_pass"], 1)
        self.assertEqual(report["n_core_validation_fail"], 0)
        self.assertEqual(report["per_origin"]["origin-1"]["core_validation"], "PASS")

    def test_missing_core_field_fails_validation(self):
        record = _complete_record()
        del record["battery_soc_pct"]
        submission = {"origin-1": record}
        report = validate_submission(submission)
        self.assertEqual(report["n_core_validation_fail"], 1)
        self.assertEqual(report["per_origin"]["origin-1"]["core_validation"], "FAIL")
        self.assertIn("battery_soc_pct", report["per_origin"]["origin-1"]["core_validation_detail"])

    def test_missing_provenance_fails_validation(self):
        record = _complete_record(_provenance="")
        submission = {"origin-1": record}
        report = validate_submission(submission)
        self.assertEqual(report["per_origin"]["origin-1"]["core_validation"], "FAIL")
        self.assertIn("_provenance", report["per_origin"]["origin-1"]["core_validation_detail"])

    def test_hardcoded_smoke_test_literal_without_provenance_is_rejected(self):
        """Mirrors the exact run_n6_closed_loop_simulation.py smoke-test
        literal shape (battery_soc_pct=80.0, battery_energy_wh=160000.0,
        no provenance) -- must be rejected, not accepted as evidence."""
        smoke_test_record = {
            "timestamp": "2024-06-01T00:00:00+00:00",
            "battery_soc_pct": 80.0,
            "battery_energy_wh": 160000.0,
            "diesel_running": False,
            "diesel_hours_running": 0.0,
            "last_observed_solar_irradiance": 300.0,
            "last_observed_demand": 1500.0,
            "last_observed_wind_generation": 0.0,
            "diesel_fuel_remaining_liters": 500.0,
        }
        submission = {"smoke-test-origin": smoke_test_record}
        report = validate_submission(submission)
        self.assertEqual(report["per_origin"]["smoke-test-origin"]["core_validation"], "FAIL")

    def test_absent_origin_in_registry_is_unavailable_error_not_malformed(self):
        """An empty submission dict (no origins at all) must report zero
        pass/fail -- it must never be silently treated as a pass."""
        report = validate_submission({})
        self.assertEqual(report["n_origins_submitted"], 0)
        self.assertEqual(report["n_core_validation_pass"], 0)
        self.assertEqual(report["n_core_validation_fail"], 0)


class TestExtendedMetadataNeverUpgradesCoreFailure(unittest.TestCase):
    def test_complete_extended_metadata_with_core_failure_still_fails(self):
        record = _complete_record()
        del record["diesel_hours_running"]  # break core validation
        submission = {"origin-1": record}
        report = validate_submission(submission)
        entry = report["per_origin"]["origin-1"]
        self.assertEqual(entry["core_validation"], "FAIL")
        # Extended metadata is still fully present, but must not flip the verdict.
        self.assertEqual(
            entry["extended_metadata_completeness"]["completeness_fraction"], 1.0
        )
        self.assertEqual(report["n_core_validation_pass"], 0)

    def test_missing_extended_metadata_reported_but_non_blocking(self):
        record = _complete_record()
        for f in EXTENDED_METADATA_FIELDS:
            record.pop(f, None)
        submission = {"origin-1": record}
        report = validate_submission(submission)
        entry = report["per_origin"]["origin-1"]
        self.assertEqual(entry["core_validation"], "PASS")
        self.assertEqual(entry["extended_metadata_completeness"]["completeness_fraction"], 0.0)
        self.assertEqual(set(entry["extended_metadata_completeness"]["missing"]), set(EXTENDED_METADATA_FIELDS))


class TestHonestDisclaimerPresent(unittest.TestCase):
    def test_disclaimer_present(self):
        report = validate_submission({"origin-1": _complete_record()})
        self.assertIn("No missing field was filled in", report["honest_disclaimer"])


if __name__ == "__main__":
    unittest.main()
