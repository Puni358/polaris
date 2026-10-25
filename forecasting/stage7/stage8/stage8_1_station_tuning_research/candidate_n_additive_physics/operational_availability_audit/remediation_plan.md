# POLARIS Candidate N6 — Operational Remediation Plan & Acceptance Criteria

**Document Version:** 1.0.0  
**Status:** ACTIONABLE ENGINEERING SPECIFICATION (Non-Production Governance)  
**Governing Status:** winner: null  
**Date:** 2026-10-17  

---

## 1. Executive Summary

The Read-Only Operational Feature Availability & Causality Audit concluded with a verdict of **`UNPROVEN`** across 27 of 36 features required by Candidate N6. While Candidate N6 has completely eliminated future target contamination and same-day zero-lead NWP leakage (the flaws that blocked Candidate F), it cannot be declared operationally viable because the repository lacks contemporaneous operational ingestion logs from 2024 and 2025.

This remediation plan outlines the exact engineering capabilities, evidentiary logging pipelines, fallback protocols, and acceptance criteria required to transition Candidate N6 from `UNPROVEN` to `INPUT AVAILABILITY DEMONSTRATED`.

---

## 2. Enumerated Blockers & Remediation Tasks

### Blocker 1: MEPS 18Z Pressure-Level Dissemination & Latency Verification
- **Affected Features:** `u700`, `v700`, `lwp_18z_fc`, `iwp_18z_fc`, `lwp_x_cloud_18z` (5 features).
- **Underlying Defect:** While the MEPS 18Z run initializes 6 hours before cutoff ($t_0 - 6\text{h}$), neither MET Norway's THREDDS server nor POLARIS maintains logged records of the actual completion and publication timestamps for the heavy pressure-level NetCDF files (`meps_det_pl_*.ncml`).
- **Required Remediation:**
  1. **Contemporaneous Latency Logger Daemon:** Implement an asynchronous polling daemon that monitors `https://thredds.met.no/thredds/dodsC/meps25epsarchive/{YYYY}/{MM}/{DD}/meps_det_pl_{YYYYMMDD}T18Z.ncml.dds`.
  2. **Metadata Logging:** Record HTTP `Last-Modified`, `Date`, round-trip latency, OPeNDAP slice fetch duration, and SHA-256 payload checksums into an append-only JSONL log (`/var/log/polaris/meps_18z_ingestion.jsonl`).
  3. **Operational Lead Range Rectification:** Update the pressure-level OPeNDAP extraction query from `lead[7:1:25]` to `lead[6:1:29]` to eliminate the historical NaN truncation for horizons $h \in [20, 24]$ in `u700` and `v700`.
- **Suggested Owner:** NWP Data Ingestion & Systems Engineering Team.
- **Acceptance Test:**
  - Continuous 30-day logging cycle showing 100% of 18Z pressure-level slices ingested, verified, and available prior to $23:15:00\text{ UTC}$ ($45\text{ min}$ safety margin before $t_0$).

---

### Blocker 2: Real-Time Station Telemetry Streaming Bridge
- **Affected Features:** `ctx_std_3h` through `ctx_max_24h` (14 features).
- **Underlying Defect:** Historical models were trained on retrospective Level 2 annual research archives (`SITES_MET_ANS_NMS_*_L2_SH.csv`) published months after observation. No real-time telemetry streaming daemon or operational logger exists in the repository.
- **Required Remediation:**
  1. **Direct SCADA / Datalogger Telemetry Bridge:** Establish an automated ingestion agent connecting to the Nuolja Middle Station datalogger (or on-site microgrid pyranometer feed via Modbus TCP / MQTT).
  2. **Rolling In-Memory Buffer:** Maintain an in-memory, ring-buffered 24-hour observation array $[t_0-24\text{h}, t_0)$ updated at 10-minute intervals.
  3. **Audit Trail:** Log telemetry buffer completion timestamp at $23:55:00\text{ UTC}$ daily, including sensor health flags and irradiance bounds checks.
