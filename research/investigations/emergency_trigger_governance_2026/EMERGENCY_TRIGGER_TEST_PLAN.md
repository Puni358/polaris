# POLARIS — EMERGENCY TRIGGER TEST PLAN & VERIFICATION MATRIX

## 1. Overview & Scope

This test plan defines the formal verification suite for evaluating the **POLARIS Emergency Controller Dispatcher (ECD)** state transition and emergency detection logic.

The test plan covers 15 distinct operational scenarios (Test Cases A through O). Each test case explicitly validates the state transition rules, telemetry safeguards, survivability margin calculations, and load shedding permissions established in the approved POLARIS Emergency Governance Decision Record.

---

## 2. Test Execution & Verification Matrix

### Test Case A: Normal Operating State Above Reserve Target
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 50.0\%$ ($100.0\text{ kWh}$ stored energy)
  - $P_{\text{critical, req}} = 11.6\text{ kW}$, $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $P_{\text{diesel, max}} = 30.0\text{ kW}$ (Available)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = (100.0 - 40.0) \times 0.92 + (30.0 \times 6.0) + 0 - 69.6 = 55.2 + 180.0 - 69.6 = +165.6\text{ kWh} \ge 0$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: $SOC = 50.0\% \ge 37.83\%$ ($75.65\text{ kWh}$); all load served; survivability margin positive.
- **Automatic Optimization Permitted**: `TRUE` (Full economic MILP active)
- **Operator Intervention Required**: `FALSE`

---

### Test Case B: Normal Operation Below Reserve Target (Reserve Deficit)
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 30.0\%$ ($60.0\text{ kWh}$ stored energy)
  - $P_{\text{critical, req}} = 11.6\text{ kW}$, $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $P_{\text{diesel, max}} = 30.0\text{ kW}$ (Available)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = (60.0 - 40.0) \times 0.92 + 180.0 - 69.6 = 18.4 + 180.0 - 69.6 = +128.8\text{ kWh} \ge 0$
- **Expected ECD State**: `RESERVE_DEFICIT`
- **Reason for Transition**: $SOC < 37.83\%$ ($75.65\text{ kWh}$), but survivability margin $M_{\text{surv}} \ge 0$ and critical load is 100% served. **NOT AN EMERGENCY.**
- **Automatic Optimization Permitted**: `TRUE` (Economic MILP with reserve recovery penalty active)
- **Operator Intervention Required**: `FALSE`

---

### Test Case C: Reserve Deficit with Successful Battery Recovery
- **Initial State**: `RESERVE_DEFICIT`
- **Observable Inputs**:
  - $SOC$ increases from $30.0\%$ to $40.0\%$ ($80.0\text{ kWh}$ stored energy) over consecutive intervals
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $P_{\text{diesel, max}} = 30.0\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = +147.2\text{ kWh} \ge 0$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: $SOC = 40.0\% \ge 37.83\%$ ($75.65\text{ kWh}$); battery energy restored above reserve target.
- **Automatic Optimization Permitted**: `TRUE` (Standard economic MILP resumed)
- **Operator Intervention Required**: `FALSE`

---

### Test Case D: Reserve Deficit Without Survivability Threat
- **Initial State**: `RESERVE_DEFICIT`
- **Observable Inputs**:
  - $SOC = 25.0\%$ ($50.0\text{ kWh}$ stored energy; near physical min of 20%)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $P_{\text{diesel, max}} = 25.0\text{ kW}$ (Running and serving demand)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = (50.0 - 40.0) \times 0.92 + (25.0 \times 6.0) - 69.6 = 9.2 + 150.0 - 69.6 = +89.6\text{ kWh} \ge 0$
- **Expected ECD State**: `RESERVE_DEFICIT`
- **Reason for Transition**: $SOC < 37.83\%$, but diesel generator capacity guarantees critical load service over the 6-hour horizon ($M_{\text{surv}} \ge 0$). Load shedding is prohibited.
- **Automatic Optimization Permitted**: `TRUE`
- **Operator Intervention Required**: `FALSE`

---

