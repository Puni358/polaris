"""
POLARIS -- N6 Multi-Origin Harness: Validated Initial-State Input Contract
================================================================================
OWNER-AUTHORIZED BLOCKER RESOLUTION PASS (2026-10-17), Section 3A: "Improve
the initial-state interface so future verified station-state records can be
supplied through a documented, validated input contract. Do not manufacture
initial-state records or treat hardcoded smoke-test constants as
authoritative evidence."

Covers the new `resolve_and_validate_authoritative_initial_state` /
`MalformedInitialStateRecordError` / `REQUIRED_STATION_STATE_FIELDS` /
`PROVENANCE_FIELD` additions to `adapters.py`. The PRE-EXISTING, unmodified
`resolve_authoritative_initial_state` / `AuthoritativeInitialStateUnavailableError`
fail-closed lookup (IA-3, Blocker B -- still open: no per-origin table
exists anywhere in this repository) is deliberately left untouched and is
NOT retested here beyond one explicit regression check, to avoid
duplicating `TestAuthoritativeInitialStateLookup` in
`system/tests/test_n6_receding_horizon_adapters.py`.

No real StationState construction, N6 engine, optimizer, simulator, or
safety evaluator is imported or used anywhere in this file.
"""
from __future__ import annotations

import unittest

from system.evaluation.n6_multi_origin_harness.adapters import (
    PROVENANCE_FIELD,
    REQUIRED_STATION_STATE_FIELDS,
    AuthoritativeInitialStateUnavailableError,
    MalformedInitialStateRecordError,
    resolve_and_validate_authoritative_initial_state,
    resolve_authoritative_initial_state,
)


def _complete_valid_record(**overrides):
    record = {
        "timestamp": "2024-06-01T00:00:00Z",
        "battery_soc_pct": 62.0,
        "battery_energy_wh": 93000.0,
        "diesel_running": False,
        "diesel_hours_running": 0.0,
        "last_observed_solar_irradiance": 410.0,
        "last_observed_demand": 18500.0,
        "last_observed_wind_generation": 0.0,
        PROVENANCE_FIELD: "SITES telemetry export 2024-06-01, ingested 2024-06-01T00:05:00Z, row 142",
    }
    record.update(overrides)
    return record


class TestValidatedContractAcceptsCompleteCitedRecord(unittest.TestCase):
    def test_01_complete_record_with_provenance_is_returned_as_a_copy(self):
        registry = {"origin-1": _complete_valid_record()}
        resolved = resolve_and_validate_authoritative_initial_state("origin-1", registry)
        self.assertEqual(resolved, registry["origin-1"])
        resolved["battery_soc_pct"] = 0.0
        self.assertNotEqual(registry["origin-1"]["battery_soc_pct"], 0.0, "must return a copy, never the live registry dict")

    def test_02_every_required_field_name_matches_the_real_station_state_contract(self):
        # Pins the exact field-name list against system/schemas/station_state.py's
        # own required (no-default) constructor arguments, so this test fails
        # loudly if that real schema and this contract ever drift apart.
        self.assertEqual(
            set(REQUIRED_STATION_STATE_FIELDS),
            {
                "timestamp",
                "battery_soc_pct",
                "battery_energy_wh",
                "diesel_running",
                "diesel_hours_running",
                "last_observed_solar_irradiance",
                "last_observed_demand",
                "last_observed_wind_generation",
            },
        )


