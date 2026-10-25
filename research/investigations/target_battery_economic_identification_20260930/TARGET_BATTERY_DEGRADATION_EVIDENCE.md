# POLARIS — Target Battery Degradation Evidence Analysis

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Degradation Evidence Audit Overview

This document categorizes all degradation evidence relevant to POLARIS according to the strict evidence classification standard defined in Section 10 of the campaign instructions.

---

## 2. Categorized Degradation Evidence Matrix

| Degradation Parameter | Classification Category | Value / Status | Source & Provenance |
|---|---|---|---|
| **Measured Capacity Fade** | **UNKNOWN** | Zero empirical data | No capacity test logs exist for target site |
| **SOH Historical Trajectory** | **UNKNOWN** | Zero empirical data | No SOH logging performed at site |
| **Cycle Aging Measurements** | **UNKNOWN** | Zero empirical data | No controlled laboratory or field cycle tests for target |
| **Calendar Aging Measurements** | **UNKNOWN** | Zero empirical data | No static SOC/temperature storage loss logs for target |
| **Cycle Count History** | **SYNTHETIC** | 4.04 EFC/yr (C0) | Output of MILP simulation on synthetic fixture |
| **Depth of Discharge (DoD)** | **SYNTHETIC** | Max 18.04% DoD (C0) | Output of MILP simulation on synthetic fixture |
| **Temperature Exposure Log** | **LITERATURE_DERIVED** | Derived from outdoor temp | Ambient weather logged; cell temp unlogged |
| **Charge/Discharge Rates (C-rate)** | **SYNTHETIC** | Max 0.25C (50 kW / 200 kWh) | Defined by synthetic fixture bounds |
| **OEM End-of-Life Criteria** | **UNKNOWN** | Unspecified | No target manufacturer datasheet available |
| **Warranty Degradation Limits** | **UNKNOWN** | Unspecified | No target warranty contract available |
| **Replacement Schedule** | **UNKNOWN** | Unspecified | No asset management schedule available |
| **Degradation Wear Cost Proxy** | **SYNTHETIC** | $0.00005/Wh ($0.05/kWh) | Linear cost surrogate hardcoded in `milp.py` |

---

## 3. Physical Model Structure vs Target Parameterization

- **Model Structure**: Supported by Tier C academic literature (Wang 2011, Schmalstieg 2014, NREL BLAST):
  $$Q_{\text{loss}} = A \cdot \exp\left(-\frac{E_a}{R T}\right) \cdot t^z + B \cdot \text{Ah}_{\text{throughput}}$$
- **Target Parameterization**: `NOT IDENTIFIABLE`. The pre-exponential factor $A$, activation energy $E_a$, time exponent $z$, and cycle wear coefficient $B$ require cell-chemistry-specific fitting against empirical test data.

> [!CAUTION]
> Using generic literature parameters (e.g., LFP parameters from Wang 2011) to simulate a hypothetical Nuolja battery provides a useful **research sensitivity tool**, but does NOT constitute target-hardware validation.
