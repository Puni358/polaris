# POLARIS — EMERGENCY MODE TRIGGER GOVERNANCE RESEARCH REPORT

## Executive Summary

This research report provides the technical, scientific, and governance foundation for defining **Emergency Mode Trigger Semantics** in the POLARIS Energy Management System (EMS). 

Following the explicit human governance decision, the 6-hour critical load reserve ($75.65\text{ kWh}$) is classified as an **operational target during Normal Mode**, rather than a hard physical floor or automatic Emergency Mode trigger. Consequently, battery energy is permitted to be drawn below $75.65\text{ kWh}$ during routine station operations without triggering load shedding.

This report evaluates candidate trigger mechanisms across six functional domains, establishes a robust four-state taxonomy, isolates sensor fault handling (`UNKNOWN / INVALID`), and presents five structured human governance choices required before code implementation begins.

---

## 1. Governance Context & Synthetic System Parameters

### 1.1 Governance Context
In polar research microgrids, power system stability and critical load survivability are paramount. POLARIS governs load protection through two primary modes:
- **NORMAL MODE**: Focuses on fuel optimization, renewable integration, and maintaining battery energy at or near the 6-hour critical load reserve target. Battery energy may drop below the reserve target when necessary to serve load or reduce generator cycling.
- **EMERGENCY MODE**: Focuses strictly on critical load survivability. Enforces Option C load hierarchy curtailment, sacrificing non-critical and flexible loads ($P_{\text{flex}}$) to guarantee power to protected critical assets.

### 1.2 Synthetic System Parameters
The evaluation is based on the following synthetic benchmark parameters:

$$\text{Nominal Battery Capacity } C_{\text{nom}} = 200.0\text{ kWh}$$
$$\text{Physical SOC Envelope } [SOC_{\text{min}}, SOC_{\text{max}}] = [20.0\%, 95.0\%]$$
$$\text{Usable Capacity } C_{\text{usable}} = 200.0 \times (0.95 - 0.20) = 150.0\text{ kWh}$$
$$\text{Protected Critical Load } P_{\text{critical}} = 11.6\text{ kW}$$
$$\text{Governed Autonomy Requirement } T_{\text{autonomy}} = 6.0\text{ hours}$$
$$\text{Discharge Efficiency } \eta_{\text{dis}} = 0.92$$

The stored energy required to support the 6-hour critical load is calculated as:

$$E_{\text{critical, 6h}} = \frac{P_{\text{critical}} \times T_{\text{autonomy}}}{\eta_{\text{dis}}} = \frac{11.6\text{ kW} \times 6.0\text{ h}}{0.92} = 75.652\text{ kWh}$$

Expressed as a state-of-charge percentage:

$$SOC_{\text{target}} = SOC_{\text{min}} + \frac{E_{\text{critical, 6h}}}{C_{\text{nom}}} = 20.0\% + \frac{75.652\text{ kWh}}{200.0\text{ kWh}} = 57.826\% \approx 57.83\%$$

**Governance Directive**: Neither $75.65\text{ kWh}$ nor $SOC < 57.83\%$ constitutes an automatic Emergency trigger.

---

## 2. Four-State Taxonomy & Boundary Protections

To prevent conflating normal battery usage with system emergencies, POLARIS defines four distinct, non-overlapping operational states:

```
+-----------------------------------------------------------------------+
|                              NORMAL MODE                              |
| - Full load service (Critical + Flexible)                             |
| - Battery SOC >= 57.83% (75.65 kWh)                                   |
| - Economic dispatch & fuel optimization                               |
+-----------------------------------------------------------------------+
                                   |
                                   | SOC < 57.83%
                                   v
+-----------------------------------------------------------------------+
|                      RESERVE DEFICIT / RECOVERY                       |
| - Full load service (Critical + Flexible)                             |
| - Battery SOC < 57.83% (Reserve target deficit)                       |
| - Active battery replenishment priorized                              |
| - NOT AN EMERGENCY: Load shedding is PROHIBITED                       |
+-----------------------------------------------------------------------+
                                   |
                                   | Critical survivability threatened
                                   v
+-----------------------------------------------------------------------+
|                            EMERGENCY MODE                             |
| - Governed Option C load shedding enforced                            |
| - Critical load (11.6 kW) hard-protected                              |
| - Non-critical / Flexible loads (P_flex) curtailed                    |
| - Maximum emergency generation dispatch                               |
+-----------------------------------------------------------------------+
                                   |
                                   | Telemetry / Sensor fault
                                   v
+-----------------------------------------------------------------------+
|                         UNKNOWN / INVALID STATE                        |
| - Telemetry missing, stale (>30s), or unphysical                      |
| - UNKNOWN_INVALID != EMERGENCY                                        |
| - Automatic MILP optimization HALTED                                  |
| - Safe-harbor dispatch locked; Operator intervention required         |
+-----------------------------------------------------------------------+
```