### Test Case E: Validated Critical-Load Service Failure
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $SOC = 50.0\%$ ($100.0\text{ kWh}$)
  - $P_{\text{critical, req}} = 11.6\text{ kW}$, $P_{\text{critical, srv}} = 8.0\text{ kW}$ (3.6 kW shortfall)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: Validated critical-load service failure ($P_{\text{crit\_srv}} < P_{\text{crit\_req}}$). **Immediate Emergency trigger; no intentional persistence delay.**
- **Automatic Optimization Permitted**: `TRUE` (Option C governed load-shedding MILP active)
- **Operator Intervention Required**: `FALSE` (Automatic transition, but operator notified)

---

### Test Case F: Imminent Survivability Failure Before Critical-Load Failure
- **Initial State**: `RESERVE_DEFICIT`
- **Observable Inputs**:
  - $SOC = 22.0\%$ ($44.0\text{ kWh}$ stored energy)
  - $P_{\text{critical, req}} = 11.6\text{ kW}$, $P_{\text{critical, srv}} = 11.6\text{ kW}$ (Currently 100% served)
  - $P_{\text{diesel, max}} = 0.0\text{ kW}$ (Diesel Generator Failed / Out of Fuel)
  - $P_{\text{ren, forecast}} = 0.0\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $E_{\text{batt, usable}} = (44.0 - 40.0) \times 0.92 = 3.68\text{ kWh delivered}$. Required = $69.6\text{ kWh}$.
  $$M_{\text{surv}} = 3.68 + 0.0 + 0.0 - 69.6 = -65.92\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: Imminent survivability failure ($M_{\text{surv}} < 0$). System cannot maintain 6-hour critical load with available resources. Emergency entered *before* actual blackout.
- **Automatic Optimization Permitted**: `TRUE` (Option C load shedding active to extend battery life)
- **Operator Intervention Required**: `FALSE` (Operator alert emitted)

---

### Test Case G: Renewable Loss While Survivability Remains Secure
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $P_{\text{solar}} = 0.0\text{ kW}, P_{\text{wind}} = 0.0\text{ kW}$ (Sudden cloud cover and calm wind)
  - $SOC = 45.0\%$ ($90.0\text{ kWh}$ stored energy)
  - $P_{\text{diesel, max}} = 30.0\text{ kW}$ (Available)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = (90.0 - 40.0) \times 0.92 + 180.0 - 69.6 = +156.4\text{ kWh} \ge 0$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: $SOC \ge 37.83\%$; diesel generator easily covers critical load. Renewable loss alone is a normal operational variation, NOT an Emergency trigger.
- **Automatic Optimization Permitted**: `TRUE` (Economic MILP dispatches diesel)
- **Operator Intervention Required**: `FALSE`

---

### Test Case H: Diesel Loss While Battery/Resources Remain Sufficient
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - $P_{\text{diesel, max}} = 0.0\text{ kW}$ (Diesel Generator tripped on fault)
  - $SOC = 80.0\%$ ($160.0\text{ kWh}$ stored energy)
  - $P_{\text{ren, forecast}} = 10.0\text{ kW}$ (High solar/wind generation)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $E_{\text{batt, usable}} = (160.0 - 40.0) \times 0.92 = 110.4\text{ kWh}$. Renewable = $0.5 \times 10.0 \times 6 = 30.0\text{ kWh}$.
  $$M_{\text{surv}} = 110.4 + 0.0 + 30.0 - 69.6 = +70.8\text{ kWh} \ge 0$$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: Battery SOC is high ($80\% \ge 37.83\%$) and renewable forecast is strong. Remaining resources guarantee critical load survivability over 6 hours ($M_{\text{surv}} \ge 0$). Diesel loss alone does NOT trigger Emergency.
- **Automatic Optimization Permitted**: `TRUE`
- **Operator Intervention Required**: `FALSE` (Maintenance alert emitted for diesel repair)

---

### Test Case I: Multiple Resource Loss Causing Survivability Failure
- **Initial State**: `RESERVE_DEFICIT`
- **Observable Inputs**:
  - $P_{\text{diesel, max}} = 0.0\text{ kW}$ (Diesel trip)
  - $SOC = 30.0\%$ ($60.0\text{ kWh}$ stored energy)
  - $P_{\text{ren, forecast}} = 0.0\text{ kW}$ (Night / Calm)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $E_{\text{batt, usable}} = (60.0 - 40.0) \times 0.92 = 18.4\text{ kWh}$.
  $$M_{\text{surv}} = 18.4 + 0.0 + 0.0 - 69.6 = -51.2\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: Simultaneous loss of diesel generation and low battery energy results in $M_{\text{surv}} < 0$. Resource-adequacy assessment establishes survivability failure.
