# POLARIS EMS — P_CRITICAL(t) SEMANTIC AUDIT

## 1. Executive Summary

This document establishes the precise semantic definition of **Protected Critical Load ($P_{\text{critical}}(t)$)** derived from sealed Option D governance and system schema inspection.

---

## 2. Semantic Distinctions

```
┌─────────────────────────────────────────────────────────────┐
│                Total Station Demand                         │
│       forecast_bundle.demand.point (Schema v1.0.0)          │
│   Includes all facility loads (labs, offices, lighting,     │
│   flexible loads, non-essential heating, etc.)              │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ Strict Subset
┌─────────────────────────────────────────────────────────────┐
│          Protected Critical Load P_critical(t)              │
│   Authorized life-support & emergency systems ONLY:         │
│   1. Essential Heating (human survivability)                │
│   2. Essential Water Treatment & Filtration                 │
│   3. Emergency Communications & Control                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ Degraded Operating Bound
┌─────────────────────────────────────────────────────────────┐
│     Minimum Viable Protected Load P_min_critical(t)         │
│   Lower electrical threshold for proportional shortfall     │
│   allocation under Option D Rule D4                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Semantic Rule Enforcement

1. **Non-Equivalence**: $P_{\text{critical}}(t) \le \text{Total Demand}(t)$. $P_{\text{critical}}(t)$ is a strict subset of total station demand.
2. **Schema Firewall**: `forecast_bundle.demand.point` in `ForecastBundle` schema (version 1.0.0) represents total station demand. It MUST NOT be relabeled, repurposed, or assigned directly to $P_{\text{critical}}(t)$.
3. **Dynamic Variation**: $P_{\text{critical}}(t)$ is not required to be a static constant. It may vary over time based on thermal demand, operating cycles, or environmental conditions.

---

## 4. Status Classification

```yaml
P_CRITICAL_SEMANTICS_STATUS: GOVERNANCE_AND_ENGINEERING_DEFINED_CONCEPTUAL_ONLY
SCHEMA_TOTAL_DEMAND_FIELD: forecast_bundle.demand.point (W)
PROTECTED_CRITICAL_DEMAND_FIELD: NOT_ESTABLISHED_IN_SCHEMA (Additive extension required)
```
