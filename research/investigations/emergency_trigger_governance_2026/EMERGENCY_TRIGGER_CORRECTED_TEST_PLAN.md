# POLARIS — EMERGENCY TRIGGER CORRECTED TEST PLAN (A–U)

## 1. Overview & Mathematical Reconciliation Scope

This document presents the **Corrected Verification Test Suite (Test Cases A through U)**. 

Every test calculation has been recalculated under the dimensionally consistent deliverable energy formulation:

$$E_{\text{batt\_deliverable}}(SOC) = \max\left(0, \, (SOC - 0.20) \times 200.0\text{ kWh} \times 0.92\right) \quad [\text{kWh delivered to bus}]$$

$$E_{\text{critical\_required}} = 11.6\text{ kW} \times 6.0\text{ h} = 69.60\text{ kWh delivered}$$

$$M_{\text{surv}}(t) = E_{\text{batt\_deliverable}}(t) + E_{\text{gen\_bus}}(t, 6\text{h}) + E_{\text{ren\_bus}}(t, 6\text{h}) - 69.60\text{ kWh}$$

---

## 2. Recalculated Test Suite (Test Cases A through O)

### Test Case A: Normal Operating State Above Reserve Target
- **Inputs**: $SOC = 50.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$, $P_{\text{diesel}} = 30.0\text{ kW}$, $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Old Calculation**: $M_{\text{surv}} = 55.2 + 180.0 - 69.6 = +165.6\text{ kWh}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.50 - 0.20) \times 200 \times 0.92 = 55.20\text{ kWh delivered}$
  - $E_{\text{gen\_bus}} = 30.0 \times 6.0 = 180.0\text{ kWh delivered}$
  - $M_{\text{surv}} = 55.20 + 180.00 - 69.60 = +165.60\text{ kWh} \ge 0$
- **Expected State**: `NORMAL` (Unchanged). $SOC \ge 37.83\%$, all loads served, $M_{\text{surv}} \ge 0$.

---

### Test Case B: Normal Operation Below Reserve Target (Reserve Deficit)
- **Inputs**: $SOC = 30.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$, $P_{\text{diesel}} = 30.0\text{ kW}$, $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Old Calculation**: $M_{\text{surv}} = 18.4 + 180.0 - 69.6 = +128.8\text{ kWh}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.30 - 0.20) \times 200 \times 0.92 = 18.40\text{ kWh delivered}$
  - $E_{\text{gen\_bus}} = 180.00\text{ kWh delivered}$
  - $M_{\text{surv}} = 18.40 + 180.00 - 69.60 = +128.80\text{ kWh} \ge 0$
- **Expected State**: `RESERVE_DEFICIT` (Unchanged). $SOC < 37.83\%$, but diesel generator guarantees survivability. **NOT AN EMERGENCY.**

---

### Test Case C: Reserve Deficit with Successful Battery Recovery
- **Inputs**: $SOC$ increases from $30.0\%$ to $40.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$, $P_{\text{diesel}} = 30.0\text{ kW}$
- **Corrected Calculation**: $E_{\text{batt\_deliverable}} = (0.40 - 0.20) \times 200 \times 0.92 = 36.80\text{ kWh delivered}$.
  - $M_{\text{surv}} = 36.80 + 180.00 - 69.60 = +147.20\text{ kWh} \ge 0$
- **Expected State**: `NORMAL` (Unchanged). $SOC = 40.0\% \ge 37.83\%$; reserve restored.

---

### Test Case D: Reserve Deficit Without Survivability Threat
- **Inputs**: $SOC = 25.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$, $P_{\text{diesel}} = 25.0\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.25 - 0.20) \times 200 \times 0.92 = 9.20\text{ kWh delivered}$
  - $E_{\text{gen\_bus}} = 25.0 \times 6.0 = 150.00\text{ kWh delivered}$
  - $M_{\text{surv}} = 9.20 + 150.00 - 69.60 = +89.60\text{ kWh} \ge 0$
