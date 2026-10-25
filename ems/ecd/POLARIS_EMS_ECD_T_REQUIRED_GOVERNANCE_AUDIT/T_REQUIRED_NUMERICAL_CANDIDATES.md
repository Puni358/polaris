# POLARIS EMS — T_REQUIRED NUMERICAL CANDIDATE ANALYSIS

## 1. Overview

This document presents a neutral numerical analysis of potential values for $T_{\text{required}}$ (6h, 12h, 24h, 48h, 72h, 96h). 

> [!CAUTION]
> **NEUTRALITY MANDATE**: None of these values is declared "correct", "optimal", "recommended", or "safest". Selecting a numerical value requires empirical station evidence and explicit human governance authorization.

---

## 2. Numerical Candidate Evaluation Matrix

Assume prototype critical load $P_{\text{crit}} = 30\text{ kW}$ ($30,000\text{ W}$) and linear fuel rate $f_{\text{rate}} = 12.5\text{ L/h}$ at $30\text{ kW}$ for illustrative calculation purposes only.

| Candidate $T_{\text{required}}$ | Required Battery Energy ($C_{\text{usable}}$ at 30kW) | Required Diesel Fuel ($\text{Fuel}_{\text{req}}$ at 12.5 L/h) | Station Evidence Required for Authorization |
| :--- | :--- | :--- | :--- |
| **6.0 Hours** | $180\text{ kWh}$ ($195.6\text{ kWh}$ total at $\eta=0.92$) | $75.0\text{ Liters}$ | Certified fast operator response SLA ($\le 6\text{h}$) |
| **12.0 Hours** | $360\text{ kWh}$ ($391.3\text{ kWh}$ total at $\eta=0.92$) | $150.0\text{ Liters}$ | Standard 12h shift change response protocol |
| **24.0 Hours** | $720\text{ kWh}$ ($782.6\text{ kWh}$ total at $\eta=0.92$) | $300.0\text{ Liters}$ | Daily weather forecast reliability metrics |
| **48.0 Hours** | $1,440\text{ kWh}$ ($1,565.2\text{ kWh}$ total at $\eta=0.92$) | $600.0\text{ Liters}$ | 2-day storm severity duration data |
| **72.0 Hours** | $2,160\text{ kWh}$ ($2,347.8\text{ kWh}$ total at $\eta=0.92$) | $900.0\text{ Liters}$ | 3-day blizzard isolation governance mandate |
| **96.0 Hours** | $2,880\text{ kWh}$ ($3,130.4\text{ kWh}$ total at $\eta=0.92$) | $1,200.0\text{ Liters}$ | Extended 4-day arctic blackout survivability policy |

---

## 3. Analysis of the 72-Hour Synthetic Prototype Value

- **Historical Origin**: Used in HD-03 research and the canonical synthetic ECD test fixture.
- **Classification**: `SYNTHETIC_ENGINEERING_TEST_VALUE_PRESERVED_UNCHANGED`.
- **Station Operational Meaning**: `NONE`.
- **Physical Implications at Prototype Scale**:
  - For battery alone to sustain 72h of $30\text{ kW}$ critical load, usable battery energy would need to be $2,160\text{ kWh}$ ($2.16\text{ MWh}$). The prototype battery is $200\text{ kWh}$ ($160\text{ kWh}$ usable), meaning the prototype battery alone provides only **$4.9\text{ hours}$** of $30\text{ kW}$ support.
  - For diesel alone to sustain 72h at $12.5\text{ L/h}$, required fuel volume is **$900\text{ Liters}$**.
- **Audit Conclusion**: The 72h synthetic test value cannot become production policy without station engineering proof that fuel storage ($\ge 900\text{L}$) or battery capacity ($\ge 2.16\text{MWh}$) is physically installed at Nuolja station.

---

## 4. Evidence Required Before Authorizing Any Numerical Value

To authorize any candidate value $T_{\text{required}} = X\text{ hours}$ for production deployment, governance must verify:

1. **Station Physical Fuel Reserve**: Tank capacity $V_{\text{tank}} \ge X \times f_{\text{rate}}(P_{\text{critical}})$.
2. **Station Battery Reserve**: Installed battery usable energy $C_{\text{usable}} \ge X \times P_{\text{critical}}$ (if battery-only survivability is required).
3. **Logistics Lead Time**: Verified empirical maximum delay between fuel re-order and delivery confirmation.
4. **Meteorological Risk Tolerance**: Formal station policy risk posture regarding extreme weather events.
