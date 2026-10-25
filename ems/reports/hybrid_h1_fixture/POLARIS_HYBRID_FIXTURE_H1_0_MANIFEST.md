# POLARIS — Hybrid Input Fixture H1.0 Canonical Manifest

> **Fixture Identity:** `HYBRID_FIXTURE_VERSION = H1.0`  
> **Manifest Classification:** `A — H1.0 FIXTURE GENERATED AND EXACTLY REPRODUCIBLE`  
> **Canonical Directory:** [`POLARIS_HYBRID_FIXTURE_H1_0/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_HYBRID_FIXTURE_H1_0/)  
> **Execution Status:** `FIXTURE FROZEN / RUNTIME EXECUTION NOT AUTHORIZED`  
> **Governance Date (UTC):** 2026-09-20  

---

## 1. Canonical Fixture Inventory

| File Name | Relative Workspace Path | SHA-256 Digest | Size (Bytes) | Description |
| :--- | :--- | :--- | :---: | :--- |
| **`fixture.csv`** | `POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv` | `762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023` | ~1.05 MB | Canonical 8,784-row hourly hybrid input fixture |
| **`provenance.json`** | `POLARIS_HYBRID_FIXTURE_H1_0/provenance.json` | `ed505b118ee774a628eeac1c8a437b8754f91c71fd2e22764b96e192385a0498` | 1,250 B | Detailed column provenance and disclaimer manifest |
| **`config.json`** | `POLARIS_HYBRID_FIXTURE_H1_0/config.json` | `b60ca342f23179cafc7fc3ea5f1301f023e93c37976a188564cff2815a336762` | 320 B | Fixture generation parameters and source links |
| **`hashes.json`** | `POLARIS_HYBRID_FIXTURE_H1_0/hashes.json` | `80b2a75fa7645f7435fce8a6e87bcbb49bb77b5d153d10fa8cd42a8a81ac712c` | 410 B | Immutable SHA-256 integrity digests |

---

## 2. Source Data Integrity Manifest

| Input Category | Source File | SHA-256 Digest | Status |
| :--- | :--- | :--- | :---: |
| **SITES Solar Source** | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` | `0a2b9d2cbf3fea14a75d2e448f9650534f2ff540601d8c89df69e3b9334fa1f8` | `UNTOUCHED` |
| **SMHI Wind Source** | `research/wind_a2/smhi_188790_ws_full.csv` | `b7f694aa957af57103176d9a2cb77bd506e2c0f56402eab5cc584ebd02d379fd` | `UNTOUCHED` |

---

## 3. Scientific Claim Boundaries

- **`REAL_MEASURED`:** Solar Shortwave Irradiance $SW_{\text{in}}$ (SITES Nuolja AWS 2024).
- **`DERIVED_ENGINEERING_QUANTITY`:** Solar PV Power $P_{\text{solar}}$ (D3 formula $SW_{\text{in}} \times 51.0$).
- **`CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY`:** Wind Speed (SMHI 188790 10m Abisko Aut).
- **`SYNTHETIC_ENGINEERING_SCENARIO`:** Generic IEC 60 kW Wind Turbine Power $P_{\text{wind}}$ (`POLAR_REFERENCE_TURBINE_SCENARIO`; **NOT** Nuolja hardware).
- **`SYNTHETIC`:** Station Demand $P_{\text{load}}$ (`SYNTHETIC_STATION_DEMAND`; **`SYNTHETIC_STATION_DEMAND != NULLOJA_MEASURED_DEMAND`**).

---

## 4. Mandatory Safety & Governance Status Block

```
FROZEN_EVIDENCE_MODIFIED      = NO
MILP_SOLVES_EXECUTED          = 0
SIMULATIONS_EXECUTED          = 0
EXPERIMENT_RERUN              = NO
NEW_MODELING                  = NO
NEW_TUNING                    = NO
ARCHITECTURE_MODIFIED         = NO

FIXTURE_GENERATED             = YES
FIXTURE_DETERMINISM           = PASS
SOURCE_INTEGRITY              = PASS
PROVENANCE_VALIDATION         = PASS
PHYSICAL_VALIDATION           = PASS

HYBRID_FIXTURE_VERSION        = H1.0
HYBRID_BRANCH                 = DESIGN AUTHORIZED / EXECUTION NOT AUTHORIZED

STEP9_FINAL_CLASSIFICATION    = A — H1.0 FIXTURE GENERATED AND EXACTLY REPRODUCIBLE
```