- **Expected State**: `RESERVE_DEFICIT` (Unchanged). $SOC < 37.83\%$, but $M_{\text{surv}} \ge 0$. Load shedding prohibited.

---

### Test Case E: Validated Critical-Load Service Failure
- **Inputs**: $SOC = 50.0\%$, $P_{\text{crit\_req}} = 11.6\text{ kW}$, $P_{\text{crit\_srv}} = 8.0\text{ kW}$ (Shortfall), $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Expected State**: `EMERGENCY` (Unchanged). Immediate trigger on confirmed load failure.

---

### Test Case F: Imminent Survivability Failure Before Critical-Load Failure
- **Inputs**: $SOC = 22.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$, $P_{\text{diesel}} = 0.0\text{ kW}$ (Diesel Fault), $P_{\text{ren}} = 0.0\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.22 - 0.20) \times 200 \times 0.92 = 3.68\text{ kWh delivered}$
  - $M_{\text{surv}} = 3.68 + 0.0 + 0.0 - 69.60 = -65.92\text{ kWh} < 0$
- **Expected State**: `EMERGENCY` (Unchanged). Preemptive trigger before blackout.

---

### Test Case G: Renewable Loss While Survivability Remains Secure
- **Inputs**: $P_{\text{solar}} = 0, P_{\text{wind}} = 0$, $SOC = 45.0\%$, $P_{\text{diesel}} = 30.0\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.45 - 0.20) \times 200 \times 0.92 = 46.00\text{ kWh delivered}$
  - $M_{\text{surv}} = 46.00 + 180.00 - 69.60 = +156.40\text{ kWh} \ge 0$
- **Expected State**: `NORMAL` (Unchanged).

---

### Test Case H: Diesel Loss While Battery/Resources Remain Sufficient
- **Inputs**: $P_{\text{diesel}} = 0.0\text{ kW}$, $SOC = 80.0\%$, $P_{\text{ren\_forecast}} = 10.0\text{ kW}$ ($30.0\text{ kWh}$ bus energy)
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.80 - 0.20) \times 200 \times 0.92 = 110.40\text{ kWh delivered}$
  - $M_{\text{surv}} = 110.40 + 0.0 + 30.00 - 69.60 = +70.80\text{ kWh} \ge 0$
- **Expected State**: `NORMAL` (Unchanged). High battery + renewables guarantee 6h survivability.

---

### Test Case I: Multiple Resource Loss Causing Survivability Failure
- **Inputs**: $P_{\text{diesel}} = 0.0\text{ kW}$, $SOC = 30.0\%$, $P_{\text{ren\_forecast}} = 0.0\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.30 - 0.20) \times 200 \times 0.92 = 18.40\text{ kWh delivered}$
  - $M_{\text{surv}} = 18.40 + 0.0 + 0.0 - 69.60 = -51.20\text{ kWh} < 0$
- **Expected State**: `EMERGENCY` (Unchanged).

---

### Test Case J: Battery Unavailable with Sufficient Remaining Generation
- **Inputs**: `battery_healthy = False`, $P_{\text{diesel}} = 45.0\text{ kW}$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = 0.0\text{ kWh}$
  - $E_{\text{gen\_bus}} = 45.0 \times 6.0 = 270.0\text{ kWh delivered}$
  - $M_{\text{surv}} = 0.0 + 270.0 - 69.60 = +200.40\text{ kWh} \ge 0$
- **Expected State**: `NORMAL` (Unchanged).

---

### Test Case K: Battery Unavailable with Insufficient Remaining Generation
- **Inputs**: `battery_healthy = False`, $P_{\text{diesel}} = 8.0\text{ kW}$, $P_{\text{crit\_req}} = 11.6\text{ kW}$
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = 0.0\text{ kWh}$
  - $E_{\text{gen\_bus}} = 8.0 \times 6.0 = 48.0\text{ kWh delivered}$
  - $M_{\text{surv}} = 0.0 + 48.0 - 69.60 = -21.60\text{ kWh} < 0$
