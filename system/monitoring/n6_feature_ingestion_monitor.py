"""
POLARIS — N6 Feature-Ingestion Observability Instrumentation
==============================================================
N6 Operational Readiness Remediation, Section 3.

GOVERNANCE STATUS: NON-PRODUCTION / PASSIVE INSTRUMENTATION ONLY
- Does not launch network requests. Does not modify upstream data.
- Does not alter `winner: null`, production routing, or any production
  controller/config file.
- Does not itself prove the live feature pipeline is operational -- it is
  instrumentation that a live caller (e.g. a future cron/daemon wired to
  `n6_operational_pipeline.py` / `meps_wind_extractor.py`) would call with
  REAL observed timestamps. Every timestamp this module reports is either
  (a) a value explicitly supplied by the caller (and in production, that
  value would come from a genuine observed clock/arrival event), or (b) an
  injectable `now_fn()` used only so tests are deterministic and offline.
  Passing a fixture or a hard-coded timestamp into this module does NOT, by
  itself, demonstrate real-world ingestion -- see
  `forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md` Section 4 (Operational
  Ingestion) for the explicit separation of "instrumentation implemented"
  vs. "live arrival-time evidence still required."

WHAT THIS MODULE DOES:
- Defines a structured, typed record of feature-readiness/provenance per
  N6 feature (one row per feature per forecast origin): expected source,
  source cycle, forecast origin, valid time, acquisition time, processing
  completion time, decision cutoff, missingness, validation failures,
  staleness, and provenance notes.
- Computes ACTUAL arrival/processing latency as a function of the
  timestamps passed in (never a hard-coded constant).
- Validates the 24-horizon contract and horizon-timestamp alignment.
- Validates a MEPS lead-time slice configuration against the documented
  lead[6:1:29] (horizons 1-24) convention.
- Checks that u700/v700 provenance tags indicate a genuine retrieved NWP
  field rather than a fabricated/imputed default, honoring the documented
  horizon 20-24 archive-coverage NaN exception.
- Fails closed (raises `IngestionIntegrityError`) whenever a required
  input is unavailable, stale, malformed, or reported later than the
  decision cutoff.
- Deliberately avoids logging credentials, secrets, personal data, or full
  raw telemetry payloads -- only scalar metadata (timestamps, booleans,
  short strings, counts) is retained on any record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

__all__ = [
    "IngestionIntegrityError",
    "FeatureProvenanceRecord",
    "FeatureIngestionMonitor",
    "DOCUMENTED_MEPS_LEAD_START",
    "DOCUMENTED_MEPS_LEAD_STRIDE",
    "DOCUMENTED_MEPS_LEAD_STOP",
    "EXPECTED_HORIZON_COUNT",
]


class IngestionIntegrityError(Exception):
    """
    Raised whenever this monitor detects that a required N6 input feature
    is unavailable, late, stale, malformed, misaligned, or of unverifiable
    provenance. Fail-closed by design: callers must not silently proceed
    on a caught IngestionIntegrityError.
    """


# Documented MEPS pressure-level lead-time slice for the 24-horizon window,
# per forecasting/stage7/.../candidate_n_additive_physics/meps_wind_extractor.py and
# operational_availability_audit/temporal_lineage.md.
DOCUMENTED_MEPS_LEAD_START: int = 6
DOCUMENTED_MEPS_LEAD_STRIDE: int = 1
DOCUMENTED_MEPS_LEAD_STOP: int = 29  # exclusive-style OPeNDAP slice upper bound -> 24 leads

EXPECTED_HORIZON_COUNT: int = 24

# Horizons (1-indexed) for which u700/v700 are permitted to be NaN due to the
# documented MEPS 18Z pressure-level archive coverage gap. Mirrors the policy
# enforced in system/forecasting/implementations/n6_solar.py.
U700_V700_PERMITTED_NAN_HORIZONS = frozenset(range(20, 25))

# Provenance tags that this monitor treats as evidence of a GENUINE retrieved
# physical field (never fabricated/imputed) for u700/v700.
GENUINE_NWP_PROVENANCE_TAGS = frozenset(
    {"meps_opendap_live_fetch", "meps_opendap_cached_fetch", "meps_archive_replay_verified"}
)
# Provenance tags that explicitly indicate a fabricated/imputed/default value
# and must therefore never be accepted for u700/v700 outside the permitted gap.
FABRICATED_PROVENANCE_TAGS = frozenset(
    {"synthetic_default", "mean_imputed", "zero_filled", "forward_filled_stale_default"}
)


def _default_now_fn() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as e:
        raise IngestionIntegrityError(f"Fail-closed: unparseable timestamp '{value}': {e}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class FeatureProvenanceRecord:
    """
    One feature-readiness record for a single (feature_name, forecast_origin)
    pair. Intentionally holds only scalar metadata -- never a raw telemetry
    series or payload -- per the "avoid logging full raw telemetry payloads"
    requirement.
    """

    feature_name: str
    schema_version: str
    expected_source: str
    source_cycle: Optional[str]          # e.g. "2024-06-01T18:00:00Z" (the 18Z NWP cycle)
    forecast_origin: str                  # decision-time origin timestamp
    valid_time: Optional[str]             # timestamp the feature value applies to
    acquisition_time: Optional[str]       # when the raw data was actually retrieved
    processing_completion_time: Optional[str]  # when feature engineering finished
    decision_cutoff: str                  # latest instant the value may arrive and still be usable
    missing: bool = False
    validation_failed: bool = False
    validation_failure_reason: Optional[str] = None
    stale: bool = False
    provenance_tag: Optional[str] = None
    arrival_latency_seconds: Optional[float] = None
    processing_latency_seconds: Optional[float] = None
    margin_to_cutoff_seconds: Optional[float] = None

    def to_safe_dict(self) -> Dict[str, object]:
        """Serializes only scalar metadata fields -- safe for logging."""
        return {
            "feature_name": self.feature_name,
            "schema_version": self.schema_version,
            "expected_source": self.expected_source,
            "source_cycle": self.source_cycle,
            "forecast_origin": self.forecast_origin,
            "valid_time": self.valid_time,
            "acquisition_time": self.acquisition_time,
            "processing_completion_time": self.processing_completion_time,
            "decision_cutoff": self.decision_cutoff,
            "missing": self.missing,
            "validation_failed": self.validation_failed,
            "validation_failure_reason": self.validation_failure_reason,
            "stale": self.stale,
            "provenance_tag": self.provenance_tag,
            "arrival_latency_seconds": self.arrival_latency_seconds,
            "processing_latency_seconds": self.processing_latency_seconds,
            "margin_to_cutoff_seconds": self.margin_to_cutoff_seconds,
        }


class FeatureIngestionMonitor:
    """
    Passive, non-production feature-readiness/provenance recorder for the
    N6 36-feature contract. Never performs network I/O itself -- callers
    (live or fixture-based) supply observed timestamps and provenance tags;
    this class only records, measures latency, and fails closed on policy
    violations.
    """

    def __init__(self, now_fn: Optional[Callable[[], datetime]] = None):
        self._now_fn = now_fn or _default_now_fn
        self.records: List[FeatureProvenanceRecord] = []

    # ------------------------------------------------------------------
    # Core recording
    # ------------------------------------------------------------------
    def record_feature_readiness(
        self,
        feature_name: str,
        expected_source: str,
        forecast_origin: str,
        decision_cutoff: str,
        schema_version: str = "1.0.0",
        source_cycle: Optional[str] = None,
        valid_time: Optional[str] = None,
        acquisition_time: Optional[str] = None,
        processing_completion_time: Optional[str] = None,
        missing: bool = False,
        provenance_tag: Optional[str] = None,
        fail_closed: bool = True,
    ) -> FeatureProvenanceRecord:
        """
        Records one feature-readiness observation and computes ACTUAL
        latency/staleness from the supplied timestamps (never hard-coded).

        Raises IngestionIntegrityError (when fail_closed=True, the default)
        if: the feature is missing, acquisition/processing times are absent
        for a non-missing feature, or processing completes after the
        decision cutoff (late/stale data).
        """
        cutoff_dt = _parse_ts(decision_cutoff)
        if cutoff_dt is None:
            raise IngestionIntegrityError("Fail-closed: decision_cutoff is required and was not provided.")

        origin_dt = _parse_ts(forecast_origin)
        source_cycle_dt = _parse_ts(source_cycle)
        acquisition_dt = _parse_ts(acquisition_time)
        processing_dt = _parse_ts(processing_completion_time)

        validation_failed = False
        failure_reason: Optional[str] = None
        stale = False
        arrival_latency_s: Optional[float] = None
        processing_latency_s: Optional[float] = None
        margin_s: Optional[float] = None

        if missing:
            validation_failed = True
            failure_reason = "feature_missing"
        else:
            if acquisition_dt is None or processing_dt is None:
                validation_failed = True
                failure_reason = "missing_acquisition_or_processing_timestamp"
            else:
                if source_cycle_dt is not None:
                    arrival_latency_s = (acquisition_dt - source_cycle_dt).total_seconds()
                processing_latency_s = (processing_dt - acquisition_dt).total_seconds()
                margin_s = (cutoff_dt - processing_dt).total_seconds()
                if margin_s < 0:
                    stale = True
                    validation_failed = True
                    failure_reason = (
                        f"late_arrival: processing completed {abs(margin_s):.0f}s after decision_cutoff"
                    )
                if processing_latency_s is not None and processing_latency_s < 0:
                    validation_failed = True
                    failure_reason = "processing_completion_before_acquisition"

        record = FeatureProvenanceRecord(
            feature_name=feature_name,
            schema_version=schema_version,
            expected_source=expected_source,
            source_cycle=source_cycle,
            forecast_origin=forecast_origin,
            valid_time=valid_time,
            acquisition_time=acquisition_time,
            processing_completion_time=processing_completion_time,
            decision_cutoff=decision_cutoff,
            missing=missing,
            validation_failed=validation_failed,
            validation_failure_reason=failure_reason,
            stale=stale,
            provenance_tag=provenance_tag,
            arrival_latency_seconds=arrival_latency_s,
            processing_latency_seconds=processing_latency_s,
            margin_to_cutoff_seconds=margin_s,
        )
        self.records.append(record)

        if fail_closed and validation_failed:
            raise IngestionIntegrityError(
                f"Fail-closed: feature '{feature_name}' failed ingestion readiness check: {failure_reason}"
            )
        return record

    # ------------------------------------------------------------------
    # Horizon / schema validation
    # ------------------------------------------------------------------
    @staticmethod
    def validate_horizon_alignment(
        timestamps: List[str], expected_count: int = EXPECTED_HORIZON_COUNT
    ) -> None:
        """
        Validates that exactly `expected_count` (default 24) horizon
        timestamps are present, strictly increasing, and hourly-spaced.
        Fails closed on any misalignment.
        """
        if len(timestamps) != expected_count:
            raise IngestionIntegrityError(
                f"Fail-closed: expected {expected_count} horizon timestamps, got {len(timestamps)}"
            )
        parsed = [_parse_ts(t) for t in timestamps]
        for i in range(1, len(parsed)):
            delta_h = (parsed[i] - parsed[i - 1]).total_seconds() / 3600.0
            if abs(delta_h - 1.0) > 1e-6:
                raise IngestionIntegrityError(
                    f"Fail-closed: horizon timestamps misaligned at index {i}: "
                    f"expected +1h spacing, got {delta_h}h"
                )

    @staticmethod
    def validate_meps_lead_window(
        lead_start: int, lead_stride: int, lead_stop: int, expected_horizon_count: int = EXPECTED_HORIZON_COUNT
    ) -> None:
        """
        Validates a MEPS OPeNDAP lead-time slice specification against the
        documented lead[6:1:29] 24-lead window (horizons 1..24). Fails
        closed if the configured slice does not produce exactly
        `expected_horizon_count` leads, or if it drifts from the documented
        convention.
        """
        if lead_stride <= 0:
            raise IngestionIntegrityError("Fail-closed: MEPS lead stride must be positive.")
        # OPeNDAP ASCII slice notation [start:stride:stop] is inclusive of both
        # endpoints (unlike Python's half-open range), so lead[6:1:29] yields
        # leads 6,7,...,29 inclusive = 24 leads.
        n_leads = len(range(lead_start, lead_stop + 1, lead_stride))
        if n_leads != expected_horizon_count:
            raise IngestionIntegrityError(
                f"Fail-closed: MEPS lead slice [{lead_start}:{lead_stride}:{lead_stop}] yields "
                f"{n_leads} leads, expected {expected_horizon_count}."
            )
        if (lead_start, lead_stride, lead_stop) != (
            DOCUMENTED_MEPS_LEAD_START,
            DOCUMENTED_MEPS_LEAD_STRIDE,
            DOCUMENTED_MEPS_LEAD_STOP,
        ):
            raise IngestionIntegrityError(
                f"Fail-closed: MEPS lead slice [{lead_start}:{lead_stride}:{lead_stop}] does not match "
                f"the documented convention [{DOCUMENTED_MEPS_LEAD_START}:{DOCUMENTED_MEPS_LEAD_STRIDE}:"
                f"{DOCUMENTED_MEPS_LEAD_STOP}]. This may indicate the known legacy truncation defect "
                f"(lead[7:1:25], horizons 20-24 missing)."
            )

    @staticmethod
    def check_u700_v700_provenance(horizon_hour: int, provenance_tag: Optional[str], is_nan: bool) -> None:
        """
        Validates that, for horizons where u700/v700 is NOT NaN, the
        provenance tag indicates a genuinely retrieved physical NWP field
        (never a fabricated/imputed default). Horizons 20-24 are permitted
        to be NaN per the documented MEPS 18Z archive-coverage gap; any
        other horizon reporting NaN, or any horizon reporting a fabricated
        provenance tag, fails closed.
        """
        if is_nan:
            if horizon_hour not in U700_V700_PERMITTED_NAN_HORIZONS:
                raise IngestionIntegrityError(
                    f"Fail-closed: u700/v700 NaN at horizon {horizon_hour}, which is outside the "
                    f"permitted archive-coverage gap (horizons 20-24)."
                )
            return
        if provenance_tag in FABRICATED_PROVENANCE_TAGS:
            raise IngestionIntegrityError(
                f"Fail-closed: u700/v700 at horizon {horizon_hour} carries a fabricated/imputed "
                f"provenance tag '{provenance_tag}'. N6 forbids synthetic substitution for this field."
            )
        if provenance_tag not in GENUINE_NWP_PROVENANCE_TAGS:
            raise IngestionIntegrityError(
                f"Fail-closed: u700/v700 at horizon {horizon_hour} carries an unrecognized provenance "
                f"tag '{provenance_tag}'; cannot verify it is a genuine retrieved physical field."
            )

    # ------------------------------------------------------------------
    # Aggregate reporting
    # ------------------------------------------------------------------
    def summary(self) -> Dict[str, object]:
        """
        Returns an aggregate, scalar-only summary of all recorded features:
        counts of missing/stale/validation-failed, and per-feature safe dicts.
        Never includes raw telemetry payloads.
        """
        return {
            "n_features_recorded": len(self.records),
            "n_missing": sum(1 for r in self.records if r.missing),
            "n_validation_failed": sum(1 for r in self.records if r.validation_failed),
            "n_stale": sum(1 for r in self.records if r.stale),
            "records": [r.to_safe_dict() for r in self.records],
        }
