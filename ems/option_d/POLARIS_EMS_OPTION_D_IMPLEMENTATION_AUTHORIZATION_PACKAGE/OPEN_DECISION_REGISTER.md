# OPEN DECISION REGISTER

## Unresolved Governance, Engineering, and Security Register

This document tracks all open decision items that must be resolved prior to full production deployment.

---

## Comprehensive Open Items Matrix

| Item # | Open Decision Description | Category | Impact on Pre-GAP19 Implementation | Required Resolution Authority |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Quantitative Operator Escalation Time Threshold | Governance | None (Uses log warning in pre-GAP19) | Human Governance Committee |
| **2** | Quantitative Operator Escalation Fuel Reserve Threshold | Governance | None (Uses log warning in pre-GAP19) | Human Governance Committee |
| **3** | System Recovery Clearance Policy (Auto vs Manual) | Governance | None (Uses mock flag in pre-GAP19 harness) | Human Governance Committee |
| **4** | Nuolja Station Critical Equipment Inventory & Circuit Mapping | Station Engineering | None (Uses 15/10/5 kW fixture in pre-GAP19) | Station Engineering Team |
| **5** | Real Station Dynamic Minimum Requirements $P_{i,\text{min}}(t)$ | Station Engineering | None (Uses fixture vectors in pre-GAP19) | Station Engineering Team |
| **6** | Generator Fuel Consumption Map & Minimum Load Limits | Station Engineering | None (Uses linear fixture model in pre-GAP19) | Station Engineering Team |
| **7** | Battery Thermal Degradation & Usable Capacity Limits | Station Engineering | None (Uses 200 kWh fixture model in pre-GAP19) | Station Engineering Team |
| **8** | Usable Fuel Tank Volume & Sensor Calibration | Station Engineering | None (Uses 500L/20L/10L fixture in pre-GAP19) | Station Engineering Team |
| **9** | Telemetry Freshness & Stale Data Timeout Values | Production Security | None (Uses mock freshness in pre-GAP19) | Production Security Team |
| **10** | Ingress Cryptographic Key Management & MFA Verification | Production Security | None (Disabled during synthetic testing) | Production Security Team |

---

## Resolution Workflow

Pre-GAP19 synthetic testing can proceed safely without resolving items 1–10 because all synthetic tests use isolated benchmark fixture parameters. However, **all 10 items must be formally resolved and signed off prior to real-world station deployment**.
