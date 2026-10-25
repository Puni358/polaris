"""
Strict validator + read-only completeness/quality report for per-origin
station-state evidence submissions (EVID-02-adjacent initial-state
evidence, Workstream C).

Reuses, rather than duplicates, the EXISTING, authoritative validation
contract in `system/evaluation/n6_multi_origin_harness/adapters.py`:
`resolve_and_validate_authoritative_initial_state`, `REQUIRED_STATION_STATE_FIELDS`,
`PROVENANCE_FIELD`, `AuthoritativeInitialStateUnavailableError`, and
`MalformedInitialStateRecordError`. This script does not re-implement, re-
specify, or loosen any of that logic -- it imports it unchanged.

This script never fills a missing field. Every missing core field or
missing provenance citation is reported as a failure, with the exact
`MalformedInitialStateRecordError` message surfaced; the script's output
distinguishes "core validation passed" from "extended evidence-quality
metadata complete" (Section docs/evidence_acquisition/schemas/
station_state_evidence_schema.json) -- the latter is informational only
and never silently promotes an incomplete record to "validated".

Usage:
    python3 tools/evidence_acquisition/validate_station_state_evidence.py <submission.json>

`submission.json` must be a JSON object mapping origin_id -> a station-state
evidence record (see the example in the schema file above).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import os

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from system.evaluation.n6_multi_origin_harness.adapters import (  # noqa: E402
    resolve_and_validate_authoritative_initial_state,
    AuthoritativeInitialStateUnavailableError,
    MalformedInitialStateRecordError,
    REQUIRED_STATION_STATE_FIELDS,
    PROVENANCE_FIELD,
)

EXTENDED_METADATA_FIELDS = (
    "station_identity",
    "measurement_timestamp_utc",
    "source_reference",
    "calibration_quality_metadata",
)


def validate_submission(submission: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates every origin in `submission` against the real, unchanged
    `resolve_and_validate_authoritative_initial_state` contract, and
    separately reports extended-metadata completeness (informational,
    non-blocking). Returns a JSON-serializable report; writes nothing.
    """
    per_origin: Dict[str, Any] = {}
    n_core_pass = 0
    n_core_fail = 0

    for origin_id, record in submission.items():
        registry = {origin_id: record}
        core_result: Dict[str, Any] = {"origin_id": origin_id}
        try:
            validated = resolve_and_validate_authoritative_initial_state(origin_id, registry)
            core_result["core_validation"] = "PASS"
            core_result["core_validation_detail"] = (
                f"All {len(REQUIRED_STATION_STATE_FIELDS)} required StationState fields present; "
                f"'{PROVENANCE_FIELD}' citation present and non-blank."
            )
            n_core_pass += 1
        except (AuthoritativeInitialStateUnavailableError, MalformedInitialStateRecordError) as exc:
            core_result["core_validation"] = "FAIL"
            core_result["core_validation_detail"] = str(exc)
            n_core_fail += 1
            validated = None

        present_extended = [f for f in EXTENDED_METADATA_FIELDS if record.get(f) not in (None, "")]
        missing_extended = [f for f in EXTENDED_METADATA_FIELDS if f not in present_extended]
        core_result["extended_metadata_completeness"] = {
            "present": present_extended,
            "missing": missing_extended,
            "completeness_fraction": len(present_extended) / len(EXTENDED_METADATA_FIELDS),
        }
        per_origin[origin_id] = core_result

    n_origins = len(submission)
    return {
        "schema_version": "1.0.0",
        "n_origins_submitted": n_origins,
        "n_core_validation_pass": n_core_pass,
        "n_core_validation_fail": n_core_fail,
        "per_origin": per_origin,
        "honest_disclaimer": (
            "A PASS here means the record satisfies the StationState construction contract and "
            "carries a non-blank provenance citation -- it does NOT independently verify that the "
            "citation is accurate, that the underlying measurement is real, or that the station "
            "operator who supplied it is authoritative. No missing field was filled in by this "
            "script. Extended-metadata completeness is informational only and never upgrades a "
            "core FAIL to a PASS."
        ),
    }


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: python3 tools/evidence_acquisition/validate_station_state_evidence.py <submission.json>")
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"VALIDATION FAILED: file does not exist: {path}")
        return 1
    with open(path, "r", encoding="utf-8") as fh:
        submission = json.load(fh)
    report = validate_submission(submission)
    print(json.dumps(report, indent=2))
    return 0 if report["n_core_validation_fail"] == 0 and report["n_origins_submitted"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
