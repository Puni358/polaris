# POLARIS EMS — MINIMUM FIXTURE DIESEL MODEL

## 1. Executive Summary

This document specifies the minimum synthetic diesel generator model.

---

## 2. Diesel Generator Parameters

- **Power Output Bounds ($P_{\text{gen,min}}, P_{\text{gen,max}}$)**: $[10,000\text{ W}, 100,000\text{ W}]$ ($10\text{ kW}$ to $100\text{ kW}$).
- **Linear Fuel Consumption Curve**: $f_{\text{rate}}(P) = 5.0\text{ L/h} + 0.00025 \times P\text{ [W]}$. (At $30\text{ kW}$, $f_{\text{rate}} = 12.5\text{ L/h}$).
- **Financial Parameters**: Fuel cost $=\$2.50/\text{Liters}$, Startup cost $=\$15.00$ per ignition event.

---

## 3. Provenance & Claim Boundary

```yaml
DIESEL_MODEL_CLASSIFICATION: REUSED_SYNTHETIC_ENGINEERING_PARAMETER
SOURCE: system/config/diesel.yaml
STATION_IDENTITY: NONE
CLAIM_FIREWALL: Reused prototype values for generator commitment & fuel accounting. Must NOT be cited as Nuolja generator specs.
```
