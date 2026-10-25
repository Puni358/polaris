"""
POLARIS -- Operational Evidence Logging Package
=================================================
EVID-01 / FOR-01 instrumentation (N6 Operational Evidence & Governance
Campaign, Workstream B).

GOVERNANCE STATUS: NON-PRODUCTION / PASSIVE INSTRUMENTATION ONLY.
This package never performs network I/O, never fabricates a timestamp, and
is never imported by any production dispatch/safety/control-flow module
(`system/control/`, `system/runtime/`, `system/orchestration/`,
`system/optimization/implementations/`, `system/simulation/simulator.py`).
It exists so that a FUTURE, separately-authorized live-ingestion daemon
(for MEPS 18Z pressure-level fetches, SITES Nuolja telemetry, or Stage 3b
benchmark execution) has a ready-to-deploy, tested, versioned-schema,
append-only logger to call at each real lifecycle event. No real daemon
has been deployed and no live evidence has been collected by this package
in this pass -- see `docs/evidence_acquisition/EVID01_FOR01_ACQUISITION_PACKAGE.md`
for the exact deployment steps and the explicit, honest statement that zero
real operational evidence exists yet.
"""

from .schema import (
    SCHEMA_VERSION,
    InputType,
    FetchOutcome,
    OperationalEvidenceRecord,
)
from .logger import (
    EvidenceLoggingError,
    AppendOnlyEvidenceLogger,
)
from .summarizer import (
    summarize_evidence_log,
    EvidenceSummaryError,
)

__all__ = [
    "SCHEMA_VERSION",
    "InputType",
    "FetchOutcome",
    "OperationalEvidenceRecord",
    "EvidenceLoggingError",
    "AppendOnlyEvidenceLogger",
    "summarize_evidence_log",
    "EvidenceSummaryError",
]