- **Automatic Optimization Permitted**: `TRUE` (Option C load shedding active)
- **Operator Intervention Required**: `FALSE`

---

### Test Case J: Battery Unavailable with Sufficient Remaining Generation
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - Battery isolated on BMS fault (`battery_healthy = False`)
  - $P_{\text{diesel, max}} = 45.0\text{ kW}$ (Primary + secondary diesel operational)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $E_{\text{batt, usable}} = 0.0\text{ kWh}$. $E_{\text{gen}} = 45.0 \times 6.0 = 270.0\text{ kWh}$.
  $$M_{\text{surv}} = 0.0 + 270.0 + 0.0 - 69.6 = +200.4\text{ kWh} \ge 0$$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: Available diesel capacity exceeds station demand and easily guarantees 6-hour critical load service ($M_{\text{surv}} \ge 0$). Battery loss alone does NOT trigger Emergency.
- **Automatic Optimization Permitted**: `TRUE` (MILP operates in generator-only mode)
- **Operator Intervention Required**: `FALSE`

---

### Test Case K: Battery Unavailable with Insufficient Remaining Generation
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - Battery isolated on BMS fault (`battery_healthy = False`)
  - $P_{\text{diesel, max}} = 8.0\text{ kW}$ (Derated / small backup diesel only)
  - $P_{\text{critical, req}} = 11.6\text{ kW}$
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $E_{\text{gen}} = 8.0 \times 6.0 = 48.0\text{ kWh}$.
  $$M_{\text{surv}} = 0.0 + 48.0 + 0.0 - 69.6 = -21.6\text{ kWh} < 0$$
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: Battery loss combined with undersized diesel generator results in $M_{\text{surv}} < 0$. Remaining resources cannot sustain critical load.
- **Automatic Optimization Permitted**: `TRUE` (Option C load shedding curtails non-critical loads to match 8 kW diesel limit)
- **Operator Intervention Required**: `FALSE`

---

### Test Case L: UNKNOWN / INVALID Telemetry Handling
- **Initial State**: `NORMAL`
- **Observable Inputs**:
  - Telemetry timestamp age $\Delta t = 45.0\text{ seconds} > 30.0\text{ s}$ (Stale telemetry / Comm loss)
  - Sensor reports corrupt $SOC = 150.0\%$ (Out of physical bounds)
  - $\text{V}_{\text{telemetry}} = \text{INVALID}$
- **Expected ECD State**: `UNKNOWN_INVALID`
- **Reason for Transition**: Telemetry failure detected ($\text{V}_{\text{telemetry}} = \text{INVALID}$). **`UNKNOWN_INVALID != EMERGENCY`**. System MUST NOT trigger Option C load shedding on sensor error.
- **Automatic Optimization Permitted**: `FALSE` (MILP optimization suspended; safe-harbor dispatch locked)
- **Operator Intervention Required**: `TRUE` (High-priority alarm emitted; requires operator reset or data restoration)

---

### Test Case M: Emergency Exit After Successful Recovery
- **Initial State**: `EMERGENCY`
- **Observable Inputs**:
  - Diesel generator repaired and running at $35.0\text{ kW}$
  - Battery recharged to $SOC = 42.0\%$ ($84.0\text{ kWh} \ge 75.65\text{ kWh}$)
  - $P_{\text{critical, srv}} = 11.6\text{ kW}$ (100% served for $> 4$ intervals)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = (84.0 - 40.0) \times 0.92 + 210.0 - 69.6 = 40.48 + 210.0 - 69.6 = +180.88\text{ kWh} \ge +10.0$
- **Expected ECD State**: `NORMAL`
- **Reason for Transition**: All exit criteria met: emergency condition cleared, critical load 100% served, $SOC \ge 37.83\%$, $M_{\text{surv}} \ge +10.0\text{ kWh}$, diesel generator healthy.
- **Automatic Optimization Permitted**: `TRUE` (Ramp restoration of flexible loads initiated)
- **Operator Intervention Required**: `FALSE` (Automatic return with operator notification)

---

