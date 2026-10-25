# POLARIS EMS GAP19 — EVIDENCE RECOVERY SCOPE

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  

---

## 1. Audit Methodology & Two-Stage Search Protocol

The evidence recovery audit followed a strict **Two-Stage Search Protocol**:

### Stage 1 — Local Project Evidence Audit
* Targeted search of local workspace registers (`POLARIS_DEMAND_*`, `POLARIS_EMS_*`, `system/config/*.yaml`, `system/data/scenarios/*.json`).
* Inspection of sealed governance decisions (DEC-004, Option D, D1–D4).
* Verification of data delivery routes (AADC, SANAP, IPF, ACEP custodian logs).
* **Local Recovery Outcome**: Stage 1 established `ACTUALLY_RECEIVED = 0` for measured station-level electrical demand time-series and hardware calibration sheets.

### Stage 2 — External Authoritative Research
* Targeted external research for official published technical documentation concerning **SITES Nuolja Station** (Abisko, Sweden).
* Prioritization rules enforced:
  1. Official station operator documentation (SITES / Abisko Scientific Research Station / STF).
  2. Official government and scientific agency reports.
  3. Peer-reviewed institutional technical publications.
  4. Generic equipment specifications or un-linked research papers tagged as `REGIONAL_PROXY` or `SYNTHETIC_ENGINEERING_ASSUMPTION`.
* **External Recovery Outcome**: Confirmed that while Nuolja is an established SITES meteorological/irradiance research site, zero public engineering datasheets exist for a standalone hybrid BESS/generator microgrid at Nuolja.

---

## 2. Mandatory Classification Rules

Every recovered item must receive exactly one of 7 evidence categories:
1. `STATION_SPECIFIC_ESTABLISHED`: Direct verified evidence for the target station. (Eligible for production).
2. `STATION_SPECIFIC_REPORTED_BUT_UNVERIFIED`: Reported for target station, lacking verification.
3. `REGIONAL_PROXY`: Data from another polar station or regional proxy. (MUST NOT be promoted to station-specific).
4. `SYNTHETIC_ENGINEERING_ASSUMPTION`: Test parameters created for software simulation.
5. `IMPLEMENTATION_FACT`: Software configuration default or MILP formulation choice.
6. `GOVERNANCE_VALUE`: Explicit policy selection by human authority.
7. `NOT_ESTABLISHED`: Required input lacking qualifying evidence.