---

## 3. Analysis of Candidate Emergency Trigger Families

### 3.1 Family A: Critical Load Service Failure
- **Concept**: Emergency is triggered if actual critical load demand cannot be fully served ($P_{\text{critical, served}} < P_{\text{critical, required}}$).
- **Analysis**:
  - *Immediate Trigger*: Zero delay, but high sensitivity to transient 1-second telemetry blips or communication packet dropouts.
  - *Persisted Trigger*: Requiring $N \ge 2$ consecutive intervals (e.g. 15-30 minutes) prevents false triggers while hardware relays handle instantaneous under-frequency trips.
  - *Verdict*: **Essential persistence-based software trigger candidate.**

### 3.2 Family B: Inability to Guarantee Critical Survivability
- **Concept**: Emergency is triggered if total available controllable energy (battery energy + dispatchable generator capability) is insufficient to maintain 6 hours of critical load service.
- **Analysis**:
  - Conceptually: $E_{\text{available}} < E_{\text{critical, 6h}}$.
  - Allows POLARIS to trigger Emergency Mode *proactively* before physical load shedding occurs, giving Option C load curtailment time to extend battery runtime.
  - *Verdict*: **High-value proactive trigger concept.**

### 3.3 Family C: Battery Depletion Trajectory
- **Concept**: Emergency is triggered if SOC is rapidly declining toward physical minimum ($20.0\%$ SOC / $40.0\text{ kWh}$) and replenishment capability is inadequate.
- **Analysis**:
  - SOC alone ($SOC \le 20.0\%$) is a hard physical minimum floor.
  - Rate of decline ($\frac{dSOC}{dt}$) provides early warning but can be noisy during brief high-load spikes.
  - *Verdict*: **Hard floor at 20% SOC; trajectory serves as a contributing condition.**

### 3.4 Family D: Generation / Resource Loss
- **Concept**: Loss of key generation assets (diesel, solar, wind, battery).
- **Analysis**:
  - Renewable generation loss (solar/wind drop to zero) is normal operating behavior in polar environments (nighttime, calm conditions) and must **NEVER** trigger Emergency Mode.
  - Complete diesel generator failure while battery energy is below target represents a critical threat.
  - *Verdict*: **Multi-resource compound failure (Diesel Loss + Depleted Battery) is a hard trigger.**

### 3.5 Family E: Reserve Recovery Failure
- **Concept**: Normal operation falls below the reserve target ($75.65\text{ kWh}$) and fails to recover within a governed period ($T_{\text{max}}$).
- **Analysis**:
  - If load is 100% served and generation is stable, a prolonged deficit alone does not inherently threaten safety.
  - *Verdict*: **Triggers Warning / Pre-Emergency, not immediate hard load shedding.**

### 3.6 Family F: Forecasted Emergency
- **Concept**: Emergency is triggered ahead of time if predictive models forecast a critical survivability violation within a 24-hour horizon.
- **Analysis**:
  - Forecasts carry inherent uncertainty (cloud cover, wind drop).
  - Forecast risk should trigger pre-emergency alerts and influence normal reserve recovery dispatch, but should not initiate hard Option C load curtailment without physical validation.
  - *Verdict*: **Advisory / Pre-Emergency trigger only.**

---

## 4. Hard vs. Soft Condition Classification Matrix

| Trigger Candidate | Classification | Primary Rationale & Tradeoffs |
| :--- | :--- | :--- |
| **Persisted Critical Load Shortfall** | **PERSISTENCE-BASED TRIGGER** | Direct proof of unserved load; persistence prevents mode chatter. |
| **Imminent Survivability Exhaustion** | **PERSISTENCE-BASED TRIGGER** | Proactive protection; extends battery runtime before blackout. |
| **Physical Min SOC (SOC <= 20%)** | **HARD IMMEDIATE TRIGGER** | Physical battery boundary protection. |
| **Diesel Loss + SOC < 37.83%** | **HARD IMMEDIATE TRIGGER** | Catastrophic loss of primary backup generation. |
| **Renewable Generation Loss** | **NOT SUITABLE AS A TRIGGER** | Normal intermittent operational behavior. |
| **Persistent Reserve Deficit** | **WARNING / PRE-EMERGENCY** | Alert for operator; does not warrant immediate load shedding. |
| **Forecasted 24h Deficit** | **WARNING / PRE-EMERGENCY** | Advisory for optimizer; forecast uncertainty prohibits hard action. |

