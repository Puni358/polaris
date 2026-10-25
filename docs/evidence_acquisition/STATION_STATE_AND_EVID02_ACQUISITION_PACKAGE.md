# Station-State Initial-Condition and EVID-02 Critical-Load — Evidence Acquisition Package

**Date prepared:** 2026-10-17
**Register items this package serves:** per-origin authoritative initial-state evidence (Harness Blocker B / IA-3, feeding any future N6 multi-origin campaign), and `EVID-02` (real, station-specific Nuolja critical-load measurement and circuit mapping), which in turn gates `CL-01`'s ultimate real-data validation and `DSL-01`'s `epsilon_tol` reconsideration.
**Status: NO REAL STATION EVIDENCE WAS FOUND OR COLLECTED IN THIS PASS.** A repository-wide search (Section 4) found zero new candidate files beyond what prior passes already inventoried. This package is acquisition tooling and documentation only.

---

## 1. Initial station state (battery SOC/energy, diesel fuel, demand/irradiance/wind at t0)

### 1.1 What already exists (reused, not duplicated)

`system/evaluation/n6_multi_origin_harness/adapters.py` already implements the authoritative, fail-closed validation contract for this evidence, added in the prior owner-authorized blocker-resolution pass:

- `REQUIRED_STATION_STATE_FIELDS` — the exact 8 required fields of `system/schemas/station_state.py`'s `StationState.from_dict` contract.
- `PROVENANCE_FIELD` (`"_provenance"`) — a mandatory, non-blank citation of where a record's values came from.
- `resolve_and_validate_authoritative_initial_state(origin, registry)` — raises `AuthoritativeInitialStateUnavailableError` if the origin is absent, or `MalformedInitialStateRecordError` if present but incomplete/uncited. Never fills a missing field.

This pass adds, on top of that unchanged contract (reused, never re-implemented):

- `docs/evidence_acquisition/schemas/station_state_evidence_schema.json` — a versioned schema documenting the 8 core fields plus EXTENDED evidence-quality metadata (station identity, measurement timestamp, units, source reference, calibration/quality flags) that the core `StationState` contract does not itself require but that a real acquisition submission should carry.
- `tools/evidence_acquisition/validate_station_state_evidence.py` — a strict validator + read-only completeness/quality report. It imports (does not duplicate) `resolve_and_validate_authoritative_initial_state` for the core, blocking validation, and separately, non-blockingly, reports how many of the 4 extended-metadata fields each submission carries.
- `system/tests/test_station_state_evidence_validator.py` — focused tests.

### 1.2 How to submit real evidence

1. Assemble a JSON file mapping `origin_id -> record`, where each record contains the 8 `REQUIRED_STATION_STATE_FIELDS`, `_provenance`, and the extended metadata fields named in the schema file (Section 1.1).
2. Run: `python3 tools/evidence_acquisition/validate_station_state_evidence.py <file.json>`.
3. A `core_validation: "FAIL"` entry means that origin is NOT usable as authoritative evidence yet — fix the exact missing field/citation named in `core_validation_detail` and resubmit. A `core_validation: "PASS"` entry satisfies the construction contract; it is still only as trustworthy as the cited source, which this tool does not independently re-verify.
4. Only after `resolve_and_validate_authoritative_initial_state` accepts a record should it ever be placed into a real `authoritative_initial_states_by_origin` registry used by any harness adapter — and per the harness's own, unchanged governance boundary, doing so with a REAL production object still requires separate campaign-execution authorization (`replay_harness.py`'s guard; see Workstream E of the governing report).

### 1.3 Repository-wide search performed this pass

A search for any pre-existing per-origin initial-state table (beyond the single, already-disclaimed `run_n6_closed_loop_simulation.py` smoke-test literals at lines ~101-112) found none. Zero origins have authoritative initial-state coverage today. This is unchanged from every prior pass's finding.

---

## 2. EVID-02 — real, station-specific Nuolja critical-load measurement

