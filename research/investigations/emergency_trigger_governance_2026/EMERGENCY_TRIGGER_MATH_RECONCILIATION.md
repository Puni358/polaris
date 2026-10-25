# POLARIS — EMERGENCY TRIGGER MATHEMATICAL RECONCILIATION

## Executive Summary

This mathematical reconciliation document explicitly resolves the distinction between **STORED BATTERY RESERVE TARGETS**, **DELIVERABLE BATTERY ENERGY ABOVE PHYSICAL MINIMUM**, and **SIX-HOUR CRITICAL-LOAD SURVIVABILITY**.

The human governance decision remains locked and unchanged:
- **NORMAL MODE**: The 6-hour critical reserve ($75.652\text{ kWh}$ / $37.83\%\text{ SOC}$) is an operational target, not a hard floor. Battery energy may drop below target without triggering Emergency Mode.
- **EMERGENCY MODE**: Triggered immediately upon validated critical-load service failure OR when net available resources cannot guarantee 6 hours of critical-load survivability ($69.60\text{ kWh}$ delivered demand).
- **RESERVE DEFICIT**: Reserve target deficit alone NEVER triggers Emergency Mode.

---

## 1. Explicit Conceptual & Mathematical Separation

To eliminate ambiguity, three distinct concepts are defined and decoupled:

