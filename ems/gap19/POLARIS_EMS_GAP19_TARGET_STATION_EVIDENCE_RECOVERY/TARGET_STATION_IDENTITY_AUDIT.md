# POLARIS EMS GAP19 — TARGET STATION IDENTITY AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Classification**: `STATION_SPECIFIC_ESTABLISHED` (Meteorological Site Identity)  

---

## 1. Target Station Identification Matrix

| Identity Field | Verified Target Station Parameter | Source & Provenance | Classification |
| :--- | :--- | :--- | :---: |
| **Station / Site Name** | **SITES Nuolja Research Station Site (Njullá)** | SITES (Swedish Infrastructure for Ecosystem Science) / ANS (Abisko Scientific Research Station) | `STATION_SPECIFIC_ESTABLISHED` |
| **Location Coordinates** | Abisko, Subarctic Sweden ($68.35^\circ \text{N}, 18.82^\circ \text{E}$) | SITES Meteorological Station Metadata | `STATION_SPECIFIC_ESTABLISHED` |
| **Operating Organization** | SITES / Swedish Polar Research Secretariat / STF | Official Swedish Scientific Infrastructure Registry | `STATION_SPECIFIC_ESTABLISHED` |
| **Primary Solar/Wind Data** | Shortwave radiation ($SW\_IN$), Clearsky GHI, Wind Speed | SITES open-access meteorological data streams | `STATION_SPECIFIC_ESTABLISHED` |
| **Microgrid BESS / Diesel Specs** | Microgrid BESS capacity, diesel curves, fuel tank specs | Un-documented in open literature; synthetic model used | `SYNTHETIC_ENGINEERING_ASSUMPTION` |

---

## 2. Distinction Between Site Irradiance vs Microgrid Hardware

1. **Site Meteorological Data**: SITES Nuolja provides measured shortwave solar irradiance ($SW\_IN$) and meteorological variables. This data is **`STATION_SPECIFIC_ESTABLISHED`** for renewable forecasting.
2. **Microgrid Power Hardware**: The $200\text{ kWh}$ battery, $100\text{ kW}$ diesel generator, and $30\text{ kW}$ load in POLARIS codebase are synthetic test models (`SYNTHETIC_ENGINEERING_ASSUMPTION` / `IMPLEMENTATION_FACT`), NOT actual physical hardware installed on Mount Nuolja.
