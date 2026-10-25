# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## PROTOTYPE PROVENANCE MATRIX & DECISION TABLE (RE-AUDITED)

**Audit Date**: 2026-09-23  
**Status**: COMPLETE — RE-AUDITED PROVENANCE MATRIX  

---

### 1. REVISED DECISION TABLE

| Input | Existing Source File | Meaning / Semantics | Provenance Category | Reusable? | Blocking? | Schema Change Required? | Real-Station Claim Allowed? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$T_{\text{required}}$** | `HD-03` / Governance | 72h prototype required survivability window | `GOVERNANCE_DECISION` | YES (for testing) | NO | NO | NO (`NOT_ESTABLISHED`) |
| **Critical Load** | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) L3-5 | Static rating baseline ($30\text{ kW}$) | `CONFIGURATION_PARAMETER` | PARTIAL (Scalar only) | YES (Needs 72h trajectory) | YES (`ForecastBundle.critical_demand`) | NO (`PROTOTYPE_ASSUMPTION`) |
| **Fuel Remaining** | [`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) | Fuel tank volume ($L$) | `NOT_ESTABLISHED_IN_CURRENT_EVIDENCE_BASE` | NO (Missing) | YES (Blocking implementation) | YES (`StationState.fuel_remaining_liters`) | NO (`NOT_ESTABLISHED`) |
| **Battery State** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) & `StationState` | Initial SOC ($50\%$) & Energy ($100\text{ kWh}$) | `CONFIGURATION_PARAMETER` | YES | NO | NO (Present in `StationState`) | NO (`PROTOTYPE_ASSUMPTION`) |
| **Diesel Model** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml) L3-6 | Linear consumption ($5.0\text{ L/h} + 0.25\text{ L/kWh}$) | `ENGINEERING_ASSUMPTION` | YES | NO | NO | NO (`PROTOTYPE_ASSUMPTION`) |
| **Solar Input** | ECD Stress Scenario (HD-04) | Zero solar irradiance ($P_{\text{solar}} = 0$) | `GOVERNANCE_DECISION` | YES | NO | NO | NO (Stress scenario only) |
| **Wind Input** | ECD Stress Scenario (HD-04) | Zero wind generation ($P_{\text{wind}} = 0$) | `GOVERNANCE_DECISION` | YES | NO | NO | NO (Stress scenario only) |

---

### 2. REVISED PROVENANCE CLASSIFICATION MATRIX

| Artifact / Input | Classification Category | Real Station Data? | Authorized for Prototype Use? | Repository Evidence Path | Real-Station Claim Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SITES Nuolja Solar SW_IN** | `REAL_MEASURED_STATION_DATA` | **YES** | YES | `data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv` | **ALLOWED** (Empirical solar) |
| **SMHI Abisko Wind Proxy** | `REAL_EXTERNAL_PROXY_DATA` | NO (Regional proxy) | YES (With proxy disclaimers) | `research/wind_a2/smhi_188790_ws_full.csv` | **PROHIBITED** (Proxy only) |
| **H1.0 Synthetic Load Trajectory** | `SYNTHETIC_ENGINEERING_TEST_DATA` | NO | YES (For H1.0 benchmarking) | `system/fixtures/hybrid_fixture_generator.py` | **PROHIBITED** (`SYNTHETIC`) |
| **168h Endurance Scenario** | `SYNTHETIC_ENGINEERING_TEST_DATA` | NO | YES (For endurance testing) | `system/data/scenarios/synthetic_168h_endurance_scenario.json` | **PROHIBITED** (`SYNTHETIC`) |
| **`loads.yaml` Critical Baseline** | `CONFIGURATION_PARAMETER` | NO | YES (Prototype scalar rating) | `system/config/loads.yaml` | **PROHIBITED** (`PROTOTYPE_ASSUMPTION`) |
| **Station Tank Fuel Inventory** | `NOT_ESTABLISHED_IN_CURRENT_EVIDENCE_BASE` | NO | **NO** (Field missing) | `system/schemas/station_state.py` | **PROHIBITED** (`NOT_ESTABLISHED`) |