```
+-----------------------------------------------------------------------------------+
|                           1. STORED RESERVE TARGET                                |
| - E_reserve_stored = (P_crit * T_req) / eta_dis = (11.6 * 6) / 0.92 = 75.652 kWh  |
| - SOC_reserve_target = 75.652 / 200.0 = 37.826% ≈ 37.83%                           |
| - Meaning: Operational target for Normal Mode battery replenishment.              |
| - NOT a physical floor. NOT an Emergency threshold.                               |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|              2. DELIVERABLE BATTERY ENERGY ABOVE PHYSICAL MINIMUM                 |
| - E_batt_deliverable(SOC) = max(0, (SOC - SOC_phys_min) * C_nom * eta_dis)         |
| - For 37.83% SOC: (0.37826 - 0.2000) * 200.0 * 0.92 = 32.80 kWh delivered         |
| - Meaning: Real energy deliverable to the critical bus while honoring 20% SOC.   |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                    3. SIX-HOUR CRITICAL-LOAD SURVIVABILITY                        |
| - E_critical_required = P_critical * T_required = 11.6 kW * 6.0 h = 69.60 kWh     |
| - Meaning: Actual delivered electrical demand required by critical station assets. |
| - Emergency asks: Can net available resources supply >= 69.60 kWh over 6 hours?  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Deliverable Battery Energy Reference Table

For synthetic parameters ($C_{\text{nom}} = 200.0\text{ kWh}$, $SOC_{\text{phys\_min}} = 0.20$, $\eta_{\text{dis}} = 0.92$):

| Nominal SOC (%) | Total Stored Energy ($E_{\text{stored}}$) | Stored Above Min ($E_{\text{stored}} - 40\text{ kWh}$) | Deliverable to Bus ($\text{kWh}_{\text{delivered}}$) | Status / Governance Role |
| :---: | :---: | :---: | :---: | :--- |
| **20.00%** | $40.00\text{ kWh}$ | $0.00\text{ kWh}$ | **$0.00\text{ kWh}$** | **Physical Minimum SOC Floor** |
| **25.00%** | $50.00\text{ kWh}$ | $10.00\text{ kWh}$ | **$9.20\text{ kWh}$** | Deep Deficit / Recovery Active |
| **30.00%** | $60.00\text{ kWh}$ | $20.00\text{ kWh}$ | **$18.40\text{ kWh}$** | Deficit / Recovery Active |
| **37.83%** | **$75.65\text{ kWh}$** | $35.65\text{ kWh}$ | **$32.80\text{ kWh}$** | **Normal Mode Reserve Target ($SOC_{\text{target}}$)** |
| **40.00%** | $80.00\text{ kWh}$ | $40.00\text{ kWh}$ | **$36.80\text{ kWh}$** | Normal Mode Operating Range |
| **50.00%** | $100.00\text{ kWh}$ | $60.00\text{ kWh}$ | **$55.20\text{ kWh}$** | Normal Mode Operating Range |
| **57.83%** | **$115.65\text{ kWh}$** | $75.65\text{ kWh}$ | **$69.60\text{ kWh}$** | **Historical J2 Standalone Autonomy Point** |
| **60.00%** | $120.00\text{ kWh}$ | $80.00\text{ kWh}$ | **$73.60\text{ kWh}$** | High Reserve Energy |
| **80.00%** | $160.00\text{ kWh}$ | $120.00\text{ kWh}$ | **$110.40\text{ kWh}$** | High State of Charge |
| **95.00%** | $190.00\text{ kWh}$ | $150.00\text{ kWh}$ | **$138.00\text{ kWh}$** | **Physical Maximum SOC Limit** |

---

## 3. Explanation of Historical 57.83% SOC Derivation

### 3.1 Mathematical Analysis of Historical J2 Formulation
In early project iterations, $57.83\%\text{ SOC}$ ($115.652\text{ kWh}$) was constructed as:

$$E_{\text{stored\_J2}} = E_{\text{phys\_min}} + E_{\text{reserve\_stored}} = 40.00\text{ kWh} + 75.652\text{ kWh} = 115.652\text{ kWh}$$

$$\text{Nominal SOC} = \frac{115.652\text{ kWh}}{200.0\text{ kWh}} = 57.826\% \approx 57.83\%$$

### 3.2 Why 57.83% Delivered Exactly 6 Hours Standalone
At $SOC = 57.83\%$, stored energy above the physical minimum is $115.652 - 40.00 = 75.652\text{ kWh}$.
Delivered energy to the critical bus is:

$$E_{\text{deliverable}} = 75.652\text{ kWh} \times 0.92 = 69.60\text{ kWh delivered}$$

$$\text{Critical Autonomy Delivered} = \frac{69.60\text{ kWh}}{11.6\text{ kW}} = 6.00\text{ hours}$$

### 3.3 Governance Directive
While $57.83\%$ provided 6 hours of *battery-only* delivery above physical minimum, POLARIS is a hybrid station with diesel generators and renewable generation. **$57.83\%$ MUST NOT BE REUSED AS AN EMERGENCY THRESHOLD.**

---

## 4. Dimensionally Consistent Survivability Margin ($M_{\text{surv}}$)

To ensure mathematical coherence, all terms in the survivability equation MUST represent **bus-delivered energy in kWh** over the 6-hour horizon:

$$M_{\text{surv}}(t) = E_{\text{batt\_deliverable}}(t) + E_{\text{gen\_credible\_bus}}(t, 6\text{h}) + E_{\text{ren\_credible\_bus}}(t, 6\text{h}) - E_{\text{critical\_delivered\_req}}(6\text{h})$$

Where:
- $E_{\text{batt\_deliverable}}(t) = \max\left(0, (SOC(t) - 0.20) \times C_{\text{nom}} \times \eta_{\text{dis}}\right)$ [kWh delivered]
- $E_{\text{gen\_credible\_bus}}(t, 6\text{h})$ = Credible diesel generator energy delivered to critical bus [kWh delivered]
- $E_{\text{ren\_credible\_bus}}(t, 6\text{h})$ = Credible renewable energy delivered to critical bus [kWh delivered]
- $E_{\text{critical\_delivered\_req}}(6\text{h}) = 11.6\text{ kW} \times 6.0\text{ h} = 69.60\text{ kWh delivered}$

---

## 5. Forensic Review of Generation & Renewable Modeling

### 5.1 Dispatchable Generation Modeling Ambiguities
The initial spec simplified generator energy as $E_{\text{gen\_credible}} = P_{\text{gen\_max}} \times 6\text{ h}$. Forensic review identifies the following unresolved modeling questions:
1. **Critical Load Cap**: Should generator energy be capped at the critical load demand ($11.6\text{ kW} \times 6\text{ h} = 69.6\text{ kWh}$), or include maximum generator nameplate capability (e.g. $30\text{ kW} \times 6\text{ h} = 180\text{ kWh}$)?
2. **Fuel Constraints**: Is diesel fuel assumed infinite, or bounded by current day-tank level?
3. **Minimum Loading**: Does generator dispatch require minimum loading ($P_{\text{min}} = 9.0\text{ kW}$)?

**Proposed Candidate Generator Models**:
- **Model G1 (Nameplate Potential)**: $E_{\text{gen}} = H \cdot \sum P_{\text{gen\_max}}$ (Unbounded potential energy).
- **Model G2 (Critical Demand Bounded)**: $E_{\text{gen\_bus}} = \min\left( H \cdot \sum P_{\text{gen\_max}}, \, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}} \right)$ (Bounded by net critical demand).
- **Model G3 (Fuel Bounded)**: $E_{\text{gen}} = \min\left( H \cdot \sum P_{\text{gen\_max}}, \, V_{\text{fuel}} \cdot \rho_{\text{fuel}} \cdot \eta_{\text{gen}} \right)$.

### 5.2 Renewable Confidence Factors ($\gamma_{\text{solar}} = 0.50, \gamma_{\text{wind}} = 0.50$)
- **Status**: The 50% confidence derating factors are **ENGINEERING ASSUMPTIONS**, not human-approved governance decisions.
- **Action**: Flagged in `EMERGENCY_TRIGGER_GOVERNANCE_GAP_REGISTER.md` for human governance review.

---

## 6. Complete Parameter Governance Classification

| Parameter Name | Value | Governance Classification | Rationale / Source |
| :--- | :---: | :--- | :--- |
| Nominal Battery Capacity ($C_{\text{nom}}$) | $200.0\text{ kWh}$ | `DOCUMENTED_PROJECT_FACT` | Benchmark station specification |
| Physical Minimum SOC ($SOC_{\text{min}}$) | $20.0\%$ ($40.0\text{ kWh}$) | `DOCUMENTED_PROJECT_FACT` | Physical battery boundary |
| Physical Maximum SOC ($SOC_{\text{max}}$) | $95.0\%$ ($190.0\text{ kWh}$) | `DOCUMENTED_PROJECT_FACT` | Physical battery boundary |
| Inverter Discharge Efficiency ($\eta_{\text{dis}}$) | $0.92$ | `DOCUMENTED_PROJECT_FACT` | Station electrical model |
| Protected Critical Load ($P_{\text{critical}}$) | $11.6\text{ kW}$ | `GOVERNED_HUMAN_DECISION` | Governed critical station demand |
| Governed Autonomy Horizon ($T_{\text{autonomy}}$) | $6.0\text{ hours}$ | `GOVERNED_HUMAN_DECISION` | Governed survivability requirement |
| Stored Reserve Target ($E_{\text{reserve\_stored}}$) | $75.652\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | $(11.6 \times 6) / 0.92$ |
| Stored Reserve Target SOC ($SOC_{\text{target}}$) | $37.826\%$ | `DERIVED_MATHEMATICAL_VALUE` | $75.652 / 200.0$ |
| Required Critical Delivered Energy | $69.60\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | $11.6 \times 6.0$ |
| Historical J2 Target SOC | $57.826\%$ | `DERIVED_MATHEMATICAL_VALUE` | $(40.0 + 75.652) / 200.0$ |
| Deliverable Energy at Target ($37.83\%$ SOC) | $32.80\text{ kWh}$ | `DERIVED_MATHEMATICAL_VALUE` | $(0.37826 - 0.20) \times 200 \times 0.92$ |
| Renewable Confidence Factors ($\gamma_{\text{solar}}, \gamma_{\text{wind}}$) | $0.50$ | `ENGINEERING_ASSUMPTION` | Requires human governance sign-off |
| Emergency Exit Buffer ($M_{\text{exit\_margin}}$) | $+10.0\text{ kWh}$ | `ENGINEERING_ASSUMPTION` | Requires human governance sign-off |
| Emergency Exit Persistence Window | $4\text{ intervals}$ ($1\text{h}$) | `ENGINEERING_ASSUMPTION` | Requires human governance sign-off |
| Mandatory Generator Availability for Exit | `TRUE` | `UNRESOLVED_GOVERNANCE_DECISION` | Requires human governance choice |
