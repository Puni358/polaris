# EVID-01 / FOR-01 — Live Operational-Evidence Acquisition Package

**Date prepared:** 2026-10-17
**Register items this package serves:** `EVID-01` (live MEPS-18Z/SITES/Stage-3b arrival-time logging) and, through it, `FOR-01` (PASS-vs-UNPROVEN N6 operational-readiness contradiction).
**Status: NO REAL EVIDENCE WAS COLLECTED IN THIS PASS.** This pass is an offline coding session with no network access, no station credentials, and no access to live MET Norway THREDDS, SITES telemetry, or Stage 3b execution infrastructure. Everything in this document is implementation and acquisition planning, not operational data.

---

## 1. What this package contains

1. A ready-to-deploy, tested, versioned-schema append-only logger: `system/monitoring/operational_evidence/` (`schema.py`, `logger.py`, `summarizer.py`, `validate_log.py`).
2. A deployment config template: `system/monitoring/operational_evidence/config_template.json`.
3. 35 passing focused tests: `system/tests/test_operational_evidence_logger.py` (timestamp/timezone validation, missing-field rejection, duplicate/retried fetches, failed/timeout outcomes, malformed-record rejection, provenance requirement, read-only summarizer behavior).
4. This deployment/monitoring/operator-checklist document.

## 2. What this package does NOT contain

- No live daemon process. No code in this repository polls `thredds.met.no`, a SITES telemetry endpoint, or executes a live Stage 3b benchmark.
- No real timestamp, sample, or "demo" evidence presented as real. Every record used in this pass's tests is explicitly a synthetic test fixture (`provenance_note="test fixture: synthetic timestamps for unit test only, not real evidence"`), never written to any evidence log outside the test's own temporary directory, and never copied into a persisted log file this report cites as operational evidence.
- No shortening or substitution for the register's own named acceptance windows (30 consecutive days of live MEPS 18Z logging, 14 consecutive days of live SITES telemetry logging, 10 consecutive live Stage 3b benchmark runs — `remediation_plan.md` Section 2-3, cited by `EVID-01`/`FOR-01`'s closure-evidence checklist in the register).

## 3. Integration point

The package is designed to be called by two existing, uninstrumented code paths, found by inspection in this pass:

- `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/meps_wind_extractor.py` — the MEPS pressure-level OPeNDAP fetch logic. A live deployment would wrap each fetch attempt with `AppendOnlyEvidenceLogger.append(...)`, constructing one `OperationalEvidenceRecord(input_type=InputType.MEPS_18Z, ...)` per attempt (success, retry, timeout, or failure), using the extractor's own observed fetch-start/fetch-end/provider-publication timestamps — never a fabricated one.
- `stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/n6_operational_pipeline.py` — the higher-level pipeline that would own the SITES telemetry and Stage 3b execution lifecycle events (ingestion/validation/downstream-ready timestamps).
- `system/monitoring/n6_feature_ingestion_monitor.py`'s existing, pre-existing `FeatureIngestionMonitor` (passive, in-memory, non-durable) is a complementary, narrower instrument (per-feature readiness within one run). This package is durable, cross-run, and schema-versioned, and is deliberately a SEPARATE module — it does not duplicate or replace `FeatureIngestionMonitor`, and this pass did not merge the two, to avoid widening either module's blast radius or coupling a durable disk-write path into an in-memory-only module used elsewhere.

**This package is NOT integrated into, and must never be integrated into, the production dispatch/safety decision path** (`system/control/`, `system/runtime/`, `system/orchestration/`, `system/optimization/implementations/`, `system/simulation/simulator.py`). It is observability tooling for a forecasting-input pipeline, not a safety-relevant control input.

## 4. Deployment instructions (for a future, separately authorized live session)

