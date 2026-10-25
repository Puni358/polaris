# POLARIS EMS GAP19 — CRITICAL LOAD EVIDENCE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Focus**: **CRITICAL LOAD TRAJECTORY ($P_{\text{critical}}(t)$) PROVENANCE**  

---

## 1. Disambiguation of Critical Load Concepts

To prevent improper promotion of test artifacts, four distinct critical load concepts are audited separately:

```text
1. CONCEPTUAL_PROTECTED_CATEGORY
   (Sealed policy definition: Heating, Water, Comms under DEC-004 D1)
        │
        ▼
2. ACTUAL_STATION_EQUIPMENT
   (Specific physical equipment nameplates at Nuolja station)
        │
        ▼
3. ACTUAL_CIRCUIT_POWER
   (Measured wattage per sub-circuit panel)
        │
        ▼
4. DYNAMIC_POWER_PROFILE
   (High-resolution time-indexed power vector P_critical(t))
```

---

## 2. Granular Audit Matrix

| Critical Load Layer | Current State in POLARIS | Evidence Classification | Status & Notes |
| :--- | :--- | :--- | :--- |
| **`CONCEPTUAL_PROTECTED_CATEGORY`** | Essential Heating, Water Treatment, Emergency Communications. | `GOVERNANCE_VALUE` | **SEALED** under DEC-004 D1 policy resolution. |
| **`ACTUAL_STATION_EQUIPMENT`** | Specific equipment inventory at Nuolja station. | `NOT_ESTABLISHED` | **ZERO** single-line electrical diagrams or nameplate reports found. |
| **`ACTUAL_CIRCUIT_POWER`** | Sub-circuit breaker panel wattage breakdown. | `NOT_ESTABLISHED` | **ZERO** sub-metered circuit telemetry datasets received. |
| **`DYNAMIC_POWER_PROFILE`** | Continuous 24h/48h $P_{\text{critical}}(t)$ time-series. | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Scenario JSON files (`demo_scenario.json`, etc.) use synthetic arrays ($30\text{ kW}$ baseline / ratio scaling). |

---

## 3. Rejection of Synthetic $30\text{ kW}$ Value

* **Prototype Value**: $30,000.0\text{ W}$ ($30\text{ kW}$) or ratio-scaled vectors ($0.5 \times P_{\text{demand}}$) used in test scenarios.
* **Audit Verdict**: This $30\text{ kW}$ value is a **`SYNTHETIC_ENGINEERING_ASSUMPTION`** created for deterministic software integration testing.
* **Firewall Requirement**: It **MUST NOT** be used as real-station evidence, nor treated as the production critical load for Nuolja station.
