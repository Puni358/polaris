# POLARIS EMS — OPEN ITEMS AFTER DEC-004 SEALING

## Executive Statement

The sealing of **DEC-004: Option D — Protected Critical-Load Fallback** completes high-level policy selection. However, all concrete numerical parameters, station physical mappings, and technical integration specifications **REMAIN OPEN**.

None of these open items have been resolved by selecting Option D. They must be formally established in subsequent engineering and governance phases.

---

## 1. Open Governance & Production Parameters

| Parameter | Current Status | Description / Requirement |
| :--- | :--- | :--- |
| **Production $T_{\text{required}}$** | `OPEN` (BLK-006) | Governing survivability time horizon for station autonomy. |
| **$T_{\text{required}}$ Override TTL** | `OPEN` (BLK-006) | Maximum allowable duration for operational horizon overrides. |
| **Telemetry Maximum Age (TTL)** | `OPEN` (BLK-007) | Maximum allowable age before telemetry is flagged stale/invalid. |
| **Ingress Cryptographic Mechanism** | `OPEN` (BLK-008) | Authentication & signature validation mechanism for incoming telemetry. |
| **Option D Watchdog Duration ($T_{\text{max,degraded}}$)** | `OPEN` | Maximum time allowed in Option D degraded state before mandatory escalation. |
| **Fuel Reserve Floor ($F_{\text{reserve,min}}$)** | `OPEN` | Minimum fuel level triggering mandatory operator escalation during fallback. |

---

## 2. Open Station Engineering Inputs

| Engineering Input | Current Status | Description / Requirement |
| :--- | :--- | :--- |
| **Protected Equipment Inventory** | `OPEN` | Definitive list of essential systems required for survivability. |
| **Breaker / Circuit Mapping** | `OPEN` | Physical breaker routing connecting physical loads to control actuators. |
| **Critical Load Profile $P_{\text{critical}}(t)$** | `OPEN` | Mathematical dynamic demand model for protected systems over time. |
| **Minimum Viable Operating Levels** | `OPEN` | Minimum power thresholds required to keep protected systems operational. |
| **Generator Minimum Operating Power** | `OPEN` | Physical lower bound ($P_{\text{gen,min}}$) for diesel generator operation. |
| **Generator Fuel Consumption Curve** | `OPEN` | Non-linear or piecewise linear fuel consumption model ($L/h$ vs $kW$). |
| **Battery Charge Acceptance Limit** | `OPEN` | Maximum charging power acceptance under various SOC and thermal conditions. |
| **Battery SOC Floor & Ceiling** | `OPEN` | Governing operational bounds for battery state-of-charge during fallback. |
| **Battery Thermal & Protection Limits** | `OPEN` | Thermal boundaries and protective disconnect criteria. |
| **Telemetry Freshness Definitions** | `OPEN` | Signal-by-signal freshness windows for telemetry validity classification. |

---

## 3. Numerical Firewall (Classification of Synthetic Prototype Values)

> [!CAUTION]
> **NUMERICAL FIREWALL**: The following synthetic prototype and test fixture values exist in current unit tests, test fixtures, or research code. They are **SYNTHETIC TEST VALUES ONLY** and must **NEVER** be promoted to production Option D policy values merely because Option D has been selected.

| Prototype / Test Value | Classification | Context / Notes |
| :--- | :--- | :--- |
| **72h $T_{\text{required}}$** | `SYNTHETIC_ENGINEERING_TEST_VALUE` | Prototype value used in HD-03 synthetic research tests. |
| **2h $T_{\text{test}}$** | `SYNTHETIC_ECD_LOGIC_VALIDATION` | Test horizon for ECD unit tests. |
| **30 kW Critical Load** | `SYNTHETIC_PROTOTYPE_VALUE` | Illustrative constant load in research memos. |
| **80% / 30% SOC Limits** | `SYNTHETIC_TEST_FIXTURE_VALUE` | Initial test bounds in synthetic fixtures. |
| **50L / 12.5L / 46L Fuel** | `SYNTHETIC_TEST_FIXTURE_VALUE` | Synthetic fuel tank capacities in test cases. |
| **10 kW Generator Minimum** | `PROTOTYPE_MODEL_VALUE` | Minimum load setting in initial model prototype. |
| **5 L/h Base Fuel Rate** | `PROTOTYPE_MODEL_VALUE` | Zero-load fuel consumption prototype estimate. |
| **0.25 L/kWh Marginal Fuel** | `PROTOTYPE_MODEL_VALUE` | Incremental fuel slope prototype estimate. |

---

## Summary

No values have been silently assumed or derived in this task. All 18 items listed above remain open for future authorized governance and engineering tasks.
