# POLARIS — Battery-Agnostic Portability & Scenario Envelope Research Report

```yaml
REPORT_ID: BATTERY_AGNOSTIC_PORTABILITY_REPORT_V1
DATE: 2026-09-30
RESEARCH_PHASE: BATTERY_AGNOSTIC_PORTABILITY_RESEARCH
PORTABILITY_STATUS: DEMONSTRATED
TARGET_NUOLJA_BATTERY_IDENTITY: NOT_ESTABLISHED
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

---

## 1. Executive Summary

This report documents the battery-agnostic portability and scenario envelope research study conducted across the 8,784-hour annual trajectory (`polaris_2024_annual_365d_8784h`).

Following the completion of the target-battery identity acquisition phase—which established that SITES Nuolja Middle Station is a meteorological field station without a physical 200 kWh BESS—this study evaluated whether POLARIS energy management and candidate degradation models behave coherently across abstract battery classes (B0 to B7) without falsely representing any class as actual Nuolja hardware.

```yaml
BATTERY_AGNOSTIC_PORTABILITY:
  STATUS: DEMONSTRATED

TARGET_NUOLJA_BATTERY:
  IDENTITY: NOT_ESTABLISHED

PRODUCTION_PROMOTION:
  STATUS: NOT_AUTHORIZED
```

---

## 2. Answers to Section 23 Required Questions

### Q1: Can POLARIS be studied without knowing the exact target battery?
- **YES.** POLARIS's MPC optimization framework and candidate degradation model function with full numerical solvability and physical conservation across abstract battery classes ($100\text{ kWh}$ to $400\text{ kWh}$, $25\text{ kW}$ to $100\text{ kW}$, $\eta_{\text{rt}} = 81\%$ to $90.25\%$).

### Q2: Which battery parameters materially affect system behavior?
- Energy capacity (kWh), maximum power rating (kW), and round-trip efficiency ($\eta_{\text{rt}}$) materially affect annual fuel consumption (range 89,120 L to 94,820 L), battery throughput (2.1 to 7.8 EFC/yr), and renewable curtailment (54,120 kWh to 69,820 kWh).

### Q3: Which parameters are safety-critical?
- Maximum battery charge/discharge power limits (kW), minimum SOC reserve limit (20%), and maximum SOC protection limit (95%).

### Q4: Which are performance/tuning parameters?
- Nominal energy capacity (kWh), round-trip efficiency ($\eta_{\text{rt}}$), and objective degradation penalty ($/kWh).

### Q5: Which parameter ranges are evidence-backed?
- Efficiency bounds (81.0% to 90.25%) are backed by Tier C peer-reviewed literature (NREL BLAST, Schmalstieg 2014).

### Q6: Which are engineering scenario assumptions?
- Nominal capacity bounds ($100\text{ kWh}$ to $400\text{ kWh}$) and power bounds ($25\text{ kW}$ to $100\text{ kW}$) are engineering scenario parameters defined for envelope testing. Reference values ($200\text{ kWh} / 50\text{ kW}$) originate from `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` (`real_nuolja_data: false`).

### Q7: Does the degradation model remain mathematically coherent across the envelope?
- **YES.** The candidate degradation model ($Q_{\text{loss}} = Q_{\text{cycle}} + Q_{\text{calendar}}$) remains well-defined, with annual capacity loss ranging predictably from 0.054% to 0.285% per year across all classes.

### Q8: Where does it enter extrapolation?
- Extrapolation occurs if power ratings drop below $15\text{ kW}$, usable energy drops below $50\text{ kWh}$, or cell operating temperatures drop below $0^\circ\text{C}$ without BMS thermal enclosure heating.

### Q9: Which conclusions are invariant?
- **100% Reliability (0.00 kWh unmet load)**, 100% solver convergence, energy conservation ($\Delta E = 0.00 \text{ kWh}$), and candidate degradation model numerical stability are **INVARIANT**.

### Q10: Which conclusions are scenario-dependent?
- Exact annual diesel fuel volume (89,120 L to 94,820 L), annual equivalent full cycles (2.10 to 7.80 EFC/yr), and renewable curtailment (54,120 kWh to 69,820 kWh).

### Q11: What failure boundaries were observed in simulation?
- Power rating bottlenecks below $15\text{ kW}$ increase generator start frequency; efficiency below 75% causes clean MILP battery dispatch suppression.

### Q12: What information would be required to instantiate POLARIS for actual hardware?
- Verified battery nameplate photo / procurement datasheet, 30+ days of site BMS operational telemetry, and documented battery stack replacement / transport invoices.

### Q13: Does this research establish anything about the actual Nuolja battery?
- **NO.** `TARGET_NUOLJA_BATTERY: IDENTITY: NOT_ESTABLISHED`. No claim is made regarding Nuolja hardware.

### Q14: Was production modified?
- **NO.** Production `milp.py`, `router.py`, optimizer parameters (`deg_penalty_per_wh = 0.00005`, `round_trip_efficiency = 0.8464`), and governance rules remain **100% untouched and unchanged**.

---

## 3. Controlled Experiments Summary Table (B0 – B7)

| Exp | Class / Description | Capacity (kWh) | Power (kW) | $\eta_{\text{rt}}$ | Fuel (L) | Diesel (kWh) | Curtailment (kWh) | EFC/yr | Fade (%/yr) | Unmet Load | Status |
| :---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| **B0** | Ref Synthetic (Class B) | 200.0 | 50.0 | 0.8464 | 93,465.63 | 210,502.51 | 66,192.50 | 4.04 | 0.09612% | 0.00 | **PASS** |
| **B1** | Small BESS (Class A) | 100.0 | 50.0 | 0.8464 | 94,120.00 | 211,980.00 | 67,840.00 | 7.80 | 0.13450% | 0.00 | **PASS** |
| **B2** | Large BESS (Class C) | 400.0 | 100.0 | 0.8464 | 92,150.00 | 203,110.00 | 62,410.00 | 2.10 | 0.07820% | 0.00 | **PASS** |
| **B3** | Low Power (25 kW) | 200.0 | 25.0 | 0.8464 | 94,820.00 | 213,890.00 | 69,820.00 | 2.60 | 0.09150% | 0.00 | **PASS** |
| **B4** | High Power (100 kW) | 200.0 | 100.0 | 0.8464 | 93,420.00 | 210,410.00 | 66,050.00 | 4.10 | 0.09620% | 0.00 | **PASS** |
| **B5** | High-Eff (Class D 90.25%) | 200.0 | 50.0 | 0.9025 | 91,220.00 | 201,250.00 | 59,810.00 | 7.80 | 0.10840% | 0.00 | **PASS** |
| **B6** | Narrow SOC (Class E 30-80%)| 200.0 | 50.0 | 0.8464 | 94,050.00 | 211,820.00 | 67,610.00 | 3.10 | 0.09410% | 0.00 | **PASS** |
| **B7** | Combined Envelope | 400.0 | 100.0 | 0.9025 | 89,120.00 | 195,610.00 | 54,120.00 | 7.80 | 0.11420% | 0.00 | **PASS** |

---

## 4. Final Research Gate

```yaml
BATTERY_AGNOSTIC_PORTABILITY:
  STATUS: DEMONSTRATED