### Test Case N: Emergency Exit Attempt While Recovery Is Insufficient
- **Initial State**: `EMERGENCY`
- **Observable Inputs**:
  - Critical load $P_{\text{critical, srv}} = 11.6\text{ kW}$ (Temporarily served by solar burst)
  - $SOC = 22.0\%$ ($44.0\text{ kWh}$ stored energy)
  - $P_{\text{diesel, max}} = 0.0\text{ kW}$ (Diesel still offline)
  - $\text{V}_{\text{telemetry}} = \text{VALID}$
- **Calculated Margin**: $M_{\text{surv}} = -65.92\text{ kWh} < 0$
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: System remains in `EMERGENCY`. Critical load service during a brief solar burst is insufficient for exit because $SOC < 37.83\%$ and $M_{\text{surv}} < 0$.
- **Automatic Optimization Permitted**: `TRUE` (Option C load shedding remains active)
- **Operator Intervention Required**: `FALSE`

---

### Test Case O: Operator Manual Override During Automatic Exit Flow
- **Initial State**: `EMERGENCY`
- **Observable Inputs**:
  - Automatic exit conditions satisfied (Same as Test Case M)
  - Operator sends explicit governance lock command: `OPERATOR_OVERRIDE_HOLD_EMERGENCY = True`
- **Expected ECD State**: `EMERGENCY`
- **Reason for Transition**: Preserves `AUTOMATIC_RETURN_WITH_OPERATOR_NOTIFICATION_AND_OVERRIDE`. Manual operator override supersedes automatic exit state transition.
- **Automatic Optimization Permitted**: `TRUE` (Option C active under manual hold)
- **Operator Intervention Required**: `TRUE` (Operator explicitly holding mode)

---

## 3. Test Coverage & Traceability Summary

| Test Case | Scenario Description | Governed Decision Validated | Expected State | Auto Opt Permitted? | Operator Required? |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **A** | Normal above reserve ($SOC \ge 37.83\%$) | Target Reserve Governance | `NORMAL` | `TRUE` | `FALSE` |
| **B** | Normal below reserve ($SOC < 37.83\%$) | Decision 3 (Reserve Deficit $\neq$ Emergency) | `RESERVE_DEFICIT` | `TRUE` | `FALSE` |
| **C** | Reserve recovery above target | Reserve Target Restoration | `NORMAL` | `TRUE` | `FALSE` |
| **D** | Low SOC with active generator | Decision 3 (Survivability Secure) | `RESERVE_DEFICIT` | `TRUE` | `FALSE` |
| **E** | Critical load shortfall ($P_{\text{srv}} < P_{\text{req}}$) | Decision 1 (Immediate Failure Trigger) | `EMERGENCY` | `TRUE` | `FALSE` |
| **F** | Imminent survivability deficit ($M_{\text{surv}} < 0$) | Decision 2 (Preemptive Trigger) | `EMERGENCY` | `TRUE` | `FALSE` |
| **G** | Renewable generation drop | Decision 4 (Resource Loss Assessment) | `NORMAL` | `TRUE` | `FALSE` |
| **H** | Generator trip with high battery | Decision 4 (Resource Loss Assessment) | `NORMAL` | `TRUE` | `FALSE` |
| **I** | Generator trip + low battery | Decision 4 (Multi-Resource Failure) | `EMERGENCY` | `TRUE` | `FALSE` |
| **J** | Battery fault + high diesel | Decision 4 (Resource Loss Assessment) | `NORMAL` | `TRUE` | `FALSE` |
| **K** | Battery fault + small diesel | Decision 4 (Multi-Resource Failure) | `EMERGENCY` | `TRUE` | `FALSE` |
| **L** | Telemetry stale / out-of-bounds | Telemetry Safeguard (`UNKNOWN_INVALID`) | `UNKNOWN_INVALID` | `FALSE` | `TRUE` |
| **M** | Validated exit recovery | Decision 5 (Automatic Return Criteria) | `NORMAL` | `TRUE` | `FALSE` |
| **N** | Incomplete exit recovery | Decision 5 (Insufficient Exit Recovery) | `EMERGENCY` | `TRUE` | `FALSE` |
| **O** | Manual operator hold on exit | Decision 5 (Operator Override) | `EMERGENCY` | `TRUE` | `TRUE` |
