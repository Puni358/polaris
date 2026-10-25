# CRITICAL LOAD ARCHITECTURE

## 1. DYNAMIC $P_{\text{critical}}(t)$ DATA STRUCTURE & VECTOR LAYOUT

Governance DEC-004 D1 requires:
> "Protected critical equipment is station-defined. Required critical power may vary dynamically: $P_{\text{critical}}(t)$."

---

## 2. DUAL REPRESENTATION ARCHITECTURE

To support dynamic hourly variations, sub-category breakdown, and backward-compatible total demand accounting, the architecture uses a **Dual Representation**:

```text
                               ┌────────────────────────────────────────────────┐
                               │       ForecastBundle (Schema v1.1.0)           │
                               └───────────────────────┬────────────────────────┘
                                                       │
               ┌───────────────────────────────────────┴───────────────────────────────────────┐
               ▼                                                                               ▼
┌──────────────────────────────┐                                               ┌──────────────────────────────┐
│ demand (TimeseriesForecast)  │                                               │ critical_demand (Forecast)   │
│ Total Station Demand (49.5kW)│                                               │ Critical Load Vector (33.0kW)│
└──────────────┬───────────────┘                                               └──────────────┬───────────────┘
               │                                                                               │
               │                                 ┌─────────────────────────────────────────────┘
               │                                 │
               ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             EnergyOptimizer Decision Variables                              │
├───────────────────────────────────────────────┬─────────────────────────────────────────────┤
│  P_served_total[t] = P_served_crit[t] + ...   │  P_served_crit[t] + P_unmet_crit[t] =       │
│                                               │  P_critical[t]                              │
└───────────────────────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 3. CATEGORY SUB-BREAKDOWN
In the fixture and station config, critical load categories are represented as:
- Heating: $P_{\text{critical,heating}}(t)$ (e.g. $15.0$ kW)
- Water: $P_{\text{critical,water}}(t)$ (e.g. $10.0$ kW)
- Communications: $P_{\text{critical,comms}}(t)$ (e.g. $5.0$ kW)

Summed total critical demand:
$$P_{\text{critical,total}}(t) = P_{\text{heating}}(t) + P_{\text{water}}(t) + P_{\text{comms}}(t) = 30.0\text{ kW}$$

- **Schema Requirement**: `ForecastBundle` carries `critical_demand` as an additive 24-step forecast array ($W$). Sub-category vectors are stored in `metadata["critical_categories"]` or an optional sub-dictionary.
- **Repurposing Prohibition**: Total `demand.point` ($49.5$ kW) is **NEVER** overwritten by `critical_demand` ($33.0$ kW).
