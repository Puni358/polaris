# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## FIXTURE PROVENANCE MATRIX & DECISION REGISTER

**Audit Date**: 2026-09-23  
**Status**: COMPLETE — RE-AUDITED PROVENANCE CLASSIFICATION MATRIX  

---

### 1. REVISED DECISION & PROVENANCE TABLE

| Input / Parameter | Source | Provenance Category | Reusable? | Real-Station Claim Status |
| :--- | :--- | :--- | :--- | :--- |
| **$T_{\text{required}} = 72.0\text{h}$** | Governed Survivability Baseline | `GOVERNANCE_DECISION` | YES (Preserved) | NO (`NOT_ESTABLISHED`) |
| **$T_{\text{test}} = 2.0\text{h}$** | Authorized Logic Test Horizon | `GOVERNANCE_DECISION` | YES (Logic test only) | NO (`STATION_MEANING = NONE`) |
| **Critical Load $P_{\text{crit}} = 30\text{ kW}$** | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `CONFIGURATION_PARAMETER` | YES (Constant test load) | NO (`PROTOTYPE_ASSUMPTION`) |
| **Battery Parameters** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `CONFIGURATION_PARAMETER` | YES | NO (`PROTOTYPE_ASSUMPTION`) |
| **Diesel Parameters** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml) | `ENGINEERING_ASSUMPTION` | YES | NO (`PROTOTYPE_ASSUMPTION`) |
| **Test SOC Bands ($80\%, 30\%$)** | Authorized Test Specification | `SYNTHETIC_ENGINEERING_TEST_DATA` | YES (Logic test only) | NO (`STATION_MEANING = NONE`) |
| **Test Fuel Bands ($50\text{L}, 12.5\text{L}$)** | Authorized Test Specification | `SYNTHETIC_ENGINEERING_TEST_DATA` | YES (Logic test only) | NO (`STATION_MEANING = NONE`) |
| **Equal-Margin Fuel ($46.0\text{L}$)** | Analytically Derived ($3.68\text{h} \times 12.5\text{L/h}$) | `DERIVED_VALUE` / `SYNTHETIC` | YES (Logic test only) | NO (`STATION_MEANING = NONE`) |

---

### 2. HARD PROVENANCE FIREWALL STATEMENT

$$\text{Interface Compatibility } \neq \text{ Provenance Equivalence}$$

Every fixture input is strictly classified as `SYNTHETIC_ENGINEERING_TEST_DATA` with `STATION_MEANING = NONE` and `REAL_STATION_VALIDATION = NOT_ESTABLISHED`. No real station telemetry was used.