- **Expected State**: `EMERGENCY` (Unchanged).

---

### Test Case L: UNKNOWN / INVALID Telemetry Handling
- **Inputs**: $\Delta t = 45.0\text{ s} > 30.0\text{ s}$ ($\text{V}_{\text{telemetry}} = \text{INVALID}$)
- **Expected State**: `UNKNOWN_INVALID` (Unchanged). **`UNKNOWN_INVALID != EMERGENCY`**.

---

### Test Case M: Emergency Exit After Successful Recovery
- **Inputs**: Diesel running at $35.0\text{ kW}$, $SOC = 42.0\%$, $P_{\text{crit\_srv}} = 11.6\text{ kW}$ ($> 4$ intervals)
- **Corrected Calculation**:
  - $E_{\text{batt\_deliverable}} = (0.42 - 0.20) \times 200 \times 0.92 = 40.48\text{ kWh delivered}$
  - $M_{\text{surv}} = 40.48 + 210.00 - 69.60 = +180.88\text{ kWh} \ge +10.0\text{ kWh}$
- **Expected State**: `NORMAL` (Unchanged).

---

### Test Case N: Emergency Exit Attempt While Recovery Is Insufficient
- **Inputs**: Solar burst ($P_{\text{crit\_srv}} = 11.6\text{ kW}$), $SOC = 22.0\%$, $P_{\text{diesel}} = 0.0\text{ kW}$
- **Corrected Calculation**: $M_{\text{surv}} = 3.68 + 0.0 - 69.60 = -65.92\text{ kWh} < 0$
- **Expected State**: `EMERGENCY` (Unchanged).

---

### Test Case O: Operator Manual Override During Exit Flow
- **Inputs**: Exit criteria met, `OPERATOR_OVERRIDE_HOLD_EMERGENCY = True`
- **Expected State**: `EMERGENCY` (Unchanged).

---

## 3. Mandatory Edge Case Tests (P through U)

### Test Case P: Standalone Battery at Reserve Target Without Generation
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 37.83\%$ ($75.652\text{ kWh}$ total stored energy)
  - $P_{\text{diesel}} = 0.0\text{ kW}$ (Diesel unavailable)
  - $P_{\text{ren}} = 0.0\text{ kW}$ (Renewables unavailable)
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$ (Currently served)
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = (0.37826 - 0.2000) \times 200.0 \times 0.92 = 32.80\text{ kWh delivered}$$
  $$M_{\text{surv}} = 32.80 + 0.0 + 0.0 - 69.60 = -36.80\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Governance Semantics Demonstrated**: The $37.83\%\text{ SOC}$ reserve target is a Normal-mode target, NOT a standalone 6-hour battery guarantee above physical min. Without generation, battery at 37.83% delivers only 32.80 kWh ($2.83\text{ hours}$ autonomy). Therefore, system correctly enters Emergency Mode due to $M_{\text{surv}} < 0$. This does NOT mean 37.83% causes Emergency; it means resource-adequacy fails without generation.

---

### Test Case Q: Standalone Battery at Historical 57.83% SOC Point
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 57.83\%$ ($115.652\text{ kWh}$ total stored energy)
  - $P_{\text{diesel}} = 0.0\text{ kW}$
  - $P_{\text{ren}} = 0.0\text{ kW}$
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = (0.57826 - 0.2000) \times 200.0 \times 0.92 = 69.60\text{ kWh delivered}$$
  $$M_{\text{surv}} = 69.60 + 0.0 + 0.0 - 69.60 = 0.00\text{ kWh} \ge 0$$
- **Expected ECD State**: `NORMAL`
- **Governance Semantics Demonstrated**: Explains why $57.83\%\text{ SOC}$ appeared historically. At 57.83%, battery alone delivers exactly $69.60\text{ kWh}$ above 20% min SOC ($6.0\text{ hours}$ autonomy). However, 57.83% is NOT an Emergency threshold in POLARIS because diesel and renewables provide additional energy.

