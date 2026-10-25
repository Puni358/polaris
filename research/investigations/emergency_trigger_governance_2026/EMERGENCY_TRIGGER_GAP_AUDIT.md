# POLARIS — EMERGENCY TRIGGER GOVERNANCE GAP AUDIT

## Executive Summary

This document provides a comprehensive forensic audit of the **five unresolved governance gaps and engineering assumptions** identified in the POLARIS Emergency Mode specification.

The locked human governance decisions remain strictly unchanged:
1. Validated critical-load service failure $\implies$ immediate Emergency.
2. Emergency may trigger before actual critical-load failure when 6-hour critical survivability ($69.60\text{ kWh}$ delivered demand) cannot be credibly guaranteed ($M_{\text{surv}} < 0$).
3. Reserve deficit alone ($SOC < 37.83\%$ / $75.652\text{ kWh}$ stored) NEVER triggers Emergency.
4. Resource loss triggers Emergency ONLY when remaining resources cannot guarantee 6-hour critical survivability.
5. Emergency may automatically return to NORMAL when conditions clear and survivability is secure, with operator notification and override.

This audit evaluates the unresolved technical and governance choices required before code implementation begins.

---

## GAP 1 — Credible Dispatchable Generation Modeling

### 1. Current Specification Position
> "The preliminary implementation specification modeled generator energy as $E_{\text{gen\_credible}} = \sum (P_{\text{gen\_max\_available}} \times 6\text{ h})$."

### 2. Exact Unresolved Question
> **"What does POLARIS mean by CREDIBLE dispatchable generation over the six-hour survivability horizon?"**

### 3. Classification
- **Primary Classification**: `HUMAN GOVERNANCE DECISION` (Model selection & energy capping rule).
- **Secondary Classification**: `ENGINEERING ASSUMPTION` (Fuel consumption curves, thermal derating parameters).

### 4. System Impact
- **Affected Subsystems**: Emergency Entry ($M_{\text{surv}}$ calculation), Emergency Exit, Survivability Assessment, Multi-Resource Loss evaluation.

### 5. Candidate Mathematical Formulations

#### MODEL A: Nameplate Potential Energy
- **Formula**: $E_{\text{gen\_credible\_A}} = H \cdot \sum_{k \in K} P_{\text{gen\_k, max}}$ ($H = 6.0\text{ h}$)
- **Required Inputs**: Generator nameplate capacities $P_{\text{gen\_k, max}}$.
- **Strengths**: Simple, deterministic, model-independent.
- **Limitations**: Overestimates credible generation by assuming generator can run at 100% capacity regardless of station load or fuel reserves.
- **Effect on Emergency Detection**: Highly conservative against entering Emergency (may delay Emergency entry if generator is large).

#### MODEL B: Credible Available Operating Capacity
- **Formula**: $E_{\text{gen\_credible\_B}} = H \cdot \sum_{k \in K} \left( A_k(t) \cdot \delta_{\text{derate}} \cdot P_{\text{gen\_k, rated}} \right)$
- **Required Inputs**: Generator availability flags $A_k(t)$, derating factors $\delta_{\text{derate}}$.
- **Strengths**: Accounts for maintenance lockouts and environmental/polar derating.
- **Limitations**: Does not bound generation by actual station critical demand or fuel availability.
- **Effect on Emergency Detection**: Prevents false confidence from faulted or derated generators.

#### MODEL C: Fuel-Constrained Deliverable Energy
- **Formula**: $E_{\text{gen\_credible\_C}} = \min\left( H \cdot \sum A_k P_{\text{max}}, \; V_{\text{fuel\_daytank}} \cdot \rho_{\text{fuel}} \cdot \eta_{\text{gen}} \right)$
- **Required Inputs**: Measured day-tank fuel volume $V_{\text{fuel\_daytank}}$, generator fuel efficiency $\eta_{\text{gen}}$.
- **Strengths**: Protects against fuel exhaustion during polar blizzards.
- **Limitations**: Requires reliable fuel tank telemetry.
- **Effect on Emergency Detection**: Triggers Emergency preemptively if day-tank fuel drops below 6-hour critical load requirement.

#### MODEL D: Critical-Load Bounded Energy
- **Formula**: $E_{\text{gen\_credible\_D}} = \min\left( H \cdot \sum A_k P_{\text{max}}, \; \max(0, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}}) \right)$
- **Required Inputs**: Connected critical load requirement ($69.60\text{ kWh}$).
- **Strengths**: Mathematically exact for critical bus balance; does not credit excess unserved generator potential toward critical safety.
- **Limitations**: Caps generator credit at critical demand.
- **Effect on Emergency Detection**: Provides exact dimensional match to net critical energy deficit.

