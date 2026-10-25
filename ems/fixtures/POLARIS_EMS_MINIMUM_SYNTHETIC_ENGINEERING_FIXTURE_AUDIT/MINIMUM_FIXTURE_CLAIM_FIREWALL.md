# POLARIS EMS — MINIMUM FIXTURE CLAIM FIREWALL AUDIT

## Executive Summary

This document specifies the master **Scientific and Performance Claim Firewall Matrix** for the minimum synthetic engineering fixture.

---

## Master Claim Boundary Matrix

| Result / Outcome Category | May Claim (Valid Technical Assertion) | Must NOT Claim (Forbidden Prohibited Claim) |
| :--- | :--- | :--- |
| **Architecture Execution** | Software architecture pipeline executes end-to-end under synthetic fixture. | POLARIS software is validated or ready for real Nuolja station deployment. |
| **ECD Risk Classification** | ECD logic correctly classifies `NORMAL`/`EMERGENCY`/`UNKNOWN_INVALID` for fixture inputs. | Real Nuolja station emergency frequency or risk probability. |
| **Option D Fallback** | Safe-state fallback policy executes correctly under Scenario 5 synthetic inputs. | Real Nuolja station emergency survivability or freeze protection guarantee. |
| **Battery Dynamics** | Synthetic BESS model correctly enforces SOC bounds and charge/discharge efficiency. | Real Nuolja battery capacity adequacy or battery health longevity. |
| **Diesel Generator** | Synthetic generator model correctly enforces minimum output and fuel consumption rate. | Real Nuolja generator fuel efficiency or physical engine performance. |
| **Fuel Consumption** | Synthetic fuel depletion accounting functions correctly in closed-loop simulation. | Real Nuolja station annual fuel savings or economic benefits. |
| **Critical Load Policy** | Synthetic 2-tier load model correctly sheds noncritical load during Option D. | Real Nuolja station critical load profile or building heat loss specification. |
| **Forecast Integration** | `ForecastBundle` schema v1.0.0 ingestion and horizon checks function correctly. | Real-world meteorological forecast accuracy or NWP model skill at Nuolja. |
| **Simulation Replay** | Receding-horizon MPC control loop completes 24 closed-loop iterations deterministically. | Real Nuolja annual microgrid performance or operational readiness. |

---

## Summary Statement

```yaml
CLAIM_FIREWALL_STATUS: PASS
MANDATE: Every synthetic fixture result MUST cite this matrix and include explicit provenance metadata (`station_identity: NONE`).
```