- **Suggested Owner:** Microgrid SCADA & Field Instrumentation Team.
- **Acceptance Test:**
  - Automated continuous receipt of 24-hour rolling observations with latency $< 60\text{ seconds}$ from acquisition, achieving zero dropped hours over 14 consecutive days.

---

### Blocker 3: Stage 3b Chronos-2 Operational Execution Latency
- **Affected Features:** `pred_stage4_clean`, `clean_attenuation` (2 direct features, plus interaction influences).
- **Underlying Defect:** `pred_stage4_clean` requires `pred_stage3b_cloud_nwp` from the Chronos-2 transformer model. Stage 3b was previously executed as an offline batch computation without documented operational inference duration benchmarks.
- **Required Remediation:**
  1. **Dedicated Inference Microservice:** Package Stage 3b Chronos-2 inference into a lightweight, containerized execution runtime triggered automatically upon receipt of the 18Z MEPS surface data (approx. 20:30 UTC).
  2. **Execution Benchmarking:** Instrument wall-clock runtime profiling to confirm that Stage 3b inference completes in $< 180\text{ seconds}$ on edge or microgrid controller hardware.
  3. **Cryptographic Input Validation:** Ensure Stage 3b consumes the certified 2024-EVEN parameters without dynamic re-fitting.
- **Suggested Owner:** Forecasting Core & ML Platform Team.
- **Acceptance Test:**
  - 10 consecutive simulated operational dispatches executing Chronos-2 inference with wall-clock time $< 3\text{ minutes}$ and output SHA-256 parity with batch references.

---

### Blocker 4: Deterministic Fail-Closed & Fallback Engine
- **Affected Features:** System-wide dispatch reliability.
- **Underlying Defect:** In the event of a network outage, THREDDS downtime, or delayed MEPS cycle, the system must not stall or substitute arbitrary synthetic inputs.
- **Required Remediation:**
  1. **Tiered Fallback Policy:**
     - *Tier 1 (Normal Operations):* Full 36-feature Candidate N6 model executed with L2 conformal reserve ($Q_{90,W} = 1.5702$).
     - *Tier 2 (Pressure Levels Missing, Surface Available):* Fall back to Candidate K (35 features) or Stage 4 Clean Baseline with inflated conformal reserve margins.
     - *Tier 3 (Complete NWP Failure):* Revert to clear-sky persistence model with maximum emergency battery reserve ($EBR_{\text{base}} = 25\text{ kWh}$).
  2. **Safe Rejection Invariants:** Any input DataFrame with missing critical columns (`solar_elevation`, `clearsky_ghi`, `pred_stage4_clean`) or NaN values outside allowed non-critical features (`u700`, `v700`) must raise `InputValidationError` and halt dispatch.
- **Suggested Owner:** EMS Optimization & Microgrid Safety Architecture Team.
- **Acceptance Test:**
  - Fault-injection unit test suite simulating missing, late, corrupt, and stale payloads, verifying 100% fail-closed termination.

---

## 3. Road to Operational Certification

| Milestone | Scope | Deliverables | Exit Gate |
|---|---|---|---|
| **Phase 1** | Ingestion Logging | Real-time daemons for MEPS 18Z & SITES | 30 days of timestamped arrival logs $< 00:00\text{ UTC}$ |
| **Phase 2** | Live Replay Audit | Bounded replay using genuine logged arrival times | `availability_replay_results.csv` with 100% PASS |
| **Phase 3** | Fallback Integration | Validated Tier 2/3 degraded modes in runner | Zero unhandled exceptions under fault injection |
| **Phase 4** | Governance Review | Formal re-audit against POLARIS standards | Authorization to advance toward production readiness |

**Notice:** Implementation of this remediation plan does NOT alter `winner: null` or constitute authorization for operational deployment.
