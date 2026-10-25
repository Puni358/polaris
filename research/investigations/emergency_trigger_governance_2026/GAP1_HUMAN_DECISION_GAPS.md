# POLARIS — GAP 1 UNRESOLVED HUMAN DECISION ITEMS

## Executive Decision Briefing

This document summarizes the **four unresolved technical choices** identified during the formalization audit of provisional decisions G1 through G6.

All options are framed in strictly neutral language. No option is described as "best", "safest", "optimal", "preferred", "correct", or "winner".

---

### ITEM 1.1: Generator Capacity Capping Policy (Model D Alignment)
- **Question**: Shall generator energy credited toward the 6-hour critical load survivability margin ($M_{\text{surv}}$) be capped at the net critical load energy requirement ($69.60\text{ kWh}$ max), or allowed to include unserved nameplate potential capacity ($600.0\text{ kWh}$ for a $100\text{ kW}$ generator)?
- **Option A (Demand Capped)**: $E_{\text{gen\_credit}} = \min\left(\int P_{\text{gen}} dt, \, \max(0, 69.60 - E_{\text{batt\_deliverable}})\right)$. Caps credit at net critical energy demand.
- **Option B (Uncapped Potential)**: $E_{\text{gen\_credit}} = \int_0^6 P_{\text{gen}} dt$. Credits total potential generator output regardless of critical demand.
- **Consequences**:
  - *Option A*: Matches exact dimensional bus balance; prevents unserved generator capacity from masking low battery SOC.
  - *Option B*: Provides higher numerical margin $M_{\text{surv}}$; reduces early Emergency triggers.

---

### ITEM 1.2: Definition of "Dispatchable" for OFF Generators
- **Question**: Under G1, does the requirement that a generator be "dispatchable" require the generator to be currently running and synchronized ($u(t_0)=1$), or does it include OFF units ($u(t_0)=0$) whose start-readiness is validated?
- **Option A (Running Only)**: "Dispatchable" applies ONLY to currently running generators. OFF generators receive $0.0\text{ kWh}$ safety credit.
- **Option B (Start-Ready Included)**: "Dispatchable" includes OFF generators if start-readiness telemetry is validated, crediting power after startup delay $\Delta t_{\text{startup}}$ (G3 alignment).
- **Consequences**:
  - *Option A*: Maximum fail-safe protection; ignores standby generators until actually running.
  - *Option B*: Credits standby generators; requires validated start-readiness telemetry.

---

### ITEM 1.3: Telemetry Freshness Threshold ($\Delta t_{\text{max}}$)
- **Question**: What numerical maximum age ($\Delta t_{\text{max}}$) shall be enforced before telemetry is marked `INVALID` under G6?
- **Option A**: $\Delta t_{\text{max}} = 30.0\text{ seconds}$ (Strict real-time threshold).
- **Option B**: $\Delta t_{\text{max}} = 300.0\text{ seconds}$ (5 minutes; accommodates satellite comm jitter).
- **Option C**: $\Delta t_{\text{max}} = 900.0\text{ seconds}$ (15 minutes; matches 1 control interval).
- **Consequences**:
  - *Option A*: High sensitivity to comm blips; transitions to `UNKNOWN_INVALID` quickly on packet loss.
  - *Option B/C*: Absorbs telemetry jitter; relies on older data during short outages.

---

### ITEM 1.4: Policy Confirmation on Telemetry Loss at Medium SOC
- **Question**: Does the human project owner confirm that if generator health telemetry becomes `UNKNOWN` while battery $SOC = 50.0\%$ (giving $55.20\text{ kWh}$ deliverable energy vs $69.60\text{ kWh}$ requirement) and renewables $= 0.0$, the system SHALL transition to `EMERGENCY` mode due to $M_{\text{surv}} = -14.40\text{ kWh} < 0$?
- **Option A (Confirm Standard Execution)**: Confirm that $M_{\text{surv}} < 0$ triggers Emergency Mode as designed.
- **Option B (Introduce Medium SOC Fallback)**: Create an exception rule holding the system in `RESERVE_DEFICIT` if battery $SOC \ge 50.0\%$ even when generator health is unknown.
- **Consequences**:
  - *Option A*: Obeyes strict survivability math ($M_{\text{surv}} < 0 \implies \text{EMERGENCY}$).
  - *Option B*: Prevents Emergency load shedding at $50\%$ SOC; introduces an exception to the survivability margin formula.
