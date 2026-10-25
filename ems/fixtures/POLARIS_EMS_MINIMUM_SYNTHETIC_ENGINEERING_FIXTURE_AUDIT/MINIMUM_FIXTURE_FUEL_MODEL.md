# POLARIS EMS — MINIMUM FIXTURE FUEL MODEL

## 1. Executive Summary

This document specifies the minimum synthetic fuel inventory model.

---

## 2. Fuel State Parameters

- **Initial Fuel Volume ($F_{\text{initial}}$)**: $100.0\text{ Liters}$.
- **Fuel Reserve Floor ($F_{\text{reserve,min}}$)**: $50.0\text{ Liters}$.
- **Resupply Schedule**: `NONE` (Resupply events omitted; 100L initial fuel is sufficient for 24h closed-loop simulation).

---

## 3. Provenance & Claim Boundary

```yaml
FUEL_MODEL_CLASSIFICATION: SYNTHETIC_ENGINEERING_ASSUMPTION
STATION_IDENTITY: NONE
CLAIM_FIREWALL: Reused for fuel depletion tracking. Must NOT be cited as Nuolja fuel tank capacity.
```