#### MODEL E: Dynamic Status-Constrained Generation Model
- **Formula**: $E_{\text{gen\_credible\_E}} = \int_0^H \min\left( \sum A_k(\tau) P_{\text{max}}, \, P_{\text{critical}} \right) d\tau$
- **Required Inputs**: Generator availability, startup time constraints, fuel limits.
- **Strengths**: Combines fuel limits, critical load capping, and availability.
- **Limitations**: Higher complexity.

### 6. Human Governance vs. Engineering Allocation
- **Must Be Decided by Human**: Selection between Model A, B, C, D, or E (specifically whether generator energy is capped by critical demand and whether fuel volume is required to establish credibility).
- **Safe as Engineering Assumption**: Technical fuel-to-kWh efficiency coefficients ($\eta_{\text{gen}}$) and specific thermal derating tables.

---

## GAP 2 — Renewable Credibility & 50% Derating Factors

### 1. Current Specification Position
> "The draft spec introduced $\gamma_{\text{solar}} = 0.50$ and $\gamma_{\text{wind}} = 0.50$ derating factors for forecast renewable energy: $E_{\text{ren\_credible}} = \int_0^6 (\gamma_{\text{solar}} \hat{P}_{\text{solar}} + \gamma_{\text{wind}} \hat{P}_{\text{wind}}) d\tau$."

### 2. Exact Unresolved Question
> **"Status and defensibility of renewable forecast derating factors: Should renewable generation be credited toward 6-hour critical survivability guarantees, and if so, under what confidence mechanism?"**

### 3. Classification
- **Primary Classification**: `HUMAN GOVERNANCE DECISION` (Policy on trusting renewables for critical safety).
- **Secondary Classification**: `ENGINEERING ASSUMPTION` (Specific numerical derating factors $\gamma$).

### 4. System Impact
- **Affected Subsystems**: Emergency Entry ($M_{\text{surv}}$ calculation), Forecast Dependency, Preemptive Emergency Triggers.

### 5. Candidate Approaches

#### Approach A: Fixed Percentage Derating ($\gamma = 0.50$)
- **Mechanism**: Multiply raw solar/wind forecasts by fixed factor 0.50.
- **Strengths**: Simple to compute.
- **Limitations**: Arbitrary factor; does not reflect actual forecast uncertainty.

#### Approach B: Forecast-Confidence Quantile (e.g. P10 Confidence Interval)
- **Mechanism**: Use the 10th percentile (P10) lower confidence bound from probabilistic weather forecasts.
- **Strengths**: Statistically rigorous; adapts to weather predictability.
- **Limitations**: Requires probabilistic forecasting model.

#### Approach C: Forecast + Uncertainty Envelope
- **Mechanism**: $\hat{P}_{\text{ren\_credible}} = \max(0, \hat{P}_{\text{forecast}} - k \cdot \sigma_{\text{forecast}})$.
- **Strengths**: Explicitly accounts for forecast error variance $\sigma$.
- **Limitations**: Requires historical forecast error statistics.

#### Approach D: Zero Renewable Credit for Emergency Guarantee ($\gamma = 0.00$)
- **Mechanism**: Set $E_{\text{ren\_credible}} = 0.0\text{ kWh}$ in emergency survivability calculations.
- **Strengths**: Fail-safe; guarantees critical load survivability relying ONLY on dispatchable assets (battery + diesel).
- **Limitations**: Conservative; may enter Emergency during daylight solar periods if diesel is offline.

#### Approach E: Resource-Specific Dynamic Credibility
- **Mechanism**: Solar derated by 20% ($\gamma_{\text{solar}} = 0.80$), wind derated by 70% ($\gamma_{\text{wind}} = 0.30$) due to high polar wind turbulence.
- **Strengths**: Reflects resource-specific predictability.
- **Limitations**: Requires site empirical validation.

#### Approach F: Persistence-Based Renewable Extrapolation
- **Mechanism**: Assume renewable power equals current measured output for 2 hours, then decays to zero.
- **Strengths**: Does not rely on external weather forecasts.
- **Limitations**: Ignore incoming weather fronts.

### 6. Human Governance vs. Engineering Allocation
- **Must Be Decided by Human**: Policy decision on whether renewable forecasts may be trusted for 6-hour critical survivability (Approach D vs Approaches A–C/E/F).
- **Safe as Engineering Assumption**: Specific statistical confidence intervals or numerical derating factors ($\gamma$).

---

## GAP 3 — Emergency Exit Criteria Parameters

### 1. Current Specification Position
> "The preliminary draft contained four exit conditions: 1) Critical load 100% served, 2) $M_{\text{surv}} \ge +10.0\text{ kWh}$, 3) $SOC \ge 37.83\%$, 4) Dispatchable generator available, 5) 4 consecutive intervals persistence."

### 2. Exact Unresolved Question
> **"Which numerical exit conditions are mandatory governance policy vs implementation details?"**

### 3. Classification & Audit Table