1. Provision a host with live network access to `thredds.met.no` (MEPS) and the SITES Nuolja telemetry endpoint, and the ability to execute Stage 3b benchmark runs against the real model artifacts.
2. Copy `system/monitoring/operational_evidence/config_template.json` to a real deployment config; fill in every `<placeholder>` field (log paths, poll intervals, timeouts). Do not leave `deployment_status: "NOT_DEPLOYED"` once a real daemon is running — update it to `"DEPLOYED"` with a start date, for the operator's own record-keeping (this repository does not read that field).
3. Wrap each of the three ingestion/execution call sites (Section 3) so that, on every attempt, it constructs one `OperationalEvidenceRecord` from values it actually observed (never a constant), and calls `AppendOnlyEvidenceLogger.append(record)`. Let `EvidenceLoggingError` propagate to the daemon's own operator-visible alerting channel — do not catch and discard it.
4. Let the daemon run continuously for at least the acceptance window named in `config_template.json` per stream (30 days MEPS, 14 days SITES, 10 consecutive Stage 3b runs).
5. Periodically run `python3 -m system.monitoring.operational_evidence.validate_log <log path>` to confirm schema conformance (this is a mechanical check, not a readiness certification).
6. At the end of the window, run `summarize_evidence_log(log_path, deadlines_by_input_type=...)` (Section 5) to produce the sample-count/missingness/coverage/margin report, supplying the ALREADY-DOCUMENTED deadline(s) this evidence should be measured against (e.g. the decision-cutoff times already used by `N6_OPERATIONAL_READINESS_REPORT.md`'s Gate 2) — never inventing a new deadline.

## 5. Monitoring / evidence-summarization instructions

```python
from system.monitoring.operational_evidence.summarizer import summarize_evidence_log

summary = summarize_evidence_log(
    "/var/log/polaris/operational_evidence/meps_18z_evidence.jsonl",
    deadlines_by_input_type={
        "MEPS_18Z_FORECAST_INPUT": "<the already-documented decision-cutoff ISO-8601 UTC timestamp>",
    },
)
```

The summary reports, per input stream: total records, success/missing/stale/failure/timeout/retry counts, distinct `process_run_id` count, earliest/latest receipt time, arrival-margin percentiles (p5/p50/p95/min/max/mean, in seconds, only if a deadline was supplied), and an explicit `small_sample_warning` when fewer than 30 records exist for that stream. The summary's own `honest_disclaimer` field restates, in every call, that a clean summary is not proof of operational readiness — the register's named acceptance windows must be independently checked.

## 6. Operator checklist (to close EVID-01, then re-open FOR-01's reconciliation)

- [ ] Daemon deployed and running continuously against live MEPS 18Z THREDDS endpoint.
- [ ] Daemon deployed and running continuously against live SITES Nuolja telemetry.
- [ ] Stage 3b benchmark executed and logged for 10 consecutive live runs.
- [ ] 30 consecutive days of MEPS evidence collected (verify via `summarize_evidence_log`'s `n_records`/`distinct_process_run_ids`/earliest-latest span, not merely "the daemon has been running for a while").
- [ ] 14 consecutive days of SITES evidence collected (same verification standard).
- [ ] `validate_log.py` reports zero schema failures across the full collection window.
- [ ] Evidence log reviewed for `n_missing`/`n_stale`/`n_failure`/`n_timeout` counts; any non-trivial rate investigated and explained, not waved through.
- [ ] A reconciliation of Gate 2's margin figures in `N6_OPERATIONAL_READINESS_REPORT.md` against the genuine logs is performed (register `FOR-01.disposition_2026_10_17.closure_evidence_checklist_2026_10_17`, step 2).
- [ ] The reconciliation is checked against the 27/36 UNPROVEN feature list in `operational_causality_audit.md` (checklist step 3).
- [ ] A decision on retracting/amending/confirming the PASS claims is made and recorded (checklist step 4).
- [ ] Formal governance sign-off recorded (checklist step 5).

**This checklist cannot be checked off from inside an offline repository session.** It exists so that whoever is granted live network/station access can execute it directly, without re-deriving the required steps from scratch.

## 7. Explicit statement of what remains unmet

As of this pass: **zero of the seven operator-checklist items above are checked.** Zero real evidence records exist anywhere produced by this package (the only records this package has ever written are synthetic test fixtures, inside `tempfile.TemporaryDirectory()`-scoped test runs that are deleted when the test process exits). `EVID-01` and `FOR-01` remain `EXTERNAL_EVIDENCE_REQUIRED` in the canonical register, unchanged by this pass.
