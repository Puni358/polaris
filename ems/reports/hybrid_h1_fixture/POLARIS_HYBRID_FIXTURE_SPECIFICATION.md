# POLARIS — Hybrid Input Fixture Specification

> **Fixture Identity:** `HYBRID_FIXTURE_VERSION = H1.0`  
> **Governance Phase:** Step 8 — Hybrid Fixture Specification & Determinism Gate  
> **Status:** `A — HYBRID FIXTURE FULLY SPECIFIED AND DETERMINISM-READY`  
> **Execution Status:** `NOT AUTHORIZED` (Design & Static Specification Only)  
> **Governance Date (UTC):** 2026-09-20  

---

## 1. Executive Summary & Purpose

This specification establishes the immutable, deterministic **Hybrid Input Fixture Specification (Version H1.0)** for future controlled engineering validation of the POLARIS predictive energy management system.

The fixture integrates:
1. **`REAL_MEASURED`:** SITES Nuolja Middle Station $SW_{\text{in}}$ shortwave solar irradiance (CY 2024, 8,784 timesteps).
2. **`CONDITIONALLY_ESTABLISHED_REGIONAL_PROXY`:** SMHI Station 188790 (Abisko Aut) 10m hourly wind speed (4.1 km distance, ~310m alt. diff).
3. **`SYNTHETIC`:** `SYNTHETIC_STATION_DEMAND` fixture (deterministic 15–45 kW diurnal polar load profile).
4. **`SYNTHETIC_ENGINEERING_SCENARIO`:** `POLAR_REFERENCE_TURBINE_SCENARIO` (generic IEC 61400-12 60 kW reference turbine curve; explicitly **NOT** Nuolja hardware).
5. **`ENGINEERING_MAPPING`:** D3 PV array solar conversion formula ($P_{\text{solar}} = \min(SW_{\text{in}} \times 300\text{m}^2 \times 0.20 \times 0.85, 60000\text{W})$).

---

## 2. Synthetic Demand Fixture Specification

- **Fixture Identifier:** `SYNTHETIC_STATION_DEMAND`
- **Crucial Rule:** `SYNTHETIC_STATION_DEMAND != NULLOJA_MEASURED_DEMAND`. This trace MUST NOT be represented as empirical station load.
- **Base Demand:** $P_{\text{base}} = 25,000\text{ W}$ (25 kW)
- **Minimum Demand:** $P_{\text{min}} = 15,000\text{ W}$ (15 kW)
- **Maximum / Peak Demand:** $P_{\text{peak}} = 45,000\text{ W}$ (45 kW)
- **Daily Diurnal Profile:**
  - Night Base (00:00–06:00 UTC): 18,000 W
  - Morning Peak (08:00 UTC): 38,000 W
  - Day Sustained (09:00–17:00 UTC): 32,000 W
  - Evening Peak (19:00 UTC): 42,000 W
  - Night Transition (22:00–23:00 UTC): 22,000 W
- **Seasonal Multipliers:** Winter = 1.20x ($P_{\text{winter\_peak}} = 45,000\text{ W}$), Summer = 0.85x, Transitional = 1.00x.
- **Stochastic Component:** Baseline H1.0 is **100% deterministic** (noise = 0 W). Optional scenario noise uses Gaussian $\mathcal{N}(0, \sigma=1000\text{ W})$ clipped to $[15000, 45000]$ with fixed PRNG seed = 42.
- **Sampling & Units:** 1-hour discrete steps ($\Delta t = 1\text{h}$) in Watts ($\text{W}$).
- **Duration & Coverage:** 8,784 hourly timesteps matching calendar year 2024.
- **Reproducibility:** 100% deterministic algorithm; SHA-256 fingerprint verified.

---

## 3. Wind Generation Scenario Specification

- **Scenario Identifier:** `POLAR_REFERENCE_TURBINE_SCENARIO`
- **Hardware Disclaimer:** `GENERIC ENGINEERING ASSUMPTION — NOT NULLOJA HARDWARE`. Enercon E-33 Scott Base/McMurdo specs are NOT used as Nuolja specs.
- **Turbine Specifications:**
  - Rated Active Power: $P_{\text{rated}} = 60,000\text{ W}$ (60 kW)
  - Cut-in Wind Speed: $v_{\text{cut\_in}} = 3.0\text{ m/s}$
  - Rated Wind Speed: $v_{\text{rated}} = 12.0\text{ m/s}$
  - Cut-out Wind Speed: $v_{\text{cut\_out}} = 25.0\text{ m/s}$