---

## 5. Telemetry Integrity & Data Fault Safeguards

A critical governance requirement established in prior ECD specifications is:

$$\text{UNKNOWN\_INVALID} \neq \text{EMERGENCY}$$

### 5.1 Telemetry Validation Requirements
Before evaluating any Emergency Mode trigger, POLARIS must validate station telemetry against three criteria:
1. **Range Checks**: $20.0\% \le SOC \le 95.0\%$, $P_{\text{gen}} \ge 0$, $P_{\text{load}} \ge 0$.
2. **Freshness Checks**: Sensor timestamps must be within $\Delta t_{\text{max}} = 30\text{ seconds}$ of system wall clock.
3. **Bus Balance Consistency**: $\left| \sum P_{\text{gen}} - \sum P_{\text{load}} - P_{\text{batt}} \right| \le \epsilon_{\text{tolerance}}$.

### 5.2 Failure Response Protocol
If telemetry fails any validation test:
- **Do NOT transition to Emergency Mode.**
- Lock EMS control outputs to safe-harbor defaults (e.g., run primary diesel at rated minimum output).
- Freeze automatic MILP optimization.
- Emit high-severity operator alarm requesting manual intervention.

---

## 6. Separation of Emergency Entry vs Emergency Response

To maintain mathematical clarity and operational safety, POLARIS strictly decouples state entry logic from state execution logic:

- **ENTRY LOGIC (State Machine)**: Evaluates observable station telemetry to decide *when* to transition into `EMERGENCY` state.
- **RESPONSE LOGIC (Option C Governed Execution)**: Governed by existing ECD policies once inside `EMERGENCY` state:
  1. Critical load ($11.6\text{ kW}$) remains 100% protected and un-relaxable.
  2. Flexible loads ($P_{\text{flex}}$) are curtailed according to the Option C priority hierarchy.
  3. Dispatcher attempts MILP re-solve with relaxed non-critical constraints.
  4. Operator receives full real-time visibility into all curtailment events.

---

## 7. Exit & Automatic Return to Normal Criteria

Consistent with the human governance decision authorizing **AUTOMATIC_RETURN_WITH_OPERATOR_NOTIFICATION_AND_OVERRIDE**, Emergency Mode clears automatically when the following observable conditions are met and sustained:

1. **Critical Load Service**: $P_{\text{critical, served}} = P_{\text{critical, required}}$ for $P \ge 4$ consecutive control intervals (1 hour).
2. **Battery Energy Restored**: Stored battery energy $E_{\text{batt}} \ge 75.65\text{ kWh}$ ($SOC \ge 57.83\%$).
3. **Generation Stability**: At least one dispatchable generator (diesel) is operational and available for dispatch.
4. **Positive Net Power Balance**: Total generation capacity exceeds total connected station demand.

Upon clearing, POLARIS transitions to `NORMAL` mode, ramps flexible loads back online under governed ramp rates, logs the event with cryptographic hashes, and notifies the station operator.

---

## 8. Academic & Industry Literature Review

The proposed POLARIS trigger governance aligns with international microgrid and polar engineering standards:

1. **IEC 62898-2 (Microgrids — Part 2: Operation and Control)**: Standardizes microgrid state transitions between grid-connected, islanded, and emergency modes. Emphasizes that telemetry loss must lead to fail-safe local control rather than uncoordinated load shedding.
2. **IEEE 2030.7 (Standard for the Specification of Microgrid Controllers)**: Defines the core functions of microgrid controllers, including transition logic and load relief. Supports persistence-based filtering for load shedding triggers.
3. **CIGRE WG C6.22 (Microgrid Control Systems)**: Highlights the necessity of separating operational energy reserves (economic target) from emergency load shedding thresholds in remote/isolated microgrids.
4. **ISO 8528-13 (Reciprocating Internal Combustion Engine Driven Alternating Current Generating Sets — Safety)**: Governs emergency diesel generator integration and survivability standards for extreme environments.

---

## 9. Provenance & Verification Manifest

- **Workspace Path**: `/home/punith-bs/01polaris (Copy)`
- **Investigation Folder**: `investigations/emergency_trigger_governance_2026/`
- **Protected File SHA256 Hashes**: 100% Verified Match against Canonical Manifest (`SOURCE_HASH_MANIFEST.json`).
- **Production Modifications**: **0**