| Parameter / Condition | Preliminary Value | Audit Classification | Governance Impact |
| :--- | :---: | :--- | :--- |
| **Critical Load 100% Served** | $100\%$ ($11.6\text{ kW}$) | `GOVERNED_HUMAN_DECISION` | Mandatory (Already approved). |
| **Survivability Margin Buffer** | $M_{\text{surv}} \ge +10.0\text{ kWh}$ | `ENGINEERING_ASSUMPTION` | Prevents chatter near $M_{\text{surv}} = 0$. |
| **Reserve Target Restoration** | $SOC \ge 37.83\%$ ($75.65\text{ kWh}$) | `REQUIRES_HUMAN_APPROVAL` | Prevents immediate re-entry to Deficit/Emergency. |
| **Mandatory Generator Available** | $A_k = 1$ | `REQUIRES_HUMAN_APPROVAL` | Ensures dispatchable backup exists before exiting Emergency. |
| **Exit Persistence Window** | $4\text{ intervals}$ ($1.0\text{ h}$) | `IMPLEMENTATION_DETAIL` | Ensures stability over short-term solar bursts. |

### 4. Human Decision Checklist for Emergency Exit
1. **Decision 3.1 (Exit Reserve Requirement)**: Should automatic return to `NORMAL` require battery $SOC \ge 37.83\%$ ($75.652\text{ kWh}$), or should return to `RESERVE_DEFICIT` be permitted when $SOC < 37.83\%$ as long as $M_{\text{surv}} \ge 0$?
2. **Decision 3.2 (Generator Availability for Exit)**: Should automatic return to `NORMAL` require at least one operational diesel generator, or can the system return to `NORMAL` on battery + renewables alone?

---

## GAP 4 — Survivability Horizon & Forecast Dependency

### 1. Current Specification Position
> "The governed survivability horizon is 6 hours ($69.60\text{ kWh}$ critical demand)."

### 2. Exact Unresolved Question
> **"What evidence is sufficient to declare 6-hour survivability guaranteed when weather forecasts are missing or unverified?"**

### 3. Classification
- **Primary Classification**: `HUMAN GOVERNANCE DECISION` (Fallback policy when forecasts fail).
- **Secondary Classification**: `DOCUMENTATION/TRACEABILITY GAP`.

### 4. Analysis of Alternatives
- **Alternative 1 (Forecast-Independent Guarantee)**: Declare 6-hour survivability guaranteed ONLY if battery deliverable energy + dispatchable generator capacity $\ge 69.60\text{ kWh}$ (Zero forecast reliance).
- **Alternative 2 (Forecast-Assisted Guarantee)**: Allow renewable forecasts to count toward the 6-hour guarantee when telemetry validation confirms forecast freshness ($\Delta t \le 30\text{ s}$).
- **Alternative 3 (Missing-Forecast Fallback)**: If forecasts are missing/unverified, set $E_{\text{ren}} = 0.0$ and evaluate survivability solely on dispatchable assets.

---

## GAP 5 — Exit / Recovery Semantics & State Transitions

### 1. Current Specification Position
> "Emergency exit specifies transition to `NORMAL` mode."

### 2. Exact Unresolved Question
> **"Can Emergency Mode exit directly into `RESERVE_DEFICIT` state if critical load survivability is secure ($M_{\text{surv}} \ge 0$) but battery SOC remains below target ($SOC < 37.83\%$)?**

### 3. Classification
- **Primary Classification**: `HUMAN GOVERNANCE DECISION` (Allowed state machine transition paths).

### 4. Analysis of Transition Paths

```
+-----------------------------------------------------------------------------------+
|                        OPTION A: DIRECT TO NORMAL ONLY                            |
| EMERGENCY --> NORMAL (Requires SOC >= 37.83% AND M_surv >= +10 kWh)               |
| - Pro: Guarantees full reserve restoration before clearing Emergency.             |
| - Con: Holds Option C load shedding active longer even if diesel is running fine. |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                     OPTION B: PERMIT EXIT TO RESERVE_DEFICIT                      |
| EMERGENCY --> RESERVE_DEFICIT (If M_surv >= 0 but SOC < 37.83%)                   |
| - Pro: Restores flexible loads immediately once diesel/generation secures 6h.     |
| - Con: Transitions immediately from Emergency into Reserve Deficit.               |
+-----------------------------------------------------------------------------------+
```

---

## Summary of Governance Gap Classifications

```yaml
GAP_1_GENERATOR_CREDIBILITY: HUMAN_GOVERNANCE_DECISION (Model Choice)
GAP_2_RENEWABLE_DERATING: HUMAN_GOVERNANCE_DECISION (Policy on Trusting Forecasts)
GAP_3_EXIT_PARAMETERS: REQUIRES_HUMAN_APPROVAL (SOC & Diesel Exit Requirements)
GAP_4_FORECAST_DEPENDENCY: HUMAN_GOVERNANCE_DECISION (Missing Forecast Fallback)
GAP_5_EXIT_TRANSITIONS: HUMAN_GOVERNANCE_DECISION (Exit to Deficit vs Normal)
```