### 2.1 Precise definition (from the register, verified against source)

`EVID-02` (register, `item_type: E`, external evidence): "Can actual measured critical-load power draw and circuit-level mapping for the Nuolja Middle Station (or, for the ultimate SIH26061 target, Maitri/Bharati) be obtained, given `REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED` is explicitly stated in both critical-load audits and no station-specific measurement exists anywhere in this repository?" Source: `CRITICAL_LOAD_HIGH_POWER_AUDIT.md` Section 6, `CRITICAL_LOAD_ONLINE_SOURCE_AUDIT.md` Sections 1 and 7 — both independently re-read this pass and confirmed still accurate: every critical-load number in the project remains `SYNTHETIC_ENGINEERING_SCENARIO`.

### 2.2 Acquisition package added this pass

- `docs/evidence_acquisition/schemas/evid02_critical_load_schema.json` — the full record shape: circuit/equipment identity + criticality rationale; measurement method/units/sampling interval/period; meter/instrument identity + calibration info; per-sample timestamp + station identity; missing-reading/operating-mode treatment; source-file/provenance fields; a validation/acceptance-check list.
- This document's Section 2.3 (data dictionary) and Section 2.4 (acceptance checklist), for the station/operator who would actually collect this data.

### 2.3 Data dictionary (summary; full detail in the JSON schema)

| Field group | Required contents |
|---|---|
| Circuit/equipment identity | `circuit_id`, `equipment_description`, station-specific `criticality_rationale` |
| Measurement method | method type, units, sampling interval, measurement period start/end (UTC) |
| Instrument identity | meter/instrument id, calibration-last-verified date (or `UNKNOWN`), calibration authority |
| Timestamp + station identity | real station name, per-sample UTC timestamp |
| Missing/operating-mode treatment | explicit missing-reading reason codes (never interpolated); per-sample operating mode (`NORMAL`/`REDUCED_LOAD_SHED`/`EMERGENCY`/`MAINTENANCE`/`UNKNOWN`) |
| Source/provenance | raw source file/log reference, extraction method, submitter name/role, submission date |

### 2.4 Acceptance checklist (station/operator-facing)

- [ ] Real station identity named (not a placeholder).
- [ ] At least 7 consecutive days of continuous metering, OR a documented circuit-by-circuit nameplate audit cross-checked against at least one metered peak-load event (a single instantaneous reading is explicitly insufficient per the schema).
- [ ] Every sample's operating mode recorded, not defaulted.
- [ ] Every missing reading carries an explicit reason code.
- [ ] Criticality rationale is station-specific (not a restatement of this project's own synthetic framing).
- [ ] Submission validated against `evid02_critical_load_schema.json`'s acceptance checks.

### 2.5 Explicit non-substitution clause (restated from the schema)

The provisional 11.6 kW `SYNTHETIC_ENGINEERING_SCENARIO` figure in `CRITICAL_LOAD_HIGH_POWER_SCENARIO.md` (CL-01, decided 2026-10-17: "retain 11.6 kW, provisional/synthetic only") is **not** inferred from, backed into, or reconciled with any future real submission under this schema. Its synthetic/provisional status is preserved explicitly and is unaffected by this pass. **EVID-02 cannot be closed in this session.** The exact external input needed is: a real, cited, circuit-mapped Nuolja (or Maitri/Bharati) critical-load measurement, meeting the acceptance checklist above, supplied by station/operator personnel with physical or SCADA access this repository/session does not have.

---

## 3. What this pass explicitly did NOT do

- Did not infer, estimate, or impute any real Nuolja critical-load value from the synthetic 11.6 kW scenario or from any external engineering reference.
- Did not fill, guess, or default any missing initial-state field for any origin.
- Did not mark any origin's initial-state coverage as sufficient; zero origins have such coverage today, unchanged from every prior pass.
- Did not modify `system/schemas/station_state.py`, `adapters.py`'s existing validation contract, or any protected file.
