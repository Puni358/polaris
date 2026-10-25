# POLARIS EMS — DEC-004 15 FAILURE SCENARIO TRACE ANALYSIS

## 1. Executive Summary

This document traces Candidate Options **A**, **B**, **C**, and **D** across 15 operational failure scenarios. For each scenario, the table factually distinguishes **Policy Behavior**, **Established Runtime Capability**, and **Missing Implementation Required**.

---

## 2. 15 Failure Scenarios Trace Table

| # | Operational Failure Scenario | Option A: Hold Last Plan | Option B: Zero Dispatch | Option C: Operator Intervention | Option D: Protected Critical Fallback |
|---|------------------------------|--------------------------|-------------------------|---------------------------------|--------------------------------------|
| **1** | **UNKNOWN_INVALID for 1 MPC Cycle** | Re-applies $t_{k-1}$ plan setpoints. <br>*Runtime*: Requires plan cache. <br>*Missing*: Cache in `runner.py`. | Solves 0-power dispatch ($P=0$). <br>*Runtime*: Established in D4-C0. <br>*Missing*: Runner adapter wiring. | Halts pipeline (`CRITICAL_TERMINATION`). <br>*Runtime*: Established in runner. <br>*Missing*: Runner adapter wiring. | Sheds noncritical load; powers critical load. <br>*Runtime*: Conceptual policy. <br>*Missing*: Policy router & load shedder. |
| **2** | **UNKNOWN_INVALID Persists for Several Cycles** | Re-applies $t_{k-1}$ plan until hold limit expiry. <br>*Missing*: Watchdog timer logic. | Advances state at 0 power for each cycle. <br>*Runtime*: Native in simulator. | Remains locked in `FAILED_TERMINATED`. <br>*Runtime*: Native in runner. | Continues critical-only dispatch for each cycle. <br>*Missing*: Policy router loop. |
| **3** | **Renewable Available but Insufficient for Critical Load** | Dispatches $t_{k-1}$ plan battery/diesel setpoints. | Directs uncurtailed renewables to load; 0 dispatch. | Automated MPC halted. | Applies renewables to critical load; dispatches diesel for remainder. |
| **4** | **Renewable Generation Zero** | Dispatches $t_{k-1}$ plan battery/diesel setpoints. | Enforces $P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$. | Automated MPC halted. | Dispatches diesel generator; uses battery as fallback under D3. |
| **5** | **Diesel Available** | Dispatches $t_{k-1}$ diesel setpoint. | $P_{\text{diesel}} = 0$. | Automated MPC halted. | Dispatches diesel for remaining critical demand ($P_{\text{D}} \ge P_{\text{D,min}}$). |
| **6** | **Diesel Unavailable / Faulted** | Dispatches $t_{k-1}$ battery setpoint. | $P_{\text{diesel}} = 0$. | Automated MPC halted. | Dispatches renewables + battery fallback to maintain critical load under D3. |
| **7** | **Battery Has Usable Energy** | Dispatches $t_{k-1}$ battery setpoint. | $P_{\text{dis}} = 0$. | Automated MPC halted. | Discharges battery for critical load under D2/D3 when generation is deficient. |
| **8** | **Battery Reaches Governed Discharge Boundary ($SOC_{\text{min}}$)** | Dispatches $t_{k-1}$ battery setpoint (risks over-discharge). | $P_{\text{dis}} = 0$. | Automated MPC halted. | Aborts battery discharge under D2; escalates to operator under D5. |
| **9** | **Available Power Insufficient for All Minimum Critical Levels** | Executes fixed $t_{k-1}$ setpoint. | Total load shed. | Automated MPC halted. | Proportionally allocates power across critical systems; escalates immediately (D4). |
| **10** | **Diesel Min Output Creates Excess Power** | Executes $t_{k-1}$ plan setpoint. | $P_{\text{diesel}} = 0$. | Automated MPC halted. | Charges battery with excess power ($P_{\text{BC}}$); curtails remaining excess (D6). |
| **11** | **Battery Cannot Accept Additional Charging Power** | Executes $t_{k-1}$ plan setpoint. | $P_{\text{chg}} = 0$. | Automated MPC halted. | Caps battery charge ($P_{\text{BC}} = P_{\text{BC,max}}$); curtails remaining excess ($P_{\text{curtail}}$). |
| **12** | **Operator Has Not Responded Yet** | Continues hold plan until horizon expiry. | Remains in 0-dispatch state. | Remains locked in `FAILED_TERMINATED`. | Continues critical fallback; escalates at D5 boundary. |
| **13** | **ECD Becomes Valid Again** | Resumes normal 24h MILP optimization. <br>*Missing*: Cache clear logic. | Resumes normal 24h MILP optimization. <br>*Runtime*: Native in runner. | Requires manual SCADA reset to restart pipeline. | Resumes normal 24h MILP optimization; re-engages noncritical loads. |
| **14** | **Critical-Load Requirement $P_{\text{critical}}(t)$ Increases Dynamically** | Fixed $t_{k-1}$ setpoints cannot adapt. | 0 dispatch (unaffected). | Automated MPC halted. | Dynamically increases generation/discharge dispatch to match $P_{\text{critical}}(t)$ (D1). |
| **15** | **Invalid Telemetry Hits D5 Time/Resource Boundary** | Escalates to Option C upon plan expiry. | Remains in 0-power state. | Already in terminal state. | Triggers mandatory D5 operator escalation via SCADA alarm and `FaultEvent`. |

Status: `SCENARIO_ANALYSIS_SEALED`
