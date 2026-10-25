# POLARIS — CRITICAL-LOAD SYNTHETIC CANDIDATES SPECIFICATION

```
CRITICAL_LOAD_STATUS = SYNTHETIC_ENGINEERING_SCENARIO
REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED
SOURCE_DATA = EXTERNAL_ENGINEERING_REFERENCES
```

## 1. Overview & Human Authorization Status

This document proposes **three candidate synthetic critical-load scenarios** constructed from authoritative online engineering data and polar building physics.

*   **IMPORTANT**: These candidates are **proposals only**.
*   **NO WINNER HAS BEEN SELECTED**.
*   **NO RUNTIME CODE OR YAML FIXTURE HAS BEEN MODIFIED** (`SOURCE_MODIFICATIONS = 0`).
*   The human project owner will review these candidates and explicitly authorize one scenario before any execution.

---

## 2. Proposed Candidate Synthetic Scenarios

Each candidate scenario specifies the minimum viable power $P_{i,\text{min}}(t)$ for the three protected life-safety categories under the human-governed formulation:

$$P_{\text{critical}}(t) = P_{\text{heating,min}}(t) + P_{\text{water,min}}(t) + P_{\text{comms,min}}(t)$$

---

### SCENARIO A — CONSERVATIVE (Minimal Essential Survivability Baseline)

Designed for ultra-efficient, highly insulated micro-shelters relying on high-COP heat pumps and minimal standby communications.

*   **$P_{\text{heating,min}}(t)$**: **2.00 kW** (Continuous minimum heat pump compressor operation / baseline freeze protection).
*   **$P_{\text{water,min}}(t)$**: **0.10 kW** (100 W average for intermittent UV sterilization, micro-filtration, and low-energy intake circulation pump).
*   **$P_{\text{comms,min}}(t)$**: **0.05 kW** (50 W for Iridium satellite modem standby, emergency VHF radio receiver, and Campbell telemetry logger).
*   **Total $P_{\text{critical}}(t)$**: **2.15 kW** (Static baseline across 8,784 hours).

---

### SCENARIO B — CENTRAL ENGINEERING CASE (Nominal Remote Polar Research Station)

Represents typical polar/sub-Arctic research station operational magnitudes based on published engineering studies.

#### Option B.1: Static Constant Formulation
*   **$P_{\text{heating,min}}(t)$**: **5.00 kW** (Nominal electric space heating demand to sustain $+5^\circ\text{C}$ indoor core during typical winter conditions).
*   **$P_{\text{water,min}}(t)$**: **0.30 kW** (300 W continuous equivalent for filtration, UV disinfection, and intake pipe trace heating).
*   **$P_{\text{comms,min}}(t)$**: **0.15 kW** (150 W for satellite transceiver, network router, emergency radio, and telemetry server).
*   **Total $P_{\text{critical}}(t)$**: **5.45 kW** (Static baseline across 8,784 hours).

#### Option B.2: Dynamic Outdoor-Temperature-Dependent Formulation
*   **$P_{\text{heating,min}}(T_{\text{out}}(t))$**: Linear model based on building heat loss ($UA = 120\text{ W/K}$):
    $$P_{\text{heating,min}}(T_{\text{out}}) = \max\left(2.0, 5.0 - 0.12 \times T_{\text{out}}(t)\right) \quad [\text{kW}]$$
    *   At $T_{\text{out}} = 0^\circ\text{C} \implies P_{\text{heating,min}} = 5.0\text{ kW}$.
    *   At $T_{\text{out}} = -25^\circ\text{C} \implies P_{\text{heating,min}} = 8.0\text{ kW}$.
*   **$P_{\text{water,min}}(t)$**: **0.30 kW**.
*   **$P_{\text{comms,min}}(t)$**: **0.15 kW**.
*   **Total Dynamic $P_{\text{critical}}(t)$**: **2.45 kW to 8.45 kW** (Varies hourly with temperature trajectory).

---

### SCENARIO C — HIGH / ROBUSTNESS CASE (High-Capacity Severe Storm Reserve)

Provides a high-margin robustness test scenario for extreme polar blizzards with maximum resistive freeze protection.

*   **$P_{\text{heating,min}}(t)$**: **10.00 kW** (Full 10 kW resistive heater array for high-wind infiltration and severe sub-zero cold).
*   **$P_{\text{water,min}}(t)$**: **0.80 kW** (800 W continuous for active RO water maker, high-pressure pump, and heavy intake line trace heating).
*   **$P_{\text{comms,min}}(t)$**: **0.30 kW** (300 W for active high-bandwidth satellite link, repeaters, and emergency comms rack).
*   **Total $P_{\text{critical}}(t)$**: **11.10 kW** (Static baseline across 8,784 hours).

---

## 3. Comparison & Compatibility Matrix

All proposed candidate scenarios are audited against the existing synthetic H1.0 total station demand trajectory ($P_{\text{total\_synthetic\_demand}}(t) \in [15.0\text{ kW}, 45.0\text{ kW}]$):

| Scenario | $P_{\text{heating,min}}$ | $P_{\text{water,min}}$ | $P_{\text{comms,min}}$ | Total $P_{\text{critical}}$ | Min H1.0 Demand | $P_{\text{critical}} \le P_{\text{demand}}$ Check | Max Critical Ratio |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Scenario A** | 2.00 kW | 0.10 kW | 0.05 kW | **2.15 kW** | 15.00 kW | **PASS** ($2.15 \le 15.0$) | 14.3% |
| **Scenario B (Static)** | 5.00 kW | 0.30 kW | 0.15 kW | **5.45 kW** | 15.00 kW | **PASS** ($5.45 \le 15.0$) | 36.3% |
| **Scenario B (Dynamic)**| 2.00–8.00 kW | 0.30 kW | 0.15 kW | **2.45–8.45 kW** | 15.00 kW | **PASS** ($8.45 \le 15.0$) | 56.3% |
| **Scenario C** | 10.00 kW | 0.80 kW | 0.30 kW | **11.10 kW** | 15.00 kW | **PASS** ($11.10 \le 15.0$) | 74.0% |

**Audit Finding**: Every candidate scenario strictly satisfies $P_{\text{critical}}(t) \le P_{\text{total\_synthetic\_demand}}(t)$ for all 8,784 hourly cycles without requiring synthetic demand clipping or redesign.

---

## 4. Double-Counting Risk Analysis

To prevent inflating $P_{\text{critical}}(t)$, the following potential overlaps have been analyzed:

1.  **UPS Conversion Losses**: Communications equipment draws power via the station battery/UPS. The candidate values specify net AC load; UPS efficiency ($\eta \approx 0.90$) is handled at the converter level in ECD.
2.  **Water Line Trace Heating vs Space Heating**: Pipe heating inside the building envelope radiates heat into the interior space. In Scenario B/C, trace heating is restricted to external raw-water intake lines to avoid double-counting indoor space heat.
3.  **Pump Thermal Dissipation**: Mechanical pump losses convert into thermal energy within the water volume. This minor thermal credit is neglected as conservative engineering margin.

---

## 5. Next Steps for Human Selection

1.  **Human Project Owner Action**: Select Scenario A, Scenario B (Static or Dynamic), or Scenario C.
2.  **Implementation**: Once selected, update `loads.yaml` fixture (if authorized) with the chosen synthetic parameter.
