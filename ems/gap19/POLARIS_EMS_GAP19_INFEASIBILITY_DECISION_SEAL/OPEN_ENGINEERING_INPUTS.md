# POLARIS EMS GAP19 — OPEN ENGINEERING INPUTS

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Classification**: `DEFERRED_ENGINEERING_INPUTS`  

---

## 1. Executive Summary

This document formally records the itemized list of 10 open engineering questions (**ENG-01 through ENG-10**). In compliance with governance instructions, these items are explicitly identified as missing engineering inputs and are **NOT answered by invention**.

---

## 2. Register of Open Engineering Questions

| Ref ID | Open Engineering Question | What Is Required Before Implementation | Current Status |
| :--- | :--- | :--- | :---: |
| **ENG-01** | How is the governed maximum $J2$ reserve-shortfall bound numerically derived from actual station survivability requirements? | Mathematical derivation connecting station $T_{\text{required}}$ to $s_{\text{J2,max}}$. | `NOT_ESTABLISHED` |
| **ENG-02** | What station engineering data are required to calculate the reserve requirement? | Site-specific load profiles, battery degradation curves, and seasonal weather limits. | `NOT_ESTABLISHED` |
| **ENG-03** | What is the exact runtime interface between optimizer infeasibility, ECD, and the emergency policy layer? | Python API class interfaces and event-bus message schemas connecting `runner.py`, `gap19_highs_native.py`, and `ecd.py`. | `NOT_ESTABLISHED` |
| **ENG-04** | What `DispatchPlan` / runtime representation is required for emergency fallback? | Schema definitions for Option D emergency dispatch plans ($P_{\text{critical}}$, circuit flags). | `NOT_ESTABLISHED` |
| **ENG-05** | What concrete authority-escalation interface is required? | Transport protocols (REST/MQTT/SMS), authentication schemas, and operator IDs. | `NOT_ESTABLISHED` |
| **ENG-06** | What should happen if ECD input itself is `UNKNOWN_INVALID`? | Governance rules for telemetry loss, stale data watchdogs, and DEC-004 fallback invocation. | `NOT_ESTABLISHED` |
| **ENG-07** | What are the exact authenticated/fresh operational inputs required for ECD in deployment? | Telemetry fresh-data TTLs, cryptographic signature validation, and sensor bounds. | `NOT_ESTABLISHED` |
| **ENG-08** | What station-specific protected-critical-load mapping is required? | Circuit-by-circuit electrical mapping of critical equipment at Nuolja station. | `NOT_ESTABLISHED` |
| **ENG-09** | What generator minimum-output / fuel-curve information is required? | Certified diesel fuel consumption curves ($L/\text{h}$ vs $\text{kW}$) and startup limits. | `NOT_ESTABLISHED` |
| **ENG-10** | What battery discharge/charge acceptance and emergency boundary inputs are required? | Temperature-dependent charge acceptance limits and emergency SOC trip floors. | `NOT_ESTABLISHED` |

---

## 3. Boundary Statement

None of these 10 engineering questions are answered or inferred by the AI assistant. They remain open engineering dependencies for future implementation gates.
