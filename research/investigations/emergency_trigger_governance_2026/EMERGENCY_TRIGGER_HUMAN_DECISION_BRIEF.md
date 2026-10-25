# POLARIS — EMERGENCY TRIGGER HUMAN DECISION BRIEF

## Executive Overview

Following the human governance decision establishing that the 6-hour critical load energy reserve ($75.65\text{ kWh}$) is a **NORMAL MODE reserve target** and **NOT a hard SOC floor**, this decision brief presents the analytical foundation for governing transitions into and out of **EMERGENCY MODE**.

Under Emergency Mode, POLARIS enforces Option C load hierarchy curtailment to protect critical load survivability ($11.6\text{ kW}$ critical load for 6 hours). To ensure predictable, safe, and explainable operations, the human project owner must decide the exact observable trigger conditions.

---

## Governed Parameters & Operational Context

| Parameter | Value | Operational Context |
| :--- | :--- | :--- |
| **Nominal Battery Capacity** | $200.0\text{ kWh}$ | Fixed synthetic benchmark capacity |
| **Usable SOC Range** | $20.0\% \text{ to } 95.0\%$ | Physical battery operating envelope ($150.0\text{ kWh}$ usable) |
| **Critical Station Load** | $11.6\text{ kW}$ | Governed protected critical load |
| **Critical Autonomy Target** | $6.0\text{ hours}$ | Governed survivability requirement |
| **Discharge Efficiency** | $0.92$ | Inverter / battery round-trip efficiency factor |
| **6-Hour Reserve Target** | $75.65\text{ kWh}$ ($57.83\%\text{ SOC}$) | **Normal Mode target**, not an automatic Emergency trigger |
| **Physical Min SOC Floor** | $40.00\text{ kWh}$ ($20.00\%\text{ SOC}$) | Usable battery exhaustion limit |

---

## State Taxonomy & Boundary Protections

The proposed governance framework establishes four distinct operational states:
1. **NORMAL**: $SOC \ge 57.83\%$ ($75.65\text{ kWh}$), full load service, standard economic dispatch.
2. **RESERVE DEFICIT / RECOVERY**: $SOC < 57.83\%$, full critical load service maintained, active reserve restoration, **NOT Emergency**.
3. **EMERGENCY**: Governed emergency state. Option C load shedding enforced to protect critical load survivability.
4. **UNKNOWN / INVALID**: Telemetry failure or missing data. **Must NEVER automatically trigger Emergency load shedding.** Halts auto-optimization, safe-harbor dispatch, operator alert.

---

## Tradeoff Analysis of Key Trigger Concepts

### 1. Actual Critical Load Shortfall
- *Immediate Trigger*: Zero lag in detecting power drop, but vulnerable to 1-second telemetry blips causing unnecessary Option C load shedding.
- *Persisted Trigger*: Filters noise (e.g. 2 consecutive 15-minute intervals), but introduces a 15–30 minute software recognition lag while physical hardware relays protect buses instantly.

### 2. Imminent Survivability Exhaustion (Look-ahead Energy Balance)
- Allows POLARIS to trigger Emergency Mode *before* actual load shedding occurs when net available energy (battery + generation) cannot sustain 6 hours of critical load.
- Prevents deep battery collapse, but relies on accurate generation capacity telemetry.

### 3. Data Integrity & Telemetry Loss
- Collapsing missing telemetry (`UNKNOWN / INVALID`) into `EMERGENCY` causes catastrophic false load shedding during routine sensor maintenance.
- Strict isolation ensures safety without unneeded disruption.

---

# HUMAN GOVERNANCE DECISIONS REQUIRED

The human project owner must explicitly choose the governed policy for each of the following 5 decisions prior to trigger implementation:

### DECISION 1: Critical-Load Service Failure Trigger Semantics
Should actual critical-load service failure ($P_{\text{critical, served}} < P_{\text{critical, required}}$) be an immediate Emergency trigger or require persistence?
- **Option 1.A**: Immediate trigger on a single control interval (15 minutes).
- **Option 1.B (Recommended)**: Require governed persistence of $N \ge 2$ consecutive intervals to filter telemetry noise.
- **Option 1.C**: Other explicit rule.

### DECISION 2: Imminent Survivability Exhaustion Pre-Trigger
Should POLARIS be allowed to enter Emergency Mode BEFORE actual critical-load failure when total available controllable energy is insufficient to sustain the 6-hour requirement?
- **Option 2.A (Recommended)**: Yes; enter Emergency Mode when net available energy falls below 6-hour critical requirement.
- **Option 2.B**: No; enter Emergency Mode ONLY upon actual load service failure or physical battery exhaustion (20% SOC).
- **Option 2.C**: Create a separate `IMMINENT_EMERGENCY` state for advisory/pre-curtailment warning.
- **Option 2.D**: Other explicit rule.

### DECISION 3: Treatment of Reserve Deficit Alone
Should a reserve deficit alone ($SOC < 57.83\% / 75.65\text{ kWh}$) ever trigger Emergency Mode?
- **Option 3.A**: Yes, if deficit persists for longer than a governed duration $T_{\text{max}}$.
- **Option 3.B (Recommended)**: No; reserve deficit remains strictly in Normal/Recovery mode regardless of duration unless critical load service or survivability is threatened.
- **Option 3.C**: Only when combined with a negative SOC trajectory ($\frac{dSOC}{dt} < 0$) and zero available generation replenishment.

### DECISION 4: Resource-Loss Condition Governance
Which generation/resource loss conditions should immediately trigger Emergency Mode?
- **Option 4.A**: Complete diesel generator loss ($P_{\text{diesel, max}} = 0$) while in Reserve Deficit.
- **Option 4.B**: Loss of all dispatchable generation when battery SOC $< 57.83\%$.
- **Option 4.C (Recommended)**: Simultaneous failure of diesel AND battery SOC $< 37.83\%$, or complete loss of all power sources. (Renewable drop alone must NEVER trigger Emergency).
- **Option 4.D**: Other explicit multi-resource matrix.

### DECISION 5: Automatic Exit / Return to Normal Criteria
What observable conditions are required for ECD to declare emergency conditions cleared and automatically return to Normal Mode?
- **Option 5.A**: Critical load 100% served for $P$ intervals AND battery $SOC \ge 57.83\%$ ($75.65\text{ kWh}$) AND at least one dispatchable generator available.
- **Option 5.B**: Critical load 100% served AND battery $SOC \ge 37.83\%$ ($50.0\text{ kWh}$) with positive charging rate.
- **Option 5.C (Recommended)**: Critical load 100% served for $P \ge 4$ intervals AND net generation exceeds station load AND battery $SOC \ge 57.83\%$ (with mandatory operator notification and override capability).