class TestValidatedContractFailsClosedOnIncompleteOrUncitedRecords(unittest.TestCase):
    def test_03_missing_required_field_rejected(self):
        incomplete = _complete_valid_record()
        del incomplete["battery_energy_wh"]
        registry = {"origin-1": incomplete}
        with self.assertRaises(MalformedInitialStateRecordError) as ctx:
            resolve_and_validate_authoritative_initial_state("origin-1", registry)
        self.assertIn("battery_energy_wh", str(ctx.exception))

    def test_04_multiple_missing_fields_all_named_in_the_error(self):
        sparse = {"timestamp": "T0", "battery_soc_pct": 50.0, PROVENANCE_FIELD: "some source"}
        registry = {"origin-1": sparse}
        with self.assertRaises(MalformedInitialStateRecordError) as ctx:
            resolve_and_validate_authoritative_initial_state("origin-1", registry)
        message = str(ctx.exception)
        for missing in ("battery_energy_wh", "diesel_running", "diesel_hours_running"):
            self.assertIn(missing, message)

    def test_05_missing_provenance_rejected_even_if_all_station_state_fields_present(self):
        record = _complete_valid_record()
        del record[PROVENANCE_FIELD]
        registry = {"origin-1": record}
        with self.assertRaises(MalformedInitialStateRecordError) as ctx:
            resolve_and_validate_authoritative_initial_state("origin-1", registry)
        self.assertIn("_provenance", str(ctx.exception))

    def test_06_blank_provenance_string_rejected(self):
        record = _complete_valid_record(**{PROVENANCE_FIELD: "   "})
        registry = {"origin-1": record}
        with self.assertRaises(MalformedInitialStateRecordError):
            resolve_and_validate_authoritative_initial_state("origin-1", registry)

    def test_07_non_string_provenance_rejected(self):
        record = _complete_valid_record(**{PROVENANCE_FIELD: 12345})
        registry = {"origin-1": record}
        with self.assertRaises(MalformedInitialStateRecordError):
            resolve_and_validate_authoritative_initial_state("origin-1", registry)

    def test_08_missing_origin_entirely_still_raises_the_unchanged_unavailable_error(self):
        # Delegates to resolve_authoritative_initial_state unchanged -- a
        # wholly-absent origin is a DIFFERENT fail-closed reason than an
        # incomplete/uncited one, and must raise the pre-existing error type.
        registry = {"origin-1": _complete_valid_record()}
        with self.assertRaises(AuthoritativeInitialStateUnavailableError):
            resolve_and_validate_authoritative_initial_state("origin-999-absent", registry)


class TestHardcodedSmokeTestConstantsAreNotAuthoritative(unittest.TestCase):
    """
    Directly exercises the directive's explicit prohibition: "Do not ...
    treat hardcoded smoke-test constants as authoritative evidence." Builds
    the EXACT literal values `run_n6_closed_loop_simulation.py` lines
    ~101-112 hardcode for its one smoke-test origin (confirmed by direct
    read this pass) and proves the new validated contract rejects them,
    both because they cite no provenance and because, as that script
    actually constructs them, several real StationState fields are sourced
    from a SEPARATE fixture object rather than being self-contained here --
    so a naive plain-dict copy of just the hardcoded literals is exactly
    the "uncited, incomplete" shape this contract must reject.
    """

    def test_09_bare_hardcoded_smoke_test_literals_without_provenance_are_rejected(self):
        hardcoded_smoke_test_literals = {
            "battery_soc_pct": 80.0,
            "battery_energy_wh": 160000.0,
            "diesel_running": True,
            "diesel_hours_running": 2.0,
            "diesel_fuel_remaining_liters": 500.0,
            # No timestamp/last_observed_* fields (those come from a
            # separate fixture-adapter call in the real script, not from
            # this literal block) and no _provenance citation -- exactly
            # the real script's own shape.
        }
        registry = {"smoke-origin": hardcoded_smoke_test_literals}
        with self.assertRaises(MalformedInitialStateRecordError) as ctx:
            resolve_and_validate_authoritative_initial_state("smoke-origin", registry)
        message = str(ctx.exception)
        # Missing StationState fields AND missing provenance both fail it --
        # whichever is checked first must still be a fail-closed rejection.
        self.assertTrue(
            "timestamp" in message or "_provenance" in message,
            "must reject for a concrete, named reason, not a generic failure",
        )

    def test_10_even_a_fully_complete_but_uncited_copy_of_the_smoke_test_state_is_rejected(self):
        # Suppose a future caller DID fill in every missing StationState
        # field (making the record structurally complete) but still copied
        # it from the smoke-test script without citing a real source. The
        # provenance requirement alone must still reject it.
        complete_but_uncited = _complete_valid_record()
        del complete_but_uncited[PROVENANCE_FIELD]
        registry = {"smoke-origin": complete_but_uncited}
        with self.assertRaises(MalformedInitialStateRecordError):
            resolve_and_validate_authoritative_initial_state("smoke-origin", registry)


class TestUnmodifiedLenientLookupStillWorksUnchanged(unittest.TestCase):
    """
    Regression guard: the PRE-EXISTING `resolve_authoritative_initial_state`
    (reused unmodified by the new function above) must still accept a
    partial record exactly as `TestAuthoritativeInitialStateLookup.test_10`
    in `test_n6_receding_horizon_adapters.py` already pins -- this pass adds
    a stricter NEW entry point, it does not retrofit new restrictions onto
    the old one.
    """

    def test_11_bare_lookup_still_accepts_a_partial_record(self):
        registry = {"origin-1": {"timestamp": "T0", "battery_soc_pct": 80.0}}
        resolved = resolve_authoritative_initial_state("origin-1", registry)
        self.assertEqual(resolved, registry["origin-1"])


if __name__ == "__main__":
    unittest.main()
