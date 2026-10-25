# POLARIS — Hybrid Input Provenance Matrix

> **Governance Phase:** Step 8 — Hybrid Fixture Specification & Determinism Gate  
> **Purpose:** Formal Input Provenance Matrix for Governed Hybrid Engineering Branch  
> **Governance Date (UTC):** 2026-09-20  

---

## 1. Input Provenance Matrix

Every input stream entering the POLARIS Hybrid Engineering Branch is strictly categorized in the matrix below to ensure complete transparency and prevent any misrepresentation of synthetic or proxy data:

| Input Name | Variable | Source & Facility | Provenance Class | Measurement Status | Station Specific? | Allowed Operational Use |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Nuolja Solar Irradiance** | `SW_IN` | SITES Nuolja Middle Station AWS (68.36°N, 18.74°E) | `REAL_MEASURED` | Real physical solar shortwave radiation observation | **YES** | Solar forecasting and solar generation availability input only (**NOT** electrical generation) |
| **Abisko Wind Speed** | `wind_speed_10m` | SMHI Station 188790 (Abisko Aut, 392.2 m a.s.l.) | `CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY` | Real meteorological observation at regional weather station | **NO** (4.1 km distance, ~310m alt. diff) | Proxy wind-speed input for controlled hybrid engineering scenarios (**NOT** Nuolja measured wind) |
| **Station Electrical Demand** | `P_load` | POLARIS Synthetic Load Profile Generator | `SYNTHETIC` | `DATA_BLOCKED` | **NO** | Controlled engineering and digital-twin validation only (**NOT** measured station load) |
| **Wind Electrical Generation** | `P_wind` | POLAR_REFERENCE_TURBINE_SCENARIO (Generic 60 kW IEC Curve) | `SYNTHETIC_ENGINEERING_SCENARIO` | `NUOLJA_GENERATION_NOT_ESTABLISHED` | **NO** | Controlled engineering scenario only if explicitly authorized (**NOT** Nuolja hardware) |
| **Solar-to-PV Mapping (D3)** | `P_solar` | $P_{\text{raw}} = SW_{\text{in}} \times 300\text{ m}^2 \times 0.20 \times 0.85$; $P_{\text{solar}} = \min(P_{\text{raw}}, 60\text{ kW})$ | `ENGINEERING_MAPPING` | Engineering model assumption | **NO** | Synthetic PV array conversion model for simulation inputs (**NOT** empirical station PV validation) |

---

## 2. Provenance Class Definitions

1. **`REAL_MEASURED`:** Directly metered physical observation collected at the specified polar research station site.
2. **`CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY`:** Real physical measurement from a neighboring regional monitoring station, used under explicit spatial/altitude proxy limitations.
3. **`SYNTHETIC`:** Deterministically generated artificial input sequence designed for engineering testing when real data is `DATA_BLOCKED`.
4. **`SYNTHETIC_ENGINEERING_SCENARIO`:** Mathematical or generic equipment model representation used for scenario analysis when site-specific hardware is `NOT_ESTABLISHED`.
5. **`ENGINEERING_MAPPING`:** Standard physical transformation formula converting a environmental variable to electrical power.

---

## 3. Mandatory Safety & Governance Status Block

```
FROZEN_EVIDENCE_MODIFIED      = NO
MILP_SOLVES_EXECUTED          = 0
SIMULATIONS_EXECUTED          = 0
EXPERIMENT_RERUN              = NO
NEW_MODELING                  = NO
NEW_TUNING                    = NO
ARCHITECTURE_MODIFIED         = NO

REAL_DEMAND_DATA_STATUS       = DATA_BLOCKED
NUOLJA_WIND_ASSET_STATUS      = NOT_ESTABLISHED
NUOLJA_WIND_GENERATION_STATUS = NOT_ESTABLISHED
```
