# POLARIS EMS GAP19 — OPEN ENGINEERING INPUTS

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `DEFERRED_ENGINEERING_INPUTS`  

---

## 1. Overview

This document itemizes the station-specific engineering parameters and data inputs required before runtime code implementation of Option D fallback dispatch or MILP infeasibility routing can proceed.

---

## 2. Register of Deferred Engineering & Station Inputs

| Ref ID | Input Name | Required Engineering Content / Schema Definition | Current Status |
| :--- | :--- | :--- | :---: |
| **ENG-INP-01** | **Protected Critical Circuit Inventory** | List of protected electrical circuits at Nuolja station (Heating, Water, Comms, Telemetry) mapped to load channels. | **MISSING** |
| **ENG-INP-02** | **Dynamic Critical Load Trajectory $P_{\text{critical}}(t)$** | Mathematical function or schema vector defining minimum critical power requirements over 24h. | **MISSING** |
| **ENG-INP-03** | **D4 Proportional Allocation Ratios ($P_{i,\min}$)** | Minimum viable operating threshold $P_{i,\min}$ per protected circuit for proportional sharing under power deficit. | **MISSING** |
| **ENG-INP-04** | **Production Telemetry TTL & Max Age** | Cryptographic authentication TTL and maximum age thresholds for telemetry data freshness. | **MISSING** |
| **ENG-INP-05** | **Degraded Watchdog Duration ($T_{\text{max,degraded}}$)** | Maximum time station may operate in degraded/emergency mode before requiring hard lockout or manual reset. | **MISSING** |
| **ENG-INP-06** | **Fuel Reserve Escalation Floor ($F_{\text{reserve,min}}$)** | Minimum fuel volume threshold triggering emergency escalation to site operators. | **MISSING** |
| **ENG-INP-07** | **Option D Implementation Authorization** | Explicit human governance gate authorizing source code edits to `runner.py`, `gap19_highs_native.py`, and `ecd.py`. | **NOT GRANTED** |

---

## 3. Implementation Boundary Statement

**CODE EDITS REMAIN BLOCKED**: Until human governance grants explicit implementation authorization and provides station engineering parameters, zero source code, schema, or configuration modifications will be performed.