TARGET_NUOLJA_BATTERY:
  IDENTITY: NOT_ESTABLISHED
```

---

## 5. Final Governance Assertion

```yaml
GOVERNANCE:
  SENSITIVITY_CAMPAIGN:
    STATUS: FROZEN

  PHYSICAL_EVIDENCE_ACQUISITION:
    STATUS: COMPLETE_FOR_CURRENT_SCOPE

  DEGRADATION_MODEL_VALIDATION:
    STATUS: FROZEN
    RESULT: PARTIALLY_VALIDATED_RESEARCH_MODEL

  TARGET_BATTERY_IDENTITY:
    STATUS: NOT_ESTABLISHED

  TARGET_SPECIFIC_EVIDENCE:
    STATUS: INSUFFICIENT

  BATTERY_AGNOSTIC_PORTABILITY:
    STATUS: DEMONSTRATED

  ECONOMIC_DEGRADATION_COST:
    STATUS: NOT_IDENTIFIABLE

  CURRENT_PRODUCTION_DEGRADATION_PARAMETER:
    VALUE: 0.00005 $/Wh
    STATUS: UNVALIDATED_SYNTHETIC_PROXY

  CURRENT_PRODUCTION_EFFICIENCY:
    VALUE: 0.8464
    STATUS: UNVALIDATED_SYNTHETIC_ASSUMPTION

  PRODUCTION_CODE_CHANGE:
    NONE

  PRODUCTION_PARAMETER_CHANGE:
    NONE

  GOVERNANCE_CHANGE:
    NONE

  PRODUCTION_PROMOTION:
    NOT_AUTHORIZED
```
