# SYNTHETIC PRODUCTION NUMERICAL AUDIT

## Package-Wide Numerical Classification Audit

This document classifies every numerical value appearing within the authorization package artifacts to prevent accidental promotion of synthetic parameters into production governance.

---

## Numerical Classification Register

| Numerical Value | Context / Field | Forensic Classification | Production Status | Usage Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **15 kW** | Heating critical load fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **10 kW** | Water critical load fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **5 kW** | Comms critical load fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **30 kW** | Total critical load fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **15 kW** | Flexible noncritical load fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **45 kW** | Total synthetic demand fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **20%** | Fixture SOC_min floor | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` (Option-D boundary is open) | Technical model floor ONLY. |
| **95%** | Fixture SOC_max upper bound | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Technical model ceiling ONLY. |
| **200 kWh** | Battery capacity fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **50 kW** | Battery max power fixture | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **10–60 kW** | Diesel generator power bounds | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **500 L, 20 L, 10 L** | Synthetic fuel test scenarios | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark fixture ONLY. |
| **72 hours** | Synthetic test horizon | `SYNTHETIC_FIXTURE` | `NOT_ESTABLISHED` | Benchmark test horizon ONLY. |
| **6.0 hours** | $T_{\text{required}}$ Survivability duration | `GOVERNANCE` | `PRODUCTION_ESTABLISHED` | Production baseline governance. |
| **50 L** | Fuel escalation example | `ILLUSTRATIVE` | `NOT_AUTHORIZED` | Illustrative example ONLY. |
| **2 cycles** | Recovery stability count | `ILLUSTRATIVE` | `NOT_AUTHORIZED` | Illustrative example ONLY. |
| **21 variables** | Formulation variable count per step | `ENGINEERING_REQUIRED` | Proposed Pre-GAP19 Model | Formulation variable count. |

---

## Audit Enforcement Summary

- **Governed Production Values**: $T_{\text{required}} = 6.0\text{ hours}$.
- **Synthetic Fixture Values**: 15 kW, 10 kW, 5 kW, 30 kW, 45 kW, 20% SOC floor, 200 kWh, 10–60 kW, 500L/20L/10L fuel, 72h.
- **Not Authorized Production Numbers**: 50 L fuel threshold, 2 solver cycles, 20% SOC production discharge boundary.