---

### Test Case R: Deficit SOC with Sufficient Continuous Generation
- **Initial State**: `RESERVE_DEFICIT`
- **Observable Inputs**:
  - $SOC = 30.0\%$ ($60.0\text{ kWh}$ stored energy)
  - $P_{\text{diesel}} = 30.0\text{ kW}$ (Available and running)
  - $P_{\text{ren}} = 0.0\text{ kW}$
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = 18.40\text{ kWh delivered}$$
  $$E_{\text{gen\_bus}} = 30.0 \times 6.0 = 180.00\text{ kWh delivered}$$
  $$M_{\text{surv}} = 18.40 + 180.00 - 69.60 = +128.80\text{ kWh} \ge 0$$
- **Expected ECD State**: `RESERVE_DEFICIT` (NOT Emergency).
- **Governance Semantics Demonstrated**: Proves Decision 3: Reserve deficit alone ($SOC < 37.83\%$) NEVER triggers Emergency when continuous generator capacity guarantees survivability.

---

### Test Case S: Medium SOC Without Diesel Generator
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 50.0\%$ ($100.0\text{ kWh}$ stored energy)
  - $P_{\text{diesel}} = 0.0\text{ kW}$ (Diesel trip)
  - $P_{\text{ren}} = 0.0\text{ kW}$
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = (0.50 - 0.20) \times 200.0 \times 0.92 = 55.20\text{ kWh delivered}$$
  $$M_{\text{surv}} = 55.20 + 0.0 - 69.60 = -14.40\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Governance Semantics Demonstrated**: Demonstrates that even at $50.0\%\text{ SOC}$ (well above reserve target), battery energy alone ($55.20\text{ kWh}$ delivered / $4.76\text{ h}$ autonomy) cannot sustain 6 hours without generation. Resource-adequacy assessment correctly triggers Emergency.

---

### Test Case T: Medium SOC with High Credible Renewable Forecast
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 50.0\%$ ($100.0\text{ kWh}$ stored energy)
  - $P_{\text{diesel}} = 0.0\text{ kW}$ (Diesel trip)
  - $P_{\text{ren\_forecast}} = 6.67\text{ kW}$ average ($40.0\text{ kWh}$ forecast energy over 6h; derated by 50% = $20.0\text{ kWh}$ credible bus energy)
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = 55.20\text{ kWh delivered}$$
  $$E_{\text{ren\_bus}} = 20.00\text{ kWh delivered}$$
  $$M_{\text{surv}} = 55.20 + 0.0 + 20.00 - 69.60 = +5.60\text{ kWh} \ge 0$$
- **Expected ECD State**: `NORMAL` (NOT Emergency).
- **Governance Semantics Demonstrated**: Demonstrates how credible renewable generation combined with medium battery SOC maintains positive survivability margin $M_{\text{surv}} \ge 0$, preventing unneeded Emergency load shedding.

---

### Test Case U: Current Critical Service Intact But Imminent Survivability Failure
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 37.83\%$ ($75.652\text{ kWh}$ stored energy)
  - $P_{\text{diesel}} = 0.0\text{ kW}$ (Diesel fault)
  - $P_{\text{ren}} = 0.0\text{ kW}$
  - $P_{\text{crit\_srv}} = 11.6\text{ kW}$ (Currently 100% served at instant $t$)
- **Calculated Deliverable Energy**:
  $$E_{\text{batt\_deliverable}} = 32.80\text{ kWh delivered}$$
  $$M_{\text{surv}} = 32.80 + 0.0 + 0.0 - 69.60 = -36.80\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Governance Semantics Demonstrated**: Highlights the vital distinction between **Current Load Service** (100% served right now) and **Future 6-Hour Survivability** ($M_{\text{surv}} < 0$). POLARIS correctly enters Emergency Mode to initiate Option C load shedding before battery reaches 20% SOC collapse.