- **Piecewise Power Curve Definition:**
  $$P_{\text{wind}}(v) = \begin{cases}
  0 & v < 3.0\text{ m/s} \text{ or } v \ge 25.0\text{ m/s} \\
  60000 \times \frac{v^3 - 3.0^3}{12.0^3 - 3.0^3} & 3.0 \le v < 12.0\text{ m/s} \\
  60000 & 12.0 \le v < 25.0\text{ m/s}
  \end{cases}$$
- **Mapping Classification:** `v_proxy (Abisko SMHI 10m)` $\rightarrow$ `Generic IEC Curve` $\rightarrow$ `P_wind_synthetic`. Classified as `SYNTHETIC_ENGINEERING_SCENARIO`.

---

## 4. Time Alignment & Truth Firewall Contracts

### 4.1 Time Alignment Contract
- **Timezone:** UTC
- **Timestamp Format:** ISO 8601 string (`YYYY-MM-DDTHH:00:00Z`)
- **Grid Resolution:** Monotonic 1-hour discrete intervals
- **Join Key:** `timestamp_utc`
- **Missing Data Policy:** Zero silent interpolation for real observations. Incomplete evaluation windows are strictly rejected.

### 4.2 Truth Firewall Contract
- **Controller Visible State:** Current state $\text{StationState}(t_0)$, historical observations $t \le t_0$, and 24-hour receding forecast bundle $F(t_0)$.
- **Hidden Future Truth:** Future actual ground truth $P_{\text{load}}(t_0 + k)$, $SW_{\text{in}}(t_0 + k)$, $v_{\text{wind}}(t_0 + k)$ for $k \ge 1$.
- **Firewall Rule:** The controller **MUST NOT** access future ground truth before simulator step execution.

---

## 5. Initial State Contract

- Battery State of Charge: $SOC(t_0) = 50.0\%$
- Stored Battery Energy: $E_{\text{batt}}(t_0) = 25,000\text{ Wh}$ (Capacity = 50,000 Wh)
- Diesel Generator Status: $Run_{\text{diesel}}(t_0) = \text{False}$, $Hours_{\text{diesel}}(t_0) = 0.0\text{ hours}$
- **Schema Mapping:** Maps directly into frozen `StationState v1.0` without schema modification.

---

## 6. Hybrid Evaluation Scenario Classes (Design Only)

| Scenario ID | Name | Purpose | Input Streams | Duration | Execution Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **H1** | Baseline Hybrid | Validate causal runtime & MPC loop | Real Nuolja $SW_{\text{in}}$, Abisko Wind Proxy, Synthetic Demand H1.0 | 168h | `NOT_EXECUTED` |
| **H2** | Solar Forecast Replay | Evaluate EMS sensitivity to solar forecast errors | Real Nuolja $SW_{\text{in}}$, Stage8.1 Solar Forecast, Synthetic Demand | 168h | `NOT_EXECUTED` |
| **H3** | Wind Proxy Scenario | Evaluate EMS under proxy wind speed inputs | Abisko Wind Proxy, Generic 60 kW Turbine Curve, Synthetic Demand | 168h | `NOT_EXECUTED` |
| **H4** | Combined Renewable | Evaluate solar + wind microgrid balancing | Real Solar, Abisko Wind Proxy, Generic Turbine, Synthetic Demand | 168h | `NOT_EXECUTED` |
| **H5** | Stress Scenario | Evaluate microgrid stability during polar winter low-solar events | Real Winter $SW_{\text{in}}$, High Winter Demand (30–45 kW), Frozen Microgrid | 168h | `NOT_EXECUTED` |

---

## 7. Claim Boundaries

### Allowed Claims:
- *"POLARIS was evaluated in a controlled hybrid engineering environment combining real measured solar irradiance, a conditionally established regional wind-speed proxy, and explicitly synthetic station demand."*
- *"Results describe behavior in the specified controlled engineering environment."*
- *"Real measured solar observations were used as an input."*

### Prohibited Claims:
- ❌ *"POLARIS was validated on real Nuolja station demand."*
- ❌ *"POLARIS was validated at Nuolja Station."*
- ❌ *"POLARIS achieved X% real-world fuel savings."*
- ❌ *"Nuolja wind generation was measured."*
- ❌ *"Nuolja turbine performance was validated."*
- ❌ *"System reliability was demonstrated for the real station."*

---

## 8. Mandatory Safety & Governance Status Block

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

STEP8_FINAL_CLASSIFICATION    = A — HYBRID FIXTURE FULLY SPECIFIED AND DETERMINISM-READY
```
